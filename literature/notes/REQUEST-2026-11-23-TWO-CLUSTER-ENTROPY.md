# Astra request: two-cluster entropy impurity under uniform context weights

**Request:** local Astra, commit `1bfb42a`, November 23, 2026. **Status: completed as a bounded primary-source check.** This response concerns prior results and their mathematical scope. Astra retains the decision about FP theory and presentation.

## Finding

I did not locate a published entropy theorem explicitly combining **exactly two clusters, equal row sums, strictly positive polynomially bounded integer counts, and inverse-polynomial additive hardness**. This is a limited search result, not evidence of novelty or a declaration that the question remains open.

There is, however, a concrete earlier route to the requested conclusion. **Aloise–Deshpande–Hansen–Popat (2009), Theorem 1**, supplies an equal-weight two-means construction with coordinates in `{−1,0,1}` and an explicit rational objective. A quantitatively controlled embedding near the uniform distribution transfers it to the exact positive equal-row-sum entropy subclass. The derivation below is written here independently; it is **not** a Shannon theorem attributed to that paper. The geometric transfer idea also predates this project: see Chaudhuri–McGregor (2008), §5.1, and Ackermann–Blömer–Scholz (2011), §3.

The same paired construction has an **exact binary-target realization with an independent query revealed after storage**, with no additional rare-event approximation. Thus the broad hardness conclusion should not be described as a newly discovered phenomenon. Priority of the particular minimum-bisection proof, and whether someone already stated precisely this entropy corollary, are not established by this search.

## What the primary sources establish

