# Reference Compiler recovery manifest

During the 2026-09-05 implementation session, the workspace contained these modules:

```text
__init__.py
anti_unigram.py
bridge.py
build.py
candidate_factory.py
compiler.py
core.py
data_store.py
data_usage.py
equivalence.py
info.py
learner.py
lineage.py
machine.py
native_search.py
persistence.py
program.py
proof.py
resources.py
runtime.py
search.py
semantics.py
```

Recorded late-session approximate file sizes included:

- `core.py` 16,616 B
- `resources.py` 8,667 B
- `semantics.py` 8,985 B
- `runtime.py` 17,775 B
- `compiler.py` 18,460 B
- `persistence.py` 13,720 B
- `candidate_factory.py` 8,845 B
- `learner.py` 8,547 B
- `bridge.py` 7,986 B
- `build.py` 9,187 B
- `search.py` 6,448 B
- `program.py` 6,958 B
- `machine.py` 4,490 B
- `equivalence.py` 3,594 B
- `native_search.py` 3,542 B
- `info.py` 3,597 B
- `proof.py` 3,826 B
- `data_store.py` 2,712 B
- `lineage.py` 1,998 B
- `data_usage.py` 1,956 B
- `anti_unigram.py` 1,608 B
- `__init__.py` 516 B

The directly persisted late-WIP files currently restored here are:

`runtime.py`, `proof.py`, `compiler.py`, `build.py`, `learner.py`, `bridge.py`, `info.py`, `persistence.py`.

Important later-session design changes recorded in execution provenance, even where final bytes were not separately persisted:

- `ExplicitFiniteDecisionClass` scopes completeness;
- `ProgramAuthority` verifies zero-valued native program skeletons;
- `CandidateStateFactory` owns registered reset/profile state construction;
- `ReferenceMachineModel` deterministically maps semantic program to physical objects/cost;
- `lineage.py` validates fixed/searchable coordinates `G,e,sigma,U,S_causal,initializer,profile`;
- candidate build records bind exact physical object IDs;
- Runtime program registry and state/machine/authority snapshots are part of complete Compiler meta-state;
- complete Runtime was intentionally restricted to graph-only `G` search until other coordinate constructors were explicitly implemented;
- compiler-resident shadows require explicit deployment copy/install work;
- paired persistence uses four trajectories and pair-atomic epoch finalization;
- resource-only bypass uses finite-system exact bisimulation authority, not a bool.

An intermediate state passed 24/24 unit tests and 47/47 gates. Later hardening invalidated the right to treat those numbers as a freeze certificate. Reconstruct and re-run from the complete endpoint before updating this status.
