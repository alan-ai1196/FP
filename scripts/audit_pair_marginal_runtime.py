"""Source-bound owned construction, profile, CPU/AMP and install audit for v8.

The independent passive builder checks syntax; owned phases retain the new
Program's full gradients/caches. No old learner or evidence is substituted.
"""
from dataclasses import asdict, replace
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import os
import subprocess
import sys
import tempfile
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'),
               str(ROOT/'experiments/joint_uncertainty')]
import positive_pair_marginals as oracle
from audit_simplex_learner import fixture, owned, preflight as simplex_preflight, HOST_CAPS, TIMEOUT
from audit_reference_construction import rejects, validate_residency
from ingress_audit_support import deliver_context
from fp_reference import CompilerPolicy, ReferenceCompilerRuntime
from fp_reference.empirical_bound import empirical_upper
from fp_reference.native_search import GrammarLimits
from fp_reference.pair_marginal_program import _emit_pair_marginals, marginal_counts
from fp_reference.program import Program, Sum
from fp_reference.relation_proposal import RelationSourceSpec, relation_proposal
from fp_reference.simplex_relation_proposal import SOLVER, MARGINAL_SOLVER, simplex_relation_proposal

CASES = {
    'marginal-cpu-n2': (MARGINAL_SOLVER, 'cpu', 2, 1, False),
    'marginal-cpu-n3': (MARGINAL_SOLVER, 'cpu', 3, 2, False),
    'marginal-cuda-n2': (MARGINAL_SOLVER, 'cuda', 2, 1, False),
    'marginal-cuda-n3': (MARGINAL_SOLVER, 'cuda', 3, 2, False),
    'marginal-likelihood-n3': (MARGINAL_SOLVER, 'cuda', 3, 2, True),
    'literal-cpu-n3': (SOLVER, 'cpu', 3, 2, False),
    'literal-cuda-n3': (SOLVER, 'cuda', 3, 2, False),
}
OUTPUT = ROOT/'evidence/minimal/FP_PAIR_MARGINAL_RUNTIME_AUDIT.json'
DEPENDENCIES = ('src/reference_compiler', 'scripts',
    'experiments/joint_uncertainty/positive_pair_marginals.py',
    'experiments/joint_uncertainty/simplex_gradient.py',
    'experiments/joint_uncertainty/predictive_counts.py',
    'experiments/joint_uncertainty/likelihood_information.py',
    'theory/proofs/POSITIVE_PAIR_MARGINAL_CIRCUIT.md')


