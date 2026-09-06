# FP Handoff

This file is written for a capable researcher/model that has **no access to prior chat history**. Treat the repository, especially `FP_THEORY.md`, as authoritative.

## 1. Current research state

The current canonical theory is [`FP_THEORY.md`](FP_THEORY.md). Its status is:

- **Foundation theory frozen.** The state/equivalence/acquisition/construction/physical-realization foundation survived the latest adversarial pass.
- **Reference Compiler implementation not frozen.** The last work was a strict rewrite toward one authority-owned complete `ReferenceCompilerRuntime`. The current persisted/recovered code must be audited before anyone claims implementation closure.
- **Science HOLD.** Do not start new RTX3090/model-science runs yet.

The central foundation principle is:

> **Never erase or assume information before proving that every legal future continuation relevant to the claim cannot use it.**

Its three manifestations are:

- **state:** claim-relative behavioral congruence / simulation;
- **information:** legal claim-separating acquisition transcripts;
- **physics:** reachable history transitions and real ownership/resource accounting, not final-state fantasies.

Computation and statistics then impose honest `UNRESOLVED` outcomes when the registered work/information/evidence contract cannot close a decision.

## 2. Native FP semantics

Do not add another architecture-action vocabulary. The semantic grammar is deliberately small:

1. preregistered typed causal nonnegative sources;
2. positive `SUM`;
3. positive `PRODUCT`;
4. positive normalized readout with a strictly positive causal base;
5. positive delayed recurrent transition programs.

Search refinements such as branch splitting, candidate enumeration or a solver queue are **Compiler search partitions**, not model primitives. Historical labels such as `BIRTH`, `MERGE`, `REWIRE`, `PROBE`, `GROW-R`, etc. must not reappear as canonical semantic controller actions.

## 3. What is actually proved

The most important theorem-level results are consolidated in `FP_THEORY.md`. In particular:

- exact deterministic quotients are valid only under claim-relative transition congruence;
- one-sided dominance is a preorder, not an equivalence quotient;
- approximate similarity uses metrics/covers/error simulation, not non-transitive “epsilon equivalence classes”;
- categorical residual count and predictive packing provide representation-independent state-information lower bounds;
- arbitrary finite categorical dynamics admit compact bit-coded positive recurrent state coordinates, so categorical state count is not a linear vector-width bound;
- one-shot degree-limited positive polynomial capacity is exactly `binom(k+d,d)`;
- fixed-generator positive predictive dimension is a restricted positive-realization invariant-cone notion, not a general recurrent-FP state bound;
- a single positive recurrent scalar can generate exponentially large finite-horizon response span, killing rank-as-general-state lower bounds;
- exact general compilation has unavoidable information/computation barriers: point-query frontier lower bounds, hidden-hypergraph hard families, exact NMF hardness and fixed-charge/knapsack structure;
- finite-amplitude legal probes can defeat local high-order derivative blindness, but **only under the declared query interface**;
- semantic divisible support and physical fixed-cost materialization are different optimization objects;
- physical graph claims require real build/install/state/resource reachability and ownership;
- persistence is fresh, lineage-specific, filtration-aware and path-matched on reference and AMP trajectories;
- the complete self-Compiler boundary is atomic and includes live shadows/jobs/frontier/RNG/resource/error state.

See `CLAIMS_AND_STATUS.md` for status classification.

## 4. What was falsified and must not be reintroduced

Do **not** resurrect these as if they were current FP theory:

- “raw K shortage inside the current coarse support is the main wall” — Trial 1C falsified this explanation;
- current function equality implies learner/compiler equivalence;
- one-step response equality implies recurrent-state equivalence;
- nonnegative rank lower-bounds general recurrent FP coordinate dimension;
- PRODUCT depth alone is a universal acquisition-complexity measure;
- proper-parent first variation can safely prune all PRODUCT descendants;
- unpriced cone/NNLS support is the final physical graph;
- physical realization/cost can be postponed until after semantic optimization;
- local GN/HVP/first-order closure is a global exact uselessness certificate;
- a finite candidate class magically reveals an unknown future expectation;
- `feasible=true`, a high e-value, a bridge bool or a safety bool can be reused as a timeless certificate;
- validation/test labels may drive proposal or persistence;
- exact current task equality permits task-free refactoring when future Compiler optionality changes;
- a solver reaching tolerance means global completion;
- a heuristic architecture choice may replace an unresolved theorem-level region.

