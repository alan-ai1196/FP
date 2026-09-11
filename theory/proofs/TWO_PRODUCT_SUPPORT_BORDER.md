# Two PRODUCTs approach a support that requires three

Status: **PROVED COUNTEREXAMPLE**, 2026-09-11. Exact Boolean support complexity
does not automatically lower-bound approximation complexity. This is stronger
than the earlier selector's exact *mass* obstruction: here even the limiting
positive/zero pattern is impossible with the approximants' PRODUCT count.

## 1. A zero-face invariant that covers shared DAGs

Use scalar unary indicators on the full d-bit cube, nonnegative finite SUM
coefficients, binary PRODUCTs, arbitrary finite SUM depth and arbitrary
sharing. Discuss a scalar excess output, before adding a positive readout
base. A coordinate face fixes a subset of the input bits.

**Face-cover theorem.** If the graph has P PRODUCT nodes, its exact zero set
is a union of at most 2^P coordinate faces.

At a positive SUM, the zero set is the intersection of the zero sets of its
positive-weight parents. At a PRODUCT it is their union. For each of the P
PRODUCT nodes, choose one parent globally and replace that union by the
chosen parent's zero set. What remains is an intersection of source zero
faces, hence a face (possibly empty or the whole cube), contained in the
original output zero set. Conversely, at any output-zero context, choose a
zero parent at each zero PRODUCT; choices at other PRODUCTs are arbitrary.
This global choice preserves the output's zero. Taking all 2^P choices
covers the zero set. Repeated occurrences of a shared PRODUCT use the same
choice, so the proof counts DAG nodes, not unrolled tree occurrences.

If a set W of zero contexts has the property that the smallest coordinate
face containing any two of its points contains a positive context, each
zero face contains at most one point of W. Therefore 2^P>=|W|. Such W is a
directly checkable lower-bound witness. It need not be a maximum face packing.

For example, the sum of m disjoint pairwise XOR indicators vanishes at the
2^m vertices where each pair agrees. Those zero vertices are isolated in
the cube, so no positive-dimensional face is contained in the zero set.
Consequently its exact scalar PRODUCT minimum is m, attained by

`sum_i (x_(2i-1)+x_(2i)) ((1-x_(2i-1))+(1-x_(2i)))`.

This is an exact-support/mass statement, not a closure or conditional-scale
theorem. The following counterexample explains why that qualification matters.

## 2. A four-input support needs at least three PRODUCTs

Write the inputs x,y,z,w as bits, and define

`f=(1-x) y z + x (1-z) w`.

Its positive set is the two disjoint edges

`S={0110,0111,1001,1101}`;

f is one there and zero elsewhere. There is no two-dimensional coordinate
face contained in S. Every nonzero nonnegative unary-additive function, or
PRODUCT of two such functions, is positive on some coordinate face fixing
at most two bits. Hence neither can have nonempty support contained in S.

Every at-most-two-PRODUCT DAG can be flattened extensionally to

```
h1 = U V
h2 = (A+a h1)(B+b h1)
g  = C+c h1+d h2,
```

where U,V,A,B,C are nonnegative unary sums and a,b,c,d>=0. This includes
parallel products, repeated inputs, shared ancestors and SUM-only cases;
it does not assert learner or physical equivalence of the flattened graph.

Suppose supp(g)=S. Positivity and the preceding face observation force
C=0 and c h1=0. The second product must be present and nonzero. If h1 is
identically zero, h2 is just AB and is already impossible by the pairwise-face
observation. Otherwise, if a,b are both positive, h2 contains a positive
multiple of h1^2; its support
cannot fit inside S. Thus at most one parent can use h1. Exchange the two
parents if needed, so b=0. The term AB must likewise vanish identically.
The remaining nonzero output is a scalar multiple of `U V B`.

Its zero set is a union of at most **three** coordinate faces. But the zero
set of f requires at least four: take

`W={0010,0101,1100,1111}`.

For each pair of W, respectively in lexicographic pair order, the pair's
coordinate hull contains these positive witnesses:

`0110,0110,0110,1101,0111,1101`.

Thus each zero face contains at most one of the four witnesses. The assumed
two-PRODUCT support is impossible. This proof uses no SMT rejection oracle.

Three PRODUCTs realize the *exact mass*, not just its support:

`a=(1-x)y`, `b=xw`, `f=(a+(1-z))(b+z)`.

The extra terms ab and z(1-z) are identically zero by the declared source
partitions. Therefore both the exact support and exact scalar mass minima
are three.

## 3. A two-PRODUCT chain reaches that mass in the limit

For epsilon>0, use two binary PRODUCTs to multiply the three positive sums

