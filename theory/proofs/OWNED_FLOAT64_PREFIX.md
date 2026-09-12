# Owned finite reference/binary64 execution prefixes

Status: **scoped implementation relation and finite-prefix induction.**
This applies to the registered checked CPU binary64 backend. It is not a
whole-future numerical theorem, an AMP/device bridge, a complete Runtime
freeze or an installation authorization. No Foundation semantic action is
added.

The normative obligations are [FP_THEORY.md II, XIV--XVI](../../FP_THEORY.md)
and [ERC-1 sections 2--5](../../EXPERIMENT_RESOURCE_CONTRACT.md).
[EXECUTION_AUTHORITY_BOUNDARY.md](EXECUTION_AUTHORITY_BOUNDARY.md) explains why
endpoint equality and a signer do not establish execution reachability.
This document derives the numerical relation for a prefix whose construction,
ordinary events and authority are actually owned by Runtime.

## 1. Two executions and one fixed numerical contract

The exact reference learner executes its registered positive native program,
delayed transitions, event-local gradient and mean projected-SGD commits in
guarded rational arithmetic. Its finite counterpart is a separate learner
implemented in [float64_learner.py](../../src/reference_compiler/fp_reference/float64_learner.py).
Every finite scalar cast, ordered SUM/PRODUCT operation, division, gradient
operation and optimizer operation runs through
[Float64Arithmetic](../../src/reference_compiler/fp_reference/binary_arithmetic.py).
The backend checks each actual CPU binary64 output against its exact
nearest/ties-even, gradual-underflow oracle, preserving the sign of zero.
It does not cast an already-computed exact gradient or optimizer endpoint
and call the result finite execution.

The immutable `Float64Contract` in
[float64_bridge.py](../../src/reference_compiler/fp_reference/float64_bridge.py)
fixes the backend identity and two exact nonnegative tolerances:
`state_atol` and `probability_atol`. Neither can be selected after looking
at an observed numerical discrepancy. The contract's backend ID is fixed by
the implementation, not supplied as a caller-selected string.

`Float64Value` retains the actual 64-bit encoding. Fraction decoding supplies
the exact numerical value used in the comparison; it does not replace the
physical state. In particular `+0` and `-0` have the same rational value but
different retained encodings. Rejecting nonfinite encodings and preserving
dtype/zero-sign/rounding semantics prevents a numerical relation from
silently erasing those physical coordinates.

Initialization must execute the registered construction path. An initializer
cast, a paid sequence of profile events and an explicitly registered
full-state transport are distinct provenance. A rounded trained endpoint
cannot be relabelled as having executed a missing finite profile trajectory.
The finite trajectory must not be reset to a rounded exact state after every
event: that would test repeated recasting, not the registered learner's
own accumulation of arithmetic error.

### 1.1. Exact scalar rounding and actual execution

For a nonzero exact rational x, let `e=floor(log2(abs(x)))`, precision p,
normal exponent limits `[emin,emax]`, and `s=max(e,emin)-p+1`. Divide exactly
`abs(x)/2^s=N/D`, with `N=q*D+r`, `0<=r<D`. Increment q iff `r>D-r`, or
`r=D-r` and q is odd. Multiplying that integer by `2^s` and restoring the
sign gives nearest/ties-even rounding, including subnormals and binade carry.
The adjacent values share this grid; nearest integer choice and even parity
at the midpoint prove the rule. A rounded result above the maximum finite
value is UNRESOLVED, never saturation. Optional output flushing occurs after
this rounding and is a different registered format policy.

All scale construction, quotient inputs, signed arithmetic and comparisons
are guarded before oversized exact work. The binary64 executor preflights
its complete raw decode representation before constructing a denominator.
It retains a separate zero-sign coordinate: exact cancellation under this
rounding gives positive zero, addition of two negative zeros gives negative
zero, and multiplication/division retain operand-sign XOR. An exact rational
zero alone cannot check these rules.

