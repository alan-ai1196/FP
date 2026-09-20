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

The first target execution retains 45 completed worker results at `ef2357f`.
The next worker (mixed exact Horner, n=5) exposes an experiment replay
assumption: a failed evidence write leaves the paid admission marker,
not a complete packed phase. This is the frozen Runtime's already audited
failure behavior. The report adapter now checks that marker and proves the
attempted phase exceeds 131,072 bytes, separately counting unretained full
records. Raw diagnostic outputs can still be independently replayed; they
gain no packed-evidence or closure authority. The failed reporting worker
is rerun; the 45 completed measurements are retained without repetition.
No constructor, depth, tolerance, cap, protocol or Runtime change is made.

## 81. Measure the resource law against strong SUM baselines on RTX 3090 (2026-09-13)

All 54 preregistered configurations now complete execution: 44 owned streams
seal and ten halt unresolved. Forty-five worker results retain source
`ef2357f`; the final nine retain `c95ef5b`, whose changes only adapt the
reporter to exhausted evidence and preserve partial results. The prior
measurements are not rerun or relabelled. No frozen implementation, scientific
parameter, tolerance, resource cap or protocol changes.

At the critical cap, scalar's strong fractional-Horner control reaches
actual retained-mass error 1/43688 with S/P/E=17/0/24. The reciprocal
reaches the same error with 12/7/30: it does not dominate node and edge
counts. For mixed Q, reciprocal 17/7/38 improves over fractional Horner
36/0/51 at the same error 1/65532, with consumed native extents 46,216
versus 75,336 bytes. These are finite measured Programs, not a complete
class Pareto certificate or physical VRAM savings.

In both tables n=3 to n=5 improves exact reciprocal error by more than
10^14 without improving actual AMP mass or rounded-output error. Ordinary
Horner at L=32 underflows and fails, whereas fractional Horner survives;
omitting the stronger comparator would overstate the PRODUCT advantage.

At small positive slack, exact-reference graphs diverge physically.
For scalar n=3 the fractional-Horner total exceeds cap by 9/32768;
ordinary Horner and positive tail repair remain below by 7/32768. All
three are exactly Q in reference arithmetic. Critical-cap approximants
also satisfy these looser ranges and have smaller actual errors, so
reference exactness is not itself the physical objective. At larger slack,
mixed Q can have exact normalized retained masses while its raw single
division still errs by 1/100663296.

The ten unresolved runs comprise four CUDA native prediction failures,
four CUDA rounded-total violations, one 138,136-byte phase that cannot
fit 131,072 prepaid bytes, and one actual binary64 stored-mass-sum
violation before the second context's CUDA execution. Raw diagnostic
outputs are independently replayed without granting failed packed evidence
or a complete stream. Totals: 2,133 CUDA outputs (2,124 checked plus nine
failed), 2,134 binary64 outputs (2,133 checked plus one failed), 828 exact
reference events and a separate 270-vector forward/reverse gradient audit.

The maximum measured packed peak is 7,485,943 bytes, consumed native extent
168,296 bytes, and completed Windows job commitment 2,381,942,784 bytes.
The physical 16 MiB arena and whole-board 24 GiB envelope do not shrink.
No timing or model-quality gain is inferred. The 148,377-byte result and
standalone SVG are reproducible through `analyze_frontier.py`; no weights,
dataset, full operation log or expanded graph is retained.

`experiments/erc1_rtx3090/RESULTS.md` records the scientific interpretation.
Foundation/ERC-1 and the scoped Runtime remain frozen. The next research
direction is model science with structure inferred from ordinary data,
legally unseen contexts, competitive baselines and the existing hierarchy
identification controls. More static or half-specific cases are parked.

## 82. Separate ordinary-data inference from the current empirical-upper gate (2026-09-13)

RN-1 preregisters 18 relation-inference cases: n=8,16 and four seeds under
conditioned one-flip-per-edge versus IID 1/10 noise, plus the existing
disconnected-world control at n=8. Each FP run uses the frozen complete
Runtime; an independent exact forest posterior and actual AMP table
predictor supply a strong baseline from the same revealed training data.
Frozen candidate quality on unseen relations is separated from search
completion and subsequent deployed policy behavior. No latent bits or
posterior forecasts enter Runtime, and no new semantic action is introduced.

Before target execution, exact analysis exposes a substantive selection
bottleneck. With ten labels per edge, the current uniform baseline/proposal
can attain the categorical empirical upper only if every split is 5:5
(baseline) or every split is 9:1 (candidate). Under IID noise its arithmetic
eligibility is p9^(n-1)+p5^(n-1): about 6.65e-7 for n=16 and 1.71e-13 for
n=32. Yet all strict empirical edge majorities recover the full relation
with probabilities about 0.976 and 0.951. This is a solver/objective gate,
not absence of information, native expressibility or a Foundation loophole.

All 121 two-edge count patterns are checked against actual native proposal
scores; exactly five are eligible. The posterior control agrees with full
hidden-assignment enumeration in 40 small forest cases. Conditioned and IID
training laws require different posteriors; the control respects that
difference. Protocol, algorithms and the scoped eligibility lemma live in
`experiments/relation_noise/`. Target/model outcomes remain to be executed.

## 83. Execute RN-1 and expose the ordinary-data proposal/selection bottleneck (2026-09-13)

All 36 preregistered workers complete at `5b050c7`, without changing code,
parameters, caps or reporting during execution. Every FP ordinary stream
seals; ten searches attain a checked categorical upper and nine candidates
actually install. Independent audits cover 12,564 CUDA phases, 12,564
binary64 phases and 2,688 separately executed AMP posterior forecasts.
Post-analysis recomputes 64 score records with exact Brier/probability
checks; the compact 125,451-byte journal and standalone SVG retain the result.
Frozen Foundation/ERC-1/Runtime and the original protocol remain unchanged.

The eight conditioned connected cases construct the native S6/P4 hierarchy,
install twenty observations after training and predict unseen relations at
the noise floor, CE 0.325082973. The strong same-cutoff posterior ties them.
Deployed-stream CE is larger while persistence awaits installation, and is
reported separately from the frozen candidate comparison.

All eight IID cases stop before candidate construction: the empirical
readout scale does not occur in the initializer (1,8). No alpha is spent,
no class proof is issued and deployed CE stays log2. This is not a lack of
relation information: every observed strict edge majority is correct, and
the actual AMP posterior scores 0.325082982--0.325212273 on unseen relations.
Post hoc integer likelihood comparisons show the already reachable scale8
beats scale1 and uniform on every sample. This is a diagnosis, not an
unexecuted candidate granted construction/forecast/installation authority.
The separately proved exponential categorical-upper gate remains even if
proposal value choice is improved.

The two disconnected cases retain identical training/candidates and
opposite cross-component truths. Frozen-candidate CE is 0.325082973 in
world A and 1.603468182 in B, while the posterior's 1/2 cross-component
forecast scores 0.592766033 in both. Mean candidate excess is
(8/11)log(5/3). A installs at 80; B has no install receipt and retains an
unfinished evidence stage when its finite stream seals. No population
identification or finite no-crossing rejection claim is made.

Read `experiments/relation_noise/RESULTS.md`. The research obstacle is the
current solver/strategy, not a need for more static cases or a Foundation
semantic mechanism. Existing installation requires a historical training
maximum, whereas the foundational fresh-evidence theorem requires a
predictable owned candidate with continuous bounded same-path gains.
Investigate separating honest unresolved class optimization from a
prospective candidate decision, preserving all value, ownership, lineage,
resource, bridge and atomic transport obligations. An expanded strategy
needs its own endpoint evidence; the old release remains frozen at its
tested scope and cannot certify an unexecuted extension.

## 84. Remove training optimality from prospective installation authority (2026-09-13)

Foundation's fresh bounded-gain argument conditions on the complete admission
filtration; it needs a predictable, continuously identified candidate, not
a past empirical maximum. Existing paired admissions already own the exact
reference/physical starting states, cursor, program/lineage IDs, comparator
and spent alpha. Their current crossings validate the continued learners.
This supplies the provenance needed by the same atomic physical transition.

The v2 installation port therefore makes historical class selection an
optional additional checked assertion. It still rejects unowned/false IDs,
wrong pairs and same-graph newborns, and retains all current state, numerical,
resource and transport checks. The owned v2 policy can advance an actually
compared improving candidate through fresh evidence while keeping the full
constructor class unresolved. Final run decisions and receipts distinguish
these claims; no new proposal signer, architecture action or class proof is
introduced.

The relation proposer now selects its readout value by guarded exact
likelihood comparison over the available initializer prefix. It does not
calculate a free fitted coefficient and demand an exact match. Counts and
the selected initialized value remain owned, and additional work is prepaid.
Independent checks cover 605 count/initializer/slot-cap combinations and 500
actual native forward likelihoods, including duplicated values, both one-
and two-slot paths and arithmetic exhaustion.

CPU and actual RTX 3090 audits exercise incomplete bounded search and a
stopped enumeration after seven of 35 native members. Both install without
historical class proofs, and their sealed reports still say `UNRESOLVED`
for the original class. An actual scale1 candidate instead exhausts its
finite evidence without installation. Wrong authority, partial optimizer
units, stale evidence, unavailable preparation work and unsupported complete
state/device transport are refused. A real negative control retains the CPU
fixture's work allowance on CUDA: installation and terminal reporting remain
unresolved. The positive enumerated case uses the already registered CUDA
policy allowance; no semantics or numerical tolerance changes.

The original full CPU installation, owned CPU policy, reference acceleration
(including n=32), CUDA installation and CUDA policy/run scripts pass. These
regressions and the new matrices establish the stated extension scope, not
a rerun of all 31 baseline release scripts. Read
`theory/proofs/OWNED_PROSPECTIVE_SELECTION.md`. The original RN-1 evidence is
unchanged; its analyzer now guards the unchanged metric/rounding dependencies
without forbidding later Runtime strategy research or relabelling old runs.

RN-2 fixes twelve known-tape diagnostics and eight previously unexecuted IID
seeds, with the same strong retained/new AMP posterior comparison. The
protocol is in `experiments/prospective_relation/PROTOCOL.md`; model outcomes
are still to be executed. Foundation/ERC-1 and the old release retain their
original scopes. This result removes a solver/authority bottleneck; it does
not establish population identification or a superior model.

The committed extension source `9ec4c33` now has retained independent audit
records: eight CPU workers / 1,120 binary64 phases and nine RTX 3090 workers /
1,323 CUDA plus 1,323 binary64 phases. Their actual completed-job peaks are
35,483,648 and 2,297,847,808 bytes. The compact records are
`evidence/minimal/FP_PROSPECTIVE_SELECTION_{CPU,CUDA}_AUDIT.json`.
The RN-2 runner is registered in `experiments/prospective_relation/run.py`.
Its preflight verifies the 28 fixed tasks and independently rechecks all
64 RN-1 score records without inspecting new-seed labels. It retains
source-bound failures, full-domain and unseen FP scores, and the original
optimization decision even after installation. Actual RN-2 execution follows
this registration; no model outcome is implied by the preflight.

## 85. Prospective IID models succeed while full training classes remain unresolved (2026-09-13)

RN-2 completes all 28 new workers at registered source
`5bcbb49665f5c1222127c50a5d399628377c0a3d`: twenty FP runs and eight separately
executed AMP posterior controls. Twelve known diagnostics reuse the original
RN-1 control journal at `4d04595` with original worker source `5b050c7`;
their case/count/device identity and all 64 RN-1 scores are independently
verified. No worker is rerun after changing a parameter or source.

All twenty FP streams seal. The eight formerly failing IID samples and all
eight preregistered new IID samples now construct initialized scale8 native
models and install them through actual paired evidence. Every one of those
sixteen full training classes remains unresolved, with no class-maximum
proof. Four conditioned/disconnected diagnostics retain their actually
attained historical categorical upper. Nineteen cases install; disconnected
world B retains its finite EVIDENCE outcome without installation. A sealed
end supplies no future continuation authority.

All observed IID edge majorities are correct. Each connected frozen candidate
has unseen CE H(1/10), exact expected Brier9/50 and zero latent-relation error.
Known/new n=8 mean deployed CE is 0.432435/0.443389; known/new n=16 is
0.352688/0.358384, compared with uniform0.693147 for RN-1's failed IID cases.
The strong AMP posterior remains near the noise floor; its new n=16 mean
is 0.325247. Known-tape diagnostics and previously unexecuted seeds remain
separate, and eight new samples imply no population success rate.

New n=16 seeds4/6 install thirty fresh events after training; the other IID
cases install after twenty. Independent analysis reconstructs the exact
dyadic wealth, checks log intervals against 100-digit Decimal, stops at
first crossing and advances to a complete optimizer boundary. It reproduces
all twenty prospective decisions without calling Runtime or rerunning a
model. Candidate loss is never substituted for actual deployed loss.

The unchanged disconnected worlds retain frozen-candidate CE0.325/1.603
and posterior0.593 in both. Their equal-world candidate excess remains
`(8/11)log(5/3)`. More generally, subtracting the posterior's conditional
expected CE from any fixed predictor's gives Bernoulli KL; success in a
realized world cannot establish Bayes dominance. Removing the training
maximum prerequisite does not identify unobserved relations.

Every executed FP path is independently replayed: 17,064 CUDA and 17,064
binary64 phases. The new posterior workers check 1,280 actual forecasts.
Post-analysis recomputes 96 new score records and all twenty prospective
decisions. Peaks are 198,042,162 packed bytes, 898,200 bytes of consumed
native extent and 2,992,779,264 completed-job bytes, within the unchanged
caps. The actual RTX 3090/device/build identity matches the retained controls.
The approximately131 KB journal and86 KB SVG retain no weights, dataset or
bulk phase histories. Read `experiments/prospective_relation/RESULTS.md` and
`evidence/minimal/FP_PROSPECTIVE_RELATION_EXPERIMENT.json`.

This closes the scoped RN-1 proposal/installation obstruction. The remaining
model-science question is representing and using uncertainty through native
reachable value paths, while keeping frozen-model and adaptive deployed
comparisons at their proper information cuts. Foundation R4, XVII.31 and
ERC-1 remain frozen; no static resource case or semantic architecture action
was added. The baseline release and each experiment retain their original
sources and scopes.

## 86. Preserve unresolved component flips with existing native products (2026-09-13)

The v3 relation proposal constructs four group SUMs and four pair PRODUCTs
per consistent untied empirical component, with two shared readout heads.
At unit1 and an available scale, this equals the average of the old hard
normalized predictions over all relative component flips on one-hot queries.
Across components all evidence products vanish; the unchanged positive
base supplies uniform uncertainty. No posterior coefficient, semantic action,
new complete-state coordinate or inherited evidence is introduced.

The exact audit checks 7,320 prediction equalities, reversed presentation,
14,640 Brier inequalities, 30 unchanged connected graphs and 605 reachable
scale cases. Tied constraints retain their counts; a balanced chord inside
one component still affects scale likelihood. Directed observations remain
separate in the all-categorical upper. A larger literal witness can exceed
the original grammar and must leave search unresolved.

Two explicit limits prevent a premature quotient. On a legal soft mixture,
the component endpoint predicts5/6 while the true hard-prediction average
is7/10. At initialized scale0, uniform predictions conceal a nonzero scale
gradient: one legal update yields17/33 while a zero-slot learner stays1/2.
The scoped CPU/CUDA matrix will retain source-bound records; RN-3 registers
eighteen new workers before its new seed/support cases are inspected.
The model study must distinguish equal-cutoff frozen risk from adaptive
deployed risk. Its target outcomes are still pending.

Both source-bound v3 matrices now pass at `ad2c350`: six CPU and six actual
RTX 3090 workers, each with 1,127 binary64 phases; CUDA independently checks
1,127 target phases. Completed-job peaks are 39,161,856 and 2,364,469,248
bytes. The n=32 reference regression also passes with its unchanged 74-node
witness, installation330, seal622 and 1,963 binary64 phases. No old release
or RN-1/RN-2 model worker is relabelled or rerun to refresh its source.

RN-3's `run_study.py` now registers the eighteen fixed workers and preserves
separate frozen/deployed outcomes, class scopes, actual phase audits, source
and completed-job records. Its preflight checks all registrations without
new labels, and recomputes 64 RN-1 scores, 96 RN-2 scores and twenty old
prospective decisions. The two historical journals stay byte-content equal
to their original commits. A preflight reader correction accounts for the
older RN-1 successful-job schema; it caused no target model execution.

## 87. Native fixed-cut uncertainty succeeds; adaptive learning remains a distinct obstacle (2026-09-13)

RN-3 executes its entire fixed matrix at
`a351da95dafab6d06fb609c044f5fb0efbc09e74`: ten FP and eight strong AMP
posterior workers, with no execution failure or parameter change. All ten
FP streams seal, nine install, and all eight new IID classes stay unresolved.
The two known diagnostics retain their actual categorical upper. Their old
v2 FP and posterior controls remain at `5bcbb49`/`5b050c7`, referenced through
the original journals at `2f24d18`/`4d04595`. No unchanged model is rerun.

