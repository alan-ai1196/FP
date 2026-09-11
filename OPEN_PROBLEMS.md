# FP Open Problems

Only genuinely unresolved problems belong here. Historical problems that were solved or falsified are documented elsewhere.

## 1. Close the complete Reference Compiler runtime

**Exact statement.** Implement one complete execution surface that instantiates `FP_THEORY.md` without allowing a caller to bypass claim state, information, value reachability, physical ownership/resources, numerical enclosures, persistence or bridge provenance.

**Why it matters.** The frozen foundation is only useful scientifically if the actual Compiler optimizes the same object. Most historical FP failures came from a correct local theorem being embedded in a smaller/different executable system.

**Known.** An intermediate 2026-09-05 reference implementation had a full module set and passed 24/24 unit tests plus 47/47 gate registry. Subsequent adversarial hardening changed the complete Runtime contract. The final endpoint integration was not re-frozen before persistence moved to GitHub. Historical R4.2/R3 implementations are complete but theoretically superseded.

**Already-failed methods.** Bare certificate booleans, caller-supplied exact uppers, arbitrary query callbacks, caller-built candidate states/object lists, resource totals without ownership, e-wealth reuse across lineages, state/cursor mismatch, partial ref↔AMP bridging, and helper-level tests that do not traverse the complete Runtime.

**Sufficient falsification of the current foundation.** A minimal program that is legal under `FP_THEORY.md` but cannot be represented/considered by any implementation conforming to the Reference Compiler contract **unless a new semantic model primitive is added**. Slow search or `UNRESOLVED` does not falsify the foundation.

## 2. Prove/test implementation-level completeness of native candidate construction for each declared decision class

**Exact statement.** For every `CERTIFIED_COMPLETE` decision, the implementation must expose the explicit finite/effective candidate class and prove that its native construction/search representation covers that class; completeness must never escape the declared class.

**Why it matters.** R4.2 was formally sophisticated but economically searched only a tiny atomic family. The same mistake must not recur behind a new API.

**Known.** The theory supplies grammar-recursive construction and honest branch-and-bound semantics. General unrestricted compact search may be exponential/hard.

**Attack surface.** Random small-grammar exhaustive oracle comparison, repeated SUM/shared ancestors, compound PRODUCT descendants with useless parents, recurrent delayed state, tied value slots, direct-vs-factorized physical realizations.

**New failed completeness shortcut.** XVII.15 proves that a bounded PRODUCT
count and final range do not make the variable-parent native class closed,
even with a finite local coefficient alphabet and bounded activations.
Growing SUM chains approach a selector task whose exact PRODUCT minimum is
larger. Closure and positive loss margins must therefore be established for
the actual complete resource class. XVII.16 now solves given one-PRODUCT
coefficient closure through a directed graph criterion and gives a full
mass/finite-cap conditional closure lift. Efficient existential search over
alternative lifts, multi-PRODUCT closure and explicit margins under complete
finite construction budgets remain open. Coefficient rejection cannot be
substituted for rejection of every observable representation. XVII.17 resolves
that existential lift for scalar masses zero at antipodal cube vertices:
observable margins select a unique coefficient-closure member. The three-input
case has a complete rational-table decision over real coefficients; all its
positive cut masses lie in one-PRODUCT closure. Arbitrary-dimensional exact
algebraic search, other zero patterns, general conditional scales and multiple
PRODUCTs remain open. The four-input two-XOR task now has an explicit robust
one-versus-two PRODUCT gap at cap four, but its sharp loss/range frontier is
unsolved: the proved CE lower bound is 1/2000000 while a checked one-PRODUCT
upper witness has excess about 0.00889241. Rational target data can require
irrational exact factors, so real
expressivity and finite-encoding candidate completeness must stay distinct.
XVII.18 further falsifies transfer of exact **support** complexity to mass
limits: two nested PRODUCTs approach a pattern that needs three exactly.
The zero-face argument gives exact minimum m for m independent XOR masses,
but their general approximation minimum and the new counterexample's full
conditional exact minimum remain open. With SUM count S and positive local
coefficient floor mu, an explicit mass margin min(gamma,mu^(S 2^P)) is proved;
removing those resource assumptions requires a separate closure argument.
XVII.19 now supplies that exact exponent/linear characterization and a sound
certificate search for fixed-PRODUCT support limits. Integer exponent vectors
accept; complete Farkas trees reject; work or exact-reconstruction failures
remain UNRESOLVED. It also characterizes full fixed-PRODUCT static mass limits
by coefficient paths a*epsilon^w. Efficient exponent search, prescribed-value
leading-coefficient solving, general typed/multiple-head implementations and
complete-resource integration remain open. Enumeration of attainable finite
Boolean supports remains falsified as a complete limit-support oracle.

