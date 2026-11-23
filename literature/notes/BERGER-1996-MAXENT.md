# Berger, Della Pietra and Della Pietra 1996 — A Maximum Entropy Approach to Natural Language Processing

## Edition, coverage and evidence

**Adam L. Berger, Stephen A. Della Pietra and Vincent J. Della Pietra.** *Computational Linguistics* 22(1), March 1996, pp. 39–71. [Official ACL record](https://aclanthology.org/J96-1002/) · [official journal PDF](https://aclanthology.org/J96-1002.pdf). The ACL record does not supply a DOI.

**Fully read, November 23, 2026, Shanghai:** all 33 printed pages, 39–71, including §§1–6, the complete algorithmic appendix, four algorithms, all twelve figures, all nine tables, footnotes, acknowledgements and 23 references. The main assistant read the body personally. The PDF has 34 physical pages: physical pages 1–33 are the article, and the last is a blank scan tail, also visually checked.

Text extraction was used for continuous prose blocks. Physical pages 3, 5 and 12 have no text layer and were read directly as images. All figures and tables, dense optimization displays and the complete appendix were checked against the original scan. The separate 36-page CMU author manuscript was downloaded but was not used to claim coverage of the journal edition.

Local source: literature/corpus/pisf_prior_art/BERGER-1996-MAXENT.pdf. A page-indexed text/OCR aid is in the same ignored source directory. Printed page numbers are used below.

**Selection:** the paper supplies the conditional feature-induction equations needed to delimit Astra's learned history/output corrections. It follows the [Della Pietra et al. 1997 reading](DELLAPIETRA-1997-FEATURE-INDUCTION.md), rather than the unrelated OpenAI catalog sequence.

**Verification scope:** the conditional gain identity was independently differentiated, and three localized issues in printed formulas or numerical reporting were checked below. These are limited algebraic checks, not a certification of the entire paper. No experiments were replicated and no formal proof was run.

## 1. Original problem — §§1–3, pp. 39–49

The authors separate choosing useful statistics from fitting a probability model consistent with those statistics. Their target is a finite-output conditional distribution \(p(y\mid x)\), where \(x\) is observed context. The examples concern translation decisions, sentence segmentation and word order.

Training pairs define an empirical joint distribution \(\widetilde p(x,y)\) and a fixed empirical context distribution \(\widetilde p(x)\). A binary feature \(f(x,y)\) contributes the constraint
\[
 \sum_{x,y}\widetilde p(x)p(y\mid x)f(x,y)
 =\sum_{x,y}\widetilde p(x,y)f(x,y).
\]
The left side uses empirical context frequencies but model output probabilities. These are joint expected feature counts under a fixed context marginal. They should not be confused with an unweighted conditional frequency within a selected context subset.

The maximum-entropy objective is
\[
 H(p)=-\sum_{x,y}\widetilde p(x)p(y\mid x)\log p(y\mid x),
\]
subject to the selected moment constraints and row normalization. The familiar exponential form is
\[
 p_\lambda(y\mid x)
 =\frac{\exp\{\sum_i\lambda_i f_i(x,y)\}}
        {Z_\lambda(x)},\qquad
 Z_\lambda(x)=\sum_y\exp\{\sum_i\lambda_i f_i(x,y)\}.
\]
Each context has its own normalizer. Within this family the fitting objective is the conditional training log likelihood
\[
 L(\lambda)
 =\sum_i\lambda_i\widetilde p(f_i)
  -\sum_x\widetilde p(x)\log Z_\lambda(x).
\]
The maximum-likelihood and constrained maximum-entropy formulations yield the same fitted conditional law on the relevant empirical context support. The footnote on p. 47 explicitly allows the optimum to occur only as a limit of finite-parameter models. A finite maximizer is not guaranteed for every empirical constraint set.

The paper refers to the 1995 random-field report for a fuller convergence and duality treatment. The related 1997 author manuscript has been read separately, but the 1995 report has not.

### Improved Iterative Scaling

For nonnegative features and \(f^\#(x,y)=\sum_i f_i(x,y)\), Algorithm 1 solves
\[
 \sum_{x,y}\widetilde p(x)p_\lambda(y\mid x)
 f_i(x,y)e^{\Delta\lambda_i f^\#(x,y)}
 =\widetilde p(f_i)
\]
for the coordinate increments. If \(f^\#\equiv M\), the equation gives
\[
 \Delta\lambda_i=\frac1M
 \log\frac{\widetilde p(f_i)}{p_\lambda(f_i)}.
\]
Otherwise the scalar equations are solved numerically. The paper states monotonicity and convergence with a cited proof. It does not present a new proof of the entire IIS theorem in this journal article.

## 2. Feature selection and the meaning of “approximate” — §4, pp. 49–53

A large candidate pool is given. Features can be initially irrelevant. The authors seek a smaller active set with reliable empirical statistics, using greedy additions and held-out likelihood to decide when to stop.

The ideal procedure refits the entire expanded model for every candidate and ranks the resulting likelihood improvements. Its cost motivates a cheaper candidate score. Given the already fitted \(p_S\), freeze its old weights and add just one coefficient:
\[
 p^\alpha_{S,f}(y\mid x)
 =\frac{p_S(y\mid x)e^{\alpha f(x,y)}}{Z_\alpha(x)},
 \qquad
 Z_\alpha(x)=\sum_y p_S(y\mid x)e^{\alpha f(x,y)}.
\]
Equations (24)–(27) give
\[
 G_{S,f}(\alpha)
 =\alpha\widetilde p(f)
  -\sum_x\widetilde p(x)\log Z_\alpha(x).
\]
This expression is **exact for the one-coefficient update with old weights fixed**. The approximation is its use to rank candidates in place of their improvements after full refitting. The method retains every context normalizer. It is not an approximation that drops normalization.

The appendix differentiates this objective:
\[
 G'(\alpha)=\widetilde p(f)
 -\sum_x\widetilde p(x)\mathbb E_{p^\alpha(\cdot\mid x)}f,
\]
\[
 G''(\alpha)=
 -\sum_x\widetilde p(x)
       \operatorname{Var}_{p^\alpha(\cdot\mid x)}(f).
\]
The scalar objective is concave. The derivative is an empirical-minus-model moment discrepancy, with the variance controlling its curvature.

If all expanded weights were optimized exactly, the expanded family would contain every frozen-weight candidate. Therefore the exact fully refitted gain is at least \(\sup_\alpha G(\alpha)\). A feature that ranks first by this lower surrogate need not rank first by the full gain. This does not provide a global optimality guarantee for a budgeted feature set.

The paper's examples use finite feature templates combining particular outputs with context-word identities or positions. This is feature discovery within a supplied family, not unconstrained discovery of every possible representation.

## 3. The complete efficiency appendix — pp. 69–71

Direct Newton steps in \(\alpha\) need not improve the objective monotonically. The appendix instead discusses Newton iteration in \(e^\alpha\) or \(e^{-\alpha}\), using the sign of the optimum relative to the starting point zero. Its update is
\[
 \alpha_{n+1}=\alpha_n+
 \frac1r\log\left(
 1-\frac1r\frac{G'(\alpha_n)}{G''(\alpha_n)}
 \right),\quad r\in\{-1,1\}.
\]
For a binary feature, the relevant curvature in the transformed variable supports the stated monotone route when the branch is chosen on the correct side. The printed branch choice has a sign problem recorded in §5 below.

Algorithm 4 computes candidate gains together. It first builds the set of features active for each context, initializes each candidate's first derivative to its empirical expectation and its second derivative to zero, then makes a shared pass through contexts to accumulate the model expectation and conditional variance. Each candidate receives its own scalar coefficient update.

The intended efficiency gain is fewer passes over the training data, especially when the data are on disk. This is not a guarantee of constant model-normalization cost or zero cost for a large candidate family. It also does not imply that every parallel candidate may be added at once without interaction.

## 4. Applications, measurements and limitations — §5, pp. 54–66

The common setting is Candide, a French-to-English statistical translation system. A language model and an English-to-French translation model are combined by Bayes' rule. The basic translation model sums over alignments, with a Viterbi-alignment approximation used in parts of the workflow. Its components include fertility, word translation and distortion probabilities.

The underlying bilingual corpus has 3.6 million sentence pairs and just under 100 million words per language. That is the corpus supporting the basic translation model. It should not be silently treated as the fitting sample size of each later maximum-entropy demonstration.

| Application | Targets and inputs | Reported evidence |
|---|---|---|
| Context-sensitive word translation | Viterbi alignments supply French rendering labels. Features pair a particular translation with a word immediately before or after the English word, or anywhere in a three-word side window. | Tables give selected features and training likelihood gains for translating “in” and “run.” Two example translations improve after adding contextual models. No aggregate translation-quality benchmark comparable to a modern deployment evaluation is supplied. |
| Safe sentence segmentation | Alignment-derived rift/no-rift labels. Inputs include nearby words, part-of-speech tags and externally obtained word classes. | The training/held-out likelihood curves separate after roughly 40 features. A dynamic program combines scores with a maximum segment length of ten words. Four sample segmentations are shown. |
| Reordering French noun–de–noun phrases | Alignment-derived swap/no-swap labels. Features depend on the left noun, right noun or pair. | 10,000 fitting events, 358 final constraints. Table 9 reports 80.4% overall accuracy on 71,555 test cases, versus 70.2% for never swapping. Reported subgroup accuracies are 93.5% on nonswapped cases and 49.2% on swapped cases. These are author-reported numbers, not locally replicated measurements. |

The segmentation objective is alignment compatibility, not necessarily semantic phrase coherence. Figure 8 can safely separate words belonging to one intuitive semantic unit. The features and labels in these applications use an alignment model, linguistic preprocessing or both.

The held-out curve is a direct warning against reading a monotonically improving training likelihood as generalization evidence. The paper does use held-out information to discuss stopping, but does not establish a universal stopping rule, a storage-price optimality theorem or a recurrent-state learning result.

The translation contexts include words on both sides of the focal word. These experiments are therefore not direct evidence for a causal next-token model using only past observations.

## 5. Limited checks of printed equations and reporting

### 5.1 The sign of the defined dual function

On p. 46, equation (7) defines
\[
 \Lambda(p,\lambda)=H(p)+
 \sum_i\lambda_i\bigl(p(f_i)-\widetilde p(f_i)\bigr),
\]
and (9) defines \(\Psi(\lambda)=\Lambda(p_\lambda,\lambda)\).
Substitution of (10) into this definition gives
\[
 \Lambda(p_\lambda,\lambda)
 =\sum_x\widetilde p(x)\log Z_\lambda(x)
  -\sum_i\lambda_i\widetilde p(f_i).
\]
This is the **negative** of printed equation (11), which is the correct conditional log-likelihood expression later used in (13)–(14).

Thus the displayed definition and the later sign convention are inconsistent. The likelihood maximization and feature-gain formulas can be read with \(\Psi=L\), or equivalently with the negative of the upper Lagrange dual. This local sign issue does not invalidate the exponential-family representation or the conditional gain identity.

### 5.2 Reversed Newton branch in Algorithms 3 and 4

Equations (40) and (42), on pp. 70–71, print
\(r=1\) when \(\widetilde p(f)\le p_S(f)\), and \(r=-1\) otherwise.

Because \(G'(0)=\widetilde p(f)-p_S(f)\), a finite interior maximizer lies at positive \(\alpha\) when the empirical feature expectation is larger. The transformed-Newton route described on p. 69 uses \(e^\alpha\), hence \(r=1\), in that case. The two printed branches are reversed.

A one-context binary example makes the implementation consequence explicit. Let
\[
 \widetilde p(f)=\tfrac1{10},\qquad p_S(f)=\tfrac9{10}.
\]
Then
\[
 G'(0)=-\tfrac45,\qquad G''(0)=-\tfrac9{100}.
\]
The printed branch chooses \(r=1\), so the logarithm in (35) receives
\[
 1-\frac{G'(0)}{G''(0)}
 =1-\frac{80}{9}=-\frac{71}{9}.
\]
The first real-valued update is undefined, despite positive base probabilities and a finite optimum. The example directly refutes the universal correctness of this branch as printed. It does not refute concavity or the derivatives in (37)–(38).

For the route described in the prose, use \(r=1\) for a positive initial derivative, \(r=-1\) for a negative derivative, and stop if it is zero, subject to the stated binary-feature and finite-optimum conditions. This correction is an independent derivation here, not a located official erratum.

### 5.3 A reported gain is not an exact optimization certificate

The p. 59 example reports an estimated frozen-weight gain of approximately 0.019059 bits, followed by a fully recomputed likelihood change from −2.8703 to −2.8525 bits, or 0.0178 bits. The latter is smaller.

An exactly optimized expanded family cannot lose against its frozen-weight subfamily. Consequently those printed numerical values cannot jointly be taken as an exact trace of both ideal optimizations. The paper does not resolve the discrepancy with numerical tolerances or another explanation in this passage. The note retains the reported values without inventing a cause or extrapolating the issue to all empirical results.

These checks were confined to equations needed to understand or reuse the feature-gain method. They are not an exhaustive audit.

## 6. Precise relevance to the current FP experiments

This is a bounded source comparison with an explicit algebraic mapping. It does not transfer authority over model design from Astra.

For the earlier [two-set protocol](https://github.com/alan-ai1196/FP/blob/0f451412fc92692d31293a1b04d982b4f903a259/research/frontier/NEXT.md), set
\[
 x=(u,q),\qquad f(x,y)=1_{\{u\in A\}}1_{\{y\in B\}},
 \qquad p_S(y\mid x)=p_q(y),\quad\alpha=\log\rho.
\]
Equations (24)–(26) then give exactly
\[
 Z_\alpha(u,q)=
 1+1_{\{u\in A\}}(e^\alpha-1)p_q(B)
\]
and the realized full-vocabulary likelihood gain
\[
 \alpha\sum_t1_{\{u_t\in A,y_t\in B\}}
 -\sum_{t:u_t\in A}
 \log\!\left[1+(e^\alpha-1)p_{q_t}(B)\right].
\]
Thus the conditional feature-induction prior art contains the normalized objective directly. The correspondence is stronger than a resemblance between information-theoretic terms. It still does not identify the paper's template search with FP's free set optimization, fixed multiplier grid or installed-bit prices.

Astra's [later nested-global protocol at ae87e2f](https://github.com/alan-ai1196/FP/blob/ae87e2fa41150ab9ff7278a0fd2c21cb67d3ba28/research/frontier/NEXT.md) fixes an output class and composes a global odds correction with context-dependent exceptions. With a fixed proper nonempty class \(B\) and positive base, write
\[
 m(x)=p_{\rm base}(B\mid x),\qquad
 \delta(x)=\alpha_0+\sum_j\alpha_j h_j(x).
\]
The class probability becomes
\[
 r(x)=\frac{e^{\delta(x)}m(x)}
 {1+(e^{\delta(x)}-1)m(x)},\qquad
 \operatorname{logit}r(x)=\operatorname{logit}m(x)+\delta(x).
\]
This is a conditional log-linear model with a fixed base offset and gated class features.

If all within-class and within-complement proportions of the base are retained, the per-token loss improvement is exactly
\[
 1_{\{y\in B\}}\log\frac{r(x)}{m(x)}
 +1_{\{y\notin B\}}\log\frac{1-r(x)}{1-m(x)}.
\]
The conditional class-event log score and the full-vocabulary log-score difference are therefore identical under these assumptions. This equality is a testable comparator identity, not evidence that a particular learned gate generalizes.

The identity fails to describe changes that also alter relative probabilities inside \(B\) or its complement. Changing \(B\) changes the aggregation itself. Neither this paper nor the fixed-class identity proves that an earlier-token exception is useful after conditioning on the latest token, or that a compact recurrent state can be learned. Computing the base class mass and storing the output IDs also remain real implementation costs.

The literature result sharpens the conventional baseline: normalized exponential corrections and likelihood-driven selection are established mechanisms. Any additional value from the current FP procedure must be assessed at the level of its particular support search, state maintenance, statistical behavior and resource accounting.

## 7. Follow-up and source dependencies

McCallum's *Efficiently Inducing Features of Conditional Random Fields* (2003) is the next selected full reading. It gives a later conditional induction method with regularization, approximation and direct feature-count comparisons. Dhillon et al. on information-theoretic co-clustering and Brown et al. on class-based n-grams remain distinct sources for learning both sides of a discrete prediction model.

The paper's 23 references include maximum-entropy geometry, iterative scaling, EM, translation models, language-model decision trees and word classes. Their appearance in this bibliography does not imply full reading of those sources. The author's separate [derivative explainer](https://www.cs.cmu.edu/afs/cs/user/aberger/www/html/gain/gain.html) was located, but its image-rendered mathematics was not separately read.

No exhaustive novelty verdict is claimed. This completed journal reading, the source's claims and the local algebraic corrections have separate evidential status.
