"""Deterministic packed reference realization, explicitly short of a GPU model.

`reference_payload_bytes` measures the actual retained packed buffers below;
it does not claim to count the CPython process heap or CUDA allocations. The
target-device machine/AMP integration remains a separate release obligation.
Work debits are conservative reference operation charges, not measured CPU or
GPU time and not lower certificates on physical cost. Exhausting those charges
is therefore UNRESOLVED for any broader physical-resource claim.

realize() prepares an exact typed UTF-8/surrogatepass extent and value. Only
Runtime admits its lease and materializes the buffer; a plan is not residency.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F

from .core import ContractError
from .learner import SIMPLEX_GRADIENT
from .semantics import reset_delayed
from .program import Program, SemanticRules, rational
from .resources import ObjectSpec
from .encoding import pack, packed_size


@dataclass(frozen=True)
class PackedObject:
    spec: ObjectSpec
    payload: bytes


@dataclass(frozen=True)
class PlannedObject:
    """A typed extent/value plan, not a created buffer or a paid lease."""
    spec: ObjectSpec
    value: object


class ReferenceMachineModel:
    model_id = 'packed-reference-payload-v9'
    initializer_id = 'registered-cyclic-rational-initializer-v1'
    residency_dimensions = frozenset(('reference_payload_bytes', 'physical_objects'))
    # Every admitted Compiler control request pays this positive charge before
    # it can mint identities, change revisions or retain failure history.
    control_admission_work = 1
    program_type = Program

    @staticmethod
    def node_count(program):
        return len(program.nodes)

    @staticmethod
    def state_work(program):
        return program.slot_count

    @staticmethod
    def initializer_validation_work(program, spec):
        return len(spec.simplex_slots)+1 if spec is not None and spec.optimizer_id == SIMPLEX_GRADIENT else 0

    @staticmethod
    def zero_payload(program, rules):
        return (F(0),)*program.slot_count, reset_delayed(rules)

    @staticmethod
    def activation_values(prediction):
        return prediction.values

    @staticmethod
    def realize(object_id: str, kind: str, value, provenance: str) -> PlannedObject:
        return PlannedObject(ObjectSpec(object_id, kind,
            {'reference_payload_bytes': packed_size(value), 'physical_objects': 1}, provenance), value)

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
    def commit_work(program: Program, spec=None) -> int:
        if spec is not None and spec.optimizer_id == SIMPLEX_GRADIENT:
            return 12*len(spec.simplex_slots)+2*program.slot_count+8
        return 6*program.slot_count+1

    @staticmethod
    def initializer(slot_count: int, pattern: tuple[F, ...]) -> tuple[F, ...]:
        if not pattern:
            raise ContractError('registered initializer pattern cannot be empty')
        pattern = tuple(rational(v, 'registered initializer value') for v in pattern)
        return tuple(pattern[index % len(pattern)] for index in range(slot_count))
