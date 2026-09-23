# Complete n64 causal learning with three physical realizations

Status (2026-09-23): **ALL SIX JOBS COMPLETE_MODEL; ALL RETAINED READERS PASS.**
The [registered matrix](BAND_MODEL_PROTOCOL.md) runs at
`45b40b463f40644ff7a5c06b67200677e8c7d9ac`, with production unchanged from
`d600dba`. Every job exits zero within the original16-GiB/two-hour envelope,
without timeout or memory-limit termination. All jobs are terminal. The
[248842-byte journal](../../evidence/minimal/FP_BAND_MODEL_A1.json) retains
every result and its source, PID and bounded-job identity; no worker is rerun.

The positive result is complete learning over2^63 latent assignments with
all2016 native count coordinates, ordinary causal ingress and actual AMP
continuations. The comparison also rejects an efficiency-win interpretation
for carry-free on these tapes: both existing controls complete, and projected
AMP uses substantially fewer floating words and arena bytes. This is a
declared bounded-width input law, not an all-pair or dense-graph result.

## Causal execution and independent checks

Each seed has126 adjacent-edge training observations and250 shuffled
radius-two evaluation observations. Learning continues after every forecast.
Each of the six runs commits all376 events and seals with no pending target,
failed phase or unpublished local commit. Every pre-target native forecast
equals the independent exact joint posterior. That control uses vertex-prefix
base9 inference, checks all counts and supplies no Runtime/GPU answer.

Across the matrix,2256 native posterior checks and6774 complete CUDA phase
checks pass. Primitive traces contain2851739 floating words, including
695013 half words. The full-frame auditors check every sealed record,
its padding and owned extent. The standalone retained-data reader recomputes
all1500 four-word evaluation readouts and all twelve native score controls:

    python -X utf8 -B scripts/run_band_model.py --read evidence/minimal/FP_BAND_MODEL_A1.json

Both exact controls make376 predictions and276448 vertex transitions per
run, with zero assignment enumeration. The large latent cardinality does
not imply exponential work on this declared width-two law.

## Predictive results

The124 ordered distance-two pairs were absent from initial training.
Their reverse orientation may already have appeared during evaluation.
Expected cross-entropy is against the hidden teacher's known noisy-label
probabilities, with binary64 logarithms. AMP scores use exact normalization
of the stored masses; raw division-word scores and exact Brier enclosures
remain in the journal.

| Seed | Exact joint posterior | Global AMP | Projected AMP | Carry-free AMP | Independent-pair ablation |
|---|---:|---:|---:|---:|---:|
|0|0.3871848232|0.3871819121|0.3871829524|0.3871847557|0.5607479822|
|1|0.3902449657|0.3902406153|0.3902457748|0.3902460663|0.5900966433|

All three reproduce the same native joint inference. Their small score
differences arise from the numerical realization, not better inference than
the exact joint control. The pair method is only a correlation ablation.
The exact joint control and both existing physical realizations are the
strong comparisons; no baseline was weakened to make carry-free succeed.

Full250-query-domain reference CE is0.3672226916 and0.3785038592 for the
two seeds. Corresponding carry-free CE is0.3672229118 and0.3785043823.
These are two fixed, exposed tapes, not a population test. The
[predictable score-transfer proof](../../theory/proofs/PREDICTABLE_SCORE_TRANSFER.md)
separates calibrated expected regret from individual-tape scores and later
completion selection. No statistical superiority follows from a small
negative rounded-minus-reference score difference.

## Actual resources

The following counts cover all phases, not just a selected final query.
Host peaks include the exact control and auditors. Concurrent CPU research
and this audit-heavy harness preclude an isolated throughput interpretation.

| Seed | Mode | Primitive floating words | Half words | Largest phase outputs | Arena bytes consumed | Whole-job peak bytes |
|---|---|---:|---:|---:|---:|---:|
|0|Global|578212|74532|3686|4652776|8118587392|
|0|Projected|55720|1560|1094|472840|7597096960|
|0|Carry-free|852575|281685|4247|6847680|8342597632|
|1|Global|543076|76344|3486|4371688|8078934016|
|1|Projected|35488|1176|502|310984|7575289856|
|1|Carry-free|786668|259716|3941|6320424|8277856256|

Carry-free additionally owns3264928 pinned table/coefficient bytes per run.
Its maximum spans are317/283, term counts470/436 and packed bit envelopes
20352/18176. The observed join maximum is32, within the label-independent
[resource upper](../../theory/proofs/BAND_MODEL_RESOURCE_BOUND.md).
The registered allowances and numerical tolerances never change.

All packed peaks lie between4884873681 and4888055705 bytes, under8 GiB.
The1129 complete4-MiB frames in every run remain fully allocated and
charged. Occupied compressed payload totals range from2530836 to7919156
bytes and reconstruct130879573 to240299336 legacy bytes. Compression does
not turn the occupied payload into the paid frame size. The largest occupied
record is47515 bytes, below its4194304-byte frame.

This experiment supplies no carry-free resource dominance: it uses more
floating work than global as well as projected on both seeds, and its host
peaks are larger. Its uniform precision theorem remains valid, while actual
resource usefulness depends on the competing realization and input law.
The later [direct-partition upper](../../theory/proofs/DIRECT_INTEGER_PARTITION_READOUT.md)
is separate research, not a replacement worker or a retroactive result in
this matrix. Its host integer inference must be paid in any future comparison.

## Decision class and remaining claims

The initial complete indexed program is the deployment throughout. The empty
Compiler policy makes zero class decisions, invokes no construction search,
spends no alpha and installs no candidate. COMPLETE_MODEL here means the
declared finite causal stream and all required numerical/resource/evidence
checks completed. No CERTIFIED_COMPLETE optimization claim was issued.

Foundation R4 and ERC-1 stay fixed. These results establish the two registered
tapes and their three physical executions; they do not establish architecture
discovery, dense/all-pair task feasibility, competitive next-token modeling,
an optimal decoder or a full indexed release. Do not repeat these terminal
jobs without a substantive new question.
