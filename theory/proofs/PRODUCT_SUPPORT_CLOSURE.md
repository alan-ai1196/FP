# Complete support-limit decisions through coefficient exponents

Status: **PROVED CHARACTERIZATION; EXACT CERTIFICATE IMPLEMENTATION**,
2026-09-11. Fixed-PRODUCT support limits reduce to a finite disjunction of
rational linear systems. Accepted integer exponents construct a finite limit;
complete Farkas trees reject every support lift. The executable search is
budgeted and may return UNRESOLVED. Its verified statuses have no Runtime
completion or installation authority.

## 1. The decision class and what the decision says

Fix the complete d-bit cube and its 2d scalar unary indicators. Allow at most
P binary PRODUCTs, arbitrary finite positive SUM graphs, arbitrary sharing,
and arbitrary fixed real nonnegative coefficients. There is no recurrence,
internal normalization, source acquisition or physical budget in this static
class. The object is a scalar excess mass g, before adding a readout base.

Given a set S of contexts, ask whether **some finite mass table f in the
pointwise closure of this class has supp(f)=S**. Values on S are not prescribed.
In particular, accepting the full support does not realize an arbitrary
strictly positive mass table. The table (1,2,2,1) has full support but is not
a two-input SUM mass: it violates the affine diagonal-sum identity.

Topologically order the PRODUCT nodes. Collapse only SUM paths to write

```
h_j = A_j(sources,h_0,...,h_(j-1)) B_j(sources,h_0,...,h_(j-1)),
g   = C(sources,h_0,...,h_(P-1)),
```

where every A_j,B_j,C is a nonnegative linear combination of its listed
features, with independent coefficient slots. This represents the entire
static at-most-P class; unused nodes/edges have zero coefficients. It has
`n=2d(2P+1)+P^2` coefficient slots. This is an extensional search normal form,
not a registered value transport, learner equivalence or resource quotient.

At each context x it is a finite polynomial in those coefficients z:

`F_x(z)=sum_alpha c_(x,alpha) z^alpha`, c_(x,alpha)>=0.

The exponents include multiplicities from shared ancestors and repeated
squaring. For these indicator sources, every nonzero c is a positive integer.
Discard a monomial only when it is zero on the **whole declared cube**, as
proved from the source partitions. An acquired sample cannot establish that
annihilator. Let Gamma contain all remaining coefficient exponent vectors.

## 2. Integer exponents capture every possible limiting support

The following statement also holds for any fixed finite nonnegative
polynomial map on its full nonnegative parameter orthant, not only the
native normal form above. Additional parameter/resource constraints are
not included in that generalization.

**Support-limit theorem.** A set S is the support of some finite limit of F
iff there exists a rational vector w, equivalently an integer vector after
rescaling, such that

```
alpha.w >= 0                    for every alpha in Gamma;
alpha.w >= 1                    if c_(x,alpha)>0 at any x outside S;
min_{alpha:c_(x,alpha)>0} alpha.w = 0   for every x in S.
```

An empty minimum cannot equal zero. Negative coordinates of w are permitted:
they encode diverging coefficients, which the earlier border examples need.

Sufficiency is direct. Set each coefficient z_i(epsilon)=epsilon^w_i.
After clearing denominators of w, each observed term has a nonnegative
integer exponent. The limit is

`f_w(x)=sum_{alpha:alpha.w=0} c_(x,alpha)`.

It is finite, positive precisely on S, and rational for rational source data.
With indicator sources it is an integer table. For 0<epsilon<=1,

`0<=F_x(epsilon^w)-f_w(x)<=epsilon sum_alpha c_(x,alpha)`.

For the native class with its freely scaled final excess readout, a uniform
positive excess cap does not change support existence: scale the entire
output by a fixed positive constant so that F_x(1) fits the cap. Intermediate
activations and physical resources are separate.

For necessity, suppose F(z_n) converges to f with support S. Zero parameter
entries may first be replaced by sufficiently small positive values, using
continuity at each finite z_n, without changing the output limit. Every
visible monomial z_n^alpha is bounded: it contributes with a positive fixed
coefficient at some context and cannot be cancelled. Take a common
subsequence on which these finitely many monomials converge, and let J be
the exponents with a strictly positive limit. Every context in S sees some
member of J; no context outside S sees one.

