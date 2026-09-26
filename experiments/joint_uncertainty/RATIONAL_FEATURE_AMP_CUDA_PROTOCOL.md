# Rational-feature AMP CUDA gate

Registration date: 2026-09-25. Status: **A1 STOPPED; TERMINAL**.
Production anchor: `e98065e`. The execution journal must name the full Git
commit containing this protocol and the runner. Production files must remain
identical to the anchor throughout the attempt.

The claim under test is the actual realization of
[the complete rational-feature AMP contract](../../theory/proofs/OWNED_RATIONAL_FEATURE_AMP.md)
inside `ReferenceCompilerRuntime`, including physical input binding, full
native state, resource/failure lifetime, profiles and paired installation.
The [exact CPU gate](../../evidence/minimal/FP_RATIONAL_FEATURE_AMP_CPU.json)
already passes; it is a prerequisite, not evidence of any device outcome.

## Fixed execution and resource declaration

Run `python -X utf8 -B scripts/audit_rational_feature_cuda.py --preflight`,
commit all inputs, then run the same script with `--attempt 1`.
The original output is `evidence/minimal/FP_RATIONAL_FEATURE_AMP_CUDA_A1.json`.
It must not be overwritten or selectively filtered. The runner stops at the
first unexpected execution/audit failure and retains every completed outcome.
There is no retry, tolerance relaxation or cap change within this attempt.

Each case uses a new Python process in a Windows Job Object attached while
suspended, before its first instruction. The whole-job commit limit is 4 GiB;
the deadline is 900,000 ms. The existing fresh-job runner enforces both.
Every root declares the same 4-GiB physical host bound. Default Runtime packed
payload allowance is 1 GiB and work allowance 10^15. These are separate units.
The resident CUDA arena is 32 MiB, allocator cap 64 MiB, and the device/build
identity is the existing exact Torch/CUDA/RTX 3090 registration.

The decoder allowance is join64/live1024/arithmetic32768/step2048/integer32768.
The profile case instead uses integer4096; the wide-denominator case uses
step8; the precision-refusal case uses step100. No other solver allowance is
changed. Scalar output allowance is 128 per phase, except the intentionally
unfunded case at2. Encoded phase frames are 65,536 bytes for n2/n3 and 524,288
for n64, using the existing registered byte-only zlib encoding.

Native state tolerance is 1/100; probability tolerance is 1/1000. Activation
cap is C-2 and normalizer cap 2(C-1), with the existing whole-domain proof.
The owned Reference integer limit remains 32768. Independent full-literal
auditing uses 131072 bits so that a more conservative literal operation order
does not masquerade as a defect of the registered representation. This audit
allowance supplies no extra bits to either owned path.

## Independent control and retained evidence

For every checked phase, reconstruct its lineage from initialization and
actual source/target events in the retained history. A separate unsigned
label-count control uses a vertex-prefix recurrence with at most eight states
per rate on the declared width-two words. It never reads the production
elimination tables or adopts the endpoints it checks. Counts, diagonal
evidence, T, ordinary/profile cursor and pending target are reconstructed
independently. On every prediction it checks the unnormalized R/Z and N,
complete readout and all rounded coefficient words. On observation it checks
every fixed and selected gradient class from those independent parts.

The separately written passive scalar schedule determines every ordered
primitive RNE word, including signed zeros. Prediction must emit exactly
21+4k+4J outputs, and observation exactly 6+29J-3z, including copies. For n2/n3,
an independent literal Program additionally checks every native cache,
parameter, ambient gradient and U transition. For n64, no world/slot expansion
is permitted; the complete basis relation and independent unsigned recurrence
provide the declared check. Neither control supplies state to Runtime.

The compact journal keeps phase/word counts, exact resource observations,
failure status and minimal directed witnesses. Maximum relation errors are
reported as exact dyadic **upper enclosures** at grid2^-48. This avoids dumping
32,000-bit error fractions; exact per-phase comparison still runs in the job.
No cache, weights, data bundle or bulk phase log is committed.

## Ordered cases and outcomes required

1. `profiles`: n3, C10/default two-rate bank; four profile replay events and
   eight ordinary events. Final cursors8, optimizer steps8/10, at4096 decoder
   bits beneath32768 reference bits.
2. `fresh-install`: n2/C10; sixteen label1 events, then prior newborn and
   separate reference/CUDA fresh identities, followed by twenty label0 events.
   Paired crossing/install at20, continued execution to36, spent alpha1/2.
   Verify the same resident objects, arena, stream, complete reference state
   and phase history across installation. The declared stochastic stream law
   is an external assumption; this deterministic tape does not prove it.
3. `large-closure`: n64/C8/three-rate bank, eight cyclic/band/diagonal events.
   No literal expansion; full parts and twelve gradients checked. Empty policy
   seals `SEALED_CUDA_STREAM` with zero constructor decisions.
4. `range-scale`: n2/C8/S120; two label1 events and the next prediction produce
   native error8950209/16471556096, within the original tolerance, then commit
   label0. The terminal old-graph S120 refusal is unchanged.
