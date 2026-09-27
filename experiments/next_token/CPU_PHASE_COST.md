# Cost of the first ordinary token event

Status: **COMPLETED CPU DIAGNOSTIC**, not a CUDA certificate or a language
result. `scripts/probe_token_phase_cost.py` runs the existing full-vocabulary
registration at implementation commit `59fea46`, with the snapshot control's
CPU device/array substitutions. It imports no Torch and reads only the already
registered first 1,024 training bytes. It neither changes nor times A2.

The worker ran once in a Windows job, attached before resume, with an 8-GiB
host limit and a 180-second deadline. It completed initialization, prediction
and the first actual target observation, retaining three phases at cursor 1.
Peak whole-job commitment was 375,259,136 bytes. The compact evidence is
`evidence/minimal/FP_TOKEN_PHASE_COST_CPU.json`; it retains the process identity,
resource observations, call counts and leading functions, not a profile dump.

Initialization took 12.3991 unprofiled seconds. The two following operations
were profiled **separately** with `cProfile`:

| Operation | Instrumented wall seconds | Recorded calls |
|---|---:|---:|
| Prediction | 15.8790 | 65,108,150 |
| Observation | 15.7076 | 63,704,483 |

The disjoint `_SharedReference.allocate` and `seal_cuda_frame` calls total
20.5685521 of 31.5866528 profiled seconds, or 65.12%. This sum does not also
count their callers or nested encoder/reader calls. Repeated canonical size,
fragment and comparison traversal dominate those calls. Program identity
hashing is not among the leading functions; this measurement does not support
making hash optimization the next research task.

This is a **first-event, instrumented, CPU-substituted observation**. Profiling
overhead depends on call frequency. These numbers do not estimate unprofiled
CUDA latency, later prefix/gradient work, whole-training cost or a speedup.
The fresh physical readbacks and numerical bridge have not been measured by
this substitution. Neither a universal lower bound nor a full-unit result
follows.

The actionable conclusion is narrower: making device storage reusable does
not by itself remove substantial repeated retention work in the current
ordinary-token Runtime. Any proposed removal of this traversal must preserve
the binding between actual complete records and independently decoded paid
evidence, including arbitrary padding and mutable-producer rejection. A
cached producer hint or a skipped physical read is not such a proof. Keep the
relation/static branches closed, preserve A2's original outcome, qualify the
already prepared physical reuse lowering, and assess the next execution from
that evidence. No additional full-vocabulary run is registered here.
