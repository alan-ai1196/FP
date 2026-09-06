from __future__ import annotations
import json,math
from pathlib import Path
import numpy as np


def _load(p):
    return json.loads(Path(p).read_text())


_T975={1:12.7062047364,2:4.30265272991,3:3.18244630528,4:2.77644510520,5:2.57058183564,6:2.44691185114,7:2.36462425101,8:2.30600413503,9:2.26215716285,10:2.22813885196,11:2.20098516008,12:2.17881282966,13:2.16036865646,14:2.14478668792,15:2.13144954556,16:2.11990529922,17:2.10981557783,18:2.10092204024,19:2.09302405441,20:2.08596344727,21:2.07961384473,22:2.07387306790,23:2.06865761042,24:2.06389856163,25:2.05953855275,26:2.05552943864,27:2.05183051648,28:2.04840714180,29:2.04522964213,30:2.04227245630}

def _student_t_ci95(x):
    a=np.asarray(x,np.float64);mean=float(a.mean())
    if a.size<=1:return mean,float('nan'),None
    se=float(a.std(ddof=1)/math.sqrt(a.size));df=int(a.size-1)
    # The preregistered experiment uses n=3 paired seeds (df=2).  The table keeps
    # the helper correct for small audit variants without a SciPy dependency.
    crit=_T975[df] if df in _T975 else 1.95996398454
    return mean,se,[mean-crit*se,mean+crit*se]


def _row_map(rows):
    out={}
    for r in rows:
        k=round(float(r['requested_wall_seconds']),6)
        if k in out:raise RuntimeError(f'duplicate requested wall snapshot {k}')
        out[k]=r
    return out


