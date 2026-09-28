# Remaining cost after the qualified token lowerings

Status: **COMPLETED CPU DIAGNOSTIC; CANONICAL RETENTION IS THE MEASURED TARGET**.

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

## Original outcome

The original worker at `075eba1da7493582665b8801a61430ac02876be6` completes
under the registered limits, with peak whole-job commitment 2,497,671,168 bytes.
All 33 phases/4,541,709 primitive words, 16 original records, pending count 16
and zero commits pass. No CUDA context is initialized. The paid reference peak
is 272,950,310 bytes, with the original 1,407,321-byte base fact and 67,102,758
canonical-image bytes. The journal is terminal; it must not be replayed.

| Profiled operation | Wall seconds | Calls | Retention/preparation/write seconds | Numerical execution seconds |
| --- | ---: | ---: | ---: | ---: |
| Prediction, index 0 | 5.2065313 | 18,597,902 | 4.2998899 | 0.7906841 |
| Observation, index 0 | 4.9003222 | 17,211,003 | 4.1569646 | 0.6114926 |
| Prediction, index 15 | 6.1422928 | 22,534,385 | 5.0525165 | 0.9647925 |
| Observation, index 15 | 5.8534433 | 21,149,166 | 4.9579045 | 0.7162643 |

The four samples total 22.1025896 instrumented seconds and 79,492,456 calls.
The four disjoint retention/encoding subtrees total 18.4672755 seconds,
**83.55254%** of sample wall time; numerical execution totals 3.0832335 seconds,
13.94965%. The remainder is unassigned. Source inspection and all four recorded
caller-graph checks exclude nested selected subtrees, so these sums do not
double-count a callee through its parent. Individual retention shares range
from 82.26% to 84.83% in these samples.

Canonical extent guards, size traversal, fragment generation and independent
stream comparison remain leading routines. This does not license deleting any
of those checks. It identifies their implementation as the next target while
the complete value/guard/decoder relation stays fixed. Initialization takes
9.5358609 unprofiled seconds and the 28 intervening calls total 52.4690037
unprofiled seconds in the same CPU worker. Neither those numbers nor the
profile fractions estimate the GPU's cost decomposition or a full-unit budget.

The concrete question selected was whether the canonical byte grammar admits a
cheaper exact extent calculation without changing serialized bytes, integer/
depth/traversal allowance decisions, mutable-field observation order or the
independent decoder comparison. This is a general trusted-encoding question,
not a new FP cache, model special case or relaxed evidence contract. The current
diagnostic is closed. The subsequent
[direct extent law and actual comparison](../../theory/proofs/DIRECT_CANONICAL_EXTENTS.md#actual-result-and-closure)
now close that question: exact/complete controls pass and one ordered actual
pair reduces ordinary time from 62.05694 to 55.44789 seconds. This profile's
fractions do not describe the subsequently changed path. Remaining complete
stream production/comparison and later-prefix costs still constrain a
demonstrated budget. Ordinary text learning with strong trained baselines
remains the objective.
