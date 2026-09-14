"""Exact information and continuation audit for fixed finite likelihood learners.

This is a small Fraction model check, not a Runtime solver or physical codec.
The native side uses the registered unit simplex learner, including its full
gradient and clocks. No posterior is supplied to an owned learner through it.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import combinations, product
from math import lcm, prod
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src/reference_compiler'))
from fp_reference.learner import (SIMPLEX_GRADIENT, LearnerSpec,
    ReferenceLearnerState, initial_state, observe_event, commit_event)
from fp_reference.program import Program, SemanticRules, Source, SourceSpec, Sum, Term
from fp_reference.semantics import Evaluation, evaluate


def normalize(values):
    total = sum(values, F(0))
    return tuple(v/total for v in values)


def rref(rows):
    a = [list(map(F, row)) for row in rows]
    pivots = []
    for col in range(len(a[0]) if a else 0):
        pivot = next((i for i in range(len(pivots), len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        p = len(pivots)
        a[p], a[pivot] = a[pivot], a[p]
        divisor = a[p][col]
        a[p] = [v/divisor for v in a[p]]
        for i in range(len(a)):
            if i != p:
                multiplier = a[i][col]
                a[i] = [v-multiplier*w for v, w in zip(a[i], a[p])]
        pivots.append(col)
        if len(pivots) == len(a):
            break
    return tuple(map(tuple, a)), tuple(pivots)


def rank(rows):
    return len(rref(rows)[1])


def valuations(value):
    """Trial division is sufficient only for this audit's small fixed bank."""
    assert type(value) is F and value > 0
    result = {}
    for number, sign in ((value.numerator, 1), (value.denominator, -1)):
        assert number <= 10**6, 'audit factor bank allowance; no general fast factorization claim'
        prime = 2
        while prime*prime <= number:
            while number % prime == 0:
                result[prime] = result.get(prime, 0)+sign
                number //= prime
            prime += 1
        if number > 1:
            result[number] = result.get(number, 0)+sign
    return {p: v for p, v in result.items() if v}


@dataclass(frozen=True)
class Model:
    table: tuple  # query, label, world; complete declared query alphabet
    prior: tuple

    def __post_init__(self):
        assert self.table and self.prior and all(type(v) is F and v > 0 for v in self.prior)
        assert sum(self.prior) == 1
        assert self.labels > 0
        for rows in self.table:
            assert len(rows) == self.labels
            assert all(len(row) == self.worlds and all(type(v) is F and v > 0 for v in row) for row in rows)
            assert all(sum(row[k] for row in rows) == 1 for k in range(self.worlds))

    @property
    def worlds(self): return len(self.prior)

    @property
    def labels(self): return len(self.table[0])

    @property
    def events(self): return tuple(product(range(len(self.table)), range(self.labels)))

    @property
    def factors(self): return tuple(self.table[x][y] for x, y in self.events)

    def step(self, weights, event):
        return normalize(tuple(w*v for w, v in zip(weights, self.table[event[0]][event[1]])))

    def history(self, history):
        w = self.prior
        for event in history:
            w = self.step(w, event)
        return w

    def forecast(self, weights, event):
        return sum((w*v for w, v in zip(weights, self.table[event[0]][event[1]])), F(0))


class Coordinates:
    def __init__(self, model):
        self.model = model
        factors = tuple(tuple(valuations(row[k]/row[0]) for k in range(1, model.worlds))
                        for row in model.factors)
        primes = sorted({p for row in factors for d in row for p in d})
        self.row_labels = tuple(product(range(1, model.worlds), primes))
        self.rows = tuple(tuple(f[k-1].get(p, 0) for f in factors) for k, p in self.row_labels)
        self.differences = tuple(tuple(v-row[0] for v in row) for row in self.rows)
        self.selected = rref(tuple(zip(*self.differences)))[1] if self.rows else ()
        self.basis = tuple(self.differences[i] for i in self.selected)
        self.rho = len(self.selected)
        pivots = rref(self.basis)[1]
        self.combinations = []
        for row in self.differences:
            equations = tuple(tuple(b[col] for b in self.basis)+(row[col],) for col in pivots)
            reduced, columns = rref(equations)
            assert columns == tuple(range(self.rho))
            coefficients = tuple(reduced[i][-1] for i in range(self.rho))
            assert all(sum(c*b[j] for c, b in zip(coefficients, self.basis)) == row[j]
                       for j in range(len(model.events)))
            self.combinations.append(coefficients)

    def key(self, counts):
        return tuple(sum(c*v for c, v in zip(counts, row)) for row in self.basis)

    def decode(self, time, key):
        assert type(time) is int and time >= 0 and len(key) == self.rho
        powers = tuple(time*row[0]+sum(c*v for c, v in zip(coefficients, key))
                       for row, coefficients in zip(self.rows, self.combinations))
        assert all(F(v).denominator == 1 for v in powers)
        ratios = [F(1)]*self.model.worlds
        for (k, prime), exponent in zip(self.row_labels, powers):
            ratios[k] *= F(prime)**int(exponent)
        return normalize(tuple(w*r for w, r in zip(self.model.prior, ratios)))


