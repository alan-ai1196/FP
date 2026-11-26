# Barzilai–Shamir 2026 — actual SGD noise, subspace alignment and the missing mean term

Pro-D. Completed 2026-11-26, Asia/Shanghai. Independent statistical-learning research.

## Sources, edition and actual reading

Daniel Barzilai and Ohad Shamir, **Limitations of SGD for Multi-Index Models Beyond Statistical Queries**, COLT 2026, PMLR 336:559–612, 54 physical pages.

- [Official publication record](https://proceedings.mlr.press/v336/barzilai26a.html).
- [Official final PDF](https://raw.githubusercontent.com/mlresearch/v336/main/assets/barzilai26a/barzilai26a.pdf), SHA256 `18ca9a4c4caee5746112fdcb73a242f2f6542a745680a736bdb46ecb4a50917c`.
- [arXiv 2602.05704v2](https://arxiv.org/abs/2602.05704v2), revised June 24, 2026 at 14:40:41 UTC, following the February 5 v1. [Versioned source](https://arxiv.org/src/2602.05704v2).

**Reading completed:** all 54 official pages, main §§1–6, Appendices A–D, all proofs, formulas, three scientific footnotes, contents and 53 references. There are no scientific figures, tables or experiments. Official pages 7, 12, 45 and 50 were additionally viewed as rendered images. Selected v2 TeX passages were checked for initialization scaling, conditioning, the target mean and application hypotheses. This is full official-PDF reading, not a claim of reading every raw source line or every cited paper.

The 54-page v2 PDF has SHA256 `b2f09034dcdb306289a51284d47bccaf166a533f15c1dfaaea6fc8e35af29c88`. The complete extracted-text comparison found only its arXiv watermark and a reflowed paragraph on p12. One final edition is counted. The inspected primary records showed no withdrawal or separate correction. No explicit AI-assistance disclosure occurs in the manuscript. This is peer-reviewed author research, not an official OpenAI or Anthropic release.

## Assessment

The useful mechanism separates population drift from the actual, history-dependent SGD noise, then compares movement in a specified direction with growth of the weight norm. Its Hermite-subspace estimates are useful conditional tools. The printed information-exponent application loses the target's degree-zero component. This is consequential: the explicit ordinary-SGD construction below violates Theorem 5 under its stated assumptions. Centering the target repairs the particular Hermite step, without constituting a full certification of the revised learning theorem.

The general alignment statement also needs careful initialization and probability wording. Deep-network applicability remains conditional on a trajectory-wide gradient condition number. Neither a small alignment nor a small relative correlation supplies an absolute prediction-risk bound without controlling output scale.

## 1. Objects and the mechanism being studied

The predictor accesses an input only through a learned first linear map,

\[
f_\theta(x)=h_\theta(Wx),\qquad W\in\mathbb R^{m\times d},
\qquad f_*(x)=\phi(Ux),\quad U\in\mathbb R^{p\times d}.
\]

The updates use fresh iid inputs, batch size one, a constant positive step size and the actual sample gradient. The concrete applications use correlation loss \(\ell=-f_\theta f_*\). They do not establish the same rates for cross-entropy, empirical risk with data reuse, momentum or Adam. The proposed minibatch extension on p4 remains a prospective statement.

Write \(P_W=W^\dagger W\), \(P_U=U^\dagger U\) and

\[
\rho(W,U)=\|P_WP_U\|_{\rm op}.
\]

This measures the strongest shared direction between two row spaces. It is invariant under invertible changes of basis inside either row space. It measures neither physical recurrent states nor the size of a discrete representation.

For \(a_t=\nabla_{W_{t-1}x_t}\ell(\theta_{t-1},x_t)\), the first-layer increment is \(-\eta a_tx_t^\top\). Assuming \(\|a_t\|\le G\), define

\[
M_t=\mathbb E[a_ta_t^\top\mid\mathcal F_{t-1}],
\qquad
\kappa_T=\frac{G^2}{\inf_{t\le T}\lambda_{\min}(M_t)}.
\]

This is a uniform lower bound on all directions of the conditional second moment, expressed relative to a global envelope. It can be infinite even when every stochastic gradient is bounded. In particular, low-dimensional dependence of \(a_t\) alone does not bound it.

**Independent width observation.** Since \(\operatorname{tr}(M_t)\le G^2\),

\[
\lambda_{\min}(M_t)\le G^2/m,
\qquad \boxed{\kappa_T\ge m.}
\]

A dimension-independent bound is therefore compatible with fixed width, but cannot also be uniform over arbitrary growing widths under this normalization. The neuronwise two-layer applications avoid this full-vector parameter by applying a width-one argument to each row. The rows share the same data stream, so a union bound is the relevant device. Their noise trajectories need not be independent.

Theorem 2 combines a small-gradient condition \(\|\nabla_W L(\theta)\|_F\le\psi(\rho(W,U))\) with sub-Gaussian input projections, input-norm concentration, initialization control and a bounded \(\kappa_T\). Its scale is

\[
\rho_t\lesssim\sqrt{\frac{\bar\kappa mp\log(Tdp/\delta)}d},
\quad
T\lesssim\psi\!\left(C\sqrt{\frac{\bar\kappa mp\log(Tdp/\delta)}d}\right)^{-2},
\]

with the separate restrictions

\[
d\gtrsim\bar\kappa^2m^2\log^2(Tdp/\delta),
\qquad
\eta\lesssim\frac1{\bar\kappa^2\sqrt{md\log(Tdp/\delta)}}.
\]

Appendix B controls projected martingale sums and accumulated squared increments, handles their cross terms, passes through a finite sphere net and bootstraps the gradient bound. The lower norm bound prevents a small numerator from being turned into large alignment merely by shrinking the denominator. This directly addresses anisotropic sample noise rather than replacing it by an adversarial SQ response.

## 2. A missing degree-zero coefficient

Definition 4 starts at positive degree,

\[
k_* =\min\{k\ge1:\mathbb E[f_*(X)H_k(X)]\ne0\}.
\]

Consequently it places no restriction on \(B_0=\mathbb E f_*\). Lemma 34 on p50 nevertheless replaces the sum beginning at zero by a sum beginning at \(k_*\). Theorems 5 and 6 do not add a mean-zero target hypothesis, and the loss used in their proofs is the uncentered product.

An exact local counterexample is \(W=e_1^\top\), \(U=e_2^\top\), \(f_W\equiv1\), and \(g_U=1+\sin X_2\). Here \(\rho=0\), \(k_*=1\), and \(\mathbb E[f_Wg_U]=1\). Lemma 34's correlation upper bound is zero. All functions have the required Gaussian square integrability and weak differentiability.

The gradient conclusion also needs the missing component. Take \(f_W(X)=\operatorname{ReLU}(w^\top X)\), \(w=e_1\), and \(g_U(X)=1+\tfrac12\cos X_2\). Then \(k_*=2\), \(\rho=0\), but

\[
\mathbb E[\nabla_w f_W(X)g_U(X)]
=\frac{1+\tfrac12e^{-1/2}}{\sqrt{2\pi}}e_1\ne0.
\]

The omitted signal is radial and changes the correlation loss without identifying the target direction.

### A counterexample to the actual SGD application

The following construction checks the update rule as well as the functional inequality. It is an independent asymptotic counterexample to Theorem 5 as printed.

Let \(u\) be any unit vector and take

\[
X_t\overset{\rm iid}{\sim}N(0,I_d),
\quad g(X)=1+\tfrac12\cos(u^\top X),
\quad f_w(X)=\operatorname{ReLU}(w^\top X),
\quad w_0\sim N(0,I_d/d).
\]

The target is smooth, lies between \(a=1/2\) and \(b=3/2\), and has bounded derivative. Its first Hermite coefficient vanishes by symmetry. Its normalized second coefficient along \(u\) is \(-e^{-1/2}/(2\sqrt2)\), so \(k_*=2\). ReLU satisfies Assumption 4 with \(G_1=1\) and \(K_\sigma=2\).

Fix \(\epsilon=1/10\) and any fixed failure probability below one half. Set

\[
\eta=d^{-3/4},\qquad t_d=\lfloor d^{3/4}\rfloor.
\]

For all sufficiently large \(d\), this step size is below the displayed \(\widetilde\Theta(d^{-1/2})\) threshold, and \(t_d\) is below the claimed \(\widetilde\Theta(d)\) horizon. Fixed source constants and polylogarithms cannot reverse these polynomial separations.

The actual correlation-SGD recursion is

\[
w_t=w_{t-1}+\eta g(X_t)\mathbf1_{w_{t-1}^\top X_t>0}X_t.
\]

Its cross term in the squared norm is nonnegative. With
\(Y_t=\mathbf1_{w_{t-1}^\top X_t>0}\|X_t\|^2\),

\[
\|w_t\|^2\ge\|w_0\|^2+\eta^2a^2\sum_{j=1}^tY_j.
\]

For every nonzero past weight, Gaussian reflection symmetry gives

\[
\mathbb E[Y_t\mid\mathcal F_{t-1}]=d/2,
\qquad
\operatorname{Var}(Y_t\mid\mathcal F_{t-1})=d^2/4+d.
\]

The weights stay nonzero because their norm cannot decrease. Martingale orthogonality and Chebyshev therefore give

\[
\Pr\!\left(\sum_{j=1}^tY_j<td/4\right)
\le\frac{4+16/d}{t}.
\]

Hence, with probability tending to one, \(\|w_{t_d}\|\ge(a/2)d^{1/8}(1+o(1))\), whereas \(\|w_0\|=O(1)\).

For \(r=\|w\|\), Gaussian ReLU moments give \(\mathbb E f_w=r/\sqrt{2\pi}\) and \(\|f_w\|_2=r/\sqrt2\). Positivity of the target yields

\[
|L(w_t)-L(w_0)|
\ge\frac{a\|w_t\|-b\|w_0\|}{\sqrt{2\pi}}
\]

once the numerator is positive. But Theorem 5's proposed right side equals

\[
\frac{\epsilon\|g\|_2}{\sqrt2}
\bigl(\|w_t\|+\|w_0\|\bigr),
\quad
\|g\|_2^2=1+e^{-1/2}+\frac{1+e^{-2}}8.
\]

The limiting ratio of our lower bound to \(\|g\|_2(\|f_{w_t}\|_2+\|f_{w_0}\|_2)\) is at least

\[
\frac{1/2}{\sqrt\pi\sqrt{1+e^{-1/2}+(1+e^{-2})/8}}>0.21>\epsilon.
\]

Thus the asserted loss bound fails with probability tending to one at an allowed iteration. This construction even has \(\kappa_T\le18\): the scalar stochastic coefficient is bounded by \(b\), and its conditional second moment is at least \(a^2/2\). An exploding gradient condition number does not explain the failure.

### What centering repairs

Write \(g=\mu+g_0\), with \(\mathbb E g_0=0\). The valid decomposition is

\[
\mathbb E[f_Wg]=\mu\mathbb E f_W+\operatorname{Cov}(f_W,g).
\]

The Hermite projection argument gives the centered estimate

\[
|\operatorname{Cov}(f_W,g)|
\le\operatorname{sd}(f_W)\operatorname{sd}(g)\rho^{k_*}.
\]

Similarly the gradient contains \(\mu\mathbb E\nabla_W f_W\) in addition to the centered term. A loss using \(g_0\) removes it. Estimating and subtracting an unknown mean would change the learning interface and needs its own analysis. This note does not silently substitute that procedure for the source's vanilla SGD.

## 3. Probability and initialization boundaries

### Trajectory condition versus conditional probability

Let \(A=\{\kappa_T\le\bar\kappa\}\) and let \(B\) denote the desired simultaneous alignment conclusion. The concentration argument on p30 constructs an unconditional event of probability at least \(1-\delta\) on which a second-moment premise implies the norm bound. Continuing the net and bootstrap argument supports the form

\[
\Pr(A\cap B^c)\le\delta.
\]

This is different from the printed \(\Pr(B\mid A)\ge1-\delta\). Without a lower bound on \(\Pr(A)\), the immediate conditional result is only \(1-\delta/\Pr(A)\). Conditioning the whole history on \(A\) does not preserve the original martingale law automatically. If \(A\) holds almost surely, or if the width-one bootstrap proves \(\Pr(A^c)\le\delta_1\), the high-probability implication can be used with the appropriate failure-budget addition. This identifies the quantifier supported by the proof, not a counterexample to every corrected alignment result.

### Initialization scale in Assumption 2

The printed tail on p7 is \(2\exp[-\gamma^2/(dK_3^2)]\), while Lemmas 15–16 use sub-Gaussian scale \(K_3/\sqrt d\). The latter needs an exponent proportional to \(-d\gamma^2/K_3^2\).

For an exact separation, take each entry independently to be \(+1\) or \(-1\), each with probability \(1/(2d)\), and zero otherwise. It has mean zero, variance \(1/d\), and satisfies the printed tail with \(K_3=1\) for \(d\ge2\). For one row, \(\|w_0\|^2\) is \(\operatorname{Binomial}(d,1/d)\), with zero probability tending to \(e^{-1}\). The claimed concentration near one does not follow. The explicit Gaussian initializations in Theorems 3, 5 and 6 satisfy the intended stronger condition.

Lemma 15(2) additionally puts “for all” directions inside one simultaneous event. Its proof only supplies a fixed-direction bound, later extended to a finite net by a union bound. A literal simultaneous bound for every direction would fail by taking the direction parallel to the realized nonzero \(w_0\). The fixed-direction/net version preserves the intended argument.

## 4. Retained tools and remaining application scope

The Gaussian tensor-support identity in Lemma 25 and the complete coefficient bound in Lemma 26 retain degree zero and survive the local checks:

\[
A_k=P_W^{\otimes k}A_k,
\qquad
|\mathbb E[f_Wg_U]|
\le\|f_W\|_2
\left(\sum_{k\ge0}\|B_k\|_F^2\rho^{2k}\right)^{1/2}.
\]

The tensor formulation makes the target's entire spectrum visible. The sinusoidal target of Theorem 3 is centered, so the nonzero-mean counterexample does not apply to it. Its displayed conclusion controls correlation change relative to a sum of neuron norms over \(\exp(d^{1/3})\) steps. To obtain an absolute loss plateau one must bound those norms. For bounded activations this is immediate. For a Lipschitz activation and the specified finite horizon, the update envelope and Gaussian input-norm event also give at most \(\exp(O(d^{1/3}))\) growth, which is dominated by the displayed \(\exp(-Cd)\) factor for polynomial width. This is a bounded consequence, not an audit of every constant in that theorem.

For the polynomial-horizon information-exponent application, uncontrolled scale remains a separate concern even after centering. Its norm-weighted correlation conclusion should not be paraphrased as a uniform constant-error or classification lower bound.

Three local application qualifications are explicit:

- The logistic sigmoid does not satisfy the derivative-energy floor in Assumption 4 over all Gaussian scales. If \(\sigma(z)=(1+e^{-z})^{-1}\), dominated convergence gives \(\mathbb E[\sigma'(sZ)^2]\to0\) as \(s\to\infty\). Appendix D.1 actually proves the floor for **softplus**, whose derivative is sigmoid. ReLU, leaky ReLU and sine have the stated useful nonvanishing-energy property. GeLU also has such a property, without needing the displayed numerical choice of its constant.
- For a product of orthogonal, centered one-dimensional functions with first nonzero Hermite degrees \(r_i\), independence gives \(k_*=\sum_i r_i\). The source's \(k_*=p\) needs every \(r_i=1\), or equivalently nonzero first Gaussian coefficient. Smoothness, boundedness and zero mean alone give only \(k_*\ge p\).
- For the p11 example \(g(X)=(u^\top X)^2e^{-(u^\top X)^2}\), let \(s=\|u\|\). Its second coefficient along the unit direction is proportional to \(2s^2(1-s^2)/(1+2s^2)^{5/2}\). The degree-four assertion needs \(s=1\). For other positive scales the information exponent is two. Its nonzero mean still needs separate treatment.

### An independent Gaussian span bound

There is a short geometric baseline for the source's \(\Omega(d)\) discussion. Every first-layer row produced by fresh-sample SGD belongs to

\[
S_t=\operatorname{span}\{\text{rows of }W_0,X_1,\ldots,X_t\}.
\]

With iid Gaussian initialization and inputs, \(S_T\) is a Haar subspace of dimension \(r=\min(m+T,d)\). For a fixed target subspace of rank \(q\),

\[
\mathbb E\|P_{S_T}P_U\|_F^2=qr/d.
\]

Nested spans, the operator/Frobenius comparison and Markov's inequality give

\[
\Pr\!\left(\max_{t\le T}\|P_{W_t}P_U\|_{\rm op}>\epsilon\right)
\le\frac{q\min(m+T,d)}{d\epsilon^2}.
\]

The coefficients may depend on all preceding labels and iterates. No independence of them is used. This baseline needs neither a condition-number bound nor a step-size restriction. It loses logarithmic/probability sharpness and only addresses alignment. It neither repairs the noncentered loss claim nor supplies the stronger high-information-exponent horizon. No novelty claim is made.

## 5. SQ comparison, evidence status and FP boundary

Appendix A's coordinate-target example separates adversarial Euclidean mean tolerance from the sample noise actually observed. The orthogonality/Bessel calculation bounds the total squared difference from a common reference response. Its vector SQ oracle has a worst-case query/tolerance obstruction, whereas actual samples preserve a noiseless coordinate and permit identification with logarithmically many examples. The scalar-SQ, vector-oracle and sample interfaces must remain distinct. No general theorem identifying all practical SGD with SQ is established or needed.

The full reading supports a useful stochastic-geometry method and Gaussian Hermite tools. The independent checks establish the missing-mean obstruction, the ordinary ReLU-SGD counterexample, the initialization-scale distinction, the conditional-probability qualification, the width floor for \(\kappa_T\), and the elementary Gaussian span bound. They are not a whole-paper certification or a formal proof-assistant replay. No numerical experiment, training run or unrelated historical full reading was performed.

No FP core definition, architecture, learning rule, experiment or implementation is changed. The transferable knowledge is a set of conditioned mathematical tools and a warning about which loss component is actually controlled. The paper supplies no autonomous finite-state discovery or finite-bit memory theorem. No substantive FP transfer is proposed.
