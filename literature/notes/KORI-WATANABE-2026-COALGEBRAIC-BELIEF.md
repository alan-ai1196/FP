# From coalgebraic determinization to belief construction for partial observability

## Source, edition and actual reading

- **Authors:** Mayuko Kori and Kazuki Watanabe.
- **Completed edition:** [CONCUR 2026 official proceedings](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CONCUR.2026.39), LIPIcs 391, article 39, pp. 39:1–39:22, published August 24, 2026, DOI [10.4230/LIPIcs.CONCUR.2026.39](https://doi.org/10.4230/LIPIcs.CONCUR.2026.39). This is a published conference paper, not just an arXiv acceptance claim. [Official 22-page PDF](https://drops.dagstuhl.de/storage/00lipics/lipics-vol391-concur2026/LIPIcs.CONCUR.2026.39/LIPIcs.CONCUR.2026.39.pdf), CC BY 4.0.
- **Full reading by Pro-C, November 26, 2026, Shanghai:** all 22 physical pages, §§1–10, Appendices A, B.1–B.2 and C.1–C.6, all published definitions, proofs, formulas, both actual figures, the unnumbered categorical diagrams, both body footnotes, funding, acknowledgements and all 31 references. Complete original-PDF text was read in contiguous blocks. Original PDF pp. 2–16 and 18–22 were also visually inspected. There are no tables or empirical experiments.
- **Separate scoped edition:** [arXiv:2604.25355v3](https://arxiv.org/abs/2604.25355v3), June 29, 2026, 27 pages. The official final explicitly cites this longer version as reference [22]. The arXiv history also lists v1 on April 28 and v2 on May 18. Pro-C read all of **Appendix C.7–C.13, pp. 23–27**, through the complete corresponding TeX block and the three included proof diagrams. All five original PDF pages were visually checked. A separate assistant compared the relevant construction, theorem and proposition statements between editions. The rest of v3 is not claimed fully read. Earlier versions were not read.
- **Verification boundary:** bounded manual checks of concrete conditioning, preservation hypotheses, scheduler information, the full-observability quantifiers, weighted normalization, an attainment counterexample and local formula typing. An assisting mathematical reader independently checked the corresponding main sections. This is not a certification of every categorical diagram, imported adjunction theorem or reachable-coalgebra result. No scripts, experiments, formalization or kernel replay were used.
- **Ignored source cache:** `literature/corpus/pro_c/kori-watanabe-2026/`, with separate `final/` and `arxiv-v3/` directories. No FP core files were changed.

**Main finding:** the paper provides an exact, model-supplied construction of observation-labelled beliefs and proves preservation of the stated deterministic-history-scheduler semantics. Turning that belief system into a fully observable system is a second result with an additional history-reconstruction hypothesis. The concrete probabilistic and nonnegative weighted examples satisfy it. The result supplies no learned state representation, finite precision guarantee or generic finite-memory policy theorem. The objective is a supremum, which need not be attained even in a finite POMDP.

## 1. What is being constructed

The input is an initial-state map \(i:I\to S\), a deterministic observation map \(\mathrm{obs}:S\to O\), and a transition structure

\[
\delta:S\longrightarrow (FTS)^A.
\]

Here \(T\) describes branching, \(F\) describes the other one-step structure, and \(A\) is the action object. Before actions are introduced, §§3–4 work with \(S\to FTS\). A distributive law \(\lambda:TF\Rightarrow FT\) permits ordinary determinization on \(TS\). It moves the branching structure through the one-step structure and flattens nested branching using the monad multiplication.

That ordinary construction is insufficient to express filtering after the observation that actually occurs. The paper adds a decomposition according to observation fibres. It retains stochastic or nondeterministic branching between possible next observations. The resulting belief coalgebra has the same effectful \(FT\) transition type. It is not a claim that the observable process has become deterministic.

The initial belief is the unit image \(\bar\eta_{\mathrm{obs}}\circ i\). In the probabilistic example, this is a Dirac belief at the specified initial state. The statements are pointwise in the initial element. They do not, without a further encoding, formulate one common policy for an undisclosed initial state drawn from a general prior.

### The observation-fibre carrier

Definition 9, p. 5, forms a pullback of

\[
T(\mathrm{obs}):TS\to TO
\quad\text{and}\quad
\eta_O:O\to TO.
\]

Write its carrier as \(B_{\mathrm{obs}}\), its underlying map to \(TS\) as \(\iota\), and its observation map as \(\bar T(\mathrm{obs}):B_{\mathrm{obs}}\to O\). This construction extends to a monad on the slice category \(\mathcal C/O\). Proposition 10 derives that monad from a sliced Eilenberg–Moore adjunction. It also supplies coherent base-change maps when the observation object changes. Proposition 12 makes the forgetful map back to \(T\) a monad morphism.

For finitely supported distributions, the carrier consists of beliefs whose support lies in **one** observation fibre:

\[
B_{\mathrm{obs}}
=\{b\in\mathcal D(S):\exists o,\ \operatorname{supp}(b)\subseteq\mathrm{obs}^{-1}(o)\}.
\]

This is not all of \(\mathcal D(S)\). The associated observation is unique. For an arbitrary monad, the pullback is the definition, and it should not automatically be described as a literal subset of \(TS\) without a monicity condition on the relevant map.

### Decompose, then retain the observation branches

Definition 15 requires a natural transformation

\[
\alpha^O:T d_O\Rightarrow T d_O\bar T_O
\]

which is a section of flattening:

\[
\mathrm{flat}^O\alpha^O=\mathrm{id},
\qquad
\mathrm{flat}^O=\mu d_O\circ T\iota.
\]

It must also be coherent under the admitted observation-label maps. Definition 16 then sets

\[
c^{\mathrm{Bel}}
=F\alpha_{\mathrm{obs}}\circ\operatorname{Det}(\delta)\circ\iota.
\]

Proposition 20 says that fully observable inputs give the original system up to canonical isomorphism. Proposition 21 says that flattening the observation-wise decomposition recovers ordinary determinization along \(\iota\). Neither proposition is a state-minimization result.

In all concrete examples, admissible observation-label maps are **monomorphisms**, hence injections on sets. The observation function itself may be many-to-one. These are different restrictions. Coherence is not asserted for arbitrary sensor coarsening.

For example, take two states with distinct labels and \(b=(\delta_{s_0}+\delta_{s_1})/2\). Decomposing before merging the two labels gives an outer mixture of the two Dirac beliefs. Decomposing after merging gives the Dirac distribution concentrated on \(b\). The two distributions over beliefs differ, although both flatten to \(b\). This bounded independent check explains why the label-map restriction matters.

## 2. The preserved semantics and its hypotheses

Assumption 23, pp. 8–9, adds cartesian closure, countable coproducts, strong \(F,T\), compatibility of \(\lambda\) with strength, an action object and an ordered evaluation object \(\Omega\). The hom-sets into \(\Omega\) are complete lattices, and precomposition preserves joins. A monotone evaluation algebra is fixed:

\[
\tau:FT\Omega\to\Omega,
\qquad
\Phi_c(f)=\tau\circ FT(f)\circ c.
\]

A scheduler is a **deterministic** function \(u:O^+\to A\). Its previous actions are recoverable from its observation history. This explains why the scheduler argument need not separately list previous actions. It does not justify omitting private random state for an arbitrary randomized scheduler. Randomized and more general effectful strategies are explicitly future work in §10.

Definition 28 carries the residual scheduler as part of the state, on \(S\times A^{O^*}\). Definition 31 instead carries the complete state history \(S^+\). Proposition 32 identifies their semantics using the explicit history-to-residual-scheduler coalgebra morphism in Appendix C.6.

The objective takes the join over schedulers and finite horizons:

\[
V^*_{i,c}
=\bigvee_{u:O^+\to A,\ n\in\mathbb N}
\Phi_{\mathrm{Sch}(c)}^n(\bot)\circ\mathrm{initialization}_u.
\]

This definition does not require an optimizer to exist. Monotonicity alone also does not make an arbitrary \(\omega\)-join of iterates a least fixed point. The paper's generic result preserves the quantity it actually defines. The concrete finite Boolean and nonnegative additive examples have additional structure supporting their stated interpretations.

### Theorem 35 is conditional on the evaluation algebra

Besides the standing categorical assumptions, the condition \((\star)\) on pp. 11–12 requires:

1. A factorization \(\tau=\rho\circ F\sigma\), where \(\rho:F\Omega\to\Omega\) is monotone and \(\sigma:T\Omega\to\Omega\) is a monotone Eilenberg–Moore algebra.
2. The compatibility and bottom identities

\[
\sigma\circ T\rho=\rho\circ F\sigma\circ\lambda_\Omega,
\qquad
\sigma\circ T\bot_X=\bot_{TX}.
\]

3. Consistency of a belief's observation with the observations of its underlying states:

\[
T\langle\mathrm{id},\mathrm{obs}\rangle\circ\iota
=\mathrm{st}^T\circ\langle\iota,\bar T(\mathrm{obs})\rangle.
\]

The last identity holds in the examples because a belief has support inside one observation fibre. It is used when moving the scheduler's residual-observation argument through the transition construction.

The proof establishes equality for the **same scheduler at each finite horizon**, then takes the joins. It does not assume a direct coalgebra morphism between the original and belief scheduler-carrying systems. Instead, Lemmas 33–34 introduce a comparison map that flattens a distribution of beliefs while carrying the residual scheduler. Its transition compatibility holds after the specified second-step flattening and distributive-law composite. Theorem 35 then uses induction, algebra compatibility and bottom preservation.

The official proof is a sketch of the induction. The full argument was read in v3 Appendix C.9, Lemma 45, together with the supporting C.7–C.8 diagrams. This fills a reading dependency. It is not a separate formal certificate.

## 3. Why full observability is a second result

Theorem 35 equates the original partially observable system and its **observation-labelled belief system**. Proposition 37 gives the general inequality from partial to full observation. A split-monomorphism observation map is sufficient for equality, because a map back from observations recovers every state.

Proposition 39, p. 13, uses a weaker, policy-dependent condition. For **every fully observable history scheduler** \(u:S^+\to A\), it requires an initial-point-containing subcoalgebra \(m_u\) of the resolved history system, together with

\[
f_u:O^+\to S^+,
\qquad
f_u\circ\mathrm{obs}^+\circ m_u=m_u.
\]

The subcoalgebra must be closed under the resolved transitions. It cannot be an arbitrary set of favorable histories. The observation-based scheduler \(u\circ f_u\) then imitates the fully observable scheduler on that part. The proof in v3 Appendix C.12 applies semantic preservation under the corresponding coalgebra morphisms and takes the join.

In sets, Remark 40 permits a separate argument for every initial element \(x\in I\). The map \(f_u\), and the reachable part used to obtain it, can depend on the scheduler and initial point. This does not supply one common optimizer for all initial elements.

For the probabilistic and weighted belief examples, given a belief, action and supported next observation, there is at most one next normalized belief. From the known initial belief, its reachable history is therefore recoverable from the observation history under a fixed scheduler. This meets Proposition 39's condition.

The result compares full access to the **belief state** with its observation history. It does not equate partial observation with seeing the original physical hidden state. The paper's two figures make that distinction concrete: the original POMDP has value 2, the fully observed original state system has value 5/2, and the reachable belief system again has value 2. The depicted four-state reachable belief graph is an example, not a general finite-state bound.

## 4. What the three examples cover

### Probabilistic control

Section 8.1 uses \(T=\mathcal D\), finite-support distributions, and \(F(X)=X\times\mathbb R_{\ge0}\). The distributive law marginalizes the next state and averages the reward. For a prior \(b\), the decomposition is

\[
\alpha_{\mathrm{obs}}(b)
=\sum_{o:Z_o(b)>0} Z_o(b)\,\delta_{b\mid o},
\quad
Z_o(b)=\sum_{s:\mathrm{obs}(s)=o}b(s).
\]

The conditional belief \(b\mid o\) is normalized within that fibre. Zero-probability observations produce no branch. The evaluation object is \([0,\infty]\), with addition for \(\rho\) and expectation for \(\sigma\). The finite iterates give finite-horizon total expected reward. Nonnegativity supports the increasing-horizon interpretation, allowing an infinite value.

This observation interface consists of the specified state labels. If rewards or other feedback are intended to be available to the controller, they must be represented in that interface. Stochastic observations and transition-based rewards can be encoded by expanding the state, as the paper notes. Such encodings are mathematical model changes, not cost-free memory or sample-complexity statements.

### Nonnegative weighted systems

Section 8.2 uses the finite-support semimodule monad over **\(\mathbb R_{\ge0}\)**. It does not prove the same construction for arbitrary semirings or signed weights. The belief carrier consists of normalized nonnegative weight functions supported on one observation fibre. The outer weights \(Z_o\) retain the fibre's original mass. Thus normalization does not throw away total weight.

A zero weight function decomposes into zero outer weight. No posterior for a zero-mass fibre is required. The evaluation combines immediate termination weight with weighted continuation. Appendix B.2, Proposition 46, identifies the horizon supremum with the sum of weights of all finite terminating paths, each path weight being the product of its transition weights and final termination weight. Transition weights need not sum to one, and the total can diverge.

The authors present the resulting equivalence as new for weighted systems. This note records their claim without an independent novelty search. The use of nonnegative real weights is substantive for conditioning, sums and order. An extension with cancellation or without division would require a different argument.

### Finite nondeterministic termination

The running example uses the **nonempty finite powerset** monad and a separate termination outcome. The evaluation takes conjunction over successors. This choice satisfies bottom preservation. The unrestricted powerset with empty branching and the same evaluation would not.

The objective is existence of a controller under which **every path terminates**. Finite branching connects that property to a uniform finite depth for each fixed starting state and resolved policy. It is not a probabilistic almost-sure termination objective.

For finite original state and action sets, the belief carrier is finite. V3 Proposition 46, Appendix C.13, computes the fully observable belief objective by iteration of a finite Boolean predecessor operator. This establishes decidability. The subset construction can be exponential in the original state count. It does not provide an efficient general POMDP solver.

## 5. Bounded independent findings and local corrections

### A supremum need not be a maximum

The general prose in §8 describes a maximum, while the formal definition is a join. Attainment can fail within the paper's finite POMDP model.

Let \(S=\{b,g,d\}\), initially \(b\), with \(b,g\) sharing observation \(o\) and \(d\) having a separate absorbing observation. There are two actions:

| State | Action | Next-state distribution | Nonnegative reward |
|---|---|---|---:|
| \(b\) | wait | \((\delta_b+\delta_g)/2\) | 0 |
| \(g\) | wait | \(\delta_g\) | 0 |
| \(b\) | stop | \(\delta_d\) | 0 |
| \(g\) | stop | \(\delta_d\) | 1 |
| \(d\) | either | \(\delta_d\) | 0 |

This is precisely a transition map into \((\mathcal D(S)\times\mathbb R_{\ge0})^A\). Before stopping, the observation sequence contains only \(o\). Every deterministic observation-history policy therefore stops after a fixed finite number \(n\) of waits, or never stops. Its expected reward is respectively \(1-2^{-n}<1\), or zero. The supremum is 1 and no policy attains it.

This independent example corrects an interpretation of the value. It does not refute Theorem 35, whose actual objective remains a supremum.

### Two local typing slips

- **Final Definition 15(ii), p. 6:** the displayed codomain of the natural-transformation equality omits an outer \(T\). Its two sides have codomain \(T d_{O'}\bar T_{O'}\Sigma_u\), as follows from the stated type of \(\alpha\) and the component \(T d_{O'}\theta_u\). The intended coherence equation is otherwise clear.
- **V3 Appendix C.9, p. 25:** the base-case calculation prints \(\sigma\circ\mu_{T\Omega}\circ T^2\bot_X\). It must use **\(\mu_\Omega\)**. The map \(T^2\bot_X\) lands in \(T^2\Omega\), and \(\mu_\Omega:T^2\Omega\to T\Omega\) then composes with \(\sigma\). The printed \(\mu_{T\Omega}\) has domain \(T^3\Omega\). Naturality of \(\mu\) and the Eilenberg–Moore law yield the intended local step after that correction. Both TeX and original PDF confirm the typo. This is a finding in the longer version's proof, not the official final's displayed Eq. (4).

Appendix B.1's flattened conditional expression is understood only on positive-mass fibres, with value zero elsewhere. Its preceding definition of \(\alpha\) already makes this restriction explicit. An unconditional reading of the subsequent quotient would write \(0/0\), but it is not a counterexample to the decomposition.

The finite-horizon preservation mechanism, explicit conditional decomposition and policy-reconstruction argument survived the bounded checks performed here. No complete certification is asserted.

## 6. Edition map and implications for further use

The final has 31 references and stops at Appendix C.6. The longer v3 has 30 references and continues through C.13. Assumptions use a different numbering convention. Relevant correspondences are:

| Official CONCUR final | Longer arXiv v3 | Read proof location |
|---|---|---|
| Definition 15, belief decomposition | Definition 14 | Final definition and Appendix A |
| Definition 16, belief construction | Definition 15 | Final §§4, C.3–C.5 |
| Proposition 32, history/scheduler equivalence | Proposition 30 | Final C.6 |
| Lemmas 33–34 | Lemmas 31–32 | V3 C.7–C.8, pp. 23–24 |
| Theorem 35, semantic preservation | Theorem 33 | V3 Lemma 45, C.9, p. 25 |
| Proposition 37, partial/full inequality | Proposition 35 | V3 C.11, p. 26 |
| Proposition 39, history reconstruction | Proposition 37 | V3 C.12, p. 26 |
| Example 41, finite nondeterministic decidability | Example 39 | V3 Proposition 46, C.13, pp. 26–27 |
| Proposition 46, weighted-path semantics | Proposition 44 | Final B.2, p. 20 |

In particular, **final Proposition 46 and v3 Proposition 46 are different results**. The scoped edition comparison found the same relevant hypotheses in the inspected construction and preservation statements. It was not a whole-document equivalence audit and does not upgrade v3 to fully read.

The adjacent [Baltieri–Virgo note](BALTIERI-VIRGO-2026-COALGEBRAIC-BAYES.md) studies a support-indexed stochastic Mealy construction and its exact Bayesian updates. The present paper treats an observation-labelled control system and specifies which evaluated control semantics are preserved. These are precise related model transformations, not automatic equivalents of every prediction problem.

For FP, the defensible use is an exact supplied-model reference and an observation-interface checklist. Replacing the exact belief by a finite randomized codebook is not this paper's section-of-flattening construction in general. A log-loss comparison also requires its own evaluation and integrability assumptions rather than importing the nonnegative additive examples. No approximation, finite precision, learned transition, sample complexity, predictive-state minimality or recursive codebook-regret theorem follows from the results read here. No transfer to FP is proposed.
