# Strong Dominance for Dynamic Signals

## Edition, status and coverage

- **Authors:** Mark Whitmeyer and Cole Williams.
- **Edition read:** [arXiv:2407.16648v2](https://arxiv.org/abs/2407.16648v2), submitted May 17, 2026 at 22:25:15 UTC, originally submitted July 23, 2024. The 19-page PDF’s title page displays **May 19, 2026** while its arXiv stamp and official metadata identify the May 17 v2 submission. Preserve both dates rather than silently replacing one.
- **Review status:** [Williams’s author research page](https://colerandallwilliams.com/932-2/) reports acceptance at *Economic Theory Bulletin*. The manuscript thanks the editor and three anonymous reviewers. A final publisher edition was not checked; the reading is of the exact arXiv v2, not a presumed journal typesetting.
- [Versioned PDF](https://arxiv.org/pdf/2407.16648v2) · [Complete source](https://arxiv.org/src/2407.16648v2). Local directory: `literature/corpus/pisf_prior_art/2407.16648v2/`.
- **Fully read, 2026-11-24 Shanghai:** complete 46,385-character, 621-line `source/ds.tex`; all printed pp. 1–19, including Introduction and related work, §2 and §§2.1–2.4, all proofs, Figure 1, payoff table, seven numbered footnotes and title acknowledgment, declarations and all 17 printed references. The source bibliography contains 133 records, mostly unused; that is not the paper’s reference count. There is no appendix. Original PDF checks covered the signal/figure representation and numerical example, with extracted PDF checks for theorem numbering and the interim definitions. Main assistant read the body; source assistants only retrieved files and metadata.
- **Independent checks:** exact rational dynamic-programming calculation of the stopping example and its cost thresholds. Two literal notation/convention qualifications below were identified from the source. No complete independent theorem certification or formal replay.

## 1. Question and primitive objects

The paper asks when one dynamic information source remains more valuable than another **whatever additional dynamic information source the decision-maker also possesses**. This is stronger than comparing two experiments as the decision-maker’s only information. Its main contribution is a compact characterization inherited from a richer representation of signals, rather than a new estimator or state-learning algorithm (§1, pp. 1–4).

The hidden state \(\theta\) lies in a finite set with a fixed full-support prior \(\mu\). A dynamic experiment is a conditional law over a possibly infinite sequence of finite signal alphabets. In contrast, a **signal** is a finite measurable partition of the common space \(\Theta\times[0,1]\), with the unit interval supplying auxiliary randomization. The measure is induced by the prior and Lebesgue measure within each state.

A dynamic signal \(\eta=(\eta_t)\) is a sequence of partitions with \(\eta_{t+1}\) refining \(\eta_t\). Thus \(\eta_t\) represents cumulative information available by date \(t\). The join \(\eta_t\vee\rho_t\) represents observing both the source and an auxiliary signal. Using a common underlying space specifies their correlations; separate experiment matrices alone do not specify these joint observations (Definition 2.1, p. 5).

An extended decision problem \(\mathcal D=(u,A,\rho)\) has compact period-specific action sets, a continuous payoff \(u(a_1,a_2,\ldots,\theta)\), and an auxiliary dynamic signal \(\rho\). Strategies are adapted to current and past observations. Actions do **not** control the signal process. The value is

\[
W(\eta;\mathcal D)
=\max_{a\text{ adapted to }\eta\vee\rho}
E[u(a,\theta)].
\]

For an infinite horizon, products have the product topology and sums over infinite signal paths mean integrals. The compactness/continuity argument in footnote 1 supplies attainment. Deterministic adapted strategies suffice for this single-agent expected-payoff optimization. A finite approximation or an arbitrary discontinuous infinite-horizon payoff is not silently covered.

**Strong dominance** quantifies over all such payoff problems and auxiliary signals. The source partitions themselves remain fixed in the same underlying space. This is not a comparison of every possible coupling of two otherwise unspecified marginal experiments, nor an intervention model in which actions change which signal kernel is encountered.

## 2. Main theorem: reveal the state or determine the other signal

Definition 2.4 says that a signal \(\alpha\) **reveal-or-refines** \(\widehat\alpha\) when each cell \(s\) of \(\alpha\) either:

1. has positive probability in at most one state, so observing it reveals the state; or
2. is contained in a cell of \(\widehat\alpha\), so observing it determines which cell of the other signal actually occurred.

Dynamic reveal-or-refinement requires this condition **at every date**, for cumulative partitions. Subject to the usual null-set interpretation discussed below, **Theorem 2.5** states

\[
\eta\text{ strongly dominates }\widehat\eta
\quad\Longleftrightarrow\quad
\eta_t\text{ reveal-or-refines }\widehat\eta_t
\quad\text{for every }t.
\]

### Proof structure and what it uses

For sufficiency, follow a realized chain of source cells up to the first date at which the state becomes known. Before that date, each source cell determines the target cell. Joining any auxiliary signal preserves this containment, so a source-adapted strategy can imitate the target’s decisions without seeing the future. Once the state is revealed, choose a best continuation given the already chosen past actions; additional signal realizations are unnecessary for attaining the maximum possible continuation payoff. If no finite date reveals the state, imitation continues at every finite date (§2, pp. 7–8; the construction is expanded again in §2.4).

For necessity, if reveal-or-refinement fails at a particular date, choose a payoff that depends only on the action at that date. The static robust comparison theorem of Brooks–Frankel–Kamenica then gives a decision problem and auxiliary signal that reverse the comparison. The key static necessity theorem is **imported**, not re-proved here.

The proof supplies **payoff dominance**, not exact reconstruction of the other source’s realized noise on state-revealing branches. On those branches it switches to a payoff-dependent optimal continuation. Consequently, this theorem should not be cited as a single task-independent simulator that reproduces arbitrary joint information trajectories, much less a simulator valid for all action-controlled environments.

### Additively separable and ordinary comparisons

Corollary 2.8 gives the same characterization when payoffs are additively separable. The failing-date necessity test already lies in this restricted class, while sufficiency follows from Theorem 2.5. Thus robust dominance has the same ordering in the separable and general sequential classes.

Without auxiliary information, dynamic reveal-or-refinement is still sufficient for ordinary sequential dominance (Corollary 2.10), but is not necessary. The paper explicitly distinguishes a Blackwell garbling that replicates a **conditional signal law** from containment that identifies the **actual realized signal cell**. The latter depends on the shared representation and its correlations (§2.2, pp. 9–10).

This does not contradict the broader discounted-comparison distinctions in the [four-author November 2026 manuscript](RENOU-ETAL-2026-DISCOUNTED.md). The comparison classes differ: arbitrary auxiliary signals strengthen the quantifiers here, whereas arbitrary controlled information kernels are not part of this model.

## 3. More information sooner can lose in an ordinary stopping problem

The paper adapts a two-date example from Greenshtein. There are two conditionally independent binary experiments. Experiment \(\alpha\) has accuracy \(3/4\); \(\beta\) has accuracy \(2/3\), so \(\alpha\) strictly Blackwell-dominates \(\beta\). The prior probability of the right state is \(4/5\).

At date one the decision-maker chooses left, right or defer. A decision made immediately ends the economically relevant choice; deferring pays cost \(c\) and permits a decision after the second experiment. Payoffs are:

| State | Immediate left | Immediate right | Defer, then left | Defer, then right |
|---|---:|---:|---:|---:|
| Left | 1 | 0 | \(1-c\) | \(-c\) |
| Right | \(9/10\) | 1 | \(9/10-c\) | \(1-c\) |

The right action is optimal iff the posterior probability of the right state is at least \(10/11\). After both experiments, the possible posteriors are \(2/5,8/11,6/7,24/25\); only two right signals cross the threshold. For \(0<c<4/195\), either order induces the same rule: stop and choose left after a first left signal; defer after a first right signal; finally choose right only after two right signals.

Gross expected payoff is the same, \(283/300\). However, the probability of deferring is \(13/20\) when \(\alpha\) comes first and \(3/5\) when \(\beta\) comes first. Therefore

\[
V_{\beta\to\alpha}-V_{\alpha\to\beta}
=c(13/20-3/5)=c/20>0.
\]

The less informative first experiment is preferred in this particular stopping problem because it causes fewer costly deferrals. This does not say that the reversed order is universally more informative.

**Independent rational check:** recomputed posterior probabilities and both date-one continuation values directly from the two conditionally independent likelihood matrices. Following a first right signal, the value of waiting before cost is \(4/195\) under \(\alpha\)-first and \(7/180\) under \(\beta\)-first; following a first left signal it is zero in both cases. With \(c=1/100\), optimized values are \(5621/6000\) and \(703/750\), respectively, giving exactly \(1/2000=c/20\). The printed thresholds and gross value agree (§2.3, pp. 10–13).

Corollary 2.11 says that, for cumulative signals \((\alpha,\alpha\vee\beta)\) and \((\beta,\alpha\vee\beta)\), the first strongly dominates the second exactly when \(\alpha\) strongly dominates \(\beta\). The stopping example does not satisfy this stronger premise: conditional independence and nondegeneracy leave both \(\beta\) realizations possible after every \(\alpha\) cell, and no \(\alpha\) cell reveals the state. The actual-cell containment required by reveal-or-refinement therefore fails.

## 4. The precise meaning of the interim proposition

For a positive-probability event \(s^t\cap z^t\) determined by the source and auxiliary partitions, §2.4 defines both conditional values on that **same event**:

\[
W(\eta\mid s^t,z^t)
=\max_{a\text{ adapted to }\eta\vee\rho}
E[u(a,\theta)\mid s^t\cap z^t],
\]

and analogously for the target’s policy class. Proposition 2.12 equates all these conditional comparisons with ex ante strong dominance.

The reverse direction averages at **date one**, where conditional optimizers can be joined into one adapted policy by selecting the appropriate first-observation branch. The forward direction again imitates before state revelation, then chooses an optimal continuation. These are the proof’s substantive steps (pp. 14–16).

**Important interpretation:** these maxima range over whole adapted policies. The definition does not fix a previously executed action history, and the conditioning event need not be observable under the target signal. Footnote 6 explicitly notes that if the event pins down a state, a state-specific constant action sequence attains the full-information conditional optimum in **both** policy classes. Each conditional optimization may choose a different constant policy. This is a comparison of policy classes under a conditional measure; it must not be substituted for a switching or continuation theorem with irrevocable past decisions. The stronger information available when evaluating the conditional maximum is not a new observation granted to the deployed target agent.

## 5. Literal notation and null-set qualifications

Two small representation issues should be kept separate from the intended economic result.

**Example 2.2:** the displayed partition notation lists the pieces in the two state fibers separately, while the repeated labels and Figure 1 group pieces of the same color into a single signal cell. To reproduce the stated experiment, the two blue \(h\) pieces must form one cell, and similarly for \(l\), \(hH\) and \(lL\). Reading the listed state-fiber pieces as separate observed cells would reveal the state immediately and would contradict the accompanying experiment. The graphic and likelihoods determine the intended union convention (pp. 5–6).

**Null sets:** Definition 2.4 prints literal set inclusion, but value comparisons depend only on probabilities. A modulo-null convention is needed for its literal “if and only if.” For example, let \(\beta\) split both state fibers into lower and upper half-intervals. Let \(\alpha\) be the same partition except that one point from the upper half of one state is moved into the lower cell. The two signals and every join with an auxiliary signal agree almost surely, so their values coincide in every problem. Both cells remain non-state-revealing, yet the modified lower cell is literally contained in neither \(\beta\) cell. The discrepancy disappears when containment/refinement is interpreted almost surely, or representatives are chosen consistently. This is an independently identified convention requirement, not a positive-measure counterexample to the intended robust-comparison theorem.

## 6. Evidence, dependencies and follow-up scope

This is a theoretical paper. It does not infer unknown partitions, learn an information structure from samples, estimate the number of response classes, solve matrix completion, or quantify sample complexity, simulator size, carried memory or update computation. Its primitive signal partitions and correlations are supplied. No benchmark result on an AI model is reported.

The main imported result is Brooks–Frankel–Kamenica’s static robust reveal-or-refine theorem. The paper cites its 2022 mimeo; the later four-author discounted manuscript cites the 2024 AER publication. Gentzkow–Kamenica supplies the common signal-space representation. Greenshtein and de Oliveira supply ordinary dynamic comparison background. The printed bibliography also retains the earlier separate 2024 Renou–Venel and Whitmeyer–Williams drafts; these are not the November 2026 merged edition. None of these dependencies is marked fully read merely because its use here was understood.

For the previously active controlled-simulator question, the source provides a clear boundary: robustness to auxiliary **exogenous** information, payoff-specific optimization after state revelation, and conditional policy-class comparisons are distinct from one universal causal simulator under interventions. No such general controlled theorem is extracted here.

Astra’s new 28e5a3d registration instead asks how ordinary delayed target prediction can discover unknown response partitions and which missing response cells are identifiable. This paper offers no learning or identification theorem for that task. The next selection therefore returns to recent primary work on that concrete object; historical background is retained for narrow necessary lookups only.
