# Owned positive mixture persistence

Status: **IMPLEMENTED; EXACT/PAIRED FAILURES AND BOUNDED CPU/CUDA INSTALL PASS**.
This is scoped endpoint evidence, not a complete release or a model
advantage. This extension does not change the running8ccacc0 experiment,
Foundation R4, ERC-1 or any search decision class.

## 1. Declaration and sufficient state

The [positive-state proof](PREDICTABLE_MIXTURE_STATE.md) supplies the scalar
construction. `ArcsinePersistenceRule` declares the same identity horizon,
epoch length, alpha, common bound B, lower-log precision and score path as
ordinary persistence, together with coefficient fractional bits q. It has
neither an unused fixed bet nor a scalar wealth grid. These are different
numerical procedures: flooring scalar wealth after each step would invalidate
the stated curve/readout identity and the proof against previous owned wealth.
The classical arcsine measure is fixed by this declaration, not selected by a
context, target, model tape or caller-provided coefficient.

After t completed epochs, the existing owned `PersistenceIdentity` retains
the tuple n=(n_0,...,n_t), its exact wealth L, and all its previous complete
lineage, learner, range, stream and alpha coordinates. The curve is

`Q_t(b) = sum_k (n_k/2^q) b^k (1-b)^(t-k)`.

Initialization sets n_0=2^q. At a closed epoch, let x be the registered mean
lower gain divided by B. The guarded update is

`n'_0=2^q; n'_k=n_k+floor((1+x)n_(k-1))`,

with missing cells zero. The returned wealth is the exact rational readout
`L'=sum_k n'_k A_(t+1,k)/2^(q+2(t+1))`. Integer weights A are streamed by
exact divisions; no sampled coefficient, integration grid or persistent
weight cache is introduced. Before an update the kernel independently
recomputes L from the current tuple and rejects a mismatch, invalid shape,
negative/noninteger cells, an exhausted horizon or an already crossed state.
Pure arithmetic results carry no Runtime authority.

## 2. Same conditional-null argument, new arithmetic

For every successfully retained pre-epoch state, Q>=0 and its constant
Bernstein coefficient is positive. Thus L>0 and
`beta=integral b Q dnu / L` lies strictly between zero and one. It depends
only on the previous retained curve and is measurable before the epoch's
contexts. Downward coefficient rounding gives, pointwise,

`Q' <= Q*(1+b*x)`, hence `L' <= L*(1+beta*x)`.

Under the declared bounded stopped-epoch conditional mean-null, conditional
expectation is at most L. Operational failure kills the testing process;
it cannot grant a crossing or start a replacement with old wealth. The
ledger still preserves the previous statistic and its spent alpha. The
usual stopped nonnegative-supermartingale threshold argument therefore
applies to owned crossings. This is Foundation XIV.20's predictable fraction,
not a new semantic architecture action or a stronger producer assumption.

The external law remains an assumption about this actual stopped statistic.
Changing arithmetic can change its operational stopping. In particular an
uninterrupted, differently stopped or differently grouped H>1 epoch-null
does not automatically transfer. Reference, binary64 and CUDA identities
still have separate scores, declarations and alpha allocations. A reference
curve never substitutes for finite-path evidence or an AMP bridge.

## 3. Ownership, work and failure publication

Alpha is spent before fallible seed materialization. The seed fee is charged
before arithmetic; the existing identity save owns the curve together with
the active range/lineage state. Each completed epoch prepays
`1024*(t+3)` primitive work before either streamed readout or coefficient
update. Each readout has two linear loops; the update has one linear loop.
Counting input scans, guarded integer operations, fixed rational operations
and threshold checks fits that charge. It is a conservative primitive-work
declaration, not a bit-time, instruction count or wall-clock bound.

All coefficient additions/products are preflighted against the registered
integer-bit limit, dyadic shifts check their extent before allocation, and
normalization/wealth use the existing guarded rational arithmetic. A
conservative preflight can refuse an operation whose reduced answer would
fit. That is `UNRESOLVED`, not a reason to change the evidence semantics.

The new curve and wealth are published in the same existing packed identity
save. A fresh score event can already be retained when the save fails; it
then records a numerical threshold without an owned crossing. The previous
curve remains historical, the identity stops, alpha cannot be refunded, and
installation cannot borrow the event's number. Unexpected backend exceptions
also halt the ordinary prefix and preserve the observed target. After a
successful crossing, the statistic stops while the existing complete learner
lineages continue to be checked and tracked.

The reference payload model charges retained packed objects, including every
curve cell, and temporary overlapping saves through its existing allocator.
It is not a claim to measure every transient CPython object. The scalar
operand/payload bounds in the earlier proof do not replace a physical host
fence. Source-bound development workers apply the existing Windows job caps
before resumption. Adding the optional tuple field also changes packed sizes
for constant-rule identities; passing their regressions does not imply byte
identity, unchanged feasibility at every cap, or a renewed project release.

## 4. Evidence and limits

