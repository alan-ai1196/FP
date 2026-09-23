# Rational likelihood coordinates without prime factorization

Status: **PROVED, SCOPED; EXACT NATIVE AND RNE32 COMPONENT AUDIT**.
The one-rational-radix restriction is unnecessary for a finite positive
rational bank. A gcd-free basis preserves the exact information law, and
positive integer weights with one joint binary scale give a selected-weight
error bound independent of history length, conditional on integer resources.
Independent scaling of the bases has an all-zero counterexample.

This is a general arithmetic component and a passive compiler prototype.
The registered Runtime/CUDA lowering still accepts its original single
radix. The component supplies no owned bridge, installation, complete-state
quotient, indexed-model release or constructor decision.

## 1. Model and the restriction being removed

Use the complete finite query/label interface, positive rational prior pi,
positive normalized likelihood bank ell_a(k), fixed native graph and unit
simplex learner from [the likelihood information law](LIKELIHOOD_INFORMATION_LAW.md).
There are K worlds and E query/label events. After T actual commits,

`w_k proportional to pi_k PRODUCT_a ell_a(k)^c_a`, `SUM_a c_a=T`.

T counts actual candidate-executed events, including profile multiplicities;
it is not necessarily the ordinary cursor. Calibration requires the declared
observation law. Replaying an observation does not create an independent
sample from that law. Native gradients, fixed slots, pending events and all
surrounding provenance/evidence remain separate coordinates.

The existing physical likelihood backend requires every prior and event
ratio to be an integer power of one registered rational radix. The joint
noise/world bank at rates 1/10 and 1/4 has independent ratios 9 and 5/6, so
it lies outside that class. This is a representation restriction, not a
failure of native SUM/PRODUCT or the unit simplex theorem.

## 2. Gcd-free construction and its bounded termination

Collect all reduced numerators and denominators greater than one from

`pi_k/pi_0` and `ell_a(k)/ell_a(0)`.

Maintain a set S of positive integers. If distinct a,b in S have gcd g>1,
replace them by the nonunit members of `{g,a/g,b/g}`, removing duplicates.
Choose the first pair in sorted order to make the implementation deterministic.
At termination write the resulting sorted bases as b_1,...,b_B.

Every old member is a product of new members, so every original integer
remains expressible. Every new member is at most an old member. For the
proof only, let P be the product of the distinct working members. Before
deduplication the replacement product is ab/g, so P falls by at least a
factor two on every split. If S_0 is the initial set and
`L=SUM_(n in S_0) bit_length(n)`, there are at most L splits, at most L
working members, and no integer exceeds the original maximum. The
implementation never constructs this potentially large P.

The final bases are pairwise coprime. Successive exact divisions therefore
recover unique integer exponents for every original rational ratio:

`r = PRODUCT_j b_j^e_j`.

They need not be prime: inputs (4,16) leave basis (4), and (36,216) leave
basis (6). No primality, perfect-power or integer-factorization oracle is
needed. Gcd-free factorization is established algorithmic work; Bernstein
gives a substantially faster algorithm [1]. We use a simple bounded
refinement with its own proof, not that paper's near-linear complexity claim.

If each input numerator/denominator has at most b bits and there are M
ratios, the simple scans take O((L+1)^3 b+M(L+b+1)) scalar division/comparison
work, including a loose bound of 2b+1 Euclidean divisions per gcd. These are
scalar operations on bounded integers, not constant-cost bit operations.
The helper additionally meters a declared primitive tariff and refuses
before exceeding it. A cap on *peak* working basis size can refuse a case
whose final basis is smaller. Input/output tables, Python objects and owner
lifetime need separate storage payment; the working-basis cap is not a heap
bound. All supplied bit/work/cell caps remain binding.

## 3. The information rank is unchanged

Let v_a[(k,j)] be the exponent of b_j in ell_a(k)/ell_a(0), and let p[(k,j)]
encode the prior ratio. Include the reference world's zero rows for convenience.
Let D_a=v_a-v_a0 for a fixed reference event, and select rho independent
rows over Q. Their sums q update by integer additions of actual event columns.
A fixed rational reconstruction matrix R gives all exponent rows:

`e(T,q) = p + T v_a0 + R q`. (1)

On reachable states these are integers. Exact rational elimination and
counter guards must refuse when their declared resources do not suffice.

