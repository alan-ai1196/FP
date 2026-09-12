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
| `begin_context(observation_id)` | Prepays bounded raw-byte storage/work and fixed status before offering input; seals the active learner and persistence identities |
| `receive_context(ingress_id, offset, chunk)` | Receives exactly the next offered bounded bytes into the paid window, without per-chunk records or counters |
| `finish_context(ingress_id)` | Guards and decodes the owned exact frame, reads available causal sources, and executes every active prediction |
| `predict_next(observation_id, encoded)` | One bounded byte chunk through the same begin/receive/finish path; raw rational values cannot bypass ingress |
| `observe(target)` | Records the target once, accumulates exact CE derivatives, advances positive delayed bodies, and commits only at the full registered update-unit boundary |
| `query(query_id, observation_ids)` | Selects already revealed legal records inside Runtime, charges the registered computation, retains proposal use, and returns the registered finite-alphabet moment answer |
| `construct_candidate(program, profile_id=...)` | Executes the initializer and optional preregistered paid replay before publishing the newborn at a common update-unit boundary |
| `retire_candidate(candidate_id)` | Releases the learner's own objects while retaining owned program references needed by past execution evidence |
| `start_reference_search(search_name)` | Fixes the current baseline and opens one preregistered finite constructor class on its revealed objective records |
| `advance_reference_search(search_id, transitions=...)` | Advances the owned checked native cursor, actually constructs/compares emitted programs, and verifies the closed reference class |
| `reference_class_proof` / `verify_reference_class_proof` | Retrieves or verifies only a current Runtime-issued token for the specified exact reference class |
| `cancel_reference_search(search_id)` | Terminates that search and its authority while retaining its queryable owned history and live constructed winner |

These manual control methods also implement the owned strategy below.
With `policy=CompilerPolicy(...)`, only event transport and passive snapshots
remain callable externally; Runtime invokes all Compiler decisions itself.

An initializer with an inconclusive range bound may be retained as an
unresolved construction; it is not a live ordinary trajectory. Active
reference lineages execute the same exogenous events.
Structural controls and queries cannot run during context reception,
between a prediction and its target, during an internal microphase, or after a halted prefix. The Runtime
has no caller-selected early flush of a partial update unit.

`DataContract.ingress` preregisters a byte capacity and maximum chunk size.
The canonical frame encodes exactly the declared rational input coordinates;
its grammar represents every nonnegative rational vector. Byte/integer
capacity failures return UNRESOLVED and keep all actually received bytes.
Only offered chunks cross the Runtime boundary. Larger producer frames must
use repeated receive calls; an unread suffix cannot be passed as hidden
caller state. Wrong canonical encodings or source-domain violations halt
with the received prefix retained. Read
[`OWNED_CONTEXT_INGRESS.md`](../theory/proofs/OWNED_CONTEXT_INGRESS.md).

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

## A complete finite reference class, with a limited proposition

`ReferenceSearchSpec` fixes separate node/SUM/PRODUCT/edge/slot caps, a fixed
nonempty set of original train/online objective IDs, and either the
initializer alone or one registered profile. Search starts at a full
ordinary boundary after its required labels are available. The finite
semantic source/type/delay rules come from the enclosing contract.

The complete ordered grammar includes repeated sources/edges/heads, shared
and square PRODUCT descendants, all legal ordered SUM edge strings,
unused slots, delayed bodies and every binding order. A poor program is
still a potentially useful prefix; no value, gradient or support test
prunes its descendants. `native_search.py` separates ordinal planning from
checked ranking/closure. The Runtime owns the complete explicit cursor,
so there is no caller-supplied generator, candidate menu or upper bound.
Read the coverage proof in
[`ORDERED_NATIVE_REFERENCE_CLASS.md`](../theory/proofs/ORDERED_NATIVE_REFERENCE_CLASS.md).

Every emitted graph uses actual owned construction/profile execution.
Its objective evaluates each logged source context with the same frozen
endpoint learner state, including delayed buffers. Multiplying its exact
positive target probabilities ranks equal-sized empirical CE sums without
floating log error. These objective evaluations create no new ordinary
event and grant no population or future-continuation claim. Each read is
charged and retains the original IDs as proposal data. Range uncertainty,
missing observations, uncompleted value construction or arithmetic/resource
failure stays unresolved; even completed syntax cannot then issue a proof.

