# Learning from Label Proportions: A Mutual Contamination Framework

## Source and limited coverage

- **Authors:** Clayton Scott and Jianxin Zhang.
- **Publication:** Advances in Neural Information Processing Systems 33, 2020.
- **Index:** NeurIPS-2020-SCOTT-ZHANG-LLP.
- **Official sources:** [entry](https://proceedings.neurips.cc/paper/2020/hash/fcde14913c766cf307c75059e0e89af5-Abstract.html), [12-page main PDF](https://proceedings.neurips.cc/paper_files/paper/2020/file/fcde14913c766cf307c75059e0e89af5-Paper.pdf), [14-page supplement](https://proceedings.neurips.cc/paper_files/paper/2020/file/fcde14913c766cf307c75059e0e89af5-Supplemental.pdf).
- **Status:** scoped dependency reading for Astra request 7b8ff15, **not fully read**.
- **Main-reader coverage, November 25, 2026:** main pp. 2–8, concentrating on notation, §§2–3, model assumptions, Algorithm 1 and Theorems 5–6. The beginning of §4 on p. 8 was also read, not the full experiments. Supplement p. 12, Theorems 10–11 and the beginning of the consistency proof, was read. Original main pp. 6 and 8 and supplement p. 12 were inspected visually. Remaining main pages, remaining supplemental proofs, complete experiments and reference lists remain unread.
- **Verification:** model and theorem-statement comparison only. No complete proof audit, reproduction or formal verification.

## 1. Target and base model

The loss target on main p. 2 is balanced error,

\[
E_P^\ell(f)=\tfrac12\mathbb E_{P_+}\ell(f(X),+1)
+\tfrac12\mathbb E_{P_-}\ell(f(X),-1).
\]

It fixes equal class weights and is invariant to class prevalence. It is different from ordinary risk under an arbitrary target label marginal.

Main §2, p. 3, uses common class-conditional distributions \(P_+,P_-\) across bags. The independent-instance model samples features iid from \(\gamma_iP_++(1-\gamma_i)P_-\). The independent-bag model permits within-bag dependence while fixing the one-point mixture marginals. Bags are independent in this preliminary model.

Mutual-contamination pairs have distributions

\[
P^\kappa_+=(1-\kappa_+)P_++\kappa_+P_-,
\qquad
P^\kappa_-=(1-\kappa_-)P_-+\kappa_-P_+,
\]

with \(\kappa_++\kappa_-<1\). An inverse mixing correction to the loss gives an unbiased estimate of clean balanced error. Small mixture separation amplifies error.

## 2. Actual LLP uses realized bag counts

The opening of main §3, p. 5, defines observed data as \((b_i,\widehat\gamma_i)\), where \(b_i\) contains \(X_{ij}\) and

\[
\widehat\gamma_i=\frac1{n_i}\sum_j\frac{Y_{ij}+1}{2}.
\]

The labels in that count are the labels of the feature instances in the same bag. A separate true proportion \(\gamma_i\) can be random.

On p. 6, CIIM draws labels conditionally iid with mean \(\gamma_i\), then independent features with the corresponding class-conditional laws. CIBM permits dependent labels and features within a bag, while requiring the stated conditional feature marginals and \(\mathbb E[\widehat\gamma_i\mid\gamma]=\gamma_i\). Its stronger CIBM′ imposes each label's individual marginal. Dependence across the true proportions is allowed. This is more specific than arbitrary unlinked feature and label samples that merely share a context name.

## 3. The separate known-population-proportion result

Main §3.1, p. 6, explicitly studies a distinct, less realistic case in which true \(\gamma_i\) are known. Pair bags with \(\gamma_i^-<\gamma_i^+\), convert them to contamination pairs, and apply Theorem 5, p. 5. Under independent instances and the stated bounded-function/Rademacher condition, optimized weights yield a generalization-error scale proportional to

\[
\left(\sum_i\bar n_i(\gamma_i^+-\gamma_i^-)^2\right)^{-1/2},
\]

with loss, function-class and confidence factors. Here \(\bar n_i\) is the harmonic mean of the two feature-bag sizes. Under the weaker dependence model the corresponding expression replaces \(\bar n_i\) by 1.

With true proportions supplied, this population-mixture result does not need their values to be realized counts of the feature samples. Independently estimating those probabilities would add statistical error and requires control relative to mixture gaps. It is not the unchanged known-proportion theorem.

## 4. Empirical proportions require the separate merging theorem

Main §3.2, pp. 7–8, explains why plugging in empirical proportions can reverse the ordering of a bag pair. It merges small bags into paired larger bags. Theorem 6 imposes the (LP) condition on the sequence of **true** proportions. This supplies a positive fraction of separated neighboring pairs and a concentration bound for merged gaps. The conditional unbiasedness uses the actual labels of the feature bags.

The theorem gives a high-probability uniform deviation bound for bounded decision functions and Lipschitz losses under CIIM or CIBM. It does not assume that mere observed count variation is population heterogeneity. When all true proportions are identical, the required positive separation is absent.

Supplement p. 12, Theorem 10 extends the merging scheme. Theorem 11 states balanced-error consistency with a compact input space, bounded universal kernel, increasing merge size \(K\), increasing remaining bag count \(N/K\), \(N=O(K^\beta)\), regularization tending to zero with \(\lambda(N/K)/\log(N/K)\to\infty\), and (LP) plus CIBM. The full proof was not read.

## 5. Scope of the comparison

It would be inaccurate to label this entire paper as learning only from known population proportions. It includes both realized-count and known-proportion experiments, with different results.

The common class-conditional laws provide the population-mixture link. They correspond to \(X\perp C\mid Y\) at the one-point level. This is not the direction \(Y\perp C\mid X\) that would justify a stable conditional-prediction bridge from separate context–feature and context–target panels. Balanced error is also not the next-word log-loss target.

Reversing the roles gives a closer population connection: take the paper's class label to be input \(D\), its feature to be target \(Y\), and the bag context to be \(T\). The shared feature laws then express \(Y\perp T\mid D\), with TD estimating mixing weights and TY sampling the mixture. The located binary balanced-error theorem still does not supply the multiclass next-word result or the cost of estimated weights.

The [completed Busa-Fekete note](BUSA-FEKETE-2025-NEARLY-OPTIMAL-LLP.md#8-requested-comparison-independent-panels-from-common-contexts) contains the requested comparison and independent-panel calculation. No broader reading or stronger transfer claim is implied by this scoped note.
