"""Owned prospective installation while the original native class stays unresolved."""
import argparse
from dataclasses import asdict, replace
from fractions import Fraction as F
from itertools import product
import json
from math import prod
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import traceback
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]
from fp_reference import ReferenceCompilerRuntime, CompilerPolicy, CompilationStep, CudaCompilerPolicy, CudaCompilationStep
from fp_reference.data_usage import ObservationRecord
from fp_reference.empirical_bound import empirical_upper
from fp_reference.host_resources import HostResourceContract
from fp_reference.persistence import CUDA_PATH, FLOAT64_PATH
from fp_reference.relation_proposal import relation_proposal
from fp_reference.resources import ResourceExceeded
from fp_reference.semantics import ArithmeticUnresolved
from fp_reference.cuda_installation import CudaInstallContract
from audit_reference_acceleration import fixture_parameters, context, ingest
from audit_reference_construction import zero_program, validate_residency, rejects
from audit_reference_events import forward_oracle
from audit_cpu_installation import configuration
from audit_float64_runtime import replay
from audit_cuda_runtime import cuda_contract, audit_snapshot
from audit_cuda_policy_run import parameters as cuda_policy_parameters, host_record
from windows_job_audit_support import run_in_job

HOST_CAP = 4 << 30
CASES = ('bounded', 'scale1', 'enumerated', 'authority', 'partial', 'stale', 'resource', 'transport')
CUDA_RESOURCE_CASE = 'cpu-work-on-cuda'


def scale_audit():
    cfg, run, _, _, _ = fixture_parameters(3)
    records_by_counts = {}
    for counts in product(range(11), repeat=2):
        records = []
        for edge, zeroes in enumerate(counts):
            values = context(3, edge, edge+1)
            sources = tuple((s.source_id, v) for s, v in zip(cfg.semantics.sources, values))
            for at in range(10):
                i = len(records)
                records.append(ObservationRecord(f'o{i}', 'train', 'train', i, values, sources, int(at >= zeroes)))
        records_by_counts[counts] = tuple(records)
    checked = proposed = 0
    for pattern, slots in (((F(1), F(8)), 2), ((F(1), F(7)), 2),
                           ((F(0), F(1), F(8)), 3), ((F(1), F(8), F(1)), 3),
                           ((F(1), F(8)), 1)):
        grammar = replace(run.searches[0].grammar, slots=slots)
        for counts, records in records_by_counts.items():
            upper = empirical_upper(records, cfg.semantics, bit_limit=32768)
            proposal = relation_proposal(upper, cfg.semantics, grammar, pattern,
                run.searches[0].relation_sources, bit_limit=32768)
            checked += 1
            if 5 in counts:
                assert proposal.program is None
                continue
            assert proposal.program is not None and proposal.scale in pattern[:slots]
            M, m = sum(max(c, 10-c) for c in counts), sum(min(c, 10-c) for c in counts)
            scores = [((a+1)/(a+2))**M*(1/(a+2))**m for a in pattern[:slots]]
            assert proposal.scale == pattern[scores.index(max(scores))]
            actual = prod(forward_oracle(proposal.program, cfg.semantics,
                pattern[:proposal.program.slot_count], dict(record.sources))[0][record.target] for record in records)
            assert actual == max(scores) <= upper.likelihood
            proposed += 1
    records = records_by_counts[10, 10]
    upper = empirical_upper(records, cfg.semantics, bit_limit=32768)
    rejects(lambda: relation_proposal(upper, cfg.semantics, run.searches[0].grammar,
        (F(1), F(8)), run.searches[0].relation_sources, bit_limit=8), ArithmeticUnresolved)
    assert 'torch' not in sys.modules
    return {'count_pattern_and_initializer_cases': checked, 'native_likelihood_checks': proposed,
            'integer_cap_failure_refuses_a_proposal': True}


