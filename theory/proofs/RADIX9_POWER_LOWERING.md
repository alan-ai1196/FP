# Exact radix powers remove repeated half rounding

Status: **PROVED, SCOPED LOWERING AND PRECISION LAW; EXACT/ACTUAL CUDA AUDITS**.
The sole new CUDA diagnostic completes at0c49618. Earlier
radix diagnostics are terminal and remain unchanged, including their actual
[accuracy failures](RADIX9_ACCURACY_ENCLOSURE.md). No Runtime, native graph,
source interface, optimizer semantics or frozen ERC contract is changed.

The previous positive count decoder multiplies finite mantissas in FP16
even when one operand is a known exact power of9. This repeatedly rounds
the *other* operand, despite an available exact exponent shift. A static
invariant removes those operations. The remaining rounding has a much
smaller structural budget, and positivity converts the mass error to an
absolute forecast bound. In the256-cycle counterexample's fixed tape, the
new uniform bound is below0.000883 for every admitted signed count vector.

## 1. The invariant is about exact values, not rounded appearances

Use the same integer-count input and positive elimination tape as in
[the original decoder](RADIX9_FRONTIER_PRECISION.md). Mark literal1,
literal9 and every likelihood input9^d as a proved power. A PRODUCT of
two proved powers is a proved power. A SUM is conservatively unmarked;
literal0 is also unmarked. The marks depend only on the tape's syntax,
not the current floating values, count magnitudes or target outcome.

Induction establishes that every marked node has exact value9^e and is
represented without error by mantissa1 and integer exponent e, for every
legal count assignment. Whenever at least one PRODUCT input is marked,

`(m*9^a) * 9^b = m*9^(a+b)`.

The lowering shares the other operand's immutable mantissa object and adds
the integer exponents. It performs no mantissa cast, multiplication or
normalization. Zero keeps its canonical exponent0. The original input and
conservative per-product exponent guards remain; overflow is unresolved.
If neither operand is marked, the original FP16 casts/product and FP32
normalization execute unchanged. All SUMs and final readout also retain
their original schedules.

The count coordinates and all tape nodes remain present. In particular,
the shifted exponent still depends on the input factor, whose count can
change in a later decode. This is a proved numerical lowering of PRODUCT,
consistent with `FP_THEORY.md` VII: a semantic PRODUCT need not survive as
a hardware multiplication. It is not deletion of a native value-one feature,
its derivative or its possible future parameter direction.

A rounded mantissa1 alone is not this invariant. For example,1+9^16 and
1+9^32 both decode to mantissa1 after small-addend omission, but neither
exact value is a power. Their product stays unmarked and receives a general
product/error budget. The audit checks this distinction explicitly. No
current numerical coincidence is promoted to an all-continuation identity.

The exact target is unchanged, but the physical operation words intentionally
change. The new schedule cannot borrow the old AMP trace as its own evidence.

## 2. Separate the two sources of rounding

Let u16=2^-11 and u32=2^-24. Assign an error-budget pair(H,S) to each node;
H counts general product contributions and is **not** history length.
The theorem assumes the declared RNE primitives. A finite device audit
checks its actual operations; it does not prove every possible future GPU
word without those same arithmetic premises.

- Inputs have(0,0).
- An exact power shift inherits the other input's pair; the proved power
  contributes no error.
- A general PRODUCT adds its input pairs and then adds(1,0).
- A SUM takes componentwise maxima of its input pairs and adds(0,1).

For every positive exact node value v and its represented value v_hat,

`(1-u16)^(3H)*(1-u32)^(2H+19S) * v <= v_hat`

and

`v_hat <= (1+u16)^(3H)*(1+u32)^(2H+19S) * v`.

Each general product has two half casts, one half product and at most two
single divisions. Each aligned sum has at most15 coefficient divisions,
one alignment product, one addition and two normalizations. If its exponent
gap is at least16, the omitted relative contribution is below9^-15<u32,
also enclosed by the19-factor bound. All relevant nonzero values are normal
and finite as in the original proof. Positivity makes the componentwise
maxima at SUM valid; no independence of rounding errors is assumed. Zero
is exact and satisfies the corresponding zero-valued inequalities.

