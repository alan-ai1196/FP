# Two PRODUCTs suffice for three-bit conditional parity at larger range

Status: **PROVED; EXACT RATIONAL GRAPH AND DUAL AUDIT**, 2026-09-11.
The full static three-bit noisy-parity class has exact and approximation
PRODUCT minima two at sufficiently large normalizer range. This contrasts
with the proved minimum four at the smallest legal range. No source,
semantic primitive or numerical convention changes between these claims.

## 1. Contract and complete-class lower bound

Use the six binary unary indicators, base one in each of two output heads,
positive SUM/binary PRODUCT DAGs and one final normalization. Contexts are
uniform. Let odd parity prefer label one and even parity prefer label zero,
with noise eta in (0,1/2). Write r=(1-eta)/eta>1, so preferred odds are r.
The final normalizer cap alone is R; SUM/encoding/physical costs are separate.

Every at-most-one-PRODUCT mass has multilinear degree at most two. Its top
three-bit parity moment vanishes, as does that of the total mass. Therefore
the total-mass-weighted means of q_1 over even and odd contexts coincide.
Some even context has q_1 at least as large as some odd context. The two
target values are eta and 1-eta, which gives the cap-independent bound

`probability sup error >= 1/2-eta`.

The two selected contexts incur CE at least 2*log(2), while all remaining
contexts incur at least Bayes CE. Thus

`CE excess >= [log(2)-H(eta)]/4 > 0`.

This is the earlier complete sub-degree envelope's lower argument. It
retains every positive normalizer and passes to prediction limits. It is
not a restriction to symmetric PRODUCT parents. For eta=1/4 the probability
bound is 1/4. The CE bound is an exact expression, not a rounded certificate.

## 2. A two-PRODUCT native witness

Let x,y,z be the three bits and build

`A=(x_1+y_1)*(x_0+y_0)`, `B=A*z_1`.

On the complete binary domain A is exactly XOR(x,y). This uses one ordinary
PRODUCT, and B uses the second. Define output excesses

```
E_0 = (r-1)*z_0 + (r-1)*(r+1)^2*B,
E_1 = (r-1)*z_1 + (r^2-1)*A.
```

All coefficients are positive. For effective contexts (A,z)=00,01,10,11,
the masses (M_0,M_1), including the fixed bases, are respectively

```
(r,1), (1,r), (r,r^2), (r*(r^2+r-1), r^2+r-1).
```

These give exactly the required parity probabilities. Their normalizers
are `(r+1)*(1,1,r,r^2+r-1)`. Hence every cap

`R >= (r+1)*(r^2+r-1)`

has exact and approximation PRODUCT minima **two**, by section 1. At noise
one quarter this cap is 44 and the excesses simplify to

`E_0=2*z_0+32*B`, `E_1=2*z_1+8*A`.

Binary Horner SUMs implement the integer coefficients using only local
weights {1,2}. No extra PRODUCT or imported XOR primitive is used.

## 3. The displayed range is optimal for this fixed two-feature bank

Fix the numerical features A and B just constructed, retaining arbitrary
positive readouts of both features and every original unary source.
Simultaneously complementing x,y preserves A, B and the task. Averaging
the complete masses over this symmetry preserves the fixed cone, cannot
increase peak range, and makes the unary remainder depend only on z.
Consequently it suffices to retain all four scales u_(A,z), with preferred
mass r*u and other mass u.

Base positivity, the A coefficient of head zero and the B coefficient of
head one give the necessary inequalities

```
e_0 = u_00-1 >= 0,
e_1 = u_01-1 >= 0,
e_A = u_10-r*u_00 >= 0,
e_B = u_11-r*u_10-r*u_01+u_00 >= 0.
```

The exact nonnegative dual identity

`u_11-(r^2+r-1) = e_B+r*e_A+(r^2-1)*e_0+r*e_1`

proves the range bound, and section 2 attains it. This is a complete range
certificate for the **fixed A,B bank**, including its full unary readouts.
It is not a proof that arbitrary two-PRODUCT parents need this range.

## 4. What remains unresolved

At the minimum range r+1, the canonical shared-disjoint theorem proves
exact and approximation PRODUCT minima four. At the displayed larger cap
they are two. The exact two-PRODUCT threshold over variable parents, any
intermediate three-PRODUCT phase, and their sharp loss/resource tradeoffs
remain open. A float64 parent search finding no better witness is not a
proof of these thresholds.

The bank A,B omits the complementary XOR feature. Positivity in section 2
works because the explicit normalizer scales change; adding an unpriced
complement source or assuming a constant normalizer would change the task.
These known-value graphs do not acquire target information or establish
registered value construction, install, persistence or an AMP bridge.

Audit: `two_product_conditional_parity_audit.py` evaluates complete rational
graphs across noise odds, verifies the local-alphabet path, checks the exact
fixed-bank dual and malformed multipliers, and exercises the full one-PRODUCT
degree/normalizer ordering argument on arbitrary shared SUM graphs.
