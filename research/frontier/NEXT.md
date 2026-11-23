# Next mathematical attack

What changes when a learner carries uncertainty about a shared computation instead of committing to the most likely partition? On the chronological text test all eight earlier words shared one selected response class at three concentrations. The best nontrivial partition improved the integrated likelihood before the per-partition prior was charged. The sum of the predictive support for alternative partitions has yet to be tested. [Training and reporting evidence](EVIDENCE.md#do-learned-response-classes-transfer-to-missing-word-pairs-on-ordinary-text)

## Registered posterior prediction and continued learning

Use the preceding eight earlier and eight current names, its original fitting counts (excluding the same 16 pairs), frozen 256-word output class, raw-bigram backbone and global odds. Freeze concentration 512, selected previously by every fitted family. Prior mass is uniform on the four class counts and uniform within each count. For every partition and block/column use the same beta conditional likelihood and quantize released class probabilities to Q16. The main new predictor averages posterior means over all 2,795 partitions before quantization. Compare it with the previous one-class MAP fit, independent-pair model and unmodified global predictor. Score the next two untouched consecutive blocks of 131,072 targets beginning at 7,700,480. Preserve the old extended-prefix hash, record the new hash after the first read, and report normalized NLL on all, eligible and withheld occurrences. Report both full-stream priced loss and the number of bytes occupied by the installed conditional response matrix relative to the previous packet. Quantify how much posterior probability remains on each class count, how many distinct Q16 row profiles actually result and whether the frozen mixture improves the whole-stream and withheld scores against the previous alternatives. Evaluate the archived five-gram and Transformer on the first 4,096 targets of each block.

Compare three prospective uses of this posterior. Freeze the fit for both reporting blocks. Alternatively allow sequential count and posterior-weight updates only after a correctly ordered observed eligible target and only for pairs permitted by the original training mask. In a third arm allow any eligible target after scoring, labeling masked occurrences that now contribute to later updates. Start all three from exactly the previous fitting evidence. The intervening selection and report labels do not initialize any arm. Include one-class and independent-pair learners with identical admissible updates. Report online loss, update counts, actual working-state bytes, operations or timings, and the cost of exact replay from raw sufficient counts. Count the ordinary-label exposures and distinguish persistent forecast parameters, continuing training memory, transient workspace and live token state. A gain due solely to adaptation shared with the one-class control does not support a claim for posterior structure. Check the partition sum and the first updates against a separately derived exact small example.

The relevant mathematical comparison is between current forecasts, the marginal probability of every block, and the state needed for arbitrary future updates. Use the product-partition prior's actual restrictions when seeking a counterexample. Existing clustering results give exact posterior calculations by subset convolution and partition trees. A direct implementation or mathematical consequence of those calculations should retain its conventional attribution. [Kohonen and Corander](https://arxiv.org/abs/1310.1034) · [Greenberg et al.](https://proceedings.neurips.cc/paper_files/paper/2018/file/29c4a0e4ef7d1969a94a5f4aadd20690-Paper.pdf)

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
