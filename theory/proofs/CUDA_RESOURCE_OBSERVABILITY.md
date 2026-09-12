# What the current CUDA resource observations can establish

Status: **actual allocation counterexample, observation-scope proof and
runtime-version correction.** The existing native tensor-arena theorem is
unchanged. The counterexample deliberately executes outside the registered
Runtime API; it does not falsify Foundation R4 or add a legal FP action.
Complete target resources/run/release remain open under frozen ERC-1.

## 1. A foreign allocation is invisible even while live

Run `python -B scripts/audit_cuda_external_allocations.py --write` in a fresh
process. The script first creates the registered 16 MiB native arena. It
then enters the CUDA Runtime through the DLL in this Torch installation,
successfully allocates a disjoint **32 MiB** buffer using `cudaMalloc`, writes
it with `cudaMemset`, synchronizes and finally frees it with `cudaFree`.
All API calls succeed. Foreign storage is freed before reporting.

The complete `CudaArena.snapshot()` is identical before allocation, while
the written foreign buffer is still live, and after its release. Its native
allocation counter remains `(1, 16777216, 1)`, and all native current/peak/
reservation fields are unchanged. The small actual result is
[`FP_CUDA_EXTERNAL_ALLOCATION_AUDIT.json`](../../evidence/minimal/FP_CUDA_EXTERNAL_ALLOCATION_AUDIT.json).
No weights, native handles or raw process list are retained.

This matches the scope in the [PyTorch memory documentation](https://docs.pytorch.org/docs/main/torch_cuda_memory):
allocator snapshots cover memory managed through that allocator; direct CUDA
allocations can be absent. The prior
[freed PyTorch allocation witness](BOUNDED_CUDA_TENSOR_STORAGE.md) increases
the native lifetime counter. This direct-CUDA witness does not.

Let O(h) be the sequence of native arena observations and let A(h) include
direct CUDA allocation history. The two traces with and without the foreign
allocation have equal O and unequal A. Consequently O alone cannot determine
total CUDA allocation history or decide a resource limit that distinguishes
those traces. Increasing the sampling rate of O does not repair an allocation
that remains invisible while live.

**Scope of the obstruction.** This is a projection/observation statement,
not equality of complete Runtime states. The foreign calls are not legal
public FP controls. An executor proof may exclude such calls, but any
broader resource claim must also establish its coverage of platform and
driver allocations. A sound conservative reservation covering both traces
could resolve the uncertainty; the counterexample does not rule out that
approach. It rules out deriving the broader claim from native counters alone.
Nor does the script measure an exact whole-device physical-residency peak:
a successful CUDA allocation and write is not a Windows residency oracle.

## 2. Build identity and actual Windows runtime differ

On this execution, Torch reports `2.12.0+cu132` and `torch.version.cuda='13.2'`.
The shipped DLL's version description is 13.2.75. However, the actual
`cudaRuntimeGetVersion` query returns **13040**, meaning 13.4.

The [NVIDIA version-management documentation](https://docs.nvidia.com/cuda/cuda-runtime-api/cuda_runtime_api/group__CUDART____VERSION.html)
explains that Windows CUDA 13 can use the runtime packaged with the display
driver. The runtime query can therefore differ from the application's
build toolkit. This is not evidence that the Torch wheel was modified.

Earlier FP records named the value of `torch.version.cuda` `CUDA_runtime`.
That field is a **build tag**, not an actual-runtime query. Existing immutable
artifacts retain their recorded bytes; this note corrects their interpretation.
The current `CudaPrefixContract.execution_identity` likewise binds the Torch
build tag, device and capability, not the separately queried runtime/driver
version. Target resource/run registration still needs that distinction.
The finite actual arithmetic replays and per-forecast exact conformance
checks remain evidence for their executed outputs; this correction supplies
no unobserved-kernel or new release authority.

## 3. Current platform queries are not hard peak bounds

Read-only inspection identifies this card as RTX 3090, driver 616.92, WDDM,
with 24,576 MiB reported total memory. Its `nvidia-smi` process-memory entries
are unavailable. This agrees with the
[NVML process-memory specification](https://docs.nvidia.com/deploy/pdf/NVML_API_Reference_Guide.pdf):
under WDDM the operating system manages memory and that process field is
unavailable. A global used-memory sample does not assign usage to this FP root.

[DXGI's video-memory information](https://learn.microsoft.com/en-us/windows/win32/api/dxgi1_4/ns-dxgi1_4-dxgi_query_video_memory_info)
offers process current usage and an OS budget. Its budget is a target and
its reservation a working-set hint; neither is an enforced application cap.
Those documented semantics alone cannot certify an unobserved lifetime peak.
This DXGI assessment is from the API contract, not an executed DXGI audit.

The resulting research boundary is precise: native allocation/extent control
is implemented, and resident installation preserves it. A complete device
resource claim needs an independently justified coverage/enforcement or
conservative reservation argument, with actual runtime identity distinguished
from build metadata. No amount of relabelling current samples, adding hashes
or repeating static PRODUCT/SUM cases establishes that premise.
