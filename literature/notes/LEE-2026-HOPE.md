# Lee, Lee and Yi (2026): predicting when program analysis becomes informative

## Edition, sources and actual coverage

**Selected edition:** Doyoon Lee, Woosuk Lee and Kwangkeun Yi, *Inductive Program Synthesis by Meta-Analysis-Guided Hole Filling*, Proceedings of the ACM on Programming Languages 10, POPL, Article 52, pp. 1500–1529, DOI **10.1145/3776694**, published January 8, 2026. The article records receipt on July 10, 2025 and acceptance on November 6, 2025.

Primary sources:

- [Publisher DOI](https://doi.org/10.1145/3776694) and [official POPL 2026 program](https://popl26.sigplan.org/details/POPL-2026-popl-research-papers/54/Inductive-Program-Synthesis-by-Meta-Analysis-Guided-Hole-Filling).
- [Author-hosted 30-page article](https://kwangkeunyi.snu.ac.kr/~kwang/paper/26-popl-leeleeyi.pdf) and [ROPas host](https://ropas.snu.ac.kr/~kwang/paper/26-popl-leeleeyi.pdf).
- [Different 31-page author draft](https://psl.hanyang.ac.kr/assets/pdf/popl26.pdf), checked only for edition identification. It contains unresolved reference/template fields and is not treated as an additional proof appendix.

**Selected-depth research completed by Pro-E on November 27, 2026, Shanghai:** the main reader personally read all 30 pages of the selected article, Sections 1–7, all seven numbered definitions, both numbered examples, all three theorem statements, both algorithms, ten figures, the numbered table, seven numbered footnotes, acknowledgments and all 38 references. Continuous extracted text was used. All figure/table-bearing pages and both algorithm layouts were visually checked, including the overview's unnumbered table.

**The supplementary proofs were not obtained.** Theorems 4.2, 4.4 and 4.5 defer their proofs to a separate supplement. Primary ACM metadata identifies an 824.66 KB supplement under CC-BY 4.0 containing proofs and complete abstract operators. ACM access returned 403, and bounded author/official-source lookup did not expose a working attachment URL. No complete TeX or authenticated implementation source was obtained. The canonical index therefore remains **scoped reading**, with complete main-article coverage and an explicit supplementary-proof gap. There is no additional fully-read credit.

Support readers separately examined the formal interface, experiment tables and edition metadata. They also checked the conditions of the independent deductions below. This did not substitute for main-reader article coverage or retrieve the missing proofs. No implementation audit, reproduction, proof-assistant replay or full theorem certification was performed. No FP core files were changed.

## 1. Constructive mechanism and supplied information

Hope constructs a search policy for **which unknown subexpression to fill next**. Its inexpensive meta analysis predicts where an existing, more detailed abstract interpreter could gain pruning information after a hypothetical fill. It can favor such holes, consider several holes together, and omit an immediate analysis call when no immediate pruning is possible. [Sections 2–4]

The synthesis input is a regular tree grammar G and a finite set of input/output examples E. Primitive operators, their semantics, grammar nonterminals, the component generator and the underlying abstract interpreter are supplied. The desired result is a complete grammar program satisfying every example. A top-down sketch queue is combined with bottom-up complete components. Filling a hole substitutes a component of the appropriate nonterminal. [Section 3, Algorithm 1]

This is a construction for scheduling structured program search. It does not learn primitive operator meanings from unstructured observations, prove that example consistency generalizes, or autonomously discover a new programming language. Its transferable mathematical content is the distinction between **having a candidate operation** and **having enough neighboring information to evaluate or constrain that operation**.

The underlying analysis alternates forward value approximation and backward necessary conditions. Forward analysis overapproximates the values a subtree can produce. Backward analysis overapproximates values compatible with the required output and the other operands. Their intersections can reject an infeasible candidate or constrain components for a remaining hole. The source formalizes the forward step by a least fixed point, backward step by a greatest fixed point, then alternates the two through a decreasing refinement chain. Inputs are substituted by their concrete example values. Multiple examples can be analyzed separately and their constraints combined. [Section 4.2, pp. 12–14]

An underlying bottom at any position certifies infeasibility only under the stated soundness assumptions. Termination, the cost of the underlying domains and complete enumeration of the grammar are separate implementation obligations. The paper does not supply a general polynomial bound for the synthesis task.

## 2. A small analysis of the analyzer

### 2.1 The meaning of May matters

For an underlying abstract domain D-hat, the basic meta domain is the three-element chain

\[
\bot_M < T < A,
\qquad
\gamma_M(\bot_M)=\varnothing,
\quad \gamma_M(T)=\{\top_{\hat D}\},
\quad \gamma_M(A)=\hat D.
\]

The source calls T **MustTop** and A **MayNonTop**. A contains the underlying top as well as every non-top value, including the underlying bottom. It says that a useful constraint is possible, not that one has been established. Meta bottom is an empty set of underlying abstract elements. It is distinct from the underlying infeasibility element. [Section 4.3]

For a hypothetical fill, the selected hole and constants are seeded by A. Other unfilled holes produce T. The required root output is seeded by A in backward analysis. Monotone meta transfers and joins are iterated to an increasing fixed point. The final forward and backward results are then recomputed separately at each position. Keeping this pair distinguishes possible forward restriction from possible backward restriction. [Sections 4.3–4.4]

The bitvector examples expose genuine information dependencies. In Figure 1, forward `xor`, addition and subtraction need both operands to be A before returning A. Forward `and`, `or`, multiplication and several division/shift operations use an OR condition. Figure 2's backward addition/subtraction/xor rule needs both an informative result and an informative sibling. These are dependencies of the selected abstraction, not generic laws that every arithmetic analysis must satisfy.

The string implementation is richer than a single three-state lattice. It combines prefix and suffix information with a length meta domain having constant, bounded and unbounded categories. The underlying domain is a reduced product of string and interval abstractions. The supplementary definitions are necessary for a complete treatment of all operators. [Section 4.6, Figures 3–6]

### 2.2 Ranking and safe use of the prediction

Algorithm 2 considers each hypothetical hole and tests:

| Rank | Meta condition | Intended use |
|---|---|---|
| 1 | Some program position has forward/backward pair (A,A) | A candidate might become infeasible after the fill. |
| 2 | Some other remaining hole has pair (T,A) | A necessary condition might filter that hole's components. |
| 3 | Neither condition occurs | Skip the immediate pruning check and retain the generated children. |

Rank 1 has priority over Rank 2. A choice within a rank can be nondeterministic. The `noprune` branch enqueues all children for the chosen hole. It does not discard the current sketch and does not declare all later refinements permanently uninformative. [Section 3.3, Algorithm 2, equations (7)–(8)]

Some explanatory sentences on pp. 12 and 17 describe a May condition as though every filled component must cause infeasibility or a nontrivial restriction. That stronger reading is not licensed by the displayed concretization. The useful construction here retains the one-sided interpretation: a possible benefit can prioritize a check, while absence of possible benefit can certify that this particular check cannot help, provided the meta abstraction and observation conditions are sound.

### 2.3 The theorem interface is narrower than optimal search

Definitions 3.3 and 3.4 define pruning power and its analysis-based estimate by taking a **maximum over the positions that a nondeterministic strategy may return**. It is neither expected pruning under the actual tie breaker nor a minimum over its outcomes. For the paper's estimated quantity, admissibility is

\[
\widehat\Theta(P,\mathrm{Pick},C)=0
\ \Longrightarrow\
\forall\mathrm{Pick}'\quad
\widehat\Theta(P,\mathrm{Pick}',C)=0.
\]

This optimistic set-valued definition must be retained when interpreting Theorem 4.4. It does not establish that every selected hole yields useful pruning, or that the chosen order minimizes total search time. Definitions 3.5–3.6 describe an optimality objective, but the implemented theorem is presented as the weaker admissibility result. [Section 3.3]

The three author statements are:

- **Theorem 4.2:** sound local meta transfers with respect to underlying forward/backward transfers imply soundness of the meta analysis.
- **Theorem 4.4:** sound meta interpretation implies admissibility of `PickHole` under the source definition.
- **Theorem 4.5:** the bitvector operators printed in Figures 1–2 are sound with respect to the underlying bitvector operators.

All three proofs are external and unread. This note does not replace their detailed hypotheses with an unconditional certification. The independent results next isolate useful constructions whose assumptions can be stated and checked directly.

## 3. Independent conditional deductions

These are Pro-E deductions prompted by the article, not additional author theorems. They concern the source-level search and analysis interface. No novelty or FP transfer claim is made.

### 3.1 An explicit contract for omitting a check

Let Useful(h,c) mean that the current underlying analysis, after inserting component c at hole h, rejects that child or filters some other current component choices. Suppose a meta predicate M(h) obeys

\[
\forall h,c\quad \mathrm{Useful}(h,c)\Longrightarrow M(h).
\]

Then

\[
\neg M(h)\Longrightarrow
\forall c\quad\neg\mathrm{Useful}(h,c).
\]

Consequently one may enqueue all these children without paying for that immediate analysis call. The implication is the entire proof. Its implementation requires sound initialization over every considered component, sound local meta transfers, a sound fixed point, and observation predicates covering every kind of pruning claimed absent. The skipped operation must only remove infeasible candidates or constrain enumeration, not perform some independent semantic update.

Two consequences are distinct. Even an overly aggressive skip normally retains extra candidates rather than deleting a valid solution, if enumeration and final validation are preserved. But only the displayed contract proves that the omitted call would have produced no pruning benefit. Neither consequence proves global search completeness under a finite budget. Future partial programs must remain eligible for analysis as more holes are filled.

### 3.2 Finite state changes in the meta worklist

On a fixed N-node syntax tree, a single stored combined map into the three-element chain has at most 2N strict coordinate increases from the all-bottom initialization. A fair worklist that revisits all transfer dependents therefore reaches its least fixed point after finitely many successful updates. This follows because each coordinate can rise only bottom→T→A, possibly skipping a level.

The 2N bound is a bound on state changes, not on all transfer evaluations or on synthesis time. Scheduling, fan-in, hypothetical choices and underlying analyses still cost work. Storing separate forward/backward maps changes the coordinate count. Product string domains have a different height. This explains why a small information abstraction can be cheap without asserting that the whole search is linear.

### 3.3 Exact information threshold for a sum of independent holes

The paper's three-hole addition example generalizes cleanly under explicit assumptions. Consider

\[
x_1+\cdots+x_h=y,
\]

where every unfilled hole is represented independently by all integers. Filled positions S have exact example values a_i. There are no relational, congruence, finite-width or grammar-derived restrictions on the remaining operands in this analysis. Put

\[
R=[h]\setminus S,
\qquad r=y-\sum_{i\in S}a_i.
\]

If |R|≥2, the exact unary projection of the feasible set onto each remaining coordinate is all of Z. Indeed, for any chosen j and any integer z, set x_j=z, choose another remaining coordinate to equal r−z, and set all others to zero. This is a satisfying assignment. Thus no sound nonrelational interval necessary condition for x_j can be narrower than interval top.

If |R|=1, the last unknown is exactly

\[
x_j=y-\sum_{i\in S}a_i.
\]

Hence h−1 filled operands are necessary and sufficient for a finite unary condition on the last hole in this model. This counts accumulated information, not a requirement that h−1 fills occur in one action. A correct sequential search can retain uninformative children until it reaches this threshold. The constructive role of multi-hole consideration is to recognize and schedule an information-enabling combination before paying repeated unhelpful analysis calls.

The result is about the stated relaxation. A finite component library might contain far fewer realizable values than Z, and a relational analysis could retain the sum constraint earlier. Shared variables, machine overflow and bounded domains require their own argument. Nontrivial information may filter a component library, but it need not do so if every available component already has the required value.

For h current holes and batch cap b, direct consideration of every nonempty subset uses

\[
\sum_{j=1}^{\min(b,h)}\binom hj
\]

subsets. If each hole has at most c≥1 components, brute-force joint assignment enumeration is bounded by

\[
\sum_{j=1}^{\min(b,h)}\binom hj c^j.
\]

These costs distinguish a useful information threshold from a free joint proposal. The source's empirical cap of three is an engineering tradeoff, not a universal theorem about sufficient composition order. [Connection to Section 4.5.1]

### 3.4 Constructing minimal information supports

The positive Boolean dependencies in the bitvector meta rules suggest an explicit planning object: the **minimal filled-hole sets that activate a chosen May fact**. This construction applies to a specified finite positive monotone Boolean rule system. It is not asserted for every full Hope domain or for the complete ranking policy without guards.

Let H be the h currently selectable holes, and let z_i indicate hypothetical filling of hole i. For each Boolean meta fact v, store an antichain A_v of inclusion-minimal supports such that, for every filled set T,

\[
v(T)=1\quad\Longleftrightarrow\quad
\exists S\in\mathcal A_v\quad S\subseteq T.
\]

Initialize a hole seed by {{i}}, an unconditional true seed by {empty set}, and false by the empty family. Let min mean deleting duplicates and strict supersets. Then OR and AND are implemented by

\[
\mathcal A\oplus\mathcal B
=\min_{\subseteq}(\mathcal A\cup\mathcal B),
\]

\[
\mathcal A\otimes\mathcal B
=\min_{\subseteq}
\{A\cup B:A\in\mathcal A,\ B\in\mathcal B\}.
\]

The same filled hole can support multiple premises and is counted only once. Forward addition's AND, forward bitwise AND's OR, backward addition's parent-and-sibling rule, and the Rank-1 forward-and-backward May test fit this representation. Iterate the positive rules fairly from their seeds to their **least** fixed point. Unseeded cycles cannot create their own justification.

**Correctness argument.** A finite OR derivation chooses one branch. A finite AND derivation needs all premises and therefore unions their hole assumptions. Conversely, each support generated by these rules has the corresponding finite derivation. Least-fixed-point semantics collects exactly such derivations. Deleting a strict superset preserves all activating assignments because any assignment containing that superset already contains the smaller sufficient support. The represented upward-closed sets grow monotonically, even when the antichain lists themselves lose obsolete supersets.

This supplies exact minimal triggers for the encoded meta rule system. Since a May fact overapproximates actual informativeness, such a trigger does not certify that any concrete component assignment will actually prune.

**Budget truncation.** Discarding every support larger than b preserves every activation realizable by at most b filled holes. In a derivation whose final support is S, every premise support is a subset of S because rules only take unions. If |S|≤b, no necessary intermediate support exceeds b. Thus the truncated calculation is both sound and complete within that support budget for this positive system.

**Rank-2 guard.** A remaining target hole j must also satisfy j not in T. This is a negative condition and is not upward closed. One safe construction fixes j outside the allowed seed set and computes its backward-May supports over H without j. Alternatively, discard supports containing j and retain the explicit guard j not in T at use time. Forgetting this guard would incorrectly turn the full Rank-2 policy into a monotone predicate.

**Resource limit.** A fact's minimal supports can form the whole middle layer of the subset lattice, with binomial(h,floor(h/2)) elements. With support size at most b, the largest possible antichain has

\[
A_b=\binom{h}{\min(b,\lfloor h/2\rfloor)}
\]

elements. To see the upper bound, a permutation's initial-segment chain contains at most one antichain member, yielding sum over S of 1/binomial(h,|S|)≤1. Taking the largest permitted layer achieves equality. A binary AND may examine A_b squared support pairs before budget and dominance filtering. Fixed small b permits polynomial-size lists in h, but an unrestricted rule graph can have exponentially many minimal supports.

The constructive opportunity is reuse of symbolic dependency explanations across hypothetical fills. It might avoid separately recomputing every subset's meta analysis. No runtime improvement, implementation, new algorithmic priority for Astra or novelty certificate is claimed. Any comparison must price support construction and its potentially large lists.

## 4. One bounded source-formula qualification

The prefix concretization displayed on p. 19 needs clarification before it can be used as a certified implementation specification. It maps a set S to its longest common prefix and the interval of **total string lengths**, but its finite concretization bounds the length of the appended suffix t by that same interval. For S={"a"}, the printed abstraction is ("a",[1,1]). Its literal concretization contains strings "a" followed by one character and therefore excludes "a" itself. This violates S contained in gamma(alpha(S)), required by the claimed abstraction relationship. The printed [0,0] branch also returns the empty set, which cannot represent the singleton empty string under the stated abstraction.

A limited repair for the wildcard-free fragment is to bound the total completed length |s concatenated with t| and to represent infeasibility separately from the valid empty string. This is not a complete repair of the wildcard domain, reduction operators or implementation. The supplement is unread, and no inference is made that the implemented solver shares the literal display error. The general information-scheduling construction remains conditional on a sound underlying domain. This bounded issue was noticed while interpreting the mechanism, not through an exhaustive audit of every operator.

## 5. Empirical evidence and resource scope

### 5.1 Design and main counts

The prototype has about 14,000 lines of OCaml and uses Z3. Experiments use an Intel i9-13900HX at 2.2 GHz with 64 GB RAM and a 60-second limit per problem. There are 337 string problems and 1,294 bitvector problems. Strings combine 205 Duet examples, themselves from SyGuS and online programming examples, with 132 Hardbench cases. Bitvectors combine 750 conditional problems, 500 deobfuscation problems and 44 Hacker's Delight problems. [Section 5.1]

The string comparison uses Duet and SynthPhonia-G, with the latter restricted to the SyGuS grammar and its multithreading disabled. Bitvectors compare Duet and Simba. Hope builds on Simba's analysis framework. A 354-problem Prose set is excluded because important operators are unsupported and the supported subset is easy. DryadSynth-BV is excluded because its term-graph enumeration, filtration and language-model guidance were not integrated. These are material comparator boundaries. [Sections 5.1–5.2]

Figure 7's tables report:

| Domain | Hope | Duet | Third comparator |
|---|---:|---:|---:|
| Strings, 337 problems | 294 | 209 | SynthPhonia-G 244 |
| Bitvectors, 1,294 problems | 1,175 | 1,038 | Simba 1,027 |

Hope uniquely solves 47 string problems and 76 bitvector problems relative to those comparators. SynthPhonia-G uniquely solves four string problems and Duet uniquely solves 51 bitvector problems. Thus aggregate coverage improves without per-instance dominance. The next page's prose instead gives 1,014 for Duet and 1,098 for Simba. Figure 9's suite labels and the ablation baseline agree with the table-level counts above. The discrepancy is retained rather than silently resolving the prose in the author's favor.

Reported mean/median times for Hope are 4.79/0.06 seconds for strings and 8.36/0.31 seconds for bitvectors. Means are calculated on different solved populations, so they are not paired speedup estimates. The source reports average underlying/meta-analysis costs of 1.48/1.38 seconds for strings and 5.43/0.83 seconds for bitvectors. Table 1's representative cost columns are not consistently additive, and the article does not establish an exact nonoverlapping runtime decomposition.

### 5.2 Intervention and multi-hole tradeoff

The Hope-minus ablation disables the meta-analysis hole strategy. It solves 78 Hardbench problems versus Hope's 91 and 1,027 bitvector problems versus 1,175. The combined net increase is 161 problems. These counts support usefulness of the implemented strategy in this benchmark setting. They do not independently identify the contributions of ranking, analysis skipping, incremental reuse and multi-hole consideration because the paper does not present a complete factorial intervention separating them. Nor do aggregate counts alone prove set inclusion of solved instances. [Section 5.3, Figure 10]

The string batch-size comparison is especially relevant to the constructive mechanism:

| Maximum holes filled together | Solved strings | Reported average seconds |
|---|---:|---:|
| 1 | 251 | 6.60 |
| 3 | 294 | 4.79 |
| 5 | 292 | 6.21 |

This is evidence of a practical information-versus-enumeration tradeoff. It does not prove three is optimal outside these benchmarks or that simultaneous filling is necessary for eventual completeness. The sum construction above explains why information may require several accumulated fills, while the subset and assignment counts price one way to search for them. [Section 5.4]

A more precise meta-analysis variant uses the underlying domain on joined component values. The source reports three fewer solved Hacker's Delight problems and one second greater average time. That paragraph says 46 problems, whereas the main benchmark inventory says 44. No absolute solved total is reconstructed from this mismatched denominator. Greater abstract precision can cost more than it saves, but this preliminary comparison is not a general law.

The shift example supplies a concrete causal explanation: knowing a shift amount first allows a useful backward restriction on the other operand. Hope solves the cited `hd-20-d5-prog` instance in 58.97 seconds while Simba times out. This is an illustrative case, not a general timing theorem. [Section 5.4]

No repeated-run count, confidence intervals or runtime variance are reported in the selected article. The supplement and artifact were not inspected. The study measures synthesis under supplied grammars and examples, rather than statistical generalization, discovery of primitive semantics or learned-library reuse across independent task distributions.

## 6. Placement and next reading boundary

The source supplies a useful constructive principle: **reason about when an existing computation will become informative, then schedule or combine the information that enables it**. The independent sum threshold and guarded support-antichain construction make that principle precise under narrow models. Their costs and the May-versus-actual distinction remain explicit.

This note is an independent ordinary program-induction reading, not a second response to Astra's joint-residual request. Pro-A completed request 2e7a6c9 in e0296c3, and that response remains canonical. Pro-E's earlier request 59b8251 remains complete in 8cd79d0. No proposed FP mapping is asserted here because the source assumes a supplied grammar, executable components, I/O examples and analysis semantics rather than establishing prediction-induced acquisition of those objects.

The completed research unit is the entire available main article plus the conditional deductions above. All three supplementary theorem proofs and the complete operator definitions remain unread and are the only reason the edition is not promoted to fully read. A future continuation should seek that exact supplement if access becomes available, rather than reread the 30-page article. Continue independent recent constructive literature after a fresh shared-history and request check.
