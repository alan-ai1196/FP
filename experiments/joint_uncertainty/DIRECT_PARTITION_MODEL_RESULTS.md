# Direct-partition n64 model outcomes

Status (2026-09-23): **BOTH SEEDS COMPLETE_MODEL; ALL RETAINED READERS PASS.**

The [registration](DIRECT_PARTITION_MODEL_PROTOCOL.md) keeps the original
two tapes and whole-resource limits. Production remains unchanged from the
owned gate at42802f6. A1's seed0 job at4c4a057 completes all376 events and
1129 CUDA phases. The parent then incorrectly indexes its `JobRun` dataclass
as a dictionary and stops before launching seed1. This is a collection
failure after completed physical execution, not a model refusal.

The original [A1 journal](../../evidence/minimal/FP_DIRECT_PARTITION_MODEL_A1.json)
retains both facts, including the traceback. The
[independent retained reader](../../evidence/minimal/FP_DIRECT_PARTITION_MODEL_A1_READER.json)
recomputes all250 evaluation readouts and both exact score controls without
a device rerun. It rejects nine altered job/readout/matrix records and
tests the corrected collector with the actual `JobRun` type. The separately
declared [A2](../../evidence/minimal/FP_DIRECT_PARTITION_MODEL_A2.json) executes
only the missing seed1 ate395c55 and completes. Its independent reader also
passes. No completed job was rerun; both are terminal. Production is identical
across the two jobs. A1 keeps its original collection-failure status.

Together the two runs check752 native forecasts,2258 actual phases/full
frames,24064 primitive floating words/1504 half casts and500 retained
evaluation readouts. The empty Compiler policy issues no class decisions.

## Completed tapes and retained strong controls

All four realizations keep2016 counts and learn the same exact joint
posterior over2^63 latent assignments. The three controls below are their
completed source-bound jobs at45b40b4; they have not been rerun or weakened.
Every direct forecast equals the independent vertex-prefix posterior; it
performs276448 vertex transitions and no world enumeration. The complete
native history, all primitive RNE words, full frames and padding pass.

| Seed | Realization | Primitive floating words | Half casts | Consumed arena bytes | Paid integer table bytes | Packed peak bytes | Whole-job peak bytes |
|---|---|---:|---:|---:|---:|---:|---:|
|0|Global|578212|74532|4652776|0|4884940044|8118587392|
|0|Projected|55720|1560|472840|0|4884940069|7597096960|
|0|Carry-free|852575|281685|6847680|3264928|4888055705|8342597632|
|0|Direct partitions|12032|752|123336|211356|4885002698|7555497984|
|1|Global|543076|76344|4371688|0|4884873681|8078934016|
|1|Projected|35488|1176|310984|0|4884873706|7575289856|
|1|Carry-free|786668|259716|6320424|3264928|4887989622|8277856256|
|1|Direct partitions|12032|752|123336|211356|4884936705|7555358720|

Direct partitions use fewer floating words and less consumed arena extent
on both tapes. Their packed peak is slightly **higher** than both global and
projected. Host exact inference, history and auditors remain costs; this is
not uniform memory dominance, isolated throughput or GPU integer inference.
The measured whole-job peak stays below the original16-GiB cap, without
timeout or memory termination. The largest compressed payloads are4350/4137
bytes, but all2258 complete4-MiB frames remain paid across the two jobs.
Occupied payload totals4834145 bytes and expands to282203345 legacy bytes;
none of that changes frame rent. Actual maximum partition-bit envelopes
are1332/1196 under the registered1564 upper, and both runs use join32.

| Seed | Exact unseen CE | Direct AMP unseen CE | Exact all-query CE | Direct AMP all-query CE |
|---|---:|---:|---:|---:|
|0|0.387184823203|0.387187542826|0.367222691554|0.367224114773|
|1|0.390244965658|0.390248037510|0.378503859153|0.378505205466|

These are rounding effects on exposed tapes, not evidence of better inference or population risk.
The exact joint posterior remains the strongest quality control; the
independent-pair result is only a correlation ablation.

## Exact posterior discrepancy and the numerical tradeoff

The [retained-risk audit](../../evidence/minimal/FP_RETAINED_PARTITION_RISK.json)
reconstructs all500 native evaluation forecasts with the independent
posterior and checks2000 saved forecasts across the four realizations.
It uses exact fractions and96-bit outward grids to enclose reference-to-
proper-AMP KL and conditional Brier excess; no GPU execution is repeated.
The [segment-integral proof](../../theory/proofs/PREDICTABLE_SCORE_TRANSFER.md#7-exact-discrepancy-intervals-from-retained-hardware-readouts)
avoids cancellation in tiny logarithmic differences. All proper probabilities lie
in[1/10,9/10]. The table gives outward decimal uppers on all250 queries.

| Realization | Maximum probability error, seed0 / seed1 | Mean KL upper, seed0 / seed1 |
|---|---:|---:|
|Global|4.56308e-5 /1.17665e-4|1.47912e-10 /7.65266e-10|
|Projected|4.60002e-5 /7.26732e-5|9.72109e-11 /9.26750e-11|
|Carry-free|1.70150e-5 /2.58789e-5|3.01006e-11 /4.86902e-11|
|Direct partitions|1.46525e-4 /1.09740e-4|3.51241e-10 /3.56162e-10|

The exact intervals separate direct KL **above projected and carry-free on
both seeds**, for both all-query and initially unseen groups. Direct is above
global on seed0 and below it on seed1. Its maximum probability errors remain
below the proved0.000195701 bound. Fewer operations and a better uniform
upper have not supplied pointwise numerical dominance over the controls.
This is a measured computational/numerical tradeoff within the same tolerance.

These path averages do not estimate population risk. Fixed-hidden-teacher
CE gaps include a signed first-order term; KL against the native posterior
is nonnegative. In particular global seed1 has a lower fixed-teacher CE
but a higher posterior KL than direct. Do not rank inference quality from
those tiny fixed-teacher score differences.

The empty Compiler policy spends no alpha and performs no installation.
The declared two-seed execution/comparison is closed. Every job is terminal;
do not rerun it. Full indexed release and claims outside these tapes remain
separate obligations. Foundation R4 and ERC-1 are unchanged.
