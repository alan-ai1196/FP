# Sharp precision composition for independent binary parity responses

Status: **PROVED, SCOPED; EXACT RATIONAL AUDIT PASS**. This is a numerical
composition theorem for the existing query-block response algebra. It
changes no Foundation definition, ERC-1 condition, Runtime action or
physical schedule. It does not assign an unaudited error budget to the
current projected AMP kernel or implement a projected histogram backend.

The [query boundary theorem](QUERY_BOUNDARY_RESPONSE.md) proves when the
current native parity response is proportional to a convolution of positive
block pairs. All native counts and future interfaces remain. That semantic
premise is essential: pointwise likelihood products have a different law.

## 1. A maximum law for projective errors

For a positive pair a=(a0,a1), write ell(a)=log(a0/a1). Its binary Hilbert
distance from a' is h(a,a')=|ell(a)-ell(a')|. Common positive scale is
irrelevant. Define the existing parity convolution

    a star b = (a0*b0+a1*b1, a0*b1+a1*b0).

For any B positive input pairs and perturbed positive pairs,

    h(star_i a_i, star_i a'_i) <= max_i h(a_i,a'_i).                 (1)

The constant1 is optimal for every B>=1. There is no factor B in (1).

**Proof.** Put x=tanh(ell(a)/2), y=tanh(ell(b)/2). The output log odds is
f(ell(a),ell(b))=2*atanh(x*y). Differentiation gives

    |d_1 f|+|d_2 f|
      = ((1-x*x)*|y|+(1-y*y)*|x|)/(1-x*x*y*y)
      = (|x|+|y|)/(1+|x*y|) <= 1.

The final inequality is (1-|x|)(1-|y|)>=0. Integrate this gradient along
the segment between the two input log-odds vectors to obtain a1-Lipschitz
map in the maximum norm. Induction over any binary convolution tree proves
(1). For sharpness, perturb one finite input while all other pairs tend
to(1,0), the exact convolution identity. All approximating pairs can be
strictly positive. Their output error tends to the perturbed input error.
Thus the sharp constant is a supremum, not necessarily attained internally.

The tanh/atanh operation is the classical binary parity-check update; see
[Ruffer, Dower, Kellett and Weller,2010, equation(1)](https://bjoern.rueffer.info/publications/pdfs/rufferdowerkellettweller2010-on-robust-stability-of-the-belief-propagation-algorithm-for-ldpc-decoding.pdf).
No novelty of that operation or general loopy-BP stability is claimed.
The elementary proof here isolates the precision implication used by FP.

This fails for pointwise products over the **same** latent variable.
Take every exact pair(1,1) and approximate pair(R,1), R>1. Each local
distance is log R; multiplying B such likelihoods gives distance B*log R.
Typed causal separation, not positivity alone, licenses (1).

## 2. Sharp transfer to the native readout and gradients

Let q=a0/(a0+a1), q'=a'0/(a'0+a'1) and h(a,a')<=delta. Put
t=tanh(delta/4). The binary case of the existing
[Hilbert/TV law](LIKELIHOOD_INFORMATION_LAW.md#5-a-uniform-future-error-bound-with-its-correct-geometry)
gives the following sharp constants:

    |q-q'|                         <= t,
    |8q-8q'|                       <= 8t,
    |(1+8q)/10-(1+8q')/10|        <= (4/5)t,
    |1/(1+8q)-1/(1+8q')|          <= (8/9)t.                     (2)

For a direct proof, write r=q/(1-q), s=exp(delta/2)>=1. The largest
sigmoid difference between odds r and s*s*r is (s-1)/(s+1), attained
at r=1/s. Also

    1/(1+8q) = 1/9 + (8/9)/(1+9r).

The reciprocal difference has the same optimum after replacing r by9r;
it is attained at r=1/(9s). Thus the nonconstant native target-gradient
forms G_fixed=1/(1+8q)-1/5 and G_match=4/5-8/(1+8q) have sharp bounds
(8/9)t and(64/9)t. G_other=4/5 has zero exact error. The probability and
gradient extremizers differ; a global derivative bound would lose this
structure. Both labels are covered by swapping coordinates.

These are exact readout bounds. Actual divisions, stored masses, rounding,
endpoints and phase conformance remain separate physical obligations.

## 3. Underflow has a different, sharp composition law

For normalized binary pairs, let TV(p_i,p'_i)<=e_i<=1/2. Either pair may
have a zero. Then

    TV(star_i p_i, star_i p'_i)
      <= Phi(e_1,...,e_B) = (1-PRODUCT_i(1-2e_i))/2.              (3)

This is sharp, and is generally larger than max_i e_i. Couple each binary
pair maximally, so its mismatch probability is its TV distance. Choose
these couplings independently across the proven independent inputs. The
two output parities differ exactly when an odd number of inputs mismatch.
Its probability is Phi of the individual distances, and bounds output TV.
Phi is increasing in each argument on[0,1/2]. Equality is attained when
one distribution in every input is the point mass at0 and the other puts
mass e_i at1. The positive-reference/rounded-zero case attains it; if both
sides must be positive the same value is approached as a supremum.

For two small equal underflow tails e>0, the output error is2e(1-e)>e.
Thus a largest-local-absolute-error claim is false even with two blocks.
For e=2^-150 this remains an exact rational counterexample in the stated
positive-pair class, not a claim that this exact pair is reachable from
the fixed count initializer. A zero against
a positive reference has infinite Hilbert distance, so (1) cannot absorb
this case by assigning it a finite relative error.

## 4. Rounded trees: a path law and an absolute-error recurrence

The following premise describes a numerical realization; it does not
assert that a particular kernel satisfies it. At a leaf choose an ideal
positive response t_i with h(t_i,p_i)<=delta_i and an actual normalized
response s_i with TV(s_i,t_i)<=e_i. At an internal node v let

    t_v = normalize(D_v * (t_left star t_right)),
    s_v differ in TV by at most eta_v from
          normalize(D_v * (s_left star s_right)),

where D_v is a positive diagonal multiplier, '*' is pointwise multiplication,
and rho_v=max(D_v[0]/D_v[1],D_v[1]/D_v[0]) is bounded. These can be
a-posteriori error factors, not arithmetic inputs or new native actions.
They may depend on the actual computation. Use the same realized D_v in
the mathematical ideal tree. The reference tree has no D_v factors.

Applying (1) then the triangle inequality gives

    Delta_v <= log(rho_v)+max(Delta_left,Delta_right),
    Delta_root <= max_leaf (delta_leaf + SUM_path log(rho_v)).    (4)

The latter is sharp as a supremum for this independent node-error model:
let every branch off a maximizing path tend to the parity identity and
align all log-odds perturbations along that path. With a common leaf bound
delta and node bound gamma, a tree of depth d has bound delta+d*gamma.
Among binary trees with B leaves the minimum possible maximum depth is
ceil(log2 B): B<=2^d is necessary and a balanced tree achieves it. A serial
fold instead has depth B-1. These are conditional precision laws, not
physical storage or execution-time bounds, nor lower bounds for a fixed
deterministic RNE kernel whose errors might not align independently.

For the absolute errors let c_v=e_left+e_right-2e_left*e_right when both
child bounds are at most1/2. Otherwise use c_v=min(1,e_left+e_right).
A common binary reweighting of ratio spread rho maps TV error c to at most

    T_rho(c) = rho*c/(1+(rho-1)*c).

To prove this, orient the favored coordinate so rho>=1 and use
g(q)=rho*q/(1+(rho-1)*q). It is increasing and concave; an interval of
length c has largest image length g(c)-g(0). Coordinate reversal handles
the other orientation. This bound is sharp, including boundary inputs.
Consequently a valid recurrence is

    e_v <= min(1, eta_v+T_rho_v(c_v)).                           (5)

Omitting the reweighting factor is unsound: local relative rounding can
amplify an inherited absolute tail. Equations(4)--(5) keep those effects
separate. With all rho=1 and eta=0, (5) reduces to the sharp (3).

At the root put t=tanh(Delta_root/4), e=e_root. The pre-readout native
excess/mass error is at most8(t+e), noisy probability error at most(4/5)(t+e),
and largest gradient error at most(64/9)t+64e. The last term uses the
global derivative bound8 of1/(1+8q) only for the absolute tail. Registered
readout-rounding bounds must still be added.

## 5. What this supplies to histogram and projected decoding

The [histogram proof](COUNT_HISTOGRAM_DECODER.md) writes each actual block
partition as s_y=(1+theta_y)*Zbar_y+error_y, with |theta_y|<=epsilon,
SUM_y|error_y|<=eta and Zbar_0+Zbar_1>=1. Its positive virtual pair
t_y=(1+theta_y)*Zbar_y therefore has projective error at most

    delta = log((1+epsilon)/(1-epsilon)),

and its normalized distance from the actual pair is at most

    e = eta/(1-epsilon-eta).

These require positive reference partitions and epsilon+eta<1. A diagonal
query's exact(1,0) identity is handled directly, outside finite log odds.
The latter bound follows by cross multiplication;
the actual sum is at least1-epsilon-eta. An exact convolution of any number
of such blocks has relative error controlled by the largest delta and
absolute error by (3). This is a theorem even when a block underflows.
The number of blocks still enters work, evidence, complete native state
and absolute tails. It cannot be erased from a whole-resource claim.

The current [projected AMP schedule](PROJECTED_INDEXED_AMP.md) uses a
registered serial convolution with its own mantissa/exponent operations.
Its local operation budgets must be proved before substituting them into
(4)--(5); exact geometry alone still supplies no physical precision release.
No histogram/projected hybrid is registered or added by this result.

The reproducible audit is `python -X utf8 -B
theory/numerical_checks/audit_parity_composition.py --check`. It checks the
projective laws, sharp readout extremizers, TV composition and reweighting,
generated mixed-error trees, and the two false extensions with Fractions.
The small [artifact](../../evidence/minimal/FP_PARITY_COMPOSITION.json)
retains counts and witnesses:2401 two-block and117649 three-block projective
comparisons,3721 TV and405 reweighting comparisons,36 readout checks/eight
attaining pairs, and3840 generated mixed-error trees with30720 internal
nodes. Three explicit counterexamples prevent invalid extensions to
same-latent PRODUCT, maximum absolute-tail error and unreweighted tails.
These are rational numerical audits, not RNE or actual-device tests.
Finite checks audit the formulas; the proofs above establish their uniform
quantifiers.
