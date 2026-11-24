# Efficient Prediction of Pass@k Scaling in Large Language Models

## Edition and actual coverage

Joshua Kazdan, Rylan Schaeffer, Youssef Allouah, Colin Sullivan, Kyssen Yu, Noam Levi and Sanmi Koyejo, **arXiv:2510.05197v1**, submitted October 6, 2025 at 17:42:27 UTC. The primary history inspected November 24, 2026 shows only v1. This note concerns that **24-page edition**. [Record](https://arxiv.org/abs/2510.05197v1) · [PDF](https://arxiv.org/pdf/2510.05197v1) · [Complete source](https://arxiv.org/src/2510.05197v1)

The official NeurIPS 2026 poster and an author's publication page establish the work's conference association. The poster lists Colin Sullivan second, unlike arXiv v1, and exposes no final manuscript link. The author page links arXiv. **The accepted final text has not been authenticated or read.** An `iclr2026` source directory and final-copy style command do not establish ICLR acceptance. This is outside-author research, not an official OpenAI or Anthropic release. No AI-assistance disclosure was found in the inspected manuscript. [Conference](https://neurips.cc/virtual/2026/poster/150130) · [Author](https://youssefallouah.com/publications.html)

The main reader covered the complete active TeX and macros, §§1–7, Appendices A–F, all formulas and proofs, both algorithms, **nine figures containing fifteen active image assets**, author-contact thanks, contribution marker and all **61 printed references**. There are no tables or ordinary body footnotes. All figure assets were inspected, with original PDF checks on pp. 7–8, 16 and 18–19 for the disputed formulas. Source files are under `literature/corpus/pisf_prior_art/2510.05197v1/`. Supporting agents handled version retrieval and two bounded checks, not full-paper reading. No experimental code was replayed, and no formal proof or complete theorem certification is claimed.

## Original question and statistical target

For m benchmark questions with fixed success probabilities p_i, independent repeated attempts give

\[
P_k=\operatorname{pass}_{\mathcal D}@k
=\frac1m\sum_{i=1}^m[1-(1-p_i)^k].
\]

The evaluator has a total budget B, assigns b_i attempts to each question and sees s_i successes. The paper emphasizes extrapolation with B/m<k<B, when uniformly allocating the budget does not provide k samples per question. The ordinary unbiased combinatorial estimator

\[
\widehat P_{i,k}=1-\frac{{b_i-s_i\choose k}}{{b_i\choose k}}
\]

requires k≤b_i. Its failure outside that range motivates a model-based forecast, not an identification theorem for unrestricted mixing distributions. The proposed contribution combines direct Beta–Binomial fitting with a simple adaptive allocation rule. The measured loss is squared error in the aggregate pass@k curve. [§§1–3]

The critique of prior approaches has three components. Reusing the same outcomes produces correlated estimates at different k, their variances vary with k, and a fitted power law may be misspecified or used before its asymptotic regime. The alternative discretized-Beta baseline first estimates individual rates, bins them and fits a scaled Beta distribution. Kazdan et al. argue that this loses information about binomial observation noise and distorts the low-probability tail. Their experiments extend the earlier distributional fit into a finite-k forecasting baseline, rather than merely comparing the earlier paper's asymptotic slope calculation.

Some descriptions are internally inconsistent. The regression display fits −log(pass@k), while the subsequent two-power example is about failure 1−pass@k. The displayed regression loss sums over a question index although its residual depends on k. The scaled-Beta forecast has a repeated alpha where the scale parameter is intended. These v1 notation issues make exact baseline implementation harder to reconstruct from the manuscript alone. Correlated, heteroskedastic residuals do not by themselves prove OLS coefficient bias under a correctly specified mean. They invalidate ordinary independent equal-variance uncertainty calculations and can reduce efficiency. The misspecification and logarithmic-transformation issues are separate. [§3, Appendix A]

## Direct fitting and adaptive allocation

The working hierarchical model is p_i drawn independently from Beta(alpha,beta), with conditionally independent Bernoulli attempts. The displayed single-question likelihood is

\[
L_i(\alpha,\beta)
={b_i\choose s_i}
\frac{\mathrm B(s_i+\alpha,b_i-s_i+\beta)}{\mathrm B(\alpha,\beta)}.
\]

The procedure maximizes the product over positive alpha,beta and predicts the population-Beta expectation. Equivalently,

\[
\widehat P_k
=1-\frac{\mathrm B(\widehat\alpha,\widehat\beta+k)}
{\mathrm B(\widehat\alpha,\widehat\beta)}.
\]

This is a structural extrapolation assumption about unobserved tail mass. It does not derive tail identification or an honest confidence interval from finite-depth counts. For finite positive fitted parameters, the forecast tends to one as k grows, since the Beta family has no atom at zero. A genuinely impossible-question fraction therefore lies outside its exact asymptotic model. [§4.1]

The estimator plugs in a population distribution, although its introductory target is the finite benchmark average. It is not the posterior mean for the already observed questions, which under the same fitted prior would instead average

\[
1-\frac{\mathrm B(\widehat\alpha+s_i,
\widehat\beta+b_i-s_i+k)}
{\mathrm B(\widehat\alpha+s_i,
\widehat\beta+b_i-s_i)}.
\]

This distinction describes the actual estimator, not a claim that the alternative necessarily has better frequentist risk. The source supplies neither finite-benchmark calibration nor a robustness theorem under Beta misspecification.

Algorithm 1 chooses the question with the **smallest number of successes**, then the smallest number of attempts among those tied, then breaks remaining ties uniformly. It does not directly minimize the empirical success proportion. Algorithm 2 initializes all counts at zero, repeats this selection and one new observation exactly B times, fits the model to all terminal counts, and forecasts. **The sampling rule does not depend on k**, even though the oracle allocation used to motivate it does. The main comparison changes both fitting and sampling. Authors explicitly say that isolating the sampling contribution on the real datasets is difficult and leave detailed adaptive Bayesian variance analysis to future work. [Algorithms 1–2, §4.2]

### Independent bounded check: adaptive likelihood remains usable

The text justifies adaptivity by saying that the likelihood accommodates different b_i. That alone is insufficient, and the literal conditional claim s_i|b_i ~ BetaBinomial is false under outcome-dependent selection. However, **the fitted objective can still be the correct joint-likelihood kernel**.

Write the complete history H_B=((I_t,Y_t)) and let q_t(I_t|H_{t−1}) be a known selection kernel depending only on recorded past data and external randomization, not on an unknown candidate parameter. Under the iid Beta model and conditional Bernoulli independence,

\[
\Pr_{\alpha,\beta}(H_B=h)
=Q(h)\prod_i
\frac{\mathrm B(s_i+\alpha,b_i-s_i+\beta)}{\mathrm B(\alpha,\beta)},
\quad Q(h)=\prod_tq_t(i_t\mid h_{t-1}).
\]

Summing over histories with the same complete labeled terminal counts replaces Q(h) by a factor C(b,s) independent of alpha,beta. Multiplying by the binomial coefficients in the authors' objective also changes only a parameter-independent factor. Thus the same MLE follows. All outcomes used for selection must be retained, with no unrecorded pilot data or additional outcome filtering. The printed fixed-B algorithm meets the predictable-selection requirement. This is an independent clarification, not a proof supplied in v1, and gives no automatic independence, unbiasedness or frequentist interval coverage.

A short counterexample isolates the conditional-distribution error. With two iid Uniform[0,1] difficulties and B=3, the first two attempts sample each question once. The third samples the question with fewer successes, with random tie breaking. Conditioning on question 1 receiving only one attempt gives

\[
\Pr(s_1=1\mid b_1=1)=\tfrac34,
\]

whereas BetaBinomial(1,1,1) assigns probability 1/2. Conditioning on the realized budget selects easier observed outcomes. This does **not** invalidate the joint-likelihood derivation above.

## Oracle allocation theorem and its exact limits

Theorem 1 concerns a different, frequentist plug-in estimator,

\[
\widehat P_k^{\rm plug}
=1-\frac1m\sum_i(1-S_i/b_i)^k.
\]

For fixed k and p in (0,1), the delta method as the **number of attempts b grows** yields

\[
\operatorname{Var}\{(1-S/b)^k\}
=\frac{k^2p(1-p)^{2k-1}}b+O(b^{-2}).
\]

Minimizing the leading independent-question variance under a total budget gives

\[
b_i\propto\sqrt{p_i(1-p_i)^{2k-1}}.
\]

The proof combines a binomial CLT/delta-method lemma with Lagrange multipliers for minimizing sum_i v_i/b_i. It does not analyze the fitted Beta parameters or the actual adaptive policy. [Theorem 1, pp. 7–8, Appendix D.1]

**The v1 theorem instead states that the number of questions tends to infinity. That limit alone does not justify the delta approximation.** An independent exact counterexample takes even m, half the questions with p=1/3 and half with p=2/3, k=2 and B=3m/2. The claimed proportion assigns respective budgets (2,1). Reversing them to (1,2) is feasible and has smaller exact variance:

| p | b | E[(1−S/b)^2] | Var[(1−S/b)^2] |
|---|---:|---:|---:|
| 1/3 | 1 | 2/3 | 2/9 |
| 1/3 | 2 | 5/9 | 53/324 |
| 2/3 | 1 | 1/3 | 2/9 |
| 2/3 | 2 | 2/9 | 29/324 |

Consequently,

\[
\operatorname{Var}(\widehat P_k^{\rm claimed})=\frac{125}{648m},
\qquad
\operatorname{Var}(\widehat P_k^{\rm reversed})=\frac{101}{648m}.
\]

The alternative improves the leading constant by 19.2%, even as m grows. Both estimators have expectation 5/9 against true 13/18, hence the same bias −1/6. Increasing the number of fixed-budget questions does not remove that plug-in bias.

A sufficient repaired asymptotic statement fixes m,k and all internal p_i, takes B→infinity and b_i=Bw_i+O(1) with positive weights. The stated proportion then minimizes the leading 1/B variance. Growing m or k requires further uniform remainder control. Appendix Lemma 5 also omits the multiplicative **B** in its displayed normalized budgets. Zero-variance coordinates require a boundary convention because the feasible set is written with strictly positive budgets.

The oracle weight is not monotone in difficulty. Its logarithmic derivative is (1−2kp)/(2p(1−p)), so it peaks at **p=1/(2k)** and vanishes toward both endpoints. It motivates attention to a low-success-probability region, not indefinitely more budget for increasingly impossible questions. Knowing an exactly zero p removes the exploration problem that an actual evaluator faces.

## Other bounded mathematical checks

**Appendix A's invertibility assertion fails at saturation.** For b=4 and s=2 or 3, the combinatorial pass@3 estimate equals one in both cases, while pass@2 equals 5/6 or one. Thus knowing one estimated k value need not determine every other value, contrary to the stated consequence of Lemma 1. The recurrence can be expressed without dividing by zero, but the displayed ratio proof divides by the zero failure term after saturation. Dependence among the estimators still exists. Appendix A's two endpoint variance identities are consistent with direct Bernoulli/binomial calculations.

**The scaled-Beta likelihood expansion is normalized correctly, but its optimization objective is not.** In Appendices B–C, for p=theta U with U~Beta(alpha,beta), n attempts and c successes,

\[
L={n\choose c}\frac1{\mathrm B(\alpha,\beta)}
\sum_{j=0}^{n-c}(-1)^j{n-c\choose j}
\theta^{c+j}\mathrm B(c+j+\alpha,\beta).
\]

The subsequent negative-log objective drops the parameter-dependent normalizer: it needs **+log B(alpha,beta)**. For n=1,c=0,theta=1 and alpha=beta=t, the true probability is always 1/2. The unnormalized sum equals B(t,t+1), which is 1/2 at t=1 and 1/12 at t=2. Omitting the normalizer therefore changes the fit. The main two-parameter likelihood includes it correctly. Alternating log-sum-exp rescaling does not itself eliminate subtraction cancellation. No released implementation was inspected to determine whether code repeats the appendix error.

The argument about binning also has limited scope. Arbitrary bins alone do not force a universal direction of bias for a correctly specified grouped-data likelihood. Here binomial noise in estimated probabilities and the particular fit are material. The synthetic result is evidence about that implementation, not a general impossibility of binned inference.

## Empirical evidence, all figures and limitations

The real-data study reuses Brown et al. 2024 and Hughes et al. 2024 outcomes, with 10,000 available attempts per selected question on CodeContests, MATH and AdvBench. Uniform baselines shuffle each question's reservoir and take B/m attempts. The combined method selects adaptively from shuffled reservoirs. The experimental setup defines the reference curve from **all** 10,000 available attempts. An earlier paragraph calls the reference withheld, but a disjoint holdout construction is not specified. No independent-reference assumption is established by this description. [§5.1, Appendix F]

The text alternates between k in 10–1,000 and 100–10,000. The actual forecast line plots cover 10–1,000, and the heatmaps display roughly 106–1,000. Main budget-10,000 line plots include six AdvBench models, six Pythia sizes for MATH and three code models. Heatmaps add Pythia70M, Llama3 8B IT for AdvBench and two further code variants. Appendix F's generic 128-prompt description is less specific than the earlier 100–200 range. Exact eligible question sets and the bootstrap replication protocol are not fully specified.

The figures support the following scoped findings:

- **Figure 1:** at B=10,000, dynamic sampling plus Beta–Binomial forecasts usually track the empirical curve closely. Regression often rises too fast and clips at one, while the discretized fit often underpredicts. Gemini1.5Pro and some code settings show less decisive separation. Shading is labeled 95% bootstrap intervals, not proven uniform extrapolation coverage.
- **Figure 2:** for 10,000 latent Uniform[0,1] probabilities and 100 attempts each, the direct fit reports alpha=.995,beta=.998, compared with .895,.922 for the discretized fit. This is one favorable correctly specified example.
- **Figures 3 and 8:** adaptive allocations shift mass toward harder questions compared with uniform allocation, often nearer the displayed oracle histogram. They do not coincide with it, particularly across several MATH settings. These plots do not establish optimality.
- **Figure 4:** the synthetic Uniform case shows a large high-budget MSE reduction. A hard-outlier case shows a smaller improvement, while the Pythia6.9B and many-hard cases largely overlap. The caption's strongest-hard-outlier language should not replace the plotted comparison.
- **Figure 6:** with 100 questions, half at p=.3 and half at p=0, adaptive sampling improves finite-budget MSE for k=1,000. This finite-k result does not make a positive-parameter Beta model able to represent the true asymptotic ceiling of .5.
- **Figures 5, 7 and 9:** broad improvements, sometimes exceeding tenfold, coexist with visible exceptions. For example, at k=1,000 the Gemma2B code panel has intermediate budgets where the dynamic method has higher MSE than the discretized baseline. Some small-budget math and AdvBench settings favor regression. The plots do not support universal superiority across all models and budgets.

Regression is clipped at one before the reported prediction/MSE comparison. The combined method's real-data advantage cannot be wholly assigned to adaptive sampling, since the fitting model also changes. No complete implementation, optimizer settings, repetition counts or independently reproduced curve was established in this reading. The computational price of fitting and selection is not measured alongside generation costs.

## Dependencies and remaining questions

Chen et al. supply the combinatorial estimator. Brown et al. and Hughes et al. supply repeated-attempt datasets and curve-fitting baselines. Schaeffer et al. provide the latent-difficulty/power-law motivation and the discretized distributional method discussed here. Delta-method asymptotics and elementary convex allocation underpin the oracle theorem. Jones et al.'s rare-behavior forecasting is a distinct recent comparison, involving additional information rather than this count-only extrapolation. Reading these citations in this paper does not mark their own sources fully read.

The useful unresolved questions are a finite-budget guarantee for the actual adaptive fitted estimator, robustness to atoms at zero or other Beta misspecification, honest simultaneous curve uncertainty, and what an authenticated final conference edition corrects. The present v1 provides an empirical forecasting procedure with a valid hierarchical joint-likelihood interpretation, not a distribution-free solution to extrapolation. It gives no theorem about total causal future KL, observed reset decisions, learned state formation or charged live-memory costs. No transfer to FP core theory is proposed.
