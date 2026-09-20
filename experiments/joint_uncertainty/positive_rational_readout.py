"""Passive native lowering of positive rational circuits to one final readout.

Each input is 1+theta_i; slot0 remains fixed at1 and the complete source
domain is the single row one=1. No Runtime constructor or bridge is added.
"""
from fractions import Fraction as F
from dataclasses import replace
from itertools import product
from pathlib import Path
import argparse
import json
import math
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(Path(__file__).resolve().parent)]
from fp_reference.program import Product, Program, SemanticRules, Source, SourceSpec, Sum, Term
from fp_reference.semantics import ArithmeticUnresolved, evaluate
from fp_reference.learner import (SIMPLEX_GRADIENT, LearnerSpec, ReferenceLearnerState,
    initial_state, ce_gradient, observe_event, commit_event)
from fp_reference.profile import attach_boundary
from positive_pair_marginals import forward_fixed_gradient

BITS = 32768


class RationalCircuit:
    def __init__(self, variables):
        self.variables = variables
        self.nodes = []
        self.memo = {}
        self.one = self.emit(('one',))
        self.inputs = tuple(self.emit(('input', i)) for i in range(variables))

    def emit(self, node):
        if node not in self.memo:
            self.memo[node] = len(self.nodes)
            self.nodes.append(node)
        return self.memo[node]

    def op(self, tag, a, b):
        assert tag in ('add', 'mul', 'div')
        return self.emit((tag, a, b))

    def dual(self, theta, head):
        values, slopes = [], []
        for tag, *args in self.nodes:
            if tag == 'one':
                v, gradient = F(1), (F(0),)*self.variables
            elif tag == 'input':
                v = 1+theta[args[0]]
                gradient = tuple(F(i == args[0]) for i in range(self.variables))
            else:
                a, b = args
                u, w = values[a], values[b]
                ga, gb = slopes[a], slopes[b]
                if tag == 'add':
                    v, gradient = u+w, tuple(x+y for x, y in zip(ga, gb))
                elif tag == 'mul':
                    v, gradient = u*w, tuple(x*w+u*y for x, y in zip(ga, gb))
                else:
                    assert tag == 'div' and w > 0
                    v, gradient = u/w, tuple((x*w-u*y)/(w*w) for x, y in zip(ga, gb))
            values.append(v)
            slopes.append(gradient)
        return values[head], slopes[head]


def lower(circuit, head):
    rules = SemanticRules((SourceSpec('one', 'mass', 0, F(1)),), ('mass',),
                          (('mass', 'mass', 'mass'),), 'mass', (F(1), F(1)))
    nodes = [Source('one')]
    memo = {nodes[0]: 0}

    def emit(node):
        if node not in memo:
            memo[node] = len(nodes)
            nodes.append(node)
        return memo[node]

    def add_nodes(a, b):
        return emit(Sum('mass', (Term(a, 0), Term(b, 0))))

    def mul_nodes(a, b):
        return emit(Product('mass', a, b))

    zero = emit(Sum('mass', ()))
    one = (0, zero)

    # Each pair stores (P, P-1), both by positive syntax. The second entry
    # removes one known constant derivation; no subtraction is executed.
    def add(a, b):
        return add_nodes(a[0], b[0]), add_nodes(a[1], b[0])

    def mul(a, b):
        return mul_nodes(a[0], b[0]), add_nodes(mul_nodes(a[1], b[0]), b[1])

    fractions = []
    for tag, *args in circuit.nodes:
        if tag == 'one':
            ratio = one, one
        elif tag == 'input':
            leaf = emit(Sum('mass', (Term(0, args[0]+1),)))
            ratio = (add_nodes(0, leaf), leaf), one
        else:
            na, da = fractions[args[0]]
            nb, db = fractions[args[1]]
            if tag == 'add':
                ratio = add(mul(na, db), mul(nb, da)), mul(da, db)
            elif tag == 'mul':
                ratio = mul(na, nb), mul(da, db)
            else:
                assert tag == 'div'
                ratio = mul(na, db), mul(da, nb)
        fractions.append(ratio)
    numerator, denominator = fractions[head]
    graph = Program(tuple(nodes), circuit.variables+1, (numerator[1], denominator[1]))
    graph.validate(rules)
    return rules, graph


