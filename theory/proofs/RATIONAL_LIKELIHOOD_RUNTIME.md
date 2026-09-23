# Owned general rational likelihood lowering

Status: **IMPLEMENTED; CPU PASS; CUDA A1 TERMINAL WITH ONE FAILURE;
ONE-CASE A2 REGISTERED, UNRUN**.
This binds the [coprime component](COPRIME_LIKELIHOOD_READOUT.md) to the
existing complete native learner and its Runtime. It changes a physical
representation, not FP syntax, the unit simplex U, the observation law or
any constructor decision class. Foundation R4 and ERC-1 remain unchanged.

## 1. Closed contract and derivation from actual native state

`RationalLikelihoodContract` declares signed counter bits, a peak factor-basis
cell cap, factorization work and per-commit integer work. It is a distinct
closed type. The existing `LikelihoodEncodingContract`, descriptor fields,
encoding ID and single-radix operation sequence remain. The new identities are:

- encoding: `finite-affine-coprime-likelihood-coordinates-v1`;
- arithmetic: `eager-cuda-half-forward-single-gradient-owned-integer-rational-decode-v1`;
- work: `prepaid-coprime-factorization-owned-integer-decode-and-CUDA-output-v1`.

The native half-forward/single-gradient schedule is unchanged. The generic
indexed contracts reject this dense likelihood representation. A new
contract cannot borrow the old arithmetic ID or its single-radix decoder.

Runtime pays before deriving a model from actual G, Gamma, U and the complete
registered finite source domain. The existing positive affine-head analyzer
retains every native node/fixed slot while proving the selected slice affine.
Expert normalizers must agree, and all actual ratios must be strictly positive.
Only unit-rate, one-event simplex U without a grid or delayed state is admitted.
Missing domain, unsupported U or exhausted arithmetic remains UNRESOLVED.

The rational descriptor stores the coprime bases, prior exponents, reference
event, selected event-difference rows and complete rational reconstruction.
Rows are flattened in world-major/base-minor order. Prior-only bases and an
empty basis are legal; neither can erase the selected simplex slots. The
constructor validates the declared peak width and pairwise coprimality.
Independent exact reconstruction checks all original rows. The initializer
exponents are decoded before authorizing physical initialization.

The complete descriptor is retained in its initialization phase. Every later
raw encoding carries its immutable descriptor digest, the complete counter
vector and the actual pending event. The owner checks raw predecessor identity
before execution, actual source/target linkage on observation, and exact
counter transitions separately from numerical tolerance. T remains the
optimizer-step clock, including actual profile multiplicities.

## 2. Payment, actual integer bytes and failure lifetime

Let K be the selected width, E the event count, C the declared peak basis cap,
R=KC and b the reference integer-bit allowance. The old native affine analysis
charge is extended by the full declared factor work and

`64 (R+1)(E+R+1)(min(R,E)+1)`

primitive units for the larger exact row elimination/reconstruction. In
addition to the existing preparation cells, the scratch envelope adds
`4(R+1)(E+R+1)+8C` cells. Each packed cell is charged
`128+2 ceil(b/8)` bytes. This bounds the retained intermediate tables in the
declared packed machine; it is not a CPython heap or bit-time theorem.

With B actual bases, each commit reserves a separate bytearray of

`4096 + (4KB+8K+4B+8)(128+2 ceil(b/8))` bytes.

This covers exponent/difference tables, integer powers/weights, loaded weights
and rational ingress temporaries. The owner additionally prepays the declared
integer work, eight primitive units per reserved byte for serialization and
validation, and the existing phase/descriptor/output charges. Numerical
integer work remains guarded; no float logarithm or prime factorization runs.

The decoder accepts only an exact-size, contiguous writable byte view of that
owned extent. It commits the actual pending event, reconstructs exponents
from physical counters and T, proves the integer power/scale envelope, and
computes primitive positive weights. Each weight occupies ceil(b/8) actual
bytes in the paid extent. The kernel ingress reads those bytes back and checks
them before forming its one shared dyadic scale. No reference theta or
caller-supplied posterior enters this path.

Successful publication releases scratch. An unsuccessful admitted phase keeps
the extent owned and charged: an exception traceback may retain a memoryview
even after the decoder stops. Counter/work/precision refusals preserve the
observed predecessor, including every native gradient coordinate, pending
event, cursor and step clock. They do not clear an unfinished update unit or
publish a new current state. Preparation failures also retain any already
admitted scratch. Prepayment failure enters no decoder.

