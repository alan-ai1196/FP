# Nielsen et al. 2026 — logit geometry, conditioned representation recovery and the cost of rare labels

Pro-D. Completed 2026-11-26, Asia/Shanghai. Independent literature research, not an FP architecture proposal.

## Edition, sources and actual coverage

Beatrix M. G. Nielsen, Emanuele Marconato, Luigi Gresele, Andrea Dittadi and Simon Buchholz, **Logit Distance Bounds Representational Similarity**, ICML 2026, PMLR 306:93144–93190, 47 pages.

- [Official conference record](https://proceedings.mlr.press/v306/nielsen26a.html).
- [Official final PDF](https://raw.githubusercontent.com/mlresearch/v306/main/assets/nielsen26a/nielsen26a.pdf), the edition used for every page and equation reference below.
- [arXiv 2602.15438v3](https://arxiv.org/abs/2602.15438v3), revised June 24, 2026 at 10:39:19 UTC. The inspected history has v1 on February 17 and v2 on February 18. [Versioned PDF](https://arxiv.org/pdf/2602.15438v3) and [TeX source](https://arxiv.org/src/2602.15438v3).
- [Author implementation](https://github.com/bemigini/logit-distance-bounds-rep-sim), inspected only at commit [`3a6e6f8decf5c29a95b456fbd4c07b0c2605e7e9`](https://github.com/bemigini/logit-distance-bounds-rep-sim/tree/3a6e6f8decf5c29a95b456fbd4c07b0c2605e7e9), dated May 27, 2026. This code snapshot is not authenticated as the exact producer of the final paper's tables.
- Official PDF SHA256 `bc3af62c233f73aff78d53393dec59634661631826b6b2c900d433484159d281`.

**Fully read:** all 47 official pages, main §§1–6, Appendices A–L, every proof and displayed formula, eight numbered figures, four numbered tables, seven scientific footnotes, impact statement, acknowledgments and all 78 printed references. The root reader read the PDF text in continuous blocks and visually inspected original pages 2, 8, 9, 34, 35, 38, 39, 40, 41, 43, 45 and 47. These pages cover every numbered figure and table, as well as selected formulas whose extraction needed checking. Targeted TeX passages were read for matrix dimensions, quantifiers and table values. This is complete official-PDF reading, not a claim of reading every raw source line or every cited work.

The v3 source has one 4854-line main TeX file. Mechanical removal of inactive comment environments and ordinary comments leaves a 3200-line numbered reading copy. The eight printed figures use eleven active image assets. Seven additional CIFAR plots occur only in an inactive source block and are not counted as printed or read figures. Official and v3 scientific text agree under the recorded normalization apart from cross-reference type names, appendix wording, watermark, line wrapping and two pieces of text moved across footnotes. The official edition corrects several v3 references that called assumptions, definitions or lemmas theorems. The conflicting Synth table values discussed below occur in both editions. Only the official edition receives a completed-reading count.

No withdrawal or substantive correction was identified in the inspected primary records. No explicit AI-assistance disclosure was found in the read manuscript. Actual assistance is undetermined. This is peer-reviewed author research, not an official OpenAI or Anthropic release. No training, benchmark reproduction, formal proof replay or whole-repository audit was performed.

## 1. Assessment

The useful contribution is a quantitative separation of **predictive error, output geometry, linear representation similarity and preservation of an already available concept**. The paper gives valid conditional tools based on centered logits, regression residuals, canonical correlations and the spectrum of the reference model's logits. Its generalization and optimization scope is limited. These are mostly comparisons of supplied population models under a common input distribution, not sample-complexity or state-discovery theorems.

A bounded independent calculation strengthens the paper's KL comparison. For finite categorical distributions whose probabilities at both endpoints are at least the same positive value \(\tau\),

\[
\boxed{4d_{\rm KL}\le d_{\rm logit}^2\le\frac{2}{\tau}d_{\rm KL}.}
\]

The original weaker bound remains valid. The extra logarithmic factor is unnecessary for centered logits. The \(\tau^{-1}\) dependence remains necessary, and the constant \(2/\tau\) is a sharp uniform upper multiplier when there are at least three classes and \(\tau<1/k\). This is a source-grounded independent deduction, not a claim of publication priority.

The CCA and spectral-tail tools are especially useful because they expose an observable conditioning parameter that is invariant under the model's linear change of representation. By contrast, the paper's \(d_{\rm rep}\) has the desired zero set but remains asymmetric and dependent on representation units. Its numerical value is not a metric on the quotient by all invertible linear maps.

The empirical comparison supports a narrower qualitative observation about the tested distillation setups. Exact \(d_{\rm rep}\) magnitudes and uncertainty require caution because the final tables disagree, the linked implementation has a normalization error in its newer distance routine, and the printed aggregation formula differs from the code. These issues do not refute the population theorems or automatically invalidate the separately computed CCA and concept accuracies.

## 2. Objects and observation interface

Inputs have a fixed distribution \(P_X\), labels form a finite set of size \(k\), and a model is a pair

\[
f:\mathcal X\to\mathbb R^m,
\qquad g:\mathcal Y\to\mathbb R^m,
\qquad
p_{f,g}(y\mid x)=\frac{\exp(f(x)^\top g(y))}{\sum_z\exp(f(x)^\top g(z))}.
\]

Only the last embedding and unembedding before softmax are studied. Arbitrary earlier network layers are not identified. Autoregressive models fit this interface when \(x\) denotes a context, but the paper does not prove a sequential-state or trajectory-distribution theorem from that observation alone.

Let \(L=[g(y_1),\ldots,g(y_k)]\in\mathbb R^{m\times k}\), center its columns so that \(L\mathbf1=0\), and write \(u(x)=L^\top f(x)\). Then \(\mathbf1^\top u(x)=0\). Translating every unembedding by the same vector leaves the predictive distribution unchanged. Centering fixes that additive logit freedom without removing the invertible linear freedom

\[
(f,g)\longmapsto(Af,A^{-\top}g).
\]

Assumption 2.1 requires the embeddings and the pivot-shifted unembeddings to span \(\mathbb R^m\). It implies \(k\ge m+1\). This is a rank condition, not a consequence of having many labels alone. Under it, equality of the entire conditional distribution identifies the pair up to an invertible linear transformation, with the transformations of embedding and unembedding constrained to be inverse transposes. Theorem 2.2 and Appendix C prove this by canceling the log partition against a pivot label and solving an invertible system of log odds.

For pivot \(i\) and an \(m\)-element subset \(J\) of the other labels, put

\[
L_{i,J}=[g(y_j)-g(y_i)]_{j\in J},
\qquad A_{i,J}=L_{i,J}^{-\top}L_{i,J}'{}^\top.
\]

When the models agree, the same invertible \(A\) is obtained from every invertible pivot system. A perfectly correlated embedding alone does not ensure the required relation between both model components. Appendix G keeps embeddings equal while swapping pairs of unembeddings and concentrating probabilities on shared maximizers. Appendix H uses inconsistent rotations of embeddings and unembeddings. These examples separate individual CCA scores from equality of predictive distributions.

All expectation-based zero-distance statements should be read modulo \(P_X\)-null sets. Appendix D states this explicitly. Pointwise conclusions outside the observed input support require additional assumptions. For CCA, centering the random variables also makes the statistic invariant under translations, so CCA equal to one ordinarily gives an affine relation of the original variables, or a linear relation after centering.

## 3. Centered logits and the probability boundary

Define \(P_k=I-\mathbf1\mathbf1^\top/k\). The centered logit map is determined by the probabilities:

\[
u(x)=P_k\log p(\cdot\mid x),
\qquad
d_{\rm logit}^2(p,q)
=\mathbb E_X\|P_k(\log p-\log q)\|_2^2.
\]

At each input this is the squared Aitchison distance on the strictly positive simplex. The unsquared population quantity is an extended metric on conditional distributions modulo null sets. The square itself is not a metric. Appendix D proves the triangle inequality using Cauchy–Schwarz in the input expectation. The printed ratios of logarithms in Eqs. 103 and 105 should be log ratios as in Eq. 101 and the preceding log-odds derivation.

Unlike KL, this distance gives every label a place in the Euclidean log-ratio geometry, including labels of tiny predictive probability. It therefore measures a stronger property than ordinary average predictive risk. Matching it requires access to accurate probabilities or logits, or a separate procedure that estimates them. A stream of sampled labels does not automatically provide equally precise rare-label log odds.

### Author results

Theorem 3.3, p4, establishes

\[
2d_{\rm KL}(p,q)\le d_{\rm logit}^2(p,q)
\le\frac{4\log^2\tau}{\tau}d_{\rm KL}(p,q),
\]

where the upper bound assumes both models satisfy \(p_y(x),q_y(x)\ge\tau>0\) almost everywhere and uses \(\tau<1/3\). Here \(d_{\rm KL}=\mathbb E_X\operatorname{KL}(p_x\|q_x)\), with natural logarithms. The lower bound has no uniform probability-floor requirement. Appendix E.1's equivalence with bounded embeddings uses a fixed full-span output head. It is not a uniform bound on representation coordinates over the full linear equivalence class.

Lemma E.4 gives a different pointwise statement when only the **first KL argument** has a probability floor:

\[
\|\log p-\log q\|_2^2
\le\frac{12\log^2\tau}{\tau}\operatorname{KL}(p\|q)
+\frac9{\tau^2}\operatorname{KL}(p\|q)^2.
\]

Integrating this inequality requires a second moment of the conditional KL. A small mean KL is insufficient. Remark E.8 recognizes this distinction. In teacher-to-student KL, a probability floor on the student alone is not the premise of this particular one-sided lemma. Direction and moment assumptions should be retained.

### Independent improvement with a short proof

Fix an input. Let \(p=\operatorname{softmax}(u)\), \(q=\operatorname{softmax}(v)\), with centered logits, and put \(h=v-u\). For \(F(w)=\log\sum_i e^{w_i}\),

\[
\operatorname{KL}(p\|q)
=\int_0^1(1-s)h^\top H_sh\,ds,
\qquad H_s=\operatorname{diag}(p_s)-p_sp_s^\top,
\]

where

\[
p_{s,i}=\frac{p_i^{1-s}q_i^s}{\sum_jp_j^{1-s}q_j^s}.
\]

Hölder gives a denominator at most one. If both endpoints have every probability at least \(\tau\), then every intermediate probability is also at least \(\tau\). For \(a\in\mathbf1^\perp\),

\[
a^\top H_sa
=\min_c\sum_i p_{s,i}(a_i-c)^2
\ge\tau\min_c\sum_i(a_i-c)^2
=\tau\|a\|_2^2.
\]

The maximum Hessian eigenvalue is at most \(1/2\), since each Gershgorin upper endpoint is \(2p_{s,i}(1-p_{s,i})\le1/2\). Thus

\[
\frac\tau2\|h\|_2^2
\le\operatorname{KL}(p\|q)
\le\frac14\|h\|_2^2.
\]

Integration over \(P_X\) proves the boxed comparison in §1. The upper bound needs no representation-rank assumption and holds for any feasible \(\tau\le1/k\). It does require the same floor for both endpoints. The lower bound remains valid without that floor.

**Sharpness.** For \(k\ge3\), \(\tau<1/k\), choose

\[
p=\left(a,a,\frac{1-2a}{k-2},\ldots,\frac{1-2a}{k-2}\right)
\]

with every component strictly above \(\tau\), and set \(v=u+t(1,-1,0,\ldots,0)\). For sufficiently small \(t\), both endpoints remain admissible. Taylor expansion gives \(\operatorname{KL}(p\|q)=at^2+o(t^2)\), whereas \(\|v-u\|^2=2t^2\). Taking \(t\to0\) and then \(a\downarrow\tau\) shows that \(2/\tau\) cannot be reduced as a uniform multiplier. At \(\tau=1/k\), only the uniform distribution is admissible and the comparison is trivial. The universal coefficient four on the other side is approached by a small perturbation of a uniform binary distribution.

The author's simpler Remark E.3 example also survives centering. With \(p=(2\tau,1-2\tau)\) and \(q=(\tau,1-\tau)\),

\[
\|P_2(\log p-\log q)\|^2
=\frac12\left[\log\frac{2(1-\tau)}{1-2\tau}\right]^2
\longrightarrow\frac{(\log2)^2}{2},
\]

while \(\operatorname{KL}(p\|q)=(2\log2-1)\tau+O(\tau^2)\). The usual Jensen–Shannon divergence is also \(\Theta(\tau)\), with coefficient \(\log2-\tfrac32\log(3/2)>0\). This establishes the unavoidable reciprocal-probability order, not a necessary logarithmic factor. The paper itself only claims tightness up to logarithms.

## 4. Representation similarity and the observable spectrum

Appendix F first works with **uncentered second moments**. Let

\[
M_u=\mathbb E[uu^\top]=L^\top M_fL,
\qquad M_f=\mathbb E[ff^\top].
\]

Assume \(L,M_f\) and their student counterparts have full ranks \(m,m'\), and finite second moments. Let \(\mu_1\ge\cdots\ge\mu_m>0\) be the nonzero eigenvalues of \(M_u\). For the unembedding canonical correlations \(\rho_i\), and separately for moment-based embedding correlations \(\widetilde\rho_i\), Theorem F.1 gives

\[
\sum_{i=1}^m\mu_i(1-\rho_i^2)\le d_{\rm logit}^2,
\qquad
\sum_{i=1}^m\mu_i(1-\widetilde\rho_i^2)\le d_{\rm logit}^2,
\]

with zero padding beyond \(m'\). The proof regresses one representation on the other, decomposes the output error into orthogonal residual terms, identifies the residual's whitened eigenvalues with \(1-\rho_i^2\), and applies the lower von Neumann trace inequality. Pairing the decreasing \(\mu_i\) with increasing \(1-\rho_i^2\) matters.

For ordinary covariance-based CCA, Theorem F.14 instead requires full-rank embedding covariances. With \(\mu_m\) now the smallest positive eigenvalue of \(\operatorname{Cov}(u)\), Theorem 3.4 for equal widths gives

\[
\operatorname{mCCA}(f,f')\ge1-\frac{d_{\rm logit}^2}{m\mu_m},
\]

and the same bound for the unembeddings. The full-rank student covariance assumption is explicit in the appendix and should accompany use of the inverse-based CCA definition. A span condition on a pointwise image does not by itself ensure all of these covariance assumptions. Appendix F acknowledges the need for regularity and separates possible pseudoinverse extensions.

Both output logits and their spectrum are invariant under \((f,g)\mapsto(Af,A^{-\top}g)\). Consequently, the independent KL improvement yields the conditional bound

\[
\operatorname{mCCA}(f,f')\ge1-
\frac{2d_{\rm KL}}{m\tau\mu_m}.
\]

This is useful only at the relevant probability and spectral scale. A fixed small KL does not guarantee high CCA uniformly over nearly collapsed logit spectra. Theorem F.13 also gives the dimension obstruction

\[
m'<m\quad\Longrightarrow\quad
d_{\rm logit}^2\ge\sum_{i=m'+1}^m\mu_i,
\]

using the **second-moment** spectrum in that theorem. Under the two-sided probability floor, an immediate independent consequence is

\[
d_{\rm KL}\ge\frac\tau2\sum_{i=m'+1}^m\mu_i.
\]

This concerns a linear output bottleneck with access to \(f'(x)\). It is not a bound on the number of physical recurrent states, persistent bits, or the cost of computing those features.

**Local transcription repairs.** On p34, Eq. 215 should have \(I_m-QQ^\top\), where \(Q=M_f^{-1/2}M_{f,f'}M_{f'}^{-1/2}\in\mathbb R^{m\times m'}\). The printed \(I_m-Q^\top Q\) has incompatible dimensions when \(m\ne m'\). The residual identity immediately above gives the correct product and supports the stated eigenvalue relation. On p35, Lemma F.10 and Remark F.11 write \(\widetilde B^\top\widetilde B\), whereas the proof and Eqs. 224–227 control \(B^\top\widetilde B\). For identical outputs with \(f'=f/2\), \(g'=2g\), the regressions are \(\widetilde B=2I\), \(B=I/2\). Thus \(\widetilde B^\top\widetilde B=4I\), while \(B^\top\widetilde B=I\). These are bounded corrections to printed formulas. They do not refute the intended CCA bounds.

## 5. The joint dissimilarity and its coordinate dependence

Assumption 3.5 requires **every** pivot-shifted \(m\)-label matrix to be invertible, as well as embedding span. This is stronger than existence of one usable basis. Writing \(J_*=\binom{k-1}{m}\), the proposed quantity is

\[
d_{\rm rep}^2((f,g),(f',g'))
=\frac1{kJ_*}\sum_i\sum_J
\mathbb E\|f-A_{i,J}f'\|_2^2.
\]

Its zero set agrees with exact predictive equivalence under the assumptions. Pairwise log-odds identities and singular-value bounds give, with \(C=\sqrt{2m/(k-1)}\),

\[
\frac{C}{\sigma_{\max}}d_{\rm logit}
\le d_{\rm rep}
\le\frac{C}{\sigma_{\min}}d_{\rm logit},
\]

where the extrema range over all pivot matrices of the **first model**. The combinatorial normalization follows because each non-pivot label occurs in \(\binom{k-2}{m-1}\) subsets. The independent KL comparison therefore gives

\[
d_{\rm rep}\le
\frac1{\sigma_{\min}}
\sqrt{\frac{4m}{(k-1)\tau}d_{\rm KL}}.
\]

The quantity is not invariant under changing only the first model's representation units. Replacing \(f\) by \(sf\) and \(g\) by \(g/s\), with \(s>0\), preserves the predictions but multiplies \(d_{\rm rep}\) by \(s\). The corresponding \(\sigma_{\min}\) is divided by \(s\), so the theorem remains consistent. Reparameterizing the second model cancels inside \(A_{i,J}f'\). This exposes the asymmetry. Zero-set compatibility with an equivalence relation is weaker than a coordinate-invariant distance between its classes.

Sampling label subsets also introduces a separate estimation issue. Seeing every individual label does not ensure an accurate average over all bases. A rare nearly singular basis can dominate \(\|f-A_{i,J}f'\|^2\) while being missed in a short random sample. Appendix L.4's label-coverage argument is therefore not a concentration guarantee for \(d_{\rm rep}\). Quantitative control would need bounds or tail assumptions on the sampled inverse-conditioned terms.

## 6. Concept preservation and the limits of the learning claim

Definition 4.2 assumes an existing concept distribution

\[
h(c\mid x)=\operatorname{softmax}(W^\top f(x)+b)_c.
\]

Appendix J explicitly uses a full-row-rank \(L\) to represent \(W=LA\). Theorem 4.3 bounds the best student linear probe's population KL by \(\tfrac12\|A\|_{\rm op}^2d_{\rm logit}^2\). A transparent proof fixes a single probe \(W'=L'A\), \(b'=b\) for every input and then integrates the pointwise softmax bound. This avoids any interchange of minimization and expectation suggested by the printed intermediate notation. Using the stronger Hessian upper bound above improves the coefficient from \(1/2\) to \(1/4\).

The needed condition is that the relevant concept directions lie in the output-head span, or that a full-rank head makes that automatic. The guarantee is conditional on the finite coefficient norm \(\|A\|\). It does not learn the concepts, discover semantic variables or prove that a finite-sample linear probe reaches the population infimum. It also does not establish causal steerability or transfer to arbitrary hidden layers. The paper leaves other linear properties to future work.

Proposition 4.1 controls squared logit distance by the population \(L_1\) logit loss under a uniform two-sided probability floor:

\[
d_{\rm logit}^2\le2|\log\tau|\,\mathbb E\|u-u'\|_1.
\]

This is a conditional inequality between achieved losses. Decreasing an \(L_1\) objective does not by itself prove monotone decrease of the actual squared loss, optimization convergence, or out-of-sample control. Without a common envelope, a small first moment can coexist with a large second moment.

## 7. Experiments, quantitative discrepancies and scoped implementation evidence

### Actual intervention

The comparisons use the same teacher outputs to train students with teacher-to-student KL, squared logit loss, or absolute logit loss. The paper does not claim to invent logit matching and cites earlier distillation work.

| Dataset | Reported setup and scope |
|---|---|
| Synth | Seven classes on interleaved spirals, 14k training and 7k each validation/test points. Two hidden layers of width 512, a two-dimensional final representation, 1500 teacher epochs and 250 student epochs. |
| CIFAR100 | ImageNet-initialized ResNet50 teacher, ResNet18 students, 50-dimensional representations. The teacher trains ten epochs and students fifty. Original 50k/10k train/test split, no validation split. |
| SUB | Generated bird data with 33 class labels and 33 concept values. DINOv2 provides fixed 768-dimensional inputs to a shallow network. Teacher and student representations have dimension ten. Both class and concept annotations supervise the teacher. Reported splits are approximately 21.5k/5.3k/11.5k. |

The main tables use five teachers and five students per teacher. Figure 8's width ablation instead uses one teacher and five student runs. It computes CCA over the student's most aligned \(m'\)-dimensional subspace. Its near-one CCA at \(m'=2\) coexists with almost random concept accuracy. This is compatible with missing most of the ten-dimensional teacher representation, and should not be read as full preservation.

CIFAR has moderate reported task accuracy, about .54 for the teacher and .48–.493 for students. In SUB, KL students have class accuracy about .929 but concept accuracy .055, while the two logit methods have concept accuracies .747 and .724. The concept intervention is supervised at the teacher, not spontaneous semantic emergence. The reported comparison does not establish that every well-tuned temperature-scaled KL distillation method has the same failure. No language-model experiment is included. The paper also explicitly recognizes that rare-label geometry may carry noise rather than useful concepts.

### Final-source conflicts

The original PDF and v3 TeX both contain the following Synth discrepancy:

| Method | Table 1, p8, reported \(d_{\rm rep}\) | Table 3, p47, reported \(d_{\rm rep}\) |
|---|---:|---:|
| KL | \(49.5\pm2.9\) | \(6.07\pm.31\) |
| \(L_1\) | \(1.44\pm.04\) | \(.169\pm.004\) |
| \(L_2\) | \(.20\pm.01\) | \(.204\pm.005\) |

This changes which logit method is best on that metric, not just a decimal place. The CIFAR point estimates are consistent across the two tables. SUB Tables 2 and 4 have broadly consistent point estimates but, for example, report KL-student accuracy uncertainties .01 versus .001. No authenticated table-generation provenance resolves these differences. Do not select a preferred table or apply a guessed rescaling.

### What the pinned code actually computes

The bounded code inspection follows only the relevant losses, representation metric, aggregation, model heads and evaluation calls. Primary file links refer to the exact May 27 commit.

In [`representation_dissimilarity.py`](https://github.com/bemigini/logit-distance-bounds-rep-sim/blob/3a6e6f8decf5c29a95b456fbd4c07b0c2605e7e9/dissimilarities/representation_dissimilarity.py), let \(n\) be the number of inputs and \(M=PC\) the number of sampled pivot/subset combinations. For each combination the function appends

\[
\frac1{nM}\sum_{r=1}^n\|f_1(x_r)-A f_2(x_r)\|^2,
\]

then takes the **mean over the \(M\) appended values**. It therefore returns the ordinary Monte Carlo estimate of \(d_{\rm rep}^2\) divided by another \(M\). This is a direct algebraic normalization error, not a stochastic estimation concern. It uses a direct matrix inverse with no ridge term in this routine. The wrapper sets model 1 to the student and model 2 to the teacher. Since the metric is asymmetric, that orientation matters.

The configured counts are \(M=105\) for Synth, \(20000\) for CIFAR and \(8250\) for SUB. For Synth, drawing fifteen two-label subsets independently at each pivot does not enumerate the fifteen possible subsets. Subsets can repeat. Thus the inspected routine also differs from the manuscript's statement that all Synth combinations are evaluated. Taking a square root downstream changes the extra factor to \(\sqrt M\), but does not remove it. No claim is made that every printed table was produced by this path.

The repository also retains an older Synth evaluation path through `evaluation/syn_evaluate_standard.py` and `utils/metrics.py`. That path averages unsquared Euclidean residuals in the opposite teacher-first direction. Its KL helper computes student-to-teacher KL with a small probability smoothing term. These differences were found by a bounded helper inspection, not by execution. They are a provenance complication, not a license to infer which table is correct. The current code and the final tables must remain distinct evidence objects. The inspected public tree and release metadata did not supply checkpoints or per-run result assets linking the tables to a particular path. The README's Zenodo archive was not authenticated in this check.

### Training does not implement the declared centering in this snapshot

The primary [`losses.py`](https://github.com/bemigini/logit-distance-bounds-rep-sim/blob/3a6e6f8decf5c29a95b456fbd4c07b0c2605e7e9/utils/losses.py), model heads, teacher-logit caching and [`train.py`](https://github.com/bemigini/logit-distance-bounds-rep-sim/blob/3a6e6f8decf5c29a95b456fbd4c07b0c2605e7e9/utils/train.py) establish the following actual main-path objectives for batch size \(B\):

| Method | Implemented objective |
|---|---|
| KL | \(B^{-1}\sum_b\operatorname{KL}(p_T(\cdot\mid x_b)\|p_S(\cdot\mid x_b))\), implicit temperature one |
| \(L_1\) | \((Bk)^{-1}\sum_b\|u_T(x_b)-u_S(x_b)\|_1\), raw logits |
| \(L_2\) | \(B^{-1}\sum_b\|u_T(x_b)-u_S(x_b)\|_2^2\), raw logits |

The no-bias linear heads directly return their matrix products. Their Xavier initialization and Adam updates do not force the class weights to sum to zero. No later centering wrapper or update was found in the inspected call path. Thus the code does not implement the manuscript's statement that all experiments fix the unembedding gauge. A no-bias output layer alone does not fix this freedom.

For the squared objective, the distinction is exact:

\[
\|u_T-u_S\|^2
=\|P_k(u_T-u_S)\|^2
+k\left(\overline{u_T-u_S}\right)^2.
\]

The trained loss additionally penalizes a common logit shift that the predictive distribution does not identify. The absolute loss is likewise not invariant under that shift, and its class averaging differs from the paper's sum convention by a fixed factor. The three methods consequently do not share the same numerical gradient scale merely because their nominal learning rates match.

The separate [`distribution_metric.py`](https://github.com/bemigini/logit-distance-bounds-rep-sim/blob/3a6e6f8decf5c29a95b456fbd4c07b0c2605e7e9/dissimilarities/distribution_metric.py) does center unembeddings before evaluating squared logit distance. Thus the inspected code's training and reported distribution metric use different treatments of the additive freedom. Driving raw squared loss small still controls the centered loss by orthogonal projection. This mismatch does not reverse that inequality, but prevents treating the actual optimization as exactly the paper's centered objective.

### Aggregation is not a pooled run standard deviation

Appendix L.4 defines within-teacher student variances \(s_i^2\), weights \(w_i=1/s_i^2\), a weighted mean and an uncertainty \((\sum_iw_i)^{-1/2}\). That uncertainty is not the standard deviation over all student runs and does not include variation of the teacher-specific means.

The pinned [`inverse_variance_weighted_average.py`](https://github.com/bemigini/logit-distance-bounds-rep-sim/blob/3a6e6f8decf5c29a95b456fbd4c07b0c2605e7e9/figures/inverse_variance_weighted_average.py) computes sample variances within teacher groups, then uses \(n_i/s_i^2\) in the denominator. Its returned variance is

\[
\left(\sum_i\frac{n_i}{s_i^2}\right)^{-1},
\]

which differs from Eq. 298 by a factor of five in variance when each teacher has five students. Equal group sizes leave the weighted mean unchanged. This code expression can describe conditional uncertainty under an additional fixed-mean independence model, but it is not a random-teacher marginal standard deviation. Neither the written formula nor the inspected function accounts for between-teacher heterogeneity. The function has no explicit zero-variance guard. The reported uncertainty should not be treated as a paired confidence interval for a method difference.

All three losses share the main training loop. It ignores the returned validation loader, periodically evaluates train and test metrics, and saves the final-epoch model. The inspected loop does not implement best-validation checkpoint selection or early stopping. CIFAR's final plotting configuration uses epoch 49 of a fifty-epoch run. Synth and SUB can supply distinct validation loaders, but this loop does not use them for checkpoint choice. Periodic test evaluation alone does not establish test-based model selection. External tuning and the exact final table-selection process remain unknown. No numerical retraining or corrected benchmark is supplied.

## 8. Relation to adjacent readings and FP boundary

The closest preceding source is [Nielsen et al., NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/hash/93fce71def4e3cf418918805455d436f-Abstract-Conference.html), **When Does Closeness in Distribution Imply Representational Similarity? An Identifiability Perspective**, with [2506.03784v2](https://arxiv.org/abs/2506.03784v2). It was screened first, then the newer 2026 work took priority. Actual root coverage of the 2025 source is its metadata, abstract, official main text through p5 and the beginning of p6, plus its author README. Its remaining proofs, experiments and appendices are unread. A metadata helper compared the 54-page official edition to the 53-page v2 and found a substantive CCA whitening-formula correction in the official Appendix D.2. The 2026 institutional metadata date is not a new 2026 scientific version. Do not mark the 2025 paper fully read or silently equate its two editions.

The current paper's explicit output-head gauge agrees with the obstruction in the [Nelson note](NELSON-2026-STATISTICAL-STRUCTURAL-IDENTIFIABILITY.md). It also provides a useful conditional repair to informal claims that small cross-entropy error uniformly preserves linear concepts. The probability floor, output spectrum and concept coefficient norm are the quantities doing the work. The contrast with [Sevi–Laulainen](SEVI-LAULAINEN-2026-MISSING-SUPPORT.md) is that a literal support kernel is different from a poorly conditioned but nonzero observation direction. Neither paper licenses discarding that distinction.

For FP, the appropriate retained knowledge is conditional mathematics: centered log-ratio geometry, output spectral tails, the coupled linear gauge and the separation between exact identifiability and quantitative stability. The paper does not infer an unknown recursive update rule, identify a physical hidden-state count, charge finite-precision storage, prove sample-efficient acquisition of logits, or show that ordinary gradient learning discovers a state machine. A large output alphabet does not supply the required rank or conditioning by itself. No source-to-FP transfer theorem or core modification is proposed.

## 9. Evidence status

- **Author theory read:** exact linear identifiability, centered-logit metric, original KL comparisons, CCA and spectral-tail bounds, joint dissimilarity bounds and conditional concept preservation.
- **Independent bounded deductions:** the sharpened and sharp KL/logit comparison, its immediate conditioned CCA and width consequences, coordinate dependence of \(d_{\rm rep}\), and the fixed-probe form of the concept argument.
- **Localized corrections:** matrix orientation in Eq. 215 and the mixed regression product in F.10/F.11, with the intended conclusions retained.
- **Source observations:** final table conflicts and exact pinned-code normalization/aggregation differences. No inference that those code paths generated every published number.
- **Not performed:** broad counterexample search, whole-paper certification, proof-assistant verification, empirical reproduction, full code audit or FP integration.

The official final reading is complete. The earlier 2025 source remains partial. Further ordinary selection requires a fresh remote history, request and ownership check.
