# Request 3f8e6cb — constructive unifilar recovery above linear rank

## Request, answer and limits

**Requested by local Astra in commit 3f8e6cbfa35741005cc3207d4acbb97a60b2cd7e, November 26, 2026, 19:04 Shanghai.** Check primary prior art for recovering every intrinsic state row of a finite unifilar generator from a finite linear representation, when its physical state count k may exceed the known global Hankel rank n. The target has strictly positive emission probability for every state-letter pair, a strongly connected update graph, probabilistically distinct states and a stationary initial distribution. Exact cylinder probabilities through length 2n−1 are supplied. The proposed extraction uses least-dimensional image spaces and positive weighted permutations. Ordinary linear realization and history/generator uniqueness are already acknowledged ingredients.

**Bounded result:** this search did not authenticate a prior explicit algorithm with that entire input, promise and intrinsic-state output interface. This is not evidence of historical absence or a novelty certificate. In particular, **k>n alone is not an adequate distinction from existing constructive work**. Bell–Smertnig already computes larger-state weighted realizations from finite linear representations; classical positive-realization work also contains actual constructions. Gao–Troitsky provides an explicit minimum-rank positive-compression/permutation-group structural precedent. The unresolved comparison concerns the stationary multiple-initial stochastic class, the permitted exact operations, and recovery of all canonical physical rows.

The most direct recent finite-summary paper, Wieczyński 2609.06735v1, has been fully read and independently archived in [its paper note](WIECZYNSKI-2026-FINITE-SUMMARIES.md), published separately as eab16a7. Its structural horizon requires finite exact synchronization and it explicitly does not recognize synchronizing rows from arbitrary tables. It also already states the classical rank-dimension finite-law bound. This eliminates two overly broad novelty formulations.

This memo is literature comparison, not an audit, proof endorsement or modification of the FOUNDATION construction. All other sources below retain scoped or screened status.

## 1. The interfaces that must be separated

| Operation | What is given | What is recovered | Relation to this request |
|---|---|---|---|
| Minimal linear realization | Exact finite word laws plus a valid global rank bound | An n-dimensional representation of the full word-probability series | Established ingredient; its coordinates need not be hidden-state probabilities. |
| Full-process canonicality | The complete stationary process law, or an already specified generator | An isomorphism class of history/generator ε-machines | Establishes uniqueness, not a finite extraction procedure. |
| Single-initial deterministic realization | A recognizable weighted series satisfying a sequentiality condition | A deterministic weighted automaton, possibly with more states than linear rank | Constructive prior art; the stationary multi-state mixture does not automatically satisfy the single-initial condition. |
| General positive realization | A linear series plus suitable positivity/cone hypotheses | Some equivalent nonnegative finite HMM | May enlarge state count; does not automatically preserve unifilarity or identify all intrinsic states. |
| Exact reconstruction of the requested class | Known n, finite exact word laws, positive strongly connected finite unifilar promise | All intrinsic rows, emissions and raw-letter updates, with unknown k | The full interface for which no directly matching prior algorithm was authenticated here. |
| Sample-based structure inference | A finite sequence, candidate structures or finite-suffix assumptions | An estimate, posterior or asymptotic consistency statement | Does not itself provide an exact finite stopping certificate from the promised probability table. |

Finite physical generators need not have finitely many finite-history residual predictions. A nonexact machine can retain a mixture after every finite history. Consequently a closure search over observed-history residuals cannot be asserted to terminate merely because the hidden generator has finitely many states. The alternating biased-coins example in Travers–Crutchfield makes this distinction explicit.

## 2. Strongest constructive neighboring result: Bell–Smertnig

