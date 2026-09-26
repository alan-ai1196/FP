# Complete positive readout learning without a dense output update

Status: **PROVED SCOPED EXACT REFINEMENT; PASSIVE IMPLEMENTATION AND EXACT
AUDIT PASS, 2026-09-26**. This is a lowering of existing positive SUM heads
and the existing grid-projected mean-CE SGD. It adds no semantic action,
optimizer, search certificate or release authority. Its purpose is ordinary
full-vocabulary next-token learning, not another relation-task family.

## 1. Native class and gradient identity

Let a native positive SUM/PRODUCT core produce K nonnegative features z_i.
Its parameters may be tied, and nodes may be shared, including squares.
Append V heads with fixed positive bases and **distinct untied final slots**:

    M_y = b_y + sum_i W_yi z_i,   W_yi >= 0,
    Z = sum_y M_y,              L = log Z - log M_t.

No W slot occurs inside the core or another final edge. The core does not
depend on W. Features can vary between events and depend on the registered
causal inputs/delayed state. The pullback below uses the native event-local
derivative; it does not introduce differentiation through delayed history.
If multiple feature incidences refer to the same core node, their adjoints
are added, as in ordinary native reverse evaluation.

Direct differentiation gives, including at W_yi=0,

    dL/dW_yi = z_i/Z - 1[y=t] z_i/M_t,
    dL/dz_i  = S_i/Z - W_ti/M_t,   S_i = sum_y W_yi.

Thus a complete pending readout gradient over an update unit has the exact
representation

    u_i = sum_events z_i/Z,
    c_yi = sum_events_with_target_y z_i/M_y,
    G_yi = u_i - c_yi.

Unobserved labels have c_yi=0; their positive gradient u_i is still present.
Store u and the correction vectors for the R distinct targets already
observed, R <= min(N,V), where N is the declared update unit. This encodes
**every** native pending coordinate, not just the ones with a nonzero master.
Neither a label nor its future trainability is removed. The feature adjoints
also recover every core gradient by the ordinary chain rule; the prototype
returns these adjoints, but does not itself own or update the core.

## 2. Exact projected commit and a noncommuting shortcut

Use `mean-ce-projected-sgd-v1`, learning rate eta >= 0, unit N, and the
existing dyadic commit grid 2^-p. All initial readout values lie on that grid.
Write q_yi = 2^p W_yi, an integer, and

    a_i = 2^p eta u_i/N,       d_yi = 2^p eta c_yi/N.

Native commit is exactly

    q'_yi = max(0, floor(q_yi - a_i + d_yi)).

For a label without a correction, integer q and a_i >= 0 imply

    q'_yi = max(0, q_yi - ceil(a_i)).

For a corrected label, use its **old** q and the combined signed expression.
Clipping the common decrement and then adding a separately rounded
correction is false. Two legal V=2, K=1, b=(1,1), z=1, eta=N=1, p=0
witnesses, with equal initial q on both rows and target 0, are:

| Initial q | a | d_0 | Native q'_0 | Clip common step, then add floor(d_0) |
|---|---|---|---|---|
| 0 | 1/2 | 1 | 0 | 1 |
| 1 | 1/4 | 1/2 | 1 | 0 |

The correction accumulator cannot be reconstructed from current parameters
and u alone. With the same bases, z=1, eta=1, N=2, p=4 and zero masters,
observing target 0 versus target 1 leaves identical parameters and u=1/2,
but opposite gradient vectors. Appending the same z=0 event then committing
produces (1/4,0) versus (0,1/4). This is a legal future continuation that
distinguishes the proposed incomplete states.

## 3. Complete lazy master encoding

For each column i retain an integer default g_i, a monotone integer offset
D_i, a persistent label-to-raw-value exception map, and an ordered multiset
of **all V** raw values, including the implicit default multiplicity. Decode

    r_yi = exception[y] if present, otherwise g_i,
    q_yi = max(0, r_yi - D_i).

Initialize D=0. Arbitrary explicitly declared grid values are supported by
overrides, up to a fully dense initializer; constructing them is not free.
Sharing default storage does not tie native parameter slots.

At commit increase D_i by ceil(a_i). This gives precisely the required
non-target update: applying a second nonnegative decrease after a previous
clamp equals clamping after the summed decreases. For each corrected label,
compute q'_yi from the old column using section 2, then write raw value
D'_i+q'_yi in the new column. If that q' equals the decoded default, represent
it by the default instead. Adjust the two raw-value multiplicities exactly.
All V label identities and masters remain decodable, even when zero.

For an ordered multiset whose entries are raw value r with multiplicity n_r,

    sum_y q_yi = sum_{r>D_i} n_r r - D_i sum_{r>D_i} n_r.

