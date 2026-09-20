# FP Handoff

This file is written for a capable researcher/model that has **no access to prior chat history**. Treat the repository, especially `FP_THEORY.md`, as authoritative.

## 1. Current research state

The current canonical theory is [`FP_THEORY.md`](FP_THEORY.md). Its status is:

- **Foundation theory frozen.** The state/equivalence/acquisition/construction/physical-realization foundation survived the latest adversarial pass.
- **Experiment Resource Contract ERC-1 frozen.** Read [`EXPERIMENT_RESOURCE_CONTRACT.md`](EXPERIMENT_RESOURCE_CONTRACT.md). XVII.31 closes the scoped PRODUCT/SUM/range/precision study; static cases and their remaining constants stay parked while registered device experiments proceed.
- **Reference/CPU and RTX 3090 AMP baseline frozen.** The CPU prerequisite passed at `ebe2c4c`; the complete target integration at `5e55eb4` passed all 21 CPU and 10 CUDA scripts in one fresh clone. Read [`CUDA_RELEASE_SCOPE.md`](theory/proofs/CUDA_RELEASE_SCOPE.md). The current prospective strategy is a separately audited extension, not a rerun of that entire release.
- **Registered experiments UNHELD.** Proceed within the tested target scope and frozen ERC-1; do not interpret the correctness release as a model-quality or structural-forcing result.

The first post-release RTX 3090 resource experiment is complete. Read
its [results and curves](experiments/erc1_rtx3090/RESULTS.md): all 54
preregistered known-table configurations ran, 44 sealed and 10 remained
honestly unresolved. A strong fractional-Horner control survives the
ordinary Horner underflow. Reciprocal recurrence improves exact accuracy
by more than 10^14 after n=3 with no further AMP accuracy gain. It saves
nodes/edges against the strong SUM control on mixed Q, but not scalar Q.
Small-slack reference-exact constructions can be physically worse than
cheaper approximants. These are finite measured Programs, not a complete
hardware optimum or a Foundation counterexample.

The first ordinary-data model experiment [RN-1 is also complete](experiments/relation_noise/RESULTS.md):
36 workers, 18 sealed FP streams, 12,564 independently replayed CUDA and
binary64 phases each, and a strong separately executed AMP posterior.
All eight conditioned connected cases install and match the noise floor
on unseen relations. All eight IID cases construct no candidate, despite
correct observed edge majorities and posterior CE near the noise floor.
The RN-1 proposer rejects fitted scales absent from its initializer;
exact post-analysis shows its already available scale8 beats scale1 and
uniform on every IID training sample. No unbuilt candidate gains a score.
The [gate lemma](experiments/relation_noise/GATE_ELIGIBILITY.md) exposes a
second bottleneck: categorical-upper eligibility is about 6.65e-7
at n=16, despite correct strict-majority recovery probability above 0.975.
Two indistinguishable disconnected training worlds produce candidate CE
0.325 versus 1.603; the uncertainty-preserving posterior scores 0.593 in both.

That implementation obstacle now has a [scoped prospective solution](theory/proofs/OWNED_PROSPECTIVE_SELECTION.md).
The v2 proposer selects by exact likelihood among actual initializer values.
The owned policy can admit a compared improving candidate from an unresolved
class, and installation binds its actual paired starts/current trajectories.
A historical training maximum is optional additional checked provenance.
No class proof is invented: both incomplete bounded and partial-enumeration
cases install on CPU and RTX 3090 while their final class decisions remain
`UNRESOLVED`. An actual one-slot scale1 case and the work/state/evidence
refusals pass. Run `scripts/audit_prospective_selection.py`; original CPU/CUDA
installation and policy/run regressions plus the n=32 reference audit pass.
These extension checks do not relabel the old 31-script baseline release.
Their compact [CPU](evidence/minimal/FP_PROSPECTIVE_SELECTION_CPU_AUDIT.json)
and [CUDA](evidence/minimal/FP_PROSPECTIVE_SELECTION_CUDA_AUDIT.json) records
bind `9ec4c33`: 8/9 workers, 1,120/1,323 binary64 phases and 1,323 CUDA phases.

[RN-2 is now complete](experiments/prospective_relation/RESULTS.md) at
`5bcbb49`: 28 new workers, twenty sealed FP streams, nineteen installations,
17,064 independently replayed CUDA/binary64 phases each, 96 independently
recomputed new score records and twenty prospective decision replays. All
eight known IID failures and all eight preregistered new IID samples now
construct and install native models, while their full training classes stay
`UNRESOLVED`. The four conditioned/disconnected diagnostics retain actual
historical bounds. Frozen connected candidate CE reaches 0.325083; new-seed
deployed means are 0.443389 at n=8 and 0.358384 at n=16. Strong retained/new
AMP posterior controls remain near the noise floor. New n=16 seeds4/6 wait
30 fresh observations; the other IID cases wait20. This is a fixed sample,
not a population success-rate or Bayes-dominance theorem.

The [component symmetry v3 proposal](theory/proofs/COMPONENT_SYMMETRY_PROPOSAL.md)
now realizes an average over unresolved relative flips on initialized one-hot
queries, using existing native unit/scale slots and component-local products.
Tied counts remain retained. Soft-input and complete-learner counterexamples
prevent promotion to a general quotient. CPU/CUDA matrices at `ad2c350`
each pass six workers and1,127 binary64 phases, with1,127 CUDA phases;
the n=32 reference regression also passes. These are separate extension
checks, not a new full baseline release.

[RN-3 is complete](experiments/component_uncertainty/RESULTS.md) at `a351da9`:
eighteen new workers, ten sealed FP streams, nine installs,7,688 independently
checked CUDA/binary64 phases each,72 new score checks and ten fresh-decision
replays. All eight new IID classes remain unresolved. In the known worlds,
v3 frozen CE is0.592766 in both, matching the strong retained posterior;
the equal-world improvement over v2 is0.371510. Yet deployed mean worsens
from0.563488 to0.626226. One n8,c4 case installs too late to improve any
remaining forecast; the other seals without installation. Retain all outcomes
and old RN-1/RN-2 controls at their original sources; do not rerun them.

The current obstacle is learning from later labels while preserving current
uncertainty. A cross label with zero current gain changes the next exact
conditional prediction from1/2 to41/50 or9/50. Runtime retains that information.
But the emitted graph has identically zero cross-component evidence and
parameter derivatives for every legal weight. Raising learning rate alone
cannot repair its support. Derive an owned reachable learner or construction
strategy that can use the retained labels, with strong adaptive controls at
matched information cuts. The same-cut frozen uncertainty question is closed
in this scope; finite within-component posterior uncertainty and useful
adaptive learning remain open. Do not add free fitted coefficients, semantic
architecture actions, or more static precision/resource cases.

The [balanced v4 readout](theory/proofs/BALANCED_UNCERTAINTY_LEARNERS.md)
now supplies a reachable learning direction: equal positive evidence with
separate initialized coefficients preserves uniform cross predictions and
responds to the next label. Exact checks cover 7,320 initial predictions,
7,072 label-sensitive first updates and 484 coupled scale/slot cases.
Functional CPU/CUDA runs learn either orientation, install continuously
updated learners and preserve unresolved training classes. Missing slots,
quadratic work and the old tight range retain honest refusals. The complete
[CPU](evidence/minimal/FP_BALANCED_UNCERTAINTY_CPU_AUDIT.json) and
[CUDA](evidence/minimal/FP_BALANCED_UNCERTAINTY_CUDA_AUDIT.json) matrices at
`803cdc2` each pass six workers and1,960 binary64 phases; the target matrix
also checks1,960 actual CUDA phases. Default v3 and the frozen baseline keep
their scopes.
[RN-4 is complete](experiments/adaptive_uncertainty/RESULTS.md) at `cffbadc`:
thirty workers, twelve sealed/installed n8 FP streams, eight n16 FP streams
unresolved at their first new prediction, and ten adaptive posterior workers.
The eight failures exceed the fixed131,072-byte CUDA phase evidence frame;
no configuration is raised or tail imputed. Independent analysis checks88
dynamic scores, twelve fresh decisions,6,552 CUDA/binary64 phases per path
in sealed runs, and1,408 posterior GPU forecasts. Failed prefixes carry no
complete independent phase-count claim. All sixteen IID training searches
stay unresolved; only four conditioned searches retain historical bounds.

New n8 two-/four-component candidate CE at rate4 is0.401997/0.488960,
versus adaptive posterior0.334035/0.350041; deployed CE is0.467520/0.569416.
Both registered rates and all failures stay in the evidence. The
[transitive-learning proof](theory/proofs/TRANSITIVE_UNCERTAINTY_LEARNING.md)
shows why nonzero local gradients and linear joint representability can
still miss relations implied by two labels. Native curvature generates that
moment; pure squares have an absorbing-zero counterexample. The mixed
polynomial control is not yet an owned resource-admitted model. Continue
joint-relation model research with a feasible declared execution envelope;
do not rerun these outcomes or add static resource cases.

The [joint polynomial v5 proposal](theory/proofs/JOINT_POLYNOMIAL_PROPOSAL.md)
now emits relative-orientation evidence `a+a^2` through shared slots on
serial native SUM paths. It removes the separate output gate and unnecessary
self-PRODUCTs from the control, while preserving direct zero recovery and
transitive learning. This constructs a new complete learner; it cannot
inherit the older control's state or evidence. Available initializer slots,
literal graph costs and prepaid work still govern the full native search.

Exact checks cover320 models,7,320 predictions,25,752 gradient coordinates,
946 zero recoveries,726 count/slot cases and729 soft-input polynomial values.
Functional CPU and CUDA transitive runs each check542 binary64 phases; the
latter also checks542 actual CUDA phases and installs. The old native1/100
precision budget fails later at cursor57, after an earlier installation;
all256 executed phases, including the rejected prediction, are independently
checked. Positive CUDA fixtures separately declare native/state1/16 and
probability1/100. The tight-range refusal and actual zero recovery remain
controls. The completed source-bound matrices at `9f9fa0b` now cover seven
CPU workers / 2,496 binary64 phases and eight CUDA workers / 2,752 CUDA plus
2,752 binary64 phases. Positive and incomplete-class installations occur at
cursor 51; the old precision control refuses at 57. Compact journals retain
all endpoint statuses and measured maxima. No RN-5 model result or new
complete baseline release is implied.

[RN-5](experiments/joint_uncertainty/PROTOCOL.md) now preregisters 31 new
workers: 22 v5 FP learners at rates 1 and 4, plus nine adaptive posteriors.
The two known diagnostics reuse RN-4's existing posterior and v4 controls;
eight new IID cases use n8/n16, c2 seeds 16/17 and c4 seeds 18/19. A separately
selected wrong-majority tape tests the
[empirical sign obstruction](theory/proofs/EMPIRICAL_SIGN_OBSTRUCTION.md).
Its fixed-state lower bound is distinct from the weaker bound valid across
changing learner states. This is a limitation of one emitted graph, not a
Foundation counterexample or exclusion of future legal constructions.

Before target execution, 1,224 independent scalar/full-graph trajectory
checks pass across reference, binary64 and rounded AMP, together with 64
fixed-state sign controls. Metadata-only preflight reads no new IID labels
and bounds the registered graph output cells. The protocol declares the
larger graph, per-phase evidence, range and numerical instance budgets,
including a bound-6 fresh evidence rule; all failed outcomes must be retained.
Target-model scores remain pending. Do not rerun RN-4's failures.

The initial RN-5 source `e3df252` hit an inherited auditor constant requiring
16MiB instead of its declared 256MiB arena. Both known-A rates have preserved
failed-job records; a known-B/rate1 process was interrupted without a complete
job or score claim. No new IID or stress worker had started. The corrected
auditor compares allocation counters with the actual immutable arena contract;
16MiB and 256MiB functional CUDA controls each replay 16 phases. The amended
runner links all three earlier attempts and keeps every model/data/resource
parameter fixed when executing the same 31-worker matrix. Results remain
pending; this repairs evidence checking, not a model or budget outcome.

[RN-5 is complete](experiments/joint_uncertainty/RESULTS.md) at execution
source `38b27b3`, retaining protocol origin `e3df252` and all 31 registered
attempts. Fourteen n8 FP streams seal, nine install, and nine new adaptive
posterior workers complete. Four n16/c2 FP workers fail in the final auditor's
arena snapshot; all four n16/c4 FP workers time out at two hours. These eight
attempts supply no model score or complete trajectory-audit claim. The largest
completed job counter is17,180,921,856 bytes, slightly above the nominal16GiB
cap; the c4 timeout counters stay below it. Original limits remain unchanged.

