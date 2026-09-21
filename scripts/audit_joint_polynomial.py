"""Joint native a+a^2 learner: exact function, transitive updates and owned paths."""
import argparse
from dataclasses import asdict, replace
from fractions import Fraction as F
from itertools import product
import json
from math import prod
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import traceback
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src/reference_compiler'),str(ROOT/'scripts')]
from fp_reference.relation_proposal import relation_proposal
from fp_reference.empirical_bound import empirical_upper
from fp_reference.native_search import GrammarLimits
from fp_reference.resources import ResourceExceeded
from fp_reference.float64_bridge import Float64Contract
from audit_component_symmetry import (partitions,relative_assignments,observations,run_contract,
    runtime,ingest,HOST_CAP)
from audit_reference_acceleration import fixture_parameters,context
from audit_reference_events import forward_oracle
from audit_reference_construction import validate_residency
from audit_float64_runtime import replay
from audit_cuda_runtime import (audit_snapshot,cuda_contract,raw_model,raw_model_prediction,
    model_initial,model_predict,model_observe,model_commit,HALF,SINGLE,pack,output_cells,forward_operations,phase_payload)
from fp_reference import ReferenceCompilerRuntime,CudaCompilerPolicy,CudaCompilationStep
from fp_reference.cuda_installation import CudaInstallContract
from fp_reference.persistence import CUDA_PATH,FLOAT64_PATH
from fp_reference.host_resources import HostResourceContract
from audit_reference_construction import zero_program
from audit_cuda_policy_run import host_record
from ingress_audit_support import deliver_context
from windows_job_audit_support import run_in_job

SOLVER='empirical-binary-relation-joint-polynomial-v5'


def configuration(n):
    cfg,old,*_=fixture_parameters(n)
    worlds=1 << (n-1)
    pattern=(F(1),F(8))+(F(1),)*worlds
    grammar=GrammarLimits(2*n+n*n+2*worlds+2,2*worlds+2,n*n,
                          3*n*n+2*worlds*n*n+2*worlds,len(pattern))
    return cfg,old,pattern,grammar


def proposal(cfg,old,counts,pattern,grammar):
    upper=empirical_upper(observations(cfg,counts),cfg.semantics,bit_limit=32768)
    return relation_proposal(upper,cfg.semantics,grammar,pattern,
        replace(old.searches[0].relation_sources,solver=SOLVER),bit_limit=32768),upper


def family(partition,h):
    return tuple(tuple(h[i]^flips[k] for i in range(len(h)) for k,vertices in enumerate(partition) if i in vertices)
                 for flips in ((0,)+bits for bits in product((0,1),repeat=len(partition)-1)))


