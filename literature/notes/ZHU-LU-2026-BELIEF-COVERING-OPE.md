# Zhu–Lu — belief-space covering for offline POMDP evaluation

## Source, edition and actual coverage

- **Paper:** Youheng Zhu and Yiping Lu, *A Covering Framework for Offline POMDPs Learning Using Belief Space Metric*.
- **Selected edition:** [AISTATS 2026, PMLR 300:1423–1431](https://proceedings.mlr.press/v300/zhu26a.html), [official PDF](https://raw.githubusercontent.com/mlresearch/v300/main/assets/zhu26a/zhu26a.pdf). The complete PDF has **31 physical pages**, including appendices, despite the nine-page proceedings range.
- **Companion version:** [arXiv:2603.03191v1](https://arxiv.org/abs/2603.03191v1), submitted March 3, 2026 at 17:48:20 UTC, **29 pages**. The inspected history lists only v1. Its active `sample_paper.tex` has no input/include children. Its abstract, section structure and printed reference list differ from the official edition. The v1 has 37 printed references, the final has 42. It is **not a text-equivalent substitute** for the official proofs. The source archive contains inactive commented material and archived files that were excluded from the active-source inventory.
- **Reading:** Pro-C, November 26, 2026, personally read the complete official extracted text, §§1–6, acknowledgments, all 42 references, the checklist, Appendices A–H, every displayed proof/formula, both figures, the table and three body footnotes. Original PDF pages **4–8, 13–14, 19–21, 23, 29–30** were visually inspected. These cover both diagrams, the table and the principal disputed formulas. The arXiv source/version comparison was scoped and is not a second full reading.
- **Evidence level:** full reading plus bounded independent checks of data interfaces, policy stability, concentration and coverage measures. No formal proof replay, author-code audit or empirical reproduction. No withdrawal or replacement was observed in the primary records inspected. The paper is a theoretical analysis and reports no numerical experiment.
- **Local source:** `literature/corpus/pro_c/zhu26a/paper.pdf`, SHA256 `74227105231fa7007c506acd28af80c3f47233ec19b35683fa10d267289e7149`. Mechanical version inventories and rendered pages are in the ignored corpus directory.

## Main assessment

The useful idea is to **analyze an existing history-based offline policy evaluator through a smaller virtual belief-space abstraction**. An abstraction-bias term, an abstract coverage term and a comparison of the actual versus virtual estimator are kept separate. This can expose structure obscured by counting every observation-action history.

This is not a learned belief-state construction. The learner need not compute the cover in the described estimator, but the guarantee assumes properties of the true belief geometry, target and behavior policies, function classes and latent coverage. Small covering number alone does not imply adequate data coverage.

Several proof interfaces need repair before using the printed rates as established premises. The double-sampling identity fails when two branches share a random reward, and conditional independence given an original belief generally disappears after that belief is coarsened. The policy-averaging comparison omits a policy Lipschitz factor. An optional uniform raw-loss concentration claim of order \(1/n\) fails even for a singleton Bellman-complete class. The coverage improvement has a valid common-pushforward interpretation, but that law must not be silently exchanged for the occupancy law of an arbitrary averaged abstract kernel.

These are local findings with different scope. They do not show that belief covering cannot improve OPE, that the main \(n^{-1/4}\) Hoeffding route is impossible after repair, or that every FDVF conclusion is false. The positive tools and exact limitations are recorded below.

## 1. Model, data and what the algorithm observes

The source uses a finite POMDP with hidden states \(S\), actions \(A\), observations \(O\), bounded reward \(r(s,a)\in[0,R_{\max}]\), and discount \(\gamma<1\). Its finite-horizon FDVF treatment uses horizon \(H\). A belief after the current observation is

\[
b(\tau_h^+)=\Pr(S_h\in\cdot\mid o_1,a_1,\ldots,o_h).
\]

The source keeps distinct copies of the same probability vector when different histories induce it. Belief distance is therefore a pseudometric on these copies. This permits a history-to-belief-copy bijection for notation, but local Lipschitz policy stability forces equal action distributions on copies at distance zero. This is a substantive restriction on history-dependent policies, not merely notation. [§§3–4, pp.3–4.]

The two data objects are:

| Data | Source definition | Supplied information |
|---|---|---|
| \(D_1\) | \(n\) independent behavior trajectories, each randomly truncated to a prefix ending with its next observation | One history, action, realized reward and successor observation per independent prefix |
| \(D_2\) | \(n\) independent complete trajectories of length \(H\) | Histories and future suffixes at every stage of each trajectory |

The learner does not observe the latent states or their true model. The independence unit is a trajectory/prefix. The \(H\) positions of one trajectory cannot be counted as \(H\) independent trajectories. A reward deterministic conditional on latent state need not be deterministic conditional on a nondegenerate belief.

### Extra double-sampling access

Section 5.1 separately assumes paired tuples

\[
(b,a,r,b'_A),\qquad(b,a,r,b'_B),
\]

with the second successor generated independently after resetting to the same belief. Ordinary \(D_1\) does not supply this extra branch. It could be supplied at collection time by an appropriate generator, but remains an additional access assumption.

Resetting a simulator to one fixed hidden state drawn from the belief and then drawing two continuations generally shares that hidden state between branches. It need not produce two independent continuations conditional only on the belief. The required conditional law must be specified at the belief interface. [§5.1, p.6.]

## 2. Abstraction and stability assumptions

An \(\varepsilon\)-cover \(C_\varepsilon\subseteq B\) induces a map \(\phi:B\to C_\varepsilon\) with

\[
\|b-\phi(b)\|_1\le\varepsilon.
\]

For each center \(c\), a fixed distribution \(p_c\) over its fiber defines the averaged reward and transition kernel. The next belief is then pushed into a bin. The abstract policy samples the original policy at the representative, \(\pi_\phi(c)=\pi(c)\), and its lift is \(\pi_\phi\circ\phi\). These are mathematical objects in the analysis, not parameters already recovered from the offline sample. [§4, Appendix B, especially Eq.11.]

**Assumption 1** requires

\[
\|\pi(b_1)-\pi(b_2)\|_1\le L_\pi\|b_1-b_2\|_1.
\]

**Assumption 2 is stronger than Lipschitz continuity of \(V^\pi\) or \(V^*\).** It requires one uniform \(L_V\) for the values, in the true system, of all the specified cover-induced policy lifts:

\[
\sup_{\varepsilon,\phi_\varepsilon}
\operatorname{Lip}\bigl(V_{\rm true}^{[\pi_{\phi_\varepsilon}]_{\rm true}}\bigr)
\le L_V<\infty.
\]

Finite latent state space alone does not imply this uniform condition. The cited Lipschitz property of the optimal value gives useful motivation, but does not prove stability of every quantized policy lift. The source's informal descriptions of “good policies” should not replace these quantifiers. [Assumptions 1–2, Theorem 1, pp.4–5.]

### Positive posterior-distance tool

Lemma 1 states the expected posterior inequality

\[
\mathbb E_{o\sim P(\cdot\mid b_1,a)}
\|b_1^{a,o}-b_2^{a,o}\|_1
\le2\|b_1-b_2\|_1.
\]

This is not a pointwise contraction. The paper's two-state Example 3 has posterior expansion factor \(1/(4\xi)\), arbitrarily large as \(\xi\downarrow0\). For one-hot beliefs the factor 1 follows from the distance being either zero or 2. [p.5, Appendix A, pp.13–14.]

A compact independent formulation also resolves the source's observation/transition-order inconsistency. Let \(K_a(s',o\mid s)\) be the joint next-state/observation kernel under the actual convention, and \(q_i(s',o)=\sum_s b_i(s)K_a(s',o\mid s)\). With observation marginal \(p_i\),

