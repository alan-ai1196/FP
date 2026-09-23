# Owned joint-noise reference continuation

Status (2026-09-23): **IMPLEMENTED; EXACT OWNED RUNTIME AUDIT PASS**. The
canonical joint-noise learner is registered inside ReferenceCompilerRuntime
for exact construction, ordinary prediction/observation/commit, profile replay
and same-path fresh reference evidence. No Foundation or ERC-1 rule changes.
This is a reference realization, with no new CERTIFIED_COMPLETE decision class,
actual joint AMP phase or installation authority.

The [indexed storage component](JOINT_NATIVE_PARTITION_STORAGE.md) supplies
the actual G/Gamma/U description and positive integer decoder. The
[joint-excess theorem](JOINT_EXCESS_PARTITION_BRIDGE.md) supplies its complete
native coordinate relation. The new work makes that computation an operation
of the existing owner, rather than treating a passive result as a certificate.

## 1. Closed registration, without a second owner

`JointInitializer(schema)` and `JointLearner(schema)` bind the same complete
`JointRelation(n,rates,prior)`. Rate order, prior, native coefficients, sources,
heads and unit simplex U are part of the registration. The whole source
domain is exactly `CategoricalPairDomain(n)`, not a successful current query.
The ordinary ingress still owns the complete received source row and actual
target. A wrong categorical row is retained as failed ingress.

The historical `indexed_histogram` configuration field already distinguishes
several non-histogram decoders by exact allowance type. It now admits
`JointPartitionAllowance` only with this joint Gamma/U. The fixed natural
order has no external solver callback. The joint registration currently
refuses order search, native-class search, binary64 execution, CPU install
and CUDA registration. A CUDA refusal occurs before creating its executor.

Machine identity is `packed-indexed-joint-noise-integer-partition-reference-v1`.
Reference arithmetic is `indexed-joint-noise-count-excess-partition-reference-v1`.
The initializer is `indexed-joint-rate-prior-fair-world-unit-simplex-initializer-v1`.
Earlier model/arithmetic identities and serialized contract fields remain.

`joint_execution.py` adds immutable coordinate records and a fixed internal
machine implementation. It has no ingress, ledger, authority signer,
persistence service or install endpoint. Runtime continues to own all those
operations. No new root field or native architecture action is introduced.
A literal Program submitted to this indexed registration, or an indexed
joint description submitted to the literal machine, is UNRESOLVED because
the machine has no funded translation. This is not native inadmissibility.
An externally supplied learner state is not a construction proposal.

The fixed owner accepts neither an external partition plan nor an external
numerical answer. It calls its trusted preparation and exact readout kernels
after the appropriate debits. This uses the existing
[singleton-plan elimination](SINGLETON_PLAN_ELIMINATION.md) boundary. The
passive independent-input plan checker remains useful for component audits;
running it again would not create another source of authority inside this
fixed dispatch. Replacing a trusted private kernel, arbitrary process-memory
writes or concurrent mutation of the owner are outside this serialized API
claim. No Python sandbox is asserted.

## 2. Complete native relation and continuation

Write J for the number of rates, S for their common denominator, P for the
prior denominator, and D=n(n-1)/2. The retained `JointCountState` has the
complete model, all D signed counts d, diagonal balance s, committed optimizer
steps T, ordinary cursor and pending ordered query/target. `JointState` also
retains all 2J+1 exact gradient forms during a pending unit. Its decoded
parameter record includes T. Zero d and s do not imply initial rate weights.

For an anchored world z, let

`E(z) = s + SUM_e d_e (1 - 2*parity_e(z))`,
`m(z) = (T+E(z))/2`, `a_j=S*eta_j`, `b_j=S-a_j`.

The selected native parameter is exactly

`theta_(j,z) = (P*pi_j) b_j^m(z) a_j^(T-m(z)) / Z`,

