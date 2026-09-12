# Bind actual CUDA identity and charge the physical framebuffer envelope

Status: **scoped resource proposition, owned native registration and actual
RTX 3090 endpoint audit.** Foundation R4, XVII.31 and ERC-1 stay frozen.
This closes an identified VRAM-residency coordinate, not a complete target
release or model-science claim. The subsequent
[owned target policy/run](OWNED_CUDA_POLICY_RUN.md) integrates these declared
coordinates; complete target release remains open.

## 1. A uniform upper does not require an exact allocation history

The [native-observation counterexample](CUDA_RESOURCE_OBSERVABILITY.md)
constructs histories with identical allocator observations and different
direct CUDA allocations. It excludes recovering that history from those
observations. It does not exclude a valid upper shared by both histories.

**Capacity proposition.** Fix a physical domain D of capacity C bytes in
the registered realization. For every legal history h, let M_D(h,t) count
physical bytes resident in D at time t, counting shared bytes once. If all
these bytes belong to D, then

`M_D(h,t) <= C`, and `sup_t M_D(h,t) <= C`.

Proof: resident byte locations form a subset of D. Taking a supremum over
time, or over all histories consistent with a partial observation, preserves
the same bound. No allocation trace or sampling-rate premise is used.

Register deployment and compiler as sharing this entire physical envelope.
Charge C to each role, once globally. Admission therefore requires

`C <= min(B_global, B_deployment, B_compiler)`.

This is a conservative charge for the fixed realization, not a measurement
of FP's actual peak, an allocation reservation, or an exclusive availability
guarantee. Other processes may consume the same board. Their interference
can make execution fail; it cannot make physical residency within D exceed
C. A smaller budget refuses this realization as unresolved, without excluding
other machines with tighter justified accounting. The implementation does
not alter graph semantics or introduce a new architecture action.

The claim concerns only this resource functional. Equal envelope charges
do not make different histories equivalent for future information, work,
allocation-volume or learner claims. Existing complete Runtime histories
and arena records remain retained.

## 2. The implemented domain and actual identity

