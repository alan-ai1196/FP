# Delegation requires a stable referent and private accepted results

Current implementation note: [singleton-plan elimination](SINGLETON_PLAN_ELIMINATION.md)
supersedes the fixed Runtime's redundant proposal interfaces. The law and
historical source-bound evidence below remain; current CPU checks and all
fifteen new actual gate jobs pass atcdea7db. Do not apply retired-port probes to the new
implementation as though those ports were still authoritative.

Status: **proved component law; implemented for reference prediction
delegation; exact CPU audits and all ten actual CUDA A1 jobs pass**.
The broader indexed helper/continuation boundary remains HOLD. This is an
implementation refinement of Foundation R4, not a new semantic action,
resource optimum, statistical certificate or complete Runtime release.

## 1. Agreement has an input premise

Let x be the actual complete native predecessor and causal input. A check
between a reference output r(x') and a physical output a(x') bounds only
their discrepancy at x'. In any output metric d,

    d(a(x'), r(x)) <= d(a(x'), r(x')) + d(r(x'), r(x)).

The second term is not a numerical rounding error. Agreement, even exact
agreement, supplies no bound on it when both paths have lost the actual
input. The [owned source counterexample](INDEXED_INPUT_ALIAS.md) realizes
precisely this case: both paths use the altered context and both learn the
wrong count. Tightening an AMP tolerance cannot repair that premise.

Likewise, an equality test against a record that the producer can rewrite
does not establish equality with the record that existed before the call.
This applies to inputs, resource declarations, operation plans and old
accepted evidence. Full byte preservation only fixes the referent supplied
to that particular byte operation.

The useful condition is **continuation stability of the comparison's
referent**. Its semantic meaning and retained representation must survive
every delegated continuation in the claimed fault class. A frozen Python
dataclass alone does not establish this condition.

## 2. Component frame and refinement law

Consider a serial owner holding complete native state S, received context e,
accepted history H and its resource ledger. The owner has a fixed trusted
native executor K and a predicate V for a proposed execution description p.
Assume:

1. Before delegation, the owner retains the actual input and prepays the
   declared admission/planning work. Failure never refunds executed work or
   removes received context.
2. The delegate receives a bounded closed immutable value describing its
   permitted input. It has no capability to mutate S, e, H, the ledger or
   the checker. No owner closure, iterator, bound method, record or mutable
   child of a record crosses this boundary.
3. The owner validates a bounded value result and reconstructs accepted
   records in a private object graph. Mutable result objects retained by
   the delegate cannot reach that private graph.
4. V uses the private input. For every admitted p, K(S,e,p) refines the
   declared native operation. The trusted executor receives private inputs
   and cannot be replaced by the proposal producer. Numerical execution is
   paid before K is entered.

Then every finite sequence of such delegations has both properties:

* **Frame property:** delegation alone cannot alter the native predecessor,
  actual input or earlier accepted records, whether it succeeds, returns
  invalid data, raises or exhausts its declared allowance.
* **Accepted refinement:** every published successor/forecast is the native
  result for the owner's actual input; every rejected proposal leaves that
  predecessor and accepted history intact. Retained ingress, failure records
  and spent resources are the separately authorized changes.

Proof: a closed immutable value contains no mutable reachability edge into
the owner. Writes to the delegate's fresh local records therefore cannot
change the owner graph. Bounded reconstruction introduces new owner records
whose mutable descendants have no edge back to delegate-retained objects.
Thus the frame property survives this call and every later call. A refusal
publishes no native result. On acceptance, V's refinement implication for
the stable actual input and K gives the native result. Induction on calls
proves both properties. Allocation or resource failure occurs before
publication and cannot create an alias into the prior graph. This is not
a rollback theorem for arbitrary process crashes or concurrent execution.

These are sufficient conditions, not a claim that immutable value exchange
is the only possible implementation. An independently checked transaction
or a stronger isolation mechanism can establish the same frame premise.
Nor is syntactic value-only input alone enough: the numeric refinement
premise cannot be dropped.

## 3. Copying and after-call equality do not establish refinement

