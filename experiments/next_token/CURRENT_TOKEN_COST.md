# Remaining cost after the qualified token lowerings

Status: **FIRST CPU DIAGNOSTIC REGISTERED; NOT LAUNCHED**.

The terminal [workspace comparison](../../theory/proofs/TOKEN_WORKSPACE_LIVENESS.md#actual-result-and-closure)
preserves complete values across actual device retirement but gives ordinary
times of 61.64774/61.88329 seconds for 16 targets and identical peak storage.
Native composition and grouped fresh reads likewise show small early-prefix
timing differences. Their source-count laws do not establish affordability.
Base-fact reuse gave a substantial finite reduction, so the old first-event
profile, which predates that implementation, cannot identify today's dominant
cost. A new diagnosis must precede another optimization or long experiment.

`scripts/probe_current_token_cost.py` registers one fresh CPU worker inside a
preattached 240-second/8-GiB Windows job. It keeps the original full-V/unit512
fixture and its 603,092 masters, complete numerical checks, 1-GiB arena,
2-GiB reference payload, 64-MiB phase frame, 2^22 output-cell allowance,
4,096 exact-cell bound and original tolerances. Generation reuse, 64 MiB of
owned canonical images and 4 MiB of qualified base facts are enabled. Grouping,
native composition and workspace archival are disabled, matching the resident
arm of the terminal comparison. No parameter or update schedule changes.

Only the existing first 1,024 training bytes are opened. One complete Runtime
history processes the original first 16 targets. The device binding uses the
existing audit's actual Torch CPU tensors and real generation arena. No CUDA
context may be initialized. Initialization and the middle 14 events are timed
without an inner profiler; prediction and observation at event indices 0 and
15 each get a separate `cProfile`. Every operation/check/retention still runs.
The terminal control requires all 33 successful phases, 4,541,709 checked
primitive words, all original contexts/targets, 16 pending records and no commit.

Five source-identified call subtrees partition part of each profiled sample:
reference-object retention, phase-image preparation, canonical frame writing,
complete frame retention and token numerical execution. The captured caller
graph must also show that none contains another. Their cumulative times may
then be added without counting a nested routine twice. The remainder is
unassigned wall time, including measurement overhead; it is not attributed
to a specific routine. Leading cumulative/self functions and total call counts
are retained, without a full profile dump or model state.

This is an instrumented CPU-substituted cost diagnosis. It does not measure
GPU transfer/driver time, unprofiled CUDA throughput, a complete unit, a
training budget or model quality. The two prefix positions do not establish
an asymptotic cost law. CPU allocation checks substitute physical device
accounting and confer no new Runtime/device certificate.

Commit the script and registration before its first launch. The exclusive
`FP_CURRENT_TOKEN_COST_CPU_A1.json` records clean source, original process
identity, limits and the bounded outcome; never replay a partial/terminal
journal or raise a failed cap. Use the original result to choose the remaining
ordinary-text research problem. This is no reopening of the static, relation,
precision or storage-variant branches. Foundation/ERC stay frozen.
