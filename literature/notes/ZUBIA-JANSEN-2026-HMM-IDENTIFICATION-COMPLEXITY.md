# On the Computational Complexity of Hidden Markov Model Identification

## Source and actual coverage

Markel Zubia and Nils Jansen. **arXiv:2610.09104v1**, submitted October 6, 2026, 20:54:08 UTC. The checked primary history exposes only v1. No peer-reviewed publication or official OpenAI/Anthropic release was authenticated. [Versioned record](https://arxiv.org/abs/2610.09104v1) · [PDF](https://arxiv.org/pdf/2610.09104v1) · [Source](https://arxiv.org/src/2610.09104v1).

**Fully read, November 26, 2026, Shanghai.** The main reader covered all 34 PDF pages through the complete active main.tex, main §§1–8, Appendices A–I, all formulas and proofs, acknowledgments, both footnotes and all 66 compiled references in main.bbl. The three actual figures, comprising six panels on pp. 9, 22 and 24, and both probability tables, numbered as Eqs. (25)–(26) on p. 26, were inspected in the original PDF. Additional dense layouts on pp. 7, 11–13 and 32–34 were checked. There are no empirical benchmark results. Source inventory and dependency lookup assistance do not substitute for this main-reader coverage.

Local ignored sources: literature/corpus/arxiv/2610.09104v1/. Reading the bibliography does not mean reading its 66 cited works. The bounded dependency checks below have their own scoped coverage and do not constitute a certification of every reduction.

## 1. The decision problem and its input

The paper asks whether a **supplied, exactly specified target HMM** has another observationally equivalent member in a supplied parameterized family. This is a decision problem about a model description, not an algorithm for recovering an unknown model from a finite observed sequence.

An HMM has \(n\) hidden states, initial distribution \(\pi\), row-stochastic transition matrix \(A\), and state-emission matrix \(B\). It emits from its current state and then transitions. With

\[
T_y=\operatorname{diag}(B_{1y},\ldots,B_{ny})A,
\qquad
p_{\mathcal M}(y_1\cdots y_\ell)
=\pi^\top T_{y_1}\cdots T_{y_\ell}\mathbf 1,
\]

output equivalence means equality of probabilities for **every finite word**.

The input family is a semialgebraic domain \(\Theta\subseteq\mathbb R^K\) and a polynomial map \(\phi:\Theta\to\mathcal H_n\). Coefficients are rational. The formula for the domain, monomials with binary exponents, parameter list and all HMM entries belong to the input length. A pointwise problem also supplies rational \(\theta^\star\in\Theta\). The state count is fixed within a family, but grows across complexity instances.

Three different uniqueness relations matter:

- **Literal equality:** all numerical entries of \((\pi,A,B)\) agree with the target. Different parameter coordinates that produce identical entries do not count as a rival.
- **Permutation equivalence:** one simultaneous relabeling transforms the initial, transition and emission arrays.
- **Classical state bisimilarity:** states in a common block have identical emission distributions and equal transition mass into each block, with matching initial masses on the final blocks.

The paper's word **deterministic** means pointwise, non-generic identifiability. It does not impose deterministic transitions, token-determined updates, unifilarity, or a deterministic learning algorithm. Its classical state bisimilarity is also different from distribution-based notions that already coincide with output equivalence.

The important restricted parameterizations are:

- **Simple:** every entry is a rational constant, \(\theta_i\), or \(1-\theta_i\). A parameter can occur in several entries. The domain is the unit cube restricted by stochasticity.
- **Mask:** every open entry has its own independent parameter, with only the stochastic row constraints coupling those entries. A zero-valued target entry can still be open. Other entries are fixed to the target.

## 2. Results, with the quantifiers retained

Here \(\exists\mathbb R\) refers to polynomial-time reducibility to existential real feasibility, and \(\operatorname{co}\exists\mathbb R\) to its complement class. The table states **identifiability**, so the existential witness generally belongs to the complementary non-identifiability problem.

| Problem | Reported upper bound | Reported hardness and qualification |
|---|---|---|
| Pointwise global, literal equality | \(\operatorname{co}\exists\mathbb R\), Theorem 11 | Complete already for simple families, Theorem 15. Masks are coNP-hard, Theorem 17, with completeness open. |
| Pointwise global, state permutation | \(\forall\exists\mathbb R\), Proposition 21 | \(\operatorname{co}\exists\mathbb R\)-hard for simple families and coNP-hard for masks. Corollary 27's extra completeness parenthesis is unsupported by the membership result. |
| Pointwise global, classical bisimilarity | \(\operatorname{co}\exists\mathbb R\), Proposition 24 | Complete for simple families, Corollary 25, and coNP-hard for masks, Corollary 28. |
| Binary observation alphabet | Same equality upper bound | Proposition 31 and Corollary 32 preserve the stated simple/mask hardness through an expanded state space. This does not fix \(n\) to two. |
| Local literal identifiability of a rational target in unrestricted \(\mathcal H_n\) | \(\operatorname{co}\exists\mathbb R\), Theorem 35 | The local lower-bound classification is left open. This formulation does not quantify only over an arbitrary supplied subfamily. |
| Generic literal identifiability of a supplied family | \(\exists\forall\mathbb R\cap\forall\exists\mathbb R\) | Compares dimensions of the whole bad-target set and domain. Hardness is left open. |
| Family-wise global literal identifiability | \(\operatorname{co}\exists\mathbb R\) | Asks uniqueness at every target. Unstated combinations with other equivalences are not proved automatically. |

The real-quantifier upper bounds used here lie in PSPACE with the fixed numbers of blocks and finite input encoding in question. The bounded citation check in §7 supports that assertion. It does not establish PSPACE for arbitrary input-growing alternation depth.

## 3. The polynomial output-equivalence certificate

Theorem 8 replaces exponentially many short-word constraints, or infinitely many word constraints, by a polynomial-size invariant-space certificate. For two HMMs with \(n,n'\) states set

\[
T_y^+=
\begin{pmatrix}T_y&0\\0&T'_y\end{pmatrix}.
\]

They are equivalent exactly when there exist real square matrices \(F,\widehat T_y\), of size \(n+n'\), such that

\[
F_{1,*}=(\pi^\top,-{\pi'}^\top),\qquad
F\mathbf 1=0,\qquad
FT_y^+=\widehat T_yF
\quad\text{for every }y.
\]

No invertibility or full-rank condition is imposed on \(F\). Its row space contains the initial signed distribution and is closed under every output operator. Thus all signed word vectors annihilate \(\mathbf1\). Conversely, take a basis of the span of those word vectors, beginning with the nonzero initial signed vector, and pad the matrix with zero rows. Right multiplication on that invariant space supplies \(\widehat T_y\).

The construction uses \(O(m(n+n')^2)\) variables and polynomially many equations. It builds on the forward-space equivalence methods of Tzeng and Kiefer–Wachter. For a rival parameter vector, add the domain constraints and a sum-of-squared-entry-differences inequality. This gives an existential certificate of literal non-identifiability without enumerating every word of length at most \(2n-1\).

For state permutation the certificate must also exclude every permutation, yielding an additional universal block in the complementary problem. Appendix D separately proves that permutation equivalence of two explicit rational HMMs is GI-complete. Its graph-to-HMM construction uses one constant output, uniform initial weights and off-diagonal transition weight \(1/(n+1)\) exactly on graph edges. The reverse direction represents rational initial/emission/transition data as colors on a directed graph.

For classical bisimilarity, Appendix E.1 encodes partition refinement on the disjoint union of the target and rival. Boolean variables describe an equivalence relation at each of \(2n+1\) stages. The initial partition is exact emission equality. Each refinement tests transition mass into every existing block. At the stable partition, a positive sum of squared differences in initial block mass witnesses failure of bisimilarity. This remains existential because the complete finite refinement is encoded directly.

## 4. Hardness reductions and what they preserve

### Simple families: real feasibility, probabilistic automata, then HMMs

Appendix A begins from a bounded real feasibility problem with nonnegative polynomial sides. A selector \(z\) creates a known dummy solution \(z=0,x=0\). The non-dummy branch \(z=1\) corresponds to a solution of the original equations. Acceptance probabilities of specially chosen PA words implement products through paths and sums through branching.

An essential device is a shared scaling parameter for the two sides of an equation. For normalized \(p,q\), the target constraints take the form

\[
\lambda(1+zp)/4=1/8,\qquad
\lambda(1+zq)/4=1/8.
\]

The positive target forces \(\lambda>0\), so equality forces \(p=q\) when \(z=1\). A solution supplies \(\lambda=1/[2(1+p)]\in[1/4,1/2]\). At the dummy solution \(\lambda=1/2\). The construction also constrains every otherwise free numerical entry, preventing extra dummy rivals. The hardness premise on bounded polynomial feasibility is imported from Winkler et al., not re-proved here.

Appendix B converts a PA with \(n\) states and \(m\) letters into an HMM with \(n(m+2)+1\) states and \(m+4\) observations. A control state emits a separator, randomly selects a PA input letter or a decision step with fixed probability \(\kappa=1/(m+1)\), simulates the PA transition, and eventually emits acceptance/rejection followed by an absorbing symbol. For the encoded word \(E(w)\),

\[
p_{\mathcal H}(E(w)\checkmark\perp^r)
=\kappa^{|w|+1}L_{\mathcal A}(w).
\]

Rejection probabilities are complementary, while unfinished simulation prefixes have parameter-independent probabilities. Consequently PA language equivalence and HMM output equivalence agree. Every original numerical entry is copied, with complements only where allowed, so literal equality and simple parameterization are preserved. This numerical-entry condition matters when the original parameter map is noninjective.

For hardness modulo bisimilarity, Appendix E.2 adds a branch whose fair acceptance choice is made early in the target and one step later in the rival. Output probabilities match, while successors have distinct future acceptance probabilities and cannot be bisimulated. Such a rival cannot be a mere permutation either.

### Masks: independent open entries and a Boolean witness

Appendix C reduces 3SAT after adjoining \(z\), replacing clauses by \(\neg z\lor C\) and adding \(z\lor\neg x_i\). The known \(z=0,x=0\) assignment supplies the target. Other satisfying assignments have \(z=1\).

Two literal states for each variable have fixed identifying symbols and open emissions \(r,\bar r\) with \(r+\bar r=\epsilon=1/4\). True and false test states mix these literal states with fixed comparison states. Nonnegative mixture constraints and target zeros force one literal to have \(r=\epsilon\) and its opposite to have \(r=0\). The comparison markers fix the open mixture weights as well. Tables (25)–(26) show how different truth assignments yield the same observed mixture.

For a clause with \(k\) literal occurrences, use \(L=2^{\lceil\log_2(k+1)\rceil}\), binary slack variables and normalizer \(W=k+L-1\). The target true-symbol probability is \(\epsilon L/W\). A satisfying assignment has a unique slack encoding of \(L-\)the number of true literals. A uniform initial distribution over identifiable test states makes equality of two-letter probabilities sufficient for this construction. After the second observation the process reaches the common absorbing output.

The proof obtains a bijection between satisfying assignments and numerically distinct equivalent HMMs, including all open entries. This prevents continuous spurious rivals. Appendix E.3 observes that changing \(z\) also creates a reachable emission row absent in the target, establishing non-bisimilarity.

These reductions use many hidden states, fixed structural zeros and absorbing behavior. Their hardness claims do not already hold under strict positivity, stationarity, a prescribed two-state architecture, or the particular deterministic token-update rules in FP.

### Binary encoding

Appendix F replaces each original observation by a fixed block \(0c(y)0\), where \(c\) is an injective binary code. Each original state has a choice state, deterministic code chains, and an exit state. Original emission probabilities become choice-transition probabilities, while original transitions appear at exits. Initial, emission and transition entries each appear once. The induced family has no additional open entries.

Complete block probabilities recover original word probabilities. Partial-block probabilities sum appropriate completions, giving the converse equivalence. Literal equality, simple entries and masks survive. This is a polynomial state expansion, not a constant-state implementation or finite-sample estimator. The printed construction assumes a nonempty code chain. A singleton input alphabet can first be padded with an unused symbol if this edge case is needed.

## 5. Local, generic and family-wise questions

For local identifiability, Appendix G forms the compact semialgebraic fiber of unrestricted stochastic HMMs whose word probabilities through length \(2n-1\) equal the rational target. A sum of squared differences represents that fiber. Although explicitly writing this polynomial can be exponential, only bounds on its degree and coefficient size are needed.

After clearing target denominators, a lower bound of Jeronimo–Perrucci–Tsigaridas controls the minimum positive squared distance on every compact connected component not containing the target. If the target is isolated, it is its own component. Uniform coefficient bounds give a polynomially computable integer \(L_{\mathcal M^\star}\) such that all distinct equivalent rivals have squared distance greater than

\[
r_{\mathcal M^\star}=2^{-2^{L_{\mathcal M^\star}}}.
\]

Thus failure of local identifiability is equivalent to an existential rival with squared distance in \((0,r_{\mathcal M^\star}]\). Variables \(z_0=1/2\), \(z_{\ell+1}=z_\ell^2\) encode the tiny radius with polynomially many constraints. This is exact algebraic decision theory, not a useful statistical separation or conditioning guarantee at finite sample size.

For generic identifiability the relevant set is

\[
\mathsf{Bad}_\phi=
\{\theta\in\Theta:\exists\theta'\in\Theta,\
\phi(\theta')\equiv\phi(\theta),\
\phi(\theta')\ne\phi(\theta)\}.
\]

The question is \(\dim\mathsf{Bad}_\phi<\dim\Theta\), with the empty domain accepted. This concerns the collection of bad **targets** over the whole domain. It is not the claim that each target's rival fiber has measure zero.

The equivalence certificate makes \(\mathsf{Bad}_\phi\) existentially definable with polynomial description size. Koiran's dimension-threshold reduction supplies existential formulas for \(\dim S\ge r\), including existentially described \(S\). Polynomially many tests already give a PSPACE algorithm. The sharper pair of real-hierarchy bounds comes from the disjunction of independent existential and negated-existential dimension tests over \(r=0,\ldots,K\).

Family-wise non-identifiability guesses both \(\theta,\theta'\), enforces observational equivalence and numerical inequality, and is existential. Other uniqueness relations or local/generic combinations may add quantifiers. The paper leaves combinations and lower bounds open.

## 6. Bounded checks of the new argument

The main reader traced every reduction and proof. The following are narrower independent checks, not a declaration that all imported theorems and complexity results have been certified.

1. **Certificate direction and padding.** The invariant-row-space implication and converse remain valid with zero-padded rows. Requiring \(F\) invertible would be an incorrect strengthening.
2. **PA normalization.** The positive target in the shared-\(\lambda\) constraints excludes the \(\lambda=0\) escape. The printed admissible scale interval agrees with normalized \(p\in[0,1]\).
3. **Mask mixtures.** Literal states force the Boolean endpoints through nonnegative products. The clause test itself is a weighted mixture and need not have endpoint-valued true/false probabilities.
4. **Local distance.** The squared-distance radius and repeated squaring agree in Proposition 34/Theorem 35. The final prose of Appendix G casually calls it a distance, but the operative inequalities use squared distance.
5. **Generic dimension polarity.** The formal threshold disjunction has the right direction. A following prose sentence has the wrong word.

Concrete v1 issues:

| Location | Finding | Consequence |
|---|---|---|
| Corollary 27, p. 12 | Non-identifiability modulo permutations is called \(\exists\mathbb R\)-hard “and thus complete.” Proposition 21 gives only an \(\exists\forall\mathbb R\) upper bound. | Retain hardness, omit unsupported completeness. No class separation or impossibility of a better upper bound is inferred. |
| Fig. 1(b), p. 9 | The final product edge is labeled \(\sigma_p,y\), while the displayed word uses \(\sigma_1\). The complete Fig. 2 labels it \(\sigma_1,y\). | Local diagram typo. The full reduction and correct complete diagram are separate evidence. |
| Appendix C, clause-test discussion after Eq. (32) | The text treats aggregate true/false probabilities as belonging to \(\{0,\epsilon\}\). For \(k=4,L=8,W=11\), the target true probability is \(2/11\), and the false probability is \(3/44\). | The endpoint sentence is false. Their sum remains \(\epsilon=1/4\), which is all the complementary-probability step needs. This does not refute the mask reduction. |
| Appendix H, p. 33, after Eq. (36) | The converse sentence says non-identifiability makes the \(r=\dim\Theta\) disjunct true. | Replace the word by generic identifiability. The formula and preceding algorithm have the correct polarity. |

## 7. Scoped verification of the real-complexity dependencies

The upper-bound citation question was checked with a source assistant and original material. **No defect in the fixed-block PSPACE conclusion was established.**

Renegar's Part I, Theorem 1.1, printed pp. 260–261, announces the general prenex decision bound, with proof in Part II. The main reader visually checked the bit-parallel bound in the original Cornell Part II report, Theorem 1.1, printed pp. 2–3. Its parallel time depends polynomially on

\[
\log L,\quad
2^\omega\Bigl(\prod_{k=1}^{\omega}n_k\Bigr)\log(md),
\]

with exponentially many processors and polynomial-length processor addresses when the number \(\omega\) of quantifier blocks is fixed. Uniform parallel simulation then gives polynomial space. Canny's existential result alone would not explain the alternating statement, but the cited Renegar source does. [Part I DOI](https://doi.org/10.1016/S0747-7171(10)80003-3) · [Original Part II record](https://hdl.handle.net/1813/8738) · [Cornell PDF](https://ecommons.cornell.edu/bitstreams/1bac1d5a-11f6-42dd-affb-544e0dfce37e/download).

Binary monomial exponents do not require explicit expansion. A polynomial-size repeated-squaring circuit has gate equations \(E(x,z)\) with a unique gate assignment for every \(x\). Existential gates use \(E\land\Phi\). Gates placed in a final universal block use \(E\Rightarrow\Phi\). This preserves a fixed number of blocks. Rational denominators have polynomial total bit length. Evaluation of \(\phi(\theta^\star)\) should likewise remain a gate system when expanding its exact rational value would take exponentially many bits. This is a bounded encoding clarification, not a new decision algorithm.

Koiran's author report 97-36, §1.1, permits existential descriptions of a semialgebraic set. Its Theorem 6, printed p. 8, treats the bit model and replaces enormous constructed integers by auxiliary variables. Both passages were visually checked by the main reader. A source assistant additionally checked the matching use in Dörfler et al., NeurIPS 2024, Lemma 9, Theorem 11 and Appendix D. Neither dependency was read in full. [Koiran original report](https://perso.ens-lyon.fr/pascal.koiran/Publis/lip.97-36.ps) · [Koiran journal DOI](https://doi.org/10.1006/jcom.1999.0502) · [Dörfler et al. proceedings PDF](https://www.proceedings.com/content/079/079017-3176open.pdf).

## 8. Appendix I's imported rank criterion fails as stated

The final appendix quotes Tune–Nguyen–Roughan (2013), Theorem 5, as an if-and-only-if criterion for identifiability modulo state permutation/scaling:

\[
\operatorname{krank}(B\otimes_{\rm row}A)=n.
\]

Because the matrix has exactly \(n\) rows, this is full row rank. The quoted assumptions are an irreducible and aperiodic hidden chain and a finite non-redundant observation alphabet. Appendix I then interprets the rival family as all stochastic entries. This criterion is not used in the main output-equivalence certificate or hardness constructions.

### Original source and limited inspection

The original [arXiv:1305.0321v1](https://arxiv.org/abs/1305.0321v1), May 2, 2013, has five pages and was accepted at ISIT 2013. The [Adelaide record](https://digital.library.adelaide.edu.au/items/ff21417a-a9eb-49c2-80cf-0f301c3b6f56) authenticates proceedings pp. 2299–2303 and DOI [10.1109/ISIT.2013.6620636](https://doi.org/10.1109/ISIT.2013.6620636). The IEEE typeset edition was not separately compared.

The main reader visually inspected original pp. 2–3: the HMM model, all-word equivalence in Definition 2, row Kruskal rank, §IV assumptions, Theorem 5 and the beginning of Lemma 6. A source assistant additionally checked the cited technical-report entry [16] on p. 5. This is a **scoped reading**, not a complete reading of TNR.

Theorem 5 actually makes the broad rank assertion. The 2026 appendix has not simply invented it. The original non-redundancy sentence concerns observation letters and only derives \(\operatorname{krank}(B)\ge1\). No requirement that hidden-state emission rows be pairwise distinct appears in the inspected model or theorem. The reference [16] technical report was not retrieved, and a bounded search did not authenticate an erratum. This does not prove that no correction exists.

### Independent exact counterexample

The following calculation was performed for these fixed rational matrices, with exact arithmetic and an all-length algebraic argument. It is our check, not a claim attributed to either paper. Use row-vector initial notation in this subsection:

\[
\pi=(1/3,1/3,1/3),\qquad
A=\begin{pmatrix}
1/2&3/10&1/5\\
3/20&9/20&2/5\\
7/20&1/4&2/5
\end{pmatrix},
\qquad
B=\begin{pmatrix}
1/4&3/4\\
1/4&3/4\\
3/4&1/4
\end{pmatrix}.
\]

Set

\[
S=\begin{pmatrix}
9/10&1/10&0\\
1/10&9/10&0\\
0&0&1
\end{pmatrix},
\qquad
A'=S^{-1}AS=
\begin{pmatrix}
207/400&123/400&7/40\\
57/400&173/400&17/40\\
17/50&13/50&2/5
\end{pmatrix},
\qquad
\pi'=\pi S=\pi,\quad B'=B.
\]

Both transition matrices are strictly positive and doubly stochastic. Both models are irreducible, aperiodic and stationary under \(\pi\). The emission matrix is strictly positive and its two observation columns are linearly independent.

For each observation, \(D_y=\operatorname{diag}(B_{\cdot y})\) commutes with \(S\), because its first two diagonal entries coincide. Since \(S\mathbf1=\mathbf1\),

\[
T'_y=D_yA'=S^{-1}T_yS,
\qquad
\pi'T'_{y_1}\cdots T'_{y_\ell}\mathbf1
=\pi T_{y_1}\cdots T_{y_\ell}\mathbf1
\]

for every finite word. This establishes output equivalence for all lengths, without relying on finite enumeration.

The diagonal multisets of \(A\) and \(A'\) are respectively

\[
\{1/2,9/20,2/5\},
\qquad
\{207/400,173/400,2/5\}.
\]

A state permutation or monomial similarity preserves that multiset, so these models are not related by permutation/diagonal similarity. Under a component-row-scaling interpretation, stochastic row normalization forces each row multiplier to be one, and the rows do not match by permutation either.

Nevertheless \(\det A=1/25\). The first three columns of \(B\otimes_{\rm row}A\) are \(D_0A\), with determinant

\[
(1/4)(1/4)(3/4)\det A=3/1600.
\]

Thus the quoted full Kruskal rank condition holds. The example is also robust to an unstated minimal-hidden-state requirement. The Hankel matrix with prefix and suffix sets \(\{\epsilon,0,00\}\) is

\[
H=\begin{pmatrix}
1&5/12&43/240\\
5/12&43/240&37/480\\
43/240&37/480&12727/384000
\end{pmatrix},
\qquad
\det H=-1/8640000.
\]

Its rank is three, so no HMM with fewer than three states realizes this process. Both displayed three-state models are minimal.

The local source problem is visible in TNR Lemma 6. Its opening argument identifies full row Kruskal rank with the absence of nontrivial row combinations that remain simple tensors. Here \(b_1=b_2=b\), hence

\[
b_1\otimes a_1+b_2\otimes a_2
=b\otimes(a_1+a_2),
\]

while the three rows of the row tensor product remain linearly independent. That claimed equivalence is false.

**Disposition:** do not use Appendix I/Theorem 44's rank-only sufficient condition as a working identifiability theorem under the printed assumptions. The counterexample concerns the original v1 statement and its 2026 reuse. It does not refute the main complexity reductions, and it does not certify or reject a different criterion with stronger emission assumptions.

## 9. Evidence limits and useful follow-through

There is no empirical evaluation, estimated sample complexity, robust finite-word threshold or learned-state construction in this paper. Its illustrative PA/HMM diagrams are exact reductions. Computational resources describe deciding exact properties of a supplied algebraic model family.

The useful distinctions are output equivalence versus structural equivalence, numerical-model uniqueness versus parameter-coordinate uniqueness, and pointwise versus generic versus family-wise quantification. General hardness with a growing state space does not decide a fixed two-state positive family.

The active FP source emits a token and applies a token-dependent deterministic state update. In general its output matrices do not factor as \(\operatorname{diag}(B_y)A\) with a single token-independent \(A\) at the same state dimension. No transfer from the paper's state-emitting HMM family is asserted. A finite-rank operator certificate may be relevant as established linear algebra, but no new FP theorem or architecture change is proposed here.

Follow-up remains proportional:

- Preserve the unsupported permutation-completeness parenthesis and the explicit rank-criterion counterexample when citing v1.
- A need for mask completeness, positive/stationary hardness, or a finite-sample consequence requires a different theorem.
- The authors' open local/generic lower bounds and proposed SAT/real-feasibility solver combinations are research directions, not implemented results.
- After mandatory Astra request3f8e6cb, the next ordinary full-reading candidate is Kutay–Eryilmaz–Shroff, arXiv:2611.03414v1, on finite-memory POMDP control. Model access, occupancy weights and recursive implementation must be read on their own terms.

No formal verification, benchmark replication or exhaustive theorem audit was performed.