def spanning_tree_circuit(n):
    """Directed trees pointing toward root n-1; positive Schur elimination."""
    root = n-1
    edges = tuple((i, j) for i in range(root) for j in range(n) if i != j)
    circuit = RationalCircuit(len(edges))
    weights = {edge: value for edge, value in zip(edges, circuit.inputs)}
    remaining = list(range(n))
    result = circuit.one
    for v in range(n-1):
        others = [u for u in remaining if u != v]
        incident = [weights[v, u] for u in others]
        total = incident[0]
        for weight in incident[1:]:
            total = circuit.op('add', total, weight)
        result = circuit.op('mul', result, total)
        for i, j in product(others, repeat=2):
            if i == j or i == root:
                continue
            via = circuit.op('mul', weights[i, v], weights[v, j])
            via = circuit.op('div', via, total)
            weights[i, j] = circuit.op('add', weights[i, j], via)
        remaining.remove(v)
    return circuit, result, edges


def tree_oracle(n, theta):
    """Independent exact enumeration of all labelled trees by Pruefer words."""
    edges = tuple((i, j) for i in range(n-1) for j in range(n) if i != j)
    slots = {e: i for i, e in enumerate(edges)}
    total, gradient = F(0), [F(0)]*len(edges)
    for word in product(range(n), repeat=n-2):
        degree = [1]*n
        for v in word:
            degree[v] += 1
        tree = []
        for v in word:
            leaf = next(i for i in range(n) if degree[i] == 1)
            tree.append(tuple(sorted((leaf, v))))
            degree[leaf] -= 1
            degree[v] -= 1
        a, b = [i for i in range(n) if degree[i] == 1]
        tree.append((a, b))
        adjacency = [[] for _ in range(n)]
        for i, j in tree:
            adjacency[i].append(j)
            adjacency[j].append(i)
        parents = {n-1: n-1}
        pending = [n-1]
        while pending:
            v = pending.pop()
            for u in adjacency[v]:
                if u not in parents:
                    parents[u] = v
                    pending.append(u)
        directed = tuple((i, parents[i]) for i in range(n-1))
        value = math.prod(1+theta[slots[e]] for e in directed)
        total += value
        for e in directed:
            gradient[slots[e]] += value/(1+theta[slots[e]])
    return total, tuple(gradient)


def checked_prediction(circuit, head, rules, graph, theta, *, oracle=None):
    value, slopes = circuit.dual(theta, head)
    if oracle is not None:
        assert (value, slopes) == oracle
    full_theta = (F(1),)+tuple(theta)
    prediction = evaluate(graph, rules, full_theta, {'one': F(1)}, (), bit_limit=BITS)
    assert prediction.probabilities == (value/(1+value), 1/(1+value))
    assert min(prediction.masses) >= 1
    for y in (0, 1):
        selected = tuple(-g/(value*(1+value)) if y == 0 else g/(1+value) for g in slopes)
        gradient = ce_gradient(graph, full_theta, prediction, y, bit_limit=BITS)
        assert gradient[1:] == selected
        assert gradient[0] == forward_fixed_gradient(graph, rules, full_theta, {'one': F(1)}, y)
    return prediction


def selected_degree(graph):
    degree = []
    for node in graph.nodes:
        if type(node) is Source:
            d = 0
        elif type(node) is Sum:
            terms = [degree[t.parent]+int(t.slot != 0) for t in node.terms if degree[t.parent] is not None]
            d = max(terms) if terms else None
        else:
            a, b = degree[node.left], degree[node.right]
            d = None if a is None or b is None else a+b
        degree.append(d)
    return max(d for d in degree if d is not None)


