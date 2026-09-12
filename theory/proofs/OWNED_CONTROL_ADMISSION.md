# Paid control admission and the unbounded-history counterexample

Status: **exact implementation counterexample, corrected control boundary,
and scoped request-count proof.** Foundation and ERC-1 remain frozen. This
does not close complete host/device accounting or authorize a Runtime freeze.

The obligations are [FP_THEORY.md II, XII, XVIII](../../FP_THEORY.md) and
[ERC-1 sections 2--3](../../EXPERIMENT_RESOURCE_CONTRACT.md): claim-relevant
identity/history state is real state, and a physical-resource claim cannot
discard it because the model's numerical buffers did not grow.

## 1. Fixed numerical resources, unbounded distinguishable history

At commit `8880371`, the public constructor increments the Compiler revision,
mints a candidate and registers its owner before attempting to pay inspection
work. If work is exhausted, the catch path closes the new owner and retains
a failed attempt. This changes no live packed model buffer and pays no work,
but it adds another identity, owner, resource-event history and diagnostic.

The exact executable witness uses a legal zero-SUM native program throughout.
Bootstrap costs 17 Compiler work units. Fix its immutable cap at 18 and make
one underfunded construction request. Once that last work unit is spent,
repeat the same legal request n times. Every result is UNRESOLVED. For every
n, current and peak packed payload, object count and spent work stay fixed,
while `next_candidate` and the failed-attempt count each grow by n. Each
request also adds an owner and three resource events. The audit reproduces
n=64 directly from the original machine/Runtime source in Git, with no second
maintained source tree.

**Counterexample.** No finite function of those fixed resource caps and that
fixed manifest bounds the complete retained state of the historical Runtime.
The states after 0,...,n requests are distinct even under the public `snapshot`
continuation, which exposes different identity counters and histories. Any
exact representation distinguishing them needs at least log2(n+1) bits.
The actual retained attempt list grows more quickly. A constant metadata
overhead multiplier on packed model bytes cannot repair this example.

UNRESOLVED was an honest decision status. The failure was inferring a complete
physical bound from an accounting model with free state growth. No new FP
semantic architecture primitive is required; the physical control admission
was incomplete.

## 2. One admission rule for Compiler control

`packed-reference-payload-v2` introduces one positive, fixed control admission
charge before an external Compiler request may change owned state. Its value
is one registered reference work unit. It is not a measured CPU instruction,
elapsed-time estimate or complete cost of the subsequent operation.

The same gate covers public construction, retirement, query, reference/finite
persistence admission and cancellation, search start/advance/cancellation,
and CPU installation. The role is derived from the immutable construction,
information or installation routing already registered for that operation.
No public caller supplies a cheaper role or an admission-success flag.

Read-only results and already closed searches do not create new history.
Malformed identifiers cannot authorize an operation. In particular an
unknown install/proof identity cannot become an arbitrarily large retained
attempt string. The ordinary event protocol remains separate: it has a
finite registered observation schedule and terminal failure semantics, and
target ingress must remain prepaid before prediction returns. This change
never adds an after-target admission gate that could unread a revealed label.

`ResourceLedger.charge_work` validates the complete debit before changing any
ledger field. If the control charge cannot be paid, the public operation
returns UNRESOLVED with no new owned identity (or raises `ResourceExceeded`
for a void cancellation/retirement operation). It changes no revision,
candidate, search, persistence, query, observation, error allocation, buffer
or resource history. This is verified on the current public endpoints.

If the charge succeeds, every following operation still pays its own
registered work/residency. Failure after admission retains its attempted
identities, actual costs and history. Even when only the admission unit fits
and construction inspection immediately fails, that failed attempt remains
recorded. Cleanup inside an already admitted action does not start a new
external admission. This is a new registered machine cost protocol, not an
assertion of behavioral equivalence to the old free-history implementation.

## 3. What the positive charge proves

Let W_r be the remaining immutable cumulative work allowance of role r at a
registered boundary, and let K_r count subsequently admitted public Compiler
control requests charged to that role. All other work debits are nonnegative,
and no cancellation, failure or install refunds prior work. Therefore

`K_r <= W_r / c`, with `c=1` in machine v2.

Every public Compiler request that changes owned state must first have such
an admitted charge; cached reads and refused admission preserve the owned
state. Consequently the historical infinite sequence of zero-price owned
control mutations is impossible. The same argument applies across CPU
installation because its prepared ledger preserves cumulative work exactly.

The statement is about admitted control requests in the registered machine.
It is not a bound on external caller activity, refusal-processing CPU time,
arithmetic scratch, garbage-collector/allocator state or complete process
memory. An admitted request can create multiple internal records. Their
storage and ingress still require complete physical accounting.

There is also a concrete authority consequence. A refused request cannot
invalidate a current reference-class proof by changing the revision or
minting an unexecuted shadow. The audit completes a 35-program class and
then makes 16 unfunded construction requests. The same owned current proof
remains valid throughout; no proof token is rebuilt or widened.

## 4. The remaining one-request ingress counterexample

Positive admission is necessary here, but it is not sufficient for a complete
memory bound. The present raw revealed-input interface can receive an exact
rational before its reference arithmetic guard runs. On a source box [0,1],
choose input `1/2^m` and reference integer work limit 128. `predict_next`
first places the raw input in its pending record, then the guard returns
UNRESOLVED and halts. For m=256,1024,4096, the halted state retains denominators
of 257,1025,4097 bits without increasing its charged work or packed payload.

These are range-legal inputs that the current arithmetic cannot process.
The code honestly halts and issues no successful prediction or certificate;
it does not claim the oversized input was unread. However, their retained
storage is outside the current payload measure. Even a single admitted
ordinary event can therefore defeat a proposed total-memory bound based
only on the present counters. This **current unclosed counterexample** is
kept separately from the corrected historical control-loop failure.

The next physical implementation must account for input representation,
partial ingress and terminal diagnostics before claiming a complete cap.
Merely moving a check after the object has been retained, deleting the
revealed value, casting it to lower precision, or rejecting the whole legal
semantic source class is not a solution. The information/physical interface
must establish which bits were legally received and where they remain owned,
with UNRESOLVED when its actual acquisition budget is insufficient. General
CPython metadata/temporaries and the full ERC-1 manifest remain obligations.

## 5. Executed evidence

Run `python -B scripts/audit_control_admission.py --write`.

- Historical witness: 64 unfunded requests at work cap 18, adding 64 candidate
  IDs, 64 owners, 192 resource events and 64 attempts with unchanged counters.
- Current admission: 11 public paths, 64 denials each, all owned snapshot
  coordinates unchanged under actual immutable role caps.
- Exact finite command class: every length-four word over construction and
  retiring the newest live shadow, at each of six extra-work caps
  {0,8,16,24,32,40}; 96 trees, 384 positions, 177 state-changing requests,
  each preceded by positive paid admission. Retirement with no shadow is a
  declared no-request position in this audit driver.
- A completed 35-program current proof survives 16 unadmitted requests.
- Three oversized raw-input prefixes reproduce the distinct still-open
  ingress/diagnostic storage problem under machine v2.

The compact artifact is
[`FP_CONTROL_ADMISSION_AUDIT.json`](../../evidence/minimal/FP_CONTROL_ADMISSION_AUDIT.json).
The ordinary/profile/search, reference/paired persistence, construction and
two-cycle CPU installation audits are rerun against the changed machine.
Their numerical/decision-class conclusions remain scoped as before; paid
retirement and install admission are now included in their cost assertions.
No historical 47/47 release count or full physical freeze is inferred.
