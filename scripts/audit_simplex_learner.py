"""Owned reference/binary64 and AMP audits of the registered simplex learner.

Exact posterior comparisons are limited to the explicit affine relation graph;
negative updates and unsupported initializer states must stay unresolved.
"""
from dataclasses import asdict, replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
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
import simplex_gradient as model
from predictive_counts import normalize, weights_from_history
from fp_reference import CompilerPolicy, CudaCompilerPolicy, ReferenceCompilerRuntime
from fp_reference.data_usage import DataContract, SourceRead, StreamSpec, StochasticStreamLaw
from fp_reference.cuda_installation import CudaInstallContract
from fp_reference.float64_bridge import Float64Contract
from fp_reference.installation import CpuInstallContract
from fp_reference.host_resources import HostResourceContract
from fp_reference.learner import SIMPLEX_GRADIENT, LearnerSpec
from fp_reference.native_search import GrammarCursor, GrammarLimits
from fp_reference.persistence import REFERENCE_PATH, FLOAT64_PATH, CUDA_PATH
from fp_reference.policy import CompilationStep, CudaCompilationStep
from fp_reference.profile import ProfileSpec
from fp_reference.program import Program, Sum
from fp_reference.relation_proposal import RelationSourceSpec
from fp_reference.runtime import OnlineContract
from fp_reference.search import ReferenceSearchSpec, likelihood
from fp_reference.simplex_relation_proposal import SOLVER, MARGINAL_SOLVER, SOLVERS
from audit_reference_construction import contract, limits, validate_residency
from audit_float64_runtime import replay
from ingress_audit_support import deliver_context

HOST_CAPS = {'cpu': 512 << 20, 'cuda': 4 << 30}
TIMEOUT = 180_000
CASES = tuple((path,n,profiles,passes) for path in ('cpu','cuda')
              for n,profiles,passes in ((2,False,1),(3,False,1),(2,True,1),(3,True,2)))
OUTPUT = ROOT/'evidence/minimal/FP_SIMPLEX_LEARNER_AUDIT.json'
DEPENDENCIES = ('src/reference_compiler','scripts','experiments/joint_uncertainty/simplex_gradient.py',
                'experiments/joint_uncertainty/predictive_counts.py','theory/proofs/SIMPLEX_RUNTIME_CONTRACT.md')


def fixture(n=2, *, unit=1, rate=F(1), solver=SOLVER):
    assert solver in SOLVERS
    if solver == MARGINAL_SOLVER:
        from positive_pair_marginals import relation_graph
        rules, graph, worlds = relation_graph(n)
    else:
        rules, graph, worlds = model.relation_graph(n)
    tape = (((0, 1, 0), (0, 1, 0), (0, 1, 1), (1, 0, 1), (0, 0, 1), (0, 1, 0)) if n == 2 else
            ((0, 1, 0), (1, 2, 0), (0, 2, 1), (0, 1, 1), (2, 2, 0), (0, 2, 0)))
    rows = tuple(tuple(model.context(n, i, j).values()) for i, j in product(range(n), repeat=2))
    theta = (F(1),)+(F(1, len(worlds)),)*len(worlds)
    cfg = replace(contract(source_domain=False, pattern=theta), semantics=rules, source_domain=rows,
                  activation_cap=F(16), normalizer_cap=F(16), reference_integer_bits=32768,
                  limits=limits(byte_cap=512 << 20, work_cap=10**11))
    ids = tuple(f'simplex-{i}' for i in range(len(tape)))
    reads = tuple(SourceRead(s.source_id, 'input', index, 0) for index, s in enumerate(rules.sources))
    data = DataContract((StreamSpec('online', 'online', ids),), 'online', (F(1),)*(2*n), reads)
    learner = LearnerSpec(unit, rate, optimizer_id=SIMPLEX_GRADIENT,
                          simplex_slots=tuple(range(1, len(worlds)+1)))
    online = OnlineContract(data, learner, profiles=(ProfileSpec('once', ids[:2], 1), ProfileSpec('twice', ids[:2], 2)),
                            float64=Float64Contract(F(1, 10**9), F(1, 10**9)))
    return cfg, graph, online, tape


