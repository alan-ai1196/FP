# Prediction Is Not a Sufficient Memory State

## Source, status and actual coverage

Robert Jenkinson Alvarez, **arXiv:2610.13881v1**, submitted October 9, 2026. [Versioned primary record](https://arxiv.org/abs/2610.13881v1) · [PDF](https://arxiv.org/pdf/2610.13881v1) · [TeX archive](https://arxiv.org/src/2610.13881v1). DOI: 10.48550/arXiv.2610.13881. The primary history checked on November 23 lists only v1. No withdrawal, correction or confirmed conference publication was established by the bounded source check. An ICLR 2027 style file in the source does not establish acceptance.

**Fully read, November 23, 2026:** all 35 PDF pages through complete TeX: §§1–9, statements, all Appendices A–N, author footnote, the sole table, all 25 bibliography entries and the compiled bibliography. The appendix order is A–H, then source files numbered 10–14, then `09_scope` as Appendix N. Main/body/appendix TeX and `references.bib` contain 129,994 characters. Original PDF pp. 6, 7, 20, 25, 27, 30, 32 and 34 were visually checked for the principal finite-bit formula, table, quantizer, operator normalization and dense supplementary constructions. There are no figure environments. The main assistant performed all body reading; a source assistant retrieved files and checked metadata only.

Local source: `literature/corpus/pisf_prior_art/2610.13881v1/`. These ignored files are retrieval aids, not additional reading-status records.

**Evidence level:** an ordinary author preprint, complete reading plus the limited independent checks described below. No formal verification, trained-model experiment, or complete independent certification. The author's statement discloses generative-AI assistance with conceptual development, claims, proof writing and literature work, and asserts author review and responsibility. This is not an OpenAI or Anthropic official research release.

## 1. The question is exact future updating, not present prediction quality

A history can determine the same current predictor as another history yet respond differently to a common new observation. The paper identifies which hidden evidence must remain distinguishable when the target is **the specified exact cumulative computation**.

“Prediction” in its title means the current readout. It does not mean a predictive-state representation containing predictions for every possible future test. The paper explicitly acknowledges this distinction and the older future-distinguishability framework.

A prefix encoder is continuous at every fixed history length and maps the complete history-dependent storage into $\mathbb R^m$. Decoders may be arbitrary; fixed parameters and a known clock are allowed. A lower-bound family has one fixed length, so its distinguishing parameters cannot be hidden in the clock. A restricted equal-prediction family can have a smaller prefix summary without admitting a globally valid recurrence of that size.

Three resources remain separate throughout: exact continuous coordinates, finite bits under an explicit error metric, and computation for finding/updating/decoding the state. The main dimension theorems do not bound optimizer runtime.

## 2. Ridge: the predictor omits its design evidence

For features $x_i\in\mathbb R^d$, labels $y_i\in\mathbb R^p$ and $\lambda>0$, the cumulative ridge computation is

\[
C=\lambda I+\sum_i x_ix_i^\top,\qquad
M=\sum_i y_ix_i^\top,\qquad W=MC^{-1}.
\]

Theorem 1 gives exact minimum dimensions:

| Required operation | Continuous coordinates |
|---|---:|
| Every present readout $Wq$ | $dp$ |
| Present readouts and one arbitrary native observation | $dp+s_d$, $s_d=d(d+1)/2$ |
| One continuation on zero-label prefixes, where $W=0$ | $s_d$ |
| Present and continued readouts with unit keys and known $N\ge d$, $d\ge2$ | $dp+s_d-1$ |

The attaining full state is the standard RLS statistic $(C,M)$, or equivalently $(P,W)$ with $P=C^{-1}$. This is not a new regression algorithm.

For one observation $(k,y)$,

\[
W^+=W+(y-Wk)\Phi_P(k)^\top,\qquad
\Phi_P(k)=\frac{Pk}{1+k^\top Pk},\qquad
Pk=\frac{\Phi_P(k)}{1-k^\top\Phi_P(k)}.
\]

Equal states first identify $W$ from present queries. The common appended label $y=Wk+e_1$ exposes $\Phi_P(k)$; basis keys expose $P$, hence $C,M$. Every $C\succ\lambda I$ and arbitrary $M$ is continuously realizable with $d$ examples using $X=(C-\lambda I)^{1/2}$ and $Y=MX^{-\top}$. This gives an open distinguishable family of dimension $dp+s_d$. Invariance of domain prohibits compressing it continuously into fewer coordinates. The unit-key proof supplies a local chart on a fixed-trace Gram slice; it does not merely subtract a coordinate without proving reachability.

The explicit collision uses $d=2,p=1,\lambda=1/4$ and zero labels with

\[
C_\pm=\begin{pmatrix}1&\pm1/2\\\pm1/2&1\end{pmatrix}.
\]

Appending $(e_1,1)$ yields rows $(4/7,\mp2/7)$. At $q=e_2$, any merged state has average squared error at least $4/49$. The raw zero-initialized update $S^+=S+\beta(y-Sk)k^\top$ remains zero on either prefix, even with a key-dependent scalar gate. Extra channels, replay or hidden states can avoid the collision and must be included in the resource account. This example is not a theorem against every DeltaNet or test-time learner.

## 3. Native observations, polynomial closure and fixed predictors

The general model minimizes

\[
F_h(w)=R(w)+\sum_{(x,y)\in h}\rho(x^\top w-y).
\]

Here $R$ is fixed, globally smooth and $\lambda$-strongly convex; $\rho$ is globally smooth, convex and nonconstant; real features and real labels are unrestricted; observations have unit weights. Define the vector-valued **function** space

\[
g_{x,y}(w)=x\rho'(x^\top w-y),\qquad
\mathcal G_\rho=\operatorname{span}\{g_{x,y}\},\quad r=\dim\mathcal G_\rho.
\]

This is a space of gradient profiles over all $w$, not the $d$ entries of a gradient at one optimum.

Theorem 2 identifies equality after every one-example continuation with equality of accumulated gradient functions. Choose $t_0$ with $c=\rho'(t_0)\ne0$. For any proposed optimum $w$, the ordinary observation

\[
x=-\nabla F_h(w)/c,\qquad y=x^\top w-t_0
\]

makes the continued gradient vanish at $w$. Strong convexity makes this the unique optimum. Applying the same observation to another history identifies its old gradient at $w$. This is an existence argument for a distinguishing input; the decoder receives no gradient oracle.

The unweighted lower bound is substantive. Observation derivatives span the profile space: finite-dimensional spaces are closed under pointwise limits via separating evaluations, and integrating tangents from a zero-feature observation recovers every profile. Independent observation tangents and finitely many evaluations give an invertible Jacobian for a fixed-length family. The inverse-function theorem supplies an open distinguishable chart. The dimension obstruction then gives $m\ge r$; arbitrarily large charts cover $r=\infty$. Additive coefficients in a fixed gradient-function basis attain finite $r$.

Theorem 3 concludes that fixed finite exact state exists **iff the residual loss is polynomial** under these hypotheses. For degree $D\ge1$,

\[
r_D(d)=\binom{d+D}{D}-1.
\]

The proof restricts features to a scaled coordinate direction, yielding a finite-dimensional space invariant under translations and positive dilations. Differentiation $\mathsf D$ is an endomorphism and is similar to $a\mathsf D$ for every $a>0$. Its finite complex spectrum is therefore zero; Cayley–Hamilton makes differentiation nilpotent, forcing a polynomial. Conversely, translated powers and varying features span all multivariate polynomials through degree $D$; differentiation removes just the constant term.

The present optimum needs $d$ coordinates. On any family with a fixed optimum $w_0$, the exact continuation-prefix dimension is $r_D(d)-d$. Appending a balancing observation to an open profile chart fixes $w_0$ while its derivative can remove at most $d$ directions. For the matching upper bound, evaluation of the profile at $w_0$ imposes exactly $d$ independent affine constraints. Nonpolynomial losses retain arbitrarily many hidden directions even at a fixed optimum. The smaller count is not a global recurrence after the predictor moves.

**Domain boundary:** with scalar feature fixed to $x=1$ and $\rho(t)=e^t$, the profile is $e^w\sum_i e^{-y_i}$ and one coordinate suffices. Finite feature/label dictionaries can also have finite spans. Thus neither the name of a nonpolynomial loss nor a finite vocabulary by itself invokes the unrestricted-feature impossibility theorem.

## 4. Bounded logistic observations still hide exact information

A separate construction uses scalar logistic regression, regularizer $\lambda w^2/2$, and $2N$ ordinary paired examples $(a_i,+1),(a_i,-1)$ with $1<a_1<\cdots<a_N<2$. Every current optimum is zero, while

\[
F_a'(w)=\lambda w+\sum_i a_i\tanh(a_iw/2).
\]

For any $b_0>0$, exact responses to all next examples $(b,+1)$, $0<b<b_0$, require at least $N$ continuous coordinates (Theorem 4). The analytic implicit-function theorem gives a nonconstant response interval near $b=0$. Equal responses identify the old analytic gradient on an interval, hence everywhere. Positive exponential tails identify the smallest feature scale; subtracting its whole contribution recursively identifies the ordered tuple. Large arguments in this uniqueness proof are not large-feature inputs supplied to the learner.

Theorem 5 strengthens this to equal finite jets. Fixing the first $K$ even power sums leaves a local $(N-K)$-dimensional manifold, by a Vandermonde Jacobian. Values and all objective derivatives through order $2K+1$ agree at zero, yet continuation responses distinguish every pair. The $K=0$ case fixes value and first derivative.

This proves exact insufficiency of any fixed local jet. It supplies no history-length-independent numerical error floor: analytic identification can be ill conditioned. Approximate summaries and coresets are not ruled out.

## 5. The finite-bit result has a specified distribution and normalization

Theorem 6 uses a different model and does not infer robustness from topological dimension. Let $d\ge2$, $a>18r>0$, $b=a+18r<1/\lambda$, and

\[
\mathcal K_d=\{H\in\operatorname{Sym}_d:
\|H\|_F\le r\sqrt d,\ \|H\|_{\rm op}\le18r\},\qquad P=aI+H,
\]

with $H$ uniform on this body. It is realized by $d$ zero-label ridge observations. Condition numbers and individual feature norms are bounded independently of $d$ when $a,r,\lambda$ are fixed. The code is formed **before** independent unit-sphere $k,q$ arrive; the next label is one and the target is $f_P(k,q)=q^\top Pk/(1+k^\top Pk)$.

For any code with at most $2^B$ values and an unrestricted decoder, including randomized encoders and independent shared randomness, the optimal mean squared risk obeys

\[
\frac{r^2}{4d(1+b)^4}2^{-2B/s_d}
\le \mathcal R_B\le
\frac{16(1+b)^2r^2}{d}2^{-2B/s_d}.
\]

The raw error scale is $1/d$. The dimension-dependent statement concerns normalized error $d\mathcal R_B/r^2$, not a constant language-model error under arbitrary data.

Proof components, all read in Appendix E:

1. Gain inversion and forward Lipschitz control give response-distance bounds proportional to $\|P-Q\|_F^2/d^2$. Each isotropic unit probe supplies one factor $1/d$.
2. A Gaussian sphere-net bound and a chi-square lower-tail bound show that the well-conditioned body contains at least half the Frobenius ball's volume.
3. A unit-density moment inequality bounds distortion for **randomized** finite codes by $(s/(s+2))(V/v_s)^{2/s}2^{-2B/s}$. It uses the conditional code probabilities as bounded densities, so no deterministic-cell assumption is hidden.
4. Two independent posterior matrix draws turn arbitrary-decoder Bayes risk into half the response-distance variance. This transfers matrix distortion to prediction risk without assuming a coherent matrix decoder.
5. A covering codebook attains the exponent. Its centers are coherent matrices; it is an offline existence construction, not an efficient streaming quantizer.

The separate worst-case bound in E.7 is deterministic, uniform over unit probes, and uses an operator-norm ball. Its quantifiers differ from the main average randomized statement.

## 6. Attention and controlled approximation

For positive kernel attention, the state before normalization is

\[
Z_h(q)=\sum_i t_i\kappa(q,k_i),\quad
B_h(q)=\sum_i t_i\kappa(q,k_i)v_i,\quad f_h=B_h/Z_h.
\]

Appending one fixed key with either zero or $e_1$ as its value gives two alternative continued readouts. Their difference recovers $Z_h$, then $B_h$. These are alternatives from the same prefix, not a two-token sequential experiment.

If the kernel-section span has finite dimension $r_\kappa$, positively weighted histories require exactly $r_\kappa(p+1)$ continuous coordinates. Independent sections, variable positive weights and independently variable weighted values give the lower chart; additive numerator/denominator coefficients attain it. The positive-weight hypothesis is not silently applied to all unweighted kernels.

For **unweighted** exponential attention on an open real query domain, a length-$N$ prefix with distinct keys needs $N(d+p)$ coordinates; the zero-valued family still needs $Nd$. Independent real exponentials identify the key multiset; disjoint key neighborhoods give continuous indexing and an open chart. Repeated keys, finite key dictionaries and restricted query sets can change the count. These are exact continuous results, not approximate streaming-attention impossibility claims.

The approximation propositions preserve evidence rather than just current outputs:

- A uniform old-gradient-profile error $\delta$ plus returned-root residual $\eta$ gives new-optimum error at most $(\delta+\eta)/\lambda$ under a common convex continuation. Existence of such an approximate root is a hypothesis.
- A polynomial approximation to $\rho'$ accumulates gradient error at most $\varepsilon\sum_i\|x_i\|$; growth with history mass is retained.
- Relative denominator error $\delta<1$, numerator error $\eta Z$ and value bound $V$ give continued attention error at most $\theta(\eta+\delta V)/(1-\theta\delta)$, where $\theta=Z/(Z+A)$ and $A$ is new kernel mass.
- Predictor-plus-Hessian supplies a controlled local approximation under Hessian/gradient Lipschitz conditions. For a small scaled appended loss the error is second order; that approximation does not create an exact globally sufficient jet.

## 7. The substantial operator supplement has separate claims

Appendices H–M are part of the paper and were read in full. They do not constitute trained-model evidence.

| Appendix | Object, result and proof structure | Boundary |
|---|---|---|
| H | A current linear observation $Lv$ permits another $Mv$ iff $\ker L\subseteq\ker M$. Joint observable dimension is $\operatorname{rank}(L,M)$. Positive-operator probe maps have an explicit adjoint/Gram map; an antisymmetric two-column target demonstrates incompatible individually attainable outputs. | A static observability result, not automatically a recurrence theorem. |
| I | Positive effects $W_i$ sum to identity. Entropy maximization uniquely gives $W_i=\exp((S_i-L)/\tau)$ with a shared Hermitian normalizer. Interior positivity, matrix divided differences and an implicit-function argument establish analytic normalization. Relative scores equal log-effect differences, and their generated feature algebras agree. | Common shifts cancel even when noncommuting. Fixed iteration counts, uniform conditioning and free score/basis generation are not established. |
| J | For a fixed observation map, entropy-normalized query coordinates analytically cover the relative interior of the feasible response body. The Hessian is $L\mathcal H^{-1}L^*$; a fiber entropy minimizer proves surjectivity. Fenchel–Young calibration and a regularized inverse give explicit response bounds. | Response dimension is $\operatorname{rank}L$; it does not retain directions in $\ker L$ needed by later probes. The decoder-dimension statement uses local Lipschitz regularity and differs from the main continuous-encoder argument. |
| K | A transverse-covariance support formula characterizes the response body; Schur complements and a polar maximizer construct attaining effects. The two-source body is a Euclidean ball, with an $O(d)$ binary formula. A three-source equilateral witness reaches $9/8$, beyond convexified pairwise bodies. A radial coordinate alternative has the same binary range. | Response completeness does not uniquely require the entropy parameterization, or preserve a teacher action on new payloads. |
| L | Above a fixed baseline, exact independent scalar value-channel cost equals the real CP rank of the residual slice tensor. Every finite interior positive action also has an $s_d$-channel finite-logit compiler, via a sign-aligning congruence and signed rank-one value maps; a spanning action requires that many channels. A separate Borsuk–Ulam argument gives a continuous contextual bottleneck for $Px$. | Channels are not physical heads. Signed output maps are permitted; source probabilities are positive. Probability generation, cancellation, conditioning and action identification remain costs. Context retained by the bottleneck decoder does not allow a raw-payload bypass. |
| M | Classical linear unbiased fusion stores unnormalized precision and information. Even an identical complete normalized action can hide $s_d$ precision coordinates exposed by the next sensor. Conditional expectation onto an operator algebra gives a squared-risk projection. A trine example separates positive commuting effects, their convex hull and unrestricted effects. | Fixed linear unbiased gains and stated noise moments are essential. Signed projected scalar compilers escape the commuting-positive comparison; routing risk does not itself imply a memory lower bound. |

Appendix N restates observation domains, resource models and intended verification. The bibliography makes the main dependencies explicit: invariance of domain; finite-dimensional function-space theory; predictive-state representations; approximate sufficient statistics; streaming bounds; matrix entropy/quantum information; Fenchel–Young losses; tensor rank; and Borsuk–Ulam. Reading their use here does not mark those sources fully read. Recent cited methods include MesaNet, test-time regression, curvature-aware DeltaNet and 2026 streaming-attention bounds; they remain separate candidates.

## 8. Independent checks, evidence gaps and use limits

The following checks were performed separately from summarizing author claims:

- Recomputed the two ridge inverse/gain vectors with exact rational arithmetic: $(4/7,-2/7)$ and $(4/7,2/7)$, hence the claimed $4/49$ merged-state risk. This checks the finite example, not the general dimension theorem.
- Followed the native steering construction, observation-tangent chart and balancing rank argument. Their essential inputs are unrestricted real observations, a nonzero derivative of the loss, strong convexity, and encoder continuity. No counterexample was found within those stated conditions during this limited examination.
- Re-derived the finite-bit normalization: two isotropic probes give $d^{-2}$; a Frobenius covering radius $r\sqrt d$ has squared size $r^2d$; together they give $r^2/d$. The upper construction printed on PDF p. 20 agrees with Theorem 6 on p. 6. There is no missing $d^2$ factor in those displayed steps.
- Checked the conditional-variance reduction's role: posterior matrices are independent draws given a code, while future probes are independent of that code's construction. Removing the pre-probe encoding restriction changes the problem.
- Checked the distinction between current-response quotient, coherent shared action, scalar execution width and continuation evidence in the operator supplement. None supplies an unrestricted neural-architecture separation.

These are bounded independent checks, not a complete new proof or a formal replay. The appendix names `checks/verify.py`, `checks/verify_operators.py` and a supplementary README. They are **not present in the retrieved arXiv TeX archive**; its non-TeX files are bibliography/style/build files. This session did not run those author scripts. A bounded check of the author homepage did not locate a link explicitly belonging to this supplement. This is an acquisition gap, not a claim that the material does not exist; described passing checks cannot be treated as observed results.

The paper reports no trained-model benchmark or downstream gain. The bounded version/replication search established no reviewed independent validation of this preprint. This is a search limit, not evidence that none exists. Its mathematical claims should be cited with the assumptions and the above evidence level.

For FP, the relevant distinction is a precise warning about identifying states solely by current outputs when a declared later operation can separate them. It does not establish a bound for FP's finite raw-token log-loss experiment or a universal comparison over arbitrary decision families. Astra's concurrent `62ddbdd` target concerns bounded decision losses and a shared reconstruction distribution across contexts; this paper does not prove that proposed necessary-and-sufficient decision certificate. No core theory or experiment is changed here.

The new decision-sufficiency screen selected van Rooyen’s October 2026 preprint Beyond Blackwell (2611.00510v1) next, because its abstract directly addresses constrained randomization and quantitative decision comparison. Its body remains unread at this checkpoint. TTT-E2E v2 remains a recent adaptive-state candidate. Historical citations are lookup dependencies only, not a full-reading queue.
