# Next mathematical attack

Can an ordinary full-vocabulary text stream teach a reusable binary update that improves on both copying the last distinction and retaining a raw token pair? The controlled experiment identified a previously unknown response operation, but its particular informative input conditions could be chosen. Uniform passive observations can make acquiring the same dictionary exponentially more expensive. This test uses the already registered FineWeb-Edu training tape, with its natural order and no calibration prompts. [Synthetic evidence](EVIDENCE.md#learning-the-response-operation-from-opaque-task-names) · [Passive observation bounds](FOUNDATION.md#the-cost-of-waiting-for-informative-inputs)

## Registered full-vocabulary text test

Use only the pinned little-endian GPT-2 training file from the original reconstruction. Train the existing 50,257-way smoothed successor model and derive its frequency group from tokens $[0,786432)$. Fit the shared calibrated next-group probability and conditional readout rates on targets $[786432,917504)$. Select purchasable context rows on $[917504,1048576)$ with the existing price of $(\log2)/256$ nats per retained bit. Choose a shared operation on $[1048576,1179648)$, the previously reported historical training-file continuation. Freeze all fits and score targets $[1179648,1310720)$ once. Preserve state continuously from token zero. These are zero-based, half-open **target indices**. Validation and confirmation files are outside the experiment.

Let $F(x)$ be the published training-frequency membership of token $x$. For target $y_t$, the decoder receives the current token $x=y_{t-1}$ and one live bit $z$ updated through $y_{t-2}$. After selecting the forecast it advances the bit by $z\leftarrow g(z,F(x))$ for the next forecast. Initialize $z=0$. Consider all 16 binary truth tables for $g$, with bit $2z+F(x)$ of the integer specifying the new state. Fit next-group rates using the historical 4,096-point grid, 64 observations of shrinkage toward the shared calibrated baseline, and the existing near-exact log-price test. A current-token row can be bought when both states occurred in both its rate-fitting and row-selection blocks. A bought row costs 16 bits for its token ID and two 12-bit rates. Every nonempty model additionally costs four truth-table bits and one live bit. Choose the model minimizing operation-selection block NLL plus this payload price, including the shared calibrated baseline with zero extra payload. Prefer the baseline at a tie, otherwise the smallest integer gate. A model with no bought rows is the baseline.

Keep full normalized token probabilities by replacing only the mass of the specified output group, preserving the successor model's within-group distribution. Compare the selected model with the shared calibrated baseline, the original smoothed successor, the standalone lagged frequency bit (operation 10 gives the second argument), the previously implemented raw-token-pair trigram with the selected operation's payload limit, and the best remaining gate on the scoring data as a labeled hindsight diagnostic. Report the 16 selection scores, the frozen operational choices, compressed payload, full-vocabulary held-out NLL and exact row/readout agreement on short synthetic histories. A positive result requires lower *priced* held-out loss than both the lagged-bit and the raw-token-pair competitor. The benchmark charges fitting passes and CPU memory and makes no hardware-throughput claim. Test data cannot choose a replacement for a losing gate.

## Completed registrations

The earlier questions, criteria and seeds remain available at their frozen revisions.

- [Learning a synchronizing bit](https://github.com/alan-ai1196/FP/blob/f8bae86/research/frontier/NEXT.md)
- [Learning the four-bit synopsis](https://github.com/alan-ai1196/FP/blob/1e6c46d/research/frontier/NEXT.md)
- [Generalizing a task operation to 92 unused names](https://github.com/alan-ai1196/FP/blob/1f7b25f/research/frontier/NEXT.md)
- [Identifying an unknown response operation](https://github.com/alan-ai1196/FP/blob/9f5fc05/research/frontier/NEXT.md)

The cloud session owns discovery, the primary-source index and the full-reading queue under the current [division of work](../../literature/COORDINATION.md).
