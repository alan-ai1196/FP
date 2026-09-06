# Output degree and positive derivation support have different range costs

Status: **PROVED under the static contract below**, 2026-09-06. This derives
a provenance-sensitive resource separation from native positivity. It does
not introduce a new semantic operation or authorize an unconstructed value.

## 1. One task, three complete comparison classes

Let d>=3, m=d-1, r>1 and eta=1/(r+1). Contexts are uniform binary d-vectors,
with their unary indicator sources, fixed base `(1,1)`, arbitrary finite positive
SUM/PRODUCT DAGs and one final normalization. Coefficients are nonnegative;
there is no recurrence, internal normalization or input-dependent base.

At every vertex except the adjacent pair `00...0,10...0`, the parity label is
correct with probability `a=r/(r+1)`. At those two root vertices its probability
is eta instead. The ordinary binary conditional table is the fixed target.
The declared resource is the maximum final normalizer R, not a hardware proxy.

Distinguish three nested classes:

1. All native programs.
2. Programs whose **output mass functions**, after multilinear reduction on
   the cube, have degree <d.
3. Programs whose every nonzero positive derivation monomial fixes <d distinct
   input coordinates, including arbitrary sharing and repeated indicators.

Class 3 is exactly the positive cone of cube-edge indicators, with independent
nonnegative coefficients for the two labels and the fixed base. Indeed any
proper cylinder can be split into edges by summing over unused coordinates;
every edge indicator is itself a native PRODUCT of d-1 unary sources. This
is an extensional cone used for exclusion, not a cost-preserving graph rewrite.

The exact minimum range for Bayes prediction in the three classes is

\[
\boxed{
R_{all}=r+1,\quad
R_{degree}=(r+1)(2^m-1),\quad
R_{support}=\frac{r+1}{r}\big[(r+1)^m-1\big].}
\]

All thresholds are attained by finite native mass constructions. In particular,
for d=3 and r=3 they are **4, 12, 20**. Reduced output degree cannot be used as
a certificate of reduced positive derivation support or its physical costs.
The ratio `R_support/R_degree` grows exponentially with dimension at fixed r>1.

## 2. The first two exact thresholds

Every exact target prediction has a mass ratio r, so base positivity implies
total mass at least r+1. Giving the more likely label mass r and the other
mass 1 at every vertex attains this using full-context indicators.

For reduced output degree <d, both mass functions have zero top parity moment.
Let T be their sum. Expressing `M_parity-M_other` as `(a-eta)T` on the ordinary
vertices and its negative on the two roots gives

\[
\sum_{roots}T=\sum_{nonroots}T.
\]

Each non-root has T>=r+1, while the roots have total at most 2R. Thus
`R>=(r+1)(2^m-1)`. To attain it, use masses `(r,1)` in parity-correct/other order
at each non-root, and `(2^m-1,r(2^m-1))` in that order at each root.
Both ordinary label masses have equal sums on the two parity classes, so
their top Fourier coefficients vanish and their reduced degree is <d.
All masses are at least 1 and have the claimed peak.

These masses are native: sum each nonnegative `M_y(x)-1` times its full-context
indicator onto the fixed base. Those are **full-support positive derivations**.
The disappearing top coefficient arises only after expanding complementary
indicators and collecting signed algebraic coefficients. Positive provenance
has not disappeared. The next lower bound proves it cannot disappear at this
range in any alternative realization either.

## 3. The complete proper-support lower bound

For the edge cone, average a feasible mass realization over permutations of
the last m coordinates, and over flipping the first coordinate together with
swapping the output labels. The target is invariant under these transformations.
Fixed-target equations, positivity and range caps are linear in masses, so
this averaging preserves feasibility. It is an optimistic static symmetry
argument, not a learner-state quotient or a free installation transform.

Write k for the Hamming weight of the last m coordinates. After averaging,
the first-coordinate edge contributes equally to both labels: let `b_k>=1`
be the fixed base plus that neutral contribution at each level-k vertex.
On every edge from level k-1 to k, let `u_k>=0` be the coefficient of the
child's parity label and `v_k>=0` that of the other label. A level-k vertex
has k parent edges and m-k child edges. Set `D_k=u_k-r v_k`.

At each non-root level, the required ratio r gives

\[
kD_k=(r-1)b_k+(m-k)[rD_{k+1}+(r^2-1)v_{k+1}],\quad 1\le k\le m,
\]

