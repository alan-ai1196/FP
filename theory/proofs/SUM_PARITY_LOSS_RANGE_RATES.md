# Noise changes the range exponent of the sharp SUM loss envelope

Status: **PROVED**, 2026-09-09. The discrepancy capacity and CE objectives
have different resource laws. This supplies matching rate exponents for the
full SUM class, without claiming sharp leading CE constants.

## 1. Scope and result

Keep the static unary-source binary parity contract of
`UNARY_SUM_PARITY_ENVELOPE.md`: d>=2, N=2^d uniform contexts, symmetric noise
0<=eta<1/2, base one in both positive affine output masses, and one final
normalization. Arbitrary nonnegative SUM DAGs are allowed. Define L_R as the
minimum CE under the final-normalizer cap T<=R, and

`L_infinity=log2-(2/N)[log2-H(eta)]`, `Delta_R=L_R-L_infinity`.

With d fixed,

\[
\boxed{\Delta_R=\Theta(R^{-1})\quad(0<\eta<1/2\text{ fixed}),
\qquad\Delta_R=\Theta(R^{-1/2})\quad(\eta=0).}
\]

Thus CE accuracy epsilon above this unattained infimum costs range
Theta(epsilon^-1) at fixed positive noise, but Theta(epsilon^-2) without
noise. These are final-normalizer resources, not hardware costs or optimizer
iteration counts. The constants depend on d and eta; no uniform interchange
of eta->0 and R->infinity is asserted.

## 2. A direct loss-discrepancy inequality

For a model prediction q=q_1, let `D=|sum chi q|`, and put p=1-eta,
a=1-2eta. The normalized affine discrepancy lemma also proves

`D <= max q-min q`:

subtract `(min q)T` from the affine numerator and divide by the oscillation
to get another nonnegative affine numerator bounded by T. This inequality
is strict for finite nonconstant masses in d>=2.

For correct-label probability r, define the tangent residual

`B_a(r)=CE(p,r)-log2+2a(r-1/2)`.

It is nonnegative and convex, and increases on [1/2,1). Moreover
`B_a(1/2+s)<=B_a(1/2-s)` for 0<=s<1/2, since
`log((1+2s)/(1-2s))>=4s`. Thus each residual is bounded below by the residual
at the same absolute deviation on the positive side of one-half.

Select vertices attaining q_max and q_min. Their absolute deviations from
one-half sum to at least q_max-q_min>=D. Convexity and monotonicity give

`sum_x B_a(r_x) >= 2 B_a((1+D)/2)`.

All other residuals are nonnegative. The signed correct-probability surplus
is `sum r_x-N/2=-sum chi q<=D`. Consequently

\[
\boxed{L(q)\ge(1-2/N)\log2+\frac2N
\operatorname{CE}\!\left(1-\eta,\frac{1+D}{2}\right).}
\]

For a constant q, D=0 and L>=log2 gives the same conclusion without selecting
two distinct extrema. This recovers the exact unbounded envelope by minimizing
over D; its minimum occurs at D=a. It is a stronger quantified statement than
the envelope alone. The proof uses probability oscillation directly; the
separate log-ratio interpolation theorem remains useful for the finite-noise
range bound below.

With the exact capacity D_d(R) from `SUM_PARITY_RANGE_CAPACITY.md`, the valid
all-class consequence is to replace D in the boxed bound by
`min(a,D_d(R))`. Maximizing discrepancy is not asserted to minimize CE.

For rational eta=A/B and a rational model, the boxed inequality has an exact
likelihood audit: writing r=(1+D)/2,

`prod_x q_correct(x)^(B-A) q_wrong(x)^A`
`<=2^(-(N-2)B) r^(2(B-A)) (1-r)^(2A)`.

## 3. Deterministic lower bound and a matching rate construction

Let `C=(d-1)H_(d-1)` denote the harmonic factor, as distinguished from binary
entropy. The capacity theorem gives
`D_d(R)<=(s-1)/(s+1)`, `s=sqrt(1+R/C)`. At eta=0 the loss-discrepancy
inequality therefore yields the explicit lower bound

\[
\boxed{\Delta_R\ge\frac2N\log\left(1+\frac1{\sqrt{1+R/C}}\right),
\quad\liminf_{R\to\infty}\sqrt R\Delta_R\ge\frac{2\sqrt C}{N}.}
\]

For a converse use the native masses

`M_y=1+k 1[y=x_1]+u sum_(i>=2) x_i`.

Their peak total is R=2+k+2(d-1)u. The two root contexts with all other inputs
zero have correct probability (k+1)/(k+2), hence loss
`log(1+1/(k+1))<=1/k`. At a context with s>=1 other active coordinates, the
correct probability is `(1+(-1)^s k/(k+2+2us))/2`.