The R4.2 historical real-GPU implementation is preserved specifically because it demonstrated that a formally sophisticated Compiler can still instantiate only a tiny partial grammar and remain near unigram.

## 5. Current implementation frontier

Read [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md) before touching code.

Two implementation strata exist:

1. **Historical complete implementations.** R3/R4/R4.1/R4.2 packages were complete runnable releases. R4.2 source is preserved under `experiments/legacy_r4_2_v23/`, but its completeness claim was theoretically superseded by the v24 counterexample.
2. **Current R4 Reference Compiler rewrite.** On 2026-09-05 a stricter reference implementation existed in the research workspace with modules including `core`, `resources`, `semantics`, `search`, `equivalence`, `data_usage`, `program`, `candidate_factory`, `machine`, `lineage`, `runtime`, `compiler`, `build`, `learner`, `bridge`, `info`, `persistence`, `proof`, `native_search`, `anti_unigram`, and `data_store`. An intermediate state passed 24/24 unit tests and a 47/47 gate registry. Subsequent hardening changed the complete Runtime contract; that final integration had **not** been re-frozen when GitHub migration began. Only part of the final scratch tree survived as directly persisted files, so this repository records that boundary explicitly instead of inventing a passing status.

The intended strict construction/commit chain is:

```text
registered native program skeleton
    -> registered initializer/profile produces complete ref+AMP states
    -> registered machine model deterministically realizes physical objects/cost
    -> authority-issued build/safety provenance
    -> four continuous trajectories (dep-ref, dep-AMP, cand-ref, cand-AMP)
    -> fresh paired persistence + event-level bridges
    -> ownership-aware atomic install of complete Omega
```

A caller must not be able to submit a magically pre-trained state, arbitrary cheap object list, arbitrary query callback, bare `upper_fn`, safety bool, bridge bool, or persistence bool and thereby obtain `CERTIFIED`/commit authority.

## 6. Immediate next work

The highest-value next task is **implementation closure**, not new theory and not GPU science:

1. finish/reconstruct the strict complete `ReferenceCompilerRuntime` from the preserved WIP, recovery notes and historical implementations;
2. make one complete execution surface own all claim-relevant mutable state;
3. force query/objective/program/profile/machine/proof/bridge/persistence implementations to be preregistered by the immutable claim contract;
4. restore an executable 47-gate registry against that complete runtime;
5. add end-to-end adversarial tests for forged proof/build/bridge/persistence tokens, cursor divergence, data freshness, ownership/refcount aliasing, build-before-free, stale snapshots, NaN/Inf, quantized query payload, and incomplete decision-class scope;
6. run randomized model checks only after the endpoint path is exercised;
7. only then create an **Implementation Freeze** commit/seal;
8. after the target AMP bridge passes, reconsider RTX3090 science.

If implementation requires a new FP semantic architecture action to become correct, stop implementation and reopen theory. If it only exposes slow search, loose bounds, expensive certificates or insufficient information, improve the solver or return `UNRESOLVED`; do not patch the semantic model.

## 7. Research discipline

1. **Theory first.** If the theoretical loop is not closed, stop expanding experiment implementation.
2. Experiments must instantiate the proved theory rather than approximate a more convenient theory.
3. Theorem/numerical audits use exact arithmetic or float64 reference paths.
4. Real GPU execution uses AMP/mixed precision only after its bridge is proved/audited.
5. Use strong modern baselines; never manufacture a weak baseline to make FP look good.
6. If a native branch collapses, first inspect provenance support, sharing, function-preserving refinement and structural semantics—not activation-repulsion patches.
7. Avoid proliferating named controller actions and special-case `if` mechanisms.
8. Cross-check every concept for necessity; remove redundant concepts rather than protecting them.
9. If theory starts forming a patch wall, retreat to the foundational state/information/physics definitions.
10. It is acceptable to overturn a large previous theory section when a counterexample demands it.
11. Preserve minimal evidence, not caches or raw workspace dumps.
12. Keep FP strictly separate from the independent memory/provenance project.

## 8. Session protocol

At the start of future work:

1. read `FP_THEORY.md`;
2. read this file;
3. read `IMPLEMENTATION_STATUS.md`, `CLAIMS_AND_STATUS.md`, and `OPEN_PROBLEMS.md`;
4. inspect recent Git commits and any active research branch/PR;
5. only then use local scratch reasoning.

At the end of meaningful work, update canonical files/evidence and commit a coherent research change. The repository, not model identity or chat history, is the research state.
