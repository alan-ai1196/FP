# Owned reference persistence with bounded lower wealth

Status: **PROVED under the explicit stochastic assumption and execution
invariants below.** This is an implementation-level derivation of the existing
Foundation persistence rule, not a new architecture action or an implementation
freeze. Actual Runtime enforcement and endpoint evidence must be audited
separately. The probability law remains an external assumption; executing a
test does not establish that its observation producer obeys that assumption.

Normative sources are [FP_THEORY.md XIV--XVI](../../FP_THEORY.md), especially
the complete global filtration, lineage-specific e-process, matched
reference/AMP paths and atomic install boundary, and
[ERC-1 sections 2--5](../../EXPERIMENT_RESOURCE_CONTRACT.md).
[LOG_LOSS_PERSISTENCE_COST.md](LOG_LOSS_PERSISTENCE_COST.md) proves the separate
XVII.6 power result. The present bounded-wealth implementation **does not
inherit its power constants**.

## 1. Native base and normalizer cap imply a gain bound

Fix the shared positive base vector `b=(b_1,...,b_k)` and write
`b_sum=sum_y b_y`. For each reference forecast, positive native evaluation
gives masses `M_y>=b_y`, total `T=sum_y M_y<=R`, and `p_y=M_y/T`.
A feasible forecast necessarily has `R>=b_sum`. For every label,

\[
\frac{b_y}{R}\le p_y
=1-\frac{\sum_{z\ne y}M_z}{T}
\le 1-\frac{\sum_{z\ne y}b_z}{R}
=\frac{R-b_{sum}+b_y}{R}.
\]

Both candidate and deployed reference forecasts therefore obey

\[
\frac1{K_y}\le\frac{p_{C,y}}{p_{D,y}}\le K_y,
\qquad
K_y=\frac{R-b_{sum}+b_y}{b_y},
\qquad K=\max_y K_y\ge1.
\]

Thus `|log(p_C,y/p_D,y)|<=log K`. A preregistered rational `B>0`
is sufficient when a sound logarithm enclosure proves `log K<=B`.
Failure to establish this comparison is `UNRESOLVED`; it is not permission
to weaken the bound after observing a target. If `R=b_sum`, every forecast
is the normalized base, so the exact gain is zero and any positive B works.
For binary base one and cap four, the same formula gives `K=3`.

This derivation covers every range-safe native graph with the declared base
and cap. It does not restrict PRODUCT count, introduce a forecast menu, or
require a new static architecture case. Its premise must remain true at every
score, including after optimizer commits and recurrent updates. A violated
or unproved range invariant cannot be repaired by clipping the true gain.

For example, a random gain equal to `1` with probability `9/10` and `-9`
with probability `1/10` has mean zero. Clipping it into `[-1,1]` produces
mean `4/5`, so the original mean-null no longer authorizes that statistic.

## 2. The actual filtration and the admitted epoch

Let F contain the complete revealed Runtime history: inputs and targets,
learner and Compiler states and actions, source reads, query/profile results,
resource and error ledgers, and every RNG outcome used so far. For an identity
i, admission occurs at a shared complete optimizer boundary before its first
incoming context. The owned admission record binds:

- the immutable claim and rule, external stochastic-law assumption and Runtime;
- the deployed and candidate lineage, program and initializer/profile provenance;
- both complete starting learner states and their common ordinary cursor;
- the epoch length H, maximum number of epochs, B, betting fraction lambda,
  alpha allocation and numerical implementation/precision;
- the physical workspace and evidence owners.

For epoch j, let `F_(i,j-1)` be the actual complete filtration immediately
before its first context arrives. H, B and lambda must be measurable there.
The implemented `PersistenceRule` fixes these quantities for an identity;
the general theorem also permits registered past-dependent predictable
choices. Epoch length is independent of the learner's optimizer clock: H=1
with an update unit of two is supported. Crossing after such an epoch can
leave a partial optimizer accumulator. It is reference evidence at that
actual state, not an optimizer-boundary or installation authorization.

On each of the H ordinary events, Runtime seals both reference forecasts
before accepting that event's target. It derives the score from those owned
predictions and the unique actual target. Define the epoch gain

\[
Y_{i,j}=\frac1H\sum_{t\in\text{epoch }j}
\log\frac{p^{ref}_{C,t}(y_t)}{p^{ref}_{D,t}(y_t)}.
\]

