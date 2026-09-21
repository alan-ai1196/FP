"""Complete native-reference coordinate bridge for a compact numerical phase.

Counts represent parameters exactly; three stored single-precision gradient
forms represent the full pending accumulator. Native cache indices retain
their fixed source/pair/parity meaning and seven actual readout words.
This component experiment has no Runtime, ingress or installation authority.
"""
from dataclasses import dataclass, replace
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
import argparse
import json
import os
import sys
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(Path(__file__).resolve().parent)]
import count_learner_encoding as counts
import indexed_relation_reference as indexed
import radix9_frontier as radix
import radix9_power_lowering as lowering
import radix9_accuracy_enclosure as enclosure
import simplex_gradient as native
from fp_reference.core import ContractError, natural
from fp_reference.learner import ReferenceLearnerState, observe_event, commit_event
from fp_reference.profile import attach_boundary
from fp_reference.semantics import ArithmeticUnresolved, Evaluation, evaluate

STATE_ATOL = F(1, 100)
PROBABILITY_ATOL = F(1, 1000)
COUNTER_CAP = (1 << 62)-1
MAX_BATCH = 512
MAX_TAPE_CELLS = 262144


def check_count(state):
    if type(state) is not counts.CountState:
        raise ContractError('complete immutable count state required')
    indexed.IndexedRelation(state.n)
    if max(state.cursor, state.steps, sum(map(abs, state.counts))) > COUNTER_CAP:
        raise ArithmeticUnresolved('compact numerical counter envelope exhausted')


def single(word):
    if type(word) is not int or not 0 <= word < (1 << 32):
        raise ContractError('raw single-precision word required')
    if (word >> 23) & 255 == 255:
        raise ArithmeticUnresolved('nonfinite compact numerical word')
    return radix.SINGLE.decode(word)


@dataclass(frozen=True)
class CompactState:
    encoded: counts.CountState
    gradient_words: tuple[int, ...] = ()  # fixed slot, matching world, other world

    def __post_init__(self):
        check_count(self.encoded)
        if type(self.gradient_words) is not tuple or len(self.gradient_words) != (3 if self.encoded.pending else 0):
            raise ContractError('pending state requires all three gradient forms; committed state has none')
        for word in self.gradient_words:
            single(word)

    def gradient(self, slot):
        schema = indexed.IndexedRelation(self.encoded.n)
        indexed.index(slot, schema.slot_count, 'compact gradient slot')
        if self.encoded.pending is None:
            return F(0)
        if slot == 0:
            return single(self.gradient_words[0])
        i, j, y = self.encoded.pending
        match = (schema.world_bit(slot-1, i) ^ schema.world_bit(slot-1, j)) == y
        return single(self.gradient_words[1 if match else 2])

    def commit(self):
        # This is the proved unit-simplex rewrite, not an SGD step using a
        # discarded approximation to theta. The pending gradient stays in
        # the immutable predecessor even if the guarded commit refuses.
        following = counts.commit(self.encoded)
        check_count(following)
        return CompactState(following)

    def attach(self, cursor):
        following = counts.attach(self.encoded, cursor)
        check_count(following)
        return CompactState(following)

    def materialize(self, *, scalar_cap):
        schema = indexed.IndexedRelation(self.encoded.n)
        indexed.allowance(2*schema.slot_count+3, scalar_cap, 'compact learner explicit scalar allowance')
        ref = indexed.bound_view(schema, self.encoded, (0, 0))
        return ReferenceLearnerState(tuple(ref.theta(k) for k in range(schema.slot_count)), (),
            tuple(self.gradient(k) for k in range(schema.slot_count)), ref.unit_count, ref.cursor, ref.optimizer_steps)


@dataclass(frozen=True)
class CompactPrediction:
    before: counts.CountState
    query: tuple[int, int]
    words: tuple[int, ...]  # excess0/1, mass0/1, normalizer, probability0/1

    def __post_init__(self):
        check_count(self.before)
        if self.before.pending is not None:
            raise ContractError('prediction requires a committed predecessor')
        if type(self.query) is not tuple or len(self.query) != 2:
            raise ContractError('complete ordered prediction query required')
        counts.query(self.before.n, *self.query)
        if type(self.words) is not tuple or len(self.words) != 7:
            raise ContractError('complete seven-word native readout required')
        decoded = tuple(single(v) for v in self.words)
        if (min(decoded) < 0 or max(decoded[:2]) > 8 or min(decoded[2:5]) <= 0
                or not all(0 < p < 1 for p in decoded[5:])):
            raise ArithmeticUnresolved('compact readout violates its positive native range')

    def values(self):
        return tuple(single(v) for v in self.words)

    def materialize(self, *, scalar_cap):
        schema = indexed.IndexedRelation(self.before.n)
        indexed.allowance(schema.graph_counts()['nodes']+7, scalar_cap, 'compact cache explicit scalar allowance')
        view = indexed.bound_view(schema, self.before, self.query)
        raw = self.values()
        values = tuple(view.value(k) for k in range(schema.heads[0]))+raw[:2]
        return Evaluation(values, raw[:2], raw[2:4], raw[4], raw[5:7], ())


