"""RN-1: complete owned FP runs and an independently executed AMP posterior baseline."""
import argparse
from dataclasses import asdict, replace
from fractions import Fraction as F
import json
from math import log
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import traceback

from model import ROOT, cases, context, counts_from_training, data, exact_audit, posterior, score, unseen_pairs
from audit_reference_acceleration import fixture_parameters
from audit_reference_construction import zero_program
from audit_reference_events import online, forward_oracle
from audit_cuda_runtime import cuda_contract, audit_snapshot
from audit_cuda_policy_run import owned, host_record
from audit_float64_runtime import replay
from audit_cuda_learner import HALF, SINGLE
from audit_paired_cpu_persistence import registration
from fp_reference import ReferenceCompilerRuntime, CudaCompilerPolicy, CudaCompilationStep
from fp_reference.cuda_device import _CudaDevice
from fp_reference.cuda_installation import CudaInstallContract
from fp_reference.data_usage import StochasticStreamLaw
from fp_reference.host_resources import HostResourceContract
from fp_reference.persistence import CUDA_PATH, FLOAT64_PATH
from ingress_audit_support import deliver_context
from windows_job_audit_support import run_in_job

HOST_CAP = 4 << 30
OUTPUT = ROOT/'evidence/minimal/FP_RELATION_NOISE_EXPERIMENT.json'


def configuration(case):
    n, law, seed = case
    _, edges, train, evaluation = data(case)
    cfg, old, _, _, _ = fixture_parameters(n, groups=(0,)*n, edges=edges)
    run = online(cfg, len(train)+len(evaluation), unit=10, rate=F(0), grid=16)
    persistence = registration(bound=F(3), horizon=len(evaluation))
    rules = tuple(replace(rule, rule_id='cuda', score_path=CUDA_PATH)
                  if rule.score_path == FLOAT64_PATH else rule for rule in persistence.rules)
    run = replace(run, searches=old.searches, float64=old.float64,
        persistence=replace(persistence, rules=rules),
        data=replace(run.data, stream_law=StochasticStreamLaw(
            'RN-1 external branch-invariant noise assumption; seeded tapes alone prove no stochastic premise')))
    policy = CudaCompilerPolicy((CudaCompilationStep(len(train), 'native', 1, 'ref', 'cuda'),))
    return cfg, run, policy


def device_record(snapshot, execution_identity):
    return {'native':asdict(snapshot.identity), 'execution_identity':execution_identity,
            'physical_vram_upper':snapshot.physical_vram_upper,
            'scope':snapshot.scope}


def read_pair(n, record):
    source = tuple(v for _,v in record.sources)
    return decode_context(n, source)


def decode_context(n, source):
    assert len(source)==2*n and all(v in (F(0),F(1)) for v in source)
    assert sum(source[:n])==sum(source[n:])==1
    return source[:n].index(F(1)), source[n:].index(F(1))


def raw_ce(predictions, hidden, pairs):
    result = 0.0
    for i,j in pairs:
        label = hidden[i]^hidden[j]
        result -= .9*log(float(predictions[i,j][label]))+.1*log(float(predictions[i,j][1-label]))
    return result/len(pairs)


def scored(masses, raw, hidden, pairs):
    result = score(masses, hidden, pairs)
    result['raw_division_expected_CE_binary64'] = raw_ce(raw, hidden, pairs)
    return result


