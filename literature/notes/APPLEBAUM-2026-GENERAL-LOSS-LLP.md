# Optimal Learning from Label Proportions with General Loss Functions

## Source, edition and actual coverage

**Lorne Applebaum, Travis Dick, Claudio Gentile, Haim Kaplan and Tomer Koren.** ICML2026, PMLR306, proceedings pages3228–3275. The official publication date is **September29,2026**, distinct from the July6–11 conference dates. The authors are affiliated with Google Research and Tel Aviv University. [Publisher record](https://proceedings.mlr.press/v306/applebaum26a.html) · [Official final PDF](https://raw.githubusercontent.com/mlresearch/v306/main/assets/applebaum26a/applebaum26a.pdf)

**Fully read by the main reader, November26,2026, Shanghai.** Coverage is all 48 physical PDF pages, §§1–5, acknowledgements and impact statement, AppendicesA–D, every displayed proof and formula, Algorithm 1, three numbered footnotes, Table 1, all six figures with 24 panels and all 51 printed references. References occupypp9–11, A begins onp12, B onp13, C onp29 and D onp43. Page numbers below refer to this PDF, not the volume pagination.

All final text was read in continuous page groups. Original page images were checked onpp5,6,7,8,15,19,23,30,31,33,34,40,43,45,46,47,48. This includes every figure and table and the mathematical displays underlying the local findings below. Source agents prepared metadata and files, and independently checked one specified second-moment calculation. They did not substitute for the main reader's complete reading.

The available [arXiv2509.15145v2](https://arxiv.org/abs/2509.15145v2), dated January29,2026, has a complete TeX package and also 48 pages. It is **not identical to the proceedings edition**. Its embedded bibliography has 48 entries, while the final PDF has 51, with added related work, acknowledgements and cross-reference changes. The final PDF is the reading authority. Obtaining the older TeX does not earn a second full-reading record. No final-version TeX or separate final supplement was authenticated. The appended 48-page PDF contains the supporting material actually read.

This is a peer-reviewed Google-affiliated paper, not an official OpenAI/Anthropic source. Author results, complete reading, bounded independent checks and formal verification are kept separate. No empirical replication or formal proof replay was performed.

## 1. Original question and observation experiment

The paper asks how to learn an individual-level predictor when labels are released only as aggregates over random bags. Its motivating example is predicting advertising conversions when click features remain visible but conversions can be associated only with a group of those clicks. The mathematical experiment is specified in §2.1, p3.

Individual pairs \((X_i,Y_i)\) are iid from one unknown distribution \(D\). A data-independent random partition places them in nonoverlapping bags. The learner receives every feature vector in each bag and the exact aggregate of the labels belonging to **those same realized feature vectors**. Labels can remain stochastic conditional on features. There is no fixed arbitrary tape, adversarial corruption model or adaptive bag construction in this experiment.

The hypothesis class \(H\) is finite. Population risk is

\[
L(h)=\mathbb E_D\ell(h(X),Y),
\qquad
\operatorname{Reg}(h)=L(h)-L(\widehat h^\star),
\]

where \(\widehat h^\star\) is best in \(H\). The Bayes predictor \(h^\star\) minimizes over measurable predictors. Realizability means that a Bayes predictor belongs to \(H\), which permits noisy labels and does not mean zero observed loss.

| Released label information | Observation for a bag of size \(k\) | Loss coverage developed here |
|---|---|---|
| Binary | \(\alpha=k^{-1}\sum_iY_i\), with \(Y_i\in\{0,1\}\) | Any binary loss admitting the required moments |
| Full multiclass histogram | Every \(\alpha_r=k^{-1}\sum_i\mathbf1\{Y_i=r\}\) | General multiclass losses with an integrable squared maximum |
| Total multiclass count | Only \(\alpha=k^{-1}\sum_iY_i\), with numerical labels \(0,\ldots,c-1\) | Losses affine in numerical \(Y\), possibly after removing a predictor-independent term |

Full histograms and numerical totals are different statistical experiments. A sum of class numbers does not determine the histogram.

## 2. Binary estimator and its information source

For binary labels every loss can be written

\[
\ell(h(x),y)=f_1(h(x))+y f_2(h(x)),
\]

with \(f_1(a)=\ell(a,0)\) and \(f_2(a)=\ell(a,1)-\ell(a,0)\). Put \(p=\mathbb EY\) and \(\mu_j(h)=\mathbb Ef_j(h(X))\). The ideal bag estimator, Eq. 2 onp4, is

\[
\ell_b(h,z)=\mu_1(h)+p\mu_2(h)
+(\alpha-p)\sum_{i=1}^k\bigl(f_2(h(X_i))-\mu_2(h)\bigr).
\]

It uses population centering quantities initially, then replaces them by estimates. It can take negative values even though the original loss is nonnegative.

The essential identity is

\[
\mathbb E\left[(\alpha-p)
\sum_i\bigl(f_2(h(X_i))-\mu_2(h)\bigr)\right]
=\operatorname{Cov}(Y,f_2(h(X))).
\]

Terms from different sample indices vanish. The \(k\) matching-index terms survive the factor \(1/k\) in \(\alpha\). Adding \(\mu_1+p\mu_2\) gives \(L(h)\). Thus bag-level label obfuscation preserves a covariance signal even when every bag comes from the same population.

**Lemma 3.1, pp4,13–15**, states unbiasedness and a variance bound independent of \(k\). The proof actually obtains the stronger form

\[
\operatorname{Var}(\ell_b(h,Z))
\le \frac52\operatorname{Var}\bigl(f_2(h(X))\bigr)
\le\frac52\mathbb E f_2(h(X))^2.
\]

The argument conditions on bag features, separates Bernoulli label noise from conditional-mean variation, and expands a centered four-index moment. Only coincident indices and pairings survive. Conditional Bernoulli variance contributes at most one quarter, while the centered feature/conditional-mean product gives the remaining bound. No fourth moment of \(f_2\) is required because the label quantities are bounded.

This differs from EasyLLP's general-loss debiasing, whose individual bag estimator can have variance increasing with \(k\). Here the effective number of aggregate observations is \(m\). With \(n=mk\), a \(m^{-1/2}\) rate is a \(\sqrt{k/n}\) rate, not a claim that aggregation costs nothing.

For square loss, \(f_1(a)=a^2\), \(f_2(a)=1-2a\). For log loss,

\[
f_1(a)=-\log(1-a),\qquad f_2(a)=\log((1-a)/a).
\]

If \(a=\sigma(w)\), then \(f_2(a)=-w\) and \(f_1(a)=\log(1+e^w)\). Appendix B.4 bounds their second moments by a constant plus \(\mathbb Ew^2\). Thus the slow-rate theorem permits unbounded logits with finite second moment. Predictions assigning zero probability to possible labels can violate these assumptions.

## 3. Tournament, sample complexity and proof structure

### Estimated centering and robust comparisons

Algorithm 1, p5, works with **\(3m\) bags**, so its total individual sample count is \(n=3mk\). It splits the bags into three independent groups:

- \(S_1\) estimates feature expectations of \(f_1(h_1)-f_1(h_2)\) and \(f_2(h_1)-f_2(h_2)\), using all \(mk\) visible feature vectors and median-of-means estimates.
- \(S_2\) estimates \(p\) by the empirical average of its label proportions.
- \(S_3\) supplies the bags on which the estimated, centered loss differences are evaluated.

A final median of means over \(S_3\) gives \(Q(h_1,h_2)\). The median of an even number of values is defined as the average of the middle two. With consistent grouping this preserves \(Q(h_1,h_2)=-Q(h_2,h_1)\). The tournament eliminates a hypothesis when it loses a comparison by more than \(\beta/2\), and returns any survivor.

Median-of-means block counts scale logarithmically with the allocated failure probability. Uniform comparison statements require the allocation across hypothesis pairs, and the proofs explicitly require enough bags for those blocks. The method is a statistical finite-class tournament, not an efficient optimization guarantee for a large neural hypothesis space.

### Slow rate

Define

\[
V_i=\max_{h\in H}\operatorname{Var}
\bigl(f_i(h(X))-f_i(\widehat h^\star(X))\bigr),
\quad
M_2=\max_{h\in H}
\left(\mathbb E[f_2(h(X))-f_2(\widehat h^\star(X))]\right)^2.
\]

**Theorem 3.2, pp5–6**, gives regret at most \(\beta\) with probability at least \(1-\delta\) at a sufficient sample order

\[
\frac{kV_2\log(|H|/\delta)+V_1\log(|H|/\delta)
+M_2\log(1/\delta)}{\beta^2}
+k\log(|H|/\delta).
\]

The displayed assumptions require finite maximal second moments of both loss components. This is a slow rate, with a linear rather than quadratic dependence on bag size in the leading general-loss term. The comparison to earlier optimality results relies on cited square-loss lower bounds. It does not establish that every possible loss requires that sample order.

The proof inB.2 first conditions on the nuisance samples. If \(E_i\) are true feature means, \(\widehat E_i\) their estimates and \(\widehat p\) the estimated prior, its conditional bias is controlled by feature-mean errors, prior error and their product multiplied by \(k\). A conditional variance estimate then permits MoM concentration on \(S_3\). Proposition B.1 separates hypotheses with regret at least \(\beta/4\) from nearer competitors. The best hypothesis survives every comparison, and every hypothesis with regret at least \(\beta\) is removed. Uniform concentration over all pairs completes the argument.

The paper points to Høgsgaard–Paudice2025 for an infinite-class extension, but does not supply that extension's full argument here. The theorem recorded above remains the finite-class result.

### Fast rate and approximation error

For \(\bar\ell(a,b)=f_1(a)+bf_2(a)\), the quadratic sandwich condition, Eq. 6, is

\[
\frac{C_i}{2}(f_i(a)-f_i(b))^2
\ge \bar\ell(a,b)-\bar\ell(b,b)
\ge \frac{c_i}{2}(f_i(a)-f_i(b))^2,
\qquad i=1,2.
\]

The paper states Eq. 6 for all \(a,b\in[0,1]\). Its examples discuss restricted predictor and conditional-Bayes ranges when finite constants require them. Those restrictions must accompany an application. Write

\[
\gamma_i=\mathbb E\left[
\bigl(f_i(\widehat h^\star(X))-f_i(h^\star(X))\bigr)^2
\right].
\]

**Theorem 3.5, p7**, gives sufficient sample order

\[
\left[
\frac{k/c_2+1/c_1}{\beta}
+\frac{k(C_2/c_2+1)\gamma_2+(C_1/c_1+1)\gamma_1}{\beta^2}
+k
\right]\log(|H|/\delta).
\]

When realizable, \(\gamma_i=0\), yielding the stated \(\widetilde O(k/\beta)\) behavior. Only the lower curvature constants remain in that specialization. Nonrealizable approximation error introduces inverse-quadratic terms.

Appendix B.6 proves the variance-to-regret comparison

\[
\gamma_{f_i}(h,\widehat h^\star)
\le \frac4{c_i}\operatorname{Reg}(h)
+2(C_i/c_i+1)\gamma_{f_i}(\widehat h^\star,h^\star).
\]

It expands a squared difference through the Bayes predictor, applies the two sandwich inequalities, bounds the cross term by Cauchy–Schwarz and solves the resulting quadratic inequality. Substitution into the two cases of Proposition B.1 produces the rate.

For log loss, the excess conditional loss is Bernoulli KL, equivalently the Bregman divergence of the softplus function in logit coordinates. Appendix B.5 uses its bounded second derivative for smoothness and a **bounded logit interval** for a positive lower curvature bound. Therefore the fast log-loss claim has stronger conditions than mere finite squared logits. It is not the slow-rate theorem's unrestricted finite-moment model with \(\beta^{-2}\) simply replaced by \(\beta^{-1}\).

### Unequal bag sizes

Appendix B.3, pp23–25, uses \(2m\) bags. It places the largest half in the nuisance-estimation group and the smallest half in the evaluation group. Theorem B.2 states a counterpart with average bag size \(\widehat k\) replacing \(k\). This preserves many feature samples for estimating nuisance quantities while retaining \(m\) bag observations. The printed implementation does not specify a new size-weighted prior formula, which matters for its stated concentration step. The exact limitation is recorded below.

## 4. Multiclass statements and their limits

### Full histogram

Let \(p_r=\Pr(Y=r)\), \(E_r=\mathbb E\ell(h(X),r)\), and \(\ell_r(x)=\ell(h(x),r)\). Eq. 28, p29, defines

\[
\ell_b(h,z)
=\sum_{r=0}^{c-1}(\alpha_r-p_r)
\sum_{i=1}^k(\ell_r(X_i)-E_r)
+\sum_{r=0}^{c-1}p_rE_r.
\]

The same matching-index argument gives unbiasedness. Lemma C.1 claims

\[
\operatorname{Var}(\ell_b(h,Z))
\le64\,\mathbb E\|\ell(h(X),\cdot)\|_\infty^2.
\]

Its printed proof has the missing label-noise term discussed below. A separate bounded argument does support this ideal-estimator bound. That does not independently validate every subsequent use with estimated centering.

The algorithm again compares loss differences. Feature loss means are estimated from \(S_1\), class priors by coordinatewise MoM from \(S_2\), and bag comparisons from \(S_3\). Define

\[
D_\ell^2=\max_{h\in H}
\mathbb E\max_r
\bigl(\ell(h(X),r)-\ell(\widehat h^\star(X),r)\bigr)^2,
\]

\[
\Sigma=
\sqrt{\max_{h\in H}
\sum_r\operatorname{Var}
\bigl(\ell(h(X),r)-\ell(\widehat h^\star(X),r)\bigr)}.
\]

**Theorem C.2, pp30–31**, states sufficient sample order

\[
\frac{[k\log(|H|/\delta)+c\log(c/\delta)]D_\ell^2}{\beta^2}
+\frac{k\Sigma\log(c|H|/\delta)}{\beta}.
\]

The proof also assumes a minimum MoM group count of order \(\log(c|H|/\delta)\). That prerequisite should be retained when implementing the displayed rate, including degenerate moment cases.

The introduction's shorter expression omits the latter terms. The complete result is **not wholly independent of \(c\)**. Bounded losses remove a class dependence inside the maximum envelope, while the displayed \(c\log(c/\delta)\) term and \(\Sigma\) remain. Their being smaller terms depends on the asymptotic regime. For unbounded losses, Appendix C.4 controls the maximum of centered sub-Gaussian components by a union bound and integration of the tail, yielding logarithmic dependence on \(c\). It does not provide a full-histogram fast-rate theorem.

Appendix C.5 tracks componentwise nuisance errors using \(\operatorname{Var}(\alpha_r)\le p_r/k\). It bounds sums involving \(\sigma_r\sqrt{p_r}\), expands the conditional variance into a centered contribution and three nuisance-error contributions, then applies the same tournament proposition. The conditional covariance matrix repeated onp40 has the same omitted diagonal term asC.3. The complete theorem is therefore recorded as an author result with an unresolved printed proof step, not as independently certified by this reading.

### Total numerical count

Appendix C.2, p31, extends the binary-style argument when the loss is affine in numerical \(Y\). Examples are Poisson log loss and squared numerical regression loss after removing \(Y^2\), which does not affect comparisons between predictors. Multiclass cross-entropy and the multiclass Brier score do not have this representation.

The authors state an additional \(c^2\) inflation in the relevant variance/moment bounds because the numerical conditional label mean now ranges across \(0,\ldots,c-1\). The detailed adaptation is omitted. This is the scope of their method, not a proved necessity theorem saying every total-count learning problem must use an affine loss.

## 5. Experiments, figures and reproducibility boundaries

The experiments optimize the proposed bag loss with Adam. They do **not** run the finite-\(H\) MoM tournament. Every reported task is binary.

| Task | Setup described in Appendix D |
|---|---|
| MNIST even versus odd | 60,000 training and10,000 test images. CNN with 32/64 filters, pooling, dropout 0.5 and a final logit |
| CIFAR10 animal versus machine and cat versus rest | Two separate binary tasks, 50,000 training and10,000 test images, the same CNN layout |
| Higgs | First 10,000 examples reserved for testing from the 11-million-example dataset. Four 300-neuron hidden layers |
| Adult | One-hot categorical features and rescaled numerical features. One 32-neuron hidden layer |
| Online Criteo | The paper describes 37 million chronological impressions over seven days. Thirteen count and 26 categorical features, embeddings and 256/128/64 hidden layers |

Table 1, p45, gives every categorical feature's bucket count and embedding dimension. Counts range from 10 to 10,000 and dimensions from 10 to 70. Count features use 40 buckets and 10-dimensional embeddings. The model is a learned neural embedding system, not a finite-state learner analyzed by the theorem.

Batch data are shuffled once into nonoverlapping bags, with leftover examples discarded. **Bag membership is held fixed across epochs**, preventing repeated regrouping from revealing additional label information. Bag sizes range from 1 to 2048. Each optimizer batch contains 4,096 examples, so the largest size still gives two bags. Sixteen learning rates from \(10^{-7}\) to \(10^{-1}\) are searched, with ten repetitions per configuration.

For batch tasks, label smoothing uses \(\epsilon=0.1\) in the loss. Actual event labels and released bag proportions are not altered. Online Criteo uses unsmoothed cross-entropy. Its chunks contain 65,536 examples, and predictions are evaluated before updating on that chunk. There are five repetitions, and the learning rate is selected using average performance across the stream.

The practical estimator uses a global training prior for batch tasks and a current-chunk prior online. Model-dependent feature means are estimated from the **other bags in the same optimizer batch**, and gradients include those terms. Their estimates change with the network parameters. This is a practical leave-one-bag-out implementation, not the theorem's three independent fixed datasets. Conditional independence claims for a fixed model should not silently be extended to an adaptively fitted model and a prior estimated using overlapping data.

Figures 1 and 3 show selected and complete batch log-loss curves. GeneralUPM improves many larger-bag cases over EasyLLP and proportion matching. Proportion matching performs best at small bags and is especially strong on MNIST even/odd. The full plots show near-trivial performance at 2048, which is omitted from the selected Figure 1. Figure 2 shows online mean and per-chunk log loss, including the 2048-bag trajectory.

Figures 4 and 5 give corresponding batch AUC curves. Figure 6 gives online AUC. The broad ordering is similar, but EasyLLP also improves over proportion matching at large bags on online AUC. All24panels were visually checked, including axis ranges, legends and uncertainty bands. No precise graph values were invented from raster positions.

**The reported batch score is selected using test performance over both learning rates and stopping epochs.** AUC and loss select their own best configurations. These are not untouched test evaluations of one independently selected checkpoint. Error bars are one standard error across repetitions, not protection against configuration-selection bias. The text does not supply a separate validation-selection protocol. This limits how strongly the comparisons support an out-of-sample quantitative advantage.

The stated hardware is a cluster of virtual machines with Tesla P100 GPUs,64 GB memory and virtualized CPUs. No end-to-end resource-priced learning theorem, total training-hour comparison or multiclass experiment is supplied. No code execution or empirical reproduction was performed here.

## 6. Bounded independent checks

### 6.1 Binary covariance and variance

An exact rational check used

\[
\Pr(X,Y)=(3/8,1/8,1/8,3/8)
\]

on \((0,0),(0,1),(1,0),(1,1)\), with \(h(0)=1/4\), \(h(1)=3/4\), and square loss. Here \(p=1/2\), \(\mu_1=5/16\), \(\mu_2=0\), and individual risk is \(3/16\).

Exhausting all bags for \(k=1,2,3,4\) gives estimator mean \(3/16\) each time. Variances are respectively \(3/64,1/16,13/192,9/128\), below the lemma's \(5/8\) bound for this example. This checks a concrete coupling and moment calculation, not every distribution.

### 6.2 Square-loss constant in Example 3.4

Onp6 the paper correctly writes

\[
(f_2(a)-f_2(b))^2=4(a-b)^2
=4(\bar\ell(a,b)-\bar\ell(b,b)),
\]

but then prints \(C_2=c_2=2\). Under Eq. 6's normalization the sharp equal constant is **\(1/2\)**. For \(a=1,b=0\), the printed lower bound is 4 while the excess loss is1. A larger upper constant is harmless, but the lower constant 2 is invalid. This is a local example error, not a contradiction of the symbolic curvature theorem.

### 6.3 Missing shift multipliers in the binary proof

Onp19, putting \(d=E_2-\widehat E_2\) and \(q=p-\widehat p\), sums of shifted centered variables must be \(U+kd\) and \(V+kq\). The printed expansion replaces them by \(U+d\) and \(V+q\). This changes subsequent powers of \(k\) onp20.

Retaining the correct shifts gives a bound of the form

\[
\operatorname{Var}(\widetilde{\Delta\ell}_b\mid S_1,S_2)
\lesssim
\sigma_{f_2}^2+kd^2+kq^2\sigma_{f_2}^2+k^2d^2q^2.
\]

For example, expanding \((U+kd)^2(V+kq)^2\) with the four-term square bound and using the centered moment calculation fromB.1 yields these terms. The stated feature/prior concentration bounds and \(m\gtrsim\log(|H|/\delta)\) still make them \(O(\sigma_{f_2}^2)\). Thus the missing multipliers are a genuine printed algebra error, while this bounded correction does not overturn the fixed-size rate. It is not a complete independent audit of Theorem 3.2.

### 6.4 Missing label-noise diagonal in the multiclass proof

Onp33 the off-diagonal identity for \(\alpha_r\alpha_s\), \(r\ne s\), is extended to the whole matrix. Put

\[
\sigma=\sum_i\eta(X_i),\quad
\widetilde\sigma=\sigma-kp,\quad
\Sigma_\eta=\sum_i\eta(X_i)\eta(X_i)^\top.
\]

The correct conditional matrix is

\[
\mathbb E[(\alpha-p)(\alpha-p)^\top\mid B]
=\frac1{k^2}
\left[
\widetilde\sigma\widetilde\sigma^\top
+\operatorname{Diag}(\sigma)-\Sigma_\eta
\right].
\]

The printed expression omits \(\operatorname{Diag}(\sigma)\). Page40 repeats that omission with estimated centering.

A four-point exact counterexample to **Eq. 32's intermediate bound**, not to Lemma C.1, uses independent fair binary \(X,Y\), \(k=1\), \(h(X)=X\), and loss vector \(\ell(X)=(X,1-X)\). Then \(p=\eta(X)=E\ell(X)=(1/2,1/2)\). The complete Eq. 28 estimator is \(\mathbf1\{X\ne Y\}\), with variance \(1/4\). Eq. 32 has right side 0 because \(\widetilde\eta=0\). The conditional matrix's missing diagonal is \(\operatorname{Diag}(1/2,1/2)\). These values were computed with exact fractions and independently rechecked by the main reader.

### 6.5 Narrow repair of the ideal multiclass variance bound

There is a direct replacement for the ideal-estimator step. Let

\[
A_i=e_{Y_i}-p,\qquad
B_i=\ell(X_i)-E\ell(X),\qquad
Z=\frac1k\sum_{i,j}A_i^\top B_j.
\]

The pairs are iid across \(i\). \(A_i\) and \(B_i\) within a pair may be dependent. Define

\[
\tau=E(A^\top B),\quad d=E[(A^\top B)^2],\quad
a=E[(A_1^\top B_2)^2],\quad
b=E[(A_1^\top B_2)(A_2^\top B_1)].
\]

The four surviving index patterns are the all-equal case, two diagonal terms, a repeated off-diagonal term and reversed off-diagonal terms. Their counts give

\[
\operatorname{Var}Z
=\frac{d-\tau^2}{k}+\frac{k-1}{k}(a+b).
\]

With \(v=E\|B\|_\infty^2\), the simplex bound \(\|A\|_1\le2\) gives \(d,a\le4v\), and Cauchy–Schwarz gives \(|b|\le a\). Consequently

\[
\operatorname{Var}Z
\le(8-4/k)v
\le32E\|\ell(X)\|_\infty^2.
\]

This supports the author's looser 64 bound for the **ideal** estimator under its stated moment condition, despite the flawed printed route. The expansion needs only the squared maximum of the loss, not a fourth loss moment. The manuscript assumes nonnegative losses, so its maximum notation agrees with the loss-vector norm.

This is a bounded independent lemma repair. It does not validate the estimated-center variance argument, simultaneous concentration, tournament implementation or all of Theorem C.2.

### 6.6 Unequal-size prior estimation

For independent bag proportions with a common Bernoulli prior,

\[
\operatorname{Var}\left(\frac1m\sum_j\alpha_j\right)
=\frac{p(1-p)}{m^2}\sum_j\frac1{k_j}.
\]

This is different from \(p(1-p)/\sum_jk_j\), the variance obtained by weighting each bag by its size. At \(p=1/2\) and nuisance bag sizes \(1,1,100\), the two exact variances are \(67/1200\) and \(1/408\).

Appendix B.3 calls its algorithm the same as the equal-size version and applies Eq. 14with the arithmetic average size. Literal reuse of the unweighted prior average does not justify that step. A size-weighted estimate

\[
\widehat p=\frac{\sum_jk_j\alpha_j}{\sum_jk_j}
\]

does have the claimed individual-sample concentration. The unequal-size implementation needs this clarification, plus control of the nonidentically distributed evaluation bags. The variance calculation is not a claim that every possible variable-size algorithm violates Theorem B.2.

## 7. Observation comparison and remaining questions

The separate \(S_1,S_2,S_3\) groups do **not** replace same-bag feature/label coupling in the evaluation group. If \(\alpha\) instead comes from an independent label panel with the same marginal distribution, the covariance term vanishes:

\[
E\ell_b=\mu_1+p\mu_2
=L(h)-\operatorname{Cov}(Y,f_2(h(X))).
\]

In the exact binary example above this changes the expectation from \(3/16\) to \(5/16\). With several contexts and exact within-context centering, the same issue arises conditionally in each context. In the full-histogram case the missing signal is the sum of the class-indicator/loss-component covariances. This is an observation-model comparison, not a new FP theorem.

The general-loss paper extends the loss coverage beyond the previously read [Busa-Fekete et al. ICML2025](BUSA-FEKETE-2025-NEARLY-OPTIMAL-LLP.md), but preserves realized bag coupling. It does not supply guarantees for arbitrary fixed tapes, unknown sensor channels, public-coin communication, finite physical learner states or autonomous raw-token transition discovery without additional reductions.

Key imported tools are the MoM concentration theorem cited from Lugosi–Mendelson2019, tournament arguments, fast-rate variance comparisons and earlier LLP lower bounds. Those dependencies were read in their use here, not newly credited as full papers. Høgsgaard–Paudice2025 is a possible current dependency for the infinite-class extension. The historical LLP papers need no expanded reading queue merely because they occur in AppendixA.

The authors leave open the tight dependence on class count, fast full-histogram rates, whether the affine restriction can be removed for total counts, and multiclass empirical validation. Further quantitative use should first resolve the estimated-center multiclass proof with the label-noise term restored, specify unequal-size weighting and MoM block counts, and distinguish the practical neural optimizer from the analyzed tournament. The current reading establishes complete source coverage and the explicit local checks above, not a repaired whole-paper theorem or an empirical replication.
