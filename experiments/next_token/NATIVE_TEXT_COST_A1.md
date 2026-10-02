# Complete native text path: bounded cost diagnosis A1

Status (2026-10-02): **ORIGINAL DIAGNOSTIC COMPLETE AT `b6d5569`; CLOSED**.

## Original result and next question

The single original worker completes with exit zero, no timeout and a
549,490,688-byte peak job commitment. Initialization takes 12.71403 seconds;
the whole worker takes 35.70524 seconds. All sixteen original sources, targets
and event traces, sixteen pending targets, zero commits and complete live
buffer/lease accounting pass. The full million-target declaration remains.
No Torch, AMP, reporting or model score occurs. The original journal is terminal.

| Instrumented operation | Wall seconds | Calls | Retention subtree seconds |
| --- | ---: | ---: | ---: |
| Prediction at 0 | 1.6228906 | 6,060,433 | 1.4065217 |
| Observation at 0 | 2.3165855 | 8,752,177 | 2.2079881 |
| Prediction at 15 | 1.7252313 | 6,140,212 | 1.4855956 |
| Observation at 15 | 2.3824464 | 8,939,989 | 2.2518825 |

Across these four disjoint samples, `_SharedReference.allocate` takes
7.3519879 of 8.0471538 instrumented seconds, **91.36134%**. This sums the
same subtree across separate calls; it does not add nested parent/child rows.
The samples total 29,892,811 calls. The 28 unprofiled intervening operations
total 14.0022540 seconds; neither that number nor the instrumented shares
establish a full training budget or later-prefix scaling law.

Canonical fragment generation, coalescing and independent decoded-stream
comparison lead the retained function evidence. Per-module ledger self-time
is small in this early prefix, although that excludes callees and does not
refute growing ledger/history costs later. This diagnostic does not isolate
each descendant of the retention subtree, measure optimizer commits or
establish the old interrupted worker's final outcome.

Native-only execution has not removed the dominant complete-retention cost.
The next question is whether the *same* canonical grammar and complete checked
streams admit an efficient bulk/native implementation, with bounded workspace,
unchanged guards and field observations, independent expected/decoded values
and terminal failures. No new codec, persistent cache, partial-state shortcut,
ledger rewrite or static relation case is selected by these measurements.
An implementation/proof must precede a new cost comparison; this journal is
closed and must never be replayed. Affordable full ordinary-text training remains
unestablished.

## Original registration

The original [native text trial](NATIVE_TEXT_A1.md) has a surviving 1,280-target
heartbeat and missing terminal execution evidence. It does not establish a
timeout or model score. The caller-boundary repair is qualified and merged.
Before optimizing or starting another long attempt, measure the current native
path. The old CPU-substituted AMP profile concerns a different execution path.

Commit this protocol and `probe_native_text_cost.py`, then launch that script
once with `--run`. One fresh worker is attached before resumption to a
one-process Windows job with a **180-second wall cap and 16-GiB process/job
commitment cap**. Both Runtime host roles bind that cap. BLAS CPU threads are
one. No Torch or CUDA may be imported, and no reporting/test data are opened.

Keep the original full-V/unit512 model, Gamma/U, million-target stream
declaration, reporting declaration and reference/archive/image/base-fact caps
from `run_native_text_a1.registration()`. Read the same one-million-token
training view and verify its recorded prefix identity. Process only the first
sixteen original targets through ordinary public `predict_next`/`observe`, as
a cost diagnostic. No learned-model score, complete optimizer unit, shorter
training experiment or full-horizon feasibility claim follows.

Profile prediction and observation at indices zero and fifteen separately with
`cProfile`; time initialization and intervening operations without that inner
profiler. Keep leading cumulative/self-time functions and per-module self-time
sums, plus call counts. Self-time groups are disjoint; cumulative parent/child
times overlap and must never be summed as a partition. Instrumented fractions
do not establish unprofiled throughput or asymptotic cost. All original native
arithmetic, pre-target recomputation, guard, retention and ledger operations
remain enabled; instrumentation supplies no Runtime authority.

Acceptance checks all sixteen exact original contexts/targets/traces, pending
count sixteen, zero commits, original full declaration, every live buffer/lease,
no reporting and no Torch/AMP. The small native harness control must pass before
launch. The new exclusive journal `FP_NATIVE_TEXT_COST_A1.json` retains the
source, original OS identity/exit/caps and compact profiles. It must not be
overwritten or retried. A failure remains UNRESOLVED. No full profile dump,
weights, cache or dataset enters Git. No source changes occur during the job.

Use this single diagnostic to identify the next complete-native solver problem.
It is not permission to erase history, bypass ownership, relax AMP obligations
or reopen static precision/relation families. The full trained ordinary-text
comparison remains required.
