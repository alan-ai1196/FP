# Continuous actual CUDA learner mechanics

**Status, 2026-09-13:** implemented mechanical executor; finite independent
exact-rounding and actual RTX 3090 audit. Its subsequent
[owned Runtime prefix](OWNED_CUDA_PREFIX.md) now registers device state and
per-phase relations, and a separate [resident install](OWNED_CUDA_INSTALLATION.md)
now executes its own owned transition. Foundation and ERC-1
are unchanged; this is their physical implementation frontier.

Source: [`cuda_learner.py`](../../src/reference_compiler/fp_reference/cuda_learner.py).
Run `python -B scripts/audit_cuda_learner.py --write`; retain only
[`FP_CUDA_LEARNER_AUDIT.json`](../../evidence/minimal/FP_CUDA_LEARNER_AUDIT.json).
The independent interpreter uses exact Fractions and the audited binary
rounding oracle, with its own native evaluation and incoming-edge tape.
It never invokes the GPU implementation to calculate expected successors.

## Executed arithmetic schedule

The backend ID is
`eager-cuda-half-forward-single-sum-readout-backward-master-v1`.
Its actual tested build/device are recorded separately. An ID without that
execution identity and checked prefix will not constitute a bridge.

| Stage | Explicit operation |
|---|---|
| External input and initializer | Host exact nearest/ties-even binary32 encoding, followed by actual CUDA transport. This host computation and transport need resource ownership during integration. |
| Parameters and sources used in forward | Master parameters and encoded sources cast to binary16 on device. No trained reference endpoint is supplied. |
| Native PRODUCT and weighted SUM edge | Separate binary16 multiplication of the stored operands. |
| Native SUM | Each half edge product widens exactly to binary32; accumulation follows native edge order; the completed node casts to binary16. |
| Nodes and all delayed queue entries | Binary16 device tensors. Each observe shifts the complete queue and appends its actual positive body. |
| Positive base, normalizer and raw division | Binary32 base addition, ordered binary32 mass sum and division by the resident device normalizer. Stored-mass probabilities remain a separate exact diagnostic object. |
| Event derivative | Stop-gradient delayed inputs, identity cast derivatives, binary32 reverse operations using the stored half forward values and coefficients. This is the declared numerical approximation to the reference derivative, not a derivative of the discontinuous rounding function. |
| Accumulation and update | Binary32 gradient sum and master parameters; device-tensor mean-step division; separate step/negation/addition/projection; optional exact floor-to-dyadic-grid by binary32 bit operations. |

There is no loss scaler or automatic differentiation in this schedule.
It executes explicit mixed precision; it does not rely on an autocast flag.
Each tensor predecessor stays unchanged. Ordinary observations keep the
master parameter tensor until a real update; profiles preserve every
parameter, queue and accumulator tensor during full-unit clock attachment.
A partial final unit remains partial.

## Executed coverage

All 64 three-event binary context/target streams run an actual reference
baseline/candidate in `ReferenceCompilerRuntime` and corresponding separate
CUDA learners. Their 1,024 device phases match the independent rounded
interpreter's full states and predictions. Actual Runtime reference states
supply a separate comparison, not device successors or GPU evidence.

A recurrent profile replays two already revealed Runtime records three
times, retains both entries of its delayed queue, attaches at ordinary
cursor two and continues through cursor six. Both baseline and candidate
CUDA trajectories continue; the candidate retains five optimizer steps.
This contributes 42 checked device phases. A further 24 seeded native DAGs
with three labels, repeated heads/edges/squares and an unused slot contribute
240 phases. Their arbitrary legal positive source values include a directed
host-single/device-half double-rounding input.

In total, 1,306 phases execute 2,452 actual half multiply results. All 6,022
half and 31,706 single arithmetic/ingress results are observed on the phase
tapes. Full-state/prediction agreement is checked at every phase endpoint;
these counts do not assert independent scalar-oracle comparison of every
tape intermediate. An additional 1,340 positive binary32 coordinates check
the floor operation exactly, including subnormals and grid indices beyond
binary32's finest lattice.

Of 1,200 coordinates compared to actual exact Reference Runtime states,
326 differ from simply recasting that reference state. Largest observed
absolute differences are approximately `2.1628e-4` for the short streams and
`8.7477e-5` for the recurrent/profile run. These are finite diagnostics, not
registered tolerances or future error bounds. The 24 other DAGs compare to
the exact rounded model only; their report does not invent a reference
comparison or a zero-error result.

## A finite endpoint can hide a nonfinite execution

Take a finite binary32 master parameter zero, a finite gradient equal to
the maximum finite binary32 value, and mean learning-rate scale two. The
actual device multiply overflows to positive infinity; negation and addition
produce negative infinity. The positive-part projection then returns finite
zero. Accepting only the final parameter would miss that execution failure.

The executor retains every arithmetic intermediate until its phase check,
which refuses this case with `ArithmeticUnresolved` and preserves the input
learner. The audit inspects the actual infinity and the subsequently finite
zero in the same failed tape. Half forward overflow, incomplete clocks,
missing sources, implicit scalar/promotion paths and mutated nonfinite
parameter handles are also refused. No CPU fallback replaces device work.

## Remaining authority boundary

The same mechanics now also execute inside one prepaid tensor arena through
explicit output views; see
[`BOUNDED_CUDA_TENSOR_STORAGE.md`](BOUNDED_CUDA_TENSOR_STORAGE.md).
All 1,306 learner phases use a single 16 MiB device allocation without a
further native allocator allocation. This closes that tensor-storage
component only; host evidence, Runtime ownership and total-device resources
remain separate obligations. The arithmetic schedule above is unchanged.

GPU tensors are mutable physical handles; the mechanical dataclasses confer
no value equality, provenance or certificate. These helpers expose no
signer. The audit's raw readbacks and phase temporaries are diagnostic work,
not paid Runtime evidence. Importing this module does not import Torch or
initialize a GPU, so the frozen CPU execution surface is unchanged.

The [owned Runtime integration](OWNED_CUDA_PREFIX.md) now registers this
schedule, owns device tensors and raw phase evidence, checks exact numerical
relations and publishes reference/device successors together. Separate
[current range/persistence](OWNED_CUDA_PERSISTENCE.md) and
[resident installation](OWNED_CUDA_INSTALLATION.md) now execute their own
owned obligations. Full device resources and target run/release remain open.
The generic full-release install port still returns UNRESOLVED. This component
neither borrows CPU wealth nor closes an AMP release gate. Model science
remains HOLD.
