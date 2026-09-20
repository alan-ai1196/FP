"""Matched current-source literal/shared n8 execution, with full owned audits.

Two fixed workers use the same retained case and common finite grammar.
Every physical attempt is published before its independent result reader.
"""
from dataclasses import asdict, replace
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import os
import traceback

import run_likelihood_model as model
import analyze_likelihood_model as reader
from analyze_likelihood_deployment import check_fresh, DEPENDENCIES as READER_DEPENDENCIES
from fp_reference.native_search import GrammarLimits
from fp_reference.simplex_relation_proposal import SOLVER, MARGINAL_SOLVER
from audit_simplex_learner import fixture

ROOT = model.ROOT
CASE = (8, 'iid-c2', 16)
BOUND = F(13, 8)
VARIANTS = (('literal-v7', SOLVER), ('shared-v8', MARGINAL_SOLVER))
OUTPUT = ROOT/'evidence/minimal/FP_PAIR_MARGINAL_MODEL_EXPERIMENT.json'
DEPENDENCIES = tuple(dict.fromkeys(READER_DEPENDENCIES+(
    'experiments/joint_uncertainty/run_pair_marginal_model.py',
    'experiments/joint_uncertainty/PAIR_MARGINAL_MODEL_PROTOCOL.md',
    'experiments/joint_uncertainty/positive_pair_marginals.py',
    'theory/proofs/POSITIVE_PAIR_MARGINAL_CIRCUIT.md')))


def common_grammar():
    graphs = [fixture(CASE[0], solver=solver)[1] for _, solver in VARIANTS]
    return GrammarLimits(**{key: max(graph.counts()[key] for graph in graphs)
        for key in ('nodes', 'SUMs', 'PRODUCTs', 'edges', 'slots')})


def configuration(index):
    return model.setup(CASE, gain_bound=BOUND, solver=VARIANTS[index][1], grammar=common_grammar())


def preflight():
    baselines, provenance = model.retained_baselines()
    baseline = baselines[0]
    assert tuple(baseline['case']) == CASE
    left, right = configuration(0), configuration(1)
    assert left[0] == right[0] and left[3:] == right[3:]
    assert replace(right[2], searches=left[2].searches) == left[2]
    left_search, right_search = left[2].searches[0], right[2].searches[0]
    assert replace(right_search, relation_sources=left_search.relation_sources) == left_search
    assert replace(right_search.relation_sources, solver=SOLVER) == left_search.relation_sources
    assert left[1] != right[1] and left[1].slot_count == right[1].slot_count == 129
    variants = []
    for index, (name, solver) in enumerate(VARIANTS):
        cfg, graph, online, cuda, _, _ = configuration(index)
        variants.append({'name': name, 'solver': solver, 'native': graph.counts(),
            'predict_cells': model.output_cells('predict', graph, cfg.semantics, online.learner),
            'observe_cells': model.output_cells('observe', graph, cfg.semantics, online.learner),
            'prepaid_scratch_bytes': model.preparation_workspace(graph, cfg.semantics,
                online.learner, cfg.source_domain, cfg.reference_integer_bits),
            'prepaid_derivation_work': model.preparation_work(graph, cfg.semantics,
                online.learner, cfg.source_domain, cfg.reference_integer_bits)})
    return {'case': CASE, 'variants_in_order': variants, 'common_grammar': asdict(common_grammar()),
        'training_events': 60, 'evaluation_events': 64, 'profile_passes': 1,
        'Gamma': 'fixed feature1; all128 selected worlds at1/128', 'unit': 1, 'rate': '1',
        'reference_integer_bits': 32768, 'native_range_caps': '16',
        'binary64_tolerances': '1/1000000000', 'AMP_state_native_normalizer_tolerance': '1/100',
        'AMP_probability_tolerance': '1/1000', 'host_cap': model.CAP, 'timeout_ms': model.TIMEOUT,
        'packed_cap': model.PACKED, 'work_per_role': model.WORK,
        'phase_frame_bytes': model.FRAME, 'phase_output_cells': model.CELLS,
        'arena_bytes': model.ARENA, 'allocator_bytes': 2*model.ARENA,
        'persistence': {'bound': str(BOUND), 'bet': '3/4', 'coefficient': '6/13',
            'alpha_per_path': '1/4', 'total_alpha_allowance': '3/4', 'epoch_events': 1,
            'horizon': 64, 'log_terms': 12, 'wealth_grid_bits': 16},
        'likelihood_encoding': {'radix': '9', 'counter_bits': 64},
        'execution_identity': cuda.execution_identity,
        'retained_strong_posterior': {'provenance': provenance, 'selected_case': CASE,
            'exact_unseen_CE': baseline['adaptive_exact_unseen']['expected_CE_binary64'],
            'AMP_unseen_CE': baseline['adaptive_AMP_unseen']['expected_CE_binary64']},
        'primary_endpoint': 'complete execution, including final auditors, and completed job/packed peaks',
        'secondary_endpoints': 'actual frame/cell counts, bit words, native posterior agreement, fresh installation and deployed CE',
        'scope': 'one exposed fixed case; common finite grammar, no class proof, population or exclusive-device timing claim'}


def worker(index):
    name, solver = VARIANTS[index]
    result = model.worker(CASE, gain_bound=BOUND, detailed_fresh=True, solver=solver, grammar=common_grammar())
    result.update(variant=name, solver=solver, registered_grammar=asdict(common_grammar()))
    return result