Independent analysis in the original execution checkout verifies7,564 CUDA
and7,564 binary64 phases,92 descriptive scores, fourteen fresh decisions and
1,344 new posterior GPU forecasts. The n8/c2 candidate unseen means are
0.390115/0.443602 at rates1/4, versus posterior0.338493; n8/c4 means are
0.416883/0.433386 versus0.365447. Deployed means are0.588589/0.610303 and
0.611359/0.621001. Both selected wrong-sign stress candidates seal without
installation, with candidate CE0.551847/0.522697 versus posterior0.418238;
the deployed stream stays uniform. The stress tape is not an IID sample.
Four conditioned searches retain only historical fixed-state reference-class
bounds; the ten other sealed searches remain UNRESOLVED. The final journal,
source-bound post-analysis and inspected plot retain all unavailable scores.

The earlier auditor failures and the separately retained
[unreported interruption](evidence/minimal/FP_JOINT_UNCERTAINTY_INTERRUPTION.json)
remain distinct from this31-attempt matrix. No cause or completed job counters
are invented for the interruption. Its original-source resume and subsequent
timeout remain documented in research history.

All main RN-5 workers and parent11020 are terminal. After its final source
guard and complete independent analysis passed, main fast-forwarded through
33a12e4, retaining every final journal row, plot and research commit from
`research/joint-learner-geometry`. Main is now the active research checkout.
The separate likelihood matrix still requires its immutable90f3883 execution
checkout; do not patch or restart that run.

RN-5 post-analysis was then reproduced from a fresh detached38b27b3 checkout
at `F:\FP-rn5-audit`, adding only the analyzer and final journal from33a12e4.
Every summary field and per-worker detail matches the original analysis.
The [results](experiments/joint_uncertainty/RESULTS.md) include reproducible
commands. This is passive analysis, not another model run; its source check
should continue to reject changed execution dependencies.

The [scale-dynamics proof](theory/proofs/JOINT_LEARNER_SCALE_DYNAMICS.md) adds
a model-level explanation, without changing Foundation or the experiment.
An exact mass-drift identity covers all orientation counts. For K8, projected
unrounded SGD strictly increases the cross scale for every positive rate;
other family sizes have decreasing examples. Equal one-hot forecasts under
rescaling still give different next SGD predictions. Synthetic audits verify
1,008 identities, 8,352 gradient coordinates and 384 projection controls.
Grid16/AMP monotonicity is not inferred. The independent analysis records
rounded-scale observations separately from the theorem. Research commits
through33a12e4 are integrated into main after all RN-5 workers terminated
and the complete original-source analysis passed. Continue research in main;
the historical research checkout is no longer the active execution boundary.
The same proof now characterizes the cross-query real-parameter mixture
relaxation and excludes suboptimal first-order stationary points there.
Another 336 exact direction checks and a pure-square zero-gradient
counterexample support the argument. This does not relax the actual
Gamma/profile/grid/resource decision class or establish SGD convergence.
An explicit residual-sign mixture now attains every blockwise optimum in the
fixed-state uniform-risk bound. Exact checks cover 1,550 mixtures and 16,600
ordered cross blocks. The selected diagnostic's relaxed optimum is therefore
the stated entropy expression, approximately 0.5069369136. It is neither a
legal-state certificate nor a bound on the stream of changing forecasts.

The [factor-dynamics law](theory/proofs/JOINT_FACTOR_DYNAMICS.md) now identifies
the unrounded update as a pairwise factor, including cycles/repeated edges.
Its forest specialization quantifies dilution by unrelated components and
proves that two unprojected steps cannot calibrate all three noise-1/10
posterior pair forecasts merely by choosing different rates. Projection can
create a four-component interaction, and equal current forecasts plus scale
still permit different next predictions. Exact checks cover 1,932 forest
states and 1,024 general factor updates. These are model-level diagnostics,
not RN-5 target scores, new resource cases or changes to the live experiment.

The [native recurrent posterior control](theory/proofs/NATIVE_RECURRENT_POSTERIOR.md)
now realizes a finite-window Bayes update through the existing positive
delayed bodies and causal target atoms, with Gamma=(1,8) and learning rate0.
A staged excess representation has a valid finite invariant and preserves
the correct noisy readout on diagonals. Exact checks cover3,487 full-prefix,
264 suffix and969 intermediate forecasts. Actual owned CPU execution seals
four ordinary events with13 independent binary64 phases;192 rounded
interpreter forecasts also pass. This is an initially registered model with
known prior/noise, not discovered structure or a CUDA result. Its literal
range grows with the declared window; Runtime still retains all history.
The [source-bound CPU evidence](evidence/minimal/FP_NATIVE_RECURRENT_POSTERIOR_CPU_AUDIT.json)
at `a487718` now completes both fixed512MiB jobs:26 binary64 phases total,
maximum completed job commitment44,797,952 bytes, no timeout. Both ordinary
streams seal; the H2 control explicitly differs from the full-history
posterior after eviction.
The [actual AMP journal](evidence/minimal/FP_NATIVE_RECURRENT_POSTERIOR_CUDA_AUDIT.json)
at `75de898` now completes49 jobs:the48 four-label interpreter streams plus
that suffix control. All seal under their fixed4GiB host,16/32MiB arena/
reservation and1/100 tolerances, with637 independent CUDA/binary64 phases
per path and196 exact stored-mass posterior forecasts. Maximum job
commitment is2,303,946,752 bytes; raw division error is at most1/41943040.
Process-local allocator history and the shared-board capacity envelope
permit these short controls beside RN-5, with no exclusive GPU or timing claim.
Initial source `e92762c` incorrectly attached an unused install contract;
all49 jobs were rejected before CUDA allocation and are retained in the
separate registration-failure journal. The corrected empty policy registers
no install contract and keeps the same49 cases and all budgets/tolerances.
This closes the initial finite model's owned AMP question. The new
[causal proposal](theory/proofs/CAUSAL_RELATION_PROPOSAL.md) now derives a
native base-one window model from ordinary observations and actual initializer
slots. Runtime constructs it through its registered profile, compares its
full endpoint and installs only through actual fresh paired evidence. One
functional CPU stream seals with268 binary64 phases and installs at cursor39;
it leaves the full historical class unresolved. Four source-bound
CPU/RTX3090 jobs now complete at6acbd85: all seal and install, with1,090
binary64 phases,545 actual CUDA phases and288 independently checked fresh
scores/wealth steps. Native/normalizer error3 is retained separately from
probability error; actual masters and delays remain exact. Next study useful
adaptation under matched information and resources. Do not equate this finite known-prior proposal heuristic with
identified noise or affordable whole-history inference.
The first four jobs at35ba35b failed in report generation because a Git
subprocess violated their one-active-process fence. Their original failure
journal is retained; the wrapper now relies on the parent's source checks.
The corrected four-job matrix keeps every case, resource and tolerance,
and its complete evidence links those four failures.
Read the [selection-objective proof](theory/proofs/RECURRENT_SELECTION_OBJECTIVE.md)
before treating recurrent training fit as generative evidence. Actual H2
endpoints give73/100 retrospective likelihood versus41/100 causal likelihood
on two repeated labels. With common Gamma=(1,0,2,8), three noise models have
identical1/4 causal evidence on two forest edges but endpoint scores1/4,
5/16 and41/100. A one-observation forest cannot identify their noise rates;
a later cycle has different predictions. Exact checks cover892 forest and32
triangle likelihoods; four functional CPU streams add28 binary64 phases.
The existing empirical class objective stays unchanged and remains distinct
from causal guidance for a proposer and actual fresh evidence.

The next [native model representation](theory/proofs/POSITIVE_CONSTRAINT_CONTRACTION.md)
contracts positive signed constraints rather than storing one weight per latent
world. At Gamma1/8, integer coefficients realize prior-averaged base-one masses
with range10*9^H; H<=3 native forward values are half-exact on the categorical
domain. Exact checks cover18,540 rank instances and5,944 forecasts, with explicit
gradient/soft-input counterexamples to broader equivalence. It is expensive:
n2,H3 uses1771 nodes versus102 for the full-world baseline, and both share all
2340 causal source-domain rows. Run `constraint_contraction.py --algebra` and
`--boundaries` under `experiments/joint_uncertainty`. The source-bound two-job
`constraint_cuda.py` comparison completes at65c6472: both seal, with56 independent
CUDA/binary64 phases each. Native errors are0/1 and normalizer errors0/2;
packed peaks are570,850,422/90,834,766 bytes. Preserve its identical
resource/interface grants and original outcomes. This is an initial-model
control, not v7, a learned prior/noise result or an installation certificate.
An adversarial comparator improvement is now essential: the centered variable
v=(w-1)/K has positive update v+I*(8v+8/K). For K<=8 its integer coefficients
use the same Gamma, giving identical averaged masses and half-exact H3 values
with only102 nodes/174 edges at n2. `centered_contraction.py --algebra` passes
2,965 exact forecasts and53 formal/rounded checks each. The generic contraction
is therefore not the useful small-n winner. Retain the original two completed
jobs. `centered_cuda.py` registers one new matched job for this stronger control,
linking those outcomes without rerunning them. It now completes at716d279:
28 independent CUDA/binary64 phases each, zero native/normalizer error and
90,865,346 packed bytes. Its completed job peak is2,553,532,416 bytes within
the same16GiB cap. All three paths total84 CUDA/binary64 phases each;
`analyze_contraction.py` checks their27 retained forecasts, source dependencies,
matched registrations and resource/error maxima without launching another job.
Prefer the centered graph in this n2,H3 scope. The general contraction remains
a representation bound with large window/domain costs, not an affordable
large-n model result. All three new jobs and both drivers are terminal.
Their results and completed RN-5 retain their original execution sources.

The [whole-history predictive-state proof](theory/proofs/WHOLE_HISTORY_PREDICTIVE_STATE.md)
now identifies what the known-noise posterior must remember: signed nonloop
edge counts are sufficient and minimal. Complete exact pair forecasts encode
these counts within the pairwise Ising family, but their rounded values can
erase a later useful distinction. At cut T, all N_m(T) integer count classes
remain distinguishable even with uniform future probability error below4/25
at noise1/10. The proof gives a finite common suffix exposing any two classes;
4,216 exhaustive state-pair checks include cyclic and frustrated histories.
Another6,175 ordered histories,846 exact forecast tables and the unknown-noise
counterexample pass. Run `experiments/joint_uncertainty/predictive_counts.py`.
This is an information law, not a native counter model, cheap inference result
or Runtime deletion permission. Next attack affordable inference and reachable
adaptation, or a stated expected-risk approximation; increasing window size
and keeping only rounded confidence do not settle this question.

The [simplex gradient derivation](theory/proofs/SIMPLEX_GRADIENT_POSTERIOR.md)
now provides a concrete learner candidate: on a positive affine block with
equal expert normalizers, the unit update w_j*(1-g_j+SUM_i w_i*g_i) from the
actual native CE gradient is exactly Bayesian. It commutes with splitting
identical fixed experts; that property forces its preconditioner within the
stated diagonal class. The known-noise relation graph has14/25/42 nodes at
n2/3/4 and whole-history normalizer10, with no lag-domain growth. Exact
audits check5,955 native forecasts,9,183 affine steps and378 refinement cases,
plus an80-event agreement/reversal trace. Read the unequal-normalizer negative
update and the distinction from the current-output Fisher metric before
generalizing it. This changes U and the actual uniform1/K initialization.
The [scoped Runtime extension](theory/proofs/SIMPLEX_RUNTIME_CONTRACT.md) now
registers the normalized simplex update and an owned v7 native constructor.
All ambient gradients remain retained, fixed slots remain explicit, and
negative updates are refused. Larger update units give a mean of individual
posterior steps at frozen weights, not sequential Bayesian conditioning.
The exact audit checks603 commits and a20-member class that retains15
initializer failures as unresolved. The [eight-job source-bound matrix](evidence/minimal/FP_SIMPLEX_LEARNER_AUDIT.json)
at b34bf7b is complete: all eight jobs execute and seal, with1,208 binary64
phases,604 CUDA phases,200 posterior forecasts and160 fresh-score checks.
All four profiled CPU/CUDA streams install at cursor22 while their historical
classes remain unresolved. Largest packed/job peaks are77,265,284 and
2,417,373,184 bytes within the fixed caps.
Run its source-dependent audits from the research worktree. This is a
different lineage and a known-model control; matched model usefulness and
long-history AMP reliability remain research questions. The first dynamic
precision boundary is now [proved and observed](theory/proofs/SIMPLEX_REVERSAL.md):
under50 agreeing and50 contrary labels, the existing FP32 master loses a
world weight at48. At source619e3cf the CPU control seals100 observations
and returns to the uniform posterior; RTX3090 halts after97 observed labels,
before revealing the next target. All293 CUDA raw phases, including the
refused prediction, and594 binary64 phases across both jobs are independently
checked. The failure has native/probability errors4/365 and2/1825 within
the original resource caps. A bounded normalizer and a currently small
parameter error do not preserve every legal future. Raw history and the
complete reference state remain owned; this is not a Foundation loophole.
The next research question concerns a declared representation that preserves
future evidence, or an explicit expected-risk approximation claim. Enlarging
a tolerance cannot recover an absorbed posterior coordinate.

