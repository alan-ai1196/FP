# Complete prediction values from captured immutable operands

Status (2026-10-03): **lossless live-state refinement proved; focused exact CPU,
25-script committed-source regression and both actual RTX 3090 A2 controls
pass; scoped qualification CLOSED**. No Foundation/ERC change, new
architecture action, numerical approximation or certificate class is added.

The [historical liveness law](NATIVE_PREDICTION_LIVENESS.md) excludes the original
million-target host budget because every trace retains LD newly allocated input
Fractions. Keeping those particular allocations is not necessary to preserve
the complete values. This refinement captures their exact immutable operands,
keeps every actual arithmetic-node result, and continues to expose the entire
original value tuple through the declared interfaces. It does not erase traces
or identify parameters that happen to have equal values.

## 1. A lossless representation, with no reconstruction of numerical execution

Let E be the exact immutable embedding bytes of the pre-target origin, D its
positive embedding width, p the exact immutable causal token tuple, Q the
registered power-of-two grid, and a the tuple of actual executed SUM/PRODUCT
outputs. The physical capture is the five-tuple (E,D,p,Q,a). Its logical value
at input index i, with 0 <= i < |p|D, is

    decode(i) = Fraction(uint32_le(E, 4*(p[i//D]*D + i%D)), Q).

The remaining logical values, in order, are a. The capture validates exact
types, embedding row extent, token domain, grid and exact Fraction tail. It
contains neither a replaceable Origin/Window wrapper nor a lookup into the
latest learner. Replacing such a supplying wrapper therefore cannot change
an already captured value. This is about immutable value operands, not a claim
that arbitrary Python code or scalar internals are unmodifiable.

At prediction time the implementation decodes this capture to the input tuple
and executes the **unchanged** `_forward`, with its original exact operation
order and bit/range guards. It then retains the capture with the actual tail
of that execution. No old SUM/PRODUCT result, normalizer, head bound or readout
is recomputed from newer parameters. In particular, the capture cannot silently
repair a wrong numerical result: it preserves whatever tail the execution
actually produced, subject to the existing checks.

On the supported little-endian uint32 native realization the decoder equals
the original `Fraction(int(origin.E[token, channel]), Q)` at every input. The
initializer already requires that realization. Thus its input tuple is exactly
the old input tuple, `_forward` has the same inputs, and the retained decoded
tuple equals the old complete result. Successful target validation, gradients
and grid commits follow from the unchanged native update and its original
source/predecessor relation. This proof applies to all legal input words and
masters in this representation, not only the sampled two-token vocabulary.

## 2. Complete continuation and ownership argument

Define projection P by replacing each capture with its complete decoded tuple
and leaving every other logical coordinate untouched. The typed canonical
encoders, bounds, phase writer and public value copier implement that same P.
Induction on a finite value tree gives

    canonical_bytes(captured_state) = canonical_bytes(P(captured_state)).

All integers, tuple tags, order, multiplicity, metadata, source origins and
guard decisions are included. Public exports are exact builtin tuples; one
copy memo preserves repeated references to the same exported capture. They
furnish no mutable path back to the capture or its enclosing private wrappers.
The capture has a closed exact class with tuple backing and no writable
instance dictionary/slots. Even instances forged with `tuple.__new__` must
validate every physical coordinate before use or image admission.

The same before-state, causal window, original embedding/core/readout bytes,
parameter positions, probability features, target, pending record and event
trace remain stored. All registered later source queries, profiles, cache
revalidation, range checks, diagnostics and archive reads therefore receive the
same complete values. Distinct source/parameter/gradient coordinates are not
merged by numerical equality. No new semantic state or callable authority is
introduced. Physical identity of newly decoded immutable scalars is not part
of FP's claim interface; public scalar-internal mutation and trusted-class
replacement remain outside the existing [value model](PUBLIC_VALUE_OWNERSHIP.md).

The private physical five-tuple is not advertised as a generic Python/C tuple
ABI. In particular, explicit base-class tuple operations can inspect its
physical representation. Actual FP consumers use the complete logical
sequence; public results materialize builtin tuples. The ordinary logical
sequence operations are covered by exact controls, not a promise about every
third-party introspection/serialization library.

Canonical images can bind the closed immutable capture. Their independent
initial full-byte comparison and size/traversal/depth/integer-bit checks remain.
The optional expression format binds the immutable parent, but **does not add
identity bindings for transient decoded Fraction children**. Doing so would
keep the very input objects this refinement removes. The identical scalar
terms are still constructed and independently checked, and every byte remains
recoverable. This compatibility change can reduce expression-binding metadata
and its later charges; it does not promise identical physical histories for
that optional representation. No new codec, flag or cost variant is introduced.
Default packed/shared byte retention has identical complete bytes and charges
in the paired controls, including image source projection.

The native-to-AMP bridge still iterates **every** decoded native value against
its independent enclosure. Physical primitive words, fresh raw reads, retained
frames, source binding, persistence and install reachability are unchanged.
CPU tensor controls do not establish actual-device qualification.

## 3. Resource law and failure boundary

For the installed Windows x64 CPython 3.12.9 layout, the capture occupies 80
bytes and a tail tuple of N values occupies 40+8N bytes. Thus the selected
capture/tail containers have the upper law

    H_containers(T) <= T [80 + 40 + 8N].

For N>0, this implementation creates a distinct tail per prediction and the
selected shallow sizes equal that expression. For N=0 the empty tuple can be
shared, so the inequality deliberately avoids charging it T times as distinct.
Embedding bytes and p are actual already-owned references, checked by identity;
the capture makes no extra embedding/context copy. The text model's N=8 costs
**184 bytes per retained prediction**, or 192,937,984 bytes (184 MiB) of these
containers at T=1,048,576. The historical selected input-Fraction/tuple component
was 114,792 bytes per prediction, or 112.1015625 GiB at that horizon.

These are deliberately **selected components, not total host bounds**. Grid
integers, actual node values and integer referents, old masters/windows, trace
wrappers, images/archives, ledger state, allocator slack and all other state
remain additional. In a general graph, let K_in be the number of distinct
input indices selected directly as readout features. At most K_in original
input Fraction objects per prediction can remain via `TokenProbabilities`.
Repeated selection preserves the existing alias; different coordinates remain
distinct even when equal. The full text program selects only its eight node
outputs, so K_in=0. The result is not a universal elimination of input storage
for every possible graph or every caller retaining its diagnostic exports.

Prediction still transiently materializes all LD inputs. A complete public
snapshot can likewise materialize all historical tuples; serialization and
image admission can allocate transient decoded scalars. All this consumes
real host memory and CPU. No reduced host peak or elapsed time is inferred.
The same conservative abstract construction/evaluation tariff
16*(slots+inputs+edges+1) is charged. Capture validation adds bounded passes
over p and a; decoding replaces the old LD input construction, and copying the
N-value tail is linear. The added passes cost O(|p|+N), without any traversal
of growing event history. In the text registration D>=1 and N is bounded by
the nonempty SUM/PRODUCT edge count, so the same registered expression bounds
the added work's order. This is not asserted for arbitrary empty-SUM graphs:
the allowance remains the declared abstract tariff, not a universal Python
instruction count, bit-cost or heap theorem. No debit is removed.

Allocation failures may occur at different physical points. A failed capture
before prediction success cannot issue a forecast. A failure in the post-target
cache recomputation keeps the revealed target and old learner, without advancing
the cursor. Failure exporting an already completed snapshot keeps its published
prefix. The existing terminal host guard closes subsequent authority and
never refunds work, retracts a target or restores a former learner.

## 4. Evidence and stopping boundary

[`FP_CAPTURED_TOKEN_VALUES_CPU.json`](../../evidence/minimal/FP_CAPTURED_TOKEN_VALUES_CPU.json)
contains 558 exact value vectors, 17,856 paired guard decisions, 39,660 equal
fragments, twenty malformed captures and supplying-wrapper mutation controls.
The historical comparator loads the actual `c67a0aa` literal prediction methods
and verifies that their remaining token-module dependencies are unchanged.
There are 98 complete history pairs/512 targets per arm and six complete CPU
tensor pairs with 129 full bodies, 5,774,243 bytes and 50,279 primitive words.
Two original full-vocabulary synthetic events preserve all buffers/role totals
and compare 502,252,884 complete serialized snapshot bytes. The million-target
declaration remains unchanged; no corpus or report is opened by that control.

[`FP_CAPTURED_VALUE_BOUNDARIES_CPU.json`](../../evidence/minimal/FP_CAPTURED_VALUE_BOUNDARIES_CPU.json)
adds twelve existing typed-phase vectors/108 cap decisions, complete canonical
image/expression recovery, malformed-image refusals, wrong-byte and five new
host-failure points. Forty-eight direct/repeated-input-feature history pairs
check another 192 targets per arm and 10,752 exact pending-gradient coordinates
across both arms. Every successful paired result and complete snapshot agrees.
The historical 192-history liveness audit also still passes with the actual
old methods; its original receipt is preserved as a historical result.

The complete [25-script CPU bundle](../../evidence/minimal/FP_CAPTURED_VALUES_REGRESSION_CPU.json)
passes at `e13e480` with assertions enabled and source unchanged. It includes
owned reference construction/search/events/profiles, persistence, installation,
reporting, public ownership, host exhaustion, both archive formats and the new
controls. Its actual Windows refusal worker exits zero after the expected
MemoryError, preserving the terminal prefix under its independent 64-MiB job.
The [first actual device control](../../experiments/next_token/CAPTURED_VALUES_CUDA_A1.md)
is terminal UNRESOLVED at `eb8e130`: its post-execution historical comparator
tries to spawn Git inside a one-process Windows job and receives error 1816.
The packed worker exits 2 within its host/time caps; shared is not launched.
This is a harness mismatch, without an observed numerical disagreement. It
does not issue a completed actual qualification, and its journal stays closed.
The corrected [A2 control](../../experiments/next_token/CAPTURED_VALUES_CUDA_A2.md)
loads a launcher-extracted, integrity-bound historical source artifact without
creating a child. Its native harness passes with `Popen` forbidden, and altered
source bytes refuse. Both original actual packed/shared workers now pass at
`6411310` with unchanged production code and limits. Each preserves nineteen
actual AMP phases, 6,340 checked primitive words, 731,331 complete phase-body
bytes and all 19,922,944 retained frame bytes, through four training targets,
two commits and four frozen report targets. All eight native forecasts match
the historical comparator at all 96 values and 61,793 canonical bytes. Public
isolation, frozen native/physical identity and terminal export failure pass.
Both jobs exit zero within 4 GiB/180 seconds, with source and the single
32-MiB arena unchanged. No full-V device, matched cost or whole release follows.

This removes the proved eager-input allocation obstruction. It does not prove
the million-target trajectory fits 96 GiB, its deadline or its numerical bounds,
nor supply a trained score. Close this scoped representation qualification and
assess the **complete** ordinary-text budget. Do not
reopen relation/precision, replay closed timing journals or add static variants.
