# Binary k-Center with Missing Entries: Structure Leads to Tractability

## Identity and actual coverage

- **Published edition:** Tobias Friedrich, Kirill Simonov and Farehe Soheil, IPEC 2025, LIPIcs 358, 8:1–8:19, published December 15, 2025. [Publisher record](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.IPEC.2025.8), [DOI](https://doi.org/10.4230/LIPIcs.IPEC.2025.8), [19-page PDF](https://drops.dagstuhl.de/storage/00lipics/lipics-vol358-ipec2025/LIPIcs.IPEC.2025.8/LIPIcs.IPEC.2025.8.pdf).
- **Linked full version:** Farehe Soheil, Kirill Simonov and Tobias Friedrich, [arXiv:2503.01445v1](https://arxiv.org/abs/2503.01445v1), submitted March 3, 2025, 11:53:09 UTC; PDF title date **March 4, 2025**, 28 pages. [PDF](https://arxiv.org/pdf/2503.01445v1), [source](https://arxiv.org/src/2503.01445v1). The published paper explicitly links this full version. Author order and mathematical presentation differ; these are not interchangeable files.
- **Read by the main assistant, November 24, 2026 Shanghai:** all 28 pages of v1, complete included TeX, all statements/proofs, Algorithm 1, seven figures, title and numbered footnotes, conclusion and 53 printed bibliography entries; then all 19 pages of the proceedings edition, including Algorithm 1, three figures, two numbered footnotes, funding/acknowledgment and all 52 references. No independent appendix appears in either PDF. The source archive's unreferenced vertex-cover appendix and disabled draft fragments are not additional published sections. Bibliography entries are not claims of reading the cited works.
- Original v1 PDF pages 3, 7, 10, 11, 13, 15, 16, 20 and 23 were visually checked; these include every figure and the critical carry/zero-row formulas. Published PDF pages 3, 7, 12, 14 and 15 were visually checked, covering every figure, the formal masked-distance definition and the printed algorithm. Reliable text was used elsewhere.
- **Evidence level:** peer-reviewed proceedings plus the author-linked extended manuscript; full reading is complete. Several small literal-formula checks below are independent. No implementation of the FPT algorithms, complete theorem certification, benchmark or formal proof replay was performed.
- Local material: literature/corpus/pisf_prior_art/2503.01445v1/, with the published edition under ipec2025/.

## Question, model and principal results

The paper asks when clustering incomplete binary rows is computationally tractable because of the **pattern of known entries**. It studies an exact finite optimization/decision problem, without a sampling distribution or a probabilistic latent-class learning model.

Let \(A\) be an \(n\times m\) binary data matrix and \(M\) its known-entry mask. The conference's Definition 5 asks whether a binary matrix \(B\), with at most \(k\) distinct rows, satisfies

\[
\forall i,\qquad
\sum_{j=1}^{m}M_{ij}\mathbf 1\{A_{ij}\ne B_{ij}\}\le d.
\]

Equivalently, choose at most \(k\) arbitrary binary center strings, assign each row to one, and bound every row's Hamming disagreement on its observed coordinates by \(d\). Centers need not be input rows. A missing entry contributes zero, not an estimated value or an uncertainty penalty. At \(d=0\), this is an existence question for a completion with at most \(k\) distinct rows. With positive \(d\), known entries may disagree with the representative. The wildcard distance can violate the triangle inequality.

The conference adds a clear observation: replacing zero missing-entry cost by any fixed, solution-independent cost only shifts each row's radius allowance; the relevant subproblems already permit nonuniform radii. This does not model informative missingness or give a statistical correction for it.

The bipartite incidence graph \(G_M\) has row and column vertices, with an edge exactly when \(M_{ij}=1\). Sparsity alone is not the parameter. The authors use vertex-cover number \(v\), fracture number \(f\), and treewidth \(t\). A fracture modulator \(F\) leaves components of at most \(|F|\) vertices; \(f\) is the minimum size of such an \(F\).

| Published result | Claimed running time and parameter scope |
|---|---|
| Theorem 1, vertex cover | \(2^{O(kv+v^2\log v)}\operatorname{poly}(nm)\); FPT in \(v+k\), without putting \(d\) in the parameter. |
| Theorem 2, fracture number | \(2^{O(kf+f^2\log f)}\operatorname{poly}(nm)\); FPT in \(f+k\). |
| Theorem 3, treewidth | \(d^{O(t)}2^{O(kt)}\operatorname{poly}(nm)\); FPT in \(t+k+d\), and XP in \(t+k\). The displayed asymptotic expression requires the usual harmless treatment of zero/small parameters. |
| Theorem 4, conditional improvement | If Closest String on \(n\) strings has time \(2^{O(n^{1+\alpha})}\operatorname{poly}(n\ell)\), bounded-variable ILP with \(r\) constraints, coefficient magnitude \(O(r)\), and maximum variable-range width \(2^{O(r)}\) has time \(2^{O(r^{1+\alpha+o(1)})}\operatorname{poly}(rc)\). |
| Corollary 19 | Under ETH, Closest String has no \(2^{o(n\log n)}\operatorname{poly}(n\ell)\) algorithm. This imports the ILP lower bound and the reduction chain; it is not a matching quadratic-exponent lower bound. |

These are computational claims about finding a feasible clustering. They do not assert recovery of a generating partition, a true class count, or unique values at missing cells.

## Algorithmic and proof structure

### Closest String as a small-constraint ILP

The extended version gives the elementary forward reduction explicitly; the proceedings instead recalls the existing Knop–Koutecký–Mnich algorithm as Theorem 9.

Group equal column patterns of the input strings. There are at most \(\min(\ell,2^n)\) types in the complete binary case. For type \(j\), with multiplicity \(m_j\), let integer \(z_j\in[0,m_j]\) count zeros in the proposed center on that block. In row \(i\), a block of ones contributes \(z_j\), while a block of zeros contributes \(m_j-z_j\). Thus

\[
d_H(s_i,s^*)=\mu_i+\sum_j \epsilon_{ij}z_j,
\quad \epsilon_{ij}\in\{-1,1\},
\]

where \(\mu_i\) counts the row's zeros. Requiring this to be at most \(d_i\) yields one constraint per input row. The number and positions of zeros inside a repeated type need not be retained. Missing entries yield zero contributions in the corresponding constraints; nonuniform radii change only the right side.

The dependency is a bounded-coefficient, few-constraint ILP algorithm of Eisenbrand–Weismantel; the corresponding Closest String-with-wildcards result is also already present in Knop et al. The paper's role is to use this subroutine inside the graph-structured decomposition, not to claim the older subroutine as new.

### Vertex cover

Split a cover \(S\) into row vertices \(R_S\) and column vertices \(C_S\). Rows outside \(R_S\) have no known entry outside \(C_S\). Enumerate:

1. an assignment of the long rows \(R_S\) to \(k\) labeled clusters;
2. all \(k\) centers on the cover columns \(C_S\).

For each cluster containing long rows, subtract their already incurred cover-column distances and solve a nonuniform Closest String instance on the remaining columns. Every short row can then be independently assigned to any center fitting its known entries in \(C_S\). Centers for clusters containing no long row are still enumerated on \(C_S\); their other coordinates are unconstrained by short rows.

The enumeration has \(k^{|R_S|}2^{k|C_S|}\) possibilities. Each remaining closest-string instance has at most \(|R_S|\) strings. This explains the parameter dependence and why enumerating all assignments of all \(n\) rows is unnecessary. The algorithm only tests existential feasibility. The source's exact distance expressions need the corrections documented below.

### Treewidth

The full manuscript supplies the proof omitted from the proceedings. At a bag, a fragment retains the cluster label of each active row, each center's bits on active columns, and each active row's accumulated distance over all columns encountered in the subtree. A record is true when a compatible partial solution exists; forgotten rows must already satisfy the radius constraint.

Leaf records start with zero row distance or unrestricted center bits for a lone column. Introducing a row chooses its label and computes its distance on the current bag; no forgotten column can be known for that new row. Introducing a column extends every center and adds each active row's **masked** mismatch. Forgetting a row or column existentially quantifies its stored labels, distances or center bits. At a join, compatible fragments have the same labels and bag-center bits, and their distance vectors combine as

\[
\mathrm{dist}=\mathrm{dist}_1+\mathrm{dist}_2-
\text{distance contributed by the common bag columns}.
\]

The subtraction removes double counting. The transition is existential over compatible child-distance pairs. At the empty root, a true record means a complete feasible clustering. The separator property rules out known entries between a forgotten part and a newly introduced part. Center labels must remain coherent even where entries are missing; assigning arbitrary zeros to individual completed rows is not always a valid witness, as discussed below.

The number of fragments is bounded by choices of row labels, \(k\) center bits per bag column, and distance counters. The proof imports a fixed-parameter constant-factor treewidth approximation and a nice decomposition. No learned compression or probabilistic prediction claim follows from the DP record being sufficient for this exact search.

### Fracture number

The proof splits according to whether \(d\ge 2f\). A short row outside the modulator has known coordinates only in the modulator or in its own small remaining component, hence at most \(2f\) known entries. In the large-radius case it fits any center, and the problem reduces to the long rows; their incidence graph has a cover of size at most \(f\).

If \(d<2f\), take bags consisting of the modulator together with one remaining component. They yield width at most \(2f\). Substituting \(d<2f\) into the treewidth algorithm gives the claimed fracture-parameter bound. This is the short structural combination behind Theorem 2; the inactive longer draft in the source archive is not its published proof.

### The reverse ILP reduction

Theorem 11 of the proceedings corresponds to Theorem 5.1 in the extended PDF. The latter's printed section/result counters jump after its Observation 4; page references are safer than assuming identical section numbering.

The chain is: shift variable lower bounds; remove negative coefficients using extra nonnegative variables and paired equations; replace bounded integers by sums of binary variables; decompose coefficients into bits with carry variables; replace binary coefficients by \(\{-1,1\}\) coefficients; replace equalities by two inequalities; translate signed inequalities into nonuniform Hamming-radius constraints; then equalize radii by padding.

The signed-to-Hamming step uses
\(d_H(x,s_i)=a_i x+\#\{j:a_{ij}=-1\}\),
where \(s_{ij}=1\) for a negative coefficient and zero otherwise. In the final step, duplicate each string and append two complementary blocks of length \(d-d_i\), leaving all other padding zero. Extending a feasible nonuniform center with zeros works forward; summing the two new distances forces the original \(d_i\) bound in reverse.

The stated output sizes are \(n=O(r\log\|A\|_\infty)\), \(\ell=O(\|A\|_\infty\log^2\|A\|_\infty\,rc\delta)\), and \(d=O(\|A\|_\infty\log\|A\|_\infty\,c\delta)\). The construction explicitly expands numerical variable bounds. “Polynomial time” here cannot be read as a general polynomial bound in the binary encoding length of arbitrary bounds: unary expansion can be exponential in that length. The restricted \(\delta=2^{O(r)}\) in the conditional FPT implication is substantive. Exact intermediate size accounting and the entire reduction are not independently certified here.

## Version differences and limited independent checks

These checks arose from reading formulas that would otherwise be copied into an implementation. They distinguish a defective printed construction from a counterexample to the existence of some FPT algorithm.

### 1. The early version drops known zero rows; the proceedings fixes that set

The extended PDF p. 15, and Algorithm 1 on p. 17, define short rows by
\(r\notin R_S\) **and** \(A[r][C_S]\ne\bar 0\).
Known zeros are still observations. With two complete one-bit rows \(0,1\), \(k=1,d=0\), the unique minimum cover is the column vertex. The printed filter discards row \(0\); a center \(1\) then makes the printed algorithm accept, although no center fits both rows at radius zero.

The proceedings p. 11 instead defines \(\overline{R_S}=R_M\setminus R_S\), and its algorithm processes every short row. That specific error is repaired. It should not be reported as an uncorrected defect of the conference row-set definition.

### 2. The published algorithm masks only one argument

Definition 5 correctly compares \(M\circ A\) with \(M\circ B\). However, proceedings pp. 12–14, including Algorithm 1 lines 10 and 21, compare \((A\circ M)[r]\) against an **unmasked** center. Read literally with the given binary Hamming distance, this counts a missing coordinate as an observed zero.

A small check uses

\[
A=M=\begin{pmatrix}1&1\\1&0\\0&1\end{pmatrix},
\qquad k=1,\quad d=0.
\]

Here the zeros of \(M\) mark missing entries. The unique minimum vertex cover consists of both column vertices. The true problem has the center \((1,1)\), with all masked distances zero. The one-sided formula instead requires that center to equal all of \(11,10,01\), so the literal algorithm rejects. Enumeration of the four centers and all two-vertex covers confirms this example.

The necessary interpretation is to mask the center by the same row mask, or calculate disagreements only on observed coordinates. This is a local implementation correction consistent with the stated problem. It does not refute the structural enumeration idea or prove the announced FPT bound false.

### 3. The full-version carry boundary is incorrectly normalized

Extended PDF p. 10, Lemma 5.4, sets
\(q=\lceil\log_2(\|A\|_\infty+1)\rceil\) coefficient bits. Its recurrence is
\[
y_{j-1}+\sum_i a_i[j]x_i=b[j]+2y_j.
\]
The terminal carry should encode the high part of \(b\) in units of \(2^q\). The displayed boundary instead uses
\(y_{q-1}=\sum_{j\ge q}2^{j-1}b[j]\).

For \(3x_1+3x_2=6\), with binary variables, the valid solution is \(x_1=x_2=1\) and \(q=2\). The low-bit equations require \(y_0=1,y_1=1\). The printed terminal formula requires \(y_1=2\). The properly normalized high part is
\(\lfloor b/2^q\rfloor=\sum_{j\ge q}2^{j-q}b[j]\).
This directly identifies a faulty formula in the supplied proof. The proceedings states the corresponding Lemma 14 but defers its proof to the full version; it does not supply a corrected carry calculation.

Other ILP exposition issues include a signed right side described as belonging to \([d]^n\), although the construction gives \(b_i=d-\mu_i\), which may be negative; Figure 3 labels \(A-J\) and \(b\) where the adjoining algebra uses \(2A-J\) and \(2b\). The algebraic signed-coefficient construction is the relevant one.

### 4. DP witness completion needs cluster-consistent values

Extended PDF p. 20 sets a newly introduced coordinate to zero on forgotten rows, but sets it to the selected center bit on active rows. Those rows can share a cluster; arbitrary zeros then need not preserve the invariant of at most \(k\) distinct completed rows. The join proof similarly fills cross-part missing cells with zeros. Missing cells have zero **cost**, but their chosen completion values must still agree with the common center of their assigned cluster.

Filling such cells from the cluster centers is compatible with the separator argument and costs nothing on missing entries. The printed introduce-column mismatch also needs the mask, and its distance domain must include zero. These are qualifications to the supplied proof/witness description; this note does not claim a complete corrected proof or an exhaustive error audit.

## Evidence, dependencies and unresolved questions

There are no experiments, implementation timings, statistical consistency results or sample-complexity bounds in either edition. Genome phasing, Netflix-style data and practical ILP solvers motivate the problem, but the claimed practical usefulness of coupling the reduction to an ILP solver is a proposal rather than an evaluated result.

Main dependencies are Knop–Koutecký–Mnich for few-row closest-string variants, Eisenbrand–Weismantel for bounded ILP, tree-decomposition algorithms, Dvořák et al. for finding a fracture modulator, and Knop–Pilipczuk–Wrochna for the conditional lower bound. The proceedings updates Rohwedder–Węgrzycki from a 2024 preprint citation to [ITCS 2025](https://doi.org/10.4230/LIPIcs.ITCS.2025.83), an independently obtained fine-grained equivalence. That cited paper has not been read here.

The conclusion asks whether dependence on \(d\) is necessary for the treewidth parameter and whether a matching lower bound can justify the quadratic exponent for cover/fracture parameters. Its informal statements about eliminating \(k\), and reducing to “\(2^v\)” ILP instances, should not replace the explicit enumeration \(k^{|R_S|}2^{k|C_S|}\) and proved parameterized bounds. In particular, two centers agreeing on cover columns may still be needed for different long rows outside those columns.

## Scope relative to the current reading question

The exact common object is an incomplete finite response table together with a constraint on the number of distinct completed rows. The paper establishes an algorithmic approach for fixed \(k\) and worst-row binary disagreement. It does not characterize whether a particular unseen response is constant over **all** compatible row partitions/completions; existence and unique identification are distinct.

It also does not select a class count by integrated Bernoulli target likelihood, handle a prior centered on a frozen language predictor, prove transfer from ordinary next-token labels, or price installed bits and deployment computation. Astra's subsequent 3b17ced registration moves to that chronological language experiment. No theorem from this paper is transferred to that experiment in this note, and no core theory or experiment file was changed.

Further work is conditional: consult the current ITCS equivalence if a precise complexity premise is needed; seek a corrected implementation/proof before using the printed algorithms literally. There is no automatic historical reading chain, and no author-contact task.
