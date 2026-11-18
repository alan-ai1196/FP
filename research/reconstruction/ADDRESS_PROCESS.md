# From one routed value to a learned process

An operator on one row can describe the present readout while leaving the lifetime of an address completely undetermined. This note derives the multitime object and exhibits a distinction which is easy to generate, expensive to identify, and of little value for average prediction.

## The multitime characterization

At each of $d$ times let there be $M$ supplied distributions $p_{tj}$ on an arbitrary finite value alphabet $A_t$. Begin with fixed, externally supplied rows. A family $F_{A_1,\ldots,A_d}$ specifies a joint output distribution on $\prod_t A_t$. Suppose that applying any stochastic channel $T_t:A_t\to B_t$ to all values in row $t$ commutes with applying $\bigotimes_t T_t$ to the joint output. The channels may differ by time. Any fixed public side information is held constant on both sides.

**Theorem.** Such a family is uniquely equivalent to a probability measure $\mu_d$ on address paths $[M]^d$. It acts by

$$ P(y_{1:d}\mid p)=\sum_{j_{1:d}}\mu_d(j_{1:d})\prod_{t=1}^d p_{t,j_t}(y_t). \tag{8} $$

Give every row the alphabet $[M]$ and the $M$ distinct point masses. Their joint output defines $\mu_d$. Apply the channel with columns $p_{tj}$ at each time to obtain (8). Conversely the expansion commutes with every specified product channel. Tagged inputs recover every coefficient, proving uniqueness. Consistent output prefix marginals for every horizon are equivalent to consistent address marginals, by marginalizing (8) and by evaluating it on tags. Thus for exogenous announcements the object is an ordinary stochastic process of address choices followed by local observations. An arbitrary joint law on the *values* could violate this assumption. In particular, allowing the postprocessing channels to share unpriced noise would change the statement.

The conditional forecast is obtained by summing the weights of paths compatible with the observed emissions, multiplying by the next local emission, and normalizing. A positive-probability condition is needed at the conditioning boundary. Filtering produces a state in a continuous probability simplex over discrete path prefixes or residual laws. Two prefixes with the same conditional future address law share one continuation computation for every future value channel. Tagged channels distinguish different laws if such diagnostic inputs are available. Open-loop naturality does not grant the learner a tagged intervention. For adaptive row generation a feedback protocol must also specify how the mechanism behaves under those choices. In the following experiment rows are independent of the address process, so this issue is decided by the data law.

Equation (8) gives SUM and PRODUCT a precise origin for this problem. They implement marginalization and conditionally independent emissions. A positive FP circuit can evaluate this finite expansion with the appropriate sources and readout, subject to coefficient and resource constraints. Its explicit expansion may have $M^d$ terms. Temporal dependence, exact state sharing and evaluation order are properties of $\mu_d$ and of the machine used to evaluate it. The invariance alone chooses no cheap factorization. A static selector, a fresh address every time and a Markov address process all satisfy it.

## Can the law be acquired without address labels?

In each independent reset block draw $J_{1:d}\sim\mu_d$. At each time the new $M$ input bits are independent and fair, and $Y_t=X_{t,J_t}\oplus E_t$ with independent noise of known rate $\eta<1/2$. Write $\theta=1-2\eta$ and $\sigma(x)=2x-1$. Every path probability has a passive moment:

$$
\mu_d(u)=\theta^{-d}\,\mathbb E\!\left[\prod_{t=1}^d\sigma(Y_t)\sigma(X_{t,u_t})\right]. \tag{9}
$$

Conditional on the address path, a factor has mean $\theta$ on a match and zero on a mismatch. Timewise independence of the conditional experiment gives (9). This acquisition result uses ordinary observed bits and next labels. With duplicated columns the orthogonality argument fails, even with unlimited data.

There is an explicit learner for unrestricted $\mu_d$ at fixed $M,d$. Start uniform, predict sequentially from the last fitted law by (8), and after each entire block add the observed sign products to their path counters. For $N\ge1$, estimate each coordinate using (9) with its empirical mean, replace negative estimates by zero, add $1/N$ to each, and normalize jointly. Use that law's marginals at earlier time indices. The positive floor makes conditional prediction well-defined on supported emission rows and vanishes for fixed $M,d$ as $N$ grows. The strong law gives consistency of this finite vector. Hoeffding and a union bound put all raw coordinates within $e$ with probability at least $1-2M^d\exp(-N\theta^{2d}e^2/2)$. This says nothing about accurate conditionals on a very rare prefix without controlling its probability.

