# Length Generalization Bounds for Transformers

## Source, edition and reading boundary

- Authors: Andy Yang, Pascal Bergsträßer, Georg Zetzsche, David Chiang and Anthony W. Lin.
- Authoritative edition: [ICML 2026, PMLR 306:144227–144248](https://proceedings.mlr.press/v306/yang26c.html), [complete 22-page proceedings PDF](https://raw.githubusercontent.com/mlresearch/v306/main/assets/yang26c/yang26c.pdf). The conference dates are July 6–11, 2026.
- Matched source edition: [arXiv:2603.02238v2](https://arxiv.org/abs/2603.02238v2), revised May 31, 2026 at 03:56:12 UTC, with [complete TeX](https://arxiv.org/src/2603.02238v2). The displayed v1 history says February 13. The identifier's month is not substituted for that history. The two PDFs have identical extracted page text on pp. 2–22. Page 1 differs by the arXiv watermark. They are different binary files with small layout differences, not identical files.
- Pro-E completed the full reading on November 26, 2026, Shanghai. The main reader covered all active TeX, main Sections 1–6, Appendices A–C, every proof and mathematical display, footnotes, Figure 1 and the complete printed references. Original PDF checks included pp. 5–7, 13, 18–19 and 21–22. Source comments and omitted draft material are not treated as published claims.
- Bounded assisting checks concerned source matching, the positive-fragment witness argument, the Diophantine encoding and the attention interface. The main reader checked the relevant primary-source passages and the arguments recorded below. No formal proof, complete theorem certification or empirical reproduction is claimed. Cited predecessor papers retain their separate reading statuses.
- Proceedings PDF SHA-256: `daa96888a778764eab357bfb2696f85fbd6a4cf68e159c3411225ffa6dd8fce4`. ArXiv PDF: `b3413b9a94dd8f1736414fb4670e92099bf8ef5f8943ecb7f54154a027d6c77a`. TeX archive: `04f8bcc5bd920ff9a328633a2996e572c8b1f4e1f1a7943fba9b16e36dd1d743`.

**Assessment.** The paper asks a precise identification question: how long a distinguishing word must be when the target and candidate programs have bounded descriptions. This is separate from statistical generalization of trained transformers. Its positive counting fragment has a particularly useful structure. An independent witness-retention proof below gives a direct bound of (q(K)+1), with (K) one above the largest comparison threshold, and a tight (2^{\Theta(S)}) worst-case rate under the paper's syntax-size convention. The displayed negative encoding and both transformer translation directions have concrete local defects. The logical undecidability route can be repaired as described below, whereas this reading does not certify the complete quantitative transformer translation.

## 1. The actual learning and representation problem

### 1.1 Counting programs

C-RASP evaluates a Boolean program on every position of a finite word. Its basic objects are letter predicates, Boolean operations and inclusive prefix counts

\[
(\#\phi)^{w,i}=|\{j\le i:w,j\models\phi\}|.
\]

Numerical predicates compare a linear combination of such counts and integer constants to an integer threshold. General C-RASP permits signed coefficients. A program accepts a word when its final Boolean output is true at the final position.

The past operator (P\phi) is strict, meaning that some (j<i) satisfies (\phi). The history operator (H\phi) includes the current position. Both are count abbreviations:

\[
P\phi\equiv(\#\phi\ge2)\lor(\neg\phi\land\#\phi\ge1),
\qquad H\phi\equiv\#(\neg\phi)=0.
\]

The representation is a straight-line DAG. A reference to an earlier Boolean definition costs one syntax unit. Integer constants are encoded in binary. Size (S), count-nesting depth (d), maximum constant bit length (p) and maximum number of summands (g) are different parameters. Unit-cost references are a syntax convention, not a claim that arbitrary addresses require one physical bit.

Definition 4.1 restricts **coefficients, constant terms and comparison thresholds to nonnegative integers**. Boolean negation remains unrestricted. Thus positive C-RASP is not monotone Boolean logic. The important restriction prevents large positive and negative counts from cancelling. Statements about this fragment use its explicit grammar, with (P,H) expanded if they are employed as abbreviations.

### 1.2 Length complexity is an exhaustive identification bound

The learner knows a bound (n) on the target's description length. It receives the complete set of accepted words of length at most (N), with the universe of shorter words known. This supplies both positive and negative membership labels. It may enumerate all candidate descriptions of size at most (n) and choose a consistent one.

The displayed definition takes the maximum, over ordered pairs of descriptions, of the shortest word in (L(P)\setminus L(Q)) when that difference is nonempty. A shortest word in the symmetric difference is sufficient for ordinary identification, but a bound on that word alone does not automatically bound both directed differences. Boolean closure lets us apply a nonemptiness bound directly to (P\land\neg Q), which handles the stated definition.

For an alphabet of size (A\ge2), exhaustive labels through length (N) number

\[
\sum_{j=0}^{N}A^j=\frac{A^{N+1}-1}{A-1}.
\]

Consequently, an exponential length bound in (S) can require a doubly exponential exhaustive sample. For a unary alphabet the count is (N+1). The paper does not prove that iid samples, SGD, a polynomial-time search or a small random training set attains the identification guarantee. Its final discussion explicitly leaves finer sample-size analysis open. The source's learning recipe writes (\Sigma^{\le n}) where the preceding construction requires (\Sigma^{\le N}), a local notation correction.

## 2. Author claims and their interfaces

| Result in the source | Mathematical claim | Scope retained in this note |
|---|---|---|
| Theorem 3.1 and Corollary 3.6 | C-RASP emptiness is undecidable, so no computable uniform length bound exists | The printed reduction needs the repairs in Section 4. This is a worst-case statement over descriptions, not failure of every individual learner or task |
| Appendix C | Satisfiability reduces to depth at most two | A complete annotation construction is supplied independently below. It can enlarge the alphabet and description exponentially |
| Proposition 4.6 and Corollary 4.7 | Positive C-RASP has an exponential short-word and length-complexity bound | Section 3 gives an independent, sharper quantitative argument under the same positive grammar |
| Section 5, first transformer class | C-RASP corresponds to ((1,\log n))-precision transformers and inherits the negative result | This uses an external expressivity theorem. Its predecessor proof was not fully reread here |
| Section 5 and Appendix B | ((1,1))-precision transformers correspond to positive C-RASP and have singly exponential bounds | The displayed translations have unresolved interfaces described in Section 5. No complete quantitative transfer is certified here |

Here ((1,1)) means that precision inside and outside attention is independent of input length. It does not mean one bit. Across models the bit parameter (p) may vary. The source's transformer upper bound is (2^{\operatorname{poly}(p,d,L)}), with dimension (d) and layers (L). Converting this into an exact serialized model-bit statement also requires accounting for the permitted position-wise functions and their representations.

The fixed-precision model rounds attention weights individually. It need not renormalize them afterward. All such weights can be zero. It also excludes arbitrary positional encodings and uses the particular causal transformer semantics of Appendix B. Ordinary floating-point implementations or other normalization orders cannot be substituted without a separate argument.

## 3. Independent result: a direct short-witness bound

This section is a note-level deduction from Definition 4.1. It is not attributed to the authors, and no novelty claim is made.

### 3.1 Retain the first witnesses of each counted predicate

Let (P) be a positive C-RASP program after expanding temporal abbreviations. Let (q) be the number of distinct count nodes (\#\psi) in its whole DAG. Let (k_{\max}) be the largest right-hand comparison threshold, taking zero if there are no comparisons, and set

\[
K=k_{\max}+1\ge1.
\]

For any nonempty input word (w), retain the first (K) positions at which each counted predicate (\psi) is true in (w), or all its satisfying positions if there are fewer. Also retain the final position of (w). Preserve their order to obtain a subsequence (u). Then

\[
|u|\le qK+1.
\tag{1}
\]

**Claim.** Every Boolean subformula has the same truth value at each retained position in (u) as at its corresponding position in (w). In particular the final acceptance decision is preserved.

**Proof.** Induct over the original Boolean/count DAG, using correctness at all retained positions as the induction statement. Letter predicates are preserved by taking a subsequence. Negation and conjunction preserve correctness directly.

For a count node (\#\psi), consider a retained position (i) of the original word and its corresponding position (i') in (u). If the original prefix contains fewer than (K) witnesses of (\psi), every one is among the first (K) global witnesses and was retained. If it contains at least (K), the first (K) were all retained before or at (i). The inductive hypothesis ensures that no retained position changes whether it satisfies (\psi). Therefore

\[
\min\{(\#\psi)^{w,i},K\}
=\min\{(\#\psi)^{u,i'},K\}.
\tag{2}
\]

Now write a numerical predicate as

\[
C+\sum_j\alpha_j\#\psi_j\ \mathrel{\diamond}\ k,
\qquad C,\alpha_j,k\in\mathbb N,
\quad \diamond\in\{<,\le,=,\ge,>\}.
\]

If any count with positive coefficient reaches (K), both sums are at least (K>k), so all five comparison types have the same truth value. Otherwise every contributing count is exact by (2), and the two sums agree. Zero coefficients do not contribute. This proves the numerical step and completes the induction. Counts above (K) need not remain exact. Only their capped values and every Boolean decision are preserved.

The construction also covers (q=0), when retaining the final letter is sufficient. Empty-word acceptance can be handled separately and only improves the shortest-witness bound. No alphabet-size factor or new letters are needed.

### 3.2 Directed differences and a tight syntax-size rate

Apply the construction to (P\land\neg Q). If (L(P)\setminus L(Q)) is nonempty, it has a word of length at most

\[
(q_P+q_Q)(1+\max\{k_P,k_Q\})+1.
\tag{3}
\]

In the paper's binary-constant syntax, (q\le S) and (K\le2^p), with (p\le S) up to fixed syntax conventions. This yields

\[
|u|\le S2^p+1\le2^{O(S)}.
\]

For a matching lower bound, over a unary alphabet the program (\#a=2^b) has size (O(b)) and accepts only (a^{2^b}). Comparing it with the empty language requires a word of length (2^b). Thus the worst-case length complexity of the positive grammar under these conventions is

\[
\boxed{2^{\Theta(S)}}.
\tag{4}
\]

The source states an exponential rate through a decomposition and temporal-logic translation. Equation (4) and the explicit (qK+1) bound are the independent sharpening here. They do not prove any transformer bound until the relevant transformer-to-logic translation has been justified.

### 3.3 Why the sign condition matters

For (M\ge3), consider the signed predicate

\[
(\#a-M\#b=0)\land(\#b>0).
\]

There are two count nodes and the largest right-hand threshold is zero. A naive extension of (1) would give three. Its actual shortest witness has length (M+1), for example (a^M b). Large opposing counts can cancel, so saturation at one destroys the equality. This refutes extending the threshold-only witness lemma to signed counting. It does not itself prove undecidability.

The same retention idea also gives a simple temporal-logic fact. For a pure past (P,H) DAG, retain the first witness of each (P\psi), the first counterexample to each (H\psi), and the original final position. Induction at retained positions preserves all temporal truth values, so (m) temporal nodes need at most (m+1) positions. This avoids the source's propositional-alphabet lift altogether.

The source's Lemma 4.5 lifts a letter alphabet to arbitrary sets of propositions but does not explicitly impose exactly one base letter per position. A direct repair is the global constraint

\[
H\left[(\bigvee_{a\in\Sigma}a)
\land\bigwedge_{a\ne b}\neg(a\land b)\right].
\]

Without it, projection from an arbitrary propositional word to a word in (\Sigma^*\) is not automatic. The direct subsequence proof above preserves the original letter alphabet and requires no such repair.

## 4. The negative encoding: defects and a corrected logical route

### 4.1 Concrete failures in the displayed mapping

Theorem 3.1 reduces a system of equations (x=c), (x+y=z), (xy=z) over nonnegative integers to language nonemptiness. Distinct variables within each equation can be arranged by fresh variables and additional equations. The multiplication witness is intended to have the form

\[
x^n(z^n y\bar z^n\bar y)^m,
\]

so its unbarred letter counts satisfy (\#x=n), (\#y=m), (\#z=nm).

The formula on p. 5 retains an (\mathrm{Only}_{y,\bar y}) restriction inside (\mathrm{Alt}_y), then uses that predicate inside the larger multiplication language. Read literally it forbids (x,z,\bar z). Deleting this inner restriction is necessary. Even after that deletion, the written formula lacks the final balance (\#z=\#\bar z). The word (xz) then passes the remaining constraints through vacuous (y,\bar y) implications, although (1\cdot0\ne1).

The concatenation and variable-matching steps on p. 6 have separate errors. The printed construction requires (n) separators for (n) blocks, and its variable comparison uses block indices (1,\ldots,n) instead of the actual (0,\ldots,n-1). Finally it disjoins rather than conjoins the variable-consistency formulas.

An exact counterexample to the displayed complete mapping uses just

\[
D_1:x=1,\qquad D_2:x=2.
\]

This system is unsatisfiable. Nevertheless (x\$xx\$xx) satisfies the printed two-separator formula. Its first and second blocks satisfy the two constant equations. The printed consistency predicate compares the second and third blocks, each containing two (x)'s, and therefore also holds. This is a counterexample to that mapping, not to the undecidability theorem.

Two additional details matter in a repair. Inclusive separator counts include the preceding separator in an unqualified block guard. Also, a variable absent from an equation must not be forced to have the same count in that equation's restricted local alphabet.

### 4.2 Correct local and block construction

The following is an independent repair of the logical route, using the paper's standard undecidability premise for Diophantine systems.

For multiplication, remove the inner two-letter-only constraint from (\mathrm{Alt}_y), retain the outer five-letter restriction and add final (\#z=\#\bar z). The remaining prefix constraints put all (x)'s first, alternate (y,\bar y), allow (z)'s only in the intervening balanced phase and (\bar z)'s only in the other phase. At each (y), the (z\)-minus-(\bar z) balance equals the total (x) count. At each (\bar y), that balance is zero. The added final balance excludes an unfinished trailing (z) block. Thus every complete pair of blocks has exactly (n) copies of each (z)-type, yielding the intended language. This includes (n=0) and (m=0).

Expand (P,H) into counts before combining equations. For (n) local equation formulas use exactly (n-1) separators and the block guards

\[
G_i=\neg\$\land(\#\$=i-1),\qquad i=1,\ldots,n.
\]

Define relative evaluation recursively, with

\[
R_i(\#\chi)=\#[G_i\land R_i(\chi)],
\]

and commute (R_i) through Boolean and numerical operations. At each position in block (i), structural induction gives its ordinary block-prefix semantics. The local equation formulas are regulated: all raw letter tests occur inside counts. Their relative terminal truth values consequently stop changing once that block has ended. They may all be checked at the final position of the concatenated word. Empty blocks use zero counts.

For a variable (x), let (I_x) be the set of equation blocks in which (x) actually appears. Choose an anchor (a_x\in I_x), and conjoin

\[
\#[G_i\land x]=\#[G_{a_x}\land x]
\quad\text{for every }i\in I_x.
\]

Do this for every variable. A system solution supplies a local witness in each block and their concatenation satisfies the construction. Conversely, these matching counts define a single assignment whose restriction solves every local equation. If necessary append a harmless fresh equation (u=1) so the overall witness is nonempty. This also avoids relying on an unspoken terminal-letter convention for an entirely empty input.

### 4.3 A complete depth-two annotation argument

The printed Appendix C omits the depth-two branch of its induction, does not explicitly accumulate all recursive consistency constraints and introduces fresh propositions without explaining their alphabet interpretation. A direct DAG construction avoids these omissions.

First expand temporal operators. For every Boolean node (\chi) of the original DAG introduce a bit (P_\chi). Work over the finite alphabet

\[
\Sigma'=\Sigma\times\{0,1\}^m.
\]

Each bit and each original-letter test is a finite disjunction of predicates for letters in this expanded alphabet. Define the flattened formula by its immediate children:

\[
\begin{aligned}
\operatorname{flat}(a)&=\operatorname{Base}_a,\\
\operatorname{flat}(\neg\theta)&=\neg P_\theta,\\
\operatorname{flat}(\theta\land\eta)&=P_\theta\land P_\eta,\\
\operatorname{flat}\!\left(C+\sum_t\alpha_t\#\theta_t\diamond k\right)
&=C+\sum_t\alpha_t\#P_{\theta_t}\diamond k.
\end{aligned}
\]

Every flattened formula has depth at most one. Require

\[
(\#\top>0)\land P_{\mathrm{root}}\land
\bigwedge_\chi\left(\#[P_\chi\mathbin{\mathrm{xor}}
\operatorname{flat}(\chi)]=0\right).
\tag{5}
\]

The explicit length guard excludes the empty word. The outer counts make these constraints depth at most two. Evaluated at the final position, each zero count enforces the corresponding equality at every position. Induction over the original DAG, with correctness at all positions as the invariant, proves that every annotation bit is the true value of its original subformula. This handles counts reading earlier positions without circularity. The root bit then enforces original acceptance. Conversely, annotating every position with its actual subformula truth values satisfies (5).

The conversion is effective and preserves nonempty satisfiability. It may have exponential alphabet or description growth. No fixed-binary-alphabet or polynomial-size reduction is claimed here. Empty-word acceptance can alternatively be checked separately. With the corrected block encoding, this supplies the logical depth-two undecidability route under the standard Diophantine undecidability premise.

A computable uniform short-witness bound would decide emptiness by checking all words up to that bound, since membership is decidable. Thus it cannot exist for this general signed class. This conclusion concerns the class with its finite alphabet represented as part of the input. A separately fixed alphabet or a differently bounded syntax requires its own reduction.

## 5. Quantitative transformer translations still need repair

### 5.1 The denominator cannot be clipped at the activation maximum

Appendix B defines a binary grid (\mathbb F) with downward rounding. With (p=4,s=1), its step is (1/2) and maximum is (3.5). The attention denominator is the untruncated sum

\[
A_{ij}=\operatorname{round}(e^{q_i k_j}),\qquad
B_i=\sum_{j\le i}A_{ij},\qquad
\alpha_{ij}=\operatorname{round}(A_{ij}/B_i).
\]

The proposed logic simulation on pp. 18–19 instead first clips (B_i) to the maximum of (\mathbb F). Take three positions with all scalar queries and keys equal to one. Then

\[
A_{ij}=2.5,\quad B_i=7.5,\quad
\alpha_{ij}=\operatorname{round}(1/3)=0.
\]

Clipping the denominator first gives

\[
\widetilde\alpha_{ij}
=\operatorname{round}(2.5/3.5)=1/2.
\]

For values all equal to one, the true context is zero, while these erroneous weights produce a weighted sum of (1.5). This last quantity is not asserted to be the output of the entire subsequent compiler. Its later enumeration assumes at most (2^s) positive weights, and the erroneous weights already violate that premise. That restriction cannot repair the preceding weight mismatch.

### 5.2 Fixing the query value does not remove the query position

The predicate written (P_{\alpha_q}) at position (j) is supposed to represent a weight after fixing (q). Its right-hand side still depends on the denominator at the current query position (i). This is not a point-wise function of data at (j).

For a separate example with no denominator overflow, take the same grid and all queries and keys zero. Each unnormalized weight is one. For the same key position (j=1), query positions (i=1,2,3) give weights (1,1/2,0), respectively. A single predicate evaluated at the unchanged position (w,1), with only (q=0) fixed, cannot represent all three values.

A possible repair direction is to enumerate both query (q) and denominator (b). Compute the key-local weight (\operatorname{round}(A_{q,j}/b)), then select the aggregate at the query position using its actual (q_i) and (B_i). If the grid step is (\Delta) and maximum is (M_F), a denominator greater than (M_F/\Delta) does make every weight round to zero. One can therefore investigate exact enumeration below that larger threshold plus a separate all-zero branch. Zero denominators, bit costs and the full inductive construction still need treatment. This note does not claim that repair is complete.

### 5.3 Other local translation conditions

Lemma B.9's finite-function disjunction tests the one bits of each input pattern but omits its zero bits. An arbitrary finite function requires exact-pattern tests, including negative literals. Adding them is a local repair with the same coarse exponential enumeration cost.

The reverse construction in Theorem B.11, p. 21, asks for a finite binary fixed-point grid containing (1/k) and states that this is always possible. It is impossible for (k=3). Its displayed average also drops coefficients from the preceding general linear predicate and uses an unrounded-weight averaging expression instead of the specified individually rounded weights. These are genuine proof-interface requirements, not counterexamples to the existence of some other compiler.

The author bound for the forward compiler is

\[
O\!\left(|\Sigma|L p^2d\,2^{p^3d}\right)
\]

with depth (O(L)), precision (O(p)) and girth (O(p)). If an appropriate compiler with these controls is repaired, the independent witness lemma would give a singly exponential transformer length bound. Until then, the positive-logic result, the source's claimed transformer result and a fully justified quantitative bridge remain separate.

## 6. Research use and limits

The most reusable mathematical instrument here is the witness-retention argument. Nonnegative counting arithmetic with fixed numerical thresholds permits saturation without changing any Boolean decision, even when counted predicates are nested and negated. Signed cancellation removes that direct argument. Neither fact implies that an unknown predictive state, a reusable program library or a useful decomposition will be learned from data.

The note also gives exact examples showing why the current printed reductions cannot simply be quoted as complete constructions. The corrected logical route is explicit. The quantitative transformer route is not fully repaired. Appendix A's comparisons with earlier restricted C-RASP and transformer models were read, but their complete separation arguments and external dependencies were not independently certified.

No FP definition, architecture, experiment or learning rule is proposed or changed. There is no FP transfer theorem in this reading. The paper's exact membership-label interface, known description bound, syntax conventions and rounding order must remain visible in any later comparison.
