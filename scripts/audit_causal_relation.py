"""Native posterior proposals: exact guidance, causal warmup and owned selection.

The deterministic tapes exercise reachability and path correctness. They do
not establish a population model, a noise estimator or a complete search.
"""
import argparse
from dataclasses import asdict,replace
from fractions import Fraction as F
from itertools import product
import json
from math import prod
import os
from pathlib import Path
import sys
import tempfile
import traceback
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src/reference_compiler'),str(ROOT/'scripts'),str(ROOT/'experiments/joint_uncertainty')]
from fp_reference import ReferenceCompilerRuntime,CompilerPolicy,CompilationStep,CudaCompilerPolicy,CudaCompilationStep
from fp_reference.cuda_installation import CudaInstallContract
from fp_reference.causal_relation_proposal import SOLVER,causal_relation_proposal,literal_counts,proposal_work_bound
from fp_reference.data_usage import ObservationRecord,StochasticStreamLaw
from fp_reference.empirical_bound import empirical_upper
from fp_reference.installation import CpuInstallContract
from fp_reference.host_resources import HostResourceContract
from fp_reference.native_search import GrammarCursor,GrammarLimits
from fp_reference.profile import ProfileSpec
from fp_reference.persistence import CUDA_PATH,FLOAT64_PATH,REFERENCE_PATH
from fp_reference.program import Binding,Program,Sum
from fp_reference.relation_proposal import RelationSourceSpec,relation_proposal
from fp_reference.resources import ResourceExceeded
from fp_reference.search import ReferenceSearchSpec,likelihood
from fp_reference.semantics import ArithmeticUnresolved,evaluate,reset_delayed
from audit_reference_construction import limits,validate_residency,rejects
from audit_float64_runtime import replay
from audit_paired_cpu_persistence import registration
from ingress_audit_support import deliver_context
import recurrent_control as control

CASES=(('cpu','full'),('cpu','twice'),('cuda','full'),('cuda','twice'))
HOST_CAPS={'cpu':512<<20,'cuda':4<<30}
TIMEOUT=300000
OUTPUT=ROOT/'evidence/minimal/FP_CAUSAL_RELATION_PROPOSAL_AUDIT.json'
FAILURE=ROOT/'evidence/minimal/FP_CAUSAL_RELATION_PROPOSAL_REPORT_FAILURE.json'
DEPENDENCIES=('src/reference_compiler','scripts','experiments/joint_uncertainty/recurrent_control.py',
    'evidence/minimal/FP_CAUSAL_RELATION_PROPOSAL_REPORT_FAILURE.json')
TAPE=((0,1,0),)*40+((1,2,0),(0,2,0),(0,1,1),(0,2,1))
AMP_NATIVE_ATOL=F(8)
AMP_PROBABILITY_ATOL=F(1,10000)


def fixture(n=3,window=3,horizon=20,pattern=(F(1),F(8))):
    cfg,_,online,_=control.fixture(n,window,horizon)
    rules=replace(cfg.semantics,base=(F(1),F(1)))
    # Broad whole-native grammar, including all declared binding choices.
    bounds=GrammarLimits(**{k:2*v+8 for k,v in literal_counts(n,1<<(n-1),window,1,len(pattern)).items()})
    cfg=replace(cfg,semantics=rules,initializer_pattern=pattern,graph_limits=asdict(bounds))
    source=RelationSourceSpec(tuple((f'now0:{i}',f'now1:{i}') for i in range(n)),SOLVER)
    return cfg,online,bounds,source


def records(cfg,online,tape):
    n=len(online.data.input_upper)//2
    result=[]
    for at,(i,j,y) in enumerate(tape):
        inputs=control.context(n,i,j)
        old=(F(0),)*(2*n+2) if at==0 else control.context(n,*tape[at-1][:2])+(F(tape[at-1][2]==0),F(tape[at-1][2]==1))
        result.append(ObservationRecord(online.data.active.observation_ids[at],'online','online',at,
            inputs,tuple(zip((s.source_id for s in cfg.semantics.sources),inputs+old)),y))
    return tuple(result)


