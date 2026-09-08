# Normalization, the exact SUM envelope, and forced PRODUCT

Status: **PROVED under the following source/readout/static-task contract**.
Date: 2026-09-06. Normative summary: `FP_THEORY.md`, XVII.1.

This result follows from FP's existing positive semantics. It introduces no
architecture action, resource exchange rate, or new foundation assumption.

## 1. Exact scope: the strongest SUM-only control

There are two binary score-time inputs `x,z`, available before the target, with
exactly their four declared unary indicator sources. The graph is a finite,
acyclic positive SUM DAG of arbitrary size, depth, sharing, and nonnegative
finite fixed coefficients. Its two evidence heads have one final native
normalization with fixed base `b_0=b_1=1`. There is no internal normalization,
input-dependent coefficient, learned extra source, recurrent state carrying the
pair, or target-dependent parameter update between cells of this static table.

By induction over the DAG, each unnormalized output mass has the form

\[
M_y(i,j)=1+u_{y,i}+v_{y,j},\qquad u,v\ge0.
\]

Conversely every such mass pair has a native SUM realization. Flattening is
used **only for this extensional loss envelope**: it asserts no resource,
optimizer, provenance, or complete-self-Compiler equivalence. Allowing all
finite coefficients makes this a stronger control than any bounded or
constructively restricted SUM-only implementation in the stated class.

The common shortcut “no PRODUCT means unigram on XOR” is **false** under FP's
normalization. It confuses additive masses with additive probabilities/logits.
This was not an explicit claim of frozen R4; it must not become an audit premise.

## 2. Exact representability of a binary conditional table

Write `p_ij=P(Y=1|i,j)` and assume all four entries lie in `(0,1)`.
Let

\[
I_D=\operatorname{conv}\{p_{00},p_{11}\},\qquad
I_O=\operatorname{conv}\{p_{01},p_{10}\}.
\]

**Theorem 1.** A finite SUM-only realization exists iff

\[
\boxed{\operatorname{ri} I_D\cap\operatorname{ri} I_O\ne\varnothing.}
\]

The relative interior of a singleton is that singleton. The closure of the
prediction family in `[0,1]^4` is exactly `I_D intersection I_O != empty`.

**Necessity.** Let `T=M_0+M_1>0`. Additivity gives

\[
T_{00}+T_{11}=T_{01}+T_{10}=S,
\]
\[
T_{00}p_{00}+T_{11}p_{11}
=T_{01}p_{01}+T_{10}p_{10}.
\]

After division by `S`, the common value is a strictly positive convex
combination of each pair, hence belongs to both relative interiors.

**Sufficiency.** Choose a common value and strictly positive convex weights
`lambda,1-lambda` and `mu,1-mu`. Set
`T=(lambda,mu,1-mu,1-lambda)` in order `00,01,10,11`, and
`M_1=T*p`, `M_0=T*(1-p)`. Both masses are positive additive tables.
Scale both by a common finite factor so every mass is at least 1; normalization
is unchanged. Subtract the registered base 1. Every nonnegative additive 2x2
table `A` is a nonnegative row-plus-column table: choose a global-minimum cell
`(i*,j*)`, set `u_i=A_i,j*` and `v_j=A_i*,j-A_i*,j*`, and use the additive
identity to obtain `A_ij=u_i+v_j`.

**Closure.** Necessity follows by continuity of the two closed intervals. For
sufficiency, first move all probabilities slightly towards 1/2 to avoid 0 and 1.
If the intervals merely touch, perturb endpoints arbitrarily slightly so that
their relative interiors overlap. Coincident singletons already qualify. Apply
the finite construction and take the limit. This is density, not permission to
install an infinite coefficient or a zero-denominator endpoint.

## 3. Exact weighted log-loss envelope for every 2x2 table

Let `w_i>0`, `sum w_i=1`, and `t_i in [0,1]` be the target probabilities of
class 1 at the four cells. Write `H(t)=-t log t-(1-t) log(1-t)` with the usual
endpoint convention. The unrestricted Bayes risk is `L_B=sum w_i H(t_i)`.

If the two target intervals intersect, the SUM-only risk infimum equals `L_B`.
Finite attainment is governed by Theorem 1, including strict output positivity.

Otherwise, let `d` range over diagonal cells and `o` over off-diagonal cells.
For each of the four pairs define

