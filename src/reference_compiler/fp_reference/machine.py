"""Deterministic packed reference realization, explicitly short of a GPU model.

`reference_payload_bytes` measures the actual retained packed buffers below;
it does not claim to count the CPython process heap or CUDA allocations. The
target-device machine/AMP integration remains a separate release obligation.
Work debits are conservative reference operation charges, not measured CPU or
GPU time and not lower certificates on physical cost. Exhausting those charges
is therefore UNRESOLVED for any broader physical-resource claim.
"""
from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from fractions import Fraction as F
import json
from typing import Mapping

from .core import ContractError
from .program import Program, SemanticRules, rational
from .resources import ObjectSpec


def _data(value):
    if type(value) is F:
        return ['rational_hex', format(value.numerator, 'x'), format(value.denominator, 'x')]
    if type(value) is int:
        return ['integer_hex', format(value, 'x')]
    if value is None or type(value) in (str, bool):
        return [type(value).__name__, value]
    if type(value) in (tuple, list):
        return [type(value).__name__, [_data(x) for x in value]]
    if isinstance(value, Mapping):
        pairs = [[_data(k), _data(v)] for k, v in value.items()]
        pairs.sort(key=lambda pair: json.dumps(pair[0], ensure_ascii=True, separators=(',', ':')))
        return ['mapping', pairs]
    if is_dataclass(value) and not isinstance(value, type):
        return ['dataclass', type(value).__module__, type(value).__qualname__,
                [[field.name, _data(getattr(value, field.name))] for field in fields(value)]]
    raise ContractError('unsupported packed reference payload')


def pack(value) -> bytes:
    return json.dumps(_data(value), ensure_ascii=True, separators=(',', ':')).encode('ascii')


@dataclass(frozen=True)
class PackedObject:
    spec: ObjectSpec
    payload: bytes


class ReferenceMachineModel:
    model_id = 'packed-reference-payload-v2'
    initializer_id = 'registered-cyclic-rational-initializer-v1'
    residency_dimensions = frozenset(('reference_payload_bytes', 'physical_objects'))
    # Every admitted Compiler control request pays this positive charge before
    # it can mint identities, change revisions or retain failure history.
    control_admission_work = 1

    @staticmethod
    def realize(object_id: str, kind: str, value, provenance: str) -> PackedObject:
        payload = pack(value)
        return PackedObject(ObjectSpec(object_id, kind, {'reference_payload_bytes': len(payload), 'physical_objects': 1}, provenance), payload)

    @staticmethod
    def construction_work(program: Program, rules: SemanticRules) -> int:
        counts = program.counts()
        return counts['nodes']+counts['edges']+counts['slots']+sum(s.delay for s in rules.states)+len(rules.base)+1

    @staticmethod
    def evaluation_work(program: Program, rules: SemanticRules) -> int:
        counts = program.counts()
        # Each repeated weighted SUM edge has a multiply and an addition;
        # source/state reads, PRODUCTs and fixed readout arithmetic are retained.
        return counts['sources']+counts['state_reads']+2*counts['SUM_edges']+counts['PRODUCTs']+3*len(rules.base)+sum(s.delay for s in rules.states)

    @staticmethod
    def observation_work(program: Program) -> int:
        return 5*program.counts()['edges']+3*len(program.heads)+3*program.slot_count+1

    @staticmethod
    def commit_work(program: Program) -> int:
        return 6*program.slot_count+1

    @staticmethod
    def initializer(slot_count: int, pattern: tuple[F, ...]) -> tuple[F, ...]:
        if not pattern:
            raise ContractError('registered initializer pattern cannot be empty')
        pattern = tuple(rational(v, 'registered initializer value') for v in pattern)
        return tuple(pattern[index % len(pattern)] for index in range(slot_count))