Put t_n=-log z_n. For alpha in J, alpha.t_n stays bounded. For alpha outside
J it tends to positive infinity. The linear system
`alpha.w=0` on J and `alpha.w>=1` outside J must be feasible. Otherwise
Farkas' alternative would give a nonzero nonnegative combination of the
outside-J exponent vectors equal to a signed combination of the J vectors.
Dotting with t_n makes one side tend to infinity while the other stays
bounded. A rational feasible point exists because the system is rational;
clear its denominators to get integer w. If Gamma=J, w=0 already suffices.
This proves necessity without bounded hidden coefficients or rounded zeros.

There is a stronger **full-mass lifting statement** on the same full
nonnegative parameter domain. Every finite limit f
has a path of the form `z_i(epsilon)=a_i epsilon^w_i`, with finite a_i>0 and
integer w, whose output tends to exactly f. For its proof use the same J,w.
The vector of logarithms of the positive limiting monomial values is the
limit of the matrix-vector products `(alpha.log z_n)_(alpha in J)`. A finite
linear image is closed, so it equals `(alpha.v)_(alpha in J)` for some v.
Taking a_i=exp(v_i) matches every positive limiting monomial simultaneously.
All other visible monomials vanish along the chosen powers. Thus

`f(x)=sum_{alpha:alpha.w=0} c_(x,alpha) a^alpha`.

This is a constructive characterization of full finite-P static mass closure,
including multiple output coordinates of the same positive polynomial map.
Its positive constants need not be rational. The implemented solver below
decides only support existence and can set a_i=1 there. Searching the leading
constants for prescribed values is an additional algebraic problem.

The monomial/toric boundary distinction underlying this argument was already
identified in `MASKED_PRODUCT_CLOSURE.md`. Here positivity of the observation
map and Farkas' alternative reduce the *support* question even for
multiple nested PRODUCTs. They do not eliminate the numerical equations for
a prescribed mass table.

## 3. A finite exact decision and a compact accepting certificate

Call alpha **bad** when its source support meets the complement of S; call
the other exponents **pure**. At each positive context choose one visible
pure monomial to be leading. For that branch solve the rational LP

`alpha.w>=1` for bad monomials, `alpha.w>=0` for pure ones,
`alpha.w=0` for the selected leading monomials.

The number of branches and the size of every LP are finite. The theorem
proves that this is a complete decision method with exact LP alternatives.
Exhaustion of the implemented monomial/search budget or failure to reconstruct
an exact LP certificate returns UNRESOLVED.

Acceptance needs only the integer vector w. A separate verifier evaluates
the original native graph in minimum-exponent arithmetic: positive SUM takes
the minimum and adds the positive counts of tied terms; PRODUCT adds the
exponents and multiplies their leading counts. It checks exponent zero on S
and exponent at least one outside S. No polynomial expansion or LP status is
trusted on this acceptance path. All coefficients epsilon^w are finite for
each epsilon>0, even when they diverge as epsilon decreases.

The entire finite Boolean-support catalogue agrees with the limit-support
catalogue in the audited zero/one-PRODUCT two/three-input cases. That is a
small exhaustive observation, not a theorem for larger counts. The previous
two-PRODUCT support-border example is a required accepted counterexample to
using Boolean enumeration as a general closure oracle.

## 4. Rejection trees are checked through exponent identities

At a search node, selected pure monomials must have exponent zero. An
infeasible LP has a rational Farkas certificate of the form

`sum_alpha u_alpha alpha = sum_selected v_alpha alpha`, u,v>=0,

with a strictly positive total u weight on bad monomials. Dotting with any
feasible w would make the left side positive and the right side zero.
The verifier checks this vector identity exactly against independently
regenerated exponents, and checks that every right-hand monomial was selected
on the current branch. The LP optimizer's reported status is irrelevant.

A split chooses an as-yet-uncovered positive context and contains **all** its
pure leading possibilities. Selecting one also covers every other context
in its source face. A context with no pure monomial closes the branch directly.
Every path either reaches a checked Farkas contradiction or such an empty
choice; a complete tree therefore excludes every exponent lift. Missing
children, a non-strict identity, changed external support, wrong dimensions
or an unselected right-hand monomial invalidate the certificate.

The saved three-input parity proof is about 117 KB of compact JSON. Identical
proof nodes are interned and split-child monomial indices are regenerated in
their complete canonical order. It has 1,906 stored nodes; expanded, it has
85 covered splits and 1,956 exact Farkas leaves. It can be checked using only
Python integer/rational arithmetic, without SciPy, Z3 or a new search:

`python -B theory/numerical_checks/product_support_closure_audit.py --verify-parity-proof`

The external claim is d=3, P<=2 and odd-parity support. Artifact metadata alone
does not set the verifier's intended claim.

