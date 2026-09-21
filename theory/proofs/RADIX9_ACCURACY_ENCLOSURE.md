# Deciding a decoder tolerance without explicit likelihood integers

Status: **PROVED, SCOPED ENCLOSURE; EXACT/BINARY64 AUDITS;
ACTUAL AMP ACCURACY COUNTEREXAMPLE**. The sole new CUDA diagnostic completes
at80f9538 and reproduces both tolerance rejections. The earlier7cb6259 diagnostic is terminal and is
only read here. Foundation, ERC-1 and native learner semantics are unchanged.

The [radix9 frontier law](RADIX9_FRONTIER_PRECISION.md) solves the local
underflow failure, but its uniform AMP bound is too loose to certify0.001
accuracy on large tapes. The new result has two parts. First, a positive
256-cycle gives an actual finite-arithmetic-model error above0.002274, so
the hoped-for0.001 guarantee is false. Second, a checked binary64 run and
its proved error envelope give a cheap rigorous enclosure of the exact
forecast. This can certify either accuracy or a tolerance violation without
materializing9^H or assuming that an approximate reference is exact.

The numerical decision concerns one specified query of the known-noise,
fixed-prior count-state learner. It is not a complete native-state relation,
constructor completeness, resource certificate or installation authority.

## 1. A small rational enclosure from the existing proof

For the declared positive decoder tape, let B be the proved mass budget and
let v be its actual checked binary64 forecast. The previous theorem gives

`R^(-q) <= v/p <= R^q`,
`q=B+1`, `R=(1+epsilon)/(1-epsilon)`, `epsilon=2^-46`,

where p is the exact count-state forecast. Put

`delta=2*epsilon/(1-epsilon)`, `t=q*delta`.

If t<1, the binomial expansion and binomial(q,k)<=q^k imply

`R^q=(1+delta)^q <= SUM_(k>=0) (q*delta)^k = 1/(1-t)`.

Thus the exact target lies in the rational interval

`I=[v*(1-t), v/(1-t)] intersect [1/10,9/10]`.

The final intersection follows from the actual positive known-noise heads;
it is not a probability floor applied to a computed result. The construction
uses the exact rational encoding of the observed binary64 word and a few
small rational operations. It never forms R^q or a likelihood integer.
For q stored with b bits, endpoint arithmetic needs O(b+53) bits, plus any
caller-declared tolerance precision. The audited budget arithmetic is small.
The independent geometric-inequality audit uses fixed exponents through1536
and at most72,193-bit integers; it is separate from the32768-bit guarded
local binary64 arithmetic and the production-size endpoint construction.

Computing v still executes the positive tape and checks each actual binary64
primitive. Count input, order construction, tape storage and exact local
rounding verification remain costs. The exponent field and its guards are
unchanged. This is an approximate reference enclosure, not an exact integer
decoder disguised under a smaller bit limit.

## 2. Honest tolerance decisions

Let a be the bound actual AMP forecast and tau>=0 the required tolerance.
For I=[L,U], compute exactly

`d_min=max(L-a,a-U,0)`, `d_max=max(|a-L|,|a-U|)`.

- If d_max<=tau, every p in the enclosure is within tolerance.
- If d_min>tau, the actual forecast is outside tolerance.
- Otherwise the available enclosure is UNRESOLVED for that decision.

If t>=1, the local execution refuses, or the exponent envelope is exceeded,
the checker also remains unresolved. A tighter bound or more reference
precision may decide a straddling case. These are numerical refinements,
not changes to FP semantics or permission to discard a failed label.

An OUTSIDE decision rejects this numerical realization at the requested
tolerance. The underlying reference Program remains legal; a complete
Runtime attempt still needs refinement or an unresolved numerical boundary.

