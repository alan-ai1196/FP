# Jones et al. (2025): Forecasting Rare Language Model Behaviors

## Source and actual coverage

Erik Jones, Meg Tong, Jesse Mu, Mohammed Mahfoud, Jan Leike, Roger Grosse, Jared Kaplan, William Fithian, Ethan Perez and Mrinank Sharma. **Forecasting Rare Language Model Behaviors**, [arXiv:2502.16797v1](https://arxiv.org/abs/2502.16797v1), submitted February 24, 2025, 03:16:15 UTC. Jones and Tong have equal-contribution markers; affiliations include Anthropic, Mila and UC Berkeley. The [official Anthropic release](https://www.anthropic.com/research/forecasting-rare-behaviors), dated February 25, links this manuscript. Only v1 appears in the inspected arXiv history. No withdrawal or replacement was observed.

The main reader covered **all 25 pages**: title/author notices, abstract, §§1–7, acknowledgments, Appendices A–E, every active formula and explanatory derivation, all **12 numbered figures** including four boxed prompts, all **11 tables**, six body footnotes and all **61 references**. Complete active TeX, macros, five table inputs, four prompt inputs and the bibliography were read. All eleven actual image assets were viewed; original PDF pages checked the dense formulas, prompts and table layouts, including the partly commented source table on p. 23. Inactive source comments are not reported as published results. [PDF](https://arxiv.org/pdf/2502.16797v1) · [source](https://arxiv.org/src/2502.16797v1).

The ICML 2025 template does **not** establish acceptance. Bounded checks of the PMLR volume 267 contents and official ICML 2025 program found no matching paper; the [first author's publication page](https://people.eecs.berkeley.edu/~erjones/) lists it under preprints. Accordingly this note records an **official Anthropic research preprint**, without asserting an authenticated conference edition or equivalence to one.

Under the project's official-paper policy, this is a complete reading, **not independent theorem certification**. No proof-audit program, formal replay or experimental reproduction was performed. Ordinary-reading notation/reporting discrepancies are retained below without launching a separate audit.

## Original problem and three distinct targets

The paper asks whether relatively few evaluation queries can forecast failures that become visible after many more deployment queries. A fixed model samples output \(o\) given query \(x\); a specified indicator \(B(o)\) defines an elicitation probability

\[
p(x)=\mathbb E[B(o)\mid x].
\]

The central assumption is **the same query distribution at evaluation and deployment**, with independent draws in the main experiment. The method uses an estimated distribution of these conditional probabilities, including nonzero probabilities for behaviors never actually observed in a small evaluation. It does not establish robustness to distribution shift, changing model weights or adaptive attackers (§3 and §7).

The upper-tail quantile \(Q_p(n)\) is defined by an exceedance probability approximately \(1/n\). The authors use it to forecast three different quantities:

1. **Worst-query risk:** the maximum \(p(x_i)\) among \(n\) deployment queries. The quantile is a forecast proxy; the realized maximum remains random.
2. **Behavior frequency:** the query-distribution fraction with \(p(x)>\tau\). Invert the predicted quantile curve to find \(n'\) such that \(Q_p(n')=\tau\), then forecast frequency \(1/n'\).
3. **Aggregate risk:** conditional on the sampled query list, the probability of at least one positive output, \(1-\prod_i(1-p(x_i))\), for independently sampled outputs. Simulations retain the observed empirical probability distribution below its top unobserved tail and substitute extrapolated quantiles above approximately \(1-1/m\).

These are respectively a maximum, a tail frequency and a product probability. They are not interchangeable, and none is a future predictive log-loss or a state-compression objective.

## Method, mathematical motivation and access assumptions

Apply the monotone score

\[
\psi=-\log(-\log p).
\]

Fit a straight line between score and log survival probability using the **ten largest observed elicitation probabilities**. The working assumption is approximately exponential upper-tail decay on this score scale. With convenient intercept notation the fitted extrapolation is

\[
Q_\psi(n)\approx c+d\log n,\qquad
Q_p(n)\approx\exp\{-\exp[-(c+d\log n)]\},\quad d>0.
\]

Thus the extrapolated negative log probability has a power-law form. The comparison method fits a Gaussian to **all** observed scores using their empirical mean and standard deviation, corresponding to a log-normal model for \(-\log p\). It uses the same downstream risk constructions (§3.3).

Appendix B motivates the score by scaling laws, random-search optimization and extreme-value theory. For an actual Gumbel distribution, expanding its upper tail makes log survival approximately affine. The discussion invokes the Fisher–Tippett–Gnedenko classification and the Gumbel domain of attraction as motivation. It does not supply a finite-sample coverage theorem, a uniform error bound at the tested extrapolation factors or a procedure certifying that the ten fitted points already lie in an adequate tail regime. Confidence intervals are explicitly future work.

Three observation regimes matter (§3.2, §4, Appendix C):

- **Full-output probability:** evaluate the probability of one specified output from token log probabilities, using one forward pass.
- **Keyword probability:** evaluate a specified token/keyword after a provided prefix. This uses both probability access and prefilling, and is a narrower target than unrestricted harmful-response frequency.
- **Repeated sampling:** estimate the probability of a response containing the designated keyword from many sampled responses. This is closer to a broad behavior target but remains a keyword proxy and has substantial sample cost.

Probability access supplies information unavailable from a few observed Bernoulli outcomes. Findings in the first two regimes must not be presented as count-only extrapolation guarantees. The paper proposes adaptive stopping and importance sampling as ways to reduce repeated-sampling cost, but does not implement a general adaptive resource theorem.

## Experiments and what their numbers support

### Misuse-related behavior proxies

The query pool contains 100,000 independently generated queries for each of nineteen designated information topics. A helpful-only Claude 3.5 Sonnet generates the queries; filtering removes prompts already containing the target keyword. The main full-output experiments use Claude 3.5 Sonnet and Claude 3 Haiku and their base models. The note records the statistical construction without reproducing the operational chemical or biological prompts (Appendix C.1 and Table 1).

Worst-query experiments vary evaluation size \(m\), then compare forecasts with maxima among held-out groups of \(n=10{,}000,20{,}000,\ldots,90{,}000\) queries. Main-text sizes are 100, 500 and 1,000; tables additionally include 200. Independent evaluation/deployment blocks are formed from the finite 100,000-query pools. **Mean absolute base-10 log error** is a separate metric from ordinary absolute probability error.

| Experiment and reported scope | Gumbel-tail | Log-normal baseline | Source |
|---|---:|---:|---|
| Full-output worst-query risk, pooled mean absolute log error | 1.672 | 2.371 | Table 2 |
| Keyword behavior frequency, pooled mean absolute log error | 0.800 | 3.655 | Table 3 |
| Same frequency, forecasts averaged in log space across evaluation sets | 0.383 | 3.452 | Table 3 |
| Aggregate risk, \(m=1{,}000\), log-error interpretation in main text | 1.286 | 2.523 | §4.4; Table 4 caption issue below |

The main worst-query discussion reports **72%** of forecasts within one order of magnitude and underprediction fractions of **34% versus 72%**. The introduction's 900-to-90,000 example and its 86% headline have a different stated scope; they must not replace the pooled 72% result. Very small absolute errors for extremely rare outputs do not imply small multiplicative errors. Figure 3 shows substantial order-of-magnitude deviations even where a wide log-scale plot looks close to diagonal.

For behavior frequency, thresholds are 0.1, 0.3, 0.5, 0.7 and 0.9, with 1,000 evaluation sets per topic and extrapolation used where the empirical frequency is below \(1/m\). Averaging across many evaluation sets is a different procedure and information budget from forecasting with a single small set.

Aggregate-risk experiments extend to 500,000 queries through **resampling with replacement from the 100,000-query empirical pools**, with ten rollouts (§4.4 and footnote). This is not direct observation of 500,000 new population queries. The paper acknowledges an underestimate beyond the source-pool scale. Individual cumulative-risk trajectories can jump when rare high-probability queries arrive (Figure 4).

### Repeated-sampling “correctness” experiment

The paper samples outputs from Claude 3.5 Haiku for 10,000 queries, using 100 outputs per query and increasing to 500 when fewer than ten queries have nonzero estimated probabilities. Settings are preselected using a 100-query, ten-output pilot with maximum estimated probability below 0.5. Where applied to the full query pool, those repetition levels imply one to five million output generations per setting, not ten thousand total outputs.

The main text reports worst-query MAE 0.172 and log error 0.17; Appendix C.2.4 instead reports MAE 0.12 and log error 0.17. This unresolved discrepancy is not silently averaged or corrected. The appendix compares against the largest observed evaluation probability, with errors 0.29 and 0.47. In the selected subset where evaluation maxima are below 0.5 but deployment maxima exceed 0.5, the forecast detects the crossing in 75% of settings, with MAE/log error 0.16/0.15 versus 0.57/0.73 for that baseline. **The 75% is conditional on this selected crossing subset**, not universal calibration or sensitivity for every deployment.

Empirical tail plots show approximate linear stretches, with curvature and discretization from repeated sampling. The fitted log-normal baseline is not used in this experiment because too many estimated probabilities are zero. Behavior-frequency log errors are 0.76 for individual forecasts and 0.52 after averaging (§4.5, Figures 5 and 8, Appendix C.2.4).

### Synthetic misalignment-related action proxies

Roughly 100,000 generated system prompts vary domains, tone, specificity and examples. Claude 3.5 Sonnet is evaluated on 41 power-seeking, 33 self-preservation and 33 self-exfiltration multiple-choice questions. The target is the model's probability of a designated answer, with 0.5 as the principal frequency threshold. This measures elicited choice probabilities under synthetic prompts, not observed open-ended autonomous behavior or established persistent intent (§5, Appendices D–E).

For individual questions, pooled worst-query log error is **0.057 versus 0.119**, and ordinary MAE **0.050 versus 0.124** (Tables 5–6). The paper also forms ten random subsets of ten questions per trait and aggregates their probabilities by mean, geometric mean or minimum. These scores are **not** the product-based at-least-one-failure probability defined earlier. On these subset scores Gumbel improves pooled log error, **0.104 versus 0.136**, while the baseline has lower ordinary MAE, **0.056 versus 0.073** (Tables 8–9). No uniform dominance across both metrics follows.

For behavior-frequency experiments restricted to evaluation sets whose maximum is below 0.5, Table 11 reports pooled individual log errors **1.046 versus 4.097**, and averaged-forecast errors **0.535 versus 5.386**. These remain empirical errors on the selected synthetic distribution. Table 7 prints all Gumbel rows but only two baseline rows; commented-out source rows and the commented baseline average are not published observations.

## Red-team allocation application

The application chooses whether an entire hypothetical fixed budget should purchase queries from a cheaper Haiku generator or a more expensive Sonnet generator. Price ratios of 10, 20, 50 and 100 are **experimental scenarios**, not verified current service prices. Evaluation uses small sets from both generators; proposed deployment query counts vary between 10,000 and 90,000 subject to feasible evaluation sizes.

Across 223 reported settings the forecasts choose the generator with larger realized worst-query risk **63%** of the time, compared with 54% for the majority-choice baseline and 50% random choice. Accuracy rises to **79% only in the subset where the actual worst-query probabilities differ by more than 100-fold**. That post-outcome conditional statistic must not be presented as the unconditional allocation success rate. This is a comparison between two forecasted fixed choices, not an adaptive bandit regret or optimal-allocation theorem (§6, Figure 6).

## Reporting and notation qualifications encountered during reading

- The displayed §3.3 intercept signs are inconsistent: \(\log(1/n)=aQ+b\) implies \(Q=-(\log n+b)/a\), whereas the printed next expression has the opposite sign on \(b\). The \(c+d\log n\) notation above avoids carrying that mismatch into the method description. This is a transcription-level observation, not a reconstructed implementation check.
- Table 4's caption says ordinary mean absolute error, although entries exceed one and §4.4 explicitly discusses log errors. The table above follows the main-text interpretation and preserves the inconsistency.
- Figure 6's generator-count legend conflicts with its caption/star positions concerning which generator has ten times as many queries. Allocation conclusions above use the stated experimental procedure, not that inconsistent legend.
- The 0.172/0.12 repeated-sampling MAE discrepancy remains unresolved. The paper's use of a 50% underprediction fraction as an “unbiased” diagnostic concerns directional balance, not a proved equality between forecast expectation and target expectation.

None of these observations establishes an alternative empirical result. Author-linked analysis code, raw experimental measurements and a final conference manuscript were not authenticated or replayed in this reading.

## Dependencies, open questions and retained scope

The paper draws on classical extreme-value theory, neural scaling-law work including Kaplan et al., best-of-many/random-search reasoning, language-model red teaming, and previous elicitation/behavioral evaluations. Appendix A distinguishes work on average model loss from rare behavior probabilities, and direct behavioral testing from forecasting an unseen probability tail. These citations were read as part of the bibliography and discussion; their full papers were not recursively reread.

The main open issues are uncertainty intervals; when the tail approximation is accurate at finite \(m,n\); efficient estimation when probability/prefix access is unavailable; selection bias and query-distribution shift; adaptively changing queries or models; and the relationship between proxy behaviors and deployment outcomes. The work supplies substantial empirical forecasting evidence on its tested distributions. It supplies **no distribution-free rare-event certificate, finite-sample simultaneous coverage result, or adaptive stopping guarantee**. No FP object mapping, future causal-KL bound, reset policy, installed representation size or live-memory theorem is inferred.
