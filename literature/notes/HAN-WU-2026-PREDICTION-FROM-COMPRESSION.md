# Prediction from compression: stationary terminal risk and a finite-memory information charge

## 1. Source, edition and reading boundary

Yanjun Han and Yihong Wu, **Next-symbol Prediction from Compression: Statistical and Computational Foundations**.

- Actual text read: the [12-page author PDF](https://yanjunhan2021.github.io/paper/BITS.pdf), listed on the [author's publication page](https://yanjunhan2021.github.io/publication.html) as an invited paper from February 2026 under Preprints.
- PDF creation and modification metadata: February 22, 2026, 03:24:45 UTC. This is file metadata, not an independently established publication date. SHA256: 5efd3cd45bfdc207304eaa495d3a62ba8f17817a750cd1e0780639d49d82f11d.
- A separate formal record exists in IEEE BITS the Information Theory Magazine, [DOI 10.1109/MBITS.2026.3742325](https://doi.org/10.1109/MBITS.2026.3742325), IEEE document 11733316. The publisher's Crossref record gives year 2026 and pages 1–12. Its October 12 registration is not a precise publication date. The IEEE full text was unavailable during this intake. **No identity between the read author manuscript and the formal edition is claimed.**
- Pro-D completed all 12 author-manuscript pages on November 26, 2026, Shanghai. Coverage includes §§I–V, every displayed statement and proof, Figure 1 and all 30 references. No appendix or research table is present. Original pages 3, 4, 7, 8, 9 and 10 were visually checked.
- The tutorial draws chiefly on Han–Jana–Wu's 2021/2023 Markov results and Han–Jiang–Wu's [COLT 2024 paper](https://proceedings.mlr.press/v247/han24a.html). The main reader additionally read physical pages 3, 8 and 20 of the 38-page official COLT PDF to check a material sample-range issue. This is scoped coverage of that source, not its full reading.
- Local ignored author PDF: literature/corpus/author/han-wu-2026-bits/paper.pdf. The 38-page COLT edition and distinct 37-page arXiv2404.15454v1 with TeX are prepared separately. The arXiv TeX is not treated as the source of the conference edition.

The main contribution of this reading is a precise account of the compression-to-terminal-prediction interface, its stationarity condition and its computational limits. A small independent Bayes construction refutes an overextended sample range in the read tutorial. Several transcription/normalization issues are also recorded. None of these findings is attributed to the unread IEEE edition.

## 2. The target is a random conditional distribution

Observe one path \(X^n=(X_1,\ldots,X_n)\), with law in a class \(\mathcal P=\{P_\theta\}\). The predictor outputs a distribution for \(X_{n+1}\). Its risk is

\[
\operatorname{Risk}_n(Q)
=\sup_\theta
\mathbb E_\theta D_{\rm KL}
\left(P_\theta(X_{n+1}\mid X^n)\Vert Q(X_{n+1}\mid X^n)\right).
\]

The target depends on the observed path. It is not a transition matrix at every possible state, a latent parameter vector, the average error on an independently initialized test trajectory or a high-probability guarantee for every history.

The minimax quantity is \(\inf_Q\operatorname{Risk}_n(Q)\), where the output distribution need not arise from a single fitted parameter in the original model class.

For a joint probability assignment \(Q_{X^n}\), redundancy is
\[
\operatorname{Red}(Q_{X^n})
=\sup_\theta D_{\rm KL}(P_{\theta,X^n}\Vert Q_{X^n}),
\qquad
\operatorname{Red}_n(\mathcal P)=\inf_Q\operatorname{Red}(Q_{X^n}).
\]

This is an expected cumulative log-loss excess for a joint code. Pointwise redundancy instead replaces the average by a supremum over sequences of the log likelihood ratio. A pointwise bound controls expected redundancy, but the two objectives are not identical.

With appropriate minimax conditions, the source gives
\[
\operatorname{Red}_n=\sup_\pi I_\pi(\theta:X^n),
\qquad
\operatorname{Risk}_n=\sup_\pi I_\pi(\theta:X_{n+1}\mid X^n),
\]
with finite observation alphabet assumed for the displayed prediction duality. The Bayes predictor is the posterior predictive distribution. The maximizing prior may depend on the horizon, so subtracting two separately optimized redundancy values does not automatically give the minimax prediction risk.

The general chain rule yields
\[
\operatorname{Red}_{n+1}\le\sum_{t=0}^n\operatorname{Risk}_t.
\]
It does not imply a bound on the last summand by dividing redundancy by \(n\). The conversion below supplies the extra structure.

## 3. How a joint code becomes a terminal predictor

### Finite-order stationary models

For a stationary order-\(m\) Markov class, take the conditional kernels of any joint code \(Q_{X^{n+1}}\). Apply its length-\((t-1)\) kernel to the corresponding suffix of the observed path, then average over \(t=m+1,\ldots,n+1\):

\[
\widetilde Q(x_{n+1}\mid x^n)
=\frac1{n+1-m}\sum_{t=m+1}^{n+1}
Q_{X_t\mid X^{t-1}}(x_{n+1}\mid x_{n+2-t}^n).
\]

Lemma III.3 gives
\[
\operatorname{Risk}_n(\widetilde Q)
\le\frac{\operatorname{Red}(Q_{X^{n+1}})}{n+1-m}.
\]

The proof has four substantive steps: convexity of KL under prediction averaging, removal of older history by the Markov property, transport of suffix laws by stationarity, and summation by the KL chain rule. **Stationarity performs an essential equality.** A good code alone does not justify this guarantee under arbitrary initialization or nonstationary data.

For first-order Markov chains, the construction becomes an average of suffix-based add-one predictors. This is a batch terminal predictor constructed from many suffixes, not a claim that the unaveraged last conditional of every good code is optimal.

### General stationary processes

Lemma IV.1 retains all suffix lengths \(t=0,\ldots,n\) and pays an information term:

\[
\widetilde Q(x_{n+1}\mid x^n)
=\frac1{n+1}\sum_{t=0}^n
Q_{X_{t+1}\mid X^t}(x_{n+1}\mid x_{n-t+1}^n),
\]
\[
\operatorname{Risk}_n(\widetilde Q)
\le
\frac{\operatorname{Red}(Q_{X^{n+1}})}{n+1}
\operatorname{Mem}_{n+1}(\mathcal P),
\]
\[
\operatorname{Mem}_{n+1}(\mathcal P)
=
\sup_\theta\frac1{n+1}
\sum_{t=0}^n
I_\theta(X_{n+1}:X^{n-t}\mid X_{n-t+1}^n).
\tag{memory}
\]

The added term measures the average conditional information omitted by each suffix predictor. The KL decomposition inserts the true suffix-conditional law between the full conditional target and the estimated suffix kernel. Stationarity then matches each suffix estimation term to the corresponding code increment.

This is not a finite-history approximation assertion. It averages all suffix lengths and bounds their collective information deficit.

## 4. Why a finite hidden state can control infinite observable memory

For a stationary \(k\)-state HMM, \(Z_t\) is a Markov chain and \(X_t\) is emitted independently conditional on the hidden path. Transition and emission parameters are unknown. No rank-based parameter identifiability or uniform mixing condition is imposed.

The hidden state at the suffix boundary separates the older observations from the suffix and the next output. Conditional data processing and stationarity give

\[
I(X_{n+1}:X^{n-t}\mid X_{n-t+1}^n)
\le I(X_{n+1}:Z_{n-t+1}\mid X_{n-t+1}^n)
=I(X_{t+1}:Z_1\mid X_1^t).
\]
Summing the right side yields
\[
\boxed{
\operatorname{Mem}_{n+1}
\le\frac{I(Z_1:X^{n+1})}{n+1}
\le\frac{\log k}{n+1}.
}
\]

The displayed time index on p.10 of the author manuscript is off by one. The identity above gives the consistent indexing.

This is an information bound for a supplied model family. The unknown filter can still have infinitely many belief states. A bounded hidden alphabet does not imply a bounded number of posterior values, finite precision of a learned predictor or an algorithm that stores only \(\log k\) bits. The quantity \(\log k\) bounds a separator's entropy in an analysis of the process.

HMMs can have infinite observable memory. Degenerate HMMs can also be iid or finite-order, so the text's blanket assertion of nonzero conditional dependence at every lag is stronger than its class-level point requires.

For a stationary renewal process with finite mean interarrival time, a hidden countdown state can be unbounded. Yet over a horizon \(n+1\), countdowns beyond \(n+1\) are observationally equivalent. Truncating at \(n+2\) gives
\[
I(Z_1:X^{n+1})\le\log(n+2).
\]
Thus the same memory term is \(O(\log n/n)\), while the source invokes a redundancy of order \(\sqrt n\), leading to prediction risk of order \(n^{-1/2}\). The initial residual waiting-time law must be the stationary one. Arbitrarily restarting an ordinary renewal process is a different initialization.

The full renewal lower bound and the older redundancy source are cited, not proved in the tutorial and not independently verified in this reading.

## 5. Rates and their proper regimes

| Model and target | Source rate or claim | Qualifications |
|---|---|---|
| iid alphabet of fixed size \(k\) | Redundancy \((k-1)\log n/2+O(1)\), prediction asymptotically \((k-1)/(2n)\) | The simple add-one risk is bounded by \((k-1)/(n+1)\). The sharper predictor is cited |
| Stationary binary Markov chain | \(\Theta(\log\log n/n)\) | No spectral-gap assumption. Lazy trajectories require different smoothing |
| Stationary \(k\)-state Markov chain, \(3\le k\le c\sqrt n\) | \(\Theta((k^2/n)\log(n/k^2))\) | Universal sufficiently small \(c\). Prediction and redundancy are different orders |
| Stationary HMM, fixed \(k,\ell\ge2\) | \(\Theta(\log n/n)\) | Unknown transition and emission matrices, no identifiability or mixing requirement |
| Stationary HMM with growing \(k,\ell\) | Upper bound \(C[(k^2/n)\log(n/k^2)+(k\ell/n)\log(n/(k\ell))]\) | Use the original main theorem's \(n\ge Ck(k+\ell)\), not the tutorial's enlarged range |
| Stationary renewal class | \(\Theta(n^{-1/2})\) | Finite mean, correctly stationary initialization, cited lower bound |

For the HMM lower bound, the original Theorem 1.1 separately gives conditions \(\ell\ge k,\ n\ge k\ell\), or \(n\ge k^C,\ k,\ell\ge2\). These are lower-bound regimes, not permission to enlarge the upper-bound range.

The binary Markov lower-bound mechanism and the \(k\ge3\) mechanism differ. For the latter, a lazy extra state embeds a smaller unknown chain. The time at which the path leaves the lazy state spreads the effective number of informative observations across many lengths. Averaging the resulting Bayesian prediction increments recovers a smaller chain's redundancy. The smaller chain is trivial when the total number of states is two.

Favorable mixing can improve prediction beyond the generic compression conversion. For binary reversible irreducible chains with absolute spectral gap at least \(\gamma_0\), the source states
\[
\operatorname{Risk}_{2,n}(\gamma_0)
\asymp \frac1n\log_+\log\min\{n,1/\gamma_0\},
\quad \log_+(x)=\max\{1,\log x\}.
\]
A fixed positive gap gives the parametric rate. For larger alphabets, the source gives a sufficient, not necessary, gap condition for the add-one estimator. Its claimed improvement uses a separate 2025 KL-concentration result whose proof was not read here.

## 6. Independent endpoint counterexample to the tutorial's uniform HMM range

Tutorial Theorem IV.2, p.10, replaces the original condition \(n\ge Ck(k+\ell)\) by \(n\ge k(k+\ell)\), while retaining logarithms without an additive constant. Interpreted uniformly in the displayed dimensions, this enlarged claim is false.

Take \(k=2\), even \(\ell\to\infty\), and \(n=2(\ell+2)\). The printed right side
\[
\frac4n\log(n/4)+\frac{2\ell}{n}\log(n/(2\ell))
\]
tends to zero.

For an elementary lower bound, partition the \(\ell\) symbols into \(\ell/2\) pairs. Each pair has total probability \(2/\ell\). An independent fair hidden bit selects the unique positive-probability symbol within each pair. This is a prior over iid categorical distributions.

If a pair has not appeared among the \(n\) observations, its bit remains fair. The posterior predictive assigns probability \(1/\ell\) to each of its symbols, whereas the true law assigns \(2/\ell\) to one. Its conditional Bayes KL contribution is
\[
\frac2\ell\log2.
\]
Each pair remains unseen with probability \((1-2/\ell)^n\). A seen pair's bit is known exactly. Therefore the average Bayes terminal risk is exactly
\[
\log2\,(1-2/\ell)^n
\longrightarrow e^{-4}\log2>0.
\]
The iid family embeds in a two-state stationary HMM by assigning the same emission distribution to both hidden states. Hence its Bayes risk lower-bounds the HMM minimax risk. This disproves the uniform extension to the tutorial's sample range.

**What is not refuted.** The original COLT2024 Theorem 1.1, official p.3, retains a sufficiently large universal \(C\) in its sample condition. The endpoint above need not satisfy that condition. Its fixed-\(k,\ell\) \(\Theta(\log n/n)\) result is not challenged by this example.

**The original intermediate proposition also needs care.** Official COLT p.8 Proposition 3.2 uses the weaker threshold \(n\ge k(k+\ell)\). Its p.20 emission-code calculation keeps terms
\[
\sum_i\left[
(\ell-1)\log\left(1+\frac{N_i}{\ell-1}\right)
+N_i\log\left(1+\frac{\ell-1}{N_i}\right)
\right]
\]
before absorbing them into \(O(k\ell\log(n/(k\ell)))\). This absorption is not uniform as \(n/(k\ell)\to1\).

The same pair prior directly disproves that intermediate proposition's uniform redundancy bound. Writing its hidden bits as \(B\), each visited pair reveals exactly one bit, so
\[
I(B:X^{n+1})
=\frac{\ell}{2}
\left[1-(1-2/\ell)^{n+1}\right]\log2
=\Theta(\ell)
\]
along the chosen endpoint sequence. This lower-bounds the maximum expected redundancy of any universal code. Proposition 3.2 instead claims a pointwise bound, hence also an expected bound, of
\[
4\log((\ell+2)/2)+2\ell\log(1+2/\ell)=O(\log\ell).
\]
The orders contradict. The fixed two-state hidden transition matrix can even be strictly positive and full rank, with diagonal entries \(3/4\). Identical emission rows are allowed in the stated model.

The problem is therefore not confined to the tutorial's wording. The stricter original main-theorem range remains the appropriate reusable statement. No complete revised intermediate proposition is proved in this note.

The pair construction is a limited independent mathematical check, not a simulation or a novelty claim.

## 7. Computational efficiency is a separate axis

The HMM code sums over hidden state paths. The original result uses a count-based dynamic program to reduce exponential enumeration in \(n\) to
\[
n^{O(k^2+k\ell)}.
\]
This is polynomial in \(n\) for fixed \(k,\ell\). It is not uniformly efficient in growing model dimensions, and it is not a finite-memory streaming implementation.

The tutorial cites conditional hardness results from the original COLT source:

1. Under an appropriate noisy-parity hardness assumption, for every fixed \(\epsilon>0\) and \(k\ge\log^{1+\epsilon}n\), a polynomial-time predictor cannot obtain risk \(o(\log k/(\log n\log\log n))\) with at least two output symbols.
2. Under an appropriate CSP-refutation assumption, for every fixed \(\alpha>0\), sufficiently many hidden states and \(\ell\ge n^\alpha\), a polynomial-time predictor cannot obtain \(o(1)\) risk.

These are conditional computational lower bounds, not unconditional statistical impossibility. Their exact computational assumptions and reduction quantifiers are not reproduced in the tutorial. The original Appendix D remains unread at this publication boundary and requires direct reading before using a formal hardness claim.

For example, \(0<\alpha<1\) with fixed sufficiently large \(k\) can put the information-theoretic HMM rate below a constant while leaving the cited polynomial-time obstruction relevant. Merely saying that one dimension is large does not establish a meaningful statistical-computational gap in every regime.

## 8. Other source problems that should not be copied

These were checked against the original author-PDF layout. They are local corrections or scope warnings, not a claim that all the cited source results fail.

- The p.3 Gamma-function form of the Krichevsky–Trofimov assignment has an extra factor \(1/2\). The preceding sequential product is normalized. Its correct Gamma form is
  \[
  Q(x^n)=\frac{\Gamma(k/2)}{\Gamma(n+k/2)}
  \prod_{i=1}^k\frac{\Gamma(n_i(x^n)+1/2)}{\Gamma(1/2)}.
  \]
  At \(n=1\), the printed Gamma formula gives \(1/(2k)\) rather than \(1/k\). The Stirling expression on the same page also prints \(+x\) where the leading expression uses \(-x\).
- Definition II.6 says the Hellinger packing number is the smallest feasible cardinality. The useful packing number is the largest feasible cardinality, or its supremum.
- The redundancy displays on pp.7–9 contain extra factors \(1/n\), putting redundancy on the prediction-risk scale. In particular, the upper-bound route through Corollary III.4 requires redundancy of order \(k^2\log(n/k^2)\), then divides by \(n\). The literal display cannot be substituted into that argument.
- Remark III.5's order-\(m\) exponent is inconsistent with the tutorial's own first-order convention when \(m=1\). It is not used here as a dimension-uniform higher-order theorem.
- Figure 1 uses lazy-state exit probability \(2/n\), whereas Eq.(15) uses \(1/n\). Both illustrate a slow state, but the figure is not the exact matrix used for the displayed \(1/2\) stationary mass calculation.

## 9. Relation to the preceding statistical-learning reading

The [Yüksel–Flammarion note](YUKSEL-FLAMMARION-2025-NEXT-TOKEN-GENERALIZATION.md) concerns a global empirical-risk estimator in a supplied finite-context parameter class and distinguishes visited-context KL from fresh-trajectory KL. This tutorial concerns minimax **terminal** KL along the same stationary path, obtained by an often improper mixture of suffix-code predictions.

Consequently, mixing requirements in one formulation and mixing-free consistency in the other are not automatically contradictory. They differ in the risk, the estimator, the source class, the probability mode of the bound and initialization. None of the compression arguments by itself repairs the preceding paper's high-probability block-transfer proof.

The useful positive result is that a process may be predictively learnable without identifiable parameters. The rate and feasible computation still require control of a distribution class and an actual code. A finite hidden separator bounds an information term, but does not establish autonomous discovery of a state representation.

No FP transfer is proposed. The next substantive dependency is the full official COLT2024 paper, especially its exact memory comparison, dynamic program and conditional computational lower bounds. Only its specified three pages have been read by the main reader so far.
