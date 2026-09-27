# Standard Transformer comparison path

Status: **IMPLEMENTED; CPU FLOAT64 CONTROL PASS; NO CORPUS OR DEVICE RESULT**.
This is preparation for the ordinary-text comparison, outside FP's native
grammar and Runtime. It selects neither a model size nor a training budget.
It adds no prerequisite to the original live FP resource attempt.

## Architecture and output space

The adapter uses the unmodified nanoGPT model source at
[`3adf61e154c3fe3fca428ad6bc3818b27a3b8291`](https://github.com/karpathy/nanoGPT/blob/3adf61e154c3fe3fca428ad6bc3818b27a3b8291/model.py),
vendored with its MIT license. It retains causal self-attention, learned
positions, pre-normalized residual blocks, GELU feed-forward layers, tied
token/output weights, the upstream initialization and ordinary AdamW groups.
Construction starts from the registered random seed; no pretrained weights
or historical FP baseline checkpoints are loaded.

`Spec` requires explicit vocabulary, context, depth, heads, width, dropout and
bias. There is no default experimental size or width sweep. At vocabulary V,
there are V+1 input embeddings: the V real tokens and one input-only PAD row
for an empty file prefix. The output projection uses only the first V tied
rows, so training and reporting both normalize over exactly V labels. The PAD
row is trainable through its input use, but receives no output probability.
The historical full GPT-2 alphabet remains V=50,257.

## Training and reporting contexts

`training_batch` provides ordinary shifted contiguous blocks of length L.
A block starting at s>=0 has inputs x_s,...,x_(s+L-1) and targets
x_(s+1),...,x_(s+L). The causal model sees one through L real preceding
tokens across these positions. Start=-1 includes the first target: inputs
PAD,x_0,...,x_(L-2), targets x_0,...,x_(L-1). No block leaves the supplied
training view. EOT is an ordinary ID and never triggers a reset.

The trial must register block sampling, data view, repetitions, optimizer,
learning-rate schedule, clipping, AMP/scaler recipe, tuning allowance and
stop rules. Sampling these blocks repeatedly is ordinary offline training;
it is not the chronological FP prequential information schedule. A shared
maximum context alone does not make all training contexts or exposures equal.
The baseline should use its useful optimizer and adequate training, not be
deliberately undertrained to match an unfavorable FP implementation detail.
Any comparison must disclose its actual data, context and cost coordinates.

`report` is frozen teacher-forced scoring. Target t receives exactly
x_max(0,t-L),...,x_(t-1); t=0 receives the single PAD input. Each window uses
local positions 0,...,length-1. Variable-length prefixes are grouped only
with windows of the same length. There is no artificial reset at batching
boundaries or EOT, and a new reporting file/view starts without training-tail
context. Every target is scored once, including the initial short contexts.
No optimizer call is made; dropout is disabled. A report is not an online
training diagnostic or evidence of a fresh stochastic stream.

The model produces the actual V logits in the declared execution precision.
Reporting converts those logits to float64 and computes
`logsumexp(logits)-target_logit` over the entire alphabet. This is the proper
softmax score of those logits, with ordinary float64 numerical error; it is
not an exact FP enclosure or a claim of native/AMP trajectory equivalence.
GPU training/reporting must use a registered mixed-precision recipe when
that later experiment is selected. This CPU control supplies no GPU result.

## Control and stopping point

`scripts/audit_text_transformer_baseline.py --write` checks:

- Adapter logits, loss and every parameter gradient against the unmodified
  upstream network with its input-only row excluded before normalization.
- Trainable PAD input, the full target alphabet, 36 causal attention prefixes,
  19 past-only reporting windows and inaccessible current/future token reads.
- Identical frozen means under four reporting batch sizes, unchanged model
  parameters, file/EOT conventions and an ordinary AdamW update.
- Seven full-50,257-label normalized forecasts, plus invalid block/token
  refusals. All model arithmetic in these controls is float64 on CPU.

Minimal evidence is `evidence/minimal/FP_TEXT_TRANSFORMER_BASELINE_CPU.json`.
No corpus file is opened, model-quality score recorded, CUDA context created
or model-size/tuning budget selected. This completes the adapter control;
do not turn it into an architecture or precision catalog. A tuned smoothed
n-gram and diagnostic controls remain part of the planned comparison. This
standard Transformer implementation does not by itself establish that any
chosen training run is a competitive baseline.

After the actual FP feasibility/reporting results, preregister the concrete
text run and its comparison budgets, then train and score the real models.
Dataset identities, exposure policy, process/resource measurements and
minimal result artifacts belong to that trial, not to a synthetic control.