A new exact witness makes that distinction concrete. Start with n3 counts
(0,0,1), cursor1, steps1 and query(1,2). Copy the complete prediction plan.
An executor changes only the copied before-count to(0,0,-1), calls the honest
exact kernel, then restores the copied count to(0,0,1). Its returned before
record aliases that copied count and is now restored too. Every copied input
coordinate agrees with its pre-call immutable value; returned before/query
agree with the actual input. The returned forecast remains9/50, while the
actual native forecast is41/50.

The witness does not corrupt the owner, so copying has proved its frame
property. It has not proved numerical refinement. No exact kernel was
modified: the untrusted wrapper simply ran it on another local argument.
Therefore a design that copies inputs and repeats metadata comparisons,
while retaining an arbitrary numerical delegation, is insufficient.

The repaired reference path deletes that unnecessary numerical delegation.
The old `IndexedReferenceMachine.execute_prediction` remains a passive
arithmetic convenience; Runtime no longer calls it. The private fixed exact
kernel executes once, after a metadata proposal has passed independent
reconstruction. Replacing that private kernel, owner or checker lies outside
the component fault model, just as replacing the canonical serializer lies
outside the byte-only compressor's claim. No general Python attestation is
claimed.

## 4. Concrete indexed realization

`indexed_values.py` implements a closed exchange algebra: exact None,
bool, int, str and recursively finite tuples. Tagged tuples encode a fixed
registry of four indexed records: counts, prediction plan, projected plan
and block. Decoding accepts no arbitrary class names, mappings, lists,
callbacks, subclasses or rational objects. Metadata needs no Fraction;
excluding it avoids reliance on copying its mutable Python internals.
Extra dataclass attributes, foreign constructors, rational objects,
excessive integer/string widths and excessive depth/aggregate traversal
refuse before acceptance. Exact type equality rejects bool/int collisions.

Runtime validates the complete categorical source interface and resolves
the actual query before delegating. The packet retains every D=n(n-1)/2
signed count, pending status, cursor and optimizer-step count, plus the
query and numeric allowance. Only committed states reach this port; their
gradient tuple is definitionally empty. The helper recreates its own machine, schema,
rules, source dictionary and native state from that packet. Even its bound
machine is a fresh local record. Its returned plan is frozen and then
reconstructed privately before validation or retention.

This query representation does not quotient the learner or discard
received source information. For the registered fixed one-hot categorical
domain, n and the ordered pair determine the entire native source row.
The original ObservationRecord and full native count vector remain owned.
Future queries and learning still use all coordinates.

The owner checks the full before state, exact query and integer allowance.
It reconstructs the complete projected plan from those private inputs and
compares exact recursive types and values. The existing query projection
theorem proves the trusted exact execution's native refinement. A helper
that poisons then restores its local counts can at most supply a valid plan
for the actual input; it cannot supply the forecast. A helper's later writes
to an earlier plan or local machine cannot change accepted history.

The delegated planning boundary trusts the closed bounded reifier, owner,
independent plan checker and fixed exact numerical kernel. The fault class
allows arbitrary writes to supplied local records, returned local records
and their later retained aliases. It excludes stack inspection, owner or
module globals, class replacement, arbitrary process-memory access and
concurrent execution. Public snapshot mutation and other reference/AMP
helper surfaces are **not** covered by this scoped claim.

## 5. Work, storage and refusal scope

Each value walk has allowance L=128(D+n+16), depth16, string length128 and
integer width max(63,min(reference_bits,32768)). The fixed decoder still
uses at most32768 bits even when the nominal reference declaration is larger;
the adapter accepts such larger declarations. The registered block path satisfies
SUM_b(|V_b|-1)<=n-1, so every ordinary full count/plan packet fits this coarse
linear allowance without erasing unused counts. The aggregate guard also
bounds traversal of malicious results; failure is not a partial success.

The metadata debit, paid before packet preparation or helper entry, is now

    64*(n+1)^2*(D+n+1) + 2048*(D+n+16).

Its second term is16L and covers the bounded input/output value walks,
fresh fixed declarations, private plan conversion/comparison and fixed
record constructors. The first term retains the two full metadata planning
passes. Primitive integer/GCD bit complexity and interpreter heap remain
outside this declared logical work metric, as in the preceding reference
contract. The numerical debit remains

    32*(n+1)*(P+S) + 64*(D+8) + 64.

