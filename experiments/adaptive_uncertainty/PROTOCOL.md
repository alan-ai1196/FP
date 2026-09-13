# RN-4: native uncertainty that learns from later labels

Preregister before target model execution. This follows the
[balanced positive-readout proof](../../theory/proofs/BALANCED_UNCERTAINTY_LEARNERS.md)
and RN-3's distinction between frozen prediction, ordinary learning and
adaptive deployment. Foundation R4, XVII.31 and ERC-1 remain frozen.

## Question and comparison

Does an actually constructed v4 learner use new cross-component labels that
leave the fixed v3 graph uniform? Does that learning improve the continuous
candidate and actual deployed streams, and how close is it to a strong
adaptive posterior with the same revealed information? Installation counts
and historical class bounds remain separate outcomes.

Both exact theory and the endpoint audit show that rate1/8 moves the first
uncertain prediction only to65/128, while the known conditional posterior
moves to41/50. To distinguish mere slow SGD from a representational obstacle,
register rates1/8 and4 before inspecting the new model samples. Rate4 has
first prediction3/4 on the same elementary example; it may also incur greater
range or numerical pressure. Keep both outcomes without selecting a winner
after looking at scores. No learning-rate or resource tuning follows a failed
or poorly performing case.

## Fixed thirty-worker matrix

Two known diagnostics retain RN-3's n8 disconnected worlds A/B, seed0,
conditioned training and complete ordinary evaluation tapes. Reuse the old
v3 and frozen-posterior outcomes from the journal committed at `2ca5b8a`,
with their original execution sources; the frozen posterior is referenced
through the original RN-1 journal at `4d04595`. Execute two new v4 learners (one per
registered rate) and one new adaptive posterior per case.

Eight new IID cases use equal-sized contiguous observed components:

| n | c | Seeds |
|---:|---:|---|
| 8 | 2 | 12, 13 |
| 16 | 2 | 12, 13 |
| 8 | 4 | 14, 15 |
| 16 | 4 | 14, 15 |

Each has both new FP rates and one separate adaptive-posterior worker.
There are twenty FP and ten posterior workers in total. These new
seed/support cases have not been inspected or executed when registering
this protocol. Keep sparse n8,c4 cases even if fresh evidence cannot yield
useful deployment before the stream ends.

Use RN-1/RN-3's seed formulas for hidden bits, training noise, evaluation
noise and pair permutation: 2026091300, 2026091400, 2026091500 and 2026091600, respectively,
plus100*n+seed.
Training observes ten labels on each consecutive within-component path
edge. New cases use IID flip probability1/10 in the ideal law; known tapes
retain conditioned9:1 training. Evaluation presents all n-squared ordered
pairs once. Only ordinary context bytes followed by the target enter FP.
Neither hidden bits nor the component support/list is passed to the proposer.

## Native construction and immutable resources

Register `empirical-binary-relation-balanced-readout-v4` in the existing
relation-source coordinate. The policy makes one owned bounded search at
the training cutoff. It derives its components from retained observations,
compares feasible initialized values, constructs the dense native witness
and admits its actual learner to fresh paired evidence when justified.
All unsearched alternatives remain in the full native decision class.

Keep the original broad node/SUM/PRODUCT/edge caps
`(2n+n^2+2, n^2+6, n^2+4, 4n^2+2n+12)` including lookup competitors.
Register initializer `(1,8)` followed by `n(n-1)` unit values, with slot cap
`2+n(n-1)`. This supplies independent coefficients for every possible
component count without knowing a hidden partition. The actual constructed
prefix, unused intervening slots, work and storage are all paid. No posterior
coefficient or new value/architecture action is introduced.

Register base `(1,1)`, activation16 and normalizer18 before execution. The
old normalizer10/scale8 boundary cannot admit even a correct within-component
positive-rate update; its refusal is retained in the endpoint audit. These
are declared ERC-1 instance parameters, not changes to its frozen specification.
A model exceeding the new fixed limits must halt unresolved. Do not raise
them after an outcome.

Use update unit1, grid16, the two stated rates, reference integer limit32768,
packed cap1GiB and role work cap10^13. Register state/probability tolerance
1/100 for binary64 and actual half/single paths; audit every numerical phase
and report observed maxima rather than treating tolerances as measured error.
Keep the RTX3090,16MiB arena,32MiB native reservation,4096-cell/131072-byte
phase limits, separate24GiB physical-board upper, and a fresh4GiB Windows
job attached before each worker begins, with a20-minute observation timeout.

Fresh reference/CUDA persistence keeps epoch1, horizon n-squared, bound3,
bet3/4 and alpha1/4 per path; global alpha is3/4. Each worker starts its own
ledger. Installation transfers the continuously tested current learner;
it cannot inherit RN-3 evidence or convert an unattained training upper into
class completeness. Do not substitute an initializer's frozen score for
the continuously learning candidate's actual forecasts.

## Strong adaptive baseline

Use the exact independent-fair-bit posterior over all2^n assignments.
Its initial weights follow the same conditioned or IID training law. Before
each evaluation target, sum those weights by the queried parity and include
the known1/10 label noise. Capture the forecast first, then update each
assignment's weight by its likelihood of the newly revealed label. This
continues to handle cycles; do not approximate later data as an independent
forest or ignore labels that were neutral for FP's current gain.

Execute each new adaptive prediction through the same strong half-excess
and single base/normalization pipeline as RN-1/RN-3, using base1 and total
scale10 (within the new range18). Check all actual output words against an
independent rounded calculation. Keep exact posterior and actual AMP scores,
integer/storage/work observations and completed-job/device identity. This
separate value constructor grants no FP coefficient or Runtime authority.
Do not rerun unchanged frozen diagnostics merely to refresh their source.

## Retention and interpretation

At each forecast, the continuously learning FP candidate and adaptive
posterior have the same revealed data cut, although different legal value
paths and computation. The deployed FP stream additionally includes the
initial uniform model and its actual install boundary. Report full-domain
and unseen-pair expected CE/Brier, raw single-division CE, probability and
classification diagnostics. The unseen set still excludes diagonals and
both orientations of initial training edges, even after those later labels
have been revealed. It is a fixed evaluation subset, not a claim that each
of its later relation implications remains unlearned.

Retain failed attempts and honest resource, numerical or evidence exhaustion;
never impute an absent candidate or unexecuted tail. Keep only compact
outcomes, source-bound jobs, independent checks and references to old
journals, without weights, datasets or bulk phase histories. Fixed PRNG
tapes prove no stochastic premise, population rate, Bayes dominance or
restarted-family significance guarantee. Pairwise balanced readouts are not
claimed to implement a globally consistent latent posterior.
