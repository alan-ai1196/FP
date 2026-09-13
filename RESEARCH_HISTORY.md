# FP Research History — R5 to Current

This is a **logic history**, not a version changelog. It records why the theory changed and which failures produced the current foundation. Historical files/commits are provenance; `FP_THEORY.md` alone is normative.

## 1. R5: provenance became structural information

R5's sparse Factor–Provenance formulation made a basic distinction that survives every later rewrite. A positive SUM contains alternative derivations; backward task credit is signed, but responsibility routes it through the positive derivation decomposition. The important lesson was not the particular sparse implementation. It was that **marginalizing derivation/provenance identity before proving it irrelevant can erase the discriminative subspace needed for structural learning**.

This became the first instance of the later “premature quotient” diagnosis.

## 2. R17: discovery moved from edit enumeration to operator geometry

Early Compiler thinking implicitly scored candidate edges/actions one at a time. R17 showed that JVP/VJP/mixed-HVP/range-sketch operators could expose whole interaction subspaces without all-pairs enumeration. A structured `n=512` hidden-permutation audit used 8 mixed-HVP probes where naive pair inspection exposes 262,144 interactions.

The durable conclusion was **use the strongest legal response operator geometry before coordinate enumeration**. The later theory corrected one overreach: an operator sketch is an acquisition/proposal mechanism, not automatically a positive semantic factorization or a global certificate.

## 3. Trial 1C: raw width was not the missing answer

Scaling Trial 1C calibrated the native block under a fixed coarse structure. Important recorded numbers were:

- `K/d` ratios `{0.25, 1, 1.75, 2.5, 3.25}`;
- at M scale, `CE_2.5 - CE_1 = +0.0179788`, CI `[0.0034627, 0.0324949]`;
- selected FP mean CE `4.2794413` versus dense `4.1196805`, gap `0.1597609`;
- removing relation-position information produced a `+0.2846545` CE diagnostic.

The inference was deliberately narrow: **more raw coordinates inside the same coarse cells had saturated; the problem was structural information/representation, not another K sweep.** Trial 1C became a falsification/calibration experiment, not a source of a new hand-written topology.

## 4. R19–R30: a candidate is a lifecycle, not a static graph

The Compiler then learned that a locally cheaper or better structure can be globally bad once build/switch/run/state/proof costs and reuse horizon are included. Candidate program state was separated from active execution state. Dependency generations and provenance-aware certificate validity were introduced to stop stale reusable results from silently becoming current proof.

This stage was the beginning of treating the Compiler itself as a causal physical system rather than an offline graph chooser.

## 5. R31–R37: local edits failed; frontier representation mattered

R31–R35 established that:

1. first-order structural scores are proposals, not finite decisions;
2. exact one-edit improvements need not compose;
3. coordinated changes can cross a loss barrier even when constituents are individually unprofitable;
4. high-order interaction should exploit provenance structure rather than instantiate generic dense high-order tensors.

R36–R37 shifted attention from raw depth to **typed frontier complexity**. A bad representation can have exponentially large cut rank while an intermediate typed distinction changes the cut and collapses the frontier. This weakened the idea that low rank inside a fixed representation was the universal escape.

## 6. R40–R44: support semantics replaced duplicated branches

R40 re-established a native recurrent SUM/PRODUCT runtime. Naively duplicated SUM branches remained symmetric and collapsed. R41's decisive correction was that a useful alternative is a **distinct provenance-support cell**, not merely another activation channel. Function-preserving support refinement/deduplication/shared factors became preferable to activation-repulsion regularizers.

The later foundation deliberately removed `SPLIT/MERGE/REWIRE/BIRTH` as canonical action names. A support refinement is a semantic/program relation or a Compiler search partition, not a new model primitive.

## 7. v13–v23: response geometry, reachable value and certified physical search

The theory progressively enlarged the object being valued:

- dormant structural response;
- quotient against incumbent-reachable value capacity;
- finite optimizer trajectory rather than frozen coefficients;
- full positive output-fiber measure rather than a preselected categorical output;
- physical cost and sharing/reuse;
- branch lower/upper bounds and exact-NLL fallback;
- finite branch-and-bound with an explicit unresolved gap.

v22 killed the “project/optimize response first, realize physically later” interpretation: identical response can reverse preference under physical cost, and hard budgets can make the unpriced cone optimum irrelevant. v23 therefore unified response and physical realization inside one finite physical-program search.

v23 then made a **closure claim too early**.

## 8. R4.2 real-GPU counterexample: formal coverage was not constructive coverage

The R4.2/V23 implementation is preserved in `experiments/legacy_r4_2_v23/` because it generated one of the most important negative results.

On the seed-1337 real trace, native validation CE at 450/900/1800/3600 seconds was approximately

`7.5940907001, 7.5940836133, 7.5940836133, 7.5940843225`,

while the audited empty-program/unigram reference was `7.5940850973`. Evidence throughput reached ~99.7% of the strong-GPT token throughput by 3600s, so simple starvation was not the explanation. Telemetry showed `product_nodes = 0`: the concrete Compiler repeatedly fit/deleted a tiny atomic family instead of economically searching the declared compound grammar.

This falsified **the previous closure claim**, not positive SUM/PRODUCT semantics. v24 withdrew the claim that interaction order/constructive bridge had been solved and imposed new gates: compound descendants without profitable parents, joint realization, one causal clock, robust numerical/statistical persistence, and a hierarchical anti-unigram witness.

## 9. v25→v155: complete physical learner became complete self-Compiler state

v25 repaired the immediate R4.2 failure by making fixed charges/sharing/ancestor closure, same-token value continuation and fresh persistence part of one branch lifecycle. Subsequent adversarial compaction to v155 kept finding places where a projection had silently discarded information:

- current task output vs future learner update;
- current response vs later continuation;
- semantic program equality vs physical cost/encoding;
- ordinary learner equivalence vs future Compiler optionality;
- ledger summary vs actually resident shadows/jobs;
- coarse optimizer-unit equality vs event-level reference↔AMP behavior;
- current cursor vs replay/transport state;
- candidate-specific evidence vs global selective testing/error allocation.

v155's final runtime object was therefore the complete self-Compiler configuration `Omega=(xi,iota,s,m_C,kappa)` with global filtration and atomic boundary transition.

## 10. v156: rank/state and “exact scalable Compiler” claims were attacked

v156 deliberately attacked the compact theory rather than defending it.

- Fixed-generator shift-closed positive predictive dimension was recognized as a **restricted invariant-cone positive realization** notion.
- Exact one-shot degree capacity was tightened to `binom(k+d,d)`.
- General recurrent FP counterexamples showed one positive scalar can carry behavior whose finite-horizon linear span grows without bound, even to full `2^H` in a constructive family. Thus response/nonnegative rank is not a general recurrent state-coordinate lower bound.
- Exact NMF hardness showed that a universal polynomial-time exact Compiler was the wrong target; finite exhaustive correctness is not a scaling theorem.

## 11. v157–v161: the patch wall was diagnosed as premature quotient + hidden oracle + tractability confusion

The accumulated corrections were compressed into a root-cause triad:

```text
complete claim state
+ legal information/query interface
+ actual physical computation/resource model
```

A claim-relative behavioral congruence theorem explained why current-function/short-horizon/semantic-only projections repeatedly failed. Behavioral packing/covering replaced rank as the representation-independent capacity starting point.

Typed-frontier dynamic programming made exact solve cost explicit: known local factors can be solved in work exponential in the typed frontier load `Phi`, and an unrestricted frontier table under point queries needs `e^Phi` exact queries in the worst case.

Acquisition was separated from solve. A hidden permutation can be recovered from one information-rich vector probe; an exact rank-r response matrix can be reconstructed with `r` forward plus `r` adjoint vector probes under the declared two-sided interface. This removed the misleading idea that “number of probes” alone measures information complexity.

## 12. v162–v164: PRODUCT acquisition and physical materialization were separated

The old Round-35 result `q*=d` for a depth-d pure PRODUCT path was reclassified correctly: it is a **local-jet observation-language lower bound**, not a universal self-compilation lower bound. If finite-amplitude subset probes are legal, a hidden conjunction reduces to group testing. For general positive SUM/PRODUCT completion, the boundary mass becomes a nonnegative polynomial and Boolean support probes reduce to hidden-hypergraph/monotone-DNF acquisition. But the result is explicitly interface-relative; prefix-only or passive interfaces can remain non-identifying.

Then a separate wall appeared even after acquisition is free: indivisible physical fixed charges turn support materialization into a discrete problem containing 0–1 knapsack. Continuous positive-measure KKT flow describes divisible semantic allocation but cannot replace the physical Compiler.

## 13. Foundation R4: one principle replaces the patch wall

The final foundation compressed these histories into one rule:

> **Never erase or assume information before proving every legal future continuation relevant to the claim cannot use it.**

Candidate generation no longer starts from an externally supplied architecture menu. A resource-bounded native program is built recursively from source references, SUM, PRODUCT and delayed binding. Exact state reduction is allowed only through claim-relative contextual congruence. Information acquisition is legal-interface-relative. Physical materialization is history/resource/ownership-aware. Search can be hard; `UNRESOLVED` is a first-class correct result.

Foundation R4 was frozen for Reference Compiler implementation on 2026-09-04. The theory was then consolidated into root `FP_THEORY.md` during the GitHub migration on 2026-09-06.

## 14. Current frontier: implementation is the pressure test

The first Reference Compiler implementation pass was intentionally adversarial. It found API-level ways a supposedly correct implementation could still fake the theorem object: caller-supplied uppers, safety/bridge/equivalence booleans, arbitrary candidate state/object lists, prediction-visible gradient accumulators, unregistered query payloads, ownership-free ledgers, hidden NaN tolerance, data reuse and incomplete Runtime snapshots.

An intermediate strict module set passed 24/24 unit tests and 47/47 executable gates, then the complete Runtime was hardened further. The final endpoint integration was **not re-frozen** before migration. That exact implementation boundary is documented in `IMPLEMENTATION_STATUS.md` and is the next research task.

## 15. Recovered authority counterexamples (2026-09-06)

Executing the actual preserved proof/bridge source against reconstructed strict
core value objects exposed four accepted invalid uses: upper-bound evidence
signed as equivalence, skipped bridge events, unexecuted same-cursor endpoint
replacement, and authorization from a dead bridge session. The missing historical
runtime is not presumed runnable. These are helper implementation mismatches, not
Foundation R4 counterexamples. The unifying obligation is a typed proposition
about an owned, continuously executed complete-state prefix; a signed endpoint
alone is insufficient. See `theory/proofs/EXECUTION_AUTHORITY_BOUNDARY.md` and
`scripts/audit_recovered_authorities.py` for the exact reproduction and scope.

## 16. Native normalization changes the structural baseline (2026-09-06)

Research shifted from authority engineering to the mathematical condition for
task-forced PRODUCT. An adversarial float64 search found that arbitrary positive
SUM with native normalization improves on unigram even for balanced XOR. The
exact solution is an interval-intersection characterization of binary 2x2
conditional tables; the entire weighted SUM loss envelope reduces to four
Bernoulli pooling costs. For balanced noisy XOR the sharp infimum is
`[log 2+H(eta)]/2`, unattained at finite coefficients unless `eta=1/2`.

The bound also controls arbitrary token-specific unary SUM models in the
block-factorized hidden-group gate, so it does not manufacture a weak baseline
by supplying or fixing a group representation. A single native PRODUCT with
positive readout masses `3+48xz` and `1+8(x+z)` predicts deterministic XOR correctly
with probability `3/4` at every context and strictly beats that full SUM envelope.
Four categorical pair-cell PRODUCTs are not necessary. This yields a scoped
all-optima PRODUCT-forcing certificate, conditional on the witness's registered
value and physical reachability. It adds no semantic action and grants no GPU
science or runtime freeze. See `theory/proofs/NORMALIZED_SUM_XOR.md`; the audit
uses 6,561 exact SUM assignments, 26,244 exact likelihood comparisons, rational
table reconstruction, and separately labeled float64 searches.

## 17. One-PRODUCT universality and the exact/approximate split (2026-09-06)

The XOR construction generalized to every strictly positive 2x2 conditional
table, with any finite output alphabet. Positive context-dependent mass scales
allow a single shared corner PRODUCT plus unary SUM to realize the entire
table. A max-ratio construction gives finite rational coefficients for rational
targets and at most `k-1` nonzero PRODUCT-to-head edges. The exact minimum count
is therefore 0 or 1, decided by intersection of the two vector-segment relative
interiors. This is a semantic count theorem, not a free coefficient constructor
or physical resource optimum.

The boundary is scientifically important: 80 of the 256 audited binary rational
tables need one PRODUCT for exact realization yet lie in the zero-PRODUCT
closure. Exact expressivity alone cannot force structure with a positive loss
margin. A separate exact four-label counterexample also kills the tempting
coordinatewise interval shortcut: all scalar intervals overlap while a rational
linear functional separates the actual vector segments. The audit checks all
256 binary tables and 700 rational tables with 2--8 labels; see
`theory/proofs/ONE_PRODUCT_CONDITIONAL_TABLE.md`.

## 18. Zero-normalizer erasure and a complete static closure solve (2026-09-06)

Extending the normalized-SUM geometry exposed another premature quotient: a
homogeneous nonnegative mass solution can give zero total to difficult contexts
and thereby appear to match them. A 3x3 unary table with an outer uniform region
and a noisy-XOR interior passes that single LP, while the interior has a sharp
`1/4` sup-norm separation from every SUM predictor.

The correction is a derived mathematical invariant rather than another model
action. Retain all zero-total contexts as a residual known-table problem. Each
feasible normalized mass direction covers at least one context; any feasible
direction is safe. At most one rational LP per context decides membership in
the entire normalized positive-cone closure. A successful sequence constructs
finite positive-base approximants with an explicit rational error bound; an
infeasible residual supplies a checked Farkas separation. The proof separates
exact realization, closure, acquisition, finite physical range, and reachable
value. Float64 LP outputs are only proposals and every accepted primal/dual
vector is checked against the original rational equations. See
`theory/proofs/NORMALIZED_POSITIVE_CONE_CLOSURE.md`.

## 19. From unattained closure to a finite-range structural phase (2026-09-06)

The binary target `(1/2,1/2,3/4,1/4)` exposed the cost hidden in “arbitrarily
approximable”: its sharp small-error SUM normalizer requirement grows as
`(1-4delta)/(delta(1+4delta))`. At cap R=4 the optimal relaxed SUM error is
`(sqrt(2)-1)/4`, so even rational inputs and a rational cap need not produce a
rational optimum.

The same task gives a complete native PRODUCT-count phase under the declared
readout-normalizer cap. Two PRODUCTs attain Bayes risk at R=4. An arbitrary
one-PRODUCT DAG obeys a same-sign mixed-difference invariant, proving that it
needs R>=16/3; a PRODUCT of two cross-input SUMs attains that threshold. Thus
relaxing the cap removes the requirement for at least two PRODUCTs. The result
also has a positive loss margin: at R=4 every at-most-one-PRODUCT model loses
at least 1/1568 nats to the two-PRODUCT Bayes witness. This avoids confusing an
unattained exact distinction with robust structural forcing. It is a numerical
range theorem, not a claim about unspecified memory/FLOPs or an executed learner.
See `theory/proofs/RANGE_CONSTRAINED_PRODUCT_PHASE.md` and its exact audit.

## 20. Structural acquisition without an exact conditional-table oracle (2026-09-06)

The static certificates were extended to a complete interval information class.
For binary 2x2 targets, strict diagonal/off-diagonal endpoint separation exactly
decides whether every admissible target is outside the SUM closure, with an
explicit rational worst-case risk gap. A one-bit transcript collision between
a SUM table and a separated table proves why additional computation cannot
replace missing query information. Full-support passive finite samples also
cannot provide zero-error structural classification.

Under a declared iid sampling law, a count-indexed simultaneous confidence box
gives an honest statistical alternative. Its dyadic radii and shared anytime
alpha allocation are checked exactly. In a seeded algorithm fixture, noisy XOR
is certified from revealed counts at event 833; a constant control stays
unresolved through 12,000 events. These fixtures are not evidence for the
probability theorem itself. The range-constrained two-PRODUCT witness also
retains a proved margin 115/301056 throughout a radius-1/224 target ball.
Discovery information remains distinct from fresh lineage-specific persistence.
See `theory/proofs/PASSIVE_INTERVAL_STRUCTURE.md`.

## 21. The structural winner became a finite value trajectory (2026-09-06)

A registered 16-label profile and ordinary projected CE descent, initialized at
zero with step 16, construct the two-PRODUCT range-four witness rather than
assuming its coefficients. The two independent slots follow a scalar rational
recurrence by symmetry. A simple contraction proof suffices after 21 updates;
exact outward enclosures certify a strict win over the entire at-most-one-PRODUCT
class after 13. A separate commit-quantized learner with 32 fractional bits
also wins after 13 steps, so the result need not install an enormous exact
rational iterate. The observation count is 208 evaluations of 16 retained
profile labels, not 208 fresh observations or a bound on total arithmetic work.

An opposing native example shows why the value condition cannot be dropped:
zero initialization keeps an expressive PRODUCT-of-SUM parameterization in an
invariant zero-gradient face forever. A static coefficient construction cannot
authorize that initializer/optimizer trajectory. The cure must be a registered
value path or an unresolved candidate, not an invented semantic action. See
`theory/proofs/REGISTERED_VALUE_REACHABILITY.md` and its exact/float64 audit.

## 22. From a constructed value to fresh log-loss power (2026-09-06)

The next gap was evidence cost: a generic bounded-gain tail bound would need an
inverse-square advantage budget. For bounded binary log loss, a direct rational-
constant proof bounds the log-ratio second moment by three times KL. Applied to
candidate/comparator excess risks, this gives a reciprocal contraction for the
existing linear e-process and an inverse-gap sufficient crossing budget when
the candidate's Bayes excess risk is at most one-sixth the comparator gap.
The theorem respects a single live identity and stops its argument at crossing.