The known equal-world frozen CE falls from 0.964276 to 0.592766, matching
the strong posterior in both worlds; the improvement is (8/11)log(5/3).
Yet their deployed mean worsens from 0.563488 to 0.626226. The old hard guess
plus fresh selection deploys only in A, using later labels; both v3 worlds
install at 80. This outcome was explicitly allowed in the protocol. A
fixed-cut improvement supplies no adaptive-deployment dominance theorem.

All eight new samples have correct strict majorities and scale8. Mean unseen
candidate/posterior/deployed CE is 0.592766/0.592766/0.663869 for n8,c2;
0.547310/0.547310/0.601999 for n16,c2; uniform 0.693147 for n8,c4;
and 0.652251/0.652256/0.669291 for n16,c4. Finite within-component posterior
uncertainty remains; these realized samples do not prove Bayes dominance.

Fresh waiting ranges from 20 to 160 events among installations. Independent
exact dyadic-wealth replay, with log intervals checked in 100-digit Decimal,
reproduces all ten decisions. n8,c4,seed10 installs after 60 fresh events,
leaving four cross-component queries and no improved deployed forecast.
Seed11 never crosses (maximum wealth 232785/65536 < 4) and seals without
installation. These finite outcomes are retained, not converted to a
statistical rejection or omitted to improve the installation count.

The result points to a deeper learning obstruction. Exact enumeration of
the four assignments left by known training shows that fresh event2's
cross label changes the next cross prediction at event4 to 41/50 or 9/50,
despite zero gain for the current uniform prediction. Runtime retains this
information. However, every component-local product has a zero factor on
cross-component one-hot queries. The fixed graph's evidence and current
parameter derivatives are identically zero for all legal weights. Raising
the learning rate alone cannot repair that support. This is a proof about
one native graph, not a Foundation failure or full-class impossibility.
The next target is reachable uncertainty that can use later retained data,
with owned learner/construction paths and strong adaptive controls.

All 7,688 CUDA and 7,688 binary64 model phases are independently replayed;
the new posterior workers check 1,280 GPU forecasts. Post-analysis verifies
72 new scores and ten fresh decisions. Peaks are 196,491,241 packed bytes,
1,242,336 consumed native bytes and 3,000,500,224 completed-job bytes under
the unchanged limits. The 83 KB journal and 28 KB SVG preserve no datasets,
weights or bulk histories. Read `experiments/component_uncertainty/RESULTS.md`.
Foundation R4, XVII.31, ERC-1 and the original baseline release remain frozen.

## 88. Balanced positive evidence keeps an ordinary learning direction (2026-09-13)

The v4 registered proposer derives the same empirical components, then
emits parameter-free token-pair products with tied within-component scales
and separate balanced unit coefficients for each component pair. Its initial
one-hot predictions equal v3, but its current-label derivatives do not.
At unit1/rate1/8, one cross label changes coefficients from (1,1) to
(33/32,31/32), giving65/128 on a corresponding next query; the opposite
label reverses the movement. This needs existing independent initializer
slots, not a posterior coefficient or new semantic action. Default v3 stays
registered separately; the full native grammar is not replaced by a menu.

The exact audit checks320 models,7,320 initial predictions,7,072 gradient
and one-step directions and484 count/slot cases. It catches a coupling
between scale choice and coefficient availability: reserving scale1 can
leave too few units even when scale8 is feasible. Feasibility now precedes
exact likelihood comparison. Runtime prepays64*n^2 additional proposal work
before dense emission; actual construction/storage retains its own charges.

CPU and CUDA functional cases learn both orientations and install current
nonzero-rate learners, including an unresolved full training class. Distinct
slot shortage and injected work shortage grant no false proposal or alpha.
The old normalizer10/scale8 boundary rejects a correct nonzero-rate update;
separately registered activation16/normalizer18 admits the positive tests.
This is an ERC-1 instance choice, not a semantics change or retuned model.

The tight-cap control exposes an old audit assumption: computed successors
are not necessarily published successors. Runtime correctly retains failed
phases and the old atomic root. The binary64 auditor now replays both and
checks the published root against the failed event's owned pre-target cut;
a fake promotion of unsafe staged values is rejected. Both target paths and
the full original binary64 audit pass. No Runtime publication rule changed.
Source-bound complete matrices follow the committed implementation.

RN-4 preregisters thirty workers: two known worlds and eight uninspected new
IID cases, with native rates1/8 and4 plus a strong exact/AMP adaptive posterior
per case. Fixed range/resource refusals and all model failures will remain.
No new model result is implied by the endpoint checks or registration.

The complete matrices subsequently execute from `803cdc2`: six workers and
1,960 binary64 phases per path, plus1,960 actual CUDA phases. Maximum CUDA
state/probability errors are5.31e-5/5.54e-5; native/normalizer error is0.003769,
all below the separately declared1/100 tolerances. Maximum jobs are41,385,984
CPU and2,393,673,728 CUDA bytes. The two minimal journals total25,883 bytes.
RN-4 now has its executable thirty-worker registration and an exact adaptive
posterior checked against48 independently recomputed full-joint forecasts,
including cycles. Fixed48-bit Brier enclosures prevent large denominator
artifacts. New target seed labels remain uninspected at this registration.

## 89. Native curvature propagates relation moments, with a zero-boundary counterexample (2026-09-13)

Two noisy path labels between three independent component orientations
change the next endpoint prediction to189/250. V4's independent readouts
stay1/2 on the untouched pair. A full linear assignment mixture can also
stay1/2: with additive SGD and inactive projection, its weights remain in
the span of individually queried parity characters. Representing a value
therefore does not imply learning the corresponding correlation.

For four relative assignments with positive polynomial weights phi(a),
base1, a shared output unit and uniform initial amplitudes, exact local
analysis gives matching endpoint probability
`1/2 + eta^2*phi'(a)^2*phi''(a)/(2*(1+2*phi(a))^3) + O(eta^3)`.
The common output coefficient has zero derivative at the two neutral
forecast cuts; it is not secretly frozen. An existing self-PRODUCT gives a
nonzero path signal. Pure squares also have absorbing zero coordinates:
rate4 eliminates two amplitudes and the opposite next label cannot revive
them. A native linear-plus-quadratic polynomial revives both in that control
while retaining curvature. Neither fact proves a globally reliable learner.

Explicit native graphs, independent forward derivatives, binary64 and
rounded AMP interpreters check64 label/rate/graph/grid combinations plus
two projection controls. The n3 mixture witnesses exceed the corresponding
RN-4 node cap; no Runtime construction or extra CUDA execution is claimed.
A separate scalar reduction checks936 forecast/successor comparisons in
all three arithmetic paths, supporting independent dynamic RN-4 analysis.
No target case or registered resource is changed. Read
`theory/proofs/TRANSITIVE_UNCERTAINTY_LEARNING.md`.

## 90. RN-4 learns native uncertainty and retains the dense-execution boundary (2026-09-13)

All thirty registered workers execute from `cffbadc`, with unchanged rates,
resources and source. Twelve n8 FP streams seal and install; all eight n16
FP streams halt at their first new prediction when actual CUDA phase
evidence exceeds the prepaid131,072-byte frame. Ten exact/AMP adaptive
posterior workers complete, consuming each new label only after forecasting.
No attempted outcome is excluded or rerun; unexecuted FP tails have no score.

In each known world, candidate CE is0.526949 at rate1/8 and0.440025 at rate4,
with deployed CE0.555822/0.495313. The new adaptive posterior scores0.370531.
The retained v3 controls score0.592766 frozen and0.626226 deployed at their
original execution sources. This comparison changes learning, constructor,
cadence and range together, not one isolated causal mechanism.

New n8 two-/four-component candidate means at rate4 are0.401997/0.488960,
versus strong adaptive posterior0.334035/0.350041; deployed means are
0.467520/0.569416. At rate1/8 the corresponding candidate means are
0.501828/0.659139 and deployed0.542259/0.674638. N16 posterior means are
0.330741/0.334428; its FP scores stay absent. All strict training majorities
are correct in these samples and all searches construct scale8. Sixteen
IID training classes stay unresolved; only four conditioned diagnostics
attain historical fixed-state empirical categorical bounds. The eight
halted streams never gain a final closure.

Independent post-analysis checks88 new dynamic scores and twelve reference/
AMP fresh decisions. The sealed runs replay6,552 actual CUDA and6,552
binary64 phases; the separate adaptive controls check1,408 GPU forecasts.
Failed-prefix complete oracle counts are not claimed. Maximum job, packed
FP and native extents are2,572,197,888 /81,202,893 /720,560 bytes. Checked
CUDA state/probability errors peak at0.000747681/0.000119088; native and
normalizer errors peak at0.00390625, below the declared tolerances. The
149,430-byte journal, standalone SVG and fixed48-bit Brier enclosures keep
no datasets, weights or bulk histories. Read
`experiments/adaptive_uncertainty/RESULTS.md`.

The model frontier now combines relation-moment propagation with owned
feasible execution. The preceding curvature control is a scoped mathematical
lead, not a free constructor or a model improvement theorem. Foundation R4,
XVII.31, ERC-1 and the original complete correctness baseline stay frozen.

## 91. Remove the shared output gate through a native polynomial constructor (2026-09-13)

The joint v5 constructor implements each orientation's `a+a^2` evidence by
putting its linear terms directly in the final head and attaching their
weighted inner SUM with the same slot. No output gate or extra self-PRODUCT
is needed. This works on soft sources too; the old square-of-feature graph
only had the corresponding one-hot identity. Removing k from an existing
learner would be invalid: after two matching labels the old/new predictions
are605786986482207/777750761524495 and17712419905/22813333329. They must keep
separate complete learners and fresh evidence.

The available unit-slot count bounds the relative-orientation family before
expansion. Feasibility precedes scale likelihood selection; connected cases
need no cross family. Runtime prepays64*n^2*(1+U) from the grammar-limited
prefix length U before inspecting its values; actual constructor charges
remain separate. No unsearched program is excluded and no new semantic
architecture action is introduced.

Exact audits pass320 models,7,320 initial predictions,25,752 gradient
coordinates,946 zero-coordinate recovery directions,726 scale/slot cases
and729 soft polynomial checks. The existing v4 exact suite remains valid.
Functional CPU and RTX3090 transitive endpoints check542 binary64 phases
each and542 actual CUDA phases, with fresh installation. CPU zero recovery
and tight-range refusal controls pass.

The initial CUDA native/state1/100 budget refuses a later prediction at
cursor57, after a prior valid installation. An independent rounded graph
replayer checks all256 phases including the completely retained failed
prediction, its exact error and non-acceptance. It does not borrow an old
crossing to authorize continued prediction. Positive CUDA fixtures instead
separately declare native/state1/16 and retain probability1/100; the old
budget's refusal stays a distinct control. The binary64 auditor reads the
owned pending record for a refused prediction; its full original regression
passes. No Runtime acceptance or publication rule changes.

The normalizer18, four-component initialization also fails after its first
nonzero update; larger-range functional fixtures are declared separately.
Source-bound complete matrices follow the committed implementation. This
is a constructor/learner advance, not a new model-quality result, static
resource law or full correctness release. Read
`theory/proofs/JOINT_POLYNOMIAL_PROPOSAL.md`.

### 91.1 Complete owned endpoint matrices

Implementation `9f9fa0b` now has seven CPU and eight CUDA fresh-job controls.
The CPU journal checks 2,496 binary64 phases; CUDA checks 2,752 actual phases
and 2,752 corresponding binary64 phases. Transitive, opposite and unresolved
historical-class proposals install at cursor 51. Both zero weights recover.
Slot/work refusal preserves no proposal or alpha spend; tight range stops
publication of its staged update. The stricter native 1/100 control retains
its installation at 51, then rejects prediction 57 with native error
43217193/4294967296 and probability error
1429926113775/31074450924605654. Its completed words are independently replayed;
the pending target remains unrevealed. Peak completed-job commit is
52,744,192 CPU / 2,491,232,256 CUDA bytes. The two journals retain 33,515 bytes
in total. No new model or full-release claim follows from these endpoints.

## 92. Joint model registration and the empirical sign obstruction

The v5 shared-SUM learner resolves the earlier missing native realization,
including a direct zero recovery direction. It still imposes empirical
internal signs. A wrong internal sign has true-parity probability at most
1/2 under every nonnegative parameter state. The new scoped proof derives
both a fixed-state uniform-domain risk lower bound and a weaker bound valid
for the evolving one-pass stream. For the selected n8 four-component wrong
majority tape these are approximately 0.5069369136 and 0.3365849799 at noise
1/10. The first cannot be compared as a lower bound to prequential scores
from different states. This restricts the emitted family, not Foundation
R4, retained observations or future native constructions.

RN-5 preregisters 31 workers before reading new IID seed labels: two FP
rates (1 and 4) on two known diagnostics, eight n8/n16 IID cases with c2
seeds 16/17 and c4 seeds 18/19, and one separately selected wrong-majority
stress tape. Nine new adaptive posterior workers accompany the new tapes;
the known adaptive posterior and v4 controls remain RN-4's original records.
The new protocol declares broader graph caps, normalizer/activation 256,
CUDA native tolerance 1/2 versus probability 1/100, 2MiB per-phase frames,
65536 output cells, 256MiB arena, 8GiB packed / 16GiB host caps, work 10^15
per role and a two-hour worker timeout. Bound-6 persistence changes the gain
multiplier to 1/8. These are registered new-run ERC-1 parameters, not a rerun
or correction of old model failures. The fully adaptive posterior keeps all
latent assignments and every subsequent label.

The pre-target independent trajectory oracle checks 1,224 exact/binary64/
rounded-AMP graph forecast and successor combinations plus 64 fixed-state
sign controls. The metadata-only preflight checks 31 tasks, posterior
algebra and cell envelopes without inspecting any new target tape. No RN-5
model score or completed worker is claimed at this registration point.

### 92.1 Preserve the inherited arena-auditor failure

Before any new IID or stress execution, source `e3df252`'s two known-A workers
failed the end auditor's literal `(1, 16MiB, 1)` allocation assertion. This
protocol had actually registered 256MiB. The 4,491-byte failure journal keeps
both completed jobs and traces, plus the explicitly interrupted known-B/rate1
process without a completed-job or score claim. Nothing from these attempts
is relabelled as a successful model result.

The auditor now checks the native allocation count and byte extent against
the immutable arena contract, also checking the actual tensor size. One old
16MiB and one 256MiB functional CUDA stream each replay 16 phases. The runner
amendment preserves the original protocol source, links the failure journal,
and changes no model/data/rate/resource/evidence parameter. The same 31-worker
matrix will execute with this corrected evidence check. No new IID labels
were inspected when making the correction.

## 93. Optimizer scale is retained continuation information

During the unchanged RN-5 execution, the native joint polynomial gives a
closed unrounded mass-drift identity. In proof coordinates u=(a+1/2)^2,
d=1-K/8, target/opposite masses M,N and T=M+N, define
A=d*(1/M-2/T) and B=(M-d)*(1/T-1/M)^2+(N-d)/T^2. Then the unprojected step has
T'-T=-4*eta*A+4*eta^2*B. For K8 the first-order term cancels and nonnegative
projection gives strict mass growth for every positive rate. Under eta<=T/2
it grows by at least 4*eta^2*N/(T*M); larger rates project all opposite
amplitudes to zero and still increase mass. A fixed finite mass cap cannot
contain an infinite unrounded cross-query continuation. No such monotonicity
or stopping-time claim transfers to grid16 or actual AMP.

The general scale-invariant norm-growth mechanism is known (Arora, Li and
Lyu, arXiv:1812.03981, Lemma 2.4); the proof explicitly cites it. The native
shifted polynomial, base cancellation, projection conditions and resource
interpretation are derived here. Two initially uniform K8 learners related
by shifted-amplitude scaling give different next predictions, 25/41 versus
1369/2594, under rate 1. The latter equals the first learner's rate-1/4 value.
Thus a current value symmetry is not a complete-learner quotient.

The independent full-graph synthetic audit checks 1,008 exact mass identities,
8,352 gradient coordinates, 288 moderate-rate and 96 large-rate projected K8
controls. Legal decreasing examples at K2/K4/K16 prevent a false extension;
K16 also audits the negative algebraic offset. The post-analysis separately
records descriptive grid16 scale changes and actual AMP forward normalizers.
No new architecture, normalizer feedback action, rate or target resource
parameter is introduced.

### 93.1 First completed RN-5 prefix, not the full experiment

