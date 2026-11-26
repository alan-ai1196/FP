# Next mathematical attack

## Can the ordinary likelihood choose which lexical distinction to create?

At a pooled lexical fit put $B_t(y)=(1-\lambda)b_t(y)+\lambda f(y)$. Split the learned row into $f(y)(1\pm\epsilon w_{g(y)})$, with bin masses $F_j=\sum_{g(y)=j}f(y)$ and $\sum_jF_jw_j=0$. The learner receives the same canonical word names and training tape as the pooled fit. Its direction $w$ must be chosen from the empirical log likelihood. No state path, word classes defined by semantics, or future tokens are supplied at prediction time. The top 256 frequency bins and shared tail are a capacity restriction.

**Mathematical attack.** For a known symmetric hold coefficient $a_y$ after word $y$, let $x_t=\lambda f(y_t)e_{g(y_t)}/B_t(y_t)$, where $e_j$ is a coordinate vector. Establish when the constrained quadratic $\sum_{s<t}(x_s^\top w)(x_t^\top w)\prod_{j=s}^{t-1}a_{y_j}$ detects the formation of a predictive distinction. Attack its zero-curvature case and determine the statistical price of detecting a weak split in an ordinary binary stream. Compare a known pooled law with an unknown fitted pooled law, a single subject with independent starts, and positive with negative persistence. Price the observations and the memory of a concrete acquisition procedure.

**Registered chronological test.** Fit the same pooled background and lexical row on the same windows as the preceding study, with $\lambda=1/4$ fixed. For each common hold $a\in\{1/2,7/8,31/32,127/128\}$, compute the direction maximizing the training quadratic at $\sum F_jw_j^2=1,\ \sum F_jw_j=0$. Normalize its largest absolute entry to one. Compute a control direction under each hold after jointly permuting the training bins and observed lexical responsibilities with one NumPy default RNG permutation, seed 20261126, common to all four holds. Use chronological validation and reports for all fitted directions. Record largest and smallest constrained eigenvalues and the direct streaming quadratic for the selected direction.

For each direction score strengths $\epsilon\in\{0,1/8,1/4,1/2,1\}$. Compare the exact two-state filter with a conventional clipped linear accumulation of the same observed errors. For $d_t=x_t^\top w$ the latter issues $B_t(y)(1+\epsilon m_t d_t(y))$ and then updates $m_{t+1}=\operatorname{clip}_{[-1,1]}[a(m_t+\epsilon d_t)]$. Both start at zero. Select hold and strength on the 65,536 validation targets separately for each training order and each update rule, ties in the displayed parameter order. Freeze all four selected models and score the two previously used 65,536-token report windows and all eight blocks per window. Include the pooled head, the stronger static average of the previous EM heads, and the earlier bigram and trigram baseline scores. Report stored coefficients, temporary matrix size and training work. An empirical positive training eigenvalue is only evidence of a local improvement on that particular tape.

## Frozen registrations

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