`python -B scripts/audit_mixture_persistence.py --write` records the
[minimal reference audit](../../evidence/minimal/FP_MIXTURE_PERSISTENCE_AUDIT.json):

* 243 complete five-score words and1,215 guarded updates, independently read
  by signed monomial integration; nine malformed/numerical refusals. The
  instrumented maximum is300 guarded integer calls per update in this audit,
  below the prepaid linear fee.
* An actual owned crossing at cursor7, with ordinary lineages tracked through
  cursor12; supplied declarations/booleans grant no installation. A changing
  learner independently checks12 scores, four three-event evidence epochs
  and six ordinary optimizer commits.
* All32 five-label fair branches execute through Runtime:160 scores and31
  exact conditional wealth inequalities. This finite audit checks the
  declared fixture law; it does not infer a law for a dataset.
* Failed crossing retention preserves the numerical event and previous
  owned curve, with no authority or revival. Immutable work caps25,823 and
  6,537 refuse epoch arithmetic and seed arithmetic before entry. A real
  128-bit limit with q124 admits the identity but refuses the first product,
  preserving the old curve, target, spent alpha and ordinary continuation.
  Injected numerical and unexpected backend failures also stop correctly.
* Three actual paired binary64 failure cases independently replay42 curve
  scores. A native mass increment2^-54 gives a reference crossing at6 while
  stored finite gains stay zero and finite wealth stays one. Refusing only
  the finite crossing save cannot borrow the reference crossing. If both
  successors cross at7 before ordinary publication fails, both remain
  auditable history but the paired result is `UNRESOLVED`.

Full existing reference, paired CPU binary64 and scalar-kernel persistence
audits pass on this extension; the [compact regression record](../../evidence/minimal/FP_MIXTURE_PERSISTENCE_REGRESSION.json)
retains their relevant counts and failures. Their reference/finite nontransfer, freshness,
ordinary-publication failure, integer/work/byte failure and no-refund checks
remain meaningful. They do not validate a new rule's actual installation.

## 5. Source-bound complete CPU path

`python -B scripts/audit_mixture_persistence.py --profile-cpu --write` ran
from committed clean4daf126. The512MiB job was attached before resumption,
exited normally, and peaked at39,084,032 bytes. PID25540 and its creation
time bind the runtime host record to the completed job. The minimal audit
retains the job, execution source and separate path records; subsequent
audit writes preserve all bounded attempts, including failures.

The fixed n2 native likelihood fixture admits after its two-event profile,
registers B13/8, alpha1/4 per path, horizon40 and q72. It independently checks
44 posterior forecasts,280 binary64 phases and16 fresh scores. Both owned
curves cross after eight fresh events; full installation occurs at cursor10,
and the ordinary stream seals at46 retained observations. Each stopped curve
has nine cells and53,248 paid update work. Every curve readout is independently
reconstructed; its score, complete trajectory, phase replay and transport
still pass the original install gates. The search class remains `UNRESOLVED`.

The retained constant-fraction3/4 fixture at the same B installed at8. The
new result establishes actual CPU reachability, not an earlier-crossing
guarantee or population/model advantage. CPU evidence does not substitute
for target AMP; that path is tested separately below.

## 6. Actual RTX 3090 bridge and installation

`python -B scripts/audit_mixture_persistence.py --profile-cuda --write` runs
from committed clean3490d76. The4GiB job is attached before resumption,
exits normally and peaks at2,392,080,384 host bytes. PID17356 and its
creation time bind the runtime observation to the completed job. The
previous CPU attempt and its distinct execution source stay retained.

The n2 fixture checks44 native posterior forecasts,280 actual CUDA phases,
280 independently replayed binary64 phases and16 fresh score/curve updates.
Both paths cross at10 after eight fresh events; complete transport/install
passes and the46-observation CUDA stream seals. Each curve retains nine
cells and53,248 paid update work. Reference and CUDA terminal wealth differ
and are independently reconstructed from their own scores. The class remains
`UNRESOLVED`; this is one selected native proposal, not a complete search.

This short development job overlaps registered model worker6920, which is
observed live before and after it. External observations bracket the audit
between17:24:56 and17:25:33 UTC on2026-09-20. The overlap is retained explicitly;
neither run is presented as an exclusive-device timing measurement. The
model's source stays8ccacc0 and its rule, caps, case order and journal are
unchanged. The board-capacity record is also not measured per-process VRAM.

This closes the new rule's exercised CUDA profile/bridge/install path.
The reference/paired fault audits above remain scoped to their actual
executions; this single CUDA success is not every possible failure test.
The [retrospective comparison](../../experiments/joint_uncertainty/MIXTURE_DEPLOYMENT_ANALYSIS.md)
still limits its model value: first-passage reversals and the strong fine-grid
fixed control remain, regardless of successful implementation.

This result closes ownership and CPU/CUDA install reachability on the exercised
paths. It does not prove first-passage dominance, model utility, full release
or any new `CERTIFIED_COMPLETE` class. The fixed n8 matrix is unchanged.
