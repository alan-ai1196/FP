# Historical Reference Compiler Contract R1 — non-normative snapshot

> **Status:** supporting implementation-design snapshot from 2026-09-04. `FP_THEORY.md` is normative. The 2026-09-05 implementation pressure test strengthened several API/provenance requirements beyond this snapshot; consult `IMPLEMENTATION_STATUS.md` and `src/reference_compiler/RECOVERY_MANIFEST.md`.

---

# FP Reference Compiler Contract R1

**Purpose.** This is the implementation contract derived from `FP_THEORY_FOUNDATION_REWRITE_R4_FREEZE_CANDIDATE_2026-09-04.md` together with the still-operative scoped numerical/persistence obligations of compact canonical v155. It adds **no FP semantic primitive and no architecture-action menu**.

**Science status:** HOLD. Passing this contract in exact/float64 reference mode is a prerequisite to any new real/GPU science; the target AMP path must then pass the registered event-level bridge.

## 0. Immutable claim contract

A compile decision is keyed by an immutable claim/snapshot record `chi` containing at least:

- declared nonnegative causal source schema and its effective indexing/evaluation rule;
- semantic type/causality rules and positive SUM/PRODUCT/readout semantics;
- fixed vs searchable lineage coordinates (`G,e,sigma,U,S_causal,...`) for the claim;
- registered initializer/profile/value-optimizer and score-before-update unit/logical clock;
- data roles (train/online vs reporting validation/test) and, if a probability guarantee is claimed, the stream/randomization law;
- legal Compiler information/query interface;
- target/lifecycle realization resource contract `B_dep`, Compiler exploration contract `B_C`, the declared role/owner of every resource functional, and already-spent resource history; candidate-specific adaptation/build/install cost belongs to `B_dep` whenever the scientific target-resource phase claims the chosen program must pay it;
- reference arithmetic, target AMP arithmetic, and the registered event-level relation/coupling to be certified;
- physical machine transition/install model;
- global statistical/error-ledger policy.

Changing a coordinate on which a certificate depends changes the certificate key. An old certificate becomes stale unless a theorem explicitly transports it.

## 1. Complete runtime object

At each structural boundary the state is the complete self-Compiler configuration

\[
\Omega=(\xi,\iota_{dep},s_{dep},m_C,\kappa),
\]

including the exogenous cursor, deployed complete learner state, every live shadow, queued/in-flight Compiler job and owned buffers, scheduler/RNG state, resource/error ledgers, certificate provenance, and any paid dormant optionality that can change future legal transitions.

No theorem may silently replace `Omega` by current logits, current graph, parameter vector, or deployed learner alone when the omitted fields can affect a future declared claim.

## 2. Only generic native construction

The semantic construction interface contains only:

1. reference a declared causal source/existing legal node/state coordinate;
2. create positive SUM with registered nonnegative parameter slots/aliases;
3. create PRODUCT of type-compatible parents;
4. establish a registered positive-delay state binding after its zero-delay body exists;
5. connect legal evidence to the registered positive readout through the same SUM semantics.

Parameter values are not free structural constants: they arise from the registered initializer/profile/value-optimizer trajectory or another explicitly declared finite encoded value operation. Physical allocation/copy/free/fusion/lowering/install are machine transitions, not new FP semantic operations. A physical backend transition may realize/lower a previously constructed semantic DAG or change an explicitly searchable physical encoding/lowering coordinate, but it may not smuggle in an undeclared semantic computation or create a new learned source/function outside the native grammar.

Any finite legal target skeleton is covered by topological application of these constructors. A target is nevertheless executable only if its **numerical complete state and full build/install trace** are machine-reachable under the registered resources.

## 3. Claim-safe state reduction

### 3.1 Exact merge

Two partial or complete states may be merged only under a certified exact deterministic claim-relative congruence

\[
\equiv^0_{\mathfrak C}
\]

(or a separately proved probabilistic/pathwise bisimulation for the declared stochastic contract). Exact congruence must preserve required observations/resources, legal-action availability, and successor relation under all legal future continuations.

### 3.2 One-sided pruning/replacement

A simulation/dominance relation is directional. It may justify only the proved direction of pruning/replacement. It is not an equivalence class unless both directions plus congruence are proved.

### 3.3 Approximation

Approximate compression uses an error-carrying abstraction/behavioral metric with a compositional certificate. A threshold `d<=epsilon` is not treated as an equivalence relation.

If exact class identity is unknown, keep regions separate or return `UNRESOLVED`.

## 4. Search regions and certificates

Every live search region `R` stores, under its current snapshot key:

