# A linear-size positive circuit for all relation marginals

**Status: proved under the stated source and parameter interface; exact native
audit passed.** This is a new ordinary SUM/PRODUCT Program. It preserves the
relation learner's predictions and selected unit-simplex updates, while
retaining its own complete gradient and evaluation state. It is not a quotient
of an installed learner, a Runtime certificate, or a measured GPU result.

The [executable construction](../../experiments/joint_uncertainty/positive_pair_marginals.py)
and [minimal audit](../../evidence/minimal/FP_POSITIVE_PAIR_MARGINALS_AUDIT.json)
use the existing native Program, exact evaluator, reverse gradient, and
registered observe/commit operations.

## 1. Interface and claim

There are n >= 2 tokens, m = n-1 independent binary latent bits, and
K = 2^m worlds z = (0,z1,...,zm). The complete legal source domain consists
of every ordered pair of one-hot token vectors x0,x1. Each source has the
existing nonnegative mass type and range [0,1]. The positive readout base is
(1,1). Parameter slot zero is fixed at a = 1; selected slots contain every
world weight w_z >= 0, with sum_z w_z = 1. No world or low-weight coordinate
is erased. The fixed initializer is (1,1/K,...,1/K).

For query (i,j), define s_y = sum_{z: z_i xor z_j = y} w_z. The desired
native masses are M_y = 1+8*s_y, total mass 10, and forecast M_y/10.
These are the existing known-noise relation forecasts. The new circuit
uses O(K+n^2) nodes and incidences, compared with O(n^2*K) incidences in
the literal world-by-query construction. Any explicit-slot circuit valid
for all independent simplex weights must read at least K-1 selected
coordinates. Consequently the new circuit's incidence order is Theta(K).

This is an explicit-coordinate circuit law. It is neither a lower bound on
the [count encoding](COUNT_LEARNER_ENCODING.md) nor a replacement for the
[compact-family decoding complexity theorem](FORECAST_DECODING_COMPLEXITY.md).
K is still exponential in n. Integer bit sizes, graph serialization,
construction work, lifetime evidence, and physical peaks are separate costs.

## 2. Positive construction

The actual native node L = SUM_i a*x0_i equals one on every legal row.
A weighted leaf is the edge Term(L, slot(z)); it need not have a separate
node. Every internal binary sum uses the existing fixed slot a on its
incoming edges. The following equalities are evaluated at a = 1.

First build the complete prefix-sum tree:

    U_p = sum_{z whose nonanchor bits start with p} w_z.

Leaves are the weighted edges above; U_p = U_p0+U_p1. This uses K-1
binary SUM nodes. U_empty is the total weight, retained as an actual value.

For each bit j in 1,...,m and b in {0,1}, construct a filtered prefix tree
H[p,j,b] for |p| < j. At depth j-1, reuse U_(p+b); at earlier depths use
H[p,j,b] = H[p0,j,b]+H[p1,j,b]. Its value is the mass with prefix p
and bit j equal to b. Across both b, bit j adds 2^j-2 binary SUMs, for
2K-2-2m altogether. It reuses the prefix sums over all later bits.

Anchor pair (0,j) has parity masses H[empty,j,0] and H[empty,j,1].
For 1 <= i < j <= m, parity y is the balanced sum

    A_(i,j),y = sum_{p in {0,1}^i} H[p,j,p_i xor y].

The summands partition the required worlds: the last prefix bit fixes
z_i, and the filter fixes z_j. Each parity uses 2^i terms and 2^i-1
new binary SUMs. All nonanchor pairs together add

    sum_{j=2}^m sum_{i=1}^{j-1} 2*(2^i-1)
      = 4K-4-m^2-3m

nodes. Thus the marginal stage uses exactly

    A = 7K-7-m^2-5m

binary SUMs. At n=2 only, the two final anchor marginals are still weighted
leaves; two singleton SUMs materialize them for PRODUCT parents. This is
the ordinary boundary case of the same construction.

Build q_ij = x0_i*x1_j for every ordered pair. For each i<j, the actual
binary SUM q_ij+q_ji selects its unordered pair. Multiply this selection
by each A_(i,j),y. Diagonal query i uses q_ii*U_empty for label zero;
its label-one excess is identically zero. Sum each label's contributions.
At a legal row exactly one unordered or diagonal query is active.

Finally create eight from L by three actual doubling SUMs and multiply
each label sum by it. No coefficient eight, constant source, fitted
parameter, or new primitive is supplied. Only positive SUM and typed
PRODUCT nodes occur. This gives precisely excesses 8*s_y.

Every marginal is a positive sum over a subset of worlds, hence at most
one. Query selectors and unscaled label heads are also at most one on the
legal domain. The doubling nodes have values 2,4,8; all native activations
lie in [0,8], and the readout total is 10. This is an exact range statement,
not an AMP error guarantee.

## 3. Native learner and complete-state distinction

At the fixed feature value, masses are affine in all selected coordinates,
with the same total coefficient eight in every world column. The actual
CE derivative for selected slot z is therefore

    G_z = 4/5 - 8*I[z_i xor z_j = y]/M_y.

With the registered unit-event, unit-rate normalized simplex gradient,
the [existing affine posterior lemma](SIMPLEX_GRADIENT_POSTERIOR.md) gives

    w'_z = w_z * (1+8*I[z_i xor z_j = y]) / M_y.

The native normalization operation has exact denominator one. Induction
gives the same selected parameter trajectory and forecasts as the literal
Program for every finite legal query/label continuation from the same
weights, including registered profile repetitions. Bounded arithmetic
still requires sufficient actual resources; the theorem supplies none.

