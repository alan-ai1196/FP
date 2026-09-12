# Complete dyadic cap boundaries and total-node accuracy cost

Status: **PROVED CLASSIFICATION AND SHARP ASYMPTOTIC ORDER; EXACT AUDIT**,
2026-09-12. On the complete binary source domain, a rational target's exact
local-alphabet cap boundary is decided row by row. Its nonattained boundary
has total SUM-plus-PRODUCT complexity Theta(log log(1/delta)), when both
node budgets may grow. This does not decide a fixed-PRODUCT subproblem.

## 1. Complete static class

Use all 2d unary indicators on the complete d-bit cube, d>=1. Fix k>=2
labels, base one in each head, one final normalization, a strictly positive
rational target table Q, and a finite rational normalizer cap R. Every SUM
coefficient belongs to {1/2,1,2}. A SUM may have arbitrary finite arity,
including repeated parents. Scalar PRODUCTs are binary, arbitrary sharing
is allowed, and every graph is finite. No additional sources or recurrence
are available. Let S and P count all weighted SUM and PRODUCT nodes up to
the final excess heads, and let C=S+P. Source and fixed readout stages are
separate. Both S and P are unrestricted in the membership classification.

The complete target table is given. Construction costs depending on its
size and coefficient encoding are retained, not acquired from a sample or
provided by a value oracle. This is an extensional static function class;
the construction is not a registered optimizer/physical/AMP path.

Every context singleton is available through a finite native graph. Share
binary prefixes: the first-coordinate indicators are sources; extending
each prefix by the next coordinate costs one PRODUCT. The full bank uses
`2^(d+1)-4` PRODUCTs and no SUMs. These are constructed features, not extra
primitive sources. The constant one, when needed, is one ordinary SUM of
the two first-coordinate source indicators.

## 2. An exact cap and local-arithmetic classification

Define the row minimum cap and the full minimum cap by

`r_x=1/min_j Q_(x,j)`, `R_0=max_x r_x`.

Call row x critical when r_x=R. For R>=k the complete alternatives are:

1. **R<R_0:** Q is outside prediction closure. A minimum-probability entry
   has the positive error gap `1/R-min_(x,j) Q_(x,j)` because every finite
   candidate has q_(x,j)>=1/R.
2. **R>=R_0 and every critical mass R*Q_(x,j) is dyadic:** Q has a finite
   exact local-alphabet graph.
3. **R=R_0 and at least one critical mass is nondyadic:** Q is in closure
   but has no finite exact local-alphabet graph, at any PRODUCT count.

For R<k the candidate class is empty. At R=k only uniform prediction fits,
and it belongs to the exact branch. A dyadic number is an integer divided
by a power of two; its numerator need not be a power of two.

Necessity follows from the base and exact arithmetic. All finite node
values, and hence all masses, are dyadic on binary sources. Exact Q
requires T_x>=r_x. If row x is critical, T_x=R is forced, so its masses
must be exactly R*Q_x. A nondyadic entry therefore excludes every finite
graph, irrespective of hidden topology, sharing, SUM work or PRODUCT count.

For sufficiency, write each rational row as Q_(x,j)=a_(x,j)/A_x using
positive integers with gcd_j a_(x,j)=1 and A_x=sum_j a_(x,j). Put
m_x=min_j a_(x,j). A valid dyadic mass row is obtained by choosing dyadic
t_x in

`[1/m_x, R/A_x]`, then `M_(x,j)=t_x*a_(x,j)`.

At a noncritical row this interval has positive width and contains a
dyadic t_x. For an explicit choice, take 2^(-n) no larger than its width
and round 1/m_x upward to that grid. At a critical row the interval is a
singleton. All required masses a_(x,j)/m_x are dyadic iff m_x is a power
of two: an odd divisor of m_x would have to divide every a_(x,j), violating
their primitive gcd. Thus the preceding mass test is also a finite integer
test on the critical rows.