The [count encoding proof](theory/proofs/COUNT_LEARNER_ENCODING.md) now covers
every reference learner field and native forward-cache value for the actual
unit-rate/unit-event relation model. Counts of committed events, the actual
uncommitted query/label and both clocks reconstruct theta and the full
gradient, including the fixed slot. Exact checks cover1,146 caches and each
observed/committed complete state, repeated profiles and a late-birth reversal.
Rate1/2 and two-event units have within-contract order counterexamples, so
the representation cannot be selected by optimizer name alone. This is an
encoding theorem; by itself it changes no Runtime/AMP backend. A physical
decoder needs owned storage, actual event binding and paid arithmetic.

The [likelihood information law](theory/proofs/LIKELIHOOD_INFORMATION_LAW.md)
now supplies a general exact exponent: Theta((T+1)^rho) predictive classes
at a known T, using the rational affine rank of likelihood-ratio valuation
increments. Two worlds can have rho=2. Exact checks cover 2,339 complete
native event phases, 2,408 histograms and 5,535 projective bounds. The
important approximation boundary is also closed: a length-19 pair stays
within 0.002 under every common future, yet any pure deterministic encoding
merging it and commuting with reference updates must merge a cut-76 pair
whose forecast gap exceeds 0.002. For reversible two-world banks this
argument gives the exact information lower bound whenever uniform error
is below half the expert contrast. History-dependent lifts and bounded
claims need separate arguments. Do not install an approximate pair cover
as a causal state quotient.
The existing AMP reversal failure and completed RN-5 retain their original
contracts and results. Their subsequent research is now integrated into main.

The subsequent [owned likelihood lowering](theory/proofs/LIKELIHOOD_RUNTIME_CONTRACT.md)
is implemented on that research branch. It derives a commensurate finite
affine bank from actual Program/Gamma/U/full source-domain inputs, retains
integer coordinates and pending events, and decodes weights with actual
positive binary32 GPU arithmetic. Development checks seal the 100-event
reversal and the n3 two-pass profile/fresh-install path at the original
tolerances. The fixed-slot gradient and all native cache fields remain
checked. The fresh score reader now retains the tagged full forecast.
Counter overflow and source/work/scratch guards remain explicit refusals.
All nine source-bound jobs now execute at08fa7bc: two sealed streams, six
preserved refusals and complete20-member grammar handling with15 unresolved
members and no class proof. Independent replay checks994/3 checked/refused
CUDA phases,997 binary64 phases,326 GPU commit tapes and40 fresh scores.
The reversed weight returns from zero to a positive subnormal at53 and to
1/2 at100; the two-pass candidate installs at22. Largest job commitment is
2,371,022,848 bytes under4GiB. The [minimal report](evidence/minimal/FP_LIKELIHOOD_LOWERING_AUDIT.json)
binds every outcome to its completed job. This closes the paid finite codec
demonstration for the stated subclass. Continue to useful-scale model and
resource tests; do not infer uniform unlimited accuracy or whole-Compiler
compression. The exact U, ERC-1 and original RN-5 outcomes are unchanged.
The new code is integrated into main after RN-5 completion.

The [sparse affine analyzer](theory/proofs/SPARSE_LIKELIHOOD_ANALYSIS.md) now
preserves the dense result while reducing n6 derivation operations from
2,536,316 to304,892. Its independent verifier proves positive polynomial
degree and uses native mass derivatives; vertex agreement alone does not
prove a legal unit update. All28,656 small-grammar cases agree, including
21,204 independent bank/vertex checks. Two further bounded development jobs
pass587 CUDA/binary64 phases each, with profile install22 and reversal
recovery53. Conservative budgets and the nine old source-bound jobs retain
their original scope. This code also stays on the research branch.

The [forecast decoding theorem](theory/proofs/FORECAST_DECODING_COMPLEXITY.md)
now proves that compact sufficient counts do not imply cheap readout. A
decoder that resolves every legal history with noisy-forecast error below
2/5 in polynomial time in n+T would solve unweighted MAX CUT in polynomial
time. At2/5, constant1/2 is valid; exact streaming enumeration uses exponential
time and polynomial workspace. The reduction uses the same native unit U,
fair prior and positive noise1/10 likelihoods. Exact checks cover all1,098
graphs at n2..5,32,089 permitted adaptive states and183 native units. This
does not establish IID hardness or explain RN-5 timeouts. Continue useful
model-scale tests and structured solver work with honest unresolved budgets;
the theory supplies no free forecast or new target/fresh-evidence authority.

The [n8 likelihood matrix](experiments/joint_uncertainty/LIKELIHOOD_MODEL_PROTOCOL.md)
stops after its first90f3883 attempt. Worker2720 exits1 in the inherited
100-digit Decimal gain auditor, with no timeout and peak job commitment
15,474,765,824 bytes. Parent15872 is terminal; the other three cases were
not attempted. The [original failure](evidence/minimal/FP_LIKELIHOOD_MODEL_AUDITOR_FAILURE.json)
is retained verbatim. It supplies no model score, install, seal or complete
independent phase count. The original execution checkout remains historical.

The [exact replacement](theory/proofs/EXACT_LOG_ENCLOSURE_AUDIT.md) proves
scalar log-interval containment using an independent rational calculation.
It rejects a forged zero-width interval accepted by the old check and accepts
the correct near-neutral reference interval that the old check rejected.
All1,572 valid scalar cases pass; accepted cases need at most32 terms and
8,103-bit operands. Unresolved overlap/bit limits never count as a pass.
Reference, paired CPU persistence and full owned-policy regressions pass.
A bounded development
CUDA profile/install seals at cursor22 with286 CUDA/binary64 phases each
and40 fresh-score checks. This is no n8 result or new complete release.

The corrected four-case protocol keeps every model/resource registration
field identical to the failed attempt, which the runner checks before launch.
It retains the same baselines, Gamma/U, graph, data, profile, bound6/bet3/4,
alpha, tolerances,16GiB/two hours,8GiB packed and4MiB frames. The corrected
matrix starts at immutable86083a0 in `F:\FP-likelihood-model-v2-run` on
2026-09-14 at07:06:48 UTC, parent23668 and first worker16644. Its initial
journal has zero completed outcomes and links the original failed attempt.
Keep that checkout's HEAD/dependencies fixed throughout; main may advance.
Do not resume90f3883 as though its auditor succeeded or fill its unavailable
model results.

The [independent result reader](experiments/joint_uncertainty/LIKELIHOOD_MODEL_ANALYSIS.md)
now verifies the complete matrix. Its immutable analysis checkout at
`F:\FP-likelihood-model-audit` stays at b85b39d, with imported execution
dependencies matching86083a0. Run against the final canonical journal without
`--partial`. All24 model scores, four paired decisions and sixteen retained
control scores pass; no baseline is rerun. A one-identity summary without
its path label still receives unresolved fresh reconstruction.

[All four corrected n8 cases are complete](experiments/joint_uncertainty/LIKELIHOOD_MODEL_RESULTS.md).
At86083a0 they seal and install at114/90/72/72, after54/30/32/32 fresh events.
All256 exact reference forecasts equal the adaptive posterior. The workers
independently check2,752 CUDA and2,752 binary64 phases,912 commit tapes and
296 fresh scores. Candidate/deployed mean unseen CE is0.338495/0.580218 for
c2 and0.365450/0.509115 for c4. All four crossings and24 risk envelopes agree
with the prior conditional prediction. Every full class remains UNRESOLVED.
Maximum job commitment15,478,538,240 bytes fits16GiB; all four finish within
the unchanged two-hour watchdog. The canonical journal and analysis are
terminal, registration and prior prefix verified. Parent23668 and all four
workers are terminal; do not restart them. Preserve the original90f3883
failure. These retained tapes establish no new IID success rate, isolated
mechanism effect, n16 recovery or full Runtime release.

The deployment obstacle now has an [owned pre-context mass-bound refinement](theory/proofs/CURRENT_MASS_PERSISTENCE_BOUND.md).
It derives one common probability-ratio bound from the existing complete
native mass enclosures, including mathematical forecasts on failing next
attempts. The old class-cap proof remains the cheap first route; a tighter
current-state proof is marked in the paid identity and refreshed after each
active event. If it fails, that identity stops before next ingress. No query-
conditional bet or changed null is introduced. The exact2025-box audit checks
181,440 corner ratios. Bounded CPU/CUDA n2 profiles both install at8 after
six fresh labels, versus22 in retained B6 fixtures; each checks280 binary64
phases and the CUDA job280 device phases. Reference, paired CPU and CUDA
persistence regressions pass. This is development reachability, not a new n8
outcome. The [next deployment protocol](experiments/joint_uncertainty/LIKELIHOOD_DEPLOYMENT_PROTOCOL.md)
now fixes the same four cases at bound13/8 and coefficient6/13, keeping the
learner, tapes, alpha, resource caps and all prior controls. The matrix starts
at immutable8ccacc0 in `F:\FP-likelihood-deployment-run` on2026-09-20 at
15:25:40 UTC, parent14264 and first worker2444. Both are live at launch
verification; the initial canonical journal contains zero completed outcomes.
Keep that execution checkout's HEAD/dependencies fixed. Do not start a second
parent or resume merely because an observation handle is lost. Use its
committed independent reader with `--partial` until the journal is terminal.
The reader checks retained score prefixes and separates numerical crossings,
owned crossings and installation. Two actual reference scenarios include
failed crossing retention; nine forged records are rejected. All24 old model
scores, four decisions and16 strong-control scores pass without rerunning a
baseline. See the [reader audit](evidence/minimal/FP_LIKELIHOOD_DEPLOYMENT_READER_AUDIT.json).

After registration, [exact conditional analysis](theory/proofs/TIGHTER_BOUND_DEPLOYMENT_TRADEOFF.md)
predicts paired crossings119/67/54/50 if the required owned computations and
gates succeed. The first is later than the old114, with more than0.016 worse
unseen deployed CE; the other three are earlier. Its reference wealth falls
to873/32768 before recovering. A native p9/10 witness also disproves transfer
of the old reciprocal-power lemma to6/13 despite faster ideal log growth.
The record contains256 reference forecasts,90 production wealth updates and
1,964 independent exact log checks. This is passive retained-tape analysis,
not a GPU result or reason to change the fixed running procedure.

The [predictable-mixture state proof](theory/proofs/PREDICTABLE_MIXTURE_STATE.md)
investigates adaptation without using any model tape or changing that run.
It expresses the classical arcsine wealth mixture with positive coefficients,
one common pre-context fraction and exact rational readout. Downward
coefficient rounding preserves mean-null validity; H+p fractional bits give
less than2^-p error through horizon H with polynomial scalar resources.
Equal wealth can conceal different future readouts, and low-precision
updates destroy gain-order equivalence.15,625 scalar words,31,248 zero-mean
null checks and160 complete native units pass. The theory alone gives no
GPU result or first-passage dominance.

The [owned mixture extension](theory/proofs/OWNED_MIXTURE_PERSISTENCE.md) now
declares coefficient precision separately from scalar wealth precision and
publishes the complete curve/wealth in the existing persistence identity.
It passes1,215 guarded updates,160 actual fair-label scores, a changing
learner with three-event epochs, failed crossing retention, prepaid work
refusals and a real128-bit exhaustion. The old reference, paired CPU and
kernel audits pass. Actual new-rule paired profile/bridge/install remains
unverified: commit execution dependencies before the bounded development
worker and retain failed attempts. This is no full-release or model result.
The fixed8ccacc0 source and experiment remain unchanged.

Main now uses [prepaid bulk CUDA observation](theory/proofs/CUDA_RAW_READOUT.md).
The device arithmetic and full operation tape stay intact. One retained8C-byte
host workspace copies the phase span and decodes only initialized floating
views, then clears opaque transport bytes. It stays owned even when an
exception traceback retains a CPU alias. The phase fee rises128C to320C:
unencoded simplex commits require six captures, a branch missed by an initial
three-pass allowance. All65,536 half patterns,526 single patterns, failure
ownership and actual six-capture commits pass. Complete Runtime/installation
and bounded likelihood profile regressions pass separately. The measured
8,192-to-one copy reduction is a fixture result; no model speed or n16
recovery is established, and86083a0 did not execute this optimization.

Main now uses [slotted complete arena-region records](theory/proofs/ARENA_REGION_STORAGE.md).
All ten fields and complete snapshots remain. Four512MiB host jobs check
1.5 million rows and show peak reductions12,582,912/25,907,200 bytes at250k/
500k regions. The full CUDA storage and thirteen-case installation audits
pass; a4GiB likelihood profile job seals/installs with286 CUDA and286
binary64 phases,94 commit tapes and40 fresh scores. These are targeted
development regressions, not new model outcomes or a whole-project freeze.
The original n16 failures remain; this change alone does not prove recovery.
The analysis checkout is pinned at b85b39d and the completed matrix at86083a0.
Use the pinned analysis checkout because main's execution dependencies now
differ from that execution source.