@dataclass(frozen=True)
class TargetEnclosure:
    """Bound result of this experiment's actual checked binary64 execution.

    This passive record cannot prove that a caller executed anything and is
    not an authority token. Runtime must eventually own its checked origin.
    """
    before: counts.CountState
    query: tuple[int, int]
    probability64: F
    mass_budget: int

    @property
    def interval(self):
        return enclosure.enclosure(self.probability64, self.mass_budget)


def prepared_tape(n, support, query, *, batch_size=1, budget=indexed.DecodeAllowance()):
    schema = indexed.IndexedRelation(n)
    counts.query(n, *query)
    order = tuple(range(n-1))
    plan = indexed.partition_shape_plan(n, support, query, order, budget)
    factor_cells = sum(2 if i == 0 else 4 for i, j in support)
    tape_size = factor_cells+plan['positive_multiplications']+plan['positive_additions']+6
    indexed.allowance(batch_size, MAX_BATCH, 'phase batch allowance')
    indexed.allowance(batch_size*tape_size, MAX_TAPE_CELLS, 'retained numerical tape-cell allowance')
    indexed.allowance(batch_size*(plan['positive_multiplications']+plan['positive_additions']),
                      budget.arithmetic, 'batched table arithmetic allowance')
    tape, heads = radix.compile_tape(n, support, query, order=order)
    assert tape.elimination_order == order
    assert len(tape.nodes) == tape_size
    return schema, tape, heads, plan


def execute_predictions(states, query, *, torch=None, budget=indexed.DecodeAllowance()):
    if type(states) is not tuple or not states:
        raise ContractError('complete immutable batch of predecessors required')
    indexed.allowance(len(states), MAX_BATCH, 'phase batch allowance')
    if any(type(s) is not CompactState or s.encoded.pending is not None for s in states):
        raise ContractError('committed compact predecessors required')
    n = states[0].encoded.n
    if any(s.encoded.n != n for s in states):
        raise ContractError('one batch must share its indexed code')
    edges = tuple(combinations(range(n), 2))
    # A fixed union supports batching different states, including zero factors.
    support = tuple(edge for e, edge in enumerate(edges) if any(s.encoded.counts[e] for s in states))
    schema, tape, heads, plan = prepared_tape(n, support, query, batch_size=len(states), budget=budget)
    positions = {edge: e for e, edge in enumerate(edges)}
    rows = tuple(tuple(s.encoded.counts[positions[e]] for e in support) for s in states)
    if any(sum(map(abs, row))+len(tape.nodes)+4 > radix.EXPONENT_CAP for row in rows):
        raise ArithmeticUnresolved('phase exponent envelope exhausted before device execution')
    decoder = lowering.Decoder(len(states), 'amp', torch)
    _, numerical = decoder.run(tape, heads, rows)
    arith = decoder.arith
    parts = tuple(numerical[h] for h in tape.partition_heads)
    high = tuple(max(a, b) for a, b in zip(parts[0].exponent, parts[1].exponent))
    aligned = []
    for part in parts:
        difference = tuple(e-p for e, p in zip(high, part.exponent))
        factor = arith.gather(decoder.powers, tuple(min(d, radix.CUTOFF-1) for d in difference))
        factor = arith.choose(tuple(d >= radix.CUTOFF for d in difference), decoder.zero, factor)
        aligned.append(arith.operation('mul', part.mantissa, factor))
    denominator = arith.operation('add', *aligned)
    marginals = tuple(arith.operation('div', part, denominator) for part in aligned)
    eight = arith.operation('constant', constant=8)
    excesses = tuple(arith.operation('mul', eight, q) for q in marginals)
    masses = tuple(arith.operation('add', decoder.one, e) for e in excesses)
    normalizer = arith.operation('add', *masses)
    probabilities = tuple(arith.operation('div', m, normalizer) for m in masses)
    columns = excesses+masses+(normalizer,)+probabilities
    predictions = tuple(CompactPrediction(s.encoded, query,
        tuple(radix.SINGLE.encode_exact(column.values[i]) for column in columns)) for i, s in enumerate(states))
    # This independent, checked binary64 computation supplies only reference
    # enclosures. None of its answers is uploaded into the actual GPU path.
    reference = radix.Decoder(len(states), 'binary64')
    p64, _ = reference.run(tape, heads, rows)
    bounds = tuple(TargetEnclosure(s.encoded, query, p, max(tape.budgets[h] for h in heads))
                   for s, p in zip(states, p64.values))
    work = {'table_plan': plan, 'tape_nodes': len(tape.nodes),
            'general_product_nodes': decoder.nonpower_products, 'exact_shift_nodes': decoder.exact_shifts,
            'checked_binary64_primitives': reference.arith.float64.operations}
    return predictions, bounds, (decoder, masses, predictions), work


