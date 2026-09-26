# Complete observed-context token prediction relation

This closes one obligation needed by ordinary next-token execution: comparing
every output label, including labels that never occur in a retained unit.
It is a passive numerical predicate, not a Runtime owner or issued bridge.
The native and AMP origins may differ; neither supplies the other's update.
Their definitions, actual source/target records and learner clocks must agree.

## Conditional numerical result

Assume IEEE binary64 round-to-nearest, ties-to-even, gradual underflow, separate
NumPy operations without contraction, and correct binary32 conversions. The
native `batched_tokens.Bounds` encloses its exact native prediction under the
[existing reference proof](BATCHED_REFERENCE.md). Let the physical prediction
retain its actual half core, uint32-valued integer masters, binary32 bases and
binary32 normalizer Z. No packed reference values replace these operands.

For each vocabulary block, `amp_tokens.Kernel.mass_block` executes the actual
binary32 weight scaling, products, balanced SUM, base addition and division.
`readout_relation.Binary32Decoder` checks its excess, mass and raw probability
words against the same deterministic rounding recipe. This checks all output
words, not every internal device primitive separately. The decoder works as
follows:

- A product of two finite binary32 operands is exact in binary64: at most48
  significand bits, with exponent range contained in binary64's normal range.
- For addition, binary64 TwoSum returns the rounded sum and exact residual.
  The residual's sign chooses the adjacent outward binary64 endpoint; zero
  residual gives a point enclosure. This is Algorithm3.1/Theorem3.4 of
  [Ogita, Rump and Oishi, *Accurate Sum and Dot Product*](https://www.tuhh.de/ti3/paper/rump/OgRuOi05.pdf).
- For division by a nonzero binary32 operand, the adjacent binary64 neighbors
  enclose the exact quotient. Its magnitude cannot underflow/overflow binary64.
- If both enclosure endpoints round to the same binary32 **bits**, monotonicity
  proves the output. Otherwise a charged exact rational RNE32 decision is used,
  up to the declared cell allowance; exhaustion is unresolved. Signed zeros
  are distinguished. Nonfinite outputs refuse. This is a verifier, never a
  learner state or gradient fallback.

With uint32 masters and grid precision p<=32, scaling by2^-p commutes with
rounding those masters to binary32: all nonzero resulting coefficients remain
normal, and the power-of-two multiplication is exact. The decoder can therefore
encode the scaled master exactly in binary64 and round it once. The registered
base cache is checked word for word before scanning any label.

The exact sum S of **stored** masses is computed separately from Z. A finite
positive binary32 word with exponent field e and significand integer m is
`m * 2^(max(e-1,0)-149)`. Accumulate m into254 int64 exponent bins per event.
For V<=2^20 each bin is less than V*2^24<=2^44, so integer accumulation cannot
overflow. The final exact integer is `sum(bin[e] << e)`; divide by2^149.
The full sum needs at most297 numerator bits. The caller's ordered traversal
covers each label exactly once; row counts and target-cache comparisons reject
incomplete traversal. No floating reduction or vocabulary-sized retained mass
tensor supplies S.

For each event let q_y be its exact native probability, m_y its stored physical
mass, and r_y its actual rounded division. The scan obtains sound upper bounds

```
Eraw   >= max_y |r_y - q_y|
Eround >= max_y |r_y - m_y/Z|
mmax    = max_y m_y.
```

Since S,Z>0, for every label

```
|m_y/S - r_y| <= mmax * |S-Z|/(S*Z) + Eround = D
|q_y - m_y/S| <= Eraw + D.
```

Thus one scan bounds both native-versus-raw and native-versus-properly-normalized
probabilities, without a second device replay or retained V-by-N tensor. Every
bound, including the last subtraction/addition and the normalization correction,
uses outward intervals. Final binary64 upper bounds are compared as exact
fractions with the declared tolerances. Positive masses/probabilities, raw
probabilities at most one, core/excess range, native error and all three pairwise
normalizer errors are checked. This is conservative: inconclusive enclosures
or exhausted resources refuse rather than certify a false inequality.

Verifier array geometry is O(KBN+254N+VK+JN), with block size B and J core
nodes. Arithmetic still scans O(VKN) entries; this is not a constant-work
certificate or a total-heap bound. Actual host/time/device fences are separate.
All-label reproduction depends on retained actual operands and the declared
deterministic recipe. These passive mutable objects confer no ownership.

## Exact controls and scope

`scripts/audit_token_readout_relation.py` checks524 boundary and5,528 fixed-seed
primitive words against exact RNE;36 overflows,28 zero divisors and exhausted
exact-cell allowance refuse. The integer accumulator checks3,060 mass words
covering all255 finite exponent fields, three exact full sums and eight invalid
or incomplete cases. Seven literal native probability comparisons pass, and
six binding/tolerance/unobserved-label/base-cache/array-cap attacks refuse.

An exact normalization witness has V=3, bases1/3 and zero learned excess.
The native and physical normalizers both equal1, but each stored mass/raw
probability is33554433/100663296. Their sum is33554433/33554432, not one.
Properly normalizing the stored masses gives exactly1/3 each. Replacing S by Z
would erase a real distinction; the predicate retains it and tests its error.
This is a numerical issue in ordinary full-vocabulary readouts, not a new task
family or Foundation action.

The evidence is [FP_TOKEN_READOUT_RELATION.json](../../evidence/minimal/FP_TOKEN_READOUT_RELATION.json).
It proves neither complete learner-state agreement nor XV's internal event
relations. Runtime integration must still own every source record, pending
gradient and resource; a successful unit endpoint cannot replace those duties.

## One actual-device preregistration

Run `scripts/run_token_readout_audit.py --run` once after committing all inputs.
Use precisely the existing full-vocabulary/context512/512-training-token
[resource fixture](REFERENCE_HOST_PROTOCOL.md), with its four SUM/four PRODUCT
features and603,092 masters. Read only the first1,024 training-file bytes. No
validation/test read, loss score, optimizer commit, architecture search or model
ranking is included. This is a new full-label comparison; the two old terminal
AMP schedule jobs must not be replayed.

Freeze activation cap2, normalizer cap64, native/normalizer absolute tolerance
1/100, probability absolute tolerance1/10^6, and proper-versus-raw division
tolerance1/10^7. Use blocks of256 labels, per-array element cap2^24, and at
most4,096 exact ambiguous rounding-cell decisions. These are finite fixture
acceptance thresholds, not a loss/persistence or complete learner tolerance.

The fresh child has a preattached4-GiB Windows private-commit limit,900-second
deadline and one active process, including imports, device transfers, native
control and all-label verifier. Retain the existing pinned Torch2.12.0+cu132,
build7661cd9c6b841b62b7f411aa52ec51f05457263b, CUDA13.2, RTX3090/capability8.6,
512-MiB Torch allocator limit and24-GiB whole-board upper. The native device
contract also binds the installed runtime/driver and board. No CPU fallback.
Parent/shared-platform costs are outside this job's scope.

Require all50,257*512 prediction coordinates, all corresponding output words,
all512 target-cache bindings and all registered inequalities. Report exact-sum
bit lengths, decoder/fallback work, timing and actual resource observations;
retain no arrays/weights. The exclusive original journal is
`FP_TOKEN_READOUT_CUDA_A1.json`. Any word/range/tolerance/device/host/time failure
terminates this attempt; preserve it unchanged and do not widen its thresholds.
After this gate, proceed to the owned event/state relation and ordinary text
learning, not another static numerical catalog.

## Actual result at35335a9

The [original CUDA journal](../../evidence/minimal/FP_TOKEN_READOUT_CUDA_A1.json)
is terminal and passes its fixed contract. All25,731,584 label/context
coordinates,77,194,752 actual output words and512 target caches pass across
197 blocks. The decoder computes437,436,928 words and needs zero exact-cell
fallbacks. Exact stored sums use at most40 numerator/37 denominator bits.

| Observed upper bound | Value | Registered limit |
|---|---:|---:|
| Core/excess/mass error | 0.0005400092741194574 | 1/100 |
| All normalizer errors | 0.005349871988048705 | 1/100 |
| Native versus raw/proper probability | 4.590267123597707e-9 | 1/10^6 |
| Proper versus raw probability | 3.950206924938882e-12 | 1/10^7 |
| Activation | 0.875 | 2 |
| Normalizer | 13.014471809364363 | 64 |

The full scan/check takes26.58475 seconds; the whole child takes29.78500
seconds. Peak job commitment is2,022,989,824 bytes, Torch allocated peak
50,787,328 bytes and reserved peak71,303,168 bytes. No timeout or limit
termination occurs. The cumulative job process counter is2; this is not
two simultaneous active processes under the enforced one-active-process cap.

The origin remains unchanged and neither a commit nor a loss is scored.
These are observed results for this fixture, not a uniform source-domain,
future-state, language-quality or owned bridge certificate. No rerun is due.

The exhaustive audit is an independent control, not a viable routine for
all180M training tokens: a purely linear extrapolation of this verifier's
time alone exceeds100 days. Actual learning therefore needs a sound complete
relation that uses the registered readout's algebra and retained event state,
or an explicitly smaller scientifically justified run. This is a solver/cost
obstacle, not grounds to weaken semantics, remove labels or widen tolerances.
