# Actual CUDA lowering before the AMP bridge

**Status, 2026-09-13:** exact arithmetic counterexamples with actual RTX 3090
reproduction, plus a finite primitive audit. This specifies obligations for
the active device implementation. It adds no Foundation action or static
resource family and does not close an AMP Runtime gate.

Run `python -B scripts/audit_cuda_primitives.py --write`. The small result is
[`FP_CUDA_PRIMITIVE_AUDIT.json`](../../evidence/minimal/FP_CUDA_PRIMITIVE_AUDIT.json).
The tested stack is PyTorch 2.12.0+cu132, CUDA runtime 13.2, driver 616.92,
RTX 3090 / SM 8.6. Operator identity, operand residence, dtype and cast order
are part of the physical path; an output dtype alone does not determine it.

## Three executable distinctions

Write R16 and R32 for nearest/ties-even rounding to gradual binary16 and
binary32. All operands below are positive and exactly representable in their
declared input formats.

**Separate operations versus a combined kernel.** For
`a=b=1025/1024, c=1/2048`, actual half `(a*b)+c` returns `1026/1024`
(`0x3c02`). Half `torch.addcmul(c,a,b,value=1)` returns `1027/1024`
(`0x3c03`). The stored multiply rounds before the separate addition; the
combined path retains its small product remainder until addition.

**A combined half kernel need not be one-round half FMA.** Take

```
a = 1027/1024, b = 3/2, c = 2^-24.
ab = 3081/2048 = (1540 + 1/2)/1024.
```

Here `ab` is a half midpoint, and the positive `c` moves the exact result
above it. Thus `R16(ab+c)=1541/1024` (`0x3e05`). But binary32 spacing here
is `2^-23`; `ab` has an even binary32 significand and `c` is a half-ULP.
Consequently `R32(ab+c)=ab`, and its final half tie rounds to even:

```
R16(R32(ab+c)) = 1540/1024 = 0x3e04.
```

Actual half `addcmul(value=1)` returns this latter value. The observed result
agrees with the versioned implementation: the real half path promotes to
float accumulation and its `value=1` helper uses `std::fma` before the
storage conversion. [PyTorch kernel](https://github.com/pytorch/pytorch/blob/v2.12.0/aten/src/ATen/native/cuda/PointwiseOpsKernel.cu),
[versioned helper](https://github.com/pytorch/pytorch/blob/v2.12.0/aten/src/ATen/native/cuda/DeviceAddCmulCdiv.cuh).
This disproves identifying that API with the one-round mathematical half
FMA. It is not a claimed violation of a PTX instruction's semantics.

**Moving a divisor to the host changes its arithmetic.** For a float32
CUDA numerator `7`, dividing by CUDA tensor `12` gives `0x3f155555`, the
correctly rounded `7/12`. Dividing by Python scalar `12.0` gives
`0x3f155556`, matching `R32(7*R32(1/12))`. The versioned CUDA division
kernel explicitly has a CPU-scalar reciprocal/multiply branch.
[PyTorch division kernel](https://github.com/pytorch/pytorch/blob/v2.12.0/aten/src/ATen/native/cuda/BinaryDivTrueKernel.cu).
A normalizer `.item()` optimization therefore needs its own registered
lowering and relation; algebraic equality of the real expressions is
insufficient.

## Dispatch and readout

With float32 CUDA inputs inside `autocast('cuda', dtype=float16)`, the
actual elementwise addition, multiplication and reduction sum tested here
remain float32; matrix multiplication produces float16. Autocast uses
operator-specific eligibility and policies.
[PyTorch 2.12 AMP documentation](https://docs.pytorch.org/docs/2.12/amp.html).
Wrapping an ordered native scalar interpreter in autocast therefore does
not establish that its SUM/PRODUCT computation used reduced precision.
The audit executes explicit half tensors as well as this dispatch probe.

The existing stored-mass/readout distinction also occurs on the real
device. Float32 masses `(1,2^-24)` have exact total `1+2^-24`. Ordered
float32 accumulation returns normalizer `1`, and the separately divided
outputs have exact sum `1+2^-24`, exceeding one. The categorical distribution
defined by the stored positive masses remains normalized by their exact
total. It differs from those raw division outputs. AMP scoring and the
bridge must retain all three objects: stored masses, rounded normalizer
and raw division outputs. This is an executed instance of the existing
readout contract, not a new probability definition.

## Coverage and authority

The audit checks every one of the 63,488 finite half encodings through raw
device transport and half-to-single-to-half conversion, including both
zero signs. It tests each adjacent finite half pair's exactly represented
single midpoint and the immediately adjacent single values, under both
signs: 190,458 conversion cases. Six further cases straddle signed overflow;
the four resulting infinities are explicitly noncertifiable.

Boundary products and seeded samples compare 11,040 finite raw results
against exact Fraction/RNE models across half/single add, multiply,
device-tensor division and `addcmul(value=1)`. The expected 528 arithmetic
overflows and 96 zero-denominator nonfinite results are separately checked.
Both minimum subnormal encodings survive the tested multiply-by-device-one
and self-addition. Neither sample correctness nor these two subnormal probes
establish all-input/all-kernel correctness or a general GPU FTZ/DAZ law.

None of the random half FMA samples caught the double-rounding difference;
the directed witness did. Random agreement is particularly weak evidence
for an unregistered lowering. A changed backend must rerun its actual
arithmetic audit and still check the executed full learner relations.

The subsequent [owned CUDA prefix](OWNED_CUDA_PREFIX.md) now retains actual
AMP parameters, delayed queues, gradient accumulators and clocks from birth
through profile and ordinary events, with registered operations, paid
evidence and joint publication. Target range, complete device resources and
installation remain open. Reference and AMP baselines/candidates still need
their own same-path fresh evidence.
These primitive outputs confer none of those authorities. The Reference/CPU
freeze and ERC-1 specification stand; model science remains HOLD.
