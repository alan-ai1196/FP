# Whole-schedule retention work on ordinary native text

Status (2026-10-03): **SOURCE-DERIVED BOUNDS; EXACT CPU COUNTS PASS**.
Source: production at `1e695c5`. No production change, corpus run, timing
experiment, device execution, new encoding or Foundation/ERC change occurs.
The relation/precision branch stays closed. These laws concern the actual
ordinary-text execution path, not a new static model class.

## 1. Decision and scope

The [captured-value](CAPTURED_TOKEN_VALUES.md) and
[owned-base export](OWNED_BASE_EXPORT.md) refinements remove specific storage
and traversal costs. Neither changes the complete canonical records emitted
by ordinary learning. That remaining representation has a large **cumulative
expansion** cost even if its physical archive deduplicates perfectly.

Consider T successfully completed ordinary targets of the registered single
native token incumbent, update unit B, context L and S uint32 master positions.
There is no CUDA/binary64 shadow, profile, query, graph replacement or reporting
inside this counted interval. Keep the original reference byte archive and
its complete writer/independent-decoder/expected-stream checks. Initialization,
reporting, failed prefixes and other work are additional.

Let C=floor(T/B), r=T mod B. Let Q be the number of commits whose master bytes
change, so 0<=Q<=C. The ordinary schedule creates exactly

    N = 5T + C + Q

archive pages: ingress identity, revealed context, pre-target prediction,
after-observation trace and current learner state per target, an additional
committed trace per commit, and a changed range-evidence page when needed.
The target's reserved mutable wire is written through the existing paid
buffer rather than becoming another archive page. Program retention adds
a lease to the already constructed object.

All assertions about a completed T are conditional on successful execution.
They do not assert that the numerical or resource machine can reach T.

## 2. Exact repeated-origin and pending-window laws

Use j=0,...,B-1 for the pending count before an ordinary target. The canonical
encoder serializes dataclass fields and all repeated occurrences. It does not
replace aliased record wrappers by graph pointers. A source image may replace
how a subtree's bytes are generated, but emits its **entire** encoding again.

| Retained value | Origin occurrences | Windows inside TokenState.windows |
|---|---:|---:|
| Pre-target tuple: learner, prediction.before, prediction.probabilities | 3 | 2j |
| After-observation trace | 4 | 3j+1 |
| Current learner payload | 1 | j+1, or zero at commit |
| Additional committed trace, at j=B-1 | 5 | 3B-2 |

The context/ingress and range records contribute neither selected coordinate.
Thus the exact total number of origin occurrences is

    O(T,B) = 8T + 5C.

Summing the table over whole units and the unfinished suffix gives the exact
number of windows *inside pending-state tuples*:

    W(T,B) = C(3B^2+B-2) + 3r^2-r.

This deliberately excludes standalone prediction/source windows and origins'
source fields. Identical Python identities are still distinct **occurrences**
in this serialization tree. This count is not a count of live heap objects.

Every origin contains exactly 4S master bytes. Their hexadecimal payload
alone occupies 8S canonical bytes, independently of their numerical values,
sharing, sparsity or whether the latest update changed them. Let A be the exact
canonical size of the fixed base tuple. A pending window's L nonnegative
integer labels use at least 20L bytes: each integer occupies at least nineteen
bytes, and tuple syntax/separators supply the remainder. These three sets of
byte positions are disjoint. Consequently the complete ordinary record volume D
satisfies

    D >= O(T,B)(8S+A) + 20L W(T,B).

All other definitions, node results, targets, names, clocks, metadata, syntax,
source windows and range evidence increase D. For fixed record expansion cap H,
successful retention also gives the conservative upper

    D <= H(5T+2C).

This upper is conditional on completing the schedule, not a feasibility
certificate. It leaves the actual compression, metadata and host constraints
undecided. The selected lower contains both Theta(TS) master repetition and
Theta(TBL) pending-window repetition when whole units are completed.

## 3. Original million-target consequences

For T=1,048,576, B=L=512, S=603,092 and V=50,257, the fixed uniform base has
A=1,407,207 canonical bytes. The laws give:

| Selected quantity | Exact count |
|---|---:|
| Optimizer commits | 2,048 |
| Origin occurrences | 8,398,848 |
| Pending-window occurrences | 1,611,657,216 |
| Repeated master hexadecimal bytes | 40,522,224,304,128 |
| Repeated base-tuple bytes | 11,818,917,697,536 |
| Pending-window byte lower | 16,503,369,891,840 |
| **Complete record-byte lower D** | **68,844,511,893,504** |

The lower is about **68.84 decimal TB / 62.614 TiB** for training alone. The
128-MiB per-record cap supplies the loose conditional upper 640.5 TiB.

Each successful byte-archive retention passes all D bytes through three
separate complete streams: producer input, independent reader output and the
owner's independently generated expected bytes. The selected three-stream
volume is therefore at least **206,533,535,680,512 bytes**. These are logical
stream byte counts, **not** a claim about distinct DRAM reads, bus traffic or
simultaneous residency. The reader's 8,192-byte piece bound further requires
at least **8,403,871,081** decoded piece occurrences.