Execution source `38b27b3` retains protocol origin `e3df252` and all three
earlier failed/interrupted attempts separately. Its first ten completed
workers contain eight sealed FP trajectories and two adaptive posterior
workers. Seven FP trajectories install. The independent analysis verifies
40 scores and eight fresh decisions, with 4,528 CUDA and 4,528 binary64
phases and 128 new posterior GPU forecasts. Known A/B have identical
candidate unseen CE 0.4120225463 (rate1) and 0.4684497346 (rate4), against
0.3705313268 for the reused adaptive posterior. Deployed scores are
0.5768125301 and 0.6107217723 with the registered bound-6 evidence wait.
The two new n8,c2 seeds average candidate unseen CE 0.3901146875 and
0.4436024324 versus posterior 0.3384927860. All remaining n16/c4 and selected
stress results are pending; none are reconstructed or imputed in this entry.
The full experiment, later failure statuses and final claims must follow the
completed source-bound journal, not this early prefix.

### 93.2 Continuous-mixture stationarity is not a reachable-state certificate

The same v5 graph admits a useful real-parameter relaxation. With
v_H=a_H+a_H^2+2/K and pi_H=v_H/sum(v), each one-hot cross prediction is a
linear mixture of relative-orientation parities. Any strictly positive pi
has a real nonnegative amplitude preimage, without asserting that its square
roots are rational, in Gamma or reachable by a profile. Cross-query CE is
convex in pi. The positive prediction-preserving direction
r_H=v_H/(1+2*a_H) has zero inner product with the native amplitude gradient.
At a nonnegative first-order stationary point every coordinate gradient must
therefore be zero, including zero amplitudes; convexity makes its relaxed
prediction globally optimal. This concerns one fixed full-batch CE objective,
not convergence of the actual finite-grid single-label learner.

The audit adds 336 exact radial-direction checks. A pure-square native graph
at zero amplitudes has zero gradients and uniform prediction, although
(2/3,1/3) strictly improves its 9:1 loss. Hence the linear term removes a
first-order boundary trap in this relaxation; it does not license erasing
scale or inferring an owned compiler optimum. Linear weights also share the
stationarity property; curvature's earlier role is the interior transitive
response. No model, resource, evidence or execution-source parameter changes.

### 93.3 A matching upper construction closes the fixed-sign risk bound

The former blockwise population-risk lower bound is now an exact minimum in
the same fixed-graph real relaxation, including a free nonnegative internal
scale. Let rho_C=(a_C-b_C)/|C|. Mixing independent component signs of means
rho_C with weight 1-2*epsilon and independent uniform signs with weight
2*epsilon gives pair moments (1-2*epsilon)*rho_C*rho_D. Its strictly positive
relative-orientation distribution attains all cross-block optima together.
At total mass 1/epsilon every excess w=pi/epsilon-2/K is nonnegative, with
real amplitude (sqrt(1+4*w)-1)/2. The internal optimum is also attained at
t=(2*q_in-1)/(1-q_in). Thus the former lower expression has a matching upper
construction; arbitrary block targets would not have this joint consistency.

The selected diagnostic has t=3, two orientation masses 17/40 and six 1/40,
or two excesses 4 and six zero at total mass 10. Its fixed-state relaxed
minimum is approximately 0.5069369136. The exact synthetic audit covers
1,550 residual-count/noise configurations, 11,100 orientation probabilities,
16,600 ordered block optima and 3,100 likelihood comparisons. A three-bit
triangle counterexample prevents treating arbitrary block optima as feasible.
The proof may use actual hidden signs to characterize a family minimum;
the experiment never receives them. Its quadratic-root amplitude values are
not legal-state certificates, and its fixed-state optimum is not a lower
bound on a changing prequential stream. RN-5 remains unchanged and running.

### 93.4 Retain the first n16 snapshot memory failure

The eleventh corrected-source attempt, n16/c2/seed16/rate1, exits with a
MemoryError in the final CUDA auditor's runtime/arena snapshot. Its completed
job records a 17,179,869,184-byte limit, process peak 17,179,660,288 and job
peak 17,180,917,760, exit code 1 and no timeout. The failure remains FAILED;
no successful host-bound, sealed model, score, install or complete phase
audit is inferred from it. The next registered rate starts under the same
protocol. This host/evidence failure does not refute Foundation or justify
changing the ongoing matrix's model, resource or acceptance parameters.

Independent post-analysis of the first eleven attempts retains ten EXECUTED
workers and one MemoryError, still 40 checked scores, eight fresh decisions,
4,528 phases per reference/CUDA path and 128 new posterior GPU forecasts.
The analyzer now reports failed workers and their retained reasons separately
from Runtime HALTED_UNRESOLVED outcomes. No failed tail is reconstructed.

The theory and checked eleven-attempt experiment prefix are retained as separate
commits on `research/joint-learner-geometry`, a linked worktree of this same
canonical repository. The running main worktree stays at source `38b27b3`
until every bound worker is terminal; only then integrate the research branch
and the final journal. This preserves ongoing execution identity while
recording auditable results in Git. The branch's partial journal is explicitly
an eleven-attempt snapshot, not a complete experiment.

## 94. Exact factor dynamics isolates a finite-update obstruction

While the unchanged RN-5 worker matrix continues, v5's shifted amplitudes
give a general exact update: b'=b*(A+B*sigma*chi_e), where lambda=eta/T,
A=1-2*lambda+lambda/Q and B=lambda/Q. Q is the actual target probability
before the update. Until projection, squared amplitudes therefore retain
positive pairwise factors on observed edges, even through cycles/repetitions.
The mass recurrence is S'=(A^2+B^2)*S+2*A*B*T*(2*Q-1), with T=S+2-K/4.
This is a value/dynamics identity, not free factor-state compression or an
efficient cyclic partition-function algorithm.

On ordered forest observations, every new edge forecast is neutral. The
update factors reduce to 1+2*lambda*sigma*chi_e; S multiplies by 1+4*lambda^2.
Cross contrasts are S/T times the product of rho_e=4*lambda/(1+4*lambda^2)
along the path. The standard Ising tree-correlation property is attributed
to Anandkumar, Tan and Willsky, Fact2/equations42-43; the native optimizer
factors and literal-base correction are derived here. Extra unrelated
components dilute the same two-label rate1 response from 0.564898 at c3 to
0.523806 at c4 and 0.507248 at c5; the ideal noisy-query posterior stays0.756.
For a fixed finite path and sufficient graph/initializer resources, the
unit-initialized advantage scales as (9/16)*(2*eta/K)^d. This is not a new
static resource lower law or an extrapolation of RN-5's fixed Gamma budget.

The two-step effect cannot be repaired just by rate selection inside the
unprojected regime. Its three signed pair contrasts obey z=x*y/(S/T), with
S/T>=9/10 for c>=3. The correct noise-1/10 posterior would require S/T=4/5.
Arbitrary real amplitude values can represent those forecasts, but no such
two-rate trajectory does so without projection. This separates finite-update
calibration from the earlier incorrect-internal-sign restriction; these
singleton controls have no wrong internal signs.

The rate4 three-edge K8 path also supplies a genuine boundary: its third
step clips and violates a four-spin product identity required by every
zero-field pairwise log density. No new architecture action created that
interaction. More generally, two free rational amplitude states can agree
on all current pair forecasts and total scale20 while retaining opposite
four-spin moments. The same subsequent exact unrounded label gives next
forecasts113/202 and89/202. These are not claimed RN-5 reachable endpoints;
they prevent treating current pair forecasts plus scale as a complete
learner summary.

The exact audit covers 1,932 signed/ordered forest prefix states, 15,668
amplitude coordinates,11,624 native forecasts,1,924 gradient successors and
11,624 independent full-assignment posterior forecasts. Another1,024 general
factor updates cover10,240 coordinates and448 nonneutral cycle/repeated-edge
steps. Unequal-rate controls retain88 unprojected cases and20 outside that
hypothesis. The projection, calibration, dilution and hidden-moment evidence
uses synthetic data only, no Torch and no Runtime/certificate authority.
The target matrix, implementation dependencies, resource budgets and all
previous successes/failures remain unchanged.

## 95. Native delayed values realize a finite-window Bayesian control

The v5 calibration obstruction motivates a direct test of FP's existing
recurrent semantics. Under a known fair latent-bit prior and noise1/10,
relative-world weights are9^matches. Their excess u=w-1 evolves as
u'=u+8*I_match*(1+u), which is entirely positive. Ordinary lag1 input/target
atoms supply the match indicator. Gamma=(1,8) and rate0 are already legal;
the native delayed values carry adaptation while the existing complete
learner, gradients, clocks and observation retention continue unchanged.

A single growing self-loop cannot justify a finite invariant box. Instead
H-1 delayed stages per world store suffixes of lengths1,...,H-1; bodyH is
the current readout. Stagej has the actual invariant upper9^j-1. The result
is exact for all retained-window observations, and for the entire prefix
when its length is at mostH. Base(K,K) plus shared excess and eightfold
matching weights produces the correct noisy posterior even on diagonals;
no normalized feedback, internal division or fitted parameter is supplied.
Literal range10*K*9^H and the known prior remain declared costs/assumptions.

The exact control checks3,487 full-prefix and264 suffix endpoint forecasts,
plus969 intermediate predictions, against enumeration of all2^n latent
assignments. An actual owned n3,H3 CPU stream seals four ordinary events
with13 independent binary64 phases. Its forecasts are1/2,1/2,189/250,77/122
for label0. The graph has123 nodes,two slots and eight delayed coordinates;
all four observations remain in Runtime. A192-forecast independent rounded
interpreter keeps native masses and delayed states exact, with maximum
gradient error193741/255852544000 and raw division error1/41943040.

This is an initially registered known-prior finite-window model, not
discovered structure, a compiler class proof, an installation or a CUDA
experiment. The functional CPU command explicitly has unresolved physical
host scope. The committed launcher preregisters two fresh512MiB jobs with
120-second timeouts, one for full-window calibration and one for observable
window eviction. The latter must forecast1/2 after labels0,0,1 at H2, where
the whole-history posterior is41/50. Actual completed jobs, rather than the
registration itself, must establish that physical scope. This control uses
no new Foundation action and changes no live RN-5 execution dependency.

### 95.1 The registered CPU jobs complete with the same semantic boundary

Source `a4877187f37926757344d1a90582b80ea25d622f` now has two completed
fresh512MiB jobs:both exit0 without timeout and seal their owned ordinary
streams, with13 independent binary64 phases each. The complete job peaks
are44,797,952 and42,512,384 bytes; process peaks are43,565,056 and41,295,872.
The full-window worker also repeats the exact and rounded-interpreter checks
inside its source-bound job. The H2 worker forecasts1/2 after labels0,0,1,
while the retained complete history's posterior is41/50. All four original
observations remain owned. The compact journal retains both completed job
identities and Runtime observations, without phase dumps or saved weights.
Actual CUDA, learned prior/structure, construction, installation and class
completeness remain outside this CPU model-control result.

## 96. RN-5 retains the second n16 failure and a valid n16 posterior

The unchanged corrected-source matrix now has thirteen completed attempts:
eleven EXECUTED and two FAILED. Attempt12, n16/c2/seed16/rate4, follows the
rate1 outcome with a MemoryError in the final CUDA auditor's Runtime/arena
snapshot. Its job exits1 without timeout at the unchanged17,179,869,184-byte
cap; the process peak is17,179,660,288 and job peak17,180,921,856. No successful
host-bound run, FP score, install, seal or complete phase-audit count is
inferred from this failed job. The following posterior worker executes256
forecasts with job peak2,311,000,064 bytes, unseen CE0.3269395302762026 and
full-domain CE0.3266204354893652. This is one registered sample, not an imputed
FP result or a population/model-dominance theorem.

Independent post-analysis verifies44 descriptive scores, eight fresh
decisions,4,528 CUDA/binary64 phases per path in eight sealed FP streams,
and384 new posterior GPU forecasts. Seven FP streams install. Both failed
workers remain separate from Runtime HALTED_UNRESOLVED outcomes. The same
canonical research branch now retains this exact thirteen-attempt partial
journal; the running main worktree remains at38b27b3 with its evolving
journal and the unchanged rest of the31-worker matrix. No partial plot,
failed tail or complete-experiment claim is introduced.

## 97. Register the native recurrent model on the actual AMP path

The frozen CUDA scope does not require exclusive board availability. Its
native allocator history is process-local and its distinct physical VRAM
coordinate charges the identified board's full capacity. Therefore an
independent short target control can proceed while the unchanged RN-5
worker continues; neither experiment gains a timing or exclusivity claim.

`recurrent_cuda.py` preregisters the48 existing H3 rounded-interpreter
four-label streams plus the H2 eviction control as49 fresh Windows jobs.
All use the same initial native graph/learner/lagged sources, with ordinary
context and target input only. Each gets4GiB host commitment,120seconds,
16MiB native arena,32MiB allocator reservation,256MiB packed payload,10^10
work per role,4096 output cells and131072 prepaid bytes per phase. State,
native, normalizer and probability tolerances remain1/100. Metadata-only
preflight finds at most941 output cells, without importing Torch or running
the target. Completed jobs, all native phases, independent rounded/binary64
replay and same-cut full-assignment posterior forecasts will determine the
outcomes. The source-bound journal must retain every failure/refusal; no
target success, compiler construction, installation or class optimum is
claimed by this registration.

### 97.1 Retain the unnecessary-install registration failures

Source `e92762c` supplied CudaInstallContract to an empty policy without
search or fresh evidence paths. Runtime's constructor correctly rejected
all49 jobs before its own host/CUDA initialization, with no forecasts.
Each completed outer job exits1 without timeout; the largest job commitment
is30,007,296 bytes. All job identities/counters and the identical traceback
are retained, with the common trace stored once. The correction removes
only the unused install declaration, which the existing constructor permits
for an empty policy. It retains all49 cases, graph/learner/data parameters,
resource budgets and numerical tolerances. No actual model/CUDA result was
seen before this correction, and no Runtime or Foundation rule changes.

### 97.2 All49 actual AMP controls complete at the declared resources

Corrected source `75de8987fc28af6edd29bcfe3930d75c299145d7` completes all49
jobs without timeout. Every owned stream seals;637 actual CUDA phases match
the independent rounded interpreter, and637 binary64 phases pass independent
replay. All196 normalized stored-mass forecasts equal the stated-window
posterior, including the H2 eviction control's1/2 instead of full history's
41/50. The complete Runtime retains all observations. The native graph's
gradient/optimizer machinery remains checked at rate0; adaptation proceeds
through its ordinary positive delayed values.

CUDA native and normalizer errors are zero. Maximum state error is
193741/255852544000 and probability/raw division error1/41943040; binary64
maxima are14311/16618282624997130240 for state and51/923237923610951680 for
probability/division. Maximum completed process/job commitments are
2,302,722,048/2,303,946,752 bytes below4GiB. Maximum packed residency is
4,727,982 bytes, consumed arena extent47,752 and phase-frame use74,490;
at most941 of the fixed4096 output cells are needed. Each job binds the same
RTX3090/native runtime identity, with the separate whole-board capacity
coordinate and no exclusive-device or comparative-timing claim.

The earlier49 constructor rejections retain their own completed jobs and
common traceback. No case, budget or numerical tolerance changes after
the unused-install registration correction. The compact target journal
retains outcomes and independent phase/forecast checks without weights or
bulk phase histories. This closes the native finite-window control's CPU/
AMP realization, but supplies no discovery, installation, class-optimality,
long-history affordability or new full implementation-release result.
The next model question is an owned native proposal guided by ordinary
observations and actual initializer/profile/fresh-evidence resources.

## 98. A recurrent endpoint fit is not causal evidence or noise identification

The existing search objective explicitly evaluates every historical record
against one frozen complete learner state; it does not advance delayed
values. A native H2 repeated-pair control gives causal likelihood41/100
but frozen-endpoint likelihood73/100 after two labels0. This is not an
online information leak: the empirical score is evaluated after both labels
were revealed, for its declared class. Relabelling it Bayesian or fresh
evidence would be the false claim.

Three native forest controls now share Gamma=(1,0,2,8) and retain all four
coordinates, differing only in SUM-edge choices of an available noise slot.
On two forest edges they all have causal likelihood1/4; endpoint scores
are1/4,5/16,41/100 for noise1/2,1/4,1/10. In general one observation per
forest edge has uniform label likelihood2^(-m) under every common noise
rate: fair latent edge parities are independent and XOR noise preserves
uniformity. Thus that data cut cannot identify noise, regardless of solver
resources or empirical endpoint fit. A later closing query can still use
the distinction, forecasting189/250 versus9/16 after the same two zeros.

For a triangle, label likelihood is[1+product(signs)*(1-2*epsilon)^3]/8,
which depends on the noise. This is a distributional identifiability
observation, not exact recovery from one cycle. Repeated-edge RN-5 training
does not satisfy the forest theorem's one-observation premise.

The exact audit checks47 small forests,892 signed-forest/noise likelihoods
and32 triangle likelihoods. Four actual functional CPU streams seal with28
independent binary64 phases and retained observations. Their physical host
scope is explicitly unresolved; no class, fresh, installation or new GPU
claim is supplied. The current objective and Foundation remain unchanged.
A future proposer must separate its causal guidance, the declared empirical
decision class and actual fresh continuation evidence.

