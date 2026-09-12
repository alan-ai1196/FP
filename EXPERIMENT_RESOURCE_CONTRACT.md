# Experiment Resource Contract — ERC-1

**Status: FROZEN SPECIFICATION, 2026-09-12.** The scoped Reference/CPU
implementation passed release integration on 2026-09-13; the target AMP
bridge is **NOT VERIFIED**. GPU/model science remains HOLD until the target
prerequisite passes. `FP_THEORY.md` remains the only
normative theory source; this file fixes its experiment resource accounting,
claim scopes and release criteria.

The PRODUCT/SUM/range/precision study closes at XVII.31 and
[`NODE_EDGE_PRECISION_ACCURACY.md`](theory/proofs/NODE_EDGE_PRECISION_ACCURACY.md).
Per the current research direction, do not extend the static special-case
catalog or pursue its remaining sharp constants before implementation and
experiments. Reopen Foundation only when experimental/implementation
correctness exposes a legal semantic behavior that a faithful Runtime
cannot represent. Search cost, insufficient data, loose bounds and numerical
uncertainty retain their existing `UNRESOLVED` meaning.

## 1. The unified law and its exact scope

The matched resource law concerns a **fixed known positive rational table Q**
on all N=2^d binary contexts, d>=1, k>=2 labels, binary unary sources,
positive base one, local SUM weights {1/2,1,2}, shared binary PRODUCTs and
one final normalization. Let R_0=max_x 1/min_j Q_xj. Assume some critical
forced mass R_0*Q_xj is nondyadic: this is the complete LIMIT_ONLY branch
at R_0 proved in XVII.30. Permit range R_0+h, 0<=h<=1, and probability
tolerance delta, with epsilon=h+delta tending to zero.

For every legal local graph with S SUM nodes, P PRODUCT nodes and direct
mass significand width b, the complete necessary envelope is

`S*2^P >= log2(1/epsilon)-O_Q(1)`,
`b >= log2(1/epsilon)-O_Q(1)`.

There is a matching native upper envelope up to fixed construction
overheads and precision constants. Write each target row Q=a/A in primitive
positive integers, set A_max=max_x A_x, and define

`L=ceil(log2(2*max(1,A_max)/epsilon))`,
`S_0=k+1`, `P_0=3N-4`, `B_0=ceil(log2(R_0+1))+1`.

If S>=S_0+1, P>=P_0, (S-S_0)*2^(P-P_0)>=L and b>=2L+B_0, a native
dyadic-grid graph meets the requested cap and error. This upper requires
its **actual repeated SUM edges** and adequate exponent range. It is not
an upper certificate for a smaller edge/memory/work budget. A sufficient
normal exponent interval is [-2L,ceil(log2(R_0+1))]; this is a format
requirement, not permission to assume an infinite hardware range.

The resulting node-only optimum is

`min(S+P)=log2(log2(1/(h+delta)))+O_Q(1)`.

A binary-arity shared reciprocal construction simultaneously achieves

`S+P=Theta(log log(1/(h+delta)))`,
`E=Theta(log log(1/(h+delta)))`,
`V=Theta(log(1/(h+delta)))`.

Here E counts all incoming edges with multiplicity and V counts direct
exact significand/exponent encodings of the fully materialized native
tables, masses and normalizers. V is not a liveness-optimal GPU memory
claim. The growing reciprocal work is n SUMs and 2n-1 PRODUCTs; retaining
one final square and a positive tail correction gives **exact** prediction
at positive slack with n SUMs and 2n PRODUCTs. All other construction work
depends on the fixed complete target and is counted.

For uniform-context CE tolerance rho the joint variable is h+sqrt(rho).
These are sharp asymptotic orders and a separate-budget envelope, not
sharp finite constants, an exact small-P Pareto solver, or a general
language-model scaling law. Dyadic-feasible targets have a different
unrestricted-node branch; their fixed-P obstruction can still matter.
Changing sources, bases, coefficient alphabet, recurrence, value access,
numeric representation or finite resource caps changes the declared class.

## 2. Immutable registration before execution

Every run is bound to one immutable claim/run manifest. Runtime owns its
identity and all evolving claim state; helpers cannot overwrite it or
silently substitute a narrower/wider class. The manifest registers:

| Coordinate | Required declaration |
|---|---|
| Semantics | Typed causal source interface; complete claimed context/task domain; base/readout; local value operations; PRODUCT/delayed-state rules; searchable and fixed coordinates |
| Information and values | Data roles/splits/stream law; known target data versus legal finite-precision queries; initializer/profile/optimizer/transport; update unit; query dimensions/ranges/precision and actual acquisition work |
| Structural resources | Separate P, SUM-node S and incoming-edge E budgets; repeated parents and squares counted with multiplicity; all constructed constants, integer scaling and final excess readouts included |
| Range | Every context's final T cap; source/native activation caps if imposed; minimum nonzero values observed for numerical diagnosis; no forced equality of noncritical normalizers to the cap |
| Arithmetic | Exact reference encoding or sound reference enclosure; storage, PRODUCT, SUM accumulation, base/normalizer and final division dtypes; rounding/cast order; exponent/subnormal/flush behavior; precision and error allocation |
| Physical resources | Registered semantic-to-machine realization; shared object identity/ownership/refcounts; current/peak/cumulative memory and work; profiling/query/search/build/install/copy work, including build before freeing the incumbent |
| Objective and comparisons | Probability/CE/task loss and certified tolerance; matched non-graph coordinates; resource-feasible baseline implementations; comparison domain and stopping/search budgets |
| Continuity and evidence | Deployed-ref/AMP and candidate-ref/AMP lineages, cursors, learners and event order; fresh paired persistence rule; error/data-use ledgers; state-bound construction/bridge/install authorizations |

