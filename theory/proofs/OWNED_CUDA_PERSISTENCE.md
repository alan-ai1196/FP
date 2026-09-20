# Current CUDA range and fresh same-path persistence

**Status, 2026-09-13: proved for the registered rounded predictor and stopped
mean null; implemented and audited through actual RTX 3090 Runtime events.**
This closes the current-domain and same-path evidence components of the AMP
bridge. It does not close target installation, total-device resources or
model-science release. Foundation R4, XVII.31 and ERC-1 remain frozen.

Normative sources are [Foundation XIV--XVI](../../FP_THEORY.md),
[ERC-1](../../EXPERIMENT_RESOURCE_CONTRACT.md), the
[owned prefix](OWNED_CUDA_PREFIX.md) and the
[existing stopped persistence proof](OWNED_REFERENCE_PERSISTENCE.md).
The [CPU range/persistence proof](PAIRED_CPU_PERSISTENCE.md) supplies the
same filtration and wealth argument. No new semantic action is introduced.

Implementation: [cuda_range.py](../../src/reference_compiler/fp_reference/cuda_range.py),
[cuda_persistence.py](../../src/reference_compiler/fp_reference/cuda_persistence.py)
and [Runtime](../../src/reference_compiler/fp_reference/runtime.py).
Run `python -B scripts/audit_cuda_persistence.py --write`; retain only
[the minimal report](../../evidence/minimal/FP_CUDA_PERSISTENCE_AUDIT.json).

## 1. The missing premise is exact forecast conformance

Closeness of an observed device forecast to reference does not prove a
whole-domain physical range law. Neither do finite primitive/kernel tests.
There is a concrete gap: changing a stored baseline mass by one single ULP
passes the existing reference tolerance relation, although it differs from
the registered rounded computation. The new audit performs both checks on
that same perturbed actual tensor; exact conformance refuses it before any
target. This is fault injection, not a claim that the unmodified kernel
spontaneously produces this error.

The implementation now separates two obligations:

1. Prove range for the **declared deterministic rounded mathematical
   predictor**, using the actual current master encodings and the full
   registered source/delayed domain.
2. Before accepting each actual forecast, check every stored native value,
   half weight, head, mass, normalizer, division output and entire shifted
   queue against that same mathematical predictor, including zero signs.

The checker runs independently on exact rational arithmetic with guarded
integer sizes. It never supplies a GPU prediction or successor. A mismatch,
nonfinite result or unaffordable check is UNRESOLVED, with actual outputs
retained and no target-time evidence. The existing reference relation is
still separately required. Thus the range theorem does not assume that
finite tests establish every possible future kernel invocation.

This also supplies the bounded mathematical score on a failing attempt
required by the existing stopped-null proof. At each pre-context history,
the current complete device learner is predictable. Its mathematical
rounded predictor is defined on the entire admitted domain even if the
next actual computation or relation check fails. Failure yields no usable
crossing or continuation of that evidence identity. Defining the null
only over successful computations, or skipping their unfavorable failures,
would instead select outcomes and is forbidden.

## 2. A monotone bound for the actual mixed schedule

Write H and S for nearest/ties-even rounding to binary16 and binary32 with
gradual subnormals. Fix every current nonnegative single master encoding
theta, the ordered native graph and immutable semantic rules. The schedule
is the one in [the continuous learner](CONTINUOUS_CUDA_LEARNERS.md):

- Every source x enters as H(S(x)); every master slot enters as H(theta),
  including unused slots. Collapsing the first composition to H(x) is wrong.
- A half PRODUCT or weighted edge uses H(S(a b)). Finite half operands have
  products with at most 22 significant bits and magnitudes from 2^-48 to
  below 2^32, so this inner product is exactly representable in single.
  The checker nevertheless retains both explicit rounding steps.
- Each SUM accumulates widened half edge products in its declared order
  with S addition, then stores H(accumulator).
