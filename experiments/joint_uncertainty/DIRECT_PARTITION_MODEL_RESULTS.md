# Direct-partition n64 model outcomes

Status (2026-09-23): **SEED0 COMPLETE_MODEL; RETAINED READER PASS; SEED1 UNEXECUTED.**

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
declared A2 will execute only the missing seed1 under the original limits.

## Completed seed0 and retained strong controls

All four realizations keep2016 counts and learn the same exact joint
posterior over2^63 latent assignments. The three controls below are their
completed source-bound jobs at45b40b4; they have not been rerun or weakened.
Every direct forecast equals the independent vertex-prefix posterior; it
performs276448 vertex transitions and no world enumeration. The complete
native history, all primitive RNE words, full frames and padding pass.

| Realization | Primitive floating words | Half casts | Consumed arena bytes | Paid integer table bytes | Packed peak bytes | Whole-job peak bytes |
|---|---:|---:|---:|---:|---:|---:|
|Global|578212|74532|4652776|0|4884940044|8118587392|
|Projected|55720|1560|472840|0|4884940069|7597096960|
|Carry-free|852575|281685|6847680|3264928|4888055705|8342597632|
|Direct partitions|12032|752|123336|211356|4885002698|7555497984|

Direct partitions use fewer floating words and less consumed arena extent
on this tape. Their packed peak is slightly **higher** than both global and
projected. Host exact inference, history and auditors remain costs; this is
not uniform memory dominance, isolated throughput or GPU integer inference.
The measured whole-job peak stays below the original16-GiB cap, without
timeout or memory termination. The largest compressed payload is4350 bytes,
but all1129 complete4-MiB frames remain paid. Occupied payload totals2431470
bytes and expands to141123859 legacy bytes; none of that changes frame rent.

Initial-training-unseen expected CE is0.3871875428258331 for direct AMP
versus exact0.3871848232032782. On all250 evaluation queries it is
0.3672241147727849 versus exact0.3672226915539738. These are rounding effects
on an exposed tape, not evidence of better inference or population risk.
The exact joint posterior remains the strongest quality control; the
independent-pair result is only a correlation ablation.

The empty Compiler policy issues zero constructor decisions, spends no
alpha and performs no installation. Seed1 and the full two-seed direct
comparison remain open. No full indexed release follows from seed0.
