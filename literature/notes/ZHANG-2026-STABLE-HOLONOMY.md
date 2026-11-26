# Zhang et al. 2026: constructing finite control states from stable quotients

## Identity and actual coverage

- **Authors:** Zuyuan Zhang, Yongshan Chen, Mahdi Imani and Tian Lan.
- **Title:** *Minimal Markovization via Stable Quotients in Holonomy-Cover Decision Processes*.
- **Edition read:** [arXiv:2607.27132v1](https://arxiv.org/abs/2607.27132v1), submitted July 29, 2026 at 17:03:35 UTC. [Pinned PDF](https://arxiv.org/pdf/2607.27132v1). [Pinned TeX](https://arxiv.org/src/2607.27132v1).
- **Status:** third-party preprint, 84 actual PDF pages. The inspected primary history lists v1 only. The AAAI 2027 source style does not authenticate acceptance. No separate reviewed edition was authenticated.
- **Reader and date:** Pro-C, November 26, 2026, Shanghai.
- **Full reading:** title material, abstract, main Sections 1–8, Appendices A–I, all active mathematical statements and proofs, Algorithms 1–2, six numbered figures, seven numbered tables and all 44 bibliography entries. The main reader covered the complete active TeX include tree and bibliography. No active body footnotes were found.
- **Visual coverage:** original PDF pp.1, 3–7, 11, 19, 21–23 and 83–84. These cover the central definitions and theorem statements, all six figures, all seven tables and both algorithms. The two composite main figures use four assets and the four appendix figures use another four.
- **Bounded support:** one reader checked the quotient construction, directed transports and finite belief consequences. Another checked the diagnostic, calibration and reinforcement learning interfaces, then the conditional probe and clustering deductions below. The main reader assessed those contributions against the primary text. This is not independent certification of every source proof.
- **Not done:** no experimental replication, executable implementation inspection, formal proof replay or full reading of the cited historical dependencies. The inspected arXiv bundle supplies TeX and figure assets, not the experimental implementation.

## Assessment

The useful mechanism is explicit. Begin with distinctions in immediate reward, propagate them backward through every feasible successor, stop at a finite stable partition, and compile the resulting classes into deterministic edge-update tables. The construction turns a family of future response distinctions into a recursively maintainable state. It is particularly transparent because the visible process is Markov and each observed edge transports the hidden mode by a permutation.

The paper also gives a conditional acquisition route. Repeatable diagnostics classify hidden checkpoints in fixed local coordinates. Paired source and successor diagnostics recover class-update rows. Correct initialization plus those rows makes the learned state exactly compatible with finite-MDP learning. The required access is substantial and stated explicitly: restoring the same hidden checkpoint, separated fingerprints, calibrated prototypes and edge–class coverage.

Several constructive consequences can be made more explicit than in the source:

1. Every quotient edge is surjective. Inside a strongly connected component it is therefore bijective, so a common coordinate system and permutation updates can be constructed without physical reverse edges.
2. For a fixed known initial prior, even an unknown true class has an exact finite reachable belief controller. A finite-map enumeration avoids equality tests on arbitrary real belief vectors.
3. Finite distinguishing witnesses can be compiled into executable random-environment probes. An exhaustive finite probe dictionary avoids presupposing the unknown quotient.
4. With a known witness-depth bound, a separation bound and checkpoints covering every class, those probes can construct the prototype labels by clustering. The resulting costs expose both path enumeration and rare-path dependence.

These are source-grounded conditional deductions, not claims that the paper already proves passive autonomous state discovery, and not proposals to alter FP. The principal distinctions are summarized below.

| Object | What is constructed or proved | Required information |
|---|---|---|
| Stable quotient | Coarsest exact observation-wise partition of raw hidden layers | Known reward table, feasible edges and hidden permutations |
| Exact class tracker | Finite deterministic recursion with alphabet size \(\max_o|\mathcal C_o|\) | Correct current class and exact edge tables |
| Quotient belief | Exact posterior pushforward and conditional-mean control state | Known prior and model, rewards excluded from online information |
| Diagnostic recovery | Exponential classification bound and eventual row recovery | Restorable checkpoints, fixed calibrated prototypes, separation and coverage |
| Calibrate then restart | Transfer of a finite-MDP backbone guarantee | Successful finite calibration, fresh algorithmic state and the original backbone assumptions |
| Passive A-HMRL | A representation-learning template | Its theorem assumes eventual exact labels. It does not establish their acquisition |
| Conditional extensions here | Finite belief enumeration and probe-based prototype construction | Additional assumptions and explicit costs in Sections 5 and 8–10 |

## 1. Model and information interface

### 1.1 A special partially observed process

Definition 3.1 uses finite observations \(\mathcal O\), finite actions \(\mathcal A\), a hidden layer set \([n]\), discount \(\gamma\in(0,1)\), and state

\[
s=(o,i)\in\mathcal O\times[n].
\]

Only \(o\) is observed. For a feasible visible edge \(e=(o,a,o')\),

\[
P_H((o',i')\mid(o,i),a)
=P_O(o'\mid o,a)\mathbf1\{i'=\sigma_e(i)\},
\qquad \sigma_e\in S_n.
\]

Thus the next visible observation has a law independent of the current hidden layer, and the hidden update is deterministic once the visible edge is known. Mean rewards \(R(o,i,a)\) may depend on the hidden layer. Statistical statements use bounded means and conditionally centered sub-Gaussian reward noise,

\[
Y_t=R(o_t,i_t,a_t)+\xi_t,\qquad
|R|\le r_{\max},\qquad
\mathbb E[e^{\eta\xi_t}\mid\mathcal G_t^-]
\le e^{\eta^2\sigma_Y^2/2}.
\]

Here \(\mathcal G_t^-\) includes the latent past and the selected action, before the current reward and transition are sampled.

For an executable path \(\omega=e_1\cdots e_k\), chronological execution gives

\[
\sigma_\omega=\sigma_{e_k}\circ\cdots\circ\sigma_{e_1}.
\]

Its visible probability from any initial layer is the same positive product of the \(P_O\) edge probabilities. Conditional on observing that path, the hidden endpoint is uniquely \(\sigma_\omega(i)\). This is Lemma 3.3's path-lifting property.

### 1.2 Rewards are learning signals, not automatically controller observations

The main controller history is

\[
H_t=(o_0,a_0,o_1,\ldots,a_{t-1},o_t).
\]

It excludes realized rewards. A finite-memory controller uses a deterministic update \(U(m,o,a,o')\), an observation-based initialization, and a possibly randomized action readout \(\pi(a\mid o,m)\). The paper does not establish the same memory lower bounds for every possible stochastic memory-update architecture.

Appendix B explicitly separates two reward interfaces. Equal conditional reward means suffice for expected-return evaluation if reward samples are not subsequent observations. If reward samples are used to infer hidden state, an exact abstraction must preserve the relevant joint conditional output law of reward, next observation and next class. Mean equality alone is insufficient.

Likewise, the analyst's augmented Markov process \((s_t,m_t)\) evaluates a fixed implementable controller. Optimizing as if the controller observed \(s_t\) would change the information available to it. For stochastic emissions, the corresponding analytical augmentation includes \((s_t,o_t,m_t)\).

## 2. Stable refinement is a constructive state compiler

### 2.1 Reward signatures and successor closure

For each observation \(o\), let \(\Pi_o\) partition \([n]\). Write \(\Pi\preceq\Pi'\) when \(\Pi\) is finer. The operator \(\mathcal T\) identifies \(i,j\) at \(o\) exactly when

\[
R(o,i,a)=R(o,j,a)\quad\text{for every }a
\]

and

\[
\sigma_{o,a,o'}(i)\equiv^{\Pi}_{o'}
\sigma_{o,a,o'}(j)
\quad\text{for every feasible }(a,o').
\]

Initialize \(\Pi^{(0)}\) by equal immediate reward vectors and iterate

\[
\Pi^{(t+1)}=\mathcal T(\Pi^{(t)}).
\]

An implementation assigns local labels to the signatures

\[
\left(
(R(o,i,a))_a,\,
\bigl(\ell_{o'}^{(t)}(\sigma_{o,a,o'}(i))\bigr)_{(a,o')\text{ feasible}}
\right).
\]

Only the support of \(P_O\) is needed for this refinement. Numerical probabilities become necessary for planning and diagnostic cost, not for deciding equality of successor signatures.

Lemma 3.5 proves monotonicity of \(\mathcal T\) and refinement of this initialized sequence. Each strict refinement increases the total number of blocks, giving

\[
L_\star\le |\mathcal O|n-\sum_o|\Pi_o^{(0)}|
\le|\mathcal O|(n-1).
\]

The first, sharper count is already present in the appendix proof. The resulting fixed point \(\Pi^\star\) is the coarsest stable family.

This is a finite known-model algorithm. It relies on exact reward comparisons. It is not a finite-sample procedure for determining exact equality of arbitrary unknown noisy means.

### 2.2 Exactness and coarseness

An exact class abstraction consists of surjections \(q_o\) such that rewards factor through \(q_o\) and every feasible edge satisfies

\[
q_{o'}\circ\sigma_e=\widehat\tau_e\circ q_o.
\]

Proposition 3.7 gives the exact criterion

\[
\Pi\preceq\mathcal T(\Pi).
\]

Equality is sufficient but not necessary. An exact partition may preserve unnecessary distinctions, so calling every exact partition a fixed point would be incorrect.

For any exact abstraction \(q\), its kernel partition refines the initial reward partition. Monotonicity then shows that it refines every subsequent iterate. Consequently it refines \(\Pi^\star\), and Theorem 3.8 gives a unique surjection

\[
\kappa_o:\widehat{\mathcal C}_o\to\mathcal C_o,
\qquad q_o^\star=\kappa_o\circ q_o.
\]

This universal property explains the precise sense in which the quotient is minimal: no exact observation-wise abstraction of all raw layers can merge two distinct stable classes.

### 2.3 Compile the stable labels into an exact finite MDP

Let \(\mathcal C_o=[n]/\Pi_o^\star\). Stability makes the definitions

\[
\bar R(o,[i]_o,a)=R(o,i,a),
\qquad
\tau_e([i]_o)=[\sigma_e(i)]_{o'}
\]

independent of the representative. On the tagged state space

\[
\bar{\mathcal S}=\bigsqcup_o\{o\}\times\mathcal C_o,
\]

the exact kernel is

\[
\bar P((o',c')\mid(o,c),a)
=P_O(o'\mid o,a)\mathbf1\{c'=\tau_e(c)\}.
\]

Theorem 3.9 intertwines the original and quotient Bellman operators. It preserves values of lifted quotient policies and gives

\[
V_{\mathrm{full}}^\star(o,i)=\bar V^\star(o,[i]_o).
\]

The left side is the **fully observed latent optimum**. The theorem does not make the current stable class observable. Implementing that optimum still requires knowing, diagnosing or otherwise maintaining the class.

## 3. A finite future-response code and its recursive update

Lemma 4.3 turns every split into a bounded witness. If two stable classes differ, there are a feasible path \(\omega\) of length at most \(L_\star\) and a terminal action \(b\) for which

\[
R(\operatorname{tgt}\omega,\sigma_\omega(i),b)
\ne R(\operatorname{tgt}\omega,\sigma_\omega(j),b).
\]

The proof is constructive. An immediate reward split has an empty-path witness. A successor split prepends the responsible edge to a witness from the previous refinement level. An implementation can retain this backpointer when it creates a split.

**Direct deduction.** Collect all such finite response coordinates into

\[
F_o(i)=
\left(
R(\operatorname{tgt}\omega,\sigma_\omega(i),b)
\right)_{\omega\text{ from }o,\ |\omega|\le L_\star,\ b\in\mathcal A}.
\]

Stable equivalence implies equality of every coordinate by repeated edge closure. Conversely, the finite witness lemma distinguishes every pair of different stable classes. Hence

\[
F_o(i)=F_o(j)\iff[i]_o=[j]_o.
\]

It follows that

\[
U_e(F_o(i)):=F_{o'}(\sigma_e(i))
\]

is well defined. The finite response code is therefore recursively updateable.

This gives a concrete sufficient condition for predictive coordinates to define a state: they exactly distinguish a continuation-closed equivalence. An arbitrary finite collection of useful predictions need not have this property.

If the known quotient has \(k_o\) classes, at most \(k_o-1\) witness coordinates are enough to separate them. Start with no coordinates. Whenever two classes still have the same current code, add one witness separating them. Each addition increases the number of code blocks, so at most \(k_o-1\) additions are needed. Selecting these short dictionaries presupposes access to the known model or the separating witnesses. Section 9 gives a larger dictionary that avoids this circularity.

## 4. Directed transport, local coordinates and strongly connected components

### 4.1 What the source proves

Every path descends to a quotient map

\[
\tau_\omega([i]_o)=[\sigma_\omega(i)]_{o'}.
\]

For a closed directed walk based at \(o\), Lemma 3.10 proves that \(\tau_\omega\) is a permutation of \(\mathcal C_o\). The set of such closed-walk maps is a finite group. It contains inverses because a finite permutation's inverse is a nonnegative power of that permutation, realized by repeating the same executable closed walk.

Physical reverse edges are not needed for this directed group. The separate fundamental-group interpretation in Appendix D assumes paired reverse edges with \(\sigma_{\bar e}=\sigma_e^{-1}\). Only then do topological cancellation and the stated fundamental-group representation follow.

The algorithm may use arbitrary fixed class names separately at each observation. If \(\lambda_o:\widehat{\mathcal C}_o\to\mathcal C_o\) is the unknown local relabeling, the corresponding update is

\[
\tau_e^\lambda=\lambda_{o'}^{-1}\tau_e\lambda_o.
\]

No global agreement among numerical label names is required. The proof-level \(\lambda_o\) need not be known by the learner.

### 4.2 Constructive consequence: permutation updates within each SCC

**Independent deduction from the source's commuting relation.**

For every feasible edge,

\[
\tau_e q_o^\star=q_{o'}^\star\sigma_e.
\]

The right side is surjective. Therefore \(\tau_e\) is surjective, giving

\[
|\mathcal C_o|\ge|\mathcal C_{o'}|.
\]

Within a strongly connected component, paths in both directions force equal class counts. Every internal edge is then a bijection.

Choose a root \(r\) in such a component and a directed spanning tree from \(r\). Let \(g_o:\mathcal C_r\to\mathcal C_o\) be transport along its unique root path. All \(g_o\) are bijective. The edge update in common root coordinates is

\[
\widetilde\tau_e=g_{o'}^{-1}\tau_e g_o.
\]

It is a permutation, and every chosen tree edge becomes the identity. Other edges preserve the ordered residual transport. Computing \(g_o^{-1}\) is a coordinate operation, not an assertion that the environment permits that physical reverse path.

Across the condensation DAG, quotient maps remain surjective and can merge distinctions. A distinction actually merged by one map cannot reappear under subsequent deterministic quotient maps. Thus the dynamics decompose into permutation transport inside SCCs and possibly merging transport between them.

The paper's optional tree-gauge construction assumes a bijective scaffold. The SCC observation supplies that condition automatically within each component. It is an explicit consequence here, without a novelty claim.

## 5. Known-class tracking and unknown-prior control are different problems

### 5.1 The source's exact tracking bound

Correctly initialized class memory obeys

\[
c_{t+1}=\tau_{o_t,a_t,o_{t+1}}(c_t).
\]

Corollary 3.12 proves

\[
|\mathcal M|_{\min}=\max_o|\mathcal C_o|
\]

among alphabets admitting injective encodings of each local class and the compatible deterministic update. The same symbol can be reused at different observations because \(o\) is supplied to the controller.

Corollary 6.6 gives a lower bound for arbitrary controllers under additional reachability and pairwise decision-separation conditions at the observation in question, together with exact optimality after every relevant history. The known-class tracking statement alone is not a universal minimum for fixed-prior, approximate or policy-specific control.

### 5.2 The source's belief recursion

For an unknown class and the reward-blind history convention, Proposition 3.11 gives

\[
\beta_t(c)=\Pr(c_t=c\mid H_t),
\qquad
\beta_{t+1}=(\tau_e)_\#\beta_t.
\]

The action is generated from the visible history, and the next visible observation has a class-independent likelihood. Neither adds a hidden-class likelihood correction. Multiple source masses are added when an open-edge map merges classes.

The conditional reward is

\[
R_B(o,\beta,a)=\sum_c\beta(c)\bar R(o,c,a).
\]

The source notes that the ambient simplex is continuous while a fixed finite HCDP can have only a finite reachable belief orbit. The following construction makes the latter statement explicit.

### 5.3 Construct an exact finite belief controller

**Independent deduction.** Fix an initial observation \(o_0\) and its known conditional raw prior \(p_0\). Visible histories do not update the probabilities of initial hidden layers through a likelihood term. Thus

\[
p_t=(\sigma_\omega)_\#p_0,
\qquad
\beta_t=(\tau_\omega)_\#\beta_0,
\qquad
\beta_0=(q_{o_0}^\star)_\#p_0.
\]

The raw posterior belongs to a finite permutation orbit, of size at most

\[
\frac{n!}{|\operatorname{Stab}_{S_n}(p_0)|}.
\]

If equal prior probabilities have multiplicities \(m_1,\ldots,m_r\), this upper bound is \(n!/\prod_jm_j!\).

There is also a purely discrete enumeration. Store

\[
(o,\theta),\qquad
\theta:\mathcal C_{o_0}\to\mathcal C_o,
\]

starting with the identity at \(o_0\), and use breadth-first enumeration under

\[
\theta'=\tau_e\circ\theta.
\]

Every reachable \(\theta\) is surjective. With \(k_0=|\mathcal C_{o_0}|\) and \(k_o=|\mathcal C_o|\), there are at most

\[
k_o!\left\{\begin{matrix}k_0\\k_o\end{matrix}\right\}
\]

such maps at \(o\), where braces denote Stirling numbers of the second kind. The interpretation is \(\beta=\theta_\#\beta_0\). This implementation need not decide equality of arbitrary real vectors. Equal beliefs can optionally be merged.

On the finite reachable beliefs, define

\[
P_B((o',\beta')\mid(o,\beta),a)
=P_O(o'\mid o,a)\mathbf1\{\beta'=(\tau_e)_\#\beta\}.
\]

Together with \(R_B\), this is an exact finite information-state MDP. Solving it gives an optimal controller under the original reward-blind observable-history information constraint. It does not grant access to the true class and need not attain the fully observed latent optimum.

At each reachable observation,

\[
|\mathcal B_o|
\le
\min\left\{
\frac{n!}{|\operatorname{Stab}_{S_n}(p_0)|},
\,
k_o!\left\{\begin{matrix}k_0\\k_o\end{matrix}\right\}
\right\}.
\]

This is a sufficient construction, not a proof that distinct beliefs cannot be further compressed for a particular control objective. For several possible initial observations, take the corresponding finite union with its initial information.

These are cardinality bounds for the changing information state. They do not charge the description precision of the supplied prior, model probabilities or value table, and are not finite-bit implementation bounds for arbitrary real inputs.

### 5.4 Exact count inside the initial SCC

Let \(H=\operatorname{Hol}_{o_0}^{\mathrm{dir}}\) and choose a reference path \(\gamma:o_0\to o\) within that SCC. The set of all feasible path transports from \(o_0\) to \(o\) is

\[
\{\tau_\omega:\omega:o_0\to o\}=\tau_\gamma H.
\]

For one inclusion, choose any return path \(\delta:o\to o_0\). Then

\[
\tau_\gamma^{-1}\tau_\omega
=(\tau_\delta\tau_\gamma)^{-1}
(\tau_\delta\tau_\omega)\in H.
\]

The reverse inclusion follows by first executing a closed walk and then \(\gamma\). Therefore

\[
|\mathcal B_o|
=\frac{|H|}{|\operatorname{Stab}_H(\beta_0)|}.
\]

This count permits all executable action paths. A restricted behavior policy may visit fewer.

For a uniform raw prior, every raw posterior stays uniform and

\[
\beta_t(c)=|c|/n.
\]

It depends only on the observation. Thus one additional memory symbol can suffice under this information constraint even when the known-class tracker needs several. This illustrates why the two minimality questions must remain separate.

## 6. What diagnostic learning actually receives

Definition 4.4 and Appendix C provide bounded-horizon protocols with class-stable means and separated fingerprints

\[
\phi_o(c)=
\bigl(\bar G(o,c,u_\ell)\bigr)_{\ell=1}^{d_o},
\qquad
\|\phi_o(c)-\phi_o(c')\|_2\ge\Delta>0.
\]

The interface can restore the **same hidden checkpoint**, without exposing its hidden index, and obtain conditionally independent repetitions with sub-Gaussian proxy \(\nu^2\). This is stronger than resetting to a fixed initial distribution.

It also supplies local label sets with unknown fixed bijections \(\lambda_o\) and prototypes satisfying

\[
\|\widetilde\phi_o(\hat c)-\phi_o(\lambda_o(\hat c))\|_2
\le\Delta/8.
\]

The source is explicit that this is calibrated classification. The prototype assumption already includes the correct number of local classes and a representative prototype for each one.

With \(m\) repetitions **per coordinate**, nearest-prototype classification obeys Theorem 4.6:

\[
\Pr(\text{error}\mid(o,i))
\le2d_o\exp\left(-\frac{m\Delta^2}{128\nu^2d_o}\right).
\]

Coordinatewise error below \(\Delta/(8\sqrt{d_o})\) gives Euclidean error below \(\Delta/8\). The correct prototype is then within \(\Delta/4\), while any competing prototype is more than \(3\Delta/4\) away. A coordinate union bound supplies the displayed probability. Coordinates need not be independent of one another.

For at most \(K\) classifications and \(d=\max_od_o\), one can use

\[
m\ge\frac{128\nu^2d}{\Delta^2}
\log\frac{2dK}{\delta}.
\]

For an indefinitely repeated protocol, summable failure budgets or the source's \(m_{o,k}=O(\log k)\) schedule give only finitely many classification errors almost surely. This does not provide an observable time at which the last error has occurred.

### Recovering the update table

An anchored sample retains an exact source checkpoint, executes an edge, and retains the actual paired target checkpoint. Both are diagnosed. For each edge \(e\), the learner counts local source–target pairs and selects the most frequent target in each source row.

Open-edge transports need not be injective. Row-wise estimation correctly allows several source classes to have one target. A global permutation-matching estimator would impose an unnecessary and sometimes false constraint.

Theorem 4.9 assumes infinitely many anchored samples for every relevant edge–true-class row, together with only finitely many classification errors. Correct counts then grow without bound, while incorrect counts stop growing. Every row eventually stabilizes to \(\tau_e^\lambda\).

Correct table recovery does not automatically repair a currently wrong propagated label. Proposition 4.12 additionally uses later diagnostic initializations at unbounded exogenous initialization times. A correct initialization after all required rows stabilize gives exact tracking on that interval and subsequent correctly initialized intervals.

## 7. Calibration, restart and a valid RL interface

Algorithm 1 first calibrates all required transport rows, freezes the maps, and reinitializes the RL backbone, including parameters, replay data, counters and optimizer state. It then diagnoses each initial checkpoint and propagates local labels by the frozen maps. Diagnostics after calibration can check consistency without overwriting the frozen online state or table.

Theorem 5.2 works at each deterministic time on the event that the current label and every possible outgoing row for the selected action are correct. On this pre-transition event, the learned state has the quotient transition law, conditional reward mean and conditional sub-Gaussian noise. Correctness only along the single realized successor is weaker than correctness of that whole conditional kernel.

An almost surely finite eventual synchronization time gives the source's ambient-filtration conclusion. Passing to a fresh learned-information MDP process requires the stated stopping-time condition or an independently valid robust-prefix argument. The state distribution at synchronization need not equal the original initial distribution.

Corollary 5.4 retains the backbone theorem's own exploration, step-size, sampling, optimization and approximation assumptions. Restarting means clearing all state affected by earlier mislabeled samples, not merely resetting the episode observation.

For the finite calibration statement, a careful probability argument can couple the real run to an ideal run using the true local classes. They coincide until a calibration or classification error. Union-bound the probability of such errors and the ideal backbone's failure event. Conditioning on a future event that every classification succeeds should not silently be used to assert that the original transition/noise law is unchanged.

The passive Algorithm 2 instead proposes history labels, predicts reward and transitions, applies split/merge routines, and penalizes representation complexity. Its exactness theorem assumes eventual correct labels in fixed gauges with the appropriate stopping-time condition. It does not prove that its general loss or refinement heuristic acquires those labels.

Theorem 4.2's passive nonidentifiability example uses a behavior policy that never selects the distinguishing action. It rules out uniform recovery over unrestricted models and behaviors. It does not rule out recovery with suitable exploration, coverage or additional structure.

## 8. Construct executable diagnostic probes from finite witnesses

**Independent conditional construction based on Lemmas 3.3 and 4.3.**

Fix a candidate path

\[
\omega=(o,a_0,o_1,\ldots,a_{k-1},o_k)
\]

and terminal action \(b\). Restore a checkpoint at \(o\), execute the prescribed actions, and stop with output zero at the first observation mismatch. If the whole path matches, execute \(b\) and return its reward \(Y_b\). The observation after \(b\) is not part of the gate.

Let \(I_\omega\) indicate a complete match and define \(W_{\omega,b}=I_\omega Y_b\). The gate is determined before the terminal reward is sampled. For a feasible path,

\[
q_\omega=\prod_{j=0}^{k-1}P_O(o_{j+1}\mid o_j,a_j)>0,
\]

\[
\mathbb E[W_{\omega,b}\mid(o,i)]
=q_\omega R(o_k,\sigma_\omega(i),b).
\]

The multiplier \(q_\omega\) is independent of the hidden layer. Therefore class stability and any nonzero witness difference are preserved. A path that is infeasible simply yields a zero coordinate, so executing the protocol does not require knowing support in advance.

### Noise bound

For a fixed checkpoint, put \(r_i=R(o_k,\sigma_\omega(i),b)\). On a successful path it is fixed. With \(q=q_\omega\),

\[
W-qr_i=r_i(I_\omega-q)+I_\omega\xi.
\]

Conditional on pre-reward information, the second term has the source's exponential-moment bound. Integrating first over the reward noise and then over the path gives

\[
\mathbb E[e^{\eta(W-qr_i)}\mid(o,i)]
\le e^{\eta^2\sigma_Y^2/2}
\mathbb E[e^{\eta r_i(I_\omega-q)}\mid(o,i)].
\]

The latter centered variable has range length \(|r_i|\le r_{\max}\). Hoeffding's lemma yields the valid common proxy

\[
\nu^2=\sigma_Y^2+r_{\max}^2/4.
\]

Unconditional independence of the path and reward noise is unnecessary. Conditional fresh randomness across restored repetitions remains necessary for the sample concentration argument.

### Separation and duration

Suppose \(L\ge L_\star\), every feasible edge probability is at least \(p_{\min}>0\), and every required nonzero witness reward difference is at least \(\eta_{\min}>0\). Then some witness coordinate for each class pair has difference at least

\[
\Delta_0=p_{\min}^{L}\eta_{\min}.
\]

Each probe uses at most \(L+1\) environment actions. The implied classification sample budget can depend on \(p_{\min}^{-2L}\). Thus a finite witness produces an actual diagnostic protocol, while retaining the cost of rare successful paths.

The execution itself does not require \(p_{\min}\) or \(\eta_{\min}\). They provide an a priori valid precision budget. A supplied fingerprint separation bound \(\Delta_0\) can replace them.

## 9. Construct prototypes without already knowing the quotient

The short witness dictionary in Section 3 uses the known model. A more expensive dictionary removes that dependency.

### 9.1 All bounded strings

Assume the finite alphabets are known and a valid integer \(L\ge L_\star\) is known. A hidden-layer upper bound \(n_{\max}\) suffices through

\[
L=|\mathcal O|(n_{\max}-1).
\]

At each starting observation, enumerate all action–observation strings of lengths \(0,\ldots,L\), followed by every terminal action. Writing \(A=|\mathcal A|\) and \(O=|\mathcal O|\), there are

\[
D=A\sum_{k=0}^{L}(AO)^k
\]

coordinates. Execute the gated probes above. This dictionary does not use the unknown hidden permutations, stable classes, their number, the numerical kernel or its support. Infeasible strings are harmless zero coordinates. A separating witness for each true class pair is included.

An empirical partition that stops changing at one finite depth does not by itself certify an unknown depth bound. The supplied \(L\) remains a substantive assumption.

### 9.2 Cluster unlabeled checkpoints

Suppose \(M\) restorable checkpoints have been collected, with known observations, and they cover every stable class in every observation fiber being reconstructed. Assume a valid known separation lower bound \(\Delta_0>0\) for the dictionary.

Estimate each checkpoint fingerprint to Euclidean error at most \(\Delta_0/8\). Cluster separately within each observation. Two estimates from one class are at distance at most \(\Delta_0/4\), while estimates from different classes are at least \(3\Delta_0/4\) apart.

Connect pairs whose distance is below \(\Delta_0/2\). On the simultaneous accuracy event, the graph is exactly a disjoint union of class cliques. Its connected components give arbitrary fixed local class names. Choose one estimated fingerprint per component as its prototype. It satisfies the source's prototype calibration condition.

This constructs both class count and prototypes from unlabeled checkpoints under the extra assumptions. It does not infer that all classes have been seen merely because no new component has recently appeared. With incomplete coverage, it correctly clusters only the represented classes.

### 9.3 Explicit probe and action budgets

With \(m\) fresh restored repetitions per coordinate and checkpoint, a sufficient condition is

\[
m\ge
\frac{128\nu^2D}{\Delta_0^2}
\log\frac{2DM}{\delta_{\mathrm{proto}}}.
\]

Then all \(M\) fingerprint estimates meet the required accuracy with probability at least \(1-\delta_{\mathrm{proto}}\). The number of scalar probe repetitions is \(MDm\), not \(Mm\).

Let

\[
H_{\mathrm{sum}}
=A\sum_{k=0}^{L}(k+1)(AO)^k
\le(L+1)D.
\]

The raw environment-action count is at most

\[
MmH_{\mathrm{sum}}\le MDm(L+1).
\]

Thus a conservative bound scales as

\[
O\left(
\frac{M\nu^2D^2(L+1)}{\Delta_0^2}
\log\frac{DM}{\delta_{\mathrm{proto}}}
\right).
\]

With \(\Delta_0=p_{\min}^{L}\eta_{\min}\), this displays both the dictionary growth and the \(p_{\min}^{-2L}\) factor.

These counts exclude acquisition of covering checkpoints, their storage and copying, restoration cost, edge anchoring, and backbone learning. There are \(MDm\) restored repetitions. Returning to the original state for subsequent control can require a final additional restoration. The several-bit online class label does not account for the simulator or environment state needed by this interface.

For a finite plan of \(K\) later classifications, a simultaneous budget over \(M+K\) fingerprint estimates gives

\[
m\ge
\frac{128\nu^2D}{\Delta_0^2}
\log\frac{2D(M+K)}{\delta}.
\]

On that common event, clustering and every later nearest-prototype classification are correct. This avoids treating a data-dependent prototype-success event as if it were independent of later data. New diagnostic calls must still have the required conditional fresh-noise guarantee. Unknown call counts can use summable per-call confidence budgets.

## 10. A finite row-coverage budget under extra access

**Independent conditional completion of the acquisition route.**

Assume a restorable representative of every local class, fresh transition draws after restoration, and a known lower bound \(p_{\min}\) on each positive \(P_O(o'\mid o,a)\). Let

\[
R_{\mathrm{rows}}=\sum_{e\in E}|\mathcal C_{\operatorname{src}(e)}|.
\]

Use a known upper bound \(\overline R\ge R_{\mathrm{rows}}\), for example \(AO\sum_o|\mathcal C_o|\) after complete class recovery. For each \((o,c,a)\), repeat restore-and-execute at least

\[
N_{\mathrm{edge}}
=\left\lceil p_{\min}^{-1}
\log\frac{\overline R}{\delta_{\mathrm{cov}}}\right\rceil
\]

times. A given feasible target edge is missed with probability at most \(e^{-p_{\min}N_{\mathrm{edge}}}\). A union bound gives complete edge–class coverage with probability at least \(1-\delta_{\mathrm{cov}}\).

Preserve a target checkpoint from the first observed occurrence of each row and diagnose it. The source representative already has its fixed class name on the prototype-success event. Correct target classification then recovers that deterministic row from one anchored pair.

The action count for coverage itself is

\[
A\sum_o|\mathcal C_o|\,N_{\mathrm{edge}},
\]

plus checkpoint restores and the target-probe costs. If source labels are re-diagnosed, count those calls too. Subsequent episode initializations also need confidence allocation.

This gives a complete conditional sequence:

1. Acquire covering checkpoints through an additional access mechanism.
2. Estimate the finite dictionary and cluster local classes.
3. Cover outgoing edges from each representative and classify paired targets.
4. Freeze the local update tables.
5. Diagnose initialization and run a restarted finite-MDP learner with its original assumptions.

The first step remains supplied unless a separate acquisition guarantee is given. The paper does not prove this expanded procedure, its general efficiency, or its applicability to arbitrary POMDPs. The construction is useful precisely because every extra input and expensive operation is visible.

## 11. Ordered memory and the limited scope of the barrier

Section 6 considers a chosen executable loop alphabet, with a free-group action \(\rho_o\) on quotient classes. A memory surrogate that factors through abelianization retains signed counts of the chosen loop generators.

If two loop words have equal counts but send a known reachable class to states with disjoint optimal-action sets, they induce the same memory and action distribution. At least one then loses

\[
\varepsilon_{\mathrm{dec}}(c,c')
=\min_{p\in\Delta(\mathcal A)}
\max\left\{
\bar V^\star(o,c)-\sum_a p(a)\bar Q^\star(o,c,a),\,
\bar V^\star(o,c')-\sum_a p(a)\bar Q^\star(o,c',a)
\right\}>0.
\]

Positivity follows from compactness and disjoint optimal-action supports. The theorem concerns conditional continuation values at those histories, not an unconditional loss without weighting their occurrence.

The three-layer example uses one observation,

\[
\alpha=(12),\qquad\beta=(123),
\]

and action-reward vectors \((1,0),(0,1),(0,0)\). The stable classes are singletons and their loop group is \(S_3\). The commutator \(\alpha\beta\alpha^{-1}\beta^{-1}=(123)\) sends class 1 to class 2. Its chronological implementation is \(b,b,a,b,a\). For \(0<\gamma<1/2\), the optimal actions at classes 1 and 2 are respectively \(a\) and \(b\).

This is a barrier for count-based loop representations. It is not a lower bound for general order-sensitive RNNs, attention or linear recurrences. Also, signed counts in an abstract loop alphabet must not be confused with counts of primitive actions after an inverse loop has been implemented by positive repetitions.

The constructive counterpart is Proposition 6.8: storing the current class and applying edge maps in order preserves every nontrivial group action on that class. It need not store the complete word or the complete group element.

## 12. What the experiments establish

The experiments instantiate controlled HCDPs and use simulator-provided diagnostic access. They check the consequences of that model rather than establishing the assumptions in general environments.

### 12.1 ChainCover: distinctions propagate backward

The depth-\(D\) chain has three reward-relevant classes and \(b\) nuisance modes, with distinctions revealed at a terminal query. Its state counts are

\[
3b(D+3)\quad\text{raw},\qquad 3(D+2)+1\quad\text{quotient}.
\]

For \(D=6,b=8\), Table 3 reports 216 raw states, 25 quotient states, stabilization at round 7, zero reward and successor inconsistency, and zero reported optimal-value difference. Figure 3 shows the three-way distinction moving backward by one observation at each refinement round.

The audit rejects all 24 proposed single-pair coarsenings of the recovered nonterminal classes. This is a useful local implementation check. The general coarseness guarantee comes from the structural theorem, not merely those 24 tests.

### 12.2 LoopGuess: finite ordered transport at a terminal decision

There are hub, two loop, query and terminal observations. Random visible loops apply \(\alpha\) or \(\beta\) to the three relevant classes and update a nuisance coordinate. Query actions guess the relevant class. The initial relevant class is fixed, and nuisance is randomized. The construction has \(15b\) raw states and 13 structural quotient states.

Actions outside the query do not change the visible kernel in this benchmark. It is principally an ordered-memory task with one consequential terminal choice. It does not test general active control over which hidden transport to explore.

The primary setting is \(b=16\), query probability \(0.1\), 3,500 online training episodes, learning rate \(0.2\), discount \(0.99\), and exploration decreasing from \(0.90\) to \(0.03\) over 1,200 episodes. Evaluation uses 500 episodes per checkpoint and 2,000 at the end. Sweeps use 1,800 training and 1,000 final evaluation episodes.

| Method | Final success, Table 1 | Same-count paired-order accuracy | Visited decision-time states |
|---|---:|---:|---:|
| Observation Q | \(0.351\pm0.055\) | \(0.336\pm0.005\) | \(1.0\pm0.0\) |
| Count Q | \(0.543\pm0.014\) | \(0.342\pm0.003\) | \(266.7\pm6.5\) |
| History Q | \(0.686\pm0.007\) | \(0.502\pm0.014\) | \(1005.3\pm16.6\) |
| Raw-state oracle | \(1.000\pm0.000\) | \(1.000\pm0.000\) | \(48.0\pm0.0\) |
| HMRL-D | \(1.000\pm0.000\) | \(1.000\pm0.000\) | \(3.0\pm0.0\) |
| Quotient oracle | \(1.000\pm0.000\) | \(1.000\pm0.000\) | \(3.0\pm0.0\) |

The shared Q-learning backbone makes the representation comparison interpretable. The information and access budgets differ. HMRL-D receives a simulator-provided calibrated diagnostic channel and uses 216 calibration interactions separately from online training. The oracles receive privileged state information.

The 216 calibration count is \(3\times24\) prototype observations plus \(6\times24\) edge observations. The control experiment uses synthetic four-dimensional class fingerprints. These are full-vector diagnostic interactions, not the scalar-per-coordinate probe budget of the general theorem or Sections 8–9 above.

History Q can preserve ordering but has sparse exact-history visits and a larger table. Its lower result at this finite budget is not an expressivity impossibility for history-dependent controllers.

### 12.3 Diagnostic experiment and reporting limits

The standalone diagnostic sweep uses three fixed three-dimensional prototypes with separation 1.48 and Gaussian noise levels \(0.25,0.5,1.0\). It tests repetitions \(m=1,2,4,8,16,32,64\), with 1,500 class trials and 1,500 transport trials per repeated evaluation. In the transport experiment, the source class is already known and the target fingerprint is averaged. It does not separately test recovery under independently permuted local gauges.

At noise \(0.5\), reported class and transport errors reach zero by \(m=8\). This is zero observed error in these finite trials. The concentration theorem gives a probability bound, not zero true error.

The active text and plots report means and standard deviations. An inactive commented source block specifies seeds and a quick-run count, but that block is not evidence that the active paper reports that replication count. No executable artifact was inspected to resolve it.

Episodes are forced to query after 48 completed loops. At query probability \(0.1\), the uncapped hit probability is \(0.9^{48}\approx0.00636\), consistent with the reported cap frequency \(0.0058\pm0.0010\). At probability \(0.05\), the reported cap frequency rises to \(0.085\pm0.010\). That sweep concerns the capped process, not an effectively uncapped geometric horizon.

Figure 6 reports three HMRL-D states for both decision-time visits and learned Q states. Those are implementation/metric counts, not the total structural quotient count of 13 and not the full storage for prototypes, edge tables and checkpoint restoration. The implementation was not obtained, so no stronger claim about its allocation is made.

Figures 4–5 and Tables 6–7 show robustness to larger nuisance multiplicity and longer expected loop histories within the reported settings. They do not independently validate the diagnostic-access assumptions.

## 13. Relations to other theories and usable scope

The source positions its construction beside bisimulation, MDP homomorphisms, predictive states, reward machines and regular decision processes. The operative overlap is exact future-response equivalence with deterministic successor closure. Reading this paper's comparison table is not full reading or independent validation of every related-work claim.

The distinctive simplifying ingredients are:

- Visible edge probabilities are independent of the hidden mode.
- An observed edge determines a hidden permutation.
- The target quotient preserves conditional mean reward and successor classes.
- Known classes can be tracked exactly.
- Diagnostics can restore an unchanged hidden checkpoint.

General POMDP transition mixing and observation likelihood updates can generate infinitely many reachable beliefs from a fixed prior. Finite raw hidden state alone does not justify Section 5's finite orbit construction outside the HCDP model. Similarly, reward-aware filtering requires output-law preservation beyond the source's mean-reward quotient.

For subsequent mathematical work, the most reusable objects are the signature refinement operator, finite witness backpointers, locally labeled deterministic update tables, SCC permutation coordinates, and a finite-map realization of fixed-prior beliefs. The conditional probe compiler supplies an explicit way to turn a structural separation into an observable experiment.

No FP object is identified with these classes without a separate source-to-target mapping and assumptions. In particular, the note does not establish that ordinary normalized language prediction automatically supplies restorable checkpoints, a finite witness-depth bound, a positive known gap or complete coverage. It provides constructive tools that Astra can evaluate, modify or discard.

## Source and claim boundary

All source attributions above refer to the pinned v1 and its numbered sections, results, figures and tables. Sections 3's response-code clarification, 4.2, 5.3–5.4 and 8–10 contain the explicitly identified independent deductions. Their proofs are given here at the level of finite maps, conditional moments and finite union bounds. They are not formalized and are not asserted to be novel relative to all prior literature.

The structural theorem, diagnostic classification theorem and exact reduction have different inputs. Their conjunction is usable only when those interfaces are supplied. The constructive additions expose one way to supply prototypes and rows under further conditions, while preserving the distinction between existence, computation, sampling and physical access.
