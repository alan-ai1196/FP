# Next mathematical attack

Can ordinary causal prediction identify when two raw tokens should execute the same action? The real-text experiment picked a recoding of the original lagged distinction. Changing which raw tokens can share an action addresses a separate constraint of that experiment. [Text result](EVIDENCE.md#selecting-a-binary-memory-update-on-ordinary-text)

## Registered test of learning an internal alphabet

Use a source with six public token IDs, one hidden bit initially fair, and independent stationary windows of three tokens. From either state, IDs 1 and 4 each have probability 1/8 and preserve the bit. IDs 2 and 5 each have probability 1/8 and flip it. ID 0 has probability 3/8 in state zero and 1/8 in state one. ID 3 takes the remaining probability. Both 0 and 3 preserve state. Training sees only the six raw token identities and episode boundaries. Fit on 262,144 independent three-token windows with NumPy PCG64 seed 2026112301. Report on 65,536 independently restarted windows with seed 2026112302. No source probabilities, hidden states, masks or proposed merges enter the learner.

Fit all 203 set partitions of the six token IDs. Given a partition with $k$ cells, fit an unrestricted empirical distribution on length-$T$ coarse words and one history-independent distribution on the raw tokens inside each cell. Choose by minimum training joint negative log likelihood plus $\tfrac12(k^T-1+6-k)\log n$, where $n$ counts independent windows; resolve a tie by lexicographic restricted-growth encoding. Use two different acquisition views, the first two tokens of each window and all three. After choosing each partition, refit both on the same three-token training windows and add one half-count to each coarse word and each token inside its cell. Scoring must be causal at each of the three positions by prefix marginalization. Compare both learned partitions, the uncompressed raw triple, a fitted model given the four true cells, and the source probabilities as an oracle. Report scores per token, deployable count storage, search work, deterministic arithmetic checks and actual CPU cost.

The full-length learner must recover exactly the four true cells and beat the two-token learner on held-out full-token NLL to support the registered claim. Report the comparison against the unrestricted raw triple even if it loses. Before interpreting the result, account for why arbitrarily long past-only and future-only population tests can both miss the stay/flip distinction, and whether the finite evidence needed to decide exact merging grows with predictive rank. This test concerns a memoryless refinement of a coarse sequence law. The natural-text decoder also conditions within-group probabilities on a raw token.

## Completed registrations

- [Learning a synchronizing bit](https://github.com/alan-ai1196/FP/blob/f8bae86/research/frontier/NEXT.md)
- [Learning the four-bit synopsis](https://github.com/alan-ai1196/FP/blob/1e6c46d/research/frontier/NEXT.md)
- [Generalizing a task operation to 92 unused names](https://github.com/alan-ai1196/FP/blob/1f7b25f/research/frontier/NEXT.md)
- [Identifying an unknown response operation](https://github.com/alan-ai1196/FP/blob/9f5fc05/research/frontier/NEXT.md)
- [Selecting a binary update on full-vocabulary text](https://github.com/alan-ai1196/FP/blob/00cd1ce/research/frontier/NEXT.md)

The cloud session owns discovery, the primary-source index and the full-reading queue under the current [division of work](../../literature/COORDINATION.md).
