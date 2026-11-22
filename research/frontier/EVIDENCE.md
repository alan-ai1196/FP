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