where Z is the sum over every rate and anchored world. Fixed slot zero is
one. The count lattice makes the exponents nonnegative integers. This is a
point decoder of the original native parameter, not a floating master array
or a conditional-factor replacement.

For an actual categorical query, integer construction gives the same native
excesses `N_y/Z`, masses `M_y=1+N_y/Z`, normalizer S and probabilities M_y/S.
All interior source/PRODUCT/feature nodes are determined by that query and
the original integer coefficient for their rate/world/label. `JointEvaluation`
retains the complete predecessor and query as well as those exact readouts
and executed table statistics. Explicit full materialization checks its
entire output allowance before enumerating any worlds.

After actual target y, the fixed-slot gradient and every selected class are

`g_fixed = 1/M_y - 2/S`,
`g_(j,match/other) = (S-2)/S - c_(j,match/other)/M_y`.

The pending query/target selects the right form for each original slot.
Observation advances the local cursor and opens the unit, without changing
theta. Commit is the original unit simplex step. The complete native
derivation gives `theta'_(j,z)=theta_(j,z)*ell_(j,z,y)/p_y`, so incrementing
the actual signed coordinate and T realizes exactly that update. The fixed
slot stays one; gradients and the pending unit clear. Neither target choice
nor native predecessor comes from a supplied cache or helper result.

The invariant applies by induction to each successful ordinary phase.
Runtime constructs every active lineage's successor locally and publishes
them together. If the second lineage fails after the first local commit,
neither published learner advances. The actual target, both observed states,
the first local commit and all paid work remain retained.

Profile construction starts at the declared prior, replays only registered
already-revealed observations, and counts every optimizer step. Attachment
changes only the ordinary cursor. In the audited two-pass profile, birth at
ordinary cursor two has T=4; after ordinary cursor eight, the original and
profiled lineages have T=8 and T=10. A failed profile retains its actual
completed prefix and never publishes an attached candidate.

The whole-domain range proof is immediate from positive normalized weights:
both masses lie in `[S*eta_min, S*(1-eta_min)]`, the normalizer is exactly S,
and every activation is bounded by the largest actual integer coefficient
or one. Range evidence binds the full registered model and categorical
domain. It does not infer admissibility from one observed source row.

## 3. Paid storage, construction and failure lifetime

Let L be the registered live-cell cap, I the integer-bit cap, Q the committed
step cap, and `h=ceil(log2 S)`. Runtime prepays and pins one actual byte extent

`W = (L+5) * ceil(min(I, n+bit_length(P)+(Q+1)*h)/8)`.

It is a `joint_noise_integer_partition_workspace` owned by the retained
information owner for the root's entire lifetime. The live table region and
two per-rate roots are reused; three other cells retain N0,N1,Z. A borrower
gets a separate memoryview. Releasing it cannot unpin the owner's export or
resize the backing array. All lineages use that same extent serially.

Before entering integer construction, the ordinary or profile path charges
`joint_partition_decoder.construction_work`. This funds the bounded complete
count/geometry scan, powers, all J rates' table arithmetic and aggregation,
byte traffic and forward compaction. The component's actual operation counts
must equal its whole-mixture preflight. Work is not divided by J merely
because the storage is reused.

After preparation, a separate debit
`128*(D+J+integer_envelope+32)` precedes rational readout and record scans.
The ordinary owner separately charges observation, commit, range checking,
ingress, retained evidence and state coexistence. Profile work is compiler
work; ordinary deployment and shadow lineages keep their existing roles.

These tariffs are declared scalar/index/byte work, not bigint bit complexity,
physical execution time or all CPython memory. W counts the actual integer
table bytes, not plan metadata, temporary bigints, snapshots or retained
Runtime records. The packed ledger counts those retained buffers separately.
These exact CPU audits do not establish a whole-host or GPU resource bound.

Type/query/state, T, precision, geometry and whole-mixture arithmetic
preflights precede the first table write. Refusal preserves the old scratch.
An admitted later fault may change scratch; the entire paid extent stays
owned and pinned, including while failed frames retain references. No spent
work is refunded. Failed construction, decoding or replay cannot erase a
received context, observed target or completed native history.