The registered finite-encoded candidate satisfies the premise after 32 profile
steps. Under an explicit independent iid uniform-context target, conservative
95% crossing budgets are 1,354,752 exact-score events or 2,709,504 events with
rational lower log scores, at alpha 1/20. These are proved sufficient bounds;
no such fresh-event experiment was executed. Exact checks cover the constants,
log-series tails, value bias, and small-grid moment/reciprocal inequalities.

An adversarial timing check exposed the limit of the structural inference:
choosing among three constant predictors after observing the context can match
the target with a zero-PRODUCT selected endpoint each time. The omitted
controller carries the interaction. Static all-class lower bounds therefore
need selection before fresh context, or a separate valid conditional argument;
they cannot be imported into causal LM by erasing the controller. The mean-null
e-process itself remains valid. See `LOG_LOSS_PERSISTENCE_COST.md`.

## 23. A full-degree obstruction and sharp sub-degree parity envelope (2026-09-06)

Further multistart float64 attacks did not disprove the d-bit unary-SUM
conjecture, but are not a proof. A different, larger class admitted an exact
all-dimension solution. Every mass polynomial below degree d has zero top
parity moment, forcing overlap of the positive-weighted prediction means on
the two parity classes. The resulting sharp infimum is Bayes risk plus
`2^(1-d)[log2-H(eta)]`.

A native spanning-tree hierarchy of degree-(d-1) edge indicators matches all
but two contexts in the limit, proving sharpness with explicit finite range
and error bounds. Positive base prevents finite attainment. Exact noisy parity
must retain full-degree mass information and needs at least `ceil(log2 d)`
PRODUCT depth; sharing means degree is not bounded by node count plus one.
The audit checks 501 proper-monomial moments, 1,153 small edge assignments and
28 finite hierarchies with exact rational arithmetic. This larger class does
not settle the unary-SUM conjecture, grant the hierarchy's value construction,
or close the complete runtime. See `PARITY_DEGREE_ENVELOPE.md`.

## 24. Local face and threshold certificates failed globally (2026-09-06)

An attempted reduction of the three-input SUM problem to independent face
constraints exposed a counterexample. Its six two-dimensional faces are each
in SUM closure, and all of its probability superlevel sets have exact linear
separators, but the full table stays exactly 2/15 away from the entire SUM
family. The common numerator and denominator carry constraints that independent
face witnesses or hyperplanes do not share.

One proof uses a coupled extremum invariant: antipodal minimum and maximum of
a linear-fractional cube prediction force coordinatewise monotonicity. The
table violates it with a strict margin. A second proof supplies the exact
global cone dual `(15/2)chi`; an integer-mass SUM model with total 30 attains
the distance. The uniform CE gap is at least 1/225. All six faces, three cuts,
13 dual atom equalities and 4,096 small coefficient assignments are checked
exactly. This kills a proposed certification shortcut, not the full residual-
cone theorem or Foundation R4. See `LOCAL_SUM_CERTIFICATE_COUNTEREXAMPLE.md`.

## 25. Polynomial cancellation did not remove positive provenance (2026-09-06)

Attacking the finite-range cost of the new degree theorem uncovered a stronger
distinction. Reduced output degree <d is larger than the class whose positive
derivations actually omit some coordinate. Full-context indicator terms can
lose their highest signed coefficient after algebraic expansion while their
positive derivation support remains indispensable under the range constraint.

For noisy parity with its preferred label reversed at one adjacent root pair,
three sharp Bayes range thresholds were derived: unrestricted, reduced-degree
and proper-support programs need 4, 12 and 20 respectively in the three-bit
odds-three example. A full positive edge-cone reduction, justified static
symmetry and a backward recurrence prove the proper-support optimum for every
dimension. Finite positive constructions attain all three formulas; the ratio
between reduced degree and proper support grows exponentially. Propagating
prediction errors through the recurrence also gives a proper-support loss
margin of 1/24336 at cap 12, where reduced-degree programs reach Bayes.

The audit checks 24 exact construction cases through eight inputs, 12 independent
LP optimality certificates against the original rational primal/dual equations,
and a separate exact Farkas exclusion inside the error ball. This is a concrete
reason not to quotient provenance by collected polynomial coefficients. It
does not grant a value initializer, physical build/install or AMP bridge.
See `PARITY_PROVENANCE_RANGE.md`.

## 26. Global loss optimization without installing a closure endpoint (2026-09-06)

Known-cone membership did not justify labeling a local CE optimizer globally
complete. The missing step was closed for the explicit rational static class:
probability-box feasibility is an LP with the original positive base fixed,
and bounded-simplex multinomial likelihood optima are exact rational uppers.
Finite integer-count likelihood is a continuous polynomial with an explicit
Lipschitz bound. Thus bisection reaches any requested relative likelihood
accuracy in finite work with an exact LP oracle, even when coefficients are
unbounded and the supremum is unattained.

The executable algorithm preserves an entire covering tree and a finite
coefficient witness. A separate verifier rederives boxes, checks all original
primal/dual equations and KKT uppers, and rejects missing branches or a forged
accuracy requirement. Generic local optimization only improves checked lower
witnesses; its proposal bounds do not shrink the global decision class.
Early searches exhausted their node budgets honestly. Highest-upper search,
range bounds derived from original constraints and stronger witness proposals
closed the audited unbounded and cap-four XOR cases. No failure required a
semantic change or an unearned completeness flag.

The retained evidence includes global likelihood brackets, multiclass and zero-
count cases, an empty-domain certificate, and adversarial proof-tree rejection.
An unscored context still restricts a shared coefficient through its resource
cap, so zero loss weight is not permission to erase it. This settles finite
arbitrary-accuracy static optimization, not efficient general compilation,
registered value/build/install paths or AMP. See `POSITIVE_CONE_LOSS_SOLVER.md`.

## 27. Shared normalizer geometry collapsed the proof search (2026-09-08)

The first complete static loss solver was correct but used 43,023 probability
boxes on cap-four noisy XOR. Its independent probability bounds discarded too
much shared mass geometry. Replacing only the concave log-normalizer terms by
their chords instead gives a convex relaxation on the original coefficient
domain, with quadratic relative-width error. Rational tangent planes and
linear-dual residual correction make this a checkable global lower certificate.

The same full XOR class closes in 87 nodes at tighter accuracy. A 551-node
run certifies `0.68483177<=inf L<=0.68483253`, with interval width below 7.52e-7
nats; no local optimizer termination is used as global authority. A coupled
three-label control also closes. Exact log enclosures are checked against an
independent 80-digit reference, and forged branches, lower values, dual signs,
accuracy requirements and witnesses are rejected.

The residual term is indispensable: a one-context example makes the
uncorrected scalar lower exceed an attainable Bayes loss. Unbounded null-atom
columns likewise cannot be erased or assigned fictional finite caps. This
is a solver improvement within unchanged FP semantics. Arbitrary inner precision
has an effective tangent-grid LP construction, but the fast numerical proposal
path still returns UNRESOLVED on missing evidence, precision or work. Physical
Compiler closure and AMP remain separate. See `NORMALIZER_CHORD_CERTIFICATES.md`.

## 28. Shared positive slack turns a sign invariant into an exact theorem (2026-09-08)

The existing one-PRODUCT mixed-difference sign obstruction was deliberately
only necessary. Attacking its possible sufficiency exposed two output heads
with disjoint nonlinear supports: each needs one PRODUCT individually, but
their same-sign differences cannot share one. A complete criterion follows
from the common nonnegative slack at the sign's two corners. Its converse
constructs one PRODUCT of two unary SUMs and a positive additive remainder.
An exhaustive rational grid has 356 such sign-only false certificates among
6,561 two-head tables; 1,200 independently generated PRODUCT-of-SUM models
with one through six heads also pass exact reconstruction.

The stronger invariant solves a conditional resource problem as well. For the
four-label identity-noise target `(1+1[x=y])/5`, sign feasibility begins at
range 15/2 but a genuine shared PRODUCT requires exactly 35/2. A convex
quadratic obstruction proves the lower threshold and a finite rational native
construction attains it. At the unrestricted minimum range 5, positivity and
the rank of the PRODUCT readout table force four nodes, with excess CE at least
1/1568 for the entire at-most-three class. This remains valid with arbitrary
compound parents and sharing. The same identity-matrix argument yields a
2^d PRODUCT lower bound for 2^d labels at their minimum range; explicit native
indicator DAGs are checked through eight bits, without claiming those larger
upper counts are sharp.

This separates unbounded conditional universality, fixed-mass sharing and
resource-constrained structure. It does not identify scalar semantic products
with hardware batches, nor turn an extensional normal form into a registered
value or provenance-preserving rewrite. See `ONE_PRODUCT_SHARED_SLACK.md`.

## 29. The multi-input SUM conjecture yields to a global oscillation bound (2026-09-08)

After closing shared-PRODUCT capacity, research returned to the still-open
unary-SUM noisy-parity envelope. A stronger 700-restart float64 attack across
three through six inputs and several noise levels found no counterexample;
that result was not treated as proof. The useful simplification was instead
to ask whether the parity contrast of a log ratio of two affine masses can
exceed the ratio's own oscillation.

It cannot. First, a normalized nonnegative affine numerator has parity
discrepancy strictly below one. Orienting the denominator's slopes and
integrating its reciprocal yields positive alternating moments; numerator
nonnegativity bounds the offsets needed for any negative slope. Integrating
this lemma along an affine path between two positive masses proves the
log-ratio oscillation bound. The two extreme log odds then control the total
log-cosh penalty, and a one-dimensional convex minimization gives exactly
`log2-2^(1-d)[log2-H(eta)]` for every d>=2 and 0<=eta<1/2.

A simple native SUM witness leaves two adjacent contexts at Bayes in the
limit and makes the other contexts uniform. Its finite excess is <=2/K with
peak normalizer `2+K+2(d-1)K^2`; no exponential coefficient hierarchy is needed.
The infimum is strictly unattained at finite coefficients. This establishes
the strong all-SUM baseline, rather than assuming it equals unigram or
conflating it with the larger degree-below-d family.

The retained audit checks 2,178 exact denominator cases, 840 random rational
mass pairs with exact discrepancy/interpolation and outward-log bounds, the
equivalent all-noise polynomial inequality without floating ordering, and 84
finite native witnesses through eight inputs. Canonical conjecture labels are
updated to PROVED; dated exploratory evidence remains historical. General
nonuniform tasks, sharp bounded optima, acquisition, registered value/install
and AMP are not supplied by this theorem. See `UNARY_SUM_PARITY_ENVELOPE.md`.

## 30. Range bounds become an exact interaction-capacity problem (2026-09-08)

The new unbounded affine discrepancy theorem exposed a quantitative resource
question: how much range is needed to approach its sharp constant one? Keeping
the positive base in both heads gives an exact numerator optimizer at every
fixed denominator. Its Laplace integrand proves that all slopes except the
smallest may be equalized when maximizing this objective. The full arbitrary
SUM-DAG class therefore reduces to a two-variable rational maximum, with a
native witness for every point. This reduction is proved from positivity and
resource constraints, not selected as an architecture menu.

The formula yields `R(1-D)^2>=4(d-1)H_(d-1)D` and the matching fixed-dimension
asymptotic constant. A rational three-scale coefficient sequence attains that
leading law; no extra semantic action is introduced. Numerical searches helped
locate finite cases but did not certify them. At d=3, R=4, clearing denominators
and a two-square plus nonnegative-monomial certificate proves the exact value
1/40. The symbolic identity and coefficient signs are checked exactly.

At noise one-quarter, this discrepancy bound implies all-SUM CE>0.69004167.
Four native scalar PRODUCTs, composed through complementary parity indicators,
reach Bayes at the same final range and beat the entire SUM class by more than
0.1277 nats. Four is not claimed minimal, and the discrepancy optimizer is not
misidentified as a CE optimizer. The retained audit includes 960 arbitrary
rational numerator/denominator reductions, 1,944 reduced-domain checks, the
global finite certificate and rational asymptotic witnesses. Registered value,
acquisition, physical build/install and AMP remain distinct. See
`SUM_PARITY_RANGE_CAPACITY.md`.

## 31. Task loss and maximal response have different range exponents (2026-09-09)

The finite-range discrepancy theorem raised a tempting but wrong shortcut:
infer the resource cost of near-optimal CE from the cost of near-maximal
Fourier response. A direct bound instead relates the two objectives without
identifying them. Normalized affine parity discrepancy is at most probability
oscillation. Convex CE residuals at the two extreme probabilities then yield
`L>=(1-2/N)log2+(2/N)CE(1-eta,(1+D)/2)`, also simplifying the original
unbounded-envelope proof.

At zero noise, the capacity law gives an Omega(R^-1/2) loss excess, and a
finite SUM construction balances root base error against non-root dilution
to attain the same exponent. At fixed positive noise, the roots can instead
reach Bayes exactly at finite total mass 1/eta. Neutral unary contributions
then produce O(R^-1) excess. A quantitative contraction of log-ratio oscillation
supplies the matching Omega(R^-1) lower bound for the whole class. Thus noise
changes the exponent; the proof does not silently exchange the two limits.

The audit checks 1,200 rational likelihood inequalities, 900 exact interpolated
contractions, outward-log bounds, 32 exact harmonic identities and 52 native
witnesses. Minimal evidence retains selected convergence values. The rate
exponents are proved, while sharp CE constants and a uniform noise/range
crossover remain open. Registered acquisition/value, physical installation
and AMP are separate. See `SUM_PARITY_LOSS_RANGE_RATES.md`.

## 32. A bounded-range one-PRODUCT class is not closed (2026-09-09)

Research next attacked exact PRODUCT counts through positive support
certificates. That exposed a more important distinction: correct Boolean
support does not guarantee correct mass values, and exact mass exclusion need
not give any loss margin. The three-input selector
`f=x_0 z_0+x_1 w_0` has a one-PRODUCT support representation that necessarily
overcounts overlaps. Zero-face geometry proves that its exact mass needs two
PRODUCTs; a separate normalization argument proves the same exact minimum for
the conditional target `(1+f)/(2+f)` at cap three.

Yet `(x_0+epsilon w_0)(x_1+epsilon z_0)/epsilon` equals f plus a small positive
overlap term. Rescaling positively preserves cap three and gives one-PRODUCT
CE excess <=epsilon^2/16. Halving, doubling and geometric SUM chains realize
the sequence with local coefficients only in `{1/2,1,2}` and feature values
at most two. What grows is complete construction length and numerical state,
not PRODUCT count. Therefore those partial resource bounds cannot justify
compactness or a positive rejection gap.

The full SUM class remains a strong control, with exact sup-norm distance
1/12 and CE gap at least 1/576; already k=3 gives a one-PRODUCT winner. An
explicitly ordered CPU float64 run at k=54 returns the exact selector mass,
while rational arithmetic preserves its tiny nonzero error. This rejects
rounded equality as authority for a different exact algebraic class, not
registered floating execution itself. The minimal audit retains zero-face
coverage, affine-scale exclusion, actual native DAG checks, exact likelihood
deficits and the floating counterexample. No new semantic action is needed.
See `ONE_PRODUCT_BORDER_COUNTEREXAMPLE.md`.

## 33. Source annihilators admit a complete coefficient-closure criterion (2026-09-09)

The selector counterexample was traced to missing edges in the product of two
positive atom sums: an invisible contradictory term can carry a diverging
coefficient while every visible mass stays bounded. Positive-edge factors
are fixed up to one scale per connected component. Visible zero edges impose
strict scale orderings between those components, so their directed graph is
acyclic exactly when a limit factorization exists. A directed cycle gives a
polynomial identity whose two sides would converge to zero and a positive
value. Integer graph heights construct every allowed limit explicitly.

This yields the closed-mask classification: every nontrivial component must
be complete bipartite. The induced three-edge path is the general minimal
obstruction behind the selector. Literature verification identifies this as
a graph specialization of the exact-versus-limiting monomial factorization
theorems of Geiger, Meek and Sturmfels, rather than a new general toric theorem.

The mass-level result needs a second proof. Positivity bounds all visible
coefficients along a convergent mass sequence after normalizing shared head
weights. Taking a subsequence yields a coefficient-closure lift; a common
excess contraction preserves the uniform finite cap in the converse. All
alternative lifts and conditional normalizers remain existential variables.
The audit checks 23,779 given coefficient tables against independent simple-
cycle equations, all 512 three-by-three visibility masks, explicit rational
limits and five rejected certificate forgeries. It also verifies that a bad
coefficient representation can project to an exactly realizable unary mass.
The full existential mass solver remains unimplemented, and Runtime/AMP
authority remains separate. See `MASKED_PRODUCT_CLOSURE.md`.

## 34. Observable margins resolve alternative PRODUCT lifts (2026-09-11)

Research next attacked the gap between a coefficient certificate and the
observed mass decision. On the antipodal zero face of the binary cube,
positive expansions and a two-by-two identity reduce even leaking one-PRODUCT
sequences to directed-cut coefficients. The observable singleton/complement
values fix their row/column margins. The known toric moment-map theorem then
selects exactly one closure lift. A boundary-safe graph/entropy proof shows
why this selection does not erase any possible observable representation;
entropy is a mathematical coordinate inverse, not a new model objective.

For three inputs those margins cover every nonzero context. The entire
positive cut cone is consequently in one-PRODUCT closure. A transport
interval and its monotone cubic completely decide rational masses over real
coefficients, including limit-only boundary cases. The audit checks 729 mass
tables against an independent Hall condition and 729 original coefficient
tables. In 348 cases the original coefficients are outside factor closure
while the mass has an exact alternative. One rational mass needs an
irrational cubic root for its unique one-PRODUCT lift, exposing a second
scope distinction between real and finite-rational exact expressivity.