## 99. RN-5's fourteenth attempt retains the third n16 snapshot failure

The unchanged n16/c2/seed17/rate1 worker also exits with MemoryError in
the final auditor's Runtime/arena snapshot. Its completed job records
process peak17,179,684,864 and job peak17,180,917,760 bytes under the declared
17,179,869,184-byte cap, exit1 and no timeout. It receives no successful
host-bound, model-score, install, seal or full trajectory-audit claim.
Independent analysis of the fourteen-attempt prefix verifies eleven
EXECUTED and three FAILED jobs, with the same44 descriptive score checks,
eight fresh decisions,4,528 CUDA/binary64 phases per path and384 posterior
GPU forecasts. The research branch retains this exact partial journal;
the running main journal continues with seed17/rate4 at the original source
and resources. The separate short recurrent-model controls change no RN-5
budget, data, source or acceptance rule, and add no comparative timing claim.

## 100. RN-5 retains all four n16/c2 failures and the first c4 completion

The seed17/rate4 worker also fails at the final auditor arena snapshot,
with process peak17,179,664,384 and job peak17,180,917,760 bytes, exit1 and
no timeout under the unchanged16GiB registration. All four n16/c2 FP jobs
therefore remain failed, without invented scores, installation or trajectory
closure. Both corresponding posterior jobs execute; their mean unseen
AMP CE is0.3269395091. This asymmetry is part of the experiment's outcome.

The first n8/c4/seed18/rate1 stream seals and installs. Its candidate unseen
CE is0.4217356003 and deployed unseen CE0.5295714675. These are descriptive
values from one registered case, not a c4 mean or population result. Exact
post-analysis now verifies the seventeen-attempt prefix: thirteen EXECUTED,
four FAILED, nine sealed FP streams, eight installs,52 dynamic score checks,
nine fresh decisions,5,034 CUDA/binary64 phases each and640 new posterior
GPU forecasts. This commit retains that checked journal prefix. The main
matrix continues at source38b27b3 with its original resources and parameters.

## 101. Native posterior proposals use actual initialization and causal replay

The v6 solver now proposes a finite-window posterior through the ordinary
owned native search path. Exact static-latent marginal guidance selects among
actual initializer noise values, retaining ties and all observations; the
existing frozen-endpoint objective and independent categorical upper retain
their own roles. The graph keeps base(1,1) by constructing K-1 from repeated
unit incidences. No posterior vector, fitted coefficient, reset callback,
new state interface or semantic architecture action enters Runtime.

The central new replay result is an origin-tail sufficiency theorem. Each
stored stage multiplies factors from actual profile source origins; only
matching their bounded tail to the ordinary history justifies a warm-state
posterior. It covers valid mixed prefixes and multiple passes without a
menu of replay modes. Reversed replay gives73/82 rather than37/42 in one
four-label example. Replaying two labels twice lets an old factor reach H4
and gives3281/3650 rather than73/82; H3 remains valid. There is no implicit
reset between passes. Declared state bounds, instead of smaller observed
values, also constrain every next body; zero learning rate still executes
commit-grid rounding of used coefficients.

Exact enumeration checks1,552 noise-guidance scores,96 uninformative ties
and2,016 native forecasts over224 profile plans. Eleven scoped interface,
resource/arithmetic and coefficient controls pass. Two actual owned search
adversaries prove that unpaid proposal work never runs and forged complete/
scale/likelihood metadata cannot supply a value or class certificate. The
previous eight empirical-upper authority adversaries also pass unchanged.
A functional44-event CPU stream constructs/profiles at3, installs from
actual paired fresh evidence at39, retains all labels and seals with268
independent binary64 phases, including changed/contradictory post-install
queries. Its historical class remains unresolved. Four fresh CPU/RTX3090
jobs, using full and twice profiles with distinct actual optimizer clocks,
are registered in the same audit before execution. Their physical evidence
is pending and cannot be borrowed from the older initially supplied model.
Foundation, ERC-1 and the frozen release stay unchanged; main RN-5 keeps
its source while these changes are committed on the canonical research branch.

The new base-one graph has a measured interpreter precision distinction:
91 profile/ordinary rounded forecasts keep masters and delays exact but
have native/normalizer error up to3 and probability error77/3362410. All171
rounded source/queue boxes fit cap29160 (maximum29158). Its pending GPU
registration fixes native/state tolerance8 and probability1/10000 before
execution; the old base-K exact-mass claim is not borrowed.

## 102. Keep the causal-proposer report failures inside their original scope

All four source35ba35b jobs returned from the owned audit but failed while
the result wrapper attempted to spawn Git inside the one-active-process
job fence. Each exits1 without timeout, with WinError1816. Their original
complete journal is retained separately; no successful model output or
full target-phase count is recreated from an absent summary. CPU job peaks
are104,632,320 and106,717,184 bytes, CUDA peaks2,412,572,672 and2,423,009,280;
the physical job accounting survives independently of the failed report.
The fix removes this unnecessary source-query child process and binds the
output to the parent's existing before/after source checks and completed
process identity. It changes no model, case, data, resource, tolerance,
Runtime semantic path or acceptance condition. The corrected four-job
registration explicitly links the earlier four failures before execution.

## 103. The causal proposal reaches owned CPU and RTX3090 installation

The corrected four-job matrix at6acbd85 completes with all four EXECUTED,
sealed and installed at cursor39. Full/twice profiles execute3/6 events and
retain distinct complete optimizer clocks and provenance. Every historical
class remains unresolved; CLOSED_BY_INSTALL is terminal bookkeeping, not
a global-maximum certificate. CPU jobs check268/277 binary64 phases; GPU
jobs independently check268/277 CUDA and binary64 phases. Totals are1,090
binary64 phases,545 actual CUDA phases and288 fresh score/log/wealth checks,
including both paths' first crossings and the spent global alpha1/2.

Actual CUDA masters/delays stay exact. Native/normalizer error3 agrees with
the independent rounded preflight; state error is130103/209715200, raw
probability error315089/13757317120 and division error3497/126852530176.
Binary64 native/normalizer errors are zero. CPU maximum job commitment is
106,569,728 bytes and CUDA2,423,279,616, within the unchanged512MiB/4GiB caps.
Maximum packed payload49,239,902, native arena extent590,704, frame75,759
and output cells958 fit the registration. The original four report failures
remain failed and linked. No whole-release, population/noise-learning or
whole-history claim is added; RN-5 continues at its original main source.

The accompanying proof also identifies why this categorical-upper route
cannot close the tested historical classes: positive base and finite R
make a pure source cell's categorical factor1 unattainable. The first lagged
target context is uniquely empty, so objectives containing record0 include
such a cell. This is a loose-bound route limitation, not an impossibility
of optimizing the actual finite native class by a different solver. Useful
future adaptation and its information/resource costs remain the research
frontier after this construction/installation control closes.

## 104. RN-5's n8/c4 prefix retains an adaptive-posterior gap

The twenty-two-attempt prefix independently verifies eighteen EXECUTED and
four FAILED jobs, twelve sealed FP streams, nine installs,72 dynamic score
checks, twelve fresh decisions,6,552 CUDA/binary64 phases each and768 new
posterior GPU forecasts. All four n16/c2 FP snapshot failures keep their
original outcomes and caps. The four n8/c4 streams seal, with two installs;
the two posterior controls also complete. Their two-seed candidate unseen
CE means are0.4168832454 at rate1 and0.4333859733 at rate4, versus the strong
posterior's0.3654471094. Deployed means are0.6113593240 and0.6210014211.
These are registered finite-sample observations, not a population comparison
or completed n16/stress result. The live main source remains38b27b3; its
n16/c4 worker continues while source extensions reside in the same Git
repository's research worktree. No partially scored plot or imputed failed
tail is published.

## 105. Contract positive constraints before enumerating latent worlds

The fair latent-prior average of a product of labelled XOR indicators is
zero for an inconsistent system and2^-r otherwise. Expanding positive noisy
likelihood factors therefore gives a native window posterior with integer
coefficients8^k/2^r at the actual Gamma1/8. Endpoint-equality partitions and
lagged target atoms realize every term using only SUM/PRODUCT. The base-one
mass range is10*9^H independently of token count, and fixed-H graph size is
polynomial in n. This specializes the classical positive subset expansion;
it is not a new Foundation semantic mechanism or a sharp circuit lower law.

Exact audits verify18,540 signed systems,5,944 native forecasts and58 formal/
rounded-interpreter controls each. At H<=3, the emitted native values and
masses are half-exact on the categorical domain. A same-interface base-one
enumerator instead rounds13122 to13121 in the diagonal witness. Different
parameter gradients and a soft-history counterexample explicitly block any
complete-learner or arbitrary-source equivalence claim.

The graph/source cost is substantial: n2,H3 uses1771 nodes versus102, and
both programs require the same2340-row full categorical source domain.
The graph window dependence involves Bell numbers; n8,H3's source domain
already has135,274,560 rows. Two owned n2,H3 CUDA controls are registered
with identical16GiB jobs,2GiB packed caps,16/32MiB target storage and complete
2MiB phase evidence. Their actual result is pending; no zero-cost inference,
model-quality improvement, discovery, fresh install or class closure is claimed.

Attacking the uncentered comparator immediately reveals a cheaper positive
coordinate: v=(w-1)/K updates as v+I*(8v+8/K). For K<=8, all coefficients are
integers made with the same actual initializer. At n2,H3 this graph has102
nodes/174 edges and achieves the same averaged masses and half-exact forward
values as the1771-node contraction. Another2,965 exact forecasts and53
formal/rounded checks each pass. A repeated informative cross edge gives
exact masses3281/369 for both new representations, versus the uncentered
6562/738 with its first mass rounded to6561. The contraction remains a
general fixed-H polynomial-in-n representation theorem, but is not the
small-n implementation winner. Existing source-bound jobs keep their original
registration and must be retained; the stronger control's owned execution
is a separate pending obligation, not grounds to repeat those jobs.

The first pair now completes at65c6472: both seal all nine events, with28
independent CUDA/binary64 phases per job,56 per path total. Contracted native/
normalizer error is zero; the uncentered errors are1/2. Raw probability errors
are1/41943040 and583/26214400. The contracted graph pays570,850,422 packed
bytes and5,319,102,464 peak job bytes, versus90,834,766 and2,554,642,432 for
the uncentered graph. Both stay inside unchanged caps without timeout.
Complete phase frames reach792,426 versus46,688 bytes. The strong centered
control is registered as one further job with the identical tape/resources;
the earlier two source-bound outcomes remain immutable and are not repeated.

The stronger centered job also completes, at716d279: all nine events seal,
with28 independently replayed CUDA/binary64 phases each and zero native/
normalizer errors. Its packed peak90,865,346, completed job peak2,553,532,416,
native extent66,712, maximum frame47,225 and output cells612 fit the same
registration. Raw probability/division error is1/41943040; gradient/state
error6383/13589544960 remains nonzero and independently checked. Post-analysis
recomputes27 retained forecasts across all three models and verifies source,
process, registration and resource/error claims; total independently audited
phases are84 CUDA and84 binary64. Thus small-n centered enumeration realizes
the precision benefit at much lower packed cost than partition contraction.
The general fixed-H existence theorem remains, but it supplies no large-n
or long-history affordability result. This initial-model comparison is closed;
none of its three jobs should be repeated or promoted to a class/install claim.

## 106. Whole-history predictive information survives fixed future error

The known-noise relation posterior has a smaller exact history description
than its latent-world mass table: signed nonloop edge counts. Opposite edge
labels and diagonal labels contribute only a common fixed-noise likelihood
factor. The count update preserves every legal future posterior forecast.
The exact full pair moment map is injective within this minimal pairwise
Ising family; this does not rescue arbitrary projected-learner moment states.

At cut T with all ordered pairs legal, reachable counts are the integer
L1 ball, with N_m(T)=SUM_j 2^j binom(m,j) binom(T,j) classes. A stronger
continuation argument shows the same information lower bound survives any
uniform future probability error below4/25 at noise1/10. For any unequal
counts, a common finite suffix nearly fixes the other bits' relative parities
and cancels one state's remaining field, exposing a forecast gap approaching
8/25. These suffixes are legal positive-probability observations, possibly
very rare; the proof gives no expected-risk impossibility or label oracle.

Exact checks cover6,175 ordered histories,12,350 likelihood identities,
846 distinct forecast tables,2,016 tree-state pairs and4,216 pairs of full
count classes. Every checked full-class suffix meets gap38/125; the actual
minimum is about0.3199967886. Counts8/9 already share a binary32 forecast,
yet eight common contrary labels give1/2 and41/50. With unknown noise,
even equal d and clock can diverge: diagonal likelihood factors affect the
next posterior. The proof and small reproducible audit retain these boundaries.

The result separates information from physical inference. It authorizes no
signed native source, counter initializer, raw-history deletion, state transport
or install certificate. Affordable reachable whole-history adaptation, or an
explicit expected-risk approximation, remains the next model research question.
Foundation and ERC-1 stay frozen. The stale end-of-theory science HOLD sentence
is aligned with the already completed release and the file's existing status.

## 107. RN-5 retains its first n16/c4 execution timeout

The twenty-third worker, n16/c4 seed18 FP rate1 at source38b27b3, reaches
its registered two-hour limit. The bounded-job record has exit1223 and
timed_out=true, with peak process commitment8,912,105,472 and peak job
commitment8,913,358,848 bytes under the unchanged16GiB cap. There is no
valid worker report and no model score, installation, seal or complete
phase-audit claim. This execution timeout is distinct from the four retained
n16/c2 final-auditor MemoryErrors.

Independent post-analysis verifies the23-attempt journal:18 EXECUTED and5
FAILED, with unchanged12 sealed FP streams,9 installs,72 descriptive score
checks,12 fresh decisions,6,552 CUDA/binary64 phases each and768 posterior
GPU forecasts. The source-bound parent proceeds to rate4. The failed case
is not restarted, its cap is not increased, and no failed tail is imputed.

## 108. Native simplex gradients recover a full posterior at a unit step

The count-state result motivates attacking the learner transition instead
of enlarging recurrent windows. For positive masses affine in a simplex
weight block, equal expert normalizers give a precise identity: the unit
multiplicative tangent step of the actual native CE gradient is Bayesian
updating. Its mean-gradient subtraction retains the native normalizer
derivative. No clipping or fitted posterior coefficient is inserted.

The rule also commutes with splitting a fixed expert into identical copies.
Within separable diagonal tangent-gradient rules, that consistency forces
f(a+b)=f(a)+f(b), and positivity forces f(w)=c*w. Euclidean tangent descent
fails the same test without reaching a projection boundary: aggregated
weights3/5 and19/30 result from two representations of the same prior.
This is a restricted model-level derivation, not a universal FP metric axiom
or a complete-Compiler equivalence. The classical replicator/Bayes connection
is cited; the native affine gradient and its boundaries are proved directly.

The explicit known-noise graph uses14/25/42 nodes at n2/3/4. Its parameter
state carries the whole posterior; every native activation stays at most8
and the normalizer is10 at every exact history. Native-gradient audits check
961 histories,5,955 forecasts,1,051 successors including80 agreement/reversal
events,9,183 affine updates and378 refinement cases. Unequal expert normalizers
give an exact negative unit-step weight, and a four-spin state direction shows
that the categorical geometry cannot be borrowed from current pair forecasts.

This changes the learner U and actual uniform1/K initializer. World count
remains exponential and exact parameter precision can grow with history.
Current Runtime correctly rejects the new optimizer ID; no existing model
class, initialized trajectory, AMP bridge or fresh install is relabeled.
Foundation VII already declares U as a lineage coordinate. The result calls
for an owned scoped learner extension and matched model evidence, without
adding an architecture-semantic action or altering live RN-5 execution.

## 109. Preserve an interrupted RN-5 attempt before resuming the matrix

At2026-09-13 23:06:55 UTC the previously active main parent and worker are
absent. The journal retains23 completed attempts and the next attempt's
directory is empty. No completed job counters or worker report survived;
the interruption's cause is unknown. A separate minimal interruption record
preserves that fact without converting it into a timeout, memory failure,
model result or resource certificate. Main source38b27b3 and its execution
dependencies pass the existing guard. The registered resume path continues
at task24, n16/c4 seed18 rate4, at23:08:27 UTC with unchanged resources and
timeout. No completed task is repeated and no earlier outcome is removed.

## 110. Register the simplex learner as an owned transition, not supplied weights

The affine theorem now has an explicit Runtime U:
`mean-ce-normalized-simplex-gradient-v1`. It binds a simplex slot block,
fixed other parameters, the actual initializer and full event/update clocks.
Every ambient native gradient remains accumulated, including the nonzero
fixed-feature derivative. Both numerical paths perform an explicit final
normalizing division; it is algebraically the identity on the exact simplex.
Negative updates are refused before numerical zero canonicalization.

