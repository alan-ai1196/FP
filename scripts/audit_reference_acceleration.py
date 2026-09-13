"""Native empirical-upper closure and hierarchy from ordinary token labels."""
from dataclasses import asdict, replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import random
import sys
import tempfile
import traceback
import math
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]

from fp_reference import ReferenceCompilerRuntime, CompilerPolicy, CompilationStep, RelationSourceSpec
from fp_reference.data_usage import ObservationRecord, StochasticStreamLaw
from fp_reference.empirical_bound import EmpiricalCell, empirical_upper, verify_empirical_upper
from fp_reference.float64_bridge import Float64Contract
from fp_reference.installation import CpuInstallContract
from fp_reference.host_resources import HostResourceContract
from fp_reference.host_resources import HostExecutionUnresolved
from fp_reference.host_failure import HOST_ALLOCATION_FAILURE, HOST_RESOURCE_FAILURE
from fp_reference.native_search import GrammarLimits
from fp_reference.program import Program, SemanticRules, SourceSpec, Source, Sum, Term, State, Binding, DelayedStateSpec
from fp_reference.resources import ResourceExceeded
from fp_reference.semantics import ArithmeticUnresolved
import fp_reference.runtime as execution
from fp_reference.proof import BoundedReferenceProof
from fp_reference.profile import ProfileSpec
from fp_reference.search import ReferenceSearchSpec
from audit_reference_construction import contract, limits, zero_program, validate_residency, rejects
from audit_reference_events import online, forward_oracle
from audit_float64_runtime import replay
from audit_paired_cpu_persistence import registration
from audit_reference_search import brute_grammar
from windows_job_audit_support import run_in_job
from ingress_audit_support import deliver_context


def context(n, i, j):
    return tuple(F(k == i) for k in range(n))+tuple(F(k == j) for k in range(n))


