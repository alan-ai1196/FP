# Exact finite-range parity capacity of normalized SUM

Status: **PROVED**, 2026-09-08. This strengthens the unbounded discrepancy
theorem in `UNARY_SUM_PARITY_ENVELOPE.md` with a resource-dependent exact
variational formula, a sharp asymptotic range law and a finite exact case.

## 1. The declared complete static class

Use d>=2 binary inputs, unary indicator sources, arbitrary finite positive
SUM DAGs, base one in each of two outputs and one final normalization. There
is no recurrence, internal normalization or context-dependent external choice.
Write chi(x)=(-1)^(sum x_i), q=M_1/(M_0+M_1), and impose the final-normalizer
cap T(x)<=R, with R>=2. Define

`D_d(R)=max_SUM |sum_x chi(x) q(x)|`.

The maximum exists: positive unary coefficients are bounded under the cap,
and the finite-dimensional mass parameterization has a compact feasible
domain. This is a prediction discrepancy, not CE or a physical hardware cost.
Its normalized Fourier amplitude is D_d(R)/2^d. The unbounded supremum is one.

More generally, in any larger binary cube the maximum absolute Fourier
coefficient on a fixed k-coordinate subset, k>=2, is exactly D_k(R)/2^k.
Condition on the other coordinates and apply this class bound, then average;
the converse simply ignores those coordinates. Extra fixed unary contributions
still satisfy the same base-one and cap contracts.

## 2. Eliminate the entire numerator class exactly

Flip coordinates to write a fixed denominator as
`T=c+sum_i t_i x_i`, c>=2, t_i>=0. Such flips only change the sign of chi.
Use the exact moments from the preceding proof:

`I=sum chi/T >=0`, `J_i=-sum chi x_i/T >=0`.

For an affine numerator `h=h_0+sum_i h_i x_i` with 1<=h<=T-1,
`sum_i max(-h_i,0)<=h_0-1<=c-2`. Therefore

\[
\sum_x\chi h/T\le(c-1)I+(c-2)\max_i J_i.
\]

Equality is attained by `h=c-1-(c-2)x_i` for an index maximizing J_i; both
output masses remain at least one. Complementing h proves the same optimum
for the negative sign. This is an exact optimization over all numerators,
including arbitrary signed affine slopes allowed by positive unary sources.

An index with smallest t_i maximizes J_i, as follows immediately by subtracting
their Laplace integral formulas. Let that slope be t and put m=d-1. For the
other slopes the optimum integrand is

`exp(-c s) [(c-1)-exp(-t s)] prod_(j!=i)(1-exp(-t_j s))`.

The prefactor is nonnegative. For each s>0, `log(1-exp(-v s))` is concave in
v>0, with the zero-slope case obtained by continuity. At fixed sum, equalizing
the other m slopes therefore increases the objective pointwise under the
integral. Increasing their common value cannot decrease it, so the cap can
be saturated. Let `u=(R-c-t)/m`; the smallest-slope condition is t<=u.

These are deductions about the objective's global optimum, not a symmetry
assumption about arbitrary fitted programs or an authorized state rewrite.

## 3. Exact two-variable variational formula

The elementary integral identity

\[
\int_0^\infty e^{-a s}(1-e^{-u s})^m ds
=\frac1a\prod_{j=1}^m\frac{ju}{a+ju}
\]

follows by substituting exp(-u s), or by repeated integration by parts. Its
zero-u value is zero for m>=1. Consequently

\[
\boxed{D_d(R)=\max_{\substack{2\le c\le R\\0\le t\le(R-c)/d}}
F(c,t),\quad u=(R-c-t)/(d-1),}
\]

\[
F(c,t)=\frac{c-1}{c}\prod_{j=1}^{d-1}\frac{ju}{c+ju}
-\frac1{c+t}\prod_{j=1}^{d-1}\frac{ju}{c+t+ju}.
\]

Every point is attained by the native masses

`M_1=1+(c-2)(1-x_1)`,
`M_0=1+(c-2+t)x_1+u sum_(i=2)^d x_i`.

Thus the reduction has both a complete lower argument and a finite converse,
and includes the constant-numerator face c=2. F is rational for rational
parameters. A numerical optimizer of this two-variable function still supplies
only a candidate unless a separate global certificate is checked.

## 4. A sharp range law for approaching maximal high-order response

Let `A=(d-1) H_(d-1)`, where H_m=sum_(j=1)^m 1/j is the harmonic number.
Discarding the nonnegative second term and using
`prod_j(1+c/(ju))>=1+c H_m/u`, with u<=R/(d-1), gives

\[
F\le\frac{1-1/c}{1+A c/R}
\le\frac{\sqrt{1+R/A}-1}{\sqrt{1+R/A}+1}.
\]

