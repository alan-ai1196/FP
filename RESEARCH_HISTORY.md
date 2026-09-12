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
