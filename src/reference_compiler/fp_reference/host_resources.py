"""Live Windows process/job commitment, separate from packed object measures.

The fixed shared process arena is charged in full to deployment and compiler, once
globally. This is process/job commit accounting, not total-machine memory.
No caller-supplied sample or native handle can bind a Runtime to this backend.
"""
import ctypes as C
from ctypes import wintypes as W
from dataclasses import dataclass, field
import sys
from typing import Mapping

from .core import ContractError, freeze_data, natural


class HostExecutionUnresolved(RuntimeError):
    """The actual host no longer establishes its registered resource premises."""


@dataclass(frozen=True)
class HostResourceContract:
    commit_cap: int
    role_commit_caps: Mapping[str, int]
    backend: str = field(default='windows-x64-current-process-job-commit-v1', init=False)
    ownership: str = field(default='whole-process-arena-shared-by-deployment-and-compiler-v1', init=False)
    cpu_measure: str = field(default='process-and-job-user-kernel-100ns-observations-v1', init=False)

    def __post_init__(self):
        natural(self.commit_cap, 'host commitment cap', positive=True)
        if not isinstance(self.role_commit_caps, Mapping) or set(self.role_commit_caps) != {'deployment', 'compiler'}:
            raise ContractError('host arena requires both fixed resource roles')
        caps = {role: natural(cap, 'host role commitment cap', positive=True) for role, cap in self.role_commit_caps.items()}
        if max(self.commit_cap, *caps.values()) >= 1 << 63:
            raise ContractError('host commitment cap exceeds the registered native integer domain')
        object.__setattr__(self, 'role_commit_caps', freeze_data(caps))
        if (self.backend != 'windows-x64-current-process-job-commit-v1'
                or self.ownership != 'whole-process-arena-shared-by-deployment-and-compiler-v1'
                or self.cpu_measure != 'process-and-job-user-kernel-100ns-observations-v1'):
            raise ContractError('unimplemented host resource policy')

    @property
    def enforced_cap(self):
        return min(self.commit_cap, *self.role_commit_caps.values())


@dataclass(frozen=True)
class HostResourceObservation:
    contract: HostResourceContract
    process_id: int
    creation_100ns: int
    process_commit: int
    lifetime_process_commit_peak: int
    job_commit_peak: int
    process_user_100ns: int
    process_kernel_100ns: int
    job_user_100ns: int
    job_kernel_100ns: int
    total_job_processes: int

    @property
    def process_identity(self):
        return self.process_id, self.creation_100ns

    @property
    def role_current(self):
        return freeze_data({role: self.process_commit for role in self.contract.role_commit_caps})

    @property
    def role_peak(self):
        return freeze_data({role: self.lifetime_process_commit_peak for role in self.contract.role_commit_caps})

    @property
    def role_cpu(self):
        return freeze_data({role: {'user_100ns': self.process_user_100ns, 'kernel_100ns': self.process_kernel_100ns}
                            for role in self.contract.role_commit_caps})


class BasicLimit(C.Structure):
    _fields_ = [('process_time', C.c_int64), ('job_time', C.c_int64), ('flags', W.DWORD),
                ('min_ws', C.c_size_t), ('max_ws', C.c_size_t), ('processes', W.DWORD),
                ('affinity', C.c_size_t), ('priority', W.DWORD), ('scheduling', W.DWORD)]


class IoCounters(C.Structure):
    _fields_ = [(name, C.c_uint64) for name in ('read_ops', 'write_ops', 'other_ops', 'read_bytes', 'write_bytes', 'other_bytes')]


class ExtendedLimit(C.Structure):
    _fields_ = [('basic', BasicLimit), ('io', IoCounters), ('process_memory', C.c_size_t),
                ('job_memory', C.c_size_t), ('peak_process', C.c_size_t), ('peak_job', C.c_size_t)]


