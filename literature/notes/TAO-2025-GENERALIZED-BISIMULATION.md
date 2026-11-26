# Generalized bisimulation: finite-MDP comparison and simultaneous sampling guarantees

## Source, edition and actual reading

- **Paper:** Zhenyu Tao, Wei Xu and Xiaohu You, *A Generalized Bisimulation Metric of State Similarity between Markov Decision Processes: From Theoretical Propositions to Applications*. [Official NeurIPS 2025 proceedings](https://proceedings.neurips.cc/paper_files/paper/2025/hash/458567910b6d21f438f22aa20c036723-Abstract-Conference.html), Advances in Neural Information Processing Systems 38, DOI [10.52202/085713-1625](https://doi.org/10.52202/085713-1625).
- **Completed edition:** [official 28-page PDF](https://proceedings.neurips.cc/paper_files/paper/2025/file/458567910b6d21f438f22aa20c036723-Paper-Conference.pdf). Pro-C read the complete official text on November 26, 2026, Shanghai: §§1–7, Appendices A–F, every statement, proof and formula, all 26 references and the complete seven-page checklist. All 13 figures and their 40 panels were inspected. Original pp. 3, 5–10 and 20–28 were visually inspected, 16 pages. The PDF has no numbered tables, algorithm boxes or body footnotes. Unreliably encoded glyph lines in extracted plot text were resolved by viewing the original figures.
- **Separate author edition:** [arXiv:2509.18714v3](https://arxiv.org/abs/2509.18714v3), November 3, 2025, 01:42:58 UTC, 23 pages. The current history lists v1–v3. Its source package has one active neurips_2025.tex and 26 compiled bibliography entries. It omits the checklist, expands Appendices D–E, changes the on-policy notation, and adds a lax bound curve to ten policy-transfer panels. Source inventory and selected version comparisons were performed. It is not treated as the official text or counted as a second full reading.
- **Later related manuscript, scoped only:** the same authors' [arXiv:2512.17265v1](https://arxiv.org/abs/2512.17265v1), *A Theoretical Analysis of State Similarity Between Markov Decision Processes*, December 19, 2025, 06:29:51 UTC, 17 pages. Its metadata says submitted to an IEEE Transactions and carries an arXiv overlap notice. This is another identifier, not v4 of the conference preprint. Read metadata, abstract, selected scope information and [§IV-B2, Theorem 9, Eqs. (21)–(23)](https://arxiv.org/html/2512.17265v1#S4.SS2.SSS2). The sample-confidence passage still omits simultaneous-event accounting. The rest of the expanded manuscript, algorithms and additional experiments were not fully read or evaluated.
- **Verification boundary:** bounded independent coupling, contraction, aggregation-interface and confidence checks. The two-state sampling family and policy-aggregation example below were checked analytically. Assisting readers independently checked selected interfaces and source differences. No exhaustive theorem audit, formal proof, proof script, implementation reproduction or empirical rerun. Checklist item 16 says that LLMs were not an important, original or nonstandard part of the core methods. This does not exclude writing assistance, which that item does not require authors to disclose.
- **Source cache:** literature/corpus/pro_c/tao2025gbsm/. No FP core files were changed.

**Main finding:** the finite-state, common-action, discounted construction has a sound coupling-based core. It gives useful deterministic value, transfer and aggregation error bounds. The printed Eq. (21) does not provide its claimed simultaneous confidence over all transition rows. An explicit two-state, 8,192-action example satisfies the stated sample threshold but violates the claimed probability. A direct transport perturbation argument preserves the paper's reward constant, and a union bound repairs the confidence calculation. The on-policy aggregation extension additionally needs an explicit policy-lifting convention. These issues are separate from the valid deterministic metric construction.

## 1. Objects and access assumptions

The basic objects are finite MDPs

\[
M_i=(S_i,A,P_i,R_i,\gamma)
\]

with a **common finite action set and action labels**, a common discount, and finite real rewards. The results require \(0\leq\gamma<1\), although §2 only calls \(\gamma\) a discount factor rather than separately stating this interval. No irreducibility, positive-transition or stationary-distribution assumption is used. The states are already given and observable. This is not a POMDP state-discovery or belief-learning result.

For a nonnegative cost matrix \(c:S_1\times S_2\to\mathbb R\), define

\[
W_c(P,Q)=\min_{\lambda\in\Pi(P,Q)}\sum_{x,y}\lambda(x,y)c(x,y).
\]

The finite transportation polytope is nonempty and compact. The cost need not already be a metric for this LP or its two-potential dual to make sense. Definition 3.1 specifies the fixed point

\[
d^{12}(s,t)=\max_{a\in A}
\left\{|R_1(s,a)-R_2(t,a)|
+\gamma W_{d^{12}}(P_1(\cdot\mid s,a),P_2(\cdot\mid t,a))\right\}.
\]

The state carries its MDP identity. The same label in two different models need not have distance zero. Different labels or models can have distance zero when their compared behaviors agree. The resulting structure is a pseudometric on the appropriately tagged states, rather than a model-identification certificate.

The paper's constant is

\[
\bar R=\max_{s\in S_1,t\in S_2,a\in A}|R_1(s,a)-R_2(t,a)|.
\]

This compares all cross-model state pairs at the same action. It is not merely the maximum discrepancy at identically named states, and it is not necessarily the pooled reward span across different actions.

## 2. Fixed point and the useful deterministic properties

Theorem 3.2 and Appendix A construct the fixed point by monotone iteration from zero on the bounded lattice \([0,\bar R/(1-\gamma)]^{S_1\times S_2}\). Finite coordinate sets justify the required limit exchanges. They obtain

\[
0\leq d^{12}-d_n^{12}
\leq\frac{\gamma^n\bar R}{1-\gamma}.
\]

A short independent check also gives uniqueness. Since every feasible coupling has mass one,

\[
|W_c(P,Q)-W_e(P,Q)|\leq\|c-e\|_\infty,
\qquad
\|F(c)-F(e)\|_\infty\leq\gamma\|c-e\|_\infty.
\]

This is an additional elementary contraction argument, not the paper's stated lattice-proof route.

Theorem 3.3 bounds \(|V_1^*(s)-V_2^*(t)|\) by \(d^{12}(s,t)\). Its finite-horizon induction uses the optimal values as feasible dual potentials for the transport LP. The argument retains the same discount and aligned action labels. It does not give the same conclusion for arbitrary policies with different action-selection rules unless those policies are incorporated into the compared models.

Theorem 3.4 follows by transposing a coupling. Theorem 3.5 first glues two optimal transport plans through their common middle marginal and then uses synchronous iteration to prove

\[
d^{12}(s,t)\leq d^{13}(s,u)+d^{32}(u,t).
\]

The proof does not assume the final triangle inequality to prove itself. It proves preservation of a triangle relation between three cost matrices and applies that result at each finite iteration. Zero-mass middle states cause no problem in the finite gluing construction.

### The diagonal comparison is a global bound

When the state labels are shared, Theorem 3.6 gives

\[
\max_s d^{12}(s,s)
\leq\frac1{1-\gamma}
\max_{s,a}\left\{|R_1(s,a)-R_2(s,a)|
+\frac{\gamma\bar R}{1-\gamma}\operatorname{TV}(P_1(\cdot\mid s,a),P_2(\cdot\mid s,a))\right\}.
\]

The coupling keeps common probability mass at identical labels and moves only the residual TV mass. The common mass can still incur a cross-model diagonal cost, which the proof correctly retains before solving the inequality.

The maximum on the right cannot be replaced by the current state's own local discrepancy. For example, use one action, states \(0,1\), transitions \(0\to1\) and \(1\to1\), and equal zero rewards at state 0. Let model 1 have reward zero at state 1 and model 2 have reward one there. The local reward and transition discrepancy at state 0 is zero, but \(d^{12}(0,0)=\gamma/(1-\gamma)>0\). Future model differences matter. Some shorthand in §5 must be read with this global qualification.

### Relation to the disjoint-union construction

An independent structural observation clarifies the claimed computational comparison. Form the tagged disjoint union of the two MDPs, keeping each component closed under its transitions. A transport problem comparing a state from component 1 with one from component 2 only sees the cross-component cost block. Its iteration therefore coincides with the displayed GBSM iteration, and uniqueness identifies their fixed-point cross blocks.

Thus direct cross-model computation avoids maintaining unnecessary blocks. It does not produce a different cross distance solely by avoiding the union notation. The sharper analytical comparisons should be assessed by their actual inequalities. This observation is not an independent historical novelty audit of the cited literature.

## 3. Policy transfer and aggregation

For a supplied map \(f:S_2\to S_1\), the transferred stationary randomized policy is \(\pi_2(a\mid t)=\pi_1(a\mid f(t))\). Theorem 4.1 and Appendix C retain both a model-mismatch term and source-policy suboptimality:

\[
\|V_2^*-V_2^{\pi_2}\|_\infty
\leq\frac{2}{1-\gamma}\max_t d^{12}(f(t),t)
+\frac{1+\gamma}{1-\gamma}\|V_1^*-V_1^{\pi_1}\|_\infty.
\]

The proof inserts source optimal and policy values, bounds the optimal-value difference by the metric, and absorbs the target gap from the remaining Bellman term. No injectivity or exact-homomorphism property of \(f\) is required. Choosing a nearest source state in the metric minimizes the displayed distance term. It is not proved to minimize the target's actual regret. The source gap may be deleted only for an optimal source policy.

For aggregation, choose representatives \(U\subseteq S\) and a map \(r(s)=[s]\) with \(r(u)=u\). The model used in §4.2.1 copies the reward and transition row of the representative, then pushes the next-state mass to representatives:

\[
R_{\mathrm{agg}}(s,a)=R(r(s),a),
\qquad
P_{\mathrm{agg}}(u\mid s,a)=\sum_{x:r(x)=u}P(x\mid r(s),a).
\]

The notation \(V_{[1]}(s)\) and \(d^{1-[1]}(s,s)\) uses this model lifted to original state labels. A model stored only on \(U\) requires the corresponding explicit lift. Define

\[
\widetilde\sigma_i=\max_s d^{ii}(s,r_i(s)),
\qquad \sigma_i=\max_s d^{i-[i]}(s,s).
\]

Theorems 4.4–4.5 yield

\[
\|V_i^*-V_{[i]}^*\|_\infty\leq\sigma_i
\leq\frac{\widetilde\sigma_i}{1-\gamma},
\]

\[
\|d^{12}-d^{[1][2]}\|_\infty
\leq\sigma_1+\sigma_2
\leq\frac{\widetilde\sigma_1+\widetilde\sigma_2}{1-\gamma}.
\]

The proof inserts a model with representative reward/transition rows before pushing their next states. The intermediate model and the pushed model have zero appropriate cross distance. A triangle inequality then gives the bound. In p. 7's first transport sum, the printed weight \(P(\tilde s\mid[\tilde s],a)\) should be \(P(\tilde s\mid[s],a)\), the actual source row. Correcting that local index preserves the zero-cost proof. It is not a counterexample to the aggregation result.

The bounds improve the cited coefficients, but weak inequalities do not imply strict improvement in every instance. Zero approximation error, for example, can give equality. The representative map is supplied. The paper does not prove an algorithm that discovers an optimal aggregation from raw observations or finite interaction data.

## 4. Deterministic estimation error versus simultaneous confidence

The sampling model in §4.2.2 keeps rewards exact and replaces each transition row by empirical frequencies from \(K\) independent next-state samples. It assumes access to every state–action row. A generative sampler can supply this access. One trajectory or an arbitrary offline dataset need not do so.

The deterministic Eq. (20) follows from the triangle inequality:

\[
\|d^{12}-d^{\widehat1\widehat2}\|_\infty
\leq\max_s d^{1\widehat1}(s,s)
+\max_t d^{2\widehat2}(t,t).
\]

That result is separate from the probability that the empirical kernels meet a required accuracy. Eq. (21) states a per-row threshold with only \(\log(2/\alpha)\), while claiming a maximum-error guarantee with probability \(1-\alpha\). Its proof applies a single-coordinate Hoeffding bound without accounting for all rows, successor coordinates and both MDPs.

### Explicit counterexample to the printed confidence claim

For each model \(j=1,2\), use two states \(L_j,H_j\). Every one of \(m\) common actions has rewards

\[
R_j(L_j,a)=0,\qquad R_j(H_j,a)=1,
\]

and transitions

\[
P_j(H_j\mid H_j,a)=1,
\qquad P_j(L_j\mid L_j,a)=P_j(H_j\mid L_j,a)=\tfrac12.
\]

The two models are behaviorally identical, so \(d^{12}(L_1,L_2)=0\) and \(\bar R=1\). Independently sample all rows, which is allowed by the stated assumptions. For an action \(a\), consider the event that one model's low-state row has all \(K\) samples high and the other's has all samples low, in either direction. Its probability is

\[
q=2^{1-2K}.
\]

In the first direction, the empirical fixed-point equations imply

\[
\widehat d(H_1,L_2)\geq1+\gamma\widehat d(H_1,L_2),
\qquad
\widehat d(L_1,L_2)\geq\gamma\widehat d(H_1,L_2).
\]

Hence the estimation error at the low-state pair is at least \(\gamma/(1-\gamma)\). The reverse event gives the same conclusion. Independent action rows give a failure probability of at least \(1-(1-q)^m\).

Choose

\[
\gamma=\epsilon=\tfrac1{10},\qquad
\alpha=\tfrac14,\qquad K=7,\qquad m=8192.
\]

The printed Eq. (21) only requires

\[
K\geq\frac{2\log8}{0.9^4}<7,
\]

so the specified \(K\) satisfies it. But \(q=1/8192\), and the error exceeds \(\epsilon\) with probability at least

\[
1-(1-1/8192)^{8192}>1-e^{-1}>\alpha.
\]

This refutes the literal global confidence statement. It leaves the deterministic Eq. (20), the metric properties and the individual Hoeffding inequality intact. No numerical experiment is needed for this finite construction.

### Retaining the original reward constant

There is also a proof-interface issue in applying Theorem 3.6 separately to \(M_i,\widehat M_i\): its reward constant would naturally become that model's within-action reward span. The original cross-model \(\bar R\) need not dominate each such span. The constant in the final perturbation bound can nevertheless be preserved by a direct argument, so it should not be labeled false.

For any cost \(0\leq c\leq B\), maximal couplings of the marginals, composed with a transport plan, give

\[
|W_c(P,Q)-W_c(P',Q')|
\leq B\{\operatorname{TV}(P,P')+\operatorname{TV}(Q,Q')\}.
\]

The probability that at least one marginal changes is at most the sum of the TV terms, and the cost changes by at most \(B\). Reversing the construction yields the absolute-value bound. This does not require \(c\) to be a pseudometric.

Let \(\eta_i=\max_{s,a}\operatorname{TV}(P_i(\cdot\mid s,a),\widehat P_i(\cdot\mid s,a))\). Combining that inequality with the contraction and \(d^{12}\leq\bar R/(1-\gamma)\) yields

\[
\|\widehat d-d\|_\infty
\leq\gamma\|\widehat d-d\|_\infty
+\frac{\gamma\bar R}{1-\gamma}(\eta_1+\eta_2),
\]

and therefore

\[
\boxed{\|\widehat d-d\|_\infty
\leq\frac{\gamma\bar R}{(1-\gamma)^2}(\eta_1+\eta_2).}
\]

This independently supports the deterministic constant used by the sampling derivation.

### A conservative simultaneous repair

Write \(n_i=|S_i|\), \(m=|A|\), and \(N=m(n_1^2+n_2^2)\). There are \(N\) scalar transition-probability coordinates across both models. Using

\[
\delta_i=\frac{\epsilon(1-\gamma)^2}{\gamma\bar R n_i},
\]

Hoeffding and a union bound give failure probability at most

\[
2m\sum_{i=1}^2 n_i^2\exp(-2K_i\delta_i^2).
\]

A sufficient per-row sample count is thus

\[
\boxed{
K_i\geq
\frac{\gamma^2\bar R^2n_i^2}{2\epsilon^2(1-\gamma)^4}
\log\frac{2m(n_1^2+n_2^2)}{\alpha},\qquad i=1,2.
}
\]

Take integer ceilings. The total number of next-state samples is \(m(n_1K_1+n_2K_2)\). Independence across rows is unnecessary for this union bound, although within-row independent samples are used for Hoeffding. The formula is a sufficient bound, not a proved necessary or minimax sample complexity. It can be conservative because multinomial coordinates are dependent. For \(\gamma=0\) or \(\bar R=0\), exact rewards make the relevant transition-induced distance error zero, and the division-based expression need not be used.

The same distinction applies after aggregation. A transition-estimation tolerance does not remove the separate aggregation error. Any combined target must allocate an error budget to both terms. The later [2512.17265v1, Theorem 9](https://arxiv.org/html/2512.17265v1#S4.SS2.SSS2) retains the single-coordinate logarithm and proof ending. That targeted passage is not a correction of the simultaneous-event gap. Its broader reformulation was not audited here.

## 5. Lax action matching and on-policy aggregation

The lax extension in §5 compares sets of state–action pairs through a Hausdorff construction, using reward difference and transported next-state cost. This permits different action sets. An action map for transfer is additional data. Appendix D explicitly requires the chosen \(g(a)\) to attain the required minimum for **every** paired state and source action. A single state-independent \(g:A_1\to A_2\) need not satisfy all those conditions. The transfer bound is conditional on that assumption, not a guarantee for arbitrary action relabeling. A state-dependent action map would be a different explicitly specified interface.

For on-policy distances, Eq. (23) first forms the Markov reward process

\[
R_i^\pi(s)=\sum_a\pi(a\mid s)R_i(s,a),
\qquad
P_i^\pi(\cdot\mid s)=\sum_a\pi(a\mid s)P_i(\cdot\mid s,a).
\]

The fixed-point and value-comparison arguments then apply to these supplied processes. They concern \(V_i^\pi\), not optimal values. Theorem E.1 is the corresponding value bound.

Theorem E.2 transfers the aggregation bound to this setting without explicitly saying whether the policy is aggregated before or after the environment. These operations do not commute for an arbitrary state-dependent policy.

### Two-state example under the literal original-label policy interface

Use states \(0,1\), two actions \(a,b\), and self-loop transitions for both actions in the original model. Set

\[
R(0,a)=R(1,b)=0,
\qquad R(0,b)=R(1,a)=1.
\]

Let \(\pi\) choose \(a\) at 0 and \(b\) at 1. The original induced reward is zero, so both policy values and all on-policy state distances are zero. Aggregate both states to representative 0 using §4.2.1's environmental row replacement and next-state pushforward. Then

\[
R_{\mathrm{agg}}(s,a)=0,
\quad R_{\mathrm{agg}}(s,b)=1,
\quad P_{\mathrm{agg}}(0\mid s,\cdot)=1.
\]

If the original policy is retained at the original labels, the aggregate value at 1 is one, and the aggregate value at 0 remains zero. Theorem E.2's rightmost quantity \(\max_s\widetilde d_\pi(s,[s])/(1-\gamma)\) is zero, whereas the value error and maximal cross-model policy distance are one.

This demonstrates a missing policy-interface condition under a reading not excluded by the text. It does not rule out a consistent intended interpretation. The result applies if one first fixes \(\pi\) and aggregates its induced Markov reward process, or equivalently uses \(\pi_{\mathrm{agg}}(a\mid s)=\pi(a\mid[s])\) on the aggregate side. Requiring the original policy to be constant on each fiber is another sufficient convention. The value-difference bound of E.1 remains valid in the example. Only the final aggregation comparison is affected.

## 6. What the numerical evidence tests

The official §6 and Appendix F report random Garnet MDPs with 20 states, five actions and a 50% branching factor. Half of the states use representative reward/transition rows in the aggregate models. Estimated models are constructed by adding Gaussian noise with standard deviation 0.1–0.3 to transition probabilities. The paper does not describe negative-entry handling or renormalization, so the actual implementation cannot be reconstructed from this statement. This omission alone does not prove invalid transition matrices were used.

There are 100 independent trials at each \(\gamma\in\{0.1,0.2,\ldots,0.9\}\). The horizontal axis is trial index, not sample count or learning progress. Four families of comparisons are shown:

| Quantity | Proposed bound | Comparator |
|---|---|---|
| Transferred-policy regret | Theorem 4.1 | Song et al. 2016's empirical MDP measure and the authors' reported ground truth |
| State-similarity aggregation error | Theorem 4.5 | Ferns et al. 2011's aggregation coefficient |
| State-similarity estimation error | Deterministic Theorem 4.6 bound | Ferns et al.'s transport-based error bound |
| Optimal value approximation error | Theorem 4.4 | Zhang et al. 2021's aggregation coefficient |

The plots support the reported comparison of deterministic bounds on these generated instances. They do not test the repaired or original \((K,\epsilon,\alpha)\) confidence claim. The Gaussian perturbation procedure is not empirical multinomial frequency estimation, and no \(K\), coverage experiment or confidence curve is given. An empirical measure's failure to upper-bound regret does not refute a coverage theorem that was never claimed for that measure.

The text calls the value calculations precise in a tabular Q-learning setting but gives no learning rate, exploration, training horizon, convergence tolerance or source-policy selection protocol. It should be recorded as the authors' reported ground truth, not an independently established exact dynamic-programming solution.

The complete official figures retain the same qualitative ordering across the discount grid. Policy-transfer bounds become loose at high discounts. GBSM aggregation and value bounds are visibly below their compared BSM bounds. The two estimation bounds can be quite close at small discounts. Figures 9–10 have aggregation in their captions but estimation on their axes. There are no aggregate confidence intervals or mean-plus-standard-deviation summaries. The repeated trials are not evidence of a specified 100-seed training protocol.

Checklist pp. 14–16 answers NA for reproducibility, open code, experimental settings, statistical significance and compute resources, describing the work as simple numerical computation. No reward-generation distribution, seed, solver, hardware, runtime or detailed representative-selection rule is supplied. No author code link was found in the checked official page, PDFs or v3 source. These are reproduction limits, not claims that no code exists anywhere.

The conference figures contain no lax-transfer curve. The v3 preprint adds one to Figure 1a and all nine Appendix F policy-transfer panels without an accompanying budget or action-mapping protocol in §6. The editions' plots therefore cannot be merged into one experimental record.

## 7. Computational and research scope

The paper compares \((n_1+n_2)^2\) union-state pairs with \(n_1n_2\) cross-model pairs. This is a count of maintained distance entries. A literal update also requires \(mn_1n_2\) transportation problems per iteration. Each dense LP may have \(n_1n_2\) coupling variables and \(n_1+n_2\) marginal constraints. Sparse support can help, but no complete runtime analysis or implementation is supplied.

The contraction bound separately determines the number of iterations for a chosen tolerance. Transition storage, LP work space, numeric precision and solver error remain additional costs. In the reported 20-state, five-action case, a direct full update has 400 distance entries and 2,000 transport subproblems per iteration. This is derived from the formulas, not an observed runtime measurement. It is not a finite-bit memory guarantee for a learned agent.

The main useful tool is a quantitative comparison between supplied finite controlled models. Reward differences and all aligned actions are built into that comparison. It does not establish how a predictor discovers hidden states, learns a sufficient recurrent update, selects a memory budget or transfers among tasks with an unknown observation/action correspondence. The \(\gamma\uparrow1\) singularity is explicitly acknowledged by the authors. Average-reward and undiscounted conclusions are not supplied.

No FP theorem, learned representation or experiment is inferred from the formal similarity. A substantive FP application would need a verified finite-state interface, action and reward alignment, a model-learning/access argument, and separate prices for the installed representation and update computation.

## 8. Cross-session status

The official NeurIPS edition is fully read and this note completes the ordinary Pro-C research unit. The v3 source and later 2512.17265v1 remain scoped. The global sampling claim is refuted by the explicit finite family, with a separate sufficient repair. The deterministic metric and transfer/aggregation conclusions retain their stated conditions and the on-policy interface qualification. No full formal certification is claimed.

Pro-E retains request 59b8251, claimed at 40c0d2a. Astra's research through 52c2310 was preserved, with no core edits. The next ordinary selection requires a fresh request, owner and duplicate check.
