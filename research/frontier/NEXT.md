# Next mathematical attack

At the same communication budget, directly sampling positions outperformed both matched-histogram learners at every nontrivial tested bag size on two fresh word blocks. For arbitrary separated fixed-alphabet tapes, mean KL and TV have different tight message prices. Exact or nearly exact *structure* is a different regime: a learner can test whether a short computation reproduces an outcome tape without receiving all the outcomes. [Communication theorem](FOUNDATION.md#what-two-separated-observers-must-communicate-to-learn-a-conditional) · [Fresh results](EVIDENCE.md#shared-position-sampling-at-the-same-communication-budget)

## Can ordinary outcomes teach and validate a shorter computation without individual labels?

Give the receiver the inputs, and the sender the synchronized binary outcomes alone. Determine which computations the receiver can acquire and test from parity checks of ordinary outcome bits. In particular, can the learner decide between an affine update and a general lookup without being told which is true, and can it repair a single errant training observation without being told its position? Compare raw reads, public random bits, decoding work, transmitted bits, installed state and honest failure under model mismatch.

## Frozen registrations

### Learning which binary computation fits a separated tape, 2026-11-25

Use $N=4096$ positions and 64 six-bit input names. Each name appears at least three times. For each of seeds 0 through 31 and each of two source types, make the inputs with NumPy [seed,8211]: start with three copies of every name, add independent uniform draws on names 0–15 to fill the tape, then permute. An affine source uses a uniformly chosen nonconstant six-bit slope and a fair intercept; a general source uses 64 independent fair target bits. Generate both with [seed,type index 0/1,8212], rejecting a general table if it happens to be affine. Train on clean output, one flip at a uniformly random position using [seed,type index,8213], and two flips at the first occurrences of distinct well-supported names 0 and 1. Uniform-name deployment asks for the original clean rule; report a fair fallback on a failed exact certificate. Score all source modes, and report rejected two-flip tapes separately.

Both parties know the menu and code lengths; only the receiver has the names and only the sender has the binary tape. Two model bits distinguish affine, affine with one error, full lookup, and lookup with one error. The parameter lengths are 7 or 64 bits plus 12 bits for an error position when applicable. With $\delta=1/256$, try thresholds 17, 29, 74 and 86 transmitted bits in that order. Draw one public random 86-bit column per position from [seed,8214] using 11 little-endian random bytes per column with the high two bits cleared. The sender XORs the columns for positive targets and reveals its sketch in prefixes. The receiver constructs its own feature columns and performs binary elimination. At every threshold try the eligible classes in description-length order, accepting a unique compatible rule and, when applicable, a unique error location. Record errors, abstentions, communication, row coverage, XOR work and which representation was installed.

At the same transmitted-bit count, a comparator receives outcomes at the first shared positions of a uniform permutation from [seed,8215]. It averages the four possible families with equal prior, fair parameters and a uniform error position when present, using the exact likelihood of the named observations. Its target is the clean label. Use a fair fallback if all four likelihoods vanish. Score the installed conditional probability on a future uniform name under both methods. For a complete alternating raw name / target stream the vocabulary has 64 ordinary symbols. Use a common positive Q16 floor of one unit per symbol, uniform before the name and a binary tilt before the target. Use one byte for an affine rule or eight for a complete lookup, plus a model tag and live phase state. Verify each raw transition for one recovered example of each type in historical R4. Exhaustively check the collision/correction argument on small tapes. Arithmetic and random-bit work at acquisition are part of the comparison.

- [Shared-position sampling versus matched histograms at equal communication](https://github.com/alan-ai1196/FP/blob/2852526/research/frontier/NEXT.md)

- [Matched bag histograms for ordinary word prediction](https://github.com/alan-ai1196/FP/blob/fff0f7a/research/frontier/NEXT.md)

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
