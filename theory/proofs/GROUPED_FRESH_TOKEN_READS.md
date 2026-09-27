# Group fresh token reads within one observation boundary

Status: **CONDITIONAL LAW; IMPLEMENTED; CPU AND FIXED ACTUAL-DEVICE CASES PASS**.
This is an optional physical transport lowering, registered by
`TokenCudaPrefixContract(grouped_reads=True)`, default off. It changes no
native G/Gamma/U, half/single primitive, numerical tolerance, source/target,
complete record or update schedule. Foundation/ERC remain frozen.

The [prefix-cost law](TOKEN_PREFIX_AUDIT_COST.md) identifies millions of
separate leaf-array read calls within one full unit. Complete fresh observation
is necessary under the present bridge; one device-to-host copy per array is
an implementation choice. The existing `CudaWorkspace.raw_words` already
transports opaque intervening bytes without decoding them. This lowering
applies that distinction to typed token residents with bounded groups.

## The immutable observation boundary

The premises are the existing serialized private Runtime, its fixed default
CUDA stream, hidden raw tensor handles, and no external callback or numeric
write during `Resident.raw`. Grouping does not move a read across a primitive,
a Runtime operation or a separate invocation of `Resident.raw`. In particular,
the pre-transition, post-transition mutation check and final record capture
are still distinct fresh observations.

For one call, enumerate `Resident.tensors()`: complete masters, prepared
operands, every leaf array, every forest block and the current basis. Validate
every named view through the original arena extent/initialization check. The
reuse arena dynamically supplies its live-generation and exact-view checks.
No address-only shortcut or historical handle becomes a legal view. Original
dtype, shape and per-array/workspace bounds remain.

Copy the named intervals from the actual backing allocation into the existing
paid host readout buffer. Every transfer is synchronous. Return only the
requested slices in their original order, including all bits and duplicates;
empty arrays return empty bytes. Clear the entire borrowed prefix after each
copy, including opaque gaps, on success and on exceptions. No gap is decoded,
returned, hashed or made part of a public snapshot.

The resulting local table strongly binds actual view objects to their fresh
read images. Its lookup requires both identity-index match and `is` identity;
an undeclared read refuses. It supplies only the subsequent read-only
`Resident._raw` traversal. It is not stored in the array executor, reused by
another capture, accepted from a Runtime caller or exported as a certificate.
All original complete-state validation and record formation still execute.
The reference producer continues using its original separate CPU arithmetic.

**Conditional preservation theorem.** Under the observation premises, device
contents cannot change between the individual reads of the old traversal or
the transfers of the grouped traversal. Each validated named extent therefore
has the same actual bytes in both. Restricting each transported span to its
named slice preserves the dtype/shape interpretation exactly. Every lookup
performed by the unchanged complete-state traversal receives those same bytes.
Induction through that traversal preserves the complete returned StateWords,
including signed zeros and complete original event/carry data. Changing any
named live array before the next capture is observed afresh, and cannot be
masked by a prior host image. Changing only opaque gaps cannot affect any
returned named value or later buffer contents.

This does not assert equivalence in a model admitting arbitrary writes during
a capture. That would require a different synchronization and ownership proof.
It does not authorize replacing still-live arrays with old host bytes or moving
checks across a numeric write. Malformed metadata may fail earlier because the
complete view set is validated before the first transfer; no failed traversal
may publish a learner.

## Grouping rule, exact class and resource law

Let H>0 be the paid host buffer capacity and let (o_i,s_i) be each named byte
extent, with 0 <= o_i <= o_i+s_i <= R for arena size R. As before, reject
s_i>H; this lowering does not split an individually inadmissible view. Discard
only zero-sized transport requests, retaining their empty outputs. Sort the
nonempty extents by start, end and original index. Extend the current group
while its bounding span fits H; otherwise close it and start the next group.

Every extent appears exactly once in the plan. Each copied span fits H, and
its member slices stay inside that span. The plan minimizes the number of
transfers among **contiguous partitions of this start-sorted list, with
indivisible views and maximum span H**. Proof: the greedy first group is the
longest admissible prefix. Extending any other partition's first group to it
can only delete items from later groups; such deletion cannot enlarge their
spans. Induct on the remaining suffix. This is the plan's exact optimization
class, not global bandwidth optimality or a Runtime completeness certificate.