The analogous four-input universality is false. Two independent XOR masses
have equal singleton/complement margins, but their unique closure lift gives
the wrong values at other contexts. A separate positive-coefficient argument
gives an explicit all-one-PRODUCT mass distance 1/7. For the conditional task
(1+f)/(2+f) at cap four, balanced context subsets bound leakage through the
other head and reduce arbitrary normalizers back to the mass obstruction.
This yields probability separation 1/500 and CE gap 1/2000000, while two native
PRODUCTs reach Bayes. Exact arithmetic checks the transfer constants, 1,000
scalar/conditional expansions, 300 supplied lifts and seven certificate
forgeries. A float64 proposal simplified to small rational coefficients gives
a separately exact-checked one-PRODUCT upper witness with CE excess about
0.00889241 and peak normalizer 799/200. It is not a global optimum certificate.
Sharp constants and general algebraic search remain open; no
Runtime freeze, new semantic action or GPU-science permission follows.
See `ANTIPODAL_PRODUCT_MASS.md`.

## 35. Even exact support complexity fails to transfer through a limit (2026-09-11)

The next attack asked whether sharing could compress m independent XOR
interactions. A global zero-parent choice at each PRODUCT shows that P gates
give at most 2^P zero faces, regardless of sharing or nesting. The 2^m
isolated zeros of the m-XOR sum establish its exact minimum m. Attempting
to transfer such exact support arguments to approximation exposed a more
important failure.

An exponent search found a two-PRODUCT limit with a support unavailable to
every exact two-PRODUCT DAG. After deleting terms absent from all leading
contributions, it became the short identity
`(x+epsilon^3 y)((1-x)+epsilon^2(1-z))(z+epsilon w)/epsilon^3`
`=(1-x)yz+x(1-z)w+epsilon(1-x)yw+epsilon^3 y(1-z)w`.
The limit consists of two positive edges. A pure-support normal-form proof
forces any supposed two-PRODUCT realization to a product of three unary
sums; four checked zero witnesses rule that out. A three-PRODUCT graph
attains the exact mass. This is stronger than the previous selector, whose
support already had an exact one-PRODUCT representation.

The scaled family has excess cap one, feature cap two and local coefficients
only {1/2,1,2}; its SUM count grows as 10k+4. Its binary conditional Bayes
infimum is attained in the limit at cap three with explicit O(epsilon^2) CE
error, but the unrestricted conditional exact minimum is not inferred from
the scalar proof. A separate parse argument gives an explicit conservative
margin when SUM count and a positive local coefficient floor are bounded.
Repeated squaring verifies why shared gates require the exponential parse
factor. The audit retains face/identity checks, twelve actual finite-alphabet
graphs, 300 shared graphs and four rejected certificate forgeries. At k=54
float64 normalizes away positive leakage, while exact arithmetic retains it.
Search traces are not retained as proof authority. General support closure
and full physical/value reachability remain open. See
`TWO_PRODUCT_SUPPORT_BORDER.md`.

## 36. Complete exponent certificates replace finite-support enumeration (2026-09-11)

The support-border counterexample made a limit-aware search necessary.
Flattening only SUM paths gives a finite positive polynomial in the slots of
the complete fixed-PRODUCT scalar grammar. Along any finite output limit,
positivity bounds every visible monomial. The logarithms of positive limiting
monomials stay bounded while those of the others diverge. Farkas' alternative
then gives rational scaling exponents that preserve exactly the desired
support. Integer powers of epsilon construct the converse. A second linear-
image argument preserves the positive leading constants as well, proving
that every full mass limit has an a*epsilon^w path; prescribed values still
require solving for a.

The executable search enumerates leading monomial choices and requests LP
proposals. Acceptance is a separately checked integer exponent vector.
Rejection is a complete branching tree whose leaves are sparse rational
exponent identities with positive weight on monomials that must vanish.
No floating optimizer or SMT rejection is trusted. Work and reconstruction
failures return UNRESOLVED. The known two-PRODUCT border support is accepted
in five search nodes, while the one-PRODUCT two-XOR support is rejected.

For three-bit odd parity the search closes a full two-PRODUCT rejection in
2,041 nodes. Its compact stored proof can be verified without LP or SMT.
The same exponent identities are multiplicative identities in finite
coefficient values, yielding an explicit mass distance 1/18432. Three
PRODUCTs attain the exact scalar parity mass, so both exact and approximation
minima are three. At conditional noise 1/4 and cap four, a separate base/cap
argument transfers the bound to probability distance 1/147456 and CE gap
1/86973087744. This stage left the three-PRODUCT conditional boundary open;
section 37 below closes it using the scalar result.

Audits cover 544 small support classes, 32 independent symbolic expansions,
60 rational evaluations, 312 conditional-scale comparisons, seven forged
certificates, fake NaN/Inf success flags and honest budget exhaustion. The 117 KB proof is substantive
auditable evidence, not an optimizer trace. Neither arbitrary numerical mass
fitting nor complete physical/value/AMP authority is claimed. See
`PRODUCT_SUPPORT_CLOSURE.md`.

## 37. Disjoint heads close the shared parity boundary (2026-09-11)

The two-PRODUCT scalar rejection did not by itself exclude three PRODUCTs
shared between opposite parity heads. A last-PRODUCT comparison resolves this
without expanding the full multihead polynomial. Flatten only final SUM
paths and discard the head with the largest coefficient on the last PRODUCT.
At a remaining target's positive contexts, disjointness bounds that shared
contribution by the discarded head's error. Repeating on the prefix removes
k-1 PRODUCTs at error at most the sum of original head errors. A current
readout only decreases, so the errors do not need recursive doubling.

This gives a general approximation lower bound r+k-1 for k disjoint targets
each separated from the at-most-(r-1) scalar class, r>=1. Overlapping copied
heads and zero-PRODUCT unary targets demonstrate why those premises matter.
Discarding the smaller-coefficient head is also explicitly falsified.

Applied to the stored parity proof, both complementary masses need four
PRODUCTs even in closure. Base one and the minimum normalizer cap 1/eta
pin the exact Bayes excess supports; a quantitative argument keeps every
approximate normalizer instead of assuming the pinned scale. At noise 1/4
and cap four every at-most-three graph has probability error >=1/184320 and
CE gap >=1/135895449600. Four PRODUCTs attain Bayes, closing the exact and
approximation conditional count. The transfer holds for every fixed noise
eta in (0,1/2) at its minimum cap, with explicit conservative constants.

The exact audit re-verifies the stored scalar certificate without LP, checks
360 actual shared/nested graphs, repeated-square features up to 2^8192 with
compensating readouts, six exact parity constructions and 13,608 arbitrary
normalizer/contribution cases. The theorem does not need bounded hidden
features. It is a static function-class comparison, not a learner equivalence
or Runtime erasure. Larger caps, higher-bit counts and sharp loss constants
remain open. See `SHARED_DISJOINT_PRODUCT_LOWER_BOUND.md`.

## 38. A native source witness survives coefficient limits (2026-09-11)

The disjoint-output theorem made scalar all-dimension lower bounds more
valuable. A direct positive-graph argument supplies one without polynomial
expansion. At a positive context, flatten SUM paths and retain a largest
original contribution in each PRODUCT parent and the readout. Shared
PRODUCTs retain the same definition wherever reused. The resulting monomial
is pointwise dominated by the original graph and uses at most P+1 distinct
sources, by the binary graph's edge count. An explicit retained-value factor
depends only on the active source count and P. Fixed positive source ratios
then control the whole intersection of those sources' supports.

There are finitely many source intersections, so the bound passes to arbitrary
mass limits despite diverging hidden coefficients. On the full binary cube,
each positive limit point lies in a contained face fixing at most P+1 bits.
This proves exact and approximation minimum m-1 for every codimension-m
face mass. A positive explicit margin follows when P<=m-2. The assertion
that every expanded monomial is short is false: two repeated squares can
contain a four-source monomial. A consistent retained witness is essential.
Repeated-square singleton approximants also show why the positive margin
cannot be uniform in dimension.

Combining the singleton result with shared-output comparison improves the
all-label identity lower bound from N to N+d-2, N=2^d, including closure.
The comparison has a stronger pointwise surplus form: one prefix output
lies between max(0,E_i-sum_(j!=i)E_j) and E_i. At the minimum conditional
cap N+1 this gives a scalar error at most 2(N+1) times probability error,
retaining every normalizer. For d=3, P<=8 has probability distance >=1/666
and CE gap >=1/1774224. Nine is the new lower count; the exact construction
uses twelve. Section 39 below resolves the distinct exact and approximation counts.

Exact audits cover 440 actual DAGs with binary and general rational sources,
3,487 full-domain retained monomials, 27 face constructions, seven square
families, five identity decoders and 786 multiclass normalizers. The known
two-PRODUCT border passes the necessary face condition. So does parity at
P=2, while its complete exponent proof rejects closure: the local condition
must not become a sufficient certificate. Read
`SOURCE_INTERSECTION_PRODUCT_BOUND.md`. Full information, physical resources,
registered learning, persistence and AMP remain separate obligations.

## 39. Decoder approximation is cheaper than exact support (2026-09-11)

The nine-to-twelve boundary splits into two sharp answers. For exact support,
singleton PRODUCTs can be made terminal: a pure singleton feature cannot
help any other context. A minimum graph thus has eight terminal nodes and
some nontrivial auxiliaries. Complete integer enumeration of the possible
union-closed support families, modulo the 48 cube automorphisms, finds that
three auxiliaries can supply at most six singleton terminals. It checks
10,835 state orbits at that depth, with raw ordered-sequence cross-checks
of the first two levels. Four pair-indicator auxiliaries and eight final
products attain the task, proving exact minimum twelve.

The same terminalization fails for limits. Construct a common product of
`x_0+epsilon*x_1` factors, scale it by `(1-epsilon)^d`, and recursively form
every subset head by multiplying an earlier head by its next one-indicator
and amplifying by epsilon^-1. A parent's vanishing tail becomes its
descendant's leading mass. The result uses exactly N+d-2 PRODUCTs and
approaches all N=2^d singleton outputs simultaneously. Total excess is
`(1-epsilon)^d*(1+epsilon)^|T|<=1`, retaining the minimum conditional cap
N+1. This matches the general lower bound: all-dimension approximation
minimum is N+d-2, and in three dimensions it is nine versus twelve exactly.

For epsilon=2^-k the actual graph has local alphabet {1/2,1,2}, feature cap
one and 2d(k+1)+k(N-1) weighted SUMs. The conditional loss excess is at most
2d^2*epsilon^2/(N+1). At d=3 the earlier positive-value floor combines with
exact-support exclusion to prove Theta(log(1/error)) SUM cost for fixed
PRODUCT budgets nine through eleven. At most eight has a persistent loss
gap; twelve admits a finite exact graph. This gives a construction-resource
phase directly from the native grammar.

The audit evaluates 15 full finite graphs through d=6, checking 16,368
excess entries, node counts, scales and rational chi-square bounds. Two
binary64 paths attack the numerical interpretation: k=54 rounds all
predictions to the target despite positive tails; k=400 underflows the
common product and all excess heads at 111 vanish. The exact correct mass
there still exceeds 0.999. Bounded maxima do not imply a numerical bridge.
The support cache is regenerated in seconds and not retained as an artifact.
Read `DECODER_EXACT_AND_LIMIT_COMPLEXITY.md`. Higher-dimensional exact
counts, sharp finite-resource constants, larger caps and registered
value/Runtime/AMP closure remain open.

## 40. A positive amount of normalizer slack removes the exact-count barrier (2026-09-11)

The twelve-versus-nine distinction at cap nine is not stable under positive
cap slack. An uncontracted subset basis has a triangular binomial inverse.
For a common exact scale s>1, its desired excess is (s-1)+s*I. The positive
baseline (s-1) outweighs the inverse's negative terms when epsilon is small,
giving an explicit all-nonnegative readout with the same N+d-2 PRODUCTs.
Every cap above N+1 therefore admits a finite exact graph at this count.
Dyadic scale and epsilon allow a complete {1/2,1,2} SUM implementation.

A separate all-class lower argument improves the three-bit one-PRODUCT
singleton mass gap from 1/37 to 1/4. Pruning source literals zero at the
target point retains a positive quadratic whose neighbor sum dominates its
target value. Combining this with the shared-output surplus and a balanced
rescaling proves probability error at least (9-26h)/(45*(9+h)) for at-most-
eight PRODUCTs at cap 9+h, h<9/26. Thus the exact minimum is nine on
9<R<243/26, and twelve at R=9. The right endpoint is not claimed sharp.
At minimum cap the probability and CE gaps improve to 1/45 and 1/8100.

The positive-value floor also gives a joint resource inequality:
h/9+(9+h)*delta >= 2^(-S*2^p) for p in {9,10,11} and sufficiently small
probability error. The exact slack construction and the earlier zero-slack
approximation family match the resulting SUM cost Theta(log(1/(h+delta))).
For CE tolerance rho the corresponding law uses h+sqrt(rho). This treats
accuracy and normalizer allowance together while keeping actual SUM work.

The exact audit checks nine actual dyadic graphs, including a scale slack
2^-40, 960 scalar source-pruning cases, 1,050 arbitrary-normalizer surplus
and rescaling cases, and four invalid coefficient proposals. Negative
inverse coefficients cause rejection of that proposal, not a semantic
patch. Read `NORMALIZER_SLACK_DECODER.md`. Larger-cap transitions, sharp
scalar and construction constants, and complete physical/value/AMP paths
remain open.

## 41. Conditional universality has an exact PRODUCT count (2026-09-11)

The decoder's larger-cap endpoint is controlled by a different invariant.
Every static mass table lies in the span of the unary sources and its
PRODUCT feature columns. Normalization preserves rank, including under
prediction limits with diverging normalizers. The N-label identity-noise
table on d bits has rank N=2^d, giving P>=N-d-1 and a cap-independent
probability gap below this count. This is a static table argument, with no
claim about recurrent state dimension.

A matching positive construction realizes every strictly positive finite
conditional table. Build all monomials of degree at least two once, then
multiply target row T by C*L^|T|. Sufficiently large explicit C,L make every
multilinear excess coefficient nonnegative. Rational tables allow integer
scales and coefficients, implementable by finite {1,2} SUM chains. Thus
the worst-case exact and approximation count is exactly 2^d-d-1. The result
transfers cost to normalizer range and SUM/encoding work; it does not provide
free acquired target information or a registered value path.

For the three-bit identity task, a smaller exact construction in the same
four-monomial bank uses normalizers 9,15,36,108 by Hamming weight. Four
PRODUCTs are therefore optimal at every cap at least 108; at most three
has probability error >=1/72 and CE gap >=1/20736 at every cap. Coordinate
permutation averaging and a four-term nonnegative dual prove cap 108 is
optimal for this bank with all complementary unary readouts retained. The
bank-specific dual is explicitly not a full variable-parent range proof.

The rational audit checks 21 positive-target graphs, nine integer-alphabet
graphs, 980 exact mass entries, 60 original DAG and prediction ranks, 45
exact null vectors, five sharp rank-relaxation examples and the cap-108/324
graphs. Forged duals and invalid tables are rejected; fixed-bank rejection
is paired with a legal twelve-PRODUCT full-class witness to attack false
completeness. Read `CONDITIONAL_PRODUCT_UNIVERSALITY.md`. Intermediate cap
thresholds, fixed smaller label alphabets and total physical/value costs
remain open.

## 42. The larger-range parity endpoint needs only two PRODUCTs (2026-09-11)

The fixed-cap four-PRODUCT parity theorem cannot be extended to all ranges.
One PRODUCT of unary SUMs supplies A=XOR(x,y), and a second supplies A*z_1.
With odds r>1, explicit positive readouts reproduce noisy three-bit parity
at cap (r+1)*(r^2+r-1). At noise 1/4 this is 44, with integer coefficients
2,8,32 that have finite {1,2}-SUM implementations. No complementary XOR
source or extra semantic action is inserted.

Every at-most-one-PRODUCT graph has sub-parity degree, so the existing
full-class moment argument gives probability error at least 1/2-eta and
uniform CE excess at least (log(2)-H(eta))/4 at every range. Two is therefore
the exact and approximation minimum above the displayed cap, whereas four
remain necessary at the minimum cap r+1. A symmetry reduction retaining
all unary readouts and an exact dual prove the new range formula is optimal
for the fixed A,A*z_1 bank. They do not decide the full variable-parent
two-PRODUCT range threshold or an intermediate three-PRODUCT phase.

The rational audit checks seven noise odds, the complete integer-alphabet
graph, 160 arbitrary one-PRODUCT moment/order examples, 100 dual-scale
identities and 21 invalid dual multipliers. Read
`TWO_PRODUCT_CONDITIONAL_PARITY.md`. This is an expressivity result under
explicit scales; target acquisition, registered value construction and the
complete physical/numerical path remain separate.

## 43. Fixed-label universality needs fewer PRODUCTs but adaptive feature values (2026-09-11)

The N-label rank witness does not decide fixed binary-label capacity. A
complete normal form gives a different lower bound: flatten SUM paths into
the affine unary span and all earlier PRODUCTs. P PRODUCTs with k readouts
give at most P^2+(2d+k+1)*P+k*(d+1) real parameters. Counting monomials after
clearing the prediction denominators proves an algebraic identity whenever
this is below N*(k-1), N=2^d. Its closed zero set cannot contain every
positive target. This excludes approximation as well as exact universality,
without assuming bounded coefficients or bounded SUM work.

A positive block factorization matches the lower order. After the known
target is positively scaled, build monomials separately on two coordinate
blocks and group each head's excess coefficients into cross-block PRODUCTs.
The count is (k+1)*2^a+2^(d-a)-d-k-2, or use the full N-d-1 bank when cheaper.
Thus exact and approximation universality both have order
Theta(min(N,sqrt(N*k))). Fixed labels cost Theta(2^(d/2)); k>=N retains the
exact count N-d-1. The construction keeps the N*k coefficient information
in its SUM weights, and range and encoding costs can still be large.

Freezing the numerical feature table changes the result. A span of dimension
r admits only k*r-1 normalized readout parameters, requiring
k*r-1>=N*(k-1) for universality. Every frozen binary bank needs at least
N/2-d PRODUCTs, while adaptive feature values admit the smaller construction.
At d=8 the comparison is at most 44 versus at least 120, and at d=20 it is
3560 versus at least 524268. This is a universal fixed-bank lower bound,
not a weakened baseline. A fixed skeleton with target-dependent SUM parent
weights attains the upper, so topology change is not proved necessary.

