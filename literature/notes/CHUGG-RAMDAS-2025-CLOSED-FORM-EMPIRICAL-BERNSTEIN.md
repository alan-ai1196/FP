# Chugg–Ramdas — Closed-form empirical Bernstein confidence sequences for scalars and matrices

## Edition and actual reading

Ben Chugg and Aaditya Ramdas, **arXiv:2512.21300v1**, December 24, 2025, 17:34:11 UTC. The primary arXiv history still lists this single version at the November 25, 2026 Shanghai check. The authors' publication lists classify it as a preprint; no peer-reviewed publication of this exact manuscript was authenticated. It is not an official OpenAI or Anthropic release.

- [Metadata](https://arxiv.org/abs/2512.21300v1), [PDF](https://arxiv.org/pdf/2512.21300v1), [TeX](https://arxiv.org/src/2512.21300v1), [HTML](https://arxiv.org/html/2512.21300v1).
- **Fully read by the main assistant:** all 36 pages, §§1–6, Appendices A–D, all proofs/formulas, six numbered figures comprising 19 image panels, two tables, three footnotes, acknowledgments and all 41 printed references. The complete active content is in one 1,494-line TeX file. Its bibliography database has 46 records, five unused by the printed manuscript.
- All actual figures and tables were inspected in the original PDF, on pp. 4, 10–13, 15, 35–36. Dense original formulas on pp. 9, 16–17, 22–23 and 27 were also inspected. Footnotes on pp. 2, 5 and 26 were checked against the extracted original. The PDF confirms the startup-rule error below; it is not a text-extraction artifact.
- Temporary sources are under `tmp/source_candidates/2512.21300v1/`; the 2,422,184-byte PDF, complete archive, source inventory and references were retrieved. Versioned URLs above provide recovery if temporary files disappear.
- Independent verification was bounded: the main assistant identified the startup counterexample and proof defects; supporting assistants checked its numerical values, the conservative startup repair and two local asymptotic repairs. No full-paper certification, formalization or simulation replay was performed.

**Disposition:** the exact mixture construction and the printed closed-form startup rule have different status. **Theorem 3.3 as printed has a coverage counterexample.** A corrected sufficient startup rule preserves the local outer-interval argument. The matrix statement and several asymptotic proofs also need the qualifications recorded below. This note does not treat a complete reading as a verified theorem library.

## Statistical target and comparison class

The observations lie in \([0,1]\), with natural filtration \(\mathcal F_t\). Write

\[
m_i=E[X_i\mid\mathcal F_{i-1}],\qquad
\mu_t=\frac1t\sum_{i=1}^t m_i,\qquad
\bar X_t=\frac1t\sum_{i=1}^t X_i.
\]

The target is the **average of the conditional means along the observed sequence**, not the current one-step mean \(m_t\). A confidence sequence satisfies
\(P(\forall t\ge t_0:\mu_t\in C_t)\ge1-\alpha\). The finite-sample construction allows dependent, non-identically distributed observations. The precise asymptotic-width analysis later imposes iid sampling and a particular predictor.

The paper seeks a closed-form, variance-adaptive interval centered at the unweighted sample mean. It compares principally with:

- The Waudby-Smith–Ramdas (WSR) predictable-plug-in interval, which uses a weighted sample mean and, in the displayed form, a constant conditional mean. Its weight schedule affects its asymptotic width.
- Howard–Ramdas–McAuliffe–Sekhon (HRMS) empirical Bernstein boundaries, which can target changing average conditional means and attain iterated-logarithm rates through stitching.
- Oracle Bernstein and Robbins mixture boundaries, whose implementations require known variance or a known sub-Gaussian variance proxy.

The empirical claim concerns the named closed-form comparators and tested sample sizes. The paper expressly acknowledges tighter implicit betting/mixture intervals, especially at small sample sizes. It does not establish universal optimality among all confidence procedures.

Running intersections are valid for a common fixed target \(\mu\). They are **not** automatically valid for the changing target \(\mu_t\), because an earlier set concerns a different average.

## Flipping the empirical Bernstein inequality

Define

\[
\psi_E(z)=-\log(1-z)-z,\qquad 0\le z<1.
\]

Modified Fan's inequality, Lemma 2.1, states

\[
\exp\{\lambda\xi-\psi_E(|\lambda|)\xi^2\}
\le1+\lambda\xi,
\quad \lambda\in(-1,1),\quad \xi\in[-1,1].
\]

For negative \(\lambda\), simultaneous sign reversal reduces it to the cited Fan inequality. The restriction \(|\xi|\le1\) is essential for this reversal.

For a predictable predictor \(\widehat X_i\), the modified Howard inequality centers the linear term at the true conditional mean while retaining an observable nonlinear penalty:

\[
E_{i-1}\exp\{\xi(X_i-m_i)-\xi^2\psi_E(|X_i-\widehat X_i|)\}\le1.
\]

Its scalar proof sets \(Y=X-EX\), \(\delta=\widehat X-EX\), applies Fan to \(Y-\delta\), and uses \(e^{\delta\xi}(1-\delta\xi)\le1\). Consequently

\[
B_t(\xi)=\exp\{\xi(S_t-t\mu_t)-\xi^2V_t\},\quad
S_t=\sum_{i\le t}X_i,\quad
V_t=\sum_{i\le t}\psi_E(|X_i-\widehat X_i|)
\]

is a nonnegative supermartingale for each fixed \(\xi\in[-1,1]\). The novelty is placing the empirical residual inside \(\psi_E\), leaving a quadratic dependence on the mixing parameter.

The printed domain \(\widehat X_i\in[0,1)\) does not itself imply the proof's strict \(|X_i-\widehat X_i|<1\): \(X_i=1,\widehat X_i=0\) is an endpoint exception. Taking predictors strictly in \((0,1)\) is a sufficient finite-valued condition. The recommended smoothed predictor
\(\widehat X_i=(1/2+\sum_{j<i}X_j)/i\) has this property. The note does not assume an undefined \(\psi_E(1)\) is an ordinary finite variance estimate.

\(V_t\) is a pathwise prediction-residual penalty, not an unbiased estimate of conditional variance. A good predictable predictor may reduce it; the theorem does not assert that learning such a predictor succeeds.

## Exact truncated-normal mixture

Choose \(\kappa>0\) before seeing the scored data, set

\[
Z=\Phi(1/\kappa)-\Phi(-1/\kappa),\quad
U_t=(2\kappa^2)^{-1}+V_t,\quad
G_\alpha=\kappa Z\sqrt{2\pi}/\alpha,
\]

and mix \(B_t(\xi)\) using a centered normal density with scale \(\kappa\), truncated to \([-1,1]\). Define

\[
I(y;u)=\int_{-1}^1e^{y\xi-u\xi^2}\,d\xi.
\]

Proposition 3.1 gives the exact interval

\[
C_t^{\rm mix}=\{m:I(S_t-tm;U_t)<G_\alpha\}.
\]

For fixed \(u>0\), \(I\) is even, convex, minimized at zero, strictly increasing for positive \(y\), and unbounded as \(y\to\infty\). Its positive root determines a symmetric interval about \(\bar X_t\); numerical inversion is needed. The center always belongs to the interval because its mixture wealth is at most one. Intersecting with the known range \([0,1]\) is permissible.

The closed expression used for inversion is

\[
I(y;u)=\frac{e^{y^2/(4u)}}{2\sqrt{u/\pi}}
\left[\operatorname{erf}\left(\sqrt u-\frac{y}{2\sqrt u}\right)
+\operatorname{erf}\left(\sqrt u+\frac{y}{2\sqrt u}\right)\right].
\]

A uniform mixing density instead gives threshold \(2/\alpha\) and uses \(V_t\) in place of \(U_t\). Indeed \(\kappa Z\to\sqrt{2/\pi}\) as \(\kappa\to\infty\). Appendix D prints a different constant, \(2/\sqrt\pi\), but the normalization and the correct limit already stated in Remark 3.2 give the former value.

The mixture density must be data-free for the argument given. Appendix D explicitly prohibits choosing the smallest interval across data-selected \(\kappa\) values without accounting for selection; it suggests an independent holdout or a multiplicity correction. Similarly, one confidence sequence does not automatically cover arbitrary post hoc choices among many predictors or data streams.

## Printed closed-form interval and its startup error

Theorem 3.3 defines \(t_0\) as the first \(t\ge1\) for which

\[
F(U_t):=\sqrt{\pi/U_t}\left(e^{U_t/4}-\tfrac12\right)\ge G_\alpha,
\tag{3.7}
\]

and claims coverage thereafter for

\[
C_t^{\rm apx}=(\bar X_t\pm W_t^{\rm apx}),\qquad
W_t^{\rm apx}=
\frac2t\sqrt{U_t\left[
\log\frac{\kappa Z/\alpha}{1-e^{-U_t/4}}
+\frac12\log(2U_t)\right]}.
\tag{3.8}
\]

The intended argument is to ensure that the positive root \(I(y_t;U_t)=G_\alpha\) obeys \(y_t\le U_t\). Both error-function arguments are then at least \(\sqrt{U_t}/2\), and a lower bound on the error function yields an explicit upper bound on the root. The startup condition printed in Eq. (3.7) does not ensure this.

### A direct coverage counterexample

Fix \(\kappa=100\), \(\alpha=0.05\), and the legal deterministic predictable sequence \(\widehat X_t\equiv0.5\). Let the observations be iid with

\[
P(X_t=0.5)=0.9,\qquad P(X_t=1)=0.1,
\quad\text{so }\mu_t=0.55.
\]

On the event \(X_1=0.5\), which has probability 0.9, the relevant values are

| Quantity | Value |
|---|---:|
| \(U_1\) | 0.00005 |
| \(G_\alpha\) | 39.9993333433332 |
| \(F(U_1)\) | 125.334547036476 |
| \(W_1^{\rm apx}\) | 0.0434845771096 |
| Upper endpoint of \(C_1^{\rm apx}\) | 0.5434845771096 |

Thus the printed rule starts at \(t_0=1\), but the interval misses \(0.55\). Its simultaneous noncoverage probability is at least **0.9**, exceeding the claimed 0.05. This example even has \(U_t\to\infty\) almost surely; it is not exploiting a permanently unchanging residual process.

The numbers were independently checked at 60-digit working precision. The gaps are large enough that coarse analytic bounds also certify the contradiction. In contrast,
\(I(0.05;U_1)=2.00080007967<G_\alpha\), so the true mean is inside the exact mixture interval on this event. **The counterexample concerns the printed closed-form approximation and startup rule, not the exact mixture construction.**

### Exact source of the error and a conservative repair

Lemma B.1 on p. 22 uses \(\operatorname{erf}(z)\ge1-e^{-z^2}\) and reaches

\[
I(U;U)\ge\frac{e^{U/4}}{2\sqrt{U/\pi}}
(2-e^{-U/4}-e^{-9U/4}).
\]

Correct expansion gives

\[
B_-(U)=\sqrt{\pi/U}
\left(e^{U/4}-\tfrac12-\tfrac12e^{-2U}\right),
\]

whereas the paper prints a **plus** before the last term. Dropping that incorrectly positive term produces Eq. (3.7). The contradiction is also visible in the limits: \(F(U)\to\infty\) but \(I(U;U)\to2\) as \(U\downarrow0\).

A sufficient replacement, independently checked within the local proof, is

\[
t_0^{\rm safe}=\inf\{t\ge1:U_t\ge2,\ B_-(U_t)\ge G_\alpha\}.
\]

For \(U\ge2\),

\[
B_-'(U)=\sqrt\pi U^{-3/2}
\left[(U/4-1/2)e^{U/4}+1/4+(U+1/4)e^{-2U}\right]>0.
\]

Since \(U_t\) is nondecreasing, this condition persists after it is first met. It gives \(I(U_t;U_t)\ge G_\alpha\), hence \(y_t\le U_t\), and the remaining outer-interval proof yields

\[
y_t^2\le4U_t\log\frac{G_\alpha\sqrt{U_t/\pi}}{1-e^{-U_t/4}},
\]

which is the same width formula (3.8). This is a conservative repaired startup rule, not a claim that the original condition was valid for every parameter choice. It does not guarantee finite startup for every allowed data stream; the exact mixture interval can be retained before startup. No revised theorem was attributed to the authors.

## Asymptotic widths: precise assumptions and constants

For iid, nondegenerate scalar data and the smoothed empirical-mean predictor, put
\(u=E\psi_E(|X-\mu|)>0\). Lemma 3.4 claims

\[
U_t/t\to u,\qquad
W_t^{\rm apx}\sim\sqrt{2u\log(t)/t}.
\]

These are asymptotics of the defined width; their use as a valid interval additionally requires a valid startup rule. For fixed \(\alpha\), its effect is lower order, of order \(\log(1/\alpha)/\log t\) in the squared width ratio. The paper correctly warns that this disappears slowly; the numerical illustration following Eq. (3.10) should not be treated as an exact finite-sample percentage.

The variance comparison is

\[
\sigma^2/2\le u\le
\frac{\psi_E(g(\mu))}{g(\mu)^2}\sigma^2,
\quad g(\mu)=\max\{\mu,1-\mu\}<1.
\]

Appendix C.4 supplies a two-point family approaching the upper ratio at fixed mean: probability \(\varepsilon\) at 1 and the remainder at \((\mu-\varepsilon)/(1-\varepsilon)\) for \(\mu<1/2\). Thus small variance **alone** does not imply \(u\sim\sigma^2/2\). The introductory skewness caveat and this example are more precise than the unrestricted wording of Table 2's caption. The paper also states \(u\le\log2-1/2\), with equality for Bernoulli(1/2).

For the particular WSR schedule

\[
\lambda_t=
\sqrt{\frac{2\log(2/\alpha)}{\widehat\sigma_{t-1}^2\,t\log(1+t)}}\wedge\frac12,
\]

Appendix C.1 derives

\[
W_t^{\rm WSR}\sim
\frac\sigma2\sqrt{\frac{\log(2/\alpha)\log t}{2t}}
(1+\log\log t).
\]

The denominator is asymptotic to a constant times \(\sqrt{t/\log t}\); the penalty numerator grows like \(\log(2/\alpha)\log\log t\). Weighted strong laws and summation estimates establish those orders. Removing the significance-level factor from the chosen weights removes it from the limiting coefficient, at a practical finite-sample cost. This result concerns the stated schedule, not every predictable-plug-in or betting CS.

Appendix C.2 gives the analogous calculation for predictable-plug-in Hoeffding bounds. C.3 compares Robbins' known-proxy normal mixture, whose normalized limit is \(\sigma\). C.5 uses the imported HRMS oracle Bernstein expansions to obtain the same \(\sqrt{\log t/t}\) coefficient and the limiting iterated-logarithm coefficient \(\sqrt2\sigma\).

### Local asymptotic proof corrections

B.3 correctly differentiates \(\psi_E(|x-y|)\), then incorrectly substitutes \(|\widehat X_i-\theta|\) for \(|X_i-\theta|\) in its mean-value bound. The resulting \(\varepsilon^2/(1-\varepsilon)\) estimate is not justified. For \(m=\min(\mu,1-\mu)>0\), eventually the segment between \(\widehat X_i\) and \(\mu\) lies in \([m/2,1-m/2]\), giving the valid uniform bound

\[
|\psi_E(|X_i-\widehat X_i|)-\psi_E(|X_i-\mu|)|
\le(2/m-1)|\widehat X_i-\mu|\to0.
\]

Cesàro averaging and the bounded iid strong law then recover \(U_t/t\to u\). This independently checked repair preserves the nondegenerate scalar asymptotic claim.

Zero variance must be treated separately: the comparison sequence is then identically zero, so neither \(W_t\sim0\) nor the displayed ratio \(R_t\) is defined as asserted. For the constant sequence \(X_i=1/2\), the smoothed predictor is exactly 1/2, \(U_t=(2\kappa^2)^{-1}\), and the defined width is a positive constant divided by \(t\), not an asymptotic ratio to zero.

C.1 also infers almost-sure control of a weighted martingale merely from zero expectation. That implication alone is invalid. In the displayed bounded-iid setting, the deterministic weights \(1/[i\log(i+1)]\) are square summable and the increments are bounded, supplying the missing second-moment convergence justification. This is a local missing argument, not a refutation of the stated nondegenerate rate.

## Stitching and the order of parameter limits

Theorem 4.1 applies fixed-\(\xi\) Ville bounds over epochs in the observed penalty \(V_t\). Choose \(\eta>1\), \(L_0\ge1\), and a positive increasing function \(h\) with \(\sum_{j\ge0}1/h(j)\le1\). On one event of probability at least \(1-\alpha\), for every time satisfying

\[
V_t\ge L_0,\qquad
h(\log_\eta(V_t/L_0))\le(\alpha/2)e^{V_t},
\]

the bound is

\[
|\bar X_t-\mu_t|
\le\frac{1+\sqrt\eta}{t}
\sqrt{V_t\left[\log(2/\alpha)+
\log h(\log_\eta(V_t/L_0))\right]}.
\]

The proof allocates \(\alpha_j=\alpha/h(j)\), chooses one fixed \(\xi_j\) for each epoch, and uses a countable union bound. The additional time condition ensures its unclipped choice does not exceed the allowed value one. The epoch index is based on \(V_t\), not directly on chronological time. This derivation does not use the defective closed-form mixture startup lemma.

For \(h(j)=\zeta(s)(j+1)^s\), fixed \(s>1\), and iid positive \(u\), the actual normalized limiting coefficient is
\((1+\sqrt\eta)\sqrt{s u}\). The coefficient \(2\sqrt u\) shown in summary comparisons is approached only by subsequently taking \(\eta,s\downarrow1\). Those limits inflate the finite-sample constants; they are not attained by a single admissible choice. The same distinction applies to the oracle/HRMS optimal constants, explicitly acknowledged in Appendix C.5. Experiments use \(\eta=2,s=1.4\).

## Matrix extension and its unresolved printed scope

The matrix observations satisfy \(0\preceq\mathbf X_i\preceq I_d\). Their target is
\(\mathbf M_t=t^{-1}\sum_iE_{i-1}\mathbf X_i\). With spectral functional calculus,

\[
\mathbf V_t=\sum_{i\le t}\psi_E(|\mathbf X_i-\widehat{\mathbf X}_i|).
\]

Lemma 5.1 replaces the scalar exponential by

\[
L_t=\operatorname{tr}\exp\left\{
\sum_i\xi_i(\mathbf X_i-E_{i-1}\mathbf X_i)
-\sum_i\xi_i^2\psi_E(|\mathbf X_i-\widehat{\mathbf X}_i|)
\right\},\quad L_0=d.
\]

It invokes a matrix supermartingale lemma from Howard et al./Wang–Ramdas; a scalar commutativity argument cannot simply be reused. A Rayleigh-vector argument bounds the scalar mixture involving \(\lambda_{\max}(\mathbf S_t-t\mathbf M_t)\) and \(\lambda_{\max}(\mathbf V_t)\) by this trace mixture. The argument works for either sign of \(\xi\) by retaining the same maximizing vector.

Theorem 5.2 then claims a bound on
\(|\lambda_{\max}(\bar{\mathbf X}_t-\mathbf M_t)|\), with scalar-shaped halfwidth and \(d\kappa Z/\alpha\) inside the logarithm. This object should not be silently identified with the operator norm of an arbitrary symmetric error matrix.

The printed matrix result is not ready for direct import:

- Eq. (5.4) contains an undefined \(b\) in \(e^{bU_t/4}\), and uses the scalar threshold \(G_\alpha\), while B.5's root equation uses \(G_{\alpha,d}=dG_\alpha\).
- It inherits the scalar startup issue. The same local outer-bound argument would require a correctly justified dimension-dependent startup, for example the conservative \(U_t\ge2, B_-(U_t)\ge dG_\alpha\), conditional on the exact trace-mixture premise.
- B.5 places an unintended logarithm on the mixture threshold and has incorrect displayed Ville probability bounds. The intended supermartingale initial value is \(d\), so the crossing threshold is \(d/\alpha\).
- In B.6 the predictable centering term needed for cancellation is \(\xi_i(E_{i-1}\mathbf X_i-\widehat{\mathbf X}_i)\); the text writes the average \(\mathbf M_i\) there. The strict endpoint issue for the predictor also has a matrix analogue.

No complete corrected matrix coverage theorem was independently certified in this reading.

### Matrix width asymptotics under a sufficient interior hypothesis

Proposition 5.3 gives the asymptotic coefficient
\(\sqrt{2v}\), where
\(v=\lambda_{\max}(E\psi_E(|\mathbf X-\mathbf M|))\). B.7 calls \(\lambda_{\max}\) the operator norm, asserts a false one-sided Lipschitz bound for arbitrary symmetric differences, and declares the whole space of symmetric matrices compact. The singularity of \(\psi_E\) at one also prevents the stated global continuity argument.

A bounded local repair is available for fixed dimension, iid data, \(0\prec\mathbf M\prec I\), and \(v>0\). Let
\(\delta=\min\{\lambda_{\min}\mathbf M,1-\lambda_{\max}\mathbf M\}>0\). The smoothed sample predictor converges in operator norm, so both difference matrices eventually lie in the compact set \(\{A=A^\top:\|A\|_{\rm op}\le1-\delta/2\}\). On this set \(A\mapsto\psi_E(|A|)\) is uniformly continuous. Cesàro averaging and the bounded matrix strong law give
\(\|\mathbf V_t/t-E\psi_E(|\mathbf X-\mathbf M|)\|_{\rm op}\to0\). The correct Weyl bound is
\(|\lambda_{\max}A-\lambda_{\max}B|\le\|A-B\|_{\rm op}\).

This establishes the defined width's claimed asymptotic equivalence under those sufficient conditions. It does not require the entire expected penalty matrix to be positive definite. Boundary-mean matrices and zero \(v\) were not fully analyzed, and this width calculation does not repair the separate coverage statement by itself.

## Experiments, tables and reproducibility limits

The results are synthetic comparisons of interval widths and example trajectories, not a fresh empirical proof of simultaneous coverage. No repeated-run coverage calibration is reported in the inspected manuscript.

1. **Figure 1:** iid Bernoulli(1/2), Beta(5,2) and uniform observations, with \(\alpha=.05,\kappa=.25\). The displayed new width typically beats WSR after roughly hundreds to a thousand observations; WSR is often tighter earlier. HRMS has a larger displayed width over these ranges despite its better asymptotic rate. The plots extend to \(10^5\); claims about still larger crossover ranges are textual discussion, not an additional displayed panel.
2. **Figure 2:** a Bernoulli mean switches from .8 to .2 after the first tenth of a run, and a separate experiment uses smooth variation. The dotted curve is the cumulative average conditional mean. The WSR interval targets a different weighted quantity when means vary, explaining its displayed failure to track this target.
3. **Figure 3:** the exact and approximate intervals visually coincide on a Bernoulli(1/2) run, with \(\kappa=1\) shown in the panel and the startup marked. Another panel shows approximately linear \(U_t\) growth for several distributions. Neither plot checks all \(\kappa\) or the small-\(U\) counterexample.
4. **Figure 4:** stitched bounds at \(\eta=2,s=1.4\) for Bernoulli(1/2) and Beta(30,10). The new bound can win early, while the HRMS leading constant eventually benefits it; there is no universal finite-time dominance statement.
5. **Figure 5:** the skewed two-point construction separates the new empirical width from an oracle Bernstein width, using \(\varepsilon=.01,\alpha=.05,\kappa=.25\). The paper's caption does not supply every distribution parameter needed for a standalone reproduction.
6. **Figure 6:** exact mixtures with several fixed \(\kappa\) values, iid Bernoulli(1/2) or Beta(10,30), \(\alpha=.01\). The effect depends on the distribution and converges toward the uniform-mixture limit for large \(\kappa\). Choosing the best curve after observing data is not covered without a selection adjustment.

Table 1 summarizes the asymptotic comparisons, subject to the positive-variance and order-of-limits qualifications above. Table 2 compares \(\sigma^2/2\) and \(u\): e.g. Bernoulli(.5) gives .125 versus approximately .194, and Bernoulli(.1) gives .045 versus approximately .144. These examples already show why variance alone is not the complete penalty.

Appendix D links the [author implementation](https://github.com/bchugg/empirical-bernstein) and [confseq](https://github.com/gostevehoward/confseq). Its Python-version remark is a historical statement at the paper's writing, not a verified current installation requirement. No code was executed to recreate its figures. A narrow static check of [methods.py at commit 635c756f202b72e49b497af13f3d33f1aeec8b30](https://github.com/bchugg/empirical-bernstein/blob/635c756f202b72e49b497af13f3d33f1aeec8b30/methods.py), September 16, 2026, confirms that `CR_mixture` and `hitting_time` still use the defective Eq. (3.7) condition; `CR_mixture` permanently switches after the first trigger. `CR_mixture_approx` is a separate entry with no startup gate. `compute_Ut` uses the stated offset with no additional lower bound. This check covers only those functions, not the full repository. The first-observation counterexample also has the same initial smoothed predictor used there.

The pinned repository also contains a shared-source wrapper titled *Tighter closed-form variance-adaptive confidence sequences for time-varying means* under `paper/alt2027`, and a separate September 2026 manuscript titled *Refining the residual-aware Gaussian mixture: construction and simulation results* under `sharp_paper`. Only their metadata/entry relationships were screened. Anonymous conference-template directories establish neither submission nor acceptance, and neither artifact is authenticated as arXiv v2 of the present paper. Their unread bodies cannot be presumed to correct the older theorem or code.

## Dependencies, applicability and remaining questions

The proof inputs are Fan's scalar inequality, Howard's empirical Bernstein and matrix-supermartingale methods, Ville's inequality, truncated-normal integration, strong laws and matrix functional calculus. The comparison claims use WSR's specified predictable weights, HRMS oracle/stitching bounds, Robbins' mixture, and Wang–Ramdas matrix bounds. Appendix A traces applications to bandits, adaptive sampling, PAC-Bayes, boosting and LLM generalization. Reading those citations does not mark the cited works fully read.

The paper leaves open a fully empirical closed-form CS with the oracle coefficient \(\sigma\) at the \(\sqrt{\log t/t}\) scale. Its achieved \(\sqrt{2u}\) is generally larger. The valid exact mixture and the separately derived stitching result remain useful references even though the printed closed-form startup rule fails.

For any proposed FP use, one would still need to specify an actually observed bounded statistic, its filtration, a predictable residual predictor, the precise cumulative conditional-mean target and any selection correction. The result does not by itself certify a newly selected counterfactual recurrent rule, future held-out predictive risk, unbounded log loss, or a finite-bit learned state. No FP architecture or experimental change is proposed here. The immediate actionable literature finding is the startup defect and its restricted repair, with exact-mixture, asymptotic-width and matrix claims kept distinct.