def fp_worker(case):
    n, law, seed = case
    hidden, edges, train, evaluation = data(case)
    cfg, run, policy = configuration(case)
    rt = ReferenceCompilerRuntime(cfg, zero_program(2), online=run, policy=policy,
        cuda=cuda_contract(install=CudaInstallContract()),
        host=HostResourceContract(HOST_CAP, {'deployment':HOST_CAP,'compiler':HOST_CAP}))
    base = rt.snapshot().deployed_id
    cutoff = None
    for cursor, (i,j,label) in enumerate(train+evaluation):
        prediction = deliver_context(rt, f'observation-{cursor}', context(n,i,j))
        assert prediction.status == 'PREDICTED_REFERENCE', prediction
        observed = rt.observe(label)
        assert observed.status == 'OBSERVED_REFERENCE', observed
        if cursor+1 == len(train):
            cutoff = owned(rt)
    final = owned(rt)
    assert final.halted is None and final.run.status == 'SEALED_CUDA_STREAM'
    assert final.cursor == len(train)+len(evaluation) and cutoff is not None
    revealed_train = tuple((*read_pair(n,row),row.target) for row in cutoff.observations)
    assert revealed_train == train
    counts = counts_from_training(n, revealed_train)
    session = cutoff.searches[0]
    proposal = session.relation_proposal
    candidates = [row for row in cutoff.candidates if row.candidate_id != base]
    assert len(candidates) <= 1 and len(final.install_receipts) <= 1
    cid = candidates[0].candidate_id if candidates else None
    install = final.install_receipts[0].attempt.cursor if final.install_receipts else None
    # Scores below read actual retained device outputs, never a supplied
    # graph evaluation or posterior. The candidate remains a fixed predictor
    # even when its installation changes which lineage is deployed.
    observations = {row.observation_id:row for row in final.observations}
    mass, raw, deployed_mass, deployed_raw = {}, {}, {}, {}
    for phase in final.cuda.phases:
        if phase.raw_prediction is None or phase.ordinary_cursor < len(train):
            continue
        assert phase.status == 'CHECKED_CUDA_PREFIX_PHASE'
        pair = read_pair(n, observations[phase.observation_id])
        values = tuple(SINGLE.decode(w) for w in phase.raw_prediction[3])
        probabilities = tuple(v/sum(values) for v in values)
        outputs = tuple(SINGLE.decode(w) for w in phase.raw_prediction[5])
        mass.setdefault(phase.candidate_id,{})[pair] = probabilities
        raw.setdefault(phase.candidate_id,{})[pair] = outputs
        current = cid if install is not None and phase.ordinary_cursor >= install else base
        if phase.candidate_id == current:
            deployed_mass[pair], deployed_raw[pair] = probabilities, outputs
    assert all(len(rows) == n*n for rows in mass.values()) and len(deployed_mass)==n*n
    domain = unseen_pairs(n, edges)
    native, candidate_score = None, None
    if cid is not None:
        graph = dict(cutoff.programs)[candidates[0].program_id]
        native = graph.counts()
        assert candidates[0].theta == cfg.initializer_pattern
        for i,j in mass[cid]:
            sources = dict(zip((s.source_id for s in cfg.semantics.sources), context(n,i,j)))
            p,_ = forward_oracle(graph,cfg.semantics,candidates[0].theta,sources)
            assert p == mass[cid][i,j]
        candidate_score = scored(mass[cid],raw[cid],hidden,domain)
    cuda = audit_snapshot(rt)
    cpu_phases = replay(rt)[0]
    assert cuda['phases'] == cpu_phases
    return {'kind':'FP','case':case,'run_status':final.run.status,
        'training_events':len(train),'evaluation_events':len(evaluation),'counts':counts,
        'cutoff_search_status':session.status,'cutoff_search_reason':session.reason,
        'proposal_status':None if proposal is None else proposal.status,
        'proposal_reason':None if proposal is None else proposal.reason,
        'proposal_assignment':None if proposal is None else proposal.assignment,
        'components':None if proposal is None else proposal.components,
        'native_candidate':native,'actually_compared':len(session.rows),
        'reference_proofs':len(final.reference_proofs),
        'final_policy_stage':final.compiler_policy.state.stages[0].status,
        'install_cursor':install,'alpha_spent':str(final.alpha_spent),
        'frozen_candidate_unseen':candidate_score,
        'deployed_stream_unseen':scored(deployed_mass,deployed_raw,hidden,domain),
        'independent_CUDA':cuda,'independent_binary64_phases':cpu_phases,
        'resources':{'peak_packed_bytes':final.resources['peak']['reference_payload_bytes'],
            'consumed_native_arena_extent':final.cuda.storage['consumed_arena_extent']},
        'device':device_record(final.cuda.device,final.cuda.contract.execution_identity),
        'host':host_record(final)}


