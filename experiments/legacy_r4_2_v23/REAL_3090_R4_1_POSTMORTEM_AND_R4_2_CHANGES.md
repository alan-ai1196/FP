# Real RTX3090 R4.1/V23 postmortem and R4.2 changes

This document records the second real RTX3090 execution of the v23 Compiler lineage. It is runtime/debug evidence only. R4.1 produced no completed native seed and must not be pooled into FP-vs-GPT science results.

## 1. What R4.1 successfully established on the target GPU

Stage01 executed **32/32** checks on the RTX3090 with `all_pass=true` and no deferred CUDA checks. The registered AMP bridge remained stable:

- max AMP-vs-FP32 NLL drift: `4.673004150390625e-4`;
- stream-vs-validation gap: `1.52587890625e-5`;
- validation AMP-vs-FP32 gap: `2.1457672119140625e-6`;
- strong good/bad ordering agreed between AMP and FP32.

Task-blind preflight selected `same_l3_one_per_core`, CPU IDs `[258,260,262,264,266,268,270]`, measured about `2.0824e8` ordinary GPU tokens/s, and about `0.509 s` mean compiler microtrial time at 131072 evidence tokens/scan.

R4.1 also verified that the R4 fixes were real rather than cosmetic: learning no longer waited for the first 450-second validation snapshot. Seed 1337 produced its first train-only structural candidate after about **1.576 s** of CPU compile wall and completed a matched physical transaction shortly thereafter.

The first candidate had:

- exact incumbent quotient rank 0;
- 2 residual-adaptive pricing scans, adding `[16,16]` fresh columns;
- 23 active cone atoms;
- local response lower bound `39.29840694653103`;
- conservative upper bound `65536.0`;
- confirmation gain `1.3605379273951002e-4`;
- 3 new positive confirmation masses.

The transaction completed rather than crashing. It logged aggregate future CE `7.748075723648071` for the value-only/deployed side and `7.747755408287048` for the structural side. R4.1 nevertheless rejected the structural branch under its predecessor transaction policy. Section 4 explains why that policy itself was subsequently rejected.

## 2. Actual R4.1 failure: numerical nonclosure was treated as a fatal exception

At about 140 s, an asynchronous Compiler job reached an ill-conditioned restricted NNLS. The small Gram fast path did not pass original-response KKT verification, so R4.1 fell back to the predecessor response-space Lawson-Hanson pivot solver. That solver hit its numerical iteration cap and raised:

`RuntimeError: finite NNLS response-space solve exceeded numerical iteration cap`

The failed Future then remained installed long enough for the same exception to be observed again during shutdown.

This is the wrong semantics for v23. For any finite restricted cone, every finite nonnegative vector `mu >= 0` is already a legal executable lower-bound witness. Failure to prove restricted KKT closure is therefore **not** failure to produce a legal FP candidate and is not permission to kill the trajectory.

R4.2 changes the contract to:


a) attempt the small Gram/QP fast path;

b) verify KKT in the original response geometry;

c) if necessary, perform monotone nonnegative coordinate refinement in the small Gram system;

d) use a warm active-face response-space polish only as a rare final refinement;

e) always retain the best finite feasible nonnegative witness;

f) if the restricted KKT still does not close to the declared tolerance, report `restricted_solver_closed_to_tol=false`, preserve the executable lower bound, and keep the global cone **UNRESOLVED**.

Numerical nonclosure is therefore a certificate state, not an exception.

A forced real-size near-collinear stress (`N=131072`, `m=32`) took about `0.71 s` for coordinate refinement plus `0.29 s` for one warm response-face polish, reaching original-response KKT about `2.7e-12`. A deliberately crippled predecessor active-set cap still returns a finite nonnegative witness rather than throwing.

## 3. The same latent failure existed in positive-measure continuation

Adversarial fuzzing found that the bound-constrained positive-measure quadratic solver could also hit its active-set iteration cap on strictly SPD but highly ill-conditioned score-metric QPs. Merely fixing restricted NNLS would therefore have moved the crash from discovery into confirmation/value continuation.

