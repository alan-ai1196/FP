# Owned carry-free histogram construction

Status (2026-09-23): **IMPLEMENTED; SCOPED CPU AND ALL19 ACTUAL RUNTIME
CUDA A1 JOBS PASS** atd600dba. Full indexed release remains separate.

The [carry-free theorem](PACKED_COUNT_HISTOGRAM.md) proves exact coefficients
and the coefficient-normalized AMP law. This implementation supplies paid
table construction inside ReferenceCompilerRuntime. It adds no native
action, state quotient, information interface, Gamma/U or Foundation/ERC-1 rule.

## Exact execution class

Register `PackedHistogramAllowance` in the existing
`ConstructionContract.indexed_histogram` and the identical allowance in
`IndexedCudaPrefixContract.histogram`. Trusted dispatch selects either the
preceding Gray enumeration or this fixed natural-order elimination. There
is no external engine/plan/result registration port. Order search and the
projected physical schedule cannot be combined with this class.

The allowance declares join cells J, live cells C, arithmetic A, span S and
integer bits I. Defaults are4096/32768/2000000/396/32768. Implementation
maxima are32768 cells/bits,2000000 operations,S1983; the native descriptor
admits2<=n<=1024. Each call requires H=sum|d_e|<=S and

```
max(n(H+1), 16H+8n+1024) <= min(I, reference_integer_bits).
```

The complete natural-order geometry must fit J/C/A. All preflights precede
workspace mutation or numerical table entry. Failure is UNRESOLVED in this
execution class, never native inadmissibility or all-decoder impossibility.
Dense n16 still refuses its width allowance. Complete counts, pending
query/actual target, clocks, native cache/gradient interpretation, profiles
and event history remain. Passive ReferenceView supports pending states.
No call issues CERTIFIED_COMPLETE or searches a constructor decision class.

## Constructive storage upper bound

For w=ceil(min(I,n(S+1))/8), c=ceil(n/8), the actual prepaid extent is

```
W_bytes = (C+2)w + 2(S+1)c.
```

It contains C wide table cells, two separately funded packed roots and two
coefficient arrays. Every coefficient is below2^n; every current wide value
has at most beta=n(H+1) bits. Preflight implies these values fit their cells.
This is a sufficient storage construction, not an all-implementation lower bound.

**Compaction lemma.** Let old tables occupy a prefix of A0 cells. Build the
joined table of size j at A0 and its reduction of size j/2 immediately after
it. The existing planner charges A0+j+j/2. Retain old tables in increasing
source order and append the reduction. Copy each, in increasing cell order,
to the next free prefix position. Only discarded tables/joins were removed,
so every destination start is <= its source start and its end <= its source
end. Thus neither overlapping self-copies nor copies of later tables can
destroy an unread coordinate. Induction reestablishes a contiguous prefix.
The final join uses the existing A0+2^|kept| bound. Therefore one buffer
realizes the old peak table-cell bound, plus the two paid root cells.

At most(n-1)C cells move. Descriptors contain only scope/start/length; every
table value comes from the actual extent. Roots are unpacked into the paid
coefficient arrays before immutable plan terms are read back. Clearing uses
at most4096 temporary zero bytes. No assignment traversal or tuple of wide
table values is constructed. Runtime holds a private permanent memoryview;
releasing borrowed views cannot resize the paid backing, even in later
calls. Snapshots copy scratch bytes; accepted terms do not alias it.

Python operands, conversions, scope metadata and immutable plans remain
host allocations. W_bytes is not a total-heap claim. An actual Windows job
separately bounds process commitment. With M/N multiplications/additions,
the original O(M mu(beta)+N beta) bit work receives a conservative extra
O((M+N+nC+C)w+(H+1)beta+(S+1)n), apart from metadata/index work. Fixed padding
and compaction are genuine costs. The sharp uniform n-bit digit lower bound
from the preceding proof remains distinct from this storage upper bound.

## Payment and refinement

For D=n(n-1)/2 the conservative construction tariff is

```
64(n+1)^2(D+n+1)
 +32[W_bytes+(A+nC+2(S+1)+D+16)(n+1+w)].
```

This prepays metadata, clearing, table accesses, compaction and extraction
at the declared ceiling. Exact Horner/native readout separately costs
64(H+1)+128(D+16). AMP prepays two constructions,1024(min(2^(n-1),2(S+1))+1)
and128(n+1)output_cap, besides the existing output/frame/relation charges.
These scalar/index/byte tariffs are not instruction, heap or time laws.
Underfunding may refuse a cheaper instance; it cannot imply semantic pruning.

The physical constructor reads its own complete predecessor and source
query. It executes the previously proved coefficient-normalized schedule,
uploading no reference partition or forecast. After execution it independently
reconstructs the whole plan, checking exact types and every field. Fresh
endpoints, full primitive traces, native-coordinate relations and complete
frames keep their existing checks. Observation/commit, lineage, fresh
persistence, installation and failures retain the same ownership paths.
The trusted fixed kernel and serialized public API scope is unchanged;
arbitrary replacement of the checker is not sandboxed.

