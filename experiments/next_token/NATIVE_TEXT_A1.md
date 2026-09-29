# Native FP text trial A1

Status: **PREREGISTERED; NO ACTUAL OUTCOME AT REGISTRATION, 2026-09-29**.

This is the first attempt to obtain an owned trained FP result on the actual
text view used by [baseline anchor A1](BASELINE_ANCHOR_A1.md). It uses the
complete native ReferenceCompilerRuntime, including every prediction,
observation, exact represented gradient, optimizer commit, range proof,
resource lease and frozen reporting event. It uses no CUDA execution and
claims no AMP-trained result. Actual GPU runs retain all their bridge duties.
No passive helper replaces a live Runtime transition or reporting authority.

## Scientific choice and limits

Select one explicit incumbent G/Gamma/U for this trial: the previously
unselected resource fixture in `audit_token_reference_host.text_model_fixture`.
This is now an empirical hypothesis about that supplied learner. Choosing the
already executable graph makes its learning test concrete; it does not assert
that the graph is optimal, representative of all FP, or forced by a complete
Compiler search. No graph replacement, construction search, persistence test,
installation or model-selection certificate occurs during the run.

The model uses V=50,257, context 512, width four and eight shared head features.
For channel k, its first four features are parameterized sums over all 512
lag embeddings. The next four multiply each such sum by channel (k+1) mod 4
of the newest token. The readout is b_y+sum_k W_yk f_k with b_y=1/V.
All E, core and W coordinates are trainable, including PAD and inactive slots.
There are 603,092 masters. The full lag/token source family and graph edge
counts remain declared even where the execution uses indexed lookup.

The supplied initialization is unchanged: integer embedding masters
8192+((v+1)(7919+2k)+104729k) mod 49151, four core masters 128, and readout
masters 1+(y(2k+1)+17k) mod 7. U is the existing mean-CE nonnegative projected
SGD with floor to Q=65,536, rate 1/1024 and update unit 512. No new residual,
regularizer, optimizer action or adaptive precision is introduced.

The known [capacity](FROZEN_READOUT_CAPACITY.md) and
[update-cell](GRID_UPDATE_DYNAMICS.md) limitations are part of the interpretation:
this graph pools older order and has at most nine fixed readout mixture
components during reporting; its first unit has one-sided embedding steps
and substantial core/readout changes. These facts do not establish useful
learning or inevitable collapse. A poor score would concern this trained
G/Gamma/U and data schedule, not prove that FP cannot model language. There is
one FP configuration and no validation-based checkpoint/hyperparameter choice.

## Data, training and reporting

Use exactly train.bin [0,1,048,576), one chronological pass, giving 2,048 whole
update units. The prefix byte identity must equal the completed baseline
anchor's identity. The worker submits only `predict_next` then `observe` for
each original target; Runtime derives every context from its owned revealed
prefix. No external context, trained state or gradient is supplied. EOT stays
ordinary, and the first source prefix uses PAD. No epoch or shortened-horizon
replacement is allowed if the declared run cannot finish.

Only after all training targets and commits complete may `begin_report`
freeze the same incumbent and open val.bin [0,16,384). This reporting view
must match the baseline anchor's byte identity. Score every event through
`predict_report`/`observe_report`; the reported comparison suffix is original
positions [4,096,16,384), retaining the preceding validation context. Do not
restart its source at position 4,096. No held-out target updates parameters.
The historical validation asset is development data, not fresh test evidence.

Native log intervals use the registered 16 terms, 32,768-bit integer guard
and 40 fractional accumulator bits. Let A_t and B_t be the *exact stored
integer* sums of the per-event lower floors and upper ceilings. Then the
suffix mean is enclosed by

    [(A_16384-A_4096)/(2^40*12288),
     (B_16384-B_4096)/(2^40*12288)].

