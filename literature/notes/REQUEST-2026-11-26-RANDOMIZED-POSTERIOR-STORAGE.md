# Request 53c10ef: randomized posterior storage and its primary-source predecessors

Date: 2026-11-26. Researcher: Pro-B. Original request: [`53c10ef7b0b61746787f41ca47cb0948e0065665`](https://github.com/alan-ai1196/FP/commit/53c10ef7b0b61746787f41ca47cb0948e0065665). Claim: `69368628d9c7210763d100885f99823f32058f34`.

**Outcome: an exact published predecessor exists for the binary adjacent-point rounding kernel and its equalized inverse-component moments.** It is Luo–Senapati–Sharan, NeurIPS 2025, Algorithm 4 and Appendix D.3. Divergence coverings, including an actual chi-square covering construction, are also established. A recent preprint explicitly uses a hypothesis-independent reset and geometric occupation measures. In the bounded sources examined here, I did not locate the full fixed-codebook inverse-moment game identity, the exact binary minimax constant, or the complete recursive physical-state sequence-mixture theorem and deterministic finite-horizon converse. This is a search result, not a novelty determination.

This is a **completed scoped request**, not a collection of full-paper readings. Source statements, algebraic matching and search exclusions are distinguished below. No FP core file was edited. No theorem audit, exhaustive counterexample search, proof script or formal replay was performed.

## 1. The precise comparison target

The request points to [FOUNDATION](../../research/frontier/FOUNDATION.md#the-precision-of-a-randomized-learner-is-a-covering-problem-for-its-live-hypotheses) and the finite-horizon section of [INTELLIGENCE_OBJECTIVE](../../research/frontier/INTELLIGENCE_OBJECTIVE.md#a-finite-horizon-lower-bound-for-a-randomized-learners-entire-memory). At the requested revision, the objects are:

- A prescribed finite codebook \(Q\subset\operatorname{int}\Delta_{m-1}\). For a target posterior \(z\), choose a distribution over \(V\in Q\) to control every \(\mathbb E[(z_i/V_i)^t]\).
- The claimed global identity
  \[
  \frac1t\log\!\left[\sup_z\min_{\nu\in\Delta(Q)}\max_i\mathbb E_\nu(z_i/V_i)^t\right]
  =\sup_p\min_{v\in Q}D_{1+t}(p\Vert v).
  \]
- At \(m=2,t=1\), an optimal \(H\)-point interior grid \(v_j=\sin^2(j\pi/[2(H+1)])\) and factor \(\Gamma_1=\sec^2(\pi/[2(H+1)])\).
- A causal gate that updates from its **currently stored rounded weights**, then draws fresh rounding randomness after the observation. Its reported sequence likelihood competes with the exact fixed-prior mixture of supplied causal experts, with an \(O(N/H^2)\) term. Expert-internal states are charged separately. The adaptive high-probability statement depends on the specified coin and observation order.
- A converse for every homogeneous randomized learner with at most \(H\) physical states, including its clock and retained seed. For supplied iid experts with means \(1/2\pm1/(8H)\), the stated equal-prior expected cumulative log-loss excess is at least \(N/(640H^2)-\log2\) for every \(N\ge2\), even when the machine is designed for that horizon.

These statements are recorded to identify the requested object. This note does not certify their proofs. In particular, a finite report alphabet, a finite family of comparator models, and a finite persistent state space are different resources.

## 2. Exact local predecessor: Luo–Senapati–Sharan, NeurIPS 2025

Haipeng Luo, Spandan Senapati and Vatsal Sharan, *Simultaneous Swap Regret Minimization via KL-Calibration*. [Proceedings record](https://proceedings.neurips.cc/paper_files/paper/2025/hash/5b38c271298813fa5c241a12f552ef5b-Abstract-Conference.html), [33-page final PDF](https://proceedings.neurips.cc/paper_files/paper/2025/file/5b38c271298813fa5c241a12f552ef5b-Paper-Conference.pdf), DOI [10.52202/085713-2116](https://doi.org/10.52202/085713-2116). Related arXiv `2502.16387` began on 2025-02-23 and has v2 dated 2025-11-15. The comparison uses the proceedings final, without claiming complete equivalence of editions.

### The same rounding probabilities and the same inverse moments

For adjacent interior grid points \(a<p<b\), let \(f(x)=x(1-x)\). Algorithm 4, p10, assigns unnormalized probabilities
\[
\Pr(V=a)\propto\frac{b-p}{f(b)},\qquad
\Pr(V=b)\propto\frac{p-a}{f(a)}.
\]
Multiplying numerator and denominator by \(f(a)f(b)\) gives
\[
\Pr(V=b)=\frac{(p-a)f(b)}{(b-p)f(a)+(p-a)f(b)},
\]
which is exactly the adjacent \(t=1\) law in the requested FP section after renaming variables. This equality is a direct algebraic match, not a resemblance of rates.

Appendix D.3, pp20–21, explicitly computes
\[
\mathbb E\frac pV=\mathbb E\frac{1-p}{1-V}
=\frac{p(1-p)}{p+ab-p(a+b)}
=1+\frac{(b-p)(p-a)}{p+ab-p(a+b)}.
\]
The denominator equals \(f(p)-(p-a)(b-p)\), exactly the chord denominator in the request. Lemma 5, p9, uses these expressions to bound the expected log-loss increase for either binary outcome by \(O(K^{-2})\). Thus both the kernel and its inverse-moment equalization need attribution to this paper.

The exact match is for an input bracketed by grid points. The printed Algorithm 4 takes \(p\in[0,1]\), but its displayed rule asks for such a bracket although the grid is strictly interior. The selected method/proof passages and targeted whole-text searches did not reveal a separate outside-grid rule. This note therefore does not treat the printed pseudocode as a complete all-posterior endpoint construction. Appendix D.3 also writes an equality immediately after an upper-bound step in Eq. (8). The inverse-moment calculations themselves are the relevant exact precedent, and the intended log-loss conclusion is an inequality. No broader correctness audit was attempted.

### Its grid, algorithm and comparator

Section 5, pp7–10, uses
\[
z_0=\sin^2\frac\pi{4K},\quad
z_i=\sin^2\frac{\pi i}{2K}\ (1\le i<K),\quad
z_K=\cos^2\frac\pi{4K}.
\]
This is a boundary-adjusted grid of \(K+1\) possible forecasts. It differs from the request's equally spaced \(H\) interior angular levels and does not state the exact \(\sec^2\) minimax factor.

Algorithms 1–3, pp8–9, maintain \(K+1\) EWOO instances, form a matrix of their forecast distributions, compute a stationary distribution and draw a forecast. Appendix D.1, pp19–20, retains real cumulative counters
\(\gamma_i=\sum_{\tau<t}y_\tau p_{\tau,i}\) and \(\delta_i=\sum_{\tau<t}(1-y_\tau)p_{\tau,i}\). The EWOO output simplifies to \((\gamma_i+1)/(\gamma_i+\delta_i+2)\). The finite forecast alphabet consequently does not establish \(K+1\) total physical learner states, and rounding does not overwrite these counters with one sampled posterior codeword.

Theorem 2, p9, bounds pseudo KL-calibration, equivalently log-loss pseudo swap regret, by \(O(K\log T+T/K^2)\), optimized at \(K=(T/\log T)^{1/3}\). This comparator differs from the likelihood of a fixed-prior mixture of supplied causal experts. The simultaneous-action protocol in §2 does not let the adversary see the current sampled report before choosing its outcome. Section 6, p10, leaves an explicit high-probability algorithm for log-loss swap regret as future work. Neither that limitation nor the paper's positive bounded-smooth-loss guarantees settle the request's different adaptive sequence-mixture statement.

## 3. Covering theory: a stronger established predecessor than expected companding alone

### Explicit Rényi covering and KL cardinality rates

Jennifer Tang, *Bounding the Capacity of the Multinomial Channel using KL Divergence Covering and Packing*, ISIT 2025, [author PDF](https://web.mit.edu/jstang/www/papers/multinomial_isit2025.pdf). Definition 1, p3, explicitly permits an f-divergence **or Rényi divergence** and defines the radius through
\(\max_p\min_{q\in Q}D(p\Vert q)\). The right side of the requested game identity is therefore already a named covering object with the same quantifier order.

Theorem 3, p4, quotes the KL covering bound
\[
M_{\rm KL}(m,R)\le 7^{m-1}\left(\frac{m-1}{R}\right)^{(m-1)/2},\qquad0<R\le1,
\]
and gives the binary refinement \(M_{\rm KL}(2,R)\le6/\sqrt R+1\). The channel-capacity argument uses a finite mixture of product laws and a cost \(\log|Q|+nR\). It does not construct a recursively rounded finite-state posterior. A Rényi redundancy–capacity theorem optimizing one unrestricted center is also not automatically an identity for a prescribed multi-point codebook.

### An actual chi-square cover, and its order-two implication

Tang's MIT PhD thesis, *Divergence Covering*, February 2022, [primary PDF](https://people.lids.mit.edu/yp/homepage/data/theses/2022_PHD_Tang.pdf), Definition 9 at printed p31 and §2.7.4 at pp38–39, is closer to the request's \(t=1\) case. Its ellipsoids are chi-square divergence balls. Theorem 3 gives, for \(\varepsilon\le1/[4(m+1)^2]\),
\[
M(m,\varepsilon)\le c_0m^{3/2}
\left(\frac{c_1}{\varepsilon}\right)^{(m-1)/2}
\log\frac1\varepsilon,
\qquad c_0\le10,\ c_1\le4.
\]
Although the theorem is stated as a KL-covering bound, its proof constructs a chi-square cover, using modified Jeffreys random centers, a finite net and radius enlargement. The immediate identity \(D_2(p\Vert q)=\log(1+\chi^2(p\Vert q))\) supplies a corresponding order-two cover. This last conversion is our algebraic implication. It is not a separately stated theorem in the thesis. Preserve the small-radius condition and extra logarithmic factor. This source does not by itself establish the request's exact all-codebook game equality, a logarithm-free sharp order-two cardinality law or the binary minimax constant.

### Existing Adler–Tang–Polyanskiy entry: extend its scope accurately

*Efficient Representation of Large-Alphabet Probability Distributions*, [arXiv2205.03752v3](https://arxiv.org/abs/2205.03752v3), [exact PDF](https://arxiv.org/pdf/2205.03752v3), related JSAIT DOI [10.1109/JSAIT.2023.3234502](https://doi.org/10.1109/JSAIT.2023.3234502). Astra's existing row accurately recorded opening-only intake. The new scoped reading adds **Theorem 4, p5, a pointwise divergence-covering guarantee**, beyond the prior-averaged companding results:
\[
\max_xD_{\rm KL}(x\Vert z(x))
\le(1+\operatorname{err}(m))N^{-2}\log^2m,
\]
for \(m>4\) and \(N\ge8\log(2\sqrt{m\log m}+1)\), with \(\operatorname{err}(m)\le18\log\log m/\log m\le7\). It uses midpoint decoding followed by normalization. Here \(N\) is the number of bins **per coordinate**, costing \(m\lceil\log_2N\rceil\) bits, rather than the total codebook cardinality. The theorem is nonasymptotic and pointwise. Do not describe the paper as only expected-loss companding. No complete arXiv/journal edition equivalence was established.

## 4. Sine-squared grids have explicit historical sources

These were targeted dependency lookups, not a historical full-reading queue.

| Primary source and exact location | What is established | Difference from the requested result |
|---|---|---|
| Baron–Bresler–Mıhçak, CISS2003, *Two-Part Codes with Low Worst-Case Redundancies for Distributed Compression of Bernoulli Sequences*, [author PDF](https://barondror.com/pdf/ciss2003.pdf), §III-C, §IV-A Eq. (9), §V Eqs. (10)–(11) | Jeffreys coordinate \((2/\pi)\arcsin\sqrt\theta\), bin edges \(\sin^2(\pi k/(2K))\), and half-step reconstruction points \(\sin^2(\pi(2k-1)/(4K))\) | Deterministic worst-case KL two-part coding. The half-step grid and its optimality equations differ from the order-two \(j/(H+1)\) optimum. |
| de Rooij–van Erven, AISTATS2009, *Learning the Switching Rate by Discretising Bernoulli Sources Online*, [record](https://proceedings.mlr.press/v5/rooij09a.html), [PDF](https://proceedings.mlr.press/v5/rooij09a/rooij09a.pdf), p436 Definition 1, Lemma 4 and Theorem 2 | Angular discretization with half-spacing boundary points. Nearest-point KL is at most \((8-4\sqrt2)\delta_k^2\). A Bernoulli-source mixture attains sequence regret \(\tfrac12\ln T+2.8\). | The method maintains a forward mixture and refines/selects a parameter grid. It does not store all posterior information in one sampled codeword. |
| Kotłowski–Koolen–Malek, COLT2016, *Online Isotonic Regression*, [record](https://proceedings.mlr.press/v49/kotlowski16.html), [PDF](https://proceedings.mlr.press/v49/kotlowski16.pdf), §7.1, PDF pp12–13, Theorem 8 | The boundary-adjusted grid later used by Luo et al. and a \((2-\sqrt2)\pi^2T/K^2\) KL discretization term | Exponential weights over a finite net of isotonic functions. The net discretizes comparators, not the machine's retained posterior state. |

Thus neither angular companding nor a \(T/K^2\) discretization contribution should be presented as newly introduced here. No inspected source supplied the exact \(H\)-level order-two optimum and its constant.

## 5. Recursive finite-state prediction and expert-memory neighbors

### Meron–Feder 2004 includes genuinely randomized finite-state prediction

The earlier [request0940e87 note](REQUEST-2026-11-24-FINITE-MEMORY-LOG-LOSS.md) inspected the deterministic results. This request extends that coverage to §V.D and the conclusion, printed pp1517–1520, of *Finite-Memory Universal Prediction of Individual Sequences*, [author journal PDF](https://www.eng.tau.ac.il/~meir/articles/48%20Finite%20Memory%20Universal%20Prediction%20of%20Individual%20Sequences.pdf), DOI [10.1109/TIT.2004.830749](https://doi.org/10.1109/TIT.2004.830749).

Their imaginary sliding window has \(K+1\) physical states. On bit 1 it moves from \(i\) to \(i+1\) with probability \(1-i/K\). Its coding forecast is \((i+1/2)/(K+1)\). Equations (2)–(3), p1508, compare expected average loss on a worst individual sequence to its empirical best constant, then take a fixed-state-count asymptotic limit. The abstract reports randomized log-loss upper \(O(\log K/K)\) and lower \(\Omega(1/K)\). On p1519, however, the log-loss calculation is explicitly qualified as approximate because it reuses moments derived before boundary correction. The formal Theorem 7 on that page treats square loss. Preserve this difference in evidence strength.

Page 1520 explicitly lists prediction against \(M\) experts with a restricted \(K\)-state predictor as a further problem. That does not establish absence of later solutions. It does show that this particular finite-state predecessor is not the requested fixed-prior supplied-expert sequence-mixture result.

### Memory-regret bounds for expert selection are not the same model

Peng–Rubinstein, *Near Optimal Memory-Regret Tradeoff for Online Learning*, [arXiv2303.01673v2](https://arxiv.org/abs/2303.01673v2), related FOCS2023 publication, was checked only at its opening results and Definition 3.1/MWU preliminaries. It selects an expert, has losses in \([0,1]^n\), compares to the best expert and counts memory words. This is not ordinary mixture-forecast log loss against a fixed-prior sequence mixture. Real registers, horizon counters and words also do not directly give a clock-inclusive number of physical states. Its bounds are not an equivalent converse for the request.

## 6. Finite-horizon converse: the classical quantifier issue and a recent method predecessor

### Classical testing does not permit an automatic finite-horizon substitution

Hellman–Cover1970, *Learning with Finite Memory*, [author scan](https://ee.stanford.edu/~hellman/publications/04.pdf), DOI [10.1214/aoms/1177696958](https://doi.org/10.1214/aoms/1177696958), Theorem 3 and Eq. (33), bounds the long-run average classification error of homogeneous randomized machines. Under symmetric Bernoulli hypotheses with \(p>1/2\) and equal priors, its infimum is \([1+(p/(1-p))^{H-1}]^{-1}\). For nondegenerate symmetric Bernoulli experiments and more than two states, the bound generally need not be attained by a machine. The existing scoped note already records the theorem and its long-run scope. Flower–Hellman **1972**, [author scan](https://ee.stanford.edu/~hellman/publications/10.pdf), DOI [10.1109/TIT.1972.1054820](https://doi.org/10.1109/TIT.1972.1054820), studies finite **terminal** error, principally numerical searches and selected machine asymptotics. Neither result alone is the requested finite cumulative log-loss theorem.

A material new passage is Cover–Freedman–Hellman1976, *Optimal finite memory learning algorithms for the finite sample problem*, [author scan](https://isl.stanford.edu/~cover/papers/paper39.pdf), DOI [10.1016/S0019-9958(76)90456-3](https://doi.org/10.1016/S0019-9958(76)90456-3). Section 3, printed pp56–59, distinguishes terminal error \(\mathbb E e_N\), average cumulative error \(\mathbb E[N^{-1}\sum_{n\le N}e_n]\), and a tail-supremum objective in Eqs. (12)–(14). It explicitly chooses the terminal definition for the subsequent analysis.

Printed p58 gives an asymmetric two-Bernoulli, two-state absorbing-machine example. A transition probability chosen as a function of \(N\) keeps optimized terminal error below the best long-run error, although every fixed such machine's terminal error eventually tends to \(1/2\). This is a primary-source reason not to exchange a fixed-machine long-run theorem with optimization over machines separately designed for each horizon. The example concerns asymmetric testing and does not refute the request's symmetric cumulative theorem. A finite occupancy and truncation argument remains a separate step.

### Petkov 2026 already uses reset kernels and geometric occupations

Samuil Petkov, *State complexity of rare-switching tracking: universal bounds and sharp counter tradeoffs*, [Hexagon2611.00656v1](https://hexagonmath.org/2611.00656v1), [primary PDF](https://hexagonmath.org/pdf/2611.00656v1). Deposited 2026-11-19, PDF dated 2026-11-01. This is an **author-responsible, non-peer-reviewed preprint**, with disclosed GPT/Claude assistance. It is not an official OpenAI or Anthropic paper. The following are source statements, not independently verified results.

Appendix A.1, p17, Proposition 27, constructs the hypothesis-independent reset kernel
\(K'=2r\mu+(1-2r)K\) and applies Hellman–Cover to obtain a stationary switching-error bound
\(r+(1-2r)e\ge[1+R^{H-1}]^{-1}\), where \(R=(1-\eta)/\eta\) for binary observation error \(\eta\). It explicitly handles reducible original kernels and stationary mixtures. Appendix A.2, pp17–18, uses
\[
f_h=h\sum_{n\ge0}(1-h)^n\nu_0P_K^n
\]
and states convergence of optimized geometric-terminal error to stationary optimum for **fixed** switching rate, observation noise and state count. This is a close methodological predecessor for a reset/occupation bridge.

The same appendix disclaims a rate uniform over tiny transition probabilities or growing state counts. Section 11 disclaims uniformity as the observation channel becomes uninformative. It does not give the deterministic finite-\(N\) cumulative log-loss bound for bias offset \(a=1/(8H)\). The source supports attribution of the method family, not an automatic transfer of its limit theorem.

### A current finite-horizon result with a different clock and loss

Wu–Wang–Deng, *The Cost of Working Memory in Streaming Mean Estimation*, [arXiv2610.39540v1](https://arxiv.org/abs/2610.39540v1), [PDF](https://arxiv.org/pdf/2610.39540v1), dated 2026-10-29. Its model has Gaussian observations over a whole mean ball, \(K\) persistent states, a known horizon and a **free public time index**. Theorem 3.2 states terminal squared-risk rate
\[
\min\left\{1,\ K^{-2/d}+\frac dn\left(1+\frac{\log(ed)}{1+(\log K)/d}\right)\right\}.
\]
The scalar rate includes \(n^{-1}+K^{-2}\), but this is not an equivalent \(N/H^2\) cumulative log-loss theorem. Model and theorem statements were scoped, not independently verified. A terminal Gaussian-testing lemma in Appendix C.3 was also screened by the source assistant and is not used to justify any FP conclusion here.

## 7. Reading coverage, evidence strength and search limit

| Edition | Actual new reading for this request |
|---|---|
| Luo et al., NeurIPS2025 final, 33 pages | Main reader read abstract/introduction intake, §5 pp7–10 and Appendix D.1–D.3 pp19–21. Source assistant additionally read §2, grid-proof portions pp18–19 and relevant references. |
| Tang, ISIT2025 author manuscript, 6 pages | Main reader checked title/abstract, Definition 1, Theorem 3 and the capacity-covering argument on pp3–4. Remaining main results were scoped by the source assistant. |
| Tang, MIT2022 thesis | Source assistant read Chapter 2 definitions and theorem statements, Definition 9 and §2.7.4 proof. Main reader checked §2.7.4 pp38–39. Supporting lemmas were not all read. |
| Adler et al., arXiv2205.03752v3, 35 pages | Main reader checked Theorem 4 and its surrounding TeX discussion. Source assistant additionally checked opening definitions and Theorems 1–2. Earlier Astra opening-only record is retained and extended. |
| Baron et al. CISS2003 | Source assistant scoped §§III-C, IV-A–C and §V optimality equations. Longer referenced proof was not read. |
| de Rooij–van Erven AISTATS2009 | Source assistant scoped abstract/introduction and §3.1–3.3, especially printed p436. |
| Kotłowski et al. COLT2016 | Source assistant scoped §7.1, PDF pp12–13. |
| Meron–Feder2004 | Existing deterministic scope retained. New source-assistant scope covers abstract, definitions and §V.D/conclusion pp1517–1520. Main reader visually checked pp1518–1520, including the approximation qualification. |
| Peng–Rubinstein arXiv2303.01673v2, 52 pages | Source assistant read abstract/introduction/Theorems 1.1–1.3, Definition 3.1 and MWU preliminaries, PDF pp1–3 and12–13. No complete-paper or final-edition equivalence claim. |
| Hellman–Cover1970 and Flower–Hellman1972 | Existing primary-source comparison reused. Source assistant rechecked the stated model, objective and selected result passages. No full-read promotion. |
| Cover–Freedman–Hellman1976, 37 pages | Source assistant read pp49–60 and81–85. Main reader personally checked original pp57–58, the distinct loss definitions and horizon-designed counterexample. Middle technical sections remain unread. |
| Petkov Hexagon2611.00656v1, 18 pages | Main reader checked original web PDF §11 and Appendix A, plus record/provenance. Source assistant additionally scoped introduction and §9 occupation identities. Local PDF download returned403, so the primary web extraction is the actual read source. |
| Wu et al. arXiv2610.39540v1 | Main reader checked title/abstract and opening model. Source assistant read §§1–2, §3 Theorems 3.1–3.2 statements, §6 result statements and Lemma C.3 statement. No technical-proof certification. |

The search started with current 2025–2026 work on finite-precision expert weights, randomized posterior quantization, finite-memory log loss and finite-horizon inference. Targeted citation checks then resolved the exact rounding kernel, angular grids, simplex coverings and classical testing quantifiers. Both search engines and primary venue/author sources were used. The already completed global discovery scan and other researchers' current papers were not repeated.

**Found:** the exact bracketed binary rounding law and inverse-moment equalizer, explicit Rényi covering definitions, KL and chi-square covering constructions, angular grid antecedents, randomized physical-state prediction under another comparator, and a reset/Abel method predecessor.

**Not located within the inspected scope:** the complete all-finite-codebook inverse-moment minimax identity, its exact binary \(\sec^2\) optimum, the whole recursive fixed-prior causal-expert mixture guarantee with the stated physical memory and coin ordering, or an equivalent all-horizon cumulative converse. The bounded search does not rule out an unexamined theorem, other terminology or later editions. It provides no novelty certificate and no automatic source-to-FP theorem transfer.