Every resulting dyadic excess M_(x,j)-1 is nonnegative. Weight the native
singleton of x by this excess using finite halving/Horner SUMs, and sum
the contributions into head j. The complete graph is exact at cap R.
No numerical linear solve, alternative source acquisition or internal
division is needed. The explicit graph need not minimize its finite node
count; the theorem decides existence over all finite graphs.

In particular, **every strict cap slack R>R_0 allows exact local realization**.
The only possible nonattainment is at the minimum cap and is completely
identified by the critical dyadic-mass condition.

For binary labels, the critical masses are 1 and R_0-1. Exactness at the
minimum cap is therefore equivalent to R_0 being dyadic. For three or more
labels the cap alone is insufficient: Q=(1/4,1/3,5/12) has R_0=4 but forced
masses (1,4/3,5/3), so it is nonattained in the local class. A second
critical row with masses (1,3/2,3/2) would not repair that obstruction.

Conversely, do not force noncritical normalizers to the cap. The two rows
(3/4,1/4) and (3/5,2/5) have an exact local graph at R=4 using normalizers
4 and 5/2. Forcing both normalizers to four would introduce nondyadic masses
in the second row and falsely reject the target.

## 3. Every feasible rational target is in local closure at that same cap

Assume R>=R_0. Choose the rational mass table

`M*_(x,j)=Q_(x,j)/min_l Q_(x,l)`.

Each row total is r_x<=R and every mass is at least one. The singleton
bank supplies an exact graph over real/rational coefficients. The local
density theorem from `CONDITIONAL_COEFFICIENT_PATHS.md` already proves
same-cap closure. The construction below quantifies it with growing
PRODUCT count and uses only actual native local-alphabet graphs.

For any positive rational excess coefficient c=a/b in lowest terms, let
H be the smallest power of two at least b and set

`s=a/H`, `t=1-b/H`, so `0<=t<1/2`.

Both s and t are dyadic and require finite SUM construction depending on
c, not on the requested accuracy. If t=0, c is already dyadic and can be
applied exactly to the singleton. Otherwise define

`g_n=s*product_(i=0)^(n-1) (1+t^(2^i))
     =c*(1-t^(2^n))`, n>=1.

Build the constant one from the original unary sources, construct s and t
by dyadic SUMs, then repeat the positive steps

`f=(1+t_i)/2`, `g_(i+1)=2*(g_i*f)`, `t_(i+1)=t_i*t_i`.

The last tail square is unnecessary. Each repetition uses two SUMs and
at most two PRODUCTs. **The computed constant g_n is a graph value**: applying
it to a context singleton requires a further counted PRODUCT. It is not
silently substituted into a free coefficient slot. Equal known coefficient
values may share their constructed constant graph.

Replace each rational excess coefficient by its g_n and retain exact
dyadic coefficients. This gives componentwise smaller masses than M*, so
every finite graph respects the original cap. At each context only its
own singleton contributes. With h=2^(-2^n), the total excess lost is at
most `(R-k)*h`; normalization with a base total at least k therefore gives

`||q_n-Q||_max <= (R-k)*h/k`.

All node activations can be kept <=max(1,R-k): source/indicator values are
<=1, the factors (1+t_i)/2 are <=1, and the positive partial coefficient
products and weighted outputs never exceed their final rational excesses.
The initial dyadic constructor has the same peak property. This bound
refers to sources/SUM/PRODUCT/excess nodes; the fixed positive base is added
afterward as declared.

For fixed Q,d,k,R, the total C is at most A_Q*n+B_Q with finite constants
that include the singleton bank, complete target encoding, dyadic seeds,
constant-to-feature PRODUCTs and final readouts. Thus every feasible rational
target has same-cap approximation with

`C_Q(delta)=O(log log(1/delta))`.

This is an accuracy asymptotic for a fixed known table, not a dimension-free
compression or an efficient method to learn the table. The coefficient
construction may use more PRODUCTs than an earlier fixed-P witness.

## 4. The nonattained branch requires that total order

Let B be a common denominator of Q. The rational bound in
`SUM_ACCURACY_COMPLEXITY.md` applies to every finite candidate on binary
sources: either q=Q or

