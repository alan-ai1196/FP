# A Unified Lower Bound on the Noisy Query Complexity of Boolean Functions

## Source and actual coverage

- **Authors:** Yuzhou Gu, Xin Li and Yinzhan Xu.
- **Publication:** COLT 2026, Proceedings of Machine Learning Research 336:2940–2962. The official conference interval is June 29–July 3, 2026.
- **Index:** PMLR-2026-GU-NOISY-QUERY.
- **Primary sources:** [official proceedings metadata](https://proceedings.mlr.press/v336/gu26a.html), [official 23-page PDF](https://raw.githubusercontent.com/mlresearch/v336/main/assets/gu26a/gu26a.pdf), [arXiv:2606.11448v1](https://arxiv.org/abs/2606.11448v1), submitted June 9, 2026.
- **Main-reader coverage, November 25:** the complete official PDF, all four body sections, every displayed argument and formula, Appendix A.1–A.4, the body footnote, acknowledgments and all 26 references. There are no figures or tables. Reliable PDF text was read in continuous page blocks, with the original dense layouts on pp. 3, 10, 11, 16, 18, 21 and 22 inspected directly.
- **Version distinction:** the arXiv source puts the main proof in body §4 and applications in §5. The official conference edition puts applications in §4 and the proof in Appendix A. The PDFs differ. This note and the full-read classification refer to the conference edition. Only the arXiv entry and source organization were checked, without claiming its full body is identical or separately fully read.
- **Verification status:** peer-reviewed theoretical paper. The main reader followed the entire proof and independently checked the local posterior and reweighting identities described below. These checks are not a formal proof or a complete independent certification of the asymptotic theorem.

## 1. Original question and model

A known Boolean function \(f:\{0,1\}^n\to\{0,1\}\) is to be evaluated on an unknown **fixed input** \(x\). The algorithm can choose an index \(i\) adaptively and observe \(x_i\) through a binary symmetric channel. Every response is independently flipped with the same fixed constant probability \(p\in(0,1/2)\). Repeated queries to one coordinate are allowed.

The noisy query complexity \(N_p(f)\) minimizes the expected number of queries, with a worst-input requirement and error at most \(1/3\). Computation between queries and the representation of the known function are not the resource being bounded.

The usual simulation gives a range between randomized exact-query complexity \(R(f)\) and \(O(R(f)\log R(f))\). Different functions attain different parts of that range. Parity needs the logarithmic overhead, whereas adaptive noisy OR and AND have linear query complexity. A maximum-sensitivity lower bound multiplied by its logarithm therefore cannot hold generally for adaptive queries.

The paper replaces maximum sensitivity by structural information in the graph of sensitive edges. It proves, for constant \(p\),

\[
N_p(f)\ge c(p)\,I(f)\log I(f),
\]

where \(I(f)\) is total influence under the **uniform** input distribution. The convention is \(0\log0=0\). This display can be weak or vacuous at very small influence. The main graph theorem retains a \(1+\) inside its logarithm and has more useful endpoint behavior.

The bound concerns worst-input computation. It is not an average-input prediction-loss theorem merely because uniform total influence appears in the formula.

## 2. Main technical theorem

Let \(H_f\) have vertex set \(\{0,1\}^n\), with an edge exactly when two inputs differ in one coordinate and their function values differ. Thus it is bipartite across \(f^{-1}(0)\) and \(f^{-1}(1)\).

Take any induced subgraph \(G\) with a nonempty edge set. Define

\[
d_1=\min_{x\in V(G)}\deg_G(x),\qquad
\mu(x)=\frac{\deg_G(x)}{2|E(G)|}.
\]

The measure \(\mu\) samples a uniformly random edge and then a random endpoint. Suppose \(d_2\ge d_1\) and

\[
\Pr_{x\sim\mu}\{\deg_G(x)\ge d_2\}\ge\gamma
\]

for a fixed constant \(\gamma>0\). Theorem 2 states

\[
N_p(f)\ge c(p,\gamma)d_2\log(1+d_1).
\]

The two degree parameters have different roles. Minimum degree controls concentration after partial revelation. A constant amount of edge-endpoint mass on high-degree vertices lets uncertainty survive the later adaptive queries. The hard input distribution is degree weighted and need not be uniform.

Taking a subgraph of minimum degree equal to the degeneracy of \(H_f\) yields Theorem 3. Since average degree is at most twice degeneracy and the average degree of \(H_f\) is \(I(f)\), the total-influence result follows.

The paper explicitly does not claim this is a complete characterization. Any bound obtained this way is at most of the order of maximum sensitivity times its logarithm, while some functions have \(R(f)\) asymptotically larger.

## 3. Three-phase reduction

Appendix A proves Theorem 2. Small bounded \(d_1\) is covered by the usual randomized-query sensitivity lower bound. The main proof takes \(d_1\) sufficiently large and treats \(p,\gamma\) as fixed constants.

It gives the algorithm a stronger interface:

1. Query every bit \(m_1=c_1\log d_1\) times nonadaptively through the noisy channel.
2. Receive selected exact input bits for free.
3. Make at most \(m_2=c_2d_2\) adaptive exact queries in expectation.

An original noisy algorithm with expected budget \(m_1m_2\) can be simulated in this interface. Stored phase-one responses cover its first \(m_1\) requests to each coordinate. When it exceeds that quota, one exact query supplies that bit, allowing every later noisy response to be simulated. The expected number of coordinates exceeding their quota is at most the total expected number of queries divided by \(m_1\).

Phase one's \(nm_1\) responses and phase two's free disclosures are deliberate extra information in a lower-bound reduction. They are not a claim that a real acquisition procedure receives those observations without cost.

Constant repetition amplifies a \(2/3\)-correct algorithm to the smaller constant error needed for the three-phase contradiction. The proof must therefore show a positive unconditional error under the hard distribution \(\mu\), not only ambiguity on an event of vanishing probability.

## 4. Making the noisy observations equivalent to partial revelation

Let \(a_i\) count ones among the phase-one responses at coordinate \(i\), and let

\[
p_j=\Pr\{\operatorname{Bin}(m_1,1-p)=j\}.
\]

Keep counts inside the window around \(pm_1\) of radius \(m_1^{0.6}\). Counts outside the window cause the corresponding bit to be revealed exactly. Within the window, selectively reveal true ones with a count-dependent probability \(q_k\).

With \(k_\ell\) the lowest integer in the window, the chosen survival factor satisfies

\[
p_k(1-q_k)
   =p_{m_1-k}\frac{p_{k_\ell}}{p_{m_1-k_\ell}}.
\]

Hence, conditional on not being revealed, the likelihood ratio of a retained count is the same for every count \(k\). The count itself gives no additional information beyond the partial revelation and its likelihood. This cancellation remains valid with the correlated prior \(\mu\).

The resulting observation \(z\in\{0,1,\star\}^n\) independently reveals each true one with probability

\[
p_+=1-d_1^{-c_3\pm o(1)}
\]

and each true zero with probability \(p_-=o(1)\). Here \(c_3=c_1(1-2p)\log((1-p)/p)<1\) after choosing \(c_1\) sufficiently small. The asymptotics are in \(d_1\), and constants depend on the fixed channel.

This is a carefully constructed disclosure mechanism in a hardness proof. It is not an estimation method for an unknown channel.

## 5. Posterior edge weights and balance

Let \(\mu_z\) be the posterior on inputs and \(X_z\) its support. Assign each surviving sensitive edge weight

\[
w_z(x,y)=
\sqrt{\frac{\mu_z(x)\mu_z(y)}
{\deg_G(x)\deg_G(y)}}.
\]

Define normalized weighted degree

\[
D_z(x)=\frac{\sum_{y:(x,y)\in E(G)}w_z(x,y)}{\mu_z(x)},
\qquad
\overline D_z=\mathbb E_{\mu_z}D_z(x).
\]

The total weighted degree on either function-value side is exactly half the total, because every edge crosses the bipartition. If almost all posterior mass has degree at most \(C\overline D_z\), neither side can have negligible posterior mass. Lemma 15 makes the exceptional-set correction explicit:

\[
\min_b\mu_z(f^{-1}(b))
\ge
\frac1{2C}
-\frac{\mu_z(A)\max_{x\in A}D_z(x)}
{C\overline D_z}.
\]

The usefulness of the degree-weighted prior is the following cancellation. For adjacent surviving inputs, Bayes' rule removes their original graph degrees from the posterior ratio. If \(N_+(x)\) and \(N_-(x)\) are up- and down-neighbors in Hamming weight,

\[
D_z(x)=\frac1{\deg_G(x)}
\left(
|N_+(x)\cap X_z|\sqrt{\frac{1-p_+}{1-p_-}}
+
|N_-(x)\cap X_z|\sqrt{\frac{1-p_-}{1-p_+}}
\right).
\]

Down-neighbors survive independently with probability \(1-p_+\), while up-neighbors survive with probability \(1-p_-\). Concentration at minimum degree \(d_1\) makes the exceptional posterior mass exponentially small in \(d_1^{1-c_3+o(1)}\). Typical weighted degrees are at most \(4\sqrt{(1-p_+)(1-p_-)}\). The average is at least one eighth of this square-root scale with high probability.

The balance lemma then gives posterior mass at least \(1/64-o(1)\) on both answers after phase two. The remaining proof shows that this balance persists with positive probability through adaptive phase three.

## 6. Why adaptive exact queries do not remove the ambiguity

The high-degree set has \(\mu\)-mass at least \(\gamma\). At least one orientation has half that mass. Complementing the entire input if necessary lets the proof use high-degree vertices with many up-neighbors.

With constant probability, a set \(B_{\mathrm{good},z}\) of these vertices retains a constant fraction of its up-neighbors and has posterior mass at least \(\gamma/4\). During exact queries, posterior mass of a fixed set is a bounded martingale. Optional stopping therefore preserves its expectation at the random stopping time. This step concerns a genuine expected-query budget.

The proof combines three requirements: good-set mass remains substantial, the bad-degree set stays negligible, and the realized number of exact queries is not too large. A conditional Markov bound gives, on an event of probability at least \(\gamma^2/64-o(1)\),

\[
q\le \frac{64c_2d_2}{\gamma^2}.
\]

One exact query removes at most one up-neighbor from any retained input, because sensitive neighbors differ at distinct single coordinates. Taking \(c_2=\gamma^2/1024\) leaves enough neighbors at every retained good vertex. Posterior normalization preserves ratios among retained inputs, so the same degree identity applies after the queries.

On this event the average weighted degree remains at least

\[
\frac{\gamma}{64}\sqrt{(1-p_+)(1-p_-)}.
\]

Degrees outside the bad set have ratio at most \(256/\gamma\) to that average. Lemma 16, the stopped version of the balance lemma, yields posterior mass at least \(\gamma/512-o(1)\) on both answers. Since the event itself has constant probability, no output rule has arbitrarily small constant error. This finishes the reduction to Theorem 2.

## 7. Applications and their conditions

Lemma 7 is the main application device. If an induced sensitive graph contains a fraction of order \(n^{-\lambda}\) of vertices of degree order \(n\), with \(\lambda<1\), and at most order \(n|S|\) edges, pruning low-degree vertices leaves minimum degree order \(n^{1-\lambda}\) while preserving constant degree-weighted mass at degree order \(n\). Theorem 2 then gives \(\Omega(n\log n)\).

| Application | Statement and mechanism |
|---|---|
| Biased random Boolean functions | For independent truth-table values with probability \(q=\gamma n^{-\lambda}\), fixed \(0<\lambda<1\), the lower bound is \(\Omega(n\log n)\) with probability \(1-\exp(-cn)\) over the function. Chernoff and Markov bounds supply enough high-degree one-inputs. |
| Counting a fixed nonempty binary subsequence pattern | For fixed constant pattern length, exact count evaluation requires \(\Omega(n\log n)\) noisy queries. The pattern need not be contiguous. A threshold reduction produces a Boolean hard function. |
| Symmetric functions and thresholds | Adjacent Hamming layers around a function-value change have degrees \(k\) and \(n-k+1\), with half the edge-endpoint mass on each layer. This recovers the displayed \(\Omega(n\log\min\{k,n-k+1\})\) bound. The main theorem itself retains \(\log(1+d_1)\). |
| Graph connectivity | For an \(N\)-vertex graph represented by all edge bits, the bound is \(\Omega(N^2\log N)\). Sensitive neighbors connect two balanced tree components into a spanning tree. |
| Fixed \(s\)-\(t\) connectivity | The same bound follows after requiring the two designated vertices to lie in different components. |

For subsequence counting, fixed prefix blocks make each zero-to-one flip in the remaining variable block increase the count by order \(\ell^{k-1}\). Bounded differences place constant probability mass in a band of width order \(\ell^{k-1/2}\). One interval of width order \(\ell^{k-1}\) therefore has mass order \(1/\sqrt\ell\). Thresholding at its endpoint and counting sensitive edges verifies Lemma 7 with \(\lambda=1/2\).

For connectivity, Cayley's tree count and Stirling's estimate show that balanced two-tree inputs occupy a fraction of order at least \(N^{-3/2}\) relative to the tree/two-tree graph, while their degrees are order \(N^2\). The ambient bit dimension is \(\binom N2\), so Lemma 7 uses \(\lambda=3/4\). This avoids the earlier paper's detailed uniform-spanning-tree structure analysis.

The random-function result is a worst-input result even though most truth-table values are zero. Guessing zero under a uniform input can have small average error and does not meet the theorem's worst-input correctness requirement.

## 8. Bounded independent checks

The following local checks were performed without claiming an independent proof of the entire theorem.

**Disclosure likelihood cancellation.** Algebraically, \(p_k/p_{m-k}=((1-p)/p)^{2k-m}\) increases with \(k\). For \(k\ge k_\ell\), the proposed reveal probabilities lie in \([0,1]\), and the retained likelihood ratio is exactly \(p_{k_\ell}/p_{m-k_\ell}\). An exact rational check with \(p=1/4\), \(m=100\), retained counts 10 through 40 verified all 31 probabilities and the common ratio \(3^{-80}\). Summing the retained likelihoods gave the same ratio for the two nonrevelation probabilities.

**Posterior-degree cancellation.** Independently substituting the degree-weighted prior into Bayes' rule gives

\[
\frac{w_z(x,y)}{\mu_z(x)}
=
\frac1{\deg_G(x)}
\sqrt{\frac{\nu_y(z)}{\nu_x(z)}}.
\]

For surviving adjacent inputs the differing bit is unrevealed, yielding the up/down factors in the paper. Conditioning on an exact response multiplies all retained input probabilities by the same factor, preserving the ratios.

**Finite exact-arithmetic check.** Four three-bit graphs were used: parity, OR, majority, and parity restricted by deleting 000 and 110, with zero-degree vertices discarded. With reveal probabilities \(p_+=13/16\), \(p_-=1/4\), all 27 possible revelation strings were considered for each graph. There were 97 positive-probability posterior cases, 192 vertex-degree identities, 372 nonempty one-query branches and 51 positive-average-degree balance cases. Exact rational arithmetic verified the degree formula, posterior martingale identity, nonincrease of retained normalized degrees and the balance inequality. The chosen probabilities test the identities and are not an asymptotic instance certifying the main concentration argument.

**Small printed endpoint issue.** Fact 11 on p. 11 writes a Stirling lower bound for all \(N\ge k\ge1\), but its denominator contains \((N-k)^{N-k+1/2}\), which vanishes at \(k=N\). The displayed formula needs \(k<N\) or a separate endpoint treatment. Its application only uses \(N/3\le k<N/2\), so this endpoint issue does not affect that connectivity argument.

The full asymptotic concentration estimates, all application constants and imported earlier results were not independently certified. No formalization or empirical algorithm replay was performed.

## 9. Dependencies, limitations and future reading

The proof uses and adapts the three-phase framework of Feige and Gu–Li–Xu 2025. It cites the earlier paper for the disclosure equivalence and parameter analysis, while presenting the likelihood cancellation and phase simulation here. The later graph weighting and balance argument are this paper's general mechanism.

Other ingredients are standard Chernoff, bounded-difference and Markov inequalities, graph degeneracy, Cayley's count and Stirling asymptotics. The 26-entry bibliography includes noisy search, sorting and decision-tree work, sensitivity comparisons and the earlier high-influence/connectivity/threshold results. Reading their uses here does not change those works' own reading status.

The paper contains no experimental section, learning-curve benchmark, memory upper bound or implementation-cost analysis. The constants in \(c(p,\gamma)\) are not uniform as \(p\to1/2\) or \(\gamma\to0\). A regime with a varying noise rate or a vanishing high-degree mass needs additional analysis.

For future use, retain these distinctions:

- The function and queryable coordinate interface are supplied. Unknown parity-support learning is a different problem.
- Responses are independent noisy copies of selected fixed coordinates. Fresh anonymous mixture reports are a different observation law.
- The objective is a known function's output with worst-input constant error, not mean log loss across future labels.
- The resource is number of queries. A finite-state learner, installed forecast table, search cost and physical report implementation require separate accounting.

No FP mapping or new theorem for aggregate-context learning is established. A concrete reduction could make the lower bound relevant later, but the present reading alone does not supply it.
