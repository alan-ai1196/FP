# A Predictive View on Streaming Hidden Markov Models

## Source and actual coverage

- **Author:** Gerardo Duran-Martin, Oxford-Man Institute, University of Oxford.
- **Read edition:** [arXiv:2604.09208v1](https://arxiv.org/abs/2604.09208v1), submitted April 10, 2026. The November 26 version check listed only v1. [PDF](https://arxiv.org/pdf/2604.09208v1) and [complete TeX](https://arxiv.org/src/2604.09208v1).
- **Publication status:** external-author preprint. The manuscript explicitly prints “Preprint.” An accepted-style LaTeX option does not establish conference acceptance. No separate reviewed edition was authenticated.
- **Full reading by Pro-C, November 26, 2026, Shanghai:** all 10 physical pages, §§1–5, Appendices A–C, every active formula and proof, all five figures with 14 panels in total, Table 1, all 25 printed references and all 28 source bibliography records. The 1,084-line main TeX and its notation definitions were inspected, with commented drafts distinguished from the published text. Original PDF pp. 3–4 and 7–10 were visually checked, covering every figure/table and the theorem, disputed proof and parameter factorization. There are no substantive author footnotes or separate unexamined paper appendices.
- **Source files:** ignored cache `literature/corpus/pro_c/2604.09208v1/`. Source acquisition and source availability are distinct from reading credit.
- **Verification:** bounded independent counterexamples and algebra for Theorem 4.1, checked by the main reader and a separate source assistant. A separate bounded implementation inspection used the author repository at [`13d06c0ec138acee0ca4f63d6512ae43b66029ba`](https://github.com/gerdm/streaming-hmm/tree/13d06c0ec138acee0ca4f63d6512ae43b66029ba), dated April 13. No experiments, complete software audit or formal proof replay were performed. The paper does not pin this later implementation commit.

**Main finding:** beam pruning is a usable recursive approximation, but the paper's general forward-KL optimality claim is false. Its conditional one-step distortion bound survives and can be sharpened. The released experimental code also uses different forecast timing for SHMM and RBPF, so the recorded comparisons do not establish a common causal prediction ranking.

## 1. Original problem and algorithm

The source models a stream with a supplied number of regimes \(K\), a known transition matrix \(\pi\), and a supplied family of regime-specific predictors. Each latent path \(h=z_{1:t}\) assigns observations to regimes. Each path therefore carries its own collection of predictive summaries \(b_{t,k}(h)\). These summaries can be conjugate parameter posteriors, GP states or more general predictive updates.

For a path extended by regime \(k\), only summary \(k\) is updated. Its unnormalized path weight is the old weight times the transition probability times the predictive likelihood of the new observation. The implementation expands \(S\) retained paths into \(SK\) candidates, retains the largest \(S\) weights, then normalizes. The next-observation predictive averages both path uncertainty and the next regime transition.

The useful mechanism is maintaining multiple regime-assignment histories while learning their emission predictors online. The number of regimes, transition law and summary update family are supplied. The algorithm does not learn an arbitrary state graph from raw observations.

Two source qualifications matter:

1. **Exact filtering is not exponential for every HMM.** A fully specified finite HMM admits the usual state-belief recursion. Path-dependent parameter learning can prevent that aggregation and motivate the path mixture considered here. The introduction's blanket exponential statement is broader than this setting warrants.
2. **Normalization is missing from two printed identities.** The path-posterior equality in §3.3 needs division by the observation evidence. The unnormalized product in Appendix B following Eq. 10 likewise needs a normalizer. The beam algorithm's explicit final normalization supplies the first operational correction. These omissions are separate from the substantive optimality failure below.

Recursive beam pruning also need not preserve the globally largest exact-posterior paths at a later time. A previously discarded ancestor can acquire a large continuation likelihood. The source proves no accumulated error guarantee relating its repeatedly pruned posterior to the exact path posterior.

## 2. What Theorem 4.1 actually asserts

At one fixed time, write

\[
p(y)=\sum_h w_h f_h(y).
\]

For a retained path set \(A\) of size \(S\), let

\[
\delta=\sum_{h\notin A}w_h,
\qquad
p_A=\sum_{h\in A}\frac{w_h}{1-\delta}f_h,
\qquad
p_{A^c}=\sum_{h\notin A}\frac{w_h}{\delta}f_h.
\]

The approximation class permits **arbitrary new mixture weights on the retained component densities**. Assumption A1 is

\[
\chi^2(p_{A^c}\Vert p_A)\le C<\infty.
\]

The theorem claims that posterior renormalization \(q_A=p_A\) minimizes \(D(p\Vert q)\) on a fixed retained set, that its divergence is at most \(\log(1+\delta C)\), and that selecting the largest posterior weights gives an optimal support. These are three separate assertions.

### Exact location of the proof failure

Appendix A, p. 7, Eq. 8 correctly decomposes

\[
D(p\Vert q)-D(p\Vert p_A)
=(1-\delta)D(p_A\Vert q)
+\delta\int p_{A^c}\log\frac{p_A}{q}.
\]

It then concludes optimality from nonnegativity of the first term. The second term depends on \(q\) and can be negative. The following example satisfies A1 and makes the total strictly negative.

## 3. A finite exact counterexample inside the stated observation model

Define real-valued densities

\[
f_r(y)=
\begin{cases}
r,&0\le y<1,\\
1-r,&1\le y<2,\\
0,&\text{otherwise}.
\end{cases}
\]

Use three components and posterior weights

\[
(r_1,r_2,r_3)=\left(\frac1{10},\frac12,\frac9{10}\right),
\qquad
(w_1,w_2,w_3)=\left(\frac25,\frac7{20},\frac14\right).
\]

Their full predictive is \(p=f_{11/25}\). All mixtures are positive on the same two intervals, so the relevant chi-square divergences are finite.

### Fixed retained support, claim (i)

For \(A=\{1,2\}\), posterior renormalization gives

\[
\delta=\frac14,
\qquad q_A=f_{43/150}.
\]

The admissible replacement weights \((3/20,17/20)\) produce

\[
\frac3{20}f_{1/10}+\frac{17}{20}f_{1/2}
=f_{11/25}=p.
\]

Consequently the alternative has KL zero, whereas

\[
D(p\Vert q_A)=0.0529932956400\ldots>0.
\]

The paper's overlap assumption holds explicitly:

\[
\chi^2(p_{A^c}\Vert p_A)
=\frac{(9/10-43/150)^2}{(43/150)(107/150)}
=\frac{8464}{4601}.
\]

In Eq. 8, choosing \(q=p\) gives approximately \(0.0373586944\) for the nonnegative term and \(-0.0903519900\) for the discarded-mixture term. Their sum is negative as required.

### Selecting a support, claim (iii)

For \(S=1\), the largest posterior weight selects component 1. Yet

\[
D(p\Vert f_{1/10})=0.386209529433\ldots,
\qquad
D(p\Vert f_{1/2})=0.007217380308\ldots.
\]

The lower-weight middle component is much better. Even a common bound \(C=64/9\) works for every retained/discarded mixture in this example. Minimizing a common upper bound does not minimize the actual objective. Without a uniform \(C\), the bound itself additionally varies with the chosen components.

### Realization as an HMM

Take three regimes, transition matrix \(I_3\), these known emission densities, and initial probabilities

\[
\left(\frac{40}{328},\frac{63}{328},\frac{225}{328}\right).
\]

After observing any \(y_1\in[1,2)\), Bayes' rule gives exactly \((2/5,7/20,1/4)\). The identity transition preserves the three next-step densities. This event has positive probability. Known emissions are a permissible special case of supplied predictive models. The theorem imposes no irreducibility or positive-transition requirement excluding this construction.

Thus claims (i) and predictive-optimality (iii) are refuted under the written assumptions, rather than merely lacking a proof in this reading.

## 4. The valid distortion estimate and the different latent objective

The source's one-step bound (ii) remains valid. In fact,

\[
p=(1-\delta)p_A+\delta p_{A^c}
\quad\Longrightarrow\quad
\chi^2(p\Vert p_A)=\delta^2\chi^2(p_{A^c}\Vert p_A).
\]

Jensen's inequality under \(p\) gives

\[
D(p\Vert p_A)
\le\log\int\frac{p^2}{p_A}
=\log\!\left(1+\delta^2\chi^2(p_{A^c}\Vert p_A)\right)
\le\log(1+\delta^2 C).
\]

The paper's weaker \(\log(1+\delta C)\) follows for \(0\le\delta\le1\). Its p. 8 algebra actually yields the squared-mass form before weakening. This estimate concerns one fixed mixture and requires finite overlap divergence. It gives neither an optimal projection nor a repeated-pruning guarantee. Small discarded weight alone does not control a missing predictive region.

A nearby correct optimization statement concerns **reverse KL on latent path weights**. For any probability vector \(\alpha\) supported on \(A\),

\[
D(\alpha\Vert w)
=D\!\left(\alpha\middle\Vert \frac{w|_A}{W_A}\right)-\log W_A.
\]

Its optimal weights are the normalized retained weights, and its optimal size-\(S\) support maximizes \(W_A\). This elementary identity is an independent clarification, not a corrected version of the paper's forward predictive-KL theorem. Marginalizing latent paths changes the objective.

## 5. Experiments and resource accounting

The GP example uses two regimes with opposite slopes, common sinusoidal terms and Gaussian noise. Figures 1–2 show one-step and four selected multi-step forecasts. They illustrate behavior without a comparative GP benchmark or an empirical test of A1.

The Gaussian experiment learns three regime means with known noise variance and transition matrix. The paper compares online EM, SHMM and a prior-proposal RBPF. Table 1 reports:

| Method | MAE | RMSE | Time, seconds |
|---|---:|---:|---:|
| Online EM | 0.9 ± 0.01 | 1.2 ± 0.02 | 0.04 ± 0.01 |
| SHMM | 0.8 ± 0.02 | 1.1 ± 0.02 | 0.10 ± 0.03 |
| RBPF | 1.0 ± 0.04 | 1.3 ± 0.06 | 0.26 ± 0.01 |

Figure 4's caption says two regimes despite the main text and three displayed mean levels. Figure 5 varies \(S\) over 1, 2, 5, 10, 20 and 50. Its RBPF errors near \(S=2\) differ substantially from the table, while the released notebook's different run configurations help explain this. No log-score, predictive KL or calibration measurement is reported. Good point prediction does not directly test the claimed distributional projection.

### Bounded inspection of the linked author implementation

The following observations refer specifically to the April 13 commit linked above, which is later than arXiv v1. They are source-code evidence, not a rerun of the published experiment.

- [`streaming_hmm.py`, `step`](https://github.com/gerdm/streaming-hmm/blob/13d06c0ec138acee0ca4f63d6512ae43b66029ba/streaming_hmm.py) computes the forecast from the incoming belief before incorporating the current observation, then expands, scores and prunes candidates.
- [`rbpf_hmm.py`, `rbpf_step`](https://github.com/gerdm/streaming-hmm/blob/13d06c0ec138acee0ca4f63d6512ae43b66029ba/rbpf_hmm.py) incorporates the current observation into parameter means and weights, resamples, then constructs its returned forecast from `bel_final`. Its regime lookup additionally uses the preceding stored regime index. The returned scalar therefore uses current-observation information.
- [`gauss1d-hmm.ipynb`](https://github.com/gerdm/streaming-hmm/blob/13d06c0ec138acee0ca4f63d6512ae43b66029ba/gauss1d-hmm.ipynb), cells `536d1ce8`, `e7fa4573` and `c76570d3`, compares these forecasts with the same-index observation without a time shift. SHMM and RBPF consequently have different causal information sets in these recorded comparisons. A repaired comparison could change either metric and has not been performed.
- The notebook's online EM cell `ac4f3bec` predicts before observing the target but uses `phi @ mu`, while its filtering step first propagates `phi @ transition_matrix`. The transition-aware pre-observation mean would use the propagated belief. The inspected routine's equivalence to the cited online EM algorithm was not established. Its mean initialization is random, without a future-data initialization in this cell.
- The initial demonstration uses \(S=2\). The ten-run experiment in cell `e7fa4573` explicitly uses \(S=10\), with seeds 100–109. Its recorded mean errors closely match Table 1 after rounding. The sweep in `c76570d3` uses one generated tape at seed 500 and three initialization trials per \(S\). These are different protocols. Some time standard deviations in the paper also differ from the notebook output, so exact table provenance is not established.
- A beam count is not a physical bit budget. The code maintains \(K\) emission summaries per path, expands \(SK\) candidates, and allocates regime-history arrays indexed by the supplied horizon. The GP version has additional per-regime buffers. Static model, numeric precision, history and working storage require separate accounting.

The Gaussian SHMM initializer itself samples parameter means and initial regime labels. Its subsequent beam update is deterministic conditional on that initialization. This is narrower than calling the entire released run sampling-free.

The inspected notebook times function calls without an explicit completion barrier around asynchronous JAX work. The published text supplies no hardware specification or complete timing methodology. Equal hypothesis counts alone do not establish equal arithmetic, memory or completed-device time.

## 6. Retained research value

This paper is useful as a concrete deterministic beam-update recipe conditional on initialization and as a warning about confusing posterior support compression with predictive optimization. Its finite-overlap inequality is a valid one-step tool.

For the current pruning question, the exact correspondence is a posterior branch weight \(w_h\) and that branch's next-output law \(f_h\). On a finite output alphabet the same mixture identities hold with sums. The counterexample shows that ranking branches by weight is insufficient for optimizing the next-output KL, even with finite common overlap bounds. It does not settle the cost of computing better weights, recursive state recovery, finite-bit mixture gates or the long-horizon loss of a particular FP learner. No core theory or experiment was changed.

**Continuation boundary:** this edition is complete. The author implementation was inspected only for the reported timing, protocol and resource questions. Linked papers retain their independent reading statuses. No rerun or remaining full-paper obligation is created by this note.
