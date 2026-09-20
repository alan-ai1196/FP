"""Registered B=13/8 deployment test on the four retained n8 tapes.

The previous B=6 owned matrix and exact/AMP posterior controls are retained.
Only the current complete Runtime constructs, profiles, scores and installs.
"""
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import os
import sys
import traceback

import run_likelihood_model as model
from fp_reference.numerics import log_enclosure_work, compare_exact_work
from fp_reference.persistence_bounds import mass_box_work

ROOT, CASES = model.ROOT, model.CASES
BOUND = F(13, 8)
OUTPUT = ROOT/'evidence/minimal/FP_LIKELIHOOD_DEPLOYMENT_EXPERIMENT.json'
CONTROL_COMMIT = '09ee265'
CONTROL_PATH = 'evidence/minimal/FP_LIKELIHOOD_MODEL_EXPERIMENT.json'
CONTROL_ANALYSIS = 'evidence/minimal/FP_LIKELIHOOD_MODEL_ANALYSIS.json'
SELF = Path(__file__).relative_to(ROOT).as_posix()
DEPENDENCIES = tuple(dict.fromkeys(model.DEPENDENCIES+(SELF,
    'experiments/joint_uncertainty/LIKELIHOOD_DEPLOYMENT_PROTOCOL.md',
    'theory/proofs/CURRENT_MASS_PERSISTENCE_BOUND.md', CONTROL_PATH, CONTROL_ANALYSIS)))


def retained_controls():
    control = json.loads((ROOT/CONTROL_PATH).read_text(encoding='utf-8'))
    analysis = json.loads((ROOT/CONTROL_ANALYSIS).read_text(encoding='utf-8'))
    for path, value in ((CONTROL_PATH, control), (CONTROL_ANALYSIS, analysis)):
        assert value == json.loads(model.git('show', CONTROL_COMMIT+':'+path))
    assert control['status'] == analysis['journal_status'] == 'COMPLETE_EXECUTION'
    assert len(control['workers']) == analysis['sealed_workers'] == 4
    assert all(w['worker_status'] == 'EXECUTED' and w['result']['run_status'] == 'SEALED_CUDA_STREAM'
               for w in control['workers'])
    assert control['registration'] == json.loads(json.dumps(model.preflight()))
    assert control['prior_auditor_failure'] == model.prior_auditor_failure(control['registration'])
    assert control['registration_source'] == analysis['execution_source']
    return control, {'journal': CONTROL_PATH, 'analysis': CONTROL_ANALYSIS,
        'retained_at': model.git('rev-parse', CONTROL_COMMIT),
        'execution_source': control['registration_source'], 'analysis_source': analysis['analysis_source'],
        'original_failed_attempt': control['prior_auditor_failure'],
        'scope': 'all four completed B6 owned controls retained exactly; no new control worker'}


def preflight():
    control, provenance = retained_controls()
    for case in CASES:
        old = model.setup(case)
        new = model.setup(case, gain_bound=BOUND)
        assert old[:2] == new[:2] and old[3:] == new[3:]
        from dataclasses import replace
        assert replace(new[2], persistence=old[2].persistence) == old[2]
        assert tuple(rule.bound for rule in new[2].persistence.rules) == (BOUND, BOUND)
    _, _, online, _, _, _ = new
    assert 'torch' not in sys.modules
    return {'model_and_resources': control['registration'], 'owned_B6_control': provenance,
        'persistence': {'bound': str(BOUND), 'bet': '3/4', 'coefficient': '6/13',
            'alpha_per_identity': '1/4', 'alpha_total': '3/4', 'epoch_events': 1, 'horizon': 64,
            'log_terms': 12, 'wealth_grid_bits': 16,
            'score_paths': tuple(rule.score_path for rule in online.persistence.rules),
            'null_ids': tuple(rule.null_id for rule in online.persistence.rules)},
        'implementation': {'mass_bound_solver_introduced_at': '1997cb9',
            'refined_proof_kind': 'current-native-mass-box',
            'raw_observation_workspace_bytes': 8*model.CELLS,
            'phase_output_work_coefficient': 320,
            'mass_refinement_work_per_attempt': mass_box_work(64, 2)+log_enclosure_work(12)+compare_exact_work()},
        'scope': 'four retained tapes; complete owned deployment with a tighter predeclared common bound; no new IID or timing claim'}


