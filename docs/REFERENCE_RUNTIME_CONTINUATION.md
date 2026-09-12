# Owned reference continuation — implementation scope, 2026-09-12

`FP_THEORY.md` is normative. Foundation and ERC-1 remain frozen. This note
describes the current executable Runtime segment; it is not a new semantic
contract or a complete Reference Compiler/AMP release.

## What the endpoint now executes

`ReferenceCompilerRuntime(construction, initial_program, online=...)` binds
an immutable `OnlineContract` to its construction contract and identity.
The added declaration fixes the ordinary learner, data identities/roles,
source evaluation rules and query implementations. No numerical learner
state, query answer, callback, event commit flag or resource role can be
supplied through these public continuation methods:

| Endpoint | Owned behavior |
|---|---|
| `predict_next(observation_id, inputs)` | Consumes the next registered pre-target context, seals the active lineage set, reads only available causal sources, and executes every active reference prediction |
| `observe(target)` | Records the target once, accumulates exact CE derivatives, advances positive delayed bodies, and commits only at the full registered update-unit boundary |
| `query(query_id, observation_ids)` | Selects already revealed legal records inside Runtime, charges the registered computation, retains proposal use, and returns the registered finite-alphabet moment answer |
| `construct_candidate(program, profile_id=...)` | Executes the initializer and optional preregistered paid replay before publishing the newborn at a common update-unit boundary |
| `retire_candidate(candidate_id)` | Releases the learner's own objects while retaining owned program references needed by past execution evidence |

An initializer with an inconclusive range bound may be retained as an
unresolved construction; it is not a live ordinary trajectory. Active
reference lineages execute the same exogenous events.
Structural controls and queries cannot run between a prediction and its
target, during an internal microphase, or after a halted prefix. The Runtime
has no caller-selected early flush of a partial update unit.

The registered optimizer is mean-CE projected SGD in exact rational
arithmetic, optionally followed by a fixed downward dyadic rounding at
commit. Its learning rate, update unit and rounding grid are fixed before
execution. The derivative is that of `log(T)-log(M_target)`, so exact
gradients do not require an approximate logarithm. Shared/repeated edges,
heads and tied parameter slots accumulate their actual derivatives; unused
slots remain present. Persistent weights stay nonnegative. This learner
treats delayed histories as stop-gradient event inputs. General recurrent
backpropagation and other optimizers are not implemented.

Each event retains the pre-target evaluation, state after observation and,
when applicable, state after optimizer commit. These are the actual phases
a later numerical bridge must cover. Computing and retaining them does not
itself prove a bridge or a certified log-loss enclosure.

## Registered profile is a value constructor

`ProfileSpec` fixes an ordered set of original observation identities, a
finite pass count and the implemented replay rule before labels arrive.
Only declared train/online IDs are legal. The constructor waits with
UNRESOLVED until all required records have actually been revealed; it
cannot substitute an initializer-only or caller-fitted endpoint. The total
number of replayed events must finish a full registered optimizer unit.
The same ordinary optimizer and rounding rule are used during profile.

Replay reads each record's **logged original score-time sources**, retaining
its observation ID and causal origin even if records are visited in another
order. It does not invent a new exogenous history by interpreting profile
indices as original event cursors. Positive recurrent bodies operate on the
newborn's actual local profile state and continue across passes. Every
prediction, observation, commit and range check incurs its registered work;
all retained buffers and old/new state coexistence are accounted for.

Profile has a separate local execution clock. Its endpoint retains theta,
gradient accumulator, delayed histories and optimizer step count; only the
clock namespace is attached to the current ordinary boundary. Both the
local and attached states are retained in the construction record. This is
a preregistered newborn value constructor, not an equivalence assertion,
an implicit recurrent reset, or replacement of a previously scored lineage.
Public ordinary/structural controls cannot interleave with construction.
The current reference endpoint assumes serialized host calls; this is not
a claim of a concurrent scheduler implementation.

Data-use records repeat the original IDs and mark every actual read as
profile. A backend/resource/range failure closes and releases the incomplete
newborn while retaining data use, charged work, executed profile evidence
and its owned code. It cannot fall back to a free fitted state. Since profile
reads old revealed targets, such failure need not halt the ordinary deployed
trajectory; its changed Compiler resources remain part of future state.
No new ordinary observation, fresh persistence event or statistical wealth
is created by replay.

## Information is declared, including what is not hidden

The supported information interface is **exact revealed train/online
access**. Public snapshots intentionally contain the revealed records and
complete reference learner state. No future target is stored by Runtime:
the exogenous producer supplies it only after the prediction. The current
interface does not claim to hide these already revealed labels behind a
small mean-query transcript. Its query precision bounds that query's output
alphabet, not information in all observable learner states or raw records.

