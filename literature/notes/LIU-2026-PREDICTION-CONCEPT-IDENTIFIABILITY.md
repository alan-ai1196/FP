# What next-token prediction identifies about latent concepts

## 1. Source, version and completed reading

Yuhang Liu, Dong Gong, Yichao Cai, Erdun Gao, Zhen Zhang, Biwei Huang, Mingming Gong, Anton van den Hengel and Javen Qinfeng Shi, **I Predict Therefore I Am: Is Next Token Prediction Enough to Learn Human-Interpretable Concepts from Data?**, ICLR2026. [Official record](https://proceedings.iclr.cc/paper_files/paper/2026/hash/db7c4a8a0c1bf8b405f21c783bbf9eae-Abstract-Conference.html) · [Official final PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/db7c4a8a0c1bf8b405f21c783bbf9eae-Paper-Conference.pdf) · [arXiv2503.08980v4](https://arxiv.org/abs/2503.08980v4) · [v4 source](https://arxiv.org/src/2503.08980v4) · [Author project](https://sites.google.com/view/yuhangliu/projects/ntp).

Pro-D completed all46official pages on November26,2026, Shanghai. Coverage includes §§1–8, every active proof and formula, AppendicesA–R, both scientific footnotes, all24figures and6tables, declarations and96printed references. Reading used the complete active scientific TeX, the official PDF bibliography on pp11–16, all16figure-bearing official pages and rendered theorem/proof pages5,6,20–25. The figure pages are2,8,9,10,32,35,37–46. The contents page is17. Commented and inactive old proofs were excluded from the final-edition interpretation.

The arXivv4 source archive, dated February28,2026, has85files and11active TeX dependencies. Its24figures use67distinct graphic assets. All are present, although eight paths in Figure23 differ in capitalization from their actual files. No source repair or reproducible compilation is claimed. The bibliography database has113entries, while96active citation keys match the96printed PDF reference destinations. Reading this reference list is not reading those96papers.

Both official and arXivv4 PDFs have46pages. Raw MuPDF text matches on pp2–46, while p1 differs by the arXiv watermark. This establishes scientific-text correspondence at that comparison depth, not byte or pixel identity. The official abstract webpage still says “invertible linear transformation”, whereas the final PDF abstract says “linear transformation”. The final body governs this note. OpenReview revision history was not accessible, and no unseen review or correction is inferred.

| Artifact | SHA256 |
|---|---|
| Official PDF | 9be2f04b9546ed8ba723d66e274533a8bbdb0dacc17c970fc227a4c0ab8c97a1 |
| arXivv4 source archive | 52944886246259385118b83122d6a50bacf233eb4483c41b18d3cbbaa1b6db54 |

This is peer-reviewed author research, not official OpenAI or Anthropic work. AppendixM discloses LLM assistance with grammar, typos and phrasing, and attributes the scientific content to the authors. No training reproduction, formal verification or whole-repository audit was performed.

**Main assessment.** The positive-probability Bayes identity retaining its correction term is useful. The stated conditions do not justify deleting that term, and they do not guarantee that every latent concept is observable in the learned predictive representation. Two finite, strictly positive constructions below establish these separate failures. A valid residual bound and a conditional contrast-space readout result retain useful mathematics without importing the unsupported conclusions.

## 2. The model and the exact identity

The joint latent configuration is \(C=(C^1,\ldots,C^m)\), with \(\ell\) possible configurations. The context \(X\) and next token \(Y\) obey
\[
p(x,y)=\sum_c p(c)p(x\mid c)p(y\mid c),
\qquad X\perp Y\mid C.
\]
The latent concepts may be dependent. Their causal graph is not identified by this factorization. The model assumes that all dependence between the entire context and the next token passes through the supplied finite joint latent variable.

The theoretical predictor has features \(f(x)\in\mathbb R^d\), output embeddings \(g(y)\in\mathbb R^d\), and exact conditional fit
\[
p(y\mid x)=\frac{\exp(f(x)^Tg(y))}{\sum_{y'}\exp(f(x)^Tg(y'))}.
\tag{1}
\]
The proof assumes this equality after invoking sufficient data, capacity and successful optimization. It does not prove a finite-sample generalization bound, convergence of training, or that a given transformer reaches the equality. The discussion concerns the final hidden representation used by this readout.