def matrix(*, resume=False):
    source = model.git('rev-parse', 'HEAD')

    def source_clean():
        assert model.git('rev-parse', 'HEAD') == source
        assert not model.git('status', '--porcelain', '--', *DEPENDENCIES), 'commit all execution dependencies first'

    source_clean()
    registration = json.loads(json.dumps(preflight()))
    baselines, _ = model.retained_baselines()
    if resume:
        report = json.loads(OUTPUT.read_text(encoding='utf-8'))
        assert report['status'] == 'PARTIAL_EXECUTION' and report['registration_source'] == source
        assert report['registration'] == registration
        assert [row['case_index'] for row in report['workers']] == list(range(len(report['workers'])))
    else:
        assert not OUTPUT.exists(), 'retain earlier attempts; no silent rerun'
        report = {'status': 'PARTIAL_EXECUTION', 'registration_source': source,
                  'registration': registration, 'workers': []}

    def publish():
        temporary = OUTPUT.with_suffix('.tmp')
        temporary.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        temporary.replace(OUTPUT)

    publish()
    for index in range(len(report['workers']), len(CASES)):
        source_clean()
        row = model.bounded(index, worker_script=__file__, directory_prefix='fp-deployment-model-')
        row.update(case_index=index, case=CASES[index], execution_source=source)
        if row['worker_status'] == 'EXECUTED' and row['result']['run_status'] == 'SEALED_CUDA_STREAM':
            try:
                assert row['result']['device'] == baselines[index]['device']
                for key in ('adaptive_exact_unseen', 'adaptive_exact_full_domain'):
                    assert row['result']['scores'][key] == baselines[index][key]
            except Exception:
                row['worker_status'] = 'FAILED'
                row['report_audit_failure'] = traceback.format_exc()
        report['workers'].append(row)
        source_clean()
        publish()
        print(json.dumps({'case': CASES[index], 'worker_status': row['worker_status']}), flush=True)
        failure = row.get('result', {}).get('traceback', '')
        if 'report_audit_failure' in row or failure and 'MemoryError' not in failure:
            report['status'] = 'STOPPED_AUDITOR_FAILURE'
            publish()
            return {'status': report['status'], 'attempted_workers': len(report['workers'])}
    report['status'] = 'COMPLETE_EXECUTION' if all(w['worker_status'] == 'EXECUTED' for w in report['workers']) else 'COMPLETE_WITH_FAILURES'
    publish()
    return {'status': report['status'], 'workers': len(report['workers'])}


def fresh_scenarios():
    """Actual small reference paths, including failed owned crossing retention."""
    from fp_reference.runtime import ReferenceCompilerRuntime
    from fp_reference.persistence import PersistenceContract
    from fp_reference.resources import ResourceExceeded
    from audit_reference_construction import contract
    from audit_reference_persistence import fixture, rule, event, owned
    examples = []
    for fail in (False, True):
        cfg = contract(cap=16, peak=1)
        runtime, candidate = fixture(cfg=cfg, count=16,
            registration=PersistenceContract(F(3, 4), (rule(horizon=16, bound=BOUND),)))
        base = runtime.snapshot().deployed_id
        runtime.admit_reference_persistence(candidate, 'future')
        original = ReferenceCompilerRuntime._save_persistence

        def save(root, identity):
            if fail and identity.status == 'REFERENCE_CROSSED':
                raise ResourceExceeded('injected owned crossing retention failure')
            return original(root, identity)

        scores = {}
        with patch.object(ReferenceCompilerRuntime, '_save_persistence', save):
            for cursor in range(16):
                prediction, _ = event(runtime, 0)
                predictions = dict(prediction.predictions)
                scores['observation-'+str(cursor)] = predictions[base][0], predictions[candidate][0]
        snapshot = owned(runtime)
        fresh = model.fresh_audit(snapshot, scores, {}, base, candidate, detailed=True)
        assert len(fresh['numerical_crossings']) == 1
        assert bool(fresh['crossings']) == (not fail)
        examples.append({'result': {'fresh': fresh, 'alpha_spent': str(snapshot.alpha_spent),
            'install_cursor': None, 'cutoff': {'candidate_selected': True}},
            'exact': {(0, 0): (F(2, 3), F(1, 3))},
            'evaluation': ((0, 0, 0),)*16, 'domain_rows': len(cfg.source_domain)})
    return examples


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--matrix', action='store_true')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--worker', type=int, choices=range(len(CASES)))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    assert (args.worker is not None) == bool(args.output)
    assert not args.write or args.matrix
    assert not args.resume or args.matrix and args.write
    if args.worker is not None:
        assert not (args.preflight or args.matrix or args.self_test)
        try:
            result = model.worker(CASES[args.worker], gain_bound=BOUND, detailed_fresh=True)
        except Exception:
            args.output.write_text(json.dumps({'traceback': traceback.format_exc(), 'process_id': os.getpid()}), encoding='utf-8')
            raise
        args.output.write_text(json.dumps(result), encoding='utf-8')
    else:
        assert args.preflight or args.self_test or args.matrix and args.write
        if args.self_test:
            values = fresh_scenarios()
            result = {'actual_reference_scenarios': len(values), 'numeric_crossing_without_owned_crossing_retained': True}
        else:
            result = preflight() if args.preflight else matrix(resume=args.resume)
        print(json.dumps(result, indent=2))