Even this uninformed learner needs $M^d$ counters for the explicit table, $O(M^d\log(N+1))$ bits for the signed sums and $O(dM^d)$ direct arithmetic per block. Reading the $dM$ raw cells once suffices if cached for the update. With rational noise, evaluating the scale and fitted predictions also costs bits for the powers and products. One coordinate costs only $d$ cell reads per block when the desired path is known in advance. Paying only for that coordinate would supply a structural hint in a study purporting to discover it. The direct learner does not find a minimal state realization or imply a polynomial sample/runtime guarantee. The persistent subfamily has the much cheaper exact filter in the [routing proof](ROUTING.md).

## A two-state separation of observation, identification and value

Set $M=2$ and use address bits 0 and 1. A fixed unknown sign chooses $\mu_+$, uniform over even-parity address paths, or $\mu_-$, uniform over odd paths. Reset the latent path independently each block, keeping the same unknown sign. Given the sign, a generator tosses $d-1$ fair coins and uses running parity to set the last address. It needs one parity bit and the declared block clock. The sign is an additional bit specifying the world. Let $P_+,P_-$ denote the two laws of the **fully observed** rows and emitted labels.

A block can distinguish these laws only if the two cells differ at every time. Call this event $I$, with probability $r=2^{-d}$. If some cells coincide, the corresponding latent address is hidden even after the label. The other addresses on informative rows have identical uniform marginals in both parity worlds. If $I$ holds, undo the orienting bit $X_{t,0}$ in each label. This gives the address path with independent bit flips. Its probability at a word $z$ is

$$ 2^{-d}\bigl(1\ \mathord{\pm}\ \theta^d(-1)^{\sum_t z_t}\bigr). $$

Indeed the parity sign multiplies across flips and each flip attenuates it by $\theta$. Summing the uniform law over noise words gives the formula. Conditional on the recovered parity, all other distinctions have the same law in the two worlds.

**Observation and sample cost.** One block has total variation exactly $r\theta^d$. Its Bhattacharyya affinity $\rho=\sum_o\sqrt{P_+(o)P_-(o)}$ is $1-r(1-\sqrt{1-\theta^{2d}})$. With clean labels and equal world prior, the exact optimal error after $N$ independent blocks is $(1-r)^N/2$. It takes one informative block to distinguish the worlds perfectly and none of the other blocks favors either world.

For $0\le\eta<1/2$, the number of blocks necessary and sufficient for error at most $1/4$ has order

$$ N_{1/4}=\Theta(2^d/\theta^{2d}). \tag{10} $$

To see this without assuming any particular learner, the product affinity is $\rho^N$. Summing $\min(P,Q)\le\sqrt{PQ}$ bounds the Bayes error above by $\rho^N/2$. Cauchy–Schwarz on $|\sqrt P-\sqrt Q|(\sqrt P+\sqrt Q)$ bounds it below by $(1-\sqrt{1-\rho^{2N}})/2$. The likelihood-ratio decision attains the optimal error. It can be implemented by counting the two observed parity signs on informative blocks. Since $x/2\le1-\sqrt{1-x}\le x$ for $0\le x\le1$ and $\rho\ge1/2$, the necessary and sufficient orders agree with universal constants. All individual reads are free to the learner for this lower bound. Latent compactness even with a known two-world model does not settle passive acquisition cost.

**Predictive value.** An oracle knowing the sign saves exactly

$$ g_d=2^{-d}\left[\log2-h\bigl((1+\theta^d)/2\bigr)\right] \tag{11} $$

nats on one fresh block over the equal-prior predictor. Before the final emission the two worlds give identical prefix laws. On $I$ they differ only in the parity bit with reliability $\theta^d$ and elsewhere they agree. Equivalently (11) is the mutual information between the world sign and the observed block. The entropy series gives $x^2/2\le\log2-h((1+x)/2)\le(\log2)x^2$. Hence $N_{1/4}=\Theta(1/g_d)$. When $\eta=0$, the expected gain per next token across the block is only $2^{-d}\log2/d$.

A predictor that updates the equal prior on the two possible worlds over successive blocks has cumulative excess log loss relative to either known world bounded above by $\log2$ on every word possible in that world, by the mixture likelihood identity. Thus insisting on a reliable structural verdict can demand exponentially many observations even when its maximum *cumulative predictive penalty while learning by mixture* is one bit. The learner in this last bound was given the two laws. It is an especially strong comparator for the lower bound, and the unrestricted learner (9) receives no such hint.

