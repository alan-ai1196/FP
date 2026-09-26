# Actual ordinary-token AMP results

Status: **BOTH ORIGINAL JOBS COMPLETE AT17c9204; ZERO-ERROR LEARNER BRIDGE
FALSIFIED, 2026-09-26**. The
[original preregistration](AMP_SCHEDULE.md) and
[11,671-byte journal](../../evidence/minimal/FP_TOKEN_AMP_CUDA_A1.json)
retain the full scope, target/build identities and actual job observations.
Both jobs are terminal. Do not rerun them.

The RTX3090 exactly reproduces the half-underflow counterexample: current
probabilities agree, native and physical next masters differ, and the actual
next ordinary token context exposes probability gap1/524286. The witness
and all six small trajectories pass2,006 exact primitive calls/10,020 raw
word checks, including976 half words and27 fixture commits. This establishes
the declared physical arithmetic at those inputs, not exact native learning.
The mixed small trajectories differ by at most two readout grid units.

The full-vocabulary/context512 job processes the same first512 training
tokens and supplied fixture as the CPU feasibility gate. Every feature,
normalizer, target mass and complete gradient-basis word, plus all603,092
endpoint masters, agrees with the independently executing CPU mixed-precision
path. The device retains its own state and computes its own gradients and
successor; the native reference never supplies a trained device endpoint.
Sources, clocks and the unchanged previous origin also agree.

Against the independent native enclosure reference, the largest endpoint
distances in grid integers are **input0, core1, readout1**, with grid2^-16.
These are complete-block comparisons. They are not a tolerance-qualified
bridge, an install authorization or a future-error guarantee.

## Numerical reporting correction

Post-run review finds that the original fields named
`full_basis_absolute_error_upper` used nearest binary64 subtraction when
measuring distance to enclosure endpoints. That last subtraction also needs
an outward bound. For example, |2^-100 - (-1)| rounds to1, below its exact
value. No physical computation, word comparison or integer-master comparison
depends on this diagnostic, and no bridge tolerance was tested against it.

Preserve the original journal. If m is its nonnegative rounded maximum,
the next larger binary64 value bounds every exact endpoint distance that
contributed to m; exact zero remains zero. Monotonicity of rounding and one
adjacent successor suffice. The
[reader and exact diagnostic witness](../../scripts/read_token_amp_audit.py)
apply this correction without reexecuting any trajectory; future diagnostics
now perform it at the measurement site. Nonfinite bounds refuse.

Conservatively rounded-up bounds for the real unit are:

| Complete quantity | Maximum absolute discrepancy upper |
|---|---|
| Stored core/input values | 0.000540010 |
| Normalizers | 0.005349873 |
| Target masses | 0.000000131683 |
| Pending embedding gradients | 0.001539825 |
| Pending core gradients | 0.562991 |
| Readout common-gradient basis | 0.002832511 |
| Readout target-correction basis | 7.587222 |

The gradient sums are over512 records; these raw absolute quantities have
different scales. An error in the common/correction representation is not
automatically the same bound on their signed difference. The explicit
state relation must account for both, all coordinates and the projection.
The table does not select or waive any bridge tolerance.

## Physical cost and next decision

Both jobs exit0 inside their original4-GiB/900-second host fences with no
timeout or limit termination. The small job peaks at1,849,323,520 bytes of
job commitment; the real-unit job peaks at2,078,146,560 bytes. Torch maximum
reserved VRAM is2,097,152 and69,206,016 bytes respectively, below the fixed
512-MiB allocator cap. The actual board identity remains bound to the
conservative24-GiB physical upper. This is not exclusive GPU reservation or
a total-machine cost claim. Cumulative process count2 may include denied
starts under the live active-process cap1, as in the existing launcher.

The real unit's106 synchronous checked floating operations and commit take
0.20284 s. The whole job, including imports and CPU/reference controls,
takes3.48435 s. This audit synchronizes frequently and does not establish
competitive training throughput. No loss, validation/test score, topology
selection or model ranking is collected.

The practical execution obstacle is now precise: this actual AMP learner
is affordable, but current prediction equality does not preserve complete
native learning. The next work is the **owned complete state/error relation
inside ReferenceCompilerRuntime**, with declared tolerances or justified
numerical refinement and honest unresolved boundaries. Do not silently
require exact native masters from this underflowing schedule, snap device
state to the reference, or widen tolerances after a failed run. No semantic
architecture action or Foundation change is needed for this numerical issue.
Then proceed to ordinary text learning with fresh strong baselines; this
gate does not justify another static or relation-task study.
