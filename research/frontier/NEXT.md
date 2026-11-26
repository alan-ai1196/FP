# Next mathematical attack

## Can ordinary predictions acquire a shared meaning that each new task initially conceals?

A balanced dictionary $s$ on $D$ raw names is shared across tasks. Each task receives a fresh unobserved fair sign $A$. Within that task the probability of an ordinary ordered pair is $D^{-2}(1+\kappa A s_xs_y)$. Different pairs are independent given $A,s$. Training from one pair per task has no dependence on $s$. With two pairs from the same task the four raw tokens jointly have law $D^{-4}(1+\kappa^2s_i s_j s_k s_l)$. Predict the fourth token on a fresh task after seeing its first three. Task grouping is an explicitly supplied observation protocol. No dictionary labels or task sign is released. The final question is the value of keeping information about $s$ across tasks, in addition to adapting to the current task within its four observations.

Derive when access to two within-task observations creates learnable cross-task meaning. Price the number of independent tasks needed for a useful held-out forecast, the information that $b$ stored bits can convey about the shared words, and the transient state used on a fresh task. In particular examine tuples with repeated raw names. Compare tests that recognize ordinary repetitions, fully fitted shared partitions, and a direct table of raw histories. Distinguish an information-theoretic search over balanced assignments from a procedure with affordable fit work.

**Registered numerical comparison.** At $D=6,12$ and $\kappa=1/2$, fit on $D,16D,64D,256D$ independent four-token tasks, with 128 independent fits per size and sample count and NumPy seed 20261126. Score fresh fourth-word loss by exact averaging over the fourth-token law. Compare uniform, the balanced prior before training, the maximum-likelihood shared partition, a posterior mixture over all candidate partitions, and a literal three-token context table with one pseudo-observation of the uniform distribution per possible output. Control the shared-partition fit by pairing the second half of each training task with the first half of the next task cyclically, using the actual grouping for scoring. Report held-out nats and fit/storage costs. Check all raw words at $D=4,6$ for the zero- versus two-observation marginal, the transfer law and the effect of retaining fixed relative labels. This is transfer to a new sign in a supplied task family. Open-ended task transfer remains a separate question.

## Frozen registrations

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