The base and candidate may learn inside the epoch through their registered
ordinary transitions. They remain the same continuous lineages. A frozen
scoring schedule, if used, must itself be registered; no retrospective
freezing, reinitialization or endpoint substitution is implied here.
The pointwise bound above gives `|Y_(i,j)|<=B`.

For a full registered continuation the epoch-null formula is

\[
\mathbb E[Y_{i,j}\mid F_{i,j-1}]\le0
\quad\text{for every epoch in the declared stochastic claim.}
\]

Failure branches require the explicit total statistic below. The null is
relative to the pre-epoch filtration, never conditioned on computation
succeeding. A statistic defined only on selected successful branches does
not state the required hypothesis. Merely unread observations in a
deterministic corpus do not establish it. The typed `StochasticStreamLaw` in
[data_usage.py](../../src/reference_compiler/fp_reference/data_usage.py)
records an external stochastic-process assumption; it does not inspect a
finite sample and certify its probability law. An exposed future tape or
seed cannot silently be omitted from F to manufacture fresh randomness.

This null and its rejection concern the admitted continuous trajectory. They
do not claim a population optimum over all graphs, or improvement on every
possible future continuation. The stronger iid-context and small-bias
premises needed for XVII.6 power are separate. In particular, choosing an
entire comparator function after seeing the current context does not preserve
the static-gap-to-conditional-power argument in that section.

### 2.1. A bounded stopped extension uses only valid current forecasts

Runtime need not execute, or prove a range bound for, learner states beyond
a failure. The following analysis convention gives the epoch a total
bounded statistic without such a continuation. Fix the convention before
using its null.

For each of its H scheduled slots, let I_t indicate that the identity is
still live immediately before that slot's context. This indicator is
pre-context measurable. On a live slot, the current pair of complete
reference states and its whole-domain range evidence define exact
mathematical forecast functions and the bounded gain g_t for the next
exogenous context/target. This current g_t is defined even if evaluating or
retaining that event subsequently exhausts its numerical/resource budget.
It is an analysis variable, not a free executed score or an evidence record.
The declared branch-invariant exogenous law supplies the current
context/target law; no unobserved value enters Runtime's actual wealth.
After the identity halts, set all remaining slot gains to zero. Define

\[
Y^*_{i,j}=\frac1H\sum_{t\in\text{epoch }j} I_t g_t.
\]

This uses the already range-safe current forecast at the failing attempt,
then zero. It never advances an unverified post-failure learner. Therefore
`|Y^*|<=B` on all branches and `Y^*=Y` on every completed epoch. A concrete
sufficient direct null for the implementation is

\[
\boxed{\mathbb E[Y^*_{i,j}\mid F_{i,j-1}]\le0.}
\]

`PersistenceRule.null_id` fixes this proposition as
`bounded-pre-context-stopped-reference-epoch-mean-v1`. The immutable run
identity and retained evidence include it. It is not a caller-selectable
null or a retrospective interpretation of successful outcomes.

An optional sufficient premise is the per-event conditional null
`E[g_t | actual live pre-context history]<=0`. Its conditioning includes
the current registered pair of whole forecast functions, complete state
and all past observations. Because I_t is predictable, the tower property
gives the boxed stopped-epoch null. Only current live forecast functions
need the bound; no hypothetical out-of-range successor after a failure is
introduced. Runtime enforces causal timing and checks current ranges, but
does not establish this stochastic null from data.

These premises must not be silently substituted for an **uninterrupted**
H-event mean-null. The two epoch statistics can differ. For example, the
fixed two-event gain sequence `(1,-1)` has uninterrupted mean zero; stopping
after its first event and filling the remainder with zero gives mean `1/2`.
If a claim instead has a separately defined, bounded uninterrupted
continuation and its own unconditional epoch-null, killing on failure also
preserves that theorem. This is a different sufficient premise and is not
inferred from the executed range checks.

There is also a selection detail at prediction time. Whether computation
successfully seals both forecasts can depend on the current context. Thus
one cannot use the pre-context per-event null to keep only successfully
sealed gains while assigning zero to the current failed attempt. The
definition above includes that attempted current exact gain before stopping.
Alternatively, a separately stated **pre-target** conditional null, with
the current context and successful sealing already in its filtration,
justifies counting only those sealed gains and filling all unsealed slots
with zero. That is another, generally stronger sufficient premise. None of
these conditions can be obtained by conditioning a failed computation away.

## 3. Lower logarithms and nonnegative factors

[numerics.py](../../src/reference_compiler/fp_reference/numerics.py) supplies
guarded exact rational enclosures. For a positive rational r it writes
`r=2^e*u`, `1<=u<2`, and uses

