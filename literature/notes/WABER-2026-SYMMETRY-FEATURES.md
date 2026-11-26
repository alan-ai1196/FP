# Waber et al. — symmetry-aware feature acquisition and an observable prediction completion

## Edition, sources and actual coverage

Jivan Waber, Vanessa Piccolo, Yatin Dandi and Florent Krzakala, *Symmetry-Aware Feature Learning: A Polynomial Separation for Multi-Index Models*.

- [arXiv 2610.08420v1](https://arxiv.org/abs/2610.08420v1), submitted October 6, 2026 at 14:23:00 UTC.
- [Exact 71-page PDF](https://arxiv.org/pdf/2610.08420v1).
- [Exact TeX archive](https://arxiv.org/src/2610.08420v1).

Pro-D personally completed the 71-page edition on November 27, 2026, Shanghai time. Coverage comprises Sections 1–11, Appendices A–B, every active statement and proof, all three figures, acknowledgments, the AI-use statement and all 38 printed references. The complete active scientific source comprises arxiv.tex, proofs.tex and appendices.tex, 3,192 lines in total. Original PDF pages 10 and 14 cover all figures. Pages 19 and 25 were additionally inspected for two local transcription defects. There are no tables, algorithm blocks or scientific footnotes.

The checked primary record lists only v1. No separate peer-reviewed final was authenticated. The source openly discloses generative-AI assistance with mathematical statements, proof strategies and proof drafting, literature, exposition, code and figures. The authors take responsibility for the result. This remains author research, not official OpenAI or Anthropic research.

SHA256:

- PDF: 67a2b31c5c15a22aea9f0e89b549d96f1ce6ec9b5819bab39d89aad54aa6af95.
- TeX archive: b7f474e9247a04dc3413157c9e65914f4d6929cea3d9108c01b5dfe17e8ed34c.

There was no training reproduction, experiment-code audit or formal verification. Independent results below include exact orbit whitening, a deterministic prediction inequality, a held-out selection rule, FFT resource accounting and partial-augmentation covariance formulas. A small floating-point algebra check validates transform conventions, not the stochastic learning theorem. No novelty claim is made.

## 1. Problem, prior information and the compared learners

The known cyclic transformation \(\Pi\) shifts a \(d\)-vector by \(d/r\) coordinates, where \(r\mid d\). The target is

\[
y=f_*(x)=\frac1{\sqrt r}\sum_{k=0}^{r-1}
\sigma(\langle\Pi^kw_*,x\rangle),
\qquad x\sim N(0,I_d).
\tag{1}
\]

Labels are noiseless. The link \(\sigma\) is known. The teacher \(w_*\) and initial weights are independent uniform unit vectors. The asymptotic regime has \(r=d^\delta\), \(0<\delta<1/2\), along admissible divisibility sequences. Untied width satisfies \(1\le s\le d^\kappa\).

The main link class is a fixed centered polynomial

\[
\sigma(z)=\sum_{\ell=p}^P a_\ell h_\ell(z),
\qquad p\ge3,\quad a_p\ne0.
\tag{2}
\]

The \(h_\ell\) are orthonormal Gaussian Hermite polynomials. Degree and coefficients do not grow with \(d\). If \(p\) is even, the entire link must be even. The separate quadratic result assumes precisely \(\sigma=h_2=(z^2-1)/\sqrt2\), not every link with information exponent two.

The tied predictor is Equation 1 with \(w\) in place of \(w_*\). The untied predictor is \(s^{-1/2}\sum_j\sigma(\langle w^j,x\rangle)\). All use correlation loss \(-yf(x)\), tangent-space gradient steps and normalization back to the unit sphere. The augmented learner averages each untied sample loss over all \(r\) known transformations of that same observation.

For reference step \(\eta\), the actual learning rates are

\[
\eta_T=\eta,\qquad
\eta_U=\sqrt{s/r}\,\eta,\qquad
\eta_A=\sqrt{rs}\,\eta.
\tag{3}
\]

Consequently the augmented and untied learners do not use equal step sizes. Their population objectives agree before this rescaling. Their fluctuations differ.

Because correlation loss is linear in the output, each weight's gradient is independent of the other weights' values. Source Equations 39–42 establish the exact samplewise identity

\[
\nabla_{w^j}L_A(W,x,y)
=\frac1{\sqrt{rs}}\nabla L_T(w^j,x,y).
\tag{4}
\]

With Equation 3 and a shared initial weight and sample stream, an augmented weight follows exactly the tied trajectory, including normalization. This is stronger than equality of population drift. It depends on full-group averaging, the linear correlation loss and the prescribed scaling.

The symmetry is supplied. The paper does not learn the group, its action, the polynomial link or its Hermite degree.

## 2. What the source recovery theorems say

Let \(m_k(w)=\langle\Pi^kw_*,w\rangle\). For even links, signs are unidentifiable. For odd information exponent, the recovered correlation must be positive. The principal event is that some weight at some time before \(n\) reaches a fixed correlation \(\rho\in(0,1)\).

For \(\eta=d^{-p/2}(\log d)^{-A}\), with \(A\) sufficiently large, Theorems 3.2, 5.1 and 5.4 give

| Procedure | Fresh samples to fixed directional recovery |
|---|---:|
| Tied | \(\widetilde\Theta(d^{p-1})\) |
| Full-group augmented | \(\widetilde\Theta(d^{p-1})\) |
| Untied without augmentation | \(\widetilde\Theta(rd^{p-1})\) |

The lower bounds concern these specified updates and rates. They are not information-theoretic lower bounds or lower bounds for all optimizers. The upper bounds hold for any fixed untied or augmented weight, while the non-escape bound covers all polynomially many weights.

For pure \(h_2\), the recovery event instead requires one weight to place a fixed fraction of its squared norm in the entire teacher-orbit subspace. At reference rate \(d^{-1}(\log d)^{-A}\), the corresponding scales are \(\widetilde\Theta(d)\) and \(\widetilde\Theta(rd)\). Recovering one vector with substantial projection is not recovering a basis of that subspace.

With \(s\ge(1+\varepsilon)r\log r\), Corollary 3.5 gives full orbit coverage for the augmented and untied learners at their respective scales. Different directions can be recovered by different weights at different times. The theorem does not state simultaneous retention at the final iterate.

The coverage proof handles the shared sample stream carefully. Untied trajectories use a uniform high-probability recovery event and a union bound. Augmented trajectories become independent across initializations after conditioning on the teacher and complete sample stream. Cyclic equivariance then supports the conditional coupon-collector argument. Independent sample streams for different neurons are not assumed.

## 3. Proof mechanism and the stronger endpoint information

Define

\[
\phi(z)=\sum_{\ell=p}^P a_\ell^2z^\ell,\qquad
V_\sigma=\phi(1).
\tag{5}
\]

Gaussian Hermite orthogonality gives the tied population objective

\[
\Phi_T(w)=-\sum_k\phi(m_k(w)).
\tag{6}
\]

Random teacher geometry yields

\[
\mu_*=\max_{k\ne0}|\langle w_*,\Pi^kw_*\rangle|
=O\!\left(\sqrt{\log r/d}\right),
\qquad r\mu_*=o(1).
\tag{7}
\]

The largest initial relevant overlap is order \(\gamma_d=\sqrt{\log r/d}\). Its relative gap over the next competitor exceeds \((\log d)^{-2}\) with high probability. The proof couples the Gaussian overlap vector to independent coordinates using the teacher Gram square root and an infinity-norm bound.

The leading scalar drift is \(pa_p^2\eta m^{p-1}\). Two intermediate scales satisfy

\[
\alpha_d=\gamma_d(\log d)^{2/(p-2)},\qquad
\beta_d=\gamma_d(\log d)^B,\qquad B>2/(p-2).
\]

Stopped martingale, interaction, Hermite-remainder and normalization errors stay below the initial leader gap. The leader reaches \(\beta_d\) while its competitors remain \(O(\alpha_d)\). A second phase uses positive selected drift and spherical damping to reach \(\rho\) in a smaller time.

The resulting endpoint property, from Propositions 7.1–7.2 and the corresponding untied reduction, is stronger than weak recovery alone. After an analysis-only cyclic alignment and, for even links, a sign alignment,

\[
\langle w_*,w_\tau\rangle\ge\rho,\qquad
\max_{k\ne0}|\langle\Pi^kw_*,w_\tau\rangle|
\le C\alpha_d,\qquad r\alpha_d=o(1).
\tag{8}
\]

The one-step overshoot is \(o(1)\). The alignment does not require an oracle in the construction below, because cyclic shifts leave the tied predictor unchanged and an even link also removes global sign.

For \(h_2\), the proof instead follows \(R(w)=\sum_km_k(w)^2\), initially order \(r/d\). Its drift is proportional to \(R\), and stopped logarithmic growth reaches a fixed level after order \(\eta^{-1}\log(d/r)\). The directional endpoint in Equation 8 is not available from that theorem.

Two local print defects have direct resolutions from the adjacent derivations. Equation 16, page 19, inserts an undefined factor \(v\) before the interaction sum. The preceding and subsequent one-step identities require coefficient \(\eta\), without \(v\). On page 25, the sentence below Equation 25 omits \(\eta\) from the asserted small normalization scale. The very next displayed bound contains it. The used condition is \(\eta C_\sigma\sqrt d(\log d)^P=o(\beta_d)\). These corrections do not amount to independent certification of the full proof system.

## 4. Independent construction: normalize the acquired cyclic orbit

The source leaves strong recovery and prediction error as further questions. The following deterministic construction gives one way to turn the stronger endpoint in Equation 8 into a useful predictor. It modifies the output stage and is not a claim about the original final iterate's prediction loss.

### 4.1 Algebraic construction and conditioning

Write

\[
U=[w_*,\Pi w_*,\ldots,\Pi^{r-1}w_*],\qquad
B=[w,\Pi w,\ldots,\Pi^{r-1}w],
\]

and set \(G=U^\top U\), \(H=B^\top B\), \(C=U^\top B\). Assume

\[
\|G-I\|_{\rm op}\le\kappa<1,\qquad
C=\theta I+E,\qquad \|E\|_{\rm op}\le e<\theta.
\tag{9}
\]

These assumptions are deterministic. Equation 8 gives them with \(\theta\ge\rho\), \(\kappa=o(1)\), and \(e\le Cr\alpha_d=o(1)\). The cross-Gram matrix is circulant, so a common leading overlap lies on its aligned diagonal.

Projection onto \(\operatorname{col}(U)\) gives

\[
H\succeq C^\top G^{-1}C
\succeq \ell I,\qquad
\ell=\frac{(\theta-e)^2}{1+\kappa}>0.
\tag{10}
\]

The orbit can therefore be whitened:

\[
\widetilde B=BH^{-1/2},\qquad
v=BH^{-1/2}e_0.
\tag{11}
\]

Both \(H\) and its inverse square root commute with cyclic shifts of column indices. Hence

\[
\widetilde B=[v,\Pi v,\ldots,\Pi^{r-1}v],\qquad
\widetilde B^\top\widetilde B=I.
\tag{12}
\]

The entire orbit of the new unit vector is orthonormal.

This operation does not destroy the selected alignment. A circulant matrix has constant diagonal, and \(\operatorname{tr}H=r\). Convexity of \(x^{-1/2}\) yields

\[
(H^{-1/2})_{00}
=r^{-1}\operatorname{tr}H^{-1/2}\ge1.
\]

It follows that

\[
\langle w_*,v\rangle
=(CH^{-1/2})_{00}
\ge
a:=\theta-\frac{e\sqrt{1+\kappa}}{\theta-e}.
\tag{13}
\]

In particular, under Equation 8, \(a\ge\rho-o(1)\). No knowledge of \(w_*\), \(C\), the leader index or the sign is needed to compute Equation 11.

### 4.2 Deterministic prediction inequality

Use the tied predictor

\[
f_v(x)=r^{-1/2}\sum_k\sigma(\langle\Pi^kv,x\rangle).
\]

By Equation 12 and centered Hermite orthogonality,

\[
\mathbb E f_v(X)^2=V_\sigma.
\tag{14}
\]

Let \(z=U^\top v\). Then \(z_0\ge a\) and

\[
\sum_{k\ne0}z_k^2\le b:=1+\kappa-a^2.
\]

Assume \(a>0\). For every integer \(\ell\ge2\),
\(\sum_{k\ne0}|z_k|^\ell\le b^{\ell/2}\). Even powers contribute nonnegatively to the target covariance. Thus

\[
\mathbb E[f_*(X)f_v(X)]
=\sum_k\phi(z_k)
\ge \phi(a)-\sum_{\ell\ {\rm odd}}a_\ell^2 b^{\ell/2}.
\tag{15}
\]

The teacher variance obeys

\[
|\mathbb Ef_*(X)^2-V_\sigma|
\le (r-1)V_\sigma\mu_*^p.
\]

Combining these identities proves the finite deterministic bound

\[
\boxed{
\mathbb E(f_v(X)-f_*(X))^2
\le
2V_\sigma-2\phi(a)
 +2\sum_{\ell\ {\rm odd}}a_\ell^2
       (1+\kappa-a^2)^{\ell/2}
 +(r-1)V_\sigma\mu_*^p.
}
\tag{16}
\]

For an even link, the odd sum vanishes. Under the source's endpoint geometry and any fixed \(\rho\in(0,1)\),

\[
\mathbb E_X(f_v(X)-f_*(X))^2
\le
2\{V_\sigma-\phi(\rho)\}
 +2\sum_{\ell\ {\rm odd}}a_\ell^2
       (1-\rho^2)^{\ell/2}+o(1)
\tag{17}
\]

on endpoint events with probability tending to one. This is a high-probability bound on the random conditional prediction risk. The expectations in Equations 16–17 are over a fresh test input, not over failed training runs. No almost-sure limsup assertion follows merely from the source's probability \(1-o(1)\).

The right side tends to zero as \(\rho\uparrow1\). For fixed desired error, one may first choose a sufficiently high fixed recovery level, then take sufficiently large dimension. This is an iterated-limit, fixed-accuracy consequence. The source does not provide the uniform dependence on \(\rho\uparrow1\) needed to assert a sample rate for a prescribed \(\varepsilon_d\downarrow0\).

### 4.3 Why raw directional overlap is insufficient

A concrete geometry illustrates the role of normalization. Choose a unit vector \(z\) fixed by \(\Pi\) and orthogonal to the teacher orbit, and put

\[
w=\rho w_*+\sqrt{1-\rho^2}\,z.
\tag{18}
\]

Such a \(z\) exists when \(d/r>1\). The fixed subspace has dimension \(d/r\), and orthogonality to all shifted teachers imposes only one linear constraint there.

This weight has a leading overlap \(\rho\) and all competing overlaps at most \(\rho\mu_*\), satisfying the endpoint type in Equation 8. Yet

\[
\langle w,\Pi^kw\rangle
=1-\rho^2+\rho^2\langle w_*,\Pi^kw_*\rangle
\quad(k\ne0).
\]

For a pure even Hermite link, the unnormalized tied predictor has variance \(\Theta(r)\), while its target covariance stays \(\Theta(1)\). Even its best scalar readout improves squared risk by only \(\Theta(1/r)\).

This does not show that SGD visits Equation 18. It shows why the endpoint overlap statement alone does not bound the raw tied predictor's variance. Orbit whitening supplies the missing deterministic control.

## 5. An observable output rule using independent validation

The recovery time in the source depends on the unknown teacher. The preceding construction can nevertheless be used without observing that time.

Fix a target recovery level \(\rho\) and a deterministic training horizon \(N\) satisfying the source upper bound. At each iterate of one tied trajectory, or one fixed augmented weight:

1. Compute its orbit Gram spectrum.
2. If the smallest eigenvalue is at least \(\rho^2/4\), form the whitened vector in Equation 11 and retain it as a candidate for evaluation.
3. Include the zero predictor as an additional candidate.
4. Use one independent validation sample to compare candidate squared risks by median-of-means estimates, then output the candidate with smallest estimate.

The source endpoint satisfies the spectral gate for all sufficiently large dimensions by Equation 10. All candidates are functions of training observations only. The validation comparisons do not influence SGD updates. One may stream the candidates while retaining just the current best vector.

Conditional on the teacher geometry and complete training path, there are at most \(M=N+2\) candidates. Each whitened candidate has \(L^2\) norm \(\sqrt{V_\sigma}\). For sufficiently large \(d\), the teacher has squared norm at most \(2V_\sigma\). Every prediction difference is a degree-\(P\) Gaussian polynomial, so hypercontractivity gives the common loss-variance bound

\[
\mathbb E[(f_v(X)-y)^4]
\le C_\sigma,\qquad
C_\sigma=81\,3^{2P}V_\sigma^2.
\tag{19}
\]

A median-of-means estimate with block size \(O(C_\sigma/a^2)\) and \(O(\log(M/\zeta))\) blocks estimates every candidate's risk to accuracy \(a\), simultaneously with conditional probability at least \(1-\zeta\). This follows from Chebyshev's inequality for a block mean, binomial concentration of the median, and a union bound over the fixed conditional candidate list. Reusing that same validation set across candidates is permitted.

The selected candidate therefore satisfies

\[
R_{\rm selected}\le\min_{j\le M}R_j+2a.
\tag{20}
\]

For any fixed \(\varepsilon>0\), choose \(\rho<1\) so that Equation 17 is below \(\varepsilon/2\), and set \(a\le\varepsilon/4\). The added validation sample count is

\[
N_{\rm val}
=O_\sigma\!\left(\varepsilon^{-2}
\log\frac{N+2}{\zeta}\right).
\tag{21}
\]

Conditional on the source endpoint theorem, this gives squared risk at most \(\varepsilon+o(1)\) with probability at least \(1-o(1)-\zeta\). Taking \(\zeta=d^{-2}\) retains an additional sample count of order \(O_{\sigma,\varepsilon}(\log d)\) when \(N\) is polynomial in \(d\).

This is a conditional completion of the prediction interface using additional postprocessing and validation. It does not certify the source SGD theorem, prove last-iterate recovery, recover unknown symmetry, cover the pure quadratic theorem, or give a uniform diminishing-error rate.

## 6. FFT implementation and actual resources

Full-group evaluation need not materialize \(r\) shifted \(d\)-vectors for this specific cyclic action. Reshape each vector into \(r\) blocks of length \(\Delta=d/r\). Take a length-\(r\) FFT along the block index for each of the \(\Delta\) within-block coordinates.

All orbit inner products are the inverse FFT of the sum of channelwise cross spectra. If \(W_{jc}\) and \(X_{jc}\) are unnormalized block FFTs,

\[
\big(\langle\Pi^kw,x\rangle\big)_{k=0}^{r-1}
=\operatorname{IFFT}
\left(\sum_{c=1}^{\Delta}\overline{W_{\cdot c}}X_{\cdot c}\right).
\tag{22}
\]

If \(q_k=\sigma'(\langle\Pi^kw,x\rangle)\), the Euclidean feature gradient is the cyclic correlation of \(q\) with each input channel, divided by \(\sqrt r\). Its FFT implementation costs the same order. Spherical projection and normalization add \(O(d)\).

Thus one tied step, or one augmented component, costs

\[
O(d\log r+rP)=O(d\log r)
\tag{23}
\]

arithmetic operations for fixed \(P\), with \(O(d)\) working storage. A naive implementation costs \(O(rd)\). One untied component costs \(O(d)\).

Orbit whitening has an equally direct formula. For the unitary block FFT \(\widehat w_{jc}\), the eigenvalues of \(H\) are

\[
\lambda_j(H)=r\sum_c|\widehat w_{jc}|^2.
\]

Set

\[
\widehat v_{jc}
=\frac{\widehat w_{jc}}{\sqrt{\lambda_j(H)}}.
\tag{24}
\]

Each frequency block then has energy \(1/r\), and the inverse transform produces Equation 11. Conjugate symmetry preserves real vectors. This takes \(O(d\log r)\) time and \(O(d)\) storage. The eigenvalue gate in Section 5 is directly computable.

Under naive independent group evaluation, the factor-\(r\) sample advantage can be consumed by the extra work per sample for a single component. The FFT compilation changes that accounting for the stipulated cyclic action. For fixed accuracy and confidence polynomially small in \(d\), the exhaustive validation construction costs at most

\[
O\!\left(N(1+N_{\rm val})d\log r\right)
\]

operations and \(O(dN_{\rm val})\) storage, plus constant-degree link evaluation. Validation inputs can be transformed once and retained. This remains polynomial and adds logarithmic factors for fixed accuracy, but it is substantially more work than merely stopping at an unobservable overlap threshold.

These are algebraic implementation bounds, not measured runtimes or a floating-point stability theorem. The source does not present this FFT prediction completion. Adding known-symmetry postprocessing to an untied learner would change its information interface and must be disclosed in any comparison.

## 7. Independent covariance formula for partial augmentation

Fix a current weight and write \(g_k(X)=g(\Pi^kX,y)\) for its unscaled one-feature gradient on transformed observations. Let \(\bar g=r^{-1}\sum_kg_k\). Invariance gives the same mean \(\mu\) and covariance \(V\) to every \(g_k\). Let \(\bar V=\operatorname{Cov}(\bar g)\).

Choose \(q\) transformation indices independently and uniformly with replacement, independently of \(X\), and average the corresponding gradients. Conditional variance followed by total variance gives exactly

\[
\operatorname{Cov}(g^{(q)})
=\bar V+\frac1q(V-\bar V).
\tag{25}
\]

For a uniform size-\(q\) subset without replacement,

\[
\operatorname{Cov}(g^{(q)})
=\bar V+\frac{r-q}{q(r-1)}(V-\bar V).
\tag{26}
\]

Both formulas concern one fresh observation and its correlated transformations. They do not treat the transformed examples as independent new samples.

In a scalar direction with variance ratio \(\chi=V_{\rm scalar}/\bar V_{\rm scalar}\), replacement sampling reduces variance relative to one transformation by factor

\[
\frac{q}{1+(q-1)/\chi}.
\tag{27}
\]

This is a constructive budget rule for estimating a fixed mean gradient. It is not a proven interpolation of the nonlinear SGD recovery times. Extending the source's stopped dynamics to partial augmentation would require new moment and growth analysis.

## 8. Empirical scope, bounded checking and transfer boundary

Figure 1 uses the pure \(h_4\) link, dimensions 36–576, \(r=\sqrt d\), ten paired seeds, shared inputs and initialization, and reference rate \(0.1d^{-2}\). It reports median hitting times with pointwise 95% bootstrap intervals. Fitted powers are 2.86 for tied/augmented and 3.38 for untied, against reference powers 3 and 3.5. Tied and augmented curves coincide by the exact update identity.

This simulation uses the boundary exponent \(\delta=1/2\), outside the proved strict range, and omits the asymptotic logarithmic rate damping. It is an illustrative observation. Figure 2 is one population-flow trajectory at \(d=2025,r=45\), with time normalized by its own hitting time. Figure 3 is explicitly schematic. The paper conjectures extension to larger ranks, but does not prove it.

The independent transform check used \(d=15,r=5,\Delta=3\), teacher \(e_0\), and \(w=0.8e_0+0.6z\), where \(z\) is uniform on the second coordinate of all five blocks. Dense and FFT whitening agreed to \(5.6\times10^{-16}\). The orbit Gram error was below \(4.5\times10^{-16}\), orbit correlations below \(1.7\times10^{-16}\), and the feature-gradient transform error below \(4.5\times10^{-16}\). For pure \(h_4\), the exact Gaussian moment formula gave risk \(0.6728486140\), below the deterministic upper bound \(2-2(0.8)^4=1.1808\). This small algebra example is outside the asymptotic experiment protocol and tests only the independent transform identities.

The reusable positive tools are exact group-average update compilation, symmetry-preserving orbit normalization, an explicit endpoint-to-risk inequality, and a statistically valid observable selection step. The limitations remain specific: known cyclic action and link, Gaussian iid inputs, noiseless labels, correlation loss, carefully scaled spherical updates and an asymptotic random teacher. No FP architecture, core definition or learning rule was changed.