def owned(n=2, *, profiles=False, cuda=False, passes=1, bounded=False, solver=SOLVER, encoding=False):
    assert not encoding or cuda
    cfg, graph, online, tape = fixture(n, solver=solver)
    zero = Program((Sum('mass', ()),), graph.slot_count, (0, 0))
    options = {'policy': CompilerPolicy(())}
    cut = 2
    if profiles:
        from audit_paired_cpu_persistence import registration
        tape = tape[:cut]+((0, 1, 0),)*40+tape[cut:]
        ids = tuple(f'simplex-{i}' for i in range(len(tape)))
        data = replace(online.data, streams=(StreamSpec('online', 'online', ids),),
            stream_law=StochasticStreamLaw('external branch-invariant stochastic relation producer; audit tape alone proves no probability law'))
        profile = ProfileSpec('warm', ids[:cut], passes)
        bounds = GrammarLimits(**{key: graph.counts()[key] for key in cfg.graph_limits})
        source = RelationSourceSpec(tuple((f'x0:{j}', f'x1:{j}') for j in range(n)), solver=solver)
        search = ReferenceSearchSpec('native', bounds, ids[:cut], profile.profile_id, relation_sources=source)
        online = replace(online, data=data, profiles=(profile,), searches=(search,),
            cpu_install=CpuInstallContract(), persistence=registration(bound=F(6), horizon=40))
        options['policy'] = CompilerPolicy((CompilationStep(cut, 'native', 1, 'ref', 'finite'),))
    if cuda:
        from audit_cuda_runtime import cuda_contract
        options = {'policy': CudaCompilerPolicy(()), 'cuda': cuda_contract(
            state_atol=F(1, 100), probability_atol=F(1, 1000), phase_output_cells=4096, phase_evidence_bytes=262144,
            install=CudaInstallContract() if profiles else None)}
        if encoding:
            from fp_reference.likelihood_encoding import LikelihoodEncodingContract
            options['cuda'] = replace(options['cuda'], likelihood_encoding=LikelihoodEncodingContract())
        if profiles:
            online = replace(online, cpu_install=None, persistence=replace(online.persistence, rules=tuple(
                replace(rule, rule_id='cuda', score_path=CUDA_PATH) if rule.score_path==FLOAT64_PATH else rule
                for rule in online.persistence.rules)))
            options['policy'] = CudaCompilerPolicy((CudaCompilationStep(cut, 'native', 1, 'ref', 'cuda'),))
    cap = HOST_CAPS['cuda' if cuda else 'cpu']
    host = HostResourceContract(cap, {'deployment':cap, 'compiler':cap}) if bounded else None
    rt = ReferenceCompilerRuntime(cfg, zero if profiles else graph, online=online, host=host, **options)
    initial = rt.snapshot()
    histories = {} if profiles else {initial.deployed_id: ()}
    compared = 0
    scores = {}
    candidate_id = None
    base_id = initial.deployed_id
    for cursor, (i, j, y) in enumerate(tape):
        event = deliver_context(rt, online.data.active.observation_ids[cursor], tuple(model.context(n, i, j).values()))
        assert event.status == 'PREDICTED_REFERENCE', event
        snapshot = rt.snapshot()
        assert snapshot.pending.record.target is None
        for candidate in snapshot.candidates:
            assert candidate.theta[0] == 1 and sum(candidate.theta[1:]) == 1
            if candidate.candidate_id in histories:
                raw = weights_from_history(n, histories[candidate.candidate_id])
                weights = normalize(raw[:len(candidate.theta)-1])
                assert candidate.theta[1:] == weights
                expected = model.native_prediction(n, weights, (i, j)).probabilities
                assert dict(event.predictions)[candidate.candidate_id] == expected
                compared += 1
        if candidate_id is not None:
            obs = online.data.active.observation_ids[cursor]
            predictions = dict(event.predictions)
            scores[obs, REFERENCE_PATH] = tuple(predictions[key][y] for key in (base_id, candidate_id))
            if cuda:
                from audit_cuda_runtime import SINGLE
                values = []
                for key in (base_id, candidate_id):
                    phase = next(p for p in reversed(snapshot.cuda.phases) if p.raw_prediction is not None
                        and p.observation_id==obs and p.candidate_id==key)
                    masses = tuple(SINGLE.decode(w) for w in phase.raw_prediction[3])
                    values.append(masses[y]/sum(masses))
                scores[obs, CUDA_PATH] = tuple(values)
            else:
                finite = dict(snapshot.pending.float64_predictions)
                scores[obs, FLOAT64_PATH] = tuple(finite[key].masses[y].exact/sum(v.exact for v in finite[key].masses)
                    for key in (base_id, candidate_id))
        result = rt.observe(y)
        assert result.status == 'OBSERVED_REFERENCE', result
        histories = {key: value+((i, j, y),) for key, value in histories.items()}
        if profiles and cursor+1 == cut:
            snapshot = rt.snapshot()
            session = snapshot.searches[0]
            assert session.status=='UNRESOLVED' and session.cursor==GrammarCursor() and not session.proof_id
            assert len(session.rows)==1 and session.rows[0].status=='COMPARED_REFERENCE'
            proposal = session.relation_proposal
            assert proposal.program == graph and proposal.worlds == graph.slot_count-1
            candidate_id = session.best_candidate_id
            assert candidate_id != base_id
            histories[candidate_id] = tape[:cut]*passes
            candidate = next(c for c in snapshot.candidates if c.candidate_id==candidate_id)
            assert candidate.profile_id==profile.profile_id and candidate.birth_cursor==cut
            assert candidate.learner==snapshot.profiles[0].attached
            assert candidate.learner.optimizer_steps==cut*passes
            assert session.best_likelihood==likelihood(graph,cfg.semantics,candidate.learner,snapshot.observations,bit_limit=32768)
            assert len(snapshot.persistence_identities)==2
            assert all(p.start_cursor==cut and p.wealth==1 and p.status=='ACTIVE' for p in snapshot.persistence_identities)
    snapshot = validate_residency(rt)
    assert snapshot.halted is None
    assert snapshot.run.status == ('SEALED_CUDA_STREAM' if cuda else 'SEALED_REFERENCE_STREAM')
    assert not snapshot.reference_proofs
    assert len(snapshot.observations) == len(tape)
    if profiles:
        from audit_reference_persistence import check_gain, wealth_oracle
        assert len(snapshot.install_receipts)==1 and snapshot.deployed_id==candidate_id
        assert all(d.decision_status=='UNRESOLVED' and d.proof is None for d in snapshot.run.closure.decisions)
        identities = {p.identity_id:p for p in snapshot.persistence_identities}
        wealth = {key:F(1) for key in identities}
        crossings = {}
        for event in snapshot.persistence_events:
            rule = identities[event.identity_id].rule
            assert event.cursor>=cut and event.epoch_finished and event.wealth_before==wealth[event.identity_id]
            assert (event.base_probability,event.candidate_probability)==scores[event.observation_id,rule.score_path]
            check_gain(event)
            assert event.wealth_after==wealth_oracle(event.wealth_before,event.gain.lower,1,rule)
            wealth[event.identity_id] = event.wealth_after
            if event.wealth_after*rule.alpha>=1:
                crossings.setdefault(event.identity_id,event.cursor+1)
        assert len(crossings)==2 and all(crossings[p.identity_id]==p.crossing_cursor for p in identities.values())
        assert snapshot.install_receipts[0].attempt.cursor==max(crossings.values())
        assert snapshot.alpha_spent==F(1,2)
    else:
        assert not snapshot.install_receipts
    phases, *_ = replay(rt)
    device = None
    if cuda:
        if encoding:
            from audit_likelihood_encoding import audit_snapshot
        else:
            from audit_cuda_runtime import audit_snapshot
        device = audit_snapshot(rt)
    else:
        assert 'torch' not in sys.modules
    snapshot = validate_residency(rt)
    host = snapshot.host_resources
    host_record = None if host is None else {key:getattr(host,key) for key in
        ('process_id','creation_100ns','lifetime_process_commit_peak','job_commit_peak',
         'process_user_100ns','process_kernel_100ns','job_user_100ns','job_kernel_100ns')}
    maxima = lambda traces: {key:str(max((getattr(t.relation,key) for t in traces if t.relation is not None),default=F(0)))
        for key in ('state_error','native_error','normalizer_error','probability_error','division_error')}
    return {'n': n, 'solver': solver, 'likelihood_encoding': encoding, 'graph_counts': graph.counts(),
            'profiles': profiles, 'profile_passes': passes if profiles else 0,
            'status': snapshot.run.status, 'native_posterior_forecasts': compared,
            'independent_binary64_phases': phases, 'CUDA': device,
            'profile_events': len(snapshot.profile_events), 'retained_observations': len(snapshot.observations),
            'fresh_score_checks': len(snapshot.persistence_events),
            'install_cursor': snapshot.install_receipts[0].attempt.cursor if profiles else None,
            'class_certificate': False, 'historical_class': 'UNRESOLVED' if profiles else None,
            'binary64_maxima': maxima(snapshot.float64_traces),
            'CUDA_maxima': None if snapshot.cuda is None else maxima(snapshot.cuda.phases),
            'packed_peak': snapshot.resources['peak']['reference_payload_bytes'],
            'device': None if snapshot.cuda is None else {'identity':asdict(snapshot.cuda.device.identity),
                'execution_identity':snapshot.cuda.contract.execution_identity,
                'physical_vram_upper':snapshot.cuda.device.physical_vram_upper,'scope':snapshot.cuda.device.scope},
            'host': host_record, 'process_id': os.getpid(),
            'host_scope': 'bind to completed job separately' if bounded else 'unbounded functional audit only'}