The extension exposes a useful distinction: for update unit U>1, the affine
transition averages single-observation posteriors at the frozen starting
weights. Two identical labels give weights9/10,1/10 in one two-event unit,
versus81/82,1/82 in two sequential units. The new exact contract audit checks
603 commits, noncontiguous blocks, zero weights,12 registration refusals and
10 complete-context proposer refusals. The full20-program tiny search keeps
15 missing-block constructor failures and remains unresolved; the distinct
SGD class compares all20. No syntax is silently removed to manufacture a proof.

The v7 emitter constructs literal native syntax for the declared fair-prior,
known-noise affine model. Runtime owns its Gamma, actual profile, frozen-state
comparison and fresh paired starts. Small development CPU and RTX3090 streams
install at cursor22, including the actual two-pass profile, and independently
replay complete state and forecasts. These are implementation checks, not a
matched model comparison or a replacement for registered job evidence.
The eight-job CPU/CUDA matrix fixes source dependencies, resource limits,
tolerances and minimal reporting before its first committed-source execution.
Foundation, ERC-1 and the still-running RN-5 SGD matrix remain unchanged.

## 111. The registered simplex learner reaches actual CPU and AMP installation

All eight jobs registered at b34bf7b execute and seal under their fixed host,
packed, arena, arithmetic and timeout contracts. Independent audits check
1,208 binary64 phases,604 CUDA phases and200 whole-history posterior forecasts.
Four profiled streams independently verify160 fresh score/wealth events and
install at cursor22. One-/two-pass profiles retain their actual multiplicity.
All four historical native search classes remain unresolved; installation
uses fresh evidence rather than a fabricated class optimum.

The largest packed peak is77,265,284 bytes and the largest completed job
commitment is2,417,373,184 bytes. Maximum CUDA state error is422861/188743680,
native error3/640, normalizer error1/256 and mass-normalized probability error
249137/1677721600, within the original1/100 and1/1000 tolerances. These are
small known-model implementation audits. They do not establish model-quality
dominance or arbitrary-horizon reliability, and do not relabel RN-5's U.

The next adversarial pressure test is already concrete in independent
rounded arithmetic:50 agreeing relation labels followed by50 contrary labels
lose a binary32 posterior weight at event48. The first declared bridge
tolerance violation is predicted at the context after97 observed events,
with native error4/365 and probability error2/1825. A source-bound owned
execution is required before calling this an observed device/Runtime result.

## 112. Actual posterior underflow is exposed by a legal future and honestly refused

The two reversal jobs were registered at619e3cf with the existing U, native
graph, source domain, arithmetic, host/arena bounds and tolerances unchanged.
An exact absorbing-zero argument and independent rounded native preflight
predicted the first lost world weight at48 and the first bridge breach after
97 observed labels. The actual RTX3090 path matches both predictions.

CPU seals all100 observations and returns to exact weights1/2,1/2, with301
independently checked binary64 phases. CUDA executes97 labels, then retains
the failed next prediction and halts unresolved before revealing its target.
All293 target raw phases are independently checked:292 successful and the
one refusal. The same prefix has293 verified binary64 phases. Its exact
weights are729/730,1/730 while the physical weights are1,0; native error4/365
and probability error2/1825 exceed the original bounds. The failed target
stream receives no seal, later forecast, model score or install claim.

The two jobs jointly check197 successful posterior forecasts. Peak packed
state is2,259,936/79,009,431 bytes and completed job commitment is
41,050,112/2,416,918,528 bytes on CPU/CUDA. This is numerical underflow within
the fixed resource envelope. Raw observations, exact reference state and
failed physical evidence remain owned. The blind continuation to weights1,0
after the balanced100-event tape belongs only to the independent arithmetic
counterexample; the real target stops at its first failing bridge.

The selected existing regression scripts pass during this extension:
reference events, profiles, search, binary64 Runtime, owned CPU policy,
CPU installation, reference run, causal relation proposal, CUDA learner,
CUDA Runtime, CUDA installation and CUDA policy/run. These working-tree
regressions do not relabel the frozen31-script release. New source-bound
evidence remains the eight jobs at b34bf7b and the two jobs at619e3cf.

The result separates exact learner geometry from future-preserving physical
state. Normalizer10 does not solve the latter; a tolerance increase cannot
recover the absorbed coordinate. A different declared representation or a
properly scoped expected-risk approximation must carry its own resource and
continuation claims. No architecture action or Foundation patch is introduced.

## 113. Preserve the whole learner phase, not only its posterior prediction

The count-state idea now has an exact encoding for the actual reference
unit-rate/unit-event relation learner. Committed counts determine theta;
the actual uncommitted query/label determines its complete gradient. At
target mass M the fixed-slot gradient is1/M-1/5 and each latent-slot gradient
is4/5-8*I/M. The former equals the weighted mean of the latter. Omitting
the fixed coordinate or clearing a diagonal event early would erase a real
uncommitted gradient even when counts and theta do not change.

Retaining both cursor and optimizer-step count handles late birth and actual
profile multiplicity. Exact transition/cache decoding commutes with native
initialization, prediction, observation, registered commit and profile
attachment. Independent checks compare1,146 full native caches and both
observed/committed states, including exhaustive n2/n3 prefixes, n4 cycles,
three profile multiplicities and a100-event late-birth reversal. A conservative
integer guard acts before materializing large powers; world/phase refusals
remain explicit. Decoder work and exact output precision are not erased.

The representation has a sharp scope. Under the same rate1/2 contract, labels
01 and10 give equal counts but first weights77/170 and93/170. With the same
two-event update schedule,0001 and0100 give equal counts but weights61/82
and9/10. Thus a physical specialization must bind the actual rate, unit,
Gamma, graph and source domain; the optimizer name is insufficient.

This proves a complete reference learner/cache encoding for the fixed model,
not an installed physical codec or a resource-equivalence theorem. Existing
raw observations, pre-target query identities, provenance and evidence stay
owned. The existing FP32 reversal failure remains unchanged. The next issue
is a paid physical decoder and its continuation relation, with exact count
overflow guards and no reconstructed value supplied through a helper port.

## 114. Exact likelihood memory and approximate causal quotients have different tests

The phase encoding now extends to fixed finite positive rational likelihood
banks under the unit simplex U. Prime valuations of world likelihood ratios
give integer increments. At a known T, their affine rank rho determines
Theta((T+1)^rho) distinct posteriors, with a matching additive-coordinate
encoding and counting lower bound. Full future signatures make these exactly
the reachable predictive classes. A two-world bank with odds increments 2
and 3 has rho=2 despite having only one free real posterior coordinate.
Another bank has raw rank 2 but fixed-cut rank 1, exposing the clock's role.

The sharp Hilbert/TV bound from Cohen and Fausti gives the appropriate
positive-perturbation geometry. Common likelihood updates preserve Hilbert
distance. Thus some distinct same-cut states remain arbitrarily close under
every common future; the single-noise relation packing constant does not
generalize to every rational bank. This initially suggests an approximate
cover, but such a cover need not commute with the learner transitions.

For pure deterministic encodings, reference commutativity and transition
consistency amplify any merged pair through repeated block substitutions.
In a reversible two-world bank this forces a future forecast gap approaching
the expert contrast. Uniform per-run error below half that contrast therefore
requires all exact posterior classes. The threshold is sharp for prediction-
only codes: the expert midpoint uses no posterior information at the boundary.
This theorem does not cover arbitrary history-dependent physical lifts or
promise that an indefinitely long word fits an actual resource envelope.

An exact native witness makes the distinction concrete. Nineteen labels with
odds factor 2 and twelve labels with factor 3 plus seven identity observations
give a pair whose every-future forecast gap is below 7153/4194304 < 0.002.
Merging them in a pure encoding forces the commuting length-38 block states
to merge; a common inverse then exposes gap 7153/2111458 > 0.002 at cut 76.
These are different continuation words linked by global quotient consistency,
not a contradiction to the original pair's small common-future distance.

The Fraction audit checks 2,339 complete native caches/observations/commits,
2,408 histogram-coordinate bijections, relation ranks through n5, 48 future
word rows, 5,535 positive-tilt bounds and 510 constant-midpoint forecasts.
Known likelihood/prior construction is explicit, full gradients/clocks stay
present, and raw observations/provenance are never quotiented. No Runtime
source, AMP lowering, Foundation action, ERC-1 limit or live RN-5 contract
changes. The result constrains a future paid codec before implementation.

## 115. The resumed n16/c4 rate4 reaches its original timeout; its baseline completes

RN-5 task24, n16/c4 seed18 rate4, resumes after the separately retained
unreported interruption and now reaches a completed two-hour timeout at
the unchanged source38b27b3. The attached job records exit1223, no host-limit
termination and peak commitment9,165,230,080 bytes under16GiB. It yields no
valid worker report, model score, seal, install or complete phase count.
Together with rate1, both seed18 FP rates fail within their original limits.
The earlier interruption remains an unknown-cause event, not an extra score
or a completed timed-out job.

Task25's strong posterior baseline completes normally. Independent exact
post-analysis reconstructs all256 pre-target forecasts, the AMP encoding,
four score records and reported integer/payload bounds. Its unseen AMP CE
is0.33055575219484024 and full-domain CE0.32970063130197597. Its job peak is
2,309,025,792 bytes. No score is assigned to either failed FP rate and no
infinite-time or infeasibility conclusion is inferred from their timeouts.

The preserved prefix now has25 attempts:19 EXECUTED and six FAILED. The
previous23 rows are unchanged. Totals are twelve sealed FP streams, nine
installs,76 independently checked descriptive score records, twelve fresh
decisions,6,552 independently checked phases per CUDA/binary64 path and
1,024 newly executed posterior GPU forecasts. Parent11020 continues the
original task order; task26, n16/c4 seed19 rate1, starts as worker22612 at
01:08:38 UTC on2026-09-14. Main HEAD and all execution dependencies remain
bound to38b27b3; integrate the research branch only after all workers finish.

## 116. Lower the exact likelihood state instead of persisting an absorbed weight

The count/likelihood information laws now support an owned numerical lowering
of the existing unit-rate/unit-event simplex U. A bounded analyzer derives
affine selected heads, equal expert normalizers and commensurate likelihood
ratios from the actual native graph, Gamma and complete source domain. It
selects independent integer rows and checks every reconstruction. The exact
coordinates, actual pending event and both clocks simulate U; no posterior,
fitted coefficient or helper-supplied successor is admitted.

The new GPU commit decodes those coordinates using positive binary32 powers
and normalization. It still executes the complete native AMP forward and
reverse derivative before each commit, including fixed-slot gradients.
An exact native square with fixed zero multiplier retains gradient -1/8,
showing why current head affineness does not license deleting its interior.
The independent exact audit checks 958 transitions and ranks1,3,6, plus
nonuniform priors, noncontiguous slots, rational radices and scope refusals.

Runtime prepays model derivation and scratch before using the analyzer, stores
the complete descriptor in the initial phase frame, and binds later counts
with a primitive descriptor digest. The digest specifically exposes mutation
of an aliased descriptor at a cut whose physical theta has already underflowed.
Counter overflow preserves the actual pending event/gradient and refuses the
next commit. Profiles retain their replay multiplicity and attached clock;
installation retains the complete resident learner and tensor leases.

Development reversal checks seal all100 events and independently replay all
301 phases per numeric path: weight zero at48, positive subnormal at53,
uniform at100. A first development profile check exposed the score reader's
old seven-field forecast requirement. Accepting and validating the additional
pre-target query tag closes that interface mismatch; the subsequent two-pass
n3 profile run seals and installs at22 after both fresh paths cross. Its286
phases per numeric path and40 fresh events replay independently. These are
development observations, not clean-source matrix evidence or model scores.

The nine-job registration covers those two successes, six corruption/resource
refusals, and complete enumeration of a20-program class that must remain
unresolved because15 members lack admissible actual simplex initializers.
The old reversal failure is preserved. General multiprime banks, other U,
unlimited numerical accuracy and whole-Compiler compression are not claimed.
Foundation, ERC-1, live RN-5 and main HEAD remain unchanged; execute the new
registration from the canonical research branch after committing its source.
Before registration, the four existing reference-event, profile, binary64
Runtime and simplex-contract scripts pass, as do ten selected default CUDA
prefix/install/policy cases, including the learned policy installation.
This focused regression check does not replace the frozen full release audit.

## 117. Exact likelihood information survives owned AMP underflow and fresh installation

All nine preregistered jobs execute from08fa7bcc85320aa699cffb25ea9f6e292b036f0b.
The100-event reversal seals at the original tolerances: the minority FP32
master is zero at48/50, becomes raw word1 at53 and returns to1/2 at100.
Independent exact rounded replay checks all100 GPU commit operation tapes
and301 complete CUDA phases, alongside301 binary64 phases. The largest
native error is4/3281, with proper-probability error421009/34407971678.
No epsilon floor or trained reference theta is used to revive the weight.

The n3 candidate executes its actual two-pass profile, preserving T4 at the
cursor2 attachment. Both fresh score paths cross at22; installation keeps
all resident coordinates and the stream seals at46. Independent checks
cover286 phases per numerical path and40 fresh score events. Its historical
decision class stays unresolved. A separate complete20-program enumeration
compares five actual endpoints, retains15 initializer failures and withholds
a class proof despite exhausting syntax.

Six-bit overflow refuses before the32nd GPU commit, preserving the published
cursor31 and all32 revealed observations, including the pending full gradient
and event at cursor32/T31/q=-31. Count and descriptor corruption at the zero
cut both fail before the next target even though numeric theta is unchanged.
They remain explicit backend execution failures with retained phase records;
the enclosing terminal label does not turn them into admissibility theorems.
Work and scratch shortages call no model analyzer. A substituted source
subset cannot initialize the physical learner or acquire any continuation.

Across the six executed learner-prefix cases, independent replay checks994
valid and3 refused CUDA phases,997 binary64 phases and326 complete GPU commit
tapes. The three construction guards retain their separate outcomes without
invented numeric replay counts. The report binds every completed job to its
PID, creation time, commitment and CPU counters. All9 jobs exit successfully
after their required outcome, with no timeout or host-limit termination.
Largest job commitment is2,371,022,848 bytes under4GiB. Reversal/profile packed
peaks are81,167,353/77,267,870 bytes, largest frame41,326 bytes and maximum
phase output484 cells. The complete minimal report is29,287 bytes.

This resolves the finite owned representation question exposed by the old
underflow/reversal counterexample. It does not repair that historical run,
claim unlimited numerical accuracy, compress all reference/history state,
establish a model win, or complete a new full release. The next frontier is
useful model scale under explicit native, exact-reference and audit costs.
Foundation and ERC-1 stay frozen. Main's running RN-5 source remains38b27b3;
the implementation and both source-bound commits stay on the linked research
branch until the main experiment is terminal.

## 118. RN-5 seed19 rate1 reaches the same finite execution boundary

Task26, n16/c4 seed19 rate1, reaches its registered two-hour limit at source
38b27b3. The completed attached job records exit1223, no host-limit process
termination, peak job commitment9,577,873,408 bytes under16GiB, and no valid
worker report. Its process identity is22612 with creation tick134338217182366094.
The missing report supplies no model score, install, seal or complete phase
count. This is a finite execution failure, not a proof that the decision
class is infeasible or that no slower solver could finish.

The preceding25 journal rows are unchanged. The retained prefix is now26
attempts:19 EXECUTED and seven FAILED. Existing score, phase and fresh-evidence
totals do not change. Parent11020 starts the original task27, n16/c4 seed19
rate4, at03:08:38 UTC on2026-09-14 as worker12732. Main HEAD and all execution
dependencies remain bound to38b27b3. Preserve the remaining original matrix;
do not repeat the failed rate, fill its scores or enlarge its budget.

## 119. Prove sparse coefficients and audit affinity independently

Likelihood preparation now carries only nonzero formal coefficients at each
registered source row. These are identities for all selected weights, not
current-weight thresholds. Native nodes, fixed-slot derivatives and the full
domain remain. The dense analyzer at08fa7bc and the sparse pass agree on28,656
cases from the complete3,184-graph three-slot grammar portion. n2..6 model
descriptors agree except for recorded operation counts; n6 drops from2,536,316
to304,892. The conservative prepaid work/scratch formulas remain unchanged.

The passive verifier takes a different route: exact positive Gamma values
prove zero support, degrees prove affinity, and native mass reverse derivatives
recover coefficients. It checks21,204 banks against native vertices and
agrees on7,452 refusals. Vertex forecasts alone are insufficient:1+8w and
1+8w^2 share all simplex vertices and their normalized initial forecast, but
the latter's native unit step is(7/6,-1/6) and refuses. The production analyzer
already excluded the example; no false historical Runtime certificate is claimed.

