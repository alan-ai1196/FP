"""One terminal boundary for exhausted allocations in the serialized Runtime.

This is a failure protocol, not a memory meter, allocator or feasibility proof.
The marker is prepared with the trusted code; marking the existing state slots
does not build a diagnostic, copy the root, clean up or refund resources.
"""
from types import FunctionType

from .core import ContractError


HOST_ALLOCATION_FAILURE = ('host-memory', 'host allocation exhausted; retained prefix has no continuation authority')


def _guard(method, *, diagnostic):
    def guarded(self, *args, **kwargs):
        if self._halted is HOST_ALLOCATION_FAILURE and not diagnostic:
            raise ContractError('host allocation exhausted; this Runtime is terminal')
        try:
            return method(self, *args, **kwargs)
        except MemoryError:
            # Existing keys and precreated immutable values only. In particular,
            # no exception formatting, attempted cleanup or new failure record.
            self._halted = HOST_ALLOCATION_FAILURE
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
    """
    for name, method in tuple(vars(runtime).items()):
        if not name.startswith('_') and type(method) is FunctionType:
            setattr(runtime, name, _guard(method, diagnostic=name == 'snapshot'))
    return runtime