Actual Python objects coexist with the bytearray. An enclosing enforced host
job measures and caps their complete commitment. The packed reservation is
not substituted for that obligation.

## 3. Physical schedule and the complete bridge

For integer weights A and s=max bit_length(A), use exact rational-to-binary32
ingress on the K-vector A/2^s, one zero constant, K ordered device additions
and one vector division. Reuse that vector directly; no extra K-vector stack
copy is needed. Copy the normalized selected weights into the complete N-slot
master state and clear all N gradient slots only at the whole commit.

The exact CUDA output extent is **1+3K+2N** cells. Initialization, prediction,
observation and clock attachment retain their existing complete schedules.
Native prediction and observation still execute genuine half/single device
arithmetic, including fixed-slot gradients and source PRODUCTs. Integer
factor combination is explicitly host computation.

The selected-weight theorem is not the complete bridge. Runtime checks every
phase against its own native reference endpoint and every prediction against
the registered whole forward arithmetic/range relation. It checks immutable
predecessors and exact metadata independently. An error or unexpected output
schedule is retained and cannot advance the prefix.

The independent reader derives likelihoods by native reverse derivatives,
checks descriptor factors by exact divisibility/rank/reconstruction, and
replays the full actual likelihood word. It constructs expected primitive
weights by common denominators and an overall gcd, without the production
factor basis or coordinate decoder. Every recorded commit word and output
count is checked, together with full frames and all other native phase words.
The byte comparison also retains the original descriptor when a deliberate
mutation is tested; it never repairs a private Runtime.

## 4. CPU evidence and actual A1 declaration

`python -X utf8 -B scripts/audit_rational_likelihood.py --write` retains the
[CPU evidence](../../evidence/minimal/FP_RATIONAL_LIKELIHOOD_CPU.json).
Ten complete banks pass 3,051 exact native cache/all-gradient/commit triples,
actual descriptor derivation, counter/pending transitions, paid weight bytes
and independently constructed ingress words. They include the n2/n3 mixed-rate
PRODUCT graphs with bases (2,3,5) and ranks 2/4, prior-only factors and rank zero.
Six further complete native triples use selected slots (0,4) in a six-slot
state, retain all fixed/unused coordinates and distinguish cursor 17 from
optimizer step 6 after a birth at cursor 11. The combined native count is 3,057.
Nineteen malformed, budget, descriptor, counter or identity checks pass.
Three real Runtime-ledger probes use an always-refusing CPU backend: short
work/storage prevents entry; admitted failure retains its 43,896-byte view.
They are payment-boundary checks, not successful CUDA execution.

The single-radix CPU audit also passes its 958 exact native transitions,
additional affine/clock cases and 19 negative cases. Against the committed
1dfe683 source, two serialized legacy models and six raw metadata transition
triples remain byte-for-byte identical. This is explicit compatibility
evidence; no historical device job is repeated to obtain it.

The new actual gate is
`python -X utf8 -B experiments/joint_uncertainty/rational_likelihood_lowering.py --matrix --write`.
Commit the full execution dependencies before running. A1 records the exact
source and each completed enforced Windows job. Its 13 cases include the
274-event recovery, a 12-event n3 unknown-noise stream, a 48-event n2 mixed-rate
profile/fresh/install continuation, five decoder/integrity faults, three
preparation faults, one declared finite-class check and a three-event legacy
regression. The profile replays the first two observations twice at cursor2;
ordinary learning must continue after actual installation. The fixture's
constant comparator tests fresh/installation mechanics, not model superiority.
All successful native posteriors use the strong exact joint-bank oracle.

Each new worker has a 4-GiB whole-job commitment cap and six-minute wall limit.
The main packed cap is 1 GiB, work is 10^11 per role, reference precision is
32768 bits, factor-basis cap is 8 and factor/decode work is 10^6 each.
State/probability tolerances are 1/100 and 1/1000. Phase output allowance is
8192; frames are 1 MiB for n3 and 256 KiB otherwise. The small class fixture
retains its stricter 512-MiB packed cap and binary64 tolerance 1e-9; other
binary64 tolerances are 1e-8. The complete declaration is executable preflight.

The finite class is the existing at-most-one-node, no-edge/no-PRODUCT,
at-most-three-slot grammar with actual Gamma/U and complete source domain,
plus its deployed comparator. Its 20 members include 15 expected unresolved
initializer shapes, so the result must remain UNRESOLVED with no class proof.
The profile installation uses the existing public constructor and paired
fresh evidence without an optional historical selection assertion. No
CERTIFIED_COMPLETE token is claimed anywhere in this gate.

