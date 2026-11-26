# Kelman et al. 2026: constructing algebraic tests with private query uncertainty

## Source, edition and actual coverage

**Esty Kelman, Uri Meir, Debanuj Nayak and Sofya Raskhodnikova, _Homomorphism Testing with Resilience to Online Manipulations_, APPROX/RANDOM 2026, LIPIcs 392, article 58, pages 58:1–58:24, published 9 September 2026.** [Official record and CC BY 4.0 article](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.APPROX/RANDOM.2026.58) · [Official PDF](https://drops.dagstuhl.de/storage/00lipics/lipics-vol392-approx-random2026/LIPIcs.APPROX-RANDOM.2026.58/LIPIcs.APPROX-RANDOM.2026.58.pdf) · [Official HTML](https://drops.dagstuhl.de/storage/00lipics/lipics-vol392-approx-random2026/html/LIPIcs.APPROX-RANDOM.2026.58.html).

Pro-A personally read all 24 pages of the official final on 27 November 2026, Shanghai: front matter, Sections 1–5, all printed proofs and formulas, four algorithms, eight scientific footnotes and all 60 references. There are no figures, tables or appendices in this edition. Original PDF pages 11, 15, 16, 18, 19 and 20 were visually checked, including the complement bars and conditional events in the amplification proof. Reliable PDF extraction supplied the complete text.

The paper sends several proofs to its longer author version. The fixed **arXiv:2511.23363v1**, submitted 28 November 2025 at 17:09:08 UTC, has 36 physical pages and is separately indexed as **scoped reading**. [Version record](https://arxiv.org/abs/2511.23363v1) · [PDF](https://arxiv.org/pdf/2511.23363v1) · [TeX](https://arxiv.org/src/2511.23363v1). Actual supplementary coverage is the front matter and main result statements, the omitted small-distance claims, all of Sections 4–6, and Appendix A. In its sole active body file these are lines 1–240, 449–537 and 785–1595. Section 4 was compared to the final rather than adopted unchanged. The v1 bibliography and remaining main-body sections were not completely read. Its selected physical PDF pages 23, 26, 29, 30 and 35 were checked visually. The source contains nine algorithms, no figure or table assets, eight scientific footnotes, four author thanks and 59 bibliography entries. The original `.bib` is absent but the generated `.bbl` is present.

**The final and v1 are not identical.** The final corrects the rejection direction of v1 Algorithm 3 and replaces the cross-iteration amplification argument with an explicit conditional-history argument. The current theorem is evaluated using that final proof. The old version is not credited as a second full reading, and its superseded amplification argument is not presented as a defect in the final.

Support readers checked source identity, the reservoir interface and two bounded deductions. The main reader covered the scientific text specified above. Historical group-generation and property-testing results are read as quoted in these editions, not independently in their original papers. No AI-use disclosure was found in the read material, which does not establish actual use. No implementation, formal replay, global dependency audit or experiment was performed.

## 1. Main construction and observation model

The paper constructs algebraic tests whose next query remains dispersed **after the previous query locations are known**. The group operation creates a relation to test. A privately selected signed subword of a queried reservoir makes the final location difficult for an online adversary to anticipate. The soundness and uncertainty analyses are separate, then joined by a conditional amplification lemma.

There is a second, simpler constructive route: a small random set generates the domain group, its observed labels determine a unique candidate homomorphism when consistent, and fresh uniform observations validate that candidate. Section 7 below makes the implicit extension operation into a finite algorithm with explicit local computation and memory costs.

Let \(G,H\) be finite, known groups. This note uses multiplicative notation, preserving the printed order of every noncommutative product. The original function \(f:G\to H\) is fixed. Distance is uniform relative Hamming distance,

\[
\varepsilon_f=\min_{h\in\operatorname{HOM}(G,H)}
  \frac{|\{x:f(x)\ne h(x)\}|}{|G|}.
\]

The tester distinguishes exact homomorphisms from functions with \(\varepsilon_f\ge\varepsilon\). It has no required decision in the intermediate band. Uniform domain sampling, group operations, inverses and equality tests are available. These are access assumptions, not learned operations.

The queried oracle \(f'\) initially equals \(f\). After each answer, an adversary obtains a budget of \(t\) modifications, which may be accumulated. It can erase an entry to \(\perp\), or in the stronger model corrupt its value. It observes the query history but not unexposed private random choices. The adversary changes the oracle, not the tester's cache or computation. The property and distance continue to concern the original \(f\). An iteration containing an observed erasure is accepted rather than used as a rejection certificate. This preserves one-sided completeness for erasures. Corruption guarantees are generally two-sided.

### Principal source theorems

The following are author results, with universal sufficiently small constants \(c>0\). All upper bounds achieve success at least \(2/3\) against the budget-managing corruption model and have one-sided error for erasures. Logarithmic bounds concern \(t\ge1\), with the no-adversary case treated by the standard tester.

| Source statement | Query bound | Permitted modification rate |
|---|---|---|
| Final Theorem 1.1, all finite \(G,H\) | \(O(\varepsilon^{-1}+\log_2t)\) | \(t\le c|G|\min\{\varepsilon^2,1/\log^2|G|\}\) |
| Final Theorem 1.3, sample-based | \(O(\varepsilon^{-1}+E(G))\) | \(t\le c|G|\min\{\varepsilon^2,1/E(G)^2\}\) |
| Final Theorem 1.5, \(G=\mathbb F_p^n,H=\mathbb F_p^r\) | \(O(\varepsilon^{-1}+\log_pt)\) | \(t\le cp^n\min\{\varepsilon^2,1/n^2\}\) |

Here \(E(G)\) is the expected number of independent uniform samples needed to generate \(G\). The source imports constant or small bounds for important group families. This note does not independently verify those historical classification-dependent results.

Theorem 1.6 gives an \(\Omega(\log_pt)\) erasure lower bound for \(\mathbb F_p^n\to\mathbb F_p\), sufficiently large \(n\), and \(0<\varepsilon\le(p-1)/(2p)\). The general-group optimality assertion is a worst-group statement. It does not say every pair \(G,H\) requires the logarithmic term. For example, if the only homomorphism is the identity-valued constant map, the algebraic property reduces to testing that constant. Distinct prime characteristics give this situation.

These are primarily **query bounds**. They do not imply the same bound on group computation, representation length, random bits or resident memory.

## 2. Random signed words give sound tests for noncommutative groups

For even word length \(L=2k\), sample independent uniform \(x_1,\ldots,x_L\in G\) and signs \(\sigma_i\in\{+1,-1\}\). Query their labels and the final product,

\[
a=\prod_{i=1}^{L}x_i^{\sigma_i},
\qquad
\text{reject if}\quad f(a)\ne\prod_{i=1}^{L}f(x_i)^{\sigma_i}.
\]

The inverse in the right-hand expression is taken **after** querying \(f(x_i)\). The algorithm does not assume that an arbitrary input function satisfies \(f(x^{-1})=f(x)^{-1}\).

Every homomorphism passes. Final Theorem 3.1 proves

\[
\Pr[\text{reject}]\ge
\min\left\{\frac{(2k-3)\varepsilon}{3},\frac1{16}\right\}
\quad\text{when }\varepsilon_f\ge\varepsilon.
\]

The signs are substantive. An unsigned length-\(L\) check can accept shifted homomorphisms: in the additive group \(\mathbb Z_{L-1}\), a nonzero shift \(f=h+s\) satisfies the long-word equation because \(Ls=s\). Length and inverse symmetry must be chosen together.

### Small-distance proof

For a closest homomorphism \(g\), first fix the signs and compare the ordered products of \(f\)-labels and \(g\)-labels. Write \(p_j\) for their agreement probability after \(j\) independent factors. A single corrupted factor cannot disappear when every other factor agrees, even without commutativity. Hence

\[
1-p_j\ge j\varepsilon_f(1-\varepsilon_f)^{j-1}.
\]

For \(j\le1/\varepsilon_f\), this gives the required linear scale. Appending one independent factor also gives

\[
p_j\le p_{j-1}(1-\varepsilon_f)+(1-p_{j-1})\varepsilon_f.
\]

The source uses this recurrence to keep the disagreement bounded away from zero beyond that range. Since the final product is uniform in \(G\), subtracting its \(f\)-versus-\(g\) error costs only \(\varepsilon_f\). Final Lemma 3.2 obtains

\[
\Pr[\text{reject}]\ge
\min\{(j-3)\varepsilon_f/3,1/6\}
\quad\text{for }\varepsilon_f<1/8.
\]

The detailed omitted claims were read in v1, not inferred from their headings.

### Large-distance proof: high-agreement correction and cancellation

Let \(\mu\) be the rejection probability for length \(2k\). For each \(a\in G\), let \(\operatorname{FIX}(a)\) be the distribution of signed words conditioned to have product \(a\). Each such word votes for \(a\)'s label through \(\prod_i f(x_i)^{\sigma_i}\). Define \(g(a)\) to be its most common vote.

Two independent words from \(\operatorname{FIX}(a)\) can be split, reversed and inverted into two ordinary random signed words with a common product. At least one original test must fail when the corresponding votes disagree. Consequently the collision probability of two votes is at least \(1-2\mu\). If their probability vector is \((p_h)_{h\in H}\),

\[
\max_h p_h\ge\sum_h p_h^2\ge1-2\mu.
\]

This holds for **each** \(a\), not merely on average. Final Lemmas 3.11–3.12 give

\[
\Pr_{\operatorname{FIX}(a)}[\text{vote}\ne g(a)]\le2\mu,
\qquad
\operatorname{dist}(f,g)\le2\mu
\quad(\mu<1/10).
\]

The homomorphism proof uses three compatible words. In block notation, choose ordered blocks \(P,R,S\) whose products are \(ar^{-1},r,rb\). Then

\[
PR=a,\qquad R^{-1}S=b,\qquad PS=ab.
\]

Reverse the order as well as invert each factor when forming \(R^{-1}\). For the corresponding products of observed labels,

\[
(\widehat P\widehat R)(\widehat R^{-1}\widehat S)
 =\widehat P\widehat S
\]

is an identity for every function \(f\). Each of the three words has the required conditional distribution, so all three votes are correct with probability at least \(1-6\mu>0\). That forces the deterministic equality \(g(a)g(b)=g(ab)\). No factors are commuted and no inverse-preservation property of the uncorrected \(f\) is assumed. Combining this result with the small-distance argument gives Theorem 3.1.

## 3. Conditional query uncertainty survives an online adversary

A marginally uniform query is insufficient. In the classical three-point test, \(x\), \(y\) and \(xy\) each have uniform marginals, but the third location is known after the first two. An online adversary can target it.

Final Definition 4.2 instead examines the conditional distribution \(\nu_j\) of query \(j\), given earlier query locations in a clean run on each fixed input function. A distribution is \(\alpha_j\)-flat if its largest point probability is at most \(\alpha_j\). The core is \((q,\alpha,\beta)\)-unpredictable when the probability of a nonflat prefix at query \(j\) is at most \(\beta_j\), with

\[
\sum_j\alpha_j\le\alpha,\qquad \sum_j\beta_j\le\beta.
\]

This conditional dispersion is an actionable resource: a manipulated set with at most \(T\) elements attracts at most \(\alpha T+\beta\) probability over one core execution.

### Conditional amplification in the final edition

Run \(r\) iterations with fresh independent private randomness. The total manipulation allowance is at most \(qrt\). Final Lemma 4.3 establishes, for any event \(E_i\) determined by the first \(i-1\) iterations,

\[
\Pr[\text{iteration }i\text{ hits a manipulated entry}\mid E_i]
\le \eta(r),\qquad \eta(r)=\alpha qrt+\beta.
\]

A precise way to use the clean-input definition is a **first-hit coupling**. Fix a past history, run the actual and clean cores with the same fresh coins, and compare them until the first queried manipulated entry. Before that event the answers and subsequent choices agree. Apply flatness and the bad-prefix bounds to this clean reference path. One need not assert that queries remain clean-distributed after a corrupted answer.

Suppose the clean core has perfect completeness and rejects every far function with probability at least \(p\). Final Lemma 4.4 takes

\[
r=\lceil3/p\rceil,
\qquad
\alpha qtr+\beta\le p/12.
\]

Completeness error is at most \(r\eta(r)\le1/3\). Conditional on all prior failures, the next iteration fails with probability at most \(1-p+\eta(r)\). The chain rule gives

\[
\Pr[\text{all iterations fail}]
\le(1-p+\eta(r))^r
\le e^{-11/4}<1/3.
\]

The final proof explicitly conditions on previous failures. Independent private coins alone would not make the failure events independent, because a budget-managing adversary connects the iterations. This is a material improvement over the v1 presentation.

**Independent reusable consequence.** The same argument, with arbitrary \(r\), gives

\[
\text{completeness error}\le r(\alpha qrt+\beta),
\qquad
\text{soundness error}\le e^{-r[p-(\alpha qrt+\beta)]}
\]

whenever \(\alpha qrt+\beta<p\). Repetition increases both statistical power and the adversary's accumulated budget. For \(r=\lceil3/p\rceil\), the simple sufficient choices \(\beta\le p/24\) and \(\alpha qt\le p^2/96\) recover the final lemma. This is an algebraic restatement of its interface, not a new resilience theorem for arbitrary dependent sampling.

## 4. A queried reservoir creates many privately selectable relations

Final Algorithm 3 chooses

\[
m=4\left\lceil\log_2t+15/\varepsilon\right\rceil+12.
\]

It queries \(m\) independent uniform elements \(X=(x_1,\ldots,x_m)\). It then privately selects signs and a uniform subset \(S\subseteq[m]\) of size \(m/2\), and queries

\[
y=\prod_{j\in S}^{\text{increasing order}}x_j^{\sigma_j}.
\]

The cached labels give the corresponding right-hand product. Reject precisely on disagreement, if no required answer was erased. The resulting core has the same clean soundness as a random signed word of length \(m/2\), hence \(p=1/16\) suffices.

Assume first \(2^m\le|G|^{1/4}\). Fix the signs and two distinct subsets. An index in their symmetric difference occurs in exactly one product. Conditioning on the other group elements leaves an equation \(A x_i^{\pm1}B=c\), which has a unique solution and therefore probability \(1/|G|\). A union bound over subset pairs and all sign vectors gives

\[
\Pr_X[\text{some signed subset map is not injective}]
\le\frac{2^{3m}}{|G|}\le2^{-m}.
\]

On a good reservoir, even after all \(x_i\) are public, the private subset gives

\[
\max_y\Pr[y\mid X]\le\binom m{m/2}^{-1}.
\]

Mixing over private signs preserves this upper bound. The first \(m\) queries are uniform, so the direct parameters are

\[
q=m+1,\quad
\alpha=\frac m{|G|}+\binom m{m/2}^{-1},\quad
\beta=2^{-m}.
\]

Final Lemma 5.1 uses the looser \(m/2^m\) in place of \(m/|G|\). The supplementary proof checks the constants with \(r=48\). The exponential number of possible subwords is a **distributional support size**, not an enumeration performed by the algorithm. One iteration uses \(m+1\) oracle queries, \(O(m)\) group operations and \(O(m)\) cached group elements and labels, plus private random bits.

When \(2^m>|G|^{1/4}\), the paper switches constructions. It invokes the sample-based Goldreich–Ron tester using \(O(\varepsilon^{-1}+\log|G|)\) queries and the quoted sample-to-resilience lemma. In this branch \(\log|G|=O(m)\), so the desired \(O(\varepsilon^{-1}+\log t)\) query order still follows. The injective-reservoir proof alone does not cover every group size. Both branches and their supplementary parameter checks were read.

## 5. Group-specific construction and prime-field refinement

### Sampling until the group is determined

V1 Section 6.1 gives the full proof of the final group-specific statement. Its Generated Subgroup Test samples about \(E(G)+9\) elements. If they do not generate \(G\), it accepts without claiming consistency. If they do, it rejects labels that have no homomorphic extension, otherwise obtains the unique extension \(h\) and compares it with \(\lceil3/\varepsilon\rceil\) fresh uniform labels.

The source obtains the sharp additive generation budget through historical group parameters. If \(m_r(G)\) counts maximal subgroups of index \(r\), write

\[
\mathcal M(G)=\sup_{r\ge2}\frac{\log m_r(G)}{\log r}.
\]

Quoted results give \(d^\beta(G)\le\mathcal M(G)+w\) when \(\zeta(w)\le1+\beta\), and \(\lceil\mathcal M(G)\rceil\le E(G)+4\). The dyadic estimate in Appendix A yields

\[
d^\beta(G)\le E(G)+5+\log_2(1+1/\beta).
\]

For \(\beta=1/12\), \(\lceil E(G)+9\rceil\) samples suffice. Generation failure costs at most \(1/12\), and the independent validation misses an \(\varepsilon\)-far function with probability at most \(e^{-3}<1/12\). The quoted uniform-sampling resilience theorem then supplies the stated modification regime. The source optimizes query order, leaving the extension step as a mathematical operation. Section 7 supplies a direct finite realization of it.

### More private coefficient choices over a prime field

For \(G=\mathbb F_p^n,H=\mathbb F_p^r\), replace signs by uniformly random nonzero coefficients from \(\mathbb F_p^*\). Negation and reverse cancellation remain available, so the self-correction argument continues to work. Set

\[
m=4\left\lceil\log_pt+15/\varepsilon\right\rceil+12.
\]

In the branch \(m\le n/4\), the sampled vectors are linearly independent except with probability at most \(2/p^{n/2}\le2/p^m\). On that event, a fixed support of size \(m/2\), together with its nonzero coefficients, identifies its sum uniquely. The private final query therefore has support of size

\[
\binom m{m/2}(p-1)^{m/2}.
\]

Its point probability is bounded by the inverse of this quantity. Together with the first \(m\) uniform queries, one may take

\[
\alpha=\frac m{p^n}+
 \frac1{\binom m{m/2}(p-1)^{m/2}},
\qquad \beta=2/p^m.
\]

The support for a fixed subset is the injective image of a nonzero-coordinate cube. It need not be an affine subspace. Injectivity and cardinality are the properties used by the proof. In the other branch, the quoted \(E(\mathbb F_p^n)\le n+3\) generation bound gives the sample-based alternative. The larger private coefficient alphabet explains the base-\(p\) logarithm.

### Bounded completion of the supplementary lower-bound interface

The source lower bound erases the span of past queries and compares a random linear function to a random function. Its v1 transcript description leaves two elementary interfaces implicit: a first query at zero and repeated queries. The following small completion preserves the intended proof and asymptotic result.

Let \(N=p^n\) and \(a=(p-1)/p\). Choose the negative distribution with \(f(0)=0\) and independent uniform values elsewhere. After each answer erase the entire current span, including previously queried points. For \(q\le\lfloor\log_pt\rfloor\), each span has at most \(p^q\le t\) elements, so this is a legal fixed-rate erasure strategy. Previously erased entries need not be charged again.

A first zero query now returns zero in both experiments. Later queries in the accumulated span return \(\perp\). A new query outside the span has a uniform label under both a random linear function and the modified random negative function. Thus their complete adaptive transcript distributions agree, including repetitions.

For any linear \(h\), its number of mismatches with the negative function is \(\operatorname{Bin}(N-1,a)\). Hoeffding and a union bound over the \(N\) linear functionals give

\[
\Pr[\operatorname{dist}(f,\operatorname{HOM})\le a/2]
\le N\exp\left[-\frac{a^2(N-2)^2}{2(N-1)}\right],
\]

which is at most \(1/7\) for sufficiently large \(n\). The negative mass needed by the source's minimax argument remains available. This is a local proof completion in the scoped v1 dependency, not a claimed failure of the theorem or an expanded lower-bound audit.

## 6. Independent static local decoder from the source corrector

The all-points vote bound supplies a concrete recovery operation. Assume the signed length-\(L=2k\) test has rejection probability \(\mu<1/10\). The source then defines a homomorphism \(g\) with each constrained vote correct with probability at least \(1-2\mu>4/5\).

To obtain one uniform vote in \(\operatorname{FIX}(a)\), sample all signs and the first \(L-1\) elements uniformly. If \(P=\prod_{i<L}x_i^{\sigma_i}\), set

\[
x_L=(P^{-1}a)^{\sigma_L}.
\]

This is the unique completion for those prefix choices and signs, so the distribution is exactly the required conditional one. Query the \(L\) labels and form the vote. With \(R\) independent votes, output their most frequent value. Since more than half correct votes force the correct output, Hoeffding gives

\[
\Pr[\widehat g(a)\ne g(a)]\le e^{-9R/50}.
\]

Thus \(R=\lceil(50/9)\ln(1/\delta)\rceil\) suffices with \(LR\) label queries. This is a **static-oracle deduction**. Its constrained last query is predictable from the prefix, so online manipulation resilience does not follow automatically. It is also conditional on the test's small rejection rate, not an unconditional procedure for learning an arbitrary function.

## 7. Independent finite compiler and elementary sample-based tester

The following deduction exposes the computational interface of “the unique extending homomorphism.” It is elementary and no novelty is asserted. It uses known finite groups, exact group operations and a known order \(|G|\).

### Cayley-graph extension compiler

Given sampled generators \(S\) and labels \(a_s\in H\), traverse the directed right-Cayley graph. Start with \(h(e_G)=e_H\). For each visited \(x\), each \(s\in S\) and \(\sigma\in\{+1,-1\}\), inspect

\[
y=xs^\sigma,\qquad b=h(x)a_s^\sigma.
\]

On first reaching \(y\), assign \(h(y)=b\). On a later visit require equality with its existing label. Continue until every reachable edge is checked. Duplicate observations of the same generator with conflicting labels are inconsistencies, not entries to overwrite. Precompute generator and label inverses.

If \(S\) generates \(G\), consistency is equivalent to the existence of its unique homomorphic extension. Indeed, for a generator word \(y=s_1^{\sigma_1}\cdots s_r^{\sigma_r}\), the checked right edges imply

\[
h(xy)=h(x)a_{s_1}^{\sigma_1}\cdots a_{s_r}^{\sigma_r}
     =h(x)h(y).
\]

The second equality follows by starting the same word at \(e_G\). Every homomorphism extending the labels is forced to take these values. Conversely, an actual extension makes every edge check consistent. The argument preserves noncommutative order.

If the traversal reaches fewer than \(|G|\) elements, it has compiled only the subgroup \(\langle S\rangle\). It does not establish a global extension. The tester below accepts in this branch, as does the source.

There are at most \(2|G||S|\) edges. With exact constant-cost group operations, equality and dictionary access, this uses \(O(|G||S|)\) local operations and \(O(|G|)\) group-element/label records, with **no extra queries to \(f\)**. Representation, hashing or comparison costs must be added when these operations are not unit cost. A full indexed table can require \(O(|G|(\log|G|+\log|H|))\) bits. This is not a small-state or logarithmic-time compilation result.

### A self-contained, slightly less sharp generation budget

Suppose a known bound \(\overline E\ge E(G)\) is available. Use

\[
m=\lceil12\overline E\rceil,
\qquad \ell=\lceil3/\varepsilon\rceil,
\qquad Q=m+\ell.
\]

Draw \(Q\) independent uniform query locations with private randomness. Use the first \(m\) to compile the candidate and the remaining \(\ell\) for validation. These may be regarded as a fixed batch of potential queries even if the execution stops early. Accept on a generation failure or an observed erasure. Otherwise reject an inconsistent extension or any validation mismatch.

If \(T_{\rm gen}\) is the number of independent samples needed to generate \(G\), Markov gives

\[
\Pr[\langle S\rangle\ne G]
 =\Pr[T_{\rm gen}>m]
 \le E(G)/m\le1/12.
\]

On a clean input far from every homomorphism, a consistent compiled \(h\) disagrees with \(f\) on at least an \(\varepsilon\) fraction. Conditional on the first batch, the independent validation passes with probability at most \(e^{-3}\). The clean error is therefore at most \(1/12+e^{-3}<1/6\), with perfect completeness.

Before query \(j\), at most \(t(j-1)\) locations have been manipulated. A fresh independent uniform query hits them with probability at most \(t(j-1)/|G|\). Couple to the clean reference run until the first hit and sum:

\[
B:=\Pr[\text{some queried location was manipulated}]
\le\frac{tQ(Q-1)}{2|G|}.
\]

Do not condition all the clean concentration arguments on “no hit”: that event itself can select query trajectories. The coupling instead adds the hit bound to an independently established clean-run error. Thus

\[
\Pr[\text{false acceptance}]\le1/12+e^{-3}+B,
\qquad
\Pr[\text{false rejection of a homomorphism}]\le B.
\]

For example, \(t\le |G|/[3Q(Q-1)]\) ensures \(B\le1/6\), giving the required \(2/3\) success. Erasures preserve exact one-sided completeness. The query order is \(O(\overline E+\varepsilon^{-1})\), while the compiler's \(O(|G|m)\) local work and full-table storage remain visible. Local computation alone does not grant the adversary more modifications in the paper's per-query model.

This construction trades the source's additive \(E(G)+9\) generation bound for \(12\overline E\), avoiding its historical generation-theorem dependency for this weaker constant-factor variant. It does not discover the group operation, remove the need for uniform sampling, or solve tolerant learning from a near-homomorphism.

## 8. Reusable mathematical content and limits

Three constructive tools are supported by the read sources and the explicitly labeled deductions.

- **Preserve a useful relation while hiding its final location.** A queried reservoir stores reusable labels. Private subsets and inverse-closed coefficients create many possible relation checks, and a collision argument prices their conditional uncertainty.
- **Compile consistency into a concrete candidate.** A generating set determines a unique algebraic map when all right-Cayley edges agree. Fresh independent labels provide a validation test. Query efficiency can coexist with a large local compilation table, so both resources must be stated.
- **Separate a corrector from a resilient tester.** The signed-word corrector yields all-points agreement and a static decoder. The online guarantee additionally needs conditional query dispersion and an amplification budget that grows with the adversary.

No FP architecture or core definition is changed. Known group structure, uniform resets over a finite domain, exact labels and an oracle whose modifications are charged per query are substantial premises. The paper does not establish that predictive experience forms a group operation or learns a reusable program, nor does it supply a finite-bit recurrent-state theorem. Its algebraic correction, relation sampling and extension-validation interfaces are available as conditional mathematical instruments without asserting those missing mappings.

The official final is complete. The v1 supplement remains scoped, historical dependency papers retain their independent reading states, and the two versions' material changes are preserved. There is no routine re-audit or implementation task queued from this note.