Sources are fixed input coordinates at a declared lag, or target one-hot
atoms at a strictly positive lag. Their native availability delays must
agree with the registered read rule. An empty prefix reads zero; recurrent
buffers begin at their registered zero reset. Past primitive source reads
use retained, charged observation records, not free reconstructed history.
The exogenous input contract must itself be causal; finite observed values
cannot prove that an external producer did not encode its target as input.

Observation identities are unique across preregistered splits and consumed
in their fixed active-stream order. Validation/test streams cannot drive
this learner or its queries. No reporting-label ingestion endpoint exists
yet. A producer cannot relabel an existing registered observation to a
different split through the Runtime API. Identity registration is still an
external provenance assumption, not a proof of independent sampling.

Query coordinates are registered products of available sources, optionally
multiplied by a target indicator, averaged over selected revealed records.
The dimension, range, precision, record cap and computation charge are
fixed. Quantization uses exact nearest-level arithmetic with ties to even,
including ranges smaller than binary64 can represent. There is no supplied
`fn` or caller-computed answer. Failed computations retain their data-use
facts and spent work. No method issues a freshness authorization.

The only currently accepted stream-law ID explicitly grants **no
probability guarantee**. Reading a deterministic future sequence does not
make it iid. Query-only hidden-information contracts, stochastic laws,
predictable persistence admissions/bets and the error ledger remain open.

## Failure and physical history

The bounded target slot and its write work are reserved before prediction
returns. After `observe` accepts a valid target, its revealed record and
paid slot retain it even if gradient computation, range checking, work or
coexistence capacity subsequently fails. It cannot be retried as unread.

All active successors are built and range-checked before any becomes the
published current learner state. Old values and new values coexist under
the actual packed-buffer cap. Multi-owner releases are prevalidated as one
batch. A failed candidate after a successfully computed deployed successor
keeps both published input states, the revealed target, executed phase
evidence, temporary physical objects, cumulative work and peak residency.
The execution is then terminally halted for this recovery interface.
Resource/numeric/range uncertainty is UNRESOLVED; an unexpected backend
exception is recorded as EXECUTION_FAILED and re-raised. No rollback or
retry can manufacture an authorized prefix.

Retained phase records require their programs for future audit. The
information owner therefore acquires an actual shared code reference;
retiring the learner does not discard the sole graph behind an evidence
record. This costs the registered Compiler residency. Historical records
remain queryable, so they are not silently garbage-collected.

The machine still counts only actual packed payload bytes/objects and its
registered reference operation charges. CPython metadata and arithmetic
scratch, ingress objects before successful allocation, total host heap,
bit-time and CUDA memory/work are not covered by this partial model. A
terminal failure may retain diagnostic state outside that payload measure.
This is a material limitation preventing a complete physical-resource claim.

## Evidence and remaining boundary

`scripts/audit_reference_events.py` checks 960 exact reverse-gradient vectors
against independent forward differentials on 80 native graphs; all 64
three-event binary context/target streams on a shared graph with two live
reference lineages; fixed clocks, causal lags, data roles, 246 exact query
level/tie cases, and failures after target reveal. Work exhaustion, actual
successor coexistence exhaustion, and a candidate backend failure after
the deployed successor are exercised through the public Runtime.

The existing XVII.5 direct-PRODUCT value fixture runs through the endpoint
for 512 declared deterministic online events and 32 complete update units.
Every commit matches its independent scalar recurrence. The existing scoped
CE upper again crosses its old threshold at unit 13. These are distinct
declared stream positions with repeated values, not a claim of 16 unique
profile labels becoming 512 fresh stochastic observations. No new static
family, probability guarantee or population-identification claim is added.

`scripts/audit_reference_profiles.py` now additionally executes the same
value path from **16 retained labels**, with 512 charged profile events and
32 commits while the ordinary cursor stays at 16. Each commit matches the
existing scalar recurrence. The existing dormant-factor fixture retains its
five zero coordinates for another 512 profile events. Sixteen exhaustive
two-event input/target streams give 64 independent replay checks; recurrent
source/state attachment, forbidden roles, unavailable data, interleaving,
backend failure, cumulative work and coexistence caps are also audited.
The uniform deployed predictor is the empirical optimal unigram on the
balanced fixture. Neither this comparison nor the dormant parameterization
is a global rejection of all one-PRODUCT programs.

Current package modules import. The previously falsified helper signers
are no longer callable: `proof.py` and `bridge.py` explicitly reserve the
unimplemented authority boundaries. The exact historical code, including
its old learner dependency, is loaded in an isolated module namespace from
Git commit `39235ef` by `scripts/audit_recovered_authorities.py`. All four
historical false authorizations remain reproducible. Empty authority ports
do not count as passed proof/bridge gates.

Next integrate grammar-complete search with explicit decision classes and
typed proof authority, then stochastic
fresh persistence and complete physical/error state. Certified float64,
actual AMP, atomic installation and the complete 47-gate mapping remain
release obligations. The Runtime currently grants no CERTIFIED_COMPLETE,
persistence, bridge or installation authorization. RTX 3090 science remains
HOLD; static theory expansion remains parked.
