# Zhao et al. — linear recurrent memory and partially observable control

## Source, edition and actual coverage

- **Paper:** Yike Zhao, Onno Eberhard, Malek Khammassi, Ali H. Sayed and Michael Muehlebach, *Why Linear Recurrent Memory Works in Partially Observable Reinforcement Learning*.
- **Selected edition:** [ICML 2026, PMLR 306:161337–161372](https://proceedings.mlr.press/v306/zhao26j.html), [official PDF](https://raw.githubusercontent.com/mlresearch/v306/main/assets/zhao26j/zhao26j.pdf), **36 physical pages**.
- **Companion:** [arXiv:2605.31261v1](https://arxiv.org/abs/2605.31261v1), submitted May 29, 2026 at 12:56:28 UTC. The inspected history lists only v1. The [v1 source](https://arxiv.org/src/2605.31261v1) contains one active scientific TeX file, `example_paper.tex`, with no input/include children.
- **Edition comparison:** complete `pdftotext -raw` outputs agree after whitespace removal and removal of the unique arXiv watermark. The common extraction has **71,898 characters**. PDF binaries differ. This establishes extracted-text agreement, not pixel or vector identity. The source archive has 98 bibliography database entries but only **35 printed references**.
- **Reading:** Pro-C, November 26, 2026, personally read the complete official text, §§1–8, Impact Statement, all 35 references, Appendices A–E and their proofs. All **10 figures**, including both panels of Figures 9 and 10, **2 tables** and the sole body footnote were covered. Original PDF pages **4, 6, 8, 11–13, 15, 26, 32–36** were visually inspected. The v1 source was used for scoped structure/formula checks, not counted as another full reading.
- **Evidence level:** full reading plus bounded independent interface and concentration checks. No training reproduction, author-code certification or formal proof replay. Primary source claims and independent deductions are separated below. No withdrawal or replacement was observed in the inspected primary records.
- **Local source:** `literature/corpus/pro_c/zhao26j/paper.pdf`. Official PDF SHA256 `4411bb438606aae9ae73d9076c4d1fe2865b7c61dd51f6947f217b3aed5763dd`. Version/source inventories and rendered pages are in the ignored corpus directory.

## Main assessment

The useful result is a concrete filtering mechanism for **supplied finite models with deterministic or nearly deterministic dynamics**. A permutation acts linearly on log likelihoods. Discounted, permuted log likelihoods can also identify a state reliably when irregular transitions become rare and emissions distinguish the relevant deterministic trajectories. The fixed-HMM proof gives a meaningful separation between the time needed to accumulate evidence and the time between irregular jumps.

Three boundaries matter when interpreting this as a memory result.

1. The exact construction uses the transition structure, emission likelihoods and initial prior. Its arbitrary-initialization statement is implemented by a model-dependent first-step correction. General deterministic transitions require a startup observation window and extended-real logits. The displayed transient-state correction is not well defined at all allowed zero probabilities.
2. The nearly deterministic theorem proves **state-decoding error**, not convergence of the softmax output to the Bayesian posterior. A two-state example below has vanishing decoding error while the proxy posterior retains a fixed positive error.
3. The experiment distinguishes fixed known-model filters from jointly learned memories. Deep ALF uses a special common-diagonalizer structure, and its random-initialization performance does not establish acquisition of the true model or the theorem's assumptions.

The fixed-HMM concentration core is supported at this bounded checking depth. The action-controlled theorem has only a one-sentence analogy proof in the source. A short independent coupling and conditional-concentration argument below supports the stated qualitative control conclusion under its stronger emission assumption, without treating future adaptive actions as exogenous.

## 1. Objects and information interface

The model has finite hidden states \(X\), actions \(A\) and one-hot observations \(Y\), with sizes \(N,L,S\). Matrices use **column-stochastic** conventions:

\[
T_{ij}(a)=\Pr(X_{k+1}=i\mid X_k=j,A_k=a),\qquad
E_{ij}=\Pr(Y_k=u_i\mid X_k=j).
\]

Starting from \(\alpha_0=\pi_0\), the action-observation belief and an unnormalized logit obey

\[
\alpha_k\propto\operatorname{diag}(E^\top Y_k)T(A_{k-1})\alpha_{k-1},
\]

\[
w_k^o=\log\{T(A_{k-1})\exp(w_{k-1}^o)\}+\log(E^\top Y_k),
\qquad \alpha_k=\operatorname{softmax}(w_k^o).
\]

The correct initial logit is \(\log\pi_0\), up to an irrelevant common additive constant. These are **unnormalized** log probabilities, so a growing common negative offset does not imply loss of posterior information. This matters for the raw-LOF neural readout experiment.

The general linear-memory class is \(z_k=Az_{k-1}+\phi(b_k)\), or \(z_k=A(b_k)z_{k-1}+\phi(b_k)\). The encoder is allowed to be nonlinear. Its input can include a fixed observation window. Thus “linear” concerns recurrence in the stored vector, not the whole observation-to-state computation.

The paper's sufficient-statistic discussion uses action-observation histories. If an implementation also exposes informative rewards or another side channel to the policy, that information must be included in the observation/history interface before claiming sufficiency for that larger policy class. Nothing in the logit algebra itself identifies an unknown model from experience. [§§3.2–3.4, Eqs.1–10.]

## 2. Exact deterministic filtering

### 2.1 Permutations give a direct linear logit recurrence

For a permutation matrix \(P\),

\[
\log(P\exp w)=Pw.
\]

With positive prior and emission probabilities, all quantities are finite and

\[
w_k=Pw_{k-1}+\log(E^\top Y_k)
\]

exactly implements the unnormalized Bayesian logits when initialized correctly. To permit an arbitrary finite \(w_0\), the source explicitly defines

\[
\psi(k,y)=\log(E^\top y)+\mathbf 1_{\{k=1\}}P(\log\pi_0-w_0).
\]

The wrong initialization is **canceled by supplied prior information**, not forgotten by an undriven unit-circle recurrence. The time input and this exceptional first update are part of the construction. The source itself leaves approximation of this encoder by standard MLPs for future work. [Theorem 4.4, Eqs.16–17.]

For controlled permutations, the same identity uses \(P(A_{k-1})\), and the correction uses the actual first action. **Corollary 4.5 assumes every action matrix is a permutation.** It is not an exact theorem for all action-dependent deterministic maps. [§4.2, Eq.18.]

### 2.2 General deterministic maps use startup history and transient support

“Deterministic” in Definition 4.1 permits repeated columns. After relabeling,

\[
T=\begin{pmatrix}T_{11}&0\\T_{21}&P\end{pmatrix},
\qquad T_{11}^{\ell}=0,
\]

where the first \(r\) states are transient and \(P\) permutes the recurrent states. One can choose \(\ell\le r\) when \(r>0\). The paper sets \(\ell=1\) in the permutation case.

After \(\ell\) steps the unnormalized transient probabilities vanish. On the remaining support, logit propagation becomes a permutation plus observation log likelihood. The stated recurrence uses

\[
T'=\operatorname{diag}(I_r,P),\qquad
w_k=T'w_{k-1}+\psi(k,Y_k,\ldots,Y_{k-\ell+1}).
\]

For \(k\le\ell\), this input window contains the entire available observation prefix. The encoder uses that prefix and the known \(T,E,\pi_0\) to calculate the exact startup filter and a correction. For \(k>\ell\), only \(\log(E^\top Y_k)\) remains. Lemma C.1 moves diagonal likelihood factors through deterministic maps and verifies the required zero support. [Lemma 4.2, Theorem 4.4, Appendix C.]

This is a representational existence construction with a nontrivial supplied encoder. The dimension \(N\) does not include storage or computation of the startup observation window, the encoder or the model matrices.

### 2.3 Bounded zero-probability check

The broad exact statement is not literally an ordinary finite-real RNN theorem. A non-permutation deterministic map has zero probability on transient states after finitely many steps, so exact logits contain \(-\infty\). Even a permutation with a zero prior or zero emission likelihood can require such logits. No finite-real softmax vector represents a probability zero exactly.

The authors explicitly use \(0\cdot(-\infty)=0\). That convention does **not** define \((-\infty)-(-\infty)\), which appears in the printed startup correction, Eq.65.

For example, take the three-state chain \(1\to2\to3\to3\), one uninformative observation, positive uniform prior, and \(w_0=0\). Here \(\ell=2\) and \(T'=I_3\). The unnormalized beliefs are

\[
\beta_1=(0,1/3,2/3),\qquad \beta_2=(0,0,1).
\]

At the first coordinate, Eq.65's \(k=2\) correction subtracts \(\log\beta_1(1)=-\infty\) from \(\log\beta_2(1)=-\infty\). Its cancellation in Eq.66 is not valid extended-real arithmetic. A support-aware definition could handle this particular case, but it is additional to the printed convention.

With the allowed point prior \(\pi_0=e_1\), the same chain gives

\[
w_1^o=(-\infty,0,-\infty),\qquad
w_2^o=(-\infty,-\infty,0).
\]

The third coordinate must recover from \(-\infty\) under \(T'=I_3\). Ordinary addition with a finite increment cannot do that, and adding \(+\infty\) is indeterminate. This delimits the displayed recurrence and its domain. It does not prove that no other finite representation or explicit reset/masking mechanism can realize the process.

The clean finite-real exact result is the permutation construction with positive prior and positive likelihoods. The general deterministic construction needs explicit support semantics or a modified representation. [Independent finite examples applied to Appendix C.2, Eqs.63–66.]

## 3. Nearly deterministic HMMs and the supported core

### 3.1 Model, observability and initialization

Now \(T=D+\varepsilon Q\), with fixed deterministic backbone \(D\). Away from its one nonzero entry per column, \(Q\) is nonnegative, and each column sums to zero. For sufficiently small \(\varepsilon\), this gives a stochastic matrix. The sign/column-sum conditions alone do not guarantee nonnegativity for arbitrary \(0<\varepsilon<1\). One also needs

\[
\varepsilon q_*\le1,\qquad
q_* = \max_j\sum_{i\ne D(j)}Q_{ij}.
\]

Appendix D.5 uses this restriction explicitly in Eq.163. The asymptotic argument holds the finite model \(D,Q,E\) fixed as \(\varepsilon\to0\). It is not uniform over diverging \(Q\), state count or vanishing emission separation.

This section orders recurrent states first:

\[
D=\begin{pmatrix}P&D_{12}\\0&D_{22}\end{pmatrix},
\qquad D_{22}^{\ell}=0.
\]

The adaptive logit filter is

\[
w_k=\begin{pmatrix}P&0\\0&I_r\end{pmatrix}(1-\delta)w_{k-1}
       +\delta\log(E^\top Y_k).
\]

Recurrent coordinates start finite. For \(0<\delta<1\), transient coordinates start and remain at \(-\infty\), so they are never decoded. This is acceptable asymptotically because their true occupancy is \(O(\varepsilon)\), not because the transient states are absent from the perturbed model.

Write \(\widetilde E\) for recurrent-state emission columns and \(M\) for the order of \(P\). Assumption 5.6 requires all entries of \(\widetilde E\) positive and all columns of

\[
E_s=\begin{pmatrix}\widetilde E\\\widetilde EP\\\cdots\\\widetilde EP^{M-1}\end{pmatrix}
\]

distinct. It does **not** require full column rank. Two states can have identical immediate emissions if their subsequent deterministic trajectories distinguish them. Appendix A.1 supplies a four-state, two-cycle example. The finite order is the least common multiple of the cycle lengths, so constants involving \(M\) are not dimension-free.

### 3.2 Quantifiers and error rate

The loss is

\[
p_k=\Pr\{\arg\max_x w_k(x)\ne X_k\}.
\]

Theorem 5.7 assumes

\[
\delta_\varepsilon\longrightarrow0,\qquad
\varepsilon/\delta_\varepsilon\longrightarrow0
\]

and concludes

\[
\lim_{\varepsilon\to0}\limsup_{k\to\infty}p_k=0.
\]

This is the **long-time limit first**, followed by the rare-irregular-transition limit. It is not a fixed-horizon statement, an almost-sure pathwise guarantee, a finite-sample learning bound or a regret theorem.

For \(\delta_\varepsilon=\lambda/\log(1/\varepsilon)\), with \(0<\lambda<\xi(P,E)\), the paper obtains

\[
\limsup_{k\to\infty}p_k
\le\kappa\varepsilon\log(1/\varepsilon)
 +o(\varepsilon\log(1/\varepsilon)).
\]

The proof specifies \(\kappa=q_*\alpha/\lambda\), with a sufficiently large window constant \(\alpha\). Its choice depends in part on the bounded starting logits and likelihood magnitudes. The positive \(\xi\) is a minimum over recurrent-state pairs of integrals of log moment-generating functions of likelihood ratios, including the permutation period. Appendix D.2 gives \(\xi\approx0.7206\) in the symmetric two-state example, explaining the tested \(\lambda=0.7\).

The paper compares this order with classical optimal-filter results of Khasminskii–Zeitouni. Its own proof is an **upper bound**. It does not establish a matching lower bound for every model allowed here, optimal leading constants or a uniform minimax theorem. For example, \(Q=0\) is explicitly allowed, so an interpretation requiring a positive universal irregular-switch lower term would be inappropriate. The historical lower-bound source was not independently read in this unit.

### 3.3 Proof structure actually read

The proof splits errors into recent irregular jumps, transient-state occupancy, and errors after a sufficiently long regular trajectory.

- For a window \(T_\varepsilon=\alpha/\delta_\varepsilon\), a union/Bernoulli bound gives irregular-jump probability at most \(q_*\varepsilon(T_\varepsilon+1)\).
- Nilpotence of the transient block gives occupancy \(O(\varepsilon)\) uniformly after a fixed startup length. Multiplying the bounded rows of \(T^\ell\) by further stochastic powers keeps the bound uniform in time.
- On a regular path, conjugating by powers of \(P\) aligns state coordinates. Each logit difference is a geometrically weighted sum of observation log likelihood ratios plus a decaying initialization term.
- Over a full permutation cycle, each competing recurrent state differs in at least one emission distribution. Positive finite emissions make the relevant likelihood ratios bounded, and their mean is a strictly positive KL divergence.
- Lemma D.9 controls the geometric sum of log moment-generating functions by an integral and a bounded remainder. With a long enough window, the initialization term cannot cancel its negative Chernoff exponent.
- The conditional error becomes exponentially small in \(1/\delta\). Balancing that term against \(\varepsilon/\delta\) gives the stated logarithmic choice.

All of Appendix D, including the integral comparison, limiting constants and supporting lemmas, was read. The fixed-HMM path conditioning does supply independent observations on the prescribed path. No material obstruction to this selected fixed-model argument was found in the bounded check. This is not a certificate of every printed lemma or every extension.

## 4. Controlled permutations and an explicit adaptive-policy argument

Theorem 5.9 assumes

\[
T(a)=P(a)+\varepsilon Q(a),\qquad
w_k=(1-\delta)P(A_{k-1})w_{k-1}+\delta\log(E^\top Y_k).
\]

There are no backbone transient states. **All** emission entries are positive and **every pair** of emission columns is distinct. This is stronger than the fixed-HMM stacked-trajectory condition. The source says that Theorem 5.7 follows analogously, without expanding the controlled proof. In a feedback policy, conditioning on an entire future action tape can change observation laws and independence. The fixed-period factorization from Appendix D therefore cannot simply be copied with actions inserted.

### Independent bounded repair under the printed stronger emission condition

The following argument supports the qualitative controlled conclusion for any causal policy, with potentially different sufficient constants. It is not a claim that the source printed this proof or that its fixed-cycle \(\xi\) is preserved.

For \(N\ge2\), define

\[
d=\min_{i\ne j}\mathrm{KL}(E_i\Vert E_j)>0,\qquad
L_0=\max_{i,j,y}\left|\log\frac{E_i(y)}{E_j(y)}\right|<\infty.
\]

Let \(W=\max(\|w_0\|_\infty,\max_y\|\log(E^\top y)\|_\infty)\). Because permutations preserve the sup norm, the ALF remains bounded by \(W\). Let \(q_*\) be the largest off-backbone rate over all actions and current states.

Fix a window-start hidden state, filter state and full policy/history state. Couple the perturbed model with a backbone-only model using the same policy random source and observations until the first irregular transition. Their histories and actions agree until that deviation, whose probability is at most \(\varepsilon q_*T\). This avoids conditioning the observation process on a future no-jump event.

In the backbone process, evolve a candidate starting state \(j\ne i\) through the **same chosen permutations** as the true state. They remain distinct. Before observing \(Y_t\), this pair is predictable. Therefore

\[
g_t=\log\frac{E_{i_t}(Y_t)}{E_{j_t}(Y_t)},\qquad
\mathbb E[g_t\mid\mathcal F_{t-1}]\ge d,\qquad |g_t|\le L_0.
\]

The corresponding logit difference at the window end is

\[
o_T=(1-\delta)^To_0+
\sum_{t=1}^{T}\delta(1-\delta)^{T-t}g_t,\qquad o_0\ge-2W.
\]

Take \(T=\lceil\alpha/\delta\rceil\), where \(\alpha\) is large enough that

\[
d(1-e^{-\alpha})-2We^{-\alpha}\ge d/2.
\]

The squared weights sum to at most \(\delta/(2-\delta)\le\delta\). Conditional Hoeffding with conditional range width \(2L_0\), followed by a union bound over \(N-1\) rivals, gives

\[
\Pr(\text{backbone decoding error})
\le(N-1)\exp\left[-\frac{d^2}{8L_0^2\delta}\right].
\]

Consequently, uniformly for \(k\ge T\),

\[
p_k\le (N-1)e^{-c/\delta}
 +\varepsilon q_*\left(\frac{\alpha}{\delta}+1\right),
\qquad c=\frac{d^2}{8L_0^2}.
\]

This supplies consistency when \(\delta\to0\) and \(\varepsilon/\delta\to0\), and an \(O(\varepsilon\log(1/\varepsilon))\) bound for \(\delta=\lambda/\log(1/\varepsilon)\) with \(0<\lambda<c\). Constants are conservative. This uses finite known emissions, fixed finite model families, bounded initialization and causal actions. It establishes neither learning of those quantities nor the source's exact constant formula for arbitrary controlled permutations.

Appendix A.2 separately explains why general deterministic action maps are harder. Actions can disagree about which states are transient. Even a common transient set can be revisited indefinitely by alternating actions. A common strictly triangular transient ordering is proposed as an additional condition, not proved as a completed general extension.

## 5. Decoding is not posterior approximation

The source's precise theorem concerns \(\arg\max w\). Its broader introductory language about approximating log beliefs should be interpreted in that restricted sense unless an additional calibration result is supplied.

### Independent two-state example

Take \(D=I_2\), \(Q=0\), positive nondegenerate prior, \(w_0=0\), and

\[
E_1=(3/4,1/4),\qquad E_2=(1/4,3/4).
\]

This satisfies the fixed-HMM assumptions, including the explicitly allowed zero perturbation. Conditional on true state 1, the logit difference obeys

\[
z_k=(1-\delta)z_{k-1}+\delta g_k,
\quad g_k\in\{\log3,-\log3\},\quad
\mathbb E g_k=\tfrac12\log3.
\]

For fixed \(\delta\), its long-time variance is \(\delta\operatorname{Var}(g)/(2-\delta)\). As \(\delta\to0\) after the long-time limit, \(z_k\) concentrates at \(\tfrac12\log3>0\), and decoding error vanishes. But

\[
\operatorname{softmax}(w_k)_1
\longrightarrow\frac{\sqrt3}{1+\sqrt3},
\]

whereas the exact posterior converges almost surely to 1. The limiting total-variation difference is

\[
\frac1{1+\sqrt3}>0.
\]

The proxy assigns a persistent positive probability to the false state even while selecting the correct state with probability approaching one. This refutes an implication from the stated decoding theorem to posterior/TV calibration. It **does not refute Theorem 5.7**. The same distinction prevents treating its error bound alone as an optimal-policy or value-approximation theorem.

## 6. Experiments and what was learned

### 6.1 Numerical state decoding

The main two-state experiment uses a swap backbone with irregular self-loops:

\[
T=\begin{pmatrix}\varepsilon&1-\varepsilon\\1-\varepsilon&\varepsilon\end{pmatrix},
\qquad E=\begin{pmatrix}.9&.1\\.1&.9\end{pmatrix}.
\]

There are 23 values of \(1/\varepsilon\) in \([30,250]\), with 20,000 Monte Carlo iterations per value. Figure 1 uses \(p_{1000}\) as a long-run proxy. The two admissible choices are \(\sqrt\varepsilon\) and \(.7/\log(1/\varepsilon)\). The compared inadmissible choices are \(\varepsilon^2,0,1\). Figure 7 shows temporal stabilization at **one** \(\varepsilon=.005\) for LOF and the two admissible ALFs, not all choices in Figure 1.

The observed ordering supports the mechanism in this finite parameter range. It does not establish asymptotic equality, optimal constants, or uniform stationarity by step 1000. The \(\delta=\varepsilon^2\) case has a particularly long adaptation scale. No Monte Carlo confidence bands are displayed. The text's statement that \(\delta=1\) violates both limit conditions is a local slip: it violates \(\delta\to0\), while \(\varepsilon/1\to0\) does hold.

Appendix E.1 generates the hidden process from \(\pi_0=(1,0)^\top\) but initializes **both** LOF and ALF at \(w_0=(0,0)^\top\). Thus its finite-time LOF uses a uniform filter prior, not the stated point prior. It cannot be identified at every finite time with the Bayes decoder for that generating prior. In this positive mixing two-state model, long-run forgetting can remove the difference, so this observation does not invalidate all long-run comparisons. No independent stationary-error calculation was performed.

Figure 5 supplies a separate single-trajectory slow-switch example with emissions .8/.2. Smaller \(\delta\) smooths observation noise but delays response to a hidden switch. Figure 6 shows a short controlled trajectory with remaining ALF decoding errors. Both are illustrations, not independent statistical validations. [§6.1, Appendices B and E.1.]

### 6.2 RingWorld and the model-knowledge distinction

RingWorld has 12 hidden positions, four clockwise/counterclockwise moves of one or two cells, and four noisy beacon observations. Overshoot and slip each occur with probability .05. Observations are drawn with probabilities proportional to \(\exp\{\cos(\theta_j-\xi_i)\}\), not a deterministic nearest-beacon rule. States 2 and 3 are goals, and 6, 11 and 12 are traps. Rewards are scaled by episode length \(K\), giving total return in \([-1,1]\). The provided text does not specify the numerical \(K\). The PPO unroll length 1024 is not automatically the episode length.

| Method | Supplied knowledge | Trained quantities |
|---|---|---|
| LOF | Full \(T(a),E\) | Actor and critic only |
| ALF | Backbones \(P(a)\), emissions \(E\), selected \(\delta=.1\) | Actor and critic only |
| S5 | Architecture and selected hidden size | Encoder, memory, actor and critic |
| Deep ALF, all random | \(N,S\) and the specified action-dependent diagonal/common-basis structure | Memory parameters, actor and critic |
| Deep ALF, informed or partially informed | Some or all true model parameters at initialization | **All** memory parameters remain trainable |

There is no reported hidden-state-label training loss, belief fitting or teacher-filter distillation objective. “Learning target” refers to an intended structure/representation, not an actual supervised distillation protocol. PPO success also does not establish that learned matrices named \(E,\Lambda,V\) identify the physical environment.

The PPO table reports learning rate \(5\times10^{-5}\), 64 environments, unroll length 1024, 30 million timesteps, 30 epochs, eight minibatches, discount .99, GAE parameter 1, clip coefficient .2, no entropy bonus, gradient-norm cap .5, and separate [128,128] actor/critic hidden layers. S5 uses ZOH discretization and initial step scales .001–.1. Figures 3, 9 and 10 show eight seeds with **standard-deviation** shading. A held-out environment distribution, independent evaluation protocol, exact seed list and significance tests are not supplied.

Visually, softmax-LOF is strongest in Figure 3, fixed ALF is close, S5-256 and all-random Deep ALF are much closer to one another than to the informed filters, and S5-12 is weaker. Raw LOF logits give slower and more variable PPO training. This is consistent with numerical conditioning of the actor/critic input, not more decision information in ALF than in an exact belief. The paper has no numeric performance table, so these are qualitative figure comparisons rather than recovered exact scores.

Figures 9–10 distinguish good initialization, random emission initialization, random adaptation initialization, random eigenvalues and fully random initialization. Only initialization differs in the partial variants, not which parameters remain learnable. True-model initialization improves the results substantially. These controls are useful, but an informed model versus a model-free baseline is not an isolated architecture comparison.

## 7. Common diagonalization and resource accounting

In RingWorld the four permutation backbones are circulant and share a DFT basis \(V\). With \(P(a)=V\Lambda(a)V^{-1}\) and \(h_k=V^{-1}w_k\),

\[
h_k=(1-\delta)\Lambda(A_{k-1})h_{k-1}
       +\delta V^{-1}\log(E^\top Y_k),\qquad w_k=Vh_k.
\]

Deep ALF makes \(\Lambda(a),V,E,\delta\) learnable. All-random initialization retains a common-basis diagonal family, known dimension and the chosen encoder form. General permutation matrices need not commute or share a diagonalizer. The authors explicitly reserve general nearly-permutation environments for future work. The appendix does not give a proof that arbitrary trained parameters remain a valid stochastic model satisfying Theorem 5.9.

The quoted parameter counts compare **only the observation encoders**:

| Encoder | Printed count |
|---|---:|
| S5, hidden size 12 | \(4\cdot128+128\cdot12=2048\) |
| S5, hidden size 256 | \(4\cdot128+128\cdot256=33280\) |
| Deep ALF | \(4\cdot12=48\) |

The S5 arithmetic omits biases. The 48 is not the full Deep ALF parameter total: learned complex \(V\), action-dependent \(\Lambda\), \(\delta\), actor and critic remain. A learned general \(V\) also does not automatically retain a fixed DFT's fast-transform implementation. The input/output basis transforms cost work even when the central recurrence is diagonal.

Dimension \(N\) is not a finite-bit memory bound. Fixed ALF stores real logits, while Deep ALF is parameterized in complex coordinates. The paper reports no complete installed-bit accounting, activation-memory measurement, FLOPs, throughput, wall-clock comparison or hardware specification. It supports a specific encoder-parameter and return comparison on one environment, not measured dominance in total memory and compute. No author implementation was inspected or training reproduced in this reading unit.

## 8. Limits relevant to future use

- The construction assumes a supplied hidden-state alphabet and model interface. Neither the theorem nor the experiment proves discovery of an unknown minimal predictive state or an unknown update program.
- Exact finite-real permutation filtering, idealized transient-support handling, near-deterministic state decoding and PPO policy learning are four different claims with different assumptions.
- The fixed-model observability condition is pairwise trajectory distinguishability. It is weaker than one-step emission separation, but it is not an identifiability or efficient model-learning theorem.
- The recurrent matrix retains a known deterministic backbone. Its near-unit eigenvalues explain a particular rare-transition evidence-accumulation regime, not the success of every linear recurrent architecture or every POMDP.
- The highly stochastic example in §7 becomes memoryless because the transition resets the state independently. That example is not a general result that stochastic environments make history useless.
- Finite discretization of continuous control is discussed without an approximation theorem or continuous-control experiment.
- The independent controlled concentration argument is a literature-level clarification. It does not modify FP theory, architecture or experiments. No concrete FP transfer is proposed in this note.

## Completion and recovery

The selected official edition is **fully read**. The companion v1 is text-matched and scoped for source/version checking, without an additional full-read count. The exact zero-support issue, the decoding/calibration separation, the supported HMM proof, the independent adaptive-policy bound and empirical/resource interfaces are the substantive findings. No theorem-wide formal certification is claimed.

At the selection boundary, Astra request `59b8251` remained owned by Pro-E through `40c0d2a`. Astra's concurrent work through `9ba8046` and Pro-D's `ecc064c` are preserved without core edits. Subsequent work requires a new fetch and owner/request check. Zhu–Lu AISTATS 2026 remains a prepared metadata/abstract candidate, with its scientific body unread at this boundary.
