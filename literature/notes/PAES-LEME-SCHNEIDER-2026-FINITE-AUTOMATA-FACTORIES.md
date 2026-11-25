# A rational dice factory that requires more than finite-state control

## Source and actual reading

Renato Paes Leme and Jon Schneider, *Note on Finite-Automata Bernoulli Factories for Rational Functions*, arXiv2606.29595v1. Both authors list Google Research. The arXiv submission is June28,2026,20:36:06UTC. The four-page PDF prints June30,2026 because its TeX uses the compilation date. Only v1 was listed when checked. No reviewed venue was authenticated.

- [Version record](https://arxiv.org/abs/2606.29595v1)
- [Original PDF](https://arxiv.org/pdf/2606.29595v1)
- [Complete source](https://arxiv.org/src/2606.29595v1)

The main reader completed all four original PDF pages and active TeX, §§1–3, every formula and proof, the tool disclosure and all five references. There are no figures, tables, appendices or body footnotes. This completes the earlier checkpoint through the setup. The paper discloses use of Gemini3.1Pro DeepThink to derive the counterexample and refine its presentation. It is not an official OpenAI or Anthropic release.

The central counterexample was independently checked at the algebraic and model level. The positive-ratio necessity and the passage from equality on the simplex to a polynomial identity are made explicit below. A symbolic gcd/expansion check supplements the reasoning. There is no formal proof replay, experiment or certification of all cited literature.

## Problem and conclusion

An unknown three-face die has probabilities p=(p1,p2,p3) in the open simplex, with every coordinate positive and their sum one. A factory observes an unbounded iid stream of die outcomes and must stop almost surely with a binary output whose success probability is a specified function g(p). A finite-automaton factory must implement that procedure with a fixed finite state set and a time-homogeneous update. A general factory has no such memory restriction.

The paper gives a rational g for which a general factory exists but no finite automaton works over the whole open simplex. It thereby contradicts the multivariate extension in Mossel–Peres Theorem2.9. It does not contradict their univariate rational-function characterization. In more than one independent variable, numerator and denominator can vanish at a boundary point without sharing a polynomial factor. Positivity on the open simplex is therefore insufficient for the closed-simplex positivity premise of Pólya's theorem.

This is an exact simulation separation, with no bound on the general factory's expected running time. It is not an approximate-memory lower bound, a fixed query-budget result or a theorem about learning transitions.

## Counterexample and existence

Write

\[
P=p_1^3p_2,\qquad
Q=p_3^2(p_1-p_2)^2+p_1^3(p_1+p_2+p_3),\qquad g=P/Q.
\]

Both polynomials have degree four. On the open simplex, P and Q are positive, and

\[
Q-P=p_3^2(p_1-p_2)^2+p_1^4+p_1^3p_3>0.
\]

Thus g is continuous with values strictly between zero and one. The paper uses Q≤2 on the closed simplex to obtain g≥p1³p2/2 and 1−g≥p1⁴/2.

Here is an explicit translation into the cited existence condition. Set Π=p1p2p3. Since each coordinate is below one,

\[
\min(g,1-g)\ge\tfrac12\Pi^4>\Pi^5,
\qquad \Pi\le 1/27.
\]

Morina's Lemma3.15 therefore applies directly. Its model is an almost-surely finite die-to-coin procedure, with optional auxiliary uniform randomness that can itself be obtained from the die. The lemma imposes no finite-state restriction or uniform mean-cost bound. This use of the lemma is a scoped dependency import, not an independent reconstruction of the thesis's entire existence theorem.

## Why no nonnegative polynomial denominator can represent g

The only irreducible factors of P are p1 and p2. Neither divides Q, as its restrictions to p1=0 and p2=0 are nonzero polynomials. Hence gcd(P,Q)=1.

Suppose g=A/B for polynomials with nonnegative coefficients. For the polynomial-ring argument, first homogenize A and B to one common degree using S=p1+p2+p3. Replace each monomial cα p^α by cα p^α S^(d−|α|), where d is the larger degree. This preserves coefficient nonnegativity and values on S=1. Now AQ−BP is homogeneous. Its vanishing on the open simplex extends by positive scaling to the positive orthant, hence it vanishes as a polynomial. The UFD argument then gives B=QR with nonzero homogeneous R. Equality merely on S=1, without this bridge, would not by itself justify divisibility in the ambient polynomial ring.

Dehomogenize at p3=1. The resulting denominator factor is

\[
q(p_1,p_2)=(p_1-p_2)^2+p_1^3(p_1+p_2+1).
\]

Its lowest homogeneous part is q2=(p1−p2)². Homogeneity of nonzero R ensures that r=R(p1,p2,1) is nonzero. If r_k is its lowest nonzero homogeneous part, the lowest part of b=B(p1,p2,1) is

\[
b_{k+2}=(p_1-p_2)^2r_k.
\]

It is nonzero because the polynomial ring is an integral domain. On the other hand b has nonnegative coefficients, so b_(k+2) does too. Its value at (1,1) is zero. That value is the sum of its nonnegative coefficients, forcing it to be the zero polynomial. This is the contradiction.

The argument excludes every nonzero polynomial multiplier R. It is stronger than merely showing that multiplying Q by a power of S fails to repair its negative coefficient.

## Necessary finite-state representation, checked separately

The paper attributes an iff involving ratios of nonnegative homogeneous polynomials to Mossel–Peres. The retrieved primary statements require more care. Their Proposition2.5 characterizes fixed-block simulation using integer Bernstein coefficients satisfying 0≤d_i≤e_i. In particular the output-zero polynomial B−A is also coefficientwise nonnegative. Proposition2.8 states that an arbitrary finite automaton has rational output probabilities. Rationality alone does not yield the coefficient restriction needed by this counterexample.

The following independent necessity argument supplies exactly the missing link, without assuming the disputed multivariate sufficiency statement.

A finite automaton driven by iid die outcomes is a finite absorbing Markov chain. Its transition entries are nonnegative linear polynomials in p. The same argument allows fixed parameter-independent randomized transitions. Remove unreachable states and combine absorbing states with the same output. For every interior p, almost-sure absorption holds from every reachable state. The underlying reachable graph is independent of p because every die outcome has positive probability.

Eliminate a transient state i while keeping the initial state. The effective transition between remaining states is

\[
q'_{kj}=q_{kj}+
\frac{q_{ki}q_{ij}}{\sum_{\ell\ne i}q_{i\ell}},
\qquad k,j\ne i.
\]

The denominator is the probability of leaving i, written as a sum of nonnegative exits rather than as a subtraction. It is positive at every interior parameter because a reachable absorbing trap at i would violate almost-sure termination. The eliminated chain records the next visit to a remaining state and retains almost-sure absorption. Addition, multiplication and division of positive rational expressions preserve a representation by nonnegative polynomial numerators and denominators. Induction therefore preserves that property through all eliminations.

With only the initial state and outputs0,1 remaining, the probability of output1 is q_(start,1)/(q_(start,0)+q_(start,1)). It is consequently a ratio of polynomials with nonnegative coefficients. Termwise homogenization gives the common-degree pair used above. This proves the needed necessary condition for arbitrary finite-state factories, not just block factories. The counterexample therefore survives the attribution gap.

This derivation does not claim the full iff as worded in the2026note, and it does not equate finite automata and blocks through the theorem being refuted.

## Dependencies actually inspected

| Source and edition | Actual coverage | Use and limitation |
|---|---|---|
| Mossel–Peres, *New coins from old: computing with unknown bias*, arXivmath/0304143v1,19pages | Main reader inspected Definitions1.3–1.4 on p3, block definition and Theorem2.2 on p5, and pp6–9 including Proposition2.5, Lemma2.7, Proposition2.8, Theorem2.9 and Corollary2.10 | Finite-state stopping model, integer block representation, univariate homogenization and the disputed multivariate assertion. Remaining paper unread. The2005 journal edition's body was not retrieved or equated with this preprint. |
| Morina, *Extending the Bernoulli Factory to a dice enterprise*, Warwick thesis,January2021,145PDF pages | Main reader inspected Definition3.7, printed p57/PDF65, Lemma3.15 and proof start, p70/PDF78, and Theorem3.17 with its proof on p72/PDF80. Lemma3.15's original display was visually checked. Agent additionally inspected printed pp66–72 | Almost-sure stopping model and the sufficient product lower bound. Only these passages are read. The remaining thesis and the full chain of proof dependencies are not independently certified. |

Primary links: [Mossel–Peres preprint](https://arxiv.org/abs/math/0304143v1), [original PDF](https://arxiv.org/pdf/math/0304143v1), [journal identity](https://doi.org/10.1007/s00493-005-0043-1), [Morina institutional record](https://wrap.warwick.ac.uk/id/eprint/157145/), [thesis PDF](https://wrap.warwick.ac.uk/id/eprint/157145/1/WRAP_Theses_Morina_2021.pdf).

The Mossel–Peres arXiv record lists an April10,2003 submission, while the served PDF prints October24,2018. That typesetting date is not evidence of another listed arXiv version. Morina's repository labels its file a Submitted Version and an unpublished thesis. The2026note also cites Keane–O'Brien1994, Pólya1928 and Paes Leme–Schneider2023. Their roles and bibliographic entries were read, without claiming complete readings of those sources. A separate agent lookup found that the multiparameter preprint's Theorem5.2 assumes a compact parameter domain, so it is not used here as the direct open-simplex premise.

## Evidence, limits and follow-up

The original is a theoretical note with no experimental dataset, numerical benchmark or runtime analysis. The decisive obstruction is the degree-two tangent polynomial at one boundary vertex. The finite-state necessity, the common-degree bridge and the explicit Π^5 lower bound were independently checked, as were gcd(P,Q)=1 and the displayed expansions. The existence theorem remains an explicitly imported primary-source result. No automated formal certification is claimed.

No FP mapping is asserted. The paper separates exact simulation with unbounded control memory from fixed finite-state simulation of one prescribed rational function over an entire open parameter family. A learned noisy-coordinate process, finite-horizon approximation or physically charged clock would require additional objects and assumptions. Quantitative approximate-state costs and the general factory's expected cost remain unanswered here. Further historical full readings are optional unless those questions become active.
