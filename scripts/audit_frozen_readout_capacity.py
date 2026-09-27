"""Model-scope audit for ordinary text; no corpus, training job or certificate.

The finite controls test a general frozen positive-head argument and inspect
the actual full-vocabulary resource fixture. They do not select a text model.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from unittest.mock import patch
import argparse
import ast
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'), str(ROOT/'experiments/next_token')]
from fp_reference.numerics import log_enclosure
from fp_reference.token_reporting import add_loss
from fp_reference.program import Sum, Product, Term, SemanticRules
from fp_reference.token_sources import TokenAtomFamily, TokenValues, TokenContext
from fp_reference.token_execution import TokenProgram, TokenInitializer, TokenReferenceMachine, TokenState
from fp_reference.token_arrays import CPUArrays
from fp_reference.token_array_check import CheckedPrimitives
from fp_reference.token_array_events import Kernel, Forecast
from fp_reference.token_causal import TokenSources, TokenWindow
from fp_reference import token_native as native, token_readout as readout, token_batch as batch
from audit_token_reference_host import text_model_fixture


def components(base, weights):
    """Passive exact distribution columns; zero columns contribute no mass."""
    denominator = sum(base, F(0))
    rows = [tuple(b/denominator for b in base)]
    for column in zip(*weights):
        total = sum(column, F(0))
        if total:
            rows.append(tuple(w/total for w in column))
    return tuple(rows)


def bounds_display(value):
    interval = log_enclosure(value, terms=20, bit_limit=32768)
    total = add_loss((0, 0), interval, fractional_bits=48, bit_limit=32768)
    return [str(F(n, 1 << 48)) for n in total]


def finite_heads():
    matrices = queries = empirical_checks = 0
    base = (F(1), F(2), F(3))
    points = tuple(product((F(0), F(1, 2), F(3)), repeat=2))
    for flat in product((F(0), F(1), F(2)), repeat=6):
        weights = tuple(tuple(flat[2*y:2*y+2]) for y in range(3))
        comp = components(base, weights)
        maxima = tuple(max(row[y] for row in comp) for y in range(3))
        capacity = sum(maxima, F(0))
        assert 1 <= capacity <= len(comp) <= 3
        best = [F(0)]*3
        for features in points:
            masses = tuple(base[y]+sum((w*z for w, z in zip(weights[y], features)), F(0)) for y in range(3))
            probabilities = tuple(m/sum(masses, F(0)) for m in masses)
            assert sum(probabilities, F(0)) == 1
            for y, p in enumerate(probabilities):
                assert p <= maxima[y]
                best[y] = max(best[y], p)
                queries += 1
        for counts in ((1, 1, 1), (2, 1, 0), (0, 0, 3)):
            n = sum(counts)
            likelihood, floor_product = F(1), capacity**n
            for count, p in zip(counts, best):
                likelihood *= p**count
                if count:
                    floor_product *= F(count, n)**count
            # Equivalent exact exponentiated CE >= H(empirical Y)-log C.
            assert likelihood <= floor_product
            empirical_checks += 1
        matrices += 1
    return dict(complete_3_by_2_integer_head_class=matrices, exact_probability_bounds=queries,
                exact_empirical_entropy_inequalities=empirical_checks)


def physical_heads():
    """Test the roundoff allowance against the actual CPU array readout recipe."""
    import numpy as np
    cases = labels = 0
    largest_factor = F(1)
    u = F(1, 1 << 24)
    for bits, k in product((0, 16, 32), (1, 2, 3, 8)):
        d = native.Definition(TokenSources(3, k), 1, (), 0, tuple(range(k)),
            readout.Spec((F(1, 3), F(1, 1 << 149), F(3, 5)), k, bits, F(1), 1))
        master = np.asarray([0, 1, (1 << 24)+1, (1 << 32)-1], dtype=np.uint32)
        weights = np.resize(master, (3, k))
        origin = batch.Origin(d, batch.words(np.zeros((4, 1), dtype=np.uint32)), b'', batch.words(weights),
                              0, 0, TokenWindow(d.sources, 0, (3,)*k))
        a = CPUArrays(element_cap=4096, cell_cap=65536, audit=CheckedPrimitives(4096))
        kernel = Kernel(d, element_cap=4096)
        uploaded = kernel.upload(origin, a)
        prepared = kernel.prepare(uploaded, a)
        decoded_weights = a.scaled_master(uploaded.W, bits)
        exact_weights = tuple(tuple(F(float(w)) for w in row) for row in decoded_weights)
        exact_base = tuple(F(float(b)) for b in prepared.base)
        comp = components(exact_base, exact_weights)
        maxima = tuple(max(row[y] for row in comp) for y in range(3))
        depth = (k-1).bit_length()+2
        alpha, beta = (1-u)**depth, (1+u)**depth
        factor = beta/alpha
        largest_factor = max(largest_factor, factor)
        for offset in range(5):
            features = np.resize(np.roll(np.asarray((0, 2**-24, 2**-10, 1, 65504), dtype=np.float16), offset), k)
            forecast = Forecast(prepared, origin.source, features, np.asarray(1, dtype=np.float32))
            masses = tuple(F(float(kernel.readout_label(prepared, forecast, y, a)[0])) for y in range(3))
            ideal = tuple(exact_base[y]+sum((w*F(float(z)) for w, z in zip(exact_weights[y], features)), F(0))
                          for y in range(3))
            for y in range(3):
                assert alpha*ideal[y] <= masses[y] <= beta*ideal[y]
                assert masses[y]/sum(masses, F(0)) <= factor*maxima[y]
                labels += 1
            cases += 1
        a.check()
    return dict(conditional_recipe_cases=cases, exact_roundoff_and_dominating_probability_checks=labels,
                grid_bits=[0, 16, 32], features=[1, 2, 3, 8], subnormal_positive_base_checked=True,
                maximum_log_loss_allowance_nats=bounds_display(largest_factor), device_claim=False)


def actual_fixture():
    # This factorization reads the same model factory as the running resource
    # fixture. Opening any corpus here would violate the audit's declared scope.
    with patch.object(Path, 'open', side_effect=AssertionError('no corpus or file access in model factory')):
        d, origin = text_model_fixture()
    prior = subprocess.check_output(['git', 'show', 'a95375f:scripts/audit_token_reference_host.py'], cwd=ROOT, text=True)
    old = next(node for node in ast.parse(prior).body if type(node) is ast.FunctionDef and node.name == 'text_fixture')
    boundary = next(i for i, node in enumerate(old.body) if type(node) is ast.With)
    old.body = old.body[:boundary]+[ast.Return(value=ast.Tuple(elts=[ast.Name(id='definition', ctx=ast.Load()),
                                                                  ast.Name(id='origin', ctx=ast.Load())], ctx=ast.Load()))]
    namespace = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[old], type_ignores=[])), 'prior-model-prefix', 'exec'), namespace)
    old_d, old_origin = namespace['text_fixture']()
    assert (old_d, old_origin) == (d, origin)
    V, L, D, K = d.sources.vocabulary, d.sources.context, d.width, d.output.features
    assert (V, L, D, K, d.slots, d.slot_count) == (50257, 512, 4, 8, 4, 603092)
    assert d.nodes[:D] == tuple(Sum('f', tuple(Term(l*D+k, k) for l in range(L))) for k in range(D))
    assert d.nodes[D:] == tuple(Product('f', L*D+k, (k+1) % D) for k in range(D))
    columns = tuple(map(int, origin.W.sum(axis=0, dtype='int64')))
    maximum = tuple(max((F(1, V),)+tuple(F(int(w), total) for w, total in zip(row, columns))) for row in origin.W)
    capacity = sum(maximum, F(0))
    assert 1 <= capacity <= K+1
    family = TokenAtomFamily(V, L)
    pattern = TokenInitializer(family, D, d.output, tuple(map(int, origin.E.flat)), tuple(map(int, origin.C)),
                               tuple(map(int, origin.W.flat)), 1 << 24)
    machine, program = TokenReferenceMachine(pattern), TokenProgram(d)
    rules = SemanticRules(family, ('f',), (('f', 'f', 'f'),), 'f', d.output.base)
    state = TokenState(origin)
    def predict(past, position=L):
        return machine.predict(program, rules, state, TokenValues(TokenContext(family, position, tuple(past))), bit_limit=32768)
    first = tuple(i % 7 for i in range(L))
    older = list(first)
    older[1], older[-1] = older[-1], older[1]
    a, b = predict(first), predict(older)
    assert a.window != b.window and a.values[:L*D] != b.values[:L*D]
    assert a.values[L*D:] == b.values[L*D:] and a.probabilities == b.probabilities
    latest = list(first)
    latest[0], latest[1] = latest[1], latest[0]
    c = predict(latest)
    assert a.values[L*D:L*D+D] == c.values[L*D:L*D+D]
    assert a.values[L*D+D:] != c.values[L*D+D:]
    assert tuple(a.probabilities[y] for y in range(7)) != tuple(c.probabilities[y] for y in range(7))
    future_a, future_b = predict((2,)+first[:-1], L+1), predict((2,)+tuple(older[:-1]), L+1)
    assert tuple(future_a.probabilities[y] for y in range(7)) != tuple(future_b.probabilities[y] for y in range(7))
    return dict(vocabulary=V, context=L, features=K, master_coordinates=d.slot_count,
        initialized_column_dominance_sum=str(capacity), initialized_log_capacity_nats=bounds_display(capacity),
        every_frozen_native_head_log_capacity_upper_nats=bounds_display(F(K+1)),
        latest_token_is_distinguished=True, older_context_permutation_is_invisible_at_current_prediction=True,
        equal_current_predictions_do_not_authorize_history_erasure=True,
        complete_model_equals_prior_factory_prefix=True,
        corpus_bytes_read=0, trained_model_or_score=False)


def frozen_premise():
    """A legal adaptive U disproves applying one frozen-head floor to a run."""
    spec = readout.Spec((F(1),)*3, 1, 16, F(16), 1)
    state = readout.initialize(spec, (0,))
    accumulator, n = (0, 0), 0
    for y in (0, 1, 2):
        for _ in range(256):
            prediction = state.predict((F(1),))
            loss = log_enclosure(1/prediction.probability(y), terms=12, bit_limit=32768)
            accumulator = add_loss(accumulator, loss, fractional_bits=40, bit_limit=32768)
            state, _ = state.observe(prediction, y)
            state = state.commit()
            n += 1
    mean = tuple(F(x, n*(1 << 40)) for x in accumulator)
    frozen_floor = log_enclosure(F(3, 2), terms=12, bit_limit=32768)
    assert mean[1] < frozen_floor.lower
    return dict(native_projected_sgd_events=n, features=1, update_unit=1, eta='16', grid_bits=16,
                prequential_loss_enclosure_nats=list(map(str, mean)),
                invalid_whole_run_frozen_floor_nats=bounds_display(F(3, 2)),
                fixed_head_premise_is_necessary=True, corpus_or_runtime_claim=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = dict(status='PASS_EXACT_MODEL_SCOPE_CONTROL', scope='frozen positive heads and existing text resource fixture; no model selection, corpus score or Runtime authority')
    for part in (finite_heads, physical_heads, actual_fixture, frozen_premise):
        result[part.__name__] = part()
        print(part.__name__+': PASS', flush=True)
    assert 'torch' not in sys.modules
    if args.write:
        (ROOT/'evidence/minimal/FP_FROZEN_READOUT_CAPACITY.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