The [finite fresh-power result](theory/proofs/LIKELIHOOD_PERSISTENCE_POWER.md)
now accounts for uncertainty learning, AMP error and the existing wealth
floor at the original coefficient1/8. Under the explicit posterior-mixture
alternative, the four training profiles give64-event lower bounds0.892775,
0.892855,0.808954 and0.809044. They concern paired crossing if all required
computations remain available; otherwise only crossing or operational
failure. They do not condition on successful workers, establish actual
installations or use evaluation targets. The exact audit also reaches
absorbing grid16 zero after45 adverse native self-query labels and refutes
the reciprocal claim under a fixed hidden world. Preserve those scope limits.
The statistical composition is closed for this model; use actual execution
to study the remaining resource and deployment outcomes.

The [retained-tape deployment envelope](theory/proofs/LIKELIHOOD_DEPLOYMENT_ENVELOPE.md)
now isolates the delay expected even from posterior-exact learning. Under
successful original fresh/AMP premises the paired crossing cursors are
114-115/90/72/72. The first case leaves9-10 forecasts and incurs at least
0.316620 extra unseen CE over the same candidate solely through waiting.
All46,656 six-event label/perturbation paths and55,986 actual wealth floors
pass the exact tube audit. This analysis explicitly uses retained evaluation
labels; it is not prospective power or installation authority. The completed
matrix now satisfies every crossing/risk envelope. Preserve that distinction
between the conditional theorem and its subsequent empirical verification.

The [radix9 decode theorem](theory/proofs/LIKELIHOOD_DECODE_ERROR.md) now bounds
the existing selected-weight commit for every accepted exponent vector.
Under its RNE32 schedule, error is at most(K-1)u/72+gamma_(K-1)+u+2^-150,
with u=2^-24. At128 worlds this is below7.735e-6, independent of history
length. A finite64-exponent lemma and a proved zero-power tail cover all
counts; exact audit checks12,481 ordered three-weight vectors,520 width/order
controls and143,614 rounded operations against binary64. The largest observed
K128 control error is6.46782e-6. No persistent count is erased. Full native
gradients, evidence, counter/work/storage limits and actual GPU words still
require their existing checks; this creates no complete Runtime certificate.

The [persistence filtration result](theory/proofs/PERSISTENCE_FILTRATION_GEOMETRY.md)
closes an apparent shortcut exposed by RN-5's deployment wait. Under the
registered pre-context mean-null and an unrestricted finite outcome law,
every valid nonnegative one-step factor is dominated by one common linear
bet. At contexts with both gain signs, context-specific linear coefficients
must agree. A native two-context, rate-zero learner has negative mean gain
but context-weighted expected factor1.40498 and positive log drift; its
unrounded false-crossing probability by256 events exceeds705/961. The
current Runtime fixes its rule before ingress and is not vulnerable to that
substitution. Exact audit checks27,725 factor tables,134,450 null-vertex
expectations,256 context-bet tables and384 continuous native units.
A common global bound13/8 follows for the known likelihood bank against
uniform with its0.001 AMP probability relation. The newer owned mass-box
solver separately proves current all-context physical ranges and admits13/8
in development fixtures. The completed n8 matrix keeps bound6; no n8 result
or power ordering for the new coefficient is inferred.

The [normalized likelihood theorem](theory/proofs/NORMALIZED_LIKELIHOOD_CHARACTERIZATION.md)
now characterizes the guarantee over all interior weights: a positive-rate
informative fixed Bayes update requires rate1 and an affine normalized forecast.
Nonlinear native masses can qualify through a common positive factor, but
their full gradients/caches are not equivalent. A second native construction
is Bayesian on every trajectory from fair Gamma because w2=w3 stays invariant,
yet fails normalized affinity off that invariant. Thus the full-simplex
criterion must not be imposed as necessary on every reachable-state codec.
Exact checks cover a10,544-graph grammar,44,880 native units, two nonlinear
160-transition pair audits and36 four-world units. This mathematical result
does not extend the running physical analyzer or the parked static program.

Reopen Foundation only when experiment correctness exposes a semantic loophole.
Slow search, loose bounds, scarce data, resources or uncertain arithmetic
still call for solver work or UNRESOLVED, not another static theory program.

Current executable progress: `src/reference_compiler/fp_reference/runtime.py`
now runs owned native construction, registered profile replay, exact ordinary
learning, causal source reads and registered revealed-data queries through
the same public endpoint. It also executes complete finite ordered native
search and issues explicitly scoped reference comparison proofs.
It now also owns fresh **reference** persistence: admission before context,
sealed paired scores, complete continuous learners, guarded lower wealth
and global alpha that cannot be refunded or inherited after a rebuild.
Do not reconstruct these modules again. Read the source README,
[`REFERENCE_RUNTIME_CONTINUATION.md`](docs/REFERENCE_RUNTIME_CONTINUATION.md),
`scripts/audit_reference_construction.py`, `scripts/audit_reference_events.py`,
`scripts/audit_reference_profiles.py`, `scripts/audit_reference_search.py`
and `scripts/audit_reference_persistence.py`.
Read [`ORDERED_NATIVE_REFERENCE_CLASS.md`](theory/proofs/ORDERED_NATIVE_REFERENCE_CLASS.md)
before interpreting that proof: it optimizes fixed-state empirical CE over
the registered initializer/profile endpoints plus the actual deployed
baseline, not all values or future continuations. Read the current
[47-gate mapping](docs/REFERENCE_RELEASE_GATE_MAP.md) before adding release
requirements. The owned run registration and CPU terminal report execute.
Machine v9 also closes the hierarchical gate through a paid empirical-upper
solver; read [`SATURATED_REFERENCE_CLASS_BOUND.md`](theory/proofs/SATURATED_REFERENCE_CLASS_BOUND.md)
and `scripts/audit_reference_acceleration.py`. From 310 ordinary labels,
the n=32 Runtime proposes native group SUMs/pair PRODUCTs, checks 1,024
contexts, installs at 330 and seals at 622 in an actual 1 GiB job. Its 1,963
binary64 phases have an independent oracle. The entire grammar remains the
decision class, with at least 2^6540 source-only strings; one evaluated
witness attains the categorical empirical upper. `BoundedReferenceProof`
never asserts that all those programs were constructed.

Keep the negative controls: a cheaper zero-PRODUCT graph ties on the train
path; disconnected components have unidentifiable relative flips; even
connected empirical majorities can fit the wrong latent grouping. Train
optimality is neither structural forcing nor fresh evidence. Unchanged
exact theta now preserves its already owned whole-domain range object;
changing theta recomputes/replaces it before release. All learner/optimizer
and delayed-state histories remain distinct and retained. Final reference
and actual target integration now pass; registered device experiments are next.

Read the frozen release scope and evidence:
[`REFERENCE_RELEASE_SCOPE.md`](theory/proofs/REFERENCE_RELEASE_SCOPE.md) and
[`FP_REFERENCE_RELEASE_AUDIT.json`](evidence/minimal/FP_REFERENCE_RELEASE_AUDIT.json).
`scripts/audit_reference_release.py --write` tested committed source `ebe2c4c`
in a clean new clone: all 30 modules import and all 21 complete audit scripts
pass. The independent endpoint model covers 36 runs, 2,665 native members,
2,619 exact scores, 46 range-unresolved members, three halted ordinary
commits and 23,274 independently replayed binary64 phases. Trained 774-member
installation and the owned n=32 chain also pass at that revision.

The freeze declaration changes documentation/evidence only; Runtime and audit
code are identical to the tested revision. It does not claim universal
strategy/value optimality, optional unimplemented interfaces, target AMP or
cross-root error control. Do not add static cases or new reference release
prerequisites merely to defer actual device work.

Actual RTX 3090 primitive execution has now started. Read
[`ACTUAL_CUDA_PRECISION.md`](theory/proofs/ACTUAL_CUDA_PRECISION.md) and run
`scripts/audit_cuda_primitives.py`. Exact positive witnesses distinguish
separate half operations, float32 FMA followed by half storage, and ideal
one-round half FMA. A CPU-scalar divisor changes float32 division to a
reciprocal/multiply path. Autocast alone leaves native elementwise operations
float32. The audit checks all 63,488 finite half roundtrips, 190,464 cast
boundary cases and 11,040 finite arithmetic results. These diagnostics
provide no Runtime authority. Complete owned AMP learners and their
same-path evidence/install chain are integrated in the target release.

The actual continuous learner mechanics are now implemented in
`cuda_learner.py`; read
[`CONTINUOUS_CUDA_LEARNERS.md`](theory/proofs/CONTINUOUS_CUDA_LEARNERS.md).
`scripts/audit_cuda_learner.py` checks 1,306 real device phases against an
independent exact rounded interpreter, including ordinary four-path
comparisons, recurrent profile replay and 24 further native DAGs. It detects
an actual optimizer overflow even when projection hides it in a finite zero.
The CUDA state keeps its own master parameters, half delayed queues and
single gradient accumulator. The mechanical helpers have no signer. Their
subsequent Runtime integration is now executed below; do not rebuild the
learner or reopen the static study to postpone registered experiments.

The actual tensor-storage component now executes all 1,306 phases in one
16 MiB backing arena, with no additional native allocator allocations; read
[`BOUNDED_CUDA_TENSOR_STORAGE.md`](theory/proofs/BOUNDED_CUDA_TENSOR_STORAGE.md).
The 304,064-byte used prefix is not the physical memory charge. Explicit
allocator binding fixes a real hidden-setting counterexample: an apparently
default snapshot can otherwise reserve 40 MiB for a 2 MiB request. Lifetime
allocation counters catch freed escaped temporaries. This is not Runtime or
total-device authority by itself.

The [owned CUDA prefix](theory/proofs/OWNED_CUDA_PREFIX.md) now runs through
`ReferenceCompilerRuntime(..., cuda=CudaPrefixContract(...))`. The immutable
manifest binds its actual build/device, tolerances, tensor arena, phase work
and prepaid evidence capacity. All native/profile phases keep independent
device state, check complete per-event relations and publish reference/device
successors together. Public snapshots expose raw immutable records, no tensor
handles. The audit independently replays 1,024 phases on all 64 short streams,
44 recurrent/profile phases beside CPU binary64, and a 35-member native class.
Actual output/evidence caps, false endpoint execution and unexpected failures
retain targets and old publication. A CUDA evidence budget failure cannot
turn native search into a completed reference class proof.

The next component now also executes: read
[`OWNED_CUDA_PERSISTENCE.md`](theory/proofs/OWNED_CUDA_PERSISTENCE.md).
Current actual master bits and complete queues have owned whole-domain
rounded range bounds. Every actual forecast is independently checked against
the declared mixed arithmetic before acceptance; finite kernel audits are
not promoted to all-input theorems. Reference and CUDA use separate fresh
stored-mass statistics and nonrefundable alpha. All 32 five-label branches
pass 832 independent device-phase checks and 62 conditional wealth tests;
a trained path recomputes its range at six optimizer changes.

Keep the negative witnesses: reference crosses at five while the half path
has zero gain; an exact 3/10 update violates its delayed cap after half
rounding; one ULP of forecast corruption passes the reference tolerance but
fails exact conformance. `PAIRED_CUDA_CROSSED` is owned conditional evidence,
not a complete bridge or install token. Run `scripts/audit_cuda_persistence.py`.

The [owned same-device installation](theory/proofs/OWNED_CUDA_INSTALLATION.md)
now also executes. Register `CudaPrefixContract(install=CudaInstallContract(...))`
and use `install_cuda` with owned proposal/reference/CUDA identities. The
selected continuous learner keeps the original CUDA objects and extents;
the full arena already belongs to both resource roles. Paid readback checks
establish initialized ownership before numeric access, complete state and
quiescence before one complete root publication. Old searches and persistence
lose authority without losing history or refunding alpha.

`scripts/audit_cuda_installation.py` passes complete classes of 35, 774 and
124 members, with 151, 870 and 240 independent CUDA/CPU phase checks. The
larger class installs nonzero trained state; the recurrent class keeps its
full queues. Two further installations at 22 and 38 retain both generations
and consume fresh alpha. Actual preparation caps, late failure/retry, pending
work and state/extent corruption have negative controls.

CPU installation and its owned run policy still refuse a CUDA root; the
registered device transition has its own precise scope. Do not rebuild
range/persistence/installation or resume static cases to defer experiments.
The complete scoped AMP release now passes as recorded above.