def execute_observations(states, predictions, targets, execution):
    decoder, masses, sealed_predictions = execution
    if tuple(predictions) != sealed_predictions:
        raise ContractError('gradient execution is not bound to these preceding prediction words')
    if len(states) != len(predictions) or len(states) != len(targets):
        raise ContractError('complete matched batch of predecessors, predictions and targets required')
    for state, prediction, target in zip(states, predictions, targets):
        if state.encoded != prediction.before or state.encoded.pending is not None:
            raise ContractError('observation predecessor differs from its preceding prediction')
        counts.query(state.encoded.n, *prediction.query, target)
    arith = decoder.arith
    mass = arith.choose(tuple(y == 0 for y in targets), masses[0], masses[1])
    eight = arith.operation('constant', constant=8)
    minus_one = arith.operation('constant', constant=-1)
    minus_fifth = arith.operation('constant', constant=F(-1, 5))
    four_fifths = arith.operation('constant', constant=F(4, 5))
    fixed = arith.operation('add', arith.operation('div', decoder.one, mass), minus_fifth)
    matching = arith.operation('add', four_fifths,
        arith.operation('mul', minus_one, arith.operation('div', eight, mass)))
    columns = fixed, matching, four_fifths
    return tuple(CompactState(counts.observe(s.encoded, *p.query, y),
        tuple(radix.SINGLE.encode_exact(column.values[i]) for column in columns))
        for i, (s, p, y) in enumerate(zip(states, predictions, targets)))


def target_intervals(probability_bounds, target):
    lo, hi = probability_bounds
    if not F(1, 10) <= lo <= hi <= F(9, 10):
        raise ContractError('proved known-noise reference interval required')
    masses = ((10*lo, 10*hi), (10*(1-hi), 10*(1-lo)))
    excesses = tuple((a-1, b-1) for a, b in masses)
    intervals = excesses+masses+((F(10), F(10)), (lo, hi), (1-hi, 1-lo))
    a, b = masses[target]
    gradients = ((1/b-F(1, 5), 1/a-F(1, 5)),
                 (F(4, 5)-8/a, F(4, 5)-8/b), (F(4, 5), F(4, 5)))
    return intervals, gradients


def error_interval(value, interval):
    lo, hi = interval
    return max(lo-value, value-hi, F(0)), max(abs(value-lo), abs(value-hi))


def check_complete(reference, prediction, observed, target_enclosure, *, target):
    if type(reference) is not counts.CountState or type(prediction) is not CompactPrediction or type(observed) is not CompactState:
        raise ContractError('complete typed reference, prediction and numerical observation required')
    pending = observed.encoded.pending
    counts.query(reference.n, *prediction.query, target)
    if pending != prediction.query+(target,):
        raise ContractError('the accumulator differs from the independently observed query/target')
    if reference != prediction.before or counts.observe(reference, *prediction.query, target) != observed.encoded:
        raise ContractError('complete count/clock/pending transition does not commute')
    if (type(target_enclosure) is not TargetEnclosure or target_enclosure.before != reference
            or target_enclosure.query != prediction.query):
        raise ContractError('target enclosure belongs to another complete predecessor or query')
    intervals, gradients = target_intervals(target_enclosure.interval, pending[2])
    predicted_errors = tuple(error_interval(value, interval) for value, interval in zip(prediction.values(), intervals))
    # For a diagonal exactly one of the two world-gradient classes occurs.
    active = (0, 1, 2) if pending[0] != pending[1] else (0, 1 if pending[2] == 0 else 2)
    gradient_errors = tuple(error_interval(single(observed.gradient_words[k]), gradients[k]) for k in active)
    state = tuple(max(e[j] for e in gradient_errors) for j in (0, 1))
    native_error = tuple(max(e[j] for e in predicted_errors[:4]) for j in (0, 1))
    normalizer = predicted_errors[4]
    probability = tuple(max(e[j] for e in predicted_errors[5:]) for j in (0, 1))
    pairs = ((state, STATE_ATOL), (native_error, STATE_ATOL),
             (normalizer, STATE_ATOL), (probability, PROBABILITY_ATOL))
    status = ('WITHIN_COMPLETE_REFERENCE_TOLERANCES' if all(e[1] <= tol for e, tol in pairs)
              else 'OUTSIDE_COMPLETE_REFERENCE_TOLERANCES' if any(e[0] > tol for e, tol in pairs) else 'UNRESOLVED')
    return {'status': status, 'state_error': state, 'native_error': native_error,
            'normalizer_error': normalizer, 'probability_error': probability,
            'parameter_error': F(0), 'exact_discrete_state': True}


