"""Run the complete scoped Reference release battery in one clean Git clone.

The result identifies tested source, executable obligations and held target
gates. It is release evidence, never a Runtime token or an AMP certificate.
Frozen scoped theorems are retained as premises, not counted as new tests.
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

ROOT = Path(__file__).resolve().parents[1]
MAX_REPORT_BYTES = 256 << 10

# Every entry runs the script's complete default battery. Required paths stop
# a partial/empty PASS report from standing in for the intended executable.
# Longer CPU cases start first; independent processes never share a Runtime.
AUDITS = {
    'owned_compiler_policy': ('registration success learned exhaustive failures bounded',
        'success.native_class_sizes success.installed_at_cursors learned.native_class_sizes learned.installed_at_cursors exhaustive'),
    'cpu_installation': ('ledger success learned failures capacity continuation',
        'ledger.independent_complete_lease_cases success.complete_native_class_programs learned.complete_native_class_programs learned.independent_continuous_binary64_phase_checks continuation.install_cursors'),
    'reference_model_check': ('counts seed distinct_class_shapes selected_cases', 'counts distinct_class_shapes seed'),
    'reference_search': ('grammar runtime compound recurrent adversaries',
        'grammar.independent_complete_classes runtime.complete_profile_constructor_programs compound.complete_native_programs recurrent.complete_delayed_binding_programs'),
    'reference_acceleration': ('cases.upper_audit cases.baseline_exhaustive cases.connected_assignments cases.profiles cases.identification_limits cases.unresolved_cases cases.authority_adversaries cases.range_residency cases.bounded',
        'cases.upper_audit cases.baseline_exhaustive cases.identification_limits cases.bounded'),
    'reference_construction': ('boundary_checks ownership_model_check',
        'existing_resource_fixture_graphs random_shared_native_graphs independent_exact_full_context_comparisons ownership_model_check.steps'),
    'reference_events': ('gradient_audit exhaustive_endpoint clock_data_boundaries causality query_precision failure_prefixes existing_value_path',
        'gradient_audit.independent_exact_gradient_vectors exhaustive_endpoint.streams exhaustive_endpoint.individual_optimizer_commits causality.exact_causal_source_rows'),
    'reference_profiles': ('existing_value_path exhaustive_replay recurrent_attachment adversaries',
        'existing_value_path.actual_profile_predictions_and_observations exhaustive_replay recurrent_attachment.recurrent_profile_events'),
    'reference_numerics': ('logarithm floor comparison adversaries',
        'logarithm.exact_formula_and_nested_tail_cases floor.exact_grid_and_monotonicity_cases comparison.exact_signed_order_cases'),
    'binary_arithmetic': ('rounding counterexamples limits actual failures',
        'rounding.signed_exact_nearest_point_comparisons actual.successful_actual_scalar_comparisons actual.actual_overflow_cases_unresolved'),
    'float64_runtime': ('exhaustive profiles normalization failures crossing',
        'exhaustive.independent_bitwise_phase_checks exhaustive.actual_finite_coordinates_differing_from_recast_exact_endpoints profiles.profile_and_initial_prefix_phase_checks profiles.recurrent_phase_checks'),
    'persistence_kernel': ('invalid_registration_or_argument_cases pointwise_floor_bound_and_threshold_cases exact_conditional_null_trees global_error_composition reproduced_unsound_shortcuts',
        'pointwise_floor_bound_and_threshold_cases global_error_composition'),
    'reference_persistence': ('scores crossing null freshness failures',
        'null.complete_fair_label_paths null.exact_conditional_lower_wealth_inequalities null.first_crossing_probability freshness.global_allocated_alpha'),
    'paired_cpu_persistence': ('range scores nontransfer null failures freshness',
        'range.independent_direct_float_context_checks scores.independent_four_trajectory_phase_checks nontransfer null.complete_fair_label_paths'),
    'context_ingress': ('codec chunking admission failures filtration',
        'chunking.all_legal_chunkings chunking.equal_prefix_complete_snapshot_checks admission.unchanged_unfunded_denials filtration.locked_action_prefix_positions'),
    'owned_encoding': ('identity encoding planned workspace',
        'identity.complete_unicode_native_class_programs encoding.independent_packed_tree_checks encoding.all_single_BMP_codepoints'),
    'control_admission': ('history endpoints trees authority ingress',
        'trees.complete_four_command_trees trees.endpoint_positions authority.complete_program_class'),
    'host_allocation_failure': ('history ports prefixes os',
        'ports.guarded_continuation_or_authority_ports ports.repeated_terminal_refusals ports.internal_allocation_failures_bypass_broad_handlers'),
    'bound_host_runtime': ('cases.binding cases.memory cases.install cases.late-fence cases.failed-exit',
        'cases.install.complete_native_class_programs cases.late-fence.low_current_memory_cannot_erase_prior_peak cases.failed-exit.completed_looking_child_file_not_accepted_as_run_success'),
    'reference_run': ('cases.registration cases.finite_streams cases.installed cases.failures cases.bounded',
        'cases.finite_streams cases.installed'),
    'recovered_authorities': ('source_commit upper_evidence_accepted_as_equivalence skipped_event_accepted same_cursor_unexecuted_state_replacement_accepted dead_session_authorization_accepted',
        'source_commit interpretation'),
}


def git(root, *args):
    return subprocess.check_output(['git', '-c', 'core.safecrlf=false', *args], cwd=root, text=True, encoding='utf-8').strip()


def at(report, path):
    for key in path.split('.'):
        report = report[key]
    return report


def decode_report(payload):
    def strict_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'duplicate report field: {key}')
            result[key] = value
        return result
    def nonfinite(value):
        raise ValueError(f'nonfinite report value: {value}')
    return json.loads(payload, object_pairs_hook=strict_object, parse_constant=nonfinite)


def validate_report(name, result):
    if type(result) is not dict:
        raise ValueError(f'{name}: report must be a JSON object')
    for path in AUDITS[name][0].split():
        at(result, path)
    if name == 'recovered_authorities':
        # These four TRUE values reproduce unsafe *historical* issuers, whose
        # actual Git source is loaded by the audit. They are negative controls.
        for key in AUDITS[name][0].split()[1:]:
            if result[key] is not True:
                raise ValueError(f'{name}: historical counterexample was not reproduced: {key}')
    elif result.get('status') != 'PASS':
        raise ValueError(f'{name}: incomplete or failed report')
    if name == 'reference_model_check':
        if result['selected_cases'] is not None or result['counts']['runs'] != 36:
            raise ValueError('a partial randomized audit is not release evidence')
        for key in ('initial_range_unresolved_members', 'profile_range_unresolved_members', 'halted_unsafe_ordinary_commits'):
            if type(result['counts'][key]) is not int or result['counts'][key] <= 0:
                raise ValueError(f'missing negative endpoint control: {key}')
    if name == 'reference_acceleration':
        bound = result['cases']['bounded']
        if (bound['tokens'], bound['complete_domain_predictions_checked'], bound['installed_at_cursor'],
                bound['continued_after_install_and_sealed_at']) != (32, 1024, 330, 622):
            raise ValueError('the actual registered 32-token hierarchy path was not executed')
    if name in ('owned_compiler_policy', 'cpu_installation'):
        count = at(result, 'learned.native_class_sizes' if name == 'owned_compiler_policy' else 'learned.complete_native_class_programs')
        if count != ([774] if name == 'owned_compiler_policy' else 774):
            raise ValueError('missing complete trained 774-member install class')


def job_receipts(value, path=''):
    """Retain small actual OS exit/identity/peak records, not child logs."""
    result = {}
    if type(value) is dict:
        if {'exit_code', 'process_creation_100ns', 'commit_limit', 'peak_process_commit'} <= value.keys():
            result[path] = value
        else:
            for key, child in value.items():
                result.update(job_receipts(child, f'{path}.{key}'.strip('.')))
    return result


def run_audit(checkout, name):
    started = time.monotonic()
    script = f'scripts/audit_{name}.py'
    print(f'START {script}', file=sys.stderr, flush=True)
    completed = subprocess.run([sys.executable, '-B', script], cwd=checkout,
        capture_output=True, timeout=7200, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONOPTIMIZE=''))
    if completed.returncode != 0:
        raise RuntimeError(f'{script}: exit {completed.returncode}\n{completed.stderr[-8192:].decode("utf-8", "replace")}')
    if len(completed.stdout) > MAX_REPORT_BYTES or len(completed.stderr) > MAX_REPORT_BYTES:
        raise ValueError(f'{script}: oversized/truncated diagnostic transport cannot pass')
    result = decode_report(completed.stdout)
    validate_report(name, result)
    seconds = round(time.monotonic()-started, 2)
    print(f'PASS {script} ({seconds}s)', file=sys.stderr, flush=True)
    return {'status': 'PASS', 'scope': result.get('scope'), 'seconds': seconds,
        'complete_sections': AUDITS[name][0].split(),
        'evidence': {key: at(result, key) for key in AUDITS[name][1].split()},
        'completed_jobs': job_receipts(result)}


def gates(checkout):
    path = checkout/'docs/REFERENCE_RELEASE_GATE_MAP.md'
    body = path.read_text(encoding='utf-8')
    references = dict(re.findall(r'^\[([^\]]+)\]:\s+(\S+)', body, flags=re.M))
    rows = {}
    for match in re.finditer(r'^\| (\d+) \| ([^|]+) \| ([RSXOT/]+) \| (.+) \|$', body, flags=re.M):
        index, _, mode, evidence = match.groups()
        index = int(index)
        if index in rows or 'O' in mode:
            raise ValueError('duplicate gate or still-open Reference obligation')
        executed = []
        for link in re.findall(r'\]\[([^\]]+)\]', evidence):
            target = (path.parent/references[link]).resolve()
            if not target.is_relative_to(checkout) or not target.is_file():
                raise ValueError(f'gate {index}: missing/outside evidence {link}')
            if target.parent == checkout/'scripts' and target.name.startswith('audit_'):
                name = target.stem[len('audit_'):]
                if name not in AUDITS:
                    raise ValueError(f'gate {index}: executable omitted from full battery')
                executed.append(name)
        if ('R' in mode or 'X' in mode) and not executed:
            raise ValueError(f'gate {index}: no current executable for Reference/denial scope')
        rows[index] = {'mode': mode, 'audits': sorted(set(executed))}
    if set(rows) != set(range(47)) or {i for i, r in rows.items() if 'T' in r['mode']} != {13, 16, 20, 28, 29, 30}:
        raise ValueError('the complete historical obligation map or target boundary changed')
    return rows


def release(workers):
    if not __debug__ or sys.flags.optimize or os.environ.get('PYTHONOPTIMIZE'):
        raise RuntimeError('audit assertions must be enabled')
    if sys.platform != 'win32' or platform.architecture()[0] != '64bit':
        raise RuntimeError('this release claim includes actual 64-bit Windows host enforcement')
    source = git(ROOT, 'rev-parse', 'HEAD')
    if git(ROOT, 'status', '--porcelain', '--untracked-files=no'):
        raise RuntimeError('commit the reviewable source before testing its release revision')
    if git(ROOT, 'show', f'{source}:scripts/audit_reference_release.py').replace('\r\n', '\n') != Path(__file__).read_text(encoding='utf-8').strip():
        raise RuntimeError('the running driver differs from the identified source revision')
    started = datetime.now(timezone.utc).isoformat()
    with tempfile.TemporaryDirectory(prefix='fp-reference-release-', dir=ROOT) as temporary:
        assert Path(temporary).resolve().parent == ROOT
        checkout = Path(temporary).resolve()/'repository'
        subprocess.run(['git', 'clone', '--quiet', '--no-hardlinks', '--no-checkout', str(ROOT), str(checkout)], check=True)
        subprocess.run(['git', '-c', 'core.safecrlf=false', 'checkout', '--quiet', '--detach', source], cwd=checkout, check=True)
        if git(checkout, 'rev-parse', 'HEAD') != source or git(checkout, 'status', '--porcelain'):
            raise RuntimeError('fresh checkout is not the declared clean revision')
        gate_map = gates(checkout)
        code = ('import sys,pkgutil,importlib,json; from pathlib import Path; '
            'root=Path.cwd(); sys.path.insert(0,str(root/"src/reference_compiler")); '
            'import fp_reference; names=sorted(m.name for m in pkgutil.walk_packages(fp_reference.__path__,fp_reference.__name__+".")); '
            '[importlib.import_module(n) for n in names]; '
            'assert all(Path(sys.modules[n].__file__).resolve().is_relative_to(root) for n in names); '
            'print(json.dumps(names))')
        modules = json.loads(subprocess.check_output([sys.executable, '-B', '-c', code], cwd=checkout))
        if len(modules) != 30:
            raise RuntimeError('review changed package module coverage before a release')
        with ThreadPoolExecutor(max_workers=workers) as pool:
            pending = {pool.submit(run_audit, checkout, name): name for name in AUDITS}
            results, errors = {}, []
            for future in as_completed(pending):
                name = pending[future]
                try:
                    results[name] = future.result()
                except Exception as error:
                    errors.append(f'{name}: {type(error).__name__}: {error}')
                    print(f'FAIL {errors[-1]}', file=sys.stderr, flush=True)
            if errors:
                raise RuntimeError('release did not pass:\n'+'\n'.join(errors))
        if git(checkout, 'rev-parse', 'HEAD') != source or git(checkout, 'status', '--porcelain'):
            raise RuntimeError('audit altered its committed source or left untracked artifacts')
        assert Path(temporary).resolve().parent == ROOT
    if git(ROOT, 'rev-parse', 'HEAD') != source or git(ROOT, 'status', '--porcelain', '--untracked-files=no'):
        raise RuntimeError('source changed during its release audit; no publication')
    return {'status': 'PASS', 'scope': 'complete scoped Reference/CPU release integration; target AMP held',
        'source_commit': source, 'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
        'machine': 'packed-reference-payload-v9', 'python': sys.version, 'platform': platform.platform(),
        'fresh_clone': {'no_hardlinks': True, 'clean_before_and_after': True, 'imported_modules': modules},
        'audit_count': len(results), 'audits': {name: results[name] for name in AUDITS},
        'historical_gate_map': gate_map,
        'closure_obligations': {
            '1': 'fresh_clone', '2': ['recovered_authorities', 'control_admission', 'owned_compiler_policy'],
            '3': ['reference_search', 'reference_acceleration', 'reference_run'],
            '4': ['reference_search', 'reference_model_check'],
            '5': ['reference_construction', 'cpu_installation', 'owned_encoding', 'host_allocation_failure', 'bound_host_runtime'],
            '6': ['reference_events', 'reference_profiles', 'reference_persistence'],
            '7': ['context_ingress', 'reference_persistence', 'owned_compiler_policy'],
            '8': ['float64_runtime', 'paired_cpu_persistence', 'cpu_installation'],
            '9': ['reference_search', 'reference_acceleration', 'control_admission', 'paired_cpu_persistence', 'cpu_installation'],
            '10': ['reference_numerics', 'binary_arithmetic', 'float64_runtime', 'reference_model_check'],
            '11': ['reference_events', 'reference_numerics', 'context_ingress'],
            '12': ['reference_acceleration'], '13': 'historical_gate_map', '14': ['reference_model_check'],
            '15': 'HOLD: actual AMP after this Reference closure'},
        'not_claimed': ['every legal registration has been enumerated', 'CERTIFIED_COMPLETE or arbitrary strategy/parameter optimality',
            'scoped static theorem rows are executable gate passes', 'actual target AMP, shared device resources or GPU science',
            'cross-root statistical family authority']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, choices=range(1, 9), default=4)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = release(args.workers)
    if args.write:
        (ROOT/'evidence/minimal/FP_REFERENCE_RELEASE_AUDIT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
