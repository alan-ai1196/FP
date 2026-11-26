# The Generative Leap: kernel moments construct an unknown predictive subspace

**Reader:** Pro-D  
**Completed:** 2026-11-26, Asia/Shanghai  
**Read edition:** Alex Damian, Jason D. Lee and Joan Bruna, *The Generative Leap: Tight Sample Complexity for Efficiently Learning Gaussian Multi-Index Models*, NeurIPS 2025, volume 38, official conference PDF, 36 pages. The official BibTeX gives pp. 28276–28311 and DOI 10.52202/085713-0953.

## Provenance and actual coverage

- [Official proceedings record](https://proceedings.neurips.cc/paper_files/paper/2025/hash/290056cc784d4825eb8cf5c72f808ebb-Abstract-Conference.html)
- [Read official PDF](https://proceedings.neurips.cc/paper_files/paper/2025/file/290056cc784d4825eb8cf5c72f808ebb-Paper-Conference.pdf)
- [Official bibliography export](https://proceedings.neurips.cc/paper_files/paper/31369-/bibtex)
- [Earlier arXiv 2506.05500v1](https://arxiv.org/abs/2506.05500v1), submitted June 5, 2025, titled *The Generative Leap: Sharp Sample Complexity for Efficiently Learning Gaussian Multi-Index Models*
- [Earlier source archive](https://arxiv.org/src/2506.05500v1)

The main reader covered all 36 physical pages of the official PDF in continuous blocks. This includes Sections 1–5, both algorithms, all displayed formulas, proofs in Appendices B–E, Appendix A limitations, footnotes, references and the NeurIPS checklist. There are no experimental figures or scientific data tables. Original PDF pages 8 and 9 were visually checked for the algorithm interface. The paper reports no experiments.

The 38-page arXiv v1 and its TeX were retrieved for provenance and targeted definition checks, but were not independently read in full or aligned against the final. A separately distributed 14-page supplemental PDF was retrieved and its opening inspected. It is not credited as another complete reading or silently substituted for the final's appendices.

The official checklist says LLMs were not an important, original or nonstandard component of the core method. This does not establish whether writing assistance was used. This is a peer-reviewed source, not an official OpenAI or Anthropic release. Full reading and the bounded deductions below are separate from independent certification of its concentration and low-degree theorems. No training reproduction or formal proof replay was performed.

## 1. Constructive result and its interface

The paper constructs a latent linear subspace from observed Gaussian covariates and labels. It pools many possible label transformations through a kernel, unfolds a Hermite tensor into a matrix, and removes same-sample products before taking a spectral decomposition. Previously recovered coordinates become extra labels for another round. Thus the construction can expose a whole interacting block before any individual first-order feature is informative.

The object learned is a real-valued subspace. It is not a finite-state transducer, an unknown transition rule, or a bounded-bit memory. Link-function estimation comes after subspace recovery. These distinctions determine which conclusions can be reused.

| Component | Source result and actual scope |
|---|---|
| Statistical interface | IID \(X\sim N(0,I_d)\), with the conditional law of \(Y\) depending on \(U^\star X\in\mathbb R^r\). The link may be stochastic. |
| Structural regime | Fixed intrinsic dimension \(r\), fixed finite Hermite orders and a fixed underlying model as \(d\) grows. |
| Population construction | A sufficiently rich PSD label kernel makes the mean matrix's range equal the next generative feature block. |
| Sampling construction | An off-diagonal matrix U-statistic estimates this population matrix with a sharp ambient-dimension exponent. |
| Iteration | Fresh data blocks, augmented labels, known leap orders and dimensions in printed Algorithm 2. An adaptive alternative is sketched in Remark 4. |
| Main upper bound | Theorem 3 states subspace error \(\epsilon\) from \(C(P,K)(d^{k^\star/2}/\epsilon+d/\epsilon^2)\) samples. A residual-coordinate interface needs to be made explicit, as discussed below. |
| Lower bound | Theorem 1 rules out weak separation by a specified low-degree class below \(d^{k^\star/2-\gamma}\). It is not an unconditional lower bound for every polynomial-time learner. |

The constants may depend badly on the link, kernels, signal eigenvalues, \(r\), and the number and orders of the leaps. A favorable exponent in \(d\) alone does not supply a uniform sample bound or a practical running time.

## 2. Which information becomes available after a feature is learned?

Write \(Z=U^\star X\sim N(0,I_r)\). For a known latent subspace \(S\subseteq\mathbb R^r\), separate

\[
\bar Y_S=(Y,\Pi_SZ),\qquad \bar Z_S=\Pi_{S^\perp}Z.
\]

Hermite tensors use the normalization

\[
h_k(z)=\frac{(-1)^k}{\sqrt{k!}}
       \frac{\nabla^{\otimes k}\gamma(z)}{\gamma(z)}.
\]

The conditional signal tensor and its second moment are

\[
\zeta_{k,S}(\bar Y_S)
=\mathbb E[h_k(\bar Z_S)\mid \bar Y_S],\qquad
\Lambda_k(S)=\mathbb E[\zeta_{k,S}\otimes\zeta_{k,S}].
\]

Let \(k(S)\) be the first positive order with
\(\mathbb E\|\zeta_{k,S}\|_F^2>0\). Starting with \(S_0=0\), the source defines

\[
S_{i+1}=S_i\oplus\operatorname{span}\Lambda_{k(S_i)}(S_i),\qquad
k^\star=\max_i k(S_i).
\]

The tensor span is its mode-one matricization's range. Minimality of the intrinsic representation ensures that a proper unfinished subspace has some remaining information. Each nontrivial leap adds a dimension, so at most \(r\) leaps are needed. The paper also gives a variational characterization over flags and rotation invariance in Proposition 1.

This differs from inspecting only the correlation with the original scalar label. The generative exponent allows all square-integrable transformations of \((Y,Z_S)\). Proposition 2 identifies it with the best information exponent after such preprocessing. Proposition 3 states \(k^\star\leq l^\star\), where \(l^\star\) is the information leap exponent.

The density-ratio expansion in Lemmas 1–2 is formal when the joint law is singular. The \(\chi^2\) identity needs finite divergence. Deterministic labels do not invalidate the conditional Hermite moments, which remain square integrable by conditional Jensen. It would be incorrect to infer an ordinary finite \(L^2\) density ratio for every deterministic example.

## 3. Why the kernel U-statistic finds a feature block

For one round, let

\[
\phi_k(x)=\operatorname{Mat}_{d\times d^{k-1}}h_k(x).
\]

The naive tensor estimate followed by a matrix square contains self-products
\(\phi_k(X_i)\phi_k(X_i)^\top\). Their noise can dominate before the desired threshold. The source instead uses

\[
U_n=\frac{1}{n(n-1)}
\sum_{i\ne j}\phi_k(X_i)\phi_k(X_j)^\top K(Y_i,Y_j). \tag{1}
\]

The sum contains ordered pairs. It is symmetric for a symmetric kernel, although an individual summand need not be symmetric. A sample realization need not be PSD. Its population mean is PSD.

If \(K(y,y')=\langle t(y),t(y')\rangle\), the population mean is a sum of Gram matrices for the moments
\(\mathbb E[t_a(Y)\phi_k(X)]\). A general kernel pools an infinite family through the same formula. The learner need not first choose one effective scalar label transform.

Lemma 3 assumes an integrally strictly positive definite kernel. For every direction \(v\), the quadratic form in \(\mathbb E U_n\) is the kernel energy of the conditional Hermite signal contracted against \(v\). Injectivity makes this energy positive exactly on the signal span. Compactness of its finite-dimensional unit sphere gives

\[
c(P,K)\Pi_{\rm next}\preceq \mathbb E U_n
\preceq C(P,K)\Pi_{\rm next}. \tag{2}
\]

This is a support theorem with a model-dependent gap. It does not lower-bound that gap uniformly over all nonzero signals.

### Concentration and iteration

Theorem 2 states that, for PSD \(K\) with \(K(y,y)\leq1\),

\[
n\gtrsim_k \frac{d^{k/2}}{\eta}
                  +\frac{dr^k}{\eta^2}
\quad\Longrightarrow\quad
\|U_n-\mathbb E U_n\|_{\rm op}\leq\eta
\]

with probability at least \(1-\exp(-d^c)\). Appendix D decouples the order-two U-statistic, controls Hermite moments and matrix variances, then applies sharp random-matrix bounds. The cases \(k=1,2\) have a separate net and subexponential argument to avoid unnecessary logarithmic losses. The resulting scale is

\[
\frac{d^{k/2}}n+r^{k/2}\sqrt{\frac dn}.
\]

Combining this with (2) and an eigenspace perturbation bound gives one-leap recovery. For further leaps, the paper replaces the label by \((Y,\Pi_SX)\), uses disjoint sample blocks, and controls the population operator's variation with a Lipschitz kernel. Lemma 4 supplies the perturbation step and Theorem 3 states the end-to-end rate in the table above.

**Required residual interface.** The definitions use \(h_k(\Pi_{S^\perp}X)\). Printed Algorithm 2 on p. 9 only augments the labels and calls Algorithm 1 on the displayed dataset, while Section 4.1 keeps the original \(\phi_i\) in its formula. It does not explicitly remove already acquired coordinates. A literal full-\(X\) call can spend its top eigenvectors rediscovering \(S\), and the displayed orthogonal direct sum then has no automatic justification.

A mathematically explicit implementation should use an orthonormal basis of \(S^\perp\), form standard-Gaussian Hermites in those residual coordinates, recover the additional block there, and lift it back. This follows the intended conditional objects. Proving its perturbation bound must account for both the changed kernel and the changed Hermite coordinate map. The printed proof is not independently certified as a proof of that amended implementation. The constructive formulas below either concern a single fixed round or condition on an acquired subspace and therefore do not rely on silently resolving this gap.

Remark 4 suggests searching increasing orders and detecting eigenvalues outside a noise bulk when leap orders and dimensions are unknown. This is a useful algorithmic idea, but it is not a complete adaptive stopping and threshold theorem with all finite-sample constants specified.

## 4. Independent construction: accumulate the statistic without all pairs

This is an exact algebraic consequence of (1), not an empirical speedup claim.

Suppose the label kernel has finite rank,

\[
K(y,y')=\sum_{a=1}^q t_a(y)t_a(y').
\]

Maintain

\[
A_a=\sum_{i=1}^n t_a(Y_i)\phi_k(X_i),\qquad
D=\sum_{i=1}^n K(Y_i,Y_i)\phi_k(X_i)\phi_k(X_i)^\top.
\]

Expanding each \(A_aA_a^\top\) separates the diagonal and yields the exact identity

\[
U_n=\frac{\sum_{a=1}^q A_aA_a^\top-D}{n(n-1)}. \tag{3}
\]

For \(q\) possible labels, the equality kernel \(K(y,y')=\mathbf1\{y=y'\}\) gives one \(A_a\) per label. It is injective on functions of that finite support, which is sufficient for the population argument. This is not a claim that the equality kernel is integrally strictly positive definite on all signed measures on \(\mathbb R\).

At \(k=1\), \(\phi_1(x)=x\). The state consists of \(q\) vectors, one second-moment matrix and the count. Standard dense arithmetic requires \(O(nd^2+qd^2)\) work for discrete-label updates and final products, plus \(O(qd+d^2)\) storage. A general dense rank-\(q\) feature map also costs \(O(nqd)\) to update. These are statistic-assembly costs, with a dense eigendecomposition costing another \(O(d^3)\).

At \(k=2\),

\[
\phi_2(x)=\frac{xx^\top-I}{\sqrt2},\qquad
(xx^\top-I)^2=(\|x\|^2-2)xx^\top+I.
\]

For discrete labels define

\[
B_a=\sum_{i:Y_i=a}(X_iX_i^\top-I),\quad
D_0=\sum_i[(\|X_i\|^2-2)X_iX_i^\top+I].
\]

Then

\[
U_n=\frac{\sum_a B_a^2-D_0}{2n(n-1)}. \tag{4}
\]

Equation (4) takes \(O(nd^2+qd^3)\) conventional dense arithmetic and \(O(qd^2)\) storage, without explicitly enumerating \(n(n-1)\) pairs. It uses exactly the source estimator, including its diagonal subtraction.

For larger \(k\), storing unfolded tensors is still costly. For a continuous infinite-rank kernel, finite-rank approximation introduces another error that (3) alone does not bound. Changing the acquired subspace changes both the augmented labels and the residual coordinates, so fixed-round accumulators cannot automatically be reused across leaps. The original fresh-block interface remains material.

## 5. Independent examples: simultaneous acquisition and feature reuse

### 5.1 A scalar label first exposes a two-dimensional block

Let \(Z_1,Z_2,Z_3\) be independent standard Gaussians, \(B_i=\operatorname{sign}Z_i\), and \(c=\mathbb E|Z_i|=\sqrt{2/\pi}\). Set

\[
Y=B_1+B_1B_2+B_1B_2B_3.
\]

Enumerating the eight sign triples gives

| \(y\) | Probability | \(\mathbb E[(B_1,B_2,B_3)\mid Y=y]\) |
|---|---|---|
| \(3\) | \(1/8\) | \((1,1,1)\) |
| \(-3\) | \(1/8\) | \((-1,1,1)\) |
| \(1\) | \(3/8\) | \((1/3,-1/3,-1/3)\) |
| \(-1\) | \(3/8\) | \((-1/3,-1/3,-1/3)\) |

Multiplying the last column by \(c\) gives \(\zeta_1(Y)\). Its span is
\(S=\operatorname{span}(e_1,e_2+e_3)\). With the equality kernel, the one-round population matrix is exactly

\[
\mathbb E U_n
=\frac{c^2}{16}
\left[e_1e_1^\top+(e_2+e_3)(e_2+e_3)^\top\right]. \tag{5}
\]

The positive eigenvalues are \(c^2/16\) and \(c^2/8\). Thus a single scalar label constructs a two-dimensional feature block.

Next let \(v=(e_2-e_3)/\sqrt2\). Once \(S\) is known, the augmented label contains \(Z_1\). The measurable transform

\[
T=\mathbf1\{Y/\operatorname{sign}Z_1=-1\}
  =\mathbf1\{B_2=-1,\ B_3=1\}
\]

has residual correlation

\[
\mathbb E[T\,v^\top Z]=-\frac{c}{2\sqrt2}\ne0. \tag{6}
\]

The last direction is therefore another first-order generative leap. Both canonical leap orders are 1. Equation (6) uses coordinates already acquired from labels to make a previously unavailable transform observable. It is an exact population calculation, not a simulation or a finite-sample certificate for the printed iterative pseudocode.

### 5.2 Parity gives a joint block and an explicit weak-signal cost

Let \(Y=\xi\prod_{j=1}^r\operatorname{sign}Z_j\), where the independent sign noise has mean \(\alpha\ne0\). All conditional Hermite moments below order \(r\) vanish. At order \(r\), tensor unfolding exposes the entire \(r\)-dimensional subspace, rather than one informative direction at a time.

For a binary equality kernel, the positive population eigenvalues are all

\[
g=\frac{\alpha^2}{2r}\left(\frac2\pi\right)^r. \tag{7}
\]

To see the constant, every distinct-index entry of the conditional normalized tensor is
\(Y\alpha c^r/\sqrt{r!}\). Each of its \(r\) nonzero matrix rows has \((r-1)!\) such entries, with disjoint column supports. Its row Gram is therefore
\(\alpha^2c^{2r}I_r/r\). The two equally likely labels contribute a further factor \(1/2\) to the equality-kernel mean.

The generative order stays \(r\) for arbitrarily small nonzero \(\alpha\), while the spectral gap decreases as \(\alpha^2\). Applying the source concentration theorem as stated gives the sufficient scale

\[
n\gtrsim_r
\frac{d^{r/2}}{g\epsilon}
\frac{d}{g^2\epsilon^2}
\]

for one-round subspace error \(\epsilon\). This is not a claim of optimal dependence on noise. It makes the hidden signal constant explicit and shows why a leap exponent alone cannot price acquisition.

## 6. Independent prediction corollary after a subspace is acquired

The source principally proves subspace recovery. Here is an explicit readout construction for noiseless degree-\(p\) polynomial labels, using the Gaussian projection argument in the [Zhang note](ZHANG-2026-GENERIC-MULTI-INDEX.md).

Assume \(Y=f(X)\) is a degree-\(p\) polynomial supported on a rank-\(r\) projector \(P\). Let \(Q\) be any learned rank-\(r\) orthogonal projector, obtained independently of the readout data, with
\(\delta=\|(I-Q)P\|_{\rm op}\). Set \(f_Q=\mathbb E[f(X)\mid QX]\).

Gaussian conditional expectation preserves polynomial degree. On the degree-\(j\) Wiener chaos it acts by \(Q^{\otimes j}\). The smallest singular value of \(Q\) restricted to \(\operatorname{range}P\) is \(\sqrt{1-\delta^2}\). Orthogonality of the chaoses gives

\[
\|f-f_Q\|_2^2
\leq [1-(1-\delta^2)^p]\operatorname{Var}(f)
\leq p\delta^2\operatorname{Var}(f). \tag{8}
\]

Take an orthonormal basis \(B_Q\) of the learned subspace and all normalized multivariate Hermites \(h_\nu(B_Q^\top X)\) with \(|\nu|\leq p\). There are
\(M=\binom{r+p}{p}\) such features. On \(N\) fresh labeled samples, estimate

\[
\widehat c_\nu=\frac1N\sum_{i=1}^N
Y_i h_\nu(B_Q^\top X_i),\qquad
\widehat f(x)=\sum_{|\nu|\leq p}
\widehat c_\nu h_\nu(B_Q^\top x). \tag{9}
\]

Conditionally on \(Q\), these are unbiased coefficients of \(f_Q\). Gaussian hypercontractivity implies

\[
\mathbb E[Y^2h_\nu(B_Q^\top X)^2]
\leq \|Y\|_4^2\|h_\nu\|_4^2
\leq 3^{p+|\nu|}\mathbb E Y^2
\leq 9^p\mathbb E Y^2.
\]

The readout basis is orthonormal, so cross-coordinate coefficient covariances do not enter its expected squared \(L^2\) error. Orthogonality of \(f-f_Q\) to every function of \(QX\) now gives the constructive bound

\[
\mathbb E_{\text{readout data},X}
[(\widehat f(X)-f(X))^2\mid Q]
\leq p\delta^2\operatorname{Var}(Y)
      +\frac{M9^p\mathbb E Y^2}{N}. \tag{10}
\]

If \(\delta\leq\delta_0\) only on a feature event of probability at least \(1-\rho\), the unconditional bound is

\[
p\delta_0^2\operatorname{Var}(Y)
\rho\operatorname{Var}(Y)
\frac{M9^p\mathbb E Y^2}{N}. \tag{11}
\]

The bad-event term uses the universal projection error bound
\(\|f-f_Q\|_2^2\leq\operatorname{Var}(f)\). The variance estimate is uniform over \(Q\). Equations (8)–(11) are independent analytic deductions, not claims that the source states these formulas.

For \(p\geq1\) and positive target variance, conditionally on the source's subspace guarantee with \(k^\star\leq2\), a target expected risk \(\varepsilon\) can use
\(\delta_0^2\) of order \(\varepsilon/(p\operatorname{Var}Y)\) and
\(N\) of order \(M9^p\mathbb E Y^2/\varepsilon\). For fixed \(r,p\), link law and kernels, the feature sample count is linear in \(d\) at a fixed accuracy. The readout stage has no additional ambient-dimensional sample factor. This statement retains the source's signal constants and unresolved iterative interface. It is not a proof about ordinary neural-network SGD, unknown polynomial degree, bounded-bit deployment, or arbitrary nonparametric labels.

Readout evaluation costs \(O(dr+M\,\mathrm{poly}(p,r))\) arithmetic with a dense basis. The basis itself occupies \(dr\) real coordinates. “Dimension-free readout sample complexity” does not mean dimension-free storage or total computation.

## 7. Lower-bound and case-study evidence

Theorem 1 first supplies the subspace preceding a hardest leap as an oracle. It then tests for additional planted structure with a Haar-random residual orientation against independent Gaussian covariates and the same augmented-label marginal. The restricted tests are low-degree in the Gaussian input coordinates, with label-dependent coefficients. For \(D=O(\log^2d)\) and \(n=O(d^{k^\star/2-\gamma})\), the projected likelihood-ratio norm tends to 1.

Appendix C expands the finite-degree likelihood ratio in conditional Hermite coefficients, controls random subspace overlap and sums admissible multi-indices. This establishes the stated low-degree obstruction under its testing interface. It does not prove a universal computational lower bound, nor a statement about all stochastic-gradient dynamics. The overall \(d^{1\vee k^\star/2}\) headline retains a linear-dimensional estimation cost when \(k^\star=1\).

The source's case studies include Gaussian parity, staircase functions, intersections of halfspaces, polynomials, continuous piecewise-linear functions and shallow networks. In particular, Proposition 4 states \(k^\star\leq2\) for polynomials and \(k^\star=1\) for staircase functions, while parity has \(k^\star=r\). Generic-coordinate claims concern almost-everywhere nonvanishing, not a quantitative lower bound on the resulting signal gap. Equations (5)–(7) provide independently derived examples of the mechanism rather than blanket certification of all case-study proofs.

One consequential proof qualification occurs in Proposition 7's additive-network argument on p. 34. It uses existence of all moments to treat polynomials as a complete \(L^2\) basis and rule out an interval on which a characteristic function vanishes. Existence of all moments alone is insufficient. For example, take nonzero \(a\in C_c^\infty(\mathbb R)\), let \(g\) be its inverse Fourier transform, and use the density \(|g|^2/\|g\|_2^2\). It has every moment, while its characteristic function is an autocorrelation of \(a\) and has compact support. It therefore vanishes on open intervals. This disproves that proof step, not the full additive-network proposition. A bounded activation, suitable exponential moments, or an explicit Fourier-overlap assumption would support the intended nonvanishing argument.

No exhaustive audit or extra proof software was developed. The most useful output remains the observable kernel construction, exact accumulation identities and explicit prediction bound.

## 8. Relationship to FP and neighboring readings

The source provides a concrete mechanism for jointly exposing a block whose individual low-order correlations vanish, and for using acquired features to define new label transformations. The relevant observation interface is IID labeled Gaussian vectors. The costs include high-order Hermite features, spectral decomposition, fresh rounds, real-coordinate storage and signal conditioning.

The [Zhang reading](ZHANG-2026-GENERIC-MULTI-INDEX.md) instead studies repeated prediction gradients as an empirical spectral filter. Equation (10) supplies a common prediction-level endpoint once either method actually returns a suitable subspace. It does not identify their acquisition algorithms or their guarantees.

No theorem here transfers directly to unknown recurrent state updates, ordinary sequential text, installed finite-bit rules, or normalization of a full-vocabulary loss. Such a transfer would need a valid replacement for Gaussian chaos, an observation-to-moment map and a separate resource analysis. No FP definition, architecture, experiment protocol or core file was changed.

Astra request 2e7a6c9 was already claimed by Pro-A at c3f5217 when this reading was archived. This note is an independently selected constructive dependency and does not take over or complete that request. Its simultaneous-block calculation is available for comparison if relevant.

## 9. Edition checksums and evidence boundary

| Asset | SHA256 | Coverage |
|---|---|---|
| Official 36-page PDF | 8c8466aac238a77712c4a6910be8c0f907f5ba9980541369e1d24b63e930e0d4 | Fully read |
| ArXiv v1 38-page PDF | 5831f63dfb0d654c362f1ecdcee134be2c3f5e195fad6a28fc515b5e475febca | Metadata and definition scope only |
| ArXiv v1 TeX archive | 2b4fa9cac468de3a8355f15e57b42288c640bbb2c79a756c7a218fba50cbc587 | Targeted comparison only |
| Separate 14-page supplemental PDF | 5ca7064b242648cdeae4929f1e61ad5e326ba72c595eaf4e29866a6c247237b4 | Opening inspected, not fully read or aligned |

The official bibliography's page range is used in preference to conflicting secondary search metadata. Prior cited papers retain their separate reading status. No novelty claim is made for the deductions in this note.
