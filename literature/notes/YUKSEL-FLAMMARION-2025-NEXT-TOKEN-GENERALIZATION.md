# Next-token sample complexity: observed contexts, fresh trajectories and missing proof conditions

## Source and actual coverage

- Oğuz Kaan Yüksel and Nicolas Flammarion, **On the Sample Complexity of Next-Token Prediction**.
- AISTATS 2025, PMLR 258, bibliographic pages 694–702. The official landing page dates publication April 23, 2025. The conference ran May 3–5.
- [Official record](https://proceedings.mlr.press/v258/yuksel25a.html) and [complete official PDF](https://raw.githubusercontent.com/mlresearch/v258/main/assets/yuksel25a/yuksel25a.pdf).
- Edition: the 28-page PMLR PDF, including its appendices. This is a peer-reviewed conference edition, not an authenticated match to an arXiv or OpenReview revision. The OpenReview page identified by the primary sources was blocked during intake. No separate TeX source or supplementary file was authenticated in the inspected PMLR assets.
- Pro-D completed the whole PDF on November 26, 2026, Shanghai. Coverage includes §§1–7, every displayed formula and proof, Appendix A–D, the bibliography, acknowledgments and checklist. There are no research figures or tables. Original PDF pages 5, 6, 19, 23, 26 and 27 were visually inspected by the main reader. Assisting readers separately inspected the attention example and the coupling/independent-block arguments.
- Local ignored source: literature/corpus/pmlr/v258/yuksel25a/paper.pdf. SHA256: 3d140a3d84dd8d98c5ec0068bb6ca6953e87009202e6ab4a7905768278916a4a.

**Status distinction.** Full reading is complete. Independent checking was confined to several material interfaces and elementary claims. It establishes concrete errors in the attention example and entropy example, and a missing probabilistic step in Appendix C. It does not refute all abstract learning bounds, certify all remaining proofs or supply a repaired theorem. No formal verification, training experiment or computational reproduction was performed.

## 1. What problem is actually studied?

The data-generating law is a realizable, finite-order, finite-alphabet autoregressive kernel. There are \(d\) ordinary tokens and a special empty token \(\phi\), embedded as zero. Ordinary tokens use canonical one-hot vectors. A length-\(k\) context is embedded in \(\mathbb R^{kd}\). The model is

\[
p_\theta(\cdot\mid c)=\operatorname{softmax}(f_\theta(E^{\odot k}c)),
\qquad f_\theta:\mathbb R^{kd}\longrightarrow\mathbb R^d.
\]

The true kernel belongs to this class, \(p^\star=p_{\theta^\star}\). The context length and hypothesis class are supplied. The paper does not learn a latent state space, establish parameter identifiability, select the Markov order or discover a representation.

The estimator minimizes the average training cross entropy over \(N\) trajectories of \(T\) tokens,

\[
\widehat L(\theta)=-\frac1{NT}\sum_{n,t}\log p_\theta(X_t^{(n)}\mid C_t^{(n)}),
\qquad
\hat\theta\in\operatorname*{argmin}_{\theta\in\Theta}\widehat L(\theta).
\]

Appendix B actually needs only \(\widehat L(\hat\theta)\le\widehat L(\theta^\star)\). A generic optimization iterate is not automatically covered. No general computational guarantee for finding an ERM in a nonlinear architecture is proved.

**Sampling interface.** The proof uses independent trajectories, particularly when conditioning on one trajectory leaves the other trajectories' loss contributions unchanged in Appendix D. The sampling paragraph on p.4 does not state their independence as explicitly as the proof requires. Correct individual trajectory marginals alone would not justify the sample count \(NT\).

The default initialization on p.4 is a stationary random context. The text allows nonstationary initialization, including deterministic empty padding, except in Theorem 4.2. Appendix D implements deterministic padding. The difference matters for its proof, as discussed below.

## 2. Three losses that must remain distinct

Define the true conditional KL at context \(c\) by

\[
g_\theta(c)=D_{\rm KL}\bigl(p_{\theta^\star}(\cdot\mid c)\Vert p_\theta(\cdot\mid c)\bigr).
\]

Then the two risks in Eqs.(5)–(6) are

\[
\widetilde L(\theta)=\frac1{NT}\sum_{n,t}g_\theta(C_t^{(n)}),
\qquad
L(\theta)=\mathbb E[g_\theta(C)],
\]

where \(C\) is a uniformly selected time-context from an independent fresh trajectory of length \(T\), with the prescribed initialization law.

| Quantity | Context distribution | Meaning |
|---|---|---|
| \(\widehat L\) | Actual training contexts and next tokens | Observed cross entropy, minimized by the estimator |
| \(\widetilde L\) | Actual training contexts | True conditional KL on those contexts, still random through their occurrence |
| \(L\) | Independent fresh trajectory, time averaged over the stated horizon | Out-of-sample true conditional KL under the data-generating process |

The mixing-free \(1/(NT)\) statement concerns \(\widetilde L\), not automatically \(L\). Neither risk is the error under autonomous rollouts of the learned kernel. Neither is a guarantee for arbitrary test contexts, another initialization law or a longer horizon.

## 3. Assumptions and the authors' four bounds

Assumptions 3.1–3.3 require, uniformly over parameters and contexts,

\[
\|f_\theta(c)\|_\infty\le B,\quad B\ge1,
\qquad
\|f_\theta(c)-f_{\theta'}(c)\|_2\le L\|\theta-\theta'\|_p,\quad L\ge1,
\qquad \theta^\star\in\Theta.
\]

The logits are uniformly bounded. Consequently \(0\le g_\theta(c)\le M\), where the paper uses \(M=2B+\log d\). The true probabilities are not permitted to have arbitrary zeros among the ordinary output tokens.

The source defines

\[
C_\epsilon(\Theta)=\log N_\epsilon(\Theta),
\qquad C(\Theta)=\max\{1,C_1(\Theta)\},
\]

and **assumes**

\[
C_\epsilon(\Theta)\le C(\Theta)\log(e/\epsilon),\qquad 0<\epsilon\le1.
\tag{A3.5}
\]

This is a specific normalization, not merely the existence of some dimension-dependent entropy coefficient. The distinction invalidates the claimed automatic applicability to some of the supplied examples.

For compact comparison set \(m=NT\), \(C=C(\Theta)\),
\[
\Lambda=\log(eLm)\log(1/\delta),\qquad 0<\delta<e^{-1}.
\]

The following table reports **source theorem statements**, with their proof qualifications recorded separately.

| Source | Displayed high-probability order | Additional interface |
|---|---|---|
| Theorem 4.1, pp.5 and 18–20 | \(\widetilde L(\hat\theta)=O(BC\Lambda/m)\) | No mixing assumption, but realizability, bounded logits, parameter Lipschitzness, entropy and empirical comparison remain |
| Theorem 4.2, pp.6 and 21–24 | \(L(\hat\theta)=O(\tau_{\rm mix}(B+\log d)C\Lambda\log(em)/m)\) | Stationary initialization and \(T\gg\tau_{\rm mix}\log(eT)\). Appendix C's transfer from independent blocks has a probability gap |
| Theorem 4.4, pp.6 and 25–26 | \(L(\hat\theta)=O(BC\Lambda/m+\widetilde\tau_{\rm mix}(1/T)(B+\log d)\sqrt{C\Lambda/m})\) | Local mixing between contexts that differ only in their last token. Initialization and indexing qualifications remain |
| Theorem 4.6, pp.7 and 26–28 | \(L(\hat\theta)=O(BC\Lambda/m+k\eta(T)(B+\log d)\sqrt{C\Lambda/m})\) | Uniform path-coupling condition, with the proof directly supporting fixed initialization |

Here \(\widetilde\tau_{\rm mix}(1/T)\) means the local mixing-time function **evaluated at accuracy \(1/T\)**. It is not \(\widetilde\tau_{\rm mix}/T\). In the last two rows both logarithms in \(\Lambda\) are inside the square root of the second term.

The global mixing time compares laws of future length-\(k\) blocks from arbitrary initial contexts. The local version takes the supremum only over pairs agreeing in their first \(k-1\) tokens. The convention is \(\tau_{\rm mix}=\tau_{\rm mix}(e^{-1})\). Slow global mixing and a shorter local influence time are distinct conditions.

## 4. The useful statistical mechanism

### 4.1 Observed-context fast rate

The Appendix B argument begins with the empirical comparison to \(\theta^\star\). A softmax Bregman identity expresses excess empirical loss as true contextwise KL plus a centered score term. With the paper's sign choice,

\[
\widetilde L(\hat\theta)\le\widehat Z(\hat\theta).
\]

For a fixed parameter, \(NT\widehat Z\) is a bounded martingale sum. Its predictable quadratic variation is \(NT\widehat V\), the average quadratic form of the logit difference against the true softmax Hessian. The identity follows because that Hessian equals the covariance of the one-token score at the true kernel.

Generalized self-concordance supplies

\[
\widetilde L(\theta)\ge\frac5{36B}\widehat V(\theta).
\]

The proof therefore controls an event where the martingale is unusually large relative to both its own variation and a positive threshold. Freedman, peeling, a parameter net and Lipschitz extension produce the fast observed-context rate. Temporal independence of consecutive contexts is unnecessary for this martingale mechanism.

This is a useful distinction: prediction error on visited contexts can be small even when those contexts do not explore the test distribution. The paper's metastable-chain illustration on p.6 explains the latter obstruction qualitatively. It is not presented here as a complete minimax lower-bound proof.

**Printed-proof caution.** Proposition B.1 defines its good event using \(E_\theta\), while its proof and Eq.(23) require the complement of \(E_\theta\). The peeling substitution on p.19 also omits the factor \(\gamma\) when setting a deterministic upper bound on \(\gamma NT\widehat Z\). One can bound that quantity by \(4\gamma BNT\), but the printed \(4BNT\) is not the stated implication for arbitrary \(\gamma\). These issues should not be silently copied into a proof. This note records the statistical mechanism without certifying every displayed constant or claiming a completed repair of Theorem 4.1.

### 4.2 Out-of-sample conversion needs an additional argument

To pass from \(\widetilde L\) to \(L\), the paper uses two different routes.

1. Appendix C makes a star-shaped extension of the KL loss class and applies localization to nominally independent blocks. This is intended to retain a fast rate under global mixing.
2. Appendix D directly bounds the Doob increments of \(L(\theta)-\widetilde L(\theta)\). A change in one revealed token affects conditional expected future losses. A path coupling controls the number of affected contexts. Azuma and a parameter net give the slower square-root term.

The first route has a missing probability transfer. The second retains a meaningful conditional argument after its initialization and elementary indexing conventions are made explicit.

## 5. Independent finding: the attention Lipschitz constant fails

### 5.1 Exact model and dimension issue

On p.5 the attention example writes

\[
a_j=\frac1{\sqrt{k}}\sum_{i=1}^k\langle Q\mu_i,K\mu_j\rangle,
\qquad
f_{Q,K,V}(\mu)=V\sum_{j=1}^k\operatorname{softmax}(a)_j\mu_j.
\]

The first display actually indexes \(a\) by \(j=1,\ldots,d\), and assigns \(g_{Q,K}\) output dimension \(d\), although the output consumes \(k\) weights and only \(k\) input blocks are defined. For general \(k\ne d\), the natural position-attention interpretation requires \(j\le k\) and \(g_{Q,K}:\mathbb R^{kd}\to\mathbb R^k\). That is an explicit correction of the printed model, not a silent substitution.

For operator-norm radii \(B_Q,B_K,B_V\), the source claims
\[
L=B_V(B_Q+B_K)
\]
under the maximum of the three operator-norm parameter distances.

### 5.2 A finite counterexample within the printed dimensions

Take \(k=d=64\), all three radii equal to one, and an input containing 32 copies of \(e_1\) and 32 copies of \(e_2\). Define
\[
r=(e_1+e_2)/\sqrt2,\quad s=(e_1-e_2)/\sqrt2,
\quad Q_\theta=\theta sr^\top,\quad K=V=I.
\]
All parameter constraints hold. A direct calculation gives
\[
f_\theta=\operatorname{sigmoid}(8\theta)e_1+
\bigl(1-\operatorname{sigmoid}(8\theta)\bigr)e_2.
\]
Between \(\theta=0\) and \(1/8\), the parameter distance is \(1/8\), whereas
\[
\|f_{1/8}-f_0\|_2
=\sqrt2\left(\frac e{1+e}-\frac12\right)
=0.3267661756\ldots
>2/8.
\]
Thus the printed \(L=2\) is false. Taking \(d=k\) avoids dependence on the dimension correction above.

For the position-attention interpretation and arbitrary even \(k\), the same construction gives derivative norm \(\sqrt{k}/(2\sqrt2)\) at zero. A context-independent parameter Lipschitz constant is impossible for the displayed \(1/\sqrt{k}\) normalization of the summed queries.

There is also a missing contribution from varying \(V\). With one token and \(k=d=1\), the output is simply \(V\), so the constant must be at least one regardless of \(Q,K\).

### 5.3 A valid local replacement bound

This is a note-level derivation, not a theorem claimed by the authors. For one-hot or zero input blocks, put
\[
u=k^{-1/2}\sum_i\mu_i,\quad a_j=\langle Qu,K\mu_j\rangle,
\quad m=\sum_j\operatorname{softmax}(a)_j\mu_j.
\]
If the maximum parameter distance is \(\Delta\), then
\[
\|u\|_2\le\sqrt{k},\quad
\|a-a'\|_\infty\le\sqrt{k}(B_Q+B_K)\Delta,\quad \|m\|_2\le1.
\]
The softmax map satisfies
\[
\|\operatorname{softmax}(a)-\operatorname{softmax}(a')\|_1
\le\|a-a'\|_\infty.
\]
Indeed its directional derivative has norm
\(\mathbb E_p|h-\mathbb E_p h|\le\sqrt{\operatorname{Var}_p(h)}\le\|h\|_\infty\).
Integrating along the line segment proves the inequality. It follows that
\[
\boxed{\|f-f'\|_2
\le\bigl[1+B_V\sqrt{k}(B_Q+B_K)\bigr]\Delta.}
\]

The parameter-count contribution to the covering entropy can remain independent of \(k\). The logarithm of \(L\) in the statistical bound then introduces a logarithmic context-length contribution. This is still substantially smaller than the exponential table size of an arbitrary \(k\)-gram kernel, but it is not the constant printed in the example.

The suggestion that positional encodings can be added unchanged also needs an input-norm bound. If each resulting block has norm at most \(R\), the same derivation gives \(B\le B_VR\) and \(L\le R+B_VR^3\sqrt{k}(B_Q+B_K)\). No size control on positional encodings is specified in the example.

## 6. Independent finding: the entropy normalization does not cover the example

Consider the product of three unit operator-norm balls with the maximum metric. A single radius-one ball centered at the zero triple covers the parameter space, so
\[
N_1(\Theta)=1,\quad C_1(\Theta)=0,\quad C(\Theta)=1.
\]
Keeping \(Q=K=0\) and varying \(V\) leaves a \(d^2\)-dimensional norm ball. Volume comparison implies
\[
\log N_\epsilon(\Theta)\ge d^2\log(1/\epsilon).
\]
For \(d=2,\epsilon=1/4\), this is at least \(4\log4\), strictly exceeding the purported A3.5 upper bound \(\log(4e)\).

Consequently this allowed parameter example does not satisfy A3.5 as it is actually defined. A statement of the form \(O(d^2\log(1/\epsilon))\) cannot justify substituting \(C(\Theta)=\max\{1,C_1(\Theta)\}\).

A valid entropy estimate is
\[
\log N_\epsilon(\Theta)
\le d^2\sum_{A\in\{Q,K,V\}}\log(1+2B_A/\epsilon)
\le A_0\log(e/\epsilon),
\]
where, for example,
\[
A_0=3d^2\max\{1,\log(1+2\max_A B_A)\}.
\]
Using this coefficient would require explicitly restating the assumption and tracking \(A_0\) through the argument. The note does not identify it with the source's already-defined \(C(\Theta)\), nor certify a complete revised theorem.

## 7. Independent finding: Appendix C drops the coupling failure probability

This is a defect in a proof step, not a counterexample to the conclusion of Theorem 4.2.

On p.22 the proof selects
\[
\xi=\frac{\tau_{\rm mix}C(\Theta)}{NT},\quad
Q=\tau_{\rm mix}(\xi),\quad I=\lfloor T/Q\rfloor.
\]
On p.23 Eq.(27), it compares a dependent-block supremum \(\widetilde S\) to an independent-block version \(\overline S\) and asserts the deterministic inequality
\[
\widetilde S\le\overline S+
\frac{QM}{NT}\frac{N(I-1)}2\xi
\le\overline S+\frac M2\xi.
\tag{27, source}
\]
The justification says each block disagrees only on \(\xi\) probability mass and each loss is bounded. This yields an expected discrepancy, not the stated samplewise bound.

The elementary example \(X\sim\operatorname{Bernoulli}(\xi)\), \(Y=0\), \(0<\xi<1\), has TV distance \(\xi\) but \(|X-Y|=1>\xi\) on an event of probability \(\xi\). It refutes the generic TV-to-deterministic-deviation inference only.

With a suitable sequential block coupling and \(K\) coupled blocks, the legitimate alternatives have the forms
\[
\Pr(\widetilde S>a)\le\Pr(\overline S>a)+K\xi,
\]
or, from an expected discrepancy bound,
\[
\Pr(\widetilde S>a+b)
\le\Pr(\overline S>a)+\frac{M\xi}{2b}.
\]
The proof's block count allows \(K\le N(I-1)/2\). Neither additional probability term appears in the transfer on p.24.

Its chosen \(\xi\) does not depend on \(\delta\), and
\[
\frac{N(I-1)}2\xi
=\frac{\tau_{\rm mix}C(\Theta)(I-1)}{2T}
\]
is not controlled by \(\delta/2\). Increasing the loss threshold \(\alpha\) to absorb \(8M\xi\) does not itself bound the probability that any block mismatches.

A repair must revisit coupling failure, block length and confidence jointly. It is not justified to assert that the identical printed high-probability bound follows unchanged. Appendix C also has normalization and sign slips, including the reversed tail inequality in Eq.(28). Correcting that sign alone does not fix Eq.(27). No replacement theorem is proved here.

## 8. What the coupling assumption does support

Assumption 4.5 compares any two contexts agreeing in their first \(k-1\) tokens. It requires a joint coupling of their full true continuations for which the expected cumulative token Hamming discrepancy is at most \(\eta(T)\).

The original display inconsistently writes continuation marginals \(k+1:T\) while evaluating variables through \(T+k\). Appendix D makes the intended \(T\)-token continuation clear. The sum starts at index \(k\), so it includes the differing last initial token. Therefore \(\eta(T)\ge1\) whenever such a distinct context pair exists.

The condition is uniform over all these pairs, including empty-padded contexts. It is stronger than an informal similarity claim about typical sentences. The joint coupling need not be online, co-adapted or computationally realizable. Its role is to compare conditional expected future losses.

For independent trajectories with fixed initialization, reveal tokens sequentially. Changing one revealed token induces a neighboring-context pair. Each changed future token can affect at most \(k\) subsequent contexts, so
\[
\mathbb E_\gamma\sum_i\mathbf1\{C_i^x\ne C_i^y\}\le k\eta(T).
\]
Since each context loss lies in \([0,M]\), the oscillation of the conditional expected total average loss is at most
\[
\frac{Mk\eta(T)}{NT}.
\]
The Doob increment is bounded by this same oscillation in absolute value. Azuma and the entropy net then give the square-root generalization term.

This argument uses an expected Hamming bound. The source's wording that there are “at most” \(k\eta(T)\) differing indices should not be read as a deterministic pathwise statement. Its printed increment changes sign between Eqs.(35) and (37), and the position index should be \(1+((m-1)\bmod T)\). Using absolute oscillations removes the sign ambiguity. These are local corrections, unlike the missing probability term in Appendix C.

### Initialization is an additional random object

With fixed empty padding, Eq.(35) telescopes from the expected loss under that fixed initialization to the observed loss. With random initial contexts \(J_1,\ldots,J_N\), the filtration as printed does not reveal them.

If they are added to \(\mathcal F_0\), the starting quantity is
\[
\mathbb E[\widetilde L(\theta)\mid J_1,\ldots,J_N],
\]
not \(L(\theta)\) averaged over an independent fresh initialization. A further term
\[
L(\theta)-\mathbb E[\widetilde L(\theta)\mid J_1,\ldots,J_N]
\]
must be handled, or the target must explicitly be conditional on the observed initializations. The paper's p.8 discussion mentions seen-initialization guarantees as a direction, but the given D.2 proof does not supply this missing general argument.

Thus the checked coupling mechanism is usable for independent trajectories, deterministic initialization and a matching fresh-trajectory target. Arbitrary random initialization is not certified by the inspected proof.

Even there, “without mixing” means replacing mixing by a uniform influence assumption. For convergence, the actual scaling requirement includes
\[
k\eta(T)(B+\log d)\sqrt{\frac{C(\Theta)\log(eLNT)\log(1/\delta)}{NT}}\longrightarrow0.
\]
If \(\eta(T)\) is linear in \(T\), the displayed bound can be vacuous. Growing \(k\), \(B\) and model complexity cannot be ignored.

## 9. Boundaries for reuse

The strongest reusable distinctions are between visited-context prediction and fresh-trajectory prediction, between an entropy coefficient and entropy at one arbitrary radius, and between expected coupling error and a high-probability transfer.

The source does not establish a general model-identification theorem, an SGD learning-dynamics result, a compression theorem for a learned state, a finite-bit memory bound or a guarantee of length extrapolation. Its architecture examples do not independently prove that realistic language-model training satisfies realizability, global parameter bounds or the coupling assumption.

The accompanying attention and entropy counterexamples are exact local deductions. The missing Eq.(27) probability term and random-initialization term are proof-coverage findings. These should not be collapsed into either “the paper is verified” or “all of its theorems are false.”

No FP transfer is proposed. The paper concerns a supplied finite-context model and a global empirical comparison. Mapping that framework to endogenous predictive-state formation would require additional objects and assumptions that this reading does not provide.
