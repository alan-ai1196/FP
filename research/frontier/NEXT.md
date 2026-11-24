# Next mathematical attack

A freshly written stochastic bit can encode a strict ordering of arbitrarily many cues through different writing probabilities. If the cue is read one symbol at a time, a single shared update must produce those probabilities. The unary example gives an exact minimum state count and shows how a two-state transient can pass every finite pointwise test while its worst gain tends to zero. [State criterion and streaming proof](FOUNDATION.md#how-many-memory-states-can-improve-prediction-in-every-training-environment) · [Ordinary-data acquisition](EVIDENCE.md#learning-one-private-bit-that-helps-every-source)

## Learning a transition from noisy sequences

What exposure permits ordinary prediction to identify a transition that keeps its benefit on later lengths? The previous clock proof gives the learner a modulus when establishing attainability. A learner that sees only short, noisy sequences faces uncertainty over both the recurrence and whether long-run structure exists. Derive a separation or an indistinguishability bound with the input lengths, file boundaries, reset information and random bits priced. Compare learning the state transition with fitting a finite table of exposed lengths, a data-fitted period estimator and a transient Markov filter. Charge any externally supplied length counter. A controlled example should reveal whether a compact acquired update continues to work on lengths far outside calibration.

The text experiment leaves a parallel empirical question. The period/newline state helped both new files, and the newly chosen period-to-“at” readout reduced total savings on each. Determine what a learner can certify across independent observed sources before paying to reuse a directed connection. Projected residuals can disagree across sources and even pooled ordinary data can lose this information. Candidate accesses still need to be predictable and charged. [Complete calibration and deletion control](EVIDENCE.md#can-prediction-errors-choose-a-directed-connection-from-samples)

## Frozen registrations

### Learning a reversible update from short observations, 2026-11-25

First test a single repeated raw action. Each independent episode starts at a uniform hidden position, produces a signed binary report, follows an observed number of advances and produces an independently noisy final report. Lag zero purchases two independent reports of the same position. The simulator uses cycles of lengths 3, 4, 5 and 7, one positive sign per cycle, all other signs negative, and report amplitude $3/4$. Only the simulated source receives these choices. The learner receives counts of the four observable report pairs at lags 0 through 20, a capacity ceiling of 20 uniform positions and the amplitude interval $[1/2,7/8]$. Fit from 4,096, 65,536, 1,048,576 and 16,777,216 independent episodes per lag, seeds 173, 419 and 773 (NumPy seed [seed, budget, lag, 2511]). These are stratified ordinary episodes. Simulating their multinomial counts charges every effective report and advance. Use simultaneous 95% Hoeffding intervals across all 12 fits and all pair-product means, calibrating the unknown scale with lag zero. Retain every possible common denominator up to 20 whose normalized correlation grid intersects all intervals. Compile a recurrence only if the necessary moments are uniquely identified and its exact finite-Gram checks pass. Compare an unobserved-length fallback, an empirical period table with parameter rent, the best grid-fitted two-state correlation, and a nonnegative cosine-mixture fit over all frequencies of orders up to 20. Report uniform mean conditional log-loss excess over lengths 21–440 and 100,001–100,420, checked against the source. Charge the installation, causal carry, arithmetic and all training accesses. Record abstentions.

Next test all-report forecasting with three opaque involutive actions on eight uniform hidden states. The simulator uses a transposition of positions 0 and 1 and the two reflections $i\mapsto-i$ and $i\mapsto1-i$ modulo 8. Its positive set is $\{0,1,3\}$, and an independent later task has positive set $\{0,2,5,7\}$. Permute state names and primitive names with seed 25112026. The learner sees signs and chooses raw action strings, with known self-inverse spelling, a capacity ceiling of 10, and a lower amplitude bound $1/2$. Distinct observations are independently noisy conditional on the hidden path and the actual amplitude is $3/4$. Starting with the empty suffix, collect signatures and successor signatures by traversing test words and returning along their reverses. Repeated ordinary reads at a position are allowed and paid. At each inconsistent signature add the first shortest lexicographic successor test revealing a conflict. Take 100 fresh uniform resets per refinement round and 225 independent reports per queried sign. Freeze the first closed quotient. Estimate readout noise and a new terminal report from 1,024 further reset episodes, using ordinary calibration signs and decoded state identities. Use seeds 173, 419 and 773 for independent fits. Score fresh observation histories with an exact Bayesian oracle, the acquired table, one-state marginal, the readout based solely on the first report, and an equally informed conventional state-partition/filter implementation. Include labeled lengths 16, 128 and 1,024, independently sampled equiprobable raw actions, 128 episodes per length/seed, and a final query for the new task. Measure logical action and observation work, packet and carry costs. Complete-law identification and transfer stay conditional on the reset and return interface.

Check the limits independently. Use exact small-law probes for indistinguishable short prefixes, pairs with equal all-lag correlations and different triples, and parity under an observation budget with and without repeated reads. Prove which conclusions survive partial coverage, missing returns or privately varying initial phase.

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
