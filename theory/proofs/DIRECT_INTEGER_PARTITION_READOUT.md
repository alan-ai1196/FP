# Direct integer partitions with a uniform mixed-precision readout

Status (2026-09-23): **PROVED, SCOPED; PASSIVE EXACT/RNE CPU AUDIT PASS.**
This attacks the necessity of the histogram representation, not its proved
correctness. The six-job n64 matrix is terminal with its original source
and implementations. The subsequent [owned construction](OWNED_INTEGER_PARTITIONS.md)
has its own resource registration and continuation gates; its status is
reported there. The passive evidence below supplies no device authority.

## 1. Compute only the current response, keeping the complete learner

The complete native input remains the signed count vector d, current query,
pending information, both clocks and retained history. For n vertices,
H=sum_e |d_e| and anchored assignments z_0=0, define

    E_d(z) = sum_e |d_e| 1[z_u XOR z_v = 1[d_e<0]],
    Z_y = sum_(z:z_0=0, z_i XOR z_j=y) 9^E_d(z).

These are the same native partition integers computed by the existing
reference semantics. Positive integer variable elimination can evaluate
them directly at base9. It need not first evaluate at base2^n, retain every
energy coefficient, and then evaluate the resulting polynomial at9.

At every intermediate positive table entry, the contributing eliminated
assignment sets are disjoint across incoming messages and every original
factor is used once. There are at most K=2^(n-1) contributions, each at
most9^H. Partial joins, reductions, roots and their total therefore satisfy

    0 <= value <= K 9^H < 2^(n+4H),
    bit_length(value) <= n+4H.                                  (1)

The H=0 endpoint has bit length at most n as well. The elimination geometry,
join cells, live table cells and positive multiplication/addition counts
are unchanged. The ordinary current pair response and gradient require the
two Z values, not the whole coefficient polynomial.

This is not state erasure: neither Z nor a histogram replaces d. Every
future query or observation can still use every count, including current
zero counts. The old equal-current-histogram/different-future witnesses
continue to apply to any attempted persistent response quotient. Here only
a transient representation used to calculate one query is removed.

For *direct explicit integer* partitions, the order n+H is sharp in the
worst case. One edge with count H gives total
2^(n-2)(1+9^H); its bit length is of order n+H. This is not a lower bound
for factored, symbolic, common-scale or approximate representations. In
particular it does not license rejecting a different decoder.

## 2. Conditional storage and work savings

For the same table plan with peak live cells C, a fixed-width construction
needs C*ceil((n+4H)/8) table bytes. Two roots, descriptors, indexing and
arithmetic temporaries remain additional costs. The existing forward
compaction proof applies to the same scope/offset geometry; no coefficient
array or degree scan is required by this construction.

For a declared span cap S and integer limit I, a contiguous
implementation can allocate (C+2)*ceil(min(I,n+4S)/8) bytes for tables and
two roots, and refuse before entry when n+4H>I. At n64/S396/C1024/I32768
this is211356 bytes, compared with3264928 in the registered carry-free
layout. At n256 it is235980 versus4227904 bytes. These are representation
payloads, not measured whole-job savings. The subsequent owned construction
actually prepays these extents; its complete resources are separate below.
The direct bit bound can be larger than n(H+1) at n2 or n3, and base9
power construction does more arithmetic than a binary shift. This is not
a uniform storage/work dominance statement across all vertex counts.

If M and A are the multiplication and addition counts and mu(b) is an
integer multiplication cost, a conservative arithmetic bit-work upper is

    O((M + |support| log(H+1)) mu(n+4H) + A(n+4H)),              (2)

plus geometry, indexing, copying, normalization and output work. The extra
term constructs the base9 powers by bounded binary exponentiation. The
Python prototype's temporary heap is not certified by a table-cell count.
Width, total work, integer and complete-history limits can still refuse.

For n256, one count of magnitude128 has carry-free envelope33024, beyond
the same32768-bit allowance; the direct envelope is768. This is a candidate
execution outside the old packing class, not a contradiction of its
correctly scoped refusal. Dense n16 retains the same4096-cell join failure.

## 3. A two-mantissa floating schedule

For every positive Z_y put b_y=bit_length(Z_y), a_y=Z_y/2^b_y, and let
B=max_y b_y. Thus a_y lies in [1/2,1) and b_y-B<=0. A zero partition
(possible for a diagonal query) is represented by an exact floating zero.

For each positive partition, execute exactly these stages:

1. Ingress a_y in binary32.
2. Cast it to binary16, then widen to binary32.
3. Multiply in binary32 by the exactly representable power2^(b_y-B).
   If b_y-B<-149, use zero for that power.

Then use the existing single-precision denominator, two marginal divisions,
excesses8q_y, masses1+8q_y, normalizer and two final probability divisions.
The observation uses the existing three single-precision gradient forms.
There are29 prediction output words including the seven endpoint copies
for a nonloop query, or25 for a diagonal query; only two or one are half
casts. Integer elimination work is not hidden inside that floating count.

The exact scaled total (Z_0+Z_1)/2^B lies in [1/2,2). Mantissa quantization
cannot zero its largest term. A rare partition may underflow transiently;
all native counts and subsequent reversal information remain exact.

