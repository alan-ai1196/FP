"""FP Runtime: scoped CPU release frozen; complete target release remains open.

Registered CPU/CUDA installation has its own scope; no CERTIFIED_COMPLETE.
"""

from .runtime import ConstructionContract, OnlineContract, ReferenceCompilerRuntime
from .host_resources import HostResourceContract
from .policy import CompilationStep, CompilerPolicy, CudaCompilationStep, CudaCompilerPolicy
from .relation_proposal import RelationSourceSpec

__all__ = ['ConstructionContract', 'OnlineContract', 'ReferenceCompilerRuntime', 'HostResourceContract',
           'CompilationStep', 'CompilerPolicy', 'CudaCompilationStep', 'CudaCompilerPolicy', 'RelationSourceSpec']
