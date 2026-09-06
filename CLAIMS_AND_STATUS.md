# FP Claims and Status

Status vocabulary:

- **PROVED** — theorem-level under stated assumptions.
- **NUMERICALLY VERIFIED** — exact/float64 audit supports an already specified mathematical claim; not a substitute for proof.
- **EMPIRICAL** — observed experiment/system behavior.
- **CONJECTURE** — precise proposed statement without proof.
- **OPEN** — unresolved question.
- **FALSIFIED** — a counterexample/experiment disproves the stated claim.
- **SUPERSEDED** — historically useful but replaced by a stronger/corrected formulation.

`FP_THEORY.md` is normative. This file is a status index, not a second theory source.

| Claim | Status | Dependencies / scope | Proof or evidence |
|---|---|---|---|
| Native semantic grammar needs only typed causal nonnegative sources, positive SUM/PRODUCT, positive readout, and legal delayed positive recurrence. | **PROVED / CANONICAL DEFINITION** | Declared source/type/causality contract | `FP_THEORY.md` I |
| R5 SUM responsibility `bar u = rho bar y` preserves positive persistent semantics while allowing signed backward task credit. | **PROVED** | Positive SUM/LSE coordinate | `FP_THEORY.md` I; `RESEARCH_HISTORY.md` |
| Exact deterministic claim-preserving compression is governed by claim-relative behavioral congruence; safe quotient maps factor observables/resources/actions/transitions. | **PROVED** | Deterministic exact contract | `FP_THEORY.md` II |
| One-sided simulation/dominance is not an equivalence quotient. | **PROVED** | Directional claim | `FP_THEORY.md` II |
| `d(x,y)<=eps` is not in general transitive and cannot define an exact quotient. | **PROVED** | Approximate behavior | `FP_THEORY.md` II |
| Minimum exact categorical symbol count equals distinct claim-relative behaviors; approximate count is bounded by packing/covering. | **PROVED** | Declared behavioral metric | `FP_THEORY.md` III |
| Across an isolating causal cut, exact finite state requires at least `D_C` distinguishable states and `ceil(log2 D_C)` stored bits. | **PROVED** | Continuation class `C` | `FP_THEORY.md` XIX.1 |
| Arbitrary finite categorical dynamics admit bit-coded positive SUM/PRODUCT recurrence using `2 ceil(log2 D)` positive semantic state coordinates. | **PROVED** | Finite deterministic transition table | `FP_THEORY.md` XIX.2 |
| Linear positive-mixture one-shot generator count equals nonnegative rank. | **PROVED, RESTRICTED** | Linear positive-mixture interface only | `FP_THEORY.md` XIX.3 |
| Degree-limited one-shot positive polynomial response has exact maximal rank `binom(k+d,d)`; PRODUCT depth `b` gives degree <= `2^b`. | **PROVED** | One-shot polynomial interface | `FP_THEORY.md` XIX.3; v156 audit summary |
| Shift-closed fixed-generator positive predictive dimension is an invariant-cone positive-realization notion. | **PROVED, RESTRICTED** | Fixed predictive-law mixture generators | `FP_THEORY.md` XIX.4 |
| Nonnegative/predictive rank lower-bounds general recurrent FP coordinate dimension. | **FALSIFIED** | Counterexamples use one scalar recurrent FP with large/full horizon span | `FP_THEORY.md` XIX.4; v156 evidence |
| One positive recurrent scalar can generate full `2^H` length-H behavior span in a constructive family. | **PROVED; NUMERICALLY VERIFIED** | Stated affine recurrence/native normalization family | `FP_THEORY.md` XIX.4; `evidence/minimal/` v156 recurrent audit |
| With complete finite categorical source basis, finite-context positive SUM/PRODUCT is exact under fixed positive base and `O(1/M)` dense under changing normalized base. | **PROVED** | Complete declared basis | `FP_THEORY.md` XIX.5 |
| Positive feature contracts converge to normalized dense exponential attention for nonnegative/simplex values. | **PROVED, SCOPED LIMIT** | Sequence of declared finite positive-feature contracts | `FP_THEORY.md` XIX.6 |
| Dense-attention limit grants free undeclared continuous/signed leaves. | **FALSIFIED / NON-CLAIM** | — | `FP_THEORY.md` XIX.6 |
| Trial 1C explanation “remaining wall is mainly raw K shortage in coarse cells.” | **FALSIFIED EMPIRICALLY** | Trial 1C fixed budget | `RESEARCH_HISTORY.md`; historical v7+ record |
| Relation-position information materially matters in Trial 1C (`+0.2846545` CE removal diagnostic). | **EMPIRICAL** | One-seed controlled diagnostic, not causal decomposition | `RESEARCH_HISTORY.md` |
| Proper-parent first variation safely controls all PRODUCT descendants. | **FALSIFIED** | parity/XOR counterexample; R4.2 exposed practical failure | `RESEARCH_HISTORY.md`; `FP_THEORY.md` |
| Local low-order jet blindness implies universal exponential PRODUCT acquisition complexity. | **FALSIFIED AS UNIVERSAL CLAIM** | Finite-amplitude subset probes can recover hidden conjunctions when legal | `FP_THEORY.md` acquisition sections |
| Hidden PRODUCT support is always cheaply recoverable. | **FALSIFIED / NON-CLAIM** | Depends on legal query language/overlap; restricted interfaces can be non-identifying | `FP_THEORY.md` acquisition sections |
| Low-rank matrix response with legal two-sided matrix-free probes can be acquired exactly with at most `r` forward + `r` adjoint vector probes in exact arithmetic. | **PROVED; NUMERICALLY VERIFIED** | Exact rank-r matrix; legal Mv/M^T u interface | `FP_THEORY.md`; v161 audit |
| Exact known-factor graph solve is tractable exponential in typed frontier load `Phi`; unrestricted point-query frontier tables require `e^Phi` worst-case queries. | **PROVED** | Declared factorization / point-query model | `FP_THEORY.md` typed-frontier sections; v158 audit |
| Universal exact polynomial-time Compiler exists for unrestricted FP. | **FALSIFIED / IMPOSSIBLE AS GENERAL TARGET** | Point-query lower bound; exact NMF hardness; fixed-charge/knapsack subclasses | `FP_THEORY.md` XVII |
| Continuous positive-measure KKT flow automatically solves fixed-cost physical graph materialization. | **FALSIFIED** | Fixed charges produce discrete selection/knapsack | `FP_THEORY.md` materialization sections; v164 audit |
| Current function equality implies future learner/self-Compiler equivalence. | **FALSIFIED** | Same output at current state but different update/future optionality counterexamples | `FP_THEORY.md` II |
| Standalone final-program feasibility implies install reachability. | **FALSIFIED** | build-before-free/peak-resource counterexample | `FP_THEORY.md` physics/atomicity sections |
| A finite physical decision class is exactly/epsilon decidable under appropriate certified comparison oracles; budget exhaustion returns a sound unresolved gap. | **PROVED** | Explicit finite decision class and certified comparisons | `FP_THEORY.md` XVII/XIX.7 |
| Fresh lineage-specific e-process persistence is anytime-valid under its conditional-mean/boundedness/filtration/error-allocation contract. | **PROVED** | Explicit stochastic/randomization law | `FP_THEORY.md` XIX.9 |
| Wealth from one candidate/base trajectory can authorize a different candidate/base trajectory. | **FALSIFIED** | lineage-contamination counterexample | `FP_THEORY.md` XIX.9 |
| Reference and AMP evidence can use cross-path baseline substitution. | **FALSIFIED / FORBIDDEN** | path-matched dual persistence | `FP_THEORY.md` XIX.10 |
| Foundation R4 requires no extra architecture-semantic action menu to state the exact Reference Compiler problem. | **PROVED AT FOUNDATION LEVEL / IMPLEMENTATION PRESSURE-TESTED** | Does not assert implementation completion | `FP_THEORY.md` XVII–XVIII |
| Foundation R4 implementation is completely frozen/passing. | **OPEN / CURRENTLY FALSE AS STATUS** | Latest strict Runtime integration was not re-frozen after final hardening | `IMPLEMENTATION_STATUS.md` |
| Historical R4.2 Compiler instantiated the full current FP grammar. | **FALSIFIED** | `product_nodes=0`, near-unigram real trace despite high evidence throughput | `experiments/legacy_r4_2_v23/`; `RESEARCH_HISTORY.md` |
| With unary sources, no PRODUCT implies unigram-optimal loss on balanced XOR under native positive normalization. | **FALSIFIED AS AN AUDIT SHORTCUT** | Static SUM masses can use normalization to improve; not a previously stated Foundation R4 theorem | `theory/proofs/NORMALIZED_SUM_XOR.md` |
| A positive binary 2x2 conditional table is representable by arbitrary SUM-only DAGs iff diagonal/off-diagonal probability intervals have intersecting relative interiors. | **PROVED; EXACT AUDIT** | Fixed unary source basis, base `(1,1)`, fixed coefficients, one final normalization; no complete-state quotient | `FP_THEORY.md` XVII.1; `evidence/minimal/FP_NORMALIZED_SUM_XOR_AUDIT.json` |
| The sharp static normalized-SUM log-loss envelope for a weighted 2x2 table is Bayes risk plus the least of four Bernoulli pooling costs when target intervals are disjoint. | **PROVED; EXACT AUDIT** | Infimum over prediction-family closure; arbitrary finite weights and graph size, not free reachable value | `theory/proofs/NORMALIZED_SUM_XOR.md` |
| Balanced noisy-XOR SUM-only loss infimum is `[log 2+H(eta)]/2`, also for arbitrary unary token-specific weights in the block-factorized hidden-group gate. | **PROVED; EXACT/FLOAT64 AUDIT** | Static task; infimum unattained for `eta<1/2`; latent group acquisition remains separate | `FP_THEORY.md` XVII.1 |
| One native PRODUCT suffices for every symmetric noisy-XOR conditional, with a finite integer witness below the entire deterministic-XOR SUM envelope. | **PROVED; EXACT AUDIT** | Source/type contract and positive normalization; forcing additionally requires feasible registered value/build/install reachability | `FP_THEORY.md` XVII.1 |
| Every strictly positive 2x2 conditional table over any finite output alphabet has a finite native realization with at most one shared semantic PRODUCT. | **PROVED; EXACT AUDIT** | Static unary sources, fixed positive base, arbitrary finite nonnegative coefficients and final normalization; not a physical-cost minimum | `theory/proofs/ONE_PRODUCT_CONDITIONAL_TABLE.md` |
| In that class, the exact minimum PRODUCT count is 0 iff the two vector-segment relative interiors intersect, and 1 otherwise. | **PROVED; EXACT AUDIT** | Exact expressivity; touching binary intervals can have zero loss gap despite needing one PRODUCT for exact attainment | `FP_THEORY.md` XVII.1 |
| Coordinatewise probability-interval overlap suffices for a multiclass SUM-only conditional realization. | **FALSIFIED AS AN EXTENSION SHORTCUT** | Four-label rational counterexample has overlapping scalar intervals but separated vector segments | `evidence/minimal/FP_ONE_PRODUCT_TABLE_AUDIT.json` |
| One nonnegative homogeneous mass-cone solution proves normalized-SUM approximation closure even when some context totals vanish. | **FALSIFIED** | 3x3 counterexample hides a noisy-XOR interior; exact sup-norm separation 1/4 | `theory/proofs/NORMALIZED_POSITIVE_CONE_CLOSURE.md` |
| Exact realization and approximation-closure membership for an explicitly known finite rational positive mass cone are decidable by rational LPs; closure needs at most one residual LP per context. | **PROVED; EXACT-CERTIFICATE AUDIT** | Fixed positive base, independent nonnegative coefficients, known atom table; any feasible direction works; not unknown-factor acquisition or full physical Compiler completeness | `FP_THEORY.md` XVII.2 |
| A successful residual-cone certificate yields finite positive-base approximants with an explicit rational O(epsilon) error bound. | **PROVED; EXACT AUDIT** | Coefficient range may grow; registered reachability/resource feasibility are not granted | `theory/proofs/NORMALIZED_POSITIVE_CONE_CLOSURE.md` |
| Native FP block can be trained from scratch on ordinary next-token LM and competitively scale under the canonical self-compilation contract. | **OPEN** | Science blocked until Compiler closure | `OPEN_PROBLEMS.md` |
| Budget/task objective induces nontrivial graph structure spontaneously in realistic language modeling under fixed matched non-graph coordinates. | **OPEN SCIENCE QUESTION** | Foundation theorem defines claim; empirical realization pending | `OPEN_PROBLEMS.md` |
