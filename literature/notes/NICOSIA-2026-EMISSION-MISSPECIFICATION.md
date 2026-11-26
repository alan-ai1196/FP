# Extra HMM states can pay for emission approximation without adding predictive memory

## 1. Source, versions and completed reading

Aurélien Nicosia, **Extra hidden states under emission misspecification in hidden Markov models**, Statistica Neerlandica 80(4), e70042, first published October 14, 2026. [Publisher record](https://onlinelibrary.wiley.com/doi/10.1111/stan.70042) · [Formal 15-page PDF](https://onlinelibrary.wiley.com/doi/pdf/10.1111/stan.70042).

The complete working edition read here is the author's September 28 revision, locked to [repository commit 97e1ba11a5d15a990e02daaef1937a82eb13a994](https://github.com/AurelienNicosiaULaval/corrective-hmm-states/tree/97e1ba11a5d15a990e02daaef1937a82eb13a994).

| Artifact | Actual coverage and provenance |
|---|---|
| [Author main manuscript](https://raw.githubusercontent.com/AurelienNicosiaULaval/corrective-hmm-states/97e1ba11a5d15a990e02daaef1937a82eb13a994/article/main.pdf) | All 18 pages, §§1–8, all formulas, 2 figures, 1 table, disclosures, 32 printed references and final figure legends. SHA256 aa4f876f3661c259fc3b0c35a683c1a6e9c3719c3cf5d7dc76947ad664161615. |
| [Author Supporting Information](https://raw.githubusercontent.com/AurelienNicosiaULaval/corrective-hmm-states/97e1ba11a5d15a990e02daaef1937a82eb13a994/supplement/supporting_information.pdf) | All 33 pages, S1–S6, five proofs, 9 figures, 13 tables and reproduction instructions. SHA256 7f022d664961ff3ed14210e8787978bd7d6d52b02b6f6f76790ce037a1a0aa49. |
| Formal journal edition | Complete 15-page textual body, formulas, table and reference list read through publisher HTML and complete PDF extraction. Definitions, all §2 theorem interfaces and §3 EM formulas were matched to the author text. The journal supplement itself was unavailable, so the formal-edition record remains scoped. |

Pro-D completed the author edition on November 26, 2026, Shanghai. Reading used all 17 active TeX files, including the inserted tables and legends, together with the PDFs. All 11 actual figure assets were visually inspected. Author-main pp5,11 and supplement pp3,10 were additionally checked as rendered pages. All 39 source bibliography entries were read, including entries not printed in the main bibliography. No numbered body footnotes occur.

The publisher records receipt on August 21, revision on September 28 and acceptance on October 1. The author's two PDFs were generated on September 28. The publisher supplement's rounded size, 757.9 KB, agrees with the author's 776,094-byte file, and its listed figure/table contents correspond. **These facts do not establish byte identity or a publisher-final supplement.** The source package and the formal journal edition remain separate index records.

The main text discloses ChatGPT assistance with text, Codex assistance with code and Claude review suggestions. This is an author paper with a peer-reviewed journal counterpart, not an official OpenAI or Anthropic research release.

## 2. The distinction being studied

The paper fixes a simple emission family \(\mathcal F=\{f_\eta:\eta\in\Theta\}\). A fitted hidden state can contribute one member of that family. If the true emission within one aggregate regime is a mixture of several members, adding fitted states can improve its representation even when the aggregate dynamics remain the same.

Three quantities must therefore remain distinct:

- The number of aggregate states in a supplied generative description.
- The number of simple emission components needed within that description.
- The predictive information that must persist from past observations to future observations.

The first is interpreted using the scientific problem. It is not inferred merely by counting likelihood-selected states. The second depends on the chosen emission family. The third is not measured by the state count of a restricted-emission representation.

The exact refinement construction and mixture-emission EM are credited by the author to earlier work, particularly Volant et al. (2014) and Holzmann–Schwaiger (2015). Their original papers were not separately read here. The current paper's mathematical emphasis is a uniform observed-law separation bound, beyond the simpler fact that a lower-order mixture cannot represent the marginal exactly.

## 3. Model classes and assumptions

All densities use one dominating measure \(\lambda\), and logarithms are natural. Let

\[
\mathcal M_K=
\left\{
\sum_{j=1}^K w_j f_{\eta_j}:
w_j\ge0,\ \sum_jw_j=1,\ \eta_j\in\Theta
\right\}.
\]

Repeated atoms and zero weights are allowed, so this is the class of mixtures with at most \(K\) atoms. Let \(\mathsf H_K(\mathcal F)\) denote observed laws of \(K\)-state HMMs with emissions in \(\mathcal F\). Candidate transitions and initial distributions are arbitrary.

The true aggregate chain has \(K_0\) states, stationary initial law \(\pi\), and transition matrix \(\Gamma^0\). Its emissions are
\[
g_k=\sum_{a=1}^{m_k}\omega^0_{k,a}f_{\eta^0_{k,a}},
\quad
R=\sum_km_k>K_0.
\]

The separation theorem requires the following conditions.

| Condition | Work it performs |
|---|---|
| \(\Theta\) compact and \(\eta\mapsto f_\eta\) continuous in \(L^1(\lambda)\) | Makes the lower-order mixture class compact in the metric used for separation. |
| Every \(f_\eta\) positive \(\lambda\)-almost everywhere | Permits candidate predictive conditionals on true histories without a support mismatch. Infinite KL still satisfies the lower bound. |
| Identifiable finite-mixture order | A positive mixture of distinct atoms cannot equal one with fewer atoms. The printed assumption also identifies the component parameters and weights up to permutation. |
| All \(R\) true atoms globally distinct | Prevents components in different aggregate states from collapsing into fewer marginal atoms. |
| \(\omega_{\min}=\min_{k,a}\omega^0_{k,a}>0\) | Keeps every component present within its aggregate state. |
| \(\varepsilon=\min_{k,\ell}\gamma^0_{k\ell}>0\) | Gives a lower bound on every next-state probability after every true history. |
| Stationary initialization | Extends that next-state lower bound to the first observation. |

The theorem is uniform over candidate HMMs for a fixed truth and fixed compact fitted family. It is not uniform over arbitrary true atom separation, minimum weights or transition probabilities.

## 4. From mixture separation to observed predictive loss

### Compact separation

For the fixed \(R\) true atoms, define
\[
\mathcal A_c=
\left\{\sum_{r=1}^R w_r f_{\eta_r^0}:
w_r\ge c,\ \sum_rw_r=1\right\},
\qquad c=\varepsilon\omega_{\min}.
\]
The actual true predictive weights show \(Rc\le1\).

For every \(K<R\), the source establishes
\[
d_{c,K}:=\inf_{p\in\mathcal A_c,\ q\in\mathcal M_K}
\|p-q\|_1>0.
\]

The proof is short and substantive. \(\mathcal M_K\) is a continuous image of the compact product of a simplex and \(\Theta^K\). The constrained weight simplex also makes \(\mathcal A_c\) compact. Identifiability makes the two sets disjoint. Disjoint compact subsets of a metric space have positive distance. Pinsker then gives
\[
D_{\rm KL}(p\Vert q)\ge\frac12\|p-q\|_1^2
\ge\frac12d_{c,K}^2.
\]

The proof needs neither continuity of KL nor an upper bound on KL. It uses \(L^1\) compactness and an extended-value KL inequality.

### The predictive weight floor

Let
\[
\beta^0_{t,k}(Y_{1:t-1})
=P_0(Z_t=k\mid Y_{1:t-1}).
\]
For \(t\ge2\),
\[
\beta^0_{t,\ell}
=\sum_kP_0(Z_{t-1}=k\mid Y_{1:t-1})\gamma^0_{k\ell}
\ge\varepsilon.
\]
Stationarity also gives \(\pi_\ell\ge\varepsilon\). Thus the true next-observation density is
\[
p_t^0=\sum_{k,a}\beta^0_{t,k}\omega^0_{k,a}f_{\eta^0_{k,a}}
\in\mathcal A_c
\]
for almost every true history at every time.

Every candidate \(K\)-state simple-emission HMM has a predictive density in \(\mathcal M_K\), whatever its candidate transition and initialization. The chain rule gives Theorem 2.6 and its stated \(K<R\) extension:
\[
\boxed{
D_{\rm KL}(P_0^{1:T}\Vert Q^{1:T})
\ge \frac{T}{2}d_{c,K}^2,\qquad
Q\in\mathsf H_K(\mathcal F),\quad K<R.
}
\tag{1}
\]

This compares observed process laws, not a likelihood conditional on matched hidden trajectories. Its lower relative-entropy-rate consequence follows by dividing by \(T\) and taking a liminf. Existence of an ordinary relative-entropy-rate limit is not needed.

Bounded independent reading of S1 found no material gap in this proof chain. The positivity, compactness and fixed-truth qualifications are doing real work.

## 5. Exact refinement and the restriction it imposes

Proposition 2.5 replaces aggregate state \(k\) by substates \((k,a)\) with emissions \(f_{\eta^0_{k,a}}\), initial probabilities \(\pi_k\omega^0_{k,a}\), and
\[
\Gamma^{\rm ref}_{(k,a),(\ell,b)}
=\gamma^0_{k\ell}\omega^0_{\ell,b}.
\tag{2}
\]

Summing over the component choices along each fixed aggregate path gives the original product of mixture emissions. Summing over aggregate paths proves equality of all observed finite-dimensional distributions.

Two restrictions are jointly necessary for this factorization:

1. Substates in the same source group share a transition row.
2. Within a destination group, component proportions do not depend on the source state.

Equal transition rows alone, or a small matrix rank alone, does not establish (2). An unrestricted \(R\)-state HMM can have more component-specific dynamics than the aggregate mixture model.

The author distinguishes this exact observed-law result from Proposition 2.4's aligned risk comparison. The latter fixes the aggregate hidden trajectory law, so emission risks separate into \(\sum_k\pi_k\delta_k(m_k)\). A strict improvement of one term implies a strict improvement of the total only when the original total risk is finite. That finiteness condition is explicitly retained in the source.

Corollary 2.7 instead enlarges the emission family to \(\mathcal M_M\), with \(M\ge\max_km_k\). The original \(K_0\)-state aggregate model then represents the same law directly. Neither representation selects a scientifically unique latent interpretation.

## 6. Independent consequences with explicit scope

These are direct deductions from the read model and proof, not claims of novel published theorems.

### 6.1 History adaptation cannot remove a restricted-decoder bias

The proof of (1) only uses membership of the output density in \(\mathcal M_K\). It therefore also applies to any measurable history-dependent predictor satisfying
\[
q_t(\cdot\mid Y_{1:t-1})\in\mathcal M_K
\quad P_0\text{-almost surely}.
\]
Its atom parameters and weights may depend arbitrarily on time and the complete past. No fixed candidate HMM is necessary. Still,
\[
D_{\rm KL}\!\left(
p_t^0(\cdot\mid Y_{1:t-1})\Vert
q_t(\cdot\mid Y_{1:t-1})
\right)\ge d_{c,K}^2/2.
\tag{3}
\]

This is a conditional expected excess log loss. It does not lower-bound the realized log-loss difference for every sampled observation.

If true initialization is arbitrary while the positive transition condition is retained, (3) holds from \(t=2\). The cumulative bound becomes \((T-1)d_{c,K}^2/2\), and the lower relative-entropy-rate conclusion is unchanged. Stationarity is sufficient to include the first observation, rather than necessary for this asymptotic consequence.

For a randomized predictor, distinguish scoring the realized density from scoring a density averaged over its random seed. The former keeps the bound if every realized output belongs to \(\mathcal M_K\). The latter can leave \(\mathcal M_K\), so the same restriction cannot be assumed.

### 6.2 Refined state count can grow while transition and predictive ranks do not

Define matrices
\[
E_{(k,a),\ell}=\mathbf1\{k=\ell\},\qquad
W_{k,(\ell,b)}=\mathbf1\{k=\ell\}\omega^0_{\ell,b}.
\]
Then
\[
WE=I_{K_0},\qquad
\Gamma^{\rm ref}=E\Gamma^0W,\qquad
\Gamma^0=W\Gamma^{\rm ref}E.
\]
Hence
\[
\operatorname{rank}\Gamma^{\rm ref}
=\operatorname{rank}\Gamma^0\le K_0.
\tag{4}
\]

The observed law retains its original \(K_0\)-state mixture-emission representation. Factoring cylinder probabilities through its hidden state gives observed Hankel rank at most \(K_0\). Equality need not hold, and this argument does not identify a minimal aggregate state count.

Within the restricted simple family \(\mathcal F\), the minimum exact HMM state count is nevertheless \(R\). Equation (2) supplies \(R\) states. Conversely, the stationary one-time marginal contains all \(R\) globally distinct atoms with positive weights \(\pi_k\omega^0_{k,a}\). Identifiable mixture order prevents any \(K<R\) simple-emission HMM from matching even that marginal.

The minimum is relative to the emission family. It is not an intrinsic lower bound on predictive memory, a unifilar-generator reconstruction theorem, or a finite-bit storage lower bound.

### 6.3 An explicit iid example with a quantitative loss floor

Fix \(a>0\) and
\[
\mathcal F=\{N(\mu,1):\mu\in[-a,a]\},\qquad
p=\tfrac12N(-a,1)+\tfrac12N(a,1).
\]
Let the observations be iid with density \(p\). This is a one-state aggregate process with two emission components. Its exact predictor is \(p\) at every history.

For any \(q=N(\mu,1)\), their characteristic functions satisfy
\[
\varphi_p(t)=e^{-t^2/2}\cos(at),\qquad
\varphi_q(t)=e^{-t^2/2}e^{i\mu t}.
\]
At \(t_*=\pi/(2a)\), the first is zero while the second has modulus \(e^{-\pi^2/(8a^2)}\). Since the test function \(e^{it_*y}\) has modulus one,
\[
\|p-q\|_1\ge
|\varphi_p(t_*)-\varphi_q(t_*)|
=e^{-\pi^2/(8a^2)}.
\]
Pinsker yields the explicit, nonsharp bound
\[
\boxed{
D_{\rm KL}(p\Vert q)
\ge\frac12\exp\!\left(-\frac{\pi^2}{4a^2}\right)>0.
}
\tag{5}
\]

Every history-adaptive predictor outputting one member of \(\mathcal F\) at each step has this same conditional loss floor. Unlimited observations and perfect knowledge of \(p\) do not remove the output-family restriction.

Yet exact prediction needs no observation history. The observed Hankel rank is one. The two-state simple-emission refinement has transition matrix
\[
\begin{pmatrix}1/2&1/2\\1/2&1/2\end{pmatrix},
\]
also of rank one. Its additional label represents a freshly drawn emission component.

The randomization distinction is concrete here. Choosing \(N(-a,1)\) or \(N(a,1)\) with equal probability and scoring the realized density pays a loss. Averaging those densities before scoring produces exactly \(p\) and zero excess KL.

This supplies a controlled counterexample to an inference from “extra fitted states improve prediction” to “extra temporal memory is needed.” The source's theorem and this calculation concern emission approximation, not optimization convergence.

## 7. What the empirical evidence actually tests

The empirical work illustrates model comparison and reports substantial limitations. It does not prove the theorem's assumptions for the real data.

### Simulation

The generator has two aggregate regimes and three distinct Gaussian atoms. The main comparison uses G2, G3 and M22, where G means one Gaussian per state and M22 means two states with two components each. M22 has four available components, so this comparison changes both component allocation and transition constraints. It is not the equal-component comparison used later.

The source reports 200 fixed-seed repetitions for each of three lengths. Its revised optimization protocol corrects 39 of 40 initial cases where BIC had favored G2 over G3. Additional starts come from fitted data and exact model nesting, not the generating parameters. This is direct evidence that optimization failures can distort a state-count comparison. Multistart convergence still does not certify global likelihood maxima.

The reported M22-over-G3 preference mainly reflects 13 versus 14 free parameters when fitted likelihoods are similar. The source gives Monte Carlo uncertainty and explicitly avoids interpreting 200 successes out of 200 as probability one.

### Genomic comparison

The main application compares G5 with M221 at the same total of five Gaussian components. Their Markov-state counts are five and three. M221 ties transitions and initial component proportions according to the refinement mechanism.

For total component count \(R\) and aggregate state count \(K\), the displayed free-initial-law parameter count simplifies to
\[
p_{\rm mix}=K^2-K-1+3R,\qquad
p_{\rm unrestricted}=R^2+2R-1.
\]
The difference is \((R-K)(R+K-1)\), giving 14 for \(R=5,K=3\). This is a parameter count, not automatically the degrees of freedom of a likelihood-ratio statistic.

The fitted G5 obtains 9.13 more log-likelihood units, while M221 has the lower BIC. Grouping the G5 component labels gives 99.73% agreement with the M221 path. Those are source-reported fits on one cell-line chromosome, not evidence for a uniquely true biological state count.

The bootstrap comparison uses 199 simulations under the fitted null model. Its reported p-value is 0.09 with Monte Carlo uncertainty. Only two sequence starts inform the free initial law, so the source does not automatically use the 14-parameter difference as a chi-square degrees-of-freedom count. Nonrejection is not an equivalence test, and the bootstrap does not remove observation-model misspecification.

Parameters remain fixed on evaluation sequences and filtering uses past observations, rather than smoothed full-path states. The technical repeat is another measurement of the same cell lines, not an independent patient cohort. Held-out chromosome comparisons show changing rankings, including substantial gains for G4 on one block and losses on another. G4 was added retrospectively. Symmetry-constrained F3 can have a lower BIC than M221. These negative and mixed results are retained in the paper.

### Supplementary movement analyses

The author compares Gaussian, support-respecting rate and joint rate-angle models, with explicit rounding and missingness rules. A mixture advantage in one Gaussian fit can disappear under another emission family. Predictive blocks are disjoint as scored observations but have nested training sets, so they are not independent experimental replicates.

The worked near-absorbing phase example contains only one observed change. Changing the transition-logit bound changes the estimated return probability by orders of magnitude while leaving decoding stable. Stable labels therefore do not identify a recurrent transition time. Reported habitat associations are descriptive and do not establish causal effects or validated behavioral labels.

No empirical reproduction was run in this reading. Source hashes, numerical-check descriptions and available code improve reviewability, but are not an independent reproduction result.

## 8. Limits relevant to reuse

The separation constant can shrink as true atoms coalesce or weights and transition lower bounds vanish. The theorem does not provide a useful numerical separation for every fitted data set. Equation (5) is one explicit fixed-family example, not a general rate formula.

A positive expected observed-law KL rate does not by itself establish an almost-sure gap between optimized sample likelihoods, BIC consistency, finite-sample order recovery or an efficient learning rule. The source explicitly reserves the required uniform stochastic likelihood control.

The relation to the preceding [Han–Jiang–Wu reading](HAN-JIANG-WU-2024-INFINITE-MEMORY-PREDICTION.md) is precise. That paper allows predictors outside a restrictive fitted HMM class and controls statistical error for a realizable model class. Here a fixed decoder family can create a nonvanishing approximation floor even when the true process is iid. There is no contradiction.

The paper and the independent iid construction are useful negative controls for interpreting state proliferation. Applying them to FP would require an actual mapping of the emission/output family and the prediction objective. No such mapping is established here, no architecture is proposed, and no core FP file was edited.

## 9. Verification and recovery boundary

The complete author main and supplement were personally read. A bounded second reader independently checked the compact-separation proof, the adaptive-predictor consequence, the rank identities and the Gaussian characteristic-function bound. No material gap was found in those specified arguments. This is not formal verification or a certification of the numerical analyses.

The formal journal's core mathematical interfaces match the author text, but its inaccessible supplement is not silently replaced as an authenticated identical edition. The complete author revision receives the full-reading record. The formal journal record describes its exact partial-version boundary.

All mandatory Astra requests through 53c10ef were already completed by their recorded owners. The new request 59b8251 was claimed by Pro-E in 40c0d2a before this publication. That successful remote claim was independently confirmed, and no competing request work was started. This remains an ordinary Pro-D direction study.
