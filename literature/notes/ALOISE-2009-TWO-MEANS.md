# NP-hardness of Euclidean sum-of-squares clustering

Daniel Aloise, Amit Deshpande, Pierre Hansen and Preyas Popat. *Machine Learning* **75** (2009), 245–248. Published online January 24, 2009. [DOI](https://doi.org/10.1007/s10994-009-5103-0) · [Publisher PDF](https://link.springer.com/content/pdf/10.1007/s10994-009-5103-0.pdf).

**Coverage:** all four journal pages, §§1–3, the actual graph/coordinate figure, displayed calculations and all 12 references. The main assistant read the complete publisher text and inspected the mathematical layouts on pp. 246–248. There are no appendices or experiments. Local source: `literature/corpus/request_entropy_2026_11_23/aloise2009.pdf`. This note records the published argument, not a formal proof replay.

## Original problem and argument

The objective is the sum of squared Euclidean distances from each input point to its assigned cluster mean. Theorem 1 establishes NP-hardness with exactly two clusters when dimension can grow.

Section 2 diagnoses an earlier minimum-bisection reduction: large private coordinates contribute `(n−2)M²` to **every** nonempty bipartition. The omitted distances of zero coordinates to their means had created a false preference for balanced clusters. The figure displays that construction.

Section 3 instead starts with a simple graph and uses its oriented vertex–edge incidence rows, with entries in `{−1,0,1}`. For cluster sizes `p,q` and crossing-edge count `e`, its exact objective is

\[
J=2|E|-\frac{(p+q)e}{pq}.
\]

Minimizing it solves densest cut. The imported NP-hardness is sparsest cut on the complementary graph, attributed to Matula–Shahrokhi (1990). Internal edges contribute two; a crossing edge contributes `2−1/p−1/q`. The paper also records independent contemporary proofs by Dasgupta and Kanade–Nimbhorkar–Varadarajan.

## Conditions and limits

The clusters are unrestricted in size, centers are means, and observations have equal weights. The coordinates are exact small integers; dimension is the edge count. The paper states neither Shannon-entropy hardness nor a KL approximation theorem. It supplies no fixed-dimensional hardness result and no constant-factor approximation lower bound. A result for two clusters is different from one for two coordinates.

## Independent observation for the requested scope check

This paragraph is an elementary deduction from the displayed objective, not an additional theorem attributed to the authors. Write `N=p+q`. Distinct values `e/[p(N−p)]` differ by at least `N⁻⁴`, since both denominators are positive integers at most `N²`. Consequently distinct values of `J` are separated by at least `N⁻³`; using the weaker lower bound `N⁻⁴` is sufficient for a quantitative transfer. Thus this particular source supplies explicit integer coordinates and a usable inverse-polynomial gap, avoiding a dependence on irrational Euclidean embeddings.

Transferring that gap to entropy requires an additional argument controlling normalization, positivity, approximation error and the additive entropy baseline. It is not justified merely by saying that KL resembles squared distance. The separate Astra request response will distinguish that derivation from the publication's own claim. No change to FP core theory is made here.
