# Presynthesis: compiling a supplied program space for repeated search

## Source, edition and actual coverage

Rui Dong, Qingyue Wu, Danny Ding, Zheng Guo, Ruyi Ji and Xinyu Wang. **Presynthesis: Towards Scaling Up Program Synthesis with Finer-Grained Abstract Semantics.** PACMPL 10, PLDI, Article 210, June 2026, DOI [10.1145/3808288](https://doi.org/10.1145/3808288).

- **Selected full reading:** [arXiv 2604.13290v2](https://arxiv.org/abs/2604.13290v2), submitted April 16, 2026 at 01:44:09 UTC, [32-page PDF](https://arxiv.org/pdf/2604.13290v2) and [complete TeX](https://arxiv.org/src/2604.13290v2). The journal citation says 25 pages. The extended PDF adds Appendices A–D on pp. 26–32.
- **Publication authentication:** [official PLDI program](https://pldi26.sigplan.org/details/pldi-2026-papers/45/Presynthesis-Towards-Scaling-Up-Program-Synthesis-with-Finer-Grained-Abstract-Semant) and the [25-page author-hosted copy](https://web.eecs.umich.edu/~xwangsd/pubs/pldi26.pdf). The ACM endpoint returned HTTP 403. The author copy is not represented as a directly retrieved publisher Version of Record. It still has an extended-version self-reference with an arXiv placeholder. Main-text comparison found citation renumbering and appendix-pointer differences, without an observed experimental-number change. The PDFs are distinct.
- **Full reading by Pro-E, November 26, 2026, Shanghai:** all 32 pages through the 32 active TeX files, main Sections 1–7, all Appendix A proof steps, Appendix B SQL rules, Appendices C–D representative rules, Algorithm 1, Figures 1–23, Tables 1–5, footnotes and all 59 printed references. Original PDF inspection covered pp. 3, 5, 6, 11, 13, 17, 19, 21, 30–32. The two plotted result figures have labels missing from the arXiv text layer and were read visually. Other formula figures and tables were read in their active source.
- Inactive draft files were excluded. In particular, the Appendix A source stops at its first endinput, and the old RQ2 table is not included by the main source. The author copy received edition comparison only, not an additional full-read count.
- **Artifact scope:** [Zenodo 19078478](https://zenodo.org/records/19078478), March 18, 2026, and its [README](https://zenodo.org/records/19078478/files/README.md?download=1). Read resource requirements, pipeline, source organization, executable descriptions, benchmark schema and abstract-transformer contract. The 1.5 GB archive, source implementations, logs and benchmarks were not downloaded or executed.
- Bounded assisting checks covered source matching, the oracle invariant, the nullary-rule interface, three SQL row-count rules and amortization arithmetic. The main reader personally checked the cited passages and arguments. No formal certification or benchmark reproduction is claimed.

Selected PDF SHA-256: 191dbdf5241ea1aa56495d5631e3f6c643ee78105850eb85364a1731e93bb439. Source archive: 32a33f7087c813192edc6e2bab92b9c22be6eb62c7c20aaedc91d3e25523390e. Author PDF: 2df45324cb5927d7b15816098dfb9e987ceaad52b92cd09dbad86f2290286c5c. Retrieved README: a9a3613677f6f28b39347cb070648b6ad924f5f691b7d25f4c7896fa3c33d013.

**Assessment.** The useful construction is an offline finite tree automaton over supplied abstract semantics, together with an oracle that preserves a single consistent input environment across a program's leaves. The online slice exactly represents abstract consistency with one example. Concrete search still checks all examples. This is reusable compilation of a prescribed search space, with substantial preprocessing and memory costs. It does not learn the DSL, abstraction or a reusable program library. A missing variable exclusion in the printed slicing rule has a direct local repair. Three SQL row-count formulas have literal soundness counterexamples, which qualify that instantiation without refuting the generic conditional theorem.

## 1. The synthesis problem and supplied structure

The input is a DSL grammar \(G\), its concrete semantics, an abstract semantics and a finite example set \(E=\{(I_i,o_i)\}\). The goal is some \(P\in L(G)\) satisfying every example under concrete execution. Identifying an intended program outside those examples is a separate requirement.

The analysis assumes a finitized, acyclic grammar, obtained for example by unrolling a recursive grammar to a supplied depth. Operators, variables, constants and the depth or cost bound are prescribed. For each input variable \(x\), a finite enumerable set \(D_x\) covers the abstract inputs of interest. The abstraction \(\alpha_x\) and concretization \(\gamma\) obey

\[
c\in\gamma(\alpha_x(c)).
\]

An operator's abstract transformer must be sound:

\[
c_i\in\gamma(a_i)\quad\forall i
\quad\Longrightarrow\quad
f(c_1,\ldots,c_r)\in\gamma(f^\#(a_1,\ldots,a_r)).
\]

The global abstract universe need not itself be finite. Finite leaf choices and an acyclic finite grammar suffice for a finite construction, assuming effective transformers and decidable equality and consistency checks. The resulting size can still be enormous. Every reference to all programs below means programs in this finitized \(G\), not an unrestricted recursive DSL.

The paper supplies abstraction families for SQL, strings and matrices. Increasing precision means adding prescribed predicates. No objective or algorithm in this paper discovers those predicates from prediction errors.

## 2. Offline FTA and the input-provenance oracle

### 2.1 What is shared

A state \(q_s^a\) records a grammar symbol \(s\) and abstract output \(a\). Offline construction includes variable transitions \(x\to q_s^a\) for covered \(a\in D_x\). For a production \(s\to f(s_1,\ldots,s_r)\), compatible child states produce

\[
f(q_{s_1}^{a_1},\ldots,q_{s_r}^{a_r})
\longrightarrow q_s^{f^\#(a_1,\ldots,a_r)}.
\]

States with the start grammar symbol are final. Programs with the same intermediate abstract behavior share states. The construction also shares those states across covered input assignments, unlike a fresh example-specific automaton.

This cross-input sharing introduces a consistency issue. An unconstrained run may select different abstract values for repeated occurrences of the same input variable. For example, with identity abstraction and \(D_x=\{0,1\}\), a run for \(x+x\) can combine a zero-valued leaf and a one-valued leaf to reach output 1. No single covered assignment to \(x\) gives that execution. This elementary example explains why offline FTA acceptance alone is insufficient.

### 2.2 Exact meaning of the oracle

The oracle \(O(q)\) is a Boolean constraint over one global abstract environment

\[
\Gamma\in\prod_xD_x.
\]

For an incoming transition \(\delta\), its contribution is

\[
\Psi_\delta=
\begin{cases}
(x=a),&\delta=x\to q_s^a,\\
\bigwedge_{i=1}^{r}O(q_i),
&\delta=f(q_1,\ldots,q_r)\to q,\quad f\text{ not an input variable}.
\end{cases}
\qquad
O(q)=\bigvee_{\delta\text{ entering }q}\Psi_\delta.
\]

Non-variable constants use the empty conjunction, hence True. Variable leaves use their equality constraint, not that empty conjunction. The invariant established in Appendix A is

\[
\Gamma\models O(q)
\quad\Longleftrightarrow\quad
\text{some run to }q\text{ has every variable leaf consistent with }\Gamma.
\]

The proof is structural induction on the acyclic construction. The forward direction picks a satisfied incoming alternative and consistent child runs. Their conjunction is evaluated at the same \(\Gamma\), so they can be assembled without conflicting bindings. The reverse direction decomposes an existing consistent run. The mixed \(x+x\) run above contributes \((x=0)\land(x=1)\), which is false.

The implementation description converts the constraints to a set representation and uses lookup. It also precomputes an input-to-reachable-final-states map. Constant-time hash membership is a data-structure access convention. Encoding a long input environment, enumerating a returned set of final states and scanning transitions still have costs.

Let \(U=\prod_x|D_x|\). A dense state-environment incidence table alone can use \(|Q|U\) bits. This is an elementary possible representation cost, not a lower bound on every compressed oracle. Neither the paper's invariant nor its hash implementation establishes polynomial preprocessing in the number of variables, grammar depth or predicate count.

## 3. What the slicing theorem guarantees

For \(e_1=(I_1,o_1)\), put \(\Gamma_1(x)=\alpha_x(I_1(x))\). The procedure first selects final states satisfying both output compatibility \(o_1\in\gamma(a)\) and \(\Gamma_1\models O(q_{s_0}^a)\). It then walks downward, retaining transitions whose arguments are reachable under this same \(\Gamma_1\). A variable leaf is retained only when its abstract label equals \(\Gamma_1(x)\).

With that variable rule, Theorem 3.3 gives

\[
L(A_{e_1})
=\left\{P\in L(G):
o_1\in\gamma\bigl(\llbracket P\rrbracket^\#_{\Gamma_1}\bigr)
\right\}.
\tag{1}
\]

Appendix A separates three ingredients: offline executions and runs, oracle reachability, and the correspondence between retained runs and the given example. Soundness of the abstract transformers then implies that every concrete solution of all examples survives this first slice.

Equation (1) is equality with an **abstract consistency set for one example**. It is not equality with the programs satisfying all \(E\), much less the intended function on unseen inputs. A coarse abstraction can preserve many incorrect concrete candidates.

Algorithm 1 subsequently concretizes the slice on the first input, enumerates candidate accepting runs and checks the examples concretely. A returned program is checked against \(E\). Completeness additionally requires exhaustive search of the finitized candidate set without a timeout. A timeout result is not a proof that no program exists.

For this one-slice argument, \(I_1\)'s abstraction must be covered by the offline input space. Other examples can be checked concretely without themselves belonging to that space, provided the implementation does not require additional slicing on them. No guarantee follows for a new first-example abstraction outside the covered domain.

### 3.1 A local side condition needed in Figure 6

The printed general Transition rule quantifies over \(f(q_1,\ldots,q_r)\to q\) without explicitly excluding variable transitions. If it can be instantiated with \(r=0\) and \(f=x\), its argument-consistency premise is vacuous and bypasses the separate Input rule.

An exact counterexample to that literal interpretation is:

\[
G:S\to x\mid0,\qquad D_x=\{0,1\},\qquad
e_1:(x=1)\mapsto0,
\]

with identity abstraction. The offline state \(q_S^0\) has incoming transitions \(x\to q_S^0\) and \(0\to q_S^0\). The constant transition makes \(O(q_S^0)\) true, so Output selects it. An unrestricted nullary Transition step would also retain \(x\to q_S^0\), accepting \(x\), although \(\llbracket x\rrbracket_{x=1}=1\).

**Local repair:** require that \(f\) is not an input variable in Transition, and dispatch variables exclusively through Input. Non-variable constants remain permitted at arity zero. The Appendix A soundness proof already relies on this exclusivity. This is a missing rule side condition, not a counterexample to the intended oracle construction.

## 4. SQL instantiation and three literal row-count defects

Section 4.2 defines \(\operatorname{NumRows}^{Q}(\ell,u)\) to mean that the concrete result of \(Q\) has between \(\ell\) and \(u\) rows. Bounds can be expressions in input sizes and constants. The following examples evaluate the bounds at concrete inputs. They also apply to symbolic input-size bounds evaluating to those numbers.

The DSL uses standard grouping, duplicate removal, inner joins and left joins. Appendix B claims a complete SQL transformer list. Figures 15, 16 and 18 preserve or combine row bounds as follows:

| Operator and printed rule | Concrete input and result | Failure of the displayed rule |
|---|---|---|
| GroupBy with at least one grouping column preserves \([\ell,u]\) | \(Q=\{(0,3),(0,4)\}\), group by the first column and count the second, producing one row | Input bound \([2,2]\) becomes the false output bound \([2,2]\) |
| Distinct preserves \([\ell,u]\) | The same two distinct source rows, deduplicating according to the first column, produce one row | Again, \([2,2]\) does not contain 1 |
| LeftJoin returns \([\ell_L,u_Lu_R]\) | A one-row left table and a schema-valid empty right table produce one NULL-extended row | The formula returns \([1,0]\) |

These are independent semantic counterexamples to the three formulas as printed. The original two rows in the first two examples are themselves distinct, so assuming the source relation has no fully duplicate rows does not eliminate them. The text does not impose key uniqueness for GroupBy, prior uniqueness for Distinct, or nonemptiness of every right-hand subquery. Nonempty original input tables would not suffice for the last condition, because Filter can produce an empty subquery.

Sound, conservative replacements for these row-count components are

\[
\begin{aligned}
\operatorname{GroupBy}_{\text{nonempty keys}},\operatorname{Distinct}:
&\quad[\mathbf1_{\ell>0},u],\\
\operatorname{LeftJoin}:
&\quad[\ell_L,u_L\max(1,u_R)].
\end{aligned}
\tag{2}
\]

For nonempty-key grouping or duplicate removal, a nonempty input yields at least one output and never more rows than the input. For the left join, each left row contributes \(\max(1,m)\) rows, where \(m\) is its number of matches and \(m\le u_R\). Summing gives (2). A weaker \([0,u]\) also safely handles the first two operators. The zero-key global aggregate is a separate case, already represented separately in the paper.

These local repairs do not certify the complete SQL predicate system. In particular, they say nothing about all column-index, type, NULL or subset rules. A restricted implementation might only encounter weaker reachable bounds that avoid a particular counterexample. Establishing that requires source inspection or a reachability argument absent from this reading.

The lightweight artifact documentation identifies the relevant implementation paths, including offline_construction_transformer.hpp and predicate_row_num_range.hpp, but does not show their formulas. Therefore this note does **not** claim that the implementation has these exact bugs, that all experimental results are invalid, or that the generic theorem under sound-transformer assumptions is false. Applying that theorem to the printed SQL instance requires corrected rules or explicit valid restrictions.

## 5. Experimental evidence and resource boundaries

The following numbers are author-reported measurements, not independently reproduced results. They are included to retain the denominators and compute regime needed to interpret the mechanism.

### 5.1 SQL tasks and comparisons

The evaluation retains 3,817 of 3,866 Cubes benchmarks after excluding 49 whose supplied ground truth did not execute on some inputs. Each task uses the original example and 16 generated examples from its ground-truth query. The stated baseline protocol uses the same examples and a 600-second task timeout. Hardware is a Xeon Gold 6154 with 192 GB RAM. SQL execution uses SQLite 3.46.

Figure 11 reports 2,604 solved by ForesighterSQL, 2,274 by Cubes, 1,951 by PatSQL and 1,781 by BlazeSQL. The 90-fold median and 51-fold geometric-mean speedups over Cubes are restricted to the tasks solved by both. Cubes solves 235 tasks that Foresighter does not, including 87 involving unsupported features.

The systems differ in DSL and guidance. BlazeSQL is the authors' implementation using the same DSL, predicates and transformers, with abstraction refinement. Cubes uses additional search hints such as candidate aggregation functions. The artifact README also describes target-query constants in Foresighter benchmark hints. Thus the main-text comparison does not justify the stronger claim that Foresighter receives no hints of any kind.

The controlled ablations are more direct evidence for the preprocessing mechanism. NoPresyn builds the example-specific FTA online and solves 2,587 tasks. NoOracle keeps the offline FTA but replaces oracle slicing with traversal, solving 2,539. Table 2 gives solved-only median times 9.3 and 34.1 seconds, compared with 0.01 for Foresighter. Paired median speedups are reported separately as 413.1 and 614.4. Ratios of marginal medians are not those paired statistics.

### 5.2 Offline cost and selected online summaries

For SQL at the finest precision, Table 1 reports:

| Quantity | Author measurement |
|---|---:|
| Offline FTA construction | 5 hours |
| FTA serialized size | 51 GB |
| FTA states / transitions | 454.8 thousand / 192.6 million |
| Oracle construction | 7.2 hours |
| Oracle serialized size | 16.8 GB |
| Solved-only online median / mean | 0.01 / 22 seconds |
| Solved-only slice median / mean / maximum | 0.001 / 0.01 / 0.5 seconds |
| Solved-only slice median states / transitions | 37 / 47 |
| Largest concrete FTA state count | 8.6 million |

The two reported construction times total 12.2 hours, or 43,920 seconds, and the two disk artifacts total 67.8 GB. Disk size is not peak RAM, and loading these structures is separate from their construction.

The README recommends at least 140 GB RAM per job for full precision and describes an approximately 20-hour evaluation setup including state maps and precomputed benchmark slices. These are different accounting boundaries from the two construction entries above. Its batch workflow caches task-specific slices before search and documents separate slicing measurements. This is not evidence that slicing is free in a new online request. No timing-code audit was performed.

The input abstraction space supports at most three tables, each with at most 15 columns. Reducing that limit to ten lowers the reported solved count to 2,478 while shrinking the offline structures. Increasing it to twenty solves only a few more tasks and enlarges them. Reuse is therefore conditioned on an engineered coverage range.

### 5.3 Finer abstraction is an empirical trend here

The SQL configurations add NumRows, NumCols, SubsetOf and ColType in a fixed order. Figure 12 uses only tasks solved by the finest configuration. Unsolved configurations receive the 600-second timeout for total time. Each task is normalized to its own zero-predicate baseline, then geometric means are taken. The finest configuration has normalized online total time 0.16.

This supports a measured trend for these nested abstractions, tasks and implementation. It is not a proved universal scaling law. Predicate count does not measure equal precision increments, and the paper's state-splitting measurements explicitly show uneven increments. The offline FTA/oracle costs rise sharply at the last step.

Section 7's approximately 70-minute construction for a benchmark-tailored input space is a measurement under that construction strategy. The accompanying lower-bound language does not establish a lower bound over all incremental synthesis algorithms. The authors themselves leave improved incremental construction open.

## 6. Independent amortization calculation

The reusable object invites an explicit total-cost comparison. Let \(P_k\) be construction cost, \(L_k\) initialization and loading cost, and \(t_{k,i}\) the online cost on fresh covered task \(i\). Against a baseline with analogous costs \(P_B,L_B,t_{B,i}\), configuration \(k\) wins on total serial time exactly when

\[
(P_k-P_B)+(L_k-L_B)
<
\sum_{i=1}^{N}(t_{B,i}-t_{k,i}).
\tag{3}
\]

This identity is an independent accounting observation. It assumes that the costs being added refer to comparable resources and execution modes. Parallel wall time, service capacity and peak memory require separate accounting.

For illustration only, ignore loading differences and substitute the rounded Table 5 means for future per-task means. All 39 matrix tasks are solved by the three compared configurations, so their reported means use the same finite task set:

| Matrix configuration | Reported construction \(P\) | Online mean \(t\) | Plug-in total \(P+39t\) |
|---|---:|---:|---:|
| Blaze | No presynthesis charge in the table | 1.449 s | 56.511 s |
| Foresighter, \(k=2\) | \(66.6+177.7=244.3\) s | 0.101 s | 248.239 s |
| Foresighter, \(k=3\) | \(472.1+424=896.1\) s | 0.086 s | 899.454 s |

Under these substitutions, \(k=2\) becomes cheaper than Blaze at approximately

\[
N>\frac{244.3}{1.449-0.101}\approx181.23,
\]

whereas \(k=3\) becomes cheaper than \(k=2\) only when

\[
N>\frac{896.1-244.3}{0.101-0.086}
\approx43{,}453.33.
\]

Using the rounded table entries as exact inputs gives first integer crossings of 182 and 43,454. These compare independent deployments built from scratch. The latter is not the cost of upgrading after \(k=2\)'s construction cost is already sunk.

For strings, the text explicitly says the finest \(k=3\) and Blaze solve the same 90 tasks. Their reported means are 0.094 and 0.296 seconds. Construction costs \(504+116.6=620.6\) seconds give the analogous threshold

\[
N>\frac{620.6}{0.296-0.094}\approx3072.28,
\]

or 3,073 under exact use of the rounded entries.

These are conditional arithmetic examples, not deployment predictions. The future tasks must be fresh and have comparable online costs and coverage. Repeating an identical benchmark could permit simple answer caching, changing both comparators. The string calculation conditions on solved tasks. The small matrix difference of 0.015 seconds is particularly sensitive to rounding and workload changes. Unknown loading, resident-memory constraints and other initialization costs can shift every threshold. The paper's observation that the finer configuration is faster online remains compatible with all of these calculations.

## 7. What is learned and what remains supplied

The algorithm searches for a concrete program satisfying examples. Its reusable structure is an automaton and input-provenance oracle compiled from known operator semantics, known grammar, known abstractions and a chosen input coverage range.

The strongest mathematical asset is the separation between cross-input sharing and single-environment consistency. It explains exactly what the oracle must preserve, why a naive shared automaton admits spurious runs, and why an oracle-guided slice can retain the same abstract candidate language as an example-specific construction.

This is relevant literature for program-search reuse. It does not by itself establish autonomous creation of operators, learned abstraction refinement, statistical compositional generalization, finite-bit predictive-state learning or the discovery of a reusable program library. No FP transfer theorem or change to FP core research is proposed.

## 8. Verification boundary and reusable conclusions

1. **Author conditional theorem:** exact first-example abstract slicing, with finitized grammar and covered input. The proof was fully read.
2. **Independent local rule correction:** exclude variables from the generic nullary Transition rule. The exact two-production counterexample explains the missing premise.
3. **Independent SQL findings:** three displayed NumRows rules are unsound under their unrestricted stated semantics. Conservative row-count repairs are given. The implementation remains unchecked.
4. **Author experiments:** large online speedups with explicit offline compute, disk, input-domain and solved-task conditioning. No independent reproduction.
5. **Independent accounting:** total-cost crossings depend on task volume, workload and initialization. The reported matrix data can favor a coarser abstraction over a much larger range of deployment sizes than online latency alone suggests.

The historical synthesis references are recorded as dependencies and related work in the paper, not newly fully read here. Follow-up implementation work would require retrieving the artifact and checking the actual transformer and timing code. It is not required to retain the present bounded theoretical findings.
