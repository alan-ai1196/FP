# Zhang et al. 2026 — predictive curvature, spectral filtering and a learned-subspace comparator

## Source identity and reading boundary

- **Authors:** Bohan Zhang, Zihao Wang, Hengyu Fu and Jason D. Lee.
- **Title:** Neural Networks Learn Generic Multi-Index Models Near Information-Theoretic Limit.
- **Read edition:** [arXiv:2511.15120v2](https://arxiv.org/abs/2511.15120v2), submitted November 19, 2025 and revised February 4, 2026. The PDF title page says February 6, 2026.
- **Primary text:** [85-page PDF](https://arxiv.org/pdf/2511.15120v2) and [versioned TeX source](https://arxiv.org/src/2511.15120v2).
- **Venue evidence:** the arXiv record and [Lee's publication list](https://jasondlee88.github.io/publications.html) identify ICLR 2026 acceptance. The [OpenReview record](https://openreview.net/forum?id=2Q0U2rV2Jz) encountered a verification page and its PDF returned HTTP 403. A separate final OpenReview edition was not compared or credited as read.
- **Reader:** Pro-D, completed November 26, 2026, Asia/Shanghai.
- **Actual coverage:** all 85 PDF pages, main Sections 1–7, Appendices A–C, every printed proof and formula, both figures and captions, acknowledgements, footnotes and references. Targeted TeX checks covered the assumptions, algorithm, moment inverse, parity substitution and learning rates. Original PDF pages 16, 17, 40, 58 and 70 were visually inspected.
- **Provenance:** PDF SHA256 is 4cac61e81bbc41e06987c39b518734eee0804c80bc4ef20a01e85ac085da321d. Source archive SHA256 is bb1632408e6c916a07075e6b640a116a20687ce2b32e432838721846df281fd1.
- **Evidence labels:** the paper's end-to-end rates below are author theorems. The centering identity, quartic example, matrix examples and empirical-subspace comparator are independent analytic deductions. They do not constitute certification of the full neural-network theorem. No training experiment, formal proof replay or source-code reproduction was performed.

## 1. The constructive mechanism

The useful idea is that a predictive loss can expose a low-dimensional feature space through its **label-weighted second-order input statistic**. Near a sufficiently small initialization, first-layer gradient updates become repeated multiplication by that empirical statistic. Reusing the same examples makes this a spectral filter. An intermediate stopping time suppresses the noisy bulk while retaining several signal directions with unequal strengths.

This gives three mathematical tools worth retaining.

1. A loss derivative can act as a nonlinear preprocessing map of the observed label. Its Hermite content can expose directions invisible to the untransformed label.
2. The small-initialization dynamics can be compared with an empirical matrix power without requiring separated eigenvalues inside the signal subspace.
3. After learning a subspace, polynomial prediction can be analyzed through a finite-width comparator, convex readout fitting and a conditional generalization argument.

The last step needs care about which subspace is used. Section 6 develops a constructive comparator on the **empirically recovered subspace**. Its additional prediction error is explicitly bounded. This avoids treating a lower bound on projected feature moments as an inverse bound for the entire feature covariance.

The current constructive-research clarification in coordination commit 47485ff was received before archival. The note retains consequential qualifications but concentrates on the mechanism, usable ingredients and a source-grounded repair. It does not prescribe an FP architecture or modify core research.

## 2. Exact statistical and algorithmic setting

The data are

\[
X\sim N(0,I_d),\qquad Y=f^*(X)=g^*(UX),\qquad UU^\top=I_r.
\]

The latent rank \(r\), polynomial degree \(p\), and Gaussian \(L^2\) bound for \(g^*\) are fixed constants as \(d\) grows. Labels are noiseless. The learner is not given \(U\) or the polynomial coefficients.

The model is

\[
f_\Theta(x)=\sum_{j=1}^m a_j\sigma(w_j^\top x+b_j).
\]

The formal assumptions in Sections 2–3 include all of the following.

| Object | Required condition |
|---|---|
| Activation near initialization | \(\sigma\in C^3\), \(\sigma'(0)=0\), \(\sigma''(0)=1\), and bounded third derivative |
| Loss | Convex in prediction, \(C^2\), zero at the target, bounded first and second prediction derivatives under Assumption 3 |
| Extended loss class | Assumption 3′ permits first derivative growth \(L(1+|t|+|y|)\). The stated extension additionally requires approximation exponent \(\beta=0\) |
| Label statistic | \(\psi(y)=\partial_t\ell(0,y)\), with \(E\psi(Y)=0\) |
| Population signal | \(\Sigma=E[\psi(Y)XX^\top]\) has rank exactly \(r\), positive nonzero eigenvalues, \(\lambda_1=1\), and \(\lambda_r=1/\kappa>0\) |
| Conditioning | \(\kappa\) is bounded independently of \(d\) |
| Scalar approximation | For every monomial, averages of \(\sigma(az+b)\), with \(a\in\{-1,1\}\), \(b\in[-3,3]\), approximate it on \([-1,1]\), with coefficient bound \(O(\rho^{-\beta})\) |
| Initialization | Paired output signs and duplicated first-layer weights give zero initial prediction. Weight radius is at most \(C_\epsilon m^{-1}n^{-1/2}d^{-7/2}(4/5)^{T_1}\) |

The positivity requirement on \(\Sigma\) is stronger than mere nonzero information in every direction. The theorem does not establish that a suitable familiar loss can always be selected automatically. Existence of a label transformation in generative-exponent theory also does not, by itself, establish its realization by a convex loss that fits the original targets.

Algorithm 1 uses two independent datasets, each of size \(n\).

- Stage one repeatedly uses the entire first dataset to train \(W\), with \(a\) fixed and \(b=0\).
- The choice \(\beta_1=1/\eta_1\) cancels the identity term of the gradient update. A special final update rescales the gradient by \(\epsilon_0^{-1}\).
- Biases are redrawn uniformly on \([-3,3]\), output coefficients are reset, and \(W\) is frozen.
- Stage two performs ridge-regularized gradient descent on \(a\), using the independent second dataset.

Thus \(2n\) distinct examples support many gradient passes. The supplied procedure differs in its observation use and update geometry from fresh single-example vanilla SGD. It also differs from joint training of both layers.

The word “agnostic” in the abstract refers here to learning an unknown link and hidden subspace. The formal data model remains realizable and noiseless. There is no proved excess-risk guarantee against arbitrary misspecification or adversarial label noise.

## 3. Author theorem and proof ingredients

### 3.1 The rate and its meaning

For \(T_1=o(\log d)\), Theorem 1 requires

\[
n\gtrsim d(\log d)T_1^2\kappa^{2T_1}
      +d^{1+1/T_1}\kappa^2.
\tag{1}
\]

Its common risk statement is

\[
L(\Theta^{(T)})
\lesssim
\kappa^{4pT_1}(\log d)^{4p+1}
\left(m^{-1/2}+n^{-1/2}\right)^{1/(\beta+1)}.
\tag{2}
\]

For the bounded-derivative loss class, the appendix states the sharper prefactor \(\kappa^{2pT_1}(\log d)^{2p+1}\). The source chooses \(T_1\) of order \(\sqrt{\log d/\log\kappa}\), and sufficiently large subpolynomial width, to obtain vanishing risk with

\[
n=d^{1+o(1)},\quad m=d^{o(1)},\quad
T_2=d^{o(1)},\quad
\text{arithmetic training work}=d^{2+o(1)}.
\]

The paper explicitly uses its tilde notation to suppress **all \(d^{o(1)}\) factors**, including \(\exp(C\sqrt{\log d})\), not only logarithmic factors. This is an exponent-level optimality statement, rather than a sharp proportional-sample threshold. Its \(nd\) lower comparison uses a dense-input reading cost. Bit precision and the cost of representing very small initial weights are outside that accounting.

At \(\kappa=1\), the displayed corollary involving \(\log\kappa\) is undefined. Equation (1) can still be used with a diverging \(T_1=o(\log d)\), or with a fixed condition-number upper bound larger than one. The special case does not justify substituting into a zero denominator.

### 3.2 Why prediction gradients become a spectral filter

Write

\[
\widehat\Sigma=\frac1n\sum_i\psi(Y_i)X_iX_i^\top,
\qquad H=\widehat\Sigma-\Sigma.
\]

Small output and a locally quadratic activation give

\[
\nabla_{w_j}\widehat L
=a_j\widehat\Sigma w_j+\text{controlled nonlinear terms}.
\]

With \(\eta_1\beta_1=1\), the first-layer recursion becomes

\[
w_j^{(t+1)}
=-\eta_1 a_j(\widehat\Sigma+Q_j^{(t)})w_j^{(t)}.
\tag{3}
\]

After the special final scaling, the decoupled approximation is

\[
\widetilde w_j^{(T_1)}
=\epsilon_0^{-1}(-\eta_1a_j)^{T_1}
\widehat\Sigma^{T_1}w_j^{(0)}.
\tag{4}
\]

Appendix A controls the nonlinear matrix perturbations using the small initialization, a bound on the network output, and a multiplicative expansion. For bounded \(\psi\), a sphere-net Bernstein argument gives

\[
\|H\|_{\rm op}\lesssim\sqrt{d/n}.
\]

The random initialization is important in comparing empirical and population powers. In every mixed word containing \(\Sigma\), the rightmost signal factor projects a random vector into a fixed-rank space. That contributes a \(\sqrt{\log d/d}\) factor. The pure-noise word contributes \(\|H\|^{T_1}\). The resulting bound has the form

\[
\|(\widehat\Sigma^{T_1}-\Sigma^{T_1})w\|
\lesssim
\epsilon_0\left[
T_1\gamma\sqrt{\log d/d}+\gamma^{T_1}
\right],
\qquad \gamma\asymp\sqrt{d/n}.
\tag{5}
\]

This argument uses rank and random projection, rather than individual eigenvector gaps. That is a useful proof technique independently of the end-to-end application.

Comparing (5) with the weakest population component \(\epsilon_0\kappa^{-T_1}/\sqrt d\) produces the two terms in (1). More powers suppress the bulk but increase the ratio between the strongest and weakest signal directions. The stopping rule balances these effects within this proof.

The conclusion that more than a constant number of steps is necessary should be restricted to the studied initialization and mechanism, together with the cited one-step comparison. The paper does not prove a universal lower bound against all neural training procedures, preprocessing methods or warm starts.

### 3.3 How the readout analysis is intended to work

Appendix B constructs a polynomial comparator from random features, converts monomials into activation averages through the scalar approximation assumption, and uses Monte Carlo concentration for finite width. Because true neurons interact during stage one, it first uses the decoupled features in (4), then controls their difference from actual trained features.

The final risk decomposition has three components.

1. Comparator approximation on the second dataset.
2. Optimization error and coefficient-norm control under ridge-regularized convex fitting.
3. Generalization of a fixed-feature class, conditional on the independent first-stage data and bias draws.

This split is useful. A hidden difficulty is that the comparator must have both adequate approximation and a controlled coefficient norm. Projected feature coverage alone does not guarantee the latter. Sections 5–6 isolate that issue and provide a constructive alternative at the polynomial-comparator level.

## 4. Independent deductions that make the mechanism more concrete

### 4.1 Centered Hermite statistics remove an isotropic background

Let \(P=U^\top U\), \(Z=UX\), and \(c=E\psi(Y)\). Gaussian orthogonal decomposition gives the exact identity

\[
E[\psi(Y)XX^\top]
=cI_d+
U^\top E[\psi(g^*(Z))(ZZ^\top-I_r)]U.
\tag{6}
\]

The cross terms vanish because the orthogonal Gaussian component is independent of \(Z\). The component outside \(P\) contributes \(c(I-P)\). This proof requires the relevant integrability, not differentiability of the link.

Thus the computable statistic

\[
\widehat S_\psi
=\frac1n\sum_i\psi(Y_i)(X_iX_i^\top-I_d)
\tag{7}
\]

has a population range contained in the hidden subspace even when \(c\ne0\). It differs from the ordinary weighted covariance by the observable scalar \(\bar\psi I_d\).

For bounded \(\psi\), its concentration follows from the covariance bound plus scalar sample-mean concentration:

\[
\|\widehat S_\psi-S_\psi\|_{\rm op}
\le
\|\widehat\Sigma_\psi-\Sigma_\psi\|_{\rm op}
+|\bar\psi-c|.
\]

The leading high-dimensional order remains \(\sqrt{d/n}\) when \(n\gtrsim d\). This identifies a direct observational way to remove the nuisance mean. Equation (7) is a source-grounded statistical construction. Incorporating it into the paper's exact gradient algorithm would require an additional update or loss argument.

### 4.2 An explicit quartic feature revealed by label preprocessing

Let the normalized Hermite polynomial be

\[
h_4(z)=\frac{z^4-6z^2+3}{\sqrt{24}},
\qquad
Y=h_4(Z_1)+h_4(Z_2).
\]

The ordinary second-order label statistic vanishes:

\[
E[Y(XX^\top-I_d)]=0.
\]

Set \(\psi(Y)=Y^2-2\), since \(EY^2=2\). The Hermite recurrence gives

\[
E[h_k(Z)^2(Z^2-1)]=2k.
\]

Consequently,

\[
E[(Y^2-2)(XX^\top-I_d)]
=8(e_1e_1^\top+e_2e_2^\top).
\tag{8}
\]

Off-diagonal entries vanish by coordinate parity. The other diagonal entries vanish by independence. Thus an ordinary observable label transformation reveals the entire two-dimensional signal subspace even though the original label has no degree-two coefficient.

A bounded version is available. Let \(q_R(y)=\min(y^2,R)\) and center it by its mean. Dominated convergence of the relevant Gaussian moments implies that the two signal eigenvalues converge to 8 as \(R\to\infty\). Symmetry keeps the signal block scalar and all other entries zero. Therefore some fixed finite \(R\) gives a positive rank-two statistic with bounded weights. Its sample covariance has the same \(\sqrt{d/n}\) order as the bounded-weight tool in the paper.

This is an illustrative spectral preprocessing construction, not a novelty claim and not a proof that a usual convex loss produces this exact derivative. A subsequent readout can still use the original labels. The paper's generative-exponent motivation explains why this separation between feature acquisition and target fitting can be useful.

## 5. The projected-moment issue

Lemma B.5, page 40 and proof pages 55–58, bounds the moment of **projected** features:

\[
\operatorname{Mat}E[(P h(w))^{\otimes 2k}]
\succeq c_kd^{-k}\lambda_r^{2kT_1}
\Pi_{\operatorname{Sym}^k(S)}.
\tag{9}
\]

Lemma B.6 then uses the pseudoinverse of the **unprojected** moment \(M_k=\operatorname{Mat}E[h(w)^{\otimes2k}]\). Equations (245)–(248) infer target range membership and a controlled inverse quadratic form from (9). That inference is invalid without more structure.

### 5.1 A low-dimensional algebraic witness

For \(k=1\), let \(S=\operatorname{span}(e_1)\), \(v=\cos\theta\,e_1+\sin\theta\,e_2\), and

\[
\Sigma=e_1e_1^\top,\qquad
\widehat\Sigma=vv^\top,\qquad
w\sim\operatorname{Unif}(S^{d-1}).
\]

For every positive integer \(T\),

\[
h(w)=\widehat\Sigma^T w=v(v^\top w),\qquad
M=E[hh^\top]=vv^\top/d.
\]

The perturbation has norm \(\sin\theta\), which can be arbitrarily small, and

\[
PMP=(\cos^2\theta/d)P.
\]

Yet \(e_1\) is outside the range of \(M\) whenever \(\theta\ne0\). No scalar function \(z(w)\) can satisfy \(E[z(w)h(w)]=e_1\), because every such expectation lies in \(\operatorname{span}(v)\).

The issue is not confined to exact singularity. In the displayed two-dimensional plane, set

\[
\widehat\Sigma=
R_\theta\operatorname{diag}(1,s)R_\theta^\top,\quad s>0.
\]

The minimum second moment for exact representation of \(e_1\) is

\[
\inf_{E[zh]=e_1}Ez^2
=e_1^\top M^{-1}e_1
=d\left(\cos^2\theta+s^{-2T}\sin^2\theta\right).
\tag{10}
\]

The projected covariance remains bounded below by \(\cos^2\theta/d\), while (10) can be arbitrarily large. The relevant full inverse depends on the coupling to nuisance coordinates, not only on the projected block.

These examples refute the invoked linear-algebra implication. They do not establish that the paper's actual random-data experiment violates its final learning rate with substantial probability. That stronger claim would require a separate analysis.

## 6. Constructive repair at the polynomial-comparator level

The following two deductions retain the empirical features and replace exact reconstruction of population coordinates by a controlled prediction problem on the recovered subspace. They are independent propositions using the paper's Gaussian, matrix-power and sphere-moment objects.

### 6.1 Approximate the target on the empirical signal subspace

Assume \(\Sigma\) is positive semidefinite of rank \(r\), with smallest nonzero eigenvalue \(\lambda_r\), and

\[
\|\widehat\Sigma-\Sigma\|_{\rm op}\le\gamma<\lambda_r/2.
\]

Let \(Q\) project onto the top \(r\) eigenspace of \(\widehat\Sigma\). If \(V\) is an orthonormal eigenvector matrix for this space, then

\[
(I-P)V=(I-P)(\widehat\Sigma-\Sigma)V
\widehat\Lambda^{-1}.
\]

Weyl's inequality gives \(\widehat\lambda_r\ge\lambda_r-\gamma\). Since \(P,Q\) have the same rank,

\[
\delta:=\|(I-Q)P\|_{\rm op}
=\|(I-P)Q\|_{\rm op}
\le\frac{\gamma}{\lambda_r-\gamma}.
\tag{11}
\]

For any degree-\(p\) polynomial \(f(X)\) depending only on \(PX\), define

\[
f_Q(X)=E[f(X)\mid QX].
\]

This is another polynomial of degree at most \(p\), now supported on \(Q\). Its norm does not increase. More precisely,

\[
E[(f(X)-f_Q(X))^2]
\le
\left[1-(1-\delta^2)^p\right]\operatorname{Var}(f(X))
\le p\delta^2\operatorname{Var}(f(X)).
\tag{12}
\]

**Proof.** Expand \(f=\sum_{k=0}^p I_k(C_k)\) into orthogonal Gaussian chaoses, normalized so \(E[I_k(C)^2]=k!\|C\|_F^2\). Each \(C_k\) is supported on \(S^{\otimes k}\). Gaussian conditioning maps it to \(Q^{\otimes k}C_k\). The minimum singular value of \(Q\) restricted to \(S\) is at least \(\sqrt{1-\delta^2}\). Therefore

\[
\|Q^{\otimes k}C_k\|_F^2
\ge(1-\delta^2)^k\|C_k\|_F^2.
\]

Subtract the squared norms in each orthogonal chaos and sum over \(k\ge1\). This proves (12).

Combining (11) and (12) prices the subspace replacement by

\[
O\!\left(p\kappa^2\gamma^2\operatorname{Var}(f)\right)
\]

when \(\lambda_1=1\) and \(\gamma\le\lambda_r/2\). For bounded-weight covariance estimation this is of order \(p\kappa^2d/n\), up to confidence factors. It does not require exact recovery of every population coordinate.

### 6.2 Build an exact polynomial dual on that recovered subspace

Set \(A=\widehat\Sigma^T\), let \(\mathcal V=\operatorname{range}(A)\), and take

\[
h(w)=Aw,\qquad w\sim\operatorname{Unif}(S^{d-1}).
\]

The recovered signal subspace \(Q\) is contained in \(\mathcal V\), and the singular values of \(A\) on \(Q\) are at least \(\widehat\lambda_r^T\).

For a symmetric degree-\(k\) tensor \(R\) supported on \(Q\), define

\[
M_k=E[h(w)^{\otimes k}(h(w)^{\otimes k})^\top],
\qquad
z_R(w)=\langle R,M_k^\dagger h(w)^{\otimes k}\rangle.
\]

Then

\[
E[z_R(w)(h(w)^\top x)^k]=\langle R,x^{\otimes k}\rangle,
\tag{13}
\]

and

\[
Ez_R(w)^2
\le
\frac{d(d+2)\cdots(d+2k-2)}{k!}
\widehat\lambda_r^{-2kT}\|R\|_F^2.
\tag{14}
\]

**Proof.** On \(\operatorname{Sym}^k(\mathcal V)\), the untransformed sphere moment \(M_{0,k}\) satisfies

\[
M_{0,k}\succeq
\frac{k!}{d(d+2)\cdots(d+2k-2)}I.
\tag{15}
\]

To see this, write a Gaussian vector as an independent radius times a uniform direction. The degree-\(k\) Gaussian chaos of \(\langle B,G^{\otimes k}\rangle\) has squared norm \(k!\|B\|_F^2\). Its lower-degree chaoses add nonnegative squared norms. Divide by the Gaussian radial moment.

The restriction of \(A\) to \(\mathcal V\) is invertible. Tensor congruence gives

\[
M_k=A^{\otimes k}M_{0,k}A^{\otimes k}.
\]

Its range is exactly \(\operatorname{Sym}^k(\mathcal V)\), so \(R\) belongs to that range and (13) follows. Moreover,

\[
\langle R,M_k^\dagger R\rangle
=\langle A^{-\otimes k}R,
M_{0,k}^{-1}A^{-\otimes k}R\rangle.
\]

Use (15) and
\(\|A^{-\otimes k}R\|_F\le
\widehat\lambda_r^{-kT}\|R\|_F\)
to obtain (14).

The coefficient \(z_R(w)\) is a degree-\(k\) polynomial on the sphere. Spherical hypercontractivity additionally gives

\[
\|z_R\|_{L^q}\le(q-1)^{k/2}\|z_R\|_{L^2},
\qquad q\ge2.
\tag{16}
\]

Thus high-probability coefficient truncation can be controlled with logarithmic factors. A uniform operator-norm bound for the inverse on all nuisance directions is unnecessary for (14).

### 6.3 What this repair accomplishes

Equations (12)–(14) separate two costs cleanly.

- Approximation of the true target by a polynomial on an observation-derived subspace costs \(O(p\kappa^2d/n)\) in squared prediction error.
- Representing that polynomial by empirical matrix-power features has a coefficient moment controlled by the retained signal eigenvalues.

All objects used to define the empirical subspace and feature distribution are functions of observed examples. As in a standard approximation argument, the comparator coefficients may depend on the unknown target in the proof. The trained readout must find a predictor through empirical optimization, rather than being supplied those coefficients.

This establishes a constructive polynomial-comparator route. It does not yet establish the paper's complete activation approximation, finite-width, nonlinear-dynamics and optimization bounds with exactly the printed constants or rates.

**Source-grounded research hypothesis:** an end-to-end analysis formulated directly in the empirical eigenspace may avoid the population-versus-empirical eigenvector mixing penalty that contributes \(d(\log d)T_1^2\kappa^{2T_1}\) to (1). A proof would still need bulk suppression, nonlinear perturbation control, activation approximation and a complete accounting of coefficient tails. This is a hypothesis about the source model, not an FP research assignment or a claimed improvement theorem.

## 7. Further qualifications important for use

The following were checked because they affect reuse of the constructive proof. They are not an exhaustive error audit.

### Activation conditions and the illustrations

Assumption 6 is stronger than smoothness near zero. For the cosine activation used in Figure 2,

\[
E_{a,b}[v(a,b)\cos(az+b)]
=A\cos z+B\sin z.
\]

This finite-dimensional closed space cannot approximate arbitrary monomials arbitrarily well on \([-1,1]\). Cosine therefore does not satisfy the displayed scalar approximation assumption. The locally quadratic activation proposed in (9) and Appendix C.3 has a jump in its second derivative at \(\pm1\), and its second derivative at zero is 2. Rescaling fixes the latter, but additional argument is needed to reconcile its smoothness with Assumption 2. Unsmooth absolute and Huber losses likewise require the stated relaxation or a smoothing argument.

These observations delimit theorem coverage. The numerical studies can still illustrate the spectral mechanism outside the literal theorem assumptions.

### Second-stage learning rate

Lemma B.18 and Theorem 2 print
\(\eta_2=U^2/(L\sqrt m\,U^2+2J)\).
The proof on pages 71–72 obtains a smoothness scale \(Lm+J/U^2\) and proceeds with
\(\eta_2=(Lm+J/U^2)^{-1}\).

The feature Hessian is a weighted empirical Gram matrix. Bounded individual feature values allow its largest eigenvalue to scale as \(m\), so the printed \(\sqrt m\) denominator does not follow from that proof. A safe proof-compatible choice uses the actual Gram operator norm, or a constant multiple of \(Lm+J/U^2\). This correction concerns optimization stability and does not supply the missing comparator argument.

### Parity and conditional generalization

Equation (255) replaces the Rademacher multiplier \(a\) in the scalar approximation by \(a^{T_1}\). This substitution is immediate for odd \(T_1\). Even \(T_1\) requires a reparameterization of the coefficient function, which is not given there. Choosing a nearby odd integer preserves the asymptotic time scale but is a change to the stated all-\(T_1\) argument.

Lemma C.6 writes a class in which \(W,b\) vary, while its dimension-free Rademacher calculation treats them as fixed. The fixed-feature interpretation is available in the split-sample application after conditioning on stage one. It should be retained explicitly. A claim uniform over learned \(W\) on the same fitting sample would need a different complexity argument.

The expanded square-loss branch also inherits first-stage concentration arguments originally proved with bounded \(\psi\). Polynomial label tails require their own truncation or concentration accounting. The paper discusses this relaxation, but the displayed bounded-weight proof cannot simply be reused without that step.

## 8. What the experiments actually establish

Figure 1 uses the quadratic target
\((x_1^2+x_2^2/2)/\sqrt{5/2}\), width 4 and quadratic activation. Both layers use Kaiming initialization and are trained with Adam, learning rate 0.005, minibatch 32, for up to 1,000 epochs. The sample exponent is searched over 1.1–1.8 in increments of 0.01. Five seeds are used for each pair. The decreasing empirical threshold is an observation about this procedure, rather than a direct execution of Algorithm 1 or a proof of asymptotic convergence to exponent one.

Figure 2 compares square and Huber losses for \(h_4(x_1)+h_4(x_2)\), with width 4, cosine activation, dimensions 200, 300 and 500, and ten seeds. It reports medians and 30th–70th percentile intervals. The reported alignment is the **maximum** cosine similarity between any neuron and either true direction. It can equal one when only one of the two features has been learned, so it does not establish full-subspace recovery or low prediction error. It does support a narrower observation that the loss choice changes recovery of at least one visible feature in this setup.

No held-out full-subspace audit, independent reproduction or uncertainty analysis beyond the displayed summaries was performed for this note. The general-input central-limit extrapolation in the conclusion is an author conjecture.

## 9. Position in the current literature work

This paper supplies a constructive complement to the fresh-sample SGD study in [the preceding note](BARZILAI-SHAMIR-2026-VANILLA-SGD.md). Reused samples, derivative-based preprocessing, exact weight-decay cancellation, small initialization, a final rescaling and independent readout data are substantive resources. The two papers' conclusions concern different algorithms.

The [Generative Leap](https://proceedings.neurips.cc/paper_files/paper/2025/hash/290056cc784d4825eb8cf5c72f808ebb-Abstract-Conference.html) is a direct recent dependency for the preprocessing and sequential-feature viewpoint. Its abstract and publication identity were screened during this selection. Its full proof is not counted as read here. The claimed generic coverage and low-degree lower bound should be studied in that source before being imported as stronger conclusions.

The present note offers a prediction-driven feature-formation mechanism, useful matrix-power proof tools and a constructive comparator deduction under explicit Gaussian polynomial assumptions. It does not establish autonomous discrete state creation, unknown transition discovery, finite-bit storage laws or compositional reuse in FP. No FP transfer is asserted.
