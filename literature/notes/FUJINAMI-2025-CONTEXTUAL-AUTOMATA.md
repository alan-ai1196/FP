# Fujinami et al. (2025): learning components in their operational context

## Edition, sources and actual coverage

**Selected edition:** Hiroya Fujinami, Masaki Waga, Jie An, Kohei Suenaga, Nayuta Yanagisawa, Hiroki Iseri and Ichiro Hasuo, *Componentwise Automata Learning for System Integration (Extended Version)*, arXiv **2508.04458v1**, August 6, 2025 at 13:58:34 UTC, 33 pages. The inspected primary history lists only v1.

Primary sources:

- [Versioned arXiv record](https://arxiv.org/abs/2508.04458v1), [selected PDF](https://arxiv.org/pdf/2508.04458v1) and [complete TeX](https://arxiv.org/src/2508.04458v1).
- [Official Springer chapter](https://link.springer.com/chapter/10.1007/978-3-032-08707-2_1), ATVA 2025, LNCS 16145, pp. 3–26. First online October 26, 2025, while the publisher's citation and copyright year is 2026. DOI 10.1007/978-3-032-08707-2_1.
- [Versioned artifact record](https://zenodo.org/records/15846781), DOI 10.5281/zenodo.15846781, issued July 9, 2025, version 0.1.0-SNAPSHOT. The record identifies implementation sources, experiment results and reproduction scripts. Its concept DOI is separately 10.5281/zenodo.15846780.

**Fully read by Pro-E on November 27, 2026, Shanghai:** all 33 pages, Sections 1–6, Appendices A–C, nine definitions, two formal problems, two theorem statements, three examples, one remark, the printed proof sketch, all formulas, four algorithms, 11 figures, five tables, four ordinary footnotes, two author-note texts and all 29 references. Continuous extracted text was read in large blocks. All figure, table and algorithm pages and the quotient/network and complexity formulas were visually inspected. The two rotated tables were also inspected in their upright orientation.

The selected paper contains **one explicitly labelled proof sketch and no standalone full proof environments**. Appendix C's title does not supply full theorem proofs. Four `auxproof` blocks are excluded from the compiled TeX and are not counted as published evidence. Complete source and its active inventory were checked by a support reader. This note does not turn full reading into full theorem certification.

The publisher's separate 24-page body was inaccessible behind a subscription redirect and was not aligned or credited as fully read. Its public bibliography has 30 entries, adding the extended version. Support readers separately checked metadata, bounded formal consequences and experimental resources. Small artifact source and script files were inspected without executing them. The main reader checked the random-word oracle, benchmark seed settings and aggregation logic directly. No full implementation audit, raw-results reconciliation, experiment or formal verification was performed. No FP core file was changed and no FP mapping is asserted.

## 1. The learning opportunity

The paper studies a system integrator who knows how components are wired together and can query each black-box component directly. This is a richer interface than observing only an assembled black-box system. Its value is that a learner can acquire a compact description of the components' **context-relevant behavior**, without learning every functionality those components support in isolation. [Sections 1, 4]

For example, a communication component may support several protocol modes while the assembled system exercises only one. Learning the unused modes can consume many queries and states without improving the model of this particular system.

The proposed CCwL* algorithm maintains one observation table per component. It uses the current hypothesized network to decide which one-step component extensions matter, asks direct component output queries for them, and uses whole-system counterexamples to trigger refinement. The mechanism constructs component models from observations, but the component boundaries, wiring, synchronous semantics and query access are supplied. It is not a method for discovering an unknown decomposition from an undifferentiated stream.

The resulting system model is intended to reproduce all system input/output traces under exact equivalence queries. The objective is not recovery of the original internal state names, global minimization of component sizes, or unrestricted component substitution into arbitrary new networks.

## 2. Synchronous Moore networks

A component is a finite deterministic Moore machine

\[
M_c=(Q_c,q_{0,c},I_c,O_c,\Delta_c,\lambda_c).
\]

Its output depends on its current state. A transition consumes the input at the current tick, and its effect appears in the next tick's output. The formalism permits partial transition functions. Its trace semantics includes the initial output and stops when a transition is undefined. Thus a complete run on m inputs produces m+1 outputs. [Definitions 2.1–2.2]

Each directed network edge e has a finite alphabet Σe. A component's input alphabet is the product of its incoming edge alphabets, and its output alphabet is the product over outgoing edges. For joint state q, let o(q) collect all component outputs, including internal edges. A system input i induces

\[
q'_c=\Delta_c\left(q_c,(i,o(q))|_{E_c^{\rm in}}\right).
\]

All components update simultaneously. Cycles in the wiring are therefore well-defined: outputs at this tick are available before transitions are taken. The appendix's Mealy example explains why instantaneous output dependencies would require additional semantics in a cyclic network. It is not a general impossibility result for composing Mealy machines. [Definitions 2.3–2.5, Appendix C.1]

The joint state space is a product, with size at most Πc |Qc|. The component descriptions contain a sum of states. However, local input alphabets are also products, and reachability analysis may visit many joint states. Sum-of-states learning does not automatically imply polynomial computation in that sum.

A component can be partial outside the local inputs induced by its network, while the assembled system remains complete. This is the formal source of useful context-specific incompleteness.

## 3. How the learner acquires a contextual model

### 3.1 Observation tables and discriminating suffixes

Each component table has access prefixes Sc, selected one-step extensions Rc, distinguishing suffixes Ec and observed outputs Tc. Rows describe how an access prefix responds to the selected suffixes. A new row distinct from all current state rows becomes a state. A valid counterexample supplies a suffix that distinguishes previously conflated behavior. [Section 3, Algorithm 1]

The contextual modification concerns which extensions enter Rc. Ordinary componentwise L* tries all local input letters at each learned state. CCwL* first asks which state/input combinations can arise in the current composed hypothesis. Only those selected extensions need new table observations.

Three approaches therefore use different interfaces:

| Learner | Output queries | Equivalence queries | Structural information used |
|---|---|---|---|
| MnL* | Whole system | Whole system | Monolithic model |
| CwL* | Individual components | Individual components | Known component decomposition |
| CCwL* | Individual components | Whole system | Known decomposition and contextual reachability |

Problem 4.1 lists all these oracles, but CCwL* does not need component equivalence queries. The comparison with MnL* includes a deliberate information-access difference. Comparison with CwL* tests how the same available component access is directed toward the assembled-system objective. [Section 4]

### 3.2 Approximation used for context analysis

Two parameters control the context analysis:

- **E:** an equivalence relation used to quotient each current hypothesis for analysis only. Choices include equality, equality of observations through depth k, equality of current outputs, and the universal relation.
- **R:** a reachability-search depth. D∞ performs full search, while Dd stops after depth d.

The quotient keeps the union of outputs and possible transitions from every representative. It is nondeterministic, even though learned component hypotheses remain deterministic. Quotienting is not a claim that the merged states are behaviorally equivalent. It intentionally overapproximates the current hypothesis. [Definition A.3, Algorithm 2]

For complete search of this quotient, every concrete hypothesis state/input opportunity is represented. For finite depth, an opportunity may be missed. The paper calls these choices sound and unsound respectively. This terminology concerns the context analysis. It does not mean a truncated analysis must produce an incorrect final model when an exact system-equivalence oracle continues to return counterexamples.

Algorithm 4 handles a hypothesis that gets stuck on a system counterexample by inserting a missing local transition. Otherwise it refines a component using an output counterexample. The analysis is repeated after hypotheses change. A sound abstraction of the **current hypothesis** is not prior knowledge of the unknown target's exact reachable states.

### 3.3 Why coarse quotienting can remain useful

With the universal equivalence, each abstract component has one state but may emit every output currently present in that component hypothesis. The abstract product then has only one configuration, so depth zero can cover all abstract configurations. It can still remove input letters that no component can emit, while losing temporal correlations between outputs.

This explains the source's distinction between non-temporal redundancy and temporal redundancy. A never-used input symbol can be excluded by coarse output-set analysis. An input that is possible only after a particular protocol history requires more state information. [Section 5, RQ1]

The cost is not necessarily negligible: a single abstract configuration can have a large product of possible outputs, and Algorithm 2 enumerates those outputs and their induced local inputs.

## 4. Constructive deductions from the interface

The following results are independent, conditional deductions. They are not source theorems, novelty claims or proposed FP changes.

### 4.1 Overapproximation gives a safe extension set

Fix one hypothesis network H and any family of component equivalences. Map a concrete state tuple to its tuple of equivalence classes. Each concrete component output is among the quotient outputs, and each concrete transition maps to a quotient successor. Induction on a system word therefore maps every concrete reachable tuple into an abstract reachable tuple.

Algorithm 2 considers each representative in each reachable abstract class and each possible abstract output. Thus, with complete abstract reachability, its extension set contains every state/input pair arising in the concrete hypothesis. The abstraction may add spurious pairs, causing extra queries. It cannot omit a concrete hypothesis pair under these conditions.

This proof supplies the precise safety contract for pruning. Depth truncation can violate the reachability premise. Changing the hypothesis also changes the contract and requires recomputation.

### 4.2 Turn a system counterexample into a local one with direct queries

Suppose deterministic H executes system word w completely and an exact system-equivalence oracle reports that w distinguishes H from the true network M. Simulate H on w and record, for each component c, the complete local input word uhat(c) induced by the **hypothesis outputs**.

Query the true component once on each uhat(c), and compare its full output trace with Hc on that same word. At least one comparison must differ.

Proof: if every local comparison agreed, start with the initial outputs and induct over ticks. Agreement of all previous component outputs makes the local inputs induced in M equal to those computed in H. The assumed equal local traces then make the next outputs equal as well. This would make the system traces on w equal, contradicting the counterexample.

Every differing comparison is already a genuine local counterexample: both the true and hypothesized component were evaluated on the same input word. It can be passed directly to the ordinary suffix-refinement routine.

The construction uses at most |Vc| component output queries and |Vc||w| component input symbols, plus local simulation and the subsequent suffix search. It assumes the paper's full-trace, resettable component-output interface. A unit output query and its consumed symbol count remain different costs. If H gets stuck, first apply the source's missing-transition branch.

This is a conditional alternative to the printed total-output reconstruction step, not a claim about what the implementation does. It avoids assuming that the entire actual internal trace of a feedback network is free to reconstruct.

### 4.3 Earliest disagreement supplies a causal witness

If the actual and hypothesis total output traces are available, there is another exact localization rule. Let t be the first tick at which any component output differs, and choose a component c differing at that tick. All outputs before t agree. Hence the actual and hypothesis local input words supplied to c before t are identical. Their outputs at t differ on that same word, producing a valid component counterexample.

The earliest-time condition is useful. An arbitrary downstream component may have a different global trace merely because an upstream hypothesis supplied it different inputs. Algorithm 2's line 27 names a component with an incorrect global output trace but does not state this earliest-time selection. The construction above provides a sufficient choice without requiring arbitrary blame assignment to work.

### 4.4 An exact contract for reuse in another context

Consider a new known synchronous context C containing true components Mc. Let Uc contain every local input word induced at component c by all system words in C[M], including the empty word and prefixes. If the true network stops, also include the local prefix ending with that first blocked system transition's attempted input, even though the transition does not complete. Suppose replacement Hc agrees with Mc on the complete output trace of every word in Uc, with the same required transition definedness.

Then replacing the components simultaneously preserves the entire system behavior:

\[
[[C[H]]]=[[C[M]]].
\]

The proof is a joint induction over time. Equal initial outputs give equal initial local inputs. At each later tick, equality of earlier edge outputs makes the replacement's local word equal to a word in Uc. The local trace premise supplies equality at the next tick. Matching definedness handles the stopping boundary for partial machines.

This gives a precise domain for component reuse. A learned component need not be correct on every imaginable local input if the new context stays within its certified domain. Conversely, equivalence of two systems in an old context does not alone establish this componentwise contract in a new one. Unknown wiring or an expanded set of local inputs requires additional evidence.

## 5. Query guarantees and explicit accounting

### 5.1 What the source states

For exact oracles and full context reachability, Theorem 4.2 states

\[
O(\ell n^2+n|V^c|\log m)
\]

component output queries and O(n) system equivalence queries, where n is the sum of true component state counts, m is the maximum counterexample length, and the printed definition makes ell the **system-level input alphabet size**. For truncated reachability it adds O(ell n |Vc|) output queries and O(ell n) equivalence queries. The short proof sketch attributes the extra component factor to total-output counterexample analysis and the truncated case to transition additions. [Theorem 4.2, pp. 14–15]

These are query claims, not computation, memory, reset-time or symbol-processing bounds. Moreover, the literal system-alphabet parameter needs qualification.

### 5.2 A bounded family exposing the local alphabet factor

Let p ≥ 3 be odd. Three components are unary cycles of lengths p, p+1 and p+2. Each outputs its current residue both to a receiver and to a system output edge. All advance on the single system input. The receiver has one state and constant output on every input tuple.

The true component state sum is n=3p+4, the system input alphabet has size one, and there are four components. The three periods are pairwise coprime. The Chinese remainder property implies that all

\[
P=p(p+1)(p+2)
\]

residue tuples occur at the receiver.

The visible outputs force an exact system learner to represent the three cycles. Once those source states have been learned, universal quotienting exposes all P tuples as possible outputs in its single abstract configuration. Algorithm 2 then admits all P receiver one-letter extensions. Each requires at least the empty-suffix output observation. Exact reachability also contains these tuples, so the issue is not merely spurious abstraction.

The visible cycles admit counterexamples of length O(p), while the receiver is always constant. Thus P grows cubically in p, whereas the printed ell=1 expression grows quadratically, up to its smaller logarithmic term. This analytic family shows why that literal parameterization is insufficient. It does not negate the contextual learning mechanism or claim a lower bound for every possible learning algorithm.

### 5.3 Charge the table entries actually acquired

A direct accounting is available without hiding local alphabets. Let sc and rc be the final numbers of access and selected-extension rows, and ec the final number of suffixes. With cached monotone table filling, at most

\[
\sum_c(s_c+r_c)e_c
\]

distinct table-cell observations are requested, before counterexample-analysis queries. Coincident concatenated words may reduce this number.

If the usual valid-counterexample row-progress argument gives sc ≤ nc and ec ≤ nc, and every local letter may be admitted, then rc ≤ nc |Ic| supplies the familiar upper expression

\[
\sum_c n_c^2(1+|I_c|).
\]

For a contextual run, the actual selected rc can be much smaller. This is exactly where contextual pruning can save queries. The local replay construction in Section 4.2 separately costs at most |Vc| resets and |Vc|m symbols per system counterexample, before the chosen local suffix search.

These are conditional counting statements, not a replacement proof of every termination and complexity claim in the source. They make the relevant query, alphabet and word-length costs available for a concrete implementation.

## 6. Experimental evidence and artifact boundaries

### 6.1 What was tested

The Scala implementations run against Moore-network teachers treated as black boxes. Benchmarks include complete, star and path networks of generated components, a deliberately redundant component family, an MQTT-inspired lighting model, and binary counters. Lean random components have state counts drawn around Normal(10,1), with edge alphabet sizes from 2–5. Rich components add a second mode that the assembled system does not invoke. This is a controlled redundancy mechanism, not a random sample of industrial systems. [Section 5, Appendix B]

The lighting model adapts a protocol model and fixes the clients' used modes. The binary counter is a synchronous model whose intended counting behavior requires spacing input ones with zeros for carry propagation. The study runs simulated teachers, not physical automotive equipment or a hardware-in-the-loop installation.

Runs use AWS r7i.2xlarge instances, eight virtual cores and 64 GB RAM, with a 3,600-second learning timeout. Learner and teacher run on the same machine. Equivalence queries during learning use random words. After learning returns, a separate exact system-equivalence check classifies the result. Its validation time is excluded from the learning timeout. [Section 5]

### 6.2 The archived oracle and averages

Bounded inspection of the versioned artifact clarifies the practical interface:

- `scripts/benchmark_full.sh` sets 100 random words per EQ, lengths from 10 through 500. Generated target seeds are 1–10 with oracle seed 42. Fixed realistic targets use oracle seeds 42–51.
- `src/main/scala/learn/mmn/lstar_moore.scala`, `OracleGen.randomWord`, initializes its random generator from the same seed inside each EQ call. Repeated calls therefore do not provide fresh independent test streams.
- `scripts/table.rb` averages numerical quantities over completed runs, including runs later found invalid, while excluding timeout/error runs. The validity triple must be read alongside every mean.
- The same aggregation script defines learner time as total learning time minus component/system OQ and EQ execution time. It sums component and system reset/step counts in the published columns.

These observations concern the archived scripts and selected source paths. They do not establish an independently reproduced numerical result. The generator syntax `10±3` maps to Normal(10,1) in the inspected parameter parser, so it does not contradict the paper's stated distribution.

### 6.3 Useful results and costs

On MQTT Lighting, the reported contextual Eq,D∞ model uses 27 component states and 130 transitions, compared with 39 states and about 2,500 transitions for CwL*. Output-query resets decrease from about 12,000 to 348, and output-query steps from about 61,000 to 2,400. Both have 10/10 exact post-run validations. Learner-only time increases from 0.76 to 1.36 seconds. These numbers support the intended benefit: spend local analysis to avoid unnecessary component interaction. [Table 2]

On the deliberately rich complete-graph family, CwL* learns an average 747 component states, compared with 47.3 for Eq,D∞, with 10/10 validations for both. The contrast is substantial but concerns redundancy deliberately inserted by the generator.

Full context search can be expensive. On Star(7),LeanComp, Eq,D∞ completes and validates only one of ten runs, with nine timeouts. Its smaller mean model is therefore not a ten-run performance advantage. Eq0,D∞ completes and validates all ten, at a much larger query count but less costly context analysis. [Table 3]

Truncated search and approximate EQs can combine poorly. For BinaryCounter(10), Eq,D0 returns ten models that all fail the exact validation, while Eq,D∞ validates all ten. Even nominally sound full context analysis is not an exact-learning certificate with the practical EQ: Path(5),RichComp has two invalid Eq,D∞ returns. [Table 2]

No confidence intervals or independent replication are established by this reading. Ten generated targets and ten oracle seeds for one fixed target measure different sources of variation. The limited benchmark families and failure-conditioned averages should not be promoted to universal scalability conclusions.

### 6.4 A usable cost comparison

For a specified deployment, let L be learner time, R the reset count, S the consumed-symbol count, and assign common costs cr and cs to resets and steps. Ignoring validation or charging it separately gives

\[
C=L+c_rR+c_sS.
\]

One method is preferable precisely when its saved interaction cost exceeds its extra learner cost. With heterogeneous components or different system-level interfaces, use separate sums over those interfaces instead of common cr and cs. The published aggregate columns cannot recover all such heterogeneous costs.

For the MQTT example, the reported rounded counts imply about 11,952 fewer total resets and 135,600 fewer total steps, for 0.60 additional learner seconds, using both OQ and EQ columns. Under the common-cost model this gives the illustrative condition

\[
11952c_r+135600c_s>0.60.
\]

The arithmetic is derived from rounded table means and excludes the separately timed validation. It is not a measured hardware-in-the-loop speedup. It shows how to turn the source's cost tradeoff into a concrete deployment question.

## 7. Retained tools and limitations

The source's useful contribution is a learning loop in which current component hypotheses determine what additional component behavior needs to be observed. Nondeterministic quotienting provides a tunable overapproximation for this decision. Whole-system feedback can then refine a local model.

The independent replay construction makes that feedback localization executable through the stated component-output interface. The local-domain theorem gives a precise condition for reuse in a changed context. Explicit table and interaction accounting retains the benefit of context pruning without suppressing local alphabet, product reachability or oracle costs.

These results concern known synchronous composition and active access to resettable components. They do not show autonomous discovery of component boundaries, unrestricted reuse of a context-pruned model, passive identifiability, a polynomial total runtime, or acquisition of an FP architecture. Those stronger tasks require additional objects and assumptions.
