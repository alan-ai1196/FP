# Equal structural resources do not imply equal numerical feasibility

Status: **exact finite counterexample to precision-safe resource tie
pruning; native input reached by owned reference execution; passive exact
RNE audit**. The existing structural DP theorem is unchanged. No new actual
CUDA execution, Runtime plan admission or model outcome is claimed.

## 1. The claim that fails

The [order-resource law](QUERY_ORDER_RESOURCE_FRONTIER.md) proves that a
subset S and its best accumulated structural cost suffice to minimize tape
nodes and floating outputs under join/live-cell limits. It explicitly
excludes numerical feasibility. The following stronger inference is false:

> Keep one representative of equal resource cost at S. If its completed
> schedule fails the registered numerical relation, every tied schedule is
> infeasible under the joint structural and numerical contract.

Even retaining all distinct Pareto resource pairs does not repair this
inference if tied plans are collapsed. This is not a lower bound on all
numerical solvers, nor a reason to retain every order: a stronger numerical
invariant or independent certificate could justify pruning. The resource
equivalence alone does not.

## 2. One complete two-order class

Use the native n4 relation, anchored at0, query(0,3), and signed counts in
canonical edge order(01,02,03,12,13,23):

`(-2,-2,-2,-2,-2,-1)`.

This is a legal native state. Present target1 twice on each of the first
five edges and once on the last. The audit performs these eleven actual
reference Runtime events, comparing the complete learner and query cache
with the independent literal FP graph. The next target is unrevealed.
The exact current probability of target0 is59013/328010.

There are two effective query-retaining orders: eliminate native vertices
1 then2, or2 then1, followed by the same terminal join/readout retaining3.
The zero-based stored permutations are(0,1,2) and(1,0,2). No alternate anchor,
factor order, arithmetic primitive, normalization or rounding rule is used.

Both plans have exactly the same structural resources:

| Coordinate | Both orders |
|---|---:|
| Largest joined table |8 cells|
| Logical live-table peak |30 cells|
| Exact positive multiplications |40|
| Exact positive additions, including final integer total |9|
| Partition-only tape |69 nodes|
| Floating outputs |70|
| Executed scalar RNE operations |63|
| Half outputs |0|

The fixed AMP interpreter uses single precision for the additions/readout
in this instance; neither order has a non-power product requiring a half
operation. It is a valid subset of the registered mixed arithmetic class.
All exact count/range inputs are identical. The structural subset DP returns
(0,1,2), tied for the exact minimum(C,N)=(70,69).

## 3. Same contract, opposite decisions

Set native/state tolerance to1/1000000, probability/division tolerance to
3/200000000, normalizer cap to10+1/1000000 and activation cap to8. Retain the
existing table/output/tape limits4096/32768/65536/262144. These are a single
explicit forward-readout contract, held fixed for both alternatives. The
normalizer cap includes the tiny rounding of the stored mass sum; it does
not change the exact native normalizer10.

The exact RNE interpreter, complete operation checker and existing native
bridge give:

| Quantity | DP-selected(0,1,2) | Alternative(1,0,2) |
|---|---:|---:|
| Rounded target0 probability |6036851/33554432|12073703/67108864|
| Native-coordinate error |1043/8598585344|1043/8598585344|
| Normalizer error |0|1/8388608|
| Probability error, including proper mass normalization |99553/5503094620160|16113/1375773655040|
| Stored-mass versus rounded-probability error |1/41943040|9897821/703687450165248|
| Fixed complete forward bridge |UNRESOLVED|satisfied|

For the selected order, probability error is about1.809e-8 and division
error2.384e-8; both exceed1.5e-8. The alternative's corresponding maxima
are about1.171e-8 and1.407e-8, both below it. All other declared inequalities
pass for both orders. Every displayed decision is made with exact rational
arithmetic, not these decimal approximations. The two target0 stored words
are1043872486 and1043872487. The complete seven-word readouts and exact
diagnostics are retained in the minimal evidence.

Thus the selected plan is unresolved while the complete two-order class
contains a witness satisfying all these forward structural/numerical
constraints. The two prefixes reach the same eliminated set with the same
structural cost, but their rounded values can affect the common remaining
readout. Erasing that distinction is not licensed by the structural DP.
No assertion about subsequent gradients, whole-stream success, installation,
search funding, or physical workspace ownership follows from this example.

## 4. Consequence for the paid solver

The structural DP remains an exact optimizer in its stated class and a
useful proposal algorithm. Its selected order can be executed and checked;
failure of that order must remain UNRESOLVED for the larger precision-aware
existence question unless a separate complete numerical certificate exists.
No architecture action, weakened bound or precision-aware architecture menu
is needed. This witness does not demand expensive numerical search before
deploying a safely checked structural proposal.

The current indexed physical Runtime still has its fixed schedule and does
not admit the alternative plan from this passive audit. No current Runtime
certificate is falsified, and the already registered model tolerances are
unchanged. The result prevents an invalid expansion of a future solver's
decision class; it reports no empirical n16 failure or model improvement.

Run `python -X utf8 -B theory/resource_checks/order_precision.py --write`.
`FP_ORDER_PRECISION_SEPARATION.json` records the eleven owned reference
events, complete literal checks, both effective orders, identical resources,
126 checked scalar RNE operations and the opposing bridge decisions. It
contains no weights, caches, device traces or duplicate research state.
