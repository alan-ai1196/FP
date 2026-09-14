# The radix9 weight decoder has a history-uniform binary32 error bound

Status: **PROVED FOR THE REGISTERED RNE32 SCHEDULE, WITH AN EXACT FINITE
POWER-TABLE AUDIT**. This is a bound for selected weights produced by the
existing count decoder. It is not a new GPU experiment, complete native
gradient bound, whole-Runtime bridge or unlimited-resource claim. The
constructor, unit U, encoding, Foundation R4 and ERC-1 are unchanged.

## 1. The actual arithmetic to be bounded

The [owned likelihood lowering](LIKELIHOOD_RUNTIME_CONTRACT.md) retains exact
likelihood coordinates and reconstructs integer exponents z. Let

`d_k = max_j z_j - z_k`, `a_k = 9^(-d_k)`, `w_k = a_k / SUM_j a_j`.

Each d is a nonnegative integer and at least one is zero. Commensurate
prior/likelihood ratios make w the exact selected successor for every
accepted coordinate state. An invalid descriptor, counter overflow or
unproved model never enters this theorem.

The existing CUDA commit schedule encodes beta=1/9 by RNE32, successively
squares it, and multiplies the powers selected by the bits of d in ascending
bit order. It sums these nonnegative binary32 weights in slot order, then
performs binary32 division. Write b(d) for its unnormalized weight, B for
the exact sum of b values, S for the computed sum, and w_hat for the rounded
quotients. RNE32 here includes gradual underflow and ties-to-even. The
existing independent CUDA audit compares actual operation words with this
exact arithmetic schedule; the theorem does not assume every future GPU
execution passes that audit.

Put `u=2^-24`, the binary32 unit roundoff, and `h=2^-150`, half its smallest
positive subnormal. For `1 <= K <= 2^24`, define

`gamma_(K-1) = (K-1)u / (1-(K-1)u)`.

**Theorem.** For every such integer exponent vector, the schedule satisfies

`max_k |w_hat_k-w_k| <= (K-1)u/72 + gamma_(K-1) + u + h`. (1)

The bound has no history-length or maximum-exponent term. At the current
K=128 model size, its right side is approximately **7.734587805e-6**, strictly
below 1e-5. It concerns this arithmetic representation; executing arbitrary
exponents still requires their exact storage, bounded guards and paid work.

## 2. Infinite exponents reduce to a finite arithmetic lemma

The first seven squared-power words, starting with beta, are

`1038323257, 1011500424, 958386638, 851938452, 639339483, 213714255, 0`.

Thus the power at bit6, corresponding to exponent64, is exactly zero.
Every later squared power is zero. Any d>=64 has a set bit at or above6,
so its unnormalized physical weight is zero. Multiplication by zero and
subsequent finite nonnegative powers leaves it zero. For this entire tail,

`|b(d)-9^(-d)| = 9^(-d) <= 9^-64`.

The remaining 64 exponents d=0,...,63 have a finite, exact decision procedure:
execute the specified rounded products and compare the decoded dyadic value
with the rational 1/9^d. The [audit](../../experiments/joint_uncertainty/likelihood_decode_bound.py)
checks every one, retaining their raw words in the minimal report. It obtains

`E := max_(d>=0) |b(d)-9^(-d)| = 1/1207959552 = u/72`. (2)

Equality occurs at d=1. At d=47 the computed word is1, the smallest positive
subnormal; all d>=48 have zero physical weight. The d>=64 tail is justified
by the zero squared power, not extrapolated from a sampled long history.
Every power/weight stays in [0,1], and b(0)=1 exactly.

## 3. Normalization adds width-dependent error, not temporal drift

Let A=sum a_k. Since some d is zero, A>=1 and B>=1, and at least one input
error b_k-a_k is zero. Equation(2) gives

`SUM_k |b_k-a_k| <= (K-1)E`.

For any index i,

`b_i/B-a_i/A = ((A-a_i)(b_i-a_i) - a_i SUM_(j!=i)(b_j-a_j))/(AB)`.

Consequently `|b_i/B-a_i/A| <= (K-1)E`, using B>=1. This controls the change
from exact powers to rounded powers before any floating normalization.

For addition of two nonnegative binary32 values, a subnormal sum is exact:
both inputs are integer multiples of 2^-149, as is their sum. A nonzero
rounded normal sum has relative error at most u. The first addition to zero
is exact. Positive accumulation is nondecreasing; after inserting b(0)=1
its total is at least one. Inductively S_j<=j for j<=K<=2^24, since each
integer j in that range is exactly representable. There is no overflow.

With m=K-1, each summand is multiplied by between zero and m factors in
[1-u,1+u]. Positivity therefore gives

`(1-u)^m B <= S <= (1+u)^m B`.

Bernoulli's inequality and `(1+u)^m <= 1/(1-mu)` imply

`|S-B|/S <= gamma_m`.

Since b_i/B<=1, the error from replacing B by S in a normalized coordinate
is at most gamma_m. Also S>=b_i, so 0<=b_i/S<=1. RNE32 division, including
possible subnormal underflow, contributes at most `u+h` absolute error.
Adding these three errors proves(1). This proof retains the actual serial
SUM and division; it does not replace them by an exact or tree reduction.

## 4. Why this does not erase future information

At each accepted commit, the selected physical weights are decoded afresh
from the current exact coordinates. They are not obtained by multiplying
the previous rounded weights by another likelihood. Thus the bound is
uniform over accepted histories rather than a sum of their rounding errors.

A physical zero remains compatible with future recovery: opposite evidence
can reduce its retained exponent difference, producing a later positive
decoded weight. All exact coordinates, descriptor identity, pending event
and clocks remain. The theorem does not permit replacing those coordinates
by current rounded weights or discarding worlds currently decoded to zero.
Doing so would invalidate the reference-to-coordinate simulation used in
the first line of the proof.

The actual counter width is at most64 bits and its update guards remain.
Likewise the full native graph, caches, ambient gradients, source reads,
provenance, evidence, host/device storage and installation must be checked
and paid. This bound addresses a selected-weight commit, not every phase of
that larger state. The maximum permissible history still depends on all
registered resources. The existing fixed-radix analyzer is not expanded.

## 5. Exact evidence and limits

Run `python -B experiments/joint_uncertainty/likelihood_decode_bound.py --write`.
The [minimal report](../../evidence/minimal/FP_LIKELIHOOD_DECODE_ERROR.json)
retains the finite power/weight words and exact bounds. In addition to the
64-exponent lemma, it checks3,713 high-bit tail patterns, including the
largest difference below2^64-1 allowed by the signed exponent guard. It
checks all12,481 ordered three-weight vectors in {0,...,64}^3 with at least
one zero, and520 width/order controls at K2,8,128. Every arithmetic input in
these audits is also cross-checked through binary64 and a binary32 cast:
143,614 rounded operations agree with the exact oracle. This finite agreement
does not assume a general double-rounding equivalence.

The K128 controls attain error about6.46782e-6, below(1) but well above a
single binary32 roundoff. The report retains a compact exponent/order witness.
The width term cannot simply be dropped because each individual power is
accurate. No sharp normalization constant or universal optimum is claimed.

No Torch or GPU model worker is run by this audit. Previously source-bound
GPU traces remain evidence only for their actually observed words. The live
n8 matrix retains its original tolerances, caps and90f3883 source; this
arithmetic theorem does not supply a missing execution or installation.