def exact_audit():
    models=initial=gradients=recoveries=scale_cases=0
    for n in range(2,6):
        cfg,old,pattern,grammar=configuration(n)
        for partition in partitions(n):
            for h in relative_assignments(n,partition):
                edges=tuple((i,j) for group in partition for i,j in zip(group,group[1:])) or ((0,0),)
                counts=tuple((i,j,9-8*(h[i]^h[j]),1+8*(h[i]^h[j])) for i,j in edges)
                proposed,_=proposal(cfg,old,counts,pattern,grammar)
                graph=proposed.program
                assert graph is not None and proposed.scale==8
                theta=pattern[:graph.slot_count]
                component={v:k for k,group in enumerate(partition) for v in group}
                members=family(partition,h) if len(partition)>1 else ()
                coordinates=[i for i in range(len(theta)) if i!=1][:len(members)]
                nonempty=0
                for member in members:
                    nonempty+=len({member[i]^member[j] for i,j in product(range(n),repeat=2) if component[i]!=component[j]})
                W=sum(len(group)**2 for group in partition);K=len(members)
                expected=(2*n+n*n+nonempty+2,nonempty+2,n*n,2*n*n+2*K*(n*n-W)+nonempty+W)
                actual=graph.counts()
                assert tuple(actual[k] for k in ('nodes','SUMs','PRODUCTs','edges'))==expected
                for i,j in product(range(n),repeat=2):
                    inputs=dict(zip((s.source_id for s in cfg.semantics.sources),context(n,i,j)))
                    p,g=forward_oracle(graph,cfg.semantics,theta,inputs)
                    cross=component[i]!=component[j]
                    expected=(F(1,2),F(1,2)) if cross else ((F(1,10),F(9,10)) if h[i]^h[j] else (F(9,10),F(1,10)))
                    assert p==expected;initial+=1
                    if cross:
                        assert g[0][1]==g[1][1]==0
                        for slot,member in zip(coordinates,members):
                            preferred=member[i]^member[j]
                            assert g[preferred][slot]==F(-3,2*(1+K)) and g[1-preferred][slot]==F(3,2*(1+K))
                            gradients+=2
                if members:
                    i,j=partition[0][0],partition[1][0]
                    inputs=dict(zip((s.source_id for s in cfg.semantics.sources),context(n,i,j)))
                    for slot,member in zip(coordinates,members):
                        weights=list(theta);weights[slot]=F(0)
                        _,g=forward_oracle(graph,cfg.semantics,tuple(weights),inputs)
                        assert g[member[i]^member[j]][slot]<0
                        update=-g[member[i]^member[j]][slot]/8
                        assert (update*65536).numerator//(update*65536).denominator>0
                        recoveries+=1
                models+=1
    cfg,old,pattern,grammar=configuration(3)
    for a,b in product(range(11),repeat=2):
        counts=((0,1,a,10-a),(1,2,b,10-b))
        c=1+int(a==5)+int(b==5);K=0 if c==1 else 2**(c-1)
        for slots in (1,2,3,4,5,6):
            prefix=(F(1),F(8))+(F(1),)*4
            proposed,upper=proposal(cfg,old,counts,prefix,replace(grammar,slots=slots))
            available=prefix[:slots];units=available.count(F(1))
            feasible=tuple(v for v in (F(1),F(8)) if v in available and units-int(v==1)>=K)
            if not feasible:
                assert proposed.program is None
            else:
                M,m=sum(max(x,10-x) for x in (a,b) if x!=5),sum(min(x,10-x) for x in (a,b) if x!=5)
                likelihood=[((v+1)/(v+2))**M*(1/(v+2))**m for v in feasible]
                assert proposed.program is not None and proposed.scale==feasible[likelihood.index(max(likelihood))]
                actual=prod(forward_oracle(proposed.program,cfg.semantics,prefix[:proposed.program.slot_count],dict(o.sources))[0][o.target]
                            for o in observations(cfg,counts))
                assert actual==max(likelihood)*F(1,2)**(10*((a==5)+(b==5)))<=upper.likelihood
            scale_cases+=1
    # The new graph realizes phi(a)*G on soft inputs too. It does not borrow
    # the old square-of-G graph's one-hot-only identity or full learner.
    counts=((0,0,9,1),(1,1,9,1),(2,2,9,1))
    proposed,_=proposal(cfg,old,counts,pattern,grammar)
    graph=proposed.program;theta=(F(1,4),F(8),F(1,2),F(3,4),F(5,4))
    members=tuple((0,)+bits for bits in product((0,1),repeat=2))
    coordinates=(0,2,3,4);soft=0
    for values in product((F(0),F(1,2),F(1)),repeat=6):
        masses=[F(1)+8*sum(values[i]*values[3+i] for i in range(3)),F(1)]
        for slot,member in zip(coordinates,members):
            for i,j in product(range(3),repeat=2):
                if i!=j:
                    masses[member[i]^member[j]]+=(theta[slot]+theta[slot]**2)*values[i]*values[3+j]
        p,_=forward_oracle(graph,cfg.semantics,theta,dict(zip((s.source_id for s in cfg.semantics.sources),values)))
        assert p==tuple(v/sum(masses) for v in masses);soft+=1
    # Removing an output gate constructs a different learner; it is not a
    # licensed edit of an existing complete learner or its evidence lineage.
    sys.path.insert(0,str(ROOT/'experiments/adaptive_uncertainty'))
    from correlation_control import mixture_graph
    old_graph=mixture_graph(cfg,'mixed')
    states=[(old_graph,(F(1),F(8))+(F(1),)*4),(graph,pattern[:graph.slot_count])]
    inputs=dict(zip((v.source_id for v in cfg.semantics.sources),context(3,0,1)))
    next_predictions=[]
    for native,weights in states:
        for _ in range(2):
            _,g=forward_oracle(native,cfg.semantics,weights,inputs)
            updated=[max(F(0),value-gradient) for value,gradient in zip(weights,g[0])]
            weights=tuple(F((v*65536).numerator//(v*65536).denominator,65536) for v in updated)
        next_predictions.append(forward_oracle(native,cfg.semantics,weights,inputs)[0][0])
    assert next_predictions[0]>next_predictions[1]>F(1,2)
    assert models==320 and initial==7320 and soft==729 and 'torch' not in sys.modules
    return {'models':models,'initialized_predictions':initial,'independent_gradient_coordinates':gradients,
        'zero_coordinate_recoveries_on_matching_one_hot_labels':recoveries,'count_slot_cases':scale_cases,
        'soft_polynomial_value_checks':soft,'no_constant_output_gate':True,
        'old_and_new_learner_next_predictions':list(map(str,next_predictions))}


CASES=('transitive','opposite','incomplete','recover','slots','work','tight')
CUDA_CASES=CASES+('precision',)


def endpoint(path,case):
    n=3 if case=='recover' else 4 if case=='tight' else 6
    edges=tuple((i,i) for i in range(n)) if case in ('recover','tight') else ((0,1),(2,3),(4,5))
    cfg,old,_,train,_=fixture_parameters(n,groups=(0,)*n,edges=edges)
    needed=8 if case=='tight' else 4
    pattern=(F(1),F(8))+(F(1),)*needed
    _,_,_,grammar=configuration(n)
    grammar=replace(grammar,slots=4 if case=='slots' else len(pattern))
    cfg=replace(cfg,initializer_pattern=pattern,graph_limits=asdict(grammar),
        activation_cap=F(16 if case=='tight' else 64),normalizer_cap=F(18 if case=='tight' else 64))
    if case=='incomplete':
        train=tuple((values,label^int(at==8)) for at,(values,label) in enumerate(train))
    opposite=int(case=='opposite')
    latent=(0,0,opposite,opposite,opposite,opposite)
    fresh=((context(n,0,2),opposite),(context(n,2,4),0),(context(n,1,5),opposite)) if n==6 else ()
    if n==6:
        fresh+=tuple((context(n,i,j),latent[i]^latent[j]) for _ in range(2) for i,j in product(range(n),repeat=2))
    elif case=='recover':
        fresh=((context(n,0,1),0),(context(n,0,1),1),(context(n,0,2),0))
    else:
        fresh=((context(n,0,1),0),)
    old=replace(old,searches=(replace(old.searches[0],grammar=grammar,
        relation_sources=replace(old.searches[0].relation_sources,solver=SOLVER)),))
    run=run_contract(cfg,old,len(train)+len(fresh),len(fresh),unit=1,rate=F(4 if case=='recover' else 1))
    run=replace(run,float64=Float64Contract(F(1,100),F(1,100)),
        persistence=replace(run.persistence,rules=tuple(replace(r,bound=F(5)) for r in run.persistence.rules)))
    if path=='cpu' or case=='precision':
        rt=runtime(cfg,run,path,(len(train),))
    else:
        rules=tuple(replace(r,rule_id='cuda',score_path=CUDA_PATH) if r.score_path==FLOAT64_PATH else r
                    for r in run.persistence.rules)
        run=replace(run,persistence=replace(run.persistence,rules=rules),cpu_install=None)
        policy=CudaCompilerPolicy((CudaCompilationStep(len(train),'native',1,'ref','cuda'),))
        # Native values up to the declared64 scale need a separately stated
        # absolute budget; the probability tolerance remains1/100. The old
        # state/native1/100 refusal is kept as its own precision control.
        cuda=cuda_contract(state_atol=F(1,16),install=CudaInstallContract())
        rt=ReferenceCompilerRuntime(cfg,zero_program(2),online=run,policy=policy,cuda=cuda,
            host=HostResourceContract(HOST_CAP,{'deployment':HOST_CAP,'compiler':HOST_CAP}))
    if case=='work':
        original=rt._event_router.charge_work
        checks=[]
        def refuse(role,costs,note):
            if note.endswith(':empirical-upper-and-proposal'):
                prefix_slots=min(len(pattern),grammar.slots)
                expected=4096+64*sum(map(len,rt._buffers.values()))+64*len(pattern)*(len(train)+1)+64*n*n*(1+prefix_slots)
                assert costs=={'work':expected}
                checks.append(expected)
                raise ResourceExceeded('audit: joint orientation emission work unavailable')
            return original(role,costs,note)
        with patch.object(rt._event_router,'charge_work',refuse):
            ingest(rt,train)
        assert len(checks)==1
    else:
        ingest(rt,train)
    cutoff=validate_residency(rt);search,=cutoff.searches;proposed=search.relation_proposal
    predictions=[];recoveries=[]
    if case in ('slots','work'):
        assert not cutoff.reference_proofs and cutoff.alpha_spent==0
        assert proposed is None if case=='work' else proposed.program is None
        ingest(rt,fresh,start=len(train))
    else:
        assert proposed.program is not None and proposed.scale==8 and cutoff.alpha_spent==F(1,2)
        cid=search.best_candidate_id
        previous_zero=None
        for offset,(values,label) in enumerate(fresh):
            predicted=deliver_context(rt,f'observation-{len(train)+offset}',values)
            if case=='precision' and predicted.status=='UNRESOLVED':
                assert 'native prediction error exceeds' in predicted.reason
                break
            assert predicted.status=='PREDICTED_REFERENCE',predicted
            actual=dict(predicted.predictions)[cid]
            if offset<3:
                predictions.append(list(map(str,actual)))
            if n==6 and offset<2:
                assert actual==(F(1,2),F(1,2))
            if n==6 and offset==2:
                assert actual[opposite]==F(25981558417,45993308790)
            observed=rt.observe(label)
            if case=='tight':
                assert observed.status=='UNRESOLVED' and rt.snapshot().halted[0]=='observe'
                break
            assert observed.status=='OBSERVED_REFERENCE',observed
            if case=='recover' and offset<2:
                theta=next(c.theta for c in rt.snapshot().candidates if c.candidate_id==cid)
                if offset==0:
                    previous_zero=tuple(i for i,v in enumerate(theta) if i!=1 and v==0)
                    assert len(previous_zero)==2
                else:
                    assert all(theta[i]>0 for i in previous_zero)
                    recoveries=list(map(str,(theta[i] for i in previous_zero)))
    final=validate_residency(rt)
    if case=='tight':
        assert not final.install_receipts and final.run.status=='HALTED_UNRESOLVED'
    elif case=='precision':
        assert final.run.status=='HALTED_UNRESOLVED'
        assert all(r.attempt.cursor < final.cursor for r in final.install_receipts)
    else:
        assert final.run.status==('SEALED_CUDA_STREAM' if path=='cuda' else 'SEALED_REFERENCE_STREAM')
        decision,=final.run.closure.decisions
        assert decision.decision_status==('UNRESOLVED' if case in ('incomplete','slots','work') else 'HISTORICAL_REFERENCE_CLASS_BOUNDED')
        if case in ('transitive','opposite','incomplete'):
            assert len(final.install_receipts)==1
            assert final.install_receipts[0].attempt.proposal_proof_id==search.proof_id
        else:
            assert not final.install_receipts
    return rt,dict(case=case,path=path,first_three_predictions=predictions,recovered_parameters=recoveries,
        native_graph=None if proposed is None or proposed.program is None else proposed.program.counts(),
        class_status=search.status,reference_proofs=len(final.reference_proofs),alpha_spent=str(final.alpha_spent),
        install_cursors=[r.attempt.cursor for r in final.install_receipts],halted=final.halted)


def failed_prediction_audit(rt):
    snapshot=validate_residency(rt)
    assert snapshot.halted[0]=='predict' and snapshot.pending.record.target is None
    records=snapshot.cuda.phases
    last=records[-1]
    assert last.status=='UNRESOLVED' and last.phase=='ordinary:predict'
    assert 'native prediction error exceeds its registered bound' in last.reason
    assert last.relation is None and last.raw_state is not None and last.raw_prediction is not None
    assert all(r.status=='CHECKED_CUDA_PREFIX_PHASE' and r.relation is not None for r in records[:-1])
    graphs=dict(snapshot.programs);observed={o.observation_id:o for o in snapshot.observations}
    observed[snapshot.pending.record.observation_id]=snapshot.pending.record
    expected={};buffers=dict(snapshot.buffers)
    for record in records:
        graph=graphs[record.program_id];kind=record.phase.split(':')[1]
        before=None if record.input_phase is None else expected[record.input_phase]
        if kind=='initialize':
            result=model_initial(graph,rt.contract.semantics,record.reference.theta,record.reference.cursor)
        elif kind=='attach':
            result=replace(before,cursor=record.reference.cursor)
        elif kind=='predict':
            result=model_predict(graph,rt.contract.semantics,before,dict(observed[record.observation_id].sources))
            assert record.raw_prediction==raw_model_prediction(result) and record.raw_state==raw_model(before)
        elif kind=='observe':
            result=model_observe(graph,before,expected[record.prediction_phase],observed[record.observation_id].target)
        else:
            assert kind=='commit';result=model_commit(before,rt.online_contract.learner)
        if kind!='predict':
            assert record.raw_state==raw_model(result)
        expected[record.object_id]=result
        assert record.forward_operations==(forward_operations(graph,rt.contract.semantics) if kind=='predict' else 0)
        assert record.output_cells==output_cells(kind,graph,rt.contract.semantics,rt.online_contract.learner)<=snapshot.cuda.contract.phase_output_cells
        frame=buffers[record.object_id];size=int.from_bytes(frame[:8],'big')
        assert size>0 and phase_payload(snapshot,frame)==pack(record) and not any(frame[8+size:])
        assert len(frame)==snapshot.cuda.contract.phase_evidence_bytes and record.arena_phase is not None
    value=expected[last.object_id];ref=last.reference_prediction
    error=max(abs(a-b) for key in ('values','excesses','masses') for a,b in zip(getattr(ref,key),value[key]))
    norm_error=abs(ref.normalizer-value['normalizer'])
    probabilities=tuple(v/sum(value['masses']) for v in value['masses'])
    p_error=max(abs(a-b) for a,b in zip(ref.probabilities,probabilities))
    assert error>snapshot.cuda.contract.state_atol==F(1,100)
    assert p_error<snapshot.cuda.contract.probability_atol==F(1,100)
    assert last.object_id not in dict(snapshot.cuda.current).values()
    assert last.object_id not in dict(snapshot.cuda.staged).values()
    assert last.object_id not in dict(snapshot.cuda.predicted).values()
    for candidate in snapshot.candidates:
        state=expected[dict(snapshot.cuda.current)[candidate.candidate_id]]
        assert (state.unit,state.cursor,state.steps)==(candidate.learner.unit_count,candidate.learner.cursor,candidate.learner.optimizer_steps)
    return {'phases':len(records),'refused_prediction_independently_word_checked':True,
        'failed_native_error':str(error),'failed_normalizer_error':str(norm_error),'failed_probability_error':str(p_error),
        'refused_cursor':snapshot.cursor,'failed_prediction_never_accepted':True,
        'actual_arena_bytes':snapshot.cuda.storage['actual_tensor_arena_bytes'],
        'largest_phase_frame_used':max(int.from_bytes(buffers[r.object_id][:8],'big')+8 for r in records),
        'maximum_output_cells':max(r.output_cells for r in records)}


def worker(path,case):
    rt,result=endpoint(path,case)
    cpu=replay(rt)[0]
    cuda=(failed_prediction_audit(rt) if case=='precision' else audit_snapshot(rt)) if path=='cuda' else None
    assert cuda is None or cuda['phases']==cpu
    final=rt.snapshot()
    errors=lambda traces:{key:str(max((getattr(t.relation,key) for t in traces if t.relation is not None),default=F(0)))
        for key in ('state_error','native_error','normalizer_error','probability_error','division_error')}
    result.update(binary64_phases=cpu,CUDA=cuda,run_status=final.run.status,
        float64_relation_maxima=errors(final.float64_traces),
        host=host_record(final),peak_packed_bytes=final.resources['peak']['reference_payload_bytes'],process_id=os.getpid(),
        device=None if final.cuda is None else {'identity':asdict(final.cuda.device.identity),
            'physical_vram_upper':final.cuda.device.physical_vram_upper,'scope':final.cuda.device.scope},
        execution_identity=None if final.cuda is None else final.cuda.contract.execution_identity)
    if path=='cuda':
        result['registered_CUDA_tolerances']={'state_native_normalizer':str(final.cuda.contract.state_atol),'probability':str(final.cuda.contract.probability_atol)}
        result['CUDA_relation_maxima']=errors(final.cuda.phases)
    return result


def bounded(path,case):
    with tempfile.TemporaryDirectory(prefix='fp-joint-audit-',dir=ROOT) as temporary:
        assert Path(temporary).resolve().parent==ROOT
        output=Path(temporary)/'result.json'
        job=run_in_job(__file__,('--worker','--path',path,'--case',case,'--output',output),commit_limit=HOST_CAP,timeout_ms=1200000)
        assert job.exit_code==0 and not job.timed_out,(case,job,output.read_text(encoding='utf-8') if output.exists() else '')
        assert output.stat().st_size<=16384
        result=json.loads(output.read_text(encoding='utf-8'))
        assert result['process_id']==job.process_id and job.attached_before_resume
        assert max(job.peak_process_commit,job.peak_job_commit)<=HOST_CAP and not job.limit_terminated_processes
        host=result['host']
        assert (host['process_id'],host['creation_100ns'])==(job.process_id,job.process_creation_100ns)
        assert host['lifetime_process_commit_peak']<=job.peak_process_commit
        return dict(result,completed_job=asdict(job))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exact',action='store_true')
    parser.add_argument('--path',choices=('cpu','cuda'),default='cpu')
    parser.add_argument('--case',choices=CUDA_CASES)
    parser.add_argument('--worker',action='store_true')
    parser.add_argument('--output')
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    if args.exact:
        assert not (args.worker or args.case or args.output or args.write)
        print(json.dumps(exact_audit(),indent=2));return
    if args.worker:
        assert args.case and args.output and not args.write
        try:
            result=worker(args.path,args.case)
        except Exception:
            Path(args.output).write_text(traceback.format_exc()[-16384:],encoding='utf-8');raise
        Path(args.output).write_text(json.dumps(result),encoding='utf-8');return
    assert not args.output and (not args.write or args.case is None)
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if args.write:
        assert not subprocess.check_output(['git','diff','HEAD','--','src','scripts'],cwd=ROOT)
        assert not subprocess.check_output(['git','ls-files','--others','--exclude-standard','--','src','scripts'],cwd=ROOT)
    report={'source_revision':source,'exact':exact_audit() if args.case is None else None,'workers':[]}
    selected=CUDA_CASES if args.path=='cuda' else CASES
    assert args.case is None or args.case in selected
    for case in selected if args.case is None else (args.case,):
        result=bounded(args.path,case)
        if report['workers']:
            assert result['device']==report['workers'][0]['device'] and result['execution_identity']==report['workers'][0]['execution_identity']
        report['workers'].append(result)
        print(args.path+' '+case+': '+result['run_status'],flush=True)
    if args.write:
        output=ROOT/'evidence/minimal'/('FP_JOINT_POLYNOMIAL_'+args.path.upper()+'_AUDIT.json')
        output.write_text(json.dumps(report,indent=1)+'\n',encoding='utf-8')
    print(json.dumps({'workers':len(report['workers']),'binary64_phases':sum(r['binary64_phases'] for r in report['workers']),'exact':report['exact']},indent=2))


if __name__=='__main__':
    main()
