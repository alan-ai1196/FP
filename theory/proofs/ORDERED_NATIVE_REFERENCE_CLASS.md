# Checked finite native coverage and reference endpoint comparison

Status: **implementation-level coverage and soundness argument**, with an
independent exhaustive audit in `scripts/audit_reference_search.py`.
`FP_THEORY.md` remains normative. This instantiates its existing grammar and
claim-relative proof boundary; it adds no architecture action or static
conditional-table family. Foundation and ERC-1 remain frozen.

## 1. The exact proposition

Fix the immutable semantic rules, separate finite caps
`(nodes, SUMs, PRODUCTs, edges, slots)`, registered initializer, and either
no profile or one registered finite profile. Let `G` be **every ordered
native Program** admitted by those rules and caps. An element includes its
declared slot count, all nodes, ordered weighted SUM edges, ordered PRODUCT
parents, readout roots and ordered complete delayed-body bindings.
There is no quotient by current values, gradients, support, commutativity,
unused coordinates, graph isomorphism or binding order.

At one ordinary update boundary, fix the actually revealed objective records
`D=(r_1,...,r_m)`, with distinct registered train/online IDs, and the deployed
reference program/state `B`. For each `g in G`, its value endpoint `V(g)` is
the registered initializer followed, if requested, by the **actually
executed** profile on its original logged observations. The deterministic
value rule reads no search rank or accumulated comparison result. Profile
keeps its local recurrence and attaches its complete endpoint to the common
ordinary boundary. It does not freely optimize parameters or reset a
previously evaluated lineage.

The objective evaluates each record's logged source context with the **same
frozen endpoint parameters and delayed buffers**. It does not advance an
ordinary or profile trajectory between objective records. Write

```
L(g) = product_i p_(g,V(g))(target_i | logged_sources_i),
L(B) = product_i p_B(target_i | logged_sources_i).
```

The sole issued proposition is that the retained live winner attains the
maximum of `L` on **`{B} union {(g,V(g)): g in G}`**, and that every member's
construction, whole-domain range check and objective computation completed
in this execution under the supported reference limits. Including `B` is
essential: a trained deployed baseline can lie outside the newborn grammar
and can win. When `G` is empty the proposition concerns `B` alone.

All bases are strictly positive and all native values are nonnegative, so
every factor is positive. Since the record count is common, maximizing this
exact rational product is precisely minimizing the mean empirical CE
`-log(L)/m`. No floating logarithm or fitted population table is required.
Guarded integer cross-products order rational likelihoods; inability to
complete that arithmetic is UNRESOLVED.

This proposition does **not** optimize all legal future continuations,
all profiles, arbitrary real/encoded parameters or an unknown population.
It does not say that every historical candidate remains simultaneously
resident. Nonwinners may retire after their comparison evidence and code
receive actual retained ownership. It grants no behavioral equivalence,
fresh persistence, AMP, physical installation or full ERC-1 authority.

## 2. Complete ordered grammar

For a typed prefix with `n` nodes and `w` declared slots, let `n_t` count
nodes of type `t`, let `k` be the number of readout heads, and let the `d`
declared delayed coordinates have types `t_1,...,t_d`.
The number of complete root choices at that prefix is

```
n_readout^k * d! * product_j n_(t_j).
```

Repeated heads and bodies are included. Each state occurs once in every
binding tuple, but all `d!` tuple orders remain distinct. Missing a needed
body type gives zero choices even when other factors are already large.

If the node cap permits an extension, the children are exactly:

1. each declared Source and each declared delayed State read;
2. for every allowed SUM type, all ordered edge strings of lengths
   `0,...,remaining_edges` from the alphabet of `n_t*w` parent/slot pairs,
   when the SUM cap permits one more node;
3. all ordered compatible PRODUCT parent pairs under each declared typed
   rule, when the PRODUCT cap and two remaining edges permit the node.

An empty SUM has one choice even when its edge alphabet is empty. Multiple
references to the same source, repeated edges, square PRODUCTs, sharing,
and unused parameter slots remain present. The complete search iterates
every declared slot count `0,...,slot_cap`, including different slot counts
with identical current evaluations.

**Coverage lemma.** Every admitted Program has a unique slot-count class,
unique sequence of these prefix extensions, and unique root choice at its
last prefix. Conversely, every emitted Program is admitted.

**Proof.** Same-time parents must precede their node, so remove the last
node of any nonempty prefix. Its constructor is one of the three cases
above, with exactly the declared parent indices, edge order, slots and
result type. Each count is monotone under prefix extension, so its parent
prefix fits the same caps. Induction gives the unique path from the empty
prefix. Source/state IDs, SUM types and PRODUCT rules are distinct by
semantic validation; different cases and coordinates cannot encode the
same child. The complete readout/binding validation is exactly the root
Cartesian product above. Slot count is part of Program identity. This also
proves disjointness. Finiteness follows from the finite node, edge and slot
caps and the fixed finite semantic alphabet. No observational equivalence
is invoked. QED.

## 3. A checked execution prefix, not a supplied frontier

The Runtime owns an initial `GrammarCursor` and the complete subsequent
cursor, including a frame for each active prefix. A frame records the next
root and next child ordinal. The solver proposes only `emit`, `descend` or
`close`. Its proposal has no authority.