The Diversity condition supplies anchors \(y_0,\ldots,y_d\) for which
\[
\widehat L=[g(y_1)-g(y_0),\ldots,g(y_d)-g(y_0)]
\]
is invertible. Define
\[
q_j(c)=p(c\mid y_j),\qquad r_j(c\mid x)=p(c\mid x,y_j),
\]
\[
L_{jc}=q_j(c)-q_0(c),\qquad
h_j(x)=\sum_c q_j(c)\log r_j(c\mid x),
\]
\[
b_j=\sum_c q_j(c)\log p(y_j\mid c),\qquad
A=(\widehat L^T)^{-1}L.
\]
Let \(\Delta h=(h_j-h_0)_{j=1}^d\) and \(b=(\widehat L^T)^{-1}(b_j-b_0)_{j=1}^d\). When all quantities in these logarithms are positive and finite, Bayes' rule gives
\[
\boxed{f(x)=A\log p(C\mid x)+b-(\widehat L^T)^{-1}\Delta h(x).}
\tag{2}
\]
This is Theorem3.1 Eq.(5), proved in AppendixD Eqs.(7)–(24), officialpp20–21. For each fixed model, \(A,b\) are constant in \(x\). An asymptotic family indexed by posterior concentration may change these matrices.

A direct derivation is worth retaining. For each \(c\),
\[
\log p(y_j\mid x)=\log p(c\mid x)+\log p(y_j\mid c)-\log r_j(c\mid x).
\]
Average against \(q_j\), subtract the anchor equation, use the exact softmax log odds, then invert \(\widehat L^T\). The weights in \(h_j\) are \(p(c\mid y_j)\), **not** \(p(c\mid x,y_j)\). Thus \(-h_j\) is a cross entropy, rather than the entropy of the concentrating posterior.

Equation(2) relates a chosen latent description and an exactly fitted predictor. It does not compare competing latent data-generating models with the same observed law, establish uniqueness of \(C\), or recover its causal semantics. In particular, \(A\) is a \(d\times\ell\) matrix and always satisfies \(A\mathbf1_\ell=0\). It cannot have a full left inverse on the entire joint-log-probability ambient space.

## 3. What the printed theorem adds

Theorem3.1, p5, adds two statements to the identity.

1. If \(\epsilon=1-\max_c p(c\mid x,y)=0\), the correction is deleted exactly.
2. As \(\epsilon\to0\), it is deleted approximately under
\[
\operatorname{TV}(q_j,q_0)=o(1/|\log\epsilon|),
\qquad
\sup_c|\log r_j(c\mid x)-\log r_0(c\mid x)|\le\delta\to0.
\tag{3}
\]

The second condition is called Coverage. It bounds variation across token anchors. It does not bound how small an individual latent posterior coordinate can be. Diversity supplies invertibility, but no uniform inverse-norm bound across a varying family. Figure1, p2, goes further and writes an \(o(\epsilon)\) residual, which is stronger than the main theorem's qualitative approximation and is not established by the printed argument.

The exact \(\epsilon=0\) argument in Eqs.(26)–(28) substitutes a point mass into \(r_j\) but retains the different averaging weights \(q_j\). If \(q_j\) charges a state where \(r_j=0\), then \(h_j=-\infty\), rather than zero. The logarithmic identity itself requires support care in this limit. Concentration alone does not allow the weighted cross entropy to be replaced by the entropy of the point mass. This is a domain and limiting-argument defect, not a claim that the finite-log identity(2) fails.

For the approximate branch, Eq.(35), p22, uses \(r_j(c)\lesssim\epsilon\) for a nonmodal state as though it implied \(\log r_j(c)\approx\log\epsilon\). It only gives an upper bound on the probability. The following construction makes the missing lower-tail control consequential.

