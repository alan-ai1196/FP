# A conditional trace check does not bind the declared factor addresses

Status: **EXACT PASSIVE AND ACTUAL OWNED A6 COUNTEREXAMPLE REPRODUCED**.

The A4 repair independently checks every endpoint and operation against
the supplied indexed AMP plan. A5 exercises that repaired path successfully.
The new obligation is upstream: does Runtime independently establish that
this plan is the one declared for its owned program, counts and source row?
At sourcecca2441, `indexed_cuda_prefix.execute` takes the plan returned by
`indexed_amp.prepare_prediction` and gives that same plan to the physical
executor and the independent RNE interpreter. It does not reconstruct the
factor-address binding from the owned input.

## 1. One legal observation and one altered address

Use the fixed n3 native program, uniform Gamma and unit U. After the actual
legal event(1,2,0), its committed count vector in canonical edge order is

`((0,1),(0,2),(1,2)) -> (0,0,1)`.

For the next query(0,1), the declared global AMP plan has

`support=((1,2),)` and `positions=(2,)`.

Alter only `positions` to(0,). The plan still says its active factor is
edge(1,2), but numerical execution reads the zero count belonging to(0,1).
Its nodes, query, complete predecessor, output extent and all table resource
numbers are unchanged. No numerical answer, target or trained state is
injected. The pure scalar executor and exact RNE interpreter are unchanged.

Both computations happen to produce the same complete seven-word readout:

`(1082130432,1082130432,1084227584,1084227584,1092616192,1056964608,1056964608)`.

These are excesses4,4, masses5,5, normalizer10 and probabilities1/2,1/2.
The genuine factor is off the query's path and cancels in the normalized
readout. This is exactly why output accuracy cannot establish the operand
provenance. Full native parameters and count metadata remain unchanged.

The operation sequences differ. At zero-based operation18, the declared
trace has a32-bit multiplication result1038323257, while the altered plan
has1065353216. The latter is1. The two interpreters compute different fixed
traces even though every native readout coordinate agrees exactly.

## 2. What the exact audit establishes

`audit_indexed_amp_plan_binding.py` executes both plans using exact rational
RNE word arithmetic. Passing the altered trace and altered plan to
`check_prediction_execution` succeeds, checking55 operations. Passing that
same trace with the declared plan fails. The output extent is62 cells.
The separate native state, probability and division errors are all zero,
even with zero tolerance.

There is no error in the conditional interpreter's arithmetic conclusion:
the actual words conform to the plan it was given. What does not follow is
conformance to the declared input-to-plan map. The existing fixed-forward
refinement argument needs this premise established independently before
physical execution. Treating a helper's returned plan as its own premise
does not discharge that obligation.

This is a fixed-program operand/trace binding issue. It is not a false
native numerical relation, statistical crossing or `CERTIFIED_COMPLETE`
counterexample. The source-bound A4/A5 successful observations remain valid
as reported; they do not cover an altered plan constructor result.

## 3. Actual test and repair criterion

The new `plan-binding` CUDA worker constructs the same history through
actual Runtime ingress and learning. It alters only the returned factor
address tuple. [Actual A6](../../evidence/minimal/FP_OWNED_INDEXED_AMP_CUDA_A6.json)
at783614f reproduces acceptance: Runtime publishes `PREDICTED_REFERENCE`
with `CHECKED_CUDA_PREFIX_PHASE`, despite disagreement with the independently
retained declared trace. Its seven readout words and all three native
error diagnostics are identical to the honest result. The phase checks55
operations and produces62 output cells. The final target remains unrevealed
and the learner has not advanced beyond the one actual prefix observation.

The attached-before-run job exits0 without timeout or limit termination;
its peak2,126,520,320 bytes stays below4 GiB and its deadline is900 seconds.
The raw result is1295 bytes. The worker is terminal. This falsifies the
prefix's claimed declared-plan binding at that source, while preserving
the conditional interpreter's arithmetic and the native numerical relation.
The fixed-forward refinement claim without independent plan binding is
withdrawn through783614f. No statistical/class-complete claim is falsified.

A repair must bind the entire program/query/count/resource-specific plan
to independently owned inputs before executing it. One special address
check would leave other plan coordinates unbound. The projected AMP work
has the same obligation, including its independently registered arithmetic
identity. No new semantic architecture action or Foundation R4 change is
needed.

Evidence: [exact passive witness](../../evidence/minimal/FP_INDEXED_AMP_PLAN_BINDING.json).
Run `python -X utf8 -B scripts/audit_indexed_amp_plan_binding.py --write`.
Only the small count/address witness, one differing operation and aggregate
checks are retained; no complete trace, weights or cache is dumped.