Consequently Z = sum_y b_y + sum_i z_i sum_y q_yi/2^p can be obtained without
enumerating output labels. A requested target mass and the core adjoints
use the same complete parameters. Asking to emit all V probabilities still
requires V outputs; the identity does not make full output free.

The implementation uses immutable AVL maps with cached subtree multiplicity
and weighted sum. In-order keys determine the map, rotations preserve that
order, and every changed node recomputes its aggregates from its children.
The threshold sum descends one path and adds only wholly qualifying right
subtrees. AVL balance gives minimum node counts n_h >= 1+n_(h-1)+n_(h-2),
hence logarithmic height. Old roots remain unchanged.

Induction now proves refinement for every finite legal event word starting
from this initializer: initialization decodes the native masters and zero
gradient; prediction agrees by the column-sum identity; observation agrees
by section 1 and preserves every pending coordinate; commit agrees by
section 2 and restores zero pending gradient. Unit count, cursor and
optimizer-step count advance exactly as in the native learner. Parameter
snapshots in past predictions remain immutable. No finite test substitutes
for this induction.

The claim is about the readout component's parameters, gradients, clocks
and supplied feature adjoints. It is **not** a quotient of complete Compiler
state, construction history or physical resource ownership. Removing an
exception equal to the current default preserves this component's decoded
state; it does not authorize deleting provenance, prior snapshots or their
charges. Creating an exception stores a value of an already declared slot;
it is not a semantic birth or a selected new edge.

## 4. Costs and limits

Count exact arithmetic and index operations first; integer/rational bit
cost is separate. With K columns, V labels and R pending target labels:

- Target mass, normalization and feature adjoints use O(K log(V+1)) index
  work. One master lookup uses O(log(V+1)).
- A common commit shift uses O(K), and all target rewrites use
  O(K R log(V+1)). There is no dense V K commit scan.
- This small prototype copies/sorts an immutable correction table on
  observation. A conservative bound is O(K R + R log(R+1)) additional
  work, and a gradient-coordinate read scans up to R correction entries.
  It is not an optimized constant-time pending-gradient index.
- Initialization validates/stores V bases, K defaults and every declared
  override. With E exceptions, the current maps use O(K+E) nodes, pending
  corrections O(K R) values, plus the V bases. Worst-case E is V K;
  there is **no** universal sublinear-memory claim. Old persistent versions
  retain additional nodes whose lifetimes must also be paid.

Exact offsets, values and rational accumulators can grow. The passive
Python implementation has no owned bit, heap or work limit and supplies no
physical throughput result. A bounded solver must fund its actual work or
return UNRESOLVED. This proof does not assert equality of finite-arithmetic
schedules: reassociated normalization, gradient accumulation and floor near
a grid boundary can change floating results. In particular, a lazy exact
offset is not automatically the same as a sequence of rounded float32
subtractions. A future AMP lowering needs its own complete relation and
resource binding.

The passive dataclasses are not reached-state certificates. Refinement is
for initialization and the stated pure transitions. The observer checks
its actual predecessor and the algebraic cache, but supplied features have
no owned causal-source binding yet. There is no Runtime ingress, fresh
persistence, installation, search or `CERTIFIED_COMPLETE` authority.

## 5. Minimal exact evidence

Implementation: [native_readout.py](../../experiments/next_token/native_readout.py).
Audit: [audit_native_readout.py](../../scripts/audit_native_readout.py).
Evidence: [FP_NATIVE_READOUT.json](../../evidence/minimal/FP_NATIVE_READOUT.json).

Run `python -X utf8 -B scripts/audit_native_readout.py --write`.

- All 120 insertion permutations of five keys, 2,400 map-update/invariant
  checks, deletion orders, threshold sums, zero-valued map entries and old
  immutable roots pass independent reconstruction.
- All 1,808 declared event words pass 6,720 literal native observations and
  4,128 native commits. Every master, pending gradient, mass, probability
  and clock is compared, including zero features and unequal positive bases.
- 81 exact core cases check the feature pullback through a shared PRODUCT
  square and a tied core slot against full native reverse differentiation.
- Both noncommuting-commit witnesses and the pending-state continuation
  witness are retained. Stale/altered caches and illegal operations refuse.
- At the actual vocabulary V=50,257, K=4, eight synthetic feature events
  compare all 402,056 masses, 1,608,224 pending gradients and 804,112 committed
  parameters against a separately stored dense exact CE/SGD control. All
  tree multiplicities are rebuilt independently. The final current maps
  contain 29 label exceptions and 33 distinct raw-value keys; this is a
  fixture observation, not a general storage bound.

No text targets, model score, Torch or GPU execution is involved. This
closes a complete-readout obstacle; useful native text features and their
training, owned binding, numerical bridge and strong baselines remain.
