# Sparse Delta Memory: Scaling the State of Linear RNNs through Sparsity

## Identity and actual coverage

- Loïc Cabannes, Pierre-Emmanuel Mazaré, Ilze Amanda Auzina, Théo Le Pendeven, Gergely Szilvasy, Matthijs Douze, Maria Lomeli, Justin Carpentier, Gabriel Synnaeve and Hervé Jégou. [arXiv:2607.07386v2](https://arxiv.org/abs/2607.07386v2), revised November 16, 2026, 16:40:29 UTC; v1 was July 8. The PDF title block is dated November 17. [Versioned PDF](https://arxiv.org/pdf/2607.07386v2) and [complete TeX source](https://arxiv.org/src/2607.07386v2). The title is authenticated in the [official NeurIPS 2026 event list](https://neurips.cc/Downloads/2026); a distinct final proceedings PDF was not matched. The full-reading badge belongs to this 33-page arXiv edition.
- **Pro-B full reading, November 26, 2026:** all 33 pages; main §§1–8; Appendices A–J, including the v2 multi-factor Appendix C; all equations, 16 figures, 16 tables and 47 printed bibliography entries. The complete substantive TeX body and appendices were read, and all actual figure pages were visually inspected. Table annotations and source build flags were checked. There are no numbered theorem/proof or algorithm environments and no numbered body footnotes. Cited papers do not inherit a reading badge.
- PDF SHA-256: `4a6f399a32f503172abf5c4cc3746cfa0392fad34e26d8f366c8e4530cfc2d70`. Ignored PDF, source, extracted text, renders and bounded algebra support: `literature/corpus/arxiv_frontier/2607.07386v2/`.
- Bounded independent checks cover the state-size algebra, product-key selection argument, slotwise decay and triangular-system timing, and the limits of the capacity interpretation. They found no substantive local algebraic error in those constructions. This is not a capacity theorem certification, formal proof or numerical reproduction. No training, GPU benchmark or author's test suite was run.
- The official Meta release was pinned to [c1afb4d9e11ace11eca197080fb3504863d32096](https://github.com/facebookresearch/sparse-delta-memory/tree/c1afb4d9e11ace11eca197080fb3504863d32096), October 24, 2026, version 2.0.0, preceding manuscript v2. A source assistant inspected the relevant layer, cache, kernel, configuration and benchmark paths; Pro-B directly rechecked the principal allocation/update/cache paths, README and benchmark conditions. This is scoped static inspection, not a full audit of 215 tracked files. Support is ignored under `literature/corpus/pisf_prior_art/CABANNES-2026-SPARSE-DELTA-MEMORY/`.

## What the construction changes

SDM separates **the number of persistent scalar entries** from **the number touched by one token**. It keeps an explicit, large recurrent table and uses product keys to select a small number of its rows for a gated delta update. The table is not a sparse dictionary of only visited rows. Its dimensions are chosen before training and the entire bank is physically allocated in the inspected implementation.

The global mixer is evaluated inside a hybrid network with three sliding-window attention layers for each global layer. The local window is 128 tokens. The global alternatives are full attention, Mamba2, Gated DeltaNet (GDN) and SDM; they share the local components. Thus the comparisons do not establish the behavior of a standalone SDM-only language model. [§§1–4]

The principal architectural result is constructive: a large table can receive input-dependent, error-correcting updates with a fixed sparse access budget, and its within-chunk dependencies can be handled by a triangular system. The paper does not prove an information-capacity or predictive-state lower bound. Its use of “capacity” is primarily a count of memory entries plus measured task performance.

## Addresses, updates and readout

For one head, let the live memory be \(M_t\in\mathbb R^{N\times d_v}\). From the current layer input \(x_t\), separate learned projections produce write scores \(k'_t\) and read scores \(q'_t\). In the two-factor construction, each projected vector has dimension \(2\sqrt N\) and is split in half. The score for slot \((a,b)\) is the sum of the corresponding factor scores:

\[
s^w_t(a,b)=k'_{1,t}[a]+k'_{2,t}[b],\qquad
s^r_t(a,b)=q'_{1,t}[a]+q'_{2,t}[b].
\]

Top-\(W\) write scores select \(I_t^w\); independently, top-\(R\) read scores select \(I_t^r\). The default configuration applies softmax **within each selected set**, producing sparse vectors \(k_t,q_t\in\mathbb R^N\). Read and write supports need not coincide. The forget and input gates are separate per-head scalars, not the address selector. [§3.1, §4]

Only selected write rows decay:

\[
\widetilde M_t[i]=\alpha_tM_{t-1}[i],\quad i\in I_t^w,
\qquad
\widetilde v_t=\sum_{i\in I_t^w}k_t[i]\widetilde M_t[i].
\]

The update and output are

\[
M_t[i]=\widetilde M_t[i]+\beta_t k_t[i](v_t-\widetilde v_t),
\quad i\in I_t^w,
\]

\[
M_t[i]=M_{t-1}[i]\quad(i\notin I_t^w),
\qquad
y_t=\sum_{i\in I_t^r}q_t[i]M_t[i].
\]

The paper uses \(\alpha_t=\exp[-A\,\operatorname{softplus}(W_\alpha x_t+b_{dt})]\) and \(\beta_t=\sigma(W_\beta x_t)\). The read is **after the current token's write**. The retrieved vector then receives per-head LayerNorm, a separate sigmoid output gate and an output projection. LayerNorm acts on the retrieved output, not on every stored row. [Eqs. 3–6, Figure 9]

A useful equivalent bookkeeping form, directly obtained from these equations, is

\[
D_t=I+(\alpha_t-1)\operatorname{diag}(\mathbf1_{I_t^w}),
\qquad
M_t=(I-\beta_tk_tk_t^\top)D_tM_{t-1}+\beta_tk_tv_t^\top.
\]

This exposes both the unchanged complement and the state-dependent residual subtraction. Conditional on the supplied per-token keys, values and gates, the memory recurrence is affine. The model as a whole is still a learned nonlinear network. The subtraction predicts an internal value embedding from the selected rows; it is not itself a future-observation sufficiency theorem.

Selecting every row recovers the gated delta recurrence with the same weights. The full GDN architecture also has its own key normalization and 1D convolutions. Appendix C's dense-limit measurement explicitly switches to \(\ell_2\)-normalized keys/queries and does not claim that merely selecting every slot under the default softmax makes the entire SDM model identical to GDN.

### Learned initialization

SDM normally learns \(M_0\) during pretraining and makes a private mutable copy for each sequence. It therefore combines parametric storage with context-dependent storage in the same bank. A null-initialized variant is tested. Learning \(M_0\) does not add token-update FLOPs to the same architecture, but adds trainable scalar values, initialization/copy work and parameter/optimizer storage. The distinction matters to every “same parameters” comparison below. [§3.1, Table 3]

## The resource comparison is deliberately narrower than total storage

The main comparisons keep the query/key and value projection dimensions at

\[
d_{qk}^{\rm total}=d/2,\qquad d_v^{\rm total}=d.
\]

GDN uses head dimensions \(d_{qk}=64,d_v=128\). SDM uses \(W=R=64\). Its principal read/write work scales as

\[
O\bigl(H(W+R)d_v\bigr)=O\bigl((W+R)d_v^{\rm total}\bigr),
\]

whereas GDN touches the full dense state of each head. These principal FLOPs are matched up to the detailed constant factors and a small additional selector cost. The two-factor main-text accounting estimates PKM top-k below 1% of the layer's FLOPs. It does not establish a below-1% latency contribution for arbitrary numbers of heads or factors. Address projections, top-k, interaction construction, full-bank initialization and HBM traffic remain real costs. [§3.2, Appendix C.3]

For the two-factor addressing and fixed total projection dimensions,

\[
M_{\rm size}
=H\left(\frac{d_{qk}^{\rm total}}{2H}\right)^2
       \frac{d_v^{\rm total}}H
=\frac{(d_{qk}^{\rm total})^2d_v^{\rm total}}{4H^2}.
\]

This is a count of scalar entries per layer. Fewer heads increase it quadratically under that constraint. With the chosen widths, unrestrained expansion would grow as \(d^3\), so the head count is also a memory-budget control. The formula is not a claim that the represented table can be stored using only its low-dimensional addressing parameters. [§3.3]

| Main ladder configuration | Listed model parameters | Pretraining tokens | GDN live-state entries, all global layers | SDM live-state entries, all global layers |
|---|---:|---:|---:|---:|
| L08, width 1920, 21 layers | 1.48B | 168.4B | 614k | 553M |
| L13, width 3840, 38 layers | 8.14B | 1.141T | 2.2M | 7.963B |

**Table 1 explicitly excludes the SDM memory state from “Params.”** Since the default \(M_0\) is learned, including it gives approximately 2.03B and 16.10B trainable scalar values for these rounded rows. This is simple addition of the reported counts, not a measured memory figure. Live banks, the shared learned initial parameter, gradients, optimizer state, snapshots and attention caches have different lifetimes and precision. No total-memory equivalence follows from the headline parameter comparison.

The budget is approximately 160 training tokens per nonembedding backbone parameter, chosen to resemble heavily trained deployed models rather than Chinchilla-optimal training. All main models pretrain on length 8192. The 1.4B and 8B models then receive respectively 4B and 16B tokens of 128k-context fine-tuning. These additional stages belong to the short/long-context evaluation protocol. [§4]

## How the training algorithm preserves the recurrence

Appendix B splits a sequence into chunks of size \(C\). The first phase can process every chunk in parallel because addresses, gates and values are available before the memory recurrence. It does **not** replace the within-chunk residuals by independent writes from a frozen memory.

For each slot \(s\), the cumulative log-decay at position \(t\) is

\[
\lambda_s(t)=\sum_{u\le t:\ s\in I_u^w}\log\alpha_u,
\]

with the sum restricted to the current chunk. A slot does not decay at steps that do not write it. The strictly lower-triangular write interaction matrix is

\[
G[i,j]=\sum_{s\in I_i^w\cap I_j^w}
 k_i[s]k_j[s]\exp(\lambda_s(i)-\lambda_s(j)),\qquad j<i.
\]

The read/write matrix instead uses \(q_i\), the read set of token \(i\), and includes \(j=i\). That diagonal implements the token's own write before its read. The interaction is nonzero only on overlapping selected slots; sparsity here is a property of routed supports, not a promise that learned supports are almost disjoint. [Appendix B.1–B.2]

Set

\[
M_{\rm sys}=I+\operatorname{diag}(\beta)G,
\quad
\Delta V_{\rm const}=M_{\rm sys}^{-1}\operatorname{diag}(\beta)V,
\quad
B=-M_{\rm sys}^{-1}\operatorname{diag}(\beta).
\]

The unit lower-triangular solve resolves within-chunk delta feedback. During the sequential chunk phase, reads from the incoming bank produce `retrieved` and the inter-chunk output. The full residual rows are

\[
\Delta V=\Delta V_{\rm const}+B\,\mathrm{retrieved},
\qquad
y=\mathrm{inter}+\operatorname{tril}(QK)\Delta V.
\]

Each row of \(\Delta V\) already contains \(\beta_t(v_t-\widetilde v_t)\). The chunk endpoint is then written to the bank. Thus only chunk boundaries remain sequential; the solve retains the exact algebraic recurrence within each chunk. The bounded source check found the strict/inclusive causal masks and slotwise decay consistent. No numerical correctness test of every CUDA specialization was performed.

This differs from the immediately preceding [E²-TTT reading](ZHONG-2026-E2-TTT.md): E²-TTT preserves scalar update timing after freezing gradients and uses chunk-start readouts; SDM's special affine delta form allows a triangular solve that retains within-chunk residual dependence and updated readouts. Neither observation is a general theorem that all test-time learners admit the same parallelization.

### Backward storage and quantization

The paper applies sparse updates in place, saves touched-row information and undoes writes during backward. Its memory-checkpoint accounting changes from

\[
O((T/C)Nd_v)\quad\text{to}\quad O(Nd_v+TWd_v).
\]

The example is 226GB to 8GB for the state-checkpoint component of one 8B-model SDM layer at length 16,384, \(C=128,W=64\). This is not the whole training peak. At 128k, even touched-row snapshots can be expensive. The authors test fp8/int4 snapshots and say the approximate recovery appears not to harm training loss or final performance. No error bound or exact-gradient guarantee accompanies that option. The released code quantizes recovery snapshots, not the live recurrent bank itself. [Appendix B.3]

## What the main experiments establish

| Post-fine-tuning metric | 1.4B GDN | 1.4B SDM | 1.4B FullAttn | 8B GDN | 8B SDM | 8B FullAttn |
|---|---:|---:|---:|---:|---:|---:|
| Validation text NLL | 2.683 | 2.654 | 2.660 | 2.298 | 2.253 | 2.285 |
| Average of 15 short-context tasks, % | 37.93 | 38.51 | 37.98 | 55.70 | 56.84 | 56.65 |
| RULER, 13 tasks averaged across 4k–131k, % | 20.1 | 31.4 | 32.6 | 34.3 | 50.3 | 61.3 |

SDM is the strongest fixed-state option in these comparisons and has slightly better average short-task accuracy than full attention. Full attention retains the higher overall RULER average. In particular, 8B SDM multikey2 is 4.7% against 58.0%, and multikey3 is 1.2% against 29.8%. Length-averaged RULER must not be described as success at the longest evaluated length. [Table 2, Figures 12–13]

SDM improves over GDN on 11 of 15 short tasks at both sizes; there are real regressions. For example, its 8B BoolQ is 67.13 versus 74.98. Appendix D notes that BoolQ improves on only 40% of adjacent pretraining evaluations and is monotone in none of 24 ladder runs. This is a useful stability diagnostic, not a seed-level uncertainty interval showing the post-fine-tuning deficit is insignificant. The broad task tables do not report a multi-seed error bar for every cell.

Figure 3 fits loss–FLOPs scaling from the smaller ladder levels, with SDM \(R^2=.999\), and tests the larger 8B point. These are empirical scaling fits, with a bootstrap band discussed for GDN, not asymptotic architecture laws. The sparse learned memory is excluded from the matching parameter count.

### Initialization and memory-size controls

| L08 initialization ablation | State entries | Code NLL | Short-task accuracy, % | RULER, % |
|---|---:|---:|---:|---:|
| GDN, null \(M_0\) | 0.6M | .849 | 37.9 | 20.1 |
| GDN, learned \(M_0\) | 0.6M | .850 | 38.0 | 20.6 |
| SDM, null \(M_0\) | 553M | .845 | 37.3 | 28.0 |
| SDM, learned \(M_0\) | 553M | .822 | 38.5 | 31.4 |

The null-initialized SDM result supports a long-context advantage independent of the extra pretrained content in \(M_0\). It does not support the stronger claim that all gains are independent of learned initialization: null SDM has lower short-task accuracy than GDN. Figures 4–5 also show improved code perplexity with larger context, but 1M-token code evaluation is not a 1M-token exact-retrieval guarantee.

The L06 state-size ablation changes the product-key projection dimension, hence the number of slots, while keeping \(W,R,d_v\) and all non-SDM layers fixed. SDM state 42M→170M→679M gives code NLL .947→.937→.914 and RULER 20.2→20.7→21.5, versus GDN's 16.0. Address projection parameters/compute also change, so this is not a pure storage-only intervention with every other resource constant. Short-task accuracy 33.7→33.6→34.6 is not monotone. [Table 3]

### Access behavior is learned, but the probes have a scope

The selected-key entropy analysis uses one held-out coding batch: the first eight eligible documents truncated to 8192 tokens, pooled over tokens, heads and layers. Writes are more concentrated than reads: top 32 of 64 write weights carry about 85% of selected mass, whereas top 64 of 128 reads carry about 77%. Effective-key utilization is \(\exp(H(p))/k\), describing concentration over the selected budget, not the fraction of the entire bank visited. [Figures 7–8, Appendix G.2]

The distinct training-time utilization plot pools approximately 21M tokens per point over ten steps and averages five SDM layers. It reaches approximately 100% distinct read-slot coverage and 28→42% write-slot coverage. Those are aggregate access statistics. They do not imply every sequence uses the full bank or that the unvisited portion has been proved semantically useful. No load-balancing auxiliary loss is used for the paper's addressing. [Figure 15]

Table 13 separately changes \(W\) and \(R\). More reads give the best training NLL in one configuration, but \(W=R=64\) gives the best reported RULER average. The table uses only six RULER subtasks and proportions rather than percentages, with pretraining only. Its .4176 is not directly comparable to the 13-task post-training 31.4% in Table 2.

## Multi-factor keys: more addresses, restricted scores and a measurable cost

Appendix C replaces two factors with \(F\) factors of sizes \(n_1,\ldots,n_F\). A head has

\[
d_{qk}=\sum_f n_f,\qquad N=\prod_f n_f,
\qquad s(c_1,\ldots,c_F)=\sum_f k'_f[c_f].
\]

For fixed sum and number of factors, balanced integer sizes maximize the product, and AM–GM gives \(N\le(d_{qk}/F)^F\). Conversely, balanced factors address \(N\) slots with approximately \(F N^{1/F}\) score columns. This expands the addressable **physical table**, with the score family restricted to additive factors. It does not realize arbitrary independent scores over all \(N\) slots and does not reduce storage of their independently mutable values. [C.1]

### Exact selection and its precision condition

Top-\(k\) of an outer sum can be recovered from top-\(k\) of its operands. Merge factors sequentially, retaining at most \(k\) scored tuples. If the two candidate lists are decreasing, the pair of zero-based ranks \((i,j)\) can be discarded whenever \((i+1)(j+1)>k\): at least \(k\) other rank pairs have scores no smaller. Thus only

\[
\sum_{a=1}^k\lfloor k/a\rfloor\le k(1+\log k)
\]

candidates are needed per merge, 280 rather than 4096 at \(k=64\). The paper's selection accounting is \(O(d_{qk}\log k+Fk\log k)\), in addition to the projection cost \(O(dd_{qk})\). The bounded argument check supports it. Exact ties allow an arbitrary valid top-\(k\) set; they do not give a unique index list. [C.2]

For more than two factors and bf16 input, the reported kernel rounds partial sums in the specified factor order. Its exactness is relative to that rounded scoring computation. It is not exact real-arithmetic summation or a guarantee of invariance to reordering factors. The release further documents different two-factor tie selections between its previous and current versions. These are precision/interface conditions, not evidence that the product-key selection principle is wrong.

### The controls fix different resources

| Controlled comparison, 1.4B | Resource held fixed | Main result | Remaining change |
|---|---|---|---|
| 2 heads/2 factors → 16 heads/4 factors, Table 5 | 110.6M entries/layer; total value width and sparse read/write FLOPs | 1M-target PPL 2.073→2.011; SLPL@128k 7.03→4.91; NIAH 36.3→40.9 | Key columns 960→992; headwise selection/interactions and latency change |
| 16 heads, 2 factors `[31,31]` → 4 factors `[15,16,16,15]`, Table 6 | 992 key columns, heads, value width, sparse access budget | 1M PPL 2.174→2.011; NIAH 27.2→40.9 | State 1.8M→110.6M/layer; learned \(M_0\) excluded from matched parameters |
| 16 heads, 2/4/8 factors, Table 7 | 57,600 slots/head and 110.6M entries/layer | Wider 2-factor model has lowest PPL and highest NIAH; 4 factors has lower listed 32k/128k SLPL | Key columns 7680/992/512, hence very different address parameters |

The last comparison prevents the simplistic conclusion that more factors are always better. Four factors are a useful efficiency tradeoff; reducing address dimensions further can harm quality and increase selector time.

The evaluation protocols also differ. Tables 5–7 PPL use the last 1024 tokens of the first \(2^{20}\) tokens of 2305 code documents, varying the preceding context. The 1M case starts with BOS; smaller windows do not. SLPL selects tokens using Llama-3.1-8B: full-context log probability above −2 and gain above two nats over a 4096-token sliding window retaining BOS. It measures key tokens in position bin \((T/2,T]\), not the same target slice as PPL. The ordinary position-PPL entries of Table 4 use yet another stated interval protocol. These measures should not be interchanged. [C.3, Metrics]

Table 4's 1.4B two-factor baseline comes from the separate sweep, with RULER 29.0 rather than the main table's 31.4. Its 4-factor value is 35.5. At 8B, the comparison is four-head/two-factor state 1.99B versus thirty-head/four-factor state 2.26B, **not** the main two-head SDM with 7.963B entries. RULER rises 53.9→56.7, but average short-task accuracy falls 56.21→56.01. These paired runs share their data and schedules; the GDN comparator is imported from the earlier recipe. Tables 8–9 explicitly use separate initialization/training code, so their absolute values are only compared within the stated experiment. Their 32k NIAH averages cannot be merged with the cross-length Table 5 NIAH. Tables 5–7 average eight needle tasks over 4k–128k; Table 4 instead averages all thirteen RULER tasks.

### Fixed read/write FLOPs do not fix layer time

Table 10 measures one SDM layer's forward and backward on **GB300**, bf16, \(4\times8192\) tokens, chunk128, CUDA-graph replay. It reports medians of three processes, twenty steps each, differing by at most .3%.

| Constant-state configuration | Total layer, ms | Selection, ms | Selection share |
|---|---:|---:|---:|
| 2 heads, 2 factors | 28.9 | .48 | 1.7% |
| 16 heads, 4 factors | 49.3 | 6.04 | 12.3% |
| 16 heads, 8 factors | 59.5 | 16.73 | 28.1% |
| 16 heads, 2 factors, wider projections | 49.7 | 3.60 | 7.2% |

Selection and the chunk interaction machinery run per head. The same principal row-read/write FLOPs therefore coexist with substantially different wall time. The table's dense-limit 79.4ms row uses the authors' **SDM sparse kernels** on a fully dense special case. It is not optimized FLA-GDN's measured latency and cannot support a claim that sparse SDM is almost three times faster than GDN.

## Dense retrieval: useful negative evidence without a capacity converse

Appendix H measures write-set Jaccard overlap around .24 on ordinary text, versus nearly zero for random writing. Heads range from about 3% overlap with 30k distinct slots touched in an 8k sequence to about 43% overlap with 1.2k slots. In a small repeated-fact update probe, writes to the same entity overlap 130–350 times above chance and the latest value is returned in 47 of 48 trials. Collisions can implement overwriting as well as destructive interference; suppressing every collision is not automatically beneficial. These are particular empirical probes, not universal routing statistics. [H.1]

With 200 key–value pairs and fixed values, changing key type gives:

| Key type | SDM, % | GDN, % | FullAttn, % |
|---|---:|---:|---:|
| Distinct letters | 30 | 2 | 95 |
| Distinct words | 19 | 8 | 90 |
| Numbers | 7 | 6 | 99 |
| UUIDs | 3 | 3 | 99 |

This supports a substantial sensitivity to address/input structure at unchanged SDM state size. It does not isolate a pure collision effect from all changes in tokenization and input distribution. The text's “strict” performance ordering at every key type is literally too strong: UUIDs tie SDM and GDN at 3%. More consequentially, cross-architecture performance gaps do not prove that the remaining finite-task error is unavoidable compression loss. The paper offers that explanation, but supplies no finite-precision capacity converse or identification of a best possible decoder. [H.2, Table 14]

The same section reports a dedicated copy-trained SDM reproducing a 16k-token text. The description lacks enough protocol detail to turn it into an independent universal capacity measure. It is further evidence that training matters.

### Targeted training narrows the gap substantially

All three 8B post-trained models receive 400 additional steps at length8k, global batch4, approximately13M tokens, AdamW with a fresh optimizer and learning rate \(10^{-5}\). Loss is applied to the answer. About 58% of the mix uses multikey2's exact RULER-style templates, with other multi-key/single-needle examples and code. Thus results through 8k measure fitting to the task distribution; only longer lengths measure length extrapolation. Each evaluation has 500 samples per task/length. [H.3]

| Multikey2 exact match | 4k | 8k | 16k | 32k | 64k | 128k | Six-length average |
|---|---:|---:|---:|---:|---:|---:|---:|
| SDM before | 18.4 | 7.0 | 1.8 | .6 | .2 | 0 | 4.7 |
| SDM after | 98.8 | 92.0 | 66.8 | 29.6 | 10.6 | 2.0 | 50.0 |
| GDN after | 92.8 | 47.8 | 8.0 | 1.6 | .4 | 0 | 25.1 |
| FullAttn after | 100.0 | 99.0 | 96.6 | 87.4 | 59.2 | 26.6 | 78.1 |

These controls are valuable: SDM's fixed state supports far more successful retrieval after targeted training, and its extrapolation is stronger than GDN's. They also leave a large multikey2 gap and a collapse on UUID-based multikey3 beyond8k. Multikey1 is different: after training SDM exceeds full attention at64k/128k. Neither an aggregate win nor a dense-retrieval failure can be promoted into a universal statement about all memory tasks. [Figure16, Table15]

The no-hit GDN cell at128k has the paper's 95% upper bound of .7%; it is not proof of identically zero success probability. No new statistical audit or benchmark reproduction was undertaken.

## Hardware measurements and release correspondence

### Paper measurements

The main implementation uses H10080GB, PyTorch, xFormers attention and FLA GDN. At8B, one training step is SDM2.516s, GDN2.177s and FullAttn2.004s. At1.4B it is1.017s versus.849s for GDN, under the specified two-node/four8k-sequences-per-GPU/chunk64 setup. These are approximately16% and20% SDM overheads. The authors attribute the difference to HBM access for the much larger state, compared with GDN's small SRAM-resident working state. The full project's approximately300k GPU-hours covers training, fine-tuning, ablations and evaluation, not one run. [§6, AppendixI]

Figure6 uses an8B model, one H100, bf16, batch1. SDM overtakes full attention at approximately32k for decode and54k for prefill; **54k is interpolated between measured32k and65k points**. At131k it reaches about1.3× full-attention decode throughput and1.2× prefill throughput. GDN still leads SDM by about3% and7%, respectively. These are conditional measured comparisons, not universal hardware scaling guarantees.

AppendixF's three-way SWA/FullAttn/SDM hybrid improves some losses and has intermediate RULER behavior. Its Table12 is pretraining-only and averages six tasks at4k–8k, unlike Table2. Including any full-attention layers also retains their length-growing KV cache.

### The public release implements real sparse access, with a dense allocated bank

The pinned code's `layer.py` creates a learned `nn.Parameter` of shape \([HN,d_v]\), then allocates or clones \([BHN,d_v]\) private live states. `memory_ops.py`'s batch expansion explicitly allocates and copies; it is not a broadcast view. Stream offsets keep each example/head's slots private. The one-token `decode.py` kernel gathers only selected write rows, applies decay/residual update, stores them, then gathers the selected read rows. The sparse arithmetic is therefore implemented rather than merely asserted by a mask over a dense update.

The layer has both multi-token prefill/continuation and one-token decoding paths. It chooses the backward-saving path based on whether gradients are needed, not merely `eval()` mode. The cache stores the full memory plus a running Python token counter; no E²-TTT-like unfinished-chunk buffer is exposed. These are static interface findings, not a run proving arbitrary continuation partitions numerically identical.

The mutable-state lifetime also matters. The plain eager path with the `cuda_graph` option off restores the bank to its incoming value during backward, approximately when snapshots are quantized; a caller carrying state onward must preserve it before backward. `cache.update_` detaches memory. Calling the cache's `reset()` zeroes it; the model generator instead creates/copies the learned initial memory for a new prompt. The `cuda_graph` option's eager fallback keeps its final bank, while replayed graph states have additional documented copy/lifetime rules. None of these paths establishes untruncated gradients across arbitrary segments.

**Fixed bank shape does not imply fixed total allocation of this released generator.** Its SWA cache is explicitly allocated at `max_tokens`; only its attention mask enforces the window. SDM generation is handled one prompt at a time. The no-gradient prefill path bounds some working slabs but still allocates all output readings and input projections for the supplied sequence. A mathematical constant-length recurrent state, a practical persistent cache, and total prefill/training memory are different resource claims.

### What is and is not reproduced by the available assets

The repository includes runnable CUDA/Triton update kernels, training scaffolding, configuration templates, tests, layer/model/decode benchmark scripts and raw release-comparison records. It is not merely an inference sketch. Nevertheless:

- Its README explicitly says the paper's8B/H100 throughput figure used the paper's own implementation, **not this repository's code**. The release benchmark compares the current implementation with commit`183e7df` on **GB300**.
- The flagship template is width2048,24layers, sixSDM layers, twoheads and65536slots/head:805,306,368 memory entries across layers. Paper L08 is width1920,21layers and553M entries. The larger template is width4096,32layers, fourheads and2,147,483,648 memory entries, unlike paper L13's width3840,38layers, twoheads and7.963B. The templates also differ in RoPE/training-input settings. README calls them templates and says paper results were not rerun after the configuration changes.
- Release timing uses synthetic/random-weight workloads. Its24-layer training benchmark omits embeddings/output and rotary embeddings, and uses squared output loss; decode uses batch1 and256 measured steps. These resources validate a performance experiment of their own, not the paper's end-task results.
- The reported cross-version equivalence test fixes selected slots for several comparisons and lists exclusions. With each version's own bf16 selector, it reports1.4% differing selected slots and11% relative-RMS layer-output difference. The releases need not implement the identical rounded function despite the same \(W,R,C\) and shapes. These are author-reported results, not new independent executions.
- The bounded release inventory did not locate trained SDM checkpoint links, complete exact ladder configurations or full raw paper task results. No exhaustive external model-registry search was performed.

Source anchors at the pinned commit: [README](https://github.com/facebookresearch/sparse-delta-memory/blob/c1afb4d9e11ace11eca197080fb3504863d32096/README.md), [layer](https://github.com/facebookresearch/sparse-delta-memory/blob/c1afb4d9e11ace11eca197080fb3504863d32096/sparse_delta_memory/layer.py), [decode](https://github.com/facebookresearch/sparse-delta-memory/blob/c1afb4d9e11ace11eca197080fb3504863d32096/sparse_delta_memory/decode.py), [memory operations](https://github.com/facebookresearch/sparse-delta-memory/blob/c1afb4d9e11ace11eca197080fb3504863d32096/sparse_delta_memory/memory_ops.py), [cache](https://github.com/facebookresearch/sparse-delta-memory/blob/c1afb4d9e11ace11eca197080fb3504863d32096/sparse_delta_memory/cache.py), [generator](https://github.com/facebookresearch/sparse-delta-memory/blob/c1afb4d9e11ace11eca197080fb3504863d32096/apps/main/generate.py), [benchmark conditions/results](https://github.com/facebookresearch/sparse-delta-memory/blob/c1afb4d9e11ace11eca197080fb3504863d32096/benchmarks/RESULTS.md). The training metric explicitly reports active and learned memory-bank parameters separately.

## Research significance and limits

The useful source mechanisms are: independent sparse read/write supports; a delta residual within selected slots; slot-local rather than global forgetting; exact triangular resolution of affine within-chunk feedback; and factorized addressing that reallocates a fixed sparse access budget over a much larger physical state. The experiments make a credible case for these as practical design choices at the reported scales, with explicit resource prices and persistent dense-retrieval weaknesses.

For prediction-induced state formation, the paper learns addressing and update weights under a language-model objective, but it starts with a supplied fixed-dimensional bank and fixed hybrid layout. It does not derive which latent predictive distinctions should exist, prove minimality/sufficiency, learn the number of physical states, or quantify the finite persistent bits needed for a specified predictive loss. Learned \(M_0\) is extra parameter storage, not a free predictive-state construction. No FP theorem transfer or architecture recommendation is claimed here.

The main negative evidence is equally reusable: matching active FLOPs can conceal a large trained-state budget; higher address factorization can improve retrieval while slowing selection; task-adapted training can recover much of an apparent capacity failure without changing state size; and a residual cross-architecture gap is not by itself a capacity converse. These are source-grounded limits on inference, not a rejection of the useful sparse-update construction.
