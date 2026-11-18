# When does a learner earn a cheaper read?

This note derives the positive case in Part IV of the [reconstruction](REPORT.md). The losses are population log losses in nats unless a finite tape is named. A “read” returns one current source cell. Training memory, bit operations and forming a cell are additional costs.

## 1. Which operations can route values of arbitrary type?

Suppose a predictor has side information $h$ before it inspects $M$ values. For every finite output alphabet $A$ it combines distributions $p_1,\ldots,p_M$ on $A$ by a map $F^h_A$. Consider the following explicit restriction: **postprocessing every value by the same stochastic channel $T:A\to B$ may be deferred until after combination**,

$$ F^h_B(Tp_1,\ldots,Tp_M)=T F^h_A(p_1,\ldots,p_M). \tag{1} $$

Here $h$ stays fixed, including any already purchased information about the keys. Equation (1) says the combination is indifferent to how a downstream observer interprets values. It is a testable assumption. Statistical mixtures are one possible realization. There is no assumed linearity, positivity of internal computation, graph of operations or differentiability.

**Characterization.** The only such families are $F^h_A(p_1,\ldots,p_M)=\sum_j w_j(h)p_j$, for unique $w(h)\in\Delta_M$. Evaluate $F^h$ on the distinct point masses on the address alphabet $[M]$ to obtain $w$. Apply (1) to the channel whose $j$th column is $p_j$. Conversely every such mixture commutes with every channel by distributivity. If the discrepancy in (1) is uniformly at most $\epsilon$ in total variation, the same tagged-input argument puts every output within $\epsilon$ of this **one** family of mixtures. This characterization is related to classical linear opinion pooling. McConway obtains linear pooling from marginalization with different hypotheses. Our full-channel condition gives the short proof above. [McConway, *Marginalization and Linear Opinion Pools*](https://doi.org/10.1080/01621459.1981.10477661)

The one-hot vertices select individual values. The entire simplex is forced once an uncertain choice is allowed. Permuting address names permutes the coordinates of its law. Mixing twice composes the two stochastic matrices. Thus shared conditional laws can be evaluated once for a fixed observer. Neither the source of $w(h)$ nor a cheap algorithm to evaluate it follows from (1). Voting by majority, creating a new label, and interactions that depend on inspecting the values can violate (1). An upstream machine may do any of these, but their acquisition and evaluation must then be priced there.

## 2. A causal learner from ordinary labels

Assume the following data law for a falsifiable subproblem. One latent $J$ is drawn uniformly from $M\ge2$ named addresses and is persistent across an episode. Each event supplies a new row of mutually independent fair bits $X_{tj}$, independent across time and of $J$. The next binary token is $Y_t=X_{tJ}\oplus E_t$ with independent noise of known rate $\eta\in[0,1/2)$. Row cells precede prediction. The label becomes available only after it. Message addresses and their prices are specified. The learner receives neither $J$ nor an update from a structural supervisor. The assumption that **some** source persists is genuine prior structure.

Conditional on the prefix, let $w_j=P(J=j\mid\text{prefix})$ and $\theta=1-2\eta$. With all row bits read, strict propriety uniquely gives $p(Y=1)=\eta+\theta\sum_jw_jX_j$. If only $A$ was read by an adaptive policy, conditioning on its transcript gives

$$p_A=\tfrac12+\tfrac{\theta}{2}\sum_{j\in A}w_j(2X_j-1). \tag{2}$$

Unqueried bits are still independent fair conditional on the stopped transcript. If all values were available during training, multiply the weights by $1-\eta$ on a match and $\eta$ on a mismatch, then normalize. If some were unread and unavailable to the update, their likelihood is $1/2$. These are Bayes' rule on the *obtained* evidence. No counterfactual reads enter the update.

For $0<\eta<1/2$, let $k_j=(2X_{tj}-1)_{t=1}^n$, $q=(2Y_t-1)_{t=1}^n$, with all training columns observed. The accumulated likelihood gives

$$ w_j=\operatorname{softmax}_j\!\left(\tfrac12\log[(1-\eta)/\eta]\,q^\top k_j\right). \tag{3}$$

The number of matches is $(n+q^\top k_j)/2$ and the shared factor cancels. This is an **exact dot-product attention readout** on the noisy-copy distribution, with a likelihood-determined temperature and a uniform prior. Its values are the current predictive source distributions. The dot products can be updated as integer counts without storing keys of length $n$. The $\eta\downarrow0$ limit weights maximum matches equally. On a noiseless-law history these are exactly the consistent addresses. A history inconsistent with every noiseless source has zero probability in that model. The positive-noise limit on such a history does not define conditioning on a zero-probability event. Learned key embeddings, multilayer self-attention and realistic language inputs require additional assumptions. The general attention formula is due to [Vaswani et al.](https://arxiv.org/html/1706.03762). The positive random-feature approximation used in original FP has a different premise and describes function approximation. [Choromanski et al., Lemma 1](https://arxiv.org/html/2009.14794)

For arbitrary causal positive expert likelihoods, the same persistent-address update with a full read gives the whole prefix probability $\sum_j\pi_j\prod_t p_{jt}(y_t)$. This follows by telescoping the successive normalizers. Its cumulative log loss is at most the best fixed expert's loss plus $-\log\pi_j$ for that expert. The comparison class is a single persistent expert. A context-sensitive composition of experts may be much better than that entire class.

## 3. Optimal paid reads, including adaptive competitors

**Theorem.** For a fixed reached posterior $w$ and a hard budget of $k$ equally priced fresh cell reads, a Bayes-optimal policy reads the $k$ largest weights (up to zero weights and ties) and forecasts (2). This compares with *every* adaptive, randomized read policy. More reads cannot increase expected optimal risk.

Condition on the history, coins and signs already observed. Given a current success probability $a$ before a new read, revealing a weight $v$ averages $h(a+\theta v/2)$ and $h(a-\theta v/2)$. By concavity this average decreases with $v$ throughout the feasible interval. For a fixed set of other observations the same inequality holds conditionally on all their signs. Induct on the number of reads remaining. After any first read the induction hypothesis selects the largest remaining weights for either sign. If the first read excluded a larger weight from the resulting set, exchange the two conditional on all other signs. Thus the top set is optimal at every partial history. Zero-benefit reads can be omitted. This is a property of the experiment's conditional independence, scalar symmetric increments, binary log score and hard budget.

Write $L_k(w)=\mathbb E[h(p_{\mathrm{top}\ k})]$. For positive noise, using the curvature $1/[p(1-p)]$ of negative entropy on $[\eta,1-\eta]$ gives

$$
\frac{\theta^2}{2}\sum_{j>k}w_{(j)}^2
\ \le\ L_k(w)-L_M(w)\
\le\frac{\theta^2}{8\eta(1-\eta)}\sum_{j>k}w_{(j)}^2. \tag{4}
$$

Indeed the conditional residual about $p_{\mathrm{top}\ k}$ has mean zero and variance $\theta^2\sum_{j>k}w_{(j)}^2/4$. Apply Taylor's formula to the expectation with curvature bounds $4$ and $1/[\eta(1-\eta)]$. This prices deletion against the full *learned* predictor. If all weights are still diffuse, deleting many cells can be cheap because even the full predictor knows little. Its quality must also be compared with the informed risk $h(\eta)$.

At positive noise all weights are positive after any finite word. Exact evaluation on every fresh row still needs all $M$ cells, since flipping an unseen bit changes its output by $\theta w_j$. Yet the best one-read forecast can be close in risk. For the true address $i$ and a wrong $j$, the expected square root likelihood ratio per complete event is $A_\eta=(1+2\sqrt{\eta(1-\eta)})/2$. With probability $1/2$ their bits agree, and otherwise sum the two noise outcomes. Independence, Markov's inequality and a union bound give $P(\hat J_{\rm MAP}\ne J)\le(M-1)A_\eta^n$. Under the stated prior this error equals $\mathbb E[1-\max w]$. Equation (4) consequently bounds the expected one-read excess over the full forecast by $\theta^2\min(1,(M-1)A_\eta^n)/[8\eta(1-\eta)]$. This is a sufficient acquisition bound. Setting a small probability permanently to zero changes future learning.

The output operation matters even with identical row encoding and machine. If only a **sample** from the forecast is requested, first draw $j\sim w$, read $X_j$, and toss the noise coin. Conditional on the row the sample has the exact full output law with one value read. Sampling the address itself still costs work and randomness. Scoring the calibrated probability before observing a target requires the evaluation above. Giving a sampled delta distribution to a log-loss evaluator can incur infinite loss. A stochastic kernel alone therefore determines neither its sampling cost nor its likelihood evaluation cost.

## 4. When an ordinary update physically removes work

With $\eta=0$, store the set $S$ of columns matching all past labels. Its posterior is uniform. Before each training target, read the live addresses, emit their empirical fraction of ones, and retain their bit values until the target arrives. Filter the list in place. A discarded column has zero likelihood under **every** continuation in this fixed noiseless model. For full Bayes forecasting, every surviving column really is needed on every fresh row. Two completions of any partial transcript differing in one survivor give different forecasts. This lower bound counts independent, previously inaccessible cell values, including for a randomized algorithm required to give exact answers almost surely.

Conditional on the true column and its $n$-bit target string each of the $M-1$ wrong columns independently survives with probability $2^{-n}$. The law is independent of the string. Therefore

$$ s_n=|S_n|\sim 1+\mathrm{Binomial}(M-1,2^{-n}),\qquad
 P(s_n=1)=(1-2^{-n})^{M-1}. $$

Summing pre-target expectations, the sharp cumulative expected training-read count for exact full forecasts over $n$ events is

$$ n+2(M-1)(1-2^{-n}). \tag{5} $$

Approximately $\log_2 M$ examples can identify a route, yet the first exact prediction already costs $M$ reads. After $n$ training events and a fresh hard budget $k$, put $r=\min(k,s)$. The exact minimum expected next log loss among learners with full training information is

$$
 \mathbb E_{s=s_n}\!\left[2^{-r}\sum_{i=0}^r {r\choose i}\,
 h\!\left(\tfrac12+\frac{2i-r}{2s}\right)\right]. \tag{6}
$$

This follows either from the theorem or direct exchangeability of the survivors. The filter reaches (6) on ordinary examples. Unlimited preprocessing of those same examples cannot improve its Bayes risk.

Every nonempty subset can occur immediately after the first training label. Two distinct sets give different full forecasts on a row having a single one in their symmetric difference. Thus any exact full predictor at that boundary must distinguish $2^M-1$ states, requiring $M$ fixed-length bits for $M\ge2$. A mask attains that state count up to the unused empty word. After identification an address takes $\lceil\log_2 M\rceil$ bits. Training memory peak and eventual deployment memory answer different questions.

A compacting array implements the filter with $O(M\log M)$ bits for addresses, $O(M)$ temporary bits in the first event, $O(s)$ address operations per current full forecast/update, and integer counters of $O(\log M)$ bits. Initializing the address list costs $O(M)$. A mask saves bits but scanning it can still cost $M$ bit tests per event. Under noise, exact match counts take $O(M\log(n+1))$ bits plus the cursor. For $\eta=u/v$ rational, one literal exact evaluation uses weights $(v-u)^{m_j}u^{n-m_j}$ of at most $O(n\log v)$ bits each and accumulators with another $O(\log M)$ bits. The powers can be computed by squaring in $O(\log(n+1))$ integer multiplications each at that bit scale. A count comparison suffices to choose the top address, but evaluating its calibrated probability also needs the other weights' normalizer or an adequately updated cached total. Counting saved *input reads* alone would overstate a speedup.

## 5. Which symbols are worth a memory cell?

**Oracle frontier with a reachable finite-data comparison.** Before a fresh row, compress knowledge of the uniform true address into at most $1\le K\le M$ possible deployment messages. Give the deployed machine that message, a single read and private randomness independent of the row and source. Its decoder and address table are fixed independently of the episode. The message is its only source-dependent side information. Decoder/program storage, training memory and variable-length rates are separate resources. Define $d(x)=\log 2-h((1+x)/2)$, and $g(m)=m\,d(\theta/m)$. Then the exact optimum gain over guessing is

$$ G^*_{M,K}=\frac{(K-1)g(1)+g(M-K+1)}{M}. \tag{7} $$

For fixed encoders the Bayes decoder can choose a deterministic read. For fixed decoder policies the encoder can select the lowest-risk message for each $J$, so randomizing cannot improve the optimum. Shared independent coins also only mix deterministic contracts. Thus consider partitions of $[M]$. In a nonempty cell of size $m$ the posterior is uniform. The best one-read choice is any member, giving conditional gain $d(\theta/m)$. Sum with the cell probabilities $m/M$. Finite optimal decoders with zero probabilities can be taken on their actual support when $\eta=0$. Unused messages can always be filled by splitting a nonsingleton, strictly increasing gain when $\theta>0$.

On $m>1$, $g(m)$ is strictly convex and decreasing, as seen from the positive series

$$g(m)=\sum_{l\ge1}\frac{\theta^{2l}m^{1-2l}}{2l(2l-1)}.$$

It extends continuously to $m=1$, including $\theta=1$. Moving one member from the smaller of two nonsingleton cells to the larger increases their sum by strict convexity. Iteration proves (7) and the unique optimal multiset of cell sizes. The identities of the singled-out addresses remain unidentifiable by the symmetric objective. The resource constraint favors a few perfectly distinguished identities and one pooled group, even though the world is exchangeable. A bit-width bound alone had not predicted that allocation.

Finite training has less information than knowledge of $J$. Formula (7) is an upper bound on its gain. Here is an explicit reachable comparison for the noiseless case. After ordinary filtering draw $\hat J$ uniformly from the $s_n$ survivors, then send the cell of $\hat J$ in the partition above. With $p=2^{-n}$,

$$a=P(\hat J=J)=\mathbb E[1/s_n]=[1-(1-p)^M]/(Mp),\qquad b=(1-a)/(M-1).$$

To obtain the expectation, integrate $(1-p+pt)^{M-1}$ from 0 to 1. The uniform tie draw makes each ordered wrong address equally likely by symmetry. Bayes' rule then gives posterior $b+(a-b)/m$ for each address inside the transmitted cell. Read any one of them. The achieved gain is $\sum_{\rm cells}(m/M)d(b+(a-b)/m)$ and tends to (7) as $n$ increases. It uses private training randomness, or one can report the exact mixture over draws. Sampling from $s$ items by binary rejection needs fewer than two trials in expectation, with unbounded worst-case trials. The finite-$n$ expression is an achievable bound. It does not assert that the randomized encoder is finite-data optimal.

The formula exposes a physical assumption that a “symbol” explanation can easily hide. If a compiler is allowed to rewrite uncharged decoder code separately for each trained instance, the true address can instead be embedded in that code with one constant message. That modified interface invalidates the bound. Count episode-dependent code as memory.

## 6. Adversarial boundaries

* **Redundant evidence.** Give three columns weights $(4,3,3)/10$ and make columns 2 and 3 identical, independent of column 1. Reading either duplicate reveals weight $0.6$, whereas the largest individual weight reveals $0.4$. The strict ordering of $d$ reverses the top-address policy. The data cannot distinguish the two duplicate identities. Values with correlated innovations require their actual joint law.
* **Adaptive stopping.** With three equal weights, zero noise and two bits already read, the value of reading the last one is $h(5/6)-h(2/3)/2$ if the first two agree, versus $\log 2-h(2/3)$ if they disagree. A per-read cost between the two favors different actions after the same number of observations. Hard-cap optimality is insufficient for pricing optional work on each path.
* **Interaction.** A binary output equal to XOR of two deterministic binary values violates (1). At input $(1,1)$, a common constant-to-one postprocessing forces output one, while XOR gives zero. An unrestricted Boolean predictor computes it in one XOR after two reads, and positive categorical conjunctions can encode its noisy version. A routing-only invariant cannot be universal. Appending a free value containing XOR would build the solution into the interface.
* **Future numerical reversal.** At $\eta=1/4$ two initially equal hypotheses can accumulate sixteen net matches in favor of the first. The other's exact probability $1/(1+3^{16})<2^{-25}$ rounds to zero under binary16 nearest-even. Sixteen opposite events restore exact equality. A multiplication-only update from the rounded zero never recovers it. Counts avoid this state collision and still incur finite evaluation costs.
* **Unobserved structure.** The filter eliminates addresses. It never invents a new source family, key function, or program for transforming a label. The causal data law explicitly supplies the persistent-selector hypothesis. A conventional version-space learner or Bayes mixture gets exactly the same predictions using the same observations. If a physical implementation claims a gain, that competitor also receives compacted lists and the same memory interface.
* **Lifetime of a distinction.** Choose one of two fair addresses persistently, or redraw it uniformly at every event. Both laws implement the same one-row operator with weights $(1/2,1/2)$. After a noiseless row $(1,0)$ and label 1, their predictions on another $(1,0)$ are 1 and $1/2$. The temporal source law is independent information. There is also a falsification test using ordinary data. The first empty survivor set refutes the noiseless persistent model. Under redraws, each specified address matches a training label with probability $(1+1/M)/2$ independently across rows. After $n$ rows the probability of still accepting any address is at most $M[(1+1/M)/2]^n$. Zero false rejection under persistence relies on strictly zero noise.

## 7. How much can context change a routing loss?

Take any finite sequence of value banks and scored labels. Write $a_{tj}\ge0$ for source $j$'s probability of the actual label at position $t$. Let $L_*$ be the minimum mean NLL over *all fixed* mixtures of these sources. A context-sensitive method uses a vector $w_t$ at each position. Define $c_j=\max_t w_{tj}$ and $C=\sum_j c_j$. Then

$$ L_{\rm contextual}\ \ge\ L_*-\log C. \tag{12} $$

Indeed $u=c/C$ is one fixed distribution and $w_t\cdot a_t\le C(u\cdot a_t)$ for every $t$. Take logs and average. This holds even if the gate chooses weights with hindsight. $C$ is the **least uniform multiplicative factor** with which a single distribution can dominate all the $w_t$ for every nonnegative readout. Test each individual address to see that any dominating $v$ requires $Cv_j\ge c_j$. This establishes sharpness of the pointwise domination constant. A particular text score can have a looser loss bound. Mathematically $\log C$ is the finite-channel maximal-leakage expression for the map from position to a sampled address, with full support on the scored positions. The argument here uses its domination property for log loss. [Issa, Wagner and Kamath, Theorem 1](https://par.nsf.gov/servlets/purl/10164324)

If each $w_t$ is any convex combination of $K$ fixed address distributions $v_i$, then $c_j\le\sum_i v_{ij}$ and $C\le K$. Arbitrary contextual computation of the gate or continuous interpolation among those $K$ distributions cannot buy more than $\log K$ nats/token over the best fixed vector. Equal use of $K$ disjoint deterministic predictions on $K$ equally frequent different labels attains the general $\log K$ allowance. For a hard message $z_t$ selecting a single vector one can also form $u=\sum_z f_z v_z$ with empirical message frequencies $f_z$ and obtain the stronger $L_{\rm contextual}\ge L_*-H(f)$. These inequalities concern routing among the **same** source distributions. New value transformations change $a_{tj}$ and must be tested afresh.

This gives a post-result consequence of the preregistered frozen text certificate. Its outward lower endpoint is 7.236294824. Two fixed lag-weight vectors, even with an unrestricted context gate between them, give a lower bound exceeding **6.543147643** nats/token after subtracting $\log 2$. The archived Transformer scored 6.260544623. The difference rules out this whole two-vector extension on this suffix. Three vectors are a necessary count for this comparison when the weights lie in such a hull. Sufficiency, a lower bound on Transformer head count, and a physical cost per vector do not follow. Against order-5 MKN, the two-vector bound is already inconclusive. [Original text receipt](text_capacity_result.json)
