# Research branch: conditional universality, 2026-09-12

Branch: `research/conditional-universality-20260912`.
Pinned base: `388251d8b05de10536bdf650e4c1a56a2bd46a4b` (`main`).
Base tree: `f878345006246c631da94c83c761501edf87508f`.

## Starting point

Main has reached canonical XVII.28, including coefficient-path completeness
for conditional closure, same-cap final excess contraction, hidden activation
rescaling, and finite-alphabet closure with unrestricted finite SUM work.
The exact/approximate universal PRODUCT count for arbitrary strictly positive
binary three-bit tables remains between two and three (XVII.26-28).
Reference Compiler closure, registered value/physical paths and the actual AMP
bridge remain separate. GPU/model science remains **HOLD**.

Both `research/product-budget-20260911` and
`research/masked-product-range-2026-09-11` have one unmerged commit relative to
main; they were inspected and left untouched. Their given-coefficient/range
results have not been silently imported into this full-class claim.

## New proved branch results

Read [`THREE_BIT_DETERMINISTIC_CLOSURE.md`](theory/proofs/THREE_BIT_DETERMINISTIC_CLOSURE.md).

1. Complete deterministic binary three-bit prediction closure: exactly 96
   Boolean tables need zero PRODUCTs, 158 need one, and the two parity tables
   need two. SUM closure is precisely the literal-decision-list class; every
   non-list has a whole-class probability sup gap at least 1/5. Parity has a
   whole-class one-PRODUCT sup gap at least 1/2.
2. Constructive resources are explicit. At epsilon=2^-k, every table has a
   witness using its minimum PRODUCT count, local SUM alphabet {1/2,1,2}, at
   most 12*k+8 SUM nodes, probability error at most 4*2^-k and normalizer at
   most 9*2^(5*k). These are upper bounds, not physical/AMP or optimality claims.
3. Finite positive SUM predictions are not closed under convex mixtures, even
   up to one PRODUCT. In d dimensions, 2^(d-1)+1 finite SUM components, each
   with normalizer <=3*(d+1), mix to noisy parity with amplitude
   1/[3*2^d*(d+1)]. Fewer than ceil(log2(d)) PRODUCTs cannot approach it.
   The margin decreases with dimension; component count is exponential.
   In three dimensions five finite SUM components mix to 47/96 versus 49/96,
   a table whose exact and approximation PRODUCT minimum is two.

The classification is an analytic lower argument plus finite exact upper
certificates, not a floating optimizer report. Exploratory solver proposals
carry no authority in the committed standard-library verifier.

## Reproduction

```text
python theory/numerical_checks/three_bit_deterministic_closure_audit.py --write
```

Minimal evidence:
[`FP_THREE_BIT_DETERMINISTIC_CLOSURE_AUDIT.json`](evidence/minimal/FP_THREE_BIT_DETERMINISTIC_CLOSURE_AUDIT.json).

The audit passed normally and with `python -O`; repeated outputs were
byte-identical. It checks 256 Boolean tables, 14 symmetry orbits, 160 independent
SUM obstruction cores, 6,144 exact native context executions, 768 expanded
finite-alphabet graphs, 240 exact one-PRODUCT moment cases, 31 rejected invalid
certificates, and 43,690 finite-mixture component/context evaluations through
dimension eight. The source SHA-256 is recorded in the evidence.

## Remaining research boundary

Do not relabel this as two-PRODUCT universality for positive binary tables.
The 256 deterministic patterns do not exhaust the 3^8 mixed support patterns
where some rows retain both positive labels. Neither that mixed-support class
nor arbitrary prescribed leading amplitudes has been decided here. The next
useful targets are mixed-support exclusions and full two-PRODUCT amplitude
feasibility, using XVII.28 while retaining every shared coefficient and normalizer.

The 14 representatives are proof artifacts, not an architecture-action menu.
Convex mixtures of normalized predictions cannot be imported as free native
SUM readouts. No training, acquisition, persistence, Runtime or AMP authority
has been inferred from a static table identity.

This is a reviewable branch supplement. `FP_THEORY.md` remains the only normative
theory source and was not overwritten; promotion of this result is a separate
integration step. No main-branch mutation or merge is included in this change.