`Float64Arithmetic` executes actual CPU operations and compares their raw
outputs to this oracle. Each phase must complete its registered scalar-call
schedule; merely returning a close endpoint is insufficient. The floor-grid
optimizer operation separately clears low raw significand bits and checks
the resulting floor. It is not confused with nearest rounding. Python's
[floating-point documentation](https://docs.python.org/3/tutorial/floatingpoint.html)
describes the host representation; the per-operation check is still required.
This CPU schedule does not establish GPU FMA, parallel SUM or input/output
FTZ behavior, which have their own
[PTX operation rules](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html#floating-point-instructions-add).

## 2. The complete learner-state relation

For one fixed native program and lineage, `check_state` requires exact
correspondence of the discrete `cursor`, `unit_count` and `optimizer_steps`
coordinates. It checks the complete shapes and maximum absolute numerical
error of:

- every persistent parameter slot, including unused slots;
- every coordinate of the signed partial gradient accumulator;
- every element of every delayed queue, with the same queue IDs and order.

The maximum of these errors is `state_error`, which must not exceed
`state_atol`. Parameters and delayed values remain nonnegative. No current
read-head match substitutes for checking a delayed queue's tail. No current
prediction match substitutes for checking the partial gradient accumulator:
either omitted coordinate can affect a later legal event.

The helper checks two passive records; it does not know whether they were
initialized, profiled or reached by an ordinary event. The graph, source
interface, observation identity, learner specification and current
microtransition must additionally be bound by the owned Runtime execution.
A matching pair of caller-written dataclasses supplies none of those facts.

## 3. Stored masses and rounded output are separate

For one sealed prediction, write the exact reference masses and normalizer
as `M^r` and `T^r`, with `p^r_y=M^r_y/T^r`. Decode the retained finite
masses, actual rounded normalizer and actual final-division outputs into
exact rationals `m_y`, `t_f` and `p_out,y`. Define independently

\[
S=\sum_y m_y,\qquad p^m_y=m_y/S.
\]

`p^m` is the mathematical probability vector defined by the stored masses.
In general `S` differs from `t_f`, and `p_out` need not sum to exactly one.
Displayed equality to `p^r`, or a displayed sum of one, therefore does not
establish the relation of the underlying masses. ERC-1 explicitly requires
this distinction.

`check_prediction` verifies both record shapes and the complete registered
delayed interface. It requires nonnegative native values and positive
masses/normalizers, and puts each reference and raw finite output probability
in `(0,1]`. It checks the reference record's exact base-plus-excess masses,
mass sum and normalized probabilities. Both the exact sum S and actual
rounded `t_f` must obey the normalizer cap. Every executed native activation
and predicted delayed coordinate must obey its registered cap.

The reported errors have the following precise definitions:

| Field | Maximum absolute discrepancy |
|---|---|
| `native_error` | Corresponding native-node values, excesses, masses and complete predicted delayed queues |
| `normalizer_error` | `T^r` versus `t_f`, `T^r` versus S, and `t_f` versus S |
| `probability_error` | `p^r` versus `p^m`, and `p^r` versus `p_out` |
| `division_error` | `p^m` versus `p_out` |

Native and normalizer errors must be at most `state_atol`; both probability
errors must be at most `probability_atol`. These are checks against the
current independent exact trajectory, not an unproved transitive chain of
approximate equivalences.

All differences, normalizations, maxima and decision-critical comparisons
use guarded exact arithmetic. A comparison whose integer cross-products do
not fit is unresolved even when an unbounded backend could decide it.
No arbitrary epsilon separates overlapping or unaffordable calculations.
The helper checks the observed prediction context. It does not establish
finite-backend accuracy or feasibility on all other contexts.

## 4. Induction over owned microtransitions

The following are execution obligations, not facts inferred from a passive
`Float64Relation` object.

1. Runtime owns the initial complete exact/finite pair and checks its
   registered construction and state relation.
2. Each next microtransition consumes exactly the current recorded pair,
   graph/source identities and phase. The two registered implementations
   execute it; the caller cannot submit a replacement successor.
3. Before every score the full state relation holds. Both predictions
   complete and are sealed before the target is accepted, and their
   prediction relation is checked.
4. After target-driven observe, the relation holds on the new delayed
   queues, gradient accumulators and ordinary clocks. If the registered
   update unit commits, the post-commit state is checked as a further
   required phase.
5. Only a successfully checked actual successor becomes the next certified
   prefix endpoint. A skipped phase or failed relation ends that identity.

The base case is the checked construction. Inductively, consuming the owned
current pair, executing the required operation and checking its successor
establishes the relation at the next required phase. Therefore every phase
of an accepted finite prefix satisfies its registered tolerance. Direct
comparison captures the accumulated error of the two actual trajectories;
an a priori error-propagation bound for the whole future is unnecessary for
this scoped conclusion.

This proof does not certify unexecuted future steps. At a horizon H it can
report that all H actually completed events passed, or the exact shorter
prefix before failure. It cannot announce H-event success at initialization.
Prediction/observation/commit phases retain their distinct clocks: a score
does not consume a target, an observe advances the ordinary cursor once,
and an optimizer commit does not advance it again. A persistence epoch can
end at a partial optimizer unit; that does not erase its accumulator or
grant a structural installation boundary.

## 5. Failure, resources and authority

Numerical overflow, NaN/Inf, an invalid range, an exceeded registered
tolerance, an unaffordable exact check or a missing phase prevents the
prefix from extending. A later coincident endpoint cannot revive it.
Runtime retains actually revealed data, real execution/provenance, work and
peak costs, and the physical states or temporary buffers required to audit
the failed operation. A post-target failure cannot unread its target or
return old statistical wealth to active use.

`relation_work(program,rules)` is a conservative fixed reference primitive
charge for one complete check, paid before invoking it. Operand sizes keep
their independent integer limit. This allowance is not a measurement of
total CPython heap, bit-time, byte-time, device memory or elapsed work.
Retaining both learner trajectories, numerical evidence and their actual
owned buffers is part of the enclosing resource contract. Numerical
agreement cannot provide a free object copy or justify freeing the incumbent
before construction succeeds.

In the current partial payload model, an evidence allocation failure leaves
only a terminal diagnostic if its state cannot be retained. Such a row cannot
remain marked CHECKED. Interpreter temporaries, total host heap and complete
physical failure accounting remain open; no complete-resource claim follows
from this prefix relation.
If an unexpected execution failure precedes the retention failure, both
causes remain in that diagnostic. A secondary resource failure cannot
downgrade the already observed execution failure to numerical uncertainty.

`Float64Contract` and `Float64Relation` are passive data. The module has no
signer, no proof-token registry and no install operation. A Runtime
authorization, if supplied later, must separately bind the exact live
executed prefix, required proposition and state. The historical endpoint
signing counterexamples remain excluded by that execution boundary, not by
the numerical tolerance calculation itself.

## 6. What this does not prove

This is a deterministic checked CPU binary64 implementation relation.
One observed output from an unrecorded nondeterministic GPU reduction does
not prove its transition kernel. Foundation XV still requires explicit
RNG/state coordinates, a pathwise relation covering legal nondeterministic
transitions, or a stated probabilistic coupling theorem for that backend.
There is no GPU execution or AMP certificate in this result.

The probability relation also supplies no statistical persistence authority.
Reference and physical paired gains remain respectively
`L_dep_ref-L_cand_ref` and `L_dep_physical-L_cand_physical`. Each lineage's
proved CE error would contribute to the paired-gain error; reference wealth
cannot simply be copied to a physical path. Exact probability tolerances
alone are not a claim to have computed those CE or statistical bounds.

In particular, an observed-context check cannot establish the whole-domain
positivity/range premise needed by a pre-context stochastic claim about a
finite predictor. Such a claim needs its own registered law and bounded
statistic, current-domain proof or explicit failure/stopped convention.
[OWNED_REFERENCE_PERSISTENCE.md](OWNED_REFERENCE_PERSISTENCE.md) describes the
existing exact-reference distinction. Nothing here infers an external
producer's law or extends that result to binary64/AMP.

Finally, Foundation XVI installation still requires the complete atomic
transition, ownership/refcount transfer, learner transport, live shadow/job
policy, error/persistence ledgers and post-install relation. A finite CPU
prefix is neither that transaction nor an equivalence of complete
self-Compiler states. ERC-1 remains the frozen specification; its remaining
Runtime and actual target-device release gates remain separate obligations.

## 7. Executed evidence

[`audit_binary_arithmetic.py`](../../scripts/audit_binary_arithmetic.py)
checks 10,232 signed small-format cases against an independent enumeration
of representable nearest neighbors, 513 actual binary64 results, 594 grid
floors and explicit underflow/overflow/zero-sign failures. It reproduces
double rounding and differing fused/separate arithmetic, without claiming
that either implements an unregistered device schedule.

[`audit_float64_runtime.py`](../../scripts/audit_float64_runtime.py) runs
64 complete three-event context/target streams with two paired lineages:
384 lineage events, 128 commits and 1,024 bitwise phase checks against an
independent direct-float interpreter. In 406 checked coordinates, actual
finite values differ from casting the exact endpoint. Six profile events
from two original observations give another 20 such differences. Sixteen
floor-grid streams, delayed queue tails, gradient accumulators, all three
readout representations, actual work/memory/integer/tolerance failures and
post-crossing failure are also checked. Minimal aggregate evidence is in
[`FP_FLOAT64_RUNTIME_AUDIT.json`](../../evidence/minimal/FP_FLOAT64_RUNTIME_AUDIT.json).
These executable checks support the implementation of the finite-prefix
argument; they are not a complete release or a model-science result.
