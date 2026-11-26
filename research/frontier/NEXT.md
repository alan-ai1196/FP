# Next mathematical attack

## Can ordinary full-vocabulary loss construct a reusable value for overlapping word histories?

Use each ordinary token's membership in a frequent-word group to form a binary sequence. Let $u,v$ be the two consecutive $M$-bit windows ending before the next token, and $x$ the newest observed sign. Fit an unknown Boolean history value $f$ by tilting a strong positive full-vocabulary base with logit $\beta x f(u)f(v)$ times the next word's group sign. Normalize over the entire vocabulary at every history. The weights of a finite signed graph should follow from the exact lexical objective. Build its table jointly from those weights, then test whether its shared values pay compared with a static calibration, a suffix rule and an independent edge table. Ordinary text has no imposed hidden task orientation.

**Data and price.** Reconstruct the previous validation-selected Kneser–Ney base (discount 0.9, lexical mixture 1/16, prior mass 65,536) from its original disjoint data. Fit new rules at training-file offset 24,000,000 for 262,144 words, then select on the following 65,536. Score frozen models on 65,536 words at training-file offset 26,000,000 and on the previously exposed development file at offset 1,900,000. The three encompassing raw-prefix SHA256 values in order are `a7bd7e3a8c50a24055580bd9d66c374859a43b66fe501414a108551954497c48`, `c79d8896d20098963ccf5e16d3e39932bd06b9598580518c9ae6eea7f90f3e7d` and `e08b01b3393c877e9c05ca42c56f9f5aa8b4c44e240c5ab71be000c0ed67f42d`. Vocabulary ranks come solely from the original 524,288-word base prefix. Use top 8, 32 or 128 words for the binary group. Fit a separate static group intercept from training for each choice. Include the original unmodified base.

**Prospective comparison.** Fit shared tables at $M=1,3,5,7$ and log tilts of both signs with magnitudes $1/64,1/32,1/16,1/8,1/4,1/2$, plus zero. Use signed adjacency, local likelihood refinements and multiple starts. Include an independent signed table on the same $(M+1)$-bit history and a same-sized single-window lookup, an adaptive suffix tree with ternary corrections, and a direct per-history continuous correction shrunk toward the static fit. Select each family on validation with and without one bit priced at $\ln2$ nats for a 65,536-word deployment. Charge the installed grid choices, group intercept, labels and topology or continuous parameter bits as applicable. Report NLL per raw word, eight successive block differences per file, normalization checks against full vocabulary sums, training work and deployed storage. Any advantage must survive comparison with the best validated static or context-dependent alternative on the same positions.

**Constructive extension specified before fitting.** Let the long-window value be the product of the same unknown function $g$ over every contiguous $\ell$-bit subword of that window. Products of neighboring long-window values cancel all interior factors. This leaves precisely $g$ of the outgoing subword times $g$ of the incoming subword. Fit these smaller shared tables at $\ell=1,2,3$ with $\ell<M$ and the same spans, raw tokens, signs, tilt grid and selection price. Compare with independently fitted signs for each pair of boundary subwords at matched access. Report whether a compact motif proposed from word likelihood survives validation and both frozen text files. The earlier unrestricted $M$-word shared-table test remains part of the comparison.

## Frozen registrations

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
