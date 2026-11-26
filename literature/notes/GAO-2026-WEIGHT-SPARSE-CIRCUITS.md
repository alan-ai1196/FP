# Weight-sparse transformers have interpretable circuits

## Identity, edition and actual coverage

- Leo Gao, Achyuta Rajaram, Jacob Coxon, Soham V. Govande, Bowen Baker and Dan Mossing. **ICML 2026 final**, PMLR 306, pp. 33483–33513. [Publisher record](https://proceedings.mlr.press/v306/gao26w.html), [final PDF](https://raw.githubusercontent.com/mlresearch/v306/main/assets/gao26w/gao26w.pdf), [publisher metadata](https://raw.githubusercontent.com/mlresearch/v306/gh-pages/_posts/2026-09-29-gao26w.md). PMLR metadata dates publication September 29, 2026. The July 6–11 conference dates are a different event. The publisher author field expands the last author's name to Daniel P. Mossing.
- Official OpenAI work, introduced in the [November 13, 2025 research article](https://openai.com/index/understanding-neural-networks-through-sparse-circuits/). Related preprint: [arXiv:2511.13653v1](https://arxiv.org/abs/2511.13653v1), November 17, 2025. The checked arXiv history lists only v1. The later conference edition is the edition fully read here.
- **Pro-B full reading, November 26, 2026:** all 31 final pages, §§1–6, Appendices A–G, formulas, all 16 numbered footnotes, 41 figures, two tables, acknowledgments, impact statement, author contributions and 69 printed bibliography entries. All figure-bearing pages were visually inspected, alongside the complete extracted text. The reference count is not a count of distinct papers independently read.
- Final PDF SHA-256: `52d28359bb36f2b95c64a44aab91082b9ef6e614d77520dda4fc6e2d3d28d4f9`. Ignored local materials: `literature/corpus/pisf_prior_art/GAO-2025-WEIGHT-SPARSE/`, including the final PDF/text/page renders, preprint PDF/complete source, edition comparison and scoped release inspection.
- The preprint source and PDF were compared with the final edition. Both have 41 figures and two tables, but the texts are not identical. The final adds the training-code release and impact statement, removes a main-text support-bit footnote and some discussion, shortens several passages, and has 69 rather than 71 printed reference entries. The principal appendix content and graphic objects match in the bounded comparison. This does **not** assign a second full-read badge to the preprint.
- Scoped official-code inspection used [openai/circuit_sparsity at dbf1fe0d27b76c19e10d2a715f28c2e5da535e08](https://github.com/openai/circuit_sparsity/tree/dbf1fe0d27b76c19e10d2a715f28c2e5da535e08). A source assistant read the minimal training entry and relevant model paths. Pro-B rechecked the important projection, auxiliary-table and release-availability passages. No training, checkpoint evaluation, GPU benchmark or general code audit was run.

The current official paper is used under the project's official-source working-premise policy. Complete reading, the authors' empirical evidence, a limited static code inspection and independent verification are separate statuses. No theorem audit, formal proof or experimental reproduction is claimed.

## Question and supplied mechanism

The paper asks whether training a transformer with very few nonzero connections makes its computations easier to understand. It trains the model itself under a weight-sparsity constraint, then searches for small task circuits. This differs from fitting an interpretable activation basis to an already trained dense model. Its central evidence concerns selected simple Python next-token behaviors, not an identified minimal predictive state or a theorem that training discovers semantic modules. [§§1–2, pp. 1–4]

The backbone is close to a GPT-2 decoder. Most experiments use eight layers, model width 2048, context 256 and attention-head dimension 16. RMSNorm gives zero a privileged meaning and permits normalization weights to be folded into adjacent weights. Embedding and unembedding matrices are untied. Some models use a learned attention-sink denominator bias. Most experiments omit positional embeddings, while some earlier experiments use read-only absolute positional channels. Appendix A explicitly warns that experiment settings differ, so numbers across different plots are not directly interchangeable. [A.1, p. 14]

### Three distinct sparsities

| Quantity | Operational meaning | What it does not measure |
|---|---|---|
| Weight \(L_0\) | Number of nonzero weights in the specified sparse components | Total tensor capacity, physical memory bits or realized hardware work |
| Activation sparsity | AbsTopK retains a fraction of current activations at designated locations, usually one quarter | A fixed count independent of width, or direct sparsity of the complete residual stream |
| Task circuit size | Number of nonzero scalar-weight edges retained in a task circuit, aggregated by geometric mean over 20 tasks | Number of mask variables, global semantic completeness or certified minimality |

An edge is a nonzero scalar connection. Nodes include neurons, attention channels and residual read/write locations. For example, a neuron reading one residual channel and writing another gives three nodes and two edges. The pruning objective penalizes node masks, but the principal reported interpretability metric counts **edges**. [§2, p. 3, §2.2, A.5]

After each dense optimizer update, the method keeps the largest-magnitude weights within each eligible matrix and sets the others to zero. Schematically,

\[
\widetilde W_{t+1}=\operatorname{AdamWStep}(W_t),\qquad
W_{t+1}=\operatorname{TopK}_{k_t}(|\widetilde W_{t+1}|)
                 \odot\widetilde W_{t+1}.
\]

Here the TopK factor denotes a binary support mask. This is repeated projection, not a permanently frozen graph. Gradients and Adam moments remain dense, allowing previously zeroed coordinates to return. The target \(L_0\) is normally annealed over the first half of training, or 80% for the largest sparse models. The learning rate includes a multiplier proportional to \(1/\sqrt{L_0}\), producing the “sharkfin” schedule. The reported optimizer uses \(\beta_1=.9\), \(\beta_2=.95\), decay .1 and epsilon .1, with learning-rate sweeps, short warmup and gradient RMS clipping. These are reported experimental choices, not universal optimization prescriptions. [§2.1, A.2, Figures 11, 13–30]

Activation AbsTopK is applied to normalized reads, MLP neurons, Q/K/V separately and block writes. It is input dependent. Weight sparsity also increases residual-activation kurtosis in the measured models, but residual entries are rarely exactly zero. The appendix retains kurtosis as the measured proxy. [A.1, Figures 10 and 12]

**An auxiliary dense component remains:** the model can add a \(d_{\rm vocab}\times d_{\rm vocab}\) bigram table directly to output logits, indexed by the last token. Its intended purpose is to reserve sparse circuit capacity for computations beyond simple bigram frequencies. With vocabulary 2048 this is 4,194,304 entries. The paper therefore does not describe an implementation in which every computational parameter is sparse. The final text does not specify an identical accounting convention for this auxiliary term across every plotted run. The scoped release check below retains that boundary. [A.1, Figure 24]

The generated training corpus has a 10-billion-token component of simpler repetitive Python and a 25-billion-token broader component, produced using GPT-4-base and GPT-4o-base. Some smaller experiments use only the simpler component. The authors explain their simplicity rationale but do not ablate that data-mixture decision. A 2048-token BPE vocabulary and special task-tokenization choices also affect the examples. [A.6–A.7, p. 21]

## What the interpretability experiment measures

The 20 hand-constructed binary next-token tasks include quote closure, bracket depth, variable type, loop syntax, indentation and related Python distinctions. The tasks and target alternatives are listed in Table 1. The default target task cross entropy is **0.15**. This is neither a 15% error rate nor a percentage of recovered cross entropy. [§2.2, Table 1, A.5]

The pruner places a Boolean mask at every node position, shared across all prompts and token positions. A removed node is replaced with its mean activation over the pretraining distribution. A learned parameter clamped to \([-1,1]\) determines each Boolean mask through a Heaviside forward operation. Backpropagation uses a biased sigmoid-gradient surrogate. Training minimizes task cross entropy plus a coefficient times the number of retained mask nodes. After training, a binary search chooses the mask size meeting the requested loss threshold. The authors note that this final size can differ substantially from the training result. [A.5, p. 20]

The evaluation also includes **16 LBFGS steps fitting scale and shift of final logits**. The authors explicitly leave the general principled status of this calibration unclear. Hyperparameters are tuned separately for each model–task combination using 32 CARBS rounds with eight parallel jobs, or 256 pruning runs. Each batch contains 64 positive/negative task pairs, up to 256 tokens per sequence. Consequently:

- The reported small circuit is the result of a substantial search and calibration procedure.
- “Smallest” or “minimal” in the experimental description does not establish global combinatorial optimality.
- The objective's node penalty and the reported edge count must remain distinct. Q and K are masked separately and often consume two nodes per pair, which the authors themselves suggest tying in future work.
- Learned pruning substantially outperforms the tested attribution baseline, but this is a comparison of procedures under the stated task distribution. [Figure 31]

### Main measured comparisons

| Result | Supported reading | Necessary qualification |
|---|---|---|
| Roughly 16-fold smaller task circuits, Figure 2 | Sparse and dense models with comparable pretraining loss are compared across target task losses | Loss matching is not parameter, training-FLOP or latency matching |
| Wider model at fixed sparse \(L_0\), Figure 3 | Both pretraining loss and measured circuit size improve in the tested range | Ambient capacity grows while active-weight budget is held fixed |
| Lower \(L_0\) at fixed ambient capacity | More compact circuits trade against language-model capability | It is movement along the measured frontier, not an unconditional gain |
| More training tokens, A.2 | Usually lower language-model loss but larger task circuits | The authors generally did not observe frontier improvement at this experimental margin |
| Increasing activation sparsity, Figure 37 | Moderate sparsity helps, excessive sparsity becomes Pareto dominated | Activation fraction is a separate control from weight \(L_0\) |
| Inverse pruning, Figure 32 | Removing the discovered circuit impairs the original model, unlike comparable random removals | Evidence is under the specified ablation, not a universal causal necessity theorem |

The individual-token loss correlation is .93 between a sparse and a dense model, compared with .94 between two differently seeded dense models. This is useful behavioral evidence, but does not identify the mechanisms of either model. [Figure 33]

## Mechanistic examples and their selection

The authors manually interpret three task circuits across two models selected for apparent simplicity. Each circuit takes approximately a researcher-day, including removal of extra nodes and activation-patching checks. The descriptions are therefore not fully automatic interpretations of arbitrary circuits. [§3.2, pp. 5–7]

### Quote closure

The displayed circuit has 12 nodes and nine edges. Two layer-0 MLP neurons detect an opening quote and its type. A layer-10 attention head uses one QK channel to find the quote and one value channel to retrieve its type, allowing the output to select the matching closing quote. The two neurons and two attention channels have 41 global connections, nine used by this circuit. Some associated channels remain understandable on pretraining data, but the particularly monosemantic Figure 39 channel is explicitly cherry-picked. This does not establish global monosemanticity. Appendix F.1 separately checks this circuit's constant-query simplification: constant replacement has a loss hit of \(2.6\times10^{-5}\) nats/token, compared with \(1.47\times10^{-4}\) for zero ablation. [§3.2.1, Figures 4 and 39, F.1]

### Bracket depth

The simplified display has seven nodes and four edges. Bracket detectors feed a nearly uniform attention average, and a later attention operation uses a sink to implement a threshold. This mechanism predicts two nontrivial failures: brackets in irrelevant comments can perturb the answer, and sufficiently long lists dilute the earlier signal. The paper reports both failures in the unpruned model. It also reports that some predictions generalize to a similarly capable dense model. These are behavioral tests of the proposed mechanism, not proof of a unique underlying algorithm. [§3.2.2, Figures 5 and 8]

The simplicity depends on additional manual operations. The six principal channels have 283 global edges. The simplified diagram elides 11 layer-3 attention channels and 48 layer-7 MLP neurons, adding 1,217 more global edges. Appendix F.2 explains removal and rescaling of apparently redundant components, operations unavailable to the automatic pruner. The authors warn that this could conceal superposition.

Two specific substitutions support their local redundancy interpretation. A linear replacement of the final MLP incurs a pretraining loss hit of \(5.8\times10^{-5}\) nats/token, compared with \(2.69\times10^{-4}\) for zero ablation. Replacing the layer-3 write to residual channel 1249 by a linear function of its layer-2 counterpart gives \(7\times10^{-4}\), compared with \(4\times10^{-3}\) for zero ablation. The substitutions are approximate, not exact functional identities. [F.2, pp. 25–26, Figure 36]

### Variable type

For a fixed variable name, one attention head copies the name into its initialization token and another retrieves the value using the name as a key. The displayed mechanism uses four QK and three value channels, with 100 global edges. Not all nodes are monosemantic. The result is an informative partial explanation, not a complete task-independent tracing of the model. [§3.2.3, Figure 6]

## Bridges to an existing dense model

The exploratory bridge construction jointly trains a sparse model and maps between dense and sparse residual representations. The encoder is linear followed by AbsTopK, and the decoder is linear. In addition to ordinary language-model loss, it uses bidirectional normalized MSE at each layer and two families of output KL penalties. If \(f_i\) maps dense to sparse and \(g_i\) sparse to dense, the reconstruction terms compare \(f_i(h_i^d)\) with \(h_i^s\), and \(g_i(h_i^s)\) with \(h_i^d\). The KL terms ask a remaining sparse suffix to accept a mapped dense prefix, and a remaining dense suffix to accept a mapped sparse prefix. [§3.3, A.3, Figure 7]

The important restriction is that these hybrids have **one switch** between dense and sparse. The authors would ideally train all \(2^L\) combinations, but use the single-switch subset as a first-order approximation. The “all paths” motivation is not a result establishing interchangeability under arbitrary repeated switches.

In two selected four-layer examples, the authors identify a sparse read channel and map its counterfactual activation difference through the corresponding decoder row to perturb the dense model. Bridge training is at pre-RMSNorm residual locations, while selected nodes are post-RMSNorm reads, so they also apply an RMS-scale correction. Steering strength varies from zero to one. One intervention increases the probability of a single closing quote in a double-quote context. The other moves a `return True` context toward the corresponding `while True` activation and increases colon probability. [A.4, Figures 9, 40–41]

**Visible caption qualification:** Figure 9's right caption reverses the return/while direction relative to §3.3 and the plot's “toward while True” axis. The preceding description follows the main text and axis. This local direction mismatch does not invalidate the broader bridge experiment.

These experiments support selected transferred causal edits. They do not establish a globally faithful circuit isomorphism, a certified causal abstraction, or an interpretation of a frontier dense model.

## Faithfulness, binarization and computational cost

Appendix E explicitly states that the circuits do not meet full causal-scrubbing standards. Two requirements would be stronger than the demonstrated evidence:

1. Values assigned the same semantic interpretation should be interchangeable.
2. Nodes described as irrelevant should be replaceable by arbitrary values from their pretraining distribution.

The first holds poorly in general, and the second is stronger than replacing every removed node by its mean. Mean ablation can remove variation on which the original model relies or create distributional artifacts. Inverse pruning reduces the concern but does not eliminate it. The authors also explain why paired-prompt patching alone can miss a necessary variable-name carrier when it is constant within a pair but varies across pairs. [Appendix E, p. 25]

Appendix C tests a soft route toward two learned activation levels, with temperature annealing and several threshold initializations. Binarization often damages task performance, indicating that activation magnitude can matter beyond a Boolean semantic label. Larger ambient capacity at fixed \(L_0\) improves this proxy, but increasing \(L_0\) at fixed capacity also improves it, unlike the compact-circuit metric. These measures cannot be collapsed into one universal “more sparsity means more interpretability” result. [Appendix C, Figure 34]

Appendix D compares the magnitude-projection method with a modified HardConcrete approach on toy language modeling. The modifications include scaled-Bernoulli initialization and a floor on the sparsity penalty. The tested smooth method has somewhat worse language-model loss at comparable empirical \(L_0\), and the authors did not obtain a pruning improvement. This is not a general impossibility result for smooth sparsity or a direct human-interpretability comparison. [Appendix D, Figure 35]

The authors estimate **100–1000 times as much training and inference compute** as comparable-capability dense models. This is a stated cost assessment, not an independently measured universal hardware bound. Unstructured sparsity disrupts dense tile movement and Tensor Core utilization. The system appendix discusses CUDA-core sparse kernels at very low nonzero fractions, limited 2:4 sparsity acceleration, TopK overhead, dense weight-gradient selection, dense optimizer moments and the dense-to-sparse annealing phase. It gives plausible bottlenecks and possible improvements, not a complete hardware impossibility theorem. No end-to-end speed or memory result was reproduced here. [§5, Appendix B]

## What the official release permits one to claim

The inspected [December 11, 2025 pin](https://github.com/openai/circuit_sparsity/commit/dbf1fe0d27b76c19e10d2a715f28c2e5da535e08) is the commit adding `train.py`. It therefore contains a minimal training entry as well as inference and visualization. A stale “inference-only” phrase inside a fallback-kernel module does not describe the entire repository at this revision.

The relevant primary files are [train.py](https://github.com/openai/circuit_sparsity/blob/dbf1fe0d27b76c19e10d2a715f28c2e5da535e08/circuit_sparsity/train.py), [gpt.py](https://github.com/openai/circuit_sparsity/blob/dbf1fe0d27b76c19e10d2a715f28c2e5da535e08/circuit_sparsity/inference/gpt.py) and [README](https://github.com/openai/circuit_sparsity/blob/dbf1fe0d27b76c19e10d2a715f28c2e5da535e08/README.md). Line numbers below refer to this fixed pin.

| Release observation | Supported scope |
|---|---|
| `train.py` 235–278 returns random token IDs | The loader is explicitly a mock that must be replaced with real data |
| `train.py` 577–624 computes next-token CE, updates weights, reapplies top-k and decays eligible parameters | An actual minimal training loop exists, but the sole entry does not implement bridge training |
| `train.py` 84–186 recalculates per-tensor magnitude support | Connections can regrow, and activation AbsTopK is a separate operation |
| Example width 1024, eight layers, head dimension 16, context 256 | The example is not the appendix's most common width-2048 experimental configuration |
| Example `afrac=.25`, `pfrac=.25`, both expansion factors 4 | Activation retention is one quarter, but ordinary weight matrices target 1/64 and token embedding/unembedding 1/16 at the end of the schedule |
| README's exact training-hyperparameter link is `[todo]` | The pinned tree is not a complete per-figure reproduction manifest |
| Model and visualization assets use external blob URLs | Their release is documented, but every remote asset was not downloaded or validated here |

There are additional narrow implementation-correspondence qualifications. The script uses Adam plus manual decoupled matrix decay, unconditionally normalizes gradients by their RMS, and only performs the projection's zeroing on two-dimensional tensors. It zero-initializes the positional embedding but sets `requires_grad` on the module rather than explicitly freezing the weight parameter. These observations prevent claiming operation-by-operation identity with every Appendix A run. They are not evidence that the reported paper experiments used this exact illustrative code path or that those experiments are invalid.

**Bigram accounting:** `train.py` 107–109 explicitly skips the dense bigram table during projection, and 623 skips it during decay. In contrast, the `numel` sums at 493–494 and the model parameter counter include an enabled learned bigram table. Those are tensor-element counts, not an actual aggregate nonzero count. Visualization code reads externally produced `L0` and `L0_non_embed` metrics without supplying their generation rule in the inspected tree. Consequently, the released example's dense auxiliary table is outside its sparse projection budget, but Figure 3's exact per-run counting convention is not established by this check.

The inspected tree lacks a complete real-corpus pipeline, per-experiment manifest, bridge-training entry, CARBS pruning reproduction pipeline and the production custom CUDA kernels. This bounded inventory establishes release scope. It does not audit all external assets or authorize a claim that no other implementation exists. The official findings remain working premises, and no independent reproduction badge is assigned.

## Research value and FP boundary

This paper provides an unusually concrete empirical example of **training-induced computational structure**: restricting connections and increasing available ambient coordinates yields smaller, more understandable task circuits on the tested distribution. Its strongest practical contribution is the combination of a structural training constraint, explicit circuit-search procedure, mechanistic predictions and admitted failures of full causal faithfulness.

For future comparisons, the source supports keeping separate axes for ambient parameter capacity, sparse nonzero budget, input-dependent activation budget, circuit-search cost, pretraining quality, held-out task behavior and measured hardware cost. Compactness of a selected graph is insufficient by itself to establish a sufficient predictive state, minimal memory or efficient computation.

No FP theorem or architectural prescription is imported here. The transformer graph, optimizer state, attention context, precision and task distribution are supplied rather than inferred as a finite physical state space. A claimed FP connection would still require explicit state objects, update semantics, resource accounting, assumptions and a falsifiable consequence. The present result stands as an independent architecture and interpretability study.
