# Carry-free elimination and coefficient-normalized histogram precision

Status: **PROVED, SCOPED; EXACT/NATIVE/RNE AUDITS PASS; ACTUAL ARITHMETIC REGISTERED**.
This removes world enumeration
from histogram construction when the declared integer elimination fits.
It also removes global world count from the rounded readout's range bound.
It changes no native state, Foundation action or ERC-1 condition. The
prototype supplies no owned Runtime, actual CUDA or complete-class authority.

The [first histogram decoder](COUNT_HISTOGRAM_DECODER.md) computes a useful
positive polynomial but enumerates K=2^(n-1) worlds. Its physical scale and
uint32 coefficient extent explicitly target n<=16. The construction below
uses the existing positive elimination geometry to compute those same
integer coefficients, without turning every elimination operation into a
floating operation. This is a solver representation, not a different G/U.

Integer packing of polynomial coefficients is classical Kronecker
substitution; see [Dumas, Fousse and Salvy](https://arxiv.org/abs/0809.0063).
Computing a density of states by transfer matrices is also established,
for example [Creswick,1995](https://doi.org/10.1103/PhysRevE.52.R5735).
The claims here are the connection to FP's complete count learner, explicit
carry/bit/table bounds and the subsequent full-coordinate numerical law.

## 1. The polynomial computed by the complete native counts

Keep the complete signed counts d, actual query(i,j), pending information,
clocks and history. Let H=SUM_e |d_e| and pin the native gauge z0=0. Define

    E_d(z) = SUM_e |d_e| * 1[z_u XOR z_v = 1[d_e<0]],
    P_y(X) = SUM_(z:z0=0, z_i XOR z_j=y) X^E_d(z)
           = SUM_(k=0)^H h_y(k) X^k.

Every coefficient is a nonnegative integer; SUM_(y,k) h_y(k)=K. The native
positive partition is exactly Z_y=P_y(9). The histogram remains only a
current-query plan. Equal current histograms can have different legal
future forecasts, as the earlier counterexample proves; no count is erased.

Use any declared complete elimination order, keeping the free query
endpoints. Replace each existing factor9^|d_e| by the monomial X^|d_e|,
and keep every positive join and binary sum. Distributivity gives P_y(X).
An empty elimination bucket contributes2, so isolated variables remain
counted. A canceled edge contributes1 for this query but keeps its state
coordinate and future updates.

## 2. A sufficient and necessary uniform digit width

Take w=n and B=2^w. Execute the same integer circuit with factor
B^|d_e|=2^(w|d_e|). Then its two final integers are P_0(B),P_1(B), and

    h_y(k) = (P_y(B) >> (w*k)) & (B-1).                         (1)

**No-carry proof.** At every elimination stage an entry counts assignments
to an already eliminated set, grouped by their accumulated integer energy.
That set has at most n-1 variables, so each coefficient is at most K<B.
The original edge factors occur once. Eliminated-variable sets belonging
to different live messages are disjoint: when a variable is eliminated,
all factors containing it enter its sole outgoing message. Multiplication
therefore forms products over disjoint eliminated assignments, and summing
the two current values counts distinct assignments. The same argument
covers partial joins, parity accumulation and the final total. Degrees
never exceed H. Consequently no coefficient produces a carry into another
energy digit. Evaluating this positive polynomial circuit at B is exact;
integer digit extraction recovers every coefficient, including zeros.

The width n is the smallest power-of-two digit width that works uniformly
for this family **including diagonal queries**. With all counts zero and
a diagonal query, P_0(X)=K. A width w<=n-1 has B<=K and cannot store that
coefficient as a single digit. At w=n-1 it produces a zero constant digit
and a spurious degree-one digit1. This lower bound concerns fixed-width
coefficient fields, not all integer encodings or all query-specific choices.
The diagonal forecast alone would not verify these coefficients.

Since the sum of coefficients of any intermediate is at most K and degree
at most H, every intermediate is at most K*B^H, hence needs at most

    beta = n*(H+1) bits.                                      (2)

The prototype checks this envelope before its first power/table value and
again on actual results. Native reference evaluation at9 and exact-RNE
fractions have their own additional bound; it requires
`max(beta,16H+8n+1024)<=32768` before execution.

## 3. What the integer resource law does and does not remove

Let M,S,C,J denote the existing plan's number of integer multiplications,
additions, peak live table cells and maximum join cells. Packing changes
none of these quantities: shape depends only on the active support, query
and declared order. The identical shape-only preflight applies before
numerical allocation. Each planned table value has at most beta bits, so
its fixed-field payload envelope is C*ceil(beta/8) bytes. Packed roots,
coefficient output, masks, metadata and arithmetic scratch are additional;
this is not a Python heap or complete Compiler residency bound.

The method performs M+S wide integer operations plus initial shifts and
coefficient extraction. With an integer multiplication cost mu(beta), a
conservative bit-work upper bound for arithmetic is

    O(M*mu(beta) + S*beta + (|support|+H+1)*beta),                (3)

apart from explicit geometry/index work. The last term covers full-width
shifts and the prototype's digit extraction, even without an optimized
linear-time unpacker. Schoolbook multiplication gives mu(beta)=O(beta^2).
The scalar tariff M+S is therefore not a bit-time claim. The bound is
pseudopolynomial in H when counts themselves are binary encoded.

No K-world traversal occurs. Nevertheless large elimination width can still
defeat the cell/work budget, and large nH can defeat the bit budget. Under
the default4096-cell join cap, dense n16 still refuses before execution;
the earlier Gray decoder handles that particular case. Neither method is
an all-decoder lower bound or a reason to discard correlations. No order
optimality or hidden order search is claimed by the prototype's fixed order.

## 4. A scale that includes coefficient magnitude

The old histogram scale9^-U, U=max occupied energy, controls powers but not
large coefficients. For n256 with all counts zero, both nonloop partitions
have coefficient2^254. Extending that old floating schedule outside its
declared n<=16 class overflows even though the native forecast is1/2.
This does not falsify the original scoped theorem.

For each nonzero term h at degree k, form exact integers

    D = 9^(U-k),    a = h/2^bit_length(h),
    b = 2^(bit_length(D)-1)/D,
    e = bit_length(h)+1-bit_length(D).

Then h*9^(k-U)=a*b*2^e, with a in[1/2,1), b in[1/2,1]. Compute the integer
E=max e over all nonzero terms. Normalize every term by the same2^-E.
Its exponent becomes e-E<=0, and at least one exact term is at least1/4.
If L is the number of nonzero terms, the exact total lies in[1/4,L].
Coefficient bit length and count magnitude no longer enter this range.
All integer constants and the maximum scan remain actual preprocessing.

Ingress a,b in binary32, cast both to binary16, multiply there, widen to
binary32, then scale by the exact binary power2^(e-E). As before, an
exponent below-149 uses+0: the mantissa is at most1, so the exact scaled
value is at most half the least single subnormal and rounds to zero.
Balance the positive binary32 sums and perform the same shared denominator,
native seven-coordinate readout and three observation gradient forms.

This is a separately specified numerical schedule. It need not reproduce
the old histogram words; it is not a transparent patch to a registered
physical prefix. Its prediction count remains

    floating outputs = 9L+21-2b_parts,    half outputs = 3L.     (4)

In particular H<=396 gives at most7163 outputs for any admitted n. The
additional common exponent is an integer plan calculation, not a new native
operation. Full native parameters and caches still have their point decoders
and explicit-output costs; preserving a compact plan is not free K-output.

## 5. Uniform full-coordinate precision, conditional on integer resources

Use u=2^-24, v=2^-11, tau=2^-150 and d=ceil(log2 Lstar). Both a and b may
now require binary32 ingress rounding. For L<=Lstar<=32768 define

    epsilon = (1+v)^3*(1+u)^(d+2)-1,
    eta = 4*Lstar*tau*(1+u)^d,
    A = 2*epsilon/(1-epsilon-eta),
    Btail = eta/(1-epsilon-eta),     Dq=A/4+Btail.

The factor4 accounts for the exact scaled total's lower bound1/4.
The half mantissas/products remain normal and in[1/2,1] /[1/4,1]. Positive
single additions have relative error at most u, including subnormal sums;
their exact subnormal sums are representable multiples of the least
subnormal. Scaling contributes at most tau in absolute error per term.
Thus the earlier histogram cross-multiplication proof gives

    |q_actual_before_readout-q_native| <= A*q_native*(1-q_native)+Btail.

There is no division by a possibly underflowed rare partition. The total
remains positive, and every partial sum is below2Lstar, so no float overflows.
Let kappa=2u/(1-u), R=8*(kappa+tau)+9u. Exactly as in the original complete
readout proof, the actual coordinate bounds are

    native excess/mass       <= 8Dq+R,
    normalizer               <= 2R+18u,
    probability              <= (4/5)Dq+R/(10-2R)+kappa+tau,
    proper-mass vs word      <= kappa+tau,
    every native gradient    <= 64*(A/36+Btail)/(1-8Dq)+8R+18u. (5)

The gradient bound uses the exact identity
`(1+8q)^2-36q(1-q)=(1-10q)^2`. The fixed slot and both labels are covered.
Counts and clocks remain exact; no parameter-rounding error accumulates
through the unchanged native count update. Actual rounded marginals stay
in[0,1], excesses in[0,8], masses in[1,9], and both normalizer forms at most18.

For Lstar32768, outward bounds are native0.005877, normalizer0.000004054,
probability0.000587760 and gradient0.005266. These meet the existing1/100
state and1/1000 probability tolerances uniformly over admitted n and count
magnitudes, conditional on the proved integer/table/output resources and
the declared RNE primitives. Actual CUDA conformance and owned execution
remain separate obligations. Foundation R4/ERC-1 are unchanged.

## 6. Reproducible evidence and boundary

The prototype is [packed_count_histogram.py](../../experiments/joint_uncertainty/packed_count_histogram.py).
Its [audit](../../experiments/joint_uncertainty/audit_packed_count_histogram.py)
compares small complete signed states and ordered queries with independent
lexicographic worlds, checks complete native history/cache/gradient phases,
and replays exact half/single arithmetic for both targets. Larger fixtures
use an independent vertex-prefix coefficient DP, binomial coefficients or
closed constant/one-edge coefficients, plus the existing native-base integer
decoder. No full-world builder is used for the large fixtures.

The audit separately checks refusal before integer entry for insufficient
bits, span, table cells and work; a short floating-output allowance refuses
before rounded entry. It preserves the dense width refusal, the too-short
digit counterexample and the failure of the old scale outside its class.
The [minimal artifact](../../evidence/minimal/FP_PACKED_COUNT_HISTOGRAM.json)
retains compact counts, bounds and reconstructible fixture summaries.
No weights, table dumps, cache or large operation logs are evidence artifacts.

The completed CPU audit checks all759 ternary count states and11919 ordered
queries through n4,48 generated dense cases through n8, and five larger
fixtures. All11972 predictions and23944 both-target observations pass exact
RNE and the full native-coordinate relation:1071311 words including copies,
183495 half words. Maximum observed probability error is about8.98242e-5
and gradient error about0.00048425, below the proved uniform bounds.
The independent literal native control matches1054 full cache/observation/
commit triples, including three profile attachments and a104-event reversal
through an underflowed transient. Five pre-numeric refusals, one width
refusal and one floating-output refusal also pass.

| Fixture | Terms | Maximum integer bits | Largest join | Floating outputs |
|---|---:|---:|---:|---:|
|n32 signed band, H76|119|2433|8|1088|
|n64 signed band, H156|247|9985|8|2240|
|n128 path, H127|128|16257|4|1169|
|n256 empty counts|2|256|2|35|
|n256 one count80|2|20735|2|35|

These execute the generic algorithm, with no graph-family branch in the
prototype. The distinct fixture oracles are independent audit controls.
They are arithmetic/scaling evidence, not larger-model completion or
native construction under full logical graph and whole-resource caps.

## 7. Registered actual arithmetic gate

After committing its inputs, run `python -X utf8 -B
scripts/audit_packed_histogram_cuda.py --attempt 1`. Register exactly one
fresh4-GiB/600-second job, one16-MiB arena/32-MiB allocator allowance,
65536 outputs per phase and the existing1/100 and1/1000 relations. Its
forward identity is `packed-count-coefficient-normalized-histogram-rne16-rne32-v1`.
Reuse the existing trusted primitive/endpoint audit runner with explicit
decoder and independent-oracle adapters; no old physical outcome is reused.

The16 fixed cases are the two n3 prior queries; both signs at n2 counts46,
47,48; n2 count396; the n32/n64 signed bands and n128 path above; both n256
empty-count query types; and n256 one-edge counts+80/-80. Each has one
prediction and both independent target-observation branches, for48 phases.
The CPU preflight checks all16 predictions/32 observations and independent
coefficients before registration. No n>16 oracle enumerates worlds.

Rebuild every physical plan from counts, compare every actual primitive word
with exact RNE, capture fresh arena endpoints, and check all native readout
and gradient coordinates. Retain compact words, actual job/device identity
and every failure or resource termination. Keep source fixed through
terminal collection, with no silent retry or cap relaxation. A separate
`--read PATH` checks the208 retained endpoint words without device execution.
No actual result, Runtime ownership, fresh/install or model score is assumed
by this registration; the new schedule cannot borrow the older n16 gate.