## 4. Strictly positive counterexample to deletion of the correction

This section is an independent bounded mathematical check. It contradicts the specified \(A,b\) approximation and residual claim, not every possible affine fit of a finite collection of points.

Let \(0<t<1/8\), \(s=\exp(-1/t)\), and let \(C\) be uniform on three states. With rows indexed by \(X=0,1,2\) and columns by \(C=0,1,2\), set
\[
P(X\mid C)=
\begin{pmatrix}
1-t-s&t&s\\
s&1-t-s&t\\
t&s&1-t-s
\end{pmatrix}.
\tag{4}
\]
Independently conditional on \(C\), let
\[
P(Y=1\mid C)=(1/2-t,\ 1/2,\ 1/2+t).
\tag{5}
\]
Every probability is positive. The matrix in(4) is doubly stochastic, so \(P(X=x)=1/3\), and its rows are precisely \(p(C\mid X=x)\). Both token marginals equal \(1/2\).

Take \(d=1\), \(g(0)=0\), \(g(1)=1\), and
\[
f(x)=\operatorname{logit}P(Y=1\mid X=x).
\]
The prediction is exact and \(\widehat L=1\) for every \(t\). Therefore the failure below is not caused by ill-conditioned output embeddings.

Bayes' rule yields
\[
q_1-q_0=(-4t/3,0,4t/3),\qquad
\operatorname{TV}(q_1,q_0)=4t/3,
\]
\[
A=(-4t/3,0,4t/3),\qquad b=0.
\tag{6}
\]
The last equality follows by symmetry of the three emission probabilities under \(y\mapsto1-y\). Each posterior \(p(C\mid x,y)\) has nonmodal mass \(\Theta(t)\), uniformly over all six \((x,y)\) pairs. The emission probabilities stay between \(3/8\) and \(5/8\), while every row of(4) has one mass \(1-t-s\) and remaining total mass \(t+s\). Hence the printed concentration and TV rate hold uniformly.

Coverage also holds uniformly. For either anchor,
\[
\log\frac{r_1(c\mid x)}{r_0(c\mid x)}
=\operatorname{logit}P(Y=1\mid c)-\operatorname{logit}P(Y=1\mid x),
\]
so
\[
\delta_t\le2\log\frac{1/2+t}{1/2-t}=O(t)\to0.
\tag{7}
\]
At \(x=0\), however,
\[
f(0)=\operatorname{logit}(1/2-t+t^2+2ts)\longrightarrow0,
\]
whereas
\[
A\log p(C\mid X=0)
=\frac{4t}{3}\{\log s-\log(1-t-s)\}
\longrightarrow-\frac43.
\tag{8}
\]
Consequently, \(\Delta h(0)\to-4/3\). All printed approximate conditions hold with a fixed, perfectly conditioned \(\widehat L\), but the correction does not vanish. The rare posterior coordinate \(s=e^{-1/t}\) supplies the missing logarithmic scale.

A four-point numerical spot check at \(t=.1,.05,.02,.01\) reproduced Eq.(2) to floating-point precision and showed \(\Delta h(0)\) approaching the analytic limit. That computation is only an arithmetic check. The explicit formulas and limits above supply the counterexample. There was no exhaustive search, theorem-prover replay or model training.

## 5. A valid quantitative residual bound

