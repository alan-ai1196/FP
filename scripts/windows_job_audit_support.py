"""Bound a disposable audit process before its first instruction on Windows.

SDK job commit accounting is independent evidence, not an ERC-1 manifest or
Compiler authority. The audit launcher is outside the measured child scope.
No breakaway, inherited handles or visible windows are requested; the job
allows only one active process. OS counts can include denied process starts.
"""
import ctypes as C
from ctypes import wintypes as W
from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys


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


class Startup(C.Structure):
    _fields_ = [('size', W.DWORD), ('reserved', W.LPWSTR), ('desktop', W.LPWSTR), ('title', W.LPWSTR)]+[
        (name, W.DWORD) for name in ('x', 'y', 'width', 'height', 'chars_x', 'chars_y', 'fill', 'flags')]+[
        ('show', W.WORD), ('reserved_size', W.WORD), ('reserved_ptr', C.c_void_p),
        ('stdin', W.HANDLE), ('stdout', W.HANDLE), ('stderr', W.HANDLE)]


class Process(C.Structure):
    _fields_ = [('process', W.HANDLE), ('thread', W.HANDLE), ('pid', W.DWORD), ('tid', W.DWORD)]


@dataclass(frozen=True)
class JobRun:
    exit_code: int
    timed_out: bool
    commit_limit: int
    peak_process_commit: int
    peak_job_commit: int
    user_100ns: int
    kernel_100ns: int
    total_processes: int
    limit_terminated_processes: int
    attached_before_resume: bool


def run_in_job(script, arguments=(), *, commit_limit, timeout_ms=60000):
    if sys.platform != 'win32' or C.sizeof(C.c_void_p) != 8:
        raise RuntimeError('this audit requires 64-bit Windows')
    if type(commit_limit) is not int or not 0 < commit_limit < 1 << 63:
        raise ValueError('positive fixed commit cap required')
    kernel = C.WinDLL('kernel32', use_last_error=True)
    def bind(name, result, args):
        fn = getattr(kernel, name)
        fn.restype, fn.argtypes = result, args
        return fn
    create_job = bind('CreateJobObjectW', W.HANDLE, [C.c_void_p, W.LPCWSTR])
    set_job = bind('SetInformationJobObject', W.BOOL, [W.HANDLE, C.c_int, C.c_void_p, W.DWORD])
    query = bind('QueryInformationJobObject', W.BOOL, [W.HANDLE, C.c_int, C.c_void_p, W.DWORD, C.c_void_p])
    create_process = bind('CreateProcessW', W.BOOL, [W.LPCWSTR, W.LPWSTR, C.c_void_p, C.c_void_p,
        W.BOOL, W.DWORD, C.c_void_p, W.LPCWSTR, C.POINTER(Startup), C.POINTER(Process)])
    assign = bind('AssignProcessToJobObject', W.BOOL, [W.HANDLE, W.HANDLE])
    is_in = bind('IsProcessInJob', W.BOOL, [W.HANDLE, W.HANDLE, C.POINTER(W.BOOL)])
    resume = bind('ResumeThread', W.DWORD, [W.HANDLE])
    wait = bind('WaitForSingleObject', W.DWORD, [W.HANDLE, W.DWORD])
    exit_code = bind('GetExitCodeProcess', W.BOOL, [W.HANDLE, C.POINTER(W.DWORD)])
    terminate = bind('TerminateProcess', W.BOOL, [W.HANDLE, W.UINT])
    close = bind('CloseHandle', W.BOOL, [W.HANDLE])
    def checked(ok):
        if not ok:
            raise C.WinError(C.get_last_error())
    job, process = create_job(None, None), Process()
    checked(job)
    try:
        declared = ExtendedLimit()
        # Active process cap + process/job committed memory + kill on close.
        declared.basic.flags = 0x8 | 0x100 | 0x200 | 0x2000
        declared.basic.processes = 1
        declared.process_memory = declared.job_memory = commit_limit
        checked(set_job(job, 9, C.byref(declared), C.sizeof(declared)))
        path = Path(script).resolve()
        command = C.create_unicode_buffer(subprocess.list2cmdline([sys.executable, '-B', str(path), *map(str, arguments)]))
        startup = Startup()
        startup.size = C.sizeof(startup)
        checked(create_process(sys.executable, command, None, None, False, 0x08000004, None,
                               str(path.parent), C.byref(startup), C.byref(process)))
        checked(assign(job, process.process))
        attached = W.BOOL()
        checked(is_in(process.process, job, C.byref(attached)))
        checked(attached.value)
        initial = ExtendedLimit()
        checked(query(job, 9, C.byref(initial), C.sizeof(initial), None))
        if (initial.process_memory != commit_limit or initial.job_memory != commit_limit
                or initial.basic.flags & declared.basic.flags != declared.basic.flags
                or initial.basic.processes != 1):
            raise RuntimeError('job did not retain its preregistered allocation limits')
        if initial.peak_process > commit_limit or initial.peak_job > commit_limit:
            raise RuntimeError('initial process commitment exceeds the declared cap before resumption')
        if resume(process.thread) == 0xffffffff:
            raise C.WinError(C.get_last_error())
        completion = wait(process.process, timeout_ms)
        if completion not in (0, 258):
            raise C.WinError(C.get_last_error())
        timed_out = completion == 258
        if timed_out:
            checked(terminate(process.process, 1223))
            checked(wait(process.process, 10000) == 0)
        code, final, accounting = W.DWORD(), ExtendedLimit(), Accounting()
        checked(exit_code(process.process, C.byref(code)))
        checked(query(job, 9, C.byref(final), C.sizeof(final), None))
        checked(query(job, 1, C.byref(accounting), C.sizeof(accounting), None))
        if final.process_memory != commit_limit or final.job_memory != commit_limit:
            raise RuntimeError('job memory limits changed during execution')
        return JobRun(code.value, timed_out, commit_limit, final.peak_process, final.peak_job,
                      accounting.user_time, accounting.kernel_time, accounting.total_processes,
                      accounting.terminated_processes, True)
    finally:
        # A failed setup never leaves a suspended child behind. Every handle
        # belongs to this audit launch, never to the user/Codex host process.
        if process.process and wait(process.process, 0) == 258:
            terminate(process.process, 1223)
            wait(process.process, 10000)
        if process.thread:
            close(process.thread)
        if process.process:
            close(process.process)
        close(job)
