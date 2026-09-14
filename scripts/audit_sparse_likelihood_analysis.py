"""Exact differential audit of sparse affine preparation and its verifier.

The comparison implementation is read from the committed dense analyzer.
Only passive mathematical functions are compared; no Runtime is patched.
"""
from dataclasses import replace
from fractions import Fraction as F
from pathlib import Path
from types import FunctionType
import ast
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'),
               str(ROOT/'experiments/joint_uncertainty')]
from fp_reference import likelihood_encoding as encoding
from fp_reference.learner import LearnerSpec, SIMPLEX_GRADIENT, initial_state, observe_event, commit_event
from fp_reference.native_search import GrammarLimits
from fp_reference.program import Program, Product, SemanticRules, Source, SourceSpec, Sum, Term
from fp_reference.semantics import ArithmeticUnresolved, evaluate
from audit_likelihood_encoding import vertex_bank, reverse_bank
from audit_reference_construction import rejects
from audit_reference_search import brute_grammar
from audit_simplex_learner import fixture

DENSE_SOURCE = '08fa7bcc85320aa699cffb25ea9f6e292b036f0b'


def dense_functions():
    source = subprocess.run(('git', 'show', DENSE_SOURCE+':src/reference_compiler/fp_reference/likelihood_encoding.py'),
        cwd=ROOT, capture_output=True, encoding='utf-8', check=True).stdout
    definition, = [node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name == '_affine_heads']
    namespace = dict(vars(encoding))
    exec(compile(ast.Module(body=[definition], type_ignores=[]), '<committed dense affine analyzer>', 'exec'), namespace)
    prepare = FunctionType(encoding.prepare_model.__code__, namespace)
    return namespace['_affine_heads'], prepare


def audit():
    dense, dense_prepare = dense_functions()
    rules = SemanticRules((SourceSpec('one', 'mass', 0, F(1)),), ('mass',),
        (('mass', 'mass', 'mass'),), 'mass', (F(1), F(1)))
    bounds = GrammarLimits(3, 1, 1, 3, 3)
    graphs = tuple(g for g in brute_grammar(rules, bounds) if g.slot_count == 3)
    checked = accepted = refused = dense_ops = sparse_ops = 0
    verified_banks = verifier_refusals = 0
    spec = LearnerSpec(1, F(1), optimizer_id=SIMPLEX_GRADIENT, simplex_slots=(1, 2))
    for graph in graphs:
        for fixed in (F(0), F(1), F(3, 2)):
            theta = (fixed, F(1, 2), F(1, 2))
            for point in ((F(0),), (F(1),), (F(3, 7),)):
                outcomes = []
                for function in (dense, encoding._affine_heads):
                    arithmetic = encoding._Arithmetic(32768, 10**9)
                    try:
                        result = function(graph, rules, theta, (1, 2), point, arithmetic)
                    except ArithmeticUnresolved:
                        result = None
                    outcomes.append((result, arithmetic.operations))
                assert outcomes[0][0] == outcomes[1][0]
                assert outcomes[1][1] <= outcomes[0][1]
                affine = outcomes[0][0]
                expected = None
                if affine is not None:
                    masses = tuple(tuple(row[0]+a for a in row[1:]) for row in affine)
                    normalizers = tuple(map(sum, zip(*masses)))
                    if len(set(normalizers)) == 1:
                        expected = tuple(tuple(m/z for m, z in zip(row, normalizers)) for row in masses)
                try:
                    verified = reverse_bank(graph, rules, theta, spec, (point,))
                except AssertionError:
                    verified = None
                assert verified == expected
                if verified is not None:
                    assert verified == vertex_bank(graph, rules, theta, spec, (point,))
                    verified_banks += 1
                else:
                    verifier_refusals += 1
                accepted += outcomes[0][0] is not None
                refused += outcomes[0][0] is None
                dense_ops += outcomes[0][1]
                sparse_ops += outcomes[1][1]
                checked += 1
    rows = []
    for n in range(2, 7):
        cfg, graph, online, _ = fixture(n)
        args = (graph, cfg.semantics, cfg.initializer_pattern, online.learner,
                cfg.source_domain, encoding.LikelihoodEncodingContract())
        limits = dict(bit_limit=32768, work_limit=encoding.preparation_work(
            graph, cfg.semantics, online.learner, cfg.source_domain, 32768))
        old, new = dense_prepare(*args, **limits), encoding.prepare_model(*args, **limits)
        assert replace(old, preparation_operations=0) == replace(new, preparation_operations=0)
        assert new.preparation_operations <= old.preparation_operations
        rows.append({'n': n, 'rank': new.rank, 'dense_operations': old.preparation_operations,
                     'sparse_operations': new.preparation_operations,
                     'prepaid_work_unchanged': limits['work_limit']})

    # All simplex-vertex forecasts can agree while the actual native U differs.
    # The new independent verifier must prove degree, not only fit vertices.
    affine = Program((Source('one'), Sum('mass', (Term(0, 1),)*8), Sum('mass', (Term(0, 2),)*8)), 3, (1, 2))
    nonlinear = Program((Source('one'), Sum('mass', (Term(0, 1),)), Product('mass', 1, 1),
        Sum('mass', (Term(0, 2),)), Product('mass', 3, 3),
        Sum('mass', (Term(2, 0),)*8), Sum('mass', (Term(4, 0),)*8)), 3, (5, 6))
    theta = (F(1), F(1, 2), F(1, 2))
    spec = LearnerSpec(1, F(1), optimizer_id=SIMPLEX_GRADIENT, simplex_slots=(1, 2))
    domain = ((F(1),),)
    assert vertex_bank(affine, rules, theta, spec, domain) == vertex_bank(nonlinear, rules, theta, spec, domain)
    assert reverse_bank(affine, rules, theta, spec, domain) == vertex_bank(affine, rules, theta, spec, domain)
    rejects(lambda: reverse_bank(nonlinear, rules, theta, spec, domain), AssertionError)
    prediction = evaluate(nonlinear, rules, theta, {'one': F(1)}, bit_limit=32768)
    state = initial_state(nonlinear, rules, theta, 0, spec=spec, bit_limit=32768)
    observed = observe_event(nonlinear, state, spec, prediction, 0, bit_limit=32768)
    assert prediction.probabilities == (F(1, 2), F(1, 2))
    assert observed.gradient_sum[1:] == (F(-4, 3), F(4, 3))
    rejects(lambda: commit_event(observed, spec, bit_limit=32768), ArithmeticUnresolved)
    assert 'torch' not in sys.modules
    return {'status': 'PASS', 'dense_source': DENSE_SOURCE,
        'complete_three_slot_graphs': len(graphs), 'coefficient_checks': checked,
        'affine_results': accepted, 'nonlinear_refusals': refused,
        'independent_bank_and_vertex_checks': verified_banks,
        'independent_degree_or_normalizer_refusals': verifier_refusals,
        'dense_scalar_operations': dense_ops, 'sparse_scalar_operations': sparse_ops,
        'prepared_model_comparisons': rows,
        'vertex_alias': {'same_vertex_probabilities': True, 'same_initial_probabilities': True,
            'nonlinear_raw_unit_weights': ['7/6', '-1/6'], 'degree_verifier_refuses': True},
        'scope': 'exact mathematical differential and certificate audit; no host/runtime or timing claim'}


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