Here D is the identified board's usable physical framebuffer, with C read
from `nvmlDeviceGetMemoryInfo().total`. The native v1 structure defines total
as physical device memory and includes driver-reserved memory in used plus
free. No used/free sample is interpreted as a historical maximum. See the
[NVML memory contract](https://docs.nvidia.com/deploy/nvml-api/api/structnvmlMemory__t.html).
This is not a count of raw silicon bits, registers, caches, host backing,
paged-out allocations or all system memory. On devices with capacity-changing
modes, the registered premise must continue to hold; this audit concerns the
actual RTX 3090 configuration, not those other configurations.

`CudaPrefixContract.device` is an immutable `CudaDeviceContract`: three VRAM
caps, expected runtime/API/display-driver versions and fixed backend/ownership
policies. It cannot be omitted on a CUDA root. The existing Torch build tag
remains a separately named registration coordinate.

Runtime loads the actual Torch-installation CUDART DLL and System32 NVML.
It maps the registered CUDA ordinal through `cudaDeviceGetPCIBusId` to
`nvmlDeviceGetHandleByPciBusId_v2`; the physical UUID and capacity then come
from that handle. A caller cannot supply a cheaper board's capacity, PID,
native handle, observation callback or resource certificate through the API.
Successful observations balance NVML initialization and shutdown references.
Only the immutable identity is exposed; no native handle enters a snapshot.

`cudaRuntimeGetVersion`, `cudaDriverGetVersion` and
`nvmlSystemGetDriverVersion` bind the actual versions. The driver API query
reports the latest CUDA API version supported by the driver; it is distinct
from the display-driver version string. Windows CUDA 13 may report its
display-driver-packaged runtime instead of the application's build toolkit,
as specified in [CUDA version management](https://docs.nvidia.com/cuda/cuda-runtime-api/cuda_runtime_api/group__CUDART____VERSION.html).

The executed registration has runtime/API 13040, display driver 616.92,
Torch build tag 13.2, PCI bus `0000:0B:00.0` and physical capacity
**25,769,803,776 bytes = 24 GiB**. The small audit record retains the actual
UUID. Version or whole-board budget mismatch is refused before the first
native tensor allocation. Observation itself can initialize platform state;
this is not a claim of zero native work or zero driver allocation beforehand.

## 3. Continuation, installation and failure

Every public continuation/authority entry rechecks the actual identity and
capacity along with the existing tensor-arena premises. This checks the
binding; the physical-capacity argument supplies the between-entry upper.
The scoped machine uses one fixed device and trusted native executor, with
no device-mode mutation, arbitrary native callbacks or external migration.
Polling is not offered as proof against an unregistered transient swap.

The [resident installation frame](OWNED_CUDA_INSTALLATION.md) now includes
the private device binding and its fixed field schema. Preparation and final
verification retain the identical device object and initial identity record,
as well as the original prefix, tensor arena and complete learners. Shared
board charges cover construction, coexistence, installation and continuation
uniformly. There is no capacity refund when a candidate becomes deployed.

Unavailable or changed native premises terminate current CUDA authority.
Restoring the observer cannot revive old proof/crossing/install ports.
Unexpected errors retain their original exception, including when native
cleanup also fails; host allocation failure keeps its established treatment.
A failed diagnostic query must also mark the retained root terminal. An
adversarial `snapshot()` query originally exposed a missing unexpected-error
boundary in the new implementation; the reproducer now passes after that
path was brought under the same terminal rule.

The existing [process-commit fence](BOUND_HOST_RUNTIME.md) remains a separate
coordinate. A 4 GiB Windows job can cover the same runtime's private host
commitment while the board has a 24 GiB framebuffer envelope. Neither is
added to tensor/packed payload counts as if those were disjoint storage.
The native arena still owns initialized extents and exact allocator history;
packed buffers still own reference/evidence state; output-cell work and
observed host CPU ticks retain their own declared meanings. No physical
capacity argument bounds cumulative allocation volume, GPU instruction work
or elapsed execution time.

## 4. Actual audit and exact remaining scope

Run `python -B scripts/audit_cuda_device.py --write`. Fresh processes exercise
version/API/driver mismatch, a global cap one byte too small and an unequal
role-cap refusal before native tensor allocation. A successful unequal-cap
registration charges the full 24 GiB to both roles.

The earlier direct 32 MiB allocation/write/free is repeated alongside a real
owned Runtime. Arena and device observations stay identical while it is live,
and an ordinary event executes. Both histories satisfy the same framebuffer
envelope; the audit does not claim their physical-residency peaks are known.

Full native selection and crossed fresh identities precede the injected
query-failure, changed-version and original/combined unexpected-error cases.
They exercise authority and diagnostic entry paths, retained alpha/history
and refusal after observer restoration.

A separate worker is fenced before execution in an actual 4 GiB Windows
process/job. It constructs the 35-member class, obtains both fresh crossings,
installs, continues ordinary learning and passes 151 independent CUDA phase
comparisons. PID/creation time bind its final host observation to that job.
The observed process lifetime commit peak is about 2.1 GiB. The native tensor
arena remains 16 MiB; the physical board charge remains 24 GiB. These are
three different resource coordinates, not three estimates of one peak.

The minimal result is
[`FP_CUDA_DEVICE_AUDIT.json`](../../evidence/minimal/FP_CUDA_DEVICE_AUDIT.json).
The complete CUDA installation, prefix and persistence regressions also pass:
35/774/124-member installation, all 64 short streams with 1,024 independent
device phases, recurrent/profile paths and all 32 fresh null branches with
832 phases and 62 conditional wealth inequalities. The shared host-failure
and reference-run regressions pass; all 38 package files import without Torch.
This is targeted regression evidence, not a reissue of the frozen CPU release.

The subsequent [owned policy/run composition](OWNED_CUDA_POLICY_RUN.md)
executes on this resource binding. Complete target release remains open.
This result supplies neither an all-kernel theorem nor new static theory
prerequisites. Continue target integration before science.