def bounded_case(n, profiles, cuda, passes):
    from windows_job_audit_support import run_in_job
    temporary = Path(tempfile.mkdtemp(prefix='fp-simplex-audit-', dir=ROOT))
    assert temporary.resolve().parent == ROOT.resolve()
    output = temporary/'result.json'
    argv = ('--worker', '--output', str(output), '--n', str(n), '--passes', str(passes))
    argv += ('--profiles',) if profiles else ()
    argv += ('--cuda',) if cuda else ()
    cap = HOST_CAPS['cuda' if cuda else 'cpu']
    job = run_in_job(__file__, argv, commit_limit=cap, timeout_ms=TIMEOUT)
    row = {'worker_status':'FAILED', 'completed_job':asdict(job)}
    if output.exists():
        with output.open('rb') as stream:
            payload = stream.read(65537)
        assert len(payload) <= 65536
        row['result'] = json.loads(payload)
    if job.exit_code==0 and not job.timed_out and job.attached_before_resume and not job.limit_terminated_processes:
        result = row['result']
        observed = result['host']
        assert result['process_id']==job.process_id
        assert (observed['process_id'],observed['creation_100ns'])==(job.process_id,job.process_creation_100ns)
        assert observed['lifetime_process_commit_peak']<=job.peak_process_commit<=cap
        assert observed['job_commit_peak']<=job.peak_job_commit<=cap
        for clock in ('user','kernel'):
            assert max(observed[f'process_{clock}_100ns'],observed[f'job_{clock}_100ns'])<=getattr(job,f'{clock}_100ns')
        row['worker_status'] = 'EXECUTED'
    # Only this single consumed report and its now-empty own directory are
    # removed; failed/unparsed reports survive exceptions for inspection.
    if output.exists():
        output.unlink()
    temporary.rmdir()
    return row


