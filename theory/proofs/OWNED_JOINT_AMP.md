# Joint-noise AMP phases inside the existing owner

Status (2026-09-23): **IMPLEMENTED; EXACT CPU GATE PASS; ACTUAL CUDA GATE
REGISTERED, NOT YET EXECUTED**. This implements the
[joint-excess schedule](JOINT_EXCESS_PARTITION_BRIDGE.md) alongside the
[owned exact reference learner](OWNED_JOINT_REFERENCE.md). Device conformance,
actual fresh/install continuation and failed-phase lifetime are hypotheses
for the registered jobs below until their results are retained. No Foundation,
ERC-1 or constructor decision class changes.

## 1. The complete physical coordinates

`JointCudaPrefixContract` binds the full ordered native model and
`JointPartitionAllowance`; both must equal the reference registration.
The current reference initializer/learner already bind exact G/Gamma/U and
the complete categorical source domain. Another model, rate order, prior,
decoder allowance or dense likelihood encoding cannot inherit this path.

Backend: `owned-indexed-joint-noise-half-mantissas-single-readout-v1`.
Forward schedule: `joint-noise-integer-excess-half-mantissas-single-readout-v1`.
Work model: `prepaid-joint-noise-integer-parts-and-full-rne-basis-v1`, with the
existing evidence-codec surcharge when that codec is selected.

The physical learner retains the entire joint count encoding: model, signed
counts, diagonal balance, total optimizer steps T, ordinary cursor and pending
ordered query/target. Parameters are exactly decoded from these coordinates.
A pending unit additionally owns a binary32 tensor containing all 2J+1 gradient
forms. A prediction owns seven binary32 readout words plus its complete native
predecessor and ordered query. Non-head native caches are exactly decoded from
that query, the model and the original rate/world slot ordering. No rare world
or rate is dropped because a transient floating excess is zero.

Initialization independently derives the registered prior/fair-world Gamma.
Observe binds the actual owned pre-target phase and actual target. Commit
increments the count representation through the proved native unit-simplex
likelihood identity; attachment changes only the clock namespace. These exact
host transitions realize the original U. The GPU portion computes the readout
and pending gradient words; it is not claimed to perform integer elimination
or a dense SGD update. Counts are not copied from trained reference endpoints.

## 2. Independent construction and complete checking

For each physical prediction, the fixed private kernel receives that path's
own committed state and the actual source row. It constructs N0,N1,Z in the
owner's paid integer extent. It receives no reference partitions, weights or
normalized forecast. The numerical schedule then:

1. Converts each positive integer's unit-scale mantissa to binary32, casts it
   to half, widens to single and applies the common binary scale. A zero part
   and an exponent below the declared single subnormal range follow the exact
   zero rules from the theorem.
2. Forms the shared denominator, two excesses, actual masses, actual summed
   normalizer and two divided probabilities in separate binary32 operations.
3. During observation, uses the resident actual target mass to compute the
   fixed derivative and all rate-specific matching/other gradient forms.

Prediction emits 21+4k words including output copies, with k positive parts:
at most 29 outputs and two half casts. Observation emits 6+8J outputs. Exact
initialization, commit and attachment have zero floating outputs. This does
not make their state, host computation or retained evidence free.

Every actual primitive is read from its paid current arena extent and compared
with exact RNE. After execution, the owner reconstructs the complete integer
plan from the independently held actual inputs. Common rescaling of N0,N1,Z
fails that comparison even when the normalized response is unchanged. A fresh
arena readout and a full scalar replay check every final word and every trace
entry, including widths, operation order, signed zeros and output copies.
Boolean/int equality cannot substitute for a typed raw word.

The native relation separately compares all native head/mass coordinates,
the normalizer and actual stored-mass sum, both rounded and properly normalized
probabilities, every active ambient gradient class, and exact complete encoded
state equality. On a nonloop query both classes exist for each rate; on a
diagonal query only the actual parity class has native slots. Inactive stored
forms still undergo full RNE conformance. T, diagonal evidence and model/prior
binding are not inferred from matching current probabilities.

The schedule uses the smaller of the reference bit limit and registered
integer allowance for its exact scalar checks. A 4,096-bit allowance beneath
a 32,768-bit reference registration preserves the same RNE words when the
preflight fits. Treating these two declarations as necessarily equal would
have produced an implementation failure for a legal resource contract.

This retains the existing fixed trusted-kernel, serializer, arithmetic
interpreter and serialized public API boundary. There is no new external
plan/result proposal or authority callback. Arbitrary trusted-code replacement,
concurrent mutation and general Python process-memory attacks are not sandboxed.
The fault jobs below probe specific output, metadata, target and storage faults.

## 3. Whole-domain range, resources and continuation

For the registered 3<=S<=2^24, all integer coefficients and S-2 are exactly
binary32 representable. Rounded nonnegative part/shared-sum ratios lie in
[0,1]. Monotone RNE therefore gives excesses in [0,S-2], masses in [1,S-1],
and both stored mass sum and rounded normalizer at most 2(S-1). These are
whole-domain physical bounds for every admitted forecast, not a fit to the
next source row. The registered tests use activation cap S-2 and normalizer
cap 2(S-1), retaining the original accuracy tolerances 1/100 and 1/1000.