`||q-Q||_max >= 1/[B*R*2^(S*2^P)]`.

In the nonattained branch exact equality is impossible for every P,S.
For sufficiently small error S must be at least one. At fixed C=S+P,

`S*2^P = 2^C*S/2^S <= 2^(C-1)`.

The maximum S/2^S is 1/2, attained at S=1 or 2. Therefore

`C_Q(delta) >= 1+log2(log2(1/(B*R*delta)))`

for sufficiently small delta. Together with the construction, this proves
the **sharp total-node order Theta(log log(1/delta))** for every nonattained
rational target in this complete source class. No small architecture menu
or bounded-SUM-arity relaxation is used in the lower bound.

Uniform-context CE has the same double-logarithmic order in inverse
tolerance rho. With N=2^d, its lower follows from Pinsker:

`C_Q^CE(rho) >= log2(log2(2/(N*B^2*R^2*rho)))`.

The upper uses q_j>=1/R and the chi-square bound. Constants and the exact
Pareto boundary between S and P are not claimed sharp.

## 5. The total-node trichotomy is now explicitly classified

Let C_Q(delta) minimize S+P over the whole finite local class. The exact
test in section 2 completely selects its asymptotic branch:

- Below R_0 there is a positive gap, or an empty class below k.
- In the dyadic-feasible branch, C_Q(delta) is eventually the minimum
  exact total node count, a finite constant.
- At the nondyadic critical boundary, it is Theta(log log(1/delta)).

For eventual constancy in the second case, fixed C permits finitely many
pairs (S,P). Each pair has finitely many observed mass tables at fixed cap,
as proved in `SUM_ACCURACY_COMPLEXITY.md`. Every budget smaller than the
minimum exact one therefore retains a positive error gap.

This class differs from the earlier fixed-P trichotomy. The three-bit
identity-noise target at cap nine is dyadic-feasible: its explicit prefix
graph has twelve PRODUCTs and no SUMs, the known minimum exact total count.
The exact PRODUCT lower is proved in `DECODER_EXACT_AND_LIMIT_COMPLEXITY.md`.
At a fixed budget P=9, the same task is nonexact but approachable, with
logarithmic SUM cost. An unrestricted-node classification must never be
used to certify the narrower P=9 decision.

## 6. Arithmetic bounds are not numerical execution guarantees

The constructed graph can be small while its exact intermediate values
have long significands. For the earlier c=2/3 example, the direct dyadic
significand has Theta(log(1/error)) bits although node count is only
Theta(log log(1/error)). The theorem does not establish small bit-time,
short encoded target descriptions, passive value acquisition, registered
optimizer reachability, ownership/install feasibility or an AMP bridge.

The complete exact/closure classifier is scoped to known positive rational
tables, binary unary sources, the specified local alphabet, finite final cap
and unrestricted finite P,S. It does not classify fixed-node subproblems,
algebraic/transcendental targets, incomplete source families or additional
resource contracts. Those unsupported decisions remain UNRESOLVED.

## 7. Audit

The exact audit compares the primitive-integer critical-row criterion to
direct forced-mass dyadic checks, evaluates full native exact and geometric
approximation graphs, verifies every normalizer and activation, retains
the actual constant-to-feature PRODUCTs, checks small rational target tables,
and attacks missing critical rows and narrowed decision-class claims.
Only concise reproducible evidence is kept; no target cache or large graph
bundle is an alternative canonical state.

Audit: `theory/numerical_checks/dyadic_cap_total_complexity_audit.py`.
Minimal evidence: `evidence/minimal/FP_DYADIC_CAP_TOTAL_COMPLEXITY_AUDIT.json`.

The follow-up `NODE_EDGE_PRECISION_ACCURACY.md` sharpens the total-node law
to an additive constant, gives a separate P/S/range/precision budget
envelope, and proves simultaneous node/edge/direct-bit orders. A positive
tail repair supplies exact local prediction at positive cap slack. Its
direct precision contract and actual edge costs remain explicit.
