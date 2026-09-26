"""Worker for the single registered complete-vocabulary CUDA relation job."""
from dataclasses import asdict
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/next_token'), str(ROOT/'scripts')]
import amp_tokens as amp
import batched_tokens as reference
import readout_relation as relation
from audit_token_amp_schedule import HOST_CAP, BOARD_CAP, ALLOCATOR_CAP, ELEMENT_CAP, EXECUTION_ID
from audit_token_reference_host import measured, text_fixture

CONTRACT = relation.PredictionContract(F(2), F(64), F(1, 100), F(1, 10**6), F(1, 10**7),
    256, ELEMENT_CAP, 4096)


def actual_text():
    d, origin, windows, targets, identity = text_fixture()
    a = amp.Arithmetic(cuda=True)
    state = amp.State.initialize(origin, a)
    kernel = amp.Kernel(d, a, element_cap=ELEMENT_CAP)
    pending = kernel.unit(state, windows, targets)
    bounds = reference.Kernel(d, element_cap=ELEMENT_CAP).bound(origin, windows, targets)
    a.xp.cuda.synchronize()
    started, previous_operations = time.perf_counter(), a.operations
    result = relation.check(bounds, pending, kernel, CONTRACT)
    a.xp.cuda.synchronize()
    elapsed = time.perf_counter()-started
    assert result['prediction_coordinates'] == 50257*512
    assert result['actual_readout_output_words'] == 3*50257*512
    assert result['target_cache_checks'] == 512
    assert state.read(a) == origin
    # Keep sufficient aggregate evidence; the exact sums are replayable from
    # the retained source/definition and recipe, not a vocabulary-sized dump.
    exact_sums = result.pop('exact_stored_sum')
    result['maximum_stored_sum_denominator_bits'] = max(v.denominator.bit_length() for v in exact_sums)
    result.update(status='PASS_ACTUAL_COMPLETE_TOKEN_PREDICTION_RELATION', source=identity,
        contract={key: str(value) if type(value) is F else value for key, value in asdict(CONTRACT).items()},
        complete_readout_check_seconds=elapsed, physical_readout_operations=a.operations-previous_operations,
        previous_origin_unchanged=True, optimizer_commits=0, loss_scored=False,
        reference_values_used_for_physical_readout=False)
    return result


def worker(output):
    from fp_reference.host_resources import HostResourceContract, _WindowsProcessHost
    from fp_reference.cuda_device import CudaDeviceContract, _CudaDevice
    host = _WindowsProcessHost(HostResourceContract(HOST_CAP, {'deployment': HOST_CAP, 'compiler': HOST_CAP}))
    before = measured(host)
    result, code = {}, 0
    try:
        import torch
        identity = (str(torch.__version__), torch.version.git_version, torch.version.cuda,
            torch.cuda.get_device_name(0), tuple(torch.cuda.get_device_capability(0)))
        if identity != EXECUTION_ID:
            raise RuntimeError('actual Torch/CUDA/device build differs from registered target')
        device = _CudaDevice(CudaDeviceContract(BOARD_CAP, {'deployment': BOARD_CAP, 'compiler': BOARD_CAP}), 0)
        torch.set_num_threads(1)
        torch.cuda.set_per_process_memory_fraction(ALLOCATOR_CAP/torch.cuda.get_device_properties(0).total_memory, 0)
        torch.cuda.reset_peak_memory_stats(0)
        result = actual_text()
        result.update(before=before, after=measured(host), device=asdict(device.check()), build=list(identity),
            allocator_cap=ALLOCATOR_CAP, max_allocated=torch.cuda.max_memory_allocated(0),
            max_reserved=torch.cuda.max_memory_reserved(0))
        assert result['max_reserved'] <= ALLOCATOR_CAP
    except Exception as error:
        result = dict(status='FAILED', error_type=type(error).__name__, reason=str(error)[:2000], before=before,
            after=measured(host))
        code = 2
    Path(output).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return code


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    raise SystemExit(worker(args.output))
