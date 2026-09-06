# FP Open Problems

Only genuinely unresolved problems belong here. Historical problems that were solved or falsified are documented elsewhere.

## 1. Close the complete Reference Compiler runtime

**Exact statement.** Implement one complete execution surface that instantiates `FP_THEORY.md` without allowing a caller to bypass claim state, information, value reachability, physical ownership/resources, numerical enclosures, persistence or bridge provenance.

**Why it matters.** The frozen foundation is only useful scientifically if the actual Compiler optimizes the same object. Most historical FP failures came from a correct local theorem being embedded in a smaller/different executable system.

**Known.** An intermediate 2026-09-05 reference implementation had a full module set and passed 24/24 unit tests plus 47/47 gate registry. Subsequent adversarial hardening changed the complete Runtime contract. The final endpoint integration was not re-frozen before persistence moved to GitHub. Historical R4.2/R3 implementations are complete but theoretically superseded.

**Already-failed methods.** Bare certificate booleans, caller-supplied exact uppers, arbitrary query callbacks, caller-built candidate states/object lists, resource totals without ownership, e-wealth reuse across lineages, state/cursor mismatch, partial ref↔AMP bridging, and helper-level tests that do not traverse the complete Runtime.

**Sufficient falsification of the current foundation.** A minimal program that is legal under `FP_THEORY.md` but cannot be represented/considered by any implementation conforming to the Reference Compiler contract **unless a new semantic model primitive is added**. Slow search or `UNRESOLVED` does not falsify the foundation.

## 2. Prove/test implementation-level completeness of native candidate construction for each declared decision class

**Exact statement.** For every `CERTIFIED_COMPLETE` decision, the implementation must expose the explicit finite/effective candidate class and prove that its native construction/search representation covers that class; completeness must never escape the declared class.

**Why it matters.** R4.2 was formally sophisticated but economically searched only a tiny atomic family. The same mistake must not recur behind a new API.

**Known.** The theory supplies grammar-recursive construction and honest branch-and-bound semantics. General unrestricted compact search may be exponential/hard.

**Attack surface.** Random small-grammar exhaustive oracle comparison, repeated SUM/shared ancestors, compound PRODUCT descendants with useless parents, recurrent delayed state, tied value slots, direct-vs-factorized physical realizations.

## 3. End-to-end reference↔AMP self-Compiler bridge

**Exact statement.** After reference implementation closure, demonstrate that the actual target mixed-precision learner/Compiler path satisfies the registered event-level relation for deployed and candidate trajectories, including structural boundary/install.

**Why it matters.** Float64 rescoring of an AMP-generated endpoint is not the theorem. The physical path itself must instantiate the reference state transition relation.

**Known.** The theory and historical gates define the obligation. Historical R5/R4 physical kernels showed why a numerically uncertified optimization path cannot be counted as an available FP realization.

**Blocked by.** Problem 1.

## 4. Real next-token structural emergence under the frozen graph-only claim

**Exact statement.** Once the Compiler is certified, test whether ordinary next-token loss plus declared hard deployment resources causes the exact/epsilon-optimal target-program set to force useful semantic structure (e.g. sharing/PRODUCT/provenance distinctions) when all non-graph coordinates are matched.

**Why it matters.** This is one of FP's core science questions: does useful graph/block structure emerge rather than being supplied?

**Known.** Trial 1C falsified raw-width-as-solution; historical native blocks remained behind strong dense/GRU-style baselines; R4.2 failed to instantiate the grammar. Foundation R4 now gives a falsifiable definition of “forced structure.”

**Do not run yet.** Problems 1–3 must close first.

## 5. Native FP block scaling from scratch

**Exact statement.** Determine whether a native FP block, without hidden non-FP architectural shortcuts, can train from scratch on ordinary next-token modeling and approach strong modern baselines under matched parameters/compute/resources.

**Why it matters.** Expressivity alone is insufficient; FP needs a competitive reachable learner.

**Known failed direction.** Increasing raw K within coarse cells did not close the gap. Symmetric duplicated alternatives collapse. Do not add activation-repulsion just to separate them.

**Promising attack surface after Compiler closure.** Let resource-bounded positive program structure/provenance distinctions compete endogenously; use response/operator acquisition only as legal proposal/certificate machinery.

## 6. Practical acquisition regimes under passive language-model data

**Exact statement.** Characterize when the interaction/provenance structures useful for language modeling can be acquired efficiently under the **actually legal passive/teacher-forced information interface**, without assuming arbitrary counterfactual subset interventions.

**Why it matters.** v162 shows finite-amplitude subset probes can destroy the local derivative wall, but next-token training generally does not grant arbitrary interventions.

**Known.** Low-rank two-sided operator access and low-overlap hidden-hypergraph interfaces have tractable subclasses; arbitrary point-query/frontier and general hidden hypergraph families have hard lower bounds.

**Falsification target.** Exhibit a realistic required FP structure family whose passive legal transcript is non-identifying even with unlimited compute; that would prove the corresponding emergence claim needs a richer declared information contract, not a new architecture primitive.

## 7. Extend the sharp normalized-SUM structural envelope

**Solved base case.** `FP_THEORY.md` XVII.1 gives the complete static weighted
2x2 loss envelope and a one-PRODUCT noisy-XOR witness. Normalization makes the
SUM-only control strictly stronger than unigram. The result extends to arbitrary
unary token coefficients under block-factorized hidden-group sampling.

**Open statement.** Characterize the corresponding envelope for multi-input
passive tasks, non-factorizing sampling, and finite physical coefficient/range
constraints, then connect a strict separation to registered acquisition and
constructive value/build/install paths. An unattained continuous infimum is a
sound optimistic control, not an installable optimizer endpoint.

**Concrete conjecture, not a pruning rule.** For uniform d-bit parity, symmetric
noise eta, unary indicator sources, arbitrary fixed nonnegative SUM coefficients,
base `(1,1)` and one final normalization, float64 searches for d=3--5 suggest
`inf L=log2-2^(1-d)[log2-H(eta)]`. Only d=2 is proved. Audit details and the
unrestricted-normalization baseline are in `theory/proofs/NORMALIZED_SUM_XOR.md`.
