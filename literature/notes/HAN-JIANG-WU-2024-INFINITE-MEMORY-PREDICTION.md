# Infinite-memory prediction from compression: finite-sample bounds and computational qualifications

## 1. Source and actual reading

Yanjun Han, Tianze Jiang and Yihong Wu, **Prediction from compression for models with infinite memory, with applications to hidden Markov and renewal processes**, COLT 2024, PMLR 247:2270–2307.

- Primary [publisher record](https://proceedings.mlr.press/v247/han24a.html) and [official 38-page PDF](https://proceedings.mlr.press/v247/han24a/han24a.pdf). SHA256: 47322ccbc1d3733f205617ea43b574ae336eb05eb95153f3652635e1f9dbbe67.
- The hosted PDF retains a placeholder proceedings-volume line on its first page. The bibliographic edition is authenticated by the PMLR catalogue, not that placeholder.
- The related [arXiv2404.15454v1](https://arxiv.org/abs/2404.15454v1) has 37 pages. Its PDF and TeX were recovered as auxiliary material but are not substituted for the conference edition or credited with a separate complete reading.
- Pro-D personally completed all 38 official pages on November 26, 2026, Shanghai. Coverage includes §§1–4, the full reference list, contents, Appendices A–E, every displayed argument, all three numbered footnotes and the sole Figure 1, an algorithm box on p33. Original PDF pages 6, 8, 18, 33, 35 and 36 were visually checked during this full-reading unit.
- A necessary historical dependency, Sharan et al., [Prediction with a Short Memory](https://theory.stanford.edu/~valiant/papers/Pred_Mem.pdf), STOC 2018, was read only at pp1–2,4,8. This covers the risk comparison, Theorem 2 and CSP hypothesis. Its other body and proofs remain unread by the main reader.
- Ignored local official PDF: literature/corpus/pmlr/v247/han24a/paper.pdf. The earlier [2026 tutorial note](HAN-WU-2026-PREDICTION-FROM-COMPRESSION.md) records the first exact endpoint counterexample. This note completes the original dependency and adds an all-sample correction and bounded checks of other material interfaces.

The useful result is that stationarity plus a finite hidden information separator permits prediction without a mixing-time or parameter-identifiability assumption. The optimal statistical construction can still be computationally expensive. The source also contains several incorrect literal formulas or ranges. The independent findings below distinguish those exact failures from the nondegenerate main asymptotic claims, which are not fully certified here.

## 2. Statistical experiment and quantifiers

There is one observed trajectory \(X^n\). A stationary hidden Markov chain \(Z_t\in[k]\) has unknown transition matrix \(M\), and emissions \(X_t\in[\ell]\) have unknown row-stochastic kernel \(T\). Given the hidden path, emissions are conditionally independent. No positive spectral gap, mixing time, identifiable parametrization, full-rank transition matrix or separation between emission rows is required for the upper-bound class.

The target is the next-symbol law conditional on the actual observed history:

\[
R_n(Q)=\sup_\theta
\mathbb E_\theta
D_{\rm KL}\!\left(
P_\theta(X_{n+1}\mid X^n)\Vert Q(X_{n+1}\mid X^n)
\right),\qquad
R_n^*=\inf_Q R_n(Q).
\]

The supremum ranges over stationary models in the stipulated class. This is expected same-trajectory terminal conditional KL. It is neither latent-parameter recovery nor a guarantee on a separately initialized test path, every history, an uncontrolled distribution shift or a future rollout of arbitrary length.

The predictor may be improper. A mixture of conditional distributions from different suffix lengths need not be the posterior predictive distribution of one fitted HMM.

For a joint code \(Q_{X^{n+1}}\), define its expected redundancy
\[
\operatorname{Red}(Q)=
\sup_\theta D_{\rm KL}(P_{\theta,X^{n+1}}\Vert Q_{X^{n+1}}).
\]
Pointwise redundancy further takes a maximum over observation strings of the log likelihood ratio. A pointwise guarantee implies the expected one. A cumulative redundancy bound alone does not bound its final conditional increment without an additional conversion argument.

## 3. Main source claims and their regimes

The following table reports the source statements, with the nondegenerate HMM regime \(k,\ell\ge2\) made explicit. The literal omission of \(k\ge2\) in one printed lower-bound branch is examined in §7.

| Source statement | Mathematical content | Qualification |
|---|---|---|
| Theorem 1.1, p3 | For sufficiently large universal \(C\), \(n\ge Ck(k+\ell)\) gives \(R_n^*\lesssim (k\ell/n)\log(n/(k\ell))+(k^2/n)\log(n/k^2)\). | The threshold is essential. The weaker threshold in Proposition 3.2 is false for its printed uniform bound. |
| Theorem 1.1 lower bound | Matching order if \(\ell\ge k,\ n\ge k\ell\), or if \(n\ge k^C,\ k,\ell\ge2\). | These are parameter regimes, not an all-\(n,k,\ell\) minimax formula. The lower proof uses separate constructions. |
| Theorem 1.1 computation | The upper bound has an \(n^{O(k^2+k\ell)}\) algorithm. | Polynomial for fixed \(k,\ell\), not uniformly efficient in growing model size. |
| Theorem 1.2, pp3,33–34 | A polynomial-time predictor achieves \(O(\log k\log\ell/\log n)\) when \(\log k\log\ell=o(\log n)\). | Uses a finite-order Markov approximation and loses statistical accuracy relative to the fixed-size optimum. |
| Theorem 1.3 and D.4, pp4,34–36 | Conditional computational barriers from LPN and planted-CSP hypotheses. | Two different hardness assumptions. The first branch's printed unrestricted large-\(k\) range cannot be literal. See §9. |
| Theorem 1.4, pp4–5 | Stationary renewal processes with arbitrary positive-integer interarrival law of finite mean have minimax prediction rate \(\Theta(n^{-1/2})\). | The upper bound uses a redundancy theorem and a possibly expensive normalized maximum-likelihood code. No efficient implementation is established. |

For a fixed nondegenerate HMM size, the paper asserts a \((\log n)/n\) terminal KL rate. This is compatible with some models being much easier. It is a worst-case class result.

## 4. Stationarity converts a joint code into a predictor

Proposition 2.1 and Appendix B.1 use the code's conditional kernels on all nonempty suffixes:

\[
\widetilde Q(x_{n+1}\mid x^n)
=\frac1n\sum_{t=1}^n
Q_{X_{t+1}\mid X^t}(x_{n+1}\mid x_{n-t+1}^n).
\]

For a fixed stationary \(P\), convexity of KL, addition and subtraction of the true suffix conditional, stationarity and the KL chain rule give

\[
\mathbb E_P D_{\rm KL}(P_{X_{n+1}\mid X^n}\Vert\widetilde Q)
\le
\frac{D_{\rm KL}(P_{X^{n+1}}\Vert Q)-D_{\rm KL}(P_{X_1}\Vert Q_{X_1})}{n}
+\frac1n\sum_{t=1}^n
I_P(X_{n+1}:X^{n-t}\mid X_{n-t+1}^n).
\]

Dropping the nonnegative initial KL and then taking the model supremum yields the class bound
\[
R_n(\widetilde Q)\le\frac{\operatorname{Red}(Q)}n+\operatorname{mem}_n(\mathcal P),
\quad
\operatorname{mem}_n(\mathcal P)=
\sup_{P\in\mathcal P}\frac1n\sum_{t=1}^n
I_P(X_{n+1}:X^{n-t}\mid X_{n-t+1}^n).
\]

The supremum must also cover the memory term. Printed Eq. (9) suppresses it while using class worst-case risk, but Eq. (11) and the completed proof give the proper interface.

The original conference construction averages \(n\) nonempty suffixes. The later 2026 tutorial averages \(n+1\) suffixes, including the empty one. Their normalizations should not be silently interchanged.

For an HMM, conditional data processing bounds each omitted-history term by the information in the hidden state at the suffix boundary. Stationarity relocates that state to \(Z_1\), and the chain rule gives

\[
\sum_{t=1}^n I(X^{n-t}:X_{n+1}\mid X_{n-t+1}^n)
\le
\sum_{t=1}^n I(Z_1:X_{t+1}\mid X^t)
=I(Z_1:X_2^{n+1}\mid X_1)
\le H(Z_1)\le\log k.
\]

This proves the usable information charge \(\operatorname{mem}_n\le\log k/n\). The source's pp19–20 equality to \(I(Z_1:X^{n+1})\) omits the \(X_1\) term. Replacing that equality by an inequality preserves the final bound.

This argument bounds information about the past needed to compare ideal conditional laws. It does not construct a learned finite-bit recursive state, identify the hidden generator, or show that \(k\) persistent implementation states suffice.

## 5. An all-sample redundancy bound for the paper's actual code

### 5.1 The add-one joint assignment

Equations (15)–(17) start the hidden state uniformly on \([k]\), code each transition row by add-one counts, and independently code each emission row by add-one counts. The observed code sums this valid joint distribution over hidden paths.

The introductory inequality on p8 reverses KL data processing. The usable direction is
\[
D_{\rm KL}(P_X\Vert Q_X)
\le D_{\rm KL}(P_{X,Z}\Vert Q_{X,Z}).
\]
The joint pointwise argument and marginal summation give the desired direction independently of that printed reversal.

Proposition 3.2 claims a pointwise bound of order
\[
k^2\log(n/k^2)+k\ell\log(n/(k\ell))
\]
already for \(n\ge k(k+\ell)\). The exact unseen-pair calculation in the [tutorial note, §6](HAN-WU-2026-PREDICTION-FROM-COMPRESSION.md) refutes this uniform endpoint range. At \(k=2,\ n=2(\ell+2)\), its right side is only \(O(\log\ell)\), whereas a stationary iid-emission subclass has redundancy \(\Theta(\ell)\). The corresponding terminal Bayes risk tends to a positive constant. The nondegenerate main upper theorem's sufficiently large \(C\) is a different condition.

### 5.2 Independent correction, with a proof

For \(u,v>0\), set
\[
F(u,v)=u\log(1+v/u)+v\log(1+u/v).
\]
Use the continuous boundary convention \(F(u,0)=F(0,v)=0\), and write
\[
d_{\rm tr}=k(k-1),\qquad d_{\rm em}=k(\ell-1).
\]

**Independent finite-sample bound.** For every integer \(n\ge0\), every \(k,\ell\ge1\), every initial distribution \(\pi\), transition matrix \(M\) and emission kernel \(T\), the joint add-one code of the source satisfies
\[
\boxed{
\sup_{x^{n+1},z^{n+1}}
\log\frac{\pi(z_1)\prod_{t=1}^nM(z_{t+1}\mid z_t)
\prod_{t=1}^{n+1}T(x_t\mid z_t)}
{Q_{\rm joint}(x^{n+1},z^{n+1})}
\le
\log k+F(n,d_{\rm tr})+F(n+1,d_{\rm em}).
}
\tag{A}
\]

The supremum ignores zero-probability numerator strings in the usual way. This statement itself does not require stationarity.

To prove it, consider one categorical row with alphabet size \(a\), counts \(c_1,\ldots,c_a\) and \(m=\sum_jc_j\). Its add-one assignment is
\[
Q_{\rm row}=\frac{(a-1)!\prod_jc_j!}{(m+a-1)!}.
\]
For any row probability vector \(p\),
\[
\frac{\prod_jp_j^{c_j}}{Q_{\rm row}}
=
\binom{m+a-1}{a-1}
\left(\frac{m!}{\prod_jc_j!}\prod_jp_j^{c_j}\right)
\le\binom{m+a-1}{a-1}.
\]
The parenthesized quantity is one multinomial probability. The elementary entropy bound for a binomial coefficient yields
\[
\log\binom{m+b}{b}\le F(m,b),\qquad b=a-1.
\]
For fixed \(b\), \(F(m,b)\) is concave in \(m\). It is also jointly homogeneous. The transition row totals sum to \(n\), so
\[
\sum_{i=1}^kF(m_i,k-1)
\le kF(n/k,k-1)=F(n,k(k-1)).
\]
The emission totals sum to \(n+1\), yielding \(F(n+1,k(\ell-1))\). Finally, \(\pi(z_1)/(1/k)\le k\). Multiplying the row bounds proves (A). Summing the pointwise inequality over hidden paths gives the same observed-code bound.

With stationarity restored, the compression conversion gives the independently derived usable bound
\[
\boxed{
R_n^*
\le
\min\left\{\log\ell,
\frac{2\log k+F(n,d_{\rm tr})+F(n+1,d_{\rm em})}{n}
\right\},\qquad n\ge1.
}
\tag{B}
\]
The first term is the uniform predictor. The second is attained as an upper bound by the original code and suffix mixture. One can choose between them using the known dimensions and sample size.

For \(n\) much larger than the dimensions, \(F(n,d)=d\log(n/d)+O(d)\), recovering the large-sample order. Near the problematic emission endpoint, \(F(n+1,d_{\rm em})=\Theta(\ell)\), as required by the counterexample. When \(n\ll d\), the term \(n\log(1+d/n)\) matters. Replacing the entire expression by \(d\log(1+n/d)\) would lose that regime.

Equation (B) is a valid bound, not a claim of sharp minimax constants or optimality for every boundary case. For example, \(k=1\) is iid and the compression conversion can lose a logarithmic factor.

### 5.3 General emission families

Corollary 3.3 and Appendix B.4 replace categorical emissions by a family \(\mathcal Q\). If its iid redundancy at length \(t\) is bounded by a concave function \(R(t)\), concavity pools the per-hidden-state sample counts:
\[
R_n^*\lesssim
\frac{k^2}{n}\log(n/k^2)
+\frac{k}{n}R((n+1)/k)
\]
in the stipulated \(n\gtrsim k^2\) regime. The transition term retains its own range conditions.

For bounded means and known identity covariance in \(d\)-dimensional Gaussian emissions, the stated consequence is \(O(k(k+d)\log n/n)\). This is a prediction result under that emission family, not recovery of an arbitrary mixture or an unknown covariance model.

## 6. Why the optimal code can be expensive

Appendix D.1 marginalizes hidden paths by transition and emission count matrices. For observed \(x^K\), let \(A(M,T:x^K)\) count hidden paths with those counts. The emission row total minus the outgoing-transition row total identifies the final state when a valid path exists.

Figure 1 recursively removes a final emission and one incoming transition, then sums over the possible predecessor state. Counts with negative entries or inconsistent totals represent zero paths. Those zero conventions and the unsuccessful \(K=1\) base case should be made explicit in an implementation. The printed box is not a fully guarded program.

The count grid has at most \(K^{O(k^2+k\ell)}\) entries. Reusing entries by dynamic programming, rather than recursively re-enumerating paths, produces the source's fixed-dimension polynomial bound. This counts arithmetic work on count-indexed states. It does not establish a small streaming workspace or a finite-bit precision bound for evaluating all code probabilities.

Appendix D.2 instead codes the observations with an order-\(d\) Markov model. Its error has a memory-approximation term of order \(\log k/d\) and a coding term growing roughly as \(\ell^{d+1}/n\), with logarithmic and boundary terms retained in the proof. Choosing \(d\) proportional to \(\log n/\log\ell\) makes the count computation polynomial in \(n\) and yields the slower rate of Theorem 1.2.

The two algorithms expose a statistical-computational tradeoff. Neither establishes that next-token training of a prescribed neural architecture finds the code or its sufficient summary.

## 7. Statistical lower bounds and two precise boundary checks

### 7.1 How the source proves the nondegenerate lower rates

Section 4 and Appendix C convert redundancy of a smaller HMM class into prediction difficulty of a slightly enlarged class.

- Proposition 4.1 adds a slowly exited auxiliary state and a special observation. A random effective informative-history length makes the terminal prediction problem charge information acquired over many shorter lengths.
- For binary observations, Proposition 4.2 cannot reserve a distinct extra observation. It instead controls the information revealed by an auxiliary exit time. Lemma A.2 explicitly charges the change in the oracle's information.
- The binary-state binary-emission case has its own rare-transition construction and a harmonic sum of conditional estimation costs.
- Large emission alphabets use a cycling hidden chain and several independent unknown emission laws. The unknown phase costs at most \(\log k\) information.
- The large hidden-state, binary-emission case constructs a high-dimensional doubly stochastic transition family, then uses estimation from block moments to lower-bound the information conveyed by observations. Tensor conditioning, random emission separation, mixing induced by the constructed perturbation, and a sufficiently large polynomial sample regime belong to this lower-bound proof. They are not assumptions imposed on every HMM in the upper-bound class.

These are source proof arguments read in full. Imported robust tensor-decomposition results and every numerical exponent in the chain of perturbation estimates were not independently re-proved. This note therefore does not certify the complete lower-bound proof.

### 7.2 Lemma A.1 loses a success-probability coefficient

The source assumes a continuous \(U\in[0,t]^d\), a Markov chain \(U\to X\to\widehat U\), and
\[
\Pr(\|U-\widehat U\|_2^2\le d\epsilon^2)\ge0.99.
\]
Its printed exact lower bound on \(I(U:X)\) drops the good-event probability multiplying a differential entropy. That entropy can be negative, so this deletion is not valid.

An exact counterexample uses \(d=t=1\), \(U\) uniform on \([0,1]\), an independent Bernoulli success indicator of probability \(0.99\), and \(M\) equal bins. On success, \(X\) reveals the bin of \(U\) and the estimator returns its center. On failure, \(X\) is an erasure and the estimator returns 2. With \(\epsilon=1/(2M)\), success has probability exactly \(0.99\) and
\[
I(U:X)=0.99\log M.
\]
The source's bound would instead require
\[
I(U:X)\ge\log M-\tfrac12\log(2\pi e).
\]
Taking \(M=2^{256}\) contradicts it, because \(2.56\log2>\frac12\log(2\pi e)\).

Writing \(p=\Pr(\|U-\widehat U\|_2^2\le d\epsilon^2)\), the valid conditional-entropy calculation is
\[
h(U\mid\widehat U)
\le h_2(p)+\frac{pd}{2}\log(2\pi e\epsilon^2)+(1-p)d\log t,
\]
and therefore
\[
\boxed{
I(U:X)\ge
h(U)+pd\log\frac1{\epsilon\sqrt{2\pi e}}
-(1-p)d\log t-h_2(p).
}
\tag{C}
\]
This follows by retaining the success probability, bounding error entropy by its second moment, and bounding failure entropy by the support volume. With \(p\ge0.99\), a positive leading constant may still yield the intended \(\Omega(k^2\log n)\) order when all other premises are established. The exact lemma is refuted, not every consequence automatically.

Here \(h_2(p)=-p\log p-(1-p)\log(1-p)\), with \(0\log0=0\), is binary entropy. All logarithms in this note are natural.

### 7.3 The first printed lower-bound branch needs a nondegenerate-state condition

The HMM definition on p2 permits \(k,\ell\in\mathbb N\). The first lower-bound branch of Theorem 1.1 prints only \(\ell\ge k,\ n\ge k\ell\), while the second explicitly requires \(k,\ell\ge2\).

For \(k=1,\ell=2\), the class is iid Bernoulli. The add-one categorical predictor has, for any iid alphabet law \(p\),
\[
\mathbb E_p D_{\rm KL}\left(p\middle\Vert
\frac{N_i+1}{n+\ell}\right)
\le \log\frac{n+\ell}{n+1}
\le\frac{\ell-1}{n+1}.
\tag{D}
\]
Here the fraction denotes the full predicted vector. A direct proof applies Jensen to each log term and uses
\[
\mathbb E\frac1{N_i+1}
=\frac{1-(1-p_i)^{n+1}}{(n+1)p_i}
\]
for positive \(p_i\). Zero-probability symbols contribute zero to KL.

At \(k=1,\ell=2\), (D) is \(O(1/n)\), whereas the printed first lower branch would be \(\Omega(\log n/n)\). Thus that literal boundary is false. Restricting the lower-rate statement to the intended nondegenerate state regime removes this particular counterexample. This is separate from the Proposition 3.2 endpoint issue and does not refute the \(k,\ell\ge2\) main asymptotic statement.

## 8. Renewal processes and the origin hazard

The renewal model has iid positive-integer interarrival times with law \(\mu\) and finite mean \(m(\mu)\). Stationarity requires a residual initial waiting time with distribution
\[
\Pr(T_0=t)=\frac{\Pr_\mu(T_1\ge t)}{m(\mu)},\qquad t\ge1.
\]
A countdown hidden state represents the process with infinitely many states. Truncating the relevant countdown beyond the observed horizon bounds the memory-information term by \(O(\log n/n)\). The source combines this with the cited renewal redundancy order \(\Theta(\sqrt n)\) to obtain the upper rate \(O(n^{-1/2})\).

Appendix E uses a prior over supports of size proportional to \(\sqrt n\), each split between two ranges. On a constant-probability event, the last renewal is recent, few distinct interarrival values have been seen, and the next candidate gap is unobserved. Posterior uncertainty about whether that gap belongs to the support creates the stated \(\Omega(n^{-1/2})\) prediction cost. The full argument was read, including its posterior likelihood simplification. That simplification and the historical redundancy proof were not independently certified.

Two elementary formulas require care:

1. **No renewal observed yet.** Equation (5) says to measure elapsed time from the last renewal or from the origin, then use the ordinary \(\mu\) hazard. The origin branch is wrong for a stationary residual initialization. Take \(\mu(1)=\mu(3)=1/2\). Then \(m(\mu)=2\) and \(T_0\) has masses \(1/2,1/4,1/4\). Consequently,
   \[
   \Pr(X_2=1\mid X_1=0)=\Pr(T_0=2\mid T_0>1)=1/2,
   \]
   while the printed ordinary hazard at elapsed time 1 is \(\mu(2)/\Pr_\mu(T_1>1)=0\). Before any observed renewal, the correct hazard is \(\Pr(T_0=n+1\mid T_0>n)\). After an actual observed renewal, the ordinary interarrival hazard is correct.
2. **Countdown stationary law.** Equation (35), p36, prints \(\sum_{j>i}\mu(j)/m(\mu)\) on positive integers. It must use \(j\ge i\) for the stated countdown convention. The strict-tail version has total mass \(1-1/m(\mu)\), rather than 1.

These checks refute the specified formulas. They do not refute the stated renewal minimax rate or the lower-bound argument restricted to events with an actual observed renewal.

## 9. Computational hardness is conditional and range-sensitive

### 9.1 The two assumptions

Appendix D.3 gives distinct hypotheses. They should not be collapsed into P versus NP or generic difficulty of HMM learning.

| Branch | Explicit assumption | Printed prediction conclusion |
|---|---|---|
| LPN, Conjecture D.2 | Random secret in \(\mathbb F_2^r\), uniform random inputs, noise \(0.05\). Distinguishing noisy parity from a fair label with success \(2/3\) requires \(2^{\Omega(r/\log r)}\) time. | For \(k\ge\log^{1+\varepsilon}n,\ell\ge2\), no efficient predictor with error \(o(\log k/(\log n\log\log n))\). |
| Planted CSP, Conjecture D.3 | Fixed clause width exceeding complexity \(r\), \(N\) variables, fixed noise in \((0,1)\). Polynomial-time planted-versus-uniform detection with success \(2/3\) needs \(\widetilde\Omega(N^{r/2})\) clauses. | For every fixed \(\alpha>0\), some constant \(k_\alpha\) makes \(k\ge k_\alpha,\ell\ge n^\alpha\) incompatible with efficient \(o(1)\) error. |

D.4 states existence of a hard distribution over HMMs. It concerns risk averaged over that prior and the observed path, hence a worst-model obstruction. It does not say every HMM is hard or provide a per-history KL lower bound. The source does not fully specify internal random coins or a bit-level computational model.

The [Sharan et al. primary source](https://theory.stanford.edu/~valiant/papers/Pred_Mem.pdf), p8, defines CSP complexity by support of an \((r-1)\)-wise uniform satisfying-assignment distribution, with no \(r\)-wise one. Its conjecture explicitly includes randomized polynomial-time algorithms. Its Theorem 2, p4, allows runtime \(f(K,\epsilon)\ell^{g(K,\epsilon)}\) and requires \(\ell^{\Omega(\log K/\epsilon)}\) observations for the stated average prediction error. Fixed \(\alpha\) permits a sufficiently large constant \(K\), but the 2024 paper gives a reduction sketch rather than an explicit \(k_\alpha\) and complete transfer constants.

The historical source's empirical-window positive theorem controls average \(\ell_1\) error at a randomly selected time, with an infinite-past comparator. The present terminal KL and finite-history comparator are different. Appendix A.1 and the hardness footnote acknowledge this distinction.

### 9.2 Revealing the initial state has a quantified cost

For a fixed model, auxiliary variable \(U\), and the same predictor \(Q\) that ignores \(U\), a direct KL chain-rule identity gives
\[
\mathbb E D_{\rm KL}
\bigl(P_\theta(X_{n+1}\mid X^n,U)\Vert Q(X_{n+1}\mid X^n)\bigr)
=R_\theta(Q)+I_\theta(U:X_{n+1}\mid X^n).
\]
This fixed-algorithm identity is useful when passing computational hardness through a side-information experiment. One must retain the information charge when the true oracle also sees \(U\).

For \(U=Z_1\), the source's stationary hidden-state argument gives
\[
I_\theta(Z_1:X_{n+1}\mid X^n)\le\log k/n.
\]
Thus initial-state revelation is asymptotically negligible in the intended hardness regimes, but the two risks are not literally identical. Lemma A.2 expresses the corresponding inequality after taking unrestricted prediction infima.

### 9.3 Exact limits of the printed LPN statement

The p35 construction uses
\[
r=C\log n\log\log n,\qquad
s=\left\lfloor\log_2(k/r)\right\rfloor-2.
\]
It cycles through \(r\) input positions and \(s\) noisy-parity positions. The stationary probability that the prediction endpoint lies in a parity position is \(s/(r+s)\).

Three source-level qualifications are material:

- **Unrestricted large \(k\) is impossible.** For \(\ell=2\), the uniform predictor always has KL risk at most \(\log2\). If \(\log k/(\log n\log\log n)\to\infty\), that constant is already little-\(o\) of the printed target. D.4 therefore cannot hold over its entire literal range without a restriction or a saturated expression. The construction's fraction \(s/(r+s)\) is naturally bounded. This check does not contradict the intended polynomial-\(k\) regime.
- **The state count has a wrong exponent.** Labels \((i,b_0,\ldots,b_s)\) give \((r+s)2^{s+1}\) states, while p35 prints \((r+s)2^{r+1}\). A bound by \(r2^{s+2}\) also needs \(s\le r\), exposing the same range issue.
- **The polynomial-degree quantifiers are not fully explained.** The source defines a large constant \(C\), then its last sentence refers to choosing the growth of an undefined \(\omega\). Fixed \(C\) supplies a hardness exponent of order \(C\) in \(n\). Uniform exclusion of all polynomial degrees requires an explicit account of how \(C\), the algorithm and the hard prior depend on each other. The sketch does not provide that account.

Remark D.5 explicitly leaves efficient \(o(1)\) risk open for polynomially large \(k\) and binary emissions. The first branch must not be cited as a constant-risk barrier in that regime.

## 10. What can be reused

The directly reusable tools are the stationary suffix-code conversion, the finite hidden-separator information charge, the all-sample row-count bound (A), the prediction consequence (B), and the corrected estimation-to-information inequality (C). Their assumptions and quantities are explicit.

The paper separates statistical prediction from parameter identification and computationally efficient prediction. Its results do not establish autonomous formation of an FP state space, recursive finite-state implementation, a learnable encoder, architectural expressivity, or optimization convergence. No FP theorem transfer is proposed in this note, and no FP core file was changed.

## 11. Verification record

Full official-text reading was personal. Bounded assisting readers checked the row-count correction, the erasure example, the renewal-origin example and the computational-hypothesis interfaces. The displayed independent deductions were also checked by the main reader. No exhaustive search, experimental reproduction, proof assistant, full tensor-proof audit or theorem-wide certification was performed.

Exact negative findings concern Proposition 3.2's uniform endpoint range, Lemma A.1's printed inequality, the first lower-bound branch at \(k=1\), the renewal origin/normalization formulas and D.4's unrestricted huge-\(k\) claim. The notes expressly retain the stricter nondegenerate main statistical regimes and distinguish source proof sketches from independently established corrections.

The scoped 2018 dependency is a necessary theorem interface, not a restarted historical reading queue. No new mandatory Astra request was pending at this reading boundary. All requests through 53c10ef remain completed by their recorded owners.