The exact audit verifies 20 complete graphs through d=9, 5,912 probability
entries, five integer-alphabet graphs, 100 arbitrary shared-DAG normal forms
and 180 finite bound cases. A fixed three-PRODUCT bank has determinant
obstruction 1/16 to a target realized by two legal variable-feature PRODUCTs
at cap 44. Read `FIXED_LABEL_PRODUCT_CAPACITY.md`. Sharp small-class counts,
including binary three-bit universality between two and three, and full
range/information/value/physical costs remain open.

## 44. Frozen conditional universality is decided by exact supports (2026-09-11)

Attacking the remaining binary three-bit capacity question exposed a simpler
obstruction to freezing features. A proper feature span has a nonzero common
annihilator. Positivity of all normalizers forces equal prediction means on
its two sign supports. A noisy Boolean target separating them has probability
gap 1/4 and uniform CE gap at least 1/(4N). Frozen universality therefore
requires the full N-dimensional span, improving the previous N/2-d binary
PRODUCT bound to the exact minimum N-d-1. The known monomial bank attains
it for every fixed number of labels. Adaptive three-bit binary universality
still lies between two and three, while a frozen universal bank needs four.

The argument extends to a complete criterion, including full-rank banks.
Partially color contexts with k labels. If every feature touching this subset
touches at least two colors, correct feature mass is bounded by a finite
multiple of wrong-color mass. A highly confident but strictly positive target
then has a cap-independent gap. Conversely, a Farkas infeasibility witness
for any positive target selects negative entries row by row, producing just
such a coloring. Thus absence of a partial coloring is equivalent to both
exact and approximate all-target universality of the frozen readout class.
This decision depends only on supports, not on the positive magnitudes.

Neither full span nor full-domain-only color checks suffice. The two-bit
features xy and (1+x)(1+y) span the same space with unary sources, but only
the first bank is universal. The second has a noise-1/4 XOR gap of 7/36.
The two frozen XOR/XNOR features together with unary sources give every pair
indicator, making the bank universal for two and three labels but not four.
A single different PRODUCT realizes a four-label target excluded from that
entire two-PRODUCT bank at every range. An additional construction shows
that every finite positive validation collection can pass exactly in some
small positive-shift bank that remains globally nonuniversal.

The audit independently checks 248 support models, 81 rational target Farkas
duals, 66 exact LP primal reconstructions, 80 arbitrary-DAG annihilators and
the scope counterexamples. A common shift 2^-19 fits 40 positive targets
exactly while retaining its obstruction. Read `FROZEN_FEATURE_UNIVERSALITY.md`.
The result replaces the weaker frozen-bank comparison with 44 versus 247
at d=8 and 3560 versus 1048555 at d=20. It does not reverse the quantifiers
into one bad target for every variable-parent program, nor price finite
range, value acquisition, complete physical construction or numerical paths.

## 45. Complete conditional limits need cap-aware paths, not a new primitive (2026-09-12)

The next attack separated variable-feature closure from frozen support
decisions. Applying the positive-polynomial lift to the proof coordinates
r_x*M_(x,j), with r_x=1/T_x along a convergent prediction sequence, shows
that every unrestricted-range conditional limit has an original-coefficient
path a*epsilon^w. Rowwise minimum exponents determine support, but all tied
leading amplitudes determine the actual probabilities. This covers different
diverging normalizer rates across contexts. The auxiliary reciprocal never
enters the native model.

A finite cap exposes a new completeness failure. Positive monomial mass
paths approach their finite limits from above, so a saturated cap may reject
every finite point. The three-bit decoder at cap nine makes this decisive:
any feasible pure monomial path with at most eleven PRODUCTs would have no
positive tails at all and thus be exact, contradicting its exact minimum
twelve. Nine PRODUCTs nevertheless approach the target at that same cap.

The missing step follows directly from the positive readout. If D bounds
the positive mass-tail coefficient sum, append the common final excess
weight beta=(R-k)/(R-k+D*epsilon). Every finite point now satisfies the
original cap R and converges to the required masses, with no extra PRODUCT.
The probability error is at most 2D*epsilon/k and uniform CE excess at most
4R*D^2*epsilon^2/k. The decoder has D=7. Thus bounded mass lifts plus this
ordinary final SUM operation characterize the complete finite-cap closure;
restricting the coefficient path family would have made a false exclusion.

Continuing the resource audit produced two general results. All hidden
activations of any finite graph can be rescaled into a bound already met by
its sources and final excesses, retaining PRODUCT count and exact outputs
when SUM scaling is free. Independently, rounding every nonnegative
coefficient down to dyadics and expanding those coefficients into local
{1/2,1,2} SUM chains preserves normalizer and common activation upper caps
and has the same prediction closure. Construction/encoding costs and small
nonzero values remain; bounding only peaks and the local alphabet cannot
repair the nonclosure. An explicit shared graph's hidden peak falls from
1048576 to one without changing either output or its two PRODUCTs.

The shifted-bank example also has a sharper quantifier consequence. Every
fixed positive t in (t+x)(t+y) is nonuniversal, with the same support pattern,
yet the union is exactly universal for every finite output alphabet. A
single small t can fit any finite mixed-alphabet target collection. Frozen
colorings therefore cannot exclude the complete variable-value family.

The independent rational audit checks 625 small exponent configurations,
64 shared/nested/squared DAG paths and their cap contractions, 38 exact
activation rescalings, 144 dyadic graph expansions and 30 exact targets
with 2/3/5 labels in one shifted bank. It rejects wrong leading values,
wrong supports and false cap premises. Read `CONDITIONAL_COEFFICIENT_PATHS.md`.
Generic phase/amplitude search, sharp full resource costs and registered
value/physical/AMP paths remain open. Foundation semantics are unchanged.

## 46. SUM accuracy follows an arithmetic trichotomy (2026-09-12)

The complete path theorem made it possible to ask for the cost of every
fixed-PRODUCT approximation, rather than another special decoder. A fixed
mass path, cap contraction and hidden rescaling have coefficient magnitudes
bounded above and below by powers of epsilon. Relative downward rounding
therefore needs O(log(1/delta)) coefficient bits. Positive halving/Horner
graphs convert this into O(log(1/delta)) SUM nodes and edges while retaining
the original normalizer and activation caps. The result is pointwise in
the given target and path; it does not acquire either for free.

The first matching lower used rational arithmetic. All local graph masses
have denominator dividing L_s^(2^P)*2^(S*2^P), where L_s is the common
source denominator. A rational target with denominator B is either exactly
equal or separated by at least 1/(B*R*D), for that mass denominator D.
Shared squaring attains the 2^P exponent and must be counted. Positivity
also bounds the visible source-monomial coefficients, making the observed
mass set finite at fixed P,S,R even with arbitrary finite SUM arity.

The lower extends beyond rational tables. For fixed algebraic data, clear
their fixed denominators in a prediction residual and take its field norm.
It is a nonzero integer; the other embeddings are bounded using the positive
coefficient bound in the actual real embedding. This gives error at least
C_*2^(-e*S*2^P), e the fixed field degree. The resulting trichotomy is:
positive closure gap, eventual minimum exact local SUM count, or
Theta(log(1/delta)) for nonexact closure points. The same order holds for
inverse CE tolerance. This proves an asymptotic classification, not an
implemented classifier for arbitrary target tables.

Several attacks clarify what the law actually says. Source one and target
(5/8,3/8) at cap 8/3 force the nondyadic excess 2/3: real zero-PRODUCT
exactness coexists with local-alphabet nonattainment at every finite PRODUCT
count. Any positive cap slack restores exact local realization. Letting
PRODUCT count grow also changes accuracy cost. A positive geometric-product
construction has 2n-1 PRODUCTs, 2n+3 SUMs and error
3*tau/(32-8*tau), tau=2^(-2^(n+1)), with the same cap and activations <=1.
It uses O(log log(1/error)) graph nodes; its direct exact significand still
has Theta(log(1/error)) bits. Factorially sparse dyadic series give separate
transcendental-source/target counterexamples to a general-real logarithmic
lower. Removing the cap with unpriced SUM arity also admits a constant-node
limit on a strictly positive rational task.

The audit verifies 120 rational shared graphs and relative perturbations,
192 exact norm/gap identities on 32 Q(sqrt(2)) graphs, corrected decoder
quantizations, six arithmetic-cap comparisons, eight geometric precision
graphs and the hypothesis counterexamples. Its generic decoder quantizer
does not replace the stronger specialized 13k+6 construction. Read
`SUM_ACCURACY_COMPLEXITY.md`. Sharp joint node/precision costs, efficient
generic phase/amplitude classification and the registered physical/value/
AMP path remain open. The proof adds no FP semantic primitive.

## 47. The dyadic cap boundary decides total-node accuracy (2026-09-12)

The fixed-P resource law left open whether the geometric PRODUCT example
was exceptional. On the complete binary source domain, arbitrary finite
PRODUCTs make all context singletons constructible. The remaining exact
local-alphabet question becomes a precise mass-scale problem. A rational
target requires R>=R_0=max_x 1/min_j Q_(x,j). At a critical row, T_x=R is
forced and every mass R*Q_(x,j) must be dyadic. Off the critical rows, a
positive interval of scales contains a legal dyadic scale. This completely
decides the unrestricted finite-node class: a gap below R_0, exactness
above it, and a critical-mass dyadic test at the minimum cap.

The distinction has small counterexamples. Integer cap four still fails
for the three-label row (1/4,1/3,5/12), whose forced masses are
(1,4/3,5/3). Checking one good critical row cannot erase a second bad one.
Conversely, forcing noncritical normalizers to the cap rejects a valid
two-row model whose legal totals are four and 5/2. The complete criterion
retains both every critical entry and every noncritical scale interval.

Every rational excess coefficient a/b has a positive geometric approximation
from below: choose dyadic seeds a/H and t=1-b/H<1/2, then shared squaring
and products produce (a/b)*(1-t^(2^n)). Applying this computed constant to
a context singleton costs another native PRODUCT. All finite masses remain
below their feasible rational limits, so the original normalizer cap and
activation bound max(1,R-k) are preserved. Total graph size is O(n) for a
fixed table, giving O(log log(1/error)) accuracy cost. The rational lower
bound from XVII.29 and S*2^P<=2^(S+P-1) give the matching total-node order
for every nonattained target, including uniform-context CE tolerance.

The exact audit compares 3,067 target/cap cases against direct forced-mass
tests, evaluates 1,995 full exact native graphs and 72 geometric graphs,
checks all generated scalar values and their actual PRODUCT applications,
and rejects six false/scope-mismatched certificates. The three-bit identity
target at cap nine has a 12-PRODUCT, zero-SUM exact witness; the same
certificate is explicitly rejected for a P=9 claim. Read
`DYADIC_CAP_AND_TOTAL_COMPLEXITY.md`. The full target encoding and singleton
bank remain in construction cost. Sharp separate-budget Pareto constants,
minimum exact graph sizes, other source/number classes and registered
physical/value/numerical paths remain open.

## 48. PRODUCT, SUM, range and precision meet in one resource envelope (2026-09-12)

The total-node theorem was attacked through its unpriced arity and direct
numerical representation. A single dyadic seed followed by squaring makes
an extremely fine grid; explicitly repeating its scaled context indicators
in final SUMs gives the sharp node leading term
log2(log2(1/error))+O(1), but Theta(1/error) incoming edges along that family.
This strengthens the node theorem while preventing it from masquerading as
a physical-work theorem.

One common rational denominator supplies a different, binary-arity native
construction. Positive updates g'=g+g*t and t'=t*t cost one SUM and two
PRODUCTs per doubling of tail precision. Its node/edge counts are
Theta(log log(1/error)), and its fully materialized direct numerical bits
sum to Theta(log(1/error)). The matching bit lower comes from a critical
nondyadic forced mass, which remains separated from every b-bit dyadic mass
by a constant times 2^(-b), irrespective of node or exponent budgets.

Retaining the final tail square gives a useful exact invariant, D*g+tau=1.
For ideal excess c=a/D, the entirely positive expression
E=a*g+(D+a-1)*tau makes the full mass a common factor
1+(D-1)*tau times its ideal. Thus every row predicts Q exactly at positive
cap slack, with no internal subtraction. The mass lower and this repair
unify range h and accuracy delta into h+delta. Necessary S*2^P and direct
precision bounds are logarithmic in its inverse; a separate-budget grid
upper matches up to fixed construction overheads and precision constants.
The optimal joint node/edge order is double-logarithmic and direct numerical
bit volume is logarithmic. Uniform-context CE uses h+sqrt(rho).

The exact audit evaluates 90 separate-budget envelope graphs, 92 positive
tail repairs, 100 binary-arity approximants and 30 expanded-edge graphs;
it rejects 100 insufficient-slack executions and checks 1,533 small floating
mass rows. The binary64 rounded-equality witness retains exact error
1/48038396025285288 after mathematical normalization of its stored masses.
Read `NODE_EDGE_PRECISION_ACCURACY.md`. The result is a complete scoped
resource law, not a general language-model law or Runtime release.

## 49. Freeze ERC-1 and return to the complete Runtime (2026-09-12)

The research direction now explicitly uses the joint resource law as the
theoretical stopping point. `EXPERIMENT_RESOURCE_CONTRACT.md` freezes ERC-1:
its immutable run/claim fields, separate PRODUCT/SUM/edge/range/precision
accounting, information/value/physical continuity, strong comparisons and
the release order Runtime -> actual AMP bridge -> RTX 3090 experiments.
The contract retains the exact decision scope of the new upper/lower law
and the existing identity/parity/numerical counterexamples.

This is a specification freeze, not a claim of executable closure. The
ReferenceCompilerRuntime recovery boundary and science HOLD remain unchanged.
The remaining static special cases and sharp finite constants are parked.
Implementation/experimental correctness may reopen Foundation when it finds
a real semantic counterexample; search cost, uncertainty or insufficient
resources do not justify extending semantics or continuing static casework.

## 50. Restore the Runtime's owned native construction segment (2026-09-12)

After the ERC-1 freeze, inspection confirmed that the repository still had
no executable Runtime and retained only six recovery modules, including
the already-audited unsafe helper authorities. Reconstruction now starts
from the actual construction chain rather than reinstating certificate
booleans or reviving the old R4.2 candidate menu.

The new native program representation has typed source/SUM/PRODUCT/delayed
bodies and parameter slot references; values cannot be smuggled into its
skeleton. Runtime first allocates zero slot state and then executes its
fixed registered initializer. Exact full-domain or conservative inductive
source/state bounds retain all heads and normalizers. A work-limited exact
calculation or loose bound stays UNRESOLVED. The actual packed reference
buffers have immutable roles, owners and reference counts; coexistence
peaks and cumulative work survive failure or explicit candidate retirement.

The endpoint audit executes nine existing resource fixtures and 80 shared
DAGs, independently checks 320 complete-context exact evaluations, and
model-checks 1,500 ownership transitions. Injected backend failure cleans up
the partial physical build without erasing spent costs. Helper booleans
cannot authorize the unimplemented install path. Read
`scripts/audit_reference_construction.py` and the source README.

This is a coherent first Runtime segment, not completion of the objective.
The complete manifest, information/data-use, ordinary learner/profile
continuation, grammar search, typed proof authority, fresh persistence,
full host/device accounting, AMP and atomic install remain to be connected.
The packed reference payload/operation profile is explicitly narrower than
actual host/GPU resources. Foundation and ERC-1 remain frozen; science HOLD.

## 51. Execute ordinary learning through owned causal prefixes (2026-09-12)

The recovered learner let callers choose commit timing and accepted mutable
callbacks; the old information helper accepted an arbitrary answer callback.
Those interfaces could not establish registered value reachability or causal
data access merely by being placed behind a Runtime class. They are now
replaced by a declared exact mean-CE projected-SGD learner, fixed update
units, causal source reads and Runtime-owned registered moment queries.
No new native semantic action or static special case was introduced.

Runtime predicts on every active reference lineage before target reveal.
It retains separate states after observation and after optimizer commit,
including complete accumulators and positive delayed histories. All current
successors are published together only after their physical coexistence
and full-domain range checks pass. A candidate failure after deployment's
successor has been computed leaves both published input states unchanged.
The already revealed target, executed temporary states, buffers, work and
peak remain; this recovery interface then halts rather than replaying an
observation as unread. Range failure does not silently alter the optimizer.

An additional erasure attack found that retaining an execution trace but
freeing its sole program would leave evidence without the graph it described.
Historical evidence now acquires an actual shared code lease and keeps its
program registry entry after learner retirement. Query failures likewise
retain proposal-use facts and spent work. These are implementation boundary
repairs, not counterexamples to Foundation.

The registered information interface is explicitly raw, exact revealed
train/online access. Finite query precision is enforced per query without
pretending that raw records and optimizer state carry no other information.
Current-target source atoms, split relabelling, repeated stream identities,
shortened newborn update units and caller-provided query/commit controls are
rejected. No stochastic guarantee is inferred from the deterministic stream.

The new endpoint audit verifies 960 exact gradient vectors against separate
forward differentials on 80 native DAGs, all 64 short binary context/target
streams with paired reference lineages, 246 quantization level/tie cases,
causal history and injected post-target backend/work/memory failures. The
existing XVII.5 direct-PRODUCT fixture now executes 512 deterministic online
events through Runtime. All 32 committed values agree with its independent
scalar recurrence; its existing scoped CE bound crosses at update unit 13.
This verifies a registered value path rather than merely constructing its
fitted endpoint. It grants no fresh persistence, unknown-population or AMP
claim, and does not relabel 16 profile labels as 512 fresh observations.

Historical unsafe proof/bridge signers are removed from the current callable
surface. Their original modules, including the old learner dependency, still
reproduce all four false authorizations when loaded from Git in an isolated
audit namespace. Current reserved authority modules import but have no
implementation; this does not close their gates.

Read `docs/REFERENCE_RUNTIME_CONTINUATION.md` and
`scripts/audit_reference_events.py`. Complete manifest/profile/grammar/proof,
stochastic persistence/error state, full host/device accounting, certified
float64/actual AMP and atomic installation remain open. Foundation/ERC-1 are
still frozen; the next research remains Runtime -> AMP -> RTX 3090 science.

