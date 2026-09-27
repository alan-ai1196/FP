# Fixed qualification of owned token storage reuse

Status: **PREREGISTERED; ACTUAL DEVICE JOBS NOT STARTED**. The lowering has
its [continuation proof and CPU controls](../../theory/proofs/TOKEN_CONTINUATION_STORAGE.md#implemented-owned-lowering-and-its-exact-scope).
Both exact proposed worker branches also pass with CPU tensor/device
substitution. This document supplies no new CUDA outcome or language score.

The new physical lowering retires sealed unreachable allocations while
retaining every historical word and all unsealed attempts. This requires
its own actual-device qualification: the earlier append-only reporting jobs
cannot establish generation guards, physical address reuse or the revised
snapshot boundary. Those jobs remain terminal and must not be replayed.
Foundation/ERC, the native G/Gamma/U and numerical tolerances stay unchanged.

## Registration and publication order

First preserve the actual terminal shared-retention A2 journal and its fixed
307251e execution. Commit that result, integrate the prepared isolated
research commits into canonical main, then commit all qualification inputs.
Only then run `python -X utf8 -B scripts/run_token_reuse_cuda_a1.py --run`.
The launcher requires the canonical worktree, clean committed sources, a
terminal A2 job record, and a nonexistent FP_TOKEN_REUSE_CUDA_A1.json journal.
It records the actual source commit and creates that new journal exclusively.
A slow A2 checkpoint is not permission to interrupt/restart it or launch here.

The two workers run sequentially in separate processes, each attached to its
Windows job before its first instruction. Stop on the first failed worker;
preserve the original outcome. Neither a terminal success nor a terminal
failure may be replayed under the same registration.

| Fixed resource/numerical field | Value per worker |
|---|---:|
| Whole-job host commitment | 4 GiB |
| Wall limit | 180 seconds |
| Actual tensor backing arena | 8,192 bytes |
| Native allocator reservation cap | 2 MiB |
| Reference payload cap | 256 MiB |
| Work per role | 10^15 |
| Complete phase frame | 1 MiB |
| Output-cell cap | 4,096 |
| Exact rounding-cell cap | 4,096 |
| State / probability tolerance | 1/4 / 1/10000 |
| Reporting log terms / mean bits | 12 / 40 |

Both roles receive the full arena/reservation charge. Shared storage uses the
existing `audit_shared_token_retention.STORAGE` registration: literal,
program, expanded and reference limits2^20, comparison limit2^22. The pinned
RTX3090/PyTorch/CUDA identity and whole-board24-GiB bound are unchanged. The
expected native allocation counters are exactly(1,8192,1); tensor lifetime
peak is8192 and allocator reservation/lifetime peak2 MiB. No reset or cache
clearing is permitted. Buddy live occupancy must fit8192 even though
cumulative requests exceed it. These are fixed physical caps, not a promise
that every legal model fits this arena.

## The two finite decision classes

`reuse-training` uses the existing two-label mixed token fixture, update
unit2, ordinary targets(0,1,1,0) repeated four times, then frozen reports(0,1).
It must complete16 observations/eight units and two reports, retaining45
checked phases and19,164 checked array words. A saved first forecast view
must be retired, its entire address interval reused by a later array, and
its numeric read refused. Both attempted public normalization-dictionary
writes must refuse. The native and physical learners remain frozen during
reporting; the proper physical mean has a positive lower bound. The exact
score enclosures are diagnostic outputs of this finite toy control.

`unsealed-retention` declares four training events but observes only(0,1),
predicts the third event and reveals target1. Inject a resource refusal at
the complete shared-frame sealing boundary after actual array execution.
The original target and pre-failure learner must remain, with no successor
published. All of that attempted phase's generations and its header stay
pinned. The expected result is eight retained phase records, seven CHECKED
records and3,351 checked array words including the failed attempt's completed
numeric execution. Addresses must already have been reused elsewhere; the
saved first forecast view must refuse. This shorter trace does not require
that particular saved view's whole interval to have been overwritten.

The proposed worker branches pass `scripts/audit_token_reuse_cuda.py
--cpu-control` with these counts. The first CPU prototype incorrectly
required the shorter failed prefix to have fully overwritten the specific
saved forecast extent; it had retired it and reused other addresses. That
pre-device assertion was corrected to the distinct claims above. No actual
device job was attempted, interrupted or retuned.

The launcher independently checks phase/event counts, original process
identity, OS peak commitment, lifetime allocator observations and the
declared outcome conditions. `PASS_ACTUAL_OWNED_TOKEN_REUSE` means only those
finite owned executions. It is not `CERTIFIED_COMPLETE`, full-vocabulary
fit, full-corpus feasibility, throughput, installation or model quality.
After this qualification, stop toy reuse variants and follow the observed
A2 training constraint toward a concrete ordinary-text comparison with
adequately trained Transformer and n-gram baselines.
