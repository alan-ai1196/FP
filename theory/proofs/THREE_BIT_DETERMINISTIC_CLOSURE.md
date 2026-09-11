# Three-bit closure and the PRODUCT cost of prediction mixtures

Status: **PROVED BRANCH RESULT; EXACT FINITE CERTIFICATES**, 2026-09-12.
Base: `388251d8b05de10536bdf650e4c1a56a2bd46a4b`, after canonical XVII.28.
The analytical lower bounds and the attached finite upper certificates establish
all minima below. This branch supplement has not been promoted into the
normative `FP_THEORY.md`; it does not change the Runtime or science-HOLD status.

## 1. Contract and result

Use the full three-bit cube, its six unary indicators, nonnegative scalar SUMs,
binary scalar PRODUCTs with arbitrary sharing, base one in each of two heads,
and exactly one final normalization. There is no recurrence, extra source,
context-dependent controller, or internal division. Every individual graph and
coefficient is finite. Normalizers and finite SUM work may grow along a sequence.

For a Boolean table f, let A(f) be the least PRODUCT count for which q_1 can
approach f uniformly on all eight contexts. This is a **prediction-closure**
question: the base prevents any finite graph from predicting an exact zero or one.

The complete classification is:

| A(f) | Number of Boolean tables | Characterization |
|---|---:|---|
| 0 | 96 | Literal decision lists, including constants and shorter lists |
| 1 | 158 | All remaining non-parity tables |
| 2 | 2 | Odd parity and its complement |

A literal decision list tests one coordinate value at a time, returns the label
of the first satisfied test, and otherwise returns a final default label. This
is a characterization of the static SUM closure, not a new native model action.

More quantitatively, every three-bit f has a sequence using **its minimum** A(f),
local SUM coefficients only `{1/2,1,2}`, and, for every integer k>=1,

```
probability sup error <= 4*2^(-k),
maximum final normalizer <= 9*2^(5*k),
number of scalar SUM nodes <= 12*k+8.
```

The counts include expanded coefficient-scaling chains, binary additions and a
shared construction of one from a source partition. Final normalization is the
already declared readout, not an added native PRODUCT. These are constructive
upper bounds, not sharp range or physical-cost optima.

## 2. SUM closure is exactly the literal-decision-list class

The following argument works for d bits. Flatten every SUM-only graph into

`M_j(x)=1+sum_(i,b) a_(j,i,b)*1[x_i=b]`, with all a>=0.

### Upper construction

For a list of length ell, give its t-th test, t=1,...,ell, coefficient
`epsilon^(-(ell+2-t))` in its returned label's head. Give the default label
a constant coefficient `epsilon^-1`, using an ordinary unary partition SUM.
Keep the fixed base one in both heads. At any context the first satisfied test
has strictly lower exponent than every later test and the default. If none is
satisfied, the default dominates the base. Hence q_1 tends to the list's f.
No PRODUCT is used; all coefficients are finite for every epsilon>0.

### Complete lower obstruction

Repeatedly remove a nonempty monochromatic literal support from the remaining
contexts, stopping if their labels are constant. If this finishes, the removals
are a literal decision list. If f is not such a list, the procedure leaves a
nonempty core C containing both labels on which **every touching literal support
contains both labels**. Thus the obstruction is a certificate for the whole
SUM class, not just a chosen numerical bank.

Consider any finite SUM program. Let W be the maximum of one and all coefficients
whose literal touches C; ignore coefficients invisible everywhere on C. If a
coefficient achieves W, choose within its support a context whose desired label
is opposite to its head. Such a context exists by the core property. At that
context the incorrect mass is at least W, while the correct mass is at most
`1+d*W <= (d+1)*W`. If W=1 is achieved only by the base, either label at any
context gives the same bounds. Therefore

`||q_1-f||_infinity >= 1/(d+2)`.

In three dimensions this is a uniform **1/5** lower bound, independent of every
normalizer and coefficient. It rules out closure for every non-list f.
The audit independently enumerates all complete three-test lists and all
possible nonempty cores: there are 96 distinct list functions and an explicit
core for each of the other 160. It does not use an optimizer or an SMT UNSAT
answer to establish this lower classification.

