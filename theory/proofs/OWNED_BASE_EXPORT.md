# Reusing the owned immutable base fact at public export

Status (2026-10-03): **REACHABLE-STATE REFINEMENT; FOCUSED EXACT CPU PASS**.
Foundation/ERC and the relation/precision branches remain closed. This is a
bounded ordinary-text implementation correction, with no new model action,
cache, certificate class, numerical shortcut or whole-runtime budget claim.

## Selected work law

At Git `5c83725`, a successful single-incumbent native `predict_next` exports
its forecast twice: once from `finish_context`, once from the outer convenience
port. Each export traverses the V-element `origin.definition.output.base`.
One copy memo avoids repeated visits to that tuple *within* an export but is
not shared between the two exports. Each exact Fraction returns unchanged;
the enclosing tuple therefore also returns with its original identity.

For T successful ordinary events using these ports, this component executes
exactly 2TV scalar visits. The original text declaration T=1,048,576, V=50,257
gives **105,396,568,064** visits, even though every event uses the already-owned
immutable base. This is a source-operation count, not a time lower bound or a
claim that these visits dominate execution. Other public ports, extra candidate
forecasts and diagnostics are outside this exact count.

## Lossless refinement

The existing `_TokenBaseFacts` constructor establishes, after payment and
complete independent byte binding, that its strongly retained `source` is an
exact builtin tuple of exact positive Fractions. Both resource roles hold the
artifact. Its dynamic scope is selected from the actual Runtime; equality of
another tuple, public metadata or a caller declaration cannot select the fact.

Under the [existing scalar ownership model](PUBLIC_VALUE_OWNERSHIP.md), every
child is immutable and the tuple has no writable metadata. The literal copy
of this tuple is therefore the identity operation. Replacing that traversal
by its known result preserves the complete recipient value and all aliases.
It skips no mutable node, numerical operation, bit guard or validation: the
public copier never imposed numerical admissibility on these scalar leaves.

`public_values.detached` uses this exact-source fact only for builtin tuples.
It retains the ordinary memo and walks/copies every other supported value.
Captured token values still export complete builtin tuples. Mutable records,
extra metadata, inherited slots, dictionaries and lists still detach. Unknown
types and cycles still refuse. No fact is inferred for an equal foreign tuple.

The public-port guard now runs the export under the same existing owner
selection as the method. A nested disabled Runtime masks an outer fact during
both phases. Scope restoration uses the existing isolated Context mechanism,
including exceptional exits. Private fact mutation, trusted class/code changes
and scalar-internal mutation remain outside the preexisting fault model; this
change does not enlarge that model.

The new outer export context may itself fail to allocate. After an already
published observation, that failure retains the revealed target, cursor, paid
resources and events and enters the existing terminal host state. No cleanup,
rollback or refund is introduced. As with other physical refinements, equal
allocation-failure cursors on different implementations are not promised.

## Exact finite evidence

`scripts/audit_owned_base_export.py` loads the actual historical copier from
Git `5c83725`; both paired arms have identical paid facts and other production
code. The historical copier ignores the additional scope, so this comparison
isolates the walk without disabling the old ownership boundary. A read-only
Python call observer counts visits without substituting any operand or producer.

`evidence/minimal/FP_OWNED_BASE_EXPORT_CPU.json` records:

- 96 complete paired histories: all sixteen four-target binary streams,
  update units one/two, and packed/shared/shared-with-fact storage; 384 training
  and 192 frozen-reporting events per arm, with identical complete result and
  state bytes despite public forecast mutations.
- Exact-source, equal-foreign, passive and other-owner controls; nested disabled
  export masking; complete mutable metadata, internal aliases and refusals.
- Eight allocation failures, before context creation and after binding, at
  contract, snapshot, prediction and post-observation exports. All preserve
  actual paid prefixes and clear dynamic scope without allocating reset.
- Two synthetic targets per arm under the unchanged full million-target text
  declaration. Every buffer and role total agrees; **502,254,394** serialized
  snapshot bytes compare in full. The counted base visits fall from **201,028
  to zero**. No corpus is opened or experiment journal replayed.

## Stopping boundary

Do not extend this into a general immutable cache or another representation
sweep. After the fixed relevant CPU regression and one actual fact-enabled AMP
control, close this refinement and decide the complete ordinary-text budget.
The unchanged `_forward` still performs a full V-by-K integer sum and maximum
for each forecast and each observation-cache recomputation. Complete retained
records, canonical stream execution, old masters, windows, metadata and actual
host limits remain. Removing 2TV Python visits proves neither a 96-GiB fit nor
the two-hour horizon, and supplies no trained score or `CERTIFIED_COMPLETE`.
