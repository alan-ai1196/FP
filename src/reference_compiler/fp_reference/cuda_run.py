"""Passive finite CUDA run records; only the complete Runtime seals a run."""
from dataclasses import dataclass, field

from .cuda_device import CudaDeviceSnapshot
from .cuda_installation import CudaTransport
from .run_state import ReferenceRunClosure, ReferenceRunSnapshot, prediction_diagnostics
from .cuda_prefix import widened_prediction


@dataclass(frozen=True, kw_only=True)
class CudaRunClosure(ReferenceRunClosure):
    cuda_device: CudaDeviceSnapshot
    cuda_transport: CudaTransport
    checked_cuda_phases: int
    unresolved_cuda_phases: int
    execution: str = field(default='SEALED_CUDA_STREAM', init=False)
    authority: str = field(default='finite owned reference/CUDA stream and policy; no future authority, CERTIFIED_COMPLETE, population or target release claim', init=False)


@dataclass(frozen=True)
class CudaRunSnapshot(ReferenceRunSnapshot):
    report_scope: str = field(default='this header and the complete RuntimeSnapshot, including owned CUDA phases, device/framebuffer, tensor arena, host and packed resource histories', init=False)


def cuda_diagnostics(prefix, bit_limit):
    # Runtime prepays this scan. Raw phase words are already owned evidence;
    # no kernel rerun, callback, new forecast or supplied resource observation.
    if prefix.indexed:
        predictions = (phase.raw_prediction.decoded() for phase in prefix.phases.values()
            if phase.status == 'CHECKED_CUDA_PREFIX_PHASE' and phase.raw_prediction is not None)
        return prediction_diagnostics(predictions, 'indexed-cuda-half-single', bit_limit)
    predictions = (widened_prediction(phase.raw_prediction) for phase in prefix.phases.values()
        if phase.status == 'CHECKED_CUDA_PREFIX_PHASE' and phase.raw_prediction is not None)
    return prediction_diagnostics(predictions, 'cuda-half-single', bit_limit)
