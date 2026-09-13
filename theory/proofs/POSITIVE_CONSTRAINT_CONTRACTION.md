# Positive constraint contraction of a native window posterior

Status: **scoped model/representation theorem, exact numerical audit and three
completed owned RTX3090 controls, including the stronger centered model**. This is
neither a new Foundation/ERC theorem nor an implemented Compiler proposer.
The question is how to realize useful uncertainty without enumerating all
latent worlds or importing their numerical posterior state.

## 1. Integrate the latent constraint, before rounding the arithmetic

Let z be n independent fair bits. A relation observation e=(i,j,y) has
likelihood proportional to `1+s I_e(z)`, where `I_e=1[z_i XOR z_j=y]` and
the independent label-noise rate is `1/(s+2)`. The usual causal/exogenous
query assumption from [the v6 model](CAUSAL_RELATION_PROPOSAL.md) applies.
Fix the last at most H observations E. Expand their positive product:

`Z = E_z PROD_(e in E) (1+s I_e)
   = SUM_(A subset E) s^|A| E_z PROD_(e in A) I_e`.

If the labelled XOR equations of A are inconsistent, the last expectation
is zero. Otherwise their binary incidence matrix has rank r(A), giving
exactly `2^(n-r(A))` solutions and expectation `2^-r(A)`. Loops and repeated
edges require no exceptions to this argument: a label1 loop is inconsistent,
and contradictory parallel constraints are also inconsistent. Rank is the
number of involved vertices minus their number of connected components.

For the current query q and possible readout y, define

`C_y = SUM_(A subset E) s^(|A|+1) 2^-r(A union {q:y})
                       1[constraints A union {q:y} are consistent]`.

Then `M_y=Z+C_y` and `M_0+M_1=(s+2)Z`. Their normalized masses are exactly
the known-noise window posterior. These masses average over the prior;
the earlier enumeration of K=2^(n-1) global-flip representatives sums it,
and has masses K times as large. This equality concerns initialized forward
values, not their complete learners or a right to erase old observations.

The unsigned positive subset expansion is classical, rather than a new FP
claim: see Sokal's [Fortuin--Kasteleyn representation, Theorem 2.3](https://arxiv.org/pdf/math/0503607).
The labelled case here follows directly by counting solutions of its binary
linear system. The FP-specific obligation is to realize the identity using
the actual declared positive syntax, coefficients and causal interface.

## 2. A native realization from Gamma=(1,8)

Register two current one-hot token roles, and the two token roles plus two
target atoms at each lag1 through H. Missing old frames are all zero; all
present frames are categorical. Sources read only their declared ordinary
input or lagged target, never a supplied rank, parity, weight or posterior.
Both the contracted and full-world control receive this identical interface,
base=(1,1), Gamma=(1,8), unit1, zero rate and no commit quantization. They
have no native delayed coordinate. This is a different source interface
from v6's lag1 plus recurrent state, so v6's decision class is not borrowed.

For k selected edges, their 2k endpoint occurrences have some equality
partition pi with at most n blocks. On one-hot token vectors, native features

`Eq(a,b) = SUM_i x_(a,i) x_(b,i)` and
`Diff(a,b) = SUM_(i != j) x_(a,i) x_(b,j)`

test equality and inequality, respectively. Multiply Eq from each block's
representative to its other members, and Diff between distinct block
representatives. This is the indicator of pi. Every endpoint occurrence is
tested, including the case of one block. Therefore a missing selected frame
makes the indicator zero; no assumption about its unknown target is made.
Exactly one partition indicator is active when all selected frames exist.

For each pi, compute its incidence rank and consistent binary label vectors
at compile time. The SUM of the corresponding products of lagged target
atoms is a 0/1 consistency indicator on the categorical domain. For query
terms the extra query label is the fixed head index, not the current target.

At s=8 every required nonzero coefficient is an integer:

`8^k / 2^r = 8^(k-r) 4^r`, with `0 <= r <= k`.

The emitter creates one from a current one-hot SUM using actual slot0;
two and four use repeated unit incidences, while eight uses actual slot1.
PRODUCTs form the displayed coefficient. There is no numerical literal
coefficient or division hidden in a SUM, and no added half-valued initializer.
The empty subset contributes precisely the registered base one. All other
common and query terms form positive excess heads. Node sharing reuses only
identical emitted syntax; it does not identify complete learner objects.

The companion enumerator uses every z_0=0 representative and the same
expanded history sources. Its positive recursion `u <- u+8 I(1+u)` runs
over the available lags; the base-one head adds the paid K-1 offset. No
posterior approximation, sign freezing or learning-rate handicap is imposed.
The separate historical base-K model has another contract and is not
silently treated as a base-one comparator.

