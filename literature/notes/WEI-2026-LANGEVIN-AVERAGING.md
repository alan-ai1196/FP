# Langevin averaging: a weak stationary bias becomes a learned direction

**Reader:** Pro-D  
**Reading:** November 26–27, 2026, Asia/Shanghai  
**Read edition:** Stanley Wei, Alex Damian and Jason D. Lee, *Improved high-dimensional estimation with Langevin dynamics and stochastic weight averaging*, ICLR 2026, official 34-page proceedings PDF. The official BibTeX gives pp. 88246–88279.

## Provenance and actual coverage

- [Official proceedings record](https://proceedings.iclr.cc/paper_files/paper/2026/hash/8e364d41159bb166c89a00a1a8bddfc0-Abstract-Conference.html)
- [Read official PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/8e364d41159bb166c89a00a1a8bddfc0-Paper-Conference.pdf)
- [Official bibliography export](https://proceedings.iclr.cc/paper_files/paper/6202-/bibtex)
- [OpenReview record](https://openreview.net/forum?id=GYXUD3hGTh)
- [ArXiv 2603.06028v1](https://arxiv.org/abs/2603.06028v1), submitted March 6, 2026, 08:23:24 UTC
- [ArXiv source](https://arxiv.org/src/2603.06028v1)

The main reader covered all 34 official PDF pages, Sections 1–5, Appendices A–H, all proofs and formulas, the algorithm, both two-panel figures, two scientific footnotes and the 33-item reference list. There are no tables. Original PDF pages 4, 8, 9 and 19 were visually inspected. In particular, the original algorithm and the source TeX confirm the favorable drift sign, which is easy to misread from layout extraction.

The separate arXiv PDF has 42 pages. Its metadata, algorithm, main even-case theorem and selected TeX passages were checked. It was not independently read in full or fully aligned against the final. The even-case time discrepancy described below is present in both inspected editions.

No explicit AI-assistance disclosure was found in the read manuscript. Actual use is undetermined. This is a peer-reviewed ICLR paper, not an official OpenAI or Anthropic release. The stationary identities, Brownian variance formulas and validation result below are independent analytic deductions. They do not certify the complete source proofs. No experiment, discretization study, code audit or formal proof replay was performed.

## 1. What the construction does

The learning trajectory need not itself align with the target. If a noisy process has a small directional bias, averaging many noisy positions can extract that bias after normalization. An even signal may have zero vector mean and instead appear in the time-averaged second moment.

The paper makes this mechanism concrete on the unit sphere. The gradient comes from a fixed empirical dataset, while externally supplied Brownian noise keeps the dynamics close to uniform spherical motion. The time average approaches a partial-trace-type estimator. Data reuse and temporal accumulation are essential features of this construction.

The statistical object is a planted continuous direction. The mechanism does not construct an unknown recurrent transition rule. Its sample exponent does not price the much longer averaging time or a numerical simulation of the diffusion.

### Observation models

**Tensor PCA.** Observe

\[
\mathcal T=u^{\otimes k}+n^{-1/2}Z,\qquad u\in S^{d-1},
\]

where the entries of \(Z\) are IID standard Gaussians. The loss is
\(L(\theta)=-\langle\mathcal T,\theta^{\otimes k}\rangle\). Here \(n\) is an inverse-noise parameter. Explicitly storing the observed tensor already takes \(d^k\) entries.

**Single-index regression.** Observe IID

\[
X_i\sim N(0,I_d),\qquad
Y_i=\sigma(u^\top X_i)+\xi_i,\qquad
\xi_i\sim N(0,1)
\]

with independent noise. The link \(\sigma\) is known, normalized by
\(\mathbb E\sigma(G)^2=1\), and \(\sigma,\sigma',\sigma''\) are uniformly bounded. The loss is the correlation objective

\[
L_n(\theta)=1-\frac1n\sum_iY_i\sigma(\theta^\top X_i).
\]

If \(\sigma=\sum_j c_jh_j\) in normalized Gaussian Hermites, its information exponent is
\(k^\star=\min\{j\geq1:c_j\ne0\}\). The source's bounded-link theorem and its polynomial-link experiments are different scopes.

Label preprocessing can change the relevant exponent, but it may also change the known-link and additive-noise interface. One cannot automatically substitute an arbitrary transformed label into every assumption of the displayed regression theorem.

## 2. Algorithm and source guarantees

Let \(P_\theta^\perp=I-\theta\theta^\top\), let \(\nabla_S\) denote the spherical gradient, and set \(b=-\nabla_SL_n\). Algorithm 1 starts uniformly on \(S^{d-1}\) and runs

\[
d\theta_t=
\left[-\frac{d-1}{2}\theta_t+\epsilon b(\theta_t)\right]dt
 +P_{\theta_t}^{\perp}dW_t. \tag{1}
\]

The sign of the \(\epsilon b\) term is positive. The geometric drift and projected noise preserve the sphere. The source calls \(\epsilon\) an inverse-temperature parameter, so small \(\epsilon\) means that noise dominates the learning drift.

The algorithm retains

\[
\widehat m_T=\frac1T\int_0^T\theta_t\,dt,\qquad
\widehat M_T=\frac1T\int_0^T\theta_t\theta_t^\top\,dt. \tag{2}
\]

For odd \(k^\star\), it returns \(\widehat m_T/\|\widehat m_T\|\). For even \(k^\star\), it returns a top eigenvector of \(\widehat M_T\). The printed selection requires knowing the parity.

| Regime | Source sample statement | Temperature and averaging time |
|---|---|---|
| Odd exponent, direct recovery | \(n\gtrsim d^{(k^\star+1)/2}/\Delta^2\) | \(\epsilon=o(d^{-(k^\star-3)/2})\), \(T\gtrsim d^{k^\star}/\epsilon^2\) |
| Odd exponent, warm start | \(n\gtrsim d^{k^\star/2}\) gives correlation of order \(d^{-1/4}\), followed by additional online SGD | Corollary 1 invokes a separate warm-start result. It is not recovery by the average alone. |
| Even exponent | \(n\gtrsim d^{k^\star/2}/\Delta^2\) | \(\epsilon=o(d^{-(k^\star-2)/2})\). Main Theorem 3 prints \(T\gtrsim d^{k^\star+1}/\epsilon^2\), while Appendix Theorem 5 uses \(d^{k^\star+2}/\epsilon^2\). |

The exponent-\(1\) case retains the ordinary \(n\gtrsim d\) information requirement. The unqualified \(d^{k^\star/2}\) headline and warm-start discussion must not be read as recovery of a generic \(d\)-dimensional direction from only \(\sqrt d\) samples.

The source's error wording is not uniform across statements. The odd propositions give a correlation at least \(1-\Delta\). The even propositions state squared correlation at least \(1-\Delta\), with an intermediate sine-angle estimate. These should not silently be relabeled as the same Euclidean error.

The time \(T\) is continuous diffusion time. Algorithm 1 supplies no finite discretization step with a matching end-to-end numerical error theorem. It therefore does not specify a number of executable gradient evaluations from \(T\) alone.

## 3. Proof mechanism: noise supplies an averaging measure

The source couples \(\theta_t\) with stationary spherical Brownian motion

\[
d\beta_t=-\frac{d-1}{2}\beta_t\,dt+P_{\beta_t}^{\perp}dW_t
\]

using the same driving noise and initialization. Write \(E_t=\theta_t-\beta_t\).
The projection difference obeys

\[
\|P_{\theta_t}^{\perp}-P_{\beta_t}^{\perp}\|_F^2
=2\|E_t\|^2-\tfrac12\|E_t\|^4.
\]

The stochastic discrepancy therefore shrinks with the displacement itself. A dissipative-process estimate bounds
\(\sup_{t\leq T}\|E_t\|\) by a constant times
\(\epsilon\sup\|b\|/d\) on a suitable finite-horizon event.

For a centered observable \(f\) of \(\beta_t\), the source solves the Poisson equation
\(-\mathcal L_0\phi=f\), where \(\mathcal L_0=\frac12\Delta_{S^{d-1}}\), by
\(\phi=\int_0^\infty P_tf\,dt\). It obtains

\[
\frac1T\int_0^Tf(\beta_t)\,dt
=\frac{\phi(\beta_0)-\phi(\beta_T)}T+\frac{M_T}T. \tag{3}
\]

Gradient contraction controls the boundary term and martingale variation. This is a reusable route from a mixing process to an acquired average.

For the first moment, the source's calculation leads to the target

\[
\frac{2\epsilon}{d-1}\bar b,\qquad
\bar b=\mathbb E_{\mu}b(Z), \tag{4}
\]

and a displayed error scale

\[
\frac1{\sqrt{Td}}+
\frac{\epsilon}{\sqrt{Td^3}}+
\frac{\epsilon^2}{d^2}
\]

when the gradient and its Lipschitz constant are bounded at the stated scale. In the odd planted model,
\(\|\mathbb E_{\rm data}\bar b\|\asymp d^{-(k^\star-1)/2}\).
Data concentration gives the direct recovery and warm-start regimes.

For the second moment, the target is

\[
\frac Id+\frac{\epsilon}{d}G,\qquad
G=\mathbb E_\mu[Zb(Z)^\top+b(Z)Z^\top]. \tag{5}
\]

The source gives a population eigengap for \(G\) of order \(d^{-k^\star/2}\).
Its Appendix D Frobenius estimate is

\[
\frac1{\sqrt T}+
\frac{\epsilon}{d\sqrt T}+
\frac{\epsilon^2}{d^2}. \tag{6}
\]

Comparing (6) with the spike scale
\(\epsilon d^{-(k^\star/2+1)}\) explains the appendix's extra factor of \(d\) in the time bound. A statement of the shorter main-text horizon needs a sharper kinetic estimate. Section 5 below supplies one exact Brownian component, without claiming it repairs every part of the theorem.

The paper's sample estimates are conditional on its particular boundedness, Gaussian model and concentration arguments. The proofs were read in full, but their entirety is not independently certified here.

## 4. Independent stationary construction: linear response and harmonic readouts

This provides an exact population explanation of (4)–(5), separate from the source's finite-time coupling proof.

Fix the realized dataset and write \(F=-L_n\). On the compact sphere the diffusion (1) has reversible invariant measure

\[
d\mu_\epsilon(z)=
\frac{\exp(2\epsilon F(z))}
{\mathbb E_\mu\exp(2\epsilon F(Z))}\,d\mu(z). \tag{7}
\]

For a mean-zero spherical harmonic \(H_\ell\) of degree \(\ell\geq1\), possibly vector or matrix valued, let
\(\lambda_\ell=\ell(\ell+d-2)/2\). Stationarity and
\(\mathcal L_0H_\ell=-\lambda_\ell H_\ell\) give the exact identity

\[
\mathbb E_{\mu_\epsilon}H_\ell
=\frac{\epsilon}{\lambda_\ell}
\mathbb E_{\mu_\epsilon}[b\cdot\nabla_SH_\ell]. \tag{8}
\]

Differentiating (7) at \(\epsilon=0\) gives

\[
\mathbb E_{\mu_\epsilon}H_\ell
=2\epsilon\,\mathbb E_\mu[H_\ell F]+O(\epsilon^2). \tag{9}
\]

The integration-by-parts identity
\(\mathbb E_\mu[b\cdot\nabla_SH_\ell]
=2\lambda_\ell\mathbb E_\mu[FH_\ell]\)
shows that (8) and (9) agree.

For \(H_1(z)=z\), \(\lambda_1=(d-1)/2\), and (8) becomes

\[
\mathbb E_{\mu_\epsilon}Z
=\frac{2\epsilon}{d-1}\mathbb E_{\mu_\epsilon}b(Z). \tag{10}
\]

For \(H_2(z)=zz^\top-I/d\), \(\lambda_2=d\), and

\[
\mathbb E_{\mu_\epsilon}[ZZ^\top]-I/d
=\frac{\epsilon}{d}
\mathbb E_{\mu_\epsilon}[Zb(Z)^\top+b(Z)Z^\top]. \tag{11}
\]

Thus the time accumulator selects a low-degree harmonic of the learned stationary bias. If \(F(z)=F(-z)\), symmetry makes the mean in (10) exactly zero for every \(\epsilon\), while (11) can still contain a directional spike. This gives a mathematical reason to change the readout observable instead of expecting every target to appear in the average vector.

### A transparent finite-temperature remainder

Suppose \(|F-c|\leq B\) for some scalar \(c\), and \(\|H\|\leq R\) in a fixed norm. Exponential tilting gives

\[
\frac{d^2}{d\epsilon^2}\mathbb E_{\mu_\epsilon}H
=4\left(
\mathbb E_{\mu_\epsilon}[H(F-\mathbb E_{\mu_\epsilon}F)^2]
-\mathbb E_{\mu_\epsilon}H\,\operatorname{Var}_{\mu_\epsilon}F
\right).
\]

Since \(\operatorname{Var}_{\mu_\epsilon}F\leq B^2\), its norm is at most \(8RB^2\). Therefore

\[
\left\|
\mathbb E_{\mu_\epsilon}H-\mathbb E_\mu H
-2\epsilon\operatorname{Cov}_\mu(H,F)
\right\|
\leq4RB^2\epsilon^2. \tag{12}
\]

This is a conservative, dimension-explicit response bound for any bounded smooth empirical objective on the sphere. It does not recover the sharper dimension factors in the source coupling analysis. It nevertheless supplies a usable temperature-versus-signal condition whenever the relevant harmonic covariance is known to be nonzero.

### Exact signal constants for a noiseless tensor

Take \(F(z)=(u^\top z)^k\), \(\|u\|=1\), and define

\[
a_{2j}=\mathbb E_\mu(u^\top Z)^{2j}
=\frac{(2j-1)!!}{d(d+2)\cdots(d+2j-2)}.
\]

For odd \(k\), the derivative at zero temperature is

\[
\left.\frac{d}{d\epsilon}\mathbb E_{\mu_\epsilon}Z
\right|_{\epsilon=0}=2a_{k+1}u. \tag{13}
\]

For even \(k\), rotational symmetry leaves one longitudinal and \(d-1\) equal transverse second-moment eigenvalues. The derivative of their gap at zero is

\[
\left.\frac{d}{d\epsilon}
(\lambda_\parallel-\lambda_\perp)\right|_{\epsilon=0}
=\frac{2k}{d+k}a_k. \tag{14}
\]

Indeed the longitudinal covariance is
\(a_{k+2}-a_k/d
=k(d-1)a_k/[d(d+k)]\), and the trace-zero transverse correction divides its negative by \(d-1\).

Equations (13)–(14) recover the signal scales
\(\epsilon d^{-(k+1)/2}\) and
\(\epsilon d^{-(k/2+1)}\). They describe how a very small stationary deformation can encode a direction, even while a typical state remains close to the equatorial scale.

## 5. Independent exact cost of Brownian averaging

For stationary spherical Brownian motion, a centered degree-\(\ell\) harmonic satisfies

\[
\mathbb E\langle H_\ell(\beta_s),H_\ell(\beta_t)\rangle
=e^{-\lambda_\ell|t-s|}
\mathbb E_\mu\|H_\ell\|^2.
\]

Integrating this covariance over the square \([0,T]^2\) gives the exact identity

\[
\mathbb E\left\|\frac1T\int_0^T
H_\ell(\beta_t)\,dt\right\|^2
=
\frac{2V_\ell}{\lambda_\ell^2T^2}
\left(\lambda_\ell T-1+e^{-\lambda_\ell T}\right),
\quad V_\ell=\mathbb E_\mu\|H_\ell\|^2. \tag{15}
\]

For the vector mean, \(V_1=1\) and \(\lambda_1=(d-1)/2\), giving asymptotic variance \(4/[(d-1)T]\).

For the centered matrix, the norm is Frobenius,
\(V_2=1-1/d\), and \(\lambda_2=d\). Hence

\[
\mathbb E\left\|
\frac1T\int_0^T\beta_t\beta_t^\top\,dt-\frac Id
\right\|_F^2
=
\frac{2(1-1/d)}{d^2T^2}
\left(dT-1+e^{-dT}\right)
\leq\frac{2(1-1/d)}{dT}. \tag{16}
\]

This improves the source's displayed \(T^{-1/2}\) bound for this Brownian component by \(\sqrt d\) at the root-mean-square level. Chebyshev immediately gives a failure-probability-dependent bound. It does not, by itself, yield the source's stretched-exponential probability or control the nonlinear displacement terms.

The identities apply to the stationary reference process with uniform initialization. They do not assert that the learned process has uniform invariant law. This separation is essential when using Brownian variance to analyze a small learned bias.

The accumulators in (2) require \(d\) and \(d(d+1)/2\) real numbers, respectively, plus a count or duration. A discretized update needs \(O(d)\) or \(O(d^2)\) accumulation work. Full empirical-gradient evaluation in the regression model adds \(O(nd)\) arithmetic per numerical step. The dimension reduction in sample requirements is therefore accompanied by explicit time and storage costs.

## 6. Independent construction: choose the readout without a parity oracle

The following removes parity knowledge only from final readout selection. It does not determine the diffusion's temperature, horizon, or unknown information exponent.

Form candidates from the normalized mean, when it is nonzero, and a top eigenvector of the second moment. Include both signs of each, giving at most four unit vectors. Choose the candidate with smallest empirical correlation loss on an independent validation batch.

Let \(M\leq4\) be the candidate count, \(N\) the validation size, and assume the source regression model with known \(|\sigma|\leq C\). For each fixed candidate \(v\), the centered score
\(Y\sigma(v^\top X)-\mathbb E[Y\sigma(v^\top X)]\)
is subgaussian with variance proxy

\[
K^2=C^4+C^2.
\]

To prove this, write the score as the bounded signal product plus
\(\xi\sigma(v^\top X)\). Conditional on \(X\), the latter is Gaussian with variance at most \(C^2\). Hoeffding's bound for the former contributes \(C^4\). Conditioning on the candidate-generating data preserves this calculation.

A union bound therefore gives, with probability at least \(1-\delta\),

\[
\sup_{v\in\mathcal V}|\widehat R_N(v)-R(v)|
\leq a_N
:=
K\sqrt{\frac{2\log(2M/\delta)}N}.
\]

The selected candidate \(\widehat v\) satisfies
\(R(\widehat v)\leq\min_{v\in\mathcal V}R(v)+2a_N\).
Since all candidates have unit norm and the known link is Gaussian-\(L^2\)-normalized,

\[
\mathbb E_X[
(\sigma(\widehat v^\top X)-\sigma(u^\top X))^2]
\leq
\min_{v\in\mathcal V}
\mathbb E_X[(\sigma(v^\top X)-\sigma(u^\top X))^2]
+4a_N. \tag{17}
\]

The equality behind (17) is squared predictive discrepancy \(=2R(v)\). Independent additive noise contributes zero to the population correlation.

This is a concrete selection rule under the source observation model, with a finite validation cost and a prediction-level guarantee. It does not turn the source's conjectural minibatch dynamics into a theorem. It also does not remove the known-link assumption or imply that sign is identifiable for an even link.

## 7. Material qualifications and empirical evidence

### Time, tail assumptions and exact gradients

The main even-case horizon and its appendix restatement differ by a factor of \(d\). The derivation using (6) supports the longer displayed horizon. Equation (16) supplies a promising sharper component, but a complete revised high-probability theorem has not been proved here.

Appendix H uses \(|Y_i|=O(1)\) in its tail argument, although the stated labels contain independent Gaussian noise. Bounded \(\sigma\) gives bounded conditional second moments, which supports the variance calculations. It does not give the printed deterministic bound on each \(Y_i\). A complete repair needs a separate conditional Gaussian-noise argument, or explicit truncation with bias and logarithmic costs. No repaired end-to-end rate is certified.

For the IID-entry tensor model, the scalar objective depends only on the symmetrized tensor. Its exact gradient is \(kP_\theta^\perp\operatorname{Sym}(\mathcal T)[\theta^{\otimes(k-1)}]\). The source's abbreviated \(kP_\theta^\perp\mathcal T[\theta^{\otimes(k-1)}]\) should be interpreted with that symmetrization. The stationary derivation above starts from the scalar objective and avoids this convention ambiguity.

### What the minibatch discussion does and does not establish

Section 5.2 uses a normalized batch-size-one SGD update on the fixed dataset. Its small-step Taylor argument assumes \(\eta\ll d^{-1/2}\), and its heuristic time rescaling identifies \(\epsilon=1/\eta\).

For odd \(k^\star\geq3\), the proved small-temperature regime would then require
\(\eta\gg d^{(k^\star-3)/2}\), which does not overlap with that Taylor regime. For even \(k^\star\geq2\), the corresponding condition is
\(\eta\gg d^{(k^\star-2)/2}\), with the same issue. Thus this particular heuristic does not instantiate the theorem's parameter regime.

The authors explicitly retain minibatch recovery as a conjecture and discuss data-dependent anisotropic noise. The parameter mismatch is a limit of the displayed bridge, not evidence that the conjecture is false.

### The two figures

Both figures use \(d=100\). The experiments run normalized batch-size-one SGD, with no externally added Brownian noise, for links \(h_3,h_4,h_5\). These polynomial links do not satisfy the bounded \(\sigma,\sigma',\sigma''\) assumption as written. The source suggests a polynomial-tail extension, but the experiments are not an implementation of a proved discretization theorem.

Figure 1 shows mean-readout alignment for the odd links alongside low instantaneous correlations. Its sample count is \(10d^{\lceil k^\star/2\rceil}\), so it tests the direct-average regime, not the smaller-sample warm-start corollary. Figure 2 contrasts an uninformative mean with a successful second-moment readout for \(k^\star=4\), using \(10d^2\) samples. Different learning rates are plotted.

The paper does not report uncertainty over repeated training runs, a comprehensive dimension sweep, or a matched wall-clock comparison with explicit spectral estimators. These plots support the proposed observable-selection phenomenon at the displayed settings. They do not independently establish an asymptotic minibatch sample law. No experiment was rerun.

## 8. Source-grounded use and limits

This paper adds a constructive mechanism to the [Generative Leap](DAMIAN-2025-GENERATIVE-LEAP.md) and [reused-gradient filtering](ZHANG-2026-GENERIC-MULTI-INDEX.md) readings. A prediction objective can leave a small, structured bias in a noisy learning process. Choosing and accumulating an appropriate observable turns that bias into an estimated direction.

The exact harmonic response, Brownian variance and validation selection are useful mathematical tools even when the source's full finite-time proof needs qualification. They supply an acquired average and a choice of readout, not an autonomous discovery theorem for a finite-state computation.

Any FP transfer would need an observable process with a justified invariant measure or mixing estimate, a predictive signal surviving the chosen average, a valid acquisition interface, and a deployment cost for the accumulated statistics. None is inferred from the current Gaussian example alone. No FP core definition, architecture, learning rule, experiment protocol or implementation was changed.

Mandatory Astra request 2e7a6c9 was owned by Pro-A at c3f5217 during this independent reading and was completed by Pro-A at e0296c3 before publication of this note. That response is preserved. This note is a separate ordinary reading.

## 9. Edition checksums

| Asset | SHA256 | Coverage |
|---|---|---|
| Official 34-page PDF | 59f45c2f1bc83374ba9100206df23e9d2483dce7452508b8575cf4047f6c5434 | Fully read |
| ArXiv v1 42-page PDF | f7170a89b5501e0a9043455f719b1af7b30c9969430ebb185163e1529ef470fb | Metadata and selected statements only |
| ArXiv v1 TeX archive | 0dbdb14d16bb474d8966a5f7091f0d544fff72a8dc9170e95277962386c19c91 | Targeted algorithm and theorem comparison |

Full reading includes the official paper's actual reference list and its use of those sources. Referenced predecessor papers retain their independent coverage status. No novelty claim is made for the deductions above.
