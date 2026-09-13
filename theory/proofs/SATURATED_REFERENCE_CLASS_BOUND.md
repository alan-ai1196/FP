# A universal empirical upper can close a native search without enumerating it

The upper proposition remains applicable. The implementation narrative
below records the v1 proposal/policy; the
[v2 prospective extension](OWNED_PROSPECTIVE_SELECTION.md) changes proposal
value choice and prospective admission without changing this upper theorem.

Status: **proved fixed-objective bound and conditional Runtime composition;
implemented exact/CPU audit.** Foundation R4 and ERC-1 remain frozen. This is
a solver for an existing reference objective, not another static resource
family or a new semantic graph operation. Runtime release and target AMP
remain separate obligations.

## 1. The comparison proposition

The registered objective is `fixed-state-empirical-ce-on-logged-contexts-v1`.
For each legally revealed objective observation, evaluate the same complete
learner endpoint on its retained complete source tuple. In particular,
parameters and delayed queues are frozen; evaluating an old context does not
advance that learner. Two identical source tuples therefore have the same
categorical prediction for each endpoint. Different endpoints can have
different predictions.

Let D be the ordered list of distinct registered observation identities,
`n_xy` the number of label-y observations with complete source tuple x, and
`n_x = sum_y n_xy`. The strictly positive native readout defines the exact
likelihood corresponding to the empirical CE objective:

```
L_D(q) = product_(x,y) q(y|x)^n_xy.
U(D)   = product_(x,y:n_xy>0) (n_xy/n_x)^n_xy.
```

**Theorem.** Every categorical prediction function q satisfies `L_D(q)<=U(D)`.
Consequently, if an actually constructed, owned, value/range-feasible
endpoint in the registered native constructor class, or the actual deployed
baseline, attains U(D), it maximizes this objective over that entire class
plus baseline. No evaluation of the remaining programs is necessary for
this particular conclusion.

**Proof.** For each x put `r_y=n_xy/n_x` on its observed labels. Weighted
AM-GM gives

```
product_(y:r_y>0) (q(y|x)/r_y)^r_y
    <= sum_(y:r_y>0) q(y|x) <= 1.
```

Raise this inequality to `n_x` and multiply over complete contexts. A zero
q on an observed label has zero likelihood and satisfies the inequality by
continuity. Native readouts themselves are strictly positive. Equality
requires q=r on every observed context, including zero probabilities for
unobserved labels there. An owned feasible endpoint attaining the upper is
an element of the comparison class, so its objective is simultaneously a
lower bound on that class's maximum and the universal upper. QED.

This is the unconstrained multinomial relaxation already underlying the
known-cone loss solver, used here to discharge the actual Runtime's finite
native comparison. It does not change native construction/value semantics.
An unvisited program's uncertain feasibility does not invalidate an upper
that covers even arbitrary categorical predictions. It would still prevent
an assertion that every native member was constructed and found feasible.

There are strict limits:

- The theorem covers this frozen-endpoint objective. A prequential learner
  can predict differently on repeated contexts as its state changes. This
  grouped bound cannot be reused for that objective or arbitrary futures.
- Complete source tuples include all registered causal source values. They
  cannot be replaced by token groups, a current prediction, or a partial
  feature projection. Erasing a distinction can produce a false upper.
- If some label has zero count at an observed context, the categorical
  optimum is on a boundary. Strict positive base mass cannot attain it.
  Failure to attain this relaxation is UNRESOLVED, not native infeasibility.
- Maximum empirical likelihood does not identify every maximizer, minimize
  nodes/range/work, force a hierarchy, or identify population relations.

## 2. An independently checked bound has no helper authority

`empirical_bound.py` builds exact counts from Runtime-owned revealed records.
Its producer uses guarded rational powers. Its separate verifier recomposes
counts and multiplies one factor per original observation; it never invokes
the producer. It checks exact numeric types, all ordered observation IDs,
every complete source tuple, all label counts, and the claimed rational U.
This passive object grants no observation access, value construction,
completion, persistence or installation permission.

Grouping is temporary arithmetic for an upper, not an information quotient.
All original observations, uses, learner states and source encodings remain
owned. The complete count table and proposal are retained in the existing
search workspace. The ordinary API receives neither a caller upper nor a
caller-supplied hidden partition or initialized candidate.

Runtime prepays a bounded number of scans, count operations, proposal steps
and workspace copies under the declared reference operation measure. Actual
native construction, profile, objective evaluation and buffer realization
also use their existing paid paths. This is not a CPU bit-time assertion.
The live host contract covers transient allocations as well as retained
objects through the process/job private-commitment limit; an unbound run
continues to have explicitly partial physical scope.

