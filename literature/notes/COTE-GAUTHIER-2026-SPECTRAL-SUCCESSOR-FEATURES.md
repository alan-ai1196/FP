# Grid Cells as Spectral Successor Features: A Reusable Basis for Continual Reinforcement Learning

## Source and actual coverage

- **Authors:** Élodie Côté-Gauthier, Doina Precup and Isabeau Prémont-Schwarz.
- **Read edition:** [arXiv:2611.26504v1](https://arxiv.org/abs/2611.26504v1), submitted November 19, 2026. Only v1 was listed in the November 26 check. [PDF](https://arxiv.org/pdf/2611.26504v1) and [complete source](https://arxiv.org/src/2611.26504v1).
- **Publication status:** arXiv author version. The authors report acceptance at the NeurReps and WiML workshops at NeurIPS 2026. [Mila's institutional publication record](https://mila.quebec/en/directory/elodie-cote-gauthier) corroborates the WiML attribution and links [OpenReview zvMTOCzg9h](https://openreview.net/forum?id=zvMTOCzg9h). The separate venue decisions and workshop-edition equivalence were not authenticated. The institutional abstract describes an earlier oracle-only stage, so it is not substituted for this 15-page edition.
- **Full reading by Pro-C, November 26, 2026, Shanghai:** all 15 physical pages, the complete 350-line active main TeX, §§1–4, Appendices A–E, all formulas and arguments, three actual figures, both tables and all 14 references. Original PDF pp. 4–6, 8–9, 12–13 and 15 were visually inspected, including every figure/table and the central formulas. No substantive author footnotes or separate unexamined paper supplement are present.
- **Verification:** bounded manual checks of the invariant-span argument, state-only obstruction, exact deterministic goal-reaching argument and operator substitution. A separate source assistant checked the same mathematical boundaries. No formal proof replay, numerical experiment or implementation reproduction. No public implementation was located in the inspected primary sources, which does not establish that none exists.
- **Source cache:** ignored `literature/corpus/pro_c/2611.26504v1/`.

**Main finding:** the paper gives a precise and useful resolvent construction on an invariant feature span. Its implemented spectral basis, however, evaluates a symmetrized state-action walk. That walk need not be the dynamics of any feasible policy in the original environment. The exact original-policy control guarantee therefore does not automatically cover the reported approximation. The continual-RL results also use supplied or directly observed state identities and unequal data/update budgets.

## 1. The exact reusable object

The underlying finite MDP has state-action nodes \(z=(s,a)\) and a fixed reference-policy transition matrix

\[
P^\pi((s,a),(s',a'))=P_{\rm env}(s'\mid s,a)\pi(a'\mid s').
\]

For \(0<\gamma<1\), its successor operator is

\[
R^\pi=(I-\gamma P^\pi)^{-1}
=\sum_{t\ge0}\gamma^t(P^\pi)^t.
\]

Let the columns of \(\Phi\) form an independent feature basis of a subspace \(U\). Section 2.1 establishes that the successor features remain in that same span exactly when \(U\) is invariant under \(P^\pi\). With the column-coordinate convention

\[
P^\pi\Phi=\Phi B,
\qquad
\Psi=R^\pi\Phi=\Phi(I-\gamma B)^{-1}.
\]

The converse also holds in finite dimensions. If the invertible resolvent maps \(U\) into itself, its restriction is injective and therefore onto \(U\). Its inverse preserves \(U\), and \(P^\pi=\gamma^{-1}(I-(R^\pi)^{-1})\) does too. This checks the source's equivalence, rather than assuming it from the eigenvector example.

For eigenfeatures \(P^\pi\phi_i=\lambda_i\phi_i\), the transform is diagonal:

\[
\psi_i=\theta_i\phi_i,
\qquad \theta_i=\frac1{1-\gamma\lambda_i}.
\]

If the immediate reward lies in the span, \(r=\Phi w\), the reference value is exactly

\[
Q^\pi=\Phi\operatorname{diag}(\theta_i)w.
\]

Changing the reward then requires changing only \(w\), provided the transition operator and its terminal convention stay fixed. This is the substantive reuse mechanism. It removes the need to learn a separate successor-feature network once the appropriate spectral objects are available. It does not remove the cost of obtaining those objects or establish that a small span captures arbitrary new rewards.

The shortcut \(w^*=\Phi^\top r\) stated on p. 5 assumes a Euclidean orthonormal basis and the corresponding full least-squares objective. The transformed Laplacian eigenfunctions below are generally orthonormal in a stationary-weighted inner product. Online visited-state regression, regularization and nonuniform sampling need not implement the full unweighted projection. Redundant features would also require care in the coordinate-resolvent formula. The selected independent eigenvectors avoid that particular problem.

## 2. Exact reference evaluation and control have separate requirements

Section 2.2 fixes \(\pi_{\rm ref}\) for computing values, while the acting policy is greedy in \(Q^{\pi_{\rm ref}}\). With exact action values, this is one ordinary policy-improvement step. It is not generally an optimal policy.

The stronger goal-reaching argument has a narrower interface. Assume deterministic transitions, a single positive goal reward, zero reward before reaching that goal, exact reference values and greedy action selection. At a nonterminal greedy step,

\[
\gamma V^{\pi_{\rm ref}}(s')
\ge V^{\pi_{\rm ref}}(s)>0.
\]

The reference value must grow by at least \(1/\gamma>1\) at each such step. Since it is bounded, a path starting where the reference policy can reach the goal cannot continue forever without reaching it. This argument is sound. It does not prove a general shortest-path result, a stochastic-transition analogue of this potential argument, or a guarantee for approximate values and epsilon-greedy actions.

The paper itself gives a countervailing example with mixed-sign rewards: a corridor containing negative lava rewards can look unfavorable under a random walk even when a good directed policy reaches a positive goal. Its experiment removes the lava, and the authors explicitly limit the one-step improvement mechanism.

There is a separate terminal-convention qualification. Section 3.1 makes goal entry terminate an episode, with random restarts and a 400-step cap. Exact episodic evaluation uses a killed kernel or an augmented absorbing state, so moving the terminal goal generally changes that evaluation operator. The text does not supply a complete terminal correction for the fixed spectral graph. This is an ambiguity in identifying the output with exact episodic \(Q\), not by itself a counterexample to reaching a single goal. An exact continuing physical-walk value with reward only on goal entry can still provide the same increasing pre-arrival potential. The unresolved symmetrization error below is a distinct issue.

## 3. Symmetrization changes which successor operator is exact

The state-action chain is normally nonsymmetric. Section 2.3 uses a strictly positive stationary distribution \(\rho\), writing \(D_\rho=\operatorname{diag}(\rho)\), and constructs

\[
L=I-\tfrac12\left(
D_\rho^{1/2}PD_\rho^{-1/2}
+D_\rho^{-1/2}P^\top D_\rho^{1/2}
\right).
\]

For orthonormal eigenvectors \(Lu_i=\mu_i u_i\), the functions \(\phi_i=D_\rho^{-1/2}u_i\) satisfy

\[
\bar P\phi_i=(1-\mu_i)\phi_i,
\qquad
\bar P=\tfrac12(P+D_\rho^{-1}P^\top D_\rho).
\]

Thus the analytic factor \(\theta_i=[1-\gamma(1-\mu_i)]^{-1}\) gives exact successor features of the **additive reversiblization \(\bar P\)**. The source explicitly says these are only approximate successor features of \(P\), on pp. 5–6 and again in §3.3.

The distinction matters for control. The reversed pair transitions generally fail to factor as

\[
P_{\rm env}(s'\mid s,a)\widetilde\pi(a'\mid s')
\]

for any feasible policy \(\widetilde\pi\) of the original environment. Consequently even a complete basis and perfect reward fit need not yield the action value of any original-environment policy. The usual policy-improvement theorem cannot simply be applied to \((I-\gamma\bar P)^{-1}r\).

The paper gives no operator-error estimate or action-gap condition transferring the exact guarantee to its symmetrized, truncated and estimated basis. Exactness is restored by reversibility, or on a selected invariant span where the original and surrogate operators agree. Those are additional conditions, not established properties of the experiments.

### A bounded independent error identity

For a fixed original stochastic or substochastic kernel \(P\), define

\[
q=(I-\gamma P)^{-1}r,
\qquad
\widetilde q=(I-\gamma\bar P)^{-1}\widehat r.
\]

Subtracting the two Bellman equations gives

\[
q-\widetilde q
=(I-\gamma P)^{-1}
\left[(r-\widehat r)+\gamma(P-\bar P)\widetilde q\right].
\]

Therefore

\[
\|q-\widetilde q\|_\infty
\le
\frac{\|r-\widehat r\|_\infty
+\gamma\|(P-\bar P)\widetilde q\|_\infty}{1-\gamma}.
\]

This is a local derivation in this note, not a theorem claimed or numerically certified by the authors. It separates reward approximation from operator mismatch and identifies the quantities a transfer argument would have to control. A uniform value error below half a strict action gap would preserve the relevant unique greedy action. No such gap or residual was measured in the paper. The statement presumes that both value problems have explicitly fixed compatible terminal conventions. For an approximate encoder or eigensolver, an additional residual \(e=(I-\gamma\bar P)\widetilde q-\widehat r\) contributes \(-e\) inside the brackets. The two-term identity is exact for retained exact eigenfeatures with \(\widehat r=\Phi w\), even with a truncated span.

## 4. What the state-only obstruction does establish

Section 2.4 considers a restricted representation that uses one state-only feature span for every action value, with action dependence placed in reward columns. Let \(P_{\mathcal S}=|\mathcal A|^{-1}\sum_a P_a\) and choose \(f\in U\), where \(U\) is invariant under \(P_{\mathcal S}\). For

\[
r=(I-\gamma P_{\mathcal S})f,
\]

the random-walk state value is \(f\), while

\[
Q^{\rm rw}(\cdot,a)=r+\gamma P_a f.
\]

To represent all such action values in \(U\), every \(P_a\) must preserve \(U\). Invariance under their average is insufficient. Walls provide a natural setting where the individual movement operators do not share the full eigenbasis used for their average.

This is a valid obstruction to the specified common-span readout. It is not a universal impossibility of state features. The complete state-function space is invariant under every action, some smaller subspaces can be jointly invariant, and action-conditioned successor heads or explicit lookahead lie outside this template.

Appendix E gives a second restricted-template failure. If no predecessor can enter the goal using action \(a\), that action's immediate-reward target is identically zero. Its separate least-squares reward column is zero, making the represented \(Q(\cdot,a)\) zero even though action \(a\) may be useful before later rewarding actions. The exact zero-column statement is about the stated least-squares solution, or a homogeneous zero-target update starting at zero. Arbitrary finite optimization from a nonzero initialization need not already attain it.

## 5. The estimated graph and retained resources

Section 2.5 observes transitions between \((s,a)\) and \((s',a')\). It forms either binary observed-edge weights or visit counts, then uses the undirected adjacency \(A=\widehat W+\widehat W^\top\) and degree-normalized Laplacian

\[
\widehat L=I-\widehat D^{-1/2}A\widehat D^{-1/2}.
\]

Its transformed eigenfunctions evaluate the random walk \(\widehat D^{-1}A\) exactly. Once all relevant transitions have been observed, binary weights recover equal weights on next actions. Count weights instead retain the behavior frequencies averaged over experience. Appendix D connects these to stationary additive reversiblization only under its empirical stationarity approximation, with goal terminations and restarts explicitly noted as exceptions. Before full coverage, the graph also incorporates the stated holding convention for untried pairs.

For the grid away from the goal, the completed binary pair graph has four incoming and four outgoing edges per node. This gives a uniform stationary law and the simpler \(\bar P=(P_{\rm rw}+P_{\rm rw}^\top)/2\) formula. That local regularity should not be silently extended through terminal/reset events.

The online method stores the observed graph over supplied cell-action identities and recomputes 128 eigenvectors. The basis is first built at 5,000 steps and rebuilt every 1,000 steps. The source aligns signs with the previous basis and carries reward coefficients unchanged. Sign alignment alone does not resolve rotations within repeated-eigenvalue spaces or eigenvector reordering at crossings. No quantified stability guarantee for this coordinate carryover is supplied.

Removing replay does not mean removing memory or computational cost. The graph, basis, eigenvalues and reward weights remain, and the paper does not give a finite-bit streaming state bound, graph-storage scaling experiment or end-to-end eigensolver timing comparison.

## 6. What the experiments support

The sole environment is the Inverted-L Walls grid, 12 by 12 with 84 free cells and four actions, hence 336 pair nodes. Lava is removed. Goal entry pays one and ends the episode. Two goals alternate every 250,000 steps, with the two-task sequence repeated for one million steps. Episodes start in a random cell and last at most 400 steps. Results use five seeds and shaded standard errors.

All agents use \(\gamma=0.99\). Epsilon is one for the first 5,000 steps and decreases to 0.1 by 25,000 steps, without reset at task changes.

| Agent | Information and representation | Material training conditions |
|---|---|---|
| DQN | 84 by 84 RGB pixels, learned CNN and value head | Batch 256, one update every 16 steps, learning begins 5,000 steps into each task. A 100,000-transition replay buffer is emptied at every goal change. |
| SimpleSF | Pixels, learned 128-dimensional base features and action-conditioned successor head | Same replay/reset/delay protocol. Network and reward weights have separate learning rates. |
| Offline Spectral-SF | Pixel encoder supervised against a supplied complete graph basis | An additional one-million-step uniform walk supplies the 336-node graph. All cell renders are used for 50,000 full-batch encoder updates before RL. The encoder is then frozen. |
| Online Spectral-SF | Direct cell identity and the graph of its own observations | Repeated eigendecomposition, 128 retained features, reward regression after each transition, no replay. |

Both spectral methods fit reward weights with Adam at 0.003 and an L2 penalty of 0.001, carrying weights across task switches. Offline encoder regression is weighted by \(\theta_i^2\), minimizing error in the scaled features. The reported fit is approximately \(10^{-6}\). DQN uses 10-step double-Q targets and a soft target update. Table 2 supplies the full architecture and optimizer details.

Figure 1 shows near-ceiling training returns for both spectral variants across the four task blocks. DQN and SimpleSF suffer large drops at goal changes under the reported protocol. Figure 2 shows a wall-sensitive approximate value field. Its scale is not a calibrated episodic-return certificate. Figure 3 favors binary over count graph weights, again with five-seed standard errors.

These observations support reuse on this supplied-state geometry. They do not isolate the cause of the baseline gaps under matched information, pretraining data, update frequency or replay-reset treatment. Section 4.1 explicitly acknowledges the privileged-information comparison. Its use of “bound” is an experimental interpretation, not a proved universal performance bound. The source says exact random-walk values induce shortest paths for these two goals, but this particular environment computation was not independently reproduced.

Learning the basis online from pixels with ALLO, scaling to varied environments, and adding a branch to evaluate the acting policy are future work in §4.2. They are not accomplished results of this edition.

## 7. Research disposition

Retain the invariant-span/resolvent identity as a precise representation tool. Its natural hypothesis is a fixed operator with a useful low-dimensional invariant span and a reward family represented within that span. Retain the distinction among original-policy values, reversible-surrogate values and acting-policy values.

For FP, this is an adjacent mathematical construction and a controlled reusable-representation example. The supplied finite state identities, graph storage and eigendecompositions prevent reading it as autonomous discovery of finite predictive states or a finite-memory learning guarantee. No FP object reduction or proposed architectural change is asserted. The neuroscience motivation is not used as independent evidence for FP.

**Completion boundary:** this arXiv edition is fully read. Implementation and experiments are unreproduced. The venue-specific edition, if different, has not received separate reading credit. No additional full-paper pass is pending.
