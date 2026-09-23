# Joint-noise AMP phases inside the existing owner

Status (2026-09-23): **IMPLEMENTED; EXACT CPU GATE PASS; ALL 17 ACTUAL CUDA
JOBS PASS AT 2432a25; TERMINAL**. This implements the
[joint-excess schedule](JOINT_EXCESS_PARTITION_BRIDGE.md) alongside the
[owned exact reference learner](OWNED_JOINT_REFERENCE.md). The source-bound
jobs establish device conformance, fresh/install continuation and failed-phase
lifetime on their declared cases; see section 6. The registration in section 5
was committed before execution. No Foundation, ERC-1 or constructor decision
class changes.

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

## 5. Original actual CUDA registration (preserved; now terminal)

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

## 6. Actual result and retained reader

All seventeen jobs complete at source
`2432a25064ec8f757f8760f24d1e4f27558dccc8`. Every job is attached before its
first instruction, exits zero, stays under the registered 4-GiB cap and
900-second deadline, and passes its independent worker reader. The largest
observed whole-job commitment is 2,251,014,144 bytes. No source, tolerance or
resource cap changed during execution. No job was retried.

[FP_JOINT_AMP_CUDA_A1.json](../../evidence/minimal/FP_JOINT_AMP_CUDA_A1.json)
retains all outcomes in 24,448 bytes. The checked joint blocks total 894
phases, 293 independently decoded/RNE-checked predictions, 869 complete
literal native phase comparisons, 10,798 actual operation words, 586 half
words and 14,105 outputs including copies. These totals exclude preparatory
phases in fault-only reports and refused phases; they are not the total
executed work of all jobs. The separate fresh known-rate regression adds
13 checked phases and four independently read predictions.

| Boundary | Observed result |
| --- | --- |
| Profile with 4096-bit integer allowance under 32768-bit reference | 58 phases; 18 predictions; four replay events. At ordinary cursor 8, learners retain T=8 and T=10. |
| Paired fresh evidence and installation | 170 phases; independent reference/physical identities begin at 16; paired crossing installs at 20, followed by continued learning to 36. Alpha 1/2 remains spent. Same resident learners, arena, history and current mappings survive transport. |
| n64 closure without literal world expansion | 25 phases/eight predictions over 2^64 native hypotheses. Table 1,326,381 bytes; peak packed 18,052,673 bytes; largest encoded frame 3,018 bytes. Empty-policy stream seals with zero constructor decisions. |
| Historical A1 count cut under the new schedule | 298 phases/98 predictions; reaches T=29, cursor 27 and continues to 48 (profiled T=50). Original tolerances pass. Historical dense A1/A2 are unchanged. |
| Actual reversible rounded-zero excess | 314 phases/105 predictions; after 52 one-rate updates one excess is zero, but 104 updates restore d=0 and the actual half forecast. T=104 remains; final target is unrevealed. |
| S=120 native precision boundary | Third prediction after two label-one events returns UNRESOLVED with actual error 65863667/4117889024. Its 29 outputs are retained; third target is not received and neither predecessor advances. |
| Refusal and corruption | Short output allowance prevents numerical kernel entry. A second-lineage commit failure retains both observed states and actual target without publishing either successor. Prediction/gradient/operation bit flips, equal-word stale output, wrong actual target and common-root mutation all fail. |
| Scratch and profile lifetime | Six monitored prepaid reference/physical/reconstruction calls use the actual pinned extent; a physical postwrite failure retains it. A one-step profile budget retains two completed replay events with no attachment or newborn publication. |

The largest native error in the summarized checked blocks is
48017/23674880 (about 0.00203); the largest normalization error is 1/262144.
The expected refused S=120 endpoint is excluded from checked maxima. Its
failure is evidence for the scale-dependent numerical boundary, not a failed
gate or justification to loosen the contract.

Run `python -X utf8 -B scripts/read_joint_amp_gate.py --negative-checks` to
validate the retained source, complete case list, job identities/admission,
original declarations, relation tolerances and observed refusal/continuation
outcomes. Eighteen altered reports are rejected. This reader imports no Torch
and performs no new device execution. It validates source-bound reports;
the full phase/native/RNE checks happened inside the original workers. The
minimal journal does not contain every frame and is not a standalone proof
of arbitrary physical execution.

This closes the actual owned bridge and fresh/install obstruction for this
registered realization. It gives neither unknown-noise model-quality evidence
nor a total-resource law across arbitrary query widths. Exact integer inference
is still paid host work; gradients and readouts use the actual GPU. Fresh
stochastic-law assumptions remain external premises. The unchanged decision
classes and all terminal historical outcomes retain their original scope.