Existing exact likelihood audits pass. Two further bounded development jobs,
PIDs22568/24360, seal profile/install and100-label reversal, replaying587 CUDA
and587 binary64 phases,194 commit tapes and40 fresh scores. Install22 and
recovery53/uniform100 persist. These are functional checks, not a replacement
for the nine source-bound jobs or a useful-scale model comparison. Proof and
minimal exact evidence are in SPARSE_LIKELIHOOD_ANALYSIS.md and its linked
report. Main execution remains fixed at38b27b3 while RN-5 task27 runs.

## 120. Compact likelihood information can still require hard forecast computation

The known-noise relation learner now has a conditional decoding lower bound.
For any fixed additive noisy-forecast error e<2/5, a uniform decoder resolving
all legal histories in polynomial time in n+T would imply P=NP. Repeating
label1 M times per edge of an unweighted graph gives posterior9^(M*cut).
Approximate anchor forecasts choose a branch with latent mass at least
gamma=1/2-e/(4/5). Repeating each chosen label M times preserves a maximum
cut because the total inconsistent/nonoptimal posterior mass is at most
2^(n-1)/9^M<=gamma/2. Each choice retains an optimum; n-1 choices recover it.
No edge-dependent giant forcing weight is needed: the same M suffices.

M is O(n+log(1/gamma)), history length is M(m+n-1), and each signed count
is bounded by2M. This avoids an invalid reduction from binary-weighted
MAX CUT by expanded labels. The cited primary result proves NP-completeness
already for unweighted simple graphs. The exact native normalizer remains10.
At e=2/5 the constant forecast1/2 works, so the accuracy threshold is sharp.
An exact scalar decoder streams2^(n-1) worlds with polynomial workspace;
no matching exponential time lower bound is claimed.

The audit explores all1,098 graphs on2..5 vertices at four rational error
bounds,32,089 adaptive states and every permitted threshold decision.
All8,617 terminal assignments are optimal; ordered products and count
decoding agree at each state. Twenty small settings additionally execute183
complete native units and36 query decisions. Proof and minimal evidence are
in FORECAST_DECODING_COMPLEXITY.md and its linked report.

The bound concerns uniform compact-model decoding, with preprocessing paid.
It does not concern polynomial time in the exponentially expanded graph,
typical IID risk, a fixed machine, or the cause of an RN-5 timeout. Adversarial
oracle histories are conditional-input problems, not a fresh stochastic
Runtime protocol. This result separates retained information from computation
without changing Foundation, ERC-1, sources, U or architecture actions.

## 121. Register useful-scale likelihood learning against retained strong controls

The next matrix tests all four original RN-5 n8 IID cases, c2 seeds16/17 and
c4 seeds18/19, with four new FP workers and the unchanged completed adaptive
posterior rows at6c202ea. This is a retrospective matched mechanism comparison.
The native v7 graph starts from actual fair Gamma, learns a complete one-pass
training profile under unit simplex U, then continues through ordinary
reference/binary64/AMP phases and paired fresh installation. Reference
forecasts are checked before each target against an independent posterior
which has no Runtime value authority. Candidate and deployment are scored
separately, with full independent numerical and wealth replays.

The fixed new envelope is16GiB host/two hours,8GiB packed,10^15 work per role,
32768-bit guards, native cap16, binary64 tolerance10^-9, AMP tolerances0.01
and0.001,256MiB arena and512MiB allocator. The phase frame is explicitly4MiB.
The complete graph has128 worlds,338 nodes,258 SUMs,64 PRODUCTs,10,368 edges
and129 slots; broad constructor caps double its five graph counts. The
historical decision class stays unresolved under one proposal.

Preflight passes without Torch or a new GPU execution. It records31,554
prediction cells,41,949 observation cells,58,433,467,456 prepaid derivation
work and2,029,576,576 scratch bytes. The same conservative formulas remain.
No n8 outcome is claimed at registration. Use an immutable experiment
checkout so the research branch can continue without changing an active job's
source. Main RN-5 remains at38b27b3, with its task27 still running.

## 122. Normalize the likelihood theorem, then attack its reachable-state scope

The one-event native simplex U now has a distribution-wide characterization.
At every interior weight and all labels, a fixed positive likelihood update
implies p_y=c_y*(w dot ell_y)^(1/eta). The second tangent derivative of the
normalization identity SUM_y p_y=1 is a positive sum of squares when0<eta<1.
It can vanish only for a readout independent of the selected weights.
Consequently an informative law forces eta=1, and normalized forecasts must
be affine on the simplex. The converse follows from the actual CE tangent;
ambient normal components cancel without erasing fixed-slot derivatives.

This removes affine unnormalized masses as a necessary global hypothesis.
A positive native common factor1+w1*w2 leaves forecasts and selected updates
unchanged but gives a reachable fixed-slot gradient144/22345 instead of0.
The exact criterion is the polynomial identity M_y-T*(w dot p_y(vertices))=0
modulo SUM(w)-1. The passive audit uses rational substitution; the running
Runtime still has its original narrower paid analyzer.

Attacking the quantifier produces an informative counterexample. A positive
three-world readout adds h=(w2-w3)^2 to one commonly scaled affine mass.
From fair Gamma, w2=w3 is preserved under every label, h and its selected
gradient vanish, and all selected updates are Bayesian. Off that invariant,
forecasts1/2 and177/352 differ. Thus full-simplex affinity is not necessary
for every reachable-orbit codec. Initial fixed gradients0 and-8/605 also
prevent a complete-state equivalence claim.

The larger complete tiny grammar has10,544 graphs,7,480 normalized-affine
certificates including20 informative cases,44,880 native unit checks and
3,064 independent native refusal witnesses. The retained3,184-graph subset
has no informative certificate; it is not counted as new independent graphs.
Two nonlinear examples each check160 paired continuous native transitions
over all five-label words, with clocks retained. Four-world substitution
adds36 native units over all nine source rows. Proof and minimal evidence
are in NORMALIZED_LIKELIHOOD_CHARACTERIZATION.md and its linked report.

Meanwhile the n8 matrix starts at90f3883 in the detached linked checkout
F:\FP-likelihood-model-run: parent15872, first worker2720, start04:31:40 UTC
on2026-09-14. No complete new model outcome is yet available. Main RN-5
task27 independently remains live at38b27b3. Source/dependency guards pass
for both executions while this research branch advances within the same
canonical Git repository. Foundation, ERC-1 and semantic actions are unchanged.

## 123. Finish the n16 RN-5 cases without inventing unavailable FP results

Task27, n16/c4 seed19 rate4 at38b27b3, reaches the registered two-hour timeout.
The completed job records PID12732, creation tick134338289186817892, exit1223,
attached-before-resume true, no host-limit process termination, and peak job
commitment9,627,586,560 bytes under16GiB. No valid worker report is available,
so the attempt supplies no score, install, seal or complete phase count.

Task28's unchanged adaptive posterior then completes as PID4704, creation
tick134338361192023420, exit0 and peak job commitment2,309,148,672 bytes. It
reconstructs256 actual GPU forecasts; unseen exact/AMP CE is0.3308954323/
0.3308954459, and full-domain exact/AMP CE is0.3299872356/0.3299872479. The
same16GiB/two-hour envelope remains. Parent11020 proceeds to task29, selected
n8 stress seed20 rate1, as worker21596 at05:08:48 UTC.

The preceding26 journal rows are identical. Independent analysis runs in the
original38b27b3 main checkout and verifies the28-attempt prefix:20 EXECUTED,
eight FAILED,12 sealed FP streams, nine installs,80 descriptive score checks,
12 fresh decisions,6,552 CUDA/binary64 phases each and1,280 new posterior GPU
forecasts. All eight n16 FP attempts now lack model scores: four c2 snapshot
MemoryErrors and four c4 timeouts. This is a finite execution result, not a
semantic infeasibility or complexity lower bound for those individual inputs.

The research runner's retained-baseline check now permits appended RN-5
rows while requiring the entire referenced26-row prefix and registration to
remain identical. Its four n8 controls are unchanged. The already running
n8 likelihood matrix stays in its immutable90f3883 checkout, retaining the
original26-row source snapshot. Neither live execution is patched or restarted.

## 124. Close RN-5 with its candidate gap, deployment waits and eight failures

The original38b27b3 driver completes all31 registered attempts. Tasks29/30,
selected n8 wrong-sign stress at rates1/4, both seal without installation;
task31's adaptive posterior completes. Their unseen candidate CE is
0.5518468081/0.5226972479 versus posterior0.4182379697, and deployed CE
remains log(2). The final status is COMPLETE_WITH_FAILURES:23 EXECUTED and
8 FAILED, with14 sealed n8 FP streams and9 installations. Every n16 FP
attempt lacks a valid model score:4 c2 final-auditor snapshot MemoryErrors
and4 c4 two-hour timeouts. The four n16 posterior controls all complete.

The complete analysis runs in the original execution checkout before any
source integration. It verifies7,564 CUDA and7,564 binary64 phases,92 dynamic
scores, fourteen fresh decisions and1,344 new posterior GPU forecasts. All
first28 journal rows remain byte-equivalent as parsed records. The original
budgets, separate earlier auditor failures and unreported interruption remain.
The largest completed job counter17,180,921,856 is slightly above the nominal
16GiB cap; only the four timeout counters are uniformly below that cap.

The inspected plot and RESULTS.md distinguish continuously updated candidates
from actual deployment, and all unavailable scores from scored cases. Rate1
has lower mean candidate CE than rate4 on both n8 IID groups, but both remain
above their strong adaptive posterior controls. Five sealed candidates do
not install, including both selected stress runs. Historical conditioned
class bounds keep their exact fixed-state empirical scope; the other ten
sealed class decisions remain UNRESOLVED. No future/model/AMP completeness
claim follows from sealing. The fixed-state sign-risk bound is not promoted
to a dynamic unseen-score bound.

The source-bound n8 likelihood matrix remains independent at90f3883; RN-5
completion neither supplies its model outcomes nor changes its fixed contract.
Foundation and ERC-1 remain frozen. This is closure of one registered model
experiment, not completion of the broader FP research goal.

## 125. Refute context-dependent betting under the original persistence null

After RN-5 final analysis passes, main fast-forwards through33a12e4 with all
final evidence and research commits retained. The separate n8 likelihood
matrix remains bound to90f3883. Subsequent research resumes in main.

The deployment gap suggests using each pre-target forecast to choose a
smaller local gain bound. Attacking that proposal exposes its invalid
filtration: the registered null conditions before the context, not merely
before the target. For every distribution on a finite outcome alphabet with
nonpositive mean gain, a nonnegative evidence factor is valid iff one common
nonnegative linear bet dominates it pointwise. One- and two-outcome nulls
give an elementary complete proof. Context-specific linear coefficients must
therefore agree when every active context has positive and negative gains.

A two-context positive native SUM graph predicts(0.9,0.1) and(0.6,0.4)
against uniform. The registered rate-zero native learner keeps it fixed
through ordinary gradient commits and advancing clocks, without retrospective
reset. A full-support IID joint law has
mean gain-0.01477198482, while valid-looking local bounds2 and1/4 with bet3/4
yield mean factor1.4049798428 and mean log factor0.2687293842. The unrounded
false-crossing probability exceeds705/961 by256 steps, and eventual crossing
is certain. Actual grid16 helper arithmetic also has initial expected wealth
4603797/3276800>1; repeated rounded eventual crossing is not claimed. Runtime
cannot select an owned rule after ingress, so no existing certificate or
Foundation theorem is falsified. The proposed shortcut is rejected.

The exact audit checks27,725 factor tables against134,450 independently
constructed null-vertex expectations,5,890 valid tables,256 context-bet
combinations and384 continuous native units. Rational logarithm enclosures
are independently checked with160-digit Decimal. The proof links established
e-variable literature without claiming novelty for mean-constraint duality.

The same examination identifies a legal pre-context bound for the likelihood
bank: exact p in[0.1,0.9], actual uniform comparator and AMP probability error
at most0.001 give |gain|<13/8 by exact endpoint enclosures. It can justify a
future common coefficient6/13 at bet3/4. The active bound6 experiment is not
patched, rerun or reinterpreted; no power improvement or new installation is
claimed. There is no Runtime code, semantic action or ERC-1 change.

## 126. Reproduce RN-5 analysis from a clean original-source checkout

After main integration, a fresh detached38b27b3 checkout receives only the
committed analyzer and final journal from33a12e4. Complete post-analysis
passes its original dependency guard and produces exactly the same parsed
summary and all per-worker details as the pre-integration analysis. No
model or GPU target is rerun. RESULTS.md now records the two-artifact source
reconstruction commands; the guarded replay remains in F:/FP-rn5-audit.
The running90f3883 likelihood checkout is unchanged. This validates audit
reproducibility after research integration without weakening source binding.

## 127. Bound current count-decoder rounding uniformly over accepted histories

The owned radix9 decoder reconstructs selected weights from exact counts at
every commit. Under its registered RNE32 schedule, the squared power for
exponent64 is zero and all later squared powers remain zero. Exact checking
of d=0,...,63 plus this analytic tail proves a uniform unnormalized absolute
error u/72, attained at d=1, with u=2^-24. The last nonzero decoded exponent
is47, with raw word1. These zeros do not replace the persistent coordinates.

Positive normalization gives the bound(K-1)u/72+gamma_(K-1)+u+2^-150 for all
accepted exponent vectors. The input normalization, actual serial SUM and
rounded division are all retained in the argument. At K128 the bound is
7.734587804e-6, independent of history length. Exact audit checks3,713 high-
bit tails,12,481 ordered three-weight vectors and520 controls at K2/8/128;
143,614 rounded operations agree with a separate binary64/cast calculation.
The largest observed K128 error is6.467816932e-6, with a compact retained
exponent/order witness, so the normalization contribution is material.

This is an arithmetic theorem for the existing selected-weight commit,
not a new actual GPU run or complete native-gradient/Runtime certificate.
Counter overflow, model derivation, source binding, actual operation words,
full gradient/cache state, evidence and host/device/work costs keep their
existing gates. Exact coordinates remain necessary for future recovery.
The active90f3883 likelihood matrix is unchanged; no unavailable outcome
is filled. No extra radix special cases or sharp constants are pursued.
Foundation R4, ERC-1 and semantic actions remain unchanged.

## 128. Retain the first n8 likelihood failure and replace its unsound scalar auditor

The first likelihood job at90f3883, n8/c2 seed16, exits1 in the inherited
100-digit Decimal gain comparison. The driver stops before the other three
cases. The complete original failure journal is retained verbatim, including
PID2720, creation tick134338339003000493, attachment before resume, no timeout
or job-limit process termination, and peak commitment15,474,765,824 bytes.
No valid model score, install, seal or complete independent phase count is
inferred from the missing report. The original execution checkout stays
historical; parent15872 and worker2720 are terminal.

Passive exact reconstruction reproduces a correct interval rejected by the
old check at case0/cursor65, for probability1436234048776862726818201/
2872468070873849901111602 against1/2. The job did not retain its offending
event, so this is not a recovered CUDA trace. A separate false-positive
example supplies the100-digit rounded log(3/2) as a rational zero-width
interval; the old check accepts it. Fixed Decimal comparison therefore has
both failure directions. No production log/U/wealth rule is changed.

The independent replacement normalizes the ratio into[3/4,3/2), uses signed
atanh series and log2=log(3/2)+log(4/3), and returns only when its proved
rational enclosure lies inside the claimed interval. Disjoint intervals
are rejected. Overlap after128 terms or a262,144-bit preflight/operand
failure returns LogAuditUnresolved. The Runtime keeps its32768-bit guard.
This verifies one scalar containment, without granting source, lineage,
freshness, alpha, bridge or install authority.

Exact audit passes1,572 valid intervals:1,024 rational/term grid cases,
14 near-one cases,21 scale cases, the concrete reproduction and512 retained
posterior label checks. Accepted cases use at most32 terms and8,103-bit
operands. It retains five rejection/budget tests and both known actual-label
legacy failures, at case0/cursor65 and case2/cursor50. Full reference,
paired CPU persistence and owned compiler policy regressions pass; the last
checks all64 six-label streams and256 independent gain/wealth events.
A bounded development CUDA warm-
profile job seals/installs at cursor22, checking286 CUDA and286 binary64
phases and40 fresh scores, with peak job commitment2,359,934,976 bytes.
Its compact record explicitly remains a development regression, not n8
model evidence or a new source-bound release.

The corrected protocol must rerun its four-case matrix only after this
checker is committed and tested. Before launch the runner requires exact
equality of the complete original model/resource registration dictionary,
and links the separately retained failed attempt. That equality passes:
no data, Gamma/U, graph, profile, baseline, bound6/bet3/4, alpha, numerical
tolerance,16GiB/two-hour or other resource parameter is changed. The failed
attempt is not relabeled; the corrected workers must earn their own results.

The corrected matrix starts from clean committed86083a0 in detached linked
checkout `F:\FP-likelihood-model-v2-run`, on2026-09-14 at07:06:48 UTC.
Parent23668 launches first worker16644. The initial journal records zero
completed outcomes and its explicit reference to the original failed attempt;
all execution dependencies are verified clean. Keep this source fixed while
main continues research. No running job is counted as a successful model.

