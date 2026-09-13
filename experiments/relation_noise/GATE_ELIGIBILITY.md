# The current empirical-upper gate under IID relation noise

Status: **scoped algorithm/data-law lemma, exact small-model audit**.
This concerns the existing frozen proposal/upper algorithm, not a new
Foundation law, a complete-class impossibility or a population guarantee
inferred from a PRNG tape. The [protocol](PROTOCOL.md) states the experiment.

Consider a connected tree with e=n-1 observed edges, one oriented context
per edge and exactly ten labels per context. Use the existing (1,8)
initializer, base (1,1), zero learning rate and no constructor profile.
The actual baseline is uniform. Suppose the native relation witness fits
the declared syntax/range caps. Ignore resource/numerical admission failures
only to compute **arithmetic eligibility**, a necessary condition for an
actual completed comparison.

The all-categorical empirical likelihood upper is attained only when every
observed context prediction equals its empirical frequency vector. This
follows from the strict equality condition of the categorical likelihood
maximum; zero-frequency boundary rows are unattainable by a positive base.

The baseline attains this upper exactly iff every edge has a 5:5 split.
Otherwise the proposal algorithm first refuses tied edge constraints.
Tree constraints are consistent for every assignment of untied edge signs.
The proposal's readout scale must occur in its initializer: it can be 1
or 8, giving common majority probabilities 2/3 or 9/10. A ten-label
frequency cannot equal 2/3. Therefore a proposed endpoint attains the upper
iff **every** edge has a 9:1 split, in either label order. Conversely those
splits give pooled scale8, a valid consistent tree assignment and the
feasible existing native witness, so they are eligible. Heterogeneous
counts with pooled scale8 can emit a useful candidate, but cannot attain
this upper. Other scales can suppress proposal construction altogether.

Under independent flips with probability 1/10, write

```
p9 = P(Binomial(10,1/10) in {1,9}) = 193710249/500000000
p5 = P(Binomial(10,1/10) = 5)      = 3720087/2500000000.
```

These split events depend on independent edge noise, regardless of the
hidden edge signs. The two eligible events are disjoint. Hence

`P(arithmetic upper-gate eligibility) = p9^e + p5^e`.

Actual resource, numeric and persistence requirements can only reduce the
chance of an installed candidate; an eligible uniform baseline is not a
candidate installation. The probabilities are about **this solver** and
this registered endpoint objective, not all available inference algorithms.

| Tokens | Current arithmetic gate eligibility | All strict edge majorities correct |
|---|---:|---:|
| 8 | 0.00131002072 | 0.988611419 |
| 16 | 0.000000664873350 | 0.975754627 |
| 32 | 0.000000000000171261777 | 0.950540474 |

The last column is `[P(Binomial(10,1/10)<5)]^e`. Whenever all strict
majorities are correct, graph traversal recovers the complete connected
hidden relation up to its irrelevant global bit flip. This gives a
constructive sufficient inference event with high probability while the
current proof gate is almost never eligible. The difference is not an
information-theoretic obstruction.

For the conditioned one-flip-per-edge training law, the 9:1 event holds by
construction and the majority is always true. The positive release fixture
therefore does not measure selection frequency under ordinary IID noise.
It remains a valid correctness fixture under its stated scope.

`model.exact_audit()` enumerates all 121 two-edge count patterns, scores
the actual proposed native graph by independent forward evaluation and
finds exactly five eligible patterns: four combinations of 1/9 zero-label
counts plus the single (5,5) baseline case. Separately, its forest posterior
is checked against enumeration of every hidden assignment in 40 small
connected/disconnected cases. These are implementation/experiment audits;
they do not manufacture a broad Runtime completion or future-value proof.
