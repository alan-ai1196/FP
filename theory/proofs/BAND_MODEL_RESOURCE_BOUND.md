# A label-independent resource envelope for a larger causal experiment

Status (2026-09-23): **PROVED, SCOPED; SMALL EXACT AUDIT PASS.** No GPU
model outcome follows from this resource argument.

This is an input-distribution restriction for a controlled experiment, not
a new FP architecture or a quotient of the native state. The full indexed
program, all n(n-1)/2 signed counts and all categorical queries remain.
At a cut assume every nonzero count edge satisfies |i-j|<=2. Queries at that
cut may be any ordered pair, including diagonal and nonlocal pairs. Future
observations outside the band can leave this class; their information must
be retained and their new resource requirements checked normally.

## 1. Geometry for every subset of the band

Anchor vertex0 and eliminate1,...,n-1, retaining the at most two nonzero
queried vertices Q. Let E=2n-3 be the number of possible band edges. Original
factor scopes have at most two vertices. A message produced at eliminated
vertex v has scope contained in Q union{v+1,v+2}. Indeed the assertion is
true of its original incident factors; an older incoming message containing
v has no nonqueried future vertex beyond v+2. Induction proves the claim.

At a cut, an existing message with any remaining nonqueried vertex was
produced at one of the last two numbered vertices: otherwise all its
nonqueried scope positions have already been eliminated. Thus at most two
such frontier messages exist. Every other retained message has scope within
Q and at most four cells. This argument does not assume that removing an
edge monotonically decreases the number of live tables: isolated variables
can leave additional constant messages.

An elimination joins at most the two queried past vertices, v,v+1,v+2:
joined size<=32, reduced size<=16. Old original factors use at most4E
cells; at most n-1 query-only messages use at most4(n-1) cells; at most two
frontier messages use at most32 cells. Adding the temporary join/reduction
gives the conservative sufficient bounds

```
largest join <= 32,
peak live table cells <= 4E+4(n-1)+32+32+16 = 12n+64.
```

At most four original incident factors and two messages enter a bucket.
There are at most6*32 multiplications and16 additions per eliminated
vertex. After all eliminations, at most three original factors and n-1
messages remain on Q. The final join has at most four cells, with at most
five final additions. Hence

```
positive multiplications+additions
 <= 208(n-1)+4(n+2)+5 = 212n-195.
```

These are sufficient bounds, not claimed tight live/work lower laws. The
32-cell join upper bound is attained in the small exhaustive audit. The
[paid contiguous construction](OWNED_PACKED_HISTOGRAM.md) realizes the live
bound with its separately funded roots/coefficient arrays and compaction.

## 2. Registered n64 stream and precision/resource limits

The [experiment](../../experiments/joint_uncertainty/BAND_MODEL_PROTOCOL.md)
has126 nearest-neighbor training observations and250 ordered radius-two
evaluation observations,376 total. Every label history and evaluation
permutation preserves band support, with H<=t after t labels. Before every
forecast H<=375. Consequently the owned carry-free class needs at most

| Quantity | Sufficient upper bound | Registered allowance |
|---|---:|---:|
| Join cells |32|4096|
| Live table cells |832|1024|
| Positive arithmetic |13373|16384|
| Packed integer bits n(H+1) |24064|32768|
| Conservative native/readout integer guard |7536|32768|
| Count span before prediction |375|396|
| Histogram terms |752|—|
| Prediction output cells |6785|65536|

Both query parities are occupied for nonloop queries, so outputs=9L+17.
The already proved coefficient-normalized AMP law meets the existing state
1/100 and probability1/1000 tolerances uniformly over these histories.
After the final commit H<=376 and the packed envelope is<=24128 bits.
No additional float, table, integer or count-span allowance is needed.

The actual fixed wide extent is3264928 bytes at n64/S396/C1024/I32768.
Reference construction, physical construction and independent reconstruction
each pay their existing tariffs. This does not prove whole-stream retention,
wall time, total host/arena fit or correctness of an unexecuted implementation.
Those remain measured obligations under the existing full model envelope.

## 3. Global AMP control is not structurally excluded

The existing natural-order global physical schedule has the same geometry.
Its original factors are syntactic powers, including ones. In each bucket,
at most two incoming messages are not syntactic powers; the global alias
rule therefore needs at most one general product per joined coordinate.
The final join adds at most4(n+2) such products. With at most16(n-1)+5
additions, its registered scalar schedule obeys

```
general products <= 32(n-1)+4(n+2) = 36n-24,
floating outputs <= 38+6(36n-24)+4(16n-11) = 280n-150.
```

At n64 this is17770, below65536. Its table/tape allowances also suffice:
at most4E+(212n-195)+6=13879 tape nodes, below262144. Pure metadata preflight
on all125 full-support local nonloop queries observes a maximum3886 outputs.
That last number is a finite check, not an all-subset theorem. The stronger
projected schedule is also included as an actual control. Numerical
conformance and whole-job completion of both controls must be tested;
structural bounds cannot substitute for them or grant completeness.

## 4. Independent exact joint control

The checker uses ordinary base9 vertex-prefix sum-product over(last two
assignment bits, queried parity), at most eight entries per vertex. It
checks all count coordinates before relying on band support. This is exact
joint inference for the declared law, retaining the latent correlations;
it neither packs coefficients nor uses the Runtime elimination plan. It
uploads no forecast, partition or trained value to the physical schedule.
The stored-table bit diagnostic excludes final rational readout arithmetic;
the n+4H bound controls all positive partition integers independently.

`scripts/audit_band_model.py` checks every support subset and every ordered
query at n2..7:122576 geometry cases. It also compares1120 forecasts in56
complete sampled histories at n2..8 with the independent full-assignment
posterior, checks168 nonlocal/diagonal partition reads against world sums
and the packed decoder, and rejects a nonzero off-band count. The two n64
exact score controls are retained before any actual model job. This is
deterministic numerical evidence, not a population inference or FP inference
advantage over the exact joint posterior it is required to reproduce.
