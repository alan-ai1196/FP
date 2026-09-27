# Ordinary next-token research: entry decision

Status: **RESEARCH PRIORITY, 2026-09-26; VERIFIED TEXT DATA AND PASSIVE CAUSAL
SOURCES AVAILABLE; NO NEW MODEL RESULT**. Foundation and ERC-1 stay frozen.
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

## First model-score boundary

The first text comparison may train one preregistered native G/Gamma/U from
its own initialization as the incumbent, with no graph replacement during
that run. This is an empirical test of that supplied learner, not an adaptive
Compiler selection or task-resource-forced structure claim. Completing an
unused token candidate-installation path is therefore not a prerequisite for
this narrower study. Persistence and install reachability remain mandatory
when an actual experiment selects/replaces a deployed graph; they are not
inferred from an empirical text loss. Foundation XIV–XV are unchanged.

The existing owned training trajectory, every internal reference/AMP phase,
resource limits and complete retained state remain required. A frozen-model
validation report additionally needs a tested, paid, read-only Runtime path
that preserves the original reporting contexts and cannot update the learner
or feed held-out labels into construction. That path is not implemented by
calling a passive predictor on a snapshot. Until it exists, ordinary training
prequential loss is at most a separate diagnostic, not a held-out result.
Compare such an online diagnostic only with genuinely prequential baselines;
a randomly trained baseline that has seen later targets is a different claim.

Score the native and actual AMP trajectories separately. For the physical
readout, the probability is the target's stored positive mass m divided by
the sum S of all stored label masses. The rounded division by stored Z is
not generally normalized. The existing pre-target readout envelope encloses
S in [L,U]; after the owned target-mass execution, a reporting decoder can
enclose negative log probability by [log(L/m),log(U/m)], intersected with
the known nonnegative loss domain. Bind the operands to that same actual
forecast and use funded numerical bounds; this formula by itself supplies
no score, ownership, freshness or installation authority. The A1 resource
attempt remains unscored under its original registration.

Choose the first affordable model/data budget from actual execution evidence,
then preregister the graph, initializer, update rule, physical schedule,
training/reporting identities, tuning allowance, baselines and stop rules.
Do not shrink the alphabet or use weak baselines to hide an unfavorable
result. The currently exposed validation file is development data, not newly
fresh evidence; deterministic unread data alone provide no stochastic law.

## Initial study direction

Use ordinary public text, not another generated relation/parity distribution.
The initial WikiText-2/raw-byte proposal was provisional. Inspection then
found and verified an existing **FineWeb-Edu180M-token training/2M-token
validation corpus**, with pinned file identities and the full50,257 GPT-2
vocabulary. The [data/source entry](CORPUS_AND_CAUSAL_SOURCES.md) is now the
preferred substrate. Corpus provenance is separated from verified file
identity; historical test files/results supply no new fresh authority.

The passive input contract fixes all lag/token atoms and distinct missing-
history padding, retains EOT without an implicit reset, and proves current/
future targets cannot change past-only inputs. It does not supply a model
or owned Runtime ingress. Use the same declared tokenization and context
conventions for compared learners; no hidden linguistic features or
held-out vocabulary selection. Choose context and training budgets from
measured feasibility before preregistration. Do not shrink the task solely
to make FP pass.