## 3. What becomes smaller, and what does not

Because every original likelihood ratio lies in [1,9], `1 <= Z <= 9^H`.
Thus the contracted normalizer obeys `T <= 10*9^H`, independently of n.
Every node obeys the same envelope: equality/label indicators are 0/1,
coefficient construction is bounded by `8^(H+1) <= 10*9^H`, common excess
is at most `9^H-1`, and a final excess at most `9^(H+1)-1`.
The coefficient comparison holds for all H>=0 because
`8^(H+1)/(10*9^H)=(4/5)(8/9)^H <= 1`.
The full-world graph's natural normalizer bound instead has an extra K.
Section7 gives a stronger centered full-world graph that removes this factor
when K<=8. It prevents interpreting contraction's range saving against the
first literal enumeration as an inherent advantage over full-world models.

For each fixed H the contracted graph has size polynomial in n, rather
than requiring K latent representatives. More explicitly, let B_m be the
m-th Bell number. Pair-feature sharing costs `O(n^2(H+1)^2)` incidences.
The remaining cost is bounded by a function of H alone, for example

`O(H^3 + H*3^H + SUM_(d=0)^H binom(H,d)
                     (B_(2d)+2 B_(2d+2))*(H^2+2^d))`.

The expression counts coefficient products, shared target monomials,
partition indicators and consistency SUM incidences, respectively. Restricting
partitions to at most n blocks only decreases it. This is an upper bound
for one explicit emission, not a minimal circuit law or efficient long-window
algorithm. The Bell-number cost is substantial even at H3.

The complete categorical source domain also grows:

`D(n,H) = n^2 SUM_(j=0)^H (2n^2)^j`.

It contains all histories through length H, with only older-prefix zero
padding, and every current ordered query. This domain is identical for the
two controls. Runtime's current exact range implementation materializes one
bound per row, retaining all node intervals. Therefore n-independent mass
range and a fixed-H polynomial native graph do not imply affordable complete
execution. Giving only the observed tape as the domain would change the
legal information/continuation contract and is not used.

Literal costs of the committed generator (all nodes, even unused ones, paid):

| n,H | contracted nodes/edges | full-world nodes/edges | domain rows |
|---|---:|---:|---:|
| 2,2 | 398 / 833 | 76 / 128 | 292 |
| 2,3 | 1771 / 3899 | 102 / 172 | 2340 |
| 3,2 | 1188 / 2662 | 141 / 323 | 3087 |
| 3,3 | 11399 / 25537 | 192 / 437 | 55575 |
| 8,2 | 2787 / 6786 | 2044 / 28046 | 1056832 |
| 8,3 | 49733 / 109813 | 2766 / 37390 | 135274560 |

At small n the contraction is substantially more expensive. At n8,H2 it
saves incidences but uses more nodes. No overall hardware/resource dominance
or strong-model performance improvement follows from these counts.

## 4. A scoped half-exact forward invariant

For H<=3, every nonconstant excess coefficient is divisible by four:
`3k-r >= 2k >= 2`. Indicator and label-polynomial values are zero or one.
Coefficients are powers of two at most4096. All remaining weighted terms,
partial excess sums and final excesses are nonnegative multiples of four,
bounded by `9^4-1=6560`. Such integers are exactly representable in binary16
(spacing is at most four below8192). Constants one and two are also exact.

In the registered AMP primitive semantics, SUM weighted terms are stored
in half, accumulated in single, then stored in half; PRODUCTs store in half.
Every operation just described is therefore exact. Readout base additions
and normalization sums are single integers below7291, also exact. Final
single division can still round. This proves exact native values and masses
for every categorical input in this H<=3 model, not exact gradients, arbitrary
parameter updates, arbitrary H, or a complete bridge/install theorem.

For n2,H3, three observed `(0,0,0)` labels followed by query `(0,0)` give
contracted masses `(6561,729)`, stored exactly. The full-world graph has
reference masses `(13122,1458)` but rounded masses `(13121,1458)`: its first
excess13121 rounds to13120, after which base one is added. The prediction
identity does not commute with this change of positive representation.

## 5. Adversarial boundaries and minimal exact evidence

After one observed `(0,1,0)` at n2,H2, both initialized graphs predict41/50
for label0 on query `(0,1)`. Their target0 CE gradients at Gamma=(1,8) are
`(-96/205,-18/1025)` and `(-256/1025,-4/205)`, respectively. Those gradients,
complete graphs, resources and provenance remain distinct even though zero
rate leaves masters unchanged. No learner/state/evidence transport is granted.

