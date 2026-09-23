"""Fixed-width causal data and an independent exact joint-posterior control.

The Runtime keeps its full pair interface and all native count coordinates.
The width restriction belongs to this experiment's covariate distribution,
not to a new learner or to a projection of its persistent state.
"""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/adaptive_uncertainty')]
from fp_reference.core import ContractError
from fp_reference.indexed_count import CountState, query
from fp_reference.indexed_relation import IndexedRelation
from adaptive_model import score

CASES = ((64, 'iid-band2', 0), (64, 'iid-band2', 1))


def data(case):
    if case not in CASES:
        raise ContractError('undeclared bounded-width model case')
    n, _, seed = case
    edges = tuple((i, i+1) for i in range(n-1))
    rng = random.Random(2026091300+100*n+seed)
    hidden = tuple(rng.randrange(2) for _ in range(n))
    noise = random.Random(2026091400+100*n+seed)
    train = tuple((i, j, (hidden[i]^hidden[j]) ^ int(noise.randrange(10) == 0))
                  for i, j in edges for _ in range(2))
    pairs = [(i, j) for i in range(n) for j in range(n) if 0 < abs(i-j) <= 2]
    random.Random(2026091600+100*n+seed).shuffle(pairs)
    noise = random.Random(2026091500+100*n+seed)
    evaluation = tuple((i, j, (hidden[i]^hidden[j]) ^ int(noise.randrange(10) == 0)) for i, j in pairs)
    assert len(train) == 126 and len(evaluation) == 250
    return hidden, edges, train, evaluation


def scoring_groups(case):
    n = case[0]
    return (('unseen', tuple((i, j) for i in range(n) for j in range(n) if abs(i-j) == 2)),
            ('evaluation_domain', tuple((i, j) for i in range(n) for j in range(n) if 0 < abs(i-j) <= 2)))


def bounds(n):
    IndexedRelation(n)
    return {'largest_join_cells': 32, 'peak_live_integer_cells': 12*n+64,
            'positive_operations': 212*n-195}


def exact_parts(state, pair):
    """Vertex-prefix sum-product over (last two bits, query parity).

    This uses native base9 directly, no packed coefficient digits, bucket
    elimination, runtime plan or reference forecast. All count positions
    are inspected before using the stated width-two information model.
    """
    if type(state) is not CountState or state.pending is not None:
        raise ContractError('complete committed count state required by the control')
    state.__post_init__()
    query(state.n, *pair)
    counts = dict(zip(combinations(range(state.n), 2), state.counts))
    if any(d and j-i > 2 for (i, j), d in counts.items()):
        raise ContractError('control received a nonzero count outside its declared interaction width')
    rows = {(0, 0): 1}
    work, maximum = 0, 1
    for vertex in range(1, state.n):
        following = {}
        for (tail, parity), weight in rows.items():
            for bit in (0, 1):
                value = weight
                for prior in range(max(0, vertex-2), vertex):
                    d = counts[prior, vertex]
                    other = (tail >> (vertex-1-prior)) & 1
                    if (other ^ bit) == int(d < 0):
                        value *= 9**abs(d)
                new_parity = parity ^ (bit if pair[0] != pair[1] and vertex in pair else 0)
                key = ((tail << 1 | bit) & 3, new_parity)
                following[key] = following.get(key, 0)+value
                maximum = max(maximum, following[key].bit_length())
                work += 1
        rows = following
        assert len(rows) <= 8
    parts = tuple(sum(value for (_, parity), value in rows.items() if parity == y) for y in (0, 1))
    assert maximum <= state.n+4*sum(map(abs, state.counts))
    return parts, work, maximum


class JointPosterior:
    """Full known-noise joint posterior, using the declared data width exactly."""
    scope = 'independent exact vertex-prefix joint posterior; all counts checked; no world enumeration or values supplied to Runtime'

    def __init__(self, n, counts=(), law='iid-band2'):
        IndexedRelation(n)
        if counts or not law.startswith('iid'):
            raise ContractError('control starts at the declared uniform prior')
        self.n, self.pending, self.labels = n, None, 0
        self.counts = [0]*(n*(n-1)//2)
        self.work = 0  # Actual assignment visits, retained by the common reader.
        self.transitions = self.maximum_integer_bits = self.predictions = 0

    def state(self):
        return CountState(self.n, tuple(self.counts), None, self.labels, self.labels)

    def predict(self, i, j):
        if self.pending is not None:
            raise ContractError('control has one unobserved forecast')
        query(self.n, i, j)
        parts, visits, bits = exact_parts(self.state(), (i, j))
        self.transitions += visits
        self.maximum_integer_bits = max(self.maximum_integer_bits, bits)
        self.predictions += 1
        self.pending = (i, j)
        return tuple((1+8*F(z, sum(parts)))/10 for z in parts)

    def observe(self, target):
        if self.pending is None:
            raise ContractError('control observation requires a prior forecast')
        i, j = self.pending
        query(self.n, i, j, target)
        if abs(i-j) > 2:
            raise ContractError('control update would leave its declared width class')
        if i != j:
            i, j = sorted((i, j))
            self.counts[i*(2*self.n-i-1)//2+j-i-1] += 1-2*target
        self.labels += 1
        self.pending = None

    def statistics(self):
        return {'predictions': self.predictions, 'vertex_transitions': self.transitions,
                'maximum_integer_bits': self.maximum_integer_bits, 'assignment_visits': self.work}


def pair_prediction(state, pair):
    """Known-noise independent-pair posterior; a correlation ablation only."""
    i, j = pair
    if i == j:
        return F(9, 10), F(1, 10)
    i, j = sorted(pair)
    d = state.counts[i*(2*state.n-i-1)//2+j-i-1]
    a, b = 9**max(d, 0), 9**max(-d, 0)
    return F(9*a+b, 10*(a+b)), F(a+9*b, 10*(a+b))


def control(case):
    hidden, _, train, evaluation = data(case)
    joint = JointPosterior(case[0])
    predictions, pair = {}, {}
    for k, (i, j, y) in enumerate(train+evaluation):
        before = joint.state()
        actual = joint.predict(i, j)
        if k >= len(train):
            predictions[i, j] = actual
            pair[i, j] = pair_prediction(before, (i, j))
        joint.observe(y)
    result = {'case': case, 'statistics': joint.statistics(), 'scores': {}}
    for name, pairs in scoring_groups(case):
        result['scores']['adaptive_exact_'+name] = score(predictions, None, hidden, pairs)
        result['scores']['independent_pair_'+name] = score(pair, None, hidden, pairs)
    return result
