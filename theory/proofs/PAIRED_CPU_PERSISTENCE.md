# Four continuous CPU learners and two same-path persistence claims

Status: **PROVED under the registered arithmetic, range, filtration and
stochastic assumptions; IMPLEMENTED with scoped endpoint audits.** This
instantiates Foundation XIV--XV for the checked CPU binary64 leg of the
reference protocol. It is not a target AMP bridge, an installation theorem,
or complete Runtime/ERC-1 resource closure. Foundation and ERC-1 stay frozen.

Normative sources: [FP_THEORY.md XIV--XVI](../../FP_THEORY.md) and
[ERC-1 sections 2--5](../../EXPERIMENT_RESOURCE_CONTRACT.md).
[OWNED_FLOAT64_PREFIX.md](OWNED_FLOAT64_PREFIX.md) establishes the separately
executed and checked numerical prefixes.
[OWNED_REFERENCE_PERSISTENCE.md](OWNED_REFERENCE_PERSISTENCE.md) proves the
existing stopped-epoch mean-null and downward-wealth construction. This
document supplies the missing current-domain premise for binary64 and
binds two applications of that statistical result to the four actual paths.

## 1. Observed numerical agreement is insufficient

An observed-context bridge checks a particular forecast. A persistence null
declared before that context arrives concerns the conditional law over all
its possible outcomes. In particular, discarding contexts whose arithmetic
or range check failed and conditioning only on successes changes the null.
The existing stopped extension needs a bounded mathematical current forecast
even at the failing attempt. It never needs an unverified learner successor.

For the registered deterministic binary64 forward, a current whole-domain
bound follows directly from positive SUM/PRODUCT and monotone scalar
rounding. No architecture case or new semantic action is necessary.

## 2. A rounded forward bound over the declared domain

Fix the actual raw binary64 parameter tuple theta. Its entries and all native
sources/delayed reads are nonnegative. The registered arithmetic is ordered,
separate binary64 multiplication/addition with nearest/ties-even rounding,
gradual underflow and explicit source/base casts. Nonfinite results fail.
The exact scalar implementation is in
[binary_arithmetic.py](../../src/reference_compiler/fp_reference/binary_arithmetic.py).

Nearest rounding on an ordered representable grid is nondecreasing: its
nearest-neighbor cells occur in that same order; a midpoint tie changes
only the ownership of their common boundary. Composition with nonnegative
addition or multiplication therefore remains nondecreasing in each input.

For a source box, cast each source's declared upper bound. For a complete
finite source domain, perform the same proof once per declared source row.
For a delayed state capped by u, the rounded value RN(u) encloses every
representable delayed value at most u. This also holds when RN(u)<u:
there is no representable number between RN(u) and u in that case. Evaluating
the positive graph at these upper coordinates bounds every stored activation
and mass. Sharing, repeated SUM edges and square incidences preserve the
argument; their actual ordered work is still performed and counted.

Let beta_y=RN(b_y), and let m_y denote a stored finite mass. Require
beta_y>0. Since RN(beta_y+v)>=beta_y for representable beta_y and v>=0,

\[
0<\beta_y\le m_y\le m_y^{upper}.
\]

The proof independently checks

\[
S=\sum_y m_y\le\sum_y m_y^{upper}\le R,
\qquad t_f\le t_f^{upper}\le R,
\]

where S is an **exact sum of decoded stored masses** and t_f is the actual
ordered rounded normalizer. Substituting t_f for S would be unsound.
Every activation upper and every delayed-update body upper must also lie
within its declared cap. The complete actual current delayed queues must
already satisfy that invariant. A delayed shift then preserves the old
tail coordinates and appends a proved bounded body.

The mathematical physical probability is

\[
p_y^m=m_y/S.
\]

The actual rounded division output is checked separately. Every positive
ordered partial sum is at least each of its representable positive addends,
so m_y<=t_f. Monotonicity of final division/rounding gives