For three-bit odd parity, a stored independently checked rejection tree now
proves mass distance >=1/18432 for every at-most-two-PRODUCT graph, and three
PRODUCTs attain the exact scalar mass. At noise 1/4 and final cap four, the
full at-most-two conditional class has CE gap >=1/86973087744. The existing
four-PRODUCT Bayes witness remains sufficient. Whether three PRODUCTs reach
conditional Bayes closure at that cap, and the sharp intervening loss/range
phases, remain open; scalar output exactness does not settle shared heads.

## 3. End-to-end reference↔AMP self-Compiler bridge

**Exact statement.** After reference implementation closure, demonstrate that the actual target mixed-precision learner/Compiler path satisfies the registered event-level relation for deployed and candidate trajectories, including structural boundary/install.

**Why it matters.** Float64 rescoring of an AMP-generated endpoint is not the theorem. The physical path itself must instantiate the reference state transition relation.

**Known.** The theory and historical gates define the obligation. Historical R5/R4 physical kernels showed why a numerically uncertified optimization path cannot be counted as an available FP realization.

**Exact-arithmetic scope counterexample.** The selector audit in XVII.15 has
a CPU float64 path that appears exactly realizable with one PRODUCT, while
the exact rational/native class requires two. Rounded equality can validate
neither a different arithmetic class nor its structural completion claim.
This is a theorem-audit counterexample, not an executed Runtime/AMP bridge test.

**Blocked by.** Problem 1.

## 4. Real next-token structural emergence under the frozen graph-only claim

**Exact statement.** Once the Compiler is certified, test whether ordinary next-token loss plus declared hard deployment resources causes the exact/epsilon-optimal target-program set to force useful semantic structure (e.g. sharing/PRODUCT/provenance distinctions) when all non-graph coordinates are matched.

**Why it matters.** This is one of FP's core science questions: does useful graph/block structure emerge rather than being supplied?

**Known.** Trial 1C falsified raw-width-as-solution; historical native blocks remained behind strong dense/GRU-style baselines; R4.2 failed to instantiate the grammar. Foundation R4 now gives a falsifiable definition of “forced structure.”

**Do not run yet.** Problems 1–3 must close first.

## 5. Native FP block scaling from scratch

**Exact statement.** Determine whether a native FP block, without hidden non-FP architectural shortcuts, can train from scratch on ordinary next-token modeling and approach strong modern baselines under matched parameters/compute/resources.

**Why it matters.** Expressivity alone is insufficient; FP needs a competitive reachable learner.

**Known failed direction.** Increasing raw K within coarse cells did not close the gap. Symmetric duplicated alternatives collapse. Do not add activation-repulsion just to separate them.

**Promising attack surface after Compiler closure.** Let resource-bounded positive program structure/provenance distinctions compete endogenously; use response/operator acquisition only as legal proposal/certificate machinery.

## 6. Practical acquisition regimes under passive language-model data

**Exact statement.** Characterize when the interaction/provenance structures useful for language modeling can be acquired efficiently under the **actually legal passive/teacher-forced information interface**, without assuming arbitrary counterfactual subset interventions.

**Why it matters.** v162 shows finite-amplitude subset probes can destroy the local derivative wall, but next-token training generally does not grant arbitrary interventions.

**Known.** Low-rank two-sided operator access and low-overlap hidden-hypergraph interfaces have tractable subclasses; arbitrary point-query/frontier and general hidden hypergraph families have hard lower bounds.

**Falsification target.** Exhibit a realistic required FP structure family whose passive legal transcript is non-identifying even with unlimited compute; that would prove the corresponding emergence claim needs a richer declared information contract, not a new architecture primitive.

