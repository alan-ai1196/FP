# What capable agents must know: diagnostic regret and predictive state

## Source, edition and actual reading

- **Author:** Aran Nayebi, Carnegie Mellon University.
- **Completed edition:** [UAI 2026 official proceedings](https://proceedings.mlr.press/v337/nayebi26a.html), PMLR 337:4773–4795, published August 17, 2026. [Official 23-page PDF](https://raw.githubusercontent.com/mlresearch/v337/main/assets/nayebi26a/nayebi26a.pdf). This is an authenticated conference publication.
- **Full reading by Pro-C, November 26, 2026, Shanghai:** all 23 physical pages, main §§1–7, Appendices A–J including C.1–C.2 and J.1–J.2, all proofs, formulas, the sole Figure 1, acknowledgements and the complete printed reference list. The complete 1,568-line PDF extraction was read in four contiguous blocks. Original physical PDF pp. 2, 4, 7–9, 14–15, 18–20 and 23 were also visually inspected. Figure 1 is a conceptual summary. There are no tables or empirical experiments.
- **Version comparison, not a second full reading:** [arXiv:2603.02491v3](https://arxiv.org/abs/2603.02491v3), June 28, 2026, also 23 pages. A source assistant compared both complete PDF extractions. Removing only the observed arXiv watermark, proceedings footer, isolated official page numbers and whitespace yields identical 55,572-character text, without Unicode folding. The PDF files are distinct. This establishes extracted-text identity under those transformations, not visual identity or scientific verification. The v3 TeX source was used for source inventory and selected formula checks, not claimed read completely. It has 58 active citation keys, one figure, no tables and no active body footnotes. No independently authenticated official-final TeX was obtained.
- **Verification boundary:** bounded manual checks of the diagnostic interface, the threshold-elicitation inequality, the no-aliasing inequality and two finite-POMDP coverage counterexamples. Assisting readers independently checked the relevant theorem interfaces and the counterexamples. This is neither a certification of every imported result nor formal verification. No experimental reproduction, exhaustive search or proof script was performed. No AI assistance disclosure was located in the read edition.
- **Ignored source cache:** literature/corpus/pro_c/nayebi26a/, with the separately identified arxiv-v3/ source and version-comparison metadata. No FP core files were edited.

**Main finding:** low regret on the paper's specified diagnostic tasks does constrain predictive distinctions. Threshold lotteries elicit predictive probabilities in an average squared-error norm, and opposite-margin history pairs yield a valid weighted memory-aliasing lower bound. Two stronger conclusions require missing coverage qualifications. Theorem 4's operator-recovery proof evaluates designated anchor histories not required to be covered in its statement. Corollary 5 converts agreement on sampled history pairs into a function on the marginal history support without sufficient pair coverage. Explicit finite POMDPs below separate these gaps from the valid elicitation and aliasing results.

## 1. The competence assumption is an evaluation interface

The normalized regret is

\[
\delta=1-\frac{V^\pi}{V^\star}.
\]

For complementary binary payoffs \(p,1-p\), put \(m=|p-1/2|\) and let \(w\) be the probability of choosing the worse alternative. Lemma 1 gives

\[
\delta=w\,\frac{4m}{1+2m}.
\]

Thus a margin \(m\geq\gamma\) makes a wrong report cost at least

\[
c(\gamma)=\frac{4\gamma}{1+2\gamma}.
\]

The paper applies this elementary decision-loss identity to deliberately constructed goal families. Competence means small regret under specified distributions over goals and histories. It does not mean good ordinary-language performance, success on one fixed reward function, or optimality under an unspecified task distribution.

The agent is queried separately with different goals. Its complete response probability is available to the displayed extraction algorithms. A theorem that recovers a quantity from this response function does not establish that an explicit array containing that quantity occurs inside the agent.

## 2. Fully observed transition recovery

### The repeated-visit experiment

Section 4 and Theorem 1 assume a finite, stationary, fully observed controlled Markov process with at least two actions, communication between states and some action influence on transitions. A goal first uses an actual environment action as an \(L/R\) marker. It then concerns \(n\) completed occurrences of a designated state-action pair \((s,a)\), at times at least one, and the number of those occurrences followed by \(s'\).

Under a policy that completes the visits, the transition count has the binomial law

\[
X\sim\operatorname{Bin}(n,P_{ss'}(a)).
\]

The two branches reward \(X\leq k\) or \(X>k\). Communication allows an appropriate policy to complete the required visits almost surely even after the marker action changes the state. The goal has no finite deadline or waiting cost. Here \(n\) counts designated trials, not all environment steps. No bound on return times is proved.

An arbitrary policy can choose whether to continue visiting based on previous outcomes. Its count law conditional on completion need not remain binomial. Appendix B avoids this mistake: it upper-bounds that policy's branch success by the optimal success attainable within the branch. This suffices for a regret lower bound on choosing the wrong branch.

### What the extractor obtains

Let \(q_{s,a,s',k}\) be the probability that the policy selects the \(L\) marker at the fixed initial state for the corresponding goal. Equation (8) is

\[
\widehat P_{ss'}(a)
=\operatorname{clip}_{[0,1]}
\left[
\frac1n\left(\sum_{k=0}^{n}(1-q_{s,a,s',k})-\frac12\right)
\right].
\]

The \(-1/2\) is **inside** multiplication by \(1/n\). The official PDF confirms the parentheses. A text-extraction ambiguity here is not a paper error.

For goals uniform over \(S\times A\times S\times\{0,\ldots,n\}\), Theorem 1 bounds the mean entrywise absolute recovery error by

\[
2t_\gamma\,\mathbb E_{s,a,s'}
\sqrt{\frac{P_{ss'}(a)(1-P_{ss'}(a))}{n}}
+\frac{\bar\delta}{c(\gamma)}
+O_\gamma(n^{-1}),
\qquad
t_\gamma=\sqrt{\frac{1+2\gamma}{1-2\gamma}}.
\]

The proof converts soft branch choices to an approximate binomial median. A one-sided variance inequality bounds the number of thresholds too close to a fair bet, and the binomial median lies within one of \(np\). The low-margin part is deliberately uncontrolled by regret.

For the displayed procedure, recovering the whole matrix reads \((n+1)|S|^2|A|\) goal-conditioned action probabilities. This is an interface count, not a lower bound. The theorem does not price estimating those probabilities by sampling, resetting to the initial state, representing the goals, visiting rare states, training the policy, or storing the recovered matrix. The guarantee is an average entry error, not a uniform row-total-variation or trajectory guarantee.

### Causal qualifications

Corollary 1 adds an assumed discrepancy \(\varepsilon_{\mathrm{cMP}}\) between the controlled transition kernel and the desired intervention kernel. Transition recovery therefore yields intervention recovery only with that additional causal interface assumption.

Corollary 2 correctly separates intervention marginals from joint cross-action counterfactuals. For a fair latent bit \(U\), the structural laws \(S'=U\) and \(S'=A\oplus U\) have the same one-action intervention marginals but different coupling of counterfactual outcomes across actions. The controlled kernel alone cannot determine that coupling.

## 3. Partial observation: fair bets and threshold lotteries differ

Section 5 uses a finite POMDP and histories \(h=(o_0,a_0,\ldots,o_t)\). A test \(T=(\alpha,W)\) specifies a finite future action sequence \(\alpha\) and an event \(W\) in future observations. Its probability \(p_T(h)\) concerns execution of that prescribed action sequence.

The report bit is now a **separate non-dynamical output**. After the agent reports \(L\) or \(R\), the evaluator executes \(\alpha\). The report does not choose the environment's action sequence. These are intervention-style tests, not arbitrary observational conditioning on actions selected by an adaptive policy.

The history distribution \(\mathcal H\) and test distribution \(D\) are supplied. They need not coincide with a deployment occupancy distribution. A shared internal representation is a deterministic, goal-independent statistic \(M=f(h)\), through which every tested report policy factors. Report policies may randomize. This is not a theorem about arbitrary randomized internal-memory channels.

Theorem 2 applies the margin identity to bound the average wrong-report mass on \(|p_T(h)-1/2|\geq\gamma\) by \(\bar\delta/c(\gamma)\). A conditional version divides by the mass of this margin event. This only recovers the decision side on covered, well-separated tests.

Proposition 1 gives a useful exact separation. Four latent states produce an initially aliased observation, then an all-zero future with probability \(r\) and an all-one future with probability \(1-r\). For any finite future event, the probability is one of

\[
0,\quad 1-r,\quad r,\quad 1.
\]

Every \(r\in(1/2,1)\) induces the same unique optimal fair-bet reports for every test, although the predictive probabilities differ. Exact optimal fair-bet access therefore does not generically identify the predictive state.

### The valid threshold-elicitation theorem

Theorem 3 instead compares \(p_T(h)\) with an independent lottery of probability

\[
\lambda_k=\frac{k-1/2}{K},\qquad k=1,\ldots,K.
\]

With \(q_{T,\lambda_k}(h)\) the probability of choosing the test over the lottery, define

\[
\widehat p_T(h)=\frac1K\sum_{k=1}^K q_{T,\lambda_k}(h),
\qquad
\varepsilon_K=2\bar\delta_K+\frac1{4K^2}.
\]

Under average normalized threshold regret at most \(\bar\delta_K\),

\[
\mathbb E_{\mathcal H,D}
\bigl(\widehat p_T(h)-p_T(h)\bigr)^2
\leq\varepsilon_K.
\]

For a uniform finite test family of size \(d\), this is the normalized vector bound
\(\mathbb E_{\mathcal H}\|\widehat\eta(h)-\eta(h)\|_2^2/d\leq\varepsilon_K\).

Appendix F supplies a pointwise proof. Writing \(p=p_T(h)\), the average unnormalized regret \(R\) equals

\[
\frac1K\sum_{k\leq J}(p-\lambda_k)
-p\widehat p+\frac1K\sum_k\lambda_kq_k,
\qquad J=\lfloor Kp+1/2\rfloor.
\]

The first term is at least \(p^2/2-1/(8K^2)\). For fixed average \(\widehat p\), placing the mass \(q_k\) on the smallest thresholds minimizes the last term, which is at least \(\widehat p^2/2\). Hence

\[
(\widehat p-p)^2\leq 2R+\frac1{4K^2}
\leq\frac2K\sum_k\delta_{T,\lambda_k}(h)+\frac1{4K^2}.
\]

The bounded check found no gap in this argument. It requires the threshold task family and full policy response probabilities. At fixed \(K\), vanishing regret still leaves quantization error. Exact recovery in the stated bound also requires \(K\to\infty\). No update rule for the recovered coordinates follows from Theorem 3 alone.

## 4. Theorem 4 needs anchor-history coverage

The linear-PSR setup assumes given core tests \(T_1,\ldots,T_d\) and operators satisfying

\[
s_\sigma(h)=B_\sigma s(h),
\qquad \sigma=(a,o),
\]

where \(s_\sigma\) consists of the prepended tests \(\sigma\circ T_i\). Choose histories \(h^1,\ldots,h^d\) so that

\[
S=[s(h^1)\ \cdots\ s(h^d)]
\]

is invertible, and write \(Y_\sigma=B_\sigma S\). The proposed estimator is
\(\widehat B_\sigma=\widehat Y_\sigma\widehat S^{-1}\).

Theorem 4 states an aggregate bound

\[
\|\widehat S-S\|_F^2+
\sum_\sigma\|\widehat Y_\sigma-Y_\sigma\|_F^2
\leq d^2(1+|A||O|)\varepsilon_K.
\tag{24}
\]

It then obtains invertibility and a perturbation bound if

\[
d\sqrt{(1+|A||O|)\varepsilon_K}
\leq\frac1{2\|S^{-1}\|_2}.
\tag{25}
\]

**The coverage gap:** the main statement invokes Theorem 3's average-regret bound for the indicated test family without requiring its history distribution to be uniform on the selected anchors. Appendix G begins by making exactly that change. It also takes a uniform indexed test collection, counting each \((\sigma,i)\) separately. An average guarantee under the original history distribution does not justify evaluating different anchor histories. The indexed-test averaging must also be covered by the regret assumption, whether directly or through a per-test guarantee.

### A one-state finite-POMDP counterexample to the unqualified statement

Use one latent state, two actions with identical transitions, and independent observations
\(\Pr(0)=3/5,\Pr(1)=2/5\). Let the single core test be observing zero after a fixed action. Then

\[
d=1,\quad s(h)=3/5,\quad
B_{(a,0)}=3/5,\quad B_{(a,1)}=2/5
\]

for every history and either action. The prepended-test probabilities are \(9/25\) and \(6/25\).

Evaluate only at history \(h=(0)\), so \(\mathcal H=\delta_{(0)}\), but select the reachable anchor \(h^1=(0,a,0)\). Let the policy be optimal on all threshold bets at \((0)\) and always report \(R\) at the anchor. Use the uniform indexed five-test family. Then \(\bar\delta_K=0\), even separately for each test under \(\mathcal H\).

Take \(K=4\), giving \(\varepsilon_K=1/64\). The true scalar matrix is \(S=3/5\), while \(\widehat S=0\), as are all \(\widehat Y_\sigma\). Equation (24) would require

\[
\underbrace{\frac9{25}
+2\left[\left(\frac9{25}\right)^2+
\left(\frac6{25}\right)^2\right]}_{459/625}
\leq\frac5{64},
\]

which is false. Even the displayed small-error condition (25) holds:

\[
\frac{\sqrt5}{8}<\frac3{10}
=\frac1{2\|S^{-1}\|_2},
\]

yet \(\widehat S\) is singular. If the earlier fair-bet nondegeneracy condition is retained, \(\gamma=1/10\) works: the core probability \(3/5\) is on the high side and the prepended probabilities are on the low side, each with positive test mass.

This example changes no linear-algebra assumption. It isolates the unchecked change in evaluation distribution.

### What survives

With Appendix G's actual uniform anchor and indexed-test evaluation assumption, its entrywise sum gives (24). The Neumann-series argument then yields

\[
\|\widehat S^{-1}\|_2\leq2\kappa,\qquad
\|\widehat S^{-1}-S^{-1}\|_2
\leq2\kappa^2\|\widehat S-S\|_F,
\quad \kappa=\|S^{-1}\|_2,
\]

and the stated operator error follows with

\[
C(S,Y)=8d^2(1+|A||O|)
\left(\kappa^2+\kappa^4\sum_\sigma\|Y_\sigma\|_2^2\right).
\]

This matrix perturbation calculation is supported. A corrected theorem must explicitly assume the relevant anchor/test regret coverage, or add a justified change-of-measure factor. It still presupposes a finite linear PSR, core tests and a sufficiently conditioned invertible anchor matrix. It does not discover them from ordinary competence.

## 5. The valid memory-necessity statement is pair weighted

Section 5.3 chooses a distribution \(\mathcal P\) on pairs \((h,h')\) with the same last observation. A directed witness set \(S_\gamma(h,h')\) contains only tests for which

\[
p_T(h)\geq1/2+\gamma,\qquad
p_T(h')\leq1/2-\gamma.
\]

The relevant collision mass is

\[
q_\gamma^{\mathrm{Alias}}(M)
=\mathbb E_{\mathcal P}
\left[
\mathbf1\{M(h)=M(h')\}
D(S_\gamma(h,h'))
\right].
\]

Pair regret averages the two histories' test regrets with equal weight. Theorem 5 proves

\[
\bar\delta_{\mathcal P}(\pi)
\geq\frac{c(\gamma)}2q_\gamma^{\mathrm{Alias}}(M)
\]

for an \(M\)-based policy. On an aliased witness pair, the two reports have the same probability \(q_T\). Their wrong-report masses are \(1-q_T\) and \(q_T\), whose average is \(1/2\). Applying the margin bound and integrating proves the result.

This is a useful necessary distinction theorem. It controls collisions weighted by the chosen pair distribution and witness-test mass. It does not force separation of all histories or all unequal predictive probabilities. It also does not quantify a number of memory states or bits without further packing and coverage information. There is no learned or recursively computable memory construction.

The history marginal governing this pair regret is \((\mathcal P_1+\mathcal P_2)/2\). It need not equal the \(\mathcal H\) used earlier.

### Structured-task corollaries have a narrower mathematical content than Figure 1

Corollary 3 partitions the test distribution into blocks of masses \(p_i>0\). Nonnegative regret gives
\(\bar\delta_{\mathcal P,i}\leq\bar\delta_{\mathcal P}/p_i\), so

\[
q_{\gamma,i}^{\mathrm{Alias}}(M)
\leq\frac{2\bar\delta_{\mathcal P}}{p_i c(\gamma)}.
\]

This prevents sufficiently harmful collisions within each covered block. It does not force separate neural modules, independent coordinates or a particular computational graph. An invertible recoding can mix coordinates while preserving every report.

Corollary 4 restricts witnesses to pairs carrying different regime labels. Its inequality is Theorem 5 applied to that witnessed event. It supports regime discrimination where the evaluation demands opposite reports. It does not construct a persistent regime variable, prove a temporal update law, or imply global affective modulation. The discussion's neuroscience and cognitive-architecture interpretations are proposals beyond these inequalities.

## 6. Corollary 5 does not follow from pairwise coverage alone

The paper defines the \(\gamma\)-coarsened profile \(\ell(h)\) with one coordinate per test:

\[
\ell_T(h)=
\begin{cases}
L,&p_T(h)\geq1/2+\gamma,\\
R,&p_T(h)\leq1/2-\gamma,\\
\bot,&\text{otherwise}.
\end{cases}
\]

Its \(\gamma\)-minimality assumption means

\[
\ell(h)=\ell(h')\Longrightarrow M_j(h)=M_j(h').
\]

Thus the memory does not further split a profile class, but this condition alone permits merging different profiles.

For two fixed memories with vanishing-regret policy sequences, the stated completeness condition requires, only for \(\mathcal P\)-almost every pair,

\[
\ell(h)\ne\ell(h')
\Longrightarrow D(S_\gamma(h,h'))>0.
\]

Corollary 5 concludes that the memories induce the profile partition on the evaluation support and admit measurable mutual recodings. The first part of Appendix J.2 is valid: minimality gives \(M_j=a_j(\ell)\). Theorem 5 and completeness also yield

\[
M_j(h)=M_j(h')\Longrightarrow\ell(h)=\ell(h')
\qquad\mathcal P\text{-almost everywhere}.
\]

The proof then defines \(\ell(h)=b_j(M_j(h))\) almost surely under the history distribution. This is the unsupported step. Pairs absent from \(\mathcal P\) can still contain positive-marginal-mass histories that collide in memory.

### Finite counterexample with nonzero witness mass

Take one test \(T\), \(\gamma=1/5\), and three histories with the same last observation:

| History | \(p_T(h)\) | \(\ell(h)\) | \(M_1(h)\) | \(M_2(h)\) | Optimal report |
|---|---:|---|---|---|---|
| \(h_1\) | \(9/10\) | \(L\) | \(A\) | \(L\) | \(L\) |
| \(h_2\) | \(3/5\) | \(\bot\) | \(A\) | \(\bot\) | \(L\) |
| \(h_3\) | \(1/10\) | \(R\) | \(B\) | \(R\) | \(R\) |

Let

\[
\mathcal P=\tfrac12\delta_{(h_1,h_3)}
+\tfrac12\delta_{(h_2,h_2)},\qquad D(T)=1.
\]

On \((h_1,h_3)\), choose \(S_\gamma=\{T\}\). On \((h_2,h_2)\), choose the empty witness set. Completeness holds on the support of \(\mathcal P\), and witness mass is \(1/2\).

Both memories satisfy minimality. They can be defined globally as \(M_2=\ell\) and \(M_1=g(\ell)\), with \(g(L)=g(\bot)=A,\ g(R)=B\). The first memory reports \(L\) at \(A\) and \(R\) at \(B\). The second reports \(L\) at \(L,\bot\) and \(R\) at \(R\). Both have **exactly zero pair regret**, so constant policy sequences meet the vanishing-regret convention.

The induced history marginal is

\[
\mu=\tfrac14\delta_{h_1}
+\tfrac12\delta_{h_2}
+\tfrac14\delta_{h_3}.
\]

Both high-margin sides have positive mass. But no function \(\psi\) can satisfy \(M_2=\psi(M_1)\) \(\mu\)-almost surely, because \(M_1(h_1)=M_1(h_2)=A\) while \(M_2(h_1)\ne M_2(h_2)\), and both histories have positive mass.

An eight-state POMDP realizes these histories. Start in \(z_1,z_2,z_3\), each with positive probability and distinct observation \(e_j\). Either of two actions moves \(z_j\) deterministically to \(x_j\), all of which emit \(u\). From \(x_j\), either action moves to absorbing \(y_1\) with probability \(p_j\) from the table and to absorbing \(y_0\) otherwise. Their observations are \(1,0\). Then \(h_j=(e_j,a,u)\) are reachable, and \(T=(a,\{1\})\) has the required probabilities. Section 5 permits these action-independent transitions and does not impose Section 4's communication assumption.

This refutes the marginal mutual-recoding conclusion under the stated premises. It does not refute Theorem 5 or the pairwise implication above.

### Bounded repair

The unconditional surviving statement is

\[
\mathbf1\{M_j(h)=M_j(h')\}
=\mathbf1\{\ell(h)=\ell(h')\}
\qquad\mathcal P\text{-almost everywhere}.
\]

To infer a function on a finite or countable, fixed-last-observation evaluation domain, sufficient additional coverage is that every positive-marginal-mass pair with the same \(M_j\) and different profiles receives positive pair mass in at least one direction. Combined with the stated directed completeness condition, such a collision would incur positive regret and is excluded.

The direction matters because witnesses are ordered high-probability then low-probability tests. It is not enough to silently replace \(\mathcal P\) by a product distribution or assume an opposite-direction witness exists. General measurable-domain recoding would require its own measure-theoretic formulation. The present counterexample needs none of those subtleties.

## 7. What can be carried forward

Three separations are useful independently of an FP application:

1. Fair-bet decisions, calibrated predictive probabilities and linear predictive operators are different recovery targets, with progressively stronger query and coverage assumptions.
2. Necessary distinctions under a weighted task family need not determine a unique representation partition on its marginal history support.
3. A finite-dimensional or uniquely decodable predictive representation does not itself supply a finite-bit online implementation, a learned recursion or an efficient exploration strategy.

Theorem 3 and Theorem 5 can be reused with their explicit report interfaces, distributions and margins. Theorem 4 should be cited with the anchor/indexed-test evaluation assumption supplied by Appendix G. Corollary 5 should be restricted to pairwise partition agreement unless the additional comparison coverage is proved.

No FP theorem, architecture prescription or empirical prediction is asserted here. The current ordinary-likelihood lexical-state question does not automatically instantiate the paper's threshold lotteries, paired-history witnesses or diagnostic reset access. Establishing such a connection would require an explicit mapping and costed evaluation interface that this reading does not provide.
