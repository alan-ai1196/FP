# Next mathematical attack

Can ordinary next-word likelihood train persistence in a model whose state is latent, with no episode labels or externally announced resets? The off-grid prototype results distinguish knowing possible locations, learning where to forecast, and learning whether a sharp state can be trusted. They assume exchangeability within announced groups. Test the following narrower step on chronological language. [Identification and physical packet cost](FOUNDATION.md#what-does-it-cost-to-learn-and-store-unknown-persistent-prototypes) · [Finite controls](EVIDENCE.md#learning-two-persistent-probabilities-off-the-dictionary-grid)

## A persistent word-class correction learned without boundaries

Use the frozen bigram with its previously learned global output set and scalar correction. It already issues normalized probabilities for the 50,257 raw tokens. At every word let $r$ be that readout's total mass on the output set. A two-state candidate multiplies odds for that set by $e^{\beta_0}$ or $e^{\beta_1}$. Both states preserve relative probabilities within each side of the split. With probability $h$ at each step resample the state from a stationary Bernoulli probability $\pi$ and otherwise retain it. Only ordinary next words and their supplied prefix are visible. Update the probability of state one by the observed word, then apply the learned refresh transition. The fresh reporting blocks form one continuous causal tape. Supply no state labels, latent reset receipts, counters for known group length or report-time parameter fits.

Train on the next 131,072 targets starting at 7,962,624. Use the following 131,072 targets starting at 8,093,696 for model selection. Report separately on the two following blocks starting at 8,224,768 and 8,355,840. Their combined 8,486,912-token prefix has SHA-256 b84d18d7274bd69134041cceb653344329c52765cfbef8626782f80b836a1bbf. The preceding prefix through the earlier experiment has SHA-256 ff12f6daaa6314f30b3a182d1ab3cac4426f01a0765c2170003b2fc6624ccf2f. Only byte identity has been inspected on the four fresh blocks.

Compare the inherited global predictor, one newly fitted scalar, a separately fitted iid two-state mixture, the persistent mixture with a learned refresh rate, and an observed exponentially averaged signed residual with fitted rate, intercept and slope. Supply a paired ablation which sets the fitted persistent model's refresh to one holding its odds and initial weights fixed. Optimize ordinary training log likelihood at multiple initializations. Use $|\beta|\le3$, stationary weights in $[0.02,0.98]$, refresh rates in $[1/2048,1]$, and residual slopes in $[-16,16]$. Quantize log odds and residual slope to signed Q10 and weights/rates to unsigned 16-bit fractions. Select a model only by chronological selection loss with the historical per-bit installation rent $\ln(2)/256$. Report each named candidate, the selected result and the inherited global baseline on both fresh blocks. Report the first 4,096 positions of each against the archived modified Kneser–Ney five-gram and Transformer, with exact checkpoint identities. Those larger trained models have different budgets.

Measure scalar CPU forecasting and update work. Check normalization, pre-observation release, restart, analytic gradients or independent derivative checks, and an independent full raw-word probability calculation. Quantize the persistent posterior into 256 and 65,536 levels on its attainable log-odds interval and score the installed probabilities. Derive explicit numerical stability conditions for this reusable state. Keep acquisition, parameters, lookup tables, shared baseline, dynamic carry and temporary work separate. Any improvement applies to a supplied binary output contrast and a supplied family of updates. A conventional residual or existing language model may win.

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
