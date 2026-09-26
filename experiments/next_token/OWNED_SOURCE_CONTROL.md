# Owned causal token sources in the Reference Compiler

Status: **ACTUAL LITERAL RUNTIME CONTROL PASS, 2026-09-26**.
This closes a source-interface mismatch while retaining the existing
ReferenceCompilerRuntime as the only owner. It does not integrate the
full-vocabulary packed reference or token AMP backend and issues no new
complete-class, bridge, persistence or installation certificate.

## The missing-history source is explicit

The native token interface declares V ordinary token atoms and a distinct
PAD atom at every positive lag. Earlier literal numerical audits supplied
these values externally and used zero availability delays in their rule
metadata. The Runtime's existing delayed target atoms correctly give zero
before the file starts, but no existing rule supplies PAD=1 there. Encoding
PAD as target V is illegal because V is outside the prediction alphabet.
Supplying source values as arbitrary exogenous inputs would evade the
intended ownership of the actual token history.

Add one closed causal source evaluator, `target_missing`, with index0 and
strictly positive lag l. At ordinary cursor t it reads1 exactly when t-l<0,
otherwise0. Every ordinary token atom remains1 exactly when the revealed
target at t-l equals its token; before the file it remains0. Consequently,
exactly one of the V+1 declared atoms is1 at each lag. The predicate uses
only the known prefix boundary, never a current or future target.

Literal materialization now declares each source's actual lag as its
availability delay. Registration checks it against the source reader. The
reader remains an explicit typed causal source within the existing FP
interface, not a new graph primitive or semantic architecture action. Its
source read, retained context and ordinary/profile use follow the existing
Runtime resource and data ledgers. Other input/target readers retain their
previous zero-prefix meanings.

Runtime revalidates every passive SourceRead at adoption, including its
closed kind, coordinate and delay. A frozen dataclass is not evidence that
those fields were never forged. Undefined callback kinds and selectable
missing-history coordinates refuse before construction.

## Actual ordinary and profile transitions

The control expands a small native token graph, registers its entire
initializer and learner, and sends **empty exogenous input** through the
Runtime's canonical ingress. Runtime alone reads its retained past targets
and creates the source record. Predictions precede targets; its ordinary
observe/commit transitions preserve every parameter and pending gradient.
Packed object ownership is checked against the actual retained buffers at
each prediction and successor.

For profiled newborns, replay retained observations0 and2 twice after four
ordinary events. Their source positions remain0 and2 while the local learner
clock advances0..3. The replay's final default source position is3 and the
ordinary cursor is4. The next ordinary event must therefore use the real
global prefix, not infer sources from the candidate's replay endpoint.
Every profile before/observe/commit state and subsequent ordinary candidate
state is compared with the independent complete token learner using explicit
original windows. Profile uses remain recorded under their actual IDs.

This demonstrates the source/learner-clock distinction inside the actual
Compiler, rather than accepting caller-made TokenWindows as acquisition
authority. It does not authorize held-out data to train or construct models.

## Evidence and remaining boundary

The [runtime audit](../../scripts/audit_token_runtime_sources.py) and
[792-byte record](../../evidence/minimal/FP_TOKEN_RUNTIME_SOURCES.json) pass:

- All96 four-token words across unit1/2 and mixed/zero-input/zero-core
  initializations:384 observations,288 commits,3,456 owned source-atom
  comparisons and10,752 complete parameter/gradient coordinate pairs.
- Sixteen retained-data profiles:64 original-context profile events and32
  ordinary candidate continuations, with complete states and data uses checked.
- Nine schema, delay, data-role, forged-metadata and caller-ingress refusals.
  Validation cannot be an active learning stream or a profile source.

The existing public Runtime event and profile suites pass, including causal
source rules, failure retention, optimizer clocks, replay accounting and
ordinary continuation. The complete native-token audit also passes after
the literal source-delay correction. Two initial local test-harness mistakes
used nonexistent result/field names; correcting them changes no production
behavior or experimental outcome.

The full-scale target remains the indexed token backend with the same
ordinary/profile state transitions. Its batch endpoint audit alone does not
establish every internal event relation required by FP_THEORY XV. It also
needs the full prediction relation: all masses, their mathematical sum and
the physical normalizer/division, not just the observed target mass. These
are concrete integration obligations, not a reason to narrow the text task,
borrow an older AMP certificate or revisit relation-task variants.