For proof, expand each b_j into prime valuations. Distinct bases have
disjoint, nonempty prime support. Thus the map from base exponents to prime
valuations is injective and has full column rank. Applied separately to
every world it preserves the rank of the event-difference matrix and equality
of every likelihood-ratio product. Prior-only bases add constant offsets,
not an extra event rank. No prime expansion is performed by the algorithm.

Consequently the prior information theorem applies with exactly the same
rho and gives, at known T,

`N(T)=Theta((T+1)^rho)`, `log2 N(T)=rho log2(T+1)+O(1)`. (2)

The upper is constructive without prime factorization. The lower and
future-prediction interpretation retain that theorem's fixed-bank, exact,
complete-word-language assumptions. In particular this is not a new
fixed-error lower bound or a quotient of complete Compiler states. Keeping
T matters even when q=0: a word consisting only of the reference event can
change the posterior without changing any difference counter.

## 4. Combine first, then choose one common scale

Given the K exponent rows e_kj from (1), put

`m_j=min_k e_kj`, `A_k=PRODUCT_j b_j^(e_kj-m_j)`.

All A_k are positive integers and `w_k=A_k/SUM_i A_i` exactly. For pairwise
coprime bases, gcd(A_1,...,A_K)=1: for every prime in a base, some world
attains exponent zero in that base. This is the unique primitive positive
integer vector proportional to the posterior. Its maximum bit length is
therefore necessary for this particular exact integer materialization.
It is not a lower bound for all approximate decoders or persistent states.

Let `h_k=max(1,SUM_j bit_length(b_j)*(e_kj-m_j))`. The helper checks
`1+max_k h_k <= supplied_bit_limit` before constructing any power. Left-to-
right binary powering uses only prefixes no larger than the eventual
positive factor. Every intermediate factor and accumulated product therefore
fits h_k bits. The envelope is conservative, not an exact feasibility oracle.
Exponent differences/envelope metadata have their own finite input-size
cost; the large numerical weight powers are the guarded objects here.

For a fixed bank, e(T,q)=O(T+1), so this gives O(T+1)-bit transient integers,
O(KB log(T+2)) scalar power/multiply work after coordinate reconstruction,
and K output weight cells. Persistent information remains (2). These
transient weights are not the persistent learner. Input rows, reconstruction,
temporaries, retained state and physical evidence are additional costs.

Choose `s=max_k bit_length(A_k)` and `a_k=A_k/2^s`. Then

`0<a_k<1`, `1/2 <= max_k a_k < 1`.

The binary-scale denominator needs at most s+1 bits, covered by the preflight.
This preflight covers integer materialization and the scale, not every
temporary of the separately guarded exact rounding oracle.
There is exactly one scale across worlds and bases. This is exact host
integer computation before any single-precision arithmetic; it is not a
GPU bigint algorithm or a transfer of the reference learner's trained theta.
An eventual owner must reconstruct from its own committed coordinates,
descriptor and actual pending event.

**Counterexample to separate per-base maxima.** Consider the normalized bank

| Query | ell(label 0, world 0) | ell(label 0, world 1) |
|---|---|---|
| A | 1/3 | 2/3 |
| B | 3/4 | 1/4 |

Use complementary label-1 probabilities and a fair prior. Its native base-1
graph uses scale 12 and the existing unit simplex U. After 168 A0 events
and 106 B0 events, the odds of world 1 are `2^168/3^106`, giving posterior
approximately 0.49895593533. The two exponent rows are (0,0) and (168,-106).
Subtracting the *maximum* of each basis exponent gives weights
`(2^-168,3^-106)`. Both round to zero in binary32, even if their products
were computed exactly before rounding. The normalizer vanishes despite
the well-conditioned posterior. The joint construction instead yields
`(A_0,A_1)=(3^106,2^168)`, both 169-bit integers, with s=169.

This falsifies that proposed extension of the single-radix scaling rule.
It is not a failure of the existing registered single-radix implementation.
Exact rational-to-binary32 ingress also matters: at
`1/2+2^-25+2^-80`, direct RNE32 chooses word 0x3f000001, whereas rounding
through binary64 first chooses 0x3f000000. The existing exact ingress avoids
this double-rounding trap; a new owner must preserve that ingress contract.

## 5. A history-uniform single-precision bound

Use IEEE binary32 round-to-nearest, ties-to-even, with gradual underflow.
Let `u=2^-24`, `tau=2^-150`, and `1<=K<=2^23`. Starting from the exact
scaled a above, perform only:

