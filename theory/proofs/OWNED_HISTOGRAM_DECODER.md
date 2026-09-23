# Owned execution of the complete count histogram decoder

Status: **IMPLEMENTED; EXACT CPU/NATIVE AUDIT PASS; ACTUAL RUNTIME CUDA GATE
REGISTERED, OUTCOME OPEN** (2026-09-23).

The [histogram theorem](COUNT_HISTOGRAM_DECODER.md) already proves the
positive regrouping, its uniform n<=16 precision law, and the insufficiency
of a query histogram as persistent state. Its arithmetic-only RTX3090 A1
passes at4a4e730. This document binds that same realization to the existing
ReferenceCompilerRuntime. It adds no native action, learner, information
interface, constructor decision class or Foundation/ERC-1 condition.

## 1. Complete state and explicit execution class

Register `ConstructionContract.indexed_histogram=HistogramAllowance(...)`.
An actual indexed CUDA prefix must register the identical allowance in
`IndexedCudaPrefixContract.histogram`. Order search and the projected
physical schedule are separate execution classes and cannot be combined
with this fixed enumeration. Registration does not select an architecture
or change the native program: the entire existing indexed relation program,
Gamma and unit/rate1 simplex U remain fixed.

Defaults are32768 anchored worlds, span S=396 and32768 integer bits. The
implementation refuses more worlds and declares at most32768 integer bits;
its finite declared span cannot exceed1983. Every actual call separately
requires `16H+8n+1024 <= bits`, with a floor of1024. Thus n>16 or an exhausted
span/integer allowance is outside this particular available execution.
It yields UNRESOLVED, not native inadmissibility or an all-decoder lower
bound. Integer budgets remain independent of the mathematical precision
law's uniformity in H.

The retained state still contains **all** signed counts, actual pending
query/target, clocks, gradient forms, source/event identity, profiles and
native history. A plan records that full predecessor and ordered query.
ReferenceView also accepts the histogram allowance for explicit parameter,
pending gradient and cache point reads. Its bounded point decoder confers
no Runtime authority. The complete native-coordinate interpretation is
unchanged, including a transient physical value that rounds to zero.

The reference machine identity is
`packed-indexed-histogram-reference-payload-v1`; the physical forward identity
is `indexed-positive-exponent-histogram-rne16-rne32-v1`. Ordinary indexed
global/projected registrations retain their own identities and algorithms.
Every successful call here is a fixed execution witness. None produces
`CERTIFIED_COMPLETE`, a constructor optimum, or a certificate that every
decoder within a larger resource class has been searched.

## 2. Packed storage and paid traversal

Runtime admits one actual reusable byte extent **before construction or
CUDA binding**. Its two arrays contain S+1 little-endian uint32 entries
each, exactly `8(S+1)` bytes:3176 at S396. Coefficients cannot exceed32768,
so this representation is exact. The owner retains a private memoryview
for its entire lifetime; each call receives a separate borrowed view.
Releasing that borrowed view cannot permit the backing bytearray to resize.
The physical builder gives a further fresh view to each of its two
reconstructions. Full snapshots copy the scratch bytes; old accepted plans
contain immutable coefficients, not aliases into reusable scratch.

The fixed kernel clears the complete paid extent. It visits all K=2^(n-1)
Gray assignments and, at every flip, scans the n-1 incident count positions
directly. There is no adjacency allocation or world-weight table. Energy
remains in[0,H], so every addressed uint32 cell is in the funded extent.
There are exactly `(n-1)(K-1)` incident visits, including zero-count edges.
The occupied maximum is obtained from this paid traversal; it is never
substituted by the unsafe local upper bound H.

For E=n(n-1)/2, the registered conservative enumeration tariff is

```
W_enum = 64(n+1)K + 32(2(S+1)+E+1).
```

The existing reference prediction debit pays this amount before entering
the kernel. An additional debit `64(H+1)+128(E+16)` precedes exact Horner
evaluation/readout. Thus funding only the plan cannot enter exact numeric
execution. The AMP phase's existing prior work debit includes

```
2 W_enum + 1024(min(K,2(S+1))+1) + 128(n+1)C_cap.
```

This funds construction and independent reconstruction, bounded integer
powers and the replay, in addition to the pre-existing output/readback and
evidence charges. The generic retained phase frame, raw readout extent,
arena allocation, source information and complete learner history are
still paid by their existing owners. A smaller realized histogram or
compressed frame does not retroactively reduce a prepaid extent.

These are declared scalar/index-visit tariffs, not bit-complexity, CPython
heap, GPU throughput or wall-time bounds. Multiprecision scalars, immutable
plan tuples and interpreter metadata still consume actual host resources.
The packed ledger counts its actual retained buffers; the Windows job
independently bounds complete process commitment in actual device tests.

## 3. Refinement and continuation argument