Let(H,S) be the componentwise maximum at the two noisy mass heads, and set

`eta=3H*u16+(2H+19S)*u32`.

For eta<1, products of(1-u) factors are at least1-SUM(u), while products of
(1+u) factors are at most1/(1-SUM(u)). The latter follows by induction from
`(1+x)/(1-y) <= 1/(1-x-y)` for nonnegative x,y with x+y<1.
Both computed masses therefore lie between(1-eta) and1/(1-eta) times
their exact counterparts. The budget depends on actual tape structure,
not the count magnitudes. If eta>=1, this bound is unresolved.

## 3. Positive normalization yields an absolute probability law

Let p be the exact probability and q the exact normalization of the two
computed positive mass values, before the final rounded total/division.
Their odds differ by a factor between kappa^-2 and kappa^2, where
`kappa=1/(1-eta)`. For positive odds this implies

`|q-p| <= (kappa-1)/(kappa+1) = eta/(2-eta)`.

For completeness, in the upper-odds case the difference is
`p(1-p)(kappa^2-1)/(1+(kappa^2-1)p)`.
Bounding it by(kappa-1)/(kappa+1) is equivalent to
`[1-(kappa+1)p]^2>=0`. The lower-odds case is symmetric.

Put epsilon_s=2^-19. Exact inequalities give
`(1+/-u32)^19` inside `1+/-epsilon_s`, and the omitted-tail bound is smaller.
Thus the final wide SUM has relative error at most epsilon_s. The existing
head-ratio proof still gives an exponent gap of0,1 or2 at the final division;
scaling the head by9 is now exact. The final scalar division/coefficient
product has at most four single-rounding factors, also covered by epsilon_s.
Consequently the returned probability a satisfies the uniform absolute law

`|a-p| <= eta/(2-eta) + 2*epsilon_s/(1-epsilon_s)`.

This is the result returned by `uniform_error_bound`. It is a sufficient
bound for the fixed tape and all count vectors accepted by its guards, not
an optimal precision law over all physical implementations.

For the256-cycle support and query(0,96), static analysis gives(H,S)=(1,256).
There are3,300 exact-shift nodes and two remaining general product nodes;
each expanded mass contribution contains at most one of those general
products. The theorem's bound is exactly

`7751553917/8788358216065 < 0.000883 < 0.001`.

This covers arbitrary positive, negative and zero signed counts on that
fixed support, not just the tested frustrated pattern. The effect is not
explained solely by a fortunate device result. Conversely, the512-cycle
query(0,128) has(H,S)=(1,512), for which the bound is about0.00102726.
The uniform0.001 question remains unresolved by this bound there, even
though its particular tested forecast passes the independent binary64
enclosure. General tapes with larger H can also need more precision.

A later observation on an additional edge changes the support and requires
a new tape and budget. The complete count state still retains that event;
the cycle bound cannot be carried over to a chorded graph by ignoring it.

## 4. Exact node audits and retained controls

Run `python -B experiments/joint_uncertainty/radix9_power_lowering.py
--output evidence/minimal/FP_RADIX9_POWER_LOWERING.json`.
The [CPU evidence](../../evidence/minimal/FP_RADIX9_POWER_LOWERING.json) checks:

- 1,125 forecasts from every triangle count vector in{-2,-1,0,1,2}^3 and
  all nine ordered queries. All35,000 exact node enclosures pass, including
 23,000 proved-power node checks. Maximum forecast error is below4.507e-8.
- 405 forecasts from81 signed profiles on edges01,12,13,14 at n5, with
  queries01,14,23,00,44. All26,406 node enclosures and16,686 proved-power
  checks pass. These include genuine general mantissa products, both signs,
  zero counts and diagonal queries. Maximum error is below8.345e-8.
- The false inference from rounded mantissa1, local exact inequalities and
  an explicit refusal of an exhausted mixed-rounding bound.

No exact node value is used to execute the AMP machine; it is an independent
post-operation check of the resulting state and static budget. Primitive
rounding is checked separately by the original exact machine.

