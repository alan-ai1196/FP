# Ye 2026 — variance-adaptive confidence regions for fixed-benchmark binomial mixtures

## Source, edition and actual coverage

Kuancheng Ye, University of California, Irvine, *Variance-adaptive confidence regions for fixed-benchmark binomial mixtures, with application to LLM evaluation*, **arXiv:2611.21266v2**. First submission November 16, 2026; this revision November 17, 2026, 08:51:50 UTC. This record concerns the author preprint; refereed acceptance was not established. [Primary metadata](https://arxiv.org/abs/2611.21266v2) · [Exact PDF](https://arxiv.org/pdf/2611.21266v2) · [TeX source](https://arxiv.org/src/2611.21266v2).

**Fully read on November 24, 2026, Shanghai:** all **84 physical pages**, comprising the 27-page main paper and 57-page supplement. The main assistant read §§1–10, declarations, Supplement §§S1–S15, every formula and proof, all seven main and 46 supplementary tables, six figures, Algorithm 1, and both bibliographies. The complete main/supplement TeX, all 49 active external table inputs and both compiled bibliographies were covered. There are no body footnotes or author thanks. Bibliographies contain 64 and 23 entries, respectively, with 68 distinct citation keys. The absent source refs.bib does not leave a reading gap because both compiled bibliographies are supplied.

Actual PDF images were inspected for all six figures, on physical pp. 11, 21, 73–75 and 79, and for the coverage construction, algorithm, identification theorem and selected dense proof layouts on pp. 8–9, 12, 37 and 40. Tables were read in their complete source, including every longtable continuation. Local source: literature/corpus/pisf_prior_art/2611.21266v2/; the ignored inventory maps every section, table, figure and bibliography to its source and PDF page. Mechanical source preparation was delegated; the main assistant performed the paper reading.

The author discloses Claude and Codex assistance with proofs, code and writing, and states responsibility for checking the final work. **This is an outside author's paper, not an official Anthropic/OpenAI release.** The paper's proofs were read, and the small exact construction in §8 below was independently checked. Neither the entire theorem suite nor the computational certificates were independently certified. No author experiment, code test, interval solver or formal proof was replayed.

## 1. The statistical question and the target that changes the answer

Fix arbitrary success probabilities \(p_1,\ldots,p_m\in[0,1]\), and observe independent counts
\[
c_i\sim\operatorname{Bin}(n,p_i).
\]
There are \(m\) benchmark problems and \(n\) rollouts per problem. The target is the **fixed benchmark's empirical latent distribution**
\[
F_m=\frac1m\sum_{i=1}^m\delta_{p_i},
\qquad
\theta_h(F_m)=\int h(p)\,dF_m(p).
\]
Coverage is conditional on this entire fixed vector. It is not initially coverage for an unknown population law \(G\) generating new problems. Although \(F_m\) has equal-weight atoms, the confidence region optimizes over arbitrary probability laws on \([0,1]\); it does not assume a known small component count.

The principal target is \(h_\delta(p)=\min(p/\delta,1)\), a softened solvability functional. Other targets are \(\mathbf1\{p\ge\gamma\}\), \(\mathbf1\{p>0\}\), and \(\operatorname{pass}@k=1-(1-p)^k\). For integer \(k\ge1\),
\[
(1-e^{-1})h_{1/k}(p)\le1-(1-p)^k\le h_{1/k}(p).
\]
This makes the softened quantity interpretable, but does not identify it with pass@\(k\). Near-zero probabilities can resemble zero under a finite rollout budget, making exact solvability especially difficult. The application obtains informative lower bounds for large-\(k\) pass rates, often with upper endpoints near one.

If instead the \(p_i\) are iid from \(G\), inference for \(\theta_h(G)\) must also account for the random composition of the benchmark. The paper supplies that second layer explicitly. The substantial fixed-benchmark width advantage does not automatically survive it.

## 2. Candidate-specific variance, rather than the iid-mixture variance

Let
\[
P_k(p)=\Pr\{\operatorname{Bin}(n,p)\ge k\},\quad
T_k=\frac1m\sum_i\mathbf1\{c_i\ge k\},
\]
with \(P_0=1,P_{n+1}=0\). Define
\[
\mu_k(F)=\int P_k\,dF,\qquad
V_k(F)=\int P_k(1-P_k)\,dF.
\]
Then \(E_{\boldsymbol p}T_k=\mu_k(F_m)\) and
\[
m\operatorname{Var}_{\boldsymbol p}(T_k)=V_k(F_m).
\]
An iid count-mixture calibration instead uses \(u(\mu_k)=\mu_k(1-\mu_k)\). The excess is exactly
\[
u(\mu_k(F))-V_k(F)=\operatorname{Var}_F(P_k).
\]
Heterogeneity can therefore make the conditional variance much smaller. With half the fixed probabilities zero and half one, each interior tail frequency is deterministic, whereas the iid-mixture variance is \(1/4\). Figure 1 displays the variance ratios across tail indices for five simulated laws.

This does **not** give an estimator that knows the true variance. \(P_k(1-P_k)\) generally has degree \(2n\), while a count-mixture distribution identifies only the first \(n\) moments. In the fixed-vector experiment, the expectation of a statistic of one count per problem is polynomial of degree at most \(n\) in each \(p_i\); this rules out globally unbiased estimation of the degree-\(2n\) variance functional. The method instead tests each candidate law using **that candidate's** variance.

For a tail-index set \(K\) fixed before observing the data, put
\[
L=\log(2|K|/\alpha),\qquad a=\sqrt{2L/m},\qquad b=L/(3m).
\]
The Bernstein radius is \(r_B(V)=a\sqrt V+b\). A tighter option is
\[
r_{\mathrm{Be}}(V)=V\,h_B^{-1}\!\left(\frac{L}{mV}\right),
\quad h_B(t)=(1+t)\log(1+t)-t,
\]
with \(r_{\mathrm{Be}}(0)=0\). Both are nondecreasing and concave, and the Bennett radius is bounded above by the Bernstein radius.

Supplement S1 derives the nonidentical-Bernoulli moment-generating-function bound
\[
\log E e^{\lambda\sum_i(X_i-EX_i)}
\le mV(e^\lambda-1-\lambda)
\le\frac{mV\lambda^2}{2(1-\lambda/3)}.
\]
Chernoff optimization and a two-sided union bound give
\[
\mathcal E=\{\ |T_k-\mu_k(F_m)|\le r(V_k(F_m)),\ k\in K\ \},
\qquad \Pr_{\boldsymbol p}(\mathcal E)\ge1-\alpha.
\]
The \(L/(3m)\) term follows from the displayed concentration calculation. Strict tail exceedances handle the zero-variance Bennett case. Concavity of the inverse Bennett function and its perspective give the tangent construction used next.

## 3. A finite LP with an off-grid coverage argument

The ideal region is
\[
\mathcal R_{\rm VA}=\{G:|T_k-\mu_k(G)|\le r(V_k(G)),\ k\in K\}.
\]
Its constraints are convex in the probability law because means and the displayed variance functionals are linear in \(G\), and the radius is concave.

Partition \([0,1]\) into cells \(C_j\), including singleton endpoints \(\{0\},\{1\}\), with closed hulls \([a_j,b_j]\). Use actual envelopes
\[
P^{lo}_{kj}=P_k(a_j),\quad P^{hi}_{kj}=P_k(b_j),\quad
\bar V_{kj}=\max_{p\in[a_j,b_j]}P_k(p)(1-P_k(p)),
\]
and \(h_j^{lo}=\inf_{C_j}h,\ h_j^{hi}=\sup_{C_j}h\). For finitely many positive variance points, the minimum of tangent lines, \(r_{\rm cut}\), is an upper envelope of the concave radius. With simplex weights \(w_j\), impose
\[
T_k\le\sum_jP^{hi}_{kj}w_j+r_{\rm cut}\!\left(\sum_j\bar V_{kj}w_j\right),
\quad
T_k\ge\sum_jP^{lo}_{kj}w_j-r_{\rm cut}\!\left(\sum_j\bar V_{kj}w_j\right).
\]
Each tangent yields one pair of linear inequalities. Add probability-one endpoint constraints
\[
w_{\{0\}}\le\#\{c_i=0\}/m,\qquad
w_{\{1\}}\le\#\{c_i=n\}/m.
\]
Minimize \(\sum_jh_j^{lo}w_j\) and maximize \(\sum_jh_j^{hi}w_j\).

**Theorem 4.3, pp. 8–9:** for every fixed vector, every finite such partition, finite tangent set and bounded target, this interval has conditional coverage at least \(1-\alpha\). The partition, tangents and targets may depend on the data. The index set \(K\), confidence levels and radius family must be fixed in advance. All bounded targets are covered simultaneously on the same event, including targets chosen after seeing the data.

The proof is deterministic containment on \(\mathcal E\). Set \(w_j=F_m(C_j)\); monotonicity brackets the true means, cell maxima bound the true variances, and radius monotonicity/tangent majorization make those weights feasible. The target lies between the envelope objectives. This argument applies to all partitions and targets at once. It does not authorize choosing a favorable \(K\) after observing counts.

Envelopes matter near zero, where \(P_1'(0)=n\). A point-value grid can give a narrower but invalid off-grid interval. Supplement S8 characterizes the endpoint constraints as all convex linear consequences of deterministic compatibility; an empirical equal-weight/integer restriction could add nonconvex information, which is not used.

For box-type monotone regions and targets continuous at both endpoints, adding sure constraints does not change the extremal values under S8's conditions. For \(h=\mathbf1\{p>0\}\), the upper endpoint remains one, and the lower endpoint is at least the observed fraction of solved problems. These statements do not automatically extend to every other region or differently refined tangent sets.

Algorithm 1 refines violated tangents and certifies endpoints through weak LP duality over **all** cells. The implementation reports HiGHS, column generation, envelope tolerance \(10^{-3}\), ten initial tangents and up to five refinement rounds. Default \(K_{\rm geo}\) includes indices 1–16 and a geometric tail grid, giving 30 or 31 distinct indices for the experimental rollout counts. Full-\(K\) asymptotic theorems and default finite computations have different hypotheses.

## 4. Comparators and their actual guarantees

The paper distinguishes these calibration claims. Low observed miss rates do not establish a missing theorem.

| Method | Scope established or expressly limited in the paper |
|---|---|
| KL per tail, iid-Bernstein, Hoeffding per tail/cell | Nonidentical Bernoulli concentration gives fixed-vector validity. With the same indices/radius calibration, the exact VA region is contained in the iid-Bernstein region. |
| Exact-binomial critical tails | Valid under stated relations between the critical integer and the mean; implementation falls back to KL when those sufficient conditions fail. This is not unrestricted binomial replacement of a Poisson-binomial law. |
| Empirical Bernstein per tail | Uses Maurer–Pontil, Theorem 11, for independent, nonidentically distributed observations. |
| DKW with \(4/\sqrt m+\sqrt{\log(1/\alpha)/(2m)}\) | Proved here by symmetrization, a maximal inequality and McDiarmid concentration. |
| DKW–Massart, supremum Berk–Jones | No finite-sample fixed-vector coverage proof is supplied. Retained as empirical competitors. |
| Pearson chi-square region | Asymptotic justification is sketched; finite-sample band undercoverage occurs in simulation. |
| AMARI | Asymptotic, pointwise comparison through the author's reimplementation; implementation and pilot error matter. |
| Plug-in bootstrap over problems | Generally estimates a noisy-count functional, not the latent functional; no guarantee for the latter. |

The two-stage comparator first bounds
\[
V_k(F)\le\Psi_k(F)=\mu_k(F)-\mu_{2k}(F)
\]
when \(2k\le n+1\), with a mirrored relation near the other endpoint. A count-tail difference estimates \(\Psi_k\). A KL upper bound and a second concentration stage share the error budget. Union bounds suffice; independence between stages is unnecessary. Binomial-tail submultiplicativity is proved through log-concavity.

The width bounds do **not** establish a leading-order separation from this two-stage method. With the requisite partner index present, the derived leading terms are very close; with experimental sparse indices, even their ordering can reverse. The observed VA advantage is an empirical result about realized feasible candidate variances.

The main AMARI comparison uses an empirical standard error intended to match Empirikos, separately from an older model-based-SE variant that undercovers. Two endpoint matches within \(2\times10^{-4}\) are implementation checks, not complete package equivalence. The finite support grid, tuning, and fixed pilot failure budget 0.01 remain qualifications; nominal \(\alpha\) or \(\alpha/3\) second-stage calibration does not remove that pilot contribution.

## 5. Width, approximation, and exactly what is optimal

Theorem 6.1 relates width to one-sided moduli over a tail-moment tube around \(F\). For \(\psi_\lambda=h-\sum_{k\in K}\lambda_kP_k\), a useful consequence is
\[
U-Lo\le \operatorname{osc}(\psi_\lambda)
  +2\sum_k|\lambda_k|\bar D_k.
\]
Here \(\bar D_k\) accounts for the observed deviation at the true law, the candidate law's permitted radius, and grid error. It is not just \(r(V_k(F))\).

A crude bound is
\[
\bar D_k\le a(\sqrt{V_k(F)}+1/2)+2b+\eta_k.
\]
For a partner \(k'\ge2k\), the sharper recursion involves
\[
g_k=\int(P_k^2-P_{k'})\,dF,\qquad
\bar D_k\le(\sqrt{S_k}+a\kappa)^2,
\]
\[
S_k=a(1+\kappa)\sqrt{V_k(F)}
 +a\kappa\sqrt{g_k+\eta_k+\bar D_{k'}}
 +2b+a t_{\min}+\eta_k.
\]
The geometric tangent ratio determines \(\kappa\); the small-variance tangent floor \(t_{\min}\) remains visible. A mirrored partner improves bounds near \(p=1\). For fixed \(F\), the leading term has order \(\sqrt{L/m}\), but adapts to **variance and partner gap**, not variance alone. The proof bounds candidate variance by tail means, substitutes the moment-tube constraints and solves a self-bounding inequality.

Corollary 6.2 compares to Bonferroni linear certificates using the true variance. Its factor includes the two-sided cost of test inversion, and its comparator is not the best available linear-estimator interval. At nearly zero true variance, that oracle comparator can be unrealistically informed and the factor can diverge. The proposed stronger \(O(a^2)\) remainder from long doubling chains remains a sketch/conjectural refinement, not a completed matching theorem.

### Worst-case identification: Theorem 6.3

With **all** tails \(K=\{1,\ldots,n\}\), the constant function and tails span the degree-\(n\) polynomials. Let
\[
E_n(h)=\inf_{\deg Q\le n}\|h-Q\|_\infty.
\]
For bounded \(h\in[0,1]\), the maximal same-moment identification diameter is at most \(2E_n(h)\). On the coverage event, under the specified tangent set,
\[
U-Lo\le2E_n(h)+2\|\lambda^*\|_1
 (a+2b+\max_k\eta_k),
\]
where \(c^*+\sum_k\lambda_k^*P_k\) is a best approximation. The prescribed tangent set includes the point \(\sqrt V=1/2\). With fixed \(n\) and a data-independent grid refined so \(\eta_m\to0\), this upper bound tends to \(2E_n(h)\).

For **continuous** \(h\), every uniformly conditionally valid procedure and every \(\zeta\in(0,1),\nu>0\) have **some** fixed vector \(\boldsymbol p\) satisfying
\[
\Pr_{\boldsymbol p}\{\operatorname{diam}C
 \ge2E_n(h)-\nu-1/\sqrt{\zeta m}\}
 \ge1-2\alpha-2\zeta.
\]
The lower bound uses moment-matching duality and fuzzy hypotheses. Two population laws with equal first \(n\) moments induce the same iid marginal count experiment. Randomly drawing the parameter vector from either law makes its empirical target concentrate around the population value. Integrating conditional coverage and averaging produces an adverse **deterministic vector**. This is a proof device, not a change of target to \(G\).

The conclusion is worst-case over moment vectors, fixed-\(n\), asymptotic identification optimality. It is **not** a positive diameter at every moment vector. The localized S6 lower bound holds at a resampled vector in a prior's support, not automatically at the original fixed vector. Its one-extremal-prior construction incurs a factor two and a subset-size penalty.

For pass@\(k\) with \(k\le n\), \(E_n=0\). A jump of size \(J\) forces \(E_n\ge J/2\), making the universal bound vacuous for an indicator. The default 30–31 tails are not the full-\(K\) theorem. At \(n=128,\delta=.01\), the reported large tail-basis coefficient norm makes the fixed \(\eta=10^{-3}\) grid term at least two. Asymptotic optimality does not certify small widths at that practical grid.

For \(h_\delta\), the paper computes 40 brackets for
\[
2E_n(h_\delta)=c_n(\delta)
 \frac{\sqrt{1-\delta}}{n\sqrt\delta}.
\]
It reports Chebyshev-polynomial upper bounds with curvature/floating-point allowances and alternation lower bounds. Apparent convergence of \(c_n(\delta)\) to Bernstein's constant is explicitly **conjectured**, not used as a proved asymptotic formula. The certificates were read, not independently recomputed.

### Separated laws and the remaining estimation gap

For \(F=\pi_0\delta_0+(1-\pi_0)F_+\), with support of \(F_+\) in \([p_{\min},1]\) and \(\delta<p_{\min}\), key small tails can have exponentially small variance and partner gap. Corollary 6.5 bounds width by an identification allowance plus \(aA_{\rm VA}+O(a^{3/2})\). Its fixed-\(n\) constant-factor comparison applies only in a specified range of \(m\), which can be empty or too conservative to explain the measured gain.

Corollary 6.6 fixes \(F,\delta,\pi_0\) with \(p_{\min}>2\delta\), takes \(m,n_m\to\infty\), and requires \(K\supseteq\{1,2,k_*,2k_*\}\), \(k_*=\lceil n\delta\rceil\), and
\[
n\delta\ge\tfrac34\log\frac{m}{2L}+1,\qquad
n\,\mathrm{KL}\!\left(\frac{2k_*-1}{n}\middle\|p_{\min}\right)
\ge\tfrac34\log\frac{m}{2L},\qquad
t_{\min}\le a^{1/2},\quad \max_k\eta_k\le a^{3/2}.
\]
It then gives width \(O((L/m)^{3/4})\). The Hoeffding competitor has width at least approximately \(\tfrac12\sqrt{2L/m}\). The iid-Bernstein comparison needs an additional high-index condition that can fail, for example when \(n\in K\), \(\delta>p_{\max}^2\), and the nonzero support stays below \(p_{\max}\). A KL-competitor extension is a sketch rather than the same completed uniform theorem. The authors do not prove that growing \(n\) is necessary for every possible rate improvement.

The general local estimation lower bounds have orders \(\delta^{-1}\sqrt{\sigma_A^2/(nm)}\) and \(1/(n\delta m)\) in different constructions. They do **not** match the complete VA estimation term; Table S2 makes the gap explicit. Approximate moment matching yields a total-variation bound through a tail of \(\sum_d(2n\varsigma)^d/d!\), but this bound is inactive in the numerical \(\delta\)-ranges used. Neither result controls total future-block KL.

## 6. Population inference and empirical evidence

### The additional \(G\)-level layer

Supplement S7 splits \(\alpha=\alpha_1+\alpha_2\). Conditional intervals for \(\theta_h(F_m)\) are expanded by iid concentration for the problem sample. Fixed finitely many targets admit KL or empirical-Bernstein expansion. A DKW/Stieltjes argument handles all monotone targets, including data-dependent ones, but does not preserve simultaneous inference for every bounded function.

This two-step method adds radii instead of optimally combining variances. For the reported \(m=1000\) comparisons, median VA+KL / best non-AMARI localization widths are **1.08, 1.32, 1.38** at \(n=32,128,512\), and VA+KL / AMARI are **1.98, 2.14, 2.33**. These are a fixed-benchmark replicate proxy, not a fresh population-coverage study redrawing \(p_i\). They support a target-dependent efficiency caution, not a finding that population coverage failed.

### Fixed-vector simulations

The five laws combine endpoint or interior atoms with beta/uniform components:
F1 \(=.3\delta_0+.7\mathrm{Beta}(.3,1.5)\);
F2 \(=.0323\delta_0+.0205\delta_1+.9472\mathrm{Beta}(.282,.401)\);
F3 \(=.5\delta_0+.5\mathrm{Beta}(2,5)\);
F4 \(=.1\delta_0+.9\mathrm{Unif}[0,1]\);
F5 \(=.2\delta_{.02}+.5\delta_0+.3\mathrm{Beta}(1,3)\).
There is no atom-free law in this main suite. A single \(F_m\) draw is held fixed per law/benchmark-size pair.

Main settings are \(m\in\{250,1000,4000\}\), \(n\in\{32,128,512\}\), and \(\delta\in\{.01,.02,.05\}\), giving 135 cells. Small F2 benchmarks of size 30, 50 and 100 are separate. Main interval replicates number only 15–30 per cell, after runtime-driven reductions; a solver failure is disclosed. Complete coverage in 30 or 15 replicates is compatible with true coverage as low as .884 or .782 by the quoted two-sided Clopper–Pearson bound. This checks implementation behavior; the theorem supplies the guarantee.

| Median VA/comparator width | \(n=32\) | \(n=128\) | \(n=512\) |
|---|---:|---:|---:|
| Two-stage band | .746 | .602 | .436 |
| AMARI, pointwise | 1.307 | .977 | .626 |
| AMARI, Bonferroni \(\alpha/3\) | 1.179 | .808 | .513 |
| iid-variance ablation | .636 | .421 | .264 |

AMARI at \(n=512\) was run only for \(m=1000\), so that column has 15 comparison cells rather than 45. VA is narrower than the two-stage comparator in all 135 cells. The author's 10%-improvement rule succeeds against the two-stage and Bonferroni-AMARI comparators, but fails against pointwise AMARI because of \(n=128\). The rule was recorded after preliminary AMARI results were already known; its disclosed timestamp/hash is not independent public preregistration. Threshold targets do not uniformly follow the softened-target ranking.

A separate \(10^5\)-replicate band study across 63 cells, including two adversarial laws, is much more precise. VA's maximum miss rate is .00207 on F1–F5 and .00139 on the adversarial pair, far below nominal .05. The chi-square band exceeds .05 in four statistically flagged cells, with maximum .07930. Plug-in bootstrap severely undercovers some latent targets, including zero empirical coverage. Oracle calibration can shorten VA further, but uses the unknown law and is a diagnostic, not an implementable calibrated competitor.

### Empirical rollout pools

Monkey Business contains eight model/task configurations with 127 or 128 problems each, pooled as **1,022 problem–model units**, including repeated problems across models. Each problem has a 10,000-rollout correctness pool. With-replacement resampling makes the experiment exactly binomial with parameter \(\hat p_i\). It tests the procedure under that controlled target; it does not verify independence of original model rollouts.

VA is narrower than the two-stage and KL methods in all 81 cells, but empirical-SE AMARI is shorter: median VA/pointwise-AMARI ratios are **1.412 and 1.290** at \(n=32,128\); Bonferroni ratios are **1.238 and 1.122**. AMARI was not run at \(n=512\) on these pools. In its larger \(R=500\) check, minimum reported coverage is .962 with interval [.941,.977]; the model-based-SE ablation undercovers several GSM cells. Those ablation failures should not be attributed to the empirical-SE method.

Pool-truth Monte Carlo errors matter when interpreting \(\theta(\hat p)\) as \(\theta(p)\), not for the resampling experiment's exact target. Without-replacement resampling and index variants are separate. Neither replaces a fresh disjoint-block study of actual rollout dependence.

### Distilled versus RL-from-distilled illustration

The application compares DeepSeek-R1-Distill-Qwen-1.5B with DeepScaleR-1.5B-Preview on 1,060 problems and 128 rollouts: 633 OlympiadBench, 358 Gaokao, 39 AMC and 30 AIME. It uses public passk-inference counts, pinned by the paper to commit ac7c3fc58d5e325447607e778bdcbc897182cf7e. This is a specific RL-from-distilled comparison, not a general pretrained-versus-RL finding.

VA estimates \(P(p\ge.5)\) as [.569,.653] and [.670,.724]; a Bonferroni difference interval is **[.015,.156]**. This is the one main functional difference excluding zero. Other softened-solvability, pass@256, pass@1024 and exact-solvability differences include zero. Combining two marginal regions does not exploit paired-problem covariance. With the main fixed \(K\), simultaneous bounded-target coverage supports reporting a selected functional; it does not license selecting among unadjusted index sets or source strata.

The two-index sensitivity table reports all three stated pairs; its narrowest pair is not a separately multiplicity-corrected search result. Source-specific intervals are expressly not simultaneous across sources. The counts depend on temperature .6, top-p .95, a 32,768-token limit and verifier/timeout conventions. Checkpoint revisions, original seeds and training overlap are not fully documented. Those conventions define the measured success probability.

### Numerical and archival boundaries

At \(m=1000\), main VA computation for seven targets and both endpoints takes median 21.2, 104.7 and 130.4 seconds for \(n=32,128,512\), versus about one second for the two-stage method, on the reported shared host. Full-tail runs are much more expensive and include failures. A theorem-aligned configuration changes widths by median factors 1.012, 1.016 and 1.098.

Figures S1–S3 and many S13 tables belong to a preliminary run without sure constraints and with the older model-based AMARI variant. They were read as archival sensitivity evidence, not pooled with the main experiment. Figure S4 uses an oracle atomic support grid. Its joint-growth and fixed-\(n\) curves are both pre-crossover in the plotted range; they do not empirically separate the asymptotic rates. Widths below \(10^{-6}\) approach numerical tolerances and are reported as upper bounds. The pilot budget table is an oracle-centered design proxy, not an observed power guarantee.

## 7. Proof dependencies, public code and unresolved work

The argument uses Bernstein/Bennett concentration, Hoeffding's nonidentical Bernoulli comparison, empirical Bernstein results, approximation duality and alternation, and fuzzy hypotheses. Wu–Yang's moment-matching/approximation duality supplies the sharp identification constant; the paper proves its conditional fixed-vector translation. AMARI/Empirikos and the benchmark/count repositories are separate method or data dependencies. Reading their citation entries and uses does not mean their complete papers, software or data were read.

A bounded metadata inspection fixes the public [valoc implementation](https://github.com/YYKKCC-kevin/valoc/tree/db407a1c33c10af524f79c4b6198e942f2f7cd13) at commit db407a1c33c10af524f79c4b6198e942f2f7cd13, November 16, 2026, 14:53:54 UTC. The visible history has one initial commit and no tag/release. All ten explicitly named check scripts exist: nine Python files and one Julia file, comprising CHK-1–CHK-9 with two CHK-9 files. Their presence, paths and blob identities were checked, not their execution.

The root README names this paper but retains an arXiv placeholder; the checks README refers to a Stage-3 manuscript/internal roadmap and expressly reclassifies checks earlier credited to a referee as author scripts. These are not independent peer-review certificates. Reported results/checks outputs and the referenced internal review/theory material are absent from the public tree. The paper does not pin valoc's commit. Its dated initial commit is not independent evidence of the exact v2 experiment runtime. The separate passk-inference SHA pins the upstream data source, not this implementation. Mechanical snapshots are in the ignored source directory as code-provenance files. No software audit, author experiment, formal proof or numerical certificate was replayed.

Material open questions are matching estimation-width lower bounds; sharper implementable joint-tail calibration; a tight population-level construction; robustness to dependent/heterogeneous rollouts; and computation with larger index sets or smaller grid tolerance. Adaptive rollout allocation, a learned reset policy, installed predictive-state memory and total future causal log loss are not analyzed.

## 8. Independent bounded check: worst fibers, singleton fibers and variance

This exact example was derived separately from the paper and cross-checked with rational arithmetic. It checks the interpretation of the identification theorem, not the full theorem suite.

For \(n=2,\ h(p)=p^3\), take
\[
G_+=\tfrac23\delta_{1/4}+\tfrac13\delta_1,\qquad
G_-=\tfrac13\delta_0+\tfrac23\delta_{3/4}.
\]
Both have first moments \(1/2,3/8\), and induce count probabilities
\[
(\Pr\{c=0\},\Pr\{c=1\},\Pr\{c=2\})=(3/8,1/4,3/8).
\]
Their third moments are \(11/32\) and \(9/32\). The polynomial
\[
Q(p)=\tfrac32p^2-\tfrac9{16}p+\tfrac1{32}
     =p^3-\tfrac1{32}T_3(2p-1)
\]
has uniform error \(1/32\). Its residual alternates \(-,+,-,+\) at \(0,1/4,3/4,1\). A strictly better quadratic would require three sign changes of the difference of two quadratics, which is impossible. Hence \(E_2(p^3)=1/32\).

For the fiber with moments \((1/2,3/8)\), \(\int Q\,dG=5/16\). Every third moment lies in \([9/32,11/32]\), and the displayed laws attain its endpoints. Its identification diameter is exactly \(2E_2=1/16\). In contrast, moment vector \((1/2,1/4)\) has variance zero and forces \(G=\delta_{1/2}\); its third-moment diameter is zero.

The same pair makes the candidate-variance distinction exact:
\[
(V_1(G_+),V_2(G_+))=(21/128,5/128),\qquad
(V_1(G_-),V_2(G_-))=(5/128,21/128).
\]
Equal marginal count laws do not determine these variances. **They do not assert equality of labeled conditional product experiments for two particular fixed parameter vectors.** The lower-bound proof needs its random-parameter averaging step to bridge that distinction.

No FP theorem is proposed. This source supplies an unrestricted moment-fiber comparison with carefully specified fixed-benchmark confidence targets. Passing from bounded-functional intervals to total forward KL, and paying for acquisition and state, requires separate results.
