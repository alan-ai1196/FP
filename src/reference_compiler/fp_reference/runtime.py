"""Authority-owned Runtime recovery: native construction and reference residency.

This restores the first executable segment of the complete endpoint. Search,
observation/learning, query/persistence, actual AMP and install integration are
not implemented yet. Consequently this endpoint never issues CERTIFIED_COMPLETE
or accepts helper certificates as installation authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
import secrets
from typing import Mapping

from .core import ContractError, freeze_data, natural, stable_hash
from .machine import PackedObject, ReferenceMachineModel
from .program import Program, SemanticRules, rational
from .resources import CostRouter, ResourceExceeded, ResourceLedger, ResourceLimits
from .semantics import ArithmeticUnresolved, RangeBound, enclose, reset_delayed


@dataclass(frozen=True)
class ConstructionContract:
    """The enforced construction slice of ERC-1, not its complete run manifest."""
    semantics: SemanticRules
    limits: ResourceLimits
    work_roles: Mapping[str, str]
    graph_limits: Mapping[str, int]
    initializer_pattern: tuple[F, ...]
    normalizer_cap: F
    activation_cap: F
    reference_integer_bits: int
    source_domain: tuple[tuple[F, ...], ...] | None = None

    def __post_init__(self):
        if type(self.semantics) is not SemanticRules or type(self.limits) is not ResourceLimits:
            raise ContractError('immutable semantic and resource declarations required')
        if set(self.limits.role_residency) != {'deployment', 'compiler'}:
            raise ContractError('deployment and compiler resource roles must stay distinct')
        if set(self.limits.global_residency) != ReferenceMachineModel.residency_dimensions:
            raise ContractError('the recovered machine measures packed reference payloads, not total host/GPU memory')
        if set(self.work_roles) != {'construct', 'range_audit'} or any(role not in self.limits.role_cumulative for role in self.work_roles.values()):
            raise ContractError('construction and range-audit work roles must be fixed before execution')
        if any('work' not in caps for caps in self.limits.role_cumulative.values()):
            raise ContractError('every work role requires its cumulative work cap')
        required = {'nodes', 'SUMs', 'PRODUCTs', 'edges', 'slots'}
        if set(self.graph_limits) != required:
            raise ContractError('declare every separate native graph budget')
        object.__setattr__(self, 'graph_limits', freeze_data({key: natural(value, key) for key, value in self.graph_limits.items()}))
        object.__setattr__(self, 'work_roles', freeze_data(self.work_roles))
        pattern = tuple(rational(v, 'registered initializer') for v in self.initializer_pattern)
        if not pattern:
            raise ContractError('registered initializer pattern is empty')
        object.__setattr__(self, 'initializer_pattern', pattern)
        object.__setattr__(self, 'normalizer_cap', rational(self.normalizer_cap, 'normalizer cap', positive=True))
        object.__setattr__(self, 'activation_cap', rational(self.activation_cap, 'activation cap', positive=True))
        natural(self.reference_integer_bits, 'exact reference integer work limit', positive=True)
        if self.source_domain is not None:
            domain = tuple(tuple(rational(v, 'declared source-domain value') for v in row) for row in self.source_domain)
            if not domain or any(len(row) != len(self.semantics.sources) for row in domain):
                raise ContractError('complete nonempty source-domain rows required')
            if any(v > spec.upper for row in domain for v, spec in zip(row, self.semantics.sources)):
                raise ContractError('declared source domain exceeds its source ranges')
            object.__setattr__(self, 'source_domain', domain)


@dataclass(frozen=True)
class ConstructedState:
    candidate_id: str
    physical_owner: str
    program_id: str
    birth_cursor: int
    theta: tuple[F, ...]
    delayed: tuple[tuple[str, tuple[F, ...]], ...]
    range_evidence: tuple[RangeBound, ...]
    range_safe: bool
    object_ids: tuple[str, ...]
    initializer_id: str
    machine_id: str


@dataclass(frozen=True)
class ConstructionResult:
    status: str
    candidate_id: str | None
    reason: str


@dataclass(frozen=True)
class RuntimeSnapshot:
    chi: str
    runtime_id: str
    phase: str
    cursor: int
    deployed_id: str
    next_candidate: int
    programs: tuple[tuple[str, Program], ...]
    candidates: tuple[ConstructedState, ...]
    resources: Mapping
    buffers: tuple[tuple[str, bytes], ...]
    attempts: tuple[tuple[str, str, str], ...]


class ReferenceCompilerRuntime:
    recovery_phase = 'native-construction-reference'

    def __init__(self, contract: ConstructionContract, initial_program: Program):
        if type(contract) is not ConstructionContract:
            raise ContractError('registered construction contract required')
        self._contract = contract
        self._chi = stable_hash(('ERC-1 construction recovery', self.recovery_phase,
                                 ReferenceMachineModel.model_id, ReferenceMachineModel.initializer_id, contract))
        self._runtime_id = secrets.token_hex(12)
        self._ledger = ResourceLedger(contract.limits)
        self._router = CostRouter(self._ledger, contract.work_roles)
        self._machine = ReferenceMachineModel()
        self._cursor = 0
        self._next_candidate = 0
        self._programs: dict[str, Program] = {}
        self._candidates: dict[str, ConstructedState] = {}
        self._buffers: dict[str, bytes] = {}
        self._attempts: list[tuple[str, str, str]] = []
        self._deployed_id = ''
        initial = self._construct(initial_program, 'deployment')
        if initial.status != 'BUILT_REFERENCE':
            raise ContractError(f'initial registered reference realization failed: {initial.status}: {initial.reason}')
        self._deployed_id = initial.candidate_id

    @property
    def contract(self):
        return self._contract

    @property
    def chi(self):
        return self._chi

    def _allocate(self, owner: str, objects: tuple[PackedObject, ...]):
        if any(type(obj) is not PackedObject or type(obj.payload) is not bytes or obj.spec.residency != {
                'reference_payload_bytes': len(obj.payload), 'physical_objects': 1} for obj in objects):
            raise ContractError('registered packed-object size disagrees with its actual payload')
        self._ledger.allocate(owner, tuple(obj.spec for obj in objects))
        self._buffers.update((obj.spec.object_id, obj.payload) for obj in objects)

    def _release_owner(self, owner: str):
        self._ledger.close_owner(owner)
        live = self._ledger.snapshot()['objects']
        self._buffers = {key: value for key, value in self._buffers.items() if key in live}

    def _construct(self, program: Program, role: str) -> ConstructionResult:
        number = self._next_candidate
        self._next_candidate += 1
        candidate = f'{self._runtime_id}:candidate:{number}'
        owner = f'{candidate}:owner'
        self._ledger.register_owner(owner, role)
        try:
            # Request inspection is itself an executed, immutable-role debit.
            self._router.charge_work('construct', {'work': 1}, f'{candidate}:inspect')
            if type(program) is not Program:
                raise ContractError('candidate structure must use the native Program grammar')
            if len(program.nodes) > self._contract.graph_limits['nodes'] or program.slot_count > self._contract.graph_limits['slots']:
                raise ContractError('candidate header exceeds a registered native budget')
            counts = program.counts()
            self._router.charge_work('construct', {'work': self._machine.construction_work(program, self._contract.semantics)}, f'{candidate}:construct')
            program.validate(self._contract.semantics)
            if any(counts[key] > cap for key, cap in self._contract.graph_limits.items()):
                raise ContractError('candidate exceeds a registered P/S/edge/slot budget')
            program_id = program.program_id
            delayed = reset_delayed(self._contract.semantics)
            zero = (F(0),)*program.slot_count
            code = self._machine.realize(f'{candidate}:code', 'native_program', program, program_id)
            initial = self._machine.realize(f'{candidate}:zero', 'zero_slot_state', (zero, delayed), program_id)
            self._allocate(owner, (code, initial))
            # The only value path at this recovery stage is this immutable
            # initializer. Callers cannot supply theta, state or physical costs.
            theta = self._machine.initializer(program.slot_count, self._contract.initializer_pattern)
            initialized = self._machine.realize(f'{candidate}:values', 'initialized_reference_state', (theta, delayed), program_id)
            self._router.charge_work('construct', {'work': program.slot_count}, f'{candidate}:registered-initialize')
            self._allocate(owner, (initialized,))
            self._ledger.release(owner, initial.spec.object_id)
            del self._buffers[initial.spec.object_id]
            evidence = []
            rows = (None,) if self._contract.source_domain is None else self._contract.source_domain
            for index, row in enumerate(rows):
                self._router.charge_work('range_audit', {'work': self._machine.evaluation_work(program, self._contract.semantics)}, f'{candidate}:range:{index}')
                point = None if row is None else {spec.source_id: value for spec, value in zip(self._contract.semantics.sources, row)}
                bound = enclose(program, self._contract.semantics, theta, source_point=point,
                                bit_limit=self._contract.reference_integer_bits)
                evidence.append(bound)
            checked = self._machine.realize(f'{candidate}:range', 'range_evidence', tuple(evidence), program_id)
            self._allocate(owner, (checked,))
            safe = all(bound.sufficient(normalizer_cap=self._contract.normalizer_cap, activation_cap=self._contract.activation_cap)
                       for bound in evidence)
            state = ConstructedState(candidate, owner, program_id, self._cursor, theta, delayed,
                                     tuple(evidence), safe, (code.spec.object_id, initialized.spec.object_id, checked.spec.object_id),
                                     self._machine.initializer_id, self._machine.model_id)
            self._candidates[candidate] = state
            self._programs[program_id] = program
            status = 'BUILT_REFERENCE' if safe else 'UNRESOLVED_RANGE'
            reason = 'native construction and fixed-value range bound checked' if safe else 'conservative full-domain range bound does not establish feasibility'
            self._attempts.append((candidate, status, reason))
            return ConstructionResult(status, candidate, reason)
        except (ResourceExceeded, ArithmeticUnresolved) as exc:
            self._release_owner(owner)
            self._attempts.append((candidate, 'UNRESOLVED', str(exc)))
            return ConstructionResult('UNRESOLVED', None, str(exc))
        except ContractError as exc:
            self._release_owner(owner)
            self._attempts.append((candidate, 'REJECTED_ADMISSIBILITY', str(exc)))
            return ConstructionResult('REJECTED_ADMISSIBILITY', None, str(exc))
        except Exception as exc:
            # Programming/backend failures are visible failures, not a fake
            # mathematical rejection. Retire the partial physical build while
            # retaining all spent work/peak and the failed attempt in Omega.
            self._release_owner(owner)
            self._attempts.append((candidate, 'EXECUTION_FAILED', f'{type(exc).__name__}: {exc}'))
            raise

    def construct_candidate(self, program: Program) -> ConstructionResult:
        return self._construct(program, 'compiler')

    def retire_candidate(self, candidate_id: str):
        if candidate_id == self._deployed_id or candidate_id not in self._candidates:
            raise ContractError('cannot retire the deployed or an unknown candidate')
        state = self._candidates.pop(candidate_id)
        self._release_owner(state.physical_owner)
        if not any(other.program_id == state.program_id for other in self._candidates.values()):
            del self._programs[state.program_id]
        self._attempts.append((candidate_id, 'RETIRED', 'explicit release; spent work and peak residency retained'))

    def install(self, candidate_id: str, *unused_authority, **unused_payload) -> ConstructionResult:
        # This method accepts no helper token as a substitute for the still
        # missing complete learning/persistence/AMP/atomic-install chain.
        return ConstructionResult('UNRESOLVED', None, 'complete Runtime continuation, actual AMP, persistence and atomic install are not yet integrated')

    def snapshot(self) -> RuntimeSnapshot:
        return RuntimeSnapshot(self._chi, self._runtime_id, self.recovery_phase, self._cursor,
                               self._deployed_id, self._next_candidate, tuple(self._programs.items()),
                               tuple(self._candidates.values()), self._ledger.snapshot(), tuple(self._buffers.items()), tuple(self._attempts))
