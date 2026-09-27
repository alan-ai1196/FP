# Modified Kneser–Ney comparison path

Status: **NATIVE WINDOWS BUILD AND SYNTHETIC CPU CONTROL PASS; NO CORPUS SCORE**.
The comparison uses the actual upstream KenLM estimator, not a replacement
counting/smoothing implementation. No experiment order, tuning policy, corpus
budget or language-quality result is selected by this component control.

## Source and local execution

The committed vcpkg manifest pins registry baseline
`07f4812200df3d3c931c0c8a6081d3b21fe2bf9f` and its
`kenlm:x64-windows-static@20230531#1` port. That port builds upstream KenLM
[`5bf7b46558e1c5595bf3b8c9b0b1f9d8d257040a`](https://github.com/kpu/kenlm/tree/5bf7b46558e1c5595bf3b8c9b0b1f9d8d257040a)
with the registry's dependency/CMake patches. The unpruned modified
Kneser–Ney estimator and unquantized trie builder both execute successfully.
KenLM's method is described by its authors in
[Scalable Modified Kneser–Ney Language Model Estimation](https://aclanthology.org/P13-2121/).

The actual machine already had Visual Studio 18, CMake and vcpkg; no WSL,
system-wide package integration or new operating environment was needed.
The build uses MSVC 19.51.36257.0 and the pinned port's Boost 1.92.0 dependencies.
Sources, packages, binaries and build logs stay under
`F:\experiment\FP_next_token_baselines`, outside the research repository.
Build concurrency was four; no GPU context or FP execution source was changed.

Reproduce with the registered Windows toolchain:

```powershell
.\scripts\build_text_ngram_baseline.ps1 -BuildRoot F:\experiment\FP_next_token_baselines
python -X utf8 -B scripts/audit_text_ngram_baseline.py --tool-root F:\experiment\FP_next_token_baselines --write
```

The manifest, C++ scorer, ingress helper and audit are canonical source.
The external build directory is only a dependency/build cache. Retain neither
compiled executables nor trained ARPA/trie files as Git research evidence.

## Causal corpus convention

The ingress writes real token ID y as the exact word `t` followed by its
decimal digits. Chunks are separated by spaces, with exactly one final
newline for the whole declared training view. EOT=50,256 is the ordinary word
`t50256`; it introduces no artificial sentence reset. The estimator adds its
own BOS/EOS once per supplied view. Those structural markers are not extra
target categories in the FP comparison.

A report begins from KenLM's BOS context at its own file boundary. It then
consumes real tokens continuously, without resetting at EOT or buffering
boundaries, and never scores an artificial EOS at the end. An order-n model
uses at most n-1 previous mapped symbols; the scorer rejects a model whose
order exceeds the registered maximum context. This states its actual
information use rather than claiming equality with a longer-context model.
There is no learner update during reporting.

The model's actual vocabulary strings are enumerated and decoded as canonical
token-ID spellings. Structural symbols stay distinct; duplicate, foreign or
out-of-alphabet spellings refuse. The real IDs do not rely on inferring
membership from a successful word-hash lookup.

## Proper probabilities over the entire target alphabet

Let A be the real IDs seen in the trained model, U=V-|A|, and q_h(w) the weight
given by KenLM's actual stored log10 score for word w at the current state h.
Define

    Z_h = sum_(y in A) q_h(t_y) + 1[U>0] q_h(<unk>),

    p_h(y) = q_h(t_y)/Z_h                     if y in A,
             q_h(<unk>)/(U Z_h)              otherwise.

Thus the full alphabet has total mass one. All unseen IDs share one unknown
bucket, divided uniformly; their future n-gram histories use the model's
unknown symbol. If every real ID is seen, no target category receives the
unused unknown mass. BOS and artificial EOS receive no target mass in either
case. This is an explicit conditional distribution on the common alphabet,
not the library's unadjusted sentence score.

The scorer evaluates every distinct required column before reading the next
target, then computes the normalizer with float64 log-sum-exp and compensated
summation. It does not assume that rounded KenLM scores sum exactly to one or
replace Z_h by one minus a structural-symbol probability. A full-V lookup table
maps every possible real label to its pre-target column. The subsequent state
advance checks that the selected model score matches that same forecast.

This correct direct implementation costs O(T (|A|+1[U>0])) model score queries
for T reporting targets, plus the finite n-gram state transitions. Its cost
must be measured for the chosen corpus; no throughput advantage is claimed.
Keep this direct normalization cost separate from the underlying model-query
cost. A later inference-speed comparison requires a competitive baseline
evaluation path; this correctness control must not manufacture an FP advantage
by making the n-gram scorer unnecessarily slow.
KenLM stores/accumulates log scores in float32, while the adapter normalizes
those actual scores in float64. This is a numerical baseline, not an exact
FP enclosure, a Runtime bridge or a population certificate.

## Evidence and stopping point

The executable control trains the upstream order-3 estimator on 10,080
deterministic synthetic tokens, using its automatic modified Kneser–Ney
discounts, interpolation and no pruning or discount fallback. It builds the
unquantized trie and checks its reporter against an independent ARPA parser
and float64 backoff calculation:

- 1,248 complete-label probability comparisons, including an alphabet with
  unseen IDs and one where every real ID was seen.
- Maximum log-probability difference 2.8989346e-7 nats, within the declared
  1e-5 tolerance for KenLM's float32 backoff accumulation.
- Eight current/future suffix mutations, a fresh-file context, three
  input-chunk sizes, ordinary EOT encoding and normalized target losses.
- The full 50,257-label map with 50,177 unseen IDs; changing the number of
  unseen IDs produces exactly the expected aggregate log-loss shift within
  float64 tolerance. Unknown probability is not duplicated per real ID.
- Four malformed report refusals, including insufficient context and an
  attempt to emit oversized diagnostic rows.

Only the small aggregate evidence file
`evidence/minimal/FP_TEXT_NGRAM_BASELINE_CPU.json` is retained. Synthetic
training/report files, scores and trained models are temporary. No actual
experiment corpus, validation/test file or GPU is opened by the audit.

This closes the adapter/toolchain control. The real text preregistration must
still choose and tune a competitive order/configuration, fix training and
reporting views and exposure policy, and measure complete process/time/storage
costs. Order 3 here is a synthetic control, not a selected experimental baseline.
No further smoothing or normalization catalog is a prerequisite.
