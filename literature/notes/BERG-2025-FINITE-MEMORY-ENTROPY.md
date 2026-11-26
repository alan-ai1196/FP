# Berg–Ordentlich–Shayevitz 2025: a finite-state expectation operator

## Source, edition and actual coverage

**Tomer Berg, Or Ordentlich and Ofer Shayevitz, _Memory Complexity of Estimating Entropy and Mutual Information_, arXiv:2406.06312v3, revised 23 April 2025.** [Version history](https://arxiv.org/abs/2406.06312v3) · [PDF](https://arxiv.org/pdf/2406.06312v3) · [TeX](https://arxiv.org/src/2406.06312v3). The primary IEEE record authenticates publication in **IEEE Transactions on Information Theory 71(5), 3334–3349, May 2025**, first online 4 March, DOI [10.1109/TIT.2025.3547871](https://ieeexplore.ieee.org/abstract/document/10909664).

Pro-A completed the **27-page author v3** on 26 November 2026, Shanghai. Main-reader coverage is the complete active TeX, Sections I–VII, Appendices A–C, all statements and proofs, four active algorithms, both figures, three active scientific footnotes, front matter, acknowledgements and all 37 printed references. Commented-out source is not counted as additional published content. PDF pages 1, 2, 5–8, 12, 17, 20 and 26 were visually inspected, including both original figures. The separate 16-page journal layout was not retrieved or compared. Earlier arXiv editions remain independently unread. No AI-use disclosure was found in the inspected manuscript, which does not establish actual use.

A support reader checked the finite-state averaging chain, renewal interface and the short deductions below. The main reader assessed those checks and read the complete paper personally. No simulation, implementation, exhaustive search, formal replay or complete dependency audit was performed.

One historical dependency was opened because its exact asymptotic statement is needed below: **Philippe Flajolet, _Approximate Counting: A Detailed Analysis_, BIT 25 (1985), 113–134**, [primary author archive](https://algo.inria.fr/flajolet/Publications/Flajolet85c.pdf). Coverage is the counter convention, Proposition 0 and Theorem 1 on printed pages 114–115, with page 115 visually inspected. Its Mellin-analysis proof and the rest of its 22 pages were not read. It receives scoped coverage only.

## 1. The constructive idea and its resource model

The paper decomposes entropy estimation into two operations that can each be implemented by a small, time-homogeneous stochastic machine:

1. Use a random approximate-counting clock and an occurrence counter to obtain a bounded, nearly unbiased estimate of a log probability.
2. Convert that bounded statistic to a Bernoulli observation and average it using a birth-and-death chain whose stationary distribution is exactly binomial.

The second operation is a reusable finite-state expectation operator. It avoids storing both a growing exact sample sum and a growing exact time index. The paper attributes its basic bias-estimation machine to earlier work by Samaniego. The deductions here explain the mechanism and assemble consequences, without a novelty claim.

The observations are iid \(X_t\sim p\) on a known alphabet \([n]\). A machine has \(S\) persistent states, a fixed initial state, a possibly randomized but **time-invariant** transition rule, and a fixed readout in \([0,\log_2 n]\). The risk is exactly

\[
\sup_{p\in\Delta_n}\limsup_{t\to\infty}
\Pr_p\{|\widehat H(M_t)-H(p)|>\varepsilon\}.
\]

The supremum is outside the limit superior. This is not a uniform finite-horizon convergence assertion. State count, or its logarithm in bits, prices the persistent machine state. It does not price the description of the transition kernel, its random-coin precision, fixed readout constants, offline precomputation or arithmetic hardware. The construction is fixed in advance from \(n\) and accuracy parameters. It does not learn a transition program or discover a state alphabet from experience.

The source's Theorem 1 gives, for \(c>1\), \(\beta>0\), \(0<\delta<1\),

\[
S^*(n,10^{-5}+\beta+\psi_c(n),\delta)
\le n\left\{\frac{8(c\log_2 n+2)^4}{\beta^2\delta}
+4(c\log_2 n+2)^2\right\},
\]

with an explicit vanishing \(\psi_c\) built from negative moments of the random clock, a Morris-counter remainder and truncation error. The printed expression is

\[
\begin{aligned}
\psi_c(n)&=(e+1)n^{-(c-1)+v_n(1)}
+\min\{1,2(e+1)10^8n^{-(c-1)/2+v_n(1/2)}\}\\
&\quad+n^{-c}\frac{100(c\log_2n+2)}{(1-\tfrac12n^{-c})^2},\\
v_n(\alpha)&=\sqrt{\frac{2c\alpha^3}{\log_2 n}}
+\frac{\alpha}{\log_2n}.
\end{aligned}
\]

For fixed accuracy above the counter's small periodic bias, the leading memory cost is \(\log_2n+O(\log\log n)\) bits. This is an asymptotic construction, not a claim that the explicit numerical bound is tight for practical alphabets. Section 6 below gives a separately derived version with simpler bias terms and logarithmic confidence cost. It does not inherit every explicit constant in the source theorem.

## 2. An exact binomial averaging machine

Let \(m\ge1\), with persistent state \(J\in\{0,\ldots,m\}\). On a fresh observation \(Y\sim\operatorname{Bern}(\theta)\), draw independently

\[
B\mid J\sim\operatorname{Bern}(J/m),\qquad J'=J+Y-B.
\]

The two nontrivial transition probabilities are

\[
P(j,j+1)=\theta\frac{m-j}{m},\qquad
P(j,j-1)=(1-\theta)\frac j m.
\]

Detailed balance gives the exact stationary law

\[
\pi(j)=\binom mj\theta^j(1-\theta)^{m-j}.
\]

Thus \(J/m\) is stationary-unbiased for \(\theta\), with variance \(\theta(1-\theta)/m\). For \(0<\theta<1\), the chain is irreducible and aperiodic. At the endpoints it converges to the corresponding absorbing state.

### Virtual resampling explains both storage and mixing

Imagine an array of \(m\) bits. At each step choose one coordinate uniformly and replace it by a fresh Bernoulli observation. The number of ones follows exactly the chain above. The actual machine stores only the count, not the array. The virtual representation is a proof device.

Couple two arrays using the same coordinate choices and new bits. Once every coordinate has been overwritten they agree. After a fixed number \(k\) of completed updates,

\[
\|\mathcal L(J_k)-\pi\|_{\rm TV}
\le m(1-1/m)^k\le m e^{-k/m}.
\]

The first expression is interpreted directly at \(m=1\). Also,

\[
\mathbb E[J'/m\mid J,Y]
=(1-1/m)J/m+Y/m.
\]

This is a randomized implementation of exponential averaging on a finite grid. It is not an exact running empirical mean, and it does not become an arbitrary-precision real accumulator by changing the interpretation of a state.

### A general bounded-statistic interface

For iid scores \(Z\in[A,A+R]\), draw

\[
Y\mid Z\sim\operatorname{Bern}((Z-A)/R).
\]

Then \(\theta=(\mathbb EZ-A)/R\), and the readout \(A+RJ/m\) estimates \(\mathbb EZ\). Its stationary tail satisfies

\[
\Pr\{|A+RJ/m-\mathbb EZ|>\beta\}
\le2\exp(-2m\beta^2/R^2).
\tag{1}
\]

At a fixed embedded update index \(k\), add \(m e^{-k/m}\) to the right-hand side. The source uses a second-moment confidence bound. Equation (1), obtained directly from its exact binomial stationary law, replaces the resulting \(1/\delta\) averaging-state cost by \(\ln(1/\delta)\). Independence of fresh scores from the current averaging state is essential.

## 3. The random clock and anchored log-count statistic

Assume \(n\ge2\) and \(c>1\), and set

\[
B=\lceil\log_2\lceil n^c\rceil\rceil,\qquad M=B+1.
\]

A Morris counter starts at 1. Each increment request at state \(s\) increases it to \(s+1\) with probability \(2^{-s}\). Stop the clock when it first reaches \(M\). The number of input samples consumed is

\[
N=\sum_{k=1}^{B}\tau_k,\qquad
\tau_k\stackrel{\rm independent}{\sim}\operatorname{Geo}(2^{-k}),
\qquad \mathbb EN=2^M-2,
\tag{2}
\]

where geometric variables have support \(\{1,2,\ldots\}\).

Choose the first sample of an attempt as anchor \(x\), and include that same sample in both counters. Conditional on \(N,x\), the number of anchor occurrences is

\[
N_x\sim1+\operatorname{Bin}(N-1,p_x).
\tag{3}
\]

This guarantees \(N_x\ge1\). An unbounded occurrence Morris counter after these increments is denoted \(C_\infty=C_{N_x}\). Abort and restart an attempt if this counter reaches \(2M\). Accepted attempts have score

\[
C_{\rm acc}\ \overset d=\ C_\infty\mid\{C_\infty<2M\}.
\]

Repeated attempts use fresh iid data and independent private coins. Thus accepted scores are iid even though an accepted score can be correlated with the duration of its own attempt.

Write \(\eta=\mathbb E\log_2N\) and

\[
\mu=\frac\gamma{\ln2}+\frac12-
\sum_{i\ge1}\frac1{2^i-1}\simeq-0.27395.
\]

Generate \(Y\mid C_{\rm acc}\sim\operatorname{Bern}(1-C_{\rm acc}/(2M))\). Its mean is \(\theta=1-\mathbb EC_{\rm acc}/(2M)\). The averaging readout is

\[
\widetilde H=2M(J/m-a),\qquad
a=1-\frac{\mu+\eta}{2M}.
\tag{4}
\]

Its stationary center is \(\mu+\eta-\mathbb EC_{\rm acc}\), which approximates entropy. Clip the final output to \([0,\log_2n]\), as the formal model requires. Clipping cannot increase absolute error and uses no additional state.

### A complete phase convention with the stated state budget

The literal startup branch of Algorithms 3 and 4 resets at \(C_N=1\) without incrementing that clock, so it can remain in its startup branch forever. The prose construction can be implemented without adding a phase bit:

- Reserve the otherwise transient value \(C_N=M\) as the pending-start marker between samples.
- On the next sample, store it as \(x\), reset both counters to 1, and increment both counters on that same anchor sample.
- While active, increment the clock on every sample and the occurrence counter exactly on matches to \(x\).
- If the occurrence counter reaches \(2M\), discard the attempt and set the pending marker. Otherwise, when the clock reaches \(M\), generate the Bernoulli score, update \(J\), and set the pending marker.

If both thresholds are reached on one sample, rejection has priority. Active clock values between samples are \(1,\ldots,M-1\). No separate stored time index is used. The state tuple \((x,C_N,C_x,J)\) has at most

\[
S\le n\,M\,(2M)(m+1)=2nM^2(m+1)
\tag{5}
\]

values. Algorithm 3 also prints \(M\) in the denominator of its offset, whereas the derivation and the Bernoulli scaling require \(2M\), as in (4). These are local transcription/phase repairs to make the constructive mechanism executable, not a claim that a different estimator was empirically tested.

## 4. Two short estimates for this construction

The following deductions are independent source-grounded calculations. They avoid unnecessary slack in the clock and rejection estimates.

### 4.1 The last two clock stages control negative moments

Since \(B\ge2\), let \(q=2^{-(B-1)}\). The last two waiting times are independent geometric variables with parameters \(q\) and \(q/2\). Consequently \(N\) stochastically dominates \(T=G+G'\) for independent \(G,G'\sim\operatorname{Geo}(q)\). For \(t\ge2\),

\[
\Pr(T=t)=(t-1)q^2(1-q)^{t-2},\qquad
\mathbb E\frac1{T-1}=q.
\]

Monotonicity and concavity therefore give

\[
\mathbb E N^{-1}\le q\le2n^{-c},\qquad
\boxed{\mathbb E N^{-\alpha}\le2^\alpha n^{-c\alpha}}
\quad(0<\alpha\le1).
\tag{6}
\]

Only two phases are needed. The factor with \(\sqrt{\log n}\) in the source's Chernoff-based negative-moment estimate is unnecessary for this range of moments.

### 4.2 Integrating the occurrence-counter tail controls rejection

Conditioned on \(N\), the occurrence counter receives at most \(N\) increment requests. For \(k\ge2\), reaching \(k\) requires a successful transition out of \(k-1\). A union bound over those requests yields

\[
\Pr(C_\infty\ge k\mid N)\le N2^{-(k-1)}.
\]

Put \(K=2M\), \(r=\Pr(C_\infty\ge K)\). Equation (2) implies

\[
r\le \mathbb EN\,2^{-(K-1)}
<2^{1-M}\le n^{-c}.
\]

Using the integer tail-sum identity,

\[
\begin{aligned}
T&=\mathbb E[C_\infty\mathbf1_{C_\infty\ge K}]\\
&=K\Pr(C_\infty\ge K)+\sum_{k>K}\Pr(C_\infty\ge k)\\
&\le(K+1)\mathbb EN\,2^{-(K-1)}
\le(2M+1)n^{-c}.
\end{aligned}
\]

The conditional-mean identity is

\[
0\le\mathbb EC_\infty-\mathbb EC_{\rm acc}
=T-r\mathbb EC_{\rm acc}\le T.
\tag{7}
\]

This directly controls the bias caused by retries. It needs neither a maximum over a block of tail terms nor an additional \((1-r)^{-1}\) factor.

## 5. A source-supported entropy bias bound

Flajolet's original Theorem 1 states the asymptotic expansion

\[
\mathbb EC_\ell=\log_2\ell+\mu+g(\log_2\ell)+r_\ell,
\qquad |g|<a_0=10^{-5},\quad r_\ell=O(\ell^{-0.98}).
\]

Therefore there exists a finite universal constant \(K_0\) such that

\[
|r_\ell|\le K_0\ell^{-1/2}\qquad\text{for every integer }\ell\ge1.
\tag{8}
\]

For sufficiently large \(\ell\) this follows from the asymptotic bound. Absorb the finitely many remaining values into \(K_0\). This deduction establishes existence, not a useful explicit numerical value of \(K_0\). In particular, it does not certify the explicit finite remainder printed as Theorem 4 in the present paper.

For (3), the exact binomial identity is

\[
\mathbb E[1/N_x\mid N,x]
=\frac{1-(1-p_x)^N}{Np_x}\le\frac1{Np_x}.
\tag{9}
\]

Only \(p_x>0\) anchors occur. Jensen's inequality applied to the reciprocal and then to the ordinary expectation gives

\[
0\le \mathbb E\left[\left.\log_2\frac{N_x}{Np_x}\right|N,x\right]
\le \frac{1-p_x}{Np_x\ln2}.
\]

Average over the size-biased anchor \(x\sim p\). By (6),

\[
0\le \mathbb E\log_2N_x-\eta+H(p)
\le\frac{2(n-1)}{\ln2}n^{-c}.
\tag{10}
\]

The logarithm base matters: \(\log_2(1+u)\le u/\ln2\), not generally \(u\). Next, (9), Jensen and Cauchy–Schwarz give

\[
\begin{aligned}
\mathbb EN_x^{-1/2}
&\le \left(\sum_x\sqrt{p_x}\right)\mathbb EN^{-1/2}\\
&\le\sqrt{2n}\,n^{-c/2}.
\end{aligned}
\tag{11}
\]

Combining (7)–(11), the center in (4) satisfies the uniform bound

\[
\boxed{
\left|\mu+\eta-\mathbb EC_{\rm acc}-H(p)\right|
\le b_c(n)
}
\]

with

\[
b_c(n)=10^{-5}
+\frac{2(n-1)}{\ln2}n^{-c}
+\sqrt2K_0 n^{-(c-1)/2}
+(2M+1)n^{-c}.
\tag{12}
\]

This proof follows the paper's architecture but uses the authenticated asymptotic dependency, a two-phase negative-moment estimate and a direct tail sum. The periodic error is a limitation of this particular log-counter statistic. It is not a universal lower bound on finite-state entropy estimation.

## 6. An assembled stationary guarantee and its time boundary

Take

\[
m=\left\lceil\frac{2M^2}{\beta^2}\ln\frac2\delta\right\rceil.
\]

Equations (1), (4), (5) and (12) give a fixed, time-homogeneous construction with

\[
\boxed{
S\le\frac{4nM^4}{\beta^2}\ln\frac2\delta+4nM^2
}
\tag{13}
\]

and asymptotic error probability at most \(\delta\) at tolerance \(\beta+b_c(n)\). If the installed value of \(\eta\) has deterministic error at most \(\zeta\), add \(\zeta\) to the tolerance. Any random failure probability of offline estimation must be accounted for separately. Equation (13) is an independently assembled corollary, not a claim of priority and not a numerical replacement for every constant in the paper.

### Why the raw-time stationary marginal is still binomial

Between accepted rounds, the averaging state is held fixed. The duration \(R\) until the next accepted round depends on fresh observations and counter coins, but not on the current averaging state. Attempts have finite mean length by (2), and acceptance probability is at least \(1-n^{-c}>0\), so \(\mathbb ER<\infty\).

At accepted boundaries, the averaging chain has invariant distribution \(\pi\). The occupation weight of state \(j\) in raw sample time is proportional to

\[
\pi(j)\mathbb E[R\mid J=j]=\pi(j)\mathbb ER.
\]

Thus its raw-time stationary marginal is also \(\pi\). Correlation between a cycle's own duration and its eventual Bernoulli mark does not change this argument: the state held during that cycle was fixed before the fresh cycle began. The repaired finite machine has a recurrent regenerative class and positive self-loop probabilities during counting, yielding convergence to this marginal for each fixed \(p\). The bound (12) is uniform in \(p\), so it supports the risk ordering stated in Section 1.

### A fixed number of completed rounds is not a fixed raw horizon

The fixed-index estimate from Section 2 gives

\[
\Pr\{|\widehat H_k-H(p)|>\beta+b_c(n)\}
\le2e^{-m\beta^2/(2M^2)}+me^{-k/m}
\]

after exactly \(k\) accepted rounds. At a fixed raw horizon \(L\), the number of completed rounds \(K(L)\) is correlated with their marks. One cannot simply condition the fixed-step mixing bound on \(K(L)\ge k\). The paper's finite-sample argument requires an additional joint renewal/mixing justification at this interface. This note neither certifies the printed raw-sample bound nor proves that such a bound is impossible. The stationary result above does not depend on that missing finite-time step.

## 7. The rest of the source and the scope of its conclusions

### Entropy lower bounds

The output-cover argument in Theorem 2 gives \(S\ge\log_2n/(2\varepsilon)\): \(S\) intervals of radius \(\varepsilon\) must cover all attainable entropies in \([0,\log_2n]\). Its second bound,

\[
S\ge n(1-2\sqrt{\varepsilon\ln2}),
\qquad \varepsilon<1/(4\ln2),
\]

reduces entropy estimation to uniformity testing using \(\log_2n-H(p)=D_{\rm KL}(p\|u_n)\). The imported testing interface requires a nontrivial confidence level, in particular \(\delta<1/2\), which is not stated in the displayed theorem. The historical testing paper was not independently audited. These lower bounds concern the supplied finite-state estimator model, not arbitrary programming languages or learned representations.

### Mutual information

Section VII shares one anchor pair and one clock across three occurrence counters for \(X\), \(Y\) and \((X,Y)\), then uses one averaging chain for their signed combination. This joint construction avoids separately multiplying three complete estimator-state spaces. Theorem 3 reports

\[
S^*_{\rm MI}\le nm\left\{
\frac{288(c\log_2(nm)+2)^6}{\beta^2\delta}
+16(c\log_2(nm)+2)^4\right\}.
\]

Its Bernoulli conversion uses a score interval of width \(6M\), so the modular averaging improvement in (1) applies to an iid accepted-score implementation. That observation alone does not certify the complete source MI bias analysis.

The displayed asymptotic bias in Theorem 3 uses the **minimum** of two marginal error expressions, whereas the supplied comparison bounds their **maximum**. The latter does not imply the former. A sharper joint-clock analysis could potentially obtain a better rate, so this discrepancy is recorded as an unfilled proof step rather than a demonstrated impossibility. The stated lower order \(\Omega(nm/(\log^3n\log^3m))\) also has explicit joint growth conditions and a constant-confidence reduction. In the phase-reuse argument, a Bernoulli phase clock must advance on completed estimator updates, not on every raw sample. No independent complete MI theorem is claimed here.

### Explicit remainder and finite examples

The paper's Theorem 4 strengthens Flajolet's asymptotic remainder to a particular all-finite-size bound. At one increment the counter has expectation \(1.5\), but the printed remainder bound vanishes at \(\ell=1\), inconsistent with \(\mu\simeq-0.27395\) and the stated tiny periodic term. This is why (8) uses the original asymptotic theorem with an unspecified universal constant. The construction and scaling argument survive that distinction.

The reported numerical observation is a single uniform alphabet with \(n=1000\), \(c=1.5\), \(\beta=\delta=0.1\): after \(10^{11}\) samples the error is about \(0.15\), below a loose theoretical bound. The manuscript does not supply replicated trials or confidence intervals for this observation. It is illustrative evidence for that setting, not empirical establishment of minimax performance. It was not reproduced.

## 8. Reusable mathematical content and FP boundary

The strongest transferable mathematical tools are explicit and separable:

- A bounded random score can feed a finite-state averaging chain with an exact binomial stationary law, a direct tail bound and a virtual-coordinate coupling proof.
- Random approximate clocks can replace a growing exact time register. Their last two phases already control the negative moments needed by this log-count estimator.
- Anchor inclusion changes a zero-prone binomial count into \(1+\operatorname{Bin}(N-1,p_x)\), producing an exact reciprocal identity and a controllable log bias.
- State-independent holding times preserve the embedded chain's stationary marginal, while fixed raw-time guarantees still require a separate convergence argument.

These are source-grounded constructions for iid statistical estimation with prescribed states and transitions. Applying them to a learned FP mechanism would require an identified bounded score, an actual observation process satisfying the independence or replacement assumptions, all persistent counters included in the state budget, and a justified temporal interface. No such mapping is asserted here. This note changes no FP definition, architecture, implementation, experiment or research priority.
