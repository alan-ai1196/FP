# FAIGLE-SCHONHUTH-2011-EQUIVALENCE — Equivalence tests for hidden Markov processes and quantum random walks

## Source and coverage

Ulrich Faigle and Alexander Schönhuth. *Efficient tests for equivalence of hidden Markov processes and quantum random walks*. IEEE Transactions on Information Theory **57**(3), 1746–1753 (2011). [Author institution record](https://ir.cwi.nl/pub/18048).

Edition read: [arXiv:0808.2833v5](https://arxiv.org/abs/0808.2833v5), November 4, 2010, 17 pages. The main assistant personally read every page in two continuous blocks, pp. 1–7 and 8–17, including all definitions, proofs, formulas, both algorithms, concluding discussion and all 21 numbered references. No separate appendix, figure or experimental table occurs in this edition. The density-matrix formulas and both printed algorithms were checked against PDF layouts on pp. 8, 10 and 13.

Local PDF and complete TeX archive are retained at:

- literature/corpus/peer_reviewed/predictive_operator_prior_art/faigle-schoenhuth-0808.2833.pdf
- literature/corpus/peer_reviewed/predictive_operator_prior_art/faigle-schoenhuth-0808.2833v5-source.tar
- literature/corpus/peer_reviewed/predictive_operator_prior_art/faigle-tex/EquivalenceTestsRevised.tex

The filename without a version suffix contains v5, as printed on its first page. Reading coverage is based on the complete PDF text plus visual formula checks. Downloading the TeX does not imply a second complete source reading.

The institution record confirms the journal publication. Its exposed final-version and publisher-version links returned 404 in this retrieval. The journal edition has not received a separate complete reading. The version-specific cautions below apply to v5.

## The original question

Different model parameters can induce exactly the same probability law for every finite output word. The paper asks how to decide this **equivalence problem** efficiently when two explicit parameterizations are supplied.

The input is not a sample of observed sequences. It consists of known hidden Markov models or known quantum random-walk descriptions. The task is equality of their entire output laws, rather than equality of hidden graphs, uniqueness of a latent parameterization, estimation of a model from data, or approximate predictive agreement.

The authors present a common finite-dimensional linear framework and claim an arithmetic-operation bound

\[
O(|\Sigma|\max(n_X,n_Y)^4).
\]

For hidden Markov models, n is the number of supplied hidden states. For quantum walks, the relevant state space in their calculation is the real space of Hermitian matrices. If the underlying complex Hilbert space has dimension k, that linear space has dimension n=k². The bound should not be reported as O(k⁴) merely by replacing “state-space dimension” with Hilbert dimension.

Section 4 explicitly uses unit-cost exact arithmetic with rational input. It does not establish a bit-complexity bound or numerical robustness of rank decisions.

## Finite-dimensional representation

For a process with word probabilities p(w), the infinite matrix of concatenated-word probabilities defines row and column spaces of the same dimension. The authors call a process **finitary** when this dimension is finite. A finite submatrix

\[
P_{I,J}=(p(wv))_{v\in I,w\in J}
\]

is generating if it has the full infinite-matrix rank. It is basic if it is also square of the minimal possible size. Their ordering of the suffix index v and prefix index w is worth preserving when translating formulas.

Theorem 2 gives a finite certificate of equality. Given a basis (I,J) for one finitary process, the other must have the same basis property and agree on the stated basis probabilities and shifted entries,

\[
p(v),\qquad p(wv),\qquad p(wav),
\quad v\in I,\ w\in J,\ a\in\Sigma.
\]

The proof invokes minimal linear reconstruction. The shifted blocks encode how appending a symbol acts in the finite state space. This is a certificate derived from complete parameterized laws. It is not a lower bound on the longest word that an adversarial identification problem may require.

## Hidden Markov models

The paper uses state-emitting hidden Markov models. A transition matrix M and diagonal emission operators give symbol matrices

\[
(T_a)_{ij}=e_{ia}M_{ij},\qquad \sum_aT_a=M.
\]

Word probabilities factor as

\[
p(v)=\pi^\top T_{v_1}\cdots T_{v_t}\mathbf1.
\]

The forward row and backward column can be cached. Once they are available for a prefix w and suffix v, the probabilities p(wav) for all central symbols a follow by matrix-vector products.

For the column generating family, initialize the same model separately at every hidden state,

\[
g_i(v)=e_i^\top T_v\mathbf1.
\]

The original process's column functions lie in their linear span. These generators may be redundant because the supplied hidden-state count may exceed the process's minimal linear dimension.

The paper's forward/backward probability discussion uses informal conditional-probability labels for objects computed without normalization. The reliable formulas for reuse are the matrix products themselves. For example, πᵀT_v sums to p(v), so it is not already a normalized conditional state distribution.

## Quantum random walks

The model starts from a normalized vector ψ₀, evolves by a unitary U and measures the output using projectors P_a. The normalized wavefunction update is nonlinear because of conditioning on the emitted symbol.

Passing to an unnormalized density matrix makes the operation linear:

\[
\mathcal T_a(Q)=(P_aU)Q(P_aU)^*.
\]

The word probability is

\[
p(a_1\cdots a_t)
=\operatorname{tr}\!\left[
\mathcal T_{a_t}\cdots\mathcal T_{a_1}(\psi_0\psi_0^*)
\right].
\]

The composition order follows chronological application to the density matrix. It differs in appearance from the row-vector convention used for hidden Markov models.

The Hermitian matrices form a real vector space of dimension k². The trace is a linear terminal functional. Consequently, the same finite-dimensional basis construction can be applied to this probability law. A spanning family of Hermitian initial matrices gives linear generator functions g_i(v)=tr(\mathcal T_v(Q_i)).

An arbitrary Hermitian generator need not be positive semidefinite or have trace one. Its generator function therefore need not itself be a probability distribution. The span argument needs linear functions with the stated computational access. It should not be justified by silently treating every basis matrix as a physical initial state.

## The basis algorithm and its proof

The construction has three stages.

1. Starting from an available generating family g₁,…,gₙ, explore words while retaining linearly independent vectors g(v). This creates a row generator.
2. Use the resulting row functions to explore the opposite side and obtain a genuine column basis.
3. Delete dependent rows of the finite matrix to reduce the initial row generator to a row basis.

The critical pruning lemma says that a linear dependence between the generator evaluation vectors gives the corresponding dependence between process functions. Applying the shift operators propagates that dependence to extensions. A dependent candidate therefore need not generate an exponentially large descendant tree.

The two directions of extension differ: the first stage prepends a symbol, while the second appends one. This reflects the prefix/suffix orientation, not an interchangeable coding convention.

At most n independent vectors are added. Each adds at most |\Sigma| candidates. The proof bounds the number of processed candidates by O(|\Sigma|n), with O(n³) linear-independence work per candidate and cached probability updates. Row reduction is also polynomial. These counts give the stated O(|\Sigma|n⁴) arithmetic bound.

For two input models, the procedure first constructs their minimal dimensions. Unequal dimensions prove nonequivalence. Equal dimensions permit the finite basis and shifted-entry comparison of Theorem 2. Equality of the complete finite representation is then equality of the entire process law.

This approach avoids enumerating every word in a length-bounded exponential tree. It does not require stationarity. No sharp positive stationary three-symbol example is constructed.

## Additional claims and experimental status

The paper describes an adaptation to a probabilistic-automaton formulation by introducing a stopping symbol and cites earlier work for the conversion. Its discussion specifically distinguishes probability laws on finite strings from cylinder probabilities of an infinite process. This distinction matters when comparing it with automata equivalence statements from other conventions.

The conclusion compares a maximum-state-count expression with an earlier expression involving the sum of the two state counts. Since max(n₁,n₂) and n₁+n₂ differ by at most a factor of two, that comparison alone is not a different polynomial asymptotic order.

The authors also explain that their basis routine can be inserted into previously developed ergodicity tests. This is an application through a cited result, not a new proof of every condition needed for ergodicity.

There are no reported benchmark experiments, learning curves or statistical estimation results. Approximate equivalence is identified as a future direction.

## Limited checks of the literal v5 formulas

The checks here concern explicit expressions needed to reproduce the method. They are separate from the authors' claims and do not amount to a full independent verification.

### Hermitian basis formula

Equation (25) defines f_m=i e_m and then forms

\[
F_{ij}=f_if_j^*+f_jf_i^*.
\]

With that definition, F_{ij}=e_ie_j^*+e_je_i^*=E_{ij}. Thus the displayed F matrices duplicate the real symmetric matrices and omit the imaginary off-diagonal Hermitian directions. They are not a basis of the k²-dimensional Hermitian space as printed.

A coordinate-correct standard choice is

\[
E_{ii},\quad E_{ij}+E_{ji},\quad i(E_{ij}-E_{ji}),\quad i<j.
\]

This is a direct algebraic observation about the printed basis. The density-matrix linearization itself remains meaningful with a genuine Hermitian basis. No implementation or full proof of the corrected algorithm was produced in this reading.

Equation (29) also omits U from one intermediate projector factor in its displayed amplitude product. The repeated update defined in equation (27), and the density-matrix expression (30), specify the intended operation.

### Queue and variable names in the pseudocode

Algorithm 1 selects a candidate from C_row but does not explicitly remove the processed item. Its termination proof presupposes consuming candidates. Algorithm 2 additionally prints a while condition on C_row instead of C_col and updates A_col instead of the returned set J. These were visually checked in the PDF, rather than inferred from a damaged extraction.

An implementation needs a pop/remove operation, the column queue in the second loop, and insertion into J. The prose and proof make those intended roles clear. The printed pseudocode should not be treated as directly executable without these repairs.

### Scope of the complexity and equality claims

The polynomial count is an exact arithmetic count. Rank tests on finite-precision samples, bit growth, approximate equality, conditioning and sample complexity are not analyzed. The linear model dimension may also differ from the original hidden-state count, and quantum operator-space dimension differs from Hilbert dimension.

## Relevance to the requested provenance question

This is a primary source for efficiently constructing finite bases and testing equality of known stochastic-process parameterizations. It supports the established role of shifted Hankel blocks and finite linear spans.

It does not contain the requested lower construction: two strictly positive stationary rank-d laws on three output letters, identical on every word shorter than 2d−1, with different answers to equality of two normalized output operators. Neither the polynomial-time algorithm nor its equivalence certificate supplies that sharpness claim automatically.

The older references most directly relevant to further provenance work are Gilbert 1959, Ito–Amari–Kobayashi 1992, Jaeger 2000 and Tzeng 1992. Their citation here is not a complete reading of those sources. No architectural transfer is proposed.

## Subsequent request status

The bounded prior-art request was subsequently completed. See [the source-grounded reply](REQUEST-2026-11-23-OUTPUT-OPERATOR-PRIOR-ART.md) for the limited negative result, remaining access gaps and separate Moore-subclass deduction. The earlier description of an open request records the status at this paper’s reading boundary.