The [device-resource observation audit](theory/proofs/CUDA_RESOURCE_OBSERVABILITY.md)
now has a concrete negative witness: native arena snapshots remain identical
before/during/after a direct CUDA 32 MiB allocation, write and free. That is
an explicit foreign call, not a legal Runtime action or a failure of the
scoped arena theorem. Native lifetime counters cannot alone certify broader
allocation history. Also distinguish the existing CUDA build tag 13.2 from
the actual Windows runtime query 13040 (13.4). Resource/run work must bind
that distinction and justify coverage or a conservative upper;
WDDM process-memory N/A and DXGI budget hints do not supply a hard peak cap.
Run `scripts/audit_cuda_external_allocations.py` for the minimal witness.

The [whole-board resource binding](theory/proofs/WHOLE_BOARD_CUDA_RESOURCES.md)
now supplies that upper for the physical framebuffer coordinate. Every CUDA
root binds the actual runtime, driver API and display-driver version; CUDA
ordinal/PCI bus/UUID identify the board whose native capacity is observed.
It charges the entire 24 GiB to deployment and compiler, once globally,
before allocating its tensor arena. This covers physical residency uniformly,
including the invisible foreign allocation, without claiming measured usage,
exclusive availability or cumulative allocation volume. Native tensor and
host private-commit resources retain their separate measures.

`scripts/audit_cuda_device.py` checks actual admission, unequal role budgets,
restoration after native failures and the diagnostic failure boundary. A
worker fenced before execution in a 4 GiB Windows job also completes the
35-member selection, fresh crossings, CUDA install and later continuation;
151 device phases have an independent exact rounded replay. Installation
retains the original device binding. Do not rebuild these resource components
or reopen static cases.

The [owned CUDA policy and finite run](theory/proofs/OWNED_CUDA_POLICY_RUN.md)
now compose those components. `CudaCompilerPolicy` accepts only immutable
native-search stages and reference/CUDA evidence rules; Runtime owns all
Compiler controls. It requires the registered CUDA prefix and live host
binding. Its same deterministic strategy publishes a completed policy stage
inside the resident installation, then prepares and verifies the full CUDA
frame before publishing `SEALED_CUDA_STREAM` at the registered horizon.
Prepared report bytes alone cannot establish a completed run.

The actual two-stage path installs at 22 and 38 and seals at 60, with 456
independent CUDA and CPU phase checks. A 40-event schedule correctly refuses
the second 30-epoch admission. Trained/recurrent/short-stream and failure
controls are in `scripts/audit_cuda_policy_run.py`. Stream completion reports
unfinished stages as unresolved and grants no future authority or current
target optimum.

The [existing hierarchy now also executes on actual AMP](theory/proofs/OWNED_CUDA_HIERARCHY.md).
At n=32 it installs at 330, seals at 622 and passes 1,963 independent CUDA
and binary64 phases. It retains the same 74-node native witness, broad class
and historical empirical-upper scope. Peak packed payload is 313,552,643
bytes; the completed job peaks at 3,905,241,088 bytes under its 4 GiB cap.
The actual smaller SUM-only learner preserves its training prediction-word
tie. Both disconnected worlds install despite opposite unseen relations;
misleading connected majorities end unresolved without install. All five
target cases pass. The complete integration also passes; proceed with
registered RTX 3090 resource and model experiments with strong
baselines. Do not treat native training optimality or fresh installation
as structural forcing or complete population identification.
The complete integration command
`python -B scripts/audit_cuda_release.py --write` passed at `5e55eb4`: all
21 CPU plus 10 CUDA batteries from a fresh clone, 38 imported submodules,
and the same actual device identity throughout the target checks. The
[integrated result](evidence/minimal/FP_CUDA_RELEASE_AUDIT.json) now closes
the [scoped target release](theory/proofs/CUDA_RELEASE_SCOPE.md). Its n=32
job peak is 3,905,482,752 bytes under 4 GiB. Preserve the tested source ID;
this declaration changes only documentation/evidence, not implementation.

The same endpoint now also executes a registered **CPU binary64** learner
beside each exact learner, throughout initialization, profile, prediction,
observe and commit. `OnlineContract.float64` fixes tolerances and the scalar
backend. Raw encodings, full delayed queues and gradient accumulators remain
owned state; no trained endpoint is replaced by a cast of the exact path.
Read [`OWNED_FLOAT64_PREFIX.md`](theory/proofs/OWNED_FLOAT64_PREFIX.md),
`scripts/audit_binary_arithmetic.py` and `scripts/audit_float64_runtime.py`.
This certifies numerical relations of executed finite CPU prefixes only.
It does not authorize future error bounds, floating whole-domain feasibility,
AMP persistence, installation or target-device execution.

The next obligation now has its own executed CPU implementation:
[`PAIRED_CPU_PERSISTENCE.md`](theory/proofs/PAIRED_CPU_PERSISTENCE.md).
Positive rounded forward bounds establish the current binary64 whole-domain
range/invariant before fresh evidence; optimizer changes require renewed
bounds. Reference and binary64 stored-mass CE use separate same-path scores,
wealth and nonrefundable alpha on four continuous learners. The paired
result reads owned identities with matching starts and schedules. An exact
reference crossing at event five while finite gain stays identically zero
demonstrates why numerical closeness cannot transfer statistical evidence.
Run `scripts/audit_paired_cpu_persistence.py`. `PAIRED_CPU_CROSSED` is scoped
CPU evidence; it supplies one premise for the separately executed CPU
installation below, with actual target AMP still open.

The endpoint now also executes `install_cpu` under immutable
`OnlineContract.cpu_install=CpuInstallContract(...)`. Read
[`OWNED_CPU_INSTALLATION.md`](theory/proofs/OWNED_CPU_INSTALLATION.md).
It combines historical owned class selection with current dual persistence
and state relations, then publishes one complete serialized CPython root
and actual buffer-lease transfer. All learners retain their exact states
and buffer identities at the same cursor. The old deployment becomes a
shadow; paused searches close with frontier/history retained, and live
persistence authority ends without wealth rebasing or alpha refunds.

The historical proposal proof stays rejected as a current optimum token.
Failed preparation preserves the old learners/evidence/frontier while
retaining attempted IDs, actual work and peak history. An audit-discovered
retry collision is fixed by attempt-specific physical metadata identities.
`scripts/audit_cpu_installation.py` checks 2,016 lease cases and complete
35-/774-member native-class chains through fresh learning, installation and
ordinary continuation. The 774-member case installs actually trained nonzero
parameters. This closes the declared serialized CPU transition, not full
host/device accounting, concurrent/crash-safe publication, target AMP or
`CERTIFIED_COMPLETE`. Both the integrated Reference/CPU prerequisite and
the subsequent registered target AMP release are now frozen.
The same audit also executes two successive compilation/evidence/install
cycles in one Runtime. New baselines and fresh identities work, old
authority stays closed, and the global alpha cap still blocks later use.

The current physical frontier is now sharper. At `8880371`, repeated unfunded
construction requests could grow IDs/owners/failure history with unchanged
work and packed payload. The control rule introduced in machine v2 pays one fixed
control admission unit before any public Compiler mutation. Unfunded
requests leave owned state and current proof revisions unchanged; admitted
failures keep their costs/history. Read
[`OWNED_CONTROL_ADMISSION.md`](theory/proofs/OWNED_CONTROL_ADMISSION.md)
and run `scripts/audit_control_admission.py` (11 endpoints and 96 finite
command trees). Existing construction/event/profile/search/persistence/CPU
installation audits have been rerun against this machine revision.

The follow-up source-box witness at `5055f3e` is now historical: `1/2^m`
could enter halted pending state before its integer guard with no payload
debit. Machine v3 replaces raw value input with mandatory prepaid exact
byte ingress. `DataContract.ingress` fixes a window and chunk size;
`begin_context` reserves storage, fixed terminal status and work before
the first byte, `receive_context` fills only the offered extent, and
`finish_context` guards integer lengths before materialization. The
one-chunk `predict_next` port accepts encoded bytes only. All received
prefixes survive failure, while an unread producer suffix never enters
Runtime. Learner and persistence IDs seal before receiving starts.

Read [`OWNED_CONTEXT_INGRESS.md`](theory/proofs/OWNED_CONTEXT_INGRESS.md)
and run `scripts/audit_context_ingress.py`. Its 208 exhaustive chunkings
give identical recorded states at equal prefixes; the historical numeric
witnesses now occupy paid windows and return UNRESOLVED without oversized
pending rationals. Existing learning/profile/search, four-learner evidence
and two-cycle CPU installation all use this same input path.

The latest encoding audit then found a correctness failure beyond costs.
At `532d713`, distinct legal source names (one astral character versus two
explicit surrogate code units) had identical JSON/hash encodings. Building
a candidate could overwrite the deployed program registry entry and change
its next probability from 2/3 to 1/2 without installation. Machine v4 now
uses streaming UTF-8/surrogatepass encoding and checks complete Program
equality before reusing an owned address. A collision returns UNRESOLVED.
The source class is preserved; no Foundation primitive is changed.

The same encoder now computes exact extents before output materialization.
`realize` returns a passive plan; Runtime admits its complete allocation
batch before writing to paid buffers. Identity hashing no longer expands
a duplicate tagged tree. A fixed 8 KiB payload-cap audit saw roughly 62 MB
of newly traced old Python allocations before refusal at 100,000 repeated
edges; the revised trace is roughly 0.134 MB. This is a workspace diagnosis,
not a total-host cap. Read [`OWNED_ENCODING.md`](theory/proofs/OWNED_ENCODING.md)
and run `scripts/audit_owned_encoding.py`; it includes the historical actual
Runtime witness, all BMP code points and independent typed-byte checks.

Machine v5 adds one terminal boundary for actual host allocation failure.
The original `dfa1583` Runtime, under a result-allocation fault, freed a new
candidate's learner buffers but still used that candidate in its next public
prediction. All public continuation/proof/persistence/install ports now close
on MemoryError; a precreated marker uses existing state slots, without
allocating cleanup/history or refunding alpha/work. Read
[`HOST_ALLOCATION_FAILURE.md`](theory/proofs/HOST_ALLOCATION_FAILURE.md).
Its audit also executes an unmodified 128 MiB ingress-window request inside
a real 64 MiB Windows job: actual allocation refusal halts before input,
while paid work survives. This is job commitment accounting for the audit
child, not total host memory or a production ERC-1 registration.

Machine v6 now binds an immutable `HostResourceContract` to the actual
executing Runtime process. Deployment and compiler share its whole private
commitment arena: both roles pay the full measure, once globally, with a
kernel fence at `min(global, deployment, compiler caps)`. Runtime queries its
own live Windows job/process; supplied counter records cannot bind it.
This covers Python metadata, temporary copies and arithmetic scratch within
that declared private-commitment scope. Whole-process lifetime peak and CPU
history are never rebased at Runtime creation. `host=None` remains explicitly
partial, with a different chi and no host observation/claim.

Read [`BOUND_HOST_RUNTIME.md`](theory/proofs/BOUND_HOST_RUNTIME.md) and run
`scripts/audit_bound_host_runtime.py`. An actual late-fence witness retains
about 103 MiB lifetime commitment while a new 64 MiB job reports only about
23 MiB; the Runtime rejects it. The same audit completes the 35-program
search, four-path persistence, CPU install and continuation inside one
64 MiB process. Resource-read failure closes authority; later diagnostic
failure cannot rewrite its first host halt cause. A worker that writes a
completed-looking result and then exits unsuccessfully is not accepted.

The next obligations are complete ERC-1 run registration, production
supervision/publication, other resource coordinates and explicit release-gate
mapping. A claim spanning multiple Runtime roots additionally needs its
family error/resource accounting. Process commitment
is not total-machine/RSS/shared-platform/device accounting; CPU observations
are not a CPU-time hard cap. External supervision cannot own FP policy for
free. No Foundation change, static expansion or Runtime freeze follows;
actual AMP correctness still precedes RTX 3090 science.

Machine v7 now also owns an executable Compiler strategy. Under
`policy=CompilerPolicy(...)`, external calls supply only context/target
events and read passive snapshots. Runtime itself drives registered full
native-class searches, separate reference/binary64 evidence admissions and
installation at complete optimizer boundaries. Policy position, owned IDs,
failed prefixes and packed buffers are part of Omega; all 17 other current
public control/authority methods are closed to the caller. The completed
policy record and learner publish in the same CPU root/lease transaction.

Read [`OWNED_COMPILER_POLICY.md`](theory/proofs/OWNED_COMPILER_POLICY.md) and
run `scripts/audit_owned_compiler_policy.py`. It executes two successive
35-program searches/installs at cursors 22/38, the trained 774-program case,
and all 64 six-label streams (32 baseline selections, 30 unresolved, two
installs). The two-install path also runs inside a 64 MiB process. Partial
admission, policy-storage failure and nested native-premise loss retain their
actual targets, work and alpha. The strategy is fixed and scoped; adding a
menu of more strategies is not the next prerequisite.

