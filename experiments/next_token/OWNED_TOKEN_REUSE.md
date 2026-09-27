# Fixed qualification of owned token storage reuse

Status: **BOTH ORIGINAL ACTUAL DEVICE WORKERS PASS AT6941373; TERMINAL**.
The registration below remains unchanged; the actual result is at the end.
The lowering has
its [continuation proof and CPU controls](../../theory/proofs/TOKEN_CONTINUATION_STORAGE.md#implemented-owned-lowering-and-its-exact-scope).
Both exact proposed worker branches also pass with CPU tensor/device
substitution. The device result has the same finite scope and no language score.

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

## Actual device result and closure

Both original workers at69413732957f09a206b801ebb9eab24ccc264faf **PASS** and
exit0. They ran only after original A2 termination, journal commit1043dcc,
integration c949fbc and scope reconciliation6941373. The terminal journal is
`evidence/minimal/FP_TOKEN_REUSE_CUDA_A1.json`; no worker was retried and it
must not be replayed. Source and all registered caps/tolerances stayed fixed.

| Fixed case | Actual result | Peak host job bytes | Launcher wall seconds |
|---|---|---:|---:|
| reuse-training | 16 targets,8 commits,2 reports,45 checked phases,19,164 words | 1,943,650,304 | 8.6675261 |
| unsealed-retention | 2 completed targets,1 commit,8 retained/7 checked phases,3,351 words | 1,951,346,688 | 3.9082772 |

Both retain exactly one8,192-byte tensor backing allocation, with2,097,152
actual/lifetime reserved bytes and unchanged counters(1,8192,1). Neither
resets counters or caches. The successful trace peaks at5,096 occupied bytes,
spends120,304 cumulative buddy bytes and retires5,341 generations. It actually
overwrites the saved first forecast extent, then rejects that stale view.
Both public snapshot normalization writes raise TypeError. All45 header
records survive; the frozen native/physical learners remain unchanged during
reporting. Its owned reference peak is4,699,152 bytes.

The successful physical mean enclosure is
`[784545145481/1099511627776, 392272900421/549755813888]` nats, with positive
lower endpoint. The native enclosure and complete resource observations are
in the journal. These are the toy qualification's scores, not corpus results.

The failure trace peaks at5,008 occupied bytes, spends21,136 cumulative buddy
bytes and retires755 generations. After the actual third target1, refusal at
complete frame sealing keeps all185 failed-phase generations and its header;
cursor2 and the preceding committed learner remain, with no successor. Its
saved forecast is retired and refuses; that particular whole interval is not
overwritten in this shorter trace, exactly as preregistered. Other addresses
are reused. All eight header records survive; owned reference peak is
3,629,880 bytes. The3,351 word count includes the failed attempt's completed
numeric execution, not eight successful retained phases.

This closes the two finite physical-lowering/snapshot-boundary cases. It is
not a full-V capacity measurement, training-throughput estimate or broader
Compiler release. Stop reuse/reporting controls here. The full-V A2 establishes
one unit in about2h57m on its different append-only source; its result must
not be attributed to this lowering. Address the measured cost of complete
ordinary-token execution before another long run or a model-budget choice.
