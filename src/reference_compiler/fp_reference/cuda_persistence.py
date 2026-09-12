"""Passive CUDA evidence records; only the owning Runtime admits/reads them.

The extension keeps non-CUDA identity encodings unchanged. Phase IDs refer to
the same owned device prefix, including full queues, accumulator and clocks;
they neither reconstruct learners nor duplicate reference evidence wealth.
"""
from dataclasses import dataclass, field
from fractions import Fraction as F

from .cuda_range import CudaRange
from .persistence_state import PersistenceIdentity, PersistenceResult


@dataclass(frozen=True, kw_only=True)
class CudaPersistenceIdentity(PersistenceIdentity):
    initial_base_cuda: str
    initial_candidate_cuda: str
    current_base_cuda: str
    current_candidate_cuda: str
    base_cuda_range: tuple[CudaRange, ...] = ()
    candidate_cuda_range: tuple[CudaRange, ...] = ()


@dataclass(frozen=True)
class CudaPersistenceResult(PersistenceResult):
    authority_scope: str = field(default='conditional same-path CUDA stored-mass mean-null evidence; no complete AMP bridge, install or release authority', init=False)


@dataclass(frozen=True)
class PairedCudaPersistenceResult:
    status: str
    reference_identity: str
    cuda_identity: str
    cursor: int
    alpha_spent: F
    reason: str
    authority_scope: str = field(default='two same-path crossings on continuous reference/CUDA learners; no complete AMP bridge, install or release authority', init=False)
