# Bounded CPU reference results

Status: **EMPIRICAL FEASIBILITY; BOTH ORIGINAL JOBS COMPLETE, 2026-09-26**.
Source36851c5; numerical sourcea0610f0. The
[preregistered protocol](REFERENCE_HOST_PROTOCOL.md) and
[6046-byte original journal](../../evidence/minimal/FP_TOKEN_REFERENCE_HOST_A1.json)
retain the complete scope and actual process identities. No job is live.

| Job | Result | Enclosure + commit | Peak job private commitment | Whole job wall time |
|---|---|---|---|---|
| V50,257/context4 synthetic rational control | Exact endpoint equals both scalar-enclosure and rational controls; full gradient basis checked | 0.03489 s | 77,168,640 B | 3.7573 s |
| V50,257/context512, first512 real training tokens | All603,092 masters resolve by sound enclosures | 0.44159 s | 236,920,832 B | 1.1342 s |

Each job starts within its preattached2-GiB/180-second fence, exits0, and
has no timeout or limit termination. Worker observations match the actual
launcher process identities and final peaks. The SDK's cumulative process
count is2 in each job although the live active-process cap remains1; as
documented by the existing launcher, that counter can include denied starts.
It is not a claim that a second concurrent worker was permitted. Shared
machine memory, file cache and the launcher itself are outside this scope.

For the control, enclosure takes0.00729 s and dense endpoint projection
0.02759 s. The separate scalar enclosure path takes0.35950 s; the rational
path takes0.14742 s including forward checks and0.13343 s for commit.
Comparing all endpoint parameters costs about1.2 s per independent control.
These single measurements include different checks and are not an isolated
or universal speedup estimate. All301,548 masters and the entire pending
gradient basis agree; the exact common denominator reaches12,303 bits.

For the real-prefix fixture, enclosure takes0.40438 s and commit0.03721 s.
It retains250 touched input rows,249 target rows and2,412,368 bytes of
committed master payload. Complete declared syntax has25,732,096 causal
atoms,52,309 SUMs,4 PRODUCTs and103,332,496 incoming edges, represented by
the proved indexing rather than literal expansion. Its full rational unit
is not materialized; endpoint correctness is conditional on the audited
enclosure refinement. Only1024 training bytes are read and identified. No
validation/test data, text loss, model ranking, Torch or GPU is used.

The practical decision is to proceed with this reference path. A full
context/vocabulary update already fits comfortably inside the declared
envelope; more passive fixture variants are not the next obstacle. The
remaining boundary is actual owned data/Runtime integration and a physical
AMP relation for this native learner. In particular, preserve the registered
grid update when lowering tiny gradient steps: ordinary floating subtraction
can round a step away before projection. The measured core is a supplied
resource fixture, not a selected language architecture or evidence of useful
text learning. Fresh strong n-gram and Transformer comparisons remain due.
