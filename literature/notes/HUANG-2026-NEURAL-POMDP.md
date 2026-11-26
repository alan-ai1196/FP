# Huang et al. 2026: neural TD on a finite-history POMDP surrogate

## Identity and actual coverage

- **Authors:** Jingjuan Huang, Zhiyao Zhang, Alvaro Velasquez, Nathaniel D. Bastian and Jia Liu.
- **Title:** *Finite-Time Convergence and Regret Guarantees for Neural Reinforcement Learning in POMDPs*.
- **Edition read:** [arXiv:2611.07069v1](https://arxiv.org/abs/2611.07069v1), submitted November 4, 2026 at 19:25:21 UTC. [Pinned PDF](https://arxiv.org/pdf/2611.07069v1). [Pinned TeX](https://arxiv.org/src/2611.07069v1).
- **Status:** third-party preprint, 33 actual PDF pages. The inspected primary version history lists only v1. A conference style file does not establish acceptance. No separately reviewed edition was authenticated.
- **Reader and date:** Pro-C, November 26, 2026, Shanghai.
- **Full reading:** abstract, main Sections 1–6, Algorithms 1–2, Appendices A–F, all displayed mathematical statements and proofs, five numbered figures, the hyperparameter table, title material and 51 bibliography entries. The main reader read the complete active TeX include tree, including the algorithm file and bibliography. Original PDF pages 3–9, 13, 18–19 and 32 were visually inspected, covering all five figures, both algorithms, the table, the architecture, the support argument and the imported NTK bounds.
- **Bounded support:** a second reader checked reset laws, support and the simulation argument. Another checked neural normalization, approximation dependencies and the PMD interface. The main reader examined their calculations and the relevant primary passages. These are scoped checks, not independent certification of every proof.
- **Dependency coverage:** Cai et al., arXiv:1905.10027v2, Appendix F on pp.47–49 through the imported lemma statements and the beginning of the linearization proof. Shen–Yang–Zhang's 32-page author manuscript, pp.1–3, especially Theorem 1.1 and Corollaries 1.2–1.3. Neither dependency was fully read. Their precise identities appear below.
- **Not done:** no Lean proof, training run, empirical replication or code audit. The arXiv TeX bundle inspected here contains no executable experimental implementation. The paper refers to supplemental code, which was not obtained or inspected.

## Assessment

The paper separates actual POMDP sampling from a finite-history surrogate more carefully than a direct identification of the two conditional laws. Its reset-occupancy argument, the resulting \(\sqrt\gamma\) projected Bellman contraction and a conditional policy mirror descent error decomposition are useful mathematical tools.

Two explicit defects prevent adopting the printed end-to-end theorem without qualifications. A feasible suffix need not be a feasible history restarted from the stated initial distribution, so the surrogate Bayes filter can be undefined under the listed assumptions. Independently, the network as printed has initialization output and parameter-gradient scales of order \(\sqrt m\), contrary to the imported bounds used throughout the critic analysis. A further approximation interface is not established: unrestricted constructive approximation does not itself locate a suitable frozen-endpoint network within a constant radius of random initialization.

These findings have different logical scopes. The support example concerns definition and applicability. The normalization calculation contradicts an explicit intermediate assertion. The local approximation issue identifies an unproved interface and a strong extra assumption. None establishes that all finite-memory TD or PMD algorithms fail.

| Item | Source claim or mechanism | Assessment after bounded checking |
|---|---|---|
| Finite-memory value comparison | Exponential pointwise filter stability gives a uniform value gap | Supported once every required surrogate belief is well defined and comparable to the true belief |
| Reset sampling | Full hidden-state and memory resets give geometric mixing | Supported for the specified reset access model |
| Actual versus surrogate occupancy | Separate stationary laws, with an explicit TV error | Supported, with a small initialization refinement below |
| Projected Bellman geometry | Contraction under discounted occupancy | Correct factor is \(\sqrt\gamma\), as used in the paper |
| Printed neural bounds | Initialization output \(O(\log m)\), gradient \(O(d)\) | Contradicted by a one-layer calculation under the printed scaling |
| Local approximation | Existence of an approximator inside the training ball | Not supplied by the cited unrestricted approximation result |
| \(N^{5/6}\) guarantee | Conditional cumulative initial-value gap | Requires repaired neural premises, stated schedules and uniform constants. It is not an actual reward-path or last-iterate guarantee |
| CheeseMaze experiments | Better curves in one small benchmark | Three-seed observations under the reported implementation choices, not verification of the theorem's assumptions |

## 1. The model and what is supplied

Section 3 uses finite hidden states \(S\), observations \(O\), actions \(A\), reward \(r(s,a)\in[0,r_{\max}]\), discount \(\gamma\in(0,1)\) and initial distribution \(\mathcal D\). The history is

\[
H_0=\varnothing,\qquad H_{t+1}=(H_t,A_t,O_{t+1}).
\]

The history convention contains actions and observations. If observed rewards carry additional hidden-state information and a comparison permits policies to use them, that information must be included in the observation/history model before calling this the unrestricted optimum for that richer interface.

A supplied map \(G\) keeps the last \(\ell\) action-observation pairs, including shorter prefixes, and produces \(B=G(H)\). The surrogate belief \(b_B\) replays that finite string from the fixed initial prior \(\mathcal D\). It is not defined as the actual stationary conditional distribution of the hidden state given \(B\).

The surrogate reward and transition kernel are constructed from \(b_B\). For example,

\[
\widetilde r(B,a)=\sum_s b_B(s)r(s,a).
\]

The paper assumes an injective unit-norm encoding \(\psi(B,a)\in\mathbb R^p\). It learns values and a policy on this supplied finite-history space. Neither the window operation nor the representational equivalence classes are discovered by the algorithm.

### Pointwise stability is the substantive memory premise

Assumption 2 asks that any two admissible histories with the same suffix satisfy

\[
\|b_H-b_{H'}\|_{\mathrm{TV}}\le\varepsilon_\ell,
\qquad \varepsilon_\ell=(1-\rho)^\ell,\quad \rho\in(0,1).
\]

This controls even rare histories pointwise. A filter theorem controlling expected distance alone cannot be substituted without an additional argument. The paper contrasts this assumption with a stronger uniform filter condition in its immediate predecessor, but that comparison does not remove the distinction between pointwise and expectation bounds.

## 2. A support condition missing from the restart construction

**Independent counterexample to the applicability step in Appendix A, Lemma 3.**

Take two hidden states, one action \(a\), deterministic transitions \(S_{t+1}=1-S_t\), exact observations \(O_t=S_t\), and \(\mathcal D=\delta_0\). Let \(\ell=1\), with any bounded reward, including zero.

The actual history \(H=(a,1,a,0)\) is feasible. Its suffix is \(B=(a,0)\). Restarting from \(\delta_0\), however, the first next state is necessarily 1. The likelihood of observation 0 is zero, so the denominator of the paper's specified Bayes map \(\mathcal U_{a,0}(\mathcal D)\) vanishes.

All feasible histories with a common last observation have the same exact-state posterior. Assumption 2 therefore holds with distance zero for any \(\rho\in(0,1)\). Bounded rewards also hold. These assumptions alone do not make the restart belief well defined.

The proof on p.13 treats the suffix itself as an admissible history from \(\mathcal D\). That implication needs an extra premise. Possible repairs are:

- Require every feasible suffix used by the algorithm to have positive likelihood when started from \(\mathcal D\).
- In the finite-state setting, require \(\mathcal D\) to have full support. Any positive-probability suffix path then also has a positive-probability start under this prior.
- Choose an actually feasible representative history \(H_B\) for each suffix and define the surrogate belief from that representative. Pairwise stability then compares \(H\) with \(H_B\), but this changes the specified restart construction.

This example does not refute the numerical simulation bound after a valid surrogate has been supplied. It also does not require weak mixing or a neural network.

## 3. Value comparison once the surrogate is defined

Under the additional support premise, the same-suffix assumption gives

\[
\|b_H-b_{G(H)}\|_{\mathrm{TV}}\le\varepsilon_\ell.
\]

Appendix A applies bounded reward and TV nonexpansiveness under the next-window observation kernel:

\[
|\bar r(H,a)-\widetilde r(G(H),a)|
\le2r_{\max}\varepsilon_\ell,
\]

\[
\|\operatorname{Law}(B_{t+1}\mid H_t=H,A_t=a)
-\widetilde P(\cdot\mid G(H),a)\|_{\mathrm{TV}}
\le\varepsilon_\ell.
\]

Comparing the two Bellman optimality equations and taking a supremum over histories gives the source's Theorem 1:

\[
\sup_H|V^*_{\mathrm P}(H)-\widetilde V^*(G(H))|
\le\Delta_\ell,\qquad
\Delta_\ell=\frac{2r_{\max}}{(1-\gamma)^2}\varepsilon_\ell.
\]

The unrestricted history-optimal value on the left is relative to the declared history information. The proof does not require the actual window process to be Markov. It compares full-history conditional transitions to a separately defined Markov surrogate.

**Independent policy-evaluation bridge.** Repeating this comparison with a fixed common window policy, using expectation instead of maximization, gives

\[
|V^\pi_{\mathrm P}(H)-\widetilde V^\pi(G(H))|\le\Delta_\ell.
\]

Consequently a surrogate-optimal policy has actual POMDP gap at most \(2\Delta_\ell\), provided the preceding uniform hypotheses hold. More generally, a cumulative surrogate-policy-value bound can be converted to the corresponding actual-policy-value sum at an additional cost \(N\Delta_\ell\). This extra conversion should be stated when interpreting the paper's regret definition.

## 4. Full resets, occupancy and the correct sampling law

### What Algorithm 1 actually does

At each critic clock step, an independent \(Z_{k+1}\sim\operatorname{Bernoulli}(\gamma)\) chooses a branch.

- If \(Z_{k+1}=0\), draw a new hidden state from \(\mathcal D\), set history and window to empty, sample a policy action, and leave the critic unchanged.
- If \(Z_{k+1}=1\), execute the action, observe reward and the next observation, update the window, sample the next action and perform a projected TD update.

The bootstrap uses the original non-reset transition and the same discount \(\gamma\). Each layer stays in a Frobenius ball of radius \(R\) around that phase's initialization. The output averages the parameter iterates. A fresh independent initialization is used in each policy phase.

Deleting the learner's memory alone cannot reset an inaccessible hidden environment. The assumption is an environment access capability, such as genuinely restartable episodes. Of \(K\) clock iterations, the expected number of executed action transitions is \(\gamma K\). Physical reset cost is not priced by this count.

### The two stationary distributions are not identified

For a fixed policy, let \(\widetilde P^\pi\) be the non-reset surrogate window-action kernel and let \(\nu^\pi\) place mass at the empty window and a policy action. The reset kernel is

\[
P^\pi_{\mathrm{reset}}
=(1-\gamma)\nu^\pi+\gamma\widetilde P^\pi.
\]

Its unique stationary law is

\[
\mu^\pi=(1-\gamma)\sum_{j\ge0}\gamma^j
\operatorname{Law}_{\mathrm{SMDP}}(B_j,A_j).
\]

This is normalized discounted occupancy for the original surrogate. Complete resets give a TV mixing bound \(\gamma^k\) from every initial state.

The actual sampler is Markov on \(X_k=(S_k,B_k,A_k)\). Its stationary law is denoted \(\xi^\pi\), with window-action marginal \(\mu^\pi_{\mathrm P}\). Appendix B expressly retains this distinct distribution. The same reset coupling gives mixing at most \(\gamma^k\).

The one-step comparison is valid at each full actual history, so its accumulated effect is bounded without pretending that the actual window sequence is Markov:

\[
\|\operatorname{Law}_{\mathrm P}(B_j,A_j)
-\operatorname{Law}_{\mathrm{SMDP}}(B_j,A_j)\|_{\mathrm{TV}}
\le j\varepsilon_\ell.
\]

The paper then obtains

\[
\|\mu^\pi_{\mathrm P}-\mu^\pi\|_{\mathrm{TV}}
\le\min\left\{1,\frac{\gamma\varepsilon_\ell}{1-\gamma}\right\}.
\]

### A bounded refinement from empty initialization

**Independent deduction, not a rederived critic theorem.** Starting from empty history, no information has been discarded at current times \(t\le\ell\). The true and surrogate one-step kernels at those times agree. Their window-action distributions therefore agree through time \(\ell+1\).

The first possible transition mismatch starts at current time \(\ell+1\), affecting the law at \(\ell+2\). The same telescoping argument improves the time-\(j\) bound to

\[
\|\operatorname{Law}_{\mathrm P}(B_j,A_j)
-\operatorname{Law}_{\mathrm{SMDP}}(B_j,A_j)\|_{\mathrm{TV}}
\le (j-\ell-1)_+\varepsilon_\ell.
\]

Summing its discounted weights yields

\[
\boxed{\|\mu^\pi_{\mathrm P}-\mu^\pi\|_{\mathrm{TV}}
\le\min\left\{1,
\frac{\gamma^{\ell+2}\varepsilon_\ell}{1-\gamma}\right\}.}
\]

This uses the same policy, exact empty initialization and the valid pointwise model comparison. It does not establish that every history-truncation term in the neural theorem can be multiplied by this factor.

### Why the Bellman contraction is \(\sqrt\gamma\)

The Bellman target uses the non-reset kernel, while the norm uses reset occupancy. From stationarity,

\[
\mu^\pi=(1-\gamma)\nu^\pi+\gamma\mu^\pi\widetilde P^\pi
\quad\Longrightarrow\quad
\mu^\pi\widetilde P^\pi\le\mu^\pi/\gamma.
\]

Jensen's inequality gives

\[
\|\widetilde T^\pi f-\widetilde T^\pi g\|_{\mu^\pi}^2
\le\gamma^2\int(f-g)^2\,d(\mu^\pi\widetilde P^\pi)
\le\gamma\|f-g\|_{\mu^\pi}^2.
\]

Projection onto a closed convex function class remains nonexpansive, so the projected map contracts by \(\sqrt\gamma\). The paper uses this factor correctly. It does not incorrectly assume that the original non-reset kernel is stationary in \(\mu^\pi\).

For the affine linearized network class, the associated variational inequality yields the one-point drift bound

\[
\langle\bar g_0(W)-\bar g_0(W^*),W-W^*\rangle
\ge(1-\sqrt\gamma)
\|Q_0(W)-Q_0(W^*)\|_{\mu^\pi}^2.
\]

Uniqueness in \(L^2(\mu^\pi)\), hence up to \(\mu^\pi\)-null pairs, does not require parameter uniqueness.

In Appendix C, the actual stochastic TD direction is decomposed into nonlinear linearization error, actual-to-surrogate population error and correlated sampling error. The population error includes both one-step reward/transition mismatch and occupancy mismatch. The mean descent has the factor \(\gamma\), because reset steps skip the update. The lagged-iterate argument uses the actual augmented chain. These interfaces are consistent with Algorithm 1.

## 5. The printed network normalization contradicts Fact 1

Section 3, p.4, specifies

\[
x^{(0)}=Ux,\qquad
x^{(h)}=m^{-1/2}\operatorname{ReLU}(W^{(h)}x^{(h-1)}),
\qquad Q(x)=c^\top x^{(d)},
\]

with unit input, iid \(U_{ij},W^{(h)}_{ij}\sim N(0,2)\), and iid \(c_i\sim N(0,1)\). Only the \(W\) matrices are trained. Appendix C, Fact 1, p.19, invokes high-probability bounds \(Q(x,W_0)=O(\log m)\) and \(\|\nabla_W Q(x,W)\|_2=O(d)\).

**Independent exact calculation.** Set \(d=1\) and fix any unit input. Let \(u=Ux\), so \(u\sim N(0,2I_m)\). Then

\[
Q=\frac1{\sqrt m}\sum_{i=1}^m c_i(w_i^\top u)_+.
\]

Conditional on \(u\), each \(w_i^\top u\) is centered Gaussian with variance \(2\|u\|^2\). Symmetry and independence give

\[
\mathbb E[Q^2\mid u]=\|u\|^2,
\qquad \boxed{\mathbb E Q^2=2m}.
\]

At differentiable initialization points,

\[
\|\nabla_WQ\|_F^2
=\frac{\|u\|^2}{m}
\sum_{i=1}^m c_i^2{\bf1}_{\{w_i^\top u>0\}},
\qquad
\boxed{\mathbb E\|\nabla_WQ\|_F^2=m}.
\]

This is not merely an expectation affected by rare events. Conditional on \(u\), normalized preactivations are iid standard Gaussians. The law of large numbers gives

\[
\frac{\|x^{(1)}\|^2}{m}\longrightarrow2,\qquad
\frac{\|\nabla_WQ\|_F^2}{m}\longrightarrow1
\quad\text{in probability}.
\]

Conditional on the hidden representation, the output is Gaussian with variance \(\|x^{(1)}\|^2\), hence

\[
Q/\sqrt m\Rightarrow N(0,2).
\]

For every fixed \(C\),

\[
\Pr\{|Q|\le C\log m\}\longrightarrow0.
\]

Thus both quoted scales fail even at initialization for a single fixed input. Fixed \(p\ge3\), \(d=1\), \(R=1\) satisfy Fact 1's width and radius restrictions for sufficiently large \(m\), so those restrictions do not exclude this case.

The same printed parameterization and bounds occur in **Cai et al., arXiv:1905.10027v2, Appendix F, pp.47–49**. The dependency check supports describing this as an inherited printed normalization inconsistency. It does not support accusing Huang of misquoting that source, or declaring Cai's entire paper false.

An additional \(m^{-1/2}\) output factor, or an appropriate input-layer rescaling, repairs the scales in this one-layer calculation. That observation is not a complete repair of the critic theorem. Gradient perturbation bounds, stepsizes, radius feasibility and the approximation class must then be analyzed under the changed parameterization.

## 6. Approximation and local training are distinct requirements

Lemma 2 invokes Shen–Yang–Zhang to assert an approximation order

\[
\varepsilon_{\mathrm{app}}(m,d)
=\widetilde O(m^{-2/p}d^{-2/p}).
\]

It selects an approximating parameter \(W_t^\dagger\), defines its layerwise distance \(R_t^\dagger\) from that phase's random initialization, and takes \(R^\dagger=\max_tR_t^\dagger\). The training ball contains these approximators if \(R\ge R^\dagger\). This containment is a condition, not a consequence of merely giving the ball a name.

The inspected Shen author manuscript states a constructive result for freely chosen ReLU networks. For a continuous function, its rate retains the modulus of continuity. For a Hölder function, it retains the exponent and Hölder constant. It does not directly establish the same rate for Huang's fixed random \(U,c\), trainable \(W\), and prescribed neighborhood of random initialization.

On a fixed finite encoded domain, a target can be continuously extended, but extension regularity depends on feature spacing. Injectivity and unit norm alone give no uniform spacing. If the window grows with the sample budget, neither the extension constant nor its approximation radius is automatically uniform. This is an unestablished interface, not a proof that all frozen-endpoint networks lack approximation power.

Corollaries 1–2 explicitly add \(R^\dagger=O(1)\). Under the other stated premises, the displayed simplified critic MSE is

\[
\mathbb E\|\widehat Q-\widetilde Q^\pi\|_{\mu^\pi}^2
\le\widetilde O\left(
m^{-1/6}+m^{-4/p}+K^{-1/2}+\varepsilon_\ell
\right),
\]

with \(R=O(1)\) and \(d=O(\log m)\). This conditional expression must not be detached from local approximation feasibility or the normalization defect.

The proof also selects

\[
\eta=K^{-1/2},\qquad
\tau=\max\left\{1,\left\lceil
\frac{\log K}{2|\log\gamma|}
\right\rceil\right\},\qquad K>\tau.
\]

The main theorem statement does not explicitly carry this critic stepsize. Algorithm 1 accepts \(\eta\) as input. A faithful statement of the proved schedule must include it.

## 7. The conditional PMD bound and what its regret means

Algorithm 2 starts from a uniform policy at every window and applies the tabular entropic update

\[
\pi_{t+1}(a\mid B)
\propto\pi_t(a\mid B)\exp(\kappa\widehat Q_t(B,a)).
\]

The recursive and cumulative exponential-weight forms are algebraically equivalent. The literal algorithm updates every \(B\), not just the currently visited window.

Let \(\widetilde\pi^*\) be optimal for the surrogate and \(\pi^*\) be history-optimal for the original POMDP. The quantity analyzed is

\[
R_N=K\sum_{t=0}^{T-1}
\mathbb E[V^{\pi^*}_{\mathrm P}(H_0)
-\widetilde V^{\pi_t}(B_0)],
\qquad N=TK,\quad H_0=B_0=\varnothing.
\]

It compares an original-model optimum with a surrogate-model policy value. Individual terms are not guaranteed nonnegative by this definition alone. It is a repeatedly weighted initial-value gap, rather than cumulative realized reward regret along one deployed POMDP path.

### A useful bound conditional on a valid critic

Suppose a critic, by whatever justified method, supplies

\[
\mathbb E\|\widehat Q_t-\widetilde Q^{\pi_t}\|_{\mu^{\pi_t}}^2
\le\varepsilon_K
\]

uniformly over phases, and \(\|\widehat Q_t\|_\infty\le Q_{\max}\). The paper's coverage condition is

\[
C_t=\sum_{B,a}
\frac{\mu^{\widetilde\pi^*}(B,a)^2}{\mu^{\pi_t}(B,a)},
\qquad \mathbb E C_t\le\bar C_\infty.
\]

This requires absolute continuity on the comparator support. Finite-time positive action probabilities do not imply a horizon-independent small constant.

The performance-difference identity separates the entropic online-learning term and the critic error. For the second error component, marginalizing the action variable cannot increase the squared density-ratio integral:

\[
\sum_B\frac{d^{\widetilde\pi^*}(B)^2}{d^{\pi_t}(B)}
\le C_t.
\]

Two Cauchy–Schwarz applications then give a total critic contribution at most \(2\sqrt{\bar C_\infty\varepsilon_K}\). Appendix D obtains

\[
R_N\le N\Delta_\ell+
\frac{K}{1-\gamma}
\left(
\frac{\log|A|}{\kappa}
+\frac{\kappa TQ_{\max}^2}{2}
+2T\sqrt{\bar C_\infty\varepsilon_K}
\right).
\]

With

\[
\kappa=\frac{\sqrt{2\log|A|}}{Q_{\max}\sqrt T},
\]

this becomes

\[
\boxed{
R_N\le N\Delta_\ell+
\frac{N}{1-\gamma}
\left[
Q_{\max}\sqrt{\frac{2\log|A|}{T}}
+2\sqrt{\bar C_\infty\varepsilon_K}
\right].}
\]

This conditional decomposition is reusable without endorsing the invalid printed neural scale bounds. The proof's policy stepsize should be included when citing it. The main Theorem 3 does not explicitly list that choice.

The averaged value gap is controlled. Algorithm 2 returns its last iterate \(\pi_T\), but the displayed sum does not by itself establish a last-iterate guarantee. Drawing an independent \(I\) uniformly from \(\{0,\ldots,T-1\}\) and deploying \(\pi_I\) for a whole episode gives the corresponding average-policy-value interpretation. This is not action-wise policy averaging. A justified last-iterate argument would be additional work.

### Resource conditions in the simplified rate

The paper chooses \(T=N^{1/3}\), \(K=N^{2/3}\) and requires

\[
\ell\ge\frac{\log N}{3|\log(1-\rho)|},
\qquad
m\gtrsim\max\{N^2,N^{p/12}\}.
\]

With the other conditional premises, this yields the stated \(\widetilde O(N^{5/6})\) rate. Constants suppressed by this expression include discount, coverage, local approximation geometry and input dimension. Uniform control as \(\ell\) and \(N\) vary needs justification.

The trainable matrices alone contain \(dm^2\) real parameters. The condition \(m\gtrsim N^2\) already gives \(\Omega(dN^4)\) such parameters in this sufficient regime. A direct dense implementation takes \(O(dm^2+mp)\) work per critic step. These are counts for the specified parameterization, not computational lower bounds against other algorithms.

If all action-observation strings are possible, the finite window set has

\[
|\mathsf B|=\sum_{j=0}^{\ell}(|A||O|)^j.
\]

Algorithm 2 explicitly ranges over it. A cumulative-critic implementation could trade table storage for stored critics and additional inference, but that tradeoff is not analyzed here. With a conventional concatenated encoding and fixed alphabets, \(p\) grows proportionally to \(\ell\). Then the sufficient factor \(N^{p/12}\) can be quasipolynomial in \(N\). Conversely, packing all windows into fixed-dimensional unit inputs leaves the spacing and approximation-regularity problem exposed.

No compact physical-state discovery theorem follows from a sublinear value-gap rate with these supplied interfaces.

## 8. What the experiments establish

Section 5 and Appendix E use CheeseMaze with 11 latent states, seven observations and four actions. Goal reward is 1 and other rewards are zero. Q-learning, actor-critic and neural PMD share window inputs and a nominal interaction budget. Windows are \(\ell=1,2,4\).

The reported table uses \(\gamma=0.99\), 200 outer phases, 500 critic steps per phase, two critic hidden layers of width 64, Adam with critic learning rate \(10^{-3}\), and seeds 1, 2 and 3. The PMD stepsize is 0.1. Evaluation uses 50 episodes every 500 training steps. Main plots report mean and one standard deviation. The sensitivity plot reports means over the same three-seed design.

For this benchmark, the reported curves improve substantially between window 1 and window 2, with relatively little additional improvement at window 4. PMD is smoother than the displayed Q-learning run family and learns earlier than actor-critic. The explanations involving greedy maximization and learning actor parameters are author interpretations. The experiment does not isolate them by a dedicated intervention.

The empirical cumulative curve uses \(\sum_tK(V^*-\widehat V_t)\), where \(\widehat V_t\) is Monte Carlo policy return. It is not direct measurement of the theoretical surrogate value. The inspected experimental sections do not give a separate derivation of the reference \(V^*\) or a direct surrogate-versus-actual evaluation. A finite, slowly growing curve does not establish an asymptotic regret exponent.

The reported Adam schedule, width 64 and omitted projection-radius details do not demonstrate the theorem's local-radius and large-width hypotheses. The table also does not establish exact implementation of the theoretical reset sampler. Without the implementation, this remains unverified rather than an accusation that the experiment used a different sampler.

The evidence is one small environment and three seeds. No independent replication was inspected or performed. There are no external datasets in the reported experiment. Nothing here establishes autonomous state formation, unrestricted POMDP generalization or a general superiority over other memory mechanisms.

## 9. A constructive evaluation model from actual reset data

**Independent source-grounded construction.** The reset geometry suggests a way to retain finite-window policy evaluation without requiring a suffix to be restartable from \(\mathcal D\). This is a conditional mathematical alternative, not the paper's algorithm, an implemented method or an FP architecture proposal.

Fix a window policy \(\pi\) with positive probability for every action at every reachable window. Run the same full-reset sampler. Under its actual stationary law \(\xi^\pi\), define

\[
\bar b^\pi_B=\operatorname{Law}_{\xi^\pi}(S\mid B),\qquad
\bar r^\pi(B,a)=\mathbb E_{\xi^\pi}[r(S,a)\mid B,A=a],
\]

and let \(\bar P^\pi\) be the conditional next-window/next-action law given \((B,a)\) on a non-reset transition. Restrict the model to reachable pairs with positive \(\mu^\pi_{\mathrm P}\) mass. The action draw is conditionally independent of the hidden state given \(B\), so these definitions use one common hidden-state conditional at each window.

Each reset episode starts from the genuine prior. Disintegrating the stationary law over episode age and full within-episode history expresses \(\bar b^\pi_B\) as a convex mixture of the actual posteriors \(b_H\) with \(G(H)=B\). Pairwise stability and convexity of TV therefore give

\[
\|b_H-\bar b^\pi_B\|_{\mathrm{TV}}\le\varepsilon_\ell
\]

for every reachable history in that window. No comparison to an infeasible restarted suffix is required.

Stationary flow also gives the exact identity

\[
\mu^\pi_{\mathrm P}
=(1-\gamma)\nu^\pi+\gamma\mu^\pi_{\mathrm P}\bar P^\pi.
\]

Thus the Bellman map \(\bar T^\pi q=\bar r^\pi+\gamma\bar P^\pi q\) is a \(\sqrt\gamma\) contraction in \(L^2(\mu^\pi_{\mathrm P})\). Its tabular fixed point is uniquely defined on reachable pairs. With a fixed convex linearized function class, the same projected contraction and one-point drift argument apply in that actual occupancy norm.

The reward and transition comparisons from Section 3 then give, for this fixed policy,

\[
\sup_{H\ \mathrm{reachable}}
|V^\pi_{\mathrm P}(H)-\bar V^\pi(G(H))|
\le\Delta_\ell.
\]

This produces a concrete acquisition route for the evaluation model. Count non-reset transitions and rewards for each visited window-action pair. The full-reset chain is geometrically mixing, and the independent reset coin does not change the stationary conditional distribution of the current pair on retained transitions. Finite-state ergodic averages consistently estimate every positive-mass row and reward mean. Solving the empirical discounted Bellman system then consistently estimates the defined surrogate value. Finite-sample uniform accuracy still depends on visitation masses and mixing. No new rate is claimed here.

The construction also shows its own boundary. Both \(\bar b^\pi\) and the data-defined kernel can change with \(\pi\). Therefore a policy-improvement proof for one fixed common surrogate MDP cannot simply be reused across these policy-specific models. The original PMD regret theorem is not repaired by replacing its kernel in this way.

### Freezing the learned reference model permits planning

There is a useful further construction. Choose one full-support reference policy \(\pi_0\), estimate its controlled reward and next-window kernel, and then freeze that model. The controlled kernel is obtained by marginalizing the next action out of the estimated window-action kernel.

Every feasible action-observation history has positive probability under \(\pi_0\). The convex-mixture posterior bound therefore holds for every reachable history, including histories produced by another policy. For any window policy \(\sigma\), the frozen reference model satisfies

\[
|V^\sigma_{\mathrm P}(H)
-\bar V_{\pi_0}^{\sigma}(G(H))|
\le\Delta_\ell.
\]

The optimal-value Bellman comparison also applies to this fixed controlled surrogate. If \(\bar\sigma^*\) is its optimal policy, then

\[
0\le V^*_{\mathrm P}(H)-V^{\bar\sigma^*}_{\mathrm P}(H)
\le2\Delta_\ell.
\]

Consequently, consistent finite-table estimates under \(\pi_0\), followed by exact discounted planning in the estimated frozen model, give an asymptotic construction with limiting actual value gap at most \(2\Delta_\ell\). Finite-dimensional discounted values are continuous in the reward and transition entries, so a vanishing uniform estimation error adds a vanishing planning error. Hidden states need not be observed.

This construction trades continual policy-specific critic evaluation for learning and retaining an entire reference window model. Rare-window acquisition, table size, true resets and subsequent planning cost remain real resources. The \(\sqrt\gamma\) weighted contraction established above is tied to the reference occupancy. It does not automatically control a different policy's off-policy critic. This planning construction supplies no finite-sample or neural PMD regret repair and makes no novelty claim.

## 10. Relation to previous Pro-C reading and remaining limits

The [Kara finite-memory linear-learning note](KARA-2025-FINITE-MEMORY-LINEAR.md) identifies the danger of replacing the actual stationary hidden-state conditional given a feedback window by a fixed-prior restart filter. Huang does not simply repeat that identification. It retains separate actual and surrogate laws and pays for their difference under pointwise filter stability and full resets. That distinction is a concrete positive contribution despite the separate defects above.

The available literature instruments are:

- A full-history-to-surrogate simulation comparison, with its support premise made explicit.
- A reset realization of discounted occupancy, including its environment-access cost.
- A \(\sqrt\gamma\) contraction for non-reset Bellman updates measured under reset occupancy.
- A critic-error-to-PMD-value-gap conversion under a specified density-ratio bound.
- A conditional model that can be acquired from actual reset trajectories. Freezing a full-support reference model supports subsequent planning with a \(2\Delta_\ell\) approximation bound, while avoiding infeasible suffix restarts.
- Negative evidence against transferring unrestricted approximation, or an NTK bound incompatible with the displayed normalization, to a local critic without checking the interface.

These are source-level mathematical tools. No FP architecture, core definition, research route or experimental protocol is changed or proposed as mandatory. A concrete FP transfer would require its own object map, access assumptions, resource accounting and falsifiable consequence.

The unfinished scientific questions are local and explicit: provide a support-safe surrogate, fix and reanalyze the network scaling, establish approximation in the actual frozen-endpoint local class, and keep constants uniform along the growing-window regime. This note does not silently perform those repairs or certify the resulting end-to-end theorem.

## Dependency sources and provenance

1. Huang et al., [arXiv:2611.07069v1](https://arxiv.org/abs/2611.07069v1). Main §§3–4 supply the model and theorem statements. Appendix A supplies the simulation proof, B the reset laws, C the critic argument, D the PMD conversion and E the experimental details.
2. Cai, Yang, Lee and Wang, [*Neural Temporal-Difference and Q-Learning Provably Converge to Global Optima*, arXiv:1905.10027v2](https://arxiv.org/abs/1905.10027v2), revised April 15, 2020 at 07:34:21 UTC. [Pinned 60-page PDF](https://arxiv.org/pdf/1905.10027v2). Only the Appendix F dependency passage on pp.47–49 was read. Other theorem families and the remainder of its proof chain were not audited.
3. Shen, Yang and Zhang, [32-page author manuscript](https://haizhaoyang.github.io/publications/NN_App_Optimal.pdf), *Optimal Approximation Rate of ReLU Networks in terms of Width and Depth*. The corresponding journal publication is *Journal de Mathématiques Pures et Appliquées* 157 (2022), 101–135, [DOI:10.1016/j.matpur.2021.07.009](https://doi.org/10.1016/j.matpur.2021.07.009). Only manuscript pp.1–3 were scoped. The unversioned author PDF's creation metadata is not a certified publication date, and equivalence with the 35-page journal typeset edition was not asserted.

The local working corpus retains the pinned Huang PDF, extracted text, complete source archive and formula/figure renders. The mathematical counterexamples and scope decisions above are persisted in this note. Source downloads and bounded calculations are separate from formal verification.