5. `wide-denominator`: n2/C4, q=2^200+1 and rates(1/4,(q+1)/(4q)); eight mixed
   diagonal/nonloop events. The 203-bit likelihood scale remains encoded even
   though an exact nonzero feature coefficient rounds to physical zero.
6. `precision-refusal`: same bank/C4;81 diagonal label0 commits. Prediction82
   passes on the actual device; its label0 Reference observation refuses the
   irreducible32,863-bit fixed-gradient denominator. Retain the target and
   both predecessors; enter no physical observation and publish no successor.
7. `reversal`: n2/C10/one rate1/10;52 label0 then52 label1 events. A temporary
   physical zero excess must recover a half forecast at T104/d0. The final
   prediction remains before its target.
8. `unfunded`: insufficient output allowance; no device schedule entry,
   primitive or arena phase, with context and failed frame retained.
9. `second-commit`: fail the second physical lineage commit after two actual
   observations; retain both observed states/target and publish neither.
10. `prediction-word`: change a readout output bit after the actual copy.
11. `coefficient-word`: change a coefficient output bit after the actual copy.
12. `gradient-word`: change an observed gradient output bit after its copy.
13. `operation-word`: change an actual primitive output bit.
14. `old-output`: return an identical-valued earlier resident readout extent;
    current-phase provenance must reject it.
15. `target-swap`: execute the opposite observation target; reject it against
    the independently owned actual target.
16. `plan-roots`: rescale all N/R/Z roots without changing any ratio; the
    canonical actual-input reconstruction must reject it.
17. `rate-parts`: at the reachable two-diagonal-zero cut, replace
    ((648,648),(450,450)) with ((653,643),(442,458)) before the physical scalar
    schedule. Heads remain equal, fixed gradients differ; reconstruction must
    reject the forged parts.
18. `stored-parts`: mutate only retained physical prediction parts after a
    successful prediction; observe must reject the changed predecessor cache.
19. `workspace`: check all three prepaid integer visits, borrowed-view pinning
    and compaction, then fail after the physical construction. Preserve the
    actual paid extent, prior states/history and unrevealed target.
20. `profile-refusal`: after two ordinary events, a four-event profile exceeds
    its one-step prediction allowance. Retain the two completed replay events;
    no attached newborn is published.
21. `legacy-unit`: a fresh four-event original unit-feature root on the shared
    owner, with its original complete native and RNE checker. This is a new
    regression job, not a rerun of a historical attempt.

Injected faults must produce the declared refusal/failure and preserve prior
frames, learner publication and the actual target state. A matching accuracy
tolerance cannot excuse a mismatched primitive, coefficient word, part,
target, complete state or physical extent. Unexpected failure ends the attempt
and becomes evidence to investigate; it does not justify a semantic change.

This gate claims no population model quality, learning superiority, GPU integer
inference, constructor completeness or full indexed release. Foundation,
ERC-1 and all existing exact decision classes remain unchanged.

## A1 outcome (after execution)

The [original journal](../../evidence/minimal/FP_RATIONAL_FEATURE_AMP_CUDA_A1.json)
retains execution at e16c976. Profiles and paired fresh installation pass,
including continuation to36. The third job fails during n64 finite-run
sealing: the closed diagnostic reader omits DecodedPrediction and requests
a nonexistent dense `values` array. No job memory/time limit triggers. The
remaining eighteen cases are unexecuted. A1 is terminal and unscored beyond
its two passing jobs; its preregistration above is unchanged.

The missing type registration is repaired separately and a focused CPU
diagnostic audit passes. A continuation attempt must register its changed
source before any further actual jobs; these original outcomes stay intact.

## A2 continuation registration (before execution)

Production anchor: `dcdd3e9`. A2 executes exactly the original ordered cases
3 through21: repaired n64 closure, then the eighteen cases A1 never reached.
Cases1/2 are not rerun. Their passing profile/install evidence remains bound
to e16c976, and no single-source complete21-case execution is claimed.

The only production difference from e98065e is the closed cache-type dispatch
in run_state.py. No physical primitive, learner, range, source binding,
resource allowance, freshness or installation code changes. The focused
CPU report audit is a new prerequisite. All original case inputs, numerical
limits, caps, deadlines, output/frame allowances and expected outcomes above
remain fixed. This changes the consumer implementation; it is not a cap or
tolerance rescue of a failed numerical experiment.

The new runner preflight checks the terminal A1 source, two passes, third
failure and exact missing-type traceback, plus the changed-file boundary.
After committing this registration, run `--attempt 2`. It writes the separate
`FP_RATIONAL_FEATURE_AMP_CUDA_A2.json`, preserves all outcomes and stops at
an unexpected failure. `--attempt 1` is refused by the new runner. A2 is
**REGISTERED, NOT YET EXECUTED** at this paragraph's registration commit.

## A2 outcome (after execution)