The registered accelerated solver has one bounded phase. A positive
`search_transitions` allowance admits that phase; it is not an assertion that
the phase costs one reference operation or emits one grammar prefix.
Its actual work/residency and any profile still have their full limits.

### Retain a proved object when its dependencies are unchanged

The larger domain exposed a separate execution cost: every ordinary event
re-encoded the entire exact range table, even between parameter updates.
The table computed by `enclose` depends only on the immutable Program,
semantic/source-domain contract and exact theta. It already quantifies over
the complete declared delayed-state invariant, not the current delayed
queue or optimizer accumulator. Inductively, if those fixed dependencies
and theta agree at the successor, the same owned range buffer still proves
the required range proposition. This does not equate the two learner states.

The ordinary transition now pays a theta comparison and keeps that existing
object/lease when equal. If theta changes, it recomputes the whole bound and
allocates the replacement before old ownership can be released. Publication
releases only superseded object IDs. All actual delayed queues, gradients,
optimizer counts, event traces and resource history remain retained; no
resource history is rebased. This is physical retention of one immutable
proof object, not a quotient, new semantic action or inferred future output
equivalence. CPU range enclosures retain their separate raw-theta checks.

An actual recurrent audit changes the delayed queue three times while
preserving that same bound object. A nonzero optimizer update replaces it.
An injected post-allocation replacement failure leaves the old published
learner/proof and the newly paid partial objects, with the target revealed
and continuation halted. The scope depends on the fixed contract; a future
mutable source domain or another bound dependency would require a new check.

After a proposed graph is built, Runtime independently rechecks its grammar
membership, actual current complete learner and registered initializer or
executed profile origin, then rescores it and the actual baseline. It checks
U again before retaining a proof. A favorable solver selector, forged raw
upper, substituted witness or fitted-but-unconstructed value cannot supply
those premises. Failure to pay final retention does not create an issuance,
even when a passive proof buffer has already been paid for.

## 3. The proof types state different facts

`ReferenceClassProof` and `REFERENCE_CLASS_EXHAUSTED` retain the older claim:
all ordered native members were constructed and compared, plus baseline.
Their `program_count` counts that complete enumerated class.

`BoundedReferenceProof` and `REFERENCE_CLASS_BOUNDED` state the theorem in
section 1 with its owned feasible witness. `evaluated_programs` counts actual
newly compared programs only. The syntactic cursor remains unexecuted and
is never marked exhausted. The decision class still has the full registered
native grammar, fixed initializer/profile, feasibility rules and baseline;
the proposal solver's preferred shapes do not define a smaller class.

Both types bind chi, root, revision, search/class IDs, comparison cursor,
baseline and selected lineage. Typed issuance and stale-context checks are
unchanged. They are exact empirical comparison proofs, not
`CERTIFIED_COMPLETE`, universal policy optima or installation permissions.
The owned policy may pass either selected lineage into the existing fresh
evidence protocol. CPU installation still needs both current, separately
paid same-path crossings, full learner relations and the atomic root/lease
transition. Run closure labels a bounded historical proof separately from
an exhausted historical proof; all its original search evidence survives.

## 4. Recovering the existing token hierarchy as a proposal

The supported acceleration preregisters only which observable one-hot token
source at position zero corresponds to the same token at position one. The
immutable solver ID selects an empirical binary-relation algorithm. It is
an acquisition/search algorithm over the full native grammar, not a new
source, graph primitive, partition oracle or architecture decision class.

From the verified observed counts it forms empirical majority XOR
constraints. A graph traversal solves consistent constraints, choosing a
root bit independently in each connected component. It retains the actual
edge counts, components and assignment. Ties and inconsistent constraints
leave this solver unresolved; they do not exclude other native programs.
An empirical majority is a proposal fact, never certified population truth.

Each group indicator lowers to a positive SUM of the corresponding token
atoms. Four native PRODUCT cells and two weighted SUM readouts combine
them. For common majority/minority ratio k, base masses `(1,1)` require
readout scale `k-1`. This proposal solver requires both unit and scale values
to be present in the registered initializer. If a profile is declared, the
actual replay then determines the candidate endpoint; it must still attain
the upper. No fitted number becomes an invisible syntax constant.