Numeric budget values and experiment instances are parameters of ERC-1,
fixed in each manifest before execution. Filling them from measured device
capabilities or a scoped task is not a new theory or a contract exception.
An unsupported or absent required field prevents a complete claim.

## 3. Accounting and numerical obligations

1. Report P, S and E separately. A fused/repeated/packed SUM must retain its
   actual logical and physical work. An integer repetition count is not a
   free coefficient. A computed scalar needs a counted PRODUCT when applied
   to another feature. All source, target and coefficient encodings retain
   their information/acquisition costs.
2. Report the actual format and per-stage precision, memory and error
   enclosures. Small node count and bounded activation maxima do not bound
   direct significand length or prevent underflow. A format with a fixed
   direct mass width has the proved boundary accuracy floor even with
   unlimited nodes. Alternative symbolic/expansion representations must
   declare and pay their own storage/evaluation costs.
3. Check mathematical normalization of retained masses as well as rounded
   predictions. The checked binary64 example displays exactly (5/8,3/8)
   while its stored masses have a nonzero exact prediction gap. Displayed
   equality, a final float64 rescore, or a plausible maximum range cannot
   authorize a reference/AMP bridge.
4. Keep each claim's complete normalizers, resource owners, information
   filtration and lineage. Static extensional constructions do not certify
   Runtime state erasure, optimizer reachability, fresh persistence or
   atomic installation. No theorem certificate escapes its decision class.
5. Search exhaustion, insufficient queries, bound overlap, numerical
   uncertainty, infeasible construction and absent bridge evidence must be
   distinguished. None implies that an unsearched native candidate is
   impossible. `CERTIFIED_COMPLETE` requires coverage of the declared
   finite/effective class and all decision-critical comparisons.

## 4. Fixed correctness fixtures and strong comparisons

Use the existing fixtures to pressure-test execution; further static
case-finding is not a prerequisite:

| Fixture | Retained obligation |
|---|---|
| Nondyadic critical mass and positive cap slack | Reproduce the separate P/S/range/precision envelope, local upper witnesses, positive exact tail repair and width lower; count expanded repeated edges and compare binary-arity constructions |
| Three-bit identity noise | Preserve the P=12 exact versus P=9 limiting distinction at cap nine; positive range slack changes exact feasibility; retain the existing float64 leakage and underflow failures |
| Three-bit noisy parity | Retain the minimum-cap four-PRODUCT result and the two-PRODUCT larger-range witness; do not claim that the known cap-44 construction is the full two-PRODUCT threshold |
| Small complete native grammars | Compare endpoint search to exact exhaustive truth with shared/repeated parents, compounds and zero-valued intermediate candidates; never replace the grammar with those example architectures |
| Complete Runtime adversaries | Exercise information roles, ownership, value construction, fresh data use, four trajectories, authority tokens and install reachability through the public complete endpoint |

The strongest applicable existing constructive upper is the baseline, not
the newest generic construction by default. Include fixed-P dyadic/Horner,
shared reciprocal, exact singleton and other already proved witnesses when
their declared budgets permit them. For small known tables an unconstrained
target oracle is a diagnostic loss floor, explicitly distinguished from a
resource/value-feasible competitor. Subsequent model science uses competitive
ordinary model baselines under matched measured training/inference budgets
and data; a deliberately weak or undertrained baseline is inadmissible.

## 5. Release order and minimal evidence

**ReferenceCompilerRuntime: scoped CPU prerequisite CLOSED.** Source
`ebe2c4c` passed 21 complete audit scripts from a fresh clone, including
the reference closure obligations and the 47-gate scope map. Read
[`REFERENCE_RELEASE_SCOPE.md`](theory/proofs/REFERENCE_RELEASE_SCOPE.md) and
its minimal release evidence. The frozen implementation concerns its declared
native classes, complete CPU learners, owned strategy and serialized Windows
resource/run protocol. ERC-1 itself supplies no implementation certificate.

**Next: target AMP bridge.** Execute the actual registered mixed-precision
path, with continuous deployed/candidate reference/AMP trajectories and
event-level enclosures, including structure construction and installation.
Device correctness/bridge tests follow reference closure. They are not
model-science wins and cannot be replaced by CPU endpoint agreement.

**Then: RTX 3090 experiments.** With the Runtime and actual target bridge
gates passed, execute the registered structural and model-science experiments
on the available target device. Hardware inspection and preparation are
read-only work that can occur earlier. Continue to return UNRESOLVED where
resources or evidence do not establish a claim.

Retain the manifest, code/version identity when needed, concise aggregate
resource/error results and the smallest reproducible failure witnesses.
Do not commit datasets, weights, caches, giant logs or expanded-edge graphs.
The exact resource audit is
`theory/numerical_checks/node_edge_precision_accuracy_audit.py`; its minimal
evidence is `evidence/minimal/FP_NODE_EDGE_PRECISION_ACCURACY_AUDIT.json`.
