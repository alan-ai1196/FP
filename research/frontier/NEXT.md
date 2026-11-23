# Next mathematical attack

Does a class of earlier word identities learned from ordinary next-token likelihood transfer to unobserved raw word pairs on natural text? In the controlled experiment, a preference for fewer occupied conditional parameters yielded correct extrapolation even when one spare response class could reverse any particular missing answer. On real language the same preference could remove useful context. [Controlled result](EVIDENCE.md#can-the-learner-discover-a-sensors-response-classes)

## Registered chronological test of learned response classes

Use the existing 50,257-token training tape, frozen raw-bigram predictor, 256-word output class and its global odds multiplier installed by the earlier text experiment. Start the new test at zero-based target position 7,045,120, immediately after the last reported block. Use 262,144 targets to fit, 131,072 to choose candidates, and then two disjoint consecutive blocks of 131,072 for reporting. Retain the causal two-token context across boundaries. Verify the earlier prefix hash and source file size. Record the extended prefix hash after the first read. The fitted 256-word output class and base model are reused and charged.

Choose the eight most frequent earlier token IDs and eight most frequent current token IDs on the new fitting block, breaking count ties by lower ID. Rank each list by that same order. Only when both names are on their lists may a new predictor change the probability of the frozen output class. Exclude from class fitting every eligible pair whose column rank minus row rank is 0 or 3 modulo 8. The remaining 48 may supply labels. All realized training tokens still count as exposure. On the subsequent blocks score every token with a normalized full-vocabulary law. Also report eligible and withheld-pair occurrence counts and conditional losses. At other contexts use the previous global predictor.

For each current token let $p_v$ be the frozen predictor's probability of the output class. Pool the binary class memberships of the actual next tokens by early-name block and current token. Fit arbitrary partitions of the eight early names into at most four classes by integrated conditional likelihood with a uniform prior on class counts and a uniform prior on partitions at each count. For each Bernoulli probability use a beta prior centered at $p_v$ with concentration 8, 64 or 512. Break score ties lexicographically. Preserve both within-class full-vocabulary distributions. Store the fitted conditional class probabilities in Q16. Include otherwise identical fits with exactly one class (current token only) and eight classes (independent pairs), and the frozen global predictor. Select concentration separately for each family on the selection block by priced loss over all tokens. Report these selections and the overall selection including the unchanged predictor. Use the existing rent of $(\ln 2)/256$ nats per installed bit per 131,072-target block. Charge ID lists, encoding tables and live state, and verify the full-vocabulary normalization and deployed lookup. Compare the previous frozen joint model and full-budget raw trigram on the same blocks, and the historical modified Kneser–Ney and Transformer on the first 4,096 positions of each block with their original budgets.

The primary hypothesis is a lower mean priced full-stream loss for learned early classes than for current-only, independent-pair and globally frozen predictions, with the held-out-pair NLL reported separately. Compare gains on the whole stream against the small subset that can change. State whether the fit selects more than one class and whether any prediction difference transfers to those 16 combinations. Failure to earn the added bytes or failure to improve held-out prediction is a reportable outcome. A scalable candidate would still need a way to learn which names and output distinctions to include.

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
