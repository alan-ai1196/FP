# Two Sample Sizes in Test-Time LLM Ensembling: Buffered ERM and Minimax Theory

## Edition and coverage

Zhi Zhang and Arash A. Amini, UCLA, **arXiv:2610.21363v1**, submitted October 15, 2026 at 06:41:37 UTC. The current primary history checked November 24 contains only v1. No journal or conference acceptance was established. The authors disclose sustained use of OpenAI and Anthropic models for literature searches, estimator design, proof development/checking and writing, with authors taking responsibility. This is **not an official OpenAI or Anthropic release**. [Record](https://arxiv.org/abs/2610.21363v1) · [PDF](https://arxiv.org/pdf/2610.21363v1) · [Source](https://arxiv.org/src/2610.21363v1)

The main reader covered all **58 pages** through the complete active 4,229-line TeX, §§1–7, Appendices A–G, every formula and proof, both figures including all three PDF assets, the empirical table and unnumbered rate table, the author-contact footnote, acknowledgments and 21 references. There are no ordinary body footnotes. Figures were inspected directly and selected dense PDF layouts checked on pp. 3, 21, 27, 39, 51 and 56. The current metadata abstract differs slightly in wording from the manuscript abstract, and both were read. Retrieved files are under `literature/corpus/pisf_prior_art/2610.21363v1/`.

Supporting work was limited to source/version retrieval, a bounded independent Appendix D check, and a narrow citation lookup. Main-body reading was not delegated. Complete reading does not certify every theorem. No model generations, numerical dual construction, optimization implementation or formal proof were replayed. The deposited source contains TeX and figures but no research code, and no author-linked public code was established in the bounded search.

## Question, target and assumptions

The paper studies learning a **single global vector of voting weights** for K fixed language models. There are Q iid labeled training questions, each with a designated gold answer and between 2 and A candidate answers. Each model supplies N independent generations per training question. Conditional independence holds across question/model/generation triples. Total training generations are KQN.

For weights w in the probability simplex, the answer law is \(p_w=\sum_iw_ip_i\). Define

\[
M_q(w)=p_w(a^\star(q)\mid q)-\max_{a\ne a^\star(q)}p_w(a\mid q),
\qquad R(w)=\Pr\{M_q(w)\le0\}.
\]

This **clean risk** is the error of the ideal infinite-generation modal answer. All ties count as errors. The benchmark consists of population draws, and the learner observes question identities as well as their gold answers and generations. The source assumes a clean-risk minimizer \(w^\star\) for its theorem. The target is not pass@k coverage, finite-budget vote optimality, a calibrated predictive probability, or cumulative log loss. A correct answer with positive probability suffices for eventual coverage, while ideal voting requires that answer to be the unique mode. [§§1–2]

The general theorem imposes only a one-sided margin condition at the chosen optimum:

\[
\Pr\{0<M_q(w^\star)\le t\}\le C_m t^\beta,
\qquad0<t\le t_0.
\]

It does not impose that condition at the learned weights. The scalar minimax class later uses a stronger two-sided condition. Neither should be silently substituted for the other.

## General buffered ERM and finite deployment

The learner replaces each answer distribution by its empirical frequencies and minimizes the fraction of questions with empirical margin at most a positive buffer. With

\[
\varepsilon_N=\sqrt{2\log(8KAQ/\delta)/N},
\]

coordinatewise Hoeffding bounds and a union bound give uniform training-margin error at most εN. Consequently, for every sampled question and every weight,

\[
\mathbf1\{M\le0\}\le
\mathbf1\{\widehat M\le\varepsilon_N\}\le
\mathbf1\{M\le2\varepsilon_N\}.
\]

This is the mechanism that prevents a favorable generation fluctuation from becoming a certified empirical success. Uniform convergence over clean threshold losses follows by counting weak sign patterns of at most Q(A−1) affine comparisons in K−1 dimensions, including lower-dimensional faces where ties occur. The growth bound is \(\sum_{r=0}^{K-1}2^r{H\choose r}\), followed by a direct exponential-moment symmetrization argument. [Theorem 2.1, Appendix A]

If 2εN≤t₀, the resulting high-probability excess risk is

\[
R(\widehat w)-R(w^\star)
\le2\mathfrak v_Q(\delta)+C_m(2\varepsilon_N)^\beta,
\qquad
\mathfrak v_Q(\delta)
=C_0\sqrt{\frac{(K-1)\log(eAQ)+\log(8/\delta)}Q}.
\]

For fixed K,A and margin constants, this is \(\widetilde O(Q^{-1/2}+N^{-\beta/2})\). A faster than parametric N exponent reflects small probability near the decision boundary, not faster estimation of every answer probability. The Q term remains. The buffer does not require β. The piecewise-constant optimization can use the previous Best-of-∞ mixed-integer formulation with shifted thresholds. An empirical optimization gap η adds η to the risk bound, but the paper gives no general efficient optimization theorem.

For deployment, independently choose a model from the learned weights for each of T new generations. With a reserve r>0 fixed before training, use the larger training buffer εN+r. Provided 2εN+r≤t₀,

\[
R_T^{\mathrm{dep}}(\widehat w)-R(w^\star)
\le2\mathfrak v_Q+C_m(2\varepsilon_N+r)^\beta
 +(A-1)e^{-Tr^2/2}.
\]

Taking \(r=\sqrt{2/T}\log(eAT)\) yields the additional \(\widetilde O(T^{-\beta/2})\) term. The comparison is still with the **optimal clean risk**, not the best ensemble under the same finite T or price constraint. Mean generation cost \(\sum_iw_ic_i\) is introduced, but matched-accuracy cost savings and adaptive stopping are left open. [Corollary 2.2, Appendix A.3]

## Scalar submodel and exact minimax characterization

Two models, two answers and an antisymmetric advantage Z∈[−1,1] give gold probabilities (1+Z)/2 and (1−Z)/2. If w=(t,1−t), then \(M=(2t-1)Z\). Every t>1/2 has the same clean decisions, every t<1/2 the opposite decisions, and t=1/2 ties everywhere. Thus only a sign decision remains. Its target and wrong-side regret are

\[
\theta(G)=\int\operatorname{sgn}(z)\,dG(z),
\qquad |\theta(G)|\mathbf1\{\widehat\sigma\theta(G)<0\}.
\]

The sufficient count \(S=X_1+N-X_2\) satisfies

\[
S\mid Z\sim\operatorname{Bin}(n,(1+Z)/2),\qquad n=2N.
\]

Writing KₙG for the marginal count law, Q counts are iid from KₙG if question identities are discarded. The class is

\[
\mathcal G_{\beta,L}=
\{G:G([-t,t])\le Lt^\beta\text{ for all }0<t\le1\},
\qquad\beta>0,\ L\ge1.
\]

It has no atom at zero. It is convex, reflection invariant and weakly compact. Uniform control near zero makes the discontinuous sign functional continuous on this class. The restriction L≥1 is necessary at t=1, and **L=1 still permits a rich class**.

With the convention \(h^2(p,q)=\sum_k(\sqrt{p_k}-\sqrt{q_k})^2\), let

\[
\omega_{n,\beta,L}(\epsilon)=
\sup\{|\theta(G)-\theta(H)|:
 G,H\in\mathcal G_{\beta,L},\ h(K_nG,K_nH)\le\epsilon\}.
\]

Theorem 4.1 establishes, for all positive integers Q,n and universal comparison constants,

\[
c\omega(Q^{-1/2})\le\mathcal R^{\mathrm{dec}}_{Q,n}
\le\mathcal R^{\mathrm{abs}}_{Q,n}\le C\omega(Q^{-1/2}).
\]

For the upper bound, the compact convex image \((K_nG,\theta(G))\) is treated as a categorical observation model with a linear target. The proof constructs robust affinity tests between convex target-level sets. A sample-split interval search reduces the interval length by 2/3 at each stage, uses fresh data at each adaptive comparison, and budgets all blocks within Q. Its explicit absolute-risk bound is \((7/2)\omega(32/\sqrt Q)\). Convexity implies \(\omega(\epsilon_2)\le(\epsilon_2/\epsilon_1)^2\omega(\epsilon_1)\), absorbing the numerical radius constant.

For a decision lower bound, a generic hard pair may have target values of the same sign. Reflection symmetrization replaces it by \((G+H^\dagger)/2\) and \((H+G^\dagger)/2\), with opposite targets and no larger Hellinger distance. Product-Hellinger control and Le Cam testing then give the required regret. This extra step is essential to transferring a functional-estimation lower bound to a sign decision. [Appendix B]

## Exact moment ambiguity and spectral estimation

The binomial count law identifies exactly the first n moments. The zero-radius modulus obeys

\[
\omega_{n,\beta,L}(0)\asymp_{\beta,L}n^{-\beta}.
\]

This is a **worst-pair width over the class**, not an assertion that every observed moment fiber has that width. The upper proof smooths sign(cos θ) with a positive finite-frequency Jackson kernel. The resulting bounded polynomial Pₙ has localized error \(C_s\min\{1,(n|z|)^{-s}\}\). Integrating dyadic shells under the margin assumption, with s>β, gives O(n^-β).

For the lower proof, the canonical measure \(d\mu_\beta=(\beta/2)|z|^{\beta-1}dz\) has weighted best L₁ sign-approximation error \(E_n(\beta)\asymp n^{-\beta}\). The reverse inequality imports Kopotun's weighted inverse theorem. Applying it at a larger degree Mn, bounding low-degree errors by the already proved upper bound, and using monotonicity for the rest extracts a pointwise lower bound. Hahn–Banach duality supplies an odd bounded hₙ that annihilates every polynomial through degree n and attains Eₙ. The positive measures (1±hₙ)μ have equal moments and opposite targets. A common symmetric endpoint mixture enforces the printed margin-constant bound. [Theorem 4.2, Appendix E]

A separate hard-margin pair supported on {−1,+1} gives the unavoidable Q^-1/2 lower bound: each latent sign is observed perfectly, but the population imbalance still must be learned. A rare near-boundary atom also gives \((Qn)^{-\beta/(\beta+2)}\), but the stronger spectral obstruction dominates it wherever that term improves asymptotically on both endpoints. [Proposition 4.3, Appendix C]

The sign-then-aggregate estimator has absolute risk \(O(Q^{-1/2}+n^{-\beta/2})\). Conditional Hoeffding error \(e^{-nz^2/2}\), integrated under the two-sided margin bound, gives its bias. A pooled estimator retains full counts: for a degree-d polynomial P, expand

\[
P(z)=\sum_{k=0}^na_k(P){n\choose k}
 ((1+z)/2)^k((1-z)/2)^{n-k},
\qquad\widehat\theta_P=Q^{-1}\sum_ja_{S_j}(P).
\]

It is unbiased for ∫P dG. Absolute risk is bounded by integrated approximation error plus half the coefficient range divided by √Q. A conservative Chebyshev conversion gives coefficient size O(7.5^d).

The sharper spectral calculation uses **uniform latent p only as an auxiliary reference**, not as a restriction on the unknown G. The conditional-expectation operator Tₙ and its adjoint produce the Bernstein–Durrmeyer operator, with shifted Legendre eigenfunctions and

\[
\lambda_{j,n}=\frac{n!(n+1)!}{(n-j)!(n+j+1)!},
\qquad \kappa_{d,n}=\lambda_{d,n}^{-1/2}.
\]

Parseval gives the exact normalized coefficient norm \(\sum_{j\le d}c_j^2/\lambda_{j,n}\), and bounding its maximum coordinate yields

\[
\mathcal R^{\mathrm{dec}}_{Q,n}
\lesssim_{\beta,L}\inf_{1\le d\le n}
\left\{d^{-\beta}+
\frac{\min(7.5^d,\sqrt{n+1}\,\kappa_{d,n})}{\sqrt Q}\right\}.
\]

For d≤n/2, log κ is of order d(d+1)/n. At full degree, \(\kappa_{n,n}\asymp2^nn^{-1/4}\). The extra √(n+1) factor is part of the **proved** upper bound, not an omitted logarithm. [§5, Appendix F]

For 0<β≤1, the lower construction cancels low Legendre modes and attenuates the remaining ones through the same spectrum. The baseline transformed density \(\beta|2p-1|^{\beta-1}\) is bounded below by β, which permits Hellinger control. For β>1/2 it is also square-integrable, improving the lower-pair radius from O((n+1)/κ₍d+1,n₎) to O(1/κ₍d+1,n₎). The first condition explains why the currently proved middle lower theorem stops at β=1. [§6, Appendix G]

## Proved rate regions and the conjecture

Here n=2N. Constants depend on the stated margin parameters, and the middle result also on fixed η>0.

| Region | Proved scalar minimax order | General-ensemble consequence |
|---|---|---|
| Q≤c n^β | Q^-1/2 | Buffered ERM matches the transferred lower bound up to logarithms, when its threshold condition holds. |
| n^(β+1+η)≤Q≤exp(cη n), 0<β≤1, sufficiently large n | (n log Q)^(-β/2) | This lower bound transfers. Matching pooled upper procedure is proved only in the scalar submodel. |
| Q≥C 4^n n^(2β+1/2) | n^-β | The lower bound transfers. Attainment at this scale remains a scalar upper result. |

In the polynomial-Q portion of the middle range, general buffered ERM is within a logarithmic factor of the transferred lower bound. This statement must not be generalized to arbitrary subexponential Q. For Q=exp(N^a), 0<a<1, the compared bounds have ratio N^(aβ), polynomial in N even though it is polylogarithmic in Q. For Q exponential in N, the general buffer theorem may cease to guarantee a vanishing finite-generation term.

**Conjecture 6.4**, not a proved full rate formula, removes √(n+1) and posits \(\inf_d\{d^{-\beta}+\kappa_{d,n}/\sqrt Q\}\). It predicts a transition based on log(eQ/n^β), all β>0, and the unresolved strip immediately above Q≈n^β. Proving it requires both stronger lower-pair indistinguishability and a sharper robust variance bound for the approximating polynomial. The exact modulus characterization is a theorem even though its proposed complete closed-form evaluation is not.

## What observing the question changes

The source carefully distinguishes sufficient reduction of raw generations to (q,S) from the further removal of q. For lower bounds it allows any measurable deterministic map Z:[0,1]→[−1,1], with known nonatomic uniform question distribution and only the pushforward margin condition.

Appendix D approximates each scalar law by equal-weight outward quantiles, preserving the same L even at L=1 and changing θ by at most 1/M. Atoms are assigned once to M equal-mass question cells using a uniformly random permutation. Every supported environment remains a deterministic map throughout the experiment. Conditioning away collisions of question-cell indices and independent comparison-atom indices makes the augmented experiments agree. Their TV discrepancy is at most \(3\alpha_{Q,M}\), with \(\alpha\le Q(Q-1)/(2M)\). Taking M arbitrarily large transfers the scalar lower bound with c₀=1/64 and c₁=1/16. Neutral additional models add no information and preserve the one-sided margin at a best vertex. [Theorem 4.4, Corollaries 4.5–4.6]

**Independent clarification of the quantifiers:** if two fixed maps have the same complete population joint law of (q,S), then

\[
\mathbb E[S\mid q]=n(1+Z(q))/2
\]

identifies Z almost everywhere for n≥1. The observed-question lower bound therefore concerns a **uniform minimax problem over unrestricted maps**, not literal nonidentification of two fixed maps in the complete joint experiment. For each finite Q,n, the construction may choose a finer M and average over two different families of deterministic maps. It does not claim question identities are useless on every instance. A countable-string version also needs a distribution-free class with arbitrarily large support. It does not directly impose the same floor on a known fixed-size question bank where repeated questions accumulate information, structured question features, or actively selected queries.

The supporting independent check found no failure of the stated Appendix D argument. Its exact M=4,Q=2 augmented-law enumeration gives TV=3/8, below the printed bound 3/4. The transfer proof actually bounds its final TV by 11/64, leaving slack in the declared constants. The L=1 uniform-law discretization with M=3 gives atoms −2/3, 2/3 and 1 and attains the stated target-error bound 1/M. These are bounded checks, not a certification of all other proofs.

## Empirical content, independent example and limits

The sole real-generation illustration is AIME 2024 I Problem 6, with 25 generations each from Gemma 3 12B and Llama 4 Maverick at temperature .8. All 50 responses reportedly completed boxed answers below their caps. The individual empirical modes are wrong answers with frequencies .24 and .52. The equal mixture gives the gold answer 294 frequency .32, exceeding the largest competing .28. This is an illustration on one selected question. It does not estimate clean rankings, generalization improvement, minimax rate, or cost savings.

Figure 1 depicts a normalized smooth tilted density and its n=12 count law. Figure 2 is a numerical dual-pair illustration with β=2,n=7, showing complementary density shells and overlapping count laws. It is not an experimental rate validation or a formal exact-arithmetic certificate. No broad benchmark study or released implementation is supplied.

An **independent explicit instance** checks the moment mechanism at a physically admissible scalar depth n=2. Set β=2, L=1, \(d\mu=|z|dz\), \(a=2^{-1/3}\), and let h(z) equal sign(z) for |z|≤a and −sign(z) otherwise. Then G±=(1±h)μ are probability laws with radial mass t², common first moment zero and common second moment 1/2. Hence their two-trial count laws are exactly

\[
K_2G_+=K_2G_-=(3/8,1/4,3/8),
\]

while \(\theta(G_\pm)=\pm(2^{1/3}-1)\). Normalization, equal moments and target separation follow by direct piecewise integration. This verifies a nontrivial L=1 count-only ambiguity without the numerical figure or the imported asymptotic inverse theorem. It does not prove the all-n sharp rate.

## Scoped check of the weighted approximation dependency

The [author-hosted final Kopotun journal PDF](https://home.cc.umanitoba.ca/~kopotunk/Publications/k-singular.pdf), *Journal of Approximation Theory* 198 (2015), 24–62, [DOI](https://doi.org/10.1016/j.jat.2015.05.003), was checked only for the hypotheses needed here. Actual coverage is the weighted-norm/doubling definitions and Definition 2.1/Remark 2.2 on printed pp. 25–27, Example 2.7 and Remark 2.10 on pp. 31–32, §3 definitions and Eq. (3.1) on pp. 32–33, and the Theorem 9.1 statement on p. 53. Main reader also inspected the original formula layouts on pp. 33 and 53. Its theorem proof, remaining sections and bibliography were not read. This source remains **scoped**, not fully read.

The original theorem explicitly allows p=1 and all power weights |x|^(β−1) with β>0. It does not require an additional Muckenhoupt condition. Choosing integer r>β is permitted and is used by Zhang–Amini's absorption step. The complete modulus includes a local degree-<r approximation term. Its difference operator requires the entire stencil interval to stay in the allowed region, so the main-part term vanishes for sign away from zero. The remaining local term is exactly the integral on [−2A(t+t²),2A(t+t²)] and has order t^β by scaling.

There is a minor **degree-index qualification** in Zhang–Amini's displayed inverse inequality. Kopotun's Eₖ uses degree strictly less than k. With \(e_j=\inf_{\deg P\le j}\|f-P\|_{1,w}\), the exact translated inequality is

\[
\omega_\varphi^r(f,A,m^{-1})_{1,w}
\le C m^{-r}\sum_{j=0}^{m-1}(j+1)^{r-1}e_j(f).
\]

The source acknowledges a one-degree shift but displays a sum starting with e₁. That is not the literal general-function theorem: for r=1 and f(x)=x all displayed eₖ, k≥1, vanish while the first complete modulus is positive. Keeping the correct shifted indices repairs the present sign argument directly. At m=Mn, the early part is O(1+n^(r−β)) and the remaining part O(m^r eₙ), so r>β still yields the same n^-β conclusion. This qualification does not overturn the stated identification rate. It is a primary-statement check and a short index repair, not an independent proof of Kopotun's theorem.

The substantive open items are matching pooled procedures for general ensembles, the first transition and β>1 middle theory, adaptation of polynomial degree to unknown β, finite-deployment optimality at a common budget, and adaptive generation allocation. The source solves a global voting decision under fixed independent training counts. It does not supply an observed-reset policy, a total future-forward-KL theorem, or an accounting theorem for learned packet size and live predictive state. No such FP transfer is asserted here.
