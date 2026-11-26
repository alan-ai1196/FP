# Integral DeltaNet: Improved Linear Attention with Adaptive Memory Integration

## Identity and actual coverage

- Junsoo Oh, Jihun Yun, Junhyuck Kim and Hanbaek Lyu. [arXiv:2611.32063v1](https://arxiv.org/abs/2611.32063v1), submitted November 24, 2026, 06:50:52 UTC. [PDF](https://arxiv.org/pdf/2611.32063v1) and [complete source](https://arxiv.org/src/2611.32063v1). The primary version history checked on November 26 lists only v1. No conference acceptance was authenticated in this bounded check.
- **Pro-B full reading:** all 18 pages, §§1–6, Appendices A.1–A.2 and B.1–B.3, both propositions and proofs, five figures, eight tables, author and implementation footnotes, acknowledgments and the complete printed bibliography. Main TeX and all substantive section files were read. Original PDF figures were inspected on pp. 2, 4, 8, 9 and 18, together with dense proof layouts. The source bibliography contains 77 records, including unused entries, which is not a count of papers independently read.
- Complete PDF and source are recoverable from the versioned links and locally under `literature/corpus/arxiv_frontier/2611.32063v1/`. Plot coordinates were used to recover exact throughput values, not as independent experimental data.
- Scoped author-code inspection at [f6ec94e15d7b4a3eaea5d8b888168a2e1a7b7ac9](https://github.com/junsoo424/Integral-DeltaNet/tree/f6ec94e15d7b4a3eaea5d8b888168a2e1a7b7ac9) covered the README, model and training configurations, the mixer/cache interface, selected gate and recurrence dispatch, and the low-level state interface. A source assistant inspected the broader inventory. Pro-B directly rechecked the important cache and configuration passages. No GPU execution, checkpoint evaluation, full Triton audit or benchmark replication was performed.

## Research question and mechanism

The paper asks whether a recurrent linear-attention model can reduce interference from competing key/value associations while retaining information weakened by later writes. It adds an exponentially weighted history of a delta-rule memory and learns how much of each memory to read. The state dimensions and update family are supplied by the architecture.

For keys and queries in dimension \(d_k\), values in dimension \(d_v\), the fast state is \(S_t\in\mathbb R^{d_v\times d_k}\). The tested backbones are Kimi Delta Attention, KDA, and Gated DeltaNet-2, GDN-2. KDA uses

\[
S_t=S_{t-1}\operatorname{Diag}(\alpha_t)
       (I-\beta_t k_tk_t^\top)+\beta_tv_tk_t^\top.
\]

GDN-2 replaces the scalar erase coefficient with a vector applied to the key and uses a separate vector write gate applied to the value. The integral construction leaves these fast-state rules unchanged. [§§2–3, pp. 2–5]

The new state and readout are

\[
X_t=S_t\operatorname{Diag}(\lambda_t)
       +X_{t-1}\operatorname{Diag}(1-\lambda_t),
\]

\[
o_t=S_t(\gamma_t\odot q_t)
      +X_t((1-\gamma_t)\odot q_t).
\]

Both states start at zero. Each key channel has its own integration and readout rates. The gates come from rank-128 projections of the normalized input hidden state. Their initial values satisfy approximately \(\lambda=1-\gamma=1/1024\), so the initial readout favors the fast state while the integral state builds slowly. The learned gates need not preserve this initial timescale separation everywhere. [§3.1 and §4]

For a single channel the historical weight on \(S_i\) at time \(t\) is

\[
\lambda_i\prod_{j=i+1}^{t}(1-\lambda_j).
\]

This is a weighted history of **complete intermediate memories**, rather than a second independent stream of raw key/value writes. The integral state affects the readout, not the subsequent fast-state transition. The paper explicitly distinguishes this from schedule-free optimization, which evaluates updates at an interpolation of fast and averaged iterates. [§5, p. 10]

### Chunk parallelization

Within one chunk, write the existing fast recurrence as \(S^r=S^0P^r+H^r\). The paper defines weighted prefix operators

\[
\bar P^r=\sum_{i=1}^rP^i\operatorname{Diag}(\omega^{i\to r}),
\qquad
\bar H^r=\sum_{i=1}^rH^i\operatorname{Diag}(\omega^{i\to r}),
\]

where \(\omega^{i\to r}\) is the preceding retention weight. Then

\[
X^r=S^0\bar P^r+X^0\operatorname{Diag}(\omega^{0\to r})+\bar H^r.
\]

The two incoming states therefore pass through a block-triangular affine recurrence. Effective queries separate the output into contributions from incoming \(S^0\), incoming \(X^0\), and within-chunk writes. These identities follow by substitution in the supplied linear recurrence. Efficient realization additionally depends on the backbone's WY/UT constructions and the implementation of the weighted operators. The algebraic display alone is not a throughput theorem. The released code contains fused Triton paths. [§3.2, pp. 5–6]

## What the illustrative separation proves

The three unit keys satisfy \(k_1=k_2+k_3\). The values are \((v_N,v_Y,v_Y)\), with orthogonal answer vectors and squared norms \(2\) and \(1\). The final query is uniform over the three supplied keys. For a fixed state and linear answer scores, define

\[
m_i=(v_Y-v_N)^\top S_3k_i.
\]

The key relation forces \(m_1=m_2+m_3\). Thus the desired sign pattern \((-,+,+)\) is impossible with a query-independent linear readout. Standard fixed tie-breaking does not remove this obstruction. Linear attention has risk \(2/3\). The scalar-gated Mamba-2, DeltaNet and GDN recurrences attain their minimum risk \(1/3\) in the specific construction. [Proposition 1, pp. 3–4, Appendix A.1, p. 16]

For Integral DeltaNet the authors choose \(\beta_t=1\), \(\alpha=(1,1/4,1)\), and \(\lambda_t=1/8\). The integral-state readout answers the first query and the fast-state readout answers the other two. **The selector is allowed to depend on the query.** This yields zero risk. [Proposition 2, p. 5, Appendix A.2, pp. 16–17]

Pro-B independently recomputed the finite construction using the exact rational Gram matrix

\[
G=\begin{pmatrix}1&1/2&1/2\\1/2&1&-1/2\\1/2&-1/2&1\end{pmatrix}.
\]

The final score differences are

\[
m(S_3)=(17/16,1/16,1),
\qquad
m(X_3)=(-23/512,11/512,-17/256).
\]

They support the printed construction. This is a bounded algebra check, with no claim of formal verification or empirical replication.

**Scope deduction:** a fixed mixture of the two matrices would again be a single linear map of the query and would retain the same obstruction. The separation uses the combination of a second retained state and an input-dependent readout. It does not prove that every trained single-state neural model fails, that these specific keys arise in language modeling, that optimization finds the selector, or that two states are memory-optimal. The paper itself identifies the example as illustrative.

## Experiments and controls

All models are trained from scratch on FineWeb-Edu, with Llama-2 tokenization and 4K training sequences. Labels of 340M and 1.3B refer to **non-embedding** parameters, with 15B and 100B tokens respectively. The shared recipe uses AdamW, a nominal 0.5M-token batch, cosine decay from \(4\times10^{-4}\) to \(4\times10^{-5}\), weight decay .1 and gradient clipping at 1. Warmup uses .5B and 1B tokens. [§4, pp. 6–7]

Comparators include Transformer++, Mamba-2, DeltaNet, GDN, KDA and GDN-2. Recurrent training uses FLA kernels, with FA2 and FA4 attention timing comparators. The experiment is stronger than a comparison with an unfused recurrent reference. It is not a complete comparison with every contemporary hybrid or Mamba-3 model.

Selected reported results at 1.3B are:

| Metric | KDA | Integral KDA | GDN-2 | Integral GDN-2 |
|---|---:|---:|---:|---:|
| WikiText perplexity | 15.33 | 15.00 | 16.34 | 15.92 |
| LAMBADA perplexity | 9.63 | 9.16 | 10.56 | 10.31 |
| Nine-task mean accuracy | 54.6 | 56.1 | 54.2 | 54.6 |
| Six retrieval tasks, mean accuracy | 35.4 | 37.3 | 32.3 | 34.5 |
| S-NIAH-2 at 4K | 70.0 | 99.6 | 74.2 | 65.2 |
| S-NIAH-3 at 4K | 24.8 | 41.6 | 30.0 | 34.6 |
| Multi-key NIAH at 4K | 20.8 | 35.6 | 23.8 | 39.8 |
| LongBench average | 13.9 | 15.0 | 14.6 | 14.8 |

Sources: Tables 1–4, pp. 7–8. Each NIAH condition uses the same 500 examples across models. The integral variants improve averages, with substantial task-specific regressions as well as gains. Transformer++ still obtains 45.6 on the real-world retrieval average, ahead of 37.3 for Integral KDA. Its failures beyond the 4K training length concern this particular extension recipe, not a universal failure of attention.

Figure 3 evaluates perplexity from 4K through 20K on six datasets. Both integral variants improve over their own backbones at the tested extrapolation lengths. These are finite-length, fixed-checkpoint measurements, with no unlimited-context theorem. The reported tables do not provide repeated-training uncertainty estimates.

### Ablations that matter

Appendix B.1 contains **state-size controls**, not just a smaller baseline. At 340M/15B it doubles the KDA key dimension, doubles its value dimension, and uses two KDA states with independent update gates and the same adaptive readout. FFN widths are adjusted to match total parameters. Retrieval averages are 21.1 for KDA, 21.1 for doubled keys, 22.2 for doubled values, 22.0 for two KDA states, and 23.3 for Integral KDA. These comparisons support a benefit of the integrated history under this recipe. They do not isolate equal runtime or establish statistical significance. [Table 6, p. 17]

A token-independent learned readout gate reduces Integral KDA's retrieval average from 23.3 to 21.8 and its commonsense average from 46.5 to 45.9. This supports the readout's practical role. Channel-wise integration and readout give the best language-model perplexities and commonsense average among the four scalar/channel combinations, but scalar readout with channel-wise integration gives the best retrieval average, 23.8 versus 23.3. Avoid describing the fully channel-wise choice as best on every metric. [Tables 7–8, pp. 17–18]

Figure 5 shows larger relative integral-state norms for distant needles in selected layers, particularly 15 and 16. The plotted ratio is the norm of one contribution divided by the sum of the two contribution norms. It is not a causal attribution fraction, and pooling heads/samples does not establish which stored information caused a correct answer.

## Resource accounting and public reproduction boundary

The recurrent memory remains constant in sequence length, but each integral layer carries two \(d_v\times d_k\) matrices. The added matrix, gate projections, arithmetic and activation storage must be charged separately from static parameter matching.

On the paper's B300, batch 8, CUDA-graph replay and **excluding prefill**, Table 5 reports:

| Model | Calculated decoding memory at 4K–64K | Measured per-token latency |
|---|---:|---:|
| KDA | 2.85 GiB | 3.34 ms |
| Integral KDA | 2.99 GiB | 4.63 ms |
| GDN-2 | 2.85 GiB | 3.19 ms |
| Integral GDN-2 | 2.99 GiB | 4.79 ms |

The integral variants add about 4.9% to these **whole-model memory totals**, while latency increases about 38.6% and 50.2%. The small total-memory percentage must not be substituted for the increase in recurrent matrix storage. Memory values are architecture calculations, not measured peak allocations. These numbers do not establish RTX3090 performance. [p. 9]

At 4K×8 training tokens per batch, the plotted throughputs are 58.0K tokens/s for KDA, 52.8K for throughput-first Integral KDA and 46.5K for memory-first Integral KDA. Corresponding activation-memory bars are 81.7, 159.3 and 49.8 GiB. The memory-first path achieves its low activation usage through extra recomputation. The paper explicitly notes that its recomputation scope differs from the baseline kernels. This result cannot be interpreted as an intrinsic activation-memory advantage at identical checkpointing. [Figure 4 and its footnote, p. 9]

The pinned public [model configuration](https://github.com/junsoo424/Integral-DeltaNet/blob/f6ec94e15d7b4a3eaea5d8b888168a2e1a7b7ac9/configs/models/integral_kda_1.3b.yaml) has 18 layers, width 2304, 16 heads of dimension 128 and FFN width 7408. KDA uses FFN width 7568. Declared total parameters are 1,450,317,600 versus 1,450,096,416, with the difference between total and body counts coming from embedding/output parameters. This authenticates the matching convention, not the actual trained run.

**Concrete release limitation:** [`IntegralMixer.forward`](https://github.com/junsoo424/Integral-DeltaNet/blob/f6ec94e15d7b4a3eaea5d8b888168a2e1a7b7ac9/integral_deltanet/integral_mixer.py) rejects a nonempty `past_key_values` or `use_cache=True` with a two-state-cache-not-implemented exception. [`Block.forward`](https://github.com/junsoo424/Integral-DeltaNet/blob/f6ec94e15d7b4a3eaea5d8b888168a2e1a7b7ac9/integral_deltanet/model.py) supplies `use_cache=False`. The low-level [`ops/readout.py`](https://github.com/junsoo424/Integral-DeltaNet/blob/f6ec94e15d7b4a3eaea5d8b888168a2e1a7b7ac9/integral_deltanet/ops/readout.py) does accept initial and final recurrent states. Thus the missing piece is the published full-model cache integration, not the possibility of recurrent decoding. The inspected release does not directly reproduce the reported cached-generation benchmark through its main model API.

The source inventory contains the four KDA/GDN-2 families at both scales and training recipes, but no dedicated benchmark launch scripts, raw experimental logs or the additional state-size ablation configurations were found. The source assistant authenticated eight public checkpoint filenames through the linked model repository, without downloading weights. These limitations do not establish that the reported experiments were not performed. They identify what remains necessary for reproduction.

## Research disposition

This is a useful current fixed-memory architecture with meaningful baseline and state-size ablations. The supported mechanism is preserving a weighted trace of intermediate delta memories and selecting between fast and integrated readouts. The finite example and empirical measurements have different evidential roles.

No state-minimality, adaptive state-count, unknown symbolic-update recovery or FP transfer theorem follows from the paper. No substantive FP mapping is proposed here. The practical open items are independent measurements with complete decode code, repeated runs, and comparisons under matched state memory, total parameters and recomputation policy at larger scales.