def make_runtime(path, kind, *, automatic):
    if kind in ('enumerated', CUDA_RESOURCE_CASE):
        cfg, run = configuration()
        if path == 'cuda' and kind == 'enumerated':
            cfg, _, run = cuda_policy_parameters()
        train = tuple(((F(1), F(0)), 0) for _ in range(2))
        fresh = tuple(((F(1), F(0)), 0) for _ in range(38))
        transitions = 11  # First improved witness: seven members, class still live.
    else:
        cfg, run, _, train, fresh = fixture_parameters(3, groups=(0, 0, 0))
        changed = (6, 7, 8, 16, 17, 18) if kind == 'scale1' else (8,)
        train = tuple((values, label ^ int(i in changed)) for i, (values, label) in enumerate(train))
        transitions = 1  # 8:2 and 9:1 rows; proposed scale8 cannot attain their upper.
    cuda = None
    if path == 'cuda':
        rules = tuple(replace(r, rule_id='cuda', score_path=CUDA_PATH) if r.score_path == FLOAT64_PATH else r
                      for r in run.persistence.rules)
        run = replace(run, persistence=replace(run.persistence, rules=rules), cpu_install=None)
        cuda = cuda_contract(install=CudaInstallContract())
        policy = CudaCompilerPolicy((CudaCompilationStep(len(train), 'native', transitions, 'ref', 'cuda'),))
    else:
        policy = CompilerPolicy((CompilationStep(len(train), 'native', transitions, 'ref', 'finite'),))
    host = HostResourceContract(HOST_CAP, {'deployment': HOST_CAP, 'compiler': HOST_CAP})
    rt = ReferenceCompilerRuntime(cfg, zero_program(2), online=run,
        cuda=cuda, policy=policy if automatic else None, host=host)
    return rt, train, fresh, transitions


def evidence(rt, path, candidate):
    ref = rt.admit_reference_persistence(candidate, 'ref')
    physical = rt.admit_cuda_persistence(candidate, 'cuda') if path == 'cuda' else rt.admit_float64_persistence(candidate, 'finite')
    assert ref.identity_id and physical.identity_id
    return ref.identity_id, physical.identity_id


def install(rt, path, candidate, ids, **extra):
    action = rt.install_cuda if path == 'cuda' else rt.install_cpu
    field = 'cuda_identity' if path == 'cuda' else 'float64_identity'
    return action(candidate, reference_identity=ids[0], **{field: ids[1]}, **extra)


