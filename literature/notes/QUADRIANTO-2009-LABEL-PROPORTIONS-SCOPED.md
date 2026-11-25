# Estimating Labels from Label Proportions

## Source and limited coverage

- **Authors:** Novi Quadrianto, Alex J. Smola, Tibério S. Caetano and Quoc V. Le.
- **Publication:** Journal of Machine Learning Research 10(82):2349–2374, 2009.
- **Index:** JMLR-2009-QUADRIANTO-LABEL-PROPORTIONS.
- **Official sources:** [journal entry](https://jmlr.csail.mit.edu/papers/v10/quadrianto09a.html), [26-page journal PDF](https://jmlr.csail.mit.edu/papers/volume10/quadrianto09a/quadrianto09a.pdf). The entry does not separately link a supplement.
- **Status:** scoped dependency reading for Astra request 7b8ff15, **not fully read**.
- **Main-reader coverage, November 25, 2026:** PDF pp. 2–6, printed 2350–2354, including problem definition, the conditional-independence premise, the mean-operator setup, Eq. (3) and Tables 1–2. Also PDF p. 11 / printed 2359, the iid discussion and Theorem 5, and PDF p. 14 / printed 2362, the perturbation setup and displayed inverse bounds. Original pp. 6 and 11 inspected visually. Remaining theory, full proofs, experiments, figures and bibliography are unread. Reading these selected pages does not imply complete coverage of §§3 or 5.
- **Verification:** source-model and theorem-statement comparison only. No full proof audit, empirical reproduction or formal verification.

## 1. Data and the structural assumption

Section 2, printed pp. 2351–2352, describes unlabeled calibration sets \(X_i\), label fractions \(\pi_{iy}\), and a test set. There are at least as many calibration sets as classes. The mixing matrix is nonnegative, row stochastic and full column rank. Test label proportions may be known or unknown.

The indispensable premise is

\[
X\perp C\mid Y.
\]

The class-conditional feature distribution is shared across calibration contexts. The source text initially describes proportions as fractions contained in the observed sets, but the later statistical derivation has a more precise population interpretation.

## 2. Population mixture and estimated mean operator

Section 3.2, Eq. (3), printed p. 2354, explicitly writes

\[
P(x\mid C=i)=\sum_yP(x\mid y)\pi_{iy},
\qquad \pi_{iy}=P(Y=y\mid C=i).
\]

Table 2 distinguishes population feature means from empirical means. A left inverse of the known mixing matrix reconstructs class-conditional feature means. These are recombined with test class probabilities to estimate the mean operator \(\mu_{xy}=\mathbb E\phi(X,Y)\).

For conditional exponential-family models, the labels enter the penalized likelihood through this mean operator. The learner substitutes the reconstructed operator for the unavailable empirical paired operator and solves the resulting convex problem. This is a model-based reconstruction using the mixture law, not the iid same-bag covariance argument in Busa-Fekete et al.

## 3. The located convergence result

On printed p. 2359, the analysis assumes iid samples from each \(P(X\mid C=i)\), with different calibration sets independently sampled. Theorem 5 treats a factorizing nonnegative kernel bounded on the diagonal, known mixing probabilities, and the full-rank setting. The bound compares the reconstructed operator with the empirical operator from the test sample. It contains a test-sample term \(m^{-1/2}\) and calibration terms involving \(m_i^{-1/2}\), the inverse mixing matrix and class-weighted label kernel.

At a fixed well-conditioned mixing matrix, these are ordinary inverse-square-root sample scales. The inverse or pseudoinverse norm can make the constant large as the contexts become indistinguishable. No universal bag-size fast rate follows from calling \(\pi\) an aggregate statistic.

The initial set-fraction wording should therefore be preserved without silently substituting arbitrary realized proportions into this population-mixture theorem. If \(\pi\) is independently estimated, the inverse also changes.

## 4. Perturbation is an additional requirement

Section 5.7, printed p. 2362, writes \(\widetilde\pi=\pi+\Delta\), with both matrices row stochastic and \(\Delta\mathbf1=0\). It compares inverse and pseudoinverse perturbations before studying the effect on the fitted parameter.

The displayed inverse identity gives a norm bound involving both \(\|\pi^{-1}\|\) and \(\|\widetilde\pi^{-1}\|\). The pseudoinverse statement cites Wedin and likewise requires full column rank. Only this setup and the displayed bounds were read. The complete stability development is not certified here.

An independent label panel may estimate the population \(\pi_{iy}\) under suitable sampling assumptions. Its estimation cost and the resulting matrix-conditioning error must be added. They are not removed by the known-\(\pi\) convergence statement.

## 5. Boundary for Astra's question

The paper clarifies one way independent marginal observations can be informative: shared class-conditional laws plus enough distinct, known mixture proportions identify class means. The structural direction \(X\perp C\mid Y\) differs from \(Y\perp C\mid X\), which would support the crossed-panel conditional bridge in the original next-word request.

The appropriate population mapping to that bridge reverses the feature/label roles. Let the paper's class be input class \(D\), its feature be target \(Y\), and its set index be \(T\). The TD panel estimates \(\pi_{td}=P(D=d\mid T=t)\), while the TY panel samples each mixture's feature law. Under \(Y\perp T\mid D\), the class-conditional mean of the one-hot target is the row \(P(Y\mid D=d)\). This recovers the intended matrix mixture at the population level. Rank, conditioning, the sampling model and independently estimated weights remain additional requirements. Theorem 5 controls a mean operator, not the entire multiclass next-word log-loss guarantee.

It is therefore a relevant population-model dependency, without establishing the desired result from common context names alone. The [completed Busa-Fekete note](BUSA-FEKETE-2025-NEARLY-OPTIMAL-LLP.md#8-requested-comparison-independent-panels-from-common-contexts) records the exact observation comparison and the rate that survives independent panels.