def native_graph(model):
    scale = lcm(*(v.denominator for row in model.factors for v in row))
    specs = tuple(SourceSpec(f'q:{x}', 'mass', 0, F(1)) for x in range(len(model.table)))
    rules = SemanticRules(specs, ('mass',), (('mass', 'mass', 'mass'),),
                          'mass', (F(1),)*model.labels)
    nodes = [Source(s.source_id) for s in specs]
    features = {}
    for k, y in product(range(model.worlds), range(model.labels)):
        terms = tuple(Term(x, 0) for x in range(len(specs))
                      for _ in range(int(scale*model.table[x][y][k])-1))
        features[k, y] = len(nodes)
        nodes.append(Sum('mass', terms))
    heads = []
    for y in range(model.labels):
        heads.append(len(nodes))
        nodes.append(Sum('mass', tuple(Term(features[k, y], k+1) for k in range(model.worlds))))
    graph = Program(tuple(nodes), model.worlds+1, tuple(heads))
    graph.validate(rules)
    learner = LearnerSpec(1, F(1), optimizer_id=SIMPLEX_GRADIENT,
                          simplex_slots=tuple(range(1, model.worlds+1)))
    return rules, graph, learner, scale


def cache_oracle(model, weights, query, scale):
    sources = tuple(F(x == query) for x in range(len(model.table)))
    features = tuple(scale*model.table[query][y][k]-1
                     for k, y in product(range(model.worlds), range(model.labels)))
    probabilities = tuple(model.forecast(weights, (query, y)) for y in range(model.labels))
    masses = tuple(scale*p for p in probabilities)
    excesses = tuple(m-1 for m in masses)
    return Evaluation(sources+features+excesses, excesses, masses, F(scale), probabilities, ())


def native_step(model, contract, state, event):
    rules, graph, learner, scale = contract
    x, y = event
    cache = evaluate(graph, rules, state.theta, {f'q:{i}': F(i == x) for i in range(len(model.table))}, (), bit_limit=32768)
    assert cache == cache_oracle(model, state.theta[1:], x, scale)
    observed = observe_event(graph, state, learner, cache, y, bit_limit=32768)
    mass = cache.masses[y]
    gradient = (1/mass-F(model.labels, scale),)+tuple(F(scale-model.labels, scale)-(scale*p-1)/mass
                                                             for p in model.table[x][y])
    assert observed == ReferenceLearnerState(state.theta, (), gradient, 1, state.cursor+1, state.optimizer_steps)
    committed = commit_event(observed, learner, bit_limit=32768)
    w = model.step(state.theta[1:], event)
    assert committed == ReferenceLearnerState((F(1),)+w, (), (F(0),)*(model.worlds+1), 0,
                                               state.cursor+1, state.optimizer_steps+1)
    return committed


def native_history(model, history):
    contract = native_graph(model)
    rules, graph, learner, _ = contract
    state = initial_state(graph, rules, (F(1),)+model.prior, 0, spec=learner, bit_limit=32768)
    for event in history:
        state = native_step(model, contract, state, event)
    return state


def bernoulli(rows, prior=None):
    table = tuple((tuple(map(F, row)), tuple(1-F(v) for v in row)) for row in rows)
    return Model(table, tuple(prior) if prior else (F(1, len(rows[0])),)*len(rows[0]))


def models():
    return {
        'uninformative': (bernoulli(((F(1, 3), F(1, 3)),)), 4, 0),
        'one_prime': (bernoulli(((F(9, 10), F(1, 10)), (F(1, 2),)*2)), 3, 1),
        'two_primes': (bernoulli(((F(2, 3), F(1, 3)), (F(3, 4), F(1, 4)), (F(1, 2),)*2)), 4, 2),
        'clock_changes_rank': (bernoulli(((F(1, 3), F(1, 2)),), (F(1, 3), F(2, 3))), 5, 1),
        'three_distinct_worlds': (bernoulli(((F(1, 4), F(1, 2), F(3, 4)), (F(1, 2),)*3)), 3, 2),
        'duplicated_world': (bernoulli(((F(2, 3), F(2, 3), F(1, 3)), (F(3, 4), F(3, 4), F(1, 4)),
                                      (F(1, 2),)*3), (F(1, 6), F(1, 3), F(1, 2))), 3, 2),
        'three_labels': (Model((( (F(1, 2), F(1, 3)), (F(1, 3), F(1, 2)), (F(1, 6), F(1, 6))),),
                               (F(1, 4), F(3, 4))), 3, 1),
    }