The registered algorithm is deliberately partial under its finite limits.
A precision or width refusal is UNRESOLVED, even if another algorithm could
answer cheaply. For example, a new leaf query on a legally acquired four-edge
star exceeds the tested natural-order join cap. It does not establish any
representation-independent resource lower bound. Likewise a zero-count
two-step history exceeds a one-step cap because its noise evidence persists.

## 4. Fresh reference evidence and exact authority scope

The existing persistence owner can retain these complete learner records and
derive its ratio bounds from the same native mass intervals. Admission still
precedes the first future score, binds both owned lineages and consumes its
declared alpha. Historical profile data do not become fresh observations.

The audit runs both this indexed machine and an independently constructed
literal Program Runtime. After sixteen label-one observations, each creates
a new prior-initialized candidate and admits reference persistence before
twenty future label-zero observations. Every comparison of initial/current
learners, score probabilities, gain intervals, epoch fields and wealth agrees.
The four fresh score events cross at cursor 20 with wealth 266119/65536.
Foreign-root candidate admission refuses. Retirement preserves spent alpha
1/4 and evidence while invalidating the live identity.

This is deterministic agreement of actual owned reference statistics under
a declared external stochastic-stream assumption. A finite test tape proves
no population law. The reference crossing supplies no paired AMP evidence
or installation path. Supplied `certified=True` and `bridge=True` flags still
return UNRESOLVED.

An empty owned Compiler policy can seal the eight-event reference stream.
Its closure has zero constructor decisions. Neither the seal, fresh crossing
nor the exact native comparisons issue CERTIFIED_COMPLETE. New joint-class
search and complete installation remain unregistered; no earlier decision
class is enlarged by this work.

## 5. Minimal evidence

Run `python -X utf8 -B scripts/audit_joint_runtime.py --write`.
[FP_JOINT_REFERENCE_RUNTIME.json](../../evidence/minimal/FP_JOINT_REFERENCE_RUNTIME.json)
retains only aggregate results and the small discriminating witnesses:

- All 516 two-event histories for n2/n3 S=20, n2 S=120 and one-rate n2 S=3:
  1,032 actual owned native triples, including all caches, parameters and
  ambient gradients against independent literal native execution.
- Four profile triples and fourteen ordinary lineage triples through cycle
  closure, cancellation, diagonal evidence and distinct profile/ordinary clocks.
- Eight actual n64 events over 2^64 native hypotheses, independently checked
  against the passive positive-tape decoder. World expansion is forbidden in
  the owner test. Its table extent is 29,841 bytes; the packed root's observed
  peak is recorded separately. Explicit whole-output expansion refuses.
- Separate pre-construction/readout work denials, zero-count T exhaustion,
  precision and tree-width refusals before writes, allocation denial before
  creating unpaid scratch, a failed replay prefix and a post-construction fault.
  Released borrower views and failed frames cannot unpin the owner's extent.
- Registration, wrong model/state, supplied plan, locked-event and invalid
  target/source attacks; actual second-lineage atomic failure; CUDA registration
  refusal before device creation; and the two-root fresh comparison above.

The component audit is also rerun with its updated cross-machine translation
boundary: the literal machine returns UNRESOLVED for the joint description.
The original unregistered result at e2802c8 remains a historical source-bound
statement. Relevant existing literal ordinary-event and known-rate indexed
profile, closure and adversarial checks pass. No Torch/device execution is
performed and no terminal GPU job is rerun.

The next unresolved boundary is a separate owned physical implementation of
the joint-excess schedule: independent actual-input/complete-state binding,
primitive mixed-precision conformance, complete resource and failed-phase
lifetime, then fresh paired evidence and install reachability. The S=20
uniform numerical theorem supports that schedule conditionally; the S=120
counterexample and both terminal dense rational A1/A2 outcomes remain intact.