1. `b_k=RN32(a_k)`;
2. `S=RN32(...RN32(RN32(0+b_1)+b_2)...+b_K)` in the declared order;
3. `hat_w_k=RN32(b_k/S)`.

Write `A=SUM a_k`, `B=SUM b_k`,
`epsilon=u+2K tau`, and `gamma=(K-1)u/(1-(K-1)u)`. Then

**`max_k |hat_w_k-w_k| <= epsilon + gamma/(1-gamma) + u + tau`.** (3)

Proof. Ingress has `|b_k-a_k|<=u a_k+tau`. Since A>=1/2, the total
absolute ingress error D satisfies D/A<=epsilon. At least one b_k>=1/2,
so B>0. For delta_k=b_k-a_k and q_k=b_k/B,

`q_k-a_k/A = (delta_k-q_k SUM_i delta_i)/A`.

The coefficients of the individual deltas have absolute value at most one,
so each coordinate changes by at most D/A<=epsilon under exact normalization.

Nonnegative additions of binary32 operands are exact in the subnormal range;
normal results have relative error at most u. The first addition to zero is
exact. The standard product expansion for the remaining K-1 errors gives
`|S-B|<=gamma B`. Also monotonic rounding implies S>=max b_k>=1/2.
Inductively S after j terms is at most the exactly representable integer j,
because each b_k<=1 and j<=2^23. Thus no addition overflows.

Gamma<1, giving `|b_k/S-b_k/B|<=gamma/(1-gamma)`. Finally b_k/S<=1, so the
last division adds at most u+tau. Adding the three bounds proves (3).

For K=2,8,128 the bounds are below 1.788140e-7, 5.364422e-7 and 7.689114e-6.
No term depends on T or the basis count. That does not grant unbounded
integer work, precision or memory. Every readout starts from preserved exact
coordinates, so a rounded zero cannot become an absorbing learner state.

The result covers the selected master weights only. It neither gives a
uniform bound for half-precision native forward caches/ambient gradients nor
replaces the full phase bridge. It also does not promise a better pointwise
error than another registered decoder. Normalized rounded weights need not
sum to exactly one; subsequent native mass/normalizer work must be audited.

## 6. Executable evidence and the remaining ownership boundary

Run `python -X utf8 -B experiments/joint_uncertainty/coprime_likelihood.py --write`.
The small [artifact](../../evidence/minimal/FP_COPRIME_LIKELIHOOD.json) retains:

- 7,839 exact gcd-free factorizations, including overlapping factors,
  rational/order/duplicate inputs and a 188-bit composite left unfactored;
- 2,406 exact integer plans, 2,401 complete three-world exponent vectors,
  83 underflow/tie vectors, widths 2/8/128, six budget refusals and nine
  malformed-input refusals;
- ten finite native banks with exact cache, all-slot gradient and commit
  checks, including nonuniform priors, duplicate worlds, multiple labels,
  zero event rank, and both unknown-noise PRODUCT graphs;
- independent prime-valuation ranks and literal likelihood-word posteriors,
  plus actual affine-head derivation checked against an independent native
  reverse-derivative analyzer;
- the complete 274-event counterexample/recovery word. One selected readout
  is zero at cuts 149 through 179; it recovers because its exact coordinates
  were retained. The endpoint single-precision error is below 1e-10.

The finite-bank prefix checks cover 3,051 native phase triples, with another
274 on the reversal word. The audit cross-checks 63,876 RNE decisions using
independent integer quotient/tie calculations. It imports no Torch and
executes no device or new Runtime path. Numerical audits test the stated
theorems; the proofs above supply their all-input scope.

The next implementation obligation is general rational-bank ownership:
derive the descriptor from actual G/Gamma/U and the complete information
interface; prepay derivation and every transient integer decode; preserve
complete phases and descriptor identity; register a distinct physical
arithmetic identity; audit actual AMP transitions, fresh persistence and
installation. No helper output currently authorizes those operations. The
new representation must not silently enter the old one-radix CUDA identity.
Foundation R4 and ERC-1 remain unchanged.

## Source

[1] D. J. Bernstein, *Factoring into coprimes in essentially linear time*,
Journal of Algorithms 54 (2005), 1–30,
[primary publication](https://www.sciencedirect.com/science/article/pii/S0196677404000732),
[author manuscript](https://cr.yp.to/lineartime/dcba-20040404.pdf).
