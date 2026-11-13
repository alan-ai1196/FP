# 2026 mathematical-results transfer audit (research only)

Date: 2026-11-13. Baseline: `main@a35ef18`. **This branch does not change Foundation R4, ERC-1, Runtime, search, training, AMP, or installation authority.**

## Selected conditional theorem: rational input influence

Source: Turturean, *A proof of the Aaronson–Ambainis conjecture* (2026), https://arxiv.org/abs/2611.09773 . The source's squared-flip influence convention and Lean statement are at https://github.com/physical-superintelligence/aaronson-ambainis/blob/main/problem_statement.md .

For fixed `n`-bit input and fixed FP readout `f=P/Q`, assume ordinary polynomial degree `deg(P),deg(Q)<=d`, `d>=1`, and `0<=P<=Q`, `0<a<=Q<=b` on the Boolean cube. Put `v=Var_uniform(f)`, `c=8 sqrt(15)/(125 pi^4)`. For any integer `m>=1`, let `delta=(1-a/b)^m`. Then

```
max_i E_uniform[(f(X)-f(X^i))^2] >=
    max(0, sqrt(c)*max(0,sqrt(v)-delta)^(5/2)/(m*d)^3-2*delta)^2.
```

**Proof.** Define `t=1-Q/b` and `g=(P/b)*sum_{k=0}^{m-1}t^k`. Geometric truncation gives `g=f*(1-t^m)`, `0<=g<=f<=1`, `deg(g)<=m*d`, and `||f-g||_infty<=delta`. Orthogonal centering implies `sqrt(Var(g))>=max(0,sqrt(v)-delta)`. Bit-flip L2 increments satisfy `sqrt(Inf_i(f))>=sqrt(Inf_i(g))-2*delta`. Apply the **external** Aaronson–Ambainis theorem `max Inf_i(g)>=c Var(g)^(5/2)/(md)^6`. QED.

For fixed finite `b/a`, `d`, and positive `v`, some `m` gives a strictly positive dimension-independent bound, but it can be tiny. Example `P=1+x1,Q=2+x1+x2`: `v=1/72`, `Inf_1=Inf_2=1/36`; at `m=40`, the bound is only about `1.4e-17`.

**Strict limitations:** uniform *independent* Boolean input (not text distribution); frozen readout (not gradient, future learner or architecture discovery); actual expanded polynomial degree (which may be exponential in a shared native DAG); actual denominator range; no efficient oracle for finding the influential coordinate. The witness `g` need not be a legal positive-native FP program (its formal coefficients may include negatives). No source deletion or deployment may follow.

## Existing standard read-only ablation law

For `S` retained bits and `f_S=E_uniform[f(X)|X_S]`, the Fourier/Poincare inequality gives

```
E_uniform[(f-f_S)^2] <= (1/4) * sum_{i not in S} Inf_i(f).
```

The right side counts every omitted Fourier coefficient at least once. This is a *frozen-function, uniform-cube* approximation bound only. A native implementation of `f_S` and its full resource/learner-state costs are not supplied. On `AND_n`, uniform error can be tiny while error under a distribution concentrated on all-ones is near one.

## Negative transfer: matrix multiplication

The reported `omega(C)<=9/4` 2026 arithmetic bound (https://github.com/openai/math/blob/main/lean/docs/107.md) admits subtraction/cancellation, unlike direct monotone positive-native arithmetic. Classical monotone semiring matrix multiplication requires `n^3` variable products, as follows from the disjoint degree-two monomial supports and the fact that a positive linear-form product contributes a complete rectangle, while each output's legal support is a matching. Reference: Jerrum and Snir, *Some Exact Complexity Results for Straight-Line Computations over Semirings* (1982), https://snir.cs.illinois.edu/listed/J7.pdf . The lower bound is **only for direct monotone polynomial outputs**: it does not settle normalized FP rational encodings, approximate computation or physical GPU kernels.

## Additional relevance screen

- **Most directly relevant learning insight:** Xu et al., *High-Dimensional Learning Dynamics of Attention-Indexed Models* (2026), https://arxiv.org/abs/2609.03858 . Parameterization-specific implicit bias and symmetry breaking suggest testing full FP learner Jacobians and continuations, not treating equal forecasts as equal learners.
- **KLS conjecture** (Song and Zhang, 2026): requires isotropic log-concave distributions. The positive `1+t^2` density on [-1,1] violates log-concavity at zero. No generic FP structure-search mixing theorem. https://www.microsoft.com/en-us/research/blog/solving-a-31-year-old-grand-challenge-in-mathematics-the-kls-conjecture/
- **Komlos discrepancy** (2026): vector sign-balancing cannot by itself round nonlinear native PRODUCT structures or preserve resource/learner states. https://arxiv.org/abs/2609.20979 .
- **k-server conjecture** (2026): matrix/determinant change of representation is instructive, but min-plus and signed determinants are not native positive FP operations. https://arxiv.org/abs/2609.15979 .
- **Subexponential #SAT / ETH claims** (2026): do not alter unconditional NP-hardness or representation-specific exact output lower bounds without matching all hypotheses. https://github.com/openai/math/blob/main/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/build/main_full_version.tex .
- **Matroid common-base FPRAS** (2026): special combinatorial oracle class, not arbitrary FP grammar. https://github.com/openai/math/tree/main/preprints/An-FPRAS-for-Common-Integer-Polymatroid-Bases-with-Binary-Capacities-October-5-2026 .

## Decision

Record this as an **optional read-only diagnostic**, not a model-quality gain or Foundation modification. Before considering source proposal prioritization, require actual registered native `P,Q` degree/range, counted acquisition work, independent observed-distribution errors, full parameter/gradient continuations, and measured strong comparisons. Return UNRESOLVED otherwise.
