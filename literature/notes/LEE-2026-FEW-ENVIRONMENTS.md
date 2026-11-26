# Lee, Jin and Aragam — constructive recovery from unknown knockout environments

## Edition and actual coverage

Inbeom Lee, Tongtong Jin and Bryon Aragam, *Beyond identifiability: Learning causal representations with few environments and finite samples*.

- [arXiv 2603.25796v1 record](https://arxiv.org/abs/2603.25796v1), submitted March 26, 2026 at 18:03:57 UTC.
- [Fourteen-page v1 PDF](https://arxiv.org/pdf/2603.25796v1). The manuscript title page says March 30, 2026.
- [Exact v1 TeX archive](https://arxiv.org/src/2603.25796v1).

Pro-D personally read all 14 available PDF pages on November 27, 2026, Shanghai time, including Sections 1–5, every displayed statement and formula, and the references. The active TeX was checked for the model, reconstruction claims, estimator definitions, assumptions and rates. Original page 8 was inspected visually, including the absolute-value bars in Equation 13. There are no figures, tables, algorithm blocks, appendices or supplied theorem proofs in this edition. References to technical results or proofs do not supply those missing materials.

This is a complete reading of the available manuscript, not a reading or verification of unavailable proofs. A directed publication check found related talk abstracts, but did not authenticate a separate peer-reviewed final. No later arXiv version was listed at the checked record. Experiments mentioned in a talk abstract are not experiments present in this v1.

SHA256:

- PDF: fe33958aecdf5829e57e7b4867adf09a8025f899bd6f9c97b56a84122759dd06.
- TeX archive: f64479edca03e56b8383b96228de1116420528ebcad8a080175f6b4864468ea2.

No training experiment, implementation audit or formal verification was performed. Sections 3–6 below contain independent analytic constructions from the source model, with no novelty claim. No explicit AI-assistance disclosure was found in the read manuscript. Actual use is undetermined.

## 1. The information interface is exact knockout plus noiseless mixing

The source's linear model is

\[
Z^{(k),\ell}=(A^{(k)})^\top Z^{(k),\ell}+\nu^{(k),\ell},
\qquad X^{(k),\ell}=BZ^{(k),\ell}.
\tag{1}
\]

The full-column-rank matrix \(B\in\mathbb R^{p\times d}\) is shared. The directed graph of \(A\) is acyclic. Noise coordinates are independent. There is no additive measurement noise in \(X\).

An intervention on the unknown set \(I_k\) zeros both the corresponding columns of \(A\) and the corresponding diagonal noise variances. With the stipulated centering, every intervened coordinate satisfies \(Z_j=0\) almost surely. This is stronger than severing incoming edges while retaining exogenous noise. It is also stronger than an arbitrary soft intervention.

Write \(S_k=[d]\setminus I_k\), with observational environment \(k=0\). When the remaining noise variances are positive,

\[
U_k:=\operatorname{col}(\Sigma_X^{(k),\ell})
 =\operatorname{span}\{b_j:j\in S_k\},
\qquad U_0=\operatorname{col}(B).
\tag{2}
\]

The reason is elementary. The surviving DAG subsystem has an invertible triangular structural matrix and positive definite noise covariance. Its latent covariance has rank \(|S_k|\). Multiplication by the independent columns \(B_{S_k}\) preserves that rank and column space.

The source uses two noise-scale regimes \(\ell=1,2\) for each \(k\). Its stated data interface therefore has \(2(K+1)\) regimes. The two observational noise covariance matrices \(D_1,D_2\) have distinct coordinatewise variance ratios

\[
\lambda_j=(D_1)_{jj}/(D_2)_{jj}.
\tag{3}
\]

Positivity of the denominators and of the relevant nonintervened variances is required for the displayed inverses and rank identities.

The intervention design is a strongly separating system. For each ordered pair of distinct nodes, an environment leaves the first active and knocks out the second. Define the active signature

\[
\kappa_j=\{k\in[K]:j\in S_k\}.
\tag{4}
\]

The signatures are pairwise incomparable under inclusion. In particular, they are distinct. This coverage condition is stronger than merely having many unknown interventions. Under it,

\[
\bigcap_{k\in\kappa_j}U_k=\operatorname{span}(b_j).
\tag{5}
\]

The empty intersection means \(U_0\). For \(d>1\), strong separation prevents an empty signature.

The source's \(K=O(\log d)\) assumption concerns the number of designed or realized environments satisfying this coverage condition. It does not show that arbitrary observational changes have such signatures.

## 2. Source pipeline and finite-sample claims

Sections 3–4 propose recovering unknown intervention targets from

\[
g(T)=\dim\bigcap_{k\in T}U_k,\qquad T\subseteq[K],
\tag{6}
\]

then obtaining decoder columns by Equation 5, and finally solving a generalized eigenproblem on decoded observational covariances. Lemma 3.1 asserts a polynomial-time target reconstruction, without presenting its algorithm or proof in v1. Its accompanying sentence says that at most \(O(d)\) values of \(g\) need to be computed. Enumerating all \(2^K\) subsets only proves polynomial dependence from \(K=O(\log d)\). It does not by itself prove that linear query count. Section 4 below supplies a separate explicit construction.

For ordered orthogonal projections, let

\[
Q(T)=\left(\prod_{k\in T}P_{U_k}\right)
      \left(\prod_{k\in T}P_{U_k}\right)^\top.
\tag{7}
\]

The eigenspace at eigenvalue one is exactly the intersection. Indeed, orthogonal projections cannot increase norm. Equality of the initial and final norms forces equality at every projection, hence membership in every subspace. The converse is immediate.

The empirical estimator counts eigenvalues of \(\widehat Q(T)\) at least \(\rho\). The decoder estimator then uses exact intersections of empirical covariance column spaces, with no threshold in that step. The graph estimator uses absolute values of generalized eigenvector entries. Equation 13 really does contain absolute-value bars, as confirmed in TeX and the original PDF.

For the statistical claims, observations are centered sub-Gaussian and the regime sample sizes satisfy \(n_{k,\ell}\asymp n/K\). Let

\[
r=\max_k|S_k|,\qquad
L=\lambda^+/\lambda^-,
\qquad c_B=\frac{\lambda_{\min}(B^\top B)}
                  {\lambda_{\max}(B^\top B)}=1-\rho^*,
\]

where \(\lambda^\pm\) bound the nonzero observed covariance eigenvalues. Assumption A3 requires

\[
c_B\gtrsim\{L^2dr\log(pn)/n\}^{1/3}.
\tag{8}
\]

The printed results include simultaneous target recovery with probability at least \(1-1/(pn)\), and the decoder bound

\[
\inf_{\text{positive diagonal }D}\|\widehat B-BD\|_F
\lesssim \frac{\sqrt d}{c_B}L\sqrt{\frac{r\log(pn)}n}.
\tag{9}
\]

The identification gauge also includes permutation and sign. Those must be aligned when interpreting Equation 9 or implementing a chosen representative.

For bounded latent covariance eigenvalues, Theorem 4.7 displays graph threshold

\[
\alpha\asymp c_B^{-1}L^3
 \sqrt{\frac{d^2\log(pn)}n}
\tag{10}
\]

and the sufficient signal condition

\[
a_{\min}\gtrsim
a_{\max}\sqrt{m_{\deg}}\,c_B^{-1}L^3
\sqrt{\frac{d^2\log(pn)}n}.
\tag{11}
\]

These are source statements. The edition supplies no proofs from which to verify hidden constants, noise-ratio gap dependence, balancing factors or a data-driven threshold rule. Distinct variance ratios suffice for population identification, but a uniform statistical rate for the displayed generalized eigenvector method needs a quantitative ratio gap. Section 6 makes this dependence explicit rather than treating the whole statistical theorem as independently established.

There is no empirical study in the read manuscript.

## 3. Independent finite-sample observation: exact subspaces in a Gaussian submodel

Consider the allowed special case in which the active noise coordinates are nondegenerate Gaussian. Each regime has a Gaussian distribution supported exactly on \(U_k\), with nonsingular covariance on that \(r_k\)-dimensional space.

For \(N_k\ge r_k\) independent observations,

\[
\operatorname{span}\{X_1^{(k)},\ldots,X_{N_k}^{(k)}\}=U_k
\quad\text{almost surely}.
\tag{12}
\]

To prove this, choose any basis of \(U_k\). The coordinate sample matrix has an absolutely continuous Gaussian law. Every specified full-rank square minor is nonzero almost surely because its determinant is a nonzero polynomial. The zero-rank case consists entirely of zero observations.

For the raw centered second moment used by the source,

\[
\operatorname{col}\left(N_k^{-1}\sum_iX_iX_i^\top\right)
=\operatorname{span}\{X_i\}.
\]

Thus all regime projectors, intervention signatures and decoder directions can be exact after finitely many observations in this submodel. The covariance entries still have sampling error. Exact direction recovery does not imply exact graph weights or exact observational covariances.

This does not contradict a vanishing upper error bound. It identifies the strength of the source observation model. There is no additive observation noise or quantization, and the statement uses exact real arithmetic. For a general sub-Gaussian law with atoms, \(N_k=r_k\) does not guarantee spanning almost surely.

If \(d\) is supplied, \(d\) samples per regime suffice for this Gaussian span step. If exact rank tests are available, sampling a regime until the first vector lying in the span of its predecessors stops after \(r_k+1\) samples almost surely. Before rank \(r_k\), such a dependence has probability zero. This is an ideal algebraic stopping rule, not a numerically robust procedure.

Only one noise regime per intervention is needed to obtain Equation 2. Combining those \(K\) regimes with the two observational noise regimes gives a constructive \(K+2\)-regime interface for the population pipeline. This is a reduction in needed data types, not a newly proved finite-sample graph rate.

## 4. Independent constructive target and decoder recovery

### 4.1 A transparent combinatorial reconstruction

Let \(m(U)\) count nodes with active signature \(U\subseteq[K]\). Then

\[
g(T)=\sum_{U\supseteq T}m(U),\qquad g(\varnothing)=d.
\]

Boolean-lattice inversion yields

\[
m(U)=\sum_{T\supseteq U}(-1)^{|T\setminus U|}g(T).
\tag{13}
\]

Under strong separation, each nonzero \(m(U)\) equals one. The node labels can be the recovered signatures, and \(I_k=\{U:m(U)=1,\ k\notin U\}\). A fast subset transform costs \(O(K2^K)\) arithmetic operations after the intersection dimensions have been computed. This explicitly proves a polynomial route when \(K=O(\log d)\).

There is a useful design constraint. An antichain of \(d\) subsets obeys

\[
d\le {K\choose\lfloor K/2\rfloor}.
\tag{14}
\]

A short proof samples a uniformly random maximal chain. A particular size-\(s\) subset occurs with probability \(1/{K\choose s}\). A chain meets an antichain at most once, so summing these probabilities proves Equation 14. Stirling's formula gives the optimal order

\[
K=\log_2d+\tfrac12\log_2\log_2d+O(1).
\]

Even near this optimum, enumerating all subsets can cost order \(d\sqrt{\log d}\), rather than \(O(d)\).

Independent random knockouts give a simple sufficient design. If each node is independently active with probability \(1/2\) in every environment, a particular ordered pair is never separated in the required direction with probability \((3/4)^K\). Therefore

\[
\Pr(\text{strong separation fails})
\le d(d-1)(3/4)^K.
\tag{15}
\]

Choosing \(K\ge\log(d(d-1)/\delta)/\log(4/3)\) gives probability at least \(1-\delta\). The interventions still need the exact knockout semantics of Section 1.

### 4.2 A direct algorithm using \(O(dK)\) subspace operations

An exhaustive subset transform is unnecessary when the actual subspaces are available. The following exact algorithm is an independent reconstruction of the source's qualitative polynomial-time claim.

First reduce coordinates to an orthonormal basis of \(U_0\). Maintain \(L\), the span of decoder columns already recovered, initially zero. Repeat until \(\dim L=d\).

1. Form quotient representatives
   \[
   V=\operatorname{col}(P_{L^\perp}U_0),\qquad
   V_k=\operatorname{col}(P_{L^\perp}U_k).
   \]
   Here projecting a subspace means projecting any basis and taking its span.
2. Set \(W=V\). Visit \(k=1,\ldots,K\). Replace \(W\) by \(W\cap V_k\) if that intersection is nonzero. Otherwise leave \(W\) unchanged.
3. At the end, \(W\) is one-dimensional. Recover its signature
   \[
   \kappa=\{k:W\subseteq V_k\}.
   \]
4. Lift through the original spaces,
   \[
   \ell=\bigcap_{k\in\kappa}U_k,
   \]
   with \(U_0\) as the empty-intersection convention. Select a unit vector spanning \(\ell\), record its signature, and replace \(L\) by \(L+\ell\).

**Proof.** After quotienting by previously recovered columns, the remaining projected columns are linearly independent. A dependence among them would say that a nonzero combination of remaining columns lies in the span of recovered columns, contradicting the full column rank of \(B\). Consequently every \(V_k\), and every intermediate \(W\), is a coordinate subspace in this remaining basis.

The final \(W\) is nonzero. If it contained two remaining basis columns with distinct signatures, choose a coordinate \(k\) at which their signatures differ. At the moment \(k\) was visited, both columns were still present. The intersection with \(V_k\) was nonzero and would have removed the column absent from \(V_k\). This contradicts its survival. Hence \(W\) is a line.

A skipped intersection remains disjoint from the final line, while a performed intersection contains it. Membership therefore recovers the full signature of the surviving node. Strong separation then makes the original-space lift exactly Equation 5, even when some columns have already been removed in the quotient. This proves the induction.

The lift is essential. An arbitrary representative of a quotient line may include previously recovered columns and need not equal a decoder column.

There are \(O(dK)\) intersection, membership and projected-image operations. With routine dense SVDs on the reduced \(d\)-dimensional space, a loose arithmetic upper bound is \(O(Kd^4)\), in addition to forming the initial observed subspaces. This is an exact real-algebra calculation, not a bit-complexity or stability result. The recovered labels are signatures and the directions retain arbitrary sign and scale.

## 5. Independent completion of the population graph step

Fix one representative of the recovered coordinates. Let \(W_*=I-A\). The two observational covariances satisfy

\[
\Sigma_\ell=W_*^{-\top}D_\ell W_*^{-1}.
\tag{16}
\]

Solving \(\Sigma_1t=\lambda\Sigma_2t\) gives \(t\propto W_*e_j\), because the ratios in Equation 3 are distinct. Unordered numerical eigenvectors therefore have the form

\[
T=W_*\Pi D,
\tag{17}
\]

with a permutation matrix \(\Pi\) and a nonsingular diagonal \(D\). The source's Equation 9 writes \(T=W_*D\), corresponding to an already aligned ordering.

There is a constructive alignment rule. Build a bipartite graph between rows and eigenvector columns, with an edge at every nonzero entry. Find a perfect matching. Reorder the columns to place that matching on the diagonal, then divide each column by its diagonal entry. The result is \(W_*\), and \(A=I-W_*\). Only off-diagonal entries represent graph edges.

The matching is unique. The true diagonal supplies one perfect matching. Any different matching would select a nontrivial permutation cycle of off-diagonal entries of \(W_*\). Each selected entry \(W_{ij}\ne0\), \(i\ne j\), is an edge \(i\to j\) of the DAG. The permutation cycle would therefore be a directed cycle, a contradiction.

This removes eigenvector ordering, sign and scale ambiguity before reading the adjacency matrix. A different initial decoder representative changes latent coordinate labels and coefficient units, while preserving the graph up to node permutation. No uniquely meaningful physical latent scale is recovered.

## 6. Independent deterministic covariance-to-graph error bound

The missing quantitative condition for the generalized eigenvector step can be exposed without a full concentration proof.

Assume in the chosen coordinates that

\[
\lambda_{\min}(\Sigma_2)\ge m>0,\qquad
\|\Sigma_1\|\le M,\qquad
\|\widehat\Sigma_\ell-\Sigma_\ell\|\le\delta_\ell,
\qquad \delta_2\le m/2.
\]

Define the whitened symmetric pencil

\[
C=\Sigma_2^{-1/2}\Sigma_1\Sigma_2^{-1/2},
\quad
\widehat C=\widehat\Sigma_2^{-1/2}
                 \widehat\Sigma_1\widehat\Sigma_2^{-1/2},
\]

and let \(\gamma=\min_{i\ne j}|\lambda_i(C)-\lambda_j(C)|>0\). Matrix inverse-square-root integration and the resolvent identity give

\[
\|\widehat\Sigma_2^{-1/2}-\Sigma_2^{-1/2}\|
\le \sqrt2\,\delta_2/m^{3/2}.
\]

Expanding the two whitening factors yields the convenient bound

\[
\|\widehat C-C\|
\le \eta:=2\delta_1/m+4M\delta_2/m^2.
\tag{18}
\]

If \(\eta\le\gamma/4\), order eigenvalues and orient eigenvectors to match their population counterparts. The residual equation projected off a simple eigenspace gives

\[
\min_{\pm}\|\widehat u_j\mp u_j\|
\le2\eta/\gamma.
\]

For the corresponding \(\Sigma_2\)-normalized generalized eigenvectors,

\[
\min_{\pm}\|\widehat t_j\mp t_j\|
\le
\xi:=\sqrt2\,\delta_2/m^{3/2}
        +2\eta/(\sqrt m\,\gamma).
\tag{19}
\]

The derivation uses eigenvalue perturbation at most \(\eta\), so the separation from all other population eigenvalues is at least \(3\gamma/4\). The perpendicular component is at most \(4\eta/(3\gamma)\), and converting it to vector distance gives the displayed constant.

Suppose the aligned population eigenvector diagonal has magnitude at least \(\beta>0\). If \(\xi<\beta/2\), thresholding absolute entries at \(\beta/2\) deletes every true zero and retains the true diagonal matching. The thresholded graph is a subgraph of the population support containing that unique matching, so the matching remains recoverable.

After matching and columnwise diagonal normalization,

\[
\|\widehat W_*-W_*\|_{\max}
\le
\zeta:=\frac{\xi(1+\|W_*\|_{\max})}{\beta-\xi}.
\tag{20}
\]

Indeed, a normalized entry has error
\[
\left|\frac{t_i+e_i}{t_j+e_j}-\frac{t_i}{t_j}\right|
\le\frac{\xi(1+|W_{ij}|)}{\beta-\xi}.
\]

If the smallest nonzero off-diagonal magnitude exceeds \(2\zeta\), thresholding between \(\zeta\) and that magnitude minus \(\zeta\) recovers graph support. These conditions give a constructive deterministic perturbation interface. They do not establish source-specific covariance concentration, decoder-error propagation, an adaptive choice of \(\beta,\gamma\), or a full sample-complexity theorem.

The gap is material. For

\[
C=\begin{pmatrix}1&0\\0&1+\gamma\end{pmatrix},
\qquad
E=\begin{pmatrix}0&\varepsilon\\\varepsilon&0\end{pmatrix},
\]

the perturbed eigendirection rotates through an angle satisfying \(|\tan(2\theta)|=2|\varepsilon|/\gamma\). All covariance eigenvalues remain bounded, but the direction error can be order one when \(\gamma\) is at the perturbation scale.

This is a limitation of the specified two-covariance eigenvector step. It is not an information-theoretic impossibility result for the full intervention data, which may contain other graph information. Hidden constants in a fixed-model source statement could depend on \(\gamma\). The unavailable proofs prevent resolving that interpretation.

## 7. Reusable content and boundaries

The constructive contribution for later use is a concrete chain of operations: exact knockout supports produce a family of coordinate subspaces, quotient intersections discover an unknown direction and its signature, original-space intersections lift it correctly, and a unique matching converts a generalized eigenbasis into an aligned structural matrix.

The finite-sample Gaussian observation result and the deterministic covariance perturbation calculation separate two resources that the abstract description can obscure. Decoder directions can already be exact under the strong noiseless support interface. Estimating graph weights through two observational covariances still needs quantitative spectral separation, scale control and finite-sample error bounds.

The original manuscript's finite-sample rate claims remain author claims without supplied proofs. The independent constructions above establish selected population and deterministic statements under their explicit assumptions. They do not certify the entire paper.

No FP core mechanism is proposed. Ordinary predictive experience does not automatically supply exact latent knockouts, a known observational environment, a full-column-rank noiseless decoder, or two exogenous noise regimes with separated ratios. A transfer would first have to justify those information sources or replace them with a different identifiable experiment.