## 3. At most one PRODUCT cannot approach parity

With at most one PRODUCT, each complete mass has reduced multilinear degree at
most two, including squares and arbitrary SUM parents. Consequently, for
`chi(x)=(-1)^(x_1+x_2+x_3)`,

`sum_x chi(x)*M_j(x)=0`, and `sum_x chi(x)*T_x=0`.

The T-weighted means of q_1 on the two parity classes are equal. For odd parity
f=(1-chi)/2, the exact identity

`sum_x chi(x)*T_x*(q_1(x)-f(x)) = (1/2)*sum_x T_x`

implies sup error at least 1/2. The complement gives the same bound. This is a
full-class statement that survives arbitrary diverging normalizers, not a
restriction to symmetric or disjoint PRODUCT parents.

For noisy parity p_eta=eta+(1-2*eta)*f, eta in (0,1/2), the same argument gives
sup error at least `1/2-eta`. This agrees with the existing
[`TWO_PRODUCT_CONDITIONAL_PARITY.md`](TWO_PRODUCT_CONDITIONAL_PARITY.md).

## 4. Exhaustive, independently checkable upper certificates

Order contexts as 000,001,...,111 and encode a Boolean table by
`mask=sum_i f(context_i)*2^i`. Input-coordinate permutations, input flips and
output complement preserve PRODUCT count, the source grammar and all bounds.
The following 14 disjoint symmetry orbits cover all 256 masks:

| Representative mask | Orbit size | Certified PRODUCT count |
|---:|---:|---:|
| 0 | 2 | 0 |
| 1 | 16 | 0 |
| 3 | 24 | 0 |
| 6 | 24 | 1 |
| 7 | 48 | 0 |
| 15 | 6 | 0 |
| 22 | 16 | 1 |
| 23 | 8 | 1 |
| 24 | 8 | 1 |
| 25 | 48 | 1 |
| 27 | 24 | 1 |
| 30 | 24 | 1 |
| 60 | 6 | 1 |
| 105 | 2 | 2 |

Here are explicit one-PRODUCT witnesses for the eight non-list, non-parity
representatives. Let t=1/epsilon tend to infinity and use M_j=1+E_j. Every entry
is a native positive SUM or the **single** displayed PRODUCT A; scalar powers
of t are coefficient values, not extra semantic PRODUCT nodes.

| Mask | A | E_0 | E_1 |
|---:|---|---|---|
| 6 | `t*(y_0+z_1) * t*(y_1+z_0)` | `t*x_1+A` | `t*x_0` |
| 22 | `(x_1+t^2*z_1)*(x_1+t^2*y_1)` | `t*y_0+t*A` | `t^2*(x_1+y_1+z_1)` |
| 23 | `(t*x_0+z_0)*(t*y_0+t^-1*z_0)` | `t*(x_1+z_1)` | `t*A` |
| 24 | `(t*x_0+t*y_1+z_1)*(x_1+t*y_0+t*z_0)` | `A` | `t*(x_0+z_0)` |
| 25 | `t*(y_1+z_1)*(x_1+t*y_0+t*z_0)` | `A` | `t*(x_0+z_0)` |
| 27 | `t*(y_0+z_1)*t*(x_0+z_0)` | `t*(x_1+z_0)` | `A` |
| 30 | `t*(y_1+z_1)*t^2*x_0` | `t^2*x_0+t*y_1+t^2*z_1` | `t*y_0+A` |
| 60 | `(x_1+t*y_1)*t*(x_0+y_0)` | `t*(x_0+y_1)` | `A` |

The five zero-PRODUCT representatives have the excesses

```
0:  E_0=t*(z_0+z_1),                E_1=0;
1:  E_0=t^2*(x_1+y_1+z_1),          E_1=t*x_0;
3:  E_0=t^2*(x_1+y_1),              E_1=t*y_0;
7:  E_0=t*x_0+t^3*x_1,             E_1=t^2*(y_0+z_0);
15: E_0=t*x_1,                     E_1=t*x_0.
```

