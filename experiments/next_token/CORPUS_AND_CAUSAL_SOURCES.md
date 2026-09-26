# Ordinary-text data entry and causal sources

Status (2026-09-26): **TRAIN/VALIDATION FILE IDENTITY AND PASSIVE CAUSAL
SOURCE AUDIT PASS; NO NEW MODEL SCORE OR OWNED RUNTIME REGISTRATION**.

## 1. Reuse a verified text asset instead of reducing the task prematurely

The inspected historical FP data directory contains180 million training and
2 million validation GPT-2 token IDs from FineWeb-Edu `sample-10BT`. The
recorded public source is revision
`87f09149ef4734204d70ed1d046ddc9ca3f2b8f9`, which remains available from the
[publisher](https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu/tree/87f09149ef4734204d70ed1d046ddc9ca3f2b8f9).
This changes the provisional WikiText-2/byte direction: the existing ordinary
text and full50,257-token alphabet are now the preferred study substrate.
No smaller vocabulary or prefix has been selected to help FP pass.

The canonical audit is
[FP_NEXT_TOKEN_DATA_ENTRY.json](../../evidence/minimal/FP_NEXT_TOKEN_DATA_ENTRY.json)
(2,211 bytes). It independently scans every training/validation token,
checks both complete file digests against the fixed historical manifests,
and records the exact local data location. No corpus is copied into Git.

| File | Tokens | Bytes | Observed ID range | EOT occurrences |
|---|---:|---:|---|---:|
| train.bin | 180,000,000 | 360,000,000 | 0..50,256 | 173,858 |
| val.bin | 2,000,000 | 4,000,000 | 0..50,256 | 1,900 |

Both files are little-endian uint16 and end without EOT. Their last
documents were truncated to the declared token quota; do not silently
append EOT, remove the partial document or reinterpret it as a full one.
Token50,256 is EOT. This tokenization is an explicit fixed data coordinate,
not a pretrained feature extractor or a new FP architecture operation.

### Provenance actually checked

The file identities match both the original pilot's recorded train/validation
identities and the inherited Trial1R manifest. The inspected pilot recipe
and config use `row.text`, key `id` with URL/text-digest fallback, SHA256 of
the UTF-8 key, the first eight digest bytes interpreted little-endian, and
remainder modulo10000. Buckets0..9799 go to training,9800..9899 to validation,
and9900..9999 to the historical pilot test. Nonempty documents are tokenized
with `gpt2.encode_ordinary`, followed by EOT; the last selected document is
truncated to each file's quota. The pilot manifest records200,381 nonempty
source rows scanned. The audit does not import or execute that historical
package, whose data module itself imports Torch.

File identity is verified. Reconstructing every raw public row and checking
content duplicates across different document IDs has **not** been performed.
The source/split recipe is provenance from the inspected preparation code,
not a new proof of document/content independence or a stochastic stream law.
The historical validation set is a development asset with prior exposure.
The pilot and confirmation test files were not opened, hashed, sampled or
scored in this entry audit. A new model protocol must state its evaluation
and test policy before model selection; historical test results or the
existence of a confirmation file cannot supply fresh evidence for this study.
Historical neural scores/checkpoints are not reused as new baselines.

## 2. A fixed indexed lag/token interface

For vocabulary size V, context bound L and a forecast of token x_t, declare
all atoms

    a_(lag,v)(t) = 1[z_(t,lag) = v],
    1 <= lag <= L, 0 <= v <= V,
    z_(t,lag) = x_(t-lag) if lag <= t, otherwise PAD=V.

PAD is not a predicted label and is distinct from token0 and EOT. Lag1 is
the most recent token. EOT remains part of the observed sequence: there is
no hidden reset and context may cross a document delimiter. No context
crosses a train/validation file boundary. Position0 has only PAD atoms.
The same boundary convention must apply to every compared learner.

**Causality lemma.** If two token tapes agree at every index below t, their
complete atom families at t are equal, regardless of the current target
and all later tokens. Each non-padding lookup has index t-lag<t; all other
values are the same declared PAD. Any fixed native positive program of
these atoms therefore has the same forward value when its complete learner
state is the same. This statement is about forward source dependence, not
about parameters trained on different histories.

**Exact indexing.** A tuple of L token/PAD IDs determines every one of the
L(V+1) declared binary source values, and each lag's unique unit atom
determines its ID. This is an exact coordinate encoding, not a marginal
summary. At V=50,257,L=512 the source family contains25,732,096 atoms; its
passive reader need not allocate that many one-hot scalars. Query, encoding,
history and ownership costs still need explicit funding in the eventual
Runtime. This does not declare older context irrelevant to language, erase
the corpus, or permit discarding Compiler/optimizer histories. L is an
experimental information restriction, not a theorem about sufficient text
memory. A different information class needs its own claim.

The [passive reader](causal_tokens.py) keeps the schema, position and all
L entries, validates exact IDs/padding, and answers only declared atom
indices. It issues no observation, freshness, installation or execution
token. A caller can construct a passive data object; that does not prove its
causal origin. Binding actual tape position and sources to an owned model
execution remains a separate required integration step.

## 3. Exact evidence and immediate implication

The audit exhausts243 five-token histories over a three-token alphabet and
context lengths1,2,3:4,374 windows and34,992 exact atom comparisons. For3,645
nonterminal windows it changes every current/future token and obtains the
same complete source point. Invalid history IDs, boolean/fractional indices,
missing-history impersonation and malformed padding refuse.

For each actual file, seven selected positions include the beginning,
context-length boundary, first EOT and its successor, and the final target.
Contexts1,32,512 give3,815 exact lag checks per file. Full scans verify token
ranges and file identities. These selected real positions supplement the
causality proof; they are not exhaustive over every real window.

Reproduce with:

    python -X utf8 -B scripts/audit_next_token_data_entry.py --data-root F:\experiment\FP_Scaling_Trial_1R_RTX3090_WindowsGlobal_OneClick\data --write

No Torch or model loss is involved. The next obstacle is a useful native
learner and its complete executable state/update under this full alphabet.
Do not turn this data success into a model, Compiler, AMP or split-independence
certificate. The next work must derive/test G/Gamma/U, including all output
masses and gradients, with competitive fresh baselines and measured costs.
