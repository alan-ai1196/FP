# Liu 2026: the exact complexity of minimum positive realization

## Source, edition and reading boundary

**Zhaobo Liu, _The Complexity of Minimal Positive Realization_, arXiv:2610.27962v1.** [Primary record](https://arxiv.org/abs/2610.27962v1) · [Complete HTML](https://arxiv.org/html/2610.27962v1) · [PDF](https://arxiv.org/pdf/2610.27962v1) · [Source](https://arxiv.org/src/2610.27962v1).

Pro-A completed the 15-page edition on 26 November 2026, Shanghai. The main reader covered Sections 1–6, both appendices, every displayed statement and proof, the two-panel figure, the two title-page notes and all 20 references. Complete primary HTML and the extracted PDF supplied the text. Original PDF pages 1, 5 and 10–13 were visually inspected, including the cycle construction and the entire arithmetic encoding. The source inventory contains one active 46,100-character `main.tex`, a bibliography and formatting files. Selected source passages were checked against the HTML and PDF. Complete TeX reading is not claimed separately.

The primary history lists only v1, submitted 20 October 2026. No revised, withdrawn or peer-reviewed edition was identified in this bounded check. This is an ordinary author preprint, not an OpenAI or Anthropic release. No AI-use statement was found in the inspected manuscript. That does not establish whether AI was used.

A secondary reader checked Appendix B's arithmetic encoding and the cited ETR-INV source statement. The main reader independently examined the encoding, the interval-cycle reduction, the stable positive witness and the finite Markov certificate. No defect was found in those bounded checks. This is substantive source assessment, not a formal proof certificate or an independent certification of every external dependency. No experiment, exhaustive enumeration or proof-assistant replay was performed.

## 1. What the decision problem actually prices

The input is a nonzero strictly proper rational transfer matrix. A realization of order \(n\) has

\[
H(z)=C(zI-A)^{-1}B,
\qquad A\in\mathbb R_+^{n\times n},
\quad B\in\mathbb R_+^{n\times p},
\quad C\in\mathbb R_+^{q\times n}.
\]

The minimum permitted order is \(d_+(H)\). The ordinary minimum linear dimension is the McMillan degree \(d_{\rm McM}(H)\), so

\[
d_+(H)\ge d_{\rm McM}(H).
\]

Here “positive” means entrywise **nonnegative**, allowing zeros. It does not require a stochastic transition matrix. The evolving state is a real vector with \(n\) coordinates. The theorem does not say that a physical register has only \(n\) possible values.

The input coefficients are rational numbers written in binary. Numerator and denominator polynomials are given by full coefficient lists. The candidate order \(n\) is written in unary. These encoding choices are part of the complexity result.

**Theorem 1, source claim.** Deciding \(d_+(H)\le n\) is complete for the existential theory of the reals, \(\exists\mathbb R\). Hardness persists for stable SISO transfer functions that already have a positive realization, with the candidate order set to their McMillan degree.

Thus the hard question can be whether positivity costs any extra dimension, even when existence and stability have already been guaranteed. The proof does not rely on undecidability or on the absence of every finite realization.

**Corollary 2.** For a supplied minimal rational SISO realization \((A_0,b_0,c_0)\), finding whether some invertible real change of coordinates makes all three components nonnegative is also \(\exists\mathbb R\)-complete. Membership uses variables \(T,V\) with \(TV=VT=I\), followed by polynomial inequalities for \(VA_0T,Vb_0,c_0^\top T\). The hardness direction uses similarity of minimal realizations.

Neither statement establishes an unconditional superpolynomial running-time lower bound. Nor does it provide a finite-precision certificate bound, approximation hardness, or a lower bound for learning from sampled observations.

## 2. A delayed impulse response fixes the entire state skeleton

For \(H(z)=1/p(z)\), with \(p\) monic of degree \(m\), write

\[
H(z)=\sum_{k\ge0}h_kz^{-(k+1)}.
\]

Then \(h_0=\cdots=h_{m-2}=0\) and \(h_{m-1}=1\). In a positive realization each \(h_k=c^\top A^kb\) is a sum of nonnegative walk weights.

A shortest positive path from the input support to the output support therefore has \(m-1\) edges. At order \(m\), it visits every state exactly once. An extra input at a later vertex, an extra output at an earlier vertex, or a forward edge skipping a vertex would create a forbidden shorter positive path. Only backward returns, self-loops and consecutive forward edges remain.

Permutation and positive diagonal scaling consequently yield

\[
b=e_1,
\qquad c=e_m,
\qquad J_{i+1,i}=1,
\qquad J_{ij}=0\text{ when }i>j+1,
\qquad J\ge0.
\]

For this Hessenberg matrix,

\[
e_m^\top(zI-J)^{-1}e_1=\frac1{\det(zI-J)}.
\]

Lemma 3 therefore converts positive realization at exactly the McMillan degree into choosing nonnegative upper-Hessenberg entries with a prescribed characteristic polynomial. The zero prefix is essential. Approximate zeros allow leakage through shorter paths, so the exact skeleton argument alone has no quantitative approximation conclusion.

## 3. Interval cycles reduce the matrix constraints to one polynomial product

Set \(q(t)=t^mp(1/t)\). A return edge \(j\to i\) closes the forward interval \([i,j]\). Since the forward weights equal one, the return weight is also the weight of that cycle. The determinant expansion is a signed sum over disjoint interval cycles.

Take an integer \(g\ge2\), let \(m=3g-1\), and impose

\[
q_k=0\quad(1\le k<g),
\qquad q_k=-s_k\quad(g\le k<2g),
\quad s_k\ge0.
\]

The initial zero coefficients exclude cycles shorter than \(g\). There cannot be three disjoint nonzero cycles. A cycle of length at least \(2g\) cannot be disjoint from any other nonzero cycle. As a result, the coefficient of a higher degree is a sum of products of two short-cycle weights minus the total weight of a long cycle.

The useful compression is especially simple. Divide short intervals according to whether their starting point is at most \(g\). Every interval in the first class contains vertex \(g\). Every interval in the second contains vertex \(2g\). A disjoint pair therefore uses one interval of each class. If the class totals for length \(k\) are \(X_k,Y_k\), then

\[
X_k+Y_k=s_k,
\qquad [t^j]X(t)Y(t)\ge q_j
\quad(2g\le j\le m).
\]

Conversely, put the \(X_k\) cycle at the left endpoint and the \(Y_k\) cycle at the right endpoint. Their contributions agree with \([t^j]XY\) whenever \(j\le m\). An additional length-\(j\) cycle of weight \([t^j]XY-q_j\) subtracts the surplus. It cannot form another disjoint pair. This proves the full equivalence in Lemma 4, not only a necessary inequality.

Writing \(S=X+Y\) and \(Z=X-Y\) gives

\[
XY=\frac{S^2-Z^2}{4},
\qquad |Z_k|\le s_k.
\]

The remaining task is therefore feasibility of selected upper bounds on coefficients of \(Z^2\), with separately bounded coefficients of \(Z\). The degree restriction \(m<3g\) is what makes this quadratic compression exact. It is not a general formula for arbitrary positive realizations.

## 4. How the arithmetic encoding avoids unwanted products

The source problem ETR-INV asks for variables in \([1/2,2]\) obeying equations \(x=1\), \(x+y=z\) and \(xy=1\). The paper uses the \(\exists\mathbb R\)-completeness statement in Abrahamsen–Adamaszek–Miltzow, arXiv:1704.06969v4, Definition 5 and Theorem 7. That historical dependency was checked only at its problem statement and theorem, not fully read.

Appendix B represents \(x_i/2\) and its negative by two bounded coefficients. Linear rows impose the lower bound \(1/4\), additive equations and the relation between each positive and negative copy. Repeated indices are collected before placing row coefficients. The equation \(x=1\) can be replaced by \(x^2=1\) because the source interval is positive.

For \(h=2n+2\), the exponents

\[
e_k=2hk^2+k\qquad(0\le k<h)
\]

have unique unordered pair sums. Equality of two sums forces equality both of the index sums and of the sums of squares. This includes repeated-index pairs. Let \(U=e_{h-1}\). Two reference positions are reserved for coefficients whose product is forced to \(-1\). Their bounds force them to be \(\varepsilon,-\varepsilon\), with one shared sign \(\varepsilon\in\{-1,1\}\). Decoding multiplies all free coefficients by that common sign.

For each linear row \(j\), choose a widely separated target degree

\[
w=2U+1,
\qquad T_j=(Q+j+1)w,
\qquad \alpha_{ji}=T_j-f_i,
\]

where \(f_i\) is the free coefficient's Sidon position. Reference-product inequalities fix the auxiliary coefficient at \(\alpha_{ji}\) to \(\varepsilon a_{ji}/2\). The coefficient of \(Z^2\) at \(T_j\) then equals the desired linear row \(\sum_i a_{ji}v_i\).

Three facts prevent spurious terms. The low pair sums are at most \(2U\). Different row blocks are separated by more than every possible low-position offset. Products of two auxiliary coefficients lie above every degree that receives a constraint. The unique-pair-sum property isolates reference products within an individual block.

Finally, an upper bound for the product of two positive copies and an upper bound for the product of a positive and a negative copy jointly impose equality \(v_iv_j=1/4\). Diagonal products use coefficient \(1\), while distinct positions use coefficient \(2\), and the construction distinguishes these cases. The resulting maximum degree is \(O(Qh^3)\), so dense coefficient lists remain polynomial in the original instance size.

The bounded check found the degree separation, shared-sign correction, repeated-variable handling and positive-interval constant encoding consistent. No numerical evidence is needed for these discrete algebraic bookkeeping steps.

## 5. Positive existence and stability are preserved independently of feasibility

The next construction places the encoded constraints at even degrees. For coefficient data of maximum degree \(D\), set

\[
g=6D+4,
\quad m=18D+11,
\quad a(t)=t^g\bigl(1+tS(t^2)\bigr),
\quad b(t)=t^{2g+2}B(t^2),
\]

where the nonnegative coefficients of \(B\) encode the bounds on \(Z^2\). Add a polynomial \(E\) supported at odd degrees from \(2g+1\) through \(m\), all with weight \(\gamma=1+a(1)b(1)\), and define

\[
q=1-a+b-E,
\qquad p(z)=z^mq(1/z).
\]

The odd correction leaves every encoded even coefficient untouched. Lemma 6 applies the cycle criterion to show that the coefficient constraints are feasible exactly when \(d_+(1/p)=m\).

Separately, Lemma 7 establishes positive realizability for **every** encoded instance. The key identity is

\[
q(1+a)=1-\mathcal R,
\qquad
\mathcal R=(a^2-b)+E+(aE-ab)\succeq_{\rm coef}0.
\]

The first difference is nonnegative by the allowed coefficient bounds. The correction covers the entire support of \(ab\), with coefficients exceeding its maximum. A larger companion realization for the denominator corresponding to \(q(1+a)\), with numerator corresponding to \(1+a\), is consequently nonnegative. Its cancellations recover \(1/p\).

If that companion has last-row weights \(R_j\), use

\[
K=2\Bigl(1+\sum_jR_j\Bigr),
\qquad \widehat H(z)=\frac{K^m}{p(Kz)}.
\]

The constructed companion divided by \(K\) has every row sum below \(1/2\). It gives a stable rational positive realization of \(\widehat H\). More generally,

\[
(A,b,c)\longmapsto(A/K,b,K^{m-1}c)
\]

is an invertible correspondence between positive realizations of the original and scaled transfer functions, preserving order. Stability therefore does not remove the encoded decision problem. The rational coefficients, scaling powers and supplied unary order retain polynomial bit length.

The promise concerns a larger rational positive witness. A minimum-order witness is still allowed to have arbitrary real coefficients. The argument does not guarantee a rational minimum-order witness or a bounded description of one.

## 6. A finite certificate for an infinite input–output identity

For membership in \(\exists\mathbb R\), let \(d\) be the largest denominator degree of an individual transfer-matrix entry. Introduce nonnegative matrices \(A,C,X_0,\ldots,X_{d+n-1}\), with \(X_0=B\), and impose

\[
X_{k+1}=AX_k\quad(0\le k<d+n-1),
\qquad CX_k=H_k\quad(0\le k<d+n).
\]

These are quadratic scalar equations. Matching the first \(d+n\) Markov matrices makes every entry of the difference between the proposed and target transfer functions vanish to order \(d+n+1\) at infinity. Its denominator has degree at most \(d+n\). After multiplying by that denominator, its polynomial numerator tends to zero and must vanish identically.

This finite certificate is a useful exact tool independent of the hardness reduction. Its input includes a bound on the competing realization order. Matching a finite prefix without such a dimension bound does not identify an unrestricted infinite process. Small errors in those coefficients likewise need conditioning estimates before implying a small long-horizon forecasting error.

## 7. Consequences and the boundary with current FP questions

The paper supplies a source-grounded obstacle to a universal efficient procedure that always finds the exact smallest nonnegative linear realization from a fully specified rational transfer function. It also supplies concrete tools: a delay-induced Hessenberg structure, a two-family interval-cycle factorization, and finite polynomial constraints certifying exact realization.

The following distinctions matter for any later transfer decision by Astra:

| Quantity in this paper | Additional work needed for a predictive-memory claim |
|---|---|
| Number of coordinates in a nonnegative linear system | Identify whether FP is charging mixture components, physical discrete states, coefficient bits or working storage |
| One fixed state matrix and an input impulse response | Specify a mapping to symbol-dependent updates and causal initialization |
| Complete exact rational coefficients | Supply an observation model and quantify the cost of estimating them |
| Exact equality at all horizons | Establish a robust separation under the target loss and state the horizon |
| Nonnegative matrices | Establish stochastic normalization and preserve the relevant state count and readout |
| Worst-case \(\exists\mathbb R\)-completeness | State a computational assumption and any restrictions of the proposed algorithm's domain |

In particular, this result does not settle the stationary log-loss price just above an exact delay-amplitude threshold. The reduction can have arbitrarily delicate exact coefficient constraints, and its initial zero impulse values carry essential combinatorial information. No inverse-polynomial approximation gap is proved here. A claim about approximate state acquisition needs a separate gap theorem.

No FP core definition, architecture, experiment, implementation or `research/frontier/` file was changed. No substantive FP transfer is asserted.

## Source dependency retained at scoped depth

- [Abrahamsen–Adamaszek–Miltzow, _The Art Gallery Problem is ∃R-complete_, arXiv:1704.06969v4](https://arxiv.org/abs/1704.06969v4). Definition 5 and Theorem 7 provide the bounded ETR-INV source problem. This was a specific proof dependency, not a historical full-reading task.
- The other 19 bibliography items were read as references in Liu's manuscript. Their full texts and theorems were not thereby verified. The exact-real classification is assessed from Liu's own reduction, with the stated external source theorem retained as a premise.
