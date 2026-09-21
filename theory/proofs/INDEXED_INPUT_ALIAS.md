# Owned prediction inputs cannot share writable authority with their helpers

Status: **three actual CPU Runtime counterexamples at a559d7a**; three fresh
actual CUDA probes registered and pending. No production change has been
made for these probes. The indexed input boundary is HOLD for extension and
further model use. Foundation R4 and the earlier byte-only codec theorem
are unchanged.

## 1. The causal input can change before its own check

The existing owned reference path calls
`machine.prepare_prediction(program, rules, state, sources, ...)` before
re-reading the query from `sources`. It compares the returned plan's before
state with `state.encoded`. The same live records and source dictionary have
already been supplied to the helper. The executor likewise receives a plan
whose before record aliases the actual native predecessor.

Returned-field substitution tests do not cover mutation of these shared
inputs. Two comparisons can agree after both have lost their original
anchor. This is the same source-stability premise identified at the byte
writer boundary, now upstream of numerical execution. Retaining every byte
of a produced phase does not establish that the phase used the actual
context or legal native history.

## 2. An ordinary source-map write changes both prediction and learning

Take n3 and the actual committed event(1,2,0). The three signed counts,
in pair order(0,1),(0,2),(1,2), are(0,0,1). The next actual context is
query(0,1), whose native forecast is(1/2,1/2).

The substituted preparation helper clears only its supplied source
dictionary, fills it with the valid categorical row for query(1,2), and
then calls the original honest preparation routine. It does not inspect a
stack, use an owner global, alter a numerical kernel or modify any codec.
Runtime's subsequent query check reads the same changed dictionary.

The actual CPU Runtime publishes PREDICTED_REFERENCE with query(1,2) and
forecast(41/50,9/50), while its retained ObservationRecord still says(0,1).
The probability discrepancy is8/25. Counts, cursor and the unrevealed target
are unchanged at this cut; the point forecast already violates the actual
native input relation.

Then supply the actual target0. Runtime commits a second unit and publishes
counts(0,0,2). The actual received history is((1,2,0),(0,1,0)), which requires
counts(1,0,1). Independent literal native execution gives theta
(1,81/100,9/100,1/100,9/100), whereas the published indexed learner decodes
to(1,81/164,1/164,1/164,81/164). Thus this is also a complete native-update
counterexample, not merely a diagnostic query label mismatch.

## 3. Mutating a supplied count record also rewrites retained history

After the same first event, request the actual query(1,2). Its native
forecast is(41/50,9/50). A preparation helper changes only the supplied
CountState.counts from(0,0,1) to(0,0,-1), then calls honest preparation.
The exact count type and its declared absolute-count/step guard still hold.
The before-state comparison sees the changed record on both sides.

Runtime publishes(9/50,41/50) at the same cursor1 without a second target.
Its live native count is now-1 despite the actual earlier target0, and an
already returned snapshot's native payload changes. A separate executor
probe performs the same mutation through `plan.before`, after the complete
plan has been checked; it has the same outcome. No owner handle beyond the
supplied argument is used. The attacks use `object.__setattr__` on a supplied
frozen dataclass, as in the former writer-alias audit; this is not a claim
of protection against arbitrary process-memory writes.

## 4. Exact evidence and decision scope

`scripts/audit_indexed_source_binding.py --cpu` reproduces all three cases in
the real Runtime, with no numerical owner mock. It compares both forecasts
and the source-map case's complete learned theta with the independent literal
program, learner and exact arithmetic. The deterministic minimal result is
`FP_INDEXED_SOURCE_ALIAS_CPU.json`; counts, contexts, targets and old snapshot
bytes are captured before delegation rather than compared through an alias.

These witnesses falsify owned causal input binding and native continuation
under the supplied-argument fault class. They are not counterexamples to
fixed-input positive partition algebra, fixed-plan RNE interpretation,
the byte-only compressor's source isolation, Foundation R4, statistical
validity conditional on legal inputs, or a class-optimality theorem. No
fresh-evidence certificate or installation counterexample is asserted.

The earlier [owned projection audit](OWNED_QUERY_PROJECTION.md) tested altered
returned fields and execution results. Its ordinary valid-input numerical
checks remain evidence; its unqualified helper-binding conclusion does not.
The newly proposed paid order solver is paused until this input boundary is
made concrete. Copying only a reported query, or repeating equality against
the same count object, would leave the causal defect intact.

## 5. Actual CUDA registration

The same script registers three fresh4-GiB/900-second jobs, with production
unchanged from a559d7a and byte-only zlib evidence enabled. The cases are
planner-sources, planner-counts and executor-counts. All dependencies must
be committed before `--attempt 1`; HEAD and execution inputs stay fixed
while live. Every outcome is retained in a new
`FP_INDEXED_SOURCE_ALIAS_CUDA_A*.json`, including any failed expectation.

The source-map case first records its pre-target prediction, then supplies
target0 and checks the complete committed learner against the legal history.
The registered hypothesis is that reference and AMP follow the same corrupted
mapping and publish the wrong update. The two count cases instead expect
the independent AMP predecessor comparison to refuse, while the native
count history and old snapshots have already changed. They check whether
older immutable phase bytes still match their now-live metadata.

These are hypotheses for the actual device probes, not outcomes borrowed
from CPU. Even a correct numerical refusal would not by itself repair a
corrupted retained predecessor. The research obligation is a causally stable,
paid input interface that leaves both live and historical state valid after
helper faults, followed by the normal source/AMP/lineage gates.
