# Wieczyński 2026 — Identifiability of finite-state ε-machines from finite summaries

## Edition and actual coverage

- **Author:** Paweł Wieczyński.
- **Edition:** arXiv:2609.06735v1, submitted September 6, 2026, 17:14:37 UTC. The November 26 primary version-history check listed only v1. Peer-reviewed publication was not authenticated.
- **Primary sources:** [versioned record](https://arxiv.org/abs/2609.06735v1), [19-page PDF](https://arxiv.org/pdf/2609.06735v1), [complete TeX](https://arxiv.org/src/2609.06735v1).
- **Local source:** literature/corpus/arxiv/2609.06735v1/, including paper.pdf, source/main.tex and source/references.bib. The PDF SHA-256 is 0c096fddc6f36df921ef244c07fc6300a2d6cf77d62e5c1972f338837ad9e6b5.
- **Fully read, November 26, 2026, Shanghai:** main reader covered all 882 lines of main.tex, all seven sections and proofs, title/author footnote, declarations, complete 41-entry source bibliography and all 28 printed references. There is no appendix. The sole figure has four panels; its actual PDF p. 7 and the unnumbered probability table on p. 11 were inspected. Dense definitions and proofs were checked in original PDF pp. 8, 11–12 and 14–16.
- **Verification level:** bounded independent reasoning checks of the conditional-table equivalence, common-synchronization proof, context-rank calculation and finite-horizon comparison. A second reader checked Lemma 5.1/Theorem 5.2. No whole-paper certification, formal proof, numerical reproduction or recursive audit of cited works is claimed.
- **AI disclosure:** the author reports using OpenAI GPT-5.6 Sol through Codex for editing, organization, notation and scrutiny, and accepts responsibility. This is an outside author's preprint, not an official OpenAI publication.

## 1. Original question and result

The paper asks which finite observable summaries determine a stationary finite-state ε-machine up to isomorphism. It distinguishes three statements: equality of full process laws, the uniqueness of canonical generators for a given law, and identification from a prescribed finite summary. The last statement needs a class restriction or a pair-dependent horizon.

Its principal result is a structural sufficient horizon for two **exactly synchronizing** generators. If their target synchronization radii are a and b, and the larger predictive separation radius is d, agreement of block probabilities through length

\[
n\ge a+b+d+1
\]

forces generator isomorphism. Theorem 5.2 gives two corresponding allocations of past and future lengths in a labeled conditional-probability table. The proof aligns states using histories that synchronize both models, then checks one-step successors.

This is an identifiability theorem. The author explicitly says it does not furnish an algorithm recognizing which rows of an arbitrary numerical table are synchronizing rows. The paper also supplies the classical linear-realization bound, a table/block-law equivalence, examples distinguishing synchronization notions, and a family comparing sufficient horizons.

## 2. Objects, assumptions and canonicality

Definition 2.1 uses a finite edge-emitting unifilar generator. A state σ emits x with probability eσ(x), then moves to δ(σ,x); the successor is defined on admissible state-symbol pairs. The positive-probability transition graph is strongly connected. Distinct states have different probabilities for at least one finite future word. The initial state distribution is the unique stationary distribution.

Zero emission probabilities are allowed. Strong connectivity is required, but aperiodicity is not. The stationary labeled-edge chain gives an ergodic output process; the state sequence alone would not retain all emission randomness.

For a word w, the state morph pσ(w) is its probability starting from σ. Symbol matrices T(x) give pσ(w) as the appropriate coordinate of T(w)1. Isomorphism preserves emission probabilities and admissible labeled successors; stationarity then matches the initial distributions.

The canonicality input is Travers–Crutchfield's history/generator equivalence, cited as the 2025 Symmetry edition. Canonical minimality is within the relevant unifilar predictive class. It does not assert that this generator has the fewest states among arbitrary nonunifilar HMMs, nor that its physical state count equals the Hankel rank.

## 3. Three different synchronization quantities

Definitions 3.1 and 3.3, Lemma 3.2 and Proposition 3.4 distinguish:

| Quantity | Meaning | Important boundary |
|---|---|---|
| Exact synchronization | Some finite positive-probability observation word leaves a point-mass posterior on the current state. | A finite generator can fail this property while synchronizing asymptotically. |
| Target radius Ltar | Maximum, over target states, of the shortest word synchronizing to that state. | Each state may have its own word. This does not say every sufficiently long history synchronizes. |
| Separation radius Lsep | Maximum, over state pairs, of the shortest future word distinguishing their probabilities. | It separates actual states, not every vector in the linear span of states. |
| Synchronization order Lsyn | Shortest length at which every positive-probability word synchronizes. | It can be infinite even when Ltar is finite. |

The one-state conventions give Ltar=Lsep=0. A synchronizing suffix remains synchronizing after any admissible prefix; a known synchronized state remains known after an admissible continuation. Exactness plus strong connectivity makes every state reachable by a synchronizing word.

For a generator with k states, the column spaces spanned by T(w)1 stabilize after at most k−1 steps, giving Lsep≤k−1. If Ltar≤A on a q-letter alphabet, assigning distinct target words gives k≤Σℓ=0…A qℓ. Thus bounded target radius already restricts state count, although its structural horizon can be much shorter than the resulting state-count bound.

### Figure 1: four examples, checked against the actual diagram

| Process | Ltar | Lsep | Lsyn | Mechanism |
|---|---:|---:|---:|---|
| Even Process | 2 | 1 | ∞ | A reset exists, but arbitrarily long runs of 1 remain ambiguous. |
| Alternating Biased Coin Process, distinct p,q in (0,1) | ∞ | 1 | ∞ | Every letter flips phase and all letters remain admissible from both states; no finite word eliminates the other phase. |
| Ternary Reset Process | 1 | 1 | 1 | Symbols 0,1,2 reset to A,B,C; diagonal emission 1/2 and off-diagonal emissions 1/4. |
| Delayed Separation Reset Process | 1 | 2 | ∞ | A and B share the one-letter distribution, but differ after a star followed by 0; star-only histories do not synchronize. |

The delayed example's A/B rows assign 1/8 to each reset symbol and 5/8 to star. C assigns 1/4 to each symbol. Star sends A to A, B to C and C to C. These labels explain why one-step row distinctions and synchronization are separate requirements.

## 4. What the finite summary retains

Definition 4.1 separates uniform identification, with quantifiers ∃h∀P,Q, from pairwise finite distinguishability, with ∀P,Q∃h(P,Q).

For L,R≥1, C(L,R) contains P(v|u) for every **labeled** positive-probability history u of lengths 1 through L and every future word v of length at most R, including the empty future. Equality includes the positive-history domain and all word labels. It is not equality of a row cloud, row multiset or convex hull.

Proposition 4.2 proves, for stationary ergodic finite-alphabet processes,

\[
C_{L,R}(P)=C_{L,R}(Q)\quad\Longleftrightarrow\quad
P_{L+R}=Q_{L+R}.
\]

The block-to-table direction uses stationarity and marginalization. For the reverse direction, the length-one rows determine the common observed one-step matrix K(x,y). Ergodicity makes its support graph irreducible: a proper closed class with positive stationary mass would also have no incoming flow, producing a nontrivial shift-invariant event. Its unique stationary distribution supplies the one-symbol marginal. The labeled conditional entries then recover history probabilities by the chain rule, followed by P(uv)=P(u)P(v|u).

This argument does **not** assume the observed process itself is first-order Markov. K is only used to recover its one-symbol stationary marginal; longer conditionals come from the supplied table. An independent check confirmed that distinction and the closed-class argument.

Ergodicity is necessary for this reverse implication. Mixtures of the two constant sequences have identical conditional tables for every nontrivial mixture weight but different marginal weights. Stationarity and history labels are also substantive assumptions.

Corollary 4.4 says that fixed-R labeled tables at arbitrarily long past horizons determine the complete process law. This is an infinite-information completeness statement, not a fixed finite identification theorem.

## 5. Classical linear realization remains a separate ingredient

Proposition 4.5 states that two HMM presentations with r and s states agreeing on all words of length at most r+s−1 agree on every word. Its block-diagonal difference representation has dimension r+s; the reachable row span starts in dimension one and stabilizes by that horizon. Every reachable row then annihilates the terminal column.

The proof is algebraic. It does not need stationarity, irreducibility, nonnegative coordinates or synchronization once the linear representations are supplied. Corollary 4.6 adds canonical generator uniqueness after equality of stationary laws. Corollary 4.7 gives uniform identification on generators with at most N states from P(2N−1).

Crucially, the paragraph following Corollary 4.6 already replaces r,s by smaller unrestricted linear realization dimensions r′,s′. Finite-window law identifiability based on linear rank is therefore an acknowledged classical ingredient here. Positive realizability and canonical physical-state extraction are additional questions.

Example 4.8 recovers the ternary reset parameters from C(1,1) **given the reset structure in advance**. Without that structure, the table itself does not certify that its labeled histories reset to individual states.

## 6. Main structural proof and its exact scope

Throughout §5, both generators are exact, finite, strongly connected, unifilar and probabilistically distinct. Put a=Ltar(P), b=Ltar(Q), and d=max(Lsep(P),Lsep(Q)).

**Lemma 5.1.** Suppose the two supports agree through length a+b. For a target state σ of P, choose a P-synchronizing word u of length at most a. Because Q admits u, choose a Q-state τ from which u is admissible. Prepend a word z of length at most b synchronizing Q to τ. Then zu has positive Q-probability, hence positive P-probability by support equality. Its suffix u synchronizes P to σ; Q remains pure after its synchronizing prefix z and unifilar continuation u. The construction also works with P and Q interchanged.

**Theorem 5.2.** Equality of the labeled tables implies isomorphism under either condition:

\[
\begin{array}{lll}
\text{A:}&L\ge a+b+1,&R\ge\max(1,d),\\
\text{B:}&L\ge a+b,&R\ge d+1.
\end{array}
\]

In both cases, common synchronizing histories provide pure-state rows in both models. The symmetric construction gives equality of the two sets of R-truncated state morphs. Separation at horizon d makes this a bijection and identifies emissions.

- Under A, append a symbol to a common synchronizing history. The resulting row is still in the table and identifies the successor pair.
- Under B, normalize the matched probability pσ(xv) by the common positive emission probability. This identifies successor morphs through R−1≥d without requiring a longer history row.

The corresponding state transition matrices agree up to permutation, so their unique stationary distributions match. The all-one-state case is handled separately; L,R remain at least one. No argument assumes that all long histories are pure. The required pure histories are constructed within the proof using **both** generators.

Corollary 5.3 gives the block horizon a+b+d+1. Corollary 5.4 restricts the class by Ltar≤A and Lsep≤D and obtains a single horizon 2A+D+1, along with the two table allocations.

**Independent check:** the support-transfer and successor arguments close under their printed assumptions, including the one-state boundary. No unstated finite Markov-order condition was found. This check does not turn the existence proof into a data-driven algorithm for detecting synchronizing rows. The author explicitly preserves that distinction.

## 7. Binary context family: full rank and narrower comparison

Section 6 fixes the de Bruijn update on length-m binary contexts. Every context u has p_u∈(0,1) for emitting 1. When all 2^m values are pairwise distinct, Proposition 6.1 gives:

\[
k=2^m,\qquad L_{\rm tar}=L_{\rm syn}=m,\qquad
L_{\rm sep}=1,\qquad \operatorname{rank}H=2^m.
\]

The Markov order is also exactly m. All m-letter words reset the context, and no shorter word can eliminate every initial suffix. Distinct one-symbol probabilities separate states.

The rank proof is concrete. Independently permuting rows and columns of the transition matrix T_m gives 2×2 blocks indexed by z of length m−1, each with determinant p(1z)−p(0z). Thus T_m is invertible. The Hankel block indexed by all m-letter words satisfies

\[
H^{(m,m)}=\operatorname{diag}(P_m(u))\,T_m^m.
\]

All diagonal probabilities are positive, so this block is invertible. The k-state presentation supplies the matching rank upper bound. The determinant only needs p(0z)≠p(1z); the stronger pairwise-distinct assumption supplies one-step state separation. The block factorization and its probability interpretation were independently checked.

Proposition 6.2 chooses p(0z)=θ_z and p(1z)=1−θ_z, with distinct θ_z in (0,1/2). The transition matrix is doubly stochastic, so every m-block has probability 2^−m. Two choices θ_z=(j(z)+1)/(4M) and θ′_z=(j(z)+1)/(6M), M=2^(m−1), agree through length m but disagree at m+1. This establishes a lower obstruction at m, not optimality of the general structural bound.

| Bound or construction on this family | Required horizon | Scope |
|---|---:|---|
| General state-count / rank-dimension formula | 2^(m+1)−1 | Sufficient bound using only dimensions. |
| General structural synchronization formula | 2m+2 | Uses target/separation radii of the two models. |
| Adapted weighted-automata W-method | 2m+1 | The known family supplies a state cover and characterization set for both competitors. |
| Fixed Hankel-basis linear realization | 2m+1 | Uses the invertible length-m basis block; identification of the full law also needs the competitor's global rank upper bound. |
| Known order-m context structure | m+1 | Updates already supplied; conditional ratios recover emissions. Sharp for this known-structure family. |

For m≥2, the structural formula is smaller than the general dimension-only formula by Θ(2^m/m). The paper repeatedly limits this to a comparison of sufficient formulas. It is not an exponential lower bound for all reconstruction algorithms.

The adapted realization uses

\[
A_x=H^{(x)}_{U,V}H_{U,V}^{-1},\quad
\alpha=(P(v))_{v\in V}H_{U,V}^{-1},\quad
\beta=(P(u))_{u\in U}^{\mathsf T},
\]

with U=V={0,1}^m. Factoring H=FG shows A_x=FM_xF^−1 and αA_wβ=P(w). This fixes the multiplication order and the boundary vectors. A finite nonzero Hankel minor certifies a lower bound only; it does not establish the required global rank upper bound.

This example has **physical state count equal to linear rank**. It is not an example of extracting more intrinsic states than the linear dimension.

## 8. Evidence, dependencies and unresolved questions

This is a mathematical paper with illustrative finite examples, not an empirical study. It contains no learned-model benchmark, sampling experiment, timing comparison, implementation or finite-precision stability guarantee. The data statement reports no generated or used data.

Principal citation roles are:

- Travers–Crutchfield 2025: finite history/generator equivalence and uniqueness.
- Travers–Crutchfield 2011 exact/asymptotic synchronization: the distinction between finite pure histories and limiting synchronization.
- Paz and Tzeng: finite linear equivalence witnesses and reachable-space stabilization.
- Carlyle–Paz, Jaeger, Huang–Ge–Kakade–Dahleh: linear realization and rank-based representations.
- Vidyasagar: positive realization is an additional constraint beyond finite rank.
- Chow and Kocsis–Rot: reach, successor and characterization-set conformance arguments. The adapted W-method application depends on full linear-space characterization, not merely pairwise physical-state separation.
- Jonoska, Cai–Frongillo, and Bradshaw–Clow–Stacho: target synchronization and common synchronization in automata. The author identifies the concatenation idea as an existing support-level principle, while locating the claimed contribution in the stationary probabilistic combination and bound.

Reading these uses is not full reading or independent verification of the cited sources. In particular, this note does not certify the external W-method theorem or its most general categorical form.

The discussion leaves open useful structural bounds or recognizable population constructions beyond exact synchronization, stability moduli under perturbed tables, finite-sample estimation guarantees, and extensions to infinite predictive-state spaces. Relevant stability quantities include the probabilities of synchronization words, separation of truncated state morphs and stationary-distribution sensitivity.

## 9. Narrow position for Astra request 3f8e6cb

The requested source interface has a known global rank n, positive state-letter probabilities, strong connectivity, distinct state future laws and unknown finite physical state count k, possibly k>n. It seeks a terminating construction of all intrinsic state rows from the minimal linear operators.

This paper is direct prior art for finite-summary identifiability and explicitly acknowledges dimension-based finite law identification. Its structural theorem additionally requires finite exact synchronization; that condition is absent from the requested general class. Its known-reset and known-context constructions rely on supplied transition structure, and its main proof does not algorithmically recognize pure history rows.

Accordingly, the complete paper does **not supply the requested least-image-subspace / positive-weighted-permutation extraction algorithm**. This source-specific distinction is supported by the full reading. It is not a novelty claim for Astra's construction, a proof that no other algorithm exists, or an audit of FP core theory. The broader prior-art request is handled separately.
