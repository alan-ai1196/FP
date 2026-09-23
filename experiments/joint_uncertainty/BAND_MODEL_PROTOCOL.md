# Complete n64 learning at bounded interaction width

Status (2026-09-23): **REGISTERED BEFORE ACTUAL MODEL EXECUTION.**

Execution at45b40b4 is now terminal: all six jobs complete and all retained
readers pass. See [the source-bound results](BAND_MODEL_RESULTS.md).
The declaration below is the registration used by those jobs; no inputs
or limits were changed during execution.

## Question and fixed data

Can the owned carry-free decoder complete a predictive learning task with
2^63 latent assignments, preserving the same exact adaptive joint posterior
and every causal event, within the existing model resource envelope? Compare
its actual numerical and resource behavior with both existing global and
projected AMP. This is a controlled width-two data distribution, not the
earlier all-pair evaluation distribution or a population generalization claim.
The [uniform bound](../../theory/proofs/BAND_MODEL_RESOURCE_BOUND.md) separates
latent population size from table width before any model outcome is seen.

Fix exactly `(64, iid-band2, 0)` and `(64, iid-band2, 1)` in that order. Use
`band_model.py`: independent uniform hidden bits, known target flip probability
1/10, and the same hidden/noise/order seed formulas as the earlier IID model.
Take two observations of each of the63 adjacent pairs, in lexicographic
edge order, for126 training events. Evaluate every ordered nonloop pair
with distance<=2 once, in the seeded shuffled order, for250 more events.
Targets are independently noisy conditional on the hidden bits. Learning
continues after every forecast throughout evaluation. The evaluation input
law is deliberately declared; no observed edge or label is removed to make
a solver fit.

The124 ordered distance-two pairs were absent from initial training. Report
their expected cross-entropy/Brier and the corresponding scores on all250
evaluation queries. The reverse orientation can already have appeared
during evaluation; "unseen" means absent from initial training, not never
observed at the current information cut. CE uses binary64 logarithms and
the true known-noise conditional probabilities; Brier uses exact rational
per-query grid enclosures. No incomplete prefix receives a model score.

The complete indexed native program is initially deployed, with uniform
Gamma and unit/rate-one simplex U. Every source and target enters ordinary
Runtime ingress. All2016 signed count positions, including zero off-band
positions, remain; the full categorical pair interface is unchanged. No
profile, architecture search, candidate selection, persistence or installation
is invoked. The empty Compiler policy can seal a completed stream and
contains zero constructor decisions. It issues no optimality certificate.

## Strong controls and fixed execution matrix

For each seed run **global, projected, carry-free**, six fresh jobs total.
All three share G/Gamma/U, data/order, source interface, host/device/retention
limits, numerical tolerances and empty policy. The carry-free registration
changes its exact/physical realization, explicit work identities and paid
wide table extent. Both legacy implementations keep their current larger
table/arithmetic allowances; neither control is weakened.

An independent base9 vertex-prefix algorithm checks every reference forecast
against the full known-noise joint posterior, including training. It is
not world enumeration and uses no packed-digit or bucket-elimination code.
It receives the actual past labels and never supplies Runtime or GPU operands.
Small comparisons with full assignment sums and the uniform geometry audit
are retained in `FP_BAND_MODEL_CONTROL.json` before actual execution.

The exact joint control's initial-training-unseen expected CE is
0.3871848232032782 and0.3902449656579961 for seeds0/1. A known-noise
independent-pair posterior yields0.560747982223021 and0.5900966433075647.
The latter is a correlation ablation, not the strongest baseline. The
joint posterior is the exact quality control; all native forecasts must
equal it. An AMP score difference is rounding error, not better inference.
These deterministic controls have been inspected at registration; no IID
population inference or blind model-selection claim is made.

## Common whole-resource contract

Keep the prior model envelope:16-GiB Windows job,7200000-ms deadline,
8-GiB packed retained payload,10^15 work units per role,256-MiB device arena,
512-MiB allocator cap,4-MiB complete phase frames,65536 output cells per
phase and32768-bit reference arithmetic. State/probability tolerances remain
1/100 and1/1000; activation/normalizer caps remain8/18. Use the existing
byte-preserving zlib evidence encoding. Do not discard full history or
shrink a paid frame to its compressed occupied payload.

Carry-free allowance: J4096/C1024/A16384/S396/I32768;3264928 actual pinned
table/coefficient bytes. For every label history on this stream, the proved
upper bounds are join32/live832/arithmetic13373,24064 packed bits and6785
prediction outputs. The global physical output upper bound is17770. These
bounds rule out the corresponding class refusals, not host/time/retention
or implementation failure. Whole-job commitment includes the independent
oracle and final full-frame/phase auditors. No cap changes after an outcome.

## Execution, readers and outcomes

The component gate passes all19 actual jobs atd600dba. Production stays
unchanged from that source. `scripts/run_band_model.py --attempt 1` must
launch only after all inputs are committed. Each fresh worker is attached
to its bounded Windows job before resumption. Keep HEAD and execution
inputs fixed until every launched worker is terminal. No numerical kernel,
owner endpoint or solver is substituted by the harness.

The worker checks every pre-target reference forecast, every native
observation/commit, actual complete plans, primitive RNE words, fresh
endpoints, all complete phase frames and resource ownership. Carry-free
model readers reconstruct the paid-table plans independently. The shared
reader's global/projected/Gray controls and altered coefficient/endpoint/
trace probes pass; the old completed n16 artifact still reads unchanged.

Retain each complete result, honest UNRESOLVED prefix, timeout, memory
termination and audit failure in `FP_BAND_MODEL_A1.json`. Continue the
declared matrix after numerical/resource refusal; stop on an unexpected
execution/audit failure. Do not retry silently, overwrite an attempt or
score incomplete prefixes. Keep only the250 four-word evaluation readouts,
compact audits/metrics and source/job identity, not datasets, weights, caches
or complete frame dumps. A separate `--read PATH` recomputes scores from
these words and the fixed exact controls without another GPU execution.

Completion would establish these two declared model tapes, including
correlation-sensitive prediction and owned continuation. It would not prove
uniform resource dominance, isolated throughput gains, architecture discovery,
all-pair task feasibility or the full indexed release. Foundation/ERC-1 remain
frozen; any actual conformance failure stays evidence to investigate.
