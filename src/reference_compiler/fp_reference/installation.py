"""Registered CPU installation and passive audit records, with no signer.

Runtime executes the transaction from owned proposal/evidence identities.
None of these dataclasses can authorize a supplied state or target AMP path.
"""
from dataclasses import dataclass, field

from .core import ContractError


@dataclass(frozen=True)
class CpuInstallContract:
    work_role: str = 'deployment'
    workspace_role: str = 'deployment'
    machine_transition: str = field(default='serialized-cpython-root-and-lease-transfer-v1', init=False)
    proposal: str = field(default='owned-constructor-class-winner-before-fresh-evidence-v1', init=False)
    transport: str = field(default='preserve-complete-learners-and-existing-buffers-v1', init=False)
    shadow_policy: str = field(default='retain-all-demote-old-base-v1', init=False)
    search_policy: str = field(default='stop-all-retain-frontier-and-evidence-v1', init=False)
    persistence_policy: str = field(default='invalidate-all-no-rebase-no-refund-v1', init=False)

    def __post_init__(self):
        if (type(self.work_role) is not str or type(self.workspace_role) is not str
                or self.work_role not in ('deployment', 'compiler') or self.workspace_role not in ('deployment', 'compiler')):
            raise ContractError('installation uses preregistered physical/work roles')
        policies = {
            'machine_transition': 'serialized-cpython-root-and-lease-transfer-v1',
            'proposal': 'owned-constructor-class-winner-before-fresh-evidence-v1',
            'transport': 'preserve-complete-learners-and-existing-buffers-v1',
            'shadow_policy': 'retain-all-demote-old-base-v1',
            'search_policy': 'stop-all-retain-frontier-and-evidence-v1',
            'persistence_policy': 'invalidate-all-no-rebase-no-refund-v1',
        }
        if any(type(getattr(self, key)) is not str or getattr(self, key) != value for key, value in policies.items()):
            raise ContractError('unimplemented CPU install policy or machine transition')


@dataclass(frozen=True)
class CpuInstallAttempt:
    attempt_id: str
    cursor: int
    old_deployed_id: str
    target_id: str
    proposal_proof_id: str
    reference_identity: str
    float64_identity: str
    status: str
    reason: str = ''


@dataclass(frozen=True)
class CpuInstallReceipt:
    attempt: CpuInstallAttempt
    revision_before: int
    revision_after: int
    candidates_before: tuple
    candidates_after: tuple
    ownership_moves: tuple[tuple[str, str, str, int], ...]
    releases: tuple[tuple[str, str, int], ...]
    closed_owners: tuple[str, ...]
    invalidated_persistence: tuple[str, ...]
    stopped_searches: tuple[str, ...]
    object_id: str


@dataclass(frozen=True)
class CpuInstallResult:
    status: str
    attempt_id: str | None
    candidate_id: str | None
    cursor: int
    reason: str
    authority_scope: str = field(default='executed serialized CPU installation only; no current global optimum, target AMP or complete ERC-1 release', init=False)
