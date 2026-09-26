# Complete native token learner: exact reference component

Status: **PASSIVE EXACT IMPLEMENTATION AND COMPLETE SMALL-CLASS NATIVE
AUDIT PASS, 2026-09-26**. This supplies the native G/Gamma/U and complete
causal learner for an explicit indexed input layer, arbitrary positive
SUM/PRODUCT core and untied readout. It is not an owned Runtime, physical
bridge, model-quality result or constructor certificate. No text model
topology or experimental initializer has been selected by these audits.

Source: [native_tokens.py](native_tokens.py).
Audit: [audit_native_tokens.py](../../scripts/audit_native_tokens.py).
Minimal evidence: [FP_NATIVE_TOKENS.json](../../evidence/minimal/FP_NATIVE_TOKENS.json).

## Native graph and initializer

Use the complete [causal lag/token source schema](CORPUS_AND_CAUSAL_SOURCES.md)
with V predicted tokens, context L and distinct PAD=V. For a declared width D,
the input layer is the ordinary native SUM family

    e_(lag,k) = sum_{v=0}^V E_(v,k) 1[x_(t-lag)=v].

The E slots are tied across positions, not across tokens or channels. PAD
has its own declared trainable row and occurs at every unavailable pre-file
position. This is an explicit representation choice, not forced structure.
There is no embedding oracle: all L(V+1) sources, LD SUMs, LD(V+1) incoming
edges and (V+1)D parameter slots are declared and point-decodable.

An arbitrary finite acyclic sequence of the existing `Sum`, `Term` and
`Product` nodes follows this prefix. The implementation currently uses one
declared semantic type `f`, compatible SUM and `f*f -> f`. It permits tied
core slots, repeated parents, shared squares, empty SUMs, unused slots and
repeated selected feature nodes. Final features feed the
[complete positive readout](../../theory/proofs/NATIVE_POSITIVE_READOUT.md).
Embedding, core and readout slot blocks are disjoint. Core slots may tie to
each other; readout slots are distinct as required by that refinement.

For J core slots, K selected features and E_core core edges, the complete
native parameter count is

    (V+1)D + J + V K,

and the incoming-edge count is LD(V+1)+E_core+V K. Indexed execution does
not rename these semantic counts as the much smaller physical lookup cost.
`materialize` constructs the literal native graph for small audit cases;
expanding a large graph is a separate computation, not a free diagnostic.

Gamma supplies every integer master on the declared 2^-p grid: per-channel
embedding defaults plus explicit token/channel overrides, every core slot,
and every readout slot through its complete default/override encoding.
An explicit initializer can override every slot. No tokenizer statistics,
language feature, hidden pretrained value or advancing RNG is supplied.
The audit initializers are test fixtures, not a selected language model.

## Source and optimizer transitions

The learner retains its own full L-token context tuple. At cursor zero it
is all PAD. Prediction has no current-target argument and constructs its
source window from this tuple and cursor. Observation first checks the
actual predecessor and complete algebraic cache, then acquires the target
and shifts it into lag1. EOT is a normal token; it never resets context.

This context queue implements the declared external lag/token source
interface. It is not an undeclared neural recurrence or backpropagation
through historical targets. The surrounding Compiler still has to own the
token tape, observations and their history. Retaining only L tokens in the
learner does not authorize erasing older Compiler information or prove that
older text is irrelevant to a different claim.

U is the existing mean-CE projected SGD with one declared learning rate,
update unit and dyadic grid. Every core and embedding parameter receives
its full event-local derivative, every pending gradient is retained, and
all three parameter blocks commit at the same native unit boundary. No
caller chooses separate per-block update clocks. The complete state is:

- all embedding, core and readout parameters;
- all three blocks' pending gradients, including implicit exact zeros;
- the context tuple and actual cursor;
- the update-unit count and optimizer-step count;
- the immutable definition and initializer-derived reachable values.

Prediction caches retain their actual predecessor, complete input/core
values and the readout's complete decodable cache. Past snapshots stay
immutable. Passive dataclass construction remains possible and supplies no
reached-state authority; refinement concerns initialization and valid pure
transitions only.

## Why sparse embedding updates preserve the complete learner

Exactly one token atom is one at each lag, so the entire native input SUM
equals E_(x_(t-lag),k). Let a_(lag,k) be its signed reverse adjoint. Then

    dL/dE_(v,k) = sum_{lag : x_(t-lag)=v} a_(lag,k).

