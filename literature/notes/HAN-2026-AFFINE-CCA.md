# Han, Matthes and Shen — spectral identifiability and conditional removal of acquired features

## Edition and actual coverage

**Primary edition.** Zhiwei Han, Stefan Matthes and Hao Shen, *Provable Affine Identifiability of Nonlinear CCA under Latent Distributional Priors*, AISTATS 2026, PMLR 300:3835–3843.

- [Official record and bibliography](https://proceedings.mlr.press/v300/han26b.html).
- [Official PDF, 38 physical pages including references, checklist and supplement](https://raw.githubusercontent.com/mlresearch/v300/main/assets/han26b/han26b.pdf).
- [OpenReview record](https://openreview.net/forum?id=plbSNDbYkb).
- [arXiv 2510.04758v3](https://arxiv.org/abs/2510.04758v3), July 8, 2026 at 10:08:32 UTC, 36 pages.
- [Complete v3 TeX](https://arxiv.org/src/2510.04758v3).
- [Author code repository, linked but not audited](https://github.com/ZhiweiHan9277/AISTATS2026_Provable_Affine_Identifiability).

Pro-D personally read all 38 official pages on November 27, 2026, Shanghai time. Coverage includes all five main sections, references, checklist, Appendices A–H, every mathematical statement and proof, all six figures and five tables. All figure/table-bearing PDF pages, 7–9 and 38, were visually inspected.

The 36-page arXivv3 received metadata, abstract, empirical-consistency assumptions and the corresponding orbit-consistency proof-step comparison in its active TeX. Its supplement starts two pages earlier because the official edition includes a two-page checklist. Extracted texts are not identical and full edition equivalence was not established. Earlier v1, October 6, 2025, and v2, May 28, 2026, were metadata-only history checks.

SHA256:

- Official PDF: b061b4261b8435f4aa34feefbb344d2fba7b1a218be6a02e47cbb4796eb48d84.
- arXivv3 PDF: 4fde240a57a39f87af51dc8fdf03f2f6c6bdc7de5cf50cb8510469c76ef26577.
- arXivv3 TeX archive: ec7acd989a0375f360d2c47e81db5e052d412e0013351bdafff0a75658bc20be.

There was no training reproduction, code audit or formal verification. Independent results below are analytic deductions from the source's operator expansion. No novelty claim is made. No explicit AI-assistance disclosure was found in the read manuscript. Actual use is undetermined.

## 1. What the source establishes

The useful core is a precise answer to when a correlation objective recovers latent coordinates, rather than merely selecting highly correlated functions of them.

Two views have the form

\[
X=g(S),\qquad X'=g'(S'),
\]

with injective Borel generators on standard Borel spaces. In the principal theorem, the latent pair is jointly Gaussian with nonsingular marginal covariances. Let its canonical correlations be

\[
1>\rho_1\ge\cdots\ge\rho_d>0.
\]

The output dimension equals the latent dimension, \(d_Z=d_S=d\). Candidate encoders are centered and population-whitened. Their base classes are assumed dense in the relevant \(L^2\) spaces, and their whitened classes are closed under output rotations.

For whitened output vectors \(H,H'\), the objective is

\[
J(H,H')=\|\mathbb E[HH'^\top]\|_*.
\tag{1}
\]

Theorem 1 assumes the strict first-order dominance condition

\[
\Delta:=\rho_d-\rho_1^2>0.
\tag{2}
\]

Every population maximizer then recovers the marginally whitened latent vectors up to separate orthogonal transformations. Before output whitening, this is recovery up to invertible affine maps. It is not componentwise or permutation identification.

The generator change of variables is not a learned inversion algorithm. Proposition 1 shows that composition with an injective measurable generator preserves the relevant moments and \(L^2\) norms. Measurable inverse and density arguments then make the source-space optimization equivalent in supremum value. Attainment of a maximizer is an additional issue for a restricted representable class.

The theorem is a population characterization of global maximizers. It does not prove that gradient training finds them, that the latent dimension is learned, or that an arbitrary pair of natural views has the required latent law.

## 2. The spectral mechanism

Use standard Gaussian canonical coordinates \(U,V\), with

\[
\operatorname{Cov}(U)=\operatorname{Cov}(V)=I,\qquad
\operatorname{Cov}(U,V)=\operatorname{diag}(\rho_1,\ldots,\rho_d).
\]

Coordinate pairs are independent across dimensions. In normalized probabilists' Hermite notation, the source's Hermite–Mehler calculation gives

\[
\mathbb E[h_\alpha(U)h_\beta(V)]
=\mathbf 1_{\alpha=\beta}\rho^\alpha,
\qquad
\rho^\alpha=\prod_i\rho_i^{\alpha_i}.
\tag{3}
\]

The source uses an equivalent physicists' Hermite convention with coordinates divided by \(\sqrt2\). These conventions must not be mixed.

Expand centered whitened outputs as

\[
H=A\Phi(U),\qquad H'=B\Phi(V),\qquad
AA^\top=BB^\top=I,
\]

where \(\Phi\) contains every nonconstant normalized Hermite function. Equation (1) becomes

\[
J=\|A D B^\top\|_*,
\qquad D=\operatorname{diag}(\rho^\alpha:\alpha\ne0).
\tag{4}
\]

Source Lemma 3 is a diagonal selection inequality: the largest achievable value with \(m\) output coordinates is the sum of the \(m\) largest diagonal entries of \(D\). A strict gap after the \(m\)-th entry forces every optimizer to use exactly that leading function subspace.

Under (2), all degree-two and higher entries are at most \(\rho_1^2<\rho_d\). Thus the top \(d\) modes are exactly the linear coordinates.

### What happens without the gap

The source already supplies the example \(\rho_1=.9,\rho_2=.5\). Its leading seven modes have correlations

\[
.9,\ .81,\ .729,\ .6561,\ .59049,\ .531441,\ .5.
\]

At output dimension two, the optimal functions are the first and second normalized Hermite functions of the first coordinate. The weak second latent coordinate is omitted. At dimension seven it enters.

The higher functions here are centered orthogonal Hermite polynomials, not raw powers. For example the second mode is \((U_1^2-1)/\sqrt2\). The source's raw-power notation in this illustration is shorthand for those orthogonal modes.

This failure of affine recovery is fully consistent with optimal cross-view correlation. A representation objective can prefer nonlinear functions of a strong predictive factor over a weak independent factor.

## 3. Independent quantitative recovery and prediction bounds

The source proves exact maximizer identification. Its diagonal-selection proof also yields a useful finite-error inequality.

Let the diagonal entries in (4) be sorted as \(\lambda_1\ge\lambda_2\ge\cdots\ge0\), let \(m\) outputs be whitened, and suppose

\[
g=\lambda_m-\lambda_{m+1}>0,\qquad
\eta=\sum_{i=1}^m\lambda_i-\|ADB^\top\|_*\ge0.
\]

Write \(A=[A_1\ A_\perp]\), with the first block covering the leading \(m\) modes, and similarly for \(B\). Set

\[
t_A=\|A_\perp\|_F^2,\qquad t_B=\|B_\perp\|_F^2.
\]

The weighted-column estimate in source Lemma 3 gives

\[
\|ADB^\top\|_*
\le\frac12\sum_j\lambda_j\|a_j\|^2
+\frac12\sum_j\lambda_j\|b_j\|^2.
\]

Because every column squared norm lies in \([0,1]\), each row system has total squared mass \(m\), and mass outside the leading block loses at least \(g\) per unit,

\[
t_A+t_B\le\frac{2\eta}{g}.
\tag{5}
\]

If \(s_i\in[0,1]\) are the singular values of \(A_1\), orthogonal Procrustes gives

\[
\min_{Q\in O(m)}\|A-[Q\ 0]\|_F^2
=2\sum_i(1-s_i)
\le2\sum_i(1-s_i^2)=2t_A.
\]

Consequently, if \(\Phi_m,\Psi_m\) denote the leading orthonormal function vectors,

\[
\inf_{Q,Q'\in O(m)}
\left[
\mathbb E\|H-Q\Phi_m\|^2+
\mathbb E\|H'-Q'\Psi_m\|^2
\right]
\le\frac{4\eta}{g}.
\tag{6}
\]

For the affine-recovery theorem, \(m=d\), \(g=\Delta\), and these leading vectors are the Gaussian canonical coordinates.

This is also a constructive completion of the orbit-separation step in Appendix D.5. That proof invokes a positive separation \(\kappa(a)\) away from the maximizing orbit, although its displayed Assumption A1 states existence and orbit uniqueness, not a quantitative separation. Equation (6) supplies it under the actual Gaussian gap. For the sum-of-\(L^2\)-distances metric used there, one may take \(\kappa(a)=\Delta a^2/8\). No compactness of the whole infinite-dimensional whitened function class is needed.

### Separating approximation, statistics and optimization

Suppose a chosen encoder class loses at most \(a\) in population objective relative to the full optimum, the empirical objective has uniform error at most \(u\), and the returned pair is within \(r\) of its empirical supremum. Then

\[
\eta\le a+2u+r,
\]

and the right-hand side of (6) becomes

\[
\frac{4(a+2u+r)}{g}.
\tag{7}
\]

This is a deterministic oracle inequality on the event supplying the statistical bound. It does not establish a sample rate for an unrestricted neural network class.

### Prediction of a new linear latent task

In the Gaussian affine case let a new target be \(Y=\beta^\top U+\xi\), with \(\mathbb E[\xi\mid U]=0\). For a whitened representation \(H=A\Phi(U)\), the best population linear readout has excess squared risk above the Bayes noise

\[
\inf_w\mathbb E[(w^\top H-\beta^\top U)^2]
=\beta^\top(I-A_1^\top A_1)\beta
\le\|\beta\|^2t_A
\le\frac{2\|\beta\|^2\eta}{\Delta}.
\tag{8}
\]

Thus the source's spectral gap controls an explicit class of downstream predictive tasks. This is a population comparator. Estimating its readout from fresh finite labels requires a separate regression bound.

## 4. Independent acquisition construction: remove all functions of acquired coordinates

The failure without (2) suggests a different population procedure. Ordinary CCA removes only linear combinations of previously selected functions. A nonlinear copy of a strong factor can therefore occupy the next slot. Conditional centering removes the complete function space of the already acquired factors.

The following is an independent, conditional construction, not an algorithm analyzed or implemented in the paper.

### Assumptions and operations

Retain the source's injective generators and jointly Gaussian latent pair, but assume only

\[
1>\rho_1>\rho_2>\cdots>\rho_d>0.
\tag{9}
\]

Distinct correlations simplify the scalar statement. There is no requirement that \(\rho_d>\rho_1^2\). The dimension \(d\) is supplied.

Assume access to global scalar maximal-correlation optimization and exact conditional expectations with respect to already learned feature tuples. After learning \(k\) paired features \(F_{1:k}(X)\), \(G_{1:k}(X')\), define

\[
R_k f=f-\mathbb E[f(X)\mid F_{1:k}(X)],
\]

\[
R'_k f'=f'-\mathbb E[f'(X')\mid G_{1:k}(X')].
\tag{10}
\]

Choose the next unit-variance pair from the ranges of \(R_k,R'_k\) to maximize absolute cross-correlation. At \(k=0\), this is ordinary scalar maximal correlation with centering.

It is essential to condition on the **joint acquired tuple**. Removing only each coordinate's linear span, or only separate univariate function spaces, does not remove all functions of the acquired tuple.

### Exact recovery proof

Inductively suppose the first \(k\) learned coordinates equal \(U_1,\ldots,U_k\) and \(V_1,\ldots,V_k\), up to nonzero signs. Their generated sigma-fields are therefore exactly those of the acquired canonical coordinates.

For a Hermite basis element,

\[
\mathbb E[h_\alpha(U)\mid U_{1:k}]
=
\begin{cases}
h_\alpha(U),&\alpha_{k+1}=\cdots=\alpha_d=0,\\
0,&\text{otherwise}.
\end{cases}
\]

Hence (10) removes precisely the modes supported entirely on acquired coordinates. Every surviving index contains an unused coordinate. Its largest correlation is \(\rho_{k+1}\), attained by \(h_{e_{k+1}}(U)=U_{k+1}\). Every surviving nonlinear mode has correlation at most \(\rho_1\rho_{k+1}<\rho_{k+1}\), while every other surviving linear mode has correlation at most \(\rho_{k+2}\).

Thus the scalar residual problem has the positive gap

\[
\gamma_k=\rho_{k+1}
-\max(\rho_{k+2},\rho_1\rho_{k+1})>0,
\qquad \rho_{d+1}:=0.
\tag{11}
\]

The same source diagonal-selection argument now forces the next pair to be the next linear canonical coordinates. Induction recovers all \(d\) coordinates.

For the source's \((.9,.5)\) example, the first step learns \(U_1,V_1\). Conditional centering removes every Hermite function of those acquired coordinates. The next leading correlation is .5, with the largest competing nonlinear correlation .45. Two sequential features therefore recover the two latent coordinates, while ordinary two-output CCA selects a nonlinear copy of the first.

### Resource and implementation boundary

The construction exchanges an oversized representation for additional nonlinear conditional-expectation operations. Those regressions can be difficult. It is not an efficient finite-sample theorem, and it does not establish a favorable comparison after pricing the new operations.

If previous coordinates and their conditional expectations are exact, (6) applies at each scalar step with gap \(\gamma_k\). With estimated earlier coordinates, the residual operators themselves change. Their statistical and operator stability, error accumulation, stopping rule and optimization cost remain unproved here. Small coordinate \(L^2\) error alone is not being assumed to provide a suitable conditional-operator perturbation bound.

The selection operates on observed views and already learned features through (10), so the population construction does not ask for the latent coordinates as inputs. Its exact expectation and global search oracles remain strong assumptions.

## 5. Independent finite capacity alternative

The source says that increasing output dimension eventually admits all first-order modes. Its diagonal expansion gives an explicit finite sufficient budget.

Put \(w_i=-\log\rho_i>0\). Define

\[
N_{\ge}(\rho_d)
=\#\left\{\alpha\in\mathbb N_0^d\setminus\{0\}:
\sum_i\alpha_iw_i\le w_d\right\}.
\tag{12}
\]

This is the number of modes with correlation at least the weakest linear one. Retaining at least this many top modes includes the entire first-order subspace, even when modes tie at \(\rho_d\). Since \(w_i\ge w_1\),

\[
N_{\ge}(\rho_d)
\le {d+L\choose L}-1,\qquad
L=\left\lfloor\frac{w_d}{w_1}\right\rfloor.
\tag{13}
\]

All relevant multi-indices can be enumerated below that weighted-degree threshold. The bound can be combinatorially large, and it presumes the source spectrum is available for choosing the budget.

For \((.9,.5)\), (12) equals seven, reproducing the source example. This finite-budget route keeps higher nonlinear modes. Conditional removal in Section 4 uses a different, more demanding operation to avoid them.

## 6. Independent coefficients for the actual non-Gaussian constructions

Appendix F gives a conditional Lancaster theorem. Independent coordinate pairs must have diagonal orthonormal polynomial cross-moments

\[
\mathbb E[\psi_{i,m}(S_i)\psi_{i,n}(S_i')]
=\lambda_{i,n}\mathbf1_{m=n}.
\]

Affine recovery follows only if the first-degree coefficients dominate all competing products. Naming a marginal distribution does not by itself specify these joint coefficients.

For the explicit additive constructions in Appendix G, the coefficients can be computed. The following derivations authenticate their ordering at the population level, without rerunning their samplers.

### Gamma shared-component construction

Let \(A,B\sim\operatorname{Gamma}(a,1)\), \(C\sim\operatorname{Gamma}(c,1)\) be independent, and \(S=A+C,S'=B+C\). Their marginal shape is \(r=a+c\). The Laguerre generating function

\[
G_r(x,t)=(1-t)^{-r}\exp\!\left(-\frac{xt}{1-t}\right)
=\sum_{n\ge0}L_n^{(r-1)}(x)t^n
\]

satisfies, for small \(t,u\),

\[
\mathbb E[G_r(S,t)G_r(S',u)]=(1-tu)^{-c}.
\]

The three independent Gamma Laplace transforms give this identity directly. Comparing coefficients and using the marginal norm \(\mathbb E[(L_n^{(r-1)}(S))^2]=(r)_n/n!\) yields

\[
\lambda_n=\frac{(c)_n}{(r)_n}.
\tag{14}
\]

For the paper's \(a=2,c=1\),

\[
\lambda_n=\frac{2}{(n+1)(n+2)},\quad
\lambda_1=\frac13,\quad\lambda_2=\frac16.
\]

These coefficients are not the geometric powers \((1/3)^n\).

### Negative binomial construction

Use the paper's convention with shape \(r\), success probability \(p\), and \(\beta=1-p\). A Meixner generating function can be written

\[
G_r(x,t)=(1-t)^{-r}
\left(\frac{1-t/\beta}{1-t}\right)^x.
\]

For independent shapes \(a,a,c\) sharing the same \(p\), the negative binomial probability-generating function gives

\[
\mathbb E[G_r(S,t)G_r(S',u)]=(1-tu/\beta)^{-c}.
\]

The marginal self-product has the same expression with \(c\) replaced by \(r\). Coefficient normalization therefore again gives (14). The source's shapes \(2,2,1\) have the same first-degree and second-degree coefficients as the Gamma construction.

### Poisson and bounded hypergeometric constructions

For private Poisson rate \(a\) and common rate \(c\), the Charlier generating function

\[
G_\lambda(x,t)=e^{-\lambda t}(1+t)^x,\qquad\lambda=a+c,
\]

has joint expectation \(\exp(ctu)\). Normalization gives \(\lambda_n=(c/(a+c))^n\). With the source rates \(a=2,c=1\), the first two are \(1/3,1/9\).

For two draws without replacement from a population of size \(N\), the source's one-draw hypergeometric marginals are Bernoulli. There is only one nonconstant univariate orthonormal polynomial, and its cross-coefficient is

\[
\lambda_1=-\frac1{N-1}.
\]

Conditional on fixed per-coordinate \(N_i\in\{10,\ldots,20\}\) and nondegenerate success counts, the first-degree absolute coefficients are at least \(1/19\), while any higher multivariate product is at most \(1/81\). The sampler implementation was not inspected, so this statement concerns the displayed fixed-parameter law.

The resulting population gaps for the displayed setups are:

| Setup | Weakest first-degree magnitude | Largest higher-degree magnitude | Sufficient gap |
|---|---:|---:|---:|
| Gaussian spectrum in [.3,.5] | .3 | .25 | .05 |
| Gamma shapes 2,2,1 | 1/3 | 1/6 | 1/6 |
| Negative binomial shapes 2,2,1 | 1/3 | 1/6 | 1/6 |
| Poisson rates 2,2,1 | 1/3 | 1/9 | 2/9 |
| One-draw hypergeometric, fixed sizes 10–20 | at least 1/19 | at most 1/81 | at least 62/1539 |

The Gaussian bound concerns the specified equally spaced spectrum with the stated endpoints. The others use independence across coordinates as in the source construction. These are sufficient population orderings, not empirical optimization certificates.

The bounded Bernoulli example also limits Appendix B's broad contrast with bounded-source contrastive learning. Bounded support alone does not preclude affine CCA identification. The precise spectral and joint-law conditions decide it.

## 7. Whitening and statistical consistency: exact scope

Appendix E makes the whitening statement more precise than some introductory wording. Normalized CCA can be rewritten on centered whitened outputs without loss of objective value. With no scale normalization, the raw cross-covariance nuclear norm is unbounded under simultaneous output rescaling.

Thus a hard whitening layer is not the only possible implementation. What matters for this proof is equivalent covariance normalization and the row-orthonormal coefficient constraint. A bound on each coordinate's variance alone does not enforce decorrelation or full rank. Nor does unit covariance make the entire infinite-dimensional \(L^2\) feasible class compact.

Theorem 2 assumes, rather than derives for a specified neural architecture:

- Existence and orbit uniqueness of a population maximizer.
- Uniform second-moment control and empirical nondegeneracy.
- Uniform convergence of all encoder auto- and cross-covariances at \(o_p(\varepsilon_n)\), for a ridge \(\varepsilon_n\to0\).
- Empirical optimization error tending to zero.

Its proof works over population-whitened feasible classes, where covariance matrices are near identity. It establishes an asymptotic conditional consistency statement. There is no explicit sample-size guarantee for the actual residual network family, and universal approximation alone does not supply the uniform convergence premise.

Equation (7) supplies a useful quantitative separation of the required errors. It does not remove their statistical or computational costs. A finite-capacity or sieve analysis would still have to bound approximation and covariance estimation while controlling normalization.

## 8. Experiments and limits

The source compares DeepCCA with SwAV, Barlow Twins, VICReg, W-MSE, DGCCA and rDGCCA under a common encoder design. Except for qualitative visualizations, reported metrics are averaged over five random seeds, with standard-deviation reporting.

On the controlled ten-dimensional synthetic setups, DeepCCA and W-MSE generally achieve near-99% latent linear-regression \(R^2\). The source tests source/observation-space training, varying finite sample sizes, source dimension, spectral dominance and over/undercomplete output dimensions. These are useful interventions on the theorem's structural assumptions.

The reported encoders use residual networks, batch normalization, Adam and a fixed learning rate \(10^{-4}\). Synthetic online training uses \(10^5\) iterations with batches of 1,024, so its observation access is much larger than a single small fixed dataset. The separate finite-dataset comparison uses a ridge schedule \(.01n^{-1/4}\). A converged neural solution trained online is used as a proxy for the population optimizer, not an exact oracle.

The image experiment constructs view pairs through nearest-neighbor retrieval in the ground-truth latent space of 3DIdent, then uses color and grayscale views. This supplies latent-informed pairing. Finite matching and grayscale conversion need not satisfy the theorem's exact injective generator and joint-Gaussian conditions. The paper acknowledges matching noise. Reported seven-dimensional image \(R^2\) is about 97.8% for DeepCCA.

Visual inspection adds two bounded qualifications. Figure 1 omits the hypergeometric two-dimensional visualization because of collapse, so the positive ten-dimensional table is not a universal optimization claim. Figure 5 retains substantial error at larger dimensions above dominance ratio one, and its left panel's plotted axis label is inconsistent with the caption's \(R^2\) description. The source theorem is an exact population statement, so these finite optimization outcomes do not refute it, but neither do they establish an all-dimension empirical threshold.

The declared code repository was not audited. The comparison does not establish that whitening is the uniquely necessary training method or that every correlation-based self-supervised objective inherits the same theorem. Momentum encoders, stop gradients, other objectives and their optimization dynamics need their own analysis.

## 9. Reusable theoretical results and boundary with FP

The source contributes a clean diagonal operator representation, a first-order spectral condition and a careful normalized-CCA symmetry account. The independent additions here are:

1. An objective-gap to \(L^2\)-recovery inequality and a linear-task prediction comparator.
2. A population sequence that removes all functions of acquired coordinates before selecting the next one.
3. A finite overcomplete budget obtained by counting weighted-degree modes.
4. Explicit Lancaster coefficients and gaps for the displayed non-Gaussian constructions.

These describe genuine mathematical operations and their required information. They do not constitute a recurrent FP state-construction theorem, a finite-bit representation, a sample-efficient conditional-regression algorithm, or a recommendation to change FP architecture.

No core files were modified. This ordinary paper was selected after fresh Git, owner and edition checks. Astra request 2e7a6c9 was already completed by Pro-A at e0296c3. The next unit begins with another request and ownership check.
