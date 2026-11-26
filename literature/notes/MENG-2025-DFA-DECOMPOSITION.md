# Meng et al. (2025/2026): compact sample graphs and constructive DFA decomposition

## Edition, sources and actual coverage

**Selected edition:** Junjie Meng, Jie An, Yong Li, Andrea Turrini, Fanjiang Xu, Naijun Zhan and Miaomiao Zhang, *Efficient Decomposition Identification of Deterministic Finite Automata from Examples*, arXiv **2509.24347v2**, October 12, 2025 at 05:16:57 UTC, 31 pages. The inspected arXiv history contains v1 and v2.

Primary sources:

- [Versioned arXiv record](https://arxiv.org/abs/2509.24347v2), [selected PDF](https://arxiv.org/pdf/2509.24347v2) and [complete TeX source](https://arxiv.org/src/2509.24347v2).
- [Official Springer chapter](https://link.springer.com/chapter/10.1007/978-981-95-7826-9_10), SETTA 2025, LNCS 16458, pp. 177–195, first online April 1, 2026, DOI 10.1007/978-981-95-7826-9_10.
- [Implementation URL printed in the paper](https://github.com/MJJ-Shuai/dfa_decomposed_3DFA), now redirecting to [Sakura-0407/dfa_decomposed_3DFA](https://github.com/Sakura-0407/dfa_decomposed_3DFA), and the [baseline repository](https://github.com/mvcisback/dfa-identify).

**Fully read by Pro-E on November 27, 2026, Shanghai:** all 31 pages, Sections 1–7, Appendices A–C, four definitions, three unique theorems and one lemma, all four active proofs, all formulas, three algorithms, 13 figures, six tables, four numbered footnotes and all 20 references. Continuous extracted text was read in large page blocks. Every figure, table and algorithm was visually inspected, as were the central R2 and O1′ formula layouts. Complete TeX was recovered and used by a support reader to verify the active inventory. A proof sketch inside an inactive `\iffalse` block is not counted as published material.

Support readers separately checked metadata, specified formal interfaces and the experimental evidence. Their bounded work did not replace main-reader coverage. The final 19-page publisher body was inaccessible behind a subscription redirect, so it was not aligned with v2 or credited as fully read. The final public reference list has 21 entries, adding the full arXiv version. An author-hosted 31-page PDF is not evidence of identity with the typeset final chapter.

The public implementation listing, README and an exposed runner were inspected only for artifact context. No paper-version commit or raw-result identity was established. No implementation audit, benchmark execution, exhaustive search or formal proof replay was performed. All independent deductions below are ordinary mathematical arguments with their assumptions stated. No FP core files were changed and no FP transfer is asserted.

## 1. The constructive problem

Given finite disjoint sets of positive and negative words, S+ and S−, the learner constructs complete deterministic finite automata A1,...,An such that their **intersection** accepts every positive word and rejects every negative word. A positive word must be accepted by every component. A negative word needs rejection by at least one component. The component count and sizes may be search variables. [Sections 2–3]

The paper develops two connected mechanisms:

1. Compress the finite sample acceptor before constructing a SAT instance, while preserving the information required by conjunctive component acceptance.
2. Enumerate component-size allocations in an objective-compatible order, using satisfiability as the existence test for each allocation.

This is constructive learning of a finite sample-consistent representation. The hypotheses extend to unseen words because they are complete DFAs, but no theorem identifies the generating components or bounds population prediction error. Many different intersections can agree on the finite samples.

For fixed component count n, a sorted allocation m1 ≤ ... ≤ mn is compared by coordinatewise Pareto domination. For variable n, the proposed **states-optimal** objective first minimizes

\[
N=\sum_{k=1}^n m_k
\]

and then maximizes

\[
H(m_1,\ldots,m_n)
=-\sum_{k=1}^n\frac{m_k}{N}\log_2\frac{m_k}{N}.
\]

This entropy is over the allocation of state counts to components. It is not the entropy of trajectories, state visitation, labels or a learned probability distribution. Its tie-breaking role is precisely defined. The suggestion that balanced decompositions generalize better is not a proved or separately measured result. [Definitions 2–4]

## 2. What the compact sample representation preserves

### 2.1 From a prefix trie to a three-valued graph

The augmented prefix tree acceptor, APTA, has one node for each observed prefix. Nodes carry positive, negative or don't-care labels. Only transitions present in the finite sample trie are needed in the encoding. The component hypotheses, in contrast, are complete automata on the whole alphabet. [Sections 2, 4.1]

The paper constructs a smaller three-valued deterministic acceptor by bottom-up signature merging. Two ordinary nodes may share a representative when their labels and all per-letter successor representatives agree. Missing successors are part of this signature. Positive leaves can therefore merge. Each original negative node retains its own representative, including a negative node that also has outgoing edges. [Section 4.2, Theorem 1]

The construction preserves the finite positively and negatively labelled word sets. It compresses equal **sample residuals**, not established residuals of an unknown target language. In the paper's small example, the positive leaves reached by `aaa` and `aab` merge, while the rejecting endpoints remain distinct. Figures 1–2 show this mechanism directly.

### 2.2 Protecting an endpoint also protects its prefixes

Lemma 1 supplies the critical interface: no two distinct prefixes of negative examples share a constructed state. Its constructive reason is stronger than simply retaining the negative leaves.

Suppose two prefixes shared a representative and one could be extended by y to a negative endpoint. Identical successor signatures propagate their shared representative along y. Both paths would then end at the same protected original negative node. In the original trie, a node identifies one complete word, so the two prefix strings followed by the same suffix y must coincide. Right cancellation gives equality of the prefixes.

Thus all histories that can still lead to an observed negative example remain distinct. Compression is available in the remaining regions. This is why the smaller representation can retain a componentwise SAT interface without carrying all cross-component reachability correlations.

Theorem 1 and Appendix A prove language preservation by induction over the bottom-up construction. The Lemma 1 proof appeals briefly to uniqueness that is supplied by the protected-node construction. The structural argument above makes that dependency explicit. It does not assert a new minimality theorem for the constructed 3DFA.

## 3. The exact SAT interface

For component k of size mk, use transition variables e(k,a,i,j), acceptance variables z(k,i), and relation variables x(k,v,i). The last variable indicates that sample-graph node v and component state i can be reached by a common word. At a merged node, several i values can be necessary. This is a reachability relation, not generally a function from compressed sample nodes to component states. [Section 4.2, pp. 9–11]

The constraints have the following roles:

| Constraint | Required property |
|---|---|
| D1–D2 | Every component state has exactly one successor for each letter. |
| T1 | The sample root is associated with initial state 1 of every component. |
| T2 | Every sample node has at least one associated state in each component. |
| T3 | Associations propagate along each sample edge and chosen component transition. |
| R1 | At a positive node, every associated state in every component accepts. |
| R2 | At a negative node, some component rejects all its associated states. |
| O1′ | At a node corresponding to a unique original prefix, each component has at most one associated state. |

In particular, the displayed negative constraint is

\[
\forall v\in A_-,\qquad
\bigvee_{k=1}^n\bigwedge_{i=1}^{m_k}
\left(x_{v,i}^k\Rightarrow\neg z_i^k\right).
\tag{R2}
\]

T1 and T3 force the actual reachable pairs to be included in x. They do not generally force x to be the smallest such relation. Correctness does not require that stronger claim.

### 3.1 Soundness and completeness of the core construction

Here is an independent reconstruction of the source's core equivalence, using the **exact sample-preserving graph constructed in Section 4.2**. Theorem 2's phrase “a 3DFA consistent with S” should not be expanded to arbitrary graphs that add extra labelled words.

For soundness, extract deterministic complete component transition tables and accepting states from a satisfying assignment. Induct along each sample word. T1 and T3 ensure that its actual component states are among the corresponding x values. At a positive endpoint, R1 makes all components accept. At a negative endpoint, R2 makes at least one component reject. Thus every sample has the required intersection label.

For completeness, start with any sample-consistent component DFAs of the given allocation. Set e and z to their true values and x to the exact common-word reachability relation. Closure and initialization hold. Every word ending at a positive graph node is a positive sample, so R1 holds. Every negative graph node corresponds to one original prefix, and therefore one component tuple, so some rejecting component witnesses R2. O1′ holds at every other unique-prefix node as well.

This establishes existence equivalence for the core D/R/T/O constraints under the stated construction. It does not independently certify the copied optional DFS symmetry-breaking displays in Appendix B or the implementation. Several Appendix B displays have index or quantifier inconsistencies, including a negative-example line that differs from main-text R2. The main-text core and its assumptions govern this note's deduction.

### 3.2 Formula size and deployment size are different resources

Let Q and E be the compressed sample graph's nodes and labelled edges. The basic variable counts are

\[
|Q|\sum_km_k,
\qquad
|\Sigma|\sum_km_k^2,
\qquad
\sum_km_k
\]

for x, transition and acceptance variables respectively. A direct pairwise at-most-one transition encoding uses order |Σ| Σk mk³ clauses. Direct T3 propagation uses |E| Σk mk² implications. Keeping |E| explicit avoids silently dropping alphabet dependence. O1′ introduces pairwise state constraints only at the unmerged nodes. These counts are constructive upper descriptions, not a complete account of solver internals or symmetry breaking.

Smaller input formulas can help substantially, but neither variable counts nor the experiments establish monotone SAT runtime as a theorem.

After synthesis, storing the current state of each component costs Σk ceil(log2 mk) bits in a straightforward representation. Dense transition tables cost approximately

\[
|\Sigma|\sum_k m_k\lceil\log_2m_k\rceil
+\sum_km_k
\]

bits, before headers and encoding conventions. The synchronous product can have up to Πk mk states, although fewer may be reachable. The paper optimizes Σk mk, which is a useful explicit structural objective but is not identical to any of these bit costs.

## 4. A constructive correlation-preserving alternative

This section is an independent conditional deduction from the source interface. It gives a reason for the protected negative paths and an alternative representation. It is not an author theorem, an implementation result or a novelty claim.

### 4.1 The missing information is a shared-word correlation

For a compressed node v, let

\[
J_v=\{(\delta_1(1,u),\ldots,\delta_n(1,u)):
\delta_A(r,u)=v\},
\qquad
R_{v,k}=\operatorname{proj}_kJ_v.
\]

For a positive node, the desired condition is exactly that each marginal R(v,k) lies inside the component accepting set Fk. Positive consistency therefore separates across components.

For a negative node, the desired condition is

\[
J_v\cap\prod_kF_k=\varnothing.
\]

Replacing Jv by the Cartesian product of its marginals gives the stronger condition

\[
\prod_k R_{v,k}\cap\prod_kF_k=\varnothing
\quad\Longleftrightarrow\quad
\exists k:\ R_{v,k}\cap F_k=\varnothing.
\]

That is displayed R2. It requires a single component to reject every word in the merged bucket. The true intersection requirement allows different words to be rejected by different components. The source avoids this quantifier exchange by retaining unique negative histories.

Consequently, if negative endpoints are merged while keeping printed R2, the possible failure is exclusion of a valid decomposition. The Section 4.3 prose describes a false-satisfiability failure, but that direction does not follow from this printed constraint with T1/T3. This bounded formula-versus-prose distinction does not challenge the protected-negative construction.

### 4.2 A small exact example

Over alphabet {a,b,#}, take

\[
S^+=\{\#,aa\#,bb\#\},
\qquad
S^-=\{a\#,b\#,ab\#\}.
\]

Two two-state DFAs suffice: one accepts an even number of a letters, the other an even number of b letters, with # acting as a self-loop. Their intersection fits all six samples.

The samples are prefix-free, so an ordinary colour-preserving minimal acyclic sample graph merges the three negative leaves. Printed R2 would then require one two-state component to accept all three positives and reject all three negatives. That is impossible.

To see this, define h(q) as acceptance after reading # from state q. Since # is positive, h(q0)=1. Since a# and b# are negative, both a and b must take q0 to the only other state q1, with h(q1)=0. Since aa# and bb# are positive, both letters must take q1 back to q0. But then ab# is accepted, a contradiction.

The example is analytic, without enumeration. It isolates the exact representational loss: componentwise marginals cannot retain which component rejected which word.

### 4.3 Joint-tuple encoding

Let A be any finite deterministic sample representation satisfying exactly L+(A)=S+ and L−(A)=S−. It may merge negative nodes. Merely retaining original sample labels while adding other labelled words is insufficient for the completeness argument.

Replace x with variables

\[
Y_{v,\mathbf i},\qquad
\mathbf i\in\prod_k[m_k],
\]

and retain deterministic complete component transitions. Add the initial tuple Y(r,(1,...,1)). For every sample edge v --a--> v′ and pair of component tuples i,j, require

\[
Y_{v,\mathbf i}\land\bigwedge_k e^k_{a,i_k,j_k}
\Rightarrow Y_{v',\mathbf j}.
\]

At a positive node require Y(v,i) ⇒ ANDk z(k,ik). At a negative node require Y(v,i) ⇒ ORk not z(k,ik). No general at-most-one tuple condition is appropriate.

**Soundness:** initialization and synchronous propagation include the real tuple for each sample word. The endpoint clauses then impose its correct intersection label.

**Completeness:** given a sample-consistent decomposition, set Y true exactly for tuples jointly reached by some common word in A and the components. Propagation holds by deterministic execution. Exact preservation of the labelled word sets makes every endpoint clause valid.

Thus the construction preserves fixed-allocation existence even when negative states merge. The proof needs finite deterministic representation and exact label-language preservation, not acyclicity itself.

The cost is explicit. Write P=Πk mk. Joint relation variables number |Q|P instead of |Q|Σk mk. A naive propagation template has |E|P² implications, each with n component-transition antecedents. Sparse or lazy generation might reduce practical cost, but no such improvement is established here.

The two designs therefore expose a useful construction choice. Preserve negative histories and retain additive component relations, or compress those histories and pay to preserve their joint component tuples. Neither representation dominates for all sample structures and allocations.

## 5. Allocation search, termination and the exact optimum

Algorithms 1–2 enumerate total size N in increasing order. At each N, they enumerate nondecreasing integer partitions whose parts are at least two, sort them by decreasing allocation entropy, and call SAT in that order. The first success therefore minimizes N and, among those allocations, maximizes H, assuming the core existence test is correct and each call terminates. [Section 5, Theorem 3, Appendix A]

The source gives a finite upper witness: include a two-state accept-all component and, for each negative word u, a DFA accepting the complement of the singleton language {u}. Such a component can use |u|+2 states. Hence a successful allocation occurs by

\[
N\le 2+\sum_{u\in S^-}(|u|+2).
\]

Disjoint labels ensure that this witness accepts every positive sample. The construction is a termination argument, not a useful worst-case polynomial runtime guarantee.

The restriction to at least two states per component needs a clear domain. If both S+ and S− are nonempty and the component count can vary, a one-state reject-all factor is inconsistent and a one-state accept-all factor is removable. Such factors cannot improve the global total-state optimum. For one-sided samples, a one-state solution should be handled separately. For a fixed component count, removing a trivial component changes the problem, so the same argument does not justify treating the restricted Pareto family as the unrestricted one.

For sorted allocations with each part at least two, the exact number is

\[
p(N)-p(N-1),
\]

where p is the integer partition function. Partitions containing at least one 1 correspond bijectively to partitions of N−1 by removing one such part. The paper prints the asymptotic formula for p(N) as if it were the allocation count. It remains an upper bound and retains the claimed subexponential allocation-count growth, but is not an asymptotic equivalence for this difference. Enumeration growth says nothing comparable about the SAT cost per allocation.

## 6. What the experiments demonstrate

### 6.1 Design and comparison

The experiments synthesize decompositions from generated partially ordered task examples. They vary alphabet size, maximum word length and equal positive/negative sample counts. There are ten generated datasets per feasible parameter combination. These are different datasets, not ten timing repetitions of the same instance. Main alphabets have 2, 4, 6, 8 or 10 letters. [Section 6, Appendix C.1]

Runs use an i7-4790 machine with 16 GB RAM and Ubuntu Server 24.04.2. BenchExec caps each run at 15 GB and 600 seconds. ParetoAPTA and Pareto3DFA use the original and compressed encodings. StatesOptimalDIP additionally changes the allocation objective/search. There is no separate states-optimal baseline and no held-out language-accuracy experiment.

The Pareto study reuses the same 460 two-letter and 1,090 four-letter datasets across component counts. The claimed harder-case speedups, 1.4–80.3 times when both methods take at least five seconds and 2.8–40.5 times when both take at least ten seconds, are conditional ranges on commonly solved subsets. They are not unconditional mean speedups. Compression preprocessing is included and can dominate easy instances: for two letters and two components, the reported APTA time is 0.3–0.6 seconds versus 2.1–2.5 seconds for 3DFA. [Section 6.1, Figures 3, 5–11]

The larger benefit is successful solving under fixed memory and time limits. The source reports that Pareto3DFA solves all tested cases through six components except one four-letter timeout, while the APTA encoding encounters many memory failures. Table 1's compact-graph size illustration uses a separate parity-game example family, so it is not a paired size/runtime ablation of the main benchmark distribution.

### 6.2 States-optimal outcomes

The directly reported totals are:

| Alphabet size | Datasets | Solved | Timeouts |
|---:|---:|---:|---:|
| 2 | 460 | 460 | 0 |
| 4 | 1,090 | 1,090 | 0 |
| 6 | 1,150 | 919 | 231 |
| 8 | 1,190 | 689 | 501 |
| 10 | 1,210 | 783 | 427 |
| **Total** | **5,100** | **3,941** | **1,159** |

No memory failures are reported for this experiment. Successful solutions have total sizes from four to ten. Box and cactus plots condition on successful runs. A lower maximum among successes can result from the hardest instances timing out. Changes across alphabet sizes also change the feasible dataset combinations, so they are not a controlled causal intervention on alphabet size alone. [Section 6.2, Figures 4, 12–13, Tables 3–6]

Several printed counts limit exact secondary analysis. Table 2's APTA columns for two letters/six components and four letters/three components do not sum to the stated dataset counts. Tables 4–6 print a nine-state column total of 45, while the visible constituent entries sum to 46. This note retains the consistent per-alphabet solved/timeout totals above and does not infer corrected APTA percentages or silently repair the tables. The scatterplot coordinates 600 and 1,000 encode timeout and memory failure categories, not measured 1,000-second runtimes.

No repeated-run timing variance, confidence intervals or statistical significance analysis is reported. The public artifact makes implementation follow-up possible, but the present reading does not establish independent reproduction or immutable paper-version correspondence. The experiments support practical compact-encoding synthesis on these generated families. They do not establish recovery of the original semantic factors, superior unseen-language generalization from allocation entropy, or a universal computational advantage.

## 7. Retained mathematical tools and scope

The most reusable source mechanism is **interface-aware compression before synthesis**. Equal finite sample residuals can share representation, but a later conjunctive acceptance constraint determines which cross-component correlations must survive. The source's protected negative paths provide one concrete way to retain them.

The independent joint-tuple construction makes the alternative exact: richer relation storage can recover completeness after more aggressive graph merging. Its proof and variable/propagation costs are explicit. The allocation argument separately converts a satisfiability oracle into a precise lexicographic optimizer, with one-state preprocessing and finite-witness conditions stated.

These are tools for finite automata induction and representation design. They do not yet supply an FP object mapping, a learned discovery rule for arbitrary reusable computations, a statistical identifiability theorem or a deployment-level compression guarantee. Those questions remain separate from the results actually established here.
