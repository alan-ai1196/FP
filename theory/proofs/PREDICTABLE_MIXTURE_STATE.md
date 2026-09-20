# Positive state for a common predictable evidence coefficient

Status: **SCOPED THEOREMS AND EXACT PASSIVE AUDIT; NOT A RUNTIME EXTENSION**.
The fixed8ccacc0 experiment remains unchanged. No retained model tape is
used to select or assess this procedure. The question follows the
[fixed-coefficient tradeoff](TIGHTER_BOUND_DEPLOYMENT_TRADEOFF.md): what
information and precision would a common adaptive coefficient actually need?

Continuous wealth mixtures and their comparison with constant bets are
classical; see [Cover and Ordentlich, 1996, Theorems1–2](https://isl.stanford.edu/~cover/papers/cover_ordentlich_96.pdf).
Predictable betting under bounded-mean hypotheses is also established
[Waudby-Smith and Ramdas, 2024](https://doi.org/10.1093/jrsssb/qkad009).
No novelty is claimed for those methods. The FP work below concerns a positive
finite state, exact continuation scope, conservative rounding and explicit
counterexamples to discarding information. No unique prior or optimal
deployment strategy is inferred from FP semantics.

## 1. One common predictable bet, without a coefficient menu

Fix a proved common B before the context and keep it fixed for the identity.
Let x_t be a rational lower score divided by B, with -1<=x_t<=1. Under the
registered stopped gain-mean null, E[x_t|F_(t-1)]<=0. Bounds, score provenance,
path and the pre-context filtration remain obligations; observing the context
does not authorize a new coefficient.

For b in[0,1], define P_t(b)=PRODUCT_(s<=t)(1+b*x_s), P_0=1. Use the fixed
arcsine measure dnu(b)=db/(pi*sqrt(b*(1-b))) and M_t=integral P_t dnu.
The integration variable is not a sampled hidden coin. The deterministic
effective fraction is

`b_t = integral b*P_(t-1)(b) dnu / integral P_(t-1)(b) dnu`.

It is strictly between0 and1 and known before the next context. Direct
expansion gives M_t=M_(t-1)*(1+b_t*x_t). Hence M is the same kind of common
nonnegative supermartingale already allowed by [Foundation XIV.20](../../FP_THEORY.md#20-lineage-specific-e-process). One
mixture starts with unit wealth and uses one identity's alpha; its continuum
does not create free independent test attempts. Any future implementation
must start at its own fresh cut with its own paid state and spent alpha.

The chosen measure specifies this statistic, rather than a new source law.
It has no tuned finite coefficient list, but it is still a statistical design
choice. Its guarantees below do not select it as the best finite-horizon rule.

## 2. Positive coefficients and a sharp classical comparison

Put z_t=1+x_t>=0. Expand

`P_t(b) = SUM_(k=0..t) c_(t,k) * b^k * (1-b)^(t-k)`.

These are unnormalized Bernstein coefficients. They start with c_(0,0)=1
and obey the positive recurrence

`c_(t,k) = c_(t-1,k) + z_t*c_(t-1,k-1)`,

where missing coordinates are zero. No signed coefficient cancellation or
numerical quadrature is required. The exact positive readout weights are

`v_(t,k) = (2k)!*(2(t-k))! / (4^t*k!*(t-k)!*t!)`,

so M_t=SUM c_(t,k)*v_(t,k). The first moment uses the same summands multiplied
by(2k+1)/(2(t+1)). This supplies the next common fraction from owned past
state if the procedure is eventually implemented.

The classical sharp comparison is

`max_(0<=b<=1) P_t(b) <= R_t*M_t`,

`R_t = 4^t/binom(2t,t) <= 2*sqrt(t)` for t>=1, with R_0=1.

An elementary verification uses positivity term by term. At p=k/t, the
maximum of b^k(1-b)^(t-k) is p^k(1-p)^(t-k). The probability at2k for
Binomial(2t,p) cannot exceed the maximal atom at k of Binomial(t,p), by
convolution. Rearranging gives that basis maximum<=R_t*v_(t,k). The ratio
recurrence R_(t+1)/R_t=(2t+2)/(2t+1) proves the displayed square-root bound
by induction from t=1. All x_s=-1 attain equality against the cash b=0.

This is a wealth comparison with every constant fraction, including an
oracle-selected one. It is not first-passage dominance: after three x=1
events the mixture has63/16<4 while fraction3/4 has343/64>4. Nor does it
transfer a physical install, null, alpha allocation or completion result.

## 3. Exact continuation equivalence has a horizon boundary

Consider only this statistic's exact multiplication/readout interface, with
the same fixed B and nu, known cut t and at most K remaining scalar inputs.
The interface exposes algebraic readouts, before any threshold truncation.
Let P,Q be two current curves. They give identical readouts after **every**
common future word of length at most K if and only if

`integral b^j*P(b) dnu = integral b^j*Q(b) dnu` for j=0,...,K.       (1)

Sufficiency follows by expanding the future product, whose degree is at most
K. For necessity it suffices to repeat any one legal nonzero score a: the
polynomials(1+a*b)^j, j=0,...,K, form a triangular basis. The allowed future
alphabet must contain that nonzero score; it cannot be assumed away.
For a still-live state below threshold, a repeatable negative score proves
the same necessity without causing an earlier threshold crossing. No claim
is made that already terminated identities need further statistic state.

For degree-at-most-t curves normalized by P(0)=Q(0)=1, K>=t-1 already makes
(1) determine the entire polynomial. Indeed D=P-Q=b*R with degree R<=t-1;
orthogonality to all polynomials through degree t-1 gives integral b*R^2=0.
The measure is positive on the open interval, so D=0. At a short remaining
horizon, (1) is the precise weaker equivalence relevant to this interface.

Current wealth alone fails even at the same cut. The two normalized score
words(1/2,-4/11) and(0,0) both give M_2=1. Their first moments are87/176 and
1/2. A common next score1/2 gives439/352 and5/4, differing by1/352. A scalar
wealth/cursor record cannot replace the omitted continuation information.

This does not prove that a coefficient vector is the only or smallest
encoding. Retained scores can reconstruct it with paid work. Nor is (1) a
quotient of the complete Compiler state: other legal futures can inspect
lineage, change procedures or consume resources. The moment criterion is for
exact multiplication; it is not applied to the rounded recurrence below.

## 4. Rounding the positive state preserves validity

Choose one grid delta=2^-q at registration. Represent a current lower curve
Q_t by coefficients d_(t,k)=n_(t,k)*delta, with nonnegative integers n.
Initialize n_(0,0)=2^q. Apply coefficientwise downward rounding:

`n_(t,k) = n_(t-1,k) + floor(z_t*n_(t-1,k-1))`.

The actual wealth is the **exact rational** integral L_t=integral Q_t dnu.
It is not a separately rounded scalar substituted back for that integral.
Let b_t be the first-moment ratio of Q_(t-1). Pointwise positivity gives

`Q_t(b) <= Q_(t-1)(b)*(1+b*x_t)`,

and therefore L_t<=L_(t-1)*(1+b_t*x_t). The same conditional mean-null proves
that L is a nonnegative supermartingale. Precision loss is conservative and
the coefficient is still common and predictable. This proof does not rely
on the invalid general inference that any pointwise lower process is itself
a supermartingale; the one-step comparison is to its own previous state.

For a killed identity the analytical testing process can be set to zero;
no later crossing is available. This is not permission to erase retained
ledger wealth or failure history. A runtime implementation would still have
to prove its actual failure/publication behavior and owned crossing gates.

Since sum_(k=0..t) b^k(1-b)^(t-k)<=1 and every factor is at most2, induction
gives a pathwise, all-history approximation bound

`0 <= P_t(b)-Q_t(b) <= delta*(2^t-1)`.

Thus the same bound holds for M_t-L_t. A registered horizon H and q=H+p give
error strictly below2^-p at every cut through H. In particular,

`L_t >= max_b P_t(b)/R_t - 2^-p`, for t<=H.                       (2)

The constant coefficient stays exactly1. Consequently L_t>=v_(t,0)>0
at every finite live cut, even at very coarse coefficient precision. This
procedure has no absorbing zero from coefficient rounding. The claim does
not cover an extra fixed-grid rounding of the reported integral, a halted
computation, a different approximation or the existing Runtime wealth rule.

Rounding also changes which histories are equivalent. At q=1, the word
(-1/4,1/2) gives coefficient numerators(2,4,1) and wealth13/16. Reversing it
gives(2,4,2) and wealth1. The exact products commute; their rounded updates
do not. Discarding order in favor of a gain histogram would change this
declared numerical procedure.

## 5. Finite mathematical resource bounds, not an owned endpoint

The coefficient recurrence has t+1 cells and O(t) arithmetic operations per
event, O(H^2) through H. Because c_(t,k)<=binom(t,k)*2^k<=3^t, each numerator
needs at most q+2t+1 bits. The coefficient payload is therefore
O((H+1)*(H+q)) bits. With q=H+p, this is O((H+1)*(H+p)). A normalized input
score of encoding length L needs O(L+q+H) temporary integer bits per update.

The readout can stream weights without retaining a weight table. In fact
the weights are dyadic: expand b^k(1-b)^(t-k) and use
integral b^j dnu=binom(2j,j)/4^j. Every denominator divides4^t. Thus common
denominator D_t=4^t suffices, with first numerator A_(t,0)=binom(2t,t);
successive weights obey

`A_(t,k+1)=A_(t,k)*(2k+1)/(2(t-k)-1)`.

Each division is exact. A_(t,0) is formed by the exact recurrence
A_(t,0)=A_(t-1,0)*2*(2t-1)/t. Only O(t) positive integer operations are
needed. The wealth denominator divides2^(q+2t), and its numerator needs
at most q+3t+1 bits because L_t<=2^t. The streamed accumulator and exact
readout therefore need O(q+H) bits. No real integration, floating density or unbounded
precision oracle is hidden in these bounds. Bit-operation costs, actual
object residency, temporary ownership and guarded failure must still be
charged before any complete Runtime claim.

These are constructive scalar bounds, not a full Compiler decision class,
a GPU implementation, a new freeze or an installation certificate. The
existing Runtime's immutable constant fraction and grid wealth are unchanged.
A different registered evidence procedure would need its own complete owned
state, information cuts, reference/AMP paths and adversarial endpoint audit.

## 6. Exact audit and research boundary

Run `python -B experiments/joint_uncertainty/predictable_mixture_state.py --write`.
The [minimal evidence](../../evidence/minimal/FP_PREDICTABLE_MIXTURE_STATE.json)
records all15,625 length-six words over{-1,-1/3,0,1/2,1},19,531 prefixes,
39,060 rounded updates,31,248 zero-mean two-point null checks,23,436
nonpositive point nulls and39,062 independent monomial readouts. Grids3
and22 cover a coarse machine and the H+16 accuracy construction.

There are2,145 exact basis-maximum comparisons and65 sharp endpoint checks
through horizon64. All three information/rounding/first-passage
counterexamples are retained. Four explicit64-event words, including
non-dyadic scores, check256 prefixes at96 fractional bits and error<2^-32,
including the dyadic readout and coefficient bit bounds. These bit lengths
are not measurements of Python heap or owned process commitment.
An actual native n2 self-query supplies
the production log scores for32 five-label words:160 pre-target forecasts
and160 complete native units remain at probabilities9/10,1/10, and the
21-bit recurrence stays within2^-16. These are exact mathematical/native
audits; no complete Runtime persistence path or new GPU worker is claimed.

The result identifies a feasible mathematical adaptive state and its limits.
It supplies no model-quality comparison and is not a replacement for the
fixed experiment already running. Foundation and ERC-1 remain frozen.