This is a distinct heterogeneous realization: its sum-product inference
runs in exact host integer arithmetic, and its quantization/readout runs
in mixed precision. It does not claim GPU sum-product inference, a faster
training kernel, or the old histogram arithmetic identity. A physical
implementation must independently construct the partitions from its own
complete predecessor and source query. A copied reference cache, supplied
partition pair or precomputed normalized forecast is not that construction.
The passive numerical upper does not authorize such an input port.

## 4. Uniform full-coordinate error bound

Write u=2^-24, v=2^-11 and tau=2^-150. The two mantissa roundings have
relative error bounded by

    epsilon = (1+u)(1+v)-1.

Scaling a half significand by a power of two is exact in binary32 when
normal; subnormal rounding has absolute error at most tau. For exponents
below-149 the omitted exact scaled term is at most tau as well. With two
terms and exact total at least1/2, take

    eta = 4 tau,
    A = 2 epsilon/(1-epsilon-eta),
    Btail = eta/(1-epsilon-eta),
    D = A/4+Btail.

The positive-partition cross-multiplication argument gives, for the native
marginal q and the exact ratio r of the two computed scaled partitions,

    |r-q| <= A q(1-q)+Btail <= D.                               (3)

There is no relative-accuracy assumption on a possibly underflowed rare
partition. No coefficient count, count magnitude, vertex count or depth
enters these floating constants. Those quantities still enter integer
and table resources.

The unchanged readout and gradient argument from the
[histogram precision proof](COUNT_HISTOGRAM_DECODER.md#4-uniform-precision-law)
uses only (3), positivity and the common readout. Set
kappa=2u/(1-u) and R=8(kappa+tau)+9u. It gives

    native excess/mass error <= 8D+R,
    normalizer/stored-mass sum error <= 2R+18u,
    proper/raw probability error <= (4/5)D+R/(10-2R)+kappa+tau,
    proper-versus-rounded probability error <= kappa+tau,
    every native gradient error <=
        64(A/36+Btail)/(1-8D)+8R+18u.                            (4)

The gradient bound uses q(1-q)/(1+8q)^2<=1/36; bounding only the largest
absolute marginal error would lose this structure. Both partitions and
targets are covered, including zero/underflow endpoints. Mathematical
native activations remain at most8; stored masses remain in[1,9] and their
sum/normalizer at most18. The standard readout integer guard is a separate
preflight requirement, not eliminated by (1).

Exact rational evaluation of (4), rounded outward, gives:

| Bridge coordinate | Sufficient upper | Existing tolerance |
|---|---:|---:|
|Native excesses/masses|0.001955809|0.01|
|Normalizer and stored-mass sum|0.000004054|0.01|
|Probabilities, including proper masses|0.000195701|0.001|
|Every native gradient|0.001753567|0.01|

This proves a uniform *conditional* arithmetic upper with constant floating
readout size and explicit O(n+H)-bit partition integers. It does not establish
an owned budget, complete Runtime bridge, model completion or a precision
optimum over all possible realizations.

## 5. Research consequence and evidence boundary

Histogram coefficients are useful if the claim requests them, or if a
particular realization needs them. They are not necessary for the current
fixed-base9 response and its admitted tolerances when paid exact integer
elimination is available. Computing them had introduced both an nH-bit
representation and a floating sum over occupied energies. Direct partitions
remove those costs while retaining the same full native information.

This challenges the choice of realization, not Foundation R4 or ERC-1.
The latter requires declaring arithmetic, physical work and independent
state-bound execution; it does not require an energy histogram. An
owned implementation needs its own fixed identity, prior construction
debits, pinned extents, complete plan checks, actual device arithmetic and
fresh/install continuation evidence. The existing six-job matrix keeps its
registered implementations and all outcomes; it is not retrospectively
replaced by this proposed control.

The [minimal CPU evidence](../../evidence/minimal/FP_DIRECT_INTEGER_PARTITION_CPU.json)
checks all759 ternary count states at n2..4 and all11919 ordered queries
against independent literal assignment sums. Both target observations pass
the full coordinate bridge at every cut. The sixteen earlier larger/range
fixtures also agree with their independent partition oracles, including
n32/n64 bands, n128 path and n256 cases. Two n256 count+/-128 witnesses
separate the bit envelopes while preserving the exact answer; both direct
constructions use660 actual maximum integer bits under envelope768.

In total,11937 predictions and23874 observations check644515 floating
words including copies and20869 half casts. Every error obeys its rational
bound. The dense n16 case still returns UNRESOLVED on its unchanged join
cap. These are passive algorithm and arithmetic checks, not owned event
histories or an actual GPU gate. CPU exact inference is part of the proposed
physical work and cannot be omitted in a later performance comparison.

The passive constructor and schedule are
[`integer_partition.py`](../../experiments/joint_uncertainty/integer_partition.py).
Run `python -X utf8 -B experiments/joint_uncertainty/audit_integer_partition.py`
to reproduce and compare the retained CPU artifact; it does not import or
execute Torch kernels.
