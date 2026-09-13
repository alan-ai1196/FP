"""RN-4 data, exact adaptive posterior and bounded descriptive score summaries."""
from fractions import Fraction as F
from itertools import product
from math import fsum, log
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'experiments/relation_noise'))
from model import context, counts_from_training, unseen_pairs
from model import data as old_data

RATES = ('1/8', '4')
GRID = 48


def diagnostic_cases():
    return ((8, 'disconnected-a', 0), (8, 'disconnected-b', 0))


def new_cases():
    return tuple((n, 'iid-c'+str(c), seed) for c, seeds in ((2, (12, 13)), (4, (14, 15)))
                 for n in (8, 16) for seed in seeds)


def tasks():
    return tuple((kind, case, rate) for case in diagnostic_cases()+new_cases()
                 for kind, rate in (('FP', '1/8'), ('FP', '4'), ('posterior', 'none')))


def support(case):
    assert case in diagnostic_cases()+new_cases()
    n, law, seed = case
    c = 2 if law.startswith('disconnected') else int(law.removeprefix('iid-c'))
    return tuple((i, i+1) for i in range(n-1) if (i+1) % (n//c))


def data(case):
    if case in diagnostic_cases():
        result = old_data(case)
        assert result[1] == support(case)
        return result
    n, law, seed = case
    edges = support(case)
    rng = random.Random(2026091300+100*n+seed)
    hidden = tuple(rng.randrange(2) for _ in range(n))
    noise = random.Random(2026091400+100*n+seed)
    train = tuple((i, j, (hidden[i]^hidden[j]) ^ int(noise.randrange(10) == 0))
                  for i, j in edges for _ in range(10))
    pairs = list(product(range(n), repeat=2))
    random.Random(2026091600+100*n+seed).shuffle(pairs)
    noise = random.Random(2026091500+100*n+seed)
    evaluation = tuple((i, j, (hidden[i]^hidden[j]) ^ int(noise.randrange(10) == 0)) for i, j in pairs)
    return hidden, edges, train, evaluation


def score(predictions, raw, hidden, pairs):
    """Exact per-query Brier enclosed on a fixed grid; no growing global LCM."""
    losses, raw_losses, gaps = [], [], []
    low = high = errors = 0
    maximum_bits = 0
    for i, j in pairs:
        truth = hidden[i]^hidden[j]
        q = (F(1, 10), F(9, 10)) if truth else (F(9, 10), F(1, 10))
        p = predictions[i, j]
        assert min(p) > 0 and sum(p) == 1
        losses.append(-fsum(float(a)*log(float(b)) for a, b in zip(q, p)))
        if raw is not None:
            raw_losses.append(-fsum(float(a)*log(float(b)) for a, b in zip(q, raw[i, j])))
        loss = sum(q[y]*sum((p[k]-int(y == k))**2 for k in (0, 1)) for y in (0, 1))
        maximum_bits = max(maximum_bits, loss.numerator.bit_length(), loss.denominator.bit_length())
        assert maximum_bits <= 32768
        scaled = loss*(1 << GRID)
        floor, remainder = divmod(scaled.numerator, scaled.denominator)
        low += floor; high += floor+bool(remainder)
        gaps.append(float(abs(p[truth]-F(9, 10))))
        errors += 1 if p[0] == p[1] else 2*int((p[1] > p[0]) != bool(truth))
    count = len(pairs)
    assert count
    interval = (F(low, count*(1 << GRID)), F(high, count*(1 << GRID)))
    assert interval[1]-interval[0] <= F(1, 1 << GRID)
    return {'contexts': count, 'expected_CE_binary64': fsum(losses)/count,
        'raw_division_expected_CE_binary64': None if raw is None else fsum(raw_losses)/count,
        'expected_Brier_exact_enclosure': list(map(str, interval)), 'Brier_grid_bits': GRID,
        'maximum_per_query_Brier_integer_bits': maximum_bits,
        'mean_true_probability_gap_binary64': fsum(gaps)/count,
        'latent_relation_error_with_half_ties': str(F(errors, 2*count))}


class AdaptivePosterior:
    """Positive likelihood weights over every assignment, including global flips."""
    def __init__(self, n, counts, law):
        self.n = n
        self.counts = tuple(counts)
        self.weights = []
        self.pending = None
        self.labels = sum(a+b for _, _, a, b in counts)
        self.work = 0
        for mask in range(1 << n):
            correct, possible = 0, True
            for i, j, a, b in counts:
                parity = ((mask >> i) ^ (mask >> j)) & 1
                correct += b if parity else a
                if not law.startswith('iid'):
                    assert sorted((a, b)) == [1, 9]
                    possible &= parity == int(b > a)
                self.work += 1
            self.weights.append(9**correct if law.startswith('iid') else int(possible))
        assert sum(self.weights) > 0
        self.maximum_weight_bits = max(w.bit_length() for w in self.weights)
        self.maximum_probability_bits = 0
        self.maximum_retained_payload_bytes = 0
        self.measure()

    def measure(self):
        # Direct integer payload, not Python heap, job commit or a bit-time
        # claim. The independently completed Windows job covers the process.
        extent = sum(max(1, (w.bit_length()+7)//8) for w in self.weights)
        self.maximum_retained_payload_bytes = max(self.maximum_retained_payload_bytes, extent)
        assert self.maximum_weight_bits <= self.n+4*self.labels+4 <= 32768
        assert self.work <= 10**13 and extent <= 1 << 30

    def predict(self, i, j):
        assert self.pending is None and 0 <= i < self.n and 0 <= j < self.n
        parity = tuple(((mask >> i) ^ (mask >> j)) & 1 for mask in range(1 << self.n))
        total = sum(self.weights)
        ones = sum(w for w, value in zip(self.weights, parity) if value)
        probability = F(total+8*ones, 10*total)
        result = (1-probability, probability)
        assert min(result) >= F(1, 10)
        self.maximum_probability_bits = max(self.maximum_probability_bits,
            *(v.numerator.bit_length() for v in result), *(v.denominator.bit_length() for v in result))
        assert self.maximum_probability_bits <= self.n+4*self.labels+8 <= 32768
        self.pending = parity
        self.work += 2*len(self.weights)
        return result

    def observe(self, label):
        assert self.pending is not None and label in (0, 1)
        # The common factor1/10 cancels from every later normalized posterior;
        # only parity likelihood weights are represented by this baseline.
        self.weights = [w*(9 if parity == label else 1) for w, parity in zip(self.weights, self.pending)]
        self.maximum_weight_bits = max(self.maximum_weight_bits, max(w.bit_length() for w in self.weights))
        self.work += len(self.weights)
        self.labels += 1
        self.pending = None
        self.measure()


def exact_audit():
    # Recompute each full joint likelihood from scratch after every history;
    # the incremental posterior neither supplies nor checks this oracle.
    checked = 0
    for n, counts, law in ((3, ((0, 1, 2, 1),), 'iid'),
                          (4, ((0, 1, 9, 1), (2, 3, 1, 9)), 'conditioned')):
        queries = ((0, n-1), (1, n-1), (0, 1))
        for labels in product((0, 1), repeat=len(queries)):
            learner = AdaptivePosterior(n, counts, law)
            past = []
            for pair, label in zip(queries, labels):
                denominator = numerator = F(0)
                for h in product((0, 1), repeat=n):
                    w = F(1)
                    for i, j, a, b in counts:
                        matches = b if h[i]^h[j] else a
                        w *= F(9, 10)**matches*F(1, 10)**(a+b-matches) if law == 'iid' else int(matches == 9)
                    for i, j, y in past:
                        w *= F(9, 10) if (h[i]^h[j]) == y else F(1, 10)
                    denominator += w
                    numerator += w*(F(9, 10) if h[pair[0]]^h[pair[1]] else F(1, 10))
                actual = learner.predict(*pair)
                assert actual == (1-numerator/denominator, numerator/denominator)
                learner.observe(label)
                past.append((*pair, label))
                checked += 1
    assert checked == 48 and 'torch' not in sys.modules
    return {'independent_full_joint_conditional_forecasts': checked,
            'cycles_and_conditioned_initial_zeros_retained': True}
