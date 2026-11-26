# Yu–Blanchard 2026: high-accuracy feasibility under finite persistent memory

## Edition, coverage and evidence status

**Jialin Yu and Moïse Blanchard. _Exponential memory/query-complexity tradeoffs in high-accuracy feasibility problems_. arXiv:2611.29320v1.** [Exact record](https://arxiv.org/abs/2611.29320v1), [PDF](https://arxiv.org/pdf/2611.29320v1), [TeX](https://arxiv.org/src/2611.29320v1).

Pro-A completed the **46-page edition in full** on 26 November 2026, Shanghai. The main reader personally covered the frontmatter, Sections 1–4, Appendices A–E, all active proofs, Algorithms 1–5, Game 1, both figures, all four numbered footnotes and the affiliation footnote, the AI disclosure and all 65 printed references. The active source consists of `main.tex`, `shortcuts.tex`, `transform_necessity.tex` and `geometric-configuration.tex`. Deleted `\comment{...}` blocks were excluded. The 92-record bibliography contains additional unprinted records, which are not credited as separately read papers.

Original PDF pages 7, 9–10, 20–21, 23–25, 31–34 and 41 were visually checked. Figure 1 is on physical page 7 and Figure 2 on physical page 33. Algorithms 1–4 are on pages 9–10, Game 1 on page 13 and Algorithm 5 on page 34. After the title page, printed page numbers are one less than physical page numbers. Prepared source files are under ignored `literature/corpus/arxiv/2611.29320v1/`.

The primary record lists only **v1, 22 November 2026 at 08:32:37 UTC**. The PDF frontmatter is dated 24 November. Its metadata explicitly says that Section 4.3 was revised to include shared randomness in the compression message. No v2 is inferred from that comment or the later PDF date. No conference or journal edition was authenticated.

The authors disclose AI assistance with Lemma 13's marginal density ratio, part of Lemma 16's transform analysis, and Lemma 14's Grassmannian density argument. They attribute the construction, reductions and information arguments to humans. The model is unidentified. This is an author statement, not an official OpenAI or Anthropic paper or an independent verification certificate.

A bounded secondary check covered Section 4.3's conditioning and channel-simulation interface, followed by the final randomized-algorithm wrapper. Another helper prepared primary dependency sources and checked the source/PDF inventory. The main reader examined the relevant source passages and assessed the resulting observations. No experiment, enumeration, proof-assistant replay or exhaustive theorem audit was performed. This note identifies a missing branch-information term, supplies two local mathematical repairs, and keeps the main theorem distinct from independent certification.

## 1. The resource model is an adaptive separation-oracle problem

An unknown convex set \(Q\subseteq B_d(0,1)\) contains a Euclidean ball of known radius \(\epsilon\). Given \(x_t\) in the unit ball, the oracle returns `Success` when \(x_t\in Q\), or a vector \(g_t\) satisfying

\[
g_t^\top(y-x_t)<0\qquad\text{for every }y\in Q.
\]

The oracle may be randomized, time-dependent and adaptive to the entire past. The target set remains fixed. An \(M\)-bit learner has a register in \(\{0,1\}^M\), a query map and a register-update map. Each round may use fresh independent randomness. Computation, arithmetic and temporary storage **within** a round are unrestricted. Only information retained **between** rounds is charged. Description length of the maps is not charged.

This model does not provide an iid observation stream, a fixed likelihood model or a fixed gradient field. Nor does it charge the computational cost of processing an exact real-valued oracle answer. These distinctions are essential when comparing its lower bound with learning or prediction.

### Theorem 1 as stated by the source

For sufficiently large \(d\), \(0<\epsilon\le e^{-d}\) and \(\delta\in[0,1]\), the source gives a memory/query tradeoff at the scale

\[
M=d^{1+\delta}\log_2(1/\epsilon),
\qquad
Q\ge
\bigl(d\ln(1/\epsilon)\bigr)^{\widetilde\Omega(d^{(1-\delta)/8})}.
\]

Equivalently, the query expression is \(\exp\{\widetilde\Omega(d^{(1-\delta)/8})\ln[d\ln(1/\epsilon)]\}\). The tilde hides powers of \(\log d\), not arbitrary functions of the accuracy. The guarantee concerns algorithms succeeding with probability at least \(2/3\) against every valid adaptive separation oracle. Deterministic learners can also be opposed by a suitable oblivious oracle. The randomized conclusion retains the adaptive oracle.

At linear persistent memory \(O(d\log(1/\epsilon))\), the exponent grows as \(\widetilde\Omega(d^{1/8})\). This is a worst-case query lower bound in a very high accuracy regime. It is not a wall-clock lower bound, a sample bound for passive data, or a statement that every convex objective demands this much memory.

The cited recursive cutting-plane upper bound uses roughly \(d^{1+\delta}\log(1/\epsilon)\) memory and \((d\log(1/\epsilon))^{O(d^{1-\delta})}\) queries. **Footnote 1 adds time consistency:** repeated identical queries must receive identical answers. Therefore the two displayed exponents should not be advertised as a tight comparison under identical randomized-oracle assumptions. Their dimension exponents also differ by the factor \(1/8\), beyond logarithmic slack. The cited `[BZJ24]` is officially **NeurIPS 2023**, volume 36, despite the source bibliography's 2024 year. [Official record](https://proceedings.neurips.cc/paper_files/paper/2023/hash/1395b425d06a50e42fafe91cf04f3a98-Abstract-Conference.html).

## 2. Why nested precision alone fails

Choose independent Haar subspaces \(E_1,\ldots,E_P\in\operatorname{Gr}(\widetilde d,d)\). The hidden feasible region is

\[
Q=B_d(0,1)\cap\{x:e_1^\top x\le-1/2\}
\cap\bigcap_{p=1}^{P}\{x:\|P_{E_p}x\|\le\epsilon\}.
\]

The halfspace excludes the trivial solution zero. With sufficiently small total subspace dimension, a norm-\(3/4\) vector in \(\operatorname{span}(E_1,\ldots,E_P)^\perp\) provides the center of an \(\epsilon\)-ball, with high probability.

A one-layer oracle can reveal progressively more precise noisy versions of its subspace. A naive multilayer oracle would repeat all second-layer precision levels each time the first layer advances, hoping to multiply the number of required queries. The paper explains why a previously stored near-solution can defeat this multiplication. A vector almost perpendicular to both earlier layers remains close to their new intersection. Restricting the current uncertainty to that vicinity multiplies the precision gains, allowing many second-layer phases to be skipped.

Appendix B illustrates an \(O(N\log N)\) strategy against a naive two-layer construction and sketches \(O(N(\log N)^{P-1})\) for more layers. Its explanation uses general-position and idealized precision assumptions and is expressly informal. It is a useful warning about retained geometric information, not a separately certified finite-bit algorithm for every nested oracle.

The new construction exploits a weaker requirement on each separator. A later layer only needs to separate points that passed the earlier layers. It can therefore introduce **anisotropic** uncertainty that would be illegal on the entire unit ball. Stretching the earlier narrow directions turns this admissible uncertainty into an approximately isotropic subspace distribution. Figure 1 makes this distinction explicit.

## 3. Skeleton, scales and the simultaneous transform bound

Set

\[
\widetilde d=\left\lfloor\frac d{36P}\right\rfloor,
\quad N_p=\left\lfloor\frac{\log_2(1/\epsilon)}{2Pp\log_2d}\right\rfloor,
\quad\lambda_p=d^{-p},
\quad\delta_p^{(i)}=d^{-1}\epsilon^{(p-1)/(2P)}\lambda_p^i.
\]

`NoiseAddition` builds a reverse Markov sequence: start at the exact transformed subspace, then sample successively coarser subspaces uniformly in maximum-principal-angle balls. The tree's layer-\(p\) nodes have indices in \([N_1]\times\cdots\times[N_p]\). A parent \(v\) has transform \(\mathcal T_v\) and dual transform \(\mathcal H_v=\mathcal T_v^{-\top}\). Its next noisy sequence approximates \(\mathcal H_v(E_p)\). A child at precision \(i\) stretches the preceding approximate normal subspace by \(1/\delta_p^{(i-1)}\).

All hidden subspaces and the entire skeleton are sampled before interacting with the learner. The adaptive oracle keeps a current leaf in lexicographic order. It checks the halfspace and then the transformed subspace tests along that path. If all tests pass, the same query is tried against the next leaf. After all leaves are exhausted, an ordinary valid separation oracle can be used. When a transformed normal is \(g\), its original-coordinate normal is \(\mathcal T_v^\top g\), as Footnote 3 states.

Two distinct geometric statements support this mechanism:

- With probability at least \(1-e^{-d/300}\), the hidden region contains the promised ball and every generated separating answer is valid.
- With probability at least \(1-2Pe^{-d/288}\), all relevant transforms simultaneously satisfy
  \[
  1\le\sigma_{\min}(\mathcal T_v)
  \le\sigma_{\max}(\mathcal T_v)
  \le\frac2{d\delta_p^{(0)}}
  \qquad(v\text{ at layer }p-1).
  \]

The second assertion is not obtained by multiplying all worst-case condition numbers along a path. Appendix D proves a uniform transform-process lemma. For contractions

\[
\mathcal H_p=T_{U_p,\delta_p}\cdots T_{U_1,\delta_1},
\qquad T_{U,\delta}=P_{U^\perp}+\delta P_U,
\]

the next direction \(U_p\) approximates the already-transformed fresh Haar subspace \(\mathcal H_{p-1}(V_p)\). If \(\delta_1<1/7\), \(\delta_{p+1}\le\delta_p/36\) and \(36P\widetilde d\le d\), then

\[
\sigma_{\min}(\mathcal H_p)\ge\delta_p/2
\]

on an event depending only on the original \(V_1,\ldots,V_P\). It holds for all allowed contraction factors and noise choices on that event.

The proof writes the cumulative direction span as \(\operatorname{span}[Q_1+D_1,\ldots,Q_p+D_p]\), with \(\|D_j\|_{\mathrm{op}}\le\delta_j/2\). Gaussian singular-value estimates control the unperturbed span and its overlap with a new subspace. A Woodbury update for \((\mathcal H_p^\top\mathcal H_p)^{-1}\) then shows that the most recent contraction sets the relevant scale. Sharing this event across the entire skeleton avoids an impossible union bound over exponentially many leaves. This simultaneous quantifier is a useful mathematical instrument in its own right.

## 4. Information-limited memory propagates a blocking property

For a random region \(R\) and information \(C\), the statement

\[
R\text{ is }\Delta\text{-}\operatorname{Block}_k(q\mid C)
\]

means that **every \(C\)-measurable \(k\)-dimensional subspace \(W\)** satisfies

\[
\Pr\{R\cap(W+\Delta B)=\varnothing\}\ge q.
\]

This is an unconditional probability statement quantified over measurable selection rules. It does not assert the same bound separately at every realized context. Confusing these quantifiers would invalidate the later threshold argument.

For a child \(w=v\mathbin\Vert i\) at layer \(p\), the context \(C_w\) includes the relevant earlier and coarser subspaces. Well-behavedness means

\[
I(E_w;\operatorname{Mem}_v\mid E_{>p},C_w)\le4M/N_p.
\]

The information chain rule distributes the \(M\)-bit memory over many precision levels. A majority of children of a well-behaved parent satisfy both this constraint and

\[
I(E_w;E_v\mid E_{v,p}^{(<i)},\operatorname{Mem}_v,C_v,E_{>p})
\le\frac{16M}{N_pN_{p-1}}.
\]

The second inequality is important. Conditioning on memory can correlate hidden subspaces that were independent before that conditioning. The reduction pays for that induced correlation rather than treating it as zero.

The propagation theorem transfers blocking from the parent to at least half of its children, losing \(1/P\) in blocking probability. Its admissible range has the form

\[
C_b\frac{M/N_p+P}{\widetilde d}\,P\log P\log(d/\Delta)
\le k\le
\frac{\widetilde d}{C_bP\log(d/\Delta)\log d},
\]

with

\[
\lambda_p\le\Delta'\le
c\frac\Delta k\left(\frac{\widetilde d}{d}\right)^{3/2}.
\]

First-layer blocking starts at probability \(1-1/(2P)\). Setting \(\Delta=\lambda_{p-1}\) and \(\Delta'=\lambda_p\) leaves probability \(1/(2P)\) after the last layer and at least

\[
N_1\prod_{p=2}^{P}(N_p/2)
\]

good leaves. The parameter choice

\[
P=1+\left\lceil\left(
\frac{c_0d^2\log(1/\epsilon)}{M\log^5d}
\right)^{1/8}\right\rceil,
\qquad
k=\left\lfloor\frac d{72C_bP^3\log^2d}\right\rfloor
\]

balances these inequalities. The eighth root comes from this coupled geometric and information budget. It is not claimed to be an optimal memory exponent.

## 5. Compression reduction and its actual randomness cost

In Game 1, the encoder observes a noisy subspace sequence through its current member \(E^{(i)}\), while the decoder only has a message and the coarser sequence \(E^{(<i)}\). The decoder must output \(k\) nonzero vectors that are nearly perpendicular to a contracted version of \(E^{(i)}\) and robustly independent of their predecessors.

If a good child region could be approached by a context-measurable low-dimensional space, the encoder could repeatedly resample compatible parent subspaces. One-shot exact channel simulation allows the decoder to reconstruct each sample from shared fresh randomness plus a prefix-free message. The conditional mean length is bounded by

\[
2I(E_w;E_v\mid\operatorname{Mem}_v,\widetilde C_v)+6,
\]

which is at most \(32M/(N_pN_{p-1})+6\) after averaging over the context. It is **not** asserted to hold uniformly for every context.

Each successful resample yields a point in the child region near a \(k\)-dimensional space. The encoder stores a nearby net point using at most \(2Pk\log d\) bits. It accepts a point only when it lies well away from the span of earlier accepted points.

Let \(P(C)\) be the conditional probability that a fresh resample both cuts the relevant region and avoids any previously selected low-dimensional span. The paper first obtains \(\mathbb E P(C)>1/(2P)\). Appendix D's threshold lemma then selects an event \(A\) with

\[
P(C)\ge p_*,
\qquad p_*\Pr(A)\ge\frac1{6P\ln(6P)}.
\]

This controls the waiting time for \(k\) accepted samples. Conditional iid resampling, a stopping-time argument and Wald's identity control the expected total channel-message length. Index codes and net-point codes complete the finite payload. The event may depend on the hidden subspace through the context, so its branch identity also carries information.

### 5.1 Independent accounting clarification and the missing branch bit

The revised source explicitly adds shared randomness \(R\) to `Message` on the successful branch. Write \(X=E_w\), \(B=\operatorname{Mem}_v\), \(C=\widetilde C_v\), let \(A\in\{0,1\}\) identify success, and let \(D\) be the finite payload, empty on failure. One can sample a full independent random tape in advance even on executions that will not use it. Then \(R\perp(X,B,C,A)\), and the actual message is a function of \((B,R,A,D,C)\). Therefore

\[
\begin{aligned}
I(X;\operatorname{Message}\mid C)
&\le I(X;B,R,A,D\mid C)\\
&\le I(X;B\mid C)+H(A\mid B,C)
 +\Pr(A=1)H(D\mid B,C,R,A=1).
\end{aligned}
\]

The conditional payload entropy is bounded by its prefix-free length. This argument charges any synergy between the fresh tape and payload. It does **not** assume \(I(X;R\mid B,C,D)=0\), which is generally false.

The first line of the source's equation (4.11), physical page 25, omits the branch term. The unsuccessful message contains only \(B\), whereas the successful tuple reveals additional fields. The displayed code-length argument does not establish a prefix-free joint encoding of these two branches or that the branch is determined by \((B,C)\). A safe bound adds

\[
H(A\mid B,C)\le1\text{ bit}.
\]

Let \(a=\Pr(A=1)\) and \(K_0=6P\ln(6P)\). Since \(a\ge1/K_0\), the correction satisfies \(1\le K_0a\). In Lemma 12's bound, replacing the internal term \(6k\) by \(6k+1\), or more coarsely by \(7k\), absorbs it while retaining the essential form

\[
I(E^{(i)};\operatorname{Message}\mid E^{(<i)},\mathcal T)
\le\widetilde M_{\mathrm{repaired}}\,a.
\]

The later fixed-\(\mathcal T\) selection still works: averaging the information minus a multiple of the conditional success probability produces a realization with success at least \(1/[12P\ln(6P)]\) and information at most twice the repaired coefficient times its own success probability. This is an explicit local accounting omission with a constant repair, not a counterexample to the asymptotic lower bound. No claim is made that every printed numerical constant survives without adjustment.

### 5.2 Independent geometric repair preserving the original constant

In Lemma 8, the source establishes \(\|x-z\|\le2\Delta'\), then uses \(\|x\|\ge\|z\|-\Delta'\). The latter does not follow from the displayed bound. It can be repaired using the geometry already present in the construction.

The point \(z\) is within \(\Delta'\) of \(W\), and \(x\in W\) is its nearest net point. Since \(z-P_Wz\perp W\) and \(P_Wz\) lies inside the covered ball,

\[
\|x-z\|^2
=\|x-P_Wz\|^2+\|P_Wz-z\|^2
\le2(\Delta')^2.
\]

Thus the perpendicularity numerator is at most \((1+\sqrt2)\Delta'\), using \(\lambda_p\le\Delta'\), while

\[
\|x\|\ge\frac12-\sqrt2\Delta'
\ge\frac{4-\sqrt2}{8}
\qquad(\Delta'\le1/8).
\]

Consequently

\[
\frac{\|P_{\widetilde E}x\|}{\|x\|}
\le\frac{8(1+\sqrt2)}{4-\sqrt2}\Delta'
<8\Delta'.
\]

This retains the source's \(\beta=8\Delta'\) over its existing parameter range. No extra \(\Delta'\le1/16\) restriction is needed. The robust-independence inequality also remains valid with this stronger distance estimate. This elementary derivation is independent of the paper's missing norm step.

## 6. Why successful compression must disclose substantial information

Lemma 13 compares the conditional law of \(E^{(i)}\), given all coarser versions, with a uniform Grassmannian ball. Its ingredients are reverse-Markov conditioning, invariance of the noise kernel, and the angular central Gaussian density of a linearly transformed Haar subspace. A controlled condition number bounds the density ratio. The source proves this comparison rather than assuming that a posterior remains Haar uniform.

Lemma 14, proved in Appendix E, gives the geometric small-ball estimate. If \(E\) is uniform in a maximum-angle ball of radius \(\alpha\le1/d\) about \(E_0\), and \(F=T_{E_0,\rho\alpha}(E)\) with \(\rho\ge1\), then for fixed \(W\in\operatorname{Gr}(k,d)\),

\[
\Pr\{\|P_WP_F\|_{\mathrm{op}}\le b\}
\le\left(C_0b\rho\sqrt{d/\widetilde d}\right)^{k\widetilde d}.
\]

The proof uses the graph chart \(E=\operatorname{span}\binom{I}{\tan(\alpha)Z}\). On the small chart, its density is within a constant of uniform measure on an operator-norm matrix ball. A Haar orthogonal block represents that uniform measure. The density of its first \(k\) rows is bounded by \((C\sqrt d)^{k\widetilde d}\), and a translated small matrix ball has volume at most \((Cb\rho/\sqrt{\widetilde d})^{k\widetilde d}\). The exponent is the number of constrained matrix coordinates, not merely the number of output vectors.

The source then uses the robust-vector extraction argument in the proof of Blanchard's 2024 Lemma 13, which itself invokes Lemma 14. From \(k\) robustly independent approximate-perpendicular vectors it constructs

\[
r=\left\lceil\frac{k}{1+\log(\sqrt d/\gamma)}\right\rceil
\]

orthonormal vectors with controlled projection. Under the product law that decouples the decoded space and hidden subspace, the perpendicularity event has probability at most \(e^{-r\widetilde d}\). Data processing to this binary event yields information of order \(\xi r\widetilde d-O(1)\) for success probability \(\xi\). The source's logarithm convention is base two, while the small-ball probability is written exponentially in base \(e\). Using \(\log_2(e)>1\) only makes the stated coarser lower bound weaker.

The information upper and lower bounds contradict one another in the propagation theorem's parameter range. This explains why conditional resampling and an adaptive success threshold were needed: the upper bound must scale with the same actual success probability as the lower bound.

## 7. Leaf counting and a finite randomized-algorithm wrapper

For a good leaf \(\ell\), let \(\mathcal E_\ell\) mean that the oracle reaches that leaf and the first query checked there immediately passes it. Blocking bounds its probability by \(1-1/(2P)\). Removing the small invalid-oracle event gives a probability at least \(1/(4P)\) of a chargeable leaf. Summing over the many good leaves gives the expected query lower bound.

**A necessary premise is eventual verified success.** A leaf never reached is also in \(\mathcal E_\ell^c\). For a learner that can stop unsuccessfully, it cannot automatically be charged as a query. When the learner always reaches a verified `Success` on a valid instance, all leaves are exhausted. Each non-skipped leaf then accounts for a distinct query that returned a separating answer. This supplies the required counting interpretation.

The source mentions both bounded-horizon gradient-descent fallback and unlimited fresh restarts. It does not combine them into one explicitly bounded-horizon learner before fixing the random tape. Unlimited restarts alone have an unbounded worst-case clock, so the preceding \(M+\lceil\log T\rceil\) simulation cannot be applied to that entire process without clarification.

The following **conditional local repair** makes both requirements hold at once. Suppose a deterministic fallback uses \(G=O(\epsilon^{-2})\) queries and \(S_G=O(d\log(1/\epsilon))\) bits in the same model, as the source assumes. Let \(\tau=T+1\) account for verifying the output of a \(T\)-query learner. If \(\tau\ge G\), use the fallback directly. Otherwise run at most

\[
K=\left\lceil\log_3(G/\tau)\right\rceil
\]

fresh attempts, resetting learner memory but not the oracle, then use the fallback. Against every valid adaptive continuation, each attempt's conditional failure probability is at most \(1/3\). Independence of the success events is unnecessary. Therefore

\[
\mathbb E Q_{\mathrm{wrapper}}
\le\tau\sum_{j=0}^{K-1}3^{-j}+G3^{-K}
\le\frac52(T+1).
\]

Its deterministic maximum horizon satisfies

\[
H\le K\tau+G=O(G),
\]

because \(x\log_3(1/x)\) is bounded for \(x=\tau/G\in(0,1)\). Thus \(\log H=O(\log(1/\epsilon))\), and sequential reuse of registers gives

\[
M'=\max(M,S_G)+O(\log H)=O(M)
\]

in the paper's memory regime. The wrapper always succeeds on valid instances and has a finite horizon. Fixing its random tape means hardwiring that tape into the uncharged query/update maps and storing a round counter. It does **not** mean fitting the entire tape into \(\log H\) working bits.

The same pre-sampled skeleton distribution and adaptive oracle rule are used before and after fixing the tape. Averaging the deterministic lower bound over independent tapes is then legitimate. One must not instead select a different oblivious oracle after seeing each tape and average those learner-dependent choices.

This repair loses only constants in expected queries and memory, preserving the stated tilde-asymptotic scale. It relies on verified success, the guarantee against every valid adaptive continuation, and the cited finite-bit fallback. The latter implementation was not independently audited here. This is a completed wrapper derivation under explicit interfaces, not whole-proof certification.

## 8. Primary dependencies checked at scoped depth

**Li and El Gamal 2018, _Strong Functional Representation Lemma and Applications to Coding Theorems_, IEEE TIT 64(11):6967–6978, DOI [10.1109/TIT.2018.2865570](https://doi.org/10.1109/TIT.2018.2865570).** [Author-hosted journal PDF](https://isl.stanford.edu/~abbas/papers/Strong%20Functional%20Representation%20Lemma%20and%20Applications%20to%20Coding%20Theorems-journal.pdf). The source's bibliography key `Li2017ContinuousCommu` denotes this journal paper, not a separate 2017 result with that name. Theorem 1's conditional form and Section III support exact channel simulation with shared randomness and average prefix-code length at most \(I+\log_2(I+1)+5\), hence the coarser \(2I+6\). The conditioning variable must be known to **both** parties. Decoder-only side information is a different interface, explicitly excluded from this direct application. The main reader checked the theorem and conditional discussion on printed page 6968 and all of Section III on pages 6969–6970. The proof of Theorem 1 and the remainder of this 12-page journal edition are unread. The local primary PDF is `literature/corpus/peer_reviewed/li_el_gamal2018_tit_strong_functional_representation.pdf`. The journal edition is not silently replaced by the earlier arXiv v4.

**Blanchard 2024, _Gradient Descent is Pareto-Optimal in the Oracle Complexity and Memory Tradeoff for Feasibility Problems_, FOCS 2024, pp. 2413–2435, DOI [10.1109/FOCS61266.2024.00141](https://doi.org/10.1109/FOCS61266.2024.00141).** [Official proceedings PDF](https://ieee-focs.org/FOCS-2024-Papers/pdfs/FOCS2024-1oojWxXs5YAKfs3z3lBRMF/167400c413/167400c413.pdf), [arXiv v1](https://arxiv.org/abs/2404.06720v1). The required extraction statement is Lemma 14. Yu's text correctly refers to the **argument in the proof of Lemma 13**, where that lemma is applied. This is not a numbering error. The main reader checked the formal statement and that proof's initial application through equation (15), on physical page 15, printed page 2427, and the edition outline on printed page 2416. The 23-page proceedings omits the extraction lemma's proof and directs readers to arXiv. The separate 64-page arXiv v1 contains it in Appendix B, which was located but not read. The local official PDF is `literature/corpus/peer_reviewed/blanchard2024_focs_gradient_descent_pareto.pdf`. No full FOCS or arXiv reading, nor independent certification of the imported extraction lemma, is claimed.

The source also invokes Harsha–Jain–McAllester–Radhakrishnan's 2010 correlation communication theorem, classical Gaussian and Grassmannian density results, and the historical memory-independent separation-oracle lower bound. Their roles were followed in this paper, but their complete originals were not separately read. No historical full-reading queue is implied.

## 9. What is and is not established for FP

The independently useful instruments are the simultaneously controlled sequence of transformed random subspaces, context-dependent blocking against every measurable low-dimensional selector, exact conditional channel simulation with correctly charged branch information, and the bounded restart/fallback conversion. They have explicit inputs and resource assumptions.

No FP transfer is proposed. A transfer would need an actual reduction from a prediction or state-formation problem to these valid adaptive separation queries, with the same retained-bit budget, accuracy interpretation and source of randomness. The present note supplies none. Arbitrarily precise real oracle answers, unlimited within-round computation, adversarially selected separators and the exceptionally high-accuracy regime cannot be silently replaced by ordinary token prediction.

The paper's statement is a new preprint theorem claim whose full argument has been read. The bounded checks reveal local missing accounting and exposition, with the repairs above. They do not refute the main asymptotic theorem, and they also do not certify every geometric, measurability, imported or implementation step. No FP definition, architecture, experiment or core research file was changed.
