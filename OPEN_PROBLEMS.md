# FP Open Problems

Only genuinely unresolved problems belong here. Historical problems that were solved or falsified are documented elsewhere.

**Current priority, 2026-09-12:** the scoped joint PRODUCT/SUM/range/precision
law in XVII.31 closes the static resource study. ERC-1 is frozen in
[`EXPERIMENT_RESOURCE_CONTRACT.md`](EXPERIMENT_RESOURCE_CONTRACT.md). Work on
the complete Runtime, actual AMP bridge and then RTX 3090 experiments.
The remaining static special cases and sharp constants below are parked,
not invitations to continue that program. Reopen Foundation only for an
implementation/experiment correctness counterexample to its semantics.

## 1. Close the complete Reference Compiler runtime

**Exact statement.** Implement one complete execution surface that instantiates `FP_THEORY.md` without allowing a caller to bypass claim state, information, value reachability, physical ownership/resources, numerical enclosures, persistence or bridge provenance.

**Why it matters.** The frozen foundation is only useful scientifically if the actual Compiler optimizes the same object. Most historical FP failures came from a correct local theorem being embedded in a smaller/different executable system.

**Known.** An intermediate 2026-09-05 reference implementation had a full module set and passed 24/24 unit tests plus 47/47 gate registry. Subsequent adversarial hardening changed the complete Runtime contract. The final endpoint integration was not re-frozen before persistence moved to GitHub. Historical R4.2/R3 implementations are complete but theoretically superseded.

**Already-failed methods.** Bare certificate booleans, caller-supplied exact uppers, arbitrary query callbacks, caller-built candidate states/object lists, resource totals without ownership, e-wealth reuse across lineages, state/cursor mismatch, partial ref↔AMP bridging, and helper-level tests that do not traverse the complete Runtime.

**Current implementation progress (2026-09-12).** The actual Runtime now
connects typed construction and owned buffers to registered profile replay,
exact ordinary learning, causal source reads and finite-alphabet revealed-data queries.
Audits cover construction/ownership, 960 independent exact gradient vectors,
all 64 short context/target streams with two reference lineages, and the
existing XVII.5 recurrence on 512 deterministic online events. Failed target
events cannot be retried as unread; past evidence retains actual program
ownership after a branch retires. Read the source README and
`docs/REFERENCE_RUNTIME_CONTINUATION.md` before extending this segment.
The XVII.5 profile is now also executed from its original 16 retained labels:
512 paid replay events preserve their IDs, reproduce all 32 updates and
create no new exogenous/fresh events. Complete recurrent/optimizer state is
retained at newborn attachment; failed profiles keep their paid prefix.
Complete finite ordered grammar search now runs through the same endpoint.
Independent enumeration checks nine grammars (14,860 program/class cases);
actual searches cover registered profiles, delayed bindings and a compound
PRODUCT discovery whose shorter prefixes have no gain. The Runtime-issued
proof is scoped to fixed-state empirical CE on registered constructor
endpoints **plus deployed baseline**, with current context and owned
evidence. Read `theory/proofs/ORDERED_NATIVE_REFERENCE_CLASS.md`.

Owned reference persistence now runs on the same ordinary event path:
pre-context admission, paired sealed predictions, continuous learner state,
guarded lower logarithms/wealth and global nonrefundable alpha. It yields
conditional reference evidence under an explicit external stochastic law;
shared fresh observations need separate allocations, not independence.
See `theory/proofs/OWNED_REFERENCE_PERSISTENCE.md` for the exact null and
failure boundary. It grants no AMP or installation authority.

Actual CPU binary64 continuation now runs beside the exact learner through
constructor/profile and every ordinary microphase. Exact rounding checks,
complete raw-bit state and stored-mass normalization establish a scoped
finite-prefix relation; no future/global floating bound is inferred. Read
`theory/proofs/OWNED_FLOAT64_PREFIX.md` before using its evidence. Actual
AMP execution and matched dual persistence remain different obligations.

The CPU four-path persistence obligation now has a direct implementation:
current-domain monotone rounded bounds, separate reference/stored-mass CE
scores and alpha, matching starts and continuous full learners. The explicit
counterexample with reference crossing and identically zero physical gain
excludes copied wealth. See `theory/proofs/PAIRED_CPU_PERSISTENCE.md` and its
endpoint audit. Its result is evidence for a CPU pair, not by itself an
install transaction or actual AMP evidence.

The serialized CPU installation now also executes through the same Runtime.
It checks owned historical class selection separately from current paired
evidence, preserves all actual learner buffers at one complete root/lease
publication, closes searches with retained history, and invalidates old
persistence without alpha refunds. Actual byte/work failures retain their
paid preparation history and permit only a new paid attempt. Independent
lease cases and full 35-/774-member native-class endpoint chains are in
`theory/proofs/OWNED_CPU_INSTALLATION.md` and its audit. This is a fixed
serialized CPython transition, with no current-optimum, crash/concurrency
or full host/device accounting claim.