The proposition compares **all registered constructor endpoints plus the
actual deployed baseline**. A baseline outside the grammar may win. Before
issuance, every retained endpoint is rebound to its initializer/profile,
rescored, and checked against an independent maximum verifier. The claimed
score must equal that of the actual live winning program and complete
learner state. Final verification has its own paid work and residency; a
search that finishes all rows can still be UNRESOLVED at this step.

`ReferenceClassProof` has one fixed proposition kind. It is accepted only
when it exactly matches a retained issuance for this Runtime, claim, class,
search, lineage/cursor and current context revision. The class ID names the
registered class specification; the issuance's executed Runtime context
binds its actual records, baseline and constructor endpoints. A constructed
or altered helper object cannot grant authority. Any relevant external
mutation makes an active prefix or old proof stale. Chunked internal search
preserves its own checked cursor; snapshots carry no resume/write authority.

The entire cursor and comparison history reside in actual packed Compiler
workspace, replaced by allocation before release. Retiring nonwinners
retains owned code needed by their rows/profile evidence. Cancellation
retains the queryable packed history; it does not silently free payload
still exposed by snapshots. Work and peaks are never refunded. A terminal
diagnostic-retention failure is explicitly outside this partial payload
model and cannot activate a proof.

The success result is `REFERENCE_CLASS_EXHAUSTED`. `programs_compared`
counts successful exact comparisons; `unresolved_programs` counts visited
members without one. Neither result nor proof authorizes arbitrary values,
all legal future continuations, a population optimum, fresh persistence,
equivalence, AMP or installation. No full Compiler `CERTIFIED_COMPLETE`
is emitted.

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
facts and spent work. A data-use record itself issues no freshness authority.

The original stream-law ID explicitly grants **no probability guarantee**.
`StochasticStreamLaw(assumption_id)` additionally records an external
branch-invariant stochastic-process assumption relative to the complete
Runtime filtration. It does not infer iid sampling from observed values or
hide an exposed future tape/seed. Query-only hidden-information contracts
remain open; the reference persistence endpoint below requires the typed
stochastic assumption before any alpha allocation.

## Fresh reference persistence

`OnlineContract.persistence` preregisters the finite rules and total alpha.
Each rule fixes the epoch length, horizon, alpha, bet, gain bound, logarithm
terms and dyadic wealth precision. `admit_reference_persistence(candidate_id,
rule_id)` takes no losses, observation IDs, supplied state or wealth. It
requires two owned range-safe learners at a shared ordinary update boundary
and admits only their subsequent contexts. The epoch clock need not match
the optimizer clock. A context already admitted by `begin_context` blocks
admission; a profile or proposal query on old IDs creates no future score.

Each identity retains the candidate/base program IDs, complete initial and
current learners, ordinary cursor, epoch accumulator, stopped wealth and
physical evidence ownership. Runtime seals the active identity set with the
event and derives gains from the same pre-target predictions used by the
ordinary continuation. Both observe/commit successors must actually finish
before evidence is published. A crossing during a partial optimizer unit
remains a reference statistic; it is not an atomic install boundary.

The positive base and native normalizer cap imply
`K=max_y (R-sum(b)+b_y)/b_y`, hence `abs(log(p_C/p_D))<=log K`.
Admission must prove the rule's rational bound covers this class. Each
event uses guarded rational log enclosures and every fixed epoch applies
a downward-rounded nonnegative factor. Exact cross-product comparisons
also obey the integer-work cap. The statistic stops at first crossing,
which bounds its wealth below `2/alpha`; future ordinary events must still
preserve the same complete pair before a live result can be returned.

The conditional null is a bounded next-epoch mean-gain statement relative
to the complete pre-epoch filtration. It is not conditioned on successful
computation. See [`OWNED_REFERENCE_PERSISTENCE.md`](../theory/proofs/OWNED_REFERENCE_PERSISTENCE.md)
for the theorem, failure branches and external-law assumptions. The Runtime
enforces the executed evidence path; it cannot empirically establish the
producer's law or a conditional expectation from its finite transcript.