This separation answers a different question from a parity circuit-size bound. There is a compact generator, and passive identification is possible at every finite $d$. The scientific obstacle is how often observable labels reveal an interaction and how much predictive work its identification could repay. Neither hidden graph size nor a rule requiring retention of every latent distinction determines those quantities.

## General binary law and the role of unscored observations

Let a fixed experiment produce an observable episode $O=(X_1,Y_1,\ldots,X_d,Y_d)$ with finite laws $P$ or $Q$ according to an equally likely persistent world bit $W$. All reads, coins and side observations available for identification belong in the transcript. Only the $Y_t$ are scored. Each comparison uses the Bayes-optimal *causal* forecast before the respective target. Denote by $g$ the expected cumulative log loss saved in the **first** episode by being told $W$, and by $s$ the information about $W$ revealed at the unscored observations. With $H_t=O_{<t}$,

$$
g=\sum_t I(W;Y_t\mid H_t,X_t),\qquad
s=\sum_t I(W;X_t\mid H_t),\qquad
g+s=I(W;O)=\operatorname{JS}(P,Q).
$$

The first equality is conditional strict propriety, the last two are the chain rule. Conditioning all predictions on the complete future input sequence could change $g$. A common input kernel given the actual prior transcript makes $s=0$. The independent fresh columns in the parity example satisfy this condition.

For independent reset repetitions given $W$, let $N_*$ be the fewest episodes permitting equal-prior error at most $1/4$. If $P\ne Q$, then

$$ \frac{1}{16(g+s)}\ \le\ N_*\ \le\ \left\lceil\frac{2(\log2)^2}{g+s}\right\rceil. \tag{13} $$

If $P=Q$, every sample size gives error $1/2$. To prove the bounds, write $m=(P+Q)/2$ and $z=(P-Q)/(P+Q)$ on its support. Then $g+s=\mathbb E_m[d(z)]$ for $d(z)=\log2-h((1+z)/2)$, whereas $1-\rho=\mathbb E_m[1-\sqrt{1-z^2}]$. The series bounds above and $z^2/2\le1-\sqrt{1-z^2}\le z^2$ give

$$ (g+s)/(2\log2)\ \le\ 1-\rho\ \le\ 2(g+s). $$

An error at most $1/4$ requires $\mathrm{TV}(P^N,Q^N)\ge1/2$. Its square is at most $1-\rho^{2N}\le2N(1-\rho)$. For sufficiency the likelihood-ratio test has error at most $\exp[-N(1-\rho)]/2$. This proves (13), including disjoint supports. This is the classical testing/divergence connection specialized here to separate causal label value from side information. Pensia, Jog and Loh study substantially broader prior/error regimes. We use the elementary equal-prior fixed-error argument above. [Pensia, Jog and Loh, COLT 2024](https://proceedings.mlr.press/v247/pensia24a.html)

The decomposition has consequences for structural learning. If a side channel reveals $W$ at the beginning while both worlds emit identical independent fair labels, one episode identifies the world and $g=0$. Even with $s=0$, a multiclass average predictive gain need not control every hard distinction. Give three equally likely worlds. One emits the distinct symbol 2, the others emit Bernoulli$(1/2\pm e)$ on $\{0,1\}$, $0<e<1/2$. The one-episode information is $h(1/3)+(2/3)d(2e)$, bounded away from zero. The latter pair requires order $e^{-2}$ episodes even to reduce conditional binary error to $3/8$, which is necessary for overall error at most $1/4$. The same affinity argument with $\mathrm{TV}\ge1/4$ gives this lower bound. Thus (13) cannot be transplanted from a binary claim to unrestricted structure identification.

Finally, the *choice* of experiment can change $g$ and $s$. Let $T,W$ be independent fair hidden bits, $E$ independent Bernoulli$(1/4)$, and let the first target be $T$, the second $W$. Before the first target buy exactly one of $A=T\oplus E$ and $B=T\oplus W$. There are no later reads. Buying $A$ minimizes immediate loss at $h(1/4)$ and leaves the second bit fair. Buying $B$ gives immediate loss $\log2$ but learning $T$ then reveals $W$, giving total loss $\log2$ versus $\log2+h(1/4)$ for $A$. A control that prices only today's predictive gain can discard the very observation needed for tomorrow's learning. A horizon, input interface and update are indispensable.