def exact_audit():
    syntax = []
    for n in range(2, 9):
        rules, graph, worlds = oracle.relation_graph(n)
        atoms = tuple((f'x0:{i}', f'x1:{i}') for i in range(n))
        emitted = _emit_pair_marginals(rules, atoms, len(worlds))
        assert emitted == graph, 'integer-index emitter differs from independent prefix-tuple builder'
        assert all(emitted.counts()[key] == value for key, value in marginal_counts(n, len(worlds)).items())
        syntax.append({'n': n, 'nodes': len(graph.nodes), 'incidences': graph.counts()['edges']})

    cfg, graph, online, _ = fixture(3, solver=MARGINAL_SOLVER)
    online = replace(online, float64=None)
    base = Program((Sum('mass', ()),), graph.slot_count, (0, 0))
    rt = ReferenceCompilerRuntime(cfg, base, online=online)
    assert deliver_context(rt, online.data.active.observation_ids[0],
        tuple(oracle.literal.context(3, 0, 1).values())).status == 'PREDICTED_REFERENCE'
    assert rt.observe(0).status == 'OBSERVED_REFERENCE'
    upper = empirical_upper(rt.snapshot().observations, cfg.semantics, bit_limit=32768)
    grammar = GrammarLimits(**{key: graph.counts()[key] for key in cfg.graph_limits})
    source = RelationSourceSpec(tuple((f'x0:{i}', f'x1:{i}') for i in range(3)), solver=MARGINAL_SOLVER)
    args = dict(upper=upper, rules=cfg.semantics, grammar=grammar, pattern=cfg.initializer_pattern,
        registration=source, data=online.data, learner=online.learner,
        source_domain=cfg.source_domain, profile=online.profiles[0], bit_limit=32768)
    assert simplex_relation_proposal(**args).program == graph
    bad_row = list(cfg.source_domain[0])
    bad_row[1] = F(1)
    changes = [
        {'pattern': (F(1), F(1, 2), F(1, 6), F(1, 6), F(1, 6))},
        {'pattern': (F(2),)+(F(1, 4),)*4},
        {'source_domain': cfg.source_domain[:-1]},
        {'source_domain': cfg.source_domain[:-1]+cfg.source_domain[:1]},
        {'source_domain': (tuple(bad_row),)+cfg.source_domain[1:]},
        {'profile': None},
        {'learner': replace(online.learner, learning_rate=F(0))},
        {'learner': replace(online.learner, update_unit=2)},
        {'learner': replace(online.learner, simplex_slots=(0, 1, 2, 3))},
        {'registration': RelationSourceSpec(tuple((f'l{i}', f'r{i}') for i in range(80)), solver=MARGINAL_SOLVER)},
    ]
    changes += [{'grammar': replace(grammar, **{key: getattr(grammar, key)-1})}
                for key in cfg.graph_limits]
    # Refusals precede any graph allocation, not just an after-the-fact rejection.
    with patch('fp_reference.simplex_relation_proposal._emit_pair_marginals',
               side_effect=AssertionError('invalid context reached syntax allocation')):
        for change in changes:
            result = simplex_relation_proposal(**dict(args, **change))
            assert result.status == 'UNRESOLVED' and result.program is None and result.reason
    assert relation_proposal(upper, cfg.semantics, grammar, cfg.initializer_pattern,
                             source, bit_limit=32768).program is None
    guarded = ReferenceCompilerRuntime(cfg, base, online=online, policy=CompilerPolicy(()))
    before = guarded.snapshot()
    rejects(lambda: guarded.construct_candidate(graph))
    assert guarded.snapshot() == before
    rejects(lambda: deliver_context(guarded, online.data.active.observation_ids[0], tuple(bad_row)))
    final = validate_residency(guarded)
    assert not final.observations and not final.install_receipts and not final.reference_proofs
    assert len(final.candidates) == 1
    # Source declaration order is not a hidden semantic requirement.
    permuted_rules = replace(cfg.semantics, sources=tuple(reversed(cfg.semantics.sources)))
    permuted_domain = tuple(tuple(reversed(row)) for row in cfg.source_domain)
    permuted = simplex_relation_proposal(**dict(args, rules=permuted_rules, source_domain=permuted_domain))
    assert permuted.program is not None
    worlds = oracle.relation_graph(3)[2]
    for i in range(3):
        for j in range(3):
            oracle.checked_prediction(3, permuted_rules, permuted.program, worlds,
                                       (F(1, 4),)*4, (i, j))
    return {'status': 'PASS', 'independent_syntax': syntax, 'preallocation_refusals': len(changes),
        'partial_context_helper_refused': True, 'owned_policy_bypass_refused': True,
        'owned_non_one_hot_ingress_refused': True, 'permuted_source_forecasts': 9,
        'certificate_authority_from_helper': False}


def run_worker(case):
    solver, path, n, passes, encoding = CASES[case]
    return owned(n, profiles=True, cuda=path == 'cuda', passes=passes, bounded=True,
                 solver=solver, encoding=encoding)


