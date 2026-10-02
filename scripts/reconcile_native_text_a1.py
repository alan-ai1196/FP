"""Seal a lost original native A1 attempt without inventing an exit receipt.

This never launches, signals or resumes a process. A stale RUNNING file is not
proof of liveness: compare the actual OS process creation identity. A live
original worker, an inaccessible process or any ambiguous observation refuses.
"""
from ctypes import wintypes as W
from datetime import datetime, timezone
from pathlib import Path
import ctypes as C
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
JOURNAL = ROOT/'evidence/minimal/FP_NATIVE_TEXT_A1.json'


def process_identity(pid):
    if sys.platform != 'win32':
        raise RuntimeError('actual Windows process identity required')
    kernel = C.WinDLL('kernel32', use_last_error=True)
    open_process = kernel.OpenProcess
    open_process.argtypes, open_process.restype = [W.DWORD, W.BOOL, W.DWORD], W.HANDLE
    get_times = kernel.GetProcessTimes
    get_times.argtypes = [W.HANDLE]+[C.POINTER(W.FILETIME)]*4
    get_times.restype = W.BOOL
    close = kernel.CloseHandle
    close.argtypes, close.restype = [W.HANDLE], W.BOOL
    handle = open_process(0x1000, False, pid)  # Query only; no terminate rights.
    if not handle:
        error = C.get_last_error()
        if error == 87:  # ERROR_INVALID_PARAMETER: this PID does not exist.
            return dict(status='PID_ABSENT', process_id=pid)
        raise C.WinError(error)
    try:
        values = [W.FILETIME() for _ in range(4)]
        if not get_times(handle, *(C.byref(v) for v in values)):
            raise C.WinError(C.get_last_error())
        created = values[0].dwLowDateTime+(values[0].dwHighDateTime << 32)
        return dict(status='PID_PRESENT', process_id=pid, creation_100ns=created)
    finally:
        close(handle)


def main():
    original = json.loads(JOURNAL.read_text(encoding='utf-8'))
    if original['status'] != 'RUNNING' or 'job' in original or 'result' in original:
        raise RuntimeError('only the original unsealed launcher receipt may be reconciled')
    path = Path(original['artifact_directory'])/'worker.json'
    payload = path.read_bytes()
    worker = json.loads(payload)
    expected = {key: worker['before'][key] for key in ('process_id', 'creation_100ns')}
    observed = process_identity(expected['process_id'])
    if observed.get('creation_100ns') == expected['creation_100ns']:
        raise RuntimeError('original process identity still exists; poll it, never infer termination')
    if worker['status'] != 'RUNNING' or worker.get('model_score') is not None:
        raise RuntimeError('unexpected worker result requires separate reconciliation')
    # No output, exit status, peak, kill cursor or timeout is inferred from age.
    result = dict(original, status='UNRESOLVED_NATIVE_TEXT_A1', accepted_execution=False,
        result=worker, termination='original worker absent; launcher exit receipt unavailable; interruption cause unknown',
        reconciliation=dict(observed_at_utc=datetime.now(timezone.utc).isoformat(),
            original_launcher_status=original['status'], expected_worker_identity=expected,
            os_process_observation=observed, original_worker_identity_absent=True,
            original_exit_code=None, original_timed_out=None, final_host_peak=None,
            exact_final_cursor=None, last_heartbeat_only=True,
            heartbeat_bytes=len(payload), heartbeat_last_write_utc=datetime.fromtimestamp(
                path.stat().st_mtime, timezone.utc).isoformat(),
            corpus_or_weights_opened=False, process_launched_or_signalled=False))
    temporary = JOURNAL.with_suffix('.reconciled.tmp')
    with temporary.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    temporary.replace(JOURNAL)
    print(json.dumps(dict(status=result['status'], reconciliation=result['reconciliation'],
        latest_heartbeat=worker['latest']), indent=2))


if __name__ == '__main__':
    main()