\[
\log u=2\sum_{m\ge0}\frac{z^{2m+1}}{2m+1},
\qquad z=\frac{u-1}{u+1}\in[0,1/3).
\]

After n terms, the positive tail is bounded by
`2*z^(2*n+1)/((2*n+1)*(1-z*z))`. The same series encloses `log 2`;
signed interval multiplication by e then encloses `log r`. Reduction,
series operations and encoding obey the registered reference integer-work
limit. A small final answer does not authorize an oversized unexecuted
intermediate operation.

For each exact sealed probability ratio, let `[l_t,u_t]` be its log
enclosure. Because the mathematical gain bound has already been proved,
`l_t^-=max(-B,l_t)` remains a lower bound on the true score. The epoch lower
gain `Y^-=(1/H)*sum_t l_t^-` therefore satisfies

\[
-B\le Y^-\le Y\le B.
\]

This truncation uses an independently proved lower bound; it is not the
unsound clipping of an out-of-range true score described above. For fixed
`0<=lambda<1`,

\[
0<1-\lambda\le1+\lambda Y^-/B
\le1+\lambda Y/B\le1+\lambda<2.
\]

Lower enclosures can be too loose to produce useful evidence. Their
mathematical direction preserves validity without requiring a uniform
power guarantee. Range, sum, division or logarithm computations that cannot
finish under the registered budget terminate this identity unresolved.

## 4. Dyadic floor wealth is a supermartingale

For the fixed grid `q=2^(-p)`, let `floor_q(x)=q*floor(x/q)`. Starting at
`W_0=1`, use the update implemented by `next_wealth` in
[persistence.py](../../src/reference_compiler/fp_reference/persistence.py):

\[
W_j=\operatorname{floor}_q
\left(W_{j-1}\left(1+\lambda Y_j^-/B\right)\right).
\]

The helper only operates on exact Fractions. It has no data, lineage,
admission, probability-law or installation authority. Its directed rounding
gives the pointwise relation

\[
0\le W_j
\le W_{j-1}(1+\lambda Y_j^-/B)
\le W_{j-1}(1+\lambda Y_j/B).
\]

Under the declared mean-null and predictable choices,

\[
\mathbb E[W_j\mid F_{j-1}]
\le W_{j-1}\left(1+\frac\lambda B
\mathbb E[Y_j\mid F_{j-1}]\right)
\le W_{j-1}.
\]

On a completed epoch `Y=Y^*`; failure branches use the killed extension in
section 6. Thus the direct stopped-epoch null in section 2.1 suffices for
this inequality without an unexecuted post-failure learner trajectory.

Thus W is a nonnegative supermartingale. Its first crossing of `1/alpha`
has probability at most alpha by Foundation XIV. The implemented threshold
test uses the exact guarded equivalent comparison `alpha*W>=1`; a rounded
display value or an arbitrary epsilon cannot decide crossing. Zero wealth
is absorbing. Quantization can prevent every crossing even under a useful
alternative, so no power bound is asserted for this implementation.

This proof applies before the first crossing; the Runtime then stops the
identity. Before that step `W_(j-1)<1/alpha`, so

\[
W_j\le W_{j-1}(1+\lambda)<\frac2\alpha.
\]

Consequently retained wealth has the form `N/2^p`, with
`0<=N<2^(p+1)/alpha`. Its numerator width is bounded by a function of
the registered alpha and p, independently of the number of epochs. The
helper rejects a further update after crossing. This bound concerns retained
wealth only: logarithm intermediates, rational arithmetic, counters, event
evidence, history and physical peak residency keep their own limits and
charges. It is neither a total-memory bound nor permission to erase history.

## 5. Freshness, shared observations and global alpha

Each admitted identity may use only the actual future ordinary observation
prefix beginning at its bound admission cursor. Proposal/profile data that
predate admission cannot return as new factors. Within an identity, an
observation contributes at most once, at its actual causal position. Repeated
values are possible fresh outcomes; reusing the same physical observation ID
is not a new outcome.

The same future observation may legally score several identities that were
all admitted before it arrived. The tests can be dependent. Each has its own
predictable rule, continuous pair of lineages and alpha allocation. Ordinary
learning after that observation's sealed scoring can also consume its label;
this does not retroactively invalidate the preceding fresh score. A later
candidate reconstructed using that label, however, cannot recycle it as a
future event of its new identity.

Let alpha_i be each identity's allocation, chosen from the actual admission
filtration, and require pathwise

\[
\sum_i\alpha_i\le\alpha_{total}.
\]

