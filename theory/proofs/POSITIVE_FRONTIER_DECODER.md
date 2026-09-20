# Correlation-preserving positive decoding from count state

Status: **PROVED, SCOPED; EXACT COMPLETE-NATIVE AUDIT AND TAPE DIAGNOSTICS**.
This applies classical positive variable elimination to the existing
[phase-level count encoding](COUNT_LEARNER_ENCODING.md). It retains joint
correlations. It is a decoder for the original literal world-slot learner,
not a product-belief approximation, new native Program or replacement for
its complete finite-arithmetic execution. No Runtime, resource reservation,
AMP bridge, installation or constructor completeness is granted.

The distinction from the [query-matroid law](FACTOR_QUERY_MATROID.md) is
essential: needing one factor with many categories does not imply that its
encoded law is expensive to decode. A cycle requires one full-world factor
under any fixed independent-factor encoding, yet its exact forecasts admit
linear positive computation. On the retained model tapes, the first full-
rank query component also precedes large elimination width.

This is an application of the known-factor frontier principle in
`FP_THEORY.md`, section XI. Variable elimination and its induced-width
analysis are classical; see [Dechter (1999), *Bucket elimination: A unifying
framework for reasoning*](https://ics.uci.edu/~dechter/publications/r76A.pdf).
The contribution here is the exact connection to FP's actual count state,
complete native cache/gradient, and exposed model histories. No new general
graphical-model inference theorem is claimed.

## 1. Exact positive factors, including negative and canceled counts

Fix the literal known-noise relation learner, uniform Gamma, unit learning
rate, one-event units and no grid, as in the count-encoding theorem. Keep
the full signed unordered nonloop count vector d, pending event, ordinary
cursor and optimizer-step clock. Counts include actual profile repetitions.
The surrounding source identity, provenance and physical evidence remain.

Let H be the number of committed candidate events and L=SUM_e |d_e|<=H.
For each nonzero edge count define a positive integer factor

`f_e(b) = 9^|d_e| if b = 1[d_e<0], and 1 otherwise`,

where b=z_i XOR z_j and z0=0. Put

`W(z)=PRODUCT_e f_e(z_i XOR z_j)`, `Z=SUM_(z:z0=0) W(z)`.

This W differs from `9^(SUM_e d_e*1[z_i=z_j])` only by the common multiplier
`9^(SUM_(d_e<0) |d_e|)`. Consequently theta_z=W(z)/Z is exactly the native
posterior weight, including negative signed counts. The construction avoids
negative or fractional intermediate factors.

An edge with d_e=0 has factor identically1 for every world and can be absent
from this particular decoder call. Its count coordinate, actual events and
clocks remain. A later observation updates d and may restore the edge. This
is exact scalar simplification at a known state, not erasure of a native
feature node, ambient derivative or future observation.

Pinning the known anchor makes factors incident to vertex0 unary. Let G_d
be the graph on free vertices1,...,n-1 with edges ij for i,j>0 and d_ij!=0.
Its width, rather than the rank of the whole query family, controls the
following computation.

## 2. Positive elimination for every current pair query

For the actual query(i,j), retain its distinct free endpoints Q, with
t=|Q|<=2. Eliminate all other free variables in an order sigma. At each
eliminated variable v, multiply every factor containing v, then SUM over
v=0,1. Preserve the resulting complete table on its remaining variables.
An unconstrained variable contributes a factor2; it is not silently forgotten.
Finally multiply remaining factors on Q and sum entries according to the
query parity, giving

`Z_y = SUM_z W(z)*1[z_i XOR z_j=y]`, `Z=Z_0+Z_1`.

For a diagonal query Z_1=0. All internal table arithmetic is positive
SUM/PRODUCT on integers. The native readout is recovered as

`A_y=8*Z_y/Z`, `M_y=1+A_y`, `T=10`,
`p_y=(9*Z_y+Z_(1-y))/(10*Z)`.

The final divisions are in this mathematical decoder, whose inputs are the
owned count coordinates. They are not extra native arithmetic actions or
new parameter-valued causal sources. Each elimination is ordinary finite
distributivity, so induction proves equality with complete world enumeration.

**Width upper bound.** Start with any complete elimination order of G_d
having induced width w. Delete Q from that order and retain those variables
until the final table. The resulting largest join has at most w+t+1
variables, hence at most2^(w+t+1) integer cells.

To see this, two surviving vertices are adjacent after an eliminated set S
iff an original path between them has all internal vertices in S. This
follows inductively from clique fill at each elimination. Before eliminating
a non-Q vertex, the new eliminated set is the original prefix with Q removed.
Its neighbors outside Q are therefore a subset of the original neighbors;
at most t retained query variables have been added. This proves the bound.

If m counts are nonzero, each original factor or generated message is
consumed once. Given the order and factors, table work is

`O((m+n)*2^(w+t+1))` positive scalar operations.

A conservative live-table bound is `O(m+n*2^(w+t+1))` integer cells. Actual
join/input/output coexistence is counted in the audit. These are arithmetic
and logical-cell statements, not Python heap or device-memory bounds.
Scanning a dense D=n(n-1)/2 count vector, constructing powers, searching for
an order, metadata and complete native output are additional costs. Binary
powering needs O(SUM_e log(1+|d_e|)) integer multiplications; the audit's
reported operation counts concern table joins/sums only.

**Bit bound.** Every message entry is a sum of at most2^(n-1) products of
disjoint original factors. Its value is at most2^(n-1)*9^L. The same bound
holds during a positive join: consumed factor sets and already summed
variables are disjoint across input messages. Thus partition arithmetic
uses at most n+4L integer bits, and scalar readout numerators/denominators
need at most four more. Every decoded native parameter, cache mass or
gradient coordinate has O(n+H) reduced rational bits. This avoids the
[exponential-in-history factor-state height](FACTOR_REPETITION_DYNAMICS.md),
while leaving exponential dependence on width possible.

An order is an algorithmic choice inside the decoder, not a semantic
architecture action. A cheap witnessed order supplies a valid upper bound
without claiming optimality. Finding the minimum can itself be expensive.
The audit uses a subset minimax dynamic program only through15 free vertices.
For each eliminated set S the path characterization determines the next
degree independently of its internal order; minimizing the largest degree
over all subset transitions is exact. An independent clique-fill enumeration
checks this minimum on every simple graph through five vertices. This exact
decision class consists only of vertex elimination orders of the specified
anchored graph; it is not all decoders or all native Programs.

## 3. Complete reference state survives, but explicit output is still large

The count-encoding theorem's phase transition diagram is unchanged. The
new decoder computes its normalization and query marginal by elimination
instead of enumerating every world. A requested world weight is W(z)/Z.
At an observed but uncommitted cut, for the actual pending target y and
`I_z=1[z_i XOR z_j=y]`, its complete native gradient is

`G_fixed=1/M_y-1/5`, `G_z=4/5-8*I_z/M_y`.

The actual pending event and clocks remain necessary. In particular a
diagonal event changes the observed gradient and cursor despite unchanged
posterior counts. Committed gradients are all zero. Profile attachment
changes the ordinary cursor, preserving its executed count multiplicity
and optimizer-step clock.

Every cache coordinate is likewise recoverable: the actual one-hot source
row, n^2 pair indicators, both parity indicators per world, two excesses,
masses, normalizer, probabilities and empty delayed state. No fixed-feature
gradient or inactive native node is dropped. Small native audits materialize
and compare all these fields, not just the final forecast.

This establishes complete **reference learner/cache decoding**, using the
existing count representation. It does not make explicit output free. A
request for the full K=2^(n-1) parameter vector, full gradient or literal
cache still has Omega(K) output coordinates. Decoding one requested coordinate
and representing the entire vector implicitly are different tasks.

Nor do these exact formulas reproduce the original binary64 or AMP operation
words merely by rounding their answers. The literal finite-arithmetic path
has its own operation order, intermediates, gradients and retained phase
frames. Replacing its executor or encoding those frames requires a complete
paid realization and bridge proof. None is issued by this passive solver.

## 4. One irreducible component can have a cheap decoder

Let the active observation graph be a single cycle on n>=3 vertices. Its
query vectors form one matroid component of rank n-1. The fixed independent-
factor closure theorem therefore requires a factor with2^(n-1) categories,
even if nonlinear world coordinates are allowed.

After pinning vertex0, however, its free-variable graph is a path with
width1. Every current pair forecast has a positive O(n) scalar decoder
by section2, with constant-sized join tables and O(n+H)-bit integers. The
factor need not be an explicit table of categories.

An independent positive cycle oracle makes the correlation explicit. For an
arc maintain even/odd edge-parity weight totals E,O. On its next factor
(a,b), update

`(E,O) <- (E*a+O*b, E*b+O*a)`.

The two arcs between query endpoints must have equal total parity because
their union is a cycle. Hence `Z_0=E_left*E_right` and
`Z_1=O_left*O_right`. The missing cycle constraint is never approximated.
This differs fundamentally from projecting onto independent edge marginals.

The audit checks cycles through n64, where the categorical requirement is
2^63 yet the largest actual join has eight cells. Its six n64 queries each
agree with the independent arc oracle; the largest table-work count is1,237
positive operations and the largest integer has309 bits. No n64 native
world-slot graph, Runtime worker or AMP state is built for that decoder test.

This is a counterexample to inferring exponential decoder cost from a single
full-rank query component. It does not keep width bounded under arbitrary
later observations: new chords can increase it, and the full count state
must continue to represent them. The complete-graph positive partition lower
bound and the general conditional forecast-hardness result remain intact.

## 5. Retained-tape structure: an early opportunity, a later cost

All eight existing RN-5 tapes are inspected at the training cut, the first
full-rank active query component, and the final cut. Each table entry below
is the exact minimum width of the anchored free graph, computed by the
finite subset DP. Six fixed pair queries per snapshot are independently
checked against all-world integer enumeration:144 partition comparisons.

| Case | Training width | First full-rank component width | Final width | Largest final join, cells |
|---|---:|---:|---:|---:|
|n8/c2/16|1|3|4|64|
|n8/c2/17|1|2|5|64|
|n8/c4/18|1|1|5|64|
|n8/c4/19|1|2|5|64|
|n16/c2/16|1|4|11|4,096|
|n16/c2/17|1|5|11|4,096|
|n16/c4/18|1|4|11|8,192|
|n16/c4/19|1|4|11|8,192|

The full-rank component thus does not immediately force enumeration of all
128/32,768 worlds. At the same time, the dense final graphs are materially
harder for this decoder. The four final n16 snapshots require up to243,903,
252,841,350,773 and281,209 positive table operations respectively over the
six checked queries. These numbers exclude order search and the other costs
listed above. They are not GPU speedups, job-memory measurements or evidence
that the complete n16 likelihood worker now fits its resource contract.

## 6. Minimal reproducible evidence

Run `python -B experiments/joint_uncertainty/positive_frontier_decoder.py`.
The [minimal report](../../evidence/minimal/FP_POSITIVE_FRONTIER_DECODER.json)
contains counts, width witnesses and small tables, with no posterior cache:

- 1,099 small graphs and124,469 independent elimination orders check exact
  width minimization against direct clique fill.
- 759 signed-count profiles and11,919 all-pair integer partition checks
  cover negative, zero and positive counts, diagonals and both orientations.
- 953 complete native caches and1,906 observed/committed states agree,
  including three repeated profiles with clock attachment and continuations.
- Six cycle sizes separate categorical irreducibility from decoding width.
- 24 retained-tape snapshots and144 exact query partitions agree with the
  independent integer world oracle.
- Two declared order/bit refusals occur before subset allocation or a huge
  likelihood power, rather than pretending the exact solver has completed.

This supplies a concrete exact decoder for structured correlated states. The
remaining implementation question is an owned physical realization that
preserves the required complete finite-arithmetic evidence and pays its
costs. It is not solved by substituting this helper into a Runtime forecast.

The [finite-mantissa continuation](RADIX9_FRONTIER_PRECISION.md) addresses
the decoder's numerical range: a frustrated triangle defeats independent
local scaling, while per-entry integer exponents give a positive-tape error
bound independent of count magnitudes. Its finite CPU evidence and completed
273,832-word actual CUDA diagnostic remain separate from the complete native
bridge required here.