Write L=sum_i s_i, including duplicate named requests, and T for the sum of
copied span lengths. Successive group starts and ends increase. A new group
exists only because its first interval ends beyond the preceding group's
admissible span; its overlap with the previous group is smaller than that
first interval's size. Thus the union occupies at most R bytes and the sum
of overlaps is bounded by the sum of those first intervals:

    number of transfers <= number of nonempty named requests,
    T <= R + L.

This covers overlaps, aliases, duplicates, nonmonotone request order, sparse
holes and empty views. It gives no hardware-time dominance: extra transport
may cost more than the saved calls. There is no gap threshold, placement search,
new device allocation or change to physical tensor ownership.

The original named-byte/metadata tariff remains. At most four complete
resident captures occur in one attempted token phase, including the final
failed-attempt capture where reached. Let N be the registered update-unit size,
J the context length, b=bit_length(N), and m=11+7N+[N(J+1)+2]b. There are at most
seven master/prepared arrays, seven arrays per leaf, two global forests,
NJ embedding forests, N correction forests and four current basis arrays;
each forest has at most b blocks. Hence m bounds the named view count.
The owner passes this derived allowance to the array executor. Enumeration
checks immutable container lengths and stops at the cap before constructing
an oversized table; capture also checks the final tuple's extent before any
transport. Invalid producer metadata cannot silently exceed this allowance.
Runtime additionally prepays 16R+256m bit_length(m+1) primitive work for opaque
transport, clearing and sorting before entering execution. The transport
bound adds at most R bytes per capture beyond L; named-byte work is unchanged.
This is a primitive work allowance, not a bit-time, allocator-fit or wall-time
theorem. The existing readout bytearray is already paid in both resource roles.
The plan, local image table, returned immutable bytes and host array views are
real host allocations under the separate host contract. No persistent cache
or owner state is hidden outside that accounting model.

The new registration and work-model suffix bind the lowering into manifest
and provenance. Failure handling, target retention, learner publication,
unsealed physical pins and terminal MemoryError behavior remain the existing
owner rules. A failed new copy does not grant an acceptance seal or free its
physical inputs/outputs. Historical complete frames remain unchanged.

## Evidence and scope

The CPU audit is `scripts/audit_grouped_token_reads.py`. It checks finite
exhaustive layouts against an independent ordered-partition dynamic program,
actual CPU tensor backing stores in both arena modes, opaque gaps, aliases,
stale generations, changed named values, and clearing after failed copies.
Complete Runtime trajectories compare full canonical phase records and native/
physical reports against the original separate-copy path. The CPU audit uses
no CUDA context or corpus data. Its copy counts are separate from the actual
device comparison recorded below.

The final control passes 6,839 valid layouts, 6,268 capacity refusals and five
malformed registrations. Eight transport comparisons include signed-word
changes and opaque uninitialized gaps. The inherited actual-overwrite control
refuses nine stale/unissued operations. Runtime matches 602 full phase records
and 24,380,850 canonical body bytes across 36 paired histories, including both
arena modes, training, profile construction and frozen reports. Both report
totals and physical allocation extents agree exactly.

Those CPU-tensor traces issue 203,986 separate copies on the baseline path.
Grouping preserves the same 3,918,344 requested bytes, replaces 32,530 resident
copies with 2,031 span copies, and leaves 171,456 other copies. Total transport
rises to 12,071,396 bytes. This is an observed count/volume tradeoff in the
finite fixtures, not a speed measurement or a full-V extrapolation.

Unpaid work refuses before execution; transport and MemoryError failures after
new-state execution preserve the revealed target and previous learner. A
complete failed transport phase remains unsealed, and new physical pins stay.
Changed live leaves still refuse while old records remain unchanged. Oversized
view tables/metadata refuse before transport. The final tariff also passes
a separate 15-phase paired record/report check. The full-V derived allowance
is 2,630,175 views and 31,993,014,784 extra primitive work per phase. Minimal
evidence is `FP_GROUPED_TOKEN_READS_CPU.json`.

This addresses transport granularity only. The native B(3B+1)/2 prefix
reevaluations and logical complete leaf inspections remain. Any reuse or
composition of native enclosures needs a separate binding and numerical proof.

