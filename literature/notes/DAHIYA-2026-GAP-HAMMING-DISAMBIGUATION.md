# Dahiya et al. 2026: the communication cost of fixing an answer on ambiguous inputs

## Source, version and reading boundary

**Yogesh Dahiya, Mika Göös, Nathaniel Harms, Hamed Hatami, Pooya Hatami, Shachar Lovett and Weiqiang Yuan. _Communication Complexity of Disambiguations of Gap Hamming Distance_. arXiv:2611.32837v1, submitted 24 November 2026, 15:50:14 UTC.**

- [Exact-version primary record](https://arxiv.org/abs/2611.32837v1), [PDF](https://arxiv.org/pdf/2611.32837v1), [complete source](https://arxiv.org/src/2611.32837v1) and [HTML](https://arxiv.org/html/2611.32837v1).
- Pro-A completed the entire 11-page manuscript on 26 November 2026, including Sections 1–4, all proofs, formulas, acknowledgements, funding and author information, and all 18 bibliography entries. The active source is the 978-line `arxiv.tex` and `refs.bib`. There are no figures, tables, appendices or footnotes. Original PDF pages 1 and 5–9 were visually inspected for the main statement, conditional distributions, constants and final iteration.
- Prepared source resides in ignored `literature/corpus/arxiv/2611.32837v1/`. PDF SHA-256: `6dd4c5598336032f57ca2425208ef6ccd9abcde52a85e66e31b4da6e5a752600`. Source archive SHA-256: `1d00ea53946d8248555d5581f9ea43ede54e72bb148ebb70235e64d16237050e`.
- This is an author preprint. No separate accepted or publisher edition was authenticated. The authors disclose that an unnamed AI model first found a square-root lower bound and, after generic prompts, a two-thirds lower bound. They extracted the ideas and rewrote the proof, with AI assistance in editing, typesetting and spellchecking. This is an author report, not identified-model attribution or independent certification. It is not an official OpenAI or Anthropic release.
- The main reader personally read the complete paper. An assisting reader authenticated the precise imported correlation bound and checked a short majority calculation. The source theorem was also checked by the main reader. No experiments, exhaustive search, formal replay or whole-proof certification were performed.

## 1. What the theorem says

Fix a constant \(\gamma\in(0,1/2)\). Alice receives \(x\in\{\pm1\}^n\), Bob receives \(y\), and the promise problem asks them to distinguish

\[
\operatorname{dist}(x,y)\le\gamma n
\quad\text{from}\quad
\operatorname{dist}(x,y)\ge(1-\gamma)n.
\]

Shared random coordinate sampling solves this promise problem with \(O_\gamma(1)\) communication. On intermediate distances, either answer is legal. A **disambiguation** is any total Boolean function \(F(x,y)\) agreeing with the required answers outside that intermediate region.

**Theorem 1.1:** every such total extension satisfies

\[
R_{1/3}(F)=\Omega_\gamma(n^{2/3}).
\]

Here communication cost is worst-case bits, public coins are allowed, and error is bounded on **every input**, including every pair in the ambiguity region. The extension can depend arbitrarily on the full pair \((x,y)\). It need not be a function of distance, or even of \(x\odot y\). The hidden lower-bound constant may depend on fixed \(\gamma\). The statement does not give a uniform bound for \(\gamma\) varying with \(n\).

The requirement to choose a fixed answer on all intermediate inputs is the source of the separation. This is not the usual narrow-gap Hamming problem with a gap of order \(\sqrt n\). Its promise gap has linear width, which is why the promise-only problem itself costs a constant number of bits.

The introduction reports an earlier \(\Omega(\log\log n)\) disambiguation bound and a conjectured linear lower bound. Those historical claims are recorded as the authors' account. Their separate recent sources were not fully read here. The present theorem establishes the two-thirds exponent, not optimality.

### Two corollaries with explicit reductions

A pseudodeterministic protocol for a relation must, for each fixed input, output one fixed legal value \(h(x,y)\) with probability at least \(2/3\). General randomized correctness only requires some legal answer with that probability. For the binary Gap Hamming relation, the canonical map \(h\) is exactly a total disambiguation. Thus the same relation has \(O_\gamma(1)\) randomized and \(\Omega_\gamma(n^{2/3})\) pseudodeterministic communication complexity.

For additive Hamming estimation with fixed \(\varepsilon\in(0,1/2)\), legal outputs satisfy \(|t-\operatorname{dist}(x,y)|\le\varepsilon n\). If \(h\) is a canonical estimator, then \(F=\mathbf1[h\ge n/2]\) is a disambiguation with \(\gamma=(1/2-\varepsilon)/2\). Thresholding the estimator's output computes \(F\) with the same success probability. This proves Corollary 1.2, including its constant-versus-polynomial separation. It does not assert that arbitrary relational success can always be amplified.

For Gap Majority on a single sign string \(z\), each parity query on \(z=x\odot y\) is simulated by exchanging the two local parities. Therefore a depth-\(q\) randomized parity decision tree supplies a communication protocol of cost at most \(2q\). Corollary 1.3 gives the same \(\Omega_\gamma(n^{2/3})\) lower bound for every total disambiguation of Gap Majority.

## 2. The imported correlation theorem really applies to arbitrary protocols

Theorem 2.1 imports Girish–Sinha–Tal–Wu, _Fourier Growth of Communication Protocols for XOR Functions_, FOCS 2023, Theorem 1.5. The directly checked source is [arXiv:2307.13926v1](https://arxiv.org/abs/2307.13926v1), [HTML](https://arxiv.org/html/2307.13926v1) and [PDF](https://arxiv.org/pdf/2307.13926v1). The arXiv manuscript is 64 pages. The distinct IEEE edition, DOI [10.1109/FOCS57990.2023.00047](https://doi.org/10.1109/FOCS57990.2023.00047), was not read.

Coverage is restricted to Definition 1.1, Theorem 1.2 and the randomization remark, Section 1.2.1 including Theorem 1.5, and the relevant conversion at the start of Appendix A. The auxiliary reader also inspected protocol conventions in Sections 4.1–4.2. This is dependency authentication, not a full reading or reproof of the Fourier-growth theorem.

Let \(U,V\) be independent uniform sign strings, and let \((U',V')\) have independent coordinate pairs with uniform marginals and \(\mathbb E[U'_iV'_i]=\rho\). Every binary protocol \(\Pi\) communicating at most \(d\) bits obeys

\[
\left|\Pr[\Pi(U,V)=1]-\Pr[\Pi(U',V')=1]\right|
\le K|\rho|\sqrt d
\]

for an absolute constant \(K\), with the harmless output-bit convention described below. **No XOR-invariance assumption is imposed on \(\Pi\).**

To see the exact translation, fix all protocol coins \(r\), write \(C_r=2\Pi_r-1\), and form its XOR-fiber

\[
h_r(z)=\mathbb E_{X\text{ uniform}}C_r(X,X\odot z).
\]

GSTW Definition 1.1 permits any deterministic protocol. If the independent coordinates of \(Z\) have mean \(\rho\), then \((X,X\odot Z)\) is exactly the required correlated pair. Thus the acceptance-probability difference is one half of the corresponding difference in expectations of \(h_r\). Apply GSTW Theorem 1.5 and average over \(r\). The parameter \(\rho\) does not need rescaling.

Local input-dependent sampling kernels can be realized with independent random seeds and included in the fixed coins. They do not add communication. The theorem charges maximum communication, not expected communication. If output is required to be a transcript label instead of Bob's local final answer, one extra bit suffices. For \(d\ge1\) this changes only constants. With zero communication, both hypotheses have identical local marginals, so any local acceptance probability is identical.

The proof uses \(d=R_{1/100}(F)\) and \(\rho=c_0/\sqrt d\), with \(c_0>0\) sufficiently small that the correlation change is at most \(1/100\). Neither paper supplies a numerical value of the absolute constant needed for a numerical \(c_0\).

## 3. Uniform proxies retain enough conditional min-entropy

All entropy logarithms are base two. On \(\{\pm1\}^m\), define the min-entropy deficit

\[
D_\infty(\mu)=m-H_\infty(\mu)=\log(2^m\|\mu\|_\infty).
\]

Lemma 3.1 starts with \(D_\infty(\mu)\le D\) and constructs a coupling \((X,U)\) with \(X\sim\mu\), \(U\) uniform, satisfying two different properties:

1. \(\mathbb E\operatorname{dist}(X,U)\le\sqrt{mD}\).
2. For every fixed coordinate set \(I\) and \(s>0\), let \(\nu_u\) be the law of \(X_{\bar I}\) given \(U_I=u\). Then

\[
\Pr\!\left[\nu_{U_I}(X_{\bar I})>
2^{-(m-|I|)+D+s}\right]\le2^{-s}.
\]

The second conclusion is a joint high-probability point-mass bound. It is not a deterministic entropy guarantee for every revealed proxy value. Later truncation converts this probabilistic control into a supportwise bound.

### Construction and collision calculation

Set \(a_i(x_{<i})=\mathbb E[X_i\mid X_{<i}=x_{<i}]\). With independent \(T_i\) uniform on \([-1,1]\), set

\[
X_i=1\iff T_i\le a_i(X_{<i}),
\qquad U_i=1\iff T_i\le0.
\]

The mismatch probability at coordinate \(i\), conditional on the past of \(X\), is \(|a_i|/2\). The elementary entropy bound \(H(\operatorname{Ber}((1+a)/2))\le1-a^2/4\), the entropy chain rule and \(H(X)\ge H_\infty(X)\) imply \(\sum_i\mathbb E a_i^2/4\le D\). Cauchy–Schwarz proves the expected-distance bound.

For the conditional claim, put \(Z=(U_I,X_{\bar I})\). The key induction proves

\[
\operatorname{col}(Z):=\sum_z\Pr[Z=z]^2\le\|\mu\|_\infty.
\]

If the first coordinate is outside \(I\), conditioning on \(X_1=a\) with probability \(p_a\) yields the bound \(\sum_a p_a^2\|\mu\|_\infty/p_a\le\|\mu\|_\infty\). If it is inside \(I\), the first proxy bit is uniform. Convexity of collision probability and the conditional induction hypothesis give

\[
\operatorname{col}(Z)
\le\tfrac12\|\mu\|_\infty
\mathbb E[1/p_{X_1}]
\le\|\mu\|_\infty.
\]

The last inequality uses the binary support size. Future thresholds remain independent after fixing \((X_1,U_1)\), which is what justifies applying the same coupling induction to the conditional tail.

Since \(U_I\) is uniform,

\[
\mathbb E\!left[2^{m-|I|}\nu_{U_I}(X_{\bar I})\right]
=2^m\operatorname{col}(Z)\le2^D.
\]

Markov's inequality gives the stated tail. This additional collision argument is the part needed to keep iterating after the inputs cease to be uniform. A distance coupling alone would not supply it.

## 4. Planting, restoring and the exponent

### Planting a block without losing product structure

Lemma 4.1 begins with a product law \(\mu\times\nu\), \(\mathbb E F\ge1/2\), an unprocessed coordinate set \(J\) of size \(m\ge100/\rho\), and both \(J\)-marginal deficits at most \(D\). It obtains a block \(I\subseteq J\), a common reference \(w\), and a restricted product law such that

\[
|I|\ge\rho m/2,
\quad
\operatorname{dist}(x_I,w),\operatorname{dist}(y_I,w)
\le b:=20\rho\sqrt{mD}
\]

for every point in the restricted support, while \(\mathbb E F>1/4\) and each remaining marginal deficit is at most \(D+7\).

Apply the uniform-proxy coupling separately on the two sides. A communication protocol on proxy inputs locally samples the corresponding original inputs and runs the protocol for \(F\). Under independent uniform proxies this reproduces \(\mu\times\nu\). Under correlated proxies, GSTW and the two pointwise protocol-error bounds give \(\mathbb E F\ge47/100\). At this intermediate stage the two original inputs need not be independent.

Generate correlated proxies by including each coordinate in \(I\) with probability \(\rho\), giving both proxies the same uniform value \(w\) on \(I\), and sampling their remaining coordinates independently. **After conditioning on \(R=(I,w)\), the two original inputs are independent.** This is why separate one-side truncations retain a product law.

On each side, the failure probability for the distance cutoff is at most \(1/20\). The min-entropy point-mass cutoff uses \(s=5\), giving another \(1/32\). Chernoff bounds the probability of \(|I|<\rho m/2\) by \(e^{-\rho m/8}<1/100\). Their union has probability less than \(1/5\). Thus some fixed \(R\) retains more than \(1/4\) of the weighted acceptance mass.

For that \(R\), each one-side retained probability is greater than \(1/4\). Conditioning therefore multiplies its marginal point masses by less than four. Combined with the \(D+5\) cutoff this gives \(D+7\). When \(D=0\), the coupling has zero mismatch and the distance event holds surely. There is no need to divide by the zero cutoff in Markov's inequality.

### Restoring acceptance costs entropy

Lemma 4.2 fixes protocol coins under any input law \(\xi\) with \(\mathbb E_\xi F\ge1/4\), retaining error at most \(1/100\). Its deterministic leaves are rectangles. Relabel any accepting leaf with conditional \(\mathbb E F<1/2\) as rejecting, which cannot increase distributional error. The surviving accepting leaves have total mass at least \(1/5\). At most \(2^d\) leaves exist, so one rectangle \(A\times B\) has mass at least \(2^{-d}/5\) and conditional \(\mathbb E F\ge1/2\).

If \(\xi=\mu\times\nu\), conditioning on this rectangle preserves the product form. Each marginal event has probability at least the rectangle's probability, hence each marginal min-entropy deficit increases by at most \(d+\log5<d+3\).

### The full recurrence

If initially \(\mathbb E F<1/2\) under uniform inputs, replace \(F(x,y)\) by \(1-F(x,-y)\). This preserves the promised labels and communication complexity. Initially \(m_0=n\), \(D_0=\Delta_0=0\). Planting followed by restoration maintains product inputs, acceptance at least \(1/2\), and distance at most \(\Delta_t\) from a common reference on processed coordinates. The recurrence is

\[
m_{t+1}\le(1-\rho/2)m_t,
\qquad D_{t+1}\le D_t+d+10,
\qquad \Delta_{t+1}\le\Delta_t+20\rho\sqrt{m_tD_t}.
\]

Stop when \(m_T\le\gamma n/2\). Because the stopping target is a fixed fraction of \(n\),

\[
T\le\left\lceil\frac2\rho\ln\frac2\gamma\right\rceil
=O_\gamma(1/\rho),
\qquad
\Delta_T\le20\rho\sqrt{n(d+10)}T^{3/2}
=O_\gamma(\sqrt n\,d^{3/4}).
\]

There is no extra \(\log n\) round count. Under \(d\le c_\gamma n^{2/3}\), a sufficiently small constant \(c_\gamma\) ensures \(\Delta_T\le\gamma n/4\). The condition \(\rho m_t\ge100\) holds before stopping for sufficiently large \(n\). Every remaining pair then satisfies

\[
\operatorname{dist}(x,y)\le2\Delta_T+m_T\le\gamma n,
\]

forcing \(F=0\) everywhere, contrary to maintained acceptance. Constant-factor amplification transfers the resulting \(R_{1/100}\) lower bound to \(R_{1/3}\).

The exponent accounting is explicit: the correlation theorem permits \(\rho\asymp d^{-1/2}\), so there are \(O_\gamma(\sqrt d)\) rounds, entropy deficit can grow to order \(d^{3/2}\), and the accumulated distance is order \(\sqrt n\,d^{3/4}\). Balancing this with \(n\) produces \(d\asymp n^{2/3}\).

## 5. A local tightness calculation and its limited implication

GSTW already uses majority of coordinate products as its tight level-one Fourier-growth example. The following explicit derivative is a note-level calculation of that existing witness, not a new lower-bound construction.

Let \(k\) be odd. Alice sends \(x_1,\ldots,x_k\), and Bob accepts when \(S=\sum_{i=1}^k x_i y_i>0\). Communication is \(k\) bits for a local Bob output, or at most \(k+1\) with an announced output. Under a \(\rho\)-correlated pair, the products \(Z_i=x_i y_i\) are independent signs of mean \(\rho\). Set \(h(\rho)=\Pr_\rho[S>0]\). Differentiating the finite probability polynomial gives

\[
h'(0)=\mathbb E_0[S\mathbf1_{S>0}]
=\tfrac12\mathbb E_0|S|
=\frac{k}{2^k}\binom{k-1}{(k-1)/2}
\sim\sqrt{\frac{k}{2\pi}}.
\]

For the exact binomial identity, condition the contribution of \(Z_i\) on the even integer \(T_i=S-Z_i\). Then \(\mathbb E[Z_i\mathbf1_{S>0}\mid T_i]=\frac12\mathbf1_{T_i=0}\), and sum over \(i\).

Consequently a correlation sensitivity bound valid for all protocols cannot replace the local linear coefficient \(O(\sqrt d)\) by \(o(\sqrt d)\). This explains why merely improving that universal exponent cannot improve the Dahiya recurrence. It does **not** show the two-thirds lower bound is optimal. A stronger argument could use additional structure of disambiguations or change the iterative method.

## 6. Assessment and relevance boundary

The source presents a mathematical lower bound, not empirical evidence. The consequential local steps checked here are the arbitrary-protocol scope of GSTW, coin and output normalization, the collision induction, the recovery of conditional product structure, both truncation constants, rectangle restoration and the final recurrence. No concrete gap was found in this bounded reading and manual checking. This does not certify all imported theorems or establish formal correctness.

Totality is essential at two places: the protocol error bounds must hold on the distributions introduced by the proxy coupling, and the restoring rectangle must compute a fixed Boolean target on all its inputs. Those distributions can visit the original ambiguity region. A protocol solving only the promise relation cannot be substituted into that argument.

For FP, this is a precise warning that replacing a set of acceptable answers by a reproducible canonical answer can change computational resources substantially. It is not a lower bound on finite-state prediction, learned state formation, general sampling, or inference-time memory. Such a transfer would require a concrete reduction producing the total disambiguation from an FP object, with communication and public randomness charged. No such reduction is established here, and no core definition or architecture is proposed.

The open linear lower bound and exact exponent remain source-level research questions. No further full reading of historical dependencies is needed for this completed intake.
