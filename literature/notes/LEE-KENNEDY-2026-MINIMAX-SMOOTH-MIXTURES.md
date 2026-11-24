# Lee–Kennedy: minimax estimation of a smooth binomial mixing density

## Source and actual reading

JungHo Lee and Edward H. Kennedy, **Minimax Rates for Learning Smooth Populations of Parameters**, [arXiv:2610.04135v2](https://arxiv.org/abs/2610.04135v2), [PDF](https://arxiv.org/pdf/2610.04135v2), [TeX](https://arxiv.org/src/2610.04135v2). Version 1 was submitted October 2, 2026. Version 2 was submitted October 9 at 16:15 UTC and its PDF is dated October 12. The primary submission history was rechecked on November 24 and lists these two versions. No journal reference, withdrawal or correction notice was present in the inspected record.

**Fully read on November 24, 2026:** all 53 PDF pages through the complete active TeX, main §§1–6, Appendix A, Appendix B.1–B.7, all statements and proofs, three actual figures, four ordinary footnotes, two author-contact footnotes, acknowledgments and all 35 printed references. Selected definitions, coefficient formulas, heterogeneous bounds and rate calculations were checked visually in the PDF. The source archive contains six files including three figure PDFs. Commented-out draft passages are not treated as published claims.

The acknowledgments disclose author use of ChatGPT, including GPT 5.5, for literature discovery, proof calculations and exposition, followed by author review. This is an outside author preprint, not an official OpenAI release. The main assistant read the manuscript. A supporting assistant performed the bounded coefficient and heterogeneous-profile checks described below. No formal proof or full independent theorem certification is claimed.

## 1. Problem, class and loss

The observations are independent counts
\[
Q_i\overset{\mathrm{iid}}{\sim}p,\qquad
X_i\mid Q_i\sim\operatorname{Bin}(t_i,Q_i).
\]
The trial counts are fixed, known positive integers. Homogeneous trials have \(t_i=t\). The latent law has a density on \([0,1]\), rather than being an arbitrary probability measure.

Writing \(s=r+\alpha\), with \(r\) the largest integer strictly below \(s\) and \(0<\alpha\le1\), the class bounds the full norm
\[
\|p\|_{C^s}=\sum_{j=0}^{r}\|p^{(j)}\|_\infty+
[p^{(r)}]_{C^\alpha}
\]
by \(L\), and separately bounds \(\|p\|_\infty\) by \(p_{\max}\). The lower bounds require **\(L,p_{\max}>1\)**, leaving room for perturbations around the uniform density. The target is one fixed interior value \(p(u)\), uniformly over \(u\in[\delta,1-\delta]\). The minimax loss is expected **absolute pointwise density error**
\[
\mathcal R_{n,\mathbf t}
=\inf_{\widehat p}\sup_{p\in\mathcal H^s(L,p_{\max})}
E_p|\widehat p(u)-p(u)|.
\]
It is neither mixing-measure Wasserstein distance nor prediction KL. The paper explicitly distinguishes its target from the earlier distribution-estimation literature.

## 2. Exact spectral structure of the observation experiment

Let \(b_{t,x}(q)=\binom txq^x(1-q)^{t-x}\), and set
\[
(B_tf)(x)=\int_0^1b_{t,x}(q)f(q)\,dq.
\]
Uniform mixing induces the uniform count law \(1/(t+1)\). The Bernstein–Durrmeyer operator
\[
(BD_tf)(q)=(t+1)\sum_{x=0}^{t}b_{t,x}(q)(B_tf)(x)
\]
therefore expresses the quadratic form governing the observable chi-squared distance of small density perturbations.

The normalized shifted Legendre polynomials
\[
\phi_k(q)=\sqrt{2k+1}\,P_k(2q-1)
\]
diagonalize this operator. Lemma 1 imports the eigenvalue identity from Derriennic (1981):
\[
BD_t\phi_k=\lambda_{t,k}\phi_k,\qquad
\lambda_{t,k}=\prod_{j=0}^{k-1}\frac{t-j}{t+j+2}.
\]
Here \(\lambda_{t,0}=1\), and \(\lambda_{t,k}=0\) for \(k>t\). For degrees bounded by \(\rho t\), with fixed \(\rho<1\), the inverse eigenvalues grow exponentially in \(k^2/t\). Thus visibility and statistical stability are different constraints. Degree \(k\le t\) is identifiable from exact count probabilities but can require many independent groups to estimate accurately.

The normalized observable Hahn polynomials are
\[
\psi_{k,t}(x)=\lambda_{t,k}^{-1/2}(t+1)(B_t\phi_k)(x).
\]
They are orthonormal under the uniform count distribution. Proposition 1 gives
\[
E[\psi_{k,t}(X)\mid Q=q]
=\sqrt{\lambda_{t,k}}\,\phi_k(q),
\]
so the Legendre coefficient \(\theta_k=\int p\phi_k\) has an unbiased estimate obtained by dividing the empirical Hahn mean by \(\sqrt{\lambda_{t,k}}\).

The proposed estimator applies a fixed smooth spectral filter:
\[
\widehat p_m(q)=
\sum_{k=0}^{2m}\eta(k/m)\widehat\theta_k\phi_k(q),
\]
where \(0\le\eta\le1\), \(\eta=1\) on \([0,1]\), and \(\eta=0\) on \([2,\infty)\). The requirement \(2m\le t\) makes all included coefficients observable. Smoothing the cutoff supplies a uniformly bounded approximation operator, rather than merely truncating the expansion sharply.

## 3. Homogeneous minimax result and proof architecture

Define
\[
S_m(u)=\sum_{k=0}^{m}\lambda_{t,k}^{-1}\phi_k(u)^2.
\]
For fixed admissibility constants \(m_0,\rho\), Corollary 2 identifies the rate
\[
\mathcal R_{n,t}\asymp
\min_{m_0\le m\le\lfloor\rho t\rfloor}
\left\{m^{-s}+\sqrt{S_m(u)/n}\right\}.
\]
The constants may depend on the fixed smoothness, class and interior-point parameters. The admissible set and the lower bound on \(t\) are explicitly set out in Assumption 1. Theorem 1 extends the lower rate statement to the remaining bounded trial counts.

For sufficiently large \(n\), Corollary 3 gives
\[
\mathcal R_{n,t}\asymp
\begin{cases}
t^{-s},&t\le\log n,\\[2mm]
\left[t\left\{1+\log\!\left(n/t^{s+1/2}\right)\right\}\right]^{-s/2},
&\log n<t<n^{2/(2s+1)},\\[2mm]
n^{-s/(2s+1)},&t\ge n^{2/(2s+1)}.
\end{cases}
\]
The logarithmic correction in the middle regime matters. Replacing it everywhere by \(\log n\) is incorrect near the transition to the direct-latent density-estimation rate. At a constant-factor distance below that transition, the braces are order one.

The lower proof uses two kinds of alternatives around \(p_0=1\).

1. **Statistically attenuated alternatives.** Before smoothness and zero-integral constraints, the optimal degree-\(m\) perturbation with value one at \(u\) has coefficients proportional to \(\lambda_{t,k}^{-1}\phi_k(u)\). Its observable quadratic cost is \(S_m(u)^{-1}\). The paper removes low degrees and multiplies by
   \[
   w_R(q)=\{q(1-q)/(u(1-u))\}^R,\qquad R\ge r+2.
   \]
   This preserves the value at \(u\), enforces zero integral by orthogonality, and controls endpoint derivative growth. Fixed degree shifts introduced by \(w_R\) preserve eigenvalues up to constants on the admissible range. The perturbation has \(C^s\) norm \(O(m^s)\). Amplitude \(c\min\{m^{-s},\sqrt{S_m(u)/n}\}\) then satisfies both class membership and bounded product chi-squared divergence.
2. **Exactly invisible alternatives.** A fixed-width block strictly above degree \(t+2R\), multiplied by the same taper, stays orthogonal to every binomial likelihood polynomial. The two induced count distributions are exactly equal for any number of groups. The permitted separation is order \(t^{-s}\). This is a worst-case class result, not a statement that every moment vector has a nontrivial fiber.

Legendre block bounds prevent normalization from failing when a single polynomial vanishes at \(u\). Their proof uses uniform interior asymptotics and the bounded sum of a geometric oscillation. Endpoint derivative estimates and Hölder interpolation control the taper. The lower bound then uses Le Cam's two-point argument.

For the upper bound, filtered polynomial approximation gives bias \(O(m^{-s})\). Since the count mass is at most \(p_{\max}/(t+1)\), Hahn orthogonality bounds variance by \(p_{\max}S_{2m}(u)/n\). Applying the estimator at half the comparison degree matches the lower envelope. Appendix B.6 derives the three regimes from exponential bounds for \(S_m\).

This supplies a minimax benchmark missing from the earlier [Lee–Baćak–Kennedy paper](LEE-BACAK-KENNEDY-2026-HETEROGENEOUS-TRIALS.md). It does not retroactively establish that the earlier empirical-proportion KDE attains these bounds, or repair every earlier finite-bandwidth argument.

## 4. Heterogeneous trials require an information profile

Set \(T=\max_i t_i\) and
\[
I_k=\sum_{i:t_i\ge k}\lambda_{t_i,k},\qquad I_0=n.
\]
The paper's coefficient estimator is
\[
\widehat\theta_k=
\frac1{I_k}\sum_{i:t_i\ge k}
\sqrt{\lambda_{t_i,k}}\psi_{k,t_i}(X_i).
\]
For \(k\ge1\), its variance under uniform mixing is exactly \(1/I_k\). These are inverse-variance weights among deterministic weighted averages of the individual unbiased coefficient estimates. For a general density in the class the paper gives the bound \(p_{\max}/I_k\), not a claim of exact global efficiency. The constant coefficient \(k=0\) is known and has variance zero.

**Theorem 5 and Corollary 4**, pp. 23–24, give
\[
\mathcal R_{n,\mathbf t}\asymp
\min_{m_0\le m\le\lfloor\rho T\rfloor}
\left\{m^{-s}+\sqrt{m/I_m}\right\},
\]
under Assumption 2's sufficiently large maximum trial count and the same nondegenerate smoothness class. The filtered estimator first has the more detailed upper bound
\[
m^{-s}+
\left\{\sum_{k=0}^{2m}\phi_k(u)^2/I_k\right\}^{1/2}.
\]
Half-degree selection and monotonicity of \(I_k\) bound this by the displayed minimax envelope.

The heterogeneous lower proof cannot assume nearby eigenvalues are comparable. A large collection of groups of length \(k-1\) can contribute to \(I_{k-1}\) while contributing zero to \(I_k\). Appendix A handles this by putting an unweighted block at degrees \(m+2R+1,\ldots,2m+2R\). After tapering, all degrees remain greater than \(m\). Its squared \(L_2\) norm is \(O(1/m)\), so monotonicity alone bounds the aggregate observable cost by \(I_m/m\). No restriction on the number of short groups is silently needed.

The max–min to min–sum conversion also tolerates sharp information drops. At the first crossing of decreasing \(m^{-s}\) and increasing \(\sqrt{m/I_m}\), the previous degree has a comparable bias. At the first admissible degree, at least the group with \(t_i=T\) supplies a fixed positive information floor. If there is no crossing, the invisible perturbation at degree above \(T\) supplies the \(T^{-s}\) endpoint. This bounded check found no counterexample to this part of the argument.

For a prescribed decreasing profile \(t_{[i]}\asymp(n/i)^{1/\beta}\), Corollary 5 obtains
\[
\mathcal R_{n,\mathbf t}\asymp n^{-s/(2s+2\beta+1)}.
\]
Its proof shows \(I_m\lesssim nm^{-2\beta}\) in general and a matching lower bound at the selected degree, supplied by groups with \(t_i\) of order at least \(m^2\).

## 5. Figures, bounded independent calculations and evidence level

There is no empirical estimator benchmark, adaptive trial-allocation experiment or data application in this manuscript. Figure 1 is an explicitly smoothed illustration of the theoretical rate for \(n=10^6\). Figure 2 illustrates a normalized oscillatory perturbation and its two nearby densities at \(u=1/2\). Figure 3 computes spectral information for three fixed allocations, each with 2,000 groups and 100,000 trials.

The Figure 3 eigenvalue products were independently recomputed with exact rational arithmetic, rounding only the table:

| Degree | All groups at 50 | Half at 10, half at 90 | 90% at 10, 10% at 410 |
|---:|---:|---:|---:|
| 1 | 1923.076923 | 1811.594203 | 1699.029126 |
| 5 | 1109.351864 | 776.709747 | 289.767275 |
| 10 | 227.824363 | 297.758629 | 153.037311 |
| 20 | 0.418241 | 9.511901 | 71.951744 |
| 50 | \(1.00098\times10^{-26}\) | \(1.29700\times10^{-10}\) | 0.397815 |

The winner changes with degree. Concentrating trials does not improve all aspects of the experiment.

A supporting exact calculation used the shifted Legendre polynomial's monomial coefficients and replaced \(q^j\) by the unbiased factorial-moment statistic \((X)_j/(t)_j\). All 14 pairs with \(t\in\{1,2,3,5,10\}\) and \(1\le k\le\min(t,4)\) had zero uniform-count mean and variance \(1/\lambda_{t,k}\) after Legendre normalization. This verifies selected finite spectral identities. It is not a numerical minimax experiment.

**Signed-estimator qualification, independently checked:** with \(m=1\), \(t\ge2\), and every observed count equal to zero, the proposed filter gives \(\widehat p_1(q)=4-6q\). Its integral is one, but its value at \(q=3/4\) is \(-1/2\). Nonnegativity is not required for a pointwise density-value estimator, so this does not contradict the paper's theorem. It matters if one tries to turn the estimate directly into a predictive probability law.

No substantive failure of the inspected central spectral or heterogeneous-profile claims was found in these bounded checks. The imported approximation theorems, all constants and the complete minimax theorem suite were not independently certified.

## 6. Dependencies, open questions and use boundary

Key dependencies are Derriennic's Bernstein–Durrmeyer eigenbasis, Szegő's Legendre asymptotics and positive Cesàro kernels, Jackson polynomial approximation, and Tsybakov's testing bounds. Appendix B.5 proves filter stability through third finite differences and positive second-order Cesàro kernels. Reading these uses does not count as fully reading the cited works.

The risk-optimal degree depends on smoothness. The paper suggests Lepski comparisons but explicitly leaves threshold selection and adaptive pointwise risk guarantees to future work. Covariates, transport between pointwise-density and distributional losses, and latent trial counts are also future directions.

For subsequent research use, retain all of these boundaries:

- Trial counts are fixed in advance. An episode stopped when its first bit is one no longer has an ordinary binomial count law conditional only on its observed length. A data-dependent continuation or reset policy therefore requires its own observation model and analysis.
- The class excludes discrete or arbitrary singular mixing laws. This paper does not cover the unrestricted measure class currently registered in NEXT.md.
- The target is an interior density value. There is no theorem controlling total forward KL on a fresh long group, posterior update stability or all later prediction horizons.
- Spectral coefficients and tables are not given a charged finite-bit memory or computation analysis. A real-valued coefficient count does not establish an installed-state budget.
- Figure 3 compares prescribed allocations. It supplies no learned policy, reset-cost optimum or adaptive advantage theorem.

No FP transfer theorem is proposed. The direct contribution is a precise recent statistical benchmark for smooth populations and a full degree-specific account of how trial depth affects information. The next selected primary source is Singh–Singh's 2026 fixed-rollout pass@k paper, whose screened abstract addresses identification beyond the observed group length and unique-extension exceptions. Its claims remain unadopted until the body is read.
