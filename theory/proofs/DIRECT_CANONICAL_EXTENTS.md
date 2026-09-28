# Exact canonical extents without reconstructing the fixed grammar

Status: **EXACT GRAMMAR LAW; CPU AND FINITE CUDA PASS; QUALIFICATION CLOSED**.
This changes the implementation of the existing packed extent calculator.
Serialized bytes, source identities, guard order, image policy and independent
decoder checks stay fixed. There is no new cache, registration option, FP
semantic action or `CERTIFIED_COMPLETE` decision class.

The [current-path diagnostic](../../experiments/next_token/CURRENT_TOKEN_COST.md)
places 83.55254% of four instrumented samples in disjoint canonical retention,
preparation and writing subtrees. It motivates this work but does not predict
its speed benefit. The separate [snapshot binding hole](CANONICAL_IMAGE_SNAPSHOT_BINDING.md)
was found during this audit and repaired first; extent arithmetic cannot repair
an externally writable source-to-evidence binding.

## Exact law and scope

Write J(s) for the byte length of the existing quoted JSON string encoding,
including its surrogatepass and DEL rules. Let

    H(n) = 2 + max(1, ceil(bit_length(n)/4)) + [n < 0]
    delta(k) = max(0, k-1).

H is the quoted signed hexadecimal integer length. For a stable finite value
in the existing supported typed algebra, its packed extent S is exactly:

| Value | S |
| --- | --- |
| None, True, False | 17, 13, 14, respectively |
| Integer n | 16 + H(n) |
| Fraction a/b | 18 + H(a) + H(b) |
| Byte string b | 16 + 2 len(b) |
| String s | 8 + J(s) |
| Tuple with k children | 12 + delta(k) + sum S(child) |
| List with k children | 11 + delta(k) + sum S(child) |
| Mapping with k observed entries | 14 + delta(k) + 3k + sum (S(key)+S(value)) |
| Dataclass with k declared fields | 18 + J(module) + J(qualname) + delta(k) + 3k + sum (J(field name)+S(field value)) |

An existing qualified immutable image hit uses its already admitted exact S,
as before. No new object becomes eligible. The mapping entry count is taken
from the actual iteration, never from an assumed `len(mapping)`.

**Proof.** An encoded array with k elements contributes two brackets and
delta(k) commas in addition to its elements. Apply this identity to each
fixed typed tag and its payload. A mapping entry or dataclass field pair adds
three punctuation bytes. The displayed constants are the fixed tag strings
and remaining brackets/commas. Induction over the same ordered field/container
walk gives exactly the original packed extent, including repeated occurrences
and empty containers. It does not serialize or retain an output tree.

For an exact printable ASCII string, J(s) is

    len(s) + 2 + count(s, quote) + count(s, backslash).

Every other character has unit UTF-8 width and no escape in this class. All
non-ASCII/control/DEL strings retain the previous character rule, including
distinct encodings for astral code points and explicit surrogate pairs. The
fast case creates no serialized string or cached assumption.

Both calculators visit the same input occurrences in the same order and make
the same existing image lookups. The implementation still fetches the declared
dataclass fields before module/qualname metadata, reads each field in order,
and visits each mapping key before its value. Only arithmetic over fixed
syntax is simplified. The node-visit count is unchanged: for the occurrence
tree cut at existing image hits it is one plus the sum of child visit counts.
This is not a claim that reading mutable fields once proves later immutability.

`bounded_packed_size` retains its separate original guard walk and final extent
test. Thus explicit byte/depth/integer guard decisions and their order agree
when both calculations complete on the same observed values. Whole-process
allocation/recursion exhaustion is outside this exact arithmetic equivalence;
existing resource failures remain possible. All existing tariffs and limits
remain, rather than claiming a reduced abstract charge from fewer Python calls.

## Counterexample to an eager extent cutoff

With byte allowance 8, `(0, object())` must first fail its original typed guard
with `ContractError: unsupported packed reference payload`. The packed first
integer alone would exceed 8, so an eager encoded-size cutoff could instead
stop before the invalid second field and return a resource refusal. Successful
byte equality would not prove preservation of this refusal decision class.
The implementation deliberately leaves the original guard walk intact.

## Evidence

`scripts/audit_canonical_extents.py` loads the old calculator from canonical
source `075eba1`, not a maintained second implementation. It compares complete
bytes/extents, exact guard outcomes and ordered field/mapping/image observations.
String controls cover every BMP code point and every printable ASCII pair.
In total, 412 values/783,100 packed bytes, 74,564 string cases, 2,530 exact
guard decisions and 12 field/mapping/image observation traces agree.
The old identity/Unicode audit also passes its 2,160 typed-mode comparisons,
65,536 code points, 3,072 surrogate-pair classes, cycle refusals and actual
Runtime source/collision controls. No identity encoding changes.

Six paired complete CPU Runtime histories preserve all 129 phase bodies,
5,774,243 bytes, 50,279 primitive words, learners, reports, frame retention,
allocations and retirements. They also preserve 45,619 raw calls/856,212 bytes.
Cases cover unit sizes 1/2/4/8, original reverse/repeated profiles and combined
lowerings including archival. All archive-plan metadata is compared. Real
owned-image controls preserve 1,800 guard decisions and seven old snapshots;
wrong-image/page, unpaid-image and post-target resource/memory failures pass.