The original decomposition in AppendixD Eq.(32) is valid:
\[
h_j-h_0=
\sum_c(q_j-q_0)(c)\log r_j(c\mid x)
+\sum_c q_0(c)\log\frac{r_j(c\mid x)}{r_0(c\mid x)}.
\]
Since \(q_j-q_0\) has total mass zero, centering the first logarithm at the midpoint of its range gives the exact bound
\[
\boxed{|h_j-h_0|\le
\operatorname{TV}(q_j,q_0)\,
\operatorname{osc}_c\log r_j(c\mid x)+\delta_j(x).}
\tag{9}
\]
Here \(\operatorname{osc}u=\max u-\min u\) and TV uses the half-\(\ell_1\) convention. This yields
\[
\|f(x)-A\log p(C\mid x)-b\|_\infty
\le \| (\widehat L^T)^{-1}\|_\infty
\max_j\left[
\operatorname{TV}(q_j,q_0)\operatorname{osc}_c\log r_j(c\mid x)
+\delta_j(x)\right].
\tag{10}
\]
This is an independent conditional repair of the residual argument. For example, a uniform lower bound \(r_j(c\mid x)\ge a\epsilon^b\), with fixed \(a,b>0\), implies logarithmic oscillation \(O(|\log\epsilon|)\). Together with the printed TV rate, vanishing Coverage bound and bounded inverse norm, it does imply a vanishing feature residual. None of those extra lower-tail or uniform conditioning conclusions follows merely from a large modal posterior probability.

A single small empirical TV number cannot substitute for the entire right side of(10). The same warning applies to a high linear-classification accuracy, which neither bounds these cross entropies nor measures the inverse norm.

## 6. Concepts, logarithmic factorization and readout rank

Corollary4.2, p6, assumes the approximate feature relation and nearly deterministic \(p(C\mid x)\). For paired contexts differing only in concept \(C^k\), it claims
\[
\Delta f\approx A B^k\,\Delta\log p(C^k\mid x),
\tag{11}
\]
where \(B^k\) broadcasts each marginal entry to the corresponding joint configurations. Corollary4.3 then asserts linear separability for that concept and a classifier with \(WAB^k\approx I\).

### 6.1 Small posterior dependence does not control unweighted logarithms

AppendixE Eqs.(42)–(56), pp23–24, moves from small KL dependence to a coordinatewise log factorization. Near concentration does imply small mutual information for a fixed finite latent alphabet:
\[
I(C^k:C^{-k}\mid X=x)\le H(C\mid X=x)
\le h_2(\epsilon_x)+\epsilon_x\log(\ell-1)\to0.
\tag{12}
\]
It does not imply a small unweighted log-vector residual. On the four configurations \(00,01,10,11\), take
\[
p=(1-3e,e,e,e).
\]
Both marginals assign probability \(2e\) to value1. At configuration11,
\[
\log p_{11}-\log p_{1+}-\log p_{+1}
=-\log(4e)\longrightarrow+\infty,
\tag{13}
\]
while the mutual information tends to zero. Thus the needed log-vector implication is false. Eqs.(63)–(65) also divide a vanishing probability difference by a possibly much smaller marginal probability. Absolute convergence alone cannot justify this step.

This identifies a proof gap in Corollary4.2. It is not, by itself, a full counterexample to every version of Eq.(11), because the multiplication by \(A\), matching assumptions and paired residuals must also be controlled. AppendixG's binary-direction reduction additionally needs compatible rates for the two small posterior errors when it treats their logarithms as interchangeable.

### 6.2 The requested full inverse is algebraically impossible

Each row of \(L\) is a difference of probability distributions. Hence
\[
L\mathbf1_\ell=0,\qquad A\mathbf1_\ell=0.
\]
If concept \(k\) has \(n_k\) values, then \(B^k\mathbf1_{n_k}=\mathbf1_\ell\). Writing \(T_k=AB^k\),
\[
T_k\mathbf1_{n_k}=0,
\qquad WT_k\mathbf1_{n_k}=0.
\tag{14}
\]
For every \(W\), its induced Euclidean operator norm therefore satisfies
\[
\|WT_k-I_{n_k}\|_{\rm op}\ge1.
\tag{15}
\]
The full identity target in Corollary4.3 and AppendixF Eq.(72), p25, cannot be approached under the paper's own definitions. The issue exists even if the earlier approximation is granted exactly.