The original registration was committed at 5937e1b. Its actual A1 is now
terminal; the outcome below supersedes the original unrun status.

## 5. A1: successful recovery, and a genuine full-native precision obstruction

The [A1 journal](../../evidence/minimal/FP_RATIONAL_LIKELIHOOD_CUDA_A1.json)
retains all 13 enforced jobs at 5937e1b. Twelve execute their declared checks.
The 274-event reversal passes 823 complete CUDA phases and 274 independent
commit tapes, including temporary zero weights and the expected recovered
endpoint words. The n3 joint unknown-noise stream passes 37 phases/12 commits.
Counter overflow, dormant coordinate/descriptor corruption, preparation
work/storage/domain faults, decode work and a short decode view all refuse
without a false certificate. Failed admitted scratch stays paid. The finite
20-member class remains UNRESOLVED with 15 unsupported members; the three-event
legacy control passes. Across these successful workers there are 1,991
checked phases and 657 independently reconstructed commit tapes. Peak whole-job
commitment is 2,499,796,992 bytes, below 4 GiB. None timed out or hit its cap.

The mixed profile/install worker fails an audit assertion after an unexpected
prediction refusal. Its retained traceback does not contain the refusal
cursor or reason, so it supplies no fresh/install completion claim. A new
independent exact replay identifies a necessary numerical refusal on its
registered trajectory; this is not a reason to erase the failed job.

**Exact counterexample to promoting selected-weight accuracy to full-native
accuracy.** After 29 copies of the n2 pair (0,1), label0, the four joint
integer weights are

`(18^29, 2^29, 15^29, 5^29)`.

The native posterior is their normalization. The registered integer decoder
and RNE32 commit produce selected master words
`(1065268829, 293987261, 1000657236, 615054864)`; every selected error is less
than 1e-7. The next native half casts are nevertheless

`h = (1019/1024, 0, 1319/262144, 0)`, `SUM h = 262183/262144`.

For this graph, the two feature rows are (17,1,14,4) and (1,17,4,14), with
base masses (1,1). Before the remaining arithmetic rounds, their total on h
is `2+18 SUM h = 2621791/131072`, rather than20. The actual half products,
ordered single sums and final half node casts give stored masses
`(18,129/64)`, and their single total is `1281/64 = 20+1/64`.
The native exact total is20. Thus the normalizer error is exactly1/64,
strictly above the registered1/100 tolerance. Native-cache error also exceeds
1/100. Current normalized forecast error is small; it cannot authorize
erasing the complete cache or unfinished ambient gradient from the bridge.

The profile has replayed two early observations twice. Candidate step29
therefore occurs at ordinary cursor27, before the next target is revealed.
The [exact audit](../../experiments/joint_uncertainty/rational_native_precision.py)
checks all50 candidate predict/observe/commit triples on the originally
registered word. Seven passive prediction cuts violate1/100. The maximum
normalizer error is1/64, native error is about0.01508952, master error is below
1e-7, ambient-gradient error below0.001, and probability error below0.0001.
The [small artifact](../../evidence/minimal/FP_RATIONAL_NATIVE_PRECISION.json)
retains exact maxima and the witness. Cuts after the first refusal are passive
calculations, not an owned continuation of A1. No Torch is imported.

This falsifies the proposed tolerance on that whole-native trajectory, not
the coprime representation or its selected-weight theorem. The correct A1
outcome remains refusal. No Foundation or ERC-1 definition changes.

## 6. Separately declared continuation

`python -X utf8 -B experiments/joint_uncertainty/rational_likelihood_lowering.py --matrix --attempt 2 --write`
registers only `mixed-profile-install-a2`, with full-native state tolerance
1/50. The exact preflight checks that this is the sole contract difference:
G, Gamma, U, the48-event tape/four profile updates, probability tolerance1/1000,
binary64 tolerances and all resource caps remain. No production arithmetic
changes. Failure diagnostics now retain cursor and Runtime reason.

This is an explicit weaker numerical contract chosen after the retained
counterexample; it does not turn A1 into a pass. The fixed-word preflight
proves its bounds only for the specified rounded interpreter and word, not
all histories. Actual AMP, paired fresh evidence, installation and learning
after installation must still pass their independent complete readers in A2.
At this declaration A2 is unrun. Keep its committed source fixed while live;
retain every outcome. Do not repeat the twelve successful A1 cases or any
historical device job. Neither gate issues CERTIFIED_COMPLETE or a full
indexed release.
