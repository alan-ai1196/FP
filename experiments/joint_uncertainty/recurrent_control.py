"""Native positive finite-window Bayes control, with ordinary delayed targets.

Known noise 1/10 and fair latent bits. This is a synthetic model control,
not an RN-5 worker or a claim of affordable long-horizon exact inference.
"""
from dataclasses import asdict,replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import subprocess
import sys
import tempfile
import traceback

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src/reference_compiler'),str(ROOT/'scripts')]
from fp_reference import ReferenceCompilerRuntime,CompilerPolicy
from fp_reference.data_usage import DataContract,SourceRead,StreamSpec
from fp_reference.float64_bridge import Float64Contract
from fp_reference.host_resources import HostResourceContract
from fp_reference.learner import LearnerSpec
from fp_reference.program import Binding,DelayedStateSpec,Product,Program,SemanticRules,Source,SourceSpec,State,Sum,Term
from fp_reference.runtime import OnlineContract
from fp_reference.semantics import evaluate,reset_delayed
from audit_reference_construction import contract,limits,validate_residency
from audit_float64_runtime import replay
from audit_reference_events import forward_oracle
from audit_cuda_learner import model_initial,model_predict,model_observe,model_commit
from ingress_audit_support import deliver_context

HOST_CAP=512<<20
OUTPUT=ROOT/'evidence/minimal/FP_NATIVE_RECURRENT_POSTERIOR_CPU_AUDIT.json'
DEPENDENCIES=('src/reference_compiler','scripts','experiments/joint_uncertainty/recurrent_control.py')


def context(n,i,j):
    return tuple(F(index==chosen) for chosen in (i,j) for index in range(n))


def fixture(n=3,window=3,horizon=None):
    assert n>=2 and window>=1
    horizon=window+1 if horizon is None else horizon
    assert horizon>=1
    worlds=tuple((0,)+bits for bits in product((0,1),repeat=n-1))
    K=len(worlds)
    specs=tuple(SourceSpec(f'{when}{side}:{i}','mass',lag,F(1))
        for when,lag in (('now',0),('old',1)) for side in (0,1) for i in range(n))
    specs+=tuple(SourceSpec(f'old-y:{y}','mass',1,F(1)) for y in (0,1))
    states=tuple(DelayedStateSpec(f'w{world}:{depth}','mass',1,F(9**depth-1))
        for world in range(K) for depth in range(1,window))
    rules=SemanticRules(specs,('mass',),(('mass','mass','mass'),),'mass',(F(K),F(K)),states)
    nodes=[Source(s.source_id) for s in specs]
    sources={s.source_id:k for k,s in enumerate(specs)}
    def emit(node):
        nodes.append(node)
        return len(nodes)-1
    def summation(parents,slot=0):
        return emit(Sum('mass',tuple(Term(parent,slot) for parent in parents)))
    multiply=lambda a,b:emit(Product('mass',a,b))
    one=summation(sources[f'now0:{i}'] for i in range(n))
    zero=summation(())
    reads={s.state_id:emit(State(s.state_id)) for s in states}
    pairs={(when,i,j):multiply(sources[f'{when}0:{i}'],sources[f'{when}1:{j}'])
        for when in ('now','old') for i,j in product(range(n),repeat=2)}
    labelled={(i,j,y):multiply(pairs['old',i,j],sources[f'old-y:{y}'])
        for i,j,y in product(range(n),range(n),(0,1))}
    bindings=[];excesses=[];head_terms=[[],[]]
    for world,z in enumerate(worlds):
        indicator=summation(labelled[i,j,z[i]^z[j]] for i,j in product(range(n),repeat=2))
        for depth in range(1,window+1):
            previous=zero if depth==1 else reads[f'w{world}:{depth-1}']
            gain=multiply(indicator,summation((one,previous)))
            body=emit(Sum('mass',(Term(previous,0),Term(gain,1))))
            if depth<window:
                bindings.append(Binding(f'w{world}:{depth}',body))
        excesses.append(body)
        weight=summation((one,body))
        for y in (0,1):
            selected=[pairs['now',i,j] for i,j in product(range(n),repeat=2) if z[i]^z[j]==y]
            if selected:
                head_terms[y].append(multiply(weight,summation(selected)))
    common=summation(excesses)
    heads=tuple(emit(Sum('mass',(Term(common,0),Term(summation(head_terms[y]),1)))) for y in (0,1))
    graph=Program(tuple(nodes),2,heads,tuple(bindings))
    graph.validate(rules)
    rows=tuple(context(n,i,j) for i,j in product(range(n),repeat=2))
    past=((F(0),)*(2*n+2),)+tuple(row+(F(y==0),F(y==1)) for row,y in product(rows,(0,1)))
    domain=tuple(current+old for current,old in product(rows,past))
    cap=F(10*K*9**window)
    cfg=replace(contract(source_domain=False,pattern=(F(1),F(8))),semantics=rules,
        source_domain=domain,normalizer_cap=cap,activation_cap=cap,reference_integer_bits=32768,
        limits=limits(byte_cap=256<<20,work_cap=10**10))
    reads=tuple(SourceRead(s.source_id,'input',side*n+i,lag)
        for when,lag in (('now',0),('old',1)) for side in (0,1) for i in range(n)
        for s in (next(s for s in specs if s.source_id==f'{when}{side}:{i}'),))
    reads+=tuple(SourceRead(f'old-y:{y}','target_atom',y,1) for y in (0,1))
    data=DataContract((StreamSpec('online','online',tuple(f'bayes-{i}' for i in range(horizon))),),
        'online',(F(1),)*(2*n),reads)
    online=OnlineContract(data,LearnerSpec(1,F(0)),float64=Float64Contract(F(1,100),F(1,100)))
    return cfg,graph,online,worlds


