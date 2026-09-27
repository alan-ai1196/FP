# A complete positive-readout envelope without label-by-context work

The [full CUDA audit](COMPLETE_PREDICTION_RELATION.md) costs26.6 seconds for
512 contexts. This result removes that measured obstacle from the numerical
predicate: use the positive readout's column sums and coordinate extrema to
cover every label. All untied masters, source records and native gradients
remain retained. This compresses the verification calculation, not the state.

Status: **conditional numerical theorem and exact CPU audit**. The implementation
is `readout_envelope.bound`. A Runtime owner still has to bind the complete actual
operands and registered code, preserve every event's learner state, and verify
executed query words. A passive envelope is not an issued physical bridge.

## The numerical law

Let V<=2^20, K>=1 and0<=p<=32. Each physical readout master q is an integer
in[0,2^32-1]; its coefficient is w=RNE32(q)*2^-p. Let f_i be the retained
nonnegative half feature widened exactly to single, and beta_y the registered
positive binary32 base. Use the fixed recipe of separate binary32 products,
balanced additions, base addition and division, with round-to-nearest/ties-even
and gradual underflow. Nonfinite outputs are inadmissible.

For an observed context define the exact unrounded physical mass

```
A_y = beta_y + sum_i w_yi f_i.
```

The exact mass of the native reference is
`M_y = b_y + sum_i W_yi z_i`, with exact native normalizer R. Denote the
stored rounded physical mass by m_y, the exact sum of these masses by S,
the actual retained rounded normalizer by Z, and the raw rounded division
by r_y=RNE32(m_y/Z). R and Z may differ, as may Z and S.

Put u=2^-24, alpha=2^-150, h=ceil(log2 K), d=h+2,

```
c   = (1+u)^d
rho = c-1
tau = 2*K*alpha*c.
```

**Rounding bound.** Every finite binary32 RNE operation with exact result x
satisfies `|RNE32(x)-x| <= u*|x|+alpha`, by normal/subnormal grid spacing.
A readout path has at most d rounded operations; there are2K operations
before division. Since all mass contributions are nonnegative, propagating
each multiplicative perturbation gives at most rho times the unrounded sum,
and propagating each additive underflow error gives at most alpha*c. Thus

```
|m_y-A_y| <= rho*A_y + tau.                       (1)
```

The same overestimate covers the excess before adding the base. Partial
positive sums have no larger propagated upper bound than the full mass.
Checking that bound against the greatest finite binary32 value discharges
the no-overflow premise inductively. This covers uneven balanced trees and
repeated feature indices without assuming cancellation or an active support.

For a context compute the following complete-coordinate summaries:

```
Amax = max_y beta_y + sum_i (max_y w_yi) f_i
db   = max_y |beta_y-b_y|
dw_i = max_y |w_yi-W_yi|
Wmax_i = max_y W_yi
df_i = |f_i-z_i|
E    = db + sum_i (dw_i f_i + Wmax_i df_i) + rho*Amax + tau
mmax = (1+rho)*Amax + tau.
```

The exact decomposition `w*f-W*z=(w-W)*f+W*(f-z)` and(1) imply
`|m_y-M_y|<=E` and `m_y<=mmax` for every label. Separate extrema may belong
to different labels, which only loosens the bound.

The complete unrounded physical sum is

```
T = sum_y beta_y + sum_i (sum_y w_yi) f_i.
```

Summing(1) preserves the actual normalization:

```
|S-T| <= rho*T + V*tau.                           (2)
```

The rounded integer RNE32(q) remains an integer at most2^32. Each column's
integer sum is therefore at most2^52 and fits both int64 and binary64
exactly. Scaling by2^-p is exact. Compute these sums in integer arithmetic,
and sum the registered binary32 bases as exact rationals. Formula(2) encloses
S without executing or retaining any unqueried label/context mass. It does
not assert that S equals Z or the native R.

For positive R,S,Z, let `e_div = u*mmax/Z+alpha`. The complete prediction
and normalization relations follow from

```
|M_y/R - r_y|   <= E/R + mmax*|R-Z|/(R*Z) + e_div
|M_y/R - m_y/S| <= E/R + mmax*|R-S|/(R*S)
|m_y/S - r_y|   <= mmax*|S-Z|/(S*Z) + e_div.       (3)
```

For example, the first identity follows by inserting m_y/R and m_y/Z;
the others use the same exact denominator difference. These bounds cover
**every label**, not a sampled subset. Native and actual core values, all
three normalizer discrepancies, and range caps are checked as well.

The implementation evaluates(1)-(3) with outward binary64 intervals, then
compares their final upper endpoints as exact fractions with the same fixed
tolerances used by the exhaustive audit. It requires a strictly positive
lower bound for S and R. Monotonic RNE gives m_y>=min beta; requiring
`min beta/Z>=2^-149` proves a positive raw probability, and requiring
`mmax/Z<=1` proves a raw probability at most one. These sufficient conditions
can be inconclusive for valid models: they are solver limits, not additional
FP semantics. Inconclusive bounds, missing bindings and exhausted quotas refuse.

The readout calculation costs O(VK+KN) arithmetic and O(VK+KN) array storage;
the complete core-value comparison adds O(JN), where J includes input nodes.
Exact base ingress/aggregation has its own rational-operand cost. This is
not a total-host bound. V*N is the number of mathematically covered entries,
not the number physically computed by this algorithm. Executed target-cache
words receive an additional O(KN) exact decoder check.

## Evidence and the ownership boundary

The [CPU evidence](../../evidence/minimal/FP_TOKEN_READOUT_ENVELOPE.json) compares
all native values/masses/normalizers and78 exact probabilities, including27
units in which native and AMP trajectories keep their own successors. It
also covers uint32 masters rounding to integer2^32, repeated features,
nonuniform bases, and the stored-mass sum33554433/33554432. Five changed
record/cache/tolerance/quota inputs refuse. A valid min-subnormal-base model
remains unresolved when the additive underflow envelope cannot prove S>0.

On the unchanged full-V/context512/512-training-token fixture, the new CPU
predicate takes0.07704 seconds and satisfies the original limits:

| Upper bound | Value | Fixed limit |
|---|---:|---:|
| Native core/excess/mass error | 0.0005400092741194574 | 1/100 |
| Normalizer error | 0.00535272428455258 | 1/100 |
| Probability error | 3.10872794358355e-8 | 1/10^6 |
| Proper versus raw division error | 1.4744959367890085e-11 | 1/10^7 |

All402,056 readout masters are included,512 target caches are checked with
8,192 decoder words, and no unqueried label/context is executed. The bounds
are looser than the exhaustive control and still pass. The time is one CPU
observation without a whole-process fence; comparison with26.6 seconds of
CUDA execution/transfers plus exhaustive verification is not an isolated
hardware speedup experiment. No Torch, old CUDA job replay, optimizer commit,
loss, validation or test read is involved in this new audit.

The conditional theorem concerns the fixed arithmetic recipe. Arbitrary
replacement code could emit a different unqueried label while preserving
its inputs and target cache; this predicate alone would not detect it. A
complete physical owner must bind the actual code and operands and enforce
that recipe, including the arithmetic premises. The existing exhaustive
actual-device result is a separate finite control, not a universal guarantee
for future device states. Pending gradients and XV's internal event relation
also remain due. Those are the next integration task; no further static
readout family or relaxed tolerance is proposed.