\[
\bar t_{do}=\frac{w_dt_d+w_ot_o}{w_d+w_o},
\]
\[
\Delta_{do}=(w_d+w_o)H(\bar t_{do})-w_dH(t_d)-w_oH(t_o).
\]

**Theorem 2.**

\[
\boxed{\inf_{SUM}L=L_B+\min_{d,o}\Delta_{do}.}
\]

An optimal table in the closure pools one minimizing diagonal/off-diagonal
pair to `bar t_do` and leaves the other two target probabilities unchanged.
Keep all tied minimizing pairs; a tie-break is not structural forcing.

**Proof.** Suppose every target diagonal probability is below every target
off-diagonal probability (the reversed case is symmetric). Any feasible table
must have `p_d>=p_o` for at least one of the four pairs. Minimize the separable
convex cross-entropy over this necessary union of four halfspaces. On each
halfspace the unconstrained pair is in the wrong order, so its constrained
optimum has `p_d=p_o`. Differentiation, or the Bernoulli likelihood identity,
gives their weighted pooled probability. Other cells minimize independently.
Each resulting pooled table has an equal diagonal/off-diagonal entry, hence
belongs to the actual family closure by Theorem 1. Thus the relaxation lower
bound is attainable as an infimum; it is not just a loose certificate.

For integer cell-label counts, all four pooled candidates are rational and
their likelihood products can be compared with **exact integer/rational
arithmetic**. No logarithmic tolerance is required to select a minimizing pair.
This is a mathematical solve over a prediction-family closure, **not** a
`CERTIFIED_COMPLETE` self-Compiler decision or a free reachable value optimum.

## 4. Sharp balanced noisy-XOR theorem

Let the four contexts be equally likely and the target equal `x XOR z` with
independent symmetric label noise `0<=eta<=1/2`. For every finite SUM-only graph,

\[
\boxed{L\ge L_{SUM}^*(\eta)=\tfrac12[\log 2+H(\eta)].}
\]

For `eta<1/2`, this is a sharp **unattained infimum**; at `eta=1/2`, the empty
graph attains it. This follows from Theorem 2: every adjacent pool equals 1/2,
and the two unpooled cells retain their Bayes probabilities.

A useful independent lower-bound proof uses correct-label probabilities
`q_00,q_01,q_10,q_11`. The weighted identity in Theorem 1 implies

\[
\min(q_{00},q_{11})+\min(q_{01},q_{10})\le1.
\]

Thus some diagonal/off-diagonal pair has `q_d+q_o<=1`. Convexity of binary
cross-entropy and its monotone decrease up to `1-eta>=1/2` give total loss at
least `2 log 2` on that pair. The other two cells contribute at least `2H(eta)`.
For deterministic XOR this also gives the exact rational certificate

\[
\boxed{\prod_{i,j}q_{ij}\le1/4.}
\]

**Sharpness with the required strictly positive base.** Put `v_0=(eta,1-eta)`
and `v_1=(1-eta,eta)`, with coordinates in output-label order, and use only SUM:

\[
(M_0,M_1)= (1,1)+A v_x+K\,1[z=0](1,1).
\]

For `A -> infinity` and `K/A -> infinity`, the `z=1` column approaches the
Bayes noisy-XOR distribution and the other column approaches `(1/2,1/2)`.
The loss approaches the displayed bound. Every member is finite and legal;
the limit is not a finite physical state. At `eta<1/2`, equality in the lower
bound would require two adjacent correct probabilities 1/2 and the other two
`1-eta`; the diagonal/off-diagonal relative interiors then fail to intersect
(or probabilities hit 0/1 when `eta=0`). This proves nonattainment.

In particular, pure SUM can approach **0.3465735903 nats** on deterministic
XOR, whereas unigram gives **0.6931471806 nats**. Beating unigram is not evidence
that PRODUCT is needed. Compactness/finite encoding and constructive value
constraints cannot be silently replaced by this unattained relaxed optimum.

## 5. One PRODUCT exactly realizes every symmetric noisy XOR

Let `r>=1` and let `x,z` now denote their declared one-indicator sources. Use
one semantic PRODUCT `xz` and positive SUM to form

\[
\boxed{M_0=r+2r(r^2-1)xz,\qquad
M_1=1+(r^2-1)(x+z).}
\]