There is a useful conditional contrast-space statement. Let
\[
J_n=I_n-\frac1n\mathbf1_n\mathbf1_n^T.
\]
If \(T\mathbf1_n=0\) and \(\operatorname{rank}(T)=n-1\), then its Moore–Penrose inverse gives \(T^\dagger T=J_n\). Consequently, under an exact feature model \(f=T\log p+u\) and a separately controlled nuisance term \(T^\dagger u\), one can recover centered log probabilities. Softmax obeys
\[
\operatorname{softmax}(J_n\log p)=p.
\tag{16}
\]
The necessary contrast rank and nuisance control are additional assumptions. Diversity of output embeddings does not imply them. For binary \(T=(v,-v)\), a nonzero \(v\) allows this construction, while \(v=0\) does not.

AppendixF Eq.(71) also equates logits with probabilities. Cross-entropy prediction instead identifies logits with \(\log p\) up to an additive common scalar. Constant scaling does not turn probabilities into their logarithms. The contrast formulation above respects this normalization freedom.

## 7. A concept that generates observations but is invisible to prediction

The following independent construction separates the separability claim from the already failed residual claim. Here the approximate relation itself really does hold.

Let \(C=(S,N)\), with independent fair bits. Observe \(X=(U,V)\), where \(U\) is \(S\) through a binary symmetric channel of error \(e\), and \(V\) is \(N\) through an independent channel of the same error. Let
\[
P(Y=1\mid S,N)=\frac12+e(2S-1),\qquad0<e<1/8.
\tag{17}
\]
Thus \(X\perp Y\mid C\), with all probabilities positive. Both latent coordinates genuinely generate part of \(X\), but only \(S\) predicts \(Y\).

Use the one-dimensional softmax with \(g(0)=0,g(1)=1\). Its exact feature is
\[
f(U,V)=\operatorname{logit}\left[\frac12+e(1-2e)(2U-1)\right],
\tag{18}
\]
which does not depend on \(V\). In the joint ordering \((00,01,10,11)\),
\[
A=(-e,-e,e,e),\qquad AB^N=(0,0),
\qquad \operatorname{TV}(q_1,q_0)=2e.
\tag{19}
\]
The posterior error given \((x,y)\) is \(O(e)\) uniformly, and Coverage is bounded by \(2\log[(1/2+e)/(1/2-e)]=O(e)\). Every posterior coordinate is at least a fixed positive multiple of \(e^2\). Equation(9) therefore gives \(\Delta h=O(e|\log e|)\to0\). The approximate feature relation used by Corollary4.3 is satisfied, and \(\epsilon_x\to0\).

Fix \(U\) and take opposite values of \(V\). The dominant latent configurations differ only in \(N\), but the features are identical for every \(e\). No classifier, linear or otherwise, can distinguish these paired concept values from \(f\). Indeed, under this model \(N\) is independent of \(f\), so its optimal unconditional classification error is \(1/2\).

This refutes the assertion that any generating concept must be linearly recoverable under the stated assumptions. It does not deny that predictive concepts can be encoded or that actual language models may retain redundant information. It identifies a missing predictive-observability condition. Exact next-token prediction has no need to preserve a latent variable that changes the context but leaves the conditional next-token law unchanged.

## 8. Empirical results and what they establish

### 8.1 Synthetic experiments

The paper samples latent binary DAGs with3–8variables, conditional Bernoulli probabilities in[.2,.8], and a nonlinear observed mapping implemented by permuting one-hot latent configurations before converting to binary observations. It masks an observed coordinate and predicts it from the others using a three-layer256-unit MLP with ReLU and batch normalization. This is a controlled masked-coordinate experiment, not full autoregressive language-model training.

Figure2 reports five-seed means and standard deviations. More observed dimensions improve probe accuracy in the reported setting, and the graph-size comparison shows high but nonmonotone accuracy. Classification success supports the particular synthetic representations. It does not measure the omitted cross-entropy residual or establish uniform rates in the theorem's assumptions.

### 8.2 Language-model concept directions and probes

The main benchmark contains27concept categories, not merely27individual word pairs. Table1 gives between4 and228pairs per category, often50. Categories mix morphology, translation and semantic relations. The smallest possessive-pronoun category has only4pairs.

