# Finite-memory prediction of two known symmetric coins: scoped prior-art reply

**Request:** local Astra commit 0940e87, November 24, 2026 Shanghai. **Status: completed as a bounded primary-source check.** No verified earlier theorem with all the requested quantifiers was located. This is not evidence of novelty, and it does not certify the local proof. The closest sources below establish different objectives or limiting regimes.

## Exact claim checked

Fix \(p\in(1/2,1)\). Draw one fair hidden orientation \(Z\), then generate all \(T\) observations iid conditional on that orientation, with bias \(p\) or \(1-p\). A predictor starts in a fixed state independent of \(Z\), uses a deterministic time-homogeneous transition and probability readout, and may be designed separately for each horizon \(T\). All information persisting between observations, including a clock if stored, counts in its \(S\) states.

The target is a fixed positive budget \(b\) for total expected excess causal log loss relative to the full Bayesian mixture:

\[
D_T=\mathbb E_P\sum_{t=1}^T
\log\frac{P(Y_t\mid Y_{<t})}{q_{M_{t-1}}(Y_t)}
=D_{\rm KL}(P_{1:T}\Vert Q_{1:T})\le b.
\]

The requested order is \(S(T)=\Theta_{p,b}(\log T)\), hence \(\log_2\log T+O_{p,b}(1)\) bits for the state index. Fixed program description and numerical readout precision are separate resources. Unknown prototype acquisition, zero-budget exact prediction, free-clock machines and randomized transition rules are outside this particular claim.

## What the primary sources actually establish