The four retained80f9538 stress references are read, not re-executed. Their
checked binary64 enclosures certify the new outputs at the identical inputs.
The additional512-cycle row executes85,800 new checked binary64 primitives
and compares with independent exact integer inference. Its old baseline is
explicitly the retained CPU AMP-machine search, not an old GPU outcome.

| Case | New exact AMP-machine output | Certified absolute error upper |
|---|---|---:|
| triangle, h10^12 |5312785/8388608|7.948e-9|
|64-cycle query(0,16), h10^12 |11744051/16777216|1.193e-8|
|256-cycle query(0,96), h16 and10^12 |10065811/16777216|0.000030911|
|512-cycle query(0,128), h8 |183517/262144|0.000061799|

The original256-cycle error exceeded0.0022741198408. Its source and failed
accuracy outcome remain retained. On the first four matching forecasts,
rounded scalar results fall from52,552 to7,660. This operation-count change
excludes exponent additions, static analysis, metadata, alias storage and
all other physical costs. It is not a speed or whole-job memory comparison.

The large-count states are synthetic reachable states. No trillion-event
history, replay resources, fresh evidence or installation is inferred from
their compact description. Complete native caches, gradients and phase
records remain separate obligations of any future owned realization.

## 5. Fixed actual mixed-precision diagnostic

Commit this proof, both new scripts and the CPU report before running
`python -B experiments/joint_uncertainty/run_radix9_power_lowering.py`.
The diagnostic must reproduce all1,530 small forecasts, exact node checks
and the five stress forecasts above on actual CUDA. Every new floating
operation/selection word must match the independently executed exact RNE
machine. Proved power products must share the actual mantissa object and
use guarded host exponent addition; every remaining general product uses
FP16 casts/product, with FP32 sums and normalization. Some tapes, including
the triangle, have no remaining general product and correctly issue no
half multiplication. The star and larger cycles exercise that mixed path.

One source-bound Windows job attaches before resume, with one active process,
4 GiB process/job commit and240 seconds. Record identity, terminal accounting,
Torch peaks and all failures. No old diagnostic is restarted, no threshold
changes, and no exclusive-device timing or memory advantage is claimed.
The source-bound reader must match every retained CPU result other than its
new positive device-word count. A passing diagnostic proves this numerical
realization only; it does not issue Runtime, native-state/AMP or installation
authority. The [terminal record](../../evidence/minimal/FP_RADIX9_POWER_LOWERING_CUDA.json)
contains the completed outcome below. It was pending at the initial proof
commit; the registered cases, thresholds and limits did not change.

## 6. Completed actual mixed-precision outcome

The sole attempt completes at source
`0c4961890bf8b16fa84a3f549f83a19546ab1506` on RTX3090, Torch2.12.0+cu132,
CUDA13.2. All209,197 actual floating-word checks match the exact machine,
including105,136 rounded scalar results. The1,530 small forecasts reproduce
all61,406 exact node enclosures and39,686 power checks. All five stress
forecasts reproduce their certified intervals and pass0.001, including the
two256-cycle inputs whose old physical schedule failed. Their new actual
probability is10065811/16777216, with certified error below0.000030911.

The first four matching stress inputs check18,992 actual floating words,
versus78,848 in the retained80f9538 schedule. Rounded scalar results change
52,552 to7,660 as predicted. Host exponent additions and static-plan/alias
metadata remain real work and storage; these counts are not total resource
dominance. The512-cycle's pointwise outcome passes, while its larger uniform
bound still does not decide the full0.001 class.

Worker25280 exits0 after attachment before resume, with no timeout, limit
termination or reader exception. Completed process/job commit peaks are
2,205,425,664/2,206,646,272 bytes under4,294,967,296. Torch allocated/reserved
peaks are930,304/2,097,152 bytes. The child includes static analysis, host
metadata, exact node/oracle work and85,800 new checked binary64 primitives;
the launcher is outside this measurement. Raw total_processes=2 and
limit_terminated_processes=0 remain recorded under the one-active-process
cap. No whole-job memory advantage or timing comparison is inferred.

The terminal journal is15,118 bytes. This diagnostic and both older radix
diagnostics are terminal and must not be restarted. The owned complete-state,
phase, persistence and installation bridge remains a separate requirement.