def propose(cfg,online,bounds,source,tape,profile='full',**changes):
    rows=records(cfg,online,tape)
    if profile=='full':profile=ProfileSpec('warm',tuple(r.observation_id for r in rows),1)
    kwargs=dict(data=online.data,learner=online.learner,source_domain=cfg.source_domain,
        range_cap=min(cfg.activation_cap,cfg.normalizer_cap),profile=profile,
        ordinary_cursor=len(tape),bit_limit=cfg.reference_integer_bits)
    kwargs.update(changes)
    return causal_relation_proposal(empirical_upper(rows,cfg.semantics,bit_limit=32768),cfg.semantics,
        bounds,cfg.initializer_pattern,source,**kwargs),rows,profile


def marginal(n,tape,s):
    return sum(prod(F(1+s if z[i]^z[j]==y else 1,2+s) for i,j,y in tape)
        for z in product((0,1),repeat=n))/2**n


def posterior(n,tape,i,j,s):
    worlds=tuple(product((0,1),repeat=n))
    weights=tuple(prod((1+s if z[a]^z[b]==y else F(1)) for a,b,y in tape) for z in worlds)
    p=sum(w*F(1+s if z[i]==z[j] else 1,2+s) for z,w in zip(worlds,weights))/sum(weights)
    return p,1-p


def replay_values(cfg,graph,rows,profile):
    delayed=reset_delayed(cfg.semantics)
    if profile is not None:
        by_id={r.observation_id:r for r in rows}
        for _ in range(profile.passes):
            for key in profile.observation_ids:
                delayed=evaluate(graph,cfg.semantics,cfg.initializer_pattern[:graph.slot_count],
                    dict(by_id[key].sources),delayed,bit_limit=32768).delayed
    return delayed


def exact_audit():
    scores=ties=forecasts=profiles=0
    for n in (2,3):
        cfg,online,bounds,source=fixture(n,2,pattern=(F(1),F(0),F(2),F(8)))
        events=tuple(product(range(n),range(n),(0,1)))
        for tape in product(events,repeat=2):
            proposal,_,_=propose(cfg,online,bounds,source,tape)
            assert proposal.program is not None
            expected=tuple(marginal(n,tape,s) for s in cfg.initializer_pattern)
            assert tuple(row[2] for row in proposal.guidance)==expected
            assert proposal.noise_slot==expected.index(max(expected))
            scores+=len(expected)
            if len(set(expected))==1:ties+=1
    # Independently verify full and suffix profile warmup against all latent
    # assignments, including signs, cycles, repeats, diagonals and eviction.
    bad_warmup=None
    cfg,online,bounds,source=fixture()
    for queries in (((0,1),(1,2),(0,2),(0,1)),((0,0),(0,1),(0,1),(1,1))):
        for labels in product((0,1),repeat=4):
            tape=tuple((i,j,y) for (i,j),y in zip(queries,labels))
            ids=online.data.active.observation_ids[:4]
            for spec,expected_window in ((ProfileSpec('full',ids,1),3),
                    (ProfileSpec('suffix',ids[-2:],1),3),(ProfileSpec('short',ids[-1:],1),2),
                    (ProfileSpec('reverse',ids[::-1],1),1),(ProfileSpec('twice',ids,2),3),
                    (ProfileSpec('mixed-prefix',ids[1::-1]+ids[2:],1),3),(None,1)):
                proposal,rows,_=propose(cfg,online,bounds,source,tape,spec)
                assert proposal.window==expected_window
                graph=proposal.program;theta=cfg.initializer_pattern[:graph.slot_count]
                assert all(graph.counts()[k]==v for k,v in literal_counts(3,4,proposal.window,1,len(theta)).items())
                delayed=replay_values(cfg,graph,rows,spec)
                old=control.context(3,*tape[-1][:2])+(F(tape[-1][2]==0),F(tape[-1][2]==1))
                for i,j in product(range(3),repeat=2):
                    sources=dict(zip((s.source_id for s in cfg.semantics.sources),control.context(3,i,j)+old))
                    actual=evaluate(graph,cfg.semantics,theta,sources,delayed,bit_limit=32768).probabilities
                    assert actual==posterior(3,tape[-proposal.window:],i,j,proposal.scale)
                    forecasts+=1
                profiles+=1
            if bad_warmup is None:
                p,rows,_=propose(cfg,online,bounds,source,tape)
                wrong=replay_values(cfg,p.program,rows,ProfileSpec('wrong',ids[::-1],1))
                for i,j in product(range(3),repeat=2):
                    sources=dict(zip((s.source_id for s in cfg.semantics.sources),control.context(3,i,j)+old))
                    actual=evaluate(p.program,cfg.semantics,cfg.initializer_pattern[:p.program.slot_count],sources,wrong,bit_limit=32768).probabilities
                    expected=posterior(3,tape[-p.window:],i,j,p.scale)
                    if actual!=expected:
                        bad_warmup={'history':tape,'query':(i,j),'wrong':str(actual[0]),'suffix':str(expected[0])}
                        break
    assert bad_warmup is not None
    # Before the second event the proper initial delayed state is still zero;
    # the previous label itself arrives through the already registered source.
    p,_,_=propose(cfg,online,bounds,source,((0,1,0),),None)
    assert p.window==3
    # A multi-pass replay has no fresh zero-start premise at each pass. Its
    # extra old factor reaches a long enough stage even with a correct tail.
    cfg,online,bounds,source=fixture(2,4)
    tape=((0,1,0),)*2;ids=online.data.active.observation_ids[:2]
    once,rows,_=propose(cfg,online,bounds,source,tape)
    twice=ProfileSpec('twice',ids,2)
    p,_,_=propose(cfg,online,bounds,source,tape,twice)
    assert once.window==4 and p.window==3
    wrong=replay_values(cfg,once.program,rows,twice)
    values=control.context(2,0,1)*2+(F(1),F(0))
    actual=evaluate(once.program,cfg.semantics,cfg.initializer_pattern,dict(zip((s.source_id for s in cfg.semantics.sources),values)),wrong,bit_limit=32768).probabilities[0]
    expected=posterior(2,tape,0,1,once.scale)[0]
    assert actual==F(3281,3650) and expected==F(73,82)
    assert 'torch' not in sys.modules
    return {'exact_guidance_scores':scores,'uninformative_tie_cases':ties,
        'profile_plans':profiles,'native_window_forecasts':forecasts,
        'shuffled_profile_counterexample':bad_warmup,
        'repeated_profile_without_reset_counterexample':{'wrong_H4':str(actual),'correct':str(expected),'accepted_window':p.window}}


