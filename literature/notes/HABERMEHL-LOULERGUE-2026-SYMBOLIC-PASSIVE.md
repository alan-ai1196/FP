# Habermehl–Loulergue 2026: labeled witnesses for symbolic state formation

## Source identity and reading boundary

**Paper:** Peter Habermehl and Erwann Loulergue, *Passive Learning of Symbolic Automata over Monotonic Algebras*, [arXiv 2606.06050v1](https://arxiv.org/abs/2606.06050v1), submitted June 4, 2026. The actual manuscript lists Habermehl first, while the arXiv metadata reverses the two authors. The [versioned PDF](https://arxiv.org/pdf/2606.06050v1) has 17 pages. The [complete TeX source](https://arxiv.org/src/2606.06050v1) was also obtained. Only v1 was listed at the November 26 inspection.

The separate [DLT 2026 chapter](https://doi.org/10.1007/978-3-032-28404-4_18), LNCS 16578, pp. 238–251, first appeared online June 6. Its 14-page full text was not retrieved. Publisher metadata, abstract and exposed notes were inspected, but scientific equivalence with the 17-page preprint was not established. Findings below concern **v1**, not an inferred correction status of the final chapter.

**Main-reader coverage:** all 17 pages, Sections 1–6, all definitions, four algorithms, Lemmas 1–2 and Theorem 1 with proofs, four scientific footnotes, six figures, acknowledgment and 14 references. The source algorithms and proof were checked against `algo.tex` and `properties.tex`, with all six figure assets viewed. There are no appendices or reported benchmark experiments. Source assistants separately checked edition identity, the central algorithm and immediate predecessor interfaces. Their scoped assistance does not substitute for main-reader coverage. No implementation, empirical reproduction, exhaustive search or formal verification was performed.

**Assessment:** the paper supplies an explicit, useful teaching-set construction for jointly inferring finite control and interval guards. Its resource is an exactly labeled, target-dependent set of boundary and continuation witnesses. The printed implementation has local discrepancies that prevent using it as a verified executable algorithm. These do not establish impossibility of efficient symbolic-automaton identification.

## 1. The problem actually learned

The alphabet is a supplied effective Boolean algebra over a domain D. For the monotonic case, D has a supplied total order, a least element d_min in D and an upper sentinel d_max outside D. Atomic predicates denote half-open intervals [a,b). A neat symbolic finite automaton uses conjunctions of atomic predicates as guards. In the interval setting these can be represented by intervals. The intended target is a complete deterministic finite-state language recognizer with a canonical, coalesced interval representation.

The learner receives a finite sample

\[
S=(S_+,S_-),\qquad S_+\subseteq L,\quad S_-\subseteq D^*\setminus L,
\]

with no contradictory labels. It returns one recognizer. It has no membership or equivalence oracle, but every supplied word already has its exact acceptance label. This is a supervised whole-word interface. An unlabeled observation tape from an unknown generative process does not supply the negative examples or the membership semantics used here. [Sections 2.1–2.2]

A characteristic sample C for learner A and language L satisfies

\[
C\subseteq S\subseteq\operatorname{graph}(1_L)
\quad\Longrightarrow\quad L(A(S))=L.
\]

The quantifier covers every correctly labeled superset of C. Efficient identification additionally requires polynomial learner time, polynomial characteristic-set size, and polynomial construction of such a set **given the target automaton**. It does not require an ordinary sampling process to produce C rapidly. [Definitions 3–4]

This distinction is useful even independently of SAI: a small certificate for the correct state structure is different from a statistical guarantee for acquiring that certificate.

## 2. Constructive mechanism

SAI starts from a symbolic prefix structure in which all words of equal length share a state and all existing edges have guard top. A state can temporarily carry both positive and negative labels. Red states are settled control states. Their unsettled successors are blue. The next blue state is selected by the shortlex access word. [Section 3]

For that state the intended operation priority is:

1. Try merging it with an existing red state.
2. If no merge is admissible, try making it a new red state.
3. If neither works, split its incoming interval using an observed letter, rebuilding the unresolved continuation structures.

Merges share control structure. Splits refine which letters cause a transition. The algorithm therefore forms these two parts of a recognizer together, without enumerating the whole alphabet. During a merge, the unsettled successor structure is first split to match the settled state's guard partition, after which equal-guard successors are recursively merged. [Algorithms 1–2, Figures 2–4]

The admissibility test detects irreversible conflicts. Opposite labels at a red state are forbidden. So are two examples with opposite labels that have already been forced through the same settled behavior and have exactly the same remaining tail. Temporary contradictions confined to refinable successor structure may remain. [Algorithm 3]

This is a concrete computational-state formation mechanism, but its order, predicate algebra, exact labels and sample storage are supplied. The paper does not infer a program language, a useful alphabet ordering, or a prediction objective from raw experience.

## 3. The explicit witness construction and its cost

Let the canonical target have n states and m interval transitions. Choose a shortest lexicographic access word u_q for each state q. For every pair of distinct residual languages, choose a shortest common distinguishing word v_qr=v_rq. Choose epsilon when the two states differ in acceptance. For each target transition (p,[a,b),q), include

\[
u_p a v_{qr}\quad\text{for every }r\ne q.
\]

Also include the state-separating words u_q v_qr with their correct labels. This is the construction in Section 3.4 and Theorem 1, written with coherent pairwise witnesses. The paper's displayed second union uses all state pairs even though a self-distinguisher is undefined. Restricting it to distinct states is the natural interpretation. Constant languages require a separate case.

The proof idea has two distinct functions:

- **Boundary identification.** Adjacent canonical guards [a,b) and [b,c) have different successor residual languages. A shared continuation gives opposite labels after a and b. Trying to extend the first interval past b makes the new settled successor inconsistent. A cut at b is admissible.
- **Successor identification.** After the interval is separated, a distinguishing continuation forbids merging its successor with any incorrect red residual state. If the correct residual state is not yet present, promotion creates it.

The exact endpoints matter. They are not arbitrary random letters drawn somewhere in each interval. The last guard, with upper endpoint d_max, needs separate treatment because d_max is not a sample letter and there is no following interval. The printed proof's generic adjacent-interval argument does not itself cover that last case. [Theorem 1, pp. 13–14]

The paper gives the word-count bound

\[
|C|\le m(n-1)+n^2,
\]

and each word has length O(n). Hence the corresponding total-symbol bound is

\[
\sum_{w\in C}|w|=O(mn^2+n^3).
\]

The advertised quadratic size concerns the number of words in a state-plus-transition measure. It should not be reported as a quadratic bound in the paper's own runtime input measure, which sums word lengths. Both bounds remain polynomial. The predecessor comparison in Section 5 gives a larger worst-case word count of order mn³+n², so the claimed saving is two state-count factors in that comparison. It is not a distributional sample-complexity improvement.

Three interface conditions must accompany any use of this argument:

1. **Canonical guards:** minimum state count alone does not prevent splitting one interval into two adjacent intervals with the same target. The proof uses a representation in which those redundant subdivisions are coalesced.
2. **Effective interval operations:** arbitrary observed cut points must be legal predicates, with computable order comparisons, construction and nonemptiness handling. Merely stating that each available atom happens to denote an interval does not specify the converse closure required by `Split`.
3. **Encoding cost:** Lemma 1 measures sample symbol occurrences. It does not price the bit length of arbitrary numerical endpoints or provide a uniform bit-complexity theorem from Boolean-algebra decidability alone.

These conditions are natural for an explicit interval algebra with efficient comparisons. They are material when extrapolating to an arbitrary effectively presented algebra. The remark on p. 15 also acknowledges that a literal least element for real-valued data may require adjoining −infinity, or using target knowledge to substitute a finite value below all relevant endpoints.

### A constructive extraction: boundary tables and residual signatures

The source's witnesses also expose a simple reconstruction procedure. This is a conditional observation-table consequence, closely related to classical automata learning, not a novelty claim or a replacement FP architecture.

Suppose a teaching interface supplies:

- A set U containing epsilon and one access word for each target residual state.
- A finite set E of suffixes, containing epsilon, that separates every two target states.
- A sorted set B of letters, containing d_min and every finite guard boundary of the target.
- The exact labels of ue and ube for u in U, e in E and b in B.

Define the residual signature r(u)=(1_L(ue)) over e in E. The signatures r(u) are distinct because E separates the target states. For every u and boundary letter b, the vector r(ub)=(1_L(ube)) matches exactly one row r(u') because U covers every target state. Use that match as the transition target from r(u) at b. Its guard extends until the next letter in B, or d_max for the last interval. Set the accepting bit from the epsilon coordinate and start at r(epsilon). Adjacent intervals with the same target can then be coalesced.

**Why this is exact:** no target guard boundary lies inside a resulting interval, so every letter in that interval has the same target transition as its lower endpoint. Row separation identifies that successor state uniquely. Induction on the input word now shows that the reconstructed machine and the target reach equal residual languages after every prefix, and the epsilon coordinate gives the same final acceptance decision.

The table uses at most |U||E|(|B|+1) labeled words. Given a minimal n-state target, a separating E of size at most n can be chosen: start with the epsilon partition, and whenever a block contains two distinct residual states add a suffix that separates them. Each addition strictly increases the number of blocks, so fewer than n additions suffice. Short distinguishing words have length O(n). Thus the table construction is polynomial in this explicitly supplied certificate, with alphabet and encoding costs still separate.

This derivation isolates two reusable computations: **state identity is row equality across continuation tests, and symbol abstraction is constancy between certified boundaries**. It also locates SAI's substantive extra work: inferring which observed words serve as access/boundary witnesses, without receiving those annotations. The simple table construction does not solve that selection problem or certify the adequacy of U,E,B from arbitrary finite data. It records exactly what can be constructed once those source-dependent witnesses are available.

## 4. Narrow discrepancies in the printed algorithm

The following checks concern literal v1 definitions and pseudocode. Their intended local repairs are straightforward, but the complete repaired learner was not independently implemented or proved here.

### 4.1 A split must consume its edge letter exactly once

Section 3.2 writes a sample word as u t v and defines its tail for the split edge as **t v**, retaining the letter that fires the edge. It partitions these tails into S_1 and S_2 by comparing t with the proposed cut. Algorithm 1 then constructs `SPTA(S_1)` and `SPTA(S_2)` and attaches their roots *after* new edges that consume t.

Take S_+={0} and S_-={100}, and split the initial top edge at 100. The printed SPTA inputs are {0+} and {100−}. Their roots have no acceptance labels, while their depth-one successors receive the labels. After attachment, the original positive one-letter word 0 ends at an unlabeled root. The sample's acceptance marking has moved one step too far.

Figure 4 shows the intended result instead: the immediate successor of the [0,100) edge already carries the positive label. To implement that picture, classify tails using t but build the new SPTAs from the residuals v, with the original labels. This is a source-local consumed-letter mismatch. It does not refute the corrected residual construction.

### 4.2 The final admissible split is never committed on exhaustion

Even granting the intended residual construction, Algorithm 4 lines 13–19 has another issue. Every consistent candidate split is undone. A previously tried split is restored only when a later candidate fails. There is no branch after the finite candidate loop to commit its last successful candidate.

Use the paper's own Figure 4 sample

\[
\{(\epsilon,-),(0,+),(100,-),(00,-),(0\,100,+)\}.
\]

At the first iteration, merging or promoting the depth-one state fails. The distinct observed candidate cuts are 0 and 100. The accompanying prose explicitly says both cuts are admissible, while any larger cut would fail. But there is no larger observed candidate. Thus the last successful cut 100 is undone and line 18 is never reached. The outer loop has no committed change.

Committing the last admissible cut on candidate exhaustion, or defining an appropriate final failure check, would address this control-flow omission. Empty-interval and empty-subsample conventions also need to be explicit. The evidence is a contradiction between the written finite loop and the displayed intended run, not evidence against all possible SAI implementations. Consequently Lemma 1's printed termination claim should not be imported as an executable-code guarantee.

### 4.3 The universal language needs an edge witness

Theorem 1 p. 14 says that a one-state constant language has a characteristic sample containing only epsilon. For S={(epsilon,+)}, the stated SPTA contains just an accepting initial state with no edge. Algorithm 4 has no nonred state to process and immediately returns it. Under Definition 2 it recognizes {epsilon}, not D*.

The negative singleton sample correctly gives the empty language. For D*, adding a positive one-letter example d_min is a natural repair: the intended merge can create an accepting top self-loop. No implicit completion operation is specified in the printed algorithm. This is a narrow defect in the stated constant-language witness case, not a lower bound against polynomial identification.

## 5. What the teaching theorem can and cannot imply statistically

The following are independent elementary deductions about the learning interface. They do not depend on the correctness of SAI's printed implementation.

### 5.1 An acquisition guarantee needs probability mass

Suppose a correctly specified learner has a characteristic set C of M words, examples are drawn iid from a word distribution mu and every witness has probability at least p_min>0. A union bound gives

\[
\Pr(C\not\subseteq S_N)
\le\sum_{w\in C}(1-\mu(w))^N
\le M e^{-Np_{\min}}.
\]

Thus N at least p_min^-1 log(M/delta) suffices for characteristic-set coverage with probability 1−delta. Polynomial witness count alone does not control p_min. For continuous letter distributions, an exact unknown transition endpoint typically has zero probability, so this coverage argument supplies no finite iid guarantee.

### 5.2 Small recognizers can require exponentially many random examples for exact identification

Over letters {0,1}, compare L_0=empty with L_1={0^k}. Both are recognized by complete interval SFAs with at most k+2 states. Fix a full-support input distribution on all finite binary words: the length has probability Pr(length=j)=2^(-(j+1)), and conditional on length the word is uniform. Reveal the exact membership label. The two labeled-data laws differ only at 0^k, whose probability is p_k=2^(-(2k+1)).

On the event that 0^k is absent from N samples, the observations are identical under both targets. Therefore every estimator, including a randomized one, has worst-case exact-language identification error at least

\[
\frac12(1-2^{-(2k+1)})^N.
\]

Achieving fixed error below 1/2 requires order 4^k examples in this family under this one fixed full-support sampling law. This is compatible with small target-dependent characteristic sets. It also does not establish a comparable lower bound for approximate prediction loss: a predictor may safely ignore a sufficiently rare distinction under a specified error tolerance.

The conclusion concerns acquisition information, not a deficit in the representational power of finite state machines.

## 6. Relation to the immediately cited methods

The paper's main contrast with Fisman–Frenkel–Zilles is constructive. That approach selects/decontaminates concrete letters, learns a DFA and generalizes its alphabet back to predicates. If the lifted result fails sample consistency, it may return a prefix tree. SAI instead starts with broad predicates and refines them while merging states. Its Section 5 example replacing one 100 by 99 illustrates why these algorithms can generalize differently on the same finite evidence. This is a constructed example, not an empirical performance comparison.

Fisman–Frenkel–Zilles's [2023 journal article](https://doi.org/10.46298/lmcs-19(2:5)2023) already separates polynomial characteristic data from worst-case sample size. Definition 5.5 and the proof of Lemma 5.7 explicitly use maximal disjoint intervals, explaining the canonical-form qualification above. Definition 7.4 makes the input to the characteristic-set constructor the target automaton. These are the relevant dependencies, not a guarantee of favorable iid acquisition.

The active-learning predecessor [Argyros–D'Antoni 2018](https://doi.org/10.1007/978-3-319-96145-3_23) has membership and equivalence/counterexample oracles. Its general efficiency statement also retains predicate-representation conditions. These resources cannot be removed by relabeling the method passive.

The [Verwer–de Weerdt–Witteveen 2012 RTI paper](https://doi.org/10.1007/s10994-011-5265-4) is the directed historical dependency for interval splitting. Its fixed evidence-order result does not certify every EDSM heuristic. SAI's suggested extension to heuristic operation scores is future work, not part of Theorem 1's guarantee.

These predecessor checks are scoped. The main reader inspected FFZ Definition 5.5, Lemma 5.7 with proof, the Definition 7.2 discussion and Definition 7.4, Argyros–D'Antoni Section 2.2 and Section 4 theorem/corollary passages, and RTI Definitions 3–5 through Theorem 2 on printed pp. 312–315. Source assistants supplied the initial interface comparisons. No predecessor is recorded as fully read.

## 7. Retained tools and limits for subsequent research

The reusable mathematical idea is a decomposition of teaching evidence into **transition-boundary witnesses** and **residual-state witnesses**. It explains why access words alone do not determine either the guard partition or the future-language classes. It also gives a concrete example of structure acquisition whose certificate is small while its probability under ordinary sampling is uncontrolled.

Keep the supplied alphabet order, legal predicate family, exact whole-word labels, canonical target representation and retained sample access explicit. Keep word count, total symbol length and endpoint encoding cost separate. A noise model, a predictive loss, a sampling law, or a finite installed-memory budget would require additional theory.

No FP object mapping or architecture change is proposed. The paper remains a useful program-structure learning reference after these qualifications. The local pseudocode defects, inaccessible final edition and missing acquisition distribution are recorded rather than silently repaired into a stronger result.

## Primary-source locations

- [v1 abstract and history](https://arxiv.org/abs/2606.06050v1), [17-page PDF](https://arxiv.org/pdf/2606.06050v1), [complete source](https://arxiv.org/src/2606.06050v1).
- [DLT 2026 final metadata](https://link.springer.com/chapter/10.1007/978-3-032-28404-4_18), final body unread.
- [Fisman–Frenkel–Zilles journal source](https://lmcs.episciences.org/11224), directed canonical-form and teaching-definition dependency.
- [Active symbolic-automata learning](https://doi.org/10.1007/978-3-319-96145-3_23) and [RTI](https://doi.org/10.1007/s10994-011-5265-4), directed historical interface checks only.
