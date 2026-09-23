# Unknown-noise acquisition and prediction: four completed n64 tapes

Status (2026-09-23): **ALL FOUR REGISTERED MODEL JOBS COMPLETE; TERMINAL**.
Execution source: `333cba1180607c8a538cb12a7115705e692c41fa`.
The [preregistered protocol](UNKNOWN_NOISE_MODEL_PROTOCOL.md) and unchanged
production gate at 2432a25 define the experiment. All four fresh Windows jobs
exit zero on an NVIDIA GeForce RTX 3090, without retries, limit changes or
partial-prefix scoring. The original [175,543-byte journal](../../evidence/minimal/FP_UNKNOWN_NOISE_MODEL_A1.json)
retains all outcomes and 1,000 four-word evaluation readouts.

## What the experiment establishes

The same equal-prior learner over rates {1/10,1/4} and fair latent worlds
completes all four declared 376-event tapes. The true rate never enters its
initializer or Runtime. All 1,504 native forecasts equal the independent
unsigned-history full joint posterior, and all 1,504 published count successors
match the independent history. The actual AMP path remains within the original
state/probability tolerances, 1/100 and 1/1000. This is scoped model execution
and numerical agreement with a strong exact control, not superiority over it.

The first 63 forest observations provide exactly zero rate information, as
the acquisition theorem predicts. Repeated edges and subsequent cycles do
provide information. The table gives the posterior on the **low rate 1/10**;
final intervals are exact integer endpoints divided by 2^40.

| True rate | Seed | Cut 63 | Cut 126, approximate | Cut 376, grid numerator interval |
|---|---:|---:|---:|---|
| 1/10 | 0 | 1/2 | 0.99764081946 | [1099511627775,1099511627776] |
| 1/10 | 1 | 1/2 | 0.99913559196 | [1099511627736,1099511627737] |
| 1/4 | 0 | 1/2 | 0.00011906178 | [7,8] |
| 1/4 | 1 | 1/2 | 0.50348689038 | [0,1] |

The last tape slightly favors the wrong rate after the repeated sweep; later
observations reverse that preference. Finite positive likelihoods and priors
keep every exact rate weight strictly positive: grid endpoints zero and one
do not authorize deleting a rate. The two seeds share hidden bits, query order
and uniform noise draws across rate strata. These are two paired samples,
not four independent draws from the model prior or a population guarantee.

## Predictive results

Scores use proper probabilities obtained from the two actual stored binary32
masses. Cross-entropy below is conditional expected loss in nats, evaluated
in binary64 against the true label law. Learning continues after every
forecast. The oracle knows the true rate but receives the same observations
and must still infer latent relations.

| True rate | Seed | All 250: AMP | Exact joint | True-rate oracle |
|---|---:|---:|---:|---:|
| 1/10 | 0 | 0.3461874103 | 0.3461869472 | 0.3461855870 |
| 1/10 | 1 | 0.3762280167 | 0.3762255160 | 0.3762248817 |
| 1/4 | 0 | 0.6133203654 | 0.6133193440 | 0.6133119317 |
| 1/4 | 1 | 0.6329596456 | 0.6329616026 | 0.6309940861 |

| True rate | Seed | Initial-training-unseen 124: AMP | Exact joint | True-rate oracle |
|---|---:|---:|---:|---:|
| 1/10 | 0 | 0.3524376481 | 0.3524367047 | 0.3524353388 |
| 1/10 | 1 | 0.3933815209 | 0.3933791694 | 0.3933780922 |
| 1/4 | 0 | 0.6240978628 | 0.6240975074 | 0.6240980261 |
| 1/4 | 1 | 0.6500227129 | 0.6500265223 | 0.6485621561 |

The maximum absolute AMP/exact gap in these eight mean CE comparisons is
3.809352e-6. The gap can have either sign on a fixed tape; it is not evidence
of an improved inference rule. Exact-joint/oracle ordering can also reverse
on an individual tape and subset. The oracle's larger advantage in the fourth
tape is consistent with its early access to the true rate; this is an observed
comparison, not an identification of all sources of predictive error.