The complete learners differ. For n>=3 every marginal used off the
diagonal has feature-slot degree m-1: the filtered and final balanced
sums place exactly that many fixed-slot factors along each weight path.
U_empty has degree m. The extra query-selector factor in off-diagonal
paths makes every unscaled label contribution have degree m+1 after its
head edge. The native eight node has degree four. Thus the complete
excess at a general feature value is 8*a^(n+4)*s_y. At a=1,

    G_fixed,new = (n+4)*(1/M_y - 1/5),
    G_fixed,literal = 1/M_y - 1/5.

For n=2, weighted-leaf materialization instead gives degrees six on a
diagonal query and seven off the diagonal. At the fair n=2 initializer,
query (0,0), target zero, both masses are (9,1), but the fixed gradients
are -8/15 and -4/45. Both actual observed states retain their own value.

The fixed slot is not updated by this selected-block optimizer; that fact
does not authorize discarding its gradient accumulator, caches, Program,
resource history, or lineage. A future Runtime use must construct a new
candidate with its actual graph, profile and evidence. No transport of
an existing installed learner follows from forecast agreement.

## 4. Exact incidence and registered schedule counts

For n>=3 the emitted graph has:

| Quantity | Shared marginal Program |
|---|---:|
| Sources | 2n |
| Selected/fixed slots | K+1 |
| SUM nodes | 7K+3-(n^2+7n)/2 |
| PRODUCT nodes | 2n^2+2 |
| All nodes | 7K+5+3n(n-1)/2 |
| SUM incidences | 14K-6n |
| All incidences | 14K+4n^2-6n+4 |

For n=2 add two to SUM nodes, all nodes, SUM incidences and all incidences.
The audit constructs the actual graphs through n=16 and checks these
counts; it retains counts, not the large graphs.

Substitution into the current generic CUDA lowering's actual `output_cells`
schedule gives, for n>=3,

    predict = 57K+3n^2-19n+24,
    observe = 66K+(19n^2-51n)/2+24.

At n=2 add ten to each expression. The audit checks the expressions against
the registered schedule function. These are scheduled scalar-output cells,
not measured bytes or elapsed time; the graph has not executed on CUDA.

| n | Literal / shared nodes | Literal / shared incidences | Literal / shared observe cells |
|---|---:|---:|---:|
| 8 | 338 / 985 | 10,368 / 2,004 | 41,949 / 8,876 |
| 16 | 65,826 / 229,741 | 8,913,408 / 459,684 | 35,816,749 / 2,164,736 |

There is no coordinatewise resource dominance: nodes and PRODUCTs increase.
At n=8 the old experiment's twice-literal node/SUM/PRODUCT caps exclude
this graph. A new declaration is needed; no old finite decision class is
silently enlarged. Even this n=16 prediction/observation schedule exceeds
the existing 65,536-cell allowance, and its 65,540-cell initialization also
exceeds that allowance. No n16 likelihood execution recovery is implied.
The separately running n16 recovery experiment uses the older v5 model.

## 5. Incidence lower bound

Consider any fixed circuit with these K independent selected simplex
coordinates, required to return the forecasts above for every interior
weight vector and every legal query. If it reads fewer than K-1 coordinates,
at least two world coordinates a,b are never read. The distinct anchored
worlds disagree at some bit j. Starting from any interior vector, transfer
a sufficiently small positive mass from b to a. All read coordinates stay
unchanged and the total remains one, so the circuit output cannot change.
But the required probability on anchor query (0,j) changes by 4/5 times
the transferred mass, a contradiction. Each coordinate read requires at
least one parameter incidence, proving the lower bound.

Since n^2=O(K), the construction and this lower bound match in incidence
order. The constants are not claimed optimal. The hypothesis allows
independent simplex inputs; it cannot be applied to a compressed history
decoder, a restricted reachable invariant, a query-specific oracle, or a
complete Runtime memory bound. In particular it leaves the earlier
information-rank and count-encoding results intact.

## 6. Adversarial scope and evidence

Source ranges [0,1] alone are insufficient. At n=3 with uniform weights,
activate x0:0, x0:1 and x1:0 simultaneously. All individual source ranges
hold, but the literal forecast is (13/18,5/18) and the shared forecast is
(49/66,17/66). The proof requires the complete one-hot source domain, which
the existing Runtime ingress can enforce. The passive evaluator does not
claim that domain enforcement.

The exact audit covers 680 forecasts and 1,360 complete gradient checks
for n=2,...,5: every simplex vertex, uniform weights, a nonuniform rational
interior vector, every ordered query and both targets. An independent
forward dual propagation checks the fixed gradient against native reverse
AD. Selected gradients are checked against the formula and literal graph.
All query/label histories through depth three for n=2 and depth two for
n=3, plus eight two-pass profile/attachment cases, execute 966 native
observe/commit pairs and compare 1,932 complete new-Program states with
an independent oracle. There are also 155 unread-coordinate witnesses and
the two explicit equivalence/domain counterexamples above.

Run `python -B experiments/joint_uncertainty/positive_pair_marginals.py`.
Arithmetic is exact `Fraction`; native operations use the declared 32,768-bit
bound. These finite checks audit the proof. They do not grant construction
reachability, reference/AMP bridges, fresh persistence, installation,
model improvement, or `CERTIFIED_COMPLETE` for any decision class. Those
remain separate owned execution obligations. Foundation and ERC-1 are unchanged.
