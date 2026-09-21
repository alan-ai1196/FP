# Reachable boundary information: exact code laws and a precision counterexample

Status: **PROVED SCOPED LAWS; EXACT ENUMERATION AND OWNED CPU AUDITS PASS**.

The [finite-future theorem](QUERY_BOUNDARY_RESPONSE.md) gives the exact
response coordinates for h future observations on b boundary vertices:

`D = D_h(b) = SUM_(k=1)^min(h+1,floor(b/2)) binom(b,2k)`.

The [reachable pure-interaction construction](REACHABLE_BOUNDARY_MESSAGES.md)
showed that its strict horizon hierarchy occurs inside the native count
learner. This proof goes further. Independent legal count choices realize
L^D distinct h-response classes at one common observation clock, in one
fixed native program with the same queries. Their exact deterministic
code length is ceil(log2(L^D)) bits under the declared isolating interface.

This is a matching upper/lower law for the constructed family. It is not
a universal precision upper bound from D. An explicit n4 family below has
b2, D=1 and exactly binom(L+1,2) boundary classes at clock T=8L. Thus the
number of exact boundary classes need not be O(T^D), even for fixed n.

## 1. Same program, queries and clock for an independent count grid

Fix b>=2, h>=0 and integer L>=2. Let F be the D nonempty even subsets S of
the boundary with |S|<=min(2h+2,b). Give each S a coordinate
`t_S in{0,...,L-1}`. For each pair S, use its direct boundary edge.
For every larger S of size r, reserve a disjoint collection of2^(r-2)
additional vertices. Connect them to S using the sign patterns with first
sign+1 and total product+1 in the preceding construction. The native
vertex count and the number of potentially nonzero count edges are

`n = b + SUM_(S in F, |S|>=4) 2^(|S|-2)`,
`E = binom(b,2) + SUM_(S in F, |S|>=4) |S|*2^(|S|-2)`.

All vertices belong to the original full relation G, with its uniform
initializer Gamma and unit simplex update U. No graph is installed or
rewired. The displayed edges are posterior count factors inside that G.
The program and all ordinary source meanings are fixed across t.

On an edge of sign s associated with S, declare L-1 consecutive query
pairs, each consisting of two observations of that edge. In the first
t_S pairs use labels(0,0) if s=+1 and(1,1) if s=-1. In the remaining pairs
use(0,1). A direct boundary edge has s=+1. The resulting signed edge count
is exactly2*t_S*s. Every history therefore has the same ordered queries,
clock and commit count

`T = 2*(L-1)*E`.

All label words have positive probability. The
[native count identity](COUNT_LEARNER_ENCODING.md) proves reachability
from the common initializer; these are not uploaded states. Pairs of
opposite labels cancel only in the posterior count parameterization. The
actual histories, observations, work and clocks are not erased.

For fixed b,h, the program size n is independent of L and T. Its potentially
large n and the costs of planning, exact arithmetic, history/evidence and
explicit native output remain real obligations. The theorem is a finite
semantic family, not a claim that every b,h,L fits one physical registration
or the current indexed n<=1024 guard. Only the n8 histories below are
reported as actual Runtime executions.

## 2. The discrete natural parameters are independently distinct

For each S, marginalizing its private additional vertices gives a positive
factor that depends only on `chi_S=PRODUCT_(i in S) sigma_i`. Write its
values at chi_S=+1,-1 as A_r(t), B_r(t). For r=2 they are9^(2t),1.
For r>=4, the earlier binomial product formula applies with

`f_j(t) = 9^(2t*j) + 9^(2t*(r-j))`.

At t=0 both parity responses agree. The same exact valuation argument gives

`v3(A_r(t)/B_r(t)) = 4*t*(-1)^(r/2)*binom(r-2,r/2-1)` for r>=4,

and4t for r=2. The coefficient of t is nonzero, so each r gives L distinct
positive rational ratios. This conclusion uses the fixed likelihood
ratio9 and discrete legal counts, not a generic real coupling argument.

Independence of the private interior sums implies that the complete
boundary distribution is

`mu_t(sigma) = exp(SUM_(S in F) eta_S(t_S)*chi_S(sigma)) / Z(eta(t))`,
`eta_S(t) = (1/2)*log(A_|S|(t)/B_|S|(t))`.

The exponential notation is for the proof. The actual distribution is
computed by positive integer products and sums; no logarithmic primitive,
negative native source, new update or regularizer is introduced.
Every distinct grid word gives a distinct natural parameter vector eta.

## 3. Distinct grid words have distinct h-future responses

Define `psi(eta)=log SUM_sigma exp(SUM_S eta_S*chi_S(sigma))` on anchored
boundary assignments. Its gradient is the vector of the D selected moments.
Its Hessian is their covariance matrix. For any nonzero vector c,

`c^T Hessian(psi) c = Var_mu[SUM_S c_S*chi_S] > 0`.

The strict inequality holds because the selected nonconstant even
characters and the constant character are linearly independent on the
anchored assignments, and every assignment has positive probability.
Integrating this positive quadratic form along a segment proves