def posterior(n,history,i,j):
    # Full latent assignments, independent of the constructor's global-flip
    # value reduction and its positive excess representation.
    assignments=tuple(product((0,1),repeat=n))
    weights=tuple(9**sum((z[a]^z[b])==label for a,b,label in history) for z in assignments)
    p0=sum(w*F(9 if z[i]==z[j] else 1,10) for z,w in zip(assignments,weights))/sum(weights)
    return p0,1-p0


def algebra():
    full=suffix=intermediate=0
    for n,window in ((2,1),(2,2),(3,3)):
        cfg,graph,online,worlds=fixture(n,window)
        domain=tuple(product(range(n),repeat=2))
        # All ordered histories through length two, including diagonals;
        # a signed triangle also covers the third delayed stage.
        histories=[()]
        for length in (1,2):
            histories.extend(product(tuple((i,j,y) for i,j in domain for y in (0,1)),repeat=length))
        if window==3:
            histories.extend(tuple((i,j,y) for (i,j),y in zip(((0,1),(1,2),(0,2)),labels)) for labels in product((0,1),repeat=3))
        if window==2:
            histories.extend((((0,1,0),(0,1,0),(0,1,1)),
                              ((0,0,0),(0,1,1),(1,1,1),(0,1,0))))
        for history in histories:
            delayed=reset_delayed(cfg.semantics)
            # Each current prediction consumes only the preceding label;
            # the current label enters the next event's lagged sources.
            for at in range(len(history)+1):
                old=(F(0),)*(2*n+2) if at==0 else context(n,*history[at-1][:2])+(F(history[at-1][2]==0),F(history[at-1][2]==1))
                if at<len(history):
                    i,j,_=history[at]
                    point=context(n,i,j)+old
                    prediction=evaluate(graph,cfg.semantics,(F(1),F(8)),dict(zip((s.source_id for s in cfg.semantics.sources),point)),delayed,bit_limit=32768)
                    assert prediction.probabilities==posterior(n,history[max(0,at-window):at],i,j)
                    delayed=prediction.delayed
                    intermediate+=1
                else:
                    for i,j in domain:
                        point=context(n,i,j)+old
                        prediction=evaluate(graph,cfg.semantics,(F(1),F(8)),dict(zip((s.source_id for s in cfg.semantics.sources),point)),delayed,bit_limit=32768)
                        assert prediction.probabilities==posterior(n,history[-window:],i,j)
                        if len(history)<=window:
                            full+=1
                        else:
                            suffix+=1
    assert 'torch' not in sys.modules
    return {'exact_native_full_prefix_posterior_forecasts':full,
        'exact_native_truncated_window_forecasts':suffix,'intermediate_forecasts':intermediate,
        'scope':'finite declared windows, including eviction; no external target tape or GPU execution'}


