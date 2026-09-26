# Exact native commits from sound numerical enclosures

Status: **PROVED CONDITIONAL REFINEMENT; PASSIVE BINARY64 AND EXACT AUDITS
PASS, 2026-09-26**. This is a reference solver for the
[complete native token learner](NATIVE_TOKEN_LEARNER.md). It changes neither
G/Gamma/U nor the dyadic commit grid. It does not implement an AMP learner,
owned Runtime, physical budget or constructor certificate.

Source: [enclosed_tokens.py](enclosed_tokens.py).
Audit: [audit_enclosed_tokens.py](../../scripts/audit_enclosed_tokens.py).
Evidence: [FP_ENCLOSED_TOKENS.json](../../evidence/minimal/FP_ENCLOSED_TOKENS.json).

## The complete pending state need not materialize every rational

Within a registered SGD update unit, parameters stay fixed. For this token
learner, a committed origin contains every parameter, the full context and
clocks; the following target prefix determines every later source window,
feature, prediction and event gradient. There is no other external input,
RNG transition or within-unit parameter update.

Retain that immutable **complete origin and every target in the current
unit**. Exact replay then decodes every native pending parameter, gradient,
context and clock. Replay here means the declared pure reference arithmetic
on retained data, not an additional observation or learner update. Its
actual work and integer size remain separate obligations. The representation
does not assume that gradients fit a smaller materialized precision cap.

Alongside this exact recipe, maintain sound binary64 intervals for the
complete readout gradient basis, all core gradients, and every embedding
coordinate touched anywhere in the unit. Untouched embedding coordinates
have structurally exact zero gradients; all other readout coordinates use
the complete common-minus-target-correction formula. Intervals are bounds
on this retained exact state, not replacement gradient values.

## Conditional scalar enclosure rule

Assume finite IEEE binary64, correctly rounded nearest basic operations,
gradual underflow and adjacent representable `nextafter` endpoints. The
prototype checks radix, significand width and nearest-rounding metadata;
an owned backend must bind the actual arithmetic environment. These checks
alone are not a proof against arbitrary external rounding-mode changes.

For each addition, use the adjacent lower float after the rounded sum of
lower endpoints and the adjacent upper float after the rounded sum of
upper endpoints. Multiplication encloses all four endpoint products;
reciprocal uses reversed endpoints on an interval excluding zero. Negation
is exact. Exact rational ingress is compared to its rounded binary64 value
to choose the necessary adjacent endpoint, then checked exactly against both
resulting bounds. Every nonfinite operation or
outward endpoint refuses; no finite clamped successor hides an overflow.

Exact point-zero addition and point-zero/one multiplication identities
avoid gratuitous widening. Equal interval bounds do **not** prove equality
of the two underlying quantities, so subtraction has no such cancellation
shortcut. Intersecting a native nonnegative quantity with [0,infinity)
uses its proved semantics, not a guess from its rounded sign.

The scalar rules enclose the exact real operations under the stated
arithmetic assumptions. Induction over the native forward/reverse DAG,
including shared parents, ties and repeated feature incidences, encloses
every exact gradient. Interval dependency can make bounds loose; it cannot
authorize choosing a convenient point inside them.

## A grid-cell decision gives an exact endpoint

Let q be a committed integer master, and let an interval [l,u] enclose

    v = q - 2^p eta G/N.

The native next master is h(v)=max(0,floor(v)). Because h is monotone,

    h(l) = h(u) = q'  implies  h(v) = q'.

For a readout column, similarly enclose a=2^p eta common/N. Equal endpoint
ceilings determine its exact common integer shift. Every target correction
uses the old master and combined signed step before floor/clamp, as required
by the readout proof. The solver covers all core slots, all touched input
slots and every corrected readout row; the two proven implicit cases cover
the remaining declared slots. It is not a sampled-coordinate certificate.

Only after all decisions resolve does the pure function return a new exact
integer-master learner, with the actual context, advanced native clocks and
zero pending gradients. Induction therefore gives exact committed native
states, without accumulated floating trajectory error. Future units start
from these exact states. Within a unit, the exact recipe and intervals
remain distinct; this does not claim exact intermediate float values.

An ambiguous floor/ceiling returns UNRESOLVED. A failed commit retains the
complete unit. If observation arithmetic fails after a new target arrives,
the exception carries a separate `RetainedUnit` containing the origin,
entire target prefix and new context. It exposes an exact decoder, not the
previous event's stale gradient bounds. No enclosed successor is published.
An actual Runtime must still reserve storage, own ingress and retain these
objects through its failure lifetime; the passive exception is not that
resource or execution authority.

## Counterexamples to weaker numerical decisions

For q=1 and a true scaled gradient2^-60, nearest binary64 subtraction
computes `1.0 - 2^-60` as1, whose floor is1. Exact native floor is0.
The sound interval crosses the boundary and refuses. Small numerical error
alone is therefore insufficient to certify a grid commit.

Conversely, a symmetric readout can have an exact zero core gradient while
its dependency-oblivious interval has positive width. The native step is
legal; this solver still refuses the undecided cell. The audit retains the
target and independently decodes the exact pending zero. This is solver
incompleteness, not a Foundation change or evidence that the learner cannot
continue. No midpoint, tolerance waiver or exact-oracle continuation is
silently substituted.

A further legal case has base2^-1024 for the newly observed target. Its
prediction fits binary64, while observation needs a nonfinite reciprocal.
The full new target and exact unit survive, every decoded gradient agrees
with the separate native reference, and no stale enclosure is published.

## Exact evidence and practical boundary

`python -X utf8 -B scripts/audit_enclosed_tokens.py --write` passes:

- 715 scalar point-operation enclosures,55 honest arithmetic refusals and
  504 nonpoint endpoint/interior comparisons, including signed values,
  nonrepresentable ingress, subnormals and overflow boundaries.
- All384 declared six-token words:2,304 observations,64,512 complete pending
  gradient-coordinate checks and1,728 exact native commits. Every requested
  word completes in this small class, with zero oracle resumptions. This
  does not contradict the separate symmetric refusal witness above.
- A V=50,257,512-event update unit. Six checkpoints compare the entire exact
  gradient basis. The largest common-gradient denominator grows through
  17,225,1,730,3,348,6,404 and12,303 bits. The interval solver resolves the
  commit, and **all301,548** resulting parameters agree with the independent
  materialized-rational control. All per-event core values, normalizers and
  target masses are enclosed. Tokens are synthetic; context is four here,
  distinct from the earlier context512 indexing audit.

The exact control and interval solver run separately; control values never
choose the interval solver's successors. The materialized control is used
only by the audit. The solver retains a short exact replay recipe instead
of those growing gradient rationals. This gives a practical direction for
the reference side of text training, not a universal precision/storage lower
bound or a throughput comparison.

Current code still uses pure Python scalar intervals, immutable-map copying,
unbounded committed integer indexes and an unbounded optional exact decoder.
Its construction, endpoint conversion, retained versions and failed scratch
must be funded before Runtime admission. Passive dataclasses can be forged;
the theorem is for initialized origins and valid transitions, not arbitrary
caller-supplied bounds. No `CERTIFIED_COMPLETE` object is issued.

The next boundary is a funded efficient numerical implementation and its
actual AMP relation, followed by the registered ordinary-text comparison.
The completed relation-task branch remains closed.