| Source inspected | Relevant statement and restrictions | What it does not directly establish |
|---|---|---|
| [Laber–Molinaro–Pereira, ICML 2018](https://proceedings.mlr.press/v80/laber18a.html), [supplement p. 19, Theorem 4.6](https://proceedings.mlr.press/v80/laber18a/laber18a-supp.pdf#page=19) | Two-cluster entropy hardness from PARTITION; input vectors are scaled coordinate vectors `u_i e_i`. The main paper's §6 explicitly asks about an FPTAS. | The reduction permits unequal row sums and zeros; PARTITION does not supply the requested polynomial-magnitude gap. |
| [Cicalese–Laber, arXiv:1807.05241v1, §6, Theorem 11](https://arxiv.org/pdf/1807.05241v1#page=30) | Strong hardness via 3-PARTITION, again using scaled coordinate vectors. | The number of clusters is the number of required triples and grows with the instance. It cannot be fixed to two by simply specializing the theorem. |
| [Cicalese–Laber, arXiv:1812.07075v2](https://arxiv.org/pdf/1812.07075v2), §§2, 4; [Cicalese–Laber–Murtinho, ICML 2019, §6](https://proceedings.mlr.press/v97/cicalese19a/cicalese19a.pdf#page=7) | APX-hardness with equal row norm. Each graph edge becomes a binary vector with two ones, so all row sums are two. The cluster count is the vertex-cover threshold. | Equal row sums are already covered, but the cluster count grows and the vectors have zeros. This is not a published fixed-two-cluster APX theorem. The v2 manuscript is dated November 16, 2019; its initial arXiv identifier is from 2018. |
| [Chaudhuri–McGregor, COLT 2008, §5](https://people.cs.umass.edu/~mcgregor/papers/08-colt.pdf#page=9) | Theorem 24 gives a local KL/Euclidean approximation-transfer statement. The stated unrestricted-center hardness in Theorem 25 concerns **maximum** KL cost; Theorem 28 concerns centers restricted to input points. | Neither hardness statement directly proves unrestricted two-centroid total entropy hardness. The printed local formulas need normalization care; see below. |
| [Ackermann–Blömer–Scholz, ECCC TR11-015](https://eccc.weizmann.ac.il/report/2011/015/download/), §1.3, Lemmas 13–16 and §5 | Smooth Bregman/Mahalanobis local comparison and transfer. The actual k-median hardness proof imports planar k-means with `k=Θ(number of points)`. | The paper expressly treats variable `k`. Its fixed-`k` discussion is not a stated no-FPTAS theorem. A PTAS and an FPTAS have different dependence on accuracy. |
| [Aloise et al., *Machine Learning* 75 (2009), Theorem 1](https://doi.org/10.1007/s10994-009-5103-0) | Exactly two means, equal observation weights, signed incidence coordinates in `{−1,0,1}`, and an exact densest-cut cost identity. | An entropy result needs a further normalization/error argument. [Full reading note](ALOISE-2009-TWO-MEANS.md). |
| [Dasgupta, January 17, 2008 technical report](https://escholarship.org/uc/item/2qm3k10c) | Another fixed-two-means hardness route, from a restricted NAE-SAT problem to a squared-Euclidean distance matrix. | Its spectral embedding is a less direct source for exact positive integer entropy counts. Full text was covered, but its figure and lost negation bars remain unchecked, so this source is still indexed partial. |

### The additive-baseline issue

For probability rows `p_i`, unrestricted KL centroids are arithmetic cluster means. With natural logarithms,

\[
\sum_C\sum_{i\in C}D_{\rm KL}(p_i\Vert\bar p_C)
=\sum_C |C|H(\bar p_C)-\sum_i H(p_i).
\]

The optimal partitions agree. Additive gaps are unchanged; multiplicative approximation ratios need not be. A KL approximation gives the corresponding impurity approximation, but the converse is not automatic because the impurity includes a positive input-dependent baseline. Cicalese–Laber v2, §2.2, states this distinction explicitly. The quantitative argument below controls the baseline directly.

### A source-normalization caveat

The actual COLT PDF p. 9 prints a leading coefficient `d` in Lemma 23 for natural-log KL near the uniform distribution. Taylor expansion gives `d/2` multiplying squared Euclidean distance. On p. 10 the first two columns of the displayed matrix `U` have inner product `−1/2`, although the text calls it unitary. These are literal local discrepancies checked against the PDF, not extraction artifacts. They do not by themselves refute the paper's general approximation results. I do not rely on those displayed constants or that matrix below, and have not audited the rest of the paper.

## Independent quantitative corollary from the 2009 construction

Everything in this section is an explicit deduction supplied with this response. Its imported hardness premise is the published two-means construction, not an assertion that the entropy corollary was already printed there.

### 1. Exact Euclidean instance and gap

Let a simple graph have `N≥2` vertices and `m≥1` edges. Orient its edges arbitrarily, and let `x_i∈{−1,0,1}^m` be the signed incidence row for vertex `i`. A nonempty bipartition `P={C_0,C_1}` has squared-error cost

\[
J(P)=\sum_C\sum_{i\in C}\|x_i-\bar x_C\|_2^2
=2m-\frac{N e(P)}{|C_0||C_1|},
\]

where `e(P)` is its crossing-edge count. Minimization solves densest cut, the reduction in Aloise et al., §3.

Each denominator `|C_0||C_1|` is a positive integer at most `N²`. Therefore distinct cut-density fractions differ by at least `N⁻⁴`, and distinct `J` values differ by at least `N⁻³`. Retain the weaker convenient gap

\[
\Delta=N^{-4}.
\]

This is an explicit separation of objective values on small-integer instances; no assumption about a gap in an arbitrary real-coordinate k-means instance is needed.

### 2. Positive rational probability rows with equal integer totals

Set

\[
T=8mN^3,\qquad \lambda=T^{-1},\qquad
p_i(e,s)=\frac{1+s\lambda x_{i,e}}{2m},
\quad e\in[m],\ s\in\{-1,+1\}.
\]

Every entry is positive. Every row sums to one. Multiplying by the common denominator `D=2mT` gives integer counts

\[
v_i(e,s)=T+s x_{i,e}\in\{T-1,T,T+1\},
\qquad \|v_i\|_1=D.
\]

The number of rows is `N`, the dimension is `2m`, and all counts and row sums are polynomially bounded in `N`. Equal row totals mean that the corresponding context distribution is uniform. In fact, these rows stay very close to uniform and require no zero probabilities.

### 3. Uniform entropy remainder over every partition

Define

\[
f(t)=\tfrac12\big[(1+t)\ln(1+t)+(1-t)\ln(1-t)\big].
\]

For `|t|≤1/2`, integration of the geometric series for `f''(t)=1/(1−t²)` gives

\[
f(t)=\frac{t^2}{2}+\sum_{r\ge2}\frac{t^{2r}}{(2r)(2r-1)},
\qquad 0\le f(t)-t^2/2\le t^4.
\]

The last bound follows, for example, by bounding the tail by `t⁴/[12(1−t²)]`. The average optimal log loss of partition `P` is

\[
F(P)=\frac1N\sum_C |C|H(\bar p_C)
=\ln(2m)-\frac1{mN}\sum_C |C|\sum_e f(\lambda\bar x_{C,e}).
\]

Since every mean coordinate lies in `[-1,1]`, the bound applies to every partition, with no dependence on which partition is optimal. Using `Σ_i‖x_i‖²=2m`,

\[
F(P)=C+aJ(P)-R(P),\qquad
C=\ln(2m)-\lambda^2/N,\quad
a=\lambda^2/(2mN),\quad
0\le R(P)\le\lambda^4.
\]

Let `G=aΔ=λ²/(2mN⁵)`. Our choice gives

\[
\frac{\lambda^4}{G}=\frac1{32mN}\le\frac14.
\]

If `P` is not Euclidean-optimal and `P_E` is Euclidean-optimal, then

\[
F(P)-F(P_E)\ge a\Delta-\lambda^4\ge 3G/4.
\]

Also `F_*≤F(P_E)`. Thus an entropy solution within additive `η=G/4` of `F_*` must be a densest-cut optimum. The required accuracy is explicitly inverse-polynomial:

\[
\eta=\frac{\lambda^2}{8mN^5}
=\frac1{512m^3N^{11}}.
\]

This proves the requested search-problem hardness at inverse-polynomial additive accuracy under the imported NP-hardness premise.

### 4. No FPTAS and the correct limitation

The count-impurity objective is `DN F(P)`, so multiplying by the common count scale does not change a multiplicative guarantee. Since `F_*≤ln(2m)≤2m`, an FPTAS run at the rational tolerance

\[
\varepsilon=\eta/(2m)
\]

would return a partition within `η` in normalized log loss. Both its input size and `1/ε` are polynomial in the graph size, so it would solve the NP-hard problem in polynomial time. This excludes a deterministic FPTAS unless `P=NP` on exactly the positive equal-total subclass in the request.

It does **not** establish APX-hardness for two clusters, rule out a PTAS, or prove hardness with fixed outcome dimension. The gap shrinks polynomially. A precise formulation is hardness of the polynomial-count search/approximation problem; no unproved membership-in-NP claim for exact comparisons of transcendental entropy values is needed.

### 5. Exact binary target with a later independent query

Keep the uniform context `U∈[N]`, and store only its cell label `g(U)` before the query. Draw `Q=(e,s)` uniformly from `[m]×{−1,+1}`, independently of `U`, and let

\[
\Pr(B=1\mid U=i,Q=(e,s))=\frac{1+s\lambda x_{i,e}}2.
\]

The calibrated binary readout in a cell replaces `x_i` with its mean. For binary entropy `h`, `h((1+t)/2)=ln2−f(t)`. Consequently, for every partition,

\[
H(B\mid g(U),Q)
=\ln2-\frac1{mN}\sum_C |C|\sum_e f(\lambda\bar x_{C,e})
=F(P)-\ln m.
\]

The additive gap is **exactly the same**. Moreover, `Pr(B=1|U=i)=1/2` for every context, so every stored bit has zero marginal information about `B`. The predictive information is conditional on the later query. This is an independent reformulation of the paired construction, not a claim from the cited clustering papers.

The query alphabet grows. Its identity is available to the decoder after storage, and query-dependent decoding has its own resource cost. This does not contradict polynomial-time sorting for an ordinary two-class contingency table without a later query. Scoring the query adds its partition-independent entropy. Allowing access to `U` again, or letting the encoder wait for `Q`, changes the problem.

## Research implication and boundary

The requested categorical hardness conclusion has a transparent route from an older exact two-means theorem and elementary entropy calculus. This is stronger evidence of prior mathematical ingredients than a search failure alone. The new local minimum-bisection presentation may still be useful for explaining a different mechanism or obtaining a different gap; neither its novelty nor its correctness is decided by this source check. I have not edited, rerun or certified Astra's local reduction.

For a proposed FP use, the correspondence is explicit: uniform contexts are rows, the stored bit is the cluster label, and calibrated log loss is the weighted entropy objective. The hypotheses include an exact input law, variable outcome/query dimension and unrestricted calibrated cell readouts. The deduction concerns worst-case computational acquisition cost. It predicts neither failure on the text experiment nor impossibility of efficient learning on structured distributions.

## Coverage and search limits

The search covered the names and cited sources in the request, their primary hardness sections, the KL/Euclidean transfer chain and targeted variants of “two clusters,” “entropy impurity,” “FPTAS,” “strongly NP-hard,” and channel quantization. Both web search systems were used. No comprehensive citation-database traversal or claim of exhaustive historical priority is made. Search date: November 23, 2026, Asia/Shanghai.

- **Fully read and separately committed:** Aloise et al. 2009, all four pages, figure and references.
- **Laber et al. 2018:** main pp. 1, 8–9; supplement pp. 17–19. Remaining body, proofs and experiments unread.
- **Cicalese–Laber 1807.05241v1:** pp. 11–12 and 30, including the entire strong-hardness argument; the rest unread.
- **Cicalese–Laber 1812.07075v2:** pp. 1–6, 10–12, 19 and 23. Full hardness proof and appendix not covered; remaining figures not visually checked.
- **Cicalese–Laber–Murtinho 2019:** pp. 1–2 and 5–7. The §6 proof continues on p. 8, which remains unread; no whole-paper completion claim.
- **Chaudhuri–McGregor 2008:** pp. 1–2 and 9–11, with actual p. 9–10 mathematical layouts checked. Algorithm sections and remaining references unread.
- **Ackermann et al. 2011:** selected web-extracted portions of pp. 1–5, 7, 10–12 and 16–17, especially Lemmas 13–16 and §5. This is partial. Direct PDF download returned HTTP 503 from both advertised hosts; the inspected web excerpts are retained locally, not labeled a downloaded full PDF.
- **Dasgupta 2008:** all extracted text of the seven-page repository PDF, including its cover and three references; original figure and negation-bar/formula layouts still unchecked. Partial status retained.

Downloaded sources and selected ECCC excerpts are under `literature/corpus/request_entropy_2026_11_23/`; each source has an edition-specific index row. A citation used here is not a claim that its entire paper or its reference tree has been read.
