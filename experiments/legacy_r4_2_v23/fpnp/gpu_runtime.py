from __future__ import annotations
import numpy as np
import torch
import torch.nn.functional as F
from .program import FactorProgram

class GpuProgram:
    """CUDA realization of the positive factor DAG.

    Reusable activation nodes and output attachments are lowered separately. Exact
    duplicate factor expressions therefore cost one activation. Output attachment
    masses are aggregated by node at install time. Token IDs stay int32 on device.
    """
    def __init__(self,program:FactorProgram,device='cuda',sync=True):
        self.device=torch.device(device);self.install(program,sync=sync)
    def install(self,p:FactorProgram,sync=False,stream=None):
        self.program_version=p.version;self.vocab=p.vocab;self.h=p.horizon
        self.node_ids=p.node_ids();self.source_ids=[x.node_id for x in sorted(p.sources,key=lambda x:x.node_id)];self.atomic_sources=[(x.node_id,int(x.lag0),int(x.context_token)) for x in sorted(p.atomic_sources,key=lambda x:x.node_id)]
        stream=stream or torch.cuda.current_stream(self.device)
        with torch.cuda.stream(stream):
            if p.sources:
                src=sorted(p.sources,key=lambda x:x.node_id)
                self.tau=torch.as_tensor(np.stack([x.tau for x in src]),device=self.device,dtype=torch.float32)
                self.phi=torch.as_tensor(np.stack([x.phi for x in src]),device=self.device,dtype=torch.float32)
            else:self.tau=self.phi=None
            self.products=[]
            for x in sorted(p.products,key=lambda x:x.node_id):
                self.products.append((x.node_id,[int(i) for i in x.parent_ids],
                    torch.as_tensor(x.mix_left,device=self.device,dtype=torch.float32),
                    torch.as_tensor(x.mix_right,device=self.device,dtype=torch.float32)))
            # A positive output measure is stored sparsely in the categorical basis; no single output fiber is preselected by the Compiler.
            # Keep them sparse in host/program storage, and lower directly into the
            # device lookup table without ever constructing an R x |V| host array.
            if p.node_count():
                self.beta_t=torch.zeros((p.vocab,p.node_count()),device=self.device,dtype=torch.float32)
                self.alpha_sum=torch.zeros(p.node_count(),device=self.device,dtype=torch.float32)
                if p.attachments:
                    # Validate the FP32 lowering on host.  Avoid a GPU `.all()`
                    # synchronization during program installation; FactorProgram
                    # already guarantees individual positive finite alpha values.
                    host_sum=np.zeros(p.node_count(),dtype=np.float64)
                    for a in p.attachments:host_sum[a.node_id]+=float(a.alpha)
                    if (not np.isfinite(host_sum).all()) or float(host_sum.max(initial=0.0))>np.finfo(np.float32).max:
                        raise ValueError('output attachment aggregation overflows FP32 lowering')
                    yy=torch.as_tensor([a.output_token for a in p.attachments],device=self.device,dtype=torch.long)
                    nn=torch.as_tensor([a.node_id for a in p.attachments],device=self.device,dtype=torch.long)
                    av=torch.as_tensor([a.alpha for a in p.attachments],device=self.device,dtype=torch.float32)
                    self.beta_t.index_put_((yy,nn),av,accumulate=True);self.alpha_sum.scatter_add_(0,nn,av)
            else:self.beta_t=self.alpha_sum=None
        if sync:stream.synchronize()
    def eval_cuda(self,ids,q,return_nodes=False,amp=True):
        """Execute the registered physical FP path.

        AMP is the science default: eligible CUDA kernels use BF16 autocast while
        positive mass/normalizer accumulation and logarithms stay FP32.  `amp=False`
        exists only for the target precision bridge and numerical diagnostics.
        """
        with torch.autocast('cuda',dtype=torch.bfloat16,enabled=bool(amp)):
            if ids.dtype not in (torch.int32,torch.int64):ids=ids.to(torch.int32)
            y=ids[self.h:];n=y.numel();q=q.to(dtype=torch.float32);acts={}
            mass=q.clone();norm=torch.ones_like(q)
            if self.tau is not None:
                u=torch.index_select(self.phi,1,ids)
                w=self.tau.flip(-1).unsqueeze(1)
                zs=F.conv1d(u.unsqueeze(0),w,groups=self.tau.shape[0]).squeeze(0)[:,:n]
                for i,nid in enumerate(self.source_ids):acts[nid]=zs[i]
            # Exact compact lowering of one-hot lag/context sources. lag0=0 means
            # the immediately previous token. Equality remains exact under AMP.
            for nid,lag0,ctx in self.atomic_sources:
                hist=ids[self.h-1-lag0:self.h-1-lag0+n]
                acts[nid]=(hist==ctx).to(torch.float32)
            for nid,parents,mix_left,mix_right in self.products:
                parent=torch.stack([acts[pid] for pid in parents],0)
                left=torch.sum(mix_left[:,None]*parent,dim=0);right=torch.sum(mix_right[:,None]*parent,dim=0);acts[nid]=left*right
            zstack=None
            if self.beta_t is not None and acts:
                # N x R is the execution layout: output lookup and compiler D2H both
                # consume it directly, so no all-node transpose is materialized.
                zstack=torch.stack([acts[i] for i in self.node_ids],dim=1)
                pt=torch.index_select(self.beta_t,0,y)
                # Positive evidence accumulation is the numerical anchor of the
                # normalized-positive semantics. Keep it FP32 even when upstream
                # factor evaluation used BF16 autocast.
                with torch.autocast('cuda',enabled=False):
                    zf=zstack.float();pf=pt.float()
                    mass.add_((zf*pf).sum(1));norm.add_(torch.mv(zf,self.alpha_sum.float()))
            with torch.autocast('cuda',enabled=False):
                nll=-torch.log(mass.float().clamp_min(1e-30))+torch.log(norm.float().clamp_min(1e-30))
            if return_nodes=='map':nodes=acts
            elif return_nodes:nodes=zstack
            else:nodes=None
            return dict(nll=nll,mass=mass,norm=norm,nodes=nodes,targets=y)
    def eval_chunk(self,context_u16,q_target,return_nodes=False,amp=True):
        ids=torch.as_tensor(context_u16,device=self.device,dtype=torch.int32)
        q=torch.as_tensor(q_target,device=self.device,dtype=torch.float32)
        return self.eval_cuda(ids,q,return_nodes,amp=amp)

    @torch.inference_mode()
    def val_windows_ce(self,val_u16,counts,total,positions,batch=512,amp=True):
        """Exact common-window CE on positions shared with the strong baseline."""
        den=float(total)+0.5*self.vocab;loss=0.0;seen=0
        positions=np.asarray(positions,dtype=np.int64)
        for b0 in range(0,positions.size,batch):
            pp=positions[b0:b0+batch];B=pp.size
            hist=np.empty((B,self.h),dtype=np.uint16);yy=np.empty(B,dtype=np.int32)
            for i,pos in enumerate(pp):hist[i]=np.asarray(val_u16[pos-self.h:pos]);yy[i]=int(val_u16[pos])
            ids=torch.as_tensor(hist,device=self.device,dtype=torch.int32);yt=torch.as_tensor(yy,device=self.device,dtype=torch.int32)
            q=((counts[yy].astype(np.float64)+0.5)/den).astype(np.float32);qt=torch.as_tensor(q,device=self.device)
            with torch.autocast('cuda',dtype=torch.bfloat16,enabled=bool(amp)):
                acts={}
                if self.tau is not None:
                    # [R,B,H] gather; batch is intentionally bounded to control scratch.
                    # Explicit BF16 operands make the gather/reduction validation path
                    # match the registered AMP factor precision used by ordinary conv1d.
                    gathered=self.phi[:,ids].to(torch.bfloat16) if amp else self.phi[:,ids]
                    tauv=self.tau.flip(-1).to(torch.bfloat16) if amp else self.tau.flip(-1)
                    zs=(gathered*tauv[:,None,:]).sum(-1)
                    for i,nid in enumerate(self.source_ids):acts[nid]=zs[i]
                for nid,lag0,ctx in self.atomic_sources:
                    acts[nid]=(ids[:,self.h-1-lag0]==ctx).to(torch.float32)
                for nid,parents,mix_left,mix_right in self.products:
                    parent=torch.stack([acts[pid] for pid in parents],0);left=(mix_left[:,None]*parent).sum(0);right=(mix_right[:,None]*parent).sum(0);acts[nid]=left*right
                mass=qt.clone();norm=torch.ones_like(qt)
                if self.beta_t is not None and acts:
                    zstack=torch.stack([acts[i] for i in self.node_ids],dim=1);pt=torch.index_select(self.beta_t,0,yt)
                    with torch.autocast('cuda',enabled=False):
                        zf=zstack.float();pf=pt.float();mass.add_((zf*pf).sum(1));norm.add_(torch.mv(zf,self.alpha_sum.float()))
                with torch.autocast('cuda',enabled=False):
                    batch_loss=-torch.log(mass.float().clamp_min(1e-30))+torch.log(norm.float().clamp_min(1e-30))
            loss+=float(batch_loss.sum().item());seen+=B
        return loss/max(1,seen)
