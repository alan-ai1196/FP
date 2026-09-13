"""Adversarial exact audits of the new U and its complete constructor class.

The affine posterior formula is an independent oracle. Exhaustive search
retains programs whose actual initializer cannot supply the declared block.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'),
               str(ROOT/'experiments/joint_uncertainty')]
import simplex_gradient as model
from audit_simplex_learner import fixture
from audit_reference_construction import rejects, validate_residency
from audit_reference_search import brute_grammar, finish
from ingress_audit_support import deliver_context
from fp_reference import ReferenceCompilerRuntime
from fp_reference.core import ContractError
from fp_reference.empirical_bound import empirical_upper
from fp_reference.learner import (SIMPLEX_GRADIENT, LearnerSpec, ReferenceLearnerState,
                                  initial_state, observe_event, commit_event)
from fp_reference.native_search import GrammarLimits
from fp_reference.program import Program, Sum, Term
from fp_reference.relation_proposal import RelationSourceSpec, relation_proposal
from fp_reference.search import ReferenceSearchSpec
from fp_reference.semantics import ArithmeticUnresolved
from fp_reference.simplex_relation_proposal import SOLVER, simplex_relation_proposal


def arithmetic():
    checked = 0
    # Noncontiguous mutable slots ensure fixed coordinates are not implicit
    # optimizer padding. Every ambient native gradient is still accumulated.
    slots = (1, 3, 4)
    weight_cases = ((F(1,3),)*3, (F(1,2),F(1,3),F(1,6)), (F(0),F(1,2),F(1,2)))
    columns_cases = (((0,3),(1,2),(3,0)), ((0,0),(0,0),(0,0)),
                     ((0,1,2),(2,1,0),(1,0,2)))
    for columns in columns_cases:
        base = tuple(range(1,len(columns[0])+1))
        for weights in weight_cases:
            graph, prediction = model.affine_evaluation(columns, base, weights)
            nodes = tuple(Sum(node.type_id,tuple(Term(t.parent,slots[t.slot]) for t in node.terms))
                          if type(node) is Sum else node for node in graph.nodes)
            graph = Program(nodes,5,graph.heads)
            theta = (F(2),weights[0],F(3),weights[1],weights[2])
            initial = ReferenceLearnerState(theta,(),(F(0),)*5,0,0,0)
            for unit in (1,2,3):
                for labels in product(range(len(base)),repeat=unit):
                    posterior_mean = tuple(sum(w*(base[y]+column[y])/prediction.masses[y]
                        for y in labels)/unit for w,column in zip(weights,columns))
                    for rate in (F(0),F(1,4),F(1)):
                        spec = LearnerSpec(unit,rate,optimizer_id=SIMPLEX_GRADIENT,simplex_slots=slots)
                        state = initial
                        for y in labels:
                            state = observe_event(graph,state,spec,prediction,y,bit_limit=32768)
                        assert state.theta==theta and state.unit_count==unit
                        actual = commit_event(state,spec,bit_limit=32768)
                        assert tuple(actual.theta[s] for s in slots)==tuple((1-rate)*w+rate*p for w,p in zip(weights,posterior_mean))
                        assert (actual.theta[0],actual.theta[2])==(F(2),F(3))
                        assert actual.gradient_sum==(F(0),)*5 and actual.optimizer_steps==1
                        assert actual.unit_count==0 and actual.cursor==unit and sum(actual.theta[s] for s in slots)==1
                        checked += 1
    cfg, graph, online, _ = fixture(unit=2)
    state = initial_state(graph,cfg.semantics,cfg.initializer_pattern,0,spec=online.learner,bit_limit=32768)
    p = model.native_prediction(2,state.theta[1:],(0,1))
    for _ in range(2):
        state = observe_event(graph,state,online.learner,p,0,bit_limit=32768)
    state = commit_event(state,online.learner,bit_limit=32768)
    assert state.theta[1:]==(F(9,10),F(1,10))
    assert state.theta[1:]!=model.native_history_state(2,((0,1,0),)*2)
    # The fixed feature coordinate has a nonzero native derivative. Observe
    # retains it; the registered commit fixes theta and clears the full sum.
    state = initial_state(graph,cfg.semantics,cfg.initializer_pattern,0,spec=online.learner,bit_limit=32768)
    spec = replace(online.learner,update_unit=1)
    p = model.native_prediction(2,state.theta[1:],(0,0))
    observed = observe_event(graph,state,spec,p,0,bit_limit=32768)
    assert observed.gradient_sum[0]==F(-4,45)
    assert commit_event(observed,spec,bit_limit=32768).theta[0]==1
    bad_graph,bad_prediction = model.affine_evaluation(((0,0),(0,20)),(1,1),(F(9,10),F(1,10)))
    initial = ReferenceLearnerState((F(9,10),F(1,10)),(),(F(0),F(0)),0,0,0)
    bad_spec = LearnerSpec(1,F(1),optimizer_id=SIMPLEX_GRADIENT,simplex_slots=(0,1))
    observed = observe_event(bad_graph,initial,bad_spec,bad_prediction,0,bit_limit=32768)
    rejects(lambda:commit_event(observed,bad_spec,bit_limit=32768),ArithmeticUnresolved)
    assert observed.theta==initial.theta and observed.unit_count==1
    return {'exact_commits':checked,'batch_is_mean_of_single_observation_posteriors':True,
            'fixed_coordinate_gradient_retained':'-4/45','unequal_normalizer_negative_update_refused':True}


def registration_refusals():
    bad = ({}, {'simplex_slots':()}, {'simplex_slots':(1,1)}, {'simplex_slots':(2,1)},
           {'simplex_slots':(-1,1)}, {'simplex_slots':(True,1)}, {'learning_rate':F(2)},
           {'commit_grid_bits':16}, {'optimizer_id':'unregistered-U'})
    count = 0
    for change in bad:
        args = dict(update_unit=1,learning_rate=F(1),optimizer_id=SIMPLEX_GRADIENT,simplex_slots=(1,2))
        if not change:
            args.pop('simplex_slots')
        else:
            args.update(change)
        rejects(lambda: LearnerSpec(**args)); count += 1
    rejects(lambda:LearnerSpec(1,F(1),simplex_slots=(1,2))); count += 1
    cfg,graph,online,_ = fixture()
    rejects(lambda:initial_state(graph,cfg.semantics,(F(1),F(2,5),F(2,5)),0,
        spec=online.learner,bit_limit=32768),ArithmeticUnresolved); count += 1
    rejects(lambda:initial_state(graph,cfg.semantics,cfg.initializer_pattern,0,spec=online.learner)); count += 1
    return count


def rounded_boundaries():
    from fp_reference.binary_arithmetic import Float64Arithmetic
    from fp_reference import float64_learner as finite
    from audit_float64_runtime import CPUState,cpu_commit,same_state
    cases = (((F(0),F(1)),(F(10),F(0)),(0,1)),
             ((F(1,3),)*3,(F(1),F(2),F(3)),(0,1,2)),
             ((F(2),F(1,4),F(3),F(3,4)),(F(7),F(-1),F(-2),F(1)),(1,3)))
    for theta,gradient,slots in cases:
        casts = Float64Arithmetic(32768)
        actual = finite.Float64LearnerState(tuple(casts.cast(v) for v in theta),(),
            tuple(casts.cast(v) for v in gradient),1,1,0)
        expected = CPUState(tuple(map(float,theta)),(),tuple(map(float,gradient)),1,1,0)
        spec = LearnerSpec(1,F(1,4),optimizer_id=SIMPLEX_GRADIENT,simplex_slots=slots)
        arith = Float64Arithmetic(32768)
        result = finite.commit_event(actual,spec,arith)
        same_state(result,cpu_commit(expected,spec))
        assert arith.operations==finite.commit_operations(actual,spec)==7+11*len(slots)
        if not theta[slots[0]]:
            assert result.theta[slots[0]].bits==0
    return {'binary64_raw_successors':len(cases),'declared_scalar_operations_exact':True,'validated_zero_canonicalization':True}


def exhaustive():
    cfg,graph,online,tape = fixture()
    bounds = GrammarLimits(1,1,0,0,3)
    spec = ReferenceSearchSpec('tiny',bounds,online.data.active.observation_ids[:1])
    base = Program((Sum('mass',()),),graph.slot_count,(0,0))
    expected = set(brute_grammar(cfg.semantics,bounds))
    rows = []
    class_ids = []
    for optimizer in (online.learner,LearnerSpec(1,F(1))):
        run = replace(online,learner=optimizer,profiles=(),searches=(spec,),float64=None)
        rt = ReferenceCompilerRuntime(cfg,base,online=run)
        assert deliver_context(rt,run.data.active.observation_ids[0],tuple(model.context(2,0,1).values())).status=='PREDICTED_REFERENCE'
        assert rt.observe(0).status=='OBSERVED_REFERENCE'
        result = finish(rt,rt.start_reference_search('tiny'))
        snap = validate_residency(rt); session = snap.searches[0]
        assert session.cursor.done and {r.program for r in session.rows}==expected
        assert len(session.rows)==len(expected)==20
        class_ids.append(session.decision_class_id)
        if optimizer.optimizer_id==SIMPLEX_GRADIENT:
            assert result.status=='UNRESOLVED' and session.unresolved==15 and result.programs_compared==5
            assert all((r.status=='COMPARED_REFERENCE')==(r.program.slot_count==3) for r in session.rows)
            assert not result.proof_id and not snap.reference_proofs
        else:
            assert result.status=='REFERENCE_CLASS_EXHAUSTED' and result.programs_compared==20
            assert rt.reference_class_proof(result.proof_id,decision_class_id=session.decision_class_id).program_count==20
        rows.append({'optimizer':optimizer.optimizer_id,'syntax_programs':20,'compared':result.programs_compared,
                     'unresolved_programs':session.unresolved,'decision':result.status})
    assert class_ids[0]!=class_ids[1]
    return rows


def proposer_refusals():
    cfg,graph,online,tape = fixture()
    base = Program((Sum('mass',()),),graph.slot_count,(0,0))
    rt = ReferenceCompilerRuntime(cfg,base,online=online)
    assert deliver_context(rt,online.data.active.observation_ids[0],tuple(model.context(2,0,1).values())).status=='PREDICTED_REFERENCE'
    assert rt.observe(0).status=='OBSERVED_REFERENCE'
    upper = empirical_upper(rt.snapshot().observations,cfg.semantics,bit_limit=32768)
    grammar = GrammarLimits(**{key:graph.counts()[key] for key in cfg.graph_limits})
    source = RelationSourceSpec(tuple((f'x0:{j}',f'x1:{j}') for j in range(2)),solver=SOLVER)
    args = dict(upper=upper,rules=cfg.semantics,grammar=grammar,pattern=cfg.initializer_pattern,registration=source,
        data=online.data,learner=online.learner,source_domain=cfg.source_domain,profile=online.profiles[0],bit_limit=32768)
    assert simplex_relation_proposal(**args).program==graph
    changes = ({'pattern':(F(1),F(1,3),F(2,3))}, {'source_domain':cfg.source_domain[:-1]},
        {'source_domain':cfg.source_domain[:-1]+cfg.source_domain[:1]}, {'profile':None},
        {'learner':replace(online.learner,learning_rate=F(0))}, {'learner':replace(online.learner,update_unit=2)},
        {'learner':replace(online.learner,simplex_slots=(0,1))}, {'grammar':replace(grammar,slots=2)},
        {'registration':replace(source,solver='empirical-binary-relation-joint-polynomial-v5')},
        {'registration':RelationSourceSpec(tuple((f'l{i}',f'r{i}') for i in range(80)),solver=SOLVER)})
    for change in changes:
        proposal = simplex_relation_proposal(**dict(args,**change))
        assert proposal.status=='UNRESOLVED' and proposal.program is None and proposal.reason
    # The old partial-context helper cannot execute the registered v7 solver.
    assert relation_proposal(upper,cfg.semantics,grammar,cfg.initializer_pattern,source,bit_limit=32768).program is None
    # A returned syntax object is not permission to bypass a registered policy.
    from fp_reference import CompilerPolicy
    owned = ReferenceCompilerRuntime(cfg,base,online=online,policy=CompilerPolicy(()))
    before = owned.snapshot()
    rejects(lambda:owned.construct_candidate(graph))
    assert owned.snapshot()==before
    return {'refused_contexts':len(changes),'old_partial_context_helper_refused':True,'policy_owns_constructor':True}


if __name__=='__main__':
    result = {'arithmetic':arithmetic(),'registration_refusals':registration_refusals(),
              'rounded_boundaries':rounded_boundaries(),'exhaustive_classes':exhaustive(),'proposer':proposer_refusals()}
    assert 'torch' not in sys.modules
    print(json.dumps(result,indent=2))
