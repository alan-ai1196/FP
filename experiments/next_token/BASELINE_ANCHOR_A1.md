# Ordinary-text baseline anchor A1

Status: **PREREGISTERED; NO OUTCOME AT REGISTRATION, 2026-09-29**.

The FP execution and model audits have reached clear stopping points, but
have not established an affordable trained-text budget. Keeping the already
qualified baseline adapters idle until that budget is known adds an unnecessary
dependency. This study obtains an actual language-learning and cost reference
on ordinary text while the FP budget remains unresolved. It does not select
an FP graph, compare an untrained FP fixture against trained models, or claim
matched costs/data exposures for an FP run that has not occurred.

Use this single bounded study to inform the FP experiment. After its original
outcome, return to the native model/budget decision; do not deepen another
baseline architecture or smoothing catalog. Foundation/ERC and relation closure
remain unchanged. This protocol supersedes the baseline-adapter documents'
suggestion to wait for FP feasibility before training any real-text baseline.

## Data and claim

Use the already verified FineWeb-Edu/GPT-2 asset in
[CORPUS_AND_CAUSAL_SOURCES.md](CORPUS_AND_CAUSAL_SOURCES.md):

| Role | Original file/token interval | Use |
| --- | --- | --- |
| Training | train.bin [0,1,048,576) | Common unique data available to every model |
| Tuning | val.bin [0,4,096) | Registered hyperparameter/checkpoint selection |
| Development report | val.bin [4,096,16,384) | Frozen selected-model score |

All distributions use the full 50,257-token target alphabet. EOT is ordinary;
no implicit sentence reset is added at it. Each file starts from its declared
PAD/BOS convention, and the reporting suffix retains the original preceding
validation context across position 4,096. It is not scored as a new file.
The selected view lengths are a baseline pilot budget, not a restriction
asserted sufficient for language modeling or chosen to make FP pass.

Validation was previously exposed and remains development data. The suffix
is excluded from this trial's tuning rule, but is not claimed fresh or
statistically independent. Do not open historical test/confirmation files.
Report descriptive finite-tape mean NLL in nats. There is no population,
significance, installation or complete-Compiler claim. Corpus files and token
arrays stay outside Git; actual read prefixes have byte identities in the
minimal result. No ceremonial rehash of the unused full training file is due.

## Models and selection fixed before scores

**Modified Kneser–Ney:** use the already built, pinned upstream estimator and
unquantized trie in [baselines/NGRAM.md](baselines/NGRAM.md). Train unpruned
orders 3 and 5, with automatic discounts, ordinary interpolation and no
discount fallback. The declared continuous training view is one estimator
sentence. Its structural BOS/EOS are excluded from the real target alphabet.
Normalize the actual stored scores over all real labels using the qualified
reporter; distribute the single unknown bucket among unseen IDs. Select the
lower tuning mean, breaking an exact tie toward order 3. Only that selected
model receives the full-prefix report. Subtract the matched tuning-prefix
loss sum to obtain the suffix mean, with ordinary float64 summation error.

KenLM's explicit all-label normalization is a correctness implementation,
not a competitive inference-throughput claim. Record estimator, trie-builder
and reporter times separately. It must not manufacture a throughput advantage
for FP by attributing this adapter overhead to all possible n-gram evaluation.

**Transformer:** use the pinned unmodified nanoGPT model through the qualified
[adapter](baselines/TRANSFORMER.md), trained from scratch. Fix context 256,
four blocks, width 128, four attention heads, dropout 0.1, no biases, and the
adapter's tied token/output embeddings with one input-only PAD row. This is
one supplied standard architecture, not a width/menu search. Initialization,
dropout and block-sampling seed are 29317. Each of two independent runs uses
one maximum learning rate in {3e-4,1e-3}; ordinary AdamW has weight decay 0.1,
betas (0.9,0.95), and gradient-norm clipping at 1.0.