## 5. The same rejection tree gives an explicit mass separation

Let the prescribed target f have this rejected support S, with positive
values in [gamma,M], 0<gamma<=M. Let K_+ be the largest sum of pure monomial
multiplicities at a positive context, and K_- the largest corresponding bad
sum. These counts come from the complete native polynomial, not a numerical
active set.

For a Farkas leaf, let D=sum u and B=sum_bad u. Every output monomial has
degree one in the final readout's coefficient slots. Summing the certificate's
exponent identity over those slots therefore gives sum v=D as well. B>0.
Take L to be the maximum of one and ceil(D/B) over all leaves. Then, when
K_+>0, every finite at-most-P mass satisfies

\[
\boxed{\|g-f\|_\infty\ge
\min\left\{\frac{\gamma}{2(K_-+1)},
2M\left(\frac{\gamma}{4K_+M}\right)^L\right\}.}
\]

If K_+=0, the first bound alone suffices. These are conservative constants.

To prove it, suppose the error delta is below the displayed bound. Each bad
monomial value is <=delta because it is visible at a zero context and its
multiplicity is at least one. At any positive context the pure terms total
at least gamma-(K_-+1)delta>gamma/2. Some pure monomial therefore has value
at least b=gamma/(2K_+). Follow this choice through every split of the proof.
A no-leading-monomial leaf is impossible. At a Farkas leaf, the exponent
identity is also an exact multiplicative identity in the coefficient values.
After clearing rational powers, it implies

`b^D <= delta^B (2M)^(D-B)`.

Here every visible monomial is at most M+delta<=2M. The chosen leading
monomials all have value >=b. Since D/B<=L and b/(2M)<=1, the inequality
forces `delta>=2M (gamma/(4K_+M))^L`, a contradiction. This argument also
handles zero coefficients: a positive selected side cannot equal a vanished
side of the polynomial identity. It assumes no lower bound on local
coefficients and no upper bound on hidden activations.

## 6. A proved two-versus-three boundary for a parity mass

For the odd-parity indicator on three bits, the stored complete rejection
tree gives K_+=48, K_-=108 and L=2. Thus

`inf_(P<=2) ||g-1_odd||_infinity >= 1/18432`.

This is a proved bound from an independently checked finite certificate,
not an empirical optimizer failure. Three PRODUCTs realize the exact mass:

```
e = (x_0+y_1)(x_1+y_0)
o = (x_0+y_0)(x_1+y_1)
1_odd = (e+z_0)(o+z_1).
```

Their cross terms eo and z_0 z_1 vanish exactly. Consequently both the exact
and arbitrarily accurate scalar PRODUCT minima are three. The excluded
two-PRODUCT class includes squared/shared first products and every positive
SUM coefficient, not only products whose reduced degree is below three.

There is also a conditional consequence retaining all scales. For symmetric
noise eta=1/4, uniform three-bit contexts, base (1,1) and cap T<=4, suppose
the probability sup error is delta. At even contexts, the target is 1/4,
so E_1=M_1-1<=4 delta. At odd contexts, the base M_0>=1 and q_1>=3/4-delta
give E_1>=2-16 delta, while the cap gives E_1<=2. Therefore

`||E_1-2*1_odd||_infinity<=16 delta`.

Scalar output scaling preserves PRODUCT count. The mass bound hence gives

`delta >= 1/147456`,
`L(q)-L_Bayes >= 1/86973087744` nats for every P<=2 model.

The latter follows from uniform-context Bernoulli Pinsker. Four PRODUCTs
give the established Bayes witness for both parity heads. Whether three
PRODUCTs suffice for conditional Bayes closure at this cap is not settled
here. The constants above are not claimed sharp.

## 7. Executable scope and remaining work

The exact audit checks 544 small support classes against exhaustive finite
Boolean graphs, 32 independent symbolic context expansions, 60 rational
arithmetic/leading-count cases, the known two-PRODUCT border acceptance,
both rejection trees, 312 conditional-scale comparisons, seven certificate
forgeries, budget exhaustion and fake LP-success outputs containing NaN/Inf.
The latter failures return UNRESOLVED. It keeps the substantive multi-PRODUCT rejection proof
as auditable evidence, not a numerical solver log.

Fixed rational atoms, general typed finite graph families and shared output
heads admit related finite polynomial formulations, but are not silently
included in this executable unary scalar decision class. Prescribed mass
values, unknown information, complete resources, registered value paths,
fresh persistence, installation and AMP remain separate obligations.

Proof search:
`theory/numerical_checks/product_support_closure_audit.py`.
