# Reproduction and scope

## Predictions recorded before running the new audits

1. With labels flipped on one of four visits to each short word, fitting the binary sign of the conditional mean should recover parity on longer words. The same learner should use one signed register for parity and three for the six-state construction. Start from a fair forecast. Give it a capacity ceiling and an alphabet with arbitrary names. Disclose every observed word and label count.
2. In the six-state construction start the generator at `(1,1,-1)`. Its three letters rotate coordinates, negate them all, or replace the last coordinate by the negative sum of all three. The target is the first coordinate with noise. Predict six reachable residual states, linear dimension three and exact signed-copy width four. Check the lower bound independently from all reachable states of the generator. A six-entry indexed state machine should reproduce the same predictions.
3. At strict density above three quarters of the signed cube, a linear form taking values in `{−1,+1}` on every reachable vertex should have only one nonzero coefficient. Exhaustively check small integer coefficient grids, including equality examples. This concerns exact linear realization on reachable vertices.
4. Withhold odd-length examples from a rank-one learner. Two transition laws should agree on every training observation and disagree on each odd-length word. A single independent odd constraint should remove that ambiguity when the even constraints span their parity subspace.

The full text certificate, the exact R4 evaluator and earlier experiments have a pinned reproduction route in the [repository guide](../../README.md). New finite-word results concern terminal binary labels.


## Executed controls

From the root of `frontier` run the following with plain Python 3.10 or later and assertions enabled.

~~~sh
python -B research/frontier/audit.py --check
python -B research/frontier/alternatives.py --check
~~~

[General learner](learner.py) · [Independent oracles and generators](audit.py) · [Primary receipt](result.json) · [Competing learners and exact covering search](alternatives.py) · [Comparison receipt](alternatives_result.json)

**NUMERICALLY VERIFIED.** For the balanced design each short word supplies four ordinary labels with one flip. The learner predicts before updating counts. The validation block includes every word of length $2R$ with the same conditional frequencies, disjoint from the training words. This is an exact design, not random sampling. At unit tap price the fair forecast is selected and at zero price the learned model is selected. An independent categorical learner merges equal vectors of short-suffix majorities from exactly the same counts. A breadth-first check closes the product of the trained machine and each independent source, covering every reachable transition and hence every word. All 128 binary-output machines with two declared states, binary alphabet and either start state also pass. The cube audit checks 736 coefficient vectors and finds 40 equality cases.

| Quantity | Parity | Six-state source |
|---|---:|---:|
| Alphabet, declared rank ceiling | 2, 2 | 3, 4 |
| Distinct acquisition words | 15 | 3,280 |
| Training labels / input symbols read | 60 / 136 | 13,120 / 85,296 |
| Held-out validation labels / state-bit taps | 64 / 256 | 26,244 / 769,824 |
| Fair / learned Brier loss | 1/4 → 3/16 | 1/4 → 3/16 |
| Learned linear width / minimum signed-copy width | 1 / 1 | 3 / 4 |
| Nonzero integer transition weights | 2 | 11 |
| Logical transition payload plus initial bits | 7 bits | 74 bits |
| Categorical states / indexed transition entries | 2 / 4 | 6 / 18 |
| Elimination divisions / multiply-subtract pairs | 6 / 6 | 156 / 2,860 |
| Short replay letters / taps | 34 / 34 | 21,324 / 78,188 |

**Resource accounting.** Let $M=|W|,b=|U|,d=|A|$. The direct acquisition stores two counts per word, each fitting $\lceil\log_2(n+1)\rceil$ bits after $n$ labels. Dense indexing by word length and base-$d$ rank avoids string keys; the Python audit uses dictionaries with keys of up to $2R-1$ characters. Fitting also holds $M$ signs, up to $rb$ echelon entries, and $O((1+d)r^2)$ rational solve entries. Constructing the candidate takes $b^2+(1+d)r^2+r$ Hankel cell lookups, at most $O(b^2r+dr^3)$ rational operations, integer coefficient reduction, and one further pass over $W$ to replay the signs. There are $M$ count reads for sign extraction in addition to those lookups. Rational operations have operand-dependent bit cost. The table reports logical data and arithmetic counts, not CPython heap peaks or accelerator timings.

