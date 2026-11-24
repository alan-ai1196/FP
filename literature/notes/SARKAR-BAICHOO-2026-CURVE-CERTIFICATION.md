# Sarkar–Baichoo (2026): Certifying Test-Time Scaling Curves

## Edition, provenance and reading coverage

Sohail (Neel) Sarkar and Shakuntala Baichoo, **Cheap to Draw, Expensive to Trust: Certifying Test-Time Scaling Curves**, [arXiv:2609.40190v1](https://arxiv.org/abs/2609.40190v1), September 30, 2026, 17:08:23 UTC. The authors list PMCC AI Lab, Peter Munk Cardiac Centre, University Health Network, Toronto. The current primary page, checked November 24, lists only v1 and no journal reference or DOI. This is an **outside-author preprint**, not an official OpenAI release. Its disclosure says generative AI assisted implementation, experimental design/analysis, literature review, figures and writing; authors retain responsibility.

The main reader covered **all 32 pages**, complete 1,335-line `main2.tex`, §§1–10, Appendices A–G, every statement/formula/proof, all **ten figures**, **five tables**, data/AI disclosures and **43 bibliography entries**. There are no body footnotes or separate active TeX inputs. All ten image assets and all table layouts were viewed; original PDF pp. 6, 8, 25 and 28 checked dense mathematical statements and proofs. [PDF](https://arxiv.org/pdf/2609.40190v1) · [TeX](https://arxiv.org/src/2609.40190v1).

Bounded independent checks covered the paired coverage chain, the fixed-law lower-bound quantifiers and the complete-pool variance calculation. They are described separately below. Full theorem certification, formal verification and experimental reproduction were **not** performed. No research-code release or pinned raw new-generation archive was authenticated in the inspected manuscript/source.

## Problem, observation model and decision guarantee

A known, equally weighted list has \(M\) questions. At each question \(x\), repeated answer pairs \(Z=(S,Y)\), numerical score and correctness bit, are iid from an arbitrary unknown \(P_x\). The first answer attaining the largest score among the first \(k\) wins; \(W_k\) is its correctness. The target is

\[
p_k(x)=E(W_k\mid x),\qquad
\theta_k=M^{-1}\sum_xp_k(x),\quad 1\le k\le K.
\]

The evaluator may choose questions, extend/stop paths, request labels and stop adaptively. It must return intervals of width at most \(2\varepsilon\) covering **all prespecified budgets** with probability at least \(1-\delta\), uniformly over answer laws. Three resources are charged separately: generated answers \(N\), correctness queries \(m\), and path starts/question visits \(n\). A label query is charged per **answer occurrence**. Reusing a known deterministic grade for repeated question–answer strings yields a separate distinct-grader-call count (§2, §7.2).

On the simultaneous event, the set \(\{k:u_k\ge\max_jl_j\}\) contains every optimal budget. A budget with \(l_k\ge\max_ju_j-\tau\) is \(\tau\)-optimal; maximizing lower bounds gives \(\tau=2\varepsilon\). Maximizing interval midpoints minus known costs has utility regret at most \(2\varepsilon\). Comparisons between two independently valid system bands use a union bound, regardless of their statistical dependence. This is the precise protection for choices made **after seeing the curve**; it is not a guarantee for adding arbitrary new budgets or generation policies after inspection.

## Three levels of statistical cost

### Fresh questions from a population

When each path starts at a fresh population draw, between-question variability remains. With deterministic caps and aborts counted as failures, put \(J=1+\lfloor\log_{16}K\rfloor\). For \(\varepsilon\le1/32\), \(\delta\le1/16\), §3/Appendix B give matching orders

\[
n\asymp\varepsilon^{-2}\log(J/\delta),\quad
m\asymp J\varepsilon^{-2}\log(J/\delta),\quad
N\asymp K\varepsilon^{-2}\log(1/\delta).
\]

These are separate resource caps attained jointly. The extra simultaneity factor for visits is only logarithmic in \(\log K\), and generated answers need no extra \(\log\log K\) factor. Winner paths have metric \(E(W_k-W_\ell)^2\le\log(\ell/k)\); logarithmic budget blocks admit a bracketing/chaining bound. Predetermined nested path lengths allocate more paths to cheap small budgets. Record indicators cost \(H_K\) labels in expectation, with a Bernstein cap. Lower bounds encode signs in geometrically separated percentile bands; posterior factorization controls labels, a question-level hidden-bit construction controls visits, and one top-scale bit controls generated answers. This population theorem does not describe a fixed list revisited freely.

### Fixed-list minimax cost

Define

\[
\bar v_k=M^{-1}\sum_xp_k(x)(1-p_k(x)),\qquad
\Sigma_{\rm w}=\sum_{j=1}^K\max_{k\ge j}\bar v_k.
\]

The total variance for a random question is \(\bar v_k+\operatorname{Var}_x p_k(x)\). Balanced visits remove the latter from estimation of the **listed-question average**, provided the interval construction actually uses within-question variability.

For continuous conditional score distributions with \(\max_k\bar v_k\le v\le1/4\), \(\Sigma_{\rm w}\le s\le Kv\), let \(M_\varepsilon=\min(M,\varepsilon^{-2})\), \(a_* =\min(v,s)\). Theorem 4 claims, up to polylogarithmic factors,

\[
\inf_{\mathcal A}\sup_{P\in\mathcal C}E_PN
=\widetilde\Theta\left(K/\varepsilon+M_\varepsilon+s/\varepsilon^2\right).
\]

The explicit label lower bound has shape

\[
H_K/\varepsilon+M_\varepsilon+
\frac{a_*[1+\log(s/a_*)]}{\varepsilon^2},
\]

with the last term zero when \(a_*=0\). A single evaluator, not told \(v,s\), attains both resource orders up to polylogarithms. **Validity is required outside the envelope class too.** Consequently even a deterministic benchmark must rule out unseen rare high-scoring answers; it cannot use knowledge that the true law belongs to a noiseless class.

The proof has three lower-bound mechanisms: score-tail contamination, unknown deterministic question labels, and within-question noisy score bands. At every law the contamination argument gives \(EN\ge7\kappa_\delta K/(32\varepsilon)\), where \(\kappa_\delta=\operatorname{kl}(1-\delta,\delta)\). Continuous-score percentile bands separately force \(H_K/\varepsilon\) label queries at every law. A multiscale construction forces both the noise-related answer and label terms at one law (Appendix C).

The constructive upper bound first estimates \(\theta_1\), then telescopes dyadic winner corrections. The key coupling is

\[
E[(W_k-W_a)^2\mid x]\le p_a(x)(1-p_a(x)),\qquad a\le k\le2a.
\]

Overlapping blocks, exchange of their unshared portions, and conditional variance give this inequality. Independent tie keys compare the first-maximum rule to the continuous-order case; ties do not invalidate the coupling. Variance-sensitive confidence sequences stop each correction level separately, and summing path lengths yields \(\Sigma_{\rm w}\). This multilevel construction establishes the rate; it is not the practical paired evaluator used for the headline measurements.

### A fixed law and the influence variance

For the symmetric, tie-averaged winner kernel \(\widetilde W_k\), define

\[
g_{k,x}(z)=k\{E[\widetilde W_k(z,Z_2,\ldots,Z_k)\mid x]-p_k(x)\},
\quad v_k(x)=E g_{k,x}^2,
\]
\[
\Gamma=\inf_{a\in\Delta_M}\max_{k\le K}
M^{-2}\sum_x v_k(x)/a_x.
\]

This is the best worst-budget **first-projection variance per generated answer**, not the variance of a single path winner. Theorem 6 states for every fixed law

\[
EN\ge\frac{\kappa_\delta}{128}
(K/\varepsilon+\Gamma/\varepsilon^2),\qquad
\liminf_{\varepsilon\to0}\varepsilon^2EN\ge\kappa_\delta\Gamma/2,
\]

and gives a law-independent schedule satisfying

\[
\limsup_{\varepsilon\to0}\varepsilon^2EN
\le2\Gamma\log(2K/\delta),\qquad
\Gamma\le\max_k k\bar v_k\le\Sigma_{\rm w}.
\]

The asymptotic statement fixes \(M,K,\delta,P\). It is not uniform in a growing benchmark or horizon. The upper method estimates block variances in a charged pilot, optimizes a Neyman allocation for a least-favorable mixture of budgets, and uses fresh, fully labeled blocks with all-subsets averages. Its pilot is \(o(\varepsilon^{-2})\) at fixed \(M,K\), but can be expensive at a practical precision: the stated MMLU-Pro pilot alone costs 179,200 answers at \(\varepsilon=1/32\), exceeding the paired evaluator's entire bill.

At any fixed precision, Proposition 5 rules out a single evaluator matching every law's individually tailored optimum: guessing a deterministic correctness table and verifying it costs \(O(\varepsilon^{-1}\log(1/\delta))\) at the guessed law, while any universal procedure has a table requiring \(\Omega(\varepsilon^{-2})\) visits/labels/answers. This does not contradict the fixed-law asymptotic influence result.

## Practical paired confidence sequence

For independent \(A,B\sim\operatorname{Ber}(p)\), \(0\le\lambda<1\), and \(\psi(\lambda)=-\log(1-\lambda)-\lambda\), Lemma 7 gives

\[
E\exp\{\pm\lambda(A+B-2p)-\psi(\lambda)(A-B)^2\}\le1.
\]

Two complete rounds visit every question once each. For budget \(k\), \(T_j\) is the pair's total correctness and \(D_j\) counts question-level disagreements. Predictable bets produce a weighted center and radius

\[
\frac{\sum_j\lambda_jT_j}{2M\sum_j\lambda_j}
\ \pm\
\frac{\sum_j\psi(\lambda_j)D_j+\log(2K/\alpha_S)}
{2M\sum_j\lambda_j},\qquad \alpha_S=.95\delta.
\]

The method intersects intervals over time, retires narrow budgets, and grows future paths only to the largest unresolved budget. Bets use **earlier completed pairs**, a pseudopair and a floor; their accuracy affects cost, while predictability is what coverage requires. A fixed final round uses the remaining \(.05\delta\).

The final pooled sum has unequal Bernoulli means. Ordinary Clopper–Pearson binomial tails cannot simply be transferred to it. Lemma 8 uses per-tail nominal \(a=.05\delta/(2K)\) and binomial inversion level \(a'=a/(1+a)\). Hoeffding's comparison handles thresholds at least one below the mean; a separate endpoint argument handles the remaining extreme threshold. The deterministic final round must be sized using these **corrected** intervals. Equality of corrected and uncorrected rounds in the experiments is not a general identity.

Coverage follows from a supermartingale for each budget/side, Ville's inequality and a union bound. A retired budget is a stopped process. For the final look, a latent complete sequence at the deterministic horizon gives an **unconditional** error event containing “still active and final interval fails”; conditioning first on being still active would be invalid. Cross-budget dependence is harmless to the union bound (§6).

The practical cost is

\[
EN=O\{KM+L(K/\varepsilon+\Sigma_{\rm w}/\varepsilon^2)\},
\qquad Em\le H_KEn,
\]

with logarithmic \(L\) and constants depending on the fixed bet cap. The startup \(KM\) is real. A dyadic-bet variant has an explicit bound with constant 16; the adaptive-bet proof's very loose millions-sized constant is not an implemented interval coefficient. A weighted portfolio of paired and multilevel procedures, on separate fresh answers and split error levels, achieves the minimax rate while charging at most \(32/31\) times the paired procedure **at its adjusted confidence level**, plus \(K\), when the portfolio weight is \(1/32\). This is an answer-count comparison, not a simultaneous guarantee for every resource.

## Other targets and the percentile theorem

- Paired coverage applies to binary pass@\(k\) and majority-vote path outcomes; their labeling rules differ. It does not automatically transfer the best-of-\(k\) minimax lower bounds or record-label savings to them.
- All-subsets averages reuse a larger iid path for every smaller budget. They are unbiased U-statistics, but nonbinary, so they need a bounded-mean betting inequality rather than Lemma 7. For pass@\(k\), stopping at first success gives a single DKW band over all budgets when paths start at iid uniform questions.
- A randomly sampled population panel permits fixed-list evaluation plus the separate Hoeffding radius \(\sqrt{\log(2K/\alpha)/(2m)}\); between-question sampling cost is retained.
- Independent complete trajectories from **one fixed generation policy** may have dependence within a trajectory. A variation quantity \(V=\sum_{k\ge2}P(W_k\ne W_{k-1})\) gives expected sup error \(O(\sqrt{\log(2+V)/n})\), and simulated Rademacher suprema give a computable band. This does not optimize acquisition or justify changing the policy adaptively between trajectories (§7).

For one question and **worst-coordinate mean squared error**, Theorem 13 compares known population score percentiles with observed ranks. Under \(K\to\infty\), \(T/\log K\to\infty\), \(C/K\to\infty\), \(C\ge T\), where \(C,T\) cap answers and labels,

\[
R_{\rm oracle}\sim\max\{\log K/(16T),K/(8C)\},\qquad
R_{\rm unknown}\sim\max\{\log K/(16T),K/(2eC)\}.
\]

Both deterministic and uniformly bounded expected resource caps are covered by the stated theorem. The ratio is \(4/e\) when \(\limsup C\log K/(KT)\le2\), one when \(\liminf C\log K/(KT)\ge8/e\), and intermediate otherwise. **This is not the ratio of fixed-width simultaneous-band costs.**

Appendix F uses adaptive van Trees lower bounds; a complete-pool U-statistic retaining all overlap orders; rank-bin domination; a saturated top-tail labeling design plus logarithmic/envelope components; and an overflow-controlled inclusion mask for deterministic caps. Its uniform variance lemma is

\[
\operatorname{Var}(U_{n,k})\le k/(2en)+(k/n)^2+1/n.
\]

For known finite score cells and fixed-width bands, §7.6 instead optimizes \(\max_k\{V_k(q)+(2\varepsilon/3)W_k(q)\}\), combining importance-weight variance and range. Convex duality supplies computable primal/dual brackets. Table 1's savings compare sufficient label budgets on two fully supplied pools, with answer generation uncharged.

## Experiments, costs and limits of evidence

The principal stored-pool study has 185 held-out pools formed from **eight** generator–benchmark answer sets, each scored by multiple verifiers. Every question has 100 stored answers, sampled **with replacement**. This defines an exact finite law, so its curve is exactly computable even for \(K>100\); those large budgets do not represent new distinct model outputs. Questions were split before tuning; 26 candidate evaluator configurations were compared on development halves. Another 32 pools were seen during development and are reported separately (Appendix G).

| Horizon | Median paired / cheapest certified competitor answer cost | Pools where paired is cheaper | Label-cost ratio |
|---:|---:|---:|---:|
| 64 | 0.74 | 175/185 | 0.73 |
| 256 | 0.66 | 175/185 | 0.68 |
| 1024 | 0.53 | 173/185 | 0.61 |

These are medians of five-run mean ratios, with an optimistic per-pool comparator chosen in hindsight. Bootstrap intervals resample **eight answer sets**, not 185 independent generators. The paired method misses none of 3,255 runs over all 217 pools/horizons/seeds. The tested 199-replicate within-question bootstrap band misses 58/925 held-out runs at \(K=64\); this diagnoses that particular procedure, not every possible bootstrap construction.

Balance with exact-binomial intervals saves little by itself. Variance-sensitive betting supplies the gain, and pairing improves over plug-in centering. At coarser \(\varepsilon=1/16\) the two-round startup makes the paired method lose on **every** held-out pool, median ratio 1.40; at \(1/64\) it wins on 179/185, median 0.51. Larger-horizon savings partly reflect saturation of 100-answer pools. A separate 4,000-answer-per-question pool still shows gains, but is also an empirical finite law (Figures 7–8).

The new MMLU-Pro study uses 100 questions, \(K=64\), three audit streams and a separate 409,448-answer reference stream. The authors report model identifier `gpt-6-luna`, no dated version, generation September 27–28, temperature one, eight answers per request and mean token log probability as verifier score. These are **author-reported experimental settings**, not independently authenticated model-version or current-price facts. A reported intraclass correlation of 0.005 is a diagnostic, not proof of iid generation.

Paired best-of-\(k\) uses a mean 79,133 answers and 6,160 occurrence labels; deterministic grade reuse reduces actual distinct grader calls to 256. All-subsets best-of-\(k\) uses 78,933 answers but 55,590 occurrence labels and 385 grader calls. Pass@\(k\) and majority all-subsets methods each use 49,067 answers. The fixed exact-binomial comparator costs 192,000 answers. The reported \$1.91 paired generation cost excludes the separate reference-generation bill; the complete study generated 716,384 answers for a reported \$17.24 (Table 3).

A fitted cost expression predicts 78,656 versus measured 79,133. **Its coefficients were frozen before the new study, but its variance input was measured from the separate reference stream.** Thus “within 0.6%” is not a cost-free forecast made before observing the new benchmark's answer distribution. Across settings the broader fitted law has \(R^2=.995\); this is empirical fit, not a finite-sample resource guarantee. All 18 new-study bands contain the estimated reference curves, whose own sampling uncertainty matters: the nearest margin is smaller than its reported reference standard error.

Reference accuracies rise from .736 to .960 for pass@\(k\), .767 for best-of-\(k\), and .787 for majority vote. Band separation certifies a pass@64 versus best-of-64 gap exceeding twelve points with at least 90% coverage via two 95% bands. It does not establish a deployable perfect verifier. Runtime is reported as \(O(N+RMK)\) and working memory \(O(MK)\) for paired evaluation; these are evaluator costs, not a learned predictor's deployed state size.

## Bounded independent checks and follow-up boundary

1. **Paired coverage.** Direct expansion reproduces the MGF inequality, including degenerate Bernoulli endpoints. For powers \(m\ge3\), the relevant coefficient factors as \(p(1-p)^2\sum_{j=0}^{m-3}(m-2-j)p^j\ge0\). Predictable pairing, retirement and final-level accounting pass the scoped check. A rational example \((p_1,p_2)=(1,4/5)\) gives \(P(S\le1)=1/5>19/100=P\{\operatorname{Bin}(2,.9)\le1\}\), confirming why uncorrected CP transfer is invalid. A finite exact check of 2,340 small Poisson-binomial cases found no corrected-level violation. The arbitrary-length internal-tail argument still imports Hoeffding's comparison theorem; that historical source was not fully reread.
2. **Fixed-law lower bound.** The bounded tilt uses expected allocation weights, with denominators \(1+w_x\) or \(\eta+w_x\), so zero allocation is permitted. The regime \(\Gamma\ge16\varepsilon K\) yields the influence term; the complementary regime is covered by the independent every-law calibration bound. Fixed-law asymptotics are uniform over the audited procedures through the regularized tilt, with \(\Gamma=0\) giving a trivial scaled lower bound. These checks do not certify the full minimax construction or every upper-bound constant. The main-text illustration with contamination probability \(3\varepsilon/K\) does not move every target by more than \(2\varepsilon\): at \(\theta_K=1/2\) the change is at most \(3\varepsilon/2\). The formal Appendix C proof uses the correct threshold involving \(-\log(1-2\varepsilon/a)\), \(a\ge1/2\); its lower bound does not rely on that incorrect illustrative constant.
3. **Complete-pool variance.** An independent shared-maximum conditional calculation reproduces the overlap covariance identity. Its pointwise extremizer is the globally realizable threshold labeling rule. With overlap fraction \(Z\), the bound reduces to \(e^{-2x}E(e^{xZ}-1)\le(2e)^{-1}EZ+EZ^2\). Hypergeometric moments yield the displayed uniform bound. Independent uniform tie keys preserve the target; tie averaging inherits the bound by Rao–Blackwell. Exact enumeration of 220 small finite-distribution/budget combinations reproduced unbiasedness and respected the bound. This does **not** independently certify the full \(4/e\) theorem.

Unresolved practical questions include learning the influence-optimal allocation at moderate precision without a separate costly pilot, robustness to drift/dependent streams, and validating the released experimental implementation and raw measurements if they become available. Fitas, [2608.21496v2](https://arxiv.org/abs/2608.21496v2), is the recent primary predecessor for reusable best-of-width evaluation; only its metadata and abstract have been inspected here. Other imported inputs include Hoeffding U-statistics and Poisson-binomial comparisons, Ville/betting sequences, stratified allocation, multilevel Monte Carlo, adaptive change of measure and van Trees. Reading their roles is not full reading of those cited sources.

The retained result concerns **acquiring simultaneous evaluation evidence about fixed generation laws**, with explicitly charged answer/label/visit resources. No predictive-state identity, unrestricted-mixture future causal-KL guarantee, adaptive reset theorem or FP architecture is imported.