def baseline_worker(case):
    n,law,seed = case
    hidden,edges,train,evaluation = data(case)
    # The learner below receives exactly this revealed training statistic.
    # Hidden bits are used only by scored(), after outputs have been captured.
    retained_training = tuple((context(n,i,j),label) for i,j,label in train)
    decoded_training = tuple((*decode_context(n,inputs),label) for inputs,label in retained_training)
    counts = counts_from_training(n,decoded_training)
    exact = posterior(n,counts,law)
    maximum_bits = max(max(v.numerator.bit_length(),v.denominator.bit_length()) for row in exact.values() for v in row)
    assert maximum_bits <= 32768
    pairs = tuple((i,j) for i in range(n) for j in range(n))
    retained_queries = tuple(context(n,i,j) for i,j,_ in evaluation)
    queries = tuple(decode_context(n,inputs) for inputs in retained_queries)
    indices = tuple(i*n+j for i,j in queries)
    assert set(queries)==set(pairs) and len(queries)==len(pairs)
    words = []
    for pair in pairs:
        for value in exact[pair]:
            excess = 10*value-1
            word = HALF.rounded(excess)
            if HALF.decode(word)>excess:
                word -= 1
            assert 0 <= HALF.decode(word) <= excess
            if word+1 < HALF.infinity:
                assert HALF.decode(word+1)>excess
            words.append(word)
    import torch
    contract = cuda_contract()
    device = _CudaDevice(contract.device,0)
    identity = (torch.__version__,torch.version.git_version,torch.version.cuda,
                torch.cuda.get_device_name(0),torch.cuda.get_device_capability(0))
    assert identity == contract.execution_identity
    assert torch.cuda.memory_allocated()==0
    with torch.no_grad():
        half = torch.tensor([float(HALF.decode(w)) for w in words],dtype=torch.float16,device='cuda').reshape(n*n,2)
        addresses = torch.tensor(indices,dtype=torch.int64,device='cuda')
        selected = half.index_select(0,addresses)
        values = selected.to(torch.float32)
        masses = values+torch.ones_like(values)
        total = masses[:,0]+masses[:,1]
        p0,p1 = masses[:,0]/total,masses[:,1]/total
        torch.cuda.synchronize()
        actual_half = tuple(w & 0xffff for w in half.view(torch.int16).cpu().flatten().tolist())
        actual_selected = tuple(w & 0xffff for w in selected.view(torch.int16).cpu().flatten().tolist())
        actual_mass = masses.view(torch.int32).cpu().tolist()
        actual_total = total.view(torch.int32).cpu().tolist()
        actual_p0 = p0.view(torch.int32).cpu().tolist()
        actual_p1 = p1.view(torch.int32).cpu().tolist()
    assert actual_half == tuple(words)
    assert actual_selected == tuple(words[2*index+j] for index in indices for j in (0,1))
    normalized,raw = {},{}
    for index,pair in enumerate(queries):
        address = indices[index]
        expected_mass = tuple(SINGLE.rounded(1+HALF.decode(w)) for w in words[2*address:2*address+2])
        assert tuple(actual_mass[index]) == expected_mass
        decoded = tuple(SINGLE.decode(w) for w in expected_mass)
        expected_total = SINGLE.rounded(sum(decoded))
        assert actual_total[index] == expected_total
        assert sum(decoded)<=10 and SINGLE.decode(expected_total)<=10
        outputs = actual_p0[index],actual_p1[index]
        assert outputs == tuple(SINGLE.rounded(v/SINGLE.decode(expected_total)) for v in decoded)
        normalized[pair] = tuple(v/sum(decoded) for v in decoded)
        raw[pair] = tuple(SINGLE.decode(w) for w in outputs)
    peak, reserved = torch.cuda.max_memory_allocated(),torch.cuda.max_memory_reserved()
    assert peak <= 16 << 20 and reserved <= 32 << 20
    domain = unseen_pairs(n,edges)
    return {'kind':'posterior','case':case,'counts':counts,
        'prior':'independent fair token bits; registered conditioned or IID edge law',
        'exact_unseen':score(exact,hidden,domain),
        'AMP_unseen':scored(normalized,raw,hidden,domain),
        'complete_domain_raw_predictions_checked':n*n,
        'maximum_exact_integer_bits':maximum_bits,
        'maximum_AMP_mass_probability_error':str(max(abs(a-b) for pair in pairs for a,b in zip(normalized[pair],exact[pair]))),
        'resources':{'materialized_half_table_bytes':len(words)*2,
            'native_tensor_peak_bytes':peak,'native_allocator_peak_reserved_bytes':reserved},
        'device':device_record(device.snapshot(),identity),'process_id':os.getpid()}


