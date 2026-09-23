# Four unknown-noise model tapes through the owned joint AMP path

Status (2026-09-23): **REGISTERED AT 333cba1; ALL FOUR JOBS COMPLETE; TERMINAL**.
The [results](UNKNOWN_NOISE_MODEL_RESULTS.md) report execution at that fixed
source and a subsequent passive reader strengthening. The registration below
records the pre-execution experiment and is not a new launch instruction.
The complete joint AMP/fresh/install gate passed all 17 jobs at 2432a25.
This is a new model comparison, not a rerun of any historical device attempt.

## Scientific question and fixed observations

Can the complete native learner infer a shared finite noise rate while
learning latent pair relations, preserve its exact joint-posterior behavior
through actual half/single execution, and finish under the declared whole
resource limits? What predictive cost remains relative to an oracle that is
given the true noise rate? Agreement with the exact joint control is required;
it cannot establish a statistical advantage over that same posterior.

Use exactly the four cases `(64,1/10,0)`, `(64,1/10,1)`, `(64,1/4,0)`,
`(64,1/4,1)`, in that order. The native prior is fixed at equal mass on rates
1/10 and 1/4 and independent fair anchored worlds: 2^64 joint hypotheses.
The case's true rate is provided only to the data generator and score/oracle
reader, never to Runtime or its initializer. It is a stratum, not a learned
parameter supplied in advance.

`unknown_noise_model.py` fixes three independent Python Random streams from
seeds `202609230100+100*n+seed` (hidden bits),
`202609230200+100*n+seed` (evaluation order), and
`202609230300+100*n+seed` (noise). For each seed, both true-rate strata share
hidden bits, query order and uniform noise draws in `{0,...,19}`. The flip
threshold is 2 or 5. These are two paired seeds across two rate conditions,
not four independent draws of the prior or a population estimate.

Train with one lexicographic sweep over the 63 adjacent pairs, then a second
sweep over those same pairs. Evaluate the 250 ordered nonloop queries with
distance at most two, once each, in the fixed shuffled order. Learning
continues after every evaluation forecast. The 124 distance-two queries were
absent from training; their reverse orientation may already have appeared
during evaluation. Targets are fresh independent flips conditional on hidden
bits and the fixed true rate. Every source and target enters ordinary ingress.

The existing [acquisition law](../../theory/proofs/NOISE_ACQUISITION_AND_STATE.md)
predicts exactly no rate information in the first forest sweep. All 63
pre-target forecasts are half, and the rate posterior at cut63 remains the
declared prior. Repeated observations then supply short-cycle evidence;
distance-two observations also close cycles. Retain posterior intervals at
cuts 0,63,126,376. No requirement says that any finite sample must concentrate
on the correct rate, or that four tapes establish a population guarantee.
This experiment tests the existing acquisition law and its physical learner;
it does not introduce a new identifiability theorem or architecture action.

## Strong independent controls and scores

The primary control is the exact full joint posterior over rates and worlds.
It stores per-edge unsigned label counts and diagonal counts, then sums
positive integer likelihoods by a vertex-prefix recurrence with at most
eight entries `(last two bits, queried parity)` per rate. All rate evidence
remains unnormalized until joint aggregation. It uses no Runtime signed-count
decoder, bucket plan, excess roots or uploaded native probabilities.

The same independent sums also produce the exact posterior forecast conditional
on the true rate. That oracle receives extra information and is explicitly
labeled as such. It receives exactly the same observations. It is not weakened
to a point estimate, independent-edge posterior or fixed latent orientation.
Every ordinary native forecast must equal the independent unknown-rate
control, and every complete count successor must match the unsigned history.

Score all 250 evaluation queries and the 124 queries absent from initial
training. Primary AMP probabilities are the proper normalization of actual
stored binary32 masses. Retain the two mass words and two divided probability
words for every evaluation forecast. The reader checks exact single-round
normalizer/division consistency and the full reference/physical tolerances.
Expected cross-entropy is a binary64 diagnostic against the true conditional
label law. Two-class Brier loss is enclosed by exact per-query rounding on a
2^-40 grid, avoiding an unbounded sum of rational denominators. Also report
latent-relation error with half weight for ties. No incomplete prefix is scored.

