# Paid exact context ingress and retained terminal prefixes

Status: **implemented protocol, scoped invariant proof, exact finite audits.**
Foundation and ERC-1 specifications remain frozen. Runtime is NOT FROZEN;
actual AMP and RTX 3090 science remain HOLD. This closes the raw rational
retention counterexample at `5055f3e` within the declared packed machine.
It does not establish a total CPython heap or physical execution bound.

The obligations come from [FP_THEORY.md II, XII, XVIII](../../FP_THEORY.md)
and the existing [ERC-1 information/resource contract](../../EXPERIMENT_RESOURCE_CONTRACT.md).
The correction changes the implemented information transport and its cost,
without adding a model architecture primitive or narrowing rational sources.

## 1. Why a later arithmetic guard was insufficient

The pre-v3 Runtime accepted a tuple of exact input values, put it in pending
state, then checked its registered integer limit. On the legal source box
[0,1], inputs `1/2^m` at arithmetic limit 128 left denominators of
257,1025,4097 bits in halted state, with unchanged work and packed payload.
[The historical audit](../../scripts/audit_control_admission.py) now executes
the original Runtime, machine and data registration from Git `5055f3e`.
The earlier positive control-admission correction did not bound the amount
of information a single context call could already retain.

Checking the value sooner still leaves the transport's ownership question:
which bytes crossed the interface, and where do they survive a failure?
Erasing or casting a received input, or claiming that all legal source
values fit the implementation's integer limit, would evade that question.

## 2. A representation contract before the first byte

`DataContract` now requires access ID
`bounded-exact-revealed-train-online-v2` and an immutable `IngressContract`.
It fixes positive window capacity C, maximum chunk q<=C and one canonical
wire grammar before execution. The current defaults are C=4096 and q=64.
The registered machine is `packed-reference-payload-v3`; its positive
Compiler control-admission rule from v2 is retained.

A frame is the three bytes `FP1`, followed by exactly d nonnegative rational
coordinates. Each coordinate stores its numerator then denominator. An
integer has a canonical unsigned base-128 byte-length prefix and a minimal
big-endian body. Zero has length zero. Denominators are positive and each
fraction is reduced; leading zeros, nonminimal lengths and trailing bytes
are invalid. This finite grammar represents every nonnegative rational
vector. It does not fix a maximum semantic precision.

The pure producer encoder and parser return no authority. The Runtime
receives data only through these public ports:

1. `begin_context(observation_id)` accepts no context. It checks the next
   registered identity and idle phase, prepays work, seals all active learner
   and persistence IDs, then reserves an owned C-byte body, a fixed control
   slot and a packed identity record. A detached ledger preflight checks
   actual current capacity before creating the empty body. All preparation
   and the return object exist before one receiving-root publication.
2. `receive_context(ingress_id, offset, chunk)` accepts only exact immutable
   bytes, a nonempty chunk within the offered remaining extent, and exactly
   the next offset. It writes in place to the prepaid body and fixed control
   slot. It cannot retain an unread producer suffix or accept a target.
3. `finish_context(ingress_id)` parses the owned prefix once. A checked
   decoded vector enters the existing causal prediction/observe/commit
   protocol. The ordinary decoded record and target slot must be allocated
   before the decoded record can enter retained pending state.

`predict_next(observation_id, encoded_bytes)` is only a one-chunk convenience
port through these same three methods. Raw value tuples are rejected;
larger frames require the offered chunk protocol. The audit producer
`scripts/ingress_audit_support.py` owns its values and full serialization
outside Runtime; it passes only offered chunks and supplies no internal
state, resource role, result flag or token.

The control slot contains one status byte plus a fixed-width received count:

`h(C) = 1 + ceil(log_256(C+1))` bytes, for C>=3.

Status is RECEIVING, DECODED, PREDICTED, UNRESOLVED, INVALID_INPUT or
EXECUTION_FAILED. The empty allocation costs exactly C+h(C)+|pack(identity)|
retained payload bytes and three objects. The body remains allocated after
successful observation too; no history compression is inferred.

## 3. Scoped receive-prefix and cost invariant

The v3 reference work metric prepays `w(C,d)=4C+16d+32` at begin. It reserves
copying, bounded parsing and up to C nonempty receive calls. This is a fixed
partial reference charge, **not** a claim about CPU instructions or bit-time
of rational arithmetic. Other ordinary prediction and evidence work still
pay their existing charges. No future target is charged retroactively.

**Proposition.** Under the registered serialized Runtime calls, every
published receiving window has a paid body and fixed control extent. For
received count r, 0<=r<=C, its first r bytes are exactly the admitted prefix,
the remaining C-r bytes are the initial zeros, and no received suffix has
been discarded. Receive segmentation changes neither recorded resources
nor any other retained Runtime coordinate at equal byte prefixes.

