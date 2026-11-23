# Next mathematical attack

When should a learner spend a training observation by continuing the same episode, and when should it reset to learn about variation between episodes? Receiving infinitely many short episodes can leave an entire family of long-horizon predictions unidentified. A procedure given the correct paired-coin shape bypasses that obstruction. The aim now is to learn the needed distinction from predictive errors while accounting for the price of acquiring observations, storing a reusable model and updating a fresh state. [Exact obstruction at three draws](OBSTRUCTIONS.md#three-draw-training-can-hide-a-continuum-of-different-future-predictors) · [Acquisition and live memory at a known model shape](FOUNDATION.md#what-does-it-cost-to-learn-the-prototype-that-a-small-state-uses)

## Mathematical target

Compare separated and coalescing mixtures of persistent, unlabelled episode biases. Give the training agent only ordinary bits and a choice to continue the current episode or buy a reset. Each new episode resamples a component with unknown weights. A fresh evaluation episode is independent given the shared environment. The agent must issue probabilities at every draw, and may continue learning. A useful deployment metric is the minimax total log loss above an observer who knows the shared environment but must infer the fresh component. Price the calibration observations and packet, the live state, any arithmetic tables, and the computation needed to condition on the packet.

First characterize which training experiments determine the future law without assuming its support count, radii or mixture weights. For a fixed group length, a binary path has a likelihood polynomial of that degree in its episode bias. Determine the decision consequence of the missing higher moments for a declared class of future horizons. Address cases where the conditional information lower bound remains bounded because there are only finitely many alternatives. Compare the classical grouped-mixture identifiability theorem against the stronger quantitative requirement of small future log loss. Inspect whether statistical uncertainty over unknown shape should be carried by the learner or whether an ordinary updating residual can earn the same score at smaller cost.

For adaptive training curves, distinguish the information about weights acquired from independent resets from the information about biases acquired by extending a group. A single long episode can estimate its own bias accurately without measuring how frequent its component is. A very large supply of short episodes can exhibit the converse obstruction. Compare the best fixed allocation, a learner selecting group length using only past observed bits and costs, and a conventional mixture predictor with the same observations. New inputs should test transfer to unseen group lengths or observation choices. Keep agent-controlled, observed resets distinct from unobserved changes of component. Feng and Meng give a much higher memory order for a fixed strictly positive switching law than the persistent-coin bound, providing a recent comparison for testing which information is useful after a reset. [Primary source, §4](https://arxiv.org/html/2611.13760v1#S4)

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
- [Learning unknown sensor response classes](https://github.com/alan-ai1196/FP/blob/28e5a3d/research/frontier/NEXT.md)
- [Learning earlier-word response classes on chronological text](https://github.com/alan-ai1196/FP/blob/3b17ced/research/frontier/NEXT.md)
- [Posterior averaging and sequential word-pair prediction](https://github.com/alan-ai1196/FP/blob/8793590/research/frontier/NEXT.md)
- [Cost of a compressed learning state under future observations](https://github.com/alan-ai1196/FP/blob/02832d5/research/frontier/NEXT.md)
- [Acquiring a compact predictor from ordinary paired episodes](https://github.com/alan-ai1196/FP/blob/0940e87/research/frontier/NEXT.md)
