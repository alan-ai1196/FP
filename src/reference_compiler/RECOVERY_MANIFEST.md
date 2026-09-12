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

The directly preserved readable late-WIP source at recovery commit `39235ef` is:

`bridge.py`, `info.py`, `learner.py`, `proof.py`.

These historical bytes remain in Git. Current `learner.py` and `info.py`
are replacements; current proof/bridge modules expose no signer pending
their complete authority integration. The historical audit loads the exact
old learner/proof/bridge modules in an isolated namespace, without copying
them into a second maintained implementation.

The following larger scratch modules were directly persisted in the session but were not a complete or frozen release and are **not** promoted into canonical source during migration:

- `build.py` — SHA-256 `37097aecc90e24b97286b602879a84fcba41906b58e1db1179195979ae0c01f3`
- `compiler.py` — SHA-256 `77933b57e052d022789fb558e531a289415528b8c8319c848fc9291190f695bc`
- `persistence.py` — SHA-256 `4beee259a52be1d638728a0af74fb780f6b4da10ddf0cc8badc568619e602b4e`
- `runtime.py` — SHA-256 `3a9b6836b1f1124690eaa79ab4016acd5afb01639f3c81ef78d04508a0b3de7c`

Important later-session design changes recorded in execution provenance, even where final bytes were not separately promoted:

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

## Reconstructed current code, 2026-09-12

`program.py`, `semantics.py`, `resources.py`, `machine.py` and `runtime.py`
are now new reconstructions against the canonical theory and ERC-1. They
are not claimed to reproduce the missing historical bytes. The actual
Runtime construction segment executes native typed programs with registered
initial values, full delayed reset, exact range checks and owned packed
reference buffers. The reconstructed `data_usage.py`, `learner.py` and
`info.py` now connect registered exact ordinary continuation to that same
Runtime. Public predictions precede target reveal; only full registered
units commit; query answers are computed and quantized internally. The
public install path remains UNRESOLVED because complete manifest/profile/
search/proof/persistence/physical accounting/AMP integration is absent.
Read `src/reference_compiler/README.md` and the root implementation status
for the exact current scope; the historical green gate counts remain stale.
