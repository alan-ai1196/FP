"""Declared unknown-noise tapes and a full joint posterior from unsigned data.

The control uses a vertex-prefix recurrence, not the Runtime count decoder,
bucket geometry, excess partitions, or a separately normalized rate mixture.
It never supplies values to the owned physical path.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import combinations
from math import fsum, lcm, log
import random

RATES, PRIOR = (F(1, 10), F(1, 4)), (F(1, 2), F(1, 2))
CASES = tuple((64, str(rate), seed) for rate in RATES for seed in (0, 1))
GRID = 40


def data(case):
    assert case in CASES
    n, rate, seed = case
    rate = F(rate)
    hidden_rng = random.Random(202609230100+100*n+seed)
    hidden = tuple(hidden_rng.randrange(2) for _ in range(n))
    edges = tuple((i, i+1) for i in range(n-1))
    evaluation = [(i, j) for i in range(n) for j in range(n) if 0 < abs(i-j) <= 2]
    random.Random(202609230200+100*n+seed).shuffle(evaluation)
    noise = random.Random(202609230300+100*n+seed)
    events = tuple((i, j, hidden[i]^hidden[j]^int(noise.randrange(20) < 20*rate))
                   for i, j in edges+edges+tuple(evaluation))
    assert len(events) == 376 and len(evaluation) == 250
    return hidden, events[:126], events[126:]


@dataclass(frozen=True)
class Forecast:
    joint: tuple
    conditional: tuple
    rate_posterior: tuple
    rate_parts: tuple


class JointControl:
    """Full finite-rate/world Bayes control, retaining per-edge unsigned counts."""

    def __init__(self, n, rates=RATES, prior=PRIOR):
        assert type(n) is int and n >= 2
        assert len(rates) == len(prior) and min(prior) > 0 and sum(prior) == 1
        assert len(set(rates)) == len(rates) and all(0 < r < F(1, 2) for r in rates)
        self.n, self.rates, self.prior = n, rates, prior
        self.scale = lcm(*(r.denominator for r in rates))
        self.prior_scale = lcm(*(p.denominator for p in prior))
        self.edges = tuple(combinations(range(n), 2))
        self.labels = {e: [0, 0] for e in self.edges}
        self.diagonal = [0, 0]
        self.steps, self.pending = 0, None
        self.predictions = self.transitions = 0
        self.maximum_integer_bits = 1

    def coordinates(self):
        return tuple(self.labels[e][0]-self.labels[e][1] for e in self.edges), self.diagonal[0]-self.diagonal[1], self.steps

    def forecast(self, pair):
        assert type(pair) is tuple and len(pair) == 2 and all(type(v) is int and 0 <= v < self.n for v in pair)
        assert all(not sum(counts) for (i, j), counts in self.labels.items() if j-i > 2)
        all_parts = []
        for rate, prior in zip(self.rates, self.prior):
            a, b = int(self.scale*rate), int(self.scale*(1-rate))
            weights = {(i, j): (b**c0*a**c1, a**c0*b**c1)
                       for (i, j), (c0, c1) in self.labels.items() if j-i <= 2}
            rows = {(0, 0): int(prior*self.prior_scale)*b**self.diagonal[0]*a**self.diagonal[1]}
            for vertex in range(1, self.n):
                following = {}
                for (tail, parity), value in rows.items():
                    for bit in (0, 1):
                        contribution = value
                        for earlier in range(max(0, vertex-2), vertex):
                            earlier_bit = (tail >> (vertex-1-earlier)) & 1
                            contribution *= weights[earlier, vertex][earlier_bit^bit]
                        next_parity = parity ^ (bit if pair[0] != pair[1] and vertex in pair else 0)
                        key = ((tail << 1 | bit) & 3, next_parity)
                        following[key] = following.get(key, 0)+contribution
                        self.maximum_integer_bits = max(self.maximum_integer_bits, following[key].bit_length())
                        self.transitions += 1
                rows = following
                assert len(rows) <= 8
            all_parts.append(tuple(sum(w for (_, parity), w in rows.items() if parity == y) for y in (0, 1)))
        total = sum(sum(parts) for parts in all_parts)
        conditional = tuple(tuple(F(int(self.scale*(1-rate))*parts[y]+int(self.scale*rate)*parts[1-y],
                                      self.scale*sum(parts)) for y in (0, 1))
                            for rate, parts in zip(self.rates, all_parts))
        posterior = tuple(F(sum(parts), total) for parts in all_parts)
        joint = tuple(sum(weight*p[y] for weight, p in zip(posterior, conditional)) for y in (0, 1))
        return Forecast(joint, conditional, posterior, tuple(all_parts))

    def predict(self, i, j):
        assert self.pending is None
        answer = self.forecast((i, j))
        self.pending = (i, j)
        self.predictions += 1
        return answer

    def observe(self, target):
        assert self.pending is not None and type(target) is int and target in (0, 1)
        i, j = self.pending
        assert abs(i-j) <= 2
        if i == j:
            self.diagonal[target] += 1
        else:
            self.labels[tuple(sorted((i, j)))][target] += 1
        self.steps += 1
        self.pending = None

    def statistics(self):
        return dict(predictions=self.predictions, vertex_transitions=self.transitions,
                    maximum_integer_bits=self.maximum_integer_bits, world_enumerations=0)


def enclosure(value):
    quotient, remainder = divmod(value.numerator*(1 << GRID), value.denominator)
    return [quotient, quotient+bool(remainder)]


def score(predictions, hidden, rate, pairs):
    """Conditional expected scores; CE binary64, Brier exact per-query enclosures."""
    losses, lows, highs, errors = [], 0, 0, 0
    for pair in pairs:
        truth = hidden[pair[0]]^hidden[pair[1]]
        actual = (rate, 1-rate) if truth else (1-rate, rate)
        p = predictions[pair]
        assert min(p) > 0 and sum(p) == 1
        losses.append(-fsum(float(a)*log(float(v)) for a, v in zip(actual, p)))
        brier = sum(actual[y]*sum((p[k]-int(y == k))**2 for k in (0, 1)) for y in (0, 1))
        assert max(brier.numerator.bit_length(), brier.denominator.bit_length()) <= 32768
        lower, upper = enclosure(brier)
        lows += lower
        highs += upper
        errors += 1 if p[0] == p[1] else 2*int((p[1] > p[0]) != bool(truth))
    count = len(pairs)
    return {'contexts': count, 'expected_CE_binary64': fsum(losses)/count,
        'expected_Brier_exact_enclosure': [str(F(v, count*(1 << GRID))) for v in (lows, highs)],
        'latent_relation_error_with_half_ties': str(F(errors, 2*count))}


def replay(case):
    """Exact full control and oracle-rate forecasts; never invokes production."""
    hidden, train, evaluation = data(case)
    control = JointControl(case[0])
    joint, known, checkpoints = {}, {}, {}
    truth_index = RATES.index(F(case[1]))
    for k, (i, j, y) in enumerate(train+evaluation):
        forecast = control.predict(i, j)
        if k <= 63:
            assert forecast.rate_posterior == PRIOR
        if k < 63:
            assert forecast.joint == (F(1, 2),)*2
        if k in (0, 63, 126):
            checkpoints[str(k)] = [enclosure(v) for v in forecast.rate_posterior]
        if k >= len(train):
            joint[i, j], known[i, j] = forecast.joint, forecast.conditional[truth_index]
        control.observe(y)
    checkpoints['376'] = [enclosure(v) for v in control.forecast((0, 0)).rate_posterior]
    return hidden, evaluation, joint, known, checkpoints, control.statistics()
