# Lee–Baćak–Kennedy — smooth mixing densities under heterogeneous trials

## Source, edition and actual coverage

JungHo Lee, Valerio Baćak and Edward H. Kennedy, *Learning Smooth Populations of Parameters with Trial Heterogeneity*, **arXiv:2507.23140v2**, uploaded October 9, 2026, 16:08:14 UTC; the manuscript cover says October 14, 2026. The first version was submitted July 30, 2025. [Versioned metadata](https://arxiv.org/abs/2507.23140v2) · [Exact 45-page PDF](https://arxiv.org/pdf/2507.23140v2) · [Complete TeX](https://arxiv.org/src/2507.23140v2).

An associated refereed article is *Learning smooth populations of parameters under trial heterogeneity*, **Electronic Journal of Statistics 20(2), 5086–5125 (2026)**, DOI [10.1214/26-EJS2602](https://doi.org/10.1214/26-EJS2602). Its title uses “under,” and its bibliographic pagination spans 40 pages; the journal PDF and its physical page count have not been inspected. The full-reading claim below concerns the pinned 45-page author version; a bounded DOI retrieval reached the publisher but returned an Incapsula “Request unsuccessful” wrapper despite HTTP 200. Web opening also failed, and a publisher-domain DOI search was empty. No journal article text or theorem comparison was obtained; no equality of editions is assumed.

**Fully read on November 24, 2026, Shanghai:** the main assistant read the entire author manuscript, §§1–6, every formula and proof, Appendix A.1–A.11, all five figures and their panels, three body footnotes, three author-email thanks, acknowledgments and all **59 printed references**. The complete active TeX has no external section inputs. Original PDF images were checked for all figures on pp. 16, 21, 23, 25–26, and for title/thanks and important formulas on pp. 1, 5–6, 8–9, 13–14, 19 and 35. There are no tables or numbered algorithm boxes. The bibliography database contains unused entries; the 59 actually cited and printed references are the reading denominator.

Local materials are under literature/corpus/pisf_prior_art/2507.23140v2/. Mathematical font extraction is unreliable, so active TeX and actual PDF images were used together. The mechanical inventory lists nine figure assets; two missing obsolete assets occur only inside comments and are not source gaps. Assistants prepared sources and checked the bounded calculations in §7; the main assistant read the paper. No simulations, public software or formal proofs were replayed. This is an academic paper, not an official OpenAI/Anthropic release.

## 1. Question, sampling model and estimand

For independent units (i=1,\ldots,n), latent proportions (Q_i) have a common density (p) on ([0,1]), and
\[
X_i\mid Q_i\sim\operatorname{Bin}(t_i,Q_i).
\]
The positive integer trial counts (t_i) are treated as given and can differ. The target is the **mixing density (p(u))** at a fixed interior point, together with density differences between groups. Here (n) counts independent units, not trials within a unit. The law is absolutely continuous and smooth; arbitrary atomic mixing distributions are outside this model.

The ordinary estimator applies a kernel directly to noisy proportions:
\[
\widehat p_h(u)=\frac1n\sum_i\frac1hK\!\left(\frac{X_i/t_i-u}{h}\right),
\qquad
\widetilde t=\frac{n}{\sum_i t_i^{-1}}.
\]
The centered estimator substitutes ((X_i+1)/(t_i+2)). This number equals the mean of a beta distribution arising in the integral calculation; the sampling model does not assume a uniform Bayesian prior for the population of (Q_i).

The paper's (s)-smooth class bounds derivatives and a Hölder remainder, using the largest integer **strictly less than** (s) as its floor convention. Kernels are bounded, supported on ([-1,1]), Hölder/Lipschitz on that support, integrate to one, and have vanishing moments through the required order. Higher-order kernels may be signed. The estimator therefore need not automatically be a nonnegative, normalized density after boundary truncation.

This is a repeated binomial sampling experiment with prescribed trials. It does not select continuation versus reset, identify unknown episode boundaries, or account for online model/state storage. Nor is (p) the empirical distribution of a fixed benchmark's latent probabilities: that was the different target in Ye 2611.21266v2.

## 2. The beta identity and the error bounds

### Integrated approximation, rather than derivatives of a narrow kernel

For (B_{x,t}\sim\operatorname{Beta}(x+1,t-x+1)), direct integration gives
\[
E_p f(X/t)=\frac1{t+1}\sum_{x=0}^{t}f(x/t)E\{p(B_{x,t})\}.
\]
The mean and variance satisfy
\[
\mu_{x,t}=\frac{x+1}{t+2},\quad
|\mu_{x,t}-x/t|\le\frac1{t+2},\quad
\operatorname{Var}(B_{x,t})\le\frac1{4(t+3)}.
\]
Lemma 1 splits the discrepancy from (\int fp) into beta fluctuation, evaluation/normalization displacement, and a **quasi-Riemann** error. The last term uses the grid (0,1/t,\ldots,1) with weight (1/t), so it has an extra endpoint relative to a usual one-sided Riemann sum. For (p\le p_{\max}) and Hölder exponent (\alpha), its beta coefficient is
\[
g(t,\alpha)=L\{4(t+3)\}^{-\alpha/2}
             +L(t+2)^{-\alpha}+p_{\max}/t.
\]
It multiplies the discrete absolute mass of (f). This puts regularity on the mixing density, avoiding the excessive powers of (1/h) produced by differentiating the narrow kernel directly.

Theorem 1 adds ordinary smoothing bias (LBh^s/\lfloor s\rfloor!), bounds the grid error explicitly, and proves
\[
\operatorname{Var}\{\widehat p_h(u)\}
\le\frac{K_{\max}^2p_{\max}}{nh}
          \left(2+\frac1{h\widetilde t}\right).
\]
Corollary 1 assumes **both (p) and (K) Lipschitz** and (C/\widetilde t\le h\le C'), and states
\[
|E\widehat p_h(u)-p(u)|\lesssim
h^s+\widetilde t^{-1/2}+(h\widetilde t)^{-1},
\qquad
\operatorname{Var}(\widehat p_h)\lesssim (nh)^{-1}.
\]
For (s<1), that additional Lipschitz premise is stronger than merely belonging to the stated (s)-Hölder class. A full-class low-smoothness minimax claim cannot silently discard it. Section 7 below also records a boundary omission and a repairable harmonic-mean proof step.

### Centering and stronger smoothness

For (s\ge2) and Lipschitz derivative (p'), Taylor expansion around (\mu_{x,t}) cancels its first-order expectation. Lemma 2 replaces the beta coefficient by (L'/\{8(t+3)\}), with a correspondingly centered quadrature grid. Corollary 2 states
\[
|E\widehat p_{c,h}(u)-p(u)|\lesssim
h^s+\widetilde t^{-1}+(h\widetilde t)^{-1},
\qquad
\operatorname{Var}(\widehat p_{c,h})\lesssim(nh)^{-1}.
\]
The stronger regularity is essential to the displayed Taylor argument. The text attributes the (t^{-1/2}\to t^{-1}) improvement to centering; the independent calculation below shows that under the **same stronger assumptions**, the uncentered beta term is also (O(t^{-1})). Centering removes a specific linear displacement and can improve constants and empirical bias, but the stated order comparison does not prove that it is necessary for the sharper rate.

### What “oracle minimax” means here

Section 2.3 calls (n^{-s/(2s+1)}) the oracle rate: it is the pointwise error scale when the latent (Q_i) are observed directly. Taking (h\asymp n^{-1/(2s+1)}), the paper's displayed bounds give these **sufficient** trial requirements:

| Bound used | Sufficient harmonic trial size |
|---|---|
| Ordinary bound, (s\le1), with its additional premises | (\widetilde t\gtrsim n^{(s+1)/(2s+1)}) |
| Ordinary bound, (s>1) | (\widetilde t\gtrsim n^{2s/(2s+1)}) |
| Centered bound, (s\ge2) | (\widetilde t\gtrsim n^{(s+1)/(2s+1)}) |

These are not matching necessary thresholds for binomial mixtures. The authors explicitly leave the smooth, heterogeneous-trial minimax theory open. Harmonic-mean upper bounds do not establish that the entire inverse problem depends only on that scalar. Even the comparison between ordinary and centered requirements is tied to the chosen bounds, in view of the common-smoothness calculation in §7.

## 3. Tuning and inference: keep the oracle calibration in view

Section 2.4 develops a pointwise Lepski comparison over a finite bandwidth grid. Its oracle balances squared **differences of expectations** against variances of differences. The data rule tests smaller-bandwidth comparisons with critical values defined from the true centered distributions. An indistinguishability region excludes bandwidths whose bias differences exceed an enlarged variance threshold. With probability at least (1-2\alpha), the chosen estimator differs from the oracle by the largest allowed comparison fluctuation in that region.

Appendix A.6 bounds difference variance by
\[
v_{h,h^*}\lesssim \frac1n(1/h^*-1/h),\qquad h\ge h^*,
\]
using a minimum of two bounds, kernel endpoint/regularity conditions and (h^*\gtrsim1/\widetilde t). A wide indistinguishability region yields a price of order (\sqrt{\log n/(nh^*)}); a narrow one can give (\sqrt{\log n/n}). The discussion invokes a maximal inequality for critical values of order (\sqrt{\log|\mathcal H|}). Its full uniform tail premises were not independently certified here.

The suggested empirical variances and multiplier-bootstrap critical values are practical replacements, **not an additional proved bootstrap approximation theorem in this paper**. The application uses a Goldenshluger–Lepski implementation; equivalence of that implementation, the theoretical ideal rule and the required undersmoothing is not established by their shared name. Ordinary cross-validation on noisy proportions is discussed heuristically and deferred, with stronger trial-size requirements conjectured rather than proved.

Proposition 2 gives a pointwise studentized CLT for a bandwidth sequence with (nh\to\infty), nondegenerate limiting (nh\operatorname{Var}(\widehat p_h)), and negligible scaled bias. In addition to (nh^{2s+1}\to0), the ordinary displayed bound requires
\[
\widetilde t/(nh)\to\infty,
\qquad \widetilde t/\sqrt{n/h}\to\infty.
\]
The centered bound replaces the first condition by (\widetilde t/\sqrt{nh}\to\infty). The sample kernel variance divided by (n) consistently estimates the estimator variance despite unequal trials; the proof controls variation in the individual means. Lindeberg follows from the bounded kernel and (nh\to\infty).

With (h\asymp n^{-\zeta}), the printed exponent intervals must still be intersected with (\zeta<1), required by (nh\to\infty). These are asymptotic fixed-point intervals with undersmoothing, not finite-sample honest bands or an automatic post-bandwidth-selection CLT. The application does not establish uniform coverage at all (u), particularly near the endpoints.

## 4. A density difference can be smoother than either density

For groups (A\in\{0,1\}), set (\tau=p_1-p_0). The individual densities are (s)-smooth while their difference may be (\gamma)-smooth with (\gamma>s). Figure 1 uses identical piecewise, discontinuous densities, making (\tau=0) infinitely smooth. That is an illustration of cancellation, not an example satisfying all positive-smoothness assumptions of the subsequent theorem.

When true (Q_i) are observed, the common-bandwidth difference is
\[
\widetilde\tau_h(u)=\frac1n\sum_i
\left\{\frac{A_i}{\bar A}-\frac{1-A_i}{1-\bar A}\right\}K_h(Q_i).
\]
Smoothing acts directly on (\tau), giving bias (O(h^\gamma)) and variance (O((nh)^{-1})). Tuning the two densities separately can lose this cancellation. The assumptions bound (\bar A) away from zero and one almost surely; interpreted literally this requires a balanced/conditioned group design, since unrestricted iid Bernoulli labels have positive probability of an empty group at finite (n).

A two-fold joint cross-validation criterion combines (\int\widetilde\tau_h^2) with validation observations weighted by their own fold's group proportions. Conditional on training and group labels, it is unbiased for integrated squared error minus (\int\tau^2). Proposition 4 obtains a finite-grid oracle inequality with leading factor (1+\delta) and remainder (O((1+\log|\mathcal H|)/n_{\rm val})). Its candidate uniform-norm bound is an assumption, not automatically guaranteed by arbitrary signed higher-order KDEs. The proof uses conditional Bernstein concentration and a union bound. A grid of both bandwidth and kernel order is suggested when smoothness is unknown.

For **empirical** proportions, the decomposition retains the (h^\gamma) smoothing term but adds separate binomial approximation errors for (p_0,p_1):
\[
|E(\widehat\tau_h\mid A^n)-\tau|
\lesssim h^\gamma+
\sum_{a=0}^1\{\widetilde t_a^{-1/2}+(h\widetilde t_a)^{-1}\}.
\]
Centering with smooth individual (p_a) replaces the square-root terms by (\widetilde t_a^{-1}). A smooth difference does not by itself cancel measurement errors from unequal trial designs. Group balance permits comparison with a global harmonic mean. The joint-validation theorem for observed (Q_i) is not a proved noisy-proportion validation theorem, and no causal treatment-effect identification follows from density subtraction alone.

## 5. Evidence from simulations and the application

**Figure 2:** (p=\operatorname{Beta}(2,2)), **(n=200) and (500)** (shown in the original figure), harmonic trial targets 30 to 100 by fives, and 1,000 repetitions. Trial sizes are initially Poisson, one is forced small and another adjusted to reach the target harmonic mean. Epanechnikov estimates share (h=n^{-1/5}); evaluation is at (u=0.5). Ordinary heterogeneous KDE nearly matches the hypothetical equal-arithmetic-mean trial benchmark; centered KDE has the lowest plotted bias, without a visible standard-error penalty. Minimum-trial and half-harmonic benchmarks have larger bias.

Those benchmarks generate new binomial samples with common trial counts. Except for the arithmetic-mean comparison, their total observation budgets differ. This is evidence about the specified estimators/designs, not a matched-budget trial-allocation or adaptive-reset experiment. The prose does not fully specify integer rounding and zero-Poisson handling, and no simulation replay was performed.

**Figure 3:** the simulation observes the **latent proportions themselves**, with two identical nonsmooth densities and true difference zero. For (n=100,200,\ldots,2000), 1,000 repetitions compare jointly tuned KDE, separately tuned KDE and least-squares density-difference estimation. Bandwidths range from 0.2 to 2 by 0.1 and Legendre kernel orders are 2, 4, 6 and 8. Joint tuning substantially reduces both bias and variability relative to separate tuning and is close to the density-difference baseline. It does not test unknown nonzero difference smoothness across a class, nor heterogeneous binomial noise in the joint-validation theorem.

**Figures 4–5:** county-level Measures for Justice data cover **67 Pennsylvania counties, 2009–2013**. Counts range from 1–24,740 for appointed counsel, 154–117,282 for public defenders and 54–39,295 for private attorneys. The centered KDE and reported pointwise intervals describe distributions of county proportions. Plotted mean conviction rates are 0.82, 0.77 and 0.68, respectively. These are not randomized individual treatment effects or necessarily case-weighted statewide rates.

The four bail panels show lower release-on-recognizance and higher cash-bail proportions for appointed counsel: misdemeanor ROR means approximately 0.65/0.73/0.78, felony ROR 0.31/0.34/0.45, misdemeanor cash bail 0.35/0.27/0.22, felony cash bail 0.69/0.66/0.54, in appointed/public/private order. This supports the authors' concern about case-severity selection. It does not identify how outcomes would change under reassignment. Caseload, payment, appointment timing and administrative support are discussed as other explanations. Informative county trial sizes and differing county populations also deserve attention before assuming the common-(p), fixed-(t_i) model literally.

## 6. Proof structure, dependencies and unfinished questions

Appendices A.1–A.2 establish beta integration, quasi-Riemann control and kernel second-moment bounds. A.3 simplifies by harmonic means. A.4–A.5 handle centered beta means and the shifted grid. A.6 proves the ideal Lepski comparison and variance increment bound. A.7 proves triangular-array normality and variance consistency. A.8–A.11 treat direct density differences, joint-validation concentration, noisy proportions and the centered extension. All eleven were read; this map describes proof content rather than independent certification.

The main imported inputs are classical kernel bias/minimax theory (van der Vaart; Tsybakov), Bernstein polynomial approximation, Spokoiny–Willrich's Lepski comparison, a Massart maximal inequality, and concentration/model-selection arguments. Goldenshluger–Lepski is also the application's tuning reference. The comparator **Ye and Bickel (2021)** is the earlier binomial-mixture/u-shape work, not Kuancheng Ye's 2026 fixed-benchmark paper. Reading the bibliography did not entail full reading of these cited works.

The authors leave matching smooth-mixture minimax lower bounds under heterogeneous trials, a full noisy-proportion cross-validation analysis, and covariate extensions open. Automatic bias-aware confidence statements and guarantees for arbitrary atoms are not supplied. No code/data repository URL was found in the active author TeX beyond emails; that bounded source observation does not prove that no materials exist elsewhere.

## 7. Bounded independent checks and their exact scope

### 7.1 A missing finite-bandwidth boundary condition

Theorem 1 states its usual smoothing term for (u\in(0,1)), without requiring the kernel window to stay inside ([0,1]). Take (p=1), triangular kernel (K(v)=(1-|v|)_+), (u=1/20), (h=1/10), (s=1,L=1,B=1/3). The latent-observation KDE has
\[
E\widehat p_{\rm oracle}(u)=\int_{-1/2}^{1}K(v)\,dv=\frac78,
\quad |E\widehat p_{\rm oracle}-1|=\frac18>\frac1{30}=LBh.
\]
The additional binomial/grid terms vanish as trials grow. Thus the literal finite-(h) bound needs an interior-window restriction such as **(h\le\min(u,1-u))**, a suitable smooth extension, or a boundary correction. This does not refute the fixed-interior-point rates with (h\to0), where the window restriction eventually holds. The same distinction must be respected in density-difference bias arguments.

### 7.2 Strong smoothness sharpens the ordinary beta term too

Let (q=x/t), (\mu=(x+1)/(t+2)), (|p'|\le M_1) and (p') be (L_2)-Lipschitz. Taylor expansion at (\mu), followed by the mean value bound, gives
\[
|E p(B_{x,t})-p(q)|
\le \frac{L_2}{8(t+3)}+\frac{M_1}{t+2}=O(t^{-1}).
\]
Equivalently, expansion at (q) retains the signed first-order mean shift; bounding its absolute fluctuation before taking expectation would unnecessarily lose a square root. Centering eliminates the (p'(q)(\mu-q)) contribution, but that contribution is already order (1/t). This is a comparison under common assumptions, not a claim that all centered and uncentered finite-sample biases coincide.

Combining this coefficient with the quadrature bound below yields the ordinary estimator's same order (h^s+\widetilde t^{-1}+(h\widetilde t)^{-1}) under the stronger assumptions and an interior window. Consequently the paper's stronger uncentered trial requirement is sufficient as derived, not an established unavoidable cost of leaving the proportions uncentered.

### 7.3 The harmonic-mean proof step and a bounded-variation repair

On **p. 35, Appendix A.3**, the proof bounds discrete kernel mass by (K_{\max}\{2+1/(ht_i)\}), then treats it as uniformly bounded and removes the same factor from an average using (h\ge C/\widetilde t). That condition does **not** imply (ht_i\ge C) for each unit. For example, take (t_1=2), the other (t_i=n^2), and (h=n^{-1/2}). Then (\widetilde t\asymp2n), while (ht_1\to0). Thus that displayed simplification does not follow. It is a proof gap, not itself a counterexample to the final harmonic-mean rate.

A direct repair for the Lipschitz corollary uses total variation. Extend (K) by zero and include any endpoint jumps in its variation. For (g_h(q)=h^{-1}K((q-u)/h)p(q)),
\[
\operatorname{TV}(g_h)
\le \frac{p_{\max}\operatorname{TV}(K)}h+L\|K\|_1.
\]
The quasi-Riemann error is at most ({\operatorname{TV}(g_h)+|g_h(0)|}/t), hence (O(1/(ht))) for bounded-above (h). The remaining discrete beta term is bounded **before averaging** by a constant times
\[
t_i^{-1/2}\{2+(ht_i)^{-1}\}.
\]
Since (t_i\ge1), Jensen and (t_i^{-3/2}\le t_i^{-1}) give
\[
\frac1n\sum_i t_i^{-1/2}\{2+(ht_i)^{-1}\}
\le 2\widetilde t^{-1/2}+(h\widetilde t)^{-1}.
\]
This restores the stated bias order without a false unitwise trial lower bound. With the stronger (O(t_i^{-1})) coefficient from §7.2, the analogous average is (O(\widetilde t^{-1}+(h\widetilde t)^{-1})). Boundary truncation remains a separate issue; total variation only repairs the discrete quadrature step.

These exact calculations were checked independently in a bounded assistant task and by the main reader. They do not certify every Lepski constant, the bootstrap implementation, all inference extensions or the complete theorem suite. No new proof-audit script or formal artifact was created.

## 8. Research-use boundary

The paper supplies an instructive smooth-population estimation method and a precise distinction between smoothing bias, trial noise and density-difference cancellation. Its harmonic-mean guarantees assume a shared smooth density and fixed trials; its “oracle” refers to directly observing latent proportions. It supplies **no theorem for unrestricted mixing measures, total future-group forward KL, adaptive purchased resets, learned finite state or priced online computation**. No FP transfer result is asserted. A recent companion, Lee–Kennedy, [Minimax Rates for Learning Smooth Populations of Parameters, 2610.04135v2](https://arxiv.org/abs/2610.04135v2), advertises matching pointwise rates and dependence on the full heterogeneous trial profile. At this note’s completion, only its primary metadata and abstract have been screened; it is the next selected full reading, not an established repair or a less restrictive-class guarantee imported here.
