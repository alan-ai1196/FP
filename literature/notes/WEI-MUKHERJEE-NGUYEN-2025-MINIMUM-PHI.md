# Minimum Φ-distance estimators for finite mixing measures

## Edition, provenance and actual coverage

**Yun Wei, Sayan Mukherjee and XuanLong Nguyen.** [arXiv:2304.10052v2](https://arxiv.org/abs/2304.10052v2), revised **September 4, 2025, 02:40:34 UTC**; the first submission was April 20, 2023. [Versioned PDF](https://arxiv.org/pdf/2304.10052v2) · [TeX source](https://arxiv.org/src/2304.10052v2). This is a 2025 revision of a 2023 preprint. The current arXiv history has two versions. [Wei's news page](https://clouduolc.github.io/news.html) identifies the September 2025 update, while [Nguyen's publication list](https://dept.stat.lsa.umich.edu/~xuanlong/papers.html) lists this item without an authenticated journal/conference acceptance. Acknowledgment of referees and an associate editor is not sufficient publication metadata. No withdrawal or subsequent correction was displayed in these checked records.

**Fully read on November 24, 2026, Shanghai:** all 74 PDF pages through the complete active TeX: introduction/notation, §§2–5, acknowledgments, Appendices A–C, all statements and proof text, the one actual figure, one table, four algorithms, three numbered footnotes, and all 69 printed references. The main reader personally covered every active section and appendix. Mechanical source preparation and a separate bounded check of the multinomial example were delegated; neither replaces that coverage. The 74-entry bibliography database contains unused/duplicate records; the compiled bibliography has 69 entries, including two entries for the same Manole–Khalili paper.

The source package contains seven TeX files, `yun.sty`, the compiled bibliography and the sole figure asset. The active `\end{document}` at original `appendix.tex` line 2201 terminates the paper: later recycling/adaptive-rate drafts and 30 comment environments are excluded. Selected dense original layouts were inspected, including pp.14,22,37,44,54–55; the actual figure/table/algorithm pages 10,15,16,20,24 were viewed. Public local copies are reproducible from the versioned links; they are ignored corpus material, not separate claims of reading.

**Assessment:** the finite-mixture estimation framework and its no-separation multinomial application are valuable. A bounded independent counterexample disproves the printed local low-order raw-moment equivalence, Theorem 2.24(c)/Eq.(16), and Lemma A.10. It does not refute the earlier powered-Wasserstein inverse theorem or the multinomial identification threshold. Other proof/notation qualifications below are separated from the authors' conclusions. No full theorem certification, formal proof replay or numerical experiment replication was performed.

## Original question and statistical objects

An injectively parameterized family \(\{P_\theta:\theta\in\Theta\subset\mathbb R^q\}\) is given. A mixing measure is

\[
G=\sum_{i=1}^{k^*}p_i\delta_{\theta_i},\qquad
P_G=\int P_\theta\,dG(\theta).
\]

The observations are **independent draws from the mixture distribution**, \(X_1,\ldots,X_n\sim P_{G^*}\). The unknown object is the entire finite mixing measure, including locations, weights and its true order \(k^*\). Write \(\mathcal E_k\) for exactly \(k\) distinct atoms and \(\mathcal G_k\) for at most \(k\). Most uniform results assume a known upper bound \(k\ge k^*\), compact \(\Theta\), and the correct component family. The class itself imposes no common minimum weight or atom separation.

The loss is a Wasserstein distance on **parameter measures**. Its powered form is

\[
W_s^s(G,H)=\min_{\pi\in\Pi(G,H)}\sum_{i,j}\pi_{ij}\|\theta_i-\eta_j\|_2^s.
\]

This is different from the distance between observable distributions \(P_G,P_H\). Small observable error can coexist with much larger latent parameter error near component collisions.

For a test-function class \(\Phi\) on parameter space, set

\[
D_\Phi(G,H)=\sup_{\phi\in\Phi}|G\phi-H\phi|.
\]

“Distinguishable” means this separates all measures in the chosen finite-mixture class. “Estimatable” means that each \(G\phi\) has an unbiased single-observation statistic \(t_\phi(X)\). This is a stronger operational requirement than simply knowing the function \(\phi\).

The minimum-distance estimator minimizes

\[
\widehat G_n\in\arg\min_{G\in\mathcal G_k(\Theta)}
\sup_{\phi\in\Phi}\left|G\phi-\frac1n\sum_{j=1}^nt_\phi(X_j)\right|.
\]

Its elementary projection inequality is \(D_\Phi(\widehat G_n,G^*)\le2Z_n\), where \(Z_n\) is the supremum of the corresponding centered empirical process. The paper separates the deterministic inversion problem from bounding \(Z_n\). An arbitrary, possibly biased statistic can still satisfy this projection inequality, but its estimation error then includes the bias. Unbiasedness is what gives the useful empirical-process interpretation.

These algorithms specify exact global minimizers. They do not establish that a chosen numerical optimizer reaches them, a polynomial runtime, or an inexpensive search over mixture order. Compactness/existence arguments use continuity or lower semicontinuity of the objective; for the principal smooth examples this is available. The early abstract statements should not be applied to arbitrary discontinuous measurable \(\Phi\) without checking that regularity. The first footnote interprets nonmeasurable suprema using outer probability/expectation; it is not a constructive measurable optimization algorithm.

## Inverse inequalities, assumptions and rates

For a reference \(G_0\in\mathcal E_{k_0}\), define the overfitting index

\[
d_1=k-k_0+1.
\]

The principal inequalities are

\[
D_\Phi(G,H)\ge cW_{2k-1}^{2k-1}(G,H)
\quad(G,H\in\mathcal G_k),
\]

and, locally with **both** arguments approaching \(G_0\),

\[
D_\Phi(G,H)\ge c(G_0)W_{2d_1-1}^{2d_1-1}(G,H).
\]

Constants and neighborhood radii depend on the component family, parameter domain, order and test class; local constants also depend on \(G_0\). Compactness plus distinguishability extends the local control away from the small neighborhood and yields the global bound. These are not constants uniform over growing dimension/order or changing kernels.

Theorem 2.21 uses a weaker derivative independence condition than demanding every derivative at every possible node. In Definition 2.17, for \(\ell\in[k_0,2k-k_0]\), choose positive multiplicities with \(m_i\le m+1\) and \(\sum_i m_i\in[2k_0,2k]\). A linear combination of the derivative evaluation operators up to order \(m_i-1\), zero on every test function and satisfying \(\sum_i a_{i0}=0\), must have all coefficients zero. Functions must be \(C^m\); the boundary convention is extension to a larger domain. The constant function can be appended without changing the distance or estimator.

Taking \(m=2d_1-1\) supplies the local inverse bound; \(m=2k-1\) covers all possible reference orders. The requirement reflects the number of colliding atoms available to two \(k\)-component measures. It is therefore applicable to finite polynomial test families that cannot satisfy an unrestricted strong-identifiability definition.

If \(\mathbb E Z_n\lesssim n^{-1/2}\), the resulting global loss bound is

\[
\sup_{G^*\in\mathcal G_k}\mathbb E W_{2k-1}^{2k-1}(G^*,\widehat G_n)
\lesssim n^{-1/2},
\]

hence, by Jensen and Wasserstein monotonicity,

\[
\sup_{G^*\in\mathcal G_k}\mathbb EW_1(G^*,\widehat G_n)
\lesssim n^{-1/(4k-2)}.
\]

The local counterpart has exponent \(1/(4d_1-2)\). **An \(n^{-1/2}\) bound for the powered loss is not an \(n^{-1/2}\) bound for unpowered parameter error.**

Theorem 2.2 claims matching global/local minimax lower exponents under Assumption \(A(\theta_0,2d_1-1)\): derivatives along an admissible parameter direction have uniformly bounded square integrals divided by a neighboring component density. The local neighborhood shrinks at the asserted estimation rate. The proof splits a component into two moment-matched alternatives, cancels terms through order \(2d_1-2\), controls their product-law separation and applies Le Cam's two-point method. The alternatives need an actual parameter segment around the chosen node; a degenerate or isolated parameter domain is not justified by merely writing a derivative extension. See the proof qualifications below before importing its literal constants.

## Instances of the framework

### KS distance

For \(X\in\mathbb R^d\), take parameter functions \(\theta\mapsto F(x\mid\theta)\) over lower orthants. The observable empirical process is the multivariate KS discrepancy, with expected size \(O(\sqrt{d/n})\). Compactness, identifiable mixtures and the corresponding weak CDF derivative independence give the powered-Wasserstein bounds in Theorem 3.3. Compared with Heinrich–Kahn's univariate treatment, the paper extends both parameter and observation dimensions and weakens the derivative conditions.

The prose uses right-closed lower orthants consistently; Algorithm 2 instead prints an open endpoint for the empirical CDF. For discrete observations, those endpoints should be made consistent before implementation. They cannot be interchanged silently at an atom.

### MMD

A bounded measurable positive semidefinite kernel \(\kappa\) defines an RKHS. The paper uses \(\|\kappa\|_\infty=\sup_x\sqrt{\kappa(x,x)}\). With its unit ball as observable tests,

\[
D_\Phi(G,H)=\operatorname{MMD}_\kappa(P_G,P_H).
\]

Theorem 3.15 explicitly assumes that the kernel mean map is injective on **finite signed measures**, not just that it distinguishes probability measures. Assumption A2 permits differentiation under the integral: continuous parameter derivatives through the required order, locally integrable envelopes for lower-order difference quotients and highest-order continuity differences. The weak density derivative independence is then transferred to RKHS tests by applying injectivity to a signed derivative measure.

The empirical MMD has expectation at most \(2\|\kappa\|_\infty/\sqrt n\), and a bounded-differences tail around that scale. Algorithm 3 optimizes

\[
\sum_{i,j}p_ip_jK(\theta_i,\theta_j)-2\sum_ip_iJ_n(\theta_i),
\]

where \(K\) integrates the kernel against two components and \(J_n\) integrates it against one component and the empirical data. The data-only term is dropped. The paper supplies closed forms for Gaussian location mixtures with known common covariance and a Gaussian kernel, allowing gradients to be evaluated analytically. It defers optimization details to existing MMD work.

Kernel choice can improve applicability to non-Euclidean observations, but does not remove inverse-conditioning constants or establish a dimension-independent parameter recovery guarantee. Existing MMD papers are distinguished as principally controlling observable distributions; the contribution here is conversion to mixing-measure loss.

### Generalized and tensor moments

The polynomial test family contains all multi-index moments through **global degree \(2k-1\)**. Lemma 3.16 gives its global inverse bound and local improvement in the *Wasserstein exponent* while retaining those \(2k-1\) observable moments. Algorithm 4 projects estimated latent moments onto the valid finite-mixture moment set in the maximum norm.

The paper treats the six NEF-QVF families—Gaussian, Poisson, gamma, binomial, negative binomial and generalized hyperbolic secant—through unbiased polynomial statistics for their mean parameter. Its stated concentration shape is

\[
\Pr\{\max_{j\le2k-1}|\bar t_j-\mathbb Et_j|>u\}
\lesssim (2k-1)\exp[-c\min(nu^2,(nu)^{1/(2k-1)})].
\]

That yields \(n^{-1/2}\) expected moment error. The availability of all those unbiased statistics must be checked for the actual family and parameterization. In particular a fixed Binomial\((N,p)\) observation cannot unbiasedly estimate arbitrary-degree powers of \(p\): its expectation of any statistic is a degree-at-most-\(N\) polynomial. Thus the full degree-\(2k-1\) recipe requires \(N\ge2k-1\); the generic six-family prose does not waive the exact threshold established later.

For multidimensional Gaussians with known covariance \(\Sigma\), the unbiased order-\(\ell\) latent tensor is built from

\[
F_\ell(X)=\sum_{j=0}^{\lfloor\ell/2\rfloor}
\binom{\ell}{2j}\frac{(2j)!}{j!2^j}(-1)^j
\operatorname{sym}(X^{\otimes(\ell-2j)}\otimes\Sigma^{\otimes j}).
\]

Then \(\mathbb EF_\ell(X)=M_\ell(G)\). Conditioning on latent locations separates a Gaussian polynomial fluctuation from a bounded empirical latent-moment fluctuation. Hypercontractivity, Hoeffding and a union bound supply the asserted tensor concentration and powered-Wasserstein rates. Covariance is supplied, not jointly learned. These are statistical statements about the prescribed global minimizer, not measured recovery experiments.

## Pointwise rate and order selection

Section 4 first chooses the smallest order whose minimum residual falls below \(a_n\). For fixed \(G\), let \(b_G>0\) be its test-distance from the smaller-order model. The event of estimating the wrong order is contained in

\[
\{Z_n\ge\min(a_n,b_G-a_n)\}.
\]

The unknown gap \(b_G\) explains why order selection is pointwise rather than uniform over near-colliding/vanishing components. Threshold \(a_n\asymp\sqrt{\log n/n}\) balances eventual gap separation with empirical concentration.

A second-order derivative condition gives a one-fixed-argument inverse in \(W_2^2\) for overfitted models. When the order is correctly selected, a first-order derivative condition gives a local \(W_1\) inverse. Theorem 4.10 combines that inverse with the empirical-process error, an excursion event and the wrong-order probability. With sufficiently large threshold constants, KS and MMD examples attain fixed-model expected \(W_1\) error \(O(n^{-1/2})\). GMM needs a known upper order because that determines its finite moment family.

The general KS/MMD construction need not input a finite upper order **when its model class remains identifiable at the relevant orders**. It does not permit arbitrarily many binomial mixture components with a fixed finite trial count. No contradiction exists between fixed-model parametric rates and a slower uniform minimax rate. The constants can deteriorate as a weight vanishes or nodes collide. Compactness is essential for many overfitted inverse bounds: a tiny mass escaping far away can have bounded-test discrepancy much smaller than its transport cost.

## Multinomial example and bounded independent check

Example 5.6 uses \(q+1\) categories, a fixed count total \(N\), and the closed probability simplex. The observable alphabet has size \(S=\binom{N+q}{q}\). Here **\(N\) is trials inside one group; \(n\) is the number of independent groups**.

The author conclusion is the exact class-wide threshold

\[
\inf_{G\ne H\in\mathcal G_k}
\frac{V(P_G,P_H)}{W_{2k-1}^{2k-1}(G,H)}>0
\quad\Longleftrightarrow\quad N\ge2k-1.
\]

No common atom separation or minimum weight is imposed. The constants fix \(N,q,k\). This threshold concerns identification over the whole class; some boundary/particular distributions can be identifiable with fewer trials.

The following scoped checks support that application without certifying the full general inverse proof:

1. **Polynomial span.** For \(|\alpha|\le N\), the multinomial factorial moment identity gives
   \[
   \sum_x\frac{\prod_j(x_j)_{\underline{\alpha_j}}}
   {(N)_{\underline{|\alpha|}}}p_N(x\mid\theta)=\theta^\alpha.
   \]
   Thus count probabilities span all parameter polynomials of degree at most \(N\), including on the simplex boundary.
2. **Derivative independence.** Lemma A.8 isolates the required jets using polynomials of degree at most \(\sum_i m_i-1\le2k-1\). Fix a target node, choose one separating coordinate for every other node, multiply the corresponding factors with their prescribed multiplicities, and descend through derivative orders at the target. This establishes the weaker condition when \(N\ge2k-1\).
3. **Necessity.** Alternating finite-difference weights on \(2k\) points of a binomial edge give distinct \(k\)-atomic measures with matching moments through degree \(2k-2\). For example, at \(k=2,N=2\),
   \[
   G=\tfrac14\delta_0+\tfrac34\delta_{2/3},\qquad
   H=\tfrac34\delta_{1/3}+\tfrac14\delta_1
   \]
   both yield count pmf \((1/3,1/3,1/3)\).
4. **A concrete estimator bridge.** With \(\kappa(x,y)=1_{x=y}\), the RKHS mean is the entire finite pmf, signed-measure injectivity holds, MMD is its Euclidean distance, and all A2 conditions follow from finite polynomial coordinates. Since \(\|p-q\|_2\ge2V(P,Q)/\sqrt S\), the TV inverse also directly supplies the MMD inverse. Its empirical fluctuation is \(O(n^{-1/2})\). Consequently the stated powered-Wasserstein and \(n^{-1/(4k-2)}\) unpowered bounds apply with constants depending on the fixed problem. This deduction uses the existing inverse theorem; it is not a new full proof of that theorem.

The comparison to Manole–Khalili's stronger derivative criterion is a source claim. The older paper's alleged multinomial proof error was not independently traced, so this note does not certify that criticism.

## A substantive counterexample to the local moment equivalence

Theorem 2.24(c), Eq.(15), and the two-sided Eq.(16) on p.14 claim that a local \(\Phi\)-distance is bounded above by the difference of **global raw moments only through \(2d_1-1\)**. Appendix A.6, pp.55–58, makes that meaning explicit; it is not a vector of moments separately centered within each cluster.

Take \(q=1\), \(\Theta=[-2,2]\), \(k=k_0=2\), hence \(d_1=1\), and

\[
\Phi=\{1,\theta,\theta^2,\theta^3\},\qquad
H_\varepsilon=G_0=\tfrac12\delta_{-1}+\tfrac12\delta_1,
\]
\[
G_\varepsilon=\tfrac12\delta_{-1-\varepsilon+\varepsilon^2}
+\tfrac12\delta_{1+\varepsilon+\varepsilon^2}.
\]

For sufficiently small positive \(\varepsilon\), all nodes are in the compact domain, all weights stay \(1/2\), and both arguments converge in \(W_1\) to \(G_0\). Every derivative required in (c) is uniformly bounded/equicontinuous. The four cubic monomials also satisfy the relevant two-node first-order Hermite independence, so adding the identifiability hypothesis does not rescue the claim.

The mass difference is zero, and the first-moment difference is \(\varepsilon^2\), while

\[
m_2(G_\varepsilon)-m_2(G_0)
=(1+\varepsilon)^2+\varepsilon^4-1
=2\varepsilon+\varepsilon^2+\varepsilon^4.
\]

Therefore

\[
\frac{D_\Phi(G_\varepsilon,G_0)}
{\|\mathbf m_1(G_\varepsilon)-\mathbf m_1(G_0)\|_\infty}
\ge\frac{2\varepsilon+\varepsilon^2+\varepsilon^4}{\varepsilon^2}
\longrightarrow\infty.
\]

The denominator stays positive, so this is a direct violation of the displayed limsup, without relying on an undefined zero ratio. With the common shift removed, the first moments agree exactly although the measures differ. The tests can also be made estimatable in the paper's framework by taking a known-variance Gaussian location family and its degree-three unbiased Hermite statistics.

**Failure point:** Lemma A.10 equates global low-order moment differences with the maximum of separately centered cluster moments. Distinct clusters can cancel in the former while the latter remain order \(\varepsilon\). The reverse comparison invoked on p.56 loses that cancellation. This is a substantive counterexample to the local upper equivalence, not an interpolation typo.

The counterexample does **not** refute Theorem 2.21's local powered-Wasserstein lower bound, Lemma 3.16's use of the full \(2k-1\) moment vector, or Example 5.6. It also does not refute a suitably qualified global equivalence that retains \(2k-1\) moments. A possible corrected local characterization using sufficiently many global moments or clusterwise coordinates needs a separate statement and proof; this note does not silently replace the published theorem with one.

## Other proof and statement qualifications

These were encountered during the complete read; the list is not an exhaustive audit.

- **Lemma A.8, p.54:** its separating-coordinate example writes exponent \(d_i\) where the preceding requirement is \(d_\ell\). Also, for \(f(A)=\inf_{\|w\|_\infty=1}\|Aw\|_\infty\), the printed inequality \(|f(A)-f(A')|\le f(A-A')\) is false. For \(A_t=\left(\begin{smallmatrix}1&1\\0&t\end{smallmatrix}\right)\), \(f(A_t)=t/(1+t)\); \(t=1,2\) gives a positive difference whereas \(f(A_1-A_2)=0\). The valid operator-norm inequality \(|f(A)-f(A')|\le\|A-A'\|_{\infty\to\infty}\) restores continuity and the compact separated-configuration minimum. These repairs preserve the interpolation conclusion; they do not supply a uniform Vandermonde condition number over colliding configurations.
- **Minimax proof, pp.44–45:** it prints \(\epsilon_n=n^{-1/(2d_1-1)}\), whereas its ensuing identity \(n=\epsilon_n^{-2(2d_1-1)}\) requires \(n^{-1/(4d_1-2)}\). It also replaces TV by normalized Hellinger directly in Eq.(58), which is not generally a valid inequality. A positive tensor Hellinger affinity can instead control TV via \(V\le\sqrt{1-\mathrm{affinity}^2}\). These are repair directions for the exponent argument, not a certification of every displayed constant. A local lower-bound constant must allow dependence on the neighborhood multiplier and reference mixture; it cannot stay positive uniformly as that neighborhood multiplier tends to zero.
- **Moment-rate wording:** Remark 3.4 groups raw moment discrepancy with unpowered Wasserstein losses when stating the slow minimax rate. The preceding theorem already bounds the *raw* moment discrepancy at \(n^{-1/2}\); the slow exponent is obtained after taking the \((2k-1)\)-st root for Wasserstein loss. Do not copy the same slow rate for both quantities. The prose after Eq.(16) also redefines \(d_1\) inconsistently; throughout this note it remains \(k-k_0+1\).
- **NEF-QVF proof coverage:** the moment-boundedness argument calls every listed gamma/negative-binomial member log-concave, which is false for shape parameters below one. Its Gaussian first-absolute-moment constant independent of the mean is also only a centered expression. Compact parameter constraints can support appropriate finite constants, but those particular lines do not prove the fully advertised family range. No general repair of all six families was attempted. The binomial degree restriction above is an independent, exact condition.
- **Moment optimality proof:** Lemma B.5 states equality through degree \(2k-2\) but its displayed construction establishes only \(2d_1-2\). That is an unfilled proof step for the general local claim, distinct from the explicit counterexample to Theorem 2.24(c).
- **Normalization and implementation:** Table 1's unit sup-norm test ball gives \(2V\) under the paper's own \(V=\frac12\|p-q\|_1\) convention; indicators give \(V\). This factor does not change rates. Algorithm 2's endpoint mismatch is recorded above. These should be corrected in any implementation rather than interpreted as new statistical claims.

## Proof architecture, evidence and dependencies

Appendix A establishes finite-atomic moment identification, moment-matched perturbations and the Le Cam lower construction. The core inverse argument extracts subsequences and a coarse-grained tree of atom separation scales. Signed mass imbalances across that tree characterize transport cost. Taylor coefficients are propagated from children to parent clusters; multivariate Hermite interpolation prevents cancellation after rescaling within a separated configuration. A normalized nonzero limiting jet then contradicts weak derivative independence. Appendix A.6 adds the raw-moment geometry claim and contains the failure isolated above.

Appendix B supplies signed-measure RKHS injection criteria, Fourier arguments for location-family derivative independence, differentiation under integrals, Rademacher symmetrization, moment and tensor concentration, and the stated local moment-order optimality. Appendix C gives order-selection event inclusions, the one-fixed-argument inverse proofs, the escaping-mass example and the final risk decomposition with McDiarmid concentration.

The principal dependencies are Heinrich–Kahn (2018) for coarse-grained atom trees and minimax comparison; Wu–Yang (2020) for denoised Gaussian moments; Nguyen (2013), Ho–Nguyen and Wei–Nguyen (2022) for inverse/latent-measure context; Morris and Lindsay for NEF-QVF polynomials; Sriperumbudur–Fukumizu–Lanckriet and Gretton et al. for kernel embeddings; Pereira–Kileel–Kolda for Gaussian tensors; Schudy–Sviridenko for polynomial concentration. Their role was read as cited, without marking the cited works fully read or recursively verifying all dependencies.

There are **no empirical benchmarks or reported simulation results** in this edition. Figure 1 is a schematic empirical-distribution projection; Table 1 compares metrics, not experiments. The four algorithms are mathematical estimator specifications. No timing, optimizer-success rate, numerical conditioning study or finite-precision robustness result is supplied.

The authors leave computational choices, optimal test-class design, explicit dependence on order/dimensions, non-Euclidean mixture applications, more general divergences and parts of unknown-order uniform estimation open. A full-read status does not resolve those questions.

## Research boundary and useful follow-up

The concrete usable distinction is between **fixed finite-order count-law identification** and the conditioning cost of recovering its latent mixing law. The checked multinomial threshold and delta-kernel construction can inform a grouped-sampling reference. They do not provide an accumulated future-sequence KL bound, a learned reset rule, online recurrent-state formation, or charged finite-bit storage. Those would need explicit new objectives, assumptions and derivations.

The highest-value follow-up within this source is a corrected statement for local moment geometry and a careful accounting of constants when \(N,q,k\) vary. The finite-alphabet application can be considered separately from that defect. Recent finite-mixture/filter-learning sources remain discovery candidates; no broad historical full-reading chain is opened merely because they are cited here.
