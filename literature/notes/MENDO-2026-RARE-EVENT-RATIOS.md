# Mendo (2026): paired sequential estimation of relative risk and log ratios

## Identity, edition and actual coverage

Luis Mendo, **Efficient estimation of relative risk, odds ratio and their logarithms for rare events**.

- Read edition: [arXiv:2604.04278v2](https://arxiv.org/abs/2604.04278v2), September 29, 2026, 21:47:47 UTC; [28-page PDF](https://arxiv.org/pdf/2604.04278v2) and [complete TeX](https://arxiv.org/src/2604.04278v2). First submission: April 5, 2026.
- Authenticated publication: [Journal of Statistical Theory and Applications 25, article 37 (2026)](https://doi.org/10.1007/s44199-026-00191-w), received April 18, accepted August 31, published September 30, 2026. This is a reviewed journal paper, not an OpenAI/Anthropic release.
- **Fully read on November 25, 2026, Shanghai:** the main assistant personally read all active text and formulas of §§1–5, all ten proof subsections A.1–A.10, all three algorithms, nine figures and their captions, and all 18 printed references. The concluding paragraph crosses pp.16–17; Appendix A occupies pp.17–27 and references pp.27–28. There are no numbered tables or body footnotes.
- The source has one substantive TeX file, Mendo4.tex, with appendix and bibliography embedded. Comments and text after end-of-document were excluded from the reading edition. All nine plotted figures were inspected on original PDF pages 9, 11, 12, 13, 14 and 16; dense estimator formulas were also checked on p.5. The disputed Eq.(102) was checked against original PDF text on p.27 and the publisher's current HTML, not inferred from an OCR disagreement.
- A supporting assistant retrieved the 31-page journal PDF and authenticated its provenance. Its different typesetting and unreliable mathematical extraction prevent a claim of full edition equivalence. The full-reading designation here is specifically for arXiv v2. Current publisher HTML separately confirms Eq.(102) and the relevant surrounding argument.
- Source retrieval before the execution container disconnected: tmp/source_candidates/sample-only-discovery-2026-11-25/2604.04278v2/. The PDF and source archive were 974,224 and 767,411 bytes respectively. These temporary files are not durable corpus guarantees; the versioned primary URLs above are the recovery sources. No empirical replay, Lean proof or whole-paper certification was performed.

## Original problem and sampling experiment

Two populations supply independent Bernoulli observations with fixed unknown probabilities \(p_1,p_2\in(0,1)\). The four targets are

\[
\mathrm{RR}=p_1/p_2,\quad
\mathrm{LRR}=\log(p_1/p_2),\quad
\mathrm{OR}=\frac{p_1(1-p_2)}{p_2(1-p_1)},\quad
\mathrm{LOR}=\log\mathrm{OR}.
\]

The goal is a prescribed **relative MSE** for RR/OR, or ordinary MSE for LRR/LOR, uniformly over the two probabilities. It is not a fixed-width confidence interval or a time-uniform confidence sequence. The sample count is random, almost surely finite at each interior parameter pair, with an expectation that diverges in rare-event limits.

The physical sampling restriction is equal numbers of observations from the two populations: one observation from each per acquired pair. This differs from merely requiring equal expected sample counts. Independent outcomes within and across pairs are assumed. The paper does not allow arbitrary dependence between the two sources or probabilities that change during an estimation run.

Its central construction reduces both two-population problems to estimating the odds or log odds of one auxiliary Bernoulli stream. It imports the two-stage inverse-binomial estimators from Mendo's earlier odds paper. The new contributions concern the transformations, exact paired sampling cost, and efficiency relative to a Cramér–Rao benchmark.

## Auxiliary Bernoulli factories and the actual sampling bill

### RR/LRR: a race between two selected successes

Algorithm 1 repeatedly selects population 1 or 2 with an independent fair coin, requests its next fresh observation, and repeats after a failure. At the first success it returns \(Y=1\) if the selected population was 1 and \(Y=0\) otherwise. Thus

\[
p:=\Pr(Y=1)=\frac{p_1}{p_1+p_2},
\qquad \frac p{1-p}=\mathrm{RR}.
\]

The number of raw requests for one output is geometric with success probability \((p_1+p_2)/2\). Independent repetitions on fresh streams produce iid auxiliary outputs. This is a two-parameter Bernoulli factory; it does not read either probability.

Write \(T_i\) for population-i requests in one run. Proposition 1 gives

\[
\begin{array}{c|cc}
 &Y=1&Y=0\\ \hline
E T_1\mid Y &(1+p_2)/(p_1+p_2)&(1-p_1)/(p_1+p_2)\\
E T_2\mid Y &(1-p_2)/(p_1+p_2)&(1+p_1)/(p_1+p_2)
\end{array}
\]

and \(E T_1=E T_2=1/(p_1+p_2)\). The conditional variance of \(T_1-T_2\), for either output, is

\[
\frac{2[p_1(1-p_2)+p_2(1-p_1)]}{(p_1+p_2)^2}.
\]

The population counts are dependent, and each count's conditional mean depends on the returned output. Replacing this mechanism by a product of arbitrary unconditional means at a dependent stopping time would need justification.

### OR/LOR: discard concordant pairs

Algorithm 2 draws a fresh pair and repeats whenever the two outcomes agree. A discordant pair returns \(Y=X_1\). Then

\[
p=\frac{p_1(1-p_2)}{p_1(1-p_2)+p_2(1-p_1)},\qquad
\frac p{1-p}=\mathrm{OR}.
\]

Here \(T_1=T_2\) is geometric with parameter \(d=p_1(1-p_2)+p_2(1-p_1)\). Its distribution, and hence its mean \(1/d\), is independent of the returned output. Both Bernoulli transformations terminate almost surely for the stated interior parameters.

### Pair acquisition is not the same as raw consumption

Algorithm 3 is described using samples requested as needed. To implement RR/LRR under paired acquisition, the unused member of each newly acquired pair is buffered for later use. A new pair is drawn only when the requested population's buffer is empty. Remaining samples are discarded at termination.

If \(U_1,U_2\) are consumed observations, the acquired-pair count is

\[
U=\max(U_1,U_2)=\tfrac12(U_1+U_2+|U_1-U_2|).
\]

Thus the actual observation bill is \(2U\), not \(U_1+U_2\). The sampling efficiency factor is
\(\sigma=E(U_1+U_2)/(2EU)\in[1/2,1]\). It equals 1 for OR/LOR, but generally is smaller for RR/LRR. Buffer memory, counters, arithmetic and random-coin costs are not included in the paper's efficiency measure; the prescribed implementation has no deterministic bound on its sample buffer or run length.

## The outer inverse-binomial estimator and accuracy

Fix an integer \(r\ge2\) before this run. Let \(\alpha=1\) for RR/OR and 0 for LRR/LOR.

1. Generate fresh auxiliary Y values until \(r+\alpha\) successes; call the number consumed \(V'\).
2. Continue on fresh observations until \(r-\alpha\) failures; call this second count \(V''\).

The counts are independent negative binomials:
\(V'\sim\mathrm{NB}(r+\alpha,p)\),
\(V''\sim\mathrm{NB}(r-\alpha,1-p)\), counting trials including successes. Equations (16)–(17) use

\[
\widehat\zeta=\frac{rV''}{(r-1)(V'-1)}
\quad\text{for RR/OR},\qquad
\widehat\zeta=H_{V''-1}-H_{V'-1}
\quad\text{for LRR/LOR}.
\]

Here \(H_n=\sum_{j=1}^n1/j\). Neither estimator is a plug-in ratio of fixed-size frequencies.

Theorem 1 states unbiasedness and the bounds

\[
\frac{\operatorname{Var}\widehat\zeta}{\zeta^2}
\le\frac1{r-1}\left(1-\frac{p(1-p)}{r-1+2p}\right)
<\frac1{r-1}
\tag{RR/OR}
\]

and

\[
\operatorname{Var}\widehat\zeta
<
\frac{r^2-r/4-1/4}{(r-1+p)(r-p)(r-1/2)}
-\frac{p(1-p)}{(r-1/2)^2}\left(1-\frac1{2r-3}\right)
<\frac1{r-5/4}.
\tag{LRR/LOR}
\]

For target \(A>0\), the choice \(r=\lceil A^{-1}+\mu\rceil\), with \(\mu=1\) for the ratio targets and \(5/4\) for their logarithms, guarantees the respective MSE below A. These statements price an unbounded sequential run; a fixed query cap, timeout truncation or discarding long runs changes the experiment.

### Bounded independent check of unbiasedness

For \(N\sim\mathrm{NB}(s,p)\), the standard negative-binomial series yields
\(E[1/(N-1)]=p/(s-1)\) for \(s\ge2\), and
\(E H_{N-1}=H_{s-1}-\log p\).
Independence of the two fresh stages therefore gives

\[
E\frac{rV''}{(r-1)(V'-1)}
=\frac r{r-1}\frac{r-1}{1-p}\frac p r=\frac p{1-p},
\]

while the two \(H_{r-1}\) terms cancel for the harmonic difference, leaving \(\log[p/(1-p)]\). This independently supports the claimed means. It does not by itself re-prove every displayed variance constant.

## Sample cost: exact identities and a useful independent check

For RR/LRR, Proposition 3 supplies the full joint mass function of \(U_1,U_2\), summing over the admissible \(V',V''\) and multinomial arrangements of failed requests and successful auxiliary outputs. The exact expectation of their maximum can consequently be written as a double series. Small probabilities make direct evaluation expensive.

Let

\[
B=\frac{r+\alpha}{p_1}+\frac{r-\alpha}{p_2}.
\]

Propositions 3–4 and Appendix A.5 give

\[
EU_1=EU_2=B,\quad
\operatorname{Var}(U_1-U_2)=2B,\quad
B\le EU<B+\sqrt{B/2},
\]

and

\[
\sigma>\frac1{1+1/\sqrt{2B}}.
\]

The upper bound on EU is described once as a “lower bound” in the preceding prose; Eq.(32) and its proof have the upper-bound direction. The lower bound in this passage is the bound on \(\sigma\).

A short independent derivation checks the cost identities without evaluating the joint mass function. Unfold the inner race into raw requests. Stage 1 stops after \(r+\alpha\) occurrences of “choose population 1 and succeed,” a Bernoulli event with probability \(p_1/2\). Stage 2 analogously stops after \(r-\alpha\) occurrences of “choose population 2 and succeed,” with probability \(p_2/2\). Hence \(E(U_1+U_2)=2B\).

Each raw choice contributes an independent fair \(+1\) or \(-1\) to \(D=U_1-U_2\). With the full filtration including observed outcomes, these increments remain conditionally centered with conditional square 1. The total stopping time has finite expectation, so the stopped random-walk identities give \(ED=0\) and \(ED^2=2B\). Cauchy–Schwarz and the maximum identity then yield the upper cost bound. Strictness follows because \(|D|\) is not constant under interior probabilities. The main assistant and a supporting checker assessed this narrow argument; it is not a simulation or a complete proof audit.

For OR/LOR, Proposition 5 gives the exact acquired-pair expectation

\[
EU=\frac{r+\alpha}{p_1(1-p_2)}
+\frac{r-\alpha}{p_2(1-p_1)}.
\]

In particular, LRR costs approximately \(r(1/p_1+1/p_2)\) pairs, with the stated square-root upper correction. Uniform MSE does not imply uniform expected sample cost over \(p_1,p_2\). Counting auxiliary Y values alone would omit the potentially large factory cost.

## Efficiency results and their quantifiers

Equation (36) defines

\[
\eta=
\frac{(\partial_{p_1}\zeta)^2p_1(1-p_1)
+(\partial_{p_2}\zeta)^2p_2(1-p_2)}
{EU\,\operatorname{Var}(\widehat\zeta)}.
\]

This compares the estimator's variance–expected-pair product with the vector Cramér–Rao benchmark for unbiased fixed-size estimation. It is not a measured runtime ratio, a universal optimum over biased procedures, or a proof that the fixed-size lower bound is attained at every finite sample size.

Theorem 2 combines exact cost or sampling factor \(\sigma\) with the sharper variance bound, represented by \(\tau<1\). For example, its RR/LRR lower bound is

\[
\eta>
\frac{[p_2(1-p_1)+p_1(1-p_2)](r-\mu)}
{(r+\alpha)p_2+(r-\alpha)p_1}\frac{\sigma}{\tau}.
\]

For OR/LOR, replace the numerator probability sum by \(p_1(1-p_1)+p_2(1-p_2)\), replace the denominator by
\((r+\alpha)p_2(1-p_1)+(r-\alpha)p_1(1-p_2)\), and omit \(\sigma\).

Write \(\phi=\sqrt{p_1p_2}\), \(\theta=p_1/p_2\), and \(\rho=\max(p_1,p_2)\). Theorem 3 bounds RR/LRR independently of \(\theta\) by

\[
\eta>
\frac{r-\mu}{r+\alpha}
\frac{r-\sqrt{\alpha^2+\phi^2(r^2-\alpha^2)}}{r-\alpha}
\frac{2(r^2-\alpha^2)^{1/4}}
{2(r^2-\alpha^2)^{1/4}+\sqrt\phi}.
\]

Its proof minimizes two positive factors separately over the admissible ratio interval, allowing a conservative lower bound. The expression decreases in \(\phi\), and the lower limiting efficiency as \(\phi\downarrow0\) is at least \((r-\mu)/(r+\alpha)\), itself at least \(1/[1+A(\mu+\alpha)]\).

For OR/LOR, small geometric mean alone is insufficient for a comparable uniform positive bound: one probability can approach 1 while the other approaches 0. Theorem 4 instead uses the stronger condition that the maximum probability is small:

\[
\eta>\frac{r-\mu}{r+\alpha}(1-\rho).
\]

The lower limiting value as \(\rho\downarrow0\) is again \((r-\mu)/(r+\alpha)\). At fixed A, these are near-one lower bounds, not a statement that rare events alone force efficiency to converge exactly to 1. Making A small increases r and improves the lower bound, at additional sampling cost.

## A.10 Eq.(102) is false; the global lower bound survives

The source's final half-axis minimization contains a concrete error. For fixed \(\rho=\max(p_1,p_2)\), define

\[
\omega=
\frac{p_1(1-p_1)+p_2(1-p_2)}
{(r+\alpha)p_2(1-p_1)+(r-\alpha)p_1(1-p_2)}.
\]

Equation (102), p.27, asserts
\(\inf_{\theta\ge1}\omega=(1-\rho)/(r-\alpha)\).
Set \(r=2,\alpha=1,\rho=1/10\) and \(p_1=p_2=1/10\), so \(\theta=1\). Then \(\omega=1/r=1/2\), whereas the claimed infimum is \(9/10\). The same contradiction remains for ratios just above 1 by continuity. Thus the equality fails for the allowed OR parameters.

The invalid step substitutes \(\theta\mapsto1/\theta,\alpha\mapsto-\alpha\) into a monotonicity argument proved with nonnegative \(\alpha\). In particular, the derivative-at-one sign used earlier is no longer preserved. The false equality is also present in the authenticated publisher HTML; it is not solely a preprint extraction problem.

The desired **global** bound has a direct repair. Put \(N=p_1(1-p_1)+p_2(1-p_2)\) and \(D=(r+\alpha)p_2(1-p_1)+(r-\alpha)p_1(1-p_2)\). Then

\[
N\ge(1-\rho)(p_1+p_2),\qquad
D\le(r+\alpha)(p_1+p_2-2p_1p_2)
<(r+\alpha)(p_1+p_2),
\]

so \(\omega>(1-\rho)/(r+\alpha)\). Holding \(p_2=\rho\) and letting \(p_1\downarrow0\) attains that value as a limit. Therefore the global infimum used in Theorem 4 is correct even though Eq.(102) is not. Combining this with Theorem 2 retains the claimed efficiency lower bound. This is a local mathematical correction, not independent certification of the entire paper.

A separate minor reference mismatch occurs in A.7: the OR argument cites Eq.(20), the logarithmic variance bound, where Eq.(18), the ratio relative-variance bound, is the appropriate input. The displayed result has the intended ratio form.

## Numerical evidence and visual reading

The figures report Monte Carlo calculations, not real population data. Each simulated configuration uses \(10^7\) independent realizations of the estimator. The principal ranges are \(\phi=10^{-3}\) to \(10^{-1}\), \(\theta\in\{1,10,0.1\}\), and target A in \(\{0.01,0.04,0.09\}\), corresponding to RMSE levels 10%, 20% and 30%.

- Figure 1 shows the paired-buffer sampling factor for RR; it is close to 1 in the tested range, and the analytic lower bound stays below the simulated values.
- Figures 2–5 compare efficiency for RR, LRR, OR and LOR against the author's earlier group-sampling method, specialized to one observation from each population. The new procedure performs particularly well at small probabilities. The comparison is with that named predecessor, not all possible estimators.
- The logarithmic targets are invariant to exchanging the populations. Consequently the LRR/LOR plots omit the redundant ratio 0.1. Ratio-target efficiency need not have this symmetry because the success counts are \(r+1\) and \(r-1\).
- For OR/LOR at \(\theta=1\), efficiency is independent of \(\phi\). At unequal ratios it deteriorates as probabilities grow; the plot evidence does not imply uniform dominance near all parameter boundaries.
- Figures 6–9 compare ratio-specific bounds with the ratio-independent bounds. The comparison uses 25 logarithmically spaced ratio values from 0.001 to 1000, only where the probability constraints permit them.
- The author's numerical examples for A=0.04 give lower efficiencies above 91.5%/93.5% for RR/LRR when \(\phi\le0.01\), and 91.6%/94.4% for OR/LOR when \(\rho\le0.01\). The stated rare-event lower limits exceed 92.5% and 95.3% respectively.

The complete figures and axes were read, but the \(10^7\)-run experiments were not repeated. The inspected source archive contains figures and manuscript material, not an authenticated complete simulation implementation. Finite simulation agreement is not a proof of uniform MSE.

## Proof structure and dependencies

A.1 derives conditional geometric laws and mixed moments for the selection race. A.2 uses the discordant-pair geometric law and independence of output and waiting time. A.3 explicitly imports Theorems 1 and 3 of the earlier odds paper. A.4 enumerates permissible input arrangements for the joint count distribution. A.5 uses total variance conditional on the two inverse-binomial counts, then the absolute-difference bound. A.6 computes OR/LOR cost from output-independent factory waiting times. A.7 differentiates the target and substitutes cost and variance bounds. A.8 gives the admissible relation among \(\theta,\phi,\rho\). A.9 minimizes the RR/LRR factors. A.10 supplies the OR/LOR minimization, subject to the Eq.(102) correction above.

Other references provide historical inverse-binomial sampling, sequential estimation, Cramér–Rao theory, multiparameter factories, and random-bit extraction. Reading their uses here does not mark those works fully read.

### Current correction notice on the principal imported source

The earlier [Estimating odds and log odds with guaranteed accuracy](https://doi.org/10.1007/s00362-024-01639-w), Statistical Papers 66, article 26 (2025), has a [September 25, 2026 correction](https://doi.org/10.1007/s00362-026-01906-y). The original publisher page specifically says Eq.(61) was updated. The exact correction body is subscription-blocked in this session.

Its public [arXiv:2404.17705v4](https://arxiv.org/abs/2404.17705v4) is dated December 12, 2024, so it cannot be presumed to incorporate that later correction. A scoped primary HTML reading covered the setup, odds Theorem 1 and proof, the log-estimator variance discussion and Theorem 3 with proof, and the displayed Eq.(61). Figures and the complete bibliography were not read; this predecessor remains **partially read**.

The v4 Theorems 1 and 3 contain the variance expressions imported by the 2026 paper. Its Eq.(61) is in the efficiency discussion and visibly writes the variance of the odds estimator in the log-odds efficiency formula; the surrounding definition calls for the log-odds estimator. This identifies an apparent notation issue in the old public version, but does not establish the inaccessible correction's exact replacement text. Preserve the correction link and version distinction rather than silently treating the 2024 PDF as the current journal text.

## Limits and follow-up

The useful result is an unbiased, prescribed-MSE estimator for a fixed pair of probabilities under a specified sequential sampling protocol, with transparent expected query cost. High-probability or time-uniform claims, adaptive model selection, evolving feedback states, finite-bit storage and fresh-token predictive-risk guarantees are not proved.

A future application would need to specify which two independent fixed-probability streams are available, whether both are priced equally, whether the stopping rule and buffering are executable, and how multiple or adaptive estimates are controlled. No FP theorem or learning-rule modification is proposed here.

Follow-up priorities are the recent variance-adaptive confidence-sequence paper by Chugg–Ramdas, and the separate debiased/fixed-automaton Bernoulli-factory candidates. The inaccessible exact text of the predecessor's correction remains an edition-verification question, not a reason to label either predecessor fully read. Astra retains the decision on integration.
