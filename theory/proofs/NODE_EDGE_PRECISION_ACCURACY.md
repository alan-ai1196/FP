# Node, edge and direct precision costs at a nonattained cap

Status: **PROVED RESOURCE SEPARATION AND MATCHING ORDERS; EXACT AUDIT**,
2026-09-12. Total node count can be sharpened to an additive-constant law,
but its simplest optimal-leading-term construction has an enormous SUM
arity. A different positive construction simultaneously uses few edges and
the optimal order of direct numerical storage. Small arithmetic graphs do
not remove a precision lower bound forced by a critical mass.

## 1. The class and the separately priced resources

Retain the complete class in `DYADIC_CAP_AND_TOTAL_COMPLEXITY.md`: all
binary unary indicators on the complete d-bit domain, d>=1, N=2^d,
positive rational k-label target Q, base one, local SUM weights {1/2,1,2},
binary shared PRODUCTs and a finite rational cap R. Assume its **LIMIT_ONLY**
branch: R is the largest reciprocal row minimum and at least one critical
forced mass R*Q is nondyadic. All statements concern a fixed complete known
target, with target-dependent construction constants retained.

Let C=S+P count native SUM and PRODUCT nodes before fixed base/normalization.
Let E count incoming edges with multiplicity: a repeated SUM parent counts
again, and a square has two incoming edges. These are different resources.
Neither an arbitrarily long parent list nor a generated numerical scalar
is an additional free coefficient in the local alphabet.

For a nonzero dyadic v write v=a*2^e with positive odd integer a. Its direct
significand width is b(v)=bit_length(a). A concrete exact encoding can store
the zero/nonzero flag, a, the exponent sign and the binary magnitude of e;
its length is b(v)+O(1+log(1+|e|)). Define numerical bit volume V by summing
these lengths for **all native node values at all N contexts**, together
with the fixed head masses and normalizers. It is a full materialization
measure, not a lower claim on liveness-optimal device memory. Including
exact rational predictions adds numerator/denominator lengths and does not
change the proved upper order. Graph syntax and the known target encoding
are charged separately.

## 2. The total-node leading term is exactly one

Write the feasible ideal excess table as

`c_(x,j)=Q_(x,j)/min_l Q_(x,l)-1 >= 0`.

For integers s>=1 and p>=0, form a constant seed 2^(-s) by s halving SUMs
from the ordinary source-pair SUM for one. Square it p times. The result is

`u=1/D`, `D=2^(s*2^p)`.

Construct the singleton prefix bank with P_0=2N-4 PRODUCTs, and apply u to
each singleton with one further PRODUCT. In head j, add
`floor(D*c_(x,j))` copies of the scaled singleton of x, each with weight one.
This is an actual finite parent list. It gives

`M_(x,j)=1+floor(D*c_(x,j))/D <= 1+c_(x,j)`.

Every finite candidate respects cap R and activation cap max(1,R-k).
Each row loses less than k/D total mass; since its final total is at least
k, prediction error is at most 1/D. The exact counts of this declared
construction, including empty final SUMs, are

`S=s+k+1`, `P=p+P_0+N=p+3N-4`.

Consequently, for all budgets with P>=3N-4, there is the sufficient envelope

`S <= k+1+max(1,ceil(2^(-(P-3N+4))*log2(1/delta)))`.

The existing complete-class necessary condition is

`S*2^P >= log2(1/(B*R*delta))`,

where B is a common denominator of Q. These describe the separate-budget
accuracy envelope up to fixed target/domain construction overheads. They
do not settle the exact Pareto curve or the smaller-P branches.

Taking s=1 and p=ceil(log2(log2(1/delta))) gives

`C_Q(delta) <= ceil(log2(log2(1/delta)))+3N+k-2`.

The lower from the preceding proof is
`C_Q(delta)>=1+log2(log2(1/(B*R*delta)))` at sufficiently small delta.
Thus, **when edges are not charged**, the complete node optimum satisfies

`C_Q(delta)=log2(log2(1/delta))+O_Q,d,k(1)`.