There is one exact numerical execution, no duplicated native evaluation.
Actual retained packed buffers keep their existing leases. Temporary value
graphs are interpreter workspace, subject to the actual job envelope during
CUDA probes; no dummy buffer is allocated or claimed to account for them.
There is no total-memory, physical-time or new feasibility lower bound.

## 6. Evidence and remaining boundary

`audit_indexed_value_boundary.py --cpu` retains:

* the exact poison/restore counterexample to the rejected copying-only rule;
* all2048 schedules of a two-bit input/one-bit target heap model, across
  four input/output sharing topologies. Only isolated input and isolated
  accepted output have zero input/history/refinement failures;
* all759 ternary count states through n4, with distinct reconstructed native
  records, plus12 malformed/resource refusals, exclusion of Fraction objects
  and a65536-bit nominal declaration with the fixed32768-bit decoder;
* six actual CPU Runtime cases: source/count faults and a raising helper
  refuse with intact predecessors; restored metadata and later retained
  aliases preserve native results; the retired executor receives zero calls;
* an unfunded proposal attempt with zero helper calls, retained actual
  context, no target and no prediction publication.

The finite heap model is exhaustive only for its explicitly stated finite
bit/write schedule. It is not an exhaustive Python or complete Runtime
certificate. Every successful Runtime continuation is checked against the
independent literal learner, including its full native parameter state.

Ten fresh4-GiB/900-second CUDA jobs are registered: the six fault/continuation
cases, global and projected profiles, projected n256, and projected fresh
installation followed by learning. All
execution dependencies must be committed before launch; source remains
fixed while live, and every outcome is retained. Refused reference proposals
must not enter AMP; successful cases must preserve all old sealed metadata,
pass full phase readers and learn the literal native update. The actual
results are given below. The full indexed Runtime regression also passes all388
two-event histories/776 native phase comparisons, profiles, n256, fresh
reference persistence and finite empty-policy closure. The projection audit
passes all1098 supports/10650 path checks and11919 complete native cache
comparisons, all seven still-active proposal substitutions and four numeric
preflight refusals. The two former result-substitution tests belong to the
retired numerical delegation; the new audit checks that port is never called.
These source-specific reports are retained separately from older evidence.
Other native/physical helper argument surfaces still
need the same frame/refinement analysis before the indexed extension can
leave HOLD. Paid order search has not begun.

## 7. Actual CUDA A1 result

`FP_INDEXED_VALUE_BOUNDARY_CUDA_A1.json` retains all ten fresh jobs at
da532dc7ce001f4943b84013134e4257edcbdcd0. All are terminal with exit0,
attachment before their first instruction, no timeout and no limit
termination. Maximum job commitment is2,357,059,584 bytes, below4 GiB.
Every execution dependency remained committed and fixed while live.

The source/count mutations and raising planner refuse before a new AMP
phase. Each preserves the actual context, unrevealed target, native
predecessor, earlier snapshot and four old sealed records. The restored
metadata and later-retained-alias cases execute the correct native input,
learn the complete literal native update and preserve historical frames.
The retired numerical helper receives zero Runtime calls. The six cases
check34 full phase records in total.

The four integration jobs check230 more complete records and independently
check4416 floating words, including144 half words. Global/projected profiles
check58 phases each. Projected n256 checks34 phases/514 words with world
builders disabled. Projected fresh evidence crosses at20, installs with
alpha1/2 retained and learns to21; its80 phases and1258 words pass. There is
no historical selection proof or complete optimization-class claim.

All264 phase records pass their full byte readers; earlier sealed metadata
does not change. The journal field `private_planning_work_paid` records the
whole prediction-phase deployment debit: on successful CUDA calls it also
includes numerical/retention work. It is not an isolated planning-cost
measurement. No time/memory dominance is inferred.

This actual gate closes the registered reference prediction delegation
fault class. It does not close the other native/physical helper surfaces,
public snapshot mutation, or arbitrary Python faults. The broader indexed
extension remains HOLD until those continuation interfaces are addressed.
Do not rerun these terminal jobs without a substantive change.