def refusal_audit():
    cfg,online,bounds,source=fixture()
    tape=((0,1,0),)*3
    def call(**kwargs):return propose(cfg,online,bounds,source,tape,**kwargs)[0]
    assert call(learner=replace(online.learner,learning_rate=F(1))).program is None
    assert call(source_domain=None).program is None
    bad=tuple(F(0) for _ in cfg.semantics.sources)
    assert call(source_domain=(bad,)).program is None
    missing=replace(online.data,source_reads=online.data.source_reads[:-1])
    assert call(data=missing).program is None
    p,_,_=propose(replace(cfg,initializer_pattern=(F(8),)),online,bounds,source,tape)
    assert p.program is None
    p,_,_=propose(cfg,online,replace(bounds,nodes=3),source,tape)
    assert p.program is None
    assert call(range_cap=F(1)).program is None
    rejects(lambda:call(bit_limit=4),ArithmeticUnresolved)
    p,rows,_=propose(cfg,online,bounds,source,tape)
    static=relation_proposal(empirical_upper(rows,cfg.semantics,bit_limit=32768),cfg.semantics,bounds,
        cfg.initializer_pattern,source,bit_limit=32768)
    assert static.program is None and 'complete registered' in static.reason
    # Loose declared ranges, unlike attained zero-start values, constrain the
    # next body's invariant. U1=9 requires U2>=89 for s8, not the nominal80.
    loose=replace(cfg,semantics=replace(cfg.semantics,states=tuple(replace(st,upper=F(9) if st.upper==8 else st.upper)
        for st in cfg.semantics.states)))
    q,_,_=propose(loose,online,bounds,source,tape)
    assert q.scale==8 and q.window==2
    # Zero-rate commits still round an off-grid noise slot. No witness may
    # retain that slot under the unchanged recurrence claim.
    third=replace(cfg,initializer_pattern=(F(1),F(1,3)))
    q,_,_=propose(third,replace(online,learner=replace(online.learner,commit_grid_bits=4)),bounds,source,tape)
    assert q.guidance[1]==(1,F(1,3),None,0) and q.noise_slot==0
    assert 'torch' not in sys.modules
    return {'source_learner_work_range_slot_context_controls':11,'loose_state_box_reduces_window':True,
        'zero_rate_commit_grid_is_not_identity':True}