class Accounting(C.Structure):
    _fields_ = [(name, C.c_int64) for name in ('user_time', 'kernel_time', 'period_user_time', 'period_kernel_time')]+[
        (name, W.DWORD) for name in ('page_faults', 'total_processes', 'active_processes', 'terminated_processes')]


class ProcessMemory(C.Structure):
    _fields_ = [('size', W.DWORD), ('page_faults', W.DWORD)]+[(name, C.c_size_t) for name in (
        'peak_working_set', 'working_set', 'peak_paged', 'paged', 'peak_nonpaged', 'nonpaged',
        'pagefile', 'peak_pagefile', 'private')]


def _ticks(value):
    return value.dwLowDateTime+(value.dwHighDateTime << 32)


class _WindowsProcessHost:
    """Runtime-owned immutable binding; counters belong to the actual kernel."""
    def __init__(self, contract):
        if type(contract) is not HostResourceContract:
            raise ContractError('host registration requires policy data, never supplied observations or callbacks')
        contract.__post_init__()
        if sys.platform != 'win32' or C.sizeof(C.c_void_p) != 8 or sys.implementation.name != 'cpython':
            raise HostExecutionUnresolved('the registered host requires 64-bit Windows CPython')
        self.contract = contract
        kernel = C.WinDLL('kernel32', use_last_error=True)
        def bind(name, result, args):
            fn = getattr(kernel, name)
            fn.restype, fn.argtypes = result, args
            return fn
        self._current = bind('GetCurrentProcess', W.HANDLE, [])
        self._pid = bind('GetCurrentProcessId', W.DWORD, [])
        self._query = bind('QueryInformationJobObject', W.BOOL, [W.HANDLE, C.c_int, C.c_void_p, W.DWORD, C.c_void_p])
        self._memory = bind('K32GetProcessMemoryInfo', W.BOOL, [W.HANDLE, C.c_void_p, W.DWORD])
        self._times = bind('GetProcessTimes', W.BOOL, [W.HANDLE]+[C.POINTER(W.FILETIME)]*4)
        self._identity = None
        self._identity = self.observe().process_identity

    def observe(self):
        limits, accounting, memory = ExtendedLimit(), Accounting(), ProcessMemory()
        memory.size = C.sizeof(memory)
        created, exited, kernel_time, user_time = (W.FILETIME() for _ in range(4))
        process = self._current()
        # NULL identifies this process's actual immediate job; there is no
        # caller-selected cheap/unrelated job handle or observation channel.
        calls = (
            self._query(None, 9, C.byref(limits), C.sizeof(limits), None),
            self._query(None, 1, C.byref(accounting), C.sizeof(accounting), None),
            self._memory(process, C.byref(memory), C.sizeof(memory)),
            self._times(process, C.byref(created), C.byref(exited), C.byref(kernel_time), C.byref(user_time)),
        )
        if not all(calls):
            raise HostExecutionUnresolved('kernel cannot establish the actual host resource observation')
        cap, required = self.contract.enforced_cap, 0x8 | 0x100 | 0x200 | 0x2000
        if (limits.basic.flags & required != required or limits.basic.flags & (0x800 | 0x1000)
                or limits.basic.processes != 1 or limits.process_memory != cap or limits.job_memory != cap):
            raise HostExecutionUnresolved('actual host job limits differ from immutable registration')
        if max(memory.private, memory.peak_pagefile, limits.peak_process, limits.peak_job) > cap:
            raise HostExecutionUnresolved('lifetime host commitment exceeds its registered shared arena')
        result = HostResourceObservation(self.contract, self._pid(), _ticks(created), memory.private,
            memory.peak_pagefile, limits.peak_job, _ticks(user_time), _ticks(kernel_time),
            accounting.user_time, accounting.kernel_time, accounting.total_processes)
        if self._identity is not None and result.process_identity != self._identity:
            raise HostExecutionUnresolved('the owning host process identity changed')
        return result
