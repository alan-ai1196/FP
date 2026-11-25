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

The selected historical Kneser–Ney binary occupied 34,489,589 bytes. The four-layer, width-128 Transformer had 7,253,376 parameters. Each of its two training runs consumed 16,777,216 target exposures and reached 1,191,628,800 allocated and 1,772,093,440 reserved GPU bytes on the RTX 3090. The historical comparison uses the same reporting positions with different training budgets. [Original measurement journal](https://github.com/alan-ai1196/FP/blob/a674dda8985be1dd316b102da4fa00a42c837819/evidence/minimal/FP_TEXT_BASELINE_ANCHOR_A1.json)

The paid learner starts with empty counts. Compute $q_y=(n_y+1)/(786432+50257)$ from the first 786,432 training tokens. An observed adjacent pair increments a row entry. Its fitted value is $p_x(y)=(n_{xy}+64q_y)/(n_x+64)$, a normalized distribution constructed from successor observations. The next 262,144 training tokens supply evidence for publishing each frozen row. Let $G_x$ sum its log-likelihood gain over the base there. A row with $h_x$ entries costs $c_x=64+48h_x$ bits. Publish exactly when $G_x>c_x\log(2)/256$. For any set of rows the priced gain is the sum of their individual net gains, proving exact optimality among subsets of this fitted bank on this gate. The gate prices declared payload and consumes training exposure. Selection on one block supplies no out-of-sample optimality theorem.

The base occupies an additional 201,028 bytes (50,257 uint32 counts). A sorted header contains a uint16 ID, uint32 outgoing count and uint16 degree; each successor has a uint16 ID and uint32 count. These are payloads. A seekable row index additionally needs offsets (e.g. four bytes per row), or sequential access costs a scan. Within a row, binary search is available on sorted IDs. A full-vector request also writes 50,257 probabilities. Acquisition counted 786,431 adjacent pairs and 346,854 occupied entries. The gate consumed 262,144 forecasts grouped into 137,014 distinct pairs after observation. The reference uses dictionaries and cached logarithms, which cost more than the indicated compact deployment. Each scored label needs a constant number of integer mass operations after indexed lookups. The conventional interpolated count table with the same rows is exactly the same learner on this task.

For portable small checks run `python -B research/frontier/text.py --check`. With the original data run `python -B research/frontier/text.py --text --check`; `--data-dir` accepts another directory containing the identical `train.bin` and `val.bin`. Both historical prefix SHA-256 digests and source extents are checked. The gate comparisons and scores sum outward integer bounds on logs of positive integer masses. Correctly rounded 60-digit decimal logs are expanded by adjacent representables, then outwards onto the $10^{-18}$ grid. Any unresolved gate comparison falls back to an exact integer-power test. All 128 small gates agree with exhaustive subset selection. The scored 12,288 positions were previously exposed in the project's historical research. No device performance was measured. [Historical text protocol and stronger anchors](https://github.com/alan-ai1196/FP/blob/a674dda8985be1dd316b102da4fa00a42c837819/research/reconstruction/EXPERIMENTS.md)


## Paid reuse of intermediate values

Run `python -B research/frontier/audit_materialization.py --check`. The learner first infers its sign updates from raw terminal labels. The layout optimizer receives only the fitted predictions, symbol counts and resource prices. Independent tests execute the lowered instructions from every reachable state and compare each transition and charged operation against direct subset enumeration. [Layout optimizer and evaluator](materialization.py) · [Audit](audit_materialization.py) · [Receipt](materialization_result.json)

**NUMERICALLY VERIFIED.** With counts $(n_q,n_m,n_v)=(3,2,2),(2,2,3),(2,1,4)$, the registered fixed-basis optimizer chooses 3, 3 and 4 registers at exact costs 77, 84 and 84. Each cut has 18 vertices and 31 arcs and used four augmentations. A rental of eight per register reverses the last choice. The subsequent all-bases audit checks all three admissible bases. It finds 3, 4 and 3 registers at workloads $(2,1,4),(48,4,48),(48,48,4)$, with costs 77, 1,200 and 928. The independent four-state counterexample verifies that two individually harmful cache additions become jointly profitable. A separate learned law verifies shared scratch execution. Another 384 small graph/price combinations agree with execution and exhaustive selection. The register-machine units cover this layout and workload; these are exact arithmetic audits.


**NUMERICALLY VERIFIED — discovery costs.** Run `python -B research/frontier/audit_discovery.py --check`. Each restricted planner receives fitted short-word moments. The independent verifier receives the complete finite source and compares the returned bounds and every reachable transition to a full-orbit solution. In the complementary example the successive certified intervals are [245,284], [252,284] and [252,252]. A paid early exit on a different workload returns an executable three-bit layout at 91 with lower bound 84. The exact optimum remains inside that reported interval. [Search and accounting](discovery.py) · [Independent checks](audit_discovery.py) · [Receipt](discovery_result.json)

The eight-state, three-letter source has 128 projective suffix columns. A declared probe dictionary consists of powers of the first letter through length seven. The specially constructed source makes that dictionary informative. Its 144 distinct concatenated words receive 576 ordinary noisy labels and require 4,576 input symbols. That is a designed coverage fixture. For counts $(46,53,1)$ the solver expands eight columns, discovers ten including the boundary, and closes the interval immediately at 2,434. It uses 2,176 rational dot-product terms, 128 divisions and 480 multiply-subtracts in the additional inverse solve, and constructs 134 cut arcs across the two solves. The initial basis extraction separately uses 64 divisions and 136 multiply-subtracts. This is evidence of a cheaper search in this case. It neither supplies a suitable probe dictionary for every source nor proves these search costs are repaid over 100 deployed letters.


**NUMERICALLY VERIFIED — finite-grid boundary.** The stream audit also exhausts 5,292 mixed two-input affine forms with integral and half-integral coefficients. For grids of sizes 2 through 8 the attained maxima are respectively 3/4, 7/9, 12/16, 19/25, 27/36, 37/49 and 48/64 of the full square. Midpoint mixing and its worst-case rounding error are checked separately. The [chain argument](FOUNDATION.md#exact-finite-grids-and-the-continuous-limit) covers arbitrary real coefficients and register dimension.

## Learning a rare action

**NUMERICALLY VERIFIED.** Run `python -B research/frontier/audit_action.py --check`. In the fixed-frequency experiment, each of four familiar words and four words containing $v$ once supplies 512 ordinary binary labels. The four rare contexts have prefix/suffix lengths $(0,0),(1,0),(2,1),(3,2)$ in $q$. The first two already determine $P(Y=1\mid q^4v)=63/128$ with minimum variance proxy $137/16384$ in the frozen true basis. Their span leaves $vq$ unidentified. All four determine a full two-by-two action. An exact change of coordinates proves agreement at arbitrary word lengths for this fitted instance. Enumeration also checks every one of 511 words through length eight. The training words cost 9,728 symbol reads and 4,096 labels. The state uses two scalars, each action four coefficients and each dense update four multiplications and two additions. The anchor elimination uses 12 divisions and 10 multiply-subtracts. The rare-action solve with its uncertainty inverse uses 36 and 108 respectively, in addition to ranks, design formation and normal-equation assembly. [Audit](audit_action.py) · [Exact results](action_result.json)

**EMPIRICALLY OBSERVED.** Independently sampling the same 512 binary outcomes per word with seed 27031 keeps all four design directions. Across the 503 *unseen* words through length eight, 427 raw predictions fall outside $[0,1]$. After clipping, mean excess Brier against the generating probabilities is in $[0.187633631,0.187633632]$. A single constant fitted to the same labels scores $[0.012616694,0.012616695]$. The score weights each unseen word equally. Ordinary least squares on the same acquired designs exactly reproduces the candidate. This one realization refutes a general finite-sample guarantee based on rank alone. [Counts and bounded scores](action_result.json)

## Stable scalar composition

Run `python -B research/frontier/audit_affine.py --check`. The bounded learner receives ordinary counts for exactly the same eight words as the unconstrained fit. Seven prefix lookups yield five usable pairs. Two observed words have no observed immediate prefix. All eight contribute to the comparison's acquisition cost. In the exact-frequency experiment its learned endpoints are $(3/8,7/8)$ for $q$ and $(5/16,9/16)$ for $v$. The independent categorical execution uses two state probabilities and two stochastic rows per letter. Every forecast agrees with the scalar implementation on all 511 words in each trial. Another 625 rational regressions pass independent first-order optimality conditions on the endpoint square. [Registered design](https://github.com/alan-ai1196/FP/blob/d36379c/research/frontier/NEXT.md) · [Learner](affine.py) · [Audit](audit_affine.py) · [Receipt](affine_result.json)

**EMPIRICALLY OBSERVED.** The 32 prospective seeds use 512 labels for each of eight words and score 503 unseen words per seed. Equal-weight mean excess Brier was $0.001075017$ for the bounded scalar, $0.139911351$ for the clipped unconstrained fit and $0.012538662$ for the fitted constant, each within $10^{-9}$. The bounded scalar won both paired comparisons on all 32 seeds. None met the predefined maximum confidence-interval width of $1/4$. The original failure seed gives $0.001107308$ for the bounded fit and a widest interval of $0.985773140$. On the separately registered 8,192-label run for seed zero the widest interval was $[0.188069419,0.188069420]$ in width, meeting the threshold. Radii were $5/64$ and $5/256$ respectively, giving the same simultaneous failure bound $16e^{-25/4}<0.031$ per trial under the sampling and model assumptions. All intervals contained the true means in these runs. The true two-state source belongs to the restricted family. This is a matched finite experiment in which the conventional two-state realization ties exactly. [Exact counts and bounds](affine_result.json)

## One learned group on the original stream

Run `python -B research/frontier/text_memory.py --text --check` for the original files or omit `--text` for the portable rational controls. A frequency partition fitted on 786,432 training tokens puts 244 token types in the first group. The calibration and search blocks use 131,072 subsequent training targets each. Both families see exactly the same tape and frozen within-group rows. The reference makes 50 training passes over the last block, totaling 6,553,600 transition evaluations. Its log bounds account for rounding, and 400 independently scored small policies agree with direct rational likelihoods. The original development stream warms for 4,095 predictions and continues going into the 12,288 scored targets. [Prior registration](https://github.com/alan-ai1196/FP/blob/2a89cc5/research/frontier/NEXT.md) · [Learner and controls](text_memory.py) · [Receipt](text_memory_result.json)

| Full-vocabulary forecast | Nats per reporting target, outward bounds |
|---|---|
| Original full successor bank | [7.039207622, 7.039207623] |
| Recalibrated rows, selected overwrite, selected recurrent | [7.034802531, 7.034802532] for each |
| Best group correction per current token with hindsight | [6.805902354, 6.805902355] |
| Correct group supplied on every target | [6.436692824, 6.436692825] |

**EMPIRICALLY OBSERVED.** Both training searches selected $(0,0)$. Even before pricing, the best nonzero recurrent pair increased training gate loss by [0.003107498, 0.003107499] nats per target. None of the 3,491 distinct last-token IDs on the reporting suffix received multiple recurrent states. The registered criterion for useful composition failed. The gain of roughly 0.00441 nats against the original full bank came entirely from fitting the row group rates to additional data. **NUMERICALLY VERIFIED.** The two hindsight rows bound entire classes acting through this partition, including models with substantially more training or state. Both preserve the same positive within-group distributions. [Limits](OBSTRUCTIONS.md)

The full bank has 346,854 successor entries plus its row headers and unigram counts. Extra packed deployment data can include a 6,283-byte group mask, a uint16 calibrated mass per token (100,514 bytes), and one uint32 in-group successor count per token (201,028 bytes). The last table and the fixed global group constant give the two group normalizers using the existing row totals. The active model needs neither a fitted nonzero slope nor a live historical scalar. A nonzero recurrent pair uses up to six slope-code bits and twelve live state bits. Each candidate inference step looks up the row and group membership and performs a bounded integer affine update with one rounding. The reference stores Python objects and reevaluates training candidates. These payloads and operation counts give no device throughput claim.

## Learning a distinction on the original stream

Run `python -B research/frontier/partitions.py --text --check` or omit `--text` for the finite controls. The first 786,430 two-step training pairs contain 34,215 target types and 1,639 distinct posterior values. The optimizer certified the best of 1,638 boundaries, at $16/35$, by outward log bounds. The high group contains 35,964 IDs including unseen IDs placed at the pooled posterior. The reference compares every fitted cut against all 16 assignments on 256 small count tables. On 729 four-vertex weighted graphs, exact conditional count likelihood equals the cut formula for every assignment. On the raw fit prefix, 6,082 eligible two-successor contexts contribute 16,929 targets. Greedy assignment retains [2721.572477544, 2721.572477545] of [3120.787384834, 3120.787384835] possible fitted information nats before the shared-cut constraint. That diagnostic has no prospective score claim. [Registered protocol](https://github.com/alan-ai1196/FP/blob/d737b5d/research/frontier/NEXT.md) · [Optimizer and controls](partitions.py) · [Receipt](partition_result.json)

| Stored past bit / output group | Overwrite NLL | Conditional NLL | Installed rows | Last-token IDs with both forecast values on the suffix |
|---|---:|---:|---:|---:|
| Frequency / frequency | 7.034802532 | 7.031797247 | 1,106 | 193 |
| Learned / frequency | 7.034802532 | 7.033218357 | 1,109 | 211 |
| Frequency / learned | 7.036673259 | 7.035382902 | 605 | 143 |
| Learned / learned | 7.036673259 | 7.036517820 | 581 | 147 |

**EMPIRICALLY OBSERVED.** The table gives upper endpoints accurate to $10^{-9}$ nats per token on the same 12,288 exposed targets. Both training blocks supplied 131,072 targets. A separate streaming evaluation preserved one delayed bit, predicted before reading the target and reproduced the exact probability-mass histogram in all four arms. The learned/learned arm beats its overwrite and the original full bank at 7.039207623. It loses to frequency/frequency, so the registered positive test failed. The learned partition's group oracle floor also worsens to [6.479076927, 6.479076928]. Its hindsight current-token floor is [6.836068747, 6.836068748]. Both partitions leave the original Transformer below their respective recurrent floors.

Two secondary controls quantify the source of the score differences. Within each current-token ID, permute the historical bits uniformly across reporting occurrences while holding token outcomes and fitted rows fixed. If $n_{ij}$ counts bit $i$ and output group $j$ for that token and $p_0,p_1$ are its fitted rates, the expected increase in total NLL is $(n_{00}n_{11}-n_{01}n_{10})(\operatorname{logit}p_1-\operatorname{logit}p_0)/n_x$. This follows by expanding the binary log loss and replacing joint counts by products of the marginals. The expected increases are 0.002211220 and 0.000397517 nats per target for frequency/frequency and learned/learned respectively, within $10^{-9}$. They measure the alignment between the actually retained history and observed targets on this tape.

A conventional sparse trigram can buy a group rate for a pair of raw 16-bit token IDs. It sees the same samples and uses the same smoothing, integer grid, gate and output decoder. Rank positive net gains under a 44-bit record price and charge 16 live bits for the previous raw token. All record costs are equal, so the best gains up to the available capacity maximize the priced gate objective. Under the frequency arm's 44,241-bit incremental cap it uses 29,408 bits and scores [7.032305681, 7.032305682]. Under the learned arm's 23,241-bit cap it uses 21,048 bits and scores [7.034337988, 7.034337989], beating the learned/learned arm. Training sees 75,931 occupied raw-pair calibration cells versus 20,512 or 21,234 bit-conditioned cells. The original base storage, rate tables and group mask are shared. Crossed arms additionally need access to both masks. Deployment uses one group normalization and one indexed lookup per selected row, with an extra class-membership lookup for the delayed-bit learner. These are packed arithmetic comparisons on the registered observer. [Full resource and score counts](partition_result.json)

## Prospective transfer to the next training-file block

Run `python -B research/frontier/transfer.py --text --check` on the original training file, or omit `--text` for the independent checks. The scored targets were the 131,072 positions immediately following the previous 1,048,576-token fit, calibration and gate prefix. The extended prefix was authenticated against the archived complete-file hash before the continuation was scored. The program reads this training file alone. The models were frozen, received the same preceding context and predicted before observing each target. [Prior registration](https://github.com/alan-ai1196/FP/blob/8b20275/research/frontier/NEXT.md) · [Implementation](transfer.py) · [Receipt](transfer_result.json)

| Frozen model | Nats per target, upper endpoint within $10^{-9}$ | Incremental payload |
|---|---:|---:|
| Full successor bank | 7.161075683 | Shared base |
| Frequency-group overwrite | 7.158738497 | Shared calibration |
| Frequency bit | 7.156688534 | 44,241 bits |
| Raw-token-pair trigram, frequency output | 7.156457557 | 29,408 bits |
| Context-conditioned exchange bit, frequency output | 7.156047730 | 96,818 bits |
| Previous graph cut as output, overwrite | 7.160098867 | Shared calibration |
| Previous graph cut as output, frequency history | 7.159116136 | 79,578 bits |
| Raw-token-pair trigram, graph-cut output | 7.158662436 | 24,788 bits |

**EMPIRICALLY OBSERVED.** The two exchange sweeps inspected 693,706 occupied-pair records, evaluated 2,662,572 entropy terms and accepted 13,815 and 1,412 bit flips. The installed model uses 1,164 conditional rows, one delayed bit and a separate 50,257-bit membership table. Against its own overwrite the new bit saved 352.68 observed nats, or 90.54 nats after its modeled share of storage. Against the raw trigram it saved 53.72 nats before a 182.52-nat incremental price. Against the frequency bit it saved 83.99 before a 142.36-nat price. The registered simultaneous lower bounds on net conditional gain were respectively $-10.10,-231.13,-165.33$ nats before pricing any extra acquisition operations. The positive test failed. At these prices the data cannot certify a positive allowance for discovery work. They establish neither a population loss for this fixed corpus nor a device-time comparison.

The older graph cut retained 2,721.57 fitted information nats on its original two-successor contexts. On the new block those context IDs occurred 3,131 times, covering 1,555 of the original 6,082 IDs. In 2,459 occurrences the next token was *neither* of the two training successors. On those IDs the frozen conditional predictor saved about 1.17 observed nats relative to its overwrite, with a conditional lower bound of $-2.34$ nats before rent. The training information total and prospective frozen score measure different quantities. For portable checks, 128 finite tapes agree with independent rational exchange trajectories. Exact path counting bounds the probability of ever falsely declaring positive gain under a specified fair null through 128 events. [Gain certificate](FOUNDATION.md#certifying-a-learned-computation-on-a-continuing-stream)

## Synchronizing bit control

Run `python -B research/frontier/audit_unifilar.py --check`. The optional `--r4-root` takes a clean checkout of the pinned reconstruction at `a674dda`. The learner sees one raw four-symbol stream, a two-state hypothesis and a lower emission bound of $1/8$. State labels and reset markers enter only in generation and independent checking. [Prior registration](https://github.com/alan-ai1196/FP/blob/f8bae86/research/frontier/NEXT.md) · [Learner](unifilar.py) · [Audit](audit_unifilar.py) · [Receipt](unifilar_result.json)

**NUMERICALLY VERIFIED.** A 514-token Eulerian tape realizes the exact stationary triple frequencies. The four recovered determinant ratios are $0,0,5/64,-5/64$. The post-reset closure recovers the two resets, retain and reverse, both emission rows, and the stationary mixture up to state renaming. Independent population calculations reproduce the source on all 210 communicating, synchronizing action tables with the declared emission rows. The best predictor using only the most recent token incurs excess stationary multiclass Brier loss $45/1024$ against the synchronized bit. Each permutation letter contributes $w_0w_1\lVert e_0-e_1\rVert_2^2/(w_0+w_1)$ with $w_i=P(S=i)e_i(a)$, and each reset contributes zero.

**EMPIRICALLY OBSERVED.** On seed 120311, the learner recovered all four actions from 65,536 training tokens. It skipped one unsynchronized prediction when fitting its add-one emission rows. Frozen NLL on the next 16,384 raw tokens was $[1.060317232,1.060317233]$, compared with $[1.127950064,1.127950065]$ for the smoothed successor and $[1.060318152,1.060318153]$ for exhaustive estimation over the same 256 transition tables. The latter recovered the same topology. It used a fixed initial-state convention and included the first training prediction. The one-seed comparison measures finite-tape performance under the registered source.

The successful learner uses three training window scans plus one ordinary replay (262,138 loop visits). Exhaustive fitting makes 16,777,216 table visits. Acquisition stores pair counts for the pivot, four counts per token for the shifted blocks and two emission rows. The synchronized deployed model has eight action bits, eight emission counts, two row totals and one live state bit. One indexed transition and one emission row suffice per token. On this fit the counts and row totals each fit in 16 bits. The pinned R4 evaluator exactly reproduced both states and all eight transitions plus its explicit initialization event, using 21 nodes, two delayed cells, eight products, six sums with 17 weighted terms and nine parameter slots. Each event performs native four-way normalization. This verifies the derived graph's forecasts after synchronization. State acquisition, stationary initial filtering and device throughput have separate costs. [Tested arithmetic](positive_comparison.py)

## November 23 literature transfers

**NUMERICALLY VERIFIED.** The portable checker recomputes the convex ratio $5588869/5505024$, 775 integer grid displacements, and summary widths for three distinct future observers. An independent calculation used 7,140 integer and fractional displacements. Fourier checks cover all 2,048 vertex-invariant Boolean properties on four vertices and all 64 fixed graph-edge masks. A separate three-uniform adaptive counterexample on six vertices leaves variance $1/2^{21}$. The noisy-OR erasure tangent at $p=1/3,\eta=1/8$ is $0.379724102535$ nats per unit coordinate-erasure probability. The entropy evaluation uses floating point. The combinatorial checks use integers or rational arithmetic. [Proofs and assumptions](../../literature/research_connections.md) · [Checker](audit_literature.py)

**FORMALLY VERIFIED for the finite construction.** All 128 seven-bit query masks have a unique codeword within Hamming distance one. The four basis masks are 7, 25, 42 and 75. Across all 16,384 hidden-word/query pairs the decoded answer equals the original parity. Lean 4.34.1 (5045d0056413266e57c625dcd7c365b10e377c52) accepted the file using Std and kernel reduction. The printed axiom reports use propext, with Quot.sound also appearing for uniqueness. The Python check separately obtains 8, 16, 32, 64 and 128 covered masks for zero through four stored bits and verifies balanced posteriors on the remainder. The general trace and entropy bound has a written proof and independent mathematical review. Its formalization remains open. [Lean source](HammingSeven.lean) · [Loss theorem](../../literature/research_connections.md#the-general-bound)

~~~powershell
python -B research/frontier/audit_literature.py
& "$env:USERPROFILE\.elan\toolchains\leanprover--lean4---v4.34.1\bin\lean.exe" research/frontier/HammingSeven.lean
~~~

The finite-state and parity results refer to different tasks. The physical charge for the parity construction includes seven raw bits, four extra stored bits, nine separate precomputation XORs, query decoding and all synopsis accesses. There is no measured GPU speedup for this construction.

## Learning a four-bit synopsis from noisy tokens

**EMPIRICALLY OBSERVED.** The task map, training and test seeds, sample sizes, hypothesis classes, tie rules and comparators were committed before generating the tapes. The fit saw raw words, opaque task IDs and noisy labels. The 32,768 training examples and 16,384 fresh test examples used independent random streams and an independent label-flip rate of $1/8$. Loss is mean natural-log loss per held-out binary target. Every ID had 256 training and 128 test examples. [Dated registration](https://github.com/alan-ai1196/FP/blob/1e6c46d/research/frontier/NEXT.md) · [Executable experiment](parity_acquisition.py) · [Complete receipt](parity_acquisition_result.json)

| Fitted learner | Layouts scored | Correct task rules out of 128 | Fair test predictions | Test loss | Query-time raw bits read over all test targets |
|---|---:|---:|---:|---:|---:|
| Exhaustive four-parity synopsis | 11,811 | 128 | 0 | 0.381640 | 14,336 |
| Greedy four-parity synopsis | 236 | 112 | 2,048 | 0.419880 | 12,288 |
| Four cached raw coordinates | 35 | 64 | 8,192 | 0.536859 | 6,144 |
| Unrestricted raw-parity reader | 1 | 128 | 0 | 0.381640 | 57,344 |

The observed labels gave each ID exactly one profitable rule. All 30 four-dimensional radius-one covering subspaces attained the same empirical optimum. The declared tie rule chose masks 7, 25, 42 and 75. The compiled readout gave 14,295 correct confident and 2,089 incorrect confident test predictions, exactly matching the unrestricted fitted reader. Greedy fitting selected 11, 22, 39 and 67. Each fit estimated its per-task decoder as well as the layout. An independent implementation scored raw predictions directly, enumerated all 11,811 layouts by a different construction, and checked 38,912 compiled task/input routes across the three constrained fits.

Acquisition accumulated 32,768 signed observations into a 131,072-byte integer histogram, then made 114,688 scalar Walsh additions or subtractions plus temporary array traffic. Each of the 16,384 key/mask pairs was tested for profitable likelihood. Candidate generation, basis extension, radius-one set construction, likelihood comparisons and route compilation are extra work. Filtering left 128 profitable key/mask pairs. The exhaustive search checked 1,511,808 readout memberships, greedy checked 30,208, the raw-cache search checked 4,480, and direct fitting checked 128. The potential mask family and legal operations are supplied to all fits, with the generator and scoring work charged. A small histogram is a sufficient statistic for this specific loss family.

Each constrained model actually serialized four seven-bit masks and 128 nine-bit route entries into 148 bytes including padding. The unrestricted model used 144 bytes. Each episode kept the seven raw input bits, and a constrained model added four bits of state before seeing the task. The full four-parity fit took 13 input taps, nine binary XORs and four writes per new raw word when the parities were reduced separately. Each later uniform query averaged two synopsis taps, $7/8$ of a raw tap, and $241/128$ binary XORs; direct evaluation averaged $7/2$ raw taps and $321/128$ XORs. For repeated independent uniform tasks on one retained input, this schedule uses fewer XORs in expectation at 15 queries. Counting all input and synopsis bit taps at equal cost crosses at 21 queries, or 28 if each of the four preprocessing writes also costs one tap. These thresholds omit routing/address logic shared or specific to each reader. Actual packed-word bit extraction and population count have machine-dependent costs.

Three complete receipt replays on the available Ryzen 7 5800X under Windows 11, Python 3.12.9 and NumPy 2.5.1 took 1.769, 1.765 and 1.743 seconds, including process startup, data generation, all fits and checks. The Windows peak working-set counters observed during those runs were 36,810,752, 36,704,256 and 36,864,000 bytes. These are whole CPU process measurements. Each logical raw-bit query in the Python replay extracts from a packed word already in host memory.

A **post hoc memorization check** used a separate clean bit for each (ID, input) pair, a uniform prior and the true label noise. Training visited 14,171 distinct pairs. The test included 2,265 occurrences of 1,399 distinct pairs absent from training. Their pair-table loss was $\log 2$ and the four-parity fit obtained 0.380958. Across all test targets the pair-table loss was 0.503990. This shows generalization to new combinations of an input and a trained task. Every test ID occurred in training. [Learning guarantee](FOUNDATION.md#which-shared-computations-does-prediction-error-select)

~~~powershell
python -B research/frontier/parity_acquisition.py --check research/frontier/parity_acquisition_result.json
python -B research/frontier/parity_packing.py
~~~

## Foundation R4 comparison for the fitted four-bit synopsis

**NUMERICALLY VERIFIED.** A post hoc comparison refits the registered opaque-ID learner, deserializes its 148-byte model and uses native positive products and sums from the pinned Foundation R4 reference evaluator. The host supplies the two indicator values for each exposed bit, looks up the fitted route and fetches its selected synopsis bits and at most one raw bit. R4 computes both the stored parities and the query reduction. A binary XOR on two indicator pairs requires four products and two two-term sums. The encoder for the actual learned masks has 70 nodes, 36 products, 19 sums and four state bindings. Its interface has one constant and fourteen indicator channels for seven raw bits. Each query circuit has up to 16 products and eleven sums across at most five selected bits. Two positive base masses and six units of learned-class excess give exactly $7/8$ to its chosen label. The scale six uses the same specified noise level as the other fitted readers.

The exact rational evaluator checked all 128 source words for the encoder and all 63 distinct argument tuples of arities zero to five for the readouts. Their operational composition returned the correct noisy law on every one of the 16,384 word/task pairs with 32,768 synopsis taps and 14,336 query-time raw taps. The bit interfaces, route lookup and dispatch are part of this realization. R4 can execute the learned computation with this interface. The fitted model and training search are shared between realizations. This control establishes representability and leaves native acquisition and optimized end-to-end throughput open. [Executable R4 comparison](parity_r4.py) · [Pinned reference arithmetic](https://github.com/alan-ai1196/FP/blob/a674dda8985be1dd316b102da4fa00a42c837819/src/reference_compiler/fp_reference/semantics.py)

## A learned operation on 92 held-out task IDs

**EMPIRICALLY OBSERVED.** Three paired synthetic worlds shared raw inputs and noise. Each fit used 7,168 binary labels on 28 task IDs and 896 labels on seven separate validation IDs. All 11,776 scored targets belonged to 92 further IDs. A fit knew public task coordinates, the binary input length, the noise rate and its allowed operations. Predictive training and validation received no task rules or composition labels. The score below is mean held-out natural-log loss per target. [Registration committed before generation](https://github.com/alan-ai1196/FP/blob/1f7b25f/research/frontier/NEXT.md) · [Learner](task_composition.py) · [Per-ID losses and full result](task_composition_result.json)

| Generating world | Validation selection | Linear loss | Interaction loss | Lookup loss | Exact rules recovered by selected predictor out of 92 |
|---|---|---:|---:|---:|---:|
| Linear map | Linear | 0.378092 | 0.378092 | 0.689915 | 92 |
| One unknown nonlinear interaction | Interactions | 0.609929 | 0.378092 | 0.689887 | 92 |
| Random permutation | Lookup | 1.083022 | 1.094424 | 0.690036 | 0 |

The oracle loss was 0.378092 in each world because they used the same independent noise draws. Every fitted singleton and doubleton task meaning was recovered correctly. In the nonlinear world the learner installed just the product of public task bits 5 and 7 with seven-bit coefficient 46. The fitted coefficient equaled the third learned singleton column, so the induced composition flips bit 3 on the cross term. The linear fit recovered 62 of the 92 held-out rules. Inversion of the learned nonlinear meaning map reproduced the teacher's composition on all 16,384 ordered pairs, while ordinary XOR of the public IDs agreed on 10,240. A post hoc two-byte instruction with pair address and update direction executed the learned operation on all pairs without building an inverse table at prediction time. The scored probability task used the learned meaning interpreter. The pair-composition check was a separate execution.

With random naming the interaction fit paid for all 21 candidate terms and mapped 128 names to only 81 distinct meanings. Validation chose the posterior lookup with loss 0.692265, compared with 1.084769 for linear and 1.056536 for the fitted interactions. The deployed lookup averaged all 93 remaining masks after inferring the 35 observed meanings. Its confidence on input zero and small residual biases on other inputs explain its gain over a fair guess. An independent fit using direct match counts reproduced the selections, NLLs, coefficients and held-out rule counts in all three worlds.

Acquisition per world used a 28,672-byte fitting histogram and 25,088 scalar Walsh additions or subtractions, plus 6,272 such operations when estimating the seven validation meanings for lookup. It tested 3,584 fit and 896 validation key/mask correlations and 21 possible interaction terms. The fitted interpreter serialized 54 bits including its term count when linear, 66 bits with one term, and 306 bits with 21 terms (7, 9 and 39 actual bytes). In the nonlinear world's 92 queried task descriptions, computing each mask once executed 408 seven-bit XORs, including 30 active interactions, and checked the interaction predicate 92 times. Each mask was reused on 128 raw words in the actual test layout. A probability lookup can keep the remaining-mask set in 128 bits. The measured implementation also cached 128 binary64 probabilities, costing 1,024 bytes. The benchmark includes neither a GPU kernel nor language-text scoring.

Three complete CPU replays with the subsequent compact-law check took 0.195, 0.190 and 0.191 seconds including startup on the Ryzen 7 5800X. The observed process peak working sets were 36,081,664, 36,208,640 and 36,196,352 bytes. The same data also admit a conventional linear predictor over a supplied quadratic feature expansion. The result establishes that ordinary labels can select and price a specific operation and transfer it to unused tasks in this grammar. A cubic bijection can agree on every training and validation answer yet change 16 of the 92 test meanings. [Finite-sample argument and induced operation](FOUNDATION.md#learning-a-nonlinear-operation-on-previously-unseen-task-descriptions) · [Indistinguishable teachers](OBSTRUCTIONS.md#seven-validation-triples-leave-a-cubic-shear-invisible)

~~~powershell
python -B research/frontier/parity_r4.py
python -B research/frontier/task_composition.py --check research/frontier/task_composition_result.json
~~~

## Learning the response operation from opaque task names

**EMPIRICALLY OBSERVED.** Each of 128 opaque names denoted an unknown subset of seven hidden features. In paired worlds the observable binary response combined the selected features by XOR or inclusive OR. The learner considered all 16 two-input truth tables. It learned the task dictionary from 58,240 noisy labels across seven pilot inputs, learned the eight training inputs' anchor answers from 3,640 separate labels, and selected its operation using 17,408 further labeled predictions. A researcher chose the pilot conditions. The learner received their noisy outcomes with no raw input-feature values or target operation. [Prospective registration](https://github.com/alan-ai1196/FP/blob/9f5fc05/research/frontier/NEXT.md) · [Learner](response_operation.py) · [Complete receipt](response_operation_result.json)

Seven pilot inputs distinguished all 128 names and left precisely XOR and OR tied at 13,332 correct fitting tokens in both worlds. One extra input condition gave the correct gate 15,244 matches out of 17,408 and the other candidate 14,824. The learner installed the selected four-bit truth table. It then used that table to produce predictive probabilities on 2,048 fresh episodes with 21 noisy anchor answers per episode, three from each learned anchor. Each episode scored a fixed panel of the other 120 nonempty tasks, for 245,760 next-token targets. No further panel outcomes were exposed before those forecasts.

| Predictor | XOR world, nats/token | OR world, nats/token |
|---|---:|---:|
| Learned binary operation | 0.534416 | 0.409900 |
| Fixed XOR | 0.534416 | 0.810485 |
| Fixed OR | 0.979035 | 0.409900 |
| Bayesian average over all 16 gates | 0.534416 | 0.409900 |
| Lookup over the eight fitted training inputs | 0.890710 | 0.684344 |
| Known dictionary and operation, same 21 observations | 0.534416 | 0.409900 |

A separate oracle summed over all 128 latent inputs given the same observed anchor outcomes. The deployed learner instead propagated the probabilities of its seven calibrated bits through the learned operation. Of the 2,048 episodes, 1,919 used a latent input pattern absent from training. Their losses were 0.535718 and 0.406048 for the respective learned operations, compared with 0.921873 and 0.701749 for prototype lookup. The oracle and conventional Bayesian gate learner matched the fitted gate to the reported precision. These 120 predictions share the same adaptation observations in each episode. Treating them as independent uncertainty estimates would understate sampling variation. Independent raw truth-table enumeration and separate closed-form posterior forecasts reproduced these scores.

The executable packed model contains 896 bits for name signatures, 49 for the seven anchor addresses, and four for the operation, or 119 bytes with padding. Pilot order fixes the coordinate convention. Replaying every name's response on the ordered pilots requires at least $\lceil\log_2(128!)\rceil=717$ bits for an arbitrary named permutation. Training compared 16 truth tables on 1,024 aggregated labeled cells. For one fresh panel the subset recurrence reuses 120 binary combines across all outputs after initializing the seven singleton probabilities. The batched implementation uses binary64 and materializes intermediate arrays. All 43,008 adaptation labels in the test are charged. Three complete Windows CPU replays on the Ryzen 7 5800X took 0.726, 0.735 and 0.735 seconds with peak working sets of 55,533,568, 55,369,728 and 55,672,832 bytes. This measures the complete script, including both worlds, controls, oracle calculations and post-fit checks.

**FORMALLY VERIFIED.** Lean 4.34.1 checked for any dimension and any pair of distinct coordinates that the augmented Boolean row family has exactly one closed operation depending on both arguments, for each of the specified XOR and OR columns. The definitions enumerate all 16 binary truth tables and quantify over arbitrary pilot rows. The identification of table indices 6 and 14 with XOR and OR is also proved. Each printed axiom report lists only propext. The finite-sample learning result has a separate probabilistic proof. [Lean source](ResponseOperation.lean) · [Information and acquisition bounds](FOUNDATION.md#identifying-a-binary-operation-from-noisy-task-responses)

~~~powershell
python -B research/frontier/response_operation.py --check research/frontier/response_operation_result.json
python -B research/frontier/audit_response_probes.py
& "$env:USERPROFILE\.elan\toolchains\leanprover--lean4---v4.34.1\bin\lean.exe" research/frontier/ResponseOperation.lean
~~~

## Selecting a binary memory update on ordinary text

**EMPIRICALLY OBSERVED.** On the registered FineWeb-Edu training file, the best of all 16 binary updates was gate 5. It stores the complement of the preceding frequency bit. Swapping the two entries of each installed decoder row gives exactly the direct lagged-bit predictor, gate 10. The two gates tied on the operation-selection block and made identical full-vocabulary predictions on all 131,072 later targets. The smaller gate index broke the tie as registered. A raw-token trigram scored better using one fewer logical bit. The registered positive criterion failed. [Frozen protocol](https://github.com/alan-ai1196/FP/blob/00cd1ce/research/frontier/NEXT.md) · [Code](text_operation.py) · [All 16 selection scores, payloads and held-out intervals](text_operation_result.json)

| Frozen predictor | Extra bits | Nats per token | Nats per token including price |
|---|---:|---:|---:|
| Smoothed successor | — | 7.111886 | — |
| Calibrated successor | 0 | 7.108584 | 7.108584 |
| Selected gate 5 | 28,925 | 7.106576 | 7.107174 |
| Lagged frequency bit, gate 10 | 28,925 | 7.106576 | 7.107174 |
| Raw-token trigram | 28,924 | 7.105866 | 7.106463 |

The score is the causal probability assigned to the observed token in a normalized distribution over all 50,257 tokens. Tokens 0–786,431 fitted the common successor law and a 244-token frequency group. Three successive blocks of 131,072 targets calibrated rates, priced rows and selected the operation. The next block, at zero-based targets 1,179,648–1,310,719, supplied the reported score. Memory persisted across the boundaries. The test used a continuation of the training file. Historical Transformer and Kneser–Ney losses were measured on different targets. The hindsight best remaining operation on this block was gate 10. No operation with a more distant history beat the lagged readout here.

The 723 selected rows occupy 3,616 packed bytes including the operation header and padding. An installed record has one 16-bit address and two 12-bit rates. Gate 5 and gate 10 buy exactly the same rows with reversed rates. The price is $(\log 2)/256$ nats for each extra logical bit over the full scoring block. The trigram bought 657 observed raw-token pairs and needs a previous 16-bit token. Both priced predictors use the shared smoothed successor rows, frequency membership, calibrated masses and the last token. The receipt counts their shared arrays and the optional cached 64-bit group numerators. Scoring looked up the observed token. Materializing all probabilities on every step would involve additional output traffic.

Fitting and choosing the 16 gates executed 18,874,352 binary state updates, visited 4,194,304 calibration or row-pricing targets and scored 2,097,152 operation-selection targets. The raw trigram inspected 75,931 distinct calibration pairs and 74,113 row-pricing pairs. The Python/NumPy reference expanded packed rows into temporary dense tables. Complete replays on the Ryzen 7 5800X took 3.45–3.61 seconds with observed peak working sets of 148–150 MB. An independent scalar execution calculated full token probabilities directly on every reporting target. It reproduced all five NLLs within their outward-rounded intervals and checked both lagged readouts on all 723 rows. Exact small controls matched counts and decoder histograms for all 4,096 pairs of a gate and a four-token history. The measurement covers CPU acquisition and evaluation.

~~~powershell
python -B research/frontier/text_operation.py --check research/frontier/text_operation_result.json
~~~

## Learning which token identities can share an action

**EMPIRICALLY OBSERVED.** A likelihood learner saw 262,144 independent stationary three-token episodes from a six-token source. Four raw tokens always had the same immediate probabilities. Two preserve a hidden bit and two flip it. Selecting the internal alphabet from adjacent pairs merged all four. Selecting it from triples recovered both true alias pairs and kept the two informative tokens separate. The learner received raw token IDs and episode boundaries. Hidden states and candidate assignments from the teacher were absent from both selection routines. [Prospective registration](https://github.com/alan-ai1196/FP/blob/4c5aa39/research/frontier/NEXT.md) · [Implementation](symbol_refinement.py) · [Exact loss intervals](symbol_refinement_result.json)

| Three-token predictor after freezing its partition | Held-out nats/token | Third-position nats | Expected nats/token under the source | Packed bytes |
|---|---:|---:|---:|---:|
| Partition learned from pairs | 1.727703 | 1.723825 | 1.726804 | 131 |
| Partition learned from triples | 1.726488 | 1.720186 | 1.725503 | 279 |
| Unrestricted raw triple | 1.726582 | 1.720396 | 1.725612 | 871 |
| Given true partition, same fitted count tables | 1.726488 | 1.720186 | 1.725503 | 279 |
| Known source probabilities | 1.726470 | 1.720103 | 1.725461 | — |

All fitted alternatives received the same raw triples for their final probability tables, including the pair-selected partition. The reporting set had 65,536 fresh episodes and 196,608 causal predictions. The registered triple learner met both conditions. Its gain over the pair-selected alternative was 0.00121448 nats per token. The expected-loss column is a post-fit calculation using exact probabilities of all 216 possible episodes of this synthetic source. It checks the sign of the small observed advantage over the unrestricted raw triple for these particular trained models. The given-partition reference measures the fit that receives the correct internal alphabet for free. This experiment learned a partition and a normalized three-position predictor. Learning and executing its underlying unlimited-horizon state update is a stronger claim.

The code examined 203 partitions in each acquisition view. After counting training windows, partition evaluation scanned 51,156 raw count cells across both searches. It used the registered parameter penalty and bounded logarithms, with a canceled integer-product comparison for ambiguous intervals. The objective margins over the next candidate were 32.31 total nats for the pair learner and 343.94 for the triple learner. The executable count layout uses one byte for the group count, six group IDs, one unsigned 32-bit count per coarse triple, and a 32-bit refinement count for each token in a nonsingleton cell. The four-cell predictor has 65 independent probability parameters in this family. Causal inference uses at most two prior cell IDs and can cache the 21 shorter coarse-prefix masses. A specialized raw layout could omit the seven-byte generic header. Both normalized prefix readouts and joint factorization were checked exactly on all 216 raw words. Complete Python CPU replays took approximately 0.45 seconds with a peak process working set near 45 MB.

**NUMERICALLY VERIFIED.** Exact population enumeration found 15 lossless partitions on pairs and four on triples. It recovered the same coarsest partitions as the training experiment. A separate integer-matrix construction verified the finite-rank obstruction at ranks two through five. It compared 11,068 word probabilities and the first separating words at lengths 3, 5, 7 and 9. The general result has a mathematical proof. The long-stream 0.053465-nat penalty in that proof concerns a population optimum under a forced merge. [Derivation](FOUNDATION.md#when-two-raw-tokens-can-share-one-internal-symbol) · [Sharp horizon and long-stream loss](OBSTRUCTIONS.md#the-sharp-window-length-for-distinguishing-token-actions) · [Exact audit](audit_symbol_depth.py)

~~~powershell
python -B research/frontier/symbol_refinement.py --check research/frontier/symbol_refinement_result.json
python -B research/frontier/audit_symbol_depth.py
~~~

## Training on three tokens and forecasting sixty-four

**EMPIRICALLY OBSERVED.** The learner recovered all six token actions from 262,144 new independent three-token episodes without hidden-state labels or a supplied reset symbol. It then predicted 262,144 tokens in 4,096 fresh episodes of length 64. The previous experiment selected an internal alphabet and fitted a finite-window table. This one fitted and executed a continuing state update. [Frozen registration](https://github.com/alan-ai1196/FP/blob/63f6f8f/research/frontier/NEXT.md) · [Learner and independent computations](permutation_filter.py) · [Receipt and learned probabilities](permutation_filter_result.json)

| Frozen predictor | All 64 positions | Positions 1–3 | Positions 4–16 | Positions 17–64 |
|---|---:|---:|---:|---:|
| Learned scalar posterior | 1.677701 | 1.721194 | 1.696677 | 1.669844 |
| Same fitted probabilities, categorical Bayesian filter | 1.677701 | 1.721194 | 1.696677 | 1.669844 |
| Unrestricted raw order-two Markov model | 1.718568 | 1.721298 | 1.720014 | 1.718006 |
| Fitted unigram | 1.732448 | 1.728010 | 1.734254 | 1.732236 |
| Known source, same observed history | 1.677671 | 1.721192 | 1.696686 | 1.669802 |

Numbers are nats per token. The learner inferred that IDs 2 and 5 flip the state. Exact empirical determinant signs fixed the six actions. The selected prefix/suffix block used IDs 3 and 0. Raw ID 3 supplied a separating eigenbasis with estimated eigenvalue gap 0.250851 and condition number 8.31. No fitted rate hit the probability floor of $1/(2n)$. Twenty-five expectation-maximization iterations on observed token triples then reduced the half-count penalized training NLL by 65.03 nats. Each step conditions on either possible initial state. Both forecasts and the fit use ordinary emitted-token likelihood. The known generator enters only data generation, oracle scoring and post-fit comparison.

The packed filter uses 105 bytes. It stores a bit mask, one binary64 initial probability, and two rows of six binary64 probabilities. Its live log odds use eight bytes per stream. Six precomputed log emission ratios cost another 48 bytes. The independent categorical readout used two probabilities. The raw competitor's 216 uint32 triple counts occupy 864 bytes and can address a prediction with two previous tokens. The fitted model has 11 independent continuous parameters and six action flags before exploiting any additional equalities. The registered acquisition counted 786,432 training tokens, used 216 triple counts, examined 36 possible prefix/suffix pairs, solved six two-dimensional systems and evaluated 216 word types from two candidate starts per EM step. All inference probabilities were computed in binary64. Whole CPU runs took about 0.22–0.25 seconds with an observed peak working set around 54 MB. These are batched reference-code measurements.

For this generator, the exactly renormalized installed binary64 probabilities yield a proved upper bound of 0.000020578 nats per token on the *expected* excess over 64 positions. The largest row normalization correction was below $1.81\cdot10^{-16}$. A realized held-out difference need not fall below its expectation bound. The mean fitted emission KL contribution was at most 0.000020533 nats and the initial-state KL at most 0.000002849 nats per episode. A separate all-swapping example required a product of two distinct letters to identify the hidden axes. Both emission matrices were reconstructed with rational arithmetic. A separate linear-count reconstruction recovered actions, emissions and initial proportions up to state naming in 480 positive rational examples over alphabets of two to five tokens, covering each stay/swap pattern. [General reconstruction and loss proof](FOUNDATION.md#recovering-a-continuing-update-from-three-token-windows)

**FORMALLY VERIFIED.** Lean 4.34.1 checked that substitution invariance in arbitrary left and right contexts is equivalent to a word weight being constant on each encoding fiber. It also checked that quotienting by contextual equivalence preserves every word and gives the coarsest preserving encoding. Instantiating the weight with $P(w)/\prod_iP(w_i)$ supplies the combinatorial step in the fixed-refinement theorem. Its printed axiom reports are propext and, for the quotient construction, Quot.sound. The rank, entropy and statistical arguments have mathematical proofs and separate numerical checks. [Lean source](SymbolContexts.lean)

~~~powershell
python -B research/frontier/permutation_filter.py --check research/frontier/permutation_filter_result.json
python -B research/frontier/permutation_filter.py --moment-audit
& "$env:USERPROFILE\.elan\toolchains\leanprover--lean4---v4.34.1\bin\lean.exe" research/frontier/SymbolContexts.lean
~~~

## How much of a probability clock does learning retain?

**EMPIRICALLY OBSERVED.** Fit and test each used 65,536 independent complete runs, giving 195,859 and 196,290 ordinary tokens respectively. The learner received the public advance/reset interface and raw marks. It chose among all deterministic shared-reset machines at each state budget by fitted likelihood. All 63 competing cycle lengths were evaluated. The comparator with a supplied cosine recurrence estimated all three of its parameters from the same training tape. [Registration](https://github.com/alan-ai1196/FP/blob/e98ce50/research/frontier/NEXT.md) · [Code](probability_clock.py) · [Results and probability intervals](probability_clock_result.json)

| States | Learned cycle | Population-optimal cycle | Held-out learned NLL | Held-out saturated-counter NLL | Best population NLL in this deterministic class |
|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1 | 0.864230 | 0.864230 | 0.863534 |
| 2 | 1 | 1 | 0.853513 | 0.853513 | 0.852996 |
| 4 | 2 | 2 | 0.847407 | 0.847523 | 0.847185 |
| 8 | 7 | 7 | 0.841700 | 0.842867 | 0.841271 |
| 16 | 7 | 7 | 0.841655 | 0.841680 | 0.841222 |
| 32 | 1 | 27 | 0.841662 | 0.841662 | 0.841220 |

The known-source NLL was 0.841638 on the reporting tape and 0.841220 in the population. The learned rotation scored 0.841671 and 0.841258 respectively. With eight states, likelihood bought a seven-step cycle after one transient state. It improved held-out NLL by 0.001167 over saturation at the same state count. With 32 states the longest observed training run contained only 24 advance tokens. Unvisited ages left exact likelihood ties and the registered tie rule selected saturation; the population optima can still be distinguished by bounded logarithms. The small held-out advantage of the fitted 16-state model over the fitted rotation held for these two fits and this tape. The receipt includes the population loss of each fitted model as well.

Each finite layout requires a transient/cycle boundary, its $K$ mark rates, one shared advance rate and a current state in $\lceil\log_2K\rceil$ bits. For these counts a simple reproducible payload can store two layout bytes and $2K+2$ uint32 counts, or $10+8K$ bytes. This formula describes a possible packing. The measured Python reference uses exact integer counts, rational numbers and temporary arrays. It inferred the rotation from 21,845 age-zero and 14,679 age-one marks. Its empirical advance probability, amplitude and cosine are in the receipt. Their unrestricted rational execution has growing denominator length. Model selection and NLL bounds worked on histograms, with a separate actual streaming state update on each reporting tape checking all finite layouts. Whole CPU replays took about one second with an observed working set near 38 MB. No language-text or GPU result is inferred from this three-token source.

**NUMERICALLY VERIFIED.** Integer/rational calculations checked 542 exact stationary word-probability equalities at budgets one through five and distinct probabilities on the first separating example for every tested budget. The exact two-state lower-bound minor and the 104-term stationary cross-entropy calculation with a geometric remainder are reproduced by the same script. **PROVED.** The unrestricted positive-model optimum reduces to marked-run KL over a finite phase-type family. Its global numerical value remains open for $K>1$ in this investigation. The smaller deterministic class has the exact optima reported above. [Loss and acquisition](FOUNDATION.md#exact-and-attainable-prediction-on-a-probability-clock) · [Finite witnesses](OBSTRUCTIONS.md#finite-prediction-windows-can-conceal-an-infinite-positive-state-requirement)

~~~powershell
python -B research/frontier/probability_clock.py --check research/frontier/probability_clock_result.json
~~~

## When prediction pays for compressing a delay

**EMPIRICALLY OBSERVED.** A learner searched 131,072 possible lags in 256 independent raw training windows. The true lag of 258,048 received 223 matching labels and the runner-up received 160. Fitting read 67,109,120 training tokens and made 33,554,432 candidate matches. Three new streams each supplied one warm-up block. Their next 2,064,384, 1,032,192 and 4,128,768 targets fitted the two error probabilities, selected a representation at each price and measured frozen performance, respectively. No deployment kernel could reread an older raw observation after it had been encoded. [Registration](https://github.com/alan-ai1196/FP/blob/be51cdd/research/frontier/NEXT.md) · [Statistical replay](causal_state.py) · [Packed C implementation](delayed_state.c) · [Observed and population intervals](causal_state_result.json)

| Installed predictor | Charged bytes | Raw reporting NLL | Reporting score at $\lambda=0.30$ | Expected score at $\lambda=0.30$ given these fitted rates |
|---|---:|---:|---:|---:|
| Fair forecast | 0 | 0.693147 | 0.693147 | 0.693147 |
| Raw delay ring | 32,274 | 0.376103 | 0.676270 | 0.676938 |
| Hamming-coded ring | 29,312 | 0.398425 | 0.671044 | 0.671581 |

The same selection rule chose raw storage at zero price, coded storage at 0.30, and the fair predictor at 0.40. The coded predictor made 563,275 reporting errors and the raw one 514,679. At the middle price the coded predictor gave up 0.022322 nats in unpriced loss and gained 0.027548 nats from reduced memory, an observed net gain of 0.005226 nats per token. The population column uses the actual frozen calibration probabilities and the analytically known source law. Its coded score beats the 0.676770 lower bound even for binary-linear boundary summaries with arbitrary readouts, ideal calibration and zero control overhead. This is a finite operating point on the general [online memory frontier](FOUNDATION.md#a-sharp-memory-and-prediction-tradeoff-for-a-delayed-stream).

The coded ring keeps 4,096 successive 57-bit indices, or 29,184 payload bytes. The raw ring keeps 32,256 payload bytes. The price includes respectively 128 and 18 additional bytes as registered. The C encoder calculates the six syndrome bits, conditionally corrects a bit, and writes the systematic part to the slot. Its decoder reconstructs one prototype for 63 forecasts. The evaluator counts mismatches under a frozen normalized Bernoulli readout, so the timed kernel measures retrieval, update and scoring comparisons. It avoids materializing probability vectors or logarithms for each token. A separate reference recalculated predictions from raw microblocks. Both native models reproduced every aggregate count on all three full streams and nine short inputs with unaligned bit offsets, partial final groups and raw remainders.

**MEASURED ON CPU.** MSVC x64 14.52, optimization /O2, Ryzen 7 5800X. On the complete reporting tape including warm-up, six replay timings were 0.454–0.580 ms with raw storage and 3.134–3.959 ms with coded storage. Encoding slowed the kernel by about sevenfold in the typical replay. The portable Python data-generation, fitting and verification run took about 0.33 seconds with an observed peak process working set of 48 MB. Kernel timers exclude data generation, compiling, ring allocation and probability calibration.

There is a consequential physical reversal. The native library grew from 103,936 to 105,472 bytes on disk when the coded kernel was added. Executable-section size grew by 1,264 bytes and read-only data by 88 bytes. If all 1,536 additional file bytes are charged to one stream at the same exchange rate, the coded score gains a further **0.014286** nats of cost and loses to the raw ring. Sharing those extra bytes equally across three simultaneous streams reduces the increment below the measured memory advantage. The extra CPU time persists. The result specifies the storage price, the chosen deployment convention and the measurements needed to use another convention. Binary size and timings can change with compiler options and hardware.

**NUMERICALLY VERIFIED.** Independent exact checks covered all 374 binary-linear subspaces in five dimensions, computing joint noise-cell probabilities and the entropy bound. Enumeration of every short binary window for 55 pairs of candidate lags verified the uniform forest-edge law used in the identification proof. Lean 4.34.1 checked that translation-invariant cells of Boolean histories are cosets of an addition-closed kernel; both axiom reports list propext and Quot.sound. The MGL inequality, online construction and physical price comparisons are separate arguments. [Independent exact checks](audit_causal_state.py) · [Lean source](CausalState.lean)

~~~powershell
python -B research/frontier/causal_state.py --check research/frontier/causal_state_result.json
python -B research/frontier/causal_state.py --native --check research/frontier/causal_state_result.json
python -B research/frontier/audit_causal_state.py
& "$env:USERPROFILE\.elan\toolchains\leanprover--lean4---v4.34.1\bin\lean.exe" research/frontier/CausalState.lean
~~~

The optional native replay builds raw-only and combined libraries in a temporary directory. It uses the available Visual Studio x64 C toolchain on Windows, or a C11 compiler on POSIX. It reports fresh kernel timings and library sizes outside the deterministic statistical receipt.

## Learning the packed update from next-bit errors

**EMPIRICALLY OBSERVED.** The 57 free columns of a $6\times63$ systematic check matrix all started at zero. Training on 262,144 history/target group pairs made every column distinct and nonzero, producing a perfect code with different coordinate assignments from the conventional designer. Each group pair supplied 63 ordinary binary prediction targets. No ideal column, correction label or clean future was exposed to selection. Training received the six fixed pivots, nearest-kernel encoding, and the previously fitted lag 258,048. The conventional designer maximized the uniform-source geometric objective and reached the same covering radius of one. [Prospective registration](https://github.com/alan-ai1196/FP/blob/491388e/research/frontier/NEXT.md) · [Implementation](learned_code.py) · [Columns, training path, predictions and prices](learned_code_result.json)

The training data comprise 64 independently restarted two-block episodes, or 33,030,144 observed tokens beyond the earlier lag-identification run. Each greedy designer tried 3,648 column assignments. The empirical search accumulated 941,359,104 signed per-coordinate observations across the 57 steps. Sums grouped by current syndrome and the proposed column's input bit give exact error counts for each candidate. The final grouped count of 2,257,968 training errors matched a separate reconstruction on the original arrays. Fresh conditional-rate calibration, model selection and reporting used respectively 2,064,384, 1,032,192 and 4,128,768 targets. Every stream had its own unscored warm-up block.

| Frozen predictor | Distinct nonzero columns | Charged bytes | Reporting nats/token | Reporting score at price 0.30 | Exact population mismatch |
|---|---:|---:|---:|---:|---:|
| Fair | — | 0 | 0.693147 | 0.693147 | 1/2 |
| Raw ring | — | 32,274 | 0.376533 | 0.676701 | 1/8 |
| Six pivots and zero free columns | 6 | 29,440 | 0.440468 | 0.714278 | 9/56 |
| Random columns | 38 | 29,440 | 0.407213 | 0.681022 | 95/672 |
| Empirically learned columns | 63 | 29,440 | 0.398592 | 0.672401 | 35/256 |
| Conventional geometric designer | 63 | 29,440 | 0.398616 | 0.672426 | 35/256 |
| Supplied Hamming routine | 63 | 29,312 | 0.398927 | 0.671546 | 35/256 |

Training improved held-out loss by **0.041877 nats per token** relative to its initialization at the same storage. The learned array made 563,647 reporting errors, compared with 662,592 for its initialization and 563,704 for the geometric designer. Their small observed difference is compatible with identical theoretical mismatch. Learning paid for the nonlinear correction relative to raw storage at price 0.30, with a frozen population score of 0.672772. When the smaller supplied implementation also competed, selection chose raw at price zero, supplied Hamming at 0.30 and fair at 0.40. On this symmetric source the final population objective cannot select a uniquely named useful assignment. The counting theorem establishes optimality among arbitrary encoders and causal decoders only for the common-confidence observer. [Theorem and equality conditions](FOUNDATION.md#when-ordinary-prediction-constructs-a-perfect-code)

**MEASURED ON CPU.** The general C implementation takes the literal 63 installed columns and 64 one-byte predecessor entries. It builds six 64-bit masks and uses a packed ring of 29,184 bytes. The 256-byte overhead allowance includes those tables, masks and fixed-width controls. It predicts each group before reading its new bits. A separate NumPy implementation retained the raw groups for verification. The packed kernels matched every error total on all three full streams plus nine short and partial cases. On an AMD Ryzen 7 5800X, MSVC x64 14.52 /O2, five reporting-tape replays took 0.413–0.439 ms raw, 2.574–2.593 ms with the learned matrix, 2.586–2.599 ms with geometric columns, and 3.100–3.126 ms for the supplied routine. The timings cover packed prediction, observation and mismatch counting. A full statistical rerun with both designers took 4.76 s and reached 138.1 MB process working set.

The general library occupied 105,472 file bytes against 103,936 raw-only. Its executable section grew by 1,392 bytes. At the same per-bit exchange rate, charging the 1,536 incremental file bytes to a single stream adds 0.014286 nats per token. That exceeds the learned model's 0.004299 advantage over raw under the table-and-ring charge. Sharing just those extra executable bytes over four streams would bring them below this margin. CPU time and one-time acquisition remain separate. A conventional implementation can obtain the exact same population mismatch by assigning all nonzero columns directly.

**NUMERICALLY VERIFIED.** Independent nearest-center enumeration on every one of the 4,096 systematic seven-bit matrices checked the error corrections, the optimum and the strict missing-column preference on all 41 distinct reachable prefixes. All 1,024 choices of a three-step adaptive binary forecast tree and a fixed noise trajectory gave exactly the binomial histogram of clean mistakes. Three-input truth-table enumeration checked the coordinate-descent obstruction. Lean 4.34.1 verified the two inverse identities and length preservation underlying the causal count, each with axiom report propext. [Formal source](CausalState.lean) · [Native implementation](delayed_state.c) · [Local-training obstruction](OBSTRUCTIONS.md#a-strict-local-training-move-can-be-unable-to-create-the-correction)

~~~powershell
python -B research/frontier/learned_code.py --audit
python -B research/frontier/learned_code.py --check research/frontier/learned_code_result.json
python -B research/frontier/learned_code.py --native --check research/frontier/learned_code_result.json
~~~

## Learning a shared bit of three text tokens

**EMPIRICALLY OBSERVED.** On the registered FineWeb-Edu training stream, 128 candidate Boolean functions covered every way to split three binary history observations, up to exchanging the output names. The learner chose table 170, which simply returns the newest of the three frequency bits. On the 131,072 subsequent reporting targets it made exactly the same full-vocabulary forecasts as the independently selected direct copy. An extra installed table byte slightly increased its price. The sparse raw-token trigram won by 0.000146 nats per token with 12 fewer bits than the learned table. The registered criterion failed. [Frozen protocol](https://github.com/alan-ai1196/FP/blob/0680d73/research/frontier/NEXT.md) · [Execution](text_statistic.py) · [Scores, sample identity and automaton](text_statistic_result.json)

| Frozen predictor | Extra bits | Reporting nats/token | Reporting nats/token with price |
|---|---:|---:|---:|
| Smoothed successor | — | 7.156115 | — |
| Calibrated successor | 0 | 7.152637 | 7.152637 |
| Learned history table | 28,936 | 7.150433 | 7.151031 |
| Selected direct copy | 28,928 | 7.150433 | 7.151030 |
| Sparse complete three-bit history | 28,936 | 7.150987 | 7.151585 |
| Raw-token trigram | 28,924 | 7.150287 | 7.150885 |

The common model scored all 50,257 possible tokens through a normalized conditional distribution. Its successor table used 346,854 observed pairs and a 244-type frequency group. The three candidate input bits were the group memberships two, three and four token positions before the target. The most recent raw token addressed the readout. Calibration and row purchase each used 131,072 early targets. Selection scored each table on targets 1,310,720–1,441,791, for 16,777,216 candidate-target evaluations. Reporting used targets 1,441,792–1,572,863 after all tables, readouts and comparator budgets were frozen. The selected table used 723 five-byte rows, one table byte and one live byte. Its minimal online automaton has two states. The complete-history comparator bought 904 exception cells and the raw trigram bought 657. All three used the same calibration and purchase data. The acquisition comparison is CPU-only and uses a later continuation of the training file.

**POST HOC.** All 124 previously fitted maps depending on at least two inputs also lost to both the copy and the raw trigram on the reporting block. The best such map by hindsight was table 42, at 7.151474 including its 30,976-bit price. Thus selecting the wrong finalist cannot explain this particular result among those frozen fits. This conclusion concerns the three frequency bits and their trained conditional readouts.

A separate calibration-only check compared the eight empirical joint distributions of current raw token and binary target. A line segment between histories 5 and 6 achieved a maximum total-variation residual of 0.526888 across 20,331 occupied joint coordinates. Floating-point weighted medians located candidate projections and integer counts verified the eight resulting distances exactly. The residual gives no informative near-line guarantee for binary-target loss here. The five distinct threshold partitions in the resulting order included table 170. Their best unpriced, unconstrained empirical conditional entropy was 0.448910 nats per *binary* target. The best of all 128 empirical partitions was table 204 at 0.446220. These retrospective quantities describe binary group prediction with empirical cell readouts on calibration data. The registered score evaluates full raw-token probabilities on held-out data. Sampling noise and current-token frequency can both contribute to the measured residual. [Conditional geometry and its assumptions](FOUNDATION.md#when-one-predictive-bit-can-be-learned-by-sorting)

**VERIFIED.** A scalar execution initialized from the reporting prefix, took the minimal automaton transitions, and rebuilt the selected raw-token probability at all 131,072 positions. It matched the vectorized histogram and outward-rounded NLL. Exhaustion of all 256 named Boolean maps, eight starting histories and all two-step-or-shorter continuations checked every quotient. Exactly 16 maps needed all eight online states. A statistical rerun with the hindsight comparison took 8.25 seconds and peaked at 187.6 MB process working set on the Ryzen 7 5800X. Adding the calibration geometry check took the total to 9.39 seconds and 188.4 MB.

The separate complexity audit generated 86 graph channels including every labeled graph on two and four vertices. It independently computed optimized log loss for 2,116 binary partitions using categorical counts, positive smoothed counts and the queried binary target. Outward log intervals checked the private-token/edge entropy identity and the separation from every wrong cut. Another 3,072 partitions with unequal history weights checked the affine-line threshold result against full search. These are finite checks of the [general reduction](OBSTRUCTIONS.md#acquiring-one-predictive-bit-can-encode-minimum-bisection). [Audit](audit_predictive_split.py)

~~~powershell
python -B research/frontier/text_statistic.py --audit
python -B research/frontier/text_statistic.py --check research/frontier/text_statistic_result.json
python -B research/frontier/audit_predictive_split.py
~~~

## Learning a raw token address from full-vocabulary loss

**EMPIRICALLY OBSERVED.** On the pinned FineWeb-Edu training file, the location $x_{t-2}$ supplied an earlier raw token. The run learned which of two fitted full-vocabulary forecasts to use after seeing $x_{t-1}$. The initial address was a frequency split with 244 types on one side. The two forecasts each learned masses for 512 common output types plus a pooled tail on 262,144 raw targets. After freezing them, the learner saw 524,288 more ordinary targets to buy address changes and used a later 131,072 targets to select its format and regularization. The following 131,072 targets were held out. The shared bigram, trained on the first 786,432 tokens, and its counts are common costs. Each additional installed or live bit costs $(\ln 2)/256$ nats per reporting block. [Prospective registration](https://github.com/alan-ai1196/FP/blob/afc26fc/research/frontier/NEXT.md) · [Reproducible receipt](text_addresses_result.json)

| Frozen predictor | Extra installed and live bytes | Held-out nats/token | With storage price |
| --- | ---: | ---: | ---: |
| Raw bigram | 0 | 7.118319 | 7.118319 |
| Pooled fitted output probabilities | 2,584 | 7.076232 | 7.076659 |
| Supplied frequency address, two fitted readouts | 4,121 | 7.074604 | 7.075285 |
| Address learned from conditional forecasts | 6,159 | 7.073369 | 7.074387 |
| Address learned from backoff probabilities alone | 6,203 | 7.073224 | 7.074249 |
| Raw trigram, selected whole context rows | 6,155 | 7.110241 | 7.111258 |
| Raw trigram, all rows | 10,092,941 | 7.152414 | 8.820365 |
| Raw trigram with fitted pooled backoff, later comparison | 6,159 | **7.071004** | **7.072022** |

The conditional learner changed **1,019 token addresses**, affecting 17,373 reporting positions. Its selected regularization was one root sum of squared observed log ratios. The installed map used two-byte exceptions to the frequency split and one live byte. It improved priced NLL by 0.000898 over the seed, meeting the registered formation criterion. The query-ignoring assignment won the separate comparison on this block by 0.000138. Both deployed forecasts still condition on the current raw token. Selection had favored the query-aware assignment. Most of the large gain over the raw bigram came from fitting the pooled output probabilities, which alone saved 0.042087 unpriced nats/token.

**Post hoc comparison.** The registered raw trigram inherited the original unigram backoff. After observing its score, we gave the same conventional raw-context learner access to the fitted output probabilities and charged for them. All nine choices of constant backoff and trigram smoothing used the original acquisition and selection targets. The winning model combines pooled calibration with 118 context rows and 358 successor counts at smoothing mass 64. The same 6,159-byte allowance includes its two-byte live raw-history register. It beat the conditional address by 0.002365 nats/token at equal storage. The unchanged model goes forward to a later block for a prospective comparison. The primary formation result identifies a useful learned distinction within the two-readout family. The stronger conventional comparison changes which implementation one would select.

**Execution and acquisition.** A scalar reference advanced the saved address sequentially and rebuilt every observed probability from integer masses. Separately compiled C and CUDA kernels scored the packed models and matched all per-token FP64 losses within $10^{-11}$ for all eight arms. An exhaustive seven-type check covered all 128 binary maps, their serialized readouts and normalization. Independent brute force checked 891 small integer knapsacks. Training visited 16.75 million DP cells across the three originally registered raw-trigram smoothings. A complete rerun including the calibrated comparator, scalar checks and selection took 3.07 seconds and reached 195.6 MB process working set on the Ryzen 7 5800X.

For 131,072 targets, five warm sequential MSVC x64 CPU replays took 10.82–11.02 ms for the learned conditional address, 8.17–8.24 ms for the supplied seed and 10.62–10.82 ms for the calibrated trigram. The same data and model bytes resident on an RTX 3090 took 0.0523–0.0537, 0.0501–0.0603 and 0.0490–0.0501 ms per teacher-forced batch respectively. Each GPU sample averaged ten identical launches with one thread per target. The shared lookup arrays occupy 2,684,212 bytes, the token input occupies 262,148 bytes and the FP64 loss output occupies 1,048,576 bytes. These timings cover observed-token scoring with hot resident data. Sequential generation, host transfer, materializing 50,257 probabilities per position and one-time acquisition require different work. All arms used the same compiled benchmarking binary. [Learning and scalar reference](text_addresses.py) · [Conventional row purchase](packed_trigram.py) · [Native kernel](address_score.c)

~~~powershell
python -B research/frontier/text_addresses.py --check research/frontier/text_addresses_result.json
python -B research/frontier/measure_addresses.py --gpu
~~~

## How much extra prediction did fractional addresses buy?

**EMPIRICALLY OBSERVED.** Before examining any target beyond position 1,835,007 we froze the preceding predictors and registered a five-level mixture, a calibrated raw-count competitor and two conventional quality references. Every compact arm used the original acquisition and validation data. The reporting stream comprised four consecutive blocks of 131,072 later FineWeb-Edu targets. The price in the table is charged for a separate deployment on each block. The pooled bigram and all history-based models share 2,684,212 bytes of base lookup arrays. [Registration](https://github.com/alan-ai1196/FP/blob/ed60c61/research/frontier/NEXT.md) · [All four block scores](mixture_addresses_result.json)

| Frozen model | Extra bytes including live state | Mean nats/token | With storage price |
| --- | ---: | ---: | ---: |
| Raw bigram | 0 | 7.055915 | 7.055915 |
| Pooled fitted bigram | 2,584 | 7.020567 | 7.020994 |
| Best constant fraction | 2,584 | 7.020391 | 7.020818 |
| Supplied frequency address | 4,121 | 7.020021 | 7.020702 |
| Conditional learned bit | 6,159 | 7.018466 | 7.019484 |
| Backoff-only learned bit | 6,203 | 7.018288 | 7.019313 |
| Five-level learned fraction | 6,158 | 7.017841 | 7.018859 |
| Budgeted raw trigram | 6,155 | 7.046408 | 7.047425 |
| Calibrated raw trigram | 6,159 | **7.013757** | **7.014775** |

The conditional bit beat its seed on all four blocks. The fraction map beat the conditional bit on all four, saving another 0.000625 priced nats/token. The calibrated trigram beat the fraction on all four by a mean of 0.004084. Selection chose the original frequency default and 679 three-byte exceptions, the maximum at this cap. The per-type regularizer was one root sum of squared improvements. The assigned intermediate weights $1/4,1/2,3/4$ went to 31, 39 and 56 raw token types respectively, accounting for **149,436 of the 524,288** subsequent predictions. Both pure endpoints and intermediate values shared the same learned output rows. The calibrated trigram retained its original 118 contexts and 358 successor counts with no refitting.

**NUMERICALLY VERIFIED, retrospective endpoint comparison.** Freeze the 126 types assigned an intermediate fraction and freeze all other predictions. Give a hard competitor the option of selecting its better endpoint separately for each of these 126 types *after* observing all four reporting blocks. The fitted fractions still saved between 89.221017010 and 89.221017011 total nats over that competitor. Only 37 of the 126 types individually beat both endpoints. This proves a gain from interpolation on these positions even after giving the endpoint selector hindsight. A competitor allowed to change assignments outside those 126 types is a different comparison. The numbers above compare models fitted entirely before deployment. [Outward-rounded audit](address_precision_bounds.json)

**Conventional quality references.** For the first 4,096 targets of each block, every predictor was scored on the same 16,384 positions. The five-gram received the previous four actual tokens and the Transformer its last 256. Both checkpoints were fitted on the first 1,048,576 training positions and selected on the earlier validation file. The selected Transformer training run made 16,777,216 target presentations. Its 7,253,376 FP32 parameters occupy 29,013,504 loaded bytes and its saved checkpoint occupies 54,753,065 bytes. The KenLM model file occupies 34,489,589 bytes. The Transformer used FP16 autocast and a full-vocabulary FP64 log-sum-exp. KenLM used the original complete-real-alphabet normalization with its unknown mass divided across unseen IDs. The comparison below uses unpriced NLL. These models have different training and memory budgets. [Frozen checkpoint identities and scores](address_anchors_result.json) · [Reproduction](address_anchors.py)

| Same 16,384 targets | Mean nats/token |
| --- | ---: |
| Conditional learned bit | 7.050888 |
| Five-level learned fraction | 7.049097 |
| Calibrated raw trigram | 7.040384 |
| Optimistic bound for any mixture of the two conditional forecasts | 7.016097 |
| Modified Kneser–Ney five-gram | 6.603733 |
| Transformer | 6.231090 |

**PROVED for this readout family and these targets.** Even access to the correct next token when picking the mixture cannot give more mass than the larger of the two forecasts on that token. Summing outward-rounded logs of the exact integer probabilities bounds the mean of this hindsight envelope in $[7.016096671,7.016096672]$. Hence these fixed conditional readouts cannot reach either larger baseline on the panel, regardless of the encoder's history length, number of states, learned assignments or fraction precision. The optimistic envelope can choose different endpoint forecasts for different possible outcomes of the same history and so supplies a lower bound on achievable NLL. [Arithmetic proof](PredictiveMixture.lean) · [Full-alphabet audit](audit_address_precision.py)

**Physical and mathematical checks.** All four blocks were replayed from packed three-byte exceptions and one live byte. A scalar integer-mass reference and separate native CPU and GPU scorers agreed with the vectorized per-token losses to $10^{-11}$. Native sequential CPU replays of all 524,288 positions took 48.39–55.74 ms for fractions, 46.60–48.31 ms for the learned bit and 43.25–45.29 ms for calibrated trigram counts. Warm teacher-forced RTX 3090 device batches took 0.1567–0.1669, 0.1564–0.1574 and 0.1579–0.1959 ms respectively. Each device thread used the two actual preceding tokens. The mixture kernel looks up the 512-entry output table once and blends integer masses before scoring. The benchmark returns the observed log loss per target. A full acquisition and four-block statistical rerun took 3.81 seconds and peaked at 216.7 MB process working set.

The separate precision audit checked 2,288 normalized binary examples using exact rational probabilities and outward log intervals, including 572 exact equalities for the worst-case pair. It checked sparse grid purchase against 108 exhaustive searches and verified full-vocabulary mass exactly for all five grid settings at three text query rows. Lean 4.34.1 checked the per-row integer-mass envelope and its product over arbitrary finite sequences. The real-variable precision theorem has a separate analytic proof. [Sharp precision theorem](FOUNDATION.md#how-much-precision-can-a-history-distinction-use)

~~~powershell
python -B research/frontier/mixture_addresses.py --check research/frontier/mixture_addresses_result.json
python -B research/frontier/audit_address_precision.py --text --check research/frontier/address_precision_bounds.json
python -B research/frontier/address_anchors.py --check research/frontier/address_anchors_result.json
python -B research/frontier/measure_addresses.py --precision --gpu
& "$env:USERPROFILE\.elan\toolchains\leanprover--lean4---v4.34.1\bin\lean.exe" research/frontier/PredictiveMixture.lean
~~~

## Learning which output probability to change

**EMPIRICALLY OBSERVED.** We allowed the learner to change the odds of one raw output of the pooled bigram. It searched all 50,257 output IDs using ordinary full-vocabulary prediction errors and 513 supplied earlier-history classes (the 512 shared named token IDs and the rest). Within each class it subtracted the base forecast's expected count of the candidate from the observed count. The criterion was the between-history variance of these residual means after subtracting the global mean. It selected GPT-2 token **286, “ of”**, with score 0.0006168403, ahead of token 11, the comma, at 0.0002755152. The selected identity came from the data. The mechanism for a single multiplicative correction, the input classes and the allowed multipliers were supplied. [Prospective registration](https://github.com/alan-ai1196/FP/blob/218c31e/research/frontier/NEXT.md) · [Implementation](output_correction.py)

Acquisition used the original 524,288 purchase targets. The 513-by-50,257 candidate calculation accumulated observed and expected counts using sparse history/query and query/successor tables, processing 512 output columns at a time. There were 122,592 occupied history/query pairs and 152,729 occupied history/target pairs. Separate direct per-observation sums checked both leading column scores. The best fitted global multiplier for “ of” was 1.5. Validation selected a dense table of one-byte responses, with 307 history classes assigned a different multiplier. It used all nine possible values from $1/4$ to $4$. The stored correction takes eight header bytes and 513 response bytes, plus one live byte above the 2,584-byte pooled readout. The default and conditional models each normalize the entire categorical forecast.

| Frozen forecast | Extra bytes above the raw bigram | Mean NLL | With storage price |
| --- | ---: | ---: | ---: |
| Pooled calibrated bigram | 2,584 | 7.172206 | 7.172633 |
| Global multiplier for “ of” | 2,592 | 7.170181 | 7.170609 |
| Learned history-dependent multiplier | 3,106 | **7.166181** | **7.166694** |
| Calibrated trigram at the same cap | 3,105 | 7.167733 | 7.168246 |
| Earlier learned five-level address | 6,158 | 7.168160 | 7.169178 |
| Earlier calibrated trigram at the larger cap | 6,159 | **7.160583** | **7.161601** |

**Two new blocks.** Frozen models scored targets $[2359296,2621440)$. The conditional correction beat its global multiplier and the matched raw trigram in each block. The matched trigram bought 19 contexts and 47 successors. The mean priced advantage over that model was 0.001552 nats/token. The earlier calibrated trigram with 118 context rows scored 0.005093 lower than the correction at its larger allowance. A total of 216,569 positions used a response different from the learned global multiplier. At 101,716 of 262,144 targets, the issued probability was more than $10^{-12}$ outside the interval spanned by the earlier two conditional forecasts **and** the pooled base on that outcome. A mixture of those three forecasts cannot reproduce these values. The two larger conventional quality anchors were measured on the preceding study's prespecified subpanels. [All model choices and block scores](output_correction_result.json)

**Post hoc current-token control.** To check how much of the gain needed the earlier token, we trained an equally sized correction that can read only the current query. Its own residual search selected token 13. The original validation data chose token 286 when it could also use the earlier learner's candidate. It required no extra live byte and scored 7.170379 priced nats/token on the two reporting blocks, above the earlier-history model's 7.166694. The native scorer verified both data accesses separately.

**Execution cost.** Each modified forecast can look up the selected token's base probability and the observed token's base probability in the original bigram. They coincide when the selected token is observed. A response of one skips the extra lookup in the native scorer. The installed table uses the named token list already stored for the calibrated output. An independent scalar decoder rebuilt the integer denominators at every reporting position. It also checked all 50,257 output masses for three query rows and all nine multipliers. A complete rerun including acquisition, both raw competitors, the later current-only control and scalar verification took 6.39 seconds and reached 266.8 MB process working set.

Five warm sequential MSVC CPU passes on 262,144 targets took 31.67–31.85 ms with the selected correction and 21.01–22.43 ms with the matched trigram. Teacher-forced RTX 3090 device passes took 0.1163–0.1177 ms and 0.0856–0.0869 ms respectively. C, CUDA and the vectorized reference agreed within $10^{-11}$ per target. These are resident-data observed-token timings. The 0.001552-nat gain pays the stated byte rent. Execution time is a separate tradeoff. The independent mathematical audit verified the sign-sweep construction and a quantized finite-step loss certificate on 128 positive probability tables, and the strongest-direction reduction on 70 graph channels. [General learning law](FOUNDATION.md#learning-a-new-output-direction-from-prediction-error) · [Exact small controls](audit_output_correction.py)

~~~powershell
python -B research/frontier/audit_output_correction.py
python -B research/frontier/output_correction.py --check research/frontier/output_correction_result.json
python -B research/frontier/measure_addresses.py --correction --gpu
~~~

## Can a state learned from one word predict other words?

**EMPIRICALLY OBSERVED.** A history map learned from the single feedback bit “was the next token ‘ of’?” improved predictions of which word occurred within two disjoint groups on new natural text. This held at the larger adaptation budget. At the smaller budget a global correction was better in both groups. A conventional rank-one model trained on the destination groups beat reuse at the larger budget. [Frozen registration](https://github.com/alan-ai1196/FP/blob/45f3338/research/frontier/NEXT.md) · [Acquisition and scoring](text_shared_state.py) · [Block scores and installations](text_shared_state_result.json)

The earlier study supplied GPT-2 token 286 as the source question. The new learner received 262,144 disjoint triples through a censored interface, then 65,536 separate selection examples. Its inputs were the earlier raw token, the pooled bigram's current probability of token 286 and a bit. Even the next source training context could not reveal the preceding example's hidden target because the triples did not overlap. There were 6,752 and 1,565 source hits. Of 50,257 raw types, the frozen encoder assigned 49,684 the default multiplier 1.5 and stored 573 exceptions in 1,437 bytes. The nine multipliers and the lookup operation were supplied. The assignments were fitted. On the 524,288 reporting positions, the source alone scored 7.065680 nats/token, the constant source correction 7.069252 and the pooled base 7.070404. Mean source binary NLL was 0.072982 with the learned map and 0.076554 with its fitted constant.

The destinations were interleaved frequency ranks among the eight most common other outputs in the prior fit. Group 1 comprised comma, period, newline and “ a”. Group 2 comprised “ the”, “ and”, “ to” and “ in”. Each head redistributed probability within its four-word group, preserving group mass. The two destination fitting budgets supplied 1,424 and 1,202 eligible fit labels at 16,384 raw adaptation targets, and 22,088 and 18,777 at 262,144 raw targets. Each budget reserved its last quarter for selection. All compact models scored the same four consecutive blocks $[3866624,4390912)$, with 60,301 and 48,492 group events. The following joint scores include the same independently learned source correction. The original rent is $(\ln2)/256$ nats per installed or live bit over a 131,072-target deployment.

| Destination readout | Joint priced NLL at 16,384 | Joint priced NLL at 262,144 | Within group 1 at 262,144 | Within group 2 at 262,144 | Destination / joint bytes at 262,144 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Global calibration | **7.067496** | 7.066228 | 0.788569 | 0.785560 | 2,628 / 4,066 |
| Reuse the frozen source map | 7.068203 | 7.065398 | 0.786615 | 0.778848 | 4,162 / 4,162 |
| Fixed token-frequency code | 7.069096 | 7.065730 | 0.787646 | 0.781065 | 2,777 / 4,214 |
| Jointly fitted rank-one correction | 7.069085 | **7.064644** | **0.784287** | 0.773607 | 2,713 / 4,150 |
| Separately fitted codes | 7.067687 | 7.064898 | 0.786942 | **0.772905** | 2,796 / 4,234 |
| Raw context counts | **7.067496** | 7.066035 | 0.786753 | 0.783009 | 4,151 / 5,588 |

At the larger budget, reuse beat global calibration on both groups in each block, beat its frequency control in three of four blocks on joint priced NLL, and lost to both directly fitted alternatives in all four on that measure. Reuse saved 0.000830 priced nats per raw token against global calibration. It lost 0.000754 to the rank-one model, which used 12 fewer joint bytes. Against global calibration at the smaller budget, reuse lost 0.000707. The raw competitor could use an additional 1,048,576 historical fully labeled tokens. It bought 117 group/context rows at the larger budget and zero at the smaller one. The larger anchors scored the first 4,096 targets of each reporting block. On these 16,384 positions the joint reuse model scored 7.052090, rank-one 7.051498, the modified Kneser–Ney five-gram 6.668466 and the Transformer 6.325342. The two anchors used their historical checkpoints and full-alphabet conventions. [Checkpoint identities and scores](shared_anchors_result.json)

**Physical and independent checks.** The common CSR bigram takes 2,684,212 bytes. The joint reuse model adds the 2,584-byte pooled readout, a 12-byte header, the 1,437-byte map, two 64-byte heads and one byte to persist the distinct history states. Native arithmetic uses machine registers and the GPU batch reconstructs each state from its input token. The source-only installation costs 4,034 bytes. All 27 budget/readout configurations were decoded from packed bytes in separate native CPU and GPU scorers. Each agreed with the Python reference within $10^{-11}$ at every reporting target. Five warm sequential CPU passes took 83.10–85.49 ms for joint reuse, 90.43–91.67 ms for rank-one and 84.63–88.83 ms for raw counts at the larger budget. Teacher-forced RTX 3090 device batches took 0.5547–0.6079, 0.8317–0.8605 and 0.5331–0.5419 ms respectively. Those timings produce the observed log score with resident data. Repeating the statistical experiment, including both acquisitions, held-out scoring and receipt comparison, took 7.04 seconds and reached 252.1 MB working set. [Initialization, optimization and packet format](shared_readout.py) · [Native scorer](shared_state_score.c) · [Timing samples](shared_state_timing.json)

The rational audit checked commuting corrections, exact normalization and the per-target product identity on 576 finite examples. It enumerated all 50,257 output base masses at four real contexts, including two purchased raw rows, and checked the simultaneous predictions of six readouts at each. It decoded ten different maps across the whole input vocabulary, checked consistent relabeling of the acquired state and verified invariance of source inputs after rewriting concealed labels. Exact rational checks of the conventional rank-one decoder use its realized binary64 weights. [Exact audit](audit_shared_state.py) · [Transfer criterion and scope](FOUNDATION.md#when-does-a-history-statistic-transfer-to-a-new-prediction)

~~~powershell
python -B research/frontier/text_shared_state.py --check research/frontier/text_shared_state_result.json
python -B research/frontier/audit_shared_state.py --text
python -B research/frontier/address_anchors.py --shared --check research/frontier/shared_anchors_result.json
python -B research/frontier/measure_shared_state.py --gpu
~~~

## Learning unfamiliar action meanings from purchases

**EMPIRICALLY OBSERVED.** In eight unfamiliar simulated environments, each word group had its own hidden mapping from four ticket names to four words. A purchase revealed one match bit and paid that bit minus the price. Passing gave no outcome feedback. After 512 opportunities per group, each of seven word-informed priors had recovered every one of the 16 mappings by maximum posterior weight. At eight opportunities, the same transferred state that earned more ticket reward than global calibration chose the single winning ticket less accurately. [Prospective registration](https://github.com/alan-ai1196/FP/blob/f912975/research/frontier/NEXT.md) · [Environment and blinded learning interface](text_ticket_actions.py) · [All budgets, menus, environments and block differences](text_ticket_actions_result.json)

On the pinned text tape, 32,768 nonoverlapping triples starting at 4,390,912 provided 3,922 and 3,001 eligible group opportunities. The learner used only the first 0, 8, 64 or 512 per group. Every subsequent evaluation used the next four blocks of 65,536 disjoint triples, giving 55,677 eligible decisions in each environment. The environment announced the group and exposed the two earlier tokens and one priced ticket. Offers used independent pseudorandom streams for acquisition and evaluation. The learner knew the possible permutations and the pretrained word forecast. A separate ridge competitor learned reward directly from the same purchased bits and current-token features. The text, eligibility and word identities were shared across the eight replications. The replications varied hidden names and menus.

During primary acquisition one quarter of offers had the floor price $1/32$. Remaining prices and all reporting prices were log-uniform on $[1/32,29/32]$. Rewards below are per eligible held-out opportunity, averaged over the eight environments. “Integrated” averages over possible deployment menus conditional on the actual word. Single-choice accuracy uses the same acquired probabilities to choose one name with no price offer. Equal probabilities choose the lowest name.

| Word prior or reward learner | Opportunities per group | Realized reward | Integrated reward | Single-choice accuracy | Correct MAPs / 16 |
| --- | ---: | ---: | ---: | ---: | ---: |
| All posterior means before feedback | 0 | 0.089763 | 0.089422 | 0.190541 | 0 |
| Global conditional heads | 8 | 0.108380 | 0.108245 | 0.452348 | 3 |
| Reused source state | 8 | 0.108885 | 0.108803 | 0.429500 | 3 |
| Directly fitted rank-one prior | 8 | 0.109143 | 0.108997 | 0.455291 | 2 |
| Direct reward ridge | 8 | 0.090841 | 0.090417 | 0.333506 | — |
| Reused source state | 64 | 0.129922 | 0.129750 | 0.623783 | 12 |
| Global conditional heads | 512 | 0.132598 | 0.132370 | 0.653663 | 16 |
| Reused source state | 512 | 0.132822 | 0.132679 | 0.655872 | 16 |
| Directly fitted rank-one prior | 512 | 0.133212 | 0.132954 | 0.656555 | 16 |
| Separately fitted codes | 512 | 0.133217 | **0.133013** | **0.659159** | 16 |
| Direct reward ridge | 512 | 0.130180 | 0.129994 | 0.639472 | — |

With eight opportunities per group, reuse gained 0.000505 actual reward over global calibration while losing 2.285 percentage points of single-choice accuracy. At 512 it gained 0.000223 actual reward, 0.000309 integrated reward and 0.221 percentage points of accuracy. Its actual reward advantage was positive in seven of eight environments and all four text blocks. The rank-one prior then beat reuse by 0.000390 actual and 0.000275 integrated reward. Separately fitted codes had the highest integrated reward. The transferred policy bought 613.5 of 1,024 acquisition offers on average, with 222 hits. Its integrated reward was within 0.0000002 of its counterpart given the true mapping. At eight opportunities that gap had been 0.023876. No full target label was returned by a purchase. A correct bit can implicitly identify the word once the mapping is known.

The coverage intervention changed acquisition. At eight opportunities, rank-one with no guaranteed purchases averaged 9.75 buys across both groups, recovered 2/16 mappings and earned 0.107504 integrated reward. Guaranteeing all purchases gave 16 buys, 5/16 mappings and 0.114973 reward on the common deployment menu. At 64 opportunities the recovery counts for exploration fractions 0, 1/4 and 1 were 12, 10 and 11. A stronger coverage guarantee alone gave no monotone finite-sample recovery ordering in these eight environments. Unknown mappings, repeated observations and partial feedback were real parts of this task. The environment supplied the groups and the mapping family. Its token stream was independent of the learner's actions.

**Resources and verification.** The reference learner carries 24 FP64 log weights per group, 384 persistent bytes across the two groups, and shares the 96-byte table of permutations. Its compiled posterior-mean readout takes 256 bytes and evaluates one four-term dot product per offer once the frozen word forecast is available. A two-byte MAP readout selects one permutation per group in the same table. At eight opportunities reuse's integrated reward fell from 0.108803 to 0.086282 with MAP. At 512 its MAP and informed readouts coincide. Direct ridge carries eight four-dimensional regression problems across both groups. Its implementation stores a Gram matrix, target vector and fitted coefficients per problem, totaling 1,536 FP64-data bytes. Its deployed coefficients take 256 bytes. The frozen word priors have the destination-only costs in the preceding text study. The full experiment including prior reconstruction, three acquisition menus and all reporting replays took 15.45 seconds and reached 253.8 MB process working set. [Policy and compiled readouts](ticket_policy.py)

The independent audit integrated 19,281 outcome/report cases using exact symbolic log factors and rational price terms. It bounded 17,980 FP64 production payoff calculations against outward log intervals, checked 44 discrete menus, enumerated 1,305 binary-tree cases and confirmed the purchase-only indistinguishability and no-update controls. Lean 4.34.1 checked the integer-scaled aggregation of the pairwise lower requirements and the total single-offer budget, using propext and Quot.sound. The integral, the passage to real coefficients and the tree theorem have separate mathematical proofs. [Decision theorem](INTELLIGENCE_OBJECTIVE.md#how-much-log-loss-can-a-single-action-measure) · [Exact audit](audit_tickets.py) · [Lean arithmetic proof](TicketBudget.lean)

~~~powershell
python -B research/frontier/text_ticket_actions.py --check research/frontier/text_ticket_actions_result.json
python -B research/frontier/audit_tickets.py
& "$env:USERPROFILE\.elan\toolchains\leanprover--lean4---v4.34.1\bin\lean.exe" research/frontier/TicketBudget.lean
~~~

## Can feedback teach a smaller state for future updates?

**EMPIRICALLY OBSERVED.** An initially empty learner acquired nine directions in the log likelihoods of a supplied bank of 24 anonymous hypotheses. A different basis learned from hypothetical hits, with no purchased outcomes, recovered the same space. The geometric structure was already available in the forecasts. Actual purchased bits determined the changing belief within this space. On 32 fresh group-belief streams, nine retained numbers reproduced all later predictions to $2.3\times10^{-15}$ and all 16,384 purchase decisions. Four retained directions changed 1,545 purchases. [Frozen protocol](https://github.com/alan-ai1196/FP/blob/46fdab6/research/frontier/NEXT.md) · [Causal acquisition and replay](text_update_subspace.py) · [Per-prior scores and packet identities](text_update_subspace_result.json)

The discovery slab comprised 65,536 disjoint triples beginning at raw position 5,275,648. Group membership and the two preceding tokens were public. Discovery used the first 512 eligible opportunities in each group and the previously fitted reuse word prior. A purchase supplied one realized log-likelihood vector in fixed anonymous column order. Subtracting its first entry gave 23 log ratios. The learner twice removed directions it had already retained and installed a normalized residual above the declared tolerance. It received neither the name-to-word incidence matrix nor a target rank. After eight opportunities per group it had seven directions from eleven purchases. Direction nine appeared on opportunity 13 of the first group. There were 79 purchases by the 64-opportunity checkpoint and 624 by the 512-opportunity checkpoint. The last two snapshots had identical packets.

Four subsequent slabs, each 32,768 triples, supplied new hidden mappings, offers and previously unobserved text. In each slab, two groups and four frozen word priors, pooled, global, rank-one and separate, gave eight learning streams. Each started with a uniform belief. Every method chose its own purchases and saw only their bits. The reporting interval ended at raw index 5,865,472. The reference made 9,963 purchases in 16,384 opportunities. The table's reward is per actual opportunity under the acquisition menu, including its quarter of floor-priced offers.

| Frozen update representation | Real numbers per group | Purchases | Different decisions from reference | Largest difference in any forecast | Mean realized reward |
| --- | ---: | ---: | ---: | ---: | ---: |
| Full posterior log weights | 24 | 9,963 | 0 | 0 | 0.149519 |
| Centered log ratios | 23 | 9,963 | 0 | $2.06\times10^{-15}$ | 0.149519 |
| Known assignment log coordinates | 9 | 9,963 | 0 | $2.17\times10^{-15}$ | 0.149519 |
| Learned after 8 opportunities/group | 7 | 10,167 | 490 | 0.856740 | 0.145310 |
| Learned after 64 or 512/group | 9 | 9,963 | 0 | $2.23\times10^{-15}$ | 0.149519 |
| First four learned directions | 4 | 10,540 | 1,545 | 0.825163 | 0.136948 |

The seven-direction learner first diverged on the 25th opportunity of the first pooled stream. The four-direction control diverged on its 11th. The full learned basis discarded at most $5.83\times10^{-15}$ in vector norm per purchased update. Acquisition, reconstruction of the original word priors and the complete registered replay took 9.15 s and reached 252.7 MB process working set. This test reuses text contexts across the four priors within an environment.

**Post hoc checks of the supplied structure.** We gave an outcome-blind control the first 304 and 320 offered names and word forecasts from the two discovery groups, matching the number of purchased vectors. It treated each as a hypothetical hit, independently of the actual price, purchase or word. After 64 and 512 opportunities' matched counts its fitted subspace projector differed from the actual-feedback projector by $7.15\times10^{-15}$ in operator norm. Its 512-checkpoint transfer produced zero different purchases, with maximum forecast discrepancy $8.78\times10^{-15}$. The source of the nine directions can therefore be distinguished from the information learned about any particular hidden mapping. [Independent control](audit_update_subspace.py)

Two further decoders exploited structure the initial numeric representation left unused. Pivoted QR selected nine directly readable likelihood ratios and learned a linear reconstruction for the other fourteen. The retained submatrix's condition number was 3.396. A rule given the public ticket names split the anonymous hypotheses by equality of the likelihoods observed for each name. At the eight-opportunity checkpoint its four names had 4, 4, 1 and 4 classes. At 64 all had four. Matching the unique disjoint class for each other name recovered all 24 assignments up to a common word relabeling. Its implementation checked the complete permutation pattern before using the specialized decoder. Both post hoc methods made all the reference purchases, with maximum forecast differences of $5.06\times10^{-15}$ and $2.17\times10^{-15}$. These methods exploit different declared interfaces and structural assumptions. [Derivation](FOUNDATION.md#when-does-current-predictive-state-suffice-for-continued-learning) · [Packet encoders and learning updates](update_subspace.py)

| Representation | Shared decoder bytes above the common likelihood bank | Persistent bytes for one group | Shared + 16 groups | Median native ms for 32 streams |
| --- | ---: | ---: | ---: | ---: |
| Full log weights | 0 | 192 | 3,072 | 2.795 |
| Centered log ratios | 0 | 184 | 2,944 | 3.068 |
| Learned orthonormal basis | 1,658 | 72 | 2,810 | 4.701 |
| Nine selected log ratios | 1,013 | 72 | 2,165 | 3.869 |
| Known assignment coordinates | 0 | 72 | 1,152 | 3.537 |
| Discovered assignment incidence | 26 | 72 | 1,178 | 3.663 |

The dense learned decoder costs 2,234 bytes for eight groups against 1,472 for direct ratios. At 64 groups it costs 6,266 against 11,776. Its crossover is 15 simultaneously retained group beliefs. The pivoted decoder crosses at ten. The 26-byte recognized incidence packet is cheaper than direct ratios even with one group. These storage comparisons count serialized numeric decoding tables and physically allocated FP64 working state per retained group. The native executable and the common word priors and likelihood evaluator remain separate. For this workload the common evaluator uses 96 bytes of word indices for the anonymous hypotheses. Every native arm performs the same four action readouts, commits its buy/pass decision, then reads the environment bit only on a purchase. The stable normalization uses 24 scratch weights per active stream execution. The cheapest persistent state did not yield the fastest native pass. The complete binary and seven resident-data samples per method are recorded. [Native CPU implementation](update_replay.c) · [Timing and control outcomes](update_subspace_timing.json)

The independent audit found exact assignment dimensions 1, 4, 9 and 16 at $K=2,3,4,5$, checked 48 updates from nonuniform positive priors, 60 even/odd response words and all 528 Boolean $2\times2$ and $3\times3$ permanent reductions. Subset dynamic programming agreed with enumeration through $K=8$ to $8.29\times10^{-14}$ on log normalizers and marginal entries. Exact rational enumeration confirmed the binary64 marginal collision on the four-ticket family and its $7/104$ next-forecast separation after a common suffix. The analytic proofs and the executed finite cases have distinct scopes. [Counterexamples and precision](OBSTRUCTIONS.md#equal-assignment-marginals-can-conceal-the-next-learning-update)

~~~powershell
python -B research/frontier/text_update_subspace.py --check research/frontier/text_update_subspace_result.json
python -B research/frontier/audit_update_subspace.py --text
python -B research/frontier/measure_update_subspace.py
~~~

## Does ordinary text teach both sides of a predictive correction?

**EMPIRICALLY OBSERVED.** From raw next-token errors the learner selected 256 earlier GPT-2 types, 256 output types and a common odds multiplier of 1.5. Applying that multiplier when the earlier token belonged to the learned input set reduced priced full-vocabulary loss by 0.006611 nats/token against a matched calibrated trigram. A simpler model learned its own 256-word output set and applied it on every history. It won on all four reporting blocks, using 513 fewer bytes than the history-dependent correction. [Prospective registration](https://github.com/alan-ai1196/FP/blob/0f45141/research/frontier/NEXT.md) · [All selected raw IDs, validation choices and block scores](text_word_classes_result.json)

The positive pooled bigram was inherited from the historical prefix. The new learner used 262,144 raw targets from position 5,865,472, followed by an independent 131,072-target selection block. It alternated an exact input-gate fit with a tangent update across 50,257 output candidates. Starting conditions used raw token frequency, fixed random partitions or every history. Validation considered 303 distinct installations. The reference symbol identities, part-of-speech tags, previous learned word groups and label-specific forecasts from the ticket studies were absent from the acquisition interface. A conventional competitor fitted individual log odds for named words at active histories, using the same available installation cap. [Sparse operators, optimizer and packet format](word_classes.py) · [Acquisition and scoring](text_word_classes.py)

| Forecast on 524,288 later raw tokens | Bytes above common bigram | Full-vocabulary NLL | NLL with storage price |
| --- | ---: | ---: | ---: |
| Pooled calibrated bigram | 2,584 | 6.935871 | 6.936298 |
| Learned earlier set, one output | 3,115 | 6.931831 | 6.932346 |
| Learned earlier set and output set | 3,625 | 6.925516 | 6.926115 |
| Global learned output set | 3,112 | **6.921533** | **6.922047** |
| Learned current-token gate and output set | 2,792 | 6.935369 | 6.935830 |
| Earlier gate and individual word odds | 3,241 | 6.926010 | 6.926546 |
| Matched calibrated trigram | 3,621 | 6.932128 | 6.932726 |
| Calibrated trigram at 4,096-byte cap | 4,095 | 6.931728 | 6.932405 |

On targets $[6258688,6782976)$ the earlier gate was active 235,570 times. Its learned output set contained the actual target on 88,323 of those occasions. It beat the singleton, current-token gate and both raw count competitors in all four blocks. Its advantage over individual fitted odds was 0.000430 on average and positive in three blocks. The matched raw model purchased 52 rows with 67 named successors. The full-cap raw model purchased 76 rows with 98 successors. Both selected counts from the fresh fit. The global and earlier-gated output sets overlapped on 171 of their 256 IDs. Both used a multiplier of 1.5. Their 0.004068 priced gap in favor of the global class shows why the gate needs a comparison against learned unconditional recalibration. A sparse active list with a neutral default cannot cheaply turn itself on everywhere. The previous two-group transfer experiment held group masses fixed and answered a different question.

On the identical 16,384 anchor positions the global class scored 6.818548, the earlier-gated class 6.818817, the matched trigram 6.825433, the modified Kneser–Ney five-gram 6.418318 and the Transformer 6.075578 nats/token. The last two had their original training histories, checkpoint sizes and context limits. [Frozen anchors and per-block scores](word_class_anchors_result.json)

**Physical cost.** The earlier-gated model stored 2,584 base bytes, a 16-byte header including an integer backoff-mass correction, two sorted lists of 512 bytes each, and one carried bit rounded up to a byte. On active queries, the uncached scorer chose the smaller of the sparse successor row and the output list for traversal. It performed 7,628,599 successor membership probes and 20,630,528 named bigram probes for normalization. The matched raw trigram directly scored one retained row or its calibrated backoff. The training and scoring rerun took 21.26 seconds and reached 259.6 MB working set. Five sequential native CPU passes and warm teacher-forced RTX 3090 batches gave the following median times on all 524,288 targets. Every native observed loss agreed with the vectorized reference to $10^{-11}$ per position. [Packed C and CUDA scorer](word_class_score.c) · [All timing samples, byte costs and probe counts](word_class_timing.json)

| Resident-data observed-token scorer | CPU ms | RTX 3090 ms |
| --- | ---: | ---: |
| Earlier-gated class, 3,625 bytes | 502.13 | 2.9434 |
| Earlier-gated class, 78 cached rows, 4,095 bytes | 174.38 | 1.3227 |
| Global class, 3,112 bytes | 1,218.30 | 2.9146 |
| Global class, 163 cached rows, 4,092 bytes | 216.11 | 0.8885 |
| Individual word odds, 3,241 bytes | 92.54 | 0.6178 |
| Matched trigram, 3,621 bytes | 44.56 | 0.1335 |

The cache study was added after observing the cost of normalization. It ranked current tokens by training context frequency while active times the number of probes avoided. Each stored query ID and summed count correction costs six bytes plus a two-byte table header. The largest earlier-gated cache avoided 20,767,992 probes and produced the same probabilities. This reduced its scoring time substantially and still left it slower than raw rows. The exact audit checked 4,096 submodularity inequalities, all 63 nonempty four-vertex graph reductions, the singleton initialization failure, and full 50,257-outcome normalization for each nonempty learned readout at three query rows. The type-specific current or earlier gate only selects whether to use the resulting normalized correction. [Exact controls](audit_word_classes.py) · [The mathematical comparison with class triggers](FOUNDATION.md#learning-the-input-and-output-sets-of-one-raw-token-prediction)

~~~powershell
python -B research/frontier/text_word_classes.py --check research/frontier/text_word_classes_result.json
python -B research/frontier/audit_word_classes.py --text
python -B research/frontier/address_anchors.py --word-classes --check research/frontier/word_class_anchors_result.json
python -B research/frontier/measure_word_classes.py --gpu --cache
~~~

## Does the earlier token help after calibrating the learned word class?

Yes on these two subsequent blocks, with a small advantage over the strongest simple reference. The selected 4,096-byte predictor used 292 current-token and 98 earlier-token exceptions. It gained **0.002319 priced nats/token** over the same-size current-only fit, and **0.000343** over the 3,112-byte global predictor inherited from the preceding experiment. The latter had the best score on selection, including the joint candidates. The first reporting block gave the joint model only 0.0000074 priced nats/token over that reference. The model comparison alone cannot identify the population conditional mutual information of the earlier token. [Prospective specification](https://github.com/alan-ai1196/FP/blob/ae87e2f/research/frontier/NEXT.md) · [Scores, per-block coverage and all installations](text_nested_class_result.json)

All models retained the same 256 output IDs acquired from raw loss in the prior experiment. Training and validation used the original 262,144 and 131,072 targets. The two new consecutive blocks had 131,072 targets each, starting at 6,782,976 and 6,914,048. A single odds multiplier rescaled the learned word class at every query while preserving both within-group distributions. Fitting the multiplier on the same sample that produced the class gave $1933/1024\approx1.888$, which transferred worse than the original factor $1.5$ on selection and both reporting blocks. The following are means over the complete 50,257-token output law evaluated on the realized targets. The price adds $(\ln 2/256)\cdot8\,\mathrm{bytes}/131072$ nats/token to observed NLL. The two inherited raw trigram payloads were checked against their original hashes.

| Predictor | Bytes above raw bigram including carry | Block 1 priced | Block 2 priced | Mean NLL | Mean priced |
|---|---:|---:|---:|---:|---:|
| Pooled base | 2,584 | 6.970570 | 7.003798 | 6.986757 | 6.987184 |
| Previous global, odds 1.5 | 3,112 | 6.957563 | 6.989040 | 6.972787 | 6.973301 |
| Refitted global | 3,112 | 6.962563 | 6.992926 | 6.977231 | 6.977745 |
| Earlier-token exceptions | 3,605 | 6.959830 | 6.989619 | 6.974129 | 6.974725 |
| Current-token exceptions | 4,096 | 6.959586 | 6.990969 | 6.974601 | 6.975277 |
| Raw-pair exceptions | 4,095 | 6.960494 | 6.991119 | 6.975130 | 6.975807 |
| Earlier and current exceptions | 4,096 | 6.957556 | 6.988362 | 6.972282 | 6.972959 |
| Two current tables allowed | 4,096 | 6.959586 | 6.990969 | 6.974601 | 6.975277 |
| Previous matched raw trigram | 3,621 | 6.966133 | 7.001465 | 6.983201 | 6.983799 |
| Previous full-cap raw trigram | 4,095 | 6.965835 | 7.001055 | 6.982768 | 6.983445 |

The two-current family selected exactly the single 392-entry current table. The two-factor winner used 4,095 installed bytes and one byte of causal carry for the earlier response code. Its current table fired on 62,180 of 262,144 predictions, its earlier table on 57,321, and both on 9,156. Against the refitted global law it gained 0.004949 pure and 0.004786 priced nats/token. Against the previous global it gained 0.000505 pure. On selection the joint model scored 7.040690 priced against 7.039251 for the previous global. The reporting advantage therefore describes the two registered arms. A learner selecting one deployment across all arms on validation would have chosen the previous global. [Fitting and serialization](nested_class.py) · [Study driver](text_nested_class.py)

On the same first 4,096 targets in each block the joint model scored **7.062070**, previous global **7.062099**, full-cap trigram **7.064072**, modified Kneser–Ney five-gram **6.602393**, and Transformer **6.221273** nats/token. The frozen five-gram occupies 34,489,589 file bytes. The Transformer's 7,253,376 parameters occupy 29,013,504 loaded bytes and received 16,777,216 training target exposures. Both anchors used 1,048,576 distinct training positions. These are predictive comparisons at different training and deployment budgets. [Anchor hashes, budgets and scores](nested_class_anchors.json)

The normalized class predictors used a shared 2,684,212-byte raw lookup and recomputed the class count in each query row. Across the full replay there were 7,052,640 successor membership probes and 28,181,760 named bigram count probes per class model. Each lookup used the shorter traversal. Five warm sequential CPU timings and five ten-launch teacher-forced RTX 3090 samples gave the joint predictor medians of **584.69 ms** and **1.5461 ms**, compared with **22.42 ms** and **0.0725 ms** for the full-cap trigram. These are observed-target scoring times. Every native CPU and GPU loss agreed with the vectorized reference within $10^{-11}$ at every position. The statistical replay including acquisition took 14.44 s with a 259.7 MB peak working set. The timing driver, measurement samples and integer probability normalizations are available below. [Native scorer](nested_class_score.c) · [Timing samples and byte accounting](nested_class_timing.json) · [Independent normalizations and exact graph audits](audit_nested_class.py)

The mathematical checks covered all 265 three-by-three supports with every vertex present, all 190 single-chord perturbations of their spanning forests, and 201 full-alphabet query and odds combinations across the learned readouts. Every loss for the carried-over global model also matched its original independent implementation within $10^{-12}$. For a hidden checkerboard interaction the audit rejected all 697 possible sets of at most three raw pair exceptions on four-by-four inputs, verified constructions through fourteen-by-fourteen, tested 26,244 rational quantitative loss bounds and compared exact population objectives under four tariff schedules with unequal replica counts. The real-parameter population proofs and the finite-precision deployment address different questions. [Information, graph structure and replication](FOUNDATION.md#which-earlier-distinctions-survive-current-token-calibration) · [Sparse repairs and loss bound](OBSTRUCTIONS.md#the-cost-of-repairing-an-interaction-one-cell-at-a-time)

~~~powershell
python -B research/frontier/text_nested_class.py --check research/frontier/text_nested_class_result.json
python -B research/frontier/address_anchors.py --nested --check research/frontier/nested_class_anchors.json
python -B research/frontier/audit_nested_class.py --text
python -B research/frontier/measure_nested_class.py --gpu
lean research/frontier/Checkerboard.lean
~~~

## How expensive is it to test a proposed state across decisions?

A finite test now reports both a reconstruction error and a bounded decision that attains it. A raw local component acts on its observed ID and an encoded component acts on a specified function of that ID. The outcome used to score decisions is hidden from both. The dense reference builds a column for every shared choice of all local reconstruction maps, minimizes half the $\ell_1$ error over their mixtures, and independently solves for the worst bounded loss. Its tests also enumerate all deterministic raw reporting policies to verify that the returned loss witnesses the gap. These are small modeled populations with supplied observation laws. [Mathematical target before calculation](https://github.com/alan-ai1196/FP/blob/62ddbdd/research/frontier/NEXT.md) · [Definition, proof and estimation guarantee](INTELLIGENCE_OBJECTIVE.md#what-can-an-unknown-decision-lose-when-a-state-discards-information)

The noisy four-context parity example gave the analytic value $(1/4-\epsilon/2)_+$ at seven noise levels from zero to one. On a single four-ID input, keeping only its upper bit incurred zero loss across tasks when the hidden outcome was that bit, and a worst bounded loss of $1/2$ when the outcome was the lower bit. Six strictly positive binary laws also checked the stability example approaching the sharp Lipschitz constant of two. The numerical primal, dual and reporting-policy objectives agreed within $10^{-9}$. Exact rational and exhaustive assignment checks certified the bipartite hardness reduction on all 63 nonempty labeled four-vertex graphs. [Dense solver and exact controls](quotient_value.py)

A second solver uses the graph of the coarse codes actually seen together. In one hidden-bit prediction, each of two components had $h$ coarse codes and $2h$ raw IDs. Occupied code pairs formed an alternating path with $2h-1$ edges. Each occupied pair was equiprobable. Write an ID as a coarse code and a bit, with row code $s$ and column code $t$. The row bit $b$ was fair and was the hidden target. The column bit was $b\oplus(s\bmod2)\oplus(t\bmod2)$. The raw row bit predicts the target exactly and the entire pair of coarse codes is independent of it. To attain a matching upper bound, a shared fair coin selects a row bit equal to the coin XOR row-code parity and a column bit equal to the same coin XOR column-code parity. The two reconstructed IDs have the right conditional relationship and match the hidden bit half the time. Thus the largest bounded decision loss is **exactly $1/2$** for every $h$. The sparse LP recovered this value at all four sizes.

| Coarse codes per component | Complete decoder columns | Bag probability variables | Absolute-deviation variables | Sparse constraint storage |
|---:|---:|---:|---:|---:|
| 2 | 256 | 48 | 32 | 2,668 bytes |
| 4 | 16,777,216 | 448 | 128 | 22,988 bytes |
| 8 | $2^{64}$ | 3,840 | 512 | 190,348 bytes |
| 12 | $24^{24}\approx1.33\times10^{33}$ | 13,248 | 1,152 | 649,548 bytes |

At 12 codes the solver had 529 equality rows and a total of 53,568 nonzero coefficients in its two sparse constraint matrices. The reported storage counts their CSR arrays. Python, the input law, the objective and the LP solver's working memory require additional bytes. A run of the four path sizes including process startup used 103.5 MB peak working set and 0.78 seconds on the local CPU. The two solvers agreed on the smallest path and on a separate instance with a multi-variable separator and a disconnected context. This demonstrates a computational advantage when candidate decoder entries have sparse co-occurrences. The joint-ID distributions on this benchmark were generated with known structure. [Sparse solver](quotient_tree.py) · [Proof of the representation and its limitations](OBSTRUCTIONS.md#even-checking-the-value-of-a-fixed-compression-can-be-hard)

~~~powershell
python -B research/frontier/quotient_value.py
python -B research/frontier/quotient_tree.py
~~~

## Learning to buy an observation from later target errors

Each episode supplies two opaque names, a delayed task index, the logging action, the emitted bit or a blank, and the eventual fair binary target. The 16 withheld name pairs never supply a training target. We gave the two learners identical logged episodes from the other 48 pairs. One estimated 384 independent target/response agreement rates with Jeffreys smoothing. The conventional model knew that each task's routing bit factored as an XOR of row and column memberships and that a wrong sensor was fair. It fitted the signs and selected the correct-sensor agreement rate from four values by conditional target likelihood. The controller optimizer saw each fitted forecast, the uniform distribution of raw pairs and the posted prices. No route label, matched-sensor indicator or unqueried outcome entered training. Logged passes contribute a constant target likelihood to both learners. With zero purchases and the registered tie choices both learners passed on all tasks. [Prospective registration](https://github.com/alan-ai1196/FP/blob/54506ee/research/frontier/NEXT.md) · [Learners and exact controller optimizer](controlled_sensing.py) · [Complete results and packets](controlled_sensing_result.json)

At 384 episodes, the factor fits made 80, 70, 30 and 58 mistakes among 192 true task/pair routes on the four seeds. At 3,072 and at 24,576 episodes each fit recovered every route, including all 48 withheld task/pair routes, and the exact agreement rate $7/8$ for each task. The larger training streams contained 16,198 to 16,364 purchases apiece. A raw-pair policy driven by the factor fit had population payoff 0.477539 at the expensive price after 384 episodes, below the 0.5 from passing. The table gives mean payoff at 24,576 episodes. Every column is an exact expectation over a specified finite population once a learner is fitted. All pairs includes the withheld 16. Withheld is conditional on just those 16. [Acquisition guarantee for the supplied factor family](OBSTRUCTIONS.md#what-passive-predictions-cannot-identify-about-a-sensor)

| Fitted probabilities | Bits after first and second name | Cheap, all | Cheap, withheld | Expensive, all | Expensive, withheld |
|---|---|---:|---:|---:|---:|
| Separate cell rates | 1 then 1 | 0.618490 | 0.572266 | 0.508545 | 0.501953 |
| Separate cell rates | 3 then 1 | 0.631836 | 0.546875 | 0.513062 | 0.500000 |
| Separate cell rates | 3 then 6, raw pair | 0.687500 | 0.500000 | 0.568359 | 0.500000 |
| Factor likelihood | 1 then 1 | 0.625000 | 0.621094 | 0.531250 | 0.531250 |
| Factor likelihood | 3 then 1 | 0.656250 | 0.648438 | 0.531250 | 0.531250 |
| Factor likelihood | 3 then 3, factored | 0.750000 | 0.750000 | 0.593750 | 0.593750 |
| Factor likelihood | 3 then 6, raw pair | 0.750000 | 0.750000 | 0.593750 | 0.593750 |

At the cheap price $1/8$, the wide first update learned from separate cell forecasts exceeded the population upper bound $0.625$ for **every** one-bit first update. Yet giving it a wider first state reduced its mean withheld payoff, from 0.572266 to 0.546875. At the expensive price $9/32$, the exact factor forecasts made both one-bit final policies buy on just one task in three. They achieved the same payoff. At the cheap price the factor-driven narrow and wide policies bought on every task.

On-policy target log losses in nats at the cheap price were 0.539648 (narrow), 0.525321 (wide) and 0.376770 (factored) using fitted factor forecasts. Forcing the sensor uniformly at test time and reading both fitted conditional forecasts instead gave 0.592377, 0.600393 and 0.534959. A difference in which observations are purchased changes the intrinsic difficulty of the subsequent prediction. The forced-sensor comparison charges neither a favorable observation distribution nor a purchase reward to a policy. At the expensive price on-policy losses were 0.587688 for both one-bit final states and 0.376770 for the factored state. Target loss here is binary. On the project's ordinary full-vocabulary text, the earlier registered experiment still favored the conventional language models. [Full-vocabulary text comparison](#does-the-earlier-token-help-after-calibrating-the-learned-word-class)

**Acquisition and execution costs.** Per fitted task the factor learner tests 128 gauge-fixed row sign vectors and four noise rates. For each candidate it optimizes eight column signs independently. The tabular learner fits two rates per task and raw pair, including the unsampled cells which receive the prior. For each price the two-bit-state controller search checks all 378 unordered pairs of three-task action plans, the wide learner assigns each of 64 raw pairs, and the narrow learner evaluates 128 first-name partitions plus the optimal second map. One complete Python replay of four seeds, four budgets including zero, both forecasters, both prices, compilation and all population metrics took 0.614 seconds process wall time, with sampled process peak working set 39,653,376 bytes. This includes startup, receipt verification and the reference optimizer.

| Controller | Action packet bytes | Packet with selected Q16 forecast | First / final bits | Warm milliseconds per 1,048,576 decisions |
|---|---:|---:|---:|---:|
| Constant | 5 | 11 | 0 / 0 | 1.783 |
| One bit at each arrival | 9 | 21 | 1 / 1 | 2.556 |
| Full first name, one final bit | 14 | 26 | 3 / 1 | 2.591 |
| Raw pair | 52 | 436 | 3 / 6 | 1.840 |
| Factored route | 16 | 64 | 3 / 3 | 6.902 |

Packets include a four-byte header. The predictive packet carries two bytes per final state and task for its chosen action. Persisting that confidence to a later target costs another 16 live bits. The packed C routine consumes first name, second name and task in causal order within each independent decision, then returns one action byte and two confidence bytes. The local MSVC optimized CPU run used nine warm samples per arm, 3,145,728 bytes each of batch input and output and a shared 103,936-byte binary including 53,680 text bytes. All 13,824 large-budget installation/context choices and Q16 forecasts matched the independent Python reference. A million additional byte-level choices and forecasts per timed arm also matched. The measurement covers decision and confidence lookup. Actual external sensor latency, future environment work, and GPU throughput were outside the benchmark. [C routine](sensing_score.c) · [Timing and verification](measure_sensing.py) · [Individual samples and binary sizes](sensing_timing.json)

**Foundation R4 comparison.** The pinned exact R4 evaluator executed the same fitted one-bit final controllers on 6,144 complete contexts across 32 installations, using three consecutive events with one-hot first name, second name and task. Every intermediate state, terminal action indicator and normalized selected Q16 probability matched. The narrower program had 54 nodes, four one-hot delayed cells, and 4 to 13 distinct parameter slots across fits. The wider had 114 nodes, ten delayed cells and 3 to 13 slots. Both used 19 external indicator channels, two positive output bases and native normalization. This is derived execution after paying for the same acquisition. A host dispatches the asserted action indicator. The packed timings above measure the direct controllers. Independent acquisition by the R4 compiler and its optimized device runtime remain open comparisons. [Pinned R4 replay](sensing_r4.py) · [Exact evaluator revision](https://github.com/alan-ai1196/FP/blob/a674dda8985be1dd316b102da4fa00a42c837819/src/reference_compiler/fp_reference/semantics.py)

The separate rational audit checked 256 possible binary final statistics, 520 posterior/price/terminal-policy combinations and 1,679,616 first/second-update spectral bounds. Lean 4.34.1 kernel-checked the price endpoints for every statistic. The printed axiom dependency for the finite bound was propositional extensionality. Interpolation in price, the general-dimensional proofs and the controlled simulator argument are written mathematical deductions. [Price and memory proofs](FOUNDATION.md#learning-what-to-sense-from-a-delayed-prediction) · [Causal simulator comparison](INTELLIGENCE_OBJECTIVE.md#which-causal-simulator-does-a-finite-horizon-decision-test)

~~~powershell
python -B research/frontier/controlled_sensing.py --check research/frontier/controlled_sensing_result.json
python -B research/frontier/audit_sensing.py
python -B research/frontier/sensing_r4.py
python -B research/frontier/measure_sensing.py
lean research/frontier/SensorPrice.lean
~~~

## Can the learner discover a sensor's response classes?

The registered learner received neither the XOR operation nor the number of row classes. For each delayed task it selected among 2,795 partitions of the eight early names into at most four classes. It fitted arbitrary target probabilities after either emitted bit by integrating conditional Bernoulli likelihood. A second learner shared a parameter for agreement on zero and one. Both saw only the sensor selected in the log and its eventual target. Four fresh seeds supplied permuted names. Across the three environments the same seed fixed the inputs, random logging actions, targets and noise draws. The three laws respectively used XOR, sometimes ignored the early name, or used the column to choose between two different bits of the early name. In each case we withheld the same 16 of the 64 pairs. [Registration before data](https://github.com/alan-ai1196/FP/blob/28e5a3d/research/frontier/NEXT.md) · [Implementation](response_classes.py) · [Per-seed fits, scores, ambiguity witnesses and all budgets](response_classes_result.json)

**Empirical result.** At 24,576 episodes the general learner and the symmetric learner each recovered the actual row partition in all 36 task/environment fits. There were two classes per task for XOR and the switch, and four for the address. Forcing an equal choice of sensors tests predictions on the same distribution of observations. Full-history raw-pair readout gave the following mean target NLL in nats on the 16 withheld pairs and the indicated payoffs there. The remaining variation in NLL measures actual probability calibration after route decisions have saturated.

| Response law | Fitted model | Forced-sensor NLL | Cheap payoff | Expensive payoff |
|---|---|---:|---:|---:|
| XOR | Separate response to each emitted bit | 0.542231 | 0.750000 | 0.593750 |
| XOR | Shared agreement parameter | 0.538453 | 0.750000 | 0.593750 |
| XOR | Supplied XOR family | **0.534959** | 0.750000 | 0.593750 |
| Column switch | Separate response to each emitted bit | 0.541824 | 0.750000 | 0.593750 |
| Column switch | Shared agreement parameter | **0.538133** | 0.750000 | 0.593750 |
| Column switch | Supplied XOR family | 0.640616 | 0.601562 | 0.500000 |
| Column address | Separate response to each emitted bit | 0.573503 | 0.710938 | 0.577637 |
| Column address | Shared agreement parameter | **0.566582** | 0.710938 | 0.578125 |
| Column address | Supplied XOR family | 0.652417 | 0.580078 | 0.500000 |
| Each law | Independent raw cells | 0.693147 | 0.500000 | 0.500000 |

At 384 episodes the free and symmetric learners recovered zero of 36 partitions each. At 3,072 episodes the counts were 19 of 36 and 25 of 36. On the four-class address at that budget the general learner scored 0.689065 withheld NLL, the symmetric learner 0.658111 and the supplied XOR learner 0.658416. Giving the true row partition as a diagnostic improved the general learner to 0.636481. At the largest budget the free learner matched that diagnostic in all three laws. Each final log contained 16,327 to 16,386 actual purchases. The pass-only control had payoff $1/2$ everywhere. The fitted models still received the family of blockwise-constant response functions and the uniform logging design.

**What the data determined.** Population enumeration gives different answers to recovering the fit and proving its extrapolation. Across four seeds and three tasks per law there are 192 withheld task/pair cells. Under the registered upper bound of four classes, **zero of 192** are identified for XOR and zero for the column switch. Every completion can be changed at any one such cell by spending a spare state. Nevertheless the unique compatible minimum-occupied-dimension partition in each instance fully determines all 192 answers. With the stronger true upper bound of two, agreement on every exposed cell also determines all of them. For the column address, the four-class partition was unique in all 12 task fits, yet **only 162 of 192** missing answers were forced. The other 30 occurred at class/column combinations with no exposed member. At the cheap price the 30 passes account exactly for the shortfall from oracle withheld payoff, $(30/192)(0.75-0.5)=0.0390625$. This is a finite example where class identities are recovered perfectly and some of their responses are unlearnable from that log. [Proofs, uncertainty and active acquisition lower bound](OBSTRUCTIONS.md#when-a-spare-response-class-can-reverse-a-prediction)

**Carried state, stored tables and execution.** At cheap price, using separate emitted-bit readouts and one bit at each arrival gave full-population payoffs 0.625000, 0.640625 and 0.609375 on XOR, switch and address. Retaining the three-bit first name before making the one-bit final state gave 0.656250, 0.656250 and 0.654785. The corresponding predictive packets were 33 and 38 bytes. A raw-pair controller needs 3 then 6 carried bits, 52 bytes for its policy and 820 with both emitted-bit forecasts. For a matched post-fit realization, the same raw pair can dispatch through the learned task's row class and later column. Three task offsets and the 24 packed two-bit row memberships cost nine bytes. For two classes per task this gave 25 policy bytes and 217 with forecasts. For four classes it gave 37 and 421. It uses the same carried state and produces the identical finite-precision outputs. The corresponding single-agreement packets with forecasts occupy 121 and 229 bytes. Persisting independent returned Q16 values across a later random emission takes 32 bits, or the controller can retain the query index and fetch the chosen value after the emission.

The complete Python statistical replay, including scoring, compaction and population identification, took 4.068 seconds, with sampled process peak working set 65,900,544 bytes. Each of the three independent per-task searches computes subset sufficient statistics and scores 2,795 partitions. The common native C deployment verified 110,592 decisions and 156,672 Q16 predictions against the fitted high-level models across the large-budget installations. Warm CPU medians for 1,048,576 two-forecast decisions were 3.330 ms for the raw-pair packet, 4.050 ms for the two-class packet and 4.061 ms for the four-class packet. Each case read 3,145,728 input bytes and wrote 5,242,880 output bytes. The smaller tables saved persistent storage and added a dependent lookup on this CPU. These are nine-sample batch measurements. [Native checks and timing driver](measure_sensing.py) · [Individual times](response_classes_timing.json) · [Packed kernel](sensing_score.c)

On seed 3011 the pinned R4 arithmetic replayed both separate conditional heads for each small controller, all laws and both prices, in 24 scalar branch circuits and 4,608 context/observed-bit cases. The host chooses the relevant branch after seeing the purchased bit. This verifies the derived positive graph after shared acquisition. The general spare-state construction was checked in Lean 4.34.1 with propositional extensionality as its printed dependency. A separate reference exhaustively compares 19,683 partial binary matrices and 118,098 candidate missing laws with all binary completions of three rows and three columns. These results concern finite controlled prediction. The project's natural-text scores remain a separate test. [R4 replay](sensing_r4.py) · [Lean proof](ResponseProfiles.lean) · [Independent enumeration](audit_response_classes.py)

~~~powershell
python -B research/frontier/response_classes.py --check research/frontier/response_classes_result.json
python -B research/frontier/audit_response_classes.py
python -B research/frontier/measure_sensing.py --response-classes
python -B research/frontier/sensing_r4.py --response-classes
lean research/frontier/ResponseProfiles.lean
~~~

## Do learned response classes transfer to missing word pairs on ordinary text?

**The registered hypothesis failed.** At each of three prior concentrations, integrated next-token likelihood selected a single class for the eight eligible earlier word IDs. The fitted table therefore made exactly the same predictions as the current-token-only comparison within this eligibility gate. Chronological selection favored the previously frozen global predictor. On the two subsequent reporting blocks, the one-class fit gained 0.0000511 priced nats/token over that predictor, but its 150 withheld-pair occurrences scored 0.0049144 nats/token worse. [Registration before reading this continuation](https://github.com/alan-ai1196/FP/blob/3b17ced/research/frontier/NEXT.md) · [Training, evidence gaps and normalization checks](text_response_classes.py) · [Complete scores and packets](text_response_classes_result.json)

The 262,144-target fitting block started at 7,045,120. The next 131,072 targets selected the concentration separately for each family, then the two 131,072-target reporting blocks began at 7,438,336 and 7,569,408. The learner retained the previous 256-word class, raw-bigram model and global class-odds multiplier of 1.5. Those ingredients determined a normalized law over all 50,257 tokens. The learnt scalar for any eligible pair changed the probability of the entire class and preserved probabilities conditional on membership and nonmembership. The same eight token IDs ranked highest at both history positions. Of 7,476 fitting observations with both names among the eight, 158 were excluded by the registered rank-pair mask. Only 29 of the 48 permitted pair types appeared. The remaining 7,318 observations supplied 409 positive next-word class memberships. Different row IDs supplied between 5 and 2,452 training observations each. The receipt and pinned source provide the frozen corpus identity, every training pair count and the hash of the extended tape prefix.

| Predictor | Charged bytes above raw bigram | Mean NLL | Mean priced NLL | Withheld NLL |
|---|---:|---:|---:|---:|
| Global, chosen on selection | 3,112 | 6.9954063 | 6.9959206 | 9.0007838 |
| Current token within eligible pairs | 3,148 | 6.9953492 | 6.9958694 | 9.0056982 |
| Learned earlier classes | 3,148 | 6.9953492 | 6.9958694 | 9.0056982 |
| Independent raw pairs | 3,260 | 6.9953494 | 6.9958881 | 9.0007855 |
| Previous joint exception model | 4,096 | 6.9961122 | 6.9967891 | 9.0117038 |
| Previous full-budget raw trigram | 4,095 | 7.0026667 | 7.0033435 | 8.9985256 |

The two reporting blocks had 3,961 and 4,176 eligible occurrences and respectively 60 and 90 withheld occurrences. Reported conditional NLLs pool positions across both blocks. All three families chose concentration 512. The selected one-class packet spent 35 new bytes and one live byte in addition to the frozen predictor. It encoded both ranks with the same 16-byte ID table. It still must remember whether the previous token was eligible; all eight eligible IDs have the same response. The independent-pair packet stored 64 Q16 probabilities. Its withheld cells retained the original class prior up to quantization.

The completely separate raw-pair maximum likelihood could gain at most **9.6002 total training nats** over the fitted one-class maximum likelihood on exposed cells. The best two-class maximum-likelihood gain was 7.7453. After integrating the probabilities at concentrations 8, 64 and 512, the best two-class log evidence gains were 1.0360, 0.5154 and 0.4607. Each individual two-class partition paid $\ln127=4.8442$ nats relative to the one-class alternative under the stated prior. The best net gains over all nontrivial candidates were therefore negative at each concentration. This identifies which part of the learning rule rejected the split. It leaves open how much mass all nontrivial alternatives carry collectively. [Exact partition learning criterion](FOUNDATION.md#what-log-loss-can-pay-for-a-history-split)

Across the first 4,096 positions of each report block the one-class fit scored 6.921247, the frozen global 6.921334, the five-gram 6.585320 and the Transformer 6.233208 nats/token. The five-gram checkpoint occupied 34,489,589 file bytes. The Transformer used 7,253,376 parameters, 29,013,504 loaded bytes and 16,777,216 training target exposures. Both comparison checkpoints had seen 1,048,576 distinct training positions. These are identical reporting positions with different learning and deployment budgets. [Checkpoint hashes and block scores](response_text_anchors.json)

One complete statistical replay including reacquisition of the frozen comparisons took 3.048 seconds with a sampled peak process working set of 261,566,464 bytes. All 240 block/column Q16 normalization cases matched exact rational group sums from the raw successor counts. The native CPU stream carried only its earlier membership or class across tokens. The GPU used parallel raw contexts for teacher-forced scoring. Their complete full-vocabulary observed-token losses for the six installed models matched the independent reference at every one of 262,144 report positions within $10^{-11}$. For the learned arm the warm medians were 575.7 ms on the CPU and 1.634 ms per batch on the local RTX 3090. For the identical current-only installation they were 570.8 and 1.605 ms. The shared count and index arrays occupied 2,684,212 bytes and the batch loss output 2,097,152 bytes. The timing includes normalization under the inherited 256-word class. The batch uses resident arrays and evaluates the probability assigned to each observed target. [C and CUDA kernel](nested_class_score.c) · [Timing samples and device](text_response_classes_timing.json)

~~~powershell
python -B research/frontier/text_response_classes.py --check research/frontier/text_response_classes_result.json
python -B research/frontier/address_anchors.py --response-classes --check research/frontier/response_text_anchors.json
python -B research/frontier/measure_nested_class.py --response-classes --gpu
~~~

## Did posterior averaging improve next-token prediction?

**The average retained eight distinct earlier-word response profiles. The one-class comparator still achieved lower priced loss on both new reporting blocks.** The one-class partition had 28.33% posterior probability. The remaining mass was 24.61% on two classes, 23.75% on three and 23.31% on four. Averaging all 2,795 fitted structures therefore kept distinctions that disappeared when selecting the single most probable partition. All eight posterior-mean row profiles survived Q16 quantization. Installed with the frozen bigram and word-class correction, they occupied the same 3,260 charged bytes as a separate estimate for every raw pair. The one-class predictor occupied 3,148 bytes. [Prospective registration](https://github.com/alan-ai1196/FP/blob/8793590/research/frontier/NEXT.md) · [Causal study](text_partition_posterior.py) · [Complete results and resource accounting](text_partition_posterior_result.json)

The models reused the 7,318 admitted training labels and fixed concentration 512. The two fresh blocks started at 7,700,480 and 7,831,552 and contained 262,144 target tokens in total. Of 8,081 eligible contexts, 135 had a rank pair withheld in the original fit. All forecasts were released before that position's update. Each admitted update used the ordinary next token's membership in the frozen output class. The readout remained a normalized law over all 50,257 tokens. The horizon before the two report blocks contributed no intervening updates.

| Model and update policy | Full-stream NLL | Priced with serialized state | NLL on 135 originally withheld occurrences |
|---|---:|---:|---:|
| Frozen global | 6.94053445 | 6.94104874 | 9.102693 |
| Frozen one class | **6.94046114** | **6.94098138** | **9.101796** |
| Frozen posterior average | 6.94046192 | 6.94100067 | 9.102016 |
| Frozen independent pairs | 6.94046562 | 6.94100436 | 9.102693 |
| One class, train only on permitted pairs | 6.94044180 | 6.94098071 | 9.102685 |
| Posterior average, train only on permitted pairs | 6.94044239 | 6.94105534 | 9.101799 |
| Independent pairs, train only on permitted pairs | 6.94044896 | 6.94106191 | 9.102693 |
| One class, train on all eligible pairs | 6.94044168 | 6.94098059 | 9.102915 |
| Posterior average, train on all eligible pairs | 6.94044286 | 6.94105581 | 9.102523 |
| Independent pairs, train on all eligible pairs | 6.94044920 | 6.94106215 | 9.103155 |

On the 135 withheld occurrences the frozen mixture improved on independent pairs and the global baseline. The frozen one-class fit scored slightly better. Permitting every observed eligible target made 8,081 updates, including those 135. Restricting updates to the 48 original pair types made 7,946 updates. With that restriction, the adaptive mixture had better withheld NLL than the adaptive one-class comparator. It still had worse full-stream NLL and paid for a larger update state. On the 8,192 matched conventional-anchor positions the frozen mixture scored 6.914817, the modified Kneser–Ney five-gram 6.626326 and the Transformer 6.207023. [Conventional checkpoint identities and individual block losses](partition_posterior_anchors.json)

**A measured statistical price for carrying alternatives.** Before the updates, the one-class component had posterior mass 0.28332638490. For the unrounded predictors the cumulative log-loss excess of the mixture over this component on admitted updates could therefore never exceed $-\ln(0.28332638490)=1.261156$ nats, at any horizon on any continuation of these context-dependent observations. Measured excess was **0.274636 total nats** for the training mask and **0.313288 total nats** for all eligible inputs. In both cases this equaled the log change of the component's posterior weight within $10^{-8}$. With Q16 releases the all-update excess was 0.310758 nats. The check used both a direct sum of sequential losses and a fresh posterior reconstructed solely from final integer counts. The independent-pair model lies outside the mixture's at-most-four-class support. [Identity and assumptions](FOUNDATION.md#keeping-uncertainty-about-a-learned-computation)

**The memory price was much larger on this workload.** The mixture could resume from a 596-byte packet containing typed counts, shared IDs, the concentration and eight binary64 prior centers. The one-class packet took 148 bytes. With the frozen global model and one live byte their totals were 3,709 and 3,261 bytes. For fast sequential updates, the mixture materialized 38,808 bytes of counts, weights and prior parameters, plus 23,384 bytes of shared row/block indices. Including the dictionary, header, carry and global model gave 65,325 bytes. Applying the same rent to these active arrays raised its all-update priced score to 6.95123842. The one-class active footprint was 3,261 bytes and its score 6.94098059. These array totals exclude Python, full-stream inputs, emitted forecasts, diagnostic comparison counts, allocator overhead and temporary vectors. In particular the per-query mixture likelihood vector has 2,795 binary64 entries. A full verified Python run including the frozen baseline fitting took 3.734 seconds and a sampled 262,422,528-byte peak working set.

For the eight-name data the sequential mixture predicted and updated on the eligible positions in about 0.21 seconds, versus 0.017 seconds for the one-class and independent-pair controls. Rebuilding all weights once from final raw counts took about 0.28–0.33 ms on this CPU. Per admitted label the cached method reweights 2,795 partitions and updates 128 subsets containing the observed row. The frozen forecast needs no posterior update. Every observed-token full-vocabulary loss from its CPU and RTX 3090 deployment matched the independent reference within $10^{-11}$. Warm medians for 262,144 frozen mixture scores were 576.5 ms CPU and 1.924 ms GPU, versus 572.7 ms and 1.890 ms for one class. The native GPU benchmark measures frozen, teacher-forced scores. The continuing updates were measured on the CPU. [Packed scoring kernel](nested_class_score.c) · [Individual native timing samples](text_partition_posterior_timing.json)

The log-domain subset recursion and full partition enumeration agreed on every block marginal to $3\times10^{-11}$ absolute tolerance. In the independent four-row example, all current forecasts were $1/2$ but the same new label led to next forecasts $13/22$ and $7/12$. Fraction arithmetic checked the two posteriors, and Lean 4.34.1 checked the finite integer identities with propositional extensionality as the listed axiom. A 26-node, seven-slot positive program in the pinned R4 evaluator reproduced both normalized forecasts. It received the calibration-history layout and the finite integrated likelihood factors. This checks arithmetic expressibility after specifying the hypothesis family. It leaves native acquisition and the full language update costs to the measured learner. [Exact reconstruction](partition_posterior.py) · [Lean certificate](PartitionUpdate.lean) · [Pinned R4 execution](sensing_r4.py)

~~~powershell
python -B research/frontier/text_partition_posterior.py --check research/frontier/text_partition_posterior_result.json
python -B research/frontier/partition_posterior.py
python -B research/frontier/sensing_r4.py --partition-posterior
python -B research/frontier/address_anchors.py --partition-posterior --check research/frontier/partition_posterior_anchors.json
python -B research/frontier/measure_nested_class.py --partition-posterior --gpu
lean research/frontier/PartitionUpdate.lean
~~~

## Checking the memory needed for future predictions

**On the same fair mixture of quarter- and three-quarter-bias coins, the best four-state homogeneous predictor spent 2,812.091 nats at horizon 65,536. A 25-state stopped counter spent 0.083874 nats with five dyadic outputs.** The relevant excess is the expected *sum* of next-bit losses relative to the unrestricted Bayesian predictor, in nats per complete stream. A shared half-count predictor with no knowledge of either bias spent 4.577821 nats. The finite experiments use known laws to integrate each predictor's performance. Training-data acquisition is a separate comparison. [Question fixed before the calculation](https://github.com/alan-ai1196/FP/blob/02832d5/research/frontier/NEXT.md) · [Proof and hardware assumptions](FOUNDATION.md#how-much-memory-does-continued-prediction-require-for-two-noisy-coins) · [Full calculations](coin_memory_result.json)

| Predictor | 16 draws | 64 draws | 1,024 draws | 65,536 draws |
|---|---:|---:|---:|---:|
| Best 1-state | 1.442009 | 7.678849 | 133.258378 | 8,572.204440 |
| Best 2-state | 0.996617 | 5.720306 | 100.980209 | 6,502.383043 |
| Best 3-state | 0.560305 | 3.760325 | 68.577504 | 4,424.267394 |
| Best 4-state | 0.318132 | 2.356580 | 43.563480 | 2,812.090994 |
| Half-count per observed arm | 0.455215 | 1.111103 | 2.498325 | 4.577821 |
| 25-state counter, exact interior releases | <0.000001 | 0.000016 | 0.001007 | 0.067687 |
| 25-state counter, five dyadic releases | 0.014580 | 0.016202 | 0.017194 | 0.083874 |

The finite search covers every labeled deterministic binary update graph rooted at state zero for $S=1,2,3,4$, respectively 1, 16, 729 and 65,536 graphs. For each source row form its transition matrix $M_z$. The initial row of $\sum_{t=0}^{T-1}M_z^t$ gives its expected state visits. For each graph the optimal state readout is the source bias averaged under those visits and the prior. Subtract the full learner's mutual information to obtain expected transcript KL. Every searched graph obeyed the finite-horizon lower bound at all four horizons. The summations and optimization over outputs used binary64 arithmetic. Exhaustive graph coverage and exact rational arithmetic are distinct checks. Direct rational path likelihoods for all 1,022 paths of lengths 1–9 independently reproduced the passive and stopped-counter KLs within $10^{-12}$. No table was fitted to sampled outcomes in this comparison.

For the passive mixture, replacing both coins by their common prior forecast gives first-draw KL zero and second-draw KL 0.031584 nats. With prior weight 0.001 on the three-quarter coin, its second-draw price drops to $8.84\,10^{-7}$ and its price at 1,024 draws is still 0.553900. With equal means or a zero-weight second row the price is exactly zero. For the controlled two-arm case an independent dynamic program and exact path likelihoods agreed on the best three-decision value over all 128 deterministic policies for each proposed replacement. Fraction arithmetic also verified the exact worst half-count likelihood ratio for all 2,145 success totals through length 64 and the worst allocation of trials among three arms through total length 32. [Controlled price and sharp rates](INTELLIGENCE_OBJECTIVE.md#how-much-can-an-adaptive-experiment-expose-a-forgotten-hypothesis) · [Half-count residual bound](FOUNDATION.md#a-shared-residual-for-discarded-bernoulli-hypotheses) · [Reproducible audit](coin_memory.py)

**Physical replay.** The native CPU counter stored one signed byte per stream and a threshold of 12. It used Q3 probabilities represented exactly in the common binary64 output array. The population-selected four-state predictor used eight transition bytes, four binary64 probabilities and one live byte per stream. The generic half-count rule used two unsigned 32-bit counts per stream and a binary64 division. Each processed 1,024 fresh streams of 1,024 bits, with equal numbers from the two source biases. All 3,145,728 issued probabilities agreed with independent reference calculations. Splitting after draw 37 and resuming from the stored state also reproduced every probability and each final state. On the local CPU their nine warm median times were 0.919 ms for the counter, 1.343 ms for the graph and 0.992 ms for half-count. Each benchmark read 1,048,576 input bytes and wrote 8,388,608 output bytes. Timings include the compiled forward pass, while data generation, allocation, state reset and reference checking are outside the timed region. The C half-count readout uses floating-point division and its exact rational coding theorem presumes counters have not overflowed. [C kernels](coin_predict.c) · [Reference and restart verification](measure_coin_memory.py) · [Individual timings and binary footprint](coin_memory_timing.json)

~~~powershell
python -B research/frontier/coin_memory.py --check research/frontier/coin_memory_result.json
python -B research/frontier/measure_coin_memory.py
~~~

## Learning coin biases from ordinary pairs

**A learner calibrated by 16,384 two-bit episodes used seven installed bits and one live byte. On a fresh 16,384-draw episode it incurred 0.71048 total excess nats, averaged over five test amplitudes. A Bayesian learner receiving the same seven bits and updating its amplitude distribution incurred 0.48606.** The reference for both learners knew the true amplitude and had to infer the new orientation. The seven bits carry only the results of calibration. The family, reset boundaries, and the form of the counter are supplied. [Prospective registration](https://github.com/alan-ai1196/FP/blob/0940e87/research/frontier/NEXT.md) · [Minimax calibration cost](FOUNDATION.md#what-does-it-cost-to-learn-the-prototype-that-a-small-state-uses) · [Full matrix](coin_calibration_result.json)

Each pair began with a fresh independent fair orientation. The learner predicted its second bit given its first. The empirical rate of agreement maximizes that ordinary conditional likelihood over the unrestricted agreement probability. Clamping and inverting it produced a fitted amplitude. The packet encoded one of $2^B$ equal-width interval midpoints. The five true amplitudes were 0.625, 0.68, 0.75, 0.82 and 0.875. The study crossed three horizons, three numbers of training pairs, three packet widths and these five amplitudes. It integrated over training packets and reporting sequences separately for each of 135 conditions. The equal average across five reported parameter values differs from the uniform continuous prior used inside the Bayesian comparator.

| Report draws $T$ | Training pairs $N$ | Packet bits | Bayesian, same packet | Full mixture at fitted amplitude | Fitted counter, Q12 center | True-amplitude counter, exact center | Fresh half-count |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 64 | 64 | 3 | 0.32319 | 0.44488 | 0.44906 | 0.00296 | 1.12249 |
| 1,024 | 1,024 | 5 | 0.45809 | 0.64804 | 0.67131 | 0.01944 | 2.49830 |
| 16,384 | 1,024 | 7 | 1.57986 | 10.09256 | 10.12240 | 0.02578 | 3.88467 |
| 16,384 | 16,384 | 7 | 0.48606 | 0.68243 | 0.71048 | 0.02578 | 3.88467 |
| 16,384 | 262,144 | 7 | 0.07756 | 0.06872 | 0.09605 | 0.02578 | 3.88467 |

All entries are total expected nats for one reporting episode. With 1,024 training pairs and 16,384 reporting draws, retaining uncertainty reduced the five-amplitude mean from 10.09 nats for the plug-in predictor to 1.58. At equal training and reporting sizes, the mean was 0.49 versus 0.68. Independent singleton training observations carried no amplitude information. The continuous Bayesian predictor with that training therefore used its original uniform prior, giving 3.32324 nats at $T=16{,}384$. At true amplitude $0.75$, $N=T=16{,}384$, raising the packet from five to seven to nine bits gave matched Bayesian prices 0.50577, 0.41214 and 0.40638. The respective plug-in prices were 0.87469, 0.63934 and 0.62629. This comparison allows every fitted-amplitude model to update its orientation during reporting.

Training-code probabilities came from binomial intervals, including empty and tied bins. The expected log score of each exchangeable model came from the reporting success count. For the compact counter, its expected state occupations under the true bias gave its expected conditional loss. The 39-state version stopped at signed count $\pm19$ and decoded a Q12 center for $|s|\le4$ plus the exact learned dyadic endpoint. The Bayesian comparator conditioned a uniform continuous amplitude prior on the *same packet*, integrated over both fresh orientations and updated on every reporting draw. Changing Gauss–Legendre integration from 512 to 1,024 nodes changed any reported Bayesian price by at most $1.35\,10^{-12}$ nats. The code drops packet masses below $10^{-15}$ individually, with total discarded mass checked below $2\,10^{-13}$, and uses reporting count tails of about $10^{-14}$ on each side. All 340 possible raw training logs of one through four pairs verified the stated agreement likelihood. The full expectation matrix took 3.770 seconds on this host with 223,019,008 bytes of sampled peak process memory. [Population integration, quadrature and finite checks](coin_calibration.py)

**Physical calibration and prediction.** A separate native replay received 32,768 ordinary training bits at true amplitude 0.76. Its 10,364 agreements produced packet value 67 out of 128 and reported amplitude 0.7568359375. A compiled integer encoder matched the reference at 4,060 bin-edge cases across the registered sizes. Its median time to acquire the packet from all 16,384 raw pairs was 0.0082 ms. The compact prediction kernel decoded the center and endpoint into six unsigned 16-bit values (12 bytes shared) and carried one signed byte per stream. The Bayesian comparison reconstructed its grid posterior from two 32-bit counts per stream, including after restart. Its 1,024 amplitude nodes and both orientations used 65,536 shared bytes for the biases, two log likelihood coefficients and the conditional log prior. All three deployments processed the same 32,768 future draws in two streams, writing 262,144 bytes each. Five warm median forward times were 0.0329 ms for the compact update, 599.7366 ms for the count-based grid and 65.7827 ms for the same Bayesian grid caching its weights. The faster grid used 16,392 live bytes per stream, shared the same table, and rebuilt its weights from log likelihoods every 128 observations. On an additional 4,096-draw reversal of long constant prefixes its forecasts matched the count-based grid within $6.11\,10^{-15}$. These are CPU costs of the stated implementations. Forward timings exclude shared-table construction. The reference built the grid prior in blocks of up to 128 agreement counts by 1,024 nodes in binary64. The compact setup needs only the six releases. The stopped counter matched its independent reference exactly and both grids matched to $1.41\,10^{-12}$ per release, including a restart after draw 37. [C kernels](coin_predict.c) · [Setup and matched native replay](measure_coin_calibration.py) · [Hardware receipts](coin_calibration_timing.json)

Pinned Foundation R4 executed the compiled, learned 39-state counter on every reachable state and both outcomes. All 78 transitions and their normalized next forecasts matched exactly. Its explicit one-hot encoding used 161 nodes, 39 delayed cells and 12 parameter slots. The ordinary calibrator supplied the learned packet and an external compiler supplied the transition layout. This establishes representation and arithmetic agreement. The one-byte native deployment and the integrated Bayesian learner use different physical encodings. [Pinned R4 runner](sensing_r4.py) · [Reference-program construction](positive_comparison.py)

~~~powershell
python -B research/frontier/coin_calibration.py --check research/frontier/coin_calibration_result.json
python -B research/frontier/measure_coin_calibration.py
python -B research/frontier/sensing_r4.py --coin-calibration
~~~

## Forecasting a long episode from short groups of unknown biases

A learner gets independent groups of $m$ ordinary bits. A fresh unobserved bias is sampled from the same arbitrary distribution on $[0,1]$ for each group. The comparison forecasts all $T$ bits of a fresh group and pays total excess log loss relative to knowing the distribution. With exact population probabilities for length $m$, the worst compatible family costs $\ln^+(\sqrt T/(m+1))+O(1)$ nats. For $m+1\ge\sqrt T$, up to $m<T$, the worst price is positive and decays as $\exp[-\Theta((m+1)^2/T)]$ up to constant factors. It is exactly zero when $m\ge T$. With $N\ge(m+1)^2$ ordinary groups, the analogous additive-constant rate replaces $m+1$ with $\min(m+1,\sqrt{m\ln(1+N)})$. The proofs allow unknown component weights and continuous bias distributions. Each is a worst-case statement over the short-group laws. [Proof, sample conditions and implementation](FOUNDATION.md#what-can-short-episodes-teach-about-an-unrestricted-future-mixing-law)

A phase-shifted grid of persistent biases has the same short-group law at every phase. With $T=4096$, the information the fresh report revealed about the hidden phase was 3.89279, 2.52937, 1.23457 and 0.66340 nats for $m=0,3,15,31$. Those values lower-bound the worst compatible-family loss. At $T=256,m=31$ it was 0.0091993 nats. An independent smooth two-law example gave 0.0045778, compared with its rigorous spectral lower bound of 0.0045669. Doubling angular quadrature from 96 to 192 nodes changed the twelve phase values by at most $1.64\times10^{-8}$ nats. The single-bias half-count reference was the exact phase-averaged transcript law. [Population results](grouped_checks_result.json)

Exact fractions verified 2,470 coefficient identities and 1,330 weighted inner products through group length 18. For the constructive Fejér forecast, 30 horizon/degree combinations checked every terminal count at 515 parameter angles including deterministic endpoints. At $T=256$, the largest observed true-to-forecast path likelihood ratio fell from 28.3731 with no moments to 5.1155 at $m=7$ and 1.6399 at $m=31$. Direct circular integration independently reproduced the recurrence on four angles for each setting. The theorem supplies the uniform bound between the sampled angles. The causal implementation needs two integer counts and a learned coefficient row. Exact-moment access, sampled training data and the small-loss existence construction have different acquisition or evaluation costs. [Numerical and rational checks](grouped_checks.py) · [Conditional recurrence and estimators](grouped_forecast.py) · [Prospective registration](https://github.com/alan-ai1196/FP/blob/38c30a6/research/frontier/NEXT.md)

## Learning when to buy a fresh coin from ordinary forecasts

**VERIFIED on four registered environments.** Each session supplied two observed bits, a randomized keep/reset receipt between them and an independent fresh report of $m$ bits from the same unlabelled environment. Training used the eight observed history rows and the report count. It received neither a component identity nor a target action. Matched fits used lengths 4 and 16, budgets 512, 8,192 and 65,536 sessions, and four seeds. The last quarter of each budget selected the harmonic degree and smoothing floor or the conventional grid's stabilizing floor by report likelihood. All 96 fits, four evaluation horizons and five prices were retained. A finite rational calculation and Lean verified the two conditional experiments. On the separated family, the actual advantage of buying after one grew from 0.002299 nats at one future draw to 0.018421 at 128. After zero it fell from −0.002926 to −0.023210. Thus the correct decision can change with the intended duration of a report that has yet to be observed. [Proof](FOUNDATION.md#when-does-an-ordinary-bit-justify-buying-a-reset) · [Prospective design](https://github.com/alan-ai1196/FP/blob/38c30a6/research/frontier/NEXT.md)

With $m=16$, 65,536 training sessions, $T=128$ and reset price 0.004 nats, the three history-dependent learners chose keep-then-buy in all four separated-family fits and the reversed policy in all four reflected fits. The table reports total expected excess log loss for an entire fresh report plus the paid rent. The reference knows the session environment and still has to infer the new coin. Oracle rows integrate over the unknown environment. Fitted rows average four deployment scores evaluated under the exact generating law.

| Readout and policy | Separated | Reflected | Contracted | Fixed within environment |
|---|---:|---:|---:|---:|
| Environment laws known, best conditional action | 0.323311 | 0.323311 | 0.162668 | 0.463107 |
| Environment laws known, best fixed action | 0.331513 | 0.331513 | 0.162668 | 0.463107 |
| Learned 65-point mixture, learned action | 0.332302 | 0.340121 | 0.202456 | 0.471755 |
| Learned positive harmonic density, learned action | 1.011141 | 1.012308 | 0.531767 | 1.189397 |
| Learned prefix histogram, learned action | 1.245878 | 1.245658 | 0.715171 | 1.479429 |
| Universal half-count rule, keep | 1.465339 | 1.465339 | 1.650687 | 2.151339 |

Against the retrospectively best fixed action **using the same fitted grid readout**, the learned decision saved 0.008354 nats in the separated family and 0.005703 in the reflection. It cost an additional 0.010607 in the contraction and 0.003270 in the fixed-bias control. The true gain after one in the contraction was only 0.000227 nats. At price 0.004 the fitted grid nevertheless bought after both inputs on one seed. In the fixed control it bought after one on two seeds. The grid readout won the four long-report comparisons. All planted biases in these four panels belong to the conventional dictionary. Fitting estimated their weights from raw group counts. This experiment alone does not establish how a support learned off that grid would transfer. The feasible likelihood directional-gap certificates were at most $4.75\times10^{-7}$ nats per fitting group on every row. Recomputing the entire fit and decision matrix matched the saved receipt in 9.146 seconds with a sampled peak process memory of 110,620,672 bytes. [All fitted rows, controls and gains at each horizon](learn_resets_result.json) · [Scoring and tie convention](learn_resets.py)

**Physical replay.** The first separated fit selected eight harmonic coefficients per history and 57 positive grid atoms across the eight histories, with six to eight in each row of this installation. A 128-draw policy takes a single packed byte after fixing its rent. Training plus selection used 1,179,648 observed bits and 65,536 receipts. The two NumPy count histograms occupied 2,176 bytes. Median warm aggregation from the observed history and report counts took 0.150 ms. From those histograms, fitting and computing the 128-draw action gains took 1.854 ms for the harmonic learner and 158.314 ms for the grid. Replay used the same 2,048 logged histories and 262,144 report draws for every kernel, including all eight history rows, and wrote 2,097,152 bytes per method.

| CPU forecast kernel | Packed model bytes | Expanded shared bytes | Persistent report bytes per stream | Median for 262,144 draws |
|---|---:|---:|---:|---:|
| Harmonic recurrence | 130 | 130 | 8 | 10.586 ms |
| Grid recomputed from counts | 540 | 1,851 | 8 | 55.892 ms |
| Grid with cached weights | 540 | 1,851 | 80 | 5.069 ms |
| Prefix histogram with half-count continuation | 546 | 8,706 | 8 | 0.251 ms |
| Half-count | 1 | 1 | 8 | 0.264 ms |

Each changing history selector adds one byte per stream for the history-dependent models. The count-only grid used another 72 bytes of reusable serial scratch. The tables include one action byte even for the constant policy. Times cover forecasting on this CPU, with seven warm repetitions and scalar binary64 arithmetic. The harmonic probabilities matched an independent circular integral to $3.45\times10^{-15}$. All five kernels matched their respective reference to $1.82\times10^{-13}$ including restart after 37 draws. The two grid implementations agreed to $5.52\times10^{-14}$ on an additional 4,096-draw reversal. Computing both outcome masses before normalization kept the cached version accurate on this reversal. Pinned R4 separately executed the acquired decision branch and four report transitions in each family using exact rational probabilities. Its explicit prefix expansion used 257 nodes and 63 delayed cells for each of the four programs, with 344 reachable transitions checked in total. The full C recurrence continues beyond this verified prefix. [C kernels](grouped_predict.c) · [Native replay and installation accounting](measure_grouped.py) · [Measured samples](grouped_timing.json) · [Pinned R4 comparison](grouped_r4.py)

~~~powershell
python -B research/frontier/learn_resets.py --check research/frontier/learn_resets_result.json
python -B research/frontier/measure_grouped.py
python -B research/frontier/sensing_r4.py --grouped-reset
~~~

## Learning two persistent probabilities off the dictionary grid

For at most $K$ unknown interior biases, fixed training-group length $m\ge2K-1$, $N$ independent calibration groups and a $B$-bit installation, the worst fresh loss is $\ln^+[\sqrt{T}\max(N^{-1/(4K-2)},2^{-B/K})]+O(1)$. The proof prices the actual packet received and permits continual adaptation on all $T$ future bits. At shorter training lengths the worst order is $\tfrac12\ln T+O(1)$ even with exact population training probabilities. At $K=2$, three bits per independent training group allow identification, yet controlling a fixed long-report loss across arbitrarily close pairs can require order $T^3$ groups. For each fixed positive allowance the installed packet needs $\log_2 T+O(1)$ bits in that two-prototype problem. The constants depend on the fixed support bound, training length and interior interval. [Complete proof and small-loss refinement](FOUNDATION.md#what-does-it-cost-to-learn-and-store-unknown-persistent-prototypes)

The tridiagonal hidden-family construction passed 80 rational moment equations and 280 path-probability equations for $K=1,2,3,4$. Eighty of the latter test the first observable changes at length $2K-1$. With $K=2$, $N=4096$ and the registered collision scale, all three-draw training groups together revealed at most 0.00001018 nats about the hidden parameter. One 16,384-draw fresh report revealed 0.41907 nats. At $K=3$ these values were $3.98\times10^{-8}$ and 0.56520. The two training numbers use a KL upper bound to a fixed reference. Doubling quadrature from 48 to 96 nodes changed any of the 24 fresh information values by less than $3.0\times10^{-15}$ nats. [Rational checks and population experiments](prototype_checks.py) · [All results](prototype_result.json)

A two-location estimator projected three factorial moments of ordinary binomial counts onto the feasible moment set and recovered two nodes by a symmetric eigendecomposition. It used no true locations or assignments. Projection's largest convex optimality gap across 72 fits was $3.85\times10^{-15}$ in the squared-moment objective with factor $1/2$. The 65-point likelihood comparator's largest gap was $4.97\times10^{-7}$ nats per training group. The table shows four-seed means at $m=5$, $N=65,536$, $T=16,384$. All true locations in this table are off the 65-point grid. Charged models receive two quantized locations and use equal component weights. The robust version expands them into geometric tails at the theorem's scale. The unquantized two-node fit additionally retains the fitted mixture weight. [Prospective choices](https://github.com/alan-ai1196/FP/blob/5a9e859/research/frontier/NEXT.md) · [Moment projection, packet and causal mixture](prototype_learning.py)

| Fresh population | Fitted locations and weight | Conventional 65-point mixture | 8-bit atoms | 16-bit atoms | 16-bit smoothed | Half-count |
|---|---:|---:|---:|---:|---:|---:|
| Separated 0.23 and 0.71 | 0.1851 | 2.2855 | 6.2272 | 0.2467 | 3.2394 | 3.9189 |
| Nearby 0.47 and 0.54 | 28.6539 | 10.6509 | 35.2621 | 28.9474 | 2.9009 | 3.9189 |
| Single 0.53 | 0.0466 | 0.1254 | 0.9948 | 0.2558 | 3.5219 | 4.5778 |

The same two-byte packet gave sharply different predictions depending on its interpretation. Sharp atomic releases earned lower loss on the separated and single-bias populations, while the wider decoder reduced the nearby-pair loss by 26.0465 nats. At the smaller sample budget of 256 three-bit groups the unquantized two-location fit lost 202.926 nats on the separated population. These averages span four specified seeds. Neither decoder dominated and both assume exchangeability, an interior probability interval, known calibration length and a cap on the number of locations. The robust finite grid had 97 points at $T=16,384$. Its resolution and weight-block width are computed from public budgets. Direct likelihood updates can reuse one weight per point, or use two report counts and recompute the mixture. Population integration used log likelihoods for all retained true counts. Dropping counts with mass $\le 10^{-23}$ contributes less than $10^{-13}$ nats even at the largest horizon for these bounded positive models. [Complete settings and per-seed risks](prototype_result.json)

## Learning persistence from next-word errors without reset labels

The frozen bigram and its earlier 256-token class correction supplied normalized probabilities over 50,257 raw tokens. Each new learner received their current class mass and the ordinary observed next word. Fits used 131,072 chronological targets, selection used the next 131,072, and all parameters were then frozen. The two fresh reporting blocks began at 8,224,768 and 8,355,840. States continued across adjacent blocks. The binary hidden-state fit learned log-odds shifts −0.410156 and 0.079102, stationary probability 0.677546 and refresh probability 0.002365 per word after packet quantization. It consumed no reset labels. Its state summarized evidence favoring the two different conditional word-class odds. The observed-residual learner instead accumulated recent signed errors with fitted rate 0.006287 and slope 4.365234. It won on the selection block with the registered incremental parameter rent. [Prospective protocol](https://github.com/alan-ai1196/FP/blob/a6063e0/research/frontier/NEXT.md) · [Learning and serialization](word_persistence.py)

| Installed predictor | Fresh block 1 NLL | Fresh block 2 NLL | Change from base, total nats | Extra installed / live bytes |
|---|---:|---:|---:|---:|
| Inherited global | 6.88750036 | 6.92422770 | 0 | 0 / 0 |
| Static refitted odds | 6.88858190 | 6.92469055 | +202.427 | 3 / 0 |
| Separately fitted iid mixture | 6.88858190 | 6.92469055 | +202.427 | 7 / 0 |
| Persistent fit, refresh forced to one | 6.88877055 | 6.92492952 | +258.477 | 7 / 0 |
| Persistent fit, binary64 carry | 6.88586096 | 6.92374297 | −278.413 | 9 / 8 |
| Same fit, 256 log-odds levels | 6.88586927 | 6.92372916 | −279.135 | 9 / 1 |
| Same fit, 65,536 log-odds levels | 6.88586098 | 6.92374292 | −278.418 | 9 / 2 |
| Selected observed-residual fit | **6.88351244** | **6.92321021** | **−656.068** | **7 / 8** |

Forgetting at every word with the same fitted regime probabilities and odds cost 536.890 nats relative to the persistent filter. The separate iid fit converged to identical quantized emissions. This isolates predictive value in temporal evidence on these blocks. The single observable residual delivered 377.655 more nats of improvement than the hidden-state fit, with two fewer installed bytes. Its gain over the base averaged about 0.00250 nats per raw word. The archived five-gram and Transformer remained substantially stronger on the matched first 4,096 positions per report. Their mean full-vocabulary NLLs were 6.210245 and 5.863071 compared with 6.584372 for the selected residual and 6.584855 for the inherited global. The archived Transformer has 7,253,376 parameters and trained on 16,777,216 target exposures. This experiment fitted the correction on top of the bigram. [Chronological results and all starting-point fits](text_persistence_result.json) · [Checkpoint identities and matched panels](persistence_anchors.json)

A direct dense 50,257-word calculation at ten reachable contexts verified probability normalization, class mass and realized raw-word log loss to $1.78\times10^{-15}$. Central differences checked all training gradient coordinates to $1.76\times10^{-10}$. The C kernels emitted class probabilities before updating and reproduced uninterrupted prediction after a restart at word 37. The frozen vocabulary correction shared a 3,112-byte packet over the older common bigram data. Producing its source class masses can use a binary64 table over 50,257 last-token rows (402,056 bytes). The CPU update timings start with that mass available. For 262,144 words, seven warm median times were 1.624 ms for the residual, 1.942 ms for the binary64 hidden state, 11.031 ms for the byte state and 11.319 ms for the two-byte state. Converting log odds to an integer grid at every update accounted for additional work in these implementations. Fitting took 163.8 ms for the residual and 270.7 ms for the hidden model, including their multiple starts. A repeated complete run reconstructed the frozen readout and all chronological scores in 5.978 seconds with a sampled peak process size of 289,763,328 bytes. [Native kernels](word_persistence.c) · [Individual CPU samples](text_persistence_timing.json) · [Full-vocabulary evaluation](text_persistence.py)

The corresponding rounding proof bounds both per-path log-score errors and expected transcript KL under the fitted model. The expected deterministic bound was 0.14909 nats over the report for the 65,536-level grid. The realized signed difference from the unrounded language score was about −0.0045 nats. For an independent observable-history-dependent source, exact summation over all 4,096 length-12 transcripts and all conditional rounding choices checked eight settings. At refresh 0.32 and 16 levels, deterministic and randomized rounding cost 0.000784 and 0.002135 expected nats. Their upper bounds were 0.05004 and 0.02047. The randomized guarantee can be tighter while its realized operational loss is larger. [Proof and assumptions](FOUNDATION.md#how-much-prediction-accuracy-is-lost-by-rounding-a-learned-persistence-state) · [Finite-tree check](persistence_rounding.py) · [Finite-tree results](persistence_rounding_result.json)

## Learning a recurrent correction on the archived Transformer

The base was the pinned 7,253,376-parameter Transformer with its rolling 256-token context and float64 normalization across all 50,257 output words. Training got 32,768 ordinary targets starting at 8,486,912. The next 16,384 targets selected models and rates. The two fresh reports started at 8,536,064 and 8,552,448 with 16,384 targets apiece. The two learned directions operated on the 32 most frequent raw token IDs in the historical training fit and a complementary class. The input vector, output vector, gain and decay were fitted using errors of the actual Transformer. The comparison includes a conventional coordinate-wise correction learned from the same errors. None of these fits changed the Transformer weights. [Prospective choices](https://github.com/alan-ai1196/FP/blob/5907fd5/research/frontier/NEXT.md) · [Acquisition theorem](FOUNDATION.md#which-prediction-errors-justify-constructing-a-recurrent-direction)

| Chronologically selected fit in each family | First report NLL | Second report NLL | Change from Transformer, total nats | Added packet / live bytes |
|---|---:|---:|---:|---:|
| Frozen Transformer | 6.0861300 | 6.9999764 | 0 | 0 / 0 |
| Static named-class logits | 6.0878877 | 6.9985969 | +6.196 | 132 / 0 |
| One learned input/output direction, decay rate 1/128 | 6.0872464 | 6.9952422 | −59.274 | 200 / 8 |
| Same direction, signed 16-bit carry | 6.0872476 | 6.9952407 | −59.280 | 200 / 2 |
| Direct vector of errors, one gain, rate 1/128 | 6.0857990 | 6.9908858 | −154.363 | 68 / 264 |
| **Selected coordinate-wise gains, rate 1/512** | **6.0822517** | **6.9855511** | **−299.886** | **132 / 264** |
| Older 256-word class with a refitted residual | 6.0865768 | 6.9966766 | −46.744 | 519 / 8 |

The selected diagonal correction saved 63.542 and 236.344 nats in the two reports, about 0.00915 nats per raw word combined. The charged selection used only the preceding block. The learned scalar cost 18.291 nats on the first fresh block and recovered 77.565 on the second. It also had worse priced selection loss than the unmodified Transformer. The single-observation scalar control (rate one) cost 28.802 nats across the fresh reports. All five scalar fits had positive same-sample quadratic certificates, ranging from 0.000471 to 0.001104 nats per fitted word. Their ranking on fresh text differed. On the first 4,096 positions of each report the five-gram scored 6.524738, the Transformer 6.166587 and its selected diagonal correction 6.162582. These are results on two chronological samples, with one previously trained language model and a supplied frequency shortlist. [All rates, packets, checkpoints and per-block scores](transformer_directions_result.json)

Producing 81,920 full-vocabulary base forecasts and their named class masses took 7.668 seconds on an RTX 3090, with 84,035,072 bytes of peak PyTorch tensor allocation. The compact extraction arrays occupied 23,102,016 bytes. Full raw-word softmax and the pinned normalized-loss implementation checked the extraction to $7.78\times10^{-16}$. Fitting all named directions and conventional comparisons took 4.353 seconds on the CPU. Seven warm median replay times for 32,768 reports were 4.194 ms for the binary64 scalar, 4.578 ms for the 16-bit scalar and 4.455 ms for the selected diagonal. The native routines consumed the same 8,650,752 bytes of precomputed class masses. Each emitted 262,144 bytes of raw-word log-loss adjustments. The scalar read both learned vectors, including a dot product of its input direction with the base distribution. Independent vector computations agreed with every native released score to $4.0\times10^{-15}$ including restart. A dense independent tilt and normalization over the actual 50,257 Transformer probabilities at six positions matched raw-word NLL to $1.78\times10^{-15}$. [Feature extraction](transformer_class_features.py) · [C stream updates](direction_filter.c) · [Scoring](transformer_directions.py) · [Physical samples](transformer_directions_timing.json)

## Two learned error coordinates transfer to a separate text file

**All subset choices were frozen before either new tape was scored.** The original diagonal rates and slopes were fixed. For the 33 class-error coordinates, forward addition and backward deletion evaluated the actual normalized training NLL as each coordinate changed. Exhaustive search over all supports of sizes one, two and three agreed with the best nested candidate at those sizes to $10^{-12}$ nats in both precisions. The original chronological selection block chose among 67 distinct serialized candidates under caps of 1, 2, 4, 8, 16 and 33 retained coordinates. The full normalized base was the same archived Transformer. Inputs from the next portion of the training file and a separate validation file each supplied 4,096 warmup words before their two 32,768-word reporting blocks. The validation file contributed no fitted coefficient, support choice or name. [Prospective protocol](https://github.com/alan-ai1196/FP/blob/c0bf3a0/research/frontier/NEXT.md) · [Packets frozen before reporting](https://github.com/alan-ai1196/FP/blob/d3cb0fc/research/frontier/sparse_selection.json)

The two-coordinate model selected under installed-plus-live rent tracks GPT-2 raw IDs 13 and 198, which decode to a period and a newline. Their names emerged from the 32 previously frequency-ranked IDs and a complement, using prediction errors. The model carries two signed 16-bit error averages and receives a 12-byte packet containing their identities and slopes. It reduced full-vocabulary log loss on all four new blocks. The unrestricted diagonal still earned more. The earlier one-dimensional signed projection lost in aggregate on each new tape. Values below are **nats saved against the frozen Transformer** over each 32,768-word block. Positive is better. The named capped rows use only the preceding original selection decisions and include live-state rent there.

| Frozen correction | Packet / live bytes | Next training 1 | Next training 2 | Separate validation 1 | Separate validation 2 |
|---|---:|---:|---:|---:|---:|
| Previous signed one-dimensional projection | 200 / 8 | −26.24 | +2.46 | −14.75 | −0.90 |
| One coordinate, cap 1 | 8 / 8 | +0.53 | +28.84 | +1.05 | −0.85 |
| Two coordinates, cap 2 | **12 / 4** | **+4.55** | **+40.21** | **+18.06** | **+14.16** |
| Six coordinates, cap 8 | 80 / 12 | +15.13 | +57.84 | +38.59 | +70.70 |
| Ten coordinates, cap 16 | 88 / 20 | +21.70 | +74.63 | +51.22 | +87.94 |
| 32 coordinates, cap 33 | 132 / 256 | +69.29 | +158.23 | +102.67 | +152.34 |
| Original full diagonal, 33 coordinates | 132 / 264 | +71.00 | +159.72 | +103.78 | +152.64 |

The sparse format uses 134 packet bytes to express the original full diagonal, whose original dense packet uses 132 bytes. Both produced the same scores. With all 33 real-valued coordinates the dense state has one linear redundancy from the zero-sum error. Independently rounding retained coordinates can break that exact identity. Above two coordinates, models retaining the complementary class paid to transmit the remaining names defining it. The two-coordinate packet needs only the two named probabilities and target membership for its branch of the normalizer on these reports. Their total savings were 44.763 nats on the next training-file tape and 32.223 nats on the validation-file tape. The full filter saved 230.724 and 256.422 nats. Reusing the same small correction on two files supports this concrete prediction claim. It leaves transfer to a new checkpoint, language or interactive task open. [All packets and block scores](sparse_transfer_result.json) · [Sparse state dimension and normalized subset loss](FOUNDATION.md#how-many-scalar-error-coordinates-does-a-normalized-predictor-need)

Feature extraction with 256-token rolling context took 6.910 seconds on the training tape and 6.577 seconds on the validation tape on an RTX 3090. Each extraction included the warmup. On 65,536 reporting words, seven warm median CPU times after probability access were 1.940 and 1.893 ms for the two Q15 coordinates and 10.838 and 10.977 ms for the full sparse-format replay. The two-coordinate normalizer used its two named accesses at every reported position. The full format used the positive-sum fallback at seven validation positions. Full-vocabulary probability reconstruction and dense reference scores agreed to $4.45\times10^{-15}$ and $2.11\times10^{-15}$ on the two tapes. The compiled carry survived a restart after word 37. [C kernels](sparse_direction.c) · [Both tape identities and replay](sparse_transfer.py) · [Timing samples](sparse_transfer_timing.json)

## Predicting and generating with sampled access to the Transformer

The frozen correction still tracked the period and newline with the same 12-byte packet. For each of the two existing tapes, the experiment replaced access to their Transformer probabilities during the **update** by empirical fractions from independent base draws. Both update precisions, all four sample budgets and all eight registered seeds were evaluated. The full evaluator retained the actual Transformer probabilities to check the normalized word scores. This is an access experiment on previously used tapes. [Prospective protocol](https://github.com/alan-ai1196/FP/blob/d87a5b1/research/frontier/NEXT.md) · [Bounds for the realized prediction and sampler](FOUNDATION.md#what-does-a-predictor-lose-when-it-can-sample-its-base-but-cannot-read-its-probabilities)

| Base information per update | Nats saved on 65,536 next training-file words | Nats saved on 65,536 separate validation words |
|---|---:|---:|
| Exact probabilities | 44.763 | 32.223 |
| 1 independent sample | 21.698 | 9.154 |
| 4 independent samples | 35.907 | 24.558 |
| 16 independent samples | 41.371 | 28.030 |
| 64 independent samples | 42.283 | 28.991 |

These are the measured signed-Q15 scores, averaged over the eight seeds for each sampled arm. With one independent sample the validation savings ranged from 1.204 to 17.570 nats. For binary64 state the mean added loss from one sample was 19.095 nats on the training tape and 19.823 on validation. The respective fixed-tape upper bounds were 423.118 and 399.363. At 64 samples the measured binary64 differences were −0.181 and +0.120 nats, both small relative to eight-seed variability. The nonnegative lower bound applies to the expectation over all update draws. Independent enumeration of every sample outcome in six short examples gave strictly positive gaps below the proven bounds. For rate 1/2 the gap fell from 0.09517 nats at one sample to 0.03223 at three, with respective upper bounds 0.34063 and 0.11354. [All seed-level results](sample_access_result.json)

The sample-only generator started four independent streams from 256 real context words on the validation file and fed each emitted raw ID back to the checkpoint. Its acceptance function received only a base-sampling callback, the learned names and the current state. Producing 512 words took 537 current-word proposals and 512 separately purchased update draws. The sum of conditional expected proposal counts along the realized paths was 535.662. A dense 50,257-word reconstruction verified each conditional distribution to $6.67\times10^{-16}$. Replaying the accepted IDs and additional base draws independently reproduced all four final four-byte states exactly. The generated-token SHA-256 begins with 2863ec9e and the update-draw SHA-256 with cc46f1be. The 128 parallel autoregressive steps took 0.779 seconds, including the RTX 3090 model, transfer of logits, CPU sampling and full-law checks. The implementation exposes a sample-only interface to the filter while the evaluator computes the full probabilities. This run verifies conditional distributions and execution; it does not evaluate human judgments of generated text. [Causal generator and finite calculations](sample_access.py) · [Native replay](sample_access.c) · [Measured time](sample_access_timing.json)

## Can samples select a useful correction without exposing base probabilities?

The fitter received the observed word class and a multinomial count vector of purchased base draws at each of the original 32,768 calibration positions. It had 33 prespecified choices, the historical 32 frequent token IDs and their complement. The rate stayed $1/512$. The learner estimated the zero-tilt derivative using its pre-observation sampled state and the next observed class. The scored validation update used exact probabilities to isolate the cost of **fitting** through samples. The two validation blocks had already been examined in the earlier transfer study. [Prospective test](https://github.com/alan-ai1196/FP/blob/789f8ec/research/frontier/NEXT.md) · [Sample-only fitting function](sample_acquisition.py)

The exact-read quadratic fit selected the complementary class with Q8 slope $740/256$ and saved 20.966 nats over the 65,536 validation words. All 20 sample-only fits also chose the complement. The four-seed mean savings at 1, 4, 16, 64 and 1,024 base draws per position were 19.259, 20.439, 20.857, 20.948 and 20.961 nats. At one draw, savings ranged from 17.877 to 20.247. The budgets cost 32,768 through 33,554,432 logical purchased draws per fit. Direct multinomial simulation made it possible to compute the sufficient count vectors without invoking the Transformer separately that many times.

The simultaneous 95% bounded-difference certificate selected the zero correction at every budget. At 1,024 draws its threshold was 21.444 in total-gradient units, while the largest absolute estimated gradient across the four fits was 13.358. The empirical selection therefore supplied no positive conservative training guarantee under that particular bound, despite its realized score. The complementary class requires access to the entire named set to determine membership or mass. This tested acquisition of one gain and one choice among supplied categories. It gives neither sample-only counting at deployment nor evidence of a newly discovered word identity. [Exact-read comparison, all choices and validation scores](sample_acquisition_result.json) · [Scope of the guarantee](FOUNDATION.md#what-does-a-predictor-lose-when-it-can-sample-its-base-but-cannot-read-its-probabilities)

## Can prediction errors choose a directed connection from samples?

The learner saw the observed words and counts of purchased base draws at 32,768 old Transformer calibration positions. It compared all 52,272 combinations of a source class, an output class, one of three decay rates, and a signed gain. Both ends could be any of the historical 32 raw names or their fixed complement. A learned connection can reuse a state already paid for by another output. The fitter chose up to three connections with distinct outputs using simultaneous lower bounds on true normalized log gain, under installation caps of 32 and 96 bytes. The confidence allowance covered both caps, every candidate, all five budgets and all four seeds. Subsequent test files were outside the scored ranges of the previous investigations. [Prospective fit and file identities](https://github.com/alan-ai1196/FP/blob/8bc761f/research/frontier/NEXT.md) · [Frozen packet bytes and deletion registration](https://github.com/alan-ai1196/FP/blob/dd990a1/research/frontier/NEXT.md) · [Certificate](FOUNDATION.md#which-prediction-errors-justify-a-connection-between-different-word-classes)

| Draws per word during fitting and replay | Training file, 32-byte cap | Validation file, 32-byte cap | Training file, 96-byte cap | Validation file, 96-byte cap |
|---:|---:|---:|---:|---:|
| 1 | 0 | 0 | 0 | 0 |
| 4 | 0 | 0 | 5.045 | 4.186 |
| 16 | 4.439 | 12.344 | 25.045 | 28.194 |
| 64 | 57.849 | 46.277 | 65.994 | 55.866 |
| 1,024 | 96.623 | 55.231 | 96.623 | 55.231 |

Entries are nats saved relative to the frozen Transformer across 65,536 fresh reporting words per file, averaged over four independent receipt tapes. Each replay first observed 4,096 warmup words. At one draw the certificate retained the base in every fit. At four draws one of four fits installed a complementary-class rule under the larger cap. At 16 draws all four smaller installations selected the period. At 1,024 draws all four fits under both caps selected identical bytes. One signed-Q15 state stored the period residual and one stored the newline residual, both at rate $1/512$. The word IDs 13, 198 and 379 decode to a period, newline and the GPT-2 token with a leading space followed by “at”. The first state tilted the period by 16 times its value and the “at” token by 32 times its value. The second tilted newline by 16 times its value. Three rules used 24 installed bytes and four bytes of live carry.

The complete 24-byte packet saved loss on all four fresh blocks. Its cross-class rule had **negative total marginal value on both files**. Removing just the period-to-“at” rule improved prediction by 0.746 nats on the training file and 4.922 nats on the validation file, with matched sampled histories. Its block-level marginal savings were $(-1.584,+0.838)$ and $(+1.144,-6.067)$ nats. At the same 1,024-draw deployment budget the previously frozen probability-trained period/newline rule saved 107.395 and 74.662 nats with twelve installed bytes and the same four-byte carry. The earlier sample-trained complementary-class model saved 69.968 and 43.249 nats. The fixed 132-byte static calibration saved 23.371 nats on the training file and lost 12.150 on validation. Exact-probability updates of the new packet saved 96.922 and 54.900 nats. These comparisons identify a useful sampled history and a particular learned connection whose calibration performance did not transfer. [All four blocks, baselines and deletions](receipt_replay_result.json)

At the highest budget the new programs certified 39.222–39.861 total training nats, before the 0.520-nat installation price, and their independently checked realized gains were 66.57–66.88 nats. The separate reverse-filter certificate for the ideal binary64 diagonal gave 0.854–1.442 training nats at 16 draws and 14.061–14.246 at 1,024. The earlier bounded-differences interval selected zero at all budgets. One rational test enumerated all 81 count sequences, reproduced the chronological martingale decomposition on each, and gave exact score variance $6942241/217005075$. The certificate covers the fixed calibration words. The fresh-text numbers are measurements. [Every fitted packet and certificate](receipt_selection.json) · [Independent small calculation](receipt_control_result.json)

Fitting took 0.454–0.476 seconds per fit in the recorded single-thread run after count simulation and compilation, excluding evaluator checks. The full search shared 32,768 to 33,554,432 logical base draws per fit. The 1,024-draw deployment purchased 71,303,168 further draws per file including warmup. These experiments simulated sufficient counts from the archived probabilities, so the logical query counts differ from measured Transformer evaluations. Dense acquisition used 33 source columns at a time, including about 8.65 MB for a single binary64 $32768\times33$ array. The full checkpoint's 256-word-context extraction took 6.775 and 6.794 seconds on an RTX 3090. The native 24-byte program took median 2.964 and 2.956 ms for 65,536 words with probabilities and update frequencies available in memory, excluding their production. Its four-byte carry excludes predecoded instructions, evaluator buffers and generator randomness. The expected rejection proposals per emitted word on the four forced-text blocks ranged from 1.114 to 1.244 in the four-seed mean. All checked full-vocabulary NLLs agreed within $1.8\times10^{-15}$ and a native restart after word 37 reproduced uninterrupted scores and final carry. [CPU kernel](sparse_direction.c) · [Evaluation and replay](receipt_replay.py) · [Hardware receipts](receipt_timing.json)

The four-symbol controlled source isolates the capability missing from own-class memories. The best possible own-class population gain is zero and the restricted fit correctly chose the base. Both packet caps selected two cross-output rules sharing one signed-Q15 state. Their 23-byte installation saved 101.260 nats on an independent 32,768-word report using 16 independent uniform draws per word. An ordinary add-one transition table learned from the same training words saved 2,656.008 nats, against 2,667.995 for the known transition law. Its four-by-four uint32 count array uses 64 bytes plus the previous symbol. The one-step table captures a dependence for which the registered slow recurrent filters were inefficient. [Controlled results](receipt_control_result.json) · [Population separation](FOUNDATION.md#which-prediction-errors-justify-a-connection-between-different-word-classes)

## Learning one private bit that helps every source

The writer sees a cue once, writes one private bit, and loses access to the cue. The reader sees that bit and forecasts an ordinary binary outcome. Training files are identified, while the deployed reader receives no file label. In the controlled family each of $m$ sources distinguishes one pair of neighboring cues in a hidden order. Names and source order were permuted before calibration. One deterministic bit cannot improve every source for $m\ge2$. The exact optimum for a randomized bit, including the price of finite random precision, follows from the signed cue residuals. [State-count theorem and proof](FOUNDATION.md#how-many-memory-states-can-improve-prediction-in-every-training-environment) · [Prospective acquisition protocol](https://github.com/alan-ai1196/FP/blob/91849de/research/frontier/NEXT.md)

| Training sources | Pairs per source at first tested nonempty fit in all three seeds | Worst-source population gain at 1,048,576 pairs per source, range over seeds | Optimal private-bit gain |
|---:|---:|---:|---:|
| 2 | 4,096 | 0.013941–0.013945 | 0.013954 |
| 4 | 65,536 | 0.001167–0.001203 | 0.001251 |
| 8 | 1,048,576 | 0.0000690–0.0000766 | 0.0000965 |

Gains are in nats per forecast relative to a fair bit. The finite learner fitted a linear program from ordinary cue/outcome counts, rounded the writing probabilities to a 256-step grid and calibrated its readout using a simultaneous population lower bound. Neither the required ordering nor the planted probabilities entered the fitting function. For three cues and the largest sample size all seeds learned the writing probabilities $0,1/2,1$ in the hidden order. For nine cues all found a strictly increasing finite ladder. All nine largest-budget fits earned positive population gain in every source. At eight sources and either smaller budget the same certificate chose the empty packet. At the largest budget the pooled deterministic fit's mean worst-source gains over seeds were $-0.01608,-0.00198,-0.00025$. Giving the reader the exact cue and averaging the learned predictions increased the respective mean worst gains to $0.01838,0.00169,0.000094$. Individual 32,768-pair test reports for the eight-source case ranged from a loss of $0.0000990$ to a gain of $0.0001208$ nats per word despite the small positive population values. [All fits, known-source risks, raw reports and finite checks](robust_bit_result.json)

The successful packets use 10, 14 and 22 bytes on the shared contiguous cue alphabet, comprising a two-byte header, a uint16 readout and one uint16 table entry per named cue. One physical bit crosses the writer–reader boundary. A deterministic full ordering of nine cues needs at least nine messages, or four bits in a fixed-width layout. At the largest training size, the fitted Q8 probabilities would require mean 0.333, 1.063 and 1.512 ideal fresh fair bits per cue under optimal variable-length writes, averaged over seeds. The actual independent-report simulation used a uniform byte per write. The linear program had $m+2$ real variables and $m$ source inequalities plus box constraints. The count simulation retained $2m(m+1)$ integer cells and consumed 2,097,152 to 8,388,608 independent-pair equivalents at the largest budget. The untagged pooled experiment cannot identify whether a uniformly useful bit exists. The resource comparison requires a reset trial and scoring the reader's realized forecast. [Acquisition, packet reader and physical bit calculation](robust_bit.py)

For sequential unary cues, the corresponding uniform guarantee can require arbitrarily many physical states even with a binary report. Across all 1,114 deterministic transition-map/reset pairs through four states for each modulus 2 through 9, the exact finite test matched the least-prime-divisor threshold whenever that threshold lay in range. For moduli 5 and 7 no tested machine was feasible. The separate proof includes stochastic transitions, a positive-but-vanishing transient construction and a sharp finite-window rate for two states at odd moduli. The enumeration uses known transitions to check the proof and makes no acquisition claim for the unary machine. [Streaming theorem](FOUNDATION.md#a-streaming-writer-can-need-arbitrarily-many-states-to-transmit-one-useful-bit)

Lean 4.36.0 checked the finite-grid feasibility equivalence for arbitrary chain length, grid size and minimum increment, together with the paired cue inequalities that imply the garbling bounds after averaging. The proof uses the standard library and has no admitted goals. The entropy, learning and Markov-chain arguments are written proofs. Separately, exhaustive numerical checks over 22,061 increasing grid encoders verified the finite-precision loss formula for chain lengths two through five and one through four private fair bits. Across five finite odd-clock windows, the two-state transient construction and a grid of stochastic transitions also satisfied the proved finite-window bounds. [Lean source](PrivateBit.lean) · [Numerical and rational checks](robust_bit_result.json)

## Learning reversible updates from ordinary noisy reports

**EMPIRICALLY OBSERVED, controlled sources.** Both experiments were committed before fitting. The unary learner received only the four observed sign-pair counts at each lag 0–20, a capacity ceiling of 20, and a noise-amplitude interval. Hidden size 19, cycle lengths, signs and noise were private to the simulator. Multinomial simulation is exact for independent reset episodes at fixed lag. Resource counts below are the ordinary physical workload represented by the simulation. The registered simultaneous intervals cover all 252 pair-product means with probability at least 0.95 under the stated model. The integer certificate covers the normalized correlations. Report probabilities also use the independently needed marginal and scale, estimated from these same counts. [Frozen registration](https://github.com/alan-ai1196/FP/blob/3d4b9a2/research/frontier/NEXT.md) · [Source](reversible_pairs.py) · [Every fit and loss](reversible_pairs_result.json)

All three seeds abstained at 4,096 pairs per lag. Each of the nine larger fits identified the same degree-16 integer recurrence and the orders 1, 2, 3, 4, 5 and 7. Its period is 420. The first successful budget represents 1,376,256 resets, 2,752,512 ordinary reports and 13,762,560 raw advances per fit. Every recovered recurrence streamed the correct numerator at every step through 100,420. The table gives the range over three fits of mean conditional excess nats per final report over lengths 100,001–100,420. Each of the two registered evaluation ranges covers a full true period.

| Pairs per lag | Certified recurrence or abstention | Nonnegative frequency fit | Two-state fit | Fitted period table |
|---:|---:|---:|---:|---:|
| 4,096 | .007366–.007369 | .000264–.001791 | .007303–.007359 | .008494–.008845 |
| 65,536 | 4.56e−7–1.73e−6 | 1.90e−5–4.45e−5 | .007318–.007320 | .008326–.008466 |
| 1,048,576 | 2.63e−8–1.66e−7 | 2.20e−6–5.89e−6 | .007322–.007325 | .008437–.008473 |
| 16,777,216 | 1.96e−9–4.88e−9 | 3.64e−8–3.67e−7 | .007323–.0073235 | .008416–.008425 |

The frequency fit used the complete cosine dictionary of rational frequencies with orders through 20, nonnegative weights summing to one, least squares on the product moments, and a $10^{-9}$ squared-weight penalty. It gave the best held-out scores at the smallest budget. At the first successful budget the marginal alone scored .007366–.007367. The period table fit product counts with $p=1,\ldots,21$ and BIC rent $\frac12p\ln(\text{purchased pairs})$. All 12 fits chose 21. The two-state comparison minimized squared correlation error in $a+(1-a)\lambda^l$ over 4,097 possible $\lambda$ and continuous $0\le a\le1$. All predictions used the same measured marginal, and all final probabilities were clipped to $[1/16,15/16]$. The evaluation supplies lengths to score the baselines. The deployed recurrence processes each advance sequentially.

**EMPIRICALLY OBSERVED, all-report forecasting and transfer.** Three unknown self-inverse raw letters moved a uniform hidden position. The learner received ordinary sign votes, could return along a traversed path, and bore the cost of every action and read. Across all three seeds it constructed successively 2, 4, 6 and 8 signature classes. Its four retained tests were the empty word, raw letters 1 and 2, and raw word 12. All 24 acquired transitions and eight old signs agreed with the hidden simulator up to inferred class names. The construction per fit used 400 resets, 10,200 ordinary actions and 765,000 reports. Calibration of the old noise and an unseen terminal report used another 1,024 resets, 8,192 actions and 923,648 reports, including all repeated signature votes. Only one additional old and one new sign per calibration position were used as target observations. New class probabilities used add-one smoothing. [Simulator, acquisition and predictors](reversible_reports.py) · [Per-seed loss, packets and costs](reversible_reports_result.json)

The following means weight the three fits equally. Each length supplied 128 independent test episodes per seed and one initial noisy report. Every subsequent report was forecast before revealing it. Excess is conditional KL against the true filter on those sampled histories. The machine-readable receipt also has realized negative log loss. The first-report baseline knows the entire fitted transition table and receives the initial sign and every action. It discards intervening sign observations.

| Raw advances | Fitted filter, ordinary | First report, ordinary | Marginal, ordinary | Fitted filter, new terminal | First report, new terminal | Marginal, new terminal |
|---:|---:|---:|---:|---:|---:|---:|
| 16 | .000157 | .15952 | .18602 | .001868 | .24447 | .27186 |
| 128 | .000164 | .25822 | .28408 | .001967 | .28919 | .31548 |
| 1,024 | .000163 | .27648 | .29812 | .002091 | .29479 | .31970 |

Conventional Moore partition refinement over the purchased final-round observations, followed by log-likelihood tracking of all possible initial classes, reproduced every fitted probability to within $4.8\times10^{-15}$. The finite-state construction uses explicit return actions, independent observation noise, and uniform resets. These are substantive assumptions for applying it to ordinary passive data.

**NUMERICALLY VERIFIED.** Exact rational enumeration covered all sign assignments to a representative of every cycle type through seven positions, 2,962 sources in total. The longest necessary lag bound held for every source pair, including pairs of different hidden sizes under the same ceiling. There were 64 different complete pair-correlation laws through size seven. A 24-position example raised an individual denominator from an initial maximum of three to six. Exhaustive action exploration on the eight-state source found 56 distinct endpoint orbit vectors of linear rank eight. Exact parity-slice enumeration for $k=2,\ldots,6$ gave one-pass total variation $(3/4)^k$. At $k=4$, optimal adaptive repeated-reading success was $337/512$ at four reads and $481257529/536870912$ at twelve. Lean 4.36.0 checked the integer parity-likelihood factorization and erasure by an uninformative coordinate for every finite list of coordinate likelihoods. The adaptive sample bounds and the Gram and quotient proofs are mathematical arguments in the foundation. [Independent small-law audit](audit_reversible.py) · [Lean source](ParityReports.lean) · [Proofs and assumptions](FOUNDATION.md#learning-a-reversible-transition-from-short-noisy-report-pairs)

**EMPIRICALLY OBSERVED, execution price.** A native C run resumed each machine after 37 steps and compared every released value. For 1,048,576 raw unary advances the degree-16 integer recurrence took 15.24 ms median, used 34 installed shape bytes and 17 carry bytes. A table compiled from the same recurrence took .69 ms with 423 shape bytes and two carry bytes. A post-registration divisibility compiler examined the learned full period and exactly verified the formula $19c_l=3+4\sum_{m\in\{3,4,5,7\}}1_{m\mid l}$ at every phase. It took 5.22 ms with 17 shape bytes and two carry bytes. All three additionally use the same two binary64 calibration scalars for report probabilities. Timings include releasing every numerator to memory, and exclude the common final probability conversion. The division-based form is available only when the verified period has that structure. The recurrence's actual signed multiply-accumulate bound was 2,071. Each implementation retained its own phase using ordinary advances.

The decoded all-report filter used eight binary64 belief weights (64 bytes per stream), a 48-byte installed packet and 160 bytes of shared decoded tables including the identity move. On 128 independently reset streams, issuing 131,200 predictions took 2.57 ms median. Maximum discrepancy from the Python probability filter was $4.5\times10^{-16}$. Exact evaluation with pinned Foundation R4 replayed both ordinary and new terminal reports over two fresh length-16 paths per fit. All 210 events matched rational Bayes. Each positive program used 82 nodes, 52 products and eight delayed cells. Its unnormalized integer-weight construction needed observed weights of 114–162 bits. The declared bounds cover the tested horizon and grow with its length. These comparisons establish execution of a learned graph and leave ordinary acquisition by historical R4 search unresolved. [Native kernels](reversible_stream.c) · [Measurement driver](measure_reversible.py) · [CPU receipt](reversible_timing.json) · [Pinned R4 replay](reversible_r4.py)

Reproduce from the repository root with Python, NumPy, SciPy and SymPy. Run the two fit scripts, then the independent audit and the pinned R4 replay. The native driver uses a local optimizing C compiler. The Lean proof imports only the standard library.

~~~powershell
$env:OPENBLAS_NUM_THREADS = '1'
python research/frontier/reversible_pairs.py
python research/frontier/reversible_reports.py
python research/frontier/audit_reversible.py
python research/frontier/reversible_r4.py
python research/frontier/measure_reversible.py
lean research/frontier/ParityReports.lean
~~~

## Discovering an unknown input parity at matched observation cost

**EMPIRICALLY OBSERVED.** The learner received noisy ordinary signs and fixed row boundaries. Both inputs and targets were corrupted independently at each read, with known amplitude $1/2$. The simulator chose the unknown mask and its affine offset separately for each seed. A single-pass arm used more independently reset rows. Its paired arm spent exactly the same number of reports rereading fewer persistent rows. Both had to discover which of the earlier raw coordinates predicted the last sign. [Frozen registration](https://github.com/alan-ai1196/FP/blob/e79bc90/research/frontier/NEXT.md) · [Simulator, fit and scoring](affine_reports.py) · [Every fitted mask, failure and held-out loss](affine_reports_result.json)

At dimension 12, the terminal bit depended on five of eleven earlier bits. The search baseline evaluated the full likelihood for all 4,096 signed affine masks, charged $\ln4096$ nats to install one, and used all observed counts. On one-pass rows it aggregated correlations with a Walsh–Hadamard transform. On repeated rows it evaluated the posterior likelihood of every candidate using log probabilities for both agreeing and contradicting votes. The elimination learner solved a binary linear system on the majority signs in each row. An inconsistent or rank-deficient system abstained. Each cell counts how many of the three seeds recovered the true mask and offset. All remaining fits abstained.

| Reads per fit | Single-pass rows | Rows with 97 reads per coordinate | Single-pass elimination | Single-pass likelihood | Repeated elimination | Repeated likelihood |
|---:|---:|---:|---:|---:|---:|---:|
| 9,312 | 776 | 8 | 0 | 0 | 0 | 0 |
| 27,936 | 2,328 | 24 | 0 | 0 | 3 | 3 |
| 148,992 | 12,416 | 128 | 0 | 0 | 3 | 3 |
| 1,191,936 | 99,328 | 1,024 | 0 | 3 | 3 | 3 |

At the first successful repeated budget the three eliminations performed 108–117 row XORs. A repeated fit paid 264 forward coordinate advances, versus 25,608 for its matched single-pass fit. The chronological source reveals many more fresh rows to the one-pass learner. Exhaustive likelihood eventually recovered all three rules there too. The unstructured fair target scored $1.22075\times10^{-4}$ excess nats per terminal on one-pass deployment. The same fair prediction cost .10620–.10739 nats when deployment provided 17 earlier reads per coordinate. In this known-channel model, an exactly recovered mask and intercept give the oracle conditional distribution.

At dimension 64, 31 of 63 earlier bits belonged to the hidden mask. At **595,968 reports per fit**, all three repeated fits recovered the full rule from 96 reset rows and 6,048 raw advances, using 2,038–2,067 row XORs. The matched single-pass arm had 9,312 rows and 586,656 advances. Its elimination encountered a contradiction in all three seeds. The separate information bound applies to every possible single-pass acquisition algorithm under the specified random-support test. Even granting the offset and support size, error at most one third requires more than $9.9\times10^{20}$ expected support-covered rows in this problem. The scale follows from $M=\binom{63}{31}$ and $C(2^{-32})\simeq2.71\times10^{-20}$. No exhaustive 64-coordinate likelihood search was run. [Acquisition and state-count proofs](FOUNDATION.md#discovering-which-earlier-observations-to-combine)

For each held-out condition, every fit was scored on 2,048 fresh rows per seed. Knowing the 64-coordinate rule gained only $2.71\times10^{-20}$ nats over a fair final bit in one pass. With 17 reads of each earlier coordinate it gained .03602–.03669 nats per final bit on the sampled histories, or .0000336–.0000342 per ordinary report counting all 1,072 reports in a row. An identified computation can be valuable on a richer later observation interface while having negligible value on the acquisition interface. Negative log loss on the actual terminal signs and conditional KL are both in the receipt.

**EMPIRICALLY OBSERVED, physical execution.** The native binary predictor issues a probability before every ordinary sign, including those within a repeated input coordinate. Its 8-byte carry stores a Q31 confidence product, the current coordinate, read count, number of observed ones, and running parity. For $d=12$ and 64 the installed packets occupy 5 and 11 bytes respectively, including three header bytes. Its common calibrated BSC table occupies 8 bytes at one read and 72 at 17. Margins index rounded rational posteriors $(3^j-1)/(3^j+1)$. Rounding each selected factor and its product costs at most one Q31 unit per selected coordinate, hence the terminal absolute probability error is at most $|S|/(4\cdot2^{31})$. The driver split streams during a row and verified restoration of the initial state after the terminal report. At $d=64$, 2,195,456 scalar predictions took 7.28 ms median on this CPU with 17 repeated reads. The maximum terminal discrepancy across all seeds, dimensions and repeat conditions was $6.68\times10^{-10}$. [C kernel](affine_report_stream.c) · [Measurement driver](measure_affine_reports.py) · [Timings and carry checks](affine_reports_timing.json)

Pinned Foundation R4 matched all 296 reset and transition evaluations in the two acquired one-pass machines for seed 173. The reachable state counts were 21 and 126, exactly the chronological minima for the respective learned masks. The scalar programs used 89 and 509 nodes. This checks all future one-pass continuations by closure of their reachable states. It tests the installed representation and the raw-symbol clock. Acquisition was performed by the stated learners. [Exact R4 comparison and independent checks](audit_affine_reports.py)

**NUMERICALLY VERIFIED.** Direct latent-state summation checked 576 small one-pass and repeated-read likelihoods. Exact rational computations reproduced all entries of two three-bit observation Gram matrices and found the adaptive off-diagonal entry $1/2$. Two different observation schedules with equal quadratic visibility had actual log gains .031584 and .032142 nats. Exact enumeration checked 4,004 hard-budget visibility comparisons over four possible inputs and all support sizes. Strict discrete quadratic concavity held through 17 reads at five rational noise amplitudes from .1 to .99. A separate 75-digit calculation checked 400 scalar log-gain second differences, and exhaustive allocation comparison checked the hard-cap log-gain optimum in 660 cases. With two fair bits and four purchases at amplitude $1/2$, exact posterior enumeration and independent dynamic programming gave adaptive squared two-bit visibility $587/3200$, versus $4/25$ for the best count schedule fixed in advance. Dynamic programming over the actual terminal log score raised the best fixed .020356 nats to .023293. [Observation spectrum and budget proofs](FOUNDATION.md#what-an-observation-budget-reveals-about-an-arbitrary-prediction-rule) · [Finite checks](audit_affine_reports.py)

~~~powershell
$env:OPENBLAS_NUM_THREADS = '1'
python research/frontier/affine_reports.py --output research/frontier/affine_reports_result.json
python research/frontier/audit_affine_reports.py
python research/frontier/audit_affine_reports.py --r4
python research/frontier/measure_affine_reports.py
~~~

## Transferring a prediction without joint labels

**NUMERICALLY VERIFIED, exact arithmetic.** Training provides the two old-to-other joint tables and three independent same-view twin tables. No new-view/target pair is observed. In the registered fair deterministic example, enumeration of the six moment constraints on eight hidden sign triples found nine feasible basic supports and attainable new-view/target correlation endpoints 0 and 1. The lifted nonnegative PSD Gram accepted $-1/2$. Fixing the missing moment at $0,1/4,1/2,3/4,1$ required respectively $6,7,5,6,4$ positive atoms by a second rational support enumeration. The physical minimax agreement forecast was .8 with worst conditional KL .223144 nats. The PSD interval gave .679131 and .386942 nats. The old-view projection gave .625 and .470004 nats. [Population proof](FOUNDATION.md#what-ordinary-paired-observations-identify-across-an-unfamiliar-view) · [Frozen design](https://github.com/alan-ai1196/FP/blob/71df582/research/frontier/NEXT.md)

**EMPIRICALLY OBSERVED, calibration at equal raw-report budgets.** Each learner saw two unlabelled crossed pair panels of $L$ fresh resets apiece, and spent $2L$ more old signs on either $L$ fresh twin panels or one persistent reset. The target was the next ordinary sign after a new-view sign. All 108 fitted uncertainty intervals were consistent and contained the true deployment correlation. The table reports the three-seed means of population conditional KL in nats per target. Each comparison shared its two crossed panels. [Learners, exact checks and replay](view_transfer.py) · [All data, fits, probabilities, intervals and packet bytes](view_transfer_result.json)

| Old amplitude | Pairs per crossed panel | Fresh twin center | Persistent center | Fresh twin profile | Persistent profile | Known amplitude | Single-old projection |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1/2 | 16,777,216 | .000000028 | .000000220 | .000000033 | .000000217 | .000000153 | .075866 |
| 1/8 | 1,048,576 | .012467 | .00004391 | .0013814 | .00002669 | .00007211 | .126899 |
| 1/32 | 256 | .130812 | .130812 | 1.068995 | .871434 | 1.038596 | .131467 |
| 1/32 | 16,777,216 | .017280 | .00006826 | .007554 | .00001954 | .00000777 | .130566 |
| 1/32 | 67,108,864 | .017962 | .00001791 | .007192 | .00001850 | .00000807 | .130569 |

A fair prediction cost .130812 nats throughout. At amplitude $1/32$ and $L=16,777,216$ each fit paid 100,663,296 modeled reports. The two arms required 50,331,648 and 33,554,433 reset episodes respectively. Their mean correlation interval widths were .77703 and .14247. Both centers returned a fair prediction at the two smallest budgets for this amplitude. At fixed high amplitude and large budget either arm can win on the sampled counts. The family-level lower and upper read orders are $a^{-4}$ for fresh old twins and $a^{-2}$ for persistent old reads at fixed accuracy and confidence. Those population statements use the two-world testing argument. The finite table comes from multinomial and binomial sufficient-statistic simulation. Its counts price every ordinary report, while wall-clock generation uses aggregate draws. The conventional likelihood fit profiles the other two amplitudes analytically and uses a grid with local one-dimensional refinement for the old amplitude. [Identification and cost proof](FOUNDATION.md#how-much-ordinary-calibration-buys-a-transferable-prediction)

**NUMERICALLY VERIFIED, causal execution.** Two signed Q15 bytes install a fitted correlation. One byte holds the live phase and previous sign across event calls. A fair pre-$D$ forecast alternates with the learned pre-$Y$ forecast after either observed $D$. With a nonzero packet these three histories have distinct next-sign probabilities, so any deterministic raw-event predictor matching them needs three live states when no phase label is supplied. Q16 conditional probability error versus the clipped floating forecast was at most $1/65536$. Pinned Foundation R4 reproduced reset and every outgoing transition on 182 distinct installed packets, including the robust categorical example, in 1,274 state and output checks. Its canonical implementation used three delayed cells and 17 scalar nodes. The comparison covers all future sign continuations by closure. [Pinned program generator](positive_comparison.py)

~~~powershell
python research/frontier/view_transfer.py --output research/frontier/view_transfer_result.json
python research/frontier/view_transfer.py --r4
~~~

## Learning a categorical assignment from two crossed pair tables

**EMPIRICALLY OBSERVED.** Three independent sources each had an unfamiliar 12-entry mapping from three old labels and four new labels to three possible targets. The learner received independent self-twin and crossed tables, a 12-atom ceiling and 55 raw count cells. The prior weights, target map, emission probabilities and the deployment $DY$ table were hidden from fitting. Enumerating the 81 possible assignments in each old-label row both evaluated an ordinary conditional log-loss objective and tested the simultaneous coverage certificate. The source generation and scoring rules were frozen before fitting. [Registration](https://github.com/alan-ai1196/FP/blob/2532ab0/research/frontier/NEXT.md) · [Learners and raw-event interpreter](categorical_assignment.py) · [All counts, maps, scores and installed packets](categorical_assignment_result.json)

| Pairs in each of five panels | Exact map by crossed log loss | Full maps certified | Conditional KL, certificate | Crossed log loss | Schur projection | Fitted marginal |
|---:|---:|---:|---:|---:|---:|---:|
| 4,096 | 2/3 | 0/3 | .437079 | .067592 | .404082 | .437079 |
| 65,536 | 3/3 | 0/3 | .433567 | .015649 | .399644 | .433567 |
| 1,048,576 | 3/3 | 3/3 | .003619 | .003619 | .399019 | .434512 |
| 16,777,216 | 3/3 | 3/3 | .000848 | .000848 | .399579 | .434895 |

Entries are three-source means in nats per ordinary target. At 65,536 pairs per panel all latent input cells passed the positivity test, but one row per source retained three different assignments. At 1,048,576 all nine rows had a unique assignment. Each fit then represented 5,242,880 fresh resets and 10,485,760 ordinary reports, drawn in aggregate using multinomial counts. The observable upper bounds on population conditional KL were .05008–.05027 at that budget and .01631–.01641 at the largest budget. On 4,096 fresh evaluation pairs per source the mean excesses of the certified predictor were .003194 and .000582 at those two budgets. The point fit and the certificate matched once the data resolved the assignments. Uniform smoothing of the fitted joint law pulls rare input rows further toward uniform, including in the abstaining marginal model. The three-source average does not give a distribution-free guarantee. The simultaneous certificate has its own stated sampling and capacity assumptions. [Proof and rare-context lower bound](FOUNDATION.md#learning-a-categorical-assignment-from-disjoint-pairs)

**NUMERICALLY VERIFIED, installed prediction.** The interpreter emits four probabilities before every token in the alternating raw $D,Y$ stream. Thirty installed bytes store three uint16 masses per row for one reset and four post-$D$ states. The remaining mass follows by subtraction. One live byte selects a row. All five chronological states were reachable. Of the 36 distinct packets, 34 produced five different forecast rows and two produced three. Their complete R4 replay covered 756 resets and transitions on all four raw inputs, using 39 nodes and five delayed cells. Every fitted output differed by at most $4/65536$ from the corresponding floating-point probability. At the largest budget the installed certified model had mean conditional KL .000874 and consumed .937616 nats per raw test token, versus 1.134862 for the projected model. Oracle mean next-target entropy varied from .49133 to .65036 between sources. This measures the installed head supplied by each acquisition rule.

**FORMALLY CHECKED AND EXACTLY ENUMERATED.** A Lean proof over arbitrary finite lists and decidable label equality checks that one row of powers-of-two label masses uniquely determines its entire target assignment. This is the population combinatorial property of the simulator weights. The finite-data confidence theorem has a separate mathematical proof. Exact enumeration recovered 81 distinct row signatures from the 81 four-input, three-output assignments. A two- versus three-atom rational source check agreed on all five available tables and gave conditional probabilities one and zero on the same deployment input. [Lean theorem](CategoricalMasses.lean) · [Capacity and stability proofs](FOUNDATION.md#learning-a-categorical-assignment-from-disjoint-pairs)

~~~powershell
python research/frontier/categorical_assignment.py --output research/frontier/categorical_assignment_result.json
python research/frontier/categorical_assignment.py --check
python research/frontier/categorical_assignment.py --r4
lean research/frontier/CategoricalMasses.lean
~~~

## How many named labels can aggregate ordinary reports teach?

**EMPIRICALLY OBSERVED.** In 256 sources a future uniform name selected one of 12 unfamiliar binary labels. During fitting a context returned either a name or a target from an independently reset source. No label was paired with its name. Within each of $m$ available groups, independent name counts calibrated an unknown ordering of the reset weights. Each fit paid $B$ target reports and $B$ separate name reports and resets of each type, with counts simulated in aggregate. The oracle-channel comparison received the true order. The empirical-weight fit knew the group names and the fixed binary response model, but received no geometric weight pattern. [Frozen design](https://github.com/alan-ai1196/FP/blob/f7aa7dd/research/frontier/NEXT.md) · [All 15 conditions, Monte Carlo errors, full-token losses and source-0 packets](aggregate_bits_result.json)

| Contexts | Total target reads $B$ | Fitted empirical weights, exhaustive | Fitted rank, exhaustive | Fitted rank, round and soften | Known rank, exhaustive |
|---:|---:|---:|---:|---:|---:|
| 1 | 192 | .10628 | .12920 | .00000 | .13510 |
| 1 | 49,152 | .32325 | .35347 | .18252 | .35347 |
| 1 | 12,582,912 | .55259 | .59862 | .43278 | .59862 |
| 3 | 192 | .24776 | .29815 | .00000 | .32813 |
| 3 | 49,152 | .69313 | .69313 | .61268 | .69313 |
| 6 | 192 | .62082 | .56663 | .00000 | .65147 |
| 6 | 49,152 | .69313 | .69313 | .68208 | .69313 |

Values are means of installed log gain over a fair binary prediction in nats per uniform deployment name. The attainable floor-limited maximum is .693132. The full token head assigns one Q16 unit to each of the ten impossible target letters and prices this mass in the separate all-token score. At $B=49,152$ the general population upper bound was .50787 for one context. At three and six the binary entropy cap was already the tighter upper bound. The confidence-softened decoder returned fair on all three smallest-budget conditions. Its single-context standard error at $B=49,152$ was .00388 across sources. An informative calibrated order improves decoding, but the empirical-weight estimator won over the fitted-order estimator at six contexts and 192 targets. [Upper bound, construction and limits](FOUNDATION.md#how-much-a-finite-number-of-sampling-contexts-can-teach)

**NUMERICALLY VERIFIED.** Exact integer binomial enumeration checked 90 average bit-error inequalities for one to five labels and six sample sizes. Sixty-five half-count regret bounds were checked by rational arithmetic. For the deliberately complementary 4-, 8- and 12-label sources the best equal-prior testing errors after $(2^q-1)^2$ aggregate targets were .158117, .158653 and .158655. On the 12-label pair, 16,769,025 target reads still leave at least 2.6393 nats of summed Bayes next-label loss. This comparison uses a two-source prior which makes all twelve label uncertainties depend on one unknown choice. [Exact checks, decoder and simulator](aggregate_bits.py)

**Physical execution.** Each exhaustive variant evaluates $m2^{12/m}$ assignments per fit, or 4,096, 48 and 24 at the three context counts. Its likelihood accumulates one sufficient count pair per group; the implementation also materializes the binary assignment matrix. The cheap decoder sorts 12 name counts across the groups and rounds one target mean per group. Every method installs 24 bytes for twelve uint16 target masses. A live byte can hold the reset or the last of the twelve input names. On the source-0 rounding packet at the registered middle budget in each condition, pinned R4 matched every full-vocabulary output and destination over 471 resets and edges. It used 207 scalar nodes and 13 delayed cells. A learned value can be looked up after fitting without retaining the enumeration used to acquire it.

~~~powershell
python research/frontier/aggregate_bits.py --output research/frontier/aggregate_bits_result.json
python research/frontier/aggregate_bits.py --check
python research/frontier/aggregate_bits.py --r4
~~~

## Learning an ordinary next-word table from two unpaired panels

**EMPIRICALLY OBSERVED on the original GPT-2-tokenized text files.** A learner fitted a 17-by-17 conditional table from two disjoint panels drawn without replacement from 1,048,576 training positions. One described the old tag and previous word class; the other described the old tag and next word class. For randomized tags, the learner saw neither which positions copied the previous class nor the names paired with training targets. The 16 singleton classes were selected by frequency on an earlier million-word prefix. All other words shared a class and retained their own lexical probability within it. The learner predicted over all 50,257 raw tokens before observing each target. All fitted bytes were published before scoring the two reporting ranges. [Registration](https://github.com/alan-ai1196/FP/blob/7b8ff15/research/frontier/NEXT.md) · [Mechanism-aware control](https://github.com/alan-ai1196/FP/blob/48ec968/research/frontier/NEXT.md) · [Frozen packets and chronological control](https://github.com/alan-ai1196/FP/blob/6a8fe50/research/frontier/text_aggregate_fits.json)

At the largest budget of 524,288 positions per panel, gains over the fitted target marginal were as follows. Both columns use 65,536 subsequent ordinary targets. A positive number is a reduction in nats per word. The common within-class lexical law makes this gain exactly the gain in the class probabilities.

| Acquisition and fitted head | Later training-file block | Separate validation-file block |
|---|---:|---:|
| Random uniform tag, aggregate likelihood | −.00077 | −.00067 |
| 1/8-copy tag, aggregate likelihood | .08743 | .09318 |
| 1/8-copy tag, fitted noise correction | .07736 | .08448 |
| Half-copy tag, aggregate likelihood | .10476 | .11163 |
| Half-copy tag, fitted noise correction | .10685 | .11431 |
| Natural earlier word, aggregate likelihood | −.01529 | −.01029 |
| Natural earlier word, directly use its shifted bigrams | .11246 | .12004 |
| Directly paired context and next word | .11241 | .11994 |

The half-copy likelihood learner retained 93.20% and 93.07% of the paired bigram gain on the respective blocks. The comparator informed of the uniform-copy mechanism estimated a copy rate of .499637 from ordinary matches and retained 95.06% and 95.30%. At the smallest budget of 8,192 per panel, the one-eighth-copy correction *lost* .06365 and .06712 nats per word while the aggregate likelihood gained .01788 and .01839. The pure-noise corrected control selected the marginal at all budgets. Raw NLLs at the largest budget on validation were 7.67309 for the marginal, 7.56146 for the half-copy likelihood, 7.55878 for half-copy correction and 7.55315 for the directly paired head. These values concern a restricted class-bigram predictor on two frozen blocks; the archived Transformer was not run on these targets. [Full word losses, eight chronological subblocks and normalization checks](text_aggregate_result.json) · [Estimator and replay](text_aggregate.py)

**Failure on a natural history feature.** At 8,192 positions per panel the natural-tag aggregate learner gained .02156 and .02308 nats per word. At 524,288 it lost on both files, including all eight later training-file subblocks. Its aggregate training gain meanwhile rose from .00592 to .01071 nats per tag-conditioned target. The held-out weighted TV discrepancy from the factorization was .03556 and .03915 for the natural tag, versus .01235 and .01218 for half-copy tags; these are empirical discrepancies on finite tapes. In the full training window, direct enumeration gave TV $1/1{,}048{,}576$ between $TD$ and $DY$ bigram frequencies. The shift control was added after the first fit and before either report was scored. Every pre-existing packet had identical bytes after the addition. The stationary counterexample explains how the aggregate optimization can select the wrong predictions even at the population level. [Identification conditions, sharp noise prices and chronological counterexample](FOUNDATION.md#when-a-fitted-aggregate-conditional-predicts-the-next-word)

**Acquisition and execution.** All 12 EM fits attained a simplex first-order suboptimality bound below $10^{-7}$ nats per effective training observation. They required 31 to 6,746 iterations using two $17\times17$ raw-count tables, plus working arrays; the natural-tag fit needed the most iterations at the largest budget. A regularized EM step allocates target counts to possible input classes and normalizes with 64 marginal pseudocounts per row. The installed class table occupies 544 bytes with an implicit final mass. Its 16 raw input names take 32 more bytes and the previous observed class fits one live byte. A common dense uint32 lexical mass array takes 201,028 bytes plus its complement denominator; the evaluator used an additional direct-address class lookup. Full-vocabulary normalization errors were at most $4.5\times10^{-16}$ on all audited rows. Pinned R4 reproduced both largest-budget half-copy and natural-tag class machines on both resets and all 578 transitions, using 358 scalar nodes and 17 delayed cells per machine. Lexical expansion was checked separately over every raw word. [All fitting diagnostics and installed bytes](text_aggregate_fits.json)

~~~powershell
python research/frontier/text_aggregate.py fit --output research/frontier/text_aggregate_fits.json
python research/frontier/text_aggregate.py score --output research/frontier/text_aggregate_result.json
python research/frontier/text_aggregate.py r4
~~~

## Learning next-word predictions from matched bag histograms

**EMPIRICALLY OBSERVED.** The learner received only a bag's unordered previous-word and next-word class counts. It fitted a full next-word head by centered cross-covariance or centered ridge regression. All experiments used the same 1,048,576 paired collection positions, 17 classes and 50,257-token lexical law. We froze 107 distinct installed heads before scoring the next 65,536 ordinary words on each file. The three random partitions were independent and nested across bag sizes. [Registration](https://github.com/alan-ai1196/FP/blob/fff0f7a/research/frontier/NEXT.md) · [Frozen packets](https://github.com/alan-ai1196/FP/blob/fe8c98d/research/frontier/matched_word_bags_fits.json) · [Both fresh files and eight subblocks](matched_word_bags_result.json)

| Positions per bag | Bags | Bits for both enumeratively coded histograms across all bags | Matched covariance gain, later train / validation | Matched regression gain, later train / validation | Contiguous covariance gain, later train / validation |
|---:|---:|---:|---:|---:|---:|
| 1 | 1,048,576 | 10,485,760 | .11010 / .10757 | .11013 / .10751 | .11010 / .10757 |
| 4 | 262,144 | 6,815,744 | .10820 / .10584 | .10776 / .10478 | −.27103 / −.26172 |
| 16 | 65,536 | 3,932,160 | .10396 / .10187 | .10335 / .10055 | −.81328 / −.77520 |
| 64 | 16,384 | 1,802,240 | .09312 / .09128 | .09547 / .09228 | −1.04137 / −.98519 |
| 256 | 4,096 | 696,320 | .07273 / .06989 | .08279 / .07672 | −.74454 / −.69644 |
| 1,024 | 1,024 | 237,568 | .04338 / .03975 | .06386 / .05939 | −.41430 / −.38308 |
| 4,096 | 256 | 75,776 | .01534 / .01268 | .03179 / .02747 | −.16050 / −.13841 |
| 16,384 | 64 | 23,040 | .00364 / .00110 | .01151 / .00970 | −.04937 / −.04095 |

Gains are nats saved per ordinary token against a fitted marginal. Each random entry averages three partitions. Directly paired training saved .11010 and .10757. Random size-16 bags preserved 94.4% and 94.7% of those gains under the covariance estimator. Size-1,024 bags preserved 58.0% and 55.2% under the ridge estimator. Shuffling output histograms among bags erased the benefit: at size 16 its mean covariance gains were −.00105 and −.00086. At size 16 the contiguous ridge learner lost 1.02064 and 1.00109 nats per word. These fixed-tape results reflect the actual relationship between preceding and current word histograms. The theoretical iid weak-correlation bound and the fixed-tape randomization variance have separate sampling assumptions. [Bag information and sample cost](FOUNDATION.md#how-much-of-a-joint-law-survives-two-matched-histograms) · [Design-unbiased finite-tape estimates](FOUNDATION.md#what-a-random-partition-of-one-fixed-tape-can-identify)

**NUMERICALLY VERIFIED.** Exact rational enumeration checked the sign-count chi-square formula, first moment and variance at 32 bag size/correlation combinations. On 24 finite-tape problems, 513 complete equal-bag partitions reproduced both the covariance and the exact variance, including singleton bags. All 107 frozen heads normalized over the full vocabulary to within $3.4\times10^{-16}$ on both files. The installed class and lexical representation is the same one audited in pinned R4 in the previous experiment. [Learners, finite enumeration and scoring](matched_word_bags.py)

The bit column is a fixed-length representation bound $2(N/b)\lceil\log_2\binom{b+16}{16}\rceil$. It excludes shared grouping and class definitions. The experiment used arrays of integer counts, without running an enumerative entropy coder. The collector still processed all $2N$ class observations. If a single collector may directly form the joint count table, 288 independent counts of at most 21 bits plus a known total suffice for the entire 17-by-17 joint. If input and target owners can agree on sample positions, they can also send a subset of literal aligned pairs. These alternatives have different resource access and the histogram bound alone establishes no communication advantage over them.

~~~powershell
python research/frontier/matched_word_bags.py fit --output research/frontier/matched_word_bags_fits.json
python research/frontier/matched_word_bags.py score --output research/frontier/matched_word_bags_result.json
python research/frontier/matched_word_bags.py check
~~~

## Shared-position sampling at the same communication budget

**EMPIRICALLY OBSERVED.** Two collectors sent the raw five-bit word classes at an agreed random subset of training positions. The receiver learned its own target marginal from just those positions. Both five-bit streams were actually packed into bytes and decoded before fitting. We froze 43 distinct new class packets before scoring the next 65,536 ordinary words on each of the training and validation files. Both the old bag fits and new paired fits used the same lexical probabilities and 17-class representation. [Registration](https://github.com/alan-ai1196/FP/blob/2852526/research/frontier/NEXT.md) · [Frozen sampled packets and wire lengths](https://github.com/alan-ai1196/FP/blob/5732908/research/frontier/word_pair_sample_fits.json) · [Full fresh word scores](word_pair_sample_result.json)

| Positions per bag | Matched covariance gain | Matched regression gain | Sampled pairs, one per bag in count | Sampled pairs, same bit budget |
|---:|---:|---:|---:|---:|
| 1 | .10111 / .11015 | .10114 / .11007 | .10111 / .11015 | .10111 / .11015 |
| 4 | .09950 / .10806 | .09859 / .10712 | .10081 / .10967 | .10107 / .11003 |
| 16 | .09653 / .10415 | .09556 / .10352 | .09912 / .10784 | .10093 / .10988 |
| 64 | .08677 / .09304 | .08898 / .09500 | .09261 / .10006 | .10063 / .10936 |
| 256 | .06750 / .07295 | .07813 / .08347 | .07374 / .07895 | .09921 / .10797 |
| 1,024 | .03941 / .04357 | .06128 / .06430 | .03561 / .04072 | .09507 / .10302 |
| 4,096 | .01350 / .01668 | .02991 / .03272 | −.02252 / −.01821 | .08429 / .09015 |
| 16,384 | .00285 / .00311 | .01043 / .01219 | −.05517 / −.05158 | .06184 / .06697 |

Entries are gains over the same full-training marginal, in nats per word on the later training-file / validation-file block, averaged over three independent sampling seeds. At 1,024 positions per bag the 29,696-byte budget permitted 23,756 aligned pairs. These retained 94.02% and 93.52% of the full paired gains. The ridge bag estimator retained 60.61% and 58.37%. At the smallest nontrivial bag size and every larger size tested, synchronized samples at the same bit budget beat both bag estimators on the three-seed mean on both blocks. With only as many **sampled pairs as bags**, the result changed: 1,024 sampled pairs produced .03561 / .04072 while using all the positions inside 1,024 matched bags produced .06128 / .06430 with ridge. A group count and a message bit budget measure different physical resources.

At the 1,024-size budget, sampling requires 47,512 selected class reads with direct addressing; the bag collector reads 2,097,152 classes. The Python evaluator loaded the same training prefix and generated a shared permutation in memory. A streaming implementation with a predetermined sampling schedule can still require scanning the tape. Address lists need not be transmitted when the sites share the permutation seed and the same position convention. Separate encoded streams fit the stated budgets including final byte padding. A colocated collector, or an observer of one full shifted word tape, has the cheaper direct-count option described in the theorem. No competitive Transformer claim follows from this fixed class model. [Packed-sample and replay code](word_pair_sample.py) · [Two-party lower bound, attainable protocol and chronological exception](FOUNDATION.md#what-two-separated-observers-must-communicate-to-learn-a-conditional)

## Learning which binary computation fits a separated tape

**EMPIRICALLY OBSERVED.** The receiver knew 4,096 input names and the sender knew their ordinary binary outcomes. On each of 32 seeds we tested an unknown affine operation, an unknown general lookup, and clean, one-error and two-error acquisition for each. The receiver had to choose and fit a program from public linear checks sent by the outcome holder. Only 16 of the 64 names occurred frequently; every other name appeared three times. A matched comparator received actual labels at the same number of shared random positions and integrated over all four registered source/error families. [Frozen experiment](https://github.com/alan-ai1196/FP/blob/97fef68/research/frontier/NEXT.md) · [All tapes reproducible from seeds, learned packets and losses](outcome_sketch_result.json)

| Clean source | Errant reports | Fits recovering entire rule and all error locations | Transmitted outcome bits | Sketch gain | Matched labelled-sample Bayes gain |
|---|---:|---:|---|---:|---:|
| Affine | 0 | 32/32 | 17 | .69313 | .26776 |
| Affine | 1 | 32/32 | 29 in 31 seeds, 74 in one | .69313 | .34575 |
| Arbitrary lookup | 0 | 32/32 | 74 | .69313 | .20103 |
| Arbitrary lookup | 1 | 32/32 | 86 | .69313 | .20408 |
| Affine | 2 | 0/32, all abstained | 86 | .00000 | .60638 |
| Arbitrary lookup | 2 | 0/32, all abstained | 86 | .00000 | .20408 |

Gains are nats per uniform fresh name against a fair target forecast, under Q16 installation. The two-error tapes were outside all four exact classes, so abstention was the intended response of the certificate. Individual ordinary samples still predicted well on the two-error affine sources. Unlike a labelled sample, one dense check combines many raw reports. A clean affine fit used 17 outcome bits but the implementation precomputed 86 check bits from the whole tape, consuming 45,056 pseudorandom bytes before masking, about 2,000 86-bit vector XORs at the sender, and 4,096 descriptor-to-column accumulations at the receiver. Counting 17 messages as 17 raw observations would misstate the result. A corrected general lookup fit reduced on average 16,384 candidate error columns across the search stages and used about 176,178 elimination-pivot XORs. The comparator's 86 positions exposed only 18.84 distinct names on average. Neither method received the hidden generating rule or the bad position. [Acquisition, conventional comparator and execution](outcome_sketch.py)

The affine installation takes a one-byte model tag and one byte holding slope and intercept. The arbitrary lookup takes the tag and eight bytes of values. Both use one live byte to select the current forecast, and both emit a uniform pre-name distribution or one of two positive 64-way pre-target distributions. Historical R4 matched 386 reset and outgoing-token evaluations on one corrected example of each kind, using 327 scalar nodes and three delayed cells. The exact small check enumerated 247 nonzero residuals and found half of all possible check rows missed each, and verified disjointness of the 28 noisy outcome tapes for two names repeated three times with at most one flip. [Acquisition guarantee and dense-noise obstruction](FOUNDATION.md#a-certificate-for-learning-a-computation-from-distributed-outcomes)

~~~powershell
python research/frontier/outcome_sketch.py --output research/frontier/outcome_sketch_result.json
python research/frontier/outcome_sketch.py --check
python research/frontier/outcome_sketch.py --r4
~~~

The comparator's complete 64-name predictive marginals were also checked for all 32 possible observed strings on a five-position tape fragment, independently enumerating both generating classes, observed lookup assignments and possible error locations. For the preceding real-word work, the primary LLP reading identifies exactly where the published event uses the same realized bag, and how reversing feature and class roles yields a population mixture identity under the stated conditional independence. Its iid binary guarantees do not establish the finite-tape word results here. [Full source and proof audit](../../literature/notes/BUSA-FEKETE-2025-NEARLY-OPTIMAL-LLP.md)

The 17–86 bit column above reports forward bits read at the selected threshold. Early stopping needs an on-demand stream or at most three one-bit receiver replies at intermediate checkpoints. A fixed, strictly one-way sender emits 86 bits on all these tapes unless both parties agree on a smaller cap before acquisition. The measured raw processing and pseudorandom generation already used the full cap.

## Recovering a lookup without transmitting its raw error positions

**EMPIRICALLY OBSERVED.** Two observers held separate tapes. The receiver used only its own input names and the public buckets to check whether the complete 32-name lookup would be recoverable for *every* error pattern of the promised size. Only then did it decode the sender's parity message. All 512 fixed one-way messages were generated, sent as packed bytes, scored and reproduced from the registered seeds. Every certified decoding recovered all 32 clean bits. An uncertified design released a fair forecast. [Frozen settings](https://github.com/alan-ai1196/FP/blob/5ec91ee/research/frontier/NEXT.md) · [Per-run results](bucket_rule_result.json)

| Raw rows | Allowed raw errors | Maps certified at 32 / 64 / 128 / 256 bits, each out of 32 | 256-bit mean gain | Same-bit sampled Bayes gain | Distinct sampled names at 256 bits |
|---:|---:|---|---:|---:|---:|
| 1,024 | 1 | 0 / 1 / 10 / 24 | .51985 | .46136 | 21.34 |
| 1,024 | 2 | 0 / 1 / 10 / 16 | .34657 | .56392 | 26.06 |
| 65,536 | 1 | 0 / 2 / 14 / 19 | .41155 | .17734 | 8.19 |
| 65,536 | 2 | 0 / 0 / 3 / 17 | .36823 | .18479 | 8.53 |

Gain is in nats per uniformly chosen future clean name, relative to a fair forecast under the common Q16 head. All successful installations attained .69313. The aligned sample comparator had the exact Bayesian predictive probabilities under the actual uniform random lookup and known count of uniformly placed raw flips. Its comparable clean-label gains at 256 bits were .46231, .56452, .17734 and .18479 in the same row order. On the short two-error tape, the sample clearly beat the all-or-abstain certificate. The long tapes concentrated most new rows on eight common names, so samples usually missed nearly all 24 rare names. A source promising only average accuracy could keep additional uncertain forecasts from failed designs; this experiment required uniform certification before releasing a rule.

Each party processed all $N$ entries for the bucket message. At 256 buckets the ideal independent hash addresses use $8N$ public random bits. The implementation materialized the indices with two bytes per row; the sender buffers 256 parity entries in bytes before packing them into a 32-byte output. The receiver used a byte per cell in a 32 by 256 construction array, plus binary elimination and a syndrome dictionary. Fully checking two errors at this width requires 32,897 syndrome entries including the zero vector. The two-error, 65,536-row runs tested 20,837 on average across passing and early-failing maps. The sampled comparator accesses 256 labels at predefined positions when the data permit direct addressing. The computation released by the bucket receiver is a four-byte table in an agreed name order and a two-way Q16 tilt, with no list of corrupt positions. Large dictionaries and full scans make the message price a partial measure of the physical cost. [Proof, sharp collision lower bound and feedback option](FOUNDATION.md#recovering-a-clean-lookup-without-locating-the-raw-errors)

**NUMERICALLY VERIFIED.** An independent exhaustive decoder checked all 868 rule/error instances on ten certified small designs and the exact distance criterion on another 26 rejected designs. Enumerating clean tables and uniform raw errors checked 56 sampled predictive posteriors. Exact integer hypercube-walk counts checked 528 two-step ball mass comparisons, together with the coordinate-weight monotonicity used in the proof. [Implementation and exact checks](bucket_rule.py)

~~~powershell
python research/frontier/bucket_rule.py --check
python research/frontier/bucket_rule.py --output research/frontier/bucket_rule_result.json
~~~

## Learning a state update from a rare ordinary token

**EMPIRICALLY OBSERVED.** An unknown subset of reachable binary vectors determined the probability of one ordinary target token. When that subset was an affine flat the minimal predictive state tracked a learned syndrome through subsequent toggles. The learner saw answer tokens, with no supplied codimension, latent group labels, basis or token-update table. The toggle action on the raw inputs was supplied to all learners. [Prospective settings](https://github.com/alan-ai1196/FP/blob/e80c919/research/frontier/NEXT.md) · [All 128 clean fits and 320 noisy checkpoints](rare_flat_result.json)

With 12 input coordinates and clean outcomes, the learner stored the affine hull of its positive examples. It stopped after eight additional positive observations inside the current hull without a dimension increase. The stopping rule succeeded on 127 of 128 sources. The one premature stop inferred codimension five for a codimension-four source. The sample bill included every negative outcome.

| True number of required bits | Exact learned states | Mean ordinary labels consumed | Mean positive labels |
|---:|---:|---:|---:|
| 2 | 32/32 | 85.16 | 20.50 |
| 4 | 31/32 | 316.19 | 18.56 |
| 8 | 32/32 | 3,221.25 | 14.44 |
| 12 | 32/32 | 39,776.84 | 9.00 |

The separate noisy experiment used nine raw symbols. Each episode contained six fair setup bits, a geometric number of named toggles, a query, and a binary answer corrupted with probability $1/8$. Sixty-four independent source tapes supplied 294,938 raw tokens and 32,768 answers across their longest prefixes. The predictive mixtures fit all affine flats and all subsets of each eligible cardinality, respectively. Both had the same prior on cardinalities. A third learner weighted these two families by their ordinary answer likelihood, and a fourth installed the individual flat with greatest posterior probability. All forecasts were normalized on the full vocabulary with a positive Q16 floor.

| True source and codimension-equivalent size | Ordinary answers per tape | Exact individual flat fits | Query gain, flat Bayes | Query gain, subset Bayes | Query gain, family mixture | Whole-stream gain, family mixture |
|---|---:|---:|---:|---:|---:|---:|
| Flat, $r=2$ | 128 | 16/16 | .24432 | .14776 | .24432 | .02715 |
| Flat, $r=3$ | 128 | 15/16 | .14300 | .08658 | .14118 | .01569 |
| Flat, $r=3$ | 256 | 16/16 | .14855 | .12609 | .14855 | .01651 |
| Random subset, size 16 | 256 | 0/16 | .01879 | .20490 | .20490 | .02277 |
| Random subset, size 8 | 256 | 0/16 | .04429 | .11852 | .11846 | .01316 |

Gains are nats relative to the true common marginal, which gives the comparison an oracle marginal while withholding every input association. The expected episode length is nine tokens. All heads share the six setup forecasts and the expected two toggle/query forecasts, hence whole-stream gain is exactly one ninth of query gain. At 32 answers forcing one most-probable flat harmed both actual flat groups, by .06351 and .03244 nats per query. The corresponding flat mixtures gained .07854 and .02404. At 512 answers on random sets the mean posterior weight on the flat family was below .0001 in both groups, and the mixture retained the lookup gains of .23608 and .14681 nats. Weight on a generating *family* depends on the specified priors because a flat is also a subset. The target control preserves prevalence and changes continuation structure.

A deployed learned flat uses $r$ live syndrome bits, a protocol phase and its learned XOR masks. In one direct packing of six $r$-bit columns and the $r$-bit target, one rank byte plus the packed parameters takes three bytes for $r=2$ and four for $r=3$. The full membership bitmap takes eight bytes, and a direct chronological evaluator tracks the six-bit input rather than its quotient. At a singleton a direct exceptional address is another cheap representation. The noisy flat implementation considered 26,388 candidates including the empty set. Its dense 26,388-by-64 binary membership matrix occupied 13,510,656 bytes as float64, and each posterior pass multiplied by this matrix in both directions. The subset comparator integrated over its much larger implicit family with prefix/suffix elementary-symmetric polynomials; its two 65-by-65 float64 tables took 67,600 bytes. These are learning costs. An averaged deployment can instead store a probability for every one of the 64 inputs. [Fitted programs, comparators and replay](rare_flat.py)

**NUMERICALLY VERIFIED.** All 175 distinct installed flat programs agreed with direct membership at every reachable input and respected every named update there, an inductive check of 67,200 input/toggle pairs. Exhaustive short tests on three input bits covered 16,640 continuations across 52 candidate sets including the empty set; direct enumeration checked the general-subset posterior over 108 possible sets. A historical R4 encoding of a learned two-bit example used masks 53 and 38 and target syndrome two. Its 25 reachable phase/syndrome states, 294 nodes and 25 delayed cells matched the complete positive nine-symbol laws on all 226 reset and outgoing-token evaluations. The native bit count and this categorical R4 construction price different implementations.

**PROVED and independently attacked.** For two fully independent uniform toggle segments the exact memory curve has strictly increasing gain per additional bit. At fixed noise $1/8$ and eight required bits the best single bit earns .00003847 nats per query. The complete state earns .00566193, or .00070774 per bit. A price of .0003 per live bit therefore rejects every first-bit step but rewards constructing all eight together. This gate concerns optimal fixed-width memory with the true source known. The separate passive learning experiment addresses acquisition, including its failure probability. Decimal calculations at 60-digit precision checked the balanced-cell result over 12,471 partition/noise combinations for up to eight latent values. The entropy proof is analytic. Lean 4.36.0 checked the translation-consistency and future-hit arguments using only the reported foundational axioms. [Loss frontier, rigidity and message price](FOUNDATION.md#an-exact-price-for-constructing-several-predictive-bits-together) · [Formalized algebraic steps](CausalState.lean)

~~~powershell
$env:OPENBLAS_NUM_THREADS = '1'
python research/frontier/rare_flat.py --output research/frontier/rare_flat_result.json
python research/frontier/rare_flat.py --check
python research/frontier/rare_flat.py --r4
lean research/frontier/CausalState.lean
~~~

## Learning token actions without supplying a toggle law

**EMPIRICALLY OBSERVED.** Forty-eight independently noised tapes used the same two uninterpreted raw input letters and one binary answer after a query. The general learner could install any accessible, minimal deterministic predictor with one to four states. It received no state names, transition table, true state count, commutation label or period. Training covered every one of the 255 words through length seven once at the first checkpoint, using 2,048 ordinary raw tokens. Later checkpoints repeated the curriculum 3, 9 and 33 times. The other learner assumed both letters toggle count parities, and fit any of the 16 output laws on that representation. A third learner averaged the two predictive families by their observed likelihood. [Frozen protocol](https://github.com/alan-ai1196/FP/blob/720cb90/research/frontier/NEXT.md) · [192 fitted checkpoints and programs](token_action_result.json)

| Generating action | Independent first-checkpoint fits | Correct general installations on every future word | General Bayes gain per answer | Toggle Bayes gain per answer | Family mixture gain per raw token |
|---|---:|---:|---:|---:|---:|
| Two independent toggles | 16 | 16 | .23873 | .23873 | .00901 |
| Four-cycle and its inverse | 16 | 16 | .24277 | −.48693 | .00916 |
| Four-cycle and a transposition | 16 | 16 | .24953 | −.13258 | .00942 |

Each gain is relative to the true marginal over the held-out inputs, with the same positive five-symbol Q16 protocol for all learners. Held-out words have 24 or 25 input letters and a query and answer, hence an average of 26.5 raw tokens. Conditional expected answer loss was computed on a separate panel of 256 words. Product-state traversal established exact installed behavior on all lengths. All 48 fits remained exact at all later checkpoints. Across these 48 tapes there were four distinct installed toggle languages, four cycle languages and seven order-sensitive languages; repeated languages still had independent answer noise. Balanced short-word exposure was deliberately extensive and every family had a hard state ceiling.

The general learner enumerated 5,477 canonical reachable transition tables and 57,068 distinct minimal rooted machines with binary readout. Its training prediction table used 14,552,340 one-byte entries; scoring formed a float32 copy for exact integer signed counts and float64 posterior weights. With two letters and four states the installed transition table and readout, including its size header, round-tripped through a three-byte packet. One live state uses two bits in addition to the common input protocol. The restricted toggle model represents its entire four-value readout in four logical bits and uses two live parity bits. A uniform size prior over a larger class assigned the structured family substantial dilution: on actual toggle sources the posterior on the general family was about .000071, even though its own best predictor exactly agreed with the true law. These are concrete training and deployment prices.

**NUMERICALLY VERIFIED.** Catalogue sizes at one through four states were 2, 24, 1,028 and 56,014. Exactly 16 machines satisfied both identities, 376 commuted without both squaring to identity, 66 had two involutions that failed to commute, and 56,610 satisfied neither combined property. For four-state predictors, the longest *shortest* witness for noncommutation was six letters and for failure of an individual square law was seven. Testing the candidate defined by both count parities already detected all joint failures in this catalogue through length four. The proof supplies a general binary-letter upper bound of $q+1$. Independently reconstructing future-response rows from the noiseless short words recovered all 48 source laws. Removing redundancy from all labelled two-state machines gave the same 26 distinct one- or two-state behaviors. Checking 126 one-word defects against 43,554 word queries confirmed the constructions and minimal sizes. [Code and complete checks](token_action.py) · [Observation theorem and sharp testing price](FOUNDATION.md#inferring-a-token-action-from-ordinary-continuation-responses)

~~~powershell
$env:OPENBLAS_NUM_THREADS = '2'
python research/frontier/token_action.py --output research/frontier/token_action_result.json
python research/frontier/token_action.py --check
~~~