def authority_audit():
    checked=0
    for case in ('work','fake-guidance'):
        cfg,online,bounds,source=fixture(2,1,4)
        ids=online.data.active.observation_ids
        profile=ProfileSpec('warm',ids[:3],1)
        spec=ReferenceSearchSpec('native',bounds,ids[:3],profile.profile_id,relation_sources=source)
        online=replace(online,profiles=(profile,),searches=(spec,))
        rt=ReferenceCompilerRuntime(cfg,Program((Sum('mass',()),),0,(0,0)),online=online)
        for at in range(3):
            assert deliver_context(rt,ids[at],control.context(2,0,1)).status=='PREDICTED_REFERENCE'
            assert rt.observe(0).status=='OBSERVED_REFERENCE'
        start=rt.start_reference_search('native');before=rt.snapshot()
        if case=='work':
            original=rt._event_router.charge_work
            def debit(role,cost,reason):
                if reason.endswith(':empirical-upper-and-proposal'):
                    assert cost['work']>=proposal_work_bound(2,len(cfg.semantics.sources),0,len(cfg.source_domain),bounds,2,3,3)
                    raise ResourceExceeded('adversarial prepaid proposal work refusal')
                return original(role,cost,reason)
            with patch.object(rt._event_router,'charge_work',side_effect=debit),patch('fp_reference.runtime.causal_relation_proposal',side_effect=AssertionError('unpaid proposal executed')):
                result=rt.advance_reference_search(start.search_id,transitions=1)
            after=rt.snapshot()
            assert result.status=='UNRESOLVED' and not result.proof_id
            assert after.observations==before.observations and after.next_candidate==before.next_candidate
            assert after.searches[0].empirical_upper is None and after.searches[0].relation_proposal is None
        else:
            def forged(*args,**kwargs):
                p=causal_relation_proposal(*args,**kwargs)
                return replace(p,status='CERTIFIED_COMPLETE',scale=F(999),guidance=((0,F(999),F(1),1),))
            with patch('fp_reference.runtime.causal_relation_proposal',side_effect=forged):
                result=rt.advance_reference_search(start.search_id,transitions=1)
            after=rt.snapshot();session=after.searches[0]
            assert result.status=='UNRESOLVED' and not result.proof_id and not after.reference_proofs
            assert session.relation_proposal.status=='CERTIFIED_COMPLETE'
            assert session.cursor==GrammarCursor() and len(session.rows)==1
            candidate=next(c for c in after.candidates if c.candidate_id==session.best_candidate_id)
            assert candidate.theta==(F(1),F(8)) and candidate.learner==after.profiles[0].attached
            actual=likelihood(session.rows[0].program,cfg.semantics,candidate.learner,after.observations,bit_limit=32768)
            assert actual==session.best_likelihood<session.empirical_upper.likelihood
        validate_residency(rt);checked+=1
    return {'owned_adversarial_searches':checked,'unpaid_proposal_not_called':True,
        'forged_metadata_not_class_or_value_authority':True}


