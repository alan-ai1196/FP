"""An actual foreign CUDA allocation invisible to native tensor counters.

This deliberately calls outside the registered Runtime executor. It is a
counterexample to promoting allocator observations into total device history,
not a legal FP action, an arena defect or a measured VRAM-residency peak.
Run in a fresh process; all foreign storage is freed before reporting.
"""
import argparse
import ctypes as C
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src/reference_compiler'))
from fp_reference.cuda_storage import CudaArena, CudaStorageContract


def audit():
    import torch
    size = 16 << 20
    arena = CudaArena(CudaStorageContract(size, size,
        {role: (size, size) for role in ('deployment', 'compiler')}))
    before = arena.snapshot()
    # Enter through Torch's runtime DLL. CUDA 13 Windows may dispatch into
    # the display driver's runtime; observe that version separately.
    lib = C.CDLL(str(Path(torch.__file__).parent/'lib/cudart64_13.dll'))
    signatures = {
        'cudaRuntimeGetVersion': [C.POINTER(C.c_int)],
        'cudaMalloc': [C.POINTER(C.c_void_p), C.c_size_t],
        'cudaMemset': [C.c_void_p, C.c_int, C.c_size_t],
        'cudaDeviceSynchronize': [], 'cudaFree': [C.c_void_p],
    }
    for key, arguments in signatures.items():
        getattr(lib, key).argtypes = arguments
        getattr(lib, key).restype = C.c_int
    def call(key, *arguments):
        result = getattr(lib, key)(*arguments)
        assert result == 0, (key, result)
    version = C.c_int()
    call('cudaRuntimeGetVersion', C.byref(version))
    assert version.value > 0
    pointer, foreign = C.c_void_p(), 32 << 20
    call('cudaMalloc', C.byref(pointer), foreign)
    try:
        assert pointer.value
        assert pointer.value+foreign <= arena._pointer or arena._pointer+size <= pointer.value
        call('cudaMemset', pointer, 0, foreign)
        call('cudaDeviceSynchronize')
        during = arena.snapshot()
    finally:
        call('cudaFree', pointer)
    after = arena.snapshot()
    assert before == during == after
    return {
        'status': 'PASS', 'torch': str(torch.__version__),
        'CUDA_build': torch.version.cuda, 'actual_runtime_version': version.value,
        'device': torch.cuda.get_device_name(),
        'direct_CUDA_allocation_written_and_freed_bytes': foreign,
        'native_arena_snapshot_unchanged_even_while_foreign_allocation_live': True,
        'native_allocation_counter': list(after['native_allocation_counter_current']),
        'scope': 'foreign-allocation counterexample to total-history inference; not a legal Runtime action or a whole-device residency peak',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit()
    if args.write:
        (ROOT/'evidence/minimal/FP_CUDA_EXTERNAL_ALLOCATION_AUDIT.json').write_text(
            json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
