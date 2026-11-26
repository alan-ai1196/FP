# Kara — linear learning on a finite observation window

## Source, edition and actual coverage

- **Paper:** Ali Devran Kara, *Learning POMDPs with Linear Function Approximation and Finite Memory*.
- **Selected edition:** [arXiv:2505.14879v1](https://arxiv.org/abs/2505.14879v1), submitted May 20, 2025 at 20:10:23 UTC. [PDF](https://arxiv.org/pdf/2505.14879v1) · [complete TeX](https://arxiv.org/src/2505.14879v1) · [HTML](https://arxiv.org/html/2505.14879v1). The inspected arXiv history contains only v1. This is an eight-page edition.
- **Reading:** Pro-C, November 26, 2026, read the complete active `linear_pomdp.tex`, all four main sections and subsections, all statements and proofs, every displayed formula and all 16 printed bibliography entries. Original PDF pages 3, 4, 6, 7 and 8 were visually inspected. There are no scientific figures, tables, appendices or numerical experiments. The author affiliation footnote was read. Commented-out source material is not counted as part of the paper.
- **Evidence:** full reading and bounded independent mathematical checks. A support reader independently checked the stationary-law and greedy-projection interfaces. The principal reader checked the exact rational example and the retained contraction argument. No formal certification, experiment replication or FP core modification.
- **Edition boundary:** publisher-deposited Crossref metadata authenticates the separate [CDC 2025 proceedings edition](https://doi.org/10.1109/CDC57313.2025.11312019), published December 9, 2025, pp.311–316. Its six-page final was not retrieved, with the IEEE full-text endpoint returning HTTP 418. It must not be treated as text-equivalent to this eight-page preprint. The findings below are explicitly about arXiv v1. No withdrawal or replacement was observed on its arXiv record.
- **Local source:** `literature/corpus/pro_c/kara2025finite/paper.pdf`, SHA256 `5d7d3c026cffe929198a71ede6d3bdd0f6b05f9c0990faaeba730e3509109ef9`, with source archive, active TeX and bibliography retained beside it. The source URLs identify the reproducible edition even though bulk source files are ignored by Git.

## Main assessment

The paper combines a fixed finite observation-action window with linear temporal-difference learning. Its most useful separation is between **memory truncation error, projection error and the sampling distribution used by the learner**. Neither the window length nor the feature functions are learned.

The stationary one-step conditional kernel supports a clean contraction argument even when the window process is not Markov. However, the paper identifies this conditional kernel with a different object, a filter restarted from the stationary hidden-state marginal. Under the stated finite-memory feedback policies, retained actions can reveal observations preceding the window. An explicit uniformly mixing binary model makes those two conditional laws different and makes the claimed reset-model TD fixed point fail its actual expected update equation.

The correction preserves useful mathematics. Define the stationary conditional kernel directly, keep its policy dependence, and do not automatically inherit the reset-filter approximation guarantee. The separate optimal-Q proof also needs an integral argument and a uniform covariance margin. A local repair is given below, without declaring all Q-learning convergence conclusions false.

## 1. Objects, information and supplied structure

The source uses a discounted POMDP with Borel hidden-state, observation and action spaces, hidden transition kernel \(\mathcal T(dx'\mid x,u)\), observation channel \(O(dy\mid x)\), bounded stage cost where required, and discount \(0<\beta<1\). At time \(t\), the controller has the observation-action history ending with \(Y_t\). [§I-A, Eqs.1–2.]

In §II, an exact augmented state is

\[
Z_t=(\mu_{t-N},H_t^N),\qquad
H_t^N=(Y_t,\ldots,Y_{t-N},U_{t-1},\ldots,U_{t-N}),
\]

where \(\mu_{t-N}\) is the predictor based on the history before the retained observations. Keeping both coordinates is sufficient. Replacing the predictor by one fixed \(\nu\) produces the approximate window model \(\eta_\nu\) and its cost \(\hat c_\nu\). The fixed-prior model is a well-defined comparison model when its conditional probabilities are specified. It is not automatically the empirical one-step conditional model of an arbitrary feedback-controlled stationary trajectory. [Eqs.3–8.]

The paper subsequently changes its window-length convention from \(N+1\) observations and \(N\) actions to \(N\) observations and \(N-1\) actions. Here the actual variables, rather than that inconsistent label, determine the interface.

For evaluation, the supplied functions \(\phi_i(H)\), \(|\phi_i|\le1\), define \(V_\theta(H)=\theta^\top\phi(H)\). The update is

\[
\theta_{t+1}=\theta_t+
\alpha_t\phi(H_t)
\{C_t+\beta\theta_t^\top\phi(H_{t+1})-\theta_t^\top\phi(H_t)\},
\qquad C_t=c(X_t,U_t).
\]

The hidden state is not needed by this formula **if the realized cost is observed**. An observation/action-only log without cost feedback does not implement the update as written. The required inputs are a chosen window, its given features, a fixed policy, observed costs and a trajectory. [§III, Eq.12.]

## 2. Ergodicity is a property of the controlled augmented process

The paper correctly notes that \(H_t\) need not be Markov. The finite-memory controlled process \((H_t,X_t,U_t)\) is Markov. Assumption 2 posits exponential ergodicity of this augmented chain. Conditions on the hidden transition alone do not control an action memory that can retain its own past indefinitely.

Assumption 3 supplies nonzero common minorizing measures for both the hidden transition and the policy:

\[
\mathcal T(\cdot\mid x,u)\ge\lambda_x,
\qquad \gamma(\cdot\mid h)\ge\lambda_u.
\]

After a block flushes the original window, the proof obtains a common minorization for the augmented chain. This is a valid useful route to uniform geometric mixing. Perturbing a policy by a small exploratory mixture supplies the **policy** minorization. It does not create a missing common minorization of \(\mathcal T\). [§III-A, Lemma 1 and following remark.]

The imported linear stochastic-approximation proposition also requires positive nonincreasing step sizes, finite moments and summable mixing deviations. The main theorem only repeats the two Robbins–Monro sums. Use the complete imported hypotheses, bounded costs and a positive definite stationary feature Gram matrix when reusing the standard convergence argument. Pointwise independence of feature functions is weaker than independence in \(L^2\) of the sampled law. Unsupported features cannot yield a unique identified parameter.

## 3. The stationary law and the reset filter are different objects

Let \(\varpi\) denote the stationary law of the augmented chain, and let \(\varpi_H\) and \(\varpi_X\) be its marginals. The end of §III-A asserts

\[
\Pr_\varpi(X_t\in\cdot\mid H_t=h)
=P^{\varpi_X}(X_t\in\cdot\mid h).
\]

On the right, §II supplies the filter starting at the hidden marginal and using the retained observations and actions as the specified control history. This equality needs additional conditions. In a general finite-memory policy, an action near the left edge of the window depends on observations before that edge. Conditioning on that action supplies information about the omitted past. The marginal \(\varpi_X\) alone does not specify this joint boundary law.

If instead the right side is defined to include the full stationary joint boundary memory and its feedback likelihoods, the equality is true by definition. It then denotes a different model from the fixed-prior construction in §II. This distinction is material to the learned Bellman operator.

### Exact positive finite example

Use binary hidden states, observations and actions, with independent fresh noises and

\[
\Pr(X_{t+1}=X_t)=\tfrac34,
\qquad \Pr(Y_t=X_t)=\tfrac34,
\qquad \Pr(U_t=Y_{t-1})=\tfrac34.
\]

Actions have no effect on the hidden transition. The policy uses the valid finite window

\[
H_t=(Y_t,Y_{t-1},U_{t-1}).
\]

All hidden-transition and action probabilities are at least \(1/4\). Thus the paper's common-minorization hypothesis holds and the finite augmented chain is uniformly mixing. The hidden stationary marginal is fair.

At \(h=(1,1,1)\), exact summation over \(X_{t-2:t}\) and \(Y_{t-2}\) gives

\[
\Pr_\varpi(H_t=h)=\frac{39}{256},
\qquad
\Pr_\varpi(X_t=1,H_t=h)=\frac{33}{256},
\]

and hence

\[
\Pr_\varpi(X_t=1\mid H_t=(1,1,1))=\frac{11}{13}.
\]

The reset filter starts from a fair \(X_{t-1}\), observes \(Y_{t-1}=1\), advances one hidden transition and observes \(Y_t=1\). Its intermediate probabilities are \(3/4\) and \(5/8\), giving

\[
P^{\varpi_X}(X_t=1\mid Y_{t-1}=1,Y_t=1,U_{t-1}=1)
=\frac{(3/4)(5/8)}{(3/4)(5/8)+(1/4)(3/8)}
=\frac56.
\]

The action does not enter this reset controlled filter because it does not alter \(\mathcal T\). In the actual stationary law it is a noisy report of \(Y_{t-2}\). At \(H_t=(1,1,0)\), the actual posterior is \(9/11\), while the reset posterior remains \(5/6\).

For a short check of the first joint probability, the stationary observation law has

\[
\Pr(Y_{t-2:t}=111)=\frac{21}{128},
\qquad \Pr(Y_{t-2:t}=011)=\frac{15}{128}.
\]

Weighting them by \(3/4\) and \(1/4\) gives \(39/256\). These are exact finite-model probabilities, not a simulation.

### A nonzero TD residual at the printed target

Set \(c(x,u)=x\), \(\beta=1/2\), and use all eight window indicators as features. The reset-model value is independent of the retained action. Ordered by \((Y_t,Y_{t-1})\), it is

| Observation pair | 00 | 01 | 10 | 11 |
|---|---:|---:|---:|---:|
| Reset posterior of \(X_t=1\) | \(1/6\) | \(5/14\) | \(9/14\) | \(5/6\) |
| Reset-model value \(J_\nu\) | \(23/39\) | \(31/39\) | \(47/39\) | \(55/39\) |

Each table entry follows from the four-state Bellman equation. Conditional on a posterior \(b\), the next positive observation has probability \(3/8+b/4\).

At \(h=111\), the immediate-cost discrepancy is

\[
\frac{11}{13}-\frac56=\frac1{78},
\]

and the next-positive-observation discrepancy is \(1/312\). The two successor values differ by \(55/39-31/39=8/13\). Consequently,

\[
(T_{\rm stat}J_\nu-J_\nu)(111)
=\frac1{78}+\frac12\frac1{312}\frac8{13}
=\frac7{507}\ne0.
\]

All eight bins have positive stationary mass, so their Gram matrix is nonsingular. The expected update in the \(111\) indicator coordinate is nonzero. **The reset-model fixed point claimed in Theorem 1 is therefore not the stationary TD target in this example.**

The actual TD algorithm still has the ordinary stationary projected target and a valid convergence route. This example does not show TD divergence. It also does not by itself refute every contraction statement about the reset kernel. In fact its reset kernel happens to preserve the window marginal. The material failure is the identification of its costs/conditional transitions with the sampled ones.

## 4. Positive result retained by direct disintegration

Define the true stationary one-step law and cost by

\[
K_\gamma(dh'\mid h,u)
=\Pr_\varpi(H_{t+1}\in dh'\mid H_t=h,U_t=u),
\qquad
r_\gamma(h,u)=\mathbb E_\varpi[C_t\mid H_t=h,U_t=u].
\]

The policy randomization uses fresh randomness conditional on \(H_t\). Its average kernel \(K_\gamma^\gamma\) preserves \(\varpi_H\) by stationarity, irrespective of whether the original window sequence is Markov. Conditional Jensen gives

\[
\|K_\gamma^\gamma f\|_{L^2(\varpi_H)}\le\|f\|_{L^2(\varpi_H)}.
\]

Thus the operator

\[
\overline T^\gamma f=r_\gamma^\gamma+\beta K_\gamma^\gamma f
\]

and its composition with the orthogonal feature projection \(\Pi_\varpi\) are \(\beta\)-contractions in \(L^2(\varpi_H)\). The function-level fixed point is unique. This is the stationary surrogate justified by the sampled normal equations.

For \(G=\mathbb E_\varpi[\phi(H)\phi(H)^\top]\succ0\) and

\[
A=\mathbb E_\varpi[\phi(H)\{\beta\phi(H')-\phi(H)\}^\top],
\]

stationarity and Cauchy–Schwarz imply, for any vector \(v\),

\[
v^\top Av
\le-(1-\beta)v^\top Gv.
\]

This gives the stable mean drift needed by the imported linear stochastic-approximation argument, under its actual mixing and step-size conditions. Non-Markov windows alone are not an obstruction to that argument.

The surrogate value is still not automatically the original POMDP's future value conditional on the window. Iterating a one-step Markovization generally changes multi-step laws. Under a different deployment policy, its hidden conditional law can also change. A policy-independent fixed-prior model, a behavior-dependent stationary conditional model and the true controlled process must remain distinct.

### Projection error and a basis-invariant qualification

For the corrected stationary surrogate, let \(J=\overline T^\gamma J\) and \(V=\Pi_\varpi\overline T^\gamma V\). The paper's usual argument yields

\[
\|J-V\|_2\le\frac{\|J-\Pi_\varpi J\|_2}{1-\beta}.
\]

Orthogonality gives the familiar sharper consequence

\[
\|J-V\|_2^2
=\|J-\Pi_\varpi J\|_2^2+\|\Pi_\varpi J-V\|_2^2
\le\|J-\Pi_\varpi J\|_2^2+\beta^2\|J-V\|_2^2,
\]

so the denominator may be replaced by \(\sqrt{1-\beta^2}\). This is a direct standard projection deduction, not a new general POMDP theorem.

The source's uniform error bound assumes an everywhere approximation \(\|J-\hat\theta^\top\phi\|_\infty\le\lambda\) and pays \(\sqrt{d/\lambda_{\min}(G)}\). A precise geometric factor is

\[
\Lambda_\phi=\sup_h\sqrt{\phi(h)^\top G^{-1}\phi(h)}.
\]

For a feature-span function \(f\), \(\|f\|_\infty\le\Lambda_\phi\|f\|_2\). Unlike a raw Gram eigenvalue, \(\Lambda_\phi\) is invariant under invertible changes of feature coordinates. Combining this inequality with the preceding estimate gives

\[
\|J-V\|_\infty
\le\lambda\left[1+\Lambda_\phi\left(1+\frac1{\sqrt{1-\beta^2}}\right)\right].
\]

This bound requires \(G\succ0\) and finite \(\Lambda_\phi\). It does not supply features, coverage or filter stability. Proposition 5's original coefficient remains a valid weaker algebraic bound once its operator identification and positive Gram premise hold.

## 5. Optimal-Q learning and what the covariance condition must do

The source replaces the next value in Eq.12 by \(\min_u\theta^\top\phi(H',u)\). The exploration policy is fixed. Assumption 5 requires

\[
\beta^2\Sigma_\theta\prec\Sigma_\gamma
\quad\text{for every }\theta,
\]

where \(\Sigma_\gamma\) uses sampled actions and \(\Sigma_\theta\) uses greedy actions at the behavior stationary window marginal. This is not merely a lower bound on the probability of trying each action. It compares every attainable greedy feature covariance against the behavior covariance. [§IV, Eqs.13–16, Theorem 3.]

The printed proof first takes a maximum over \(\theta\) separately at each \(h\), then treats its maximizer as one global parameter inside an integral. That exchange is not justified by the pointwise inequality. A useful repair for finite actions is available.

Let \(v=\theta_f-\theta_g\), \(\theta_s=\theta_g+sv\), and \(m_h(\theta)=\min_u\theta^\top\phi(h,u)\). Along this segment, \(m_h\) is piecewise linear. For almost every \(s\),

\[
\frac{d}{ds}m_h(\theta_s)
=v^\top\phi(h,\gamma_{\theta_s}(h)).
\]

Jensen and Fubini therefore give

\[
\int|m_h(\theta_f)-m_h(\theta_g)|^2\,\varpi_H(dh)
\le\int_0^1v^\top\Sigma_{\theta_s}v\,ds.
\]

With the explicit uniform margin

\[
\beta^2\Sigma_\theta\preceq\kappa^2\Sigma_\gamma
\quad\text{for all }\theta,\qquad \kappa<1,
\]

this proves the required contraction on the feature span, using the genuine behavior conditional successor law. For finitely many attainable greedy policies, the source's strict positive-definite inequalities supply such a margin by taking a finite maximum. For general Borel spaces, uniformity, greedy-action attainment and measurable selections need to be stated and justified.

The Q recursion is nonlinear in \(\theta\), whereas the imported Proposition 3 is a **linear** stochastic-approximation theorem. A suitable nonlinear stochastic-approximation result is still needed after establishing contraction/stable drift. The integral proof repairs one analytic step. It is not a full independent certification of Theorem 3.

## 6. Exact representation and discretization

These are different positive cases.

**Bellman closure.** If the surrogate cost and transition kernel have the appropriate linear factorization, the Bellman image of the feature span remains in that span. Then projection leaves that image unchanged and the Bellman sup-norm contraction is available. Merely having \(Q^*\) in the span, as the introduction informally suggests, does not imply Bellman closure for other candidate \(Q\)'s. Convergence of a particular stochastic parameter update additionally needs its sampling and approximation theorem.

**Partition indicators.** For disjoint bins \(A_i\) of positive behavior mass,

\[
(\Pi_\varpi f)(h,u)
=\frac{\int_{A_i}f\,d\varpi}{\varpi(A_i)}
\quad\text{when }(h,u)\in A_i.
\]

This is conditional averaging and is nonexpansive in the sup norm. The indicators are orthogonal with squared norms \(\varpi(A_i)\), not orthonormal unless rescaled. The norm property comes from their partition-average structure, not orthonormality alone.

For a short counterexample to the general orthonormality assertion, give \(\{-1,1\}^3\) the uniform law and take \(\phi_i(s)=s_i\). These three functions are orthonormal and bounded by 1. For \(f(s)=\operatorname{sign}(s_1+s_2+s_3)\),

\[
\Pi f=\tfrac12(s_1+s_2+s_3),
\qquad \|f\|_\infty=1,
\qquad \|\Pi f\|_\infty=\tfrac32.
\]

The paper's actual partition-indicator argument survives this distinction. Every used bin needs positive occupancy and sufficient updates. Ergodicity alone does not put positive mass on every nominal bin.

The discretization result retains compact observations, a common observation density Lipschitz in the observation coordinate, bounded cost, finite actions or a justified action discretization, filter stability and sampling support. Its displayed basis count is exponential in window length, \((M|U|)^N\) under §IV's convention. It supplies no learned minimal memory and no computational saving independent of these counts. The claimed near-optimality separates a discretized-filter term from observation mesh error. Its transfer to the actual learned operator inherits the stationary-law issue above. [§IV-A, Assumption 6, Theorem 4.]

## 7. What can be retained and what remains conditional

| Result or mechanism | Status after this reading |
|---|---|
| Predictor plus raw window gives an exact augmented POMDP state | Retain under the stated controlled filtering convention |
| Replacing the predictor by one fixed prior defines a surrogate | Retain as a specified comparison model |
| Joint transition/policy minorization gives mixing after the window is flushed | Retain, with both minorization premises |
| Stationary disintegration equals the reset marginal-prior filter for all finite-memory policies | False in the exact positive binary example |
| Theorem 1 identifies the sampled TD target with that reset model | False in that example, residual \(7/507\) at one positive-mass bin |
| Direct stationary conditional kernel gives projected on-policy contraction | Independently derived above, no Markov claim about the raw window sequence |
| Projection and near-linear approximation bounds | Retain for the correct operator with support/Gram hypotheses |
| Optimal-Q contraction from a uniform greedy covariance margin | Conditional repaired proof for the stated finite-action setting |
| General orthonormal features imply sup-norm nonexpansive projection | False, partition indicators have the stronger required structure |
| Full finite-memory control error bound for arbitrary feedback exploration | Do not reuse automatically after changing the surrogate |

The paper reports no numerical results. This reading has no experiment to replicate and makes no sample-complexity or hardware-memory claim. Its formulas concern a prescribed finite window and a supplied approximation class. No FP migration is proposed. The corrected stationary-law tool and the explicit feedback-action counterexample are literature findings for Astra to evaluate.