def rounded_preflight():
    from audit_cuda_runtime import raw_model
    from fp_reference.cuda_range import enclose_cuda
    cfg,online,bounds,source=fixture(horizon=len(TAPE))
    proposal,rows,_=propose(cfg,online,bounds,source,TAPE[:3])
    graph=proposal.program;theta=cfg.initializer_pattern[:graph.slot_count]
    all_rows=records(cfg,online,TAPE)
    maxima={k:F(0) for k in ('values','masses','normalizer','probability','gradient','raw_division')}
    forecasts=0
    for passes in (1,2):
        amp=control.model_initial(graph,cfg.semantics,theta,0)
        delayed=reset_delayed(cfg.semantics)
        for row in rows*passes+all_rows[3:]:
            point=dict(row.sources)
            ref=evaluate(graph,cfg.semantics,theta,point,delayed,bit_limit=32768)
            p,g=control.forward_oracle(graph,cfg.semantics,theta,point,delayed)
            actual=control.model_predict(graph,cfg.semantics,amp,point)
            assert actual['delayed']==ref.delayed
            for key in ('values','masses'):
                maxima[key]=max(maxima[key],*(abs(a-b) for a,b in zip(actual[key],getattr(ref,key))))
            maxima['normalizer']=max(maxima['normalizer'],abs(actual['normalizer']-ref.normalizer))
            masses=tuple(v/sum(actual['masses']) for v in actual['masses'])
            maxima['probability']=max(maxima['probability'],*(abs(a-b) for a,b in zip(masses,p)))
            maxima['raw_division']=max(maxima['raw_division'],*(abs(a-b) for a,b in zip(actual['probabilities'],masses)))
            amp=control.model_observe(graph,amp,actual,row.target)
            maxima['gradient']=max(maxima['gradient'],*(abs(a-b) for a,b in zip(amp.gradient,g[row.target])))
            amp=control.model_commit(amp,online.learner)
            assert amp.theta==theta
            delayed=ref.delayed;forecasts+=1
    raw=raw_model(control.model_initial(graph,cfg.semantics,theta,0))
    envelopes=tuple(enclose_cuda(graph,cfg.semantics,raw,source_point=row,
        normalizer_cap=cfg.normalizer_cap,activation_cap=cfg.activation_cap,bit_limit=32768) for row in cfg.source_domain)
    assert max(maxima[k] for k in ('values','masses','normalizer','gradient'))<=AMP_NATIVE_ATOL
    assert maxima['probability']<AMP_PROBABILITY_ATOL and 'torch' not in sys.modules
    assert maxima['masses']==3 and maxima['normalizer']==3
    return {'rounded_interpreter_forecasts':forecasts,'maximum_errors':{k:str(v) for k,v in maxima.items()},
        'master_parameters_and_delayed_states_exact':True,'whole_source_domain_boxes':len(envelopes),
        'maximum_rounded_normalizer_upper':str(max(b.rounded_normalizer_upper for b in envelopes)),
        'actual_CUDA_execution':False}


