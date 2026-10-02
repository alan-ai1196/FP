# Retained native predictions exceed the full text host budget

Status (2026-10-03): **source/ABI lower bound proved; finite complete CPU
controls PASS; unchanged 96-GiB full-training representation infeasible**.

Subsequent [captured-value refinement](CAPTURED_TOKEN_VALUES.md) changes the
eager-allocation hypothesis and removes this selected obstruction. This proof
and its original receipt remain historical source-bound evidence; they are not
relabelled as a lower bound for the new implementation.

The [two-unit diagnosis](../../experiments/next_token/OWNED_TRANSITION_COST_A1.md)
passes every ownership and byte duty. Its small host peak does not establish
the million-target budget. A separate live-state obstruction settles that
decision without extrapolating its elapsed time or memory slope. Foundation,
ERC-1, the native update, source interface and all experiment declarations stay
unchanged. No certificate or new `CERTIFIED_COMPLETE` decision class is issued.

## 1. The source retains distinct input objects

Fix the complete ordinary native trajectory at `c67a0aa`, with its one supplied
incumbent and no additional profile or policy actions. Let T be the number of
successful ordinary events, L the registered context length, D the embedding
width and N the number of subsequent SUM/PRODUCT nodes. The original text
registration has L=512, D=4, N=8 and T=1,048,576.

`TokenReferenceMachine.predict` constructs a new `Fraction(int(q), grid)` for
each of the L D categorical embedding inputs, including padding and equal
values. `_forward` places those same objects in a new list, appends the N node
values, and returns a new tuple of length L D + N. `TokenEvaluation.values`
retains that tuple. No interning or sharing of equal input Fractions occurs.
The local CPython 3.12.9 `Fraction.__new__` allocates its instance before
processing the numerator/denominator; even repeated zero constructs a fresh
object. Numeric equality does not merge these instances.

During `observe`, the actual pre-target prediction becomes
`EventTrace.prediction`, and the Runtime appends that trace to `_event_traces`.
At an optimizer commit, `replace(trace, after_commit=...)` keeps the prediction.
The ordinary runner never removes an earlier trace. Recomputing the current
prediction for validation does not replace the recorded original. Thus the T
recorded predictions contain **T L D distinct simultaneously live input
Fraction instances and T distinct value tuples**. Garbage collection cannot
free those reachable objects. The observer is not needed to keep them alive.

This is an induction through the actual allocation/append/commit writers, not
a claim about all possible FP realizations. The audit binds the complete
relevant Runtime, token execution, token batch and original runner files to
that source. The maintained reproduction loads the actual old prediction and
activation methods and checks unchanged ASTs for their remaining token-module
dependencies; the other source files still match the original commit. Public
value copies, shared archive encoding and the new resource
indices leave this live object graph intact.

## 2. Exact selected-object lower bound

On the installed Windows x64 CPython 3.12.9 ABI, a Fraction instance has 32
object bytes and a 16-byte GC header. A tuple of length k has 40 bytes including
its header plus 8 k element-pointer bytes. The audit checks the actual type
sizes, `sys.getsizeof` and GC status. Numerator/denominator integer allocations
are deliberately excluded: small integers and equal referents may be shared.

