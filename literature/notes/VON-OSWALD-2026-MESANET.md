# MesaNet: locally optimal regression and the finite solver actually executed

## Sources and actual coverage

- Johannes von Oswald, Nino Scherrer and coauthors, **MesaNet: Sequence Modeling by Locally Optimal Test-Time Training**.
- Primary reading: [arXiv 2506.05233v2](https://arxiv.org/abs/2506.05233v2), June 3, 2026, [PDF](https://arxiv.org/pdf/2506.05233v2), [complete source](https://arxiv.org/src/2506.05233v2).
- Authenticated peer-reviewed counterpart: [ICLR 2026 proceedings](https://proceedings.iclr.cc/paper_files/paper/2026/hash/2c3d5a4eff20d24390a445762d61bfbb-Abstract-Conference.html), [conference PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/2c3d5a4eff20d24390a445762d61bfbb-Paper-Conference.pdf).
- Pro-B, November 26, 2026, Shanghai. **The arXiv v2 is fully read:** all 53 physical pages, with scientific content through p.52 and a final header/page-number-only page, main Sections 1–6, Appendices A–O, all mathematical derivations, Algorithm 1, 14 numbered figures, 19 numbered tables, footnotes, acknowledgments, reproducibility statement and 123 printed references. Read all active scientific TeX and nine separate table files. Inspected every scientific figure on PDF pp.2,5,7,8,10,35,36,39,41,51,52 and the mathematical pages 24–27 visually.
- Figures 5 and 7 repeat the same two assets. There are 25 active image insertions using 23 distinct assets, not 25 independent experiments. A commented-out old figure was excluded.
- The conference PDF has 51 pages and remains **scoped comparison**, not a second full read. First-page metadata, source-to-PDF differences, changed timing presentation and relevant acknowledgment/related-work passages were compared. The v2 adds Sarthak Mittal to the author list, where the conference version acknowledges his post-submission contribution. It removes the middle single-layer inference panel of Figure 2, expands whole-model throughput discussion, and adds Lattice/Trellis references. These editions are not interchangeable.
- The main reader covered the entire v2. Assistants supplied bounded mathematical, edition/evidence and visual-inventory checks. There was no training reproduction, kernel audit, formal proof replay or independent certification of every claim.

**Assessment.** The useful construction is a recurrent sufficient-statistic pair for weighted ridge regression, together with parallelizable matrix-vector products for a query-only conjugate-gradient solve. The ideal regression optimum, the finite solver, and the learned language model are three distinct objects. The paper itself acknowledges approximate implicit differentiation. Several printed chunk and gradient formulas need local correction, without establishing an implementation failure. Experiments show competitive average perplexity alongside substantial recall and translation deficits relative to full attention.

## 1. What is optimized and what is stored

For one head, let keys and queries lie in \(\mathbb R^d\), values in \(\mathbb R^m\), and let \(\Lambda\succ0\) be a fixed-in-time learned diagonal matrix. With zero initial states the actual layer uses

\[
G_t=\gamma_tG_{t-1}+\beta_tv_tk_t^\top,
\qquad H_t=\gamma_tH_{t-1}+\beta_tk_tk_t^\top,
\]

\[
A_t=H_t+\Lambda,\qquad
x_t=A_t^{-1}q_t,\qquad o_t=G_tx_t.
\]

Here \(G_t\in\mathbb R^{m\times d}\) and \(H_t\in\mathbb R^{d\times d}\). Scalar write and forget gates are content-dependent. The full block also contains projections, local convolutions, nonlinearities, normalization and the surrounding decoder/MLP backbone. The output includes the current causal input's write and predicts the next token. [Section 2, Appendix E]

Define

\[
\zeta_{ti}=\prod_{j=i+1}^t\gamma_j,
\qquad w_{ti}=\beta_i\zeta_{ti}.
\]

For nonnegative gates, the exact corresponding objective is

\[
\widehat\Phi_t=\arg\min_\Phi
\left\{\frac12\sum_{i\le t}w_{ti}\|v_i-\Phi k_i\|^2
+\frac12\operatorname{tr}(\Phi\Lambda\Phi^\top)\right\}.
\]

Its normal equations give \(\widehat\Phi_tA_t=G_t\), and therefore \(o_t=\widehat\Phi_tq_t\). The objective fits **one static coefficient matrix to a weighted history** at the current time. It is not a trajectory objective for independently changing past coefficients. [Equations 4,7, Appendix D, Equations 25–38]

The main objective initially omits the input gate while the actual recurrence includes it. Appendix D explicitly absorbs this gate into the data. A consistent interpretation is

\[
\widetilde k_i=\sqrt{\beta_i}k_i,
\qquad \widetilde v_i=\sqrt{\beta_i}v_i.
\]

Both need the square-root factor. This reconciles the displayed regression argument with the implemented recurrence as described.

Local optimality refers to this quadratic loss in learned features. It is not optimal next-token risk, optimal physical memory, recovery of a true hidden state, or zero error on arbitrary associations. Even one unit key/value with scalar ridge \(\lambda>0\) gives self-read \(v/(1+\lambda)\). The global model parameters are still learned by ordinary end-to-end training. No theorem here derives autonomous discovery of the chosen state structure.

The constructive learning principle is to let the outer predictive objective learn which key/value regression problem should be solved inside each layer, while making its inner optimum algebraically accessible. The key second moment supplies directions and scales missing from a single Hebbian sum. Without forgetting, adding one observation gives the exact update

\[
\widehat\Phi_t=\widehat\Phi_{t-1}
+\beta_t(v_t-\widehat\Phi_{t-1}k_t)k_t^\top A_t^{-1}.
\]

Thus an error-correcting write can incorporate the curvature of all retained keys, rather than a scalar learning rate alone. Appendix H derives the unit-weight Newton interpretation. The query-only implementation obtains the required output without materializing this entire coefficient update. This is a concrete combination of representation learning outside the layer and solved learning dynamics inside it.

## 2. Why a query solve suffices, and what parallelization buys

The layer needs \(A_t^{-1}q_t\), not every column of \(A_t^{-1}\) or \(\widehat\Phi_t\). This is an exact algebraic saving. Conjugate gradient replaces the solve with iterations involving \(A_tp\), vector operations and inner products. With input gates absorbed,

\[
A_tp=\Lambda p+\sum_{i\le t}\zeta_{ti}k_i(k_i^\top p).
\]

The second term has gated-linear-attention form. Chunkwise linear-attention machinery can compute these products for many prefix positions together, storing boundary matrices instead of every \(H_t\). The same observation applies to \(G_tx_t\) and the reverse-time sums in the ideal implicit gradient. This is parallelism across sequence positions, with serial dependence between CG iterations. [Appendices C–D]

For fixed dimensions and iteration cap, inference cost is independent of prefix length. It still pays \(O(kd^2)\) for the solver and stores \(md+d^2\) recurrent scalars per head, before local buffers. For equal dimensions this is two matrix states, rather than one. The paper's claim that extra state is less than 1% of overall model memory uses a denominator including model parameters. It is not a statement that recurrent-state cost barely changes, and batching changes this accounting. [Table 5]

### 2.1 The block carry must be forgotten too

For a chunk beginning after position \(c\), the correct unrolling is

\[
G_t=\zeta_{tc}G_c+\sum_{i=c+1}^t\zeta_{ti}v_ik_i^\top.
\]

Writing chunk columns as \(c+1,\ldots,c+C\) and
\(D_c=\operatorname{diag}(\zeta_{c+1,c},\ldots,\zeta_{c+C,c})\), this yields

\[
O_c=G_cQ_c^*D_c+
V_c[Z_c\odot(K_c^\top Q_c^*)].
\]

The main text and Appendix D Equations 39–40 omit \(\zeta_{tc}\), or equivalently \(D_c\), on the carry. Their displayed key range also includes \(C+1\) columns for a \(C\)-column chunk. Main Equation 9 mixes starred and unstarred queries in its GLA formula. These are local printed inconsistencies. For example, scalar \(G_c=1\), next \(\gamma=1/2,v=0,k=q=1\) gives GLA output \(1/2\), whereas the printed carry gives 1.

Restoring these factors preserves the intended algorithm. The corrected chunk computation still uses the full current prefix system at each position. Chunking itself does not replace \(H_t\) by a frozen chunk-start regression target.

### 2.2 A constructive reuse rule with an explicit certificate

The Discussion suggests warm-starting neighboring solves, especially for heads that hardly forget. The following is an independent conditional derivation of that suggestion, not a tested improvement or a novelty claim. Suppose the previous solve retained its approximate solution \(z\), query \(q_{t-1}\) and residual \(r_{t-1}=q_{t-1}-A_{t-1}z\). Using \(z\) as the next initial guess gives exactly

\[
r_t^{(0)}=q_t-\gamma_tq_{t-1}+\gamma_tr_{t-1}
-(1-\gamma_t)\Lambda z-\beta_tk_t(k_t^\top z).
\]

This residual costs only vector operations with diagonal \(\Lambda\), after the usual statistic update. It avoids a fresh dense matrix-vector product merely to evaluate the candidate initial guess. The extra carried information is a constant number of length-\(d\) vectors per head, rather than another \(d\times d\) matrix. It can immediately start a standard CG correction solve \(A_t\Delta=r_t^{(0)}\), then return \(z+\Delta\).

With no forgetting and an unchanged query, an exact previous solve has next residual \(-\beta_tk_t(k_t^\top z)\). If the new key is orthogonal to that solution, the old solution is already exact for the new system. More generally, high retention alone does not suffice. Query motion, the new observation's alignment and accumulated solve error all appear explicitly in the formula. This identifies what a reuse hypothesis must measure.

There is also a conservative computable output certificate. Maintain one scalar

\[
S_t=\gamma_tS_{t-1}+\beta_t\|v_t\|\|k_t\|,
\quad S_0=0,
\]

so \(\|G_t\|\le S_t\). If the learned ridge is lower-bounded by \(\lambda_0>0\), any final residual satisfying

\[
S_t\|r_t\|/\lambda_0\le\varepsilon_{\rm out}
\]

certifies error at most \(\varepsilon_{\rm out}\) against this head's ideal regression read on the same realized features. If \(S_t=0\), the output is zero regardless of the solve. The proof is the residual identity in Section 3 plus the triangle inequality for the cross-statistic. This supplies a concrete output-budget stopping rule, rather than treating a relative solver residual as a language-quality guarantee.

The bound may be loose, extra vectors and scalar operations must be counted, and full-model error propagation still needs separate analysis. Whether residual reuse lowers measured computation at matched output or language error is an open empirical question. No implementation, FP architecture change or imposed research direction follows from this candidate.

## 3. Exact solve versus finite CG

Let \(\widehat x_t\) denote the returned approximation and
\(r_t=q_t-A_t\widehat x_t\). Independently, direct subtraction gives

\[
\widehat x_t-x_t=-A_t^{-1}r_t,
\qquad
\|\widehat o_t-o_t\|
\le \|G_tA_t^{-1/2}\|\,\|r_t\|_{A_t^{-1}}
\le \frac{\|G_t\|}{\lambda_{\min}(A_t)}\|r_t\|.
\]

Algorithm 1 stops at \(\|r_k\|\le\epsilon\|r_0\|\). The threshold is relative to the **initial residual**, not directly to query norm, output error, or language loss. A small residual controls output only with the corresponding gain and conditioning factors. No end-to-end language-risk bound is supplied.

Since keys are normalized and the weights are nonnegative,

\[
\lambda_{\min}(A_t)\ge\lambda_{\min}(\Lambda),
\qquad
\kappa_2(A_t)\le
\frac{\lambda_{\max}(\Lambda)+\sum_iw_{ti}}
{\lambda_{\min}(\Lambda)}.
\]

This independent bound proves well-posedness, but a fixed ridge alone does not give sequence-length-independent conditioning. A further uniform \(\gamma_t\le\bar\gamma<1\), \(\beta_t\le1\), gives \(\sum_iw_{ti}\le1/(1-\bar\gamma)\).

The implementation description lower-bounds diagonal regularization by 0.25 and initializes it at one. It also states an upper forgetting bound \(b_\gamma=0.9975\), but its displayed correction is

\[
\gamma_t^{\rm eff}=\gamma_t^{\rm raw}
[1-(1-b_\gamma)\beta_t^2].
\]

This formula alone only implies \(\gamma_t^{\rm eff}\le1-(1-b_\gamma)\beta_t^2\), which exceeds \(b_\gamma\) when \(\beta_t<1\). Separate clipping would need implementation evidence. This observation does not establish an actual numerical failure. [Appendix G.5]

Three solver-interface descriptions also differ. Appendix C's prose initializes with \(q_t/\operatorname{diag}(H_t+\Lambda)\). Algorithm 1 uses \(H_{t-1}+\Lambda\). The main zero-step-to-GLA argument requires \(x_0=q_t\), which is not generally either diagonal initialization. Actual CG0 routing remains unverified. A diagonal initial guess is also not the same as Jacobi-preconditioned CG at every iteration. Finally, Algorithm 1 needs an initial zero-residual return to avoid \(0/0\) when its initial guess is exact. This is a pseudocode guard observation, not a kernel audit.

### 3.1 A finite CG read need not be linear in the query

This is an independent exact-arithmetic example for the Appendix C prose initialization. Take

\[
A=\begin{pmatrix}2&1\\1&2\end{pmatrix},
\qquad x_0=q/2.
\]

One ordinary CG step gives

\[
\widehat x(e_1)=(1/2,-1/4)^\top,
\quad\widehat x(e_2)=(-1/4,1/2)^\top,
\quad\widehat x(e_1+e_2)=(1/3,1/3)^\top.
\]

The first two sum to \((1/4,1/4)^\top\), not the third. This is a valid positive ridge system with \(\Lambda=I\) and \(H\succeq0\). Restricting queries to unit norm does not restore a single linear map, since the CG map here is homogeneous and the normalized diagonal query gives the same contradiction.

Thus the finite algorithm is an adaptive approximation to a linear ridge read. It need not itself be representable as multiplication by a query-independent fast-weight matrix. This distinction concerns the solver, before the surrounding nonlinear network.

### 3.2 Approximate implicit differentiation is disclosed by the authors

For the ideal solve, define upstream output derivative \(e_t\) and
\(y_t=A_t^{-1}G_t^\top e_t\). Differentiation gives

\[
dL=e_t^\top(dG_t)x_t+y_t^\top dq_t-y_t^\top(dA_t)x_t.
\]

Replacing \(x_t,y_t\) by finite CG approximations approximates this implicit derivative. It does not generally differentiate the actual truncated program. Appendix J explicitly acknowledges the accuracy assumption and proposes backpropagating through unrolled CG as future work.

A bounded example makes the difference concrete. Let

\[
A(a)=\begin{pmatrix}2&a\\a&2\end{pmatrix},
\quad q=e_1,\quad x_0=(1/2,0)^\top.
\]

For \(0<|a|<1\), one CG step gives \(\widehat x=(1/2,-a/4)^\top\). The actual derivative of its first coordinate is zero. Inserting this forward approximation and an exact adjoint into the implicit derivative gives \(a/(4-a^2)\), which equals \(2/15\) at \(a=1/2\). Using the same one-step approximation for the adjoint gives \(a/4=1/8\). All differ from zero, while \(H=A-I\) remains positive definite near this parameter. This does not refute sufficiently converged implicit differentiation.

## 4. Local backward repairs

With input gates absorbed, the correct derivatives of the ideal solve are

\[
\nabla_{v_s}L=\sum_{t\ge s}\zeta_{ts}e_t(k_s^\top x_t),
\]

\[
\nabla_{k_s}L=\sum_{t\ge s}\zeta_{ts}
[x_t(e_t^\top v_s)-y_t(x_t^\top k_s)-x_t(y_t^\top k_s)],
\]

\[
\partial_{\gamma_s}L=\sum_{t\ge s}\zeta_{ts}
[e_t^\top G_{s-1}x_t-y_t^\top H_{s-1}x_t].
\]

Appendix D p.27 prints \(y_t\) instead of \(e_t\) in the first key term, and the first gate term has reversed orientations without the needed transpose. These fail dimensionally when key/value widths differ and can fail numerically when they agree.

For a unit-key example, set \(t=1,\Lambda=I,k=e_1,q=e_2,v=e=e_1\). Then \(x=e_2,y=e_1/2\). The correct key gradient is \(e_2/2\), while the printed expression gives zero. Along the unit circle \(k(\theta)=(\cos\theta,\sin\theta)\), direct evaluation gives \(L(\theta)=\sin\theta/2\). Its derivative at zero is \(1/2\), so key normalization does not remove the discrepancy.

The later gate-gradient trace expansion inherits the orientation issue. For \(F_s=\sum_{t\ge s}\zeta_{ts}e_tx_t^\top\), the carry contraction is \(\operatorname{tr}(G_{s-1}^\top F_s)\). The corresponding expanded scalar factors are \((e_t^\top v_p)(k_p^\top x_t)\). These repairs follow directly from the displayed differential. They do not establish what derivatives the unreplayed kernel actually uses.

## 5. Comparison with KRA: distinct meanings of forgetting

Compare the fully read [KRA note](CHEN-2026-KERNEL-RIDGE-ATTENTION.md), based on [Chen et al. 2611.23896v1](https://arxiv.org/abs/2611.23896v1). This comparison is an independent algebraic deduction about the two specified operators.

For Mesa set \(P=(H+\Lambda)^{-1}\) and \(\Theta=(GP)^\top\). Before the next observation, discounting old statistics gives

\[
\bar P_{\rm Mesa}=[\gamma P^{-1}+(1-\gamma)\Lambda]^{-1},
\qquad
\bar\Theta_{\rm Mesa}=\bar P_{\rm Mesa}\gamma P^{-1}\Theta.
\]

KRA instead uses

\[
\bar P_{\rm KRA}=\delta^2P+(1-\delta^2)\lambda^{-1}I,
\qquad \bar\Theta_{\rm KRA}=\delta\Theta.
\]

Mesa discounts evidence about a current static coefficient while preserving a fixed ridge. KRA propagates a dynamic coefficient under an OU transition and process noise. In scalar form with matched ridge, Mesa's covariance is \(p/[\gamma+(1-\gamma)\lambda p]\), whereas KRA's is affine in \(p\). Nontrivial forgetting generally cannot be identified by setting \(\gamma=\delta\) or \(\gamma=\delta^2\).

For a concrete common-data comparison, take scalar unit keys/queries, ridge one, unit input weights, \(v_1=1,v_2=0\), and second-step retention parameter numerically equal to \(1/2\) in each model. Mesa reads \(1/5\). KRA reads \(2/15\). The difference is in the objective, not solver approximation. With no forgetting, identical features, ridge, observation weighting and inclusive-read convention, both reduce to the same static ridge regression.

The exact Mesa precision recursion is

\[
A_t=\gamma_tA_{t-1}+(1-\gamma_t)\Lambda+\beta_tk_tk_t^\top.
\]

This explains why merely initializing a standard discounted RLS precision with \(\Lambda\) would forget the regularizer. Appendix H's old-Mesa comparison concerns that simpler recursion. It is not an impossibility theorem for every recursive implementation with a fixed ridge.

## 6. Evidence, resources and negative results

The paper uses a common decoder backbone, GPT-2 tokenizer, common data order, training context 2,048 and separately selected learning rates. Nominal sizes are about 140M, 440M and 940M, also labeled 145M/400M/1B in plots. Training budgets are 15B and 50B tokens. All heads use key size 128. Most recurrent controls use scalar per-head gates, unlike some native architectures. LRU width is adjusted to match parameters. These controls isolate sequence-layer differences in this backbone, rather than comparing every architecture at its independently optimized native design. [Section 4, Appendices E,G,J]

For the 1B/50B setting:

| Reported metric | Mesa | Gated DeltaNet | Transformer |
|---|---:|---:|---:|
| SlimPajama perplexity | 10.83 | 10.89 | 10.86 |
| Six-dataset arithmetic mean of perplexities | 13.79 | 13.87 | 13.79 |
| Global reasoning accuracy | 45.03% | 44.84% | 45.54% |
| In-context recall accuracy | 41.79% | 39.54% | 52.27% |
| 100-shot word scrambling accuracy | 10.10% | 8.90% | 6.98% |
| 50-shot translation BLEU-sb | 8.17 | 8.53 | 13.61 |

[Main Tables 2–3 and Appendix L.] The average of dataset perplexities is not pooled-token perplexity. A 0.19-point reasoning difference has no reported cross-training-run uncertainty. The main language-model training seeds and repeated-training count are not specified, so this note does not infer a single seed.

The position-conditioned analysis is valuable. In these models, recurrent layers gain on early tokens while full attention overtakes later. Mesa/Hawk-Mesa extend the early advantage beyond about 512 positions in the main setting. Equal aggregate perplexity can therefore coexist with different use of available context. Packing shorter documents into fixed-length sequences is also acknowledged to bias training/evaluation toward short sequences. [Figures 3,10–12, Appendix G.1]

The local/global benchmark split is an empirical classification using short-window attention controls in these sizes and data, not a universal theorem about task dependency. The paper itself expects the partition to change with larger models or other data. Recall evaluation truncates prompts to 2,000 tokens and checks case-insensitive target inclusion in up to 48 greedily generated tokens. Matching a short-window model on an aggregate does not prove all examples can be solved locally. [Appendices L,N]

Length extrapolation is mixed. At 32K, Mesa is broadly competitive with Gated DeltaNet and SWA-1024 is strong. Failures of the fixed-2K-trained transformer occur under its particular RoPE/extrapolation setup. They are not architecture-wide impossibility evidence. In NIAH at 4,096 tokens, Mesa scores 95.1±3.9% on noise but 17.9±9.0% on essays. GLA reaches 41.4±26.9% and Hawk-Mesa 55.5±28.5% on essays. These deviations are across nine key/value type combinations, with 1,000 examples per combination, not training-seed confidence intervals. [Figure 4, Tables 11–12,19]

Word-scrambling deviations are over ten random few-shot prefixes. Only two of five tasks are tabulated because the other three stay near zero at these scales. The stronger scores do not establish unrestricted algorithmic generalization. Translation still favors full attention, and Mesa is not the strongest recurrent variant in every setting. MAD's 76.1% aggregate versus transformer's 75.8% and RegBench's close curves are task-specific synthetic evidence. [Appendices F,K,L]

### Solver and timing evidence

Default models use fixed 30 CG iterations in training and evaluation. The main inference ablation reports approximately matched results at relative residual tolerance \(10^{-4}\), averaging about nine iterations. This is not automatically a 30/9 end-to-end speedup. Fixed low iteration counts hurt later positions more, whereas residual stopping distributes work differently. Figure 13 also changes training iteration counts on 400M/15B models. Training with five steps degrades validation loss, and evaluating that model at 30 steps does not erase all of the gap. [Figures 5,7,13]

CG arithmetic inside the Pallas kernel is FP32, with BF16 activations elsewhere. Lower-precision CG is left largely unexplored. Figure 2 compares single-layer TPU training and whole-model H100 training throughput. Figure 6 reports whole-model autoregressive throughput on H100 and TPUv5, averaged over five measurements. Hardware, batch size, generation length and precision matter. GLA is faster in these plots and Mesa spends more FLOPs even where wall-clock throughput is competitive. Timing repetitions do not supply model-quality uncertainty.

### State tracking is a separate experimental variant

Appendix I changes the forget gate to allow negative values and uses very large regularization, initialized at 50 and lower-bounded by 49. The resulting read approaches a rescaled GLA read. A roughly 1M-parameter two-layer model trained on parity strings of length 40 extrapolates accurately to length 256 with negative gates, while the positive-only comparator falls toward chance. [Figure 8]

Negative gates can make \(H_t\) indefinite and destroy the nonnegative weighted-regression interpretation. A sufficiently dominant ridge may retain an invertible positive system on the tested range, but the paper does not establish that uniformly over arbitrary histories. The authors explicitly describe this as falling back toward GLA and leave state tracking while retaining useful Mesa computation unresolved. This is not evidence that the default positive-gate ridge layer learns arbitrary finite-state machines.

### Unresolved recipe and artifact details

The 50B learning-rate grid prints 0.0085, whereas the selected-rate table uses 0.00085 in several entries. Small/50B Transformer is listed at 0.003, outside that stated grid. The word-scrambling caption says best 50-shot while its table uses 100-shot. These remain source conflicts. No benchmark-contamination audit or cross-training-run variance was located in the read paper.

The acquired TeX package provides scientific text, figures, tables and pseudocode. Its reproducibility statement promises future Triton/Colab release and links FLA/recurrentgemma, but this package does not contain complete training code, checkpoints, token manifests or a pinned implementation sufficient for replay. Current external release fulfillment was not audited. No claim is made that public code is absent today.

## 7. What is retained for future theoretical work

The supported tools are the weighted sufficient-statistic objective, query-only SPD solve, corrected chunk algebra, exact-solve adjoint and explicit residual-to-readout accounting. The finite-CG examples show that truncating an optimizer can change both the function class and the derivative interface. The KRA comparison separates static evidence discounting from dynamic latent-coefficient filtering.

These are independent architecture results and limitations. No FP core definition, architecture, objective, experiment or learning rule is proposed or changed. This paper supplies neither finite-bit state-acquisition prices nor a theorem that its learned representation is the minimal predictive state. Any later use must retain the chosen features, objective, regularizer, solver accuracy and physical resource model explicitly.