\[
\sum_o p_1(o)\|q_1(\cdot\mid o)-q_2(\cdot\mid o)\|_1
\le\|q_1-q_2\|_1+\|p_1-p_2\|_1
\le2\|b_1-b_2\|_1.
\]

Choose a conditional-probability version when \(p_2(o)=0\). This supports the finite-kernel lemma, without asserting pointwise filtering stability or uniform forgetting.

### Abstraction bias and the radius/diameter convention

Theorem 2 prints

\[
\|V_{\rm true}^{\pi}-[V_{\rm bin}^{\pi_\phi}]_{\rm true}\|_\infty
\le L_\phi^{[1]}\varepsilon,
\]

\[
L_\phi^{[1]}=
\frac{(L_\pi+1)R_{\max}+2L_V}{1-\gamma}
+\frac{\gamma R_{\max}L_\pi+R_{\max}}{(1-\gamma)^2}.
\]

The proof separates true-policy perturbation from lifted-policy versus averaged-model comparison. The former has the familiar \(R_{\max}L_\pi\varepsilon/(1-\gamma)^2\) scale. The latter uses value stability, observation-law distance and the expected posterior bound. This route can support an \(O(\varepsilon)\) bias under its strong assumptions. [Theorems 11–12, Appendix B.]

However, an \(\varepsilon\)-radius cover guarantees only fiber diameter \(2\varepsilon\). Theorem 11 treats two arbitrary members of one fiber as within \(\varepsilon\), while the main meta-theorem explicitly assumes that diameter bound. Use a diameter parameter, or an \(\varepsilon/2\)-radius cover, before reusing printed constants. This is a constant/interface correction, not a change of order.