def worker(path, case):
    automatic = case in ('bounded', 'scale1', 'enumerated', CUDA_RESOURCE_CASE)
    rt, train, fresh, transitions = make_runtime(path, case, automatic=automatic)
    ingest(rt, train)
    cutoff = rt.snapshot()
    if automatic:
        stage = cutoff.compiler_policy.state.stages[0]
        assert stage.status == 'EVIDENCE' and stage.proof_id is None
        candidate = stage.candidate_id
        assert not cutoff.reference_proofs and not cutoff.searches[0].cursor.done
        ingest(rt, fresh, start=len(train))
        final = validate_residency(rt)
        assert not final.reference_proofs and final.alpha_spent == F(1, 2)
        assert len(final.searches[0].rows) == (1 if case in ('bounded', 'scale1') else 7)
        if case == CUDA_RESOURCE_CASE:
            assert path == 'cuda' and final.run.status == 'HALTED_UNRESOLVED'
            assert final.halted == ('run-closure', 'ResourceExceeded: compiler cumulative work exhausted')
            assert not final.install_receipts and final.deployed_id == cutoff.deployed_id
            assert 'deployment cumulative work exhausted' in final.compiler_policy.state.stages[0].reason
            outcome = 'CPU work allowance cannot fund CUDA installation or terminal reporting; no false completion'
        else:
            assert final.run.status == ('SEALED_CUDA_STREAM' if path == 'cuda' else 'SEALED_REFERENCE_STREAM'), (final.run.status, final.halted, final.compiler_policy.state.stages[0])
            assert all(d.decision_status == 'UNRESOLVED' and d.proof is None for d in final.run.closure.decisions)
            if case == 'scale1':
                assert cutoff.searches[0].relation_proposal.scale == 1
                assert next(c.theta for c in cutoff.candidates if c.candidate_id == candidate) == (F(1),)
                assert not final.install_receipts and final.deployed_id == cutoff.deployed_id
                outcome = 'actual one-slot initialized scale1; finite evidence ends without installation or class completion'
            else:
                assert len(final.install_receipts) == 1
                assert final.install_receipts[0].attempt.proposal_proof_id is None and final.deployed_id == candidate
                outcome = 'installed continuous candidate; original full class remains unresolved'
    else:
        opened = rt.start_reference_search('native')
        selected = rt.advance_reference_search(opened.search_id, transitions=transitions)
        assert selected.status == 'UNRESOLVED' and selected.proof_id is None
        candidate = selected.best_candidate_id
        assert candidate != cutoff.deployed_id
        ids = evidence(rt, path, candidate)
        assert install(rt, path, candidate, ids).status == 'UNRESOLVED'  # Before any fresh score.
        ingest(rt, fresh[:20], start=len(train))
        before = rt.snapshot()
        paired = rt.paired_cuda_persistence_result if path == 'cuda' else rt.paired_persistence_result
        assert paired(*ids).status == ('PAIRED_CUDA_CROSSED' if path == 'cuda' else 'PAIRED_CPU_CROSSED')
        if case == 'authority':
            assert install(rt, path, candidate, ids, proposal_proof_id='unowned-maximum').status == 'UNRESOLVED'
            rejects(lambda: install(rt, path, candidate, ids, proposal_proof_id=True))
            rejects(lambda: install(rt, path, candidate, ids[::-1]))
            graph = dict(before.programs)[next(c.program_id for c in before.candidates if c.candidate_id == candidate)]
            newborn = rt.construct_candidate(graph)
            assert newborn.candidate_id and newborn.candidate_id != candidate
            assert install(rt, path, newborn.candidate_id, ids).status == 'UNRESOLVED'
            assert rt.snapshot().deployed_id == before.deployed_id and not rt.snapshot().install_receipts
            # The original correctly identified pair remains independently usable.
            assert install(rt, path, candidate, ids).status == ('INSTALLED_CUDA' if path == 'cuda' else 'INSTALLED_CPU')
            outcome = 'unknown assertion, boolean, wrong path and same-graph newborn refused; actual pair installs'
        elif case == 'partial':
            ingest(rt, fresh[20:21], start=len(train)+20)
            assert install(rt, path, candidate, ids).status == 'UNRESOLVED'
            assert any(c.learner.unit_count for c in rt.snapshot().candidates)
            outcome = 'partial optimizer unit retained; installation refused'
        elif case == 'stale':
            cancel = rt.cancel_cuda_persistence if path == 'cuda' else rt.cancel_float64_persistence
            cancel(ids[1])
            assert install(rt, path, candidate, ids).status == 'UNRESOLVED'
            outcome = 'cancelled same-path evidence cannot authorize installation or refund alpha'
        elif case == 'resource':
            original = rt._ledger.charge_work
            def refuse(role, costs, *, note=''):
                if note.endswith(':prepare-complete-root'):
                    raise ResourceExceeded('audit: installation preparation work unavailable')
                return original(role, costs, note=note)
            with patch.object(rt._ledger, 'charge_work', refuse):
                assert install(rt, path, candidate, ids).status == 'UNRESOLVED'
            outcome = 'prospective authority cannot bypass paid installation preparation'
        else:
            assert case == 'transport'
            original = rt._machine.realize
            def corrupt(object_id, label, value, chi):
                if label == 'prepared_cuda_install_receipt':
                    phase = rt._cuda.current[candidate]
                    rt._cuda._values[phase].gradient_sum.unsqueeze_(0)
                return original(object_id, label, value, chi)
            if path == 'cuda':
                with patch.object(rt._machine, 'realize', corrupt):
                    rejects(lambda: install(rt, path, candidate, ids))
                assert rt.snapshot().halted
            else:
                rt._unexpected_state = 1
                assert install(rt, path, candidate, ids).status == 'UNRESOLVED'
            outcome = 'unproved complete-state/device transport refused'
        final = rt.snapshot()
        if case != 'authority':
            assert final.deployed_id == before.deployed_id and not final.install_receipts
        assert not final.reference_proofs and final.alpha_spent == F(1, 2)
    # All *executed* earlier phases remain replayable even after a terminal
    # externally injected metadata fault; that fault grants no valid future.
    cpu_phases = replay(rt)[0]
    gpu = audit_snapshot(rt) if path == 'cuda' else None
    if gpu is not None:
        assert gpu['phases'] == cpu_phases
    final = rt.snapshot()
    return {'path': path, 'case': case, 'outcome': outcome, 'cursor': final.cursor,
        'reference_proofs': len(final.reference_proofs), 'alpha_spent': str(final.alpha_spent),
        'install_cursors': [r.attempt.cursor for r in final.install_receipts],
        'binary64_phases': cpu_phases, 'CUDA': gpu,
        'peak_packed_bytes': final.resources['peak']['reference_payload_bytes'],
        'host': host_record(final),
        'device': None if final.cuda is None else {
            'identity': asdict(final.cuda.device.identity),
            'physical_vram_upper': final.cuda.device.physical_vram_upper,
            'role_physical_vram_upper': dict(final.cuda.device.role_physical_vram_upper),
            'scope': final.cuda.device.scope},
        'execution_identity': None if final.cuda is None else final.cuda.contract.execution_identity,
        'process_id': os.getpid()}