\[
0<\operatorname{RN}(\beta_y/t_f^{upper})
\le p_{out,y}=\operatorname{RN}(m_y/t_f)\le1.
\]

The strict lower inequality is checked; a potentially zero rounded division
is UNRESOLVED even when the mathematical mass probability is positive.
This result establishes definition/range of the current finite predictor
on the entire declared domain. It does **not** establish its numerical
closeness to reference on every context. The latter is still checked only
on the actual executed context before scoring and at all learner microphases.

[float64_range.py](../../src/reference_compiler/fp_reference/float64_range.py)
implements this proof computation. An insufficient box bound, overflow,
underflow, or unaffordable exact comparison is UNRESOLVED. A source box may
overapproximate a constrained input family; a sufficient bound is not a
complete feasibility decision. These passive records are bound to current
theta and the immutable source/state/backend contract only by Runtime.

## 3. The two loss statistics and their bounds

The physical score declaration is `binary64-stored-mass`: normalized CE of
the actual stored masses, not the log of possibly nonnormalized displayed
division outputs. That choice is immutable in `PersistenceRule.score_path`.
The existing `exact-reference` declaration keeps its original meaning.
Runtime seals both paths of both lineages before accepting the unique
target, and then computes

\[
g_t^r=\log(p^r_{C,t}(y_t)/p^r_{D,t}(y_t)),\qquad
g_t^f=\log(p^m_{C,t}(y_t)/p^m_{D,t}(y_t)).
\]

No expression mixes the reference candidate with the finite comparator,
and neither score is computed from a post-target optimizer endpoint.
Actual rounded masses are decoded, summed and normalized with guarded exact
arithmetic; logarithms use the existing sound rational enclosure.

Put beta_sum=sum_y beta_y. The same positive-base argument as for reference
gives

\[
\beta_y/R\le p_y^m\le(R-\beta_{sum}+\beta_y)/R,
\qquad K_f=\max_y(R-\beta_{sum}+\beta_y)/\beta_y.
\]

Thus |g_t^f|<=log K_f. Reference uses K_r with the original exact base b.
Each identity's preregistered rational B must enclose its own log K. It
cannot copy another path's bound when base casting changed its value.
Global bounds do not authorize clipping an out-of-range true gain.

Before each live context, the current finite parameters retain their proved
domain bound. An ordinary optimizer change triggers a fresh paid bound
before that successor can extend the finite persistence identity. If theta
bits are unchanged, the same box invariant remains valid as queues evolve.
Even after the first crossing, the complete learners and their current
domain invariants continue to be tracked. A failed ordinary transition,
retirement, or failed new-domain proof removes current authority while
retaining the historical crossing and spent alpha.

## 4. Stopped nulls, separate wealth and one global error ledger

The complete pre-event filtration includes all four learner states,
Compiler/profile/query operations, revealed observations and all resource,
error and randomness coordinates. It is never reduced to the history of
one path. Both admissions occur before the first fresh context. Epoch
length H and all numerical/statistical choices are fixed in the declaration.

For each path a, define the previously registered stopped statistic

\[
Y^{a,*}_j=H^{-1}\sum_{t\in j} I^a_t g^a_t.
\]

Here I is predictable liveness immediately before the context. The current
whole-domain forecast defines the gain at the failing attempt; subsequent
slots are zero. No failed post-target learner is continued in the analysis.
The null is `E[Y^{a,*}_j | actual pre-epoch history]<=0`, not an expectation
conditioned on successful computation. For finite masses its fixed null ID
is `bounded-pre-context-stopped-binary64-mass-epoch-mean-v1`; the reference
null ID is unchanged. A per-live-event conditional mean-null suffices by
the tower property. An uninterrupted epoch-null alone need not suffice.

Apply the existing exact lower-log and downward-grid wealth construction
separately to each path. Under its own null, that path's killed-at-failure
and stopped-at-first-crossing extension is a nonnegative supermartingale.
The implementation preserves historical wealth as data, but a failed
identity cannot reactivate it as statistical authority. Alpha is paid
before fallible admission work and is never refunded after failure,
cancellation, rebuilding or retirement.