def bounded_case(case):
    from windows_job_audit_support import run_in_job
    directory = Path(tempfile.mkdtemp(prefix='fp-pair-marginal-audit-', dir=ROOT))
    assert directory.resolve().parent == ROOT.resolve()
    output = directory/'result.json'
    cap = HOST_CAPS[CASES[case][1]]
    job = run_in_job(__file__, ('--worker', case, '--output', str(output)),
                     commit_limit=cap, timeout_ms=TIMEOUT)
    row = {'case': case, 'worker_status': 'FAILED', 'completed_job': asdict(job)}
    if output.exists():
        with output.open('rb') as stream:
            raw = stream.read(65537)
        assert len(raw) <= 65536
        row['result'] = json.loads(raw)
    if (job.exit_code == 0 and not job.timed_out and job.attached_before_resume
            and not job.limit_terminated_processes):
        result, observed = row['result'], row['result']['host']
        assert result['process_id'] == job.process_id
        assert (observed['process_id'], observed['creation_100ns']) == (job.process_id, job.process_creation_100ns)
        assert observed['lifetime_process_commit_peak'] <= job.peak_process_commit <= cap
        assert observed['job_commit_peak'] <= job.peak_job_commit <= cap
        for clock in ('user', 'kernel'):
            assert max(observed[f'process_{clock}_100ns'], observed[f'job_{clock}_100ns']) <= getattr(job, f'{clock}_100ns')
        solver, path, n, passes, encoding = CASES[case]
        assert (result['solver'], result['n'], result['profile_passes'], result['likelihood_encoding']) == (solver, n, passes, encoding)
        assert result['status'] == ('SEALED_CUDA_STREAM' if path == 'cuda' else 'SEALED_REFERENCE_STREAM')
        assert result['historical_class'] == 'UNRESOLVED' and not result['class_certificate']
        row['worker_status'] = 'EXECUTED'
    if output.exists():
        output.unlink()
    directory.rmdir()
    return row


def preflight():
    common = simplex_preflight()
    common['cases'] = CASES
    common['grammar'] = 'exact independent emitted graph counts per case; no old class enlarged'
    common['profile_passes'] = 'one for n2; two for n3, for each declared solver'
    common['likelihood_encoding'] = 'existing radix9 contract, 64-bit counters, only in the named case'
    common['scope'] = 'new ordinary Program with full owned state; constructor classes stay unresolved; no model comparison'
    common['concurrency'] = 'may overlap fixed model workers; no exclusive-device timing claim'
    return common


def matrix():
    def git(*args):
        return subprocess.run(('git', *args), cwd=ROOT, capture_output=True, encoding='utf-8', check=True).stdout.strip()
    source = git('rev-parse', 'HEAD')
    def clean():
        assert git('rev-parse', 'HEAD') == source
        assert not git('status', '--porcelain', '--', *DEPENDENCIES), 'commit every execution dependency first'
    clean()
    assert not OUTPUT.exists(), 'retain prior attempts; do not silently rerun the registered matrix'
    report = {'status': 'PARTIAL_EXECUTION', 'registration_source': source,
              'registration': preflight(), 'exact': exact_audit(), 'workers': []}
    def publish():
        temporary = OUTPUT.with_suffix('.tmp')
        temporary.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        temporary.replace(OUTPUT)
    publish()
    for index, case in enumerate(CASES):
        clean()
        row = bounded_case(case)
        row.update(case_index=index, execution_source=source)
        report['workers'].append(row)
        clean()
        publish()
        print(json.dumps({'case': case, 'status': row['worker_status']}), flush=True)
    report['status'] = ('COMPLETE_EXECUTION' if all(row['worker_status'] == 'EXECUTED'
                         for row in report['workers']) else 'COMPLETE_WITH_FAILURES')
    publish()
    return {'status': report['status'], 'workers': len(report['workers'])}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--exact', action='store_true')
    group.add_argument('--preflight', action='store_true')
    group.add_argument('--matrix', action='store_true')
    group.add_argument('--worker', choices=tuple(CASES))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    assert bool(args.worker) == bool(args.output)
    if args.worker:
        try:
            result = run_worker(args.worker)
        except Exception:
            args.output.write_text(json.dumps({'traceback': traceback.format_exc(), 'process_id': os.getpid()}), encoding='utf-8')
            raise
        args.output.write_text(json.dumps(result), encoding='utf-8')
    else:
        print(json.dumps(exact_audit() if args.exact else preflight() if args.preflight else matrix(), indent=2))
