# Request 59b8251: learning a balanced partition and retaining its predictive value

Date: 2026-11-26, Shanghai. Researcher: Pro-E. Request: [59b8251805a2e6e0edf4b828a5562848e215f983](https://github.com/alan-ai1196/FP/commit/59b8251805a2e6e0edf4b828a5562848e215f983). Existing claim: [40c0d2a](https://github.com/alan-ai1196/FP/commit/40c0d2a). This is a completed **scoped prior-art comparison**. No source is promoted to fully read.

## Result

The observation model has an exact antecedent in the Poisson stochastic block model. The quadratic payload dependence for independent signs follows directly from an established message-cell inequality in Hidden Matching. Predictive KL distortion and compression of a posterior mean are established information-bottleneck and indirect-quantization constructions. These ingredients deserve explicit attribution.

The bounded primary-source search did not locate either complete balanced-partition law under the request's exact fixed-payload and fresh-pair interface. In particular, asymptotic nonreconstruction does not specify the finite, nonzero early prediction gain. This finding does not establish global novelty.

A material resource distinction is proved below. Replacing the fixed alphabet bound by an average mutual-information budget admits a rare-reveal code with gain of order \(\kappa^2 b/D\). That differs from the requested fixed-payload order \(\kappa^2 b^2/D^2\). The source-generation, loss and memory interfaces must therefore accompany any comparison.

## 1. Exact comparison target

The request points to [the dictionary-storage statement](../../research/frontier/FOUNDATION.md#how-many-bits-of-a-learned-dictionary-can-predict-a-fresh-pair) and [the acquisition statement](../../research/frontier/INTELLIGENCE_OBJECTIVE.md#finding-an-unknown-raw-word-distinction-before-it-can-be-stored). Its model is

\[
\mathcal S_D=\{s\in\{-1,1\}^D:\mathbf1^\top s=0\},\qquad
P_s(x,y)=\frac{1+\kappa s_xs_y}{D^2},
\quad D\ge4\text{ even},\quad 0<\kappa\le\tfrac12 .
\]

Training consists of \(n\) independent ordered pairs conditional on one shared unknown \(s\). Repeated pairs and equal endpoints are observed. At deployment the first endpoint of a fresh pair is supplied and the second is scored by ordinary log loss.

For the uniform balanced prior, write

\[
M_0=\mathbb E ss^\top,\qquad
Q_0(x,y)=D^{-2}(1+\kappa M_0(x,y)).
\]

The diagonal of \(M_0\) is one, and its other entries are \(-1/(D-1)\). The comparison baseline \(Q_0\) already exploits equality of the endpoints. It earns order \(\kappa^2/D\) over uniform without any learned dictionary.

The two requested additional gains are:

| Interface | Resource | Requested order above \(Q_0\) |
|---|---|---|
| Encoder supplied the partition, followed by deployment | A single installed message with at most \(2^b\) values | \(\Theta(\kappa^2\min(b,D)^2/D^2)\), for integer \(b\ge1\) |
| Encoder observes \(n\) ordinary pairs | Unrestricted retained training information, \(n\kappa^2\le cD\) | \(\Theta(n\kappa^4/D^2)\) |

The first is an oracle-memory comparison, followed by separate learning considerations. The second prices acquisition before reconstruction. Neither statement limits all temporary working memory during training. The present note checks precedence and interfaces, without certifying or editing the core proofs.

## 2. An exact Poisson SBM antecedent

Karrer and Newman explicitly use undirected multigraphs with independent Poisson edge counts, including self-loops. Their adjacency convention counts a self-loop twice on the diagonal. Section II, Eq. (1), gives the complete likelihood. This is the ordinary, non-degree-corrected model in that paper. [Journal source, printed p. 016107-2](https://www.cs.cornell.edu/courses/cs6241/2019sp/readings/Karrer-2011-community.pdf), [DOI](https://doi.org/10.1103/PhysRevE.83.016107).

### Exact mapping, derived here

Draw \(N\sim\operatorname{Pois}(\tau)\), independently of the balanced partition, and then \(N\) requested ordered pairs. Poisson splitting gives independent ordered counts

\[
C_{ij}\sim\operatorname{Pois}\!\left(\frac{\tau}{D^2}
                      (1+\kappa s_i s_j)\right).
\]

For \(i<j\), let \(A_{ij}=A_{ji}=C_{ij}+C_{ji}\), and let \(A_{ii}=2C_{ii}\). Set

\[
\omega_{++}=\omega_{--}=\frac{2\tau(1+\kappa)}{D^2},
\qquad
\omega_{+-}=\omega_{-+}=\frac{2\tau(1-\kappa)}{D^2}.
\]

Then the off-diagonal counts have means \(\omega_{s_i,s_j}\), while the self-loop counts have means \(\omega_{s_i,s_i}/2\), exactly as in the source. Moreover,

\[
\sum_{i<j}\mathbb E A_{ij}+\sum_i\mathbb E(A_{ii}/2)
=\frac{\tau}{D^2}\left(D^2+\kappa(\mathbf1^\top s)^2\right)
=\tau .
\]

The total count is independent of the balanced assignment. Conditional on \(N=n\), randomly orient each nonloop and randomly order all observations. The resulting tape has precisely \(P_s^{\otimes n}\). Orientations and order are ancillary given the counts.

Thus a fixed-total, balanced specialization of an established Poisson SBM supplies the same observation experiment. Repeats and loops do not establish a new generative-model family. The mapping is elementary Poisson conditioning applied to the source model, rather than a learning theorem stated by Karrer and Newman.

Projecting the off-diagonal multigraph counts to edge indicators gives independent Bernoulli probabilities

\[
p_\pm=1-\exp[-2\tau(1\pm\kappa)/D^2]
\]

before conditioning on the total. This projection discards multiplicities. After conditioning, independent-edge assumptions no longer hold. A finite prediction-rate theorem consequently requires quantitative work beyond invoking an asymptotic simple-graph threshold.

## 3. The quadratic payload law already has a cube antecedent

The request already cites the 2011 conference version of Buhrman, Regev, Scarpa and de Wolf. The later journal version provides an especially clear numbered statement. In **Claim 3.4, printed p. 634**, a deterministic message cell of mass \(p_z\) under independent fair signs satisfies

\[
\sum_{i<j}\beta_{z,ij}^2
\le
\begin{cases}
4\log_2^2(1/p_z),&p_z\le\tfrac12,\\
2,&p_z>\tfrac12,
\end{cases}
\qquad
\beta_{z,ij}=\mathbb E[S_iS_j\mid Z=z].
\]

The proof applies KKL to the cell indicator. The final Hidden Matching task lets the receiver select an edge from a supplied matching. Its success-probability conclusion has a different interface. The intermediate squared-bias claim is the direct useful antecedent. [Official journal PDF, pp. 633–635](https://theoryofcomputing.org/articles/v008a027/v008a027.pdf), [publication record](https://theoryofcomputing.org/articles/v008a027/).

### Fixed-alphabet consequence, derived here

If \(|\mathcal Z|\le2^b\), counting message cells gives

\[
\Pr\{\log_2(1/p_Z)>b+t\}\le2^{-t}\quad(t\ge0).
\]

Integration yields

\[
\mathbb E\log_2^2(1/p_Z)
\le b^2+\frac{2b}{\ln2}+\frac{2}{(\ln2)^2}.
\]

Averaging Claim 3.4 therefore gives
\(\mathbb E_Z\sum_{i<j}\beta_{Z,ij}^2=O(b^2)\) for \(b\ge1\).
For the matching lower order, retain the relative signs of \(m=\min(D,b+1)\) fixed coordinates using \(m-1\) bits. Every one of their \(\binom m2\) pair parities is determined. Dividing by \(\binom D2\) proves

\[
\sup_{|\mathcal Z|\le2^b}
\mathbb E_{Z,\{I,J\}}
 \left[\mathbb E(S_IS_J\mid Z)^2\right]
=\Theta\!\left(\frac{\min(b,D)^2}{D^2}\right).
\]

A private stochastic encoder cannot exceed this upper bound. Reveal its independent random seed to the decoder, condition on that seed, apply the deterministic bound and average. Revealing extra information only increases captured squared conditional mean. A deterministic relative-sign code supplies the lower bound.

A valid predictive interpretation on the cube first supplies uniform distinct indices \(I,J\), then draws a binary target with conditional mean \(\kappa S_IS_J\). Binary KL curvature on the bounded probability interval converts the preceding statement into the same quadratic payload order for log-loss gain. This corollary should be credited to the existing message-cell bound and elementary coding argument.

### What balance contributes

Independent signs cannot be substituted directly into the requested raw-endpoint law, because

\[
\sum_{x,y}\frac{1+\kappa S_xS_y}{D^2}
=1+\kappa\left(\frac1D\sum_xS_x\right)^2 .
\]

Balance ensures normalization and changes the zero-training pair correlations. The balanced source consequently requires centering by \(M_0\), its equality baseline and a slice concentration argument. The already indexed Sambale–Sinulis Theorem 1 supplies that concentration input. Its prior scoped reading is retained, without a repeated theorem audit. [Published source](https://doi.org/10.1007/s10959-021-01139-9).

## 4. Predictive KL and posterior quantization are established constructions

Let \(T\) be the training tape, \(W=(X,Y)\) a fresh pair, and \(Z\) the installed message generated from \(T\) with independent encoder randomness. The first endpoint \(X\) is uniform for every assignment, so it is independent of \(Z\). With \(Q_Z=P(W\mid Z)\), direct conditional likelihood identities give

\[
G(Z)-G_0
=I(Y:Z\mid X)
=I(W:Z)
=\mathbb E D_{\mathrm{KL}}(Q_Z\Vert Q_0).
\]

Here a colon denotes mutual information. If the full tape is retained, write \(Q_T=P(W\mid T)\). The loss incurred by compressing it to \(Z\) is exactly

\[
G(T)-G(Z)=\mathbb E D_{\mathrm{KL}}(Q_T\Vert Q_Z).
\]

These are the predictive relevance and conditional-distribution distortion of information bottleneck. Tishby, Pereira and Bialek give the objective in Eq. (15), the averaged predictive representative in Eq. (17), and the effective KL distortion after Theorem 4. Their joint law is supplied. Courtade and Weissman give the iid operational log-loss coding formulation and its single-observer information-bottleneck specialization in §III.F, Eq. (14). [Tishby et al., pp. 8–12](https://arxiv.org/pdf/physics/0004057v1), [Courtade–Weissman, §II, Lemma 1 and §III.F](https://people.eecs.berkeley.edu/~courtade/pdfs/CourtadeWeissman_TransITJan2014.pdf).

The relevant target is the fresh pair. Log-loss reconstruction of the latent partition would instead measure information about that partition and is a different task.

For the quadratic proxy, put \(U=ss^\top-M_0\) and \(M(T)=\mathbb E[U\mid T]\). Orthogonal projection gives the exact decomposition

\[
\mathbb E\|U-\mathbb E[U\mid Z]\|_F^2
=\mathbb E\|U-M(T)\|_F^2
 +\mathbb E\|M(T)-\mathbb E[M(T)\mid Z]\|_F^2.
\]

For fixed reconstruction matrices, a best encoder assigns \(M(T)\) to a nearest matrix. Each optimal reconstruction is its cell conditional mean. Thus finite-alphabet compression under this proxy is vector quantization of the random posterior matrix.

Doubchak, Philosof, Erez and Berman explicitly formulate finite \(L\)-index indirect quantization in Eqs. (1)–(3). Section I.C.1 and §IV.A, Claim 1, state estimate-then-quantize and the corresponding nearest-cell and centroid conditions, with historical attribution to Wolf–Ziv. Their displayed setup assumes joint densities. The finite discrete identity above follows directly from conditional expectation and needs no density assumption. Their threshold-constrained hardware design is an additional restriction. [2409.06839v1, pp. 1–3 and 8](https://arxiv.org/pdf/2409.06839v1).

This reduction does not give the distribution of \(M(T)\), an efficient way to compute it, or the requested dependence on \(D,n,\kappa,b\). Those are the problem-specific parts. No full posterior over assignments needs to be stored merely to forecast one fresh pair, although computing its sufficient predictive matrix can be expensive.

## 5. A mutual-information budget gives a different curve

This is an independent deduction for the exact balanced source.

Let \(C\) be the balanced partition modulo global reversal. It is uniform on

\[
K=\tfrac12\binom D{D/2}
\quad\text{classes},\qquad
h=\log_2K=\Theta(D).
\]

For \(0\le b\le h\), independently reveal \(C\) with probability \(p=b/h\). Otherwise output an erasure. Then

\[
I(C:Z)=ph=b\quad\text{bits}.
\]

The erasure leaves the original prior unchanged. A revealed partition gives the oracle fresh-pair law. If its additional gain is \(g_\star=\Theta(\kappa^2)\), the rare-reveal code earns exactly \(p g_\star\), hence

\[
G(Z)-G_0=\Theta(\kappa^2 b/D).
\]

The message alphabet has \(K+1\) values. For \(b\ll D\), it exceeds \(2^b\). This is a valid point under a mutual-information constraint and an invalid point under the request's installed-alphabet constraint.

Consequently the standard information-bottleneck single-letter optimization cannot be substituted for the fixed-\(b\)-bit storage problem. Its iid block-coding operational meaning allows information allocation across many independent source instances. The request has one shared partition and a worst-case installed alphabet at a particular cut. Ordinary data processing only gives \(I(C:Z)\le b\) from the cardinality constraint, not the converse.

## 6. What established SBM inference actually supplies

Mossel–Neeman–Sly **1202.1499v4** defines iid fair vertex labels and conditionally independent simple edges in Definition 1.1. The exact downloaded version is titled *Reconstruction and Estimation in the Planted Partition Model*. Theorem 2.1 gives asymptotic pair-label nonreconstruction when \((a-b)^2\le2(a+b)\) and \(a+b>2\). Theorem 2.4 gives contiguity below the strict threshold. Its proof overview exposes the classical overlap second-moment method. These are precise predecessors for the qualitative reconstruction obstruction. [Versioned source, pp. 2–8](https://arxiv.org/pdf/1202.1499v4).

Deshpande–Abbe–Montanari already make the posterior pair matrix \(\mathbb E[ss^\top\mid G]\) central. Eqs. (14)–(19) define normalized matrix MMSE and identify it with a relative-sign estimation error. Theorem 1.4 makes its limit equal to one below threshold, under the hypotheses of Theorem 1.1, including diverging average degree. The source uses iid labels. [Author manuscript, pp. 2–4](https://yash-deshpande.github.io/PAPERS/sbm_info.pdf), [1507.08685v1](https://arxiv.org/abs/1507.08685v1).

Neither leading asymptotic limit supplies the finite remainder
\(\Theta(n\kappa^4/D^2)\). The small gain can be positive while the normalized explained fraction tends to zero. Nor do these theorems impose a post-training \(b\)-bit message.

Banerjee–Ma study growing-degree simple-graph testing and likelihood-ratio fluctuations, with cycle contributions in Eq. (1.3). The source supplies a nearby route to finer asymptotics, rather than a result for the requested conditional Poisson tape and fresh log-loss objective. Only the introductory model and likelihood-ratio formula were examined here. [1705.05305v2, pp. 2–3](https://arxiv.org/pdf/1705.05305v2).

## 7. Graph rate-distortion, communication and training memory

| Source | Actual object and priced resource | Consequence for the request |
|---|---|---|
| Wafula et al., 2309.14464v1, §§II–III, Theorem 1 | Reconstruct the observed simple adjacency matrix under edge Hamming distortion. Conditional RDF supplies the community labels to both terminals. Unconditional and conditional values differ by an \(O(D)\) term | Graph reconstruction and fresh prediction have different distortions. The \(O(D)\) gap is already on the scale of a full partition |
| Rashtchian et al., COLT 2021, introductory models and result overview | Distributed communication, sketches and queries for planted clique, biclique and related matrix problems | A law-preserving reduction is required. These results do not price only the final installed message after unrestricted training |
| Garg et al., 2603.00770v1, Problem 1.2 and the general theorem framework | Working memory throughout a multipass stream that detects a planted submatrix, with a likelihood-ratio premise | A final one-bit decision can follow a computation using substantial working memory. Detection advantage and vanishing log-loss gain remain separate |
| Wu–Joudeh, 2510.08364v2, §II and Theorems 1–2 | Iid remote-source block coding and excess-log-loss error exponents with a rate-limited message | Blocklength counts independent source instances. It is not the number of observations under one shared unknown partition |

Primary sources: [Wafula et al.](https://arxiv.org/pdf/2309.14464v1), [Rashtchian et al. official proceedings](https://proceedings.mlr.press/v134/rashtchian21a.html), [Garg et al. versioned manuscript](https://arxiv.org/abs/2603.00770v1), [Wu–Joudeh v2](https://arxiv.org/abs/2510.08364v2).

These are useful neighboring models. No direct reduction to either requested complete law was established in the inspected passages.

## 8. Source editions and actual coverage

The main Pro-E reader examined the central source passages and integrated the comparison. Three temporary research assistants provided bounded source discovery and secondary comparison. Their additional coverage is labeled below. No source was independently certified in full, no formal proof replay was run, and no experiments or FP core files were changed.

| Edition | Actual coverage credited by this request |
|---|---|
| Karrer–Newman, PRE 83, 016107, 2011, 10-page final | Main reader: source identity and §II, especially printed p. 016107-2 and Eqs. (1)–(6). Original p. 2 visually checked. No full reading |
| Buhrman et al., ToC 8(27), 2012, 23-page final | Main reader: §§3.1.1–3.2 on printed pp. 633–636, including Claim 3.4 proof. Original physical p. 12 visually checked. Assistant additionally checked §2.1 KKL. Distinct from the existing 2011 conference row |
| Sambale–Sinulis, JTP 35, 2022 | Existing scoped Theorem 1 and quadratic-specialization record reused. No new full-paper coverage |
| Tishby et al., physics/0004057v1, 16 pages | Main reader: §§3.1–3.2, pp. 9–12, including the displayed variational proof. Assistant also checked the supplied-law premise on p. 8. Remaining paper unread |
| Courtade–Weissman, TIT 60(1), 2014, 22-page final | Main reader: §§I–II, physical pp. 1–3 including Lemma 1, and §III.F on physical p. 7. Assistant checked the Theorem 3 statement and reconstruction-alphabet discussion. Remaining proofs unread |
| Doubchak et al., 2409.06839v1, 14 pages | Main reader: §§I.A–I.C.1, pp. 1–3, and §IV.A Claim 1 on p. 8. Original p. 2 visually checked. No identification with the later 2026 journal edition |
| Mossel–Neeman–Sly, 1202.1499v4, 36 pages | Main reader and assistant: pp. 1–8, model and Theorems 2.1, 2.4, 2.5, with proof overview. Main proofs unread. Upgraded from abstract screening to scoped reading |
| Deshpande–Abbe–Montanari, 1507.08685v1, 41 pages | Main reader: author manuscript pp. 2–4, model, Theorems 1.1 and 1.4, Eqs. (14)–(20). Proofs unread. The later journal edition is not equated |
| Banerjee–Ma, 1705.05305v2 | Main reader: introductory model and Eq. (1.3), physical pp. 2–3. Proofs unread |
| Wafula et al., 2309.14464v1, 9 pages | Main reader: §§II–III through Theorem 1, pp. 2–4. Assistant additionally checked Theorem 2 and start of §IV-A. Proofs remain scoped |
| Rashtchian et al., PMLR 134, 2021, 28 pages | Main reader: introductory models and opening result overview, pp. 1–2. Assistant extended through the beginning of §1.2. No proof reading |
| Garg et al., 2603.00770v1, 81 pages | Main reader: abstract, introduction and Problems 1.1–1.2. Assistant examined the general theorem statements and information-cost definitions. Full proofs unread. Short STOC final authenticated only at metadata level |
| Wu–Joudeh, 2510.08364v2, 42 pages | Main reader: §II and §III statements on pp. 5–8. Proof sections unread |

Two ancillary communication leads were examined by the matching assistant: Ben-Aroya–Regev–de Wolf FOCS 2008, §4 Definitions 1–2, Lemma 6 and Theorem 7, and Doriguello–Montanaro *Quantum* 5:402, Definitions 6–7 and selected Theorems 24, 25, 32. They concern average absolute XOR bias and quantum/classical random-access interfaces. The main reader did not rely on their bounds to prove the squared-bias statement. Their source and reading scopes are retained in the index as assisted scoped reading. [0705.3806v2](https://arxiv.org/abs/0705.3806v2), [Quantum final](https://quantum-journal.org/papers/q-2021-03-07-402/).

Wolf–Ziv 1970 was identified through Doubchak's historical attribution. Its original proof was not retrieved. An unavailable Linder–Lugosi–Zeger lead supplies no evidence here.

## 9. Attribution and remaining boundary

The supportable attribution is:

> The source is a balanced fixed-total Poisson block model. Conditional pair-parity Fourier bounds already yield quadratic fixed-payload prediction on independent signs. Information bottleneck supplies predictive KL relevance, and indirect quantization supplies the posterior-mean compression reduction. The balanced-source reference correction and the finite acquisition law require their own stated derivations.

The bounded search covered targeted primary-source threads in Hidden Matching and random access, SBM reconstruction and matrix MMSE, graph rate-distortion, indirect quantization, information bottleneck and communication/streaming constraints. It extended the existing dated discovery record and did not repeat a global literature sweep. No examined theorem combines all of the requested sampling law, installed payload, fresh-pair distortion and finite learning regime.

The later one-observation graph-encoder and one-bit acquisition results now present in the core documents are outside the original request. This note does not claim a prior-art review of those subsequent statements. Astra retains the integration and research decisions.