def binary64_forward(rules, graph, theta):
    values = []
    weights = (1.0,)+tuple(map(float, theta))
    for index, node in enumerate(graph.nodes):
        if type(node) is Source:
            value = 1.0
        elif type(node) is Sum:
            value = sum(weights[t.slot]*values[t.parent] for t in node.terms)
        else:
            value = values[node.left]*values[node.right]
        if not math.isfinite(value):
            return {'status': 'UNRESOLVED', 'first_nonfinite_node': index}
        values.append(value)
    masses = tuple(float(b)+values[h] for b, h in zip(rules.base, graph.heads))
    total = sum(masses)
    if not math.isfinite(total):
        return {'status': 'UNRESOLVED', 'first_nonfinite_node': 'readout total'}
    return {'status': 'FINITE_FORWARD_ONLY', 'probability0': masses[0]/total}


def general_audit():
    rng = random.Random(20260921)
    checked = 0
    for _ in range(100):
        circuit = RationalCircuit(2)
        for _ in range(8):
            head = circuit.op(rng.choice(('add', 'mul', 'div')),
                              rng.randrange(len(circuit.nodes)), rng.randrange(len(circuit.nodes)))
        rules, graph = lower(circuit, head)
        for theta in ((F(0), F(0)), (F(1, 2), F(1, 2)), (F(1, 3), F(2, 3)), (F(2), F(3))):
            checked_prediction(circuit, head, rules, graph, theta)
            checked += 1
        assert len(graph.nodes) <= 2+2*circuit.variables+12*8
    return {'deterministic_seed': 20260921, 'circuits': 100,
            'rational_operations_per_generation': 8,
            'native_forecasts': checked, 'full_gradient_checks': 2*checked}