The remaining work is complete ERC-1 registration, full Compiler decision
authority beyond the scoped reference comparison, paired reference/AMP
persistence and complete error state, actual host/device accounting, target
AMP and target installation, plus explicit mapping of the historical release
obligations to current evidence. Raw revealed train/online access is explicitly
registered; query-only and reporting-only execution are not yet supported.
The new endpoint pass is not a complete release certificate.

**Current physical boundary.** Machine v2 removed unfunded control history
growth. Machine v3 now also closes the raw-input witness at `5055f3e`:
mandatory paid byte windows replace naked rational receipt. Length guards
precede integer creation, partial/failed frames retain every received byte
and a fixed terminal status, and no post-context evidence admission is
possible. All 208 chunkings of a small frame have identical recorded
states at equal prefixes. Read `theory/proofs/OWNED_CONTEXT_INGRESS.md`;
the old raw-value counterexample remains executable from Git.

The follow-up encoding audit also corrected a real identity failure: old
JSON conflated a legal astral source name with explicit surrogate code units,
allowing candidate construction to change the deployed program without
installation. Machine v4 preserves these code points and requires full code
equality before address reuse. Its size plans and streaming writer also remove
the expanded encoding-tree peak before capacity refusal. The old 100,000-edge
case traces about 62 MB despite an 8 KiB packed cap; the revised trace is
about 0.134 MB. Read `theory/proofs/OWNED_ENCODING.md` for exact scopes.

Machine v5 additionally closes public authority after MemoryError. An
executed injected-fault witness at `dfa1583` had allowed next prediction from
a candidate whose learner buffers were already freed. The current failure
marker preserves the prefix without assuming cleanup allocation can succeed.
An actual 64 MiB Windows job refuses the Runtime's registered 128 MiB ingress
window before input, with paid work retained; see
`theory/proofs/HOST_ALLOCATION_FAILURE.md`.

Machine v6 additionally binds the actual Runtime process to registered
private-commitment limits. Its complete process arena is shared by both
roles, with the minimum global/role cap enforced by the kernel. This covers
Python metadata, copies, diagnostics, rational scratch and allocator arenas
in that declared measure; complete-state ownership still comes from the
Runtime/packed ledger. Process-lifetime peak and CPU history cannot be reset
with a new Runtime or nested job. An actual late-fence counterexample and
35-program search/persistence/install under 64 MiB are in
`theory/proofs/BOUND_HOST_RUNTIME.md`.

The remaining resource closure is complete ERC-1 run/policy registration,
production supervision/publication and error ownership across terminated
runs, external/shared platform and device resources, other resource limits,
and release-gate mapping. A sampled host observation is not full physical
state or run authority, and the unbound reference mode proves no host cap.
Static special cases stay parked; after reference closure the next target
is actual AMP and then RTX 3090.

**Sufficient falsification of the current foundation.** A minimal program that is legal under `FP_THEORY.md` but cannot be represented/considered by any implementation conforming to the Reference Compiler contract **unless a new semantic model primitive is added**. Slow search or `UNRESOLVED` does not falsify the foundation.

## 2. Prove/test implementation-level completeness of native candidate construction for each declared decision class

**Exact statement.** For every `CERTIFIED_COMPLETE` decision, the implementation must expose the explicit finite/effective candidate class and prove that its native construction/search representation covers that class; completeness must never escape the declared class.

**Why it matters.** R4.2 was formally sophisticated but economically searched only a tiny atomic family. The same mistake must not recur behind a new API.

**Known.** The theory supplies grammar-recursive construction and honest branch-and-bound semantics. General unrestricted compact search may be exponential/hard.

**Closed finite implementation slice.** The checked ordered DFS covers all
programs under the five explicitly declared native caps and fixed finite
semantic rules. It retains all slots/edges/roots/binding orders and never
rejects descendants from a poor parent score. Every emitted program runs
the registered initializer/profile; the endpoint is rescored before the
one fixed empirical-maximum proof. This is proved at the implementation
level and checked against an independent exhaustive oracle. A failed
range/value/comparison remains unresolved. More efficient solving may be
needed, but do not expand static special cases to obscure an unfinished
complete Runtime or extrapolate this fixed constructor to every value path.

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
full at-most-two conditional class has CE gap >=1/86973087744. XVII.20 now
closes the shared three-versus-four boundary: disjoint excess targets permit
a last-PRODUCT comparison, transferring scalar approximation exclusions to
joint graphs. Four are necessary even for conditional closure at minimum
cap 1/eta for every noise eta in (0,1/2); at eta=1/4 all at-most-three graphs
have CE gap >=1/135895449600. Sharp loss constants, higher-bit scalar/joint
counts and larger-cap phases remain open. At larger caps the conditional
excess supports need not be disjoint, so this argument cannot be reused
without retaining the alternative normalizers.

