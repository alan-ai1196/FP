# AI in a vat: predictive world models, realization size and interface boundaries

## Source, edition and actual reading

- **Authors:** Fernando E. Rosas, Alexander Boyd and Manuel Baltieri.
- **Completed edition:** [Reinforcement Learning Journal 6:2844–2881, 2025](https://rlj.org/papers/rosas2025fundamental), presented at RLC 2025, August 5–9. [Official 38-page PDF](https://rlj.cs.umass.edu/2025/papers/RLJ_RLC_2025_367.pdf), including the cover. Page references below are physical PDF pages, including that cover. The supplementary-material heading on p. 20 explicitly says that this content was not necessarily subject to peer review.
- **Full reading by Pro-C, November 26, 2026, Shanghai:** all 38 pages, main §§1–7, Appendices A–Q, all statements, proofs, formulas and ten footnotes, all five numbered figures including the three examples in Figure 4 and four panels of Figure 5, acknowledgements and all 99 printed references. There are no numbered tables, algorithm boxes or empirical experiments. The complete official PDF extraction was read in consecutive blocks. Embedded LaTeXiT annotation payloads were removed from a reading copy without changing scientific prose. Original pp. 4–12, 20, 25, 27, 29–30, 32–33 and 38 were visually inspected, 17 pages in total.
- **Separate author edition:** [arXiv:2504.04608v1](https://arxiv.org/abs/2504.04608v1), April 6, 2025, 20:35:44 UTC, also 38 pages. This remains the latest arXiv version at the source check. Its complete source package has one active main.tex, 98 compiled references and Appendices A–S. Source inventory and selected section comparisons were performed, not a second full reading. The official edition adds Castro 2011, changes §5 and has no separate counterparts to the v1 Appendix J on reduction algorithms or Appendix P on a canonical retrodictive model. Later appendices and equations are renumbered. Equal page counts do not establish edition identity.
- **Scoped dependency:** Çakır, Saleemi and Zimmermann, [On the Theory of Stochastic Automata, arXiv:2103.14423v1](https://arxiv.org/abs/2103.14423v1), March 26, 2021, 50 pages. Read selected definitions in §2 and physical pp. 10–11, 13 and 20, including the state-distribution equivalence definitions, the meaning of reduced, Proposition 4.1, the statement and beginning of Theorem 4.2, Theorem 4.8 and Corollary 4.9 with proof. Original pp. 11, 13 and 20 were visually inspected. This is a targeted dependency check, not a full reading or verification of that survey.
- **Verification boundary:** bounded independent checks of the joint-kernel reduction, two finite realization examples, the predictive-state proof interface, Bayesian timing and the card illustration. Assisting readers independently checked selected definitions and proof steps. No exhaustive theorem audit, formal proof, proof script, implementation benchmark or experiment reproduction. No AI assistance disclosure was located in the read edition. Ignored source cache: literature/corpus/pro_c/rosas2025fundamental/.

**Main finding:** the useful organizing idea is to preserve the entire action–outcome interface while comparing different internal generators. Known-model Bayesian beliefs and equivalence classes of histories supply predictive representations. These are exact representation constructions, with potentially infinite state sets. The printed general Mealy bisimulation condition loses an output–successor correlation. Theorem 1 changes from statewise behavior to one fixed initial interface, and Theorem 2 imports a linear reduction into a time-dependent setting without the required common invariance. Explicit small examples delimit those claims. Predictive-state minimality, numerical representation dimension, sampling and installed memory must remain separate.

## 1. The interface and what is held fixed

Definition 1, p. 4, specifies an interface by the family

\[
\mathcal I(Y\mid A)=\{p(y_{0:t}\mid a_{0:\infty}):t\geq0,\ a_{0:\infty}\in\mathcal A^{\mathbb N}\}.
\]

Anticipation freedom means that the prefix law depends only on \(a_{0:t}\). The direct quantifier is over **all external action sequences**, rather than over one behavior policy or a distribution of visited tests. Initial conditions are part of the interface. A world model is an auxiliary process whose current state and action screen the present outcome from earlier history, while future inputs do not change past states. Its update may initially depend on the whole state and observation history. Lemma 1 gives the corresponding factorization.

Definition 3, p. 5, restricts to a transducer with

\[
\kappa_t(y,s'\mid a,s),\qquad p_0\in\Delta(\mathcal S),
\]

where the kernel explicitly permits dependence on time. State \(S_t\) is present before action \(A_t\). The kernel jointly emits \(Y_t\) and chooses \(S_{t+1}\). This is a Mealy interface, and the correlation between the two outputs of that kernel matters. For finite \(n=|\mathcal S|\), let

\[
[T_t^{y\mid a}]_{ij}=\kappa_t(y,s_i\mid a,s_j).
\]

With column state vectors, chronological products mean

\[
p(y_{0:t}\mid a_{0:t})
=\mathbf1^\top T_t^{y_t\mid a_t}\cdots T_0^{y_0\mid a_0}p_0.
\]

The paper's three special classes, p. 6, are worth retaining exactly:

| Class | Kernel factorization | Constraint |
|---|---|---|
| Input-Moore | \(\mu_t(y\mid s)\nu_t(s'\mid y,a,s)\) | The current outcome ignores the current action |
| Output-Moore | \(\mu_t(y\mid a,s)\nu_t(s'\mid a,s)\) | The next state ignores the sampled current outcome, conditional on current state and action |
| I–O Moore | \(\mu_t(y\mid s)\nu_t(s'\mid a,s)\) | Both constraints |

Appendix F, Eq. (33), includes reward in the outcome and writes \(\mu(o\mid s)\rho(r\mid s,a)\tau(s'\mid s,a)\). This is generally output-Moore. Its printed I–O Moore label additionally needs the reward law to be action independent, or a different declared outcome interface.

### Closing the loop is a separate interpretation step

If the interface laws are interpreted as externally specified causal channel kernels, then equality of those kernels extends to a common causal randomized policy by multiplying by the same factors \(\pi_t(a_t\mid h_{0:t-1})\). This is an elementary inference from the interface, provided that the policy has no hidden-state side channel and its private randomness is appropriately independent.

It is not valid to identify this open-loop kernel with the ordinary conditional distribution of an adaptively generated trajectory given its entire action tape. Future actions may encode past outcomes. Appendix J, Eq. (47), explicitly uses current-action history measurability. Appendix P, footnote 10, and the final paragraph of Appendix Q separately flag independence of the initial state from future inputs. These assumptions should not be silently exchanged.

The manuscript uses sets, sums, discrete entropy and finite matrices where needed. It does not provide a general measurable-space theorem covering arbitrary continuous observations. Its positive-probability convention also excludes undefined conditionals on null histories.

## 2. Exact reduction needs the joint outcome–successor law

Definition 4, p. 7, defines a reduction by a surjective state map \(\phi\), with actions and outcomes unchanged. It preserves the outcome law and the next abstract-state law **conditional on the current outcome**. Together with the pushed-forward initial law, this is an appropriate exact compatibility condition. Lemma 5 and Appendix H use it to preserve the whole interface.

Definition 5 instead requires only equal outcome marginals and equal next-class marginals:

\[
\sum_{s'}\kappa_t(y,s'\mid a,s)
=\sum_{s'}\kappa_t(y,s'\mid a,\tilde s),
\]

\[
\sum_y\sum_{s'\in C}\kappa_t(y,s'\mid a,s)
=\sum_y\sum_{s'\in C}\kappa_t(y,s'\mid a,\tilde s).
\]

These two marginals do not determine the joint law of \((Y_t,[S_{t+1}])\). Proposition 1's converse therefore fails for the general Mealy class as printed.

### Four-state counterexample

Use one action, outcomes \(0,1\), and states \(p,q,u,v\). The nonzero kernel entries are

| Current state | Joint outcome and next state | Probability |
|---|---|---:|
| \(p\) | \((0,u)\), \((1,v)\) | \(1/2\) each |
| \(q\) | \((0,v)\), \((1,u)\) | \(1/2\) each |
| \(u\) | \((0,u)\) | 1 |
| \(v\) | \((1,v)\) | 1 |

For the partition \(\{p,q\},\{u\},\{v\}\), states \(p,q\) have the same fair output law and the same half–half next-class law. Thus Definition 5 is satisfied. After outcome 0, however, \(p\) goes to \(u\) and \(q\) goes to \(v\). Definition 4 cannot hold for this quotient. Their two-output laws also differ: \(p\) produces 00 or 11, whereas \(q\) produces 01 or 10. Both can be assigned positive initial probability, so this is not a null-state issue.

Appendix I, p. 27, Eq. (42), makes the unsupported step by replacing a conditional-on-\(y\) next-class probability using a hypothesis that only sums over \(y\).

**Repair:** require equality of \(\sum_{s'\in C}\kappa_t(y,s'\mid a,s)\) for each \(y,C\). Alternatively, impose an appropriate output-Moore conditional independence. The example refutes the stated equivalence between Definitions 4 and 5. It does not assert that a particular initial mixture has no other smaller presentation.

## 3. Canonical dimension and a fixed initial distribution are different problems

On pp. 7–8 the paper defines a vector for each action–outcome word, with one coordinate per possible **starting state**:

\[
w(h_{0:t})_i
=p(y_{0:t}\mid a_{0:t},S_0=s_i),
\qquad
d(\mathcal T)=\dim\operatorname{span}\{w(h_{0:t})\}.
\]

Theorem 1 says that \(d=n\) rules out every smaller transducer generating the same interface. That interface already has a fixed \(p_0\). Statewise distinguishability does not establish this claim.

### A full-support, fully reachable two-state example

Take \(\mathcal S=\{0,1\}\), one action and \(p_0=(1/2,1/2)\). Let

\[
\kappa(y,s'\mid s)=\frac12\mathbf1\{y=s\}.
\]

Each step outputs the current state and redraws the next state as a fresh fair bit. Consequently, the observed process is an independent fair coin at every time and has a one-state transducer realization. Both hidden states have positive probability at every time.

Nevertheless,

\[
w(Y_0=0)=e_0,\qquad w(Y_0=1)=e_1,
\]

so the printed dimension is \(d=n=2\). This directly contradicts Theorem 1's fixed-interface conclusion. Adding reachability alone does not repair it.

### What the cited source actually supplies

The paper points to Çakır et al., Corollary 4.9, for the proof. The [primary source](https://arxiv.org/pdf/2103.14423v1), physical p. 20, states that full dimension makes the automaton **reduced**. On physical p. 13, reduced means that no two distinct states are behaviorally equivalent. Its Proposition 4.1 compares reduced automata under equality of the entire family of pure-state behaviors, called S-equivalence. Physical pp. 10–11 also distinguish the family induced by all initial distributions from one selected initial distribution.

The two-state example is reduced in this sense. Its two pure-state first outputs differ. Its selected fair mixture nevertheless has a smaller realization. Thus the citation does not support the stronger quantifier change. A fixed-interface minimal realization requires the corresponding reachable and observable behavior object, such as an appropriately defined Hankel construction, rather than this statewise rank alone. No general replacement theorem was independently certified here.

## 4. Time dependence also limits the claimed linear reduction

Definition 6 allows signed real matrices and boundary vectors whose products reproduce valid external word probabilities. Theorem 2, p. 9, says that \(d<n\) always permits a linear transformation to a smaller realization. The paper's kernels explicitly depend on time, while its \(d\) only compares behaviors starting at time zero. A common invariant unobservable subspace does not follow from that comparison.

### Two states with a later persistent bit

Use one action and two states. At time 0, emit 0 and choose \(S_1\) as a fresh fair bit, independently of \(S_0\). At every later time, keep that bit forever and emit it. The entire future law from either possible \(S_0\) is identical, so all time-zero result vectors are multiples of \((1,1)\), and \(d=1<n=2\).

But the three-output probabilities satisfy

\[
p(000)=p(011)=\tfrac12,
\qquad p(001)=p(010)=0.
\]

Any one-dimensional signed time-dependent linear realization would factor each probability as

\[
u\,a_2(y_2)a_1(y_1)a_0(y_0)v.
\]

The two positive diagonal probabilities force the factors for both values at times 1 and 2 to be nonzero. The off-diagonal products then cannot vanish. Equivalently, the time-1/time-2 probability matrix has rank two, whereas a scalar realization has rank one. Thus the claimed reduction to one dimension is impossible even allowing signed coordinates.

This is a counterexample to applying the printed time-zero dimension to the stated time-dependent class. It does not refute homogeneous linear realization theory. A repair needs homogeneous/common-invariance assumptions or a dimension notion that accounts for the relevant time cuts and reachable conditional behaviors. The imported historical proofs were not fully reread.

### What a signed representation does and does not buy

Negative internal components need not admit a sampling interpretation as probabilities of internal states. If the representation nevertheless yields a valid anticipation-free controlled output law \(Q\), then on a positive-probability history,

\[
P(Y_t=y_t\mid h_{0:t-1},a_t)
=\frac{Q(y_{0:t}\mid a_{0:t})}
{Q(y_{0:t-1}\mid a_{0:t-1})}.
\]

The numerator is a controlled output probability, not a joint probability of sampled actions and outcomes. Thus lack of sampleable internal trajectories does not by itself prove that outputs cannot be generated.

The number of linear coordinates is not a bound on numerical precision, parameter description length, cancellation error or runtime. Nor does it automatically bound entropy or installed bits. The claim of minimal computational complexity following Theorem 2 is stronger than the representation statement, even after its hypotheses are repaired. Figure 3's global-minimum interpretation must retain both this distinction and the preceding counterexamples.

## 5. Predictive, observable and unifilar representations

Section 5 uses three different properties:

| Property | Definition and initialization boundary |
|---|---|
| Predictive | \(I(S_t\mathbin{;}Y_{t:\infty}\mid H_{0:t-1},A_{t:\infty})=0\). State adds no future-output information once observed history and future inputs are given |
| Observable | \(S_{t+1}=f_t(H_{0:t})\), a deterministic function of observed history |
| Unifilar | \(S_{t+1}=\widehat f_t(S_t,A_t,Y_t)\). A known deterministic initial state makes this directly observable |

Predictive does not imply that the state is determined by history. Independent random nuisance state can satisfy the predictive condition while retaining a nondegenerate posterior. This matters for the proof of Theorem 3 below.

### Known-model Bayesian prediction is a valid construction

Definition 7 and Proposition 2 use

\[
b_t(s)=P(S_t=s\mid H_{0:t-1}),
\qquad
b_{t+1}(s')
=\frac{\sum_s\kappa_t(y_t,s'\mid a_t,s)b_t(s)}
{\mathbf1^\top T_t^{y_t\mid a_t}b_t}.
\]

The denominator is the next-output probability. On positive-probability updates, the belief transition is deterministic given current belief, action and observed output, so it is unifilar. With the correct supplied model and \(b_0=p_0\), Appendix J shows equality of the generated interface.

This construction has no estimator for an unknown kernel, exploration guarantee, finite-data rate, optimization convergence or numeric-precision budget. A simplex with finitely many coordinates generally contains infinitely many reachable belief states. Calling the update available in real time is a structural recursion claim, not a proved practical runtime or statistical learnability bound.

### Postdictive beliefs need a consistent timing convention

For an I–O Moore model, the paper defines

\[
d_t(s)=P(S_t=s\mid Y_{0:t},A_{0:t-1}).
\]

Its Eq. (9) is the usual posterior-to-posterior recursion

\[
d_{t+1}(s')\propto\mu_{t+1}(y_{t+1}\mid s')
\sum_s\nu_t(s'\mid a_t,s)d_t(s).
\]

The recursion itself is valid. Proposition 3 also says that faithfulness follows from \(d_0=p_0\), which conflates a pre-output prior with the already updated \(P(S_0\mid Y_0)\). When \(Y_0=S_0\) and \(p_0\) is nondegenerate, the latter is a point mass and cannot equal the prior.

Appendix K actually shifts the interface so that step \(\tau\) takes \(a_{\tau-1}\), produces \(y_\tau\), and reaches the posterior \(d_\tau\). A consistent construction starts with \(p_0\) **before** generating \(Y_0\), then applies the first emission update. Its initial emission-only matrix should be \(\operatorname{diag}(\mu_0(y\mid s))\). Printed Eq. (57), p. 29, instead fills every row of each column with the same emission probability, omitting the state-preserving Kronecker delta. Summing over successor states and outputs then gives \(n\), not one. Normalizing that matrix would lose the initial state information.

Eq. (65), p. 30, additionally reverses the paper's \(b,d\) naming. Under the main-text definitions, the order is predictive prior \(b_t\), observation update to \(d_t\), then action-conditioned state prediction to \(b_{t+1}\). These are local initialization and indexing repairs, not a rejection of Bayesian filtering.

## 6. Future equivalence supplies a canonical predictive statistic

Eq. (10), p. 10, identifies two observed histories when they give the same law for every finite future output sequence under every future input sequence. Write the class as

\[
M_t=\epsilon_t(H_{0:t-1}).
\]

On reachable histories and positive-probability extensions, equality of all future laws is stable under appending the same action–outcome pair. The resulting class update is deterministic, and its next-output law is well defined. This is the useful content of the \(\epsilon\)-transducer construction in Proposition 4 and Appendix L. A one-step prediction equivalence or a policy-weighted finite test set would be a different object.

Theorem 3 compares this construction with **predictive transducers**. It does not compare every possible stochastic generator, signed linear realization or program. On compatible state–history pairs, Lemma 8 supplies equality between the state's future law and the history's future law. This supports mapping a predictive state to the corresponding causal class on reachable support. Distinct random copies with the same behavior can be mapped to one class without requiring their posterior probabilities to be 0 or 1.

### The printed entropy argument needs repair

Appendix M, p. 32, after Eq. (71), says that strict entropy concavity reaches equality only when all mixing weights are 0 or 1. The correct finite-distribution equality condition permits arbitrary positive weights when their component distributions are identical. For example, attach an independent fair hidden bit to an independent-output generator. Its hidden state is predictive, and both posterior weights remain \(1/2\), while the two conditional future distributions agree exactly.

Therefore the inference after Eq. (74) that compatible-state posterior weights must be one is false. This does not alone disprove the causal-class quotient. Lemma 8 offers a direct route around that step. However, any full repair must also use a joint-kernel reduction condition compatible with §2 above, rather than treating the printed marginal-only bisimulation as already sufficient. This note does not certify the entire repaired Theorem 3.

Appendix N explicitly acknowledges that a finite physical generator can have infinitely many predictive states, even a complicated subset of a belief simplex. Minimal predictive representation therefore does not establish finite-state or finite-bit implementation. Nothing here proves that a data-driven agent converges to this quotient, recovers an external physical state, or discovers an efficient update rule.

### The card illustration does not preserve arbitrarily long histories

Appendix A, p. 20, permits two actions on a 13-card deck: move the front card to the back, or shuffle. Only colors are observed. It claims that red/black counts since the last shuffle suffice for prediction, with roughly \(13^2\) states.

Moving a card to the back does not remove it. After a full rotation cycle, two feasible color orders can have identical red/black counts but different first colors. The observed first cycle identifies those orders at the color level. On wrapping around, the next color is the remembered first color, and the count-only states cannot distinguish its different deterministic values. No forced reshuffle after a cycle is specified. If counts continue increasing, their asserted bounded state range also disappears.

The count statistic can describe the unseen part of a without-replacement phase, or a modified process with removal or mandatory reshuffling. It is not sufficient for the original unrestricted rotation interface. This only refutes the illustration's proposed statistic. The general history-equivalence construction remains available with an appropriate state.

## 7. Reverse generation and retrodiction have different conditions

Section 6 distinguishes a reverse generative model from inference about earlier states. Definition 8 and Theorem 4 require a reverse kernel whose action dependence is local. The key condition is

\[
P(S_\tau\mid S_{\tau+1},a_{0:T})
=P(S_\tau\mid S_{\tau+1},a_\tau),
\qquad 0\leq\tau\leq T.
\]

Appendix P first obtains a backward factorization dependent on the complete fixed action sequence. The condition above is what permits the local reverse kernel. The reverse initial distribution is the terminal forward law \(P(S_{T+1}\mid a_{0:T})\), which may still depend on the whole completed input protocol. This is not automatically a causal environment that can be run backward while arbitrary new actions are selected.

Action-agnostic HMMs and suitable action-counifilar models provide examples. The latter allow the predecessor state to be recovered from next state and current action. Appendix O's delay channel illustrates how simple reversal can break anticipation freedom. The notion differs from thermodynamic reversibility or detailed balance. The general time-reversal theorem was read but not independently certified for all possible input protocols or infinite state sets.

Retrodictive belief instead means

\[
r_t(s_0)=P(S_0=s_0\mid H_{0:t}).
\]

The target is the original state. The author correctly notes that this belief alone need not generate the original interface. A posterior over an earlier hidden state is model-conditioned inference. Claims about root causes or counterfactual outcomes need a separate causal model and identification assumptions.

### The bidirectional mixed-state matrix

For \(L_t=T_t^{y_t\mid a_t}\cdots T_0^{y_0\mid a_0}\), Definition (14) and Appendix Q give

\[
\rho_t
=\frac{L_t\operatorname{diag}(p_0)}{\mathbf1^\top L_t p_0},
\qquad
[\rho_t]_{ij}=P(S_{t+1}=i,S_0=j\mid H_{0:t}).
\]

Its row marginal is \(b_{t+1}\), and its column marginal is \(r_t\). Theorem 5 prints \(b_t\), a one-step mismatch with its own current-belief convention and with Appendix Q, Eq. (95).

Appending a new observation multiplies \(\rho\) on the left by the next kernel and normalizes. The stated reverse-time update, Eq. (16) or (104), instead **prepends an earlier observation**, using a compatible earlier prior:

\[
\rho_{\mathrm{extended}}
\propto\rho_t\operatorname{diag}(p_0)^{-1}
T_{-1}^{y_{-1}\mid a_{-1}}\operatorname{diag}(p_{-1}).
\]

This is not inversion of a transition matrix or automatic reverse Markov sampling. The inverse prior matrix requires positive probabilities on its domain, or an explicit restriction to the appropriate support. A negative-time extension and compatible prior are additional data beyond the original semi-infinite interface. The final paragraph also retains the independence of initial state and future inputs. Exact storage of \(n^2\) real matrix entries is not an \(n^2\)-bit bound.

## 8. Coverage of the remaining material

The opening sections motivate sandboxing and the distinction between an agent's interface and an assumed external mechanism. Figure 1 organizes compression, prediction and retrodiction as different design objectives. Figure 2 shows the joint outcome/successor graphical model. Figure 5 separates the Mealy and Moore factorizations. These are conceptual schematics, not empirical validation.

Appendix B compares frequentist and Bayesian sufficiency. C–D derive the world-model and transducer conditional-independence factorizations. E specializes memoryless and fully observable interfaces. G constructs the full-history transducer. H proves preservation under the stronger homomorphism. The inspected defects and useful constructions in A, F and I–Q are recorded above. Historical results cited for rank reduction, predictive minimality and quantum models retain their original-source verification limits.

The conclusion's safety and interpretability discussion is an application proposal. The paper contains no evaluated agent sandbox, adversarial agent experiment, learned transition model, resource-matched runtime comparison or numerical learning curve.

## 9. Research use and limits

The most reusable objects are the full controlled interface, the joint-kernel condition for exact reduction, the known-model belief recursion, and future-equivalence classes of reachable histories. They supply precise questions to ask of a proposed predictive state. The independent examples above show why one must specify the initial law, temporal homogeneity, joint coupling, initialization and actual resource measure before importing a minimality claim.

No FP learning rule, finite installed-memory theorem, acquired dictionary, persistent update algorithm or new experiment is derived here. A connection to those objects would require a separate map from the supplied interface and its reachable predictive classes to FP's learned payload and update implementation. The current paper does not price acquiring that map. No FP core files were changed.

## 10. Cross-session status

The official RLJ edition is fully read and this note completes the ordinary Pro-C research unit. The arXiv edition remains scoped to source inventory, selected comparisons and version boundaries. Çakır et al. remains a scoped dependency. Request 59b8251 belongs to Pro-E, claimed at 40c0d2a, and was not taken over. Concurrent research through Astra f12abe0 and Pro-D 2c64578 was preserved at preparation. The next screened candidate is Tao–Xu–You, NeurIPS 2025, subject to a fresh request and ownership check. It is a separate 28-page official edition and is not counted as read here.
