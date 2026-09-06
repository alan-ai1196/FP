# v155 47-gate catalog and Foundation-R4 crosswalk

> Historical gate catalog retained for implementation auditing. The normative obligations are consolidated in `FP_THEORY.md`; this file makes the gate names human-readable.

Gate count: **47**. All mapped in the migration source audit: **True**.

| ID | Gate | Coverage mode | R4 / Reference Compiler mapping |
|---:|---|---|---|
| 0 | source/type/causality/basis | `strengthened_or_reframed_by_R4` | R4:I,X.1,X.2; RC:0,2,13 |
| 1 | residual/cut/causal-memory | `strengthened_or_reframed_by_R4` | R4:II,III; RC:1,3 |
| 2 | parity/noisy-XOR compound | `strengthened_or_reframed_by_R4` | R4:XII,XIII; RC:5,6 |
| 3 | finite-amplitude barrier | `strengthened_or_reframed_by_R4` | R4:XIII,XVII.3; RC:4,5,6 |
| 4 | zero-score curvature | `strengthened_or_reframed_by_R4` | R4:XIII,XVII.3; RC:4,5,6 |
| 5 | incumbent value-cone | `strengthened_or_reframed_by_R4` | R4:II,VII.1; RC:3,4,8 |
| 6 | factor/shared/direct | `retained_v155_runtime_gate_plus_R4_foundation` | v155 gate detail retained; R4:V,XIV; RC:4,8 |
| 7 | decoded-parameter/occurrence lifting | `retained_v155_runtime_gate_plus_R4_foundation` | v155 gate detail retained; R4:V,VII; RC:4,6,8 |
| 8 | reusable SUM | `retained_v155_runtime_gate_plus_R4_foundation` | v155 gate detail retained; R4:X.1,X.9; RC:2,8 |
| 9 | resource history/no refund | `retained_v155_runtime_gate_plus_R4_foundation` | v155 runtime detail retained; R4:XIV,XVII.2; RC:0,1,8,11 |
| 10 | whole reachable positivity/range/context | `retained_v155_runtime_gate_plus_R4_foundation` | v155 runtime detail retained; R4:I,XIV; RC:0,8,10 |
| 11 | birth-state | `retained_v155_runtime_gate_plus_R4_foundation` | v155 runtime detail retained; R4:X.1,XVII.2; RC:2,8 |
| 12 | causal microbatch/logical clock | `retained_v155_runtime_gate_plus_R4_foundation` | v155 runtime detail retained; R4:XV,XVII.2; RC:0,8,10 |
| 13 | structural epoch/continuous shadow/noninterference/atomic context | `retained_v155_runtime_gate_plus_R4_foundation` | v155 runtime detail retained; R4:XV,XVII.2; RC:1,9,11 |
| 14 | bounded evidence/error ledger | `retained_v155_runtime_gate_plus_R4_foundation` | v155 runtime detail retained; R4:XV; RC:9,10,13 |
| 15 | self-compiler equivalence | `strengthened_or_reframed_by_R4` | R4:II,X; RC:1,3,9.1,11 |
| 16 | float64-AMP bridge/enclosures | `retained_v155_runtime_gate_plus_R4_foundation` | v155 event-level bridge retained; R4:XV; RC:9,10,13 |
| 17 | anti-unigram hierarchical | `strengthened_or_reframed_by_R4` | R4:XVIII.1; RC:2,5,7 |
| 18 | claim scope/data role/stream law | `retained_v155_runtime_gate_plus_R4_foundation` | v155 data-role/stream detail retained; R4:XV,XVII.2; RC:0,7,9 |
| 19 | certificate provenance/honest unresolved | `strengthened_or_reframed_by_R4` | R4:XIII,XVII.2,XVII.3; RC:3,4,6,12 |
| 20 | complete self-compiler atomicity | `retained_v155_runtime_gate_plus_R4_foundation` | v155 complete atomicity retained; R4:II,XVII.2; RC:1,11 |
| 21 | resource ledger provenance | `retained_v155_runtime_gate_plus_R4_foundation` | v155 ledger recomposition retained; R4:XIV,XVII.2; RC:0,4,8 |
| 22 | stream cursor/state atomicity | `retained_v155_runtime_gate_plus_R4_foundation` | v155 cursor atomicity retained; R4:II,XVII.2; RC:1,8,11 |
| 23 | constructive reachability/profile | `retained_v155_runtime_gate_plus_R4_foundation` | v155 reachability detail retained; R4:VII.1,X.1; RC:2,4,8 |
| 24 | global filtration predictability | `retained_v155_runtime_gate_plus_R4_foundation` | v155 filtration detail retained; R4:XV; RC:0,6,9 |
| 25 | initializer/profile attribution | `retained_v155_runtime_gate_plus_R4_foundation` | v155 attribution detail retained; R4:X.1,XVII.2; RC:0,2,8 |
| 26 | encoding/lowering attribution | `retained_v155_runtime_gate_plus_R4_foundation` | v155 attribution detail retained; R4:V,XVII.2; RC:0,2,8,10 |
| 27 | positive dense-attention limit | `retained_v155_scoped_semantic_theorem_plus_R4_scope` | v155 scoped dense-positive-limit theorem retained; RC:0,14 |
| 28 | path-matched dual persistence | `retained_v155_runtime_gate_plus_R4_foundation` | v155 same-path persistence retained; R4:XV; RC:9,10 |
| 29 | dual-branch bridge | `retained_v155_runtime_gate_plus_R4_foundation` | v155 dual-branch bridge retained; R4:XV; RC:9,10 |
| 30 | structural-boundary bridge | `retained_v155_runtime_gate_plus_R4_foundation` | v155 structural bridge retained; R4:XV,XVII.3; RC:10,11 |
| 31 | predictive-mixture/general-FP scope | `retained_v155_scoped_semantic_theorem_plus_R4_scope` | v155 scoped predictive-mixture counterexample retained; R4:IV; RC:14 |
| 32 | predictive-dimension/resource scope | `retained_v155_scoped_semantic_theorem_plus_R4_scope` | v155 scoped resource counterexample retained; R4:IV,V; RC:14 |
| 33 | predictive-dimension turning point | `retained_v155_scoped_semantic_theorem_plus_R4_scope` | v155 turning-point theorem retained; R4:IV,XIII; RC:14 |
| 34 | semantic continuum/reachability | `retained_v155_scoped_semantic_theorem_plus_R4_scope` | v155 semantic-continuum reachability control retained; R4:II,IV; RC:14 |
| 35 | dynamic categorical-positive continuum | `retained_v155_scoped_semantic_theorem_plus_R4_scope` | v155 categorical-positive extension retained; R4:IV; RC:2,8,14 |
| 36 | coordinate-relative categorical/positive | `retained_v155_scoped_semantic_theorem_plus_R4_scope` | v155 coordinate-relative control retained; R4:III,IV; RC:3,14 |
| 37 | future-phase identifiability | `strengthened_or_reframed_by_R4` | R4:VII.1,XV,XVII.1,XVII.7; RC:7,9,14 |
| 38 | deployment-vs-Compiler budget | `strengthened_or_reframed_by_R4` | R4:XIV,XVII.7; RC:0,7,8 |
| 39 | budget-phase scope | `strengthened_or_reframed_by_R4` | R4:XIV,XVII.7; RC:7,8 |
| 40 | predictive-generator validity | `retained_v155_scoped_semantic_theorem_plus_R4_scope` | v155 predictive-generator validity theorem retained; R4:IV; RC:0,14 |
| 41 | predictive-horizon lower bound | `retained_v155_scoped_semantic_theorem_plus_R4_scope` | v155 horizon lower-bound theorem retained; R4:IV; RC:3,14 |
| 42 | shift-closed predictive scope | `retained_v155_scoped_semantic_theorem_plus_R4_scope` | v155 shift-closed scope theorem retained; R4:IV; RC:3,14 |
| 43 | budget-forced structural phase | `strengthened_or_reframed_by_R4` | R4:II,V,XIV,XVII.7; RC:7,8,11 |
| 44 | no-crossing not rejection | `retained_v155_runtime_gate_plus_R4_foundation` | v155 no-crossing rule retained; R4:XV; RC:9,12 |
| 45 | one-shot expressivity hierarchy | `retained_v155_scoped_semantic_theorem_plus_R4_scope` | v155 one-shot hierarchy retained; R4:III,IV,X.10; RC:2,3,14 |
| 46 | degree-limited expressivity | `retained_v155_scoped_semantic_theorem_plus_R4_scope` | v155 degree-limited theorem retained; R4:IV,VII; RC:4,5,14 |