\[
g_\epsilon=
\frac{(x+\epsilon^3 y)((1-x)+\epsilon^2(1-z))(z+\epsilon w)}{\epsilon^3}.
\]

Exact expansion on the complete cube gives

\[
\boxed{g_\epsilon=f+\epsilon(1-x)yw+\epsilon^3 y(1-z)w.}
\]

For 0<epsilon<=1/2 the only extra positive context outside S is 0101.
Its mass is epsilon+epsilon^3. In particular, no finite member has the
limiting support. The disappearing contribution cannot be deleted on the
grounds that the desired limiting support has a cheaper representation:
that representation does not exist with two PRODUCTs.

Set `e_epsilon=(1-epsilon)g_epsilon`. Since max g=1+epsilon,

`0<=e_epsilon<=1`, `||e_epsilon-f||_infinity=epsilon`.

Thus even at the uniform excess cap one, the closure of the full two-PRODUCT
mass class contains a mass whose *support* requires three PRODUCTs.
The earlier one-PRODUCT selector already had an exactly one-PRODUCT support
representation. That shortcut is now explicitly falsified for two PRODUCTs.

There is a conditional consequence that does not fix unknown scales in a
lower-bound argument. With base (1,1), uniform contexts, target
`p_1=(1+f)/(2+f)` and cap T<=3, the two-PRODUCT masses `(1,1+e_epsilon)` give

`inf_(P<=2,T<=3) L = L_Bayes`.

Their probability errors at the four positive contexts are at most epsilon/6,
and at the one leaking zero context at most epsilon/4; all other errors vanish.
Their probabilities lie in [1/2,2/3], so Bernoulli KL is at most (9/2) times
squared probability error. Averaging yields

`0<L-L_Bayes<=25 epsilon^2/512`.

This does **not** assert that the full conditional task's exact minimum is
three: different finite normalization scales are a separate existence problem.
The exact three-PRODUCT lower bound is for scalar mass/support. The exhibited
sequence does prove zero Bayes infimum for the full conditional class.

## 4. Small local coefficients and activations still permit the degeneration

For epsilon=2^-k, k>=1, realize the three tails by 3k, 2k and k halvings.
Three SUM nodes form the parents, and two PRODUCTs multiply them. A chain of
3k doublings supplies epsilon^-3. To form `(1-2^-k)g`, construct its k
successive halvings and sum those k values. The complete construction uses

`P=2`, `SUM=10k+4`, local coefficients only in `{1/2,1,2}`.

All source/intermediate features are at most two; the final excess is at
most one and the binary normalizer at most three. The exact unscaled product
is `epsilon^3 g`, and the subsequent doubling chain never exceeds g<=3/2.
Construction length and exact intermediate precision grow. This is not a
counterexample to the finite complete-state theorem or to compactness when
all nodes, slots and coefficient domains are genuinely bounded.

For comparison, exact support can give a quantitative bound under additional
explicit encoding resources. Suppose at most S weighted SUM nodes (including
readout scaling), at most P binary PRODUCTs, and every nonzero local SUM
coefficient is at least 0<mu<=1. A positive evaluation has a positive parse:
choose one positive summand at a SUM and both parents at a PRODUCT. Each
distinct SUM can occur at most 2^P times in the unfolded parse, so its value
is at least `tau=mu^(S 2^P)` on indicator inputs. Thus, if a target's smallest
positive mass is gamma and its exact support is impossible at P PRODUCTs,

`||g-f||_infinity >= min(gamma,tau)`.

An error smaller than that would force exact zero/positive agreement. This
deliberately conservative bound prices SUM construction length. It does not
apply to arbitrary tiny local coefficients, nor to rounded machine arithmetic
without a separately registered numerical argument.

## 5. Audit and research boundary

The counterexample was found by searching integer coefficient exponents in
a two-PRODUCT DAG, evaluating positive SUM by minimum exponent and PRODUCT
by addition. Removing terms absent from every leading contribution reduced
the proposal to the displayed three-factor identity. The retained evidence
is the exact identity and an independent combinatorial lower bound, not a
large search trace or an SMT success flag.

The audit checks every context, all coordinate faces, the six zero-packing
witnesses, the three-PRODUCT exact graph, actual finite-alphabet two-PRODUCT
graphs, the finite-resource positive-value bound on shared graphs, and exact
conditional errors. At k=54 a CPU float64 normalized readout equals the target
although the excess still has positive leakage at 0101. That observation is
scoped to the evaluated floating path; it cannot certify an exact real zero
pattern or authorize deletion of a claim-relevant coefficient.

General support closure at fixed PRODUCT count, sharp approximation costs,
complete physical/value reachability and the reference/AMP bridge remain
separate. No new FP semantic action follows from this counterexample.

Exact audit: `theory/numerical_checks/two_product_support_border_audit.py`.
