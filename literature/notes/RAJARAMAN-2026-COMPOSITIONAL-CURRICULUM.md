# Learning to Reason with Curriculum II: Compositional Generalization

## Source, edition and reading boundary

- Authors: Nived Rajaraman, Audrey Huang, Miroslav Dudík, Robert Schapire, Dylan Foster and Akshay Krishnamurthy.
- Read edition: [arXiv:2606.27721v1](https://arxiv.org/abs/2606.27721v1), submitted June 26, 2026 at 05:09:08 UTC. The [versioned PDF](https://arxiv.org/pdf/2606.27721v1) has 82 pages. The [complete TeX source](https://arxiv.org/src/2606.27721v1) and the [Microsoft Research publication page](https://www.microsoft.com/en-us/research/publication/learning-to-reason-with-curriculum-ii-compositional-generalization/) were authenticated. Only v1 was listed in the November 26 check. The PDF's June 29 date comes from its build and is not the arXiv submission date.
- Publication status: Microsoft Research author preprint. No separate reviewed edition was authenticated. This is not an OpenAI or Anthropic official-source reading.
- Pro-E completed the full reading on November 26, 2026, Shanghai. Coverage is all main Sections 1–6, Appendices A–F, every active proof and algorithm, mathematical displays, footnotes, all five figures and the complete printed reference list. The main reader covered the active TeX and inspected the original figures on pp. 3, 11, 25, 37 and 48, plus the key conditioning formulas on pp. 66 and 75. Source comments were excluded from claims about the published paper.
- Three bounded assisting checks separately examined the precision schedule, the conditional-distribution identity and the RL optimization dependency. The main reader checked the corresponding sources personally. The independent calculations below are ordinary mathematical arguments, not a formal proof or certification of the entire paper. No empirical reproduction was needed because this paper's contribution is theoretical.
- PDF SHA-256: `2ccb427b8243b113af5fde3f7299958cad7606e6aa7240f0ddf013d26074369f`. Source archive SHA-256: `15a2fc7ba8e154db297989ecac34472f8dc08be9e3b25f74e9df0ff443ba1d60`.

**Reading assessment.** The paper formulates a substantive reduction from long semiautomaton simulation to short supervised or verified subproblems. Its information interfaces are substantially stronger than passive terminal-label learning. Two specific proof issues need to remain attached to the claimed upper bounds: the conditional-distribution identification in Lemma F.3 is false under the stated definitions, and the written top precision schedule does not imply the advertised accuracy dependence. The first issue has not been repaired here. Neither observation is a counterexample to the main existence theorem. The RL path also assumes a separate trajectory-list optimization primitive. Section 7 gives an independent linear sampling lower bound in the paper's black-box model.

## 1. The mathematical problem and supplied interfaces

The unknown target is a deterministic, time-homogeneous transition

\[
\pi^\star:S\times\Sigma\longrightarrow S,
\qquad s_t=\pi^\star(s_{t-1},w_t).
\]

The learner receives a state space, an input alphabet and a realizable class \(\mathcal F\) containing the target. An instance is \(x=(s_0,w_{1:T})\). Training instances are iid from an arbitrary distribution \(\rho\) on \(S\times\Sigma^T\), and the goal is small terminal-state error under that same distribution. The learned terminal predictor may be an ensemble/composition outside the one-step class.

This is learning to simulate an automaton with supplied state meanings. It does not identify an unknown minimal automaton from unlabeled histories. The state names, legal restart interface and temporal factorization are already available. No theorem constructs these objects from prediction alone.

The iSFT oracle supplies the exact state at the end of any queried prefix or constructed subproblem. A query can start at a supplied state and can have a different length from the training prompts. One complete state label costs one oracle call. Under a fixed-width encoding of arbitrary states in \(S\), each state label costs \(\lceil\log_2|S|\rceil\) bits. Reading a length-\(T\) input and computing the oracle's answer are also distinct from counting labels.

At the base, Definition 2.2 provides realizable next-state ERM on exact labeled examples

\[
(s,w)\longmapsto\pi^\star(s,w).
\]

The more general theorem permits any distribution-free weak learner with error at most \(1/4\) from \(n_{\mathrm{weak}}(\delta)\) iid examples, with failure probability at most \(\delta\). The generic assumption is

\[
n_{\mathrm{weak}}(\delta)
\le\operatorname{comp}(\mathcal F)\log(1/\delta).
\]

Natarajan dimension \(d\) and ERM give the displayed choice \(\operatorname{comp}(\mathcal F)=d\log|S|\). For a finite supplied class, its cardinality can instead give the usual \(\log|\mathcal F|\) dependence. This distinction explains why the regular-expression and finite-field examples need not pay an additional full state-space factor.

## 2. What the paper claims quantitatively

The results below describe the source's statements. The outstanding proof issue in Section 4 prevents this note from independently endorsing the full upper-bound chain.

### 2.1 Supervised curriculum

Theorem 3.4 states, for \(H=\sqrt{\log_2T}\in\mathbb N\), a high-probability terminal-error bound using

\[
n_{\mathrm{sample}},n_{\mathrm{query}}
\le
2^{\widetilde O(\sqrt{\log T})}
\frac{\operatorname{comp}(\mathcal F)
\log^2(1/\varepsilon)\log(1/\delta)}{\varepsilon}.
\]

The general Appendix C statement makes the weak-learner dependence explicit. With

\[
h_\varepsilon(T)
=2^{C\sqrt{\log T}\log\log T}\log^2(1/\varepsilon),
\]

Theorem C.1 bounds samples and queries by

\[
\frac{h_\varepsilon(T)}{\varepsilon}
\left[
n_{\mathrm{weak}}\!\left(\frac\delta{h_\varepsilon(T)}\right)
\vee\log\frac{h_\varepsilon(T)}\delta
\right],
\]

and base-learner calls by \(h_\varepsilon(T)\). The fixed-accuracy horizon dependence is subpolynomial. This does not mean sublinear total input-processing work or sublinear execution of every generated trajectory.

The extension to arbitrary \(T\) pads to an admissible \(T'\in[T,2T^2]\) and augments the state with a clock, enlarging the state space by a factor of \(T\). That is an explicit representation change. The weak-learning interface transfers, but the clock should not disappear in a bit or state-cardinality accounting.

### 2.2 The baselines have different feedback restrictions

| Comparison | Source statement | Restriction that matters |
|---|---|---|
| Full-CoT learners, Proposition 3.7 | A worst-case class needs \(\Omega(dT)\) queried states even for constant accuracy | Every chosen prompt must be labeled at all \(T\) positions |
| End-to-end learners, Proposition 3.9 | A worst-case class needs \(\Omega((dT+\log(1/\delta))/\varepsilon)\) prompts | Training obtains only each original prompt's terminal label |
| Curriculum learner | The displayed subpolynomial query bound | The learner can construct and label shorter instances and restart from intermediate states |

These are comparisons of protocols. They are not a lower bound against every algorithm with the curriculum learner's richer oracle. The end-to-end result is imported from Joshi et al. and was read in its use here, without promoting the cited paper to fully read.

### 2.3 The applications preserve strong supervision

For regular expressions of alphabetic length at most \(k\), the Glushkov NFA and powerset construction supply a shared state interpretation. The oracle returns reachable-state subsets, rather than only language membership. The reported statistical dependence uses the logarithm of the expression-class size, while the powerset state space can be exponential in \(k\).

For \(s_t=As_{t-1}+Bw_t\) over \(\mathbb F_q^d\), the finite class has size \(q^{2d^2}\). The same reduction gives a class-complexity factor of order \(d^2\log q\). The original text separately acknowledges that implementing the state oracle can use linear-in-\(T\) work even when parallel depth is small. Neither application learns its decomposition or internal state semantics from endpoint observations alone.

## 3. The algorithm and intended proof mechanism

For a length-\(T\) problem, split the word into \(L\) pieces of length \(\tau=T/L\). Oracle labels supply the true starting state of each piece. A short-instance predictor with error \(\varepsilon_0\) under the uniform mixture of true block marginals has composed terminal error at most \(L\varepsilon_0\). This union bound alone loses the benefit of shortening the horizon.

AutoLearn combines two operations. It boosts short predictors to sufficiently small error, then composes their plurality aggregate across the \(L\) blocks. The recursive version repeats this construction until the leaves are one-step weak learners. Half-integer layers perform boosting without length reduction. Integer layers combine boosting with length reduction. Children are learned in an ordered, adaptive sequence, and the final object is a hierarchy of plurality models and compositions.

The boosting potential is a binomial tail with reference error \(1/4\). At iteration \(j\), the weight of an instance depends on how many preceding models were correct there. Thus the algorithm focuses new supervision on parts where the ensemble still has insufficient agreement. The potential proof separates successful weak-learning iterations from truthful aborts whose residual contribution is small.

The unusual sampling issue is that one long prompt contains \(L\) correlated blocks. Selecting a block uniformly and then rejecting according to its boosting weight can waste most of these opportunities. The proposed inverted procedure instead tests all blocks with independent acceptance coins and returns one uniformly among the accepted positions. It returns at most one child example per parent prompt, preserving iid input to a weak learner after conditioning on previously trained models.

Write \(X=(X_0,\ldots,X_{L-1})\sim\mu\), let \(\bar\mu\) be the average marginal, and let \(w\) be a nonnegative weight. The ideal target is

\[
\nu(dx)=\frac{w(x)\bar\mu(dx)}{\int w\,d\bar\mu}.
\]

Inverted sampling produces a different law \(\widehat\nu\). The intended argument does not require \(\widehat\nu\) to be close to \(\nu\). Instead, it chooses a high-probability event \(\mathcal K\) on the joint tuple and the acceptance coins, conditions the tuple law on that event, and claims

\[
\nu_{\mathcal K}\propto w\,\overline{\mu_{\mathcal K}},
\qquad
\left\|\frac{\nu_{\mathcal K}}{\widehat\nu}\right\|_\infty
=O(c^{-1}\log L),
\qquad\Pr(\mathcal K^c)\le c.
\]

A recursive analogue tracks a nested sequence of good events. This change of measure is the substantive bridge from inverted samples to the boosting potential. The next section identifies a gap precisely at that bridge.

## 4. A conditional-distribution identity in the proof is false

### 4.1 Two distributions that must be distinguished

The definitions on p. 66 give \(\mu_{\mathcal K}\) as the conditional distribution of the tuple \(X\), with acceptance coins integrated out. Put

\[
p_i(X)=w(X_i)/\|w\|_\infty,
\qquad B_i=\mathbf1\{i\in\mathcal I\}.
\]

For any measurable set \(A\), the stated target therefore satisfies

\[
\nu_{\mathcal K}(A)=
\frac{\mathbb E[\mathbf1_{\mathcal K}\sum_i p_i(X)\mathbf1\{X_i\in A\}]}
{\mathbb E[\mathbf1_{\mathcal K}\sum_i p_i(X)]}.
\tag{1}
\]

Lemma F.3, pp. 75–76, identifies this target with the output of a further acceptance procedure. Its first equality and following count calculation instead yield

\[
R_{\mathcal K}(A)=
\frac{\mathbb E[\mathbf1_{\mathcal K}\sum_i B_i\mathbf1\{X_i\in A\}]}
{\mathbb E[\mathbf1_{\mathcal K}|\mathcal I|]}.
\tag{2}
\]

The event \(\mathcal K\) is defined using these same \(B_i\). The unconditional identity \(\mathbb E[B_i\mid X]=p_i(X)\) does not imply

\[
\mathbb E[\mathbf1_{\mathcal K}B_i\mid X]
=\Pr(\mathcal K\mid X)p_i(X).
\]

### 4.2 An exact witness using the paper's own event

Take \(L=2\), a deterministic tuple \(X=(a,b)\), \(w(a)=1\), \(w(b)=1/8\), \(c=1/2\), and let \(\mathcal U\) be the entire tuple space. Then

\[
\Pr(|\mathcal I|=1)=7/8,
\qquad\Pr(|\mathcal I|=2)=1/8.
\]

The number of dyadic bins is \(m=\lceil\log_2(L+1)\rceil=2\). Equation (65) calls a bin heavy when its conditional probability is at least \(c/m=1/4\). Only the bin \([1,2)\) is heavy. Equation (66) therefore gives

\[
\mathcal K=\{|\mathcal I|=1\}\quad\text{almost surely},
\qquad\Pr(\mathcal K)=7/8.
\]

The zero-acceptance branch has probability zero. All stated high-probability-event conditions are met. Since the tuple is deterministic, conditioning does not change its distribution, and (1) gives

\[
\nu_{\mathcal K}(\{b\})
=\frac{1/8}{1+1/8}=\frac19.
\]

On \(\mathcal K\), however, the only accepted position is \(a\). Equation (2) gives

\[
R_{\mathcal K}(\{b\})=0.
\]

Thus the identification of the two distributions is false. This is not a boundary case involving zero total weight or an undefined conditional distribution.

### 4.3 What the witness does and does not settle

In this example the original inverted sampler still assigns \(\widehat\nu(b)=1/16\), and

\[
\|\nu_{\mathcal K}/\widehat\nu\|_\infty=16/9.
\]

Consequently the example does **not** refute the final density-ratio inequality, Lemma E.3/E.5, or the main learning theorem. It refutes a specific equality used to prove that inequality. The iterated argument in Lemma F.6, pp. 77–78, invokes the same proof strategy, so the downstream recursive upper bounds retain this unresolved dependency.

Fresh coins conditionally independent of \(\mathcal K\) would make a count representation of (1) valid. But the heavy-bin condition bounds the old acceptance count, not the fresh one. Substituting fresh coins alone does not restore the following estimates. No complete repair is claimed here.

For reproducibility, the source locations are `semiautomata_1_proofs.tex` immediately before `lemma:apxsample-specialcase`, `semiautomata_1_auxproofs.tex` at `eq:Lheavy`, `eq:calK`, `lemma:nu_calK`, and `density_ratio_k_proof.tex` at `lemma:nu_calK-new`.

## 5. The written top precision schedule loses the stated accuracy rate

Algorithm 2 on p. 14 specifies

\[
k_{H+1/2}=C\log(1/\varepsilon)\log\log(1/\varepsilon).
\]

Section C.3, p. 57, also writes the product, with coefficient \(c^{-1}\). This is not a text-extraction ambiguity. Equation (34), p. 49, and the proof of Lemma C.8, p. 53, require the top sample multiplier

\[
2k\exp(ck).
\]

Let \(u=\log(1/\varepsilon)\). With the displayed schedule, this multiplier is

\[
2Cu\log u\,\exp(cCu\log u)
=2Cu\log u\,\varepsilon^{-cC\log u}.
\]

For fixed admissible \(T\), this cannot be absorbed into \(\varepsilon^{-1}\) times the claimed logarithmic factors as \(\varepsilon\to0\). Bounding the product of branching factors alone does not bound the additional exponential in the sample recursion.

A local parameter repair is available **assuming the preceding lemmas**. The top error bound is \(3\sqrt{k}e^{-ck}\), so choose

\[
k=\left\lceil c^{-1}[u+\log(u+1)+A]\right\rceil
\]

for a sufficiently large constant \(A\) depending only on \(c\). Then

\[
3\sqrt{k}e^{-ck}\le\varepsilon,
\qquad 2ke^{ck}=O_c(\varepsilon^{-1}u^2).
\]

This is an independently proposed adjustment, not the original algorithm and not a repair of Section 4. An unspecified large multiplier on all of \(u+\log u\) would still change the main power of \(\varepsilon^{-1}\), so the leading coefficient matters.

There is also a lower-impact mismatch between \(2k\delta\) and \(4k\delta\) in the integer-level induction statements. The union-bound calculation in Lemma C.15 actually supports the sharper constant. That issue should not be promoted to a separate theorem refutation.

## 6. RLVR needs both forms of coverage and a trajectory-list optimizer

### 6.1 Coverage is uniform over constructed block inputs

The reference model is a supplied stochastic next-state map. Definition 2.11 requires, for every \(x\in S\times\Sigma^B\),

\[
\pi^{\mathrm{ref}}_{1:B}(\pi^\star_{1:B}(x)\mid x)
\ge1/C_{\mathrm{seq}}^{(B)},
\qquad
\pi^{\mathrm{ref}}_B(\pi^\star_B(x)\mid x)
\ge1/C_{\mathrm{ans}}^{(B)},
\]

with \(C_{\mathrm{ans}}^{(B)}\le C_{\mathrm{seq}}^{(B)}\). These are infima over all starts and words, not average coverage only on the original prompt distribution.

An exact verifier can check the terminal state of a constructed block. GuessAndCheck repeatedly rolls out the reference model until a terminal answer is verified, then uses that state to start the next block. This uses answer coverage. The base learning procedure must also include the entire correct trace among its candidates, which uses full-sequence coverage. Answer coverage alone does not imply the full theorem.

### 6.2 The claimed resource separation

Theorem 4.2 states the following bounds, suppressing the source's logarithmic factors:

\[
n_{\mathrm{sample}}=\widetilde O(d/\varepsilon),
\]

\[
n_{\mathrm{query}}
=\widetilde O(d/\varepsilon)
+\widetilde O((T/B)dC_{\mathrm{ans}}^{(B)}+dC_{\mathrm{seq}}^{(B)}),
\]

\[
n_{\mathrm{generated\ states}}
=\widetilde O(dT/\varepsilon)
+\widetilde O(dTC_{\mathrm{ans}}^{(B)}+dBC_{\mathrm{seq}}^{(B)}).
\]

The decomposition moves the expensive reference-model coverage factors into a burn-in term. It pays for short-block coverage instead of full-horizon coverage. It does not eliminate generation proportional to the horizon, and the term called computational cost counts generated states rather than every optimization operation. The same inverted-sampling proof dependency remains relevant to this upper-bound chain.

### 6.3 The optimizer is not the exact-label next-token oracle

Algorithm 5 retains verified, sufficiently probable candidate traces \(\widetilde D_i\) and returns

\[
\widehat\pi\in\arg\min_{\pi\in\mathcal F}
\frac1n\sum_i
\mathbf1\{\pi_{1:B}(x_i)\notin\widetilde D_i\}.
\]

This is sequence-list consistency ERM. A candidate list can contain traces with different internal states but the same correct endpoint. Expanding all candidates into next-state labels can create conflicts. Selecting an arbitrary trace from each list need not produce labels realizable by a common \(\pi\in\mathcal F\). The stated exact-label ERM interface therefore does not implement this step directly.

The cited dependency was checked in the version actually available before Part II: [Part I, arXiv:2603.18325v1](https://arxiv.org/abs/2603.18325v1), submitted March 18, 2026. Its source `arxiv_algorithms/Vlearn.tex` has the same list loss. The paragraph *Computation spent in running RLFineTune* in `appendix_RL_boosting.tex` explicitly counts a separate optimization call minimizing that loss. Thus the dependency preserves an additional oracle rather than supplying the missing reduction to ordinary next-token ERM.

This is an interface limitation, not a proof that such a reduction is impossible. The resource statements should be read conditional on solving the sequence-list problem. The source also assumes access to reference-trace probabilities for the filtering step. Part I remains **scoped reading**, not fully read. Its later August v2 was not used to retroactively fill the June dependency.

## 7. Independent consequence: a linear black-box sampling lower bound

This section is a new, short deduction from the source's Definition 5.1 and its Appendix F.6 construction. It is not attributed to the authors and makes no claim of priority across the literature.

The sampler has black-box iid access to \(\mu\), query access to a fixed \(w\), and must output one sample after at most \(N\) draws. The parameters specifying the unknown \(\mu\) are not an extra input. Fix even a known \(z\in\{1,\ldots,L\}\) and use the paper's family

\[
\mu_{p,z}
=p\,\delta_{z\mathbf1}
+\frac{1-p}{L}\sum_{i=0}^{L-1}\delta_{(L+1)e_i},
\qquad
w(x)=\mathbf1\{x\in\{1,\ldots,L+1\}\}.
\]

Every tuple has at least one weight-one coordinate, so the inverted sampler's tuple acceptance probability is one. The weighted marginal target is

\[
\nu_{p,z}(z)=\theta_L(p)
=\frac{Lp}{1+(L-1)p},
\qquad
\nu_{p,z}(L+1)=1-\theta_L(p).
\]

Take \(p_0=0\) and \(p_1=1/L\). The target laws differ by

\[
\operatorname{TV}(\nu_{p_0,z},\nu_{p_1,z})
=\frac{L}{2L-1}>\frac12.
\]

Couple the input samples so the two datasets are identical unless a rare \(z\mathbf1\) tuple is drawn under \(p_1\). With at most \(N\) samples, this occurs with probability

\[
1-(1-1/L)^N\le N/L.
\]

Internal randomness can be coupled, and all weight-query responses are identical across the two worlds. Data processing therefore bounds the total variation between the two output laws \(Q_0,Q_1\) by \(N/L\). If the algorithm is within \(\eta\) of its target in both worlds, the triangle inequality yields

\[
\frac{L}{2L-1}
\le 2\eta+\frac NL,
\qquad
N\ge L\left(\frac{L}{2L-1}-2\eta\right).
\tag{3}
\]

For every fixed \(\eta<1/4\), this proves \(N=\Omega(L)\). For example, target TV error at most \(1/8\) requires more than \(L/4\) samples. A random stopping rule bounded almost surely by \(N\) is included by padding its transcript with unused draws. This statement does not cover an unbounded stopping rule merely because its expectation is bounded.

If an open parameter range excludes \(p=0\), use the strictly interior pair \(p_0=L^{-2}\), \(p_1=L^{-1}\). Their input TV is at most \(1/L\), while their target TV is

\[
\frac{L}{2L-1}-\frac{L}{L^2+L-1}
\ge\frac12-\frac1L.
\]

The same argument gives \(N\ge(1/2-2\eta)L-1\), preserving the linear lower bound without an endpoint convention.

The source derives an \(\Omega(\sqrt L)\) obstruction by polynomial approximation and discusses a near-linear improvement as a prospective route. Equation (3) gives a direct linear obstruction for the stated fixed error range using its own family. It does **not** replace the source's exact worst-case TV threshold of \(1/2\) by the same threshold at \(N=\Theta(L)\). The constants and quantified accuracy must remain explicit.

There is a simple reason the generic polynomial argument is weaker here. A true \(N\)-sample algorithm has output probability

\[
f_N(p)=\sum_{k=0}^N a_k{N\choose k}p^k(1-p)^{N-k},
\qquad 0\le a_k\le1.
\]

The coefficients are conditional output probabilities given the number of rare tuples. Differentiating this Bernstein representation gives \(|f_N'(p)|\le N\). Treating the output only as a bounded degree-\(N\) polynomial discards those coefficient constraints and yields the weaker generic Markov derivative bound of order \(N^2\). This explanation concerns this model and construction, not all polynomial-method lower bounds.

This deduction is independent of the flawed conditional-distribution identity. It explains why preserving the original reweighted target can be expensive even when every input tuple contains an accepted coordinate. It does not prove that the proposed relaxed target is sampled with the claimed coverage.

## 8. Two useful auxiliary results, with their boundaries

**Online mistake bounds.** Theorem 6.4 uses a supplied next-state online learner with mistake bound \(M^\star\). When a predicted trajectory has a wrong endpoint, binary search locates a true erroneous transition with logarithmically many state queries. It maintains a correct left boundary and an incorrect right boundary. It does not require the entire error pattern to be monotone, because a wrongly predicted path can later rejoin the true path.

The online-to-batch argument takes a uniform mixture over snapshots and controls expected generalization error by \(M^\star/n\), with total query cost \(O(M^\star\log T)\). The proof averages over the training draw as well as the test draw. It does not by itself give a high-probability guarantee for every realized training dataset. The finite online-mistake assumption is stronger than ordinary finite-dimensional iid learnability.

**Stochastic composition.** Proposition 6.1 is a KL composition inequality. If the target and learned block transitions are stochastic, the chain rule and marginalization give

\[
\mathbb E_{x\sim\rho}
D_{\mathrm{KL}}(P_T(\cdot\mid x)\Vert Q_T(\cdot\mid x))
\le L\,\mathbb E_{X\sim\bar\mu}
D_{\mathrm{KL}}(P_\tau(\cdot\mid X)\Vert Q_\tau(\cdot\mid X)),
\]

where \(\bar\mu\) uses true target block-start states. This is a useful standalone error-propagation inequality. It is not a proved stochastic analogue of the full curriculum learner, and the paper leaves a weak-to-strong KL learning reduction open.

## 9. Relevance to Pro-E and limits of transfer

The reusable mathematical question is how a known compositional structure changes the supervision needed to learn long computations. This paper makes that question precise through a supplied semiautomaton and controlled queries at intermediate boundaries. It distinguishes the cost of learning short rules, composing them and allocating additional supervision adaptively.

The current upper-bound proof should not be imported as a certified lemma without resolving Section 4. The source also does not establish autonomous discovery of state semantics, a reusable program library, a decomposition grammar or an optimal abstraction. Training receives full-length prompts from the target distribution, so the guarantee is not extrapolation from a fixed shorter training support to every unseen length. The recursion constructs multiple learned models whose aggregate solves a specified target horizon.

The exact conditional-distribution witness, the accuracy-schedule calculation, the sequence-list optimization distinction and the black-box sampling lower bound can be used independently as methodological constraints. No source-to-FP theorem transfer, core definition change, architecture proposal or experimental protocol is made in this note.

## 10. Recovery and outstanding questions

This edition is fully read and archived. The large ordinary-paper claim can be closed. Part I v1 is a separate scoped dependency. The current proof gap requires an additional argument or an author correction, rather than a routine full theorem re-audit. The finite-sample lower bound above is fully proved within the stated black-box interface, but is not a novelty claim.

The next ordinary Pro-E candidate is Yang et al., *Length Generalization Bounds for Transformers*, ICML 2026 / arXiv:2603.02238v2. Its official full proceedings PDF and source are prepared, with no main-paper reading status inferred from source preparation. Selection remains subject to a fresh coordination/request check. Astra request `53c10ef` belongs to Pro-B and was not duplicated.