def serial(value):
    if type(value) is F:
        return str(value)
    if type(value) is dict:
        return {k: serial(v) for k, v in value.items()}
    if type(value) in (list, tuple):
        return [serial(v) for v in value]
    return value


def native_controls(n, support, rows):
    rules, graph, _ = native.relation_graph(n)
    spec = indexed.IndexedRelation(n).materialize_learner(slot_cap=64)
    result, units = [], 0
    for row in rows:
        reference = counts.native_initial(n)
        history = tuple((i, j, int(d < 0)) for (i, j), d in zip(support, row) for _ in range(abs(d)))
        for i, j, y in history:
            prediction = evaluate(graph, rules, reference.theta, native.context(n, i, j), (), bit_limit=32768)
            reference = commit_event(observe_event(graph, reference, spec, prediction, y, bit_limit=32768),
                                     spec, bit_limit=32768)
            units += 1
        signed = [0]*(n*(n-1)//2)
        edges = tuple(combinations(range(n), 2))
        for i, j, y in history:
            signed[edges.index((i, j))] += 1-2*y
        encoded = counts.CountState(n, tuple(signed), None, len(history), len(history))
        assert indexed.bound_view(indexed.IndexedRelation(n), encoded, (0, 0)).materialize_state(scalar_cap=1000) == reference
        result.append((CompactState(encoded), reference))
    return tuple(result), units


def compare_native(state, reference, prediction, observed, target, target_enclosure, *, native_prediction=None):
    n = state.encoded.n
    rules, graph, _ = native.relation_graph(n)
    spec = indexed.IndexedRelation(n).materialize_learner(slot_cap=64)
    actual = (evaluate(graph, rules, reference.theta, native.context(n, *prediction.query), (), bit_limit=32768)
              if native_prediction is None else native_prediction)
    native_observed = observe_event(graph, reference, spec, actual, target, bit_limit=32768)
    native_committed = commit_event(native_observed, spec, bit_limit=32768)
    relation = check_complete(state.encoded, prediction, observed, target_enclosure, target=target)
    numerical = prediction.materialize(scalar_cap=10000)
    numerical_state = observed.materialize(scalar_cap=1000)
    assert numerical_state.theta == native_observed.theta
    assert (numerical_state.delayed, numerical_state.unit_count, numerical_state.cursor, numerical_state.optimizer_steps) == (
        native_observed.delayed, native_observed.unit_count, native_observed.cursor, native_observed.optimizer_steps)
    assert observed.commit().materialize(scalar_cap=1000) == native_committed
    lo, hi = target_enclosure.interval
    assert lo <= actual.probabilities[0] <= hi
    differences = {
        'state_error': max(abs(a-b) for a, b in zip(numerical_state.gradient_sum, native_observed.gradient_sum)),
        'native_error': max(abs(a-b) for a, b in zip(numerical.values+numerical.excesses+numerical.masses,
                                                     actual.values+actual.excesses+actual.masses)),
        'normalizer_error': abs(numerical.normalizer-actual.normalizer),
        'probability_error': max(abs(a-b) for a, b in zip(numerical.probabilities, actual.probabilities))}
    for key, value in differences.items():
        assert relation[key][0] <= value <= relation[key][1], (key, value, relation[key])
    assert relation['status'] == 'WITHIN_COMPLETE_REFERENCE_TOLERANCES', serial(relation)
    return differences, native_committed


def small_audit(torch=None):
    groups = ((3, ((0, 1), (0, 2), (1, 2)), tuple(product(range(-2, 3), repeat=3)), tuple(product(range(3), repeat=2))),
              (5, ((0, 1), (1, 2), (1, 3), (1, 4)), tuple(product(range(-1, 2), repeat=4)),
               ((0, 1), (1, 4), (2, 3), (0, 0), (4, 4))))
    reports = []
    for n, support, rows, queries in groups:
        controls, units = native_controls(n, support, rows)
        states = tuple(s for s, ref in controls)
        references = tuple(ref for s, ref in controls)
        maxima = {k: F(0) for k in ('state_error', 'native_error', 'normalizer_error', 'probability_error')}
        phases = words = rounded = binary64 = general = 0
        rules, graph, _ = native.relation_graph(n)
        for query in queries:
            predictions, bounds, execution, work = execute_predictions(states, query, torch=torch)
            native_predictions = tuple(evaluate(graph, rules, ref.theta, native.context(n, *query), (), bit_limit=32768)
                                       for ref in references)
            # Fork both possible labels from the same complete pre-target
            # prediction. Reusing it does not skip either observation/commit.
            for y in (0, 1):
                observations = execute_observations(states, predictions, (y,)*len(states), execution)
                for s, ref, p, o, b, actual in zip(states, references, predictions, observations, bounds, native_predictions):
                    errors, _ = compare_native(s, ref, p, o, y, b, native_prediction=actual)
                    for key, value in errors.items():
                        maxima[key] = max(maxima[key], value)
                    phases += 1
            arith = execution[0].arith
            words += arith.device_words
            rounded += arith.scalar_results
            binary64 += work['checked_binary64_primitives']
            general += work['general_product_nodes']
        reports.append({'n': n, 'count_profiles': len(rows), 'queries': len(queries), 'targets_per_query': 2,
                        'distinct_pre_target_predictions': len(rows)*len(queries),
                        'native_preparation_units': units, 'complete_native_phase_comparisons': phases,
                        'general_product_nodes': general, 'rounded_scalar_results': rounded,
                        'checked_binary64_primitives': binary64, 'checked_device_words': words,
                        'maximum_exact_native_errors': maxima})
    return reports


def trajectory_audit(torch=None):
    reports = []
    for name, n, events, attach_cut, birth in (
        ('profile_and_continuation', 3, ((0, 1, 0), (1, 2, 1), (0, 2, 0))*2+((2, 0, 1), (0, 0, 0), (1, 2, 0)), 6, 0),
        ('late_birth_reversal', 2, ((0, 1, 0),)*50+((0, 1, 1),)*50, None, 7)):
        state = CompactState(counts.initialize(n, birth))
        reference = counts.native_initial(n, birth)
        maxima = {k: F(0) for k in ('state_error', 'native_error', 'normalizer_error', 'probability_error')}
        words = rounded = binary64 = 0
        for k, event in enumerate(events):
            if k == attach_cut:
                state = state.attach(20)
                reference = attach_boundary(reference, 20, counts.spec(n))
                assert state.materialize(scalar_cap=100) == reference
            predictions, bounds, execution, work = execute_predictions((state,), event[:2], torch=torch)
            observed = execute_observations((state,), predictions, (event[2],), execution)[0]
            errors, reference = compare_native(state, reference, predictions[0], observed, event[2], bounds[0])
            for key, value in errors.items():
                maxima[key] = max(maxima[key], value)
            state = observed.commit()
            words += execution[0].arith.device_words
            rounded += execution[0].arith.scalar_results
            binary64 += work['checked_binary64_primitives']
        if n == 2:
            assert state.encoded.counts == (0,) and reference.theta == (F(1), F(1, 2), F(1, 2))
        reports.append({'name': name, 'events': len(events), 'final_cursor': state.encoded.cursor,
                        'final_steps': state.encoded.steps, 'checked_device_words': words,
                        'rounded_scalar_results': rounded, 'checked_binary64_primitives': binary64,
                        'maximum_exact_native_errors': maxima})
    return reports


def large_audit(torch=None):
    n = 256
    schema = indexed.IndexedRelation(n)
    state = CompactState(counts.CountState(n, (0,)*(n*(n-1)//2), None, 0, 0))
    events = ((0, 1, 0), (0, 0, 0), (1, 2, 0), (0, 2, 1))
    exact_probabilities = (F(1, 2), F(9, 10), F(1, 2), F(189, 250))
    reports = []
    words = rounded = binary64 = 0
    for k, (event, exact_probability) in enumerate(zip(events, exact_probabilities)):
        if k == 3:
            state = state.attach(20)
        predictions, bounds, execution, work = execute_predictions((state,), event[:2], torch=torch)
        observed = execute_observations((state,), predictions, (event[2],), execution)[0]
        relation = check_complete(state.encoded, predictions[0], observed, bounds[0], target=event[2])
        lo, hi = bounds[0].interval
        assert lo <= exact_probability <= hi
        assert relation['status'] == 'WITHIN_COMPLETE_REFERENCE_TOLERANCES'
        intervals, exact_gradients = target_intervals((exact_probability, exact_probability), event[2])
        for value, interval in zip(predictions[0].values(), intervals):
            assert abs(value-interval[0]) <= max(relation['native_error'][1], relation['probability_error'][1], relation['normalizer_error'][1])
        for slot in (0, 1, schema.K//2+1, schema.K):
            if slot == 0:
                category = 0
            else:
                match = (schema.world_bit(slot-1, event[0]) ^ schema.world_bit(slot-1, event[1])) == event[2]
                category = 1 if match else 2
            assert abs(observed.gradient(slot)-exact_gradients[category][0]) <= relation['state_error'][1]
        reports.append({'event': event, 'exact_reference_probability0': exact_probability,
                        'relation': relation, 'general_product_nodes': work['general_product_nodes']})
        state = observed.commit()
        words += execution[0].arith.device_words
        rounded += execution[0].arith.scalar_results
        binary64 += work['checked_binary64_primitives']
    view = indexed.bound_view(schema, state.encoded, (0, 1))
    # The unchanged free variables contribute K/4 copies of the four weights
    # (81,81,1,81); this independent formula covers the entire parameter map.
    for slot in (1, 2, schema.K//2, schema.K//2+1, schema.K):
        a, b = schema.world_bit(slot-1, 1), schema.world_bit(slot-1, 2)
        assert view.theta(slot) == F(1 if (a, b) == (1, 0) else 81, 61*schema.K)
    assert state.encoded.cursor == 21 and state.encoded.steps == 4
    refused = sum(indexed.refusal(fn, ArithmeticUnresolved) for fn in (
        lambda: state.materialize(scalar_cap=100000),
        lambda: predictions[0].materialize(scalar_cap=100000)))
    return {'n': n, 'logical_worlds_power_of_two': n-1, 'executed_component_events': 4,
            'profile_attachment': [3, 20], 'final_cursor': 21, 'final_steps': 4,
            'parameter_formula': '(81,81,1,81)/(61*K), repeated over free coordinates',
            'explicit_full_output_refusals': refused, 'phases': reports,
            'checked_device_words': words, 'rounded_scalar_results': rounded,
            'checked_binary64_primitives': binary64}


def correlated_audit(torch=None):
    n, query = 256, (0, 96)
    states = []
    for height in (16, 10**12):
        support, row = enclosure.cycle_input(n, height)
        signed = tuple(row[support.index(edge)] if edge in support else 0 for edge in combinations(range(n), 2))
        states.append(CompactState(counts.CountState(n, signed, None, n*height, n*height)))
    states = tuple(states)
    predictions, bounds, execution, work = execute_predictions(states, query, torch=torch)
    rows = []
    for y in (0, 1):
        observed = execute_observations(states, predictions, (y,)*len(states), execution)
        for height, s, p, o, b in zip((16, 10**12), states, predictions, observed, bounds):
            relation = check_complete(s.encoded, p, o, b, target=y)
            assert relation['status'] == 'WITHIN_COMPLETE_REFERENCE_TOLERANCES', serial(relation)
            # Independent positive cycle tail bounds, without huge 9^height.
            target = enclosure.limiting_interval(n, query, height)
            assert b.interval[0] <= target[0] <= target[1] <= b.interval[1]
            successor = o.commit()
            assert successor.encoded.pending is None and successor.encoded.steps == n*height+1
            rows.append({'height': height, 'target': y, 'relation': relation})
    return {'n': n, 'query': query, 'synthetic_reachable_states': 2, 'executed_component_observations': 4,
            'history_scope': 'phase-map inputs; the n*height historical events are not replayed',
            'phases': rows, 'checked_device_words': execution[0].arith.device_words,
            'rounded_scalar_results': execution[0].arith.scalar_results,
            'checked_binary64_primitives': work['checked_binary64_primitives']}


def gradient_counterexample():
    """Adversarial readout perturbation, NOT a failure observed in our kernel."""
    state, reference = native_controls(2, ((0, 1),), ((4,),))[0][0]
    schema = indexed.IndexedRelation(2)
    probability = indexed.bound_view(schema, state.encoded, (0, 1)).probability(0)
    # A coherent nearby positive readout passes probability and native-value
    # tolerances, while its matching rare-world derivative is too far away.
    perturbed = probability-F(1, 2000)
    exact_values = (10*perturbed-1, 9-10*perturbed, 10*perturbed, 10*(1-perturbed), F(10), perturbed, 1-perturbed)
    prediction = CompactPrediction(state.encoded, (0, 1), tuple(radix.SINGLE.rounded(v) for v in exact_values))
    arith = radix.Arithmetic(1, 'amp')
    mass = arith.operation('constant', constant=prediction.values()[3])
    one = arith.operation('constant', constant=1)
    fixed = arith.operation('add', arith.operation('div', one, mass), arith.operation('constant', constant=F(-1, 5)))
    other = arith.operation('constant', constant=F(4, 5))
    matching = arith.operation('add', other, arith.operation('mul',
        arith.operation('constant', constant=-1),
        arith.operation('div', arith.operation('constant', constant=8), mass)))
    observed = CompactState(counts.observe(state.encoded, 0, 1, 1),
        tuple(radix.SINGLE.encode_exact(v.values[0]) for v in (fixed, matching, other)))
    intervals, gradients = target_intervals((probability, probability), 1)
    pred_errors = tuple(error_interval(v, i)[1] for v, i in zip(prediction.values(), intervals))
    grad_error = max(error_interval(single(v), i)[1] for v, i in zip(observed.gradient_words, gradients))
    assert max(pred_errors[:5]) < STATE_ATOL and max(pred_errors[5:]) < PROBABILITY_ATOL
    assert grad_error > STATE_ATOL
    # Use a real bound from the independent binary64 execution, with its
    # original count/query binding, to exercise the same complete checker.
    _, bounds, _, _ = execute_predictions((state,), (0, 1))
    result = check_complete(state.encoded, prediction, observed, bounds[0], target=1)
    assert result['status'] == 'OUTSIDE_COMPLETE_REFERENCE_TOLERANCES'
    return {'scope': 'synthetic nearby-readout adversary, not an actual main-kernel failure or weak baseline',
            'reference_count': 4, 'target': 1, 'probability_shift': F(1, 2000),
            'maximum_probability_error': max(pred_errors[5:]), 'maximum_native_error': max(pred_errors[:5]),
            'maximum_gradient_error': grad_error, 'complete_relation': result}


def boundary_audit():
    schema = indexed.IndexedRelation(3)
    state = CompactState(counts.initialize(3))
    predictions, bounds, execution, work = execute_predictions((state,), (0, 1))
    observed = execute_observations((state,), predictions, (0,), execution)[0]
    p, b = predictions[0], bounds[0]
    forged = replace(observed, encoded=replace(observed.encoded, pending=(0, 1, 1)))
    assert forged.gradient_words == observed.gradient_words
    # Reproduce the draft verifier's circular assumption explicitly: its
    # "reference target" was copied from the physical report being checked.
    circular = check_complete(state.encoded, p, forged, b, target=forged.encoded.pending[2])
    assert circular['status'] == 'WITHIN_COMPLETE_REFERENCE_TOLERANCES'
    correct_next = indexed.bound_view(schema, observed.commit().encoded, (0, 1)).probability(0)
    forged_next = indexed.bound_view(schema, forged.commit().encoded, (0, 1)).probability(0)
    assert (correct_next, forged_next) == (F(41, 50), F(9, 50))
    swapped_error = max(abs(forged.gradient(k)-observed.gradient(k)) for k in range(schema.slot_count))
    assert swapped_error > STATE_ATOL
    refused = 0
    for function in (
        lambda: execute_observations((CompactState(replace(state.encoded, cursor=1)),), predictions, (0,), execution),
        lambda: execute_observations((state,), (replace(p, query=(1, 0)),), (0,), execution),
        lambda: check_complete(state.encoded, p, replace(observed, encoded=replace(observed.encoded, cursor=2)), b, target=0),
        lambda: check_complete(state.encoded, p, replace(observed, encoded=replace(observed.encoded, steps=1)), b, target=0),
        lambda: check_complete(state.encoded, p, replace(observed, encoded=replace(observed.encoded, pending=(0, 1, 1))), b, target=0),
        lambda: check_complete(state.encoded, p, observed, replace(b, query=(1, 0)), target=0),
        lambda: check_complete(state.encoded, p, observed, replace(b, before=replace(state.encoded, steps=1)), target=0),
        lambda: observed.attach(20), lambda: state.commit(),
        lambda: CompactState(observed.encoded, (0x7f800000,)+observed.gradient_words[1:]),
        lambda: CompactPrediction(state.encoded, (0, 1), p.words[:-1])):
        refused += indexed.refusal(function)
    # A finite synthetic profile endpoint at the clock cap can still predict
    # and observe. Its next commit must fail without deleting that observation.
    edge = counts.CountState(2, (0,), None, 0, COUNTER_CAP)
    boundary = CompactState(edge)
    ps, bs, ex, _ = execute_predictions((boundary,), (0, 0))
    pending = execute_observations((boundary,), ps, (0,), ex)[0]
    assert check_complete(edge, ps[0], pending, bs[0], target=0)['status'] == 'WITHIN_COMPLETE_REFERENCE_TOLERANCES'
    refused_commit = indexed.refusal(pending.commit, ArithmeticUnresolved)
    assert pending.encoded.pending == (0, 0, 0) and pending.encoded.cursor == 1
    assert pending.encoded.steps == COUNTER_CAP and pending.gradient_words
    # Refusals must precede every arithmetic constructor, including constants.
    original = radix.Arithmetic
    def forbidden(*args, **kwargs):
        raise AssertionError('an unfunded phase entered its numerical executor')
    radix.Arithmetic = forbidden
    try:
        dense = CompactState(counts.CountState(16, (1,)*120, None, 120, 120))
        preflight = indexed.refusal(lambda: execute_predictions((dense,), (0, 1)), ArithmeticUnresolved)
        preflight += indexed.refusal(lambda: execute_predictions((state,), (0, 1),
            budget=indexed.DecodeAllowance(arithmetic=1)), ArithmeticUnresolved)
        preflight += indexed.refusal(lambda: execute_predictions((state,)*(MAX_BATCH+1), (0, 1)), ArithmeticUnresolved)
    finally:
        radix.Arithmetic = original
    return {'bad_phase_state_query_or_word_refusals': refused, 'retained_pending_clock_refusals': refused_commit,
            'pre_numeric_resource_refusals': preflight,
            'self_reported_target_counterexample': {
                'actual_target': 0, 'forged_target': 1, 'unchanged_gradient_words': observed.gradient_words,
                'circular_check_status': circular['status'], 'independent_actual_target_check': 'REFUSED',
                'decoded_gradient_swap': swapped_error, 'correct_next_probability': correct_next,
                'forged_next_probability': forged_next},
            'clock_case_scope': 'synthetic reachable endpoint; no COUNTER_CAP-event history is replayed'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cuda-worker', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = {}
    try:
        torch = None
        if args.cuda_worker:
            import torch
            assert torch.cuda.is_available()
            torch.cuda.set_device(0)
            assert (torch.__version__, torch.version.cuda, torch.cuda.get_device_name(0), torch.cuda.get_device_capability(0)) == (
                '2.12.0+cu132', '13.2', 'NVIDIA GeForce RTX 3090', (8, 6))
            torch.cuda.reset_peak_memory_stats()
        report = {'status': 'PASS_ACTUAL_COMPACT_PHASES' if torch else 'PASS_EXACT_COMPACT_PHASE_AUDIT',
                  'small_audit': small_audit(torch), 'trajectories': trajectory_audit(torch)}
        original = native.relation_graph
        def forbidden(_):
            raise AssertionError('a large phase tried to construct an exponential native graph')
        native.relation_graph = forbidden
        try:
            report['large_prefix'] = large_audit(torch)
            report['correlated_states'] = correlated_audit(torch)
        finally:
            native.relation_graph = original
        report.update(gradient_counterexample=gradient_counterexample(), boundaries=boundary_audit())
        report['scope'] = 'complete native-reference coordinate/phase component bridge; no owned Runtime, source acquisition, persistence or installation authority'
        if torch:
            torch.cuda.synchronize()
            report.update(process_id=os.getpid(), torch=torch.__version__, CUDA=torch.version.cuda,
                          device=torch.cuda.get_device_name(0), peak_torch_allocated_bytes=torch.cuda.max_memory_allocated(),
                          peak_torch_reserved_bytes=torch.cuda.max_memory_reserved())
    except Exception:
        args.output.write_text(json.dumps(serial({'status': 'FAILED', 'process_id': os.getpid(),
            'completed_components': report, 'traceback': traceback.format_exc()}), indent=2)+'\n', encoding='utf-8')
        raise
    args.output.write_text(json.dumps(serial(report), indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'small_complete_phase_comparisons':
        sum(row['complete_native_phase_comparisons'] for row in report['small_audit'])}, indent=2))


if __name__ == '__main__':
    main()