def owned(path='cpu',case='full',bounded=False):
    assert path in ('cpu','cuda') and case in ('full','twice')
    cfg,online,bounds,source=fixture(horizon=44)
    cut=3
    ids=online.data.active.observation_ids
    profile=ProfileSpec('warm',ids[:cut],1 if case=='full' else 2)
    spec=ReferenceSearchSpec('native',bounds,ids[:cut],profile.profile_id,relation_sources=source)
    online=replace(online,profiles=(profile,),searches=(spec,),cpu_install=CpuInstallContract(),
        persistence=registration(bound=F(11),horizon=40),
        data=replace(online.data,stream_law=StochasticStreamLaw('external branch-invariant stochastic relation producer; audit tape alone proves no probability law')))
    zero=Program((Sum('mass',()),),0,(0,0),tuple(Binding(st.state_id,0) for st in cfg.semantics.states))
    cuda=None
    policy=CompilerPolicy((CompilationStep(cut,'native',1,'ref','finite'),))
    if path=='cuda':
        from audit_cuda_runtime import cuda_contract
        online=replace(online,cpu_install=None,persistence=replace(online.persistence,rules=tuple(
            replace(r,rule_id='cuda',score_path=CUDA_PATH) if r.score_path==FLOAT64_PATH else r for r in online.persistence.rules)))
        cuda=cuda_contract(install=CudaInstallContract(),state_atol=AMP_NATIVE_ATOL,probability_atol=AMP_PROBABILITY_ATOL)
        policy=CudaCompilerPolicy((CudaCompilationStep(cut,'native',1,'ref','cuda'),))
    cap=HOST_CAPS[path]
    host=HostResourceContract(cap,{'deployment':cap,'compiler':cap}) if bounded else None
    rt=ReferenceCompilerRuntime(cfg,zero,online=online,policy=policy,cuda=cuda,host=host)
    tape=TAPE
    forecasts=[];candidate_id=None;proposal=None;history=[];score_inputs={}
    for at,(i,j,y) in enumerate(tape):
        event=deliver_context(rt,ids[at],control.context(3,i,j))
        assert event.status=='PREDICTED_REFERENCE',event
        snap=rt.snapshot()
        assert snap.pending.record.target is None
        if candidate_id is not None:
            predictions=dict(event.predictions)
            assert predictions[candidate_id]==posterior(3,history[-proposal.window:],i,j,proposal.scale)
            score_inputs[ids[at],REFERENCE_PATH]=(predictions[base_id][y],predictions[candidate_id][y])
            if path=='cuda':
                from audit_cuda_runtime import HALF,SINGLE
                physical=next(p for p in reversed(snap.cuda.phases) if p.raw_prediction is not None
                    and p.observation_id==ids[at] and p.candidate_id==candidate_id)
                assert tuple(SINGLE.decode(w) for w in physical.raw_state[0])==cfg.initializer_pattern
                delayed=tuple((key,tuple(HALF.decode(w) for w in values)) for key,values in physical.raw_prediction[6])
                assert delayed==physical.reference_prediction.delayed
                values=[]
                for key in (base_id,candidate_id):
                    phase=next(p for p in reversed(snap.cuda.phases) if p.raw_prediction is not None
                        and p.observation_id==ids[at] and p.candidate_id==key)
                    masses=tuple(SINGLE.decode(w) for w in phase.raw_prediction[3])
                    values.append(masses[y]/sum(masses))
                score_inputs[ids[at],CUDA_PATH]=tuple(values)
            else:
                physical=dict(snap.pending.float64_predictions)
                score_inputs[ids[at],FLOAT64_PATH]=tuple(physical[key].masses[y].exact/sum(v.exact for v in physical[key].masses)
                    for key in (base_id,candidate_id))
        forecasts.append(str(dict(event.predictions)[snap.deployed_id][0]))
        assert rt.observe(y).status=='OBSERVED_REFERENCE'
        history.append((i,j,y))
        if at+1==cut:
            snap=rt.snapshot();session=snap.searches[0];proposal=session.relation_proposal
            assert session.status=='UNRESOLVED' and not session.proof_id and session.cursor==GrammarCursor()
            assert len(session.rows)==1 and session.rows[0].status=='COMPARED_REFERENCE'
            candidate_id=session.best_candidate_id
            base_id=session.base_lineage_id
            assert candidate_id!=session.base_lineage_id and proposal.window==3 and proposal.scale==8
            candidate=next(c for c in snap.candidates if c.candidate_id==candidate_id)
            assert candidate.profile_id==profile.profile_id and candidate.birth_cursor==cut
            assert candidate.theta==cfg.initializer_pattern
            assert candidate.learner==snap.profiles[0].attached
            assert candidate.learner.optimizer_steps==profile.event_count
            assert session.best_likelihood==likelihood(proposal.program,cfg.semantics,candidate.learner,snap.observations,bit_limit=32768)
            assert len(snap.persistence_identities)==2
            assert all(x.start_cursor==cut and x.wealth==1 and x.status=='ACTIVE' for x in snap.persistence_identities)
    final=validate_residency(rt)
    assert final.run.status==('SEALED_REFERENCE_STREAM' if path=='cpu' else 'SEALED_CUDA_STREAM') and final.halted is None
    assert len(final.install_receipts)==1 and not final.reference_proofs
    assert final.deployed_id==candidate_id and len(final.observations)==44
    assert all(d.decision_status=='UNRESOLVED' and d.proof is None for d in final.run.closure.decisions)
    from audit_reference_persistence import check_gain,wealth_oracle
    crossing={};wealth={p.identity_id:F(1) for p in final.persistence_identities}
    identity={p.identity_id:p for p in final.persistence_identities}
    for event in final.persistence_events:
        rule=identity[event.identity_id].rule
        assert event.cursor>=cut and event.epoch_finished and event.wealth_before==wealth[event.identity_id]
        assert (event.base_probability,event.candidate_probability)==score_inputs[event.observation_id,rule.score_path]
        check_gain(event)
        assert event.wealth_after==wealth_oracle(event.wealth_before,event.gain.lower,1,rule)
        wealth[event.identity_id]=event.wealth_after
        if event.wealth_after*rule.alpha>=1:crossing.setdefault(event.identity_id,event.cursor+1)
    assert len(crossing)==2
    assert all(crossing[p.identity_id]==p.crossing_cursor for p in final.persistence_identities)
    assert final.install_receipts[0].attempt.cursor==max(crossing.values())
    assert final.alpha_spent==F(1,2)
    phases=replay(rt)[0]
    cuda_audit=None
    if path=='cuda':
        from audit_cuda_runtime import audit_snapshot
        cuda_audit=audit_snapshot(rt)
        assert cuda_audit['phases']==phases
    else:
        assert 'torch' not in sys.modules
    final=validate_residency(rt)
    resource=final.host_resources
    host=None if resource is None else {key:getattr(resource,key) for key in
        ('process_id','creation_100ns','lifetime_process_commit_peak','job_commit_peak',
         'process_user_100ns','process_kernel_100ns','job_user_100ns','job_kernel_100ns')}
    maxima=lambda traces:{key:str(max((getattr(t.relation,key) for t in traces if t.relation is not None),default=F(0)))
        for key in ('state_error','native_error','normalizer_error','probability_error','division_error')}
    return {'run_status':final.run.status,'independent_binary64_phases':phases,
        'native_graph':proposal.program.counts(),'window':proposal.window,'noise_slot':proposal.noise_slot,
        'profile_events':profile.event_count,'historical_class_decision':'UNRESOLVED',
        'independent_fresh_score_and_wealth_checks':len(final.persistence_events),
        'terminal_search_status':final.searches[0].status,'install_cursor':final.install_receipts[0].attempt.cursor,
        'deployed_forecasts_p0':forecasts,'retained_observations':len(final.observations),
        'CUDA_audit':cuda_audit,'binary64_relation_maxima':maxima(final.float64_traces),
        'CUDA_relation_maxima':None if final.cuda is None else maxima(final.cuda.phases),
        'packed_peak':final.resources['peak']['reference_payload_bytes'],
        'consumed_arena_extent':None if final.cuda is None else final.cuda.storage['consumed_arena_extent'],
        'device':None if final.cuda is None else {'identity':asdict(final.cuda.device.identity),
            'execution_identity':final.cuda.contract.execution_identity,'physical_vram_upper':final.cuda.device.physical_vram_upper,
            'scope':final.cuda.device.scope},'host':host,
        'host_scope':'bound to completed job separately' if bounded else 'functional execution; no source-bound host-job claim'}