These sizes agree with CPython's [GC header](https://github.com/python/cpython/blob/v3.12.9/Include/internal/pycore_gc.h),
[GC allocation](https://github.com/python/cpython/blob/v3.12.9/Modules/gcmodule.c)
and [tuple representation/allocation](https://github.com/python/cpython/blob/v3.12.9/Objects/tupleobject.c).
They count disjoint live allocations, without charging a referenced object
again for every incoming pointer. Allocator rounding, pool slack and all other
objects can only add storage.

Consequently the selected live allocation bytes satisfy

    H_selected(T) = T [48 L D + 40 + 8(L D + N)].

Whole-host allocation is at least this amount. With the standard CPython
Windows allocator, live small objects occupy private committed arenas;
its [arena allocator](https://github.com/python/cpython/blob/v3.12.9/Objects/obmalloc.c)
uses committed writable memory, and larger tuples occupy allocated private
heap storage. The Runtime's Windows host measure counts process commitment
through `PrivateUsage`, as defined by [Microsoft's process memory counters](https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-process_memory_counters_ex).
Paging changes residency without making those live allocations free under
the registered commitment cap. This argument assumes that standard ABI and
allocation model; it is not a portable `sys.getsizeof` theorem for arbitrary
Python interpreters or substituted allocators.

For the original full text registration:

| Selected coordinate | Exact bytes |
| --- | ---: |
| 2,048 input Fraction instances per prediction | 98,304 |
| One tuple of 2,056 values per prediction | 16,488 |
| Selected allocation per retained prediction | 114,792 |
| Selected allocation at 1,048,576 targets | 120,368,136,192 |
| Original whole-process/job cap, 96 GiB | 103,079,215,104 |

The selected lower bound is **112.1015625 GiB**, already above the entire
96-GiB allowance. It excludes integer referents, eight arithmetic-node objects
per event, trace/wrapper/list metadata, old masters, pending units, sources,
all archive/image bytes, every resource object and the interpreter itself.
Even omitting tuple headers and node pointer slots gives 112 GiB.

The selected objects alone exceed the cap at 897,966 retained events. This is
an upper exclusion on successful prefix length, **not the actual failure
cursor**: the omitted allocations and other resource/numerical/deadline duties
can fail much earlier. In particular, this theorem does not assign a cause to
the old interrupted A1 worker whose final execution evidence is missing.

The conclusion is independent of training labels, rates, optimizer unit,
integer magnitudes or useful learning, conditional on those events succeeding
with this representation. Even all-zero numerical inputs keep separate
Fraction shells. Faster serialization, archive compression and local resource
indices do not remove these live shells. The unchanged full trajectory cannot
complete under its host contract; a further launch is not needed to observe
that already proved exclusion.

## 3. Exact finite audit and deliberate sharing control

[`audit_native_prediction_liveness.py`](../../scripts/audit_native_prediction_liveness.py)
produces [`FP_NATIVE_PREDICTION_LIVENESS_CPU.json`](../../evidence/minimal/FP_NATIVE_PREDICTION_LIVENESS_CPU.json).
It runs all sixteen binary four-target words with units 1/2/4, mixed and
zero-embedding initializers, and packed/shared retention: **192 complete
Runtime histories, 768 targets and 448 commits**. They retain 4,608 distinct
input objects and 325,632 selected allocation bytes. Pre-target addresses are
preserved through observation, commits and explicit garbage collection; every
input agrees with its original causal window and committed origin.

The observer saves only integer addresses before later Runtime operations.
It obtains the final objects from actual retained traces, so it cannot create
the historical liveness it is checking. Equal-zero histories still exhibit
fresh input objects. A deliberately shared scalar/tuple control, in contrast,
has 64 input occurrences but one scalar and one tuple; the counting routine
charges each once. This blocks the false argument of multiplying occurrence
counts when the implementation actually shares objects.

A separate complete Runtime control keeps the original full vocabulary,
L/D/N, unit512, image/archive bounds and million-target declaration, using
two explicit synthetic legal labels and no corpus/report. Its 4,096 distinct
input objects represent only eight distinct numerical values and occupy
229,584 selected bytes with the two value tuples. This sample checks the
actual full-V representation; it is not a rerun of any original corpus worker,
a performance measurement, optimizer-unit result or trained model score.

## 4. Research consequence

The full-horizon budget question for this unchanged representation is closed
negatively. Do not repeat its short cost probes or launch another million-token
attempt on the assumption that smaller archive payload proves host feasibility.
The next necessary refinement is a complete recoverable live prediction/trace
representation with a proved ownership and host-size law.

An equal scalar value can potentially share immutable storage while its
distinct causal source, parameter coordinate, old origin, gradient dependency
and recorded event remain separate. Proving that separation is required before
sharing or deferred reconstruction gains authority. Truncating traces or
merging parameter slots because current values agree would not follow from
this bound. No representation improvement, speedup or affordable full run is
claimed here. Continue ordinary next-token research at this concrete live-state
obstruction; the closed relation/precision and codec branches remain closed.