## 52. Make profile a paid, auditable newborn value path (2026-09-12)

The ordinary event endpoint left a distinction that matters to the original
XVII.5 result: 512 deterministic online positions are not the same physical
construction as 32 passes over 16 retained labels. The new preregistered
`ProfileSpec` and Runtime constructor now execute the latter explicitly.
The profile fixes original IDs/order/pass count, uses the existing ordinary
optimizer, and charges every actual read, prediction, update and range check.
It cannot be supplied as a fitted parameter dictionary or applied over an
existing ordinary lineage.

Replay retains each observation's original logged causal source context.
Its local clock is distinct from the shared exogenous cursor. Positive
recurrent buffers continue through the declared passes; complete parameters,
accumulators, optimizer count and delayed state survive final attachment to
the newborn ordinary boundary. This is an executed value constructor, not
an equivalence assertion or a new architecture-semantic operation.

The public endpoint reproduces all 32 dyadic commits of the existing
direct-PRODUCT scalar recurrence using only 16 retained labels; the ordinary
cursor stays at 16 and the old CE upper crosses at update 13. A second
512-event profile preserves the existing dormant-factor face's five zero
coordinates. It does not jump to an expressive encoded witness that its
registered gradient path cannot reach. The deployed uniform predictor is
the empirical optimal unigram on these balanced labels, not an intentionally
weak baseline, and no global one-PRODUCT rejection is inferred.

Sixteen exhaustive two-event binary input/target streams provide 64
independent replay checks. Reordered causal records, recurrent state
attachment, illegal split/horizon/parameter inputs, public-control
interleaving, backend failure after partial execution, and actual work and
coexistence caps are audited. Failed profiles close the newborn owner while
retaining code for evidence, repeated original data-use IDs and spent work.
They create neither exogenous events nor fresh persistence observations.

Read `scripts/audit_reference_profiles.py` and
`evidence/minimal/FP_REFERENCE_PROFILE_RUNTIME_AUDIT.json`. Next integrate
complete native grammar search with explicit decision classes and typed
proof authority. The full manifest, stochastic persistence/error state,
host/device accounting, float64/AMP bridge and atomic installation remain
open. Foundation/ERC-1 remain frozen and RTX 3090 science remains HOLD.

## 53. Close an executed native reference decision class (2026-09-12)

Native construction and paid profiles are now connected to a complete
finite ordered syntax search through the same Runtime. The grammar has
separate node/SUM/PRODUCT/edge/slot caps and retains repeated sources,
edges, heads, tied/unused slots, shared PRODUCT descendants, typed delayed
bodies and every binding order. A coverage proof derives its exhaustive
children and roots directly from Program validation. An explicit checked
cursor owns visited ordinals; the solver cannot declare a missing region
closed or substitute an unrelated comparison row. No score/gradient/support
quotient suppresses an unhelpful prefix's descendants.

The exact decision is deliberately explicit: fixed-state empirical CE on
registered initializer/profile endpoints at one ordinary boundary **plus
the actual deployed baseline**. Every member is actually constructed and
compared using its logged original objective contexts. Exact positive
likelihood products order the common CE objective without a floating log.
This is neither arbitrary-value optimization nor a population or future
trajectory theorem. The fixed class specification and current Runtime
context jointly identify the comparison.

Two proof weaknesses were attacked during implementation. Trusting the
solver's best flag would admit a wrong selector. Checking only that a
claimed score dominates all alternatives would admit an inflated score
unbound to any live state. Issuance now rebinds and rescores every retained
endpoint, independently verifies the maximum, and requires the winning
score to equal that of its actual owned program and complete learner.
The type has one fixed proposition; altered, cross-Runtime, wrong-class or
stale tokens are rejected. A full syntax traversal with one unresolved
row, or without enough work for final verification, remains UNRESOLVED.

The cursor/row history has real packed Compiler residency. Old and new
workspaces coexist before replacement; nonwinners retain owned code for
their evidence. Cancellation was kept from freeing history still exposed
by snapshots. Partial backend failures retain paid reads, executed evidence
and spent work while closing speculative learner ownership. These are
repairs to execution/proof boundaries, not Foundation counterexamples.

An independent Cartesian-product oracle checks nine complete grammars,
14,860 program/class cases and 3,120 saturated count calculations. Actual
Runtime search executes all 110 members of a registered-profile class,
440 replay events (eight endpoints change), and ten recurrent/binding
programs, with independent exact endpoint/likelihood checks. A separate
587-program XOR audit finds a PRODUCT descendant with likelihood 1/12
while all shorter prefixes and the complete same-class P=0 portion stay
at 1/16, also the empirical optimal unigram. Its explicit zero-slot scope
is not an unrestricted SUM exclusion or a neural model-science comparison.

Read `theory/proofs/ORDERED_NATIVE_REFERENCE_CLASS.md`,
`scripts/audit_reference_search.py` and
`evidence/minimal/FP_REFERENCE_SEARCH_AUDIT.json`. The successful result is
`REFERENCE_CLASS_EXHAUSTED`; it cannot authorize equivalence, persistence,
AMP or installation. Complete ERC-1 registration, stochastic fresh
persistence/error state, host/device accounting, certified reference/AMP
and atomic install remain the next integration frontier. No full Runtime
freeze or RTX 3090 science authorization follows; static expansion remains
parked and Foundation/ERC-1 stay frozen.

## 54. Reject numeric coercion as proof identity (2026-09-12)

Independent review found a public-interface counterexample to the new
typed reference proof admission. Dataclass equality alone accepts equal
Python floats, integers and Fractions despite their different encodings.
More strongly, a caller-created Fraction subclass can represent likelihood
one while overriding equality to match an issued likelihood of one quarter.
The verifier then returned the supplied altered proof. This required no
Runtime state mutation and no replacement of its solver.

Reference proof construction and admission now require exact declared
integer, Fraction and string field types and their value domains before
comparing with retained issuance. Identical typed copies remain valid;
numeric coercions and subclass comparison behavior are rejected. The
scoped search regression and full finite search audit pass. This is a
concrete implementation mismatch under the existing typed-state principle,
not a reason to change Foundation or expand the static theorem catalog.

## 55. Execute fresh reference evidence with bounded lower wealth (2026-09-12)

The next implementation obstacle was continuous statistical evidence under
finite numerical resources. Multiplying exact rational factors forever is
unnecessary for the existing linear e-process: a downward dyadic update is
pointwise below the exact nonnegative factor, so it preserves the declared
conditional mean-null supermartingale inequality. Stopping at first crossing
keeps retained wealth below `2/alpha`. This is a validity statement; rounding
can lose all power and does not inherit XVII.6 sample constants.

Positive base and a native normalizer cap supply the needed bound without
an architecture menu: `K=max_y (R-sum(b)+b_y)/b_y` bounds every candidate/base
probability ratio. Fixed-term rational atanh expansions enclose logarithms;
signed comparisons, intermediate integers and downward floors are guarded.
Exhaustion cannot invoke an unlimited exact or floating-point fallback.

Runtime now owns the entire reference evidence identity: admission before
context ingress, fixed future epoch schedule, both complete continuous
learners, sealed pre-target scores, paid workspaces/events, lower wealth and
global alpha. Every actual admission spends a new allocation before fallible
materialization. Failed admission, finite noncrossing, retirement and
cancellation never refund it. Multiple preadmitted identities may legally
score the same fresh event with separate allocations; ordinary post-score
learning is also legal. A later profile/rebuild cannot recycle past IDs or
inherit wealth. Epoch boundaries and optimizer commits remain separate clocks.

Failure handling required an explicit probabilistic boundary. A null
conditioned on computation succeeding is insufficient: success can select
contexts or targets. The proof states a bounded score on all branches of
the pre-epoch law, and carefully distinguishes stopped continuations from
uninterrupted-trajectory nulls. Failed evidence terminates its identity
(mathematically killed to zero), retaining the old wealth only as history.
An unexpected failure during ordinary execution halts that whole prefix;
neither skipped losses nor a mismatched successor can inherit a live crossing.
No external producer's stochastic law is inferred from a test tape.

The kernel audit checks 1,586 exact floor/threshold cases, six conditional
null trees and 256 shared-observation/global-alpha paths. It reproduces
false guarantees from upward rounding, outcome-dependent bets, skipped
losses and refunded allocations. Numerical evidence adds 600 exact log-tail
checks with independent Decimal diagnostics, 12,321 signed-order cases and
1,385 floor checks. The actual Runtime audit independently verifies sealed
scores across six changing optimizer commits, actual crossing/noncrossing,
32 complete fair-label paths with 31 exact conditional wealth inequalities,
freshness, shared observations, alpha ownership and numeric/work/memory/
backend failure boundaries. These are execution audits, not model science.

Read `theory/proofs/OWNED_REFERENCE_PERSISTENCE.md` and the three new minimal
numerics/kernel/Runtime evidence files. The result `REFERENCE_CROSSED` is
conditional reference evidence only. Actual paired reference/AMP evidence,
complete ERC-1 physical enforcement and atomic installation remain open;
Runtime is NOT FROZEN and RTX 3090 science stays HOLD. Foundation and ERC-1
remain frozen, and static special-case expansion remains parked.

## 56. Execute binary64 trajectories and certify their finite prefixes (2026-09-12)

The numerical bridge need not begin with an error recurrence proved for
every possible future. A more direct scoped result follows by induction:
execute two registered continuous trajectories, check their complete state
and score relation at every required microphase under fixed tolerances,
and retain only the accepted finite prefix. Failure stops its extension;
a later close endpoint cannot reconstruct a skipped or failed phase. This
does not establish an unexecuted horizon or a whole-domain floating bound.

The Runtime now implements that result for actual CPU binary64 beside the
exact reference learner. Every initializer cast, ordered native operation,
reverse-gradient incidence, accumulator update, optimizer step and optional
grid projection is executed through a fixed scalar backend. A guarded exact
binary nearest/ties-even oracle checks actual result bits. Both zero signs
remain represented. The finite path runs its own profile from the original
retained observations; it is never replaced by a cast of the fitted exact
endpoint. Both paths' current buffers and all accepted numeric phases have
real packed residency and prepaid reference work.

The readout relation keeps three objects: exact mathematical normalization
of decoded stored masses, the rounded normalizer and the actual final
division output. Displayed equality cannot replace the first object. The
existing precision fixture now reproduces this distinction through Runtime:
raw output exactly equals the reference target while the proper stored-mass
probability gap is `1/48038396025285288`. A zero probability tolerance rejects
that forecast. Full delayed queues and partial gradients are similarly
checked instead of comparing only current parameters or predictions.

Adversarial integration exposed two classification/ownership defects.
An internal numerical executor ContractError was initially caught as native
admissibility rejection; it now records and propagates EXECUTION_FAILED.
A phase was initially marked CHECKED before its packed evidence allocation;
an actual tight byte cap left that successful-looking row unowned. A failed
retention now leaves only an explicitly terminal diagnostic, never CHECKED
evidence. A final combined-failure audit found that evidence exhaustion could
also hide an earlier unexpected backend failure. The diagnostic now retains
both causes and preserves EXECUTION_FAILED. Missing registered scalar
operations also block a close endpoint.
The binary decoder now checks its integer budget before constructing its
largest raw rational denominator. These are implementation repairs under
the existing frozen Foundation, not new architecture primitives.

The primitive audit checks 10,232 small-format rational cases, 513 actual
binary64 nearest-neighbor results and 594 grid floors. The Runtime audit
executes 64 full three-event streams, 384 paired-lineage events and 128
commits, with 1,024 bitwise checks against an independent direct-float
interpreter. In 406 coordinates the executed finite value differs from a
cast of the exact endpoint. Six profile events from two original labels
give 20 further differences. Sixteen floor-grid streams add 192 phase
checks. Numeric/work/memory/tolerance failure, signed zero, stale crossing,
profile/recurrent state and fake endpoint regressions pass. Existing
construction, ordinary-event, profile, search and persistence regressions
also pass; no target GPU execution was performed.

Read `theory/proofs/OWNED_FLOAT64_PREFIX.md`,
`evidence/minimal/FP_BINARY_ARITHMETIC_AUDIT.json` and
`evidence/minimal/FP_FLOAT64_RUNTIME_AUDIT.json`. CPU reference protocol
closure precedes actual target AMP validation. The old 47 labels survive
as a catalog, not the executable registry, so its historical pass count
cannot be reused. Complete ERC-1 physical enforcement, four-path/dual
persistence protocol, actual target AMP and atomic installation remain
open. Runtime remains NOT FROZEN, science HOLD, and static expansion parked.

## 57. Close the CPU same-path persistence gap with current-domain bounds (2026-09-12)

The next obstacle was statistical, not an additional static model case.
An observed-context numerical bridge cannot justify a pre-context null that
quietly conditions away failed computations. The current finite predictor
needs a whole-domain bounded definition even at a failing attempt.

Positive SUM/PRODUCT and monotone nearest rounding supply that premise.
The new `float64_range.py` executes the registered ordered forward on source
upper endpoints or every declared finite source row and the complete delayed
box. It independently bounds exact decoded mass sums and rounded normalizers,
requires positive rounded bases/divisions, and checks the delayed invariant.
Bounds are tied to current raw theta; optimizer changes cause a paid renewal
before the persistence identity can extend. Inconclusive bounds yield
UNRESOLVED. This is a generic Runtime proof computation under frozen semantics.

The same persistence engine now executes both `exact-reference` and
`binary64-stored-mass` CE. Both score only their own deployed/candidate pair
from sealed predictions, use separate lower wealth and pay separate alpha
from one global budget. They share fresh events without an independence
assumption. A paired CPU result requires matching four-learner starts,
lineage identities and schedules, two current crossings, and continuous
post-crossing learners. Failure, retirement, profiles and rebuilding cannot
copy wealth, backfill observations or refund alpha. No external-law proof
is inferred from the executed tapes.

A concrete new endpoint counterexample shows why this separation matters.
With delta=2^-54 and cap 2+delta, reference masses (1+delta,1) strictly beat
the incumbent (1,1). Binary64 rounds both candidate masses to one. Ordinary
learning rate zero keeps the registered learners fixed while predictions,
gradients and optimizer commits still execute. Reference crosses at event
five with lower wealth 322095/65536, whereas physical gain is exactly zero
and wealth stays one. The paired result correctly remains UNRESOLVED.

The audit also catches a rounded optimizer reaching slightly above 1/10:
reference remains exactly at cap 21/10, while the whole-domain finite mass
sum exceeds it. A currently inactive source would hide that violation.
The physical identity terminates before the next context. Separate exact
score arithmetic exhaustion cannot borrow finite evidence, and a failed
finite crossing-state allocation cannot leave a usable paired crossing.

Independent checks cover 400 contexts from 16 box declarations and 125
delayed states. Twelve learning events give 24 same-path score/wealth checks,
six renewed optimizer range bounds and 62 bitwise learner phase checks.
All 32 five-event fair-label paths execute 160 actual events and verify 62
conditional wealth inequalities; each path crosses with probability 1/32
under its separately allocated alpha 1/3. Four profile events from two old
observations produce fresh identities starting only at the next unread ID.
Actual work/byte limits, identity mismatch, and post-crossing failure pass.

Read `theory/proofs/PAIRED_CPU_PERSISTENCE.md` and the minimal
`evidence/minimal/FP_PAIRED_CPU_PERSISTENCE_AUDIT.json`. This advances the CPU
four-path/dual persistence protocol; complete immutable ERC-1 enforcement,
physical accounting, atomic installation, explicit gate mapping and actual
target AMP remain open. No Foundation action or static special case was
added. Runtime is NOT FROZEN, and RTX 3090 science remains HOLD.

## 58. Separate historical selection from current install authority (2026-09-12)

The next obstruction was the time at which a proposition is true. A complete
native search selects one actual initialized/profiled endpoint at cursor t0.
Fresh evidence then advances its candidate and baseline learners. The
original maximum proof is stale as a current optimum at t>t0, even though
its historical selection statement remains true. Requiring unchanged
constructor-endpoint optimality alongside nonempty fresh learning confuses
these two roles and can prevent the intended composition.

The new owned CPU installer uses the search proof only as historical
provenance. It checks that both fresh evidence paths started at exactly the
selected candidate/base states and original cursor. Current four-learner
continuity, two same-path crossings, complete update boundary and numerical
relation are separate obligations. No current global optimum is inferred;
the stale reference proof stays rejected in its current-maximum API.

`CpuInstallContract` registers a serialized CPython root/lease transition
before execution. All learners retain complete numeric/discrete state and
the same physical buffers at the same exogenous cursor. Metadata preparation
coexists with the incumbent and target and pays declared work/peak costs.
A detached lease map validates original owned debits, final role/global
residency and closed owners. One complete root publication changes deployed
lineage and actual ownership together, retains the old learner as a shadow,
closes search continuations with frontier/history preserved, and ends old
persistence authority without rebasing wealth or refunding alpha.

The atomic lease primitive is a declared physical machine operation, not a
resource-total certificate. An exact two-byte example shows why acquiring
before releasing is a different machine: two one-byte role caps admit the
simultaneous exchange but reject acquire-first. The Runtime publishes the
prepared ledger only with its actual buffer map and complete state. Unknown
Runtime/ledger coordinates cannot inherit this fixed schema/frame proof.
No model-level semantic action or static architecture case was added.

Failure does not restore the whole past. Old learners/evidence/frontier stay,
but attempted identities, revision, paid work, peak and retired buffers
remain part of the complete history. Adversarial retry exposed an actual
implementation defect: abort retired a prepared object's ID while leaving
the old logical generation intact, so the next attempt tried to recycle
that physical identity. Prepared metadata now uses a unique attempt namespace.
Late failure leaves the old continuous evidence usable only for a subsequent
paid attempt; cleanup failure halts instead of hiding workspace.