The checker recomputes choice counts, validates/ranks the proposed native
object, and permits only the next ordinal. Every root must be emitted
before descent; every child must return before closure. A caller cannot
provide a cursor, alternative list, skipped region or completeness bit to
the Runtime. Each emitted Program must append exactly its own comparison
row; substituting a different row is an execution failure.

Counts are computed only up to `next_ordinal+1`. Nonnegative addition and
multiplication preserve this saturation, with zero factors retained.
Exponentiation, geometric sums and factorials likewise saturate without
forming the astronomical exact count of an unvisited class. Therefore the
checker still distinguishes “this ordinal exists” from “all choices have
been visited.” Ranking and unranking are separate routines; the checker
does not trust the planner's chosen coordinate.

**Executed-coverage invariant.** Starting from the owned empty cursor, every
accepted transition preserves that the stored frames describe exactly the
visited prefix. Final closure implies that every Program in `G` has been
emitted once.

**Proof.** An emission advances only its verified next root. A descent
advances only its verified next child and pushes an untouched child frame.
A close requires both coordinate sets exhausted and returns to the unique
parent; root closure moves to the next slot class or finishes the last one.
Induction on accepted transitions and the coverage lemma prove the claim.
A work limit can stop this process, but cannot convert its remaining
subtrees into a rejection theorem. QED.

The implementation intentionally does no value-based pruning. A poor
completed program is also a prefix whose descendants may be useful;
neither its CE nor a failed value/range computation bounds those descendants.

## 4. Endpoint and authority checks

Every emission runs the same owned constructor and optional profile as the
public Runtime endpoint. Objective reads use retained original IDs, incur
registered work and remain proposal data. A failed constructor or uncertain
range/arithmetic comparison leaves an unresolved row. Even if syntax later
closes, **one unresolved row blocks the maximum proof**; the current solver
does not turn its conservative feasibility failure into an exclusion.

Before issuance, Runtime rescans all retained rows, checks their ordinal,
grammar membership and registered initializer/profile endpoints, recomputes
every exact likelihood, and verifies the maximum independently of the
solver's selection routine. The claimed score must equal the score of the
actual live winning program **and complete learner state**. An inflated
upper score alone is not a winning endpoint. Verification reads/work and
the proof object itself are paid; exhausted final verification does not
inherit a success token from the completed enumeration.

The full explicit cursor and comparison history have an actual packed
Compiler workspace. Replacing that workspace allocates the successor
before releasing the predecessor. Retained code keeps an owned lease even
when a nonwinning lineage retires. Cancellation terminates search but keeps
its queryable packed history; there is no free-and-retain history shortcut.

`ReferenceClassProof` is typed data with one fixed proposition kind. Only a
matching Runtime-retained issuance at the current complete-context revision
is accepted. The token binds claim, Runtime, search, exact class, ordinary
cursor, deployed/winner lineage, compared count and likelihood. Relevant
external mutations invalidate that revision. Search chunking carries its
own checked prefix forward. An altered/copied-from-another-Runtime object,
stale issuance, different class or issuance during a live internal phase
is rejected. Recreating identical already-issued data does not create a
new authority. Python internals are trusted implementation, not a security
boundary against code that can arbitrarily overwrite the process.

The issuance comparison validates every field's **exact declared type**
before ordinary dataclass equality. Python's `1 == 1.0 == True` is not
typed evidence identity; a Fraction subclass can even override equality
while representing a different number. The initial implementation accepted
such a caller-created likelihood of one as equal to an issued quarter.
Strict integer/Fraction/string validation at construction and admission
closes that concrete public-interface mismatch without another hash.

The result is called `REFERENCE_CLASS_EXHAUSTED`, **not** full Compiler
`CERTIFIED_COMPLETE`. `install` still returns UNRESOLVED. The packed-buffer
and declared operation model excludes total host heap, transient scratch,
serialization/bit-time and CUDA costs. Its successful comparison therefore
cannot freeze the Runtime or authorize device/model science.

## 5. Auditable evidence

The independent oracle explicitly expands Cartesian products rather than
using production counts/ranks/cursors. It compares actual Program objects,
including types, shared descendants, repeated edges, unused slots and all
delayed binding orders. Runtime audits then execute every member of a
110-program registered-profile class, plus recurrent attachment classes,
with independent forward differentials and exact likelihoods.

A four-context XOR endpoint audit visits all 587 programs with caps
`nodes=3, SUMs=1, PRODUCTs=1, edges=2, slots=0`. The complete same-class P=0
portion and every shorter prefix have best likelihood `1/16`, also the
empirical optimal unigram. A constructed PRODUCT descendant reaches `1/12`.
This verifies discovery through unhelpful prefixes inside the **stated**
finite grammar; it is not a new unrestricted-SUM exclusion or a model-science
comparison against neural baselines.

Fault injections attack skipped/closed regions, repeated/substituted rows,
wrong selection, an inflated winner score, backend failure, forged/stale
proofs and resource exhaustion after all rows have been compared. Tiny
rational likelihood differences survive a binary64 tie; insufficient
reference precision remains UNRESOLVED. The minimal JSON records counts
and outcomes, not a dump of every search workspace or execution trace.