With alphabet and shape given, the tabulated payload uses $r$ initial bits, a support mask of $r$ bits per letter/output, and a sign and $\lfloor r^{r/2}\rfloor.\mathrm{bit\_length}()$ magnitude bits per nonzero parameter. Deployment additionally needs the shape (at most $\lceil\log_2(R+1)\rceil$ bits), a calibration numerator and denominator (each at most $\lceil\log_2(n+1)\rceil$ bits), a letter index, two $r$-bit buffers and an accumulator with one sign bit plus $\lfloor rD\rfloor.\mathrm{bit\_length}()$ magnitude bits. Reading a word of length $l$ costs $l$ symbol reads plus the stated taps, one head read and one calibrated probability output. These are feasible explicit encodings; the Python tuples use more memory. On the six-state source the three letters use 3, 3 and 5 stored-bit taps. Only the last letter requires two additions and a sign decision in the specified integer realization.

The strongest simple conventional comparator here is a minimal indexed deterministic machine. With a public state numbering it uses $Nd\lceil\log_2 N\rceil+N$ table/output bits (60 for the six-state case), the initial index, one active state index, calibration, one indexed transition per letter and one output lookup per word. The independent fitter used 4,840 suffix-sign probes plus signature hashing/comparison on the six-state training data. A conventional exact linear realization obtained by Hankel elimination has the same fitted maps before integer reduction. A signed-copy realization at width four stores four initial bits, 12 address/sign pairs (three bits per pair), and a head address/orientation unless fixed by convention. It performs four taps per letter. Binary bit packing, table lookups and dense rational multiplication have different costs. There is no demonstrated overall speed or memory win for the proposed learner.

**NUMERICALLY VERIFIED — canonical R4.** In a pinned reconstruction checkout, run the command below from `frontier`, replacing the final path with that checkout. The program lowers the independently **learned** deterministic table into positive SUM, PRODUCT and delay nodes. Both arms pay for ordinary acquisition. One reset event prepares the positive initial state. The positive-base comparison uses fitted amplitude $1/2$.

~~~sh
python -B research/frontier/audit.py --check --r4-root ../fp-reconstruction-check
~~~

The actual R4 exact evaluator closes 5 evaluations on parity and 19 on the six-state source, including reset and every reachable transition. The six-state positive graph uses 36 nodes, 4 sources, 6 delayed cells, 18 PRODUCTs, 8 SUMs with 25 terms, two coefficient slots $(1,2)$ and the native two-head normalization. The parity graph uses 13 nodes, 3 sources, 2 delayed cells, 4 PRODUCTs, 4 SUMs with 7 terms and the same two slots. The reference evaluator multiplies and adds per SUM term. An optimized conventional indexed table is included above. This tests R4 arithmetic on equally informed **derived** graphs. R4's full installation, persistence and mixed-precision obligations have different costs. [Lowering and comparison](positive_comparison.py)

**EMPIRICALLY OBSERVED.** One 32,768-episode seeded run sampled short words uniformly and flipped each ordinary label independently using the pseudorandom generator. All 364 cells had at least 65 visits. With $R=3$ the inferred six-state law had all signs correct under product-state verification, amplitude $8131/16384$ and exact fresh excess Brier $3721/1073741824$. The finite-sample probability theorem has independent hypotheses. The seeded outcome supplies one observation.

**NUMERICALLY VERIFIED.** On the 24 prefix/probe pairs, exhaustive search over 4,960 free three-bit projective encodings finds two unavoidable sign errors; a valid three-register program attains them. On the even-only rank-one experiment, 64 examples determine four equations. Four additional noisy observations of one odd word raise the dimension to five. The check compares 1,365 unseen and seen query words to the hidden generator and 2,240 independent posterior queries to exhaustive enumeration.

On the balanced two-token, 16-label design, the separate ridge factor learner has eight stored entries at initialization and after each dense sweep. One sweep at $\lambda=1/2$ gives positive score $4/17$ and Brier $237/1156$. The saturated empirical conditional table on the same examples obtains $3/16$. Both-zero factors never move. Three sweeps use 48 divisions and 40 multiply-subtract pairs in the linear solves plus the matrix multiplications. An $m$-by-$n$ pair problem stores $m^2+nm$ trainable entries, $2mn$ outcome counts and $O(m^2+mn)$ temporary entries. Per sweep the dense arithmetic order is $m^3+nm^2$ and an inference dot product uses $m$ multiplies and $m-1$ additions. Three fixed sweeps form the tested finite optimizer. Its limiting shrinkage proof is separate.


