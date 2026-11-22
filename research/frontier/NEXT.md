# Next mathematical attack

Does learning which token identities share an action also identify a causal update that can run for arbitrarily long histories? Finite windows recovered the true four-cell partition of the six-token source. The fitted table itself has only three positions. [Finite-window result](EVIDENCE.md#learning-which-token-identities-can-share-an-action)

## Registered test of learning a continuing update without reset symbols

Use the same six-token stationary source specified in the [alphabet experiment](https://github.com/alan-ai1196/FP/blob/4c5aa39/research/frontier/NEXT.md). Start afresh with 262,144 independently initialized three-token training windows from NumPy PCG64 seed 2026112303. Use 4,096 independent 64-token episodes from seed 2026112304 for reporting, 262,144 scored tokens in total. Freeze all parameters before reporting. Every prediction sees only the past tokens of its own episode. This study supplies the candidate class of at most two hidden states with a deterministic permutation update for each token. It supplies neither the emission rates, hidden labels, token alias assignments nor the individual permutations.

From training word frequencies through length three, choose the one-letter prefix/suffix pair maximizing the absolute determinant of the two-by-two Hankel block built with the empty word. Use the associated shifted blocks to identify each candidate stay or flip by determinant sign. Seek an operator with two distinct real eigenvalues among the stays and pair products of flips, preferring the largest absolute eigenvalue gap. Form a candidate hidden-state basis from its two spectral projectors applied to the terminal vector. Project the resulting emissions and initial probabilities to strictly positive normalized distributions; disclose floor and fallback. Fit initial probabilities and the two emission rows further by 25 ordinary triple-likelihood EM steps with half-count smoothing, keeping the inferred actions fixed. Execute the frozen predictor both by a scalar signed log-odds update and by an independently normalized two-state probability vector. Check the alternative all-swapping case with exact population matrices separately.

Compare full six-way causal NLL against an unrestricted add-half order-two Markov predictor trained on the same triples, a fitted unigram, and the known-source predictor with the same observed history. Report all 64 positions or disjoint registered blocks (1–3, 4–16, 17–64), the inferred actions, acquisitions, model state, total CPU time and memory. Success requires recovering all six actions and improving on the raw order-two predictor over all 64 positions as well as over positions 17–64. Preserve these criteria if results fail. A positive result concerns this source and candidate family. The original FineWeb-Edu corpus and its Transformer baseline are outside this synthetic test.

## Completed registrations

- [Learning a synchronizing bit](https://github.com/alan-ai1196/FP/blob/f8bae86/research/frontier/NEXT.md)
- [Learning the four-bit synopsis](https://github.com/alan-ai1196/FP/blob/1e6c46d/research/frontier/NEXT.md)
- [Generalizing a task operation to 92 unused names](https://github.com/alan-ai1196/FP/blob/1f7b25f/research/frontier/NEXT.md)
- [Identifying an unknown response operation](https://github.com/alan-ai1196/FP/blob/9f5fc05/research/frontier/NEXT.md)
- [Selecting a binary update on full-vocabulary text](https://github.com/alan-ai1196/FP/blob/00cd1ce/research/frontier/NEXT.md)
- [Learning a shared internal alphabet](https://github.com/alan-ai1196/FP/blob/4c5aa39/research/frontier/NEXT.md)

The cloud session owns discovery, the primary-source index and the full-reading queue under the current [division of work](../../literature/COORDINATION.md).
