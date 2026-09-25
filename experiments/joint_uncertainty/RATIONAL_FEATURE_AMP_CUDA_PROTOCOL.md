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
