# Huang 2026: shared randomness, private support and parallel permutation sampling

## Edition and deliberately scoped reading

**Haoxiang Huang. _Shared Randomness and Parallel Rounds in Permutation Sampling_. arXiv:2611.01028v2, 18 November 2026, 17:39:40 UTC.** The original submission was 31 October 2026. [Exact primary record](https://arxiv.org/abs/2611.01028v2), [PDF](https://arxiv.org/pdf/2611.01028v2), [source](https://arxiv.org/src/2611.01028v2).

Pro-A completed a **scoped reading**, not the whole 80-page paper, on 26 November 2026. The question was how conditional independence within a round constrains exact permutation sampling, and how a fixed shared seed can attain the resulting bound.

Actual coverage: frontmatter, Sections 1–3, Table 1, all of Appendices A and B, and all 34 bibliography entries. This includes the complete proofs of the private-support recurrence, finite conversion, monotone-schedule comparison, exact finite optima, exact asymptotic rates and finite group averaging. In the single active `v2.1.tex`, the substantive blocks are lines 110–481 and 1841–3036, plus the frontmatter and bibliography. Appendix A occupies physical pages 15–29 and Appendix B the remainder of page 29. Six original PDF pages, 3, 5, 16, 18, 25 and 28, were visually checked.

Sections 4–7 and Appendices C–J remain unread except for statements mentioned in the introduction/model. Their sharp positive-error rates, strict adaptive-entropy advantage, collision bounds, one-round approximate tensor-rank result and injection extension are **not** assessed by this note. Figure 1 belongs to that unread part. The statement of the common-part reweighting lemma in Section 2 was read, but its proof was not.

Prepared files are in ignored `literature/corpus/arxiv/2611.01028v2/`. PDF SHA-256 is `1e39de75b92b3456fdaf1fce2a99a4e04a5fb6468217f8f862919b1259537127`, and source archive SHA-256 is `4906b35f33cc497c2f6c0a60b7ad7662e82e30eafabcef7645b349c061f4ce71`. The complete source has 7,216 lines, one table, one figure and one affiliation footnote. No separate publisher edition was authenticated. AI involvement is undetermined. No disclosure was found by the bounded source search, which does not establish absence of assistance.

The main reader personally covered the stated sections. A secondary check was limited to the three exchanges proving the high-round finite optimum and its boundary cases. Another bounded check authenticated a cited common-source predecessor. No enumeration script, numerical experiment, full-paper certification or formal verification was performed.

## 1. Resources and the exact sampling problem

The target is the uniform distribution on the \(n!\) permutations of \([n]\), represented as words in \([n]^n\). At each stage the protocol can draw a finite-valued shared variable \(Z_t\), choose a batch \(A_t\) of unwritten coordinates, and write that batch. Conditional on the entire public history and \(Z_t\), the coordinates in the batch are independent. Every coordinate is written once. At most \(R\) nonempty batches occur on every execution.

The entire earlier output and the shared draws are publicly accessible. Private coins and computation are free. All other random choices, including random selection of the next batch, count as shared randomness. Empty stages can draw shared randomness without consuming an output round. Static protocols draw their entire shared seed before the first output. Adaptive protocols can draw it later, conditional on the history.

Logarithms are natural. For a finite protocol \(Q\), the two costs are

\[
B(Q)=\max_{\text{positive-probability executions}}
\sum_t\log|\operatorname{supp}Q(Z_t\mid\mathcal H_t)|,
\qquad
C_H(Q)=\sum_t H_Q(Z_t\mid\mathcal H_t).
\]

Thus adaptive support cost is a maximum accumulated branching cost. It is not simply the entropy of the final shared transcript. Static support cost is \(\log|\operatorname{supp}Z|\), and static entropy cost is \(H(Z)\). The protocol permits arbitrary finite distributions and arbitrary kernels. Numerical description precision and computational time are not charged.

Write \(B_0^{\mathrm{st}},B_0^{\mathrm{ad}},C_0^{\mathrm{st}},C_0^{\mathrm{ad}}\) for their optimal exact-sampling costs. The finite protocol model is sufficient for the results recorded below. The paper's extension to almost-sure termination lies outside the checked proof scope.

## 2. Private support is an explicit dynamic program

Suppose \(m\) labels remain and a private batch writes \(b\) coordinates. To avoid collisions with probability one, its coordinate supports must be pairwise disjoint subsets of the unused labels. If two supports share a label of positive probability, independence gives a positive collision probability. Conversely, disjoint supports suffice.

Their product size is maximized by using all labels and balancing the sizes. With \(m=ub+v\), \(0\le v<b\), define

\[
L(m,b)=u^{b-v}(u+1)^v.
\]

Let \(F(n,R)\) be the largest number of permutations in the support of a collision-free private-coin protocol using at most \(R\) rounds. Lemma A.1 proves

\[
F(n,R)=\max_{1\le b\le n}L(n,b)F(n-b,R-1),
\qquad F(0,R)=1,
\qquad F(n,0)=0\quad(n>0).
\]

Every first-round output has at most \(F(n-b,R-1)\) continuations, even if the later batch sizes depend on that output. Balanced uniform draws followed by a relabeled maximizing continuation attain the recurrence and are uniform on the resulting support.

For \(R\le n\), it is equivalent to maximize over deterministic compositions \(b_1+\cdots+b_R=n\):

\[
F(n,R)=\max_{\mathbf b}\prod_{t=1}^R L(m_t,b_t),
\qquad m_t=\sum_{j=t}^R b_j.
\]

Splitting a non-singleton batch can only increase the attainable count, so exactly \(R\) nonempty parts can be used. This does not restrict the original adaptive model. It proves an extremal count in that model has a schedule representation.

Define the entropy shortfall

\[
\Delta(n,R)=\log n!-\log F(n,R).
\]

The transcript chain rule gives the exact lower bound for any static or adaptive sampler:

\[
\log n!\le C_H(Q)+
\mathbb E\sum_t\log L(m_t,b_t)
\le C_H(Q)+\log F(n,R).
\]

Consequently every entropy cost is at least \(\Delta\). Proposition A.3 sharpens the support lower bound to \(\log\lceil n!/F(n,R)\rceil\). The ceiling follows because the exponential of the maximum support cost of a finite protocol is an integer. None of these arguments equates an entropy bound with finite persistent memory.

## 3. Why a static seed attains the deficit within a universal constant

Theorem 3.1 and its precise Appendix A version, Theorem A.13, state

\[
\Delta\le C_0^{\mathrm{ad}}
\le C_0^{\mathrm{st}}
\le B_0^{\mathrm{st}}<\Delta+38,
\qquad
C_0^{\mathrm{ad}}\le B_0^{\mathrm{ad}}\le B_0^{\mathrm{st}}.
\]

The constant is **38 nats**, uniformly in \(n\) and \(R\). It is an upper-bound constant, not a claimed optimum. General exact equality of all four costs is not asserted.

### Recycling balanced partitions

Let \(A(M,b)\) count ordered balanced partitions of \(M\) labels into \(b\) parts, with prescribed locations of the larger parts. If \(M=ub+v\), then

\[
A(M,b)=\frac{M!}{(u!)^b(u+1)^v}.
\]

A uniform such partition, followed by one independent uniform draw from each part, produces a uniform ordered injection. Given that injection, the residual partition is uniform over its compatible partitions. Lemma A.4 gives

\[
\frac{A(m,b)}{A(m-b,b)}=\frac{(m)_b}{L(m,b)}.
\]

Thus the same shared partition can serve successive equal-sized batches. Each chosen label is removed from its part. The construction does not resample a completely independent partition every round.

When batch size increases, the partition must be converted to a uniform partition with more parts. This is where an entropy-only common-source theorem would be insufficient for the claimed finite support bound.

### Finite common source and exact conversion

Lemma A.5 considers a finite family of distributions, each with at most \(d\) outcomes and probability masses in \(S^{-1}\mathbb Z\). It constructs one common finite source, with deterministic maps to every family member, having support at most

\[
2+\frac{\log S}{\log(d/(d-1))}.
\]

At each step choose a largest residual atom in each distribution and peel off their smallest mass. With residual total \(r\), the peeled mass is at least \(r/d\). Residual masses remain multiples of \(1/S\), so geometric contraction forces finite termination. The support bound is independent of the number of family members, while depending on their common probability denominator.

Lemma A.6 then converts a uniform source on \([A]\), plus an independent finite source, to uniform on \([K]\), for \(K\ge A\). Writing \(\chi=K/A\) and \(a=A/\gcd(A,K)\), the extra source can have support at most

\[
\chi+1+\frac{\log(2a)}{\log(3/2)}.
\]

If \(\chi\) is an integer, a uniform source on \([\chi]\) suffices exactly. The proof overlays integer row and cell partitions of an interval, removes whole cells, and couples the remaining at-most-three-point row laws through Lemma A.5.

For adjacent partition counts, Lemma A.7 proves a large ratio and a small reduced denominator: with \(s=\lfloor M/(b+1)\rfloor\), the ratio is at least \(2^s\), while its reduced denominator divides \(s!\). Along a nondecreasing batch schedule, this makes the excess logarithmic support costs summable. Theorem A.8 bounds their sum by a convergent series below ten nats.

### The nontrivial schedule comparison

The maximizing integer schedule in \(F\) need not already be nondecreasing. Theorem A.12 proves that restricting to nondecreasing schedules loses less than 28 nats of private support. This is essential to the uniform 38-nat statement.

The proof interpolates \(\log L(m,b)\) by the concave homogeneous function \(g(m,b)=b\psi(m/b)\), where \(\psi\) linearly interpolates \(\log u\) at positive integers. An exchange lemma bounds inversions in an optimal integer schedule. A continuous optimal policy supplies quotient runs, and constrained monotone rounding loses less than 25 nats. The full comparison splits an optimal schedule into a sortable prefix and a rounded tail, with losses below \(2+25+1\). Together with the partition-conversion cost below ten, this gives 38.

The complete argument was read. This note does not independently certify every quotient-run estimate or the numerical constant. The bounded independent checks concentrated on the support recurrence, entropy accounting, partition recycling, finite common-source construction and the finite high-round theorem.

## 4. Exact finite cases and their algebraic construction

| Regime | Maximal private support | All four optimal exact costs |
|---|---:|---:|
| \(R=1\) | \(1\) | \(\log n!\) |
| \(R=2\), \(n\ge2\) | \(G(n)\) | \(\log(n!/G(n))\) |
| \(\lceil n/2\rceil\le R\le n\), \(d=n-R\) | \(n!/\binom{2d}{d}\) | \(\log\binom{2d}{d}\) |

Here \(G(n)\) is the largest product of positive integers summing to \(n\):

\[
G(n)=
\begin{cases}
3^{n/3},&n\equiv0\pmod3,\\
4\,3^{(n-4)/3},&n\equiv1\pmod3,\\
2\,3^{(n-2)/3},&n\equiv2\pmod3.
\end{cases}
\]

### Cosets provide the two-round upper bound

Lemma A.17 partitions coordinate positions into blocks and chooses a subgroup \(H_j\) on each block with a base of length at most \(R-1\). A base is a list of positions whose images determine a group element. For \(H=\prod_jH_j\), a uniform coset representative supplies a seed with \(n!/|H|\) values.

Within each block, the protocol samples the next base image uniformly from its conditional orbit. Equal stabilizer fibers give the conditional distribution of a uniform group element. Different blocks sample independently in the same round. Once the bases are exhausted, all remaining images are determined and written in a final batch. This produces uniform output inside the chosen coset, hence a uniform permutation overall.

For two rounds, take cyclic groups on blocks of sizes two and three realizing \(G(n)\). Each has a one-point base. This attains the lower bound exactly, rather than merely covering the permutation set with overlapping private supports. The cited historical predecessor is Diaconis–Shahshahani's subgroup algorithm. Its original paper was not read here.

### Singletons followed by pairs are optimal at high round count

Theorem A.19 uses three schedule exchanges: split a batch, move a singleton earlier, and replace \((1,2,\ldots,2,b)\), \(b\ge3\), by one more pair followed by \(b-1\). The crucial third comparison follows from

\[
L(M,b)\le\frac M4L(M-1,b-1),\qquad M\ge4,\ 3\le b\le M.
\]

Merge the two smallest balanced parts \(x,y\) into \(x+y-1\). The other parts have total at least two, and

\[
4xy\le(x+y+2)(x+y-1)\le M(x+y-1).
\]

The exceptional \(M=3\) case is handled separately and gives equality in the exchange. If a schedule has \(s\) singletons and excess \(E=\sum_t(b_t-2)_+\), then \(s-E=2R-n\ge0\). Thus a singleton remains available whenever a larger-than-pair batch remains. Each exchange decreases \(E\), proving termination with \(n-2d\) singletons and \(d\) pairs.

The first coordinates are sampled sequentially without replacement. A single seed chooses a uniform bipartition of the final \(2d\) labels into two parts of size \(d\), and each remaining round draws one label from each part. Partition recycling proves exact uniformity. The seed has \(\binom{2d}{d}\) values. Endpoints \(d=0\), even \(n\) at \(R=n/2\), odd \(n\) at \(R=(n+1)/2\), and the \(M=3\) exchange were included in the bounded secondary check. No local problem was found.

## 5. Consequences and asymptotic statements within the read scope

**Direct finite difference, derived in this note.** In the high-round regime, let \(d=n-R\ge1\). One extra round saves exactly

\[
\log\frac{\binom{2d}{d}}{\binom{2d-2}{d-1}}
=\log(4-2/d)
\]

nats of each optimal exact cost. In bits this is \(\log_2(4-2/d)\), from one bit at \(d=1\) toward two bits as \(d\) grows. This is a consequence of the source's exact formula, not a new asymptotic theorem.

For each fixed \(R\), Corollary A.14 gives

\[
\log F(n,R)=\lambda_Rn+O_R(1),
\qquad
\lambda_1=0,
\qquad
\lambda_r=\max_{u\in\mathbb N}
\frac{\log u+(u-1)\lambda_{r-1}}u.
\]

The dependence on fixed \(R\) in this error is material. It is not the same uniform constant as the 38-nat comparison between resource cost and \(\Delta\). For \(R/n\to\rho\in(0,1]\), Theorem A.15 gives \(\Delta(n,R)/n\to\Phi(\rho)\), where \(\Phi\) is piecewise affine through \((1/j,\log j)\). The proof truncates large batches to bounded size, pays a harmonic correction, applies convexity with coordinate weights, then uses batches of two consecutive sizes for the matching bound.

**Finite group averaging, Appendix B.** For a transitive finite group action on a target set of size \(M\), assume the action preserves the permitted private protocols and round bound. If a private protocol is uniform on \(F\) target points, a mixture of \(J\) fixed relabelings satisfies

\[
\operatorname{TV}(Q_J,\operatorname{Unif}(\mathcal T))
\le\frac12\sqrt{\frac{M/F-1}{J}}.
\]

Randomly select the relabelings, compute the coordinate variances, and apply Cauchy–Schwarz. Some fixed choice attains the expectation bound. One uniform shared index implements that mixture. For the permutation protocol above, a sufficient seed size for error \(\varepsilon>0\) is therefore

\[
J=\max\!\left\{1,
\left\lceil\frac{e^{\Delta(n,R)}-1}{4\varepsilon^2}\right\rceil\right\}.
\]

This is a direct sufficient construction from the read lemma. It neither proves the paper's sharp approximate frontier nor replaces the exact zero-error conversion theorem.

## 6. Scoped predecessor comparison: finite support is not entropy

Appendix A cites only Han–Hoshi 1997, Li 2021 and Diaconis–Shahshahani 1987. These references identify interval generation, common-source coupling and subgroup sampling predecessors. The exact finite conversion and schedule estimates are proved in Huang's appendix itself.

Cheuk Ting Li, _Efficient Approximate Minimum Entropy Coupling of Multiple Probability Distributions_, [arXiv:2006.07955v2](https://arxiv.org/abs/2006.07955v2), revised 17 January 2021, appeared in IEEE Transactions on Information Theory 67(8):5259–5268, DOI [10.1109/TIT.2021.3076986](https://doi.org/10.1109/TIT.2021.3076986). Only the common-source definitions, Theorems 8 and 11, and surrounding interpretation were checked in the [author HTML](https://arxiv.org/html/2006.07955v2). The full proof and the separate IEEE typesetting were not read.

Li's Theorem 11 supplies exact deterministic aggregation maps from one finite source for \(m\) distributions on an \(a\)-point alphabet, with support at most \(m(a-1)+1\), alongside entropy guarantees. The title's approximation concerns entropy optimality, while the marginals in that theorem match exactly. Thus finite common sources are already explicit in that predecessor. Its Theorem 8 also gives an exact conversion through an independent geometric source, whose entropy is finite but whose support is infinite. Neither statement directly gives Huang's rational-mass, family-size-independent support estimate \(2+\log S/\log(d/(d-1))\). This is a bounded comparison of statements, not a novelty certificate.

Han and Hoshi's _Interval Algorithm for Random Number Generation_, IEEE Transactions on Information Theory 43(2):599–611, is a historical method reference only in this intake. No historical full reading was initiated.

## 7. What is established for use and what is not

The selected material supplies explicit combinatorial resource bounds and exact constructions under a known target and a supplied protocol model. It separates output entropy, privately generated entropy, shared-source support, expected shared entropy, number of output rounds and free history access. The algebraic coset construction and the finite common-source argument are reusable mathematical tools within their hypotheses.

The read proof supports source-grounded use of the exact frontier, with the independent checking limits above. No counterexample was found in the inspected elementary core or high-round exchanges. The detailed monotone-rounding constant remains a source theorem read for comprehension, without independent certification.

For FP, no finite-state or learning conclusion follows from the saved shared random bits. The protocol can retain the entire growing output, use arbitrary computation and choose arbitrary kernels. Its uniform-permutation target is known. A transfer would need a specific target distribution, the required conditional product structure, exact treatment of public history and a matching resource measure. No such FP mapping is established here. No architecture, experiment or core definition is changed.