XVII.25 now supplies the larger-range endpoint for three-bit parity: exact
and approximation PRODUCT minimum two for R>=(r+1)*(r^2+r-1),
r=(1-eta)/eta. At noise 1/4 this is cap 44. The range is proved optimal
only for the explicit XOR/PRODUCT feature bank. The full two-PRODUCT
threshold, possible intermediate three-PRODUCT phases and sharp losses
remain open; the endpoint count is no longer unresolved.

XVII.21 adds a general necessary condition for mass limits: every positive
point has a positive source intersection using at most P+1 distinct sources.
A quantitative retained-monomial proof closes exact and approximation counts
for every binary coordinate-face mass: codimension m requires m-1 PRODUCTs.
It does not decide general support closure; the two-PRODUCT parity rejection
already passes this local condition. Sharp scalar approximation margins and
stronger invariants relating different positive points remain open.

XVII.22 now closes the full shared singleton approximation count: N+d-2,
N=2^d, both for excess masses and the identity-noise conditional task at
minimum cap N+1. At d=3 exact support/mass/conditional minimum is twelve,
whereas approximation minimum is nine. Exact singleton nodes may be made
terminal for a complete finite support search; nearly singleton nodes cannot,
because legal descendants can amplify their positive tails. With the finite
local alphabet {1/2,1,2}, d=3 and PRODUCT budgets nine through eleven, SUM
accuracy cost is Theta(log(1/error)). Sharp constants, higher-dimensional
exact minima and larger-cap phases remain open. Bounded intermediate maxima
do not remove underflow or give a reference/AMP bridge.

XVII.23 resolves the immediate cap-slack question: any positive slack above
N+1 admits exact prediction with N+d-2 PRODUCTs. For d=3, exact minimum is
nine on 9<R<243/26 and twelve at R=9. The at-most-eight probability lower
bound on R=9+h is (9-26h)/(45*(9+h)); the endpoint is not claimed sharp.
Joint SUM cost for fixed PRODUCT budgets nine through eleven is
Theta(log(1/(h+delta))) as cap slack and probability tolerance jointly vanish.
Transitions to eight or fewer PRODUCTs, sharp one-PRODUCT singleton distance
and sharp SUM constants remain open; a small slack cannot be silently treated
as the exact minimum-cap support contract.

XVII.24 resolves the unrestricted-range universal PRODUCT count: 2^d-d-1
for all strictly positive finite conditional tables, both exactly and in
approximation. A static rank obstruction matches a constructive positive
row scaling in a fixed monomial bank. For three-bit identity noise, four
PRODUCTs attain exact prediction at cap 108 and at most three has a positive
gap at every cap. The exact four-PRODUCT range threshold remains open:
108 is optimal for the fixed xy,xz,yz,xyz bank only. Thresholds between the
near-nine nine-PRODUCT phase and this four-PRODUCT phase, sharp universality
counts for fixed smaller label alphabets, and sharp total resource costs remain
open. Unbounded-range universality neither identifies unknown target values
nor supplies a registered learning/physical/numerical path.

XVII.26 resolves the alphabet-dependent asymptotic order: both exact and
approximate universality cost Theta(min(2^d,sqrt(2^d*k))) PRODUCTs for k>=2.
The complete-class parameter lower bound survives prediction limits and
matches a positive block construction in order. XVII.27 sharpens the frozen
bank universal minimum to 2^d-d-1 even for binary labels, so the smaller budget
forces target-dependent feature values, even though its skeleton can remain
fixed. Sharp small-(d,k) counts remain open: binary three-bit universality
currently needs a budget between two and three. Exact/approximation count
differences for fixed alphabets, optimal range/SUM/bit costs and registered
acquisition/value paths remain unresolved. The number of PRODUCTs alone
does not price the retained full target coefficient table.

XVII.27 completely decides conditional universality of a known finite
frozen positive feature bank at unrestricted range via partial colorings
of its supports. Exact and approximation universality coincide for that
decision, with explicit positive-margin counterexamples on rejection.
Efficient searches for larger banks, single-target feasibility under finite
range/SUM/bit budgets, variable-parent universality and registered feature
acquisition remain open. Full numerical span, full-domain-only color checks
and finite positive validation suites are all insufficient substitutes for
the criterion. Numerical feature magnitudes cannot be discarded for range
or target-specific claims merely because universality depends only on support.