The coefficients remain local; it is the parent list that grows. If
K=sum_(x,j)c_(x,j)>0, its readout edge count lies between D*K-N*k and D*K.
For s=1 and p tending to infinity, total E=Theta_Q(D). Every produced mass
is on the grid 1/D. Since exact prediction is impossible, the rational
probability separation also gives error >=1/(B*R*D). Therefore along this
family, **E=Theta_Q(1/error)**. Compressing an integer repetition count in
the graph description does not make those repeated physical additions
free, nor does it turn the count into a legal single local SUM weight.

This is an upper witness and a matching node lower, not a theorem that
every optimal-leading-term graph must have so many edges.

## 3. One shared reciprocal gives few nodes and few edges

A common denominator improves the earlier per-coefficient geometric
construction. Choose a positive integer D_0 clearing every c_(x,j), and
put a_(x,j)=D_0*c_(x,j), a nonnegative integer. On the LIMIT_ONLY branch
D_0 is not a power of two. Let H be the smallest power of two at least D_0,
and set t=1-D_0/H, so 0<t<1/2. Construct the dyadic constants

`g_0=1/H`, `t_0=t`

using actual local SUMs from one. Perform n positive updates

`h_i=g_i*t_i`, `g_(i+1)=g_i+h_i`,

and square `t_(i+1)=t_i*t_i` between updates. Omit the final tail square.
The invariant is

`g_n=(1/D_0)*(1-t^(2^n))`.

This form costs one SUM and at most two PRODUCTs per update; it never
constructs the factor 1+t_i above one. All generated values stay <=1.
Apply g_n to each native singleton with a counted PRODUCT. Multiply that
scaled singleton by each fixed integer a_(x,j) using binary Horner SUMs,
then add the head terms using binary SUMs. These integer multipliers take
fixed target-dependent work; they are neither arbitrary local weights nor
new primitive sources. All SUMs in the construction have arity at most two.

Put tau=t^(2^n), and T*_x=sum_j(1+c_(x,j)). Then exactly

`M_n=1+(1-tau)*c`,
`q_(n,x,j)-Q_(x,j)=tau*(1-k*Q_(x,j))/(T*_x-tau*(T*_x-k))`.

Thus error is Theta_Q(tau), as at least one row is nonuniform. Cap R and
the node activation cap max(1,R-k) hold for every finite n. The growing
part has **2n-1 PRODUCTs and n SUMs**, with all remaining work independent
of n. It follows that one family simultaneously has

`C <= 3*log2(log2(1/delta))+O_Q,d,k(1)`,
`E=O_Q,d,k(log log(1/delta))`.

The complete lower makes both C and E Theta(log log(1/delta)) in optimal
order: along the output ancestry, each useful non-source node has an
incoming edge, and the same denominator lower can be applied after
discarding dead work. Empty zero SUMs can be shared in this static graph
class; at most one such node is needed and has no effect on the order.
This is not a Runtime equivalence or a license to erase provenance.

The coefficient three in this bounded-arity construction is **not claimed
optimal**. A lower bound separating its leading constant from the
unpriced-arity optimum remains open.

## 4. A critical nondyadic mass forces precision, at any node budget

Choose a critical row x and a label j with

`r=R*Q_(x,j)=A/B_r` in lowest terms, nondyadic.

For any candidate dyadic mass row with M_l>=1, T<=R and prediction error
at most delta, a minimum-probability label l_0 satisfies

`1/T <= q_(l_0) <= 1/R+delta`.

Therefore `R/(1+R*delta)<=T<=R`, and

`|M_j-r| <= T*delta+Q_j*(R-T) <= R*(1+r)*delta`.

If b=b(M_j), then M_j>=1 implies its reduced denominator is at most
2^(b-1), even when its binary exponent is not bounded. Since r is
nondyadic, M_j!=r and rational separation gives

`|M_j-r| >= 1/(B_r*2^(b-1))`.

Combining them proves the explicit complete-candidate bound

`delta >= 2^(1-b)/(B_r*R*(1+r))`.

Hence **direct mass significand width is Omega(log(1/delta))**, regardless
of node count, sharing, arity or available exponent range. If each stored
mass has at most b bits, this formula gives a positive accuracy floor.
It concerns mathematical normalization of those masses. A final rounded
probability can equal a dyadic target while hiding the nonzero mass-level
gap; output equality alone is not an arithmetic or bridge certificate.