For scale, two-class expected Brier losses on all 250 queries are below,
rounded for display. The journal retains exact rational enclosing intervals
with width at most 2^-40, and the corresponding unseen-query results.

| True rate | Seed | AMP | Exact joint | True-rate oracle |
|---|---:|---:|---:|---:|
| 1/10 | 0 | 0.197682842 | 0.197682304 | 0.197681726 |
| 1/10 | 1 | 0.221246896 | 0.221245689 | 0.221245412 |
| 1/4 | 0 | 0.423000838 | 0.422999886 | 0.422992978 |
| 1/4 | 1 | 0.440981262 | 0.440983217 | 0.439546536 |

The retained tie-aware latent classification scores are secondary: rounding
near 1/2 can change a classification or tie without improving proper scores.
The largest evaluation proper-probability error is less than 0.000147.

## Complete execution and measured resources

Each job checks 1,129 phases, 14,664 operation words, 752 half words and
19,176 outputs including copies. Totals are 4,516 phases, 58,656 operation
words, 3,008 half words and 76,704 outputs. The worker reads every retained
frame and padding byte and reconstructs integer plans and primitive RNE
from complete state and actual causal inputs. Literal expansion of the 2^64
native hypotheses is forbidden; `full_literal_native_phases=0` is explicit.
The complete-state basis proof and independent positive control supply that
comparison, not a claim of literal native execution at n64.

| True rate | Seed | Whole-job peak commitment, bytes | Packed peak, bytes | Largest encoded frame, bytes |
|---|---:|---:|---:|---:|
| 1/10 | 0 | 7583363072 | 4888603630 | 7029 |
| 1/10 | 1 | 7582195712 | 4888537719 | 6859 |
| 1/4 | 0 | 7580893184 | 4888172974 | 6632 |
| 1/4 | 1 | 7579086848 | 4888267471 | 6693 |

All workers are attached to the 16-GiB job before resumption, finish within
two hours, and have no limit termination. Each pins a 264,453-byte integer
table and consumes 147,400 arena bytes. The 8-GiB packed and 4-MiB frame
limits hold. Maximum observed complete relation errors across all jobs are
below 0.002906 (state), 0.003228 (native), 0.000001908 (normalizer),
0.000162 (probability) and 0.000000067 (division).

The independent control performs 553,884 vertex transitions per case with
no world enumeration; its largest integer is at most 1,464 bits. Integer
inference and count updates remain paid host work. Actual half/single readout
and gradient arithmetic runs on the GPU. Measurements include retention and
auditors; they are not an isolated inference-throughput benchmark.

Every run seals `SEALED_CUDA_STREAM` with one learner and zero constructor
decisions. These jobs invoke no profile, fresh comparison or installation;
those have the separate terminal 17-job gate. No `CERTIFIED_COMPLETE` decision,
new decision class, full indexed release or Foundation/ERC-1 change follows.

## Post-execution attack on the retained reader

The original worker already checked the complete exact RNE schedule. The
original passive reader checked tolerances and self-consistent normalization,
which was weaker. Changing the first retained row of the first case from

    [1074597300,1099849290,1038200710,1063504400]

to

    [1074597301,1099849290,1038200711,1063504399]

changes one mass word and recomputes the two divisions. The old passive
reader admitted this within-tolerance row. This is an artifact-reader gap;
the original Runtime's full primitive checks did not admit the alteration.

The strengthened reader now derives the two excess integers independently
from unsigned-history rate partitions, executes the exact half/single RNE
equations, and requires all four retained words to agree. It uses neither the
production partition constructor nor its scalar schedule. All 4,000 original
retained words pass, while the altered row and a foreign execution source
refuse. Original journal, device jobs, declared schedule and limits remain
unchanged. This is a post-execution passive audit, not a preregistered test.

Reproduce without Torch or device execution:

    python -X utf8 -B scripts/run_unknown_noise_model.py --cpu-readers
    python -X utf8 -B scripts/run_unknown_noise_model.py --read evidence/minimal/FP_UNKNOWN_NOISE_MODEL_A1.json --reader-adversaries

The journal is a source-bound report of executed audits. Independent word
reconstruction proves agreement with the declared schedule; it does not by
itself prove arbitrary physical execution from a compact JSON artifact.
