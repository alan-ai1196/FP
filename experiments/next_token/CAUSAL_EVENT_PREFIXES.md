# Causal predictions and complete token event prefixes

The compact kernels previously accepted only complete update units. This
was enough to audit a unit endpoint but could not express FP_THEORY XV's
intermediate event relation. They now expose target-free `predict`, bound
`observe`, nonempty `prefix`, and a complete pending-state comparison. These
are passive numerical components for the actual Runtime integration.

## Native and physical event meaning

A committed origin contains every embedding/core/readout master, its source
context, ordinary cursor and optimizer clock. A pending prefix additionally
retains **all** actual ordered source windows and targets since that origin,
plus complete forward/gradient arrays or the native interval enclosures.
No earlier window is replaced by the latest context. Prefix length n is
independent of the source file position and satisfies1<=n<=N, with registered
update-unit size N. The ordinary cursor is origin.cursor+n; the optimizer
clock does not advance until commit.

For each prefix, the reference sums every native gradient contribution
without projection or division by n. Its existing enclosure induction works
unchanged with n columns: every column's forward/reverse operations enclose
the corresponding exact event, and explicit reductions enclose the sums over
all tied/repeated incidences. `Unit.exact_decoder` remains a complete independent
semantic decoder. Only a full unit may commit, still using the registered
learning-rate/N scaling. An incomplete commit refuses before producing any
successor.

The physical prefix recipe uses the same half core and single balanced
gradient operations as the earlier full-unit recipe, restricted to the
actually revealed n records. Appending a record recomputes that declared
balanced reduction from the retained origin/records. This defines its
pending accumulator at every event; it does **not** claim that floating
sequential addition or a differently shaped reduction tree is equivalent.
At n=N it is exactly the existing full-unit recipe, with unchanged operation
order. The AMP origin and successor remain its own, never reference values.

`predict(predecessor, window)` has no target argument. It carries its complete
committed or pending predecessor and source point. Forward graph and
normalizer operations are independent across context columns, so the same
pre-target column is obtained when that context is subsequently included in
a prefix. This property is conditional on the registered primitive arithmetic;
the CPU audit also checks its actual words. A full pending unit must commit
before another prediction. `mass_block` now accepts a target-free physical
prediction, and the algebraic all-label envelope can check it before any
target cache or target gradient exists.

`observe` checks predecessor identity, source binding, cache shapes/dtypes
and all cache words against recomputation, then appends the new actual
record. Original retained profile windows can be supplied explicitly; a
cache from a different default source refuses even if numeric values agree.
If arithmetic becomes unresolved after receiving the target, the exception
retains the complete new source/target prefix. This supports the Runtime's
separate obligation to own target acquisition before arithmetic work.

## Exact class of the state comparison

`state_relation.check` compares **one pair** of committed origins, or one
pair of retained prefixes with identical definitions, records, source contexts
and learner clocks. It is not a transition/future/source-domain certificate.
For every master q, its decoded parameter is exactly q/2^p. Integer differences
therefore give an exact maximum parameter discrepancy.

For a pending state, compare all embedding-incidence keys and all core
slots, including unused slots and zero values. Unlisted embedding gradients
are exactly zero on both sides. The readout gradient decoder is

```
unobserved label:  common[k]
observed label:    RNE32(common[k] - correction[label,k]).
```

This is precisely the physical subtraction consumed by the registered
commit. An exact binary32 decoder determines it without expanding V*K
gradient entries. The native enclosures represent the exact signed difference
of its complete common/correction sums. Comparing all corrected rows and
the common row therefore covers every native readout gradient coordinate.
All source records/masters remain retained; the representation does not
discard unobserved labels or earlier inactive-row gradients.

Take the maximum of the exact parameter error and outward-enclosed gradient
coordinate errors, and compare it as an exact fraction with `state_atol`.
Committed origins have zero pending gradients by their registered type.
Wrong incidence keys, nonfinite/wrong-shape arrays, exact-decoder allowance
exhaustion and an inconclusive error threshold refuse. Results are passive
comparison data, never a `CERTIFIED_COMPLETE`, physical bridge or install token.

## Audit and remaining integration

The [event audit](../../evidence/minimal/FP_TOKEN_EVENT_PREFIXES.json) exhausts
all sixteen four-token words for unit sizes2/4 and mixed/zero-input/zero-core
fixtures:96 histories,384 observations and144 independent commits. It checks
768 pre-target label forecasts against exact native/proper/raw probabilities,
10,752 complete native gradient coordinates, and624 state relations at births,
observations and commits. The small-fixture state tolerance is1/4; the maximum
observed state-error upper bound is1/32. This is not a text-training tolerance.

The physical CPU oracle checks49,110 primitive calls/289,512 words, including
41,472 half words. Every pre-target feature/normalizer/selected-mass word equals
the later prefix column. Parameter distances are input0/core0/readout1 grid
unit. All480 early commits and288 predictions before a required full-unit
commit refuse. Twelve predecessor/cache/type/shape/arity attacks, seven
complete-state mutations and two post-target arithmetic refusals pass their
expected outcomes. Dormant core and earlier embedding-gradient changes are
included in the state attacks.

Four repeated/out-of-order profile records end at source position2 and learner
cursor4, preserving every original window. A first harness assertion compared
sparse backing dataclasses rather than decoded semantic coordinates; the
independent packed-origin decoder can legitimately use a different exact
backing layout. The corrected audit compares every parameter/gradient, source
and clock. No semantic equality requirement was removed.

Existing batched reference, exact AMP CPU schedule and algebraic readout
controls also pass. The original10,020-word full-unit AMP oracle count remains
unchanged after extracting shared forward operations. No old CUDA job is
rerun, and no new actual-device or model result is claimed.

This prefix executor is an integration control: recomputing each prefix costs
quadratic unit work. It supplies no causal acquisition, role/lineage, memory
ownership or full Compiler release by itself. Integrate it into the existing
ReferenceCompilerRuntime and fund its complete resources; any later batch or
deferred execution must separately imply all internal event relations and
preserve legal Compiler access to pending gradients. This is the next task,
followed by ordinary language learning and strong baselines. Foundation and
ERC-1 remain frozen; no new semantic architecture action is introduced.