R4.2 gives the positive-measure QP the same fail-safe semantics. The shifted variable `u=d+alpha >= 0` is solved by monotone small-dimensional coordinate refinement plus warm active-face polish. The solver always returns a feasible `d>=-alpha` and an explicit KKT residual. A numerically unresolved QP may not authorize cross-fit/value continuation; it becomes `no-commit / unresolved`, while the trajectory continues. Any actual mass update still requires exact normalized-positive NLL Armijo descent.

The deterministic release fuzz covers 128 near-singular score-metric QPs. A broader 500-case near-collinear exact-NLL attack produced no exceptions; rare numerical nonclosure was conservatively rejected rather than mislabeled successful.

## 4. R4.1 transaction acceptance contained an unjustified controller condition

The real R4.1 transaction exposed a second, independent issue. The candidate's aggregate paired future CE was lower than the value-only side, yet R4.1 could veto it because the code required the candidate to be noninferior in **every diagnostic evaluation block**.

No v23 theorem gives block partitioning this semantic role. The v22/v23 physical objective is the declared aggregate lifecycle task loss under the hard physical contract. Evaluation blocks are useful heterogeneity diagnostics, but `all blocks must win` is a historical if/else controller action and is removed in R4.2.

The build-host selection oracle now explicitly includes a witness where the structural branch wins aggregate CE while one diagnostic block is worse. The structural branch must still be selected.

## 5. The physical branch set itself was incomplete

A deeper audit showed that R4.1 structural selection compared only:

1. value-only continuation;
2. candidate + value continuation.

If value-only continuation changed active masses, the already deployed program was omitted. That violates the absolute physical objective because `do nothing` is itself a legal physical program with zero new realization cost.

R4.2 therefore uses the absolute branch set

`{ deployed, value-only continuation, structural continuation }`.

All distinct branches execute sequentially under the same hard system-wall and VRAM contract; the deployed route remains resident and at most one shadow exists at a time. If value-only is semantically identical to deployed, it aliases deployed exactly. Aggregate common-future CE selects the strict feasible argmin, with deployed winning exact ties. Diagnostic block splits never veto the aggregate winner.

A non-deployed final commit is atomic with its causal state. If the final persistent build fails or violates the hard VRAM gate, **both** the program realization and the KT/cursor state fall back to the deployed branch. A deployed program may never continue with a different branch's prequential state.

## 6. Async failure propagation

R4.2 clears a failed Compiler Future and its compiling-bank/pending state before propagating a genuine implementation exception. Thus a real code/shape/CUDA error still fails fast, but it is propagated once rather than lying dormant and reappearing again from `close()`.

Numerical solver nonclosure is not an exception and therefore never enters this path.

## 7. Scientific status

R4.1 supplies useful hardware and runtime evidence:

- all 32 target Stage01 gates passed;
- online-from-first-evidence learning worked;
- batched pricing reduced early Compiler latency into the ~1.6 s range;
- the first matched transaction actually executed.

It supplies **no completed native seed** and therefore no valid FP-vs-GPT science result. Native stages must restart from 0 in R4.2. The bundled historical GPT JSONs remain the explicitly authorized reused baseline evidence.

## 8. Physical selection and persistent commit are distinct telemetry events

A final schema audit found one remaining reporting ambiguity after the three-way transaction rewrite. A physical branch comparison can finish after the final preregistered validation snapshot. In that case the transaction result is deliberately discarded to prevent a branch future observed after the experiment horizon from retroactively changing the reported trajectory. The physical selector may therefore have preferred `value` or `structural` even though no persistent program update occurs.

R4.2 records these separately. `matched_system_time.chosen_branch` is the physical selector result; `committed_branch` is the branch that actually becomes the persistent trajectory state. Final-snapshot discard records `committed_branch=deployed` and `program_changed=false`. The integrated readout counts only `committed_branch`, so an uncommitted shadow winner cannot be misreported as a learned structure or value update.