`(eta-eta') dot (grad psi(eta)-grad psi(eta')) > 0` whenever eta!=eta'.

Thus the selected moment vectors differ for every distinct grid word.
By both directions of the finite-future theorem, there are exactly L^D
h-response classes in this constructed family. This supplies a native
reachable family attaining the earlier information lower bound. It does
not assert reachability of the particular linear Fourier-perturbation
grid used in the earlier arbitrary-message proof; the family here is a
different, reachable exponential family.

## 4. Exact code law and its resource scope

Declare an isolating cut at T with the common b,h,L,G,Gamma,U and query
schedule fixed. After the cut the receiver must reproduce every forecast
after at most h common boundary observations. Interior queries, direct
parameter access and the old history are unavailable except through the
code. All recoverable side information that varies with the grid word is
part of the code. Use a fixed-width deterministic code, or a prefix code
with its lengths included.

There are L^D pairwise distinguishable states, so at least
`ceil(log2(L^D))` bits are required in the worst case. Conversely, encode
the D digits t in base L, reconstruct the count family and execute its
declared positive response on the supplied continuation. This uses exactly
that many persistent input bits. Thus

`B_family = ceil(log2(L^D))`.

The upper bound does not say reconstruction, arithmetic, future inputs or
temporary storage are free. It is a code-length statement about the
declared response object, not a complete Compiler resource equivalence.
The actual Runtime retains full counts, lineage, histories and evidence.
Since T=2E(L-1), for fixed b,h this constructed family has exactly
`(1+T/(2E))^D` classes on its registered clock sequence. That exponent D
is attained; it is not a bound on all other count-reachable families.

## 5. One response coordinate can contain quadratically many count classes

Keep only two boundary vertices0,1 and two additional vertices2,3 in a
fixed n4 native program. For integers a,b in{1,...,L}, use signed counts
2a on(0,2),(1,2) and2b on(0,3),(1,3), with the other counts zero.
For each of these four edges use L two-observation slots: the first a or b
slots have labels(0,0), the rest(0,1). Every history has the same queries
and clock `T=8L`.

Put q=81. Summing the two private interior spins gives boundary parity odds

`R(a,b) = ((q^(2a)+1)*(q^(2b)+1)) / (4*q^(a+b))`.

The current noisy boundary forecast is `(9R+1)/(10(R+1))`, strictly
increasing in R. Equality of R gives the same normalized two-boundary
distribution and hence all boundary futures. The same one scalar is the
complete boundary response for every h: D_h(2)=1.

Nevertheless R determines the unordered pair{a,b} exactly. Its rational
3-adic valuation is `-4(a+b)`, so it determines s=a+b. Multiplication by
4*q^s then recovers

`q^(2s) + q^(2a) + q^(2b) + 1`.

After subtracting the known first and last terms, its base q^2 expansion
has a1 at a and b, or a2 at a=b. No carry is possible. Unique positional
expansion recovers the unordered pair. Exchanging the two interior
vertices is indeed a collision for this restricted boundary interface.

There are exactly `binom(L+1,2)` such boundary classes, with exact worst-case
code length `ceil(log2(binom(L+1,2)))`. At T=8L their count is Theta(T^2),
although the response dimension is1. This falsifies a proposed universal
O(T^D_h(b)) reachable-class upper bound. The strict-convexity argument
above was an injectivity theorem for its chosen parameter family, not
a precision bound on all rational boundary moments.

This is an exact distinction. It does not claim a fixed AMP word resolves
all these increasingly close forecasts, nor a model advantage at a stated
tolerance. It also does not permit identifying the two full native states
under interior queries or parameter reads.

## 6. Exact and owned evidence

The [audit](../../evidence/minimal/FP_REACHABLE_BOUNDARY_INFORMATION.json)
checks25 discrete parameter valuations. It exhausts four small grids:
8,64,729 and2187 words, totaling2988 independent full-world marginal
comparisons and distinct selected-moment vectors. A b6,h1,n66 grid receives
190 deterministic sampled checks; its2^30 class count comes from the proof,
not exhaustive execution. No literal world table is built for that grid.

Two n8,L2 words execute the same44-query history through owned Runtime:
all coordinates zero and all one. Independent literal native execution
checks90 complete caches,88 observed states and88 committed states. The
final query(0,1) has its target unrevealed and forecasts1/2 versus
413258281348153/460432086362162. Current packed roots are774,720 and784,947
bytes. These are not total-RAM measurements or physical savings.

For the two-path precision counterexample,1365 ordered count states over
L=1,2,4,8,16,32 match independent full-world marginalization. Every collision
is exactly interior exchange; the L32 family has528 classes at T256.
No GPU or new complete-class Compiler certificate is claimed.

Run `python -X utf8 -B experiments/joint_uncertainty/reachable_boundary_information.py --write`.
Evidence retains small coordinate words and aggregate exact checks, without
weights, full caches or datasets. Foundation R4 and ERC-1 are unchanged.
