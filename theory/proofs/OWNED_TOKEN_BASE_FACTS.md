# Reuse declared token invariants without weakening arithmetic guards

Status: **CONDITIONAL PRESERVATION THEOREM; IMPLEMENTED, DEFAULT OFF**.
This concerns the ordinary token Runtime under frozen Foundation/ERC. It
changes no SUM/PRODUCT semantics, G, Gamma, U, physical precision, source
interface or observation. There is no new architecture action, class
completeness certificate, persistence authority or installation path.

## Why the final value is insufficient

The original exact `token_execution.total` adds Fractions in declaration
order. Each addition first checks the operand integer widths, then a
conservative upper bound on the raw rational operation, then the result.
Those are part of this registered solver's decision class.

For positive operands 1/3 and 2/3 the final sum is 1 and needs only one-bit
numerator/denominator integers. Nevertheless this fold refuses allowance 4:
the second operation's preflight requires 5. Replacing the original fold by
its final value and checking only that value would silently accept a case
the registered work model cannot close. This is a counterexample to that
shortcut, not to FP. Different exact arithmetic can have a different work
contract; it cannot silently borrow this one's certificate.

## Exact guard-profile theorem

Let x_1,...,x_n be a finite tuple of exact Fractions, s_0=0 and s_j=s_(j-1)+x_j.
For each step, let a,b be the numerator/denominator bit lengths of s_(j-1),
and c,d those of x_j, using `int.bit_length` including its value 0 for zero.
The original preflight bound is

    u_j = max(a+d, c+b, b+d) + 1.

Define R as the maximum of all operand widths, all u_j and all result widths.
For an empty fold R=0. For every positive integer allowance L, the original
ordered fold completes **if and only if L >= R**, provided the trusted exact
integer operations themselves complete. Its answer is s_n. Unbounded
allowance `None` yields the same value. This is a threshold for the *declared
conservative guards*, not a universal lower bound on summation memory.

Proof: every executed guard is one inequality included in the maximum.
If L>=R, induction completes all steps with their exact s_j. If L<R, choose
the first guard that exceeds L; preceding successful steps have the same
exact values, so that guard refuses. The definition includes result guards
explicitly and does not assume away cancellations. The implementation
`guarded_fold` runs the original `_operation` with the actual supplied cap;
it never temporarily raises the integer allowance to discover R.

The owned fact is produced only by a successful fold. A later request on
the identical immutable tuple may return s_n when L>=R or L is `None`.
Smaller and malformed allowances follow the original operations, preserving
the original first exception as well as refusal. An equal but different
tuple is a miss. In the owner the source is also checked to have at least
two strictly positive exact Fraction entries, so its positivity validation
can be reused under the same binding. Every other Spec field is revalidated.

The decision class is exactly these two operations on one supplied immutable
tuple: positive-base validation, and the existing ordered guarded sum. It
does not cover mutable containers, arbitrary reductions, future observations,
different arithmetic, new compiler decision classes or a whole model's
validity. Summing that same tuple for the native binary64 kernel is also
exactly preserved, since both paths supply the identical Fraction to its
existing interval constructor.

## Complete ownership and scope

`SharedReferenceContract(token_invariant_bytes=C)` registers a single optional
token base fact, default C=0. It stores the complete original base tuple,
exact sum and guard threshold. The fixed base belongs to the declared model,
not to a trained endpoint or observed data. No source/target or learned slot
is cached by this mechanism. No public Runtime method accepts a supplied fact.

Construction prepays 128C plus 256 times the source/table metadata allowance.
It performs a bounded source walk, the original positivity check and the
guarded fold. The complete typed fact must fit C and the original integer
allowance. Actual scratch and immutable byte extents are admitted before
allocation in both compiler and deployment roles. A fresh independent
canonical traversal checks the copied bytes before publication; both copies
coexist until then. A failure retains admitted partial extents and publishes
no live Runtime. The full-process/job host cap continues to cover Fraction,
context, tuple, table and temporary Python allocations. The tariff is a
primitive-work allowance, not a bit-time or whole-heap theorem.

The private fact keeps a strong source reference and requires `is` identity.
The source is an exact tuple of exact Fractions, immutable under their ordinary
value APIs in the existing closed-value model. No frozen dataclass wrapper
is itself trusted: replacing its `base` field gives a miss; an invalid
replacement is checked normally. A changed feature count, learning rate,
grid or unit is still checked. Snapshots expose builtin value data and the
paid byte identity, never the mutable private fact object. The artifact,
role leases and complete fact occur in the normal resource/buffer/archive
snapshots. Its lookup contains no digest and retains no independent truth.

An owner operation selects its fact in an isolated Python context. The
selection is read-only. A nested disabled owner explicitly masks the outer
fact, and a different owner selects its own. Calls outside such an operation
execute the original validation/sum. The context is disposable call workspace;
it cannot survive as an unrecorded numerical cache between legal Runtime
operations. Initial construction uses the same scope for its registered
native/Gamma/physical checks. Each newborn still executes Gamma independently.

### Allocation failure during scope cleanup