Assume the same trusted fixed kernel, serializer, arithmetic interpreter,
and serialized public Runtime API as the preceding owned indexed gate.
There is no external histogram/plan/numerical-result proposal callback.
Arbitrary Python introspection, monkeypatching an entire trusted checker,
or concurrent mutation of the owner are not claimed to be sandboxed.

At every reference prediction, the actual complete predecessor and source
query enter the fixed histogram constructor. The Gray energy invariant and
positive polynomial identity give exactly the native partition pair.
Horner evaluation therefore gives the complete native evaluation, not an
approximation selected by a helper. Observation and commit keep the
existing actual-target checks and exact signed-count transition. Induction
over ordinary events, profile events and attachment proves preservation of
the complete native count learner whenever the paid execution succeeds.

The physical prediction separately constructs its histogram from its own
retained predecessor, without receiving reference partitions, forecasts
or trained floating parameters. After execution it reconstructs the entire
plan from those actual inputs and checks every typed coordinate. Its exact
RNE replay checks every primitive and a fresh final arena readout. Current
phase ownership prevents reuse of an earlier tensor even if all seven
words agree. Native/physical state equality covers counts, clocks and the
pending event; the histogram precision theorem covers all decoded native
heads and all pending gradient forms. The unchanged observation schedule
is bound to the actual pre-target prediction and target. Exact commits
mean transient rounding error does not accumulate into hidden count drift.

Prediction/observation/commit publication, retained failed phases, complete
byte frames, candidate lineage, fresh alpha spending, range checks and
installation remain inside the existing owner. These arguments depend on
their prior scoped invariants; the new actual gate explicitly exercises
them. Finite testing does not upgrade this to a full indexed release.

## 4. Exact CPU outcome

`scripts/audit_owned_histogram.py --write` produces the retained
[complete CPU audit](../../evidence/minimal/FP_OWNED_HISTOGRAM_CPU.json):

- 759 ternary signed-count states and11919 ordered queries agree with an
 independent lexicographic full-assignment oracle. The production packed
 kernel and earlier passive schedule agree on744462 output words,
 including178611 half words.
- 388 complete owned histories check776 native phase triples. Every
 parameter, pending gradient and cache coordinate is checked through the
 new decoder. Profiles/attachment and20 paired native fresh-evidence
 comparisons pass; crossing is at20 and retirement retains alpha1/4.
- Both prior-work refusals, span/integer exhaustion, workspace shape and
 out-of-class declarations preserve their declared boundaries. Four
 release/later-call resize attempts fail with3176 billed/actual bytes.
- Eight complete plan-coordinate substitutions, seven endpoint bit flips,
46 operation bit flips, two trace-extent changes and one-short output
 allowance refuse. The empty policy seals with zero constructor decisions.
- A real n16 learner receives all120 distinct positive edge observations.
 Its dense counts make the existing join class refuse; the histogram
 answers the same query with17 terms. All32768 decoded parameter slots sum
 to1, an independent32768-world oracle matches its forecast, and an
 opposite label commits the correct complete count vector at121.
- The pre-existing n256 reference control still passes with histogram
 registration absent. The separate
 [legacy owned-schedule regression](../../evidence/minimal/FP_HISTOGRAM_LEGACY_OWNED_CPU.json)
 also passes388 histories/776 phases, profiles and closure; all eight
 pre-existing arithmetic/checker bodies remain unchanged.

The small post-audit borrowed-view adjustment changes no arithmetic or
traversal. The affected complete-plan/endpoint/trace audit was rerun and
passed; the actual gate below tests release and later reuse on both paths.

## 5. Registered actual Runtime gate

Run `python -X utf8 -B scripts/audit_owned_histogram_cuda.py --attempt 1`
only after committing its inputs. There are17 serial fresh jobs, each4 GiB
and900 seconds, with one32-MiB arena/64-MiB allocator allowance. Standard
histogram phases retain262144-byte compressed frames and at most65536
floating output cells; both legacy n256 controls retain their existing
4-MiB frames. State/probability tolerances stay1/100 and1/1000.

Cases: profiles, paired fresh evidence/install/continued learning, closure,
unfunded output, second-lineage commit refusal, retired producer ports,
fresh prediction/gradient/operation bit faults, stale output, target swap,
changed plan coefficient, paid scratch release/resize continuations,
52-label underflow followed by52 contrary labels, the complete dense n16
history and opposite-label continuation, and both legacy n256 schedules.
All fault/continuation records receive complete frame reads. Successful
integration flows additionally reconstruct every prediction and observation
outside Runtime. The dense final query has a separate full-assignment oracle.

The collector binds launch HEAD and all execution inputs, keeps them fixed
until collection ends, and retains every terminal outcome. Stop at the
first failure without silent retries or cap changes. The preregistration
claims no actual owned Runtime outcome, model score or release yet. The
earlier16-fixture arithmetic A1 is terminal and is not repeated here.