The helper returns conditional scalar evidence only. In the device experiment,
the actual observed word, case inputs, original source and checked arithmetic
bind a and v. An arbitrary caller-supplied fraction or underestimated B has
no such authority. Runtime does not import this helper; full input lineage,
pending gradients, clocks, owned resources, phase records, fresh persistence
and install reachability cannot be inferred from its numerical result.

## 3. Positivity alone does not give the desired AMP accuracy

Use the anchored n=256 cycle. Every edge count is+h except(0,255), whose
count is-h. Query(0,96). At h=16, the declared FP16-product/FP32-sum decoder
returns exactly

`a=10104483/16777216`.

The checked binary64 forecast is5404319552844599/9007199254740992. Its B=767
enclosure proves

`0.0022741198408 < |a-p| < 0.0022741198671`.

Both displayed endpoints are widened outward. Independent integer variable
elimination checks the target at h=16 under the existing32768-bit ceiling.
No factor entry vanishes in this decoder, and there is no across-event
rounding accumulation: this is one freshly decoded positive state.
Its half arithmetic simply accumulates enough error within the computation.
This falsifies a uniform0.001 claim for the present decoder, not the previous
R^(B+1) theorem, which never claimed that tolerance.

The original exploratory search retains all ten tested cycle/query/count
rows. Eight meet0.001; besides this256-cycle, the512-cycle query(0,128), h8
has error above0.004686248. No minimal-size failure or statistical prevalence
claim is made. The already committed27-case GPU result stays valid.

## 4. An independent cycle enclosure for enormous counts

The same cycle has an independent combinatorial description. Preferred edge
parities have odd XOR, so a legal anchored world violates an odd number k
of preferred edges. There are binomial(n,k) such worlds, each with mass
9^((n-k)h). The n minimum-violation worlds (k=1) have equal mass. For query
(0,j), whose forward arc consists of j equality-preferring edges, their
limiting probability is

`p_infinity=9/10-4*j/(5*n)`.

Writing a0=9^-h and y=n*a0, the relative total mass of all k>=3 worlds is

`T=SUM_(odd k>=3) binomial(n,k)/n * a0^(k-1)`
` <= SUM_(k>=3) y^(k-1) = y^2/(1-y)`, if y<1.

The other worlds' label probabilities stay in[1/10,9/10], hence

`|p-p_infinity| <= (4/5)*T/(1+T) <= (4/5)*y^2/(1-y)`.

Replacing h by any smaller h0 preserves this upper bound. The audit uses
h0=min(h,16); even h=10^12 therefore needs only the small integer9^16.
For the triangle, the sole negative edge is(1,2) and query(0,1) follows the
same minimum-violation argument. Its limit is19/30.

The binary64 enclosures contain these independent, much narrower analytic
intervals. They certify two accurate large-count states (triangle and64-cycle)
and reject the256-cycle at both h16 and h=10^12. At the latter count,
the same AMP output is returned, but an explicit integer decoder honestly
refuses its height guard. Per-entry exponents reach255,000,000,000,003,
requiring48 bits; no9^(10^12) object is constructed.

These are synthetic, legally reachable count states. Trillions of events
were not replayed, and no data, fresh evidence or historical execution cost
is credited to a Runtime from these fixtures. The result is an available
numerical decision at a specified state, not a cheap way to acquire it.

## 5. CPU and retained-device evidence

Run `python -B experiments/joint_uncertainty/radix9_accuracy_enclosure.py
--output evidence/minimal/FP_RADIX9_ACCURACY_ENCLOSURE.json`.
The [minimal report](../../evidence/minimal/FP_RADIX9_ACCURACY_ENCLOSURE.json)
contains:

- An independent new reader of the terminal7cb6259 GPU evidence. All27
  retained forecasts now have rigorous error upper bounds below0.001;
  the largest is less than0.000605535512. No GPU case is rerun.
- All125 signed triangle profiles and nine ordered queries:1,125 exact
  target containments and tolerance decisions, supported by298,125 actual
  checked binary64 primitives. Maximum interval width is below4.604e-13.
