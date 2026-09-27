"""One terminal boundary for host failures in the serialized Runtime.

This is a failure protocol, not a memory meter, allocator or feasibility proof.
The marker is prepared with the trusted code; marking the existing state slots
does not build a diagnostic, copy the root, clean up or refund resources.
"""
from types import FunctionType

from .core import ContractError
from .host_resources import HostExecutionUnresolved
from .policy import POLICY_EXTERNAL_PORTS
from .cuda_storage import CudaStorageUnresolved
from .token_reporting import REPORT_PORTS


HOST_ALLOCATION_FAILURE = ('host-memory', 'host allocation exhausted; retained prefix has no continuation authority')
HOST_RESOURCE_FAILURE = ('host-resource', 'host resource premises failed; retained prefix has no continuation authority')
CUDA_RESOURCE_FAILURE = ('cuda-resource', 'CUDA storage premises failed; retained prefix has no continuation authority')


def _guard(method, *, diagnostic):
    def guarded(self, *args, **kwargs):
        if (self._halted is HOST_ALLOCATION_FAILURE or self._halted is HOST_RESOURCE_FAILURE
                or self._halted is CUDA_RESOURCE_FAILURE) and not diagnostic:
            raise ContractError('host execution failed; this Runtime is terminal')
        if self._run_closure is not None and not diagnostic:
            raise ContractError('the registered run is sealed; retained evidence has no continuation authority')
        if self._token_report is not None and not diagnostic and method.__name__ not in REPORT_PORTS:
            raise ContractError('terminal reporting permanently freezes all learning and Compiler ports')
        if (self._policy_contract is not None and not self._policy_running
                and method.__name__ not in POLICY_EXTERNAL_PORTS):
            raise ContractError('the registered Runtime strategy owns all Compiler control and authority ports')
        try:
            if self._cuda is not None and not diagnostic:
                self._cuda.check()
            if self._host is not None:
                # Entry check only. The registered job enforces allocations
                # throughout the body; no allocating post-check is added after
                # the CPU transaction's sole publication point.
                self._host.observe()
            result = method(self, *args, **kwargs)
            if method.__name__ == 'observe' and self._policy_contract is not None and result.status == 'OBSERVED_REFERENCE':
                # A separate owned post-commit phase, outside observe's failed
                # target handler. No policy transition is an exogenous event.
                self._advance_policy()
                self._seal_run()
            return result
        except MemoryError:
            # Existing keys and precreated immutable values only. In particular,
            # no exception formatting, attempted cleanup or new failure record.
            if self._halted is not HOST_ALLOCATION_FAILURE and self._halted is not HOST_RESOURCE_FAILURE:
                self._halted = HOST_ALLOCATION_FAILURE
            self._event_phase = 'halted'
            raise
        except HostExecutionUnresolved:
            # A failed diagnostic cannot replace the first host halt cause.
            if self._halted is not HOST_ALLOCATION_FAILURE and self._halted is not HOST_RESOURCE_FAILURE:
                self._halted = HOST_RESOURCE_FAILURE
            self._event_phase = 'halted'
            raise
        except CudaStorageUnresolved:
            if self._halted is None:
                self._halted = CUDA_RESOURCE_FAILURE
            self._event_phase = 'halted'
            raise
        except Exception:
            # A failed native binding must retain the original unexpected
            # exception while ending current authority on the device root.
            if self._cuda is not None and self._cuda.arena._failure is not None:
                if self._halted is None:
                    self._halted = CUDA_RESOURCE_FAILURE
                self._event_phase = 'halted'
            raise
    # Keep readable public names without publishing a __wrapped__ bypass.
    guarded.__name__, guarded.__qualname__, guarded.__doc__ = method.__name__, method.__qualname__, method.__doc__
    return guarded


def guard_host_allocations(runtime):
    """Register every public method; snapshots remain passive diagnostics.

    Constructor failure cannot return a Runtime. Immutable contract/identity
    properties carry no continuation authority. Private methods are not ports.
    Internal broad exception handlers must let MemoryError escape untouched.
    A registered host also has its live resource premises checked on entry.
    """
    for name, method in tuple(vars(runtime).items()):
        if not name.startswith('_') and type(method) is FunctionType:
            setattr(runtime, name, _guard(method, diagnostic=name == 'snapshot'))
    return runtime