`scripts/audit_cpu_installation.py` checks 2,016 small lease-map cases, 649
feasible transfers, and actual complete native constructor classes of 35 and
774 programs. Both execute fresh dual persistence, install and later ordinary
learning; the larger case installs nonzero trained parameters. Independent
binary64 continuation replay checks 151 and 870 phases respectively. Exact
learner/buffer identity, stale proof/frontier rejection, no alpha refund,
wrong lineage/path, partial units, unknown job state, late failure and paid
retry pass. Actual immutable byte/work caps reject a currently resident
target whose installation preparation cannot fit.

A further continuation test executes two complete 35-member searches and
installations in one Runtime, at cursors 22 and 38. The second proposal uses
the new actual deployment as baseline and starts fresh identity/wealth at
cursor 24 under preregistered later rules. The four alpha allocations reach
3/4 and remain spent across both installs; a third admission is refused even
with enough unread horizon. Both receipts remain owned and another 306
independent binary64 phase checks include ordinary events after the second
install. Closing the first search therefore does not disable the declared
future compilation interface or revive earlier evidence.

Read `theory/proofs/OWNED_CPU_INSTALLATION.md` and the compact
`evidence/minimal/FP_CPU_INSTALLATION_AUDIT.json`. This is executed CPU
transition evidence, not a model-science advantage or complete release.
Concurrent/crash-safe publication, total host/device physical accounting,
complete ERC-1/gate closure and actual target AMP are not inferred. The
generic target installation port stays UNRESOLVED. Foundation/ERC-1 remain
frozen; Runtime is NOT FROZEN and RTX 3090 science remains HOLD.

## 59. Unfunded requests exposed unbounded Compiler history (2026-09-12)

The physical audit found a failure before any model arithmetic mattered.
At `8880371`, a construction request minted its candidate ID, owner and
revision before attempting to pay inspection work. Once that work cap was
exhausted, each new request still appended owner/resource/failure history,
with unchanged live payload, peak and cumulative work. A legal zero-SUM
program at cap 18 reproduces 64 additional IDs, owners and attempts plus
192 resource events; the same sequence extends to arbitrary length.

Because the public snapshot distinguishes those history states, no finite
complete-state storage bound follows from the fixed old counters. This is
not fixed by multiplying packed model bytes by a metadata overhead constant.
UNRESOLVED was the correct task decision; complete physical accounting did
not follow from it. The old source is replayed directly from Git for audit.

The correction is one paid admission boundary for all public Compiler
control operations. Machine `packed-reference-payload-v2` charges a positive
reference work unit through the immutable operation role before any owned
mutation. A refused request creates no new attempt or revision; an admitted
failure retains all its subsequent history/work/peak. Retirement and
cancellation also require admission. Ordinary target observation remains
prepaid so a revealed outcome can never be refused retroactively.

With remaining role work W_r and positive admission cost c=1, the number of
admitted control requests satisfies K_r<=W_r. This rules out the historical
free state-growth loop, without claiming a total heap or instruction bound.
Current proof authority is preserved correctly too: 16 unfunded requests
leave the same completed 35-program class proof current. The audit checks
64 denials on each of 11 public paths and all 96 four-command construct/
retire trees at six work caps (384 positions, 177 funded state changes).
Construction/event/profile/search, reference/paired persistence, binary64
and continuous two-install endpoint audits pass against the revised machine.

Attacking the resulting resource claim found the next concrete obstruction.
A source-box input `1/2^m` enters the pending record before the 128-bit
reference guard refuses prediction. Denominators of 257,1025,4097 bits remain
in halted state with unchanged packed payload/work. This is a separate
counterexample at that revision: bounding admitted calls still does not bound raw
ingress and terminal diagnostic storage. The input has been received and
cannot simply be erased, rounded or treated as unread to improve accounting.

Read `theory/proofs/OWNED_CONTROL_ADMISSION.md` and
`evidence/minimal/FP_CONTROL_ADMISSION_AUDIT.json`. The next physical work is
paid representation-aware ingress/diagnostics and complete host accounting,
with full ERC-1/gate registration still open. No Foundation action or static
case expansion is introduced; Runtime is NOT FROZEN and science stays HOLD.

## 60. Exact input becomes an owned paid byte prefix (2026-09-12)

The next protocol correction addresses the one-request counterexample from
section 59. Moving the arithmetic guard alone would not specify which input
bits had already arrived or where they survive failure. The Runtime now
requires one preregistered exact byte interface, with a capacity and maximum
chunk size, rather than accepting naked rational objects.

Machine `packed-reference-payload-v3` prepays a receive window, a fixed
received-count/status slot, identity and bounded reference ingress work
before offering any bytes. Current learner and persistence IDs seal at that
boundary. Each legal nonempty chunk writes only the next offered extent;
the Runtime creates no chunk-count or chunk-history state. The canonical
grammar represents every nonnegative rational vector. Insufficient byte or
integer resources yield UNRESOLVED, without changing the semantic source
class or inventing an architecture action.

Length fields and leading bits are checked before creating numeric bodies.
Malformed, truncated, too-wide or later failed predictions preserve their
received bytes in the paid window and a fixed terminal status. No decoded
rational enters retained pending state before its own allocation succeeds.
A failed empty-window preparation preserves work, peak and retired IDs,
and only a fresh paid retry can publish a receiving identity. Unexpected
prediction failures keep their original halt cause.

The old Runtime/machine/data source at `5055f3e` remains an executed
counterexample. On the current path its 257-/1025-/4097-bit denominators
remain as 42/139/523 paid wire bytes, with no oversized pending rational.
The new audit checks 3,072 integer/width cases, 85 vectors, 24 boundaries,
and all 208 chunkings of a nine-byte frame. All 1,328 equal-prefix snapshot
checks agree, as do completed prediction and observation states. Real work
and residency refusal, preparation failure/retry, partial capacity and 90
forbidden mid-ingress actions are tested. A four-event four-learner path
also passes 22 independent binary64 phase checks.

All current integration producers now enter through the mandatory byte
protocol. Ordinary/profile/search, reference/paired evidence and the
35-/774-member selection/install chains pass, including the two-install
continuation and 2,016 lease cases. The small work-exhaustion persistence
fixture preregisters a sufficient 16-byte window for its fixed binary
domain, preserving paid ordinary continuation after evidence becomes
unresolved; it does not bypass the new ingress debit.

Read `theory/proofs/OWNED_CONTEXT_INGRESS.md` and
`evidence/minimal/FP_CONTEXT_INGRESS_AUDIT.json`. The scoped invariant covers
recorded serialized Runtime state and packed payload. Full Python metadata,
transient copies/arithmetic scratch, general diagnostics, ERC-1 enforcement
and release-gate mapping remain the physical frontier. The fixed status slot
is paid; this does not imply every exception object is paid. Foundation and
ERC-1 stay frozen, static cases stay parked, Runtime stays NOT FROZEN, and
actual AMP correctness precedes RTX 3090 science.

## 61. Encoding workspace exposed a deployed-program identity failure (2026-09-12)

The next resource audit attacked what happens before a buffer's ledger debit.
At `532d713`, identity hashing and packed realization expanded complete
duplicate trees of tagged Python lists. Under one fixed 8 KiB payload cap,
100,000-edge grammar and zero initializer, a legal repeated-edge SUM request
could create about 62 MB of newly traced Python allocations before returning
UNRESOLVED. The recorded packed peak stayed 1,823 bytes. This made the missing
temporary-workspace obligation concrete; final buffer accounting did not
establish a complete host cap.

While replacing the encoder, its purported typed injectivity failed too.
The legal Python names `"\U0001f600"` and `"\ud83d\ude00"` denote different
causal sources, but ASCII-escaped JSON gave them identical bytes before
hashing. The actual old Runtime could construct a candidate on the second
source and overwrite the deployed program's registry entry. Its next
probability became 1/2 instead of the required 2/3, with no installation.
This was an execution/identity mismatch, not a cryptographic attack or a
Foundation counterexample: faithful encoding requires no new native action.

Machine v4 now emits typed UTF-8/surrogatepass bytes that preserve all code
points. ASCII encodings remain compatible; non-ASCII artifact IDs change.
An existing program address also requires full validated code equality.
Even an injected constant address can only make construction UNRESOLVED;
it cannot replace owned code or declare the otherwise legal graph impossible.

The resource correction is centralized. Exact extent calculation creates
neither escaped scalar text nor a duplicate tagged tree. `realize` returns
only a value/size plan. Runtime validates and admits the complete allocation
batch before creating an output buffer and streaming into it without resize.
Hashing streams as well. Privately owned bytearrays preserve the prior CPU
install object's identity, and the already reserved target slot stays prepaid.
The matched traced peak is about 0.134 MB over 1,000--100,000 repeated edges;
it still exceeds the packed cap and is not a full physical-memory certificate.

`scripts/audit_owned_encoding.py` retains the historical actual Runtime
witness, corrected forecasts, forced-address failure and allocation denial/
partial-write checks. It compares 235 packed trees and 240 identities,
all 65,536 BMP code points and 3,072 surrogate/astral boundary classes,
including ASCII preservation and exact extents. The mathematical argument,
measurement exclusions and next physical boundary are recorded in
`theory/proofs/OWNED_ENCODING.md`, with concise evidence in
`evidence/minimal/FP_OWNED_ENCODING_AUDIT.json`.

Full host metadata, scalar/key encoding workspace, arithmetic scratch and
allocator state remain open, along with ERC-1/gate enforcement and target
AMP. Foundation/ERC-1 remain frozen, static families are not expanded,
and Runtime/science release is not inferred from these corrected prefixes.

## 62. Host exhaustion cannot assume an allocating cleanup succeeds (2026-09-12)

The next physical-budget investigation tested the failure protocol itself.
At `dfa1583`, injecting MemoryError into construction-result allocation
caused cleanup to close a candidate's owner and free every learner buffer,
while its published candidate record survived. After an earlier event had
retained the same program code, the next public prediction still evaluated
that orphaned learner. A generic cleanup attempt was not a complete-state
recovery proof.

Machine v5 now propagates host allocation exhaustion past all internal broad
handlers to one public boundary. It writes a precreated marker to existing
state slots and closes continuation, proof, persistence and installation
authority. It allocates no cleanup/history representation and refunds no
alpha or work. Construction also prepares its result before publication.
Snapshots remain passive diagnostics when they can be allocated and decoded;
the terminal prefix is not certified to be resumable or generally recoverable.

The endpoint audit covers all 22 authority/continuation ports, 352 repeated
refusals, event and ledger failures, a previously issued class proof, and an
actual CPU installation attempt with four learners and paired evidence. Its
separate Windows experiment creates a suspended child, fixes and checks a
64 MiB job commitment cap before resuming it, and executes an unmodified
128 MiB Runtime ingress-window allocation. The kernel refuses it, MemoryError
closes authority before any input, and paid work survives. This is actual
allocation refusal, not an injected ResourceExceeded or a packed-byte estimate.

Read `theory/proofs/HOST_ALLOCATION_FAILURE.md` and its minimal JSON evidence.
The OS mechanism offers a central bound on its declared commitment measure,
but remains an audit harness: production run registration, resource roles,
supervision/publication after process termination, other host/device resources
and full ERC-1 enforcement remain open. Foundation/ERC-1 stay frozen; no
native architecture action, static family or science release is added.

## 63. Resource boundaries cannot reset the execution history (2026-09-12)

The v5 OS refusal audit supplied a concrete commitment mechanism, but the
Runtime itself had no live binding to that mechanism. Machine v6 now owns
one. `HostResourceContract` fixes a whole-process private-commitment arena
shared by deployment and compiler, charged in full to both and once globally.
The kernel cap is the minimum of their three declared caps. Native Runtime
queries establish its actual process/job association and resource history;
supplied counter data cannot replace them. This puts private Python metadata,
transient copies, diagnostics and arithmetic scratch under the same resource
measure instead of introducing object-category multipliers.

An adversarial real-process experiment exposed why a live job alone is still
insufficient. Under a 128 MiB outer cap, allocate and free a real 80 MiB
buffer, then attach a new 64 MiB inner job to the same process. Its current
commitment and new job peaks are about 23 MiB while the process-lifetime
peak remains about 103 MiB. A current/new-job-only check would erase the
earlier violation. Runtime now checks whole-lifetime process peak and keeps
process CPU history as well; job aggregates remain separate observations.
These observations are not complete physical-state equivalence classes.

The actual Runtime also executes the existing 35-program search, four-path
reference/binary64 persistence, CPU installation and ordinary continuation
inside a 64 MiB process. Its host binding survives the single root publication.
Native premise failure closes authority without allocating cleanup, and
later diagnostic failures preserve the first host halt marker. Actual host
ingress refusal retains spent work. A worker that completes the install,
writes a result and exits 17 is not accepted as a successful run. Parent
measurements come from the actual launched process/job handles.

Read `theory/proofs/BOUND_HOST_RUNTIME.md` and the five-case endpoint audit.
This implements the declared private-commitment dimension, not complete
ERC-1 run/policy registration, production supervision/publication and error
ownership after termination, shared platform/device resources or gate mapping.
Unbound reference execution stays explicit; no manifest field or sampled
counter grants missing authority. Foundation/ERC-1 stay frozen, static cases
stay parked, and target AMP correctness remains ahead of RTX 3090 science.

## 64. The search/evidence/install driver becomes owned state (2026-09-12)

The live host binding made the remaining owner question concrete. Previous
audits controlled when search ran, which returned winner entered persistence
and when installation was attempted. Those endpoint proofs did not make the
external driver's changing state part of the actual self-Compiler's Omega.
Rather than add a general restart mechanism, the next implementation puts
the declared strategy into the existing Runtime root.

Machine v7 accepts immutable `CompilerPolicy` stages over registered complete
native classes, with fixed earliest boundaries, search allowances and paired
rule names. Ordinary context/target input now drives the whole strategy.
All other external control/authority methods close in that mode. Strategy
state, IDs, progress buffers and work are owned, and failed action prefixes
cannot be retried as fresh. The strategy adds no semantic graph operation
and receives no supplied architecture, fitted value or winner.

Installation required a real frame extension: its successful policy action
must publish with the complete learner and physical leases. The new policy
buffer is prepared under workspace ownership and participates in that same
single root transaction. A refusal there preserves the old deployment.
Native resource-premise loss also propagates through nested public calls
and their broad exception handlers without allocating cleanup. Its exception
type is distinct from argument/graph rejection; an injected construction
failure verifies that lost host premises cannot become graph inadmissibility.

The actual strategy executes two 35-program cycles with installations at
cursors 22/38 and alpha 3/4, plus the trained 774-program case. Exhausting all
64 six-label streams gives 32 incumbent selections, 30 unresolved stages and
two installs, matching an independent prediction/wealth oracle. Separate
tests attack partial alpha admission, search allowance and policy-storage
failure. The two-install path runs in a real 64 MiB Windows job. Read
`theory/proofs/OWNED_COMPILER_POLICY.md` and its minimal audit evidence.

One root's alpha ledger is global across its stages and installations. A
family spanning new Runtime roots needs its own total allocation; the audit's
separate diagnostic roots do not supply that broader error guarantee. More
hand-written strategies are not the next research frontier. Complete ERC-1
run/report registration and historical release-gate mapping remain, followed
by actual target AMP and RTX 3090 science. Foundation/ERC-1 stay frozen.

## 65. The finite run owns its conclusion and the release map becomes explicit (2026-09-12)

The v7 owned strategy separates ordinary event publication from later control
failure. Consequently `OBSERVED_REFERENCE` is not a whole-run success flag.
The next step makes the actual run's immutable registration and terminal
conclusion owned state rather than relying on an external summary of events.

Machine v8 assembles and pays for one reference manifest containing the
initial Program, construction/data/value/search/persistence/CPU/host/policy
contracts and fixed numerical machine. Budget encodings themselves cost
space/work; old exact-boundary audit fixtures now calibrate actual immutable
roots instead of assuming their declarations are free.

After the last registered ordinary event and eligible policy phase, Runtime
prepares a paid conclusion and publishes a final closure pointer. Every
non-diagnostic port then denies without growing recorded history. A partial
optimizer unit is preserved without a new commit. Unfinished stages report
UNRESOLVED; historical finite-class proofs remain attached to their exact
classes even after installation has revoked the current search authority.
The complete snapshot keeps normalizers, raw numerical paths, owned resources,
filtration and alpha alongside finite prediction diagnostics.

Injected report-retention failures after the cursor-22 installation demonstrate
why event, install and run completion must be distinct. The first two remain
completed facts, with actual deployed learner/receipt/target/alpha retained;
no run closure is issued. The endpoint audit also covers all 28 binary tapes
of lengths 2/3/4, 638 terminal refusals, native/arithmetic failures and a full
35-program CPU chain in a 64 MiB job. It independently replays 141 binary64
phases and checks the actual process identity and final exit. The existing
64-stream native policy oracle, host/failure, control, CPU capacity, ordinary
event and search adversaries remain passing at this change.

The new `docs/REFERENCE_RELEASE_GATE_MAP.md` assigns all 47 historical
obligations to concrete reference/CPU evidence, retained scoped theorems,
absent bypass authority, open reference discovery or held target AMP. It
does not turn a mapping count into a release certificate. The specific
remaining reference discovery gap is the hierarchical anti-unigram gate:
the old 32-token identifiability audit and current scalar compound search
cannot be spliced into an owned Runtime execution that did not happen.
Attack that acquisition/construction problem, then final reference integration
and actual target AMP before RTX 3090 science. Optional universal strategies,
quotient implementations or restarted families do not become prerequisites
to this single-root reference claim. Foundation/ERC-1 remain frozen.

## 66. A saturated empirical upper unlocks the owned hierarchy gate (2026-09-13)

The n=32 hierarchy cannot be recovered by interpreting a hand-written
candidate as the whole native class. Literal complete construction also
cannot fit its finite work declaration: the broad registered caps contain
at least 2^6540 source-only program strings, as well as full pair lookup.
The useful escape is a stronger comparison bound, not different semantics.