For fixed d, k->infinity, k/u->0, expand the finitely many non-root log losses.
The exact identity
`sum_(s=1)^m (-1)^(s-1) binom(m,s)/s=H_m`
follows by integrating `[1-(1-t)^m]/t` on [0,1]. It gives

\[
\Delta_{witness}=\frac2{Nk}+\frac{kH_m}{Nu}
+O(k^{-2}+k^2/u^2),\qquad m=d-1.
\]

Choose rational witnesses k=n, `u=C n^2/(2m)`, with cap
`R_n=C n^2+n+2`. Then

`lim sqrt(R_n) Delta_witness=4 sqrt(C)/N`.

Monotonicity in R and R_(n+1)/R_n->1 extend the upper asymptotic bound to
all large R. Thus

\[
\frac{2\sqrt C}{N}\le\liminf\sqrt R\Delta_R
\le\limsup\sqrt R\Delta_R\le\frac{4\sqrt C}{N}.
\]

The exponent is sharp; the possible factor-two gap in the leading constant
is not closed by this proof.

## 4. A finite-range contraction of log-ratio oscillation

Let f be affine with 1<=f<=R-1, and h affine with 0<=h<=f. Orient f as
`c+sum_i t_i x_i`, c>=1. The integral proof of normalized discrepancy bounds
`|sum chi h/f|` by `c max_i int exp(-cs) prod_(j!=i)(1-exp(-t_j s)) ds`.
Equalize those d-1 slopes and use their sum <=R-1-c. As the product depends
monotonically on slope/c and c>=1, this is at most

\[
\beta_d(R)=\prod_{j=1}^{d-1}\frac{j(R-2)}{d-1+j(R-2)}<1.
\]

Every affine interpolation between the model's two masses lies between one
and R-1. Apply this bound to the normalized derivative numerator in the
log-ratio interpolation argument to obtain

`|sum chi log(M_1/M_0)|<=beta_d(R) osc log(M_1/M_0)`.

The extreme-log-odds log-cosh proof now gives

\[
\boxed{L_R\ge\log2-\frac2N\left[\log2-
H\!\left(\frac{1-a\beta_d(R)}2\right)\right].}
\]

At R=2 the base is the only mass table and beta=0; the same formula gives
log2 without dividing by beta. If eta is fixed in (0,1/2),
`1-beta_d(R)=C/R+O(R^-2)`, so

\[
\liminf_{R\to\infty}R\Delta_R
\ge\frac{aC}{N}\log\frac{1-\eta}{\eta}>0.
\]

This contraction bound is valid also at eta=0, but the deterministic
capacity/loss bound above is stronger in that limit.

## 5. Positive noise allows finite exact Bayes masses at the root pair

For fixed eta>0 put lambda=1/eta. The two noisy target vectors v_0,v_1 satisfy
`lambda v_(x_1,y)>=1`. At any R>=lambda choose

`M_y=lambda v_(x_1,y)+u sum_(i>=2) x_i`,
`u=(R-lambda)/(2(d-1))`.

This is a native base-one SUM program: all excess unary coefficients
`lambda v-1` are nonnegative. The two root contexts are **exactly** Bayes
at finite lambda. At other contexts, probabilities approach one-half as u
grows. If R>lambda, each non-root CE is at most
`log2+a lambda/(2u)`, by `-log(1-z)<=z/(1-z)`. Hence

`0<Delta_R<=Delta_witness<=a lambda(d-1)/(R-lambda)`.

The same finite binomial identity gives the sharper witness asymptotic

\[
\lim_{R\to\infty}R\Delta_{witness}
=\frac{2a^2\lambda C}{N}.
\]

Together with the strictly positive lower constant this proves Theta(R^-1).
It also explains why the eta=0 limit is singular: lambda=1/eta diverges, and
the fixed positive base prevents any finite root mass from giving a zero
wrong-label probability. The deterministic construction must balance that
root error against the non-root normalization error.

## 6. Interpretation and remaining scope

Near-maximal parity discrepancy costs Theta(epsilon^-2) range, whereas at
fixed positive noise, CE near its sharp SUM infimum costs only
Theta(epsilon^-1). Substituting a discrepancy objective for task loss would
therefore give the wrong resource exponent. More strongly, for any fixed
eta>0, the direct inequality forces CE to diverge as D->1, with a term
`(2eta/N) log(2/(1-D))`, while the task's optimal infimum stays finite.
Increasing interaction amplitude without regard to the declared task can
therefore be inconsistent even in this completely known static setting.

The exact finite CE optimum,
sharp leading CE constants, nonuniform context laws and a uniform noise/range
crossover remain open. These theorems concern finite static witnesses and
all-class bounds; they supply no acquisition, registered value trajectory,
fresh persistence or physical/reference-to-AMP installation evidence.

Exact likelihood, rational construction and outward-log audit:
`theory/numerical_checks/sum_parity_loss_rate_audit.py`.