## Self-driven next-token streams

Run `python -B research/frontier/audit_stream.py --check`. Both learners start with the same all-zero context, score before each token, and receive just that token. Raw-context acquisition ends after each context has supplied its first $k$ labels. The next 4,096 tokens form one uninterrupted held-out continuation. The unknown generators enter only in data generation and independent risk evaluation. [Stream learner](stream.py) · [Comparison and exhaustive checks](audit_stream.py) · [Receipt](stream_result.json)

**NUMERICALLY VERIFIED.** Exhausting all 4, 16 and 256 binary conditional sign functions of orders 1, 2 and 3 finds respectively 0, 0 and 16 with strict linear-width advantage over signed copying. The first order-three witness in integer truth-table order has positive contexts 001 and 100. Every compiled transition and head is checked on every raw context. Four hundred small exact grid fits agree with exhaustive multinomial Brier minimization.

**EMPIRICALLY OBSERVED.** On that binary source with noise $1/4$, 1,310 tokens supplied 63 retained labels for each of eight contexts. The fit recovered the four-dimensional update and all true signs. Five distinct predictive states and five signed-copy coordinates suffice. Its fitted amplitude is $61/126$. On a separate ternary order-two source, 1,765 tokens supplied 97 labels per context. A 12-unit probability grid produced a five-dimensional recurrent fit with nine distinct predictive states. Forecasts on all nine contexts exactly equal the fitted conventional table. This is a mathematical price for particular state instructions, not a finding of cheaper execution than indexed lookup.

| Predictor | Binary held-out NLL | Ternary held-out NLL |
|---|---:|---:|
| Recurrent fit and directly indexed identical fit | 0.569724488479 | 1.025666211525 |
| Full-prefix conditional table, half-count posterior | 0.571599912627 | 1.020260257028 |
| Frozen binary context-tree weighting, full prefix | 0.570008595913 | — |
| Continuing binary context-tree weighting | 0.570533721646 | — |
| Known generating law | 0.569845189561 | 1.015520876859 |

