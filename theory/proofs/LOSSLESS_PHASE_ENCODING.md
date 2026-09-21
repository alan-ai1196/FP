# Lossless complete phase encoding and its resource boundary

Status: proved byte reconstruction on the declared typed domain; CPU and
the scoped actual A1 matrix pass. Writer-input alias counterexamples in
both CPU and actual CUDA invalidate unqualified evidence/execution
binding. Both actual probes are terminal at ba48cb3. This record-taking
Runtime codec is now retired; the passive grammar and byte law remain.
The [byte-only replacement](BYTE_ONLY_PHASE_EVIDENCE.md) has exact CPU
evidence and a passing scoped actual gate at b53889e. Integration statements
below describe the original source-bound implementation and experiments.
Foundation R4, ERC-1, native learning and numerical
tolerances are unchanged. This is a physical representation, with an
explicit contract identity and work tariff, not a new architecture action.

## 1. The obstruction being removed

The [query-order resource law](QUERY_ORDER_RESOURCE_FRONTIER.md) proves
that the existing typed JSON plan representation requires uniform frames
whose accumulated payload exceeds the 8-GiB packed cap on every n16 tape,
even with ideal order selection. Its 65-byte binary-node lower bound is
specific to that encoding. It does not prove an information lower bound
of 65 bytes per node or an impossibility for every resource-bounded solver.

The new representation retains every field of the existing typed record:
full counts and clocks, sources and explicit identities, reference values,
raw operation and endpoint words, gradients, execution plans and power
tags, lineage, status and reason. No statistic or selection of those fields
replaces the complete record. No old frame is migrated or rewritten.

## 2. Fixed grammar and left inverse

The registered identity is
`typed-phase-varints-interned-strings-short-sequences-v1`.
`phase_encoding.py` admits the same supported typed value kinds used by
the existing record encoder, subject to the explicit finite limits below.
For dataclasses the domain uses the registered constructors and their
ordered declared fields. It is a data codec, not an arbitrary Python object
identity or reflection sandbox. Mapping subclasses already have the old
encoder's common `mapping` representation.

Unsigned integers use minimal seven-bit continuation varints. Signed
integers map x>=0 to 2x and x<0 to -2x-1. The byte tags are:

| Tag | Payload |
|---|---|
| 00, 01, 02 | None, false, true respectively |
| 03 | Signed integer varint |
| 04 | Signed numerator and positive denominator varints, reduced fraction |
| 05 | UTF-8/surrogatepass byte length and first exact string definition |
| 06 | Index of an earlier string definition |
| 07 | Mapping pair count, then keys and values in the old canonical key order |
| 08 | Module, qualified name, field count, ordered field names and values |
| 09, 0A | Tuple or list length at least sixteen, then elements |
| 20--2F, 30--3F | Tuple or list of length zero through fifteen |

Other tags, nonminimal varints/sequence headers, invalid references, repeated
definitions, malformed UTF-8, noncanonical fractions, truncated data and
trailing bytes are refused. Strings are interned by exact code-point
equality; an astral code point and an explicit surrogate pair stay distinct.
None, booleans, integers, fractions, strings, tuples and lists stay distinct.

Let J(v) be the complete old typed packed byte stream, E(v) the new stream,
and D the independent streaming decoder. For every admitted v,

    D(E(v)) = J(v).

Proof: tags distinguish the primitive and container kinds. Minimal varints
and the signed map invert their integer payloads exactly; canonical
fractions retain both exact integers. Each first string definition inverts
surrogatepass UTF-8, and a reference returns that same code-point string.
Its old JSON escaping is reconstructed independently, including DEL and
lone surrogates. Containers retain lengths and order, and dataclasses retain
the old module/name/field schema. Induction over the finite tree gives the
equality. The reader checks end-of-input, so a suffix cannot be ignored.

Consequently different old typed byte records cannot acquire the same new
encoding. The decoder reconstructs bytes and never imports a class, creates
a learner, or grants execution authority. An arbitrary syntactically valid
stream need not be a valid native state: Runtime independently compares
its decoded bytes with its entire expected record before acceptance.

This is an information-preservation theorem, not equality of raw physical
snapshots or resource-constrained continuations between two machines. The
new codec declaration and physical bytes are observable and its decoding
cost is paid. No cost-free decoding or whole-Compiler history quotient is
claimed.

## 3. An indexed-record byte upper bound

Consider scalar indexed prediction records satisfying all these premises:

