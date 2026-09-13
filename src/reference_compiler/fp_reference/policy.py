"""A registered Compiler strategy over complete native classes, never graphs.

These immutable declarations and passive records carry no authority. Runtime
owns the strategy's execution, search/evidence handles and publication state.
"""
from dataclasses import dataclass, field

from .core import ContractError, natural
from .persistence import REFERENCE_PATH, FLOAT64_PATH, CUDA_PATH
from .program import name


@dataclass(frozen=True)
class CompilationStep:
    after_cursor: int
    search_name: str
    search_transitions: int
    reference_rule: str
    float64_rule: str

    def __post_init__(self):
        natural(self.after_cursor, 'earliest ordinary compilation boundary', positive=True)
        natural(self.search_transitions, 'fixed native search step budget', positive=True)
        for key in ('search_name', 'reference_rule', 'float64_rule'):
            name(getattr(self, key), key)

    @property
    def physical_rule(self):
        return self.float64_rule


@dataclass(frozen=True)
class CudaCompilationStep:
    after_cursor: int
    search_name: str
    search_transitions: int
    reference_rule: str
    cuda_rule: str

    def __post_init__(self):
        natural(self.after_cursor, 'earliest ordinary compilation boundary', positive=True)
        natural(self.search_transitions, 'fixed native search step budget', positive=True)
        for key in ('search_name', 'reference_rule', 'cuda_rule'):
            name(getattr(self, key), key)

    @property
    def physical_rule(self):
        return self.cuda_rule


def _validate_schedule(steps, online, path):
    searches = {s.search_name for s in online.searches}
    if online.persistence is None:
        raise ContractError('compilation requires registered fresh path-specific evidence')
    rules = {r.rule_id: r for r in online.persistence.rules}
    for step in steps:
        if (step.after_cursor % online.learner.update_unit
                or step.after_cursor > len(online.data.active.observation_ids)):
            raise ContractError('compilation must start at a possible complete optimizer boundary')
        if step.search_name not in searches:
            raise ContractError('strategy selects an unregistered native decision class')
        a, b = rules.get(step.reference_rule), rules.get(step.physical_rule)
        if (a is None or b is None or a.score_path != REFERENCE_PATH or b.score_path != path
                or (a.epoch_events, a.max_epochs) != (b.epoch_events, b.max_epochs)):
            raise ContractError('strategy requires a registered pair of same-schedule path-specific rules')


@dataclass(frozen=True)
class CompilerPolicy:
    steps: tuple[CompilationStep, ...]
    driver: str = field(default='sequential-native-search-proposal-paired-cpu-install-v2', init=False)

    def __post_init__(self):
        steps = tuple(self.steps)
        if any(type(step) is not CompilationStep for step in steps):
            raise ContractError('immutable native compilation stages are required')
        if any(a.after_cursor > b.after_cursor for a, b in zip(steps, steps[1:])):
            raise ContractError('registered compilation boundaries must be ordered')
        if self.driver != 'sequential-native-search-proposal-paired-cpu-install-v2':
            raise ContractError('unimplemented Compiler strategy')
        object.__setattr__(self, 'steps', steps)

    def validate(self, online):
        self.__post_init__()
        if online is None:
            raise ContractError('the strategy requires registered ordinary event execution')
        if not self.steps:
            return  # The closed ordinary baseline has no compilation actions.
        if online.cpu_install is None:
            raise ContractError('the registered strategy requires the complete CPU search/evidence/install path')
        _validate_schedule(self.steps, online, FLOAT64_PATH)


@dataclass(frozen=True)
class CudaCompilerPolicy:
    steps: tuple[CudaCompilationStep, ...]
    driver: str = field(default='sequential-native-search-proposal-paired-cuda-install-v2', init=False)

    def __post_init__(self):
        steps = tuple(self.steps)
        if any(type(step) is not CudaCompilationStep for step in steps):
            raise ContractError('immutable CUDA compilation stages are required')
        if any(a.after_cursor > b.after_cursor for a, b in zip(steps, steps[1:])):
            raise ContractError('registered compilation boundaries must be ordered')
        if self.driver != 'sequential-native-search-proposal-paired-cuda-install-v2':
            raise ContractError('unimplemented Compiler strategy')
        object.__setattr__(self, 'steps', steps)

    def validate(self, online):
        self.__post_init__()
        if online is None:
            raise ContractError('the strategy requires registered ordinary event execution')
        if self.steps:
            _validate_schedule(self.steps, online, CUDA_PATH)


TERMINAL_STAGES = frozenset(('INSTALLED_CPU', 'INSTALLED_CUDA', 'BASELINE_SELECTED', 'UNRESOLVED'))


@dataclass(frozen=True)
class CompilationState:
    status: str = 'WAITING'
    started_cursor: int | None = None
    ended_cursor: int | None = None
    search_id: str | None = None
    candidate_id: str | None = None
    proof_id: str | None = None
    reference_identity: str | None = None
    float64_identity: str | None = None
    install_attempt: str | None = None
    reason: str = ''

    @property
    def physical_identity(self):
        return self.float64_identity


@dataclass(frozen=True)
class CudaCompilationState:
    status: str = 'WAITING'
    started_cursor: int | None = None
    ended_cursor: int | None = None
    search_id: str | None = None
    candidate_id: str | None = None
    proof_id: str | None = None
    reference_identity: str | None = None
    cuda_identity: str | None = None
    install_attempt: str | None = None
    reason: str = ''

    @property
    def physical_identity(self):
        return self.cuda_identity


@dataclass(frozen=True)
class CompilerPolicyState:
    stages: tuple[CompilationState | CudaCompilationState, ...]
    generation: int
    object_id: str


@dataclass(frozen=True)
class CompilerPolicySnapshot:
    registration: CompilerPolicy | CudaCompilerPolicy
    state: CompilerPolicyState
    executing: bool


# The owned strategy accepts only exogenous event transport and passive
# snapshots from its caller. All future authority/control methods default
# to denied as well; no caller can supply a search winner or fresh rule choice.
POLICY_EXTERNAL_PORTS = frozenset(('begin_context', 'receive_context', 'finish_context',
                                  'predict_next', 'observe', 'snapshot'))
