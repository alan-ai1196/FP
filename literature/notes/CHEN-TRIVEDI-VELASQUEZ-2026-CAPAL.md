# Chen–Trivedi–Velasquez 2026 — CAPAL, scoped proof and code reading

## Source and incomplete-reading boundary

Lekai Chen, Ashutosh Trivedi and Alvaro Velasquez, *Towards Persistent Noise-Tolerant Active Learning of Regular Languages with Class Query*. Official ICLR 2026 proceedings, 24-page conference PDF.

[Official record](https://proceedings.iclr.cc/paper_files/paper/2026/hash/df01766dc88e5f1d475df4f7f3097d73-Abstract-Conference.html) · [Official PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/df01766dc88e5f1d475df4f7f3097d73-Paper-Conference.pdf) · [Author code at 57d877f6](https://github.com/lkwargs/CAPAL/tree/57d877f6a083d58852660fac388ff49c052dc2d2)

Read November 25, 2026, Shanghai. **Status remains partially read.** The main assistant covered all available extracted text on pp. 1–24, §§1–6, Appendix A.1–A.6, all four theorem statements and their arguments, Lemma 1, two algorithms, two tables, three footnotes, all 32 references and all figure captions. The actual 18 figures did not reach the reader. Screenshot calls returned text placeholders and local execution was unavailable. Several figures contain full prompts, graph structure and numerical curves absent from the extracted text.

The precise remaining visual pages are p.3 Fig1, p.5 Fig2, p.8 Fig3, p.10 Fig4, p.14 Figs5–6, p.19 Fig7, p.20 Fig8, p.21 Figs9–10, p.22 Figs11–13, p.23 Figs14–17 and p.24 Fig18. Resume by inspecting these figures and the original formula layouts on pp.6–7 and15–18. Do not repeat the already covered prose or mark this paper fully read before resolving that boundary.

A narrow static comparison covered README and the following parts of capal.py at the pinned June18,2026 commit: PersistentNoisyMQ, PerfectEQ, SameStateOracle initialization and label cache, probe construction and same_state, the learner's noise initialization, counterexample handling and fit. This is not a full code audit or an execution replay. No later paper revision was authenticated.

## Original question, access and method

The authors want to infer a regular language and its DFA from an imperfect membership oracle, motivated by language models answering questions about natural-language specifications. A separate equivalence oracle receives a proposed DFA and either certifies the entire language or returns a genuine disagreeing word. That oracle is exact in the main model.

Three notions must remain distinct.

- Definition3.1 allows independent stochastic answers to repeated identical complete prompts. The prompt includes context and auxiliary information, not only the queried word.
- Definition3.2 calls a prompt persistently erroneous when its modal answer is wrong. Thus its probability of answering correctly is below1/2. Majority resampling concentrates on the wrong answer under that condition.
- Section4 caches the first answer to each word and uses that fixed value thereafter. Its statistical calculations invoke an error level eta below1/2, while later complexity prose calls eta an average error rate. The homogeneous independent cached-flip model is stronger than a general query-dependent biased language-model oracle.

The learner keeps a prefix set S, required distinguishing suffixes E_core, a supplementary suffix pool and a discrimination tree. A class query compares two prefixes using the proportion of suffixes for which cached labels disagree. The threshold is

\[
p_0+\tau,\qquad p_0=2\widehat\eta(1-\widehat\eta),\qquad
\tau=\min\{\tau_{\max},\sqrt{\log(2/\alpha)/(2m)}\}.
\]

Only DIFFERENT results are cached, with suffix-set version and threshold in the key. Early stopping is safe for a fixed planned suffix set when the already accumulated disagreement count divided by its final size exceeds the threshold. Closedness and consistency repairs enlarge the table. The discrimination tree supplies separating suffixes. Exact counterexamples overwrite membership labels for those words and may trigger structural or acceptance repairs.

The code-based oracle is a distinct experimental mode. One language-model call synthesizes a deterministic Boolean program, after which membership calls execute that program. Determinism removes repeated-call variance but does not establish that the generated program matches the intended language. Exact equivalence checking remains the external correctness mechanism.

## Claimed results and actual proof obligations

**Theorem2, AppendixA.3.1, is unconditional soundness relative to the perfect verifier:** if the algorithm halts after an exact OK answer, its output language is correct. This statement follows directly from the assumed oracle and does not itself prove termination or an efficient learning procedure.

**Theorems1,3 and4 claim high-probability convergence and query bounds.** With n target states, alphabet Sigma, access diameter rho, counterexample-length bound L_CE and a suffix budget m, the displayed bounds are

\[
\#EQ=O(n),\qquad
\#MQ=O(|\Sigma|n^2\rho+nL_{\rm CE})
      +O(m|\Sigma|n\rho).
\]

The proof imports classical exact-table, counterexample-decomposition and discrimination-tree results. The new steps concern statistical class decisions, cached negatives and trusted-label repairs.

AppendixA.3.2 assumes a safe noise upper bound and per-comparison false-DIFFERENT probability at most alpha. It uses a union bound over comparisons. Footnote2 explicitly offers a summable alpha_t schedule when their number is not known. This schedule still changes the required per-call sample budget. A fixed per-call confidence is not automatically a fixed overall confidence for arbitrarily many comparisons.

Lemma1 asserts that every counterexample permanently decreases a potential consisting of unseparated pairs of target states plus incorrectly accepting hypothesis states. Theorem3 invokes that finite potential. AppendixA.4 then uses shortest access representatives and a uniform class-discrimination gap to obtain the claimed complexity. Its count of O(n rho) prefixes is conditional on keeping shortest access strings. The implemented insertion of every counterexample prefix is not by itself such a pruning rule.

These are author claims and proof dependencies. The local checks below identify obstacles to importing the claims unchanged. They do not amount to a full impossibility proof for every intended or revised implementation.

## Bounded independent checks

### The literal structural test is a DFA identity

Algorithm1 line18, the main text on p.7 and AppendixA.3.3 all extract the proposed split condition as

\[
\delta^H(H[u],a)\ne H[ua].
\]

The paper defines H[w] as the state obtained by running H from its start on w. Under that definition,

\[
H[ua]=\delta^H(H[u],a)
\]

for every u and a. Thus the literal condition never fires. One must compare a hypothesis successor with a separately represented table class or use an actual counterexample-decomposition test. The printed expression alone cannot justify the structural-progress branch.

The current author code does make a different comparison. In _process_counterexample it computes a successor in the hypothesis, separately obtains the table class of u+a, maps that class into a hypothesis state, and compares those two objects. It also inserts all counterexample prefixes before processing, and promotes one suffix on the first label-only occurrence. The paper's pseudocode instead defers label-only suffix additions until repetition. These distinctions are recorded rather than conflating the code with the displayed algorithm.

This is a defect in the literal stated test, not a proof that the code's different test always fails or that no corrected learner can converge.

### A noise bound does not give a suffix-separation bound

Under independent same-rate cached flips on distinct queried words, let Delta be the probability that a suffix distinguishes the two true residual languages. Direct conditioning gives

\[
\mathbb E[D]
=2\eta(1-\eta)+(1-2\eta)^2\Delta.
\]

Thus the gap above the correct baseline is (1−2eta)^2 Delta. Keeping eta away from1/2 does not bound Delta away from zero.

For example, compare the residual language containing exactly a^ell with the empty residual, over a binary alphabet, and draw a suffix uniformly from words of length ell. Even with no noise, Delta=2^{-ell}. With m independently sampled suffixes, the chance of seeing no witness is (1−2^{-ell})^m. A suffix pool excluding that word gives zero gap. These residuals occur in an ordinary finite DFA for the singleton language.

An exact counterexample or deliberately chosen distinguishing suffix can change this situation. That is additional information about the suffix-selection mechanism. It does not follow from the noise level alone. The paper's assertion that fixed noise and confidence make m independent of target size needs such a separation premise.

The formula itself also requires stronger noise assumptions than an average correctness rate for arbitrary query-dependent prompts. Distinct suffix votes can share cached words, can be selected using previous labels, and can include reused core columns. Independence and the relevant conditional expectations must be justified for the claimed concentration argument. Repeating the same cached word does not create a fresh independent label.

### The active tolerance cap can invalidate the asserted alpha bound

There is a simple local counterexample even with independent homogeneous errors and an exactly known safe noise level. Take a truly equal pair, one suffix, eta=0.1, alpha=0.05 and tau_max=0.1. Then p_0=0.18, the capped threshold is0.28, and the disagreement indicator equals1 with probability0.18. The test therefore falsely declares DIFFERENT with probability0.18, exceeding0.05.

This refutes the stated generic per-comparison alpha implication for the capped threshold. It is not a simulation of the complete CAPAL loop or a counterexample to every larger budget. Retaining the uncapped Hoeffding radius, or establishing that a chosen budget makes the cap inactive, repairs this particular concentration step under its independence assumptions.

Similarly, upper-capping an underestimate does not make it an upper confidence bound. The proof can legitimately assume a supplied safe value bar_eta, but the algorithm needs to justify that value. Even a valid safe upper bound can reduce the distinguishing margin and therefore has a cost beyond false-split control.

### A trusted word label is not automatically a permanent state label

A perfect counterexample gives a correct label for that exact word. If the current hypothesis merges two target residuals with different acceptance, two different trusted words reaching the same hypothesis state can require opposite labels. Overriding that state's acceptance to fit one word may invalidate the other.

Consequently, the claim that every label-only correction permanently reduces the potential requires a separate invariant or a structural split when trusted labels conflict. Section4 does mention conflict-triggered refinement, which is relevant, but the short proof of Lemma1 does not establish the required permanent decrease merely from correctness of the counterexample label. This is a stated proof obligation, not a claimed full counterexample to the intended conflict-handling mechanism.

## Static code comparison and limits

The pinned code's simulated PersistentNoisyMQ draws one independent flip per new word and caches it. PerfectEQ explicitly accesses the true target DFA and searches the product with the hypothesis for a shortest disagreeing word. Hence its benchmark verification access is substantially stronger than passive noisy traces.

The implementation includes the same capped square-root tolerance in same_state. It also handles two gold labels with opposite values as decisive, which is sound for those exact words. A second shortcut treats one gold label and one disagreeing noisy label as decisive. For two truly equal residuals, that second observation can occur with probability eta. It is not, by itself, an alpha-certified difference for alpha<eta.

The inspected initialization obtains a noise parameter from the oracle or configuration, with a numerical lower floor and upper clamp. This is not an independently verified data-only bootstrap confidence bound. It should not be described as acquiring an unknown safe noise bound from ordinary unlabeled interactions on the strength of the inspected code.

There is no execution replay, no verification of all call paths and no claim that the June18 implementation exactly generated the published tables. The public tree has28 target .taf files. The paper's §5 describes200 human-interpretable DFAs. The mapping from the stated experimental cohort to the public files was not established by this bounded check.

## Experiments actually read

The text studies prompt variants and active learners on described regular languages. Unless stated otherwise the main experimental oracle is GPT-4o at temperature0.9. Figure2 instead specifies GPT-4o-mini, temperature0.9 and30 samples per query. These experiments using OpenAI models do not make this an official OpenAI paper.

The two tables were read in full. Selected entries illustrate both reported improvement and its limits.

| Oracle | LA mean model calls | CAPAL mean model calls | MQ error | LA exact recovery | CAPAL exact recovery |
|---|---:|---:|---:|---:|---:|
| Direct prompt | 46.07 | 43.75 | 0.156 | 0.107 | 0.250 |
| Reasoning prompt | 52.64 | 30.93 | 0.068 | 0.500 | 0.571 |
| Verification plus reasoning | 51.57 | 28.96 | 0.044 | 0.714 | 0.679 |
| Discriminator plus reasoning | 51.82 | 29.14 | 0.047 | 0.714 | 0.821 |
| Synthesized code | 1 | 1 | 0.013 | 0.786 | 0.928 |

Table1 also reports standard deviations. Model-call counts exclude the cost of later deterministic checker executions in the one-call synthesis mode. They are not a matched total-computation comparison. Contrary to §5.2's blanket wording, CAPAL is below LA on the verification-plus-reasoning row.

The injected-noise experiment describes eta up to0.2 and counterexamples up to length10. AppendixA.2 considers independently missed counterexamples with probability p. Four independent retries make the chance of accepting one incorrect fixed hypothesis p^4. That per-call calculation does not establish a uniform guarantee for a correlated or adversarial practical verifier. The corresponding curves and all learning diagrams remain visually unread.

The appendix also explains direct prompts, reasoning, a second model acting as verifier, discrimination-tree-guided examples, and synthesized code. Complete prompt examples are embedded in figures and remain part of the outstanding reading boundary.

## Relevance boundary and next reading

This source gives a concrete example of active transition discovery with exact external counterexamples, persistent cached labels and carefully selected suffix probes. It does not authenticate learning a common finite-state update from ordinary noisy observations alone. Its perfect equivalence oracle can rule out disagreements at arbitrary unseen lengths. Such access must be supplied when citing its exact-language conclusion.

No new FP theorem, architecture recommendation or experimental change is proposed. The completed dd1e654 response remains separate. The current note preserves the source's claims, the actual textual coverage, the independent local checks and the code distinction while image access is blocked.

The next recovery task for this paper is the listed figures and original mathematical layouts. Its complete-reading count remains zero. Ordinary reading may proceed to an accessible original OpenAI text while this concrete visual blocker persists.
