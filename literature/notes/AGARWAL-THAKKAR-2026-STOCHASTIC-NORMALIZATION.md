# Agarwal–Thakkar 2026: completion weights and stochastic normalization

## Source, edition and reading boundary

**Smayan Agarwal and Aalok Thakkar, _Localising Stochasticity in Weighted Automata_, arXiv:2602.23805v2, revised 3 October 2026.** [Primary history](https://arxiv.org/abs/2602.23805v2) · [PDF](https://arxiv.org/pdf/2602.23805v2) · [TeX](https://arxiv.org/src/2602.23805v2) · [FSTTCS 2026 accepted list](https://www.fsttcs.org.in/2026/papers.php).

Pro-A completed this 20-page edition on 26 November 2026, Shanghai. The main reader covered the entire active `main.tex`, Sections 1–9, Appendices A–C, every statement and proof, Algorithm 1, both original figures, front matter and all 20 printed references. PDF pages 1, 7, 9–13 and 18–20 were visually inspected. The bibliography database contains additional unused entries, which are not counted as printed references. No separate scientific footnotes were found.

The official conference list authenticates acceptance. The arXiv PDF prints DOI `10.4230/LIPIcs.FSTTCS.2026.15`, volume 400, article 15. The December conference is still in the future at the reading date. A separately retrieved final proceedings edition is not claimed. V1 is a distinct unread edition. No AI-use statement was found in the inspected manuscript, which does not establish actual use.

A secondary reader performed a bounded check of Section 8 and Appendix C, assessed by the main reader. The main reader checked the real normalization, local/global distinction, state-elimination update, printed examples and the cross-paper consequence below. These are mathematical source checks and explicit small counterexamples. No exhaustive search, numerical replication, formal proof replay or certification of all cited dependencies was performed.

## 1. The main usable result

For a nonnegative weighted automaton, use row-vector notation

\[
f_A(w)=\alpha M_w\mu,\qquad M=\sum_{a\in\Sigma}M_a.
\]

The paper's generative local condition is

\[
\alpha\mathbf1=1,\qquad M\mathbf1+\mu=\mathbf1.
\]

At each state, one either emits a letter and moves, or terminates. This differs from an input-driven probabilistic automaton, where each separate letter matrix is stochastic or substochastic.

**Proposition 11 and Theorem 19.** Suppose the supplied automaton is finite, trim and nonzero, with nonnegative weights and finite total finite-word mass

\[
0<Z=\sum_w f_A(w)<\infty.
\]

Then \(\rho(M)<1\), and the actual completion vector is

\[
d=(I-M)^{-1}\mu=\sum_{k\ge0}M^k\mu>0,
\qquad Z=\alpha d.
\]

With \(D=\operatorname{diag}(d)\), define

\[
\alpha'=\alpha D/Z,\qquad M'_a=D^{-1}M_aD,
\qquad \mu'=D^{-1}\mu.
\]

The new automaton has the same state set, satisfies the local condition, and has

\[
f_{A'}(w)=f_A(w)/Z,\qquad \sum_w f_{A'}(w)=1.
\]

The proof has two separate parts. The completion equation \(Md+\mu=d\) gives the local row identities. Along every run, the diagonal factors cancel, giving the exact word identity and hence global mass one. Normalization is a change of coordinates using supplied model parameters. It does not discover the smallest representation or learn it from strings.

Trimness matters in the spectral characterization. An unreachable or non-coaccessible unstable component can have spectral radius at least one without contributing to \(f_A\). Remove such states before invoking Proposition 11. The nonzero qualification excludes the empty trim automaton, for which division by \(Z\) is undefined.

### Computing completion weights by strongly connected components

Order the SCC blocks so that transitions leave a block only for a later block. In reverse order compute

\[
\varepsilon_i=\mu_i+\sum_{j>i}M_{ij}d_j,
\qquad d_i=(I-M_{ii})^{-1}\varepsilon_i.
\]

Algorithm 1 implements this recursion and then rescales all entries. Its stated \(O(n^3+n^2|\Sigma|)\) bound counts arithmetic operations. Block inversions cost \(\sum_i n_i^3\le n^3\). This is not a demonstrated bit-complexity or numerical-conditioning guarantee. In particular, a pole close to one can produce large completion weights. The SCC sentence in the printed proof understates dense edge inspection, but charging it to the already present \(O(n^2|\Sigma|)\) term preserves the overall arithmetic bound.

## 2. Local normalization and termination are different assertions

Under Definition 1 alone, a locally stochastic nonnegative automaton need not have total finite-word mass one. For the one-state machine

\[
\alpha=1,\qquad M_a=1,\qquad\mu=0,
\]

the local identity holds, but every finite word has weight zero. All probability follows an infinite run. Mixing a terminating branch with this branch yields any prescribed finite-word mass strictly between zero and one.

Consequently, the broad PA-to-stochastic-expression wording in Theorems 21–22 needs a proper-termination qualification, or restriction to trim nonzero locally stochastic machines over the nonnegative reals. For a finite trim locally stochastic machine, every state reaches a positive stopping weight. A fixed finite horizon therefore has a uniform positive probability of termination, implying \(\rho(M)<1\) and eventual termination with probability one.

**This qualification does not damage Theorem 19.** That theorem constructs its normalization from the actual finite completion sum, which directly establishes global mass one.

Similarly, deleting the final vector does not leave a standard row-stochastic labelled Markov chain: the transition row sum is \(1-\mu(q)\). It leaves a killed or substochastic process. A conventional Markov-chain representation needs explicit termination or an absorbing completion of the model.

## 3. What the expression constructors require

Sections 3–4 introduce atoms, weighted choice, Cauchy product and a guarded discounted star. The unrestricted grammar is broader than the normalized subclass. Its mass-one invariant applies when choice coefficients sum to one and the star's closure equation is solvable.

The source star performs **at least one** copy. Over the nonnegative reals,

\[
r_t^*(w)=\sum_{k\ge1}t^{k-1}(1-t)
\sum_{w=w_1\cdots w_k}\prod_{i=1}^kr(w_i),
\quad 0\le t<1,
\]

where \(r\) is normalized and \(r(\varepsilon)=0\). In particular, \(r_t^*(\varepsilon)=0\). The normalized distribution of zero or more repetitions is instead

\[
G_t(r)=(1-t)\delta_\varepsilon+t r_t^*.
\]

For the abstract semiring version, the stop coefficient \(e\) solves \(t^*e=1\). The star proof sums each intervening word function to one in its original position. It does not commute \(t\) through a noncommutative weight, so distributivity is enough for that step. Rearrangement of the indexed sums still needs the stated complete-sum structure or an appropriate summable domain.

The ordinary finite nonnegative reals are not complete for arbitrary countable sums without adjoining infinity. Likewise \(\mathbb R\cup\{+\infty\}\) under min-plus does not contain the infimum of an unbounded-below family. The concrete finite-mass and no-negative-cycle arguments use existing closures and avoid these unrestricted completeness claims.

Appendix B gives a Thompson construction with \(O(|r|)\) states, initially allowing epsilon transitions. Guardedness makes its positive epsilon graph acyclic. With \(E=(I-M_\varepsilon)^{-1}\), replacing \(M_a\) by \(EM_a\) and \(\mu\) by \(E\mu\) removes epsilon transitions without adding states. The identity

\[
E\left(\sum_aM_a\mathbf1+\mu\right)
=E(I-M_\varepsilon)\mathbf1=\mathbf1
\]

preserves local stochasticity. The concatenation description can be implemented by an epsilon connection between distinct endpoints, avoiding its ambiguous simultaneous wording about identifying endpoints and adding an edge.

## 4. Two concrete corrections to state elimination

### Use the current generalized loop

Theorem 21 initializes expression-labelled edges, then writes the eliminated state's loop mass as

\[
s_k=\sum_\sigma M_\sigma(q_k,q_k).
\]

This is the original one-letter self-loop mass. Earlier eliminations create new multi-letter return loops, which must be included.

For an explicit proper trim machine, start at \(q_1\), let

\[
q_1\xrightarrow{a,1/2}q_2,\qquad
q_2\xrightarrow{b,1/2}q_1,\qquad
\mu(q_1)=\mu(q_2)=1/2.
\]

Both original self-loop masses are zero. Eliminating \(q_1\) creates at \(q_2\) a `ba` loop of weight \(1/4\). Continuing with the original value \(s_2=0\) discards it and loses `aba`, whose actual probability is \(1/16\).

The update must use the current expression \(R_{kk}\):

\[
s_k=\|R_{kk}\|,\qquad L_k=R_{kk}/s_k,
\]

and the zero-or-more loop series is

\[
\delta_\varepsilon+\frac{s_k}{1-s_k}(L_k)^*_{s_k}
=\frac{G_{s_k}(L_k)}{1-s_k}.
\]

Use the identity term alone when \(s_k=0\). For a proper finite machine, elimination preserves finite completion sums, and the current loop has mass below one. Intermediate scalar sums must be regrouped by their actual masses to give normalized expression choices. This repairs the specific update defect. It is not evidence that stochastic regular expressions cannot characterize proper rational distributions.

### The printed examples omit the zero-loop branch

Figure 1 has completion weights, in order \(q_0,\ldots,q_5\),

\[
d=(28,10,25,3,1,3).
\]

They give the four initial branch probabilities \(4/28,15/28,6/28,3/28\). Figure 2 depicts only the first branch, with mass \(4/28\), rather than a complete mass-one machine.

Let

\[
R=\frac4{19}\delta_{ab}+\frac{15}{19}\delta_a.
\]

Equation (2) uses \(R^*_{19/25}\) after the initial `ab`. Because this star requires at least one iteration, it loses the direct exit word `abab`, whose correct branch probability is

\[
\frac4{28}\frac6{25}=\frac6{175}.
\]

The branch expression should be

\[
\frac4{28}\delta_{ab}\,G_{19/25}(R)\,\delta_{ab}.
\]

Equation (3) has the same issue for the full machine. In particular its final term uses \((\delta_b)^*_{1/3}\), excluding `aa`. The actual normalized weight of `aa` is \(2/28=1/14\). A corrected complete expression is

\[
\frac{19}{28}R\,G_{19/25}(R)\,\delta_{ab}
+\frac6{28}\delta_{ab}
+\frac3{28}\delta_a\,G_{1/3}(\delta_b)\,\delta_a.
\]

This also restores `aab` with probability \(9/70\). These exact hand calculations check the displayed examples. They do not require numerical experimentation or invalidate completion-weight normalization.

## 5. General conjugation, Viterbi and tropical scope

**Theorem 10** is an abstract conjugation theorem over a complete commutative semiring, with actual closure vector \(d=M^*\mu\), and with \(d(q)\) and \(Z\) invertible inside the semiring. Its telescoping proof is valid under those premises. The specialized constructions sometimes use external real division or subtraction instead.

For the Viterbi semiring \(([0,1],\max,\times)\), a number below one has no multiplicative inverse inside the set. The assertion after Theorem 10 that invertibility is automatic for Viterbi is therefore too broad. Appendix C's Remark 43 explicitly recognizes this issue.

**The specialized Appendix C proof survives.** Take actual best completion values

\[
d(q)=\max_{w,\text{ runs from }q}\operatorname{weight}(w),
\qquad Z=\max_q\alpha(q)d(q).
\]

For a nonempty trim machine, deleting a cycle cannot lower its run weight, so a best run is attained without a repeated state. The Bellman inequalities bound every numerator in the real quotient construction by its denominator. Thus all normalized transition, initial and final weights remain in \([0,1]\), and telescoping preserves every word value up to \(Z\). This is a specialized proof with external quotients, not a direct application of internal invertibility.

For min-plus, first subtract the finite minimum cycle mean \(\gamma\) from every finite transition. There are then no negative cycles. Actual least completion costs \(d(q)\) and

\[
c_0=\min_q\{\alpha(q)+d(q)\}
\]

are finite and attained on simple paths. Theorem 28 uses potentials

\[
\alpha'(q)=\alpha(q)+d(q)-c_0,
\quad M'_a(q,q')=M_a(q,q')-\gamma+d(q')-d(q),
\quad\mu'(q)=\mu(q)-d(q).
\]

