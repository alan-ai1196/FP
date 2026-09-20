# Shared positive denominators reduce native readout cost

Status: **PROVED FOR THIS EMITTER; EXACT NATIVE AND CHECKED BINARY64 AUDITS**.
The factorial degree in the first [positive rational readout compiler](POSITIVE_RATIONAL_READOUT.md)
is avoidable for its directed-tree example. A common-denominator construction
reduces the degree to `2^(n-2)` with O(n^3) native syntax and the same selected
learning law. Its explicit rational output still has exponentially many
numerator bits. Neither
degree law is a lower bound against all representations of the forecast.

This is a passive alternative Program emitter. It changes no Foundation
action, production constructor, Runtime state representation, AMP bridge or
registered model experiment. In particular, it does not erase denominators
or feature gradients from an executing graph.

## 1. Preserve one denominator at each elimination stage

Use the directed spanning-tree polynomial phi_n from the earlier proof,
with root n-1 and `(n-1)^2` edge weights `w_ij=1+theta_ij`, theta>=0.
The complete unit source and fixed feature are both 1. The existing positive
Schur update eliminates v with pivot `s=SUM_(j != v) w_vj`:

`w'_ij = w_ij + w_iv*w_vj/s`.

The output phi_n is the product of these pivots. This is the same classical
positive elimination identity already justified in the preceding proof.

Maintain every surviving edge in the form `N_ij/Q` with a common positive Q.
Initially N_ij=w_ij and Q=1. Put `S=SUM_j N_vj`. Then the exact update is

`N'_ij = N_ij*S + N_iv*N_vj`, `Q'=Q*S`, `s=S/Q`.

All numerator operations are positive additions and multiplications. They
use the old incident row/column and therefore remain valid with shared
subexpressions. Q is a symbolic invariant used to derive the output, rather
than an extra value that the emitted native graph secretly reads.

Index the successive pivot numerators by S_0,...,S_(n-2). The denominator
at stage t is `Q_t=PRODUCT_(u<t) S_u`. Since every S_u is strictly positive,
canceling these formal factors in the product of rational pivots gives

`phi_n = S_(n-2)/D`,

`D = PRODUCT_(j=0..n-4) S_j^(n-3-j)`.

An empty product is 1. D itself has a positive circuit with only O(n)
extra multiplications: multiply successive prefixes of S_0,...,S_(n-4).
There are O(n^3) numerator updates. Apply the earlier positive `(P,P-1)`
construction to the numerator and denominator circuits. The actual native
masses are **N=S_(n-2) and D**, with bases(1,1), and its forecast is

`p_0=N/(N+D)=phi_n/(1+phi_n)`.

This compilation uses only native SUM/PRODUCT and the existing final
normalization. The single abstract division describing N/D becomes these
two masses; it does not run as an internal native operation. No large
numeric coefficient is imported. Every coefficient comes from counted
positive operations on the unit source and shifted parameter leaves.

## 2. Exact degree, range and operand law for this graph

After t eliminations, each numerator is homogeneous of degree `2^t` in w,
and the common denominator has degree `2^t-1`. This follows immediately
from the two products in N' and from Q'=Q*S. Thus

`degree N = a_n = 2^(n-2)`,

`degree D = SUM_(j=0..n-4) (n-3-j)*2^j = 2^(n-2)-n+1`.

The largest selected degree in the actual positive-base native graph is
a_n. All intermediate numerator degrees are smaller, denominator prefixes
have degree at most degree D, and forming P-1 by the positive recurrence
does not increase selected degree. The zero excess for a constant mass has
degree zero for this mass calculation. This replaces the first emitter's
`Theta((n+1)!)` maximum degree, without changing the O(n^3) graph order.

The improvement does not make the complete native values small. When all
edge weights equal w, a stage with k remaining vertices has equal edge
numerators A. The next numerator is `k*A^2`. Consequently

`N = C_n*w^a_n`, `C_n=PRODUCT_(k=3..n) k^(2^(k-3))`.

For n>=3, `log2 C_n=Theta(2^n log n)`: its last factor supplies the lower
bound, while summing all exponents supplies the upper. At the uniform
simplex initializer, d=(n-1)^2 and w=(d+1)/d. The reduced numerator of N is
at least `(d+1)^a_n`, because d and d+1 are coprime. Before reduction it is
at most `C_n*(d+1)^a_n`, with denominator `d^a_n`. Therefore this particular
output mass has **Theta(2^n log n) numerator bits** at that initializer.

This is also the order of the largest forward operand there. For a legal
simplex state, 1<=w_e<=2. Positive coefficient monotonicity bounds numerator
nodes by their values at w=2. The final uniform numerator dominates the
earlier pivots and update summands. Denominator prefix products are at most
D, and D=N/phi_n<=N since phi_n>=1. The positive excess construction never
exceeds its corresponding polynomial value at feature1. Thus all native
values are at most `C_n*2^a_n`, and the normalizer is at most twice that.
At uniform initialization, their denominators divide powers of d of degree
at most a_n; this gives the matching O(2^n log n) forward bit upper bound.