def preflight():
    from audit_cuda_runtime import cuda_contract
    cuda=cuda_contract(install=CudaInstallContract(),state_atol=AMP_NATIVE_ATOL,probability_atol=AMP_PROBABILITY_ATOL)
    cfg,online,grammar,_=fixture(horizon=44)
    return {'cases':CASES,'host_caps':HOST_CAPS,'timeout_ms':TIMEOUT,
        'source_domain_rows':len(cfg.source_domain),'grammar':asdict(grammar),
        'initializer':list(map(str,cfg.initializer_pattern)),'learner':{'rate':'0','unit':1,'grid':None},
        'range_cap':str(cfg.normalizer_cap),'packed_cap':256<<20,'work_per_role':10**10,
        'native_arena_bytes':cuda.storage.arena_bytes,'native_allocator_bytes':cuda.storage.allocator_reserved_cap,
        'output_cells':cuda.phase_output_cells,'phase_evidence_bytes':cuda.phase_evidence_bytes,
        'state_native_normalizer_tolerance':str(cuda.state_atol),'probability_tolerance':str(cuda.probability_atol),
        'fresh':{'cut':3,'epochs':40,'gain_bound':'11','bet':'3/4','alpha_per_path':'1/4','alpha_total':'3/4'},
        'ordinary_events':44,'scope':'owned native construction, actual profiles and paired installation; deterministic correctness tapes, no population/noise-identification or full-class optimum'}