A representative 512-rational value still visits all 515 occurrences and has
the same 13,588-byte extent. Recorded calls fall from 12,894 to 4,659. These
are deterministic component counts, not a wall-time or full-model speedup.
`FP_DIRECT_CANONICAL_EXTENTS_CPU.json` retains the minimal exact/owner evidence.
No corpus or CUDA is opened by this audit. Actual performance remains to be
measured under the unchanged complete contract and repaired snapshot boundary.

## Fixed first actual comparison

`scripts/run_canonical_extents_cuda_a1.py` is registered before launch. Two
fresh workers run in order `prior-extents`, then `direct-extents`, each in a
preattached 240-second/16-GiB Windows job. Both use the original V=50,257,
L=512, D=4, K=8, unit=512 fixture and its 603,092 masters. They keep the 1-GiB
arena/reservation, 2-GiB reference payload, 64-MiB phase frame, 2^22 output-cell
allowance, 4,096 exact-cell bound, state tolerance 16 and probability/division
tolerance 10^-6. Generation reuse, 64 MiB of canonical images and 4 MiB of
base facts are enabled. Grouping, native composition and archival stay off.
Both arms include the corrected snapshot binding boundary.

The prior calculator is loaded from `075eba1` by the launcher into temporary
source before either worker starts; only that calculator and its recursive
helpers are used for prior extents. All other current Runtime code is shared.
No second implementation is checked into the repo and no baseline numerical
or ownership check is weakened. There is no inner profiler or counter wrapper.
Initialization is timed separately from the 32 ordinary calls over the first
16 original targets, using only the already declared 1,024 training bytes.

Each worker must retain 33 checked phases/4,541,709 primitive words, all original
contexts/targets, pending count 16 and zero commits. After timing, the worker
substitutes only a returned embedding-image binding's metadata. A fresh public
prediction at cursor 16 must succeed with the private binding unchanged, and
its entire retained frame must match a fresh **uncached** encoding of its actual
phase, including the complete padding check. No seventeenth target is revealed.
Both arms must have identical cumulative arena allocations through that control.

The exclusive `FP_CANONICAL_EXTENTS_CUDA_A1.json` records clean committed source,
prior-calculator source, worker/device identities, caps and original outcomes.
Commit before launch. Never replay a partial/terminal journal, raise a failed
cap or replace a failed worker. This one ordered pair qualifies the corrected
public boundary and measures this extent change; it cannot establish general
speedup, full-unit benefit, sustainable training or language quality. Close it
at its original result and reassess the remaining ordinary-token constraint.

## Actual result and closure

Both original workers at `40903540d28d91dde407f6605ce77a5e7d5f2b53` pass under
every registered cap on the declared RTX 3090. Each timed prefix retains all
33 phases/4,541,709 primitive words, 16 original records, pending count 16 and
zero commits. The prior arm uses only the original extent calculator from
`075eba1`; both use the current corrected snapshot boundary and all checks.

| Original measurement | Prior extents | Direct extents |
| --- | ---: | ---: |
| Initialization seconds | 9.9273950 | 7.8164996 |
| All 32 ordinary calls, seconds | 62.0569381 | 55.4478877 |
| First eight targets, ordinary seconds | 29.8564602 | 26.6876995 |
| Last eight targets, ordinary seconds | 32.2004779 | 28.7601882 |
| Peak whole-job committed bytes | 3,465,949,184 | 3,464,151,040 |
| Peak paid reference bytes | 272,951,974 | 272,951,974 |

The ordinary-time ratio is 1.1191939, a 10.64998% observed reduction in this
single ordered pair. This is no statistical/general or full-unit speedup.
Both workers retain 336 images/67,102,758 bytes and 122 complete archive pages/
19,680,386 actual page bytes after the post-timing control. Cumulative buddy
allocation is 37,038,864 bytes, peak live buddy bytes 24,214,064, and maximum
arena extent 24,379,392 in both. All native/current allocation counters remain
`(1,1073741824,1)` with original actual/lifetime 1-GiB tensor/reservation use.
Whole-job peaks include the same additional control; their small difference
is not a memory-efficiency claim.

After timing, each worker replaces the returned embedding-image binding's
buffer/guard metadata with output-image metadata. Its next public prediction
still uses the unchanged private binding. The retained 34th phase matches
27,660,005 uncached actual-phase bytes inside the full 67,108,864-byte frame,
including zero padding. Learner and cursor 16 stay unchanged; no seventeenth
target is revealed. This separately qualifies the corrected binding boundary
on the actual device. The old alias is not reintroduced in a GPU run.

`FP_CANONICAL_EXTENTS_CUDA_A1.json` is terminal, retaining original source,
process/device evidence and per-call times. This finite comparison is closed;
never replay it or turn it into an extent-variant sweep. General canonical
work was a useful target in this trace, but 55.45 seconds for 16 targets still
does not establish an affordable text experiment. Complete retention,
independent expected-stream generation/comparison and later-prefix cost remain
relevant. Use the existing diagnosis and source analysis to attack that larger
constraint; no new cache policy, semantic relaxation or long replay follows
from this result alone. Foundation/ERC and the rational/relation closure remain.