**Proof.** Before publication, allocation validates both sizes and the
complete current ownership/residency map. The initial header is (RECEIVING,0)
and the body is C zeros. A legal receive call has 1<=k<=min(q,C-r) and offset r.
It prepares its return/header before writing, then replaces exactly k bytes
and the equal-length header with count r+k. No buffer grows and no ledger
event, revision, identity or per-chunk record is created. Induction gives
the prefix invariant; it also bounds accepted calls by C and copied incoming
bytes by C. Equal prefixes have the same body, header and all untouched
recorded coordinates. Finishing starts from those identical states, so the
fixed deterministic parser and ordinary execution have identical results.

There is a cumulative bound too. If W is the remaining work in the immutable
information role at a boundary, at most `floor(W/w(C,d))` subsequent windows
can publish, because failed admissions and all other work are nonnegative
and no install refunds them. Their retained raw bodies total at most
`C*floor(W/w(C,d))` bytes; the finite remaining observation schedule and
actual residency cap can reduce this further. This is the ingress-storage
bound absent from the historical raw-value interface. Packed identity and
control objects are additionally checked against actual residency; general
host metadata is outside this proposition.

The two fixed-size writes assume ordinary serialized CPython execution.
The proposition does not cover asynchronous exceptions between those writes,
concurrent callers, crash recovery, allocator histories or elapsed time.
Equality here is of the declared retained Runtime state, not an equivalence
claim for an unregistered complete physical machine that observes those
additional coordinates.

An unfunded begin changes no owned state or current proof revision. A begin
that paid work but failed before publication retains its attempt, spent work,
peak and retired physical IDs. Only predetermined empty preparation storage
may be released at that point: no receive call was possible. A retry needs
a new paid identity. Successful begin invalidates an old current optimum
revision before any context byte is offered.

## 4. Failure is a retained information prefix

The decoder bounds byte lengths before shifting a length into an oversized
integer or materializing its body. It checks the body's leading bit before
`int.from_bytes`, so an integer of L+1 bits cannot be created first and
rejected only by the L-bit reference guard. Missing bytes or insufficient
numeric capacity yield UNRESOLVED. Invalid canonical encodings or actual
source-domain violations retain the prefix, mark INVALID_INPUT and halt.
UNRESOLVED does not certify semantic infeasibility or completeness.

All received bytes and the fixed status slot already have owned storage
when parsing starts. Failure at zero remaining ordinary work therefore
cannot require a new raw-input buffer or erase the input. The old examples
now retain respectively 42,139,523 exact wire bytes in prepaid 1024-byte
windows, with no oversized rational in pending state. Their raw bytes are
available in the owned snapshot. A capacity-limited frame retains exactly
its received prefix; the external suffix never enters the Runtime method.
The halt is terminal: repeated finish or receive cannot turn it into unread
data. An earlier unexpected prediction failure keeps its original cause;
ingress does not append a second halt and replace that cause.
An internal predictor contract failure remains EXECUTION_FAILED; it is not
relabeled as an invalid source value merely because it uses ContractError.

Structural/query/evidence controls are blocked throughout receiving. The
preadmitted reference and binary64 comparison IDs are fixed before the
first byte, and later pending predictions inherit exactly those IDs.
No partially observed context can authorize a new bet or candidate. A
stochastic producer and its full-filtration law remain explicit external
assumptions; the deterministic test tapes do not prove those assumptions.

## 5. Evidence and remaining boundary

Run `python -B scripts/audit_context_ingress.py --write`. Its compact
[artifact](../../evidence/minimal/FP_CONTEXT_INGRESS_AUDIT.json) records:

- 3,072 small numerator/denominator/width cases, 85 complete small vectors,
  24 integer/length-prefix boundaries and all ten proper prefixes of one
  complete frame; instrumentation checks refusal before big-integer creation.
- All 208 chunkings of a nine-byte frame with q=4, including 1,328 exact
  owned-prefix snapshot checks and identical prediction/observation states.
- 64 unchanged work-denied admissions, a 10^12-byte registration refused
  before window creation, actual allocated-then-failed preparation and retry.
- All three historical numeric witnesses corrected at the real endpoint;
  retained partial/capacity/invalid/backend failures and fixed terminal
  storage even when ordinary work is exhausted after begin.
- 90 control/target rejection positions during partial context reception,
  four ordinary events on the preadmitted four learners and 22 independent
  binary64 phase checks. The ordinary/profile/search/persistence/installation
  integration audits also enter through the mandatory byte protocol.

The same 2,016-case lease audit and 35-/774-member selection/evidence/install
chains pass, including two successive installations and later observations.
CPU root publication now includes ingress identities and the active ingress
coordinate, with past byte windows retained as actual leases.

The physical frontier remains real: Python objects behind packed metadata,
detached ledger copies, transient byte copies, decoder arithmetic/gcd scratch,
general diagnostic records, allocator/GC behavior and refused-call CPU time
are not all measured by this model. The fixed ingress **status slot** is paid;
this is not a claim that every Python exception/history allocation is paid.
Complete ERC-1 registration/enforcement and release-gate mapping still precede
actual target AMP correctness and then RTX 3090 science. A manifest field or
a constant metadata multiplier cannot substitute for those missing bounds.