For each category, the authors average paired representation differences to estimate a direction, then fit a logistic probe. The normalized direction/probe products are shown for Pythia, Llama2, Llama3 and DeepSeek-R1 variants in Figures3 and6. Diagonal alignment and structured off-diagonal similarities are visible. These normalized cosine-like products are different mathematical objects from the complete joint-state \(WAB^k\) inverse in the theorem.

AppendixN explicitly addresses data reuse. It reports a50/50split of word pairs into disjoint direction-estimation and probe-fitting subsets, a label-permutation null baseline, and repeated split seeds. Figures7–16 retain diagonal alignment relative to the null. These are meaningful controls and must not be omitted when evaluating the empirical evidence. They do not turn the lexical labels into identified latent ground truth or prove the Bayes residual bound.

AppendixO uses70/30probe train/test splits with three seeds. Figures17–21 show heterogeneous test accuracy, including much weaker categories and unstable results for the four-pair category. The authors acknowledge this limitation. The near-perfect Figure5 fit should not be confused with those held-out results. High accuracy is used as an empirical proxy for a small correction term, but no mathematical implication from accuracy to the magnitude of that term is proved.

AppendixR adds eight semantic contrast categories with the same split/null protocol and repeated seeds. Figures23–24 show weaker but persistent alignment. The authors explicitly acknowledge that such pairs may change more than one latent factor. There is no independent verification that all paired words satisfy the formal single-concept intervention premise.

### 8.3 Sparse autoencoders

The comparison includes top-k, batch-top-k, p-annealing and the proposed structured SAE. The latter has two encoders with a shared decoder, assigning sparse and low-rank penalties to different components. The implemented low-rank penalty approximates a nuclear norm using the leading64singular values. It is not the complete nuclear norm unless the remaining singular values vanish.

The reported setup uses32,768features, the first200million Pile tokens,20,000steps, batch size10,000, three seeds, and fourA10040GB GPUs. Pythia70m,1.4b and2.8b final-layer representations are tested. Equal feature count does not establish equal parameter count or training compute when an extra encoder is introduced.

The evaluation correlates exponentiated SAE features with a supervised probe-derived concept target. Main prose calls the probe's logits an unnormalized posterior, while AppendixI alternates between probabilities and logits. The exact calibration and matching object need care. The main best-feature description and AppendixI's Hungarian matching are also different selection descriptions. AppendixN's explicit split applies to direction/probe alignment. It does not by itself document an independent held-out split for every SAE feature-selection and evaluation operation.

Figure4 and Tables3–5 show higher average PCC for structured SAE under this benchmark and lower plotted reconstruction error. For1.4b the four average PCCs are approximately .697,.686,.742,.752, and for2.8b they are .707,.704,.762,.771. Individual concepts have exceptions. The low-rank-weight ablation peaks at the tested \(\gamma=.1\), with overlapping uncertainty across nearby values. These are empirical benchmark results, not a theorem that structured SAE recovers the unique latent concepts.

AppendixP varies probe regularization, class weights and label flips. The text describes class-proportion changes implemented through the classifier's class-weight parameter, which is not the same operation as resampling the dataset. Figure22 gives modest sensitivity under these interventions. It does not provide independent ground truth for semantic completeness.

### 8.4 The posterior-proxy calculation does not verify the asymptotic premises

AppendixQ and Table6, pp44–45, normalize27binary probe outputs into a pseudo-posterior across the27concept categories. This is not the joint posterior over all latent configurations used in the theorem. Variation of that proxy across contexts is then used as a surrogate for variation in \(p(C\mid Y)\), without an identification or error bound for the substitution.

The reported5th-percentile concentration error is
\[
\widehat\epsilon_{q05}=.7473,\qquad|\log\widehat\epsilon_{q05}|=.2913.
\]
At that quantile the largest pseudo-posterior coordinate is only .2527. This does not demonstrate a posterior approaching a point mass. A5th percentile also does not bound the worst-case posterior error. Nonanchor TVs range from .0754 to .2940, giving the reported products approximately .02196 to .08565. A small product at one finite setting establishes neither the little-o rate nor the missing logarithmic-tail control. Coverage and inverse conditioning are not measured. This is a limited exploratory proxy analysis, not verification of the sufficient conditions in Eq.(10).

