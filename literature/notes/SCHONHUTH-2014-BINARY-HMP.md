# SCHONHUTH-2014-BINARY-HMP — Generic identification of binary-valued hidden Markov processes

## Source and reading status

Alexander Schönhuth. *Generic identification of binary-valued hidden Markov processes*. Journal of Algebraic Statistics **5**(1), 72–99 (2014). DOI [10.18409/jas.v5i1.26](https://doi.org/10.18409/jas.v5i1.26).

Edition read in full: [arXiv:1101.3712v6](https://arxiv.org/abs/1101.3712v6), dated October 22, 2013, 28 pages. The main assistant personally read the complete TeX source, including definitions, every proof, Algorithm 7.2, acknowledgements and all 40 bibliography entries. There are no separate proof appendices or graphical figures in this edition. Dense statements and reconstruction formulas were checked on PDF pp. 16–17 and 19. The complete algorithm and its following formulas were checked visually on pp. 24–25.

Local sources:

- literature/corpus/peer_reviewed/predictive_operator_prior_art/schoenhuth-1101.3712v6.pdf
- literature/corpus/peer_reviewed/predictive_operator_prior_art/schoenhuth-tex/BinHMMId.tex
- literature/corpus/peer_reviewed/predictive_operator_prior_art/schoenhuth-1101.3712v6-source.tar

The [institutional copy of the journal version](https://repository.iit.edu/islandora/object/islandora%3A1007820/datastream/OBJ/download/Generic_Identification_of_Binary-Valued_Hidden_Markov_Processes.pdf) was separately inspected through its primary web extraction for Remark 6.7 and pp. 95–96. Those passages retain the length-bound statement and the algorithm expressions discussed below. Direct download returned HTTP 503. This is a complete reading of v6, with selected journal-version comparisons, not a claim to have independently read every word of a second edition.

The paper is human-authored reviewed research. Complete reading and the limited checks below do not certify all its results.

## Original problem

The paper asks when a finite-alphabet stochastic process is a hidden Markov process, and how its parameters can be recovered from exact word probabilities. It distinguishes two questions.

**Complete identification** asks whether the entire process has some finite hidden-state realization. **Finite identification** starts with the distribution on words of a fixed length n and a proposed state bound d. A finite distribution alone cannot settle complete identification without additional restrictions: it can be extended to a hidden Markov process and also to an infinite process outside that class. An unbounded sequence of finite tests is consequently different from a terminating decision procedure on one finite window.

The intended main result is generic finite identification for binary outputs when n ≥ 2d−1. “Generic” means outside a lower-dimensional algebraic exceptional set in the parameter space. It is not a uniform guarantee for every parameter choice, a finite-sample estimation theorem, or a statement that small empirical errors lead to small parameter errors.

The geometric part is broader. It characterizes polynomial invariants of finite-rank process models for arbitrary finite output alphabets, and shows that their algebraic varieties agree with those of d-state hidden Markov models when the alphabet is binary.

## Definitions and conventions

For a word w = a₁…aₙ, p(w) is its cylinder probability. Empty-word probability is one for a normalized process. Right consistency is

\[
p(u)=\sum_{a\in\Sigma}p(ua).
\]

This lets every probability of a shorter word be expressed as a linear combination of length-n probabilities. The paper can therefore work in one finite polynomial ring without introducing a separate elimination problem for shorter words.

Stationarity adds left consistency,

\[
p(v)=\sum_{a\in\Sigma}p(av).
\]

These are distinct constraints. On Hankel matrices, right consistency constrains columns and stationarity gives the corresponding condition on rows. The algebraic treatment does not assume stationarity. Its stationary locus is an additional subvariety, so a statement generic in the ambient family cannot be restricted to an arbitrary subvariety without checking the exceptional set.

A finitary representation has real matrices T_a and a vector π with

\[
p(a_1\cdots a_n)=\pi^\top T_{a_1}\cdots T_{a_n}\mathbf1,\qquad
\left(\sum_aT_a\right)\mathbf1=\mathbf1,\qquad
\pi^\top\mathbf1=1.
\]

The probabilities must be nonnegative, but the realization matrices need not be entrywise nonnegative. Its rank is the least possible realization dimension.

A d-state hidden Markov process in this paper is a **state-emitting** model with nonnegative row-stochastic transition matrix M, row-stochastic emission matrix E and initial distribution π. Writing O_a for the diagonal matrix of emission probabilities gives

\[
T_a=O_aM,\qquad \sum_aT_a=M.
\]

Every such model is finitary of rank at most d. The converse with the same state count is not asserted. Finitary rank, a chosen representation dimension and the number of states in a nonnegative hidden Markov realization are different quantities.

The algebraic parameter spaces are complexified. They retain the row-sum constraints but omit the normalization of the initial vector. This removes an inhomogeneous equation and adds one dimension relative to the normalized stochastic family. Algebraic membership by itself does not establish positivity.

## Results and argument through the paper

### Sections 2–4: polynomial process models

The family of polynomial maps for successive word lengths respects marginalization. Hidden Markov parameterizations embed into finitary parameterizations through T_a = O_aM. Hence their images and Zariski closures are nested, while the corresponding invariant ideals have reverse inclusion.

Example 3.9 supplies a full-rank hidden Markov model. Take M = I, a uniform initial distribution and distinct emission probabilities λ₁,…,λ_d for one letter. The Hankel submatrix indexed by powers of that letter is a Vandermonde Gram matrix and has rank d. This proves that rank-d examples exist. Its transition matrix is the identity. It does not establish a sharp lower construction with a strictly positive transition matrix.

### Section 5: dimensions, fibers and the special binary case

For n ≥ 2d−1, minimal finitary realizations representing the same distribution are related by an invertible change of coordinates S satisfying S1 = 1. The generic fiber dimension is d(d−1). The resulting finitary variety dimension is

\[
\dim V_{\mathcal M_d,n}=(|\Sigma|-1)d^2+d
\]

for an alphabet of at least two letters. The unary case has dimension one.

For hidden Markov models, the exceptional locus includes rank below d, singular M, and emission configurations without the required simple spectrum. Outside that locus, hidden-state permutations account for d! equivalent parameterizations. The author uses earlier stationary identification arguments, explaining their extension to nonstationary and complex parameters. This yields

\[
\dim V_{\mathcal H_d,n}=d^2+(|\Sigma|-1)d.
\]

For two outputs these dimensions agree. Inclusion and irreducibility then yield equality of the two Zariski closures, and hence equality of their invariant ideals.

The conclusion concerns complex algebraic closures. It does not say that every positive binary finite-rank process has a d-state stochastic realization. The later algorithm still has to test whether the recovered parameters are real and stochastic. For larger alphabets, the dimension comparison generally separates the model classes.

### Section 6.1: finite Hankel rank and the word-length upper bound

The Hankel matrix is

\[
H_p=(p(uv))_{u,v\in\Sigma^*}.
\]

Theorem 6.6 identifies finite Hankel rank with a finite linear representation compatible with right consistency. An intermediate form has a terminal vector y satisfying (\sum_aT_a)y = y. A suitable similarity transform puts that vector into the all-ones convention.

For a process function of rank at most d, prefixes and suffixes of length at most d−1 span the relevant spaces:

\[
\operatorname{rank}H_p
=\operatorname{rank}H_{p,d-1,d-1}.
\]

A basis block uses word lengths through 2d−2. Inserting a central letter into that block uses length at most 2d−1. Those shifted blocks determine all the operators, and thus the whole process within the rank bound. The key statements are equations (6.11)–(6.12), with the explicit reconstruction in Lemma 6.12.

Remark 6.7 distinguishes generic hidden Markov identifiability at potentially shorter lengths from identification throughout the class. It states that shorter strings no longer uniquely determine hidden Markov processes. The remark does not exhibit a pair of strictly positive, stationary, exactly rank-d processes over three letters with agreement through length 2d−2. Nor does it discuss the predicate that two particular output letters have identical normalized operators. It is a useful historical statement about sharpness, but it is not, on its own, a source for that more specific construction.

### Section 6.2: finite invariant equations

Let I_{d+1,n} be generated by the (d+1)-minors of the two rectangular Hankel blocks whose row and column lengths are bounded by floor(n/2) and ceil(n/2), in both orders. Let J_{d,n} be generated by the d-minors of H_{p,d−1,d−1}. Theorem 6.10 states

\[
I_{\mathcal M_d,n}=\sqrt{I_{d+1,n}}:J_{d,n},\qquad n\ge 2d-1.
\]

For a binary alphabet this is also I_{\mathcal H_d,n}. The colon denotes an ideal quotient.

The rank-stratum argument matters. Vanishing (d+1)-minors alone can introduce unwanted components because Hankel entries are repeated and marginalization introduces further dependencies. The rank-d stratum is isolated by requiring at least one nonzero d-minor. Taking its Zariski closure and translating the difference of varieties into an ideal quotient yields the theorem. The paper reports a nonprime I_{3,4}, so one cannot invoke the familiar primality theorem for a generic matrix of independent indeterminates.

The radical is retained in the general formula. The author reports that it is unnecessary in a small d = 2, n = 3 computation, while leaving its necessity in general open. This note has not rerun the reported Macaulay or Bertini calculations.

Lemma 6.12 supplies the constructive step. It equates membership in the exact rank-d finitary image with equality of the ranks of the small square Hankel block and both larger rectangular blocks. Choose an invertible block

\[
V=(p(v_iw_j))_{i,j=1}^d,
\]

then set

\[
x^\top=(p(w_1),\ldots,p(w_d)),\qquad
y=V^{-1}(p(v_1),\ldots,p(v_d))^\top,
\]
\[
W_a=(p(v_i a w_j))_{i,j=1}^d,\qquad
T_a=V^{-1}W_a.
\]

Two induction lemmas propagate the chosen row coordinates and the terminal evaluation. Splitting a word into a permitted prefix and suffix proves p(u)=xᵀT_uy throughout the observed length range. Right consistency then gives (\sum_aT_a)y=y. This produces an extension with the desired finite representation. The proof does not presume independent indeterminates at every Hankel position.

The final ideal argument uses irreducibility and the dimension formulas to show that the closure of the exact rank-d stratum is the full rank-at-most-d model variety.

### Section 7: reconstruction and the stochasticity test

The intended procedure examines possible ranks, tests the finite Hankel rank equalities, constructs a finitary realization, and attempts to conjugate it into hidden Markov form.

For binary outputs, write T = T_a+T_b. If T is invertible, the matrix T_aT^{-1} plays the role of an emission operator. Under the stated simple-spectrum condition it can be diagonalized. The same change of coordinates transforms T into a candidate transition matrix and transforms the initial vector. The final test asks whether the resulting parameters are stochastic.

The generic uniqueness argument is what makes a negative stochasticity test meaningful in its intended regular regime: hidden-state permutations cannot turn invalid entries into a stochastic realization. Degenerate rank, singularity and repeated spectral values require separate handling. The printed algorithm and the introductory three-way decision statement also need to be distinguished, as described below.

## Limited independent checks and implementation cautions

These are observations from this reading, not claims made by the author and not a general disproof of the paper's algebraic results.

### 1. The printed determinant test is too strong

Algorithm 7.2, line 5, prints det(T_a+T_b) > 0. Its following explanation requires invertibility, which is det(T_a+T_b) ≠ 0. Both the v6 PDF and the primary extraction of journal p. 95 have the strict-positive version.

A direct two-state example shows the distinction is consequential. Take

\[
M=\begin{pmatrix}1/4&3/4\\3/4&1/4\end{pmatrix},\quad
O_a=\operatorname{diag}(1/4,3/4),\quad
O_b=I-O_a,\quad
\pi^\top=(1/2,1/2).
\]

This is a stationary state-emitting model with strictly positive transition and emission probabilities. It has

\[
\det M=-1/2,\qquad
p(a)=1/2,\qquad p(aa)=7/32.
\]

Its Hankel block on the empty word and a has determinant

\[
\det\begin{pmatrix}1&1/2\\1/2&7/32\end{pmatrix}=-1/32,
\]

so the process has rank two. M is invertible and O_a has distinct eigenvalues, placing it outside the particular exceptional conditions used here. A similar realization retains det(T_a+T_b)=−1/2. At n=3, the literal determinant test rejects it. Negative determinant, strict positivity and nonzero rank persist in a neighborhood, so this is not merely an isolated algebraic exceptional point.

The nonzero test is the correction suggested by the surrounding proof. This limited calculation does not certify the rest of the implementation.

### 2. Keep all matrices in the same basis

After defining M=S^{-1}TS, the printed reconstruction writes O_a=T_aM^{-1}. Unless T_a has silently been reassigned to the transformed operator, this combines two bases. The coordinate-consistent expression is

\[
O_a=(S^{-1}T_aS)M^{-1}
=S^{-1}T_aT^{-1}S.
\]

The same issue applies to b. The selected journal passage retains the printed formula. An implementation must make the conjugation explicit.

Equation (6.9) also reverses the operator order while displaying a similarity transform. A similarity transform preserves the order T_{a_1}…T_{a_n}. This is a local displayed-formula problem, not a reason to reverse the process convention.

### 3. Generic failure handling needs care

The introduction describes a three-way answer including an undecidable exceptional case. The printed Algorithm 7.2 instead terminates with a negative answer in cases for which Lemma 7.3 acknowledges possible erroneous rejection. Its proposed generic scope is therefore essential. It should not be copied as a certified universal recognition algorithm, even after repairing the two expressions above.

### 4. Exact algebra is not a sampling guarantee

The paper starts from exact word probabilities. It provides no uniform finite-sample bound for recovering a rank, testing exact equality, selecting a well-conditioned Hankel basis or distinguishing nearly repeated eigenvalues. Positivity of probabilities does not by itself supply these margins.

## Evidence from computations and limits of this reading

The paper reports algebraic computations supporting nonprimality, small-case radical behavior and dimension checks. It does not present a predictive benchmark or an empirical learning comparison. The proof structure and those reported calculations have different evidentiary roles.

This reading covers the full text and bibliography. It follows the dimension, reconstruction and ideal arguments, and checks the concrete determinant counterexample above by elementary arithmetic. It does not establish a new proof of generic identifiability, rerun the computer algebra, verify every cited theorem or solve the nonnegative-realization problem.

The bibliography provides a useful primary-source trail: Blackwell–Koopmans (1957), Gilbert (1959), Dharmadhikari, Heller (1965), Paz (1971), Ito–Amari–Kobayashi (1992), Jaeger (2000), Allman–Matias–Rhodes (2009), and Faigle–Schönhuth (2011). Having read these references in the bibliography does not count as reading those papers.

## Scope for the outstanding prior-art request

This paper gives an explicit primary source for the classical upper bound and for the difference between generic and worst-case identification. Its rank-d model includes general linear process realizations, but its d-state hidden Markov model has the narrower state-emitting factorization T_a=O_aM.

It does not by itself settle whether an earlier theorem already implies the requested **three-letter, strictly positive, stationary, rank-exact lower construction for equality of normalized output operators**. That question remains open in this reading record pending a targeted check of the older sharp examples. No FP mechanism or architectural consequence is inferred from the paper's terminology or algebraic resemblance.

## Subsequent request status

The bounded prior-art request was subsequently completed. See [the source-grounded reply](REQUEST-2026-11-23-OUTPUT-OPERATOR-PRIOR-ART.md) for the limited negative result, remaining access gaps and separate Moore-subclass deduction. The earlier description of an open request records the status at this paper’s reading boundary.
