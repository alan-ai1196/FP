"""Integrate the current scoped CPU and actual CUDA Runtime in one fresh clone.

All existing complete CPU batteries run again on the tested target source.
CUDA batteries run serially on the registered board. No old PASS artifact,
partial case or static theorem is substituted for an actual target run.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import time

from audit_reference_release import AUDITS as CPU_AUDITS
from audit_reference_release import MAX_REPORT_BYTES, at, decode_report, gates, git, job_receipts, run_audit

ROOT = Path(__file__).resolve().parents[1]

# Complete sections first, then the minimal result coordinates to retain.
CUDA_AUDITS = {
    'cuda_primitives': ('encodings arithmetic counterexamples dispatch',
        'device encodings arithmetic counterexamples dispatch'),
    'cuda_learner': ('exhaustive profile topology failures',
        'backend_id exhaustive profile topology failures'),
    'cuda_storage': ('registration actual_initial_reservation_classes exhaustive_learners recurrent_profile varied_native_graphs learner_storage extents grid_and_failure escaped_allocation',
        'registration actual_initial_reservation_classes learner_storage extents grid_and_failure escaped_allocation'),
    'cuda_runtime': ('complete_binary_three_event_streams profile search search-exhaustion output-cap prepaid-frame frame-cap unexpected-backend combined-failure malformed-backend unexecuted-endpoint allocation-escape zero-tolerance normalization',
        'complete_binary_three_event_streams independently_replayed_stream_CUDA_phases all_finite_half_exact_widenings_including_zero_sign profile search search-exhaustion malformed-backend unexecuted-endpoint normalization'),
    'cuda_persistence': ('range null scores crossing nontransfer range-admission range-refresh double-round mismatch freshness failed-crossing',
        'range null scores nontransfer range-admission range-refresh double-round mismatch failed-crossing'),
    'cuda_installation': ('small learned recurrent guards late unknown pending corrupt extent continuation byte-cap work-cap no-cpu',
        'small learned recurrent guards corrupt extent continuation byte-cap work-cap no-cpu'),
    'cuda_external_allocations': ('direct_CUDA_allocation_written_and_freed_bytes native_arena_snapshot_unchanged_even_while_foreign_allocation_live',
        'CUDA_build actual_runtime_version direct_CUDA_allocation_written_and_freed_bytes native_arena_snapshot_unchanged_even_while_foreign_allocation_live'),
    'cuda_device': ('runtime driver-api driver capacity role binding foreign query-failure changed unexpected combined snapshot-query-failure snapshot-unexpected snapshot-combined hosted-install',
        'binding foreign query-failure unexpected combined snapshot-query-failure snapshot-unexpected snapshot-combined hosted-install.worker'),
    'cuda_policy_run': ('success learned recurrent no-cpu registration partial search-budget unfinished horizon-budget report-resource report-memory report-device report-unexpected admit-policy-failure install-policy-failure late-frame host_enforcement finite_branches',
        'success learned recurrent no-cpu registration partial search-budget unfinished horizon-budget report-resource report-memory report-device report-unexpected admit-policy-failure install-policy-failure late-frame host_enforcement finite_branches'),
    'cuda_hierarchy': ('cases.hierarchy cases.wrong-majority cases.disconnected-a cases.disconnected-b cases.sum-tie disconnected_witness common_actual_device',
        'cases.hierarchy cases.wrong-majority cases.disconnected-a cases.disconnected-b cases.sum-tie disconnected_witness common_actual_device'),
}

TARGET_GATES = {
    13: ('cuda_runtime', 'cuda_persistence', 'cuda_installation', 'cuda_policy_run'),
    16: ('cuda_primitives', 'cuda_learner', 'cuda_runtime', 'cuda_persistence'),
    20: ('cuda_installation', 'cuda_policy_run'),
    28: ('cuda_persistence', 'cuda_policy_run'),
    29: ('cuda_learner', 'cuda_runtime', 'cuda_persistence'),
    30: ('cuda_runtime', 'cuda_installation', 'cuda_policy_run'),
}


def cuda_report(payload):
    """Existing CUDA scripts emit bounded progress lines then one JSON object."""
    offset = payload.find(b'{')
    if offset < 0:
        raise ValueError('target audit omitted its complete JSON report')
    prefix = payload[:offset].decode('ascii')
    if any(not re.fullmatch(r'[A-Za-z0-9 _-]+ PASS', line) for line in prefix.splitlines()):
        raise ValueError('unrecognized target audit output before its report')
    return decode_report(payload[offset:])


def validate_cuda(name, report):
    if type(report) is not dict or report.get('status') != 'PASS':
        raise ValueError(f'{name}: failed or incomplete target report')
    for path in CUDA_AUDITS[name][0].split():
        at(report, path)
    required = {
        'cuda_primitives': {'encodings.all_finite_half_raw_roundtrips': 63488},
        'cuda_learner': {'exhaustive.all_binary_context_target_three_event_streams': 64,
            'exhaustive.actual_CUDA_phases': 1024, 'topology.seeded_native_graphs': 24},
        'cuda_storage': {'exhaustive_learners.all_binary_context_target_three_event_streams': 64,
            'learner_storage.actual_tensor_arena_bytes': 16 << 20},
        'cuda_runtime': {'complete_binary_three_event_streams': 64,
            'independently_replayed_stream_CUDA_phases': 1024, 'search.independent_complete_native_members': 35},
        'cuda_persistence': {'null.complete_fair_label_paths': 32, 'null.two_path_conditional_wealth_inequalities': 62},
        'cuda_installation': {'small.native_class_size': 35, 'learned.native_class_size': 774,
            'recurrent.native_class_size': 124, 'continuation.install_cursors': [22, 38]},
        'cuda_external_allocations': {'direct_CUDA_allocation_written_and_freed_bytes': 32 << 20,
            'native_arena_snapshot_unchanged_even_while_foreign_allocation_live': True},
        'cuda_device': {'foreign.foreign_CUDA_bytes': 32 << 20},
        'cuda_policy_run': {'success.install_cursors': [22, 38], 'success.cursor': 60,
            'learned.native_classes': [774], 'recurrent.native_classes': [124],
            'host_enforcement.workers': 32, 'finite_branches.complete_binary_four_event_streams': 16,
            'finite_branches.baseline_selected': 8, 'finite_branches.evidence_unresolved': 8},
        'cuda_hierarchy': {'cases.hierarchy.tokens': 32, 'cases.hierarchy.install_cursors': [330],
            'cases.hierarchy.sealed_at': 622, 'cases.hierarchy.independent_CUDA.phases': 1963,
            'cases.wrong-majority.stage_status': 'UNRESOLVED',
            'cases.sum-tie.actual_AMP_train_context_probability_equalities': 30,
            'disconnected_witness.identical_observable_data_proposal_graph_and_train_objective': True},
    }
    for path, expected in required[name].items():
        actual = at(report, path)
        if type(actual) is not type(expected) or actual != expected:
            raise ValueError(f'{name}: required complete coverage missing at {path}')


def run_cuda_audit(checkout, name):
    started = time.monotonic()
    script = f'scripts/audit_{name}.py'
    print(f'START {script}', file=sys.stderr, flush=True)
    completed = subprocess.run([sys.executable, '-B', script], cwd=checkout,
        capture_output=True, timeout=7200, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONOPTIMIZE=''))
    if completed.returncode:
        raise RuntimeError(f'{script}: exit {completed.returncode}\n{completed.stderr[-8192:].decode("utf-8", "replace")}')
    if len(completed.stdout) > MAX_REPORT_BYTES or len(completed.stderr) > MAX_REPORT_BYTES:
        raise ValueError(f'{script}: oversized audit transport')
    report = cuda_report(completed.stdout)
    validate_cuda(name, report)
    seconds = round(time.monotonic()-started, 2)
    print(f'PASS {script} ({seconds}s)', file=sys.stderr, flush=True)
    return {'status': 'PASS', 'scope': report.get('scope'), 'seconds': seconds,
        'complete_sections': CUDA_AUDITS[name][0].split(),
        'evidence': {path: at(report, path) for path in CUDA_AUDITS[name][1].split()},
        'completed_jobs': job_receipts(report)}


def release(workers):
    if not __debug__ or sys.flags.optimize or os.environ.get('PYTHONOPTIMIZE'):
        raise RuntimeError('all audit assertions must be enabled')
    if sys.platform != 'win32' or platform.architecture()[0] != '64bit':
        raise RuntimeError('the registered target includes actual 64-bit Windows enforcement')
    source = git(ROOT, 'rev-parse', 'HEAD')
    if git(ROOT, 'status', '--porcelain', '--untracked-files=no'):
        raise RuntimeError('commit the reviewable target source before release integration')
    if git(ROOT, 'show', f'{source}:scripts/audit_cuda_release.py').replace('\r\n', '\n') != Path(__file__).read_text(encoding='utf-8').strip():
        raise RuntimeError('running target release driver differs from its declared source')
    started = datetime.now(timezone.utc).isoformat()
    with tempfile.TemporaryDirectory(prefix='fp-cuda-release-', dir=ROOT) as temporary:
        assert Path(temporary).resolve().parent == ROOT
        checkout = Path(temporary).resolve()/'repository'
        subprocess.run(['git', 'clone', '--quiet', '--no-hardlinks', '--no-checkout', str(ROOT), str(checkout)], check=True)
        subprocess.run(['git', '-c', 'core.safecrlf=false', 'checkout', '--quiet', '--detach', source], cwd=checkout, check=True)
        if git(checkout, 'rev-parse', 'HEAD') != source or git(checkout, 'status', '--porcelain'):
            raise RuntimeError('target checkout is not the declared clean revision')
        reference_map = gates(checkout)
        if {i for i, row in reference_map.items() if 'T' in row['mode']} != set(TARGET_GATES):
            raise ValueError('held target obligations differ from the executed integration map')
        if any(name not in CUDA_AUDITS for names in TARGET_GATES.values() for name in names):
            raise ValueError('a mapped target executable is missing from integration')
        code = ('import sys,pkgutil,importlib,json; from pathlib import Path; '
            'root=Path.cwd(); sys.path.insert(0,str(root/"src/reference_compiler")); '
            'import fp_reference; names=sorted(m.name for m in pkgutil.walk_packages(fp_reference.__path__,fp_reference.__name__+".")); '
            '[importlib.import_module(n) for n in names]; '
            'assert "torch" not in sys.modules; '
            'assert all(Path(sys.modules[n].__file__).resolve().is_relative_to(root) for n in names); '
            'print(json.dumps(names))')
        modules = json.loads(subprocess.check_output([sys.executable, '-B', '-c', code], cwd=checkout))
        if len(modules) != 38:
            raise RuntimeError('review changed complete package coverage before target release')
        results, errors = {}, []
        # CPU tasks can overlap one another. Actual target batteries remain
        # serialized; no other target root supplies their numerical history.
        with ThreadPoolExecutor(max_workers=workers) as pool:
            pending = {pool.submit(run_audit, checkout, name): name for name in CPU_AUDITS}
            for name in CUDA_AUDITS:
                try:
                    results[name] = run_cuda_audit(checkout, name)
                except Exception as error:
                    errors.append(f'{name}: {type(error).__name__}: {error}')
                    print(f'FAIL {errors[-1]}', file=sys.stderr, flush=True)
            for future in as_completed(pending):
                name = pending[future]
                try:
                    results[name] = future.result()
                except Exception as error:
                    errors.append(f'{name}: {type(error).__name__}: {error}')
                    print(f'FAIL {errors[-1]}', file=sys.stderr, flush=True)
        if errors:
            raise RuntimeError('target release did not pass:\n'+'\n'.join(errors))
        if git(checkout, 'rev-parse', 'HEAD') != source or git(checkout, 'status', '--porcelain'):
            raise RuntimeError('audit changed its declared source or left untracked artifacts')
        assert Path(temporary).resolve().parent == ROOT
    if git(ROOT, 'rev-parse', 'HEAD') != source or git(ROOT, 'status', '--porcelain', '--untracked-files=no'):
        raise RuntimeError('canonical source changed during target integration; no publication')
    device = results['cuda_hierarchy']['evidence']['common_actual_device']
    if results['cuda_device']['evidence']['binding']['actual_identity'] != device['identity']:
        raise ValueError('actual bound device differs between target binding and hierarchical execution')
    return {'status': 'PASS', 'scope': 'complete integration of the registered Reference/CPU and actual half/single CUDA Runtime paths',
        'source_commit': source, 'reference_prerequisite_source': 'ebe2c4cf23f296fe517d4fe237cef45eaa98d309',
        'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
        'machine': 'packed-reference-payload-v9', 'python': sys.version, 'platform': platform.platform(),
        'fresh_clone': {'no_hardlinks': True, 'clean_before_and_after': True,
            'all_package_modules_import_without_torch': True, 'imported_modules': modules},
        'audit_count': len(results), 'CPU_audits': {name: results[name] for name in CPU_AUDITS},
        'CUDA_audits': {name: results[name] for name in CUDA_AUDITS},
        'reference_gate_map': reference_map, 'executed_target_components': TARGET_GATES,
        'shared_target_resource_evidence': ['cuda_storage', 'cuda_external_allocations', 'cuda_device', 'cuda_policy_run'],
        'hierarchy_and_identification_controls': 'cuda_hierarchy', 'actual_device': device,
        'not_claimed': ['every legal registration or future stream has been tested',
            'CERTIFIED_COMPLETE or arbitrary target strategy/parameter optimality',
            'static theorem rows are newly executed target tests', 'unregistered fusion, reduction orders or other devices',
            'tight FP VRAM peak, GPU instruction/time cap, all-system memory or cross-root statistical family authority',
            'population identification, necessary hierarchy, model quality or performance superiority']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, choices=range(1, 9), default=4)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = release(args.workers)
    if args.write:
        (ROOT/'evidence/minimal/FP_CUDA_RELEASE_AUDIT.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