For odd parity, build two shared nodes

`A=(x_1+y_1)*(x_0+y_0)`, `B=A*z_1`,

and use `E_0=t*z_0+t^3*B`, `E_1=t*z_1+t^2*A`. In effective contexts
(A,z)=00,01,10,11 the dominant labels are respectively 0,1,1,0. Swapping heads
gives representative 105 (even parity); odd parity itself is mask 150.
The XOR value A is constructed by an ordinary PRODUCT, not imported as a source.

### Why these are certificates, rather than sampled successful fits

Every mass expands into a finite Laurent polynomial with nonnegative integer
coefficients. For each representative and every context, the smallest exponent
in the correct head is at least one below the smallest exponent in the wrong
head. If c is the correct leading coefficient and B is the sum of wrong-head
coefficients, then for 0<epsilon<=1,

`1-q_correct <= (B/c)*epsilon`.

The supplied exact verifier checks these exponent inequalities by two separate
methods, retains all tied coefficients, and independently expands and evaluates
every native rational graph. Across all representatives B/c<=4. Every mass term
has exponent at least -5, and the sum of coefficients across both heads is at
most nine at each context. Thus `T_x<=9*epsilon^-5` without a numerical fit.
The input/output transformations transfer the proofs to every Boolean table.

Set epsilon=2^-k. Implement each coefficient epsilon^w by abs(w)*k unary SUM
scalings with local weight 1/2 or 2, then combine terms with binary unit-weight
SUMs. No PRODUCT is added. The audit executes those expanded graphs, and their
largest count is `12*k+8`. Choosing `k=ceil(log2(4/delta))` gives the stated
accuracy with logarithmic SUM construction and a finite, explicitly charged
normalizer upper bound. No unknown coefficient or registered optimizer path is
being granted by this known-table construction.

## 5. Finite SUM prediction mixtures can force growing PRODUCT complexity

This phenomenon does not require any component to be a boundary limit.
For every d>=1 there are `2^(d-1)+1` **finite, strictly positive, zero-PRODUCT**
conditional tables, each with normalizer at most `3*(d+1)`, whose convex
mixture cannot be approximated with fewer than `ceil(log2(d))` PRODUCTs.
The exclusion margin is explicit but decreases with dimension.

### Native components and their exact mixture

For each odd-parity vertex v, define the positive SUM program

```
M_(v,0)(x)=1+3*Hamming(x,v),    M_(v,1)(x)=2,
g_v(x)=2/[3*(1+Hamming(x,v))].
```

Hamming distance is just the SUM of d mismatching unary indicators. Thus each
component is an actual native zero-PRODUCT graph, and its normalizer is at most
3*(d+1). Let K=2^(d-1), let gbar be the equal-weight average of these K
probability tables, and define

`m=(4-2^(1-d))/[3*(d+1)]`, `h=1-m`.

Here h is a constant SUM prediction, realized by masses `M_0=1`,
`M_1=(1-m)/m`. Since 0<m<=1/2, both masses are at least one and the normalizer
1/m is also at most 3*(d+1). Consider the convex mixture of **predictions**

`p=(1/2)*h+(1/2)*gbar`.

This defines a target table; it does not add a mixture primitive to FP.

Distances from x to the odd vertices have even parity when x is odd and odd
parity when x is even. Therefore gbar has only two values, whose difference is

```
gbar_odd-gbar_even
 = (2/(3*K))*sum_(r=0,...,d) (-1)^r*binom(d,r)/(r+1)
 = 2/[3*K*(d+1)].
```

The alternating identity follows by integrating (1-t)^d over [0,1]. The
corresponding nonalternating binomial identity, obtained by integrating
(1+t)^d, gives the midpoint m above. Consequently the mixture is exactly

`p(x)=1/2+a_d*(2*parity(x)-1)`, `a_d=1/[3*2^d*(d+1)] > 0`.

