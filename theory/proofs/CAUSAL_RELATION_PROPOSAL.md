# An owned native posterior proposal, with causal profile provenance

Status: **scoped construction and replay theorems, exact adversarial checks,
and functional owned CPU construction/installation**. Four fresh CPU/RTX3090
jobs are registered below and remain pending at this source. This extends
a solver, not Foundation, ERC-1, the native grammar, learner or search objective.

The [initial recurrent control](NATIVE_RECURRENT_POSTERIOR.md) established
that positive delayed programs can adapt as a known finite-window posterior.
The new question is whether ordinary data can cause the complete Compiler
to construct and install such a program without receiving its state. The
answer is yes in the scope below. This does not establish a useful noise
estimator, affordable whole-history inference or a complete model search.

## 1. Model guidance and the actual decision class

Solver `causal-binary-relation-window-posterior-v6` receives the existing
`RelationSourceSpec` alignment of two observable token roles. It receives
no latent partition, fitted parameter, posterior vector or delayed endpoint.
Runtime supplies its actual registered DataContract, learner, source domain,
initializer, grammar, profile and ordinary cursor after paying proposal work.

The guidance model has n independent fair latent bits and common independent
label noise epsilon. Pair queries may repeat, close cycles or be diagonal.
Interpreting its likelihood generatively assumes queries carry no extra
latent/noise information beyond their revealed history and independent
randomness. The solver does not establish that assumption from finite data.

For each available initializer slot s>=0, set epsilon=1/(s+2). The exact
descriptive score is

`G(s) = 2^(-n) SUM_z PROD_(i,j,y in objective records)
                      [(1+s)/(2+s) if z_i XOR z_j=y; 1/(2+s) otherwise]`.

Equal global flips have equal factors and pair predictions, so a value
calculation may enumerate K=2^(n-1) representatives with z_0=0. No complete
state quotient follows. Every empirical count, including ties, remains
retained; no majority constraint freezes an uncertain relative sign.

Each feasible slot's score and window are retained. A strict exact argmax,
with first-slot tie breaking, proposes one native graph. G is a static-latent
full-history marginal on the declared objective records. With an evicting
window it is not even the emitted learner's trajectory likelihood. It is
also not Runtime's frozen-endpoint empirical objective, fresh wealth or
noise identification. The [forest impossibility](RECURRENT_SELECTION_OBJECTIVE.md)
still applies: a one-observation forest gives identical G for every s.

The complete decision class remains `ReferenceSearchSpec`'s ordered native
grammar, including every legal registered state binding and initialized/
profiled endpoint, plus actual deployment. The constructor actually builds
the proposal through `_construct`, executes the registered profile and
scores that resulting frozen learner on the logged contexts. Only an owned
witness attaining the independently verified categorical upper can close
this bounded search. One proposed graph does not advance an enumeration
cursor, declare other graphs infeasible, or exhaust that class.

## 2. Base-one positive realization

Require an actual unit initializer slot and a registered zero learning
rate. A used noise coefficient must also be stable under the registered
commit grid: its reduced denominator divides 2^b, if a b-bit grid is used.
Zero rate still executes quantization; it does not make off-grid values
constant. Unused prefix slots, gradients, clocks and all ordinary commits
remain part of the actual learner; there is no identity transport claim.

For each representative z use the positive excess recurrence

`u_next = u + s I_z (1+u)`.

Here I_z is the positive sum of matching lag1 input/target atom products.
The current first token role's one-hot SUM produces the unit, an empty SUM
produces zero, and actual unit/noise SUM slots supply every coefficient.
The missing preceding observation at ordinary cursor0 has I_z=0. Thus
`1+u_next = (1+u)*(1+s I_z)` and a depth-H chain computes weights
`w_z=(1+s)^(number of matches in the last min(t,H) labels)`.

Unlike the initial control, the enclosing semantic base stays (1,1).
Construct K-1 by K-1 repeated unit incidences in a native SUM. With
`C = (K-1) + SUM_z u_z`, the two excess heads are

`E_y = C + s SUM_z (1+u_z) G_(z,y)(current query)`.

Therefore native masses, including base1, satisfy

`M_y = SUM_z w_z + s SUM_(matching y) w_z`,
`T = (s+2) SUM_z w_z`.

Their final normalization is precisely the noisy finite-window posterior,
including diagonal queries. There is no internal division, supplied state,
numeric SUM literal, extra optimizer or semantic architecture action. This
base-one graph has different unit derivatives from the base-K control;
equal initialized forecasts do not identify their complete learners.

## 3. Registered boxes, literal syntax and bounded proposal work