## 129. Compose uncertainty learning with finite physical persistence power

The running n8 matrix exposes a scientific distinction that remains even
after exact posterior forecasts are proved: useful prediction does not
immediately imply fresh paired crossing, and valid downward rounding does
not automatically retain power. The earlier power result left physical
wealth composition open. A new scoped theorem closes that composition for
the actual likelihood model and its original coefficient1/8, with no new
bet, bound, grid, model or semantic action.

At the post-profile cut, the power alternative draws the hidden relation
world from the candidate's posterior and supplies independent noise1/10.
Queries may be causal but cannot add unmodeled latent or current-target
information. Exact native Bayesian telescoping and the chord of the log
evidence factor give a pathwise lower bound: initial world uncertainty costs
A log(1/w_h), where A is approximately0.1344964. No per-event positive gap
or prior identification is assumed. Conditional noise counts are binomial.

Under that alternative, inverse ideal wealth is a supermartingale because
the log-loss second moment is at most three times its mean and the existing
factor is above3/4. This controls downward excursions. The actual score
relation, including AMP error0.001 and12-term lower logs, gives common
score deficit below1/98 and factor distortion587/588. The actual grid16
recurrence is bounded below by the ideal product less its accumulated floor
losses. One common drawdown event covers both reference and AMP paths.

At horizon64, alpha1/4 and analysis parameter kappa1/4, the drawdown allowance
is below0.004356. Exact binomial cutoff sums using only the four retained
training profiles give lower bounds0.892775,0.892855,0.808954 and0.809044,
rounded down. These are posterior-mixture law bounds for paired crossing
when required computations remain available. Without that completion premise
they bound crossing or operational failure; they never condition on passing
workers or substitute for measured installation. No evaluation targets or
new GPU scores enter the calculation.

Two scope attacks succeed. A single adverse label in the native two-world
learner gives forecast(9/50,41/50); inverse-factor mean exceeds1 conditional
on the equal-bit world but is below1 under the posterior mixture. Thus the
reciprocal result cannot be asserted under every fixed hidden world. Also,
45 consecutive adverse self-query labels drive actual grid16 wealth to zero,
with1/65536 immediately before absorption. This has probability10^-45 under
the correct IID noise law, despite positive unrounded log drift. It falsifies
almost-sure-power transfer, not the validity of lower wealth.

Exact audit passes158 interior chord inequalities,81 reciprocal expectations,
all64 six-label words with384 continuous native units and384 actual floor
composition checks,1,536 mixture comparisons and126 certified noise cutoffs.
Independent rational log verification precedes outward96-bit interval
arithmetic. The two native counterexamples and small probability bounds are
retained, without weights or event tapes. The matrix at immutable86083a0
continues unchanged and supplies no completed outcome yet. Statistical
composition is settled in this scope; continue actual model execution.

## 130. Prepare independent minimal-record analysis for the running n8 matrix

The corrected first worker remains live at86083a0 with no completed result.
An independent reader now checks the retained attempt/job/source identities,
reconstructs exact stored-mass probabilities from binary32 words, and keeps
raw divisions separate. It recomputes reference posterior forecasts in a
different world order, checks expected CE with binary64 and Brier intervals
with an independent exact expansion, and uses the corrected exact log checker
for fresh reference/CUDA wealth. Deployment receives only forecasts at its
actual installation cut. No complete-class proof is inferred from one v7
proposal, and crossing alone does not force an installation.

The reader summarizes the completed worker's independent full phase audits;
the minimal mass-word journal is not misrepresented as another full raw-tape
replay. A single admitted identity without a retained path label gives
unresolved fresh reconstruction. Failed jobs and halted streams have no
imputed complete scores. The original90f3883 failure remains separate.

Development validation passes twelve malformed/nonfinite word, duplicate or
missing readout, stale cursor, zero mass, premature install, extra fresh
event, failed-job promotion and false-class-certificate checks. It explicitly
accepts paired crossing without installation. Sixteen retained strong-control
scores are independently checked, without a baseline worker rerun. The initial
prefix still has zero completed model rows; successful model-result validation
awaits the actual corrected worker. Preserve the reader's committed source in
`F:\FP-likelihood-model-audit` while main continues implementation research.

## 131. Reduce arena metadata overhead while preserving complete snapshots

The retained four RN-5 n16/c2 failures occur while materializing the complete
region table in CudaArena.snapshot. The storage source is unchanged from38b27b3
through b85b39d. The region record carries ten fields in an ordinary frozen
Python dataclass. Main now uses a frozen slotted dataclass with the identical
field set and defaults; no record, old extent, snapshot row or guard is removed.

The preservation argument covers construction, field access, immutable
replacement on a whole-extent write, detached snapshots, initialized reads
and installation leases. Every relevant arena continuation uses those retained
fields and explicit sequence/phase/owner identities. Physical Python layout
and resource outcomes can change; complete-state byte charges, native arena,
allocator history, frame caps, actual job accounting and all admission gates
remain in force. This is no new architecture action or Foundation revision.

Four attached512MiB/120-second host jobs compare the actual old source with
the slotted representation at250,000 and500,000 regions. Every field in all
1,500,000 snapshot rows matches the declared construction. Peak job bytes
fall147,939,328 to135,356,416 and276,951,040 to251,043,840, respectively.
The separate360-case field/replacement/detachment audit passes. A shallow
object-size diagnostic materializes one ordinary instance dictionary and is
not extrapolated into process memory. No GPU throughput claim is made.

The full existing CUDA storage audit passes, including1,306 learner phases,
32,996 initialized views,216 typed allocation sequences and648 requests.
All thirteen installation cases pass, including learned/recurrent state,
corruption/extent guards, capacity refusals and fresh evidence against a new
baseline after an earlier install. The bounded likelihood profile job also
seals at cursor46 and installs at22:286 CUDA and286 binary64 phases,94 commit
tapes and40 fresh scores; peak job commitment2,354,864,128 bytes within4GiB.
Its full constructor class remains UNRESOLVED. Compact development reports
retain these checks without raw region tables, weights or large tapes.

No n16 model job has been recovered by this evidence. Original failures and
the current n8 matrix remain unchanged. The latter executes at86083a0 while
its independent reader is pinned at b85b39d in the separate analysis checkout.
Main can advance without silently changing either source or their outcomes.

## 132. Isolate deployment delay even for posterior-exact learning

The finite fresh-power theorem survives the failure/filtration recheck: its
bound concerns crossing or operational failure without conditioning on which
workers pass. A separate passive analysis now reads the retained evaluation
tapes to isolate the registered rule's actual delay even when learning is
posterior-exact. This is explicitly retrospective, not another profile-only
power result or an imputed outcome of the running matrix.

For every proper AMP forecast in the original0.001 probability tube, a uniform
production-log width bounds its actual lower score from both sides. Monotone
grid16 wealth recurrences then enclose first crossing, with the exact reference
crossing retained separately. Pairing gives ordinary cursors114-115,90,72,72
for the four n8 cases. No alternative bet, source law, numerical tolerance,
resource limit or semantic action is introduced.

Conditional on the original installation gates and subsequent predictions
succeeding, the first case therefore leaves only9-10 of64 forecasts for the
candidate. Exact convex CE intervals give deployed unseen CE in
[0.659686,0.668053], versus reference candidate CE about0.342961. Cancelling
the shared post-install trajectory proves at least0.316620 extra unseen CE
from waiting over the same AMP candidate. The other three conditional waiting
penalty lower bounds are0.166668,0.120500,0.166420. Earlier installation is
not presumed to improve every query's true risk; possible cursors are
enumerated and every risk interval is rounded outward.

The exact audit checks63 native prediction prefixes,126 native complete
units, all46,656 six-event label/proper-forecast paths and55,986 applications
of the actual wealth helper. Four unsupported reference probabilities are
refused. The256 retained n8 reference forecasts give eight CE comparisons
with the original strong controls. All1,975 log enclosures are independently
verified, needing at most32 terms and16,061-bit operands. No Torch import,
model/GPU worker or baseline rerun occurs. The compact record retains only
scalar envelopes and counts, without world weights or event tapes.

Actual source-bound completion remains the test of whether the owned procedure
realizes these premise-qualified predictions. Missing admission, resource
failure, numerical refusal or failed installation retains its own outcome.
It acquires no hypothetical score from this analysis. The matrix at86083a0
and its b85b39d result reader stay fixed while main records this research.

## 133. Complete the first owned posterior learner at the retained n8 model scale

The corrected86083a0 c2/seed16 worker16644 completes under its original16GiB
and two-hour limits. It seals at124, constructs/selects one native v7 member,
profiles all60 training events and matches the independent exact adaptive
posterior on every one of64 pre-target reference forecasts. Its full
constructor class remains UNRESOLVED. No other candidate family is excluded.

The worker independently replays748 CUDA and748 binary64 phases,248 actual
commit tapes and108 fresh scores. Both reference and actual CUDA stored-mass
paths cross at114 after54 fresh labels; the ordinary policy installs then,
with full owned state/lease transport. Candidate unseen CE is0.342961291
against the retained exact posterior's0.342961337. Actual deployed unseen CE
is0.659686798, leaving a0.316725507 waiting penalty and only ten deployed
candidate forecasts. The near-neutral relation-error metric changes1/88 to
1/44 under rounding; tiny CE differences are not treated as dominance.

The separate b85b39d reader passes its first successful real model result,
reconstructing six scores and the paired decision from retained word records.
It also rechecks sixteen strong-control scores without new baseline workers.
The previously committed crossing/risk envelopes contain the actual install
and both unseen/full-domain candidate, deployed and waiting-cost values.
This establishes a real owned posterior implementation in one registered
case and confirms the remaining deployment delay predicted by theory.

Peak job commitment is15,478,538,240 bytes, packed peak3,206,983,117 bytes,
maximum output cells41,949 and largest evidence frame3,544,209 bytes. All
original caps remain. The journal is copied only after verifying prefix and
registration equality; the original90f3883 failed attempt remains retained.
The one-row independent analysis and concise results page are now canonical.

Parent23668 continues at the same source. Worker10820 starts c2/seed17 at
09:02:48 UTC on2026-09-14; the two c4 cases follow. No aggregate conclusion
is drawn from the remaining uncompleted cases. Main's subsequent readback
optimization does not change this execution or receive credit for its result.

## 134. Complete the four-case owned posterior matrix and measure its deployment cost

All four corrected n8 likelihood jobs at86083a0 finish under their unchanged
16GiB/two-hour limits. Each constructs/selects the native v7 member, profiles
its training stream, seals and installs. The full classes remain UNRESOLVED.
All256 exact pre-target forecasts equal the independent adaptive posterior.
Independent worker replay checks2,752 CUDA and2,752 binary64 phases,912
actual commit-operation tapes and296 fresh scores. Maximum job commitment
is15,478,538,240 bytes; packed peak3,208,396,061 bytes, output cells41,949
and frame bytes3,544,209 stay within their original caps.

The paired paths cross and the policy installs at114/90/72/72, after54/30/
32/32 fresh labels. Candidate/deployed unseen CE means are0.338495/0.580218
for c2 and0.365450/0.509115 for c4. The largest stored-mass posterior error
is below6.677962e-5. All four conditional crossing envelopes and24 candidate,
deployed and waiting-cost risk envelopes from section132 contain the actual
results. The first case's0.316725507 waiting penalty confirms the distinction
between posterior learning and useful deployment. Close CE does not erase
its changed near-neutral relation-error metric.

The pinned b85b39d reader independently reconstructs24 model scores and
four fresh decisions, rechecks16 original strong-control scores, and verifies
the terminal journal/source/registration. No baseline is rerun. Both retained
RN-5 v5 rates and exact/AMP posterior controls appear in the results and
comparison figure. Every likelihood candidate scores lower than both v5
rates on its retained case, but graph, Gamma, U, lowering and resources change
together; this is no isolated-mechanism or population conclusion. The separate
posterior predictors receive no invented FP deployment record.

The canonical final journal is copied after registration/prefix equality
checks; the original90f3883 failed attempt remains verbatim and unscored.
All four workers and parent23668 are terminal. Later main storage/readout
changes did not run in86083a0 and cannot explain these outcomes. n16 recovery,
useful evidence efficiency and broader model performance remain open; this
experiment does not reopen Foundation/ERC-1 or freeze a new full release.

## 135. Batch raw CUDA observation without losing words, ownership or failed state

A short nonblocking sample of the original86083a0 worker motivates reducing
per-intermediate device-to-host copies; its65 successful/34 failed samples
are explicitly not a whole-job time estimate. The new observer copies the
covering byte span once and decodes the same ordered initialized binary16/32
views. No GPU arithmetic, complete operation record, failed intermediate,
coordinate or lineage is removed. Opaque padding never becomes a numeric
source and the CPU transport prefix is cleared in finally.

The arena's per-allocation padding bound proves8C bytes suffice for a phase
with C charged output cells, including zero-size and integer/bool temporaries.
Runtime owns that workspace before CUDA binding and keeps it resident. An
injected post-copy exception shows why phase-local freeing would be wrong:
the actual traceback retains a CPU tensor alias. The retained owner covers
that alias, and all four public cuts retain a zeroed buffer without cursor
advance or failed-phase promotion.

Final proof review finds that the draft's three-pass allowance misses an
unencoded simplex commit: two positive-normalizer checks, proposal and final
checks, outer prefix and trace total six captures. The work coefficient is
corrected from the old128C to320C before commitment. An actual six-event
simplex Runtime seals, independently checks19 phases per path and counts13
three-capture phases plus six six-capture commits. This is an accounting
correction within the existing work model, not an architecture action.

The bounded observer audit checks all65,536 half words,526 single words,
ordered/duplicate/subviews/empty views, nine refusals, padding/buffer poison
and fresh detection of an infinity introduced after a prior successful check.
Three4GiB/120-second jobs pass. An ABBA fixture reduces8,192 synchronous
copies to one; scalar trials take0.237/0.269 seconds and bulk0.022/0.035,
without any model-throughput claim. Full CUDA Runtime and13 installation
cases pass again after the six-pass correction; a bounded likelihood stream
seals at46 and installs at22 with286 phases per path,94 commit tapes and40
fresh scores. These targeted checks do not relabel the baseline release.

The added resident extent and increased declared work can change feasibility.
Every completed n8 model ran the earlier86083a0 source; none used these
optimizations. No previous n16 failure is erased and no recovery is claimed.
The next research question remains useful deployment and complete model
execution under a separately declared, semantically valid procedure.

## 136. Close the pre-context range gap for a tighter owned persistence rule

The completed n8 study isolates fresh-evidence delay after exact posterior
learning. The previous13/8 likelihood bound used successful AMP closeness;
that alone cannot define a bounded score on a failing next attempt. Existing
Runtime admission instead used binary base one and R16 to prove log15, so it
could not admit13/8. This is a loose solver bound, not a Foundation failure.

For positive mass intervals L<=m<=U, normalized probability has sharp box
endpoints L_y/(L_y+sum_other U) and U_y/(U_y+sum_other L). Maximizing the paired
ratios across every declared source row gives one common pre-context bound.
The proof uses native positive masses and already owned domain enclosures;
no context-specific coefficient, new source or architecture action enters.
Physical enclosures concern the mathematical rounded predictor on failing
attempts as well as successes. Against uniform, candidate masses in[1,9]
give K5, with log5<13/8 independently of a next-query tolerance check.

Runtime keeps the cheap original class-cap proof, then pays for this
refinement when necessary. The existing identity now records whether its
ratio bound is class-wide or current-state. An ACTIVE current-state proof
is refreshed after the event and before next ingress. Current event scoring
uses the old pre-context bound. Failure leaves the identity unresolved,
spent alpha and actual event history retained. Crossing stops the statistic;
ordinary lineage and install checks still apply. No rule is changed in place.

Exact enumeration checks2025 paired boxes,181,440 normalized corner ratios,
306 sharp endpoints and eight malformed/budget refusals. An actual candidate
starts uniform under B1/4, updates to theta4 while still native-range-safe,
and correctly loses its tighter evidence identity before another context.
A harmless actual context cannot overcome an unsafe alternative domain row.
A calibrated work cap refuses refinement before its arithmetic executes and
retains the allocated alpha.

Two bounded n2 profile/install jobs, CPU and RTX3090, register B13/8 with the
existing3/4 fraction, yielding common coefficient6/13. Both seal/install at8
after six fresh labels; each checks280 binary64 phases and12 fresh scores,
and the CUDA job also checks280 device phases. Every bound calculation's
information cut is checked. Retained B6 fixtures installed at22 after20
fresh labels; no baseline is rerun. Maximum job commitment is37,785,600 bytes
for CPU and2,391,838,720 for CUDA, within512MiB/4GiB and180 seconds.

