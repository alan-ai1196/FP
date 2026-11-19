# Next mathematical attack

Can a learner create reusable state while scoring every next symbol of a single stream, without word resets, terminal label markers or a supplied transition graph?

Start with an unknown order-bounded binary Markov source and homogeneous flip noise. The memory ceiling determines which raw contexts can be counted. Fit the sign of the next-token conditional by forecasting before every token. Starting with that fitted sign column, repeatedly append observed-symbol transitions and retain linearly independent continuation tests. Compare the learned computation to both an indexed context model and an independent conventional context-tree predictor on exactly the same stream.

An exhaustive finite search over all 256 order-three sign tables found 16 with dimension four and signed-copy width five. Orders one and two had none. One order-three table predicts a positive sign exactly on contexts 001 and 100. This table was selected **after** the search. Before running the stream learner, predict that the same fitting code will recover its four-dimensional update at noise 1/4 from a sufficiently covered single stream. Test the coverage argument at stopping times and charge the original context counts. A language claim would also require lifting the binary conditional-law restriction and establishing the cost of acquisition on the real vocabulary.
