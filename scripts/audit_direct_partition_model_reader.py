"""Revalidate A1's completed device result and attack collection recovery."""
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import run_direct_partition_model as model


def audit():
    retained = json.loads((ROOT/model.FIRST_ATTEMPT).read_text(encoding='utf-8'))
    recovered = model.completed_first_attempt()
    row = retained['workers'][0]
    job = model.JobRun(**row['completed_job'])
    live_reader = model.read_completed_job(job, row['result'], model.band.CASES[0])
    assert live_reader == {k: v for k, v in recovered['reader']['workers'][0].items() if k != 'case'}
    try:
        model.read_completed_job(replace(job, commit_limit=job.commit_limit+1), row['result'], model.band.CASES[0])
    except AssertionError:
        pass
    else:
        raise AssertionError('completed-job boundary accepted a changed cap')
    faults = []
    for name in ('exit', 'attachment', 'cap', 'pid', 'missing-word-row', 'readout-word',
                 'different-collection-error', 'unexecuted-case', 'false-complete-attempt'):
        changed = deepcopy(retained)
        row = changed['workers'][0]
        if name == 'exit':
            row['completed_job']['exit_code'] = 1
        elif name == 'attachment':
            row['completed_job']['attached_before_resume'] = False
        elif name == 'cap':
            row['completed_job']['commit_limit'] += 1
        elif name == 'pid':
            row['result']['process_id'] += 1
        elif name == 'missing-word-row':
            row['result']['result']['evaluation_readouts'].pop()
        elif name == 'readout-word':
            row['result']['result']['evaluation_readouts'][0][0] ^= 256
        elif name == 'different-collection-error':
            row['collection_traceback'] = 'unclassified failure'
        elif name == 'unexecuted-case':
            row['case'] = list(model.band.CASES[1])
        elif name == 'false-complete-attempt':
            changed['status'] = 'COMPLETE_WITH_RETAINED_OUTCOMES'
        try:
            model.read_report(changed)
        except AssertionError:
            faults.append(name)
        else:
            raise AssertionError('reader accepted '+name)
    assert 'torch' not in sys.modules
    return {'status': 'PASS_RETAINED_A1_COLLECTION_RECOVERY_CPU',
        'scope': 'independent reader of the retained completed seed0 job; original collection failure preserved; no device rerun',
        'recovered': recovered, 'rejected_mutations': faults}


if __name__ == '__main__':
    report = audit()
    output = ROOT/'evidence/minimal/FP_DIRECT_PARTITION_MODEL_A1_READER.json'
    if output.exists():
        assert json.loads(output.read_text()) == json.loads(json.dumps(report))
    else:
        output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
