# Next mathematical attack

A fixed number of stationary binary sampling contexts can teach at most a logarithmically growing amount about individually reusable labels. Geometric hidden sampling attains the order under a fair product prior, including the case where name ranks must be learned. Aggregate counts can still conceal opposite answers on every input. [Theory](FOUNDATION.md#how-much-a-finite-number-of-sampling-contexts-can-teach) · [Ordinary acquisition and costs](EVIDENCE.md#how-many-named-labels-can-aggregate-ordinary-reports-teach)

## Can disjoint aggregate observations teach an ordinary text prediction?

In text the same word may have different meanings in different histories. A fitted table $P(Y\mid D)$ for current context $D$ should therefore be tested on actual future words. Compare an old tag $T$ randomly generated from $D$ against a natural earlier word. Only two separate training tables $(T,D)$ and $(T,Y)$ reach the weakly supervised learner. Determine how much direct bigram predictive gain survives, whether aggregate fitting can amplify small sampling or structural errors, and how much predictive performance a finite shared categorical packet retains. Learning from label proportions has an established literature; here target probabilities are estimated from separate chronological samples and scored under the ordinary raw-token clock. [Quadrianto et al.](https://jmlr.csail.mit.edu/papers/v10/quadrianto09a.html) · [Scott and Zhang](https://proceedings.neurips.cc/paper/2020/hash/fcde14913c766cf307c75059e0e89af5-Abstract.html)

## Frozen registrations

### Learning an ordinary next-word table from two unpaired panels, 2026-11-25

Use the archived uint16 GPT-2 training and validation files and the 50,257-word vocabulary. Fix the 16 most frequent names in the first 1,048,576 training words, breaking ties by token ID, and map every other name to class 16. Fit a common half-count-smoothed unigram lexical law on that prefix. Target position $i$ has context $D=C(x_{i-1})$ and target class $Y=C(x_i)$. Four separate old tags are the natural $C(x_{i-2})$ or a random tag which copies $D$ with probability $0,1/8,1/2$ and otherwise chooses a uniform class. Generate random tags separately by channel and tape with NumPy [1217,5212,channel index 0–2 in listed order,file index 0/1/2 for fit/training report/validation report], consuming all uniform copy decisions then all random labels. No tag is supplied at deployment.

Use the 1,048,576 targets beginning at zero-based position 9,000,000 in the training file. Permute their indices with NumPy [1217,5211]. The first and second halves respectively supply the crossed $TD$ and $TY$ panels without preserving chronological pairing. Use nested budgets $L=8192,65536,524288$ from each half. Stronger directly paired controls get the true $DY$ table on exactly the $L$ target-bearing positions. Give the weak learner only its two integer tables. Give all models the historical class names and lexical-law packet. The reporting ranges are 65,536 untouched targets starting at 11,000,000 in the training file and 262,144 in validation. Through these endpoints the SHA-256 digests are 40f586a5016363714c2fc950f2202c5a67938625ff3d015f02638a6b1095a030 and c13f864650df4e782af578430da4e36b00d542db0a3ba0014ad5fde568386a1d. Freeze the installed class tables in Git before scoring the reporting targets.

Estimate each row of $W=P(D\mid T)$ from $TD$ with one pseudocount distributed as its half-count-smoothed $D$ marginal. Let $u$ be the half-count-smoothed $TY$ target marginal. Fit a row-stochastic $\Theta$ by minimizing the negative ordinary aggregate multinomial log likelihood of $W\Theta$ on $TY$, with the penalty $-64\sum_{dy}u_y\log\Theta_{dy}$. Start each row at $u$; use the multinomial EM allocation, check the simplex first-order upper bound on suboptimality per effective target and report it. Target $10^{-7}$ with up to 20,000 iterations; retain and identify any unconverged fit. The independently paired conditional uses the same 64 marginal pseudocounts per input. Also score the marginal and the original lexical unigram alone. Diagnostics include rank and singular values of $W$, held-out weighted TV of the closure discrepancy using actual test triples, and aggregate likelihood versus actual downstream word loss. Diagnostics cannot select or refit the packets.

Quantize each 17-class row by reserving one Q16 unit per class then allocating the remaining units by largest remainders and index tie breaks. For an ordinary word, release its class probability times its common lexical probability conditional on that class. Check full-vocabulary normalization, chronological update from the observed word and held-out next-token loss on both files. Compare matched information for the weak heads, the stronger paired training data, storage of the class packet and common lexical law, and all 289 class transitions in pinned R4 for the largest-budget half-copy and natural-tag packets. Report gains or deterioration in nats per token.

**Prospective mechanism-aware control.** Before fitting, add a comparator on the three randomized-tag channels. It knows the uniform-contamination mechanism and estimates its copy rate solely from the observed fraction of exact $TD$ matches. Subtract the estimated uniform contribution from the empirical $TY$ joint, divide by the fitted rate, clip negative cells and normalize each row. If the fitted rate is below the two-sided 95% Hoeffding radius for the copy-rate estimator, use the target marginal. Otherwise mix the inferred row with the same 64 marginal pseudocounts relative to the observed $TD$ input counts. Give this comparator the same integer output and lexical law. The fitting-only training prefix has SHA-256 be533658c8850f1a5a50f35981a369f5d5a69944e4726fe49e0b01141b078957.

**Chronological control added after the first fit and before reporting scores.** For the natural old tag, $TD=(C(x_{i-2}),C(x_{i-1}))$ is an ordinary bigram ending one position earlier. Over the complete contiguous fitting window its count table and the complete $DY$ count table differ by one entering and one leaving pair. Fit a head directly from the available natural $TD$ counts with the same 64 target-marginal pseudocounts per row. Freeze it with the original packets and compare it with both the aggregate projection and the directly paired target-bearing panel. The randomized-tag channels expose disjoint position panels and lack that shifted-bigram table. Sampling them without replacement from the same fixed tape is part of the experimental design.

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
