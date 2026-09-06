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
