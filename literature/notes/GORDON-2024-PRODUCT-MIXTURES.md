# Gordon et al. (COLT 2024): Identifying discrete product mixtures

## Edition and actual reading

Spencer L. Gordon, Erik Jahn, Bijan Mazaheri, Yuval Rabani and Leonard J. Schulman, **Identification of Mixtures of Discrete Product Distributions in Near-Optimal Sample and Time Complexity**, COLT 2024, *PMLR* **247:2071–2091**. [Official record](https://proceedings.mlr.press/v247/gordon24a.html) · [conference PDF](https://proceedings.mlr.press/v247/gordon24a/gordon24a.pdf).

The main reader covered **all 21 conference pages**, §§1–6, Appendix A including its continuation on p.19, Appendix B, all formulas/proofs, Algorithm 1, both numbered body footnotes, the author funding note and **37 references**. There are no figures or tables. Reliable page extraction was checked against original PDF layouts on pp.6–11, 17–21, especially the matrix products, algorithm, conditioning inequality and lower-bound calculation. This is a full reading of the reviewed conference edition, not independent certification of every theorem.

The current [arXiv record](https://arxiv.org/abs/2309.13993) lists only **v1, September 25, 2023**. Its 17-page PDF and three-file TeX package were retrieved, but the older body was **not** read or declared equivalent. The conference version rearranges the seven older sections into six main sections and two appendices and has additional references. Its first-page template says “vol196:1–21”; the official proceedings catalog supplies the bibliographic volume/pages above. The paper is not an official OpenAI/Anthropic release. No AI involvement or paper-specific formal proof was identified in the inspected edition.

## Original problem and the meaning of identification

One observation is a vector \((X_1,\ldots,X_n)\), with \(X_i\in[0,1]\), conditionally independent given a latent class \(U\in[k]\). Independent vectors are sampled repeatedly. The unknown parameters are

\[
\pi_j=P(U=j),\qquad m_{ij}=E[X_i\mid U=j].
\]

For Bernoulli coordinates, these means specify each component product law. For general bounded coordinates, the formal parameter target consists of their conditional means, not their complete conditional distributions. The number \(n\) is the number of coordinates in **one grouped observation**, not the number of sampled groups.

The observable multilinear moments are

\[
g(S)=\gamma_n(\pi,m)(S)=E\prod_{i\in S}X_i
=\sum_{j=1}^k\pi_j\prod_{i\in S}m_{ij},\qquad S\subseteq[n].
\]

The parameter error \(d_{\rm model}\) is the smallest, over a common permutation of the \(k\) classes, maximum coordinate error in \(\pi\) and \(m\). The statistical error \(d_{\rm stat}\) is the maximum absolute difference of these multilinear moments. Identification of all parameters is distinguished from merely learning the observed mixture distribution. Neither error is a bound on log loss for a longer future group.

The principal guarantee assumes a **known component count \(k\)**, \(\pi_j\ge\pi_{\min}>0\), at least \(2k-1\) informative coordinates, and, for each such coordinate,

\[
|m_{ij}-m_{ij'}|\ge\zeta>0\quad(j\ne j').
\]

This is coordinatewise separation of every pair of classes, stronger than merely having distinct joint components. The iid Bernoulli subcase has every row equal to the same vector of separated biases. At a collision, labeled weights and locations cease to be the right uniformly stable target; the discussion explicitly points toward Wasserstein recovery instead.

## Hadamard extension and spectral reconstruction

The Hadamard extension \(H(m)\) has a row for each subset of coordinates, with \(H(m)_{S,j}=\prod_{i\in S}m_{ij}\); its empty-set row is all ones. Choose disjoint \(S,T\) of size \(k-1\), with one additional coordinate labeled 1. Form two observable matrices

\[
C_{ST}=H(m[S])\operatorname{diag}(\pi)H(m[T])^\top,
\]
\[
C_{ST,1}=H(m[S])\operatorname{diag}(\pi)
\operatorname{diag}(m_1)H(m[T])^\top.
\]

Their entries are respectively \(g(A\cup B)\) and \(g(A\cup B\cup\{1\})\). The two slices form a three-way tensor. The first two factors have column rank \(k\), while separation makes the third factor have Kruskal rank 2. Their rank sum meets the \(2k+2\) uniqueness criterion, **up to permutations and factor scales** (§§2.3–3.1).

SVD projections reduce the first two factors to square matrices. With \(A=U^\top H(m[S])\), \(B=V^\top H(m[T])\), and projected slices \(\bar C,\bar C_1\),

\[
\bar C_1\bar C^{-1}=A\operatorname{diag}(m_1)A^{-1},
\qquad
\bar C_1^\top(\bar C^\top)^{-1}
=B\operatorname{diag}(m_1)B^{-1}.
\]

The common distinct eigenvalues align the two sets of columns. Once **their scales are fixed**, linear systems recover the weights and remaining rows:

\[
A\pi=U^\top(g(R))_{R\subseteq S},
\quad
A\operatorname{diag}(\pi)m_i^\top
=U^\top(g(R\cup\{i\}))_{R\subseteq S},\quad i\notin S.
\]

The analogous equations with \(T\) recover the other coordinates. This separates observable moment acquisition, tensor factorization and parameter reconstruction.

## Stated upper bound and its proof dependencies

Theorem 13 supplies the main new conditioning estimate, in the bounded-mean model:

\[
\sigma_k(H(m))>
\frac1{\sqrt{k}}\left(\frac{\zeta}{2\sqrt5}\right)^{k-1}
=:\sigma,
\qquad
\sigma_k(C_{ST})>\pi_{\min}\sigma^2.
\]

The proof introduces the minimum normalized action of \(H(m)\) on rank-one tensor test vectors. An annihilating product test kills \(k-1\) columns, relating this quantity to the least singular value with a factor \(\sqrt{k}\). A rowwise exclusion argument leaves at least one surviving column and bounds its product from below. The product factorization then controls \(C_{ST}\). The printed first part says rows in \(\mathbb R^k\), but its argument uses \(0\le m_{ij}\le1\); that domain restriction must accompany reuse.

Theorem 10 asserts that, for \(0<\varepsilon<\zeta/2\), moment error below

\[
\varepsilon\,\pi_{\min}^{O(1)}\zeta^{O(k)}
\]

permits parameter error below \(\varepsilon\), with stated post-input runtime \(\exp(O(k))\). A nearby **same-\(k\)** valid model is also asserted to have nearby parameters even if it is not itself assumed separated. This does not compare arbitrary model orders or add positive-weight overfitted classes.

Corollary 11 obtains, with confidence \(1-\delta\), the group-sample bound

\[
\zeta^{-O(k)}\pi_{\min}^{-O(1)}\varepsilon^{-2}\log(1/\delta).
\]

Each sample supplies all its subset products; concentration and a union bound control their empirical means. Appendix A combines numerical SVD perturbation, Weyl's inequality, bounded condition numbers for projected factors, a robust tensor-decomposition input attributed to Bhaskara et al. (2014), and standard linear-system perturbation bounds attributed to Higham. The diagonalization implementation is attributed to Banks et al. (2020). Those external papers/books were not read in full here, and their invocation is not an independent certificate.

For \(n>2k-1\), Corollary 12 states an additional \(\log n\) sample factor, and runtime \(n\exp(O(k))\) if a suitable subset is known or \(n^{2k}\exp(O(k))\) if it must be found. Its proposed unknown-subset procedure enumerates subsets and selects by moment fit. The proof's application of Theorem 10 to the selected subset does not establish that this subset inherits the true separation condition; that selection argument was **not certified** in this reading. A stable known-subset statement and the printed selector should not be conflated.

The quoted runtimes are the paper's statements. They are not a full accounting of retained bits, training storage, numerical word precision or installed predictor memory.

## Stated lower bound and what near optimality means

Theorem 17 takes \(n=2k-1\), \(\zeta\le1/(8k)\), \(\pi_{\min}\le1/(4k)\), and

\[
0<\varepsilon<\min\{\pi_{\min}/(4\sqrt{k}),\zeta\}.
\]

It constructs two separated models more than \(\varepsilon\) apart in parameter distance while their moment distance is at most \((k\zeta)^{\Omega(k)}\varepsilon\). Corollary 18 states a necessary sample order

\[
(k\zeta)^{-\Omega(k)}\varepsilon^{-1}.
\]

The proof changes weights along an almost-null direction of \(H(m)\), corrects their sum to one, and uses separation to prevent relabeling from hiding the change. An equally spaced iid Bernoulli construction supplies an ill-conditioned Vandermonde structure. Inclusion–exclusion converts moment distance to total variation at cost at most \(2^{2n}\), after which a two-point testing argument gives the sample lower bound.

The claimed upper/lower comparison concerns exponential dependence on separation and component count, with conditions on \(\pi_{\min}\). The displayed bounds have **different accuracy powers**, \(\varepsilon^{-2}\) and \(\varepsilon^{-1}\). They also leave a gap near maximal feasible separation: for \(\zeta=\Theta(1/k)\), the text compares \(\exp(O(k\log k))\) to \(\exp(\Omega(k))\). Thus the title does not establish a sharp joint minimax rate in every parameter. A literal exponent problem in the stated Vandermonde lemma is recorded below.

## Bounded independent checks and source limitations

### Eigenvector scale is missing from the printed algorithm

Algorithm 1, lines 5–6, only sorts eigenvectors by eigenvalue. It does not specify their scales. If the two returned matrices are \(AD_S\) and \(BD_T\), for nonsingular diagonal matrices \(D_S,D_T\), line 7 returns

\[
\widetilde\pi=D_S^{-1}\pi.
\]

The scales cancel in line 8, but line 9 returns \(m_iD_T^{-1}D_S\). Absorbing \(\pi\) into the tensor's third factor does not remove these two independent freedoms. Even ordinary unit-norm eigenvectors need not give a probability vector in line 7.

For example, take \(k=2,n=3\), \(\pi=(1/2,1/2)\), \(m_1=m_2=(0,1)\), \(m_3=(0,1/2)\), and \(S=\{2\},T=\{3\}\). All rows are at least \(1/2\)-separated. With unit-norm eigenvectors and signs chosen to make the lifted empty-set coordinate positive, the printed algorithm gives, in the original class order, \(\widetilde\pi=(1/2,\sqrt2/2)\) and \(\widetilde m_2=(0,\sqrt{10}/4)\). Both differ from the truth despite exact statistics. The bounded algebra was independently checked, with one temporary numerical calculation agreeing; no persistent audit program was introduced.

A direct noiseless correction is to lift each projected eigenvector through its orthonormal SVD basis and divide by the lifted **empty-set coordinate**, which must equal one in a true Hadamard column. Apply this separately on both sides, then align by eigenvalue. This restores the displayed noiseless linear systems. It is a bounded algebraic repair, **not** an independently completed noisy perturbation proof with the paper's sample constants.

Theorem 23's adapted statement similarly says eigenvectors approximate factor columns up to permutation, omitting scale. A tensor permits reciprocal rescaling of its factors, so that conclusion requires an explicit normalization convention. This observation concerns the paper's transcription/use, not a checked refutation of the original Bhaskara theorem.

### Lemma 27's printed exponent fails in a small exact case

The lemma on p.20 asserts existence of a separated \(m\) with

\[
\sigma_k(H(m))\le n2^n(k\zeta)^k.
\]

Take \(k=2,n=3,\zeta=1/1000\). In the paper's coordinatewise separation setting, the empty-set row and any one singleton row form

\[
Q=\begin{pmatrix}1&1\\a&b\end{pmatrix},
\quad a,b\in[0,1],\quad |a-b|\ge\zeta.
\]

Then \(\sigma_2(Q)=|a-b|/\sigma_1(Q)\ge\zeta/2\), since \(\|Q\|_F\le2\). Adding rows increases the minimum eigenvalue of the column Gram matrix, hence \(\sigma_2(H(m))\ge0.0005\). The printed upper bound is \(96\zeta^2=0.000096\). This contradicts the literal existential lemma, not merely the performance of one proposed construction.

The proof itself first obtains a term proportional to \(\zeta^{k-1}\), then replaces it by a bound proportional to \(\zeta^k\) without justification. It also uses \(n\) Vandermonde rows even though subsets include degree \(n\), requiring degrees \(0,\ldots,n\). A corrected exponent of order \(k-1\) can preserve qualitative exponential ill-conditioning; it does not validate the printed inequality. The broad lower-bound mechanism is therefore distinguished from this false intermediate formula.

A bounded independent repair uses the same equally spaced biases and a unit vector annihilating degrees \(0,\ldots,k-2\). Directly bounding the remaining subset rows gives

\[
\sigma_k(H(m))\le\sqrt{k}\,2^{n/2}
((k-1)\zeta)^{k-1}\le n2^n(k\zeta)^{k-1},
\qquad k\ge2,\ n\ge k-1.
\]

Theorem 17's qualitative moment-distance construction can be repaired even more directly. Put \(r=k-1\), \(M=\max_j\binom rj\), and \(v_j=(-1)^{r-j}\binom rj/M\), for \(j=0,\ldots,r\). Then \(\sum v_j=0\), \(\|v\|_\infty=1\), \(\|v\|_1\le k\), and its moments through degree \(r-1\) vanish. With \(\pi_j=1/k\), \(\pi'_j=1/k+2\varepsilon v_j\), the theorem's assumptions preserve all weights above \(\pi_{\min}\). Identity matching has weight error \(2\varepsilon\); other permutations move a mean by at least \(\zeta>\varepsilon\). Writing \(t=k\zeta\le1/8\), the remaining moments satisfy

\[
d_{\rm stat}\le2k t^{k-1}\varepsilon
\le t^{k/6}\varepsilon,\qquad k\ge2.
\]

Thus the false intermediate exponent does **not** refute Theorem 17's qualitative existential conclusion. This local construction was checked algebraically; its coarse constants were not claimed to independently establish all of Corollary 18 after the total-variation conversion.

### Domain and typographical boundaries

Theorem 13 cannot be imported for arbitrarily large real means solely because its first clause writes \(\mathbb R^k\). For \(k=2\), \(m=(M,M+\zeta)\) has fixed separation but \(\sigma_2(H(m))\to0\) as \(M\to\infty\). The actual probability model already restricts means to \([0,1]\).

Appendix B prints \(\sum_j\widehat\pi_j=0\), although its own mass-preserving perturbation gives 1. The construction, not the final printed digit, determines the intended normalization. These directly inspected issues do not amount to a rejection of all identifiability results in the paper.

## Evidence, open questions and use boundaries

This is a theoretical paper; it reports no empirical benchmark or replication package. Its useful structural contribution is a separation-dependent condition-number bound tied to an explicit observable tensor decomposition. The discussion leaves weaker identifiable-model conditions, distribution learning with comparable complexity, transportation-distance recovery for general product mixtures, and typical-case improvements open. Generic groups may need only roughly \(2\log_2k+1\) coordinates, but that is distinct from the stated worst-case \(2k-1\) guarantee.

Relevant cited dependencies are Kruskal's uniqueness theorem, Leurgans/Bhaskara spectral decomposition, earlier Hadamard-extension work, and sparse-moment recovery without separation by Li et al. and Fan–Li. Their citation roles were read; their entire originals were not.

For the project's finite-prototype question, the directly shared objects are latent finite classes, ordinary independent groups and multilinear moments. The source does **not** provide an adaptive-reset learning theorem, a no-separation collision rate, total future-group KL control or a charged finite-bit installation theorem. No new FP theorem or architectural recommendation is inferred. A separate recent revision, Wei–Mukherjee–Nguyen2304.10052v2, is retained to examine the Wasserstein/no-separation question on its own terms; its initial screening is not a full reading.