Full reference, paired CPU and CUDA persistence suites pass, retaining their
existing fair-null, failure, nontransfer and same-path evidence checks. The
current solver is a validated route to a separately registered deployment
experiment. It establishes neither n8 improvement nor a power ordering, and
does not transfer an uninterrupted or differently stopped epoch-null to the
new procedure. The completed four-case bound6 study remains unchanged.

## 137. Register the tighter-bound deployment test and distinguish threshold from authority

The mass-box proof makes the existing common coefficient6/13 reachable, but
does not show useful n8 deployment or a finite-horizon ordering over1/8.
One fixed protocol therefore registers B13/8 on all four retained tapes.
The runner compares full setups: only the persistence declaration differs;
learner, graph, Gamma/U, alpha and all resource caps stay fixed. Current
slotted metadata and owned bulk observation are included with their actual
charges, so successful execution and candidate-word agreement must be tested.
All four B6 results, the original auditor failure, both earlier v5 rates and
the exact/actual AMP posterior controls remain at their original sources.

Before launch, actual reference execution exposes a reporting distinction:
an event can cross the numerical threshold while retaining its crossing
identity fails. The event is real, but installation authority is absent.
The detailed recorder preserves both facts, each path's retained scalar
prefix and paid refinement attempts. It never supplies hypothetical scores
after an identity stops. The independent reader checks rule, path, alpha,
wealth floor, cursor, owned crossing and paired installation separately;
complete phase, range and transport evidence remains the worker's scope.

Two actual reference paths, including injected crossing-retention failure,
pass. Nine forged rule/scope/wealth/cursor/work/install records are refused.
The common reader still checks all24 prior model scores, four old decisions
and16 strong posterior scores. These are reader-development results with
zero new model workers. Execute the committed protocol from an immutable
checkout before making any n8 improvement claim; no bet menu or control
rerun is authorized by this registration.

The registered matrix starts from immutable8ccacc0 in a separate execution
checkout on2026-09-20 at15:25:40 UTC. Parent14264 and first worker2444 are
observed live with matching commands and creation times. The initial journal
is retained only after same-source registration and reader checks; it has
zero completed outcomes. The reader rechecks24 B6 scores, four B6 decisions
and16 posterior scores. These launch observations establish no new model
outcome. Keep the execution source fixed while main research proceeds.

## 138. Faster ideal evidence growth need not give earlier deployment

After the13/8 protocol is committed and launched, passive exact analysis
predicts its outcome under successful owned proof/retention/physical/install
premises. The same full AMP probability tube gives unique paired cursors
119/67/54/50. The first case is later than its retained B6 cursor114 and
would have more than0.016 worse unseen deployed CE; the other three are
earlier. Its reference wealth falls to873/32768 at cursor84 before recovery.
This result is retained before a completed new worker is observed, and the
running rule, source, caps and case order remain unchanged.

The failure is not a mass-bound or mean-null-validity counterexample. Keeping
the3/4 fraction while tightening B increases the actual risk coefficient.
For a correct binary posterior p against uniform, write a=log(2p),
b=log(2(1-p)) and mu=p*a+(1-p)*b. The exact expected reciprocal contracts
iff the coefficient is at most mu/(-a*b). The native p9/10 self-query has
expected reciprocal0.963585 at1/8 and1.096773 at6/13, while expected log
growth rises from0.041348 to0.080229. Downward production rounding cannot
repair the latter reciprocal inequality. Thus the earlier finite-power
proof's reciprocal step does not transfer even to a correct native posterior.

The exact audit checks that native witness,256 pre-target forecasts,90
production wealth updates before crossing and1,964 independently enclosed
logs, using at most32 series terms and16,061-bit operands. Conditional CE
intervals cover all allowed AMP perturbations and keep failed gates unscored.
No model or baseline is rerun, and no new rule is chosen from these labels.
Compare the fixed physical outcomes next; do not confuse larger ideal growth,
improved admission bounds, finite first passage and useful deployment.

## 139. Derive the state and precision obligations of a common adaptive bet

The fixed-coefficient counterexample motivates investigating adaptation, while
the registered GPU run remains untouched. Classical continuous wealth mixtures
already supply one common predictable coefficient under the same mean-null.
The research issue is which past information a finite implementation must
retain, rather than a menu of bets selected from the exposed model tapes.
No model tape is used in this analysis and no novelty is claimed for the
Cover–Ordentlich mixture or its classical regret bound.

An arcsine mixture has a positive Bernstein-coefficient recurrence driven
by z=1+x>=0. Both wealth and its next common coefficient are finite rational
readouts. Exact continuation equivalence is equality of the moments needed
by the remaining scalar horizon; sufficient remaining future inputs determine
the whole normalized polynomial. Two length-two words have the same unit
wealth but a common continuation separates them by1/352. This is a scalar
interface result, not permission to quotient complete Compiler state.

Coefficientwise downward rounding preserves a one-step supermartingale
inequality against the rounded state's own previous wealth. At horizon H,
H+p fractional bits ensure error below2^-p on every allowed history. The
coefficient payload and streamed exact readout have explicit polynomial bit
bounds, with O(H^2) arithmetic operations. Expanding the arcsine moments shows
the readout weights are dyadic; the apparent factorial denominator is
unnecessary, and O(q+H) readout bits suffice. The constant coefficient prevents
absorbing-zero wealth at finite live cuts. These facts do not include an
extra scalar wealth rounding, physical resource success or an owned install.

Precision changes equivalence: at grid one,(-1/4,1/2) and its reversal give
13/16 versus1 although their exact products commute. A gain histogram cannot
replace the state of that rounded procedure. Classical wealth regret also
does not imply first-passage dominance: after three unit positive scores,
the mixture remains below4 while the fixed3/4 fraction has crossed.

Exact audit covers15,625 six-score words,19,531 prefixes,39,060 rounded
updates,31,248 zero-mean null pairs and39,062 independent monomial readouts.
The sharp classical comparison is checked through64.32 native five-label
words check160 pre-target forecasts/complete units and the production-score
precision bound. Four64-event words check256 prefixes at96 fractional bits,
including non-dyadic input scores and the readout/payload bounds. All evidence
is passive. Runtime still has its fixed-rule
contract; ownership, failure publication, separate AMP evidence and actual
model utility are not inferred from this prototype. Foundation/ERC-1 and
the running8ccacc0 experiment remain unchanged.

## 140. Retain the adaptive curve as owned persistence state

The scalar proof now has a guarded implementation inside the existing fresh
persistence lifecycle. A separate immutable arcsine declaration names its
coefficient precision; it does not carry an unused fixed coefficient or
pretend coefficient rounding is scalar wealth rounding. The complete tuple
and its exact streamed readout share one owned identity update. No new
semantic architecture action, search certificate or install bypass is added.

Work is charged before seed/update arithmetic, exact integer operations
preflight their bit extent, and alpha remains spent on terminal failure.
A failed crossing save can retain a numerical threshold event while keeping
the previous owned curve. The stopped identity has no crossing authority and
cannot revive. A real128-bit limit with q124 also admits successfully, then
refuses the first product without losing the target or refunding alpha.

The audit checks243 scalar words/1,215 updates using independent monomial
integration, nine malformed/numerical refusals,160 actual fair-label scores
and31 conditional inequalities. A changing learner checks four three-event
evidence epochs separately from six optimizer commits. Calibrated immutable
work caps refuse both initialization and epoch arithmetic before entry.
The old reference, paired CPU binary64 and kernel suites also pass.

This is an owned reference result. New-rule paired CPU/CUDA profile, bridge,
physical-resource and install evidence remains separate. The added optional
field changes packed identity sizes even for constant rules; no complete
release or universal resource-feasibility preservation is claimed. The
bounded development audit preserves failed process attempts and requires
committed clean execution dependencies. No such worker has run yet. The
registered8ccacc0 n8 experiment stays immutable and all old controls remain.

## 141. Exercise the adaptive state through CPU install and paired failures

A committed4daf126 development worker now passes the existing complete n2
likelihood profile, binary64 bridge and installation gates. The512MiB job
is attached before resumption, exits normally and peaks at39,084,032 bytes.
It checks44 exact posterior forecasts,280 binary64 phases and16 independent
fresh scores. Both positive curves cross after eight fresh events and install
at cursor10; the46-observation stream seals. Each curve retains nine cells
and53,248 paid update work. The historical search class stays `UNRESOLVED`.
The fixed-fraction3/4 fixture at the same bound had installed at8; reaching
installation supplies no general first-passage or model advantage.

Three new-rule paired failure cases independently replay42 scores. A native
mass increment2^-54 produces a reference crossing at6 but zero stored finite
gain and unit finite wealth. A refused finite crossing save keeps its old
curve and cannot borrow a live reference crossing. Failed shared ordinary
publication leaves both executed crossing curves as history while revoking
current paired authority. Targets and both alpha allocations stay retained.

The minimal record preserves bounded attempt provenance across subsequent
audit writes. New-rule CUDA and larger model value remain unverified; the
ongoing registered8ccacc0 source is unchanged. This is a scoped reachability
and adversarial result, not a new release or complete-class certificate.

## 142. Prove finite power without the failed reciprocal premise

The positive curve's absolute rounding bound composes directly with its
classical pathwise comparison to any fixed coefficient. At q=T+p, every
successful path has wealth at least r^T W_c/R_T minus2^-p, with R_T at most
2sqrt(T). Native Bayesian telescoping and the endpoint chord lower-bound
W_c by the realized noise count and the initial weight of each world.
No division by earlier wealth or reciprocal-contraction premise is used.

This also removes the old proof's need to draw the actual world from the
learner's posterior. The loss inequality is worldwise, and fresh1/10 noise
gives a binomial count under each fixed world, including adaptive past-only
queries. The theorem bounds crossing or operational/premise failure, never
success conditioned on completion. With a fixed finite positive weight
vector and q=T+p, the finite-declaration bounds tend to one. This is neither
fixed-precision almost-sure power nor free alpha across restarts.

Attacking necessity gives a useful limitation: a fixed comparator with the
same fine scalar precision also has bounded absolute rounding error and
needs no R_T penalty. Its matched lower bounds are stronger and its statistic
is one rational. At uniform128-world initialization, T128 and160 fractional
bits, the mixture's bound is0.861239 versus0.970213 for the fine-grid fixed
control. These are worldwise conditional-law lower bounds, not empirical
rates or actual first-passage ordering. The mixture still supplies simultaneous
coefficient comparison, whose complete resource value remains unproved.

The exact audit checks2,430 curve compositions and matched fixed-control
updates. Two native initial weight vectors, one nonuniform, each execute
all64 six-label words:768 complete units,3,072 worldwise compositions and
1,536 production score/curve checks. Rational pre-target perturbations test
the physical score tube without pretending to execute AMP. Uniform-prior
power examples use no model tape. The6/13 comparator also has positive
distorted growth even though its old reciprocal lemma is false. The actual
registered experiment, Runtime declarations and Foundation/ERC-1 stay fixed.

## 143. Observe the predicted deployment regression in the first actual job

The fixed8ccacc0 matrix's first worker2444 completes normally and seals at124.
Its reference and CUDA identities each score59 labels, cross at119 and pass
full transport/install. The old B6 control installed at114. Both candidate
readout forms are bitwise identical to the old control, yet deployed unseen
CE rises from0.6596867981 to0.6764169893. This is an actual retrospective
counterexample to uniform benefit from the tighter valid bound.

The job checks64 exact posterior forecasts,748 phases per path,248 native
commit tapes and118 fresh scores. Peak15,047,073,792 bytes fits16GiB.
The independent reader runs from the same immutable source, verifies six
new scores and two fresh paths, and rechecks all24 old B6 scores/four
decisions/16 strong-control scores. Its journal/analysis append only the
verified new row. The old prefix and registration are preserved.

The actual cursor and both conditional risk envelopes match the previously
committed prediction. No future case is inferred. Parent14264 starts worker
6920 at17:09:20 UTC on2026-09-20; it is verified live at17:11:45 UTC. The
remaining three attempts proceed under the same source, rule, order and
limits. All constructor classes remain `UNRESOLVED`.

## 144. Test the adaptive curve against an equally precise fixed control

The protocol and passive analysis code are fixed at57ac5a9 before execution:
arcsine coefficients on grid96 versus the preceding theorem's coefficient
1/3 scalar control on grid96, both at B13/8 and alpha1/4 per path. There is
no coefficient sweep, rule retuning or new GPU worker. All four exposed n8
tapes and all retained controls remain in the calculation.

Positive-state monotonicity gives conditional AMP first-crossing envelopes.
Mixture paired cursors are117/69/55/51; the fixed control gives100-101/69/56/52.
The first adaptive curve waits16-17 more events and has over0.075284 worse
unseen CE. Its58 cells carry7,760 unsigned coefficient payload bits plus416
wealth bits, versus the fixed control's one190-bit scalar. These are statistic
costs only. On the last two cases the mixture gains one full-domain prediction,
about0.00575 CE, while unseen envelopes coincide. Neither first-passage ordering
nor universal deployment benefit follows from the classical wealth guarantee.

The exact audit checks10,368 prefix enclosures and31,104 independent readouts,
reconstructs256 reference forecasts, and verifies1,954 exact log intervals.
Synthetic censored-path checks separately refuse a physical upper-envelope
crossing as a substitute for an uncrossed reference identity and retain
possible continued uniform deployment when the AMP lower path does not
cross. No scalar outcome becomes a model result or an install certificate.

This is evidence against promoting the larger adaptive state from power or
regret alone. Keep the equally precise fixed control, keep the existing
curve's continuation obligations intact, and do not turn this comparison
into a menu search on the same labels. The live8ccacc0 matrix and actual
first-row result remain separate and unchanged.

## 145. Close the exercised adaptive CUDA bridge and install path

The new rule's actual RTX 3090 development worker runs from committed clean
3490d76 in a4GiB job attached before resumption. PID17356 exits normally with
peak2,392,080,384 host bytes. It checks44 exact posterior forecasts,280 actual
CUDA and280 binary64 phases, and16 independently reconstructed fresh curves.
Reference and CUDA wealth differ; both cross at10, complete transport/install
passes, and the46-observation stream seals. Each stopped curve has nine cells
and53,248 paid update work. The class remains `UNRESOLVED`.

The previous CPU job/source remain in the same minimal attempt history.
The GPU audit overlaps model worker6920, observed live before and after
it in the17:24:56-17:25:33 UTC bracket on2026-09-20. This overlap is explicit
evidence, not hidden under an exclusive-device timing claim. The registered
model source stays8ccacc0 and no rule, cap, case order or outcome is changed.

This closes the exercised mixed-precision reachability gap. It neither
completes all possible failure tests nor changes the retrospective deployment
reversals. The extra adaptive state still needs a research justification
against the strong scalar control; implementation success is not that proof.

## 146. Preserve every CUDA frame byte while eliminating repeated snapshot payload copies

The first tighter-bound n8 worker peaks at15,047,073,792 host bytes. Code
inspection identifies a concrete representation cost: all completed CUDA
frames remain bytearrays, and every complete snapshot copies them again.
The748 four-MiB frames alone total3,137,339,392 bytes per copy. This is an
extent calculation, not a measured attribution of the whole-worker peak.

The [new representation](theory/proofs/IMMUTABLE_CUDA_EVIDENCE_FRAMES.md)
converts a frame only after its final write, preserves all padding and fields,
prepays work and the duplicate extent, and publishes with the existing root
transaction. Expected or unexpected preparation failure keeps both buffers
owned. Phase acceptance still follows successful retention. No mutable
ingress, learner buffer, numerical operation or installed identity changes.

The exact audit passes33 frames and17,904 complete-byte comparisons, checks
all256 values and nonzero padding, preserves prior snapshots after a new
frame, refuses two real resource boundaries before copying, and retains both
buffers in four injected prepublication faults. The fixed host comparison
uses128 one-MiB frames, two live complete snapshots,512-MiB/60-second jobs;
actual simplex/likelihood installation and finalization failures have their
own4-GiB/180-second fixtures. These bounded executions are pending at this
commit. The live8ccacc0 experiment remains unchanged. No n16 or whole-model
recovery is inferred from the exact frame-payload law.

The bounded `c133008` batch then passes eight CUDA workers. The simplex and
likelihood profiles seal and install at22, with566 independently checked
CUDA/binary64 phases each,80 fresh score checks and94 likelihood commit tapes.
The observer compares148,373,504 complete frame bytes across these profiles.
Existing frame-cap/combined-failure checks and four new finalization fault
workers also pass, including target retention, no acceptance and original
unexpected-error priority. Model worker6920 remains live during and after
the batch, explicitly excluding exclusive-device timing claims.

Both host jobs fail in report serialization of their read-only peak mapping.
Their original jobs/counters remain retained unscored. A small independent
reproduction confirms the TypeError; converting the report mapping to dict
changes neither Runtime nor the fixed fixture. Only those two jobs need
repetition. The CUDA passes are not rerun for this reporting correction.
