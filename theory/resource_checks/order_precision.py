"""An equal-resource order tie need not preserve exact RNE feasibility.

The native input is reached by real reference Runtime events and checked
against the independent literal learner. Both alternative orders are passive
exact RNE evaluations, with no GPU, proposal admission or install authority.
"""
from fractions import Fraction as F
from itertools import combinations, permutations
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'),
                str(ROOT/'experiments/joint_uncertainty')]
from fp_reference import ReferenceCompilerRuntime, indexed_amp as amp
from fp_reference.indexed_relation import DecodeAllowance, partition_shape_plan
from fp_reference.positive_tape import compile_tape
from fp_reference.float64_bridge import Float64Contract
from fp_reference.semantics import ArithmeticUnresolved
from audit_indexed_runtime import fixture, literal, step
from audit_indexed_source_binding import predict, native
from query_order_resource_frontier import subset_costs


def audit():
    n, query = 4, (0, 3)
    counts = (-2, -2, -2, -2, -2, -1)
    edges = tuple(combinations(range(n), 2))
    history = tuple((u, v, int(d < 0)) for (u, v), d in zip(edges, counts) for _ in range(abs(d)))
    cfg, schema, online = fixture(n, len(history)+1)
    runtime = ReferenceCompilerRuntime(cfg, schema, online=online)
    models = {runtime.snapshot().deployed_id: literal(n)}
    for event in history:
        step(runtime, schema, event, models)
    assert predict(runtime, schema, query).status == 'PREDICTED_REFERENCE'
    snapshot = runtime.snapshot()
    reference = snapshot.pending.predictions[0][1]
    expected, learner = native(schema, history, query)
    assert reference.materialize(scalar_cap=1000) == expected
    assert snapshot.candidates[0].learner.materialize(scalar_cap=1000) == learner
    assert reference.before.counts == counts and reference.probabilities[0] == F(59013, 328010)
    assert snapshot.cursor == 11 and snapshot.pending.record.target is None

    # Same exact input, complete order class and precision/range contract.
    # The existing Runtime has not admitted these alternative physical plans.
    budget = DecodeAllowance()
    precision = Float64Contract(F(1, 10**6), F(3, 200_000_000))
    normalizer_cap, activation_cap = F(10)+F(1, 10**6), F(8)
    before = amp.IndexedAmpState(reference.before)
    support = tuple(e for e, d in zip(edges, counts) if d)
    positions = tuple(edges.index(e) for e in support)
    orders = tuple(p+(2,) for p in permutations((0, 1)))
    optimum = subset_costs(n, support, query)
    rows = []
    for order in orders:
        shape = partition_shape_plan(n, support, query, order, budget)
        tape, heads = compile_tape(n, support, query, order=order, readout=False)
        plan = amp._finish_plan(n, query, support, positions, tuple(tape.nodes), heads,
                                tuple(shape.items()), 65536)
        arithmetic = amp._Arithmetic(32768)
        raw, _ = amp._prediction_schedule(plan, before, arithmetic)
        assert len(arithmetic.trace)+7 == plan.output_cells
        operations = tuple(('host-RNE32-ingress' if tag == 'constant' else
            'cast-float'+str(width) if tag == 'cast' else tag, width, (word,))
            for tag, width, word in arithmetic.trace)
        checked = amp.check_prediction_execution(plan, before, raw, operations, bit_limit=32768)
        # Read exact diagnostics with a loose probability bound, then apply
        # the single fixed contract above unchanged to both orders.
        diagnostics = amp.check_prediction(reference, raw, Float64Contract(precision.state_atol, F(1)),
            normalizer_cap=normalizer_cap, activation_cap=activation_cap, bit_limit=32768)
        reason = None
        try:
            amp.check_prediction(reference, raw, precision, normalizer_cap=normalizer_cap,
                                 activation_cap=activation_cap, bit_limit=32768)
            status = 'SATISFIES_FIXED_BRIDGE'
        except ArithmeticUnresolved as exc:
            status, reason = 'UNRESOLVED_SELECTED_ORDER', str(exc)
        rows.append({'order': order, 'output_cells': plan.output_cells, 'tape_nodes': len(plan.nodes),
            'table_shape': shape, 'half_outputs': sum(w == 16 for _, w, _ in arithmetic.trace),
            'checked_RNE_operations': checked, 'readout_words': raw.words,
            'probabilities': tuple(str(amp.single(w)) for w in raw.words[5:]),
            'exact_errors': {k: str(v) for k, v in vars(diagnostics).items()},
            'status': status, 'reason': reason})
    assert len(rows) == 2 and optimum['order'] == rows[0]['order']
    assert (optimum['partition_only_output_cells'], optimum['partition_only_tape_nodes']) == (70, 69)
    assert all((r['output_cells'], r['tape_nodes']) == (70, 69) for r in rows)
    assert rows[0]['table_shape'] == rows[1]['table_shape']
    assert rows[0]['status'] == 'UNRESOLVED_SELECTED_ORDER' and rows[1]['status'] == 'SATISFIES_FIXED_BRIDGE'
    assert 'torch' not in sys.modules
    return {'status': 'PASS_ORDER_RESOURCE_PRECISION_SEPARATION',
        'scope': 'exact native input and passive RNE counterexample to precision-safe resource tie pruning; no existing structural theorem falsified and no actual CUDA claim',
        'n': n, 'query': query, 'counts': counts, 'owned_reference_events': len(history),
        'full_native_learner_and_query_cache_match_literal': True,
        'next_target_revealed': False, 'exact_native_probabilities': tuple(map(str, reference.probabilities)),
        'contract': {'state_atol': str(precision.state_atol), 'probability_atol': str(precision.probability_atol),
            'normalizer_cap': str(normalizer_cap), 'activation_cap': str(activation_cap),
            'join_cells': budget.join_cells, 'live_cells': budget.live_cells,
            'output_cells': 65536, 'tape_nodes': amp.MAX_TAPE_CELLS},
        'structural_DP': optimum, 'complete_query_retaining_order_class': rows,
        'conclusion': 'the selected order is numerically unresolved; the two-order resource-and-precision feasible class is nonempty'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = audit()
    if args.write:
        (ROOT/'evidence/minimal/FP_ORDER_PRECISION_SEPARATION.json').write_text(
            json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