- The ten-row exploratory counterexample search, retaining both failures.
- Four stress forecasts,90,240 checked binary64 primitives, three explicit
  integer-height refusals, and two within/two outside decisions. Their
  independent cycle tubes are contained in the numerical enclosures.
- Exact geometric inequalities, inclusive/straddling decision boundaries
  and refusal when the geometric denominator is no longer informative.

The report retains only short fractions, counts and worst-case summaries,
not large posterior integers or phase caches. This is a new numerical audit,
not a rerun or reinterpretation of any completed model experiment.

## 6. Fixed new actual CUDA diagnostic

Commit this proof, the scripts and CPU evidence before launching
`python -B experiments/joint_uncertainty/run_radix9_accuracy_enclosure.py`.
The original7cb6259 diagnostic remains terminal. This new attempt uses:

| Shape | Query | Count magnitudes h | Required numerical outcomes |
|---|---|---|---|
| triangle, negative edge12 |01|10^12|within0.001|
|64-cycle, negative edge(0,63)|(0,16)|10^12|within0.001|
|256-cycle, negative edge(0,255)|(0,96)|16 and10^12|both outside0.001|

The child runs actual FP16 products and FP32 alignment/sums/divisions, with
guarded host integer exponents, and checks every word independently. Its
binary64 control executes checked primitives; all results and decisions
must reproduce the committed CPU report. Correctly rejecting the two
inaccurate AMP forecasts is part of diagnostic success. A passing diagnostic
does not label those forecasts as accurate or admissible to Runtime.

Register one Windows job before resuming the child, with one active process,
4 GiB process/job commit and240 seconds. The parent stays outside this child
measurement. Retain device/software identity, process identity, completed
job accounting, Torch peaks and every outcome, including reader failure.
No source change, silent restart, tolerance change or timing comparison is
allowed. The [terminal record](../../evidence/minimal/FP_RADIX9_ACCURACY_CUDA.json)
retains the completed outcome below. At this proof's initial commit the
outcome was pending; the fixed cases, thresholds and limits did not change.

## 7. Completed actual CUDA accuracy counterexample

The sole attempt completes at source
`80f9538319b70e84ee63835eca340a61d3f05ab8` on RTX3090, Torch2.12.0+cu132,
CUDA13.2. All78,848 floating-word checks agree with the independent machine,
including52,552 rounded scalar results and coefficient/normalization
selections. The exact same CPU enclosures and decisions reproduce: triangle
and64-cycle within0.001, both256-cycle forecasts outside0.001. Thus the
error interval above0.0022741198408 is now an actual GPU result, including
the large-count state that the explicit integer reference cannot materialize.
No approximate binary64 answer is treated as an exact target in that claim.

Worker28616 exits0 after attachment before resume, with no timeout, limit
termination or reader failure. Completed process/job commit peaks are
2,233,999,360/2,235,232,256 bytes under the fixed4,294,967,296-byte envelope.
Torch allocated/reserved peaks are2,128,384/4,194,304 bytes. The child includes
host exponent updates,90,240 checked binary64 primitives, independent exact
machine work and the bounded integer/analytic controls. Raw accounting keeps
total_processes=2 and limit_terminated_processes=0 under the one-active-process
cap. There is no exclusive-device timing or complete Runtime-resource claim.

The terminal journal is8,406 bytes. Neither this diagnostic nor the older
one should be restarted. The result proves a precision failure and validates
a numerical rejection mechanism; it does not grant bridge authority to an
inaccurate realization or replace any complete native-state obligation.

The [static radix-power refinement](RADIX9_POWER_LOWERING.md) now removes
unnecessary half casts and proves a sharper mixed-rounding bound. Its new
CPU audit recovers the failing256-cycle, with a uniform error<0.000883 for
that fixed tape over all admitted signed counts. The old failure remains
valid for the original schedule; the new lowering needs its own device and
eventual complete-state evidence.
