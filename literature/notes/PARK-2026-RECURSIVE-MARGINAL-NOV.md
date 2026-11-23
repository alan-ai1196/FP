# Recursive Bayesian Compression and False Certainty

## Source, edition and actual coverage

Jonghyun Park, Department of Economics, Virginia Tech. **November 2026 author manuscript, 41 pages.** [Author research page](https://jonghyun-econ.github.io/research/) · [Exact PDF read](https://jonghyun-econ.github.io/assets/pdf/Recursive%20Bayesian%20Compression%20and%20False%20Certainty.pdf). Retrieved November 24, 2026 Shanghai. This is an author working paper; no peer-reviewed publication was established.

The related [SSRN 7274879 record](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7274879), DOI 10.2139/ssrn.7274879, was reported in search metadata as 43 pages, written August 13 and revised August 25, 2026. Its PDF returned 403 and was not read. It is **not equated with this November manuscript**. The current PDF's creation metadata says November 22, but that is not an authenticated publication date; the document itself specifies only the month.

**Fully read by the main assistant:** all 41 pages, title/acknowledgments, §§1–6, Appendix A.1's main proofs, Appendix A.2's auxiliary proofs, every displayed formula, both figures, the unnumbered probability table, all 12 numbered footnotes, title-page notes and 21 references. Reliable layout text was read in continuous blocks; original PDF pp. 8–9, 12–13, 17–18, 22, 26, 34 and 38–39 were visually checked, including both complete figures. No TeX was exposed by the checked author page. Source files are in literature/corpus/pisf_prior_art/SSRN-7274879-author-2026-11/.

The current author webpage and older SSRN abstract also advertise an exact condition under which marginal records reproduce full Bayesian updating. **That separate characterization is absent from the 41-page manuscript read here.** The current paper characterizes attainable certainty under a no-tie condition and gives a binary-network correction test. The webpage wording must not be substituted for a missing body theorem.

**Verification status:** full reading, plus bounded independent recomputation of the manager example and three small reporting networks below. No formal proof, global convergence certification, simulation study or independent reproduction of all theorems. The paper contains analytical examples, not an empirical evaluation.

## Original question and update rule

The question is whether repeated loss of dependence between components can prevent correct learning even when the learner sees every report and knows the correct likelihood. It separates the information in the observed history from the information retained for the next update.

There are finitely many components \(i\in I\), each with a finite value set \(\Theta_i\); all combinations in \(\Theta=\prod_i\Theta_i\) are feasible. At least two components and at least two values per component are assumed. A fixed true state \(\theta^*\) generates conditionally iid reports \(Y_t\) on a finite alphabet. Every likelihood \(P_\theta(y)\) is strictly positive, and distinct states have distinct reporting distributions. Initial component beliefs have full support.

The retained record is \(q=(q_i)_i\). Before each report the learner reconstructs the product distribution

\[
R(q)(\theta)=\prod_iq_i(\theta_i).
\]

She then applies the correct likelihood to that product, obtains an interim joint posterior, and retains only its component marginals. All components are updated simultaneously. The loss of dependence occurs **between observations**; there is no omission of the within-date joint likelihood. The first-step marginals agree with full Bayes initialized at \(R(q_0)\), but subsequent retained marginals generally differ from the full-history posterior marginals.

The effective likelihood for component \(i\), conditional on its candidate value \(a\), is

\[
\widetilde P_i(y\mid a;q_{-i})
=\sum_{\theta_{-i}}P_{(a,\theta_{-i})}(y)
\prod_{j\ne i}q_j(\theta_j).
\]

Consequently its odds obey the exact recursive identity

\[
\frac{q_{i,t}(a)}{q_{i,t}(b)}
=\frac{q_{i,t-1}(a)}{q_{i,t-1}(b)}
\frac{\widetilde P_i(Y_t\mid a;q_{-i,t-1})}
{\widetilde P_i(Y_t\mid b;q_{-i,t-1})}.
\]

The same product weights over other components are used under both hypotheses. A full joint posterior generally supplies different conditional weights.

Define \(K(\theta)=D_{\rm KL}(P_{\theta^*}\Vert P_\theta)\). Identifiability gives \(K(\theta^*)=0<K(\theta)\) for false states. Ordinary finite-model Bayesian learning therefore converges almost surely to the truth from every full-support joint prior. The recursive learner may instead converge to a false corner \(q^{\bar\theta}=(\delta_{\bar\theta_i})_i\).

Footnote 3 gives two arbitrary joint distributions with uniform marginals, masses \((.4,.1,.1,.4)\) and \((.1,.4,.4,.1)\), whose match probabilities are .8 and .2. This illustrates information lost by marginalization. It does not itself prove that both joints are attainable posteriors under one fixed reporting system.

## Which certainty corners are possible?

A weak coordinate-wise KL minimum \(\bar\theta\) satisfies

\[
K(\bar\theta)\le K(a,\bar\theta_{-i})
\quad\text{for every }i,\ a\ne\bar\theta_i.
\]

It is strict when every comparison is strict. This compares single-coordinate changes while fixing all others, not arbitrary changes or mixtures.

**Theorem 1, pp. 12 and 24–25:** from any full-support initial record, almost surely every certainty corner actually reached is a weak coordinate-wise KL minimum. It does not prove that beliefs always converge, that every weak minimum is attainable, or that an attained corner globally minimizes KL.

**Proposition 1, pp. 13 and 25–28:** every strict coordinate minimum is locally attracting. For each \(\varepsilon\in(0,1)\) there is \(\eta>0\) such that every full-support prior satisfying \(q_{i,0}(\bar\theta_i)>1-\eta\) for all \(i\) converges to this corner with probability at least \(1-\varepsilon\). The neighborhood and its probability guarantee are local. The result does not say that every prior is trapped.

**Corollary 1:** when all adjacent KL comparisons at the candidate corner are unequal, the following are equivalent: positive-probability convergence to that corner from some full-support prior; strict coordinate minimality; local attraction. Without the no-tie hypothesis the paper gives the separate necessary and sufficient results above, not this equivalence.

The true state is always a strict minimum under the model's identifiability assumption. False states can also be strict minima. Thus consistency of the full-information statistical model does not imply consistency of this particular update-and-project procedure.

### Proof structure and hypotheses

Strict positivity and finiteness give a uniform lower likelihood bound \(p>0\), bounded log-likelihood increments and continuous effective likelihoods on the closed product of simplices. For

\[
Z^{i,a}_t=\log\frac{q_{i,t}(\bar\theta_i)}{q_{i,t}(a)},
\]

the conditional mean increment \(\Phi_i^a(q_{-i})\) approaches
\(K(a,\bar\theta_{-i})-K(\bar\theta)\) at the candidate corner. The martingale remainder divided by time tends to zero. If this limiting drift is negative, divergence of \(Z^{i,a}_t\) to positive infinity is impossible, proving Theorem 1.

For a strict corner, the minimum of finitely many positive KL gaps is \(g>0\). Continuity supplies a neighborhood where every relevant log-odds drift is at least \(g/2\), regardless of the relative weights on different alternatives. The proof describes that neighborhood using simultaneous log-odds lower bounds \(C\). If \(d=\sum_i(|\Theta_i|-1)\) processes start at least \(r\) above their exit threshold, a stopped exponential-supermartingale argument bounds the probability of any exit by \(d e^{-\gamma r}\). On no exit, the martingale law gives positive asymptotic growth of every required log odds.

Appendix A.2 proves both auxiliary ingredients: a bounded martingale-difference law using exponential tail bounds and summability, and the stopped-process exit bound using a Taylor estimate for \(e^{-\gamma x}\). Independence among the different odds processes is not required. These are full proof coverage statements, not a claim of separate formal certification.

The paper compares Proposition 1 with Loh–Phelan (2019), Theorem 2. Footnote 6 says the earlier condition compares against mixtures of one-coordinate alternatives, while this one compares individual alternatives. Under binary components there is only one alternative, so the stated conditions coincide; with larger component alphabets Park claims a weaker condition. This comparison is **Park's attribution**, not independently verified from the older theorem here. The [publisher record](https://doi.org/10.1111/iere.12406) confirms Isaac Loh and Gregory Phelan, *International Economic Review* 60(4):1861–1876, first online April 16, 2019. A [January 22, 2019 author manuscript](https://web.williams.edu/Economics/wp/LohPhelanDimensionalityDisagreement_Jan2019.pdf) exists; its body and the publisher's separate online appendix remain unread.

## Manager example and independent arithmetic

The two components are requirements \(H/L\) and contractor type \(g/s\). The report is Bernoulli with probabilities

| Probability of report 1 | \(g\) | \(s\) |
|---|---:|---:|
| \(H\) | \(3/5\) | \(1/10\) |
| \(L\) | \(9/10\) | \(1/2\) |

Truth is \((L,s)\). Direct calculation gives

\[
K(L,s)=0,\qquad K(H,g)=\tfrac12\log(25/24),
\qquad K(H,s)=K(L,g)=\tfrac12\log(25/9).
\]

The false state \((H,g)\) is a strict coordinate minimum: correcting either component alone worsens fit; correcting both reaches the truth. At the false corner each wrong-versus-correct component log odds has expected increment \(\frac12\log(8/3)>0\). Full Bayes instead accumulates a truth-versus-false log-odds rate \(\frac12\log(25/24)>0\).

Independent direct Bernoulli KL calculations reproduced \(0.0204109972601\), \(0.510825623766\) and the false-corner drift \(0.490414626506\) nats. Figure 1's square and dashed diagonal represent comparisons of fit, **not trajectories of beliefs**. The paper does not give a measured trap probability for a particular interior prior.

## Binary reporting networks

Section 5 specializes to binary components. A set \(M\) has individual reports with positive finite laws \(\ell_i^0\ne\ell_i^1\). Every graph edge \(\{i,j\}\) has a report about whether the endpoints match, with positive finite laws \(h_{ij}^0\ne h_{ij}^1\). Reports are conditionally independent within and across dates. One learner observes the entire report vector and updates all components.

Each connected component of the graph must contain an individual report. In the binary model this anchors its otherwise ambiguous common flip and ensures identification. Pair reports need not themselves be binary or symmetric. Their KL strengths generally depend on the true state:

\[
k_i^*=D(\ell_i^{\theta_i^*}\Vert\ell_i^{1-\theta_i^*})
\quad(i\in M),\qquad k_i^*=0\quad(i\notin M),
\]

\[
c_{ij}^*=D(h_{ij}^{m_{ij}^*}\Vert h_{ij}^{1-m_{ij}^*}),
\qquad m_{ij}^*=1\{\theta_i^*=\theta_j^*\}.
\]

For an already guaranteed set \(A\), define the evidence balance

\[
B_i^*(A)=k_i^*+
\sum_{j\in N(i)\cap A}c_{ij}^*
-\sum_{j\in N(i)\setminus A}c_{ij}^*.
\]

Start with \(A_0^*=\varnothing\), repeatedly add every outside node with positive balance, and stop at \(A_\infty^*\). Balances only increase as the selected set grows, so sequential qualifying additions give the same closure. The rounds are an **analytical test**, not time phases of the actual learner.

**Theorem 2(i):** each component in \(A_\infty^*\) is learned almost surely from every full-support prior, even if the remaining beliefs do not converge. If the closure is all nodes, complete correction follows.

**Theorem 2(ii):** if the unresolved set \(U^*\) is nonempty and every terminal balance \(B_i^*(A_\infty^*)\) for \(i\in U^*\) is strictly negative, flip exactly those unresolved components relative to truth. The resulting false state is a strict coordinate minimum. Proposition 1 then supplies locally arbitrarily high-probability false certainty.

**Zero terminal balances are not resolved by part (ii).** The correction test becomes a necessity-and-sufficiency statement under the stated strictness condition; an unconditional iff for all reporting systems would overstate it. The theorem is stated at a fixed truth; a guarantee for the whole reporting system requires the corresponding property at every possible truth.

### Why the network bound survives uncertain neighbors

The general Appendix A proposition uses the worst expected true-versus-alternative log-likelihood drift over records where the already learned components are fixed at truth. Denote it \(\Gamma_i^*(A)\). Positive uniform drift makes component \(i\) learn once all components in \(A\) learn. Uniform continuity on a compact domain permits their merely asymptotic, rather than exact finite-time, correctness.

Lemma A.3 proves \(\Gamma_i^*(A)\ge B_i^*(A)\). It first conditions on all reports not involving \(i\). Their likelihood reweights the product prior on other components into generally dependent mixture weights \(\lambda_v(w)\); the proof does not pretend these weights stay independent. Individual evidence and edges to fixed-true neighbors contribute their positive KL strengths exactly.

For the remaining incident edges, the effective true-value likelihood is a mixture of products. Each product differs from the true product only on edges to mistaken neighbors, and its forward KL is at most the sum of those edges' strengths. Convexity of KL in its second argument preserves that bound after mixing. Nonnegativity of the alternative mixture's KL then bounds the true-versus-false expected log ratio below by minus the total unresolved-edge strength. Conditional independence under the truth makes the bound valid after averaging over the other reports.

For a state \(\theta^S\) that flips exactly \(S\), the proof also uses the exact cut identity

\[
K(\theta^S)=\sum_{i\in S}k_i^*+
\sum_{\{i,j\}\in\partial S}c_{ij}^*.
\]

At the all-unresolved-flipped corner, correcting an unresolved component changes loss by \(-B_i^*(A_\infty^*)>0\). Introducing a mistake in an already selected component has a positive balance inherited from its selection round. Thus every one-coordinate move worsens fit.

Footnote 8 explicitly notes that full Bayes can retain accumulated individual and relationship likelihood information instead of storing an entire joint posterior. Accordingly, this paper does **not** establish that faithful Bayesian learning requires an exponentially materialized posterior table.

## More accurate relational evidence can hurt

For a binary symmetric report whose correct label has probability \(r>1/2\), strength is
\(\kappa(r)=(2r-1)\log[r/(1-r)]\), which increases strictly with accuracy.

With two nodes, one individual report of accuracy .9 and one relationship report, accuracy .8 permits correction to propagate. Raising relationship accuracy to .95 instead permits a false strict corner in which both components are wrong together. This concerns a specified bounded learner; it does not contradict the value of information for unrestricted optimal Bayesian decisions.

For the three-node path \(1-2-3\), only node 1 has an individual report. Let its strength be \(a\), and the two edge strengths \(d,b\). Assuming \(a>b>0\), \(d>0\) and \(d\notin\{b,a\}\), Corollary 2 gives complete correction iff \(b<d<a\). Below \(b\), only node 1 is guaranteed; above \(a\), no node is guaranteed. The boundary equalities are explicitly excluded. Figure 2's filled nodes mean guaranteed learning from every full-support prior; unfilled nodes indicate possible persistent mistakes from some priors, not estimated error probabilities.

As a bounded independent check, set individual accuracy .9 and edge-23 accuracy .7. Enumerate all eight states and all eight report vectors using the exact conditional-product model. The directly summed KL losses agreed with the cut identity to at most \(4.5\times10^{-16}\) in floating point:

| Edge-12 accuracy | \(d=\kappa(r)\) | Guaranteed closure | Corner from flipping unresolved nodes | KL at that corner |
|---|---:|---|---|---:|
| .6 | .081093022 | \(\{1\}\) | \(011\), truth \(000\) | .081093022 |
| .8 | .831776617 | \(\{1,2,3\}\) | \(000\) | 0 |
| .95 | 2.649995081 | empty | \(111\) | 1.757779662 |

Here \(a=1.757779662\) and \(b=.338919144\). At false corner \(011\), the three one-bit loss increases are \(1.676686640,\ .257826123,\ .338919144\). At false corner \(111\), they are \(.892215419,\ 2.988914225,\ .338919144\). These concrete examples verify the advertised strict minima and both sides of the intermediate correction interval. They are not a numerical test of every theorem hypothesis or a computation of convergence probabilities.

## Dependencies, limitations and follow-up

The introduction distinguishes repeated posterior compression from ignoring some current signals, selecting a wrong fixed statistical model, coarse initial categorization, social double-counting and full Bayesian updating with misspecification. Berk-type global KL minimization is background contrast; it is not the coordinate-minimum criterion proved for this recursive procedure. The finite correctly specified comparator is attributed to ordinary Bayesian consistency; bounded martingale and drift tools needed for the main results are proved within the appendix.

The two structural limitations matter most. First, the state and report sets are finite, likelihoods strictly positive, observations conditionally iid, and the tested representation exactly the product of component marginals. These results do not automatically cover changing latent states, policy-controlled experiments, general projections, posterior pruning, quantized memory or learned representations. Second, the theorems identify possible certainty corners and sufficient propagation conditions; they do not characterize all interior limit sets, cycles, global basins or finite-time learning rates. Tied cases remain open within the stated network characterization.

The weak-additional-report robustness observation in footnote 11 is local to strict margins: a conditionally independent extra finite positive report with sufficiently small maximal truth-to-state KL does not overturn those strict conclusions. No explicit universal numerical tolerance is supplied.

For later attribution, a narrow check of Loh–Phelan's precise mixture condition would resolve the comparison in footnote 6. This is a historical dependency lead, **not** a new full-reading queue. Cited experimental papers are contextual support, not experiments performed by Park and not independently read here.

No FP theorem or architecture recommendation is inferred. In particular, the manuscript supplies no bound on finite-horizon observable transcript KL after state merging, no uniform guarantee over future probing policies, and no account of acquisition, storage or update costs. Those would require different mathematical objects and additional assumptions. The paper is a concrete recent warning about one explicitly defined recursive projection and a useful source for its asymptotic failure mechanism.
