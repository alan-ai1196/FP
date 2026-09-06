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