def fixture_parameters(n=4, *, groups=None, edges=None, bound=F(3)):
    """The same declared task and streams, before any Runtime is constructed."""
    if groups is None:
        groups = [i % 2 for i in range(n)]
        random.Random(2026091266+n).shuffle(groups)  # external synthetic task parameter; never passed to Runtime
    groups = tuple(groups)
    edges = tuple((i, i+1) for i in range(n-1)) if edges is None else tuple(edges)
    training = tuple((context(n, i, j), (groups[i] ^ groups[j]) ^ int(repetition == 9))
                     for i, j in edges for repetition in range(10))
    training_count = len(training)
    unit = 10
    total = 2*training_count+2
    atoms = tuple(SourceSpec(f'p{position}:t{i}', 'mass', 0, F(1)) for position in range(2) for i in range(n))
    rules = SemanticRules(atoms, ('mass',), (('mass', 'mass', 'mass'),), 'mass', (F(1), F(1)))
    cfg = replace(contract(), semantics=rules, initializer_pattern=(F(1), F(8)), normalizer_cap=F(10),
        activation_cap=F(8), reference_integer_bits=32768, limits=limits(1 << 30, 10**13),
        source_domain=tuple(context(n, i, j) for i in range(n) for j in range(n)))
    # These broad caps also contain a direct lookup for every token pair.
    # No candidate/architecture list or latent partition defines the class.
    bounds = GrammarLimits(2*n+n*n+2, n*n+6, n*n+4, 4*n*n+2*n+12, 2)
    cfg = replace(cfg, graph_limits=asdict(bounds))
    spec = ReferenceSearchSpec('native', bounds, tuple(f'observation-{i}' for i in range(training_count)),
        relation_sources=RelationSourceSpec(tuple((f'p0:t{i}', f'p1:t{i}') for i in range(n))))
    run = online(cfg, total, unit=unit, rate=F(0), grid=16)
    run = replace(run, data=replace(run.data, stream_law=StochasticStreamLaw('external branch-invariant relation fixture assumption; deterministic audit tape alone proves no probability law')),
        float64=Float64Contract(F(1, 1 << 24), F(1, 1 << 24)), persistence=registration(bound=bound, horizon=training_count),
        cpu_install=CpuInstallContract(), searches=(spec,))
    # Subsequent pairs include previously unobserved diagonal/cross-token
    # contexts. Only context bytes and ordinary labels reach the Runtime.
    fresh = tuple((context(n, (block//n) % n, block % n),
                   (groups[(block//n) % n] ^ groups[block % n]) ^ int(repetition == 9))
                  for block in range(len(edges)) for repetition in range(10))
    return cfg, run, groups, training, fresh+training[:2]


def fixture(n=4, *, groups=None, edges=None, automatic=True, host=None, bound=F(3), transform=None):
    cfg, run, groups, training, fresh = fixture_parameters(n, groups=groups, edges=edges, bound=bound)
    if transform is not None:
        cfg, run = transform(cfg, run)
    policy = CompilerPolicy((CompilationStep(len(training), 'native', 1, 'ref', 'finite'),)) if automatic else None
    rt = ReferenceCompilerRuntime(cfg, zero_program(2), online=run, host=host, policy=policy)
    return rt, groups, training, fresh


def ingest(rt, tape, *, start=0):
    for index, (inputs, target) in enumerate(tape, start):
        predicted = deliver_context(rt, f'observation-{index}', inputs)
        assert predicted.status == 'PREDICTED_REFERENCE', predicted
        observed = rt.observe(target)
        assert observed.status == 'OBSERVED_REFERENCE', observed


def upper_audit():
    rules = contract().semantics
    rows_checked = comparisons = rejected = 0
    for counts in product(range(4), repeat=4):
        if not sum(counts[:2]) or not sum(counts[2:]):
            continue
        records = []
        for cell, label in product(range(2), repeat=2):
            values = (F(cell), F(1-cell))
            sources = tuple((spec.source_id, value) for spec, value in zip(rules.sources, values))
            for _ in range(counts[2*cell+label]):
                i = len(records)
                records.append(ObservationRecord(f'o{i}', 'train', 'train', i, values, sources, label))
        records = tuple(records)
        bound = empirical_upper(records, rules, bit_limit=4096)
        verify_empirical_upper(bound, records, rules, bit_limit=4096)
        for a, b in product(range(9), repeat=2):
            probabilities = (F(a, 8), 1-F(a, 8), F(b, 8), 1-F(b, 8))
            value = math.prod(p**n for p, n in zip(probabilities, counts))
            assert value <= bound.likelihood
            comparisons += 1
        for fake in (replace(bound, likelihood=bound.likelihood/2),
                     replace(bound, cells=bound.cells[:-1]),
                     replace(bound, observation_ids=bound.observation_ids[::-1]),
                     replace(bound, likelihood=float(bound.likelihood)),
                     replace(bound, cells=(replace(bound.cells[0], counts=tuple(float(v) for v in bound.cells[0].counts)),)+bound.cells[1:])):
            rejects(lambda: verify_empirical_upper(fake, records, rules, bit_limit=4096))
            rejected += 1
        altered = (replace(records[0], sources=tuple((key, int(value)) for key, value in records[0].sources)),)+records[1:]
        rejects(lambda: verify_empirical_upper(bound, altered, rules, bit_limit=4096))
        rejects(lambda: empirical_upper(altered, rules, bit_limit=4096))
        rejected += 2
        rows_checked += 1
    # Erasing a source distinction can manufacture a false upper: opposite
    # deterministic targets at two contexts admit likelihood one, while a
    # single merged context yields only 1/4. Neither producer nor verifier
    # is allowed to install that coarser information interface.
    opposite = tuple(replace(records[i], observation_id=f'opposite-{i}', cursor=i,
        inputs=(F(i), F(1-i)), sources=tuple((s.source_id, v) for s, v in zip(rules.sources, (F(i), F(1-i)))),
        target=i) for i in range(2))
    distinct = empirical_upper(opposite, rules, bit_limit=4096)
    assert distinct.likelihood == 1
    merged = replace(distinct, cells=(EmpiricalCell(opposite[0].sources, (1, 1)),), likelihood=F(1, 4))
    rejects(lambda: verify_empirical_upper(merged, opposite, rules, bit_limit=4096))
    return {'two_context_count_tables': rows_checked, 'exact_rational_prediction_comparisons': comparisons,
            'independent_proposition_and_numeric_type_refusals': rejected,
            'erasing_source_distinction_can_make_false_upper_and_is_rejected': True}


def selected(*, n=4, tape_transform=None, **kwargs):
    rt, groups, train, fresh = fixture(n, automatic=False, **kwargs)
    if tape_transform is not None:
        train = tuple(tape_transform(train))
    ingest(rt, train)
    started = rt.start_reference_search('native')
    result = rt.advance_reference_search(started.search_id, transitions=1)
    return rt, groups, train, fresh, result


def baseline_exhaustive():
    caps = GrammarLimits(2, 1, 0, 1, 1)
    def configure(cfg, run):
        return cfg, replace(run, searches=(replace(run.searches[0], grammar=caps),))
    rt, _, train, _, result = selected(n=2, transform=configure,
        tape_transform=lambda tape: ((values, i % 2) for i, (values, _) in enumerate(tape)))
    final = validate_residency(rt)
    assert result.status == 'REFERENCE_CLASS_BOUNDED' and result.programs_compared == 0
    proof = rt.reference_class_proof(result.proof_id, decision_class_id=result.decision_class_id)
    assert proof.winner_lineage_id == final.deployed_id and proof.evaluated_programs == 0
    assert not final.searches[0].cursor.done and final.searches[0].relation_proposal is None
    graphs = brute_grammar(rt.contract.semantics, caps)
    maximum = F(0)
    for graph in graphs:
        theta = rt.contract.initializer_pattern[:graph.slot_count]
        score = F(1)
        for values, target in train:
            sources = {spec.source_id: value for spec, value in zip(rt.contract.semantics.sources, values)}
            probabilities, _ = forward_oracle(graph, rt.contract.semantics, theta, sources)
            score *= probabilities[target]
        maximum = max(maximum, score)
    assert maximum == proof.best_likelihood == F(1, 2)**len(train)
    return {'independently_enumerated_native_programs': len(graphs),
            'baseline_attains_upper_with_zero_new_candidates': True, 'syntax_not_claimed_exhausted': True}


def connected_assignments():
    predictions = 0
    for hidden in product(range(2), repeat=4):
        rt, _, _, _, result = selected(groups=hidden)
        final = validate_residency(rt)
        assert result.status == 'REFERENCE_CLASS_BOUNDED'
        proposal = final.searches[0].relation_proposal
        assert len(proposal.components) == 1
        assert all(actual == (value ^ hidden[0]) for actual, value in zip(proposal.assignment, hidden))
        for i, j in product(range(4), repeat=2):
            sources = {s.source_id: value for s, value in zip(rt.contract.semantics.sources, context(4, i, j))}
            probabilities, _ = forward_oracle(proposal.program, rt.contract.semantics, (F(1), F(8)), sources)
            assert probabilities[hidden[i] ^ hidden[j]] == F(9, 10)
            predictions += 1
    return {'all_four_token_hidden_assignments': 16, 'independent_complete_domain_predictions': predictions,
            'global_flip_invariance_including_empty_group': True}


def profiles():
    results = {}
    for biased in (False, True):
        def configure(cfg, run):
            spec = run.searches[0]
            profile = ProfileSpec('owned-profile', spec.observation_ids[:1] if biased else spec.observation_ids,
                                  len(spec.observation_ids) if biased else 1)
            return (replace(cfg, normalizer_cap=F(12), activation_cap=F(12)),
                replace(run, profiles=(profile,), learner=replace(run.learner, learning_rate=F(1, 64)),
                        searches=(replace(spec, profile_id=profile.profile_id),)))
        rt, _, _, _, result = selected(transform=configure)
        final = validate_residency(rt)
        assert len(final.profiles) == 1
        profile = final.profiles[0]
        assert profile.status == 'PROFILED_REFERENCE' and profile.events_completed == 30
        if biased:
            assert profile.attached.theta != (F(1), F(8))
            assert result.status == 'UNRESOLVED' and not final.reference_proofs
        else:
            assert profile.attached.theta == (F(1), F(8)) and profile.attached.optimizer_steps == 3
            assert result.status == 'REFERENCE_CLASS_BOUNDED'
        phases, _, _ = replay(rt)
        results['biased' if biased else 'empirically_saturated'] = {
            'profile_events': 30, 'independent_binary64_phase_checks': phases, 'search_status': result.status}
    return results


def identification_limits():
    # Same observations, opposite relative component flips: both empirical
    # optima exist, but the unseen relation (0,2) changes.
    outcomes = []
    for hidden in ((0, 1, 0, 1), (0, 1, 1, 0)):
        rt, _, train, _, result = selected(groups=hidden, edges=((0, 1), (2, 3)))
        final = validate_residency(rt)
        assert result.status == 'REFERENCE_CLASS_BOUNDED'
        proposal = final.searches[0].relation_proposal
        assert len(proposal.components) == 2
        outcomes.append((train, proposal, result.best_likelihood, hidden[0] ^ hidden[2]))
    assert outcomes[0][:3] == outcomes[1][:3] and outcomes[0][3] != outcomes[1][3]
    rt, hidden, train, _, result = selected()
    final = validate_residency(rt)
    # A strictly smaller zero-PRODUCT program has the same optimal empirical
    # likelihood on the oriented training tree. This witness falsifies any
    # inference from train optimality to forced hierarchy.
    nodes = [Source(f'p0:t{i}') for i in range(3)]
    heads = []
    for label in range(2):
        heads.append(len(nodes))
        nodes.append(Sum('mass', tuple(Term(i, 1) for i in range(3) if hidden[i] ^ hidden[i+1] == label)))
    cheaper = Program(tuple(nodes), 2, tuple(heads))
    assert final.searches[0].spec.grammar.admits(cheaper)
    built = rt.construct_candidate(cheaper)
    assert built.status == 'BUILT_REFERENCE', built
    score = F(1)
    for values, target in train:
        sources = {spec.source_id: value for spec, value in zip(rt.contract.semantics.sources, values)}
        predictions, _ = forward_oracle(cheaper, rt.contract.semantics, (F(1), F(8)), sources)
        score *= predictions[target]
    assert score == result.best_likelihood and cheaper.counts()['PRODUCTs'] == 0
    # Existing XVII sharp SUM infimum is an unrestricted strong comparator,
    # independent of this particular train-tied (poorly generalizing) graph.
    entropy = -0.9*math.log(0.9)-0.1*math.log(0.1)
    sharp_sum = (math.log(2)+entropy)/2
    assert entropy < sharp_sum < math.log(2)
    return {'disconnected_indistinguishable_worlds_with_opposite_unseen_relation': 2,
            'same_empirical_optimum_does_not_identify_relative_component_flip': True,
            'cheaper_train_tied_zero_PRODUCT_actual_construction': cheaper.counts(),
            'empirical_optimality_does_not_force_hierarchy': True,
            'existing_full_uniform_task_Bayes_CE': entropy,
            'existing_sharp_unrestricted_SUM_infimum_CE': sharp_sum}


def unresolved_cases():
    cases = {}
    variants = {
        'unavailable_initializer_scale': {'transform': lambda cfg, run: (replace(cfg, initializer_pattern=(F(1), F(7))), run)},
        'insufficient_witness_grammar': {'transform': lambda cfg, run: (cfg, replace(run, searches=(replace(run.searches[0], grammar=GrammarLimits(3, 1, 0, 2, 2)),)))},
        'no_finite_boundary_scale': {'tape_transform': lambda tape: ((values, tape[10*(i//10)][1]) for i, (values, _) in enumerate(tape))},
        'tied_relation': {'tape_transform': lambda tape: ((values, i % 2 if i < 10 else target) for i, (values, target) in enumerate(tape))},
        'inconsistent_cycle': {'edges': ((0, 1), (1, 2), (2, 0)),
            'tape_transform': lambda tape: ((values, target ^ int(i >= 20)) for i, (values, target) in enumerate(tape))},
        'heterogeneous_empirical_noise': {'tape_transform': lambda tape: ((values, target ^ int(i in (8, 19))) for i, (values, target) in enumerate(tape))},
    }
    for name, kwargs in variants.items():
        rt, _, _, _, result = selected(**kwargs)
        final = validate_residency(rt)
        assert result.status == 'UNRESOLVED' and not final.reference_proofs and not final.searches[0].cursor.done, name
        assert final.alpha_spent == 0 and final.halted is None
        if name == 'heterogeneous_empirical_noise':
            assert result.programs_compared == 1 and final.searches[0].relation_proposal.program is not None
        cases[name] = {'proposal_reason': final.searches[0].relation_proposal.reason,
                       'actually_compared': result.programs_compared, 'search_reason': result.reason}
    rt, _, train, fresh = fixture(bound=F(2))
    ingest(rt, train+fresh)
    final = validate_residency(rt)
    assert final.run.status == 'SEALED_REFERENCE_STREAM' and not final.install_receipts
    assert final.reference_proofs and final.alpha_spent == F(1, 2)
    assert all(p.status == 'UNRESOLVED' for p in final.persistence_identities)
    cases['full_range_persistence_bound_too_small'] = 'historical empirical proof survives; alpha remains spent; no install'
    rt, _, train, fresh = fixture(groups=(0, 1, 0, 1))
    misleading = tuple((values, target ^ int(i < 10)) for i, (values, target) in enumerate(train))
    ingest(rt, misleading)
    prior = validate_residency(rt)
    assert prior.reference_proofs and prior.compiler_policy.state.stages[0].status == 'EVIDENCE'
    assert prior.searches[0].relation_proposal.assignment != (0, 1, 0, 1)
    ingest(rt, fresh, start=len(train))
    final = validate_residency(rt)
    assert final.run.status == 'SEALED_REFERENCE_STREAM' and not final.install_receipts
    assert final.alpha_spent == F(1, 2) and final.reference_proofs
    assert all(p.status == 'UNRESOLVED' for p in final.persistence_identities)
    cases['consistent_but_false_empirical_relations'] = 'train upper attained; fresh evidence ends unresolved without crossing or installation'
    return cases


def authority_adversaries():
    rt, _, _, fresh, result = selected()
    proof = rt.reference_class_proof(result.proof_id, decision_class_id=result.decision_class_id)
    for key, value in (('decision_class_id', 'wrong-class'), ('evaluated_programs', 2), ('best_likelihood', proof.best_likelihood/2)):
        rejects(lambda: rt.verify_reference_class_proof(replace(proof, **{key: value}), decision_class_id=result.decision_class_id))
    rejects(lambda: replace(proof, evaluated_programs=True))
    other, _, _, _, _ = selected()
    rejects(lambda: other.verify_reference_class_proof(proof, decision_class_id=result.decision_class_id))
    ingest(rt, fresh[:1], start=30)
    rejects(lambda: rt.verify_reference_class_proof(proof, decision_class_id=result.decision_class_id))
    faults = {}
    for fault in ('raw_upper', 'wrong_witness', 'changed_class', 'retention', 'proof_publication', 'arithmetic', 'host', 'memory'):
        rt, _, train, _ = fixture(automatic=False)
        ingest(rt, train)
        start = rt.start_reference_search('native')
        if fault == 'raw_upper':
            def fake(*args, **kwargs):
                return replace(empirical_upper(*args, **kwargs), likelihood=F(1))
            injection = patch.object(execution, 'empirical_upper', fake)
        elif fault in ('wrong_witness', 'changed_class'):
            actual = ReferenceCompilerRuntime._compare_native_program
            def fake(self, session, graph):
                updated, error = actual(self, session, graph)
                if fault == 'changed_class':
                    return replace(updated, spec=replace(updated.spec,
                        grammar=replace(updated.spec.grammar, nodes=updated.spec.grammar.nodes+1))), error
                return replace(updated, best_candidate_id=updated.base_lineage_id), error
            injection = patch.object(ReferenceCompilerRuntime, '_compare_native_program', fake)
        elif fault in ('retention', 'proof_publication'):
            actual = ReferenceCompilerRuntime._save_search
            def fake(self, session):
                if (session.empirical_upper is not None and session.status == 'RUNNING' and fault == 'retention'
                        or session.status == 'REFERENCE_CLASS_BOUNDED' and fault == 'proof_publication'):
                    raise ResourceExceeded('injected upper retention exhaustion')
                return actual(self, session)
            injection = patch.object(ReferenceCompilerRuntime, '_save_search', fake)
        else:
            exception = {'arithmetic': ArithmeticUnresolved, 'host': HostExecutionUnresolved, 'memory': MemoryError}[fault]
            injection = patch.object(execution, 'empirical_upper', side_effect=exception('injected bound failure'))
        with injection:
            action = lambda: rt.advance_reference_search(start.search_id, transitions=1)
            if fault in ('raw_upper', 'wrong_witness', 'changed_class'):
                rejects(action)
            elif fault in ('host', 'memory'):
                rejects(action, exception)
            else:
                assert action().status == 'UNRESOLVED'
        final = validate_residency(rt)
        assert not final.reference_proofs and not final.install_receipts and final.alpha_spent == 0
        if fault in ('host', 'memory'):
            assert final.halted == (HOST_RESOURCE_FAILURE if fault == 'host' else HOST_ALLOCATION_FAILURE)
            rejects(lambda: rt.advance_reference_search(start.search_id, transitions=1))
        else:
            assert final.searches[0].status in ('UNRESOLVED', 'EXECUTION_FAILED')
        if fault == 'proof_publication':
            assert any(key.endswith(':bounded-reference-proof') for key, _ in final.buffers)
            assert final.searches[0].proof_id is not None  # passive failed prefix, never an issuance
        faults[fault] = 'no false completion or install authority'
    return {'changed_class_value_count_cross_root_and_stale_proofs_rejected': True, 'injected_failures': faults}


def range_residency():
    cfg = contract(pattern=(F(1, 2),))
    run = online(cfg, 4, unit=2, rate=F(1, 4), grid=8)
    graph = Program((Source('x0_0'), Sum('mass', (Term(0, 0),)), Sum('mass', ())), 1, (1, 2))
    rt = ReferenceCompilerRuntime(cfg, zero_program(2), online=run)
    built = rt.construct_candidate(graph)
    prior = next(s for s in validate_residency(rt).candidates if s.candidate_id == built.candidate_id)
    original = rt._buffers[prior.object_ids[2]]
    ingest(rt, (((F(1), F(0)), 0),))
    mid = next(s for s in validate_residency(rt).candidates if s.candidate_id == built.candidate_id)
    assert mid.learner.unit_count == 1 and mid.learner.gradient_sum != prior.learner.gradient_sum
    assert mid.object_ids[2] == prior.object_ids[2] and rt._buffers[mid.object_ids[2]] is original
    ingest(rt, (((F(1), F(0)), 0),), start=1)
    final = validate_residency(rt)
    changed = next(s for s in final.candidates if s.candidate_id == built.candidate_id)
    assert changed.theta != prior.theta and changed.object_ids[2] != prior.object_ids[2]
    assert prior.object_ids[2] not in dict(final.buffers)
    base = next(s for s in final.candidates if s.candidate_id == final.deployed_id)
    assert base.learner.optimizer_steps == 1 and base.object_ids[2].endswith(':range')
    # Delayed values and predictions change while the same full invariant
    # remains valid. Reusing evidence does not identify those learner states.
    rules = replace(cfg.semantics, states=(DelayedStateSpec('lag', 'mass', 1, F(1)),))
    recurrent = Program((Source('x0_0'), State('lag'), Sum('mass', ())), 0, (1, 2), (Binding('lag', 0),))
    recurrent_cfg = replace(cfg, semantics=rules)
    rt = ReferenceCompilerRuntime(recurrent_cfg, recurrent, online=online(recurrent_cfg, 4, unit=2, rate=F(1, 4), grid=8))
    prior = validate_residency(rt).candidates[0]
    original = rt._buffers[prior.object_ids[2]]
    changed_histories = 0
    for i, values in enumerate(((F(1), F(0)), (F(0), F(1)), (F(0), F(1)), (F(1), F(0)))):
        ingest(rt, ((values, 0),), start=i)
        current = validate_residency(rt).candidates[0]
        changed_histories += int(current.delayed != prior.delayed)
        assert current.object_ids[2] == prior.object_ids[2] and rt._buffers[current.object_ids[2]] is original
        prior = current
    assert changed_histories == 3 and prior.learner.optimizer_steps == 2
    # Failed replacement after real allocation keeps the old published
    # proof/learner plus the paid partial objects; it cannot publish a stale
    # range proof with changed theta or retry the target as unread.
    rt = ReferenceCompilerRuntime(cfg, zero_program(2), online=run)
    built = rt.construct_candidate(graph)
    ingest(rt, (((F(1), F(0)), 0),))
    prior = next(s for s in validate_residency(rt).candidates if s.candidate_id == built.candidate_id)
    assert deliver_context(rt, 'observation-1', (F(1), F(0))).status == 'PREDICTED_REFERENCE'
    actual = ReferenceCompilerRuntime._allocate
    def fail(self, owner, objects):
        actual(self, owner, objects)
        if any(obj.spec.object_id.endswith(':event:1:range') for obj in objects):
            raise ResourceExceeded('injected post-allocation changed-range refusal')
    with patch.object(ReferenceCompilerRuntime, '_allocate', fail):
        assert rt.observe(0).status == 'UNRESOLVED'
    final = validate_residency(rt)
    same = next(s for s in final.candidates if s.candidate_id == built.candidate_id)
    assert same == prior and prior.object_ids[2] in dict(final.buffers)
    assert final.halted is not None and final.cursor == 1 and len(final.observations) == 2
    assert any(key.endswith(':event:1:range') for key, _ in final.buffers)
    rejects(lambda: rt.observe(0))
    return {'same_theta_reuses_actual_range_buffer_without_new_lease': True,
            'changed_theta_recomputes_and_replaces_before_old_release': True,
            'changed_delayed_histories_under_same_whole_invariant': changed_histories,
            'failed_replacement_retains_old_root_and_new_paid_prefix': True}


def hierarchy(n=4, *, host=None):
    rt, hidden, train, fresh = fixture(n, host=host)
    ingest(rt, train)
    initial = validate_residency(rt)
    stage = initial.compiler_policy.state.stages[0]
    assert stage.status == 'EVIDENCE', (stage, [(x.status, x.reason) for x in initial.persistence_identities])
    session, proof = initial.searches[0], initial.reference_proofs[0]
    assert type(proof) is BoundedReferenceProof and proof.evaluated_programs == 1
    assert session.status == 'REFERENCE_CLASS_BOUNDED' and not session.cursor.done and session.cursor.emitted == 0
    assert len(session.rows) == 1 and len(session.relation_proposal.components) == 1
    candidate = next(value for value in initial.candidates if value.candidate_id == proof.winner_lineage_id)
    graph = dict(initial.programs)[candidate.program_id]
    checked = 0
    for i, j in product(range(n), repeat=2):
        values = context(n, i, j)
        source = {spec.source_id: value for spec, value in zip(rt.contract.semantics.sources, values)}
        probabilities, _ = forward_oracle(graph, rt.contract.semantics, candidate.theta, source)
        assert probabilities[hidden[i] ^ hidden[j]] == F(9, 10)
        checked += 1
    ingest(rt, fresh, start=len(train))
    final = validate_residency(rt)
    assert final.halted is None and final.run.status == 'SEALED_REFERENCE_STREAM'
    assert final.install_receipts and final.install_receipts[0].attempt.cursor == len(train)+20
    assert final.cursor == 2*len(train)+2 and final.alpha_spent == F(1, 2)
    assert final.run.closure.decisions[0].decision_status == 'HISTORICAL_REFERENCE_CLASS_BOUNDED'
    phases, _, _ = replay(rt)
    # Source-only strings alone already make complete construction infeasible
    # for the registered finite work cap. This is a counting lower bound,
    # not a deliberately under-run search baseline.
    syntax_lower = (2*n)**session.spec.grammar.nodes
    assert syntax_lower > rt.contract.limits.role_cumulative['compiler']['work']
    result = {'tokens': n, 'ordinary_training_events': len(train), 'optimizer_update_unit': rt.online_contract.learner.update_unit,
            'complete_domain_predictions_checked': checked,
            'native_graph': graph.counts(), 'full_native_class_caps': asdict(session.spec.grammar),
            'source_only_class_cardinality_at_least_power_of_two': syntax_lower.bit_length()-1,
            'actually_evaluated_native_witnesses': 1, 'unexecuted_syntax_cursor_not_declared_exhausted': True,
            'installed_at_cursor': final.install_receipts[0].attempt.cursor,
            'continued_after_install_and_sealed_at': final.cursor, 'independent_binary64_phase_checks': phases,
            'peak_reference_payload_bytes': final.resources['peak']['reference_payload_bytes'],
            'not_claimed': 'population identification, forced unique hierarchy, or actual target AMP'}
    if host is not None:
        observed = final.host_resources
        result['host'] = {key: getattr(observed, key) for key in ('process_id', 'creation_100ns',
            'lifetime_process_commit_peak', 'job_commit_peak', 'process_user_100ns', 'process_kernel_100ns')}
    return result


def bounded(n=32):
    cap = 1 << 30
    with tempfile.TemporaryDirectory(prefix='fp-native-bound-audit-', dir=ROOT) as temporary:
        assert Path(temporary).resolve().parent == ROOT
        output = Path(temporary)/'result.json'
        job = run_in_job(__file__, ('--worker', '--size', str(n), '--output', output), commit_limit=cap, timeout_ms=1800000)
        if job.exit_code != 0 or job.timed_out:
            diagnostic = output.read_text(encoding='utf-8')[:12000] if output.exists() else 'no worker report'
            raise AssertionError((job, diagnostic))
        with output.open('rb') as source:
            payload = source.read(8193)
        assert len(payload) <= 8192
        result = json.loads(payload)
        host = result['host']
        assert (host['process_id'], host['creation_100ns']) == (job.process_id, job.process_creation_100ns)
        assert host['lifetime_process_commit_peak'] <= job.peak_process_commit <= cap
        assert host['job_commit_peak'] <= job.peak_job_commit <= cap
        assert host['process_user_100ns'] <= job.user_100ns and host['process_kernel_100ns'] <= job.kernel_100ns
        return dict(result, completed_job=asdict(job))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--size', type=int, default=32)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--output')
    sections = ('upper_audit', 'baseline_exhaustive', 'connected_assignments', 'profiles',
                'identification_limits', 'unresolved_cases', 'authority_adversaries', 'range_residency', 'bounded')
    parser.add_argument('--section', choices=sections+('local',))
    args = parser.parse_args()
    if args.worker:
        cap = 1 << 30
        try:
            result = hierarchy(args.size, host=HostResourceContract(cap, {'deployment': cap, 'compiler': cap}))
        except Exception:
            Path(args.output).write_text(traceback.format_exc(), encoding='utf-8')
            raise
        Path(args.output).write_text(json.dumps(result), encoding='utf-8')
    else:
        cases = {name: bounded(args.size) if name == 'bounded' else globals()[name]() for name in sections
                 if args.section in (None, name) or args.section == 'local' and name != 'bounded'}
        result = {'status': 'PASS', 'machine': 'packed-reference-payload-v9',
            'scope': 'universal frozen-context empirical upper, owned native witness and bounded CPU hierarchy protocol',
            'cases': cases, 'not_claimed': ['all native members constructed', 'unique or resource-forced hierarchy',
                'population identification from empirical majorities', 'deterministic tape proves stochastic freshness',
                'complete Runtime release or actual target AMP']}
        if args.write:
            assert args.section is None and args.size == 32
            (ROOT/'evidence/minimal/FP_REFERENCE_ACCELERATION_AUDIT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