- At most 128 distinct strings in the full record.
- N<=262144 tape nodes, each a registered constant, factor, addition or
  multiplication node; all integer operands are in [0,262144).
- One boolean power tag per node.
- Each operation row has a string tag, width 16 or 32, and one word of
  that width. The number of rows is at most C and below 2^21.

A string reference costs two bytes. A tagged node index costs at most four
bytes. A binary node plus its power flag therefore costs at most
1+2+4+4+1=12 bytes; constants and factors cost no more. A scalar operation
row costs at most 1+2+2+1+6=12 bytes, including its one-word tuple and full
32-bit unsigned word represented as a signed integer.

Define a metadata skeleton by replacing only `execution_plan.nodes`,
`execution_plan.power_tags` and `raw_operations` with empty tuples. Let M
be its independently encoded size, and let D_s be the sum of full string
definition sizes for every distinct tag string in the removed nodes/rows.
Set B=M+D_s+9. The nine bytes cover the increase from three empty sequence
headers to at most four-byte headers. Removing earlier string definitions
can only increase the remaining metadata cost: references are two bytes
and every definition is at least two bytes, while all reference indices
still fit one varint byte. Charging all removed tag definitions again is
conservative. Thus

    |E(record)| <= 12(N + C) + B.

At the existing N cap 262144 and C cap 65536, the linear part is 3,932,160
bytes. Therefore B<=262136 is sufficient for the payload and its eight-byte
length header to fit a 4-MiB frame. This is a conditional upper bound; it
does not discard the metadata term or assert that every arbitrary FP
record satisfies those integer, string and shape premises.

The exact passive fixtures give:

| n16 case/cursor | N | C | Old bytes | Encoded bytes | B |
|---|---:|---:|---:|---:|---:|
| c2/16, 366 | 210817 | 61478 | 23255926 | 2966634 | 4781 |
| c2/17, 328 | 207353 | 61478 | 22997299 | 2943076 | 4607 |
| c4/18, 276 | 246407 | 65574 | 26693458 | 3417988 | 4509 |
| c4/19, 297 | 224753 | 40998 | 22661585 | 2913532 | 4507 |

These are full CPU RNE records for passive output-minimizing orders from
the order audit, with independent full-byte equality, not records executed
by the current natural-order Runtime. The third output count still exceeds
the existing cap; a fitting representation does not authorize its execution.
The optimized orders remain unpaid passive witnesses.

## 4. Ownership, work and refusal semantics

`CudaPrefixContract.evidence_encoding` selects either this fixed codec or
the explicit legacy identity `typed-reference-json-v4`. The default remains
legacy. The new contract adds `+prepaid-lossless-phase-expansion-v1` to the
work identity, leaving the backend and numerical forward identities intact.

The fixed limits are 128 MiB of expanded legacy data, depth 64, 4096 string
definitions, and 32768 bits per integer coordinate. An initial type/size
guard runs before the legacy size traversal. Over-limit values return a
resource refusal; the grammar and numerical relation are not weakened.
The guard counts aggregate character/integer lengths over all occurrences,
including repeated strings and dataclass schema names. A limit on each
individual string would not bound the subsequent total traversal. The
decoder also checks a raw string's length against its remaining expansion
allowance before copying or decoding it.

For each phase, before admission encoding or numerical execution, Runtime
charges its existing work plus 32*128 MiB +16*F primitive work units. This
is a declared conservative traversal/byte tariff, including both admission
and final retention, string-table operations and padding inspection. As in
the registered primitive model, integer/dictionary primitives are not CPU
cycles or a bit-complexity assertion. It is not a complete Python heap or
wall-time bound. Bounded host jobs still independently constrain actual
allocation and time, including transient strings, sort keys and decoding.

The complete F-byte frame is allocated and paid first. Runtime measures
the full record, invokes the writer through a live fixed-size memoryview,
checks the exact returned extent and its integer types, independently
decodes/compares every legacy byte, checks header preservation and all
reserved padding, then writes the used length. The live view prevents
ordinary helper resizing from introducing an unowned bytearray tail. The
view is released before the existing paid immutable finalization. Only
after retention and finalization succeed can the numerical owner accept
the phase. The tested byte/type/extent faults cannot authorize publication
when the expected input stays fixed. Section 7 shows why this premise is
not established by the current helper interface.

