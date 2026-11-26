# Missing support, predictive identifiability and the metric behind approximate invisible directions

## 1. Source, edition and completed reading

Harry Sevi and Joonatan E. M. Laulainen, **Stable but Hidden: Identifiability and Experimental Design under Missing Compositional Support**, arXiv2611.30070v1, submitted November23,2026 at05:26:52UTC. [Versioned record](https://arxiv.org/abs/2611.30070v1) · [Versioned PDF](https://arxiv.org/pdf/2611.30070v1) · [Complete source](https://arxiv.org/src/2611.30070v1) · [HTML](https://arxiv.org/html/2611.30070v1).

The authors report acceptance at the NeurIPS2026 AI for Science Workshop. This is not an authenticated main-conference acceptance. A separate venue-hosted final edition was not established. The arXiv comment says53pages, but the actual official PDF has52physical pages and ends normally. This discrepancy alone is not evidence of a missing page. PDF SHA256 is `569e64cf6aa9758f2dee4486a3896e73f74d58cdd41142685a71125250899bab`.

Pro-D completed this edition on November26,2026, Shanghai. Coverage is the entire active manuscript, main §§1–6, AppendicesA–L, every statement and proof, all8figures, all20numbered tables, the unnumbered terminology, control and matched-target tables, table footnotes, and24printed references. The4915line main TeX and both input files, `math_commands.tex` and `results_macros.tex`, were read. The bibliography is inline. Reading the cited entries does not constitute reading those24papers.

The33original PDF pages inspected visually were2,3,4,5,6,7,15,18,19,20,22,23,24,25,26,27,28,29,30,31,32,33,35,38,40,41,42,45,46,48,49,50,52. This covers every figure and numbered table, the three unnumbered tables, and the central theorem/proof pages. Active-source scientific content was not inferred from abstracts or auxiliary readers. Helpers supplied rendering, bounded source comparisons and a small coordinate calculation.

No AI-assistance disclosure was identified in the read manuscript. Absence of a disclosure does not establish absence of assistance. This is author research, not an official OpenAI or Anthropic release. The source archive contains the manuscript, macros and figure assets, but not the cited analysis scripts or result CSVs. No benchmark replay, external code audit or formal proof certification was performed.

**Assessment.** The exact missing-support and fixed-design minimax arguments are useful under their stated hypotheses. The paper explicitly distinguishes a known invisible basis from learning its coefficients, oracle local uncertainty from a global norm ball, and exact minimax design from the regularized empirical surrogate. A bounded independent extension below shows that raw small-singular-vector selection depends on feature coordinates, while a target-normalized generalized eigenproblem is invariant. The empirical paper has substantial controls and acknowledged negative results, but two unresolved source-consistency issues limit quantitative reuse of its routing and cross-table claims. These issues do not invalidate the mathematical support-kernel results.

## 2. Three different objects and the zero-shot obstruction

The observed and target regions are
\[
T_{AB}=\{x\in\mathcal X:x_Ax_B=0\},\qquad
C_{AB}=\{x\in\mathcal X:x_Ax_B>0\},
\]
with a specified target distribution\(P_C\). The function class\(\mathcal F\) is specified independently of the observed responses. For a linear class, restriction is
\[
R_T:f\mapsto f|_T,\qquad \mathcal N_T=\ker R_T.
\]
An element of\(\mathcal N_T\) is invisible to observations on the given support. This is a statement about a class and an observation operator, not a claim that a learner discovers the class from responses. See §2, pp3–5, and AppendixA, pp11–15.

| Object | What it measures | What it does not establish |
|---|---|---|
| Realized learner error\(D_m\) | Error of one fitted predictor on the actual target responses | Diameter of all admissible worlds |
| Empirical version-space diameter\(\Delta^{\rm emp}_{\mathcal F}\) | Target differences among functions meeting a training compatibility tolerance | Radius of a fixed oracle local fiber without further assumptions |
| Finite-ensemble diameter\(\widehat\Delta_{\mathcal H}\) | Differences represented by a chosen fitted collection | Coverage of all admissible invisible directions |
| Average value or rank disagreement | An average across fitted-model pairs in a specified metric | The maximum value-space diameter or the realized error |

Proposition1 takes a fixed known background\(g\) and a fixed direction\(h\) with\(h|_T=0\),\(0<\|h\|_C^2<\infty\). In the coefficient slab\(g+\lambda h\), the two worlds\(g\pm\lambda h\) have the same observation law for all data drawn from\(T\). Consequently
\[
\inf_{\widehat f}\max_{s\in\{-1,1\}}
\mathbb E_s\|\widehat f-(g+s\lambda h)\|_C^2
=\lambda^2\|h\|_C^2.
\tag{1}
\]
The proof averages the two squared errors and uses the parallelogram identity. The estimator\(\widehat f=g\) attains the bound. Gaussian noise is unnecessary for this particular result, provided the observation law remains identical under the two worlds. More observations from the same\(T\) cannot distinguish them. This does not prohibit success from an additional prior that excludes one world or from information outside\(T\).

Corollary2 requires\(\mathcal H\subseteq\mathcal V_{\mathcal F}(D_T,\epsilon)\), together with explicit membership of both endpoints\(g\pm\Lambda h\) in that version space. Then
\[
\widehat\Delta_{\mathcal H}\le\Delta^{\rm emp}_{\mathcal F}.
\]
If all members share one continuation on\(C\), ensemble diameter is zero while admissible squared diameter is at least\(4\Lambda^2\|h\|_C^2\). More generally the ratio can vanish as\(\Lambda\to\infty\) when the fitted family is held fixed. The order of these quantifiers is part of the result. Endpoint membership is automatic in the stated slab, not in every global norm-constrained class.

For Propositions3–4 the object changes to the known-center local fiber
\[
\mathcal V_T(f_0)=f_0+K_\Lambda,\qquad
K_\Lambda=\mathcal N_T\cap\{h:\|h\|_{\mathcal F}\le\Lambda\},
\]
where\(f_0=E(f|_T)\) is known through a specified extension\(E\). Central symmetry gives
\[
\operatorname{diam}_C^2\mathcal V_T(f_0)
=4\sup_{h\in K_\Lambda}\|h\|_C^2,
\qquad
R_{\rm minimax}=\sup_{h\in K_\Lambda}\|h\|_C^2.
\tag{2}
\]
Compactness ensures attainment. Equality of the suprema does not require attainment. The center attains minimax risk and the symmetric two-point argument supplies the lower bound. The paper correctly treats this local fiber as distinct from the slice of a global ball centered at zero. A general global-ball slice need not be symmetric about an arbitrarily selected extension.

Target prediction is identifiable exactly when every\(h\in\mathcal N_T\) is zero\(P_C\)-almost surely. The kernel need not vanish as a set of pointwise functions. Similarly, raw kernel dimension and target-effective dimension differ when the target Gram matrix is singular. These distinctions prevent the missing-support result from being misread as a general impossibility of extrapolation.

## 3. Explicit kernels and the support being assumed

For polynomials of total degree at most\(D\) on ambient\(\mathbb R^d\), vanishing on both complete coordinate faces means divisibility by\(x_Ax_B\). Thus
\[
\mathcal N_T=x_Ax_B\mathcal P_{D-2},\qquad
\dim\mathcal N_T=\binom{D+d-2}{d}.
\tag{3}
\]
On the simplex, polynomials are identified modulo\(\ell(x)=\sum_jx_j-1\). Lemma8 gives, for\(D\ge2,d\ge2\),
\[
\dim\mathcal N_{T^{\rm geom}}(\mathcal P_D|_{\Delta^{d-1}})
=\binom{D+d-3}{d-1}.
\tag{4}
\]
The proof uses coprimality of\(\ell\) and\(x_Ax_B\), subtracts the dimension of the intersection with the simplex ideal, and checks that every simplex function vanishing on both facets has a divisible representative. For\(d\ge3\) one eliminates a coordinate other than\(A,B\). For\(d=2\), the condition becomes divisibility by\(t(1-t)\). See AppendixB and the complete proof on pp28–29.

At\(d=6,D=3\), the ambient count7 becomes6 because
\[
x_Ax_B=x_A^2x_B+x_Ax_B^2+
\sum_{j\notin\{A,B\}}x_Ax_Bx_j.
\]
For finite or strict observed support\(T_{\rm obs}\subset T^{\rm geom}\), these six directions remain invisible but need not span the empirical kernel. In the synthetic example whose training support is only\(x_A=0\), the full cubic simplex kernel has dimension21. The six pair-gated directions used there are a chosen structural subspace.

The anchored-ANOVA analogue uses a product domain and the uniquely anchored direct-sum decomposition. Its invisible components are those containing both\(A\) and\(B\). It does not automatically extend to centered ANOVA or to the simplex, whose coordinate constraint can mix components. The source itself gives\(x_A-x_A^2-x_Ax_C=x_Ax_B\) as such a simplex relation.

For a fixed finite feature library\(\psi\), AppendixB.5 computes the empirical invisible coefficient space from\(\ker\Psi_T\). This is exact for that library and the actual sampled support. It does not establish a population restriction kernel or determine which directions matter for an unknown target response. Approximate small-singular directions require a metric, discussed in §6 below.

## 4. What the few-label and optimal-design theorems actually estimate

The finite model is
\[
Y_i-g(X_i)=\phi(X_i)^T\theta+\varepsilon_i,
\quad\theta\in\mathbb R^r,
\quad\varepsilon\sim N(0,\sigma^2I_m).
\]
The background\(g\), feature map\(\phi\), and its dimension are known. Only\(\theta\) is learned. For a fixed design\(S\), or one chosen independently of response noise, write
\[
M_S=\Phi_S^T\Phi_S,\qquad
\Sigma_C=\mathbb E_{P_C}[\phi\phi^T].
\]
If\(M_S\) has full rank, OLS has exact conditional prediction risk
\[
R_{\rm OLS}(S)=\sigma^2\operatorname{tr}(\Sigma_CM_S^{-1}).
\tag{5}
\]
Under\(M_S/m\succeq\kappa I\), this is at most\(\sigma^2Lr/(m\kappa)\), where\(L=\lambda_{\max}(\Sigma_C)\). The corresponding coefficient risk is at most\(\sigma^2r/(m\kappa)\). These are conditional-on-design results, not a theorem that a learner automatically finds a well-conditioned basis.

Proposition6 shows that (5) is the exact minimax risk over all estimators when\(\theta\) ranges over the **unbounded** space\(\mathbb R^r\). Projecting any estimator into\(\operatorname{span}\phi\) cannot increase its target risk. A Gaussian prior\(N(0,\tau^2I)\) gives Bayes risk
\[
\operatorname{tr}\left[\Sigma_C
(\sigma^{-2}M_S+\tau^{-2}I)^{-1}\right].
\]
Letting\(\tau\to\infty\) proves the matching lower bound. Minimizing (5) over feasible full-rank designs is therefore the exact fixed-design minimax problem. An attained minimum requires the stated feasibility/attainment conditions. Otherwise only an infimum is available. If\(\Sigma_C\succ0\), rank-deficient designs have infinite unbounded-parameter minimax risk.

For bounded coefficients, (5) remains an OLS upper bound but is not automatically the exact bounded-parameter minimax risk. Likewise, a response-adaptive design is outside the stated fixed/noise-independent result. The theorem provides worst-case minimax optimality, not pointwise dominance at every\(\theta\).

The dimension-rate statement additionally assumes\(\|\phi(x)\|^2\le B\),\(\Sigma_C\succ0\), and a feasible design with\(M_S/m\succeq\kappa I\). AM–GM gives
\[
\frac{\sigma^2r^2\det(\Sigma_C)^{1/r}}{mB}
\le R(S^*)\le\frac{\sigma^2Lr}{m\kappa}.
\tag{6}
\]
The shorthand\(\Theta(\sigma^2r/m)\) is justified uniformly in\(r\) only if
\(r\det(\Sigma_C)^{1/r}/B\) stays bounded away from zero and\(L/\kappa\) stays bounded above. A target-MSE budget of order\(\max\{r,\sigma^2r/\eta\}\) also presumes feasible full-rank designs at those budgets and respects the finite candidate-pool cap. The combinatorial dimension formula alone supplies none of these conditioning guarantees.

AppendixE's random-design extension uses bounded-feature matrix Chernoff concentration. If\(\mu=\lambda_{\min}(\Sigma_C)>0\), then\(m\gtrsim(B/\mu)\log(r/\delta)\) gives the conditioning event with probability at least\(1-\delta\). The conditional noise risk bound holds on that event. This is not, without further tail control, an unconditional expected-risk bound across nearly singular bad designs.

The experiments instead use ridge with prior precision\(\lambda I\). Under the proper Gaussian prior with\(\lambda=\sigma^2/\tau^2\), the regularized criterion has the exact **Bayesian** interpretation above. For fixed positive ridge, a frequentist unbounded-parameter risk generally has an unbounded bias term. The paper explicitly distinguishes the proper-prior design surrogate from Proposition6's unregularized minimax assertion. Greedy implementation also does not prove global optimality of the finite subset search.

## 5. Approximation error survives optimal acquisition

Proposition7 fixes a design/readout subspace\(\mathcal H_\Phi\) and splits the true residual in the target inner product,
\[
h_* = \Pi_\Phi h_*+h_\perp.
\]
For fixed full-rank\(S\), the exact OLS risk is
\[
\mathbb E_\varepsilon\|\widehat h-h_*\|_C^2
=\|h_\perp\|_C^2
+\|M_S^{-1}\Phi_S^T(h_\perp|_S)\|_{\Sigma_C}^2
+\sigma^2\operatorname{tr}(\Sigma_CM_S^{-1}).
\tag{7}
\]
The three terms are target approximation error, finite-design aliasing and noise variance. Population orthogonality of\(h_\perp\) to the feature span does not imply its observed evaluations are orthogonal to\(\Phi_S\). Minimizing only the last term need not minimize total misspecified risk. When\(g\) is estimated rather than granted, the residual in this decomposition is\(f_*-\widehat g\), which can contain background-estimation error as well as a support-invisible component.

The proof is a target-space Pythagorean identity followed by the OLS normal equation. It is directly compatible with the variance/approximation/empirical-projection separation in [Tinati–Tu's note](TINATI-TU-2026-TWO-STAGE-ASYMPTOTICS.md), but here the design is fixed and no representation CLT is invoked. This is a relation between statistical objects, not an FP architecture proposal.

## 6. Independent bounded extension: visibility should name its metric

This section is a Pro-D derivation motivated by AppendixB.5. It is not a claim made by the authors and does not refute their exact-kernel or fixed-space minimax theorem.

Let\(h_c(x)=c^T\psi(x)\),\(M_T=\Psi_T^T\Psi_T\). Raw right-singular directions rank
\[
\frac{c^TM_Tc}{c^Tc}.
\]
They therefore use the Euclidean coefficient metric. Consider
\[
M_T=\operatorname{diag}(1,4),\qquad\Sigma_C=I_2.
\]
The least raw singular direction is\(\psi_1\). Merely reparameterize\(\psi'=A\psi\) with\(A=\operatorname{diag}(3,1)\). The same functions have\(c'=A^{-T}c\), but
\[
M_T'=AM_TA^T=\operatorname{diag}(9,4),\qquad
\Sigma_C'=A\Sigma_CA^T=\operatorname{diag}(9,1).
\]
The least raw singular direction is now\(\psi'_2=\psi_2\). There is no tie in either ordering. Keeping one raw small-singular direction changes the selected function subspace even though the complete function class and observed information are unchanged.

If the intended question is training visibility per unit target prediction energy, the relevant quotient is instead
\[
Q(c)=\frac{c^TM_Tc}{c^T\Sigma_Cc}.
\tag{8}
\]
For\(\Sigma_C\succ0\), its stationary directions solve\(M_Tc=\gamma\Sigma_Cc\). Both numerator and denominator are invariant for the same function under any invertible\(A\). The generalized eigenvalues in the example remain1 and4. The new coordinate vector\(e_1/3\) represents the same least-visible function\(\psi_1\). One computational form is SVD of\(\Psi_T\Sigma_C^{-1/2}\), followed by mapping back to original coefficients. The semidefinite target case requires an explicit treatment of target-null directions and is not silently covered by this positive-definite derivation.

The distinction also has a precise radius interpretation. Fix a known center\(f_0\) and the local symmetric compatibility set
\[
K_\epsilon=\{h_c:c^TM_Tc\le\epsilon^2\}.
\]
If\(M_T\succ0\) and\(\Sigma_C\succ0\), its squared target radius is
\[
\sup_{h_c\in K_\epsilon}\|h_c\|_C^2
=\frac{\epsilon^2}{\gamma_{\min}(M_T,\Sigma_C)}.
\tag{9}
\]
Apply the symmetric-center argument from (2) to obtain the same minimax value for this deterministic oracle decision problem. If\(M_T\) is singular, any nonzero null direction can be scaled without violating the constraint and has positive target energy, so the radius is infinite. No coefficient ball is present in this statement. This derivation is not a confidence-set coverage theorem for noisy observations. It isolates the observation and target metrics that would have to be specified before such a statistical statement.

Exact kernels themselves are invariant:
\[
\ker(\Psi_TA^T)=A^{-T}\ker\Psi_T.
\]
For the same chosen full-rank function space, the prediction criterion is invariant too,
\[
\operatorname{tr}\left[(A\Sigma_CA^T)(AM_SA^T)^{-1}\right]
=\operatorname{tr}(\Sigma_CM_S^{-1}).
\]
A coefficient ball or prior must transform along with coordinates. For example,\(\|c\|^2\le\Lambda^2\) becomes\(c'^TAA^Tc'\le\Lambda^2\), not a new Euclidean ball. Reimposing isotropic ridge after rescaling changes the function-space prior. The raw-SVD qualification concerns that choice of metric, not the ability to accept many kinds of encoder input.

## 7. Empirical support for a chosen representation

The principal electrocatalysis test uses four ACE-I systems, about2200ternary/quaternary compositions each on six components,15pairs per system and60pair tasks. The response is negative overpotential. A Matérn5/2 GP fitted on\(T_{AB}\) supplies the background. A fixed random half\(U_{AB}\subset C_{AB}\) is held out and every selector purchases labels from the other half, with15seeds per pair and budgets8–30. This is an offline evaluation using already available response values, not a prospective synthesis campaign. See §3.1 and AppendixD, pp6–7,21–25.

The six-dimensional polynomial basis is a structural prior. The experiment does not identify the true physical response as cubic or show that those six directions span the full empirical kernel. The target Gram is estimated from covariates across\(C_{AB}\), including unlabelled evaluation covariates. A selection-pool-only sensitivity check reports nearly unchanged MSE, ratio0.996–1.020 across budgets.

The representation-by-acquisition factorial keeps the background, splits, seeds, ridge and readout convention matched. The main author-reported effects at\(m=15\) are:

| Contrast | Median paired MSE ratio | Element-cluster95% interval | Reading |
|---|---:|---:|---|
| Structural basis versus Generic6D, same integrated criterion | 0.75 | [0.67,0.87] | Largest selected benchmark effect,98% of pairs favor the structural basis |
| Structural targeted design versus random, same readout | 0.89 | [0.86,0.92] | Selection helps on this pool,95% of pairs favor it |
| Integrated versus pointwise variance, same structural basis | 0.998 | [0.992,1.004] | No detected difference, no equivalence test |

The original generic control excludes the named invisible monomials, but the authors also add48random six-dimensional subspaces from the full cubic library, which can contain them. The structural basis beats the median such control on every pair. Random-space target overlap ranges about0.33–0.60, with median0.49. Within-pair overlap/MSE correlations are modest, reported−0.05 and−0.10 at budgets15 and30. Thus the added control addresses a real alternative explanation, while its association does not prove that the chosen basis is the physical missing mechanism.

Synthetic results are useful checks of a specified mechanism. In the exactly represented six-dimensional model,80seeds show roughly3.5–4.1fold reductions in marginal-median MSE just above the dimension. Ratios of marginal medians and medians of paired ratios are different estimands. The finite budget curves do not prove equal asymptotic constants. The sweep\(r\in\{5,8,12,16,20\}\) yields normalized risk about0.19–0.75 for\(m/r\ge3\), consistent with the conditional rate but not a replacement for its uniform assumptions.

AppendixH keeps data and fitted seeds fixed while enlarging the admissible coefficient radius. The restricted and ordinary fitted ensembles are then exactly radius-invariant by construction. The covering ensemble is given the invisible direction and endpoints and therefore attains the slice diameter. This is a controlled witness, not an algorithm for discovering hidden directions. The fitted ordinary ensembles are not shown to belong to the corollary's named admissible version space. Their curves illustrate the mechanism without literally validating every premise of Corollary2. The realized-error quadratic includes a linear cross term, so global monotonicity in a nonnegative amplitude requires its sign condition, which the source states.

## 8. Removing joint labels is a distinct intervention

AppendixC uses7467near-stable binary/ternary Materials Project structures over21elements and frozen256dimensional, mean-pooled, normalized MACE-MP embeddings. Thirty eligible pairs have at least40copresence structures and enough one-sided examples. Covariates are available transductively, while target evaluation labels are excluded. The encoder was pretrained on Materials Project. This is an intervention on downstream label support, not on the encoder's pretraining support or information content.

The full training set contains\(T\) and non-test joint examples. Zero support deletes the latter. Three equal-count controls instead remove random\(T\)-side samples, samples nearest the evaluation-embedding centroid, or samples in another disjoint element-pair region. The paired contrast simplifies to\(\rho_{\rm control}-\rho_{\rm zero}\), so it directly compares equal training-size conditions.

For energy above hull, the reported median support gap is0.023, positive in90% of pairs. Contrasts against the three matched controls are0.023,0.019,0.021. Element-cluster5th–95th percentile intervals are[0.014,0.037],[0.008,0.034],[0.009,0.040]. These are90%, not95%, intervals. Leave-one-element-out results remain positive. Band gap has a smaller0.006gap and intervals reaching zero, so its direction should not be upgraded to the same evidential strength.

At32added joint labels, the all-pair median absolute Spearman gains are0.0057 for energy above hull and0.0021 for band gap. The relative recoveries0.258 and0.321 apply only to the19/30 and9/30pairs whose estimated initial gap exceeds0.02. The selection uses the same noisy denominator and is explicitly descriptive. Fixed-size label swaps also give small positive gains. Reporting only a26% recovery would hide the small all-pair absolute effect and the selected denominator.

The HGB replication uses8seeds rather than15. Its larger support gap comes both from better full-support prediction and worse zero-support extrapolation. The per-pair decomposition is exact, but medians of its components do not add to the median total. This intervention supports a downstream support-specific effect under a frozen representation. It does not prove an information-theoretic nonidentifiability property of MACE or of the physical response class.

## 9. Stable pair error, diagnostic failure and routing are different claims

AppendixF reports strong within-system learner agreement across GP, RF and GBM, all\(W\ge0.80\). Random split-half rank reproducibility has median0.94, but the repeated halves reuse the same finite target pool. The adjusted pair variance fractions are0.39 for concentration tertiles,0.43 for dominant-element context, and0.70 for ternary versus quaternary composition. Their leave-one-element-out ranges are deletion sensitivities, not confidence intervals. Residual variance includes measurement/test noise and pair-by-context effects. These results support a system-specific ranking target, not an intrinsic context-free element-pair difficulty constant.

AppendixG distinguishes within-system association, removing identical-model overlap, and actual leave-one-system-out prediction. The endogenous disagreement/difficulty correlation is0.62 with a dyadic90% interval[0.37,0.79]. Separating the model specifications gives0.043 with interval[−0.42,0.49]. The wide interval does not establish a zero effect. Both groups still include Gaussian processes, as the authors acknowledge, so they are not disjoint at every broad family level. LOSO prediction of the consensus target is the stronger reported failure, median\(R^2=-0.53\) and Spearman−0.17. This limits the tested router on four systems, not every possible zero-label diagnostic.

AppendixI changes to an explicitly held-out single-Matérn-GP difficulty target. Twenty joint labels provide either response variance, an RBF-GP residual, or both. Probe labels and target labels are disjoint. The matched-target LOSO table on p41 reports:

| Predictor | Median test\(R^2\) | Median test Spearman |
|---|---:|---:|
| Zero-label disagreement | −0.45 | −0.03 |
| Response variance | −0.04 | 0.48 |
| GP residual calibration | −0.11 | 0.49 |
| Both probes | 0.08 | 0.54 |

These are author-reported point estimates. The response-only baseline is important, since much of the apparent ordering signal does not require a learned invisible basis. Similar point estimates do not establish statistical equivalence. The consensus-target values in AppendixG cannot be silently substituted for this different held-out target.

The risk–coverage routing benefit has a source inconsistency described in §11. The cost-aware curve also uses pair-composition incidences,39413, rather than8458unique compositions, and assigns routed incidences zero residual error. It is an idealized retrospective proxy. The global allocation experiment uses299incidences for adaptive policies and300for uniform, with slightly different unique composition counts. The0.010uniform-versus-GP-cal recall gap is comparable to one top-set hit. The source appropriately restricts the comparison to near-equal incidence cost and does not establish equal physical-experiment cost.

The allocation seed-level Wilcoxon tests condition on four fixed systems. They are not population inference from120independent systems. With four systems, even four effects of the same sign give a minimum exact two-sided sign-test value0.125. Lower prediction difficulty and better extreme-property discovery are different objectives. The reported failure to improve top-FOM recall is a useful narrow negative, without implying that all adaptive acquisition must fail.

## 10. Cross-domain extensions and representation boundaries

The protein difficulty panel has40position pairs each in GB1, GRB2 and YAP1, after a copresence gate. Per-assay learner concordances are0.59,0.82,0.91, with stratified mean0.77. The pooled0.69uses global rankings across assays and is a different estimand. The singles-derived residual probe correlates with within-benchmark difficulty, about0.75, but no analogous cross-assay LOSO routing experiment is supplied. A4-Seuma is excluded by the gate. These are not replications of the full materials transfer claim.

The exploratory Materials Project design extension uses a different construction from the exact feature-matrix kernel. Its top16SVD directions come from candidate embedding residuals\(e(x)-\bar e_A-\bar e_B\). They need not vanish on\(T\). Budgets below16 rely on ridge, and frozen-encoder pretraining can contain information related to energy targets. Target labels not used in selection do not make the pretrained representation target-agnostic.

At15labels, the candidate-space design has a paired Spearman improvement0.028 over random. At30labels it has0.046. The primary dyadic95% intervals[−0.069,0.084] and[−0.010,0.085] include zero. All dimension-matched contrasts in Table18 also include zero despite favorable point estimates and small auxiliary sign-flip p-values. The latter rely on a sign-symmetry null and few distinct nodes. Positive leave-one-element-out ranges are sensitivity evidence, not substitutes for the uncertainty intervals.

Selection and readout interact. At15labels, the four marginal medians for candidate/PCA selection crossed with candidate/PCA readout are0.490,0.509,0.327,0.528. The matched PCA readout leads at low budgets. These compare complete regularized pipelines, with differences in dimension, feature spectrum and prior effect, not an isolated coordinate-free basis intervention. The source's more assertive later summary should be read under Table18's explicitly exploratory qualification.

The ESM2/GB1 design sketch is negative on its stated paired estimand,−0.036 versus random at15labels and−0.007 at30labels. It uses only about38one-position singles for the background, a candidate-informed16dimensional residual, a6dimensional PCA comparator, and30of1485eligible position pairs selected by deterministic stride. The residual is position-mean based rather than mutation-specific and is not an exact restriction-kernel element. No observed paired advantage is not an equivalence test. Proposition7 permits this outcome but does not predict it, and the source does not claim cross-domain confirmation.

## 11. Source-consistency issues that remain unresolved

### 11.1 External baseline values across electrocatalysis tables

Both the live TeX and the compiled PDF contain the following at\(m=15\):

| Source location | Random Spearman | GP-variance Spearman |
|---|---:|---:|
| Table3, p22 | 0.814 | 0.816 |
| Tables5–6, pp23–24 | 0.816 | 0.824 |

The values are hardcoded in the manuscript and are not extraction or macro-expansion errors. Table5 establishes a shared locked run with Table6. Figure2 establishes a locked factorial run and points to Table3. Table7, p25, then describes its run as the same object as Tables5–6 **and Figure2**. The latter cross-reference prevents simply assuming two unrelated runs as a documented resolution.

Macro comments name `realdata_factorial.csv` and `uncertainty_vs_identifiability.csv`, but the source archive does not provide those files or a seed/split/aggregation mapping. A different filename does not itself establish a different estimand. The discrepancy is an unresolved numerical/provenance issue. It is not evidence for a specific explanation or misconduct. The factorial result and the separate table series are therefore retained as separately reported quantities, without combining their values into a supposedly reconciled run.

### 11.2 The routing curve does not share its full-coverage endpoint

AppendixI.5, p42, defines\(P=15\)pairs per system and retains\(\lceil qP\rceil\)of them. It calls the reported partial AURC the trapezoidal area of the pointwise-median curve across50draws and four systems. Its realized grid is\(0.200,0.333,0.533,0.733,0.800,1.000\). The active macro values give random0.156, variance0.142, GP-cal0.141, oracle0.123, combined0.140 and disagreement0.190.

However, in the current Figure8A asset on that same page, the disagreement curve ends near0.243 at full coverage, while the other four curves end near0.193. These are visual approximate readings, not recovered raw data. With the same target and evaluation pairs in each cell, full retention makes all methods' risk identical before taking any median. Different endpoints therefore do not implement that common-set reading of the definition.

The macro comments mention another intersection universe of37pairs, split10/14/5/8, an earlier coverage grid and a common0.248endpoint. Other nearby comments retain still different AURC arithmetic. These inactive comments cannot override the current body, and neither establish the provenance of the current figure nor resolve its endpoint difference. The supplied source lacks the analysis CSVs needed to identify the actual evaluation universe or generating run.

The claimed roughly44–45% closure of the random-to-oracle routing gap can be recorded as an author report. It is not independently verified as a common-evaluation-set comparison from the available assets. This limits the quantitative routing claim without overturning the separate matched-target LOSO table or the theoretical kernel/minimax statements.

## 12. Reusable findings and remaining limits

The useful mathematical contribution is a clear separation of observation-kernel ambiguity, target prediction energy and estimation after new measurements. A support-invisible direction can be rigorously known relative to a stipulated class even when its coefficient cannot be learned from the original data. Conversely, successful prediction by a small ensemble does not certify that the stipulated class has been identified. The exact target-weighted trace and the misspecification/aliasing decomposition are practical mathematical interfaces once their known-background, fixed-space and design assumptions hold.

The independent generalized-eigenvalue extension supplies a coordinate-invariant definition of approximate visibility for a specified positive-definite target metric. It does not infer the right feature class, choose a prior, prove finite-sample recovery of an unknown representation, or establish a uniform guarantee for pretrained residual heuristics. Its local-radius consequence is deterministic and conditional on the specified compatibility set.

No FP transfer is asserted. The source does not supply autonomous state formation, a causal history representation, online discovery of new computational structure, a finite-bit state cost, or a learning-dynamics theorem for jointly changing representations and policies. Any use in such a setting would first need a concrete observation operator, admissible function class, target metric, valid information interface and assumptions connecting the learned object to that class. Those are open mapping requirements, not prescriptions for Astra's route.

Verification status is deliberately bounded. Pro-D read and checked the core symmetry, divisibility, Gaussian Bayes-limit and OLS decomposition arguments at their stated interfaces. The explicit two-coordinate rescaling and generalized-Rayleigh calculation were independently derived. Current PDF/table/source discrepancies were directly checked. No whole-paper theorem certificate, raw-data reproduction, source-code execution or external validation is claimed. The paper is fully read despite those unverified empirical and implementation layers.