def preflight():
    from audit_cuda_runtime import cuda_contract
    device = cuda_contract()
    return {'cases':CASES,'optimizer':SIMPLEX_GRADIENT,'unit':1,'rate':'1','grid':None,
        'initializer':'fixed slot0=1; every selected latent slot=1/K, K=2^(n-1)',
        'profile_cut':2,'profile_passes':'one for n2; two for n3',
        'ordinary_events':6,'profiled_run_events':46,'retained_source_domain':'all n^2 current ordered pairs; no delayed sources',
        'fresh':{'bound':'6','bet':'3/4','alpha_per_path':'1/4','total_alpha':'3/4','epoch_events':1,'max_epochs':40},
        'native_range_caps':'16','reference_integer_bits':32768,'binary64_tolerances':'1/1000000000',
        'AMP_state_native_normalizer_tolerance':'1/100','AMP_probability_tolerance':'1/1000',
        'host_caps':HOST_CAPS,'timeout_ms':TIMEOUT,'packed_cap':512<<20,'work_per_role':10**11,
        'native_arena_bytes':device.storage.arena_bytes,'native_allocator_bytes':device.storage.allocator_reserved_cap,
        'phase_output_cells':4096,'phase_evidence_bytes':262144,
        'execution_identity':device.execution_identity,
        'scope':'finite owned extension audit; fixed known prior/noise; not a matched model comparison or a historical class optimum'}