The same order already holds for a critical **excess** value when the mass
is not materialized. Here c=r-1>0 is nondyadic. Put L=R*(1+r). For
delta<=c/(2L), the excess e=M_j-1 is at least c/2 and within L*delta of c.
A b-bit dyadic e then has denominator at most 2^(b+1)/c, so

`delta >= c/(2*B_r*L*2^b)`.

Thus bypassing a separate base-add storage slot does not remove the lower
for a directly represented excess head. Symbolic sums, expansions and
multi-component representations require their own encoding/resource
analysis; they are not implicitly identified with one b-bit number.

## 5. The optimal numerical bit-volume order is also attained

In the shared reciprocal graph, the exact denominators and numerator bit
lengths of g_i,t_i,h_i are O_Q(2^i). There are O(1) such values per stage
and a fixed finite context domain. Their total direct bit length is
therefore O_Q(sum_(i<=n)2^i)=O_Q(2^n), including exponent encodings.
The fixed number of final context/target operations adds O_Q(2^n) bits.
The graph uses O(n) edges whose explicit parent indices cost O(n log n)
bits, also dominated by O(2^n). Target and seed encoding costs are fixed.

Since error is Theta_Q(t^(2^n)), this is O_Q(log(1/error)). The precision
lower gives the reverse inequality for the full materialization volume.
Thus the same family simultaneously attains

`C=Theta(log log(1/delta))`,
`E=Theta(log log(1/delta))`,
`V=Theta(log(1/delta))`.

This is a joint achievable order, not an unavoidable node-versus-storage
tradeoff. The optimal-leading-term high-arity family is simply a different
point whose edge count is much worse. In particular the node theorem
does not imply double-logarithmic total information or bit-time costs.

The precision floor also yields a uniform-context CE floor by
`CE>=2*delta^2/N`. The shared reciprocal construction attains the matching
orders in inverse CE tolerance. Exact arithmetic storage bounds do not
certify the errors of a fixed AMP execution: rounding, underflow, interval
propagation, optimizer reachability and reference/physical lineage remain
separate obligations. No new FP semantic action is introduced.

## 6. Joint cap slack and accuracy: an exact positive tail repair

Now let R_0 be the original nonattained minimum cap, permit cap R_0+h
with 0<=h<=1, and ask for error at most delta. The target Q remains fixed.
Both h and delta may tend to zero, with h+delta>0. For any critical
nondyadic r=R_0*Q_j, the preceding normalizer argument becomes

`|M_j-r| <= (R_0*(1+r)+1)*(h+delta) = K_r*(h+delta)`.

Indeed T>=R_0/(1+R_0*delta), T<=R_0+h, and
`|T-R_0|<=h+R_0^2*delta`. For every local graph its mass grid has
denominator dividing 2^(S*2^P), and M_j can never equal nondyadic r.
Thus even **exact prediction at positive slack** obeys

`h+delta >= 1/(B_r*K_r*2^(S*2^P))`.

The earlier total-node and direct precision lower bounds follow with
delta replaced by h+delta and fixed constants changed. In particular,
precision cannot remain bounded as exact realizations approach the
nonattained cap, although every strictly positive slack allows exactness.

For the node-only upper at positive slack, write each row Q=a/A with
primitive positive integers a and m=min a. On the dyadic grid 1/D choose
`v=ceil(D/m)/D` and masses M_j=a_j*v. These are dyadic, at least one,
and exactly normalize to Q. Their total is <=R_0+A/D. Hence D>=max_x A_x/h
suffices. The corresponding excesses have nonnegative integer numerators,
so the actual repeated-edge construction of section 2 applies unchanged.
Use this exact construction if h>=delta; otherwise use the previous
below-cap approximation. Together with the lower this proves

`C_Q(h,delta)=log2(log2(1/(h+delta)))+O_Q,d,k(1)`.

Few edges and optimal bit volume can also be retained in the exact-slack
branch. In the shared reciprocal construction, **keep the final tail
square**, so both g_n and tau=t^(2^n) are available. Write a_(x,j)=D_0*c_(x,j)
as before, and construct the excess entirely with positive operations:

`E_(n,x,j)=a_(x,j)*g_n+(D_0+a_(x,j)-1)*tau`.

Every integer multiplier is nonnegative and implemented by the declared
local Horner SUMs. Both computed scalars are applied to native context
indicators with counted PRODUCTs. The invariant D_0*g_n+tau=1 gives