`JointAmpRange` binds the complete decoded theta, including T, and the whole
categorical domain. The existing owner uses these mass boxes for same-path
fresh evidence. Proper stored-mass probabilities, not merely rounded probability
words or reference forecasts, feed the physical score process.

The reference and physical paths use the existing root-lifetime pinned integer
extent serially. Each physical prediction is charged for two full integer
constructions, guarded scalar work and complete RNE/coordinate scans before
execution. Specifically its construction/check surcharge is

`2*decoder.construction_work(model,budget)
 +1024*(n+bit_length(P)+(Q+1)*ceil(log2 S)+J+1)
 +128*(n+1)*output_cap`,

where Q is the declared committed-step cap. This is in addition to the existing
phase, relation, readout, retained-frame, arena and evidence-codec charges.
Temporary bigints and metadata remain real host costs; the table extent is
not a whole-process memory bound. The job supplies separate physical host
admission in actual tests.

The owner retains failed phase frames and scratch under the same rules as
successful work. A released borrowed view cannot unpin the permanent export.
All current learners publish together only after the reference and physical
phases succeed. Profile replay retains its distinct T and local clock before
attachment. A fresh paired crossing and installation must be produced by the
existing owner from its retained identities; flags and helper records cannot
authorize them.

The installation transport has no new root, prefix or arena coordinate. Its
closed state dispatch now recognizes the joint resident record and checks its
complete raw encoding and every initialized tensor extent. The transaction
preserves the same resident objects, arena, complete reference learners,
history and spent alpha while transferring roles. Actual reachability and
post-install continuation are explicitly tested below; they are not inferred
from the passive relation or this transport description.

## 4. Exact CPU evidence

`python -X utf8 -B scripts/audit_joint_amp.py --write` produces
[FP_JOINT_AMP_CPU.json](../../evidence/minimal/FP_JOINT_AMP_CPU.json).
The complete audit covers 366 reachable cuts, 2,844 ordered-query predictions,
5,688 both-target observations, 227,244 scalar outputs including copies and
5,628 half words. The independent tape prototype agrees with every integer
root, RNE endpoint, operation trace and gradient class. All S=20 and S=3 cases
pass the original tolerances. At S=120, 182 cut/query cases correctly return
UNRESOLVED for the native relation; they are separate passive tests, not
continuations of refused Runtime phases.

Another 80 complete literal native triples check all slots, caches and
gradients through a profile attachment at T=4/cursor2 and continuation to
T=80/cursor78. The original two-event S=120 witness is refused with unchanged
native error 65863667/4117889024. The old S=20 A1 cut at T=29/cursor27 passes
this distinct schedule at the original tolerances; the terminal dense A1/A2
verdicts remain unchanged. A two-snapshot mixed-rate 1,000/1,000 reversal
retains rate evidence while recovering the half forecast. It is not a
2,000-event device execution.

Adversaries reject thirteen plan-field mutations, common-root scaling, seven
prediction-word changes, five gradient-word changes, 22 operation-word changes,
two trace lengths, extra/boolean fields, wrong actual targets, an insufficient
output extent and two foreign CUDA registrations. A narrower 4,096-bit integer
registration produces the same admitted prediction words. The complete owned
reference audit and prior known-rate AMP CPU audit also pass.

## 5. Registered actual CUDA gate

Commit all code, readers and this protocol before running
`python -X utf8 -B scripts/audit_joint_cuda.py --attempt 1`. The CPU-only
`--preflight` imports no Torch and prints the exact declaration. Keep HEAD and
all execution dependencies fixed until all launched jobs are terminal. Retain
every result in a new `FP_JOINT_AMP_CUDA_A1.json`; stop at the first unexpected
failure and never overwrite, silently retry or change a cap within an attempt.

Seventeen fresh Windows jobs each have a 4-GiB commitment cap, 900-second
deadline, attachment before the first instruction, 32-MiB tensor arena,
64-MiB allocator cap and the existing complete byte-preserving evidence codec.
Joint phases have 64 output cells, 64-KiB retained frames through n3 and
512-KiB frames at n64. The integer contract is join64/live1024/arithmetic32768,
T-cap2048/32768 bits, except the profile job's 4096-bit cap and the explicit
one-step/short-output refusal cases. The fresh four-event legacy regression
uses its existing registered bounds and a new owner after these shared changes.

Cases cover ordinary/profile clocks; fresh paired evidence, actual installation
and continuation to cursor36; an n64 eight-event empty-policy closure; the
old A1 count cut reached by this new physical schedule and continued to48;
104 one-rate updates followed by an actual restored-half prediction; and the
expected S=120 third-prediction refusal after two label-one events. Faults cover
unfunded execution, second-lineage commit failure, fresh prediction/gradient/
operation word changes, a stale equal-word output, actual-target substitution,
common-root plan mutation, pinned table lifetime after a physical postwrite
fault, and profile exhaustion before attachment.

The independent reader binds queries and targets to retained actual ingress,
reconstructs counts/clocks phase by phase, checks all complete native phases
for small models, and compares larger predictions with a separate integer tape
and RNE interpretation. It checks every retained frame and padding byte, raw
operation/endpoint word, and recorded table extent. No model score, all-width
resource optimum, GPU integer inference or new CERTIFIED_COMPLETE follows,
even if all jobs pass. At this registration commit, none has yet run.
