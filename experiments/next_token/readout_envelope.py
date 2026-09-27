"""All-label error envelope for the fixed positive binary32 readout recipe.

Conditional numerical data, not an issued physical bridge. An owner must
bind the actual complete operands/code and check executed query words.
Unlike the exhaustive control, this does not execute unqueried labels.
"""
from collections import Counter
from fractions import Fraction as F
import math
import numpy as np

import amp_tokens as amp
import batched_tokens as ref
import readout_relation as scan
from enclosed_tokens import EnclosureUnresolved
from fp_reference.binary_arithmetic import round_binary


def upper(value):
    return float(np.max(value.upper))


def bound(bounds, pending, kernel, contract):
    if type(contract) is not scan.PredictionContract or type(kernel) is not amp.Kernel or type(pending) is not amp.Pending:
        raise ValueError('registered readout recipe, complete operands and comparison contract required')
    contract.__post_init__()
    d, a = bounds.unit.origin.definition, kernel.a
    if (kernel.definition != d or pending.origin.definition != d or bounds.unit.windows != pending.windows
            or bounds.unit.targets != pending.targets or bounds.unit.origin.cursor != pending.origin.cursor
            or bounds.unit.origin.optimizer_steps != pending.origin.optimizer_steps):
        raise ValueError('paired actual records, definitions and learner clocks required')
    N, V, K, p = len(pending.targets), d.output.labels, d.output.features, d.output.grid_bits
    if V > 1 << 20 or p > 32 or not N or not K:
        raise EnclosureUnresolved('readout envelope word/geometry domain exhausted')
    for shape in ((V, K), (d.input_nodes+len(d.nodes), N), (K, N)):
        ref.size_check(shape, contract.element_cap)
    actual = a.raw(pending.values)
    Z32, target32 = a.raw(pending.normalizer), a.raw(pending.target_mass)
    q, bases = a.raw(pending.origin.W), a.raw(kernel.base)
    if (actual.dtype != np.float16 or actual.shape != bounds.values.lower.shape or np.any(actual < 0)
            or not np.all(np.isfinite(actual)) or Z32.dtype != np.float32 or Z32.shape != (N,)
            or np.any(Z32 <= 0) or not np.all(np.isfinite(Z32)) or target32.dtype != np.float32 or target32.shape != (N,)):
        raise ValueError('complete finite nonnegative half core and positive normalizer required')
    if q.dtype != np.int64 or q.shape != (V, K) or np.any(q < 0) or np.any(q > ref.WORD_MAX):
        raise ValueError('complete physical uint32-valued integer masters required')
    base_counts = Counter(d.output.base)
    rounded = {b: F(round_binary(b, amp.SINGLE, bit_limit=4096).value) for b in base_counts}
    registered = np.asarray([float(rounded[b]) for b in d.output.base], dtype=np.float32)
    if bases.dtype != np.float32 or bases.shape != (V,) or bases.tobytes() != registered.tobytes() or np.any(bases <= 0):
        raise EnclosureUnresolved('base cache is not the positive registered RNE32 ingress')

    I = ref.ArrayInterval
    # Rounding q<=2^32-1 to binary32 gives an integer <=2^32. Its column
    # sum over V<=2^20 is <=2^52, exactly representable in binary64.
    rounded_q = q.astype(np.float32).astype(np.int64)
    weights = np.ldexp(rounded_q.astype(np.float64), -p).astype(np.float32)
    columns = np.ldexp(rounded_q.sum(axis=0, dtype=np.int64).astype(np.float64), -p)
    weight_max = I.point(np.ldexp(rounded_q.max(axis=0).astype(np.float64), -p))
    native_max = I.point(np.ldexp(bounds.unit.origin.W.max(axis=0).astype(np.float64), -p))
    delta = np.max(np.abs(rounded_q-bounds.unit.origin.W.astype(np.int64)), axis=0)
    weight_error = I.point(np.ldexp(delta.astype(np.float64), -p))
    actual = actual.astype(np.float64)
    features = I.point(actual[np.asarray(d.features)])
    native_features = bounds.values[np.asarray(d.features)]
    feature_error = I.point(scan.absolute_upper(features-native_features))
    base_total = sum((count*rounded[b] for b, count in base_counts.items()), F(0))
    base_error = max(abs(b-rounded[b]) for b in base_counts)
    beta_min, beta_max = min(rounded.values()), max(rounded.values())

    # h balanced additions, one product, one base addition on any path.
    h, u, alpha = (K-1).bit_length(), F(1, 1 << 24), F(1, 1 << 150)
    factor = (1+u)**(h+2)
    rho, tau = I.rational(factor-1), I.rational(2*K*alpha*factor)
    maximum_excess = ref.reduce_rows(weight_max[:, None]*features)
    maximum_unrounded_mass = I.rational(beta_max)+maximum_excess
    rounding = rho*maximum_unrounded_mass+tau
    maximum_mass = maximum_unrounded_mass+rounding
    # Every intermediate is positive and bounded by this same upward
    # propagation bound. Refuse before relying on finite RNE arithmetic.
    if upper(maximum_mass) > float(np.finfo(np.float32).max):
        raise EnclosureUnresolved('uniform binary32 readout overflow envelope exhausted')
    mass_error = I.rational(base_error)+ref.reduce_rows(
        weight_error[:, None]*features+native_max[:, None]*feature_error)+rounding
    native_excess = ref.reduce_rows(native_max[:, None]*native_features)
    physical_excess = maximum_excess+rho*maximum_excess+tau

    total_unrounded = I.rational(base_total)+ref.reduce_rows(I.point(columns)[:, None]*features)
    total_rounding = rho*total_unrounded+I.point(V)*tau
    S = I((total_unrounded-total_rounding).lower, (total_unrounded+total_rounding).upper)
    R, Z = bounds.normalizer, I.point(Z32.astype(np.float64))
    if np.any(S.lower <= 0) or np.any(R.lower <= 0):
        raise EnclosureUnresolved('positive complete mass normalization not enclosed')
    ideal_minimum = I.rational(beta_min)/Z
    ideal_maximum = maximum_mass/Z
    if np.any(ideal_minimum.lower < 2.0**-149) or np.any(ideal_maximum.upper > 1):
        raise EnclosureUnresolved('positive at-most-one raw probabilities not uniformly resolved')
    division_rounding = I.rational(u)*ideal_maximum+I.rational(alpha)
    abs_RZ = I.point(scan.absolute_upper(R-Z))
    abs_RS = I.point(scan.absolute_upper(R-S))
    abs_SZ = I.point(scan.absolute_upper(S-Z))
    raw_error = mass_error/R+maximum_mass*abs_RZ/(R*Z)+division_rounding
    proper_error = mass_error/R+maximum_mass*abs_RS/(R*S)
    division_error = maximum_mass*abs_SZ/(S*Z)+division_rounding

    # Bind every already-executed target cache to the fixed recipe. This
    # costs O(KN), with no evaluation of the remaining vocabulary entries.
    labels = np.asarray(pending.targets)
    decoder = scan.Binary32Decoder(contract.exact_cell_cap)
    excess = decoder.reduce(decoder.op('mul', weights[labels].T, features.lower.astype(np.float32)))
    target = decoder.op('add', bases[labels], excess)
    if target.tobytes() != target32.tobytes():
        raise EnclosureUnresolved('executed target cache differs from the registered readout recipe')
    diagnostics = dict(native_error_upper=max(upper(mass_error), float(np.max(scan.absolute_upper(I.point(actual)-bounds.values)))),
        normalizer_error_upper=max(upper(abs_RZ), upper(abs_RS), upper(abs_SZ)),
        probability_error_upper=max(upper(raw_error), upper(proper_error)), division_error_upper=upper(division_error),
        activation_upper=max(float(np.max(actual)), float(np.max(bounds.values.upper)), upper(native_excess), upper(physical_excess)),
        normalizer_upper=max(upper(R), upper(Z), upper(S)))
    for key, cap in (('native_error_upper', contract.native_atol), ('normalizer_error_upper', contract.native_atol),
                     ('probability_error_upper', contract.probability_atol), ('division_error_upper', contract.division_atol),
                     ('activation_upper', contract.activation_cap), ('normalizer_upper', contract.normalizer_cap)):
        if not math.isfinite(diagnostics[key]) or F(diagnostics[key]) > cap:
            raise EnclosureUnresolved('complete recipe envelope unresolved: '+key)
    return dict(status='PASS_CONDITIONAL_COMPLETE_READOUT_ENVELOPE', **diagnostics,
        events=N, labels=V, covered_prediction_coordinates=V*N, readout_master_coordinates=V*K,
        target_cache_checks=N, target_decoder_words=decoder.words, exact_rounding_cells=decoder.exact_cells,
        unqueried_label_contexts_executed=0, balanced_depth=h,
        stored_sum_lower=tuple(float(x) for x in S.lower), stored_sum_upper=tuple(float(x) for x in S.upper),
        scope='conditional RNE32 recipe envelope for retained operands; no issued physical, state/event or Runtime bridge')
