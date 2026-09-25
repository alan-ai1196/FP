"""Passive declarations and conclusions of one owned, finite reference run.

Only Runtime assembles/retains these records. A returned record is not a
signer, an install token, a population guarantee or a release certificate.
"""
from dataclasses import dataclass, field
from fractions import Fraction as F

from .numerics import compare_exact
from .semantics import _guard


@dataclass(frozen=True)
class ReferenceRunManifest:
    construction: object
    initial_program: object
    online: object
    host: object
    policy: object
    machine_id: str
    initializer_id: str
    python_implementation: tuple
    cpu_arithmetic: tuple | None
    protocol: str = field(default='single-root-finite-ordinary-stream-and-owned-policy-v1', init=False)
    reference_arithmetic: str = field(default='guarded-exact-rational-native-and-learner-operations-v1', init=False)
    reference_scope: str = field(default='registered constructor endpoints and baseline; executed CPU prefix only', init=False)
    target_amp: str = field(default='UNRESOLVED: actual target AMP is not implemented', init=False)

    def __post_init__(self):
        from .histogram_decoder import MODEL_ID
        from .packed_histogram_decoder import MODEL_ID as PACKED_MODEL_ID
        from .integer_partition_decoder import MODEL_ID as DIRECT_MODEL_ID
        from .joint_execution import MODEL_ID as JOINT_MODEL_ID, ARITHMETIC_ID as JOINT_ARITHMETIC
        from .joint_execution import RATIONAL_MODEL_ID as RATIONAL_JOINT_MODEL_ID, RATIONAL_ARITHMETIC_ID as RATIONAL_JOINT_ARITHMETIC
        if self.machine_id == JOINT_MODEL_ID:
            object.__setattr__(self, 'reference_arithmetic', JOINT_ARITHMETIC)
        if self.machine_id == RATIONAL_JOINT_MODEL_ID:
            object.__setattr__(self, 'reference_arithmetic', RATIONAL_JOINT_ARITHMETIC)
        if self.machine_id == DIRECT_MODEL_ID:
            object.__setattr__(self, 'reference_arithmetic',
                               'indexed-literal-count-direct-partition-reference-v1')
        if self.machine_id == PACKED_MODEL_ID:
            object.__setattr__(self, 'reference_arithmetic',
                               'indexed-literal-count-carry-free-histogram-reference-v1')
        if self.machine_id == MODEL_ID:
            object.__setattr__(self, 'reference_arithmetic',
                               'indexed-literal-count-positive-exponent-histogram-reference-v1')
        if self.machine_id in ('packed-indexed-reference-payload-v1', 'packed-indexed-reference-payload-v2',
                               'packed-indexed-reference-payload-v3'):
            object.__setattr__(self, 'reference_arithmetic',
                               'indexed-literal-count-positive-query-block-reference-v1')


@dataclass(frozen=True)
class RunDecision:
    search_id: str
    decision_class_id: str
    spec: object
    ordinary_cursor: int
    base_lineage_id: str
    search_status: str
    decision_status: str
    proof: object
    scope: str = field(default='historical fixed-state empirical CE over registered native endpoints plus actual baseline', init=False)


@dataclass(frozen=True)
class PredictionDiagnostics:
    path: str
    predictions: int
    minimum_nonzero_activation: F | None
    maximum_activation: F | None
    minimum_mass: F | None
    maximum_normalizer: F | None
    max_rational_numerator_bits: int
    max_rational_denominator_bits: int
    scope: str = field(default='retained ordinary/profile prediction values; rational encoding widths, not hardware significand widths or future bounds', init=False)


def prediction_diagnostics(predictions, path, bit_limit):
    """Paid by Runtime before scanning; no reevaluation or authority here."""
    from .indexed_execution import IndexedEvaluation
    from .joint_execution import JointEvaluation
    count = numerator = denominator = 0
    amin = amax = mmin = tmax = None

    def smaller(a, b):
        return compare_exact(a, b, bit_limit=bit_limit) < 0

    def low(old, value):
        return value if old is None or smaller(value, old) else old

    def high(old, value):
        return value if old is None or smaller(old, value) else old

    for prediction in predictions:
        count += 1
        decode = (lambda value: value.exact) if path in ('cpu-binary64', 'cuda-half-single') else (lambda value: value)
        for label in ('values', 'masses', 'probabilities', 'normalizer'):
            values = ((prediction.normalizer,) if label == 'normalizer' else
                      prediction.activation_basis() if label == 'values' and type(prediction) in (IndexedEvaluation, JointEvaluation) else
                      getattr(prediction, label))
            for raw in values:
                value = decode(raw)
                _guard(value, bit_limit=bit_limit)
                numerator = max(numerator, value.numerator.bit_length())
                denominator = max(denominator, value.denominator.bit_length())
                if label == 'values':
                    amax = high(amax, value)
                    if value > 0:
                        amin = low(amin, value)
                elif label == 'masses':
                    mmin = low(mmin, value)
                elif label == 'normalizer':
                    tmax = high(tmax, value)
    return PredictionDiagnostics(path, count, amin, amax, mmin, tmax, numerator, denominator)


@dataclass(frozen=True)
class ReferenceRunClosure:
    object_id: str
    cursor: int
    deployed_id: str
    policy_generation: int
    stage_outcomes: tuple[tuple[int, str, str], ...]
    decisions: tuple[RunDecision, ...]
    native_graphs: tuple
    diagnostics: tuple[PredictionDiagnostics, ...]
    partial_optimizer_events: int
    alpha_spent: F
    alpha_scope: str = field(default='one Runtime root under its declared external stream-law assumptions; no restarted-family guarantee', init=False)
    execution: str = field(default='SEALED_REFERENCE_STREAM', init=False)
    authority: str = field(default='no future continuation or install authority; no CERTIFIED_COMPLETE or target AMP claim', init=False)


@dataclass(frozen=True)
class ReferenceRunSnapshot:
    manifest: ReferenceRunManifest
    manifest_object_id: str
    status: str
    closure: ReferenceRunClosure | None
    host_scope: str
    report_scope: str = field(default='this header and the complete RuntimeSnapshot, including owned buffers, resources, host observation and halt state', init=False)