## 3. The meta-analysis and coverage improvement

The meta-theorem uses three comparisons:

1. The true and abstract evaluation functionals applied to the same learned object.
2. Statistical estimation error within the abstract system.
3. Abstract versus true ground-truth policy values.

It assumes the second term has a finite-class bound involving abstract coverage, a statistical term and \(L_E\varepsilon\). This is a transfer template, not a guarantee for an arbitrary estimator. The main displayed formula and Appendix A omit an \(\varepsilon\) multiplier on \(L_\phi\), and one triangle-expression endpoint is mislabelled. The subsequent concrete bound, Theorem 7, uses the intended \(L_\phi\varepsilon\). [Theorem 3, pp.5–6 and13.]

Lemma 3's infimum over \(\varepsilon\) is justified for **one fixed real estimator/error random variable** and deterministic bound thresholds. A decreasing sequence of numerical thresholds approaching the infimum gives nested events, so an uncountable union bound is unnecessary. This does not justify selecting among different data-adaptive estimators without additional control.

### What Theorems 4–5 compare

These theorems compare abstract coverage with the true-system coverage of the **lifted target policy** \([\pi_e^\phi]_{\rm true}\). Their right side is not automatically the coverage of the original \(\pi_e\). Small policy-value error does not imply close occupancy density ratios. The statement that the two coverages “generally” have the same scaling is not independently established. [§4.2, pp.6,29–30.]

The fundamental positive statement is data processing for a **common pushforward of two probability laws**. Write \(P\) for target occupancy, \(Q\) for behavior occupancy, and \(\psi\) for a fixed coarsening. If \(P\ll Q\), then

