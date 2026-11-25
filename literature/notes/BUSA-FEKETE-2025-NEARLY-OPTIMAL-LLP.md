# Nearly Optimal Sample Complexity for Learning with Label Proportions

## Source and actual reading coverage

- **Authors:** Robert Istvan Busa-Fekete, Travis Dick, Claudio Gentile, Haim Kaplan, Tomer Koren and Uri Stemmer.
- **Publication:** ICML 2025, PMLR 267:5943–5976, July 13–19, 2025. Index ID `PMLR-v267-busa-fekete25a`.
- **Primary sources:** [official proceedings entry](https://proceedings.mlr.press/v267/busa-fekete25a.html), [official 34-page PDF](https://raw.githubusercontent.com/mlresearch/v267/main/assets/busa-fekete25a/busa-fekete25a.pdf), [arXiv 2505.05355v2](https://arxiv.org/abs/2505.05355v2), May 29, 2025. Page references below are PDF pages, not the volume's continuous pagination.
- **Complete main-reader coverage, November 25, 2026:** all 34 official PDF pages, §§1–7, impact statement, Appendices A–D, every proof and formula, two algorithms, seven footnotes, all three figures and their 15 panels, and all 45 references. There are no tables. Reliable text was read in continuous page blocks. Original PDF layouts were inspected on pp. 3–6, 8–9, 14, 17–18, 25–27, 30 and 34.
- **Supporting material:** the official PDF itself includes the complete supporting Appendices A–D on pp. 12–34. These have been read. The PMLR entry links this PDF and OpenReview, with no separately linked supplement. OpenReview's forum and attachment endpoints could not be authenticated from this environment. A conventional separate PMLR supplement URL returned 404. This establishes the coverage of the official appended material, not the nonexistence or reading of an unknown second attachment.
- **Edition comparison:** the source agent obtained arXiv v2 PDF and TeX. Its entire extracted text matches the proceedings PDF after removal of running titles, arXiv marks and whitespace. This is not an assertion of pixel identity. The original proceedings PDF governs this note. The main reader used the complete PDF text, not a claim of separately reading every TeX macro.
- **Verification:** peer-reviewed source, followed in full. The local checks in §7 and the requested comparison in §8 are independent deductions. Several printed proof steps are not valid as written. No full theorem certification, formal verification or empirical reproduction is claimed.

## 1. The original observation experiment

Section 2, p. 3, Eq. (1), begins with \(n=mk\) independent **paired** examples \((X_{ji},Y_{ji})\sim D\), where \(Y\in\{0,1\}\). A uniform random partition produces bags of size \(k\). The learner receives

\[
B_j=\{X_{j1},\ldots,X_{jk}\},\qquad
\alpha_j=\frac1k\sum_{i=1}^kY_{ji}.
\]

Every feature vector is individually available in its bag. The individual feature–label matching is hidden, but **the label count belongs to those same realized examples**. Bags are independent under the iid source model. There is one joint distribution \(D\), not a family of unrelated context distributions.

For a finite class \(H\subseteq[0,1]^{\mathcal X}\), define

\[
L(h)=\mathbb E(Y-h(X))^2,\quad
h^*(x)=\mathbb E[Y\mid X=x],\quad
\widehat h^*\in\arg\min_{h\in H}L(h).
\]

The target is excess square loss \(R(h)=L(h)-L(\widehat h^*)<\beta\). Realizability means \(h^*\in H\). It permits stochastic labels and positive irreducible square loss. This differs from a deterministic-label assumption \(L(h^*)=0\).

The resource \(m\) counts bags, while \(n=mk\) counts the underlying examples. Neither counts the bits in an aggregate report, the cost of obtaining the features, or the installed size of a predictor. A label count has \(k+1\) possible values, but that observation alphabet alone does not determine its statistical information.

## 2. Two hypotheses and the two sources of information

Section 3, Algorithm 1 and Theorem 3.1, pp. 3–4, take \(H=\{h_1,h_2\}\), with one member equal to (h^*). Write

\[
\beta=\mathbb E(h_1(X)-h_2(X))^2,
\qquad \Delta=\mathbb E[h_1(X)-h_2(X)].
\]

These are assumed known or estimable from unlabeled data. Let \(E_{js}=\sum_{x\in B_j}h_s(x)\), the expected label count **conditional on that realized bag under hypothesis \(s\)**, and let \(\mu_j=(E_{j1}+E_{j2})/2\).

The large-bias branch, \( |\Delta|\ge\sqrt{\beta/(2k)}\), compares

\[
A_s=\sum_j(k\alpha_j-E_{js}).
\]

It chooses the smaller absolute residual. Only the total empirical label mean and total empirical prediction means matter here.

The small-bias branch uses the sign of

\[
Q=\sum_j\left[
1_{\{E_{j1}\le E_{j2}\}}(k\alpha_j-\mu_j)
+1_{\{E_{j1}>E_{j2}\}}(\mu_j-k\alpha_j)
\right].
\]

It chooses \(h_2\) if \(Q\ge0\). Its orientation depends on the features in the **same** bag whose label count is tested. This is not a comparison of two separate per-hypothesis losses.

The theorem claims, for \(k=\Omega(1/\beta)\), a sufficient total sample order

\[
n=O\!\left(\min\left\{\Delta^{-2},\frac{k}{\beta}\right\}
\log\frac1\delta\right).
\]

For a hard pair with \(\Delta=0\), it also claims a necessary order

\[
n=\Omega\!\left(\frac{k(1-H_2(\delta))}{\beta}\right).
\]

As always, an actual experiment uses an integer number of bags and at least \(k\) examples when it takes a bag. The theorem's displayed asymptotic expression should not be read as permitting a fraction of a bag.

### Proof structure, Appendix A, pp. 12–19

For the large-bias branch, Hoeffding concentration separates a zero-mean total residual from one with mean \(n\Delta\). For the small-bias branch, condition on all feature bags. A bag is discriminative if its two expected counts differ by a threshold. Conditional label independence bounds fluctuations around the correct expected count. Berry–Esseen anti-concentration then gives a constant fraction of discriminative bags. The eventual threshold is \(k|\Delta|+\sigma\sqrt{k}\), with \(\sigma^2=\beta-\Delta^2\), producing an error exponent of order \(m\beta\).

The lower-bound construction has fair binary \(X\) and conditional probabilities \(1/2\pm\sqrt\beta/2\), with the signs interchanged between the hypotheses. A fair prior on the hidden hypothesis, data processing and Fano reduce the problem to an upper bound on information in one observed bag. The proof estimates that information using entropies of binomial and Poisson-binomial counts. Its printed entropy steps require the qualifications in §7. In particular, the proof's final asymptotic discussion takes small fixed \(\beta\) and sufficiently large \(k\), which is more restrictive than an unqualified uniform reading of every parameter in the headline lower bound.

## 3. Debiased square loss and finite-class ERM

Section 4, pp. 4–6, defines \(p=\mathbb E Y\), \(\mu_h=\mathbb E h(X)\), \(\widetilde\alpha_j=\alpha_j-p\), and \(\widetilde E_j(h)=\sum_i h(X_{ji})-k\mu_h\). Its central untruncated loss is

\[
\ell(h,Z_j)=\frac1k\big(k\widetilde\alpha_j-\widetilde E_j(h)\big)^2
+(\mu_h-p)^2. \tag{2}
\]

Equation (3), p. 5, is \(\mathbb E\ell(h,Z)=L(h)\). Appendix B.1, p. 20, proves it by expanding the square of the sum of iid centered residuals \(Y_i-h(X_i)-\mathbb E[Y-h(X)]\). The within-pair covariance remains in each residual variance.

For the ERM theorem, retain the squared centered term only when

\[
|k\widetilde\alpha_j-\widetilde E_j(h)|
\le\sqrt{8k\log(2/\theta)},\qquad \theta=\frac{\beta}{16k^2}.
\]

The deterministic mean-square term is always retained. Theorem 4.1, p. 5, states that with probability at least \(1-\delta\), clipped ERM achieves \(R(\widehat h)<\beta\) using

\[
m=O\!\left(
\frac{(\gamma^*+\beta)\log(k/\beta)}{\beta^2}
\log\frac{|H_\beta|}{\delta}\right),
\quad
\gamma^*=\mathbb E(\widehat h^*(X)-h^*(X))^2,
\]

where \(H_\beta=\{h:R(h)\ge\beta\}\). The realizable case has \(\gamma^*=0\), hence roughly \(m=\widetilde O(1/\beta)\) bags and \(n=\widetilde O(k/\beta)\) examples. With positive approximation error, the additional \(\gamma^*/\beta^2\) term remains.

The proof on pp. 19–23 studies **loss differences**. Clipping changes their expectation by at most \(8k\theta\), bounds their magnitude logarithmically in \(k/\beta\), and gives second moment controlled by

\[
\gamma(h,h')\log(1/\theta)+k^2\theta.
\]

The square-loss identity implies

\[
\gamma(h,\widehat h^*)\le4\gamma^*+2R(h).
\]

Bernstein concentration and a finite union bound then yield the displayed fast rate. The gain comes from variance control and localization of excess loss, not from observing the missing individual labels.

Appendix B.2, pp. 24–29, splits bags into \(S_1,S_2\). It estimates (p) and every \(\mu_h\) on \(S_2\), uses a wider clipping threshold \(\sqrt{18k\log(6/\theta)}\) on \(S_1\), and claims the same overall rate. The sample split makes the estimated means independent of the bags used for ERM. It does **not** replace the label count in an ERM bag by labels from unrelated examples. The printed derivation of this extension has specific algebraic gaps recorded in §7. Its claimed rate is retained as an author result, without local certification.

## 4. Convex stochastic gradient descent

Section 5, pp. 6–7, changes to bounded linear prediction \(h_w(x)=w^\top x\), with \(\|w\|\le\rho_w\), \(\|x\|\le\rho_x\), and real labels \( |Y|\le\rho_y\). The population means \(\mu_x,\mu_y\) are initially known. The bag loss is

\[
k\big[w^\top(\bar X-\mu_x)-(\alpha-\mu_y)\big]^2
+(w^\top\mu_x-\mu_y)^2.
\]

Algorithm 2 skips bags whose centered feature centroid exceeds \(\theta\rho_x\), performs projected gradient updates on retained bags, and averages the iterates. The theorem sets a threshold of order \(\sqrt{\log(km)/k}\) with explicit dependence on the norm bounds.

Theorem 5.1 states an expected excess-risk guarantee with

\[
m=\widetilde O\!\left(
\frac{\rho_x^2\rho_w^2}{\beta}
+\frac{L_*\rho_x^2\rho_w^2}{\beta^2}\right),
\]

when \(L(w^*)\le L_*\). Logarithmic factors include (km) and the norm ratio involving \(\rho_y\). Appendix C, pp. 29–31, combines convex smooth nonnegative losses, small truncation bias, a self-bounding gradient inequality, projected online-gradient regret and an online-to-batch argument.

Here a fast \(1/\beta\) regime requires small **absolute optimum loss** \(L_*\). It is not the same condition as the finite-class ERM theorem's \(h^*\in H\), which allows nonzero Bayes noise. Unknown-mean modifications are asserted to be analogous to Appendix B.2, rather than separately proved in full for SGD. The convex linear theorem does not certify optimization of the neural networks in the experiments. Some printed smoothness constants omit the factor two for an unhalved square loss, so exact constants should not be imported from the display without correction.

## 5. Experiments and evidence

Sections 6.1–6.5, pp. 7–9, and Appendix D, pp. 32–34, use actual paired datasets. They shuffle training examples once, create fixed bags, and reveal the average of the labels belonging to each bag. Bags remain fixed across epochs, while their order is shuffled. This preserves the observation experiment in §1.

The datasets are binary versions of MNIST and CIFAR-10, plus Higgs and Adult. MNIST uses digit parity. CIFAR groups six animal classes against four vehicle classes. Higgs uses the first 10,000 of 11,000,000 examples as test data. Adult uses its standard train/test split, one-hot categorical features and numerical scaling to ([0,1]). The image model has two convolution/max-pool stages, dropout and one output. Higgs uses four 300-unit hidden layers. Adult has a 32-unit hidden layer.

Minibatches contain 1,024 examples, with bag sizes \(1,2,\ldots,512\) on a power-of-two grid. Adam learning rates are chosen from eight values between (10^{-6}) and (10^{-2}). Ten repetitions vary partition and initialization. The reported curves use the best average final test accuracy across learning rates for each loss and bag size. This is a tuned performance comparison, not a separately established guarantee for a prospective model-selection rule.

The proposed method uses **unclipped** Eq. (2). Footnote 3 explains that clipping was omitted to avoid another hyperparameter after preliminary experiments. The comparison losses are Li et al.'s debiased square loss, vanilla bag-level square and cross-entropy losses, and EasyLLP's corrected cross-entropy. The global label mean is estimated from all training counts. A bag's prediction mean is estimated from the other bags in its minibatch, avoiding direct reuse of that bag's fluctuations.

Figures 1 and 3 show better accuracy for the proposed loss particularly at large bags and fewer epochs. As approximate visual readings, at bag size 512 and the smaller epoch counts, its CIFAR accuracy is about .81 while the alternatives are around .55–.60, and its MNIST accuracy is about .90 against approximately .75–.80. These are graph readings, not new measurements. Adult is included in Figure 3. Error bars show one standard error over ten repetitions. The Dulac-Arnold comparison cites earlier reported results rather than a fresh matched implementation in this paper.

Figure 2 uses \(X\sim\mathrm{Unif}[0,1]\), \(Y\mid X\sim\mathrm{Bernoulli}(X^2)\), and evaluates \(h(x)=x\). At (2^{20}) examples, the proposed estimator's variance stays near .034 and rises to about .055 at bag size 256 as fewer other examples remain to estimate its mean. The two comparison estimators grow approximately linearly with bag size. This supports the variance-reduction mechanism on that example. It does not verify all constants or all distributions in the theorems.

Footnote 4, p. 9, reports that an implementation measurement bug in the original submission made the Li et al. baseline appear better than it does in this corrected version. Edition-specific results therefore matter.

## 6. Limitations and cited inputs

Section 7 explicitly leaves log-loss guarantees, multiclass classification and drifting within-bag or across-bag distributions for future work. The two-hypothesis theorem requires \(k=\Omega(1/\beta)\). Finite-class statistical ERM need not be computationally tractable for an arbitrary class. The practical neural training omits the theoretical clipping and does not inherit the convex SGD guarantee.

The proof uses Hoeffding, Bernstein, Berry–Esseen and Chernoff inequalities, Fano/data processing, binomial entropy approximations from Adell et al. and Poisson-binomial entropy comparisons attributed to Harremoës. The fast-rate argument follows the loss-difference/localization tradition represented by Massart, Mendelson and Bartlett et al. The SGD proof imports smooth online-gradient analysis. EasyLLP and Li et al. are prior algorithmic comparators. Reading these uses does not mark those cited sources fully read. No broad weak-supervision survey was undertaken for this request.

## 7. What the printed arguments do and do not establish locally

The full paper was read. That is separate from independent verification. The following checks are deliberately limited to key algebra and the requested observation distinction.

1. **Unbiased loss, Eq. (3), verified directly.** Expanding a sum of independent centered paired residuals gives the individual square risk exactly. The independent-panel calculation below shows precisely where it changes.
2. **Appendix A, p. 17, conditional binomial assertion is false as written.** Mixing over one shared hidden hypothesis makes labels conditionally dependent after the features are fixed. For example, with two identical feature values, the count is a mixture of two different binomials, not (mathrm{Binomial}(2,1/2)). However, the unconditional count is binomial in this hard construction. Thus \(H(\alpha\mid B)\le H(\alpha)\) supplies the entropy upper bound needed at this particular step. The false equality alone does not refute the theorem.
3. **Appendix A, p. 18, a further entropy step is unsupported.** The preceding lower bound uses \(\bar k_i=\lfloor2\mu_i/(1+\sqrt\beta)\rfloor\). The last displayed combination replaces the associated \(\bar k_i\) factor by \(k\). At \(s=k/2\), \(\bar k_i\sim k/(1+\sqrt\beta)\), so this change is not an asymptotically vanishing error in \(k\). It can discard a term of order \(\sqrt\beta\). The earlier statement \(\bar k_i=\Omega(k)\) does not justify the displayed \(O(\beta)\) information conclusion. Page 19's additional claim that \(-\tfrac12\log_2(1-\beta)+o(1)\) becomes smaller than \(\beta/2\) is also inconsistent with its small-\(\beta\) coefficient \(1/(2\ln2)\). No alternative lower-bound proof is supplied here.
4. **Appendix B.2, pp. 25–26, uncentered terms are mishandled.** Page 26 prints \(\mathbb E(E_j(h_2)-E_j(h_1))^2=k\gamma(h_1,h_2)\). The exact expression is \(k\gamma+k(k-1)(\mu_{h_2}-\mu_{h_1})^2\). For constant hypotheses 0 and 1, the asserted square-root estimate becomes \(k\le\sqrt{k}\), which fails for (k>1). The preceding difference-of-squares factorization on p. 25 also omits the estimated-mean difference in its first factor. Original PDF and v2 TeX both contain these steps. They require repair before this printed unknown-mean proof can count as independently verified. They are not a counterexample to the stated rate itself.

The source agent independently checked the narrow printed-step concerns after the main reader identified them. No proof-auditing program, exhaustive search or empirical reproduction was developed. The working status is **fully read, author theorems accurately recorded, selected identities verified, specified proof steps unresolved**.

## 8. Requested comparison: independent panels from common contexts

This section answers Astra request `7b8ff15`. It is an independent comparison of statistical experiments, not an additional theorem attributed to the paper.

### What is observed

| Experiment | Retained link | What is missing |
|---|---|---|
| Busa-Fekete et al., §2 | The feature multiset and label count arise from the same \(k\) paired draws | Individual feature–label assignments inside the bag |
| Independent panels at context \(c\) | Both panels share \(c\) and its population marginals | The count is not the count of labels attached to the realized feature panel |
| Known population proportions with common class-conditional laws | Context-specific mixing probabilities link different feature populations | Individual labels, with identifiability supplied by the mixture model |
| Matched finite-alphabet histograms | Both histograms summarize the same realized paired items | Within-bag matching, but not bag-level count covariance |

For the second experiment, condition on \(c\). Draw \(X_1,\ldots,X_k\sim P_{X\mid c}\) and independently \(Y'_1,\ldots,Y'_k\sim P_{Y\mid c}\). Put \(\mu_c=\mathbb E[h(X)\mid c]\), \(p_c=\mathbb E[Y\mid c]\). Reusing the paper's centered loss with these exact context means yields

\[
\mathbb E[\ell_{\mathrm{ind}}(h)\mid c]
=\operatorname{Var}(h(X)\mid c)+\operatorname{Var}(Y\mid c)+(\mu_c-p_c)^2
=L_c(h)+2\operatorname{Cov}(h(X),Y\mid c).
\]

The paired-bag version instead has

\[
k\operatorname{Cov}(\bar h,\bar Y\mid c)
=\operatorname{Cov}(h(X),Y\mid c).
\]

The independent version has zero conditional covariance. Consequently **Eq. (3), Theorem 4.1 and Theorem 5.1 do not transfer merely by retaining the context name**. The small-bias branch of Theorem 3.1 also fails to transfer because its conditional expected count \(E_{js}\) no longer describes the label panel. Estimating the global means on a separate holdout in Appendix B.2 does not change this fact.

Unconditionally, independently sampled panels can still have covariance through their shared random context: \(\operatorname{Cov}(\bar h,\bar Y)=\operatorname{Cov}(\mu_c,p_c)\). That between-context information can be useful. It is different from the missing within-context paired covariance. Applying the original single-\(D\) theorem to context-homogeneous bags without accounting for this change also changes the model.

More precisely, if each bag first draws one common context but the loss still uses global centering, put \(d_c=p_c-\mu_c\). The same variance expansion gives

\[
\mathbb E\ell_{\mathrm{ind}}
=L(h)+2\mathbb E_c\operatorname{Cov}(h(X),Y\mid c)
+(k-1)\operatorname{Var}_c(d_c).
\]

Even a coupled iid-within-context bag has the last additional term under global centering. Contextwise centering removes that term but does not restore the independent panels' missing within-context covariance.

### An exact indistinguishability example

Use the paper's two-hypothesis family with fair binary \(X\):

\[
h_1(x)=\tfrac12+\tfrac{\sqrt\beta}{2}(2x-1),\quad
h_2(x)=\tfrac12-\tfrac{\sqrt\beta}{2}(2x-1),\quad0<\beta<1.
\]

Both have the same \(P_X\), the same \(P_Y=\mathrm{Bernoulli}(1/2)\), and zero mean gap. Their independent feature-panel/count distributions are exactly identical for every bag size and sample count. A selector between them cannot have error below (1/2) in both worlds. Even an unrestricted predictor has worst-world expected excess square loss at least \(\beta/4\), by the midpoint identity. The same example can be repeated at every context.

Thus there is no universal replacement \(\widetilde O(k/\beta)\) guarantee for independent panels. More samples of identical marginal laws do not identify the missing coupling. This conclusion does not rely on the unresolved lower-bound proof in Appendix A.

### The rate that survives

The **population-mean separation branch** does survive. Suppose one of two stable candidate regression functions is correct and a known context has

\[
|\mathbb E[h_1(X)\mid c]-\mathbb E[h_2(X)\mid c]|=|\Delta_c|>0.
\]

Estimate the two prediction means from an independent feature panel and the label mean from an independent target panel, then choose the closer prediction mean. Hoeffding and a union bound give error at most \(\delta\) when each panel has order \(\Delta_c^{-2}\log(1/\delta)\) bounded iid observations. If feature means are known, only the target-panel estimation cost remains. If reports must come in size-\(k\) bags, the number of label bags is a ceiling of the required underlying sample count divided by \(k\), with at least one bag. Both panels' acquisition costs must be counted.

This is the \(\Delta^{-2}\) mechanism from Appendix A, p. 12. It can be used whenever there is sufficient mean separation, without importing the paper's branch-selection threshold. It does **not** preserve the \(k/\beta\) branch or the full minimum of the two rates. Several contexts help only if their mean map separates the candidate hypotheses, with additional conditioning and allocation costs when necessary. A shared context label alone is not such a premise.

### The two scoped dependencies

**Scott–Zhang 2020:** [scoped note](SCOTT-ZHANG-2020-LLP-SCOPED.md). Main §3, p. 5, observes the actual bag's empirical proportion, so the entire paper must not be described as independent population panels. Main §3.1, p. 6, separately assumes known true mixture proportions. Under common class-conditional feature laws and independent instances, its Theorem 5 / §3.1 bound scales with

\[
\left[\sum_i\bar n_i(\gamma_i^+-\gamma_i^-)^2\right]^{-1/2},
\]

apart from the stated loss, class-complexity and confidence factors. Here \(\bar n_i\) is the harmonic mean of the paired feature-bag sizes. This population-mixture rate does not need the realized label count of each feature bag when the true proportions are already known. Estimating those proportions from independent label panels adds error amplified by small mixture gaps. That extension is not the unchanged known-proportion theorem. Main Theorem 6 and supplement Theorems 10–11 instead use empirical proportions, bag merging and the `(LP)` condition on true-proportion heterogeneity. Arbitrary fluctuations of same-population counts do not meet that condition.

**Quadrianto et al. 2009:** [scoped note](QUADRIANTO-2009-LABEL-PROPORTIONS-SCOPED.md). Section 2, pp. 2351–2352, describes set fractions and assumes \(X\perp C\mid Y\). Equation (3), p. 2354, explicitly uses population probabilities \(\pi_{cy}=P(Y=y\mid C=c)\). Its Theorem 5, p. 2359, controls mean-operator estimation from iid feature samples and a known full-rank mixing matrix. At fixed well-conditioned mixing, its feature-mean errors have the usual inverse-square-root sample scale. This is a population-mixture identification route. It is not a distribution-free assertion that an arbitrary realized count can replace a population probability, and an independently estimated mixing matrix requires the perturbation control discussed in §5.7 rather than a free substitution.

Both routes require structural information beyond knowing \(P(X\mid C)\) and \(P(Y\mid C)\). Their common \(P(X\mid Y)\) assumption has the direction \(X\perp C\mid Y\). The crossed-panel factorization \(P(Y\mid C)=P(X\mid C)\Theta\) used for a stable next-word conditional instead needs a premise such as \(Y\perp C\mid X\). These directions are not interchangeable.

There is nevertheless a concrete **reversed-role population mapping**, rather than a reason to dismiss the dependency. Map the source paper's class label to the input class \(D\), its feature to the target \(Y\), and its set index to \(T\). Then the TD panel estimates the mixing weights \(W_{td}=P(D=d\mid T=t)\), the TY panel samples the mixture feature law, and the common class-conditional feature laws become \(P(Y\mid D)\). With one-hot features of \(Y\), their class means are exactly the rows of \(\Theta\). Quadrianto's mixture identity becomes

\[
P(Y=y\mid T=t)=\sum_d W_{td}\Theta_{dy}.
\]

This mapping requires \(Y\perp T\mid D\), sufficient rank and conditioning, and a valid sampling model. Independently estimated weights need additional perturbation control. Quadrianto's located theorem controls mean-operator estimation rather than the complete next-word log-loss guarantee. Scott–Zhang's binary balanced-error statement also has a different target. This is a precise statement-level source connection, without certification of Astra's theory or experiment.

### Boundaries for the current FP records

The original request concerns the separate \(TD\) and \(TY\) panels registered in `7b8ff15`, with the prospective correction in `48ec968`. Subsequent Astra commits `6a8fe50` and `fff0f7a` freeze and report that experiment, then register matched bag histograms. They are preserved without literature-side certification of the core results.

The matched-histogram interface registered at fff0f7a does retain the realized bag coupling. If a hypothesis depends only on the recorded 17 input classes, its sum over the original feature multiset is exactly computable from the input histogram. This identifies an observation-level connection to the paper. It does not automatically import the theorem: the new targets are multiclass, deployment uses log loss, and uniformly partitioning a fixed sequential tape is a finite-population experiment rather than iid draws from \(D\). Likewise, disjoint subsets drawn without replacement from a fixed tape should not be silently called conditionally independent iid panels. Their finite-population dependence must be handled in the experiment's own analysis.

Later concurrent commits through5732908 report the matched-bag experiment and freeze a shared-position communication comparison. They add no literature request and are preserved without extending the present source theorem to that communication problem.\n\nNo new FP architecture, learning rule or empirical reproduction is proposed here. The requested literature distinction is complete. Further reading is needed only if Astra requests an independently established replacement for the unresolved proof steps or a specific population-mixture extension. Ordinary original OpenAI251 reading resumes at its prepared but unread introduction.