def cpu(case='full',bounded=False):
    assert case in ('full','suffix')
    window=3 if case=='full' else 2
    sequence=(((0,1,0),(1,2,0),(0,2,1),(0,1,0)) if case=='full' else
              ((0,1,0),(0,1,0),(0,1,1),(0,1,0)))
    cfg,graph,online,worlds=fixture(window=window,horizon=len(sequence))
    host=HostResourceContract(HOST_CAP,{'deployment':HOST_CAP,'compiler':HOST_CAP}) if bounded else None
    rt=ReferenceCompilerRuntime(cfg,graph,online=online,policy=CompilerPolicy(()),host=host)
    history=[];forecasts=[]
    for cursor,(i,j,label) in enumerate(sequence):
        forecast=deliver_context(rt,f'bayes-{cursor}',context(3,i,j))
        assert forecast.status=='PREDICTED_REFERENCE',forecast
        snapshot=rt.snapshot()
        p=dict(forecast.predictions)[snapshot.deployed_id]
        assert p==posterior(3,history[-window:],i,j)
        if case=='suffix' and cursor==3:
            assert p==(F(1,2),F(1,2)) and posterior(3,history,i,j)==(F(41,50),F(9,50))
        assert snapshot.pending.record.target is None
        forecasts.append(tuple(map(str,p)))
        assert rt.observe(label).status=='OBSERVED_REFERENCE'
        history.append((i,j,label))
    final=validate_residency(rt)
    assert final.run.status=='SEALED_REFERENCE_STREAM' and final.halted is None
    assert not final.install_receipts and not final.reference_proofs
    assert len(final.observations)==len(sequence) and tuple(r.target for r in final.observations)==tuple(r[2] for r in sequence)
    state=final.candidates[0]
    assert state.theta==(F(1),F(8)) and len(state.delayed)==len(cfg.semantics.states)
    phases,*_=replay(rt)
    final=validate_residency(rt)
    assert 'torch' not in sys.modules
    observed=final.host_resources
    if bounded:
        assert observed.contract==host and 'UNRESOLVED' not in final.run.host_scope
    return {'status':final.run.status,'window':window,'native_graph':graph.counts(),
        'delayed_coordinates':len(cfg.semantics.states),'retained_observations':len(final.observations),
        'independent_binary64_phases':phases,'native_forecasts':forecasts,
        'full_history_claim_after_window':False,'host_scope':final.run.host_scope,
        'host':None if observed is None else {key:getattr(observed,key) for key in (
            'process_id','creation_100ns','lifetime_process_commit_peak','job_commit_peak',
            'process_user_100ns','process_kernel_100ns','job_user_100ns','job_kernel_100ns')},
        'class_or_install_certificate':False}


def rounded():
    cfg,graph,online,worlds=fixture()
    cases=(((0,1),(1,2),(0,2),(0,1)),((0,1),(0,1),(1,2),(0,2)),
        ((0,0),(0,1),(1,1),(0,1)))
    checks=0;maximum_gradient=maximum_division=F(0)
    for queries,labels in product(cases,product((0,1),repeat=4)):
        amp=model_initial(graph,cfg.semantics,(F(1),F(8)),0)
        delayed=reset_delayed(cfg.semantics);history=[]
        for at,((i,j),label) in enumerate(zip(queries,labels)):
            old=(F(0),)*8 if at==0 else context(3,*history[-1][:2])+(F(history[-1][2]==0),F(history[-1][2]==1))
            point=context(3,i,j)+old
            inputs=dict(zip((s.source_id for s in cfg.semantics.sources),point))
            ref=evaluate(graph,cfg.semantics,(F(1),F(8)),inputs,delayed,bit_limit=32768)
            p,g=forward_oracle(graph,cfg.semantics,(F(1),F(8)),inputs,delayed)
            assert p==ref.probabilities==posterior(3,history,i,j)
            ap=model_predict(graph,cfg.semantics,amp,inputs)
            assert tuple(ap['masses'])==ref.masses and ap['delayed']==ref.delayed
            maximum_division=max(maximum_division,max(abs(F(a)-b) for a,b in zip(ap['probabilities'],p)))
            amp=model_observe(graph,amp,ap,label)
            maximum_gradient=max(maximum_gradient,max(abs(F(a)-b) for a,b in zip(amp.gradient,g[label])))
            amp=model_commit(amp,online.learner)
            assert amp.theta==(F(1),F(8))
            delayed=ref.delayed;history.append((i,j,label));checks+=1
    assert maximum_gradient<F(1,100) and maximum_division<F(1,100) and 'torch' not in sys.modules
    return {'rounded_interpreter_forecasts':checks,'native_masses_and_delayed_states_exact':True,
        'maximum_gradient_error':str(maximum_gradient),'maximum_raw_division_error':str(maximum_division),
        'actual_CUDA_execution':False}


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT).decode().rstrip('\r\n')


