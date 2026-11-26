# Next mathematical attack

## Can predictive residuals jointly create a useful input value and its output transformation?

Given a frozen positive next-word distribution, first calibrate its pooled output-class frequencies on training. For a lagged raw input name $i$ and next-word class $j$, accumulate residual $R_{ij}=\sum_{t:i_t=i}(1_{\{Y_t\in j\}}-q_t(j))$. Search over signs of all output classes and assign each input name the sign of its row projection. This exactly maximizes $z^\top R s$ for paired binary values. Fit a normalized likelihood tilt using the resulting two new tables. Also allow a shared real output direction and refit the input signs from ordinary likelihood. The null model has one pooled input value and a static calibration. Record whether both learned tables matter, how much predictive work the one-bit input value does across different realized words, and how much stronger direct conventional controls can do.

**Data and selection.** Retain the previous full-vocabulary base and its original name ranks. Train on 131,072 ordinary words at training-file offset 27,000,000. Select on the next 32,768. Use 32,768-word reporting windows at training-file offsets 29,000,000 and 33,000,000 and development-file offset 1,967,232. The development corpus has prior project exposure. Prefix SHA256 values in that order are 634b826b79cb9871a12788986b0520d1ab3247c016b5e8829aad439085eeb669, 91a4746a21de328d782a355e94b6541a3ec4d25b1ecff3dfb02a58b792861b12, d42c3ec72a745a3e72374368c58b5da1de585269507efaf61616172228a9f64e and fe2ce7174972d67b4be62a189f600491dae40cc90e7a0226f1178c8e122b2cb3. Partition outputs into the 8 or 12 most frequent individual names plus the complement. Partition inputs into the 64 or 256 most frequent individual names plus the complement. Search lags 1, 2, 4 and 8. These finite boundaries and the fact that a lagged name is available are supplied. All memberships within the two learned signed directions and their tilts must come from ordinary words.

**Comparators and costs.** Include the unmodified base, pooled multiclass calibration, a preassigned frequent-versus-other output sign with fitted input signs, the jointly learned signs, and their real-output refinement. Include a direct regularized multiclass correction per input name on the same lags, word classes and base. Use a common 14-bit fixed-point format with spacing 1/4096 for installed logits. Select per family on validation at zero price and at one $\ln2$ per installed bit for one reporting-length deployment. Report both independently transmitted 16-bit name IDs and the incremental payload when the selected ranks can be reconstructed from retained base counts. Record candidate/search size, table storage, execution work, full-vocabulary normalization, paired block gains and gross gain over pooled calibration. A higher training likelihood alone does not establish learning on either reporting source.

## Frozen registrations

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