With P scalar PRODUCTs, reduced mass degree is at most 2^P even with arbitrary
sharing, nesting and squares. If 2^P<d, the top parity moment of both masses
and their total is zero. The argument of section 3 then gives the
cap-independent bound `||q_1-p||_infinity >= a_d`. This proves the stated
necessary PRODUCT count for both exact representation and approximation.

For d=3, h=11/16 and the five finite components have mixture weights 1/2 and
four copies of 1/8. The target is 47/96 on even contexts and 49/96 on odd
contexts. At most one PRODUCT has sup gap **1/96**, whereas the existing
parity construction with r=49/47 realizes the mixture exactly with two
PRODUCTs (its explicit cap is 239520/103823). The constituent normalizers
are all at most twelve. Thus the **finite** SUM and one-PRODUCT prediction
classes are not convex, and neither are their closures.

The lower bound grows with d; its margin a_d does not stay constant. The number
of mixture components is exponential, and no free mixture execution, favorable
information cost or practical learning advantage is claimed.

### A larger-gap boundary comparison

Let h be the constant-one table and, for each of the four odd-parity contexts v,
let s_v be its singleton indicator. Each h and s_v is a literal decision list,
so all five belong to SUM prediction closure. Their convex combination

`p=(3/7)*h+(1/7)*sum_(v odd) s_v`

is strictly positive, with p=3/7 at even contexts and p=4/7 at odd contexts.
Section 3 excludes every at-most-one-PRODUCT approximation by a sup gap **1/14**.
The existing two-PRODUCT parity witness with r=4/3 realizes p exactly at cap
**133/27**. The audit independently checks all eight probabilities and that cap.
Therefore this mixture has exact and approximation PRODUCT minimum two.

Both examples expose the same missing operation. Mixing normalized predictions
is not free positive-SUM closure:

`sum_a lambda_a*M_(a,j)/T_a`

is generally not the normalization of `sum_a lambda_a*M_(a,j)`. The missing
context-dependent scales cannot silently be supplied as readout coefficients.
This is an obstruction to an argument, not a new model operation.

## 6. What this resolves, and what it does not

The deterministic-support frontier for binary three-bit targets is now complete.
No such boundary label pattern can prove a requirement of three PRODUCTs at
unrestricted normalizer range. The result does **not** settle whether every
strictly positive eight-row binary table needs at most two PRODUCTs: their
probability amplitudes and compatible shared normalizers remain substantive.
Mixed support patterns, with some deterministic rows and some two-positive-head
rows, are not exhaustively classified here: they form a separate 3^8-pattern
decision problem. The 256-table result must not be reported as solving that
larger support class. Containing every deterministic vertex in closure does not prove interior
universality without a closure-under-mixing theorem; section 5 demonstrates
why such a step cannot be assumed from the native SUM syntax.

The canonical `2 <= A(3,2) <= U(3,2) <= 3` bounds for arbitrary strictly positive
tables remain unchanged. Fixed-cap phases are also unchanged; deterministic
limits necessarily leave every finite cap because each finite q_j>=1/R.
No recurrence/state quotient, acquisition transcript, trained value profile,
Runtime installation, fresh persistence or reference/AMP bridge is established.

## 7. Reproduction and evidence

Run from the repository root:

```text
python theory/numerical_checks/three_bit_deterministic_closure_audit.py --write
```

The audit requires only the Python standard library. It checks 256 truth tables,
14 disjoint symmetry orbits, 160 independent SUM-obstruction cores, 6,144 exact
native context evaluations, 768 actually expanded finite-alphabet graphs,
240 exact one-PRODUCT moment cases (including squares), and rejects 31 invalid
or replayed certificates. It also checks all finite-mixture target rows through
dimension eight, 43,690 actual component/context evaluations and the alternating
identity through dimension twelve. Solver proposals were used during exploration; no
solver dependency or solver UNSAT answer is needed by the committed proof audit.
Finite tests audit the analytic theorem; they do not replace its whole-class
lower arguments. Repeated output must be byte-identical.

Minimal evidence: `evidence/minimal/FP_THREE_BIT_DETERMINISTIC_CLOSURE_AUDIT.json`.