Scores are nats per token. The indexed and recurrent forms are equal by construction. The full-prefix controls may use **all** observed labels; the receipt also includes binary CTW fit to the same retained counts. For the binary CTW comparator the exact KT likelihood and half stop/split recursion are evaluated on the suffix tree. Each frozen next-token probability is independently checked against the exact new/old tree-likelihood ratio. The continuing score is the joint likelihood ratio over the entire continuation. Mean logs use 60-digit decimal arithmetic after exact probability calculation. Exact stationary context weights give population NLLs of 0.562500807397 and 1.021877609618 for the two fits, versus 0.562335144619 and 1.011304981624 for the generators. The ternary half-count table wins both stationary and realized comparisons. [Original CTW recursion](https://pure.tue.nl/ws/portalfiles/portal/1383848/Metis122608.pdf)

With $C=K^L$ raw contexts, acquisition uses $KC$ bounded counters and one context index. Fitting also uses up to $Cr$ rational echelon entries, $Cr$ fitted coordinates, and $O(Kr^2+Kr)$ solve entries, with up to $O(KCr^2+Kr^3+KCr)$ arithmetic operations. The literal grid allocator costs $O(CK(Q-K))$ integer comparisons. A stream deployment keeps $r$ bounded integer values, a second update buffer, coefficients, denominators and one accumulator. The binary fit uses 6 or 10 coefficient taps per symbol; the ternary fit uses 14, 19 or 17, in addition to head evaluation. The exact source tables, closures and audit code determine every operation. The indexed form maintains a raw context index and looks up one forecast row, with $C(K-1)$ free empirical probability entries. CTW uses counts and mixture values at $2^{L+1}-1$ nodes and updates one suffix path per token. Its exact fraction bit costs depend on prefix length.


## Original full-alphabet successor values

**NUMERICALLY VERIFIED.** The registered closed-form learner beats the entire fixed 513-source mixture class on the historical development suffix. Both successor models still score above the historical modified Kneser–Ney and Transformer. The positive-price model stores 42.34% of the unpriced model's row payload. [Pre-execution registration](https://github.com/alan-ai1196/FP/blob/477c05a/research/frontier/NEXT.md) · [Integer-mass audit](text.py) · [Machine-readable certificate](text_result.json)

| Predictor | Development NLL in nats/token | Learned successor rows | Sparse row payload |
|---|---:|---:|---:|
| Training-only add-one base in this audit | [7.758622196, 7.758622197] | 0 | 0 bytes |
| Positive-price successor rows | [7.109546182, 7.109546183] | 6,715 | 997,040 bytes |
| All observed successor rows | [7.039207622, 7.039207623] | 34,215 | 2,354,844 bytes |
| Best fixed mixture, even fitted on the development labels | [7.236294824, 7.236529809] | — | Different source bank |
| Historical order-5 modified Kneser–Ney / Transformer | 6.587281632 / 6.260544623 | — | Different training and execution budgets |

The paid learner starts with empty counts. Compute $q_y=(n_y+1)/(786432+50257)$ from the first 786,432 training tokens. An observed adjacent pair increments a row entry. Its fitted value is $p_x(y)=(n_{xy}+64q_y)/(n_x+64)$, a normalized distribution constructed from successor observations. The next 262,144 training tokens supply evidence for publishing each frozen row. Let $G_x$ sum its log-likelihood gain over the base there. A row with $h_x$ entries costs $c_x=64+48h_x$ bits. Publish exactly when $G_x>c_x\log(2)/256$. For any set of rows the priced gain is the sum of their individual net gains, proving exact optimality among subsets of this fitted bank on this gate. The gate prices declared payload and consumes training exposure. Selection on one block supplies no out-of-sample optimality theorem.

The base occupies an additional 201,028 bytes (50,257 uint32 counts). A sorted header contains a uint16 ID, uint32 outgoing count and uint16 degree; each successor has a uint16 ID and uint32 count. These are payloads. A seekable row index additionally needs offsets (e.g. four bytes per row), or sequential access costs a scan. Within a row, binary search is available on sorted IDs. A full-vector request also writes 50,257 probabilities. Acquisition counted 786,431 adjacent pairs and 346,854 occupied entries. The gate consumed 262,144 forecasts grouped into 137,014 distinct pairs after observation. The reference uses dictionaries and cached logarithms, which cost more than the indicated compact deployment. Each scored label needs a constant number of integer mass operations after indexed lookups. The conventional interpolated count table with the same rows is exactly the same learner on this task.

For portable small checks run `python -B research/frontier/text.py --check`. With the original data run `python -B research/frontier/text.py --text --check`; `--data-dir` accepts another directory containing the identical `train.bin` and `val.bin`. Both historical prefix SHA-256 digests and source extents are checked. The gate comparisons and scores sum outward integer bounds on logs of positive integer masses. Correctly rounded 60-digit decimal logs are expanded by adjacent representables, then outwards onto the $10^{-18}$ grid. Any unresolved gate comparison falls back to an exact integer-power test. All 128 small gates agree with exhaustive subset selection. The scored 12,288 positions were previously exposed in the project's historical research. No device performance was measured. [Historical text protocol and stronger anchors](https://github.com/alan-ai1196/FP/blob/a674dda8985be1dd316b102da4fa00a42c837819/research/reconstruction/EXPERIMENTS.md)


## Paid reuse of intermediate values

Run `python -B research/frontier/audit_materialization.py --check`. The learner first infers its sign updates from raw terminal labels. The layout optimizer receives only the fitted predictions, symbol counts and resource prices. Independent tests execute the lowered instructions from every reachable state and compare each transition and charged operation against direct subset enumeration. [Layout optimizer and evaluator](materialization.py) · [Audit](audit_materialization.py) · [Receipt](materialization_result.json)

**NUMERICALLY VERIFIED.** With counts $(n_q,n_m,n_v)=(3,2,2),(2,2,3),(2,1,4)$, the registered fixed-basis optimizer chooses 3, 3 and 4 registers at exact costs 77, 84 and 84. Each cut has 18 vertices and 31 arcs and used four augmentations. A rental of eight per register reverses the last choice. The subsequent all-bases audit checks all three admissible bases. It finds 3, 4 and 3 registers at workloads $(2,1,4),(48,4,48),(48,48,4)$, with costs 77, 1,200 and 928. The independent four-state counterexample verifies that two individually harmful cache additions become jointly profitable. A separate learned law verifies shared scratch execution. Another 384 small graph/price combinations agree with execution and exhaustive selection. The register-machine units cover this layout and workload; these are exact arithmetic audits.