Conditional validity at admission and the union bound give

\[
\Pr(\text{at least one false crossing})
\le\sum_i\mathbb E[\alpha_i]
\le\alpha_{total},
\]

where the first sum can be restricted to the admitted null identities.
Independence between tests is unnecessary. Declaring several rules is not
itself spending alpha: each actual admission consumes a fresh allocation.
Reusing a rule, retiring a candidate, cancelling a run, exhausting resources,
or failing to cross does not refund that allocation. All admission and
allocation records remain owned canonical state.

## 6. Failure and live authority

A target cannot be unread after numerical or backend failure. In particular,
Runtime may not discard an unsuccessful epoch and resume the same identity
with its old wealth. Failures can depend on the just-observed outcome, so
such skipping could selectively remove losses.

Instead, a post-reveal failure terminates that identity. For the statistical
proof, extend its process as zero on failure and thereafter. Zero is below
the nonnegative exact next factor on every failed branch of the bounded
stopped-epoch law specified in section 2.1: `1+lambda*Y^*/B>=1-lambda>0`.
This preserves the one-step inequality at epoch boundaries. It does not
condition the null on success or infer an unproved future bound from
successful traces. The Runtime may retain the old numerical wealth as
historical audit state; it is not continuing live wealth and cannot be
reactivated. This killed-process extension does not require rewriting the
historical record. A later admission has a new identity and a new alpha
allocation.

Re-forking, reinitializing, changing the base, replacing the candidate or
losing trajectory continuity likewise ends the old certification identity
unless a separate authorized transport theorem establishes the full
required relationship. Current prediction equality does not establish it.
Resource work, revealed information and allocated alpha survive failure;
physical workspace release must use actual ownership operations.

At the registered horizon, absence of crossing means `UNRESOLVED`, never
structural rejection. Historical crossing and current continuation authority
also differ. A score crossing followed by an unsuccessful ordinary update,
optimizer commit or required bridge transition cannot authorize installation
of a nonexistent or mismatched successor.

## 7. Implementation obligations and retained scope

The arithmetic derivation is exercised by
[audit_persistence_kernel.py](../../scripts/audit_persistence_kernel.py).
It independently checks finite null laws, past-dependent choices, directed
floor inequalities, first-crossing bounds and shared-observation alpha
composition, and reproduces failures from upward rounding, outcome-dependent
bets, skipped losses and refunded allocations. Finite audits are evidence for
the implementation, not a replacement for the conditional proof above or a
proof of an external producer's law.

Complete Runtime use additionally requires its own enforced registration,
pre-context admission, fresh identity schedule, sealed paired predictions,
continuous observe/commit trajectory, owned work/evidence, terminal failures,
error ledger and state-bound result validation. No caller-supplied score,
cursor, terminal endpoint, rule replacement or helper result may supply these
facts. Endpoint evidence must record which of these obligations was actually
executed; this document does not invent an audit count or passing Runtime
freeze status.

The actual endpoint audit is now
[`audit_reference_persistence.py`](../../scripts/audit_reference_persistence.py).
It executes 32 complete fair-label null paths and checks 31 conditional
wealth inequalities, independently checks sealed probabilities and log
enclosures across changing learner commits, and verifies both crossing and
finite noncrossing. It covers shared fresh events, old query/profile data,
newborn state, alpha ownership, real numeric/work/memory exhaustion and
failure while staging or after completing a crossing. See its
[`minimal evidence`](../../evidence/minimal/FP_REFERENCE_PERSISTENCE_AUDIT.json)
for the exact fixed null and supported execution scope. These counts do
not prove all stochastic producers or close the remaining AMP/install gates.

The resulting evidence concerns **reference candidate versus reference
deployed**. It carries no AMP or installation authority. Foundation XV still
requires deployed/candidate reference/AMP trajectories with event-level
relations before scores, after observations and after commits. Foundation
XVI still requires the complete atomic installation transaction. Numerical
and stochastic bridge errors must be separately accounted for; a CPU
endpoint match does not discharge them. ERC-1 remains the frozen specification
and GPU/model science remains subject to its existing release gates.

The subsequent [PAIRED_CPU_PERSISTENCE.md](PAIRED_CPU_PERSISTENCE.md) executes
the four CPU paths with separate reference/stored-mass gains, current-domain
finite bounds and independent alpha allocations. It reuses this stopped-null
and lower-wealth argument without transferring reference evidence to finite
arithmetic. Actual target AMP and atomic installation remain unclosed.
