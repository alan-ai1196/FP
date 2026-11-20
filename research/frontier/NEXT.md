# Next mathematical attack

How can ordinary sequence observations teach the learner which output distinctions to create when changing the mass of a frequency-defined group has a strict predictive ceiling?

Start with two observable history classes and a finite next-token alphabet. Learn the output partition from counts of actual history/next-token pairs. Derive an exact optimizer for the gain from distinguishing history classes through a fixed number of groups, charge its search and storage, and compare against ordinary predictive word clustering with the same counts. Test the algorithm independently by enumerating all partitions of small alphabets. Establish what changes when the decoder also conditions on the most recent token. A partition valuable for one history distinction can discard a different useful distinction in a later context.

The decisive text comparison must use a training-only partition, a matched frequency partition, the same within-group successor rows and a held-out history-dependent mass predictor. Recompute the within-group oracle floor for each partition. An improved oracle floor alone does not establish that a causal learner can realize the improvement. [Current obstruction](OBSTRUCTIONS.md)

## Fixed original-stream comparison

Use the same first 786,432 training tokens, two subsequent blocks of 131,072 targets, and original exposed reporting interval. Fit the frequency bit on the first block as before. On its targets starting at index two, count each token against the frequency bit of the token two positions earlier. Fit the best binary posterior-ordered partition by ordinary count loss, keeping equal posterior values together and using the first minimizing boundary. Place an unseen token at the pooled training posterior.

Cross the frequency and posterior-learned partitions as the stored one-step-delayed input bit and the output group. In all four arms, preserve the original full successor distribution inside each output group. Fit the current-token group rate on the second block with the original row mass as a prior of weight 64. Fit its two history-conditioned rates with the fitted current-token rate as a prior of weight 64. Round all deployed rates to interior points of denominator 4,096. The third block pays for a row's two conditional rates and token ID (40 bits), and for one shared history bit if any row is used, at the previously studied deployment horizon of 256 gate workloads. Use integer log bounds, preserve every selected arm and count row lookups and search work.

Report all four frozen scores, both overwrite controls, the original full bank and both within-group oracle floors. The registered positive test requires the learned-input/learned-output arm to beat its own overwrite, the frequency-input/frequency-output arm and the original bank. This is an empirical test of useful learned distinctions under an ordinary backed-off categorical predictor on previously exposed positions.
