# Recursive memory for prediction and generation

## Source, edition and reading coverage

Pengbin Feng (University of Southern California) and Chunlei Meng (Fudan University), **arXiv:2611.13760v1**, submitted November 10, 2026 at 09:00:36 UTC, **62 pages**. [Versioned abstract](https://arxiv.org/abs/2611.13760v1) · [PDF](https://arxiv.org/pdf/2611.13760v1) · [Complete source archive](https://arxiv.org/src/2611.13760v1). This is an arXiv preprint; no peer-reviewed publication was established. Reading completed November 24, 2026 Shanghai.

**Full reading by the main assistant:** complete TeX `paper.tex`, lines 1–3818, §§1–7, all proofs in Appendices A–E, displayed formulas, all five figures and five tables, author information, and all 49 bibliography entries. The manuscript has no numbered footnotes. The actual figures/tables were inspected on PDF pp. 6, 14–15, 18, 46, 54 and 56; formula layouts were also checked on pp. 10–11, 32–33, 52–53 and 58. This completes the disjoint ranges previously read for Astra's 0940e87 request without counting that scoped intake as a separate full paper.

The primary PDF, complete 32-file source archive, eight ancillary Python programs and eight supplied verification JSON files are available under `literature/corpus/pisf_prior_art/2611.13760v1/`. Mechanical inventory confirms all 21 ancillary links on the versioned abstract page have corresponding archive members. Source acquisition and inventory were assisted; substantive body/proof reading was not delegated. Ancillary programs are **not all read or rerun**, and supplied JSON records are author evidence, not independent replication. Appendix D.6 mentions a rebuilding/rerunning README; the retrieved archive has an arXiv `00README.json` build manifest and a third-party license README, but no separate experiment instructions matching that description.

**Assessment:** full reading plus the bounded independent rational/numerical checks and one original dependency-statement lookup described below. No formal replay or independent certification of every theorem. The paper is primarily mathematical, with finite-state numerical illustrations; it does not train a learned language-model architecture.

## Original question and the memory model

The paper asks how much **retained recursive memory** is needed to form and maintain useful predictions. Three tasks have different answers even when the underlying stochastic model is small: answering a future-event probability query, generating a sequence using states determined by visible observations, and simulating with a private hidden state. A second example distinguishes encoding a count after seeing an entire window from computing and updating it as data arrive and expire.

A deterministic observer starts at a fixed state independent of the observations and updates

\[
Z_{t+1}=F_t(Z_t,Y_{t+1}).
\]

At every observation time it retains at most \(K\) labels, costing \(b=\lceil\log_2 K\rceil\) bits. The maps may depend on time: **a clock is free**. Source parameters, transition/output maps and their descriptions are known; temporary computation performed by a decoder is not charged unless retained between observations. A stored prompt, cache or past observations do count. Machines can be designed for the desired horizon and error tolerance. These conventions are weaker resource accounting than charging training observations, learned parameters, arithmetic precision, tables and working memory together.

For a target \(W_t\), the best state-based squared-error estimate is its conditional mean. Proposition 2.1 and Appendix E give the orthogonal decomposition into irreducible conditional variance and decoder error. For a true one-step conditional distribution \(\Pi_t\), write \(\bar\Pi_t=\mathbb E[\Pi_t\mid Z_t]\). Then

\[
\mathbb E D(\Pi_t\Vert q_t(Z_t))
=\mathbb E D(\Pi_t\Vert\bar\Pi_t)
+\mathbb E D(\bar\Pi_t\Vert q_t(Z_t)).
\]

The proof treats zero coordinates through conditional expectation, not by dividing by a zero probability. Equal-length histories mapped to one state stay merged after any common continuation, including for time-dependent updates. This continuation constraint makes online state formation stricter than separately optimizing a representation at each time.

The loss quantifiers also differ. Window mean-square risk is \(\sup_t\mathbb E[(\text{error at }t)^2]\), not the expected maximum of a trajectory's errors. Event-query guarantees hold after every admissible history. Total generation KL averages histories under the true source but must hold at every forecast start time. Logarithms are natural except explicit base-two memory expressions.

## Positive hidden Markov models: future-event queries

Let a known finite-state HMM have strictly positive transition matrix \(P\), finite observation alphabet and emission probabilities \(g_i(y)\). For this upper bound emissions may vanish. If \(u_t\) is the predictive distribution of the next hidden state, the update after observing \(y\) is

\[
\Psi_y(u)=\frac{uD_y}{uD_y\mathbf1}P,
\qquad D_y=\operatorname{diag}(g_i(y)).
\]

After an update the belief lies in the convex hull of the positive rows of \(P\). For any future event \(B\), its conditional probability is \(uv_B\), where the likelihood vector \(v_B\) is nonnegative. The ratio \(uv_B/(wv_B)\) lies between the smallest and largest coordinate ratios of \(u,w\). Thus Hilbert projective distance controls log probability error uniformly over **every future event and every horizon**.

Write \(d_H(u,w)=\operatorname{osc}_i\log(u_i/w_i)\), \(\Delta(P)\) for the largest logarithmic cross-ratio of matrix entries, and \(\kappa=\tanh(\Delta(P)/4)<1\). The filter contracts Hilbert distance by \(\kappa\); an emission with zeros first restricts both positive beliefs to their common surviving support. Positivity of \(P\) then returns them to the interior. The proof does not assume the emission matrix itself contracts Euclidean distance.

**Theorem 3.1:** let \(L_P=\log(p_{\max}/p_{\min})\) and \(\eta=(1-\kappa)\varepsilon\). A rounded log-odds grid, with a separate exact initial label, uses at most

\[
1+\left(1+\left\lceil\frac{2L_P}{\eta}\right\rceil\right)^{m-1}
\]

states to answer all event queries with absolute log error at most \(\varepsilon\), uniformly in time, history and future horizon. Coordinate rounding gives at most \(\eta\) Hilbert error; the stable recursion sums it to \(\eta/(1-\kappa)\). The exact initial label covers priors on the boundary. Degenerate equal-row cases are handled separately rather than dividing by a zero interval width.

**Theorem 3.2:** for a stationary two-state model with strictly positive transitions **and emissions**, distinct transition rows and distinct emission laws, query memory is \(\Theta(\log(1/\varepsilon))\) bits. If either pair is identical, the observed process is iid and one state suffices. The lower bound allows time-varying maps; the construction is homogeneous. The positive-emission assumption here is stronger than the one needed for Theorem 3.1's upper bound.

**Theorem 3.3 and Appendix A.2:** the supremum log-ratio metric over all future events is the increasing limit of its finite-horizon versions. The remaining error after horizon \(T\) is at most \(\kappa^T d_H(u,w)\). The proof partitions an infinite-future event by length-\(T\) prefixes and controls each conditional suffix using contraction. Along a fixed infinite word, log likelihood ratios have an exponentially controlled tail. This is saturation of event distinguishability, not a guarantee that repeated quantized generation incurs no new error.

Figure 3 makes the distinction concrete using emission probabilities .52/.48 and hidden flip rate \(r\). At \(r=0\), comparing the two present hidden states on an all-ones continuation gives \(T\log(.52/.48)\). At every positive \(r\) it saturates. At \(r=10^{-4}\), the uniform contraction timescale is 5,000 steps, much slower than the approximately 100-step saturation of that one word. The limiting ratio is computed from the Perron eigenvector; plotted gaps below \(2\times10^{-12}\) are omitted.

## Sequential generation and the quantization lower bound

A unifilar generator emits from \(q_{t,z}\) and updates its state deterministically from the visible symbol. For an initial retained state \(z\), its word probability is the product of the emitted one-step probabilities along that word's state trajectory. Output sampling is allowed; a separate persistent random state not determined by visible symbols is excluded from this class.

The uniform-word criterion (4.3) controls the absolute log ratio for every positive source history and every word of length at most \(T\). The total-KL criterion (4.5) instead requires

\[
\sup_t\mathbb E_{Y_{1:t}}
D\!\left(P(Y_{t+1:t+T}\mid Y_{1:t})
\Vert Q_{t,Z_t}\right)\le\varepsilon.
\]

This is a **whole-horizon budget**, not \(\varepsilon\) per token. The source is fixed and known. There is also a separate initial-forecast version, with only one forecast from the initial state.

### Theorem 4.2: the general converse

Let \(\mu_j\) be the distribution of the true one-step predictor after a finite history of length \(j\), and define

\[
\mathcal D_K(\mu)=\inf_{q_1,\ldots,q_K}
\int\min_k\operatorname{TV}(p,q_k)^2\,d\mu(p).
\]

The KL chain rule along source-generated prefixes and Pinsker's inequality give

\[
\mathbb E D(P_{\mathrm{future}\mid\mathrm{past}}\Vert Q)
\ge2\sum_{j=t}^{t+T-1}\mathcal D_{K_j}(\mu_j).
\]

This finite-history statement does not require stationarity. At step \(j\), a deterministic \(K_j\)-state decoder has at most \(K_j\) output distributions. Allowing an arbitrary nearest-center assignment only weakens the lower bound; the resulting quantizer need not be recursively realizable.

For a stationary source and the every-start-time criterion, martingale convergence of finite-past predictors to the infinite-past predictor gives

\[
\varepsilon\ge2T\mathcal D_K(\mu).
\]

The passage to the limit uses a uniform Lipschitz bound for squared distance to any codebook. If \(\mu\) has infinite support, compactness ensures \(\mathcal D_K(\mu)>0\) at each fixed finite \(K\); consequently the required number of states diverges with \(T\). A small-ball estimate \(\mu(B(q,r))\le Cr^d\) gives \(\mathcal D_K(\mu)\ge\tfrac12(2CK)^{-2/d}\), hence

\[
K\ge(2C)^{-1}(T/\varepsilon)^{d/2}.
\]

Neither infinite support alone nor this power-law converse gives a matching state-count exponent or a recursively implementable optimal quantizer.

### Positive two-state classification and the upper bounds

**Theorem 4.1:** for a stationary two-state HMM with strictly positive transitions and emissions, either the observed process is iid in the two degeneracies above, or both uniform-word and total-KL generation require \(\Theta(\log(T/\varepsilon))\) **bits**. More precisely, for model-dependent positive constants and \(x=T/\varepsilon\),

\[
c x^{d_*/2}\le K_{\mathrm{gen}}\le C(1+x),
\qquad
c x^{d_*/2}\le K_{\mathrm{KL}}\le C(1+\sqrt{x}).
\]

The lower state exponents are not proved sharp. Taking logarithms yields matching order in bits despite this gap. For one initial forecast and fixed positive \(\varepsilon\), the bit cost is also \(\Theta(\log T)\).

Appendix A.6 proves a small-ball bound even when the two filter images overlap or the transition determinant is negative. The scalar filter maps have absolute derivatives bounded below by \(\lambda>0\) on a compact interior interval. Two symbols with distinct likelihood ratios have different filter fixed points; sufficiently long constant-symbol blocks have separated images. After a common outer word their separation decreases no faster than a power of \(\lambda\). An interval small enough therefore excludes one of two older blocks. Every such specified block has conditional probability at least a fixed positive \(\beta^k\), even conditioning on the recent observed word. Iterating this pruning gives a power-law mass bound. The argument excludes **disjoint word events**, so it does not incorrectly infer disjoint one-step filter images in the overlapping case.

Uniform-word generation rounds the filter accurately enough that each step has log error \(\varepsilon/T\), giving a log-odds grid with order \(T/\varepsilon\) points in the binary case. **Theorem 4.3** improves total-KL precision to order \(\sqrt{\varepsilon/T}\): with

\[
\xi=\log(1+\sqrt{\varepsilon/T}),\qquad
\eta=(1-\kappa)\xi,
\]

one-step likelihood ratios are within \(e^\xi\), and \(D\le\chi^2\le(e^\xi-1)^2=\varepsilon/T\). The chain rule gives a uniform conditional total-KL guarantee, stronger than the required average over past histories. For \(m\) hidden states, the upper bit coefficient is \((m-1)/2\) on \(\log_2(T/\varepsilon)\), up to a model-dependent additive constant.

The initial-forecast converse is not obtained by assuming an infinite observed past. Appendix A.5 couples the finite-past and stationary filters with exponentially decaying Hilbert distance and obtains

\[
\varepsilon+C_P\ge2T\mathcal D_K(\mu),
\qquad C_P=2L_P/(1-\kappa).
\]

The fixed additive allowance is then combined with the stationary quantization lower bound.

### Private-state simulation has a different cost

Proposition 4.4 samples a hidden state once from the retained approximate belief and then simulates the original HMM using private randomness. The probability of a future event is still the retained belief's mixture against the exact likelihood vector. Error is inherited from the initial approximation and does not accumulate through repeated filter rounding.

Observation and simulation phases can reuse storage: \(K_{\mathrm{obs}}+m\) labels suffice, rather than their product. In the nondegenerate two-state case the bit cost is \(\Theta(\log(1/\varepsilon))\), uniformly over horizon. Appendix A.7 also represents the private simulator as a visible-output projection of an augmented process containing hidden labels. Retaining that entire auxiliary output transcript would change the storage cost.

This distinction does **not** show that a predictor issuing forecasts on an independently arriving real sequence can privately sample a hidden hypothesis and thereafter forecast as if it were true. Exact marginal simulation and expected log loss of issued forecasts have different conditionings. Nor does the paper settle arbitrary randomized observation updates assessed after averaging their internal randomness.

## Explicit HMM evidence and independent checks

The principal numerical model has hidden flip rate \(r=1/5\), emission noise \(s=1/10\) and tolerance \(\varepsilon=.1\). The filter's interval is \([1/5,4/5]\); its two image intervals are \([8/37,5/13]\) and \([8/13,29/37]\). Appendix D derives

\[
g_V=12/65,\quad \rho=37/50,\quad
\lambda=135/1369,\quad d=\log\rho/\log\lambda.
\]

The asymptotic lower exponent is \(d/2\simeq.065\). Its numerical lower counts are below one at both example horizons, so the paper correctly calls those particular bounds vacuous and replaces them with finite-history/quantization bounds.

| Operation | Horizon | Lower states (bits) | Nominal construction states | Reachable states (bits) |
|---|---:|---:|---:|---:|
| Every future-event query | all horizons | 6 (3) | 72 | 29 (5) |
| Uniform-word generation | 100 | 6 (3) | 4,590 | 257 (9) |
| Uniform-word generation | 10,000 | 11 (4) | 458,825 | 3,139 (12) |
| Total-KL generation | 100 | 4 (2) | 225 | 51 (6) |
| Total-KL generation | 10,000 | 11 (4) | 2,198 | 183 (8) |

These are source Table 3's separate lower bounds and attained upper bounds, not exact optima. Private simulation adds two hidden labels to the 29-state observer, for 31 labels and five bits. Restricting a homogeneous machine to the initial state's transition-closed reachable set preserves all word probabilities and query answers.

**Independent rational check:** starting from the defining two-component joint probabilities, separately implemented vector filtering reproduces all six beliefs after `00000`, `00010`, `01110`, `00001`, `11101`, `01011`. For the adjacent comparisons witnessed by future `11` or `00`, the minimum ratio is exactly

\[
422842040885/345978333749>171/140>e^{1/5}.
\]

Thus no two of those equal-length positive histories can share an \(\varepsilon=.1\) query state. Independent breadth-first closure with exact rational midpoint comparisons also reproduces the uniform-grid counts

\[
(17,41,65,257,4590,458825)\mapsto(9,23,23,55,257,3139).
\]

This check did not import or run author modules. It verifies these finite constructions and separating examples, not the general converse, log-odds interval certificates or all reported experiments.

For stronger finite-horizon KL lower counts, Appendix D.2.3 uses the exactly weighted predictor law \(\mu_j\) after \(j\) observations. Coupling its starting belief with a stationary belief through the same word gives

\[
|\mathcal D_K(\mu)-\mathcal D_K(\mu_j)|
\le\zeta_j=2\sum_wP(w)\operatorname{diam}p(F_w(I)).
\]

The 65,536 atoms for \(j=16\) are sorted by exact rational comparisons. Optimal scalar squared-error quantization has consecutive cells and weighted-mean centers. Its interval-cost dynamic program has Monge structure; the authors use monotone optimal splits and exact objective comparisons, plus outward rational intervals for sums. They report

\[
\zeta_{16}<1.756943268\,10^{-10},\qquad
\mathcal D_3(\mu)>.00122730555,\qquad
\mathcal D_{10}(\mu)>.00000623283118.
\]

The test \(2T\mathcal D_K(\mu)>.1\) excludes three states at \(T=100\) and ten states at \(T=10,000\). The exact 65,536-atom certificate is author-supplied evidence and was not independently recomputed. Its derivation and reported interval bounds were read; the separate rational checks above concern history separation and uniform-grid reachability.

Figure 1's all-ones example uses a common retained belief .7625 after history `0110100111`. Adding the two exact filter fixed points to a 17-point grid changes its reachable set from 9 to 13 states and stops drift on this **particular word**. At \(T=16,384\), the reported absolute log errors are 355.553796 and .01943474. It does not make total source-averaged KL uniformly bounded for that fixed unifilar grid.

For Figure 1(c), 32 independent replicates each use a source history of length 128 and 64 conditional futures of length 4,096. Summed conditional Bernoulli KL estimates total forward KL. Reported final losses for grids 17/65/257 are 1.712960/.015759/.003601; private simulations from the same approximate beliefs give .0004605/.00000448/.00000119. Figure 4 separately tests four nondegenerate models—separated images, overlapping images, negative determinant, asymmetric transitions—and both iid degeneracies. It uses histories of length 256, 32 conditional futures per replicate and 32 replicates. Error bands use replicate-level 1.96 standard errors, respecting dependence among futures sharing a history. Each measured grid loss upper-bounds the optimal loss; the universal lower bounds come from mathematics and the quantization certificate, not from those curves.

## Sliding windows and rare-event prediction

For window length \(n\), start with \(n\) independent fair bits and let

\[
X_{t+1}=X_{t-n+1}\mathbin\oplus N_{t+1},
\qquad P(N=1)=(1-\delta)/2,\quad0<\delta\le1/2.
\]

The \(n\) residue classes are independent stationary binary Markov chains. Every consecutive block of at most \(n\) observations is iid fair, although successive windows are dependent. If \(S_t\) is the current count and \(p_\pm=(1\pm\delta)/2\), then

\[
P(X_{t+1:t+n}=1^n\mid X_{1:t})=p_+^{S_t}p_-^{n-S_t},
\quad\ell_t=n\log p_-+aS_t,\quad a=\log(p_+/p_-).
\]

The unconditional event probability is \(2^{-n}\). A one-state fair next-bit predictor has KL at most \(\delta^2\) and absolute log error at most \(2\delta\), while estimating the long rare-event log probability is equivalent to estimating the window count. Set count RMS tolerance \(E=\varepsilon/a\).

**Theorem 5.1:** for every fixed \(c\in(0,1/4)\), all sufficiently large \(n\), uniformly in \(0<\delta\le1/2\), and \(E^2\le cn\), the minimal retained bits satisfy

\[
b_*=\Theta_c\!\left(\frac{n}{1+E^2}+\log_2n\right).
\]

A constant state suffices exactly when \(E^2\ge n/4\). The constants in the theorem depend on the fixed distance from that threshold; the result is not uniform as \(c\uparrow1/4\).

### Lower-bound structure and the imported initial-count theorem

Appendix B.1 gives the algorithm its whole next window as side information. Differences between estimates along this common continuation recover counts of expiring length-\(L\) blocks with MSE at most \(4E^2\). Conditional on the next window, old bits remain independent, with variance \(v=(1-\delta^2)/4\ge3/16\). Fourier inversion bounds each block-count atom, giving a conditional-entropy lower bound. An integer-entropy/MSE inequality, proved by adding independent uniform dither and comparing with a Gaussian, bounds the entropy left after the memory and side information. Summing over blocks yields a lower bound of order \(n/(1+E^2)\). The proof uses information in the **expiration order**, not merely the one-time count distribution.

Appendix B.2 supplies the separate \(\log n\) term because the learner must form its first useful count from a fixed state. The necessary original dependency was checked directly: Braverman, Garg and Woodruff, *The coin problem with applications to data streams*, FOCS2020, DOI [10.1109/FOCS46700.2020.00038](https://doi.org/10.1109/FOCS46700.2020.00038), [ECCC TR20-139 full version](https://eccc.weizmann.ac.il/report/2020/139/), **Theorem 13, physical p.21 / printed p.20, equations (13)–(15)**.

For independent fair bits and deterministic streaming memory, the original theorem states that for \(\eta>c'n^{-1/20}\), a positive \(d_\eta\), with a polynomial lower dependence on \(\eta\), satisfies

\[
\sum_{i=1}^n I(Z_i;X_{1:i})\le d_\eta n\log n
\quad\Longrightarrow\quad
\mathbb E\operatorname{Var}(S_n\mid Z_n)\ge(1/4-\eta)n.
\]

Its §2 model, physical p.14 / printed p.13, permits a different arbitrary update function at each step, so it covers the free-clock deterministic subclass used here. Logs are base two in that source. Taking fixed \(\eta=(1/4-c)/2\) and \(I\le\log K\) gives the claimed \(\Omega_c(\log n)\) bits for large enough \(n\). The **deterministic qualification is essential to this single-sum information condition**: the older paper separately handles private randomization with a conditional double-sum measure. This was a scoped statement/model lookup, not a full reading or re-proof of the 66-page dependency.

### Bounded storage construction and the uniform-error comparison

Appendix B.3 sets \(B=\lfloor E^2\rfloor\), \(q=\lfloor E\rfloor\), \(M=\lceil n/B\rceil\), and a bit capacity \(H=\lceil8M+64\log(2n)\rceil\). It maintains a bounded residual of the centered cumulative count and a queue of signed coarse increments from completed blocks. Unary magnitude plus sign encoding gives variable-length entries inside a **fixed-capacity** queue, not merely bounded expected storage. If appending would overflow, the queue is cleared, the exact bounded residual is retained, and the estimate falls back to \(n/2\) while the queue refills.

When the needed increments are available, rounding and the expired partial block use at most \(5E^2/8\) MSE. A bounded-differences tail bound controls overflow and recovery costs uniformly in query time. It groups the at-most-two observations from each residue class in the relevant span, rather than assuming the whole span is independent. The stated state bound is \(2^H(M+1)(q+2B)\). A corollary extends the upper construction to any process with iid-fair length-\(n\) window marginals by splitting the relevant blocks into two admissible stretches; it does not thereby extend the lower bound to all such processes.

Indeed a stationary periodically repeated fair \(n\)-bit block has the same window marginals, but its count becomes fixed once the initial block has been read. Counting once and freezing needs only \(n+1\) states. This is the paper's explicit warning against deriving recursive lower bounds from single-window marginals alone.

For error bounded on **every history**, Proposition 5.3 uses \(L=\lfloor2E\rfloor+1\), \(B=\lfloor E\rfloor+1\) and proves

\[
\left\lfloor n/L\right\rfloor\le b_\infty
\le\min\{n,\lceil n/B\rceil+\lceil\log_2(2B)\rceil\}.
\]

The lower proof separates block-constant histories by a common continuation that expires preceding blocks; the upper proof uses a deterministic carry representation. When \(E<1/2\), exact \(n\)-bit memory is necessary. In the shared range \(E^2\le cn\), the uniform order is \(n/(1+E)\), different from the MSE order. Conversely, independently encoding a completed single window to MSE \(cn\) needs only \(O_c(1)\) labels, using concentration and coarse quantization; this is not an online implementation.

### Finite example and what the simulations measure

For \(n=512\), \(\delta=.02\), \(\varepsilon=.1\), the count tolerance is \(E=.1/\log(51/49)=2.49966663\ldots\). A simple completed-block estimator stores the latest \(M=\lceil n/B\rceil\) full block counts plus the current partial count, with phase supplied by the clock. Only an expired prefix of the oldest intersecting block is uncertain. Its exact count MSE at phase \(u\) is

\[
u(B-u)/(4B)\le B/16.
\]

Choosing \(B=99,M=6\) gives \(K\le99\cdot100^6\), hence at most 47 bits and RMS log error at most .099512013394. The zero-bit constant estimate has RMS log error .45260869. A guarantee on every history requires at least 102 bits; a \(B=3\) uniform carry construction uses at most 174 bits with absolute log error at most .08001067. These are distinct risk guarantees, not directly comparable optimal memory values.

The asymptotic fixed-capacity construction gives 1,143 bits for this finite example, so the experiments fall back to the 512-bit exact register there. The useful 47-bit example is the simpler block-count estimator. Figure 2's main finite experiment has 32 independent streams, each contributing 32,769 overlapping queried windows. Those windows remain grouped within their replicate when computing standard errors. Broader comparisons use 52 parameter configurations, an iid control and 32 length-\(9n\) realizations per configuration. These experiments illustrate stated estimators; they do not independently establish the lower bounds.

## Few states near the constant-estimator threshold

Appendix C studies the gain below constant count MSE \(n/4\). Let \(V_m(b)\) be the largest explained variance of the terminal count of \(m\) iid bits obtainable by a \(b\)-bit deterministic program with a free clock, and let \(\Gamma_{n,\delta}(b)\) be the all-query-time gain in the delayed-copy window. A block-transfer result bounds the latter above by \(V_n(b)\) and below by a terminal program on about half a window using about half the bits. The lower construction keeps both the current block's program state and the previous completed block's output. Clock phase identifies which completed block lies wholly inside the current window.

The conditional-score identity gives Fisher information \(16\operatorname{Var}(\mathbb E[T_m\mid Z])\) at Bernoulli parameter \(1/2\). Classifying all 16 deterministic one-bit update tables yields

\[
V_m(1)\le(1-2^{-m})/2.
\]

Alternating OR at odd times and AND at even times achieves an explicit terminal gain approaching \(1/2\) exponentially. Appendix D.11 derives an exact integer dynamic program indexed by output count and maximal signed input-count sum. Author computations through \(m=22\) find the alternating program terminally optimal. This is a finite verification range, not a proof of exact optimality at every length.

For all query times, Theorem C.6 couples the actual state with an auxiliary alternating program initialized at its parity-dependent stationary distribution. They coalesce unless the whole window is the unique nonresetting alternating word, with probability \(2^{-n}\). The resulting upper and lower bounds imply

\[
1/2-\Gamma_{n,\delta}(1)=\Theta(2^{-n})
\]

uniformly in \(\delta\). Any fixed gain below \(1/2\) therefore eventually needs just one bit, whereas gain \(1/2\) needs two bits; retaining the last two observations attains it for \(n\ge2\).

A six-state program evaluates Tribes on a completed block while retaining the preceding block's Boolean result. If \(w\) is the largest integer with \(w2^w\le\lfloor n/2\rfloor\), its exact gain has leading form

\[
\gamma_w\sim\frac{w^2}{4(e-1)}.
\]

Because \(w=\log_2n-\log_2\log_2n+O(1)\), replacing it prematurely by \(\log_2n\) gives a poor finite approximation: at \(n=10^7\), exact gain is 47.140330668, the width-based approximation is 47.140113256, and the coarse log-based expression is 78.672354289. Figure 5 displays the width-induced steps.

A read-once depth-\(2h\) AND–OR hierarchy yields gain \(c_h(\log n)^{2h}\) with \(4h+2\) labels, hence \(\lceil\log_2(4h+2)\rceil\) bits. Thus any fixed polylogarithmic gain can be obtained with a fixed number of bits when the clock is free. This explains why the fixed-fraction \(\log n\) lower bound cannot hold with constants uniform all the way to \(c=1/4\).

The free clock is substantial here. On an iid fair stream, a **homogeneous** one-bit update rule has optimal all-time gain only \(1/4\), even with a clock-dependent decoder. The proof checks all 16 tables: input-copy rules attain \(1/4\), absorbing rules lose gain, parity and input-ignoring rules do not retain useful window count, and the remaining negative-slope rules are smaller. At one terminal time, even an OR of two bits can gain \(1/3\); a terminal result must not be substituted for an every-query-time guarantee. Charging phase storage can also destroy the constant-memory interpretation of the block constructions.

## Dependencies, verification limits and remaining questions

Hilbert filter contraction is attributed to Le Gland–Oudjane and classical positive-matrix theory. Quantization uses the finite-dimensional distortion framework of Graf–Luschgy and related filter work. The manuscript distinguishes its recursion requirement from predictive rate-distortion, generative complexity, computational mechanics and short-memory prediction. It cites the correction to Marzen–Crutchfield's rate-distortion paper separately. BGW's initial-count theorem was checked only to the precise scope above. Other cited papers remain independent reading items; bibliography coverage does not count as reading their proofs.

The bounded independent work here covers exact finite-history separation and six rational grid closures. The general chain-rule/quantization argument and all supplied proofs were read and their conditions traced; this is not a full independent theorem audit. The authors' log-grid interval certificates, finite-buffer overflow implementation, full one-bit DP range, AND–OR verification and Monte Carlo figures were not independently rerun. No Lean or other formal proof was found or executed.

The main unresolved mathematical costs are sharp state-count exponents for positive HMMs, recursively attainable quantizers beyond lower bounds on arbitrary codebooks, averaged randomized observers, and operational models charging the clock, source description, parameter acquisition and temporary computation. The small-memory window results deliberately leave the transition from constant/polylogarithmic gain to a fixed fraction of \(n\) nonuniform.

The discussion's language-model connection is conditional. A teacher's own predictor distribution must exhibit enough quantization distortion over the tested state-budget range. A finite-precision teacher has finitely many possible predictive laws, so an asymptotic infinite-support argument does not automatically apply beyond that range. Teacher-forced one-step KL sums to forward generation KL only when evaluated on teacher rollouts while the student uses **its own recursively updated state**. Substituting a teacher cache or an uncharged rereadable prompt changes the decoder class. For a prompt available at every step, codebooks must be conditioned on that prompt; the manuscript gives a binary-prompt counterexample to an unconditioned bound.

There is no source-level theorem here for learning unknown mixture shape or weights from ordinary training episodes, choosing when to buy an observed reset, or pricing a reusable installed parameter packet. In particular, the persistent known-coin mixture has transition matrix \(I\), violating strict positivity. Its infinite-past predictor has two atoms, so the stationary quantization converse vanishes for \(K\ge2\); the finite-history version remains valid but requires a separate analysis. The [completed 0940e87 reply](REQUEST-2026-11-24-FINITE-MEMORY-LOG-LOSS.md) preserves that distinction and does not claim novelty for Astra's finite-coin result. No new FP architecture, transfer theorem or core-theory edit is proposed by this reading.
