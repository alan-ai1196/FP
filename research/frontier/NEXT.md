# Next mathematical attack

Two observation interfaces for the same latent state can require very different amounts of calibration. The complete-positive constraints identify which deployment laws are possible in the population. A small support promise can identify a nonlinear assignment which projecting through the old view misses. [Identification and weak-channel calibration](FOUNDATION.md#what-ordinary-paired-observations-identify-across-an-unfamiliar-view) · [Matched-budget experiment](EVIDENCE.md#transferring-a-prediction-without-joint-labels)

## Can a learner acquire a new categorical mapping from ordinary counts?

Three kinds of observations are available on the same source, but the two needed at deployment never appear together in training. Test whether ordinary discrepancies suffice to learn an unfamiliar map using a finite latent capacity promise. Compare an explicit confidence certificate, ordinary conditional log-loss fitting, and the projected latent span. Price the new mapping, its uncertainty, the full chronological output and the complete search for a fitting rule. Determine which benefits survive when the hidden capacity has to be tested from experience. [Finite-data transfer mechanism](FOUNDATION.md#learning-a-categorical-assignment-from-disjoint-pairs)

## Frozen registrations

### Learning a categorical assignment from two crossed pair tables, 2026-11-25

Use three old $T$ labels, four new $D$ labels, three target $Y$ labels and a known ceiling of 12 hidden atoms. On a simulator-only state $(t,d)$, the hidden weights within each fixed $t$ are an independent permutation of $(1,2,4,8)/45$. Each row's rounded target is an independent permutation of $(0,0,1,2)$. Generate these with NumPy default RNG [seed, 3711], drawing the three weight permutations then the three target permutations, for seeds 173, 419 and 773. Each true label independently changes to a uniform different label with probability $1/4096$ per read. The learner receives only the alphabets, capacity, independent-view/twin/reset interface and ordinary counts. It receives no prior weights, noise rate, partition pattern or matching examples.

At $L=4096,65536,1048576,16777216$ draw independent multinomial raw joint tables in order $TT',DD',YY',TD,TY$ using RNG [seed, L, 3712]. Charge $5L$ fresh resets and $10L$ ordinary reports per learner. Allocate family error .05 across $M=12(12+9+3)=288$ cell and disagreement quantities. Use two-sided Hoeffding on crossed cells and exact one-sided Clopper–Pearson on disagreement counts. Enumerate all $3^4$ assignments per row. Certify the mapping only on complete positive coverage and a single compatible assignment per row under the empirical event test in the proof. On abstention fit the marginal target. Independently choose a conventional assignment minimizing ordinary $TY$ conditional log loss, using as predicted label counts the empirical $TD$ row pushed through each candidate, with half a count per output. Also score the symmetrized old-twin pseudoinverse projection with negative cells clipped, a fitted independent marginal and the population oracle. Normalize point-model joints to the empirical $D$ marginal; use a uniform conditional after a zero row. Give all fitted heads the same uniform joint smoothing with weight $\min(1/2,b_T+b_D+b_Y+6\eta)$, where $\eta$ is the crossed-cell radius. Compare true mean conditional KL per target and on fresh 4,096-pair test counts from RNG [seed, 3713].

Deploy ordinary alternating $D,Y$ as raw tokens numbered 0–3. Predict the $D$ marginal before each fresh pair and a mapped conditional before $Y$. Assign each of four tokens one Q16 unit, then allocate the remaining units by largest remainders with index tie-breaks. Record row certification, recovered mappings, search size, log losses, the finite-sample KL bound when applicable, install bytes, live state and all-event agreement with historical R4. Preserve a capacity-plus-one source giving exactly the same training panels and an incompatible deployment law.

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