Matching endpoint subtraction is justified by the additive accumulator
recurrence: each difference is exactly the sum of its suffix's directed
integer terms. This is not subtraction of two unrelated unknown intervals.
The CPU control checks this on an owned trained/reported trajectory against
the original exact event bounds; each endpoint adds less than 2^-40 rounding
error. The full-prefix mean is also retained. Physical mean remains absent.

Compare only if this full trial finishes. The baselines use the same unique
training view, full alphabet and reporting targets, but their exposures,
context and parameter counts differ: the Transformer receives sixteen
million sampled-block target exposures per rate candidate and context 256;
this FP learner receives one million chronological exposures and context 512.
MKN uses up to four prior tokens. Do not claim all resources/exposures are
matched, or attribute a gap solely to architecture. Baseline convergence is
also unestablished. A timeout or numerical refusal yields no FP model score.

## Registered resources and execution

Run `python -B scripts/run_native_text_a1.py` once after committing the inputs.
The original worker starts suspended, attached to a one-process Windows job
with a **two-hour wall limit and 96-GiB process/job commitment cap**. Both
Runtime host roles bind that same actual cap. No Torch/CUDA is imported.
NumPy/BLAS/OpenMP thread counts are one. This is a bounded feasibility/learning
attempt, not a claim that a million targets already fit the implementation.

The reference ledger permits 64 GiB of live packed payload and 2^26 physical
objects globally and in each of its compiler/deployment roles, with 2^63
abstract work units per role. The existing shared-byte archive is used with
64-MiB literal, 16-MiB program, 128-MiB expanded-record, 2^23 reference and
1-GiB comparison allowances. Canonical image capacity is 8 GiB and base-fact
capacity 4 MiB. Misses keep the original complete serializer. The parked
expression codec is disabled. Per-array numerical capacity is 2^24 elements;
uint32 masters and every ambiguous-cell refusal remain unchanged.

Range caps are activation 2^80 and normalizer 2^96. These exceed a direct
worst-case bound for this graph's representable uint32 masters: each real
parameter is below 2^16, lag sums below 2^41, PRODUCT features below 2^57,
head excess below 2^76 and normalizer below 2^93. Thus the old resource test's
arbitrary cap 100 does not select a numerical learning trajectory here.
Runtime still proves and retains the actual range bound after each update;
the enlarged cap grants neither unbounded arithmetic nor AMP authority.

The current implementation repeatedly copies/scans growing resource maps
and histories. This may prevent the horizon from fitting even without AMP.
Do not erase retained information, skip ledger checks, replace the full
history by the latest unit or shrink the task to force a score. Record the
actual obstruction and use it to choose the next solver/Runtime work.

Numerical uncertainty, work/storage exhaustion, implementation error or
timeout makes the original attempt incomplete/UNRESOLVED, with its reason
and last observed state counters retained. A timeout heartbeat is only the
last reported completed prefix, not an assertion about the exact kill cursor.
Never restart the original job, raise its cap or score an unfinished prefix.
Any changed trial needs a separate question and preregistration.

## Minimal evidence and stopping rule

The exclusive journal is `evidence/minimal/FP_NATIVE_TEXT_A1.json`; active
worker diagnostics reside under `F:\experiment\FP_next_token_native_a1`.
Retain logarithmic progress milestones and one latest heartbeat, source and
process identities, final exact score bounds only on success, resource peaks
and the actual exit/refusal. A successful frozen master artifact is external
audit data, not a resumable Runtime checkpoint or installation receipt.
Do not put datasets, weights, archive pages or per-event logs in Git.

The assembly control preserves original reporting contexts and the frozen
learner identity, checks three suffix reductions, and compares the bounded
resource inspection with a full snapshot. Existing native/runtime/reporting
qualifications remain their own evidence. This introduces no new complete
decision class or Foundation/ERC definition.

After the original attempt, interpret its score or precise blocker against
the actual ordinary-text objective. Do not turn this into another static
precision, archive-codec or baseline branch. The full trained FP comparison
remains required; an honest UNRESOLVED result does not complete that goal.