| Source and exact location inspected | Objective and scope | Relation to the request |
|---|---|---|
| **Hellman–Cover (1970), Learning with Finite Memory**, *Annals of Mathematical Statistics* 41(3):765–782, [DOI](https://doi.org/10.1214/aoms/1177696958), [author PDF](https://ee.stanford.edu/~hellman/publications/04.pdf). Printed p.766 eq.(3), p.772 Theorem 3/eqs.(32)–(33). | Expected long-run fraction of classification errors, with fixed \(m\), time-invariant machines and permitted randomized transitions. For fair symmetric coins the lower bound reduces to \(1/[1+(p/(1-p))^{m-1}]\). | Supplies a classical exponential state/error relation. It is a long-run classification statement, not a finite-\(T\) cumulative log-loss bound uniform over machines designed for \(T\). |
| **Flower–Hellman (1972), Hypothesis Testing With Finite Memory in Finite Time**, *IEEE TIT* 18(3):429–431, [DOI](https://doi.org/10.1109/TIT.1972.1054820), [author PDF](https://ee.stanford.edu/~hellman/publications/10.pdf). Printed pp.429–430. | Same symmetric coins and fair prior, but minimizes terminal classification error \(P_N\). Allows randomized homogeneous transitions. The reported numerical search covers up to seven states and \(2^{22}\) observations. | Very close source model and finite horizon; different scored output. Its restricted-machine asymptotics are not an all-machine cumulative Bayes-log-loss theorem. |
| **Cover–Freedman–Hellman (1976), Optimal finite memory learning algorithms for the finite sample problem**, *Information and Control* 30(1):49–85, [DOI](https://doi.org/10.1016/S0019-9958(76)90456-3), [author PDF](https://isl.stanford.edu/~cover/papers/paper39.pdf). Printed p.50 eqs.(2)–(5). | Explicitly defines finite-\(N\) optimal terminal error separately for randomized and deterministic homogeneous machines, and separately defines infinite-time optima. | Confirms that horizon-dependent optimization and an infinite-time optimum are distinct formulations. Only this setup was checked here; no claim about all later theorems in the 37-page paper. |
| **Meron–Feder (2004), Finite-Memory Universal Prediction of Individual Sequences**, *IEEE TIT* 50(7):1506–1523, [DOI](https://doi.org/10.1109/TIT.2004.830749), [author PDF](https://www.eng.tau.ac.il/~meir/articles/48%20Finite%20Memory%20Universal%20Prediction%20of%20Individual%20Sequences.pdf). Printed p.1508 eqs.(2)–(3), p.1514 Theorem 5, pp.1516–1517 Theorem 6 and consequence. | Deterministic homogeneous \(K\)-state probability forecasts are included. Log-loss results compare worst individual sequences with the empirical best constant predictor: asymptotic redundancy per symbol \(O(K^{-2/3})\) for the EDM construction and lower order \(\Omega(K^{-4/5})\). | Correct machine vocabulary and loss, but different source/comparator and a fixed-\(K\), infinite-sequence average. Substituting \(K=K(T)\) requires finite-horizon control absent from the statements inspected. |
| **Managoli–Prabhakaran (2026), Memory Constrained Adversarial Hypothesis Testing**, [arXiv:2605.12063v2](https://arxiv.org/abs/2605.12063v2), revised November 12; 22 pages. Physical p.3 eqs.(3)–(4), p.14 Theorems 4–7. | Asymptotic average 0–1 minimax error, then an error exponent as state count grows. Main class permits random transitions; §VII extends deterministic Bernoulli testing exponents to adversarial parameter intervals. | Recent original testing result. Neither the definition nor the inspected deterministic theorems supplies the requested finite-\(T\) accumulated probability-forecast loss. |
| **Sagan–Weissman, A Family of LZ78-based Universal Sequential Probability Assignments**, [arXiv:2410.06589v2](https://arxiv.org/abs/2410.06589v2), December 12, 2025 accepted manuscript; 40 pages. *IEEE TIT* 72(4):2557–2583 (2026), [DOI](https://doi.org/10.1109/TIT.2025.3645223). Physical pp.8–10, Definitions IV.1–IV.2, Theorems IV.11/V.1 and Remark V.2. | Defines homogeneous deterministic finite-state SPAs, but studies normalized individual-sequence log loss, with sequence length tending to infinity before state count. Universal LZ78 assignments are compared with that class. | No fixed-total Bayes-regret state count is stated. The finite-state comparator does not make the universal LZ78 algorithm itself an \(M\)-state predictor. The remark explicitly limits universality to the asymptotic regime. |
| **Feng–Meng (2026), Recursive memory for prediction and generation**, [arXiv:2611.13760v1](https://arxiv.org/abs/2611.13760v1), November 10; 62 pages, full PDF and TeX retrieved from arXiv. §§2, 3.1–3.2, 4.1–4.5 and selected proofs. | A general finite-history quantization lower bound for deterministic-state issued laws; polynomial state growth, equivalently \(\Theta(\log(T/b))\) **bits**, for nondegenerate strictly positive two-state HMMs. Explicitly separates private hidden-state generation. | Closest recent conceptual match. Its sharp-order HMM result excludes the persistent coin's transition matrix \(I\), and its generic converse does not itself yield the requested logarithmic **state** count. Details follow. |

All entries above are **scoped readings**, not newly completed full papers. Publisher versions and author-manuscript versions retain their own identity. No numerical experiments or ancillary verification programs were run for this request.

## Why the nearest results do not settle this exact claim

### Fixed-machine limits do not supply uniform finite-time control

Hellman–Cover define an expected asymptotic fraction of mistakes before minimizing over a fixed-size machine class. Flower–Hellman explicitly discuss how reducing endpoint escape probabilities improves the infinite-time error but lengthens the machine's time constant. Their finite-time numerical optimization therefore changes the transition parameters with \(N\).

Meron–Feder similarly define \(R(U_K)=\limsup_{n\to\infty}R_n(U_K)\), with \(R_n\) normalized by \(n\). A bound on this limit at each fixed \(K\) cannot simply be multiplied by a horizon \(T\) while choosing \(K=K(T)\). Neither transient terms nor uniformity in the changing machine are thereby controlled. Moreover, their individual-sequence comparator is chosen for the observed sequence; the requested Bayes comparator integrates a specified two-point prior.

These distinctions do not rule out deriving the desired theorem from older tools. They mean that the inspected published statements are not already that theorem. The local stopped-counter construction is closely related to classical finite-memory testing mechanisms; the bounded search establishes no new-mechanism claim.

### The recent HMM theorem is about a different source family

Feng–Meng Theorem 4.2 gives, for any finite-alphabet source and a deterministic-state machine with at most \(K_j\) states at time \(j\),

\[
D_{\rm KL}(P_{1:T}\Vert Q_{1:T})
\ge 2\sum_{j=0}^{T-1}\mathcal D_{K_j}(\mu_j),
\]

where \(\mu_j\) is the distribution of the source's next-symbol predictor and \(\mathcal D_K\) is squared total-variation quantization distortion. The finite-history statement allows free clocks and varying codebooks. Its proof uses the KL chain rule and Pinsker's inequality, and was read directly. A separate stationary limit uses a guarantee at every forecast start; Proposition A.5 provides an additive-initialization version for one initial forecast in the positive-HMM setting.

The sharp two-state classification, Theorem 4.1, assumes transition parameters \(\alpha,\gamma\in(0,1)\) in

\[
P=\begin{pmatrix}1-\alpha&\alpha\\1-\gamma&\gamma\end{pmatrix},
\]

distinct transition rows, distinct emissions and positive emission probabilities. At \(x=T/b\), it gives
\(c x^{d_*/2}\le K_{\rm KL}\le C(1+\sqrt{x})\). The logarithm of this count is \(\Theta(\log x)\).

The persistent two-coin model has \(\alpha=0,\gamma=1\), outside those assumptions. The filter-contraction constants used in the upper bound also cease to have the required uniform positive-transition bounds. One cannot take a zero-switching limit without new analysis.

There is a second concrete obstruction to using the stationary converse as the missing result. For a fixed latent coin, the infinite past identifies its orientation almost surely. Hence the stationary next-bit predictor law is the two-atom measure
\(\frac12\delta_p+\frac12\delta_{1-p}\), whose \(\mathcal D_K\) is zero for \(K\ge2\). This is a direct scope deduction from the model, not a counterexample to the paper. Its general finite-history bound remains valid; the positive-HMM stationary nonconcentration argument does not establish the coin's recursive state lower bound.

### Hidden-state generation is not the issued-forecast experiment

A generator can draw a private fair bit once and then emit the corresponding known coin. Its **marginal generated transcript law** is exactly the desired mixture, with two private regime labels after initialization. That fact does not produce a deterministic causal probability predictor with two observable states.

For a concrete distinction, draw that private orientation independently of the real source and issue its coin probability on every real observation. With \(d_*=D(\operatorname{Ber}(p)\Vert\operatorname{Ber}(1-p))\), its expected total loss is
\(T h(p)+(T/2)d_*\). Full Bayes has expected loss \(T h(p)+I(Z;Y_{1:T})\), where \(I\le\log2\). Thus the issued-forecast excess is \((T/2)d_*-I(Z;Y_{1:T})\), despite exact agreement of the generator's marginal transcript distribution. This elementary identity only illustrates the distinction; it is not a lower bound for every randomized predictor.

Feng–Meng's §§2 and 4.5, and the private-initialization proofs, make the same modeling separation explicit: hidden labels may remain random conditional on the visible outputs. Marginalizing those labels for likelihood evaluation is different from charging the log loss of the actual component probability that was issued.

## Search boundary and reading provenance

The check ran on **November 24, 2026 Shanghai / November 23 UTC**, against the exact 0940e87 request. The recent-source assistant used twelve topic/title queries plus one publication-DOI lookup, emphasizing 2024–2026 finite-state prediction, Bernoulli memory complexity, cumulative log loss, finite-memory inference and sequential probability assignments. The main assistant added general/exact-title queries across both search engines, retrieved the official Feng–Meng PDF/TeX, and read the source passages reported above. Historical searches were restricted to the named comparisons and their nearest necessary neighbors.

The main assistant personally inspected Flower pp.429–430; Hellman–Cover definitions on p.766, surrounding material on pp.767–768/770 and Theorem 3 on p.772; Cover–Freedman–Hellman p.50; Meron–Feder definitions and Theorems 5–6 on pp.1508/1514/1516–1517; Managoli–Prabhakaran physical pp.1/3/14; and Sagan–Weissman pp.8–10. Formula layouts were checked in the original PDFs where extraction dropped symbols.

Feng–Meng coverage is main TeX lines 1–365 and 410–783; Theorem 4.2's proof at 1264–1349; and the initial-forecast/private-state material at 1507–1645. PDF pp.10–11 were visually checked. Sections and figures outside those ranges, the nonconcentration proof, window results, full bibliography and ancillary programs remain unread. It is a promising recent source for subsequent full reading, not a completed paper.

**Remaining source limit:** Rajwan–Feder (2000), *Universal Finite Memory Machines for Coding Binary Sequences*, DCC pp.113–122, [DOI](https://doi.org/10.1109/DCC.2000.838151), was verified through the [authors' university record](https://cris.tau.ac.il/en/publications/universal-finite-memory-machines-for-coding-binary-sequences/). Its abstract covers stochastic/individual-sequence log loss and several machine classes, but the bounded retrieval did not recover a legal complete PDF; exact original theorems remain unchecked.

A mirror-only rare-switching candidate was rejected because its claimed title did not match its arXiv identifier's official record. Abstract-only neighboring work on unknown-HMM sample complexity, general logistic regret and the 2024 limited-memory survey was not treated as an exact result. This is a deliberately bounded search, not exhaustive citation closure. No core FP theorem, experiment or claim of novelty was changed.
