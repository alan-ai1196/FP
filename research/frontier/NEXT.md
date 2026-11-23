# Next mathematical attack

Can ordinary prediction learn a cheaper **state for continued learning** with a quantitative guarantee on the predictions it will make after new observations? The product-partition learner gave a pathwise statistical guarantee yet required substantially more physical memory and update work than the one-class comparator. Keeping its frozen prediction table discarded information needed to perform future updates. The reachable four-row example exhibits this failure after one additional token. [Measured statistical and physical costs](EVIDENCE.md#did-posterior-averaging-improve-next-token-prediction) · [Target observable and safe bounds](INTELLIGENCE_OBJECTIVE.md#pricing-a-compressed-learning-state-by-its-future-predictions)

## Mathematical target

For a declared learner, family of attainable training histories and policy class, price a candidate replacement state by the supremum of forward **observable future transcript KL** over an explicit horizon. Include access to new evidence and the cost of every ongoing update. A full-support approximation to the latent posterior has a horizon-independent KL upper bound, but computing or even storing that posterior can be less practical than computing the observable distributions. Hard pruning can have infinite latent forward KL while its short-horizon observable penalty is small. Determine when cheaper summaries achieve a finite, sharp or estimable *observable* guarantee across the allowed actions and histories. Acquiring an inaccessible simulator is a separate cost.

Start with a mixture of two Bernoulli response laws and a cheaper summary that may merge them, under passive and selected repeated observations. Characterize forward predictive regret from the first observation through the limit, explicitly allowing coincident components, vanishing mixture weight, positive noise and an experiment that distinguishes the components. Find the point at which an initially harmless merge becomes expensive. Then determine whether a shared low-cost residual predictor can cover discarded components well enough to repair hard pruning. A proposed upper bound must handle a future action probing a distinction that its training actions never exposed. Compare direct enumeration, bounds based on coupling whole component processes, and the cost of keeping sufficient counts. Trace any existing likelihood-aggregation or information-geometry result to its original argument before claiming a mechanism.

Return to ordinary text only for a test that can distinguish an advantage over a cheap adaptive comparator. The recent eight-name, single-output-class setup left just 8,081 eligible targets in 262,144 positions. A larger output family or a learned choice of contexts should come with an attainable selection rule, chronological reporting targets, a price for candidate acquisition, and matched conventional language-model scores. An exact derivation on the small mixture may instead rule out the proposed compression. The universal representation and its acquisition law remain open.

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