Each actual admission spends alpha before fallible workspace creation.
Several preadmitted identities may share a fresh observation, with separate
allocations; statistical independence is unnecessary. No cancellation,
retirement, failed build or exhausted horizon refunds alpha. Post-reveal
evidence failure terminates the identity, and ordinary transition failure
terminates every live comparison. Old wealth remains historical only;
skipping the failed factor and resuming is forbidden. A rebuilt candidate
requires a new identity and allocation even if its current prediction agrees.

`reference_persistence_result` reports `REFERENCE_CROSSED` only while the
actual current reference pair matches the retained continuous trajectory.
There is no caller-submittable persistence certificate or helper signer.
Finite noncrossing, range/numeric/resource uncertainty and lack of a
stochastic assumption give UNRESOLVED. This supplies no pair-atomic AMP
persistence, equivalence, complete Compiler or installation authority.

## Checked CPU binary64 continuation

`OnlineContract.float64` fixes the exact state/probability tolerances and
one scalar backend before execution. Runtime constructs an independent
finite learner beside each exact learner. Both begin at the registered
initializer; profile replay and ordinary events advance each trajectory
through its own arithmetic. Profile clock attachment preserves all raw
finite values. No optimizer endpoint, gradient or recurrent queue is reset
to a cast of its exact counterpart.

The finite evaluator executes ordered separate multiply/add, rounded
reciprocal derivatives, a fixed accumulation order and projected SGD. Its
scalar CPU outputs must match a guarded exact rounding oracle. Signed zero
bits survive alongside complete delayed queues and partial accumulators.
The declared scalar schedule must finish before a phase can pass. Runtime
checks full state before scoring and after observe/commit, and separately
checks exact decoded mass normalization, the rounded normalizer and actual
final division output. Displayed prediction equality cannot hide a stored
mass error.

Every successful phase has owned packed evidence in `snapshot.float64_traces`;
current state buffers contain both learners. A failed evidence allocation
leaves a terminal diagnostic with no CHECKED status, subject to the same
partial physical-model limitation below. A backend invariant error is an
execution failure, not rejection of an already admitted native graph.
Ordinary numerical failure halts the shared prefix and removes any current
reference persistence authority. Passive phase records cannot be submitted
as installation or AMP tokens.

This is an executed finite CPU prefix relation. No all-context floating
range bound, unexecuted future guarantee or stochastic finite-path evidence
is inferred. Read [`OWNED_FLOAT64_PREFIX.md`](../theory/proofs/OWNED_FLOAT64_PREFIX.md).
The endpoint audit checks 1,024 phases over 64 complete short streams plus
192 floor-grid phases, with 406 coordinates differing from exact-endpoint
recasts. It also checks actual profile/recurrent paths and post-target
failure through the public endpoint, using an independent float interpreter.

## Two same-path CPU persistence statistics

The current endpoint has one path-declared persistence engine. The original
`exact-reference` rule and the new `binary64-stored-mass` rule each name a
fixed stopped-epoch mean-null, their own gain bound and a separate allocation
from the same global alpha budget. The finite path uses exact mathematical
normalization of its actual stored masses. It cannot borrow reference
scores or wealth, or substitute the rounded output for a probability vector.

`admit_float64_persistence` proves current whole-domain binary64 range and
delayed invariants with paid monotone rounded forward bounds. These bounds
cover the registered source box or every declared finite source row. They
are refreshed when optimizer theta changes. Failure ends that evidence
identity before the next context; an observed safe point cannot substitute
for the domain premise. All four raw/exact current learners stay owned.

`paired_persistence_result(reference_id, float64_id)` reads two owned
identities and checks their four complete initial states, lineage/program
IDs, starts and epoch/horizon schedule. Both current same-path statistics
must have crossed. Each stopped statistic continues to track the ongoing
complete learner paths; numerical failure, retirement or failed current
evidence allocation cannot leave a reusable crossing. Profiles retain
original observation IDs and create no new persistence events.

Read [`PAIRED_CPU_PERSISTENCE.md`](../theory/proofs/PAIRED_CPU_PERSISTENCE.md)
and `scripts/audit_paired_cpu_persistence.py`. With delta=2^-54, the actual
reference path crosses at event five while binary64 mass gain is exactly
zero forever under the declared fixture. This excludes statistical evidence
transfer based on small numeric error. `PAIRED_CPU_CROSSED` is a CPU protocol
result, not actual AMP, full resource closure or atomic install authority.

