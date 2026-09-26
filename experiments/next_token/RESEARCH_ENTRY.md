# Ordinary next-token research: entry decision

Status: **RESEARCH PRIORITY, 2026-09-26; no new language experiment or model
result is registered by this document.** Foundation and ERC-1 stay frozen.
The user explicitly requested a reassessment when rational-feature/precision
work reached a clean stopping point. The decision is to move on now.

## Evidence for the decision

The [rational-feature gate](../../theory/proofs/OWNED_RATIONAL_FEATURE_AMP.md#10-a4-completion-and-the-research-stopping-point)
has a successful execution for every original case, with its revisions and
three failures preserved. Its motivating questions now have answers:
denominator-independent native range is possible; materialized exact
gradients still impose a precision lower; redundant verifier intermediates
can be removed without erasing state; the owned device execution reaches
that boundary and passes its declared binding/failure obligations.

More variants of the relation task would not determine whether FP learns a
useful representation on ordinary text. The earlier
[scoped Reference release](../../theory/proofs/REFERENCE_RELEASE_SCOPE.md)
and [target release](../../theory/proofs/CUDA_RELEASE_SCOPE.md) already permit
registered experiments inside their tested boundaries. An unrestricted
indexed Compiler release is not inferred from the new gate, and the new
language representation receives no borrowed bridge authority.

[Research history, Trial 1C](../../RESEARCH_HISTORY.md#3-trial-1c-raw-width-was-not-the-missing-answer)
records FP CE4.2794413 versus dense4.1196805 and a width increase that worsened
CE. Its interpretation was a structure/information problem. Another raw-K
sweep, duplicated alternatives or an added repulsion regularizer would
repeat that failed direction. Those historical values are not results on a
new corpus or directly comparable with a new tokenization.

Repository inspection finds no current ordinary-text experiment directory
alongside the active relation/uncertainty studies. The legacy R4.2 package
has vocabulary/readout utilities, but its existence does not establish a
current native Compiler language-model path. Do not silently rehabilitate
that historical framework to obtain a convenient training loop.

## Question and claim boundary

The immediate scientific question is whether a completely specified native
positive SUM/PRODUCT learner can learn useful conditional text structure
from ordinary teacher-forced next-token loss under declared resources.
Report loss and cost against competitive baselines, including failure.
If structure is supplied by initialization, say so; if a constructor proposes
structure, expose the actual class, acquired information and search outcome.

An empirical advantage or a selected graph is not a proof that useful
structure is forced in the complete resource-constrained optimum. That
stronger Foundation claim still requires its exact decision class and a
valid comparison bound. A finite syntax search also does not certify all
trained values or all future continuations. Report UNRESOLVED when needed.

## Initial study direction

Use ordinary public text, not another generated relation/parity distribution.
The first corpus candidate is **WikiText-2 raw**, with official train,
validation and test splits. Its raw version retains tokens before vocabulary
unknown-word replacement; the publisher provides a character-level variant
and dataset/license metadata. Pin the actual source revision and preserve
the selected row/byte construction exactly. This candidate still needs an
audited manifest and split/boundary protocol before execution.
[Publisher dataset card](https://huggingface.co/datasets/Salesforce/wikitext).

Prefer an explicit UTF-8 byte alphabet initially: no pretrained tokenizer,
hidden linguistic features or vocabulary chosen using held-out labels.
Treat document/row boundaries, initial context, evaluated positions and
context resets as part of the information contract. Teacher-forced past
targets become legal later context; the current or future target cannot
enter a forecast or structural proposal prematurely. Choose the context
and training budgets from measured feasibility before preregistration.
Do not shrink the task solely to make FP pass.

Include a tuned smoothed n-gram control and a competitive causal Transformer
trained from scratch on the same bytes/splits, in addition to diagnostic
unigram/SUM-only controls. Modified Kneser–Ney has an established implementation
in [KenLM](https://github.com/kpu/kenlm); verify its byte vocabulary, boundary
and normalization conventions if used. Unigram or deliberately undertrained
neural baselines alone are insufficient. Give baselines their normal useful
optimizers and a declared validation tuning allowance. Match the comparison
being claimed—data, context, parameter/storage and training/inference cost—
and disclose residual differences instead of claiming every coordinate is
simultaneously equal. Byte metrics cannot be compared to published word or
subword perplexities as if they used the same prediction space.

## Next executable boundary

First recover the actual native G/Gamma/U and complete causal state for the
proposed text learner, using existing grammar/optimizer operations wherever
they suffice. The current registered projected SGD can have explicit commit
grids; the joint relation's count/Bayes refinement cannot simply be renamed
as a general language learner. No hidden attention/GRU, signed activation,
softmax feature extractor or externally selected topology may appear inside
the FP path without its declared native meaning. Strong non-FP baselines
remain free to use their ordinary architectures.

Then establish a small exact/float64 reference and actual AMP equivalence
check for that precise representation, including all parameters, gradients,
optimizer state, context queues and source identities. A fast lowering must
preserve the native computation or explicitly decline the bridge; sampled
word agreement alone cannot certify an entire training trajectory. Charge
construction, updates, inference, audit reads and retained evidence under
their actual owners. Exact-reference cost is a measured constraint, not a
reason to silently substitute a different learner.

The data-ingress and throughput study should determine a concrete affordable
run, after which commit the corpus manifest, baseline implementations,
training/search class, seeds, tuning policy, held-out protocol, resource caps
and stop rules before model outcomes are inspected. Store minimal aggregate
evidence and source identities; keep corpus caches and weights outside Git.
Do not launch another relation study as a prerequisite unless this work
exposes a correctness question that genuinely requires it.
