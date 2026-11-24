# Chen–Chang–Mehta (2026): Differentiable HMM filtering

## Source, version and complete coverage

Reginald Zhiyan Chen, Heng-Sheng Chang and Prashant G. Mehta, **Differentiable Filtering for Learning Hidden Markov Models**, L4DC 2026, *PMLR* **331:1035–1054**, June 17–19, 2026. [Official proceedings](https://proceedings.mlr.press/v331/chen26c.html) · [official PDF](https://raw.githubusercontent.com/mlresearch/v331/main/assets/chen26c/chen26c.pdf) · [arXiv:2511.10571v2](https://arxiv.org/abs/2511.10571v2).

The current arXiv version is **v2, April 24, 2026, 15:39:38 UTC**; v1 was submitted November 13, 2025. Both current PDFs have **20 pages**. They are not byte-identical, but their extracted text is identical after removal of the arXiv watermark and whitespace normalization. The main reader used the complete active v2 TeX for the body and checked the official conference PDF, including every actual figure. The conference-program title *Belief Net: A Filter-Based Framework for Learning Hidden Markov Models from Observations* is an alias, not another paper.

**Fully read:** §§1–5, Appendices A–C, all displayed formulas, two algorithms, eight figures, the composite Table 1, the hardware footnote, corresponding-author note, acknowledgments and all **46 printed references**. Main source, all three substantive appendix files, algorithm/table inputs, notation definitions and bibliography were read. All eight figures and the table/algorithms were inspected in original conference layouts. The source additionally contains 44 plot-data CSVs; selected displayed values were checked against those files. This does not mean all underlying experiments were reproduced.

The work is a reviewed university-authored paper, not an official OpenAI/Anthropic release. No AI-assistance declaration or formal verification artifact was identified. The paper provides empirical evidence and explicit algorithms; it leaves a Belief-Net-specific convergence/sample-complexity theory open. Bounded independent checking here concerns loss indexing and mathematical interpretation, not an experimental replication.

## Problem: ordinary observations, supplied HMM family

The latent process \(X_t\in[d]\) is a time-homogeneous Markov chain, observed through symbols \(Z_t\in[m]\). Its unknown parameters are

\[
\mu_i=P(X_0=i),\quad
A_{ij}=P(X_{t+1}=j\mid X_t=i),\quad
C_{ik}=P(Z_t=k\mid X_t=i).
\]

Training data are \(N\) observed sequences \(Z^{(n)}_{0:T}\); no latent labels are supplied. The learner estimates initial, transition and emission probabilities **offline**, then filters and predicts with the learned model. The architecture supplies the HMM form, finite alphabet and a state dimension, or a finite list of candidate dimensions. It does not learn an unrestricted update program or an arbitrary state space.

The original questions are how transformers perform on HMM-generated data and how an HMM trained using modern prediction-loss optimization performs on real text. The authors position Belief Net as an interpretable HMM baseline implemented as a differentiable computation graph. They explicitly acknowledge earlier gradient-based HMM estimation and differentiable filters. The method does not introduce a new statistical model class beyond a standard categorical HMM.

## Learnable recursion and objective

Unconstrained logits for \(\mu,A,C\) are converted by softmax, rowwise for matrices. For finite logits this produces strictly positive, normalized probabilities. The paper's free statistical dimension is

\[
(d-1)+d(d-1)+d(m-1),
\]

while its parameter tables count the stored logit entries \(d+d^2+dm\), including softmax gauge redundancies.

Write \(b_{t|t-1}\) for the prior on the current state and \(b_t\) for its posterior after the current symbol. Algorithm 1 begins with \(b_{0|-1}=\mu\), consumes \(Z_t=k\), and computes

\[
e_t=C_{:,k},\qquad
b_t=\frac{b_{t|t-1}\odot e_t}
{\sum_i b_{t|t-1,i}e_{t,i}},
\]
\[
b_{t+1|t}=b_tA,\qquad p_{t+1}=b_{t+1|t}C.
\]

Thus \(p_{t+1}\) is released before seeing \(Z_{t+1}\). The belief is an exact sufficient statistic under the **specified, fixed HMM parameters**. When those parameters are estimates, this is the fitted model's posterior; the source does not prove that it equals the unknown process's posterior.

The actual training loss is

\[
\ell_\theta(Z_{0:T})=-\frac1T\sum_{t=1}^T
\log p_{\theta,t}(Z_t),
\]

averaged over a sampled minibatch. Automatic differentiation through the filtering path updates all three logit blocks using AdamW. Algorithm 2 initializes parameters once and repeats minibatch forward/backward passes. The state is reinitialized at the start of each sequence/window in Algorithm 1. Offline parameter optimization and online application of a trained filter are different phases; online parameter learning is listed as future work.

### Exact conditional-versus-joint likelihood boundary

The displayed loss begins at \(t=1\), after the model has consumed \(Z_0\). Consequently

\[
T\ell_\theta=-\log P_\theta(Z_{1:T}\mid Z_0),
\]

whereas ordinary joint-likelihood Baum–Welch includes

\[
-\log P_\theta(Z_{0:T})
=T\ell_\theta-\log[(\mu C)_{Z_0}].
\]

Section 3.3 writes the joint chain rule starting at zero and says its objective is the same as the displayed Belief Net objective. **For finite windows with learned \(\mu,C\), that is not an exact equality:** the omitted first-symbol probability depends on parameters. The two printed algorithms and Appendix B do not add this term or fix it to a constant. Conditioning on a supplied first symbol is a valid predictive objective; adding its likelihood is necessary if claiming exact equivalence to full joint training. This bounded distinction does not invalidate the causal filter or the measured conditional prediction task.

An exact one-state Bernoulli example makes the difference visible: let \(P(Z=1)=q\) and the sequence be \((0,1)\). The conditional loss is \(-\log q\), whereas the joint loss is \(-\log[q(1-q)]\). Moving from \(q=1/2\) to \(3/4\) improves the first and worsens the second. Both choices have finite logits. This check does not assert that the learned initial distribution has no gradient: it still affects later conditional forecasts through the posterior after \(Z_0\).

## Optimization and computation: what is and is not proved

The authors compare full-batch Baum–Welch smoothing, roughly \(O(NTd^2)\) work per iteration, with minibatched differentiable filtering, stated as \(O(BT(d^2+dm))\) per iteration. Here \(B\ll N\), but the number of iterations, data exposures and validation searches differ. Faster minibatch iterations do not by themselves prove faster optimization to a fixed error.

The experiments use AdamW with \((\beta_1,\beta_2)=(.9,.999)\), \(\epsilon=10^{-8}\), weight decay .01, batch size 10, and at most 2,000 synthetic or 4,000 text iterations. Belief Net searches dropout \(\{0,.1\}\) and learning rate \(\{.01,.1\}\) by validation loss. The transformer baselines search dropout \(\{0,.1\}\) and learning rate \(\{.001,.01\}\), with the same batch/iteration limits. Baum–Welch uses `hmmlearn.CategoricalHMM`, at most 20 iterations, and selects the best of five random initializations by validation loss. The separate initialization-sensitivity study uses ten runs per condition.

Appendix B explicitly leaves optimization and HMM parameter-recovery sample complexity to future work; generic smooth nonconvex SGD results are cited as possible inputs, not proved to apply with complete HMM assumptions and constants. Neither AdamW's empirical success nor EM's conditional stationarity guarantees establish global parameter identification here.

A deployed fixed-parameter filter can carry a \(d\)-coordinate belief and perform \(O(d^2+dm)\) work to issue the complete next-symbol distribution. This is an immediate interpretation of the recursion, not a paper theorem about charged memory. Full-window automatic differentiation, parameter/optimizer storage, finite-precision rounding and retained training intermediates have separate costs. No constant-memory training or finite-bit stability theorem is provided.

## Synthetic evidence and the actual comparisons

Synthetic data use \(d=64\), uniform initial state, random sharply concentrated emission rows, and

\[
A=\alpha P_{\rm cycle}+(1-\alpha)A_{\rm random},
\quad\alpha=.9
\]

for the main experiment. Random logits are Gaussian, with softmax temperatures .1 for random transitions and .01 for emissions. Training uses 4,000 sequences for the undercomplete \(m=128\) case and 1,000 for the overcomplete \(m=32\) case, nominal length 256; validation has 10% as many independently generated sequences from the same HMM. The written \(Z_{0:T}\) versus length-\(T\) convention has an endpoint ambiguity; the scored loss contains \(T\) targets after an initial input.

All reported timings use a CPU-only laptop: Intel i7-12700H, 32 GB RAM, no GPU. Table 1 reports:

| Method | Undercomplete validation NLL | Overcomplete validation NLL | Undercomplete / overcomplete training time |
|---|---:|---:|---|
| True-model HMM filter | 1.368 | .737 | Reference, no learning |
| Belief Net | 1.569 | .830 | 20 / 6 minutes |
| Baum–Welch | 1.951 | 1.216 | 51 / 12 minutes |
| Tested spectral method | 1.624 | Rank failure | PCA reported as instantaneous / failure |
| nanoGPT-s, one head/one layer | 1.458 | .829 | 2.5 / 1 minutes |
| nanoGPT-m, four heads/four layers | 1.475 | .810 | 7.5 / 1.5 minutes |

Belief Net improves on the tested classical baselines, while these transformers have lower prediction losses and shorter reported training times. The methods are matched by state/embedding dimension, **not by parameter or compute budget**. In the undercomplete case the reported parameter counts are 12,352 for Belief Net/Baum–Welch, 73,920 for nanoGPT-s and 221,760 for nanoGPT-m. The corresponding overcomplete counts are 6,208, 51,392 and 199,232. The spectral representation has 524,416 parameters in the undercomplete setup.

The rank failure is for the implemented single/pair/triple-moment spectral construction; it is not a theorem that all spectral methods fail for all overcomplete HMMs. Appendix B clips negative predicted entries to the smallest current positive value, renormalizes, and resets the spectral state if its update denominator is zero. These are part of the tested baseline, not part of the original spectral guarantee.

Figures 2 and 5 sweep candidate dimensions \(4,8,16,32,64,128,256\). Prediction losses approach the true-model baseline when capacity is large enough, and ten-seed Belief Net runs show less variation than the tested Baum–Welch runs. A flat or improving curve above the true dimension does not identify a unique minimal dimension without a model-selection rule or penalty. The paper reports a nanoGPT-s with dimension 16/9,264 parameters reaching loss comparable to a dimension-64/12,352-parameter Belief Net.

Figure 7 adds \(\alpha=.7\) and \(\alpha=1\). The latter is labeled “slow mixing,” but at exactly one the specified transition is a deterministic cyclic permutation, hence periodic rather than a finite mixing-time example. This is a direct consequence of the displayed generator. It should not be cited as evidence of a uniform ergodic-mixing guarantee. The compared transformers remain strong on these synthetic regimes.

## Parameter recovery means the reported diagnostics

Figure 6 uses two diagnostics:

1. Sorted **magnitudes of transition eigenvalues**, compared with the true spectrum. Extra fitted states show small eigenvalue magnitudes after the main cluster.
2. An emission discrepancy: choose a uniform row-mass optimal-transport coupling using Hellinger row costs, then report the coupled absolute entry differences weighted by the true stationary symbol probabilities.

The coupling has column masses \(1/d\) and row masses \(1/\hat d\); the paper computes it using Sinkhorn/POT. Its printed shorthand for the coupling domain is dimensionally awkward, but the subsequent row/column constraints specify the intended matrix coupling.

These measurements support the stated recovery behavior of some dynamical and emission features. They are **not a joint permutation-aligned error certificate for \((\mu,A,C)\)**: eigenvalue magnitudes do not determine transition entries; the emission coupling is evaluated separately; no initial-distribution error is reported. Figures show particularly clear emission improvements in the overcomplete case, with near-equality and small exceptions in other conditions. Complete structural recovery should not be inferred solely from prediction loss or these summaries.

## Character-level text evidence

The Federalist Papers experiment uses 82 characters, 4,000 length-256 training sequences and 64 latent states. It is a small character-level benchmark, not a full-vocabulary modern language-model scaling study. Figure 3 and its supplied plotting source give:

| Model | Validation NLL | Perplexity, \(\exp(\mathrm{NLL})\) |
|---|---:|---:|
| Belief Net | 2.002 | 7.40 |
| Baum–Welch | 2.286 | 9.84 |
| Spectral, selected dimension 2 | 3.020 | 20.49 |
| nanoGPT-s | 1.492 | 4.45 |
| nanoGPT-m | 1.351 | 3.86 |

These are source results, not independent measurements. The submitted Belief Net validation CSV has 81 points, ending at iteration 4,000 with loss **2.001921823150233**, also its minimum. Checking this file and exponentiating the plotted values is not a training replay. The spectral method failed at the nominal dimension 64, so the authors swept dimensions 1–64 and reported dimension 2. Appendix C calls nanoGPT-m single-layer, whereas Appendix B's explicit configuration is four heads/four layers. Results and hyperparameters are selected on validation data; no separate final-test estimate is supplied in the reported comparison.

Figure 8's learned emissions concentrate lowercase letters broadly and identify rows associated with uppercase letters/digits. The transition heatmap is sparse visually. These are interpretable fitted patterns; the data have no known true latent HMM against which to establish recovery of the actual language-generating state. A transformer's improvement is not, by itself, a formal proof that a particular latent language process is non-Markovian.

## Dependencies, reproducibility and remaining scope

The main dependencies are classical HMM filtering, Baum–Welch/EM, Hsu et al.'s observable spectral representation, automatic differentiation/AdamW, and standard neural sequence models. Appendix A distinguishes this work from continuous-state differentiable Kalman/particle filters and Hidden Markov Neural Networks, where neural weights themselves are latent states. Cited originals remain independently unread unless already separately indexed.

The paper links author implementations at [Signal-System](https://github.com/hanson-hschang/Signal-System) and [BeliefNet-HMM](https://github.com/Rockostoneo/BeliefNet-HMM), in addition to upstream `hmmlearn`, spectral-learning, nanoGPT and POT. Source plot data are public, but benchmark training and the exact paper run environments were not reproduced here.

A bounded independent code inspection pinned `BeliefNet-HMM` at **88bc2bc9e66d3285e7dbad490561e222f3035cd0** and `Signal-System` at **c077d1899be626876fe5ffe038431526514a7372**. [Training](https://github.com/Rockostoneo/BeliefNet-HMM/blob/88bc2bc9e66d3285e7dbad490561e222f3035cd0/BeliefNet/training.py) uses the input prefix `z_train[:, :-1]` and shifted target `z_train[:, 1:]`. The [transition module](https://github.com/hanson-hschang/Signal-System/blob/c077d1899be626876fe5ffe038431526514a7372/src/ss/estimation/filtering/hmm/learning/module/transition/_transition.py) initializes a prior, corrects with each input and then transitions. The [learning process](https://github.com/hanson-hschang/Signal-System/blob/c077d1899be626876fe5ffe038431526514a7372/src/ss/estimation/filtering/hmm/learning/process/_process.py) computes cross entropy on the predicted trajectory without an added initial-symbol term. The transition implementation explicitly stores a \((B,d,T)\) state trajectory before whole-loss backpropagation. These inspected paths agree with the conditional-loss and growing-training-storage distinctions above. The pinned current commits were **not authenticated as the exact commits used for the paper's experiments**.

The directly relevant prior-art fact is that ordinary next-observation loss can train transition and emission parameters through a causal probabilistic state update in a supplied finite HMM family. The paper does not give a prefix-dependent emission/base-model correction, a learned two-state refresh guarantee, an optimal memory dimension, a finite-bit quantization bound, a future-horizon total-KL theorem or a general construction of new recurrent input/output directions. Its POMDP, online-learning and broader-memory extensions remain proposed future work. No FP architecture or theorem is imported from these experiments.
