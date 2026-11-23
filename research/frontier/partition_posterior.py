"""Posterior prediction and sequential updates for a finite product-partition model."""

from fractions import Fraction as F
from itertools import product
from math import factorial

import numpy as np
from response_classes import BLOCKS, LABELS, LOG_COUNTS, SUBSETS
from scipy.special import betaln, logsumexp

ROW_BLOCK = np.ascontiguousarray(
    BLOCKS[np.arange(len(LABELS))[:, None], LABELS].T, dtype=np.uint8
)
CONTAINING = np.stack([np.flatnonzero(row) for row in SUBSETS.T]).astype(np.uint8)


def posterior(n, h, prior, alpha):
    ns, hs = SUBSETS @ n, SUBSETS @ h
    a, b = alpha * prior, alpha * (1 - prior)
    utility = (betaln(hs + a, ns - hs + b) - betaln(a, b)).sum(axis=1)
    scores = utility[BLOCKS].sum(axis=1) - LOG_COUNTS
    weights = np.exp(scores - logsumexp(scores))
    return ns.astype(np.uint32), hs.astype(np.uint32), weights, utility


def subset_marginals(utility):
    """Log-domain partition recursion independent of the enumeration of complete partitions."""
    z = np.full((5, 256), -np.inf)
    z[0, 0] = 0.0
    for mask in range(1, 256):
        first = mask & -mask
        other = mask ^ first
        subset = other
        selected = []
        while True:
            selected.append(first | subset)
            if subset == 0:
                break
            subset = (subset - 1) & other
        selected = np.asarray(selected)
        for k in range(1, min(4, mask.bit_count()) + 1):
            z[k, mask] = logsumexp(utility[selected] + z[k - 1, mask ^ selected])
    prior = -np.log([1.0, 127.0, 966.0, 1701.0])
    ln_z = logsumexp(prior + z[1:, 255])
    block = np.zeros(256)
    for mask in range(1, 256):
        block[mask] = np.exp(
            utility[mask] + logsumexp(prior + z[:-1, 255 ^ mask]) - ln_z
        )
    np.testing.assert_allclose(SUBSETS.T @ block, 1.0, rtol=0, atol=3e-11)
    return block


class Online:
    def __init__(self, kind, n, h, prior, alpha):
        self.kind = kind
        self.alpha = alpha
        self.prior_hits = alpha * prior
        self.weights = np.empty(0, dtype=np.float64)
        if kind == "mixture":
            self.n, self.h, self.weights, _ = posterior(n, h, prior, alpha)
        elif kind == "current":
            self.n = n.sum(axis=0, keepdims=True).astype(np.uint32)
            self.h = h.sum(axis=0, keepdims=True).astype(np.uint32)
        else:
            assert kind == "independent"
            self.n, self.h = n.astype(np.uint32), h.astype(np.uint32)

    def predict(self, u, v):
        if self.kind == "mixture":
            means = (self.h[:, v] + self.prior_hits[v]) / (
                self.n[:, v] + float(self.alpha)
            )
            likelihood = means[ROW_BLOCK[u]]
            return float(self.weights @ likelihood), likelihood
        row = 0 if self.kind == "current" else u
        return float(
            (self.h[row, v] + self.prior_hits[v]) / (int(self.n[row, v]) + self.alpha)
        ), None

    def observe(self, u, v, y, likelihood):
        if self.kind == "mixture":
            self.weights *= likelihood if y else 1 - likelihood
            self.weights /= self.weights.sum()
            cells = CONTAINING[u]
            self.n[cells, v] += 1
            self.h[cells, v] += int(y)
        else:
            row = 0 if self.kind == "current" else u
            self.n[row, v] += 1
            self.h[row, v] += int(y)

    def allocated(self):
        arrays = (
            self.n.nbytes + self.h.nbytes + self.weights.nbytes + self.prior_hits.nbytes
        )
        return {
            "counts_weights_prior_bytes": arrays,
            "shared_update_indices_bytes": ROW_BLOCK.nbytes + CONTAINING.nbytes
            if self.kind == "mixture"
            else 0,
        }


def exact_example():
    plans = [(0, *p) for p in product(range(2), repeat=3)]
    result = []
    for groups in ((0, 0, 1, 1), (0, 1, 0, 1)):
        weights = []
        for plan in plans:
            w = F(1)
            for block, col in product(range(2), range(2)):
                m = sum(
                    s == block and c == col for s, c in zip(plan, groups, strict=True)
                )
                w *= F(factorial(m) ** 2, factorial(2 * m + 1))
            weights.append(w)
        same = sum(
            w for p, w in zip(plans, weights, strict=True) if p[0] == p[1]
        ) / sum(weights)
        result.append((same, F(1, 2) + same / 6))
    assert result == [(F(6, 11), F(13, 22)), (F(1, 2), F(7, 12))]
    assert result[0][1] - result[1][1] == F(1, 132)
    return result


def r4_example():
    from fp_reference.program import (
        Product,
        Program,
        SemanticRules,
        Source,
        SourceSpec,
        Sum,
        Term,
    )
    from fp_reference.semantics import evaluate

    names = ("straight", "cross", "unit")
    nodes = [Source(n) for n in names]
    params = []

    def coeff(v):
        if v not in params:
            params.append(v)
        return params.index(v)

    def node(n):
        nodes.append(n)
        return len(nodes) - 1

    plans = [(0, *v) for v in product(range(2), repeat=3)]
    weighted = []
    for p in plans[1:]:
        products = []
        for straight, cross in (((0, 1), (0, 2)), ((2, 3), (1, 3))):
            a, b = straight
            c, d = cross
            products.append(
                node(
                    Sum(
                        "n",
                        (
                            Term(0, coeff(5 + int(p[a] == p[b]))),
                            Term(1, coeff(5 + int(p[c] == p[d]))),
                        ),
                    )
                )
            )
        weighted.append(node(Product("n", *products)))
    heads = []
    for y in (0, 1):
        direction = 2 * y - 1
        # The all-together partition weighs 36 in both histories. Absorb the required native base of one.
        terms = [Term(2, coeff(36 * (3 + direction) - 1))]
        terms.extend(
            Term(w, coeff(3 + direction * int(p[0] == p[1])))
            for p, w in zip(plans[1:], weighted, strict=True)
        )
        heads.append(node(Sum("n", tuple(terms))))
    rules = SemanticRules(
        tuple(SourceSpec(n, "n", 0, 1) for n in names),
        ("n",),
        (("n", "n", "n"),),
        "n",
        (1, 1),
        (),
    )
    program = Program(tuple(nodes), len(params), tuple(heads), ())
    for history, (_, prediction) in enumerate(exact_example()):
        observed = {"straight": 1 - history, "cross": history, "unit": 1}
        assert evaluate(program, rules, params, observed).probabilities == (
            1 - prediction,
            prediction,
        )
    print(
        "R4 normalized posterior forecasts",
        len(nodes),
        "nodes",
        len(params),
        "parameter slots",
    )


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("verification requires assertions")
    print("co-clustering probabilities and next forecasts", exact_example())
