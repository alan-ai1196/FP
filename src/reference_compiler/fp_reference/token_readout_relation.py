"""Passive complete-vocabulary prediction relation, with bounded block scans.

Actual readout words are checked against a deterministic binary32 decoder.
The exact sum of stored masses is distinct from the physical normalizer.
No Runtime, state/gradient, freshness, bridge or installation authority.
"""
from dataclasses import dataclass
from fractions import Fraction as F
import math
import numpy as np

from . import token_batch as ref
from .token_enclosures import Interval, EnclosureUnresolved
from .binary_arithmetic import round_binary
from .token_amp import SINGLE
from . import token_readout as readout


class Binary32Decoder:
    """Exact-RNE decisions from binary64 enclosures, with paid tie fallback.

    Products of two finite binary32 operands are exact in binary64. TwoSum
    determines addition residuals. Division gets outward binary64 bounds.
    Only ambiguous binary32 rounding cells use the finite exact verifier.
    These values check an actual result, never choose a learner successor.
    """
    def __init__(self, exact_cell_cap):
        readout.natural(exact_cell_cap)
        self.exact_cell_cap, self.exact_cells, self.words = exact_cell_cap, 0, 0

    def op(self, kind, a, b):
        if a.dtype != np.float32 or b.dtype != np.float32:
            raise ValueError('binary32 decoder operands required')
        x, y = np.broadcast_arrays(a.astype(np.float64), b.astype(np.float64))
        if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
            raise EnclosureUnresolved('nonfinite decoder operand')
        with np.errstate(over='ignore', under='ignore', invalid='ignore', divide='ignore'):
            if kind == 'mul':
                low = high = x*y
            elif kind == 'add':
                value = x+y
                z = value-x
                residual = (x-(value-z))+(y-z)
                low = np.where(residual < 0, np.nextafter(value, -np.inf), value)
                high = np.where(residual > 0, np.nextafter(value, np.inf), value)
            elif kind == 'div':
                if np.any(y == 0):
                    raise EnclosureUnresolved('zero decoder denominator')
                value = x/y
                low, high = np.nextafter(value, -np.inf), np.nextafter(value, np.inf)
            else:
                raise ValueError('closed binary32 decoder operation required')
            rounded_low, rounded_high = low.astype(np.float32), high.astype(np.float32)
        result = np.array(rounded_low, copy=True)
        # Numerically equal signed zeros still retain their distinct bits.
        uncertain = rounded_low.view(np.uint32) != rounded_high.view(np.uint32)
        for flat in np.flatnonzero(uncertain):
            if self.exact_cells >= self.exact_cell_cap:
                raise EnclosureUnresolved('exact readout rounding-cell verifier allowance exhausted')
            self.exact_cells += 1
            i = np.unravel_index(int(flat), result.shape)
            left, right = F(float(x[i])), F(float(y[i]))
            value = left+right if kind == 'add' else left*right if kind == 'mul' else left/right
            signs = (bool(np.signbit(x[i])), bool(np.signbit(y[i])))
            negative_zero = (not left and not right and all(signs)) if kind == 'add' else not value and signs[0] != signs[1]
            rounded = round_binary(value, SINGLE, bit_limit=4096, negative_zero=bool(negative_zero))
            result[i] = -0.0 if rounded.negative_zero else float(rounded.value)
        if not np.all(np.isfinite(result)):
            raise EnclosureUnresolved('binary32 decoder result is nonfinite')
        self.words += result.size
        return result

    def reduce(self, values):
        while len(values) > 1:
            pairs = len(values)//2
            following = self.op('add', values[:2*pairs:2], values[1:2*pairs:2])
            values = np.concatenate((following, values[-1:])) if len(values) % 2 else following
        return values[0]

    def block(self, masters, features, bases, normalizer, p):
        # uint32 masters and p<=32 have an exact binary64 scaled encoding.
        weights = np.ldexp(masters.astype(np.float64), -p).astype(np.float32)
        terms = self.op('mul', weights.T[:, :, None], features[:, None, :])
        excess = self.reduce(terms)
        masses = self.op('add', bases[:, None], excess)
        return excess, masses, self.op('div', masses, normalizer[None, :])


