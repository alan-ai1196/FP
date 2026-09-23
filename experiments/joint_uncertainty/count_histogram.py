"""Passive exponent-histogram decoder for the fixed native count family.

No Runtime, source, allocation, certificate or installation authority. Integer
enumeration remains explicit. The rounded path constructs its own histogram
from its predecessor; it receives no reference partition or forecast.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src/reference_compiler'))
from fp_reference.core import ContractError, natural
from fp_reference.indexed_count import CountState, query as require_query, world_count
from fp_reference.indexed_execution import IndexedEvaluation
from fp_reference.indexed_amp import (_Arithmetic, IndexedAmpState,
    IndexedAmpPrediction, _observation_schedule)
from fp_reference.semantics import ArithmeticUnresolved

MAX_WORLDS = 32768


@dataclass(frozen=True)
class Histogram:
    n: int
    query: tuple[int, int]
    span: int
    terms: tuple[tuple[tuple[int, int], ...], tuple[tuple[int, int], ...]]
    world_visits: int
    incident_visits: int

    @property
    def term_count(self):
        return sum(map(len, self.terms))

    @property
    def nonempty_parts(self):
        return sum(bool(part) for part in self.terms)

    @property
    def output_cells(self):
        # Every scalar result, and the complete seven-word output copy.
        return 9*self.term_count+21-2*self.nonempty_parts


def _preflight(state, query, world_cap, span_cap, bit_limit):
    if type(state) is not CountState:
        raise ContractError('complete native count predecessor required')
    state.__post_init__()
    if state.pending is not None:
        raise ContractError('prediction requires a committed predecessor')
    if type(query) is not tuple or len(query) != 2:
        raise ContractError('complete ordered query required')
    require_query(state.n, *query)
    for value, name in ((world_cap, 'world allowance'), (span_cap, 'span allowance'),
                        (bit_limit, 'integer allowance')):
        natural(value, name)
    if not 2 <= state.n <= 16:
        raise ArithmeticUnresolved('histogram prototype declares n2 through n16')
    K = world_count(state.n, min(world_cap, MAX_WORLDS))
    H = sum(map(abs, state.counts))
    if H > span_cap:
        raise ArithmeticUnresolved('histogram span allowance insufficient')
    # Before allocation/powers; not a claim about all Python heap or bit work.
    if bit_limit < max(1024, 16*H+8*state.n+1024):
        raise ArithmeticUnresolved('histogram conservative integer allowance insufficient')
    return K, H


def _enumerate(state, query, K, H):
    """One Gray traversal, no materialized world-weight or assignment table."""
    bins = [[0]*(H+1) for _ in range(2)]
    adjacency = [[] for _ in range(state.n)]
    for (i, j), d in zip(combinations(range(state.n), 2), state.counts):
        if d:
            adjacency[i].append((j, d))
            adjacency[j].append((i, d))
    energy = sum(d for d in state.counts if d > 0)
    mask = parity = visits = 0
    bins[0][energy] += 1
    for t in range(1, K):
        v = (t & -t).bit_length()  # Native vertex; bit v-1 changes.
        bit = (mask >> (v-1)) & 1
        for j, d in adjacency[v]:
            other = 0 if j == 0 else (mask >> (j-1)) & 1
            energy += -abs(d) if (bit ^ other) == int(d < 0) else abs(d)
            visits += 1
        mask ^= 1 << (v-1)
        parity ^= int(query[0] != query[1] and v in query)
        bins[parity][energy] += 1
    terms = tuple(tuple((k, h) for k, h in enumerate(part) if h) for part in bins)
    assert sum(h for part in terms for _, h in part) == K
    assert visits <= (state.n-1)*(K-1)
    return Histogram(state.n, query, H, terms, K, visits)


def histogram(state, query, *, world_cap=MAX_WORLDS, span_cap=396, bit_limit=32768):
    K, H = _preflight(state, query, world_cap, span_cap, bit_limit)
    return _enumerate(state, query, K, H)


def exact_parts(hist):
    """Positive polynomial evaluation; large integers are still actual work."""
    totals = []
    for part in hist.terms:
        by_degree = dict(part)
        value = 0
        for k in range(hist.span, -1, -1):
            value = 9*value+by_degree.get(k, 0)
        totals.append(value)
    return tuple(totals)


def reference(state, query, **limits):
    hist = histogram(state, query, **limits)
    parts = exact_parts(hist)
    excesses = tuple(F(8*z, sum(parts)) for z in parts)
    masses = tuple(1+v for v in excesses)
    return IndexedEvaluation(state, query, excesses, masses, F(10),
        tuple(v/10 for v in masses), (('world_visits', hist.world_visits),)), hist


def _rounded_schedule(state, hist, arith):
    top = max(k for part in hist.terms for k, _ in part)
    sums = []
    for part in hist.terms:
        terms = []
        for k, h in part:
            denominator = 9**(top-k)
            eh, bd = h.bit_length(), denominator.bit_length()
            exponent = eh+1-bd
            a = arith.op('constant', constant=F(h, 1 << eh))
            b = arith.op('constant', constant=F(1 << (bd-1), denominator))
            product = arith.op('cast', arith.op('mul',
                arith.op('cast', a, half=True), arith.op('cast', b, half=True), half=True))
            # Product mantissa is in [1/4,1]. Below this exponent its exact
            # RNE32 scaling is +0, including the half-ulp tie at exponent -150.
            scale = F(0) if exponent < -149 else (
                F(1 << exponent) if exponent >= 0 else F(1, 1 << -exponent))
            terms.append(arith.op('mul', product, arith.op('constant', constant=scale)))
        if not terms:
            terms = [arith.op('constant', constant=0)]
        while len(terms) > 1:
            terms = [arith.op('add', terms[i], terms[i+1]) if i+1 < len(terms) else terms[i]
                     for i in range(0, len(terms), 2)]
        sums.append(terms[0])
    denominator = arith.op('add', *sums)
    marginals = tuple(arith.op('div', value, denominator) for value in sums)
    one, eight = (arith.op('constant', constant=value) for value in (1, 8))
    excesses = tuple(arith.op('mul', eight, value) for value in marginals)
    masses = tuple(arith.op('add', one, value) for value in excesses)
    normalizer = arith.op('add', *masses)
    probabilities = tuple(arith.op('div', value, normalizer) for value in masses)
    columns = excesses+masses+(normalizer,)+probabilities
    arith.stack(columns)
    return IndexedAmpPrediction(state, hist.query, tuple(v.word for v in columns))


def rounded_prediction(state, query, *, output_cap=65536, **limits):
    """Passive exact-RNE simulation, independently derived from physical counts."""
    natural(output_cap, 'floating output allowance')
    hist = histogram(state, query, **limits)
    if hist.output_cells > output_cap:
        raise ArithmeticUnresolved('histogram floating output allowance insufficient')
    arithmetic = _Arithmetic(limits.get('bit_limit', 32768))
    raw = _rounded_schedule(state, hist, arithmetic)
    assert len(arithmetic.trace)+7 == hist.output_cells
    assert sum(width == 16 for _, width, _ in arithmetic.trace) == 3*hist.term_count
    return raw, hist, tuple(arithmetic.trace)


def rounded_observation(state, prediction, target):
    arithmetic = _Arithmetic(32768)
    raw, _ = _observation_schedule(IndexedAmpState(state), prediction, target, arithmetic)
    assert len(arithmetic.trace)+3 == 13
    return raw, tuple(arithmetic.trace)


def precision_bound(terms=MAX_WORLDS):
    """Rational upper bounds, including host ingress, underflow and readout."""
    natural(terms, 'positive term bound', positive=True)
    if terms > MAX_WORLDS:
        raise ContractError('precision theorem declares at most32768 terms')
    depth = (terms-1).bit_length()
    u, v, tau = F(1, 1 << 24), F(1, 1 << 11), F(1, 1 << 150)
    epsilon = (1+v)**3*(1+u)**(depth+1)-1
    eta = terms*tau*(1+u)**depth
    A, B = 2*epsilon/(1-epsilon-eta), eta/(1-epsilon-eta)
    D = A/4+B
    kappa = 2*u/(1-u)
    R = 8*(kappa+tau)+9*u
    assert 1-epsilon-eta > 0 and 1-8*D > 0
    return {'terms': terms, 'sum_depth': depth, 'epsilon': epsilon, 'underflow': eta,
        'marginal': D, 'native': 8*D+R, 'normalizer': 2*R+18*u,
        'probability': F(4, 5)*D+R/(10-2*R)+kappa+tau,
        'proper_mass_division': kappa+tau,
        'gradient': 64*(A/36+B)/(1-8*D)+8*R+18*u}