The final scalar maximum permits every c>0; it is attained at
`c=1+sqrt(1+R/A)`, so the relaxation remains an upper bound even if this c is
outside the original feasible interval. Equivalently, for any feasible
nonnegative discrepancy D,

\[
\boxed{R(1-D)^2\ge4 A D.}
\]

In particular reaching D>=1-epsilon requires
`R>=4 A (1-epsilon)/epsilon^2`. This is a lower bound on the declared final
normalizer range, not on every intermediate activation or physical byte/FLOP.

The leading constant is sharp for each fixed d:

\[
\boxed{\lim_{R\to\infty}\sqrt R\,[1-D_d(R)]=2\sqrt A.}
\]

For a rational witness sequence take integer n tending to infinity and
`R_n=A n^4`, `c=n^2`, `t=n^3`, `u=(R_n-n^2-n^3)/m`. The domain conditions
hold for all sufficiently large n. The first product in F is
`1-c H_m/u+O(n^-4)=1-n^-2+o(n^-2)`. Its prefactor is 1-n^-2; the subtracted
term is at most 1/(c+t)=O(n^-3). Hence
`n^2[1-F(c,t)]->2`. The universal upper bound on D supplies the reverse
asymptotic inequality. Monotonicity in R and R_(n+1)/R_n->1 extend the result
from this rational sequence to every large R.

These limits hold with d fixed. They do not silently interchange growing
dimension, precision and range limits. The exact finite lower bound retains
its explicit dimension factor A for all d>=2.

## 5. A globally exact finite case: three inputs at range four

For d=3 and R=4,

\[
\boxed{D_3(4)=1/40.}
\]

The witness has c=2, t=u=2/3, namely M_1=1 and
`M_0=1+(2/3)(x_1+x_2+x_3)`. Here is an exact global certificate, independent
of local optimization. Write c=2+2a/S, t=2b/(3S), u=(2b/3+g)/S, where
a,b,g>=0 and S=a+b+g>0. This parameterizes the entire reduced domain.

Let `Q=40 c(c+t)(t-4)(-c+t-4)(c+t+4)>0`. Direct clearing of denominators gives
`S^5 Q [1/40-F(c,t)]=P(a,b,g)`, where

```
P = 4096 a^5 + 14336 a^4(b+g)
  + a^3(15360 b^2 + 26112 b g + 9472 g^2)
  + a^2(51712 b^3/9 + 34304 b^2 g/3 + 5632 b g^2 + 512 g^3)
  + a(35840 b^4/81 + 1408 b^3 g/27 - 1216 b^2 g^2
      - 704 b g^3/3 + 576 g^4)
  + 3904 b^3 g^2/9 + 13024 b^2 g^3/9 + 4768 b g^4/3 + 576 g^5.
```

Subtract from P the two nonnegative polynomials
`608 b^2 g(a-g)^2` and `(352/3) b g^2(a-g)^2`. Every remaining monomial
coefficient is nonnegative. This proves P>=0 on the full domain. The audit
reconstructs the rational identity and every coefficient exactly. Equality
at a=g=0 gives the displayed witness.

## 6. Consequence for a full-class CE comparison

The later `SUM_PARITY_LOSS_RANGE_RATES.md` strengthens the connection through
a direct loss-discrepancy inequality and proves distinct noisy/deterministic
CE rate exponents. The elementary comparison below remains a valid bound.

For noisy parity with correct-label probability p=1-eta>=1/2, let r_x be the
model's correct-label probability. The discrepancy bound gives
`mean r_x<=1/2+D_d(R)/2^d`. Convexity of Bernoulli CE therefore proves

`L >= CE(p, min(p, 1/2+D_d(R)/2^d))`.

At d=3, R=4, eta=1/4, every SUM program consequently obeys

\[
L\ge-\tfrac34\log(161/320)-\tfrac14\log(159/320).
\]

This is a proved lower bound, not an assertion that the CE optimum shares the
discrepancy maximizer. A finite native four-PRODUCT graph reaches Bayes at the
same range: form complementary two-bit parity indicators with
`e=(x_0+z_1)(x_1+z_0)` and `o=(x_0+z_0)(x_1+z_1)`, then form
`E=(e+w_1)(o+w_0)` and `O=(e+w_0)(o+w_1)`. Complementarity eliminates the
two contradictory terms in each product, giving exact three-bit parity
indicators. Read out M_0=1+2E and M_1=1+2O. Four is an upper count here;
minimal PRODUCT count for this task is not proved by this construction.

The comparison uses the strongest declared SUM class. Acquisition, registered
value dynamics, resource ownership, fresh persistence and reference/AMP
installation remain independent obligations. No static extremizer or
symmetrized mass table can bypass them.

Exact audit: `theory/numerical_checks/sum_parity_range_audit.py`.