Completion in 7,200 seconds would require more than 9.56 GB/s of complete
record volume in each stream, before initialization, numerical learning,
metadata, other canonical fields, reporting or any final audit. This is a
necessary average throughput, **not a proved machine throughput ceiling or
wall-time impossibility**. Historical timings are not substituted into it.

For comparison, the same successfully completed trajectory has at most C+1
native origins, whose distinct master-byte payload totals at most
4S(C+1)=4,942,942,032 bytes. That selected sharing upper is not the whole host:
archives, images, windows, indices, resource events and transients are additional.
The former 112-GiB eager-input exclusion no longer applies to captured values;
this cumulative work bound is not a replacement host-memory exclusion.

## 4. The existing expression path has a different unresolved cost

The [compositional theorem](COMPOSITIONAL_COMPLETE_RETENTION.md) already proves
that complete recovery need not re-expand old immutable bytes at each native
binding. It refutes interpreting section 3 as an FP semantic lower bound.
But its current owned realization at this source executes

    bindings = dict(self.bindings)
    pages = self.pages + [page_id]

on every successful publication. The second expression copies exactly p old
page references on publication p. Across M pages, this is **M(M-1)/2**, even
when every encoded literal is already known. An initial prefix only increases
the ordinary suffix's count. Since N>=5T+C, the original training schedule
alone would copy at least **13,754,632,240,128 old page slots**, or
**110,037,057,921,024 bytes of pointer slots** on a 64-bit host. This is again
cumulative copy volume, not resident bytes or elapsed time. Copying bindings
is additional; even retaining just one distinct ID per revealed observation
forces at least T(T-1)/2 copied entries across a completed schedule.

There is also an immediate **capacity exclusion** for simply carrying over
the old actual expression comparison's 2^20 source-binding cap. The immutable
full text manifest contains 1,048,576 distinct training-ID strings plus 16,384
distinct reporting-ID strings. `Walk.value` binds each individual source before
binding its containing tuple. Thus these leaves alone require **1,064,960**
entries, already exceeding that cap by 16,384; other fields and tuples add more.
An earlier node/page refusal cannot rescue this inequality. This is a
counterfactual mismatch between that existing cap and the full declaration,
not a claim that the old sixteen-target experiment used the larger declaration
or failed its own registration. No full constructor is replayed to prove it.

Increasing the cap alone does not remove either publication-copy law. The
old actual AMP comparison remains a slower, terminal observation in its
original scope; no native speedup or new codec configuration is inferred.

## 5. Evidence and research consequence

`audit_native_retention_volume.py` checks all 93 binary histories of lengths
zero through four at units one/two/four: 294 targets, 158 commits, 1,774 pages
and 12,434,083 bytes in **each** of the three actual streams. It checks the
formula at every completed prefix. Fifteen complete observed/unobserved state
pairs agree. Hooks count the real producer packets, reader yields and expected
fragments; they do not replace operands or accept a header as a count oracle.

The unchanged full text declaration with two synthetic labels gives ten pages,
sixteen origins, ten pending windows and 103,924,417 bytes in each stream;
the selected lower is 99,813,488. The page payload is only 1,289,224 bytes,
demonstrating directly why compressed residency is a different quantity.
Canonical images are active and every live buffer/role total is checked.
The full-horizon numbers above come from the source formulas, not multiplying
this short prefix. Evidence: `FP_NATIVE_RETENTION_VOLUME.json`.

`audit_compositional_publication_work.py` observes the unchanged expression
owner through eight targets/four commits. Its 53 total pages copy exactly
1,378 prior page slots and 12,456 binding entries; complete state agrees with
an unobserved control. Ten exact tuple controls check the source-binding
threshold: n distinct strings require n+1 entries including their tuple, and
all admitted pages independently recover their complete canonical bytes.
Evidence: `FP_COMPOSITIONAL_PUBLICATION_WORK.json`.

**Decision:** retain the complete state and keep the trained ordinary-text
comparison as the target. Whole-host and wall-time feasibility remain
UNRESOLVED; neither a small copy refinement nor enabling the existing
expression option establishes them. The next solver intervention must account
jointly for repeated record expansion, source traversal, dictionary/binding
growth and publication work, using the existing compositional theorem as an
available principle. No new architecture action or static precision theorem
is required. Do not launch another full attempt or reopen an old codec timing
journal on the strength of a selected payload/count saving alone.

The subsequent [typed value-graph construction](OWNED_VALUE_GRAPH_RETENTION.md)
addresses these coordinates jointly in a passive model: complete typed fields,
captured operands, independent source binding and prefix publication. Its exact
wire/guard laws and original full-declaration control do not install an archive
or establish a full-run budget. The source-stability premise and actual host/
index/memo costs remain explicit prerequisites to an owned realization.