`1+E_(n,x,j)=(1+(D_0-1)*tau)*(1+c_(x,j))`.

This is **exact conditional prediction**, with all row normalizers retained
and maximum total `R_0*(1+(D_0-1)*tau)`. Choose n so that
`R_0*(D_0-1)*tau<=h`. No subtraction, internal normalization or additional
semantic action is used. The apparently subtractive base adjustment has
been derived into nonnegative integer coefficients before construction.

The growing work is now 2n PRODUCTs and n SUMs. All other counts depend only
on the fixed complete target. Positive partial outputs stay below their
final excesses, so the actual cap R_0+h and activation cap
max(1,R_0+h-k) hold. This family has n=log2(log2(1/h))+O_Q(1), binary SUM
arity, and direct bit volume O_Q(log(1/h)). Combining the two branches
gives simultaneous optimal orders

`C,E=Theta(log log(1/(h+delta)))`, `V=Theta(log(1/(h+delta)))`.

This settles the joint **orders**, and the unpriced-edge node leading term,
over growing finite P,S. It does not improve a fixed-P threshold. In terms
of uniform-context CE tolerance rho, replace h+delta by h+sqrt(rho);
Pinsker and the finite-cap chi-square upper justify both directions.

### A unified PRODUCT/SUM/range/precision budget envelope

The same proof can be stated directly in separate budgets. Let
epsilon=h+delta, let A_max be the largest primitive row sum A_x, and set

`L=ceil(log2(2*max(1,A_max)/epsilon))`,
`S_0=k+1`, `P_0=3N-4`, `B_0=ceil(log2(R_0+1))+1`.

The complete necessary inequalities are

`S*2^P >= log2(1/epsilon)-O_Q(1)`,
`b >= log2(1/epsilon)-O_Q(1)`

for direct mass significand budget b. Conversely, if

`S>=S_0+1`, `P>=P_0`,
`(S-S_0)*2^(P-P_0)>=L`, `b>=2*L+B_0`,

there is a native candidate meeting the requested range and error, provided
its repeated edges and exponent range are available. To prove it, choose

`p=min(P-P_0,ceil(log2 L))`, `s=ceil(L/2^p)`.

Then s<=S-S_0 and L<=s*2^p<=2L. The grid construction has exactly the
counted S/P overheads and all positive values lie on the grid
2^(-s*2^p). Every native value, mass and total is at most R_0+1, so the
displayed b bound suffices for **exact direct storage**. A format whose
normal exponent range includes [-2L,ceil(log2(R_0+1))] suffices; a finite
hardware format cannot assume that range. Choose the exact upward row
scales if h>=delta, and the below-cap approximation otherwise.

These are matching upper/lower envelopes up to fixed construction overheads
and precision constants. They do not require P to be fixed while precision
changes. Their upper explicitly prices actual E when used in a complete
resource claim. For a small-edge budget, the shared reciprocal/tail-repair
family instead supplies the simultaneous C,E,V orders above; an arbitrary
S/P allocation with a small E cap is not certified by the unpriced-edge
envelope. Sharp constants and low-budget exceptions are not needed to
freeze that distinction in the experiment contract.

## 7. Audit and remaining questions

The audit evaluates actual local-alphabet DAGs on every binary context,
counts repeated incoming edges, checks the exact dyadic grid, compares a
single shared reciprocal across distinct rational coefficients, records
direct significand/exponent volume, verifies the positive tail repair at
its declared slack, rejects an insufficient-slack execution, and checks precision bounds
against exact small floating mass rows with arbitrary signed exponents.
An exact reconstruction of a binary64 rounded-equality example exposes
the retained nonzero error. Evidence contains only counts, bounds and a
small set of example records, never the enormous repeated-parent graph.

Sharp bounded-arity leading constants, exact low-P Pareto phases, optimal
bit-time/liveness/alternative encodings and registered physical/AMP paths
remain open. The resource theorems apply to the stated complete static
class, not to every possible numerical representation or Runtime state.

Audit: `theory/numerical_checks/node_edge_precision_accuracy_audit.py`.
Evidence: `evidence/minimal/FP_NODE_EDGE_PRECISION_ACCURACY_AUDIT.json`.
