# A bounded-range posterior can still lose a legal future in finite precision

**Status at registration:** exact model-level argument and independent
round-to-nearest binary32 preflight; the two owned CPU/CUDA jobs below have
not yet supplied device or Runtime evidence. This study keeps the registered
[simplex U and lowering](SIMPLEX_RUNTIME_CONTRACT.md) unchanged.

## 1. An absorbing zero in a whole-history learner

Consider the two-token fair-prior, noise1/10 native relation model. After t
copies of query(0,1),label0, its exact two world weights are

`(9^t/(1+9^t), 1/(1+9^t))`.

All native activations stay at most8 and the exact normalizer remains10.
Both weights are strictly positive at every finite t. Nevertheless, an ideal
binary32 rounding of the second weight becomes zero when
`9^t+1 >= 2^150`, since half the smallest positive binary32 subnormal is
2^-150 and ties round to even zero. The first such integer t is48. This
ideal single rounding is a reference threshold, not a substitute for auditing
the actual sequence of rounded native gradients and updates.

Once a stored simplex weight is zero, the registered multiplicative rule
cannot revive it through a finite-gradient continuation: multiplication by
any finite factor produces a signed zero, positive finite normalization
leaves zero, and the validated zero encoding is positive zero. A nonfinite
intermediate is separately refused, not a resurrection mechanism. This
absorbing property concerns the physical learner transition. Runtime still
owns the raw observations, complete reference state, error records and
Compiler options; **no complete-state erasure or Foundation counterexample
is inferred from a rounded parameter alone**.

Appending t copies of the same query with label1 returns the exact weights
to(1/2,1/2), hence next-label forecast(1/2,1/2). A blind continuation from
physical weights(1,0) remains there and predicts(9/10,1/10) from its stored
masses. The future error is2/5 despite an arbitrarily small current error at
the confident cut. Every finite label sequence has positive probability in
this noise model. The reversal can be very rare; this is a legal-future
counterexample, not an expected-risk or typical-performance lower bound.

This instantiates the [uniform-future information boundary](WHOLE_HISTORY_PREDICTIVE_STATE.md)
in an actual registered learner. Small absolute parameter error at one cut
and a bounded normalizer do not certify a numerical relation for every
future. A pointwise bridge must be checked again when the future arrives.

## 2. Independent numerical prediction

`experiments/joint_uncertainty/simplex_reversal.py --preflight` executes the
independent exact-rounded AMP oracle on50 agreeing labels followed by50
contrary labels. It uses native half-forward and single-readout/gradient/
master operations, including the actual normalized update. No Torch or
device is imported. The full finite trajectory predicts:

- the first zero world weight after48 ordinary observations;
- no earlier breach of the declared state/native/normalizer tolerance1/100
  and mass-normalized probability tolerance1/1000;
- the first breach at the **prediction after97 observed labels**, before
  revealing label98: native error4/365 and probability error2/1825;
- blind final physical weights(1,0), while the exact full-assignment
  posterior returns to(1/2,1/2).

At the predicted failure cut the exact weights are(729/730,1/730), so the
stored mass discrepancy is `8/730=4/365` and the conditional discrepancy is
`(8/10)/730=2/1825`. The blind predictions after a refused event belong only
to the independent arithmetic counterexample; they are not legal executed
Runtime forecasts or model scores. This audit does not extrapolate its
actual first-underflow index to another floating format, kernel or hardware.

## 3. Registered owned audit

Two jobs use the same one-candidate native graph, actual Gamma=(1,1/2,1/2),
selected slots(1,2), rate1 and one-event update units. There is no profile,
search, persistence or installation. The empty registered strategy still
owns the complete Runtime control interface. The current ordered-pair source
domain is all four categorical pairs. Every context is delivered before its
label; the exact data contract contains the100 predetermined observations.

The CPU job should seal the full100-event stream and return to the uniform
exact posterior. The target job must stop at the registered bridge breach,
retain the already executed raw phase and pending unlabelled context, and
keep its pre-prediction learner and physical current state. It must not
reveal another label, issue a seal or receive an install/class certificate.
An earlier kernel/bridge mismatch, a missing record, an auditor error or a
resource failure is a retained failed audit outcome, not a substituted success.

Both jobs retain the earlier simplex audit's unchanged32768 reference integer
bits,512MiB packed allowance,10^11 work per role, native range caps16 and
binary64 tolerances10^-9. Host job caps are512MiB for CPU and4GiB for CUDA;
each has180 seconds. The RTX3090 path keeps16MiB resident arena,32MiB allocator
allowance,4096 output cells and256KiB evidence frames, with state/native/
normalizer tolerance1/100 and probability tolerance1/1000. Source dependencies
are committed and checked by the parent before and after each whole job.

Independent audits replay all binary64 phases. For CUDA they check every
raw successor, prediction, output extent and packed evidence frame, including
the **failed** prediction. The expected counts are292 checked CUDA phases
plus one retained refused phase, and293 binary64 phases in that same prefix.
The CPU control expects301 binary64 phases. Completed-job accounting includes
the final replay, and the minimal journal preserves all outcomes without
rerunning failed cases or increasing limits after observing a failure.

Passing this audit means a sealed CPU control and an honest CUDA refusal,
not a successful100-event target model. If these outcomes occur, subsequent
research must distinguish solving a model's information representation from
its floating realization. Raising a tolerance cannot recover an absorbed
posterior coordinate. Expected-risk approximations, different declared
representations or resource allocations need their own claims and evidence;
the exact whole-history and all-future statements are not weakened silently.
