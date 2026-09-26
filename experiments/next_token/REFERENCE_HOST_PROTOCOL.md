# CPU feasibility of the complete text reference

Status: **PREREGISTERED; NOT YET EXECUTED, 2026-09-26**.
Numerical source anchor: a0610f0. The launch journal binds the complete
committed source at execution, including this protocol and its runner.

This is a two-case numerical/resource audit. It determines whether the
batched exact-endpoint reference is practical enough to integrate with the
ordinary-text Runtime/AMP path. It is not a language-model comparison,
online acquisition claim, Compiler release or full ERC-1 run manifest.
No loss is scored; no validation or test data is read. The fixed fixture is
not selected as a useful architecture from these resource measurements.

## Fixed jobs

Both cases run once, sequentially, in fresh one-process Windows jobs with
**2 GiB private commitment and 180 seconds wall time per job**. The existing
launcher creates the process suspended, attaches it before resumption, and
enforces kill-on-close without breakaway or a visible window. Imports,
fixture construction, master copies, exact controls, comparisons and report
serialization all count toward the child lifetime. The parent launcher and
shared machine/file cache are outside this measured scope. NumPy numerical
thread environment is fixed to one; no Torch or GPU is used.

The per-array element limit is 2^24. It supplements the OS commitment cap
and does not replace it. The job reports process/job peak commitment and
CPU time; stage wall times are one observation, not a stable benchmark.
Do not claim isolated acceleration from stages containing different checks.

1. **rational-control**: the previously exact-audited full-vocabulary
   synthetic fixture, context4, width2, features4, 512 records, p16,
   eta1/1024. Compare the complete gradient basis and all301,548 committed
   parameters against separate materialized-rational and scalar-enclosure
   paths. Time compilation, packing, batch enclosure/commit, scalar
   enclosure/commit, rational update and comparisons separately. Retain
   the independent controls in the same measured job.
2. **train-context512**: first512 tokens from the already verified
   FineWeb-Edu training file only; full50,257 vocabulary, distinct PAD,
   context512, width4, eight features, one512-record update, p16,
   eta1/1024, positive bases1/V. Four core SUMs average each embedding
   channel over all512 lags, sharing one native coefficient1/512 per
   channel; four PRODUCTs multiply each average by the next channel's
   lag-one embedding. Features are these eight nodes. Every embedding and
   output coordinate is trainable; all603,092 masters are retained.

For the second job the complete initializer is fixed in grid integers:

    E[v,k] = 8192 + ((v+1)(7919+2k) + 104729k) mod 49151
    theta[k] = 128
    W[y,i] = 1 + (y(2i+1) + 17i) mod 7

Its apparent average structure is supplied by this fixture, not forced by
an optimizer or discovered by construction. It makes all context coordinates
participate while remaining a modest reproducible resource probe. It is
neither the chosen language-model architecture nor a performance baseline.

The runner reads only1024 training bytes, checks the registered360,000,000
file length and unchanged metadata during the read, and identifies those
actual prefix bytes once. It cites the earlier full-file identity audit
without claiming to reverify all corpus bytes or obtain a Runtime-owned
source attestation. Retained windows use only earlier prefix positions and
PAD. Reading this already available training unit is not a freshness test.

## Outcomes and stop rules

Only sound unique grid decisions publish an endpoint. Record a numerical
UNRESOLVED with its complete retained unit and no oracle resumption. The
large-context job does not materialize its full rational unit: its endpoint
correctness remains conditional on the proved solver, separately audited
at smaller shapes. Neither that fact nor the OS fence supplies data-role,
lineage, installation or AMP authority.

Commit all source before `python -X utf8 -B scripts/audit_token_reference_host.py --run`.
An existing journal prevents rerun, including a lost observation of a live
job. Keep each original terminal outcome. Stop the attempt on a worker,
comparison, host or timeout failure; do not silently raise caps or retry.
Store only the compact job/stage/source summaries, no masters, tensors,
corpus, interval arrays or large logs.

Afterward, use the evidence to choose the practical reference/AMP
integration path. If it refuses, investigate the actual obstacle instead
of expanding relation-task variants or changing the native optimizer.