where the child term is absent at k=m. At the roots the ratio is reversed:

\[
mD_1=(r-1)b_0.
\]

Backward induction gives `D_k>=u_k^*`, where

\[
u_m^*=\frac{r-1}{m},\qquad
u_k^*=\frac{(r-1)+(m-k)r u_{k+1}^*}{k}.
\]

Solving the finite recurrence yields

\[
b_0\ge\frac{m u_1^*}{r-1}
=S:=\sum_{j=1}^m {m\choose j}r^{j-1}
=\frac{(r+1)^m-1}{r}.
\]

The root parity-label mass is `b_0+m v_1>=b_0`; its total is r+1 times that
mass. Hence every proper-support program needs `R>=(r+1)S`.

## 4. A finite matching edge construction

Take `v_k=0`, `b_k=1` for k>=1, `u_k=u_k^*` and `b_0=S`. Put coefficient
`S-1` on both label edges of the first-coordinate root edge, and no such
neutral additions elsewhere. On each remaining edge from level k-1 to k,
put weight u_k only on the child's parity label. These are legal nonnegative
edge-indicator coefficients. The equations above hold exactly.

The root total is `(r+1)S`. At level k>=1 the total is
`(r+1)[1+(m-k)u_{k+1}]`, interpreting the child term as zero at the leaves.
No other vertex exceeds the root. One way to check this is the positive
integral identity

\[
u_k=(r-1)\int_0^1 t^{k-1}[1+r(1-t)]^{m-k}\,dt,
\]

which shows `u_k>=u_{k+1}`. The recurrence for u_1 gives
`S=m+mr(m-1)u_2/(r-1)>=1+(m-1)u_2`, bounding every non-root total.
This proves finite attainment of the proper-support threshold.

In the three-bit odds-three case, the construction is particularly small:
`u_1=5`, `u_2=1`, and the neutral root-edge coefficient is `S-1=4` per label.
At levels 0,1,2 the parity-label/other mass pairs are respectively
`(5,15)`, `(6,2)`, `(3,1)`, with totals 20,8,4. The reduced-degree construction
instead has root pair `(3,9)` and every non-root pair `(3,1)`, with peak 12.
These are distinct finite realizations of the same conditional table.

## 5. The separation has a positive approximation/loss margin

The threshold gap is not only an exact-equality artifact. Suppose an edge-cone
prediction is within sup-norm delta of the target and has cap R. Averaging
still preserves these inequalities, because `(p-delta)T<=M_1<=(p+delta)T`
is linear in the masses for fixed delta.

Let `e_k=M_parity-r M_other` at non-roots and
`e_0=r M_parity-M_other` at the roots. Each has magnitude at most
`C delta`, where `C=(r+1)R`. The non-root recurrence now has `(r-1)b_k+e_k`
in place of `(r-1)b_k`, while `mD_1=(r-1)b_0-e_0` at the root. Backward
induction, retaining these errors, gives

\[
b_0\ge S-\frac{C\delta(S+1)}{r-1},\qquad
T_0\ge(r+1)b_0-C\delta.
\]

Therefore whenever R<R_support,

\[
\boxed{\delta\ge
\frac{(r-1)(R_{support}-R)}{(r+1)R(R_{support}+2r)}.}
\]

At d=3, r=3 and R=12 this is `delta>=1/78`. Uniform binary Pinsker then gives
excess CE at least `2 delta^2/8=1/24336` against the entire proper-support
class, while a reduced-degree native model attains Bayes at that same cap.
Thus a reduced-degree output can still require full-support positive provenance
with a proved risk margin. The margin is a bound, not claimed sharp.

## 6. What this does and does not authorize

The theorem rejects erasing derivations on the basis of collected polynomial
coefficients. It supplies a complete static comparator cone, exact numerical-
range optima and a robust exclusion. It does not say that degree must always
be retained as a new state field: claim-relative future behavior and actual
resources still determine what information is necessary.

The fixed cap is on final normalizers. Finite algebraic coefficients do not
establish registered initialization/profile/optimizer reachability, minimal
physical storage, build-before-free feasibility, fresh persistence or AMP
authorization. Those remain independent obligations. The lower bound allows
all proper-support derivations, not a handpicked graph menu.

Exact audit: `theory/numerical_checks/parity_provenance_range_audit.py`.