Machine v8 now owns the aggregate ERC-1 reference manifest, including the
initial baseline, exact CPU arithmetic declaration and their paid bytes/work.
At the registered ordinary stream's end it records a terminal conclusion and
closes all continuation ports. `snapshot().run` distinguishes complete finite
execution, historical class proofs, unresolved policy stages and failed run
closure. A completed event or installation alone cannot imply run success;
report retention can still fail while those completed prefixes remain owned.
Partial optimizer units and spent alpha are never flushed or refunded.
Read [`OWNED_REFERENCE_RUN.md`](theory/proofs/OWNED_REFERENCE_RUN.md) and run
`scripts/audit_reference_run.py`. The complete 35-program CPU path seals at
cursor 22, including in an actual 64 MiB process with checked final exit.

The [47-gate crosswalk](docs/REFERENCE_RELEASE_GATE_MAP.md) is an evidence map,
not 47 passing flags. Gate 17 now has the actual n=32 owned execution and
negative controls described above; final reference integration now passes.
Gates 16/28–30 and the target parts of 13/20 now have complete actual AMP
integration at `5e55eb4`.
Do not expand static cases or invent optional universal
policy, quotient or cross-root protocols as prerequisites for this scope.

Read [`OWNED_REFERENCE_PERSISTENCE.md`](theory/proofs/OWNED_REFERENCE_PERSISTENCE.md)
before interpreting `REFERENCE_CROSSED`. Its mean-null and stochastic
process law are explicit assumptions, never inferred from unread data.
Downward rational bounds/floor wealth preserve conditional validity but
can destroy power; failure terminates the identity instead of skipping a
loss. A fresh observation can serve several preadmitted identities, each
with its own alpha. Epoch and optimizer clocks remain distinct. This is
reference evidence, not a paired AMP or installation certificate.

The online interface explicitly permits exact revealed train/online access;
its finite-precision query is not the only observable information channel.
The deterministic registered learner uses mean-CE projected SGD and stops
gradient through delayed histories. Failed event prefixes retain revealed
targets and spent work and cannot resume as unread. Retired lineages keep
owned code references for their retained evidence. Historical unsafe signers
are no longer callable; the exact old modules are still replayed from Git
by the historical audit. Current `proof.py` contains only typed data and
the fixed reference-maximum checker; issuance belongs to Runtime.
`bridge.py` remains an empty reference/AMP authority boundary. The new
`float64_bridge.py` performs passive numeric checks, with execution and
retained phase evidence owned by Runtime; importability grants no token.

Current exact evidence includes 960 independent gradient vectors, all 64
three-event binary context/target streams with two reference lineages, and
the existing XVII.5 value path executed for 512 deterministic online events.
That path now also executes 512 paid **profile** events from only 16 retained
original labels, without advancing the ordinary cursor. The final learner
preserves its optimizer count and delayed state at newborn attachment;
profile creates no fresh observations. The old dormant factor face also
survives the actual 32-step registered profile, as its theorem predicts.
Independent complete enumeration now checks 14,860 program/class cases in
nine small grammars. Runtime compares 110 profiled programs (440 actual
replay events), ten recurrent/binding programs and all 587 members of a
small XOR grammar. The latter discovers a PRODUCT descendant after all
shorter prefixes fail to improve. No fitted value, gradient/support quotient
or heuristic prefix rejection supplies the winner. Typed proofs reject
wrong classes, stale state, bad selection, inflated scores and skipped
regions; any unresolved member or verification budget blocks issuance.
The packed-reference model, `ConstructionContract` and `OnlineContract`
remain partial; no complete ERC-1 enforcement or 47-gate release is claimed.

The central foundation principle is:

> **Never erase or assume information before proving that every legal future continuation relevant to the claim cannot use it.**

Its three manifestations are:

- **state:** claim-relative behavioral congruence / simulation;
- **information:** legal claim-separating acquisition transcripts;
- **physics:** reachable history transitions and real ownership/resource accounting, not final-state fantasies.

Computation and statistics then impose honest `UNRESOLVED` outcomes when the registered work/information/evidence contract cannot close a decision.

## 2. Native FP semantics

Do not add another architecture-action vocabulary. The semantic grammar is deliberately small:

1. preregistered typed causal nonnegative sources;
2. positive `SUM`;
3. positive `PRODUCT`;
4. positive normalized readout with a strictly positive causal base;
5. positive delayed recurrent transition programs.

Search refinements such as branch splitting, candidate enumeration or a solver queue are **Compiler search partitions**, not model primitives. Historical labels such as `BIRTH`, `MERGE`, `REWIRE`, `PROBE`, `GROW-R`, etc. must not reappear as canonical semantic controller actions.

## 3. What is actually proved

The most important theorem-level results are consolidated in `FP_THEORY.md`. In particular:

- exact deterministic quotients are valid only under claim-relative transition congruence;
- one-sided dominance is a preorder, not an equivalence quotient;
- approximate similarity uses metrics/covers/error simulation, not non-transitive “epsilon equivalence classes”;
- categorical residual count and predictive packing provide representation-independent state-information lower bounds;
- arbitrary finite categorical dynamics admit compact bit-coded positive recurrent state coordinates, so categorical state count is not a linear vector-width bound;
- one-shot degree-limited positive polynomial capacity is exactly `binom(k+d,d)`;
- fixed-generator positive predictive dimension is a restricted positive-realization invariant-cone notion, not a general recurrent-FP state bound;
- a single positive recurrent scalar can generate exponentially large finite-horizon response span, killing rank-as-general-state lower bounds;
- exact general compilation has unavoidable information/computation barriers: point-query frontier lower bounds, hidden-hypergraph hard families, exact NMF hardness and fixed-charge/knapsack structure;
- finite-amplitude legal probes can defeat local high-order derivative blindness, but **only under the declared query interface**;
- semantic divisible support and physical fixed-cost materialization are different optimization objects;
- physical graph claims require real build/install/state/resource reachability and ownership;
- persistence is fresh, lineage-specific, filtration-aware and path-matched on reference and AMP trajectories;
- the complete self-Compiler boundary is atomic and includes live shadows/jobs/frontier/RNG/resource/error state.

See `CLAIMS_AND_STATUS.md` for status classification.

## 4. What was falsified and must not be reintroduced

Do **not** resurrect these as if they were current FP theory:

- “raw K shortage inside the current coarse support is the main wall” — Trial 1C falsified this explanation;
- current function equality implies learner/compiler equivalence;
- one-step response equality implies recurrent-state equivalence;
- nonnegative rank lower-bounds general recurrent FP coordinate dimension;
- PRODUCT depth alone is a universal acquisition-complexity measure;
- proper-parent first variation can safely prune all PRODUCT descendants;
- unpriced cone/NNLS support is the final physical graph;
- physical realization/cost can be postponed until after semantic optimization;
- local GN/HVP/first-order closure is a global exact uselessness certificate;
- a finite candidate class magically reveals an unknown future expectation;
- `feasible=true`, a high e-value, a bridge bool or a safety bool can be reused as a timeless certificate;
- validation/test labels may drive proposal or persistence;
- exact current task equality permits task-free refactoring when future Compiler optionality changes;
- a solver reaching tolerance means global completion;
- a heuristic architecture choice may replace an unresolved theorem-level region.

The R4.2 historical real-GPU implementation is preserved specifically because it demonstrated that a formally sophisticated Compiler can still instantiate only a tiny partial grammar and remain near unigram.

## 5. Current implementation frontier

Read [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md) before touching code.

Two implementation strata exist:

1. **Historical complete implementations.** R3/R4/R4.1/R4.2 packages were complete runnable releases. R4.2 source is preserved under `experiments/legacy_r4_2_v23/`, but its completeness claim was theoretically superseded by the v24 counterexample.
2. **Current R4 Reference Compiler rewrite.** On 2026-09-05 a stricter reference implementation existed in the research workspace with modules including `core`, `resources`, `semantics`, `search`, `equivalence`, `data_usage`, `program`, `candidate_factory`, `machine`, `lineage`, `runtime`, `compiler`, `build`, `learner`, `bridge`, `info`, `persistence`, `proof`, `native_search`, `anti_unigram`, and `data_store`. An intermediate state passed 24/24 unit tests and a 47/47 gate registry. Subsequent hardening changed the complete Runtime contract; that final integration had **not** been re-frozen when GitHub migration began. Only part of the final scratch tree survived as directly persisted files, so this repository records that boundary explicitly instead of inventing a passing status.

The intended strict construction/commit chain is:

```text
registered native program skeleton
    -> registered initializer/profile produces complete ref+AMP states
    -> registered machine model deterministically realizes physical objects/cost
    -> authority-issued build/safety provenance
    -> four continuous trajectories (dep-ref, dep-AMP, cand-ref, cand-AMP)
    -> fresh paired persistence + event-level bridges
    -> ownership-aware atomic install of complete Omega
```

A caller must not be able to submit a magically pre-trained state, arbitrary cheap object list, arbitrary query callback, bare `upper_fn`, safety bool, bridge bool, or persistence bool and thereby obtain `CERTIFIED`/commit authority.

## 6. Historical research progression (static study now parked)

The dated sequence below explains the route to XVII.31. It is not an active
TODO list. Section 1 gives the current CUDA-prefix result and target frontier.

**Research update (2026-09-06).** The user explicitly redirected work away from
getting stuck in engineering and towards research. The new result in
`FP_THEORY.md` XVII.1 solves the exact normalized-SUM loss envelope for weighted
binary 2x2 tables and gives a one-PRODUCT XOR witness below the strongest SUM
control. Read `theory/proofs/NORMALIZED_SUM_XOR.md` and its exact audit before
using anti-unigram gates. Beating unigram alone does not force PRODUCT. The
continuous SUM optimum can be unattained, so it is an optimistic envelope,
not a reachable lower witness. The next research frontier includes multi-input
passive tasks, finite dynamic range, and construction/acquisition of witnesses.
The authority counterexamples are committed separately; full runtime closure
and actual AMP gates remain open, with science HOLD.

The subsequent `ONE_PRODUCT_CONDITIONAL_TABLE.md` result generalizes the witness
to **every positive 2x2 conditional table, any finite output alphabet**. Exact
minimum PRODUCT count is 0 or 1 according to vector-segment relative-interior
intersection. Do not substitute scalar coordinatewise overlap for a shared
vector witness. Exact need for PRODUCT can coexist with zero approximation
gap; robust forcing requires the loss-separation theorem and physical/value
reachability. This construction exploits native normalization and is not an
external architecture menu.

`FP_THEORY.md` XVII.2 now also supplies a complete static known-positive-cone
membership/closure procedure. A single homogeneous cone solution is **not**
enough when it sets some normalizers to zero: retain those contexts and solve
the residual problem. At most one rational LP per context suffices, with exact
primal/dual checks and constructive finite approximation bounds. This is a
useful scoped solver result, not a full Compiler freeze or an oracle for an
unknown conditional table. The 3x3 hidden-XOR counterexample and audit are in
`NORMALIZED_POSITIVE_CONE_CLOSURE.md`.

The finite-range gap is now explicit in `FP_THEORY.md` XVII.3: the boundary
table `(1/2,1/2,3/4,1/4)` has a sharp SUM approximation/range tradeoff, and its
Bayes-optimal minimum PRODUCT count falls from 2 to 1 when a preregistered
readout-normalizer cap passes `16/3` (Bayes feasibility starts at 4). The
at-most-one-PRODUCT exclusion at R=4 has a proved `1/1568` CE margin and covers
PRODUCTs of arbitrary SUM parents, not a corner-interaction menu. This is still
a static numerical-range result; do not label it a GPU/bytes/FLOPs phase or
grant unconstructed coefficients. Remaining research should connect such
certificates to finite passive information and registered value construction.

The finite-information step is now partly closed in XVII.4. Complete probability
interval boxes, rather than point estimates, admit an exact robust SUM-exclusion
criterion. A one-bit query collision proves a genuine unresolved information
class; an explicitly iid passive stream admits simultaneous anytime confidence
boxes using a single preregistered alpha budget. A range-four two-PRODUCT witness
also retains its loss advantage over a whole radius-1/224 target ball. Read
`PASSIVE_INTERVAL_STRUCTURE.md` for law/data-role boundaries: this does not
grant conditional-table queries, validate a fixed corpus, or recycle discovery
labels as fresh persistence. The remaining construction question is substantive:
can registered value dynamics reach the useful witnesses within their resources?

There is now a scoped positive answer in XVII.5: an explicit zero-initialized
ordinary CE profile reaches a two-PRODUCT state that beats the entire one-PRODUCT
class at R=4. The exact proof gives 21 updates; a checked enclosure and a
separately registered finite-encoded coefficient path each certify 13. An
expressive one-PRODUCT factorization supplies the counterexample in the other
direction: its dormant zero-gradient face is permanently stuck under that
initializer. Read `REGISTERED_VALUE_REACHABILITY.md`. This closes one real value
construction, not arbitrary-graph value reachability, complete build/install,
fresh persistence, or the target AMP bridge.

