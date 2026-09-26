# Source context and learner time are separate coordinates

Status: **EXACT COUNTEREXAMPLES AND PASSIVE REFINEMENT AUDIT PASS,
2026-09-26**. This corrects an interface restriction encountered while
preparing the native token learner for Runtime integration. It adds no
semantic reset action, optimizer, data-access permission or new source.

The [source schema](CORPUS_AND_CAUSAL_SOURCES.md) already declares lag/token
atoms relative to position within a file, with distinct PAD and no context
crossing files. Existing [profile semantics](../../src/reference_compiler/fp_reference/profile.py)
already retain each example's original source context while advancing a
local optimization clock. Those facts cannot be represented by identifying
file position with the learner's observation count in every execution.

## The restriction and the counterexample

The first token prototype starts at file position zero and advances one
contiguous stream. In that class the two clocks agree, and the complete unit
origin plus target prefix determines every source. Its proofs and audits
remain valid for that class. Generalizing the same shortcut to retained
profiles or separate-file reporting would be false.

An exact two-event witness has V=2, L=D=K=1, base=(1,1), p=4, eta=1/3 and
update unit2. Embedding values are E_0=0, E_1=1, E_PAD=0; both readout
masters start at zero. Both units observe targets(0,0). Their first source
windows are respectively token0 and token1 at file position1; both second
windows contain token0 at position2. Thus the origin, targets, final
context, source position and learner clock all agree. Nevertheless their
target readout masters after commit are **0 and1/16**. Replaying only the
targets from the initial default context reconstructs the wrong second unit.

Keeping only computed feature values is also insufficient. With equal
embedding values E_0=E_1=1, base=(1/2,1/2), readout weights(2,1) and target0,
source token0 versus token1 gives identical forward caches but places the
nonzero gradient **-1/20 in different embedding rows**. Source identity is
needed by the present learner, not merely a speculative future constructor.

## Explicit source points and exact decoding

The passive learner now keeps `source_position` separately from its native
cursor. Its default source reader preserves the old contiguous behavior.
`predict(window)` can also evaluate an explicitly supplied complete
`TokenWindow`, including position0 of a new file or a retained profile
example. This performs the same native SUM/PRODUCT computation with that
declared source point; it does not change any parameter, pending gradient
or optimizer clock.

For learning, `observe(cache, target, window=actual_window)` checks the cache
against the **independently supplied actual source point**. It does not
infer that point from possibly altered cache metadata. Omitting the keyword
binds the original default reader. Equal computed values do not waive a
source mismatch. The normal native observation advances the learner cursor
and accumulators; the default source-reader successor is the actual
window with the revealed target appended. Source position need not equal
the new learner cursor. This is data-interface state, not a hidden neural
recurrence or a new architecture action.

The enclosure solver now retains every actual window with its target.
Exact decoding replays those complete source/target records from the unit
origin. Bounds, commits and failure records use that same sequence. The
target-only representation remains a possible proved compression for an
explicitly contiguous sequence, but this general prototype does not silently
assume continuity. Its retained source storage is up to O(N L) token/PAD
entries per update unit, in addition to the origin, bounds and other state.
Those entries and all retained versions require resource funding.

This suffices for component refinement: the complete native state and every
prediction/gradient depend on the origin and the ordered complete records;
induction applies even when original file positions repeat or run backward.
No optimizer step is caused merely by changing the supplied source point.
When an observation enclosure fails, its retained exact unit includes the
newly supplied source and target, with both clocks distinguishable.

## Frozen reporting and owned information

A trained immutable learner can predict successive windows from a new file
without calling `observe`. The external source reader alone appends each
revealed reporting token. Parameters, pending gradients and optimizer clocks
remain unchanged. The first new-file window is PAD, not the last training
context. In the audit, the proper first probability is1/2; accidentally
retaining training context gives11/15.

These are passive mathematical operations. A supplied `TokenWindow` does
**not** prove its corpus identity, split role, availability, retained-example
identity or causal origin. The actual Runtime must derive/bind the source
from owned information, retain observation identities and history, prevent
reporting labels from training/discovery, and pay for all reads and replay.
There is no profile admission, test access, freshness or installation
authority here. Caller-made windows/bounds cannot become certificates.

## Minimal evidence

Run `python -X utf8 -B scripts/audit_token_source_clock.py --write`.
The [audit](../../scripts/audit_token_source_clock.py) retains only
[FP_TOKEN_SOURCE_CLOCK.json](../../evidence/minimal/FP_TOKEN_SOURCE_CLOCK.json).

- Both source-erasure witnesses above, including the different exact commits
  and equal-output/different-gradient case; five source-binding refusals.
- All96 declared retained-source schedules from16 four-token files and six
  two-position selections, each repeated twice. All384 observations and192
  commits agree with literal native G/U and the enclosure path; complete
  gradients, sources and both clocks are checked independently.
- 64 frozen exact/enclosed predictions over16 synthetic reporting files.
  All model parameters, gradients and clocks remain unchanged while source
  positions0..3 advance independently of learner cursor4.
- Observation failure at source position7 retains its actual source and new
  target; the exact decoder reaches learner cursor1/source position8 with
  every gradient matching the separate native control.

The unchanged contiguous native and enclosure suites also pass. No actual
validation/test file, model loss, Torch or GPU is used. The immediate next
work remains owned, resource-bounded execution and its AMP relation for
ordinary text; the relation-task branch stays closed.
