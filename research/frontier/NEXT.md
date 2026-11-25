# Next mathematical attack

From disjoint positional panels, the calibrated half-copy tag preserved about 93% of the gain earned by paired bigram training on each of two text blocks. A natural earlier word supplied a directly shifted bigram table, yet fitting a different aggregate relation to that tag lost on both reporting files at the largest budget. What the collector reveals about shared items and chronology changes the computation a learner can justify. [Frozen word-level scores](EVIDENCE.md#learning-an-ordinary-next-word-table-from-two-unpaired-panels) · [Population conditions](FOUNDATION.md#when-a-fitted-aggregate-conditional-predicts-the-next-word)

## How much pairing survives when the input and target arrive as two histograms?

Suppose a collector pairs only the bags of inputs and outputs; correspondence of individual items within a bag is lost. Determine the information per bag about a reusable input-to-output operation, the sample price of larger bags, and which combinations of histogram counts an ordinary learner can actually fit. Account for random partition of a fixed sequential tape. Contiguous bags of preceding and current words share all but their endpoints and can present a spurious apparent copying rule.

## Frozen registrations

### Matched bag histograms for ordinary word prediction, 2026-11-25

Use the same 17 word classes, one-million-word lexical fit, 1,048,576 training target positions starting at 9,000,000 and class-head encoding as the previous experiment. In this experiment the learner receives only the two unordered histograms for each bag of $b=1,4,16,64,256,1024,4096,16384$ token positions. All bag sizes divide $N=1,048,576$. A single group permutation from NumPy [seed,6311] for seeds 173,419,773 makes uniformly random equal-sized bags nested across sizes. Test a matched random partition, shuffle the target histograms across these same bags using [seed,b,6312], and also test chronological contiguous bags. Each construction charges the same $N$ input and $N$ output labels at collection. Bag ordering, bag size, alphabet and grouping protocol are shared. The learner gets neither individual positions nor pairings; it gets an item pairing at $b=1$ by definition.

Let $G=N/b$. For centered input and target count matrices $U,V$, estimate the joint from $\pi\nu^\top+(N-1)U^\top V/[N(N-b)]$ with empirical marginals $\pi,\nu$. Clip negative cells, normalize each input row, and add 64 marginal pseudocounts against $G\pi_d$ effective observations per input. Compare a centered ridge fit using $\Delta=(U^\top U/b+64I)^{-1}U^\top V/b$, the unnormalized output rows $\nu+\Delta_d-\pi^\top\Delta$, then positive-part normalization. Give all heads the same positive Q16 row encoding. Controls are the empirical marginal and the directly paired $N$-position bigram with 64 marginal pseudocounts; use a half-count only for the empirical target prior in pseudocounts and for the independent marginal. Use exact empirical marginals in centering. Distinguish a zero class score from smoothing and actual raw-word loss. Record unique frozen packets, the singular behavior of observed bag design and estimated class gain.

Freeze every fitted packet before looking at the next two 65,536-token report ranges beginning at 11,065,536 on the training file and 327,680 on validation. Their uint16 prefix SHA-256 values are 6a5ba10e3d734d15ee7afc161d0e9bba5671bc07fa71c4f9ea09e36dc0976302 and 48c8f46c59996036aac2fdd76d06e5439ddc32898b25b3b11c43c8b8809fc4b2. Evaluate both full-vocabulary scores, the same common lexical law, the raw communication and the fixed-length enumerative bit budget for exchanging two histograms per bag. Reuse the audited physical class-head representation. Check exact small sign-bag likelihood ratios and the finite-population covariance mean and variance by independent enumeration, including $b=1$ and a size of order $N$.

- [Ordinary next-word transfer and its shifted-bigram control](https://github.com/alan-ai1196/FP/blob/6a8fe50/research/frontier/NEXT.md)

- [Acquiring named label values from ordinary aggregate reports](https://github.com/alan-ai1196/FP/blob/f7aa7dd/research/frontier/NEXT.md)

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