- a reachable feasible lower witness when one is known;
- a sound upper enclosure `U_R` on the **declared trajectory task objective** over every still-possibly-feasible candidate in `R`;
- typed resource lower/upper/enclosure information with guarantee type;
- numerical/range certificate state;
- exact/approx/simulation status of any quotient/signature used;
- provenance of every query/probe/result used to construct the certificate.

The task objective is a functional of the registered trajectory/history when the claim observes cumulative prediction/adaptation cost. Endpoint value is used only when the claim explicitly declares a terminal objective after a charged adaptation prefix.

A normalized-positive NLL branch always has a coarse finite task range when the registered positive-base/activation envelope is finite. Lack of a tight structural bound therefore causes retained search / `UNRESOLVED`, never an invented prune.

## 5. Information is explicit and charged

JVP/VJP/HVP, finite-amplitude interventions, group tests, replay, counterexamples and physical measurements are legal only if they are in the registered information interface. Their observation dimension, precision, work, memory and any perturbation/state costs are charged.

An acquisition procedure is exact only when its transcript separates every pair of hypotheses that are noncongruent for the declared claim. Stable finite-precision decisions additionally require a certified separation/enclosure margin.

A theorem that works with arbitrary subset probes does not authorize those probes in a contract that exposes only local gradients, prefixes or passive stream observations.

## 6. Lazy exact proposal search

A reference exact solver repeats:

1. choose a live region using a nonanticipating registered Compiler policy;
2. refine/expand it only via generic native constructors, legal information queries, certified physical/value-profile transitions, or exact region partitioning;
3. merge exact-equivalent states only under Section 3.1;
4. update feasible lower witnesses and sound uppers under the current snapshot;
5. prune only when a sound exact-objective/resource certificate proves the region cannot beat the incumbent;
6. keep unresolved hard-feasibility boundaries in the upper envelope.

The policy may be heuristic. **Solver optimality is not part of FP semantics.** Exhausting `B_C` while a live region can still beat the incumbent returns `UNRESOLVED`.

With unlimited Compiler work, exact/effectively finite quotient (or equivalent finite physical class), decidable/certified feasibility and task comparison, and complete region refinement, zero-gap proposal selection is exact for the declared finite-prefix target class. None of this proves unknown-future superiority.

## 7. Target-program forced structure versus solver selection

For the declared target/deployment contract define the complete machine-reachable target set independently of which candidates a finite-work solver happens to visit. Let `O_B` be the exact optimum set of the registered finite-prefix/horizon trajectory objective.

A structural property `P` is task-resource forced only when:

- `O_B` is nonempty;
- `P` is invariant to declared nuisance renamings/equivalences;
- the claim predeclares whether `P` is semantic-graph/provenance structure or physical-realization structure; fused lowering cannot erase semantic structure and lowering-only opcodes cannot manufacture it;
- **every** exact optimum in `O_B` has `P`.

If a `not P` exact optimum remains possible, `P` is not forced. A finite-work Compiler that happens to select `P` may report only policy selection unless it has closed the target-class gap.

Changing only Compiler exploration budget is a Compiler-work effect, not automatically a target-model resource phase. If a required build/install debit is classified under Compiler budget and that cap changes feasibility, the resulting transition is explicitly a self-Compiler resource phase. Under componentwise relaxation of fixed target/lifecycle resource caps with the search contract held fixed, feasible target sets and optimal task value are monotone, but the identity/property of optimal structure need not be monotone.

## 8. Candidate build and value continuation

A proposal becomes a physical candidate only through a legal history trace that accounts for:

- peak/current/cumulative resources with no refund of already-spent work;
- candidate plus incumbent/shadow coexistence during build;
- reusable SUM/shared ancestors and true tied parameters in feasible lower witnesses;
- initializer/replay/transport for every new optimizer/recurrent/causal field;
- the registered value-adaptation/profile trajectory on the same logical data prefix;
- whole-reachable-state positivity/range safety;
- actual install/state-copy/serialization/quantization path.

Standalone final feasibility does not imply build/install reachability. A pointer-swap/atomic-replace shortcut is legal only when the machine contract actually provides and certifies it.

## 9. Fresh persistence protocol

Proposal/discovery/profile data and persistence data have distinct causal roles. A candidate proposed using an epoch cannot backfill that epoch as persistence evidence.
The retained persistence theorem is scoped to teacher-forced / branch-invariant exogenous observation streams (or another explicitly proved randomized sampling design). If deployed/candidate actions change future observations, a separate environment/counterfactual theorem is required; this contract does not reuse the fixed-token e-process there.

