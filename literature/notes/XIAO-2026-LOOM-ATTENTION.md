# Rewirable Circuits in Transformers with Loom Attention

## Identity and actual coverage

- Da Xiao, Qingye Meng, Shengping Li and Xingyuan Yuan, Beijing University of Posts and Telecommunications and ColorfulClouds Technology. [arXiv:2611.30634v2](https://arxiv.org/abs/2611.30634v2), revised November 24, 2026, 08:46:11 UTC; v1 was November 23. [Versioned PDF](https://arxiv.org/pdf/2611.30634v2) and [TeX source](https://arxiv.org/src/2611.30634v2). The authenticated arXiv record and author repository identify a preprint. The source uses an ICML 2027 style with its arXiv flag; that is not evidence of conference acceptance.
- **Pro-B full reading, November 26, 2026:** all 23 pages; main §§1–6; Appendices A–H; every proof, equation, pseudocode block, three body footnotes, nine actual figures, ten tables and 63 printed references. The main reader covered the complete substantive TeX and bibliography and visually inspected every figure. Parallel assistants supplied bounded theory, experiment and release checks. Referenced papers do not inherit full-reading status; v1 remains a separate unread edition.
- PDF SHA-256: 734c5bd9c768eb2b205c9c39958883709ed7f08b9dcbeda7bf5f6e0fc8d01a40. Ignored source, PDF, extracted text, renders and support: literature/corpus/arxiv_frontier/2611.30634v2/.
- The local mathematical checks are limited to the stated routing model, the exact-support/threshold distinction, the effect of token centering on matrix rank, and resource arithmetic. Two small hand-calculated counterexamples below delimit particular statements. They do not refute the reported trained-model scores or certify the rest of the paper. No historical cover-free-family theorem was independently reproved; no proof script, formal verification, training or GPU reproduction was run.
- Official release pinned to [e52e5761d36066ed62e061a044d8314437cb7b11](https://github.com/Caiyun-AI/LoomFormer/tree/e52e5761d36066ed62e061a044d8314437cb7b11), November 26, 2026, 11:58:31 +09:00. The 41-file inventory, selected source paths, configurations, model metadata and inspection support are ignored under literature/corpus/pisf_prior_art/LOOM-2026-MATRIX-STREAM/. Source inspection is scoped, not a complete implementation audit.

## What is actually constructed

LoomFormer changes how attention heads exchange intermediate content **across network depth at the same token**. It adds a shared matrix residual stream to the ordinary vector stream. The vector generates read/write ports and positional queries/keys; the matrix accumulates content written by earlier heads and FFNs. Each later head reads its own query, key, value and local bypass from that shared matrix. Ordinary horizontal attention still connects tokens. [§§1, 3; Figures 1, 4]

This is an input-dependent factorization of inter-head communication, with strong reported language-modeling results. It is not a new fixed-size recurrent summary of the entire sequence. In the tested architecture, horizontal attention retains a full KV cache; MShift additionally keeps each layer's previous-token raw matrix input. The matrix dimensions and number of heads are supplied architecture choices, not structures created or enlarged during inference.

Three distinctions matter throughout the paper:

1. A combinatorial capacity result asks which exact writer–reader support patterns can be represented when ports or gates can be chosen.
2. A trained port generator is a particular low-rank neural function of the vector stream; representability does not prove that it learns or reaches every permitted pattern.
3. Empirical loss, head-use and attribution measurements characterize trained instances. Their improvements do not by themselves identify the unique causal source of the gain.

The theoretical vocabulary is useful when these distinctions are retained.

## The writer–reader model and its combinatorial result

### Virtual weights and node gating

There are \(w\) earlier writers with outputs \(o_i\in\mathbb R^d\), and \(r\) reader roles. In the basic Transformer decomposition, a writer's output projection and a reader's Q, K or V projection compose into a fixed virtual weight

\[
\bar C_{ij}=W_i^O W_j^s,\qquad
u_j=\sum_i o_i\,c_{ij}\bar C_{ij}.
\]

The scalar coefficient matrix \(C=(c_{ij})\) is called the wiring matrix. A connection is defined by \(c_{ij}\bar C_{ij}\ne0\). A pattern specifies exactly which writers reach which readers. A node-gated model has

\[
C=g(g')^\top.
\]

On exact support, the active edges are the fixed nonzero virtual-weight support intersected with an active-writer × active-reader rectangle. Dense fixed projections cause unwanted co-activation in this model; permanently zero projections make some pairs unreachable. [§2, Proposition 2.3; Figure 3]

Appendix A.1 handles pre-LN by expanding the residual sum at a fixed input. LayerNorm centering is a fixed linear map, its learned gain can be absorbed into the virtual weights, and its inverse norm is a common scalar. RMSNorm omits centering. This is a forward algebraic decomposition conditioned on the realized normalization scale. The scale still depends on the whole residual vector: a zero direct coefficient is not automatically a zero Jacobian or a statement of no causal influence through normalization.

### Clean-head routing and cover-free families

For each reader role \(j\), a set \(H_j\) of candidate heads may implement it. A task \(\pi:[r]\to[w]\) requires reader \(j\) to receive exactly writer \(\pi(j)\). Every enabled candidate head must be free of other enabled writers; the proof does not permit cancellation between heads. Define

\[
B_i=\{h\in H_j:\bar C_{ih}\ne0\}.
\]

A \(t\)-cover-free family requires

\[
B_i\not\subseteq\bigcup_{i'\in J}B_{i'}
\quad\text{for all }J\subseteq[w]\setminus\{i\},\ |J|\le t.
\]

The use of “at most” removes a possible vacuity when \(t\) exceeds the number of other writers. Under independently selectable node gates and fixed supports, all tasks are realizable exactly when each reader's family is \((r-1)\)-cover-free. The minimum candidate-head count is therefore \(N(w,r-1)\). [Theorem 2.4; full statement Theorem A.2 and proof, Appendix A.2]

The proof is short and specific. For sufficiency, enable the writers in \(\pi([r])\), choose a witness head in \(B_{\pi(j)}\) outside the union of the competing writers' supports, and disable the other heads. For necessity, force any set of at most \(r-1\) competing writers to be active through the other reader roles; a clean head for the desired writer must lie outside their union.

The paper imports these classical size bounds:

- \(N(w,1)\) is the smallest \(N\) with \(\binom{N}{\lfloor N/2\rfloor}\ge w\), approximately \(\log_2w\).
- For \(2\le t\le\sqrt w\), \(N(w,t)=\Omega(t^2\log w/\log t)\), with the stated upper bound \(O(\min\{t^2\log w,w\})\).
- For \(t>\sqrt w\), \(N(w,t)=\Theta(w)\); the displayed Bassalygo bound and singleton construction give equality \(N=w\) once \(\binom{t+2}{2}\ge w\).

These are cited dependencies, not newly checked historical results. In the paper's layer count \(w=nl,r=3n\), the linear regime applies when \(l\le9n-6\). The construction also pays for sufficiently many orthogonal residual subspaces. It does not hold fixed all ordinary Transformer width/resource budgets while supplying arbitrary support matrices for free. [Appendix A.3]

**Scope of this theorem.** It is a clean-head support-routing lower bound. It is not a general lower bound on Transformer computation, learned task expressivity or prediction quality. The full appendix explicitly excludes FFN rerouting and notes that value heads with identical attention weights can cancel interference. It also distinguishes independently switchable reader roles from physically coupled Q/K/V inputs in one head. The “if” direction presumes the required gate combinations can be selected; the equation \(C=g(g')^\top\) alone does not establish reachability of every gate combination by a fixed trained controller.

Appendix A.5 gives a separate ReLU FFN routing upper construction for supplied binary pattern indicators and bounded writer coordinates: \(2wrd\) hidden units and \(D\ge(w+r)d+wr\). The identity

\[
\operatorname{ReLU}(z-\Lambda(1-p))
-\operatorname{ReLU}(-z-\Lambda(1-p))=pz
\]

holds for \(p\in\{0,1\}\), \(|z|\le\Lambda\). The construction is expensive and uses an intervening FFN, but the paper explicitly proves no lower bound against all FFN routing.

### Local boundary: thresholded edges are not exact support

The main text counts sufficiently small entries as zero, and Appendix A.2 remark (i) says the counting argument is unchanged under this convention. An arbitrary magnitude threshold does not preserve a rank-one rectangle. A direct scalar example is

\[
C=\begin{pmatrix}2&1.2\\1&0.6\end{pmatrix}
=\begin{pmatrix}2\\1\end{pmatrix}
\begin{pmatrix}1&0.6\end{pmatrix},
\qquad \bar C_{ij}=1.
\]

Thresholding at \(0.8\) leaves three edges, an L-shaped pattern. Thus the exact-support argument cannot be transferred unconditionally to magnitude-thresholded patterns. A binary gating interpretation or explicit on/off margins and a suitable robustness statement would be needed. This hand example addresses the approximate-edge extension, not the cover-free argument under its exact clean-head assumptions.

Likewise, naive vertical attention with a finite unmasked softmax has strictly positive weights, and a finite sigmoid gate cannot itself be exactly zero. Exact absent connections require zero ports, masks, exact switches, or a limiting/quantitative formulation. The reported plots and training scores do not depend on claiming such exact zeros.

## From vertical attention to a compact matrix stream

Naively, each reader can attend to all earlier head outputs at that token, with identity virtual weights. Generating a full weight vector for every reader uses approximately

\[
\frac32n^2L(L-1)D
\]

parameters and as many multiply-adds per token. Factoring the scoring weights alone still leaves a quadratic-in-depth collection of attention weights and aggregations. [§§2–3; Appendix A.4]

LoomFormer instead accumulates a matrix \(M\in\mathbb R^{d_k\times d}\):

\[
M\leftarrow M+(k_i^m)^\top o_i,\qquad
u_j=q_j^mM.
\]

Without MShift, and with scalar normalizations absorbed appropriately,

\[
u_j=\sum_i\langle q_j^m,k_i^m\rangle o_i,\qquad
C=KQ^\top,\qquad
\operatorname{rank}C\le\min(w,d_k,r).
\]

The heads share this matrix. In sequence-axis linear attention, by comparison, each head typically maintains its own matrix across tokens, and that matrix's read is the horizontal head output. Here the state accumulates across depth and its reads feed horizontal Q/K/V computations. The axes and sharing structures differ. [§4, Appendix A.7]

### Ports, content and residual timing

For a sub-layer input \(x\), low-rank shared features are

\[
x^r=\operatorname{GELU}(xW_1^R),\qquad
x^w=\operatorname{GELU}(xW_1^W).
\]

Each read arm uses

\[
q^m=\operatorname{RMSNorm}(x^rW_2^R)\,
       \sigma(xW_g^R)
       +\bar q\,\sigma(xW_{\bar g}^R),
\qquad u=q^mM.
\]

The two gates are scalars per head/arm. A write uses

\[
k^m=\operatorname{RMSNorm}(x^wW_2^W)\,
       \sigma(xW_g^W),\qquad
\Delta M=(k^m)^\top o.
\]

These are dense signed linear ports, not sparse top-k selectors or probability distributions over slots. Their direction and magnitude are separately parameterized. Static read directions and dynamic read directions coexist.

Before LoomMHA reads, a per-slot gate mixes current- and previous-token raw matrix inputs at the same layer:

\[
\widetilde M_{l,t}=
\operatorname{MNorm}\!\left[
z_{l,t}\odot M_{l,t-1}+(1-z_{l,t})\odot M_{l,t}
\right].
\]

MNorm is a scalar RMS normalization over the entire flattened matrix, not a separate per-slot normalization. Each head reads \(\tilde q,\tilde k,v,o^m\) from this view. Q and K concatenate a \(d/4\)-wide vector-stream RoPE projection with the \(d\)-wide matrix read. V comes only from the matrix. The horizontal attention mask is strictly causal, excluding the current token; the \(o^m\) bypass provides the current token's local content. A head output contributes both a projected vector residual and a normalized outer-product matrix write.

The FFN has a vector branch and a second content branch whose output is split into head-sized vectors and written to the matrix. This is the only post-embedding route for vector-stream content to enter the matrix. The embedding initializes both streams. Both receive residual additions; the last block omits unused matrix writes. MShift changes the **read view**, not the identity of the raw matrix residual being accumulated. [§3.2; Appendix C; release paths below]

The default \(d_k=2n\) gives \(d_kd=2D\) matrix entries, plus \(D\) vector entries per token. \(D_r=n^2\), capped at 640 in the 2.8B model. Matching total parameters reallocates the FFN widths, approximately 2:1 between the vector and matrix-writing branches. This is not a free extra matrix on top of an otherwise identical FFN budget.

### What the port-capacity proposition does and does not show

With fixed K and Q, flattening M turns its reads and writes into fixed Kronecker-structured linear projections. The effective virtual weight is \(\langle q_j,k_i\rangle I_d\); scalar gates and scalar normalization can be absorbed into rows/columns. This is the intended fixed-port, node-gated comparison model. The argument explicitly omits MShift: dynamic per-slot cross-token mixing cannot simply be called a fixed projection. [Proposition 3.1; Appendix A.6]

For a pattern with at most \(d_k\) active writers, choose an injection of those writers into slots, assign one-hot write keys, zero inactive keys, and let each query sum the basis vectors of its desired writers. This exactly implements the support pattern with one reader head per role. RMS rescaling preserves the support. The construction is locally correct as a port assignment.

It does not prove that the particular shared low-rank GELU generators can realize every such assignment from all relevant inputs. Nor does it prove that all patterns involving more than \(d_k\) writers fail; it supplies a sufficient universal class, with a rank bottleneck and possible interference beyond it. The scalar-gate exact-zero qualification above remains. Across tokens, horizontal attention mixes representations computed under different ports, so the whole sequence model is not a single fixed-port Transformer.

## The rank measurements need a separate mathematical qualification

The uncentered \(C_t=K_tQ_t^\top\) rank bound is valid. Appendix H reports a different object. It normalizes each port direction, weights writers by a fixed corpus RMS norm, and then subtracts each pair's token mean:

\[
\widehat C_{ij}(t)=\bar\omega_i
\langle\widehat q_j(t),\widehat k_i(t)\rangle,\qquad
\Delta\widehat C(t)=\widehat C(t)-\mathbb E_{t'}\widehat C(t').
\]

Its energy effective rank is the exponential entropy of normalized **squared** singular values. Fixed ports with positive scalar gates have constant unit directions, hence zero centered matrix; that part of the comparison is sound, apart from a needed convention for zero ports.

**Local check:** a pointwise rank-\(d_k\) factorization does not generally survive subtraction of the token mean. With \(d_k=1\), \(\bar\omega_1=\bar\omega_2=1\) and two equally likely tokens, take these stacked ports, each row of unit norm:

\[
\widehat K_1=\widehat Q_1=(1,1)^\top,\qquad
\widehat K_2=\widehat Q_2=(1,-1)^\top.
\]

Then

\[
\widehat C_1=
\begin{pmatrix}1&1\\1&1\end{pmatrix},\quad
\widehat C_2=
\begin{pmatrix}1&-1\\-1&1\end{pmatrix},\quad
\mathbb E\widehat C=I,\quad
\Delta\widehat C_1=
\begin{pmatrix}0&1\\1&0\end{pmatrix}.
\]

The centered matrix has rank and energy effective rank two, although each uncentered matrix has rank one. This example obeys the stated unit-direction definition; it does not need gate magnitude fluctuations. Consequently §5.3's transfer of the Loom \(d_k=64\) ceiling to the centered quantity is not established by the uncentered factorization. Without a common cross-token row/column subspace, the general dimensional bound is \(\min(w,96)\), not 64.

The baseline comparison is more nuanced. When node-gating factors are omitted as in Appendix A.7, shared reader columns for Transformer/HC/mHC, or three fixed Q/K/V column groups for MUDDFormer, remain shared after centering. That structural restriction can preserve the respective 1/3 bounds. Generic rank-one node gating alone would not. The reported Loom effective ranks, mean 26.4 and final-layer 41.0, remain descriptive experimental measurements; the example does not show them to be numerically false. It removes an unjustified general upper-bound interpretation.

## Empirical evidence and matched resources

### Scaling and longer pretraining

All scaling experiments use Pile, JAX/MaxText, the same data order, tokenizer and schedule for the compared baselines. The reference is Transformer++ with RoPE, SwiGLU and RMSNorm; residual alternatives are DHC, mHC, full AttnRes and MUDDFormer. [§5.1, Appendix D]

| Scale | Total parameters | Layers / width | Heads / head width | Tokens | Context |
|---|---:|---:|---:|---:|---:|
| Medium | 432M | 18 / 1200 | 16 / 75 | 7B | 4096 |
| Large | 778M | 22 / 1536 | 16 / 96 | 14B | 4096 |
| XL | 1.4B | 28 / 1920 | 20 / 96 | 26B | 4096 |
| LoomPythia | 2.8B | 32 / 2560 | 32 / 80 | 300B | 2048 |

The scaling plot uses **total parameters × training tokens** as its compute proxy. The 3.19–3.25× Transformer++ comparison and 1.73–2.76× residual-baseline comparisons are obtained by log-linear interpolation, not by training a separate exactly quality-matched baseline for each value. The Large-scale analytical FLOP adjustment changes 3.19× to about 3.10×. At XL, Loom loss is 1.979 versus Transformer++ 2.101, below the largest measured model of every baseline.

There is a concrete XL exception to an otherwise similar architecture comparison: for stability Loom's vector FFN uses bounded SiTU-GLU with \(\beta_1=4,\beta_2=7\), while the baseline description lists SwiGLU. This is a package-level comparison, not a perfectly isolated change in routing alone.

For 300B-token pretraining, LoomPythia and mHC-Pythia use serial sub-layers, while original Pythia uses parallel sub-layers. The authors cite prior and internal evidence that this placement is quality-neutral, but do not separately tabulate that control here. [§5.2, footnote 3]

| Model | Pile ppl | FLAN target-span ppl | 0-shot 10-task mean | 5-shot 10-task mean |
|---|---:|---:|---:|---:|
| Pythia-2.8B | 6.63 | 8.16 | 56.3 | 57.3 |
| Pythia-6.9B | 6.29 | 7.85 | 58.1 | 59.3 |
| mHC-Pythia-2.8B | 6.24 | 7.35 | 58.8 | 59.9 |
| Pythia-12B | 6.01 | 7.26 | 59.9 | 60.8 |
| LoomPythia-2.8B | 6.02 | 6.94 | 59.9 | 61.6 |

Table 2 reports task-specific outcomes as well as these averages. Matching the 12B zero-shot mean does not mean winning every task: Pythia-12B remains stronger on several rows. The approximately 4.9× compute statement for the mean of zero/five-shot scores is explicitly a log-linear **extrapolation** of Pythia. FLAN is a randomly sampled instruction/chain-of-thought/few-shot subset; the inspected text gives no subset count. Quality results have no reported cross-seed confidence intervals.

### Ablations weaken an exclusively dynamic-writing explanation

All 18 variants use Medium/7B/4k, with removed parameters reallocated to the vector FFN, matching 432.11M within ±1.4K. Gain is

\[
\frac{L_{\rm Tfm++}-L_{\rm variant}}
     {L_{\rm Tfm++}-L_{\rm full}},
\]

where baseline and full losses are 2.443 and 2.266. It is a retained validation-loss improvement, not an accuracy percentage or an identified additive causal contribution. [Table 10]

| Variant | Loss | Retained gain |
|---|---:|---:|
| Full LoomFormer | 2.266 | 100.0% |
| Static attention write directions, gates retained | 2.266 | 100.0% |
| Static FFN write directions, gates retained | 2.268 | 99.3% |
| All write directions static, write gates retained | 2.274 | 95.6% |
| All write directions static, write gates removed | 2.283 | 90.3% |
| Static read queries, read gates removed | 2.310 | 75.4% |
| Static reads/writes, dynamic write gates retained | 2.327 | 65.8% |
| Static reads/writes, port gates removed, MShift retained | 2.344 | 56.0% |
| Previous row with MShift removed | 2.348 | 53.6% |
| No FFN matrix write | 2.300 | 80.7% |
| No output bypass; current-token attention restored | 2.299 | 81.8% |
| No MShift | 2.277 | 94.2% |

The final static/no-MShift row is the appendix's exact fixed-port comparison. The main text's 56% shorthand omits the remaining MShift. Stable write slots plus dynamic read selection and magnitude gating preserve much of the gain; fully dynamic write directions are not shown necessary for nearly all measured improvement. The static dual-stream backbone itself retains over half the loss gain.

Removing bypass also restores the horizontal self-diagonal. Removing vector-stream RoPE moves RoPE onto 18 of 75 matrix-read coordinates. These are compound substitutions, not simple deletion of one independent mechanism. Norm/gate ablations show interactions: removing dynamic norms alone retains 87.1%, while removing both dynamic norms and gates retains 90.3%.

Figure 7 varies \(d_k=16,32,48,64\), with losses 2.293/2.266/2.262/2.259. Total vector-plus-matrix size is 2D/3D/4D/5D. The default 32-slot point is near a diminishing-return region. Comparisons to DHC's 4D and MUDDFormer's layer-growing residual stores concern this per-token representation size, not total training HBM or inference cache bytes.

## Arithmetic overhead, measured throughput and storage lifetime

Under matched dense parameter count \(P_0=12LD^2\), the leading reference forward cost is

\[
F_0=2TP_0+2LDT^2.
\]

Four reads per head plus writes from attention/FFN and the embedding cost \((12L-2)TDd_k\). Wider Q/K add \(LDT^2/4\), while V width is unchanged. With \(\rho=T/D,d_k=2n\), the approximation is

\[
\frac{\Delta F}{F_0}\simeq
\frac{1}{d(1+\rho/12)}
+\frac{1}{8(1+12/\rho)}.
\]

The parameter reallocation already pays for port generators and the FFN matrix branch in the dense-projection budget; charging them again would double-count. The formula excludes shared embedding/unembedding, normalization, nonlinearities, bias and elementwise operations. Medium rounds \(d/4=18.75\) down to 18, explaining 3.70% rather than the unrounded 3.81%. The long-context horizontal attention term remains quadratic in sequence length. [Appendix E]

| Scale | Approx. extra forward FLOPs | Transformer step ms | Loom step ms | Loom training throughput |
|---|---:|---:|---:|---:|
| Medium | 3.70% | 1224 | 1352 | 90.5% |
| Large | 3.13% | 962 | 1078 | 89.2% |
| XL | 2.77% | 1590 | 1723 | 92.3% |
| 2.8B | 1.95% | 2988 | 3233 | 92.4% |

These TPU v5p device-step measurements use full activation rematerialization and Splash attention on both sides. Loom uses fused Pallas forward/backward kernels. At 2.8B, Loom alone uses 512-token cross-entropy chunking to fit v5p-128 HBM; original Pythia does not. The measured overhead is therefore larger than the FLOP ratio and includes implementation/memory effects. [Appendix F, Table 8]

Inference uses one A800-80GB PCIe, BF16, five-run medians, fused Triton and compiled CUDA-graph decode. Prefill uses each model's faster backend: FlashAttention for the reference and cuDNN SDPA for Loom's unequal QK/V dimensions. At 2.8B, prefill B1/B8 is 30.4k/33.1k tokens/s versus 34.7k/36.6k; decode B1/B16/B64 is 171/1248/1836 versus 198/1425/2066. Across scales, Loom sustains about 84–92% of the reference inference throughput. [Table 9]

The paper does not directly measure wall time to reach equal quality. Its fitted/interpolated training-compute advantages cannot be restated as observed threefold wall-clock speedups. Similarly, the 2D matrix is a depth-local representation count: retaining full horizontal K/V and per-layer last-M states leaves generation storage growing with context.

## Mechanistic evidence and causal scope

Appendix H uses 300B checkpoints, held-out Pile sequences of length 2048 and positions \(t\ge64\). The dynamic rank statistic is described above. Its shaded band is the 10th–90th percentile over token measurements, not a seed-level confidence interval. Read-port cross-token cosine distances average 0.33–0.46; attention and FFN write directions average 0.36 and 0.56. These measurements support genuine variation in directions, beyond scalar gate variation.

“Head on” means the attention argmax avoids positions 0/1 and a supplied list of sink tokens. In layers 17–32, non-sink fractions are 74.4% for Loom, 22.9% for Pythia and 17.7% for mHC. Figure 6's all-32-layer legend instead gives 76.7/27.4/30.6%. Masking the reference models' current-token diagonal leaves their deep-layer fractions at 21.2/15.7%, so that particular mask difference does not explain the observation. It is still an operational attention statistic, not a direct measurement that every counted head performs necessary computation.

Conditioning on the current gates and normalization, the authors decompose

\[
u_j=\sum_i c_{ij}o_i,\qquad
a_{ij}=\frac{c_{ij}\langle o_i,u_j\rangle}{\|u_j\|^2},
\qquad \sum_i a_{ij}=1.
\]

The sum includes embedding, attention and FFN writers at the current and previous token. Reported reconstruction differs from BF16 execution by 0.4% median RMS. Positive attribution mass mostly comes from attention writes (53.4–62.5%), then FFN writes (27.5–35.2%), with embedding around 10–12%. The previous-token share is 13.7–15.2% of absolute attribution, a different denominator. Figure 8's routing map is column-max normalized.

This is an additive forward decomposition, not a total derivative through the port generators, nor a general causal attribution. In particular, a nonrectangular heatmap of thresholded \(a_{ij}\) does not independently establish the exact-support theorem: \(a_{ij}\) also contains writer/output geometry, and thresholding already has the limitation above.

There is a genuine, narrower intervention. For one country–capital prompt ending in Germany followed by a colon, the next-token probability of Berlin is 0.65. Freezing the colon's dynamic read ports to the previous token's values lowers it to 0.54 for layer 19 alone, and 0.41 when applied across all layers. Figure 9 displays a selected submatrix: the top 18 earlier attention writers and six readers per arm, selected by peak absolute attribution across those two tokens. At the colon, current Q and bypass affect the current prediction; current K/V only serve future tokens under the strict mask.

This single-prompt intervention supports functional relevance of token-varying read ports. It does not supply a dataset-wide causal decomposition of five-shot or FLAN gains. The main text's statement that increased non-sink head use accounts for those gains is stronger than the reported population-level intervention evidence.

## Official implementation and artifact scope

The pinned repository has real JAX/Flax training components, Pallas kernels, PyTorch model implementations, Triton inference kernels, a checkpoint converter, benchmark driver and tests. The release is not just architectural pseudocode. The inspection did not run any of them.

Directly rechecked paths include the root and PyTorch READMEs, the central LoomPythia matrix/attention/decoder/cache code, static cache allocation and the fast-engine initial-prefill branch. A parallel source check covered the corresponding JAX/configuration paths and model metadata. In the pinned [LoomPythia implementation](https://github.com/Caiyun-AI/LoomFormer/blob/e52e5761d36066ed62e061a044d8314437cb7b11/pytorch/loompythia/modeling_loompythia.py):

- Each forward call embeds the current tokens and creates M with shape B × T × slots × head-width.
- Layer updates add attention and FFN outer products to the unshifted raw matrix residual.
- MShift builds a read view from the current layer's raw input and that layer's previous-token raw input. Whole-matrix RMSNorm is applied to this view.
- Each layer saves its last raw input M for continuation, alongside attention K/V in DynamicCache. Standard HF continuation supports multiple new tokens with existing-prefix attention and the first token's prior M.
- Port operations are dense signed contractions with sigmoid gates. There is no top-k slot pruning, learned bank allocation or eviction mechanism.
- The released Pythia variant also has full-head Q/K normalization, read scales and content divisors beyond the schematic main-text equations. These details belong to the actual checkpoint configuration and should be preserved in any implementation comparison.

The [fast cache](https://github.com/Caiyun-AI/LoomFormer/blob/e52e5761d36066ed62e061a044d8314437cb7b11/pytorch/fast_inference/cache.py) preallocates per-layer K/V up to max_len, plus last-M buffers. The Pythia fast path uses a transposed matrix layout; the padded Llama path uses two M buffers. This is not a context-independent total cache.

The inspected fast-engine prefill branch attends within the supplied initial prompt and writes K/V starting at cache index zero; its documented paired usage is initial prefill followed by single-token decode. It should not inherit an arbitrary cached chunk-append guarantee merely because the separate standard HF implementation supports chunked continuation. This is an API-scope distinction, not a claim that the documented initial-prefill/decode path fails.

Public model metadata was authenticated for [LoomPythia-2.8B at be28d5dc2f8754bca698e0685fb560b4b07bd53d](https://huggingface.co/Caiyun-AI/LoomPythia-2.8B/tree/be28d5dc2f8754bca698e0685fb560b4b07bd53d), November 24 07:07:59 UTC, and [mHC-Pythia-2.8B at bdb878125bc78db18a493fa2552c8e5575511d4d](https://huggingface.co/Caiyun-AI/mHC-Pythia-2.8B/tree/bdb878125bc78db18a493fa2552c8e5575511d4d), 07:08:02 UTC. Each lists a single model.safetensors; absence of a sharded index file is therefore not evidence of absent weights. No weight file was downloaded, executed or numerically compared to the JAX source. Published model metadata and inspected tests are evidence of available artifacts, not independent reproduction of paper numbers.

The public inference benchmark resets the decode position to a fixed context after each measured step. It is a fixed-context microbenchmark, not end-to-end growing-context generation. The specialized Pythia fused path requires BF16, \((d,d_k,r_{\rm RoPE})=(80,64,20)\), and a power-of-two head count at least 16; other configurations can use a packed PyTorch path. The pinned inventory did not expose complete raw scaling sweeps, a ten-task evaluation driver or the paper's attribution/intervention driver. These limited inventory findings do not assert that such materials exist nowhere else. The release snapshot postdates v2 and is not authenticated as the exact original experiment commit.

## Research value and limits

The useful architectural result is a concrete dual-stream design: a compact vector controls dense head-specific ports into a shared depth matrix, with parameter reallocation and efficient fused implementations. The ablations distinguish stable write addresses, dynamic magnitude and dynamic read selection. The cost accounting separates analytical contractions from observed latency and context-growing caches.

The combinatorial model explains a particular price of clean support routing, and its port assignment is constructive. Exact-support versus thresholded patterns and uncentered versus token-centered rank must be kept separate; the two local examples above prevent importing stronger statements than the proof supports. The reported empirical advantages remain interesting despite those limitations.

No FP transfer theorem is proposed. The paper neither derives a minimal future-predictive sufficient state nor bounds learned dictionary acquisition, installed bit payload or finite-precision log-loss. A matrix shared across depth, token-varying communication coefficients and genuine stochastic state formation are different objects. Applying this architecture to the project's current inference/storage questions would require new assumptions and experiments, not a relabeling of the supplied matrix as a predictive state.
