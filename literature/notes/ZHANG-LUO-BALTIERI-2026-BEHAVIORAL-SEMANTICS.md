# Compositional behavioral semantics: exact abstraction, post-fixed transfer and interface boundaries

## Source, edition and actual reading

- **Authors:** Yivan Zhang, Ziyan Luo and Manuel Baltieri.
- **Completed edition:** [ICML 2026 official proceedings](https://proceedings.mlr.press/v306/zhang26dy.html), PMLR 306:157468–157507, July 6–11, 2026. [Official 40-page PDF](https://raw.githubusercontent.com/mlresearch/v306/main/assets/zhang26dy/zhang26dy.pdf).
- **Full reading by Pro-C, November 26, 2026, Shanghai:** all 40 physical pages, §§1–5, Appendices A–F including F.1–F.7, all definitions, proofs, displayed formulas and footnotes, acknowledgements, impact statement, contents, Symbols and all 91 printed references. The complete 2,406-line official PDF extraction was read in consecutive blocks. Original pp. 4–5, 7, 16, 24, 26–27, 29–30, 32–40 were visually inspected. This covers both numbered figures, all three panels of Figure 2, both numbered tables, the Symbols table and all six additional interface/agent schematics. The source inventory also identifies 33 mathematical commuting-diagram environments. There are no empirical experiments or numbered algorithm boxes.
- **Separate author edition:** [arXiv:2606.25357v2](https://arxiv.org/abs/2606.25357v2), August 7, 2026, 07:04:36 UTC, 40 pages. The current source history contains v1 and v2. The complete v2 TeX package is cached, with main.tex and 26 recursively active TeX files. It was used for source inventory and selected formula checks, not read as a second complete manuscript. The official PDF and v2 are different byte streams. Raw PDF-text extraction agrees over 102,977 non-whitespace characters after removing the v2 watermark and normalizing exactly eight official “Appendix” cross-reference labels to the v2 “Section” labels. Layout extraction has additional ordering differences. This documents a text comparison, not a second full reading or graphical identity certificate.
- **Verification boundary:** bounded independent checks of the transfer directions, the probability/observation/policy interfaces, the zero-set compatibility conditions and two small examples below. Assisting readers checked these selected interfaces independently. No formal proof, exhaustive theorem audit, learning implementation or experiment reproduction was performed. No AI assistance disclosure was located in the read edition.
- **Ignored source cache:** literature/corpus/pro_c/zhang26dy/, including arxiv-v2/ and render/. No FP core files were edited.

**Main finding:** this is a useful compositional framework for transferring one-step behavioral structures through exact system homomorphisms. Its main transfer statements concern post-fixed bundles. They do not automatically supply metric axioms, value-function uniqueness, lossy observation compression or learned finite memory. The logical–quantitative bridge needs compatible observation leaves as well as the stated operator identities. Its standard finite-support Wasserstein instance can satisfy the additional zero-cost attainment step. The paper explicitly leaves approximation and a complete treatment of bidirectional stateful-agent feedback to future work.

## 1. What is being abstracted

The concrete examples work over sets. The probability functor \(P\) contains **finitely supported probability distributions**, including when the underlying state, action or observation sets are infinite. A different measurable probability functor would require its own instance and hypotheses. General continuous-noise kernels are not already covered by the specified \(P\).

An environment is a stochastic Moore coalgebra

\[
\tau_X:X\longrightarrow F X,
\qquad F X=(PX)^A\times O,
\qquad \tau_X(x)=(p_X(x,\cdot),o_X(x)).
\]

The next-state distribution is stochastic. The current observation \(o_X(x)\) is deterministic and independent of the chosen action. The main environment interface does not include initialization, termination or an optimality criterion. Appendix A.2 lists other functors for independent stochastic observations, correlated outputs, Mealy behavior and termination. Listing those types is distinct from proving every later RL instance for each type.

A map \(f:X\to Y\) is an exact homomorphism when

\[
\tau_Y f=Ff\,\tau_X.
\]

For the stochastic Moore type, Eq. (7) expands this into

\[
p_Y(f(x),a)=f_*p_X(x,a),
\qquad o_Y(f(x))=o_X(x)
\quad\text{for all }x,a.
\]

The first \(f_*\) here is the ordinary pushforward of a probability law. It should not be confused with the later fiber-join pushforward of an arbitrary bundle.

Definition 2.7 calls an encoder \(\phi:S\to Z\) an abstraction when an abstract system on \(Z\) makes it such a homomorphism. The abstract transition map is part of the required existence statement. The paper explicitly recognizes that this is stronger than other useful abstraction notions.

### Observation preservation is a substantive constraint

Directly from the second equation,

\[
f(x)=f(x')\Longrightarrow o_X(x)=o_X(x').
\]

If the declared observation map is injective, the encoder must also be injective. Consequently, the same-interface theorem does not justify merging states that have different declared observations. Choosing reward or a selected cumulant as \(O\) can permit a coarser abstraction, but changes what is being preserved. The paper explicitly identifies reward prediction with this condition only when the observation map is a reward function, p. 4.

This is an exact structural characterization for supplied systems. There is no sample complexity, representation-learning rule or acquisition theorem hidden in the existence of \(\phi\).

## 2. Policy composition and one-step behavioral semantics

The main closed-loop construction uses

\[
\pi:O\to A,
\qquad p_X^\pi(x)=p_X(x,\pi(o_X(x))).
\]

This is a deterministic stationary reactive policy. A natural transformation changes the environment type \((PX)^A\times O\) to the policy-conditioned type \(PX\times O\), while retaining the same carrier. Naturality ensures that an existing same-type homomorphism remains a homomorphism after this common interface transformation.

Figure 1 shows this current-observation feedback. It does not introduce recurrent controller memory or an arbitrary history-dependent policy. Stochastic and stateful policies are discussed later, with different scope.

An \(n\)-ary **bundle** is simply a function

\[
h_X:X^n\to V.
\]

Unary bundles include predicates and values. Binary bundles include relations and nonnegative dissimilarities. The bare definition does not impose metric axioms. The orders used in the main examples are

\[
\bot\preceq\top,
\qquad u\preceq v\iff u\geq v
\quad\text{on nonnegative quantities}.
\]

A lifting \(\lambda_X\) takes \(h_X\) to a bundle on the one-step behavior space \((FX)^n\). Composing with the dynamics gives

\[
T_X=\tau_X^*\lambda_X,
\qquad T_Xh_X=h_X^{\mathrm{lift}}\circ\tau_X^n.
\]

A behavioral structure is a post-fixed bundle \(h_X\preceq T_Xh_X\), or sometimes a fixed point. The paper calls \(T_X\) a “closure operator.” That name does not add the usual order-theoretic requirements of extensivity and idempotence. Its Bellman examples are ordinary one-step operators and generally are not idempotent.

### The concrete constructions

For the policy-conditioned Markov type, Eq. (10) has the form

\[
\lambda_X(h_X)(p,o)
=\left(\odot\,P h_X(p)\right)\oplus h_O(o).
\]

Here \(\oplus\) combines the successor statistic with the current observation statistic. \(\odot\) aggregates a probability distribution over values. An additional \(\Box_A\) handles action-indexed components for open-loop systems.

| Example | Chosen operations and resulting meaning | Scope |
|---|---|---|
| Safety predicate | Almost-sure successor truth, conjunction with current output safety | A one-step invariant condition for the specified system |
| Reward / general value function | \(T v(x)=r(o(x))+\gamma\mathbb E[v(X')\mid x]\) | A fixed-policy Bellman form, provided the intended return is well defined |
| Successor feature | Vector-valued cumulant with a linear scalar map \(w\) | Linearity makes scalarization commute with this one-step aggregation |
| Binary relation | Existence of a coupling satisfying the relation almost surely, then output and action aggregation | Logical distribution lifting |
| Binary quantity | Infimum of expected cost over couplings, then output and action aggregation | A Wasserstein-style lifting of a chosen cost |

For binary probability lifting, the paper contrasts the independent product coupling with optimization over all couplings. Figure 2 makes the distinction visible. Equality of individual probability masses, independent samples lying in one equivalence class, and equality of total mass across equivalence classes are different conditions. Independent coupling is generally too restrictive to express the usual probabilistic bisimulation relation.

The reward example allows \(\gamma\in[0,1]\). The displayed formula alone does not establish a unique finite return for \(\gamma=1\), arbitrary rewards or arbitrary infinite systems. A bounded-reward, \(\gamma<1\) setting supplies a familiar sufficient condition, but is an additional specialization. This is a qualification of the value interpretation, not a problem with the syntactic operator construction.

## 3. What the transfer theorems prove

For a bundle on the abstract system,

\[
f^*h_Y=h_Y\circ f^n.
\]

For a bundle on the concrete system, Definition 3.10 uses

\[
(f_*h_X)(y_1,\ldots,y_n)
=\bigvee_{x_i\in f^{-1}(y_i)}h_X(x_1,\ldots,x_n).
\]

All relevant joins must exist, including the empty-fiber join. For Boolean truth this is existential aggregation. For \([0,\infty]\) in the reverse order it is the usual infimum, with empty join \(+\infty\). It is neither empirical averaging nor conditional expectation. On \(\mathbb R\), or in a general base category, existence and closure in the appropriate morphism class require care.

### A genuine lifting is an assumption, not just a shared formula

Definition B.4 requires

\[
h_X\preceq h_Y\circ f^n
\Longrightarrow
\lambda_X(h_X)\preceq\lambda_Y(h_Y)\circ(Ff)^n.
\]

This implies monotonicity by taking \(f=\mathrm{id}\). Appendix B.2 explicitly assumes order-preserving operators and component modalities when using the compositional formulas on lax bundle categories. Thus “constructed with the same operators” in Lemma 3.11 must be read with those compatibility conditions.

Under an exact coalgebra homomorphism, the proof chain yields

\[
T_Xf^*\preceq f^*T_Y,
\qquad f_*T_X\preceq T_Yf_*.
\]

The first inequality follows from oplax lifting plus the exact dynamics square. The second uses monotonicity and the adjunction \(f_*\dashv f^*\). Appendix C derives the first direction and Appendix D the second. The independent bounded check found their inequality directions consistent.

| Statement | Hypotheses and direction |
|---|---|
| Theorem 3.12 / C.16, verification | For surjective \(f\), \(f^*h_Y\preceq T_X(f^*h_Y)\) implies \(h_Y\preceq T_Yh_Y\) |
| Theorem 3.13 / D.8, construction | \(h_X\preceq T_Xh_X\) implies \(f_*h_X\preceq T_Y(f_*h_X)\) |
| Pullback preservation | Requires the reverse closure inequality. C.16 supplies it when the lifting is strict at \(f\) |
| Fixed-point equality after pullback | Follows if strictness gives \(T_Xf^*=f^*T_Y\) |
| Fixed-point equality after pushforward | Not supplied by the general post-fixed transfer theorem |

In a general category the reflection condition is that \(f^n\) is an epimorphism. In Set, surjectivity supplies it. Construction does not need surjectivity if the required pushforward exists. None of these statements alone establishes fixed-point existence, uniqueness or general preservation of least/greatest fixed points.

For nonnegative quantities the condition \(h\preceq Th\) means \(h\geq Th\) in the usual numeric order. Losing this reversal changes the interpretation of the guarantees.

### Small independent example: post-fixed transfer does not preserve metric axioms

Take four concrete states at coordinates \(0,1,9,10\), one action, a constant observation and a deterministic self-loop at every state. Let \(d(x,x')=|x-x'|\). Use the binary Wasserstein lifting, zero observation cost and discount one. The coupling of two Dirac transitions is unique, so \(T_Xd=d\).

Map \(0\) to abstract state \(a\), both \(1,9\) to \(b\), and \(10\) to \(c\). Give every abstract state the same observation and a self-loop. This is an exact homomorphism. Its fiber-inf pushforward satisfies

\[
(f_*d)(a,b)=1,
\qquad(f_*d)(b,c)=1,
\qquad(f_*d)(a,c)=10.
\]

The triangle inequality fails. The pushed-forward bundle still is a fixed point of its one-step operator, exactly as the transfer theorem permits. This four-state calculation is not a counterexample to Theorem 3.13. It shows why a post-fixed bundle theorem is insufficient to certify a quotient metric. Metric closure or another additional construction would be a separate step.

## 4. Logical–quantitative correspondence and its missing explicit premises

Theorem 3.14 uses the zero predicate

\[
z:[0,\infty]\to\{\top,\bot\},
\qquad z(q)=[q=0].
\]

Its desired identity is

\[
z\circ\lambda_X^Q(h_X)
=\lambda_X^L(z\circ h_X).
\]

Main-text footnote 7 and the repeated footnote 9 in Appendix E explicitly impose three algebra-homomorphism equations, for the combinator, action aggregator and probability barycenter. Nonnegative addition/conjunction, nonnegative sum/universal quantification and expectation/almost-sure truth satisfy the standard identities. Signed reward cancellation is outside this nonnegative zero-set argument.

### Observation leaves must also agree

The composite lifting includes a specified bundle on the observation object. It must satisfy

\[
h_O^L=z\circ h_O^Q,
\]

with the analogous condition for binary observation structures and every other constant/base component. The three explicitly listed operator identities do not enforce this condition on independently chosen leaves. Appendix B.8 treats a constant-functor lifting as choosing a fixed morphism, which makes this omitted base case particularly clear.

**Independent singleton check.** Take \(X=\{x\}\), \(O=\{o\}\), \(h_X^Q(x)=0\), \(h_O^Q(o)=1\), but \(h_O^L(o)=\top\). Use addition and expectation for quantities, conjunction and almost-sure truth for logic. All three listed operator identities hold, using sum/universal aggregation if needed. At \((\delta_x,o)\),

\[
z\bigl(\lambda_X^Q(h_X)(\delta_x,o)\bigr)=z(1)=\bot,
\]

\[
\lambda_X^L(z\circ h_X)(\delta_x,o)=\top.
\]

Thus the stated list of three conditions is insufficient without compatible base observations. This is a local sufficient-condition repair. It does not refute the correctly paired standard construction.

### Coupling minimization is an additional operation

The binary Wasserstein construction also uses \(\kappa\), a join over the coupling fiber. It is not one of the three listed operations. In general,

\[
z\left(\inf_\pi c(\pi)\right)
=\exists\pi\,z(c(\pi))
\]

requires a zero-cost witness whenever the infimum is zero.

For the paper's **finite-support marginals and expected nonnegative cost**, that step can be supplied. All couplings are supported on a finite Cartesian product and form a compact finite-dimensional polytope. A finite nonnegative cost has an attained minimum. With \(+\infty\) entries, a sequence of finite-cost couplings places zero mass on those entries, and a convergent subsequence remains in that closed face. Consequently,

\[
\inf_{\pi\in\Pi(\mu,\nu)}\mathbb E_\pi h=0
\iff
\exists\pi\in\Pi(\mu,\nu):h=0\quad\pi\text{-almost surely}.
\]

This bounded completion supports the standard Wasserstein/expectation instance. It does not establish the same claim for every barycenter or arbitrary infinite fiber.

In particular, finite support of each transition law does not make an encoder fiber finite. A fiber with values \(1,1/2,1/3,\ldots\) has infimum zero and no zero-valued element. The theorem about lifting therefore must not be silently extended to commutation of \(z\) with every bundle pushforward.

With compatible base components, compatible operators and the necessary coupling step, the zero set of a quantitative post-fixed bundle is a logical post-fixed bundle. A quantitative fixed point similarly gives a logical fixed point. This is a relation between **specified** structures. It neither recovers a unique numerical structure from a Boolean one nor proves metric axioms or a learning algorithm.

## 5. The state-abstraction equivalences recovered in §4

**Next-observation prediction, Proposition 4.1.** Exact homomorphism preserves the law of the next declared observation for every action. The proof composes the transition pushforward square with the observation-preservation square. The paper explicitly says the converse fails. Accurate next-observation prediction alone does not prove the full homomorphism conditions.

**Model-irrelevance abstraction, Proposition 4.2.** Within a fiber of \(\phi\), both the current observation and the next abstract-state law for each action must agree. This is the kernel condition that allows \(F\phi\circ\tau_S\) to factor through \(\phi\). It constructs the required abstract dynamics on the represented image. It is an exact structural factorization, not an optimization or generalization result.

**Bisimulation, Proposition 4.3.** For an equivalence relation \(r\) with quotient map \(q_r\), define

\[
T_X(r)=\ker(Fq_r\circ\tau_X).
\]

Then the quotient map is a homomorphism exactly when \(r\subseteq T_X(r)\). The proof is the same factorization criterion. For the stochastic Moore instance this recovers the equality of observation and transition masses across quotient classes. It organizes the relationship between self-prediction and bisimulation without supplying a procedure that learns the quotient from finite samples.

**Value equivalence, §4.4.** The kernel of a specified policy's value function need not preserve the one-step decomposition. Immediate and future contributions can cancel. The authors explicitly distinguish this from a structural bisimulation or an exact dynamics-preserving homomorphism. This qualification should remain when using the paper as a unification reference.

## 6. Interface changes, stateful agents and what remains open

Appendix F separates several constructions that are easy to conflate:

| Construction | What changes | What it does not establish |
|---|---|---|
| Action translation, F.2 | Reinterprets an action through \(g:A\to A'\), same state carrier | State compression |
| Reactive closed loop, F.3 | Feeds current observation through \(\pi:O\to A\), same carrier | Arbitrary recurrent or history-dependent control |
| Observation-dependent action adapter, F.4 | Uses \(g:O\times A\to A'\), separating action interface from state abstraction | An unchanged-input-interface homomorphism by itself |
| Forward statistic aggregation, F.5 | Augments \(S\) to \(S\times M\), updates \(M\) from emitted observations | Feedback from the statistic into environment actions |
| Stateful-agent discussion, F.6 | Draws the two-way loop between environment state and controller memory | A completed categorical feedback-transfer theorem |
| Options, F.7 | Treats the option index as internal control state and discusses random intra-option policies | A proved equivalence of all state and temporal abstractions |

The forward statistic update is \(\triangleright:O\times M\to M\). F.5 provides a bifunctor for the deterministic illustrative systems, with augmented update

\[
(s,m)\longmapsto\bigl(t(s),\triangleright(o(s),m)\bigr).
\]

Belief filters, PSRs, temporal monitors and budget statistics are listed as examples of forward state. They are not automatically given finite cardinality, finite precision or a learned update mechanism by this product construction.

F.6 explicitly says that feedback from memory to actions, which then changes future observations, is not captured by that one-way statistic construction. It suggests more general categorical systems formalisms and leaves the extension to future work. It is therefore inaccurate to cite this appendix as a completed theorem for arbitrary stateful-agent composition.

The formal policy pullback \(\pi_Z\circ\phi:S\to A\) also needs an implementation qualification. In a partially observed environment, the displayed composition does not prove that \(\phi(s)\) is computable from observations or available history. Accessibility of the representation is a separate requirement.

F.7 does mention stochastic intra-option policies \(\pi:S\times I\to PA\). This prevents the overstatement that the paper ignores stochastic or memory-based control. Its presence in the discussion does not expand the proved reactive-policy natural transformation to all such controllers.

## 7. Research value and applicability boundary

The reusable mathematical content is the separation of system type, exact state homomorphism, chosen observation interface, behavioral bundle and one-step lifting. It gives a concise route from compositional compatibility to the two post-fixed transfer directions. The quotient-kernel characterization is also useful when exact abstraction is genuinely the intended object.

The paper's own §5 limitations reserve lax abstractions with explicit error, quantitative approximation guarantees, diagnostics, training objectives and practical learning algorithms for future work. Appendix F adds the explicit stateful-feedback and temporal-abstraction boundaries.

For predictive-state research, the main questions it does **not** settle are whether observations admit useful lossy compression, how a sufficient state is acquired from finite data, how much installed information a representation costs, whether its recurrence is realizable with finite resources and what approximate errors do to decision performance. Those are absent targets, not negative theorems supplied by this paper.

No FP object mapping or transfer claim is proposed. The note records a recent exact-semantics framework, its valid transfer directions, two small independently checked scope examples and the premises required to use the logical–quantitative bridge.
