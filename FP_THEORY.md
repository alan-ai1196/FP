# Factor Programs (FP) — Canonical Theory

**Canonical status (2026-09-06): THEORY FROZEN; IMPLEMENTATION NOT FROZEN; SCIENCE HOLD.**

This file is the **only normative theory source** for FP. Historical v1–v155 canonicals, v156–v164 attack drafts, R2/R3/R4 working files and experiment-era theory snapshots are provenance only. If an older statement conflicts with this file, this file wins.

The theory is frozen in the following sense: do not add a new architecture-semantic mechanism merely to make search faster. If implementation exposes a mathematical counterexample to the declared object, reopen theory. If it exposes only hard search, weak information, expensive certificates, numerical ambiguity or insufficient fresh evidence, improve the solver or return `UNRESOLVED`.

No new RTX3090/model-science run is authorized until the complete Reference Compiler runtime instantiates this contract in the float64/reference path and the actual target AMP path passes its event-level bridge gates.

---

## 0. Research object and root principle

FP asks whether a **typed causal positive program** can allocate useful distinctions and physical graph structure under ordinary task loss and hard resources without being handed a fixed architecture topology or a finite menu of model actions.

The repeated v1→v155 failure mode is now compressed to one rule:

> **Never erase or assume information before proving that every legal future continuation relevant to the claim cannot use it.**

A sound structural claim therefore requires three declared objects:

\[
\boxed{
\text{complete claim state}
+\text{legal information interface}
+\text{physical computation/resource model}.
}
\]

The three corresponding failure modes are:

1. **premature quotient** — two states/programs are identified because they agree under a smaller current observable while a later legal continuation distinguishes them;
2. **hidden oracle** — the Compiler is silently granted relation/rank/counterexample/factor/cost information without an acquisition interface and cost;
3. **correctness ≠ tractability** — finite exact decidability is mistaken for scalable self-compilation.

---

# I. Minimal native semantic calculus

## 1. Primitive sources and causality

Before learning, the claim declares a finite or effectively indexed primitive source family \(\mathcal X_0\). Every score-time source has:

- a semantic type;
- a nonnegative semantic codomain;
- an availability delay;
- a rule making its score-time value measurable before the current target.

The current target, a statistic already depending on that target, or an undeclared signed/complement leaf is not a legal primitive score-time source.

An effectively indexed source schema such as lag/token atoms

\[
1[x_{t-\ell}=v]
\]

need not be materialized densely, but its index set and evaluation rule are fixed by the claim and its search/query cost is not free.

## 2. Native operations

For nonnegative values,

\[
\boxed{z_{SUM}=\sum_i a_i z_i,\quad a_i\ge0,}
\]

\[
\boxed{z_{PRODUCT}=z_Lz_R.}
\]

`SUM` combines declared compatible result types. `PRODUCT` is legal only under a declared product/composition rule. The zero-delay dependency graph is acyclic. A recurrent cycle is legal only through positive causal delay; same-time algebraic fixed points are not an implicit primitive.

The semantic primitive set is therefore:

1. typed causal nonnegative sources;
2. positive SUM;
3. positive PRODUCT;
4. positive normalized output readout;
5. delayed recurrent state transitions whose transition body is itself a legal typed positive program.

There is no canonical `SPLIT`, `MERGE`, `REWIRE`, `BIRTH`, `GROW-R`, `DENSE`, `PROBE-MORE` or similar model-action vocabulary. Such words may describe search bookkeeping or historical experiments but do not extend the grammar.

## 3. Positive output

For evidence \(m_y\ge0\) and strictly positive causal base \(b_y>0\), let \(B=\sum_y b_y\). The native readout is

\[
\boxed{p_y=\frac{b_y+m_y}{B+\sum_z m_z}.}
\]

Zero semantic mass is legal. Log coordinates are only a numerical coordinate where represented values are strictly positive.

## 4. Provenance responsibility

For one SUM derivation family,

\[
y_m=\operatorname{LSE}_{p\in\mathcal P_m}u_{m,p},
\qquad
\rho_{m,p}=e^{u_{m,p}-y_m},
\]

and the exact local backward rule is

\[
\boxed{\bar u_{m,p}=\rho_{m,p}\bar y_m.}
\]

This R5 identity is foundational: signed task credit may flow backward while persistent semantic mass remains positive. Marginalizing derivation/provenance identity before proving it future-irrelevant can erase useful structural information.

A positive provenance measure is a coordinate system for semantic derivations, not the whole physical graph: sharing, fusion, encoding, scheduling and ownership can change physical resources and future Compiler optionality without changing an extensional measure.

---

# II. Complete claim state and safe quotients

## 5. Complete self-Compiler state

The scientific runtime object is the complete configuration

\[
\boxed{\Omega=(\xi,\iota,s,m_C,\kappa),}
\]

where \(\xi\) is the consumed exogenous/logical-event cursor; \(\iota\) is learner lineage; \(s\) is complete learner state; \(m_C\) is complete mutable Compiler state; and \(\kappa\) is claim/resource/numerical/statistical context.

Anything that can change a future legal claim-relevant transition belongs in \(\Omega\): model/optimizer/recurrent state, RNG, live shadows, jobs, frontier/queue/scheduler, certificate provenance, object ownership, resource/error ledgers and revealed information.

Semantic program, physical learner, certificate and persistence evidence are distinct projections of this one causal system.

## 6. Exact claim-relative behavioral congruence

A contract \(\mathfrak C\) declares legal exogenous continuations, legal controls/actions, transition semantics and required claim/resource/numerical observables.

For the deterministic exact case define

\[
\Omega\equiv^0_{\mathfrak C}\Omega'
\]

iff every legal finite continuation has matching legal-action availability and identical required claim traces from both states.

Then \(\equiv^0_{\mathfrak C}\) is an equivalence relation, a transition congruence and the coarsest exact symmetric quotient preserving those traces.

A proposed quotient \(\pi\) is safe only if the exact system factors through it:

\[
\boxed{
O=\bar O\circ\pi,\quad
R=\bar R\circ\pi,\quad
A_{legal}=\bar A_{legal}\circ\pi,\quad
\pi\circ T_{e,a}=\bar T_{e,a}\circ\pi.
}
\]

For stochastic/nondeterministic transitions, use a separately proved pathwise/probabilistic simulation or bisimulation under the declared coupling/filtration law; one realized trace is not a transition theorem.

## 7. One-sided and approximate claims

Directional no-worse replacement is a preorder

\[
\Omega\preceq_{\mathfrak C}\Omega',
\]

not an equivalence quotient. It can justify a directional prune/replacement only in the proved direction. It becomes a quotient only when both directions and congruence are established.

Approximate preservation uses a behavioral pseudometric, packing/covering or an error simulation with an explicit composition law. In general

\[
d(x,y)\le\varepsilon
\]

is not transitive, so “epsilon equivalence classes” are invalid.

Current-function equality, one-step response equality, semantic gauge equality, same provenance measure, ordinary learner bisimulation or static Pareto dominance is insufficient unless it implies the claim-relative relation above.

---

# III. Behavior-first capacity

Let \(\mathcal Y\) be the set of claim-relative future behavior objects under metric \(d_{\mathfrak C}\).

For deterministic categorical compression with worst-case error \(\varepsilon\),

\[
\boxed{
\mathsf{Pack}_{>2\varepsilon}(\mathcal Y)
\le K^*_{cat}(\varepsilon)
\le \mathsf{Cover}^{legal}_{\varepsilon}(\mathcal Y).
}
\]

For a finite exact behavior family,