## 7. Extend the sharp normalized-SUM structural envelope

**Solved base case.** `FP_THEORY.md` XVII.1 gives the complete static weighted
2x2 loss envelope and a one-PRODUCT noisy-XOR witness. Normalization makes the
SUM-only control strictly stronger than unigram. The result extends to arbitrary
unary token coefficients under block-factorized hidden-group sampling.

**Open statement.** Characterize the corresponding envelope for multi-input
passive tasks, non-factorizing sampling, and finite physical coefficient/range
constraints, then connect a strict separation to registered acquisition and
constructive value/build/install paths. An unattained continuous infimum is a
sound optimistic control, not an installable optimizer endpoint.

**Former all-dimension conjecture: CLOSED.** XVII.12 proves
`inf L=log2-2^(1-d)[log2-H(eta)]` for uniform d-bit parity, symmetric noise,
the full unary-SUM family, base `(1,1)` and one final normalization. The proof
uses normalized affine discrepancy and log-ratio oscillation, followed by a
scalar convex loss bound. A native construction has excess <=2/K and range
O(d K^2). This is an unattained infimum for d>=2 and eta<1/2, not a static
coefficient vector or a Runtime completion flag. See
`theory/proofs/UNARY_SUM_PARITY_ENVELOPE.md`. Sharp finite-range versions and
general nonuniform context/target envelopes remain open.

**Finite-range interaction capacity: scoped closure.** XVII.13 exactly reduces
the full unary-SUM parity discrepancy maximum D_d(R) to a two-variable rational
optimization. It proves a sharp asymptotic range law and the exact finite value
D_3(4)=1/40 through a global polynomial certificate. This gives a full-SUM
three-bit CE lower bound and a same-cap PRODUCT comparison with margin >0.1277.
General closed forms for finite D_d(R), sharp bounded CE optima and the actual
acquisition/value/build cost remain open. Maximizing one Fourier coefficient
is not the same optimization as minimizing total CE.

**Finite-range CE exponents: CLOSED.** XVII.14 proves that excess above SUM's
unbounded parity infimum is Theta(R^-1) at fixed positive noise, versus
Theta(R^-1/2) at zero noise. Both include all-class lower bounds and finite
native matching-rate constructions. Exact bounded CE optima, sharp leading
constants, the uniform eta->0/R->infinity crossover and registered value
reachability remain open. The discrepancy resource exponent cannot be
substituted for the task-loss exponent.

**All-dimension degree result, distinct from the SUM envelope.** XVII.7 proves
that the larger family of native mass polynomials with multilinear degree <d
has sharp infimum `H(eta)+2^(1-d)[log2-H(eta)]`. A Fourier moment gives the
all-class lower bound; a finite edge-indicator hierarchy approaches it with
explicit range/error costs. Exact noisy parity requires full degree and at
least `ceil(log2 d)` PRODUCT depth. Intermediate degree/node/physical-budget
phases remain open. Do not mistake this degree family's small Bayes excess
for the now-proved unary-SUM envelope's small unigram gain.

**Failed reduction.** Independent two-dimensional face closures do not decide
multi-input SUM closure, even when every probability threshold cut is also
linearly separable. The three-bit counterexample in XVII.2 has a sharp global
distance 2/15, an exact dual and a matching finite SUM model. A proof must
retain a common mass realization or another justified global invariant; local
ordering or face relaxations cannot silently acquire completion authority.

**Solved provenance/range separation.** XVII.8 gives exact all-dimension range
thresholds on reversed-root noisy parity for unrestricted, reduced-output-degree
and proper-positive-derivation-support programs. At d=3 and odds 3 the thresholds
are 4/12/20, and the latter distinction has a proved loss margin at cap 12.
Thus algebraically low-degree output does not prove low-support positive
provenance is available at the same resource bound. General physical budgets,
registered acquisition/value reachability and sharp node-count phases remain
open; reduced polynomial degree must not be used as their substitute.

**Additional solved expressivity boundary.** One shared PRODUCT realizes every
positive 2x2 conditional table, including multiclass outputs; zero-PRODUCT exact
realizability is a vector-segment intersection condition. The binary four-pool
loss formula does not automatically extend to multiclass vector geometry.
Physical coefficient range, acquisition, and reachable value remain substantive
parts of the problem; exact PRODUCT count alone can have zero loss margin.