def small_tree_audit():
    checked = 0
    for n in range(2, 7):
        circuit, head, edges = spanning_tree_circuit(n)
        rules, graph = lower(circuit, head)
        d = len(edges)
        priors = [(F(0),)*d, (F(1, d),)*d,
                  tuple(F(i+1, d*(d+1)//2) for i in range(d)),
                  (F(1),)+(F(0),)*(d-1), (F(0),)*(d-1)+(F(1),)]
        for theta in priors:
            checked_prediction(circuit, head, rules, graph, theta, oracle=tree_oracle(n, theta))
            checked += 1
    return {'n_values': list(range(2, 7)), 'priors_per_n': 5,
            'native_forecasts_with_independent_tree_derivatives': checked,
            'full_gradient_checks': 2*checked}


def learner_audit():
    checked = profiles = 0
    for n in (2, 3, 4):
        circuit, head, edges = spanning_tree_circuit(n)
        rules, graph = lower(circuit, head)
        d = len(edges)
        spec = LearnerSpec(1, F(1), optimizer_id=SIMPLEX_GRADIENT,
                          simplex_slots=tuple(range(1, d+1)))
        theta = tuple(F(i+1, d*(d+1)//2) for i in range(d))
        initial = initial_state(graph, rules, (F(1),)+theta, 0, spec=spec, bit_limit=BITS)

        def step(state, target):
            nonlocal checked
            theta = state.theta[1:]
            value, slopes = tree_oracle(n, theta)
            prediction = checked_prediction(circuit, head, rules, graph, theta, oracle=(value, slopes))
            selected = tuple(-g/(value*(1+value)) if target == 0 else g/(1+value) for g in slopes)
            assert max(selected)-min(selected) < 1
            full = (forward_fixed_gradient(graph, rules, state.theta, {'one': F(1)}, target),)+selected
            observed = observe_event(graph, state, spec, prediction, target, bit_limit=BITS)
            assert observed == ReferenceLearnerState(state.theta, (), full, 1,
                                                     state.cursor+1, state.optimizer_steps)
            mean = sum(w*g for w, g in zip(theta, selected))
            updated = tuple(w*(1-g+mean) for w, g in zip(theta, selected))
            assert min(updated) > 0 and sum(updated) == 1
            committed = commit_event(observed, spec, bit_limit=BITS)
            assert committed == ReferenceLearnerState((F(1),)+updated, (), (F(0),)*(d+1),
                                                      0, state.cursor+1, state.optimizer_steps+1)
            checked += 1
            return committed

        frontier = [initial]
        for _ in range(2):
            frontier = [step(state, y) for state in frontier for y in (0, 1)]
        # Two one-event profile passes and a complete clock attachment.
        state = step(step(initial, 0), 0)
        attached = attach_boundary(state, 12, spec)
        assert attached == replace(state, cursor=12)
        step(attached, 1)
        profiles += 1
    return {'native_observe_commit_pairs': checked, 'complete_state_boundaries': 2*checked,
            'two_pass_profile_cases': profiles}


def degree_recurrence(n):
    denominator_degree = total = 0
    for k in range(n, 1, -1):
        total += 1+(k-1)*denominator_degree
        denominator_degree = 1+(k+2)*denominator_degree
    return total


def resource_audit():
    rows = []
    for n in (*range(2, 9), 10, 12, 16):
        circuit, head, edges = spanning_tree_circuit(n)
        rules, graph = lower(circuit, head)
        d = len(edges)
        theta = (F(1, d),)*d
        degree = selected_degree(graph)
        assert degree == degree_recurrence(n)
        row = {'n': n, 'rational_nodes': len(circuit.nodes), 'native': graph.counts(),
               'max_selected_degree': degree}
        if n <= 8:
            w = F(d+1, d)
            value = n**(n-2)*w**(n-1)
            # A root-directed edge occurs in 2/n of the labelled trees;
            # another directed edge occurs in 1/n, by labelled symmetry.
            slopes = tuple(F(2 if j == n-1 else 1, n)*n**(n-2)*w**(n-2) for i, j in edges)
            row['exact_probability_oracle'] = str(value/(1+value))
            try:
                prediction = checked_prediction(circuit, head, rules, graph, theta,
                                                oracle=(value, slopes))
                row.update(exact='PASS', maximum_operand_bits=max(max(v.numerator.bit_length(),
                           v.denominator.bit_length()) for v in prediction.values),
                           probability0=str(prediction.probabilities[0]))
            except ArithmeticUnresolved as exc:
                row.update(exact='UNRESOLVED', reason=str(exc))
            row['binary64'] = binary64_forward(rules, graph, theta)
            if row['binary64']['status'] == 'FINITE_FORWARD_ONLY':
                assert abs(F(row['binary64']['probability0'])-value/(1+value)) < F(1, 10**12)
        else:
            row['evaluation'] = 'NOT_RUN; syntax and degree only'
        rows.append(row)
    return {'reference_bit_limit': BITS, 'rows': rows,
            'binary64_is_passive_forward_only': True, 'GPU_or_Runtime_authority': False}


def domain_counterexample():
    circuit, head, _ = spanning_tree_circuit(3)
    rules, graph = lower(circuit, head)
    theta = (F(1),)+(F(1, 4),)*4
    valid = evaluate(graph, rules, theta, {'one': F(1)}, (), bit_limit=BITS)
    invalid = evaluate(graph, rules, theta, {'one': F(0)}, (), bit_limit=BITS)
    assert valid.probabilities != invalid.probabilities
    return {'source_range_does_not_prove_unit_domain': True,
            'valid_probability': str(valid.probabilities[0]),
            'zero_source_probability': str(invalid.probabilities[0]),
            'fixed_slot_gradient_is_retained': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = {'status': 'PASS_WITH_DECLARED_RESOURCE_REFUSALS',
              'scope': 'passive native positive rational readout compilation; no Runtime or AMP authority',
              'general_circuits': general_audit(), 'directed_tree_oracle': small_tree_audit(),
              'complete_learner': learner_audit(), 'resource_pressure': resource_audit(),
              'source_scope': domain_counterexample()}
    text = json.dumps(result, indent=2)+'\n'
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