For the existing frozen-endpoint objective, identical complete source rows
have identical predictions. The saturated multinomial likelihood therefore
bounds every categorical predictor, hence every native constructor endpoint.
An actual owned feasible witness attaining it closes the whole class's
empirical maximum. Machine v9 independently recomposes that upper from
retained observations and rechecks the witness's class/frame, initializer
or executed profile and actual current score. Its separate bounded proof
does not assert that unvisited programs were constructed. Both proof types
continue through the same fresh-evidence and CPU installation requirements.

The registered empirical relation solver receives aligned observable token
atoms, never hidden groups. Majority constraints propose group SUMs and
pair PRODUCTs using existing initialized values. It retains all counts,
components and arbitrary component-root flips. A missed upper remains
UNRESOLVED; the preferred proposal shape never narrows the decision class.

The larger execution exposed needless repeated encoding of unchanged exact
range tables. Their premises are the fixed program/source-domain contract
and theta, with all legal delayed values already enclosed. Keeping the same
owned bound when theta agrees is sound while the actual delayed queues,
gradients and optimizer counters change. Changed theta still recomputes and
allocates before releasing the old bound. This is physical object retention,
not whole-state equivalence. A recurrent case and post-allocation failure
test check the distinction.

An initial 310-event-update-unit diagnostic timed out after 30 minutes with
no completed Runtime report. The passing result is a new immutable run with
unit ten and the range-retention change, not a continuation or borrowed
evidence from that failed root. These different registrations do not form
a matched timing benchmark.

The actual bounded n=32 run now receives 310 training labels, constructs a
74-node graph with six SUMs/four PRODUCTs, checks all 1,024 token pairs,
installs at cursor 330 and continues to the sealed cursor 622. Independent
replay checks 1,963 binary64 phases. The 1 GiB job exits successfully with
peak process commitment 333,139,968 bytes; peak owned reference payload is
65,266,182 bytes. Exact audits additionally cover 18,225 rational comparisons,
218 independently enumerated native programs, all 16 four-token assignments,
real profile endpoints and eight injected authority/resource/numerical faults.

The strongest lesson is a negative one alongside the successful construction.
A five-node zero-PRODUCT program ties at the same train optimum. Two
disconnected latent worlds have identical train records and different unseen
relations. Even a connected but wrong empirical assignment attains the train
upper; subsequent real protocol events can end without crossing or install.
The existing sharp full-uniform SUM envelope remains the strong broader-task
control, not a claim inferred from the training path. No new forcing,
population-identification or deterministic-tape freshness theorem is asserted.

Read `theory/proofs/SATURATED_REFERENCE_CLASS_BOUND.md` and the minimal
`FP_REFERENCE_ACCELERATION_AUDIT.json`. Gate 17 now has current owned CPU
evidence. Complete release-revision integration remains before actual AMP
and RTX 3090 science. Foundation/ERC-1 stay frozen and static families parked.

## 67. Independent complete-learner model and release integration (2026-09-13)

The remaining reference question is whether the assembled owned endpoint
matches its exact decision classes at one source revision. A new oracle
enumerates each sampled small native grammar independently, executes full
rational learner/profile states by forward differentials, and compares all
actual rows, the trained baseline and subsequent ordinary successors. Typed
sources, compound nodes and recurrent queues remain part of the checked
syntax/state; no current-function quotient is used.

The preliminary 32-registration version passed 1,310 endpoint comparisons
and 20,708 independent binary64 phases, but encountered no infeasible ranges.
That omission motivated four active-constraint cases. Those separately pass
with 44 initializer-range failures, two profile-range failures, three
unresolved classes and three halted ordinary commits; a delayed-state case
seals its stream while class coverage remains unresolved. The expanded
full randomized battery is pending its committed integration run.

`scripts/audit_reference_release.py` now prepares a real clean clone of one
committed source revision, imports all package modules and runs all 21
current complete reference audit scripts. It checks the 47-row obligation
map without converting scoped theorem/absent-authority/held-target rows into
aggregate passes. It requires actual success exits and complete bounded
reports and retains minimal coverage and OS job records. Read
`theory/proofs/REFERENCE_RELEASE_SCOPE.md`. This preparation adds no Runtime
authority and does not yet freeze Reference or release AMP/model science.

The first fresh-clone integration at `7360eb0` exposed two old audit-boundary
assumptions. Since budget values are now paid manifest coordinates, replacing
the generous budget also changes initial work/payload. An intended ingress
refusal had three work units to spare; a supposedly failed constructor
evidence allocation actually succeeded with eight bytes to spare and failed
at a later allocation. The retained CHECKED phase was correctly owned.

The corrected tests calibrate new immutable diagnostic roots, never edit an
executed root's budget, and assert the intended first finite-observe or
constructor-evidence failure itself. They now pass at actual ingress work
cap 5,310 and byte caps 32,114/11,177/9,785. This corrects audit coverage,
not Runtime semantics. A fresh complete release run is still required.

The next complete run reached a further ingress assertion using the same
obsolete cross-budget initial-work assumption, this time for exhaustion
immediately after admitted bytes. Admission refusal and post-admission
exhaustion now share calibration at offsets minus one and zero; their actual
caps are 5,310 and 5,311. The **entire** ingress and binary64 Runtime audit
batteries then passed, including all later failure/filtration checks, and
their small current evidence files were refreshed before another integration.

## 68. Freeze the scoped Reference/CPU release (2026-09-13)

The complete release battery now passes at source
`ebe2c4cf23f296fe517d4fe237cef45eaa98d309`, machine v9, CPython 3.12.9 on
64-bit Windows 11. A real clone without hardlinks imported all 30 current
modules and ran all 21 full audit scripts, then remained clean at the same
source revision. This is the final integrated result, not a union of partial
diagnostics or a reclassification of the two earlier failed release runs.

The independent learner oracle checks 36 Runtime registrations/34 class
shapes and every one of their 2,665 native members. It matches 2,619 exact
endpoint scores and 33 class proofs, keeps 46 range failures unresolved,
checks 361 ordinary successors and three halted commits, and independently
replays 23,274 binary64 phases. The full suite also covers 2,016 lease cases,
the trained 774-member install, two successive installs at 22/38, all 64
short policy streams and all terminal/failure/authority counterexamples.

The owned n=32 hierarchy again installs at 330 and seals at 622, checking
all 1,024 source contexts and 1,963 binary64 phases. Its actual 1 GiB job
exits successfully with process peak 333,582,336 bytes and reference payload
peak 65,266,182 bytes. The declared complete native class still includes
at least 2^6540 source-only strings; one attained universal empirical upper
closes selection without asserting that all members were constructed.

`FP_REFERENCE_RELEASE_AUDIT.json` records the source, complete executed
sections, small coverage summaries and actual OS exit/identity/peak records.
The 47-gate map preserves scoped-theorem, absent-authority and held-target
rows. The freeze declaration changes documentation/evidence only; no
implementation or audit code differs from the tested revision.

This closes the registered Reference/CPU prerequisite, including its owned
single-root strategy and serialized resource/install/run protocol. It does
not close actual target AMP, universal strategy/value optimality, optional
unsupported information interfaces, shared platform/device accounting or
cross-root error families. Foundation R4 and ERC-1 are unchanged. Static
cases remain parked. Actual AMP correctness and its complete ownership,
four trajectories, fresh same-path evidence and installation are now the
active frontier before RTX 3090 model science.

## 69. Execute and distinguish actual CUDA arithmetic (2026-09-13)

The first post-freeze device correctness audit runs on RTX 3090 / SM 8.6,
PyTorch 2.12.0+cu132, CUDA runtime 13.2, driver 616.92. It checks all 63,488
finite half encodings through real device transport and widening/narrowing,
190,464 conversion boundary cases, and 11,040 finite half/single arithmetic
results against exact Fraction/RNE models. Expected overflow and division
by zero remain noncertifiable; no CPU fallback can pass the audit.

The adversarial result matters more than the coverage count. Positive
`a=1027/1024,b=3/2,c=2^-24` gives actual half addcmul `0x3e04`, while ideal
one-round half FMA gives `0x3e05`: single-precision intermediate rounding
returns the exact half midpoint before the storage tie is resolved.
The random FMA samples missed this difference. The versioned PyTorch
implementation corroborates single FMA followed by half storage.

Separate half multiply/add also differs from addcmul on positive inputs;
float32 `7/12` changes by one ULP when its device divisor becomes a Python
scalar. Autocast leaves the tested elementwise native operations float32.
Actual positive stored masses again distinguish a categorical distribution
from rounded normalizer/division outputs. These observations require an
explicit physical lowering and event relations, already required by ERC-1;
they do not reopen Foundation or extend the frozen static resource study.

`ACTUAL_CUDA_PRECISION.md` gives the small exact derivations and primary
implementation sources. `audit_cuda_primitives.py` regenerates all inputs
and writes only minimal counts and witnesses. The complete owned AMP
learner, device resources, four continuous paths, fresh evidence and
installation remain open; this diagnostic issues no bridge authority.

## 70. Execute continuous native mixed-precision learners (2026-09-13)

The next component executes actual half storage/forward products, ordered
single SUM/readout, single reverse operations and master SGD on RTX 3090.
It retains complete device parameters, delayed queues and gradient
accumulators from birth. Source/initializer encoding is explicitly host
RNE32 followed by device transport/casts; no trained reference endpoint is
recast into a supposed GPU successor. Previous device states stay unchanged.

The independent exact rounded interpreter matches 1,306 actual phases:
all 64 three-event context/target streams beside the Reference Runtime's
baseline/candidate, a six-event recurrent profile followed by ordinary
continuation, and 24 further three-label native DAGs. Repeated edges/heads,
squares, unused slots, arbitrary positive sources, whole-unit profile
attachment and partial final units are exercised. The phase tapes observe
2,452 real half multiplications; 1,340 coordinate tests verify the exact
binary32 dyadic floor. Of 1,200 state coordinates compared to actual exact
Runtime learners, 326 differ from endpoint recasts. These measured errors
do not supply a future bound or a chosen bridge tolerance.

A finite-state counterexample exposes an additional numerical acceptance
hazard: maximum finite single gradient times scale two becomes infinity,
while projection of the negative resulting parameter returns finite zero.
The executor retains and checks every intermediate before success, so it
refuses that actual CUDA phase without changing its input state. Forward
overflow and mutable nonfinite parameter corruption are refused too.

The new module imports without importing Torch or creating a device context;
the frozen Reference/CPU implementation and target install behavior are
unchanged. `CONTINUOUS_CUDA_LEARNERS.md` states the exact physical schedule
and finite coverage. The component has no signer, resource claim or Runtime
AMP authority. Next is complete owned device integration and event relations,
then target range/persistence/build/install. Foundation and ERC-1 stay frozen;
model science stays HOLD. No new static special case is introduced.

## 71. Bind complete CUDA learner tensors to a prepaid arena (2026-09-13)

The continuous mixed-precision learner now uses explicit output/copy views
for every tensor, including casts, queues, masks and integer grid work.
All 1,306 phases execute in one actual 16 MiB backing tensor. Native tensor
and reservation peaks stay at 16 MiB; no further allocator event occurs.
The 32,996 initialized extents consume a 304,064-byte prefix, while the full
arena and reservation remain charged to each role, once globally. Append-only
phase/extents retain failed work and avoid an unproved erasure/reuse step.

Two accounting assumptions failed under actual execution. First, a 2 MiB
tensor request needs a default 20 MiB segment, so checking reservation only
after allocation can overspend an admitted budget. Worse, setting large
segments to 40 MiB and then passing an empty allocator configuration restores
the entire reported default settings dictionary while leaving the hidden
segment size at 40 MiB. A fresh 2 MiB request then really reserves 40 MiB.
The corrected path binds the segment size explicitly, admits its versioned
allocation extent before the first tensor and verifies the actual result.
The counterexample and correction both execute in independent fresh processes.

Second, allocating and freeing an external single returns current tensor
bytes to the same 16 MiB. Lifetime native allocation counters retain the
extra 512-byte allocation and segment, so they refuse the escaped work.
That failure is terminal without clearing state or resetting counters. If an
unexpected executor error already occurred, a simultaneous closure refusal
cannot downgrade it into expected budget uncertainty. Actual prior writes
and the failed phase remain available for diagnosis.

The independent extent model checks 216 complete three-request sequences;
typed bounds, initialization, stale writes, 1,340 exact grid coordinates and
masked optimizer overflow also pass. This is a bounded tensor-storage
implementation, not host/driver/context/total-device accounting or Runtime
authority. `BOUNDED_CUDA_TENSOR_STORAGE.md` records its proof premises and
minimal evidence. The next work is the complete Runtime-owned AMP prefix,
then target range, same-path fresh persistence and installation. Foundation,
ERC-1 and the scoped Reference/CPU freeze are unchanged; science stays HOLD.

## 72. Put actual CUDA prefixes inside the complete Runtime (2026-09-13)

Actual device learners now execute through the existing Runtime's native and
profile phase hook. The immutable run manifest registers the CUDA build,
device, numerical schedule, tolerances, arena and phase budgets. The private
owner retains actual master/gradient/queue tensors; passive snapshots expose
their immutable raw records. No public method accepts a device endpoint or
bridge token. All state and prediction comparisons use exact arithmetic,
reusing the existing comparator through an injective half/single encoding
widening. This does not create a CPU trajectory or transfer CPU evidence.

Each GPU phase receives its fixed evidence frame before executing. The
whole frame is paid, including unused padding; successful raw records are
written into it. Every output/cast/copy/mask extent consumes a phase allowance.
An exact count derived from the fixed lowering also checks completion. A
numerically correct zero-slot baseline successor produced without device
work would otherwise pass the value relation; the schedule check refuses
that substituted endpoint. This is a physical implementation constraint,
not an added semantic action or lower bound over other realizations.

The ordinary event prepares all reference and CUDA successors before joint
publication. A real 46-coordinate budget lets the baseline finish observe
but stops the candidate; both published learners remain unchanged, while
the revealed target, baseline's staged output and candidate's failed work
remain. Actual evidence-frame exhaustion cannot leave an unowned CHECKED
record. A prior unexpected executor error also remains primary when its
oversized diagnostic fails retention. A malformed backend object exposed a
second classification hazard: failure during raw extraction could escape
as ContractError and resemble native inadmissibility. The admitted execution
boundary now preserves it as EXECUTION_FAILED.

The independent rounded interpreter replays 1,024 actual Runtime phases for
all 64 three-event binary context/target streams, 44 recurrent/profile phases
beside 44 CPU binary64 phases, and 41 phases for a complete 35-member native
reference class. The profile retains both delayed positions, replays only
the original two revealed records, and attaches full state before ordinary
continuation. Every successful phase's actual paid bytes match its raw record.
All 63,488 finite half encodings and twelve signed single boundaries verify
the exact comparison injection, including zero signs.

A one-million-byte packed cap allows the baseline prefix but prevents some
CUDA constructor-evidence frames. The native search therefore remains
UNRESOLVED without a class proof: exhausted physical construction cannot
become member exclusion. Other actual controls reject an escaped freed
allocation, an inexact zero-tolerance newborn and rounded readout error
before target revelation. The existing full CPU event, binary64-prefix,
installation, ingress, host-failure and finite-run audits also pass.

CPU installation and its owned policy/run closure explicitly cannot omit
or transfer a CUDA-bearing root. Current target whole-domain range, fresh
same-path AMP persistence, build/copy/install and total-device resources
remain open. `OWNED_CUDA_PREFIX.md` fixes this precise checked-prefix scope.
Foundation R4, XVII.31 and ERC-1 stay frozen; model science stays HOLD.

## 73. Prove current CUDA range and execute fresh same-path evidence (2026-09-13)

The next AMP obstacle was a missing proof premise: observed closeness to
reference and finite primitive audits do not establish a whole-domain
physical arithmetic law. The implementation now proves range over a
declared deterministic mixed rounded predictor and checks every actual
forecast against that same predictor before accepting it. The exact check
compares all stored native/weight/head/readout/queue coordinates, including
zero signs. It never repairs a device output from reference. A one-ULP
actual-tensor fault passes the old tolerance relation and fails this added
conformance check before any target; the audit executes both comparisons.

Positive SUM/PRODUCT and monotone rounding give one general current-domain
bound for the registered schedule. It preserves source RNE32 then RNE16,
all master casts including unused slots, half products, ordered single SUM
accumulation, single base/readout and both normalizer representations.
Complete queue invariants cover every tail entry. Reference work is paid
before forecast/range checking, and immutable range records belong to the
Runtime's own persistence identities. Changed actual master bits require
renewed bounds; unchanged theta reuses only the bound, retaining distinct
complete learners and checking the actual successor queues.

The existing fresh-evidence machinery now has a separate CUDA stored-mass
score path and null. Reference and CUDA independently spend global alpha,
seal their own pre-target forecasts and update guarded lower wealth. Their
identities bind initial/current owned device phases as well as the exact
and optional CPU trajectories. Pairing reads those owned identities and
requires matching starts and epoch schedules. No helper can submit a range,
device endpoint or crossing. The new CUDA identity extension leaves the
frozen non-CUDA identity encodings unchanged.

Two real trajectory witnesses prevent evidence transfer. With a fixed
coefficient 2^-25 and zero-rate SGD without a floor grid, reference crosses
at event five while the half forward has exactly zero gain and wealth one.
In another registered update, exact theta reaches 3/10 but its future half
value is 1229/4096, above the delayed-body cap. The current zero queue and
ordinary exact successor remain valid; the unproved future CUDA identity
stops. A safe observed context cannot revive failed full-domain admission.

Independent rounded evaluation checks 16 boxes/400 predictions and 125
complete recurrent queues. All 32 five-label fair branches run on actual
CUDA, contributing 832 independent phase checks and 62 conditional wealth
inequalities; each path's fixture crossing probability is 1/32 under alpha
1/3. A 12-event trained path checks 24 scores/logs/wealth steps, six range
recomputations and 62 CUDA phases beside 62 CPU binary64 phases. Source
33570817/67108864 has actual double-rounded half value 1/2 instead of direct
half 1025/2048, in both owned range and executed forecast. Fault controls
cover crossing-state retention, later CUDA commit failure and one-ULP
conformance failure; cancellation/readmission/retirement keep spent alpha
and forbid old-target or wealth reuse.

