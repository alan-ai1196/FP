# Lossless indexed token sources inside the actual Runtime

Status: **actual ReferenceCompilerRuntime source integration**. The full token
learner/AMP backend remains to be integrated. This change removes expansion
of L*(V+1) primitive source declarations/values from each live context while
preserving their complete native meaning and future query/profile access.

## Exact refinement and ownership

The closed `TokenAtomFamily(V,L,type_id)` declares the same ordered SourceSpecs
as the literal token expansion: `lag{l}/token{v}`,1<=l<=L and0<=v<=V, each of
the registered type, upper1 and availability delay l. Label V is PAD and is
distinct from token0. Canonical IDs are injective; alternate spellings and
out-of-family IDs refuse. The current realization requires its logical index
range to fit Python's container indices; exhaustion is arithmetic unresolved,
not a new constraint on abstract FP semantics.

`TokenSourceReads` can only use the Runtime's owned past targets. Its data
registration requires the identical semantic family, V output labels and
no external input coordinates. `read_sources` checks the complete revealed
history, then constructs the immutable `TokenContext(family, position, past)`.
At original source position p, its lag-l token is V if p-l<0, otherwise the
owned target at p-l. No current/future target is read. All closed metadata
fields are revalidated, including rejection of undeclared hidden fields.

For every declared atom, the scalar decoder returns

```
x[l,v] = 1[past[l-1] == v].
```

This equals the original target_atom/target_missing rules exactly. Conversely,
the unique one in each lag block recovers the retained token; the decoded
one-hot interface and the compact lag vector contain the same information.
This is an encoding of the full source family, not a numeric token-ID feature
substituted for native indicators. Program validation still checks every
referenced source ID/type, and all existing SUM/PRODUCT semantics are unchanged.

The original source position is retained with the lag vector. Runtime profile
replay and moment queries now use the closed scalar decoder on each original
record. They do not reconstruct sources from the candidate's optimizer clock
or from a later ordinary context. Ordinary observations, roles, target values,
data uses and source records remain owned and serialized by the existing
Runtime. No supplied context object is admitted through ordinary ingress;
caller-provided history coordinates fail the declared empty input interface.

The native conservative range checker uses the same independent[0,1] source
box through indexed lookups. This is sound and may be loose. It does not
claim exact categorical range optimization or a new completeness class.
Floating/CUDA and native-class-search registrations using this source encoding
are refused until their own translations are integrated; this reference-only
change cannot borrow an older physical certificate.

## Paid work and retained representation

Before constructing even the source-history tuple or lag context, Runtime
charges the indexed source read. Its reference tariff covers history copy/
continuity visits and lag decoding/validation:2*p+3*(L+1). Evaluation/profile
work adds2*(L+1) for decoder validations; queries additionally fund each
indexed-context validation actually used by their coordinate loops. These
charges describe the registered reference machine, not measured processor
cycles. The original literal-source tariffs remain unchanged.

A source context is a retained dataclass with L token integers, position and
the complete family header. The generic canonical encoder sees these fields;
it never sees an iterable mapping of all L*(V+1) atoms. Transient scalar maps
remain read-only interfaces. The ordinary packed-buffer ledger pays the
resulting bytes and object lifetime. This is not a total-Python-heap claim.

Every observation still retains its lag vector and the complete history is
still retained. Therefore this implementation uses O(TL) source-record storage
over T events, and history validation has an O(T) component. A full-corpus
execution will need a funded shared indexed tape/record representation that
preserves all original contexts and legal past-data access. The present result
removes the vocabulary factor; it does not assert end-to-end training scalability.

## Actual evidence

The [audit](../../evidence/minimal/FP_INDEXED_TOKEN_SOURCES.json) uses the real
ReferenceCompilerRuntime, with packed ownership checks at its transitions:

- All96 native four-token histories pass384 observations,288 commits and
  3,456 complete atom/type/delay comparisons. Every parameter/gradient state
  matches the separate native learner.
- Sixteen actual newborn profiles pass64 original-context events and32 next
  ordinary candidate continuations. Their original source positions and
  profile data uses are preserved.
- Two registered moment coordinates, including a source PRODUCT/target atom,
  give the identical exact quantized answer to the full literal records.
  Seventeen malformed ID/PAD/role/reader/field/index/ingress cases refuse.
- A source-work cap refuses before the history copy or decoder can run,
  retains the owned ingress failure and publishes no prediction.
- The full V=50,257,L=512 source interface processes four real training
  tokens through Runtime construction, score/observe and an owned query.
  All25,732,096 primitive sources remain decodable. Patching atom enumeration
  to fail immediately confirms that no source family expansion occurs.
  The largest packed source context is12,059 bytes.

The last case uses an explicitly supplied elementary graph with uniform
probabilities to isolate source integration. It checks the complete output
vector but is not the packed trainable token learner or a model-quality result.
Only the first8 training-file bytes are read, against the previously verified
corpus identity and unchanged file size/mtime. No validation/test data, loss,
Torch or GPU is used. Existing event and profile regression suites also pass.

The next boundary is the compact complete token learner inside this same
Runtime, with immutable parameter/prefix representation, paid execution,
reference/AMP event relations and existing lineage/install obligations. No
new semantic architecture action or Foundation/ERC change is introduced.
