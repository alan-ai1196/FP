# Limit-sure reachability: small controllers, symbolic ranks and probability precision

## Source, edition and actual reading

- **Authors:** Ali Asadi, Krishnendu Chatterjee, Raimundo Saona and Ali Shafiee.
- **Completed edition:** [UAI 2025 official proceedings](https://proceedings.mlr.press/v286/asadi25b.html), PMLR **286**:238–256, July 21–25, 2025. [Official 19-page PDF](https://raw.githubusercontent.com/mlresearch/v286/main/assets/asadi25b/asadi25b.pdf). The first-page PDF footer says volume 244, whereas the authenticated publisher record says 286. This note uses the publisher's volume.
- **Full reading by Pro-C, November 26, 2026, Shanghai:** all 19 physical pages, §§1–4, all subsections 3.1–3.4, Appendices A–C, all proofs and displayed formulas, all three figures, Table 1, acknowledgements and all 38 printed references. The complete 1,246-line official PDF extraction was read in four contiguous blocks. Original physical pp. 2–5, 7, 12, 15–16 and 18–19 were visually inspected, including all three figures and the table. There are no empirical experiments, numbered algorithm boxes or body footnotes.
- **Separate author edition:** [arXiv:2412.00941v2](https://arxiv.org/abs/2412.00941v2), June 13, 2025, 09:06:25 UTC, **33 pages**, with complete proofs in the main text and no A–C appendix organization. A source assistant downloaded its PDF and complete TeX package and compared structure and extracted text. Differences include proof placement, restatements, citation formatting and captions. Mathematical equivalence of all changes was not established. This edition is not marked fully read, and the v1 historical preprint was not read.
- **Scoped dependency:** [Junges et al., UAI 2018](https://proceedings.mlr.press/r16/junges18a.html), current PMLR reissue R16:518–528, reissued October 4, 2026, [11-page PDF](https://raw.githubusercontent.com/mlresearch/r16/main/assets/junges18a/junges18a.pdf). Read selected §3–4 material on physical pp. 4–6, including Problems 1–2, the correspondence and reduction statements, Corollary 1, Theorems 1–4, the simple-pMC restriction and associated examples. These three PDF pages were visually inspected. The remaining paper and experiments were not read. This is a 2018 mathematical dependency, not a new 2026 paper or a new historical full-reading queue.
- **Verification boundary:** bounded manual checks of memory semantics, the rank-certificate size argument, explicit formulas in the four-state example, local proof notation and one counterexample to the claimed fixed-memory use of the SAT gadget. Assisting readers independently checked these interfaces. Imported real-algebraic, stochastic-game and directed-tree theorems were not independently re-proved. No exhaustive search, proof script, formalization or experimental reproduction was performed. No AI assistance disclosure was located in the read final edition.
- **Ignored source cache:** literature/corpus/pro_c/asadi25b/, with separate arxiv-v2/ and dependency-junges2018/ directories. No FP core files were edited.

**Main finding:** the paper gives a useful symbolic certificate route for qualitative reachability under a bounded controller state count. Its certificate describes relative orders of rare action probabilities, not a finite-precision implementation at a requested failure tolerance. The memoryless hardness argument and the NP upper-bound construction have identifiable scope. The displayed SAT gadget does not prove hardness for every fixed memory size, as a two-state controller defeats its unsatisfiable-instance direction. The unrestricted parametric-Markov-chain extension also exceeds the scope of the cited 2018 equivalence. Several local formula omissions can be repaired explicitly without constituting a counterexample to the memoryless NP-completeness conclusion.

## 1. The controller model and the quantifiers

The POMDP has finite state set \(S\), action set \(A\), deterministic observation map \(o:S\to Z\), transition probabilities \(\delta(s,a)(s')\), a specified initial state \(s_0\) and a target \(\top\). Reaching the target at least once is the objective. For the subsequent absorbing-class analysis, make \(\top\) absorbing, which preserves this event even if its observation aliases other states.

A controller with \(m\) memory states is

\[
\sigma=(\sigma_a,\sigma_u,M,m_0),\qquad |M|=m,
\]

\[
\sigma_a:M\times Z\to\Delta(A),\qquad
\sigma_u:M\times Z\times A\to M.
\]

Action selection is randomized. The update is **deterministic given the current memory, current observation and selected action**. It does not receive the next observation. In particular,

\[
\Pr(a,\mu'\mid\mu,z)
=\sigma_a(\mu,z)(a)
\mathbf1\{\mu'=\sigma_u(\mu,z,a)\}.
\]

The chosen action can transmit randomness into the update, but this is not an arbitrary joint kernel on \(A\times M\). The fixed-\(m\) statement should not silently be applied to a different controller model with an independent randomized memory update.

Memoryless means \(m=1\), with \(\sigma_a:Z\to\Delta(A)\). The objective distinguishes

\[
\begin{aligned}
\text{almost sure:}\quad&
\exists\sigma\in\Sigma_m:
\Pr^\sigma_{s_0}(\operatorname{Reach}(\top))=1,\\
\text{limit sure:}\quad&
\forall\eta>0\ \exists\sigma_\eta\in\Sigma_m:
\Pr^{\sigma_\eta}_{s_0}(\operatorname{Reach}(\top))\geq1-\eta.
\end{aligned}
\]

The memory bound is fixed before \(\eta\) varies. The action probabilities are allowed to depend on \(\eta\). A supremum equal to one need not be attained by any one policy, and the pointwise limit of an approaching family need not preserve its success value.

This is a decision problem for a supplied finite model. It is not a learning theorem, a bound on discovering a controller from trajectories or a guarantee that a practical NP solver finds one quickly.

## 2. The four-state example makes the precision cost visible

Example 1 and Figure 1, printed pp. 240–241, use a blind POMDP with states \(s_0,s_1,\bot,\top\) and two actions, wait and commit. Every state has the same observation, including both absorbing states.

Let \(\alpha\in(0,1)\) be the probability that wait moves \(s_0\) to \(s_1\). Otherwise wait leaves the process at \(s_0\). Wait leaves \(s_1\) unchanged. Commit sends \(s_0\) to failure \(\bot\) and \(s_1\) to success \(\top\). The paper does not specify \(\alpha=1/2\).

No history policy succeeds with probability one. Committing at any finite time leaves a positive probability of still being in \(s_0\). Never committing cannot reach \(\top\). Yet a memoryless policy that commits very rarely makes failure arbitrarily unlikely.

### Direct calculation, beyond the paper's qualitative example

Let the stationary commit probability be \(q\in(0,1)\). The failure probability \(F\) satisfies

\[
F=q+(1-q)(1-\alpha)F,
\]

so

\[
F(q)=\frac{q}{\alpha+(1-\alpha)q},
\qquad
V(q)=\frac{\alpha(1-q)}{\alpha+(1-\alpha)q}.
\]

For an error tolerance \(0<\eta<1\),

\[
F(q)\leq\eta
\quad\Longleftrightarrow\quad
q\leq\frac{\eta\alpha}{1-\eta(1-\alpha)}.
\]

One sufficient dyadic choice is

\[
q=2^{-b},\qquad
b=\left\lceil\log_2\frac1{\eta\alpha}\right\rceil.
\]

The controller still has one state, while the probability resolution becomes finer as \(\eta\) decreases. With this choice the expected number of actions until the **first commit, hence either absorption**, is

\[
\mathbb E[T_{\mathrm{commit}}]=1/q
=\Theta((\eta\alpha)^{-1}).
\]

This is not the unconditional expected time to reach the success target. Every fixed \(q>0\) has positive failure probability, so that latter hitting time has infinite expectation when failed trajectories are assigned time infinity.

For comparison, waiting exactly \(N\) times then committing has failure probability \((1-\alpha)^N\) and can be implemented with \(N+1\) memory states. These are different resource allocations: counting needs memory states, while rare random commitment needs probability resolution and a longer expected wait.

Figure 2 uses a family with commit probability \(\varepsilon\). Its \(\varepsilon\) is an asymptotic parameter, not automatically the achieved failure tolerance. With the normalized rank family \(q=\varepsilon/(1+\varepsilon)\), the failure probability is instead \(\varepsilon/(\alpha+\varepsilon)\).

At \(q=0\), success is zero. This explains why retaining only the limiting policy loses the useful information. The relative rate at which an action vanishes is part of the certificate.

## 3. How the NP certificate is constructed

Theorem 1 states NP-completeness for the memoryless problem. The upper-bound route in §3.2 has three substantive transformations.

### Remove observations by adding ineffective actions

Lemma 1 changes \(A\) to \(A\times Z\), retains \(S\), and gives the controller one observation. Action \((a,z)\) executes \(a\) when \(z=o(s)\), and otherwise self-loops.

An original policy is represented by

\[
\sigma'((a,z))=\frac{\sigma(z)(a)}{|Z|}.
\]

Deleting unsuccessful observation guesses recovers the original state evolution. In this forward construction there are on average \(|Z|\) blind actions per original transition. The reduction preserves infinite-horizon reachability value, not a fixed deadline or the same action budget.

The reverse conditional distribution in Appendix A divides by \(\sum_a\sigma'((a,z))\). When that denominator is zero, choose an arbitrary original action distribution at \(z\). The blind process would stay forever at a non-target state with that observation. The original continuation can only improve its eventual success relative to that zero continuation. Equality of each policy's coupled dynamics need not hold there, but the value inequality needed for the reduction survives.

### Replace an approaching family by asymptotic orders

The paper uses a real-closed field of Puiseux germs near \(0^+\), Tarski transfer and the least-fixed-point characterization of reachability to obtain a symbolic policy witness.

For each action of positive support, write its leading order as \(r_a\), with positive leading coefficient. The environment probabilities are fixed and nonnegative. Consequently there is no cancellation in

\[
\delta^\varepsilon(s,t)
=\sum_a\sigma^\varepsilon(a)\delta(s,a)(t),
\]

and its order is

\[
r(s,t)=\min_{\substack{a\in\operatorname{supp}\sigma\\\delta(s,a)(t)>0}}r_a.
\]

Actions of identically zero probability must remain outside the support. Replacing the other action probabilities by normalized monomials retains the relevant orders:

\[
\widetilde\sigma^\varepsilon(a)
=\frac{\varepsilon^{r_a}}
{\sum_{b\text{ in support}}\varepsilon^{r_b}}.
\]

This preserves qualitative exit supports and the subsequent communicating-class graph. It does not preserve the numerical exit probabilities.

A Puiseux communicating class is a set whose states are mutually reached with limiting probability one before exit. These classes form a laminar family with at most \(2|S|-1\) members. The paper characterizes limit-sure reachability by the absence of a reachable absorbing class other than the absorbing target.

### Integer ranks can have short descriptions

Lemma 6 preserves the ordering of action exponents and comparisons between sums of exponents on exit forests. This yields finitely many homogeneous linear equalities and weak or strict inequalities. A strict relation \(L<R\) can, after scaling a feasible solution, be replaced by \(L+1\leq R\).

The system can have many constraints. The certificate contains the chosen action support and an integer rank per active action, rather than all of those constraints. A rational-solution bound followed by clearing denominators gives polynomial **bit length**, not polynomial rank magnitude.

For clarity, a bounded completion of the paper's Cramer-rule argument is as follows. With \(d\) active blind actions and \(n=|S|\), each forest has at most \(n\) edges, so coefficients in forest comparisons are \(O(n)\). A nonempty nonnegative feasible polyhedron has a vertex determined by at most \(d\) independent active constraints. Determinant bounds and a common denominator give a sufficient rank description of \(O(d(\log d+\log n))\) bits per action. This explicit order is a reading-side derivation, not a numerical bound printed in the paper. A common shift makes the smallest rank zero without changing comparisons among forests of the same class.

The rank values may be exponentially large. Even at \(\varepsilon=1/2\), expanding \(2^{-r_a}\) as an ordinary rational denominator can take space proportional to the value \(r_a\), far larger than the symbolic rank's bit length.

### Verification uses weighted forests, not numerical probability estimation

Lemma 7 constructs the communicating-class graph. It obtains minimum exit-forest orders with minimum-weight directed spanning-tree computations after collapsing the outside of a class. To test whether a specified outside state belongs to an exit support, it fixes a candidate last exit edge and compares constrained and unrestricted minimum weights.

Bottom strongly connected components add larger classes. A final graph search checks that only the target is an accessible absorbing class. The bounded check supports this route assuming the stated communicating-class characterization and the corrected forest convention below.

Under the usual explicit finite input encoding, for example binary rational transition probabilities, these steps require positivity tests on fixed environment transitions and arithmetic on polynomial-bit integers. The paper does not specify a model of arbitrary real-number oracles. Its complexity claim should not be transferred to an encoding in which even positivity is unavailable.

## 4. Local formulas that require explicit repair

These issues are in the authenticated final PDF, not merely extraction noise.

### The first-order reachability formula lacks its boundary

Lemma 2, printed pp. 243 and 249, writes a homogeneous fixed-point equation for every state and asks for the least solution, without \(v_\top=1\) or an explicit bounded domain for \(u,v\). The appendix repeats the omission.

Literally, every constant vector solves the homogeneous equation, so there is no least real solution. Merely adding nonnegativity would select the zero vector.

The intended encoding follows the paper's preceding Theorem 4:

\[
v\in[0,1]^S,\quad v_\top=1,\quad
v_s=\sum_t\delta^\sigma(s,t)v_t\quad(s\ne\top),
\]

with minimality only among \(u\in[0,1]^S\) obeying the same target boundary. This restores the reachability quantity used by the real-closed-field argument. The missing conditions must be supplied rather than assumed present in the displayed formula.

### Exit graphs must be forests with one outgoing edge per internal state

The printed p. 242 definition only requires at least one outgoing edge from every state in \(B\). The spanning-tree verifier needs exactly one. The wider definition also changes the numerical formula quoted as Theorem 6.

Take \(B=\{s\}\) and constant transitions \(P(s,t)=P(s,u)=1/2\). The wider definition admits the two single-edge graphs and the graph with both edges, all of order zero. Their probability products are \(1/2,1/2,1/4\). The displayed ratio would assign exit probability

\[
\frac{1/2+1/4}{1/2+1/2+1/4}=\frac35
\]

to \(t\), although the true probability is \(1/2\). Requiring exactly one outgoing edge removes the spurious graph. This is a definition-level correction to the imported formula. It does not itself refute the qualitative NP route, whose verifier already uses forests.

### The action-order formulas contain two local index errors

On printed p. 252, the definition of \(i(a)\) uses the whole transition sum with free states \(s,\widetilde s\), rather than the order of the action probability, and omits the nonzero condition inside the displayed set. The intended quantity is \(\operatorname{val}(\sigma_a)\) for active actions.

In the next definition, the universal competitor \(\widetilde a\) must be required to enable the same edge:

\[
\delta(s,\widetilde a)(\widetilde s)>0
\Longrightarrow i(a)\leq i(\widetilde a).
\]

The PDF instead repeats \(a\) in that premise. Taken literally, it asks for a global minimum action even when that action cannot realize the edge. These are repairable local formulas, not an independently certified implementation as printed.

## 5. Fixed-memory upper bounds and the hardness gap

### The product construction is valid with its existential update-table quantifier

For a fixed deterministic update \(u:[m]\times Z\times A\to[m]\), Appendix C defines

\[
\widetilde S=S\times[m],\quad
\widetilde Z=Z\times[m],\quad
\widetilde o(s,\mu)=(o(s),\mu),
\]

\[
\widetilde\delta((s,\mu),a)(s',\mu')
=\delta(s,a)(s')\mathbf1\{\mu'=u(\mu,o(s),a)\}.
\]

Only the controller's own memory becomes visible. The hidden environment state does not. The product has \(|S|m\) states and \(|Z|m\) observations.

There are finitely many deterministic update tables for each fixed \(m\). If some sequence of \(m\)-state policies approaches value one, one update table has a subsequence whose values approach one. Therefore the correct equivalence is existence of **some** such product with memoryless supremum one, not equivalence for every arbitrarily fixed update table.

Guessing the table and then the rank certificate gives the stated NP upper-bound route. Remark 1 also allows \(m\) polynomial in the explicit POMDP input size. This does not give an NP bound for an arbitrarily huge memory limit encoded by a short binary integer.

### The displayed SAT reduction establishes the memoryless case

Appendix B chooses a clause uniformly, visits its three literal states in order and goes to \(\top\) at the first satisfied literal. A failed third literal goes to \(\bot\). Observations reveal the variable, not its sign or clause. The initial, success and failure states have their own observations.

For a deterministic memoryless policy, the action at variable \(x_i\) gives one fixed truth assignment. A satisfiable formula therefore has success one. An unsatisfiable formula with \(c\) clauses has success at most \(1-1/c\).

Restricting to 3-SAT clauses with distinct variables, randomized memoryless policies do not improve that upper bound. Draw each variable's action once in advance according to its stationary distribution. Since no variable is queried twice along a clause path, this mixture of deterministic assignments induces the same path probabilities. This direct argument supports the memoryless reduction without needing the appendix's informal perfect-recall interpretation.

### Two memory states invalidate the same gadget's fixed-\(m\) extension

Proposition 1 claims hardness for every fixed memory amount. Its displayed appendix reduction does not establish that extension.

Consider the conjunction of all eight sign patterns on three distinct variables, ordered as follows:

\[
\begin{aligned}
&(x\vee y\vee z)\ \wedge\
(x\vee y\vee\neg z)\ \wedge\
(x\vee\neg y\vee z)\ \wedge\
(x\vee\neg y\vee\neg z)\\
&\wedge\ (y\vee\neg x\vee z)\ \wedge\
(y\vee\neg x\vee\neg z)\ \wedge\
(z\vee\neg x\vee\neg y)\ \wedge\
(\neg x\vee\neg y\vee\neg z).
\end{aligned}
\]

Every assignment falsifies one clause, so the formula is unsatisfiable. Seven clauses have a positive first literal. The remaining clause is entirely negative.

The original construction has 27 environment states, six observations and two actions. Use memory states \(0,1\), initially \(0\). Keep memory unchanged at \(s_0\). At a variable observation, choose true in memory \(0\), false in memory \(1\), and flip the memory after the action.

All seven positive-first clauses reach \(\top\) on their first literal. The all-negative clause fails its first literal, then reaches \(\top\) on its second. Thus this **deterministic two-state controller is almost-sure winning** on the gadget for an unsatisfiable formula. No repeated variable or repeated observation within a clause is involved.

Extra unused states give the same counterexample for any bound \(m\geq2\). This disproves the claimed use of this particular reduction for every fixed \(m\). It does not disprove the overall fixed-\(m\) hardness proposition, the fixed-memory NP upper bound, or the memoryless Theorem 1. An additional hardness construction is needed before this note treats the every-fixed-\(m\) extension as independently supported.

If the problem instead takes a memory bound as part of the input and includes the case \(m=1\), memoryless hardness already gives hardness of that combined input problem. That is a different assertion from hardness separately at every fixed \(m\).

## 6. Extensions: parity is support based, arbitrary pMCs need more

### Parity

Corollary 3 takes a subsequence of policies with the same action support, possible because there are finitely many supports. The resulting Markov chains have the same recurrent classes. A class satisfies the parity objective precisely when its minimum recurring priority is even. Reaching the union of these good classes reduces the parity question to reachability.

This explains the upper-bound mechanism after guessing the support and, for finite memory, the update table. Its cited every-fixed-\(m\) hardness still has the preceding qualification. An arbitrary LTL formula also has a separate automaton-translation cost, which should not be omitted by quoting the explicit parity-graph result.

### Parametric Markov chains

Corollary 4 and Appendix C cite Junges et al. 2018, Corollary 1, as a two-way equivalence between POMDP policy synthesis and parameter synthesis for pMCs. The scoped primary-source check finds a narrower statement:

- Junges Corollary 1 concerns a pMC **induced from a particular POMDP/controller construction** and its corresponding controller instantiation.
- Its reverse reduction and Theorems 3–4 use **simple pMCs**, with transition expressions in
  \[
  \mathbb Q\ \cup\ \{p,1-p:p\in V\}.
  \]
- The listed polynomially interreducible problems contain simple-pMC instantiation, not unrestricted polynomial pMC instantiation.

The primary paper explicitly discusses why the naive reverse mapping is obstructed for more general parameter combinations. Its controller model also allows a randomized memory update, so it should not be silently identified with Asadi's deterministic-update model at the same memory count.

The threshold-independent simple-pMC construction supports carrying the memoryless qualitative question across that restricted interface. The citation does not establish the unqualified extension to arbitrary pMC syntax, parameter constraints or encodings. This note records a missing scope restriction, not a general pMC complexity classification. No separate historical full reading was undertaken.

## 7. Reusable result and unresolved boundaries

The useful instrument is a symbolic hierarchy of rare actions. It can distinguish a policy family whose reachability tends to one from a limiting stationary policy whose value is zero. In the qualitative decision problem, support and relative orders can replace detailed real-valued probabilities.

The resources remain distinct:

| Resource | What the reading establishes |
|---|---|
| Controller state count | Fixed \(m\), or a polynomially bounded \(m\), under the stated update model |
| Symbolic certificate | Support and polynomial-bit integer ranks, plus a deterministic update table when needed |
| Certificate verification | Polynomial graph and weighted-forest operations under the explicit finite input model and stated class characterization |
| Required action-probability precision for error \(\eta\) | Not bounded in general by the paper |
| Sampling and time to absorption | Not priced by the NP theorem, and explicitly diverging in the four-state example as precision increases |
| Learning the model or controller from data | Outside the result |

The local first-order and forest definitions should be repaired before reuse. The fixed-\(m\geq2\) hardness proof and unrestricted pMC extension should be cited as unresolved at the coverage established here. These qualifications leave the paper's central asymptotic-certificate idea useful.

No FP architecture, statistical acquisition rule or state-formation theorem is derived. A finite controller-state count alone does not account for installed probability parameters, random sampling, waiting time or how an unknown model was learned.
