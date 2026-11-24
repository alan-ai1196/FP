# Next mathematical attack

Can the learner construct both sides of a useful recurrent computation from full next-token errors of the archived Transformer? The preceding correction received the output set that its single history state tracked. Its larger gain came from an observable error average. Derive how to choose which error direction to retain and which future probabilities it should change. Test whether either is worth its cost on top of the strongest existing language baseline. [Previous transfer](EVIDENCE.md#learning-persistence-from-next-word-errors-without-reset-labels)

## A learned input and output direction on the frozen Transformer

Take the next contiguous 81,920 targets starting at 8,486,912 in the registered training file. Use 32,768 for fitting, 16,384 for selection and two fresh blocks of 16,384 each. The full 8,568,832-token prefix SHA-256 is 465c041d897528e706cca4ba39aa3126496cebb07a3aa7886ec5019899d2083a. Only their byte identity has been inspected. Use the pinned, evaluated 7,253,376-parameter checkpoint 0becbbd8515ac04fb225939cf1e81b594632b4aefd268d0e16f3faa8d16fae9b, its archived rolling-context procedure, and normalized probabilities across all 50,257 tokens. Retain class masses for the 32 most frequent tokens in the old 786,432-token fit and one complementary class. Rank names by count with raw ID as tie breaker. Supply no semantic labels or class chosen from reporting targets.

Let $e_t$ be the one-hot observed class minus the Transformer's predictive class distribution. At rates $1/512,1/128,1/32,1/8,1$, fit on training pairs of current error and the exponentially averaged *prior* errors. Derive a lower bound to the normalized full-vocabulary log-likelihood gain for a low-rank matrix applied to this history. Use its leading singular direction after regularizing the history second moment by $10^{-6}I$ to choose the one-dimensional memory input and readout. Normalize each direction by its largest absolute coordinate. Fit one nonnegative output gain up to 64 on ordinary training likelihood. Deploy only the projected scalar of the history. Include signed Q15 input and output vectors, unsigned Q8 gain, rate code and the named raw IDs in the packet. Also test a 16-bit persistent history value rounded over its fixed attainable interval. Each next-word forecast must precede incorporation of that word's error.

Compare to the unmodified Transformer, a static fit on the same 33 classes, a direct vector error average with one common fitted gain, and a per-class diagonal correction with fitted slopes and 33 live coordinates. Include the earlier frozen 256-token class and its observable residual as a further conventional control, refitted on the new Transformer errors. Include the last-observation rate in the comparison. Count installed and live bytes. Use chronological selection plus the historical installation rent $\ln(2)/256$ per bit to choose rates and the deployed candidate. Charge each named set if transmitted with that predictor. Report all families on both new reporting blocks, and the five-gram on the first 4,096 positions of each. Compare all methods at identical Transformer inputs, report correct raw-word NLL and normalized distributions, and measure both cost of extracting features from the frozen checkpoint and recurrent correction work. An improvement on this tape is conditional on the supplied fixed alphabet, full base probabilities, permitted history filter family and finite covariance fit.

## Frozen registrations

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
