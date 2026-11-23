# Beyond Blackwell: Constrained Data Processing Inequalities

## Source and reading status

Brendan van Rooyen, Epigraph Solutions. **arXiv:2611.00510v1**, October 31, 2026. [Versioned primary record](https://arxiv.org/abs/2611.00510v1) · [PDF](https://arxiv.org/pdf/2611.00510v1) · [TeX](https://arxiv.org/src/2611.00510v1). DOI 10.48550/arXiv.2611.00510. The primary history checked November 23 lists only v1; no reviewed venue or author correction was established in this check.

**Fully read, November 23, 2026:** all 18 pages, §§1–5, complete statements and proofs, all three commutative diagrams, examples, conclusion and 13 printed references. There are no appendices, figure/table environments or footnotes. The entire 50,345-character `main.tex` was read; the 13 printed references were read separately from the much larger shared bibliography database. Original PDF pp. 4, 6, 7, 10–13, 15–17 were visually checked. The main assistant did all body reading; source assistance was limited to metadata, abstracts and retrieval.

Local source: `literature/corpus/pisf_prior_art/2611.00510v1/`. The note distinguishes author results from independent objections. **The data-processing argument is usable with appropriate existence conventions, but the quantitative theorem needs explicit regularity/normalization, and the asserted reduction to minimal transformations is not valid under the stated general assumptions.** No formal proof replay or complete independent certification is claimed.

## 1. Original question and basic objects

The paper compares statistical experiments when a decision maker may use only admissible decision rules. It keeps the decision problems broad while restricting rules; this differs from restricting the test losses used to compare otherwise unrestricted experiments.

For finite sets, a Markov transition is a column-stochastic matrix. An experiment $e:\Theta\to Z$ specifies the observation distribution for each hidden state. A decision rule $d:Z\to A$ induces a strategy $d\circ e:\Theta\to A$. A garbling $f:Z\to Z'$ produces $e'=f\circ e$.

For prior $\pi$ and signed bounded loss $L(\theta,a)$, the paper uses

\[
R_L^\pi(e,d)=\mathbb E_{\theta\sim\pi,a\sim d(e(\theta))}L(\theta,a),
\qquad \|L\|_\infty=\max_{\theta,a}|L(\theta,a)|.
\]

The Bayes value is the minimum over available rules. A perfect experiment reveals $\theta$; a terminal experiment reveals nothing. The former permits pointwise action minimization, whereas the latter chooses before learning anything about $\theta$.

The qualitative DPI is simply feasible-strategy containment. Every rule after $e'$ can be used after $e$ by first applying $f$. Therefore garbling cannot improve the minimized risk. Theorem 3 extends this to an arbitrary real-valued functional of induced strategies, rather than requiring an expectation of a loss.

## 2. What the categorical formulation adds

The decision presheaf assigns to each experiment its rule set and maps a rule after a garbled experiment back by precomposition. A risk functional is compatible with this map because the induced strategy is unchanged. Theorem 4 states that taking the minimum in each such set preserves the resulting order.

For a fixed admissible strategy set $S_A\subseteq M(\Theta,A)$, define

\[
D_S(e,A)=\{d\in M(Z,A):d\circ e\in S_A\}.
\]

Lemma 5 establishes precomposition stability for **any** such strategy constraint. If $d'$ is admissible after $e'$, then $d'\circ f$ induces exactly the same strategy after $e$. This proves constrained DPI by the same containment argument.

A general decision sub-presheaf is contained in the canonical strategy constraint formed from its rules at the identity experiment. The paper proves inclusion, not equality. Replacing a general information-access constraint by that larger strategy set can therefore change the comparison.

For quantitative comparison across changing action sets, the paper imposes more structure: post-processing of an admissible action must remain admissible, and every rule set $D(e,A)$ is assumed convex in the text preceding Theorem 6. Unbiasedness supplies qualitative DPI but generally fails this arbitrary post-processing property. These extra conditions are not consequences of merely restricting a decision maker's observations.

## 3. The author's constrained randomization claim

Ordinary prior-weighted deficiency is written

\[
\xi^\pi(e,e')=
\min_{f:Z\to Z'}\mathbb E_{\theta\sim\pi}
V(f\circ e(\theta),e'(\theta)).
\]

The paper introduces all compliant coarsenings

\[
H(e)=\{h:Z\to\widetilde Z:\ h\circ e\in S_{\widetilde Z}\},
\]

allowing every finite output alphabet $\widetilde Z$, and defines

\[
\xi_D^\pi(e,e')=
\max_{h'\in H(e')}\min_{h\in H(e)}
\xi^\pi(h\circ e,h'\circ e').
\]

**Theorem 6, PDF p. 10**, claims equivalence between $\xi_D^\pi(e,e')\le\epsilon$ and

\[
\underline R_{L,D}^\pi(e)
\le \underline R_{L,D}^\pi(e')+\epsilon\|L\|_\infty
\]

for every loss and action set at the fixed prior $\pi$. It does not certify states assigned zero prior mass, or supply a uniform-over-priors conclusion without another quantifier. Corollary 7 sets $\epsilon=0$.

The forward proof simulates each compliant target coarsening, then applies its downstream rule. Closure under post-processing preserves admissibility, and contraction of variational divergence bounds the risk difference. The converse fixes an admissible target rule and applies minimax to the affine-in-rule, concave-in-loss objective obtained by subtracting $\epsilon\|L\|_\infty$. A suitable simulator for that target rule is then extracted. The proof invokes Komiya's minimax theorem or convex duality and the author's 2025 *On Experiments*.

**Independent unpacking of the quantifiers:** since any $d\in D(e,A)$ can itself be used as a compliant coarsening followed by the identity, and any post-processing of a compliant coarsening is admissible, the inner simulation concerns matching a specified target strategy. With a consistent $\ell_1$ norm and sup/inf conventions, the corresponding fixed-action comparison has the form

\[
\sup_{d'\in D(e',A)}\inf_{d\in D(e,A)}
\mathbb E_\pi\|d\circ e(\theta)-d'\circ e'(\theta)\|_1.
\]

The matching rule can depend on the target rule. The displayed construction does not assert one reconstruction kernel chosen once for all admissible target rules, all contexts, or all future policies.

Theorem 8, PDF pp. 11–12, further claims that both optimizations may be restricted to minimal members of the garbling preorder on $H(e)$. Its proof shows that more informative compliant channels improve the relevant objective. Monotonicity alone does not prove that minimal compliant channels exist. The counterexample below addresses precisely this missing step.

## 4. Independent check: inconsistent variational normalization

The manuscript uses incompatible normalizations in §§4.1–4.2. For a uniform binary experiment with zero–one loss, the exact identity is

\[
\frac12-\underline R
=\frac12\sup_C[Q(C)-P(C)]
=\frac12\operatorname{TV}(P,Q)
=\frac14\|P-Q\|_1,
\]

where $\operatorname{TV}=\frac12\|P-Q\|_1$ is defined explicitly here to avoid convention ambiguity.

On PDF p. 12 the paper calls the left side $V(P,Q)$. On p. 13 it also identifies $V$ with the $\phi$-divergence for $\phi(t)=|t-1|$, which, for strictly positive finite probabilities, equals $\|P-Q\|_1$. These differ by a factor of four.

A positive rational example removes support/absolute-continuity issues:

\[
P=(3/4,1/4),\qquad Q=(1/4,3/4).
\]

Exact arithmetic gives Bayes error $1/4$, blind-risk improvement $1/4$, $\operatorname{TV}=1/2$, and the displayed $\phi$-divergence $1$. Both pages and the TeX were checked. This is an internally observable constant error, not merely a preference between two standard TV conventions.

Theorem 6's coefficient $\|L\|_\infty\xi$ naturally uses the dual norm $V(P,Q)=\|P-Q\|_1$ for arbitrary signed bounded losses. If ordinary half-$\ell_1$ TV is used, the corresponding general signed-loss estimate has coefficient $2\|L\|_\infty$. A narrower loss range can be centered to sharpen this, but its range must be stated. The paper's DPI monotonicity survives a positive rescaling; its printed constants must not be transferred without choosing a consistent convention.

## 5. Independent counterexample: admissible fibers need closure, and minimal coarsenings can be absent

The paper explicitly assumes convexity and post-processing closure. It does **not** state closedness/compactness or prove attainment for the arbitrary sets used in its minimum and saddle-point assertions. Here is one family satisfying its stated structural conditions.

Let $\Theta=\{0,1\}$, $e=\mathrm{id}_\Theta$, and fix $0<c<1$. For every finite action set $A$, define

\[
S_A=\{s:\Theta\to A:\operatorname{TV}(s(0),s(1))<c\}.
\]

This family is nonempty, convex and closed under every Markov post-processing, by TV contraction. Its induced rule sets form the required bifunctor. The strict inequality makes them nonclosed.

### A missing minimum

With binary actions and uniform zero–one classification, write $p_i=\Pr(A=1\mid\theta=i)$. Admissibility is $|p_1-p_0|<c$, and

\[
R=\frac{1-(p_1-p_0)}2.
\]

The infimum is $(1-c)/2$, but no admissible rule attains it. Thus finite observation/action alphabets and convexity do not themselves justify the paper's use of a minimum or an attained saddle point. Using infima preserves the elementary containment DPI; a quantitative attained simulation theorem needs additional conditions or an explicit closure/approximation formulation. This note does not claim to repair every theorem under a new set of assumptions.

### No minimal element of $H(e)$

Take any compliant finite-output channel $h$, with
$\delta=\operatorname{TV}(h(0),h(1))<c$. Define

\[
\alpha=\frac{c-\delta}{2(1-\delta)}\in(0,1).
\]

Construct $h^+$ as follows: with probability $1-\alpha$, use $h$ on its old output alphabet; with probability $\alpha$, output one of two new tags revealing $\theta$. Then

\[
\operatorname{TV}(h^+(0),h^+(1))
=(1-\alpha)\delta+\alpha
=\frac{c+\delta}{2}<c.
\]

So $h^+$ remains compliant. A garbling recovers $h$ by retaining old outputs and replacing a revealing tag $i$ by a draw from $h(i)$. The reverse garbling is impossible: it would increase TV from $\delta$ to $(c+\delta)/2$. Therefore every compliant channel has a strictly more informative compliant predecessor. **There is no minimal member of $H(e)$.**

For $e=e'$, the paper's unrestricted expression for $\xi_D^\pi(e,e)$ is still exactly zero: for each $h'$ choose $h=h'$ and the identity simulator. Theorem 8's expression over minimal members instead has empty indexing sets. This gives a concrete counterexample to that reduction under the stated general hypotheses, beyond merely noticing an omitted proof step.

The construction was also checked in exact rational arithmetic for $c=3/4$ and

\[
h=\begin{pmatrix}3/4&1/4\\1/4&3/4\end{pmatrix},\qquad
h^+=\begin{pmatrix}9/16&3/16\\3/16&9/16\\1/4&0\\0&1/4\end{pmatrix}.
\]

Their TV values are $1/2$ and $5/8$. The recovery kernel with columns $(1,0)$, $(0,1)$, $(3/4,1/4)$ and $(1/4,3/4)$ maps $h^+$ exactly to $h$.

This obstruction uses a **strict** admissibility threshold. It does not show that the paper's particular closed equalized-odds fibers lack minima, or that a suitably stated compact version of the quantitative comparison is false. It shows that the generality printed in the paper is insufficient.

## 6. The worked fairness example remains informative within its scope

The paper first discusses demographic parity, then uses **equalized odds** for its substantive example. Let hidden state be $(\theta_0,y)\in\{0,1\}^2$ under the uniform prior. Only a binary observation $Z$ is revealed; the decision rule does not additionally receive $y$.

For $0<\varepsilon<1/2$, experiment $e_1$ applies a group-independent binary symmetric channel with crossover $\varepsilon$. Experiment $e_2$ is noiseless when $y=0$ and has crossover $2\varepsilon$ when $y=1$. At the specified task-label zero–one loss and prior, both have unconstrained risk $\varepsilon$.

Equalized odds requires the action to be conditionally independent of $y$ given $\theta_0$. For $e_1$, the Bayes identity rule already satisfies it. For $e_2$, comparing the two groups at label zero gives

\[
2\varepsilon(p_1-p_0)=0,
\]

so every admissible rule ignores $Z$ and has risk $1/2$. This elementary calculation was followed directly, including the model's observation restriction.

Corollary 10 proves incomparability in both directions. A garbling from $e_2$ to $e_1$ would contradict constrained DPI. A garbling from $e_1$ to $e_2$ cannot create dependence on $y$. The direct channel calculation gives the same conclusion. The evidence is equality of **one** unconstrained Bayes risk, followed by a separating constrained value; it is not equality under every unconstrained decision problem.

The examples for arbitrary fairness sublevel sets and unbiasedness use strategy-level precomposition stability. Arbitrary action post-processing is a separate requirement. In particular, unbiasedness is an affine, hence convex, constraint on randomized strategies; the conclusion's statement that convexity excludes unbiasedness is incorrect. The body earlier gives the relevant obstruction correctly: unbiasedness is generally not preserved by arbitrary post-processing.

## 7. Remaining formal and scientific limits

- Theorem numbers in this note follow the printed statements: constrained randomization is Theorem 6 and the minimal-coarsening claim is Theorem 8. The conclusion instead refers to 7 and 9. Its naturality display on p. 7 also writes the type-inconsistent composition $e\circ d$ where the strategy is $d\circ e$. These are additional editorial issues, distinct from the substantive existence counterexample.
- The qualitative presheaf result allows arbitrary risk functionals but still requires a meaningful minimum, or an infimum in an appropriate extended order. An inclusion of one set in another does not establish nonemptiness. Some constraints can make all feasible rules disappear.
- The paper explicitly leaves computational constraints and effective characterization of minimal compliant coarsenings to future work. It supplies no generic polynomial-time checking algorithm or finite-sample confidence bound.
- Its main formal setting is finite experiments and action sets. The illustrative convex action set for unbiased estimation and broad $\phi$-divergence correspondence require their own action-space/existence conditions. No extension to arbitrary infinite spaces is proved.
- No empirical experiment, learned representation benchmark, or causal sequential simulator is supplied. The only substantive numerical example is analytically calculated.
- The main imported dependencies are classical experiment comparison and deficiency, minimax, categorical experiment comparison, and risk/divergence correspondences. The cited papers retain separate reading statuses. The author's *On Experiments*, 2508.08288v2, is retrieved but not read by completing this note.

## 8. Relation to Astra's current question

This is directly relevant literature for the one-stage decision-comparison question in `62ddbdd`: admissible-rule stability matters, and approximate domination needs quantified simulator error. It does **not** by itself establish that FP's local observation constraints form the required post-processing-closed class, or that its target permits the same quantifiers as the paper. In particular, the target-dependent matching rule above cannot be silently replaced by one shared contextual reconstruction distribution.

Astra's subsequent `625c026` target adds actions, observation arrival times and a simulator shared across policies. This paper has no sequential causality or controlled-observation theorem, so it cannot close that question. Likewise, unrestricted next-token log loss has no finite global $\|L\|_\infty$ when predicted probabilities may approach zero. An actual probability floor, finite bounded action family or other score-range argument must be supplied before using the displayed loss constant.

No FP theory or experiments were edited. The source's qualitative containment argument and carefully stated quantitative ideas remain leads, with the normalization and existence objections attached. The next full reading is the four-author November 11, 2026 merger *Comparing Experiments in Discounted Problems*, selected after checking the author-reported relationship to Astra’s named sequential source. *On Experiments* is retained for a specific normalization/proof lookup, rather than becoming a background full-reading obligation.
