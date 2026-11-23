# Comparing Experiments in Discounted Problems

## Source, edition and actual coverage

- **Authors:** Ludovic Renou, Xavier Venel, Mark Whitmeyer and Cole Williams.
- **Edition read:** four-author manuscript, latest version **November 11, 2026**, first version June 9, 2023, **87 pages**. [Exact author PDF](https://whitmeyerhome.wordpress.com/wp-content/uploads/2026/11/dynamic-blackwell-draft-revision-v8.pdf) · [Whitmeyer’s research page](https://sites.google.com/site/markwhitmeyer/).
- **Version distinction:** the author page reports that Whitmeyer–Williams’s earlier separable-problem paper was merged into this work. Neither [2405.16458v3](https://arxiv.org/abs/2405.16458v3), the two-author April 2025 Renou–Venel edition, nor [2405.13709v1](https://arxiv.org/abs/2405.13709v1) is the edition read here. The filename `revision-v8` is not an arXiv version number. No reviewed publication of this merged edition was established.
- **Local original:** `literature/corpus/pisf_prior_art/RENOU-VENEL-WHITMEYER-WILLIAMS-2026-11-11/paper.pdf`. Complete Poppler and PyMuPDF extractions accompany it. No explicit public TeX link was located; older TeX was not substituted.
- **Coverage, 2026-11-23 Shanghai:** main assistant personally read all physical/printed pp. 1–87: §§1–4; every statement, formula and proof in Appendix A.1–A.10; all 29 references; Appendix B.1–B.5; and complete Appendix C. This includes the title acknowledgments, all 36 numbered footnotes, Figure 1 and all tabular probability/payoff/call-function displays. Original PDF checks covered pp. 10, 20, 27–28, 31, 47, 54–55, 64–65, 74, 82, 84–86. Agents handled metadata/retrieval/mechanical extraction only.
- **Verification:** exact rational recomputation of Appendix C’s separating payoffs, all ten displayed call-function differences and its mixing cancellation. Main proofs were read, but not independently certified in full or formally replayed. No empirical learning experiment or implementation benchmark is reported.

## Research question and the distinctions that matter

How should two streams of information be ranked when a decision-maker cares about both accuracy and arrival time, and when choices can influence later information? The paper varies the admissible class of decision problems. Changing that class changes which simulation condition is necessary.

Its strongest general controlled characterizations, Theorems 6–7, have the order **for every test kernel, there exists a matching garbling**. Their consistency condition makes the same garbling both generate the comparison distribution and determine actual future controls. It does not reverse the quantifiers into one garbling for all test kernels. Nor does the word “unique” in the discussion assert uniqueness of a mathematical solution: it means one witness must serve both roles in that fixed comparison (§3.2, pp. 26–28).

Three separate issues must therefore be retained: whether a comparison preserves only discounted action frequencies or each date’s action distribution; whether successive simulated histories must extend one another; and whether one simulator must work for every control policy. The paper is unusually useful for keeping these issues apart.

## 1. Uncontrolled experiments and the static reduction

Except for a possibly infinite time horizon, the primitive sets are finite. A fixed hidden state is \(\theta\in\Theta\). An uncontrolled experiment consists of kernels

\[
f_t:X^{t-1}\times\Theta\to\Delta(X_t),\qquad
f^t(x^t\mid\theta)=\prod_{s\le t}f_s(x_s\mid x^{s-1},\theta),
\]

and similarly for \(g\). Actions do not influence signals. In the basic problem, the same finite action set \(A\) and payoff \(u(a,\theta)\) apply at every date. A discount vector is a probability distribution \(\delta\) on dates, and payoff is \(\sum_t\delta_tu(a_t,\theta)\). Strategies may remember signals and their own past actions. **Realized payoffs are not additional observations.** If observed rewards convey information, that channel must be included in a controlled experiment (§2.1, pp. 5–7).

Dominance means that for every decision problem and every strategy under \(g\), some strategy under \(f\) yields at least as much payoff **in every state**. The static benchmark is Blackwell’s equivalence among this comparison, replication of action distributions, a state-independent garbling, and convex ordering of posterior distributions (Theorem 0, pp. 7–8).

### Fixed discount vector: Theorem 1

For the basic discounted problems, these conditions are equivalent:

1. Dominance for the fixed \(\delta\).
2. Replication of **discounted action distributions**, \(\sum_t\delta_t\operatorname{marg}_{A_t}P_{\theta,g,\tau}=\sum_t\delta_t\operatorname{marg}_{A_t}P_{\theta,f,\sigma}\), simultaneously in all states.
3. Blackwell sufficiency of the **tagged mixtures** \(\sum_t\delta_tf^t\) for \(\sum_t\delta_tg^t\).
4. Convex-order dominance of the corresponding discounted posterior distributions for every prior.

More explicitly, kernels \(\gamma_s:X^s\to\Delta(\bigsqcup_tY^t)\) satisfy

\[
\delta_tg^t(y^t\mid\theta)
=\sum_{s,x^s}\delta_sf^s(x^s\mid\theta)\gamma_s(y^t\mid x^s).
\]

The date tag is part of the mixture observation. A report produced at actual date \(s\) can represent a history of a different length \(t\). This is a comparison of aggregate discounted opportunities, **not a procedure reconstructing the target stream by its original deadlines**. The deployed decision rule still uses only information available at its actual date; the reduction permits compensation between dates because instantaneous payoff is the same function and actions do not constrain later choices (§2.3, pp. 8–11).

The proof uses convexity of attainable distributions, Kuhn’s behavioral/mixed-strategy equivalence, and separating hyperplanes. For infinite horizons, finite report alphabets are enlarged, diagonal subsequences are taken, and discount tails control the limit. Fatou initially gives subprobability kernels; total output mass rules out missing mass on relevant histories (A.1, pp. 40–44). These limiting steps are substantive, not an assumption that a countably infinite simplex is compact in the needed sense.

### Evolving states: Theorem 2

For a fixed joint law of state paths and payoff depending on the **current** state, the replicated object is the discounted distribution of \((a_t,\theta_t)\). The mixture identity uses \(P_{p,f}(x^s,\theta_s=\theta)\), and posterior comparison concerns the current state. Actions still affect neither state evolution nor signals. This extension does not by itself establish a theorem for action-dependent state transitions (§2.3.2, pp. 13–14; A.1).

### Discount families and arrival-time applications

The set of discount vectors for which dominance holds is convex (Proposition 2). Combining two witnesses requires date-dependent weights proportional to the two discount masses, rather than an unweighted mixture of kernels. Closure is obtained from posterior convex-order inequalities under the \(\ell^1\) topology. The infinite-dimensional extreme-point discussion invokes the Radon–Nikodym property of \(\ell^1\); the finite-horizon cases are ordinary polytopes (§2.4).

- **All discount vectors:** dominance is equivalent to \(f^t\) Blackwell-dominating \(g^t\) separately for every \(t\), and to dominance in all additively separable problems (Theorem 3).
- **All decreasing discount vectors:** it suffices and is necessary to compare every uniform-prefix mixture, since uniform distributions on initial date segments are the extreme points (Corollary 2).
- These datewise garblings can redraw the entire reported history at each date. They are not required to be mutually compatible prefixes.

For one fixed informative static signal arriving at random times with CDFs \(F,G\), dominance reduces to \(\sum_t\delta_tF_t\ge\sum_t\delta_tG_t\). For all discounts, this is earlier arrival in first-order stochastic order; for decreasing discounts, the criterion is the corresponding second-order order. Under geometric discounting it can be expressed using transforms \(E[\rho^{T_F}]\ge E[\rho^{T_G}]\). This is a comparison of the cumulative value remaining after arrival, rather than only the instantaneous signal value (Proposition 1, Corollaries 3–4).

If the arriving signals differ, a static information-value ratio \(r^*\) enters: \(r^*E[C(T_F)]\ge E[C(T_G)]\), with \(C(t)=\sum_{s\ge t}\delta_s\). The full characterization of \(r^*\) is assigned to a companion note, not proved here. Appendix B.1 states the finite-horizon feasibility condition for replacing a multiplicative reduction by delay: \(\lambda E[C(T)]\ge\delta_T\). This prevents pretending that any loss in precision can be represented by an allowed finite delay.

## 2. When history consistency becomes necessary

In arbitrary sequential problems, payoff can depend on the whole action sequence and feasible action sequences may be constrained. The paper invokes Greenshtein (1996): dominance in this larger class is equivalent to an **adapted garbling** that incrementally extends the simulated history,

\[
g^t(y^t\mid\theta)
=\sum_{x^t} f^t(x^t\mid\theta)
\prod_{s\le t}\eta_s(y_s\mid x^s,y^{s-1}).
\]

The same sequence of state-independent kernels works at every prefix. Unlike separate Blackwell witnesses for \(f^t,g^t\), it must preserve the reports already produced. The cited result is an external dependency; reading its use here does not mark the 1996 paper fully read (§2.5, pp. 19–22).

**Theorem 4:** even one fixed full-support discount vector recovers this stronger ordering when all history-dependent feasible action sets are allowed. The proof encodes each partial action sequence as the next action, forces successive prefixes to agree, and after a finite horizon repeats the terminal report. Dividing the terminal reward by the positive remaining discount weight reproduces the original sequential payoff. For an infinite horizon, nested closed sets of adapted kernels have a common point in a product of finite simplexes (A.4).

**Theorem 5 and Proposition 7:** allowing all history-dependent discount factors also recovers adapted sufficiency, but for an experiment of finite duration \(T\), problems of duration **\(T+1\)** are used. A large bonus after a coherent action history rewards incremental reporting; an incoherent choice removes later bonuses. The extra date prevents a last-period decision-maker from replacing previously chosen components using information learned later. The proof compares original and encoded strategies in both directions, with a common additive \(TM\) payoff shift (A.5).

These are exact expressive-equivalence constructions. Their expanded action alphabet contains partial histories, and their reward scales can depend on the instance. They do not bound the size, description length or update cost of a learned memory.

## 3. Controlled information and the actual quantifiers

### Primitive experiment versus decision problem

A controlled experiment has fixed control alphabets \(K_t\) and kernels

\[
f_t:X^{t-1}\times K^{t-1}\times\Theta\to\Delta(X_t).
\]

The decision problem specifies \((A,u,\kappa)\), where
\(\kappa_t:A\times K^{t-1}\to\Delta(K_t)\).
Thus the action/control map can vary without changing the experiment’s primitive domain. At date \(t\), the agent has observed \((x^t,k^{t-1})\), chooses an action, and a control is generated for subsequent information (§3.1, pp. 23–24).

Three assumptions are explicit: realized controls are observed; the control map is state-independent; and earlier actions influence the current control only through previously realized controls, in addition to the current action. Making controls state-dependent would introduce an extra informative channel. These assumptions are part of the theorem, not merely notation.

### Theorem 6: fixed-discount controlled comparison

Given a target strategy, the conditional distribution of its current action given its signal/control history is state-independent: the experiment likelihood factors cancel from the numerator and denominator. Zero-probability histories are completed consistently across states. This cancellation is needed to construct valid test kernels (A.6, pp. 49–50).

A test kernel \(\xi_t\) accepts a fictitious signal/control history, possibly of another length, together with the actual control history. A garbling \(\gamma_t\) maps the actual signal/control history to a fictitious report. The target process uses \(\xi\); the source process uses **\(\xi\circ\gamma\)**, so the simulation changes the information the source will receive next.

The key characterization is

\[
\forall\xi\quad\exists\gamma:\qquad
\delta_tP_{\theta,g,\xi}(y^t,l^{t-1})
=\sum_{s,x^s,k^{s-1}}\delta_s
P_{\theta,f,\xi\circ\gamma}(x^s,k^{s-1})
\gamma_s(y^t,l^{t-1}\mid x^s,k^{s-1}).
\]

This is equivalent to dominance in all fixed-\(\delta\) controlled problems and to replicating their discounted action distributions (pp. 27–28). **The \(\gamma\) in the source dynamics must be the same as the \(\gamma\) in the matching equation.** Treating the two as unrelated witnesses would omit the endogenous effect of simulation on future information.

Nevertheless, the witness may depend on \(\xi\), and reports can have different lengths from the actual date (footnote 18). The statement is not \(\exists\gamma\,\forall\xi\), is not a joint path-law assertion, and is not a general approximate-deficiency bound. Footnote 20 describes a fixed-point formulation with an LP for the outer matching problem when the dynamics-generating garbling is fixed. It does not provide a complexity guarantee for checking all test kernels or finding a fixed point.

For infinite discount support the section assumes **full support**. The proof separately extracts limits of report kernels and induced control kernels, obtains subprobabilities by Fatou, then uses positive weight at every date and total mass to identify the two limiting compositions. Omitting full support would remove a stated step in this proof (A.6, pp. 53–55).

### Theorem 7: separable controlled comparison

For time-dependent action sets and payoffs with summable sup norms, the replicated object is each date’s action marginal. Its characterization is again \(\forall\xi\,\exists\gamma\), now with

\[
\gamma_t:X^t\times K^{t-1}\to\Delta(Y^t\times K^{t-1}),
\]

and matching at the **same date**, without discount mixing. The fictitious history is still a full report redrawn from the actual history; the theorem does not impose that it extends the previous fictitious report. The proof uses finite-prefix separation and compactness, followed by the same state-independent conditional-action and induced-control identities (A.8, pp. 61–64).

Unlike the uncontrolled case, dominance for every discount vector with one common flow-payoff function is **strictly weaker** than dominance for all time-dependent separable payoffs. Appendix C establishes this distinction constructively, rather than assuming that a result for all discounts can absorb arbitrary date-specific payoffs.

## 4. Applications, special sufficient conditions and time consistency

### Stationary controlled experiments

Here \(f_t(x_t\mid x^{t-1},k^{t-1},\theta)=h_f(x_t\mid k_{t-1},\theta)\), with an analogous \(g\) and fixed initial control. Proposition 3 gives a sufficient fixed-discount criterion in terms of worst static regret ratios

\[
R_k^*=\sup_u
\frac{V_{p,h^*}^*(u)-V_{p,h_f(k)}^*(u)}
{V_{p,h^*}^*(u)-V_{p,h_g(k)}^*(u)}.
\]

With the stated zero-denominator conventions, it requires
\(R_{k_0}^*\le\sum_t\delta_t\max\{1,R_k^*\}^{1-t}\) for every \(k\). The construction uses static garblings into a mixture of target signals and fully revealing state reports, a subdominance kernel for later signals, and date-dependent weights that gradually replace continued simulation with repetition of an earlier action. When the initial mixture includes full revelation with positive weight, the hypothesis really requires source signals that identify the state with positive probability; the proof does not grant the simulator access to the hidden state (A.7, pp. 55–61).

**Proposition 4:** pointwise Blackwell dominance \(h_f(\cdot\mid k,\cdot)\succeq h_g(\cdot\mid k,\cdot)\) for every control is sufficient for separable dominance. The proof chooses static kernels \(\lambda_k\), keeps fictitious and real controls equal, and conditions the product of signal-garbling and control probabilities (A.9).

**Restricted construction, not a general characterization:** the per-control \(\lambda_k\) can be applied to successive source signals while retaining the simulated past and using the resulting target actions. Because the source and target have the stated stationary conditional kernels, this gives a policy-independent causal simulation in this sufficient special case. The whole-history conditional \(\gamma_t\) displayed in A.9 includes \(\xi\), because it integrates over past random reports after observing actual controls. Neither this special construction nor its conditional representation establishes a necessary policy-independent simulation theorem for arbitrary history-dependent controlled experiments.

Pointwise dominance is not necessary for a fixed initial control: an initially fully revealing source can make later deficiencies irrelevant. Requiring the comparison uniformly over initial controls makes first-period static comparisons necessary (§3.3.1).

### Bandits

An arm is a state-contingent vector of mean rewards, used as a control. The reward distribution has that mean, and its realized reward is observed at the next date. Pointwise Blackwell dominance for each arm suffices. Conversely, if one arm’s experiment fails static dominance, a finite menu and a two-period problem can expose the failure. The proof creates continuation arms from a supporting affine function of a separating convex payoff, then gives enough first-period weight to force acquisition of the distinguished arm (Proposition 5, A.10). Necessity concerns some constructed menu containing that arm, not every existing menu.

The scalar payoff-noise family additionally requires injectivity of the nonzero reward map before comparing revelation probabilities. Equal mean rewards with different noise laws need extra arm labels in the basic representation (§3.3.1, pp. 32–34).

### Commitment versus consistent planning

In the basic uncontrolled problem optimal choices are myopic, so commitment and consistent planning agree. With controls, different temporal selves can disagree about information acquisition. The three-date example has prior probability \(3/4\), a late informative signal of accuracy \(q>3/4\), and a middle self caring only about the final payoff. That self acquires information at the expense of the current reward, giving the initial self \(q/2<3/4\), whereas an uninformative experiment allows \(3/4\). Commitment can ignore the extra information and does not suffer this loss (§3.4).

Proposition 6 rules out a global reversal of the two orderings **when all profiles of discount factors are quantified over**: one may choose time-consistent continuation preferences matching the first self. The paper conjectures an extension for a fixed profile; it does not prove it. A fixed-control necessary condition for reversal is discussed separately.

## 5. Remaining appendices and independent checks

Appendix B.2 fixes the payoff problem instead of varying it. Comparison for all discounts becomes datewise value comparison; for decreasing discounts it becomes prefix-sum comparison. If priors also vary, the equivalent conditions are inclusions of attainable payoff sets after downward closure, or of their Minkowski averages. These are weaker task-specific criteria than Blackwell comparison for all payoffs.

Appendix B.3 and Figure 1 show that dominance need not vary monotonically with patience. For the supplied example, with \(\alpha=0,\beta=1,\varepsilon=0,\chi\in(1/3,1/2)\), source-minus-target information weight is zero at \((1,0,0)\), negative at \((4,2,1)/7\), and positive at \((1,1,1)/3\). A sufficiently small positive \(\alpha\) makes the first inequality strict while preserving the other two signs.

Appendix B.4 derives finite-horizon extreme points for two patience classes. A discount distribution stochastically later than a fixed one has extreme points obtained by pushing each date’s mass to the next retained date. With decreasing discounts imposed as well, the extreme points average the original weights on consecutive blocks. The proofs examine active cumulative-sum constraints and concavity; the resulting comparison tests remain mixture-experiment tests.

Appendix B.5’s “sequential comparison” is a different notion from arbitrary sequential-payoff dominance. It asks whether the decision-maker should ever **permanently switch information sources after an observed history**, under a specified joint coupling of the two sources. Equal marginal experiments can give an incentive to switch when their signals are conditionally independent and no incentive when perfectly correlated. Theorem 8 compares normalized continuation mixtures at every feasible source history. Fixing the coupling is essential; it is not a robustness theorem over all couplings or arbitrary repeated switching.

### Appendix C: exact separation checked

Proposition 9 supplies binary states, two dates, binary signals and a binary control. For every discount \((d,1-d)\), \(f\) dominates \(g\) in all problems with a common flow payoff. A date-dependent separable problem nevertheless favors \(g\).

The first source signal has accuracy \(3/4\); the target’s first signal is uninformative. The original second-signal tables are in (C.2), p. 82. With control \(k_1=1-a_1\), the separating rewards are

| Action | \(u_1(a,0)\) | \(u_1(a,1)\) | \(u_2(a,0)\) | \(u_2(a,1)\) |
|---|---:|---:|---:|---:|
| 0 | \(-9/32\) | \(3/32\) | 0 | 0 |
| 1 | 0 | 0 | \(-4\) | 9 |

Under the uniform prior, the best source value is \(184/64=23/8\). The target rule \(a_1=y_1\), with \(a_2=1\) exactly when \(y_1=1\) or \(y_2=0\), yields \(185/64\). I independently enumerated the 64 relevant deterministic source rules with exact rational arithmetic and recomputed the target witness: the gap is exactly **\(1/64\)**. Convexity makes randomized rules no better than the best deterministic rule for this fixed expected-payoff problem.

For dominance at every common discount, the proof constructs two source strategies satisfying

\[
L_2=G_2,\qquad E_1=G_1,\qquad E_2-G_2=-\tfrac14(L_1-G_1).
\]

Their mixing weights \(\omega_L=(1-d)/(1+3d)\), \(\omega_E=4d/(1+3d)\) cancel the discounted discrepancy. Existence of their second-date kernels follows from binary posterior call-function inequalities. I independently recomputed **all ten** entries of the p. 85 difference table symbolically from (C.1)–(C.2), and checked the intermediate target matrix’s row sums and the mixing cancellation. These checks support the concrete separating example and its numerical algebra. They are not an independent proof of every general theorem in the manuscript.

Two minor scope/notation cautions encountered while reading: A.9 sometimes calls its Theorem 7 condition “\(\Delta\)-sufficiency” although the main text names it S-sufficiency; its displayed equations establish the stronger same-date condition. Also B.1’s unrestricted infinite-horizon delay sentence needs an endpoint convention at \(\lambda=0\): with strictly positive remaining discount and almost-sure finite arrival, \(E[C(\widehat T)]\) cannot equal zero. Allowing never-arrival resolves that endpoint. Neither observation invalidates the main finite-horizon comparisons. Footnote 11’s description of a first-order later discount distribution as “more impatient” is reversed relative to B.3–B.4’s explicit convention.

## 6. Citation dependencies, limitations and next reading

Core dependencies are Blackwell’s static comparison, Kuhn’s theorem and separation/compactness arguments; Greenshtein’s adapted comparison supplies the uncontrolled arbitrary-sequential equivalence. Arrival-time ordering refers to Shaked–Shanthikumar, and the patience discussion cites Yang–Zentefis. Related results on Gaussian information acquisition, stopping, and repeated i.i.d. experiments are discussed but are not established here. The information-ratio companion note has not been retrieved.

**The missing controlled sequential result is explicit:** footnote 30, p. 37, says that a generalization of Greenshtein to controlled sequential problems is available upon request. Its statement and proof are **not present** in this 87-page manuscript; Appendix C instead proves the discounted-versus-separable separation. No author was contacted. The omission is a source-availability boundary, not evidence that the claimed result is false.

For Astra’s current controlled terminal-payoff question, the read source establishes relevant exact distinctions and a stationary sufficient construction. It does **not** supply a general quantitative finite-horizon deficiency characterization by one causal simulator valid for all policies. It does not charge carried state, serialized tables, simulator construction, update execution or acquisition samples. Translating its full-history strategy spaces into a bounded learned recurrence requires additional assumptions and a separate argument; no FP architecture or learning rule is derived here.

Next selected recent source: Whitmeyer–Williams, *Strong Dominance for Dynamic Signals*, arXiv:2407.16648v2, revised May 17, 2026; author reports acceptance at Economic Theory Bulletin. Its abstract concerns robustness to additional dynamic information sources. Whether that robustness addresses controlled-policy quantifiers remains an unread question at this checkpoint. Recent adapted-transport duality sources are screened technical leads only, not automatic full-reading obligations. No historical full-reading backlog is introduced.