## Serialized CPU installation from owned evidence

`OnlineContract.cpu_install` fixes the CPU policy before execution.
`install_cpu(candidate_id, proposal_proof_id=..., reference_identity=...,
float64_identity=...)` retrieves only owned records. A reference search
proves selection at the proposal cursor; fresh persistence starts from those
exact candidate/base states and then advances them. The old proof remains
rejected as a current maximum. Installation instead checks historical
selection, current dual persistence, full unit boundaries and the current
complete exact/binary64 relation as separate premises.

All existing learner buffers stay physically identical. Paid preparation
stages replacement metadata and a receipt against the live old ledger.
`ResourceLedger.prepare_transfer` checks aggregate debits against original
leases and constructs a detached final map. Runtime prepares the complete
new root before one serialized CPython publication changes deployed ID,
ownership, search status and persistence status together. The old deployed
learner becomes a retained shadow. Other shadows and all history remain;
paused searches close without losing their frontier, and persistence cannot
rebase its wealth or refund alpha after the comparator changes.

An unsuccessful preparation preserves old learners/evidence/frontier, but
the attempt, revision, work, peak and retired IDs remain changed. Retrying
uses unique attempt-specific physical metadata IDs. Actual resource failures
return UNRESOLVED and cleanup failure halts. A prepared receipt is never
published as installation authority after an abort. Unknown Runtime or
ledger coordinates prevent reuse of this fixed frame proof.

Read [`OWNED_CPU_INSTALLATION.md`](../theory/proofs/OWNED_CPU_INSTALLATION.md)
and `scripts/audit_cpu_installation.py`. Independent checking covers 2,016
small lease cases, including a simultaneous role exchange that cannot be
implemented by acquire-first under the same role caps. Actual complete
35-/774-program classes proceed through fresh continuous evidence,
installation and later ordinary events; the larger case installs trained
nonzero parameters. Real immutable byte/work caps, stale proof/frontier,
same-graph newborn, partial unit, late abort and paid retry are exercised.
A second complete search/evidence/install cycle uses the actually installed
baseline. Both generations retain their receipts; four alpha allocations
reach the global cap and refuse a third admission despite available fresh
events. This continuation has 306 independent binary64 phase checks.
`INSTALLED_CPU` describes this executed serialized transition only. It is
not a current class optimum, target AMP, full ERC-1 physical enforcement,
concurrent caller linearizability or crash recovery.

## Failure and physical history

The control rule introduced in v2 and retained by v7 charges one fixed unit for each
public Compiler mutation, using the already immutable construction,
information or install work role. If that debit cannot be paid, no owned
attempt, revision, query, frontier, evidence or resource history changes.
An already issued current reference proof remains current across such a
refusal. Once admission succeeds, all actual following work and failed
history remain spent. Ordinary target ingress stays prepaid by prediction;
there is no new after-target gate that could unread its value.

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

The packed ledger counts actual payload bytes/objects and registered reference
operation charges. CPython metadata, scratch, transient byte/ledger copies
and general exception/history objects remain partly outside that measure.
The optional v6 live host binding below covers the process-private commitment
dimension. Neither measure alone closes the complete physical contract.

[`OWNED_CONTROL_ADMISSION.md`](../theory/proofs/OWNED_CONTROL_ADMISSION.md)
preserves two historical obstructions. Paid admission corrected free control
history growth. Mandatory v3 byte ingress now also corrects uncharged
oversized rationals in pending state: the byte window and fixed terminal
status exist before receipt, length guards precede numeric materialization,
and incomplete or over-precision frames keep their exact paid prefixes.
Equal byte prefixes have identical recorded states under all legal chunkings
in the fixed serialized machine. Neither result measures every host object;
a metadata multiplier or manifest-only change cannot establish that claim.

## Source identity and admitted encoding

The pre-v4 JSON encoding conflated an astral source-name character with two
explicit surrogate code units. Both were distinct legal Python source names.
The original Runtime at `532d713` consequently let candidate construction
overwrite the deployed program registry entry, changing its next probability
from required 2/3 to 1/2 without installation. The current typed stream uses
UTF-8/surrogatepass and preserves the exact code points. Reusing an owned
address also requires complete validated Program equality, with UNRESOLVED
on a collision. This does not identify programs merely by current forecasts.

