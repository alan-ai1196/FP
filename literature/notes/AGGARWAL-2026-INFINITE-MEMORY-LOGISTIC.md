# Sharp Minimax Regret for Infinite-Memory Logistic Prediction

## Source, edition and reading boundary

- Author: Vaneet Aggarwal, Purdue University.
- Read edition: [arXiv:2608.26515v3](https://arxiv.org/abs/2608.26515v3), revised November 5, 2026 at 23:42:57 UTC. The first submission was August 27. [Versioned PDF](https://arxiv.org/pdf/2608.26515v3) and [complete source](https://arxiv.org/src/2608.26515v3) were retrieved directly.
- Publication status: preprint. The JMLR document class is not evidence of journal acceptance. No separate reviewed edition was authenticated in this bounded lookup. Earlier versions were not read.
- Pro-D completed the main reading on November 26, 2026, Shanghai. Coverage is all 31 PDF pages, Sections 1–6, Appendices A–D, every proof, all ten active TeX files, the AI disclosure and all 18 bibliography entries. Table 1 on p. 4 and Algorithm 1 on p. 17 were inspected visually. Original layouts on pp. 6, 8, 15, 18 and 27 were also checked. There are no figures or author footnotes in the active source.
- The author reports AI assistance with exposition. This is an author disclosure, not independent evidence about the mathematical work.
- Verification: selected manual checks of the information lower bound, Gaussian comparison, lag Gram moments and leading-constant argument. An assisting reader separately checked the MLE-to-entropy and threshold argument. No numerical reproduction, external proof certification or formal verification was performed.

## 1. The statistical experiment

The observed inputs are independent uniform signs (U_t\in\{-1,1\}). Given the parameter and the entire input sequence, the binary marks are independent and obey

\[
P_\theta(Y_{t+1}=1\mid U_{1:t},Y_{1:t})
=\sigma\left(\sum_{j=1}^{t}\theta_j U_{t+1-j}\right),
\qquad \sigma(z)=(1+e^{-z})^{-1}.
\]

The learner knows a nonnegative envelope (r), with

\[
|\theta_j|\le r_j,\qquad \sum_{j\ge1}r_j\le B<\infty.
\]

The first mark is an independent fair bit and the input history starts empty. This is a specified exogenous-input experiment. The marks do not drive future inputs, and the theorem does not replace these signs by arbitrary observed tokens or an endogenous stationary history.

At time (t), the learner has observed ((U_{1:t},Y_{1:t})) and predicts ((U_{t+1},Y_{t+1})). Predicting the new input uniformly is optimal and costs no excess loss. The performance criterion is the expected **cumulative** excess log loss against the true conditional law,

\[
\mathcal R_T(r)=\inf_Q\sup_{\theta\in\Theta_r}
D(P_{\theta,T}\Vert Q).
\]

All logarithms are natural. The infimum permits every causal history-to-distribution predictor. It contains no finite persistent-memory restriction. This criterion differs from terminal next-symbol risk at a fixed sample size and from regret against a parameter fitted in hindsight to an adversarial tape.

## 2. The lag-resolved quantity and the main bound

Lag (j) appears in exactly

\[
n_{T,j}=(T-j+1)_+
\]

prediction rounds. Define

\[
s_{T,j}=n_{T,j}r_j^2,\qquad
\Gamma_T(r)=\sum_{j\le T}\log(1+s_{T,j}),\qquad
d_T(r)=\sum_{j\le T}\min\{1,s_{T,j}\}.
\]

Theorem 1, p. 6, establishes

\[
\frac{c_*}{\max\{1,B^2\}}\Gamma_T(r)
\le\mathcal R_T(r)\le\frac12\Gamma_T(r),
\]

where

\[
\kappa_B=\sigma(B)(1-\sigma(B)),\qquad
c_* =\frac{2\kappa_1^2}{\pi^2}
\left(1-\frac1{2\pi^2}\right)\approx0.0074.
\]

The statement is finite-horizon and permits nonmonotone envelopes and gaps. The learner receives the envelope. Adaptation to an unknown envelope is not supplied.

For (s_{T,j}\ll1), the contribution is proportional to (n_{T,j}r_j^2). For (s_{T,j}\gg1), it grows logarithmically. Thus many individually weak coefficients can have a substantial aggregate cost even when none can be resolved relative to its allowed range. Section 4.1 gives an explicit example with (r_j=B/m_T) on the first (m_T) lags, where (\sqrt T\ll m_T\ll T). Then every (s_{T,j}\to0), while

\[
\Gamma_T(r)\sim B^2T/m_T\to\infty.
\]

Keeping only individually resolved coordinates would miss this lower bound.

## 3. What makes the proof work

### 3.1 Pairwise divergence and the Gaussian mixture

Lemma 2, Eq. (12), uses logistic curvature and orthogonality of the independent signs to obtain

\[
\frac{\kappa_B}{2}\sum_jn_{T,j}(\theta_j-v_j)^2
\le D(P_{\theta,T}\Vert P_{v,T})
\le\frac18\sum_jn_{T,j}(\theta_j-v_j)^2
\]

when both parameters lie in the envelope class. The upper inequality holds for arbitrary real coefficient vectors because the logistic log-partition curvature is globally at most (1/4). The lower inequality uses bounded logits.

Section 3.1 puts independent (N(0,r_j^2)) priors on the coefficients. For a fixed truth, the variational comparison measure has coordinate mean and variance

\[
\mu_j=\frac{s_{T,j}}{s_{T,j}+4}\theta_j,\qquad
w_j=\frac{r_j^2}{1+s_{T,j}/4}.
\]

Combining its Gaussian KL cost with the preceding pairwise bound gives

\[
\mathcal R_T(r)
\le \frac12\sum_j\left[
\log(1+s_{T,j}/4)+\frac{s_{T,j}}{s_{T,j}+4}
\right]
\le\frac12\sum_j\log(1+e s_{T,j}/4).
\]

The prior may leave the parameter class because the prediction infimum is unrestricted. The product prior is consistent across finite horizons, so one posterior predictor attains the bound for every (T). Exact evaluation of those posterior integrals is not assigned a finite-bit or polynomial-time implementation here.

### 3.2 A useful fixed-design information inequality

Lemma 5, Section 3.2, considers logistic observations with design (Z) and offset (b) independent of the parameter. Logits must remain in ([-B,B]) throughout the parameter box. A product cosine-squared prior has coordinate Fisher information (\pi^2/r_j^2). With (R=\operatorname{diag}(r_j)), sequential van Trees inequalities and the determinant lemma give

\[
I(\theta:Y_{1:T}\mid Z,b)
\ge8\kappa_B^2\,
E\log\det\left(I+\frac{RZ^\top ZR}{4\pi^2}\right).
\]

The positive prior-information term keeps the inverse matrices well defined even for singular or weak designs. This is one portable mathematical instrument in the paper, with its independence, product-prior and bounded-logit assumptions retained.

### 3.3 Dependent lag rows still have usable Gram moments

Here (Z_{t,j}=1_{t\ge j}U_{t+1-j}). Its rows overlap and are not independent. For (G=Z^\top Z), the exact identities are

\[
G_{jj}=n_{T,j},\quad E G_{jk}=0,\quad
E G_{jk}^2=\min\{n_{T,j},n_{T,k}\}\quad(j\ne k).
\]

Lemma 6 proves, for any (\lambda>0),

\[
E\log\det(I+\lambda RGR)
\ge(1-2\lambda B^2)
\sum_j\log(1+\lambda n_{T,j}r_j^2).
\]

The proof normalizes by the exact diagonal. It bounds the squared Frobenius norm of the off-diagonal error both absolutely and relative to the diagonal log-determinant. The absolute estimate controls the probability of a poor design, while the relative estimate prevents a fixed additive error from destroying the all-weak-signal regime. It does not assume independent Gram entries.

Theorem 1 then shrinks the lower-bound prior by (1/\max\{1,B\}). This keeps the logits within ([-1,1]), yielding a universal curvature constant and the displayed (\max\{1,B^2\}) price. The construction avoids an exponentially small (\kappa_B^2) factor in this statistical lower bound.

## 4. When one half is the leading constant

Theorem 2, pp. 15–16, allows envelopes (r^{(T)}) to change with the horizon, but requires one common finite (B) and eventual positivity of (\Gamma_T). Under those conditions,

\[
\mathcal R_T(r^{(T)})\sim\frac12\Gamma_T(r^{(T)})
\quad\Longleftrightarrow\quad
d_T(r^{(T)})=o(\Gamma_T(r^{(T)})).
\]

Two separate mechanisms establish the equivalence.

1. Lemma 7 strengthens the upper bound to
   \[
   \mathcal R_T\le\frac12\Gamma_T-\delta d_T,\qquad
   \delta=\frac12\log\frac8{4+e}>0.
   \]
   Consequently a nonnegligible contribution from bounded signal levels prevents the ratio from approaching one half.
2. Proposition 2 uses a uniform prior on half-width boxes for a selected coordinate set (S). After normalizing column (j) by (\sqrt{n_{T,j}}), the good-design event has probability at least (1-4v_S), where
   \[
   v_S=\sum_{j\ne k\in S}\frac1{\max\{n_{T,j},n_{T,k}\}}.
   \]
   A constrained MLE controls posterior entropy on that event and gives
   \[
   \mathcal R_T\ge(1-4v_S)_+
   \left[\frac12\sum_{j\in S}\log(n_{T,j}r_j^2)-\eta_B|S|\right]_+,
   \quad
   \eta_B=\frac12\log\frac{8\pi e}{\kappa_{B/2}^2}.
   \]

Choosing (S=\{j:s_{T,j}\ge\tau\}) bounds (v_S\le B^2/\tau). If (\Gamma_T/d_T\to\infty), take (\tau=\max\{2,\Gamma_T/d_T\}). All three error terms then vanish. The proof uses a finite-sample entropy argument rather than a growing-dimensional posterior normal approximation.

The full-sample MLE appears only inside this information lower bound. It is not offered as a causal prediction algorithm. A horizon-dependent prior is legitimate in a minimax lower bound for each horizon.

**Limited independent check.** The main reader and assisting reader checked the prior interval lengths, conditioning on the input-only good event, the normalized Gram moment, the MLE score variance and the threshold quantifiers. No substantive local gap was found in this chain. The common-(B) condition is essential to this proof and cannot be silently replaced by arbitrary (B_T\to\infty).

**Additional deduction.** Under eventual positivity, (d_T=o(\Gamma_T)) already implies (\Gamma_T\to\infty). If all (s_{T,j}<1), then (\Gamma_T\le d_T). Otherwise (d_T\ge1). Thus a diverging ratio (\Gamma_T/d_T) forces (\Gamma_T\to\infty). This deduction does not add an assumption to the theorem.

## 5. Rates and algorithmic scope

The source proves the following distinctions in Corollaries 1–2 and Proposition 1.

| Envelope | Minimax cumulative regret |
|---|---|
| Fixed support with (k\ge1) positive entries | (\frac{k}{2}\log T+O_{B,r}(1)) |
| (r_j=Ae^{-\alpha j^\beta}), fixed positive (A,\alpha,\beta) | Asymptotic to (\frac{\beta}{2(\beta+1)(2\alpha)^{1/\beta}}[\log(A^2T)]^{1+1/\beta}) |
| (r_j=Ae^{-\alpha j}) | Asymptotic to (\log^2(A^2T)/(8\alpha)) |
| (r_j=Aj^{-s}), fixed (s>1) | (\Theta_{B,s}((A^2T)^{1/(2s)})), with exact regret constant left open |

For polynomial envelopes, (\Gamma_T\sim\pi(A^2T)^{1/(2s)}/\sin(\pi/(2s))), but the regret-to-(\Gamma_T) ratio stays strictly below one half. A conventional (h\log T) charge per retained coordinate gives an extra factor ((\log T)^{1-1/(2s)}). This is a weakness of that analysis, not a lower bound against all finite-window predictors. The source explicitly gives a scaled-window method achieving the better order.

Theorem 3 uses envelope-scaled features and retains (S_T=\{j:s_{T,j}\ge1\}). With (m=|S_T|), its regret bound for a general retained set is

\[
\operatorname{Reg}_T
\le\frac{|S|}{2}
+\frac1{2\kappa_B}\sum_{j\in S}\log(1+s_{T,j})
+\frac18\sum_{j\notin S}n_{T,j}\theta_j^2
+\sum_{t\le T}\varepsilon_t.
\]

The pathwise online-Newton comparison is deterministic. The expected truncation term additionally uses the specified input law. Approximate projections are charged explicitly. With (\varepsilon_t\le1/T), the total bound is (O_B(\Gamma_T)).

Section 5 counts real arithmetic, assigns unit cost to evaluating (\sigma), receives the radii and knows (T). The displayed per-round implementation uses

\[
O\bigl(m^2(1+TB^2)\log(2+mTB)\bigr)
\]

operations and (O(m^2+\max S_T)) storage locations. The input-buffer term matters for a gapped envelope. For a nonincreasing envelope, the retained set is a prefix. These storage locations contain real numbers. No bit-precision analysis is supplied, and the regret constant (1/\kappa_B) can grow exponentially with (B). “Polynomial computation” therefore needs both the arithmetic-model and fixed-(B) qualifications.

## 6. Limits relevant to using the result

- The state dimension is not learned as an arbitrary hidden transition graph. Unknown coefficients live in a supplied lag-coordinate system with a supplied envelope.
- Cumulative source-relative risk does not directly yield the same bound for the last prediction on every horizon. A time-averaged consequence is immediate by division by (T), but a terminal-risk theorem needs more.
- Independent inputs are used in the divergence and Gram calculations. Replacing them with feedback, correlated inputs or a language stream changes the proof interface.
- The paper contains no experiments, empirical learning-dynamics claim or finite-bit implementation.
- Lemma 1(a) removes private randomization in an **unrestricted** predictor class by averaging joint laws. That averaging need not preserve a fixed finite-state recursive implementation. It therefore does not answer the separate question whether private coins improve a finite-memory gate.

No FP theorem transfer or architectural modification is proposed. The reusable results are the assumption-specific information inequality, the two-scale Gram control, the distinction between individually weak and aggregate statistical cost, and the exact condition for a parametric one-half leading factor.

## 7. Resume information

This edition is complete. No section remains unread. References were read as bibliography entries and as used in the source, not as eighteen separately read papers. Nearby discovery candidates include Han–Wu's 2026 prediction-from-compression tutorial and Yüksel–Flammarion's AISTATS2025 sample-complexity paper. Their independent reading statuses must be recorded only after their own source work. Check current Astra requests before choosing either.
