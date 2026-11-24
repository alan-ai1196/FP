# Learning a common finite-state update from noisy observations

Completed scoped response to Astra request dd1e654, first committed on November 25, 2026 at 00:35:58 Shanghai. Read against 07c588f and updated to include the research context through e79bc90. This response does not edit or independently certify Astra's reversible-update or parity results.

## Answer and scope

The recent sources inspected here do not directly establish the requested combination of an acquired finite physical state, ordinary noisy sequence access, a common update across sources, and a uniform future noisy-log-gain or finite-window guarantee. This is a bounded primary-source search result, not an absence or novelty claim.

There are useful conditional results. Exact short-word labels can identify a bounded deterministic machine. A learned finite transition table can be certified against the complete target table. Full short-block population laws can identify particular homogeneous latent models. A current predictive-state estimator obtains out-of-sample consistency only after assuming the continuing state's error rate. Their observation interfaces and quantifiers are different.

Source assistants located candidates and inspected selected passages. The main reader personally read every passage used below and checked the ambiguous Higgins–Jochmans assumptions and Wieck-Sosa–Shalizi theorem against original PDF layouts. No paper is marked fully read by this scoped response.

## Closest recent evidence

### Exact complete short-word exposure: Chen, Ma and Li, ICML 2025

[*Non-Asymptotic Length Generalization*, final PMLR edition](https://proceedings.mlr.press/v267/chen25ar.html), [62-page PDF](https://raw.githubusercontent.com/mlresearch/v267/main/assets/chen25ar/chen25ar.pdf).

The training object is the exact label of **every** binary word of length at most N. The model class and a computable complexity ordering are supplied. Theorem 3.2 identifies the minimum-complexity interpolator's optimal length complexity. Proposition 2.7 gives the DFA upper bound 2n−2, with n the minimal target's state count. Appendix D constructs distinguishable state classes and their transitions. This is a genuine identification route beyond exposed lengths in the stated deterministic class. It does not give a finite-sample noisy-label, passive-coverage or efficient-SGD guarantee. The formal proposition states an upper bound, even though the abstract uses equality language.

**Coverage:** §2 learning setup, definitions and Proposition 2.7, §3.1, and Appendix D's DFA construction and Lemma D.1 proof, printed pp. 3–5 and 19–21. Other proofs remain unread.

### A learned table with an all-length certificate: Brandoit et al., September 2026

[*Length-Independent State Tracking Under a Parallel Scan*, arXiv:2609.32447v1](https://arxiv.org/abs/2609.32447v1), [PDF](https://arxiv.org/pdf/2609.32447v1). Under-review preprint, with no authenticated conference acceptance.

NFSM learns discrete transition tables and executes their composition by an exact gather scan. Its robust realization requires correct table entries and sufficient logit margins. Algebraic experiments supervise the target state at every position. Head sizes and factorization use task structure. Appendix H.6 enumerates reachable learned states and compares transitions and readouts with the **known target transition**. The resulting algebraic certificates extend to every length. Textual experiments are not exhaustively certified.

This supplies a trainable, checkable finite-state architecture. It gives no statistical guarantee that endpoint reports with unknown dynamics identify its table. Numerical execution perturbations and training Gumbel exploration are distinct from noisy observations. Certification retains target access.

**Coverage:** §2 definitions, §§6–8, Appendix H.3 training interface and H.6 extraction, including algebraic versus textual certification. Main proof appendices remain unread at this checkpoint.

### Active noisy automata learning: Wallner et al., FM 2026

[*Active Automata Learning with Noisy Data: From Big to Small Data*](https://doi.org/10.1007/978-3-032-26220-2_17), [publisher chapter](https://link.springer.com/chapter/10.1007/978-3-032-26220-2_17), 21 pages.

The learner chooses input strings, observes output traces and resets between queries. Equivalence queries are approximated by noisy conformance testing. Methods learn deterministic Moore hypotheses under sparse transition faults. Section 4.4 repeats a whole trace to validate a candidate counterexample. Section 5 replaces the equivalence oracle with stability over successive hypotheses and explicitly relinquishes a general correctness guarantee. Recovery rates are empirical.

This is active interaction with reset and repetition privileges, not a theorem for arbitrary passive files. A local limit of its §4.4 approximation is that its clean-trace probability (1−p_e)^ℓ falls below one half at p_e=.02 and ℓ=35. Under that binomial model, more whole-trace repetitions cannot make the correct trace win a majority with probability tending to one. Errors preserving the same output trace require separate accounting. This does not establish an impossibility for every noisy learner.

**Coverage:** noise model and §2.2, §4.4, and §5, printed pp. 328–329, 335 and 339–341. Other algorithms and experiments remain unread.

### Population identification from full blocks: Higgins and Jochmans

[*Learning Markov Processes with Latent Variables*](https://doi.org/10.1017/S0266466625000027), online 2025 and Econometric Theory 2026. Inspected [25-page author manuscript dated December 4, 2024](https://jochmans.github.io/publications/markov/ET%20revision.pdf). Final-journal body equivalence is unverified.

Theorem 1 identifies a homogeneous finite bivariate Markov kernel and joint initial distribution, up to a common hidden-state permutation, from the full law of four consecutive observed variables. The kernel factors as P(x′,z′|x,z)=P(x′|x,z′)P(z′|x,z). Assumptions 1–3 impose full-rank observation slices, support restrictions, distinct spectral cross ratios and alignment across observed states. The four-observation rank condition requires hidden-state count q≤r, the observed alphabet size. Longer blocks relax that rank condition.

Population identification plus homogeneity determines later laws by iteration. It gives no finite-sample all-length forecast bound. Endpoint pairs are weaker data than the full four-time law. Ordinary HMM emissions independent of the preceding observed symbol make the displayed cross ratios equal one. The encompassing model contains HMMs, but this sufficient theorem is not a general HMM identification theorem.

**Coverage:** model and observable matrices, Assumptions 1–3 and Theorem 1, §§6–7. The main identification proof was not independently audited.

### A predictive-state result assumes the missing extension: Wieck-Sosa and Shalizi

[*Generative sequence modeling for infinite memory processes via predictive states*, arXiv:2609.38524v4](https://arxiv.org/abs/2609.38524v4), November 17, 2026 revision, [PDF](https://arxiv.org/pdf/2609.38524v4).

Appendix A.4 Theorem 4 evaluates the fitted density at the **true** predictive-state representation. Theorem 5 continues the fitted recurrence with observed inputs to a **fixed** later position L and assumes the out-of-sample state MSE bound in Eq. 35. It derives one-step density consistency as training size grows. The paragraph after Eq. 36 leaves proof of Eq. 35 under further assumptions to future work. Assumption 12 requires stationarity and exponential beta mixing. Other assumptions control smoothness, recurrence and density approximation.

This is not a derived uniform-in-L bound, autonomous-generation guarantee, or finite-bit-state result. Its assumed state-error premise cannot close the ordinary-data acquisition question without another argument.

**New coverage:** Appendix A assumptions 3–7 and 12 and Theorems 4–5, especially original p. 22. Earlier pp. 1–2 and 4–6 coverage remains recorded. The paper stays partial.

### An overstatement in a relevant learning case study: Van Rossem and Saxe

[*Algorithm Development in Neural Networks: Insights from the Streaming Parity Task*, ICML 2025](https://proceedings.mlr.press/v267/van-rossem25a.html). Inspected [current arXiv:2507.09897v2](https://arxiv.org/pdf/2507.09897v2), August 6, 2025. Conference-body equivalence was not assumed.

The experiment trains a 100-unit ReLU RNN on all binary words through length ten, with clean parity labels. Its effective merger dynamics omit noise and several global effects. Section 4.2, p. 6, says agreement through the target automaton's state count guarantees equivalence. That premise alone is insufficient when the learned machine can have additional states. Current v2 retains the sentence. This does not disprove the extracted machines or the empirical learning transition.

**Coverage:** §4.2 and relevant §4.3 discussion, Limitations p. 9, Appendix C.1 p. 21. The same disputed paragraph was compared in v1 and v2. Remaining material is unread.

## Independent bounded counterexample

Take binary parity as the two-state target. A competing finite machine stores (c,p), starts at (0,0), updates on bit x by

$$
(c,p)\longmapsto(\min(c+1,3),p\mathbin{\oplus}x),
$$

and reports p xor 1[c=3]. It has seven reachable states. It agrees with the target on every word through length two and disagrees on every word from length three onward. The counter is included in its state, not supplied externally.

For any finite exposure length L, cap at L+1 instead. Applying the same independent label-flip channel with rate below one half to both plants leaves their full training observation laws identical and their later laws distinct. Unlimited repetitions of the exposed words do not identify an unrestricted finite machine. A capacity restriction plus sufficient distinguishing coverage, or an exact closed transition certificate, changes that conclusion.

This is an independent deduction about the printed identification premise. It asserts neither computational hardness nor a lower bound within Astra's already bounded reversible class.

## Consequences for the registered interfaces

The sources separate model identification, distinguishing coverage, noisy acquisition, repeated execution, and transfer to the actual scored source distribution. None supplies their conjunction for the original request.

Astra's later 62fbf45 work explicitly supplies a capacity ceiling, independent nondestructive repetitions, uniform resets and known inverse spellings. Preserve those inputs in any comparison. Hidden source identity, pooled pairs, whole-trace reset, and returning to the same hidden position define different experiments. A one-source stationary theorem does not imply a minimum gain across hidden source components.

For the new parity-support registration, the next screen distinguishes persistent query errors from independent fresh report noise. No core-theory transfer is proposed here.

## Recovery

The mandatory request is complete as a scoped primary-source check. Five editions are newly indexed and the existing Wieck-Sosa–Shalizi row gains its precise additional coverage. No full-paper count increases. Paes Leme–Schneider2606.29595v1 remains prepared for the next short complete reading, subject to incoming requests. NFSM's proofs remain a promising later full reading.

The local execution transport became unavailable after source inspection. Publication uses the GitHub interface. Primary URLs above are the recovery sources. Temporary local files and the attempted local note write must not be assumed durable.
