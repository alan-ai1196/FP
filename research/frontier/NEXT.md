# Next mathematical attack

When does a low-dimensional predictive state save resources once small errors are allowed? Results for two-state permutation sources identify the individual updates from ordinary triples and execute them for much longer histories. They assume the existence of a finite positive hidden-state model. [Registered result](EVIDENCE.md#training-on-three-tokens-and-forecasting-sixty-four)

Consider the rank-three probability clock from observable-operator theory. An irrational rotation can prevent any exact finite hidden Markov realization. Jaeger's original report gives the construction and a learning experiment. Investigate the best *expected causal log loss* of a physically limited positive model. A failure of exact realization alone gives no value for that loss. [Jaeger, Sections 6 and 9.1.3](https://publica-rest.fraunhofer.de/server/api/core/bitstreams/c5799916-b434-4186-94ab-717cb74db946/content)

Use a stationary, three-token variant with a constant advance probability and two reset outcomes. Give an explicit all-positive word law, a proof of its predictive rank and the exact-state obstruction, a finite-horizon witness against each fixed number of hidden states if justified, and an executable approximation bound. Calculate what short ordinary observations reveal about its parameters. Charge precision, state storage and the work to estimate the clock. Distinguish an exact real-valued representation from finite binary hardware.

## Completed registrations

- [Learning a synchronizing bit](https://github.com/alan-ai1196/FP/blob/f8bae86/research/frontier/NEXT.md)
- [Learning the four-bit synopsis](https://github.com/alan-ai1196/FP/blob/1e6c46d/research/frontier/NEXT.md)
- [Generalizing a task operation to 92 unused names](https://github.com/alan-ai1196/FP/blob/1f7b25f/research/frontier/NEXT.md)
- [Identifying an unknown response operation](https://github.com/alan-ai1196/FP/blob/9f5fc05/research/frontier/NEXT.md)
- [Selecting a binary update on full-vocabulary text](https://github.com/alan-ai1196/FP/blob/00cd1ce/research/frontier/NEXT.md)
- [Learning a shared internal alphabet](https://github.com/alan-ai1196/FP/blob/4c5aa39/research/frontier/NEXT.md)
- [Learning a continuing update from triples](https://github.com/alan-ai1196/FP/blob/63f6f8f/research/frontier/NEXT.md)

The cloud session owns discovery, the primary-source index and the full-reading queue under the current [division of work](../../literature/COORDINATION.md).

## Prospective probability-clock comparison

Use $P(a)=2/3$, $\kappa=1/2$, $\cos\theta=3/5$ and $\sin\theta=4/5$. Each observed reset starts the raw run $a^k$ followed by $b$ or $c$, with $P(b\mid\mathrm{reset},k)=(1+\kappa\cos(k\theta))/2$ at its terminal mark. The learner knows which token advances and which two reset. It sees raw runs and ordinary outcomes, with no true rotation angle, age-dependent probabilities or preferred period. Train on 65,536 complete independent runs with NumPy PCG64 seed 2026112305 and score 65,536 further runs at seed 2026112306. Include every advance and mark in the full three-way NLL. A run ends at an observed mark; the first run begins immediately after a reset.

At budgets $K=1,2,4,8,16,32$, fit all ways a deterministic $K$-state update with a single shared reset can arrange its transient and cycle. Use empirical raw-token likelihood to choose among layouts with exactly $K$ potentially reachable states, preferring the shorter cycle on a tie. Every model fits a common advance rate and its own within-state mark probabilities, using one half-count per outcome for deployment. Compare the selected layout, the same-budget saturated age counter, a fitted rotation using the empirical mark probabilities at ages zero and one, and the known-source oracle. Clip the fitted rotation amplitude to $[-1+1/n,1-1/n]$ and fitted cosine to $[-1,1]$. Singles and adjacent ages determine these parameters only in the declared cosine family. Report held-out NLL, exact or certified population losses, fitted state counts and precision. The decisive quantitative questions are which layouts win, whether a learned cycle beats a saturated counter in the same budget, and how strongly unrestricted positive models are excluded. Keep exact realization, attainable expected loss and observed learning distinct.
