# Bshouty–Haddad 2024 — sparsity approximation and proper noisy parity learning

## Source and actual coverage

Nader H. Bshouty and George Haddad, *Approximating the Number of Relevant Variables in a Parity Implies Proper Learning*. APPROX/RANDOM 2024, LIPIcs 317, article 38, pp. 38:1–38:15. Published September 16, 2024. Peer-reviewed conference version, DOI [10.4230/LIPIcs.APPROX/RANDOM.2024.38](https://doi.org/10.4230/LIPIcs.APPROX/RANDOM.2024.38).

[Official record](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.APPROX/RANDOM.2024.38) · [Complete proceedings PDF](https://drops.dagstuhl.de/storage/00lipics/lipics-vol317-approx-random2024/LIPIcs.APPROX-RANDOM.2024.38/LIPIcs.APPROX-RANDOM.2024.38.pdf)

Read November 25, 2026, Shanghai. The main assistant covered all 15 PDF pages through reliable extracted text, including §§1–3.2, the two introductory proof approaches, every theorem and proof, all ten footnotes, acknowledgements and all 36 references. There are no figures, tables or separate appendices. The PDF was opened in continuous overlapping blocks through its final line. The image endpoint returned text placeholders, so no image-based formula verification is claimed. The formulas used below were read in the original PDF's text extraction. This is complete text reading, not a whole-paper independent proof certificate or a formal verification.

The paper is a conditional reduction result. It does not supply a polynomial-time noisy parity learner or an unconditional computational lower bound.

## Original question and model

For a linear function over a finite field, d(f) counts nonzero coefficients. Binary linear functions are parities. Samples have independent uniform inputs from the full ambient vector space. A label equals the target with probability 1−eta and otherwise is uniform among the other field elements. The learner knows an upper bound eta_b below the uniform-label threshold 1−1/q, where q is the field size. It need not know eta itself.

For increasing gamma, the approximation task returns D between gamma^{-1}(d(f)) and gamma(d(f)), with success probability at least 2/3, uniformly over targets. The formal statements use gamma(x)>x. The introductory statement allows equality. Proper learning must return the exact coefficient vector, rather than only a predictor of small error.

The operative meaning of polynomial time includes polynomial dependence on the inverse noise gap

\[
g^{-1}=(1-\eta_b-1/q)^{-1}.
\]

Consequently, polynomial in dimension is not automatically polynomial in all physical parameters when the gap shrinks exponentially with another parameter. Integer rounding in the dimension and sparsity expressions is left at the paper's asymptotic level.

## Principal statements

**Binary result, Theorem 1 and its generalization Theorem 6.** A polynomial-time gamma approximation valid for every target yields a polynomial-time proper learner for some unbounded sparsity sequence k(n). It is not a learner for every prescribed k(n). The finite-field theorem retains field-size and noise dependencies. For any chosen diverging pi(n), the displayed time dependence is polynomial in

\[
n,\quad g^{-1},\quad
\min\{q,(1-\eta_b)^{-\pi(n)}\}.
\]

The construction selects k(n) in a range whose lower endpoint diverges and whose upper endpoint is controlled by pi(n). For binary fields, the field-size factor is constant.

**General learner, Theorems 2 and 11.** Write Gamma=gamma composed with gamma. An approximation algorithm taking time T(n) and Q(n) examples yields exact proper learning. The explicit finite-field statement on p. 38:12 gives

\[
\widetilde O(q\Gamma(n)^{12})
T(O(\Gamma(n)^2))\log(1/\delta)
\]

time and

\[
\widetilde O(\Gamma(n)^8)
Q(O(\Gamma(n)^2))\log(q/\delta)
\]

examples. Noise-gap dependence is already part of T and Q. The ambient dimension inflation is essential. A very rapidly growing approximation factor can make this reduction very expensive. In particular, the first theorem's weak approximation conclusion should not be rewritten as an unconditional polynomial-time algorithm for all parities.

The historical subexponential benchmarks in the introduction describe the literature available to the 2024 authors. They were not independently refreshed as 2026 best-known complexity claims.

## Proof structure and dependencies

1. **Hypothesis selection and amplification, Lemmas 3–5.** Under uniform inputs, an incorrect linear function agrees with noisy labels with probability 1/q, whereas the target agrees with probability at least 1−eta_b. Empirical agreement selects among a finite candidate set using a sample count proportional to its logarithmic size and g^{-2}. Repeating approximation and taking a median amplifies success. Repeating an exact proper learner and taking the most frequent coefficient vector also amplifies success.

2. **A calibrated approximation statistic, Lemma 7.** The authors first amplify the approximator at a fixed small failure probability delta', then transform and cap its output to the interval from d to Delta(d), where Delta(d)=min(Gamma(d),n). They define Psi_A(d) through uniform random d-sparse functions and successful internal randomness. Synthetic labeled examples at a known noise level permit estimating this statistic without drawing examples from the unknown target. Hoeffding concentration controls the calibration table.

3. **Simulating the calibrated distribution, Lemma 8.** Random coordinate permutations and nonzero coordinate rescalings turn any fixed d-sparse linear function into a uniformly random member of that class. This can be done by transforming already obtained uniform examples. It does not require querying the target on selected new inputs. The fixed delta' matters when accumulating the chance of unsuccessful approximation runs.

4. **Finding a useful sparsity gap, Lemma 9.** A telescoping sum locates nearby sparsity levels at which Psi_A changes by an inverse-polynomial amount. In the binary case, adding one coordinate to each label changes the target sparsity to k−1 or k+1, depending on whether that coordinate is relevant. Their separated calibrated outputs reveal relevance. Over larger fields, two nonzero perturbations distinguish relevance, followed by coefficient recovery.

5. **Recovering coefficients, Lemma 10.** Once the support is known, repeated small batches and Gaussian elimination give a correct candidate when a batch is both noiseless and full rank. The displayed nonsingularity probability is bounded below by 1/4. Independent hypothesis selection chooses the correct candidate. This is a potentially expensive alternative whose dependence on k and noise is retained in Theorem 6.

6. **Covering all sparsities, Lemmas 12–13.** Randomly adding unused coordinates increases a d-sparse target to a learnable larger sparsity. Enlarging the ambient dimension to 12 Gamma(n)^2 makes collision unlikely. Extra coordinates in examples are generated independently and uniformly. Running the relevant learners and selecting among their candidates completes the general reduction.

The second approach in §1.2.2, credited to an anonymous reviewer and the earlier cryptographic reduction of Blum et al., first separates two sparsity ranges. At least one range can then be distinguished from uniformly random labels. Replacing one input coordinate by a fresh uniform value makes labels independent of the input exactly when that coordinate was relevant. This yields support identification. Its known noise upper bound also supplies a finite running-time cutoff on uniform-label inputs.

For unknown eta, §1.2.1 describes guessing a sufficiently fine noise grid, adding independent label noise to approach a common eta_b, controlling the resulting distributional error, and selecting among hypotheses. This handling is part of the authors' proof outline. No independent full quantitative certification of that grid argument or every finite-field bookkeeping step was performed.

The principal external dependencies are Angluin–Laird's noisy-example model and hypothesis selection, the Blum–Furst–Kearns–Lipton search/decision technique, and the noisy-parity complexity literature cited for context. Reading their use here does not make those cited works fully read.

## Evidence, limitations and bounded independent checks

This is a theorem paper without experiments. No training run, implementation comparison, benchmark or code artifact establishes its conclusions. The evidence is the reductions and concentration arguments under the specified oracle.

**Agreement calculation checked.** If f and h are distinct linear functions, f−h is a nonzero linear map. On a uniform input it is uniform on the field. The independent additive classification noise therefore gives Pr[h(X)=label]=1/q. This directly verifies the central finite-candidate separation in Lemma 3. It does not apply unchanged to arbitrary nonuniform input distributions or arbitrary target-dependent label corruption.

**Padding bound checked.** Let r=k−d. Sampling r distinct coordinates uniformly gives exact probability

\[
\Pr[\text{avoid the true support}]
=\frac{\binom{n-d}{r}}{\binom nr}
=\prod_{j=0}^{r-1}\left(1-\frac{d}{n-j}\right).
\]

A union bound using the marginal selection probability r/n gives

\[
\Pr[\text{avoid support}]\ge 1-\frac{dr}{n}
\ge 1-\frac{k^2}{n}.
\]

Thus the required 11/12 bound follows from 12 Gamma(d)^2≤n and k≤Gamma(d). If sampling independently with replacement, the sufficient event that all new coordinates are distinct and avoid the support has probability product over j=0,...,r−1 of (1−(d+j)/n), with the same coarse k^2/n bound.

The extracted display on p. 38:13 gives a product indexed from d through k as an equality for the success probability. That is not the exact no-replacement probability above and even gives a non-unit value when k=d. The intended lower bound has the direct repair just derived. Because the image endpoint was unavailable, this observation is explicitly tied to the PDF extraction rather than a claim to have inspected its rendered glyphs. It does not refute the padding reduction or the main conditional result.

No full independent audit, exhaustive search or formal proof was undertaken. In particular, do not import the result as an impossibility theorem for unrestricted learning, as a lower bound on physical state count, or as an adaptive rereading result.

## Separate interface comparison with Astra's e79bc90 registration

This section is an independent elementary model calculation. It is not claimed as a theorem in the paper and does not change FP's theory or experimental registration.

**Objects and assumptions.** Let m=d−1 latent input bits X be independent uniform bits. Let the latent target be b XOR parity_S(X), with unknown support S and intercept b. Each coordinate report, including the target, has an independent BSC error. Define rho=1−2p, where p is its flip probability, and suppose 0<rho<1. Rows reset independently. This is precisely a single-report-per-coordinate comparison, with the row partition and coordinate identities available.

Write Z=X XOR N for the observed inputs and W for the observed target. Then

\[
W=b\oplus\operatorname{parity}_S(Z)\oplus E,\qquad
E=N_y\oplus\bigoplus_{i\in S}N_i.
\]

For every z and noise vector a,

\[
\Pr(Z=z,N=a)=2^{-m}\Pr(N=a).
\]

Hence Z is uniform and independent of all the report errors. Therefore E is independent of Z and

\[
1-2\eta_{\rm eff}
=\mathbb E[(-1)^E]
=\rho^{|S|+1}.
\]

If the registration calls s=|S|+1, the effective label-noise rate is (1−rho^s)/2. Its binary noise gap is rho^s/2. This exact distributional mapping includes noisy input reports, rather than silently assuming those reports are clean.

**Usable conclusion.** A single-read row is an ordinary uniform-example noisy affine parity sample at that effective noise rate. The unknown intercept can be handled by two label orientations, a time-bounded learner, and independent hypothesis comparison. Appending a constant input coordinate would instead violate the full uniform-input premise. The same finite-candidate agreement argument gives a sufficient sample order

\[
O\!\left(\frac{\log |{\cal C}|+\log(1/\delta)}
{\rho^{2s}}\right)
\]

for exhaustive identification in a fixed-s affine candidate class. This is a sufficient statistical bound with an explicit enumeration cost, not an efficient algorithm or a matching lower bound proved here.

**Limits of transfer.** Knowing s already solves the support-size estimation question by returning s−1. It does not solve support identification. Bshouty–Haddad require a single approximation algorithm valid across all target sparsities at the stated ordinary label-noise interface. A fixed-s learner or a constant estimator on a promised slice does not satisfy that premise. If support size is unknown, the effective noise rate also changes with the support. A theorem parameterized by a noise upper bound must use an appropriate uniform upper bound, potentially with an exponentially small gap. A guarantee whose time is polynomial in the inverse gap is then compatible with exponential dependence on s.

There is also a closure issue. The reduction transforms W to W XOR Z_i, changing the target support from S to its symmetric difference with {i}, while preserving the existing independent error E and its bias rho^{|S|+1}. A physical model with fixed rho would prescribe a different bias for the new support size. Thus success on the original physical family alone does not establish success on every transformed dataset used by the reduction. Coverage of arbitrary allowed label-noise rates, or a justified calibration construction, is an additional requirement.

Repeated nondestructive reports of the same latent coordinates introduce shared latent information across reports. They are not independent fresh LPN rows. This paper supplies no lower bound against Astra's repeated-coordinate experiment, no discovery theorem for its majority/elimination rule, and no finite-state or longer-sequence generalization result. Such conclusions need their own access model and proof.

**Testable identity only.** Under the stated single-read simulator, signed correlation between the observed target and the correct observed affine parity must be rho^s. Nonuniform latent inputs, dependent report noise, missing row identities or selection of rows can invalidate the independence argument. This identity is the proposed diagnostic, not a new experimental mandate.

## Necessary follow-up

The closest recent complementary lead is Gu–Li–Xu, COLT 2026, on repeated noisy queries to a known Boolean function. Its primary abstract states a total-influence lower bound, but its complete proof was not part of this reading. CAPAL, ICLR 2026, has a different persistent membership-noise model and a perfect equivalence oracle. Its complete source has become accessible and is next for reading after this paper's publication and a request check.

For this paper, a later available image rendering can resolve the literal product display without rereading the completed text. No blanket historical queue is opened. The finite-field and unknown-noise proof bookkeeping remains author-established rather than independently certified.