Failed mutable frames and actually received context/targets remain owned;
they do not certify a successful phase. A final retention refusal may
leave an admission record or partial bytes rather than a sealed final
record. Only successfully finalized frames receive the full-record
decoding assertion. All padding remains paid: using fewer bytes inside
the same F-byte frame does not lower its retained residency. Existing
snapshots continue to share prior immutable frames without mutation.

## 5. Evidence and the actual CUDA matrix

`FP_PHASE_ENCODING_CPU.json` retains 3195 typed round trips, eleven malformed
stream refusals, five resource/prewrite refusals, all 19216 single-bit
substitutions and 2402 truncations of a complete small phase, plus the four
complete records above. `FP_PHASE_ENCODING_BOUND_CPU.json` independently
measures the metadata skeletons and checks the upper bound.
`FP_PHASE_RETENTION_CPU.json` exercises the real Runtime retention hook:
two seals with old-snapshot preservation, ten resource refusals and six
writer faults. Its numerical owner is explicitly mocked; it supplies no
CUDA, complete-learner or installation authority.

`FP_PHASE_ENCODING_REGRESSION_CPU.json` also checks both aggregate-length
preflight refusals, the decoder's pre-copy limit, the current primitive
and retention suites, and the unchanged 270-prediction/540-observation
exact RNE bridge. The 33-frame storage component audit passes with
constructor, snapshot and sealer bound unchanged from pre-codec e8fa568.
The older storage script's b0c409c constructor predicate already fails
because of intervening indexed/prospective extensions; that failed old
predicate is retained explicitly, with no altered claim about its original
experiment or anchor.

Before the first actual execution, `scripts/run_phase_encoding.py` fixes
seventeen fresh Windows jobs, each attached before its first instruction:

- Matched legacy/binary recurrent generic profiles, including independent
  exact rounded execution and checked binary64 phases.
- Matched indexed profiles; projected profiles; indexed n256 execution
  with literal world builders disabled; projected fresh persistence,
  installation and subsequent learning.
- Existing independent endpoint, full-plan and foreign-plan adversaries
  under the new encoding.
- Five actual post-execution writer faults: prediction payload, observation
  header/padding, prediction extent and attempted resizing. Published
  learner advances must remain zero; target receipt must remain truthful.
- Matched global legacy/binary execution of exposed n16/c2 seed16 using
  the original indexed model worker, full independent posterior and
  retained strong exact/AMP-readout controls. All original A1 failures
  remain intact. A failed stream gets no complete-domain score.

Ordinary fixtures have 4-GiB/900-second jobs. Both generic profile contracts
receive a 10^14 work allowance; indexed fixtures already use it. The model
pair keeps the original 16-GiB/7200-second job, 8-GiB packed cap, 4-MiB
uniform frame, 65536 outputs, 256-MiB arena, 512-MiB allocator cap and 10^15
work per role. Only codec identity and its work tariff differ in each pair.
No arithmetic, order, data, tolerance, frame or node/table cap changes.

Every sealed actual record is independently reconstructed and compared in
the child, including full padding and owned extents. The model reader also
checks native transitions, RNE traces, posterior equality and any complete
score. The parent compares common evaluation words between the two model
prefixes. Every attempt, timeout, resource refusal and unexpected failure
is retained in a new `FP_PHASE_ENCODING_CUDA_A*.json` journal; failures
are never silently restarted. HEAD and all execution dependencies remain
fixed while jobs run.

`FP_PHASE_ENCODING_CUDA_A1.json` is terminal at 3d3711e. All fifteen
integration/fault fixtures pass. The two matched n16 jobs remain unresolved:

| Global n16/c2/16 | Legacy | Typed binary |
|---|---:|---:|
| Committed cursor | 173 | 194 |
| Successful CUDA phases | 520 | 583 |
| Checked floating words | 111781 | 457450 |
| Largest retained payload | 2146715 | 1013847 |
| Largest reconstructed old record | 2146715 | 7860141 |
| Packed peak | 2192098799 | 2457162057 |
| Host job peak | 4660322304 | 5309132800 |

Legacy reproduces its original phase-frame refusal at query(3,7). Binary
continues for 21 additional ordinary events, then the reference decoder
refuses the 8192-cell natural-order join at query(6,9), before a new CUDA
phase. Both retain all120 counts and leave the next target unrevealed.
All367 published reference forecasts match the independent posterior;
the33 common evaluation word rows are identical. Neither gets a complete
model score. The larger retained prefix increases packed residency; these
different endpoints do not establish isolated memory or runtime savings.

