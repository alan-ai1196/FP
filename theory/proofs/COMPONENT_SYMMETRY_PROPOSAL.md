# Component symmetry as a native relation proposal

Status: **scoped proof and exact model check; source-bound endpoint records pending**.
This addresses the model uncertainty measured in
[RN-1](../../experiments/relation_noise/RESULTS.md) and
[RN-2](../../experiments/prospective_relation/RESULTS.md). It changes a
registered proposal solver, not Foundation R4, XVII.31 or ERC-1.

## 1. Average predictions over unresolved relative flips

Let the untied empirical parity constraints be consistent, with components
`C_1,...,C_c` and one representative bit assignment `h`. A tied observation
imposes no preferred parity. For `g in {0,1}^c`, flip every bit in component
`C_k` by `g_k`. These transformations preserve every untied constraint; a
global flip is redundant for pair predictions. Observations, counts and the
unvisited constructor class are retained, not quotiented away.

At initialized unit weight1 and one available readout scale `a >= 0`, the
old hard proposal predicts `(a+1)/(a+2)` for the parity selected by that
representative and `1/(a+2)` for the opposite label. Average these normalized
predictions over the component flips. For one-hot token queries `(i,j)`:

* Within a component the parity is unchanged, so the old prediction remains.
* Across components each relative parity occurs equally often, so the
  average prediction is `(1/2,1/2)` for every available scale.

This finite-family prediction identity does not require that empirical
majorities are true. Interpreting the cross-component prediction as the
true posterior additionally requires a prior/likelihood invariant under
independent component flips. The registered independent fair-bit prior and
parity-only forest observations have that symmetry. Finite IID data still
leave uncertainty *inside* a component; the hard within-component model is
not thereby an exact posterior.

For any fixed query and target, convexity gives log loss of the average
prediction no larger than the average log loss of the representatives.
The same statement holds for Brier loss. Under a flip-invariant conditional
world distribution this also improves or preserves average risk relative
to an arbitrary representative. It does not order the models in each
individual world, or compare adaptive deployments using different labels.

## 2. Realize that endpoint using existing positive syntax

For position `p`, component `k` and representative bit `b`, let `G_pkb`
be the ordinary unit-weight SUM of its token sources. Construct

`e_y = a * SUM_{k,b,d: b xor d = y} (G_0kb * G_1kd)`.

The base remains `(1,1)`. On a one-hot query within one component, exactly
one PRODUCT is one; readout masses are `(1+a,1)` or `(1,1+a)`. Across
components every PRODUCT is zero, so masses are `(1,1)` and normalization
produces the required uniform prediction. No half coefficient, posterior
value constructor or new architecture action is introduced.

The straightforward native graph has `2n+8c+2` nodes, `4c+2` SUMs, `4c`
PRODUCTs and `2n+12c` edges. It uses the same available initializer prefix
as v2. This counts one explicit witness, not an optimality or lower-bound
theorem; the strong forest posterior already avoids enumerating flips.
When `c=1`, sorted source terms reproduce the old connected graph.
When this witness exceeds the registered grammar or numerical/resource
limits, the solver returns unresolved without narrowing the class.

The implementation uses the already retained components and counts. It
creates no new complete-state coordinate or signer. Native construction,
whole-domain range checks, actual learner/AMP paths, fresh evidence and
installation remain Runtime-owned. Construction charges the actual larger
graph; existing bounded proposal work covers a fixed number of scans, and
the actual scale likelihood operations remain guarded and prepaid.

## 3. Ties and exact reachable scale selection

The v3 solver omits a tied edge from the parity constraints but retains its
full counts. If its endpoints remain in one component via other constraints,
those counts still contribute to the scale-dependent empirical likelihood.
If the endpoints belong to different components, its prediction is uniform
and its likelihood factor is independent of the readout scale.

Thus the exact scale argmax can use only within-component counts, including
any within-component ties. For preferred/opposite totals `M,m`, compare
`((a+1)/(a+2))^M * (1/(a+2))^m` over the available initialized values.
Across-component factors are common to every alternative and may be omitted
from this argmax, not from the independently evaluated full endpoint score.
The separate empirical upper, baseline and complete native decision class
are unchanged. A balanced bridge can now be predicted uniformly while
other observed relations remain useful. Inconsistent untied cycles still
leave this proposer unresolved.

This does not remove the existing policy's restriction to an actually
compared improving proposal. If the baseline already attains the universal
upper, bounded search can finish without constructing this alternative;
all-tied data therefore do not force a new candidate or installation.

## 4. Two limits that must not disappear

The prediction identity is **not valid for general soft inputs**. With
unit weight1 and scale8, take two components and representative bits all zero. Let the
left input select token0, and give the right input half mass on token0 and
half on a token in the other component. Averaging the old normalized
predictions gives `(7/10,3/10)`. The component-only construction instead
has masses `(5,1)` and predicts `(5/6,1/6)`. Both respect activation8 and
normalizer10. Normalization prevents the one-hot argument from being used
outside its stated domain. No Runtime prediction certificate claims this
extra averaging property on soft contexts.

Nor does equality of initialized predictions imply equality of complete
learners. At scale0 a component proposal and the zero-slot uniform program
both predict uniform. On a within-component target agreeing with its parity,
the proposal has readout-scale loss derivative `-1/2` at unit weight1;
the zero-slot program has no such coordinate. One legal single-observation
update at learning rate1/8 gives scale1/16 and probability17/33 instead of1/2.
The graphs, optimizer state, resource ownership, lineage and fresh evidence
must stay distinct. No rewrite, merge, quotient or inherited certificate is
authorized by the endpoint identity.

Actual model quality, finite fresh-evidence power and deployed risk require
their own registered experiments. An improved frozen orbit-average risk
does not establish an improved adaptive deployed stream.

## 5. Audit and experiment boundary

`scripts/audit_component_symmetry.py --exact` passes 74 partitions and 320
relative assignments: 7,320 one-hot orbit-average equalities, the same
predictions after reversing token presentation, 14,640 exact labelwise
Brier inequalities and 30 connected graphs identical to v2 at `2f24d18`.
All 605 count/initializer/slot-cap combinations agree with an independent
enumeration of parity assignments and exact scale likelihoods. A balanced
intra-component chord changes the chosen scale; absent unit values,
inconsistent cycles and a tight integer budget retain their refusals.
Opposite directed rows remain distinct in the independent empirical upper.

The CPU/CUDA matrix has six cases: disconnected installation, a balanced
bridge, an unresolved-class scale1 installation, literal-witness grammar
refusal, and the two complete learner continuations above. Its committed
source and compact execution records will be recorded after the full matrix.
The [RN-3 protocol](../../experiments/component_uncertainty/PROTOCOL.md)
fixes eighteen new model workers before inspecting its new seeds. Endpoint
correctness supplies no unexecuted model score or deployment claim.
