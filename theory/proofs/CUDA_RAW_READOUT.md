# Complete raw CUDA observation through an owned host workspace

Status: **IMPLEMENTED; WORD-PRESERVATION ARGUMENT; BOUNDED CUDA AUDITS**.
This changes transport of existing phase observations. It changes no native
arithmetic, learner, source interface, fresh-evidence rule or installation
action. It does add a retained host workspace and a larger declared work fee;
resource feasibility is therefore not asserted to be identical.

## 1. The observed cost and the proposed change

A passive 20-second sample of the first `86083a0` n8 worker contains 20
`raw_tensor`/`raw_trace` stacks among 65 successfully read stacks, with 34
nonblocking read errors. The [minimal diagnostic](../../evidence/minimal/FP_LIKELIHOOD_PASSIVE_STACK_SAMPLE.json)
retains worker identity and the sampling command. These counts motivate a
transport experiment; they are not proportions of whole-job time. The
[profiler's nonblocking mode](https://github.com/benfred/py-spy#how-can-i-avoid-pausing-the-python-program)
does not pause the target and can return partial/error samples because its
reads are non-atomic. No execution source or model registration was changed.

Previously each retained floating intermediate issued its own device-to-host
copy during finite checks and raw trace capture. `CudaWorkspace.raw_words`
instead copies the contiguous byte span covering all requested phase views
into a prepaid host bytearray, then decodes only those views. Each call makes
a fresh copy. All original device extents and operation records remain.

## 2. Exact observation and information preservation

Fix an admitted owned phase on the registered serialized CUDA stream, with
initialized contiguous binary16/32 views and the target's little-endian word
encoding. `_region_for` verifies actual arena storage identity, declared
dtype and extent, and rejects lazy negative/conjugate or foreign views.
The readout additionally requires each region to belong to this phase.

For a view at byte offset o with n elements of width w, its unsigned word i
is the little-endian interpretation of bytes `[o+iw,o+(i+1)w)`. Copying the
same bytes as uint8 and interpreting that exact slice returns the same word.
This is a bit identity, including signed zero, subnormals, infinities and NaN
payloads; no floating conversion occurs. Ordered, repeated, empty and valid
subviews preserve their old tuple order. Every finite check still tests every
recorded floating word. The retained trace keeps operation, width and words.

The CPU tensor borrows the actual bytearray through
[`torch.frombuffer`](https://docs.pytorch.org/docs/2.12/generated/torch.frombuffer.html).
Its memory is shared and its reference keeps that buffer alive. The copy uses
the same uint8 dtype and `non_blocking=False` before CPU decoding, following
the registered [copy semantics](https://docs.pytorch.org/docs/2.12/generated/torch.Tensor.copy_.html).
No new GPU allocation, numerical kernel, reference endpoint injection or
pinned-memory pool is introduced by this transport.

Padding and any intervening temporary bytes are transported opaquely: the
decoder never interprets them as values. The CPU tensor clears its written
prefix in `finally`, after immutable word tuples are computed and also if
copy/decoding raises. Starting from zero, the reusable workspace is therefore
zero at successful and handled-failure public cuts. GPU records and extents
are not cleared. Private padding has no legal numeric-source interface;
the optimization creates none. This is not a proof that arbitrary physical
memory can be erased or that asynchronous/concurrent access is supported.

The method can observe a closed failed phase for diagnostics. It never clears
arena failure, advances a cursor or signs authority. Default-stream checks,
predecessor immutability, reference/AMP relations, owned evidence frames and
all persistence/install guards continue to govern an accepted phase. A new
readout cannot reuse an old successful finite check after device mutation.

## 3. Capacity, complete lifetime and work

Let C be the registered per-phase output-cell allowance. For each actual
allocation with n elements and width w <= 4, including integer/bool
temporaries, the arena reserves

`max(8, 8*ceil(w*n/8)) <= 8*max(1,n)` bytes.

`CudaArithmetic._empty` charges `max(1,n)` cells before allocating, including
zero-sized tensors and those temporary types. Allocations of one phase are
contiguous. Excluding its eight-byte identity header, their total span is at
most 8C. The requested floating views lie within this span, so their minimum
covering byte interval fits one 8C-byte host buffer. Empty-only captures need
no copy. A helper call outside this bound fails unresolved before copying.

Runtime allocates this zero-initialized extent before CUDA binding as one
`cuda_raw_readout_workspace` ledger object, with `reference_payload_bytes=8C`
and `physical_objects=1`. Binding prepays its initialization work. It stays
resident for the Runtime lifetime and appears in complete snapshots. It is
not freed merely when a phase returns: an exception traceback can retain a
borrowed CPU tensor alias. The retained owner covers that alias as well.

There are at most six full captures per admitted endpoint: an unencoded
simplex commit checks its two positive normalizers, proposal, final update,
outer prefix and retained trace. Other current nonempty endpoints use at most
three. The first draft's three-capture allowance missed this simplex branch
and was corrected before commitment. Runtime adds a declared `6*32C` work fee
for complete readback/decoding/clearing and extent checks, changing the phase
coefficient from 128C to 320C while retaining other work charges. This is the
registered abstract work model, not a bound on CPU instructions, wall time or
all Python heap bytes. Actual job, ledger, arena and frame limits still apply.

If both old and new executions admit their required resources, the same
device computation yields identical raw operation words and finite verdicts.
The new fee and persistent workspace can change which resource budgets admit
a run. There is no dominance claim over every old resource configuration.

## 4. Adversarial and complete-endpoint evidence

Run `python -B scripts/audit_cuda_readout.py --write`. The
[minimal audit](../../evidence/minimal/FP_CUDA_READOUT_AUDIT.json) retains three
jobs attached before execution, each capped at 4 GiB and 120 seconds:

* All 65,536 binary16 patterns and 526 special/random binary32 patterns
  agree with the previous scalar observer. Seven ordered/repeated/subview/
  empty rows and nine ownership/extent/buffer refusals pass. Poisoned padding
  does not alter logical words; poisoned host bytes cannot fake the device.
  A finite value changed to infinity is caught on the next fresh read, and
  the old detached record stays unchanged. GPU allocation counters do not
  move during the captures.
* The actual owned Runtime has four zero-workspace public cuts, including
  an injected exception immediately after a successful host copy. Its
  traceback retains an alias to the still-paid 32,768-byte buffer. The buffer
  is cleared, Runtime halts at cursor 1 and the failed phase stays failed.
  Six prior CUDA phases pass independent replay.
* An actual unencoded simplex stream seals, with six posterior forecasts
  and 19 CUDA/binary64 phases independently checked. Instrumentation counts
  13 phases with three captures and six commits with six captures. The
  conservative six-pass fee thus covers the previously missed branch.

An ABBA microbenchmark observes the same 8,192 scalar views. A full capture
uses 8,192 scalar copies versus one bulk copy. The two scalar trials take
0.237/0.269 seconds and the bulk trials 0.022/0.035 seconds. These are shared-
machine fixture measurements, not model speed or GPU throughput claims.

The [complete-endpoint regression record](../../evidence/minimal/FP_CUDA_READOUT_REGRESSION.json)
retains the full CUDA Runtime audit, all 13 installation cases and a bounded
likelihood profile/install. The Runtime audit includes 64 complete binary
three-event streams and 1,024 independently replayed CUDA stream phases.
Installation includes continuation after two installs and byte/work refusals.
The likelihood job seals at 46 and installs at 22, with 286 phases per path,
94 commit tapes and 40 fresh scores. These are development regressions for
this change, not a rerun of the old complete baseline release.

All four completed n8 model workers ran at `86083a0` before this change.
Their results cannot be attributed to bulk observation or slotted metadata.
No n16 model recovery or larger-scale execution has been established.
