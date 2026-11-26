# Two-stage risk, representation symmetry and the limits of the printed application formulas

## 1. Source, edition and completed reading

Mohammad Tinati and Stephen Tu, **On the Asymptotics of Self-Supervised Pre-training: Two-Stage M-Estimation and Representation Symmetry**, COLT2026, PMLR336:6197–6309. [Official record](https://proceedings.mlr.press/v336/tinati26a.html) · [Official113page PDF](https://raw.githubusercontent.com/mlresearch/v336/main/assets/tinati26a/tinati26a.pdf) · [arXiv2603.27631v2](https://arxiv.org/abs/2603.27631v2) · [v2 complete source](https://arxiv.org/src/2603.27631v2) · [Author simulation code](https://github.com/mtinati/mog-subspace-jax).

Pro-D completed the official edition on November26,2026, Shanghai. Reading covers all113physical pages, main §§1–7, AppendicesA–L, every active mathematical statement and proof, all4figures, the5scientific footnotes, acknowledgments and65printed references. The scientific source has21active TeX files, including macros and entry files, with12scientific appendix files. Its bibliography database has73entries, while the final PDF has65reference destinations. Reading that bibliography does not constitute reading those65papers.

The full source was read in natural section blocks. Official PDF text supplied the complete main text, bibliography and contents. Four figure-bearing pages2,12,13,112 and ten additional formula/proof pages7,10,39,40,64,65,83–85,100 were visually inspected. There are no table environments. The86displayed theorem-style blocks include one restatement. No inactive scientific blocks were found in the source, and the reading copy only merged redundant blank lines.

Both the official PDF and arXivv2 have113pages. Raw MuPDF text and Poppler layout text agree pagewise on pp4–113. On pp1–3, the author version adds a title star, acceptance footnote and arXiv watermark, shifting two lines across each of the first two page boundaries. After those enumerated metadata changes and page furniture are removed, the combined first-three-page body text agrees. This establishes scientific-text correspondence, not binary, pixel or recompilation identity. ArXivv2 is dated July1,2026 and is a companion to the one counted full reading.

| Artifact | SHA256 |
|---|---|
| Official PDF | 5513738555936ea16d74e9d4ebc9518f9261b4c0cd2f73ee78402e72b3fc9698 |
| arXivv2 PDF | a5936e3ffa80397ce8cf9f66323e877073a9ed1e297968ea544ce95bf8b000ab |
| arXivv2 source archive | 3a1a0cf7a50e8bc3a8218c15fceaa46f55831a6694cec624d102e44aa7bbe562 |

This is peer-reviewed author research, not official OpenAI or Anthropic research. AppendixL discloses ChatGPT assistance with literature identification, high-level proof strategies, mathematical proofreading, editing and experiment code, and Claude assistance with schematic illustrations. The disclosure is retained as provenance, without attributing individual mistakes to those tools.

**Assessment.** The exact conditional risk decomposition, quotient treatment of orthogonal symmetries, relative covariance argument and regular residual linearization provide useful tools. The printed extension to activated null directions misses an exact-hit condition. Two separate small, fully Gaussian regular examples also contradict the explicit constants in Corollaries6.3 and6.4. These application failures do not refute the regular abstract proof using the correct Hessian and projector derivative. The note gives bounded independent calculations and conditional repairs, not a whole-paper certification or empirical reproduction.

## 2. Statistical object and assumptions

The pipeline receives independent iid pretraining data of size\(m\) and downstream pairs of size\(n\). The downstream law is
\[
Y=f_\star(X)+\varepsilon,
\qquad \mathbb E[\varepsilon\mid X]=0,
\qquad \mathbb E[\varepsilon^2\mid X]=\sigma^2.
\]
A representation parameter\(w\) is fitted by empirical minimization of a pretraining loss. The feature vector\(\psi(x,w)\in\mathbb R^p\) is then frozen, and a minimum-Euclidean-norm least-squares head is fitted to the labeled data. All dimensions and the data-generating instance are fixed while\(m,n\) grow.

A compact Lie group\(G\) describes representation nonuniqueness. The descriptor\(\Omega=D(w)\) identifies the relevant local orbits and lies on a finite-dimensional smooth manifold. The population pretraining descriptor is\(\Omega_\star\). Orthogonal equivariance,
\[
\psi(x,g\cdot w)=\rho(g)\psi(x,w),
\qquad \rho(g)\in O(p),
\]
makes the fitted predictor independent of the representative, including rank-deficient designs. The pseudoinverse identity\((MQ)^+=Q^TM^+\) is the relevant algebra. Equality of the feature function classes alone would not guarantee that an arbitrary change of coordinates preserves a minimum-Euclidean-norm interpolant off the observed design. See §4 and AppendixE, pp5–6,43–47.

The risk in the paper is
\[
R(D_{\rm pre}^{(m)},X_{1:n})
=\mathbb E[(Y_{\rm new}-\widehat f(X_{\rm new}))^2
\mid D_{\rm pre}^{(m)},X_{1:n}].
\tag{1}
\]
It averages over the training label noise and the independent test pair. It is random through pretraining and the downstream covariates. It is not the risk conditional on the entire realized labeled training set.

The assumptions needed to use the proof are substantive.

| Condition | Actual content |
|---|---|
| D.5, pp39–40 | A unique separated population descriptor, local uniform LLN, localization of the empirical minimizer, local\(C^2\) loss, a finite second score moment, invertible Riemannian Hessian and uniform convergence of transported empirical Hessians |
| Compatibility | \(f_\star\in\mathcal H_{\Omega_\star}\), the class at the population **pretraining** optimum |
| G.1, p52 | The downstream evaluation map is injective on the learned feature function space with probability tending to one |
| G.2, p52 | Uniform local\(4+\delta\) feature moments,\(2+\eta\) leverage moments and an appropriate leverage-weighted residual moment |
| G.3, p52 | Pointwise local\(C^1\) features with uniform\(4+\delta\) derivative moments |
| G.4, p53 | The orthogonal projector onto the span activated by previously null coefficients has a direction-independent operator-norm limit |

Compatibility is stronger than\(f_\star\in\mathcal F=\bigcup_w\mathcal H_w\). The latter alone does not imply zero approximation error at an unrelated pretraining minimizer. The main text's sentence making this implication must be read with the compatibility requirement made explicit in AppendixG.

D.5 assumes localization. A local LLN and a uniquely separated population minimizer do not by themselves establish localization of every empirical minimizer on a noncompact parameter space. Likewise, a generic local optimizer is not automatically the selected consistent minimizer.

The descriptor CLT is the standard sandwich form in intrinsic coordinates,
\[
Z_m=\sqrt m\log_{\Omega_\star}(\widehat\Omega_m)
\Rightarrow Z\sim N(0,V),
\qquad V=H_\star^{-1}\Gamma_\star H_\star^{-1},
\tag{2}
\]
where\(\Gamma_\star\) is the covariance of the loss score. The paper calls it\(\Sigma_\star\), and sometimes Fisher information. For a general pretraining loss it is a score covariance, without the likelihood information identity. D.5 makes\(H_\star\) invertible but does not require\(\Gamma_\star\) to be positive definite or nonzero.

## 3. Exact conditional decomposition

For a fixed descriptor define
\[
T_\Omega\theta=\theta^T\phi(\cdot,\Omega),
\quad \Sigma_\Omega=T_\Omega^*T_\Omega,
\quad \mathcal H_\Omega=\operatorname{Im}T_\Omega,
\quad \Pi_\Omega=T_\Omega\Sigma_\Omega^+T_\Omega^*.
\]
Let\(\Sigma_{\Omega,n}=n^{-1}\sum_i\phi_i\phi_i^T\) and let\(\Pi_{\Omega,n}f\) denote the function produced by minimum-norm empirical least squares on the values\(f(X_i)\). Write\(e_\Omega=(I-\Pi_\Omega)f_\star\).

PropositionB.1 and AppendixF give the exact identity
\[
\boxed{
R=\sigma^2+\|e_\Omega\|_2^2
+\|\Pi_{\Omega,n}f_\star-\Pi_\Omega f_\star\|_2^2
+\frac{\sigma^2}{n}\operatorname{tr}
(\Sigma_\Omega\Sigma_{\Omega,n}^+).
}
\tag{3}
\]
All norms are in the true downstream\(L^2\) space, and\(\Omega=\widehat\Omega_m\) after conditioning. The empirical bias lies in\(\mathcal H_\Omega\), orthogonal to\(e_\Omega\). The noise-fit cross term vanishes after averaging the centered labels. The trace is the exact covariance contribution of the fitted noise.

On G.1's event,\(\Pi_{\Omega,n}\Pi_\Omega f_\star=\Pi_\Omega f_\star\). Thus the middle squared norm becomes
\[
\operatorname{Leak}_{m,n}=\|\Pi_{\Omega,n}e_\Omega\|_2^2.
\tag{4}
\]
This specialization requires the empirical identification event. Equation(3) itself does not require it.

One presentation detail in AppendicesC/F is best avoided in reuse. An arbitrary vector of noisy labels cannot always be lifted to a function of\(x\) that takes all those values if covariates repeat. Direct design-matrix algebra proves(3) without such a lift. This does not obstruct the identity, and the bounded discrete example below can be analyzed directly in that form.

## 4. The useful proof mechanism

### 4.1 Residuals can be smoother than the whole projector

Set\(N_\star=\ker T_\star\),\(E_\star=N_\star^\perp\), and use normal coordinates\(\Omega(v)=\exp_{\Omega_\star}(v)\). The stable image is
\[
\mathcal A_v=\operatorname{Im}(T_v|_{E_\star}).
\]
For nonzero\(v\), the additionally activated image is
\[
\mathcal B_v=operatorname{Im}[(I-\Pi_{\mathcal A_v})T_v|_{N_\star}].
\]
G.4 assumes\(\Pi_{\mathcal B_v}\to\Pi_{\mathcal B_0}\) in operator norm, with\(\mathcal B_0\perp\mathcal H_\star\). Then\(\mathcal H_v=\mathcal A_v\oplus\mathcal B_v\) away from zero. The source's residual argument yields
\[
e_{\Omega(v)}=\mathcal L(v)+o(\|v\|),
\qquad
\mathcal L(v)=-(I-\Pi_\star-\Pi_{\mathcal B_0})DT_\star[v]\theta_\star.
\tag{5}
\]
The formula does not depend on the selected coefficient representation of\(f_\star\). It extends to\(v=0\), where both the residual and its linearization vanish. Combining(2) and(5) gives
\[
m\operatorname{Rep}(\widehat\Omega_m)\Rightarrow\|\mathcal LZ\|_2^2.
\tag{6}
\]
The source proves these steps in G.5–G.11, pp53–59. Moment bounds allow pointwise feature differentiability to pass to operator differentiability through uniform integrability. The proof treats the residual of the compatible target, rather than assuming the entire projector is differentiable across a rank jump.

When\(\mathcal B_0=0\), operator-norm convergence of finite-rank projectors makes the rank locally constant. The positive nonzero eigenvalues then have a local gap from zero. Pseudoinverse differentiation gives
\[
\mathcal L(v)=-D\Pi_\star[v]f_\star
=-(I-\Pi_\star)DT_\star[v]\theta_\star.
\tag{7}
\]
Equation(7) is the correctly typed and signed regular formula from AppendixG. The displayed Eq.(6.1) in the main text instead puts\(f_\star\) where a coefficient vector is needed and has a sign mismatch in its final expression. Squared risk hides a global sign error, but derivative reuse should follow(7).

### 4.2 Whitening controls the noise term without a uniform eigenvalue gap

Write\(\Sigma_m=\Sigma_{\widehat\Omega_m}\),\(r_m=\operatorname{rank}\Sigma_m\), and\(P_m\) for its range projector. Define
\[
C_{m,n}=\Sigma_m^{+/2}\Sigma_{m,n}\Sigma_m^{+/2}.
\]
G.16 conditions on pretraining and uses the leverage
\[
q_\Omega(X)=\phi(X,\Omega)^T\Sigma_\Omega^+\phi(X,\Omega).
\]
The local uniform second leverage moment bounds the Frobenius mean-square error of\(C_{m,n}\) by a constant divided by\(n\). Hence
\[
\|C_{m,n}-P_m\|_{\rm op}\to_P0.
\]
On an event with this difference at most\(\rho<1\), the empirical span equals the population span and
\[
\left|\operatorname{tr}(\Sigma_m\Sigma_{m,n}^+)-r_m\right|
\le\frac{p\rho}{1-\rho}.
\tag{8}
\]
Thus the trace converges to the **actual learned rank** in probability. This part does not require an absolute covariance eigengap, because whitening and leverage control carry the conditioning. See G.15–G.17, pp62–64.

### 4.3 Leakage vanishes at the downstream scale

Orthogonality gives\(\mathbb E[e_\Omega(X)\phi(X,\Omega)]=0\). The whitened empirical residual-feature correlation has conditional second moment of order
\[
\frac1n\mathbb E[e_\Omega(X)^2q_\Omega(X)].
\]
The weighted moment in G.2 and Hölder imply
\[
\mathbb E[e_\Omega^2q_\Omega]
\le
(\mathbb E e_\Omega^2)^{\eta/(1+\eta)}
(\mathbb E[e_\Omega^2q_\Omega^{1+\eta}])^{1/(1+\eta)}\to0.
\tag{9}
\]
Together with relative covariance control, this gives\(n\operatorname{Leak}_{m,n}\to_P0\), the content of G.21–G.22, pp67–70.

Equations(3), (5), (8) and(9) consequently retain the following useful intermediate expansion, before replacing the random rank by a claimed limit:
\[
\boxed{
n(R-\sigma^2)
=\sigma^2r_m+\frac nm\|\mathcal LZ_m\|_2^2+o_P(1).
}
\tag{10}
\]
Here\(m/n\to\alpha\in(0,\infty)\) and all the stated localization, compatibility and moment assumptions are in force. Equation(10) is a direct synthesis of those source lemmas, with the rank left explicit. It is not an unconditional claim for arbitrary representation learners.

## 5. A precise limit theorem and two useful consequences

The printed Theorem5.1 on p7 replaces\(r_m\) in(10) by
\[
d_{\rm act}=\dim\mathcal H_\star+\dim\mathcal B_0
\]
and asserts
\[
n(R-\sigma^2)\Rightarrow
\sigma^2d_{\rm act}+\alpha^{-1}\|\mathcal LZ\|_2^2.
\tag{11}
\]
Although AppendixG's introductory paragraph describes the main theorem as regular, the actual displayed main theorem includes\(d_{\rm act}\) and G.4's nonregular case. Section6 below addresses that printed formulation.

Equation(11) is supported by the preceding proof when the additional conclusion\(r_m\to_Pd_{\rm act}\) holds. It holds in the regular case\(\mathcal B_0=0\). More generally, if only\((r_m,Z_m)\Rightarrow(R_\infty,Z)\) is available, (10) instead gives
\[
n(R-\sigma^2)\Rightarrow
\sigma^2R_\infty+\alpha^{-1}\|\mathcal LZ\|_2^2.
\tag{12}
\]
The rank and Gaussian limit need not be independent. Without convergence of this pair, no unique distributional limit is asserted here.

### 5.1 The entire Gaussian quadratic form matters

Let\(K=V^{1/2}\mathcal L^*\mathcal LV^{1/2}\) on the finite-dimensional descriptor tangent space. If its nonzero eigenvalues are\(\lambda_1,\ldots,\lambda_s\), then
\[
Q=\|\mathcal LZ\|_2^2
\overset d=\sum_{j=1}^s\lambda_j\chi_{1,j}^2,
\quad \mathbb EQ=\operatorname{tr}K,
\quad \operatorname{Var}Q=2\operatorname{tr}(K^2).
\tag{13}
\]
This direct consequence separates mean, dispersion and directional pretraining uncertainty. A single effective dimension does not determine\(Q\). Positive descriptor dimension does not even force a nonzero pretraining penalty when the score covariance vanishes in the relevant directions.

Convergence in distribution does not imply convergence of the expected scaled risk. The paper explicitly states uniform integrability as an additional requirement for its expected-risk crossover. It does not prove this property in the general theorem. Without it, one can still use distributional quantiles at continuity points, and nonnegativity gives a lower-semicontinuity statement for expectations.

### 5.2 The downstream tangent dimension gap equals the residual rank

In the regular case, AppendixG.4 defines
\[
\mathcal T_{\rm base}
=\mathcal H_\star+
\{DT_\star[v]\theta_\star:v\in T_{\Omega_\star}\mathcal M\}.
\]
Since\(\mathcal L(v)=-(I-\Pi_\star)DT_\star[v]\theta_\star\), its argument immediately strengthens to the orthogonal decomposition
\[
\boxed{
\mathcal T_{\rm base}=\mathcal H_\star\oplus\operatorname{Im}\mathcal L,
\qquad d_{\rm base}-d_{\rm eff}=\operatorname{rank}\mathcal L.
}
\tag{14}
\]
Indeed, subtracting the\(\mathcal H_\star\) component of every derivative leaves exactly\(-\mathcal L(v)\), and these remaining directions are orthogonal to\(\mathcal H_\star\). This is an independent linear-algebra consequence of the source's tangent definitions, stronger than G.23's zero-gap equivalence.

If the separately assumed regular downstream-only estimator has the paper's limit\(\sigma^2d_{\rm base}\), then under uniform integrability the expected crossover is
\[
\alpha_0=\frac{\operatorname{tr}K}{\sigma^2\operatorname{rank}\mathcal L},
\tag{15}
\]
for\(\sigma^2>0\) and a positive dimension gap. A distributional comparison instead uses quantiles of\(Q\). Neither comparison is a proof of global optimization, increasing-dimensional sample complexity, or memory optimality. The theorem fixes\(\alpha\) in\((0,\infty)\). Sending\(\alpha\) to zero or infinity in its resulting expression is an iterated-limit interpretation, not a proved uniform result for every unbalanced sample sequence.

## 6. Exact-hit counterexample to the activated-dimension claim

This independent example satisfies the printed geometric and moment assumptions but makes the inference in LemmaG.18 fail.

Take a trivial group and descriptor\(w\in\mathbb R\). Let
\[
\ell_{\rm pre}(w,z)=\frac12w^2,
\qquad w_\star=\widehat w_m=0
\]
for every pretraining dataset. The Hessian is1, the score covariance is0, and all D.5 conditions hold. Let\(X\) be a fair sign and
\[
\phi(X,w)=(1,wX),\qquad f_\star(X)=1,
\qquad Y=1+\varepsilon,
\quad \varepsilon\sim N(0,\sigma^2),\quad \sigma^2>0.
\tag{16}
\]
At zero,\(\mathcal H_\star=\operatorname{span}\{1\}\). For every nonzero\(w\), the null coefficient direction activates\(X\), so
\[
\mathcal A_w=\operatorname{span}\{1\},
\quad \mathcal B_w=\mathcal B_0=\operatorname{span}\{X\},
\quad d_{\rm act}=2.
\]
The leverage equals1 at zero and2 away from zero. All feature, derivative and weighted moments are bounded locally. The true signal belongs to every feature class, so\(e_w=0\) and\(\mathcal L=0\). G.1 holds for the actually learned intercept class on every nonempty design.

Nevertheless the learned features are always\((1,0)\). The minimum-norm fit is simply the sample mean of the labels. Exactly,
\[
\boxed{n(R-\sigma^2)=\sigma^2,}
\tag{17}
\]
whereas the printed(11) gives\(2\sigma^2\).

The failure is on p65. G.18 first correctly establishes the active rank for all sufficiently small **nonzero**\(v\), then substitutes a random\(v_m\to_P0\) without excluding\(v_m=0\). The latter event can have probability one.

A sufficient repair is to require\(r_m\to_Pd_{\rm act}\) explicitly. Under the paper's local stable-null-span geometry, when\(\mathcal B_0\ne0\), the additional condition
\[
\Pr(\widehat\Omega_m\ne\Omega_\star)\to1
\tag{18}
\]
also suffices. If the Gaussian in(2) has nonzero covariance, even if singular, it has no point mass at zero, and the CLT implies(18). Positive definiteness is unnecessary. The zero-covariance case may still satisfy(18), but it is not guaranteed to do so. The constant-rank regular theorem is unaffected by this example.

## 7. Linear spectral example: a regular Gaussian counterexample to Corollary6.3

The source's spectral loss is
\[
\ell(M)=-2X^TMX^++(X^TMX^-)^2,
\quad M=A^TA,\quad\operatorname{rank}M=k.
\tag{19}
\]
The positive pair is exchangeable. The negative sample is an independent copy of\(X\). The population objective is
\[
L(M)=-2\operatorname{tr}(M\Sigma_{\rm pre}^+)
+\operatorname{tr}(M\Sigma_{\rm pre}M\Sigma_{\rm pre}).
\]
Whitening reduces its minimizer to the positive top-\(k\) truncation of the whitened positive-pair covariance. An appropriate eigengap gives a unique regular descriptor. These are the useful geometric ingredients in AppendixH.

For the following bounded check take exactly the concrete main-text instance with\(k=1,d=3\),
\[
\Sigma_{\rm pre}=I_3,
\quad C=\Sigma_{\rm pre}^+=\operatorname{diag}(1,1/2,1/3),
\quad f_\star(x)=x_1,
\quad X_{\rm down}\sim N(0,I_3).
\]
To specify the full observation law, take independent standard normal variables\(A,B_2,B_3,E_2,E_3,R,F_2,F_3\), and set
\[
X=(A,B_2,B_3),\qquad X^-=(R,F_2,F_3),
\]
\[
X^+=(A,c_2B_2+\sqrt{1-c_2^2}E_2,
c_3B_3+\sqrt{1-c_3^2}E_3),
\quad(c_2,c_3)=(1/2,1/3).
\tag{20}
\]
This has precisely the stipulated covariance and exchangeability, and all moments exist. Perfect correlation of the first positive-pair coordinate is already required by\(C_{11}=1\). It is not a violation of an assumed positive-pair nonsingularity condition.

### 7.1 The curvature term cannot be discarded

Use a genuine rank-one PSD chart at\(M_\star=\operatorname{diag}(1,0,0)\),
\[
M(r,z)=\begin{pmatrix}r&z^T\\z&zz^T/r\end{pmatrix},
\quad r>0,\quad z=(z_2,z_3).
\]
Substitution into the population objective gives exactly
\[
L(r,z)=r^2-2r+2\|z\|^2
-\frac2r(c_2z_2^2+c_3z_3^2)+\frac{\|z\|^4}{r^2}.
\]
Therefore its coordinate Hessian at\((1,0,0)\) is
\[
H_{\rm coord}=\operatorname{diag}(2,4(1-c_2),4(1-c_3))
=\operatorname{diag}(2,2,8/3).
\tag{21}
\]
CorollaryH.14 on p83 instead substitutes the ambient Hessian\(v\mapsto2\Sigma_{\rm pre}v\Sigma_{\rm pre}\). The ambient population gradient has a normal component at this constrained minimizer, so the manifold curvature contributes to the second derivative. In a Frobenius orthonormal off-diagonal tangent basis, the correct eigenvalues are\(2(1-c_i)\), not2.

### 7.2 Direct score calculation

The coordinate scores from the original sample loss are
\[
S_r=2A^2(R^2-1),
\]
\[
S_i=2\left[AB_i(R^2-1-c_i)
-\sqrt{1-c_i^2}AE_i+A^2RF_i\right],\quad i=2,3.
\tag{22}
\]
They have zero means and covariance\(24I_3\). For example,
\[
\operatorname{Var}S_i
=4[(2+c_i^2)+(1-c_i^2)+3]=24.
\]
The two off-diagonal scores have zero conditional means and are conditionally independent given\((A,R)\), which gives zero cross covariance. Their joint Gaussian **limit** is independent after diagonalization. The original scores need not be independent.

The coordinate sandwich covariance is consequently
\[
H_{\rm coord}^{-1}(24I_3)H_{\rm coord}^{-1}
=\operatorname{diag}(6,6,27/8).
\tag{23}
\]
The downstream representation error has the exact elementary form
\[
\operatorname{Rep}(r,z)=\frac{z_2^2+z_3^2}{r^2+z_2^2+z_3^2}.
\]
Thus the correct limit in this instance is
\[
\boxed{
n(R-\sigma^2)\Rightarrow
\sigma^2+\alpha^{-1}\left(6\chi_1^2+\frac{27}{8}\widetilde\chi_1^2\right),
}
\tag{24}
\]
with independent chi-square variables. The printed Corollary6.3 gives\(\sigma^2+6\alpha^{-1}\chi_2^2\), which differs.

There is a second factor issue in the subsequent conversion of symmetric-matrix covariance to entry variance. For\(H_i=E_{1i}+E_{i1}\),
\[
\langle H_i,Z\rangle_F=2Z_{1i},
\quad \langle H_i,VH_i\rangle_F=4\operatorname{Var}(Z_{1i}).
\]
Treating this quadratic-form value as entry variance loses a factor of4. At\(c_i=1/2\) this happens to cancel the ambient-Hessian error, which is why the\(d=2\) version would fail to reveal the problem. The\(c_3=1/3\) coordinate separates the two effects.

These calculations refute the printed closed form in a regular Gaussian example. They do not refute the abstract constant-rank mechanism with the correct Riemannian Hessian. The claimed comparison with earlier\(k\)-dependent bounds cannot be imported using the printed coefficient. A fixed-dimensional CLT also does not by itself establish a simultaneous high-dimensional rate.

A separate scope issue appears in Proposition6.2. Its statement assumes fourth moments, while the downstream verification uses stronger\(4+\delta\) moments and positive definite downstream covariance, and the pretraining verification invokes stronger polynomial moment envelopes. This is a mismatch in the written implication, not a proof that every fourth-moment version of the limit is false. The Gaussian counterexample above avoids that issue by satisfying all these stronger moment conditions.

## 8. Factor model: a moving section has a real transverse derivative

The source considers\(X=A_\star h+\mu\), with standard independent Gaussian\(h,\mu\), and labels\(Y=\beta_\star^Th+\nu\). Pretraining estimates\(M=A A^T\) by PPCA maximum likelihood. The feature
\[
\phi(x,M)=s(M)^T(I+M)^{-1}x
\]
generates the same linear prediction space as\(\operatorname{range}M\). The PPCA estimator and its descriptor covariance limit in AppendixI are usable here.

For a second bounded check take\(k=1,d=2\),\(A_\star=\sqrt{s}e_1\),\(\beta_\star=1\), with fixed\(s>0\). Gaussian conditioning gives
\[
\Sigma_x=\operatorname{diag}(1+s,1),
\quad f_\star(x)=\frac{\sqrt{s}}{1+s}x_1,
\quad \sigma^2=\sigma_\nu^2+\frac1{1+s}.
\tag{25}
\]
The main text's noise formula has a dimensional typo, placing a\(d\)-dimensional inverse between\(k\)-dimensional\(\beta\) vectors. The correct general conditional variance uses\((I_k+A_\star^TA_\star)^{-1}\). Equation(25) resolves that presentation issue directly and does not resolve the distinct error below.

With\(S_m=m^{-1}\sum X_jX_j^T\), the PPCA estimator is
\[
\widehat M_m=(\widehat\lambda_1-1)_+\widehat u_1\widehat u_1^T.
\]
The population eigengap is\(s\). Eigenvector perturbation and\(\operatorname{Var}(X_1X_2)=1+s\) give
\[
\sqrt m(\widehat M_m)_{21}\Rightarrow Z_{21}\sim N(0,1+s).
\tag{26}
\]
This agrees with the source's pp98–99 descriptor calculation.

Use\(M(r,z)=\bigl(\begin{smallmatrix}r&z\\z&z^2/r\end{smallmatrix}\bigr)\) and the valid section\(a(r,z)=(\sqrt r,z/\sqrt r)^T\), at\((r,z)=(s,0)\). Since\((I+M)^{-1}a\) is a scalar multiple of\(a\), the feature space is\(\operatorname{span}\{rx_1+zx_2\}\). Its exact downstream projection loss is
\[
\operatorname{Rep}(r,z)
=\frac{s}{1+s}\frac{z^2}{(1+s)r^2+z^2}.
\tag{27}
\]
Consequently
\[
\mathcal L(Z)(x)=-\frac{Z_{21}}{\sqrt{s}(1+s)}x_2,
\qquad
Q\overset d=\frac1{s(1+s)}\chi_1^2.
\tag{28}
\]
For\(s=2\), the correct limit is
\[
\boxed{n(R-\sigma^2)\Rightarrow\sigma^2+\frac1{6\alpha}\chi_1^2,}
\tag{29}
\]
whereas Corollary6.4 prints\(\sigma^2+2(3\alpha)^{-1}\chi_1^2\).

The erroneous step is p100, after Eq.(I.13). The correctly differentiated feature loading is
\[
DU_\star[v]=-\Sigma_x^{-1}v\Sigma_x^{-1}A_\star
+\Sigma_x^{-1}Da(M_\star)[v].
\]
For a pure off-diagonal direction\(v_{21}=z\), these two terms are respectively
\[
-\frac{\sqrt{s}z}{1+s}e_2,
\qquad \frac z{\sqrt{s}}e_2.
\]
Both are transverse to the original feature subspace. Their sum is\(z/[\sqrt{s}(1+s)]e_2\). The source discards the second term as section-dependent. Pure gauge changes within a fixed subspace can be removed, but the whole section derivative also contains the physical motion of that subspace. It cannot be discarded.

The discrepancy is consequential for weak signals. Across the family of fixed\(s>0\) instances, the correct asymptotic coefficient is\(1/[s(1+s)]\), rather than\(s/(1+s)\). This is a comparison of fixed-instance coefficients, without asserting a uniform theorem as\(s\) tends to zero jointly with sample size.

## 9. Mixture example and numerical evidence

The third application uses equal-weight spherical Gaussian mixtures with distinct centers, a locally stable centered-mean subspace, and posterior-responsibility features multiplied by projected affine covariates. Component permutations give a discrete orthogonal symmetry. The regular rank assumption sets the effective feature dimension to\(K(r_\star+1)\). In the ambient\(K(d+1)\) description, the remaining directions are redundant. The AppendixJ full-rank argument should be read in a smooth local basis for the retained subspace.

The appendix verifies local feature and derivative moment bounds, and gives likelihood score/Hessian formulas. Its localization argument invokes additional local strong-convexity, Hessian-consistency and gauge-fixing conditions in LemmaJ.5. A selected consistent local MLE remains distinct from an assertion that arbitrary EM initialization reaches it. No independent global optimization theorem is supplied by these arguments. Compatibility of the downstream target is also required.

The numerical study is explicitly synthetic. AppendixK uses means\(\beta e_i\), with\(d\ge K\), and a block-structured downstream coefficient vector whose blocks decay like\(1/i\) before normalization. Its three-stage interaction estimate uses100,000samples for Fisher information,1,000,000for projection and1,000,000fresh samples for evaluation. Figure2's quadratic, logarithmic and power-law curves are descriptive fits, with reported\(R^2\) values0.99,0.89,0.90. They are not proved laws in\(K,d,\beta\).

For Figures3–4 the instance is\(K=4,d=20,\beta=2,m/n=2\). The authors simulate1000repetitions per downstream sample size, compare with20,000Gaussian draws from the limit, and use100,000samples for the Fisher estimate and200,000each for projection, evaluation and risk calculation. Label-noise expectations are computed analytically from the conditional decomposition. Independent downstream and evaluation data are part of the stated protocol.

The study reports CDF convergence for the total and pretraining terms. For the deterministic variance limit it uses the probability of a5percent relative deviation, avoiding the discontinuity problem of Kolmogorov distance to a point mass. Figure4's plotted error bars are not accompanied by an explicit confidence-level construction in the read AppendixK. These simulations support the selected regular mixture setting at the reported numerical precision. They do not validate the two separate spectral/factor closed forms, remove exact-hit cases, establish uniform integrability, or prove broad empirical scaling laws. The linked code was not audited or rerun in this reading.

## 10. Reusable conclusions and research boundaries

The following are the main mathematical instruments retained from this reading.

1. Orthogonal equivariance is a sufficient interface for representative-independent minimum-norm least-squares predictions.
2. The exact conditional decomposition separates approximation, empirical signal leakage and label-noise fitting.
3. Relative whitening can control the trace risk at a moving, poorly scaled covariance when leverage moments remain controlled.
4. A compatible target residual can have a first-order expansion even when the full projector crosses a rank jump.
5. The actual learned rank must be tracked before replacing it by an activated limiting dimension.
6. In the regular setting the downstream tangent dimension gap is exactly\(\operatorname{rank}\mathcal L\), and the pretraining cost is a Gaussian quadratic form determined jointly by sensitivity and score covariance.

The independently checked negative results have distinct scopes. Equation(17) addresses the nonregular extension of Theorem5.1. Equation(24) addresses the spectral closed form in a regular Gaussian model. Equation(29) addresses the factor closed form in another regular Gaussian model. Root derived the explicit models and formulas, a helper independently checked the bounded examples, and exact symbolic Gaussian-moment and projection calculations confirmed the displayed small-model Hessians, covariances and coefficients. No whole-theorem reproof, formal proof assistant, training replication or comprehensive code audit was performed.

This paper studies fixed-dimensional iid two-stage estimation with a supplied representation family, an assumed compatible population pretraining optimum and a least-squares readout. It does not establish autonomous state formation, finite installed-bit memory, predictive sufficiency for all future tasks, learning from dependent controlled histories, or global optimization of a general neural representation. No FP theorem transfer or modification of core definitions, architecture, learning rules or experiments is proposed. The reusable statistical interfaces and their explicit failure conditions are provided for Astra's judgment.
