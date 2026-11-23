# Next mathematical attack

Can ordinary target prediction discover which early names have the same response to future interventions, when both the operation and its number of input classes are unknown? The previous XOR model had to learn its memberships and noise rate, but received the form of the operation. An unrestricted raw table had poorer generalization to unseen pairs. We can now remove that assumption and measure exactly which parts of a missing response table are identifiable. [Controlled acquisition result](EVIDENCE.md#learning-to-buy-an-observation-from-later-target-errors)

## Registered learning of response classes

Use the preceding two-name, delayed-task sensor experiment, prices $1/8,9/32$, three training budgets 384, 3,072 and 24,576, uniform logging and the same 16-pair withholding rule. Use new seeds 3011, 4001, 5003 and 6007. For each seed randomly permute the eight row and eight column words independently using PCG64 keyed by seed and purpose. Use a common sequence of names, tasks, logging decisions, targets and noise draws across the three laws within a seed. Only the chosen signal and final target enter training. Let $u_i,v_i$ denote latent word bits, with indices modulo three. Use three laws for the matching sensor:

- XOR at coordinate $j$ selects $u_j\oplus v_j$.
- A column-dependent switch selects $(u_j\mathbin{\mathrm{AND}}v_{j+1})\oplus v_j$. Half of the columns ignore the row.
- A column-dependent address chooses $u_j$ when $v_{j+2}=0$ and $u_{j+1}$ otherwise, then flips by $v_j$. A fixed task has four distinct complete row-response profiles.

A common learner sees opaque IDs and episode histories. Per task enumerate all partitions of the eight row names into at most four nonempty blocks. For each block, column, queried sensor and emitted bit, fit an independent Bernoulli law for the eventual target bit with Jeffreys prior. Select one partition by integrated conditional target likelihood, with uniform prior over block counts and uniform prior over partitions at each count. Equivalently subtract the log number of partitions at that count from its evidence. Use posterior means for prediction, including $1/2$ in empty cells. Break exact score ties in lexicographic order of first-occurrence-normalized block labels. A second learner with identical search and priors is supplied symmetric sensor channels and fits agreement with the emitted token per block, column and sensor. This comparison measures the cost of inferring separate responses to zero and one. Both learners see the IDs of all pairs, but only the permitted observations train their probabilities.

Include the original taskwise XOR/noise learner, the original independently smoothed raw-pair rates, a pass-only control and a diagnostic given the true per-task row partition with emissions still fitted from observations. Use a fixed terminal policy that copies a purchased bit. For the separate emitted-token forecaster, average its two match probabilities at equal bit exposure for purchase decisions and retain its two conditional probabilities for log loss. Report target loss under uniform forced sensors as the primary predictive metric, alongside payoff under the learned purchase policy at both prices. Evaluate all 64 pairs and the withheld 16 separately. Report the selected class counts, exact equivalence with the true row partition, noise calibration or forecasting loss, purchases and learning work. Compile each fitted channel to direct raw-pair policies and to the previously defined one-bit final controllers; compare physical state and installed forecast bytes when a calibration depends on the received bit. The supplied-partition diagnostic is excluded from claims about learning. Any advantage of the unsupplied operation must be compared against the conventional model that is correctly specified on the XOR law.

Derive a necessary and sufficient population condition for every withheld prediction to be determined by observed cells across the allowed response partitions. On a finite noisy log, distinguish lack of statistical evidence from a genuinely unidentified missing cell. If the flexible model fails even with complete evidence on observable cells, report an alternative indistinguishable completion. Ordinary language remains the decisive prediction test. Transferring this procedure to shared next-token distributions on real contexts will require a separate chronological split and accounting for the output alphabet.

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
