# FP Handoff

This file is written for a capable researcher/model that has **no access to prior chat history**. Treat the repository, especially `FP_THEORY.md`, as authoritative.

## 1. Current research state

The current canonical theory is [`FP_THEORY.md`](FP_THEORY.md). Its status is:

- **Foundation theory frozen.** The state/equivalence/acquisition/construction/physical-realization foundation survived the latest adversarial pass.
- **Reference Compiler implementation not frozen.** The last work was a strict rewrite toward one authority-owned complete `ReferenceCompilerRuntime`. The current persisted/recovered code must be audited before anyone claims implementation closure.
- **Science HOLD.** Do not start new RTX3090/model-science runs yet.

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

## 6. Immediate next work

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

Implementation closure remains a prerequisite to model/GPU science. Its
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
