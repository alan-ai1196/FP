# Bayesian updates from coalgebraic determinisation

## Source and actual coverage

- **Authors:** Manuel Baltieri and Nathaniel Virgo.
- **Read edition:** [arXiv:2607.00034v1](https://arxiv.org/abs/2607.00034v1), submitted June 24, 2026, 11:49:30 UTC. The June submission date is retained despite the July-style identifier. The November 26 primary history lists only v1. [15-page PDF](https://arxiv.org/pdf/2607.00034v1) and [complete source](https://arxiv.org/src/2607.00034v1).
- **Publication status:** the [ACT 2026 official accepted list](https://actconf2026.github.io/accepted.html) lists the same authors and shorter title, *Bayesian updates from determinisation*, under **Talks**, separately from Proceedings. Its [conference-hosted manuscript](https://actconf2026.github.io/papers/ACT_2026_paper_54.pdf) has 14 pages and is not the PDF read here. A separate source assistant inspected its title page and metadata, not its body. No EPTCS publication entry or publication DOI was authenticated. The [author's publications page](https://manuelbaltieri.com/research/publications/) lists the arXiv preprint. The arXiv DOI is not a proceedings DOI.
- **Full reading by Pro-C, November 26, 2026, Shanghai:** all 15 physical pages, §§1–5, the complete main source and notation definitions, all 33 numbered displays, both panels of the algebra-law diagram, every published definition/proposition/proof, the funding acknowledgement, sole body footnote and all 30 printed references. Original PDF pp. 3–4 and 6–13 were visually checked. No numbered figures, tables, appendices or separate paper supplement are present.
- **Source coverage boundary:** `main.tex` has 1,020 lines including a long commented-out alternative proof. The commented draft is not counted as a published proof. All 311 lines of `math_commands.tex` were inspected. The large bundled Zotero database contains thousands of unused records and was not read as if it were the paper's bibliography.
- **Verification:** bounded manual checks of the algebra transport, pointwise exponent algebra, positive-output Bayesian update and selected typing/generalization statements, with a separate assisting mathematical reader. The main result is presented as a sketch proof. Imported final-coalgebra proofs were not independently certified. No proof scripts, formal replay or experiments were performed.
- **Source cache:** ignored `literature/corpus/pro_c/2607.00034v1/`.

**Main finding:** on sets with finitely supported distributions, the chosen determinisation composite does give exactly the usual Bayesian filter for a supplied stochastic Mealy machine. Its contribution is a precise structural identification and a richer choice of observable semantics. It supplies neither a finite belief-state representation nor a procedure for learning the supplied model. Several surrounding typing and generality statements need correction, without invalidating the core distribution-monad calculation.

## 1. The semantic problem being solved

The standard structured Moore construction used in §2 has one-step type

\[
S\longrightarrow \mathcal D(O)\times\mathcal D(S)^I.
\]

Its determinised carrier is \(\mathcal D(S)\). An input pushes a prior forward through the transition kernel, while the output component averages the current output distribution. The resulting final semantics assigns

\[
g:I^*\longrightarrow\mathcal D(O).
\]

It describes the output distribution after each input word. It does not condition the next internal distribution on every realized intermediate output.

The limitation concerns this semantics, not an inherent inability of Moore models to represent filtering problems. For an elementary illustration, consider a process that repeats one initially fair hidden bit forever and a process that produces independent fair bits. Their individual-time output marginals are identical, while the probabilities of two equal successive outputs differ. Last-output marginals alone do not determine their joint observation histories. An interactive controller can use those histories.

The paper therefore chooses a Mealy transition that retains the joint law of output and next hidden state:

\[
K:S\longrightarrow\mathcal D(O\times S)^I.
\]

This is the information that can be mixed over a prior and then conditioned on the output that actually occurred. The paper relates the resulting machine to belief MDPs and mixed-state presentations. It does not claim to have invented Bayesian filtering.

## 2. Support is part of the transition type

Definition 7 works on \(\mathbf{Set}\). For a monad \(T\), it requires designated subsets \(\operatorname{supp}(p)\subseteq X\) and isomorphisms

\[
\Phi_{X,Y}:T(X\times Y)
\cong
\coprod_{p\in T(X)}T(Y)^{\operatorname{supp}(p)},
\]

natural in \(Y\). In the probabilistic case \(T=\mathcal D\), distributions have finite support and

\[
\Phi(\rho)=\left(\rho_X,
x\mapsto\rho(\cdot\mid x)\right),
\qquad x\in\operatorname{supp}(\rho_X).
\]

The inverse multiplies the marginal by the conditional on supported points and assigns zero outside that marginal support. Restricting the conditional's domain makes it a unique actual function, avoiding arbitrary posterior choices after zero-probability observations.

Finite nonempty powersets supply another example. A nonempty relation \(U\subseteq X\times Y\) is equivalent to its nonempty projection on \(X\), together with its nonempty fibers over that projection. The unrestricted nonempty powerset also has this decomposition. The formal abstraction does not itself require finite support for every monad. The finite-support restriction is explicit for \(\mathcal D\).

The authors say that ordinary powersets with the empty set, partiality and subdistribution monads do not fit in the most immediate way. They do not claim an impossibility result for every reformulation of those effects. They also explicitly exclude a general measure-theoretic extension. General Borel conditional laws are not obtained merely by replacing finite sums with integrals in this support-based isomorphism.

Remark 8 compares this setup with hypernormalisation and strongly representable Markov categories. It constructs a map from a joint law to a joint distribution of an observation and its posterior distribution. The relationship between the two general frameworks is left open. The paper's bibliography specifically notes that the strongly representable material it cites occurs in version 2 of the Fritz et al. preprint, not version 3 or the published version. No reading credit for that external edition is implied here.

## 3. Theorem 23: the exact composite and its assumptions

Let

\[
F(X)=\left(\coprod_{p\in T(O)}X^{\operatorname{supp}(p)}\right)^I.
\]

A supported Mealy machine has type \(f:S\to F(TS)\). A unifilar machine has type \(X\to F(X)\). The latter still generates stochastic outputs when \(T=\mathcal D\). Its next state is deterministic **given the current state, input and supported realized output**.

The general structured-coalgebra construction starts with an algebra

\[
\xi:T(F(TS))\longrightarrow F(TS)
\]

and extends \(f\) to

\[
f^\sharp=\xi\circ T(f):TS\longrightarrow F(TS).
\]

Proposition 22 supplies the required algebra by transporting the free algebra along the marginal/conditional isomorphism:

\[
\nu=\Phi\circ\mu\circ T(\Phi^{-1}).
\]

On sets, taking one copy of this algebra for each input gives the pointwise exponent algebra \(\xi=\nu^{(I)}\). Transport preserves the unit and multiplication laws. These checks justify the particular algebra needed by the theorem. The paper deliberately works with the algebra for the chosen construction and does not develop a global Eilenberg–Moore distributive law.

For a supplied prior \(q\in\mathcal D(S)\) and input \(i\), the full composite is simply

\[
\rho_{q,i}(o,s')=\sum_s q(s)K_i(s)(o,s'),
\]

followed by

\[
p_{q,i}(o)=\sum_{s'}\rho_{q,i}(o,s'),
\qquad
q'_{q,i,o}(s')=
\frac{\rho_{q,i}(o,s')}{p_{q,i}(o)}
\quad\text{when }p_{q,i}(o)>0.
\]

The monad multiplication performs the prior-weighted mixture. The final \(\Phi\) performs marginalization and conditioning. This is exactly the explicit unifilarisation of Definition 21. Theorem 23's sketch on pp. 11–12 uncurries the algebra and identifies these stages in Eqs. 26–27. The bounded independent check found no obstruction to this identity.

No posterior branch exists for an output with \(p_{q,i}(o)=0\). This is appropriate for the machine's own generated trajectories. It supplies no rule for out-of-model external observations, misspecified likelihoods or numerical near-zero denominators.

The sets \(S,I,O\) may be infinite. At any one step, a finitely supported prior and finitely supported kernels produce a finite union of finite joint supports, so the new joint law and its positive-output posteriors remain finitely supported. There is no uniform bound on support growth over time and no restriction to finitely many possible probability values.

## 4. Causal behavior retains full observation histories

Definition 24 describes a causal stochastic behavior by a family

\[
b_n:I^n\to\mathcal D(O^n),\qquad n\ge1,
\]

satisfying prefix consistency

\[
\mathcal D(\pi_n^O)\circ b_{n+1}
=b_n\circ\pi_n^I.
\]

The distribution of the first \(n\) outputs depends only on the first \(n\) inputs. In the Mealy timing convention an output may depend on its current input, but not a later input.

After a supported pair \((i,o)\), the behavior evolves by conditioning its longer output-word law on its first output. With the typing correction below, the continuation is

\[
\bigl(b\mathbin{\bullet}(i,o)\bigr)_k(i_1,\ldots,i_k)
=
\left(b_{k+1}(i,i_1,\ldots,i_k)\right)_{O^k\mid o}.
\]

Proposition 25 identifies all such behaviors with the final coalgebra for the unifilar functor. Its proof is imported from Virgo 2023, with adaptations from the earlier comb-machine convention stated but not fully written out here. This note records the claimed characterization and its observable meaning, without certifying the full external finality argument.

This final semantics is richer than the selected Moore semantics because it preserves full causal input-output word laws. It is not a finite machine-synthesis algorithm. Mapping a belief to its behavior also does not establish that different beliefs are behaviorally distinct or supply an effective minimal quotient.

## 5. Four local corrections and their scope

| Location | Literal problem | Consequence and repair |
|---|---|---|
| Introduction, p. 2 | Calls \(\Phi\) natural in \(X\). | Definition 7 and the later construction use naturality in \(Y\), the state variable. Read the formal definition as authoritative. |
| Proposition 3 and preceding sentence, p. 4 | Claims canonical strength for every monad on an arbitrary Cartesian closed category. | This generality is too broad. The pointwise exponent algebra is valid on \(\mathbf{Set}\), which is sufficient for the actual construction. |
| Remark 15, p. 9 | Says the nonempty powerset monad lacks a final coalgebra. | As a claim about the endofunctor \(\mathcal P^+\), it is false. The singleton coalgebra is final. A claim about another composite functor would have to identify it. |
| Equation 31, p. 13 | Conditions a law on \(O^{k+1}\) but labels the remaining law \(O^{k-1}\). | The remaining law is on \(O^k\). The printed expression is ill typed already at \(k=1\). This has a direct correction and does not refute the intended finality claim. |

The powerset correction is elementary: \(\mathcal P^+(1)=1\), and direct image sends every nonempty successor set to that singleton. Hence the unique map from any \(\mathcal P^+\)-coalgebra to \(1\) is a coalgebra morphism.

For the strength qualification, a bounded counterexample to the broad wording is available on the Cartesian closed category \(\mathbf{Set}\times\mathbf{Set}\). The coproduct–diagonal adjunction induces

\[
T(X,Y)=(X\sqcup Y,X\sqcup Y).
\]

With \(A=(\varnothing,1)\) and \(B=(1,\varnothing)\), a strength would need a morphism

\[
TA\times B=(1,\varnothing)
\longrightarrow T(A\times B)=(\varnothing,\varnothing),
\]

which does not exist. This checks the excess generality without challenging the Set-based algebra used in Theorem 23.

These are scoped corrections, not a whole-paper refutation. In particular, none changes the valid prior-mixture and positive-output conditioning formula.

## 6. Exact filtering does not imply finite predictive memory

For a finite hidden state set with at least two elements, \(\mathcal D(S)\) is an uncountable simplex. Restricting to the states reachable from one prior also need not make the filter finite.

A direct example has a persistent hidden bit, prior probability \(1/2\) for each state, and conditional output-one probabilities \(1/3\) and \(2/3\). After \(n\) consecutive ones,

\[
q_n(S=1)=\frac{2^n}{1+2^n}.
\]

Every such prefix has positive probability, and all these beliefs are distinct. Their next-output-one probabilities are \(1/3+q_n/3\), so they are also predictively distinct. This is an elementary scope example in this note, not a counterexample to the authors' theorem. It shows why finite support and unifilarity do not bound the number or precision of belief states.

The paper supplies no kernel-learning rule, state-discovery procedure, finite-state realization criterion, precision budget, sample-complexity result or approximate-filter error bound. It starts with the machine and prior semantics. Its reward/control motivation does not add a planning algorithm or a regret theorem.

## 7. Research disposition and dependencies

The useful object is a supplied one-step joint law together with an observation-indexed posterior update. The support-indexed transition type makes the impossible-observation boundary explicit. The useful conceptual separation is between predicting one output marginal after a word and preserving the whole causal output-word law.

The cited 2026 Kori–Watanabe paper uses a different route through belief decomposition. This edition states that comparison in its introduction but does not establish a general equivalence between every detail of the two frameworks. Its full text has not been read at this completion boundary. The earlier Silva determinisation construction and Virgo finality result remain imported dependencies, not additional full readings.

For FP, this is precise adjacent semantics. No mapping from a learned FP state to the supplied hidden-state beliefs, no finite compression theorem and no experimental advantage have been established. The note proposes no research-core change and does not duplicate Pro-B's separate randomized posterior-storage request.

**Completion boundary:** arXiv v1 is fully read. The distinct 14-page ACT-hosted edition, external proofs and general measure-theoretic extensions have no full-reading credit. No empirical or formal verification is claimed.