They yield local minima zero and the exact identity

\[
f_A(w)=|w|\gamma+c_0+f_{A'}(w).
\]

The cycle-mean part requires a finite-cost cycle. For an acyclic machine, choose no growth correction and use the actual minimum word cost. This gives local and global normalization, but its empty-set cycle mean is \(+\infty\), not zero.

**Actual completion values cannot be replaced by an arbitrary Bellman fixed point.** A trim one-state Viterbi machine with \(\alpha=1,M_a=1,\mu=1/2\) is locally max-normalized, yet every word has value \(1/2\). Its Bellman equation has many solutions, while the actual completion value is \(1/2\). The min-plus counterpart \(\alpha=0,M_a=0,\mu=1\) has local minima zero but minimum finite-word cost one. These examples qualify a generic local-to-global inference. They leave the specialized constructions from true completion values intact. Max and min semantics here describe optimal runs, not sampling distributions.

## 6. Removing growth changes the word law

Section 7 covers nonnegative automata of infinite total mass. When \(\rho(M)>0\), choose \(\zeta=(1+\epsilon)\rho(M)\), with \(\epsilon>0\), and replace \(M_a\) by \(M_a/\zeta\). The discounted automaton has spectral radius below one. After finite-mass normalization,

\[
f_A(w)=\zeta^{|w|}Zf_{A'}(w).
\]

This separates a length-dependent growth factor from a proper stochastic component. It does not preserve the original distribution over lengths. If \(\rho(M)=0\), the finite nonnegative transition graph is acyclic after zero edges are removed, and the finite-mass route applies directly. No learning, approximation-loss or precision guarantee follows from this algebraic factorization alone.

## 7. Independent consequence: exact generator minimization remains hard

The following is a source-to-source deduction from Theorem 19 and the [completed Liu reading](LIU-2026-POSITIVE-REALIZATION-COMPLEXITY.md). It is not stated as a theorem of Agarwal–Thakkar, a novelty claim, or an FP architecture proposal.

For a mass-one function that has a finite nonnegative weighted realization, let \(n_+(f)\) be its least nonnegative realization size and \(n_{\rm gen}(f)\) its least proper generative probabilistic-automaton size. Then

\[
n_+(f)=n_{\rm gen}(f).
\]

One inequality follows because a generator is a nonnegative automaton. For the other, trim a least nonnegative realization and apply completion normalization with \(Z=1\). No states are added. Nonnegative word values of an arbitrary signed realization alone are not the assumed positive-realizability promise.

Now let \(H(z)=\sum_{k\ge0}h_kz^{-(k+1)}\) be a nonzero stable SISO transfer function promised to have a positive realization. Set

\[
Z=H(1)=\sum_{k\ge0}h_k>0,
\qquad f(a^k)=h_k/Z.
\]

An order-\(n\) positive realization \(H=C(zI-A)^{-1}B\) gives the unary weighted representation \(\alpha=C/Z,M_a=A,\mu=B\). Trimming and normalization give a proper generator with at most \(n\) states. Conversely, a generator \((\alpha,M_a,\mu)\) for \(f\) gives \(H=Z\alpha(zI-M_a)^{-1}\mu\). Hence

\[
d_+(H)=n_{\rm gen}(f).
\]

For rational full numerator/denominator lists, evaluating \(H(1)\) and scaling have polynomial encoding cost. The corresponding ordinary generating function is

\[
F(t)=\sum_{k\ge0}f(a^k)t^k=\frac{H(1/t)}{tH(1)}.
\]

The pole-free series interpretation at zero is understood. The scalar normalization preserves the McMillan degree. Liu's exact hardness therefore transfers to deciding the least proper unary generator size for a finite-word distribution supplied by this rational generating-function description, already at the threshold given by the associated transfer function's McMillan degree. The input is promised to admit a finite generator, and the size threshold is unary encoded.

Membership in \(\exists\mathbb R\) follows from the same finite Markov-parameter equality certificate, together with nonnegative generator entries and the local normalization equations. Global mass one of the represented target gives properness from its initial distribution. If properness is required from every padded state, add a positive vector \(v\) satisfying \((I-M_a)v=\mathbf1\), which certifies \(\rho(M_a)<1\). A proper trim generator can be padded with unreachable immediately terminating states. The result is therefore an exact-real \(\exists\mathbb R\)-complete promise problem under the specified rational-series input model.

This concerns hidden generator state count with exact real parameters. An online predictor may need a continuum of posterior values even for a small hidden generator. There is no finite-bit storage lower bound, approximate KL gap, stationary one-step loss theorem, or statistical learning lower bound in this deduction.

### Bounded earlier-source comparison

[Kiefer–Wachter, ICALP 2014](https://archive.model.in.tum.de/um/bibdb/kiefer/14KW-ICALP.pdf), Theorems 5 and 11, already establish NP-hardness and an existential-real upper bound for minimization of supplied probabilistic automata. Their model assigns an acceptance probability to each input word, with a separate substochastic matrix for each letter. The hardness construction has a growing alphabet. It is not the unary proper finite-word generator input above. Main-reader coverage was the model in Section 2 and the relevant statements and reduction discussion in Section 4. The full-version correctness proofs and the numerical algorithm were not read.

[Chistikov et al., ICALP 2016](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ICALP.2016.103), Section 3 and Proposition 6, relate an NMF of dimension \(d\) to a covering labelled Markov chain with \(d+2\) states. Covering quantifies over every initial distribution, and the chain emits infinite traces without stopping weights. Main-reader coverage was metadata, abstract, these definitions and statements, and the displayed construction. Remaining proofs and sections were not read. These two historical queries establish relevant precedents, not a complete search for the exact cross-paper corollary's novelty.

## 8. What is retained for subsequent work

The strongest reusable instrument is normalization by actual completion weights, with state count preserved. It provides an exact bridge between a supplied nonnegative finite-mass representation and a proper finite-word generator. SCC computation, telescoping identities and potential transforms remain useful under their explicit domains.

The source's literal local/global equivalence wording, stale-loop update and two printed expressions need the qualifications above. They do not erase the core nonnegative normalization theorem. The abstract internal-inverse claim and the Viterbi special proof have different scopes. No FP core files, experiment protocols or research goals were changed.
