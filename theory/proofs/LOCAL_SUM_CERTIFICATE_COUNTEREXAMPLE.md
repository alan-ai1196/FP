# Local SUM closure certificates do not compose on a three-bit cube

Status: **FALSIFIED shortcut, with a PROVED global margin**, 2026-09-06.
The full residual-cone theorem in XVII.2 is unaffected. This rules out replacing
its global problem by independent two-dimensional checks or threshold cuts.

## 1. The rational counterexample

For vertices in lexicographic order `000,...,111`, take binary target

\[
\boxed{p=(1/10,11/30,19/30,11/30,19/30,11/30,19/30,9/10).}
\]

Every one of its six coordinate faces lies in the closure of the corresponding
normalized unary-SUM family: the diagonal and off-diagonal closed probability
intervals intersect. Thus each face individually admits arbitrarily accurate
finite positive SUM approximants. Their coefficients need not agree on shared
contexts, which is precisely the unproved step in composing these certificates.

Also every strict probability superlevel set `{x:p_x>t}` is linearly separable.
Apart from empty/full sets, the three possible sets are separated by

| Superlevel set | Exact linear test |
|---|---|
| All vertices except 000 | `2x+2y+2z>1` |
| `{010,100,110,111}` | `4x+4y-2z>3` |
| `{111}` | `2x+2y+2z>5` |

Nevertheless **no single normalized SUM model can approximate the entire table
closer than 2/15 in sup norm**, and that distance is sharp. These two necessary-condition families, even
together, are not a complete global membership certificate.

## 2. The missing coupled invariant

Any unary-SUM model has a linear-fractional prediction

\[
q(x)=\frac{a+\sum_i b_ix_i}{c+\sum_i d_ix_i},\qquad T(x)>0.
\]

The coefficients here are an algebraic flattening; b_i,d_i may be signed when
complementary indicators are expanded. No hidden positivity of these slopes
is assumed.

**Antipodal-extrema lemma.** If 0 is a global minimum m and 1 a global maximum M
of q on the cube, then q is nondecreasing in each coordinate everywhere.

Proof: the edge from 0 to e_i gives `b_i-m d_i>=0`. The edge from `1-e_i` to 1
gives `b_i-M d_i>=0`. Their convex combinations imply `b_i-r d_i>=0` for every
`r in [m,M]`. At any edge with x_i=0,

\[
q(x+e_i)-q(x)=\frac{b_i-q(x)d_i}{T(x)+d_i}\ge0.
\]

Both denominators are actual positive normalizers. Complementing coordinates
gives the corresponding statement for any antipodal minimum/maximum pair.
The common numerator/denominator enforce this invariant simultaneously across
all threshold cuts. Independent separating hyperplanes do not enforce it.

## 3. Robust exclusion, including all limiting SUM hierarchies

The counterexample has unique minimum 1/10 at 000 and unique maximum 9/10 at
111. Each is separated from the next value by 4/15. But the edge `010 -> 011`
strictly decreases by 4/15. If a candidate q were within distance `<2/15`, it
would retain both unique antipodal extrema and that decreasing edge. This
contradicts the lemma. Therefore

\[
\boxed{\inf_{q\in\overline{SUM}}\|p-q\|_\infty\ge2/15.}
\]

This argument applies to every finite approximant before taking limits, so a
zero-normalizer hierarchy cannot evade it.

An independent exact mass identity both certifies and explains the sharp
constant. Write `chi=(-1)^(x+y+z)` and

\[
p=r-\tfrac2{15}\chi,\qquad r=\tfrac7{30}+\tfrac4{15}(x+y).
\]

For any SUM mass numerator M_1 and total T, both are affine. The product rT
has degree at most two. Its top parity moment vanishes, as does that of M_1.
Consequently

\[
\boxed{\sum_x\chi_x T_x(q_x-p_x)=\tfrac2{15}\sum_xT_x.}
\]

The absolute value of the left side is at most `||q-p||_infinity sum T`, giving
the same lower bound. In the XVII.2 cone equations this is the explicit dual
`alpha_x=(15/2)chi_x`, with `A^T alpha=s` exactly for every unary mass atom
and the fixed positive base. It needs no numerical LP status.

The matching finite SUM model is

\[
M_1=7+8x+8y,\qquad M_0=7+8(1-x)+8(1-y).
\]

It has total 30 and predicts r. Its error from p is exactly 2/15 at every
vertex. Both mass functions are legal over the fixed base `(1,1)` (the
additional constant 6 is a positive sum of either complete unary partition).
Thus the distance is exactly 2/15 even before taking closure. This is a
static encoded witness, not a granted registered value/build/install path.

For uniform context weighting, binary Pinsker in nats then gives a loss margin
against the **entire** static unary-SUM class:

\[
\boxed{L(q)-L_{Bayes}=\tfrac18\sum_x KL(p_x\Vert q_x)
\ge\tfrac18\,2(2/15)^2=1/225.}
\]

The failure is representational, not a loose optimizer tolerance or insufficient
sampling. The correct full known-cone solver may still decide it; local face
or independent threshold checks alone must leave it unresolved. No source,
semantic action, regularizer, or Foundation R4 change is needed.

Exact audit: `theory/numerical_checks/local_sum_certificate_audit.py`.
