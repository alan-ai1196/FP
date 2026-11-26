# Kernel Ridge Attention: an exact evolving regression state

## Source and actual coverage

- Haowei Chen, Yichen Wang and Congfu Xu, **Kernel Ridge Attention: Nonlinear Memory with Selective Forgetting**.
- Primary edition: [arXiv 2611.23896v1](https://arxiv.org/abs/2611.23896v1), submitted November 18, 2026. [PDF](https://arxiv.org/pdf/2611.23896v1) and [complete source](https://arxiv.org/src/2611.23896v1).
- Read by Pro-B on November 26, 2026, Shanghai. **Fully read:** all 15 physical pages, main Sections 1–6, Appendices A–E, both propositions, all derivations, Algorithm 1, three figures, six numbered tables, the correspondence footnote and all 18 references. Complete active scientific TeX was read. All three original figure assets and PDF pages 4, 5, 11 and 12 were inspected visually.
- Ancillary README, numerical manifest, equation-check script and report were inspected. The source uses an ICLR 2027 style but explicitly identifies itself as a preprint. No acceptance or independent experimental replication was authenticated.
- The main reader covered the complete paper. Two assistants supplied bounded algebra and evidence checks. Those checks are distinguished below from the paper's results.

**Assessment.** The central object is a learned-feature regression model whose coefficients evolve under an Ornstein–Uhlenbeck transition. Its covariance controls the geometry of future writes. The exact recurrent/kernel equivalence and the checked block derivatives are supported. The language-model results are one-seed development-set measurements. They do not establish reliable distant copying, a calibrated posterior over language, or a general finite-bit memory theorem.

## 1. The computation the paper actually constructs

For one head, causal width-four convolutions, projections and SiLU produce query, key and value vectors. A shared bank of learned frequencies produces

\[
\phi_\Omega(z)=m^{-1/2}(\cos(\Omega z),\sin(\Omega z))^\top,
\qquad a_t=\phi_\Omega(k_t),\quad b_t=\phi_\Omega(q_t).
\]

Both features have unit norm. Their inner product is an exact positive semidefinite finite-feature kernel. Gaussian/orthogonal random-feature ideas initialize the bank. After end-to-end learning, the displayed cosine sum defines the kernel, without a theorem that it remains a particular Gaussian kernel. The reported head uses 32 frequencies and feature dimension 64. [Section 2.1]

Let \(r=\lambda^{-1}>0\), and let the learned positive content clock give \(\delta_t=\exp(-\rho_t)\). The head stores a coefficient matrix \(\Theta_t\in\mathbb R^{D\times d_v}\) and covariance \(P_t\in\mathbb R^{D\times D}\). Starting at \((0,rI)\), its update is

\[
\bar\Theta_t=\delta_t\Theta_{t-1},\qquad
\bar P_t=\delta_t^2P_{t-1}+(1-\delta_t^2)rI,
\]

\[
z_t=\bar P_ta_t,\quad s_t=1+a_t^\top z_t,\quad G_t=z_t/s_t,
\]

\[
e_t=v_t-\bar\Theta_t^\top a_t,\qquad
\Theta_t=\bar\Theta_t+G_te_t^\top,\qquad
P_t=\bar P_t-z_tz_t^\top/s_t.
\]

The output is \(o_t=\Theta_t^\top b_t\), **after** writing the current causal input. It is used to predict the next token. There is no access to that next token in the update. [Equations 4–7, Algorithm 1]

The covariance has a computational role beyond scaling one learning rate. In an isotropic covariance, the write direction is parallel to the key. In general it is \(\bar P_ta_t\), so correlations between earlier keys can rotate it. The OU prediction simultaneously contracts the coefficient mean and replenishes covariance toward the prior.

The local objective is quadratic observation error plus a quadratic displacement penalty with metric \(\bar P_t^{-1}\). Its positive definite Hessian gives a unique optimum. Sherman–Morrison gives exactly the displayed update. Proposition 1 proves

\[
0\prec P_t\preceq rI,
\qquad
0<a_t^\top G_t\le (1+\lambda)^{-1}.
\]

This is a self-write bound. A different query reads \(b_t^\top G_t\), whose sign and size also depend on alignment. [Appendices A.1–A.2]

## 2. Exact temporal kernel, with the conditioning stated correctly

Fix the realized features and clock values, and put \(u_t=\sum_{j\le t}\rho_j\). On a prefix define

\[
C_{ij}=a_i^\top a_j\,e^{-|u_i-u_j|},\qquad
d_{t,i}=b_t^\top a_i\,e^{-(u_t-u_i)}.
\]

Proposition 2 gives the exact identity

\[
o_t^\top=d_t^\top(C+\lambda I)^{-1}V_{1:t}.
\]

Its proof constructs a virtual stationary Gaussian coefficient process with transition \(\theta_t=\delta_t\theta_{t-1}+\xi_t\), innovation covariance \((1-\delta_t^2)rI\), and unit observation-noise variance. The observation covariance is \(rC+I\), and the query cross-covariance is \(rd_t^\top\). Gaussian conditioning and sequential filtering compute the same mean. This proves the algebraic identity for arbitrary fixed numerical values, whether or not real language data follow that Gaussian model. [Equation 10 and Appendix A.3]

The content Gram and exponential-time Gram are positive semidefinite. Their entrywise product is therefore positive semidefinite, and the ridge makes the solve invertible. Separate query and key projections are compatible with this construction because the query evaluates a function fitted at the key points.

The qualifier **fixed realized path** matters. Features, values and clocks in the network share their input source and depend on learned representations. The identity does not by itself identify \(P_t\) with calibrated uncertainty about the true language process. Freezing an adaptively obtained path for an algebraic proof also differs from proving a generative posterior statement after conditioning on that selection process.

For \(0<\delta_i<1\), Appendix A.4 gives a trajectory least-squares objective with transition penalty

\[
\frac\lambda2\sum_i
\frac{\|\theta_i-\delta_i\theta_{i-1}\|^2}{1-\delta_i^2}.
\]

The final minimizer equals the filtered mean. Unit retention forces a constant coefficient trajectory and recovers ordinary ridge regression. Zero retention removes previous regression evidence, while the separate convolution still retains local context.

## 3. Independent consequences of the specified recurrence

These deductions are about this mathematical operator. They are not additional claims of the authors, priority claims, or proposed changes to FP.

### 3.1 A fixed-dimensional state can implement a full-rank temporal Gram

Take every key and query feature equal to one unit vector and choose constant \(0<\delta<1\). Then

\[
C_{ij}=\delta^{|i-j|},\qquad
\det C_t=(1-\delta^2)^{t-1}>0.
\]

To obtain the determinant, subtract \(\delta\) times row \(i-1\) from row \(i\), proceeding from the last row upward. The resulting matrix is upper triangular with first diagonal entry one and all remaining entries \(1-\delta^2\).

Thus the temporal Gram has rank \(t\), although the active regression direction needs only its scalar coefficient and variance. The covariance in unused directions stays at the known prior. The Markov realization compresses the computation of the current filtered read. It does not claim a low-rank factorization of the entire temporal Gram or retention of every possible old query answer. Exact real arithmetic and an installed finite-precision implementation remain different resource descriptions.

### 3.2 Equal present readouts do not determine the next write

In the unit-retention case, write the same unit key \(a\) with zero values \(n\) times. Then \(\Theta_n=0\), so every current query output is zero, but

\[
P_n=(\lambda I+naa^\top)^{-1},\qquad
a^\top P_na=(\lambda+n)^{-1}.
\]

One further observation of value one along \(a\) produces coefficient \((\lambda+n+1)^{-1}\). Different past evidence counts therefore give identical current mean predictions and different subsequent updates. Keeping only \(\Theta\) cannot implement this exact recursion across these histories. The covariance supplies update-relevant information. Unit retention is an admitted mathematical endpoint, not the finite-parameter value of the paper's strictly positive learned clock.

### 3.3 Positive semidefinite kernels do not make stochastic read weights

Use two Fourier features \(a_1=(1,0)^\top\), \(a_2=b_2=(-1,0)^\top\), which the one-frequency map realizes at phases zero and \(\pi\). Set \(\lambda=1\) and the intervening retention to \(1/2\). Then

\[
C=\begin{bmatrix}1&-1/2\\-1/2&1\end{bmatrix},\qquad
d_2^\top=(-1/2,1),\qquad
d_2^\top(C+I)^{-1}=(-2/15,7/15).
\]

The history weight is negative and the weights do not sum to one. This is a valid regression read. Calling its internal coefficients probabilities or a convex memory mixture would change the mathematical object.

## 4. Parallel computation and what the checks establish

A block maps incoming covariance by

\[
\Phi(P)=C+A(P^{-1}+J)^{-1}A^\top.
\]

With an earlier block \(l\), later block \(r\), and \(N=(I+C_lJ_r)^{-1}\), the source supplies

\[
A_{r\circ l}=A_rNA_l,
\]
\[
C_{r\circ l}=C_r+A_rNC_lA_r^\top,
\qquad
J_{r\circ l}=J_l+A_l^\top J_rNA_l.
\]

Woodbury gives the composition. Although \(N\) need not be symmetric, \(NC_l\) and \(J_rN\) have symmetric positive semidefinite forms. Once boundary covariances determine the gains, the coefficient update is affine and has a second associative scan. The sequence is divided into 64-token blocks. Logarithmic scan depth across blocks does not remove within-block recurrence or the cost of matrix operations. [Section 3.1, Appendix B.1]

For the joint adjoint, \(T_i=\delta_i(I-G_ia_i^\top)\), \(F_i=T_i\cdots T_1\), and the cross statistic \(E\) give

\[
dP_{\rm out}=F\,dP_{\rm in}F^\top,
\qquad
d\Theta_{\rm out}=F\,d\Theta_{\rm in}+F\,dP_{\rm in}E.
\]

These are **first-order differentials**, not equalities for arbitrary finite differences. Under the paper's symmetric-adjoint convention, covariance contributions use \(\tfrac12\langle S,dP\rangle\). This accounts for both cross terms and the \(\tfrac12\operatorname{tr}(S_0)\) initial-prior contribution. [Equations 15–17 and Appendix B.2–B.3]

After reading the complete supplied NumPy script, Pro-B reran it using float64. All 60 cases passed, with maximum errors \(4.66\times10^{-15}\) for the dual output, \(8.88\times10^{-15}\) for prefix covariance and \(5.33\times10^{-15}\) for the joint adjoint. This reproduces the author's small formula-check program. It does not execute the optimized model or independently validate the training runs.

A separate assistant calculation used non-diagonal initial covariance, nonzero initial coefficients, arbitrary PSD block triples and central finite differences. Its checked differential errors were below \(6.5\times10^{-11}\). Together with the displayed derivations, these are bounded consistency checks. No formal certification is claimed.

### Numerical qualification

The source correctly gives positive eigenvalues for \(W=I+C_lJ_r\) and the exact residual-correction identity \(R^+=R^2\). A spectral interval alone does not give an equally small Euclidean operator-norm error for a nonnormal matrix.

For example, with \(K>0\), take

\[
C=\frac1{K^2+1}\begin{bmatrix}K^2&K\\K&1\end{bmatrix},
\qquad J=\operatorname{diag}(0,K^2+1).
\]

Here \(0\preceq C\preceq I\), \(J\succeq0\), and \(W=\begin{bmatrix}1&K\\0&2\end{bmatrix}\). Starting at \(X_0=I/2\), two exact residual corrections leave

\[
R_0^4=\frac1{16}\begin{bmatrix}1&-K\\0&0\end{bmatrix},
\qquad
\rho(R_0^4)=1/16,\quad
\|R_0^4\|_2=\sqrt{1+K^2}/16.
\]

This limits a generic inference from positive spectrum to norm stability. It does not show that the actual 64-token block statistics attain this example or contradict the reported kernel measurements. If \(C\succ0\), a similarity transformation to \(I+C^{1/2}JC^{1/2}\) supplies a bound with an additional \(\sqrt{\kappa_2(C)}\) factor. Actual residual norms or conditioning must enter a uniform guarantee. [Independent qualification of Section 3.3 and Appendix B.4]

## 5. Experimental evidence and resource interpretation

All reported models use six layers, width 384, the same 100,007,936-token training stream, 3,052 updates, one training seed and one data order. Evaluation resets memory on 2,048-token windows. The final 512-window validation stream is also the development split used in model construction. The curve uses a smaller fixed 128-window subset. [Section 4.1, Appendix C]

| Model | Parameters, M | Validation PPL | Natural rare-repeat top-1 | Far rare-repeat top-1 |
|---|---:|---:|---:|---:|
| Transformer++ | 30.81 | 97.21 | 32.00% | 13.79% |
| Gated DeltaNet | 31.75 | 110.95 | 6.69% | 4.91% |
| KDA recurrence control | 32.62 | 111.62 | 6.42% | 4.91% |
| GDN-2 recurrence control | 34.37 | 107.01 | 8.95% | 5.09% |
| KRA | 30.92 | 88.00 | 25.41% | 8.69% |

The table is consistent with the included numerical manifest. The KDA and GDN-2 entries are recurrence replacements in the Gated DeltaNet outer layer, not evaluations of every component of the original named architectures. The evidence supports improvements in this shared protocol. It does not estimate variation across training seeds or certify independent test performance. Exact raw-document hash disjointness was reported. Near-duplicate and overlapping-span separation were not authenticated. [Tables 1–2]

The controlled-copy probe has 128 base cases, seven distances, matched/distractor cues and two stored answers. Its distant score averages distances at least 512. KRA has association gain 0.2004 nats but balanced answer-choice accuracy only 50.390625%. At distances 1024, 1536 and 1984, that accuracy is exactly 50% in the supplied data. Positive answer-probability influence and reliable answer selection are different measurements. The natural-recall score uses full-vocabulary top-1 and remains below the softmax comparator. [Figure 3, Appendix D, ancillary data]

The three ablation pairs use different front ends and cannot be chained into one additive decomposition. A fixed Fourier bank still has a learned bandwidth and learned input features. Value SiLU improves PPL from 93.16 to 88.00 and far-repeat accuracy from 8.00% to 8.69%, while all rare-repeat accuracy decreases from 27.04% to 25.41%. No reported matched intervention separately removes full covariance or OU covariance replenishment, so their individual causal contribution is unresolved. [Table 3 and Appendix C.3]

KRA's measured eight-GPU training step is 31.77 ms against Gated DeltaNet's 27.97 ms, approximately 13.59% greater latency. Single-GPU forward/backward takes approximately 25.04% longer. These are training measurements, not decode-speed results. [Table 4]

Persistent state is 1,221,120 bytes, including coefficient matrices, full covariances and convolution histories. It is constant in prefix length, approximately 1.893 times the Gated DeltaNet state and 61.83 times smaller than the reported 8K softmax cache. Parameters, training activations and temporary workspace are different costs. The 4K/8K entries measure storage, not demonstrated predictive quality at those lengths. [Table 5 and Appendix C.4]

## 6. Reproducibility and retained research value

The source package includes selected metrics, curves, confidence-interval fields, hashes, equation checks and figure assets. It does not include the main model implementation, optimized kernels, checkpoints, token files or evaluation scripts. Bare implementation commit hashes lack corresponding repository URLs. They provide identifiers without making the full experiment independently replayable from this release. The confidence-interval construction and resampling unit are not specified in the supplied text, and those intervals cannot measure cross-training-seed variation.

The recoverable mathematical tools are an exact learned-feature temporal kernel realization, covariance-dependent residual writing, a dynamic regression objective, associative covariance maps and their joint derivatives. The source distinguishes a useful finite-dimensional update state from raw history storage. The independent examples above clarify the difference between temporal Gram rank, present readouts, update state and probabilistic mixture semantics.

No FP transfer is proposed. There is no new core definition, architecture, experimental protocol or implementation in this note. A future source-led comparison with MesaNet or curvature-aware delta rules would concern their actual objectives and covariance approximations, without requiring an FP connection.