The [original A2 journal](../../evidence/minimal/FP_RATIONAL_FEATURE_AMP_CUDA_A2.json)
is terminal at f298eab. n64 closure, C8/S120 and the 203-bit denominator pass:
60 phases, 19 independently reconstructed predictions and 1,822 primitive
words. The precision-refusal case instead stops at observation T=41, with
`reference operation may exceed its integer work limit`. No memory/time
limit triggers. No detailed independent phase summary is retained for that
failed job; it remains unscored. Original cases7..21 never run.

CPU localization finds an exact error-comparison cross product of 33,492
bits, although canceling the shared denominator reduces it to 16,732 bits.
The native gradient fits and the rounding error is below tolerance. Thus
the original expected first refusal at T=81 is false for the A2 verifier.
Preserve its original preregistration and result; do not relabel it a pass.

The subsequent [paid reduced-arithmetic proof/audit](../../theory/proofs/OWNED_RATIONAL_FEATURE_AMP.md#8-paid-gcd-reduction-exact-valueorder-with-a-distinct-resource-promise)
changes the exact relation solver and work tariff. Native G/Gamma/U, physical
primitives, caps and tolerances remain. A new CPU continuation reaches the
true materialized-gradient obstruction after81 commits. This improvement
requires a separately registered A3 before further device execution; the
five successful A1/A2 jobs are not repeated or attributed to its source.

## A3 continuation registration (before execution)

Production anchor: `95ba561`. Execute original cases6..21, exactly sixteen
fresh jobs: the wide precision-refusal continuation, then the fifteen
unexecuted cases. The five successful original cases keep their A1/A2 sources
and are not run again. No single-source complete21-case gate is claimed.

The changed production boundary is numerics.py and float64_bridge.py for
the distinct guarded value/order helpers, rational_feature_amp.py for their
use and work ID, joint_amp.py for its unchanged old tariff, and cuda_prefix.py
for closed tariff dispatch. The new ID is
`prepaid-rational-feature-parts-and-gcd-reduced-complete-native-relation-v2`.
The owner pays2048*(d+2n+8J+32) for either rational-feature relation. The old
unit-feature coefficient remains512. No native Reference operation or
physical primitive changes, and all original bit/range/tolerance, output,
frame, root work/bytes, GPU/host caps and deadlines remain fixed.

The CPU proof/audit of this solver is a new prerequisite. The precision
case again expects81 commits and a checked82nd prediction before the next
native gradient's32,863-bit denominator returns UNRESOLVED. This is a
prospective expectation for the changed solver; A2's earlierT=41 refusal
remains the actual result of its original registration.

Preflight checks both original journals and the new exact audit, locks the
production anchor and changed-file boundary, and records the work change.
Commit this registration before `--attempt 3`; the runner refuses attempts1/2
and writes a new `FP_RATIONAL_FEATURE_AMP_CUDA_A3.json`. Stop at any unexpected
failure and retain every outcome. A3 is **REGISTERED, NOT YET EXECUTED** at
this registration commit. No Foundation/ERC-1 or release scope changes.

## A3 outcome (after execution)

The [original A3 journal](../../evidence/minimal/FP_RATIONAL_FEATURE_AMP_CUDA_A3.json)
is terminal at862e91c: fourteen jobs pass. Summarized blocks check566 full
native phases/189 predictions/12,090 primitive words. The actual wide case
reaches81 commits and a checked82nd prediction before the32,863-bit native
gradient correctly refuses, retaining its target and publishing nothing.
Reversal, all declared word/target/part attacks, funding, atomic publication
and pinned workspace cases pass. No memory/time limit triggers.

The profile-refusal job then fails in its passive full-state reader, which
tries to materialize committedT=2 under the live prediction capQ=1. Q=1
legally permits the prediction atT=1 and its commit, then refusesT=2's next
forecast. A separate materialization needs its own Q>=2 allowance. The job
remains unscored; the last legacy-unit case never runs. Keep this audit
failure distinct from a Runtime semantic, resource or physical failure.

## A4 continuation registration (before execution)

Production remains `95ba561`, identical to A3's862e91c execution source.
A4 runs only original cases20/21: profile-refusal and the unexecuted fresh
legacy-unit regression. Nineteen prior passes are not repeated or reassigned.
No production file, runtime cap, physical schedule, solver tariff, tolerance,
output/frame allowance, host limit or deadline changes.

The passive reader now declares a materialization step cap max(Q,T), where
Q is the original live prediction allowance and T the encoded committed
state being independently audited. Its existing literal bit cap remains
131072; it runs inside the same bounded fresh job. The profile case thus
reports liveQ=1 and passiveQ=2. These extra audit reads issue no prediction,
profile, constructor or publication authority to Runtime.

The [CPU witness](../../evidence/minimal/FP_RATIONAL_FEATURE_READER_BUDGET.json)
checks all four two-target histories, eight full literal comparisons and
eight old-reader refusals; later live predictions remain UNRESOLVED. This
is a prerequisite alongside the three terminal journals and earlier exact
audits. Preflight enforces unchanged production and records the audit change.
Commit this declaration before `--attempt 4`; only the new separate A4
journal may be written, with the same stop-first-unexpected-failure policy.
A4 is **REGISTERED, NOT YET EXECUTED** at this registration commit.