class MassTotal:
    """Exact positive binary32 sum through 254 bounded integer exponent bins."""
    def __init__(self, labels, events, *, element_cap):
        readout.natural(labels, positive=True)
        readout.natural(events, positive=True)
        if labels > 1 << 20:
            raise EnclosureUnresolved('exact exponent-bin word allowance exhausted')
        ref.size_check((254, events), element_cap)
        self.labels, self.events, self.rows = labels, events, 0
        self.bins = np.zeros((254, events), dtype=np.int64)

    def add(self, values):
        if type(values) is not np.ndarray or values.dtype != np.float32 or values.ndim != 2 or values.shape[1] != self.events:
            raise ValueError('complete binary32 label rows required')
        if self.rows+len(values) > self.labels:
            raise ValueError('too many mass rows')
        words = values.view(np.uint32)
        exponent = ((words >> 23) & 255).astype(np.int64)
        if np.any(words >> 31) or np.any(exponent == 255):
            raise EnclosureUnresolved('mass bins require finite nonnegative words')
        mantissa = (words & 0x7fffff).astype(np.int64)+np.where(exponent != 0, 1 << 23, 0)
        # Each bin is < V*2^24 <=2^44. Neither repeated integer addition nor
        # its int64 storage can overflow; no floating reduction is involved.
        np.add.at(self.bins, (np.maximum(0, exponent-1), np.arange(self.events)[None, :]), mantissa)
        self.rows += len(values)

    def finish(self):
        if self.rows != self.labels:
            raise ValueError('the complete vocabulary was not scanned')
        return tuple(F(sum(int(self.bins[e, t]) << e for e in range(254)), 1 << 149) for t in range(self.events))


@dataclass(frozen=True)
class PredictionContract:
    activation_cap: F
    normalizer_cap: F
    native_atol: F
    probability_atol: F
    division_atol: F
    block_labels: int
    element_cap: int
    exact_cell_cap: int

    def __post_init__(self):
        for name in ('activation_cap', 'normalizer_cap', 'native_atol', 'probability_atol', 'division_atol'):
            value = getattr(self, name)
            if type(value) is not F or value < 0 or name.endswith('_cap') and not value:
                raise ValueError('exact nonnegative tolerance or positive range cap required')
        for name in ('block_labels', 'element_cap'):
            readout.natural(getattr(self, name), positive=True)
        readout.natural(self.exact_cell_cap)


def absolute_upper(interval):
    return np.maximum(abs(interval.lower), abs(interval.upper))


def rational_vector(values):
    intervals = tuple(Interval.exact(value) for value in values)
    return ref.ArrayInterval(np.asarray([v.lower for v in intervals]), np.asarray([v.upper for v in intervals]))


def native_block(bounds, first, stop):
    origin, d = bounds.unit.origin, bounds.unit.origin.definition
    weights = ref.ArrayInterval.point(np.ldexp(origin.W[first:stop].astype(np.float64), -d.output.grid_bits)).transpose()
    features = bounds.values[np.asarray(d.features)]
    excess = ref.reduce_rows(weights[:, :, None]*features[:, None, :])
    return excess, rational_vector(d.output.base[first:stop])[:, None]+excess