Each persistence identity binds:

- immutable claim key;
- fixed deployed comparator lineage;
- fixed candidate lineage;
- one continuous candidate and comparator complete-state trajectory;
- initializer/transport provenance;
- predictable epoch schedule and bounded statistic;
- explicit predictable error allocation.

Reference and AMP each use their **same-path** deployed comparator and candidate gain. Wealth never transfers to a new candidate/base/reinitialized trajectory merely because a policy-level process was previously large.

No-crossing within finite time is not a structural rejection unless a separately valid negative test exists.

### 9.1 Exact resource-only bypass

Fresh task persistence may be bypassed only for a refactor covered by a **strong enough exact complete self-Compiler equivalence/simulation theorem** for the declared claim: the installed learner behavior/transition trace is preserved, the complete Compiler meta-state (live shadows/jobs/queues/RNG/ownership/optionality) has a certified mapping, and relevant hard-resource feasibility is no worse. Current-function equality, semantic gauge equality, ordinary learner bisimulation or a cheaper static graph is insufficient. If this theorem is unavailable, the refactor is an ordinary candidate and Section 9 applies.

## 10. Causal event order and numerical bridge

Every branch reproduces the registered ordinary learner's event order:

`predict -> score -> reveal/causal-state advance -> ... -> registered optimizer commit`.

No target affects its own prediction and no optimizer effect leaks earlier than the declared update-unit boundary. All compared branches use the same exogenous cursor/token/update-unit clock for the graph-emergence claim.

Reference and AMP are related by a registered event-level inductive relation (or explicit probabilistic coupling for declared nondeterminism) for **both deployed and candidate trajectories**, from actual initialization through every prediction-visible event and optimizer commit. Decision-critical inequalities use exact arithmetic or non-overlapping sound enclosures.

## 11. Atomic structural boundary

An install is one complete self-Compiler transition at the same exogenous cursor. It simultaneously:

- installs the certified target learner/state;
- applies certified state transport;
- rebases/stales/cancels/retains live shadows and jobs according to the registered transition;
- transfers/releases actual owned resources, not merely ledger labels;
- updates resource and statistical/error ledgers;
- updates scheduler/frontier/RNG/meta-state.

A graph install followed by an uncertified compaction/fusion/quantization/state reset is a second structural edit and is illegal under the first candidate's certificate.

## 12. Honest statuses

A compile/deployment decision returns exactly one of:

- `CERTIFIED_COMPLETE` (or explicitly `EPSILON_COMPLETE`) for the declared finite decision class, with all required numerical/resource/install/persistence obligations satisfied;
- `UNRESOLVED`, when any still-relevant region/feasibility/statistical/numerical gap remains after available work;
- `REJECTED_INFEASIBLE`, only with a sound deterministic/resource/admissibility certificate or a separately declared valid negative statistical claim.

A local optimizer tolerance, failed heuristic proposal, persistence no-crossing, stale certificate, or exhausted Compiler budget is never silently converted into global rejection/completeness.

## 13. Required implementation invariants

The implementation must make the following mechanically inspectable:

- every model node was created by source/SUM/PRODUCT/delay binding under the fixed type system;
- every structural state carries lineage and snapshot provenance;
- every merge/prune records the theorem/certificate kind that justified it;
- every query records its legal-interface identity, input snapshot, precision/dimension and resource debit;
- every lower witness is executable and every upper covers unresolved feasibility;
- every shadow has isolated complete semantic state;
- every persistence identity has immutable lineage/base/error-allocation provenance;
- every install preserves cursor and linearizes the whole self-Compiler configuration;
- every reference/AMP decision has the corresponding bridge/enclosure evidence;
- `UNRESOLVED` is a normal first-class outcome.

## 14. What this contract deliberately does not contain

There is no primitive `split`, `merge`, `rewire`, `birth type`, `grow rank`, `attention`, `state-space`, `dense fallback`, `probe more`, or other architecture action. Historical implementations may use such words as UI/debug descriptions of generic candidate differences, but they do not define the model or completeness theorem.

There is also no claim that exact compilation is polynomial, that future useful structure is always identifiable, that a finite semantic witness is physically reachable, or that increasing a budget makes structure monotone.

## 15. Freeze implication

If a Reference Compiler can implement Sections 0--13 and pass the retained v155 reference gates without adding a new semantic constructor/action, then R4's foundation passes the intended closure pressure test: remaining failures are solver, information-interface, resource/machine, numerical or statistical failures and must yield a weaker certificate or `UNRESOLVED`, not a new architecture mechanism.
