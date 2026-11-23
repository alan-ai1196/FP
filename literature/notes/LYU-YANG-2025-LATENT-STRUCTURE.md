# Identifiability and Estimation in High-Dimensional Nonparametric Latent Structure Models

## Source, edition and actual coverage

Yichen Lyu and Pengkun Yang, Tsinghua University. Main source: [arXiv:2506.09165v2](https://arxiv.org/abs/2506.09165v2), uploaded August 5, 2025 at 11:00:10 UTC; the PDF cover is dated August 6. [Versioned PDF](https://arxiv.org/pdf/2506.09165v2) and [complete source archive](https://arxiv.org/src/2506.09165v2). The separate [COLT 2025 proceedings record](https://proceedings.mlr.press/v291/lyu25a.html), PMLR 291:3879–3880, is a **two-page extended abstract**, not the full proof manuscript. Its footnote points to v1; this note's full-paper analysis is of v2.

**Fully read November 24, 2026, Shanghai:** all 36 author-version pages, §§1–5, Appendices A–D, every statement and proof, both algorithm boxes, the two panels of Figure 1, two title acknowledgements/thanks and all 48 printed references. The main reader covered the opening PDF text and the complete continuous TeX body through source line 1836, including the compiled bibliography. The six-file source archive contains no separate supplementary proof document or experiment program. There are no tables or numbered body footnotes. The actual PDF layouts on pp. 7–10, 18, 20, 24, 26, 32, 34 and 36 were checked for the principal formulas, algorithm conventions and figure. The separate two-page proceedings text, its footnote and all ten references were also read. Its broad claims do not independently supply the omitted proofs.

Local sources are under `literature/corpus/pisf_prior_art/2506.09165v2/` and `PMLR-v291-lyu25a/`. Source collection and two narrowly specified exact calculations were assisted; the paper's body and proofs were read by the main assistant. Reading is complete; **the quantitative theorems are not independently certified**. Several literal statement/proof problems, including one minimax counterexample, are separated below from the authors' intended results. No formal proof replay or experimental replication was performed.

## 1. Original problem and model

The observed law is a finite mixture of product distributions,

\[
P=\sum_{k=1}^m\pi_k\bigotimes_{j=1}^d P_{kj},
\qquad \pi_k>0,\quad\sum_k\pi_k=1.
\]

The number of components **m is known and fixed**, with m at least two. Conditional on one latent component, the d coordinates of an observation are independent. Statistical data consist of n independent **whole d-dimensional observations**. Both the component laws and weights are unknown. Identifiability means that another m-component product-mixture representation of the same joint law has the same weights and coordinate laws under one common permutation of component labels.

The authors separate three questions: uniqueness from the exact joint law; stability of component recovery from an approximate joint density; and estimation of that joint density from samples. These questions have different hypotheses and losses. A fourth contribution is an operator version of simultaneous diagonalization for recovering component densities.

Two important submodels explain why coordinatewise full linear independence is too demanding. In the conditional iid model, all coordinates within a component have the same law, so observations are groups of repeated draws from a randomly selected distribution. In a Bernoulli product mixture, each coordinate law lies in a two-dimensional vector space; three or more component laws at one coordinate can never be linearly independent. Distinct laws at several coordinates can nevertheless create independent product blocks. The paper studies that source of identifiability, rather than assuming a full-rank single-coordinate representation.

The unknown mixing measure here has at most the prescribed finite number of atoms. There is no unrestricted distribution over Bernoulli biases, variable or adaptively selected group length, reset action, recursive finite-state learner, charged parameter storage or total future-horizon log-loss objective in the model. These are scope statements, not objections to the original question. [§§1–1.2, pp. 1–3.]

## 2. Identifiability through grouped Kruskal ranks

### 2.1 Definitions and exact statement

For coordinate j, let \(r_j=\operatorname{Ind}_P(j)\) be the largest integer such that **every** subset of that many component measures is linearly independent. This is Kruskal rank, rather than ordinary rank. For a coordinate block S define

\[
\tau_P(S)=\min\left\{m,\ \sum_{j\in S}r_j-|S|+1\right\}.
\]

**Theorem 7:** if there is a partition into three coordinate blocks \(S_1,S_2,S_3\) for which

\[
\tau_P(S_1)+\tau_P(S_2)+\tau_P(S_3)\ge 2m+2,
\]

then the m-component model is identifiable. The converse part constructs a nonidentifiable model for which every such sum is at most \(2m+1\). This is an **existence/sharpness construction**; it does not say that every model failing the displayed sufficient condition is nonidentifiable.

Corollary 8 follows by using at least \(2m-1\) coordinates at which the m component laws are pairwise distinct. Probability normalization makes two distinct probability measures linearly independent, so each such coordinate has Kruskal rank at least two. Group sizes \(m-1,m-1,1\) then give the required three-way ranks. Full coordinatewise independence is a stronger sufficient case, not a prerequisite for this corollary. [§2, pp. 3–6.]

The prose immediately following Definition 5 should be interpreted carefully: \(r_j=1\) only requires a dependent pair, hence a repeated law; it does not force all m laws to coincide. Pairwise distinctness gives \(r_j\ge2\), not necessarily equality. These wording issues do not prevent the sufficient argument above.

### 2.2 Proof structure

The proof first dominates all true and competing coordinate measures by a finite sum measure. Their Radon–Nikodym densities are bounded and therefore belong to the relevant L2 spaces. This step accommodates both discrete and continuous components and avoids requiring a common Lebesgue density for the identifiability theorem. Finite tensor products of these Hilbert spaces identify with L2 of the corresponding product measure.

For vectors in a Hilbert space, the Kruskal rank of the vector family equals the Kruskal rank of its Gram matrix. The Gram matrix of a block of product vectors is the entrywise product of the coordinate Gram matrices. **Lemma 9** proves, for positive semidefinite Gram matrices with nonzero diagonal,

\[
k_{A\circ B}\ge\min\{m,k_A+k_B-1\}.
\]

The proof factors A and B into Gram vectors. A zero quadratic form for their entrywise product becomes a zero Frobenius norm of a sum of rank-one matrices. Projections isolating independent vectors force its coefficients to vanish. Applying this argument to principal submatrices gives the general Kruskal-rank bound; iteration produces each block's \(\tau_P(S)\).

The three block families then satisfy the imported Hilbert-space Kruskal uniqueness theorem, cited as Theorem 5.1 of Vandermeulen–Saitenmacher (2022). Tensor uniqueness initially allows a common permutation and scaling factors. Integrating the probability densities fixes those factors and the mixture weights; marginalization recovers individual coordinate measures. Appendix A supplies the measure/tensor identifications, Gram-rank argument and complete proof. The cited 2022 paper was not separately fully read in this task.

### 2.3 Sharpness construction and a normalization repair

Appendix A uses alternating binomial weights on two interlaced sets of Bernoulli biases. Finite differences annihilate all polynomials of degree at most \(2m-2\), so those two mixing laws have the same distributions for groups of that length. Additional coordinates can be made uninformative. The argument establishes a worst-case obstruction below the stated dimension threshold.

The printed construction on p. 18 has concrete formula errors. Each parity class of coefficients \(\binom{2m-1}{j}\) sums to \(2^{2m-2}\), whereas the displayed denominator is \(2^{2m-1}\); each purported mixing law therefore has mass one half. One displayed competing product has a different dimension, and the polynomial expansion drops a binomial factor and the initial power of the bias. A proper version takes, with \(N=2m-1\),

\[
\nu_E=2^{-(N-1)}\sum_{j\ {\rm even}}\binom Nj\delta_{j/N},
\qquad
\nu_O=2^{-(N-1)}\sum_{j\ {\rm odd}}\binom Nj\delta_{j/N}.
\]

For every polynomial p of degree less than N, \(\int p\,d(\nu_E-\nu_O)=0\), by the Nth finite-difference identity. Every specified ordered binary word of length \(N-1\) has a probability of that form. Its count-class probability additionally has a binomial multiplicity; the two quantities must not be confused. A main-text display on p. 4 inserts that count multiplicity into the probability of a single word.

The corrected parity construction was checked independently with exact rational arithmetic for m=2,3,4,5, including all 340 ordered words. The checks are finite examples of the corrected identity, not a certification of every theorem in the paper.

| m | Group length | Words individually checked | First unequal moment order | Even minus odd moment at that order |
|---|---:|---:|---:|---:|
| 2 | 2 | 4 | 3 | −1/18 |
| 3 | 4 | 16 | 5 | −3/1250 |
| 4 | 6 | 64 | 7 | −45/470596 |
| 5 | 8 | 256 | 9 | −35/9565938 |

In general the last column is \(-N!/(2^{N-1}N^N)\). Both normalized laws have mass one, their moments through order N−1 agree, and the total probabilities of the enumerated words are one. Reproducible scripts and complete rational outputs are in the ignored `finite-checks/` source subdirectory; the construction and conclusions needed to reproduce them are recorded here.

## 3. Quantitative component recovery

### 3.1 What Theorem 12 claims

Definition 10 calls a family μ-incoherent when the absolute normalized inner product of every distinct pair is at most \(\mu<1\). Assumption 11 requires this at every coordinate, square-integrable component densities, and true mixture weights at least \(\zeta>0\). Theorem 12 additionally assumes support \([0,1]^d\), a proper m-component product-mixture estimate \(\widetilde f\), and a common upper bound C≥1 for every true and estimated coordinate density.

Put \(L_m=4m^{3/2}(m-1)!\). The theorem states that if

\[
\|f-\widetilde f\|_2\le\varepsilon
<\frac{(1-\mu)^{2m-1}\zeta^2}{32m^{5/2}L_m^2 C^{2m}},
\]

then one permutation σ satisfies

\[
\|f_{kj}-\widetilde f_{\sigma(k)j}\|_2
\le \frac{8C^2L_m}{(1-\mu)^{m-1}\zeta}\varepsilon,
\quad
\|\pi-\sigma(\widetilde\pi)\|_2
\le \frac{16C^{2m-2}L_m^2}{(1-\mu)^{3(m-1)/2}\zeta}\varepsilon.
\]

The printed statement omits **d≥2m−1**, although both the main proof sketch and Appendix B select that many coordinates. These displayed constants and hypotheses are recorded as the authors' claim, with the qualifications below. Incoherence and a lower weight bound are quantitative separation conditions; qualitative uniqueness alone gives no uniform favorable conditioning.

### 3.2 Four stages of the proof

Marginalizing on a unit-volume cube contracts the L2 error. After contracting one coordinate against a unit test function w, the tensor becomes a finite-rank operator

\[
T_w=A\,\operatorname{diag}(\pi_k\langle w,f_{k1}\rangle)\,B^*,
\]

where A and B collect product densities on two blocks of m−1 coordinates. Quantitative Kruskal/Gram bounds aim to keep those block operators well conditioned. Weyl's inequality transfers small operator perturbations to small singular-value perturbations. The ordinary operator norm is bounded by the Hilbert–Schmidt/L2 norm; these norms are not in general equal, despite some equalities in the text.

1. **Coordinatewise closeness.** A Gaussian projection argument produces a test function orthogonal to one estimated density but bounded away from orthogonality to every true density, if that estimate is separated in angle from all true candidates. The true contraction then has rank m while the estimated one has rank at most m−1, contradicting closeness.
2. **A bijection at each coordinate.** If two estimates correspond to one true component, a second contraction gives an m−1 versus m−2 rank discrepancy.
3. **One common permutation.** If two coordinatewise permutations disagree, contractions remove different estimated components but the same true component. A third contraction and the remaining product blocks aim to distinguish the ranks.
4. **Weights.** The first m−1-coordinate marginal is a well-conditioned linear combination of recovered product densities; perturbing this linear system yields the weight bound.

Appendix B's Gaussian lemma, quantitative Hadamard/Kruskal lemma, angle-to-normalized-density lemma and singular-value inequalities support these stages. This is a useful architecture to understand, but the literal calculation is not a checked uniform theorem here.

### 3.3 A precise omitted-dimension counterexample

For m=2,d=1, put \(h(x)=2x-1\) on [0,1] and take equal weights with

\[
f_\pm=1\pm\tfrac12h,\qquad
\widetilde f_\pm=1\pm\tfrac14h.
\]

All four functions are strictly positive densities, bounded above by 3/2. Both mixture densities equal 1 identically. The within-pair normalized inner products are 11/13 and 47/49, respectively, so a common incoherence bound μ=47/49<1 is available. Yet the best permutation leaves every matched component at L2 distance \(\sqrt3/12\); the cross-matching distance is \(\sqrt3/4\). Exact polynomial integration independently reproduced these values.

Thus zero joint error does not imply zero component error under the **literal** printed conditions of Theorem 12. Adding the dimension condition excludes this example. It is not a counterexample to a theorem that explicitly assumes d≥2m−1.

Two further proof details prevent treating the exact constants as established by this reading. The p. 8 sketch prints a reciprocal conditioning factor relative to the appendix; the factorial bound subsequently asserted does not follow with those constants from the displayed denominator in Lemma 23. In the common-permutation step, the choice \(w=f_{23}/\|f_{23}\|_2\) does not ensure positive inner products with all remaining component densities: incoherence permits orthogonality. A constant test function may repair that local choice for probability densities, but this note does not claim a complete repaired theorem or recalculated constants.

## 4. Joint-density minimax estimation and a limitation of the printed lower bound

### 4.1 Losses, class and claimed rates

Theorem 13 concerns all mixtures of m product densities whose one-dimensional factors are q-Hölder with constant L>0. For q=ℓ+β, β in (0,1], the ℓth derivative is β-Hölder. The class in (11) permits simplex weights and does **not** impose Assumption 11, incoherence or separated components. Let

\[
R_\rho^*(m,d)=\inf_{\widehat f}\sup_f E_f[\rho(\widehat f,f)^2].
\]

Here \(H^2(f,g)=\int(\sqrt f-\sqrt g)^2\), and TV is half the L1 distance. The **claimed** rate bounds are:

| Risk | Printed lower bound | Printed upper bound | Range |
|---|---|---|---|
| Squared Hellinger | \(d(n\log n)^{-q/(q+1)}\) | \(d\,m^{q/(q+1)}n^{-q/(q+1)}\) | \(n\ge m d^{1+1/q}\) |
| Squared TV | \((n\log n)^{-2q/(2q+1)}\) | \(m^{2q/(2q+1)}d^{(2q+2)/(2q+1)}n^{-2q/(2q+1)}\) | all n≥1 as printed |

Implicit constants are stated to depend on L,q. Even if the bounds applied, the TV pair would establish near-matching n-exponents for fixed m,d, rather than matching dimension dependence. Hellinger/TV joint-density control also does not directly supply the L2 premise of Theorems 12 or 14. An additional bridge or an L2 estimator is required.

### 4.2 Entropy proof route

Appendix C builds mixture covers from univariate covers and a simplex cover. TV uses telescoping product differences; squared Hellinger uses product affinities and mixture convexity. A Gilbert–Varshamov construction supplies separated arrays for packing bounds. For part of the TV lower construction, components are put on disjoint support intervals; retaining the original fixed smoothness constant under that restriction requires care, especially for small L. The Hellinger lower bound instead uses a product-density subfamily, a KL-covering comparison and the Yang–Barron entropy method.

The stated Hellinger entropy has exponent 2/q, while the TV entropy has exponent 1/q. Optimizing squared approximation error plus covering entropy divided by n yields the corresponding proposed n-rates. The imported univariate Hellinger entropy is pivotal; it is not a consequence of conditional independence alone.

There are literal transcription/algebra issues in Appendix C. Proposition 29 defines N and M as **cardinalities**, then uses them where the entropy equations require their logarithms; later manipulations revert to logarithms. One upper-bound optimization line drops 1/n. The last TV lower-bound lines do not match the TV exponent of Theorem 13. These are recorded without promoting every displayed lower bound to an independently verified rate.

### 4.3 Independent counterexample to the stated Hellinger lower bound

This objection concerns the quantifiers actually printed in Theorem 13 and Definition 26, not a conjectured corrected version. Take q=1, L=1/2, d=1 and any fixed m≥2. A mixture of L-Lipschitz densities is itself an L-Lipschitz density, so **the entire stated mixture family** satisfies the following uniform bound. It is not merely an easy subfamily.

For any such density f, integration of \(f(y)\le f(x)+L\) gives \(f(x)\ge1-L=1/2\). Partition [0,1] into J equal bins, let \(p_j=\int_{I_j}f\), and use the ordinary density histogram \(\widehat f_J(x)=J N_j/n\) on bin j. The histogram is nonnegative and integrates to one. Writing \(f_J=Jp_j\) on each bin, Lipschitz continuity and binomial count variances give

\[
\|f-f_J\|_2^2\le L^2/J^2,
\qquad
E\|\widehat f_J-f_J\|_2^2
=\frac Jn\sum_jp_j(1-p_j)\le\frac Jn.
\]

The bias and centered random error have zero cross term. Also,

\[
H^2(\widehat f_J,f)
=\int\frac{(\widehat f_J-f)^2}{(\sqrt{\widehat f_J}+\sqrt f)^2}
\le2\|\widehat f_J-f\|_2^2.
\]

Choosing \(J=\lceil n^{1/3}\rceil\) therefore gives a uniform squared-Hellinger minimax **upper bound O(n^{-2/3})**. The claimed lower bound for these same fixed L,q,d is a positive constant times \((n\log n)^{-1/2}\), for n≥m. Their ratio tends to zero:

\[
\frac{n^{-2/3}}{(n\log n)^{-1/2}}
=n^{-1/6}\sqrt{\log n}\longrightarrow0.
\]

Consequently the Hellinger lower bound is false **with its stated unrestricted L>0 and d quantifiers**. Constants depending on the fixed L,q cannot remove the asymptotic contradiction. This does not refute the qualitative identifiability result, the displayed slower Hellinger upper bound, or every possible regime allowing densities near zero. It also does not establish a replacement theorem for arbitrary m,d,q,L.

### 4.4 Narrow primary dependency check

The paper twice cites equation (32.56) of Polyanskiy–Wu's *Information Theory: From Coding to Learning* for Hellinger entropy. The [MIT author page](https://people.lids.mit.edu/yp/homepage/papers.shtml) links a [free prepublication PDF](https://people.lids.mit.edu/yp/homepage/data/itbook-export.pdf). The retrieved file is the **August 16, 2024, 18:58 author draft**, 730 physical pages, not the 2025 printed book. The author page says numbering is preserved while the print edition may contain corrections.

The main reader checked only Theorem 27.14/class definition on printed p. 538, the start of §32.4 on p. 622, and pp. 624–625 including the relevant formulas, proof sketch and footnotes; corresponding physical pages are 563,647,649,650. In this draft, (32.56) is a **risk rate**; the entropy upper bound is (32.58), followed by a proposed matching packing construction. The latter requires smoothly extending densities that are arbitrarily small on a substantial region while staying in the specified Hölder class. Such an extension cannot simply be assumed for every fixed small L. The independent histogram argument above resolves the paper's literal small-L case without relying on that imported packing claim. No full-book reading, verification of the 2025 print edition, or historical density-estimation audit is claimed.

## 5. Recovery algorithm and reported experiments

### 5.1 Operator diagonalization

For d=2m−1, split the first 2m−2 coordinates into two blocks of m−1. From an estimated joint density, integrate the last coordinate to form \(\widehat T_+\), retain its first m singular directions, and form a second operator by integrating that coordinate over a measurable set A. In the exact model,

\[
T_+=F_1D_\pi F_2^*,\qquad
T_A=F_1D_{\pi,A}F_2^*,\qquad
T_AT_+^\dagger F_1=F_1\operatorname{diag}(a_1,\ldots,a_m),
\]

where \(a_k=\int_A f_{k,2m-1}\). Thus the component product densities are eigenfunctions. Compute the finite matrix of this operator in the left singular basis U, diagonalize it with eigenvectors as columns of W, reconstruct \((g_1,\ldots,g_m)=UW\), normalize and marginalize to recover the requested coordinate. Appendix D explains both the exact-density construction and its plug-in counterpart.

**Theorem 14** assumes true incoherence/weight conditions, bounded densities, \(|A|\ge\mu_0>0\), masses \(a_k\ge\delta\), and pairwise gaps \(|a_k-a_l|\ge\delta\). For joint L2 error ε below the printed radius \(\zeta(1-\mu)^m/[4(m-1)!]\), it claims a component error at most

\[
\frac{L_{C,m}\varepsilon}{\zeta^3(1-\mu)^{3m}\delta\sqrt{\mu_0}}.
\]

The good set A and its quantitative separation are substantive premises. The discrete remark replaces integrals by sums and A by random coordinate weights; almost-sure eigenvalue distinctness alone is not a uniform numerical gap guarantee. For larger d, the authors propose repeated 2m−1-coordinate subproblems. Consistent label alignment and construction of the initial joint-density estimator remain necessary operational details. The continuous statement is a functional-operator procedure, not a supplied efficient finite-sample implementation with all approximation costs bounded.

### 5.2 Literal implementation and perturbation qualifications

Algorithm 1 defines W by **columns** of eigenvectors but its reconstruction line uses row-indexed \(w_{kh}\); the exact operator derivation and Algorithm 2 use UW, which requires \(w_{hk}\). More seriously, division by \(\|g_k\|_1\) leaves the arbitrary sign of an eigenvector unchanged. Even with exact input, replacing an eigenvector by its negative can produce a negative function rather than a density. A sign/orientation convention or normalization by an appropriately signed integral must be supplied; its stability then needs an argument.

The same issue appears in **Lemma 24**, stated for arbitrary signed L2 functions: taking f=1,g=−1 gives zero sine of the angle but L2 distance two between their L1-normalized versions. Nonnegative density applications exclude that example; arbitrary eigenvectors do not. In Appendix D, the Davis–Kahan subspace estimate is also turned into an estimate between particular bases without an alignment convention. Identical subspaces with \(\widehat U=-U\) have zero principal angles but \(\|U-\widehat U\|=2\), so equation (66) is not valid for arbitrary bases as printed. These are explicit conventions/gaps in the stated algorithm and proof, not a denial that a properly oriented and aligned spectral method can work. This reading does not certify Theorem 14's exact constants or radius after repairs.

### 5.3 What Figure 1 measures

Both simulations use m=3,d=5, weights (0.2,0.3,0.5), n from \(2^{17}\) through \(2^{24}\), ten repetitions, and the empirical joint mass table as the initial estimate. The reported error is \(\sum_k\|f_{k1}-\widehat f_{k1}\|_2\); the text does not fully specify the matching convention or confidence interpretation of the displayed error bars.

| Experiment | Components | Evidence shown |
|---|---|---|
| Conditional iid, four symbols | Each coordinate uses (1/4,1/4,1/4,1/4), (0,0,1/2,1/2), or (1/2,1/2,0,0). The first is the average of the other two. | Left panel decreases roughly from 0.01 to 0.001 over the sample range, despite the single-coordinate linear dependence. |
| Bernoulli product mixture | Bias \(\alpha_{kj}=0.1j+0.2(k-1)\), j=1,…,5. | Right panel has a broadly declining error with considerable variability and a local increase; it is not a monotone error guarantee. |

The source reports means and variances in log–log plots, without an end-to-end runtime/sample-complexity benchmark, competing estimator comparison, public experiment code in this archive, or explicit random seeds. The examples support numerical feasibility in small discrete models; they do not test unknown component count, adaptive group allocation or the continuous minimax theorem. Values above are visual approximations, not extracted original run data. [§4.2 and the actual Figure 1, p. 10.]

## 6. Dependencies, unresolved points and usable scope

The central provenance is Kruskal uniqueness and its Hilbert-space extension, quantitative Khatri–Rao/Kruskal bounds, classical simultaneous diagonalization, and metric-entropy density estimation. Recent related work includes Gordon et al. (COLT 2024) for discrete product mixtures; the conditional iid threshold connects to Vandermeulen–Scott and finite-mixture/moment work. The paper also cites nonparametric EM-style estimation, grouped-sample learning and sparse Hausdorff reconstruction. Those citations were read in the bibliography and in their uses here; their complete proofs were not silently counted as read.

The full reading establishes exactly what this source proposes: flexible block identifiability for a **known finite component count**, a separation-dependent route from joint-density error to component error, entropy-based joint-density rates, and an operator recovery construction. Its clean identifiability mechanism is distinct from the quantitative and algorithmic issues above. The corrected parity construction and the d=1 component counterexample were independently checked in finite exact calculations. The histogram argument is an independent analytic objection to the printed Hellinger lower-bound quantifiers. No full theorem, formal proof system or experiment replication was independently completed.

Before using a quantitative theorem from this edition, the necessary unresolved items are the missing dimension premise in Theorem 12, consistent conditioning constants and contraction choices, a corrected Hölder/rate regime for Theorem 13, and eigenvector orientation/basis alignment in Theorem 14. These are not instructions to start an open-ended audit. A later corrected author edition or a narrowly relevant independently proved result could resolve them.

For the current repository questions, ordinary grouped observations are a concrete shared sampling format. **An unrestricted mixing law, prediction at a future length different from the training group length, causal total KL and adaptively observed reset decisions are not conclusions of this paper.** No FP theorem or architecture is imported, and no core theory or experiment file was changed.
