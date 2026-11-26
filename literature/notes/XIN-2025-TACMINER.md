# Xin et al. (2025): dependency graphs for learning reusable proof tactics

## Edition, sources and actual coverage

**Selected edition:** Yutong Xin, Jimmy Xin, Gabriel Poesia, Noah Goodman, Qiaochu Chen and Isil Dillig, *Automated Discovery of Tactic Libraries for Interactive Theorem Proving*, arXiv **2503.24036v2**, revised August 22, 2025, 36 pages. The first version is March 31, 2025. The published article is *Proceedings of the ACM on Programming Languages* 9, OOPSLA2, Article 343, DOI **10.1145/3763121**, published October 9, 2025. The journal author list uses Noah D. Goodman and Işıl Dillig.

Primary sources:

- [Versioned arXiv record](https://arxiv.org/abs/2503.24036v2), [36-page PDF](https://arxiv.org/pdf/2503.24036v2) and [TeX source](https://arxiv.org/src/2503.24036v2).
- [Author-hosted 28-page journal copy](https://www.cs.utexas.edu/~isil/tacminer.pdf), [publisher DOI](https://doi.org/10.1145/3763121) and [official OOPSLA program](https://2025.splashcon.org/details/OOPSLA/142/Automated-Discovery-of-Tactic-Libraries-for-Interactive-Theorem-Proving).
- [Public implementation](https://github.com/mx-xn/TacMiner) and [archival software DOI](https://doi.org/10.5281/zenodo.15761151). The repository metadata and README were inspected. The artifact was not executed. Zenodo archive access returned 403, while DataCite authenticated the software record.

**Reading completed by Pro-E on November 26, 2026, Shanghai:** all 36 PDF pages, Sections 1–11, Appendix A's four theorem proofs, Appendices B–D, all mathematical definitions and formulas, all 25 figures, four tables, four scientific footnotes, acknowledgments and 60 references. Complete extracted text was read in continuous page blocks. Source was consulted for algorithms, active versus commented evaluation text and footnotes. All figure-bearing pages were visually inspected, including the two appendix figures.

Bounded support readers separately compared editions, examined the theorem interfaces and assessed evaluation resources. Their work did not replace the main reader's complete reading. The first 28 pages of v2 and the author-hosted journal copy have identical extracted word sequences after removing running headers, arXiv stamping, template warnings, author typography and the 36-versus-28-page citation field. This is text alignment, not binary or image identity. The journal edition receives a separate alignment record, not a second full-reading credit. No later arXiv revision or correction relation appeared in the primary metadata checked. The ACM landing page and Crossmark endpoint were inaccessible, so this is not a comprehensive correction audit.

No independent implementation audit, experiment replication, proof-assistant replay or complete certification of the discovery algorithm was performed. Independent mathematical deductions below are explicitly conditional. No FP core files were changed.

## 1. What is constructed

TacMiner constructs **parameterized composite tactics from existing successful proofs**. Its central representation is a tactic dependence graph, or TDG. A vertex is an executed tactic invocation. An edge records which output of one invocation supplies which input of another. This removes irrelevant identifier choices and some ordering differences while retaining the dependencies needed to execute the proof.

The constructive sequence is:

1. Execute or parse proof traces sufficiently to expose consumed and produced objects.
2. Represent their dependencies as port-labeled DAGs.
3. Find repeated graph regions that can be contracted without violating dependencies.
4. Turn the region's incoming and outgoing boundary into a reusable tactic interface.
5. Replace occurrences by calls to the new tactic, then repeat discovery on the shortened corpus.

The useful advance over consecutive-string abstraction is concrete. Two operations separated in a script can belong to one reusable region when intervening operations are independent. Conversely, identical tactic-name sequences cannot necessarily be abstracted when implicit proof-state dependencies differ. Figures 1–11 illustrate both situations. [Sections 2–4]

The input already supplies primitive tactics, their execution semantics, a proof assistant and successful proof scripts. The learned objects are compositions of those operations. The paper does not establish invention of new primitive proof rules, induction from unstructured sensory observations, or prediction-induced state formation. It is nevertheless a direct constructive example of acquired operations that can be reused across different proofs.

## 2. Explicit inputs make the graph semantics possible

### 2.1 Proof-state interface

A proof state maps identifiers to hypotheses or goals. A goal includes a proposition and the hypotheses in its context. A tactic definition has a name, formal inputs, formal outputs and a body. An invocation binds actual input and output identifiers. Consumed goals are removed, hypotheses persist, and produced identifiers are fresh. A proof succeeds when no goals remain. [Section 3]

A crucial assumption is **determinism relative to every consumed input**. This includes goals, hypotheses, hint databases and any other state affecting the invocation. Two invocations with equal recorded inputs must produce equal outputs even if unrecorded parts of the ambient proof state differ. Thus the abstraction is not justified merely by recording tactic names.

For an invocation graph, an edge labeled \((\alpha,\beta)\) identifies a producer's formal output port \(\alpha\) with a consumer's formal input port \(\beta\). Special boundary nodes in a tactic TDG describe its external interface. They are not body invocations and should not be charged as such in the compression objective. [Definitions 4.1–4.2]

### 2.2 What the reordering theorem establishes

**Author Theorem 1, Appendix A:** topologically reordering the TDG preserves the proof and its invocation count under the formal execution model.

The proof invariant is that every executed node receives the same actual inputs and produces the same outputs as in the original trace. Complete dependency recording places each producer first. Persistent hypotheses remain available. A goal is consumed by exactly one invocation, so no unrelated earlier step can remove it. A conceptual initial node produces the starting inputs.

The paper's main text additionally restricts induced scripts to topological orders satisfying branching constraints. Its implementation performs branch analysis when emitting Ltac. Therefore this is a theorem about explicit-input executions, with a branch-respecting serialization interface. It is not permission to arbitrarily reorder textual Ltac commands. [Section 4, Section 7, Appendix A pp. 29–30]

## 3. A safe region becomes a reusable operation

### 3.1 Collapsibility

An isomorphic embedding preserves tactic labels and port-labeled edges. This alone is insufficient. Let \(S\) be the selected vertices inside a host proof DAG \(P\). Definition 4.4 requires:

- **Dependency convexity:** whenever \(u,v\in S\) and \(u\leadsto w\leadsto v\), then \(w\in S\).
- **Complete internal dependencies:** the candidate includes every host edge whose endpoints lie in \(S\).

The first condition prevents a proposed macro from needing an outside operation between two of its own steps. The second prevents an apparently matching body from omitting an actual internal dependency. Boundary rewiring then converts host actual arguments into the macro's formal arguments. [Definitions 4.3–4.4, Figure 10]

**Author Theorem 2:** repeatedly finding and contracting a currently collapsible occurrence preserves proof validity. Different choices among overlapping occurrences can produce different refactorings. Semantic preservation of each valid contraction does not require a globally unique decomposition. [Section 4, Appendix A pp. 30–31]

### 3.2 Independent conditional contraction lemma

The following spells out the reusable graph argument behind the source theorem.

**Assumptions.** \(P\) is a finite DAG describing an actual successful execution. Dependencies are complete, invocations are input-local and deterministic, hypotheses persist without hidden mutation, and goals have fresh identities and unique consumption. The nonempty region \(S\) is dependency-convex, its body is the full induced graph \(P[S]\), and its interface preserves every boundary value and port correspondence. Renaming avoids capture. Macro semantics execute a topological ordering of the body.

**Conclusion.** Contracting \(S\) to one macro vertex, deleting all internal edges and rewiring the boundary gives another DAG. Expanding that macro in any topological order of the quotient yields a topological order of the original graph and preserves the execution.

**Proof.** A new cycle would have to pass through the macro vertex. Lifting the segment that leaves and reenters the macro gives a path in \(P\) with both endpoints in \(S\) and an outside intermediate vertex. This contradicts convexity. Internal self-edges are removed. Hence the quotient is acyclic. On expansion, internal edges are respected by the body's order, boundary edges by the quotient's order, and all other edges are unchanged. The input/output invariant from Section 2.2 therefore applies. Macro evaluation agrees with its expansion. Actual Rocq serialization must also satisfy branch scope. \(\square\)

This is a conditional source-level derivation, not a new general theory of learned computation. Convexity supplies a scheduling condition. Complete internal edges and boundary ports supply the execution interface.

For several regions, use sequentially checked valid contractions or a jointly acyclic quotient with valid interfaces. Vertex-disjointness alone is a packing condition and should not silently become a semantic guarantee for simultaneous contraction.

## 4. How the discovery search exploits structure

### 4.1 Corpus objective and grammar

Let \(C=\sum_{\pi\in\Pi}|\pi|\), where size counts tactic invocations. The paper defines

\[
\operatorname{CP}(\tau,\Pi)
=\frac{C}{\sum_{\pi'\in\operatorname{Refactor}(\Pi,\tau)}|\pi'|}.
\]

For a body of size \(m\) used at \(k\) legally replaceable occurrences, the call saving is \(k(m-1)\). Under the paper's nonoverlap accounting, effectiveness is

\[
\mathcal E(\tau,\Pi)=(m-1)F(\tau,\Pi),
\]

where \(F\) counts collapsible embeddings. This makes maximizing effectiveness equivalent to maximizing CP when the counted occurrences can actually be realized. [Definitions 5.2, 6.4–6.5]

The algorithm first mines a graph grammar. A production

\[
\eta\longrightarrow(\eta',\theta)
\]

records a pair of observed tactic labels and the complete set \(\theta\) of port dependencies between that pair. Candidate expansion adds a fresh target node with these edges or adds edges to an existing node. This supplies a data-derived search restriction instead of proposing arbitrary graphs and testing them afterward. [Figure 13, Definition 6.6]

A candidate stores its graph and all current isomorphic embeddings in each proof. These witnesses need not yet be collapsible. Retaining them enables incremental witness extension and an optimistic bound. The source explicitly observes that collapsibility cannot in general be enforced incrementally. [Section 6.1]

### 4.2 Upper bounds as a constructive search tool

For a nonempty candidate \(G\) and a witness \(f\) in host proof \(P_\pi\), let \(M_{\pi,f}\) be the size of the largest permitted extension containing \(f(G)\) and preserving its designated root. The paper's optimistic bound is

\[
U(G,\Pi)
=\sum_{\pi\in\Pi}\sum_{f\in W_G(P_\pi)}(M_{\pi,f}-1).
\]

It sums over all isomorphic prefix witnesses, including currently noncollapsible ones. Any descendant can use only part of this optimistic capacity. Prune when the bound is below an already achieved score. [Definition 6.7, Figure 17]

**Independent charging argument.** Suppose \(H\) extends \(G\) without changing its designated root. In each host, choose a family \(\mathcal P_\pi\) of vertex-disjoint occurrences of \(H\). Restrict each selected occurrence \(g\) to \(f_g=g|_G\). Because \(G\ne\varnothing\), disjoint larger occurrences give distinct restricted witnesses. Because roots are preserved, \(g(H)\) is an admissible contender for \(M_{\pi,f_g}\). Therefore

\[
|H|-1\le M_{\pi,f_g}-1
\]

for every selected occurrence, and

\[
\sum_\pi|\mathcal P_\pi|(|H|-1)\le U(G,\Pi).
\]

The bound applies to an optimal disjoint packing and hence to any feasible sequence of contractions drawn from it. It does not require the total number of arbitrary embeddings to decrease during extension.

This distinction matters to Appendix A's printed proof of Theorem 3. Its restriction map from all larger witnesses to all smaller witnesses can be many-to-one, so that map alone does not prove the claimed witness-count inequality. Charging **selected disjoint occurrences** supplies the needed injection and preserves the useful upper-bound mechanism.

Finite hosts, finite labels, strict expansions and retained witnesses give a finite candidate universe. If candidate generation covers the chosen target class and the bound applies to its actual score, branch-and-bound can safely avoid unpromising descendants. There is no polynomial-time search guarantee here.

### 4.3 Scope of library optimality

The paper's Theorem 4 claims that LearnTactic finds a single tactic maximizing corpus compression. Definition 5.3 then defines a library by repeating single-tactic discovery on the refactored corpus. This is a greedy sequence of local objectives. It does not prove optimality over all final libraries or all extraction orders.

There is also a specific obstacle in the **displayed candidate filter**. Figure 16, line 11, retains a partial candidate only when its *currently collapsible* frequency is at least two. This can discard a prefix needed to assemble a useful completed graph.

A bounded example uses two disjoint proofs containing distinct-label dependencies

\[
r\to u,\qquad u\to t,\qquad r\to t.
\]

This graph is realizable: \(r\) produces a persistent hypothesis \(h\) and a goal \(g\), \(u\) transforms \(g\) into \(g'\), and \(t\) consumes \(h,g'\). The prefix \(\{r,u\}\) is collapsible. Adding \(t\) through either available pair production adds only one of its two incoming dependencies. The resulting three-node graph omits an internal host edge, has zero collapsible frequency, and is discarded before the missing edge can be added. Starting from \(\{r,t\}\) fails convexity. Starting from \(\{u,t\}\) cannot add the ancestor through the displayed outward expansions. The full triangle would save \(2(3-1)=4\) calls, while available two-node patterns save two.

Thus the literal algorithm does not establish the unrestricted claimed optimum. Even without this triangle, a frequency threshold of two excludes a beneficial one-occurrence macro under the printed objective, which does not charge its definition.

Two local repair candidates are to retain extendable isomorphic partial witnesses until scoring, or to add required induced dependencies and convex closure atomically. Neither is presented here as a fully proved repair. A complete claim would need a target class, complete root-preserving generation, a sound recurrence policy and feasible overlap accounting. This limited qualification leaves the dependency-safe abstraction and conditional upper-bound tools intact. No implementation failure is inferred from pseudocode alone.

## 5. Pricing a reusable library separately from its calls

The original CP objective measures shorter proof scripts **given an available library**. It does not charge the learned tactic bodies, formal interfaces, argument encodings or kernel execution work.

For an explicit alternative accounting model, suppose a macro has \(m\ge2\) unit-cost body calls, is legally used \(k\) times, costs one unit per invocation, and requires \(c\ge0\) additional units for its name and interface. Then

\[
\Delta_{\rm calls}=k(m-1),
\qquad
\boxed{\Delta_{\rm total}=k(m-1)-m-c.}
\]

Saving the definition is beneficial precisely when

\[
k>\frac{m+c}{m-1}.
\]

For example, a three-call body used twice saves four corpus calls. Charging the three-call definition leaves one unit before interface cost. A two-call body used twice saves two calls and merely pays back its body before interface cost.

This is an independent elementary accounting deduction under stated units, not the paper's objective and not a general minimum-description-length theorem. Token lengths, bits, argument binding and execution time can induce different thresholds. A macro can reduce search depth without reducing its expanded kernel work. It is useful to keep corpus reuse, stored library size and runtime as separate quantities.

## 6. What the experiments support

### 6.1 Three distinct evaluation populations

| Experiment | Information supplied | Supported observation |
|---|---|---|
| RQ1, discovery | Entire per-topic proof corpus used for mining | Learned library size and usage within that corpus |
| RQ2, refactoring | 65% of proofs for mining, 35% disjoint test proofs in the same topics | Transfer of executable dependency patterns to other proofs |
| RQ3, Copra | A selected set of 50 theorems, new tactic definitions and one different-lemma usage example per tactic | Utility of the library plus invocation guidance on a relevance-selected proving suite |

The source collections are CoqArt, Program Logics, CompCert and BigNums, with 14 curated topics. They are not a random sample of all Rocq projects. [Section 8.1, Table 2]

The adapted comparison is the authors' Rocq reimplementation of Peano's sequence anti-unification approach. It searches common consecutive tactic sequences, generalizes arguments and removes tactics that cannot refactor any proof. This is a useful syntactic-library comparator, but not an unchanged original Peano executable. [Appendix B]

### 6.2 Reuse on different proofs

RQ2 reports aggregate test compression power **1.35 for TacMiner and 1.10 for the adapted Peano baseline**. These correspond to approximately **25.9% and 9.1% fewer tactic invocations**. Figure 18 shows a TacMiner advantage in all listed topics. Mining uses 65% of proofs selected by an automated sampling script. The active text does not provide a seed or specify that sampling is random. [Section 8.3]

This is the paper's clearest evidence for acquired reusable operations: macros learned from one set of proofs are validly substituted into different proofs in the same topic. It supports within-domain reuse of existing semantic dependencies. It does not establish a distribution-free generalization theorem or transfer to unrelated domains.

### 6.3 Proof search with new operations

The 50 Copra problems were chosen because a smaller-budget preliminary run made partial progress but did not finish, and because their known refactored proofs used at least one TacMiner tactic. This selects intermediate-difficulty problems with known library relevance. The reported results are:

| Available tactics | Theorems proved |
|---|---:|
| Built-in tactics | 11/50, 22% |
| Adapted Peano library | 18/50, 36% |
| TacMiner library | 30/50, 60% |

The absolute gain over built-ins is 38 percentage points. The relative gain is approximately 172.7%. [Section 8.4, Table 4]

Appendix C explains the usable interface. New declarations are inserted before their first use. Available tactics are indexed by lemma. Refactored proofs are run through SerAPI to extract proof-state/action examples. Copra receives each tactic's definition plus one usage example from a **different lemma**. The authors qualitatively report that definitions alone often led the model to avoid new tactics or use invalid arguments.

Different-lemma demonstrations do not by themselves establish target-excluded library induction. The paper does not say that a target proof was excluded from mining the library used for its Copra attempt. It also does not state that the RQ2 split applies to RQ3. The source is insufficient to assert either clean target-excluded induction or contamination of every test case.

Available operations, definitions and demonstrations all change together. This is not an isolated action-vocabulary ablation. The model identifier is printed as **gpt-4o-2024-10-06**, which was not independently authenticated here. Numerical call, token and timeout budgets are not supplied in the inspected protocol. The experiment should not be described as matched in total inference compute.

### 6.4 Search resources and uncertainty

The reported machine is an Apple M2 with 24 GB RAM running macOS. Full-corpus TacMiner learning takes about 13 minutes. Removing upper-bound pruning or withholding argument-dependency labels from the grammar fails to finish within a 30-minute limit. Figures 20–23 plot cumulative time against the number of discovered tactics, with a logarithmic time axis. These experiments support the practical importance of grammar constraints and the optimistic bound. They do not establish polynomial scaling or equal-quality runtime comparisons at every point. [Sections 8.1, 8.6]

Figure 19 labels standard-error bars when varying training fraction. The active text does not specify repetitions or seeds. A paragraph giving five repetitions and a 30% randomly sampled test set is commented out in the TeX and is not part of the published protocol. No repeated-run uncertainty is reported for the three Copra counts.

Preserve two simple reporting discrepancies rather than silently repairing them:

- Section 8.1 says 918 proofs. Table 2's 14 rows sum to **819 proofs and 14,733 tactic applications**.
- Table 3's per-topic learned-tactic counts sum to **911 versus 307**, while its total row says **918 versus 310**. The usage totals **2,430 versus 842** agree with their rows.

These arithmetic observations do not determine the actual artifact population. Both learned-tactic tallies retain the approximate threefold discovery difference. They are proportionate reporting limits, not grounds to dismiss the constructive mechanism.

## 7. Implementation boundary

The implementation comprises about 5,000 Java lines and uses Coq-SerAPI. Its current target is Ltac. It can parse input scripts containing advanced tactics and existing custom tactics. Combinator bundles such as try, first and repeat are atomic for this representation, while sequencing is decomposed. [Section 7]

The learnable class is narrower than the accepted input class. Executed traces omit unexecuted branches, so the system does not synthesize new proof-state-dependent control flow from them. Existing state-dependent primitives can still appear inside a fixed composite. Evars are supported only with localized effects in the resulting proof states. Branch tracking is required when turning a graph back into a script.

For overlaps, the implementation uses backtracking to find a disjoint subset for effectiveness scoring. Retaining all witnesses in an optimistic upper bound is compatible with this strategy. It does not remove the need to check feasible contractions and the generator's coverage.

The paper and inspected README provide an available artifact and reproduction interface. No code audit, installation, kernel replay or end-to-end rerun was needed for this reading. Source claims about implementation behavior remain source claims.

## 8. Reusable instruments and FP boundary

The following instruments can be used independently of a proposed FP architecture:

| Instrument | Required interface | What it provides |
|---|---|---|
| Port-labeled execution DAG | Primitive semantics and complete consumed/produced values | An equivalence class of reorderings beyond string adjacency |
| Convex induced-region extraction | Deterministic input-local operations and complete boundary ports | A composite operation preserving the observed execution |
| Witness-cached graph expansion | Finite corpus and observed label/port grammar | A constructive hypothesis generator with reusable matching work |
| Root-preserving charging bound | Selected disjoint descendants and a maximum-extension envelope | Safe optimistic pruning when candidate generation is complete |
| Definition-inclusive accounting | Explicit costs for bodies, calls and interfaces | A concrete threshold for profitable persistent reuse |
| Different-proof refactoring test | Mining/test separation within a specified domain | Direct evidence that a learned operation recurs beyond its mining traces |

No formal transfer to prediction-induced state formation is asserted. A transfer would first have to supply a justified execution trace interface, learn or specify primitive semantics, define a valid contraction criterion in the target setting, and price the acquired library and its acquisition. TacMiner supplies a useful construction in a domain where those interfaces are unusually explicit.

The most useful research question left by the paper is constructive: how to acquire a graph-level abstraction while keeping its dependency closure, generation completeness and installed cost explicit. That question can be studied without treating the literal optimality claim as established and without replacing FP's current research route.

## 9. Completion and continuation

This completes the selected 36-page edition. The journal counterpart is separately text-aligned. Screened 2025–2026 program-induction and automata candidates are recorded in the dated discovery ledger, with actual assistant/main-reader coverage and unread bodies preserved.

During publication preparation, Astra's new request **2e7a6c9** was detected. Pro-A had already successfully claimed it in **c3f5217**. Pro-E respects that ownership and does not duplicate the requested joint-feature comparison. Request **59b8251** remains completed by Pro-E in **8cd79d0**.

No FP architecture, learning rule, experiment protocol or core research file was changed.