Include a tuned smoothed n-gram control and a competitive causal Transformer
trained from scratch on the same tokens/splits, in addition to diagnostic
unigram/SUM-only controls. Modified Kneser–Ney has an established implementation
in [KenLM](https://github.com/kpu/kenlm); verify its token vocabulary, boundary
and normalization conventions if used. Unigram or deliberately undertrained
neural baselines alone are insufficient. Give baselines their normal useful
optimizers and a declared validation tuning allowance. Match the comparison
being claimed—data, context, parameter/storage and training/inference cost—
and disclose residual differences instead of claiming every coordinate is
simultaneously equal. Perplexities on different tokenizations or corpus
constructions cannot be treated as the same prediction space.

Two baseline details need explicit treatment before implementation. KenLM's
estimator adds its own sentence/unknown symbols and treats newlines as
boundaries. Its author also warns that assigning the full unknown probability
to multiple distinct unseen words does not give a normalized comparison.
Map GPT-2 IDs injectively, keep EOT as the declared ordinary token, and define
the probability over the entire50,257-token alphabet, including unseen IDs,
before scoring. Do not silently introduce extra document resets or count
several unseen IDs as the same event. See the
[KenLM estimation documentation](https://kheafield.com/code/kenlm/estimation/)
and [estimator options](https://github.com/kpu/kenlm/blob/master/lm/builder/lmplz_main.cc).

Likewise, the standard nanoGPT training loop samples random contiguous blocks,
and its causal attention sees only preceding positions available in each
block. It is not automatically the same information schedule as chronological
rolling-context FP. Keep a competitive Transformer and its normal optimizer,
but state the training exposure and scored-context lengths exactly; do not
claim matched context or prequential exposure from a shared block_size alone.
The source references are the
[training loop](https://github.com/karpathy/nanoGPT/blob/master/train.py)
and [causal model](https://github.com/karpathy/nanoGPT/blob/master/model.py).
Its default output width is50,304. Use the declared50,257 categories or mask
the extra logits during both training and reporting; unused padding rows must
not take probability mass from the common target alphabet.
These are implementation conventions to audit, not a fixed model-size choice
or a claim that this particular repository is the strongest current baseline.

## Next executable boundary

The [actual Runtime source control](OWNED_SOURCE_CONTROL.md) now establishes
ordinary and retained-profile semantics for a literal native token graph,
including explicit PAD and original source delays. This is the control the
compact full-vocabulary backend must refine. Preserve every internal event
relation and the complete normalized readout when integrating batch/AMP;
the small control does not replace the target task or grant a new release.

The [actual RTX3090 schedule gate](AMP_RESULTS.md) also completes. It
computes its own complete text-unit successors and matches the CPU physical
schedule, while native masters can differ. A physical counterexample shows
that exact current prediction equality can conceal future-visible learning
loss. The immediate issue is now an owned complete state/error relation
inside ReferenceCompilerRuntime, not another passive cost study or static
variant. The real data/model/baseline research direction remains unchanged.

The [bounded CPU jobs](REFERENCE_HOST_RESULTS.md) now complete, including
one actual-training/full-vocabulary/context512 update at0.442 s enclosure
plus commit and226 MiB peak job commitment. That supports proceeding with
the reference implementation. Owned text/Runtime and AMP integration are
next; no further passive benchmark sweep is needed. No model loss is scored.

The [batched complete-unit reference](BATCHED_REFERENCE.md) now preserves
the exact native endpoints with explicit array enclosures and immutable
packed masters. Its full-vocabulary audit passes. The immediate execution
step is a committed whole-process feasibility audit, then owned source/Runtime
integration and AMP; further passive static examples are not the priority.

The [source-clock refinement](SOURCE_AND_LEARNER_CLOCKS.md) now supports
explicit retained-example contexts and frozen new-file scoring without
identifying source position with optimizer time. General pending units
retain every actual source/target record; the original target-only recipe
requires the contiguous subclass. This supplies the necessary mathematical
interface, but Runtime must still bind corpus/observation IDs, roles and
actual acquisition rather than accepting caller-made windows as authority.

The [sound enclosure solver](EXACT_COMMITS_WITH_ENCLOSURES.md) now advances
exact native committed states without materializing every pending rational:
it retains the complete unit origin and source/target records, and resolves only unique
grid cells. A full-vocabulary512-event audit matches every resulting master
against a separate exact control. Ambiguous cells remain unresolved with
the exact decoder retained. The efficient funded implementation and actual
AMP bridge, rather than further static variants, are the next execution work.

The [complete passive token learner](NATIVE_TOKEN_LEARNER.md) now supplies
an explicit native G/Gamma/U: indexed lag/token SUMs with declared embedding
ties, an arbitrary positive core DAG and the untied readout. It retains
every parameter/gradient, its causal context and shared update clocks.
Literal small-program trajectories pass, as does synthetic execution at
the full vocabulary/context512. This has not selected a useful topology or
initializer and grants no owned or floating execution authority. The actual
numerical/resource lowering and model/baseline protocol are next.

The [complete positive readout refinement](../../theory/proofs/NATIVE_POSITIVE_READOUT.md)
now removes one execution obstacle without changing the native optimizer.
It retains all final SUM slots and pending gradients using exact common
offsets and target corrections, and passes an independent dense control at
all50,257 labels. This is a passive mathematical component: it supplies
neither useful language features nor an owned or floating training path.
Do not assume exact reassociation preserves an old AMP schedule. Use the
result where it makes complete native learning affordable, then continue
with the actual text core and comparisons rather than deepening static cases.

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
