# Joint native indexing and shared positive integer storage

Status: **DERIVED, EXACT COMPONENT AUDIT PASS**. The canonical finite-noise
relation learner now has an exact indexed G/Gamma/U description, a closed
complete count encoding, and a contiguous positive integer decoder. This
implements the integer construction required by the
[joint-excess bridge](JOINT_EXCESS_PARTITION_BRIDGE.md). It adds no semantic
architecture action and makes no change to the original native learner.

This component is deliberately not registered with ReferenceCompilerRuntime.
An admission test confirms that Runtime rejects the new indexed description.
Caller-owned bytes and a checked passive plan do not establish paid Runtime
ownership, provenance, fresh persistence, install reachability or a CUDA phase.
The existing production registrations and terminal GPU outcomes are unchanged.

## 1. The indexed description is the actual native graph

Let J be the number of ordered distinct rational rates in (0,1/2), with positive
rational prior pi. Put V=2^(n-1), K=JV, and S=lcm of the rate denominators.
The current indexed implementation has 2<=n<=1024 and S<=2^24; these are
implementation and arithmetic limits, not limits on Foundation semantics.

The decoder's source domain is the complete set of n^2 ordered one-hot pair
rows. Current source membership is checked on every bound call. Eventual
Runtime registration must also bind that entire declared domain; fitting one
current row would not justify using this decoder for a broader future input
interface. The literal graph itself still has its ordinary native semantics.

`JointRelation(n,rates,prior)` orders hypotheses by rate, then by the original
big-endian anchored world enumeration. It describes exactly:

1. The 2n native categorical sources, in left/right order.
2. All n^2 actual pair PRODUCT nodes, in ordered query order.
3. Two feature SUMs per hypothesis. For hypothesis (j,z) and target y, pair
   (u,v) occurs S*ell(j,z,u,v,y)-1 times, bound to the fixed slot t=1.
4. Two head SUMs. Each contains its corresponding feature once, bound to
   that hypothesis's selected parameter slot.

Repeated SUM incidences remain real native syntax. In particular, this graph
is not interchangeable with the older known-rate indexed graph, which puts
its repeated factor eight on the heads and has different interior caches.
An equivalent forecast alone would not prove a complete native relation.

The exact counts are

`nodes=2n+n^2+2K+2`, `PRODUCTs=n^2`, `SUMs=2K+2`,
`SUM_edges=K*((S-2)*n^2+2)`, `slots=K+1`.

For a feature, let z have o ones and n-o zeros. There are
`E=o^2+(n-o)^2` parity-zero ordered pairs. Its arity is
`c_match*E+c_other*(n^2-E)` for y=0, with E and n^2-E exchanged for y=1.
The point incidence decoder scans the ordered source pairs and subtracts
their exact repeat counts; it never enumerates the other worlds. Thus node
headers and ordered term reads are computable from the description. Explicit
materialization still preflights the full native node/term/slot outputs.

Gamma sets t=1 and theta_(j,z)=pi_j/V. U is the unchanged unit-rate,
one-event, no-grid simplex optimizer on all K selected slots. Complete
literal comparison checks the graph, source/type/base declaration, Gamma
and U, rather than comparing only their initial probabilities or a hash.
The indexed identity names the full description, including its prior; it
does not pretend to be the hash of an expanded Program.

The audit compares six complete literal graphs/Gamma/U instances at n2..4
for the S=20 and S=120 rate banks. Wrong heads, bases, prior weights and
learning rate all fail the complete comparison. Typed recursive checks also
reject extra declaration fields and a boolean source delay equal to integer
zero under ordinary Python equality.

## 2. Complete retained coordinates and canceled histories

`JointCountState` retains the entire model, all n(n-1)/2 signed nonloop counts,
diagonal balance s, ordinary cursor, optimizer-step clock T and pending
ordered query/target. Types and extra fields are checked; clocks have the
declared finite implementation envelope 0..2^62-1. Counts satisfy

`SUM |d_e|+|s| <= T`, `T-SUM |d_e|-s` even.

Observe advances only the ordinary cursor and pending unit. Commit increments
the actual signed coordinate and T, then clears the unit. Attach requires an
empty unit and changes only the ordinary cursor. A late birth or profile
attachment must not make that cursor a substitute for T. These field checks
are not a proof that an external caller owns the corresponding history.

The complete-state proof remains the prior joint likelihood theorem. In
particular, with H=SUM |d_e|, A=(T+s-H)/2 and B=(T-s-H)/2, every rate keeps
its own constant `C_j=P*pi_j*b_j^A*a_j^B`. Cancellation removes a parity
factor from current support but does not remove its rate evidence.

The decoder therefore has a **committed-step allowance**, not just a support
or absolute-count allowance. With d=0,s=0,T=4, a step cap of three refuses
before touching scratch even though H=0. The uniform bit envelope

`b=n+bit_length(P)+(T+1)*ceil(log2 S)`

depends on T. Treating the canceled state as the initial state would invalidate
both posterior continuation and resource admission. Profile multiplicity
counts as actual optimizer steps even when it reuses ordinary observations.

## 3. One contiguous table region is shared by all rates

`joint_partition_decoder.prepare` accepts a complete committed state, ordered
query, explicit elimination order, allowances and an exact-size writable
contiguous byte view. `prepare_bound` first derives the ordered query from
independently supplied native syntax, semantics and complete source values;
the state's entire model must match. Default order is natural order. This
component does no uncharged order search.

Let L be the allowed live table cells and C the byte width determined by the
declared step cap, model and integer limit. The exact supplied extent is

`(L+5)*C` bytes.

