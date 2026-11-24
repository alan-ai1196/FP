# What Fixed-Rollout pass@k Evaluations Can Identify

## Edition and completed coverage

Pranav Singh and Prashant Singh, **arXiv:2609.09245v1**, submitted September 8, 2026 at 10:27:52 UTC. The primary history inspected on November 24 shows this version only. No refereed publication was established. The source uses a TACL style option named `acceptedWithA`, but explicitly calls itself a non-submission professor-review copy. That option is not evidence of acceptance. [Record](https://arxiv.org/abs/2609.09245v1) · [PDF](https://arxiv.org/pdf/2609.09245v1) · [Source](https://arxiv.org/src/2609.09245v1)

The main reader covered all **13 PDF pages**, the complete active `main.tex`, `abstract.tex`, `body.tex` and `appendix.tex`, §§1–8, Appendices A–D, every displayed formula and proof, all three figures, seven tables and 15 printed references. The bibliography source has 18 entries, including three unused entries. There are no ordinary footnotes. Dense mathematical and tabular layouts were checked in the original PDF, including pp. 3, 7 and 11–13. Source files are retrieved under `literature/corpus/pisf_prior_art/2609.09245v1/`. Reading a citation here does not complete the cited source.

This is a complete reading with bounded independent mathematical checks, not a full empirical replication or formal proof. A supporting reader checked only specified Appendix A/C claims and a small exact example. The main paper reading was not delegated. The public-data revision was independently authenticated, but the authors' analysis scripts were not located.

## Original question and observation model

The paper asks what an evaluation with **a fixed number n of completions per task** can determine about the probability of obtaining at least one success at a larger budget k. Fixing prompt, decoding, token cap, parser and scorer defines a task probability p. Conditional on p, completions are iid Bernoulli. In the principal population experiment, task probabilities are independently sampled from an unrestricted probability measure F on [0,1], and the observed success count has law

\[
q_c=\int_0^1 {n\choose c}p^c(1-p)^{n-c}\,dF(p),
\qquad c=0,\ldots,n.
\]

Failure at budget k is \(R_F(k)=\int(1-p)^k\,dF(p)\), and pass@k is \(1-R_F(k)\). A conditional unbiased direct estimator is

\[
\widehat R(k)=\frac1N\sum_{i=1}^N
\frac{{n-C_i\choose k}}{{n\choose k}},\qquad k\le n.
\]

The distinction between experiments is essential. For a **fixed labeled finite vector** of task probabilities, the product-binomial model is formally identifiable. The main nonidentification theorem concerns the pooled/random-task count-law experiment. Infinite exchangeability supplies a Bernoulli-mixture representation, while finite exchangeability alone does not. Correlated completions, task-dependent adaptive rollout counts and pipeline changes require different observation models. [§§1–3, 7]

## Identification, incompatible extensions and exact intervals

The n+1 Bernstein kernels form a basis for polynomials of degree at most n. Thus q is equivalent to the first n free moments, with the zeroth moment fixed at one. In particular,

\[
m_j=\sum_{c=0}^n\frac{(c)_j}{(n)_j}q_c,
\qquad
R_F(k)=\sum_{j=0}^k(-1)^j{k\choose j}m_j.
\]

**Theorem 1** identifies R(k) for k≤n. For every integer k>n there exist two laws with the same complete q and different R(k). More strongly, at every **interior** truncated Hausdorff moment vector, the identified interval has strictly positive width. The derivative of order n+1 of (1−p)^k has constant nonzero sign in the open interval, yielding the required extended Chebyshev system. Boundary moment vectors can have a unique representing measure, in which case all later functionals are determined. More tasks estimate q more accurately, while increasing n changes which moments are directly observable. Neither sentence implies that every particular fiber has a large width. [§3, Appendix A]

Three constructions clarify what remains free:

1. A positive Gauss–Legendre rule integrates all polynomials through degree n just as the uniform law does. Their count laws agree, but uniform failure is 1/(k+1), whereas finite support bounded away from zero gives eventual exponential decay. Figure 1 illustrates n=64, with maximum count-law discrepancy about 6.5×10^-16 in the reported computation.
2. For \(m=n+1\), \(f_\varepsilon(p)=1+\varepsilon P_m(2p-1)\), |ε|<1, preserves these moments. The exact identity

   \[
   \int_0^1(1-p)^kP_m(2p-1)\,dp
   =(-1)^m\frac{(k!)^2}{(k-m)!(k+m+1)!},\qquad k\ge m,
   \]

   makes every higher-budget difference explicit. Relative to uniform failure, the ratio tends to \(1+\varepsilon(-1)^m\). This changes the leading tail constant without changing the exponent.
3. Analytic densities can also have different exponents. With \(h_m=(-1)^mP_m(2p-1)\), compare \(f_0=2p\) and \(f_\varepsilon=2p+\varepsilon h_m\), where \(0<\varepsilon\le1/[m(m+1)]\). They have identical moments through n, but CDFs x² and εx+O(x²) at zero. This avoids relying on a discrete-versus-continuous distinction.

For a given q, the image of its compact convex set of representing measures under R(k) is a compact interval \(\mathcal I_{n,k}(q)\). For an interior even-order sequence n=2r, its endpoints are attained by the two principal representations with r+1 atoms, one containing 0 and the other 1. The representation containing **0 maximizes failure**, and the one containing **1 minimizes failure**. The implementation obtains nonendpoint nodes by positive-measure Gaussian quadrature for p dF and (1−p)dF, using Golub–Welsch Jacobi eigendecomposition. It avoids a support grid and raw-power Vandermonde solve. Odd orders require their appropriate principal representations, not a blind reuse of the two even-order rules. [§4, Appendix A.3]

A nearly singular numerical matrix does not certify a flat moment extension. An observed zero count does not prove a task has p=0. These qualifications matter particularly for the extraordinarily narrow reported GSM8K interval.

## Sampling uncertainty is a separate layer

The sharp interval conditional on a known q is not a confidence interval. An empirical count histogram need not even lie in the binomial-mixture image. The authors propose projecting a simultaneous confidence region \(\mathcal Q_N\) for the complete count law through the moment map and taking \(\bigcup_{q\in\mathcal Q_N}\mathcal I_{n,k}(q)\), but **do not implement this full procedure**. [§4, Appendix C]

They do implement a coarser valid certificate. In the iid random-task experiment, the number Z of tasks with zero successes is Binomial(N,q₀), where q₀=R(n). For any distribution F and k≥n, Jensen applied to X=(1−p)^n gives

\[
q_0^{k/n}\le R_F(k)\le q_0.
\]

If [a(Z),b(Z)] is a two-sided Clopper–Pearson interval with coverage at least 1−δ, then [a(Z)^(k/n),b(Z)] has the stated finite-sample coverage. It uses just q₀ and can be very wide. It is not the sharp full-histogram projection. Conditional on a fixed heterogeneous labeled task vector, Z is generally Poisson-binomial, so that binomial coverage argument does not automatically apply.

**Independent deduction from the same event, beyond the paper's scalar presentation:** on q₀∈[a,b], this interval contains the entire true \(\mathcal I_{n,k}(q)\), simultaneously for every k≥n, because every law in the fiber has the same q₀. No multiplicity correction over future k is needed. This permits choosing the target k after this fixed-design data collection. It does **not** justify outcome-dependent N, rollout depth n, or within-task stopping. The bound is sharp if only q₀ is retained: a constant p=1−q₀^(1/n) attains the lower endpoint, and q₀δ₀+(1−q₀)δ₁ the upper endpoint.

## Public calibration and numerical evidence

No new language-model generations were run. The authors use Brown et al.'s public 10,000-rollout data, retaining 128 MATH tasks for each Llama-3 model, 127 GSM8K tasks and 140 CodeContests tasks. They create a counterfactual population count law by averaging Binomial(n,p̂ᵢ), where p̂ᵢ is each task's empirical frequency. This removes finite-task uncertainty about the constructed q. The quoted intervals are **population plug-in diagnostics conditional on that convention**. [§5, Appendix D]

At k=1000, Table 1 reports:

| Configuration | Raw reference R(1000) | Sharp interval, n=16 | Sharp interval, n=64 | Relative n=64 width |
|---|---:|---:|---:|---:|
| MATH, Llama-3-8B | .0673 | [.000916, .168] | [.0663, .0683] | .0300 |
| MATH, Llama-3-70B | .0314 | [.0000289, .0755] | [.0308, .0319] | .0359 |
| GSM8K, Llama-3-70B | .00214 | [.00214, .00476] | [.00214, .00214], rounded | 8.84×10^-47 |
| CodeContests, Llama-3-70B | .713 | [.503, .775] | [.713, .713], rounded | 2.93×10^-12 |

The n=16 upper/lower ratios range from about 1.5 to over 2,600. The two rounded n=64 point-looking intervals are not asserted to be exact singleton fibers. In GSM8K, the only empirical probability below .2 is 13/10,000, while the other 126 are above .2. This geometry nearly determines the target at this depth.

A **different** Jeffreys convention uses (c+.5)/(M+1) for the induced count law, and independent Beta(c+.5,M−c+.5) posteriors over the same finite task set for propagated reference uncertainty. Its 95% posterior intervals are not error bars around the raw-frequency convention. At k=1000 the posterior medians are .0656, .0304, .00210 and .681. Fitted Beta–Binomial predictions are .0873, .0434, .0000100 and .723. The GSM prediction is about 210 times below its posterior median and more than 85 times below its lower interval endpoint. The other three forecasts exceed their corresponding upper posterior endpoints. These are diagnostic failures in four specified calibrations, not a universal impossibility theorem for Beta models. CodeContests has 87 of 140 observed zero-success tasks, making the convention important: raw failure .713 versus smoothed .678 and posterior median .681. [§5, Table 2]

The descriptive interval [1/k,1/n] captures some hard-task contribution, but its mass and task count are neither identified quantities nor sufficient summaries of sharp width. A controlled 128-task construction fixes nine hard probabilities and all their relevant diagnostics, while changing 119 easy probabilities. Target failure agrees to 40 digits. Relative interval widths still vary about 28-fold at n=16 and by more than 10^16 at n=64. Thus the whole moment geometry matters. This is an exact-designed numerical stress test, not an additional observed benchmark. [§6, Tables 3–4, Figure 3]

Appendix B reports failures to resolve positive moment matrices at inadequate precision, rather than forcing answers. For n=64, 16 digits resolve none of four public cases, 50 digits resolve two, and 120 and 300 digits resolve all four. Endpoints at the last two precisions reportedly agree to relative 5.6×10^-54. A uniform control at n=64,k=1000 retains relative width .223, while a distinct 127-atom hard-task control has width 1.01×10^-22. These checks address numerical stability, not uncertainty about the true task probabilities.

Appendix C reports 20,000 prospective finite-task simulations under each raw reference. All simulated targets are covered by the coarse 95% certificate. The componentwise median intervals at n=16,k=1000 have upper endpoints .417, .275, .0431 and .899, with tiny lower endpoints. The theoretical coverage comes from the fixed-sample argument, not the all-covered empirical outcome.

## Reproducibility and citation dependencies

The pinned revision `a9f8f73bcd6948a57ed922cba4e48062ef95f553` belongs to **the Hugging Face dataset**, not Brown's GitHub code. The [author project page](https://scalingintelligence.stanford.edu/pubs/large_language_monkeys/) separately links the [generation code](https://github.com/ScalingIntelligence/large_language_monkeys) and [Monkey Business data](https://huggingface.co/datasets/ScalingIntelligence/monkey_business). The [pinned dataset revision](https://huggingface.co/datasets/ScalingIntelligence/monkey_business/commit/a9f8f73bcd6948a57ed922cba4e48062ef95f553) and its API metadata return the exact hash. Appendix D streams Boolean `is_corrects` vectors of length at least 10,000. That dataset field must not be silently replaced by the generation repository's differently named YAML field.

The Beta–Binomial projection minimizes count-law cross-entropy over positive a,b using log coordinates. It uses five specified Nelder–Mead starts and 450 iterations, with 900-iteration and BFGS comparisons. The failure forecast is B(a,b+k)/B(a,b). Reported objective and forecast agreement across starts support optimization stability within this two-parameter fit. They do not validate its extrapolation assumptions.

The source promises task identifiers, counts, moment vectors, residuals, seeds and complete analysis scripts upon publication. No authenticated current analysis-code release was established. Full benchmark recomputation, high-precision principal representations and the fit audit were **not independently replayed**. A separately surfaced repository about pass@k forecasting is not evidence that Singh's scripts are released.

The mathematical dependencies are the Hausdorff moment problem, Chebyshev/principal-representation theory of Krein–Nudelman, Gaussian quadrature and Clopper–Pearson coverage. Related statistical citations distinguish partial identification from interval estimation. Chen et al. supply the direct estimator's lineage, Brown et al. the data, Schaeffer et al. the tail-scaling discussion, and Kazdan et al. the Beta–Binomial forecasting comparison. Their full texts have separate reading statuses. The source's bibliography does not itself authenticate later conference editions.

## Bounded independent checks and unresolved work

Integration by parts in the shifted Rodrigues formula reproduces the factorial identity and its sign. Nine small rational-integral cases agree. For the analytic construction, \(h_m(0)=1\) and \(\|h_m'\|_\infty\le M=m(m+1)\) imply

\[
2p+\varepsilon h_m(p)\ge\varepsilon+(2-\varepsilon M)p
\ge\varepsilon+p>0.
\]

This supplies a global positivity argument for the printed sufficient ε condition. At n=2, m=3, ε=1/12, the perturbed density has moments (1,2/3,1/2), matching 2p, but R(3)=169/1680 instead of 1/10.

The endpoint orientation is independently visible at the uniform n=2 moments (m₁,m₂)=(1/2,1/3). The laws \(\frac14\delta_0+\frac34\delta_{2/3}\) and \(\frac34\delta_{1/3}+\frac14\delta_1\) share q=(1/3,1/3,1/3), while their R(3) values are 5/18 and 2/9. Nonnegative cubic witnesses certify these extrema directly. In contrast, (m₁,m₂)=(1/2,1/4) forces δ₁/₂ by zero variance. These are checks of the claim's exact quantifiers, not a new empirical model.

The principal unresolved method is an implemented finite-sample full-count-law projection. Adaptive evaluation, correlated outputs and changing pipelines remain outside the theorem. Future-group forward KL, observed reset policy design and charged learned state are not established here. Reading Kazdan's available manuscript can clarify its explicit forecasting and allocation assumptions, and Zhang–Amini2610.21363 can test whether a more general current minimax formulation bridges finite moments and learned prediction. No FP theory or experiment is modified by this note.