\[
\boxed{K^*_{cat}(0)=\#\{\text{distinct claim-relative behaviors}\}.}
\]

A finite physical state with \(b\) bits obeys

\[
\boxed{b\ge\log_2\mathsf{Pack}_{>2\varepsilon}(\mathcal Y).}
\]

If a smooth family contains an \(r\)-dimensional metrically nondegenerate patch and factors smoothly through \(k\) coordinates, then \(k\ge r\). If

\[
d(F(u),F(v))\ge c\|u-v\|_\infty,
\quad F:[0,L]^r\to\mathcal Y,
\]

then finite-precision state information scales at least as

\[
b\gtrsim r\log_2\frac{cL}{2\varepsilon}
\]

up to endpoint/floor constants.

These are representation-independent statements. Rank notions below are restricted realization/interface statements.

---

# IV. Exact categorical and one-shot realization theorems

## 8. Residual/categorical state

For a finite deterministic task and cut \(S\),

\[
a\sim_S b\iff\forall c,\ f(a,c)=f(b,c),
\qquad D(S)=|X_S/\!\sim_S|.
\]

A single exact deterministic categorical separator needs exactly \(D(S)\) labels.

Across an isolating causal cut for continuation class \(\mathcal C\), any finite exact physical state needs at least \(D_{\mathcal C}\) distinguishable states and therefore

\[
\boxed{b_{state}\ge\lceil\log_2D_{\mathcal C}\rceil.}
\]

Approximation replaces this by the predictive/behavioral packing bound. These are state-information bounds, not generic vector width, node count, generator count, FLOPs or bytes under an unspecified realization.

## 9. Bit-coded positive recurrence

Any deterministic \(D\)-state machine can be embedded in native positive recurrence with \(m=\lceil\log_2D\rceil\) bits represented by \(2m\) positive simplex coordinates. If \(c_j(s)\) is bit \(j\) of state \(s\),

\[
\chi_s(z)=\prod_{j=1}^m z_{j,c_j(s)},
\]

\[
\boxed{
z'_{j,b}=\sum_{s,a:c_j(\delta(s,a))=b}1[a]\chi_s(z).
}
\]

The transition is exact on categorical vertices and extends multilinearly to \((\Delta_2)^m\). Unused binary codes can be completed differently, so the soft interior extension is an existence theorem, not uniqueness.

## 10. One-shot positive realization hierarchy

For nonnegative one-shot response matrix \(R\):

- minimum deterministic categorical labels = number of distinct response rows;
- in the **linear positive-mixture interface**, minimum generator count = \(\operatorname{rank}_+(R)\);
- unrestricted PRODUCT invalidates any inference from \(\operatorname{rank}_+(R)\) to general FP coordinate dimension.

For \(k\) positive scalar coordinates and total polynomial degree at most \(d\),

\[
\boxed{
\max\operatorname{rank}R
=\max\operatorname{rank}_+R
={k+d\choose d}.
}
\]

If maximum PRODUCT-path instruction depth is \(b\), then \(d\le2^b\), giving one-shot rank capacity

\[
\boxed{{k+2^b\choose2^b}.}
\]

---

# V. Predictive mixtures are restricted; recurrent FP is broader

A fixed-generator positive predictive realization can be written as a polyhedral cone \(K\) containing reachable predictive states, lying inside the observability-positive cone and invariant under every legal symbol-shift operator.

Finite-horizon nonnegative rank is a projection lower bound for this class. The minimum invariant-cone generator count can jump under arbitrarily small process perturbations. That is a classical positive-realization turning point, not a general FP coordinate/program/hardware lower bound.

General recurrent FP can be much smaller. A one-positive-scalar affine recurrence with native normalization can generate length-\(H\) word-probability functions whose linear span is the full \(2^H\). Thus finite-horizon response rank can grow exponentially while internal positive coordinate dimension remains one.

For polynomial transitions of degree \(d_T\) and readout masses degree \(d_R\), finite-horizon behavior has an explicit rational/polynomial lift and hence a monomial-space span upper bound; this is an **extrinsic response-span** bound, not a state-dimension theorem.

---

# VI. Categorical→positive and dense limits

## 11. Finite-context universality

With the complete declared lag/token positive partition basis, every finite categorical context indicator is a legal PRODUCT monomial. Under a fixed strictly positive base, finite-history positive SUM/PRODUCT can exactly realize every strictly positive finite-context conditional distribution.

Against a changing normalized positive base, choosing evidence scale \(M\) yields

\[
\boxed{\|p_t-q\|_\infty\le\frac1{1+M}.}
\]

A coarser source contract does not inherit this universality for free.

## 12. Positive dense-attention limit

The exponential dot-product kernel admits a positive random-feature representation. Therefore a sequence of **declared finite positive-feature contracts** can converge to normalized dense exponential attention for nonnegative/simplex-valued values.

This is a limit across legal finite approximants. It does not create undeclared infinite features, arbitrary signed hidden-value attention or a free continuous source family inside one fixed finite Compiler contract. Exact separable shared-feature realizations have scoped rank lower bounds on Vandermonde families; no universal quadratic lower bound over all attention algorithms/hardware is claimed.

---

# VII. Extensional semantics vs intensional physical realization

Two semantic programs may compute the same current positive function while differing in sharing, object ownership, build/install cost, optimizer coordinates, future value directions or future Compiler optionality.

Therefore extensional semantic equality does not imply physical equivalence. Semantic factorization/provenance becomes intensional claim information whenever resources or future learning/search depend on it.

A physical learner lineage includes at least

\[
\iota=(G,e,\sigma,U,\mathcal S_{causal})
\]

plus the registered initialization/profile/transport semantics needed by the claim. A graph-only science claim fixes non-graph coordinates; a joint search over \((G,e,\sigma,\ldots)\) is physical-program compilation and must be reported as such.

A semantic PRODUCT may be fused away by lowering and still be semantic PRODUCT. A hardware multiply introduced only by lowering is not evidence of semantic PRODUCT emergence.

---

# VIII. Resource model and physical reachability

Hard resources are typed functionals of the **executed history**

\[
\boxed{\mathcal R_k[\Gamma_{0:t}],}
\]

including as declared current residency, peak residency, cumulative work, latency or other physical quantities. There is no canonical scalar exchange rate between CE, bytes, FLOPs, compile work and latency.

Target/deployment realization resources \(B_{dep}\) and Compiler exploration resources \(B_C\) are distinct roles fixed before seeing the result. A debit is not moved between roles after the outcome.

Final-state feasibility does not imply build/install reachability. If the incumbent occupies capacity 1 and the candidate also occupies 1 under a peak cap of 1, build-before-free can make the candidate unreachable unless the physical machine contract supplies a certified atomic replace operation.

No new causal state obtains forgotten history for free. It must come from a proved transport/refinement, charged replay over retained history, or an explicit reset/newborn initializer after which only future data can certify persistence.

---

# IX. Divisible semantic support vs fixed-cost materialization

Continuous positive-measure allocation can obey an ordinary constrained KKT flow when capacity is divisible. This does **not** solve physical graph materialization when a live record has fixed charge

\[
C_{fixed}\mathbf1[\mu_i>0].
\]

Even after acquisition/value is made trivial, selecting independent candidates with gains \(g_i\), fixed costs \(c_i\) and budget \(B\) contains

\[
\boxed{
\max_{x_i\in\{0,1\}}\sum_i g_ix_i
\quad\text{s.t.}\quad
\sum_i c_ix_i\le B,
}
\]

which is 0–1 knapsack. Thus the physical Compiler is not an artificial patch eliminable by pretending fixed cost is a smooth mass budget.

---

# X. Information interface and acquisition

## 13. Transcript observability

For admissible hidden structure \(h\in\mathcal H\), a legal query strategy produces transcript \(\mathcal A(h)\). Exact acquisition requires

\[
\boxed{
\mathcal A(h)=\mathcal A(h')\Rightarrow h\equiv_{\mathfrak C}h'.
}
\]

For fixed linear observation \(A\),

\[
\ker A\cap(\mathcal H-\mathcal H)
\subseteq\mathcal N_{\mathfrak C}.
\]

Finite precision additionally requires stable separation; exact injectivity with vanishing minimum separation is numerically ill-conditioned and may be `UNRESOLVED` under the registered enclosure.

Probe count alone is not information complexity. A probe's output dimension and registered precision determine how many claim-separating bits it can carry, and its physical computation is charged separately.

## 14. Low-rank operator acquisition

For exact rank-\(r\) matrix \(M\in\mathbb R^{m\times n}\) with legal two-sided matrix-free access, draw generic \(\Omega\in\mathbb R^{n\times r}\), query

\[
Y=M\Omega,
\]

let \(Q\) span \(\operatorname{range}(Y)\), then query

\[
Z=M^TQ.
\]

With probability one in exact arithmetic,

\[
\boxed{M=QZ^T,}
\]

using at most \(r\) forward and \(r\) adjoint vector probes. This reconstructs signed response geometry; it is **not automatically** a legal positive SUM/PRODUCT factorization or cheap physical realization.

## 15. Positive PRODUCT acquisition

For a finite acyclic positive SUM/PRODUCT region with dormant structural gates \(z_i\), each unnormalized factor-space boundary mass expands as a polynomial

\[
M_y(z)=\sum_\alpha c_{y,\alpha}z^\alpha,
\qquad c_{y,\alpha}\ge0.
\]

On Boolean subset probes \(z=1_A\),

\[
M_y(1_A)-M_y(0)=\sum_{\varnothing\ne S\subseteq A}\tilde c_{y,S}.
\]

Thus, **if arbitrary subset probes are legal**, sign/magnitude queries reduce minimal positive PRODUCT completions to hidden-hypergraph/monotone-DNF acquisition. A single hidden conjunction \(S\subset[n]\) can be queried by

\[
O(A)=1[S\subseteq A],
\]

whose complement is a group test. Adaptive splitting gives \(O(|S|\log n)\) probes in this interface, with information lower bound \(\lceil\log_2{n\choose|S|}\rceil\).

This does not grant arbitrary interventions. Under a prefix-only or passive interface, distinct supports can have identical transcripts. Round-35's \(q^*=d\) result is therefore a **local-jet observation-language lower bound**, not a universal self-compilation lower bound.

General hidden hypergraphs can require exponential query complexity; low-overlap families have polynomial-query regimes. PRODUCT depth alone is not the correct universal acquisition-complexity parameter.

---

# XI. Known-factor exact solve and typed frontier

Let structural variables \(z_v\in\mathcal Z_v\), \(|\mathcal Z_v|=S_v\), factor through a graph/hypergraph with tree decomposition \(\mathcal T\). Define typed frontier load

\[
\boxed{\Phi(\mathcal T)=\max_B\sum_{v\in B}\log S_v.}
\]

Given exact/certified local factors,

\[
\boxed{
C_{solve}=O\!\left(\sum_{B\in\mathcal T}\prod_{v\in B}S_v\right)
\subseteq O(|\mathcal T|e^\Phi).
}
\]

All nonlocal history/resources required for exactness must be carried through the frontier state; dropping them merely to reduce width is unsound.

Acquisition cost is separate:

\[
C_{compile}\le C_{acquire}+O(|\mathcal T|e^\Phi)+C_{cert/install}.
\]

For an unrestricted frontier table of \(M=e^\Phi\) assignments under point queries, an adversary can force all \(M\) queries before exact certification. This unconditional information-model lower bound explains why exact solve cannot be universally cheap.

---

# XII. Exact Compiler problem and honest status

## 16. Candidate construction from grammar

The Compiler does not receive an external architecture family. A finite resource-bounded native semantic DAG is generated recursively from source references, positive SUM, positive PRODUCT and legal delayed state binding. Search may quotient partial construction states only after claim-relative contextual congruence is proved.

A large syntactic candidate universe may admit compact representation; the number of behavioral equivalence classes is a state-information quantity and is not by itself a runtime lower bound. Acquisition/signature computation and optimization work are separate complexities.

## 17. Truth objective

A structural candidate's value is its **constructively reachable**, registered trajectory value, not a free optimum over all encoded numbers. Schematically

\[
\boxed{
V_H(\Omega;D)
=\sup_{\gamma\in\mathsf{Cont}_H(\Omega;D),\ \mathcal R[\gamma]\preceq B}
T_D(\gamma_H).
}
\]

`Cont` contains only registered initializer/profile/optimizer/state-transport/Compiler transitions. Encoded-but-unreachable states may appear only in optimistic uppers.

First-order scores, GN/HVP, monomial duals, rank sketches, kernels and relaxations are proposal/upper-bound accelerators, not truth conditions. A branch can be globally pruned only by a sound upper covering its exact finite-amplitude/declared trajectory objective plus sound resource lower bounds.

Compound descendants do not require profitable proper parents.

## 18. Finite exact decision and `UNRESOLVED`

For an explicit finite/effectively finite decision class with certified task/feasibility comparisons, exact or certified \(\varepsilon\)-complete branch-and-bound is valid. Every prune has theorem/certificate provenance. If a live region can still beat the incumbent, a feasibility boundary is undecidable at current precision, or work/resource budget expires, return

\[
\boxed{\texttt{UNRESOLVED}.}
\]

Do not insert a heuristic architecture decision and relabel it completeness.

No universal polynomial-time exact Compiler is claimed. Exact NMF is NP-hard in a contained restricted interface; fixed-charge materialization contains knapsack; unrestricted point-query frontier acquisition can require \(e^\Phi\) queries. Some broader exact recurrent/equivalence contracts may not even be effectively decidable.

---

# XIII. What “structure emerges from task loss + budget” means

For a declared finite-prefix/horizon target-program problem, let

\[
\mathcal O_{B_{dep}}(D,H)
=\operatorname*{arg\,max}_{\Omega'\in\mathfrak R^{target}_{B_{dep}}(\Omega_0)}
V_H(\Omega';D).
\]

A structural property \(P\) is **task-resource forced** iff

\[
\boxed{
\mathcal O_{B_{dep}}(D,H)\ne\varnothing
\quad\text{and}\quad
P(\operatorname{dep}(\Omega'))\ \text{for every }\Omega'\in\mathcal O_{B_{dep}}(D,H).
}
\]

The property must be defined on the declared semantic or physical object and invariant to nuisance renamings. If exact optima include both \(P\) and \(\neg P\), an engineering tie-break does not make \(P\) scientifically forced.

For \(\varepsilon\)-complete decisions, call \(P\) forced only when every still-possibly-feasible \(\varepsilon\)-optimal candidate has \(P\); otherwise the structural phase is unresolved.

Increasing hard caps makes feasibility monotone but **optimal structure need not be monotone**. A phase transition is a change in the forced-property set along a declared budget path, not a claim that all tasks have a phase.

Compiler exploration budget \(B_C\) and target/deployment budget \(B_{dep}\) are distinct. A graph found only because more search was spent is a Compiler-work effect unless the scientific claim explicitly studies self-Compiler resource phases.

---

# XIV. Persistence and global filtration

## 19. Global filtration

Let \(\mathcal F_t\) be the complete revealed history of the actual self-Compiler through logical event \(t\): observations/targets already revealed, learner/shadow states/actions, Compiler actions/results, resource/error ledgers and all RNG outcomes used so far.

Admission, horizon, bounds, betting fractions and error allocation are **predictable** only when measurable from the actual pre-event filtration. A random coin hidden from the theorem filtration is not magically predictable because it was sampled earlier in wall time.

Proposal/discovery/profile data and persistence evidence obey declared data roles. Validation/test labels are read-only reporting data. Proposal/profile observations cannot be recycled as “fresh” persistence evidence.

## 20. Lineage-specific e-process

For one fixed candidate lineage against one fixed deployed comparator, define paired epoch gain \(Y_j\). Under

\[
\mathbb E[Y_j\mid\mathcal F_{j-1}]\le0,
\quad |Y_j|\le B_j
\]

with predictable bound and predictable \(0\le\lambda_j<1\),

\[
\boxed{
E_n=\prod_{j=1}^n\left(1+\lambda_j\frac{Y_j}{B_j}\right)
}
\]

is a nonnegative supermartingale; Ville yields anytime type-I control. A probability guarantee requires an explicit stochastic/randomization law; merely unread future tokens on a fixed deterministic corpus do not create one.

Evidence is bound to claim key, base lineage, candidate lineage, continuous complete-state trajectory, initializer/transport provenance and alpha allocation. Re-forking, reinitializing or switching base/candidate creates a new certification identity unless a separate transport theorem proves otherwise. Alpha is not silently recycled from stale/failed identities.

Finite-horizon no-crossing is **not rejection**. Without a valid negative certificate, the result remains unresolved/not certified.

---

# XV. Reference and AMP are two matched causal claims

Science tracks the same-path gains

\[
\boxed{
Y_j^{ref}=L_{dep,j}^{ref}-L_{cand,j}^{ref},
\qquad
Y_j^{AMP}=L_{dep,j}^{AMP}-L_{cand,j}^{AMP}.
}
\]

The reference candidate is not compared with an AMP deployed loss, and vice versa.

Both deployed and candidate trajectories require their own initialization and event-level reference↔AMP relation. The relation must hold before every score, after target-driven causal updates that can affect later scores and after optimizer commits. A coarse endpoint check is valid only when separately proved to imply all internal event relations.

If nondeterminism is not represented by explicit RNG/state coordinates, the bridge must cover the transition relation/kernel pathwise or through an explicit probabilistic coupling theorem.

The reference chain is

\[
\boxed{
\text{abstract real semantics}
\to\text{certified float64 reference}
\to\text{certified AMP physical path}.
}
\]

Theorem/algorithm audits use exact arithmetic or float64 reference. Real GPU execution uses the registered AMP path only after the bridge is certified. Decision-critical ordering uses exact encoded arithmetic or sound enclosures; overlapping enclosures are unresolved rather than separated by an arbitrary epsilon.

---

# XVI. Atomic self-Compiler boundary

After an epoch/certification boundary, at most one target lineage is installed. The complete transition is atomic:

\[
\boxed{\Omega_{old}\longrightarrow\Omega_{new}.}
\]

The structural boundary itself does not advance the exogenous cursor; only registered ordinary learner score/observe events do.

The transaction includes:

- exact target reference and AMP complete states;
- install/state transport;
- live shadow retention/release;
- job cancellation/retention/quiescence;
- frontier/queue/scheduler/RNG changes;
- physical object ownership/refcount transfer;
- cumulative/current/peak resource accounting;
- certificate staleness/rebase;
- error/persistence ledger changes;
- post-install bridge state.

Marking a shadow/job stale does not physically release its memory or future side effects.

A resource-only task-probation bypass is permitted only under a **strong complete self-Compiler equivalence/simulation certificate** preserving future learner and Compiler behavior/resources. Current-function equality or ordinary learner equivalence is insufficient when future structural optionality differs.

---

# XVII. Anti-unigram identifiability gate

The historical hierarchical gate uses a hidden binary group label \(g_i\) for tokens and pair relation

\[
r_{ij}=g_i\oplus g_j.
\]

If the observed train relation graph is connected and labels are consistent, choose one root group arbitrarily and propagate XOR constraints along a spanning tree. All group labels are then identified up to the unavoidable global flip, which leaves every XOR prediction invariant.

If the observed graph has \(c>1\) connected components, each component may be flipped independently without changing observed relations, yielding \(2^{c-1}\) task-distinct relative assignments modulo global flip. Unseen cross-component relations are therefore not exactly identifiable without more evidence.

Once the partition is identified, each group source is a legal positive SUM of token one-hot atoms and pair cells are native PRODUCT. The Compiler must not be handed latent group IDs or the conditional relation table.

## XVII.1. Sharp normalized-SUM control and a scoped PRODUCT-forcing certificate

For a static two-binary-input task with only the four unary indicator sources,
fixed base `(1,1)`, fixed finite coefficients, an acyclic SUM-only DAG of
arbitrary width/sharing, and one final native normalization, every output mass
is additive: `M_y(i,j)=1+u_{y,i}+v_{y,j}`. This is an extensional loss envelope,
not a physical or complete-state quotient.

A strictly positive binary conditional table `p_ij=P(Y=1|i,j)` is realizable
iff the relative interiors of `conv{p_00,p_11}` and `conv{p_01,p_10}` intersect.
Its prediction-family closure replaces relative interiors with closed intervals.
For arbitrary positive cell weights, if the target intervals are disjoint, the
exact log-loss infimum is obtained by pooling one diagonal/off-diagonal pair:
choose the least weighted Bernoulli entropy increase among the four pairs and
leave the other target probabilities unchanged. Integer-count likelihoods
permit exact rational comparison. This solves a relaxed prediction envelope;
it does not authorize unreachable coefficient states or Compiler completion.

For balanced XOR with symmetric noise `0<=eta<=1/2`, this gives the sharp bound

\[
\boxed{\inf_{SUM}L=\tfrac12[\log2+H(\eta)].}
\]

For `eta<1/2` it is an unattained infimum over finite coefficients. In particular,
SUM plus normalization can beat unigram: the deterministic-XOR infimum is
`(log 2)/2`, not `log 2`. This same sharp control holds for arbitrary unary
token-specific SUM coefficients in the hidden-group task under block-factorized
within-group sampling; it does not assume the baseline knows the hidden groups.

One semantic PRODUCT suffices for an exact noisy-XOR conditional. With the
declared one-indicators `x,z` and `r>=1`, use

\[
M_0=r+2r(r^2-1)xz,\qquad M_1=1+(r^2-1)(x+z).
\]

The constant extra mass is a SUM of the declared partition atoms. Correct-label
probability is `r/(r+1)` at all four cells. In particular `r=3` uses masses
`3+48xz` and `1+8(x+z)` and obtains deterministic-XOR loss `log(4/3)<(log2)/2`.

If a registered reachable target class has a nonempty optimal set and a feasible,
constructively reachable witness strictly below the SUM envelope, every optimum
contains semantic PRODUCT. For epsilon-optimal forcing require
`L_witness+epsilon<inf_SUM L`. Source enrichment, internal normalization, adaptive
recurrence, an input-dependent base, build/install reachability, and fresh
persistence are separate conditions; this theorem does not grant them.

Full proofs, weighted formulas, nonattainment, and exact audits are in
[`NORMALIZED_SUM_XOR.md`](theory/proofs/NORMALIZED_SUM_XOR.md).

More generally, **one shared semantic PRODUCT suffices for every strictly
positive 2x2 conditional table with any finite output alphabet** in this same
static source/readout contract. Choose positive scaled target vectors
`A=C_00 p_00>=1`, `B=C_01 p_01>=A`, `C=C_10 p_10>=A`, and
`E=C_11 p_11-(B+C-A)>=0`. Then

\[
\boxed{M(x,z)=A+(C-A)x+(B-A)z+E xz}
\]

normalizes exactly to the four target distributions. Choosing each scale as
the maximum necessary coordinate ratio makes every coefficient finite and
nonnegative; at most `k-1` output heads need a nonzero PRODUCT edge.

The zero-PRODUCT criterion is intersection of the relative interiors of the
**vector** segments `conv{p_00,p_11}` and `conv{p_01,p_10}`. Thus the exact
minimum semantic PRODUCT count is 0 when they intersect and 1 otherwise.
Coordinatewise interval overlap is insufficient for multiple output labels.
For binary touching intervals, exact realization may need 1 PRODUCT even
though 0 PRODUCTs approximate arbitrarily well: exact count is not a robust
epsilon-optimal forcing certificate. This does not minimize coefficient range,
SUM structure, or any unspecified physical resource. See the constructive proof
and exact counterexample in
[`ONE_PRODUCT_CONDITIONAL_TABLE.md`](theory/proofs/ONE_PRODUCT_CONDITIONAL_TABLE.md).

## XVII.2. Exact membership and closure for a known finite positive mass cone

Fix a finite context/output table, known nonnegative rational mass atoms `a_j`,
strictly positive causal base `b`, and independently variable nonnegative SUM
coefficients. Write `M(v)=lambda b+sum_j w_j a_j`, `v=(lambda,w)>=0` and
`T_x=sum_y M_xy`. The actual finite family has `lambda>0`, rescaled to the fixed
base. For a known target table `p`, exact realization is a rational LP with
`M_xy=p_xy T_x` and `lambda>=1`.

Approximation closure requires more than a nonzero solution with `lambda=0`:
cells with `T_x=0` are unresolved, not automatically matched. On the current
residual set `R`, solve

\[
v\ge0,\quad M_{xy}(v)=p_{xy}T_x(v)\ (x\in R),\quad
\sum_{x\in R}T_x(v)=1.
\]

Retain any feasible direction and remove only its positive-total contexts.
Repeat on all remaining cells. This decides closure in at most `|X|` rational
LPs for the explicitly known atom table. Any choice of feasible direction works.
Infeasibility is witnessed by a linear alternative on the residual set; absent
a checkable primal/dual certificate, the numerical implementation is unresolved.

Successful directions `v_0,...,v_(L-1)` give the finite positive-base sequence
`sum_l epsilon^l v_l+epsilon^L e_b`, with an explicit rational `O(epsilon)`
prediction-error bound. They are proof layers for a limiting coefficient
sequence, not new semantic model actions. Coefficient range, acquisition,
registered value construction, and physical resources are still charged.

A 3x3 unary-source table with uniform predictions on the outer row/column and
noisy XOR in the interior falsifies the single-LP shortcut: its first cone
direction exists, yet the unresolved interior has exact sup-norm distance
`1/4` from every SUM-only predictor. The procedure is a complete **static
known-cone membership/closure** result, not general FP compilation or a
Reference Compiler `CERTIFIED_COMPLETE` decision. Proof and exact certificates:
[`NORMALIZED_POSITIVE_CONE_CLOSURE.md`](theory/proofs/NORMALIZED_POSITIVE_CONE_CLOSURE.md).

The global problem cannot be replaced by local face certificates. On the
three-bit cube the rational table
`(1/10,11/30,19/30,11/30,19/30,11/30,19/30,9/10)` has every coordinate face in
SUM closure and every probability superlevel set linearly separable, yet its
distance to the whole unary-SUM family is **exactly 2/15**. A common affine
numerator/denominator obeys coupled constraints absent from independent cuts.
An explicit top-parity dual certifies the distance and a finite integer-mass
SUM model attains it; uniform excess CE is at least `1/225`. This falsifies
both shortcuts, not the full known-cone solver. Proof and exact audit:
[`LOCAL_SUM_CERTIFICATE_COUNTEREXAMPLE.md`](theory/proofs/LOCAL_SUM_CERTIFICATE_COUNTEREXAMPLE.md).

## XVII.3. A range-constrained, positive-margin PRODUCT phase

In the static binary unary-source class above, let the class-1 target table be
`p=(1/2,1/2,3/4,1/4)` on uniform contexts, retain base `(1,1)`, and preregister
the **readout-normalizer cap** `max_(i,j) T_ij<=R`. This is a numerical range
constraint, not a claim about unspecified hardware resources or intermediate
activation bounds.

For SUM-only graphs, the minimum required peak normalizer at sup-norm error
`0<delta<=1/8` is exactly

\[
\boxed{R^*_{SUM}(\delta)=\frac{1-4\delta}{\delta(1+4\delta)}.}
\]

For `1/8<=delta<=1/4` it is `4/(1+4delta)`, and for `delta>=1/4` it is 2.
Exact SUM realization needs unbounded range. These are attained finite-error
bounds; the closure theorem alone does not remove their cost. At `R=4`, the
best SUM sup-norm error is the irrational number `(sqrt(2)-1)/4`.

Every DAG with at most one semantic PRODUCT has output masses
`M_y=1+u_y(i)+v_y(j)+c_y h_ij`, `c_y>=0`. Thus their mixed differences satisfy
`Delta M_0 * Delta M_1>=0`, including arbitrary PRODUCTs of SUM parents. This
proves that exact realization of the stated target with one PRODUCT needs
`R>=16/3`. A native witness attains that bound:

\[
h=(x_0+z_1)(3x_1+\tfrac53z_0),\quad
M_0=1+h,\quad M_1=1+\tfrac13x_1+\tfrac53z_0.
\]

Two PRODUCTs, `M_0=1+2x_1z_1` and `M_1=1+2x_1z_0`, attain Bayes risk already
at `R=4`; no graph can do so below 4. Therefore the minimum PRODUCT count among
Bayes-optimal realizations is 2 for `4<=R<16/3` and 1 for `R>=16/3`. Larger
graphs remain tied: the latter regime does not force every optimum to have
exactly one PRODUCT.

This separation is robust. For `4<=R<16/3`, every at-most-one-PRODUCT model
has sup-norm error at least `(16-3R)/(48+16R)` and excess CE at least half the
square of that number. At `R=4`, the gap is at least `1/1568` nats. Subject to
the two-PRODUCT witness's registered value/build/install reachability, every
epsilon-optimal target with `epsilon<1/1568` must therefore have at least two
PRODUCTs. Full proof, scope, and exact audit:
[`RANGE_CONSTRAINED_PRODUCT_PHASE.md`](theory/proofs/RANGE_CONSTRAINED_PRODUCT_PHASE.md).

## XVII.4. Finite-information structural certificates

An exact conditional table is not free information. In the binary 2x2 static
class, suppose the legal revealed information is a closed probability box
`H=product_i[ell_i,u_i]`. The entire box excludes the SUM prediction closure
iff `max_D u_d<min_O ell_o` or the reversed strict ordering holds, where
`D={00,11}` and `O={01,10}`. Otherwise a SUM-closure hypothesis remains possible
and a positive-margin universal exclusion is unresolved.

For known positive context weights and the first ordering, the exact worst-case
SUM excess over Bayes risk is the least of four weighted Bernoulli pooling
costs at the closest interval endpoints. A rational lower certificate is

\[
\boxed{\min_{d,o}\frac{2w_dw_o}{w_d+w_o}(\ell_o-u_d)^2.}
\]

A declared one-bit mean query can produce the same `1111` transcript for
`(3/4,3/4,3/4,3/4)` and `(5/8,7/8,7/8,5/8)`, although only the first is
SUM-realizable. Repetition and unlimited computation do not resolve this
information class. Under passive full-support Bernoulli sampling, every finite
transcript can likewise occur under both hypotheses: zero-error structural
classification needs unresolved outcomes unless more information is available.

Under an explicitly registered iid context/label law, a statistical alternative
is valid. Preregister `alpha_(i,n)=alpha/[4 n(n+1)]`; simultaneous Bernoulli
confidence intervals at every context count give coverage for all times at
least `1-alpha`. Their radii and interval comparisons can be implemented with
conservative exact dyadic arithmetic. Adaptive stopping then adds no unallocated
error. This is discovery/structural evidence, not fresh candidate persistence,
and the law does not transfer to an arbitrary deterministic corpus.

The finite-range two-PRODUCT witness also has an information-robust comparison.
At `R=4`, if the complete confidence box lies within radius `r<=1/28` of
`p^0=(1/2,1/2,3/4,1/4)`, every at-most-one-PRODUCT model loses to the fixed
two-PRODUCT witness by at least

\[
\boxed{G(r)=\tfrac12(1/28-r)^2-\tfrac{16}3r^2.}
\]

For `r=1/224`, this is `115/301056>0`. Witness reachability, actual physical
feasibility, fresh persistence, and reference/AMP authorization remain separate.
Proof, exact information counterexample, and passive algorithm audit:
[`PASSIVE_INTERVAL_STRUCTURE.md`](theory/proofs/PASSIVE_INTERVAL_STRUCTURE.md).

## XVII.5. A finite registered value path, and an initialization obstruction

For the range-four target, take 16 retained profile labels, four per context,
with class-1 counts `(2,2,3,1)`. Register zero initialization, full-batch mean-CE
projected gradient descent with step 16, and two independent output SUM slots
on direct source PRODUCTs:

\[
M_0=1+\theta_0x_1z_1,\qquad M_1=1+\theta_1x_1z_0.
\]

Symmetry preserves `theta_0=theta_1=theta` without tying the slots, and gives

\[
\boxed{\theta^{(t+1)}=\theta^{(t)}+
\frac{2-\theta^{(t)}}{(\theta^{(t)}+1)(\theta^{(t)}+2)},\quad\theta^{(0)}=0.}
\]

The trajectory remains in `[0,2)` and obeys the readout cap. An analytic
contraction bound proves that 21 steps beat the whole at-most-one-PRODUCT class;
an exact outward-rounded trajectory certificate proves 13 steps suffice. A
separately registered learner that rounds every commit down to `2^-32` also
passes at step 13, using at most 33 bits per encoded coefficient. This counts
208 profile-observation evaluations and 13 backward/update passes over 16
unique labels, not total arithmetic/build work or fresh persistence evidence.

Conversely the expressive parameterization
`h=(a x_0+b z_1)(c x_1+d z_0)`, `M_0=1+e h`, `M_1=1+u x_1+v z_0`
has the invariant zero face `a=b=c=d=e=0` under the same zero initializer and
gradient update. Its static one-PRODUCT witness is unreachable by that value
path, regardless of the number of updates. This does not exclude other graphs,
nonzero initializers, or separately registered value constructors.

The result closes a scoped constructive-value gap using ordinary task loss;
it does not authorize an unregistered parameter kick or a complete physical
install. Profile/population identification, full resource ownership, fresh
persistence, and actual AMP execution remain separate. Proof and exact/float64
audit: [`REGISTERED_VALUE_REACHABILITY.md`](theory/proofs/REGISTERED_VALUE_REACHABILITY.md).

## XVII.6. Fresh log-loss persistence with a fast conditional power bound

For binary true probabilities and candidate/comparator forecasts in `[1/4,3/4]`,
the elementary inequality `E_p log^2(p_Y/q_Y)<=3 KL(p||q)` implies that fresh
paired log-loss gain has second moment at most `6(D+epsilon)`, where D and
epsilon are the comparator and candidate excess risks relative to Bayes.
The existing preregistered linear e-process `E_n=product(1+Y_t/24)` is valid
under its conditional mean-null, without any Bayes assumption. If, additionally,
`D_t>=Delta>0` and `epsilon_t<=Delta/6` throughout the live identity, its first
threshold-crossing time satisfies

\[
\boxed{P(\tau>n)\le\alpha^{-1}(1-\Delta/96)^n.}
\]

Thus this bounded log-loss alternative needs a sufficient fresh budget of order
`Delta^-1 log[1/(alpha beta)]`, not the generic bounded-mean quadratic rate.
The proof uses a killed reciprocal process and assumes nothing about an
uncertified post-crossing continuation. Discovery/profile information supplies
no factors; lineage, path and alpha ownership remain mandatory.

For an independent iid uniform-context stream with the exact XVII.3 target,
the XVII.5 finite-encoded learner after 32 profile steps and a preregistered
frozen scoring phase satisfies the bias condition. Every cap-four at-most-one-
PRODUCT comparator whose **entire forecast function is chosen before the
fresh context** has `D>=1/1568`, even if that function adapts to earlier events.
At `alpha=beta=1/20`, 1,354,752 events are a conservative theoretical sufficient
budget. Sixteen-term rational log enclosures preserve validity and give a
2,709,504-event sufficient bound for the mathematical lower-score process.
These are not executed event counts, bounded-memory wealth implementations,
complete installation or AMP certificates.

The forecast-timing premise cannot be erased: after seeing the current context,
a controller can select among three zero-PRODUCT constant predictors to match
the target there. This falsifies transferring the static class gap through
context-dependent model selection, not the mean-null e-process theorem. The
controller and its information/computation must themselves belong to complete
Omega; the iid-context power premise is not granted for general causal LM.
Proof and exact audit:
[`LOG_LOSS_PERSISTENCE_COST.md`](theory/proofs/LOG_LOSS_PERSISTENCE_COST.md).

## XVII.7. The exact sub-parity-degree envelope in every dimension

For uniform d-bit parity, d>=2, symmetric label noise `0<=eta<1/2`, unary
indicator sources, base `(1,1)` and one final normalization, consider **all**
native fixed-coefficient programs whose two mass polynomials have multilinear
degree at most d-1. Their exact cross-entropy infimum is

\[
\boxed{L_{<d}^*=H(\eta)+2^{1-d}[\log2-H(\eta)].}
\]

The top parity moment of each mass vanishes, forcing the positive-normalizer-
weighted probability means of the two parity classes to coincide. Some
opposite-parity pair must therefore have reversed probability order, costing
at least `2 log2`; all other contexts cost at least Bayes. Equality is impossible
at finite positive mass. A native spanning-tree hierarchy of N-1 cube-edge
indicators, each of degree d-1, approaches Bayes at all but two root contexts
and attains the bound in the limit. At finite coefficient scale K, prediction
error to that limit is at most `(d+1)/K`; its range and graph costs are explicit.

Exact noisy parity requires nonzero full-degree mass information despite
normalization. In this source contract it therefore needs PRODUCT depth at
least `ceil(log2 d)`. Degree is not PRODUCT count: shared repeated squaring
precludes assuming degree <= count+1. The depth bound is not asserted sharp.

This full sub-degree family is **larger than unary SUM** for d>=3. Its small
gap above Bayes is not the unary-SUM family's small improvement over unigram,
whose complementary exact envelope is now proved in XVII.12. Neither infimum nor the finite
algebraic construction supplies registered value/install or AMP evidence.
Proof and exact audit:
[`PARITY_DEGREE_ENVELOPE.md`](theory/proofs/PARITY_DEGREE_ENVELOPE.md).

## XVII.8. Reduced output degree does not erase positive derivation support

Change noisy d-bit parity only by reversing its preferred label at the adjacent
vertices `00...0,10...0`. Let d>=3, m=d-1 and odds r>1. Under the same static
unary-source, positive-base `(1,1)`, final-normalization contract, the minimum
peak normalizer for Bayes prediction is exactly

\[
\boxed{
R_{all}=r+1,\quad
R_{degree}=(r+1)(2^m-1),\quad
R_{support}=\frac{r+1}{r}[(r+1)^m-1].}
\]

These refer respectively to all native programs, all programs with reduced
output mass degree <d, and all programs whose nonzero positive derivations
fix <d distinct input coordinates. The last class is the complete positive
cube-edge cone, not an architecture menu. All optima have finite native mass
witnesses. A symmetry argument valid for this static linear feasibility
problem gives a sharp recurrence lower bound for the whole edge cone.

For d=3,r=3 the three ranges are **4,12,20**. At range 12 a degree-two output
can require full three-input positive derivations: high-order coefficients
cancel only after expanding complementary indicators. Every proper-support
competitor at this cap has sup-norm error at least `1/78` and excess CE at
least `1/24336`, while a reduced-degree native model reaches Bayes. In general,
for `R<R_support`, the proper-support error is at least

\[
\frac{(r-1)(R_{support}-R)}{(r+1)R(R_{support}+2r)}.
\]

Thus collected polynomial degree cannot certify removal of positive provenance
or preservation of its range/resource feasibility. The range ratio between
these two restricted classes grows exponentially with d at fixed r>1.
This strengthens the distinction used in XVII.7; its reduced-degree family
was never a quotient of physical or learner state. Final normalizer range
is still not a hardware budget, and these algebraic witnesses do not grant
registered value/build/install, persistence or AMP authorization.
Proof and exact primal/dual audits:
[`PARITY_PROVENANCE_RANGE.md`](theory/proofs/PARITY_PROVENANCE_RANGE.md).

## XVII.9. Complete static loss brackets for a known positive mass cone

For finitely many known rational nonnegative mass atoms, strictly positive
rational base, independent nonnegative coefficients subject to a declared
rational polyhedral domain, and integer observation counts c of total C>0,
write `P(q)=product q_xy^c_xy` and `L=-log(P)/C`. The entire static coefficient
class admits **finite arbitrary-accuracy global likelihood brackets**:
for any rational gamma>1, an exact-LP algorithm returns an empty-class proof
or a finite rational witness with

\[
\boxed{P_{low}\le\sup P\le P_{high}\le\gamma P_{low},\qquad
L_{witness}-\inf L\le\log(\gamma)/C.}
\]

Bisect probability boxes while retaining the original fixed positive base.
The inequalities `ell_xy T_x<=M_xy<=u_xy T_x` are rational linear constraints
on the actual finite coefficients; no zero-total context is introduced.
Independent bounded-simplex multinomial optima give exact rational likelihood
uppers, with checked KKT conditions. Each feasible box supplies a finite
coefficient witness; each infeasible box requires an exact Farkas alternative.

On the probability cube, `|P(q)-P(q')|<=C ||q-q'||_infinity`. An initial finite
witness has P_0>0, so every feasible box closes once its width is at most
`(gamma-1)P_0/C`. Longest-coordinate bisection therefore terminates with an
exact LP oracle even for unbounded coefficients and an unattained supremum.
This proves finite computability, not a small or polynomial work bound.

The executable solver returns `UNRESOLVED` on missing rational LP evidence or
node-budget exhaustion. Its separate verifier reconstructs tree coverage,
rechecks original constraints and uppers, and binds gamma to the caller's
declared requirement. Generic numerical optimization proposes lower witnesses
only; its search bounds never restrict the global class. Zero-count contexts
retain any shared coefficient/resource constraints.

This is a complete **static known-cone approximation decision class**, not
`CERTIFIED_COMPLETE` for the Reference Compiler. It neither decides arbitrary
exact-optimum equality nor grants unknown dictionary acquisition, optimizer
reachability, physical construction, fresh persistence or AMP authorization.
Proof, executable solver and adversarial tree audit:
[`POSITIVE_CONE_LOSS_SOLVER.md`](theory/proofs/POSITIVE_CONE_LOSS_SOLVER.md).

## XVII.10. Quadratically tight global bounds in normalizer space

When finite normalizer caps follow from the original linear coefficient
domain, retain the common mass variables and write
`C L=sum_x n_x log T_x-sum_xy c_xy log M_xy`. In a normalizer interval [l,u],
the affine chord of log T is a lower bound with error at most
`(u-l)^2/(8l^2)`. Replacing only these concave terms leaves a convex relaxation
over the full original mass cone. Rational lower endpoint logs and rational
tangent lower planes for -log M yield a linear lower `k+g^T w`.

For original/node constraints `Aw<=b`, a proposed rational y<=0 gives a sound
mean-CE lower bound

\[
\boxed{[k+b^T y-\sum_j W_j\max((A^T y)_j-g_j,0)]/C,}
\]

where each W_j is a coefficient bound proved from positive atoms and the node's
normalizer caps. An unbounded zero-mass column must have no positive residual;
its original constraints cannot be deleted. Ignoring residuals is falsified
by an explicit one-context example whose uncorrected "lower" exceeds an
attainable Bayes loss. Exact log enclosures, correction terms and covering
branches are reconstructed by the independent verifier.

On uniform noisy XOR `p=(1/4,3/4,3/4,1/4)`, base `(1,1)`, all unary SUM models
and cap T<=4, the verified tree shrinks from 43,023 probability-box nodes to
87 normalizer-box nodes at a stricter CE tolerance. A 551-node run certifies
`0.68483177<=inf L<=0.68483253`, with actual interval width below 7.52e-7 nats.
These are scoped exact-certificate numerical bounds, not a closed-form optimum
or an equal-factor claim about FLOPs, memory or wall time. A coupled three-label
control and adversarial certificates are also checked.

Convex inner problems admit arbitrarily accurate rational tangent-grid LP
approximations when the grid and log precision are both refined. The fast
numerical proposal path does not claim to implement that completeness oracle:
missing caps/evidence, precision limits and work exhaustion remain UNRESOLVED.
No model-class reduction, registered value path or Runtime/AMP authorization
is inferred. Proof and reference certificate implementation:
[`NORMALIZER_CHORD_CERTIFICATES.md`](theory/proofs/NORMALIZER_CHORD_CERTIFICATES.md).

---

## XVII.11. Exact shared-PRODUCT capacity and a multiclass range phase

For a fixed four-context mass table `M_y>=1`, scalar unary indicators, positive
SUM/PRODUCT and one final normalization, write `E_y=M_y-1` and
`Delta_y=E_y(00)+E_y(11)-E_y(01)-E_y(10)`. Zero differences exactly characterize
SUM-only realization. For one shared PRODUCT the nonzero differences must
have a common sign sigma, but this necessary sign test is **not sufficient**.
Let `(s_0,s_1)` be the two corners of that sign and define

\[
H_i=\min_{y:\Delta_y\ne0}\frac{E_y(s_i)}{|\Delta_y|}.
\]

The complete remaining criterion is `H_0+H_1>=1`. A positive PRODUCT of two
unary SUMs realizes a table supported on these two corners with values a and
1-a; subtracting its shared contribution leaves a nonnegative additive table
in every head. This is an exact rational decision and construction for known
**masses**, not a congruence of complete states or a conditional-table decision
with undeclared normalizers. Among 6,561 small integer two-head tables, 356
pass the sign condition but fail this shared-slack criterion.

For four labels indexed by the contexts, target `p_y(x)=(1+1[x=y])/5` and
base `(1,1,1,1)`, the exact Bayes normalizer cap is 5 without a PRODUCT limit.
The sign relaxation alone has minimum cap 15/2, while the actual one-PRODUCT
class has minimum cap **35/2**, attained by a finite rational native witness.
At cap 5 the minimum is **four PRODUCT nodes**: positivity forces the excess
mass matrix to be identity, while flattening SUM readout paths gives
`E=A+HC` with unary-additive A and `rank(HC)<=number of PRODUCT nodes`.
Unary support cannot contribute to a diagonal entry without leaking off the
diagonal, so A must vanish. A robust version excludes every at-most-three-
PRODUCT model by sup-norm distance at least 1/28 and uniform excess CE at
least 1/1568, allowing arbitrary compound parents and sharing.

For d binary inputs, N=2^d labels, target `(1+1[x=y])/(N+1)` and cap N+1,
the same proof forces at least N PRODUCT nodes. Finite native constructions
give explicit upper counts; sharp counts for d>2 remain open. These counts
refer to scalar semantic arithmetic nodes, not batched physical instructions
or a different vector-output primitive. Range caps, registered value,
information acquisition, build/install and AMP remain distinct obligations.
Proof and exact constructive audit:
[`ONE_PRODUCT_SHARED_SLACK.md`](theory/proofs/ONE_PRODUCT_SHARED_SLACK.md).

---

## XVII.12. The exact unary-SUM parity envelope in every dimension

The earlier multi-input conjecture is now **PROVED**. On uniform d-bit parity,
d>=2, with symmetric noise eta, unary indicators, base `(1,1)`, arbitrary
finite nonnegative SUM graphs and one final normalization,

\[
\boxed{\inf_{SUM}L=\log2-2^{1-d}[\log2-H(\eta)].}
\]

It is unattained finitely for eta<1/2; at eta=1/2 the base attains log2. The
proof covers the full affine mass class, without a symmetry reduction or a
restriction on sharing, depth or width. It starts from a stronger global
invariant: if f is strictly positive affine and 0<=h<=f is affine on the cube,
then `|sum_x chi(x) h(x)/f(x)|<1`. Orient f to have nonnegative slopes and use
the Laplace integral for 1/f; nonnegative affine numerator coefficients and
their necessary offset bound the alternating sum.

Conditioning on other inputs gives the sharp bound `|E[chi_S q]|<=2^(-k)`
for every k-coordinate Fourier coefficient. Normalization can create nonzero
higher-order prediction information even in a SUM-only graph, but its maximum
amplitude decays exponentially with interaction order. Linearly separable
threshold cuts alone do not imply this bound.

Integrating this discrepancy bound along an affine interpolation between two
positive masses proves the log-ratio oscillation inequality

\[
\left|\sum_x\chi(x)\log(M_1(x)/M_0(x))\right|
\le\max_x\log(M_1/M_0)-\min_x\log(M_1/M_0).
\]

The two extreme log odds alone then lower-bound the total log-cosh penalty.
A scalar convex minimization gives the exact noisy-loss formula. A finite
native SUM witness approaches Bayes on two adjacent contexts and uniform on
all others: `M_y=1+K v_(x_1,y)+K^2 sum_(i>=2) x_i`, where v_0 and v_1 are
the two noisy target vectors. Its excess above the infimum is at most 2/K and
its peak normalizer is `2+K+2(d-1)K^2`.

Thus unary SUM's best unigram gain decays exponentially with input dimension,
while its gap to Bayes approaches `log2-H(eta)`. The larger degree-below-d
class in XVII.7 has the complementary small gap above Bayes. A reachable
Bayes-quality competitor would separate from the entire unary-SUM class by
`(1-2^(1-d))[log2-H(eta)]`; static expressivity alone does not supply that
competitor's acquisition, value, fresh persistence or physical installation.
The arbitrary-token baseline extension still holds under block-factorized
hidden-group sampling. Nonuniform context laws and sharp finite-range
envelopes remain separate. Proof and exact/outward-log audit:
[`UNARY_SUM_PARITY_ENVELOPE.md`](theory/proofs/UNARY_SUM_PARITY_ENVELOPE.md).

---

## XVII.13. Finite-range SUM interaction capacity and a sharp resource law

Keep the complete static binary unary-SUM class and base `(1,1)`, with
normalizer cap R>=2. Define `D_d(R)=max |sum_x chi(x)q_1(x)|`, d>=2. With
`m=d-1` and `u=(R-c-t)/m`, its exact value is the two-variable maximum

\[
\boxed{D_d(R)=\max_{2\le c\le R,\;0\le t\le(R-c)/d}
\left[\frac{c-1}{c}\prod_{j=1}^{m}\frac{ju}{c+ju}
-\frac1{c+t}\prod_{j=1}^{m}\frac{ju}{c+t+ju}\right].}
\]

This reduction is proved over the entire mass class. At a fixed denominator,
positive numerator offsets bound all negative slopes and give an attained
linear optimum. A Laplace integral then proves that equalizing every slope
except the smallest improves the objective. Every reduced point has a native
SUM mass witness; this is not an assumed architectural symmetry or a
complete-state congruence. Numerical maximization alone remains uncertified.

Writing `A=(d-1)H_(d-1)` for the harmonic-number factor, every feasible
nonnegative discrepancy obeys

\[
R(1-D)^2\ge4AD,\qquad
\lim_{R\to\infty}\sqrt R[1-D_d(R)]=2\sqrt A.
\]

Thus response at least 1-epsilon needs range at least
`4A(1-epsilon)/epsilon^2`, with a sharp leading constant at fixed dimension.
The exact maximum amplitude of a k-coordinate Fourier coefficient in any
larger cube is D_k(R)/2^k. Small amplitudes still contain information and are
not permission to erase source provenance or future optionality.

For three inputs at cap four, a rational polynomial positivity certificate
proves **D_3(4)=1/40**. The witness is `M_1=1`,
`M_0=1+(2/3)(x_1+x_2+x_3)`. At noise eta=1/4, convexity then gives the
full-SUM CE lower bound
`-(3/4)log(161/320)-(1/4)log(159/320)>0.69004167`.
A native four-PRODUCT construction attains Bayes at the same cap, with a
certified all-SUM comparison gap greater than 0.1277 nats. The discrepancy
maximizer is not asserted CE-optimal, and four is an upper PRODUCT count,
not a proved minimum. These are range-constrained static claims, separate
from registered acquisition/value, physical cost, fresh evidence and AMP.
Proof and exact audit:
[`SUM_PARITY_RANGE_CAPACITY.md`](theory/proofs/SUM_PARITY_RANGE_CAPACITY.md).

---

## XVII.14. Noise changes the range exponent of the optimal SUM loss

In the same uniform d-bit parity class, let L_R be the full unary-SUM minimum
CE under cap R and let `Delta_R=L_R-L_infinity`, with L_infinity from XVII.12.
For fixed d>=2, the resource-rate exponents are

\[
\boxed{\Delta_R=\Theta(R^{-1})\quad\text{for fixed }0<\eta<1/2,
\qquad\Delta_R=\Theta(R^{-1/2})\quad\text{for }\eta=0.}
\]

A direct loss-discrepancy inequality supplies part of the proof. For
`D=|sum chi q_1|`, the affine numerator lemma implies `D<=max q_1-min q_1`.
The convex CE residual above its tangent at one-half is nonnegative; its
values at the two extreme probabilities alone give

\[
L(q)\ge(1-2/N)\log2+\frac2N
\operatorname{CE}(1-\eta,(1+D)/2),\quad N=2^d.
\]

This is also a simpler proof of the unbounded envelope. At zero noise,
combining it with XVII.13 yields a lower excess of
`(2/N)log(1+1/sqrt(1+R/C))`, where `C=(d-1)H_(d-1)`.
A finite native witness balances root error and non-root normalization error,
giving the matching square-root exponent. The lower and upper asymptotic
constants are respectively `2sqrt(C)/N` and `4sqrt(C)/N`; their gap remains open.

At positive noise, affine interpolation and the original log-ratio argument
give the finite contraction
`beta=prod_(j=1)^(d-1) j(R-2)/(d-1+j(R-2))` and the loss lower bound
`log2-(2/N)[log2-H((1-(1-2eta)beta)/2)]`. It exceeds the unbounded envelope
by Omega(1/R) at fixed eta>0. Conversely two root contexts can have exact
Bayes masses at finite total `lambda=1/eta`; adding neutral unary mass at
other contexts then achieves O(1/R) excess. At zero noise this finite root
construction is impossible because the wrong-label base remains positive.

Hence maximizing near-unit parity discrepancy and minimizing task CE have
different range costs. At any fixed positive noise, the direct inequality
even forces CE to diverge when D approaches one. The theorem does not interchange eta->0 with R->infinity,
identify a discrepancy extremizer with a CE optimizer, or grant acquisition,
registered value, physical installation or AMP evidence. Proof and exact audit:
[`SUM_PARITY_LOSS_RANGE_RATES.md`](theory/proofs/SUM_PARITY_LOSS_RANGE_RATES.md).

---

## XVII.15. Exact PRODUCT exclusion does not imply a loss gap at bounded range

There is a three-input counterexample even with a bounded final normalizer.
On unary indicators let `f=x_0 z_0+x_1 w_0` and
`p_1=(1+f)/(2+f)`, with base `(1,1)` and cap T<=3. Exact Bayes realization
needs **two PRODUCTs**, yet the one-PRODUCT class has Bayes loss infimum.

For the exact mass, every nonnegative additive remainder vanishes because
each unary source meets a zero of f. The two PRODUCT parents' zero faces must
be `x=0,z=1` and `x=1,w=1`. Their required positive coefficients overcount
the overlap, so one PRODUCT cannot equal f. Allowing conditional scales does
not evade the obstruction: cap three fixes masses `(1,2)` wherever f=1;
the remaining one-PRODUCT cases either reduce to the impossible mass table
or force total mass at least four on an f=0 context.

Nevertheless, for epsilon>0, the native identity

\[
\epsilon^{-1}(x_0+\epsilon w_0)(x_1+\epsilon z_0)
=f+\epsilon z_0w_0
\]

gives a one-PRODUCT excess `e=(1-epsilon)(f+epsilon z_0w_0)` with T<=3,
probability error `epsilon/[3(3-epsilon)]`, and CE excess <=epsilon^2/16
for epsilon<=1/2. The contradictory term x_0 x_1 vanishes by the declared
partition source contract; the small positive tails remain essential.

At epsilon=2^-k this can use only local coefficients `{1/2,1,2}`, all source
and feature values <=2, and exactly **4k+3 SUMs plus one PRODUCT**. Halving
chains create the tails, doubling recovers their contribution, and a finite
geometric SUM keeps the final cap. Thus even these local bounds do not
replace complete construction length, work, storage and precision resources.
Bounding all graph nodes/slots and compact coefficient domains would restore
compactness of the static prediction class; bounding PRODUCTs alone does not.

The full zero-PRODUCT class is still separated: its exact sup-norm distance
is 1/12 and its CE gap is at least 1/576. The k=3 one-PRODUCT witness beats
every SUM model. No positive gap separates one PRODUCT from two.
An explicitly ordered CPU float64 evaluation at k=54 rounds the excess to f
exactly while exact fractions retain a nonzero error. Floating equality
therefore cannot authorize a real-arithmetic exact structure certificate.
This is not a counterexample to a registered numerical decision class or the
fixed-known-atom cone closure theorem. Proof and exact/float64 audit:
[`ONE_PRODUCT_BORDER_COUNTEREXAMPLE.md`](theory/proofs/ONE_PRODUCT_BORDER_COUNTEREXAMPLE.md).

---

## XVII.16. Complete coefficient closure across source annihilators

For one PRODUCT of positive sums of finite known atoms a_i,b_j on a declared
finite context domain, let G contain exactly the nonzero products a_i b_j.
Missing edges must be proved identically zero on that domain. A **given**
visible coefficient table q_ij>=0 has finite factors q_ij=u_i v_j precisely
when its positive edges admit consistent factors and every visible edge
between active row/column vertices is positive.

Closure has a different complete criterion. Contract the connected components
of the positive edges, including isolated vertices, and orient every visible
zero edge from its row component to its column component. Then

\[
\boxed{q\text{ is in factorization closure iff positive factors are
consistent and this directed graph is acyclic}.}
\]

A cycle gives a multiplicative polynomial contradiction. For an acyclic graph,
integer heights H provide explicit factors `u_i=alpha_i epsilon^H_i`,
`v_j=beta_j epsilon^(-H_j)`: positive edges remain exact while zero edges
vanish with positive powers. Invisible coefficients may diverge. The full
visible factor image is closed **iff each nontrivial connected component of
G is complete bipartite**. An induced three-edge path gives the minimal
obstruction otherwise. The exact audit cross-checks 23,779 coefficient cases
against independent cycle equations and all 512 three-by-three visibility masks.

For full one-PRODUCT mass closure, a separate lift theorem retains additive
coefficients, shared head weights and all alternative visible coefficient
tables. Positivity bounds visible coefficients along convergent mass sequences;
the head weights can be normalized before taking a subsequence. Thus the
closure is exactly the original mass representation with q in the coefficient
closure above. At finite uniform cap R>number of heads, a common contraction
of excess masses returns approximants inside the cap. Conditional closure
still requires existential normalizers and alternative lifts. A rejected
coefficient table alone does not reject an observable mass table.

The executable checker decides given rational coefficient tables only. The
full mass/conditional theorem is a finite semialgebraic characterization,
not an efficient implemented solver or Runtime completeness authority. The
proof also locates this graph criterion within established monomial/toric
factorization theory. No source acquisition, complete-state quotient or
value/install/AMP permission is inferred. Proof and exact certificate audit:
[`MASKED_PRODUCT_CLOSURE.md`](theory/proofs/MASKED_PRODUCT_CLOSURE.md).

---

## XVII.17. Observable PRODUCT closure, a dimension boundary and a robust task

For a scalar excess mass f on the complete d-bit cube with f(0)=f(1)=0,
the full unary-source at-most-one-PRODUCT class has the form A+UV. Its
closure consists exactly of directed-cut masses
`B(q)=sum_(i!=j) q_ij x_i(1-x_j)` with q in the off-diagonal visible rank-one
closure. The proof allows approximants to leak at the zero contexts: positive
same-polarity coefficients vanish in the limit, and a two-by-two product
identity prevents both cross-polarity orientations from surviving.

The observable singleton and complement values fix q's row and column margins.
Every feasible margin polytope has exactly one coefficient-closure member q*.
It is the entropy maximizer on that polytope, a specialization of the known
toric moment-map theorem. Entropy characterizes a coordinate inverse here;
it is not an additional FP loss or regularizer. Thus **full observable closure
is equivalent to B(q*)=f**, and exactness additionally requires the finite-
factor support condition. A checked q* with the wrong observable mass excludes
all alternate lifts.

With three inputs the margins specify every context. Therefore the entire
positive directed-cut cone lies in one-PRODUCT closure. Rational tables admit
a complete exact decision by a one-dimensional transport interval: an interior
monotone cubic root gives finite real factors, while a singleton interval
uses the graph support criterion. The audit has 348 examples where rejecting
the original coefficient table would falsely reject an exactly realizable
mass. Some rational masses require irrational coefficients for their exact
one-PRODUCT representation; real existence is not finite-encoding reachability.

Four inputs already differ. For the sum f of two independent pairwise XOR
indicators, two native PRODUCTs realize f, but

\[
\inf_{A,U,V\ \mathrm{nonnegative\ unary}}\|A+UV-f\|_\infty\ge1/7.
\]

A positive expansion and cross-pair rank-one identity prove this uniform
bound, with no exact-zero assumption on approximants. For uniform contexts,
base (1,1), target `p_1=(1+f)/(2+f)` and final cap four, a separate argument
retaining both heads and all normalizers proves probability error >1/500 and
CE excess at least 1/2000000 for every at-most-one-PRODUCT model. Two PRODUCTs
reach Bayes risk. These constants are conservative, not claimed sharp.

The executable audit completely decides the stated rational three-input
mass class over real coefficients and checks supplied rational margin lifts
in any dimension. General arbitrary-dimensional algebraic search, arbitrary
conditional classes, full resources and value/install/AMP reachability remain
separate. Proof and exact audit:
[`ANTIPODAL_PRODUCT_MASS.md`](theory/proofs/ANTIPODAL_PRODUCT_MASS.md).

---

## XVII.18. Exact support complexity can also increase in a PRODUCT limit

For a scalar excess built from binary unary indicators by positive SUM and
P binary PRODUCT nodes, its zero set is covered by at most 2^P coordinate
faces. Choose one zero parent per PRODUCT globally; each choice leaves an
intersection of source zero faces. Shared occurrences use the same choice.
This gives the sharp exact minimum m for the sum of m independent pairwise
XOR indicators, including arbitrary shared/nested DAGs.

It does not make exact support exclusion a robust approximation certificate.
On four inputs let `f=(1-x)yz+x(1-z)w`. Its positive support is two disjoint
edges. Any two-PRODUCT graph with exactly that support would reduce to a
product of three nonnegative unary sums: no unary or pairwise term fits inside
the support, including the squared first-product term. Its zeros could then
be covered by three coordinate faces, but four explicit zero witnesses need
four different faces. Three PRODUCTs attain f via
`a=(1-x)y`, `b=xw`, `f=(a+1-z)(b+z)`.

Nevertheless two nested PRODUCTs give

\[
\frac{(x+\epsilon^3y)((1-x)+\epsilon^2(1-z))(z+\epsilon w)}{\epsilon^3}
=f+\epsilon(1-x)yw+\epsilon^3y(1-z)w.
\]

Multiplying by 1-epsilon keeps the excess in [0,1] and gives exact sup error
epsilon for 0<epsilon<=1/2. The limiting mass's **support itself** needs three
PRODUCTs; the earlier selector's support did not. For epsilon=2^-k the actual
graph uses two PRODUCTs, 10k+4 SUMs, local alphabet {1/2,1,2} and feature cap
two. At base (1,1), the conditional target `(1+f)/(2+f)` has a two-PRODUCT
Bayes infimum at cap three, with CE excess <=25 epsilon^2/512. Its unrestricted
conditional *exact* minimum is not inferred from the scalar support proof.

With at most S weighted SUM nodes and every nonzero local coefficient >=mu,
0<mu<=1, every positive scalar evaluation is >=mu^(S 2^P). A support-excluded
target with smallest positive mass gamma therefore has mass error at least
min(gamma,mu^(S 2^P)). Repeated squaring explains the exponential sharing
factor. Unlike a PRODUCT-only count, this bound prices SUM construction.

Exact face/identity/DAG audits and a float64 readout-erasure example:
[`TWO_PRODUCT_SUPPORT_BORDER.md`](theory/proofs/TWO_PRODUCT_SUPPORT_BORDER.md).
No state quotient, finite-machine completeness or value/install/AMP permission
is inferred from this static result.

---

# XVIII. Reference Compiler contract

A complete Reference Compiler implementation must obey all of the following.

1. **Immutable claim contract.** Source/type/causality rules, data roles, legal query interfaces/precision/ranges, fixed/searchable lineage coordinates, optimizer/update-unit/logical clock, initializer/profile semantics, machine/resource roles, reference/AMP arithmetic, stream law and proof/bridge implementations are preregistered.
2. **Single complete execution surface.** Every claim-relevant mutable object is owned by the runtime and reflected in \(\Omega\); helper modules cannot create a second hidden Compiler state.
3. **Native program construction only.** Program skeletons arise from source/SUM/PRODUCT/delayed binding. Structure contains zero-valued/registerable slots; a caller cannot smuggle trained constants in as structure.
4. **Registered value construction.** Candidate numerical state is produced only by the declared initializer/profile/optimizer/transport path.
5. **Registered physical realization.** A deterministic/certified machine model maps semantic program to physical objects/cost; a caller cannot submit an arbitrary cheap object list.
6. **Proof-carrying search.** Exact completion is always scoped to an explicit decision class. Caller-supplied raw upper functions or booleans cannot authorize pruning/completion.
7. **Registered finite-precision information.** Query outputs obey declared dimension, range and finite precision; failed queries still consume their real work/information provenance.
8. **Real ownership/resources.** Sharing/refcount/current/peak/cumulative resources are part of complete state; build-before-free and install-copy work are explicit.
9. **Fresh paired persistence.** Candidate/base/path/trajectory identities are continuous; proposal data cannot reappear as fresh evidence.
10. **Authority-bound commit evidence.** Build, safety, bridge, persistence and equivalence authorizations are bound to exact current states/provenance; bare dataclass flags/booleans are insufficient.
11. **Four trajectories.** Deployed-ref, deployed-AMP, candidate-ref and candidate-AMP execute the same exogenous scored events under their registered path-specific learners.
12. **Prediction visibility.** Target-derived within-unit accumulators cannot affect prediction before the registered optimizer commit.
13. **Atomic install.** Installed state is the certified state (or a separately certified transport), at the same cursor, with full Compiler meta-state/resource/error transition.
14. **Honest status.** Unsupported searchable coordinates, insufficient work, non-identifying queries, loose uppers, numerical overlap or missing evidence yield `UNRESOLVED`/rejection as appropriate—not semantic shortcuts.

The historical v155 gate catalog has **47 gates numbered 0–46**. Foundation R4 groups/reframes them but does not delete them. Implementation closure must account for every gate by runtime invariant, exact/randomized model check or scoped theorem audit.

---

# XIX. Proved, not proved, and frozen research rule

## Proved/scoped

Within assumptions stated above:

- native positive SUM/PRODUCT semantics and R5 responsibility are exact;
- categorical residual/predictive packing gives exact/approximate state-information bounds;
- arbitrary finite categorical dynamics have a compact bit-coded positive recurrent realization;
- one-shot linear positive-mixture rank and degree-limited polynomial capacity are characterized in their stated interfaces;
- fixed-generator predictive dimension is a restricted invariant-cone notion;
- general recurrent FP can have tiny internal coordinate dimension with exponentially large finite-horizon behavior span;
- finite-context positive universality/density holds relative to the complete declared source basis;
- positive finite features converge to the scoped dense exponential-attention limit;
- claim-relative congruence/simulation determines safe exact/directional state reduction;
- typed-frontier exact solve and point-query lower bounds hold under their stated factor/information models;
- low-rank and positive-PRODUCT acquisition theorems hold only under their declared legal query interfaces;
- fixed-cost physical materialization is a discrete problem even when semantic support allocation is continuous;
- finite exact compilation can be certified only relative to explicit decision/comparison/resource contracts;
- fresh lineage-specific persistence is valid under its explicit probabilistic/filtration/boundedness/error-ledger contract.

## Not claimed

FP does not claim:

- universal polynomial-time exact compilation;
- that local GN/HVP/first-order closure is a global exact uselessness theorem;
- that nonnegative/predictive rank lower-bounds unrestricted recurrent FP state coordinates;
- that arbitrary finite-amplitude interventions are available in passive language modeling;
- that semantic equality implies physical/runtime equivalence;
- that final-state feasibility implies install reachability;
- that larger budget makes optimal structure monotone;
- that a fixed candidate/action menu is complete;
- that finite-prefix forcing predicts an arbitrary nonstationary future;
- that a no-crossing finite persistence run is structural rejection;
- that Foundation-R4 **implementation** is already frozen.

## Current science frontier

The immediate authorized work is **Reference Compiler implementation closure**. New model/GPU science remains HOLD. After the complete reference runtime passes all required gates and the target AMP bridge passes, the main science questions are whether task/resource optimization forces useful FP structure in real next-token modeling and whether a native FP block can scale competitively from scratch.

## Frozen research rule

The theory is reopened only if a counterexample distinguishes the object declared here from the object a faithful implementation must optimize/execute. If the counterexample attacks only a solver acceleration, acquisition policy or computational shortcut, weaken that component and keep the semantic foundation fixed.

Prefer removing artificial mechanisms and exposing a smaller native invariant over adding another hand-written controller action.