Each run makes 8,192 update attempts with eight length-256 shifted blocks per
attempt: 16,777,216 target exposures, sixteen times the unique data count.
Starts are sampled uniformly with replacement from [-1,N-257], including
the PAD-start block and never crossing the training view. This is offline
repeated-block training, not FP's chronological prequential schedule. Warm up
linearly for 256 attempts, then use cosine decay to 0.1 times the maximum rate
at the last attempt. No early stopping shortens the registered training.

Use FP32 master parameters/AdamW state, CUDA FP16 autocast, normal dynamic
GradScaler, and no TF32. Overflow skips are counted; more than one percent
of attempts skipped is a failed numerical execution. Otherwise report both
attempted and successful updates. Evaluate the tuning prefix, with dropout
disabled and rolling original contexts, after attempts 512,1024,2048,4096,8192.
Within a run, retain the lowest tuning-loss checkpoint; ties keep the earlier
checkpoint. Across the two rates, select the lower tuning loss; ties choose
3e-4. Load exactly that retained state for the final frozen development report.
The report must reproduce its tuning-prefix mean within 1e-6 nats.

The output logits are the actual FP16-autocast values, normalized over the
entire alphabet in float64. Standard CUDA kernels are used without a bitwise
determinism promise. Log training-window losses, tuning losses and all selected
steps. These curves expose inadequate learning or ongoing improvement; the
registration does not assert convergence or that this is the strongest possible
Transformer. The ordinary optimizer, tuning and repeated exposures are intended
to avoid a deliberately undertrained comparison.

**Unigram diagnostic:** fit exact training counts, tune additive smoothing
alpha in {1/16,1,16} on the same prefix, then freeze and score the same suffix.
This is a diagnostic alongside the two stronger families, not their replacement.

## Execution, evidence and stop rules

Run `python -B scripts/run_text_baseline_anchor_a1.py` once, after committing
this protocol, runner and CPU controls. Original sequence: n-gram/unigram,
Transformer 3e-4, Transformer 1e-3, selected Transformer report. No concurrent
FP or baseline training job is part of the measurement. Existing terminal
FP journals are untouched and never replayed.

Each worker starts suspended and is attached to its Windows job before its
first instruction. Host commitment is capped at 16 GiB per process and job.
The n-gram worker allows two simultaneous processes for the parent and its
external tool; other workers allow one. No breakaway is enabled. The existing
job helper still defaults to one, and FP's HostResourceContract is unchanged.
The baseline launcher independently records OS job/process peaks, CPU time,
wall time, PID and process creation identity. These are baseline resource
measurements, not borrowed FP/ERC certificates.

The n-gram job has 30 minutes total; each individual tool call has 10 minutes.
Each Transformer training job has two hours; frozen reporting has 15 minutes.
PyTorch peak reserved memory must stay within a **monitored** 22-GiB allowance;
this is not an OS-enforced device-memory cap. Never reset peak counters. The
device must be the registered RTX 3090, UUID
GPU-229f6784-2b41-5313-3f21-e30f26b0bf5c, capability 8.6.

Numerical failure, timeout, source/identity mismatch or resource refusal leaves
the original journal terminal and the study incomplete/UNRESOLVED. Do not retry
the job, increase a cap or substitute a smaller alphabet after observing it.
Any later changed experiment requires a new explicit question and registration.
No score may be invented for an unfinished model or absent FP learner.

`FP_TEXT_BASELINE_ANCHOR_A1.json` retains the original source commit, selected
view identities, aggregate training/tuning/report losses, selections, numerical
events and measured costs. Selected models and current worker checkpoints stay
under `F:\experiment\FP_next_token_baselines\text_anchor_a1`, outside Git, with
artifact identities for frozen reporting. Temporary text, report tapes and ARPA
intermediates are removed after a successful n-gram report. No full logits,
gradient histories, datasets or trained weights enter the repository.

The prelaunch CPU control checks original-context suffix reporting against an
independent float64 traversal, unchanged frozen parameters, the complete rate
schedules, and actual one-/two-process Windows job behavior. Its small-model
and OS checks supply no real-text or actual GPU result. There is no additional
synthetic-control branch to complete before this original launch.
