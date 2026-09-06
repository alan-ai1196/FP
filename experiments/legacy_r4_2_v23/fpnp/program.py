from __future__ import annotations
from dataclasses import dataclass,field
import numpy as np

@dataclass
class SourceNode:
    node_id:int;tau:np.ndarray;phi:np.ndarray;name:str='source'

@dataclass
class AtomicSourceNode:
    node_id:int;lag0:int;context_token:int;name:str='atomic_source'

@dataclass
class ProductNode:
    node_id:int;parent_ids:np.ndarray;mix_left:np.ndarray;mix_right:np.ndarray;name:str='product'

@dataclass
class OutputAttachment:
    attachment_id:int;node_id:int;output_token:int;alpha:float

@dataclass
class FactorProgram:
    """Finite positive causal FP DAG.

    Model semantics are only positive source values, SUM/PRODUCT and nonnegative
    output measure. ``AtomicSourceNode`` is an exact physical specialization of a
    one-hot lag/context source, not a new semantic primitive. It exists because
    materializing a 511-vector and 50k-vector of zeros for one atomic provenance
    expression would be a deliberately bad physical realization under v23.
    """
    vocab:int=50257;horizon:int=511
    sources:list[SourceNode]=field(default_factory=list)
    atomic_sources:list[AtomicSourceNode]=field(default_factory=list)
    products:list[ProductNode]=field(default_factory=list)
    attachments:list[OutputAttachment]=field(default_factory=list)
    version:int=0;next_id:int=0;next_attachment_id:int=0

    def _all_nodes(self):
        return sorted([*self.sources,*self.atomic_sources,*self.products],key=lambda x:x.node_id)
    def node_count(self):return len(self.sources)+len(self.atomic_sources)+len(self.products)
    def node_ids(self):return [x.node_id for x in self._all_nodes()]
    def attachment_count(self):return len(self.attachments)

    @staticmethod
    def _positive_simplex(a,expected,name):
        a=np.asarray(a,np.float32)
        if a.ndim!=1 or a.size!=expected:raise ValueError(f'{name} shape mismatch: expected {expected}, got {a.shape}')
        if not np.isfinite(a).all() or np.min(a)<-1e-7:raise ValueError(f'{name} violates finite positive provenance')
        a=np.maximum(a,0);s=float(a.sum(dtype=np.float64))
        if not np.isfinite(s) or s<=0:raise ValueError(f'{name} has zero/nonfinite positive mass')
        return np.ascontiguousarray(a/s,dtype=np.float32)

    @staticmethod
    def _canonical_product(parent_ids,mix_left,mix_right):
        parent_ids=np.asarray(parent_ids,np.int32)
        if parent_ids.ndim!=1 or parent_ids.size==0:raise ValueError('PRODUCT requires at least one parent')
        if np.unique(parent_ids).size!=parent_ids.size:raise ValueError('PRODUCT parent list must use unique reusable nodes')
        ml=FactorProgram._positive_simplex(mix_left,parent_ids.size,'product left mix')
        mr=FactorProgram._positive_simplex(mix_right,parent_ids.size,'product right mix')
        order=np.argsort(parent_ids,kind='stable');parent_ids=np.ascontiguousarray(parent_ids[order],dtype=np.int32);ml=np.ascontiguousarray(ml[order]);mr=np.ascontiguousarray(mr[order])
        if mr.tobytes()<ml.tobytes():ml,mr=mr,ml
        return parent_ids,ml,mr

    def _find_source(self,tau,phi):
        for x in self.sources:
            if np.array_equal(x.tau,tau) and np.array_equal(x.phi,phi):return x.node_id
        return None
    def _find_atomic(self,lag0,context):
        for x in self.atomic_sources:
            if x.lag0==int(lag0) and x.context_token==int(context):return x.node_id
        return None
    def _find_product(self,parent_ids,mix_left,mix_right):
        for x in self.products:
            if np.array_equal(x.parent_ids,parent_ids) and np.array_equal(x.mix_left,mix_left) and np.array_equal(x.mix_right,mix_right):return x.node_id
        return None

    def _attach(self,node_id,output_token,alpha):
        if not np.isfinite(alpha) or alpha<0:raise ValueError('attachment alpha must be finite and nonnegative')
        y=int(output_token)
        if y<0 or y>=self.vocab:raise ValueError('output token outside vocabulary')
        if alpha==0.0:return False
        for a in self.attachments:
            if a.node_id==int(node_id) and a.output_token==y:
                new=float(a.alpha)+float(alpha)
                if not np.isfinite(new):raise ValueError('merged attachment alpha overflow')
                if new!=a.alpha:a.alpha=new;return True
                return False
        self.attachments.append(OutputAttachment(self.next_attachment_id,int(node_id),y,float(alpha)))
        self.next_attachment_id+=1;return True

    def add_source(self,tau,phi,output_token,alpha):
        if not np.isfinite(alpha) or alpha<0:raise ValueError('source alpha must be finite and nonnegative')
        tau=self._positive_simplex(tau,self.horizon,'tau');phi=self._positive_simplex(phi,self.vocab,'phi')
        node_id=self._find_source(tau,phi);changed=False
        if node_id is None:
            node_id=self.next_id;self.sources.append(SourceNode(node_id,tau,phi));self.next_id+=1;changed=True
        changed=self._attach(node_id,output_token,float(alpha)) or changed
        if changed:self.version+=1
        return int(node_id)

    def add_atomic_source(self,lag0,context_token,output_token,alpha):
        lag0=int(lag0);context_token=int(context_token)
        if lag0<0 or lag0>=self.horizon:raise ValueError('atomic lag outside horizon')
        if context_token<0 or context_token>=self.vocab:raise ValueError('atomic context outside vocabulary')
        if not np.isfinite(alpha) or alpha<0:raise ValueError('atomic alpha must be finite and nonnegative')
        node_id=self._find_atomic(lag0,context_token);changed=False
        if node_id is None:
            node_id=self.next_id;self.atomic_sources.append(AtomicSourceNode(node_id,lag0,context_token));self.next_id+=1;changed=True
        changed=self._attach(node_id,output_token,float(alpha)) or changed
        if changed:self.version+=1
        return int(node_id)

    def add_product(self,parent_ids,mix_left,mix_right,output_token,alpha):
        if not np.isfinite(alpha) or alpha<0:raise ValueError('product alpha must be finite and nonnegative')
        parent_ids=np.asarray(parent_ids,np.int32)
        if parent_ids.ndim!=1 or parent_ids.size==0:raise ValueError('PRODUCT requires at least one parent')
        if np.any(parent_ids<0) or np.any(parent_ids>=self.next_id):raise ValueError('PRODUCT may only reference already-materialized causal nodes')
        parent_ids,ml,mr=self._canonical_product(parent_ids,mix_left,mix_right)
        node_id=self._find_product(parent_ids,ml,mr);changed=False
        if node_id is None:
            node_id=self.next_id;self.products.append(ProductNode(node_id,parent_ids,ml,mr));self.next_id+=1;changed=True
        changed=self._attach(node_id,output_token,float(alpha)) or changed
        if changed:self.version+=1
        return int(node_id)

    def attachment_alpha_vector(self):
        rows=sorted(self.attachments,key=lambda a:a.attachment_id)
        if [a.attachment_id for a in rows]!=list(range(len(rows))):raise ValueError('noncanonical attachment IDs')
        return np.asarray([a.alpha for a in rows],dtype=np.float64)

    def replace_attachment_masses(self,alphas,tol=0.0):
        """Replace all currently materialized measure masses in one transaction.

        Zero mass removes support. This is the value/birth/death-unified v16/v23
        semantics; there is deliberately no separate delete action.
        """
        rows=sorted(self.attachments,key=lambda a:a.attachment_id)
        a=np.asarray(alphas,dtype=np.float64)
        if a.ndim!=1 or a.size!=len(rows):raise ValueError('attachment mass vector shape mismatch')
        # Empty support is a valid positive measure.  In particular the very first
        # structural transaction has an empty incumbent continuation and a nonempty
        # candidate continuation.  Never reduce an empty mass vector.
        if not np.isfinite(a).all() or (a.size and float(np.min(a))<-1e-12):raise ValueError('attachment masses must be finite nonnegative')
        a=np.maximum(a,0.0)
        old=np.asarray([x.alpha for x in rows],dtype=np.float64)
        changed=not np.array_equal(old,a)
        keep=[]
        for rec,val in zip(rows,a):
            if float(val)>float(tol):keep.append(OutputAttachment(len(keep),rec.node_id,rec.output_token,float(val)))
        if len(keep)!=len(rows):changed=True
        if changed:
            self.attachments=keep;self.next_attachment_id=len(keep);self.version+=1
        return changed

    def prune_unreferenced_nodes(self):
        """Remove zero-support dead nodes while preserving causal ID order.

        Products whose parents disappear are removed transitively. The operation is
        purely a physical canonicalization of the support already selected by mass.
        """
        live=set(a.node_id for a in self.attachments)
        products={p.node_id:p for p in self.products}
        grew=True
        while grew:
            grew=False
            for nid in list(live):
                p=products.get(nid)
                if p is not None:
                    for pid in p.parent_ids:
                        if int(pid) not in live:live.add(int(pid));grew=True
        nodes=[n for n in self._all_nodes() if n.node_id in live]
        remap={n.node_id:i for i,n in enumerate(nodes)}
        if len(nodes)==self.node_count() and all(remap[n.node_id]==n.node_id for n in nodes):return False
        ns=[];na=[];npd=[]
        for n in nodes:
            nid=remap[n.node_id]
            if isinstance(n,SourceNode):ns.append(SourceNode(nid,n.tau.copy(),n.phi.copy()))
            elif isinstance(n,AtomicSourceNode):na.append(AtomicSourceNode(nid,n.lag0,n.context_token))
            else:npd.append(ProductNode(nid,np.asarray([remap[int(x)] for x in n.parent_ids],np.int32),n.mix_left.copy(),n.mix_right.copy()))
        self.sources,self.atomic_sources,self.products=ns,na,npd
        self.attachments=[OutputAttachment(i,remap[a.node_id],a.output_token,a.alpha) for i,a in enumerate(self.attachments) if a.node_id in remap]
        self.next_id=len(nodes);self.next_attachment_id=len(self.attachments);self.version+=1
        return True

    def clone(self):
        q=FactorProgram(self.vocab,self.horizon)
        q.sources=[SourceNode(x.node_id,x.tau.copy(),x.phi.copy()) for x in self.sources]
        q.atomic_sources=[AtomicSourceNode(x.node_id,x.lag0,x.context_token) for x in self.atomic_sources]
        q.products=[ProductNode(x.node_id,x.parent_ids.copy(),x.mix_left.copy(),x.mix_right.copy()) for x in self.products]
        q.attachments=[OutputAttachment(a.attachment_id,a.node_id,a.output_token,a.alpha) for a in self.attachments]
        q.version=self.version;q.next_id=self.next_id;q.next_attachment_id=self.next_attachment_id
        return q

    def to_jsonable(self):
        return dict(vocab=self.vocab,horizon=self.horizon,version=self.version,next_id=self.next_id,next_attachment_id=self.next_attachment_id,
            sources=[dict(node_id=x.node_id,tau_nonzero=int(np.count_nonzero(x.tau)),phi_nonzero=int(np.count_nonzero(x.phi))) for x in self.sources],
            atomic_sources=[dict(node_id=x.node_id,lag0=x.lag0,lag=x.lag0+1,context_token=x.context_token) for x in self.atomic_sources],
            products=[dict(node_id=x.node_id,parent_ids=x.parent_ids.tolist(),mix_left=x.mix_left.tolist(),mix_right=x.mix_right.tolist()) for x in self.products],
            attachments=[dict(attachment_id=a.attachment_id,node_id=a.node_id,alpha=a.alpha,output_token=a.output_token) for a in self.attachments])

    def persistent_bytes(self):
        # Exact physical description bytes used by this Python realization. Atomic
        # sources intentionally avoid dense one-hot tau/phi storage.
        return int(sum(x.tau.nbytes+x.phi.nbytes for x in self.sources)+8*len(self.atomic_sources)+
            sum(x.parent_ids.nbytes+x.mix_left.nbytes+x.mix_right.nbytes for x in self.products)+16*len(self.attachments))
