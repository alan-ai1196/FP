# Next mathematical attack

What does a finite memory have to preserve when its own actions change the data it can learn from? For one-stage decisions, a state has a measurable worst loss over a specified family of payoffs. A sparse graph of the decoder entries can make this loss computable. A continuing agent must pay to update its state and choose its actions before seeing the next signal. [One-stage decision criterion](INTELLIGENCE_OBJECTIVE.md#what-can-an-unknown-decision-lose-when-a-state-discards-information) · [Tractable case and computational obstruction](OBSTRUCTIONS.md#even-checking-the-value-of-a-fixed-compression-can-be-hard)

## Mathematical target

Consider a finite controlled experiment with a hidden environment, an observation and action at each time, and a bounded terminal payoff. Compare full observation history against a candidate learned recurrence with a declared number of states, a serialized update table and charged computation. Determine which finite-horizon decision gaps can be characterized by a single causal simulator that must respect actions and the arrival times of observations. Compare this with a simulator allowed a different reconstruction for each policy. A gap between their values would identify an assumption hidden by the one-stage analysis. Existing comparisons of sequential experiments delimit claims about timing and payoff classes. [Whitmeyer and Williams](https://arxiv.org/abs/2405.13709) · [Comparison in sequential social learning](https://arxiv.org/abs/2503.05015)

The first finite check should include an optional information-gathering action, delayed consequences and two future payoffs that value different distinctions. Enumerate the finite policies and causal memory updates to check any proposed theorem against their exact returns. Distinguish the cost of a simulator witnessing a mathematical comparison, the state a deployed policy must carry, and the evidence available to learn that state. The ordinary-text predictor, separately fitted conventional model and held-out decisions remain independent tests of a candidate foundation.

## Registered controlled acquisition from later token predictions

Two consecutive raw names \(u,v\) range independently over eight IDs. Independent hidden permutations assign each name a three-bit word on each side. Their bitwise XOR gives three unobserved routing bits. After the second name the system must retain its state and forget both inputs. A uniformly chosen task index \(j\) arrives. The agent may pass or pay to query sensor zero or one. The queried sensor returns the requested fair target bit with probability 7/8 if its number matches routing bit \(j\), and returns a fair independent bit otherwise. A pass returns a blank. The eventual ordinary binary target is always observed. The target is independent of the two raw names, and either sensor response is marginally fair for every pair. The names can change how strongly the response predicts the eventual target. Only the selected sensor outcome is present in the training stream.

Freeze environment seeds 257, 509, 1021 and 2039 and use independent PCG64 streams keyed by environment seed and purpose for the permutations and recorded episodes. Hold out all raw pairs whose column ID minus row ID equals 0 or 3 modulo 8. Train on prefix sizes 384, 3,072 and 24,576 independent episodes from the other 48 pairs. Choose each logging action uniformly from pass and the two sensors. Use the same episodes across learners. Test on exact population reward and conditional target log loss under each deployed policy, for all 64 pairs and separately the 16 unseen pairs. Query costs are 1/8 and 9/32. The target's balanced marginal is public. After a purchase the chosen action policy copies the response and after passing guesses zero. These are Bayes-optimal terminal decisions for the declared nonadversarial sensors.

Fit two predictive models without giving them any routing labels. The first uses Jeffreys-smoothed observed target-response agreement by raw pair, task and purchased sensor. The conventional factor model fits an XOR of binary row and column memberships separately for each task by exact conditional likelihood; the incorrect sensor agreement rate is 1/2 and the correct rate is selected from 5/8, 3/4, 7/8 and 15/16. It is supplied this factor family and the interpretation of the sensor. Compile each forecast to a constant state, an arbitrary one-bit update after each of the first and second names, and a one-bit final state with full first-name access. Optimize the final two-state policies across all pairs using equal input exposure, including the names of the withheld pairs but none of their outcomes. Enumerate all pass and two-sensor choices at each final state and task, and optimize the arbitrary raw type lists under each such policy. Include a direct raw-pair readout and a conventional three-bit factor state, with their different memory and acquisition budgets. Include a pass-only training control. Count serialized tables and carried bits at both input stages. Validate deployed predictions or actions against the reference and measure the direct table execution. A separate finite population audit will enumerate the binary final statistics and the legal local decisions, and test whether the first-stage memory restriction changes the best attainable value.

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
