# Complete arena metadata without per-instance dictionaries

Status: **VALUE-PRESERVING IMPLEMENTATION; BOUNDED HOST AND ACTUAL CUDA AUDITS**.
This addresses an observed implementation cost. It changes no native program,
learner update, evidence rule, resource cap or architecture action.

## 1. The measured obstruction

All four retained RN-5 n16/c2 workers fail while constructing the complete
region table in `CudaArena.snapshot`. Their original failures remain in the
[RN-5 journal](../../evidence/minimal/FP_JOINT_UNCERTAINTY_EXPERIMENT.json).
They contain no complete model scores. The source storage implementation is
unchanged between that execution at38b27b3 and the baseline used below.

The arena retains one frozen `CudaRegion` record for every allocated extent.
An ordinary Python dataclass supports an instance dictionary in addition to
its ten declared fields. A snapshot then materializes the complete primitive
region table and recursively freezes it. This host cost is separate from the
small GPU allocation occupied by many scalar extents.

The implementation makes `CudaRegion` a frozen slotted dataclass. Every
record and field remains present. The complete snapshot construction remains
the same; actual host accounting measures its resulting cost.

## 2. Preservation argument and its boundary

The declared fields, in their original order, are

`sequence, phase, owner, operation, offset, byte_size, reserved_size, shape, dtype, initialized`.

The constructor accepts the same field values and default false initialized
flag. Field access and dataclass replacement preserve those values. Ordinary
assignment remains forbidden. Slot layout changes the private Python object
representation, not the declared field set.

Every arena continuation that uses a region reads these fields:

* `_region_for` checks offset, size and dtype against the owned backing arena;
* `require_initialized` checks the initialization flag;
* `_mark` checks phase, prior initialization and whole-extent coverage, then
  replaces the record with the same fields and initialized=true;
* snapshots emit all ten fields and retain their detached immutable values;
* installation leases use the recorded sequence and the actual tensor's
  checked offset, shape, size and dtype.

Thus induction over allocations, attempted reads, marks and snapshots gives
the same primitive region table and the same results of these guards for
the same arena/tensor inputs. Replacement does not mutate an older record
or a retained snapshot. The explicit sequence/phase/owner identities remain;
Python instance-dictionary identity is not an authority in these operations.

This proves preservation of the region interface. It does not claim identical
Python heap layouts, addresses or resource outcomes across executions. Lower
host overhead is the intended difference. The actual fixed job caps, complete
packed-state charges, tensor extents, allocator history, phase frames and
installation checks still determine whether an execution can finish. No
region is pruned, recycled or omitted from a snapshot.

## 3. Bounded comparison with the actual prior implementation

Run `python -B experiments/joint_uncertainty/arena_region_storage.py --write`.
The baseline imports the actual storage/freezer code from the immutable
b85b39d checkout. Both versions construct the same complete metadata and
snapshot values, under separate jobs attached before execution with a512MiB
commit cap and120-second limit. There is no GPU import in these host jobs.

The [minimal host audit](../../evidence/minimal/FP_ARENA_REGION_STORAGE_AUDIT.json)
retains all four completed jobs and checks every field in1,500,000 snapshot
rows. It also checks360 field/replacement/detachment cases.

| Regions | Prior peak job bytes | Slotted peak job bytes | Reduction |
|---:|---:|---:|---:|
| 250,000 | 147,939,328 | 135,356,416 | 12,582,912 |
| 500,000 | 276,951,040 | 251,043,840 | 25,907,200 |

These are observed whole-job peaks for the declared host fixture. The small
shallow-object diagnostic materializes one ordinary instance's lazy dictionary
and excludes field referents; it must not be multiplied into a claimed process
memory result. The jobs, not that diagnostic, establish the table above.
Shared-machine elapsed times are not presented as GPU throughput evidence.

## 4. Actual CUDA and owned transport checks

The [development CUDA regression record](../../evidence/minimal/FP_ARENA_REGION_CUDA_REGRESSION.json)
contains the unchanged existing audit results with the slotted representation:

* the full CUDA storage audit passes, including1,306 learner phases,32,996
  initialized views and all216 typed three-request sequences/648 requests;
* uninitialized, cross-extent, dtype-reinterpreted and old/double-written
  views remain refused, as do oversized allocations and escaped allocator
  history; failed writes and unexpected failures remain retained;
* all thirteen existing installation cases pass, including learned and
  recurrent states, capacity refusals, corruption/extent guards and a second
  installation using its actual new baseline and fresh alpha;
* the bounded likelihood profile/install job seals at cursor46 and installs
  at22, checking286 CUDA and286 binary64 phases,94 commit tapes and40 fresh
  scores. The full constructor class remains UNRESOLVED.

Commands are `python -B scripts/audit_cuda_storage.py`,
`python -B scripts/audit_cuda_installation.py`, and
`python -B experiments/joint_uncertainty/likelihood_lowering.py --case profile-install`.
The first two are complete targeted regressions, not a new source-bound
whole-project release. The last retains its actual4GiB/180-second job.

No old n16 worker is rerun or relabeled by these audits, and no n16 recovery
is established. The n8 likelihood matrix continues at immutable86083a0;
its reader stays at b85b39d in `F:\FP-likelihood-model-audit`. Subsequent
model evidence must identify its own actual execution source and costs.
