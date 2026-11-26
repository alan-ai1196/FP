# Nelson et al. 2026 — statistical stability, structural recovery and the remaining linear gauge

Pro-D. Completed 2026-11-26, Asia/Shanghai. Independent literature note, not an FP architecture proposal.

## Edition, sources and actual coverage

Walter Nelson, Marco Fumero, Theofanis Karaletsos and Francesco Locatello, **Statistical and structural identifiability in representation learning**, ICLR 2026, 36 pages.

- [Official conference record](https://proceedings.iclr.cc/paper_files/paper/2026/hash/f67e5f99b23b108a3a6665f410034bcd-Abstract-Conference.html).
- [Official PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/f67e5f99b23b108a3a6665f410034bcd-Paper-Conference.pdf), the canonical edition for every page reference below.
- [arXiv 2603.11970v1](https://arxiv.org/abs/2603.11970v1), submitted March 12, 2026, with [PDF](https://arxiv.org/pdf/2603.11970v1) and [TeX source](https://arxiv.org/src/2603.11970v1). The inspected history lists v1. No replacement or withdrawal was identified in these records.
- Official PDF SHA256 `988b9d7f33fc8790b487619bc3383b3c820dbefadbf3d8c4c9191fbeac0e4706`. ArXiv PDF SHA256 `ffbb4f6d90888f6e0c5d06b53e46d7c595e73f9ccf4cff8454f779b62219e01a`. Source archive SHA256 `f8e7505fd992e2bea33567016d42aa95cd8cdc49fe4cb90e66bdcb744ccb0060`.

**Fully read:** all 36 official pages, main §§1–5, discussion and acknowledgments continuing onto p11, all of Appendices A.1–A.7, every displayed proof/formula, all six figures including the ten panels in A.6, seven numbered tables, the unnumbered standard-error table on p34, and all 71 printed references on pp11–17. The root reader read the complete official PDF text in continuous blocks and visually inspected 16 original pages: 6–10, 22, 24–25, 28–32, 34–36. The active TeX consists of the 1173-line main file and a 508-line notation input. The notation input and targeted main/appendix passages were read to resolve definitions, constants and provenance. This is complete PDF reading, not a claim of separately reading every source line or every cited paper.

Both PDFs have 36 pages. MuPDF extraction matches exactly on pp2–36, with only the arXiv watermark added on p1. Removing that line gives exact full-text agreement. Poppler additionally differs by one horizontal space in three formula lines on pp24/26. All six embedded image pixel hashes agree. This establishes scientific correspondence, not byte equality or a second completed-paper count.

The source package contains no experimental implementation and no experiment-repository link was found in the read manuscript. No training, code reproduction or formal proof replay was performed. No AI-assistance disclosure was identified in the read paper. Actual assistance is undetermined. Author research at ICLR is not an official OpenAI or Anthropic release.

## 1. Assessment

The useful distinction is between agreement of population-optimal representations and recovery of a separately specified generating variable. The paper also supplies a useful geometric route from **pointwise identical composite outputs** through well-conditioned invertible decoders to approximate rigid alignment, and a useful whitening perturbation bound.

Several extensions need qualifications. Most decisively, A.3.4 substitutes **linear equivalence of the penultimate layer** for the exact composite-output premise. A one-dimensional exponential-family scaling example satisfies the stated model conditions while giving positive optimal rigid-alignment error at decoder distortion zero. This refutes that application under its printed assumptions, not the exact-output geometric argument.

Additional bounded checks identify missing small-distortion and domain conditions, a sign/constant problem in the ICA perturbation argument, a dynamical-isometry boundary failure, and an incompatible metric in the binary-image example. The experiments provide useful observations about particular alignment and downstream procedures. They do not establish the full population hypotheses, and the final paper contains unresolved discrepancies between two disentanglement tables and between two descriptions of the biological evaluation split.

## 2. Mathematical objects and quantifiers

### Population minimizers and representation equivalence

For a model class and loss, let

\[
\mathcal S=\arg\min_{\theta\in\Theta}\mathbb E_P\mathcal L_\theta,
\qquad f_\theta:\mathcal X\to\mathbb R^D.
\]

Definition 1, p3, calls the representation statistically \(\varepsilon\)-near identifiable up to a group \(\mathcal H\) when

\[
\forall\theta,\theta'\in\mathcal S\quad
\exists h\in\mathcal H\quad
\operatorname*{ess\,sup}_{x\sim P}
\|f_\theta(x)-h(f_{\theta'}(x))\|_2\le\varepsilon.
\]

The paper explicitly reserves identifiability without an indicated group for **pointwise equality**. These quantifiers concern all global minimizers of population risk. They do not prove that an optimizer reaches those minimizers, that finite-sample minimizers are close to them, or that different data samples produce a particular alignment rate. The discussion acknowledges the finite-sample and optimization gaps.

The groups need careful bookkeeping. Invertible linear maps form \(GL(D)\). Euclidean rigid maps have form \(z\mapsto Qz+b\), \(Q\in O(D)\). Signed permutations form a subgroup of \(O(D)\). The printed inclusion of translations in a subgroup of invertible *linear* maps is literally incorrect. Centering removes this issue for the intended arguments. A similarity transform that also permits global scaling is a larger class than a rigid transform, which matters for Table 1.

### Structural recovery

Definition 2, p5, introduces a specific target

\[
u(x)=\arg\max_u P(x\mid u)
\]

assumed well-defined almost everywhere, and requires \(\|h\circ f_\theta-u\|_\infty\le\varepsilon\) for every population optimum. This is a deterministic maximum-likelihood target. For a noisy generative model it is not automatically the actual sampled latent, its posterior mean or its posterior distribution. Theorem 3 specializes to a noiseless invertible generator, where \(u=g^{-1}\) is unambiguous.

A.5, pp29–30, gives the useful implication from structural to statistical nearness. Its clean condition is a uniform Lipschitz bound \(\operatorname{Lip}(h^{-1})\le C\) for the transformations being used. Triangle inequality then gives pairwise error at most \(2C\delta\). Rigid transformations have \(C=1\), including translations. At \(\delta=0\), group inversion and composition suffice. An operator norm for a general nonlinear or translated map should not replace the inverse Lipschitz condition without explanation.

## 3. Exact-output geometric rigidity, with the required conditions retained

Theorem 1 and A.3.2, pp4 and21–23, study encoders \(f_\theta\) and decoders \(g_\theta\). The intended premise is

\[
g_\theta\circ f_\theta
=g_{\theta'}\circ f_{\theta'}\quad P\text{-a.e.}
\]

for any two population optima. The decoders are smooth and injective onto the relevant common image and locally \(B\)-bi-Lipschitz, \(B=1+L\). The latent supports must be convex. Boundedness is used in the proof and the near-isometry lemma, even though the formal theorem's short statement does not enumerate a uniform compact-support condition.

The proof constructs

\[
T=g_{\theta'}^{-1}\circ g_\theta,
\qquad T\circ f_\theta=f_{\theta'}.
\]

Locally, \(T\) and its inverse have derivative norm at most \(B^2\). Integrating the upper derivative bound for \(T\) on a convex source and for \(T^{-1}\) on a convex target gives the **global** two-sided bound. This use of both latent domains is distinct from incorrectly integrating a derivative lower bound through a curved observation-space image.

If the source diameter is \(\Delta\), write \(\rho=B^2-1=2L+L^2\). Then \(T\) is a \(\rho\Delta\)-near-isometry. The cited bounded-set approximation result gives

\[
\inf_{U\in\operatorname{Isom}(\mathbb R^D)}
\sup_{z\in Z}\|T(z)-U(z)\|
\le c_D\sqrt\rho\,\Delta
\tag{1}
\]

in its small-distortion regime.

### The imported theorem has a missing restriction

This was checked by a narrow historical dependency lookup, not by a new full reading. Väisälä's [2002 survey, Theorem 4.1 on printed p9](https://arxiv.org/pdf/math/0201098), explicitly citing Alestalo–Trotsenko–Väisälä 2001, Theorem 2.2, requires the dimensionless near-isometry parameter to be at most one. The [original publisher abstract](https://link.springer.com/article/10.1007/BF02773375) gives the same restriction after normalizing the domain diameter to one. Nelson Lemma A.4 omits it.

The restriction cannot simply disappear when \(\Delta\) is only the **source** diameter. On \(Z=[0,1]\), let \(T_M(x)=Mx\), \(M>1\). It is an \((M-1)\)-near-isometry, but its best rigid approximation error is \((M-1)/2\), which cannot be bounded by \(c_1\sqrt{M-1}\) for all \(M\).

**Conditional repair, independently stated:** with \(\rho\le1\), retain (1). If both latent supports instead have a common diameter bound \(\Delta_*\), a translation aligning one corresponding pair gives error at most \(2\Delta_*\). Thus for \(\rho>1\) a trivial bound combined with the small-distortion result yields \(\max(c_D,2)\sqrt\rho\,\Delta_*\). This repair changes the diameter convention and makes the uniform support assumption explicit. It does not justify the paper's claim that the proof's diameter of \(f_\theta(\mathcal X)\) is automatically independent of the model.

At zero distortion, under exact outputs and the geometric premises, rigid identifiability is the appropriate conclusion. The counterexample in the next section leaves the exact-output premise false and therefore does not refute this restricted mechanism.

### Masked autoencoders

A.3.3, pp23–24, uses squared loss on the **whole reconstruction**. On the masked-input distribution its unconstrained population optimum is the conditional mean \(\mathbb E[X\mid\widetilde X]\). The model must contain that function. Continuity of the chosen version, full support on the masked-input space and sequential density of that space in the union with unmasked inputs are explicit additional assumptions used to extend uniqueness.

This is not a theorem for arbitrary masking distributions. The remark about evaluating only masked coordinates preserves, at most, an inclusion of minimizers under appropriate conditioning. It does not by itself prove that the smaller loss has the same unique full-output minimizer. Unscored coordinates and the information carried by the mask require separate treatment before invoking Theorem 1.

## 4. A precise counterexample to the GPT/supervised application

A.3.1, pp20–21, builds on exponential-family linear identifiability. Under a unique and realizable pointwise KL projection and suitable sufficient-statistic diversity, identical optimal conditional distributions yield **linear equivalence** of natural-parameter representations. A.3.4, p24, then invokes Theorem 1 for earlier layers from this linear equivalence alone.

If the penultimate outputs instead satisfy

\[
g_{\theta'}f_{\theta'}=A\,g_\theta f_\theta,
\]

the correct stitching map is \(g_{\theta'}^{-1}A g_\theta\). Its distortion depends on \(A\). Omitting \(A\) is a substantive gap.

### Continuous-label construction, avoiding the source's sampling ambiguity

Let \(X\sim\operatorname{Unif}[-1,1]\), \(a\in[1,2]\), and define a positive conditional density on \(Y\in[-1,1]\), relative to Lebesgue measure, by

\[
B(x)=\log\int_{-1}^1 e^{xy}\,dy,
\qquad p(y\mid x)=e^{xy-B(x)}.
\]

Choose

\[
f_a(x)=ax,
\quad g_a(z)=z,
\quad\eta_a(x)=ax,
\quad t_a(y)=y/a,
\quad A_a(x)=B(x).
\]

Then

\[
q_a(y\mid x)
=\exp\{\eta_a(x)t_a(y)-A_a(x)\}
=p(y\mid x)
\]

for every \(a\). All losses are pointwise identical and all parameters are population optima. Each \(f_a\) has compact convex support \([-a,a]\), uniformly bounded over the parameter family. Every \(g_a\) is a smooth global 1-bi-Lipschitz diffeomorphism, so the application's \(L\) is zero.

For each fixed sufficient statistic \(t_a\), the natural-parameter family is

\[
Q^{(a)}_\kappa(y)=\exp\{(\kappa/a)y-B(\kappa/a)\}.
\]

Strict positivity gives \(B''(x)=\operatorname{Var}(Y\mid X=x)>0\). The unique KL projection is therefore \(\kappa^*_a(x)=ax\), represented exactly by \(\eta_a\). Definition A.4's fixed-\(t_1\) interpretation is also satisfied at \(a=1\). It does not require all parameter settings to share a fixed output-head coordinate system. The continuous label marginal has positive density. For \(D=1\) and fixed \(y_0=0\), \(t_a(Y)-t_a(0)\ne0\) almost surely, so even the stronger literal one-draw reading of diversity is satisfied.

Nevertheless, for a one-dimensional rigid map \(U(z)=sz+b\), \(s\in\{-1,1\}\),

\[
\begin{aligned}
\inf_U\|f_{a_1}-U\circ f_{a_2}\|_{L^\infty(P_X)}
&=\inf_{s,b}\bigl(|a_1-sa_2|+|b|\bigr)\\
&=|a_1-a_2|.
\end{aligned}
\]

Taking \(a_1=1,a_2=2\) gives error **one**, while the claimed application of Theorem 1 at \(L=0\) gives zero. This is an exact finite-dimensional counterexample to A.3.4 under its stated model assumptions.

For a familiar classification version, use \(Y\in\{0,1\}\), \(P(Y=1\mid x)=\sigma(x)\), and \(B(x)=\log(1+e^x)\). The same construction works under the intended full-affine-span or positive-covariance interpretation of label diversity. All categories have positive conditional probability. The scale of the representation is canceled by the classification head.

Possible repairs include a fixed identified head, an explicit orthogonal restriction on the surviving penultimate gauge, or distortion bounds for the **whole gauge-adjusted stitching map**. Whitening the penultimate layer does not on its own show that the original intermediate-to-penultimate decoder keeps the old constant. These are mathematical conditions, not recommendations for FP architecture.

### A.1's covariance argument is weaker than the printed sampling claim

Positive definite covariance implies full affine support, not that any fixed batch of \(D\) draws yields linearly independent differences almost surely. If \(t(Y)\) is uniform on \(\{0,e_1,e_2\}\), its covariance is

\[
\frac19\begin{pmatrix}2&-1\\-1&2\end{pmatrix}\succ0,
\]

but two draws coincide with probability \(1/3\). This directly contradicts the corresponding sentence in the proof of Lemma A.1, p20. The usual existence-of-diverse-labels interpretation can be retained. The continuous counterexample above does not depend on this issue.

## 5. Whitening and ICA: a conditional stability tool

### The whitening bound is useful

Lemma A.5, p25, assumes centered paired vectors \(X,X'\), both bounded in norm by \(a\), with \(\|X-X'\|\le\varepsilon\) almost surely and covariance eigenvalues at least \(\lambda>0\). For symmetric positive definite whiteners,

\[
\|\Sigma'^{-1/2}X'-\Sigma^{-1/2}X\|
\le\lambda^{-1/2}(1+a^2/\lambda)\varepsilon.
\tag{2}
\]

The proof controls \(\|\Sigma-\Sigma'\|\le2a\varepsilon\), then the inverse-square-root perturbation, then separates the change of the matrix from the change of the vector. This is a well-conditioned, bounded-support statement. It becomes uninformative as the covariance approaches singularity.

For exact centered linear equivalence \(X=AX'\), whitening leaves an orthogonal map. For approximate equivalence, a safe consequence of (2) avoids ambiguity about singular values in Lemma A.6. Let

\[
\|X-AX'\|\le\varepsilon,
\quad\|X\|,\|X'\|\le a,
\quad\lambda_{\min}(\Sigma),\lambda_{\min}(\Sigma')\ge\lambda,
\]

\[
s=\sigma_{\min}(A)>0,
\quad S=\sigma_{\max}(A),
\quad m=\lambda\min(1,s^2),
\quad R=a\max(1,S).
\]

Set \(\Sigma_A=A\Sigma'A^\top\) and \(U=\Sigma_A^{-1/2}A\Sigma'^{1/2}\). Direct multiplication gives \(UU^\top=I\), and (2) applied to \(X,AX'\) gives

\[
\|\Sigma^{-1/2}X-U\Sigma'^{-1/2}X'\|
\le C_w\varepsilon,
\qquad C_w=m^{-1/2}(1+R^2/m).
\tag{3}
\]

This is an independent conservative repair, not the paper's printed constant. The covariance transformation uses the **square** of the smallest singular value. The paper calls its \(\lambda_A\) a singular value but its proof substitutes it as a covariance-scale lower bound without that square or the minimum with the original covariance bound. Choice of an arbitrary whitener also cannot be combined with (2) without choosing the consistent orthogonal factor. Equation (3) states those choices explicitly. If noncentered near equivalence is first centered, the perturbation can grow by a factor of two and must be charged.

### What the ICA step actually assumes

A.3.5, pp24–28, assumes more than convergence of an ICA program. It requires bounded representations, a uniform covariance spectral floor, bounded linear alignment condition numbers, a smooth contrast with controlled derivatives, isolated well-conditioned stationary branches, and no residual ambiguity among relevant optima beyond signed permutations. The last condition already supplies the required statistical uniqueness of the ICA problem. The paper explicitly does not claim a new general ICA identifiability theorem.

Lemma A.8 uses the implicit function theorem to continue a stationary point under a sufficiently small paired data perturbation. Its displayed bound, writing \(a_w\) for a radius in the **whitened** coordinates and \(b\) for perturbation size, is

\[
\|Q_b(x+e)-Q_0x\|
\le b+\frac{[L_2(a_w+b)+\sqrt D L_1]a_wb}{\mu}.
\tag{4}
\]

The cross-derivative of the contrast gradient contributes \(1/N\) per observation. Aggregation cancels the \(\sqrt N\) norm of the stacked perturbation, explaining why this deterministic perturbation bound need not grow with sample count. It is not a statistical generalization or sample-complexity rate.

Three points prevent treating the printed Theorem 2 constants as certified.

1. The objective is maximized, but the stated Riemannian Hessian is bounded **below by positive** \(\mu\). At a nondegenerate maximum on a positive-dimensional tangent space the Hessian has the opposite sign. A usable condition is \(-\operatorname{Hess}\mathcal J\succeq\mu I\), or a bound on the inverse Hessian with stationary-branch and optimum-selection assumptions.
2. The \(+b\) in Lemma A.8 disappears when its bound is substituted into Theorem 2 on p28. The source and original PDF agree on this omission. With \(b=C_w\varepsilon\), the direct algebraic consequence of (4) has a linear coefficient at least
   \[
   K=C_w\left[1+\frac{a_w(L_2a_w+\sqrt D L_1)}\mu\right],
   \qquad K'=\frac{L_2a_wC_w^2}\mu.
   \]
   The printed \(K\) lacks the first \(C_w\). Also, an unwhitened diameter cannot be used as \(a_w\) without accounting for whitening.
3. The implicit function theorem supplies a local continuation, not arbitrary-perturbation stability, convergence of FastICA to that branch, or an automatic \(N\to\infty\) theorem. A uniform continuation neighborhood, spectral gap and appropriate convergence of empirical objectives are needed to make that limit rigorous. Permutation/sign invariance also requires the contrast to have those symmetries, as in the usual even contrasts.

Equations (3)–(4) preserve a conditional \(O(\varepsilon)+O(\varepsilon^2)\) mechanism under explicit stable-branch assumptions. They do not independently certify every differential-geometric step or every original constant. A Gaussian or otherwise rotationally degenerate distribution cannot be handled by merely saying that ICA converged, because the required isolated-optimum condition fails.

## 6. Structural recovery and dynamical-isometry boundaries

### Structural theorem

A.3.6, pp28–29, additionally assumes independent non-Gaussian **zero-mean unit-variance** true factors, an injective smooth locally bi-Lipschitz generator, a sufficiently rich model containing the true inverse, perfect reconstruction, and the conditioning/ICA assumptions above. The same stitching argument compares a learned encoder with the true inverse. The unit-variance convention removes the usual per-component scale ambiguity. Exact reconstruction and the true generator's membership/geometry are substantive assumptions, not consequences of predictive loss minimization.

The argument also inherits the support and stable-ICA qualifications in §§3 and5 of this note. It is not a result for arbitrary hidden variables, noisy dynamics, changing state dimension, or representations whose decoder has collapsed directions.

### A.4 does not establish the claimed implication at all printed dimensions and endpoints

The proposition on p29 bounds only \(\min(D,N)\) singular values of the Jacobian of \(f:\mathbb R^D\to\mathbb R^N\) in \([1-\eta,1+\eta]\), then claims local bi-Lipschitz constant \((1+\eta)/(1-\eta)\).

- For \(D=2,N=1\), \(f(x,y)=x\) has its only listed singular value equal to one but is not locally injective.
- Even with full column rank, \(f(t)=(\cos t,\sin t)\) has derivative norm one, while \(\|f(t+h)-f(t)\|=2|\sin(h/2)|<|h|\). Thus at \(\eta=0\) it is not locally 1-bi-Lipschitz in the ambient Euclidean chord metric.

The proof's attempted integration of a lower derivative bound is invalid because different derivative vectors can cancel. A bounded **upper** derivative can be integrated directly.

**Local repair:** assume \(C^1\), \(N\ge D\), full column rank, and \(0<\eta<1\). Around a point \(x_0\), choose a convex neighborhood where \(\|Df(x)-Df(x_0)\|\le\zeta\). Then

\[
(1-\eta-\zeta)\|x-y\|
\le\|f(x)-f(y)\|
\le(1+\eta)\|x-y\|.
\]

Taking \(\zeta<\eta(1-\eta)/(1+\eta)\) recovers the stated larger local constant. At \(\eta=0\), every constant strictly greater than one is locally obtainable, but exact constant one does not follow. This local repair does not create a global lower bound without additional geometry.

## 7. The binary-square example changes the metric

In §3.3.1, pp6–7, fix a square half-side \(r>0\) and position \(p\), with all permitted squares inside the frame. The original map is

\[
F(p)(x,y)=\mathbf1_{\{|x-p|\le r,\ |y|\le r\}}
\in L^2([-1,1]^2).
\]

For \(0<|t|\le2r\), the area of the symmetric difference is exactly \(4r|t|\). Consequently,

\[
\|F(p+t)-F(p)\|_{L^2}^2=4r|t|,
\qquad
\left\|\frac{F(p+t)-F(p)}t\right\|_{L^2}
=2\sqrt{r/|t|}\longrightarrow\infty.
\]

The raw map has neither an \(L^2\)-valued derivative nor a finite local \(L^2\) Lipschitz constant. Its boundary distributions are not \(L^2\) functions. An equal partition of a nonzero position interval of length \(d\) yields a curve-length sum \(2\sqrt{rdn}\), diverging with the number of pieces. The original image curve therefore cannot have the finite ambient-\(L^2\) arc length asserted in the informal calculation.

**The appendix recognizes part of this issue.** A.6, p30, first mollifies with a Gaussian, then renormalizes a limiting geodesic distance. It explicitly states that the resulting metric is not inherited from \(L^2\). The correct criticism is the unestablished transition from this new metric to the original model's hypotheses, not that the authors never considered smoothing.

There is also a concrete norm-versus-squared-norm error. After displaying \(\|F'_\sigma\|_2^2\) with leading term \(2r/(\sqrt\pi\sigma)\), p30 uses that same coefficient as a curve-length speed. Length uses \(\|F'_\sigma\|_2\), with a square root. For smoothing only in the horizontal direction on the whole plane, the exact calculation is

\[
\|F'_\sigma\|_2^2
=\frac{2r}{\sqrt\pi\sigma}
\left(1-e^{-r^2/\sigma^2}\right).
\]

The displayed derivative retaining an unsmoothed vertical indicator corresponds to that one-direction smoothing. A genuinely isotropic two-dimensional convolution also smooths the vertical factor. A fixed finite frame introduces a further boundary condition for exact translation-invariant speeds.

Two mathematically honest alternatives are available, neither established as the original model by the paper. In the \(L^1\) metric, the unsmoothed images obey \(\|F(p+t)-F(p)\|_1=4r|t|\) locally, which is a metric statement rather than an \(L^2\) differentiability result. For a fixed smooth template \(\psi\in H^1(\mathbb R^2)\), \(F(p)=\psi(\cdot-p,\cdot)\) is differentiable with constant speed \(\|\partial_x\psi\|_2\). This controls arc length and infinitesimal chords, not exact finite chord equality. Taking the smoothing scale to zero and renormalizing length changes the geometry again.

For the varying-radius example, main-text \(r\in(0,R]\) is not compact and has no positive lower radius. A.6 instead introduces \(R_0\le r\le R\). Any claimed uniform lower metric bound depends on \(R_0>0\). The full two-dimensional heuristic metric and coordinate reparameterization were read but not independently certified.

## 8. Experimental evidence and its actual controls

### MNIST intervention

The authors vary the LeakyReLU leak \(\alpha\) in orthogonally parameterized autoencoders, with a two-dimensional bottleneck. A.7.1 describes 60 full-data configurations and 180 digit-specific configurations, with 11/60 and5/180 removed using a reconstruction-error threshold based on the reference leak value0.9. This filtering conditions the displayed relationship on convergence/reconstruction quality.

Representations are measured on 1000 sampled examples and Jacobian action on ten sampled directions. The paper itself says that a mean local estimate is not the global bound needed by Theorem 1. Even the maximum over those finite samples is not a certified uniform bound. The printed reciprocal term uses the reciprocal of the Jacobian norm rather than explicitly the smallest singular value. The plots show a relationship between estimated conditioning and **average** fitted alignment error, not the essential-supremum population theorem. At \(\alpha=0\), an inverse bound based on \(\alpha^{-3}\) is unavailable. The derivative assumptions also require care at piecewise-linear kinks.

Figures2 and A.4 show the reported trend, and A.6 supplies ten digit-specific panels. A.5 illustrates a tradeoff with reconstruction. Several captions mix the directions \(\alpha\to0\) and \(\alpha\to1\), and \(L\) with \(1+L\). These do not replace the quantitative conditions in the theorem.

### Off-the-shelf alignment is in-sample

A.7.2, p33, explicitly says that all reported alignment statistics are in-sample on training data. The so-called rigid comparator uses Procrustes **with a fitted global scale**. Linear alignment uses unconstrained least squares. FastICA retains all components, and signed permutation matching uses paired representations. Thus the ICA rotation itself is unsupervised, but the final cross-model comparison uses paired data.

| Model pair, Table1 | Permutation | Similarity transform | Linear | ICA |
|---|---:|---:|---:|---:|
| Pythia160M seeds | .219 | .150 | .131 | .202 |
| MAE implementations | .197 | .109 | .036 | .145 |
| CheXpert small/base | .218 | .104 | .048 | .175 |
| ResNet18 instances | .382 | .206 | .175 | .312 |

The reported ICA efficiencies25%,59%,38%,40% are fractions of the permutation-to-similarity improvement, not improvements over the supervised similarity fit. The cross-size example is not a pair satisfying the same fixed-dimensional architecture assumptions. These results show partial empirical alignment. They do not demonstrate exact population rigidity or uniform out-of-sample alignment.

### Disentanglement uses label-based selection and violates a key theoretical premise

The four datasets are Shapes3D, MPI3D, Falcor3D and Isaac3D. The model-selection procedure uses ground-truth modularity, averages three retrainings per configuration and filters on reconstruction, as stated in A.7.3. Other methods' numbers are quoted from Hsu et al., generally over five seeds. Only AE and AE+ICA are reproduced here. This is not an equally rerun comparison or a label-free selection procedure.

The latent dimension is twice the number of generating sources. The appendix states that the representation is rank deficient and therefore runs FastICA **without whitening**, retaining every coordinate. That experiment does not instantiate Theorem 2's full-rank whitening assumptions. Similar decoder singular values on active directions do not restore the missing covariance floor on inactive directions.

**Unresolved final-source discrepancy:** p33 describes Table5 as an augmented version of Table2, but central values differ materially. For AE+ICA:

| Dataset | Table2 p8, InfoM/InfoE/InfoC | Table5 p35, central values |
|---|---|---|
| Shapes3D | .79/.99/.52 | .78/1.00/.42 |
| MPI3D | .44/.66/.31 | .44/.66/.31 |
| Falcor3D | .71/.83/.33 | .68/.75/.37 |
| Isaac3D | .64/.82/.43 | .64/.80/.34 |

Both PDF page images and source tables confirm these numbers. Table2's aggregate .65/.83/.40 corresponds to its own dataset rows. Averaging Table5's listed central values gives approximately .64/.80/.36. Some differences exceed rounding. The text provides no resolution, so neither table is silently substituted for the other. Table5 also includes discrete models such as QLAE with higher modularity on several datasets. A broad all-methods state-of-the-art claim is not established by the selected continuous-baseline comparison. No raw logs were supplied in the source package or reproduced here.

### Cell imaging shows downstream classifier behavior, with an unresolved split description

The mathematical motivation is source separation, not a biological mechanism claim. OpenPhenom embeddings from Rxrx3-core are transformed in four ways: raw, PCA whitening, whitening+ICA, and whitening+random rotation. LightGBM then classifies perturbation versus shared controls. The six genes include16 guides in total and share22062 controls. Whitening and ICA are fit on about222000 patches obtained across images before the downstream plate split as described. This is an unsupervised transductive preprocessing step. It is not a pipeline whose complete representation transform is learned only from training plates.

The reported average AUROCs improve under PCA+ICA relative to raw embeddings, for example .663 to.709 for CYP11B1 and.803 to.815 for PLK1. The p34 table supplies standard errors over folds/guides, not a paired confidence interval for every contrast. The whitening-only and random-rotation controls are useful. Shared controls and overlapping folds should not be treated as independent biological replications.

Two source conflicts remain. Main §4.4, p10, describes training on80% of plates and holding out20%. A.7.4, p34, instead describes training a separate model on **one** plate and evaluating all remaining plates. Main p10 says a patch is randomly sampled per image, whereas p33 specifies the top-left patch of the first channel. The source does not reconcile these protocols. The main and augmented biological tables do agree on their displayed means, but the exact evaluation procedure cannot be certified from the conflicting descriptions.

Feature-use sparsity and the concentration statistic reflect the fitted axis-aligned classifier. Tables4/7 give concentration .386/.372/.334 for ICA at top25%/33%/50%, compared with lower values for the other rotations. These statistics show that the chosen coordinates concentrate classifier usefulness under the reported evaluation. They do not prove that all technical confounders were separated from biological causes or that the true generative coordinates were recovered. The paper does not measure the required true-factor independence, decoder geometry or perfect reconstruction in this setting.

## 9. Retained tools, limits and relation to prior readings

Retain the distinction between population equivalence and a specified structural target, the exact-output stitching construction under explicit convex-support/conditioning assumptions, the stable whitening estimate, and the inverse-Lipschitz structural-to-statistical implication. Treat ICA as a conditional stable-optimization interface whose uniqueness and curvature must be supplied.

The one-dimensional scale counterexample supplies negative evidence against deriving a stronger symmetry class merely from equal predictive distributions. It is separate from the rare-log-tail and unrecoverable-concept issues in [Liu et al.](LIU-2026-PREDICTION-CONCEPT-IDENTIFIABILITY.md), and from the rank/leakage asymptotics in [Tinati–Tu](TINATI-TU-2026-TWO-STAGE-ASYMPTOTICS.md). None of these findings implies that learned representations are useless or that the reported empirical improvements are impossible.

No claim of an FP transfer is made. The paper assumes fixed representation dimension, suitable population optima, a controlled decoder geometry and, for structural recovery, an invertible true generator. It does not supply autonomous state discovery, identifiable state cardinality, finite installed-bit accounting, learning from dependent histories or a generalization theorem for a learned transition mechanism. Those objects require their own assumptions and evidence.

The bounded independent work here consists of the scale-family counterexample, a direct check of the omitted near-isometry range, whitening/perturbation bookkeeping, projection/circle examples and an exact binary-image distance calculation. There was no exhaustive counterexample search, broad proof certification or experiment replay. Historical sources were consulted only for the named near-isometry dependency. All remaining cited works retain their pre-existing reading status.