The constant extra mass `r-1` in head 0 is a SUM of the two `x` indicators;
it is not an undeclared leaf. The registered base remains `(1,1)`. Direct
substitution gives correct-label probability `r/(r+1)` at **all four cells**.
For `0<eta<=1/2`, set `r=(1-eta)/eta` to reach Bayes risk `H(eta)` exactly.
At `eta=1/2` the PRODUCT is unnecessary/zero-weighted.

For deterministic XOR, the finite integer witness `r=3` is

\[
M_0=3+48xz,\qquad M_1=1+8(x+z),
\]

with mass pairs `(3,1),(3,9),(3,9),(51,17)`, respectively. It has one PRODUCT,
correct probability `3/4` everywhere, and

\[
L=\log(4/3)<\tfrac12\log2,
\quad (3/4)^4=81/256>1/4.
\]

Four categorical pair-cell PRODUCTs are therefore sufficient but not necessary
to express this conditional distribution. Normalization is part of the native
semantics and must participate in minimum-structure reasoning.

## 6. Extension to the hidden-group token gate without weakening its baseline

The inputs may be arbitrary finite tokens with unary one-hot sources, partitioned
by hidden binary groups. Suppose the context distribution has the form

\[
P(i,j)=w_{ab}\rho_a(i)\sigma_b(j),\quad a=g(i),\ b=h(j),
\]

and the target conditional `t_ab` depends only on the two groups. The groups
need not be supplied to the SUM-only control: permit **arbitrary token-specific
unary coefficients**, which is at least as strong as any acquired group model.

Draw independently one token from each of the two left and two right groups.
Every resulting 2x2 rectangle obeys Theorems 1--2 with the same `w,t`, since
its mass tables remain additive. Average the rectangle risk inequality over
these draws to obtain the original token-task risk inequality. Conversely,
group-constant unary coefficients approach the two-bit envelope. Thus the
infimum over all unary-token SUM models is **exactly** the weighted two-group
envelope, not merely a lower bound for a restricted group-aware baseline.

For balanced groups and symmetric noise it is again `[log 2+H(eta)]/2`.
Once legally acquired, each group indicator is a positive SUM of token atoms;
the one-PRODUCT witness then applies. Acquisition of `g,h`, its cost, and noisy
identifiability are not supplied by this loss theorem. Nor does equality of
this static optimum justify quotienting complete token-specific learner states.
Arbitrary non-factorizing within-block sampling does not inherit this averaging
argument without another proof.

## 7. What is actually forced, and what still requires evidence

For any registered reachable target class in this **static source contract**,
if its optimal set is nonempty and it contains a feasible, constructively
reachable witness with loss below `L_SUM^*`, then **every** optimum contains at
least one semantic PRODUCT. This excludes every SUM-only graph at once,
regardless of width, sharing, or its optimizer's success. For epsilon-optimal
forcing, require `L_witness+epsilon<L_SUM^*`.

For noisy XOR with a reachable Bayes witness the gap is
`[log 2-H(eta)]/2`. For the displayed deterministic integer witness the certified
gap is `log(3/(2 sqrt(2)))`, approximately `0.0588915178` nats.

The algebraic witness alone does **not** prove its numerical state is reached
by a specific registered initializer/profile/optimizer, that its build/install
fits a machine's resources, that passive data identifies a hidden partition,
or that fresh persistence/AMP gates pass. Those are independent premises for
an installation or resource-phase claim. No GPU/model-science run follows.

The theorem also does not apply after enriching the sources with the pair
indicator, using an input-dependent positive base that already solves XOR,
feeding readout normalization back internally, or allowing adaptive recurrence
to carry joint information. It is an extensional separation useful as a sound
relaxation bound, not a universal FP-coordinate or physical-node lower bound.

## 8. Audit and remaining research

`theory/numerical_checks/normalized_sum_xor_audit.py` checks the algebra with
exact fractions, exhaustively checks small SUM weight assignments, constructs
representable rational tables, and compares the four weighted projection
candidates without float ordering. Optional float64 optimization is a search
stress test, not the proof. Minimal evidence is recorded in
`evidence/minimal/FP_NORMALIZED_SUM_XOR_AUDIT.json`.

The exploratory float64 searches on 3--5 bit parity originally suggested a
stronger dimension-dependent SUM envelope. That conjecture is now proved in
`UNARY_SUM_PARITY_ENVELOPE.md` (2026-09-08), using a global affine log-ratio
oscillation bound, not numerical optimizer termination. The historical search
evidence records its then-conjectural status. General passive multi-input
targets, nonuniform sampling and sharp finite-range optima remain open.
