# Harris et al. 2026: three-round normalization through random low-curvature paths

## Source, edition and actual coverage

**David G. Harris, Vladimir Kolmogorov, Hongyang Liu, Yitong Yin and Yiyao Zhang, _Near-Optimal Parallel Approximate Counting via Sampling_, arXiv:2604.01263v2, 12 July 2026.** [Version record](https://arxiv.org/abs/2604.01263v2) · [PDF](https://arxiv.org/pdf/2604.01263v2) · [TeX](https://arxiv.org/src/2604.01263v2) · [HTML](https://arxiv.org/html/2604.01263v2).

The [official SPAA 2026 accepted-paper list](https://spaa.acm.org/papers-accepted-to-spaa-2026/), [conference program](https://spaa.acm.org/spaa-2026-conference-program/) and [Kolmogorov's institutional author page](https://pub.ista.ac.at/~vnk/papers/GIBBS-PARALLEL.html) authenticate the peer-reviewed conference publication. The [publisher-supplied Crossref record](https://api.crossref.org/works/10.1145/3816782.3819191) gives _Proceedings of the 38th ACM Symposium on Parallelism in Algorithms and Architectures_, pages 550–559, DOI [10.1145/3816782.3819191](https://doi.org/10.1145/3816782.3819191), print date 6 July and online date 8 July 2026. The separately typeset ten-page conference body was not retrieved or compared. Actual full reading is the later **23-page arXiv v2**, not an assertion that every conference statement is identical.

Pro-A completed the full active `main2.tex` on 27 November 2026, Shanghai: front matter, Sections 1–4, Appendices A–C, all statements and proofs, all five algorithms, the comparison table, three scientific footnotes and all 21 printed references. There are no figures. Original PDF pages 3, 5, 7, 10, 16, 21 and 22 were visually inspected. The source has one body file and a complete `.bbl`, with no omitted chapter or image files. The earlier merged manuscripts 2505.18324 and 2408.09719 and the first edition of the present identifier were not independently read. No AI-use disclosure was found in the inspected manuscript, which does not establish actual use.

Support readers checked version identity, file inventory, the PPE/width interface and the application resource boundaries. The main reader personally read the entire scientific text. This is a mathematical reading with the short independently derived bridge interpretation below, not a complete dependency audit, formal verification, implementation audit or empirical reproduction. Historical results cited by the paper are read only as stated and used here, unless explicitly indicated otherwise.

## 1. What is constructed

The paper constructs a short temperature path on which a product estimator has controlled relative variance. The temperature coordinates are observable, but the useful spacing coordinate, \(z(\beta)=\log Z(\beta)\), is unknown. A two-batch procedure approximates the spacing of a Poisson process in that unknown coordinate using only samples and evaluations of the Hamiltonian. A third independent batch estimates the partition ratio.

The constructive chain is

\[
\text{pointwise expected path width}
\ \Longrightarrow\ \text{expected total curvature}
\ \Longrightarrow\ \text{product-estimator relative error}.
\]

It is not necessary to learn \(Z\) first, maintain a uniformly accurate estimate of it, or make every random gap small simultaneously. The pointwise expectation interface is enough. This is the main mathematical instrument extracted from Sections 2–3.

### Observation and resource model

For finite \(\Omega\), nonnegative weights \(F\) and Hamiltonian \(H\), set

\[
Z(\beta)=\sum_{\omega\in\Omega}F(\omega)e^{\beta H(\omega)},
\qquad
\mu_\beta(\omega)=\frac{F(\omega)e^{\beta H(\omega)}}{Z(\beta)}.
\]

The black box supplies independent samples at any chosen \(\beta\in[\beta_{\min},\beta_{\max}]\). The counting algorithm uses a sample only through \(H(\omega)\), equivalently through the gross energy law \(\mu_\beta(x)=c_xe^{\beta x}/Z(\beta)\). The coefficients \(c_x\) need not be known.

The assumptions are an energy support contained in \(\{0\}\cup[1,\infty)\), after an allowed rescaling, and known bounds

\[
q,h\ge2,\qquad
\log Q\le q,\qquad
\mathbb E_{\mu_{\beta_{\max}}}H\le h,
\qquad Q=Z(\beta_{\max})/Z(\beta_{\min}).
\]

In particular, **\(h\) bounds the endpoint mean, not the largest possible energy**. A finite lower endpoint need not have zero-energy mass. If \(\beta_{\min}=-\infty\), a finite ratio requires \(c_0=Z(-\infty)>0\), and its gross law is the known point mass at zero.

Theorems 1–2 give the following, for relative error \(\varepsilon\), with constant success probability at least 0.7.

| Construction | Sampling batches | Number of oracle samples |
|---|---:|---:|
| Deterministic `StaticSchedule` plus PPE | 1 | \(O(q\varepsilon^{-2}\log^2h)\) |
| `PseudoTPA` plus fresh PPE | 3 | \(O(q\varepsilon^{-2}\log h)\), in expectation |

The abstract's two rounds of adaptivity mean two additional rounds after the initial batch, hence three sampling batches in total. Independent parallel repetition and a median give confidence \(1-\delta\) at an additional \(O(\log(1/\delta))\) sample factor without adding batches.

These are oracle-query and adaptivity bounds. An efficient implementation additionally needs the sampler, arithmetic, scheduling and sorting work. They do not measure learned-state size or finite-precision description length. The source compares its sample complexity with the best sequential \(O(q\varepsilon^{-2}\log h)\) bound and a cited \(\Omega(q\varepsilon^{-2})\) oracle lower bound. The lower-bound dependency is not independently reread here.

## 2. A midpoint bridge controls the product estimator

For a schedule \(B=\{\beta_0<\cdots<\beta_t\}\), define

\[
w_i=z(\beta_{i+1})-z(\beta_i),\qquad
\kappa_i=z(\beta_i)+z(\beta_{i+1})-2z((\beta_i+\beta_{i+1})/2),
\qquad \kappa(B)=\sum_i\kappa_i.
\]

Convexity of \(z\) gives \(\kappa_i\ge0\). For finite endpoints \(a<b\), write \(m=(a+b)/2\). Independently draw \(X\sim\mu_a\), \(Y\sim\mu_b\), and use

\[
U=e^{(b-a)X/2},\qquad V=e^{-(b-a)Y/2}.
\]

The moment-generating identity \(\mathbb E_{\mu_\beta}e^{\alpha H}=Z(\beta+\alpha)/Z(\beta)\) gives

\[
EU=Z(m)/Z(a),\qquad EV=Z(m)/Z(b),
\qquad \operatorname{RV}(U)=\operatorname{RV}(V)=e^{\kappa(a,b)}-1.
\]

Here \(\operatorname{RV}(W)=\operatorname{Var}(W)/(EW)^2\). Average \(k\) independent copies of each variable in each interval, and multiply the interval averages separately. The ratio of the two product expectations is exactly \(Q\). For the numerator product,

\[
\operatorname{RV}\!\left(\prod_i\overline U_i\right)
=\prod_i\left(1+\frac{e^{\kappa_i}-1}{k}\right)-1
\le\frac{e^{\kappa(B)}-1}{k},
\]

and the denominator has the same bound. The inequality follows by expanding the nonnegative products and using \(k^{-r}\le k^{-1}\) for \(k\ge1\). Theorem 6, attributed to Huber's PPE, takes

\[
k\ge100(e^{\kappa(B)}-1)/\varepsilon^2,
\qquad 0<\varepsilon<1/2,
\]

to make both products concentrate sufficiently for their ratio to have relative error at most \(\varepsilon\), with probability at least 0.8. **The ratio estimator itself is not asserted to be unbiased.**

At \(\beta_0=-\infty\), the first factor is handled separately: \(U_0=1\), while \(V_0\) averages indicators that a sample at \(\beta_1\) has energy zero. Set \(\kappa(-\infty,\beta_1)=z(\beta_1)-z(-\infty)\). The same upper bound works, without claiming the finite-endpoint equality of both relative variances for this special interval.

If the schedule is random, condition on its construction and use fresh independent PPE samples. Reusing the schedule-selection observations without a new argument would not supply this conditional product calculation.

## 3. Width bounds curvature without observing the normalizer

For a fixed temperature \(x\), let \(B_-(x)\) and \(B_+(x)\) be its neighboring schedule points and define

\[
W(B,x)=z(B_+(x))-z(B_-(x)).
\]

Theorem 7 states that, if \(\mathbb EW(B,x)\le\theta\le1\) for every fixed \(x\), then

\[
\boxed{\mathbb E\kappa(B)\le5\theta\log(h/\theta).}
\]

This is **pointwise expected width**, not an expectation of the maximum width. It permits occasional large random intervals. A deterministic maximum-width bound is a special case, giving Corollary 8.

The proof uses \(z'=E_\beta H\), \(z''=\operatorname{Var}_\beta H\) and the interval inequality

\[
\kappa(a,b)\le [z(b)-z(a)]
\min\{1,\log(z'(b)/z'(a))\}.
\]

Above the location where \(z'\) reaches \(\theta/2\), summation is bounded by an integral of
\(W(B,x)z''(x)/z'(x)\). Taking expectation leaves \(\theta\) times a logarithmic change in \(z'\), bounded by the endpoint mean \(h\). Below this location, the support gap above zero gives

\[
z(-\infty,\beta)\le2z'(\beta)
\quad\text{when }z'(\beta)\le1/2.
\]

This bounds the initial tail. The proof separately handles the cases where the threshold lies outside the interval. The energy support premise is doing real work here, even though the final condition is expressed through derivatives and expected widths.

### Deterministic path from only \(q,h\)

`StaticSchedule(\theta)` starts at \(\beta_{\max}\) and moves backward with step \(\theta/s_i\), where

\[
s_i=\min\{h,q/(\beta_{\max}-\beta_i)\},
\]

with \(s_0=h\). Convexity and the ratio bound imply \(z'(\beta_i)\le s_i\), so each completed interval has \(z\)-width at most \(\theta\). Once \(s_i<\theta/2\), the initial-tail bound closes the path, including a possible infinite endpoint.

Theorem 9 gives length \(O(q\log(h/\theta)/\theta)\). The initial \(O(q/\theta)\) steps are equally spaced. Thereafter the distance from \(\beta_{\max}\) grows geometrically, with ratio \(1+\theta/q\). Proposition 10 uses these explicit formulas to generate the grid in NC, despite its sequential-looking pseudocode.

Taking \(\theta=1/(5\log h)\) yields length \(O(q\log^2h)\) and \(\kappa(B)\le3\). All PPE samples can then be requested in one batch.

## 4. Parallelizing the useful geometry of TPA

The ordinary Tootsie Pop Algorithm draws \(X\sim\mu_\beta\) and \(\eta\sim\operatorname{Exp}(1)\), then moves to

\[
\beta'=\beta-\eta/X,
\]

with \(X=0\) interpreted as \(-\infty\). For \(\alpha<\beta\),

\[
\Pr(\beta'<\alpha)=E e^{-(\beta-\alpha)X}=Z(\alpha)/Z(\beta).
\]

Consequently the decrease in \(z\) is an exponential variable, truncated at the zero-energy boundary. Repeating this process creates a Poisson process in \(z\)-space. Superposing \(k\) independent paths gives expected adjacent left/right distances \(1/k\), but constructing each path is adaptive. The paper's new operation preserves enough of that spacing geometry with two batches instead of simulating the entire sequential path.

### Batch 1: an observable thinning rule for a hidden coordinate

Construct the deterministic coarse grid \(B=\operatorname{StaticSchedule}(1/4)\). At each interior \(\beta_i\), draw two independent samples \(X_1,X_2\) from the right endpoint law \(\mu_{\beta_{i+1}}\), and retain \(\beta_i\) with probability

\[
1-\exp[-(X_1+X_2)(\beta_{i+1}-\beta_i)].
\]

Unconditionally this is exactly

\[
1-e^{-2[z(\beta_{i+1})-z(\beta_i)]}.
\]

Retentions are independent across grid cells. This is the occupancy probability of a rate-two Poisson process in each unknown \(z\)-cell, computed without knowing its length. It gives expected retained length at most \(2q+2\). For each fixed \(x\), the retained left and right \(z\)-gaps \(W'_-\), \(W'_+\) obey

\[
\Pr(W'_\pm>s+1/4)\le e^{-2s}.
\]

The two gaps depend on disjoint sets of retention decisions and are independent. The rate greater than one is useful because the next step needs exponential moments, not just expected gap lengths.

### Batch 2: one generation of independent exponential jumps

Set \(k=\lceil10/\theta\rceil\). At every retained anchor, generate \(k\) fresh TPA jumps and add their destinations, together with the anchor itself. Clamp to the original temperature interval. Destinations do not recursively initiate more queries in this batch. Deterministic infinite endpoints require no new energy sampling.

Condition on left/right pruned gaps \(p,r\). The tail calculations in Propositions 17–18 give

\[
E[W''_+\mid B']\le e^r/k,
\qquad E[W''_-\mid B']\le e^{r+p}/k.
\]

The rate-two tails and independence imply
\(Ee^r\le2e^{1/4}\) and \(Ee^{r+p}\le4e^{1/2}\). Thus

\[
EW(B'',x)\le(2e^{1/4}+4e^{1/2})/k<10/k\le\theta.
\]

The expected final length is \(O(kq)\). Schedule construction uses \(O(q\log h+kq)\) samples in expectation, in two batches. These bounds price all initial coarse-grid pruning calls, not only the retained anchors.

### Batch 3: fresh bridge estimation

Choose \(\theta=1/(5\log h)\). The width theorem gives \(E\kappa(B'')\le3\), and Markov gives \(\kappa(B'')\le30\) with probability at least 0.9. On this event, a fresh PPE with \(k_{\rm PPE}\ge100(e^{30}-1)/\varepsilon^2\) succeeds with probability at least 0.8. The joint success is at least 0.72 and hence at least the advertised 0.7.

The resulting expected query count is \(O(q\varepsilon^{-2}\log h)\). The displayed constants are large. This is an asymptotic construction, not a practical performance measurement. Expected length/query count and the fixed number of sampling batches are different guarantees.

## 5. Independent deduction: curvature is exactly an overlap budget

The following is a direct algebraic interpretation of the source PPE, without a novelty claim. For finite endpoints on the common positive support, define the Hellinger affinity

\[
A(a,b)=\sum_\omega\sqrt{\mu_a(\omega)\mu_b(\omega)}.
\]

The common Gibbs base weight gives

\[
A(a,b)=\frac{Z((a+b)/2)}{\sqrt{Z(a)Z(b)}},
\qquad
\boxed{\kappa(a,b)=-2\log A(a,b).}
\]

Thus curvature is the order-\(1/2\) Rényi divergence between endpoint laws. Moreover, writing \(\mu_m\) for the midpoint law,

\[
\chi^2(\mu_m\Vert\mu_a)
=\chi^2(\mu_m\Vert\mu_b)
=A(a,b)^{-2}-1
=e^{\kappa(a,b)}-1.
\]

For example, the first equality follows by summing \(\mu_m^2/\mu_a\): its value before subtracting one is \(Z(a)Z(b)/Z(m)^2\). The paired estimator therefore gives the midpoint the same relative-variance cost from either endpoint. Along a schedule, \(e^{\kappa(B)}=\prod_i A_i^{-2}\) measures the cumulative loss of overlap that enters the product bound.

There is also the exact variance integral

\[
\kappa(a,b)=\int_a^m(u-a)\operatorname{Var}_{\mu_u}H\,du
+\int_m^b(b-u)\operatorname{Var}_{\mu_u}H\,du.
\]

It follows by integrating \(z''\) twice on both sides of \(m\). The triangular weights make clear which energy fluctuations contribute to local bridge cost.

### A bridge estimator beyond one-parameter Gibbs families

Let \(w_a,w_b\) be arbitrary positive, computable unnormalized weights on a common finite support, with normalizers \(Z_a,Z_b\) and exact sampling access to their normalized laws. For independent endpoint draws use

\[
U=\sqrt{w_b(X)/w_a(X)},\qquad
V=\sqrt{w_a(Y)/w_b(Y)}.
\]

The geometric bridge weight \(w_g=\sqrt{w_aw_b}\) has normalizer \(Z_g\). Direct calculation gives

\[
EU=Z_g/Z_a,\qquad EV=Z_g/Z_b,\qquad
\frac{EU}{EV}=\frac{Z_b}{Z_a},
\qquad \operatorname{RV}(U)=\operatorname{RV}(V)=A(a,b)^{-2}-1.
\]

Consequently the telescoping ratio and independent product-variance bound survive for any such chain with a controlled sum of \(-2\log A\). This is a reusable normalization interface. It does **not** extend the short-grid or three-round schedule theorem to arbitrary weight families. Those constructions additionally use the ordered exponential-family path, energy support, derivative bounds and computable TPA transitions. Common support and evaluable endpoint weight ratios are also substantive assumptions.

## 6. Applications and what pays for the sampling oracle

Section 4 and Appendices B–C give actual samplers to instantiate the counting interface. The quoted mixing and parallel-simulation dependencies are not independently fully read here.

| Model and conditions | Counting depth | Processors, suppressing logarithmic factors |
|---|---|---|
| Anti-ferromagnetic two-spin, fixed edge parameters, uniqueness gap \(\delta\). For \(\gamma_2>1\), the stated theorem requires a regular graph. | \(O_\delta(\log\Delta\,\log(n/\varepsilon))\) | \(\widetilde O_\delta(m^2/\varepsilon^2)\) |
| Hard-core model in that uniqueness regime | Same depth | \(\widetilde O_\delta(mn/\varepsilon^2)\) |
| Monomer-dimer, fixed edge activity \(\lambda>0\) | \(O_\lambda(\Delta^4\log^3n\,\log(n/\varepsilon))\) | \(\widetilde O_\lambda(m^2\Delta/\varepsilon^2)\) |
| Ferromagnetic Ising, \(\gamma_e\ge1+\delta\), \(0<\lambda_v\le1-\delta\), fixed slack \(\delta\) | \(O_\delta(\log(n/\varepsilon)^{O(1)})\) | \(\widetilde O_\delta(nm^2/\varepsilon^2)\) |

The monomer-dimer bound retains \(\Delta^4\). It supplies polylogarithmic depth for bounded or suitably polylogarithmic degree, not a degree-independent RNC conclusion from that displayed bound alone. The other suppressed constants retain the formal parameter conditions. No empirical timing or memory advantage is demonstrated.

For two-spin systems, the path changes the vertex activity through the connected lower or upper uniqueness interval. A lower-interval path starts at zero activity, with \(H=n_+\). An upper-interval path factors out \(\lambda^n\) and uses \(H=n-n_+\), so it also starts at a tractable zero endpoint after inversion. The formal theorem handles general anti-ferromagnetic parameters with either \(\gamma_2\le1\), or regularity when \(\gamma_2>1\). It does not cross a nonunique region merely because the target is easy.

Appendix B combines a sequential mixing theorem with a parallel single-site simulator. The latter has depth \(O(\rho(T/n+\log n)\log\Delta)\) when a Dobrushin matrix norm is at most \(\rho\ge1\). This is not a demand that the norm be below one. The anti-ferromagnetic application bounds it by \(64/\delta^2\). The matching application uses the line graph and the elementary bound \(\|R\|_1\le2\Delta\), which explains its retained degree cost. Extreme activities permit a deterministic near-all-minus or near-all-plus output. These cases keep the oracle depth uniform over the activity path, while fixed edge parameters remain in constants.

### Why an endpoint mean matters for the Ising application

Take \(\eta=-1/\log(1-\delta)\) and

\[
H(\sigma)=\eta\sum_{v:\sigma_v=+1}\log(1/\lambda_v),
\qquad \beta_{\max}=-1/\eta,\quad\beta_{\min}=-\infty.
\]

Then nonzero energies are at least one, but can be arbitrarily large when some \(\lambda_v\) is tiny. The random-cluster representation gives \(\Pr(\sigma_v=+1)\le\lambda_v\). Therefore

\[
E_{\beta_{\max}}H
\le\eta\sum_v\lambda_v\log(1/\lambda_v)
\le n\eta/e.
\]

One can take \(h=\max\{2,n\eta/e\}\) and \(q=n\). The latter follows by bounding every edge factor by the all-minus edge product and summing at most \(2^n\) spin configurations. No positive lower bound on the vertex activities is needed for this mean-energy argument.

### Field dynamics supply the Ising sampler

Appendix C switches to random-cluster edge parameters \(p_e=1-1/\gamma_e\), bounded away from zero by the slack. At each field-dynamics step, add edges independently to \(S\) with probability \(\theta\), retain the current edges \(X\), and sample on \(G'=(V,S\cup X)\) with

\[
p_e^*=\frac{p_e}{p_e+\theta(1-p_e)}.
\]

This makes the retained-edge probabilities close to one, where a cited parallel Glauber simulator applies. Minimum \(p^*\) is over edges of \(G'\), not over deleted edges assigned zero. Algorithm 5 specifies

\[
C_1=10^{-27}(1-\lambda_{\max})p_{\min},\qquad
C_2=\left(\frac2{p_{\min}(1-\lambda_{\max})}\right)^{30/(1-\lambda_{\max})^2},
\]

\[
\theta=C_1/\log(n/\varepsilon),\quad
T=C_2\theta^{-200000}\log(2n/\varepsilon),\quad
N_0=\max\{1/C_1,C_2\}.
\]

For \(n\ge N_0\), the biased parameters meet the inner sampler's condition

\[
p^*_{\min}\ge1-\frac{1-\lambda_{\max}}{e^{45}\log(n/\varepsilon')},
\qquad \varepsilon'=\varepsilon/(2T).
\]

Each inner call has \(O(\log^2(mT/\varepsilon))\) depth and \(\widetilde O(m^2\log(T/\varepsilon))\) processors. The \(T\) outer updates are sequential. For fixed slack this is polylogarithmic depth with exponent independent of the slack, rather than constant depth. Smaller \(n\) are handled by brute force whose cost is hidden in a possibly enormous slack-dependent constant. There is no field-truncation operation or positive lower bound on \(\lambda_v\) in Appendix C.

The total sampling error is \(T\varepsilon'\) for approximate updates plus \(\varepsilon/2\) for field-dynamics mixing. The appendix adjusts the cited algorithm's iteration and good-cut parameters. It does not rederive the underlying dynamic-connectivity implementation. Its huge explicit exponent is part of the asymptotic guarantee, not evidence of a practical sampler.

## 7. Approximate sampling, evidence status and reuse boundary

The introduction permits approximate sampling at TV error \(o(1/N)\) for an \(N\)-query algorithm. The appropriate justification is a coupling of the entire adaptive execution. For a run with a deterministic cap of \(N\) calls, a uniform conditional TV error at most \(\tau\) per call changes success probability by at most \(N\tau\). In the expected-query construction one must specify a compatible cap/error budget, or use a stopping-time coupling bound. Merely stating that every sample's marginal distribution is close while allowing arbitrary correlation would not justify the product estimator.

This coupling route does not require bounding the change in every exponential-weight moment by TV. On the coupled event the entire output agrees. It also makes explicit that the sampler must work at the temperatures actually chosen, including random second- and third-round temperatures.

The established source contribution is a constructive sampling-to-counting reduction with a precise low-adaptivity guarantee and conditional parallel samplers for concrete Gibbs models. The independent section above supplies an exact overlap interpretation and a common-support geometric-bridge extension of the estimator. It makes no new optimality or novelty claim, and does not prove the construction discovers a latent representation, learns a transition system, or solves arbitrary sequential prediction.

No FP architecture or experiment is proposed here. A future use would need an explicitly available sampling family, evaluable weight ratios, a bounded overlap path and a physical accounting of sampler and arithmetic work. The mathematical tools can be reused without asserting those premises already hold for FP.

## Archive and continuation

One fixed author edition is marked fully read. Conference publication metadata and merged predecessors remain provenance, without additional full-reading credit. No historical reference has been promoted from a citation to a separate full read. The completion updates the existing index, reading ledger, discovery ledger and Pro-A coordination entry in one paper-result commit. Astra request2e7a6c9 remains completed in its separate response under claimc3f5217, with Astra5be147a preserved as canonical for its completed word-likelihood experiment. Continue ordinary constructive mathematics after a fresh request and ownership check.