Both identities follow by expanding the declared SUM, not by selecting a
subset of inputs. An absent token has exactly zero event gradient. Repeated
tokens, including repeated PAD, add every occurrence. A zero-valued active
master can have a nonzero gradient and remains trainable.

Over a full update unit, a token absent from every event has exactly zero
pending gradient. Because its old master is already on the commit grid,
the native projected/grid commit leaves it unchanged. Sparse storage may
therefore leave it implicit. A token absent **only from the current event**
can still have a retained earlier gradient and must not be forgotten.

The generic core uses ordinary reverse differentiation, with separate
incidences for both parents of a PRODUCT even when they coincide. Readout
adjoints enter every feature incidence, including repeated selected nodes.
The readout theorem supplies every final slot gradient and its exact commit.
These identities and the shared clocks give an induction on all finite
token streams: decoded parameters, pending gradients, source context,
clocks and native predictions agree after every valid microphase.

This is a complete learner-component refinement. It does not prove a
complete Compiler/resource-state equivalence, supply a legal information
acquisition token, or certify that constructing/retaining it is affordable.

## Concrete failure witnesses and initialization

The audit retains a three-occurrence token example with exact embedding
gradient -4/231. Keeping only the last occurrence gives -1/33, a different
native learner. In another three-event unit, a PAD gradient16/171 survives
two subsequent events where PAD is inactive; its committed master changes
from1/2 to7/16. Updating only the last context's rows would lose that step.

Initialization also constrains learning. If every embedding is zero and
the only feature is a PRODUCT of two embedding values, the feature and all
embedding derivatives are zero. Readout gradients are zero as well. Every
token continuation preserves the initial parameters and base-only output.
This follows by induction and is checked on all32 five-token binary words.
It is the existing dormant-PRODUCT obstruction in this concrete text
representation, not a new Foundation claim. A direct SUM feature at zero
can still learn because its derivative need not vanish.

With equal bases and a label-symmetric readout W_yi=w_i, the exact core
adjoint is Vw_i/Z-w_i/(Z/V)=0. This blocks the first core update. It does
not by itself prove an invariant collapse: nonzero features allow target
updates to break readout symmetry. The audit's next core gradient is
12800/196173. An actual text initializer must state how useful distinctions
and non-dormant PRODUCT paths are provided or acquired. Adding a repulsion
regularizer or calling supplied distinctions learned structure would not
answer that question.

## Evidence and remaining execution boundary

`python -X utf8 -B scripts/audit_native_tokens.py --write` passes:

- 384 complete six-token words across two unit sizes and three initializers,
  with2,304 literal native observations and1,728 commits. All28 parameters,
  all pending gradients, full input/core caches, readout values/probabilities,
  clocks and context queues agree at every relevant phase.
- The repeated-token, retained earlier-gradient, dormant-PRODUCT and
  readout-symmetry witnesses above, plus eleven malformed/stale refusals.
- Eight synthetic token events at V=50,257, L=512, D=4, including EOT and
  token0. All16,384 cached embedding values and complete windows agree with
  the retained source history. The declared G has25,732,096 sources,
  52,306 SUMs, two PRODUCTs,103,129,419 incoming edges and402,063 slots.
  It is **not** literally expanded or independently fully materialized;
  the exhaustive literal comparison belongs to the small class above.

No real text targets, validation loss, Torch, GPU or timing comparison is
used. The large fixture has only a few stored exceptions; worst-case
embedding/readout storage can still be dense. The current pure-Python
implementation copies pending-gradient maps, uses unbounded Fractions and
retains persistent versions. It is a reference component, not a throughput
claim or an owned memory/work implementation.

Reordered exact sums do not establish floating equivalence. Embedding
gradient occurrence order, core pullbacks, readout normalization and grid
boundaries need an explicitly declared numerical lowering and checks. The
next practical boundary is that lowering with actual resource ownership,
followed by the registered text study and fresh strong baselines. This
component does not re-open the completed relation-task branch.

The subsequent [sound enclosure solver](EXACT_COMMITS_WITH_ENCLOSURES.md)
now resolves exact native commits from interval bounds while preserving a
complete exact unit decoder. Its full-vocabulary512-event control closes
one reference-cost obstacle; efficient owned execution and AMP remain.
