# Finite-Memory Control of POMDPs: Fundamental Limits and Efficient Design

## Source and reading record

- **Authors:** Emrecan Kutay, Atilla Eryilmaz and Ness Shroff.
- **Read edition:** [arXiv:2611.03414v1](https://arxiv.org/abs/2611.03414v1), submitted November 2, 2026, 16:38:33 UTC; [original PDF](https://arxiv.org/pdf/2611.03414v1), 42 physical pages; [complete source](https://arxiv.org/src/2611.03414v1). Only v1 was listed in the November 26 check.
- **Publication evidence:** the [official NeurIPS 2026 poster](https://neurips.cc/virtual/2026/poster/153239) authenticates this title and author list. The separately linked OpenReview PDF/supplement returned HTTP 403. The camera-ready-named arXiv source is the edition read; equivalence to a separate proceedings edition has not been established.
- **Local source:** `literature/corpus/arxiv/2611.03414v1/`, including `paper.pdf`, `source/CameraReady_v1.tex`, `source/checklist.tex` and `source/references.bib`.
- **Full reading, November 26, 2026, Shanghai:** complete main manuscript, every formula and proof in §§1–6 and Appendices A–F, acknowledgments, all checklist text, all 63 source bibliography entries and all 25 actually printed references. Main reader covered the complete 3,071-line manuscript, 223-line checklist and 742-line bibliography, counting each final line without a trailing newline. No cited paper receives full-reading credit merely from its citation here.
- **Original PDF coverage:** body pp. 1–10; funding p. 11; references pp. 11–12; A pp. 12–16; B pp. 16–17; C pp. 18–23; D pp. 23–27; E pp. 27–34; F p. 35; checklist pp. 36–42. All actual visual items were inspected: Figure 1 p. 6, Algorithm 1 p. 9 and Tables 1–2 pp. 10 and 35. Dense formulas were additionally checked on pp. 4–5, 7–8 and 30–31; p. 1's conference notice was inspected. There are no author footnotes; the p. 10 table note was read. Eleven selected original pages were inspected visually.
- **Verification level:** independent manual checks of the decision-witness reduction, tracking counting argument, regularized error recursion and exact-correction condition. The most consequential additional deduction is in §7 below. No complete theorem certification, formal proof, code audit or experimental replication was performed. This is an external-author paper, not an OpenAI or Anthropic release.

## 1. Original question and precise resource model

The paper asks how much discounted control value is necessarily lost when a known finite POMDP controller can carry only a finite label between observations, and how that label should be designed. It combines an information-theoretic converse, a special model with a matching bound, and RECAP, a predictive-prior quantization architecture with a conditional performance bound and empirical codebook optimization.

The environment supplies finite state, action and observation spaces, transition kernel, observation kernel, reward function, initial law and discount factor. Rewards satisfy \(0\le r(s,a)\le R_{\max}\); \(0<\gamma<1\). The full-information policy here means access to the complete *observation/action history*, not direct observation of the hidden state. Its sufficient statistic is the posterior belief \(b_t\).

A \(B\)-bit finite-state controller (FSC) has at most \(2^B\) persistent labels. Its action kernel can depend on the current observation \(Y_t\) and label \(Z_t\), and its update kernel on \(Z_t,Y_t,A_t\). The definition permits randomized and time-dependent kernels. At \(t\ge1\), \(Z_t\) has been formed before \(Y_t\) arrives; current \(Y_t\) is separately available. The objective is

\[
D_e(B)=V_e^*-\sup_{\kappa\in\Pi_B}V_e^\kappa.
\]

**What the budget charges:** persistent label cardinality. It does not charge the POMDP model, real-valued codebook, static action/update tables, pilot cloud or planner working memory. After fixing the model, codebook, tie-breaking and planner, the action and next label for each finite pair \((z,y)\) can be compiled into a lookup table, so the construction is an FSC in the stated sense. The result is not a claim that the complete implementation occupies \(B\) bits, nor a finite-precision theorem. All model-based calculations assume the supplied kernels; there is no unknown-model identification or sample-complexity theorem.

## 2. Decision witnesses and the converse

### Definition and statement

Definition 2 partitions belief space into labels \(\Theta_t=\psi(b_t)\in\{0\}\cup[N]\). Label zero is outside the witness. On the witness event

\[
E_t=\{\Theta_t\in[N],\ Y_t\in\mathcal Y_0\},
\]

each current observation \(y\in\mathcal Y_0\) has an **injective** map from witness labels to optimal actions. Any other action loses at least \(\eta>0\) in optimal action value, uniformly over the relevant reachable beliefs and controllers. In particular, \(N\le|\mathcal A|\).

For a fixed controller \(\kappa\), Theorem 1 lower-bounds its loss using

\[
\gamma^t\eta\Pr_e^\kappa(E_t)
\inf_{P_{\widetilde Z_t\mid\mathcal H_t}:\,|\widetilde{\mathcal Z}_t|\le2^B}
\left[
\frac{H_e^\kappa(\Theta_t\mid Y_t,E_t)
-I_e^\kappa(\Theta_t;\widetilde Z_t\mid Y_t,E_t)-1}{\log_2N}
\right]_+.
\]

If \(\Pr_e^\kappa(E_t)=0\), the complete displayed expression is defined to be zero, rather than requiring conditional information on a null event. The theorem then takes the appropriate infimum over controllers for \(D_e(B)\). Entropy, event probability and the joint law in the encoder problem remain controller-dependent. Appendix B's summed version retains \(\inf_\kappa\sum_t\gamma^t c_t^\kappa\); it does not interchange the infimum and sum or replace the actual occupancy by an optimal-policy occupancy.

### Proof structure, Appendix B

1. Write the discounted performance difference under the actual controller as the sum of Bellman residuals.
2. Condition on \((Z_t,Y_t)\). Fresh action randomization is independent of the true belief given this pair. Thus the best deterministic action for the conditional mean \(Q^*\) is at least as good as the actual randomized action.
3. Use the witness's injective action map to turn that action into a label decoder. Each decoding error on \(E_t\) incurs at least \(\eta\).
4. Apply Fano under the conditional law given \(E_t\).
5. Relax the actual recursive memory to an arbitrary stochastic encoder of \(\mathcal H_t\), then optimize. The actual conditional kernel \(P^\kappa(Z_t\mid\mathcal H_t)\) is feasible, even when the memory itself is randomized.

The relaxation includes current \(Y_t\) and imposes no consistency across times. This enlarges the encoder class and weakens the lower bound in the correct direction. It is not an implicit proof that the optimal relaxed encoder has a recursive implementation.

### Strength limits derived from the stated formula

- For \(N=2\), \(H(\Theta\mid Y,E)\le1\), so the printed Fano expression with the subtracted one is always zero. In particular, this formula alone cannot give a positive bound in a binary-action POMDP. A sharper counting argument can still do so.
- Once \(2^B\ge N\), the relaxed encoder can store the current label on \(E_t\), so the same expression is zero. Consequently, when \(2^B\ge|\mathcal A|\), this particular single-time witness/encoder converse cannot prove a positive memory gap. Computing that label recursively might require substantially more state, but the relaxation discards this requirement.
- Designing and optimizing a valid witness, and controlling its policy-dependent occupancy, remain substantive tasks. The theorem is a tool for lower bounds, not a general computable characterization of the entire memory/value curve.

These are limitations of this converse's strength, not errors in the conditional Fano proof.

## 3. The tracking example and exact sharpness regime

Appendix C considers a position \(X_t\) on \(\mathbb Z_K\), initialized as \(X_0\sim\operatorname{Unif}(\mathbb Z_K)\), with independent uniform increments in \(\{-m,\ldots,m\}\), \(m\ge1\), \(K\ge2m+1\). The controller guesses the current position and receives unit reward for a correct guess. Actions do not affect dynamics or observations. A reading is a beacon with probability \(q\), otherwise odometry; a reading is erased with probability \(p\). At time zero the position is revealed by a clean beacon.

A witness occurs when the most recent clean beacon has been followed entirely by clean odometry, with the current reading also odometry. Then the full history determines position exactly. Let

\[
\rho=(1-q)(1-p),\qquad
\alpha_t=\rho^t+q(1-p)\sum_{j=1}^{t-1}\rho^j.
\]

On each fixed-current-odometry slice, translation symmetry makes \(X_t\) uniform. A deterministic decoder of a \(2^B\)-valued label has at most \(2^B\) possible position outputs, irrespective of whether the label was randomized. This yields the stronger counting bound

\[
D_e(B)\ge\sum_{t\ge1}\gamma^t\alpha_t
\left(1-\frac{2^B}{K}\right)_+.
\]

When \(2^B\mid K\), the constructed FSC stores a position coset in a quotient of \(\mathbb Z_K\). On the clean-history witness slices, its pre-observation invariant is \(Z_t=q_G(X_{t-1})\), and current odometry advances it to the coset of \(X_t\) before the action. For \(p=0\) that invariant holds at every \(t\ge1\). Clean beacons reset it; erasures hold the memory fixed while the position still moves, so the invariant need not hold after an erasure before a fresh reliable beacon. The timing agrees with the formal FSC definition. The upper bound is

\[
D_e(B)\le\sum_{t\ge1}\gamma^t
\left[1-q(1-p)-\alpha_t\frac{2^B}{K}\right].
\]

For \(p=0\), \(\alpha_t=1-q\), and the upper and lower bounds coincide:

\[
D_e(B)=\frac{\gamma(1-q)}{1-\gamma}
\left(1-\frac{2^B}{K}\right),\qquad 2^B\mid K.
\]

The appendices also give the \(p\to0\) matching limit by dominated convergence. They do not establish exactness of the displayed coarse upper bound at arbitrary positive erasure probability. The finite cyclic transition and quotient action are supplied in this example; their discovery from data is not part of the result.

## 4. Two additional examples

### Appendix A: recursive counts versus recent windows

For \(B\ge3\), set the maximum packet age to \(L=2^B-1\). An observed age identifies position within a packet, whose hidden binary label is refreshed at resets. Each observed bit is a noisy version of that label. Parameters satisfy \(\epsilon<q<1/2\), with a positive reset probability and a forced reset at the maximum age. The observed age is free side information under the FSC definition.

The number \(C\in\{0,\ldots,L\}\) of positive observations since reset fits exactly within \(B\) bits. Together with the observed age \(G\), it gives posterior odds

\[
\frac{q}{1-q}\left(\frac{1-\epsilon}{\epsilon}\right)^{2C-G}.
\]

The unique MAP action is \(C>G/2+\alpha\), where

\[
\alpha=\frac{\log((1-q)/q)}{2\log((1-\epsilon)/\epsilon)}\in(0,1/2).
\]

The count controller is globally optimal. For equal-budget windows of the last \(B\) observations, or the last \(\lfloor B/2\rfloor\) observation/action pairs, the proof constructs positive-probability histories with identical windows but distinct MAP actions. For the action-window class, the argument uses the fact that global optimality forces the earlier actions in these histories; actions cannot secretly supply the missing distinction. The \(B=3\) construction is handled separately. Compactness of the policy-kernel product space and uniform discounted-tail continuity ensure attainment, converting the failure of every globally optimal window policy into a strict gap in the corresponding suprema.

This is a specific counterexample to these two window classes. It does not show that arbitrary \(B\)-bit FSCs fail; the counterexample deliberately contains an optimal one. Its observed age and bounded packet length are essential parts of the information budget.

### Appendix D: identifying a temporarily fixed hidden source

There are \(K\) distinct Bernoulli sources with known parameters, a visible age capped at \(n\), and a hidden source that changes at resets. A correct source guess at age \(\tau\) earns \(v(\tau)\). The proof restricts to the first \(n\) steps without a source change, of probability \((1-\alpha)^{n-1}\), where the initial source is uniform.

Choose a separation width \(\delta\) and a positive likelihood-ratio exponent \(\xi\), with \(a_n=(K-1)2^{-n\xi}<1\). Hoeffding gives good empirical-frequency probability at least \(1-2e^{-2n\delta^2}\), and the likelihood ratio makes the posterior's winning action separated by at least \(v(n)(1-a_n)/(1+a_n)\). The current binary observation costs at most one bit of the uncertainty. Fano contributes its extra one, giving

\[
D_e(B)\ge\gamma^{n-1}(1-\alpha)^{n-1}v(n)
\frac{1-a_n}{1+a_n}
\left[1-2e^{-2n\delta^2}-\frac{B+2}{\log_2K}\right]_+.
\]

Here \(\delta\) is an empirical-frequency width, not RECAP's later regularization strength. The lower bound pays both the no-reset probability and discount to the decision time. It is not a uniform source-learning or state-formation rate.

## 5. RECAP's predictive-prior architecture

RECAP retains a codebook label \(z\) for a predictive prior \(\bar c_z\), rather than a posterior. Its cycle is correction by current observation, action selection, prediction under the chosen action, and recompression. The finite model and all representatives are fixed.

For a full-support anchor \(\nu\), define prior smoothing

\[
S_\delta(\bar b)=(1-\delta)\bar b+\delta\nu,
\quad C_{y,\delta}(\bar b)=C_y(S_\delta(\bar b)).
\]

The quantizer selects a nearest-TV representative among those that preserve the input prior's feasible observations, using deterministic tie-breaking. If none is compatible, it falls back to a global nearest representative. The source's general notation explicitly supplies a fixed full-support fallback for zero-denominator Bayes maps; these maps are not left undefined. Appendix E uses the anchor on globally impossible observations.

Initialization is \(Z_0=\operatorname{enc}(\xi_e)\). At time \(t\), the controller computes \(\widehat b_t=C_{Y_t,\delta}(\bar c_{Z_t})\), selects the planner's greedy action, predicts with the known transition kernel and encodes the resulting prior. The current observation is not stored as an extra unconstrained persistent state.

The observation compatibility rule and regularization have different roles. Compatibility avoids representatives excluding observations that the approximated prior permits. Positive smoothing gives a global likelihood floor and a finite correction sensitivity; it also introduces bias.

## 6. The regularized performance bound and its proof

Write \(p(y\mid\bar b)\) for observation likelihood. The theorem's constants are

\[
\beta_\delta=
\sup_{y,\bar b:p(y\mid\bar b)>0}
\operatorname{TV}(C_{y,0}(\bar b),C_{y,\delta}(\bar b)),
\quad
\Lambda_\delta=
\max_{y:p(y\mid\nu)>0}\frac{2(1-\delta)}{\delta p(y\mid\nu)}.
\]

Let \(e_0\) be initial predictive-prior quantization error, and \(\bar\eta\) the worst TV error when recompressing a one-step prediction from any codebook state and observation under the chosen planner. The written \(\bar\eta\) supremum includes all observations, using the declared fallback maps. The planner in Theorem 2 is the exact optimal \(H\)-stage planner with **zero terminal value**, whose uniform truncation error is

\[
\varepsilon_H=\frac{\gamma^H R_{\max}}{1-\gamma}.
\]

For \(0<\delta\le1\), if **\(\gamma\Lambda_\delta<1\)**, Theorem 2 gives

\[
V_e^*-V_e^{\kappa_{\mathcal C,\delta}}
\le \frac{2\varepsilon_H}{1-\gamma}
+\frac{4R_{\max}}{1-\gamma}
\left[
\frac{\beta_\delta}{1-\gamma}
+\Lambda_\delta\left(
\frac{e_0}{1-\gamma\Lambda_\delta}
+\frac{\gamma(\beta_\delta+\bar\eta)}
{(1-\gamma)(1-\gamma\Lambda_\delta)}
\right)\right].
\]

This upper-bounds \(D_e(B)\) as well, because the constructed controller belongs to \(\Pi_B\). It need not be numerically informative: it may exceed the trivial value range.

Appendix E supplies each interface. Prediction is TV nonexpansive **under the same realized action**. The fixed-action optimal \(Q\)-function has the stated TV Lipschitz bound \(2R_{\max}/(1-\gamma)\). Comparing true and approximate greedy actions yields the per-step residual

\[
V^*(b_t)-Q^*(b_t,A_t)
\le 2\varepsilon_H+\frac{4R_{\max}}{1-\gamma}d_t.
\]

Along the actual RECAP history, predictive error \(e_t\) and posterior error \(d_t\) obey

\[
d_t\le\beta_\delta+\Lambda_\delta e_t,
\qquad e_{t+1}\le\Lambda_\delta e_t+\beta_\delta+\bar\eta.
\]

Summing the discounted recursion and dividing by \(1-\gamma\Lambda_\delta>0\) gives the theorem. Actual-controller occupancy is retained throughout. The argument never compares two transition kernels with independently chosen actions or silently substitutes an optimal-policy trajectory. Bounded manual inspection found no algebraic obstruction in this conditional regularized result.

### Pointwise small bias is not a uniform small-bias theorem

Proposition 9 proves convergence to exact Bayes for each *fixed positive-likelihood* prior/observation pair as \(\delta\to0\). It does not prove \(\beta_\delta\to0\), since \(\beta_\delta\) is a supremum over priors with arbitrarily small likelihoods.

For a direct illustration, take three states, an observation with likelihoods \((1,1,0)\), uniform anchor and priors \((\epsilon,0,1-\epsilon)\). Exact correction is the first point mass. For every fixed positive \(\delta\), regularized correction approaches \((1/2,1/2,0)\) as \(\epsilon\downarrow0\). Hence \(\beta_\delta\ge1/2\) for every positive \(\delta\) in this valid model. This independently checked example is consistent with the paper's pointwise proposition; it prevents an unjustified strengthening of that proposition.

## 7. A substantive limitation of the exact-correction tube condition

Appendix E also presents a sufficient local tube for \(\delta=0\), followed by an exact-correction performance bound. Definition 5 assigns each codebook state a radius \(\rho(z)\). For every non-exempt branch it requires

\[
p(y\mid\bar c_z)-\rho(z)>0,\qquad
\Lambda\ge\frac{2}{p(y\mid\bar c_z)-\rho(z)},\qquad
\rho(z')\ge\Lambda\rho(z)+\eta_0(z,y).
\]

The exemption is only when \(p(y\mid\bar c_z)+\rho(z)=0\). Initialization must lie in its assigned tube. The original PDF was checked against these signs and constants.

**Additional deduction: these written conditions force every radius to be zero.** Let \(M=\max_z\rho(z)\), attained since the codebook is finite, and choose an attaining state and any observation having positive likelihood there. If \(M>0\), the branch is not exempt. Its positive denominator is at most one, so \(\Lambda\ge2\). Since reprojection errors are nonnegative,

\[
M\ge\rho(z')\ge\Lambda M+\eta_0(z,y)\ge2M>M,
\]

a contradiction. Thus \(\rho\equiv0\), initial error is zero, and \(\eta_0(z,y)=0\) on every branch feasible at its representative. The actual controller path consequently has exact predictive/posterior representation and exact closure. This does **not** imply that the literal all-observation supremum \(\bar\eta_{\mathcal C,0}\) is zero on impossible fallback branches.

The condition therefore certifies exact initialization and closure on feasible branches, not a nonzero quantization neighborhood. Its additional requirement \(\gamma\Lambda<1\) also entails \(\gamma<1/2\), often more restrictive. The tube induction remains logically valid conditional on feasibility; the issue is the severe limitation of the sufficient condition itself. This does not refute Theorem 2 for positive regularization. No replacement tube theorem or FP theory change is proposed here.

## 8. The practical codebook objective and search

The codebook consists of at most \(2^B\) medoids from a finite pilot cloud. The objective combines three empirical terms:

- **Predictive coverage:** average TV distance from pilot priors to their representatives.
- **Recursive closure:** pilot/observation-weighted discrepancy between the next predictive prior from the pilot's exact posterior and the recursively quantized prediction from its representative, both under the same representative-induced action.
- **Action regret:** pilot/observation-weighted truncated-planner \(Q\)-loss from the representative's induced action compared with the planner action on the pilot posterior.

The implementation description uses weights \(0.2,0.3,0.5\), action-term normalization by a pilot \(Q\)-span, and a \(10^6\) incompatibility penalty. Farthest-first TV \(k\)-center initializes the medoids. Sequential candidate replacements strictly reduce the score; at most 64 candidates per representative are considered per pass, with at most 16 passes and stopping after three non-improving passes. Finite candidates and strict improvement give termination, not global optimality.

The stated \(O(I_{\max}K m_{\rm cap})\) is a count of **objective evaluations**. Evaluations themselves involve pilot points, branches, filtering, representative assignment and planner calls. It is not total arithmetic complexity or total working-memory complexity. Appendix F explicitly acknowledges exponential dependence of the strict planner on horizon and observation branching.

The finite-cloud average objective is motivated by the converse and error decomposition, but it is not the theorem's worst-case bound. No result converts its empirical closure average to \(\sup_{z,y}\eta(z,y)\), proves pilot coverage of future occupancy, or guarantees that each score decrease reduces true discounted loss.

## 9. Experiments, observed results and applicability limits

### Protocol

The authors report eleven POMDP.org benchmarks, budgets \(B=2,3,4\), three independent design seeds and 1,000 evaluation episodes per seed, each truncated at length 128. Table 1 reports mean and pooled standard deviation across the 3,000 episodes and seeds. These are not standard errors or confidence intervals; no paired significance test is supplied. For most method/benchmark pairs, the reported seed-level variability in mean return is below 20% of the pooled deviation.

All quantization methods use the same runtime correction/action architecture and budget. Comparators are predictive TV \(k\)-center, predictive \(k\)-medoids, value-feature \(k\)-medoids, recursive-feature \(k\)-medoids, a Dirichlet simplex codebook and a finite observation window. The full-belief planner is a separate unbudgeted reference, not a certified \(V^*\).

Appendix F specifies 256 pilot predictive priors: 30% deterministic branch expansion of depth two, keeping the top three positive-probability observations and dropping branches below \(10^{-8}\); 30% planner-guided epsilon-greedy rollouts, epsilon 0.15 and horizon 32; and 40% random-action rollouts. The planner uses **50 PBVI iterations as a terminal estimate plus exact depth-three lookahead**. Regularization is \(\delta=0.02\) with uniform anchor throughout, and the reported design hyperparameters are shared across instances.

The stated hardware is a single Intel i9-13950HX machine with 32 GB RAM and no GPU. Reported per-benchmark CPU time spans roughly 0.2–13 hours, with about 25 CPU hours for the suite. No implementation was executed in this reading.

### Table 1 result extraction

The table below condenses the paper's reported means. The original table and its standard-deviation interpretation were read; the strongest comparator can differ across rows.

| Benchmark | B | RECAP mean ± pooled SD | Best other budgeted mean | Full-belief mean |
|---|---:|---:|---:|---:|
| paint | 2 | 3.30 ± 1.81 | 3.30 | 3.30 |
| marking | 2 | 2.73 ± 0.55 | 2.58 | 2.75 |
| saci_s12 | 2 | 14.65 ± 7.81 | 14.65 | 14.65 |
| line4_2goals | 2 | 0.47 ± 0.57 | 0.47 | 0.47 |
| shuttle | 3 | 32.94 ± 4.81 | 28.23 | 32.94 |
| network | 3 | 272.62 ± 181.09 | 275.60 | 290.10 |
| 1d_noisy | 3 | 1.11 ± 0.43 | 1.24 | 1.24 |
| query_s2 | 3 | 355.80 ± 36.12 | 355.43 | 356.43 |
| mini_hall2 | 4 | 2.72 ± 0.57 | 2.72 | 2.72 |
| 4x4 | 4 | 3.71 ± 0.48 | 1.48 | 3.73 |
| 4x5x2 | 4 | 0.60 ± 0.79 | 0.10 | 2.08 |

RECAP leads or ties the best budgeted comparator in nine rows and is second in network and 1d_noisy. Its gap to the unbudgeted reference remains substantial on 4x5x2. The comparisons support this implemented codebook design on these tasks; they neither trace the full optimal memory/value curve nor prove generally superior optimization. Feature-only comparators probe useful alternatives, but their optimizer differences mean the table is not a clean exhaustive ablation of every objective term.

### The experiments do not supply a numerical certificate for Theorem 2

1. With \(m_{\min}=\min_{y:p(y\mid\nu)>0}p(y\mid\nu)\), the printed global sensitivity at \(\delta=0.02\) is \(\Lambda_\delta=98/m_{\min}\ge98\). The theorem therefore requires at least \(\gamma<1/98\). If there are \(q\) globally feasible observation symbols, \(m_{\min}\le1/q\), giving the necessary restriction \(\gamma<1/(98q)\). The manuscript does not give the individual benchmark discounts or a sharper local certificate. Thus this reading does not establish that any named benchmark violates the condition, but also does not establish that the experimental settings satisfy it.
2. PBVI-terminal lookahead differs from the zero-terminal optimal \(H\)-stage planner used for \(\varepsilon_H\). Its terminal-value error needs separate control before importing that numerical bound.
3. Pilot averages and the reported returns do not certify the theorem's worst-branch errors. No occupancy/generalization conversion is supplied.
4. Some baseline returns are negative, while the theoretical model assumes nonnegative rewards. A reward shift could reconcile bounded rewards, but no explicit experimental normalization is authenticated in the manuscript. This is a missing application interface, not a counterexample to a theorem with explicit reward assumptions.

The [author-linked repository](https://github.com/RECAP-research/RECAP/tree/35604fb937e6abede0a38c714ce64bac6eef6999) was authenticated at the pinned May 6 commit. Its root listing and full README were inspected during source preparation; implementation files, benchmark discounts and experimental outputs were not inspected. The checklist's reproducibility answers are author statements, not independent reproduction evidence.

## 10. Dependencies, disclosures and remaining questions

The converse uses discounted performance difference, conditional Fano and a purpose-built action margin. The examples additionally use finite-group symmetry, counting, compactness/discount continuity, likelihood ratios and Hoeffding. The upper bound uses stochastic-kernel TV nonexpansion, finite-horizon truncation, a Bayes normalization inequality and a stable scalar discounted recursion. These are the argument's main mathematical dependencies.

The related-work comparison distinguishes bounded FSC synthesis, approximate information states, value-directed belief compression, asymptotic finite-model/finite-memory approximation and sensor-information lower bounds. Printed references include Smallwood–Sondik, Kaelbling–Littman–Cassandra, Poupart–Boutilier, Majumdar–Mei–Pacelli, Subramanian et al., Kara–Yüksel, Saldi–Yüksel–Linder and others. Their cited roles were read here; this note does not independently authenticate every novelty comparison or read all 25 source papers. The larger BibTeX inventory contains unused entries and some inconsistent metadata; it must not be mistaken for the printed reference list.

The acknowledgments disclose US Army, NSF and ONR support. The checklist states that LLMs were used only for writing assistance, and not as a methodological component. It reports no human-subject research. These are recorded as author disclosures, without additional investigation.

Concrete open points are the full rate/distortion curve beyond the special tracking model, witness selection under controller-dependent occupancy, a nondegenerate exact-correction robustness condition, sharper local correction constants, pilot-to-runtime error control, terminal-planner certification, and the cost of model/codebook storage and computation beyond the persistent label. A separate source/code inspection would be required to determine the eleven benchmark discounts and reward conventions. No FP transfer is asserted: neither a supplied-model POMDP codebook nor a known cyclic quotient establishes learning unknown token updates, generating new state addresses, or preserving individual-continuation log loss after posterior pruning.