The fresh-evidence connection now has a scoped power theorem in XVII.6. Bounded
binary log loss controls the gain's second moment by Bayes excess risks, so the
existing linear e-process has a sufficient fresh budget proportional to inverse
gap when the constructed candidate is sufficiently accurate. The 32-step finite-
encoded witness satisfies this premise for the declared independent iid target
law. The exact-log and certified-lower-score budgets are mathematical upper
bounds, not executed million-event experiments. Crucially, the entire comparator
function must be selected before the fresh context to import the static
all-class gap. An exact context-aware constant-selection counterexample shows
why this cannot be silently assumed for general causal LM. Read
`LOG_LOSS_PERSISTENCE_COST.md`; complete controller accounting, actual wealth
arithmetic, physical installation, and the AMP bridge remain separate.

Multi-input research now has an all-dimension exact envelope in XVII.7 for the
**full mass-degree-below-d family** on noisy parity. Positive normalization
retains a highest-order Fourier obstruction; a native edge-indicator hierarchy
shows the loss lower bound is sharp but unattained. This also proves a PRODUCT
depth lower bound, without conflating degree with node count under sharing.
Read `PARITY_DEGREE_ENVELOPE.md`. This is a larger class than unary SUM for d>=3:
its small excess over Bayes differs from the unary-SUM envelope's small
improvement over unigram, now separately proved in XVII.12. Range, value construction and physical
installation of the hierarchy are not granted by the extensional theorem.

A new exact counterexample sharpens that frontier: all six coordinate faces
of a three-bit table pass SUM-closure checks, and every probability threshold
cut is linearly separable, while the global table is exactly 2/15 away from
every SUM model. An explicit global cone dual and matching finite integer-mass
witness certify the distance. Read `LOCAL_SUM_CERTIFICATE_COUNTEREXAMPLE.md`.
Local certificates need a compatible shared realization; their independent
existence is insufficient. The complete residual-cone theorem remains valid.

XVII.8 now separates reduced output degree from positive derivation support
quantitatively. On one reversed-root noisy-parity task, minimum normalizer
ranges for unrestricted / reduced-degree / proper-support programs are exactly
4 / 12 / 20 in three dimensions, with a proved proper-support CE gap at cap
12. The general formulas give an exponential range ratio. Read
`PARITY_PROVENANCE_RANGE.md`: algebraic cancellation of a top coefficient does
not authorize deleting its full-support positive provenance. Independent LP
primal/dual checks verify the sharp static optima; registered value and physical
installation remain separate. This is a research result about native semantics
and resource feasibility, not another controller action or Compiler freeze.

XVII.9 closes another scoped research gap: known-cone global loss optimization
now has a finite arbitrary-accuracy algorithm, not only membership tests or
local optimizer values. Probability-box feasibility keeps the positive base
fixed; exact multinomial uppers, primal/dual checks and a separately verified
covering tree certify a finite likelihood bracket. Termination with an exact LP
oracle survives unattained optima and unbounded coefficients. The implementation
still returns UNRESOLVED on work exhaustion or missing rational evidence. Read
`POSITIVE_CONE_LOSS_SOLVER.md`; this solves a static relaxation and must not
grant reachable value, full Compiler completion or installation authority.

XVII.10 makes that static solver substantially tighter when finite normalizer
bounds are declared. Chords relax only log normalizers, preserving shared mass
coupling, and have quadratic error. Rational tangent/dual certificates charge
every positive residual against a proved coefficient bound. On the same full
cap-four XOR class, 87 nodes beat the earlier 43,023-node tolerance; 551 nodes
give a global CE interval narrower than 7.52e-7 nats. Read
`NORMALIZER_CHORD_CERTIFICATES.md`. The fast proposal path may still return
UNRESOLVED, and this node reduction is not a physical budget/AMP result.

XVII.11 now completely characterizes fixed-mass one-PRODUCT sharing on two
binary inputs. The mixed-difference sign invariant misses a common nonnegative
slack condition; exact enumeration finds 356 false sign certificates among
6,561 small tables. A four-label identity task separates the relaxed minimum
range 15/2 from the actual one-PRODUCT threshold 35/2. At its unrestricted
minimum range 5, four scalar PRODUCT nodes are necessary and sufficient, with
a positive all-at-most-three-PRODUCT loss margin. The rank argument extends to
N=2^d labels and forces at least N products at range N+1. Read
`ONE_PRODUCT_SHARED_SLACK.md`. This is a static mass/resource theorem; neither
the derived normal form nor batching authorizes changing complete-state
provenance or scalar semantic node counts.

XVII.12 closes the all-dimension unary-SUM parity conjecture:
`inf L=log2-2^(1-d)[log2-H(eta)]`. The proof goes through a global normalized
affine parity discrepancy bound, an integrated log-ratio oscillation bound,
and the log-cosh loss identity. A finite SUM witness approaches the exact
infimum with excess <=2/K and normalizer O(d K^2). Exact rational checks,
an equivalent algebraic likelihood inequality and outward-log audits all
pass. Read `UNARY_SUM_PARITY_ENVELOPE.md`. This establishes a strong all-SUM
baseline in every dimension; the earlier conjecture labels are superseded,
not evidence that a local optimizer established global completeness. General
nonuniform targets, sharp finite-range optima and reachable acquisition/value
remain open.

XVII.13 quantifies how final-normalizer range limits SUM's higher-order
response. The full d-input class reduces exactly to a two-variable rational
optimization after proving the optimal numerator and denominator smoothing.
For `A=(d-1)H_(d-1)`, approaching maximal parity discrepancy within epsilon
requires range at least `4A(1-epsilon)/epsilon^2`; the leading constant is
attained asymptotically by finite native witnesses. A separate exact positive
polynomial certificate proves D_3(4)=1/40. It implies CE>0.69004167 for all
SUM models on noise-one-quarter three-bit parity, while four native PRODUCTs
attain Bayes at the same cap, separated by more than 0.1277 nats. Read
`SUM_PARITY_RANGE_CAPACITY.md`. The derived objective reduction does not
preserve a particular learner or authorize a runtime rewrite. Sharp CE optima,
general finite-cap discrepancy formulas and physical installation remain open.

XVII.14 now closes the finite-range **CE rate exponents**, distinct from the
discrepancy capacity. At fixed dimension and fixed positive noise, the gap
above SUM's sharp unbounded infimum is Theta(1/R); at zero noise it is
Theta(1/sqrt(R)). A direct loss-discrepancy inequality supplies the deterministic
lower bound, while a quantitative log-ratio contraction supplies the noisy
lower bound. Finite native constructions match both exponents. Positive noise
allows finite exact Bayes masses at the two root contexts; deterministic
labels do not. Read `SUM_PARITY_LOSS_RANGE_RATES.md`. Sharp leading CE constants,
the uniform noise/range crossover and actual reachable value remain open.
This is not a claim that maximizing Fourier response solves the task loss.

XVII.15 exposes a more basic certificate hazard. A three-input selector task
at cap three needs two PRODUCTs for exact Bayes realization, but one PRODUCT
approaches Bayes arbitrarily closely at the same cap. The family can even
use a fixed coefficient alphabet and bounded feature values: its SUM chains
and required exact numerical state keep growing. This is a concrete reason
to charge complete construction resources and never turn exact exclusion
into a positive loss margin without a closure argument. The full SUM class
still has a proved positive gap. At k=54, CPU float64 rounds the one-PRODUCT
excess table to the exact target even though rational evaluation differs.
Read `ONE_PRODUCT_BORDER_COUNTEREXAMPLE.md`; do not confuse this with an
exact finite-machine theorem or a counterexample to fixed-atom cone closure.

XVII.16 explains the border mechanism with a complete given-coefficient graph
criterion. Positive visible PRODUCT edges must factor consistently; after
contracting them, directed zero edges must form an acyclic graph for closure.
Cycles provide polynomial contradictions and acyclic heights construct exact
rational epsilon families. The coefficient image is closed iff its visibility
graph is a disjoint union of complete bipartite components. Read
`MASKED_PRODUCT_CLOSURE.md`, including its relation to existing toric
factorization results. A separate lift theorem retains all alternative mass
coefficients and finite conditional scales. That existential theorem is not
an implemented full mass solver: only the given-coefficient checker is
executable, with independent cycle and forged-certificate audits.

XVII.17 resolves alternative observable lifts on a substantial zero-face
subclass. For scalar masses zero at opposite cube vertices, all one-PRODUCT
limits reduce to directed cuts even when approximants leak at those vertices.
Singleton/complement observations fix row/column margins, whose unique toric
closure member decides the full mass. Three inputs give a complete rational-
table decision over real coefficients and closure of the whole positive cut
cone. A rational example needs irrational exact factors. Four inputs already
separate: the sum of two independent XORs has one-PRODUCT mass distance >=1/7;
its conditional target at cap four has all-one-PRODUCT CE gap >=1/2000000,
while two PRODUCTs reach Bayes. Read `ANTIPODAL_PRODUCT_MASS.md`. The entropy
characterization is a proof of the unique margin lift, not a new training
objective. General mass solvers, sharp constants and finite-encoding/value
reachability remain open.

XVII.18 exposes a stronger border obstruction: a two-PRODUCT chain approaches
`f=(1-x)yz+x(1-z)w`, whose positive/zero pattern itself requires three
PRODUCTs. The proof covers all shared/nested two-PRODUCT DAGs and uses four
zero-face witnesses; it no longer relies on a mass mismatch inside an already
available support. The explicit family has local alphabet {1/2,1,2}, feature
cap two and growing SUM length. Read `TWO_PRODUCT_SUPPORT_BORDER.md`.
Its general zero-face theorem also proves that m independent XOR masses
need exactly m PRODUCTs. Those are exact-support results; unrestricted
approximation and conditional normalizers cannot inherit their lower bounds
without another argument. A conservative explicit margin is available when
SUM count and a nonzero coefficient floor are additionally bounded.

XVII.19 closes the finite-P static support-limit characterization and provides
an exact certificate search. Visible monomial exponents obey a finite set of
linear inequalities, with disjunctions selecting a leading monomial at each
positive context. Accepted integer powers construct limits; fully covered
Farkas trees reject every alternative. Three-bit odd-parity mass has a checked
all-at-most-two-PRODUCT distance >=1/18432, while three PRODUCTs attain it.
Read `PRODUCT_SUPPORT_CLOSURE.md`. The saved rejection can be verified without
an LP/SMT solver via `product_support_closure_audit.py --verify-parity-proof`.
A general positive-polynomial lifting proof also shows that every finite
mass limit has a path a*epsilon^w. Searching the positive leading constants
for prescribed mass values is unimplemented; generic executable status is
only about support. Search budgets or failed exact reconstruction return
UNRESOLVED; full Runtime/AMP authority is separate.

XVII.20 closes the three-versus-four conditional parity boundary through a
general last-PRODUCT comparison. For k disjoint excess targets, discard the
head with maximal coefficient of the last PRODUCT and compare the remaining
prefix to the other targets. Repeating removes k-1 PRODUCTs at error at most
the sum of the original head errors. Thus scalar approximation minimum r>=1
forces joint minimum at least r+k-1. Three-bit complementary parity needs
four PRODUCTs exactly and in closure. With noise eta in (0,1/2) and minimum
cap 1/eta the same conditional minimum is four; at noise 1/4 and cap four,
all at-most-three graphs have CE gap >=1/135895449600. Read
`SHARED_DISJOINT_PRODUCT_LOWER_BOUND.md`. The proof retains arbitrary
normalizers, and the exact audit includes shared/nested/squared graphs,
unbounded features, invalid premise counterexamples and the four-PRODUCT
witness. General higher-bit counts, larger-cap phases and sharp loss gaps
remain open. This comparison supplies no state-erasure or install permission.

XVII.21 derives a source-support invariant that survives arbitrary coefficient
limits without expanding the full polynomial. At each positive context, a
globally consistent largest-term choice retains a monomial using at most
P+1 distinct sources. Its value is bounded below by an explicit factor of
the original output, even with shared ancestors and unbounded coefficients.
On the full binary cube this proves that a codimension-m face mass needs
exactly m-1 PRODUCTs both exactly and in approximation. Read
`SOURCE_INTERSECTION_PRODUCT_BOUND.md`. Combined with the shared-output
comparison, N=2^d singleton heads need at least N+d-2 nodes, improving the
earlier N bound. At d=3 and minimum conditional cap nine, all at-most-eight
graphs have CE gap >=1/1774224. XVII.22 below closes the remaining exact
and approximation counts. The pointwise source-intersection rule is only necessary:
three-bit parity passes it at P=2 while the complete exponent proof rejects
closure. Sharp higher-dimensional exact counts, larger-cap phases and quantitative
optima remain open; physical/value/AMP scope is unchanged.

