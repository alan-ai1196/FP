# Learning Finite-Memory Binary Sources

## Source, edition and actual coverage

**Maciej Skórski**, University of Luxembourg. **arXiv 2610.40845v1**, submitted October 29, 2026, 18:27:06 UTC. The authenticated edition has 36 pages. No peer-reviewed acceptance or later edition was established. The source filename main-alt2027.tex and its JMLR class do not establish a conference acceptance. [Versioned record](https://arxiv.org/abs/2610.40845v1) · [Original PDF](https://arxiv.org/pdf/2610.40845v1) · [Submitted source](https://arxiv.org/src/2610.40845v1)

**Fully read by the main reader on November 26, 2026, Shanghai.** Actual coverage is all published text and mathematics, §§1–4.7, conclusions and AI disclosure, Appendix A.1–A.5 and Appendix B.1–B.5, Algorithm 1, all three tables and all 21 printed references onpp13–14. There are no figures or active body footnotes. The complete main TeX through its end-document at line2124 was read in continuous sections. Its30-entry bibliography was also read. Nine unused bibliography records and the text after end-document are not additional published sections.

Original PDF pages5,6,8,10,11,12,16,19,20,21,24,25,27,28,35,36 were visually checked. This includes every table, the algorithm and the displays used in the quantitative checks below. Source agents prepared files and performed two narrow independent checks. They did not replace the main reader's complete reading.

The submitted source package contains the main file, references.bib, jmlr.cls and a README. No active author input or figure dependency was missing. The paper'sp12 disclosure says Claude was used for editorial polishing, related-work search and numerical-simulation coding, with author review and responsibility. This is an author disclosure, not independent evidence about how the proofs were obtained.

The paper links [learning-binary-sources](https://github.com/maciejskorski/learning-binary-sources) for code and numerical experiments. At the checked default-branch commit [7963e2f930830999e4fec1ee42f824c4b070c49f](https://github.com/maciejskorski/learning-binary-sources/tree/7963e2f930830999e4fec1ee42f824c4b070c49f), its complete recursive tree contains only a 94-byte README. No program, experimental data, Wolfram certificate or extra proof file was present. Releases were empty. Tags were not authenticated because that endpoint was unavailable. The README does not identify arXiv v1, so a precise paper-to-commit correspondence is unestablished. The supplementary code claimed in the paper was not obtained.

## 1. Statistical question and supplied structure

The unknown source emits one binary symbol at a time. Its next-bit distribution depends on the **last prescribed \(d\) observed bits**. For

\[
a=\tfrac12+\epsilon,\qquad b=\tfrac12-\epsilon,
\qquad 0\le\epsilon<\tfrac12,
\]

the class \(\mathcal C_{\epsilon,d}\) consists of kernels satisfying

\[
b\le p(1\mid w)\le a
\quad\text{for every }w\in\{0,1\}^d.
\]

Both outcome probabilities therefore lie in \([b,a]\). The estimator observes an initial window and \(n\) new bits. The target is a simultaneous, multiplicative guarantee

\[
\Pr\!\left[
|\widehat p(v\mid w)-p(v\mid w)|
\le\gamma p(v\mid w)
\quad\forall w,\ v\in\{0,1\}
\right]\ge1-\delta.
\]

The minimax sample size requires success for every source in the class and every initial window. This is uniform estimation of all \(2^d\) transition rows from one trajectory. It is stronger than average next-symbol KL risk and different from learning a compact latent state representation. The order and shift transition structure are supplied. There is no hidden-state discovery, unknown-order selection or general token-action learning theorem. [§§3.2–3.3,p. 5](https://arxiv.org/pdf/2610.40845v1#page=5)

The observable state is \(W_t=(X_{t-d+1},\ldots,X_t)\). Its transition removes the oldest symbol and appends the new one. A length-\(d\) path ending at \(w\) is unique from every initial window, so

\[
P^d(u,w)=
\prod_{j=1}^d
p(w_j\mid u_j\cdots u_d w_1\cdots w_{j-1}),
\qquad
b^d\le P^d(u,w)\le a^d.
\]

The positive \(d\)-step kernel gives an irreducible aperiodic chain with a unique stationary distribution satisfying \(b^d\le\pi(w)\le a^d\). Kac's formula gives \(\mathbb E_w\tau_w^+=1/\pi(w)\). Hitting counts the first visit at time 0 if already at the target, while return time begins at1. The learning count \(N_w(n)\) includes times 0 through\(n-1\), each followed by an observed new bit. These conventions matter for the additive \(d\) and \(n-1\) terms below.

## 2. Main learning result and its parameter range

For fixed **\(0<\epsilon<3/10\)**, Theorems 12–13 give

\[
n^\star(\gamma,\delta)
\asymp_\epsilon
\frac{\ln(d+1)+\ln(1/\delta)}
{\gamma^2 b^d},
\]

when

\[
0<\gamma\le\min\{\epsilon/4,1/12\},
\qquad 0<\delta\le1/4.
\]

The constants in this equivalence can depend on \(\epsilon\). The statement is not uniform as \(\epsilon\downarrow0\) or \(\epsilon\uparrow3/10\). At \(\epsilon=0\), the class contains only the known fair source, so a zero-data estimator is possible. This degenerate endpoint is excluded from the matching minimax theorem. [§4.5,pp. 10–11](https://arxiv.org/pdf/2610.40845v1#page=10)

The estimator in Algorithm 1 simply collects the bits following visits to a requested window. It returns their empirical frequency, or\(1/2\) if there were no visits. It needs the trajectory and window definition, but not \(\epsilon\), \(\pi\), mixing time or hitting time.

Put

\[
m_\gamma=\frac{a}{b\gamma^2},\qquad
C(\epsilon)=\sup_{d\ge1}B_d(\epsilon).
\]

The actual sufficient condition is

\[
n\ge
\frac{8(m_\gamma+C(\epsilon))}{b^d}
\max\left\{
\ln\frac6\delta,\
\frac{b}{2\epsilon}(1+\ln d)
\right\}.
\]

For a single window, at every \(\epsilon<1/2\), the bound instead uses its mass and the finite-\(d\) constant:

\[
\Pr\{\text{relative error exceeds }\gamma
\text{ at }w\}
\le
4\exp\!\left[
-\frac{n\pi(w)}
{8(m_\gamma+B_d(\epsilon))}
\right].
\]

Thus the per-row theorem continues above the hitting threshold, but its constant can grow with \(d\). The lower bound holds for every \(0<\epsilon<1/2\), under the stated small-\(\gamma\) restriction, with the explicit absolute constant\(1/20\). The paper does **not** prove that the minimax learning rate changes at\(\epsilon=3/10\). That threshold is proved for normalized hitting times, and extending the matching learning upper bound beyond it is an open question.

The memoryless source \(p(1\mid w)=a\) has \(\pi_{\min}=b^d\) and mixing time exactly\(d\), using worst-start TV threshold\(1/4\). Perturbations of its rare rows supply the learning lower bound. Rapid loss of the initial window does not make every rare conditional probability easy to estimate. For fixed admissible parameters,

\[
\lim_{d\to\infty}\frac{\log_2 n^\star}{d}
=1+\log_2\frac1{1-2\epsilon}.
\]

This is a sample exponent for uniform kernel recovery. It is not a lower bound on the number of states needed for a specified predictive task.

## 3. Exact coin overlap and the hitting-time argument

### 3.1 Sharp \(d\)-step contraction

Define

\[
c_d(\epsilon)
=1-d_{\mathrm{TV}}
\bigl(\operatorname{Bern}(a)^{\otimes d},
\operatorname{Bern}(b)^{\otimes d}\bigr),
\qquad
\beta=2\sqrt{ab}.
\]

Theorem 3 proves parity \(c_{2m-1}=c_{2m}\), the exact binomial-tail/integral formula

\[
c_{2m}
=2\Pr\{\operatorname{Bin}(2m-1,b)\ge m\}
=
\frac{\int_{2\epsilon}^{1}(1-u^2)^{m-1}du}
{\int_0^1(1-u^2)^{m-1}du},
\]

and, with \(m=\lceil d/2\rceil\),

\[
\frac1{\sqrt\pi}
\frac{\beta^{2m}}{\sqrt{1+4m\epsilon^2}}
\le c_d(\epsilon)\le
\frac{\beta^{2m}}{\sqrt{1+4m\epsilon^2}}.
\]

Both absolute constants are optimal. The proof compares the derivative of the normalized beta tail with the derivative of its explicit approximation. A monotone derivative-ratio function yields the upper bound and a lower factor
\(\binom{2m}{m}4^{-m}\sqrt{m+1}\), decreasing to\(1/\sqrt\pi\). The parity argument observes that appending a bit to an odd-length likelihood ratio cannot reverse its sign. [Theorem 3,pp. 6–7 and Appendix A.2,pp. 15–17](https://arxiv.org/pdf/2610.40845v1#page=6)

For the Dobrushin coefficient,

\[
\delta(P^d)\le1-c_d(\epsilon)
\]

holds for every admissible shift chain and is attained by
\(p(1\mid w)=b+(a-b)w_1\), where \(w_1\) is the oldest bit. Starting from all ones and all zeros produces the two endpoint product laws over the next\(d\) symbols.

The proof establishes a stronger weighted-overlap inequality for any two depth-\(d\) binary laws whose conditional probabilities lie in the box. The reference overlap is concave and homogeneous in the two incoming masses. At each branch its minimum over the probability rectangle occurs at a corner. Opposite endpoint corners give the next coin-product overlap, while equal endpoints give the previous, larger overlap. This induction handles arbitrary allowed dependencies without replacing them by independent observations.

### 3.2 Occupancy oscillation controls hitting

For \(G_n(u,w)=\sum_{t<n}P^t(u,w)\) and column oscillation
\(\Omega_s(w)=\max_uP^s(u,w)-\min_uP^s(u,w)\), Theorem 5 gives

\[
|G_n(u,w)-n\pi(w)|
\le\operatorname{osc}G_n(\cdot,w),
\]

\[
\pi(w)\mathbb E_u\tau_w
=\lim_{n\to\infty}
\bigl(G_n(w,w)-G_n(u,w)\bigr).
\]

The second identity follows by stopping at the first target hit. Before that hit, no target occupancy is accumulated. The proof uses Fatou for infinite expected hitting times and dominated convergence plus
\(n\Pr(\tau_w\ge n)\to0\) in the finite-mean case. It does not assume stationarity of the initial state.

If \(\delta(P^L)<1\), the column oscillations contract every\(L\) steps. Keep the first block's cumulative oscillation intact and sum the remaining column spreads geometrically:

\[
\sup_n\operatorname{osc}G_n(\cdot,w)
\le
\max_{k\le L}\operatorname{osc}G_k(\cdot,w)
+\frac{L\,\Omega_L(w)}{1-\delta(P^L)}.
\]

For a shift chain set\(L=d\). A target can be reached by at most one path of length\(t\le d\), giving a return bound\(a^t\). After\(d\) steps every column value is in\([b^d,a^d]\). Consequently Theorem 7 obtains

\[
B_d(\epsilon)
=\frac{1-a^d}{1-a}
+\frac{d(a^d-b^d)}{c_d(\epsilon)},
\]

which bounds both finite-time occupancy error and \(\pi(w)\mathbb E_u\tau_w\). The tail is a polynomial factor times\((a/\beta)^d\), so it is uniformly bounded in\(d\) when\(a<\beta\), equivalent to\(\epsilon<3/10\). [§§4.2–4.3,pp. 7–8 and Appendix A.3,pp. 17–20](https://arxiv.org/pdf/2610.40845v1#page=7)

Theorem 18 states
\(C(\epsilon)\le(2/5)(3/10-\epsilon)^{-3/2}\).
Its final numerical-constant inequalities are attributed to Wolfram Resolve and a named certificate script. That script is absent from the obtained source package and current companion tree. The existence of the reported computational certification was not independently authenticated. The preceding explicit analytic envelope and the elementary asymptotic proof in Appendix B.4 can be read without that script.

### 3.3 A genuine threshold for normalized hitting

For odd\(d\), the majority chain chooses\(p(1\mid w)=a\) in the ones-majority region and\(b\) in the zeros-majority region. Bit-flip symmetry gives stationary mass\(1/2\) to each region. From the ones region, \(d\) consecutive ones occur with probability\(a^d\), so\(\pi(1^d)\ge a^d/2\).

Before escaping the zeros region from\(0^d\), the emitted bits are iid with one-probability\(b\). A union bound over windows controls the escape probability using
\(q_d=\Pr\{\operatorname{Bin}(d,b)\ge(d+1)/2\}\).
An upper bound on this binomial tail yields

\[
\pi(1^d)\mathbb E_{0^d}\tau_{1^d}
\ge
\frac{\sqrt{2\pi}\epsilon}{4\beta}
\sqrt d\left(\frac a\beta\right)^d.
\]

This diverges at and above\(3/10\), including the boundary where the exponential ratio is1. Together with the upper theorem,
\(\sup_{d,P,u,w}\pi(w)\mathbb E_u\tau_w<\infty\)
if and only if\(\epsilon<3/10\). [Theorem 8,p. 8 and Appendix A.3.3,pp. 20–21](https://arxiv.org/pdf/2610.40845v1#page=20)

For \(\Delta=3/10-\epsilon\downarrow0\), Appendix B.4 leaves a gap between the true worst-case lower growth\(\Delta^{-1/2}\) and upper growth\(\Delta^{-3/2}\). The explicit envelope\(C(\epsilon)=\sup_dB_d(\epsilon)\) does have exponent\(3/2\). Its growth is not established as necessary for the actual worst hitting time or for sample complexity.

## 4. Visits, majorization and the estimator's random sample count

Theorem 9 separates a repeated-visit cost from the first-hit delay. For
\(t_w=\max_y\mathbb E_y\tau_w\), the \(k\)-th visit satisfies, with probability at least\(1-\eta\),

\[
\tau_w^{(k)}
\le
1.3\,\frac{k-1}{\pi(w)}
+6.5\,t_w\ln\frac2\eta.
\]

The proof constructs an exponential moment for the hitting time at scale\(1/t_w\). Kac's formula then bounds the return-time moment using its mean\(1/\pi(w)\). Strong Markov independence of successive returns yields the displayed additive structure. It avoids multiplying the full precision cost by the hitting envelope.

The bits following successive visits to a fixed window are iid, but the number of observed visits can depend on those bits. Lemma 20 therefore proves a maximal Chernoff bound over **all visit counts \(j\ge k\)**, rather than conditioning on a random sample count as if it were independent:

\[
\Pr\left\{\exists j\ge k:
\left|\frac1j\sum_{i\le j}Z_i-q\right|\ge\gamma q
\right\}
\le
2\exp\left[-\frac{kq\gamma^2}{2+2\gamma/3}\right].
\]

The proof changes measure to a coin at the deviation boundary and sums disjoint first-crossing events. A bound for the rarer outcome also controls the other outcome because the estimates sum to1. Combining this event with the repeated-visit event gives Theorem 12. [Appendix A.4–A.5,pp. 21–24](https://arxiv.org/pdf/2610.40845v1#page=21)

Theorem 10 supplies the other essential improvement. For every convex\(\varphi\),

\[
\sum_w\varphi(\pi(w))
\le
\sum_{j=0}^d\binom dj\varphi(a^jb^{d-j}).
\]

A stationary window distribution is a depth-\(d\) probability tree. Its prefix-conditioned branch probabilities remain in\([b,a]\) because they are averages of allowed full-context probabilities. At each node, convexity maximizes the leaf functional at an endpoint split. Induction therefore gives the product-coin mass profile.

For \(s=tb^d\) and \(\rho=a/b\),

\[
\sum_w e^{-t\pi(w)}
\le\sum_{j=0}^d\binom dj e^{-s\rho^j}
\le \exp[-s+d e^{-2s\epsilon/b}].
\]

If \(s\ge b(1+\ln d)/(2\epsilon)\), the sum is at most\(1.445e^{-s}\). Treating all\(2^d\) states as if they had the minimum mass would instead introduce a factor proportional to\(d\). The profile keeps the fact that only polynomially many windows lie near a given rare mass level.

Lemma 19 also gives the sharper logarithmic coefficient
\(\kappa(\rho)=\max_{j\ge1}j\rho^{-j}\le1/(e\ln\rho)\):
the product sum is at most\(e^{1-u}\) when
\(s\ge\kappa(\rho)\ln d+u\).
A single maximizing level shows this coefficient is sharp for that product sum. This is a refinement of the summation step, not a complete sharp-constant minimax theorem.

## 5. Lower bounds and information actually observed

The divergence–visit identity, Lemma 21, is

\[
D(P_0^{(n)}\Vert P_1^{(n)})
=
\mathbb E_{P_0}N_{w_0}(n)\,
D(\operatorname{Bern}(q)\Vert\operatorname{Bern}(q')),
\]

when the two kernels differ only at\(w_0\) and start from the same window. It is a pathwise KL chain-rule calculation. Information about a modified row is acquired only on visits to that row. The source result concerns observed bits and a statistical estimator, with no computation, storage or finite-precision budget charged.

**The logarithmic-\(d\) term.** Start the iid source with zero-probability\(b\) at\(1^d\). Alternatives modify a single window
\(w_j=0^{j-1}10^{d-j}\), \(j=2,\ldots,d\), changing its zero-probability to\(b(1+2.2\gamma)\). The first such window is omitted because it could occur before the initial context has shifted out. The remaining windows cannot appear before time\(d\).

Small\(\gamma\) both keeps the alternatives in the box and makes their relative-accuracy intervals disjoint. Every proper border of a one-one window consists of zeros and has length at most\((d-1)/2\). Two returns are consequently more than\(d/2\) steps apart. A length-\(d\) path ending at the changed row encounters at most one earlier changed departure, controlling its likelihood ratio and expected visits under the alternative. Combining this with Fano yields

\[
n\ge \frac{\ln(d+1)}{6\gamma^2b^d}
\quad(d\ge16).
\]

**The confidence term.** Modify the rarest row\(0^d\) instead. Under the iid baseline, its expected number of visits is exactly\((n-d)_+b^d\). Binary testing gives the information requirement
\((1-2\delta)\ln((1-\delta)/\delta)\).
For\(\delta\le1/4\), its ratio to\(\ln(1/\delta)\) is at least\(\ln3/(2\ln4)\). Combining the two lower bounds, and using the confidence term alone for\(d<16\), gives the stated\(1/20\) constant. [Appendix A.5,pp. 24–26](https://arxiv.org/pdf/2610.40845v1#page=24)

**An instance-indexed bound.** Theorem 29 fixes a window in an arbitrary reference source, with rarer outcome probability\(q\), and assumes
\(q'=q(1+\gamma)/(1-\gamma)<a\).
It compares the original row, the perturbed row and their midpoint\(q_m\). With

\[
\kappa=\max\{D(\operatorname{Bern}(q_m)\Vert\operatorname{Bern}(q)),
D(\operatorname{Bern}(q_m)\Vert\operatorname{Bern}(q'))\},
\qquad
\Lambda=\frac{\ln[1/(4\delta(1-\delta))]}{2\kappa},
\]

it obtains

\[
n\ge
\frac{1-2\gamma}{1-\gamma}
\frac{\Lambda-C(\epsilon)}{\pi(w_0)}.
\]

The method must still be correct on **every source in the class**, including the local alternative. This is not a lower bound for an estimator promised the exact reference source. A midpoint change-of-measure argument forces enough visits. A Kac return decomposition bounds how much changing the one row can increase its stationary mass. The strict inequality for\(q'\) allows a small further perturbation so touching accuracy intervals become disjoint.

Corollary 30 uses a rarest window with\(\pi(w_0)\le2^{-d}\), and requires
\(\gamma<\epsilon/(1+\epsilon)\). The resulting source-independent necessary length retains the uniform-class correctness premise. [Appendix B.5,pp. 35–36](https://arxiv.org/pdf/2610.40845v1#page=35)

## 6. Additional results and the quantitative audit

### 6.1 General alphabets and expanders

Appendix B.2 separates two quantities for a block length\(L\): its row overlap\(c_L=1-\delta(P^L)\), and its maximum target landing probability\(r_L(w)\). With\(S_L(w)=\sum_{t<L}P^t(w,w)\), the bound is

\[
\pi(w)\mathbb E_u\tau_w
\le S_L(w)+\frac{Lr_L(w)}{c_L}.
\]

For general finite-alphabet shift sources with maximum conditional symbol probability\(a<1\) and minimum conditional Hellinger affinity\(\beta>0\), the block overlap is at least
\(1-\sqrt{1-\beta^{2d}}\).
This yields a dimension-uniform hitting bound when\(a<\beta^2\). That is a sufficient criterion for this general class. The sharper binary endpoint-coin argument replaces the squared affinity exponent and reaches\(\epsilon<3/10\), whereas the general-affinity criterion reaches only\(\epsilon<1/4\).

For a connected nonbipartite regular graph on\(m\ge4\) vertices, let\(\lambda_*\in(0,1)\) be the maximum absolute nontrivial eigenvalue and
\(L=\lceil\ln m/\ln(1/\lambda_*)\rceil\). Corollary 15 and Appendix B.3 give

\[
\frac1m\mathbb E_u\tau_w
\le\frac1{1-\lambda_*}+\frac{5L}{m}.
\]

The proof uses spectral estimates only to bound block overlap, landing mass and early returns. A fixed spectral gap gives hitting time\(O(m)\). This application does use a spectral quantity, while the binary-source learning bound does not require a mixing-time or spectral-gap input.

### 6.2 Direct min-entropy lower bound

Proposition 22 uses a source that is fair everywhere except at\(0^d\), where its zero-probability is\(x\ge1/2\). Its min-entropy rate is exactly\(-\log_2x\), since the all-zero path attains the maximal asymptotic per-step probability.

Let\(v=2^{2\eta}\), require\(v/2<a\), and write
\(L_\delta=(1-2\delta)\ln((1-\delta)/\delta)\).
Any procedure estimating the min-entropy rate to absolute error\(\eta\) with confidence\(1-\delta\) uniformly over the class needs, from\(1^d\),

\[
n\ge d+
\frac{2^{d+1}L_\delta}{-\ln[v(2-v)]}.
\]

The proof compares the fair source with the one-row alternative. Their entropy rates differ by\(2\eta\), and a limiting extra perturbation handles the shared endpoint of the accuracy intervals. Under the fair source the changed row is seen only\((n-d)_+2^{-d}\) times in expectation. The binary row divergence is\(-\tfrac12\ln[v(2-v)]\). As\(\eta\to0\), the denominator is\(4\ln^2(2)\eta^2+o(\eta^2)\). This directly establishes an\(\Omega(2^d\eta^{-2})\) uniform entropy-estimation obstruction, rather than assuming that full-kernel recovery is necessary for every entropy estimator. [Appendix B.1,pp. 27–29](https://arxiv.org/pdf/2610.40845v1#page=27)

### 6.3 Numerical values and limits of the hardware attribution

Tables 2–3 apply the formulas at\(\epsilon=.05,\gamma=.01,\delta=.01\). The main reader independently substituted the actual formulas, using\(C(.05)\le2.31\) in Theorem 29 and the exact product-profile sum with the proof's unrounded\(K_\star\) for sufficiency:

| Memory \(d\) | Necessary transition-estimation length | Sufficient transition-estimation length | Necessary length for entropy error \(\eta=.01\) |
|---:|---:|---:|---:|
| 8 | 22,782,595 | 249,576,429 | 11,830,753 |
| 12 | 555,588,367 | 6,406,894,430 | 189,291,932 |

The source rounds these to\(2.3\times10^7,2.5\times10^8,1.2\times10^7\) for\(d=8\), and\(5.6\times10^8,6.4\times10^9,1.9\times10^8\) for\(d=12\). At\(n=10^6,d=8\), the formula inversions give relative-error lower resolution\(0.04518\), sufficient resolution\(0.16773\) and min-entropy lower resolution\(0.03381\). These reproduce the paper's approximately 4.5%, 17% and 0.034 figures. They are bounds within the stipulated source class, not measured performance or authenticated hardware properties.

The paper labels two hardware rows, “Ring-oscillator TRNG (OpenTRNG)” and “Multi-ring oscillator jitter,” as using a million-bit trace with\(d=8\), and calls them underpowered. Appendix B.1 supplies no row-specific external citation. The submitted TeX contains an unpublished TODO asking to recheck those trace lengths and noting a possible mismatch between correlation tests and an 8-bit Markov fit. The note below treats the mathematical calculations separately from these application claims.

The bounded primary-source check found the following:

| Identifiable source | What the inspected original actually reports | Limit of the attribution |
|---|---|---|
| Alcocer, Gómez and Gómez-Pérez, [arXiv2603.13525v1](https://arxiv.org/pdf/2603.13525v1), §IV,p. 4 | \(10^5\) bits per configuration for \(C_2\) and Maurer Z-score calculations, across 34 ERO and 24 COSO configurations | The million-bit number onp3 is a theoretical scale for a \(C_8\) condition. It is not this experiment's trace length or a demonstrated 99% guarantee for a fitted order-eight kernel |
| [OpenTRNG analysis documentation](https://opentrng.org/docs/analysis.html), Entropy estimation | Its eight-bit example applies the most-common-value estimator to eight-bit samples | Sample width is not an authenticated eight-bit binary history order |
| Lubicz and Fischer, [Journal of Cryptology 37, 13, 2024](https://link.springer.com/article/10.1007/s00145-024-09494-6), §7 | \(10^6\) bits estimate duty cycle, period ratio and Wiener volatility. Later validation uses one million **bytes** per configuration. Shannon-entropy management uses a physical model and target 0.997 | Neither stage authenticates the table's unrestricted \(d=8\) kernel and accuracy specification. The generic multi-ring row is not explicitly assigned to this paper |
| Hamburg, Kocher and Marson, [CRI Intel report](https://www.rambus.com/wp-content/uploads/2015/08/Intel_TRNG_Report_20120312.pdf), §4.2,pp. 19–20 | A state comprising the preceding 12 output bits, with sparse-state problems at longer histories, and Markov–Rényi min-entropy estimates | The inspected empirical sections do not disclose per-file bit counts or the table's 99%/1% estimation target. Intel's table verdict is blank in Skórski |

These are **scoped dependency readings**. Root inspected Alcocer's originalpp3–4, Intel's§4.2 text and adjacent material onpp19–20, the OpenTRNG estimator passage, and Lubicz–Fischer's primary model/§7 passages. The source agent inspected the additional narrowly identified experimental passages. No cited hardware paper is marked fully read, and no device-security conclusion is drawn.

The bound requires an order-\(d\) binary source in the stated probability box and an estimator whose accuracy/confidence target is guaranteed uniformly over that class. A physics-based source model, a byte-valued sample, a correlation test and an arbitrary 8-step binary transition kernel are different statistical objects. Neither a matching trace length nor a computed lower-bound number establishes that a named experiment promised the theorem's task. The paper's general mathematical obstruction remains useful without accepting the unverified hardware verdicts.

## 7. Independent checks and verification status

The main reader followed all proofs, including the stopping-time dependence issue, the one-row KL calculation, the one-one-word border restriction and the midpoint stationary-mass comparison. No formal proof was run, no empirical source experiment was replicated and no whole-theorem independent certification is asserted.

An independent finite-kernel calculation enumerated **828 endpoint-valued kernels**: every table for\(d=1,2,3\), at each\(\epsilon=.05,.2,.4\). Stationary distributions and target hitting times were computed by finite linear systems. At tolerance\(10^{-10}\), all checked kernels obeyed the stationary-profile majorization and the stated\(B_d\) hitting bound. The maximum observed Dobrushin coefficient equaled the endpoint-coin prediction in each case. The largest stationarity residual was below\(2.3\times10^{-16}\). This is a finite floating-point check, covering no arbitrary interior table or unbounded order.

For example, at\(\epsilon=.2,d=3\), the maximum observed Dobrushin coefficient was 0.568, the maximum normalized hitting time was 3.52778 and\(B_d=4.38444\). At\(\epsilon=.4,d=3\), these were 0.944, 25.75 and 41.71. The latter case checks the finite-\(d\) formula above the uniform threshold. It does not test the asymptotic threshold itself.

An independently written standard-library calculation checked the overlap on1,152 declared points: \(\epsilon\in\{0,.0001,.001,.01,.05,.10,.15,.20,.25,.28,.29,.30,.40,.49,.499,.5\}\), and \(d\in\{1,\ldots,64,127,128,255,256,511,512,1023,1024\}\). Direct overlap sums, a separate binomial-tail implementation and576 distinct parity pairs agreed in exact rational arithmetic. The sharp inequalities passed squared rational comparisons, with a rational enclosure for\(\pi\) from the alternating-series remainder in Machin's formula. No numerical integration or proof of global optimal constants was performed.

Table 1 was independently recomputed for \(d=1,\ldots,512\) at its seven endpoints:

| \(\epsilon\) | Maximizing \(d\) | \(\max_d B_d\), rounded for display | Printed upper bound |
|---:|---:|---:|---:|
| .05 | 5 | 2.306238527376 | 2.31 |
| .10 | 5 | 2.837354032258 | 2.84 |
| .15 | 5 | 3.703259874050 | 3.71 |
| .20 | 7 | 5.339711760799 | 5.34 |
| .25 | 9 | 10.605087732350 | 10.61 |
| .28 | 23 | 30.418360940905 | 30.42 |
| .29 | 47 | 76.366823195508 | 76.37 |

For the unscanned integer tail, retaining central binomial terms gives, independently of the sharp overlap inequality,

\[
c_d\ge\frac{(4ab)^m}{2m+1},\qquad
B_d\le\frac1b+
\frac{(2m+1)^2}{a}\left(\frac a{4b}\right)^m,
\quad m=\lceil d/2\rceil.
\]

The ratio of successive tail terms is
\((a/(4b))((2m+3)/(2m+1))^2\), decreasing in\(m\).
At\(m=257\) it is below1 for all seven endpoints. The resulting tail supremum is below the corresponding finite maximum in every case. Thus the seven outward-rounded values are supported for the explicit scalar expression, without the missing author certificate. The main reader read the independent code and tail derivation. The table's “\(\epsilon\le\)” interpretation also follows from scalar monotonicity: the head and \(a^d-b^d\) increase with\(\epsilon\), while the exact integral formula makes\(c_d\) decrease.

These checks do not independently certify the connection of \(B_d\) to every allowed Markov chain. The main reader's separate finite-kernel calculation checks that connection only in the stated finite cases. Tables 2–3 were independently reproduced numerically as recorded above. Author-provided scripts were unavailable, so no claim of replaying them is made.

## 8. Citation dependencies, unresolved questions and use boundary

All21printed references were read as references. Their complete source papers were not thereby read. The principal dependencies are:

| Role | Cited sources and actual use |
|---|---|
| General Markov-chain background | Kac 1947, Dobrushin 1956, Aldous–Fill and Levin–Peres–Wilmer provide recurrence, contraction and hitting/mixing terminology |
| Existing estimation objectives | Wolfer–Kontorovich 2019/2021, Huang–Li 2024, Han et al.2018, Kamath–Verdú 2016 and Han–Jana–Wu 2023 concern distinct row norms, entropy targets or prediction losses |
| Multiple visits and sequential tails | Chan–Ding–Li 2021 motivates \(k\)-cover time, Howard et al.2020 supplies time-uniform concentration context, Freedman 1975 is cited for a constant improvement |
| Overlap and testing | Talagrand 1995, Smirnov 2026, DLMF, Bretagnolle–Huber 1979 and Cover–Thomas 2006 support tail, beta-integral and information-inequality tools |
| Prediction and entropy-source context | Willems–Shtarkov–Tjalkens 1995, NIST 800-90B and Hamburg–Kocher–Marson 2012 supply contextual comparisons, not a demonstrated identification of every hardware-table row |

The source discussion distinguishes uniform relative transition estimation from expected next-symbol KL prediction, including context-tree methods. No new claim of priority over all statistical estimation work is independently established here.

Open questions retained from the paper are the matching learning upper bound for\(\epsilon\ge3/10\), the true near-threshold growth of worst normalized hitting, and whether the hitting-envelope blow-up must enter optimal learning at all. Exact numerical certification of the advertised global constants remains limited by missing author scripts. The hardware rows require authenticated models, trace definitions and accuracy targets before being used as a refutation of those evaluations.

The result may be used as a source on learning **a supplied observed-window model**. It supplies no general construction of learned finite state, no bound on charged model bytes, no unknown raw-name action acquisition result and no transfer guarantee for a separate text source. No FP theoretical deduction or novelty claim is made in this note.