An H-window emission uses K(H-1) distinct declared lag1 mass coordinates.
Unused registered coordinates keep legal typed zero bodies and remain owned.
At each stage, if its predecessor's **declared** upper is U, a successor
coordinate must have upper at least `(1+s)(1+U)-1`. The construction assigns
available coordinates in guarded increasing-upper order. It never infers
an invariant from a smaller value attained during one observed replay.

For example, nominal s8 bounds U1=8,U2=80 support H3. Loosening every first
bound to9 while keeping the second80 invalidates that assignment: the
next body needs89. The emitter accepts H2 instead. This is a conservative
witness search within a declared interface, not a maximal-window theorem
for all programs or all possible state assignments.

If final predecessor bounds are U_z, the forward envelope
`(s+2) SUM_z (1+s)(1+U_z)` covers the normalizer and every emitted activation
on the declared categorical source domain. For H1, U_z=0. The actual
constructor's independent full-domain range check remains mandatory.
Tighter reachable-value reasoning, a different encoding, more resources or
another solver may admit a graph this emitter does not propose.

For n tokens, K=2^(n-1), window H, Z distinct zero-body types and P retained
initializer-prefix slots, the emitted literal counts are

| Quantity | Count |
| --- | --- |
| Nodes | 4n+2+Z+5+4n^2+K(4H+5) |
| SUMs | Z+6+K(2H+4) |
| PRODUCTs | 4n^2+KH+2K-1 |
| Edges | n+2Kn^2+6KH+10K+8n^2+1 |
| Slots | P |

There are 4n+2 source nodes, K(H-1) state reads, 2n^2 query-pair
products and 2n^2 labelled previous-pair products. All orientations except
the all-zero one have two nonempty parity heads, giving 2K-1 such products.
The counts include repeated unit incidences and unused-type zero bodies.
For n3,H3,Z1,P2 this is124 nodes,47 SUMs,55 PRODUCTs,260 edges and8 bindings.
This literal accounting closes this emitter's registration; it does not
reopen the frozen static PRODUCT/SUM/range/precision study.

Before reading objective observations or calling the proposer, Runtime
pays its metadata/scan/arithmetic allowance. The emitter refuses exponential
expansion once even K exceeds the node allowance; at most the declared node
count of worlds and state count of stages/assignments can be visited. Its
allowance covers source/domain scans, the ordinary-ID index, quadratic
state-assignment scans, guarded comparisons and per-world/slot likelihood
factors. `compare_exact` bounds rational ordering cross products as well as
ordinary arithmetic. Constructor, actual replay, endpoint comparison and
retained objects pay their existing separate charges. This is reference
primitive accounting, not integer bit-time, elapsed CPU time or total host
memory. Fresh process/job fences supply the separate physical audit.

## 4. Replay has a causal origin sequence, not an implicit reset

Let T be the ordinary birth cursor. A profile reuses logged source contexts
with their original provenance. Replaying ordinary record r>0 supplies the
factor for original label r-1; record0 supplies the identity factor. Profile
targets still execute normal gradients and commits, but cannot redefine
the lagged source origins. A new candidate starts with all delayed values
zero, once. There is no reset between profile passes.

For a depth d counted backward from the end of actual profile replay, define
`a_d=r-1` for the replayed original record r>0, and a_d=empty for record0 or
padding before the candidate's initialization. The required ordinary origin
is `b_d=T-d-1` when nonnegative, and empty otherwise.

**Causal-tail sufficiency theorem.** If a_d=b_d for every1<=d<=H-1, the
attached native state and the next ordinary lag1 source compute the exact
H-window posterior at birth and every subsequent legal continuation.
Each actual operation must still succeed within its declared resource and
arithmetic envelope; this theorem does not turn a refused computation into
a completed forecast.

Proof: by induction a native depth-j state is the product of the last j
replayed likelihood-ratio factors, minus1. Initial padding and record0 have
the proved identity factor. Matching origins for every relevant depth
therefore makes every stored stage equal its ordinary-stream counterpart.
The next source supplies label T-1, and each later ordinary transition
preserves the relation. Nothing in this argument identifies optimizer
clocks, replay provenance, other candidate coordinates or full Runtime state.

The emitter checks only this bounded tail by indexing the registered profile
period; it does not expand its potentially large pass count. It chooses H
before the first unmatched origin. This one rule accepts a sufficient suffix,
an arbitrary earlier replay prefix, or multiple passes when their needed
tails match. A one-pass ordinary suffix of length L gives the familiar
sufficient condition `L>=min(H-1,T-1)`, thanks to zero initial padding.
That zero-padding argument cannot simply be reused between profile passes.