Across all17 jobs,1498 sealed complete records pass full byte/padding
comparison; six failed mutable frames remain owned. Every job exits zero
without timeout or limit termination, and all jobs are terminal. Maximum
host commitment is5309132800 bytes. The generic matched pair has44 checked
phases each, the indexed pair58; fresh installation and subsequent learning
pass. This is the registered fault class, not a proof against input mutation.

## 6. Attack the need for a custom format

The conventional baseline `zlib.compress(payload,6)` reconstructs every
original byte in all four passive fixtures. No compressed bodies are
retained. `FP_PHASE_COMPRESSION_CPU_A1.json` records the initial inline
CPU audit at3d3711e; `audit_phase_encoding.py --compression` reproduces its
steps and observations. These are byte measurements, not Runtime or
bounded-workspace compression evidence.

| Case | Typed binary | zlib of old typed JSON | zlib of typed binary |
|---|---:|---:|---:|
| c2/16 | 2966634 | 971929 | 525029 |
| c2/17 | 2943076 | 964910 | 511098 |
| c4/18 | 3417988 | 1127439 | 600355 |
| c4/19 | 2913532 | 1034033 | 551688 |

Thus the custom format is not needed to fit these observed records. Its
constructive upper bound remains valid, but claiming it is the best
practical encoding would be unsupported. A simpler standard compressor
is a serious alternative, subject to a paid and bound Runtime interface.

## 7. Fixed-input invertibility does not prove execution binding

The independent decoder can be correct while its expected value has changed.
Runtime passes the same phase object to `codec.write` and later `codec.check`.
An injected writer changes only that supplied object and then invokes the
honest writer. No owner globals or external inputs are modified. Two CPU
witnesses preserve both encoded and expanded lengths and every padding byte:

- Decrement the phase output count by one, leaving its actual execution
  plan and raw operation words unchanged.
- After count(1,2)=1, query(0,1), change the plan's count address from2 to0
  while retaining its declared support(1,2), readout and operation words.

In the real retention hook both records seal and reach its mocked numerical
owner's accept callback. Their decoded bytes match the mutated record and
differ from the record before the writer. The second retained plan fails
an independent operation replay. `FP_PHASE_WRITER_ALIAS_CPU.json` supplies
this narrow evidence; it does not establish actual CUDA publication.

`scripts/audit_phase_writer_binding.py` registers two fresh4-GiB/900-second
actual probes, one per witness, with production unchanged from3d3711e.
They retain actual publication status, immutable frame equality, plan/raw
word mismatch, target nonreceipt and native learner state. Each attempt
gets a new `FP_PHASE_WRITER_ALIAS_CUDA_A*.json`; no silent retry is allowed.
`FP_PHASE_WRITER_ALIAS_CUDA_A1.json` is terminal at ba48cb3, with production
unchanged from3d3711e. Both actual probes publish `PREDICTED_REFERENCE` and
seal `CHECKED_CUDA_PREFIX_PHASE` despite their false metadata:

| Actual witness | Executed input/result | Retained checked record |
|---|---|---|
| n3, query(0,1), cursor0 | 58 output cells in the plan | 57 output cells |
| n3 after(1,2,0), query(0,1), cursor1 | Support(1,2), count address2 | Same support, count address0 |

Both keep the raw readout/operation words, encoded/expanded lengths and
padding unchanged. The latter retained plan fails independent replay of
the actual operation trace. No target is revealed and neither native
learner advances. Both jobs exit zero without timeout or limit termination,
below4 GiB; maximum job commitment is2191769600 bytes. No numerical point
probability error, class-completeness certificate or installation failure
is alleged: the falsified claim is the local executed phase's output/plan
conformance. This is an implementation information-interface mismatch,
not a counterexample to the byte theorem or a new semantic action.

The repair must bind the input before delegation and prevent helper access
to mutable authority. Repeating the same check against the same alias does
not establish that boundary. Immutable canonical bytes plus a standard
compressor are now implemented in the [byte-only replacement](BYTE_ONLY_PHASE_EVIDENCE.md).
Its paid staging, work and failure retention pass CPU and scoped actual
checks at b53889e. The replacement retains its separate source-bound evidence.

The outstanding scientific question is how far a paid lossless encoding
can move the actual execution boundary. The 147 empty join/live order
classes and four output minima above the cap remain separate proved
restrictions. No all-n16 recovery, smaller whole-memory bound, new complete
release or model advantage follows from this codec theorem.