def native_audit():
    rows = []
    for name, (model, depth, expected_rank) in models().items():
        contract = native_graph(model)
        rules, graph, learner, _ = contract
        coordinates = Coordinates(model)
        assert coordinates.rho == expected_rank
        state = initial_state(graph, rules, (F(1),)+model.prior, 0, spec=learner, bit_limit=32768)
        levels = [(state, (0,)*len(model.events))]
        phases = 0
        for time in range(1, depth+1):
            following = []
            for before, counts in levels:
                for i, event in enumerate(model.events):
                    after = native_step(model, contract, before, event)
                    updated = tuple(c+(j == i) for j, c in enumerate(counts))
                    assert coordinates.decode(time, coordinates.key(updated)) == after.theta[1:]
                    following.append((after, updated))
                    phases += 1
            levels = following
        rows.append({'model': name, 'rho': coordinates.rho, 'raw_rank': rank(coordinates.rows),
                     'histories': phases+1, 'each_cache_observe_commit': phases, 'scale': contract[3]})
    return rows


def compositions(total, width):
    if width == 1:
        yield (total,)
    else:
        for first in range(total+1):
            for rest in compositions(total-first, width-1):
                yield (first,)+rest


def count_audit():
    result = []
    for name, (model, _, _) in models().items():
        coordinates = Coordinates(model)
        cardinalities = []
        histograms = 0
        for time in range(7):
            forward, reverse = {}, {}
            for counts in compositions(time, len(model.events)):
                # Independent product likelihood; no decoder or native gradient.
                w = normalize(tuple(model.prior[k]*prod(row[k]**c for row, c in zip(model.factors, counts))
                                    for k in range(model.worlds)))
                key = coordinates.key(counts)
                assert forward.setdefault(key, w) == w
                assert reverse.setdefault(w, key) == key
                assert coordinates.decode(time, key) == w
                histograms += 1
            number = len(forward)
            rho = coordinates.rho
            assert (time//rho+1)**rho <= number if rho else number == 1
            assert number <= prod(time*(max(row)-min(row))+1 for row in coordinates.basis)
            if name in ('two_primes', 'duplicated_world'):
                assert number == 2*time*time+2*time+1
            if name == 'clock_changes_rank':
                assert number == time+1 and rank(coordinates.rows) == 2
            cardinalities.append(number)
        result.append({'model': name, 'histograms': histograms, 'fixed_cut_classes_T0_to_6': cardinalities})
    for n in (2, 3, 4, 5):
        worlds = tuple((0,)+z for z in product((0, 1), repeat=n-1))
        rows = tuple(tuple(F(9 if z[i] == z[j] else 1, 10) for z in worlds)
                     for i, j in product(range(n), repeat=2))
        assert Coordinates(bernoulli(rows)).rho == n*(n-1)//2
    return {'cases': result, 'relation_rank_recovered_n': [2, 3, 4, 5]}


def observability_audit():
    rows = []
    for name, (model, _, _) in models().items():
        signatures = tuple(tuple(row[k] for row in model.factors) for k in range(model.worlds))
        groups = tuple(dict.fromkeys(signatures))
        # Explicit interpolation polynomial values, without exponential expansion.
        for g, signature in enumerate(groups):
            values = [F(1)]*len(groups)
            for h, other in enumerate(groups):
                if g == h:
                    continue
                event = next(i for i in range(len(signature)) if signature[i] != other[i])
                values = [v*(at[event]-other[event])/(signature[event]-other[event])
                          for v, at in zip(values, groups)]
            assert values == [F(i == g) for i in range(len(groups))]
        word_rows = tuple(tuple(prod(model.factors[i][k] for i in word) for k in range(model.worlds))
                          for length in range(len(groups)) for word in product(range(len(model.events)), repeat=length))
        assert rank(word_rows) == len(groups)
        rows.append({'model': name, 'distinct_experts': len(groups), 'word_rows': len(word_rows),
                     'maximum_word_length': len(groups)-1})
    model = models()['three_distinct_worlds'][0]
    a, b = model.history(((0, 0), (0, 1))), model.history(((1, 0),)*2)
    assert a != b
    assert all(model.forecast(a, event) == model.forecast(b, event) for event in model.events)
    after_a, after_b = model.step(a, (0, 0)), model.step(b, (0, 0))
    gap = abs(model.forecast(after_a, (0, 0))-model.forecast(after_b, (0, 0)))
    assert gap == F(1, 120)
    return {'cases': rows, 'same_current_forecasts_after_two_actual_histories_next_gap': str(gap)}


def ratio_diameter(p, q):
    ratios = tuple(a/b for a, b in zip(p, q))
    return max(ratios)/min(ratios)


def projective_audit():
    checks = 0
    for worlds in (2, 3):
        probabilities = tuple(normalize(tuple(F(c+1) for c in counts))
                              for total in range(4) for counts in compositions(total, worlds))
        tilts = tuple(tuple(F(v+1) for v in values) for values in product(range(3), repeat=worlds))
        for p, q in combinations(probabilities, 2):
            radius = ratio_diameter(p, q)
            for tilt in tilts:
                a, b = (normalize(tuple(w*v for w, v in zip(s, tilt))) for s in (p, q))
                assert ratio_diameter(a, b) == radius
                tv = sum(abs(v-w) for v, w in zip(a, b))/2
                # Equivalent to TV <= tanh(log(radius)/4), using only rationals.
                assert ((1+tv)/(1-tv))**2 <= radius
                checks += 1
    return {'positive_tilt_isometries_and_sharp_TV_bounds': checks}


def approximate_boundary():
    model = models()['two_primes'][0]
    midpoint_checks = 0
    for a in range(-6, 7):
        for b in range(-6, 7):
            if abs(a)+abs(b) > 6:
                continue
            w = normalize((F(2)**a*F(3)**b, F(1)))
            for event, row in zip(model.events, model.factors):
                midpoint = sum(row)/2
                assert abs(model.forecast(w, event)-midpoint) <= F(1, 4)
                midpoint_checks += 1
    h = ((0, 0),)*19
    g = ((1, 0),)*12+((2, 0),)*7
    assert len(h) == len(g) == 19
    a, b = model.history(h), model.history(g)
    ratio = ratio_diameter(a, b)
    assert ratio == F(531441, 524288)
    upper = (ratio-1)/8
    assert upper == F(7153, 4194304) and upper < F(1, 500)
    middle_odds = (a[0]/a[1]+b[0]/b[1])/2
    middle = normalize((middle_odds, F(1)))
    assert max(ratio_diameter(a, middle), ratio_diameter(b, middle)) == (ratio+1)/2
    representative_bound = (ratio-1)/16
    assert representative_bound == F(7153, 8388608) and representative_bound < F(1, 1000)
    # Pure learner encoding must identify commuting histories at the same clock.
    assert native_history(model, h+g) == native_history(model, g+h)
    inverse = tuple((x, 1-y) for x, y in h+g)
    left, right = native_history(model, h+h+inverse), native_history(model, g+g+inverse)
    assert left.cursor == right.cursor == left.optimizer_steps == right.optimizer_steps == 76
    assert left.theta[1]/left.theta[2] == 1/ratio
    assert right.theta[1]/right.theta[2] == ratio
    gap = abs(model.forecast(left.theta[1:], (1, 0))-model.forecast(right.theta[1:], (1, 0)))
    assert gap == F(7153, 2111458) and gap > F(1, 500)
    close = []
    for p, q in ((19, 12), (84, 53), (1054, 665)):
        first, second = 2**p, 3**q
        r = F(max(first, second), min(first, second))
        bound = (r-1)/8
        digits = max(i for i in range(15) if bound < F(1, 10**i))
        close.append({'A_labels': p, 'B_labels': q, 'identity_padding': abs(p-q),
                      'every_future_forecast_gap_lt': f'1/{10**digits}'})
    return {'same_cut': 19, 'odds_ratio': str(ratio), 'all_future_gap_strict_upper': str(upper),
            'one_positive_rational_representative_each_future_error_lt': str(representative_bound),
            'forced_pure_encoding_collision_cut': 76, 'forced_collision_forecast_gap': str(gap),
            'per_run_error_forbidden_by_forced_collision': '1/1000', 'closer_prime_powers': close,
            'constant_midpoint_forecast_checks_at_error_1_over_4': midpoint_checks,
            'scope': 'pure deterministic reference-state encoding with exact transition commutation; not every history-dependent implementation'}


if __name__ == '__main__':
    report = {'native': native_audit(), 'counting': count_audit(), 'observability': observability_audit(),
              'projective': projective_audit(), 'approximation_boundary': approximate_boundary(),
              'scope': 'exact finite-model theorem audit; no Runtime, AMP, installation or total-resource certificate'}
    assert 'torch' not in sys.modules
    print(json.dumps(report, indent=2))