\[
\frac{d\psi_\#P}{d\psi_\#Q}(z)
=\mathbb E_Q\!\left[\frac{dP}{dQ}\,\middle|\,\psi=z\right].
\]

Conditional Jensen gives

\[
\mathbb E_{\psi_\#Q}\left[\left(\frac{d\psi_\#P}{d\psi_\#Q}\right)^2\right]
\le\mathbb E_Q\left[\left(\frac{dP}{dQ}\right)^2\right],
\qquad
\left\|\frac{d\psi_\#P}{d\psi_\#Q}\right\|_\infty
\le\left\|\frac{dP}{dQ}\right\|_\infty.
\]

The first quantity is \(1+\chi^2\), rather than \(\chi^2\) itself. That common additive constant does not affect the comparison. Use essential supremum on infinite/countable histories, without assuming a maximizing history exists.

### An exact augmented-process interpretation

At a fixed stage, or with stage included in state, retain the original latent state and project

\[
\psi(s,\tau)=(s,\operatorname{window}_T(\tau)).
\]

For a target policy depending only on the window, this projection is exactly Markov. Its kernel is

\[
K((s',w')\mid(s,w))=
\sum_{a,o'}\pi_\phi(a\mid w)T(s'\mid s,a)O(o'\mid s')
\mathbf1\{w'=\operatorname{shift}(w,a,o')\}.
\]

Old histories in the same \((s,w)\) fiber have the same transition row. Thus any fiber average leaves this kernel unchanged. Choosing \(d^D=\psi_\#Q\) is independent of the target policy, and the two coverage inequalities follow. This is a useful positive interpretation of the claimed “no worse” result.

### Why an arbitrary averaged window model is a different law

Appendix D instead constructs a new latent space of **window strings** and derives its transition from the general averaged \(P_\phi\). Appendix E declares its occupancy to equal the original process's window pushforward automatically. That equality needs an additional argument. Coarsening different original latent states and then running an averaged kernel does not generally preserve multi-step occupancy.

A small law-separation example makes the issue concrete. Use states \(v,w,y\), observations \(x,x,y\), and initial mass \(1/2\) each on \(v,y\). Transitions are

| State | Action \(a\) | Action \(z\) |
|---|---|---|
| \(v\) | \(v\) | \(w\) |
| \(w\) | \(y\) | \(w\) |
| \(y\) | \(y\) | \(y\) |

Take constant uniform action policy and zero rewards. Every complete history ending in the current observation yields a one-hot belief. A one-observation window \(x\) merges the initial \(v\) history and the reachable \((x,z,x)\) history at \(w\). Choose the allowed fiber average \(p_x=\delta_w\), \(p_y=\delta_y\). With the same initial window law, one step gives

\[
\Pr_{\rm true}(x)=\tfrac12,\qquad
\Pr_{P_\phi}(x)=\tfrac14.
\]

Using the proof's prescribed reference law, the true behavior pushforward \((1/2,1/2)\), the abstract law \((1/4,3/4)\) has \(L^2\) ratio \(5/4\) and \(L^\infty\) ratio \(3/2\). The true target equals behavior, with both ratios 1. Constant policy and zero reward make the stability conditions trivial, and a two-observation window already identifies the state.

This example **only disproves the automatic law identity and the proof's particular reference-measure construction under that interpretation**. It does not refute the full existential statement allowing another \(d^D\), the augmented \((s,w)\) argument, or every small-radius approximation guarantee. The ambiguity must be resolved before transferring the comparison to the actual averaged model.

## 4. Double sampling: claimed route and independent checks

The actual objective is

\[
\widehat Q\in\arg\min_{f\in\mathcal F}
\mathbb E_D[(f(b,a)-r-\gamma f(b'_A,\pi))
(f(b,a)-r-\gamma f(b'_B,\pi))].
\]

The virtual abstract objective uses **the same offline data**, replacing arguments by their bins, reward by \(r_\phi\), and policy by \(\pi_\phi\). The source assumes abstract occupancy coverage \(C_\pi(\phi)\), abstract realizability, finite bounded function class and fixed-action belief Lipschitz constant \(L_Q\). The proof uses the bound \(0\le f\le V_{\max}=R_{\max}/(1-\gamma)\). [§5.1, Assumptions 3–5, Appendix C, Definition 4.]

The intended chain is a telescoping value-error bound by the square root of a Bellman residual, uniform empirical concentration, realizability and abstraction comparisons. Theorem 7 then prints an infimum over admissible \(\varepsilon\) of

\[
\frac{\sqrt{C_\pi(\varepsilon)}}{1-\gamma}
\sqrt{\sqrt{\frac{32R_{\max}^4\log(2|\mathcal F|/\delta)}{n(1-\gamma)^4}}
+L_E\varepsilon}
+L_\phi\varepsilon.
\]

With the chosen \(\varepsilon\asymp n^{-1/2}\), its basic sample factor is \(n^{-1/4}\sqrt{C_\pi(\varepsilon_n)}\). Coverage may worsen as the cover is refined, so it is not a free constant. The following checks concern the proof of this route.

### 4.1 Shared realized reward

For two independent complete targets \(Y_A,Y_B\) conditional on \((b,a)\),

\[
\mathbb E[(q-Y_A)(q-Y_B)\mid b,a]
=(q-\mathbb E[Y\mid b,a])^2.
\]

The printed target instead shares \(r\). With \(\gamma=0\), belief \((1/2,1/2)\), latent rewards 0 and1, and \(f=1/2\), its expectation is \(1/4\), while squared Bellman residual with the true conditional mean reward is zero.

Thus the squared-residual identity needs a known conditional-mean reward, or independently sampled \((R_A,b'_A)\) and \((R_B,b'_B)\). The original offline realized reward is not the conditional mean. This counterexample does not show that the extra variance always changes the minimizer. It does invalidate an unqualified unbiasedness/zero-realizable-loss step. [Eq.39 and the realizability use following Eq.51.]

### 4.2 Independence is lost after coarsening

Even with deterministic rewards, conditional independence at \(b\) does not imply independence at \(C=\phi(b)\). Let

\[
m_b=\mathbb E[f(\phi(b'),\pi_\phi)\mid b,a].
\]

If the bin mixing distribution matches the data conditional distribution, the virtual paired product has expectation

\[
\mathbb E_{b\mid C}[(q-r_C-\gamma m_b)^2]
=(q-r_C-\gamma\mathbb E[m_b\mid C])^2
+\gamma^2\operatorname{Var}(m_b\mid C).
\]

Matching the fiber distribution therefore does not remove the variance term. A mismatch between the arbitrary \(p_C\) and data distribution introduces a further interface problem.

For an explicit finite example, use one action, \(\gamma=1/2\), fully observed states \(u,v,x,y\), with \(u\to x\), \(v\to y\), and \(x,y\) absorbing. Rewards are zero except \(r(x)=1\). Merge \(u,v\) into \(C\), with equal mixture, leaving \(x,y\) separate. The exact abstract values are

\[
f(C)=1/2,\qquad f(x)=2,\qquad f(y)=0.
\]

Two successors from the same original state are degenerate independent draws. From \(u\), both are \(x\), and from \(v\), both are \(y\). The product is always \(1/4\), while the abstract Bellman residual at \(C\) is zero.

Consequently **Eq.39 and the abstract-realizable-zero-loss step are false for the printed same-data coupling**. This is a counterexample to an exact identity, not a disproof of a final bound with an additional controlled abstraction term. Possible repairs are independent fiber-member draws for the two virtual branches, a relevant lumpability condition, or explicit retention and bounding of the covariance term. None was completed here as a replacement full theorem.

### 4.3 Policy averaging requires \(L_\pi\)

Lemma 9, Eq.47, and Theorem 14 use only Assumption 5 while bounding a policy-averaged function. Theorem 6 consequently prints \(L_\phi^{[2]}=V_{\max}+L_Q\). Fixed-action Lipschitz continuity does not control changing action probabilities. Under Assumption 1, a conservative bound is instead

\[
|f(b,\pi)-f(\phi(b),\pi_\phi)|
\le(L_Q+V_{\max}L_\pi)\varepsilon.
\]

A smaller constant is possible using total variation and the range of \(f\), but the policy factor cannot simply be deleted.

A fully reachable example uses two states, a uniform initial latent prior, a transition resetting to uniform independently of action, and symmetric observation rows \((1/2-\eta,1/2+\eta)\), \((1/2+\eta,1/2-\eta)\). The only post-observation beliefs are

\[
b=(1/2-\eta,1/2+\eta),\quad c=(1/2+\eta,1/2-\eta),
\quad\|b-c\|_1=4\eta.
\]

Let \(\gamma=0\), \(R_{\max}=1\), \(f(\cdot,a_0)=0\), \(f(\cdot,a_1)=1\), so \(L_Q=0\). The policy chooses \(a_0\) at \(b\) and \(a_1\) at \(c\). Map both beliefs to \(c\) and use \(\pi_\phi(c)=\pi(c)\). Take the singleton class \(\mathcal F=\{f\}\). With \(\eta=0.01\), an \(\varepsilon=0.05\) cover is valid. Initial observations are equiprobable, so the true functional is \(1/2\) and the abstract functional is 1. Theorem 6's printed bound is \(0.05\), not \(1/2\). This policy has a finite, large Lipschitz constant on the two-point belief space. The missing dependence is material. [p.7, pp.21–22, Eqs.47,57–58.]

### 4.4 Concentration: preserve the ordinary rate, reject the stronger raw-mean claim

Lemma 8's proof incorrectly declares the paired sample product nonnegative. With bounded targets it can be negative, but lies in \([-V_{\max}^2,V_{\max}^2]\). A two-sided bounded-range Hoeffding argument still supports a conservative \(n^{-1/2}\) uniform objective deviation of the displayed order. This sign issue alone does not invalidate the later \(n^{-1/4}\) value-error route.

In contrast, Proposition 3 claims a uniform **raw empirical objective** deviation of order

\[
\frac{R_{\max}^2}{n(1-\gamma)^2}\log(|\mathcal F|/\delta)
\]

from Bellman completeness alone. This stronger claim fails even without abstraction or reward ambiguity.

Take two fully observed states, one action, both transition rows uniform, \(r(0)=0\), \(r(1)=1\), and \(\gamma=1/2\). The exact values are \(Q(0)=1/2\), \(Q(1)=3/2\). The singleton \(\mathcal F=\{Q\}\) is exactly Bellman complete. At either current state, each independent target residual is an equiprobable \(\pm1/4\). Its paired product is an equiprobable \(\pm1/16\). For independent samples the empirical objective is

\[
\frac{1}{16n}\sum_{i=1}^n\xi_i,
\qquad \Pr(\xi_i=\pm1)=1/2,
\]

with population objective zero. This has nondegenerate \(n^{-1/2}\) fluctuations. More explicitly, with \(S_n=\sum_i\xi_i\),

\[
\mathbb E S_n^2=n,\quad\mathbb E S_n^4=3n^2-2n,
\quad\Pr(|S_n|\ge\sqrt n/2)\ge3/16.
\]

The last inequality follows from the second-moment bound applied to \(S_n^2\). Any fixed constant times \(1/n\) is smaller than \(1/(32\sqrt n)\) for sufficiently large \(n\), contradicting the displayed high-probability claim, for example at \(\delta=0.1\). A full-support current-state sampling law can be used, so missing coverage is not the cause.

This does not rule out a fast **excess-risk** guarantee under suitable Bernstein structure. Proposition 3 is an optional stronger assertion, and the source explicitly does not use it for its main Hoeffding-based route. [Assumption 8, Remark 7 and Eq.44, p.21.]

## 5. Future-dependent value functions

The second application is finite-horizon off-policy evaluation. A future-dependent value function is a bridge satisfying

\[
\mathbb E_{\pi_b}[V_F(f_h)\mid s_h,\tau_h]
=V_S^{\pi_e}(s_h,\tau_h),
\]

where the argument includes the future suffix and history. Existence of such a bridge in the chosen class is an assumption, not a universal consequence of partial observability. [§5.2, p.7.]

The actual estimator uses the observed complete trajectories:

\[
\widehat V\in\arg\min_{V\in\mathcal V}\max_{\theta\in\Theta}
\sum_{h=1}^H\mathbb E_D
\left[(\mu_h(r_h+V(f_{h+1}))-V(f_h))\theta(\tau_h)
-\tfrac12\theta(\tau_h)^2\right],
\]

\[
\mu_h=\pi_e(a_h\mid\tau_h^+)/\pi_b(a_h\mid\tau_h^+).
\]

It does not require double sampling or explicit true-belief computation. It does require evaluable target and logging propensities. The source says the logging policy is known and chosen by the learner. It does not include an error analysis for estimated unknown propensities.

The future suffix is available offline. It is not a causal online memory representation. The exact finite-class min-max optimizer is assumed available, with no general optimization complexity or neural approximation theorem. [pp.7–9, Appendix D.]

### Full and policy-only analysis pipelines

The full pipeline constructs a virtual short-window POMDP and compares it with the true model. Its assumptions include:

- **Assumption 6:** uniform belief forgetting after a sufficiently long common window.
- **Assumption 7:** both target and behavior policies forget old history, with uniform tolerance \(L_\pi\varepsilon\).
- **Assumption 9:** every function in \(\mathcal V\) uniformly forgets truncated information. The printed Eq.63 truncates **future as well as history**. This is stronger than a condition on only the true value function or only the policy.
- Abstract bridge realizability and Bellman completeness, bounded finite \(\mathcal V,\Theta\), adequate latent residual coverage and finite \(C_\mu=\sup\pi_e/\pi_b\).
- A uniform positive lower bound on the logging action probabilities. The full model-change pipeline additionally assumes uniformly positive observation probabilities.

The window \(T\) is the maximum of the relevant forgetting times. The allowed \(\varepsilon\) depends on \(H\), logging/observation minima and \(L_\pi\). The objective-comparison constant \(L_E\) depends on these support quantities, class bounds and horizon. They cannot be suppressed as universally benign constants. [Assumptions 6–7, Conditions 1–3, pp.8–9, Eq.63 and Appendix D.]

The virtual likelihood ratio \(w_\phi\) compares action-observation tapes and contains observation likelihoods in the full pipeline. It is an analysis device for the virtual objective, **not a weight present in the actual displayed estimator**. The paper neither requires the learner to compute those unknown observation likelihoods for the actual min-max program nor proves that they are learned.

Theorem 10's simpler **policy-only** pipeline keeps the original environment and drops Assumptions 2 and6 and the observation-probability lower bound. It retains policy/function-class forgetting, logging support, realizability, completeness and coverage. Its proof is an analogous-construction argument, not a full new proof written out line by line. Removing environment forgetting is a useful distinction, but does not yield unrestricted history-dependent OPE.

### What the reported statistical quantity covers

The main bound has the structure

\[
L_\phi\varepsilon+
\sqrt H\,\mathcal C_T
\sqrt{\frac{cH C_{\mathcal V}^2C_\mu\log(|\mathcal V||\Theta|/\delta)}{n}
+L_E\varepsilon},
\]

where \(\mathcal C_T\) is a supremum of square-root ratios of target latent/window residual energy to behavior history-residual energy. This coverage quantity is not directly observable from the sample in general. The statistical target is

\[
|J(\pi_e)-\mathbb E_{\pi_b}[\widehat V(f_1)]|.
\]

A final empirical implementation of that population expectation needs its own uniform finite-class concentration term or an independent evaluation sample. The displayed theorem does not separately account for that step. The class bound must apply to a data-selected \(\widehat V\), not just a fixed function.

The theorem still uses \(H\) explicitly. Its illustrative \(n^{-1/4}\) improvement requires logarithmic forgetting and an additional sublinear coverage-growth condition with favorable constants. It is not an unconditional horizon-free or constant-memory guarantee. [Theorems 9–10, Corollary 2, Example 2.]

## 6. Geometry examples, scope and empirical status

Example 1 assumes a bounded \(m\)-dimensional representation of reachable beliefs. A covering bound has the scale

\[
N(\varepsilon)\lesssim(C|S|m/\varepsilon)^m.
\]

The additional assumption \(C_\pi\lesssim N^{1/(2m)}\), combined with \(\varepsilon\asymp n^{-1/2}\), gives the source's illustrative \(n^{-1/8}\) rate. Geometry alone does not supply that coverage-growth condition or a feasible policy realizing uniform bin occupancy. Appendix E's substituted covering-number display has the statistical factor with positive exponent \(m/2\), opposite the dependence obtained from \(1/\varepsilon^m\). The stated rate corresponds to the corrected inverse dependence. [Example 1 and p.29.]

The two-state toy model in Appendix E has action-independent transition matrix

\[
\begin{pmatrix}.9&.1\\.1&.9\end{pmatrix},
\qquad b_t=(.5+.5\cdot.8^t,.5-.5\cdot.8^t).
\]

It correctly illustrates exponentially many action histories but a geometrically convergent belief sequence, with an \(O(\log(1/\varepsilon))\) covering upper bound. Its printed exact covering-number equality is not generally correct. At \(T=1\), \(\varepsilon=1/2\), the two beliefs are distance \(.2\), so one center suffices, while the formula gives2. Retain the qualitative upper-bound illustration, not that equality.

Figure 1 and Figure 2 are analysis diagrams. Table 1 compares theoretical coverage definitions. The checklist marks experimental code, training details, error bars and computational resources not applicable. There is no benchmark result, seed count, training run or author-code experiment to reproduce. Appendix G explicitly leaves stability-regularized training and post-training selection for future algorithm design. Appendix H notes that separated one-hot beliefs can recover exponential complexity and that general POMDP hardness remains.

## 7. Reusable findings and FP boundary

The source offers three useful conditional tools: expected posterior-distance control under a common action/observation experiment, an abstraction/statistical-error comparison template, and the contraction of density-ratio coverage under a common measurable coarsening. Their assumptions and probability laws must travel with them.

The paper does not learn an unknown state alphabet, discover an update program, account for installed bit precision, or provide a streaming finite-memory implementation of the FDVF optimizer. Cover cardinality, a future-history bridge and physical predictive storage are different objects. No FP transfer theorem is proposed here, and no core research files were changed.

The bounded checks above establish explicit failures of selected identities and the optional raw-mean rate. They do not certify the remaining full theorem family. A future use of the double-sampling bound needs a corrected branch/reward law and policy factor. A use of the coverage comparison needs the exact common-pushforward law or an explicit approximation argument. These are source-specific conditions, not a prescribed FP research direction.