def bounded(write):
    from windows_job_audit_support import run_in_job
    source=git('rev-parse','HEAD')
    def source_clean():
        assert git('rev-parse','HEAD')==source
        assert not git('status','--porcelain','--',*DEPENDENCIES)
    source_clean()
    rows=[]
    for case in ('full','suffix'):
        with tempfile.TemporaryDirectory(prefix='fp-recurrent-control-',dir=ROOT) as temporary:
            assert Path(temporary).resolve().parent==ROOT.resolve()
            output=Path(temporary)/'result.json'
            job=run_in_job(__file__,('--worker',case,'--output',output),commit_limit=HOST_CAP,timeout_ms=120000)
            row={'case':case,'completed_job':asdict(job),'worker_status':'FAILED'}
            try:
                if output.exists():
                    with output.open('rb') as stream:
                        payload=stream.read(16385)
                    assert len(payload)<=16384
                    row['result']=json.loads(payload)
                if job.exit_code==0 and not job.timed_out:
                    observed=row['result']['runtime']['host']
                    assert (observed['process_id'],observed['creation_100ns'])==(job.process_id,job.process_creation_100ns)
                    assert observed['lifetime_process_commit_peak']<=job.peak_process_commit<=HOST_CAP
                    assert observed['job_commit_peak']<=job.peak_job_commit<=HOST_CAP
                    for clock in ('user','kernel'):
                        assert max(observed[f'process_{clock}_100ns'],observed[f'job_{clock}_100ns'])<=getattr(job,f'{clock}_100ns')
                    row['worker_status']='EXECUTED'
            except Exception:
                row['audit_failure']=traceback.format_exc()
            rows.append(row)
        source_clean()
    report={'status':'PASS' if all(r['worker_status']=='EXECUTED' for r in rows) else 'FAILED',
        'registration_source':source,'scope':'native finite-window posterior control; owned CPU stream and complete fresh host jobs',
        'host_cap':HOST_CAP,'worker_timeout_ms':120000,'workers':rows,
        'not_claimed':['actual CUDA execution','learned prior or noise','compiler construction or installation',
            'class completeness','whole-history inference beyond the window','affordable long-horizon inference']}
    if write:
        OUTPUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    assert report['status']=='PASS',report
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_mutually_exclusive_group()
    modes.add_argument('--cpu',action='store_true')
    modes.add_argument('--rounded',action='store_true')
    modes.add_argument('--bounded',action='store_true')
    modes.add_argument('--worker',choices=('full','suffix'))
    parser.add_argument('--output')
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    assert not args.write or args.bounded
    assert bool(args.output)==bool(args.worker)
    if args.worker:
        try:
            result={'runtime':cpu(args.worker,bounded=True)}
            if args.worker=='full':
                result.update(algebra=algebra(),rounded=rounded())
        except Exception:
            Path(args.output).write_text(json.dumps({'status':'FAILED','traceback':traceback.format_exc()}),encoding='utf-8')
            raise
        Path(args.output).write_text(json.dumps(result),encoding='utf-8')
    else:
        print(json.dumps(bounded(args.write) if args.bounded else cpu() if args.cpu else rounded() if args.rounded else algebra(),indent=2))
