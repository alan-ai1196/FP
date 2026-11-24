# Koskela et al. — A debiased Bernoulli factory and unbiased estimation of a probability

## Edition, sources and actual coverage

Jere Koskela, Toni Karvonen, Krzysztof Łatuszyński and Dario Spanò. **arXiv:2510.01941v2**, submitted September 1, 2026, 09:49:31 UTC; first version October 2, 2025. No peer-reviewed venue was authenticated in this reading. This is not an official OpenAI or Anthropic release.

- [Versioned metadata](https://arxiv.org/abs/2510.01941v2), [complete HTML](https://arxiv.org/html/2510.01941v2), [10-page PDF](https://arxiv.org/pdf/2510.01941v2), [TeX source](https://arxiv.org/src/2510.01941v2).
- **Fully read by the main assistant, November 25, 2026 Shanghai:** all ten pages, §§1–5, every stated result and proof, formulas, acknowledgments and all 21 bibliography entries. The manuscript has no figures, tables, body footnotes or appendices. Continuous primary HTML reading was cross-checked with the complete TeX package and original PDF layouts on pp. 4, 6–8, including the problematic variance display.
- Local retrieved source: `tmp/source_candidates/2510.01941v2/`, containing the 260,511-byte PDF, source archive, `debiasing-factory.tex` and bibliography. These are temporary retrievals; the versioned original URLs are the recovery sources.
- Independent work was limited to the counterexample to Corollary 1, a replacement for the final coefficient-bound step, and the truncation-cost calculation below. A supporting assistant checked these three points. No full-paper certification, numerical replay, proof script or formalization was performed.

The separately cited Holtz–Nazarov–Peres (HNP) paper is **only partially read**: [publisher version, DOI 10.1007/s00365-010-9108-5](https://doi.org/10.1007/s00365-010-9108-5), *Constructive Approximation* 33, 331–363 (2011), first online June 11, 2010. The scoped reading covered printed pp. 333–334 (definitions and Result 3), p. 337 (Theorem 8 and the beginning of Lemma 9), and pp. 354–356 (end of an estimate, Steps 3–5, Eqs. 47–50 and Lemma 25). Original p. 355 was visually checked. Its other pages and full bibliography were not read.

## Original problem and contribution

A known function \(f:[0,1]\to(0,1)\) must be evaluated without access to its argument \(x\). Instead, independent \(X_i\sim\operatorname{Ber}(x)\) can be sampled. The paper constructs an unbiased estimator \(\psi\) with support in \([0,1]\). A further independent draw with success probability \(\psi\) then gives a Bernoulli random variable with parameter \(f(x)\), by conditioning.

The distinguishing feature is **non-adaptivity of the input count**: the random number of input coins is chosen independently of their outcomes and can be sampled before them. It is neither a deterministic maximum query count nor a finite-state-machine restriction. The construction combines the consistent Bernstein approximations underlying Nacu–Peres/HNP factories with randomized telescoping debiasing of McLeish and Rhee–Glynn.

The introduction situates this among simulation, exact Bayesian methods, diffusion sampling, and the constraints on nonnegative unbiased transformations studied by Jacob–Thiéry. These are motivations and imported results, not new empirical demonstrations. Ordinary debiasing can produce negative values even from nonnegative approximants; maintaining both lower and upper bounds is the central issue here.

## Approximation assumptions are coefficient assumptions

For integer \(\rho\), \(C^\rho\) has its usual continuous-derivative meaning; for noninteger \(\rho\), the highest derivative has Hölder exponent \(\rho-\lfloor\rho\rfloor\). The spaces are nested. The imported HNP theorem is stated for noninteger smoothness; the main theorem treats integer exponents by moving to a slightly smaller noninteger exponent while retaining the strict parameter inequalities.

Theorem 1 supplies polynomials

\[
g_n(x)=\sum_{j=0}^n {n\choose j}a(n,j)x^j(1-x)^{n-j},\qquad
h_n(x)=\sum_{j=0}^n {n\choose j}b(n,j)x^j(1-x)^{n-j},
\]

with \(0\le a(n,j)\le b(n,j)\le1\), both converging to \(f\), and

\[
0\le h_n(x)-g_n(x)\le Cn^{-\rho/2}
\]

uniformly on the whole closed interval. For \(m\le n\), define the degree-elevated lower coefficient

\[
H_n(m,j)=\sum_i
\frac{{n-m\choose j-i}{m\choose i}}{{n\choose j}}a(m,i).
\]

The required compatibility is

\[
a(n,j)\ge H_n(m,j),\qquad
b(n,j)\le\sum_i
\frac{{n-m\choose j-i}{m\choose i}}{{n\choose j}}b(m,i).
\tag{3–4}
\]

These are coefficient inequalities under hypergeometric averaging. Pointwise convergence, even with coefficients in \([0,1]\), does not substitute for them. They imply the one-sided monotonicity needed in the proof, and hence \(g_n\le f\le h_n\).

HNP's original rate is expressed through \(\Delta_n(x)=\max\{\sqrt{x(1-x)/n},1/n\}\); its uniform consequence is the rate used here. HNP Result 3 explicitly uses the Bernstein coefficient order. The older source also accounts for fair-coin randomization and rounding; reading this dependency statement is not independent certification of HNP's full constructive approximation argument.

## Randomized telescoping estimator

Independently of all input coins, sample

\[
\Pr(L=n)=\frac{n^{-\lambda}}{\zeta(\lambda,k)},\quad n\ge k,
\qquad \lambda>1,
\quad \zeta(\lambda,k)=\sum_{j=k}^{\infty}j^{-\lambda}.
\]

Write \(S_L=\sum_{i=1}^L X_i\) and \(q_n=\Pr(L\ge n)=\zeta(\lambda,n)/\zeta(\lambda,k)\) for \(n\ge k\). Lemma 1, imported from Nemes' zeta expansion, gives

\[
\left|\zeta(\lambda,k)-\frac{k^{1-\lambda}}{\lambda-1}\right|
\le\frac1{2k^\lambda}+\frac{\lambda}{12k^{1+\lambda}}.
\]

**Theorem 2:** if \(f\in C^\rho[0,1]\), \(\rho>3\), and
\(1<\lambda<(\rho-1)/2\), then for every sufficiently large \(k\),

\[
\boxed{
\psi(L,S_L)=H_L(k-1,S_L)
+\sum_{n=k}^{L}
\frac{H_L(n,S_L)-H_L(n-1,S_L)}{q_n}
}
\tag{7}
\]

is unbiased for \(f(x)\) and lies in \([0,1]\) almost surely for every \(x\in[0,1]\). The same \(k\) works uniformly in the unknown input bias, but depends on the function and approximation constants.

### Proof structure

1. **Unbiasedness:** conditioning on \(L\), a uniformly chosen size-\(n\) subset of the \(L\) iid coins still has binomial count. Equation (8) establishes \(E[H_L(n,S_L)\mid L]=g_n(x)\) when \(n\le L\). The survival weights cancel after expectation, leaving \(g_{k-1}+\sum_{n\ge k}(g_n-g_{n-1})=f\). The proof's later nonnegativity result justifies the interchange by Tonelli.
2. **Nonnegativity:** Eq. (3), Pascal's identity and degree elevation imply \(H_L(n,S_L)\ge H_L(n-1,S_L)\). Every term in (7), including the initial term, is nonnegative.
3. **An upper bound on increments:** Eq. (11) bounds each difference by a hypergeometric average of \(b(m-1,i)-a(m-1,i)\). The polynomial gap controls endpoint coefficients directly. For interior coefficients, isolate one nonnegative term of the binomial sum at \(x=j/n\), then use the stated Stirling bound. Equation (14) gives
   \[
   b(n,j)-a(n,j)\le C\sqrt{\pi/2}\,e^2 n^{(1-\rho)/2}.
   \]
   The loss of a square-root factor is consequential; a uniform bound on a positive Bernstein polynomial is not itself the same bound on each coefficient.
4. **Summable correction:** dividing the increment bound by \(q_n\asymp n^{1-\lambda}\) produces summands of order \(n^{\lambda-(\rho+1)/2}\). Their sum converges exactly under the displayed strict restriction on \(\lambda\). The full correction in Eq. (15) decreases as \(O(k^{-(\rho-3)/2})\).
5. **Headroom below one:** the initial hypergeometric average must stay uniformly below one, leaving room for that vanishing correction. This is the step involving the HNP construction and the source discrepancy discussed next.

The theorem is a sufficient construction. The conjecture that the extra derivative is necessary for this approach is not an impossibility theorem for all factories.

## The HNP formula is incompletely transcribed; the headroom step can be made explicit

On p. 7, the paper cites HNP Eq. (48) but writes the correction as a raw function,

\[
h_n(x)=f_n(x)+D\left[\theta/n^\rho+(x(1-x)/n)^{\rho/2}\right].
\]

HNP's original printed p. 355 instead has

\[
\varphi_n(x)=\theta_\rho/n^\rho+(x(1-x)/n)^{\rho/2},\qquad
h_n=f_n+[x+(1-x)]^rD B_n\varphi_n.
\tag{HNP 47–48}
\]

Thus the Bernstein operator \(B_n\) and the degree-elevation bookkeeping were omitted in the citation's displayed transcription. The latter polynomial identity matters for which Bernstein coefficients are being compared. HNP Step 4 supplies uniform headroom for the coefficients of \(f_n\); the coefficients of \(B_n\varphi_n\) are the sampled values \(\varphi_n(j/n)\), and degree elevation forms convex combinations. This specific construction can support the desired small coefficient correction. It would be incorrect to infer the same conclusion for an arbitrary polynomial merely from its pointwise size and linearity: \(4\delta x(1-x)\le\delta\) has degree-two Bernstein coefficients \((0,2\delta,0)\).

Consequently this is a source-transcription/justification issue, **not evidence that Theorem 2 is false**. One can also close the final step directly from its stated approximation assumptions, without tracing HNP's construction:

Take \(\varepsilon>0\) with \(f\le1-\varepsilon\), possible by continuity and compactness. Fix \(m\) with \(Cm^{-\rho/2}\le\varepsilon/4\). Then
\(h_m\le1-3\varepsilon/4\). For \(n\ge m\), Eq. (4) and coupling sampling with and without replacement give

\[
b(n,j)\le E\,b(m,\operatorname{Hyp}(n,j,m))
\le h_m(j/n)+\frac{m(m-1)}{2n}.
\]

Indeed the two count laws can be coupled to agree whenever the \(m\) sampled population indices are distinct, and the collision probability is at most \({m\choose2}/n\). Because \(b(m,\cdot)\in[0,1]\), that probability bounds the expectation difference. Thus for

\[
n\ge N_0:=\max\left\{m,\left\lceil2m(m-1)/\varepsilon\right\rceil\right\},
\qquad \max_j b(n,j)\le1-\varepsilon/2.
\]

If \(k\ge N_0\), Eq. (3) implies
\(H_L(k-1,S_L)\le a(L,S_L)\le b(L,S_L)\le1-\varepsilon/2\). Increasing \(k\) until the Eq. (15) correction is less than \(\varepsilon/2\) completes the bound. This independently checked local replacement preserves the main parameter range; it is not a certification of every imported lemma.

## Corollary 1 omits a necessary hypothesis

The printed corollary retains only \(0\le a(n,j)\le1\) and \(g_n\to f\), and then claims that (7) is unbiased and nonnegative for any \(\lambda>1\) and any \(k\). It does **not** retain Eq. (3). The omission invalidates its literal nonnegativity conclusion.

For a concrete counterexample, take \(k=2\), \(f\equiv1/2\), and coefficients constant within each row:

\[
a(1,j)=a(2,j)=3/4,\qquad a(3,j)=0,\qquad
a(n,j)=1/2\quad(n\ge4).
\]

These meet the corollary's displayed bounds and convergence assumption. Hypergeometric averaging leaves each row constant. On the positive-probability event \(L=3\),

\[
\psi(3,S_3)=\frac34-\frac{3}{4\Pr(L\ge3)}
=-\frac34\frac{2^{-\lambda}}{\zeta(\lambda,3)}<0.
\]

This holds for every \(x\), including the endpoints. There are only finitely many nonzero increments, so the example is still integrable and unbiased: its mean is \(3/4-3/4+1/2=1/2\). It precisely refutes the asserted nonnegativity, not the main theorem or the example's unbiasedness.

Restoring Eq. (3) restores the nonnegative increments and the Tonelli proof. The analogous upper-only construction requires the corresponding reverse coefficient order, Eq. (4). Later implementability examples attributed to Corollary 1 should retain these compatibility hypotheses; arbitrary consistent bounded Bernstein coefficients are insufficient.

## Bounded variance does not imply finite expected sampling cost

Corollary 2 correctly follows from Theorem 2's support statement: \(\operatorname{Var}\psi\le1/4\). The input count can nevertheless have infinite mean.

Direct calculation for the paper's chosen truncation law gives, for \(s>0\),

\[
E L^s=\frac{\zeta(\lambda-s,k)}{\zeta(\lambda,k)}<\infty
\quad\Longleftrightarrow\quad\lambda>s+1.
\]

In particular, a finite mean requires \(\lambda>2\). A choice satisfying both this requirement and Theorem 2's range exists iff **\(\rho>5\)**. For \(3<\rho\le5\), every allowed power-law choice in the theorem has infinite \(EL\), although \(L\) is finite almost surely. More generally the theorem permits a finite \(s\)-th moment only when \(\rho>2s+3\).

This is a statement about the displayed construction and available smoothness guarantee, not a necessary regularity condition for every Bernoulli factory. A function known to be smoother can use the stronger exponent. Affine functions already have the one-input solution described below. The stochastic truncation has no deterministic maximum, and explicit storage of its count and success count is not a fixed-bit resource guarantee. Arithmetic, coefficient construction and additional random-bit cost are also outside \(EL\).

### The weaker-regularity variance paragraph is unresolved and contains printed errors

After Corollary 2, p. 8 asks whether \(\rho>2\) can suffice for finite variance. It invokes the Rhee–Glynn variance identity and gives the formal summability condition \(2<2\lambda<\rho\), but explicitly says the needed square-integrability/decay condition has not been established.

The displayed differences subtract identical terms, repeatedly writing \(H_L(n-1,S_L)^2-H_L(n-1,S_L)^2\), and Eq. (18) prints a limit \(n\to0\). Both defects are present in the original PDF and TeX, not only HTML extraction. An intended index shift and a limit at infinity are plausible, but the note does not silently replace them with a proved variance theorem. Moreover the triangular dependence on \(L\) deserves care when interpreting the imported identity. The established conclusion recorded here remains the bounded-support variance result under Theorem 2's assumptions.

## Implementability, experiments and open questions

The approximation coefficients exist through an iterative construction; the paper does not provide a generally practical coefficient generator. It cites an earlier Łatuszyński–Kosmidis–Papaspiliopoulos–Roberts example that would require \(2^{2^{26}}\) coefficients. That is a cited illustration of construction difficulty, not a measured runtime of this new algorithm.

Even with coefficients supplied, the starting cutoff \(k\) requires bounds involving five constants \(\varepsilon,\theta,C_\theta,D,C\), with \(C=2C_\theta D\) available from the cited construction. Several are implicit and require following HNP's estimates. Conditional-expectation versions of the coefficient inequalities used by earlier practical factories are insufficient to ensure the **pathwise** interval constraint on this estimator.

For \(f(x)=a+bx\) satisfying the probability bounds, Bernstein polynomials reproduce the function exactly: \(a(n,j)=b(n,j)=f(j/n)\). Choosing \(L=1\) deterministically yields \(\psi=a+bX_1\). This is a special replacement of the power-law count, not a parameter choice with finite \(\lambda\) that concentrates its law at one.

The discussion also gives lower-coefficient forms for Lipschitz or twice differentiable functions, respectively subtracting \((1+\sqrt2)M/\sqrt n\) or \(\|f''\|_\infty/(2n)\) from \(f(j/n)\). Their use invokes the one-sided construction and must respect the missing compatibility condition identified above. The paper does not turn these examples into a general bounded, finite-mean algorithm for weakly smooth functions.

There are **no numerical experiments, tables or new datasets**. The final section leaves open whether \(\rho>3\) is necessary for the particular bounded estimator, whether suitable functions admit a non-adaptive version with exponential input-count tails, and how to relax the endpoint or strictly interior output assumptions. The Nacu–Peres exponential-tail result on a closed subset of \((0,1)\) cannot simply be substituted into this proof: the observed sufficient statistic includes all-success and all-failure cases, so endpoint coefficient control is still needed.

The main dependencies are HNP for compatible approximation, Nacu–Peres for its Bernstein/probabilistic interpretation, McLeish and Rhee–Glynn for debiasing, Łatuszyński et al. for conversion and practical constructions, Nemes for zeta estimates, and Robbins for Stirling bounds. Other references supply simulation applications and existence constraints. Their citation here does not confer a completed reading or independent verification status on them.

## Disposition for continuing research

This is a useful precise example of unbiased probability transformation where input-count independence, pathwise output bounds, expected sampling work and practical coefficient availability are separate properties. The known function, iid fixed-bias input stream and complete approximation machinery are essential objects. No direct FP learning-rule, finite-state formation, multi-environment shared-encoder or future predictive-loss theorem is proposed.

Retain the main sufficient construction with its stated conditions, the corrected scope of Corollary 1, and the finite-mean threshold for this power-law design. HNP stays a scoped dependency. The next complete reading can proceed to the already screened Chugg–Ramdas confidence-sequence paper; the finite-automaton factory candidate remains separate. Astra decides whether any of these results belongs in the project theory.
