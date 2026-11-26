# Mittal–Roy 2026: agreement moments as query distributions and executable cyclic candidates

## Sources, versions and actual reading

**Tushant Mittal and Sourya Roy, _A General Framework for Low Soundness Homomorphism Testing_, arXiv:2509.05871v2, revised 27 July 2026 at 02:09:02 UTC, 41 physical pages.** [Fixed version and history](https://arxiv.org/abs/2509.05871v2) · [PDF](https://arxiv.org/pdf/2509.05871v2) · [TeX](https://arxiv.org/src/2509.05871v2) · [HTML](https://arxiv.org/html/2509.05871v2).

Pro-A personally completed this edition on 27 November 2026, Shanghai. Coverage includes the front matter, all active Sections 1–6 and proofs, all formulas, eight boxed test displays, two tables, two unnumbered commutative diagrams, six scientific footnotes, two author thanks and all 35 printed references. There are no appendices or figure floats. The active body comprises the abstract, introduction, preliminaries, generic test, cyclic, vector-space, finite-field-to-vector-space, nonabelian, conjugation and lifting sources. Disabled old drafts and commented-out section inputs are not part of the published article. The source archive has 14 TeX files, two bibliography files and a manifest. Original PDF physical pages 4, 6–9, 11–12, 17, 20, 22–23, 25, 28, 33 and 38 were visually checked. Printed page numbers are two below physical page numbers.

The **ITCS 2026 official final**, LIPIcs 362, article 103, 103:1–103:18, published 23 January 2026, is an earlier, shorter edition. [Official record](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITCS.2026.103) · [Official PDF](https://drops.dagstuhl.de/storage/00lipics/lipics-vol362-itcs2026/LIPIcs.ITCS.2026.103/LIPIcs.ITCS.2026.103.pdf). Root personally read its physical pages 1, 8, 11 and 14–16 for metadata, the generic interface, cyclic constant, vector test and nonabelian/lifting statements. The remainder and its reference list were not fully read, so the official edition is indexed as **scoped reading**. It explicitly sends substantial proofs to the long version.

The editions are materially different. Later v2 adds the independent-versus-iid query comparison and a discussion of Kelman et al. The official Theorem 27 assumes acceptance \(\delta_k>1/q\), while later Theorem 4.8 omits that guard. Both inspected editions print the same problematic cyclic zeta multiplier. No equivalence of all remaining text is claimed. The September 2025 v1 was not separately read.

Support readers inventoried sources and checked bounded algebraic interfaces. The main reader covered all scientific content above. Historical BLR, group-theoretic and classification dependencies were read as used here, not independently in their original papers. No AI-use disclosure was found in the inspected material, which does not establish actual use. There was no experiment, implementation, exhaustive search, formal proof or global theorem audit.

## 1. The reusable construction

The paper turns **moments of agreement with a structured function class** into actual query distributions. A batch of observed labels is accepted when some full-domain homomorphism agrees with all of them. If the number of completions is constant over every nonempty evaluation fiber, weighting tuples by that fiber size makes test acceptance proportional to an agreement moment. Low-order moment bounds then force a high-agreement candidate when a higher-order test accepts.

This is a construction of tests for known algebraic structures. The source oracle \(f:G\to H\) is fixed, group operations are given, and agreement is uniform Hamming agreement. There is no online corruption adversary. A constant number of oracle queries does not imply constant local computation, a free weighted sampler, an efficient extension solver, or learned group operations.

For \(\mathcal C=\operatorname{Hom}(G,H)\), write

\[
\alpha_\varphi=\Pr_{x\sim U(G)}[f(x)=\varphi(x)],\qquad
A=\max_{\varphi\in\mathcal C}\alpha_\varphi,\qquad
M_k=\sum_{\varphi\in\mathcal C}\alpha_\varphi^k.
\]

When \(H\) is abelian, pointwise multiplication makes \(\mathcal C\) a group. Evaluation on a tuple \(\mathbf x=(x_1,\ldots,x_k)\) is a homomorphism

\[
\Gamma_{\mathbf x}:\mathcal C\longrightarrow H^k,\qquad
\varphi\longmapsto(\varphi(x_1),\ldots,\varphi(x_k)).
\]

Let \(I_{\mathbf x}=\operatorname{im}\Gamma_{\mathbf x}\) and \(K_{\mathbf x}=|\ker\Gamma_{\mathbf x}|\). Each attainable label vector has exactly \(K_{\mathbf x}\) completions. Double counting yields the central exact identity

\[
\boxed{M_k=\mathbb E_{\mathbf x\sim U(G^k)}
  K_{\mathbf x}\mathbf1\{f(\mathbf x)\in I_{\mathbf x}\}.}
\tag{1}
\]

The kernel normalization has a second computable form, source Claim 2.3:

\[
\gamma_k=\sum_{\mathbf x\in G^k}K_{\mathbf x}
        =\sum_{\varphi\in\mathcal C}|\ker\varphi|^k.
\tag{2}
\]

Although the printed generic setup assumes both groups abelian, the equal-fiber argument itself only needs the target abelian. Later lifting also uses nonabelian domains with abelian targets.

### Global extension is the actual predicate

The condition in (1) is extension to an element of \(\operatorname{Hom}(G,H)\), not merely consistency with relations inside the sampled subgroup. For \(G=\mathbb Z_4,H=\mathbb Z_2\), assigning \(2\mapsto1\) defines a homomorphism on the subgroup \(\{0,2\}\). It cannot extend to \(G\), because every full homomorphism sends \(2\) to twice the image of \(1\), hence to zero. A local relation checker needs an extension theorem or a global solver before it implements this test.

### Removing tuples that accept every label vector

The source samples only informative tuples

\[
D_k=\{\mathbf x:I_{\mathbf x}\ne H^k\},\qquad
\eta_k=|D_k|/|G|^k.
\]

Within \(D_k\), it samples proportionally to \(K_{\mathbf x}\), queries \(f\), and accepts global extendibility. Let its acceptance be \(\delta_k\), put \(T_k=\gamma_k/|G|^k\), and define

\[
b_k=(1-\eta_k)\frac{|\mathcal C|}{|H|^k}.
\]

On the complement of \(D_k\), every fiber has size \(|\mathcal C|/|H|^k\). Thus the correctly normalized consequence of source Lemma 2.1 and Corollary 2.2 is

\[
\boxed{M_k=\delta_k(T_k-b_k)+b_k
              =\delta_kT_k+(1-\delta_k)b_k.}
\tag{3}
\]

Printed summary equation (6), physical page 12, drops the term \(-\delta_k b_k\). This bounded normalization correction matters when \(\eta_k<1\). The cyclic applications below have \(\eta_k=1\), so their identity is exactly \(M_k=\delta_kT_k\).

For nonnegative agreements, the extraction inequalities are elementary:

\[
A\ge \frac{M_{k+1}}{M_k},\qquad
A^{k-s}\ge\frac{M_k}{M_s}\quad(0\le s<k),\qquad
A\le M_k^{1/k},
\tag{4}
\]

when the relevant denominators are positive. Also,
\[
|\{\varphi:\alpha_\varphi\ge\varepsilon\}|
\le M_s\varepsilon^{-s}.
\tag{5}
\]

These give existence and combinatorial list bounds. They are not by themselves a procedure that enumerates the list.

## 2. Source cyclic results

For a nontrivial abelian target and cyclic source, the number of homomorphisms is at most \(|H|\). Hence every tuple is informative for \(k\ge2\). For \(G=\mathbb Z_{p^r}\), source Section 3 counts maps according to their kernel:

\[
\gamma_k=
|\operatorname{Hom}(\mathbb Z_{p^r},H)|
+(1-p^{-k})\sum_{a=1}^{r}p^{ak}
 |\operatorname{Hom}(\mathbb Z_{p^{r-a}},H)|.
\tag{6}
\]

If the \(p\)-primary component of \(H\) has rank \(t\), the number of maps from \(\mathbb Z_{p^u}\) is at most \(p^{ut}\). A geometric series gives, for \(k>t\),

\[
1-p^{-k}\le\frac{\gamma_k}{|G|^k}
\le\frac{p^{k-t}}{p^{k-t}-1}.
\tag{7}
\]

Source Theorem 3.4, interpreted as a bound on maximum agreement, then gives for \(k\ge t+2\),

\[
\left(\frac{(p-1)^2}{p^2}\delta_k\right)^{1/(k-t-1)}
\le A
\le\left(\frac{p^2}{p^2-1}\delta_k\right)^{1/k}.
\tag{8}
\]

Using the \(t+1\) moment in (5) gives the source list-size bound
\[
|\{\varphi:\alpha_\varphi\ge\varepsilon\}|
\le\frac{p}{p-1}\varepsilon^{-(t+1)}.
\tag{9}
\]
In particular the \(2\varepsilon^{-2}\) conclusion concerns the prime-power cyclic setting with cyclic target. It is not the stated all-order cyclic bound.

For arbitrary finite cyclic source and target, primary components factor. Source Proposition 3.8 bounds
\[
1\le T_k\le\zeta(k-1)^2,\qquad k\ge3.
\tag{10}
\]
Combining \(M_k\ge\delta_k\), \(M_3\le\zeta(2)^2\) and (4) gives the reusable lower bound
\[
\boxed{A\ge
\left(\frac{\delta_k}{\zeta(2)^2}\right)^{1/(k-3)}},
\qquad k\ge4.
\tag{11}
\]
The printed Theorem 3.10 instead multiplies \(\delta_k\) by \(\zeta(2)^2\), which already exceeds one at perfect acceptance. Its displayed proof also retains variables from the preceding prime-power argument. The earlier official Theorem 20 has the same multiplier. Equation (11) is an explicitly derived correction, not a quotation of that displayed theorem. The source all-order list bound is \(\zeta(2)^2\varepsilon^{-3}\).

The following exact cyclic construction avoids these loose constants and supplies the computational interfaces that the generic tester leaves abstract.

## 3. Independent deduction: exact cyclic sampler, CRT solver and candidate generator

This section is a source-grounded deduction, with no novelty claim. It applies to known \(G=\mathbb Z_n,H=\mathbb Z_m\), \(m>1\), \(k\ge2\), and arbitrary fixed \(f:G\to H\). Arithmetic uses canonical residue representations. Let \(g=\gcd(n,m)\).

### 3.1 An exact finite normalization

Every homomorphism has a unique parameter \(u\in\mathbb Z_g\):

\[
\varphi_u(x)=\frac{m}{g}ux\pmod m.
\tag{12}
\]

For a tuple, the kernel count is
\[
K_{\mathbf x}=\gcd(g,x_1,\ldots,x_k).
\tag{13}
\]
Writing \(\phi_{\mathrm E}\) for Euler's totient, the divisor identity
\(d=\sum_{a\mid d}\phi_{\mathrm E}(a)\) gives

\[
\boxed{C_k:=\frac{\gamma_k}{n^k}
       =\sum_{d\mid g}\frac{\phi_{\mathrm E}(d)}{d^k}.}
\tag{14}
\]

To see this directly, expand (13) as
\(\sum_{d\mid g}\phi_{\mathrm E}(d)\mathbf1\{d\mid x_i\ \forall i\}\).
Because \(d\mid n\), the uniform probability of that event is \(d^{-k}\).
Thus no enumeration of all \(n^k\) tuples or all \(g\) maps is needed to characterize the normalization.

### 3.2 Sampling the actual weighted tuple distribution

1. Draw a divisor \(D\mid g\) with probability
   \(\phi_{\mathrm E}(D)D^{-k}/C_k\).
2. Draw \(x_1,\ldots,x_k\) independently and uniformly from the multiples of \(D\) in \(\mathbb Z_n\).

For a fixed tuple, this produces
\[
\Pr[\mathbf x]
=\sum_{\substack{D\mid g\\D\mid x_i\ \forall i}}
\frac{\phi_{\mathrm E}(D)D^{-k}}{C_k}
\left(\frac Dn\right)^k
=\frac{K_{\mathbf x}}{n^kC_k}.
\tag{15}
\]

If the factorization \(g=\prod_p p^{e_p}\) is supplied, no full divisor list is required. Choose prime exponents independently, with weights
\[
w_{p,0}=1,\qquad
w_{p,a}=(1-1/p)p^{-a(k-1)},\quad1\le a\le e_p.
\tag{16}
\]
Their product has the desired divisor law. Exact integer sampling uses the equivalent weights
\[
\widehat w_{p,0}=p^{e_p(k-1)+1},\qquad
\widehat w_{p,a}=(p-1)p^{(e_p-a)(k-1)}.
\tag{17}
\]
There are only \(\sum_p(e_p+1)\) weights, each with \(O(k\log g)\) bits. Building these weights, drawing exact integers and sampling multiples are real computational costs. Polynomial bit complexity here is conditional on the factorization being available. Factoring an arbitrary binary integer is not silently counted as free. The acceptance solver below needs only gcd and extended Euclidean arithmetic, not factorization.

### 3.3 Global extension by generalized CRT

Query \(y_i=f(x_i)\). If any \(y_i\) is not a multiple of \(m/g\), reject. Otherwise put \(v_i=y_i/(m/g)\in\mathbb Z_g\). The batch extends exactly when
\[
x_i u\equiv v_i\pmod g\qquad(1\le i\le k)
\tag{18}
\]
has a simultaneous solution.

Let \(d_i=\gcd(x_i,g)\). An individual equation requires \(d_i\mid v_i\), and then reduces to
\[
u\equiv
(x_i/d_i)^{-1}(v_i/d_i)\pmod{g/d_i}.
\tag{19}
\]
The inverse exists because its two arguments are coprime. A modulus-one constraint is vacuous. Merge these congruences with generalized CRT, rejecting incompatible residue pairs. This uses \(O(k)\) gcd, inverse and congruence-merge operations on integers of controlled bit length.

When consistent, the answer is
\[
u=u_0+j\frac g{K_{\mathbf x}}\pmod g,\qquad
0\le j<K_{\mathbf x},
\tag{20}
\]
because \(\operatorname{lcm}_i(g/d_i)=g/K_{\mathbf x}\).
The solver therefore gives both an exact extension test and a compact description of all completions. Uniformly drawing \(j\) gives a uniform global completion without constructing a full truth table.

This is stronger than merely checking relations in the sampled subgroup. It uses the known full-domain parameterization (12). When \(g=1\), the unique map is zero and the construction reduces to uniform queries and zero-label checking. The trivial target \(m=1\) is handled separately by immediate acceptance.

### 3.4 Acceptance, certified existence and list bounds

All tuples are informative in this setting, so the acceptance of (15)–(19) is precisely the paper's cyclic \(\delta_k\), and
\[
M_k=\delta_kC_k.
\tag{21}
\]
For any integer \(2\le s<k\), \(M_s\le C_s\). Thus
\[
\boxed{
\left(\frac{\delta_kC_k}{C_s}\right)^{1/(k-s)}
\le A\le \min\{1,(\delta_kC_k)^{1/k}\}.}
\tag{22}
\]
Also, the number of candidates with agreement at least \(\varepsilon\) is at most \(C_s\varepsilon^{-s}\).
The constants are exact finite quantities depending only on \(g\), not asymptotic placeholders.

For \(s>2\), one can optionally bound the finite divisor sum by its full Euler product,
\[
C_s\le\prod_p\frac{1-p^{-s}}{1-p^{1-s}}
=\frac{\zeta(s-1)}{\zeta(s)}.
\tag{23}
\]
Each local factor follows by summing the geometric weights in (16). This supplies an all-order constant for the explicit cyclic-to-cyclic subclass. The finite \(C_s\) is preferable when known. No claim that (23) is new is intended.

### 3.5 A candidate distribution with computable query cost

After an accepted tuple, choose a completion uniformly using (20). For a fixed \(\varphi\), its single-trial output probability is
\[
\begin{aligned}
\Pr[\text{output }\varphi]
&=\sum_{\mathbf x:\varphi(\mathbf x)=f(\mathbf x)}
\frac{K_{\mathbf x}}{n^kC_k}\frac1{K_{\mathbf x}}\\
&=\frac{\alpha_\varphi^k}{C_k}.
\end{aligned}
\]
Consequently,
\[
\boxed{\Pr[\varphi\mid\text{accept}]
       =\frac{\alpha_\varphi^k}{M_k}.}
\tag{24}
\]
The abstract agreement-power measure motivating the paper has become an executable random candidate generator in this subgroup of problems.

With fresh independent trials and \(\delta_k>0\), the expected query count until the first candidate is \(k/\delta_k\), counting exactly \(k\) queries per trial. A budget of \(T\) trials has no-output probability
\[
(1-\delta_k)^T.
\tag{25}
\]
Conditioned on obtaining any output within that budget, the first candidate still has distribution (24). A finite budget also provides an honest failure exit when \(\delta_k=0\).

The candidate's mean true agreement is
\[
\mathbb E[\alpha_\varphi\mid\text{accept}]
=\frac{M_{k+1}}{M_k}
\ge \left(\frac{M_k}{M_s}\right)^{1/(k-s)}
\ge \left(\frac{\delta_kC_k}{C_s}\right)^{1/(k-s)}.
\tag{26}
\]
For the middle step, moment log-convexity makes \(M_{j+1}/M_j\) nondecreasing, and their product from \(j=s\) to \(k-1\) equals \(M_k/M_s\).
A complementary tail statement is
\[
\Pr[\alpha_\varphi\le\tau\mid\text{accept}]
\le\min\left\{1,\frac{\tau^{k-s}C_s}{\delta_kC_k}\right\}.
\tag{27}
\]
It follows by bounding \(\alpha_\varphi^k\le\tau^{k-s}\alpha_\varphi^s\) on the bad set.

These statements concern an average or a quantified tail, not a guarantee that every accepted candidate achieves the mean. Fresh validation is required to estimate one selected candidate's agreement. The procedure does not enumerate every good homomorphism and is not a complete list decoder. Larger \(k\) sharpens relative weighting but can lower acceptance and increase query cost. Local arithmetic, factorization preparation, random bits and validation remain separate from the displayed oracle count.

## 4. Finite-field tests: useful cancellation and its precise category

### 4.1 Vector space to field

Section 4.1 studies \(f:\mathbb F_q^n\to\mathbb F_q\). Its actual comparison class is the \(\mathbb F_q\)-linear maps \(\varphi_a(x)=a\cdot x\): the count is \(q^n\), evaluation kernels are counted by rank over \(\mathbb F_q\), and the test uses nonzero coefficients from that field. For nonprime \(q\), this is a proper subclass of additive-group homomorphisms. For example, Frobenius \(x\mapsto x^p\) on \(\mathbb F_{p^r}\), \(r>1\), is additive but not generally \(\mathbb F_{p^r}\)-linear.

A uniformly sampled short tuple usually has full rank and accepts any labels, so the unshifted moment is dominated by a baseline. The authors shift agreement to
\[
s_a=\frac{q\alpha_a-1}{q-1}
\]
and use a binomial finite-difference cancellation. The informative test samples \(k-1\) independent vectors, draws nonzero coefficients \(a_i\), sets \(x_k=\sum_{i<k}a_ix_i\), and checks the same equation on labels. Here independent means linearly independent, so \(n\ge k-1\).

Rank-\((k-1)\) tuples have a unique dependence up to scale. Partitioning by its support size and canceling lower-rank contributions gives the source approximation
\[
\sum_a s_a^k
=\theta_k+O_{q,k}(q^{-n}),\qquad
\theta_k=\frac{q\delta_k-1}{q-1}.
\tag{28}
\]
The asymptotic constants depend on \(q,k\). This is not a uniform estimate for \(k\) approaching \(n\).

Later v2 Remark 4.5 compares the actual independent-vector law with iid uniform vectors. A direct coupling bounds their total variation by
\[
\rho_{q,n,k}
=1-\prod_{i=0}^{k-2}(1-q^{i-n})
\le q^{-n}\frac{q^{k-1}-1}{q-1}.
\tag{29}
\]
Thus an iid implementation changes acceptance by at most this amount. Independence cannot simply be ignored at finite dimension.

The source Theorem 4.8 states an odd-\(k\) lower and upper agreement bound with exponents \(1/(k-2)\) and \(1/k\). The lower-bound mechanism uses an even second moment and a signed odd moment. For a reusable finite-\(n\) statement, write a valid error bound in (28) as \(E_k\). If \(\theta_k>E_k\), and \(S_2=\sum_a s_a^2\), then
\[
\max_a s_a\ge
\left(\frac{\theta_k-E_k}{S_2}\right)^{1/(k-2)}.
\tag{30}
\]
Indeed, negative terms only decrease the odd moment, while each positive term is at most \((\max s)^{k-2}s_a^2\). The error stays inside the root. A uniform additive \(O(q^{-n})\) error outside a root does not follow near zero advantage.

**Independent exact second-moment bound.** In fact \(S_2\le1\) for every \(f\), any prime power \(q\), and every \(n\). Take a nontrivial additive character \(\chi\) of \(\mathbb F_q\), put \(h_t(x)=\chi(tf(x))\), and normalize Fourier coefficients by
\(\widehat h(v)=\mathbb E_x h(x)\overline{\chi(v\cdot x)}\).
Character orthogonality gives
\[
s_a=\frac1{q-1}\sum_{t\ne0}\widehat h_t(ta).
\]
Convexity of squared complex modulus, the bijection \(a\mapsto ta\), and Parseval imply
\[
\sum_a s_a^2
\le\frac1{q-1}\sum_{t\ne0}\sum_a|\widehat h_t(ta)|^2
=\frac1{q-1}\sum_{t\ne0}\mathbb E_x|h_t(x)|^2=1.
\]
The character itself need not be faithful for nonprime \(q\). Thus a safe finite-error consequence of (28), for odd \(k\ge3\) and \(\theta_k>E_k\), is
\[
\boxed{A\ge\frac1q+\frac{q-1}{q}
(\theta_k-E_k)^{1/(k-2)}.}
\tag{30a}
\]
For \(k=3\), this becomes \(A\ge\delta_k-(q-1)E_k/q\).
The exact Parseval inequality is independently established here. The numerical value of \(E_k\) still requires the source rank-count error bound or a separately supplied bound.

The printed upper-bound step is not justified by the displayed signed-moment identity alone: for odd \(k\), negative \(s_a^k\) can cancel positive terms. This note does not use that upper bound or claim an exhaustive refutation of every possible stronger theorem. The official earlier guard \(\delta_k>1/q\), finite-dimension error and actual linear category are retained.

### 4.2 Field to vector space gives an exact collision sampler

For \(f:\mathbb F_q\to\mathbb F_q^n\), the comparison maps are \(\varphi_a(x)=xa\). On a uniform nonzero \(X\), define
\[
R=X^{-1}f(X),\qquad p_a=\Pr[R=a].
\]
The source nonzero-input tester accepts iff \(k\) independent values of \(R\) agree. Hence exactly
\[
\delta_k=\sum_a p_a^k,\qquad
\delta_k^{1/(k-1)}\le\max_a p_a\le\delta_k^{1/k}.
\tag{31}
\]
On the full domain the agreement is
\[
A=\frac{\mathbf1\{f(0)=0\}}q+\frac{q-1}{q}\max_a p_a.
\tag{32}
\]
The zero contribution is the same for every linear candidate and should not be silently discarded.

An accepted test directly supplies \(a=R\), with probability \(p_a^k/\delta_k\). Repetition has expected \(k/\delta_k\) queries and mean nonzero-domain agreement \(\delta_{k+1}/\delta_k\). This is another exact candidate sampler, derived from the source collision identity. It has the same validation and budget qualifications as Section 3.5.

## 5. Automorphisms replace kernels by stabilizers

For nonabelian targets the homomorphism set need not be a pointwise group. Section 5 instead uses the composition group \(\operatorname{Aut}(G)\), acting diagonally on \(G^k\). Evaluation need not be a group homomorphism. What matters is that a nonempty fiber is a coset of the tuple stabilizer.

With \(\alpha_\varphi=\Pr[f(x)=\varphi(x)]\),
\[
\sum_{\varphi\in\operatorname{Aut}(G)}\alpha_\varphi^k
=\mathbb E_{\mathbf x}
 |\operatorname{Stab}(\mathbf x)|
 \mathbf1\{f(\mathbf x)\in\operatorname{Orb}(\mathbf x)\},
\tag{33}
\]
and
\[
\rho_k=\sum_{\mathbf x}|\operatorname{Stab}(\mathbf x)|
       =\sum_{\varphi\in\operatorname{Aut}(G)}
          |\operatorname{Fix}(\varphi)|^k.
\tag{34}
\]
Weighting by stabilizer size makes the same nonnegative moment extraction available. The computational oracle is now simultaneous orbit membership.

### Dihedral groups

For \(D_{2p}=\langle r,s:r^p=s^2=1,srs=r^{-1}\rangle\), odd prime \(p>3\), automorphisms have \(r\mapsto r^\ell,s\mapsto sr^m\), \(\ell\ne0\). There are \(p(p-2)\) automorphisms fixing two elements, \(p-1\) fixing \(p\), and the identity fixing \(2p\). Thus
\[
\rho_k=p(p-2)2^k+(p-1)p^k+(2p)^k.
\tag{35}
\]
Source Theorem 5.7 gives \(A\ge\frac12\delta_k^{1/(k-2)}\) for \(k\ge3\). The exact normalizer in (35), rather than an assumed dimension-free upper constant, controls the opposite moment direction.

### Inner automorphisms and conjugacy-class geometry

For inner automorphisms, the stabilizer count is
\[
\frac{|\bigcap_i C_G(x_i)|}{|Z(G)|}.
\]
The quotient by the center is necessary because central conjugators define the same map. One early source display omits it, while subsequent normalizations use it.

The useful exact invariant is
\[
\boxed{
C_k^{\rm Inn}
=\frac1{|Z(G)|}
 \sum_{\text{conjugacy classes }\mathcal K}|\mathcal K|^{1-k}
=\frac1{|Z(G)|}\sum_{g\in G}
 \left(\frac{|C_G(g)|}{|G|}\right)^k.}
\tag{36}
\]
This translates the cost of many competing automorphisms into the distribution of centralizer sizes.

If every nontrivial irreducible representation has dimension at least \(|G|^c\), the permutation action on a proper centralizer's cosets gives the source bound
\[
1\le C_k^{\rm Inn}
\le1+\frac{|G|^{1-kc}}{|Z(G)|}.
\tag{37}
\]
This yields small normalized moments when \(kc>1\). For extraspecial groups of order \(p^r\), all noncentral conjugacy classes have size \(p\), giving the exact formula
\[
C_k^{\rm Inn}=1+(p^{r-1}-1)p^{-k}.
\tag{38}
\]
For symmetric groups, the authors state \(C_k^{\rm Inn}=1+O(n^{-2(k-1)})\). Their proof and imported structural results were read, but this asymptotic was not independently certified. A displayed final binomial estimate does not by itself establish the whole claimed tail uniformly, so this note uses the exact invariant (36) as its dependable interface rather than promoting that step to a verified bound.

The introduction and later body also give different finite-simple-group exponents. The body Theorem 5.22 requires \(k\ge6\) and uses \(1/(k-5)\). The introductory Theorem 1.4 advertises \(k\ge4\) and \(1/(k-2)\). These are not merged into one theorem here. For extraspecial families with fixed \(p\) and growing \(r\), (38) grows, so a generic upper agreement bound must retain \(C_k^{\rm Inn}\). None of these classification-dependent side claims is needed for the cyclic constructor.

All group actions and orbit tests remain supplied algebraic interfaces. The paper's query complexity does not price a general simultaneous-conjugacy algorithm.

## 6. Lifting through known quotients

Section 6 considers a surjection \(\pi:\widetilde G\to G\) and an embedding \(\iota:H\to\widetilde H\). A base homomorphism lifts as \(\iota\varphi\pi\). To identify this lift class with the entire target homomorphism class requires a separate factorization theorem, not just the displayed commuting diagram.

For the lift class,
\[
K_{\widetilde{\mathbf x}}=K_{\pi\widetilde{\mathbf x}},
\qquad
\widetilde\gamma_k=|\ker\pi|^k\gamma_k,
\qquad
\frac{\widetilde\gamma_k}{|\widetilde G|^k}
=\frac{\gamma_k}{|G|^k}.
\tag{39}
\]
Uniform measure pushes forward through a finite group quotient. Thus the normalized kernel moments transfer exactly.

If \(\iota\) is onto, informative tuples correspond under \(\pi\). Given a sampler for the base weighted tuple and a uniform sampler for each quotient fiber, one can sample its coordinates' preimages independently and query \(\widetilde f\). This implements the lifted test with the same oracle-query count. Constructing a section or a uniform kernel sampler is an additional computational obligation.

If \(\iota\) is a proper embedding, every tuple is informative relative to \(\widetilde H^k\), including base tuples that allowed all \(H^k\) labels. Therefore one must use the full base kernel-weighted law with range-membership checking, rather than blindly reusing a sampler conditioned on the base informative set. The source explicitly treats its general lift as an analysis framework, not a universal black-box reduction. An arbitrary \(\widetilde f\) need not be constant on quotient fibers.

The principal applications are:

- **Group characters.** Maps to an abelian target factor through \(G/[G,G]\). For the stated \(\mathrm{GL}_n(\mathbb F_q)\) regime \(q>2,n\ge2\), determinant supplies the quotient \(\mathbb F_q^\times\), a cyclic group of order \(q-1\). It is not a map into \(\mathrm{SL}_n\). The usable cyclic constant is (11) or the exact cyclic analysis, not the printed multiplier.
- **Lie algebra characters.** The comparison maps are field-linear and vanish on brackets, so they factor through \(\mathfrak g/[\mathfrak g,\mathfrak g]\). For the matrix algebra, trace gives the one-dimensional quotient and characters have form \(X\mapsto a\,\operatorname{tr}X\). The additive group of \(\mathbb F_q\) is not \(\mathbb Z_q\) when \(q\) is a nonprime prime power. The field-to-vector-space collision calculation can be transferred with actual trace-fiber sampling.
- **Maps to \(\mathbb F_p\).** The relevant quotient is the elementary abelian quotient of the abelianization modulo \(p\)-multiples, hence an \(\mathbb F_p\)-vector space. A cyclic component \(\mathbb Z_{p^b}\) should not be replaced by the additive group of \(\mathbb F_{p^b}\). Finite-dimension error and odd-\(k\) requirements from the vector-space base theorem remain obligations after lifting, even when absent in a compressed corollary statement.

These are constructive uses of a known quotient. They do not show how an unknown quotient, operation vocabulary or predictive state partition is acquired from observations.

## 7. What is established and what remains conditional

The most useful output of the paper is the sequence
**equal evaluation fibers → weighted local queries → agreement moments → structured candidates**.
For cyclic groups, this note additionally supplies exact finite normalizers, an implementable divisor-mixture sampler, generalized CRT extension, uniform completion, and a quantified agreement-power candidate distribution. All added results have explicit known-structure and sampling assumptions.

The bounded source corrections above protect this computational interface: informative-set normalization, a cyclic constant, linear-versus-additive categories, signed-moment error handling, and quotient sampling. They do not constitute a certification or rejection of the entire paper. The full scientific text has been read even where a source theorem remains unverified or a displayed proof is insufficient for direct reuse.

Compared with [Kelman et al.](KELMAN-2026-RESILIENT-HOMOMORPHISM.md), this work deliberately biases static query locations to obtain low-soundness moment control. Kelman instead preserves uncertainty of the next query against an online adversary. The cyclic candidate sampler here cannot inherit that adversarial guarantee. Kelman's full-group generator compiler and this CRT solver also solve different extension problems.

No FP transfer is asserted. Known finite groups, chosen query access, exact equality labels, uniform-agreement objectives and tractable completion are substantive assumptions. Any future transfer would need a specific prediction object, a justified algebraic class and an accounting of acquisition, local arithmetic, stored descriptions and independent validation. The note changes no FP core definition, architecture, experiment or research direction.