The full 1,109-phase owned CUDA prefix audit now also checks exact forwards.
The complete existing reference/CPU persistence, ordinary-event, binary64,
installation, host-failure, ingress and finite-run audits pass. This does
not reissue the frozen 21-script CPU release or grant a new target release.
`OWNED_CUDA_PERSISTENCE.md` states the proof and remaining scope. Actual
build/copy/install, full device resources and target run integration are
next; `PAIRED_CUDA_CROSSED` is only conditional same-path evidence. No
Foundation/ERC change or additional static architecture case is needed.

## 74. Prove and execute resident CUDA installation (2026-09-13)

Installation does not require a new semantic architecture action. In the
current registered realization, candidate and incumbent already coexist in
one actual arena; its entire allocation and allocator reservation belong
to both roles from birth, once globally. Their complete CUDA learners can
therefore retain object identity through a deployment change. This is a
physical transition argument for that realization, not a general assertion
that model installation has no copying or resource costs.

`CudaInstallContract` now registers that transport in the immutable CUDA
manifest. Runtime checks its historical native winner, independently current
reference/CUDA crossings and matching complete starts. The proposal maximum
belongs to its original constructor boundary; it is not asserted to remain
a current optimum after fresh learning. Same-graph newborns cannot inherit
the selected lineage, starts or wealth.

The device frame checks the registered stream is quiescent, the arena has
no active phase and its settings/allocation history remain valid. Every
current candidate must retain its owned device phase and complete learner.
Initialized extent ownership precedes numeric readback, then metadata and
raw state are checked. All old/current/staged/forecast objects and the full
arena history stay in the private frame. Target and old base also satisfy
their current reference/CUDA relations at a complete optimizer boundary;
optional CPU binary64 state is preserved and checked.

One common private root transaction now implements CPU and CUDA installation.
All fallible checks, readback, packed metadata allocations and lease
preparation precede one complete root publication. CUDA objects and extents
stay identical. The target becomes deployment, the incumbent a retained
shadow, and all old live persistence and continuing searches close together.
History and alpha remain; initialization-phase extent labels retain their
provenance instead of becoming fictitious exclusive resource-role leases.

Failure testing exposed why raw-value identity alone is inadequate. An
injected gradient shape change preserves its bytes but invalidates complete
learner state. Such observed corruption now halts the prefix and makes old
crossings unusable, even though no new deployment was published. Another
injected view crosses its initialized extent; ownership must reject it
before numeric readback can inspect that unowned range. A pending external
kernel prevents installation's quiescence premise. Benign late/unknown-frame
failures preserve old learners/evidence/frontiers and permit a new paid
attempt, retaining work, peaks and unrecycled physical IDs.

The actual endpoint completely evaluates classes of 35, 774 and 124 native
members. Their installed continuations have 151, 870 and 240 independently
replayed CUDA phases alongside the same CPU binary64 counts. The larger
case installs nonzero learned parameters at cursor 18; the recurrent class
preserves both delayed positions. Observational tracing sees the old root
and then one complete new root. All retained actual device objects, extents
and lifetime allocation counters are identical across publication.
Another 35-member run omits the optional CPU binary64 learners and still
checks 151 CUDA phases through installation and later ordinary learning.

A continued Runtime installs twice at 22 and 38 after two complete
35-member selections. The second starts at 24 against the actual new
baseline with fresh identities and wealth one. Both receipts remain; four
alpha allocations consume 3/4 and a later admission is refused. An
independent rounded replay checks all 306 CUDA phases. Real immutable byte
and work caps refuse installation preparation even when existing model
buffers fit. These tests retain only a compact aggregate evidence file.

The complete CPU installation, owned Compiler policy, host-allocation and
finite-run regressions pass with the shared transaction. This does not
reissue the frozen CPU release. The last owned-policy bounded fault hook
had to follow the transaction body from `install_cpu` to `_install_owned`;
its intended nested host failure then passes in the unchanged 64 MiB job.
The full CUDA prefix and persistence regressions also pass.
`OWNED_CUDA_INSTALLATION.md` fixes the
scoped theorem and executed evidence. Full device resource accounting and
owned target policy/run/release integration remain the active frontier;
model science remains HOLD. The unified resource law and ERC-1 stay frozen.

## 75. Separate native allocation observations from complete device claims (2026-09-13)

The next resource audit obtains an actual indistinguishability witness.
Starting with the same 16 MiB native arena, direct CUDA Runtime calls allocate
a disjoint 32 MiB buffer, write it, synchronize and free it. The entire arena
snapshot is identical before, during and after, including the native lifetime
counter `(1, 16777216, 1)`. Even observing while the foreign allocation is
live cannot reveal it through that projection. This differs from a foreign
PyTorch allocation, whose lifetime counter increases even after release.

The direct calls intentionally lie outside the registered Runtime API. They
do not falsify its scoped arena theorem or provide a new FP action. They
falsify promoting native allocator observations into total CUDA allocation
history. Any cap that distinguishes those histories requires an additional
coverage premise or a sound conservative reservation; faster sampling of
the same insufficient projection does not decide it. No exact whole-device
physical-residency peak is inferred from the successful allocation and write.

Trying to bind the test's actual runtime also corrected a metadata error.
Torch is built for CUDA 13.2 and its shipped DLL describes version 13.2.75,
but `cudaRuntimeGetVersion` returns 13040, or 13.4. Current NVIDIA documents
explain Windows CUDA 13 dispatch to the display driver's packaged runtime.
The repository's earlier CUDA_runtime fields stored `torch.version.cuda`;
they identify the build tag. Their interpretation is corrected without
rewriting immutable historical evidence. Actual per-phase/forecast numerical
checks remain checks of the executed outputs, not unseen-kernel theorems.

Read-only device inspection confirms RTX 3090, driver 616.92, WDDM and
24,576 MiB total memory. Process-memory entries are unavailable under this
model, as the NVML specification states. DXGI documentation offers current
usage and a target budget/reservation hint, not an enforced lifetime peak
cap. A DXGI execution audit has not been claimed.

`CUDA_RESOURCE_OBSERVABILITY.md` records the observation argument, primary
sources and exact remaining scope. The reproducer retains a small aggregate
result and frees foreign storage before reporting. Target resource/run
registration must distinguish actual runtime from build metadata and justify
coverage/enforcement or a conservative reservation. This is progress on the
active device frontier; Foundation, XVII.31 and ERC-1 remain frozen.

## 76. Close a physical framebuffer upper and bind the actual device (2026-09-13)

The allocation-observation obstruction does not prevent every resource
decision. For a registered physical domain of capacity C, all resident byte
locations belong to that domain, so C bounds residency uniformly over time
and over histories compatible with an incomplete observation. Charging the
whole domain to both roles, once globally, gives a conservative admissible
realization when all three caps cover C. This does not recover allocation
history, erase complete state or guarantee exclusive available capacity.

`CudaDeviceContract` implements that rule for the board's physical framebuffer.
The private owner maps the actual CUDA ordinal through native PCI bus to
NVML UUID and capacity. It separately binds actual runtime/API 13040 and
display driver 616.92, while Torch's CUDA build tag stays 13.2. The observed
capacity is 25,769,803,776 bytes, charged to both roles. A wrong version or
a cap one byte too small is refused before the first native tensor allocation.
No caller-supplied observation or device handle can establish the premise.

Native identity is checked on public authority/continuation entries, and
the resident installation frame retains the exact binding and initial identity.
Failure closes old crossings and install authority even after the observer
is restored. The adversarial review reproduced a missing unexpected-error
boundary through `snapshot()` in this new work; that path now also marks
the root terminal. Original unexpected exceptions survive a simultaneous
native-cleanup failure. These are injected executor faults, not spontaneous
device failures or Foundation counterexamples.

The actual 32 MiB foreign allocation remains invisible to native tensor
observations while an ordinary Runtime event executes. Both histories fit
the same proved 24 GiB framebuffer upper. It is not a measured peak or a
cumulative allocation bound. A separate worker, fenced before execution in
a 4 GiB Windows process/job, performs the 35-member native selection, obtains
fresh reference/CUDA evidence, installs and continues the learner. Its 151
device phases pass independent exact rounded replay. Actual host lifetime
commitment is about 2.1 GiB, native tensor allocation 16 MiB, and the board
charge 24 GiB; these typed coordinates are not added as disjoint bytes.

`WHOLE_BOARD_CUDA_RESOURCES.md` states the capacity argument, platform API
premises, complete failure/transport scope and minimal executed evidence.
The next work is owned target policy, finite run/report integration and a
complete scoped target release. Exact foreign allocation volume, arbitrary
GPU instructions or all-system memory are not inferred from this upper.
No static case expansion, ERC-1 change or model-science claim is introduced.
Complete CUDA installation/prefix/persistence regressions pass, including the
trained 774-member class, 64 short streams and all 32 null branches. Shared
host-failure and CPU finite-run regressions pass; all 38 package files import
without Torch. The frozen CPU release is not reissued by these targeted checks.

## 77. Compose the owned CUDA strategy and finite run boundary (2026-09-13)

The existing Compiler strategy depends on owned search completion, fresh
admission/crossing and reachable installation results. It therefore extends
to the already registered CUDA path without another semantic architecture
action. `CudaCompilerPolicy`/`CudaCompilationStep` explicitly name the CUDA
rule; path-specific records keep the actual CUDA identity. The shared Runtime
strategy still owns every Compiler control and accepts only ordinary event
transport from its caller. The target policy requires the live host binding
and actual device contract, plus resident transport when compilation is used.

The completed CUDA policy stage now publishes inside the same root/lease
transaction as its installed learner and receipt. Failure to retain that
record cannot leave an installed model with an old retryable stage. Separate
reference/CUDA evidence spends global alpha normally; a refused admission
retains each path's concrete reason instead of losing it in a generic result.

At the registered finite horizon, Runtime retains partial optimizer units
and reports unfinished stages as unresolved. CUDA closure preparation checks
all retained current learners and their complete state relations, initialized
extents and the quiescent device frame. Diagnostics come from owned forecast
words. Device binding, current transport, checked/nonchecked phase counts,
historical reference decision classes and spent alpha accompany the complete
snapshot. After paid report allocation, final identity verification precedes
the single run-closure publication. A prepared buffer is not a sealed run.

The actual two-stage path installs two 35-member selections at 22 and 38 and
seals at 60, with 456 independently replayed CUDA and CPU phases. An initially
attempted 40-event fixture correctly refused its second 30-epoch admission at
24: only 16 future events remained. The successful fixture preregisters the
full 60-event stream; the original refusal is retained as a control, with no
new identity or alpha debit. No FP resource rule was relaxed to pass it.

The full audit also exercises trained/recurrent installation, no optional
CPU learner, short complete branches, partial units, unfinished stages and
search allowance exhaustion. Report failures after installation retain the
completed target and event without run completion. A same-value tensor shape
mutation after report allocation prevents final verification; even its owned
prepared report bytes cannot revive authority after the view is restored.
Admission-policy retention and combined install-policy preparation failures
have distinct terminal/no-install outcomes.

One whole-run trace of the 774-member test exceeded the external audit
watchdog. Restricting observational tracing to every expected installation
boundary removes that overhead; receipt/cursor equality still checks every
actual publication. The same full class and FP budgets then pass. A static
method fault hook and valid-argument terminal probes were corrected in the
audit, without changing Runtime behavior to accommodate them.

The complete minimal audit passes in 32 pre-fenced Windows workers. The
774-member trained run independently replays 970 CUDA and 970 CPU phases;
the recurrent run replays 320 of each. All 16 four-event binary streams
pass 776 CUDA phase checks, with eight baseline decisions and eight unresolved
evidence outcomes. Maximum completed job commitment is 2,794,962,944 bytes
under the 4 GiB cap. Full CPU owned-policy, finite-run and host-allocation
failure regressions pass; the affected CPU policy-failure section was checked
again after the final diagnostic change. All 39 package files import without
Torch. These checks do not reissue the frozen CPU release.

`OWNED_CUDA_POLICY_RUN.md` gives the scoped composition and publication
argument. The next work is the existing hierarchical fixture on actual AMP
and complete target release integration. Its strong SUM training tie and
identifiability controls remain required. A sealed stream is neither current
CUDA optimality, structural forcing nor model-science authority.

## 78. Execute the existing hierarchy and its limits on owned AMP (2026-09-13)

The same pure token-task registration now feeds either the Reference/CPU
or CUDA audit before Runtime construction. No discarded helper Runtime,
hidden partition or supplied learned state enters the target path. The
native grammar, empirical-upper solver, `(1,8)` initializer, zero learning
rate and complete ordinary tape retain their previous scope. The selected
endpoint's indicators/products are binary, its masses are exactly one and
nine, and only its final binary32 division rounds the forward distribution.
`OWNED_CUDA_HIERARCHY.md` explains this instance and the comparison boundary.

At n=32, the actual owned strategy attains the historical reference upper
with one 74-node witness in a class containing at least 2^6540 source-only
strings. It obtains independent fresh CUDA evidence, installs at 330 and
continues to 622 without flushing its last two partial-unit events. All
1,963 CUDA and 1,963 CPU binary64 phases pass independent exact rounded
replay. The full 1,024-context reference conditional is also checked; that
count does not describe additional unexecuted device observations.

Actual negative controls remain decisive. A smaller five-node SUM-only
learner reaches the same exact train upper and matches the hierarchy's raw
forecast words on all 30 repeated training observations. Two disconnected
worlds produce identical observed data, proposals, graphs and training
objectives. Both target learners install at 40 and seal at 42, despite the
opposite unseen relation (0,2). Fresh comparison with an incumbent cannot
recover information absent from that stream. A misleading but connected
training path attains its upper and then finishes fresh evidence unresolved
without installation. None of these finite tapes establishes a stochastic
producer law, population identification or necessary PRODUCT structure.

All five actual workers pass 2,701 CUDA and 2,701 binary64 phase checks.
The n=32 peak packed payload is 313,552,643 bytes, consumed native arena
extent 1,944,952 bytes inside its preallocated 16 MiB, and completed job peak
3,905,241,088 bytes inside the original 4 GiB cap. Whole-board 24 GiB VRAM
remains a separate uniform upper. No resource cap or Runtime semantics was
changed to pass this experiment. The report drops identical graph/data/device
fields only after direct equality checks; per-worker outcomes and native job
records remain. That report-only reduction uses the complete executed result
without rerunning unchanged numerical work. CPU n=4 bounded hierarchy,
identification and all unresolved-case regressions pass after fixture extraction.

The next work is complete target release integration and then registered
RTX 3090 model science with competitive baselines. Foundation/ERC-1 remain
frozen and no additional static resource cases are prerequisites.

## 79. Freeze the integrated scoped Reference/CPU and target AMP Runtime (2026-09-13)

Source `5e55eb4f359016d18d68239938bdfb15893238eb` passes the complete target
integration: all 21 current CPU and 10 complete CUDA audit scripts execute
from one clean clone without hardlinks. All 38 package submodules import
without Torch. The CPU suites can overlap; actual CUDA suites execute
serially. The driver checks complete report sections, concrete class/branch
coverage, process exits, owned host/device identities and source cleanliness.
Earlier component PASS files are not used as execution substitutes.

The integration runs from 01:37:52 to 02:07:33 UTC on 2026-09-13 under
CPython 3.12.9 and 64-bit Windows 11. No implementation, audit or budget
change was needed during this run. It preserves all 47 Reference obligation
scopes and executes the target components 13/16/20/28/29/30, plus shared
physical resources and the existing hierarchy/identifiability controls.
The static theorem rows remain premises rather than invented GPU test flags.

Actual RTX 3090 binding again distinguishes Torch build CUDA 13.2 from
native runtime/API 13040, with driver 616.92, PCI 0000:0B:00.0 and the
original board UUID. The whole-board 24 GiB residency upper, native arena,
host commitment and packed resource histories retain their separate types.
No exact FP VRAM peak, exclusive allocation or GPU instruction/time cap is
inferred from them.

The target policy/run's 32 independently fenced workers all pass. Its
trained 774-member and recurrent 124-member classes, 16 complete finite
branches and report/installation failure controls are included. The n=32
target again installs at 330 and seals at 622 with 1,963 independently
checked CUDA and binary64 phases. Its completed job peak is 3,905,482,752
bytes under 4 GiB, including independent final replay. The smaller SUM
training tie and both identifiability controls remain active negative
results, not swept into a model-quality claim.

`CUDA_RELEASE_SCOPE.md` fixes the exact boundary and
`FP_CUDA_RELEASE_AUDIT.json` retains the 90,000-byte integrated evidence.
The declaration is documentation/evidence only, with no change to tested
implementation or audit code. The earlier CPU release at `ebe2c4c` keeps its
own identity; the declaration does not recursively test itself to chase a
new commit ID. Foundation definitions and ERC-1 resource laws are unchanged.

Registered RTX 3090 experiments are now unheld within the tested scope.
The next work is measured resource/model behavior with competitive baselines,
starting from the existing known-table constructions and their strong
fixed-P dyadic/Horner, shared-reciprocal and exact-singleton controls.
This is an experiment choice, not an added release gate or permission to
expand the parked static program. Reopen Foundation only for an experimental
correctness counterexample to its declared semantics.

## 80. Register the first post-release RTX 3090 resource experiment (2026-09-13)

`experiments/erc1_rtx3090/README.md` preregisters 54 configurations on the
two existing rational LIMIT_ONLY tables. It compares fixed-P dyadic/Horner,
a fractional-Horner control, shared reciprocal, and exact singleton versus
positive tail repair at matched slack. Equal coefficients are grouped and
exact singleton row scales use the smallest feasible denominator. No target
result is used to choose these constructors, depths, caps or tolerances.

The exact preflight checks all 54 complete context tables, forward loss
differentials and 257 fractional-Horner coefficients without importing
Torch. The mixed table's ideal excess denominator is six, not three;
registration uses its own correct positive-tail slack and stays at h<=1.
The largest graph has 314 nodes. No Foundation, ERC-1 or frozen Runtime
code changes. Target execution and scientific interpretation are next.