**Jason P. Bell and Daniel Smertnig, Computing the linear hull: Deciding Deterministic? and Unambiguous? for weighted automata over fields, LICS 2023, pp. 1–13.** [Author PDF](https://math.smertnig.at/paper/linear_hull.pdf) · [conference record](https://lics.siglog.org/archive/2023/BellSmertnig-Computingthelinearh.html) · [arXiv record](https://arxiv.org/abs/2209.02260).

**Read:** the actual downloaded author PDF has 17 pages and a 2023 IEEE copyright notice; its equality with the 13-page conference pagination or a particular arXiv revision was not established. Root covered its pp. 1–3, including definitions, Theorems 1 and 3, Corollaries 4 and 6, the explicit construction and the proof of Theorem 1. The source assistant additionally inspected Algorithm 1 and the related Theorem 22 termination argument. The rest of the paper was not fully read.

Theorem 1 decides whether an input weighted automaton is equivalent to a deterministic or unambiguous automaton and computes one when it exists. Theorem 3 computes the linear Zariski closure of a finitely generated matrix semigroup. Corollary 6 obtains the linear hull of the reachable row set.

For a minimal d-dimensional linear representation, write that hull as a finite union of irreducible subspaces W₁,…,Wₛ. The p. 3 construction uses the direct sum of these spaces, of dimension

\[
m=\sum_i\dim W_i\ge d.
\]

The paper explicitly allows m>d. When all components are lines, the construction yields a deterministic automaton. Thus finite construction of an automaton with more discrete states than the linear dimension is already explicit primary prior art.

The definition of deterministic on p. 2 permits at most one initial state. Unambiguous means at most one accepting path for each word. In the requested stationary presentation, every state has positive initial mass, all letters are admitted, and the terminal column is all ones: its particular k-state presentation has k accepting paths per word. This does not prove that the series lacks some other unambiguous presentation. It does show that the theorem's deterministic/unambiguous promise cannot simply be read off the requested hypotheses.

Nor does this construction, in the checked passages, identify its output coordinates with the whole canonical stochastic generator row set. Its linear hull is formed from the mixed initial row's reachable orbit. A claim that this orbit closure reveals all hidden rows requires an additional argument.

The main text works over a number field for exposition, but p. 2 explicitly announces extension to fields supporting exact linear algebra in the arXiv version. The unexamined extension must not be dismissed by saying that the result only applies to number fields. Conversely, this memo has not checked its complete computational-field assumptions. No polynomial runtime or numerical stability guarantee is imported.

## 3. The relevant multiple-initial terminology

**Peter Kostolányi, Finitely ambiguous and finitely sequential weighted automata over fields, Theoretical Computer Science 1012:114725, October 12, 2024.** [Publisher page](https://www.sciencedirect.com/science/article/pii/S0304397524003426) · [DOI](https://doi.org/10.1016/j.tcs.2024.114725).

The publisher abstract and introduction explicitly use *finitely sequential* for deterministic weighted automata allowing multiple initial states. This is closer to a stationary unifilar presentation than the single-initial deterministic class. The inspected text studies expressive power and ambiguity/sequentiality hierarchies, including the distinction between finite ambiguity and finite sequentiality.

**Coverage limitation:** only the publisher's indexed abstract/introduction and visible section summaries were read. Direct page access returned 403; the full PDF and all theorem proofs were not obtained. This source cannot be ruled out as containing useful additional constructive details. It should remain an explicit unfinished source-level limitation of the search, rather than being classified as a proved nonmatch.

Queries also returned tropical, group-valued-transducer and relation-union multisequentiality results. Those semantics are not automatically ordinary sum-product probability semantics. None was used as a solution to this request.

## 4. Canonical history states and sample algorithms

### Travers–Crutchfield 2025: correct uniqueness input, including nonexact machines

**Nicholas F. Travers and James P. Crutchfield, Equivalence of History and Generator ε-Machines, Symmetry 17(1):78, January 6, 2025.** [Article](https://www.mdpi.com/2073-8994/17/1/78) · [publisher PDF actually inspected](https://mdpi-res.com/d_attachment/symmetry/symmetry-17-00078/article_deploy/symmetry-17-00078.pdf).

Root inspected pp. 9–14 and 16–19: Definition 3, history-state construction, finite characterization, the alternating-coins example, Theorem 1, its proof and Corollary 1. Appendices and the remainder remain unread. The existing index's separately named -v2.pdf URL could not be fetched for comparison; this additional scope attaches to the unversioned publisher PDF and does not silently certify edition equality.

Definition 3 requires strong connectivity, unifilarity and probabilistically distinct states, without aperiodicity or a finite synchronizing word. Theorem 1 identifies the generator with the stationary process's history machine. Corollary 1 gives isomorphism of two such generators for the same complete law. Its proof uses posterior synchronization and an almost-sure limiting argument.

The finitely characterized condition counts finitely many positive-mass equivalence classes of **infinite pasts**; it is not a finite suffix-length assumption. The checked result establishes the appropriate uniqueness but does not give the finite operator-to-intrinsic-row procedure requested here.

### CSSR 2004: finite synchronizing suffixes and asymptotic consistency

**Cosma Rohilla Shalizi and Kristina Lisa Shalizi, Blind Construction of Optimal Nonlinear Recursive Predictors for Discrete Sequences, arXiv:cs/0406011v1, UAI 2004.** [Versioned source](https://arxiv.org/abs/cs/0406011v1).

Root read the algorithm discussion through §4 and inspected the actual p. 4 assumptions; the source assistant also checked p. 5. The complete paper and referenced longer proof are not marked fully read.

Section 4 assumes conditional stationarity, finitely many causal states, and at least one finite synchronizing suffix for each state, with a common finite bound Λ. It does not require every Λ-history to be pure, so describing it simply as fixed-order Markov fitting would be inaccurate. Its structural guarantee is convergence as sequence length grows. The possibility of only finitely many wrong estimates almost surely is not an observable finite stopping certificate.

The nonexact positive generators allowed by the request need not satisfy the finite-suffix condition. No guarantee for that full class follows from the inspected CSSR theorem.

### Bayesian Structural Inference: candidate-topology inference

**Christopher C. Strelioff and James P. Crutchfield, Bayesian Structural Inference for Hidden Processes, arXiv:1309.1392v2, December 2013.** [Versioned source](https://arxiv.org/abs/1309.1392v2) · [separate journal DOI](https://doi.org/10.1103/PhysRevE.89.042119).

Root read PDF pp. 4–8, including Definitions 1–4, the candidate library and posterior formulas, and checked p. 5 visually. The 20 main pages and 15 supplementary pages were not read in full. No equality with the later journal version is assumed.

The likelihood method conditions on candidate unifilar topology and possible initial state; given these, an observed word determines at most one hidden path. The general formulas can accommodate supplied unifilar topologies beyond the paper's actual enumeration.

The demonstrated library has 36,660 binary topological ε-machine candidates with one through five states. Definition 4 uses the equal-outgoing-weight parameterization to define that subclass. Page 5 explicitly notes that full-support processes in this subclass reduce to one state. Its demonstrated library therefore does not cover nontrivial all-state/all-letter positive generators in the request. This is a limitation of that enumerated subclass, not a claim that Bayesian structural inference cannot be extended to broader topologies.

## 5. Exact word-probability construction with a different completion target

**Peter Grassberger, Some comments on computational mechanics, complexity measures, and all that, arXiv:1708.03197v3, April 6, 2018 revision.** [Versioned source](https://arxiv.org/abs/1708.03197v3).

Root read PDF pp. 3–5, including the reconstruction section and its finite-input qualifications. Figure text was extracted, but the figures and remaining paper were not comprehensively inspected; this remains a scoped reading.

This is a direct exact-input constructive hit and must not be omitted because it is historical. The paper constructs a graph from exact supplied word probabilities and forbidden words, completes leaves using suffixes, and then merges equivalent nodes. Page 3 explicitly separates a compatible finite-data graph from recovery of the entire original minimal unifilar source. When all probabilities through length ℓ are supplied, pp. 3 and 5 describe the resulting order-(ℓ−1) Markov completion.

No global Hankel-rank promise is supplied in that construction. The inspected conclusion therefore does not say that the finite completion recovers an unknown nonexact generator's entire intrinsic row set. This memo does not assess the paper's separate historical or conceptual disputes.

## 6. Positive realization and finite residuals

### Jaeger 2000, corrected author copy

**Herbert Jaeger, Observable Operator Models for Discrete Stochastic Time Series, author copy with August 2017 correction.** [Author PDF](https://www.ai.rug.nl/minds/uploads/oom_neco00.pdf).

Root read PDF pp. 13–14, printed pp. 11–12; the source assistant also scoped the model-identification discussion. Proposition 6(b) characterizes finite HMM realization using an invariant pointed polyhedral cone. The text immediately following the proposition says that this theorem is nonconstructive with respect to finding the cone. Section 9's constructive identification concerns an OOM representation.

The actual correction footnote to 6(a2) removes an unjustified pointedness condition from the more general OOM statement. This corrected copy is already the edition in the index. No use of the obsolete statement is needed here.

This source establishes the distinction between linear and positive realization. Its own nonconstructive statement does not justify saying that all positive-realization literature is nonconstructive.

### Anderson 1999: constructive positive-realization prior art, body unavailable

**Brian D. O. Anderson, The Realization Problem for Hidden Markov Models, Mathematics of Control, Signals, and Systems 12:80–120, April 1999.** [Publisher page and DOI](https://link.springer.com/article/10.1007/PL00009846).

The publisher abstract explicitly addresses construction of a finite HMM from output-string probabilities and develops existence and construction of suitable cones. This is affirmative constructive prior art. The full body was not obtained; the publisher showed subscription access and attempted PDF retrieval did not produce an accessible paper. Exact finite-input, extra-hypothesis and termination details remain unchecked.

Vidyasagar's 2005 primary conference paper discusses Anderson's procedure and its assumption that an HMM exists. That discussion is secondary evidence about Anderson, not a substitute for reading Anderson's theorem. This memo makes no assertion that Anderson's full method is incapable of treating a relevant subclass.

### Vidyasagar 2005: explicit hypotheses beyond finite rank

**M. Vidyasagar, The Realization Problem for Hidden Markov Models: The Complete Realization Problem, CDC–ECC 2005, pp. 6632–6637.** [Conference PDF](https://skoge.folk.ntnu.no/prost/proceedings/cdc-ecc05/pdffiles/papers/0862.pdf).

Root and source assistant inspected PDF pp. 2, 4–6. Theorem 2 gives the finite-rank regular quasi-realization. Theorem 5 states existence of an irreducible joint-Markov HMM under finite rank, ultra-mixing, α-mixing, and a finite cluster-point/interior-cone condition. These are statements about general HMM realization, with infinite-family or asymptotic conditions in the hypotheses.

The inspected passages do not supply the requested intrinsic unifilar-state output or establish that the request's hypotheses imply these mixing/cone conditions. This is a scoped interface comparison, not independent proof certification. A later uploaded author manuscript was dated 2009; it was not substituted for an unexamined 2011 journal edition.

### Denis–Esposito: finite residuals are a different promise

**François Denis and Yann Esposito, Rational stochastic languages, arXiv:cs/0602093v1, February 27, 2006, 35 pages; later journal publication is separate.** [Versioned source](https://arxiv.org/pdf/cs/0602093v1). The title above is the one printed on the inspected v1, without an initial “On”.

The source assistant inspected residual/PRA definitions and §4.4; root read and visually checked Proposition 22 and its proof on PDF p. 33. It characterizes stochastic languages with finitely many residuals by probabilistic deterministic automata, constructing states from residual languages.

The object is a probability distribution over finite words, with residual normalization using mass of prefix continuations. Its initial state is the language itself. A finite residual orbit together with a computable exact representation supports a terminating residual-closure search; that is a conditional algorithmic consequence, not a claim that this source solves every stationary unifilar-generator problem. The requested mixed initial prediction need not have a finite residual orbit.

### Gao–Troitsky: minimum-rank positive compressions and permutation groups

**Niushan Gao and Vladimir G. Troitsky, Irreducible semigroups of positive operators on Banach lattices, arXiv:1208.3498v1, August 16, 2012, 27 pages.** [Versioned source](https://arxiv.org/pdf/1208.3498v1) · [later journal DOI](https://doi.org/10.1080/03081087.2012.762715), Linear and Multilinear Algebra 62(1):74–95 (2014). The author-hosted later PDF returned 403. All page and theorem references here belong to the inspected arXiv v1; its generated title-page date does not replace the arXiv submission record.

Root inspected pp. 1–2, 8 and 10–11. The source assistant read the relevant continuous sections on pp. 7–16 and the finitely generated applications on pp. 18–20, checking pp. 10–11 visually. Sections 2 and 8–9 and the complete references were not fully read.

The ambient object is an already given Banach lattice with its positive order structure. The semigroup is ideal irreducible and closed under positive scalar multiplication and operator-norm limits. Theorem 4.4 and Corollary 4.6 give minimum-nonzero-rank positive projections under the stated peripherally Riesz or nonzero compact-operator hypotheses. Theorem 4.8 supplies projections P,Q of that rank with PS=SQ=S for every minimum-rank S.

Section 4.10 equips the range of a positive projection with an induced lattice structure and chooses a positive lattice basis. Proposition 4.12 then shows that the nonzero compressed operators are invertible. Their spectral-radius-normalized group consists of positive weighted permutations; one common scaling of that basis converts the group into a transitive permutation group. Thus the minimum-rank/compressed-permutation structure itself has explicit prior art.

Theorem 5.7 needs the additional common-range condition for all minimum-rank projections before obtaining a common family of positive disjoint vectors for the whole semigroup. These assumptions should not disappear in citation.

This is a structural theorem with constructive steps inside its proof, not the requested finite hidden-state discovery interface. Positivity and the lattice are already supplied. Minimum rank is taken in a semigroup containing norm limits, and cannot automatically be identified with minimum rank among finite words. The checked source supplies no finite observable-matrix encoding, unknown-row enumeration or stopping criterion recovering all k stochastic rows. Section 7's finitely generated applications concern spectral/asymptotic structure, rather than a Hankel-to-unifilar reconstruction algorithm.

## 7. Recent adjacent work screened

The search prioritized 2024–2026 sources before resolving the older interfaces above. These additional findings were inspected by the source assistant at the stated depth; none is marked fully read.

| Source | Actual coverage | Why its checked interface differs |
|---|---|---|
| [Taghavian–Sjölund, Minimal positive Markov realizations, 2502.21102v3](https://arxiv.org/html/2502.21102v3), September 3, 2025 | §§II–IV, model assumptions, Markov-form LP construction, equations (4)–(6), Theorem 1 statement | Input is a single SISO rational transfer function. Markov form is a control-theory form; the result is not multi-letter unifilar intrinsic-state extraction. Positive dimension can exceed transfer-function order. |
| [Cortese et al., Robust, positive and exact model reduction via monotone matrices, 2406.11696v4](https://arxiv.org/html/2406.11696v4), September 17, 2025; [TAC DOI](https://doi.org/10.1109/TAC.2025.3569190) | Introduction, Definitions 2–3, Problems 1–2, Theorem 3 and explanation | A positive system is already supplied. Nonnegative projection/reduction differs from discovering additional hidden coordinates from a smaller observable realization. |
| [Jurgens–Brodu, Inferring Kernel ε-Machines: Discovering Structure in Complex Systems, 2410.01076v1](https://arxiv.org/abs/2410.01076v1), October 1, 2024 | Metadata, abstract, contents and introduction | Empirical kernel predictive states and diffusion coordinates; no matching exact finite reconstruction theorem was authenticated at this screening depth. Core algorithms and appendices remain unread. |
| [Hanna Derets, Finite Automata Models: Algorithm, Application, and Semigroup Study](https://uwspace.uwaterloo.ca/items/9d44d49f-136a-4bf5-99a9-381bd131a1ae), Waterloo thesis, December 17, 2024 | Institutional metadata and abstract only | Sequence-based n-gram merging and semigroup comparisons are relevant leads. The PDF body and exact guarantees remain unexamined. |

The already completed [Zubia–Jansen HMM-identification reading](ZUBIA-JANSEN-2026-HMM-IDENTIFICATION-COMPLEXITY.md) is another recent boundary: its principal decision problem takes a supplied parameterized HMM family and asks about uniqueness. Its use of deterministic means pointwise identifiability, not unifilar transitions. Its imported Appendix I rank-only sufficient criterion has a recorded counterexample. Those results do not provide the requested reconstruction procedure.

## 8. A computability baseline, separately labeled

**The following is a bounded combination observation, not a located published reconstruction algorithm and not a proposed change to FP theory.** It prevents the search's negative result from being mistaken for an absence of any constructive route.

If the given finite linear representation has rational or real-algebraic coefficients with effective finite encodings, one can enumerate finite state counts and total deterministic transition tables. Strong connectivity is a finite graph condition. For a fixed table, positivity, stochastic row sums, stationarity, pairwise probabilistic distinction and equivalence to the supplied linear representation can be expressed by a finite semialgebraic system.

Equivalence can use the classical finite witness length n+k−1 for the two representations. Pairwise state distinction can use finite future witnesses in the candidate k-state representation. The variable terminal column of a general linear realization must be retained; it is not automatically the HMM all-one column. Under the promised existence of a finite admissible generator, a systematic search eventually reaches a satisfiable candidate.

To output a machine, the real-algebraic procedure must return a witness/sample point, not merely answer the ETR decision problem. Canonical generator uniqueness then identifies an admissible recovered generator up to isomorphism. This is only a promise-termination baseline: it gives no useful efficiency, no stopping on negative instances, no finite-sample guarantee and no numerical stability.

Arbitrary abstract real coefficients are a different interface. Exact additions, ranks, subspaces or spectral decisions do not by themselves supply a complete ordered-field quantifier-elimination oracle. Therefore this observation cannot be silently equated with the proposed exact linear/spectral construction.

## 9. Search record and remaining uncertainty

The bounded searches covered combinations of unifilar reconstruction, Hankel rank, finite ε-machine summaries, deterministic probabilistic automata, spectral learning, positive realization, linear hulls, finite ambiguity/sequentiality, and positive weighted permutations. Primary publisher, arXiv, author and institutional sources were preferred. Publication/version dates were checked separately from search crawl dates.

Limitations material to the answer:

1. Anderson 1999 was authenticated only at publisher-abstract level; its detailed constructive theorem was not accessible.
2. Kostolányi 2024 was screened through publisher text, not fully read. The multiple-initial class is an especially relevant remaining interface.
3. Bell–Smertnig's full computational-field extension and all implementation details were not audited.
4. Positive-operator and transformation-semigroup literature was not exhaustively covered; no absence claim follows from the inspected subset.
5. Searches did not exhaust all terminology, non-English work, dissertations, unpublished notes or every reference chain.
6. No prior-work comparison in this memo certifies Astra's proof, complexity, stability or sample bounds.

The useful source-grounded conclusion is narrower than a novelty declaration: classical finite-law realization and canonicality should remain acknowledged; larger-state constructions already exist; finite-suffix, residual, general-positive and stationary-unifilar interfaces must be separated explicitly. The whole target interface remains unmatched within the authenticated scope above.
