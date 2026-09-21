# A byte-only boundary for complete execution evidence

Status: implemented; exact CPU checks and all 21 actual integration/fault
jobs pass at b53889e. The two matched model prefixes remain UNRESOLVED,
with their readers passing. All 23 jobs are terminal. The former record-taking codec is
retired from Runtime registration. Its byte theorem and both actual alias
counterexamples remain historical evidence. This changes a physical
information interface, not Foundation R4, native learning or ERC-1.

## 1. The missing premise was source stability

At production3d3711e, the writer received the same phase object used by the
subsequent expected-byte check. Two actual probes at ba48cb3 published false
phase conformance: 58 outputs reported as57, and count address2 replaced
by0 while retaining support(1,2). Encoded lengths, padding and actual words
stayed unchanged. See [the retained counterexamples](LOSSLESS_PHASE_ENCODING.md#7-fixed-input-invertibility-does-not-prove-execution-binding).

For a fixed input v, D(E(v))=J(v) remains correct. It says nothing about
whether v still denotes the phase produced before a helper call. Copying
only a length or repeating a comparison against the same alias does not
establish that premise.

The new boundary keeps the phase and its canonical serialization iterator
inside Runtime. A delegated encoder is constructed with no arguments and
receives only exact immutable byte strings of at most65536 bytes, followed
by a no-argument finish call. It receives no phase, native value, iterator,
frame, staging view or owner handle. Runtime alone writes the frame and
compares the decoded output with its own complete expected byte stream.

## 2. Preservation argument and exact fault class

Assume the existing serialized Runtime API, the private owner, canonical
typed serializer and independent format reader are correct. An encoder
fault may manipulate its own state, supplied byte values and returned
data, but may not inspect Python stacks, mutate owner globals, alter the
trusted reader or write arbitrary process memory. This is an explicit
component fault model, not a Python/native-code sandbox or attestation.

Let v be the checked execution record immediately before retention. In
this model the encoder receives no mutable capability reaching v; its byte
inputs cannot be modified in place. No other Runtime event interleaves.
Therefore v stays fixed throughout encoding and comparison. The owner
checks D(y)=J(v), including every byte, length, end marker and frame padding,
before the existing immutable sealer and numerical acceptance. An altered
encoding either reconstructs the whole original record, fails the check,
or exceeds a registered resource allowance. This supplies the source
stability premise missing in the old interface.

The decoder is independent of encoder state and returned metadata. It is
part of the trusted checker; the encoder cannot replace it through a
contract or output. The canonical serializer was already in the trusted
Reference machine. No new helper taking a phase object is introduced.

The decision class is **full recovery of the owned canonical execution
record from one retained compressed stream**, subject to its declared
resource limits. It is not uniqueness of the compressed bit pattern or
conformance to every internal instruction of a compressor. Deflate permits
different representations of identical expanded bytes, including irrelevant
bits within its own grammar. The actual produced bytes and external frame
padding are retained; no equality of physical histories is asserted.
The independent native/AMP operation and full-plan checks remain unchanged.

## 3. Simpler representation, explicit costs

The standard compressor is zlib, level6, method DEFLATED, window15,
memLevel8, default strategy, without a supplied dictionary. Its compile and
runtime library versions are included in the evidence encoding identity.
The current identity is
`typed-reference-json-v4-zlib-1.3.1-1.3.1-l6-w15-m8-s0-v1`.
The work identity adds `+prepaid-byte-only-phase-compression-v1`.
The legacy uncompressed encoding remains the default; the old
`typed-phase-varints-interned-strings-short-sequences-v1` registration now
refuses. Its passive encoder/decoder remain available for old evidence.

This choice is informed by the strong baseline: standard zlib of the four
old complete records uses964910--1127439 bytes, less than the custom
format's2913532--3417988. The custom format's constructive12(N+C)+B upper
bound remains valid; no such compression-ratio bound is borrowed for zlib.
An incompressible record can still return UNRESOLVED at its frame cap.

Runtime pays and allocates one65536-byte reusable staging buffer before
binding the CUDA prefix. The owner fills it from the canonical serializer
and passes immutable byte copies to the encoder. It creates no full
uncompressed record body. The whole F-byte evidence frame and padding
remain prepaid, and the existing extra F-byte copy during finalization
remains paid. The snapshot and immutable sealer implementations are
unchanged. The staging buffer is retained with its sole data-owner lease,
including after faults, and later snapshots copy its mutable bytes normally.

Each phase prepays its existing work plus32*128 MiB +16*F primitive units.
Canonical traversal first bounds aggregate character/integer lengths,
depth64 and integer widths32768 before computing the exact size. The
expanded stream is capped at128 MiB. Both encoding and independent byte
comparison are covered by this registered tariff. It is not a bound on
zlib's internal instruction count, bit time, complete Python/C heap or
wall time. Transient immutable chunks, codec C state and allocator memory
remain under the separately enforced whole-process/job limits. The paid
64-KiB buffer is an actual buffer, not a claim that total host workspace
is64 KiB. No dummy allocation is substituted for a host-memory bound.

The reader limits each decompression result to at most65536 bytes and to
the remaining expansion allowance plus one detection byte. It requires
EOF, refuses unused/trailing data and a second stream, and does not call
an unbounded decompression flush. These API properties follow the
[official Python zlib documentation](https://docs.python.org/3/library/zlib.html#decompress.decompress).
Checksums alone supply no execution identity: the owner compares all
expanded bytes against its private record.

Compressor results must be exact bytes and fit the already paid frame
before the owner copies them. No encoder receives a writable output view.
Malformed bytes or changed record content produce execution failure;
insufficient work, expansion or frame capacity produces UNRESOLVED.
The existing first-unexpected-executor-error priority is preserved.
Failed mutable frames, staging storage, raw execution records and actually
received context/targets remain owned. No false phase is accepted and no
learner advances on those failures. CPU and actual evidence are below.

## 4. Exact CPU evidence

`scripts/audit_phase_deflate.py` and `FP_PHASE_DEFLATE_CPU.json` retain:

- 23 byte round trips over1177634 bytes, including random/incompressible
  data, empty input, UTF-8/surrogatepass and block boundaries.
- 1152 single-bit variants:1150 malformed streams refused and two valid
  representations with identical expansion. This is why an all-bit-change
  rejection claim would be incorrect. All144 truncations, two trailing/
  second-stream cases and the bounded expansion bomb refuse.
- Eight input-type/lifecycle refusals, aggregate traversal admission and
  refusal of the retired record-taking codec registration.
- The actual Runtime retention hook with an explicitly mocked numerical
  owner: two successful frames with old-snapshot preservation; an additional
  329625-byte Unicode record crossing five full64-KiB blocks; ten resource
  refusals; eight byte-only faults. Changed output counts, count addresses
  and readout words refuse while the original record and plan stay intact.
- A60000-byte global cap refuses the staging allocation before any CUDA
  binding can occur. The registered allocation kinds are retained.

The existing canonical encoding audit also passes:235 packed-tree checks,
240 identity checks, all65536 BMP code points and3072 surrogate/astral
boundary classes. CPU mocks grant no CUDA or installation authority.

## 5. Actual CUDA registration

`scripts/run_phase_deflate.py` fixes23 fresh Windows jobs before execution:
matched legacy/deflate generic and indexed profiles; projected profiles;
n256 with world builders disabled; projected fresh persistence, installation
and subsequent learning; existing endpoint/full-plan/foreign-plan adversaries;
a byte-input interface witness; eight prediction encoder faults; two
observation faults; and the matched global n16/c2 seed16 model pair.

The byte faults act solely on received immutable chunks and returned data.
They alter output counts, the known count address, readout or gradient words,
attempt in-place input mutation, return a wrong type, overrun the frame,
truncate the stream or append trailing data. An independent numerical/plan
reader must still validate the original actual record after each refusal.
Prediction targets stay unrevealed; observation targets remain received.
Native learners and published CUDA predecessors must not advance.

Ordinary fixtures use4-GiB/900-second jobs. Both generic controls have10^14
work; indexed fixtures already use it. The model pair keeps16-GiB/7200-second
jobs,8-GiB packed caps,4-MiB frames,65536 outputs,256-MiB arenas,512-MiB
allocator caps and10^15 work per role. Only evidence/work identity and
the compressed path's paid staging differ. Native learners, data, schedules,
tolerances and table/tape/output caps remain fixed. The original complete
posterior/AMP-readout controls and all previous refusals remain retained.

The existing substantive event, phase, RNE, lineage, frame, fresh-evidence,
installation and model readers are reused. The parent compares common
model readouts; incomplete prefixes receive no complete-domain score.
Every job, timeout and refusal goes into a new
`FP_PHASE_DEFLATE_CUDA_A*.json`. All inputs must be committed and HEAD and
execution dependencies stay fixed while jobs run. Unexpected failures stop
the matrix and remain evidence. No all-n16 completion, whole-resource
dominance, new full release or model superiority is claimed by registration.

## 6. Actual RTX 3090 outcomes

`FP_PHASE_DEFLATE_CUDA_A1.json` retains all 23 terminal fresh jobs at
`b53889eb2ae8e6410b935588fd4f0248fdc4754e`. All 21 integration/fault fixtures
pass. Both model readers validate unresolved prefixes. Every job was
attached before its first instruction, exited zero and stayed below its
registered cap without timeout or limit termination. Maximum job commitment
is 5,235,593,216 bytes. There are 1,513 independently checked complete sealed
frames and 11 retained failed mutable frames, including the legacy model's
frame refusal.

Both matched generic profiles check 44 phases, and both indexed profiles
check 58. Projected profiles, n256, projected fresh persistence/installation
and subsequent learning pass. All preceding endpoint, complete-plan and
foreign-plan adversaries still refuse. The direct interface fixture observes
12 immutable chunks while two ordinary events commit; its seven phases and
130 actual floating words pass the independent reader.

Every byte-only attack refuses before publication. Wrong output counts,
the count address2-to0 substitution, changed readout/gradient words, attempted
input mutation, wrong return type, truncation and trailing data retain
EXECUTION_FAILED phases. An over-cap result returns UNRESOLVED. The actual
original phase still passes full numerical and plan replay after each
attack. Failed frames retain all 262,144 owned bytes. Prediction targets
remain unrevealed; both observation targets remain0. Published learners,
cursors and current CUDA predecessors do not advance.

The matched n16/c2 seed16 model pair gives:

| Measure | Legacy | Byte-only zlib |
|---|---:|---:|
| Committed events / independent reference checks | 173 | 194 |
| Checked complete CUDA phases | 520 | 583 |
| Retained used payload bytes | 26,735,925 | 5,295,557 |
| Reconstructed old typed bytes | 26,735,925 | 121,016,192 |
| Largest used payload | 2,146,715 | 337,710 |
| Largest old typed record | 2,146,715 | 7,860,141 |
| Packed peak | 2,192,098,799 | 2,457,227,597 |
| Whole-job peak | 4,659,236,864 | 5,235,593,216 |

Legacy reproduces its frame refusal at cursor173/query(3,7). The compressed
path reaches cursor194/query(6,9), then refuses the unchanged reference
natural-order join allowance before another CUDA phase. Both next targets
remain unrevealed and all120 global counts remain. All367 published native
forecasts match the independent full posterior, and the33 common evaluation
readout rows agree exactly. The compressed prefix also matches all54
evaluation readouts and every numerical audit aggregate of the historical
typed-codec prefix at3d3711e: 457,450 floating words, 55,212 half words,
69,909 maximum tape nodes and25,390 maximum phase outputs.

This closes the observed mutable-writer mismatch in the declared component
fault class. It does not finish either model or certify a new full Runtime
release. Uniform4-MiB frames and padding still dominate packed retention;
smaller used payloads are not smaller complete frames. Different reached
prefixes and source-bound fixture timings do not establish isolated memory
or speed dominance. The next obstacle is a paid solver and its complete
numerical/ownership bridge under the unchanged native learner.