**Additional solved decision problem.** For an explicitly known finite rational
positive mass cone, exact realization is a linear feasibility problem and
approximation closure is decided by at most one residual LP per context
(`FP_THEORY.md` XVII.2). Zero-normalizer cells must not be discarded. This
settles membership. XVII.9 now additionally gives arbitrary-accuracy global
loss brackets for this known rational class, including polyhedral coefficient
constraints, with a finite exact-LP termination proof and independently checked
covering trees. This does not provide an efficient closed-form loss envelope,
unknown atom acquisition, exact optimum attainment or physical reachability.
A first nonnegative cone solution alone is still falsified as a closure
certificate by the 3x3 hidden-XOR example.

**Tighter finite-range solver.** XVII.10 supplies a quadratically tight
normalizer-chord relaxation over the full mass cone, with exact log enclosures
and explicitly corrected linear-dual residuals. It reduces the audited cap-four
XOR proof from tens of thousands of nodes to hundreds at substantially higher
accuracy. General search efficiency, useful bounds for unbounded normalizers,
and actual registered-state/physical integration remain open. Neither a
numerical convex optimizer nor an uncorrected dual is a completeness oracle.

**Additional solved finite-range case.** `FP_THEORY.md` XVII.3 gives the sharp
SUM range/error tradeoff for a boundary table and a positive-margin transition
from two required PRODUCTs to one as a final-normalizer cap increases. The
at-most-one-PRODUCT class is unrestricted within the stated native grammar.
General multi-input/multiclass loss envelopes, actual hardware-resource phases,
passive acquisition, and registered value reachability remain open. A cap on
the readout normalizer is not automatically a cap on intermediate activations.

**Shared PRODUCT capacity, scoped closure.** XVII.11 supplies a complete
fixed-mass one-PRODUCT criterion, including the common nonnegative slack that
the necessary sign invariant missed. Its four-label identity-noise target
has true one-PRODUCT minimum range 35/2 versus 15/2 for the sign relaxation;
at range 5 four products are necessary, with a robust all-at-most-three loss
gap. The all-dimension identity task forces at least 2^d scalar PRODUCT nodes
at minimum range. Sharp intermediate two/three-PRODUCT range phases, sharp
counts in higher dimensions, and efficient global loss optimization over the
variable-parent one-PRODUCT class remain open. A fixed-mass normal form is not
a learner/provenance equivalence and does not settle conditional scales.

**Finite information, scoped progress.** XVII.4 supplies exact interval-box
structural certificates, a non-identifying query counterexample, an anytime
passive procedure under an explicit iid law, and robustness of the range-four
two-PRODUCT comparison to a whole target-uncertainty ball. This does not solve
nonstationary language-model acquisition, unknown latent partitions, or fresh
candidate persistence. The next connection is registered value construction:
an expressivity witness and a structural confidence certificate do not prove
that the actual optimizer can reach and install the witness under its budget.

**Registered value, scoped progress.** XVII.5 now gives a genuine finite-step
zero-initialized CE path, including a separate finite-encoded coefficient
implementation, to a strict two-PRODUCT winner at R=4. It also proves a
zero-gradient invariant that prevents a different expressive factorization
from ever activating under the same initializer. General registered value
reachability, graph construction/build/install budgets, fresh persistence,
and the actual AMP bridge remain open; no static coefficient vector may be
substituted for their evidence.

**Fresh persistence, scoped progress.** XVII.6 derives an inverse-gap sufficient
fresh-sample bound for the existing linear e-process under a bounded log-loss
alternative and constructs a finite-encoded candidate satisfying its bias
premise. Exact score enclosures retain validity. This is not a theorem of fast
evidence under arbitrary teacher-forced contexts: the static class gap transfers
only when the complete forecast function is fixed before the fresh context (or
another valid conditional-law argument supplies the gap). A controller selecting
among constant functions after seeing context defeats the naive inference.
Characterizing structural forcing with the complete adaptive controller and
legal causal information remains a research problem; accumulated-wealth
arithmetic, complete resource/install accounting and AMP remain unclosed.