For history `[(0,1,0),(0,1,1)]`, soften only the newest first-token vector to
`(1/2,1/2)`, then query `(0,1)`. Contracted p0 is59/98, enumerated p0 is43/70.
The equality-partition proof needs its categorical source contract; it cannot
be promoted to arbitrary bounded or simplex inputs.

`python -B experiments/joint_uncertainty/constraint_contraction.py --algebra`
checks18,540 signed rank cases by independent enumeration of satisfying bits;
5,944 native forecasts by an independent integer interpreter and full latent
prior average;58 formal Fraction and58 exact rounded-interpreter forecasts.
It covers all categorical histories for n2,H2/H3 and n3,H2, plus every label
assignment on n3,H3 triangle/repeated-edge/diagonal diagnostics. The latter
225 forecasts are not all55,575 domain rows. All57 distinct encountered node
values are exact half values; maximum node6560 and normalizer7290 are attained.
`--boundaries` checks the two counterexamples; `--counts` reports literal costs.
These audits do not load Torch and confer no Runtime authority.

## 6. Completed owned comparison, with its actual costs

`experiments/joint_uncertainty/constraint_cuda.py` registers both n2,H3
models as separate initial owned CUDA runs, with independent binary64 replay.
Each has the identical full2340-row domain,22 sources, no delayed coordinate,
base1, Gamma1/8, rate0, unit1, no grid, and the same fixed nine-event tape:
four `(0,0,0)`, then `(0,1,0),(0,1,0),(0,1,1),(0,1,1),(0,1,0)`.
It includes the rounding witness, adaptation to cross labels and window
eviction. It is synthetic correctness evidence, not a statistical model score.

Both use16GiB host jobs with900-second limits,2GiB packed payload,10^12 work
per role, cap14580 for activation/normalizer,16MiB native arena/32MiB allocator,
16384 phase output cells,2MiB full phase evidence, state/native/normalizer
tolerance2 and probability tolerance1/10000. Binary64 tolerances are1/100.
The whole-board resource contract supplies its usual capacity upper; no
exclusive GPU access or timing comparison is claimed. The contracted graph
requires10785 maximum output cells versus604. Its smaller theorem range is
recorded separately, not used to grant it a different resource envelope.

Independent rounded tape preflight finds mass errors0/1 and raw probability
errors1/41943040 versus583/26214400. All gradients and ordinary commits still
execute. The complete Runtime must independently admit its full range/evidence
and actual mixed-precision trajectory. Any failure remains in its original
fixed-budget job. No discovery, class certificate, fresh evidence or install
is requested by this initially registered control. Do not borrow v6's separate
construction/installation authority or declare this a complete compiler path.

Both source-bound jobs complete at `65c6472d42649a0a6ac78fa418737e1819ac1458`,
seal all nine observations, and each independently replay28 CUDA and28
binary64 phases. The [compact journal](../../evidence/minimal/FP_CONSTRAINT_CONTRACTION_CUDA_AUDIT.json)
retains both completed jobs and device/build identities, without whole-phase
or dataset dumps. Neither job times out or acquires a class/install certificate.

| Measured coordinate | contracted | uncentered enumeration |
|---|---:|---:|
| completed job commitment peak (bytes) | 5319102464 | 2554642432 |
| packed payload peak (bytes) | 570850422 | 90834766 |
| used native arena extent (bytes) | 1003144 | 65704 |
| maximum complete phase frame (bytes) | 792426 | 46688 |
| maximum output cells | 10785 | 604 |
| maximum CUDA native error | 0 | 1 |
| maximum CUDA normalizer error | 0 | 2 |
| maximum CUDA raw probability error | 1/41943040 | 583/26214400 |
| maximum CUDA division error | 1/41943040 | 1/41943040 |

CUDA gradient/state errors are39917/69646417920 and117225893/92861890560;
zero native error never meant an exact backward trajectory. Binary64 native
and normalizer errors are zero for both. The retained reference p0 sequence
is `(.9,.9,.9,.9,.5,41/50,73/82,41/50,9/50)`: causal labels change subsequent
predictions and eviction is actually executed. The declared common16MiB arena,
32MiB allocator and whole-board capacity are charged even where used extent
is smaller. These are correctness/resource observations from separate jobs,
not throughput or population performance claims.

## 7. Attack the comparator: centered integer excesses