## 9. Bounded public-code check and reproducibility boundary

The author [repository](https://github.com/yuhangliu01/I-Predict-Therefore-I-Am/tree/bc43ab261002b07f50984891edc2c6972a95a54b) was inspected at commit bc43ab261002b07f50984891edc2c6972a95a54b, March1,2026. The check read its README and three linear-property scripts, without executing them or loading models.

- [1_store_matrices_Lin.py](https://github.com/yuhangliu01/I-Predict-Therefore-I-Am/blob/bc43ab261002b07f50984891edc2c6972a95a54b/linear_property/1_store_matrices_Lin.py), lines121–149, actively uses all word pairs for both the averaged direction and logistic-probe fitting/scoring, with C=.0001. The half-data and permutation-label alternatives are commented out. Active filenames nevertheless contain holdout. Ten seeds are iterated without an active random split in this entry point.
- [2_heatmap_stats_F.py](https://github.com/yuhangliu01/I-Predict-Therefore-I-Am/blob/bc43ab261002b07f50984891edc2c6972a95a54b/linear_property/2_heatmap_stats_F.py), lines33–67, consumes saved matrices, forms the27-by-27products and separately computes an ambient-space projection discrepancy. The plotted label uses a2-norm symbol while the code computes a Frobenius norm, and the final annotation uses the last loop's norm value.
- [linear_rep_geometry.py](https://github.com/yuhangliu01/I-Predict-Therefore-I-Am/blob/bc43ab261002b07f50984891edc2c6972a95a54b/linear_property/linear_rep_geometry.py), lines85–136, feeds each observed word separately and takes the final token's last hidden-layer activation. This is a lexical representation measurement, not recovery of an unobserved future token's latent state.

The active public entry points therefore do not independently reproduce the AppendixN split/null protocol as printed. This does **not** establish that the paper's figures omitted the reported controls. The saved private activations and exact figure-producing configurations were not available in this bounded check. No accusation about data fabrication, corrected benchmark, full implementation audit or empirical replication follows.

## 10. Reusable conclusions and FP boundary

The retained mathematical instruments are the exact anchored Bayes identity(2), the TV-times-log-oscillation residual bound(9)–(10), and the conditional contrast-space readout(14)–(16). Each has explicit hypotheses. The three-state construction shows why modal concentration and cross-anchor Coverage do not control rare log tails. The two-concept construction shows why a predictive representation need not retain a context-generating variable that has no next-token effect.

The source's world-model discussion in AppendixJ, including comparisons with human cognition and pure vision models, is explanatory speculation beyond these formal results. It is not adopted as an account of general intelligence. The experiments establish alignment and comparative SAE performance in the reported protocols, with real split/null controls and the limitations described above.

For FP, this is independent positive and negative theoretical evidence. It does not define FP's states, alter the prediction objective, select an architecture, or establish a memory/sample-complexity theorem. A genuine transfer would require an explicit observable predictive distinction, the relevant posterior/log-tail controls, a stable readout and a learning guarantee. No such FP transfer is asserted here.

## 11. Recovery record

Completed selected edition: official ICLR2026 final46pages, counted once with scientifically text-matched arXivv4 as companion. All active scientific material, figures, tables and printed references have been read. Bounded independent analysis establishes the two constructions and the conditional repairs above, without certifying all other claims. No historical paper was promoted to full-read status from its citation here.

Before starting this paper and at its publication boundary, the shared frontier history, index and researcher entries were checked. Astra request59b8251 remains with Pro-E under successful claim40c0d2a. Astra's concurrent sample, memory and cross-task transfer work is preserved. The next ordinary selection requires a fresh request and ownership check. No core research file was edited.