Machine: `packed-indexed-carry-free-histogram-reference-payload-v1`.
Reference arithmetic: `indexed-literal-count-carry-free-histogram-reference-v1`.
Work: `prepaid-contiguous-carry-free-histogram-v1`.
Forward: `packed-count-coefficient-normalized-histogram-rne16-rne32-v1`;
this deliberately matches the audited numerical component's arithmetic.

## Evidence and actual gate

`scripts/audit_owned_packed_histogram.py --write` passes, retaining
`FP_OWNED_PACKED_HISTOGRAM_CPU.json`. Independent world coefficients and
prototype RNE words match759 states/11919 queries:744462 prediction outputs/
178611 half. Every physical coefficient field, including unused cells, is
checked. Sixteen larger/range fixtures reach n256. Literal native comparisons
cover388 owned histories/776 phase triples, profiles and fresh reference
evidence; the four-event n256/profile continuation also passes. Funding and
span/bit/table refusals preserve predecessors/information. Four resizes are
blocked; ten plan alterations, seven endpoint flips,46 operation flips,
two trace extents and a short output cap are refused. Legacy Gray native,
closure, funding, workspace, adversarial and n256 reference checks pass.

`scripts/audit_owned_packed_histogram_cuda.py` registers19 fresh jobs, each
4 GiB/900 seconds, a32-MiB arena/64-MiB allocator cap,65536 phase outputs
and original1/100 state,1/1000 probability tolerances. Frames are256 KiB
through n32 and4 MiB for n256. Its allowance uses C1024/A16384 and otherwise
defaults; n3/n32/n256 scratch sizes are153668/1632464/4227904 bytes. Cases
cover profiles, fresh/install, closure, funding, partial commit failure,
retired producers, word/plan/target faults, buffer lifetime,104-event
underflow reversal, n256 profiles and an actually learned n32 signed band.
Legacy global/projected n256 and Gray profiles are controls. Readers check
every successful integration phase, with independent world or vertex-prefix
coefficient oracles and prototype RNE traces. Commit inputs before launch;
stop on failure and retain every attempt without changing caps. This gate
does not establish a larger-model score or a complete indexed release.

## Actual A1 outcome

All19 registered jobs pass atd600dba with fixed source and caps, exiting
zero without timeout or limit termination. Peak whole-job commitment is
2394722304 bytes under4 GiB. The24487-byte
`evidence/minimal/FP_OWNED_PACKED_HISTOGRAM_CUDA_A1.json` retains every job,
its source/process/limit binding and compact checked result. All jobs are
terminal; do not repeat them unchanged.

The ten integration flows check861 complete phases,78945 primitive words
and26163 half words. Of these, seven new carry-free flows check735 phases,
34623 primitive words/9933 half and37030 outputs including copies;241
prediction readers compare independent coefficients and prototype RNE.
Seven additional probes read36 full records. Fresh evidence crosses at20,
installation retains alpha1/2 and learning continues to21. Six actual buffer
calls reject12 resize attempts across reference construction, physical
construction and independent reconstruction. At cursor52 a positive native
coordinate transiently rounds to zero;52 contrary observations restore
count zero and forecast1/2 at104 without losing the native coordinate.

The n32 band is built through76 observations, retaining all496 count
positions. Its new end-to-end query has119 terms and a2464-bit envelope
for2^31 latent assignments; one more target-one observation commits, reaching
77 events/232 phases/27757 primitive words. Maximum actual compaction is3484
cells, in a1632464-byte paid extent. That last event concerns previously
unseen edge(0,31), not reversal of an earlier count on that edge. The original
journal's `continued_opposite_label` field names this target-one continuation;
the harness field is clarified afterward without changing numerical code
or repeating the terminal job.

The n256 continuation includes four ordinary and four profile events,
34 complete physical phases,449 primitive words and81 half. Its actual
4227904-byte table extent and32893 maximum compaction moves are paid.
Both existing n256 controls also pass on the same ordinary/profile tape:

| Realization | Primitive words | Half words | Consumed arena bytes |
|---|---:|---:|---:|
| Existing global | 42594 | 15924 | 341504 |
| Existing projected | 514 | 24 | 4864 |
| Carry-free histogram | 449 | 81 | 4344 |

The projected control is the stronger comparison: the new path trades
additional wide integer storage/work for modestly fewer floating outputs
on this tape and uses more half operations. These counts establish neither
overall efficiency dominance nor a throughput benchmark. The earlier Gray
profile control passes too. Actual continuation correctness is closed for
this declared component; useful larger-model evidence and full indexed
release remain separate research obligations.
