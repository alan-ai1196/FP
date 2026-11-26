# Memory Constrained Adversarial Hypothesis Testing

## Source, status and actual coverage

Malhar A. Managoli and Vinod M. Prabhakaran, arXiv **2605.12063v2**, submitted 12 November 2026 at 20:59:17 UTC. The retrieved PDF has 22 pages and a 16 November draft footer. Sources: [versioned record](https://arxiv.org/abs/2605.12063v2), [PDF](https://arxiv.org/pdf/2605.12063v2), [TeX](https://arxiv.org/src/2605.12063v2), [HTML](https://arxiv.org/html/2605.12063v2).

**Pro-A completed the full v2 reading on 26 November 2026, Shanghai.** Coverage is all eight body sections, Appendices A–B and their proofs, all equations and seven numbered explanatory footnotes, title acceptance notice, three actual automaton figures on pp. 7, 15 and 16, AI disclosure and all 23 printed references. The main reader read the complete 1,092-line journal_version.tex, its active AIStatement.tex and the 24-entry source bibliography. The unused Huber 1964 entry is not a printed reference. Original PDF layouts on pp. 5–7, 11–12, 14–18 were inspected. There are no tables or experimental results.

The source reports acceptance **in part** at ITW 2026 under an earlier title. No separate proceedings version was authenticated. This note concerns the extended arXiv v2. The previously scoped v2 record is now complete. The distinct 15-page v1 remains outside this full-reading claim.

The authors disclose that ChatGPT-6 Astra review suggested the occupation-measure proof strategy and a shorter proof for the three-letter example. They report manually writing the resulting analysis and AI-assisted copy-editing. This is author-reported assistance, not official OpenAI authorship or independent verification.

Local ignored source path: literature/corpus/pisf_prior_art/0940e87-recent-source-screen/2605.12063v2/. PDF SHA-256: b741903317c9d0322014bb7983d27642cd818556f95113fca02b00df155cce48.

## What the paper solves

The paper characterizes how the number of states controls **asymptotic time-average binary testing error** against an adaptive distribution-selecting adversary. The testing machine is time-invariant and randomized. The adversary sees its past states, but not its fresh future random coins.

Its main result gives upper and lower bounds separated by at most one state. Their common exponential rate is one half the smallest Hellman–Cover log likelihood-ratio spread over the two uncertainty sets. Two states have a different exact constant, reflecting the adversary's ability to choose different distributions at opposite ends of the machine.

This is a mathematical result about a supplied testing problem and an optimally chosen finite machine. It does not learn a state structure from unknown raw data, bound acquisition cost, or give finite-horizon cumulative predictive log loss.

## Model and order of limits

The alphabet \(\mathcal X\) is finite. The two hypothesis-dependent sets \(\mathcal P_0,\mathcal P_1\subseteq\Delta(\mathcal X)\) are nonempty, closed and convex. Convexity allows adversarial randomization to be absorbed into a distribution in the set.

An \(S\)-state machine has a fixed initial state, a fixed transition kernel \(\pi(t\mid s,x)\), and a fixed deterministic binary output \(\widehat H(s)\). Under the true hypothesis \(h\), the adversary selects \(P_i\in\mathcal P_h\) after observing all previous samples and states. Then \(X_i\sim P_i\), and the machine uses fresh randomness to update its state.

For an adversarial pair \(\mathcal A=(\mathcal A_0,\mathcal A_1)\), the risk is

\[
P_e(\pi,\widehat H,\mathcal A)
=\max_{h\in\{0,1\}}\limsup_{n\to\infty}
\frac1n\sum_{i=1}^{n}
\Pr_h^{\pi,\mathcal A_h}\{\widehat H(R_i)\ne h\}.
\]

The minimax value takes the infimum over machines after this long-run risk has been defined. The error exponent then lets the state count grow:

\[
P_e^*(S)=\inf_{\pi,\widehat H}\sup_{\mathcal A}P_e(\pi,\widehat H,\mathcal A),
\qquad
\Gamma=\lim_{S\to\infty}-\frac1S\log P_e^*(S).
\]

Thus the time limit is taken at a fixed machine and fixed \(S\). A small transition parameter may be selected to approach the infimum. An external time index, a finite observation budget and a bound on transition-probability precision are not part of this resource count.

## Two separation parameters

For nonnegative letter weights \(f_+,f_-\), define

\[
G(f_+,f_-,p,q)
=\frac{E_qf_+\,E_pf_-}{E_qf_-\,E_pf_+}.
\]

The interior parameter uses one distribution per hypothesis:

\[
\gamma
=\sup_{f_++f_-\le1}
\min_{p\in\mathcal P_0,\ q\in\mathcal P_1}G(f_+,f_-,p,q).
\]

The endpoint parameter allows separate distributions in the numerator and denominator:

\[
C=\sup_{0\le f_+,f_-\le1}
\min_{\substack{p,p'\in\mathcal P_0\\q,q'\in\mathcal P_1}}
\frac{E_qf_+\,E_pf_-}{E_{q'}f_-\,E_{p'}f_+}.
\]

The printed convention for an indeterminate full quotient is \(0/0=0\). Independent positive rescaling of either function leaves the objective unchanged. This permits simplex normalizations in the minimax proof without imposing an additional observation model.

Constant functions give \(1\le C\le\gamma\). For singleton sets both quantities reduce to

\[
\gamma_{\rm HC}(p,q)
=\left(\max_x\frac{q(x)}{p(x)}\right)
 \left(\max_x\frac{p(x)}{q(x)}\right).
\]

### Main claims

Theorem 1, p. 6, states for \(S\ge2\)

\[
\frac1{1+\gamma^{(S-1)/2}}
\ \le P_e^*(S)\le\
\frac1{1+\sqrt{C\gamma^{S-2}}}.
\]

The \(S+1\) upper bound is no larger than the \(S\) lower bound because \(C\ge1\). Corollary 1 gives \(\Gamma=\tfrac12\log\gamma\). Lemma 2 identifies

\[
\gamma
=\min_{p\in\mathcal P_0,\ q\in\mathcal P_1}\gamma_{\rm HC}(p,q).
\]

Appendix A, Theorem 8, gives the exact two-state value

\[
P_e^*(2)=\frac1{1+\sqrt C}.
\]

Theorem 2 supplies another exact case. A weak least-favourable pair controls only the probabilities of the sets of largest and smallest likelihood ratio. Its conditions make \(C=\gamma=\gamma_{\rm HC}(p^*,q^*)\). Full stochastic ordering of the likelihood ratio at every threshold is stronger than needed.

## How the achievability proof handles adaptive observations

The machine is a birth-and-death chain. At an interior state it moves right with probability \(f_+^\gamma(x)\) and left with probability \(f_-^\gamma(x)\). At state 1 it leaves right with probability \(\delta f_+^C(x)\). At state \(S\) it leaves left with probability \(\kappa\delta f_-^C(x)\). Endpoints output 0 and 1. Interior outputs can be arbitrary.

The endpoint functions can differ from the interior functions. This is substantive: at distinct endpoints an adversary may use two different members of the same uncertainty set, which is exactly what the definition of \(C\) charges.

The analysis does not assume the adaptive state process is a homogeneous Markov chain. Instead, form its expected occupation measure

\[
\mu_n^h(s)=\frac1n\sum_{i=1}^{n}\Pr_h(R_{i-1}=s).
\]

Average the adversary's distributions over visits to state \(s\), obtaining \(\bar p_n^h(\cdot\mid s)\). Closed convex uncertainty sets ensure that this averaged distribution remains in \(\mathcal P_h\). The averaged transition matrix \(T_n^h\) obeys the exact identity

\[
T_n^h\mu_n^h-\mu_n^h
=\frac{\mathcal L_h(R_n)-\mathcal L_h(R_0)}n.
\]

Compactness gives subsequential limits \((\mu^h,\bar p^h)\), and every such limit satisfies \(T^h\mu^h=\mu^h\). A positive regularization of all four letter functions makes the limiting birth-and-death chain irreducible.

Detailed balance gives

\[
\frac{\mu^0(1)}{\mu^0(S)}\ge\kappa C_0\gamma_0^{S-2},
\qquad
\frac{\mu^1(S)}{\mu^1(1)}\ge
\frac{C_1\gamma_1^{S-2}}{\kappa}.
\]

Each interior state's outgoing ratio uses the **same** averaged distribution in numerator and denominator. The endpoint ratio uses two independently chosen averaged distributions. This is the precise reason that the product has one factor \(C\) and \(S-2\) factors \(\gamma\).

If all letter weights are at least \(\eta>0\), the interior occupancy relative to state 1 is bounded by \(\delta/\eta^{S-2}\). Choosing \(\delta\) small makes the total interior mass arbitrarily small. Balancing the two endpoint error ratios with \(\kappa\), then taking the regularized optimization limits, proves the claimed infimum bound. The argument works for every limiting occupation measure and therefore controls the original limsup averages.

## Why the converse's minimax exchange is valid

A fixed iid pair \(p,q\) is already an admissible adversary. The Hellman–Cover lower bound for that pair reduces the converse to proving the minimax identity for \(G\).

The paper explicitly avoids asserting that \(G\) is jointly quasiconvex in \((p,q)\) and jointly quasiconcave in \((f_+,f_-)\). These properties need not hold. Its proof makes four separate exchanges using two factorizations:

\[
G=
\frac{E_qf}{E_pf}\frac{E_pg}{E_qg}
=
\frac{E_qf}{E_qg}\frac{E_pg}{E_pf}.
\]

It first restricts \(f\) to distributions of weights with \(\min_qE_qf>0\), and \(g\) to weights with \(\min_pE_pg>0\). These convex dense domains make the numerator positive and restore the required upper semicontinuity in the maximizing variables. Compactness stays on the minimizing distribution sets. Joint lower semicontinuity of the original extended quotient justifies recovery of the unrestricted supremum.

The first exchange moves \(g\) past \(p\) after minimizing over \(q\). Factorization isolates the \(p\)-dependent positive ratio. The exchange of \(g\) and \(q\) then gives a representation permitting the exchange of \(f\) and \(p\). Finally, maximizing over \(g\) leaves a positive factor independent of \(f\), so \(f\) can be exchanged with \(q\). Taking a minimum preserves upper semicontinuity and quasiconcavity. Taking a supremum preserves lower semicontinuity and quasiconvexity.

The imported extended-real Sion theorem was checked narrowly against **Ben-David–Blais, Theorem 2.11, printed p. 13** in the [author manuscript](https://cs.uwaterloo.ca/~eblais/assets/pdf/minimax.pdf). That source has 59 physical pages and is a 2023 manuscript with placeholder publication metadata. Only the theorem statement and immediate definitional context were used. Its full paper and Appendix A proof were not read.

For the exact two-state converse, the adversary separately maximizes transitions into the wrong state and minimizes transitions out of it. The product of the two error odds is at least \(1/C\), so one error is at least \(1/(1+\sqrt C)\). Appendix A also treats reducible machines. Fixed initialization matters in the case where both states are absorbing.

## Examples and deterministic machines

The three-letter example is

\[
p_\lambda=\left(\frac\lambda2,\frac{1-\lambda}4,\frac{3-\lambda}4\right),
\quad 0\le\lambda\le1,
\qquad q=(1/3,1/3,1/3).
\]

For \(\gamma\), the optimal normalized functions are

\[
f_+=(1/4,3/4,0),\qquad f_-=(0,0,1).
\]

Their ratio is 4 for every \(\lambda\), and \(p^*=(1/6,1/6,2/3)\) bounds any competing functions above by 4. Equality requires the stated supports, and testing the two endpoint distributions fixes the normalized weights. The paper's alternate \(f_+=(1/3,1,0)\) is the same function up to scale.

For \(C\), the different optimizer \(f_+=(1/3,2/3,0)\), \(f_-=(0,0,1)\) gives \(C=3\). A numerator bound \(1/2\) and denominator bound \(1/6\) establish optimality. Thus the exact two-state error is \(1/(1+\sqrt3)\), while the asymptotic exponent is \(\log2\). Restricting the interior functions to indicator sets loses the optimum.

A separate five-letter family has weak least-favourable pairs for \(\lambda\in(2/27,23/27)\) but no strong pair. Extreme ratios stay at 9 and \(1/9\). The middle likelihood-ratio threshold at \(2/3\), or the zero-probability case at \(\lambda=1\), violates full least favourability.

Section VII concerns deterministic machines and separated Bernoulli intervals \([0,p]\) and \([q,1]\), where \(0<p<q<1\). It extends the existing run-based achievable exponent

\[
\Gamma_{\rm det}\ge
\frac{\log q\log(1-p)-\log p\log(1-q)}
{\log(p(1-p))+\log(q(1-q))}
\]

and, when \(q=1-p\), the stronger symmetric bound

\[
\Gamma_{\rm det}\ge
\frac12\log(q/p)\left(1+\frac{\log q}{\log p}\right).
\]

Use shared uniform variables to couple every adaptive Bernoulli sample below an iid Bernoulli-\(p\) sample under hypothesis 0, and above an iid Bernoulli-\(q\) sample under hypothesis 1. Both displayed deterministic automata have transitions increasing in the state and the sample. Their ordered trajectories and increasing output then yield error domination at every time. This transfers the earlier achievable rates. It does not solve the remaining deterministic minimax exponent problem.

The prior deterministic converse also applies by choosing the iid endpoint adversary. The paper distinguishes private fresh randomness, advance-revealed randomness and unobserved machine states. Hiding states does not improve the optimal exponent, because the converse already uses iid observations. Exact finite-\(S\) values may still differ. Advance revelation of random coins is left unresolved.

## Reader deductions and bounded checks

**Algebraic reformulation, not a new source theorem.** For strictly positive \(p,q\),

\[
\log\gamma_{\rm HC}(p,q)
=D_\infty(q\Vert p)+D_\infty(p\Vert q).
\]

Consequently the paper's exponent is half the minimum symmetric order-infinity divergence over the two sets, under this positive-support restriction. Equivalently it uses the spread of log likelihood ratios. This restatement does not replace support conventions or turn the objective into a KL-risk bound.

**Finite-time obstruction for this construction.** Start its chain at endpoint 1. Under hypothesis 1, as long as it has never left 1, the next departure probability is at most \(\delta\). For any allowed adversary and fixed horizon \(N\),

\[
\Pr_1\{\widehat H(R_i)=0\}\ge(1-\delta)^i,
\qquad
\frac1N\sum_{i=1}^{N}\Pr_1\{\widehat H(R_i)=0\}
\ge1-\frac{\delta(N+1)}2.
\]

The second inequality uses \((1-\delta)^i\ge1-i\delta\), for \(0\le\delta\le1\). The lower bound can be negative and is then vacuous, but at any fixed \(N\) it tends to 1 as \(\delta\) tends to zero. This explicitly explains why the asymptotic endpoint-concentration argument does not furnish a uniform finite-time guarantee. It is a deduction for this endpoint initialization and construction, not a converse for every finite-memory test.

Manual checks covered occupation-measure balance, endpoint versus interior pairing, the four minimax exchanges, the two-state error-odds step, the exact three-letter saddle values and monotonicity of the two deterministic transition maps. No substantive gap was found in these inspected steps. A separate bounded second-reader check examined Lemma 2 and the two-state converse. Full-paper reading remained with Pro-A. No exhaustive FSM enumeration, numerical experiment, Lean formalization or whole-theorem certification was performed.

## Limits and research use

The result supplies an exact asymptotic state exponent, an informative endpoint correction and a reusable occupation-measure reduction for a known robust testing problem. State count charges persistent labels. Description length of the transition kernel, the precision of its real probabilities, transient waiting time and the work required to choose optimal functions remain separate resources.

The paper's own discussion explicitly leaves finite-time bounds and convergence rates for later work. Its criterion is a long-run average of binary mistakes, with an adversary that sees prior states. A finite-horizon posterior-mixture guarantee needs a separately proved relation between its update law, permissible adversary, loss and horizon. No such FP transfer is claimed here. Pro-B independently completed Astra's request 53c10ef in commit 15e837d. This full reading does not duplicate that bounded prior-art response.
