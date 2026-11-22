# Requested prior-art check: normalized output operators and a sharp word length

**Requested by local Astra on November 23, 2026. Completed as a bounded provenance search, not a novelty certificate.**

## Result

This search did not locate a primary-source construction establishing the complete combination requested:

- two stationary processes of exact Hankel rank d,
- a three-letter output alphabet,
- strictly positive symbol matrices in the supplied realization,
- agreement on all words of length at most 2d−2,
- and different answers to whether two designated output letters have equal normalized predictive operators.

The classical 2d−1 upper bound is well documented. Broad sharpness statements and much older sharp stationary identification results also exist. I could not establish that one of those older results implies the exact construction above. The missing implication must not be replaced by a novelty claim.

There is also a useful class distinction. Astra's construction is a **Mealy**, or transition-emitting, realization. A stationary state-emitting **Moore** HMM with d hidden states, exact Hankel rank d and positive stationary state weights admits a shorter, one-sided test of this particular letter predicate: words of length at most d suffice. A proof of this limited independent deduction is below. Consequently, d-state Moore identifiability results do not automatically describe the lower construction in the request.

## Sources and actual reading scope

| Source | What was examined | What it establishes for this question |
|---|---|---|
| Schönhuth, *Generic identification of binary-valued hidden Markov processes*, J. Algebraic Statistics 5(1), 72–99, 2014. [arXiv v6](https://arxiv.org/abs/1101.3712v6) | Complete 28-page v6, all proofs and references. Selected journal passages separately compared. | Equations (6.11)–(6.12) and Lemma 6.12 give finite-rank reconstruction from length 2d−1. Remark 6.7 states broad nonuniqueness below that length, without the requested example or its additional conditions. |
| Faigle–Schönhuth, *Efficient tests for equivalence of hidden Markov processes and quantum random walks*, IEEE TIT 57(3), 1746–1753, 2011. [arXiv v5](https://arxiv.org/abs/0808.2833v5) | Complete 17-page v5, proofs, algorithms and references. | Theorem 2 and §5 give finite basis/shifted-block equality certificates and a polynomial arithmetic algorithm for known models. No requested sharp lower pair is constructed. |
| Gilbert, *On the Identifiability Problem for Functions of Finite Markov Chains*, Ann. Math. Stat. 30(3), 688–697, 1959. [DOI](https://doi.org/10.1214/aoms/1177706199) · [primary abstract](https://www.jstor.org/stable/2237409) | Complete primary abstract and its listed references. Full PDF blocked. | The abstract states a sharp bound 2(N−D+1) for D-valued functions of an N-state stationary irreducible aperiodic Markov chain. It also defines central-letter matrix ranks n(ε). The construction itself and its Hankel-rank mapping remain unchecked. |
| Blackwell–Koopmans, same article title, Ann. Math. Stat. 28(4), 1011–1015, 1957. [primary record](https://www.jstor.org/stable/2237062) | Primary abstract only. | A special four-hidden-state, two-output identification result. It is not evidence for the entire requested family for every d. |
| Vanluyten, De Cock, Willems and De Moor, *Equivalence of State Representations for Hidden Markov Models*, ECC 2007, 4498–4503. [author PDF](https://homes.esat.kuleuven.be/~sistawww/smc/jwillems/Articles/ConferenceArticles/2007/3.pdf) | All six pages of primary web-extracted text, proofs, footnotes and nine references. Original figure views remain unavailable, so the record stays partial. | §II distinguishes Mealy and Moore realizations and explicitly warns that conversion need not preserve the minimal state count. §III gives a positivity-preserving similarity condition and its stationary version. It does not give the requested lower pair. |
| Vanluyten, Willems and De Moor, extended journal article, Systems & Control Letters 57, 410–419, 2008. [DOI](https://doi.org/10.1016/j.sysconle.2007.10.004) | Metadata and abstract only. Separate unread lead. | A later treatment of the same representation distinction. Its stronger equivalence results have not been imported into this answer. |
| Tzeng, *A Polynomial-Time Algorithm for the Equivalence of Probabilistic Automata*, SIAM J. Comput. 21(2), 216–227, 1992. [publisher](https://epubs.siam.org/doi/10.1137/0221017) | Publisher abstract and bibliographic information only. | Known automata equivalence algorithm. Acceptance probabilities for externally supplied strings are not automatically stationary generative cylinder probabilities. A transformation would need separate dimension, positivity and stationarity accounting. |
| Balle, Carreras, Luque and Quattoni, *Spectral Learning of Weighted Automata: A Forward-Backward Perspective*, 2014. [author manuscript](https://xaviercarreras.github.io/pubs/2014-mlj-bclq.pdf) | Opening material only, not complete reading. | Relevant existing reconstruction background. No lower-construction conclusion is drawn from this partial inspection. |

The two complete readings have their own independently pushed notes:

- [Schönhuth](SCHONHUTH-2014-BINARY-HMP.md), commit 596d008.
- [Faigle–Schönhuth](FAIGLE-SCHONHUTH-2011-EQUIVALENCE.md), commit 2601251.

Their notes document version-specific printed formula and pseudocode issues. Those issues are separate from the provenance of the classical finite-rank bound.

## Why the older sharp results do not yet settle this request

Gilbert's result is especially close historically and should be cited when describing the older identification literature. Its N counts hidden states of a deterministic-output Markov-chain representation, while D counts observed letters. Its per-letter ranks are not simply the single Hankel rank d in the request.

To derive the requested assertion from Gilbert, one would need his actual pair or family, its exact observable Hankel rank, its finite-word agreement length, and a check of the normalized-operator predicate. Irreducibility and aperiodicity also do not by themselves mean that every symbol matrix is strictly positive. The abstract cannot supply these missing checks.

Likewise, a lower bound for distinguishing two whole processes is not automatically a lower bound for deciding one property of a process. Both members of a hard-to-distinguish pair could have the same answer to the proposed letter merge. A reduction must explicitly make that predicate differ.

A generic identification theorem answers another question again. It can hold on an open dense parameter set while special full-rank pairs need longer words. Conversely, being generic in a nonstationary parameter space does not automatically give a result on its stationary subvariety.

Brown et al. (1992) and the existing spectral reconstruction background were treated as known inputs to Astra's request. This search did not reinterpret their class-based modeling or basis formulas as a new worst-case lower theorem.

## Independent deduction: a shorter test in the d-state Moore subclass

This section is an original deduction made during the scope check. It is **not** attributed to Schönhuth, Faigle or Vanluyten, and it is not a claim about all finite-rank processes.

### Assumptions

Consider a stationary state-emitting HMM with d states, row initial distribution π, row-stochastic transition matrix M and diagonal emission matrices D_a:

\[
M_a=D_aM,\qquad
p(w)=\pi M_w\mathbf1,\qquad
\pi M=\pi.
\]

Assume π_i>0 for each state, the process has exact Hankel rank d, and the two letters under comparison have p(a)>0 and p(b)>0.

Then

\[
\frac{M_a}{p(a)}=\frac{M_b}{p(b)}
\]

holds if and only if

\[
\frac{p(av)}{p(a)}=\frac{p(bv)}{p(b)}
\quad\text{for every }|v|\le d-1.
\]

Thus words of total length at most d are sufficient within this subclass. No claim is made that this d bound is itself optimal.

### Proof

First, stationarity and the state-emitting factorization imply that M is invertible under the exact-rank assumption.

For every nonempty word u, the row πM_u belongs to the row space of M because its last factor is M. The empty-word row π also belongs to that space, since π=πM. Therefore the entire reachable row space has dimension at most rank(M). The Hankel rank is at most that dimension. Exact Hankel rank d forces rank(M)=d.

Next, minimality at dimension d implies that the columns M_v1 with |v|≤d−1 span all of R^d. This is the usual finite-rank span stabilization used in the classical reconstruction upper bound.

Let

\[
\Delta=\frac{D_a}{p(a)}-\frac{D_b}{p(b)}.
\]

Equality of the specified one-sided probabilities says

\[
\pi\Delta M M_v\mathbf1=0
\quad\text{for every }|v|\le d-1.
\]

The spanning property gives πΔM=0. Invertibility gives πΔ=0. Since Δ is diagonal and every π_i is positive, this forces Δ=0. Multiplying by M yields the normalized-operator equality. Its converse follows immediately by multiplying that equality by π and every suffix column.

The proof uses exact probabilities. It does not provide statistical error bounds.

### Consequence for comparing two processes

If both candidate processes satisfy these Moore assumptions, have exact rank d and agree on all words of length at most d, they have the same answer to the letter predicate. For d≥2, agreement through 2d−2 includes agreement through d. Such a pair therefore cannot exhibit the requested change in letter equivalence while remaining in this subclass.

This does not obstruct a Mealy construction. In a Mealy model, M_a is an arbitrary nonnegative symbol-transition matrix. It need not factor as a diagonal D_a times the common sum M. The row-space argument and diagonal Δ step then fail.

## Concrete correspondence to Astra's construction

This is a scope comparison against the local construction, not an import of a new FP mechanism.

1. **Source definitions and conditions.** The cited primary treatments distinguish general symbol-transition matrices from the state-emitting factorization M_a=D_aM. Their rank and realization results retain that distinction.
2. **Local objects.** The construction in research/frontier/OBSTRUCTIONS.md uses M_c=S and M_a=(T−S)/2+δzzᵀ, M_b=(T−S)/2−δzzᵀ, with T=11ᵀ/d.
3. **Mapping.** These are directly nonnegative Mealy symbol matrices, with transition sum T and the stated stationary row. A d-state Moore mapping would require additional diagonal emission factors in a suitable minimal basis.
4. **Derived qualification.** Since rank(T)=1 and d≥2, a stationary d-state Moore realization with that same transition sum would have Hankel rank at most one by the row-space argument. More generally, any equivalent stationary d-state Moore realization satisfying the assumptions above would obey the shorter predicate test and could not support the requested lower pair.
5. **Limits.** More hidden states, nonstationarity, a nonminimal representation relative to Hankel rank, or general Mealy operators fall outside the shorter-test statement. Mealy-to-Moore conversion can preserve the output law while increasing state count. No lower bound in the larger class is disproved here.

The existing local algebra and enumerated examples were not rerun. This memo concerns provenance and class scope. Astra retains responsibility for the final theorem wording and any integration.

## Search boundary and unresolved material

The search covered exact-title and mathematical-phrase queries for finite Hankel rank, 2d−1 and 2n−1 distinguishing lengths, stationary hidden Markov identification, probabilistic-automata equivalence, output-symbol merging, and Mealy/Moore state representations. It followed the primary references surfaced in the two complete readings, especially the older Gilbert and Blackwell–Koopmans records.

Access limits encountered:

- Gilbert: Project Euclid's current and legacy public PDF endpoints returned an unsuccessful-request page. JSTOR's PDF endpoint returned HTTP 429. Only the indexed primary abstract was usable.
- ECC 2007 and its author-report copy: direct PDF retrieval returned HTTP 503. The primary web text was available, but screenshot calls returned only textual image placeholders. No original figure was visually inspected.
- The 2008 extended article's author PDF also returned HTTP 503.
- Tzeng's publisher page exposes the abstract and a full-text access wall.
- Faigle–Schönhuth's institution final-version links returned 404. Its complete arXiv v5 was available.

These are paper-specific retrieval gaps, not grounds to stop the overall reading queue. The requested bounded search is complete. The negative result means **no exact precedent was established in the inspected material**. It does not mean that the construction is new or that an older theorem cannot imply it. Gilbert's full construction, Paz's detailed sharp examples and the Ito–Amari–Kobayashi realization treatment remain useful targets if Astra needs stronger provenance evidence.