This simple proposal can miss a valid empirical optimum, for example when
noise proportions differ. If its actual endpoint fails to attain U, the
whole unsearched native class remains UNRESOLVED. The bound's correctness
does not depend on the heuristic being complete or the relations being true.

## 5. Identification and strong controls

The audit uses the existing noisy hidden-group task with only ordinary
context bytes and labels crossing into Runtime. The producer knows hidden
groups to synthesize data and the independent evaluator knows them to check
predictions. Neither supplies those bits or a conditional table to Runtime.

For n tokens the train graph is a path with n-1 edges. Each observed pair
has nine majority and one minority labels, so scale eight is in the fixed
initializer `(1,8)`. The proposal has `2n+10` nodes, six SUMs, four PRODUCTs,
`2n+4` weighted SUM edges, `2n+12` total edges and two retained slots. Exact
normalizer cap ten and activation cap eight hold on the entire n-squared
registered one-hot source domain, not only the train path.

The full class caps are deliberately broad enough to include a separate
direct-lookup cell for every token pair. Even source-only strings at its
largest node extent exceed the finite registered work allowance. This is
an explicit cardinality lower bound on literal complete construction, not
a weakened or prematurely stopped baseline. The all-categorical empirical
upper is a stronger objective comparator than any native subclass.

The audit also constructs a smaller SUM-only graph tied at the same train
optimum: for each oriented path edge `(i,i+1)`, send only the left token i
to its majority-label readout at weight eight. The last left token is absent
from the training path. On four tokens this uses five nodes, two SUMs, three
edges and no PRODUCT, versus the proposed hierarchy's eighteen nodes.
Thus reaching U on these observations cannot force PRODUCT or hierarchy.

Generalization uses different premises. On the full uniform balanced-token
task, the existing XVII.1 theorem gives the sharp unrestricted unary-SUM
infimum `[log(2)+H(0.1)]/2`, approximately 0.50911507698 nats, while the
hierarchical conditional achieves `H(0.1)`, approximately 0.32508297339.
That sharp SUM control includes arbitrary token-specific unary coefficients
and does not require baseline access to hidden groups. It is an external
known-task theorem/control, never a train-derived Runtime certificate.

Two disconnected components give a further exact negative control. Hidden
assignments `(0,1,0,1)` and `(0,1,1,0)` agree on edges `(0,1)` and `(2,3)`
and on every revealed noisy training record. Runtime produces the identical
proposal and empirical optimum in both worlds, while unseen relation `(0,2)`
differs. Component-root choices must remain arbitrary proposal choices.

Connectivity alone also cannot make noisy empirical majorities true. An
audit flips all training labels on one path edge, producing another
consistent connected assignment and an attained empirical upper. Subsequent
labels from the original task yield no persistence crossing and no install.
This is an executed negative control, not a theorem that false candidates
can never cross or that a finite noncrossing rejects them.

## 6. Executable boundary

`scripts/audit_reference_acceleration.py` combines the exact count-table
checks, independent small native enumeration, all four-token assignments,
actual profile endpoints, ambiguity/train-tie controls and authority faults.
Its bounded worker registers a 1 GiB host arena, n=32, 310 training events,
310 subsequent ordinary events and two final continuation events. The
optimizer unit is ten; the separately admitted evidence horizon permits
up to 310 events, but crossing stops each statistic and installation uses
the next eligible ordinary boundary. Subsequent events continue the actual
installed learner and old shadow. The owned strategy performs one
proposal/upper phase, separate reference and CPU evidence admissions,
installation and final stream closure. An
independent binary64 oracle replays every retained numerical phase; the
parent verifies the actual child identity, final job resources and exit.

The executed n=32 run compares one native witness against the universal
upper. Its registered class contains at least `2^6540` source-only program
strings, yet the syntax cursor is not declared exhausted. It installs at
cursor 330, continues through 622, and passes 1,963 independent binary64
phase checks. Peak owned reference payload is 65,266,182 bytes; the completed
job's process-commit peak is 333,139,968 bytes, below the 1 GiB registration.
The latter includes the independent final audit and is not a tensor-memory
measurement. The run's actual process identity and successful exit are
checked by the parent.

The deterministic audit tape exercises a protocol conditional on the
explicit stochastic producer assumption. It does not itself prove that
assumption or an empirical population error rate. The
[subsequent owned CUDA audit](OWNED_CUDA_HIERARCHY.md) now executes the same
n=32 fixture and negative controls on its actual storage/operation/cast path,
with independent target evidence and resident installation.
Read the minimal audit record for executed counts and measurements; this
proof is not an aggregate Runtime release certificate.
