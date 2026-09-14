"""Independent exact and raw-CUDA audits of the likelihood-coordinate lowering.

The expected likelihoods come from an independent positive-degree proof and
native mass derivatives, cross-checked against simplex vertices on small graphs.
They do not come from the production affine analyzer or its coordinate decoder.
This file is a passive auditor; it cannot supply a Runtime model or successor.
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
from fp_reference.core import ContractError, stable_hash
from fp_reference.encoding import pack
from fp_reference import learner as native
from fp_reference.likelihood_encoding import (ENCODING_ID, EncodedLikelihoodState,
    LikelihoodEncodingContract, exponents, prepare_model, preparation_work,
    preparation_workspace, require_learner)
from fp_reference.program import (Binding, DelayedStateSpec, Product, Program,
    SemanticRules, Source, SourceSpec, State, Sum, Term)
from fp_reference.semantics import ArithmeticUnresolved, evaluate
from audit_simplex_learner import fixture
from audit_reference_construction import rejects, validate_residency
from audit_cuda_learner import model_initial, model_predict, model_observe, q, SINGLE
from audit_cuda_runtime import no_device_handles, raw_model, raw_model_prediction
from fp_reference.cuda_range import forward_operations
from fp_reference.cuda_prefix import output_cells
from likelihood_information import rank

BITS = 32768


def power(value, radix):
    """Audit-only exact comparison to powers; no logs or production decoder."""
    assert value > 0 and radix > 1
    at, exponent = F(1), 0
    if value >= 1:
        while at < value:
            at *= radix
            exponent += 1
    else:
        while at > value:
            at /= radix
            exponent -= 1
    assert at == value, (value, radix)
    return exponent


def vertex_bank(graph, rules, theta, spec, domain):
    rows = []
    for point in domain:
        experts = []
        for world in range(len(spec.simplex_slots)):
            vertex = list(theta)
            for index, slot in enumerate(spec.simplex_slots):
                vertex[slot] = F(index == world)
            experts.append(evaluate(graph, rules, tuple(vertex),
                dict(zip((s.source_id for s in rules.sources), point)), bit_limit=BITS))
        assert len({e.normalizer for e in experts}) == 1
        rows.extend(tuple(e.probabilities[y] for e in experts) for y in range(len(graph.heads)))
    return tuple(rows)


def reverse_bank(graph, rules, theta, spec, domain):
    """Independent positive-degree proof and scalar native mass derivatives.

    A positive polynomial vanishes at a strictly positive selected Gamma iff
    it is identically zero on that selected slice. Thus exact initializer
    values certify zero support; integer degrees certify affine heads. Their
    native mass Jacobians then determine all vertices without K evaluations.
    This uses neither the producer's affine maps nor its likelihood factors.
    """
    selected = set(spec.simplex_slots)
    assert all(theta[i] > 0 for i in selected) and sum(theta[i] for i in selected) == 1
    assert not rules.states
    rows = []
    for point in domain:
        prediction = evaluate(graph, rules, theta,
            dict(zip((s.source_id for s in rules.sources), point)), bit_limit=BITS)
        degrees = []
        for index, node in enumerate(graph.nodes):
            if prediction.values[index] == 0:
                degree = -1
            elif type(node) is Source:
                degree = 0
            elif type(node) is Product:
                degree = min(2, degrees[node.left]+degrees[node.right])
            else:
                assert type(node) is Sum
                degree = max(min(2, degrees[t.parent]+int(t.slot in selected))
                    for t in node.terms if theta[t.slot] and prediction.values[t.parent])
            degrees.append(degree)
        assert all(degrees[head] <= 1 for head in graph.heads), 'native positive head is not affine on the selected slice'
        masses = []
        for y, head in enumerate(graph.heads):
            adjoint, gradient = [F(0)]*len(graph.nodes), [F(0)]*graph.slot_count
            adjoint[head] = F(1)
            for index in reversed(range(len(graph.nodes))):
                node, seed = graph.nodes[index], adjoint[index]
                if type(node) is Product:
                    adjoint[node.left] += seed*prediction.values[node.right]
                    adjoint[node.right] += seed*prediction.values[node.left]
                elif type(node) is Sum:
                    for term in node.terms:
                        gradient[term.slot] += seed*prediction.values[term.parent]
                        adjoint[term.parent] += seed*theta[term.slot]
            coefficients = tuple(gradient[i] for i in spec.simplex_slots)
            constant = prediction.masses[y]-sum(theta[i]*gradient[i] for i in spec.simplex_slots)
            assert constant >= rules.base[y] and min(coefficients) >= 0
            masses.append(tuple(constant+a for a in coefficients))
        normalizers = tuple(map(sum, zip(*masses)))
        assert len(set(normalizers)) == 1 and min(normalizers) > 0
        rows.extend(tuple(mass/z for mass, z in zip(row, normalizers)) for row in masses)
    return tuple(rows)


def verify_model(model, graph, rules, theta, spec, domain):
    assert (model.program_id, model.semantics, model.initial_theta, model.learner,
            model.source_domain) == (graph.program_id, rules, theta, spec, tuple(dict.fromkeys(domain)))
    bank = reverse_bank(graph, rules, theta, spec, model.source_domain)
    prior = tuple(theta[i] for i in spec.simplex_slots)
    prior_powers = tuple(power(w/prior[0], model.contract.radix) for w in prior)
    increments = tuple(tuple(power(w/row[0], model.contract.radix) for w in row) for row in bank)
    differences = tuple(tuple(row[k]-increments[0][k] for row in increments) for k in range(len(prior)))
    assert model.prior_exponents == prior_powers and model.reference_increment == increments[0]
    assert model.rank == rank(differences)
    representatives = tuple(next(k for k, row in enumerate(model.reconstruction)
        if row == tuple(F(i == j) for i in range(model.rank))) for j in range(model.rank))
    for a, row in enumerate(increments):
        assert model.event_increments[a] == tuple(differences[k][a] for k in representatives)
        assert tuple(sum(c*d for c, d in zip(coefficients, model.event_increments[a]))
            for coefficients in model.reconstruction) == tuple(row[k]-increments[0][k] for k in range(len(prior)))
    assert model.preparation_operations <= preparation_work(graph, rules, spec, domain, BITS)
    return bank, representatives


def expected_metadata(model, bank, representatives, joint, steps, pending):
    powers = tuple(power(w/joint[0], model.contract.radix) for w in joint)
    coordinates = tuple(powers[k]-model.prior_exponents[k]-steps*power(bank[0][k]/bank[0][0], model.contract.radix)
                        for k in representatives)
    return ENCODING_ID, stable_hash(model), coordinates, pending


def derive(cfg, graph, online, **changes):
    args = dict(program=graph, rules=cfg.semantics, theta=cfg.initializer_pattern,
        spec=online.learner, source_domain=cfg.source_domain, contract=LikelihoodEncodingContract(),
        bit_limit=BITS, work_limit=preparation_work(graph, cfg.semantics, online.learner, cfg.source_domain, BITS))
    args.update(changes)
    return prepare_model(**args)


def exact_audit():
    comparisons, rows = 0, []
    for n, depth in ((2, 3), (3, 2), (4, 1)):
        cfg, graph, online, _ = fixture(n)
        model = derive(cfg, graph, online)
        bank, representatives = verify_model(model, graph, cfg.semantics, cfg.initializer_pattern,
                                             online.learner, cfg.source_domain)
        assert bank == vertex_bank(graph, cfg.semantics, cfg.initializer_pattern, online.learner, cfg.source_domain)
        assert model.rank == n*(n-1)//2
        initial = native.initial_state(graph, cfg.semantics, cfg.initializer_pattern, 0,
                                       spec=online.learner, bit_limit=BITS)
        frontier = ((initial, EncodedLikelihoodState(model, (0,)*model.rank, None),
                     tuple(initial.theta[i] for i in online.learner.simplex_slots)),)
        local = 0
        for _ in range(depth):
            following = []
            for before, encoded, joint in frontier:
                for event, ell in enumerate(bank):
                    query, target = divmod(event, len(graph.heads))
                    point = dict(zip(model.source_ids, model.source_domain[query]))
                    prediction = evaluate(graph, cfg.semantics, before.theta, point, bit_limit=BITS)
                    observed = native.observe_event(graph, before, online.learner, prediction, target, bit_limit=BITS)
                    pending = encoded.observe(query, target)
                    assert pending.raw() == expected_metadata(model, bank, representatives, joint, before.optimizer_steps, event)
                    pending.validate_phase(graph.slot_count, observed.unit_count, observed.optimizer_steps, observed.delayed)
                    after = native.commit_event(observed, online.learner, bit_limit=BITS)
                    encoded_after = pending.commit()
                    joint_after = tuple(w*p for w, p in zip(joint, ell))
                    weights = tuple(w/sum(joint_after) for w in joint_after)
                    assert after.theta == (F(1),)+weights and after.gradient_sum == (F(0),)*graph.slot_count
                    assert encoded_after.raw() == expected_metadata(model, bank, representatives, joint_after, after.optimizer_steps, None)
                    decoded = tuple(model.contract.radix**v for v in exponents(encoded_after, after.optimizer_steps, bit_limit=BITS))
                    assert tuple(w/sum(decoded) for w in decoded) == weights
                    following.append((after, encoded_after, joint_after))
                    local += 1
            frontier = tuple(following)
        comparisons += local
        rows.append({'n': n, 'rank': model.rank, 'exact_transitions': local,
            'derivation_work': model.preparation_operations,
            'prepaid_work': preparation_work(graph, cfg.semantics, online.learner, cfg.source_domain, BITS),
            'scratch_bytes': preparation_workspace(graph, cfg.semantics, online.learner, cfg.source_domain, BITS)})

    # A nonlinear native interior can have a zero fixed multiplier at the
    # selected slice. Its nonzero ambient fixed-slot gradient must survive.
    rules = SemanticRules((SourceSpec('one', 'mass', 0, F(1)),), ('mass',),
        (('mass', 'mass', 'mass'),), 'mass', (F(1), F(1)))
    graph = Program((Source('one'), Sum('mass', (Term(0, 1),)), Product('mass', 1, 1),
                     Sum('mass', (Term(2, 0),)), Sum('mass', ())), 3, (3, 4))
    theta = (F(0), F(1, 2), F(1, 2))
    spec = native.LearnerSpec(1, F(1), optimizer_id=native.SIMPLEX_GRADIENT, simplex_slots=(1, 2))
    zero_model = prepare_model(graph, rules, theta, spec, ((F(1),),), LikelihoodEncodingContract(),
                               bit_limit=BITS, work_limit=10**8)
    verify_model(zero_model, graph, rules, theta, spec, ((F(1),),))
    prediction = evaluate(graph, rules, theta, {'one': F(1)}, bit_limit=BITS)
    gradient = native.ce_gradient(graph, theta, prediction, 0, bit_limit=BITS)
    assert zero_model.rank == 0 and prediction.values == (F(1), F(1, 2), F(1, 4), F(0), F(0))
    assert gradient == (F(-1, 8), F(0), F(0))
    rejects(lambda: prepare_model(graph, rules, (F(1),)+theta[1:], spec, ((F(1),),),
        LikelihoodEncodingContract(), bit_limit=BITS, work_limit=10**8), ArithmeticUnresolved)

    # Noncontiguous slots, nonuniform commensurate Gamma, and a rational radix.
    graph = Program((Source('one'), Sum('mass', (Term(0, 1),)), Sum('mass', (Term(0, 3),))), 4, (1, 2))
    spec = replace(spec, simplex_slots=(1, 3))
    theta = (F(7), F(1, 3), F(11), F(2, 3))
    affine = prepare_model(graph, rules, theta, spec, ((F(1),),), LikelihoodEncodingContract(F(2)),
                           bit_limit=BITS, work_limit=10**8)
    verify_model(affine, graph, rules, theta, spec, ((F(1),),))
    rational_rules = replace(rules, base=(F(2), F(2)))
    rational_theta = (F(7), F(2, 5), F(11), F(3, 5))
    affine_rational = prepare_model(graph, rational_rules, rational_theta, spec, ((F(1),),),
                                   LikelihoodEncodingContract(F(3, 2)), bit_limit=BITS, work_limit=10**8)
    verify_model(affine_rational, graph, rational_rules, rational_theta, spec, ((F(1),),))
    additional_updates = 0
    for model, actual_rules, initial_theta in ((affine, rules, theta), (affine_rational, rational_rules, rational_theta)):
        bank, representatives = verify_model(model, graph, actual_rules, initial_theta, spec, ((F(1),),))
        assert bank == vertex_bank(graph, actual_rules, initial_theta, spec, ((F(1),),))
        state = native.initial_state(graph, actual_rules, initial_theta, 6, spec=spec, bit_limit=BITS)
        encoded = EncodedLikelihoodState(model, (0,)*model.rank, None)
        joint = tuple(initial_theta[i] for i in spec.simplex_slots)
        for target in (0, 0, 1, 1):
            pred = evaluate(graph, actual_rules, state.theta, {'one': F(1)}, bit_limit=BITS)
            state = native.commit_event(native.observe_event(graph, state, spec, pred, target, bit_limit=BITS), spec, bit_limit=BITS)
            encoded = encoded.observe(0, target).commit()
            joint = tuple(w*p for w, p in zip(joint, bank[target]))
            assert tuple(state.theta[i] for i in spec.simplex_slots) == tuple(w/sum(joint) for w in joint)
            assert (state.theta[0], state.theta[2]) == (F(7), F(11))
            assert state.cursor == 6+state.optimizer_steps
            assert encoded.raw() == expected_metadata(model, bank, representatives, joint, state.optimizer_steps, None)
            additional_updates += 1
    unequal = Program(graph.nodes, graph.slot_count, (0, 1))
    rejects(lambda: prepare_model(unequal, rules, theta, spec, ((F(1),),), LikelihoodEncodingContract(F(2)),
        bit_limit=BITS, work_limit=10**8), ArithmeticUnresolved)
    delayed_rules = replace(rules, states=(DelayedStateSpec('memory', 'mass', 1, F(1)),))
    delayed_graph = Program(graph.nodes+(State('memory'),), graph.slot_count, graph.heads, (Binding('memory', 0),))
    rejects(lambda: prepare_model(delayed_graph, delayed_rules, theta, spec, ((F(1),),), LikelihoodEncodingContract(F(2)),
        bit_limit=BITS, work_limit=10**8), ArithmeticUnresolved)

    cfg, graph, online, _ = fixture(2)
    negatives = 3
    for changed in (replace(online.learner, learning_rate=F(1, 2)),
                    replace(online.learner, update_unit=2)):
        rejects(lambda: require_learner(changed), ArithmeticUnresolved)
        negatives += 1
    rejects(lambda: replace(online.learner, commit_grid_bits=16), ContractError)
    negatives += 1
    for changes in ({'source_domain': None}, {'theta': (F(1), F(0), F(1))},
                    {'theta': (F(1), F(1, 3), F(2, 3))}, {'contract': LikelihoodEncodingContract(F(2))},
                    {'work_limit': 1}, {'bit_limit': 2}):
        rejects(lambda: derive(cfg, graph, online, **changes), ArithmeticUnresolved)
        negatives += 1
    model = derive(cfg, graph, online, contract=LikelihoodEncodingContract(counter_bits=6))
    state = EncodedLikelihoodState(model, (0,)*model.rank, None)
    query = model.query_index(dict(zip(model.source_ids, cfg.source_domain[1])))
    for _ in range(31):
        state = state.observe(query, 0).commit()
    rejects(lambda: state.observe(query, 0).commit(), ArithmeticUnresolved)
    rejects(lambda: exponents(state, 32, bit_limit=BITS), ArithmeticUnresolved)
    rejects(lambda: model.query_index({}), ContractError)
    negatives += 3
    from fp_reference.cuda_range import stored_probability
    raw = ((), (), (), (0x3f800000, 0x40000000), (0x40400000,), (), ())
    assert stored_probability(raw, 0, bit_limit=BITS) == stored_probability(raw+(3,), 0, bit_limit=BITS) == F(1, 3)
    for malformed in (raw+(-1,), raw+(True,), raw+(F(0),), raw+(0, 0)):
        rejects(lambda: stored_probability(malformed, 0, bit_limit=BITS), ContractError)
        negatives += 1
    assert 'torch' not in sys.modules
    return {'status': 'PASS', 'relation_banks': rows, 'exact_transitions': comparisons,
        'zero_annulled_nonlinear_gradient': str(gradient[0]), 'additional_affine_banks': 3,
        'additional_noncontiguous_clocked_updates': additional_updates,
        'negative_cases': negatives, 'precision': 'exact Fraction; no torch or CUDA'}


def rounded_commit(before, spec, joint, radix):
    """Round actual joint likelihoods on the registered positive GPU schedule.

    The mathematical inputs use the complete replayed word and native vertex
    likelihoods. They do not read the implementation's coordinate transition.
    """
    trace = []
    def operation(name, values):
        result = tuple(q(v) for v in values)
        trace.append((name, 32, tuple(SINGLE.encode_exact(v) for v in result)))
        return result
    beta = operation('host-RNE32-ingress', (1/radix,))[0]
    one = operation('host-RNE32-ingress', (F(1),))[0]
    zero = operation('host-RNE32-ingress', (F(0),))[0]
    differences = tuple(power(max(joint)/w, radix) for w in joint)
    bits = max(differences).bit_length()
    powers = [beta]
    for _ in range(1, bits):
        powers.append(operation('mul', (powers[-1]**2,))[0])
    weights = []
    for exponent in differences:
        value = one
        for bit in range(bits):
            if exponent & (1 << bit):
                value = operation('mul', (value*powers[bit],))[0]
        weights.append(value)
    total = zero
    for value in weights:
        total = operation('add', (total+value,))[0]
    normalized = operation('div', tuple(w/total for w in weights))
    theta = list(before.theta)
    for slot, value in zip(spec.simplex_slots, normalized):
        theta[slot] = value
    after = replace(before, theta=tuple(theta), gradient=(F(0),)*len(theta), unit=0, steps=before.steps+1)
    cells = 3+max(bits-1, 0)+sum(d.bit_count() for d in differences)+3*len(weights)+2*len(theta)
    return after, tuple(trace), cells


def audit_snapshot(runtime, *, expected_failure=None, pre_attack_models=()):
    snapshot = validate_residency(runtime)
    no_device_handles(snapshot)
    graphs, observations, buffers = dict(snapshot.programs), {r.observation_id: r for r in snapshot.observations}, dict(snapshot.buffers)
    if snapshot.pending is not None:
        observations[snapshot.pending.record.observation_id] = snapshot.pending.record
    expected, physical, banks, records = {}, {}, {}, {}
    checked = commits = failed = 0
    saved_models = dict(pre_attack_models)
    for observed_record in snapshot.cuda.phases:
        record = observed_record
        if record.encoding_model is not None and record.program_id in saved_models:
            assert expected_failure is not None
            # Audit the immutable original frame with a saved pre-attack
            # descriptor; never repair the private failed Runtime state.
            record = replace(record, encoding_model=saved_models[record.program_id])
        records[record.object_id] = record
        graph, kind = graphs[record.program_id], record.phase.split(':')[1]
        frame = buffers[record.object_id]
        size = int.from_bytes(frame[:8], 'big')
        assert size > 0 and frame[8:8+size] == pack(record)
        assert len(frame) == snapshot.cuda.contract.phase_evidence_bytes and not any(frame[8+size:])
        if record.status != 'CHECKED_CUDA_PREFIX_PHASE':
            assert expected_failure is not None and observed_record == snapshot.cuda.phases[-1]
            assert expected_failure in record.reason, record.reason
            assert record.raw_prediction is None and record.raw_operations == () and record.output_cells == 0
            assert not snapshot.install_receipts and snapshot.run.status != 'SEALED_CUDA_STREAM'
            failed += 1
            continue
        before = None if record.input_phase is None else expected[record.input_phase]
        history = None if record.input_phase is None else physical[record.input_phase]
        if kind == 'initialize':
            model = record.encoding_model
            bank, representatives = verify_model(model, graph, runtime.contract.semantics,
                record.reference.theta, runtime.online_contract.learner, runtime.contract.source_domain)
            banks[stable_hash(model)] = model, bank, representatives
            joint = tuple(record.reference.theta[i] for i in model.simplex_slots)
            history = model, joint, None
            result = model_initial(graph, runtime.contract.semantics, record.reference.theta, record.reference.cursor)
        else:
            assert record.encoding_model is None
            model, joint, pending = history
            _, bank, representatives = banks[stable_hash(model)]
            if kind == 'attach':
                result = replace(before, cursor=record.reference.cursor)
            elif kind == 'predict':
                row = observations[record.observation_id]
                source = dict(row.sources)
                result = model_predict(graph, runtime.contract.semantics, before, source)
                assert record.raw_prediction[:7] == raw_model_prediction(result)
                query = model.source_domain.index(tuple(source[key] for key in model.source_ids))
                assert record.raw_prediction[7] == query
                assert record.raw_state[:6] == raw_model(before)
            elif kind == 'observe':
                row = observations[record.observation_id]
                prediction = records[record.prediction_phase]
                assert prediction.input_phase == record.input_phase and prediction.observation_id == record.observation_id
                result = model_observe(graph, before, expected[record.prediction_phase], row.target)
                query = model.source_domain.index(tuple(dict(row.sources)[key] for key in model.source_ids))
                history = model, joint, query*len(graph.heads)+row.target
            else:
                assert kind == 'commit' and pending is not None
                joint = tuple(w*p for w, p in zip(joint, bank[pending]))
                result, trace, cells = rounded_commit(before, model.learner, joint, model.contract.radix)
                assert record.raw_operations == trace
                assert record.output_cells == cells
                history = model, joint, None
                commits += 1
        if kind != 'predict':
            assert record.raw_state[:6] == raw_model(result)
        state = before if kind == 'predict' else result
        model, joint, pending = history
        _, bank, representatives = banks[stable_hash(model)]
        assert record.raw_state[6] == expected_metadata(model, bank, representatives, joint, state.steps, pending)
        assert record.forward_operations == (forward_operations(graph, runtime.contract.semantics) if kind == 'predict' else 0)
        if kind != 'commit':
            assert record.output_cells == output_cells(kind, graph, runtime.contract.semantics, runtime.online_contract.learner)
        assert record.relation is not None and record.arena_phase is not None
        assert record.output_cells <= snapshot.cuda.contract.phase_output_cells
        expected[record.object_id], physical[record.object_id] = result, history
        checked += 1
    assert failed == int(expected_failure is not None)
    current = dict(snapshot.cuda.current)
    assert set(current) == {c.candidate_id for c in snapshot.candidates}
    for candidate in snapshot.candidates:
        actual = expected[current[candidate.candidate_id]]
        assert (actual.unit, actual.cursor, actual.steps) == (candidate.learner.unit_count, candidate.learner.cursor, candidate.learner.optimizer_steps)
    assert not any('likelihood-scratch' in key for key in buffers)
    storage, arena_bytes = snapshot.cuda.storage, snapshot.cuda.contract.storage.arena_bytes
    assert storage['actual_tensor_arena_bytes'] == arena_bytes
    assert storage['native_allocation_counter_current'] == storage['native_allocation_counter_at_binding'] == (1, arena_bytes, 1)
    return {'checked_phases': checked, 'refused_phases': failed, 'independent_commit_operation_tapes': commits,
        'factorization_ranks': sorted(model.rank for model, _, _ in banks.values()),
        'maximum_output_cells': max(r.output_cells for r in snapshot.cuda.phases),
        'largest_phase_frame_used': max(int.from_bytes(buffers[r.object_id][:8], 'big')+8 for r in snapshot.cuda.phases),
        'actual_arena_bytes': arena_bytes}


if __name__ == '__main__':
    print(json.dumps(exact_audit(), indent=2))