The literal uncentered enumerator is not the strongest available small-n
baseline. For K=2^(n-1)<=8, put `v_z=(w_z-1)/K`, starting from zero. Since
`w_z>=1`, this analytical change of coordinates has a positive update:

`v_z' = v_z + I_z*(8 v_z + 8/K)`.

Now `Z=1+SUM_z v_z` and

`M_y = 1+SUM_z v_z + SUM_z G_(z,y)*(8 v_z+8/K)`.

Here c=8/K is an integer (4,2 or1), formed from paid unit incidences; the
coefficient8 of v uses actual slot1. No runtime subtraction or division is
performed. This produces the same averaged masses as the partition expansion,
using the original number of world chains. In fact the affine forward identity
still holds for soft previous indicators, provided the current unit source
sums to one. It does not grant complete learner or evidence transport.

For H<=3, all v values are integers at most364; scaled terms are
`(8/K)*9^j`, at most2916 for K2 and at most1458 for K>=4, hence half-exact.
The common excess is an integer at most728. Query and final excess SUM
results are multiples of four by the signed-rank identity above, at most6560;
their partial accumulation is single. Thus the centered graph also has
half-exact native forward values and averaged masses on the categorical
domain. Final division and all gradients retain their own numerical obligations.

Literal n2,H3 counts are102 nodes/174 edges, compared with102/172 uncentered
and1771/3899 contracted. n3/H3 has192/435 and n4/H3 has334/1043. For the
actual n2 registered scope, centering therefore supplies the same exact
forward arithmetic at far smaller graph cost than partition contraction.
This is a strict correction to any inference that the latter is the useful
small-n implementation; its general fixed-H n-dependence remains a separate
representation theorem.

For K>8, the same individual v coordinate cannot be implemented by a zero-rate
native program with integer Gamma1/8, Boolean sources and zero-initialized
native delays: induction gives integer node/delay values, but its first
matched observation requires v=8/K, a noninteger. This only rules out that
particular scalar coordinate realization under that initializer. It does not
rule out the contracted integer masses, another code, a different registered
initializer, or a more effective positive program.

`python -B experiments/joint_uncertainty/centered_contraction.py --algebra`
checks2,965 exact native forecasts: the entire n2,H3 domain and225/400 n3/n4
diagnostic forecasts. It also checks53 formal and53 exact rounded forecasts;
all56 encountered integer values are half-exact. An informative witness avoids
relying on a cancelable diagonal likelihood factor: three `(0,1,0)` labels,
then query `(0,1)`, give both centered and contracted masses `(3281,369)`
exactly. The uncentered graph has `(6562,738)` but stores `(6561,738)`.
These are interpreter results, not an actual target claim for centering.
The two completed jobs from section6 retain their original registration.
`experiments/joint_uncertainty/centered_cuda.py` registers one new centered
job with the same tape, full source domain, caps, tolerances and independent
audits. It checks equality of every registration field except the model/counts,
links the completed two-job journal, and does not repeat either earlier job.
The new job completes at `716d27989e35754fc5e5328c95bb1ba72be2f414`, seals
all nine observations and independently checks28 CUDA plus28 binary64 phases.
Its [compact journal](../../evidence/minimal/FP_CENTERED_CONTRACTION_CUDA_AUDIT.json)
links both original jobs without repeating them. Actual native and normalizer
errors are zero; raw probability and division errors are1/41943040. Gradient/
state error is6383/13589544960. Packed peak is90,865,346 bytes, completed host
job peak2,553,532,416, native extent66,712, maximum complete phase frame47,225
and maximum output cells612. No timeout, class certificate or installation
is introduced. The same resource grants include the whole16MiB arena even
when fewer bytes are consumed within it.

The matched conclusion is now physical as well as algebraic: centered
enumeration keeps the contracted model's exact masses with102 instead of1771
nodes and about91MB instead of571MB of charged packed payload. The original
enumerator has almost the same small graph/payload but retains its observed
mass/normalizer errors. The general partition contraction still supplies a
fixed-H polynomial-in-n existence bound; it is not a small-n resource winner,
a minimum circuit theorem, or affordable full-history inference.

`python -B experiments/joint_uncertainty/analyze_contraction.py` independently
checks all27 retained forecasts using a fresh four-world scalar sum, verifies
source dependencies and matched registrations, binds completed process IDs,
checks resource caps, and recomputes stored-mass/raw-division error maxima.
It totals84 independently audited CUDA and84 binary64 phases across the three
sealed jobs. It executes no new GPU workload and cannot reconstruct omitted
raw hardware phases from the compact record. The per-phase audit authority
remains the executed auditors at each recorded source.