XVII.22 settles the shared decoder boundary: the full all-dimension
approximation minimum is N+d-2, N=2^d, while the three-bit exact minimum is
twelve versus approximation minimum nine. Read
`DECODER_EXACT_AND_LIMIT_COMPLEXITY.md`. Its common near-singleton root keeps
epsilon-ordered tails; descendants use an ordinary source PRODUCT and SUM
amplification to recover every other singleton. The actual finite-alphabet
graph has feature cap one, minimum final cap N+1 and
2d(k+1)+k(N-1) weighted SUMs for epsilon=2^-k. A separate exact-only
terminalization theorem permits complete support enumeration: three auxiliary
PRODUCTs can supply at most six of the eight terminal singleton outputs.
This reduction is explicitly falsified for limits by the new construction.
At d=3 and PRODUCT budgets nine through eleven, SUM cost for accuracy is
Theta(log(1/error)); eight or fewer retain a loss gap, and twelve permit a
finite exact graph. Exact arithmetic is essential: binary64 k=54 appears
exact, while k=400 underflows before amplification and loses all excess
outputs at context 111. General higher-dimensional exact counts, sharp
construction constants, larger-cap phases and the registered AMP/value path
remain open. No support quotient or mass limit receives Runtime authority.

XVII.23 proves the exact decoder count is discontinuous at the minimum cap:
twelve PRODUCTs at R=9, nine throughout 9<R<243/26. Any positive cap slack
allows nonnegative inverse readout weights over the shared subset basis,
giving finite exact prediction with N+d-2 PRODUCTs in every dimension.
Read `NORMALIZER_SLACK_DECODER.md`. The lower argument retains all normalizers
and improves the three-bit scalar one-PRODUCT singleton gap to 1/4; at cap
nine the at-most-eight probability/CE gaps improve to 1/45 and 1/8100.
The endpoint 243/26 is only a proved exclusion boundary. Dyadic witnesses
need O(log(1/h)) SUMs as slack h tends to zero. For PRODUCT budgets nine
through eleven the full joint SUM law is Theta(log(1/(h+delta))) for
probability tolerance, or Theta(log(1/(h+sqrt(rho)))) for CE tolerance.
Higher cap transitions, sharp scalar/constructive constants and registered
physical/value/AMP realizations remain open.

XVII.24 closes the unrestricted-range endpoint: the exact worst-case PRODUCT
count for arbitrary strictly positive finite conditionals on d binary inputs
is 2^d-d-1, also in approximation. A complete-class static rank bound matches
a fixed monomial-bank construction after explicit positive row scaling.
Read `CONDITIONAL_PRODUCT_UNIVERSALITY.md`. Rational target tables permit
finite integer-coefficient SUM graphs; their potentially large normalizers
and encoding/construction costs remain resources. The three-bit identity
task has exact/approximation minimum four for R>=108, while at most three
has probability gap 1/72 and CE gap 1/20736 at every cap. Cap 108 is proved
optimal only for the fixed xy,xz,yz,xyz bank with full unary readouts, not
for the complete variable-parent four-PRODUCT class. The intermediate cap
thresholds, fixed-small-alphabet universality counts and full value/resource
path remain open. Static table rank must not become a recurrent state bound.

XVII.25 closes the larger-range three-bit parity PRODUCT count: exactly two
for R>=(r+1)*(r^2+r-1), r=(1-eta)/eta, versus four at minimum range r+1.
Read `TWO_PRODUCT_CONDITIONAL_PARITY.md`. At noise 1/4, two native nodes
A=XOR(x,y) and B=A*z_1, with explicit positive readouts, attain cap 44.
XOR itself is an ordinary PRODUCT of unary SUMs, not an added source.
The range formula is sharp only for this fixed A,B bank; full variable-parent
thresholds and intermediate three-PRODUCT phases are unresolved. At most
one has a cap-independent positive CE gap by the full sub-degree theorem.

XVII.26 resolves the fixed-alphabet asymptotic capacity question. With N=2^d
and k>=2 labels, exact and approximate positive conditional universality
both cost Theta(min(N,sqrt(N*k))) PRODUCTs at unrestricted normalizer range.
Read `FIXED_LABEL_PRODUCT_CAPACITY.md`. A full-class rational parameter map
and algebraic dependence exclude approximation below the parameter bound;
positive block factorization supplies the matching order. XVII.27 sharpens
the frozen numerical bank minimum to N-d-1, even for binary labels. At
d=8, target-dependent intermediate feature values permit 44 versus the
exact frozen-bank minimum 247. The graph skeleton can stay fixed:
this forces feature-value adaptation, not topology change or optimizer
reachability. The full N*k coefficient information and potentially large
SUM/encoding/range costs remain explicit. Sharp small-(d,k) counts, especially
two versus three for binary three-bit universality, and full resource/value
paths remain open.

XVII.27 gives a complete support-only criterion for frozen-bank conditional
universality: no partial coloring may make every touching feature span at
least two colors. A coloring yields a strictly positive hard target and a
cap-independent gap; absence yields exact feasibility by Farkas separation.
Read `FROZEN_FEATURE_UNIVERSALITY.md`. Proper span has a simpler common-
annihilator obstruction, closing the exact frozen universal PRODUCT count
N-d-1 for every fixed k>=2. Full span itself is insufficient. The two-bit
banks xy and (1+x)(1+y) have the same full span but different universality;
the frozen XOR/XNOR bank is universal for two/three labels and fails for four.
Any finite positive validation set can pass exactly in a shifted bank that
is still nonuniversal. Both partial domains and exact zero supports matter.
This closes a frozen readout decision class, not variable-parent target
search, fixed-resource learning or Runtime authority. Binary three-bit
variable-feature universality still lies between two and three PRODUCTs.

XVII.28 completes the coefficient-path characterization for conditional
closure. Every unrestricted-range limit has a native monomial coefficient
path; support comes from rowwise leading exponents, while exact probability
values require all tied amplitudes. At finite cap R>k, a bounded mass-limit
lift plus one final excess contraction
`beta=(R-k)/(R-k+D*epsilon)` gives actual finite candidates at that same cap
and PRODUCT count. Read `CONDITIONAL_COEFFICIENT_PATHS.md`. Pure monomial
paths alone are incomplete under the cap: none with at most eleven
PRODUCTs can approach the three-bit decoder at cap nine while remaining
feasible, although nine PRODUCTs approach it after readout contraction.
With unrestricted SUM scaling, any finite graph can also be rescaled to
keep hidden values within a bound already met by its sources and final
excesses. Downward dyadic rounding gives the same prediction closure with
local coefficients {1/2,1,2}, retaining normalizer and common activation caps
at the cost of growing SUM work. Those caps and the finite alphabet do not
replace complete construction/numerical accounting. Generic phase/amplitude
search remains unimplemented; the new audit independently verifies rational
paths, cap corrections, hidden rescalings and actual finite-alphabet graphs.
The union of shifted nonuniversal banks is also proved exactly universal
over positive targets of every finite label count, despite its fixed support
pattern. Full variable-parent counts and registered value/physical/AMP paths
remain open.

XVII.29 turns free-SUM closure into a general construction-cost law. At
fixed PRODUCT budget and finite normalizer cap, every closure point has
a same-cap local-{1/2,1,2} approximation with O(log(1/delta)) SUM nodes.
For fixed algebraic source and target values, this is also a lower bound
unless exact local realization is possible: the full trichotomy is a
positive gap, an eventually constant minimum exact SUM count, or
Theta(log(1/delta)). Read `SUM_ACCURACY_COMPLEXITY.md`. Rational data give
an explicit denominator bound; a field-norm argument covers algebraic
irrational data without rounding them away. A one-context target (5/8,3/8)
at cap 8/3 already distinguishes real exactness from local-alphabet
nonattainment. With growing PRODUCT count, a positive geometric construction
achieves O(log log(1/error)) SUM/PRODUCT nodes at that same cap, while its
direct numerical significand still grows logarithmically. Transcendental
data and unbounded range with unpriced arity give explicit counterexamples
to broader lower claims. Generic fixed-P exact/closure branch classification,
sharp constants and joint/full resource costs remain open; the new audit
is exact rational/number-field graph verification, not Runtime authority.

XVII.30 completely classifies exactness/closure for positive rational tables
on the binary cube when both SUM and PRODUCT budgets are unrestricted but
finite, with the local alphabet {1/2,1,2}. Read
`DYADIC_CAP_AND_TOTAL_COMPLEXITY.md`. Let R_0 be the largest reciprocal row
minimum. Below it there is a gap; above it exact local realization exists;
at R_0 exactness holds iff every critical forced mass R_0*Q is dyadic.
For the nonattained boundary, the sharp total-node order is
Theta(log log(1/error)). Positive geometric reciprocals supply the upper;
the full dyadic denominator bound supplies the lower. Actual constant-to-
indicator PRODUCTs, target encoding and the native singleton bank are charged
in the construction. A dyadic cap alone fails for multiclass targets, and
noncritical normalizers must retain their own legal scales. The audit checks
3,067 classifications, 1,995 exact graphs and 72 limit graphs. This settles
the unrestricted-node branch decision and accuracy order; it does not solve
fixed-P classification or exact finite-size optimization. In particular,
the identity task's 12-PRODUCT exact certificate is rejected for P=9.
Sharp Pareto/physical/value/precision/AMP costs remain open.

XVII.31 closes the joint asymptotic resource study for the rational binary
nondyadic-cap class. Read `NODE_EDGE_PRECISION_ACCURACY.md`. For cap slack h
and probability tolerance delta, write epsilon=h+delta. Every candidate
needs S*2^P>=log2(1/epsilon)-O(1) and direct mass precision
b>=log2(1/epsilon)-O(1). A native upper matches the separate budget envelope
up to fixed target/domain overheads and precision constants, with actual
repeated edges and exponent range retained. The node-only optimum is
log2(log2(1/epsilon))+O(1). One binary-arity construction simultaneously
attains optimal C/E order Theta(log log(1/epsilon)) and full direct numerical
bit volume Theta(log(1/epsilon)). A retained positive reciprocal tail gives
exact Q at positive h without subtraction; complete critical masses force
the precision lower. The audit checks 90 budget-envelope graphs, 92 exact
tail repairs, 100 small-edge approximants and 1,533 floating mass rows.
This is a scoped law, not generic fixed-P completeness or an AMP bridge.

ERC-1 freezes the experiment specification, not its executable enforcement.
The remaining static sharp constants and small-P phases are parked. Proceed
to implementation closure, which remains a prerequisite to model/GPU science. Its
outstanding work is:

1. finish/reconstruct the strict complete `ReferenceCompilerRuntime` from the preserved WIP, recovery notes and historical implementations;
2. make one complete execution surface own all claim-relevant mutable state;
3. force query/objective/program/profile/machine/proof/bridge/persistence implementations to be preregistered by the immutable claim contract;
4. restore an executable 47-gate registry against that complete runtime;
5. add end-to-end adversarial tests for forged proof/build/bridge/persistence tokens, cursor divergence, data freshness, ownership/refcount aliasing, build-before-free, stale snapshots, NaN/Inf, quantized query payload, and incomplete decision-class scope;
6. run randomized model checks only after the endpoint path is exercised;
7. only then create an **Implementation Freeze** commit/seal;
8. after the target AMP bridge passes, reconsider RTX3090 science.

If implementation requires a new FP semantic architecture action to become correct, stop implementation and reopen theory. If it only exposes slow search, loose bounds, expensive certificates or insufficient information, improve the solver or return `UNRESOLVED`; do not patch the semantic model.

## 7. Research discipline

1. **Theory first.** If the theoretical loop is not closed, stop expanding experiment implementation.
2. Experiments must instantiate the proved theory rather than approximate a more convenient theory.
3. Theorem/numerical audits use exact arithmetic or float64 reference paths.
4. Real GPU execution uses AMP/mixed precision only after its bridge is proved/audited.
5. Use strong modern baselines; never manufacture a weak baseline to make FP look good.
6. If a native branch collapses, first inspect provenance support, sharing, function-preserving refinement and structural semantics—not activation-repulsion patches.
7. Avoid proliferating named controller actions and special-case `if` mechanisms.
8. Cross-check every concept for necessity; remove redundant concepts rather than protecting them.
9. If theory starts forming a patch wall, retreat to the foundational state/information/physics definitions.
10. It is acceptable to overturn a large previous theory section when a counterexample demands it.
11. Preserve minimal evidence, not caches or raw workspace dumps.
12. Keep FP strictly separate from the independent memory/provenance project.

## 8. Session protocol

At the start of future work:

1. read `FP_THEORY.md`;
2. read this file;
3. read `IMPLEMENTATION_STATUS.md`, `CLAIMS_AND_STATUS.md`, and `OPEN_PROBLEMS.md`;
4. inspect recent Git commits and any active research branch/PR;
5. only then use local scratch reasoning.

At the end of meaningful work, update canonical files/evidence and commit a coherent research change. The repository, not model identity or chat history, is the research state.