Each path receives a separate allocation from the same immutable global
budget. The sum of all reference and finite allocations is bounded by
alpha_total. Conditional Ville plus a union bound therefore controls the
probability of any false path crossing by alpha_total, even when identities
share every fresh event and their statistics are perfectly dependent.
No independence or extra freshness is created by scoring a target twice.
Pairing two current crossings needs no additional alpha allocation: a false
paired assertion implies at least one false individual assertion already
covered by that union bound. This implementation does not exploit a tighter
intersection-union allocation; no such optimization is needed for validity.

`paired_persistence_result` reads owned identity IDs. It requires the same
base/candidate programs and lineages, the same four complete starting states,
start cursor and epoch/horizon schedule. Both independent statistics must
have crossed and both current trajectories must still match. Crossings may
occur at different epochs; each statistic stops at its first crossing while
its learner paths continue. Wrong-path IDs, different starts, detached
endpoints and caller-written result objects cannot supply this relation.

`PAIRED_CPU_CROSSED` concerns these two conditional historical mean-null
claims on continuous CPU learners. It is not a future-improvement claim,
a complete search decision, a target AMP result or install authorization.

## 5. A reference crossing with exactly zero physical gain

Let delta=2^-54. Use binary base one, cap R=2+delta, an incumbent with zero
excess and a candidate with one registered SUM coefficient delta multiplying
the first unary source. Fix ordinary learning rate zero, update unit two,
and the same future context activating that source with target zero.
Both paths still execute predictions, gradients, accumulation and commits.

Reference masses are (1+delta,1), so the target likelihood ratio versus the
incumbent is `2*(1+delta)/(2+delta)>1`. Binary64 stores delta exactly but
rounds `1+delta` to 1. Its masses are exactly (1,1), and its gain is exactly
zero on every event. The finite mean-null therefore holds under every law
for which these forecasts apply. Numerical closeness alone cannot transfer
the positive reference evidence to that physical null.

With B=delta, bet=3/4, alpha=1/4 per path, 12 logarithm terms and a 16-bit
wealth grid, the actual Runtime reference path crosses at event 5 with
lower wealth `322095/65536`. The finite wealth stays exactly one through
the registered eight-event horizon. The paired result is UNRESOLVED.
This is a concrete execution counterexample to copied reference wealth,
even with an extremely small probability discrepancy. It adds no static
architecture family or Foundation exception.

## 6. Audit and remaining boundaries

Run `python -B scripts/audit_paired_cpu_persistence.py --write`.
The audit includes independent direct-float comparisons for 16 source boxes
and 400 contexts, 125 delayed-box states, two separately scored learning
paths over 12 events and six range-recertified commits, the counterexample
above, and all 32 five-event fair-label paths. Those null trees execute
160 actual ordinary events and check 62 exact conditional wealth inequalities;
each path crosses with probability 1/32 under its declared alpha 1/3.

It also exercises current-safe/global-unsafe contexts, a rounded optimizer
that violates cap 21/10 only on another context, actual integer/work/byte
limits, a failed first-crossing state allocation, failure after two crossings,
wrong-path/start IDs, four paid profile events from two old observations,
and fresh identity/alpha behavior after rebuilding. Minimal evidence is
[`FP_PAIRED_CPU_PERSISTENCE_AUDIT.json`](../../evidence/minimal/FP_PAIRED_CPU_PERSISTENCE_AUDIT.json).

This does not infer the external producer's law from an audit tape. The
packed-payload machine still omits complete host heap, interpreter temporaries,
bit-time and target-device accounting; terminal diagnostics retain that
explicit limitation. Numerical and statistical evidence cannot replace
complete ERC-1 registration, an atomic self-Compiler transaction or actual
target AMP execution. Those remain the route to RTX 3090 science.