def matrix(write=False,resume=False):
    def git(*args):
        return subprocess.run(('git',*args),cwd=ROOT,capture_output=True,encoding='utf-8',check=True).stdout.strip()
    source = git('rev-parse','HEAD')
    def source_clean():
        assert git('rev-parse','HEAD')==source
        assert not git('status','--porcelain','--',*DEPENDENCIES),'commit the complete execution dependencies before the registered matrix'
    source_clean()
    registration = json.loads(json.dumps(preflight()))
    if resume:
        report = json.loads(OUTPUT.read_text(encoding='utf-8'))
        assert report['status']=='PARTIAL_EXECUTION' and report['registration_source']==source
        assert report['registration']==registration
        assert [r['case_index'] for r in report['workers']]==list(range(len(report['workers'])))
    else:
        assert not write or not OUTPUT.exists(),'retain earlier evidence; do not silently rerun the matrix'
        report = {'status':'PARTIAL_EXECUTION','registration_source':source,'registration':registration,'workers':[]}
    def publish():
        if write:
            temporary = OUTPUT.with_suffix('.tmp')
            temporary.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
            temporary.replace(OUTPUT)
    publish()
    for index in range(len(report['workers']),len(CASES)):
        path,n,profiles,passes = CASES[index]
        source_clean()
        row = bounded_case(n,profiles,path=='cuda',passes)
        row.update(case_index=index,case=CASES[index],execution_source=source)
        report['workers'].append(row)
        source_clean(); publish()
        print(json.dumps({'case':index,'status':row['worker_status']}),flush=True)
    report['status'] = 'COMPLETE_EXECUTION' if all(r['worker_status']=='EXECUTED' for r in report['workers']) else 'COMPLETE_WITH_FAILURES'
    publish()
    return {'status':report['status'],'workers':len(report['workers']),
            'executed':sum(r['worker_status']=='EXECUTED' for r in report['workers'])}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cuda', action='store_true')
    parser.add_argument('--n', type=int, choices=(2, 3), default=2)
    parser.add_argument('--profiles', action='store_true')
    parser.add_argument('--passes', type=int, choices=(1,2), default=1)
    parser.add_argument('--bounded', action='store_true')
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--output')
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--matrix', action='store_true')
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    assert args.worker == bool(args.output)
    assert not args.resume or args.matrix and args.write
    assert not args.write or args.matrix
    assert not (args.worker and (args.matrix or args.preflight))
    if args.worker:
        try:
            result = owned(args.n, profiles=args.profiles, cuda=args.cuda, passes=args.passes, bounded=True)
        except Exception:
            Path(args.output).write_text(json.dumps({'traceback':traceback.format_exc(),'process_id':os.getpid()}),encoding='utf-8')
            raise
        Path(args.output).write_text(json.dumps(result),encoding='utf-8')
    else:
        print(json.dumps(matrix(args.write,args.resume) if args.matrix else preflight() if args.preflight else
            bounded_case(args.n,args.profiles,args.cuda,args.passes) if args.cuda or args.bounded else
            owned(args.n,profiles=args.profiles,passes=args.passes),indent=2))