These are graph-specific statements. They are neither an optimal resource
law for tree forecasts nor a lower bound for the relation-task decoder.
They measure explicit reduced rational operands, not the minimum description
length of a symbolic encoding of those values.
In particular, one cannot promote the original factorial cost or this
remaining exponential cost to an impossibility for another emitter.

## 3. Preserve learning, distinguish complete native states

Readout equality holds for all theta>=0 at fixed feature1, not just at the
initializer. The selected CE gradients therefore remain

`g_e=-(partial_e phi_n)/(phi_n*(1+phi_n))` for label0,

`g_e=(partial_e phi_n)/(1+phi_n)` for label1.

Each tree uses an edge at most once, so
`0<=partial_e phi_n<=phi_n/(1+theta_e)`. The selected gradient spread is
strictly below 1; the existing one-event, unit-rate simplex U remains legal
and preserves unit mass. The two emitted learners thus have equal selected
parameters and forecasts along every jointly representable exact history
from the same initializer. A finite arithmetic refusal is still possible.

The complete native learners are different. At n4 and uniform theta, label1
has fixed-feature gradient `35727879337439/6691600000000` in the old graph
and `3884387/501870` in the new one. Selected gradients agree, but observed
gradient accumulators, native values and graph identities do not. Each new
Program must retain its own full evidence and obtain its own bridge.

Nor may D be discarded after seeing a small odds oracle. In that same n4
state, the correct forecast is `16000/16729`; replacing D by 1 gives
`160000/162187`. The cancellation used in section1 is a proved compile-time
identity on the complete domain, not an observed-value erasure.

## 4. Exact and ordered binary64 evidence

Run `python -B experiments/joint_uncertainty/shared_denominator_readout.py`.
The [minimal evidence](../../evidence/minimal/FP_SHARED_DENOMINATOR_READOUT.json)
retains graph counts, checks and refusal reasons:

- 25 independently enumerated tree cases through n6, including nonsymmetric
  priors and simplex vertices, with 50 complete native-gradient checks.
- 51 actual native observe/commit pairs through n4, covering every binary
  history through depth3 and three two-pass profile attachments; 102 complete
  observed/committed states match the independent expected states.
- Uniform initializers through n12 pass exact forward and both full-gradient
  checks under the unchanged 32768-bit arithmetic guard. The known labelled
  tree count and directed-edge frequencies supply independent oracles.
- Actual registered CPU binary64 primitives, with each rounding checked
  exactly, pass forward plus both one-event observe/commit branches through
  n10. All native values, all gradient coordinates and the complete successor
  state are checked. These are two branches from each initializer, not a
  claim about arbitrary-length binary64 histories.

| n | Old emitter degree | New degree | New nodes | Maximum exact forward operand bits | Checked binary64 |
|---|---:|---:|---:|---:|---|
| 6 | 377 | 16 | 645 | 102 | Both units pass |
| 7 | 2,935 | 32 | 1,090 | 221 | Both units pass |
| 8 | 25,955 | 64 | 1,704 | 493 | Both units pass |
| 10 | 2,788,329 | 256 | 3,551 | 2,216 | Both units pass |
| 11 | 33,174,439 | 512 | 4,840 | 4,557 | Forward overflow |
| 12 | 428,193,867 | 1,024 | 6,410 | 9,738 | Forward overflow |
| 13 | 5,958,465,857 | 2,048 | 8,289 | Exact audit unresolved | Forward overflow |

The bit column covers retained native values, masses, normalizer and
probabilities; transient arithmetic work remains subject to the separate
32768-bit guard.

The new n7/n8 exact and binary64 checks succeed where the retained original
emitter refused. Its original outcomes are retained rather than recomputed
or replaced. At n8, nodes increase only 1,683 to 1,704 while degree falls
25,955 to 64. The independent exact checks still succeed at n11/n12, where
the binary64 forward path explicitly returns `UNRESOLVED` for overflow.
At n13 the full exact audit also refuses the same 32768-bit operation guard;
this is an actual guard outcome, not a claim that the guard is tight. The
n16 row constructs syntax and checks degree only.

The binary64 audit uses fixed relative native-value and absolute full-gradient/
parameter tolerances 1e-9, with absolute probability tolerance 1e-12. Largest
observed full-gradient error is below 3.726e-13. Short upward dyadic error
enclosures replace long exact error numerators in the retained report; all
comparisons themselves use exact arithmetic. No componentwise absolute
native-value bridge, GPU result, time/memory measurement or Runtime
installation authority follows from these passive checks.