XVII.28 now extends the full coefficient-path characterization to arbitrary
finite-head conditional limits, including diverging normalizers. At a finite
cap, a bounded monomial mass lift and one final positive excess contraction
give complete closure without extra cap slack or PRODUCTs. Pure monomial
paths required to remain within the cap are an incomplete search class:
the cap-nine decoder rejects every such path with at most eleven PRODUCTs
but has nine-PRODUCT constrained closure. The remaining generic solver
problem is finite leading-pattern search together with positive-amplitude
and normalizer feasibility, not the existence of a path characterization.
The new exact audit verifies rational witnesses; it supplies neither a
generic complete amplitude solver nor a complete rejection search.

The same result proves two resource reductions when SUM work is free:
hidden activations can be rescaled into any bound already met by sources
and final excesses, and downward dyadic rounding preserves prediction
closure, PRODUCT count, normalizer caps and common activation caps using
local weights {1/2,1,2}. Sharp SUM/encoding/precision costs, lower bounds on
nonzero numerical values, complete-resource closure and registered value
paths remain open. A constant support pattern for variable feature values
does not restore frozen-bank completeness: the positive shifted two-bit
banks are jointly exactly universal although each fixed bank fails.

XVII.29 closes the general fixed-PRODUCT SUM accuracy **order** at finite
normalizer cap. Every closure point admits O(log(1/delta)) local-{1/2,1,2}
SUM construction. For fixed algebraic sources and targets, a nonexact local
closure point necessarily costs Theta(log(1/delta)), also logarithmic in
inverse CE tolerance. The full asymptotic alternatives are positive gap,
eventually minimum exact SUM count, or this logarithmic growth. Generic
fixed-P classification into those alternatives, efficient amplitude/value acquisition
and sharp target-dependent constants remain open. Exact realization over
real coefficients is insufficient to decide the exact local-alphabet branch:
Q=(5/8,3/8) at cap 8/3 already separates them with zero PRODUCTs.

Sharp **joint** SUM/PRODUCT/precision costs remain unresolved. A positive
geometric-product construction for that same task attains error exponential
in -2^n with 2n-1 PRODUCTs and 2n+3 SUMs, retaining cap 8/3 and activation
cap one. Its direct significand has order 2^n bits. The separate fixed-P
rate therefore cannot be extrapolated while P grows. Arbitrary transcendental
data can violate the logarithmic lower along accuracy subsequences, and
unpriced arity plus unbounded range can hide all growth outside SUM node
count. Complete physical/numerical/registered-value costs remain open.

XVII.30 closes the rational binary-domain **unrestricted-node** branch
classification and total accuracy order. With local {1/2,1,2} coefficients,
R_0=max_x 1/min_j Q_(x,j) is the exact closure threshold. Above R_0 finite
exactness is always possible; at R_0 it holds iff every critical forced mass
R_0*Q_(x,j) is dyadic. Every nonattained boundary costs
Theta(log log(1/error)) in total SUM-plus-PRODUCT nodes. Both bounds retain
all normalizers and actual coefficient-application PRODUCTs.

The sharp Pareto curve for separate S and P budgets, minimum finite exact
graph size, constants/uniform dependence on the full target encoding, other
source/number classes, and complete physical/numerical/value paths remain
open. The scoped classifier allows arbitrary finite P,S and must not answer
the earlier fixed-P decisions: cap-nine three-bit identity remains nonexact
at P=9 even though its unrestricted exact branch has a 12-node witness.

The joint static resource **orders** are no longer open in the rational
binary nondyadic-cap class: XVII.31 gives necessary S*2^P and direct-precision
b bounds logarithmic in 1/(h+delta), and a matching separate-budget native
upper envelope up to fixed overheads/precision constants. It also gives
node optimum log2(log2(1/(h+delta)))+O(1), and simultaneously optimal
node/edge/direct-bit orders. Positive tail repair gives exact prediction at
positive cap slack. The remaining exact small-P phases, bounded-arity leading
constants and alternative encoding/bit-time questions do not block that
scoped resource specification. Runtime accounting and the actual AMP bridge
remain open; static exact arithmetic is not their certificate.

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
gap. XVII.21 and XVII.22 give exact all-dimension identity approximation
minimum 2^d+d-2 at minimum range. At d=3 the exact minimum is twelve and
the approximation minimum nine; XVII.23 improves the all-at-most-eight CE
gap to 1/8100. XVII.24 supplies the other endpoint: exactly four PRODUCTs
for the three-bit task at R>=108, and sharp worst-case conditional universality
count 2^d-d-1 with unbounded range. Intermediate range phases, exact counts
at minimum range in higher dimensions, and efficient global loss optimization over the
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
