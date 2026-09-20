# Tighter-bound owned likelihood deployment: partial results

Status: **TWO OF FOUR JOBS COMPLETE; REGISTERED MATRIX STILL RUNNING**.
Execution and independent reader both use immutable8ccacc0. The
[protocol](LIKELIHOOD_DEPLOYMENT_PROTOCOL.md), ordered cases and all caps
remain fixed. The [journal](../../evidence/minimal/FP_LIKELIHOOD_DEPLOYMENT_EXPERIMENT.json)
and [same-source analysis](../../evidence/minimal/FP_LIKELIHOOD_DEPLOYMENT_ANALYSIS.json)
retain both actual outcomes. No uncompleted case receives a score.

## 1. A valid tighter bound can worsen actual deployment

Case(8,iid-c2,16) seals at124 and installs at119, leaving five forecasts.
The old B6 result installed at114 and left ten. The exact and actual AMP
candidate forecasts have not deteriorated: all candidate stored-mass and
raw-division words equal the retained control. The loss comes from later
deployment, despite the larger valid evidence coefficient.

| Procedure | Install | Fresh wait | Candidate unseen CE | Deployed unseen CE |
|---|---:|---:|---:|---:|
| Retained B6, coefficient1/8 |114|54|0.3429612915|0.6596867981|
| Current B13/8, coefficient6/13 |119|59|0.3429612915|0.6764169893|

The new unseen CE is0.0167301912 worse. Full-domain deployed CE changes
from0.6356371482 to0.6643921644. This is an actual retrospective counterexample
to uniform deployment improvement, not an estimate of a population effect
or the completed matrix's average. The candidate remains useful in isolation.

Both owned reference and CUDA paths score59 fresh labels and cross at119;
the full transport/install receipt passes. Their terminal identities become
historical when deployment changes, rather than granting reusable authority.
The constructor class stays `UNRESOLVED`: this is one executed v7 proposal.

## 2. The next tape benefits from the same fixed change

Case(8,iid-c2,17) also seals at124, but installs at67 versus the old90.
Its wait falls30 to7 events, leaving57 instead of34 deployed forecasts.
Again, every candidate mass and raw-division word equals the retained B6
control. The change affects deployment timing, not candidate quality.

| Procedure | Install | Fresh wait | Candidate unseen CE | Deployed unseen CE |
|---|---:|---:|---:|---:|
| Retained B6, coefficient1/8 |90|30|0.3340278121|0.5007499814|
| Current B13/8, coefficient6/13 |67|7|0.3340278121|0.3752735502|

The unseen improvement is0.1254764312; full-domain deployed CE changes
0.4976130705 to0.3653399982. Both reference and CUDA paths cross at67 after
seven actual scores each; transport and installation pass. The terminal
identities retain historical crossings after the base changes, and the full
constructor class remains UNRESOLVED.

Across these two fixed c2 tapes, mean deployed unseen CE changes0.5802183897
to0.5258452698. The per-case effects have opposite signs. This is a descriptive
two-case mean, not a population power ordering or the unfinished matrix mean.
The retained strong posterior controls and all old outcomes remain included.

## 3. Execution and independent checks

Worker2444 exits normally under its16GiB/two-hour cap. It was attached to
the job before resumption and peaks at15,047,073,792 bytes. The completed
source checks64 exact pre-target posterior forecasts,748 actual CUDA and
748 binary64 phases,248 native likelihood commit tapes and118 fresh scores.
The reader independently rechecks six model scores and both fresh paths,
plus all24 old B6 scores, four old decisions and16 strong-control scores.
It confirms bitwise equality of both candidate readout forms to the old run.

Worker6920 also exits normally, with peak15,034,691,584 bytes under the same
cap,64 exact posterior forecasts,748 CUDA/binary64 phases per path,248 commit
tapes and14 fresh scores. The two-case totals are128 forecasts,1,496 phases
per path,496 commit tapes and132 fresh scores. The same-source reader now
checks12 new scores and four fresh paths, plus the unchanged24 old B6 scores,
four old decisions and16 strong-control scores.

The [earlier conditional prediction](../../theory/proofs/TIGHTER_BOUND_DEPLOYMENT_TRADEOFF.md)
already fixed paired cursor119 and both risk envelopes before a completed
new outcome was available. It also fixed cursor67 for seed17. Both actual
cursors and all four unseen/full-domain CE values lie inside the prior
envelopes. This verifies their premises on these executed cases; it does
not turn predictions for the two c4 cases into outcomes.

The third worker30700 starts at2026-09-20 18:30:54 UTC under the same parent
14264 and is verified live afterward. Continue the registered order. Do not
restart, change coefficients, rerun controls or infer future success from
these rows. Use the reader in the immutable execution checkout with `--partial`
until all remaining attempts are terminal.
The separate n16 recovery worker2660 runs concurrently from75e4f93, as
recorded in its launch evidence. No exclusive-device timing claim is made.