def read_result(row, baseline, source):
    if not reader.check_job(row, source, baseline['device']):
        return {'status': 'FAILED_WORKER_UNSCORED', 'reason': reader.failure_reason(row)}
    index = row['case_index']
    name, solver = VARIANTS[index]
    result = row['result']
    assert (result['variant'], result['solver']) == (name, solver)
    assert result['registered_grammar'] == asdict(common_grammar())
    detail, scores, decisions = reader.check_result(result, CASE, baseline,
        fresh_checker=check_fresh, solver=solver)
    return {'status': 'SAME_SOURCE_INDEPENDENT_READER_PASS',
        'model_score_checks': scores, 'fresh_path_checks': decisions, 'details': detail}


def paired_comparison(rows):
    if len(rows) != 2 or any(row.get('analysis', {}).get('status') != 'SAME_SOURCE_INDEPENDENT_READER_PASS'
            or row.get('result', {}).get('run_status') != 'SEALED_CUDA_STREAM'
            or row['result']['candidate_native'] is None for row in rows):
        return {'status': 'UNRESOLVED_MISSING_COMPLETE_PAIR', 'imputed_outcomes': False}
    left, right = (row['result'] for row in rows)
    def candidate_words(result):
        return {r['cursor']: r for r in result['CUDA_readouts'] if r['candidate'] == 'posterior'}
    a, b = candidate_words(left), candidate_words(right)
    assert set(a) == set(b) == set(range(60, 124))
    return {'status': 'BOTH_COMPLETE',
        'candidate_mass_word_matches': sum(a[k]['mass_words'] == b[k]['mass_words'] for k in a),
        'candidate_division_word_matches': sum(a[k]['division_words'] == b[k]['division_words'] for k in a),
        'forecast_rows': 64, 'job_peaks_in_variant_order': [r['completed_job']['peak_job_commit'] for r in rows],
        'packed_peaks_in_variant_order': [r['packed_peak'] for r in (left, right)],
        'install_cursors_in_variant_order': [r['install_cursor'] for r in (left, right)],
        'candidate_unseen_CE_in_variant_order': [r['scores']['candidate_stream_unseen']['expected_CE_binary64'] for r in (left, right)],
        'deployed_unseen_CE_in_variant_order': [r['scores']['deployed_stream_unseen']['expected_CE_binary64'] for r in (left, right)],
        'scope': 'two current-source executions on one retained tape; no universal resource or population ordering'}


def matrix():
    source = model.git('rev-parse', 'HEAD')
    def clean():
        assert model.git('rev-parse', 'HEAD') == source
        assert not model.git('status', '--porcelain', '--', *DEPENDENCIES), 'commit every execution dependency first'
    clean()
    assert not OUTPUT.exists(), 'retain prior attempts; this fixed comparison has no automatic retry'
    baselines, _ = model.retained_baselines()
    baseline = baselines[0]
    report = {'status': 'PARTIAL_EXECUTION', 'registration_source': source,
        'registration': preflight(), 'baseline_score_checks': reader.check_baseline(baseline, *model.data(CASE)),
        'workers': []}
    def publish():
        temporary = OUTPUT.with_suffix('.tmp')
        temporary.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        temporary.replace(OUTPUT)
    publish()
    for index, (name, solver) in enumerate(VARIANTS):
        clean()
        row = model.bounded(index, worker_script=__file__, directory_prefix='fp-pair-marginal-model-')
        row.update(case_index=index, case=CASE, variant=name, solver=solver, execution_source=source)
        report['workers'].append(row)
        report['status'] = 'WORKER_FINISHED_READER_PENDING'
        publish()
        try:
            clean()
            row['analysis'] = read_result(row, baseline, source)
        except Exception:
            row['analysis'] = {'status': 'READER_FAILURE_UNSCORED', 'traceback': traceback.format_exc()}
        report['status'] = 'PARTIAL_EXECUTION'
        publish()
        print(json.dumps({'variant': name, 'worker_status': row['worker_status'],
                          'reader_status': row['analysis']['status']}), flush=True)
        if row['analysis']['status'] == 'READER_FAILURE_UNSCORED' or 'report_audit_failure' in row:
            report['status'] = 'STOPPED_AUDITOR_FAILURE'
            publish()
            return {'status': report['status'], 'attempted_workers': len(report['workers'])}
    report['comparison'] = paired_comparison(report['workers'])
    report['status'] = ('COMPLETE_EXECUTION' if report['comparison']['status'] == 'BOTH_COMPLETE'
                        else 'COMPLETE_WITH_REFUSALS_OR_FAILURES')
    publish()
    return {'status': report['status'], 'attempted_workers': len(report['workers'])}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument('--preflight', action='store_true')
    operation.add_argument('--matrix', action='store_true')
    operation.add_argument('--worker', type=int, choices=range(2))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    assert (args.worker is not None) == bool(args.output)
    if args.worker is not None:
        try:
            result = worker(args.worker)
        except Exception:
            args.output.write_text(json.dumps({'traceback': traceback.format_exc(), 'process_id': os.getpid()}), encoding='utf-8')
            raise
        args.output.write_text(json.dumps(result), encoding='utf-8')
    else:
        print(json.dumps(preflight() if args.preflight else matrix(), indent=2))