def build_readout(root:Path,out:Path,seeds=(1337,2027,3141)):
    native=[_load(root/'runs'/f'native_s{s}'/f'native_seed{s}.json') for s in seeds]
    base=[_load(root/'runs'/f'gpt_s{s}'/f'gpt_seed{s}.json') for s in seeds]
    if [int(x['seed']) for x in native] != list(seeds) or [int(x['seed']) for x in base] != list(seeds):
        raise RuntimeError('seed/order mismatch in final readout')
    contracts=[x.get('validation_contract') for x in [*native,*base]]
    # The user explicitly requested direct reuse of the completed prior GPT baseline
    # by file presence. Compare deterministic protocol metadata only; stored SHA256
    # fields are carried through as provenance but are not checked here.
    def _protocol(c):
        c=c or {}
        return tuple(c.get(k) for k in ('kind','token_count','horizon','examples','seed'))
    protocols={_protocol(c) for c in contracts}
    if len(protocols)!=1:raise RuntimeError('native/baseline validation protocol metadata differ; refusing incomparable readout')
    val_contract=contracts[0]

    nm=[_row_map(x['rows']) for x in native];bm=[_row_map(x['rows']) for x in base]
    snapshot_sets=[set(x) for x in [*nm,*bm]]
    if any(s!=snapshot_sets[0] for s in snapshot_sets[1:]):
        raise RuntimeError('native/baseline requested wall-clock snapshot sets differ')
    times=sorted(snapshot_sets[0])
    if not times:raise RuntimeError('no paired scaling snapshots')

    curves=[]
    for t in times:
        pairs=[]
        for seed,nr,br in zip(seeds,nm,bm):
            n=nr[t];b=br[t];d=float(n['val_ce'])-float(b['val_ce'])
            pairs.append(dict(seed=int(seed),native_val_ce=float(n['val_ce']),baseline_val_ce=float(b['val_ce']),native_minus_baseline=d,
                native_actual_wall_seconds=float(n['actual_wall_seconds']),baseline_actual_wall_seconds=float(b['actual_wall_seconds']),
                native_ordinary_tokens=int(n['ordinary_tokens']),baseline_train_tokens=int(b['train_tokens']),
                native_program_version=int(n['program_version']),native_source_nodes=int(n['source_nodes']),native_product_nodes=int(n['product_nodes']),
                native_output_attachments=int(n.get('output_attachments',0)),native_compiler_cpu_wall_seconds=float(n['compiler_cpu_wall_seconds']),
                native_compiler_d2h_bytes=int(n['compiler_d2h_bytes']),native_compiler_dropped_evidence_tokens=int(n.get('compiler_dropped_evidence_tokens',0)),native_compiler_skipped_busy_evidence_tokens=int(n.get('compiler_skipped_busy_evidence_tokens',0)),native_compiler_sampled_evidence_tokens=int(n.get('compiler_sampled_evidence_tokens',0))))
        mean,se,ci=_student_t_ci95([p['native_minus_baseline'] for p in pairs])
        curves.append(dict(requested_wall_seconds=float(t),pairs=pairs,mean_native_minus_baseline=mean,se=se,ci95_student_t=ci,
            all_three_native_better=all(p['native_minus_baseline']<0 for p in pairs)))

    by=curves[-1]['pairs'];mean=curves[-1]['mean_native_minus_baseline'];se=curves[-1]['se'];ci=curves[-1]['ci95_student_t']
    for x,n,b in zip(by,native,base):
        comp=n['compiler'];sampled=int(comp.get('sampled_evidence_tokens',0));busy=int(comp.get('skipped_busy_evidence_tokens',0));dropped=int(comp.get('dropped_evidence_tokens',0))
        tx=n.get('transactions',[]);tx_seen=len(tx);accepted_struct=sum(1 for t in tx if t.get('committed_branch')=='structural');accepted_value=sum(1 for t in tx if t.get('committed_branch')=='value');kept_deployed=sum(1 for t in tx if t.get('committed_branch')=='deployed')
        x.update(native_nodes=int(n['program']['next_id']),native_sources=len(n['program'].get('sources',[]))+len(n['program'].get('atomic_sources',[])),native_atomic_sources=len(n['program'].get('atomic_sources',[])),native_products=len(n['program']['products']),
            native_compiler_cpu_wall=float(comp['cpu_wall_seconds']),native_compiler_d2h_bytes=int(comp['d2h_bytes']),
            native_compiler_sampled_evidence_tokens=sampled,native_compiler_skipped_busy_evidence_tokens=busy,native_compiler_true_drop_tokens=dropped,
            native_compiler_sample_fraction=sampled/max(1,sampled+busy+dropped),native_program_transactions=tx_seen,native_selected_structures=accepted_struct,native_selected_value_updates=accepted_value,native_selected_deployed_keeps=kept_deployed,
            native_cpu_compile_overlap_ratio=float(comp['cpu_wall_seconds'])/max(1e-12,float(n['total_wall_seconds'])),
            native_peak_vram_gib=float(n['peak_vram_gib']),baseline_peak_vram_gib=float(b['peak_vram_gib']))

    pf=_load(root/'artifacts'/'SYSTEM_PREFLIGHT.json');chosen=pf.get('chosen',{})
    result=dict(project='FP Native-from-Prior Scaling Trial 1 R4.2/V23',status='COMPLETE',gpt_baseline_reuse=dict(seeds=list(seeds),source='bundled completed prior R1 GPT results',hash_verified=False,resume_policy='file_presence_only'),validation_contract=val_contract,
        scaling_curve=curves,paired_final=by,mean_native_minus_baseline=mean,se=se,ci95_student_t=ci,
        all_three_native_better=all(x['native_minus_baseline']<0 for x in by),system_preflight=pf,
        overlap_physical_measurement=dict(raw_gpu_tokens_s=pf.get('raw_gpu_tokens_s'),chosen_layout=chosen.get('layout'),chosen_gpu_ratio_vs_raw=chosen.get('gpu_ratio_vs_raw'),chosen_compiler_evidence_tokens_s=chosen.get('compiler_evidence_tokens_s'),telemetry_cap=pf.get('evidence_node_cap')),
        compiler_scope=dict(active_region='finite first-order lag x context x output positive provenance measure',response_operator='implicit B/B^T atomic operator',quotient_policy='all active response columns or explicit UNRESOLVED',solver='batched exact pricing + feasible response-KKT-verified restricted solve; numerical nonclosure stays unresolved',value_learning='same positive-measure optimizer runs on every exact evidence confirmation window',confirmation='fresh train-only value-only versus candidate+value continuation with exact NLL Armijo',physical_selection='absolute {deployed,value,structural} matched hard-resource system-wall/VRAM transaction; blocks diagnostic only',finite_first_order_kkt_closed_to_tol='reported per certificate; sound response upper retained',higher_order_product_grammar_complete=False,global_physical_program_complete=False),
        claim_guardrail='This is a real from-uniform-prior positive factor-program trajectory if the target RTX3090 launcher gates pass. Validation is readout only. GPT baseline trajectories are directly reused by user-authorized file presence. A finite first-order atomic response cone may be called KKT-closed-to-declared-tolerance only when its numerical certificate closes; this is not a zero-gap completeness claim; incomplete active-response telemetry is UNRESOLVED, never approximated as complete. Higher-order PRODUCT grammar and global physical-program optimality remain unresolved unless their own branch upper bounds close. Baseline superiority/inferiority is empirical only.',
        native_semantics='uniform KT/Jeffreys prior + positive causal SUM/PRODUCT provenance measure; ordinary value learning and support change share one nonnegative measure optimizer; no inherited embedding/attention/norm/FFN/residual/LM-head/RNN scaffold')
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2));return result