Two exact counterexamples distinguish the conditions. Reversing replay of
`(01,0),(12,0),(02,0),(01,0)` gives a previously constructed H3 graph's next01
probability73/82 instead of the proper suffix37/42. For n2, replaying two
`(01,0)` records twice in an H4 graph gives3281/3650 instead of73/82: an old
factor from the earlier pass reaches the longer stage. The origin check
accepts H3 for that second profile, and H1 for the reversed first profile.
These are false warm-state claims, not defects in legal Runtime replay.

## 5. What has actually been checked

Run `python -B scripts/audit_causal_relation.py`. Independent full2^n
enumeration checks1,552 guidance scores and96 uninformative ties. The new
base-one graph passes2,016 exact next-window forecasts across224 profile
plans, including cycles, signs, repetitions, diagonals, mixed prefixes,
multiple passes and window eviction. The two displayed false warm-state
claims are retained as minimal exact counterexamples. Eleven interface,
type/slot, range, bit, declared-box and commit-grid controls remain scoped
to refusal by this emitter, not exclusion of the whole native class.

`--authority` also checks two actual owned searches. An injected prepaid
work failure prevents any proposer call, candidate creation or upper-table
publication. A forged helper status `CERTIFIED_COMPLETE`, fictitious scale999
and likelihood1 metadata cannot bypass actual initializer/profile execution
or produce a class proof. The resulting owned decision remains UNRESOLVED.
The existing eight empirical-upper/authority adversaries also pass unchanged.

The functional CPU `--cpu` stream starts with a uniform zero program binding
all registered states. Three ordinary repeated labels cause the policy to
emit the native s8,H3 candidate, initialize its actual two slots, replay three
retained records and compare the complete resulting endpoint. Its class
remains UNRESOLVED. Both fresh identities start at cursor3 with wealth1;
actual independent paths cross and install at cursor39. All44 observations
are retained, including five post-install forecasts with previously unseen
pairs and contradictory labels. The stream seals and268 binary64 phases
are independently replayed. Terminal search status CLOSED_BY_INSTALL keeps
the original class decision UNRESOLVED. This functional run supplies no
source-bound physical host or new CUDA claim.

## 6. Registered physical continuation

The independent `--rounded` preflight checks91 profile/ordinary forecasts
for the two replay cases before any new GPU job. Master parameters and
delayed coordinates remain exact, but base-one readout masses do not. After
three identical off-diagonal zeros the literal reference masses are
(13124,1476); the independent rounded path produces(13121,1476). Its head
excess13123 lies between binary16 values and rounds to13120 before base1
is added. Reusing the base-K control's exact-mass claim would be false.

Maximum value/mass/normalizer error on the registered traces is3; maximum
normalized stored-mass probability error is77/3362410, gradient error
130103/209715200 and raw division error3497/126852530176. A separate rounded
invariant calculation checks all171 source rows and every legal queue box;
its largest rounded normalizer upper is29158, below the fixed cap29160.
This preflight uses an independent interpreter and claims no actual GPU
execution. It motivates the following registration before target jobs:
absolute state/native/normalizer tolerance8 and probability tolerance1/10000.
Actual masters and delayed values are additionally checked for exactness;
observed errors must be reported separately from the allowed tolerances.

`--preflight` fixes four fresh jobs: CPU/full, CPU/twice, CUDA/full and
CUDA/twice. CPU host cap512MiB, CUDA host cap4GiB, each timeout300 seconds;
256MiB packed payload and10^10 reference work per role; actual CUDA
16MiB arena,32MiB allocator,4096 output cells and131072-byte phase frames.
Each job uses the same
44-event script, Gamma=(1,8), rate0, gridNone, normalizer/activation29160 and
the full171-row source domain. Grammar limits are(256,102,118,528,12).

Full and twice profiles execute3 and6 actual events respectively. Their
needed tails agree, while their optimizer clocks and provenance stay
distinct. Fresh evidence has40 one-event epochs, gain bound11, bet3/4,
alpha1/4 per path and global alpha3/4. Only actual paired crossings can
install; every retained fresh score, log enclosure, wealth step and first
paired crossing is independently recomputed from the actual forecast path.
The initial uniform deployment is a construction fixture; this
matrix tests causal reachability and physical correctness, not model
quality against a weakened baseline. Independent full-latent enumeration
checks the declared window probabilities. The earlier strong posterior
model experiments retain their own scopes and measured results.

Commit this registration before `--bounded --write`; retain every completed
job, failed or successful, under its source. Pending GPU results cannot be
borrowed from the earlier initially supplied native model. The existing
RN-5 matrix keeps its main source, data, budgets and acceptance rules.
