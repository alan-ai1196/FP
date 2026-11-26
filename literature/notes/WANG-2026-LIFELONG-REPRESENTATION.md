# Wang, Zhang and Vinayak — learning a representation only when its task head fails

## Edition, provenance and actual reading

**Primary edition.** Zhi Wang, Chicheng Zhang and Ramya Korlakai Vinayak, *Bridging Lifelong and Multi-Task Representation Learning: An Algorithm and a Complexity Measure*, ALT 2026, PMLR 313:1–44, February 23–26, 2026.

- [Official record and bibliography](https://proceedings.mlr.press/v313/wang26c.html).
- [Official 44-page PDF](https://raw.githubusercontent.com/mlresearch/v313/main/assets/wang26c/wang26c.pdf).
- [OpenReview attachment](https://openreview.net/attachment?id=EHfKvTC0Vs&name=pdf).
- [Earlier arXiv 2511.01847v1](https://arxiv.org/abs/2511.01847v1), submitted November 3, 2025 at 18:54:56 UTC, 36 pages, with the different title ending *via Algorithm and Complexity Measure*.
- [Earlier complete TeX](https://arxiv.org/src/2511.01847v1).

Pro-D personally read all 44 pages of the official edition on November 27, 2026, Shanghai time. Coverage includes Sections 1–8, Appendices A–D, all definitions, statements and proofs, both algorithms, all four figures, the numbered table, footnotes, acknowledgements and references. Original PDF pages 2, 5, 7, 14, 15, 16, 17, 27 and 30 were visually inspected. In particular, the new-task threshold in Definition 7 is **epsilon divided by two**, not twice epsilon. PDF text extraction can reverse this fraction.

The earlier arXiv edition received metadata, abstract, task-independence definition and linear/logistic example comparison only. Its full body and proofs were not read or aligned. Its input/head normalization and logistic conditional specification differ from the final. There is no second full-reading credit.

SHA256:

- Official PDF: f035c3f16242588b8dd30a1c3f2ec64b6869bd49064250db02bc0a07cbd398d8.
- Earlier PDF: 5ecfff6eabe397b308bafa4f43afb6edef53a9616e968755d1e3bc18d8a392c7.
- Earlier TeX archive: efa7f408b0683de1d1792fdd2720c1dfc10ec8877fab58d8d591959112319c38.

The results below distinguish source theorems, source experiments and independent analytic consequences. No code was audited, experiment rerun or theorem formally certified. No explicit AI-assistance disclosure was found in the read manuscript. Actual use is undetermined.

## 1. The constructive contribution and its interface

The paper gives a concrete reduction from sequential representation acquisition to two optimization subroutines:

1. Freeze the current representation and fit a new task head on a small fresh sample.
2. If its empirical loss is too high, collect a larger sample and jointly refit one representation plus separate heads on a buffer of selected tasks.

The buffer contains tasks that exposed a deficiency of a previously maintained representation, together with an initial anchor task. The proof turns those failures into an independence sequence. A complexity measure of that sequence bounds how often the expensive joint optimization is needed.

This is a useful acquisition mechanism with an explicit trigger and retained evidence. The optimization subroutine is a general global multi-task ERM oracle. The paper does not supply a polynomial-time implementation for arbitrary neural representation classes, a rule that adds new computational primitives, or a guarantee for unknown task boundaries.

### Statistical model

Tasks have laws

\[
P_t=P_{f_t^*\circ h^*},\qquad
P_g(x,y)=P_X(x)P_{Y\mid X}(y\mid x;g),
\]

with one unknown shared \(h^*\in\mathcal H\), heads \(f_t^*\in\mathcal F\), a common input marginal and a bounded loss \(\ell\in[0,1]\). The generating function is Bayes optimal for its task law and loss. The composite class must satisfy the source's measurability/permissibility condition.

The task sequence need not be drawn iid from a task environment. The source allows adversarial task choices consistent with a shared representation. Its proof uses sample tapes and uniform bounds over selected subsets of the \(T\) task distributions. I retain that stated model without adding a guarantee against an unrestricted adversary that can inspect and choose tasks from the learner's hidden sample tapes.

For the current task the learner can request iid samples in multiple rounds. It then outputs a predictor and moves on. A previous task is never requested again as the same task. The objective is that each predictor is accurate when produced:

\[
\Pr\!\left\{\forall t\le T:
L_{P_t}(\widehat f_t\circ\widehat h_t)-L_{P_t}(f_t^*\circ h^*)\le\epsilon
\right\}\ge1-\delta.
\]

It does not require the final representation, combined with all old heads, to preserve every earlier task. Nor does its buffer-size bound count the cost of storing every emitted model snapshot.

Define the representation approximation error

\[
\mathcal E(h,P_g)=\inf_{f\in\mathcal F}L_{P_g}(f\circ h)-L_{P_g}(g).
\]

All these errors are nonnegative under well specification. This nonnegativity is used when a bound on the sum of buffered errors implies a bound for the current task. Fully agnostic misspecification is left open.

### Noise information is a supplied resource

Assumption 3 supplies the Bayes risk \(\kappa_t=L_{P_t}(f_t^*\circ h^*)\). The head test compares empirical risk with \(\kappa_t+3\epsilon/4\). A known upper bound \(\nu_t\) instead yields an absolute-risk guarantee relative to \(\nu_t\). Its excess over the actual Bayes risk includes \(\nu_t-\kappa_t\).

Proposition 19 and Appendix A.1 show why this information matters. For Gaussian linear regression and a supplied subspace of dimension at most \(d/2\), distinguishing a pure-noise task from a task with almost all signal outside that subspace can require \(\Omega(\sqrt d)\) observations when the noise level is unknown. Both constructions have unit-variance response marginals. The proof reduces to earlier variance-testing lower bounds. Those historical sources were not independently fully read here.

This is a lower bound for that representation-quality test. It is not a universal impossibility theorem for learning every representation without a known noise level.

## 2. Task-eluder dimension and the actual update algorithm

### Definition 7, with the fraction read correctly

For a fixed center \(h\), a task head \(f_n\) is epsilon-independent of \(f_1,\ldots,f_{n-1}\) when a competing \(h'\) satisfies

\[
\sum_{i<n}\mathcal E(h',P_{f_i\circ h})\le\epsilon,
\qquad
\mathcal E(h',P_{f_n\circ h})>\epsilon/2.
\tag{1}
\]

The task-eluder dimension \(D=\operatorname{TEdim}(\mathcal H,\mathcal F,\epsilon)\) is the supremum over \(h\) of the longest such sequence. It is a fixed-scale, center-dependent representation discrimination quantity, not the parameter dimension of \(\mathcal H\).

Proposition 9 bounds it by \(2\min(|\mathcal H|,|\mathcal F|)\) for finite classes. A witness or repeated task cannot support three positions, because the first two errors already exceed the allowed old-task sum.

Appendix A.3 explains why replacing the sum in (1) by the maximum can fail. Repeat one noiseless Gaussian halfspace task forever and choose a rotated representation whose best error is a number in \((\epsilon/2,\epsilon]\). Every earlier individual error is acceptable and the current error is still above the failure threshold. The same witness works at every step. For the nontrivial small-error regime the displayed rotated construction therefore gives an infinite pointwise-independence sequence.

There is no contradiction with compactness or finite positive-gap packing. The earlier-task threshold epsilon is **larger** than the new-task threshold epsilon/2, so this definition imposes no separation between repeated targets. The aggregate condition supplies the missing accounting.

### Algorithm 1

Start with capacity \(N=1\), learn the first task by ERM from \(m_N\) samples, and retain those samples. At a later task:

- Collect \(\widetilde m\) fresh samples and optimize its head with the representation frozen.
- If the head's empirical loss is at most \(\kappa_t+3\epsilon/4\), emit it.
- Otherwise, add a larger fresh sample to the buffer and optimize a shared representation and all buffered heads jointly.
- When the buffer is already at capacity, double \(N\) and clear it before retaining the new failure task.

Algorithm 2 gives the version with supplied task-eluder dimension, without this doubling procedure.

For an exact head ERM and a uniform deviation of at most \(\epsilon/4\), a failed test implies \(\mathcal E(\widehat h,P_t)>\epsilon/2\). Multi-task ERM is trained accurately enough that the sum of errors on buffered tasks is at most epsilon. Thus its next failure has precisely the witness structure in (1).

The samples from successful tasks can be discarded. This gives a finite witness buffer for controlling future updates. It does not prove that the representation has been uniquely identified, that all successful past tasks remain solved by later representations, or that its coordinates equal an underlying ground truth.

## 3. Author sample bounds and their meaning

Let \(C_H(a)\) and \(C_F(a)\) denote the loss-induced representation and head covering capacities in Section 4.1. Baxter's uniform multi-task bound gives average excess epsilon-zero with per-task sample count of order

\[
\frac{1}{n\epsilon_0^2}
\left[
\log C_H(\epsilon_0/64)+n\log C_F(\epsilon_0/64)+\log(1/\delta_0)
\right].
\tag{2}
\]

The factor \(1/n\) in representation acquisition is useful, but the algorithm needs an **aggregate** epsilon bound over the selected tasks. It therefore sets the average target at order \(\epsilon/N\), which increases the required per-task sample count.

Theorem 14 and its explicit Appendix B restatement choose, suppressing confidence and task-subset logarithms,

\[
m_N=\widetilde O\!\left(
\frac{N}{\epsilon^2}
\left[
\log C_H(\epsilon/(64N))+N\log C_F(\epsilon/(64N))
\right]\right),
\]

\[
\widetilde m=\widetilde O\!\left(
\epsilon^{-2}\log C_F(\epsilon/128)\right).
\]

The source obtains \(O(D)\) representation updates and total samples

\[
\widetilde O\!\left[
\frac{T}{\epsilon^2}\log C_F(\epsilon/128)
+\frac{D^2}{\epsilon^2}
\left(
\log C_H(\epsilon/(128D))
+D\log C_F(\epsilon/(128D))
\right)\right].
\tag{3}
\]

The second term also bounds the retained sample buffer up to suppressed factors. Its logarithmic dependence on \(T\) and confidence should not be described as literally constant bits of memory.

The exact numerical update count in the appendix is not needed for this note's use of (3). For a conservative implementation one can use \(D+1\) to include the unconditional initial anchor, including the degenerate \(D=0\) case, and bound the geometric doubling sum by \(O(D+1)\). The independent construction below states its own count rather than depending on the printed sharp constant.

### Linear and logistic instances

The final edition uses \(\|X\|\le\sqrt d\), well-conditioned second moment, and \(h_B(x)=B^\top x\), \(B^\top B=I_k\). Its regression heads have norm at most \(1/(2\sqrt d)\), with bounded independent mean-zero noise and loss \((y'-y)^2/4\). The noise variance \(\kappa\) therefore corresponds to Bayes risk \(\kappa/4\), not \(\kappa\).

The logistic heads are \(\sigma(w^\top z)\), with \(\|w\|\le1/(4\sqrt d)\), and Bernoulli conditional probability equal to this head output. The logits are bounded by \(1/4\), so log loss is bounded and uniformly curved on the specified domain.

Propositions 15–16 give

\[
\log C_F(a)=O(k\log(1/a)),\quad
\log C_H(a)=O(dk\log(1/a)),\quad
D=O(k\log(1/\epsilon)).
\]

Consequently (3) becomes

\[
\widetilde O\!\left((kT+dk^3)/\epsilon^2\right).
\tag{4}
\]

The displayed rates are not claimed sharp for these special models. The supplied-head-normalization also matters. For example, the regression signal has second moment \(O(1/d)\). A fixed epsilon target can eventually be met without resolving that small signal. Equation (4) alone is not a dimension-free result at fixed nonvanishing target amplitude.

The arXiv predecessor used a unit input ball together with a dimension-uniform lower covariance bound and different head norms. The final's normalization is the one used here. I do not import its rates from the earlier example statement or treat the editions as interchangeable.

Appendix C.4 also gives \(D=O(k\log(1/\epsilon))\) for noisy halfspaces under isotropic log-concave inputs, with random classification noise bounded away from one half. The paper explicitly leaves the full sample-bound instantiation under discrete 0–1 loss to a VC-based multi-task analysis. The dimension lemma is not itself that complete sample theorem.

## 4. Independent construction: approximate optimization with a certified trigger

This section is an independent analytic consequence of the source's error-witness argument. It gives sufficient tolerances for using approximate ERM and, when available, approximate noise information. It is not a new optimizer or a claim that the experiments satisfy these tolerances.

For a fixed current representation, suppose the fresh head sample satisfies

\[
\sup_{f\in\mathcal F}|\widehat L(f\circ h)-L(f\circ h)|\le a,
\]

the head solver returns \(\widetilde f\) with

\[
\widehat L(\widetilde f\circ h)\le\inf_f\widehat L(f\circ h)+r,
\]

and a supplied noise estimate satisfies \(|\widehat\kappa-\kappa|\le b\).

Accept when \(\widehat L(\widetilde f\circ h)\le\widehat\kappa+\tau\). Then

\[
\text{accept}\Longrightarrow
L(\widetilde f\circ h)-\kappa\le\tau+a+b,
\tag{5}
\]

\[
\text{reject}\Longrightarrow
\mathcal E(h,P)>\tau-a-r-b.
\tag{6}
\]

For (6), approximate optimality lower-bounds the empirical optimum by the rejected head's empirical loss minus \(r\). Uniform deviation and the lower noise confidence endpoint then give the result.

For a buffer of \(n\) tasks, suppose uniformly over shared representations and all heads,

\[
\left|\sum_{i=1}^n L_i(f_i\circ h)-\sum_{i=1}^n\widehat L_i(f_i\circ h)\right|\le A.
\]

If the joint solver has empirical **average** optimization gap at most \(\gamma_n\), comparison with the realizable shared target gives

\[
\sum_{i=1}^n
\left[L_i(\widehat f_i\circ\widehat h)-\kappa_i\right]
\le 2A+n\gamma_n.
\tag{7}
\]

One feasible allocation with exact noise information is

\[
\tau=3\epsilon/4,\quad
a=r=\epsilon/8,\quad
A=\epsilon/4,\quad
\gamma_n\le\epsilon/(2n).
\tag{8}
\]

Accepted tasks have error at most \(7\epsilon/8\). Rejections certify error greater than \(\epsilon/2\). After each joint fit the aggregate error is at most epsilon, so every future rejection supplies a source-compatible independence witness.

With uncertain noise, \(a=r=b=\epsilon/16\) and the same \(\tau,A,\gamma_n\) also work. Accepted error is at most \(7\epsilon/8\), and rejection implies error greater than \(9\epsilon/16\). Obtaining that noise estimate is an additional statistical task. The construction does not bypass Proposition 19.

With a known bound \(D\), retain the initial anchor plus every failed task and do not reset. The actual failed tasks form an epsilon-independent sequence, even after excluding the unconditional anchor. Hence there are at most \(D\) failures and at most \(D+1\) joint fits/buffered task datasets. The comparison representation after each fit witnesses the next failure. With unknown \(D\), geometric capacity doubling preserves the \(O(D+1)\) order.

The sample orders in (3) are preserved up to constants by strengthening the uniform deviation targets as in (8). The computational requirement becomes explicit: joint average optimization accuracy must scale as epsilon divided by the number of retained tasks. A constant average solver error does not maintain a constant aggregate certificate.

## 5. Independent quantitative form of the geometric update bound

Lemma 26 supplies a useful route from predictive error to a bounded number of representation changes. Here is a version with explicit dependence on its risk-comparison constants.

Suppose for some \(p\in[1,2]\) and positive \(c_-,c_+\),

\[
c_-\|B'w'-Bw\|^p
\le L_{P_{f_w\circ h_B}}(f_{w'}\circ h_{B'})-L_{P_{f_w\circ h_B}}(f_w\circ h_B)
\le c_+\|B'w'-Bw\|^p.
\tag{9}
\]

Assume the source's common head annulus, bounded by one, and semi-orthogonal \(B,B'\). Source Lemma 32 compares the best admissible approximation with the orthogonal residual within factor two. For a witness at position \(n\), let

\[
R=P_{B'^\perp}B,\quad
W=[w_1,\ldots,w_{n-1}],\quad
\lambda=\epsilon^{2/p},\quad
V=WW^\top+\lambda I.
\]

The old-task sum and new-task failure imply

\[
\sum_{i<n}\|Rw_i\|^p\le\epsilon/c_-,
\qquad
\|Rw_n\|>a_0\epsilon^{1/p},
\quad
a_0=(2^{p+1}c_+)^{-1/p}.
\tag{10}
\]

For any decomposition \(w_n=W\alpha+z\), Hölder, \(p\le2\) and \(\|R\|\le1\) give

\[
a_0\le b_0\|\alpha\|_2+\epsilon^{-1/p}\|z\|_2,
\qquad b_0=c_-^{-1/p}.
\]

The ridge variational identity, which is source Lemma 31, therefore yields

\[
w_n^\top V^{-1}w_n
=\min_\alpha\{\|\alpha\|_2^2+\epsilon^{-2/p}\|w_n-W\alpha\|_2^2\}
\ge q_0:=\frac{a_0^2}{1+b_0^2}.
\tag{11}
\]

This shows concretely what an update discovers: a head direction that retains a nonzero regularized residual against the earlier selected directions.

Put \(q=\min(1,q_0)\). The determinant/elliptical-potential argument gives, for a length-\(s\) sequence,

\[
sq\le 2k\log\!\left(1+\frac{s}{k\epsilon^{2/p}}\right).
\]

Using the elementary implication \(z\le x\log(1+yz)\Rightarrow z\le3x\log(1+xy)\), also proved in the source's Appendix C.5, gives the explicit bound

\[
s\le\frac{6k}{q}
\log\!\left(1+\frac{2}{q\epsilon^{2/p}}\right).
\tag{12}
\]

Unlike a bare \(O(k\log(1/\epsilon))\), this form remains meaningful throughout \(\epsilon\in(0,1)\) and exposes deterioration of the risk-to-geometry constants. It does not extend (9) to arbitrary neural representations.

For the linear-instance orders, comparison of (4) with separate learning gives two different amortization scales, ignoring logs. The overhead is dominated by the head-only term when \(T\gg dk^2\). It can already improve on the separate-learning representation cost when \(T\gg k^2\), for nontrivial \(d\). Matching the known-representation benchmark and merely beating independent ERM are different claims.

## 6. Empirical evidence and its actual controls

The experiments test the proposed scheduling mechanism, not the full general ERM theorem or recovery of an identifiable ground-truth representation.

| Experiment | Intervention and observations | Material limits |
|---|---|---|
| Synthetic logistic regression | \(d=10,T=50,\epsilon=.05\), \(k\in\{3,5,8\}\), head norm beta in \(\{8,4,1\}\). Ten trials. Updates usually track \(k\), with \(k=8,\beta=1\) giving mean 5.3 and standard deviation 1.27. Held-out evaluation uses \(32/\epsilon^2\) samples. | Gaussian covariates and large head norms differ from the bounded theorem instance. The selected \(m_N\) is smaller than the theorem prescription. Bayes risks are estimated using \(10^6\) Monte Carlo samples, with the synthetic generating model available. That information has a cost. |
| MNIST binary tasks | One positive digit and five negative digits. A learned ReLU representation of width 128, 50 tasks, target absolute error .05. Ten trials, mean 4.9 updates, standard deviation .54. | The head trigger uses training empirical 0–1 risk. Optimization uses binary cross entropy. Changing chosen digit classes changes the input marginal. This is not a direct trial of the common-marginal, supplied-Bayes-risk theorem. |
| CIFAR-10 binary tasks | ResNet-18 variant trained from scratch, output dimension 256, more than 11 million parameters, 50 tasks and absolute error .15. Ten trials, mean 8.0 updates, standard deviation 1.18. | The trigger uses a reserved validation split, reused during adaptive representation decisions. It is not the fresh independent head-test interface of the proof. Training loss is again a surrogate, and task-specific class selections change the input law. |

Figure 2 reports mean curves with one-standard-deviation shading, and Table 1 reports update counts. Figures 3–4 show task errors on held-out dataset test sets. Those test sets are described as evaluation only. There is no evidence here of test-set training leakage, but reused training/validation images and adaptive trigger selection must retain their actual roles.

Appendix D specifies Adam-based optimization and early stopping. Synthetic runs allow up to \(10^4\) epochs. MNIST allows up to 2,000 epochs. CIFAR joint fits allow up to 300 epochs and head tests up to 200. None is a certificate of global empirical optimality or of the tolerances in (8).

The figures support that the method can run with substantially fewer updates than tasks in these chosen settings. They do not establish asymptotic update bounds for deep representations, a matched wall-clock advantage over all alternative lifelong methods, or an all-task retention theorem.

## 7. What can be reused and what remains outside the result

The most useful source-level objects are the predictive-quality trigger, the selected-task buffer, the aggregate error witness and the ridge-potential argument. Together they specify when stored evidence can justify changing a representation and how repeated failures consume a finite complexity budget.

The independent tolerance calculation makes that mechanism reviewable with imperfect solvers. The explicit potential bound prices geometric conditioning. Both are mathematical tools attached to the source interface. Neither requires a claim that FP should adopt this algorithm.

A substantive FP transfer would still need an actual source of identifiable tasks or probes, a stationary sampling interface, a representation/head class, a calibrated predictive baseline, and a method that supplies the required joint optimization or replacement guarantee. Autonomous task formation, learned recurrent updates, finite-bit state accounting and computation reuse are not established here.

No core definitions, architecture, experiments or files under research/frontier were changed. The ordinary reading was selected after checking current discoveries, edition identities and active owners. Astra request 2e7a6c9 had already been completed by Pro-A at e0296c3. The next research unit requires another fresh request and ownership check.
