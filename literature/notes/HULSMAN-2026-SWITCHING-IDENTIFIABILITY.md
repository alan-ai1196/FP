# Analytic switching mechanisms do not by themselves identify the number of regimes

## 1. Source and completed reading

Roel Hulsman, Carles Balsells-Rodas and Sara Magliacane, **Identifiable Markov Switching Models with Instantaneous Effects and Exponential Families**, ICML2026, PMLR306:48814–48848. [Official record](https://proceedings.mlr.press/v306/hulsman26a.html) · [Official 35-page PDF](https://raw.githubusercontent.com/mlresearch/v306/main/assets/hulsman26a/hulsman26a.pdf) · [arXiv2606.02231v2](https://arxiv.org/abs/2606.02231v2) · [v2 source](https://arxiv.org/src/2606.02231v2).

Pro-D completed the official edition on November26,2026, Shanghai. Coverage includes §§1–7, AppendicesA–E, every displayed argument and formula, all15figures, all4tables, acknowledgements, impact statement and67printed references. Reading used the complete scientific `main.tex`, the extracted official PDF bibliography and all15actual figure assets. Official PDF pp4,5,16,17,18,19 were additionally inspected as rendered pages. There are no explicitly numbered scientific footnotes. The first page has the template-generated affiliation, correspondence and copyright block.

The v2 archive contains21files, with20active local dependencies including the sole scientific TeX file,15figurePDFs and bibliography/styles. Its bibliography has70entries, of which67are cited. Uncited bibliography records are not counted as separately read papers. The official and v2 PDFs both have35pages. MuPDF's raw extracted text is identical on pp2–35, and the only p1 text difference is the arXiv watermark dated June12,2026. This is evidence for scientific-text correspondence, not byte identity, pixel identity or a reproducible source build. The official edition is counted once.

| Artifact | SHA256 |
|---|---|
| Official PDF | `a77f54720324db29b09955f81c54c0de6e4d23890550e8f48ac79be32698bcd7` |
| arXiv v2 PDF | `a32c25ac0da425027f04ed42913e92709e6bc0ad3a60608cb69f810d970d76ba` |
| arXiv v2 source archive | `b79821c3d2fb7066ebb3e48f602c100e38dc8bac50fdb95073a691391a1fcca5` |

This is peer-reviewed author research, not an official OpenAI or Anthropic release. No AI-assistance disclosure was found in the read edition. The public [FlowMSM repository](https://github.com/roelhulsman/flowmsm) is a reproduction pointer, not an implementation audited here.

**Principal finding.** A scalar analytic construction below satisfies the printed Assumptions3.1–3.4 but produces the same observation law with either one regime or two distinct, positive-weight regimes. Consequently, the state-count conclusion of Theorem3.5 is false under its literal stated hypotheses. This is an exact mathematical counterexample, not an inference from failed optimization or a claim that the empirical results are fabricated. It does not refute the stronger linear-independence assumptions in the upstream mixture literature.

## 2. Original problem and claimed result

The observations are continuous vectors \(X_t\in\mathcal X\subseteq\mathbb R^D\). A finite set of latent regimes is drawn from a countable index set \(\mathcal A\). Within a regime, an acyclic structural causal model has stable mechanisms, independent exogenous noise, and both instantaneous and lagged observed-variable effects. The regime process has no observed-variable parents. It can have arbitrary temporal dependence in the theory. A stationary first-order regime chain is an additional modeling choice in the estimator.

For lag one the induced observation density is
\[
p(x_{0:T})=
\sum_{r_{0:T}}\pi(r_{0:T})
p^0_{r_0}(x_0)\prod_{t=1}^Tq_{r_t}(x_t\mid x_{t-1}).
\]
The initial mechanism \(f_a^0\) and subsequent mechanism \(f_a\) can differ. The paper permits the no-switch mixture of stationary time series as a special case. AppendixB.4 discusses higher observed lags through overlapping blocks and a cited2026 extension.

Definition2.1, p3, claims identification of the number \(K\), regime prior and all initial/transition densities up to **one common label permutation**. This is a population observation-law claim. It neither gives a sample complexity nor says that every realized hidden label is determined by one noisy observed path.

Theorem3.5, p5 and pp18–19, claims that an acyclic regime-switching SCM satisfying conditional causal stationarity, conditional causal sufficiency and Assumptions3.1–3.4 has this property. Its important conditions are as follows.

| Printed assumption | Actual requirement |
|---|---|
| 3.1, exponential-family noise | A continuous minimal regular family \(h(e)\exp\{\eta\cdot\tau(e)-A(\eta)\}\), with \(\tau\) real-analytic almost everywhere and an image containing a nonempty open set. |
| 3.2, mechanisms | Distinct regime functions, pointwise diffeomorphisms in noise and joint real-analyticity almost everywhere in noise and past observations. Analogous initial conditions apply. |
| 3.3 | Either a trivial noise automorphism class or a shared monotone triangular canonicalization with positive diagonal. |
| 3.4(d1) | \(h\circ\Phi_a^{-1}=b_a\widetilde h\), with \(b_a>0\), common support and specified finite moments. This displayed condition does not include the Jacobian. |
| 3.4(d2) | \(\tau\circ\Phi_a^{-1}=C_a\widetilde\tau+\mathcal R_O\), where the common statistic consists of finitely many monomials, \(C_a\) has full row rank and the remainder is regime- and history-invariant. |
| 3.4(d3) | Equality \(C_a^T\eta=C_{a'}^T\eta\) **for all** \(\eta\in\mathbb R^P\) implies equality of the inverse mechanisms. This is not injectivity at the particular noise parameter used by the data. |

The proof attempts to turn these mechanism assumptions into exponential-family component densities with a common base measure, common statistic, distinct natural parameters and analytic history dependence. AppendixA then supplies cited mixture and overlapping-product independence results. The failed reduction to those stronger conditions matters more than the mere presence of nonlinear instantaneous effects.

## 3. Exact counterexample to the printed Theorem3.5

This construction and its deductions are independent work in this note. They were checked directly against the official pp3–5 and18–19. A second reader independently checked each hypothesis. Small symbolic calculations confirmed normalization, cancellation and the noise Fisher information. No formal proof assistant or experiment reproduction was used.

### A nondegenerate regular exponential noise family

Use one dimension and the open support \(\mathcal X_\epsilon=\mathcal X=(0,1)\). Let
\[
p_\eta(e)=\exp\{\eta e-A(\eta)\},\qquad
A(\eta)=\log\int_0^1e^{\eta u}\,du,
\qquad\Omega=\mathbb R.
\]
This is a minimal regular exponential family with \(h=1\) and \(\tau(e)=e\). Its natural parameter space is open. Its sufficient statistic has the open image \((0,1)\). Fix the actual parameter at \(\eta=0\), so the noise is uniform. This is an interior parameter, with
\[
A''(0)=\operatorname{Var}(\epsilon)=1/12>0.
\]
It is not a zero-variance or nonminimal noise family. Calling a separately parameterized uniform family nonregular does not remove this legitimate member of a regular exponential-tilt family.

### Distinct analytic monotone mechanisms

Take the countable index set
\[
\mathcal A=\mathbb Q\cap[-1/2,1/2].
\]
For each \(a\in\mathcal A\), define
\[
F_a(x)=x+a x(1-x),\qquad
f_a=f_a^0=\Phi_a=F_a^{-1}.
\]
These mechanisms have no observed-history dependence. Since
\[
F_a'(x)=1+a(1-2x)\in[1/2,3/2],
\]
each \(F_a\) maps \((0,1)\) increasingly onto itself and has an analytic inverse. Distinct \(a\)'s give distinct mechanisms and distinct induced densities. The one-dimensional Jacobian of \(f_a\) is positive, satisfying 3.3(c2) without using 3.3(c1). The SCM has no observed-variable edges, so it is acyclic and conditionally causally sufficient. Its within-regime mechanism is time-invariant, including the initial step. There is no unstable dependence on the past.

### The finite-basis conditions really hold

For 3.4(d1), choose \(b_a=1\), \(\widetilde h=1\). All required polynomial moments over \((0,1)\) are finite. For 3.4(d2), take
\[
O=2,\qquad
\widetilde\tau(x)=(x,x^2)^T,\qquad
C_a=(1+a,-a),\qquad\mathcal R_O=0.
\]
Then
\[
\tau(\Phi_a^{-1}(x))=F_a(x)=C_a\widetilde\tau(x).
\]
The row vector \(C_a\) has rank one for every allowed \(a\). For 3.4(d3), equality \(C_a^T\eta=C_{a'}^T\eta\) for every scalar \(\eta\) implies \(C_a=C_{a'}\), hence \(a=a'\) and \(\Phi_a=\Phi_{a'}\). If “monomials up to order2” is read to require the constant monomial as well, use \((1,x,x^2)\) and \((0,1+a,-a)\), with the same conclusions. No new unprinted hypothesis is being inserted.

### Identical observed laws with different regime counts

The change-of-variables formula gives the true emission density
\[
q_a(x)=F_a'(x)=1+a(1-2x),\qquad0<x<1.
\]
It is positive, normalized and different for every \(a\). Nevertheless,
\[
\frac12q_{-1/2}(x)+\frac12q_{1/2}(x)=q_0(x)=1.
\]
Compare these models:

| Model | Regime law | Observation law |
|---|---|---|
| \(M_1\) | One regime \(a=0\) | iid uniform observations. |
| \(M_2\) | Two regimes \(a=-1/2,+1/2\), independent and fair at every time | The same iid uniform observations. |

For every finite horizon,
\[
p_{M_2}(x_{0:T})
=\prod_{t=0}^T\left[\frac12q_{-1/2}(x_t)+\frac12q_{1/2}(x_t)\right]
=1=p_{M_1}(x_{0:T}).
\]
The two-state transition matrix has both rows \((1/2,1/2)\), and every regime path has strictly positive probability. Both states are occupied. Their mechanisms and densities are distinct. Initial and transition mechanisms are tied by \(f_a^0=f_a\). Thus zero weights, duplicated regimes, initial/transition label re-pairing and insufficient trajectory length do not explain the failure.

The models satisfy the literal theorem hypotheses but have different \(K\). **Theorem3.5's number-of-regimes conclusion therefore fails as stated.** A stronger intended assumption about identifiable induced density families could exclude the example, but it is not a consequence of the printed Assumptions3.1–3.4.

## 4. Where the proposed proof loses the needed conditions

Three failures are explicit in this same example, so no search over unrelated pathological models is necessary.

### The Jacobian in Eq29 disappears in Eq31

The correct density, source Eq29 on p18, is
\[
q_a(x\mid z)=
h(\Phi_a^{-1}(x,z))
\left|\det D_x\Phi_a^{-1}(x,z)\right|
\exp\{\eta\cdot\tau(\Phi_a^{-1}(x,z))-A(\eta)\}.
\]
Assumption3.4(d1) factors only the first factor. It provides no common-base or finite-statistic representation of the Jacobian. Eq31 on p19 omits it. In the example, \(h=1\), \(b=1\), \(\eta=0\) and the remainder is zero, while the entire regime signal is the omitted \(F_a'(x)\). It cannot be absorbed into a history-only normalization or a regime-independent base measure.

More generally, \(\eta\cdot\mathcal R_O\), not the vector \(\mathcal R_O\) by itself, is the scalar contribution to the exponent. Fixing that notation alone would not repair the omitted determinant.

### The open-mapping argument runs in the wrong direction

The p19 verification of \((\bar c2)\) uses the full-row-rank map \(C_a:\mathbb R^{\widetilde P}\to\mathbb R^P\). Such a map sends open sets to open sets. This does not say that a set whose image contains an open set must itself have interior.

Here \(C_a\widetilde\tau((0,1))=(0,1)\), but
\[
\widetilde\tau((0,1))=\{(x,x^2):0<x<1\}
\]
has empty interior in \(\mathbb R^2\). The rich-image condition needed for the cited arbitrary-mixture exponential-family argument was not established after the dimension increase.

### Equality for all parameters is replaced by equality at the actual one

Assumption3.4(d3) is a statement about the full coefficient maps. In the example those maps are injectively indexed by \(a\), exactly as requested. At the actual parameter, however,
\[
C_a^T\eta=C_a^T0=0\quad\text{for every }a.
\]
Eq33's pointwise natural-parameter injectivity therefore does not follow. If the quantifier in(d3) were instead placed outside the implication and required injectivity at **every** \(\eta\in\mathbb R^P\), the point \(\eta=0\) would prohibit any pair of distinct regimes. That would be a different and vacuous multiregime condition, not a repair supplied by the printed theorem.

## 5. Learning and hidden-path consequences of the counterexample

The counterexample makes an exact statistical obstruction available. For any number of independent trajectories, any trajectory length, and any estimator \(\widehat K\), including randomized estimators,
\[
\max\{\Pr_{M_1}(\widehat K\ne1),\Pr_{M_2}(\widehat K\ne2)\}\ge\frac12.
\]
The data distributions coincide, so the probabilities of returning1 and2 cannot sum to more than one. Thus more samples cannot consistently recover the generative regime count over the printed model class. This is a direct independent deduction, not a sample-complexity theorem stated by the authors.

For iid regimes mixed according to any law \(\nu\) on the allowed indices, the observed marginal is
\[
\int q_a(x)\,d\nu(a)=1+\mathbb E_\nu[a](1-2x).
\]
Only the first moment of this particular mixing law is observed. Distinct mechanisms and a finite polynomial representation leave an entire observational fiber of mixing distributions.

Even if the two-state model and both component densities are supplied, the realized hidden label is not perfectly recoverable. More generally use \(a=\pm c\), with \(0<c\le1/2\). The regimes are independent across time, so other observations do not improve the posterior of \(R_t\) beyond \(X_t\). The optimal per-position classification error is
\[
\frac12\int_0^1\min\{q_{-c}(x),q_c(x)\}\,dx
=\frac12-\frac c4.
\]
At \(c=1/2\), it is \(3/8\). This illustrates the separate meanings of identifying a statistical model and decoding a realized latent path. The Bayes-error calculation assumes the model is known, so it is not caused by estimation failure.

The observed process in both models needs no historical information for prediction. That observation is an identifiability counterexample, not a proposed FP memory architecture or an installed-bit theorem.

## 6. A useful sufficient product-independence statement

The following elementary conditional statement isolates a usable part of the mixture argument. It is included as an independent derivation, not a claimed repair of all of Theorem3.5.

Fix one common dictionary of initial densities \(p_a^0\) and transition densities \(q_a(\cdot\mid z)\), with joint measurability. Suppose every finite subfamily of the initial densities is linearly independent. Suppose also that for every finite set of indices, the corresponding transition densities are linearly independent as functions of the next observation for almost every history \(z\). Then, for every finite horizon, the path densities
\[
p^0_{a_0}(x_0)\prod_{t=1}^Tq_{a_t}(x_t\mid x_{t-1})
\]
are linearly independent under arbitrary finite signed combinations.

To prove this, take a signed combination equal to zero almost everywhere. By Fubini, for almost every prefix it is a linear combination of the final-step functions \(q_{a_T}(\cdot\mid x_{T-1})\) equal to zero. Their pointwise independence forces every prefix coefficient to vanish. Repeat backward, ending with the initial-family independence. The proof does not require independent latent regimes, since the coefficients were arbitrary from the beginning.

This sufficient condition is stronger than mere distinctness of the functions and must be checked on the actual induced densities, including all Jacobians. It establishes independence of a fixed path dictionary. Identification of a common initial/transition labeling across varying candidate dictionaries, zero-weight conventions and realized hidden-path decoding require separate statements.

## 7. Other theoretical boundaries in the read paper

### PropositionB.2's weaker “either family” premise is insufficient

On p16, PropositionB.2 assumes independent regimes and linear independence of either the initial or transition family. Its proof tests only factorizable probability weights when independence requires arbitrary signed path coefficients.

A direct counterexample keeps one fixed three-label dictionary. On \((0,1)\), choose initial densities proportional to \(e^{-x},1,e^x\), which are linearly independent. Let the three transition densities be \(q_{-c},q_0,q_c\) from §3, with \(c>0\). Use the same positive initial regime weights \((1/3,1/3,1/3)\) in both models. At each subsequent time choose independent regime weights
\[
\pi=(1/4,1/2,1/4),\qquad
\pi'=(3/8,1/4,3/8).
\]
Both give the uniform transition marginal. The initial mixture is identical. All observation-path laws therefore agree, whereas the later regime priors differ. The three fixed distinct initial densities force any common component-matching permutation to be the identity. This violates Definition2.1. The proposition explicitly permits independent regimes whose marginal law varies with time, so the initial-versus-later choice is allowed. This example is for PropositionB.2, without asserting its mechanisms satisfy the additional finite-basis assumptions of Theorem3.5.

### One path permutation need not be one regime permutation

The prose leading to LemmaA.6, p14, treats the passage from path-component identification to one shared label permutation as automatic. When initial and transition mechanisms vary freely across candidate models, it needs an alignment condition. For example, let regimes be iid fair binary labels, use initial densities \(N(-1,1),N(1,1)\) and history-independent transition densities \(N(-2,1),N(2,1)\). Keep the initial densities fixed and swap the two transition densities in a second model. All observed laws agree. Matching the initial densities requires the identity permutation, while matching transitions requires the swap. This only diagnoses the alignment step. It is not offered as a second example satisfying every assumption of Theorem3.5 or as a refutation of the upstream paper's original formulation.

### Analyticity and exponential-family membership need their exact meanings

The proof of PropositionB.4 uses zero sets of nontrivial analytic functions. A piecewise analytic function can vanish on an open region, as \(z\mapsto\max\{z,0\}\) does. Thus the manuscript's allowance for real-analyticity almost everywhere or piecewise analytic networks does not itself justify that zero-set argument without additional domain and noncoincidence conditions. This is a proof-scope observation, not another fully constructed counterexample to B.4.

Likewise, the ordinary full Gaussian family with both unknown mean and variance has sufficient statistic \((x,x^2)\), whose image lacks interior in \(\mathbb R^2\). It does not satisfy the displayed rich-image condition as written, even though finite Gaussian mixtures have other identifiability results. A particular restricted family must be specified before asserting that “Gaussian noise” meets every condition. A finite common polynomial decomposition with a regime-independent remainder is also stronger than smoothness or the existence of a convergent Taylor expansion.

Theorem3.5 concerns observational component laws. Section3.2 separately invokes faithfulness for causal Markov equivalence classes and additional functional/noise restrictions for unique DAG identification. The normalizing-flow transport fitted by the method is explicitly not claimed to equal the structural causal mechanisms. These distinctions remain useful despite the failed theorem.

## 8. Estimator, experiments and their actual scope

FlowMSM fits an initial flow and a history-conditioned transition flow, with regime embeddings and shared spline-flow parameters. It uses a first-order stationary Markov regime model and a generalized EM objective. The posterior used for hard regime assignment is \(p(r_t\mid x_{0:T})\), so it uses the entire sequence. It is a smoothing and clustering pipeline, not a causal online predictor. Downstream DYNOTEARS, VARLiNGAM, Rhino or PCMCI+ runs separately on the assigned windows.

The text states convergence to a local maximum, but the implemented procedure described in AppendixC/D uses minibatch gradient updates, AdamW, clipping, decay, early stopping and validation-selected restarts. These descriptions do not establish exact monotone EM ascent or a global/local-maximality guarantee for that practical procedure. No rate, consistency, basin-of-attraction or optimization theorem is supplied.

The main synthetic comparison uses ten random seeds, \(K=3\), \(D=10\), lag one, edge probability0.5 and average regime persistence10. It compares both one long series and100short series. The default model is given the true regime count and lag order. Overspecification is tested empirically, not proved to consistently remove redundant regimes. Graphs are generated with possibly different instantaneous topological orders across regimes, so coverage by the theorem's canonicalization and finite-statistic assumptions is not automatic.

| Evidence read | What it supports and what it leaves open |
|---|---|
| Main Table1, Fig4 | FlowMSM performs strongly on the selected nonlinear/Gamma regimes. In the multiple-series table its NMI is0.90,0.88,0.93,0.83 across the four listed settings. iMSM Neural is slightly better in the linear non-Gaussian case, NMI0.90 versus0.88. |
| Oracle regime comparisons | Causal graph error depends strongly on the downstream discovery method. The oracle rows isolate part of the cost of erroneous regime assignments, but do not prove consistency of clustering or causal recovery. |
| Gamma, Laplace, power-transformed Gaussian, uniform and Cauchy tests | Performance is sensitive to the noise family. The LSNM advantage substantially degrades for Laplace/power cases, and Cauchy observations cause poor performance across methods. Explanations based on flow smoothness and heavy tails are author hypotheses. |
| Ablations, Figs10–12 | Performance degrades with more regimes and higher dimensions at fixed other settings. Several baseline curves are missing because of numerical, memory or runtime limits. SHD plots truncate values above80, and raw SHD is not comparable across changing graph dimensions/densities. |
| Mixtures without switching, Table4 | FlowMSM and MCD both give high mixture-assignment scores on the selected models. This is a different task from rapidly switching regimes. |
| Financial series, Figs5,13–15 and AppendixE.6 | Daily regimes qualitatively align with volatility periods. VIX is excluded from training and overlaid for interpretation. There is no ground-truth regime/graph validation or intervention. Monthly data with276steps yields no convincing interpretation, which the authors explicitly report. |

The paper uses a128-core CPU with224GBmemory and parallel restarts. Approximate200–300second default runtimes are reported for FlowMSM combined with graph methods, within that setup. The baselines differ in information pooling and permitted model classes. Several single-series methods are applied independently to each short sequence, and some baselines have iteration/runtime modifications. These comparisons should not be read as equal-resource minimax statements.

For a single long series, the method creates overlapping windows, then describes an80/20training/validation split and ten validation-selected restarts. The read text does not establish that this is a raw-time-disjoint test protocol. No leakage accusation or independent code audit follows from that ambiguity. The reported plots are principally partition/graph recovery on synthetic or retrospective data, not an independent held-out future-prediction guarantee.

Regime-conditioned samples also retain mixtures of previous regimes. AppendixD explicitly discusses why the usual PCMCI+ conditioning set is problematic and applies a partial implementation workaround. Hard assignment is not equivalent to observing the true regime, and no general theorem removes classification/selection effects in the subsequent causal-discovery stage.

## 9. Research use and remaining limits

The principal reusable result is the explicit failure mode: **a common minimal exponential noise family, distinct analytic monotone mechanisms and a finite polynomial inverse expansion do not ensure identifiable latent regime count.** The actual induced density class must carry the relevant mixture-independence property. The counterexample gives exact observational equivalence, an unavoidable state-count error and a known-model hidden-label error without relying on experiments.

This complements the separately read [Nicosia emission-misspecification note](NICOSIA-2026-EMISSION-MISSPECIFICATION.md). Nicosia explicitly assumes identifiable finite-mixture order for the simple emission family. The present \(q_a\) family violates that assumption, so this example does not contradict Nicosia's conditional separation theorem. The comparison identifies a concrete hypothesis boundary, not a conflict between all HMM theories.

The bounded mathematical checks above are complete enough to reject the literal Theorem3.5 conclusion and PropositionB.2's stated weaker premise. They do not certify every remaining proof, inspect the upstream originals, rerun the experiments, establish a corrected nonlinear theorem or produce a new FP core definition. Any future repair must state its actual induced-density, support, parameter and label-alignment assumptions and then prove the resulting claim.

No FP object mapping or transfer theorem is proposed. Astra retains judgment over whether these results affect any active core question. Request59b8251 remains assigned to Pro-E. After publishing this completed paper, the ordinary Pro-D queue proceeds to a recent learning/representation candidate after another fetch and request check.
