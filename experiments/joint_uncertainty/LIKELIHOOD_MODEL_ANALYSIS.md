# Independent analysis of the n8 likelihood matrix

The reader is `analyze_likelihood_model.py`. It executes no Runtime or GPU
worker. It analyzes the corrected86083a0 journal, preserves the earlier
90f3883 auditor failure, and reuses the original strong posterior controls.

## Reproduction and source separation

Keep an immutable analysis checkout at `F:\FP-likelihood-model-audit`, from
the commit introducing this reader. Its imported model/audit dependencies
must still match86083a0; the reader checks that condition and its own clean
committed file. Main may then advance without changing either the running
worker or the analysis source.

From that analysis checkout, while the matrix is live:

```powershell
python -B experiments/joint_uncertainty/analyze_likelihood_model.py --journal F:\FP-likelihood-model-v2-run\evidence\minimal\FP_LIKELIHOOD_MODEL_EXPERIMENT.json --partial
```

Omit `--partial` after the journal becomes terminal. A stopped auditor
failure is a terminal outcome, not a successful four-case matrix. The output
records the distinct execution and analysis sources. The default journal
path is the canonical file in the current checkout; an initial copied
prefix does not automatically acquire later worker results.

## What the reader verifies

* Original registration equality, fixed attempt order, retained failure,
  completed-job identity, attachment, exit/timeout status, memory bounds,
  and matching device/build metadata.
* A sealed candidate uses the registered native graph. The full constructor
  class remains UNRESOLVED; a claimed complete-class certificate is rejected.
* Every evaluation context has exactly one baseline readout and, when a
  candidate exists, one candidate readout at the matching ordinary cursor.
  Binary32 words are decoded independently to exact rationals. Proper
  stored-mass probabilities and raw floating divisions remain distinct.
* The reference posterior is reconstructed in bit-tuple world order. Exact
  Brier intervals use an independently expanded variance/calibration formula;
  expected CE and probability gaps use binary64 reference calculations.
  All four retained controls are checked without reexecuting their workers.
* When both identities were admitted, each original linear-factor/grid16
  wealth path is reconstructed using exact log enclosures and the independent
  exact log verifier. An install cannot precede paired crossing. Paired
  crossing without installation remains a possible reported outcome.
* Candidate and deployed metrics use their actual distinct information cuts.
  Deployment switches on the first query at or after the reported install
  cursor; the candidate's earlier scores are not credited to deployment.

An EXECUTED worker can still report HALTED_UNRESOLVED. Such a stream has no
complete model score. FAILED workers receive no imputed scores or phase
counts, even if their incomplete reports contain other plausible fields.

The completed worker already ran independent full CUDA and binary64 phase
replays. This reader checks and summarizes those source-bound results; it
does not pretend that the small mass-word journal contains the complete
raw gradient/operation tapes for another full phase replay. Source, lineage,
alpha and installation transport authority remain with the owned execution.

The compact fresh summary omits per-identity path labels. If exactly one
identity was admitted, the reader returns `UNRESOLVED_FROM_MINIMAL_RECORD`
for its fresh reconstruction instead of inventing that label. It may still
check separately retained model scores. This does not erase the original
worker's own checks or supply a new completeness claim.

## Development validation

`python -B experiments/joint_uncertainty/analyze_likelihood_model.py --self-test`
checks twelve adversarial word/readout/freshness/job/class cases, accepts
paired crossing without installation, and refuses promotion of the retained
failed job. Its initial run independently checks sixteen retained control
scores and reports zero completed model rows. The
[first completed corrected worker](LIKELIHOOD_MODEL_RESULTS.md) now also passes
the successful-model branch: six reconstructed scores, one paired decision
and748 worker-verified phases per path. Its reader runs from unchanged
b85b39d against the live86083a0 journal. No synthetic model worker is
published as validation evidence.
