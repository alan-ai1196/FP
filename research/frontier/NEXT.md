# Next mathematical attack

## Can a learned rule on the last three words improve full-vocabulary chronological prediction?

Fix the earlier smoothed raw trigram $B_h$ and pooled lexical distribution $q$ on 50,257 word IDs. The pooled forecast is $0.75 B_h(y)+0.25q(y)$. Name the eleven most frequent IDs in the 524,288-token background and assign all others to a twelfth group. Fit a balanced binary partition $s$ of those twelve groups by ordinary word loss. On input history $z$ consisting of the last three group signs, tilt only the lexical component to $q(y)(1+u_zs_y)/(1+u_z\sum_v q(v)s_v)$. This is a normalized full-vocabulary forecast at every position. The binary history, choice of groups and placement of the lexical component are supplied. The partition, rule and useful strength are fitted. Evaluate rolling histories across token positions.

**Frozen protocol.** Use the earlier 524,288-token background, 262,144-token fit and 65,536-token validation beginning at training-file index 9,000,000 in that order. Fit the pooled row by the earlier twelve EM updates at lexical weight $1/4$. Try all 462 sign partitions. For $u_z=\lambda f(z)$ fit each of four rule classes: an arbitrary eight-entry Boolean table, any function of the last two signs, a constant or function of the last sign (the rolling two-state class), and the fixed three-sign product. For each $\lambda=1/4,1/2,3/4$ keep the exact highest training-likelihood partition and rule and select strength on chronological validation, allowing zero. Also fit a comparator choosing each of the eight $u_z$ independently from $0,\pm1/4,\pm1/2,\pm3/4$ and a free-table control with the three-word histories shifted cyclically by 131,073 training positions; keep its target, lexical responsibility and reporting histories aligned to their actual positions. The independent-row model may select a global attenuation of 0, 1/2 or 1 on validation.

Compare with the frozen trigram and pooled forecast, and with eight full-vocabulary lexical rows using the learned free-table partition for the three history signs. Fit those rows by twelve ordinary mixture EM updates with 64, 1,024, or 8,192 pseudocounts toward $q$ per row. Allow pooled as a validation choice. Report total nats, nats per token, all eight consecutive block means per source, vocabulary storage and fit work. Give the actual minimal rolling machine width of the installed Boolean table. Compare whether dropping the oldest history sign sacrifices held-out prediction to a separately trained two-history model. A zero validation strength is an admissible negative result.

Score 65,536 tokens starting at 17,000,000 in the training source and 1,179,648 in the reporting source. Their prefix SHA-256 values through the ends of these windows are respectively ee1c4fd74f5371a27fa1124786ce776fd47b4149d69047b8e4101002e9149996 and 4bcc4bf13fd15b26306ed792385d1b9c8f7209c4673ffede81c70d0c8a9d45ab. These windows are distinct from the lexical switching and curvature reports. No scores from either window informed this registration. Inspect complete conditional normalization and compare optimized likelihood sums with an independent raw-token evaluation.

## Frozen registrations

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
