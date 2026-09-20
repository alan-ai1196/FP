# Tighter-bound owned likelihood deployment: completed results

Status: **COMPLETE FOUR-CASE MATRIX; THREE IMPROVE, ONE WORSENS**.
All four registered workers seal, pass their independent readers and install
under the original caps. Execution and analysis both use immutable `8ccacc0`.
The [protocol](LIKELIHOOD_DEPLOYMENT_PROTOCOL.md), ordered cases and controls
are unchanged. The [terminal journal](../../evidence/minimal/FP_LIKELIHOOD_DEPLOYMENT_EXPERIMENT.json)
and [same-source analysis](../../evidence/minimal/FP_LIKELIHOOD_DEPLOYMENT_ANALYSIS.json)
retain every outcome.

## 1. Deployment timing changes while candidate predictions stay identical

The new common bound is 13/8 with coefficient 6/13; the retained B6 procedure
uses coefficient 1/8. Every candidate stored-mass and raw-division word is
identical to its old control. The observed score differences therefore come
from deployment timing on these fixed tapes.

| n8 case | Install, old -> new | Fresh wait, old -> new | Candidate unseen CE, both | Deployed unseen CE, old | Deployed unseen CE, new |
|---|---:|---:|---:|---:|---:|
| iid-c2, seed16 | 114 -> 119 | 54 -> 59 | 0.3429612915 | 0.6596867981 | 0.6764169893 |
| iid-c2, seed17 | 90 -> 67 | 30 -> 7 | 0.3340278121 | 0.5007499814 | 0.3752735502 |
| iid-c4, seed18 | 72 -> 54 | 32 -> 14 | 0.3806734300 | 0.5014470727 | 0.4094547653 |
| iid-c4, seed19 | 72 -> 50 | 32 -> 10 | 0.3502262118 | 0.5167830813 | 0.3787700980 |

Seed16 loses five deployed forecasts and its unseen CE worsens by
0.0167301912 despite the tighter valid bound. Seeds17/18/19 gain 23/18/22
deployed forecasts. Full-domain deployed CE changes respectively
0.6356371482 -> 0.6643921644, 0.4976130705 -> 0.3653399982,
0.5091150770 -> 0.4056148270 and 0.5091150770 -> 0.3826013266.

Across these four fixed cases, mean deployed unseen CE falls from
0.5446667333 to 0.4599788507, a descriptive improvement of 0.0846878826.
Mean full-domain deployed CE falls from 0.5378700932 to 0.4544870790.
The unchanged candidate mean unseen CE is 0.3519721863; the retained strong
exact posterior mean is 0.3519714364. Thus a substantial deployment gap
remains. All strong AMP posterior controls are also retained and rechecked.
These are exposed retrospective cases, with no population effect estimate
or uniform first-passage ordering. Uniform improvement is falsified by seed16.

## 2. Actual crossings and prior conditional predictions

Both owned reference and CUDA paths cross at 119/67/54/50, exactly at the
actual installation cursors. Each transport/install receipt passes. The
terminal identities retain those historical crossings but become
`UNRESOLVED` after deployment changes the base; they grant no reusable
authority. Every constructor class also remains `UNRESOLVED`: one owned v7
proposal executes per case, with no complete-class proof.

The final worker seals at cursor 104 after 40 training and 64 evaluation
events. Its two paths each score ten fresh labels, crossing at 50 with
reference wealth 314235/65536 and AMP wealth 19639/4096. Installation leaves
54 forecasts, compared with 32 under B6. The total alpha spent is 1/2.

The [earlier conditional prediction](../../theory/proofs/TIGHTER_BOUND_DEPLOYMENT_TRADEOFF.md)
fixed all four paired cursors and unseen/full-domain deployed risk envelopes
before any completed new outcome. All four actual cursors and all eight
deployed CE values lie inside those prior exact intervals. This verifies
the conditional calculation on the completed executions; it does not turn
that calculation into a general power ordering.

## 3. Complete execution and independent evidence

Every worker exits 0 without timeout or a job-limit termination. Each was
attached to its bounded job before resumption, under 16 GiB and two hours.

| Worker / seed | Seal cursor | Completed job peak, bytes | Posterior forecasts | CUDA and binary64 phases, each | Native commit tapes | Fresh scores, both paths |
|---|---:|---:|---:|---:|---:|---:|
| 2444 / 16 | 124 | 15,047,073,792 | 64 | 748 | 248 | 118 |
| 6920 / 17 | 124 | 15,034,691,584 | 64 | 748 | 248 | 14 |
| 30700 / 18 | 104 | 12,994,330,624 | 64 | 628 | 208 | 28 |
| 4056 / 19 | 104 | 13,017,206,784 | 64 | 628 | 208 | 20 |
| Total checks | | | 256 | 2,752 | 912 | 180 |

The same-source terminal reader independently checks 24 new model scores
and eight fresh paths, plus all 24 old B6 scores, four old decisions and
16 strong-control scores. No baseline worker is rerun. Before final
collection, every registration field and the first three complete worker
records are checked unchanged. The reader then consumes one frozen byte
capture of the terminal journal, and its first three analysis rows are
also checked unchanged. The retained raw journal and analysis suffice;
no weights, cache or additional completion bundle is retained.

The final worker's packed peak is 2,694,743,715 bytes and maximum candidate
mass-posterior error is 1055845445464353/15810895495970635730. Its 628 phases
per path, 208 commit tapes and all candidate words pass the same checks as
the earlier rows.

Parent14264 and final worker4056 are absent at the terminal observation
2026-09-20 20:58:54 UTC, and the source journal is `COMPLETE_EXECUTION`.
This matrix is finished; do not restart it. It overlapped both the completed
n16 recovery at `75e4f93` and the separately registered matched v7/v8 run at
`ec373e7`. No exclusive-device timing claim is made. The matched experiment
remains independent and continues under its original protocol.