The draft `ContextVar.set/reset` context manager was rejected during source
review: `reset` can call allocating HAMT update routines. The implementation
instead uses `copy_context().run(...)`; the copied context receives the new
binding and the parent is restored by `Context.run`. In the actual pinned
CPython 3.12.9 source, `context_run` calls `_PyContext_Exit` after the callback,
including its exception path, and that exit restores the parent pointer
without constructing a HAMT path. This implementation premise is scoped to
the registered interpreter, not a claim about arbitrary Python VMs.
See the [primary CPython source](https://github.com/python/cpython/blob/v3.12.9/Python/context.c#L613)
and its [context-exit implementation](https://github.com/python/cpython/blob/v3.12.9/Python/context.c#L131).

The audit injects failure before context copying, after setting the isolated
binding and during an actual post-target Runtime observation. It checks
parent restoration, retained target and the original terminal host-failure
boundary. No allocation-heavy cleanup or scope reset is added after learner
publication. Fatal process loss still grants no continuation authority.

## Preservation and resource limits

Under those premises, every hit equals the original operation's successful
value or validation result; every miss executes the original path. Induction
through the existing phase executor therefore preserves native forecasts,
observations, interval endpoints, physical primitive words and complete
phase bodies. All live device reads, primitive checks, lineage, old learner
publication, fresh evidence and installation restrictions remain unchanged.
The new manifest, fact bytes, resource ledger and snapshot metadata correctly
differ. Added work/memory can cause a resource refusal, so this is not a
same-budget feasibility dominance theorem.

The original phase work fees remain conservative; only the extra fact
construction work is added. For N subsequent identical-tuple validations and
folds, source scanning/folding is paid once at admission instead of being
executed N times. The hot lookups use constant metadata work. There is no
corresponding claim that the entire Runtime becomes linear, that all model
validation disappears, or that retaining/freshly checking a long physical
history is now affordable.

## Evidence and experimental boundary

`scripts/audit_token_base_facts.py` checks 2,801 small tuples and 27,162 exact
guard decisions against the original operation, including signed values,
zeros, cancellation and positive bases. It retains the final-value shortcut
counterexample. Nineteen paired complete Runtime histories preserve 318
phase bodies/12,853,318 bytes and 117,355 checked primitive words, complete
learners, old snapshots and native/physical reports. Profiles and independent
batch commits remain. The composed native solver is included in one pair.
Hot positive-base checks and guarded base additions are 10,192/676 originally
and 0/0 with the owned fact, after its separate admission. These are finite
toy counts, not full-vocabulary timing.

The controls also cover distinct/equal tuples, changed public wrappers,
different and disabled owners, malformed/tight integer allowances, snapshot
replacement, failed context allocation and post-target MemoryError. Capacity,
unpaid-work, corrupted-writer and post-write allocation failures refuse before
publishing a Runtime. The minimal artifact is `FP_TOKEN_BASE_FACTS_CPU.json`.
CPU substitution supplies no actual CUDA authority or model-quality result.

The default prefix-cost and token-owner controls also pass. Current host
failure ports, prefixes and actual Windows allocation-exhaustion controls
pass separately. The legacy host audit's aggregate command stops in its
historical-source fixture: its old ConstructionContract does not accept the
later `indexed_order_search` field. That historical replay was not repaired
or counted as a passing regression in this change.

## Fixed first CUDA comparison

`scripts/run_token_base_facts_cuda_a1.py` is registered before its first launch.
It opens only the already declared first 1,024 training bytes and uses the
original first 16 targets. Two fresh workers run in order `original`, then
`owned-facts`, each inside a preattached 240-second/16-GiB Windows job. The
existing V=50,257, L=512, D=4, K=8, unit=512 resource-test model is unchanged.
Both keep the 1-GiB arena/reservation, 2-GiB reference payload, 64-MiB phase
frame, 2^22 output-cell bound, 4,096 exact-cell bound, state tolerance 16,
probability/division tolerance 10^-6 and 64-MiB canonical-image allowance.
Fresh-read grouping, composed native bounds and region reuse are disabled.

Only the owned worker declares a 4-MiB token-invariant allowance. The pure
full-vocabulary factory, without corpus access, gives an exact sum of 1,
guard threshold 33 and a complete 1,407,321-byte fact body. The worker checks
that same body and both ownership roles after its ordinary trace. Artifact
construction is timed separately from the 32 ordinary calls; neither timed
arm uses an inner-call profiler or arithmetic counter wrapper.

Both workers must preserve 33 checked phases, every original context/target,
the original pending count and no optimizer commit. All independent native
checks, fresh live-array reads, primitive checks and resource limits remain.
After timing, the owned worker zeros its first actual live leaf and must
retain a failed next phase with the changed words, old sealed record, old
learner and cursor, without a successor or new tensor allocation.

The exclusive `FP_TOKEN_BASE_FACTS_CUDA_A1.json` records the clean committed
source and original process/device evidence. Commit before launch; never
replay a terminal or partial journal, raise a failed cap or replace a failed
worker. Compare the total ordinary-call time in this single ordered pair.
Even a successful reduction establishes no statistical/general speedup,
full-unit benefit, sustainable training budget or language quality. Close
this qualification at its original outcome; further work must address the
remaining ordinary-token cost on evidence, with the rational/relation branch,
Foundation and ERC closed.
