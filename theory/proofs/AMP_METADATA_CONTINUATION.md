# AMP metadata must survive rejection and later helper calls

Status: **two exact passive CPU counterexamples; two actual CUDA probes
registered, pending**. Production remains7fe0471. The repaired reference
prediction component remains valid in its stated fault class. The broader
indexed helper boundary is HOLD.

The [continuation-stability law](CONTINUATION_STABLE_DELEGATION.md) requires
both private input authority and private accepted output records. Checking
a plan before and after the current execution does not establish its
stability under a later call to the same producer.

## 1. A rejected physical call can change its predecessor

After the actual n3 event(1,2,0), the native and physical counts are(0,0,1).
For query(1,2), the native probability is41/50. `ResidentState.raw()` creates
a raw wrapper sharing the resident CountState, which also occurs in older
phase metadata. The physical executor receives that raw wrapper.

Change only the supplied count to(0,0,-1) and then run the honest physical
schedule. The full plan check and conditional exact RNE interpreter agree
with this altered predecessor. The independent native bridge refuses: the
reference remains correct and differs from the altered raw before record.
Nevertheless the physical predecessor has already changed. A correct
refusal cannot undo that write or restore an earlier snapshot's metadata.

The passive CPU witness confirms the distinction using the existing exact
RNE interpreter, with separate reference and physical states. It produces
probability12079595/67108864 instead of the required41/50, passes the
conditional plan/operation checks and fails the independent native bridge.
It is not a claim of an actual owned CUDA execution; that probe is registered
below.

## 2. A later planner can rewrite an earlier checked phase

The AMP planner's returned `IndexedAmpPlan` is checked, executed, checked
again and then stored directly as `IndexedCudaPhase.execution_plan`. The
planner can retain the same object. On a later call it can change its own
old returned plan while returning a correct fresh plan for the current
input. The current plan checks cannot see that historical change.

The exact passive witness begins at the empty n3 state and query(1,2).
Its valid global plan has62 output cells. A later preparation changes only
the retained old plan's output count to61, then prepares the honest current
plan for counts(0,0,1) and query(0,1). The new plan passes its complete check;
the old plan no longer passes its original complete check.

If Runtime retains that same old object, its previously checked phase and
an already returned snapshot change after sealing. The immutable bytes
remain intact but cease to represent their live phase metadata. This is
the output side of the frame law, across a later legal continuation, rather
than an in-call producer substitution. It need not change any prediction
word, native count, fresh statistic or numerical tolerance.

## 3. Scope and minimal evidence

`scripts/audit_indexed_amp_alias.py --cpu` produces
`FP_INDEXED_AMP_ALIAS_CPU.json`. The evidence distinguishes a correct
numerical refusal with a corrupted physical predecessor from a temporal
metadata rewrite compatible with a correct current computation.

The supplied-argument/retained-result fault class uses only a CountState
passed to the physical helper, or the planner's own previously returned
plan. There is no owner global, stack inspection, tensor write, codec
change or arbitrary process-memory access. All arithmetic functions remain
the registered implementations. No false native probability publication,
class-completeness, statistical certificate, installation or Foundation
counterexample is inferred from the passive evidence.

The repair obligation is the same component law already proved: a delegated
producer cannot receive or retain mutable reachability into owned inputs
or accepted history. Numerical refinement is a separate obligation. The
physical executor's arithmetic/workspace argument must also be accounted
for when defining its actual trust boundary; copying only one count field
would not establish a general capability-isolation theorem.

## 4. Actual CUDA registration

Two fresh4-GiB/900-second jobs are registered at unchanged production7fe0471.
All execution dependencies must be committed before `--attempt 1`; source
remains fixed while live and every outcome is retained in a new
`FP_INDEXED_AMP_ALIAS_CUDA_A*.json`.

* `physical-input-counts`: after(1,2,0), change only the supplied physical
  count from+1 to-1 during prediction. Expect native bridge refusal with no
  target or forecast publication, but a changed physical predecessor,
  earlier snapshot and older sealed phase metadata. The reference learner
  must remain unchanged.
* `later-planner-result`: retain the first honest plan, complete its event,
  then change that old plan's output count during the next preparation.
  Expect the new query(0,1) to pass, while the earlier checked phase no longer
  matches its sealed bytes. Supply target0 and compare the complete native
  and AMP update with the legal history((1,2,0),(0,1,0)); that update should
  remain correct.

These are hypotheses, not actual outcomes borrowed from the passive CPU
witnesses. They will be resolved before production repair.