The same encoding now has an exact size pass. `realize` returns a passive
value/extent plan; only the owning Runtime's allocation check precedes actual
in-place output writing. Identity hashing does not build a second tagged
Python tree. The reserved target slot is written through the same encoder.
ASCII artifacts retain their bytes, while non-ASCII encodings intentionally
change. Stored buffers are private bytearrays and snapshots return byte copies.

Read [`OWNED_ENCODING.md`](../theory/proofs/OWNED_ENCODING.md). The old/new
100,000-edge construction audit reduces a roughly 62 MB newly traced Python
peak to roughly 0.134 MB before the same 8 KiB packed-cap refusal. This is a
measured removal of encoding workspace growth, not total-heap enforcement.
The v6 host binding supplies a declared commitment fence for the remaining
private workspace. The complete physical contract still precedes Runtime freeze.

## Host allocation exhaustion

Machine v5 distinguishes an ordinary checked ledger refusal from a host
MemoryError. Old `dfa1583` cleanup after a failed construction-result allocation
freed the new learner buffers while the next public prediction still used
its candidate. Current code prepares that result before publication and
propagates MemoryError to one public terminal boundary. A precreated marker
uses existing state slots; it allocates no cleanup/history, refunds no alpha
or work and cannot be reset by a legal continuation. All proof, persistence
and install ports also close. Snapshots are passive and may still fail.

Read [`HOST_ALLOCATION_FAILURE.md`](../theory/proofs/HOST_ALLOCATION_FAILURE.md).
The audit includes 22 ports and a real Windows job denying an unmodified
128 MiB ingress-window allocation under a 64 MiB commitment cap. That OS
measure is independent of packed bytes; the next section binds it to Runtime.

## Live host resource history

Machine v6 additionally accepts `HostResourceContract` at Runtime creation.
The fixed whole-process private-commitment arena is shared by deployment and
compiler: each pays its full measure, once globally. Thus the Windows
process/job cap is `min(global, deployment, compiler caps)`. Runtime owns the
native queries of its current process and immediate job, with no caller PID,
handle, counter or callback port. The immutable policy contributes to chi;
`host=None` has no populated host observation and proves no host cap.

Public calls check the actual native limits and process-lifetime peak. The
kernel enforces commitment throughout the body, including metadata and
temporary workspace; installation adds no fallible post-publication check.
The complete CPU root retains the binding. Process CPU history is observed,
not rebased or hard-capped. Host snapshots are sampled kernel observations,
not full physical state or a future-equivalence test; repeated counters can
change without a learner transition. Job aggregates remain separate from
process-lifetime history.

An unestablished host premise gives `HostExecutionUnresolved` and closes
continuation/authority through a precreated marker. The first host marker
survives subsequent diagnostic failures of either host-failure type. This
does not assert successful recovery or general snapshot availability.

Read [`BOUND_HOST_RUNTIME.md`](../theory/proofs/BOUND_HOST_RUNTIME.md) and run
`scripts/audit_bound_host_runtime.py`. The real late-fence witness shows why
current memory/new-job peaks cannot establish the whole process history.
The actual 35-program search, four-learner persistence, CPU installation and
continuation execute inside one 64 MiB process. A completed-looking child
file followed by unsuccessful exit is rejected by the audit parent.

The scoped binding assumes the trusted launcher preserves its job policy.
Complete ERC-1 run/report registration, production supervision/publication,
family accounting for claims spanning multiple roots, other resource limits and
shared platform/device costs remain open. A supervisor cannot perform FP
policy work or retain its state outside the measured execution for free.

## Owned native-class strategy

Machine v7 registers `CompilerPolicy` in the actual Runtime constructor.
Each stage names a complete registered native class, an earliest complete
ordinary boundary, a fixed enumeration-step allowance and the two matched
persistence rules. It supplies no architecture or fitted state. Empty stages
give the closed ordinary baseline; `policy=None` is explicitly manual.