The first L cells hold the active tables, joined table and reduced result.
Two following cells hold the current rate's parity roots. Three final cells
accumulate N0,N1,Z. Every numeric table access goes through this byte extent;
there is no retained parallel array with one bigint per tape node.

For each rate, build both positive edge powers, write the initial tables,
then perform ordinary positive elimination. After reducing a variable,
compact surviving tables toward the front. Descriptors remain ordered by
their source offsets. Every destination is at most its source, so increasing
source traversal cannot destroy an unread value, including overlapping moves.
This invariant holds for any supplied complete elimination order, not just
the default. Query endpoints are retained until the final parity sums.

Multiply both rate roots by C_j and accumulate their actual integer excess
coefficients and normalization. Clear and reuse the table/parity region for
the next rate, preserving the three joint roots. On return,

`N0+N1=(S-2)*Z`, `Z>0`.

The extent size has no factor J other than the effect of the declared rate
denominators/prior on C. J still multiplies integer work and contributes to
the model and eventual gradient storage. The returned three bigints, scalar
temporaries, dense count encoding, table metadata and caller's state/evidence
records are separate storage. This is not a total Python heap bound.

## 4. Preflight and exact operation accounting

Before the first workspace write, check all of the following against the
actual complete inputs: committed phase, T cap, integer/readout precision,
query, full order, support, join/live geometry, total positive integer work,
and extent size/format. The scalar-rounding margin remains 1,024 bits beyond
the integer envelope, with at least 1,075 reference bits for exact RNE checks.

Let M_g,A_g be the single-rate geometric multiplication/addition counts,
including its final parity-root sum, and let

`p(e)=popcount(e)+bit_length(e)-1` for e>0, `p(0)=0`.

The implemented binary powers and full aggregation use exactly

`M = J*[M_g+2*SUM_e p(|d_e|)+p(A)+p(B)+8]`,
`A_total = J*(A_g+6)`.

Both totals are checked before powers, then matched against actual execution.
This engine performs one raw root-sum addition per rate that the earlier
tape prototype omits; their operation counts intentionally differ by J.
Compaction copies at most `J*(n-1)*L` integer cells. Clears, byte reads/writes,
index projections and metadata scans are additional work, not free positive
arithmetic. The module exposes a conservative scalar/index/byte construction
tariff for a future owner; it is not an elapsed-time or bigint bit-time law.
Whole-host admission, validation and retained records remain separate.

The passive plan retains its complete predecessor, ordered query, order,
integer roots, geometry, operation counts, compaction, bit limits and exact
byte layout. `check_bound_plan` independently reconstructs them from the
owner-supplied inputs. It rejects even jointly doubling N0,N1,Z, although
that mutation preserves every current normalized readout. Exact part identity
and derivation are obligations separate from forecast equality. Reconstruction
also costs work and uses its supplied extent; it is not a free certificate.

Preflight refusal leaves scratch unchanged. After an admitted arithmetic
failure, scratch may have changed and traceback frames may still refer to it.
The component never commits a learner or refunds/releases a ledger lease.
The fault-injection audit keeps the caller's own pinned view alive after the
borrower exits and verifies that the backing buffer cannot resize. Runtime
must eventually own that lifetime; this test does not supply the owner.

## 5. Minimal evidence and exact remaining boundary

Run `python -X utf8 -B scripts/audit_joint_partition_storage.py --write`.
The [retained artifact](../../evidence/minimal/FP_JOINT_PARTITION_STORAGE.json)
records aggregate counts and bounds:

- Six complete literal G/Gamma/U comparisons, eight literal-binding refusals
  and three materialization-output refusals.
- All 1,516 reachable small cuts through T=3, with 21,604 ordered-query
  comparisons to independent world sums and 64,812 direct reads of the three
  packed joint root cells. External canary bytes remain unchanged.
- All six elimination orders for sixteen n4 ordered queries: 96 independent
  tape comparisons under changing signs, a cycle, diagonal evidence and T>H.
- Four one-rate endpoint checks at S=3 and S=10, T=396, cover a true zero
  excess integer and a small positive excess on a concentrated state.
- 566 complete native prediction/observation/commit triples, including both
  labels, late birth and an 80-update profile/cycle/reversal continuation.
  Actual interior caches, fixed gradients and every selected slot are checked.
- Four n32/n64 cyclic-band queries against an independent vertex/energy
  histogram oracle. The n64 three-rate case uses 78,584 table bytes, 1,088
  executed integer bits, 5,424 positive multiplications, 765 additions and
  45,396 compaction-cell copies. It represents 3*2^63 native worlds.
- An n256 three-rate path agrees with the independent positive forest decoder
  over 3*2^255 worlds: 531,727 table bytes, 1,787 maximum integer bits, 7,665
  multiplications and 1,551 additions. These are exact CPU queries, not model
  comparisons, owned continuations or GPU experiments.
- Seventeen plan mutations, seven complete-input substitutions, five prewrite
  resource boundaries, canceled-height-zero exhaustion, three malformed extents
  and dense n16 width all refuse. A postwrite fault preserves the count state
  and the caller's pinned extent. Runtime rejects the unregistered description.

The S=20 numerical theorem still applies to these exact roots under its
declared scalar schedule. No device operation is inferred from integer
agreement, and the S=120 numerical counterexample remains. The next boundary
is registration inside the existing owner: prepaid construction/verification,
complete Reference and actual AMP state/evidence, retained failure lifetime,
lineage, fresh persistence and installation. This component returns no
CERTIFIED_COMPLETE and establishes no new constructor decision class or
Foundation/ERC-1 revision.
