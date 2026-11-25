# Next mathematical attack

Ordinary outcomes on short words identified either a toggle, a four-cycle or an order-sensitive transition under a four-state ceiling. What matters for language is the predictive gain on natural histories, including what a fixed suffix or a reader of more of the raw token already provides. [Action and its acquisition cost](FOUNDATION.md#inferring-a-token-action-from-ordinary-continuation-responses)

## Does learning a small token action improve ordinary next-word prediction?

Fit every accessible two-letter update with at most four states on chronological text. Give each update a fitted multiclass readout and compare it with constrained toggles, literal short suffixes and class bigrams/trigrams. Freeze the selected programs before measuring their next-word log loss on two new word blocks.

## Frozen registrations

### Learning an unrestricted finite update on chronological text, 2026-11-26

Use the original 50,257-symbol files and shared first-1,048,576-word lexical law of the previous real-text work. The 16 most frequent training words are singleton output classes, with the other words in one class. Raw tokens in the top eight of that same vocabulary map to input letter one, every other token to zero. This fixed input coarsening and the common within-class lexical probabilities are supplied to all relevant learners.

Fit transition readouts on target indices 9,000,000 through 9,065,535 inclusive of the training file and validate on the following 16,384 targets, continuing the trained-state trajectory. Start the state at zero just before consuming the preceding raw token. Enumerate all 5,477 breadth-first canonically named accessible two-letter transition tables through four states. Fit each state's 17-way output row from its ordinary successor counts, with 64 pseudo-observations of the global half-count-smoothed fit marginal, and install a positive Q16 row with stable largest-remainder quantization. Fit the same way for the constant, literal binary suffix lengths one, two and three, the direct 17-class last word and direct 17-by-17 last-two-word context. For the last-two-class control initialize missing earlier context to class 16. Use zero padding for literal binary suffixes. All heads retain the same full 50,257-word law inside classes.

Select the unrestricted program and, separately, the best commuting involutive transition table, first by mean validation log loss alone, then with 8 ln(2) times packet bytes divided by a prospective 65,536-token deployment horizon added to validation loss. Break exact ties by smaller packet size and then enumeration order. A transition-only header uses two bits for q−1 plus 2q fixed-width destinations; pack to bytes. Store sixteen uint16 masses per output row, with the last determined by normalization. Charge any larger literal-suffix and word-class controls under their known fixed transition rules. Freeze the names, rows, selected maps and validation scores before opening the scored intervals.

Report on training-file indices 11,196,608 through 11,262,143 and reporting-file indices 458,752 through 524,287. Their inclusive-of-data prefix SHA-256 digests are e98695002e61f5057b10ad84199a21b117bd0a3033d13e556f850c24591c88b2 and bccf652efb1b1432a911ae5f057c44cb89ff973db8a0bcadb30de6b662c11543, respectively. Only byte digests were computed before fitting. Reset each head at each reporting block, consume the token immediately preceding the first target, and evaluate true full-vocabulary pre-target log probabilities and eight consecutive 8,192-token block scores. Report gains against the fitted constant, the selected rule's two algebraic properties, comparison to literal suffixes and class n-grams, model bytes and raw training/validation work. Any new structural conclusion must survive the corresponding stronger comparison.

- [Inferring token updates without a supplied algebra](https://github.com/alan-ai1196/FP/blob/720cb90/research/frontier/NEXT.md)

- [Learning a state update from an ordinary rare token](https://github.com/alan-ai1196/FP/blob/e80c919/research/frontier/NEXT.md)

- [Recovering a rule without identifying its corrupted positions](https://github.com/alan-ai1196/FP/blob/5ec91ee/research/frontier/NEXT.md)

- [Learning which binary computation fits a separated tape](https://github.com/alan-ai1196/FP/blob/97fef68/research/frontier/NEXT.md)

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
