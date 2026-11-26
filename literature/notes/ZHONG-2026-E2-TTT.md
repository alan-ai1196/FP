# Rethinking Expressivity and Efficiency in Test-Time Training

## Identity and actual coverage

- Zeyun Zhong, Joya Chen, Manuel Martin, Frederik Diederichs, Juergen Gall and Juergen Beyerer. [arXiv:2608.21308v3](https://arxiv.org/abs/2608.21308v3), revised November 23, 2026, 09:57:01 UTC. [Versioned PDF](https://arxiv.org/pdf/2608.21308v3) and [complete source](https://arxiv.org/src/2608.21308v3). Earlier versions were submitted August 21 and August 26. The current record identifies v3 as the NeurIPS 2026 camera-ready author version. The title is also present in the [official NeurIPS 2026 event list](https://neurips.cc/Downloads/2026). A distinct proceedings PDF was not matched here.
- **Pro-B full reading, November 26, 2026:** all 23 pages, §§1–7, Appendices A.1–A.5 and B.1–B.7, Proposition 3.1 and its derivation, Algorithm 1, all five figures, 15 tables, acknowledgments, impact/limitations and all 68 printed references. All 17 active TeX files, including the table inputs and notation preamble, were covered. Actual figures and selected mathematical/table layouts were visually inspected. References cited by the paper are not themselves marked read.
- PDF SHA-256: `5786afa9c9ba4d549aec297f167cf9c2304d4307e179c565dbb5a8a6f64b62e9`. Ignored source, text, renders and algebra support are under `literature/corpus/arxiv_frontier/2608.21308v3/`.
- Bounded independent work followed the finite-sum reindexing and the one- and two-token endpoints, identified a missing qualification in the appendix's ratio-sum discussion, and checked the reported comparisons against the actual tables. No whole-theorem certification, formal proof, training or benchmark reproduction was performed.
- Scoped author-code inspection used [zeyun-zhong/E2-TTT at 0d1da370c7e3cea1642ba3af0477b7601849a1be](https://github.com/zeyun-zhong/E2-TTT/tree/0d1da370c7e3cea1642ba3af0477b7601849a1be), a September 25 commit preceding the v3 manuscript. A source assistant inspected the relevant update/cache paths, configurations and release inventory. Pro-B rechecked the important source passages. Exact correspondence to every v3 experiment is not established. Code materials are ignored under `literature/corpus/pisf_prior_art/ZHONG-2026-E2-TTT/`.

## The distinction the method actually resolves

TTT stores context in the fast weights of an inner learner. The outer language-model objective learns slow parameters and the initialization/update machinery. The inner self-supervised objective changes the fast weights while processing a sequence, including at inference.

Three different choices must be kept separate: where gradients are evaluated, which optimizer recurrence is represented, and which state produces a token's output. The paper's Table 1 distinguishes them explicitly:

| Schedule | Gradient evaluation | Represented update | Output readout |
|---|---|---|---|
| Fully token-wise TTT | Previous token's weights | Per token | Newly updated token state |
| Mini-batch TTT | Batch-start weights | Per token | Newly updated token state |
| LaCT-style chunk TTT | Chunk-start weights | One aggregated chunk update | Chunk-start state |
| E²-TTT | Chunk-start weights | Per-token scalar dynamics, collapsed exactly at the endpoint | Chunk-start state |

E²-TTT preserves the temporal weighting induced by per-token learning rates, momentum and decay **after accepting frozen chunk-start gradient evaluation**. It does not parallelize arbitrary online gradients evaluated at freshly changing weights. It also does not restore token-wise updated readouts inside a chunk. These restrictions are stated in the abstract, method and limitations. [§§2–4, Table 1]

The word “expressivity” here concerns retaining those input-dependent update factors rather than replacing them with chunk averages. The paper does not establish a general strict hypothesis-class separation between every architecture named in the experiments.

## Exact endpoint algebra

Within a chunk of length \(C\), let \(W_0,M_0\) be the incoming fast weights and momentum. A symbol \(W\) can denote the whole collection of fast-weight tensors. For fixed keys and values,

\[
G_t=-\left.\nabla_W\mathcal L(f_W(k_t),v_t)\right|_{W=W_0},
\qquad
M_t=\beta_tM_{t-1}+\eta_tG_t,
\qquad
W_t=\gamma_tW_{t-1}+M_t.
\]

The scalars satisfy \(0<\beta_t,\gamma_t<1\), \(\eta_t>0\), and are predicted from the input independently of the evolving inner \((W,M)\). All \(G_t\) use the same \(W_0\). Those conditions permit parallel evaluation of the driving quantities. [Eq. 7, Proposition 3.1]

Define suffix products and a suffix ratio sum by

\[
\widetilde\beta_t=\prod_{i=t+1}^{C}\beta_i,
\qquad
\widetilde\gamma_t=\prod_{i=t+1}^{C}\gamma_i,
\qquad
R_t=\sum_{i=t}^{C}\frac{\widetilde\gamma_i}{\widetilde\beta_i},
\]

with empty products equal to one. Then

\[
M_C=\widetilde\beta_0M_0+
       \sum_{t=1}^{C}\underbrace{\eta_t\widetilde\beta_t}_{K_t^M}G_t,
\]

\[
W_C=\widetilde\gamma_0W_0+
       \widetilde\beta_0R_1M_0+
       \sum_{t=1}^{C}\underbrace{\eta_t\widetilde\beta_tR_t}_{K_t^W}G_t.
\]

The two kernels have different jobs. \(K^M\) measures how much a gradient remains in momentum at the boundary. \(K^W\) also sums the intervening occasions on which that momentum writes into weights, with later weight decay. The incoming momentum contributes separately through \(\widetilde\beta_0R_1\). Keeping the momentum endpoint therefore matters even though all within-chunk gradients were frozen. [§3.2, A.1–A.2, A.5]

The proof unrolls momentum, substitutes it into the weight recurrence, and exchanges the two finite sums. The coefficient of \(\eta_tG_t\) becomes

\[
\sum_{j=t}^{C}
  \left(\prod_{i=t+1}^{j}\beta_i\right)
  \left(\prod_{q=j+1}^{C}\gamma_q\right)
  =\widetilde\beta_tR_t.
\]

No state-dependent optimizer solve is hidden in this identity. The bounded independent check found no local algebraic problem in Proposition 3.1 or A.1–A.2. For example, at \(C=2\), the coefficient of \(G_1\) in \(W_2\) is \(\eta_1(\gamma_2+\beta_2)\), and the coefficient of incoming \(M_0\) is \(\beta_1(\gamma_2+\beta_2)\), as in direct unrolling.

### What endpoint equivalence does and does not imply

The implemented output for every token in the chunk is

\[
o_t=f_{W_0}(q_t),
\]

not \(f_{W_t}(q_t)\). Exact \((W_C,M_C)\) therefore does not imply exact token-wise output trajectories. Even \(C=1\) recovers the stated update while retaining a pre-update readout under this output rule. A token cannot influence a later token in its own chunk through this TTT state path. [Algorithm 1, §4]

Cross-chunk induction is valid when the compared systems use the same inputs, partition, initialization and boundary operations. Appendix B.1 applies **L2 normalization to fast-weight matrices after each chunk**. Applying the same normalization to two equal endpoints preserves equality, but the experimental trajectory includes this operation in addition to the displayed affine recurrence. Normalizing after every token would be a different reference system.

The authors report a 128-chunk FP32 comparison with \(C=512\), totaling 65,536 tokens, with relative endpoint deviations below \(2\times10^{-6}\). This is their numerical result. It was not rerun here and is not an exact-arithmetic proof of arbitrary implementation behavior. [§3.2, A.3]

### Parallel contractions and a local stability qualification

For each token let \(g_t=-\partial\mathcal L_t/\partial f_{W_0}(k_t)\). The two weighted weight-gradient sums reuse the same per-token backward intermediates and differ in scalar weighting. For the instantiated MLPs, the contractions can be performed per fast-weight tensor without materializing every token's full matrix gradient. The paper retains \(O(Cd^2)\) work for its schematic matrix model, with \(O(C)\) scalar scans. It avoids \(O(Cd^2)\) storage of an entire sequence of matrix states, not all token activations or all outer-training memory. A general black-box differentiable learner does not automatically inherit a universal one-GEMM overhead. [§3.2, A.4]

Appendix A.3's informal claim that small \(\gamma\) makes \(R_t=O(1)\) needs an additional ratio condition. With constant \(\beta=.01\), \(\gamma=.1\), the ratio sum is \(\sum_{j=0}^{C-t}10^j\), despite small \(\gamma\). A sufficient geometric condition would be a uniform \(\gamma_i/\beta_i\le q<1\). This is a qualification of the ratio-sum discussion, not a refutation of the endpoint formula.

The **actual update kernel has a simpler valid bound** for every admissible \(\beta,\gamma\), obtained directly from its positive-product expansion:

\[
0<K_t^W\le\eta_t(C-t+1)\le\eta_{\rm base}C,
\qquad
0<K_t^M\le\eta_t\le\eta_{\rm base}.
\]

This independent elementary deduction does not need a near-unit limit. A large \(R_t\) can be offset by small \(\widetilde\beta_t\). It also does not prove stable floating-point evaluation, uniformly bounded gradients or bounded infinite-horizon states. The paper's log-space computation and measured numerical agreement remain implementation evidence with their stated scope.

## Architecture and learned dynamics

The language model uses a Llama-style backbone with two parallel token-mixing branches: 512-token sliding-window attention, SWA, and E²-TTT. They share query/key/value projections and are fused by an input-dependent elementwise gate. The TTT path applies SiLU and L2 normalization to queries and keys. The local attention branch supplies the within-chunk interactions missing from the fast-weight readout. [§4, Figure 2]

The scalar heads are

\[
\eta_t=\eta_{\rm base}\sigma(a_\eta(x_t)),\qquad
\beta_t=\sigma(a_\beta(x_t))^{1/\tau},
\]

\[
\alpha_t=\alpha_{\rm base}\sigma(a_\alpha(x_t)),\qquad
\gamma_t=1-\eta_t\alpha_t.
\]

Defaults are \(\eta_{\rm base}=.01\), \(\alpha_{\rm base}=.1\), \(\tau=32\). Thus \(\gamma_t>.999\) in this default mathematical parameterization. The aggressive-small-\(\gamma\) regime discussed generically in A.3 is not reached under these defaults. The heads are trained by the outer language-model objective, not extra labels for desired forgetting or memory timescales. [§4, Table 7]

The GELU inner learner has two fast-weight matrices and the SwiGLU learner has three. Both include a residual connection and LayerNorm. The momentum contains corresponding tensors. Architecture and state dimensions are supplied in advance. The paper studies their learning and execution, not discovery of a finite sufficient state set.

## Empirical setup and evidence

The main E²-TTT language-model configurations use FineWeb-Edu, a 32K vocabulary, 24 layers, 512-token chunks and a 512-token attention window. The exact main training recipes differ from the shorthand “15B tokens at 2K”:

| Setting | 340M | 1.3B |
|---|---:|---:|
| Hidden width / heads | 1024 / 8 | 2048 / 16 |
| Sequence length | 2048 | 2240 |
| Effective batch / steps | 256 / 28,672 | 256 / 28,672 |
| Reported actual token budget | About 15B | About 16B |
| Reported H100 GPU-hours | 132 | 348 |

Appendix B.1 explicitly explains the approximate main-text labels. Likewise, “8 times the training context” uses the nominal 2K label. The actual reported 1.3B training length is 2240. [§5 setup, B.1, Table 7]

Some baseline rows marked with an asterisk are taken from HQLT rather than rerun. The other models are described as trained under matched data/optimization conditions using public implementations. HQLT uses the synchronous variant. The reported LaCT configuration uses Muon for its inner update. Titans and E2E-TTT have separate author reimplementations described below. These are distinct evidentiary levels, not one uniformly reproduced benchmark suite. [§5, B.2, B.5–B.6]

### Language modeling and retrieval have different best variants

At 1.3B, E²-TTT-MLP has WikiText perplexity 19.5, LAMBADA perplexity 15.3 and six-task zero-shot average 54.5%, compared with the strongest listed baseline average of 53.8%. These are modest general-task gains. The SwiGLU variant instead gives the strongest E²-TTT retrieval results. On the three real retrieval tasks truncated to 2K, it averages 43.6%, versus LaCT 36.7%, HQLT 35.5% and E²-TTT-MLP 37.1%. Full-attention Transformer++ still leads at 53.3%. [Tables 2–3]

On 14 LongBench tasks, the reported average scores are 14.1 for SwiGLU, 13.3 for MLP, 12.1 for HQLT, 10.3 for Mamba2 and 7.7 for LaCT. These are heterogeneous task scores, not one common classification-accuracy scale. The per-token loss plots show stable E²-TTT curves through the displayed 8K range on six datasets, while the tested LaCT curves worsen. Stable language-model loss does not by itself show retained exact information. [Figure 3, Table 4]

### The strongest long-range result is task specific

| 1.3B model | S-NIAH-1 at 8K | S-NIAH-1 at 16K | S-NIAH-2 at 8K | S-NIAH-2 at 16K |
|---|---:|---:|---:|---:|
| Mamba2 | 31.6 | 13.0 | 27.4 | 5.0 |
| HQLT | 37.4 | 25.2 | 15.4 | 4.4 |
| LaCT | 37.4 | 3.0 | 5.6 | 0.0 |
| E²-TTT-SwiGLU | 95.4 | 93.6 | 40.6 | 6.0 |
| E²-TTT-MLP | 88.2 | 85.0 | 9.8 | 4.0 |

All entries are reported percentages. The abstract's above-90% result is supported for the SwiGLU **passkey** task S-NIAH-1. At 16K the numerical-needle S-NIAH-2 task has already degraded to 6.0%, even though that is the best listed value. Neither the high absolute accuracy nor universal superiority extends to both tasks and both E² variants. [Figure 4, Table 14]

### Same-architecture controls are present

Table 5 includes three rows that share the authors' framework, SWA and fusion gate. LaCT-Matched ports LaCT's update into that framework. Chunk-averaged collapses E²-TTT's per-token momentum and decay factors into chunk scalars. The original LaCT row and SWA-only row are separate comparisons.

| Same-framework update | S-NIAH-1 2K | 4K | 8K | 16K | S-NIAH-2 8K |
|---|---:|---:|---:|---:|---:|
| LaCT-Matched | 99.8 | 99.2 | 51.6 | 0.0 | 4.8 |
| Chunk-averaged | 25.2 | 10.8 | 6.8 | 3.0 | 7.2 |
| E²-TTT-SwiGLU | 95.6 | 95.0 | 95.4 | 93.6 | 40.6 |

LaCT-Matched can be stronger near the training range but still degrades at longer lengths. Chunk-averaged has slightly *better* in-domain LAMBADA perplexity and zero-shot average than the corresponding full model, 15.6 versus 15.8 and 53.8% versus 53.6%, while retrieval is much worse. This is useful evidence that its retrieval failure is not simply a failure to train a language model. The comparison supports the specific aggregation rule under the tested framework. It is not a theorem that exact recurrence preservation is necessary for every long-context learner. [§5.4]

### Other ablations and their limits

- Removing SWA leaves the TTT-only model at zero on the tested S-NIAH-1 lengths. SWA-only also performs poorly at long lengths. This supports complementary paths in this implementation, not an impossibility theorem for all recurrence-only models.
- Removing post-chunk normalization actually **improves** S-NIAH-1 at 16K, 98.8% versus 93.6%, while LongBench drops from 14.1 to 13.4. The specific Table 9 discussion describes a tradeoff. The introductory claim in B.3 that removing normalization causes collapse is too broad for its own table.
- At \(C=512\), the closed-form model improves the three Table 8 metrics over averaged factors. At \(C=1024\), only WikiText perplexity improves. LAMBADA perplexity and mean accuracy are slightly worse. The source's unqualified “already outperforms” needs that metric restriction.
- Table 10 adds momentum **and** decay together, improving WikiText perplexity from 26.6 to 25.5. It does not independently identify each term's effect. Hyperparameter sweeps support reasonable robustness over the tested values, with degradation at the largest base learning rate. [Tables 8–11]

Appendix B.4 gives additional posthoc evidence: the scalar heads have nontrivial dispersion, and shuffling the learning-rate head reduces S-NIAH-1 16K accuracy from 93.6% to 6.0%. Momentum and decay-head shuffles have smaller effects. This supports use of input-aligned coefficients by the frozen checkpoint. However, preserving a head's marginal distribution while permuting tokens also changes its temporal and cross-head relationships. Approximate additivity of perplexity changes does not by itself prove statistical independence or rule out compensatory solutions after retraining. This is a qualification of the authors' causal/nonredundancy interpretation, not a dispute of the reported scores. [Table 12]

## Measured efficiency and real state

The paper's “kernel” is first a mathematical aggregation. The reported experiments use plain PyTorch, not the experimental fused Triton path now present in the repository. Training throughput is measured on the authors' stated single H100 64GB setup, with 2K sequences and batches four for 340M and two for 1.3B. [B.1, B.5, Figure 5]

| Training throughput, k tokens/s | 340M | 1.3B |
|---|---:|---:|
| E²-TTT-MLP | 20.0 | 8.9 |
| E²-TTT-SwiGLU | 17.6 | 7.6 |
| LaCT | 23.7 | 9.2 |
| Authors' Titans reproduction | 1.0 | Out of memory |

The often-quoted 15.6% and 3.3% overheads relative to LaCT are **MLP throughput reductions**. The SwiGLU reductions from the same displayed numbers are about 25.7% and 17.4%, respectively. Thus the variant with the best retrieval is not the one behind the smallest throughput gap.

Titans was reimplemented by the authors in PyTorch. They tried scan and memory-optimized dual forms and report the faster dual form with inner mini-batch 64. Its out-of-memory result is conditional on this implementation and measurement setup. It is not a general capacity limit for Titans. E2E-TTT in Table 14 is also an author PyTorch reproduction of an originally JAX-based method, with a short-length sanity check rather than an independently certified reproduction. [B.5–B.6]

Decode timing is the mean per-token time over 512 post-warmup steps, taking the median of three runs. Selected 1.3B results are:

| Batch and model | Decode ms/token, 2K → 16K | Peak memory GB, 2K → 16K |
|---|---:|---:|
| Batch 1, Transformer++ | 14.8 → 15.0 | 3.25 → 6.10 |
| Batch 1, E²-TTT-SwiGLU | 34.0 → 33.9 | 3.62 → 3.71 |
| Batch 8, Transformer++ | 14.8 → 59.9 | 7.50 → 29.90 |
| Batch 8, LaCT | 38.2 → 38.8 | 7.10 → 7.10 |
| Batch 8, E²-TTT-MLP | 33.7 → 33.8 | 6.86 → 6.86 |
| Batch 8, E²-TTT-SwiGLU | 34.3 → 34.4 | 8.08 → 8.08 |

The recurrent models' costs are approximately flat across these tested lengths. They do not universally beat attention latency, especially at batch one, and SwiGLU uses more memory than LaCT in the shown batch-eight setting. These are reported whole-model peak-memory measurements, not just the theoretical fast-weight arrays. The paper provides **no prefill-latency, prefill-throughput or time-to-first-token table**. Training throughput should not be relabeled as prefill performance. [Table 13]

The released inference state contains more than \(W\): two or three fast-weight tensors, corresponding momentum tensors, buffers for the unfinished chunk's keys, values and scalar factors, and the separate sliding-window KV state. Optional convolution state is also supported. With fixed architecture and window/chunk lengths these are bounded in size with respect to total sequence length, but that is not a finite-bit predictive-state theorem or a claim of lossless arbitrary-history compression.

## Release scope and reproduction boundary

The pinned [README](https://github.com/zeyun-zhong/E2-TTT/blob/0d1da370c7e3cea1642ba3af0477b7601849a1be/README.md) provides model classes, training/evaluation recipes, four checkpoint links, a state-transition verification script and experimental fused kernels. The [1.3B training script](https://github.com/zeyun-zhong/E2-TTT/blob/0d1da370c7e3cea1642ba3af0477b7601849a1be/training/train_1B.sh) explicitly uses 2240 tokens and approximately 16B total, matching B.1 despite the README's shorter “15B/2K” description.

The default MLP and SwiGLU update paths produce outputs from the old chunk state, accumulate an unfinished chunk, and update weights and momentum at a completed boundary. In cached continuation they explicitly require **one new token** per call. Initial multi-token prefill followed by token-wise decode is supported by that interface. Arbitrary multi-token continuation on an already populated cache is not established by it. Training omits an unused final-chunk update, while evaluation can retain the endpoint for later continuation. These details distinguish operational support from the abstract recurrence.

The [MLP update/cache source](https://github.com/zeyun-zhong/E2-TTT/blob/0d1da370c7e3cea1642ba3af0477b7601849a1be/e2_ttt/ops/e2_ttt_mlp/chunk_momentum.py) and [SwiGLU counterpart](https://github.com/zeyun-zhong/E2-TTT/blob/0d1da370c7e3cea1642ba3af0477b7601849a1be/e2_ttt/ops/e2_ttt_swiglu/chunk_momentum.py) also contain aggregate-update clipping, post-chunk normalization and truncation of small-coefficient momentum contributions. Those are additional implementation operations. In particular, clipping an aggregate is not automatically equivalent to clipping every token's contribution before summing. The [verification script's opening scope statement](https://github.com/zeyun-zhong/E2-TTT/blob/0d1da370c7e3cea1642ba3af0477b7601849a1be/training/verify_state_transition.py) explicitly limits its test to scan algebra for the same fixed gradients and excludes the gradient approximation, normalization, clipping, bf16 and Triton. It should not be cited as a full-model or cache-equivalence certificate. The [scalar scan](https://github.com/zeyun-zhong/E2-TTT/blob/0d1da370c7e3cea1642ba3af0477b7601849a1be/e2_ttt/ops/scan_utils.py) uses suffix log-products and `logcumsumexp`, forming the combined log-kernel before exponentiation.

The repository includes E²-TTT and LaCT configurations and general training metrics. The bounded inventory did not find the complete cross-model driver/results for Figure 5 or Table 13, or the Titans reproduction used there. Its presence of an evaluation harness and training token/time metrics does not by itself reproduce the inference comparison. The experimental Triton implementation is explicitly described by the README as outside the paper's results and outside its test coverage. No performance claim here relies on that optional path.

No dependency installation, model loading, numerical-verifier execution, training or GPU benchmark was performed in this reading. Code correspondence is scoped, and no whole-release correctness claim is made.

## Larger-budget and multimodal results

The 100B-token feasibility run also changes training context to 4K. At 1.3B, its SwiGLU checkpoint improves WikiText/LAMBADA perplexity from 19.9/15.8 to 16.0/10.0, commonsense average from 53.6 to 60.1, and the three-task retrieval average from 43.6 to 58.1. The retrieval inputs remain truncated to 2K. Since both token budget and context change, these gains do not isolate a token-scaling effect. The authors explicitly retain this limitation. [B.7, Table 15]

The video experiment adds a TTT branch with its own projections to Qwen3VL-2B-Instruct, freezes the backbone and trains the TTT parameters on 43K LLaVA-Video examples. The reported VideoMMMU/LongVideoBench scores are 43.9/59.0, versus 43.5/58.3 for full fine-tuning on the same data and 41.9/56.9 for the base model. Evaluation uses the specified fixed frame/token sampling protocols. This supports useful parameter-efficient adaptation at the tested scale. It does not establish equal training compute, a statistically significant universal advantage, or replacement of the backbone's self-attention memory. [§5.5, B.1–B.2, Table 6]

## Research conclusion and FP boundary

The main transferable mathematical object is a two-channel affine recurrence driven by frozen gradients and token-dependent scalars. Its chunk-end reduction is valid, efficiently evaluable in the supplied setting, and empirically better than averaged-factor controls on the strongest retrieval comparisons. The paper also demonstrates that similar language-model scores can conceal very different long-context retrieval behavior.

The limits are equally concrete: frozen gradient evaluation, stale within-chunk readouts, an auxiliary attention path, boundary normalization, learned but supplied state dimensions, task-specific retrieval success and implementation-dependent efficiency. The result does not prove finite physical memory suffices for arbitrary prediction or that prediction loss alone forms a minimal state space. No FP theorem, architecture change or experiment is proposed here without a separate explicit mapping and testable consequence.