The generator, four cases, comparisons and limits are fixed before actual
model jobs. The small CPU audit computes no scores on these four tapes.
This is a declared deterministic comparison, not blind model selection.

## Complete native and resource contract

Use the already executed joint model/Gamma/U and complete categorical source
domain. Keep all 2016 signed count coordinates, total optimizer steps,
diagonal evidence, pending state and ordinary clock. The width restriction
belongs to these tapes; no future source is removed from the native interface.
The complete indexed program is initially deployed. No profile, candidate
construction, persistence or installation is invoked; those are independently
executed gate results. Empty-policy stream closure issues zero constructor
decisions and grants no class optimality.

Keep the established larger model envelope: 16-GiB Windows job, two-hour
deadline, 8-GiB packed retention, 10^15 work per role, 256-MiB arena,
512-MiB allocator cap, 4-MiB complete frames, 65536 outputs, and 32768-bit
reference arithmetic. State/probability tolerances remain 1/100 and 1/1000.
Native activation/physical normalizer caps are 18/38 for the S=20 realization.
The exact native normalizer remains 20. Use the same complete byte-preserving
phase codec as the joint gate. Full paid frame extents remain retained.

Joint integer allowance: join64/live1024/arithmetic32768/T396/I32768.
The existing [width-two geometry proof](../../theory/proofs/BAND_MODEL_RESOURCE_BOUND.md)
gives join32/live832 and at most `212*n-195` positive geometry operations for
every support subset and every query. The shared rate schedule adds powers
and aggregation. Binary exponentiation has
`p(e)=popcount(e)+bit_length(e)-1 <= 2e` for positive e and p(0)=0. With
H=sum|d| and A+B=T-H, per-rate extra work is bounded by

    2 SUM p(|d|) + p(A) + p(B) + 14 <= 4T + 14.

Before every forecast T<=375. Thus both rates need at most
`2*(212*64-195+4*375+14)=29774` positive operations, below32768. The guarded
integer envelope is `64+bit_length(2)+5*(375+1)=1946` bits, with scalar-readout
guard2970, below32768. The fixed table/root extent is264453 bytes under the
declared T396 allowance. Each prediction has29 output words and each
observation22, including copies. All 376 predictions therefore require
19176 outputs, 14664 operation words and752 half casts across1129 phases.
These bounds exclude temporary bigints, metadata, frame retention, total
host/time and implementation failure; those are measured, not assumed to fit.

The [CPU artifact](../../evidence/minimal/FP_UNKNOWN_NOISE_MODEL_CPU.json)
checks480 small full-assignment forecasts,384 complete unsigned/native state
and partition matches, all16 four-edge forest label words, and an off-band
refusal. It reuses the existing122576-case geometry audit rather than
repeating it. Neither literal world expansion nor a known-noise replacement
is allowed in the actual n64 Runtime.

## Execution and minimal evidence

`scripts/run_unknown_noise_model.py --preflight` reads the complete terminal
17-job gate and CPU evidence, and checks that production is unchanged from
2432a25. Commit this protocol, code and readers before `--attempt 1`. Keep
HEAD and all execution dependencies fixed while any job is live. Each worker
is attached to its whole-host limit before its first instruction; the limit
includes controls and final auditors. Exact integer inference is host work;
actual half/single readout and gradient arithmetic runs on the GPU.

Retain every outcome in `FP_UNKNOWN_NOISE_MODEL_A1.json`. Continue after an
honest resource/numerical refusal, stop at an unexpected execution/audit
failure, and never retry, overwrite or relax a cap within an attempt. Record
actual GPU identity, SDK job admission/termination, complete phase/resource
summaries, rate checkpoint intervals and the250 four-word evaluation readouts
for completed jobs. Preserve failures without scoring partial prefixes.

The worker independently reconstructs all complete phase transitions,
integer plans, primitive RNE and endpoint words, and reads every retained
frame/padding byte. `--read PATH` replays the deterministic independent
control and scores retained actual readouts without importing Torch or running
a new device job. Report all four outcomes, including a lack of rate learning
or poor predictive performance. No whole-width efficiency, GPU integer
inference, population improvement or complete indexed release follows.
