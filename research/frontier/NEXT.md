# Next mathematical attack

Ordinary categorical log loss recovered three previously unknown mappings from disjoint pairs. A finite-data certificate needed more information than the point fit, and one additional hidden atom can invalidate perfect transfer without altering the training data. A calibrated categorical marginal can encode all values of a binary mapping in a single real number. Its physical value depends on how precisely ordinary reads can reveal that number. [Assignment experiment](EVIDENCE.md#learning-a-categorical-assignment-from-two-crossed-pair-tables) · [Identification conditions](FOUNDATION.md#learning-a-categorical-assignment-from-disjoint-pairs)

## How many independent label distinctions can a few sampling contexts teach?

A future ordinary input asks for one of $n$ unfamiliar labels. Each acquisition context issues a single binary report from a fresh reset, with a persistent context-specific mean. Determine the number of predictable label bits obtainable from $B$ reports across $m$ contexts even if the learner chooses the next context after seeing its past responses. Compare a genuinely finite readout with an exhaustive Bayesian learner on the same raw observations. Check whether average-source gains hold on a deliberately hard pair, and distinguish externally available sampling operations from computations learned by the predictor.

## Frozen registrations

### Acquiring named label values from ordinary aggregate reports, 2026-11-25

Use 12 names, each with a fixed independently fair binary label, and $m=1,3,6$ contexts. Names form public disjoint equal-size groups. Within each group of $q=12/m$ names, the reset probabilities are a hidden permutation of $2^j/(2^q-1)$ for $0\le j<q$. Each reset returns either a name or its binary target on separate draws. The learner never sees the name responsible for a training target. A future query is a uniform fresh name. For 256 sources indexed $s=0,\ldots,255$, generate the 12 hidden labels with NumPy default RNG [s,4811] and the ordered within-group rank permutations with [s,m,4812]. At total target budgets $B=192,3072,49152,786432,12582912$, use $L=B/m$ name-only and $L$ independent target-only reports per group. For each [s,m,B,4813] RNG draw name counts then a target count in group order. Every arm pays $2B$ modeled reports and resets. Charge the 12-label deployment table separately.

Compare a fair reference to three fits using the same observations. One enumerates all $2^q$ group assignments with independent fair label prior, half-count-smoothed empirical name weights and ordinary binomial target likelihood. The second knows the geometric multiset but learns its order by sorting name counts with name-index tie-breaking, and averages the binomial likelihood over all encoded integers. The third uses that same fitted order, rounds $(2^q-1)\widehat p$ to the nearest integer, and predicts from its bits. Soften bit $j$ using the proved upper bound on its average error from rounding and misranking, capped at $1/2$. Also give the exact geometric order to an oracle-channel Bayesian diagnostic. Report mean prediction gain versus fair in nats per fresh name, actual acquisition work and installed full-vocabulary forecasts. Use one uint16 positive mass per name and one unit for each structurally unused raw target when deploying the alternating 12-letter name/target stream. Check reset and all 156 transitions in historical R4 for the fitted rounding decoder on source 0 at $B=49152$ for each $m$.

Independently evaluate the two complementary assignments whose geometric indices are $(2^q-2)/2$ and $2^q/2$ for $q=4,8,12$. Compare their entire aggregate Bernoulli laws and the optimal equal-prior testing error at $(2^q-1)^2$ target reads. Verify how a low average-source risk can coexist with high ambiguity on this pair. Separate this test from learning on raw text, and preserve the distinction between the known geometric observation design and the unknown label values.

- [Learning a categorical assignment from two crossed pair tables](https://github.com/alan-ai1196/FP/blob/2532ab0/research/frontier/NEXT.md)

- [Transferring a categorical prediction without joint labels](https://github.com/alan-ai1196/FP/blob/71df582/research/frontier/NEXT.md)

- [Discovering an unknown input parity through noisy coordinates](https://github.com/alan-ai1196/FP/blob/e79bc90/research/frontier/NEXT.md)

- [Learning a reversible update from short observations](https://github.com/alan-ai1196/FP/blob/3d4b9a2/research/frontier/NEXT.md)

- [Learning a synchronizing bit](https://github.com/alan-ai1196/FP/blob/f8bae86/research/frontier/NEXT.md)
- [Learning a four-bit synopsis](https://github.com/alan-ai1196/FP/blob/1e6c46d/research/frontier/NEXT.md)
- [Transfer to unused task descriptions](https://github.com/alan-ai1196/FP/blob/1f7b25f/research/frontier/NEXT.md)
- [Learning a response operation](https://github.com/alan-ai1196/FP/blob/9f5fc05/research/frontier/NEXT.md)
- [Binary updates on natural text](https://github.com/alan-ai1196/FP/blob/00cd1ce/research/frontier/NEXT.md)
- [Learning a shared alphabet](https://github.com/alan-ai1196/FP/blob/4c5aa39/research/frontier/NEXT.md)
- [Learning a continuing state update](https://github.com/alan-ai1196/FP/blob/63f6f8f/research/frontier/NEXT.md)
- [Finite probability clocks](https://github.com/alan-ai1196/FP/blob/e98ce50/research/frontier/NEXT.md)
- [Price and acquisition of a delayed computation](https://github.com/alan-ai1196/FP/blob/be51cdd/research/frontier/NEXT.md)
- [Learning a packed update](https://github.com/alan-ai1196/FP/blob/491388e/research/frontier/NEXT.md)
- [A shared bit of three text tokens](https://github.com/alan-ai1196/FP/blob/0680d73/research/frontier/NEXT.md)
- [Learning a raw-token address from full-vocabulary loss](https://github.com/alan-ai1196/FP/blob/afc26fc/research/frontier/NEXT.md)
- [Precision and calibrated raw context counts](https://github.com/alan-ai1196/FP/blob/ed60c61/research/frontier/NEXT.md)
- [Acquiring one output correction from ordinary errors](https://github.com/alan-ai1196/FP/blob/218c31e/research/frontier/NEXT.md)
- [Transfer of a history state to new outputs](https://github.com/alan-ai1196/FP/blob/45f3338/research/frontier/NEXT.md)
- [Learning unfamiliar action meanings from purchases](https://github.com/alan-ai1196/FP/blob/f912975/research/frontier/NEXT.md)
- [Acquiring a smaller update state](https://github.com/alan-ai1196/FP/blob/46fdab6/research/frontier/NEXT.md)
- [Learning both raw sets of a prediction](https://github.com/alan-ai1196/FP/blob/0f45141/research/frontier/NEXT.md)
- [Earlier context after global word-class calibration](https://github.com/alan-ai1196/FP/blob/ae87e2f/research/frontier/NEXT.md)
- [Value of discarded observations across one-stage decisions](https://github.com/alan-ai1196/FP/blob/62ddbdd/research/frontier/NEXT.md)
- [Choosing what sensor to buy from later predictions](https://github.com/alan-ai1196/FP/blob/54506ee/research/frontier/NEXT.md)
- [Learning unknown sensor response classes](https://github.com/alan-ai1196/FP/blob/28e5a3d/research/frontier/NEXT.md)
- [Learning earlier-word response classes on chronological text](https://github.com/alan-ai1196/FP/blob/3b17ced/research/frontier/NEXT.md)
- [Posterior averaging and sequential word-pair prediction](https://github.com/alan-ai1196/FP/blob/8793590/research/frontier/NEXT.md)
- [Cost of a compressed learning state under future observations](https://github.com/alan-ai1196/FP/blob/02832d5/research/frontier/NEXT.md)
- [Acquiring a compact predictor from ordinary paired episodes](https://github.com/alan-ai1196/FP/blob/0940e87/research/frontier/NEXT.md)
- [Unrestricted mixing laws and a purchased reset](https://github.com/alan-ai1196/FP/blob/38c30a6/research/frontier/NEXT.md)
- [Finite prototypes from short unlabelled groups](https://github.com/alan-ai1196/FP/blob/5a9e859/research/frontier/NEXT.md)
- [Learning persistence from ordinary next words without boundaries](https://github.com/alan-ai1196/FP/blob/a6063e0/research/frontier/NEXT.md)
- [Learning a recurrent correction on the frozen Transformer](https://github.com/alan-ai1196/FP/blob/5907fd5/research/frontier/NEXT.md)
- [Selecting and transferring sparse recurrent coordinates](https://github.com/alan-ai1196/FP/blob/c0bf3a0/research/frontier/NEXT.md)
- [Sampling access and autoregressive generation](https://github.com/alan-ai1196/FP/blob/d87a5b1/research/frontier/NEXT.md)
- [Sample-only acquisition of one coordinate](https://github.com/alan-ai1196/FP/blob/789f8ec/research/frontier/NEXT.md)
- [Sample-only directed readouts](https://github.com/alan-ai1196/FP/blob/8bc761f/research/frontier/NEXT.md)
- [Frozen packets, directed-rule deletions and four-symbol control](https://github.com/alan-ai1196/FP/blob/dd990a1/research/frontier/NEXT.md)
- [Learning a private bit across sources](https://github.com/alan-ai1196/FP/blob/91849de/research/frontier/NEXT.md)