def bounded(write,resume):
    from windows_job_audit_support import run_in_job
    source=control.git('rev-parse','HEAD')
    def source_clean():
        assert control.git('rev-parse','HEAD')==source
        assert not control.git('status','--porcelain','--',*DEPENDENCIES)
    source_clean()
    registration=json.loads(json.dumps(preflight()))
    if resume:
        report=json.loads(OUTPUT.read_text(encoding='utf-8'))
        assert report['status']=='PARTIAL_EXECUTION' and report['registration_source']==source
        assert report['registration']==registration
        assert [r['case_index'] for r in report['workers']]==list(range(len(report['workers'])))
    else:
        assert not write or not OUTPUT.exists(),'retain previous evidence; do not silently repeat registered jobs'
        report={'status':'PARTIAL_EXECUTION','registration_source':source,'registration':registration,'workers':[]}
        failure=json.loads(FAILURE.read_text(encoding='utf-8'))
        assert len(failure['workers'])==4 and all(r['worker_status']=='FAILED' for r in failure['workers'])
        assert failure['registration']==registration
        report['prior_report_failure']={'journal':FAILURE.relative_to(ROOT).as_posix(),
            'source':failure['registration_source'],'completed_failed_jobs':4,
            'correction':'parent binds unchanged source before/after every job; remove forbidden child Git query after owned audit; all cases/resources/tolerances unchanged'}
    def publish():
        if write:
            temp=OUTPUT.with_suffix('.tmp')
            temp.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
            temp.replace(OUTPUT)
    publish()
    for index in range(len(report['workers']),len(CASES)):
        path,case=CASES[index]
        source_clean()
        with tempfile.TemporaryDirectory(prefix='fp-causal-proposal-',dir=ROOT) as temporary:
            assert Path(temporary).resolve().parent==ROOT.resolve()
            output=Path(temporary)/'result.json'
            job=run_in_job(__file__,('--worker',str(index),'--output',str(output)),
                commit_limit=HOST_CAPS[path],timeout_ms=TIMEOUT)
            row={'case_index':index,'path':path,'case':case,'worker_status':'FAILED','completed_job':asdict(job),'execution_source':source}
            try:
                if output.exists():
                    with output.open('rb') as stream:payload=stream.read(65537)
                    assert len(payload)<=65536
                    row['result']=json.loads(payload)
                if job.exit_code==0 and not job.timed_out:
                    result=row['result'];observed=result['host']
                    assert result['process_id']==job.process_id
                    assert (observed['process_id'],observed['creation_100ns'])==(job.process_id,job.process_creation_100ns)
                    assert observed['lifetime_process_commit_peak']<=job.peak_process_commit<=HOST_CAPS[path]
                    assert observed['job_commit_peak']<=job.peak_job_commit<=HOST_CAPS[path]
                    for clock in ('user','kernel'):
                        assert max(observed[f'process_{clock}_100ns'],observed[f'job_{clock}_100ns'])<=getattr(job,f'{clock}_100ns')
                    row['worker_status']='EXECUTED'
            except Exception:
                row['audit_failure']=traceback.format_exc()
            report['workers'].append(row)
        source_clean();publish()
        print(json.dumps({'case':index,'status':row['worker_status']}),flush=True)
    report['status']='COMPLETE_EXECUTION';publish()
    return {'status':report['status'],'attempts':len(report['workers']),
        'executed':sum(r['worker_status']=='EXECUTED' for r in report['workers'])}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cpu',action='store_true')
    parser.add_argument('--authority',action='store_true')
    parser.add_argument('--preflight',action='store_true')
    parser.add_argument('--rounded',action='store_true')
    parser.add_argument('--bounded',action='store_true')
    parser.add_argument('--write',action='store_true')
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--worker',type=int,choices=range(len(CASES)))
    parser.add_argument('--output')
    args=parser.parse_args()
    assert not args.resume or args.write and args.bounded
    assert not args.write or args.bounded
    assert bool(args.output)==(args.worker is not None)
    if args.worker is not None:
        try:
            path,case=CASES[args.worker]
            result=owned(path,case,True)
            # The job admits one active process. Source identity is bound by
            # the parent's checks around this complete job, never by spawning
            # Git from the measured worker after its owned execution.
            result.update(process_id=os.getpid())
        except Exception:
            Path(args.output).write_text(json.dumps({'traceback':traceback.format_exc(),'process_id':os.getpid()}),encoding='utf-8')
            raise
        Path(args.output).write_text(json.dumps(result),encoding='utf-8')
    else:
        print(json.dumps(bounded(args.write,args.resume) if args.bounded else preflight() if args.preflight else
            rounded_preflight() if args.rounded else owned() if args.cpu else authority_audit() if args.authority else
            {'exact':exact_audit(),'refusals':refusal_audit()},indent=2))