def bounded(kind,case):
    with tempfile.TemporaryDirectory(prefix='fp-relation-noise-',dir=ROOT) as temporary:
        assert Path(temporary).resolve().parent == ROOT
        output = Path(temporary)/'result.json'
        job = run_in_job(__file__,('--worker',kind,'--case',*map(str,case),'--worker-output',output),
                         commit_limit=HOST_CAP,timeout_ms=1200000)
        assert job.exit_code==0 and not job.timed_out, (job,output.read_text()[-8192:] if output.exists() else '')
        raw = output.read_bytes()
        assert len(raw)<=12288
        result = json.loads(raw)
        assert job.attached_before_resume and job.peak_process_commit<=HOST_CAP and job.peak_job_commit<=HOST_CAP
        if kind=='FP':
            host=result['host']
            assert (host['process_id'],host['creation_100ns'])==(job.process_id,job.process_creation_100ns)
            assert host['lifetime_process_commit_peak']<=job.peak_process_commit
        else:
            assert result['process_id']==job.process_id
        return dict(result,completed_job=asdict(job))


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).rstrip('\r\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight',action='store_true')
    parser.add_argument('--worker',choices=('FP','posterior'))
    parser.add_argument('--case',nargs=3)
    parser.add_argument('--worker-output')
    parser.add_argument('--write',action='store_true')
    parser.add_argument('--resume',action='store_true')
    args=parser.parse_args()
    if args.preflight:
        assert not(args.worker or args.case or args.write or args.resume)
        result=exact_audit()
        for case in cases():
            cfg,run,policy=configuration(case)
            assert len(run.data.active.observation_ids)==len(data(case)[2])+case[0]**2
            assert max(run.persistence.rules[0].max_epochs,run.persistence.rules[1].max_epochs)==case[0]**2
        assert 'torch' not in sys.modules
        print(json.dumps(result,indent=2))
        return
    case=None if args.case is None else (int(args.case[0]),args.case[1],int(args.case[2]))
    assert case is None or case in cases()
    if args.worker:
        assert args.worker_output and case is not None and not args.write
        try:
            result=fp_worker(case) if args.worker=='FP' else baseline_worker(case)
        except Exception:
            Path(args.worker_output).write_text(traceback.format_exc()[-12288:],encoding='utf-8')
            raise
        Path(args.worker_output).write_text(json.dumps(result),encoding='utf-8')
        return
    assert args.write and case is None
    allowed=OUTPUT.relative_to(ROOT).as_posix()
    assert all(line[3:]==allowed for line in git('status','--porcelain','--untracked-files=all').splitlines())
    revision=git('rev-parse','HEAD')
    if args.resume:
        report=json.loads(OUTPUT.read_text(encoding='utf-8'))
        assert report['status']=='PARTIAL_EXECUTION'
        assert report['registration_source']==revision, 'changed code requires an explicit reviewed resume policy'
    else:
        assert not OUTPUT.exists()
        report={'experiment':'RN-1','status':'PARTIAL_EXECUTION','registration_source':revision,
                'exact_audit':exact_audit(),'workers':[]}
    tasks=tuple((kind,case) for case in cases() for kind in ('FP','posterior'))
    assert [(r['kind'],tuple(r['case'])) for r in report['workers']]==list(tasks[:len(report['workers'])])
    for kind,case in tasks[len(report['workers']):]:
        result=bounded(kind,case)
        if report['workers']:
            assert result['device']==report['workers'][0]['device']
        if kind=='posterior':
            assert result['counts']==report['workers'][-1]['counts']
        report['workers'].append(dict(result,execution_source=revision))
        report['status']='COMPLETE_EXECUTION' if len(report['workers'])==len(tasks) else 'PARTIAL_EXECUTION'
        assert git('rev-parse','HEAD')==revision
        assert all(line[3:]==allowed for line in git('status','--porcelain','--untracked-files=all').splitlines())
        OUTPUT.write_text(json.dumps(report,indent=1)+'\n',encoding='utf-8')
        print(kind+' '+str(case)+' '+result.get('cutoff_search_status','AMP posterior checked'),flush=True)
    print(json.dumps({'status':report['status'],'workers':len(report['workers'])},indent=2))


if __name__=='__main__':
    main()
