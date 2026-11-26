# Next mathematical attack

## Can a learned predictive bit become an input to a second useful computation?

Freeze the previously selected 266-bit prediction rule, including its learned raw-word input bit $a=z_0(X_{t-1})$, output signs, calibrated biases and amplitude. Make $a$ available to a second learner on disjoint ordinary text. Given an earlier raw name bin $i$ and next-word class $j$, construct a new signed value $a\,w_i$ and connect it through a learned output direction $s_j$. The ordinary conditional residual weighted by $a$ should yield an exact sign-norm proposal. Characterize when calibrated main effects leave any learnable interaction, and whether growing a series of these new computations approaches the full conditional table at a rate controlled by its representation cost. Distinguish this bounded conditional-table result from learning an unrestricted recurrent program.

**Data.** Keep the previous positive 50,257-token base, the top 12 output names and their complement, and the installed two-sign rule from the preceding experiment. Fit on 131,072 words at training-file offset 35,000,000 and select on the following 32,768. Evaluate on three previously unscored 32,768-word windows at training-file offsets 37,000,000, 39,000,000 and 41,000,000. The four encompassing prefix SHA256 values in that order are ed3db66445a7ca1475fa6c46c0ceec2e292fc05e66eed2df4b19b7b8a44f7f72, 162bfcc0c18dc9fdfd9a84f34c17b3f3b8399d4f3ccf2b2e4189d9c540e4c8e7, ee4f1d70b8239101d6a25609abdc47517ec3bf34d34323028f51ace55e804a8f and 327643717c2768cc872145219e731316625ad8de4393e7a2ad6a3f83da3e2306. Use the top 16 or 64 earlier input names plus the complement at lags 2, 4 or 8. The learned bit is computed before every target for the original frozen predictor and can be read again by the new operation.

**Construction and controls.** Starting at the same frozen model, compare growth restricted to ordinary additive sign corrections depending on $a$ or $i$, growth restricted to the products $a\,w_i s_j$, and growth choosing between these frontiers by the greatest residual score. Fit amplitudes by exact normalized log loss and deploy their 1/4096-grid values. Look at 1, 2, 4 and 8 growth steps. Compare to jointly fitted and regularized additive class logits on $a$ and $i$, independent saturated logits on $(a,i)$, the same joint additive fit followed by a learned product, and keeping the predictor as it is. Attributing a gain to composition requires comparisons with the additive alternative and whether the installed computation varies with both inputs. Report gross and bit-priced validation choices, eight reporting blocks per window, installed table sizes, acquisition work and actual full-word normalization. Charge shared learned tables once, including the earlier model when reporting total installation. Explicitly name its resident word ranks and the alternative cost of packing its raw names.

## Frozen registrations

- [Creating both sides of a normalized word correction from ordinary residuals](https://github.com/alan-ai1196/FP/blob/5be147a/research/frontier/NEXT.md)

- [Learning shared values on overlapping ordinary word histories](https://github.com/alan-ai1196/FP/blob/6cd3363/research/frontier/NEXT.md)

- [Inference of an arbitrary table from transitions hidden during fitting](https://github.com/alan-ai1196/FP/blob/6b2b606/research/frontier/NEXT.md)

- [Learning and installing a shared rule from linked raw tasks](https://github.com/alan-ai1196/FP/blob/9e7d752/research/frontier/NEXT.md)

- [Ordinary prediction loss and acquisition near a delay threshold](https://github.com/alan-ai1196/FP/blob/da74cc3/research/frontier/NEXT.md)

- [Minimum-width finite-memory mixtures and their sharp amplitude](https://github.com/alan-ai1196/FP/blob/769f929/research/frontier/NEXT.md)

- [State distinctions in autonomous next-token prediction](https://github.com/alan-ai1196/FP/blob/a92bc31/research/frontier/NEXT.md)

- [Training and deploying a nearly pooled stochastic update](https://github.com/alan-ai1196/FP/blob/8e162c2/research/frontier/NEXT.md)

- [Learning a four-state update across uninformative smaller widths](https://github.com/alan-ai1196/FP/blob/e164129/research/frontier/NEXT.md)

- [Ordinary outcome correlations and a lower bound on stochastic states](https://github.com/alan-ai1196/FP/blob/9700cc6/research/frontier/NEXT.md)

- [Distinguishing a sampled state from a reported state probability](https://github.com/alan-ai1196/FP/blob/9ba8046/research/frontier/NEXT.md)

- [Refitting chronological history rules on a stronger static predictor](https://github.com/alan-ai1196/FP/blob/6c623ca/research/frontier/NEXT.md)

- [Learning rolling history rules on chronological full-vocabulary text](https://github.com/alan-ai1196/FP/blob/52c2310/research/frontier/NEXT.md)

- [Learning the dictionary and the prediction operation together](https://github.com/alan-ai1196/FP/blob/f12abe0/research/frontier/NEXT.md)

- [Learning a shared meaning behind independent task orientations](https://github.com/alan-ai1196/FP/blob/5bbf626/research/frontier/NEXT.md)

- [Compressing a single observation into a predictive bit](https://github.com/alan-ai1196/FP/blob/59b8251/research/frontier/NEXT.md)

- [The price of learning and storing an unknown word dictionary](https://github.com/alan-ai1196/FP/blob/0566b90/research/frontier/NEXT.md)

- [Choosing which pooled state to split from ordinary word likelihood](https://github.com/alan-ai1196/FP/blob/4cfe00c/research/frontier/NEXT.md)

- [Learning a word-dependent lifetime alongside a trigram](https://github.com/alan-ai1196/FP/blob/319888a/research/frontier/NEXT.md)

- [Observable phase distinctions under persistent and destructive reads](https://github.com/alan-ai1196/FP/blob/53c10ef/research/frontier/NEXT.md)

- [Storing uncertainty with private randomized weights](https://github.com/alan-ai1196/FP/blob/beccdb0/research/frontier/NEXT.md)

- [Forecasting after discarding a state hypothesis](https://github.com/alan-ai1196/FP/blob/45217a9/research/frontier/NEXT.md)

- [Creation of a state without a supplied state count](https://github.com/alan-ai1196/FP/blob/f9a6c19/research/frontier/NEXT.md)

- [Pricing passive and active access to a hidden clock phase](https://github.com/alan-ai1196/FP/blob/3f8e6cb/research/frontier/NEXT.md)

- [Passive learning of a raw update from ordinary triples](https://github.com/alan-ai1196/FP/blob/1f9a9cf/research/frontier/NEXT.md)

- [Learning raw-word-specific updates against learned partitions and a posterior](https://github.com/alan-ai1196/FP/blob/a4c1f9f/research/frontier/NEXT.md)

- [Learning an unrestricted finite update on chronological text](https://github.com/alan-ai1196/FP/blob/27b9ef9/research/frontier/NEXT.md)

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