- Base, head widening, mass addition, ordered normalizer and resident-tensor
  division use single precision. There is no host-scalar reciprocal path,
  fused addcmul, reassociation or autocast inference in this declaration.

The source implementation's half opmath choice is visible in the pinned
[PyTorch multiplication kernel](https://github.com/pytorch/pytorch/blob/7661cd9c6b841b62b7f411aa52ec51f05457263b/aten/src/ATen/native/cuda/BinaryMulKernel.cu).
It motivates the registered schedule; source inspection is not substituted
for the per-forecast exact conformance check.

Rounding on an ordered representable grid is nondecreasing. Addition and
multiplication of nonnegative values preserve that order. Therefore, by
induction over the DAG, evaluating this mixed schedule at source upper
coordinates bounds every stored node and mass for the entire source box.
For a complete finite source domain, do the same once per registered row.
Sharing, repeated edges, squares and PRODUCT-of-SUM parents require no
separate architecture case.

For each delayed cap u and every representable half queue value z <= u,

\[
z=H(S(z))\le H(S(u)).
\]

This holds even when rounding u goes downward. Use H(S(u)) at each delayed
read, verify every body upper <= u, and verify **all current queue entries**
<= u. Shifting the retained tail and appending the bounded body preserves
the invariant. Looking only at the current head is insufficient.

Let beta_y=S(b_y)>0. Monotone mass addition implies m_y >= beta_y. The proof
keeps both the exact sum of decoded stored masses and the rounded sum:

\[
S_m=\sum_y m_y\le U_m=\sum_y m_y^{upper}\le R,\qquad
t_f\le U_t=\mathop{\mathrm{ordered}\,S\mathrm{sum}}_y m_y^{upper}\le R.
\]

Every activation upper must also meet its registered activation cap. The
two normalizer tests are independent: `(1, 2^-24)` has exact sum above one
but rounded sum one, while `(1, 3*2^-24)` rounds its sum above the exact sum.
Neither representation can replace the other in a range proof.

The proper physical probability is p_y^m=m_y/S_m. The separately stored
division output obeys

\[
0<S(\beta_y/U_t)\le p_{out,y}=S(m_y/t_f)\le1.
\]

The strict lower inequality is checked. A positive real base that rounds
to zero, or positive masses whose division can round to zero, is unresolved.
The upper inequality follows because each positive ordered partial sum is
at least each of its representable addends. This proves definition/range,
not uniform numerical closeness to reference or future optimizer success.
Loose boxes and arithmetic/resource limits remain UNRESOLVED.

## 3. Owned scope, updates and payment

The manifest fixes `forward_id` and the v2 phase work model before execution.
Each prediction prepays the exact check in addition to the existing GPU
output, relation and evidence allowances. Its scalar round count is

\[
Q=M+2A+1+2P+4E+N_{SUM}+5K,
\]

where M is the actual slot count, A the source count, E the SUM-edge count,
P the PRODUCT count and K the head count. A range enclosure adds two rounds
per delayed-state specification and K lower-bound divisions. Runtime charges
256 per scalar round plus a fixed coordinate/decode allowance; integer
sizes have their separate cap. These are abstract reference-machine charges,
not GPU elapsed time, bit complexity or total host memory measurements.

`CudaPhase.forward_operations` records successful forecast checking in the
already prepaid packed phase frame. Whole-domain calculations use compiler
work and are retained in the owned persistence identity before ACTIVE status.
No public port accepts theta, range objects, forecasts or a checked flag.

A CUDA-bearing root extends persistence identities with its initial/current
base and candidate **owned phase IDs**. These refer to the same retained
complete masters, gradient accumulators, delayed queues and clocks, without
reconstructing a learner. Non-CUDA identity encodings stay unchanged.
The root binds each range to that lineage's actual theta, Program and full
immutable domain. Changed master bits require a new range proof before the
identity continues. Unchanged theta reuses its existing bound while checking
the entire actual successor queue; it does not identify complete learners.

A real update illustrates the distinction: exact theta becomes 3/10, within
its delayed-body cap; single master followed by half storage becomes
1229/4096 > 3/10. The current queue remains zero, so the ordinary event can
publish. The future CUDA range proof fails and that evidence identity stops
before another context. Reference evidence can remain active; it cannot fill
the missing physical claim.

## 4. Fresh statistics and precise authority

The immutable score path is `cuda-half-single-stored-mass`, with null ID
`bounded-pre-context-stopped-cuda-mass-epoch-mean-v1`. For both lineages it
uses the proper probabilities from actual pre-target stored masses, never
rounded division outputs, reference probabilities or post-update values.
The unique ordinary target is scored only for identities admitted before
its context. Profiles, old observations and another identity's wealth do
not become fresh evidence. An external branch-invariant stochastic-law
declaration is required; the audit tapes do not prove that law.

Put B0=sum_y beta_y. The same class-wide bound as on the CPU leg gives

\[
\beta_y/R\le p_y^m\le(R-B0+\beta_y)/R,\qquad
K=\max_y (R-B0+\beta_y)/\beta_y.
\]

Consequently both candidate/base ratios lie in [1/K,K], and their log gain
is bounded by log K. Runtime proves that its registered bound covers this
quantity before evidence starts. Guarded log enclosures and the existing
downward-rounded linear wealth update preserve the stopped mean-null
supermartingale argument. Reference and CUDA pay separate nonrefundable
alpha allocations; dependence from using the same fresh events is allowed.

`admit_cuda_persistence`, `cuda_persistence_result`,
`cancel_cuda_persistence` and `paired_cuda_persistence_result` access only
owned identities. Pairing requires matching starting complete trajectories,
lineages and epoch schedules. `PAIRED_CUDA_CROSSED` means both current
same-path statistics crossed. It is neither `CERTIFIED_COMPLETE` nor
installation authority. Failed first-crossing retention, later learner
failure, retirement and cancellation leave spent alpha and history, with
no current claim or wealth recycling. CPU install continues to refuse a
CUDA root. The separate [resident installation](OWNED_CUDA_INSTALLATION.md)
now executes its own full transition checks from these owned identities;
complete device resource/run/release closure remains open.

The later [current mass-box solver](CURRENT_MASS_PERSISTENCE_BOUND.md) adds
an owned fallback when the class-cap gain bound is too loose. It uses the
already retained whole-domain mathematical mass bounds, not closeness of a
successful query. Its current-state proof is refreshed while ACTIVE; failure
stops the identity before next ingress. The above stopped-null, exact actual
forecast conformance and installation requirements continue to apply.

## 5. Minimal executed evidence

The audit checks 16 mixed PRODUCT/SUM boxes against 400 independent rounded
predictions and 125 complete recurrent queue combinations. Adversaries cover
unused-slot half overflow, source/product rounding overflow, queue tails,
base/division underflow, both normalizers and two-stage input rounding.
For source `33570817/67108864`, actual H(S(x)) is 1/2 while direct H(x) is
1025/2048; an owned range and actual forecast retain the former.

All 32 five-label fair branches execute on CUDA: 160 ordinary events,
832 independently replayed device phases and 62 two-path conditional wealth
inequalities. Each path's first-crossing probability is 1/32 under this
fixture, below its allocated 1/3. A separate 12-event trained path checks
24 scores/logs/wealth updates, six range recomputations and 62 complete CUDA
phases beside 62 CPU binary64 phases. The old 1,109-phase owned CUDA prefix
audit is rerun with exact forecast checks.

The nontransfer witness uses a fixed coefficient 2^-25 and zero-rate SGD
without a floor grid on both paths. Reference crosses at event five, while
half forwarding erases its excess and CUDA gain remains exactly zero with
wealth one. Other actual/injected controls cover the one-ULP conformance
gap, domain failure at admission and after learning, separate start times,
spent-alpha exhaustion, crossing-state retention failure and device failure
after both crossings. None of these tests claims experimental model utility
or a complete target release.