def check(bounds, pending, physical_kernel, contract):
    """Check every label/event; return passive diagnostics, never authority."""
    if type(contract) is not PredictionContract:
        raise ValueError('fixed complete prediction comparison contract required')
    contract.__post_init__()
    d, a = bounds.unit.origin.definition, physical_kernel.a
    if (physical_kernel.definition != d or pending.origin.definition != d or bounds.unit.windows != pending.windows
            or bounds.unit.targets != pending.targets or bounds.unit.origin.cursor != pending.origin.cursor
            or bounds.unit.origin.optimizer_steps != pending.origin.optimizer_steps):
        raise ValueError('paired complete definitions, actual records and learner clocks required')
    N, V, K = len(pending.targets), d.output.labels, d.output.features
    for shape in ((K, min(V, contract.block_labels), N), (V, K),
                  (d.input_nodes+len(d.nodes), N)):
        ref.size_check(shape, contract.element_cap)
    total = MassTotal(V, N, element_cap=contract.element_cap)
    decoder = Binary32Decoder(contract.exact_cell_cap)
    actual_values = a.raw(pending.values)
    if actual_values.dtype != np.float16 or np.any(actual_values < 0):
        raise ValueError('complete nonnegative half core state required')
    actual_values = actual_values.astype(np.float64)
    actual_z = a.raw(pending.normalizer)
    actual_target = a.raw(pending.target_mass)
    if (actual_values.shape != bounds.values.lower.shape or actual_z.shape != (N,) or actual_z.dtype != np.float32
            or actual_target.shape != (N,) or actual_target.dtype != np.float32 or np.any(actual_z <= 0)):
        raise ValueError('complete physical forward state required')
    features = actual_values[np.asarray(d.features)].astype(np.float32)
    masters, bases = a.raw(pending.origin.W), a.raw(physical_kernel.base)
    if masters.dtype != np.int64 or masters.shape != (V, K) or np.any(masters < 0) or np.any(masters > ref.WORD_MAX):
        raise ValueError('complete physical integer readout masters required')
    cache = {v: float(round_binary(v, SINGLE, bit_limit=4096).value) for v in set(d.output.base)}
    registered_base = np.asarray([cache[v] for v in d.output.base], dtype=np.float32)
    if bases.dtype != np.float32 or bases.shape != (V,) or bases.tobytes() != registered_base.tobytes():
        raise EnclosureUnresolved('physical base cache differs from registered RNE32 ingress')
    native_error = float(np.max(absolute_upper(ref.ArrayInterval.point(actual_values)-bounds.values)))
    activation_upper = max(float(np.max(bounds.values.upper)), float(np.max(actual_values)))
    raw_error, round_error, maximum_mass = (np.zeros(N) for _ in range(3))
    targets = np.asarray(pending.targets)
    target_checks = coordinates = blocks = 0
    for first in range(0, V, contract.block_labels):
        stop = min(V, first+contract.block_labels)
        physical = physical_kernel.mass_block(pending, first, stop)
        excess, masses, probabilities = tuple(a.raw(value) for value in physical)
        expected = decoder.block(masters[first:stop], features, bases[first:stop], actual_z, d.output.grid_bits)
        if any(x.dtype != np.float32 or x.shape != (stop-first, N) or x.tobytes() != y.tobytes()
               for x, y in zip((excess, masses, probabilities), expected)):
            raise EnclosureUnresolved('physical readout disagrees with its reproducible binary32 decoder')
        selected = np.flatnonzero((targets >= first) & (targets < stop))
        if not np.array_equal(masses[targets[selected]-first, selected].view(np.uint32), actual_target[selected].view(np.uint32)):
            raise EnclosureUnresolved('target cache differs from the complete physical readout')
        target_checks += len(selected)
        total.add(masses)
        native_excess, native_mass = native_block(bounds, first, stop)
        m, p = ref.ArrayInterval.point(masses.astype(np.float64)), ref.ArrayInterval.point(probabilities.astype(np.float64))
        native_error = max(native_error, float(np.max(absolute_upper(ref.ArrayInterval.point(excess.astype(np.float64))-native_excess))),
            float(np.max(absolute_upper(m-native_mass))))
        activation_upper = max(activation_upper, float(np.max(native_excess.upper)), float(np.max(excess)))
        raw_error = np.maximum(raw_error, np.max(absolute_upper(p-native_mass/bounds.normalizer), axis=0))
        round_error = np.maximum(round_error, np.max(absolute_upper(p-m/ref.ArrayInterval.point(actual_z.astype(np.float64))), axis=0))
        maximum_mass = np.maximum(maximum_mass, np.max(masses, axis=0))
        coordinates += masses.size
        blocks += 1
    if target_checks != N or coordinates != V*N:
        raise ValueError('incomplete full-vocabulary prediction traversal')
    exact_total = total.finish()
    S, Z = rational_vector(exact_total), ref.ArrayInterval.point(actual_z.astype(np.float64))
    if np.any(S.lower <= 0):
        raise EnclosureUnresolved('positive exact mass sum not numerically resolved')
    normalizer_error = max(float(np.max(absolute_upper(bounds.normalizer-S))),
        float(np.max(absolute_upper(bounds.normalizer-Z))), float(np.max(absolute_upper(S-Z))))
    # For every label: |m/S - raw_p| <= m_max |S-Z|/(S Z)
    # + max |m/Z - raw_p|. This covers the entire vector without a second scan.
    correction = ref.ArrayInterval.point(maximum_mass)*ref.ArrayInterval.point(absolute_upper(S-Z))/(S*Z)
    division = correction+ref.ArrayInterval.point(round_error)
    probability = division+ref.ArrayInterval.point(raw_error)
    diagnostics = dict(native_error_upper=native_error, normalizer_error_upper=normalizer_error,
        probability_error_upper=float(np.max(probability.upper)), division_error_upper=float(np.max(division.upper)),
        activation_upper=activation_upper, normalizer_upper=max(float(np.max(bounds.normalizer.upper)),
            float(np.max(Z.upper)), float(np.max(S.upper))))
    for key, cap in (('native_error_upper', contract.native_atol), ('normalizer_error_upper', contract.native_atol),
                     ('probability_error_upper', contract.probability_atol), ('division_error_upper', contract.division_atol),
                     ('activation_upper', contract.activation_cap), ('normalizer_upper', contract.normalizer_cap)):
        if not math.isfinite(diagnostics[key]) or F(diagnostics[key]) > cap:
            raise EnclosureUnresolved('complete prediction relation unresolved: '+key)
    return dict(status='PASS_COMPLETE_PREDICTION_RELATION_DATA', **diagnostics, events=N, labels=V,
        prediction_coordinates=coordinates, complete_label_blocks=blocks, target_cache_checks=target_checks,
        actual_readout_output_words=3*coordinates, decoder_words=decoder.words, exact_rounding_cells=decoder.exact_cells,
        maximum_stored_sum_numerator_bits=max(v.numerator.bit_length() for v in exact_total),
        exact_stored_sum=exact_total,
        scope='passive full observed-context prediction relation; no state/gradient, Runtime, freshness or issued bridge')