## Fixed first actual-device comparison

`scripts/run_grouped_reads_cuda_a1.py` registers two fresh sequential Windows
jobs: separate reads then grouped reads. Each has a 240-second wall limit,
16-GiB host cap and the original full-V model: 50,257 labels, context512,
width4, K8, 603,092 master coordinates and update unit512. Both use append-only
physical storage and 64-MiB owned canonical images. Both read only the already
registered first1,024 training bytes and observe its first16 targets. The
original G/Gamma/U, source interface and all numerical checks remain.

Unchanged limits are 1-GiB tensor arena/allocator reservation, 2-GiB paid
reference payload, 64-MiB complete phase frames, 2^22 output cells, state
atol16, probability/division atol10^-6, 4,096 exact-rounding cells and the
24-GiB whole-board bound on the pinned RTX3090. The new planning/transport
tariff is paid normally. Initialization and all32 ordinary calls are timed
without a profiler or read-counter instrumentation.

Each positive trace must retain16 observations,33 checked phases, the same
positive checked-word count, every original context/target, pending count16
and zero commits. The final native/physical state predicate, full-frame roots,
resource residency and actual/lifetime allocator counters must pass. Both
workers must consume the same append-only extent and keep counters
(1,1073741824,1).

After its timed positive trace, the grouped worker additionally zeros the
first leaf's actual live device values in place. The next prediction must
raise with the existing changed-predecessor refusal, retain the differing
actual words in an EXECUTION_FAILED record, preserve the old sealed bytes,
cursor16 and native learner, and publish no successor. This is an explicitly
injected fault after timing, not an ordinary numeric update or extra target.
It must add no tensor allocation or reset.

The launcher requires a clean committed canonical source, the terminal image
comparison and the passing CPU control. It exclusively creates
`FP_GROUPED_READS_CUDA_A1.json`, keeps original process identities and stops
at the first failed worker. Existing journals are never replayed. This finite
comparison supplies no complete512-event unit, text score, general timing
ratio or sustained-training budget. No additional device variant is registered.

## Actual-device result: qualified, small observed early-prefix time difference

Both original workers pass at `a833b68b15ba6998d29bea90c6f2bbc0ffc76740` on
the pinned RTX3090. Each positive trace retains16 observations,33 checked
phases and4,541,709 checked primitive words, with all original sources/targets,
pending count16 and zero commits. Both consume29,850,216 append-only bytes
and preserve actual/lifetime allocator counters(1,1073741824,1). All original
caps and tolerances hold. Each retains336 images/67,102,758 bytes under64 MiB.

| Observed quantity | Separate reads | Grouped reads |
| --- | ---: | ---: |
| Initialization seconds | 10.50256 | 10.21104 |
| First eight predict/observe pairs, seconds | 40.76275 | 39.98898 |
| Last eight predict/observe pairs, seconds | 43.65134 | 42.82878 |
| All32 ordinary calls, seconds | 84.41409 | 82.81775 |
| Entire worker launcher wall seconds | 98.13034 | 98.01929 |
| Peak whole-job commit bytes | 3,330,473,984 | 3,455,455,232 |
| Paid reference peak bytes | 271,544,497 | 271,544,531 |

The ordinary-call ratio is1.01928, an observed1.89108% time reduction. This
single ordered pair does not estimate statistical significance or a general
speedup. It supplies no material evidence that transport grouping alone makes
ordinary training affordable. The grouped whole-job measurements additionally
include its post-timing fault, so they are not isolated memory/time penalties.

The grouped worker zeros the actual first leaf in place. Its next prediction
refuses with `token CUDA predecessor or continuation cache changed after its
owned phase`. The34th record is EXECUTION_FAILED and contains the changed
actual leaf words. Prior sealed words stay intact; cursor16 and the complete
native learner remain, with no successor or new tensor allocation. This is
an actual physical freshness check, not a simulated host-payload corruption.

`FP_GROUPED_READS_CUDA_A1.json` records both original processes, source, device,
stages and outcomes. It is terminal and must not be replayed. The current
transport qualification is closed and the feature remains optional/default
off. No gap-threshold sweep, extra transport case or long-unit run is due from
this result. Late-unit benefit is unmeasured. Follow the still-repeated native
prefix computation and complete retention cost toward actual text learning.