After each successful optimizer unit, the strategy visits the first unfinished
stage. It searches, keeps an incumbent selection or admits two fresh paths,
then follows their ordinary continuous evidence until a common-boundary
installation or an unresolved outcome. A step allowance never certifies
grammar exhaustion. The registered external interface permits only context/
target transport and snapshots; the 17 other current control/authority ports
reject, and newly added methods default to denied in this mode.

All policy status, cursors and owned search/candidate/proof/evidence/install
IDs belong to Omega and paid packed storage. Retention failure after an action
halts with its actual targets and costs retained; no retry can manufacture
fresh alpha. The completed policy record participates in the same installation
root/lease publication as the actual learner. There is no allocating success
bookkeeping afterward. Native premise loss now propagates through nested
public calls and broad handlers without allocating cleanup.

The ordinary `ObservationResult` describes the already completed event. The
separate owned policy/halt coordinates describe any subsequent Compiler
failure; observing a target is not a successful-run publication certificate.
Read [`OWNED_COMPILER_POLICY.md`](../theory/proofs/OWNED_COMPILER_POLICY.md)
and run `scripts/audit_owned_compiler_policy.py` for the two-install and trained
native-class chains, exact short-stream oracle, failed-prefix tests and real
64 MiB process. Its error bound is per actual Runtime root. A comparison
family spanning restarted roots needs a larger declared allocation protocol.

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

The search audit independently covers nine full grammars (14,860 program/
class cases), 3,120 saturated count calculations, 110 actual profile
candidates with 440 replay events, and ten recurrent/binding programs.
Eight profile endpoints actually change their initialized values. All 587
members of a small XOR grammar are compared: a PRODUCT descendant reaches
likelihood 1/12 while every shorter prefix and the complete same-class P=0
portion stay at 1/16, also the empirical optimal unigram. This is an exact
bounded Runtime audit; its explicit zero-slot class is not substituted for
the unrestricted SUM coefficient class. False prefix closure, substituted
rows, wrong selection, an inflated winner score, stale/altered tokens and
backend/range/information/numeric/work/coexistence failures are exercised.

`scripts/audit_reference_persistence.py` traverses the actual admitted event
path, including 12 independent pre-target score/log/wealth checks with six
changing optimizer commits and H=3 distinct from update unit two. A separate
H=1 crossing at cursor three retains its partial accumulator. All 32
five-event fair-label paths execute 160 ordinary events and give 31 exact
conditional lower-wealth inequalities. Actual integer/work/memory limits,
shared fresh IDs, old profile/query data, new lineages, post-crossing commit
failure and failure while materializing the first crossing are checked.
Pure numerical and wealth kernels have separate exact audits; neither is
substituted for these Runtime ownership/filtration/continuity checks.

Current package modules import. The previously falsified helper signers
are no longer callable. Current proof data and fixed maximum checking have
only the Runtime-issued scope above; `bridge.py` remains reserved.
The exact historical code, including
its old learner dependency, is loaded in an isolated module namespace from
Git commit `39235ef` by `scripts/audit_recovered_authorities.py`. All four
historical false authorizations remain reproducible. An empty bridge port
does not count as a passed bridge gate.

Machine v8 adds the actual aggregate immutable reference manifest and finite
run closure. `snapshot().run` binds the original Program, all constituent
contracts, fixed arithmetic and paid manifest bytes. At the registered
ordinary horizon the owned strategy finishes its eligible phase and Runtime
prepares a paid closure before sealing all non-diagnostic public ports.
Historical class completion, unfinished policy stages and execution status
are separate report coordinates. Partial final optimizer state stays intact.
Closure failure retains any already published event/install but reports a
halted, unresolved run. Read [the run proof](../theory/proofs/OWNED_REFERENCE_RUN.md)
and execute `scripts/audit_reference_run.py` for the bounded CPU chain and
terminal/failure adversaries.

The [47-gate mapping](REFERENCE_RELEASE_GATE_MAP.md) identifies owned
hierarchical anti-unigram discovery and final integration checks as current
reference work. Optional broader control/information/family claims do not
silently enlarge that scope. The CPU relation and finite run do not close
actual target AMP. The generic target install port stays UNRESOLVED; no
CERTIFIED_COMPLETE or target AMP authorization is issued. Actual target
correctness follows reference closure, then RTX 3090 model science, which
remains HOLD. Static theory expansion stays parked.