def bounded(path, case):
    with tempfile.TemporaryDirectory(prefix='fp-prospective-', dir=ROOT) as directory:
        assert Path(directory).resolve().parent == ROOT
        output = Path(directory)/'result.json'
        job = run_in_job(__file__, ('--worker', '--path', path, '--case', case, '--output', output),
                         commit_limit=HOST_CAP, timeout_ms=1200000)
        assert job.exit_code == 0 and not job.timed_out, (case, job, output.read_text(encoding='utf-8') if output.exists() else '')
        raw = output.read_bytes()
        assert len(raw) < 16384
        result = json.loads(raw)
        assert result['process_id'] == job.process_id and job.attached_before_resume
        assert max(job.peak_process_commit, job.peak_job_commit) <= HOST_CAP
        assert (result['host']['process_id'], result['host']['creation_100ns']) == (job.process_id, job.process_creation_100ns)
        assert result['host']['lifetime_process_commit_peak'] <= job.peak_process_commit
        return dict(result, completed_job=asdict(job))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--path', choices=('cpu', 'cuda'), default='cpu')
    parser.add_argument('--case', choices=CASES+(CUDA_RESOURCE_CASE,))
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--output')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.worker:
        assert args.case and args.output and not args.write
        try:
            result = worker(args.path, args.case)
        except Exception:
            Path(args.output).write_text(traceback.format_exc()[-16384:], encoding='utf-8')
            raise
        Path(args.output).write_text(json.dumps(result), encoding='utf-8')
        return
    assert not args.output and (not args.write or args.case is None)
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if args.write:
        assert not subprocess.check_output(['git', 'diff', 'HEAD', '--', 'src', 'scripts'], cwd=ROOT)
    report = {'source_revision': source, 'scale_audit': scale_audit() if args.case is None else None, 'workers': []}
    cases = CASES+(CUDA_RESOURCE_CASE,) if args.path == 'cuda' else CASES
    for case in (cases if args.case is None else (args.case,)):
        result = bounded(args.path, case)
        if report['workers']:
            assert result['device'] == report['workers'][0]['device']
            assert result['execution_identity'] == report['workers'][0]['execution_identity']
        report['workers'].append(result)
        print(args.path+' '+case+': '+result['outcome'], flush=True)
    if args.write:
        output = ROOT/'evidence/minimal'/('FP_PROSPECTIVE_SELECTION_'+args.path.upper()+'_AUDIT.json')
        output.write_text(json.dumps(report, indent=1)+'\n', encoding='utf-8')
    print(json.dumps({'workers': len(report['workers']),
        'binary64_phases': sum(r['binary64_phases'] for r in report['workers']),
        'scale_audit': report['scale_audit']}, indent=2))


if __name__ == '__main__':
    main()
