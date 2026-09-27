"""Passive complete parameter/pending-gradient relation for native tokens.

The exact decision class is one pair of committed origins or one pair of
retained prefixes with identical definitions, records and clocks. No future
event, owned Runtime, physical-code or installation authority is issued.
"""
from dataclasses import dataclass
from fractions import Fraction as F
import math
import numpy as np

from . import token_amp as amp
from . import token_batch as ref
from . import token_readout as readout
from .token_enclosures import EnclosureUnresolved
from .token_readout_relation import Binary32Decoder, absolute_upper


@dataclass(frozen=True)
class Contract:
    state_atol: F
    element_cap: int
    exact_cell_cap: int

    def __post_init__(self):
        if type(self.state_atol) is not F or self.state_atol < 0:
            raise ValueError('exact nonnegative complete-state tolerance required')
        readout.natural(self.element_cap, positive=True)
        readout.natural(self.exact_cell_cap)


def _masters(origin, physical, arithmetic, contract):
    if type(origin) is not ref.Origin or type(physical) is not amp.State or origin.definition != physical.definition:
        raise ValueError('paired complete registered origins required')
    if (origin.cursor, origin.optimizer_steps, origin.source) != (physical.cursor, physical.optimizer_steps, physical.source):
        raise ValueError('complete origin clocks and source contexts differ')
    error, coordinates = F(0), 0
    for key in ('E', 'C', 'W'):
        native = getattr(origin, key)
        ref.size_check(native.shape, contract.element_cap)
        actual = arithmetic.raw(getattr(physical, key))
        if actual.dtype != np.int64 or actual.shape != native.shape or np.any(actual < 0) or np.any(actual > ref.WORD_MAX):
            raise ValueError('complete physical integer master array required')
        distance = int(np.max(np.abs(actual-native.astype(np.int64)), initial=0))
        error = max(error, F(distance, origin.definition.output.grid))
        coordinates += actual.size
    return error, coordinates


def _gradient_error(actual, native):
    if actual.dtype != np.float32 or actual.shape != native.lower.shape:
        raise ValueError('complete single-precision gradient basis block required')
    discrepancy = absolute_upper(ref.ArrayInterval.point(actual.astype(np.float64))-native)
    value = float(np.max(discrepancy, initial=0))
    if not math.isfinite(value):
        raise EnclosureUnresolved('complete gradient error envelope exhausted')
    return F(value)


def check(native, physical, arithmetic, contract):
    if type(contract) is not Contract:
        raise ValueError('registered complete-state comparison contract required')
    contract.__post_init__()
    pending = type(native) is ref.Bounds and type(physical) is amp.Pending
    committed = type(native) is ref.Origin and type(physical) is amp.State
    if not (pending or committed):
        raise ValueError('paired committed states or paired actual prefixes required')
    left = native.unit.origin if pending else native
    right = physical.origin if pending else physical
    parameter_error, parameters = _masters(left, right, arithmetic, contract)
    gradient_error, decoded_cells = F(0), 0
    unit_count, cursor, compared_basis = 0, left.cursor, 0
    decoder = Binary32Decoder(contract.exact_cell_cap)
    if pending:
        if (native.unit.windows != physical.windows or native.unit.targets != physical.targets
                or native.unit_count != physical.unit_count or native.cursor != physical.cursor or native.source != physical.source):
            raise ValueError('complete retained records, source and pending clock differ')
        unit_count, cursor = native.unit_count, native.cursor
        if not 1 <= unit_count <= left.definition.output.update_unit:
            raise ValueError('pending prefix outside the registered unit')
        for key in ('embedding_ids', 'correction_ids'):
            actual, expected = getattr(physical, key), getattr(native, key)
            if actual.dtype != np.int64 or actual.shape != expected.shape or not np.array_equal(actual, expected):
                raise ValueError('complete gradient incidence keys differ')
        arrays = {}
        for key in ('embedding', 'core', 'common', 'corrections'):
            enclosed = getattr(native, key)
            ref.size_check(enclosed.lower.shape, contract.element_cap)
            actual = arithmetic.raw(getattr(physical, key))
            # Both readout basis blocks must be valid even when only their
            # signed combination is an ordinary gradient coordinate.
            if actual.dtype != np.float32 or actual.shape != enclosed.lower.shape or not np.all(np.isfinite(actual)):
                raise ValueError('complete finite single-precision gradient block required')
            arrays[key] = actual
            compared_basis += actual.size
            if key != 'corrections':
                gradient_error = max(gradient_error, _gradient_error(actual, enclosed))
        # A common row covers every unobserved label. For observed labels,
        # decode exactly the RNE32 subtraction consumed by the AMP commit.
        decoded = decoder.op('add', arrays['common'], -arrays['corrections'])
        gradient_error = max(gradient_error, _gradient_error(decoded, native.common-native.corrections))
        decoded_cells = decoded.size
    maximum = max(parameter_error, gradient_error)
    if maximum > contract.state_atol:
        raise EnclosureUnresolved('complete token learner-state error exceeds its fixed tolerance')
    return dict(status='PASS_COMPLETE_TOKEN_STATE_RELATION_DATA',
        parameter_error_upper=str(parameter_error), gradient_error_upper=str(gradient_error), state_error_upper=str(maximum),
        parameter_coordinates=parameters, gradient_coordinates=parameters, compared_gradient_basis_words=compared_basis,
        decoded_corrected_gradient_words=decoded_cells, exact_rounding_cells=decoder.exact_cells,
        cursor=cursor, unit_count=unit_count, optimizer_steps=left.optimizer_steps,
        scope='one complete observed learner-state relation; no owned code, Runtime, future event or issued bridge')
