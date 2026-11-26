"""Fit a balanced word partition and an arbitrary binary prediction rule together."""

import argparse
import json
from fractions import Fraction
from itertools import product
from math import atanh, log1p
from pathlib import Path

import numpy as np
from pair_dictionary import representatives
from transfer_dictionary import BETA, walsh

REGISTRATION = "f12abe0"
TRIPLES = 1 - 2 * ((np.arange(8)[:, None] >> np.arange(2, -1, -1)) & 1)
TABLES = 1 - 2 * ((np.arange(256)[:, None] >> np.arange(8)) & 1)
PRODUCT = TRIPLES.prod(axis=1)
SELECTOR = np.where(TRIPLES[:, 0] == 1, TRIPLES[:, 1], TRIPLES[:, 2])
HADAMARD = np.column_stack([walsh(e) for e in np.eye(8, dtype=np.int64)])
POWER = np.array([4, 2, 1], dtype=np.int64)
DEGREE = np.array([mask.bit_count() for mask in range(8)])


def table_id(table):
    return int((table < 0) @ (1 << np.arange(8)))


def contexts(signs):
    return (signs < 0) @ POWER


def machine_rules(states):
    """All three-step readouts with one reused transition and a fixed reset."""
    found = set()
    outputs = list(product((1, -1), repeat=states))
    for flat in product(range(states), repeat=states * 2):
        ends = [0]
        for _ in range(3):
            ends = [flat[2 * q + x] for q in ends for x in (0, 1)]
        for out in outputs:
            mask = sum((out[q] < 0) << j for j, q in enumerate(ends))
            found.add(mask)
        if len(found) == 256:
            break
    return found


def clock_width(table):
    # At each depth the distinct residual functions are necessary and suffice.
    return max(len(set(map(tuple, table.reshape(2**j, -1)))) for j in range(4))


def rolling_width(table):
    # Minimize the full shift register as a deterministic Moore machine.
    _, groups = np.unique(table, return_inverse=True)
    successors = (np.arange(8)[:, None] * 2 + np.arange(2)) % 8
    while True:
        keys = np.column_stack((groups, groups[successors]))
        _, refined = np.unique(keys, axis=0, return_inverse=True)
        if len(set(refined)) == len(set(groups)):
            return len(set(groups))
        groups = refined


def widths():
    minimum = np.zeros(256, dtype=np.int64)
    for count in range(1, 6):
        fitted = np.array(sorted(machine_rules(count)))
        minimum[fitted[minimum[fitted] == 0]] = count
        if np.all(minimum):
            break
    assert np.min(minimum) > 0
    clocks = np.array([clock_width(t) for t in TABLES])
    rolling = np.array([rolling_width(t) for t in TABLES])
    # Independent position-specific transition enumeration, with identity
    # output labels and both constant readouts included explicitly.
    phase_maps = list(product(range(2), repeat=4))
    words = {0, 255}
    for first in phase_maps:
        for second in phase_maps:
            for last in phase_maps:
                leaves = [
                    last[2 * second[2 * first[a] + b] + c]
                    for a, b, c in product(range(2), repeat=3)
                ]
                words.add(sum(x << j for j, x in enumerate(leaves)))
    assert words == set(np.flatnonzero(clocks <= 2))
    assert set(np.flatnonzero(rolling <= 2)) == {
        table_id(np.ones(8)),
        table_id(-np.ones(8)),
        table_id(TRIPLES[:, 2]),
        table_id(-TRIPLES[:, 2]),
    }
    assert (minimum <= 2).sum() == 18 and len(words) == 88
    return {"reset": minimum, "public_clock": clocks, "rolling": rolling}


class Search:
    def __init__(self, d, state_counts):
        self.d = d
        self.labels = representatives(d)
        self.bits = 1 << np.arange(d)
        self.masks = (self.labels < 0) @ self.bits
        self.size = 1 << d
        self.raw = np.array(list(product(range(d), repeat=4)))
        self.test_masks = self.subsets(self.raw)
        self.allowed = {
            "homogeneous_two_states": np.flatnonzero(state_counts["reset"] <= 2),
            "clocked_two_states": np.flatnonzero(state_counts["public_clock"] <= 2),
            "fixed_product": np.array([table_id(PRODUCT)]),
            "output_only": np.array([0, 255]),
        }

    def subsets(self, raw):
        names = self.bits[raw]
        prefixes = [names[:, 3]]
        for col in (2, 1, 0):
            prefixes += [x ^ names[:, col] for x in prefixes]
        return prefixes

    def counts(self, raw):
        # Recover all 8 signed outcome counts from their history Walsh moments.
        coeff = np.column_stack(
            [
                walsh(np.bincount(z, minlength=self.size))[self.masks]
                for z in self.subsets(raw)
            ]
        )
        total = coeff @ HADAMARD
        assert (total % 8 == 0).all()
        return total // 8

    def fit(self, c):
        best = int(abs(c).sum(axis=1).argmax())
        found = {"free_table": (best, table_id(np.where(c[best] < 0, -1, 1)))}
        for name, allowed in self.allowed.items():
            scores = c @ TABLES[allowed].T
            choice, f = np.unravel_index(scores.argmax(), scores.shape)
            found[name] = (choice, allowed[f])
        return found

    def posterior(self, c):
        logits = atanh(BETA) * c
        evidence = np.logaddexp(logits, -logits).sum(axis=1)
        weights = np.exp(evidence - evidence.max())
        weights /= weights.sum()
        coeff = (weights[:, None] * np.tanh(logits)) @ HADAMARD / 8
        predicted = np.zeros(len(self.raw))
        payload = np.zeros(self.size)
        for col, masks in enumerate(self.test_masks):
            payload[self.masks] = coeff[:, col]
            predicted += walsh(payload)[masks]
        assert np.max(abs(predicted.reshape(-1, self.d).sum(axis=1))) < 1e-12
        return predicted


def signed_counts(t, raw):
    return np.bincount(contexts(t[raw[:, :3]]), weights=t[raw[:, 3]], minlength=8)


def spectral_fit(raw, d):
    # Four ordinary moment candidates. Magnitudes and the final likelihood
    # choose between them without knowing the generating table or its signs.
    y = raw[:, 3]
    features = [np.bincount(y, minlength=d)]
    for col in range(3):
        C = np.bincount(d * raw[:, col] + y, minlength=d * d).reshape(d, d)
        A = C + C.T
        avg = A.mean(axis=1)
        values, vectors = np.linalg.eigh(A - avg[:, None] - avg[None, :] + avg.mean())
        features.append(vectors[:, abs(values).argmax()])
    best = -1
    for v in features:
        t = -np.ones(d, dtype=np.int64)
        t[np.argsort(v, kind="stable")[d // 2 :]] = 1
        c = signed_counts(t, raw)
        score = int(abs(c).sum())
        if score > best:
            best = score
            result = (t, table_id(np.where(c < 0, -1, 1)), score)
    return result


def samples(rng, n, s, f):
    d = len(s)
    x = rng.integers(d, size=(n, 3))
    z = f[contexts(s[x])]
    drawn = z * np.where(rng.random(n) < (1 + BETA) / 2, 1, -1)
    index = rng.integers(d // 2, size=n)
    y = np.where(
        drawn == 1, np.flatnonzero(s == 1)[index], np.flatnonzero(s == -1)[index]
    )
    return np.column_stack((x, y))


def correlation(r, f, g):
    # Each pair of true and candidate signs has correlation r at uniform names.
    return float(r * ((f @ HADAMARD) * (g @ HADAMARD)) @ (r**DEGREE) / 64)


def gain(corr, strength=BETA):
    return 0.5 * log1p(-(strength**2)) + BETA * atanh(strength) * corr


def selector_envelopes(state_counts):
    coefficients = (TABLES @ HADAMARD) * (SELECTOR @ HADAMARD)
    for i in range(17):
        r = Fraction(i, 16)
        weights = [r ** (1 + int(k)) / 64 for k in DEGREE]
        exact = coefficients @ np.array(weights, dtype=object)
        assert max(exact) == (r**2 + r**3) / 2
        assert max(exact[state_counts["public_clock"] <= 2]) == r**2 / 2 + r**3 / 4
        for kind in ("reset", "rolling"):
            assert max(exact[state_counts[kind] <= 2]) == r**2 / 2
    spectrum = TABLES @ HADAMARD
    first = np.any(spectrum[:, DEGREE == 1] != 0, axis=1)
    biased = spectrum[:, 0] != 0
    assert biased.sum() == 186 and ((~biased) & first).sum() == 62
    return {
        "rational_overlaps": 17,
        "truth_tables": 256,
        "nonzero_mean": 186,
        "balanced_with_first_order_signal": 62,
        "pure_higher_order": 8,
    }


def check(d, state_counts):
    search = Search(d, state_counts)
    x = np.array(list(product(range(d), repeat=4)))
    # A deliberately nonuniform multiset of records also checks the sample fit.
    raw = np.concatenate((x[::5], x[7::11], x[3:19]))
    c = search.counts(raw)
    for k, t in enumerate(search.labels):
        codes = contexts(t[raw[:, :3]])
        expected = np.array([t[raw[codes == z, 3]].sum() for z in range(8)])
        assert np.array_equal(c[k], expected)
    s = search.labels[0]
    for t in search.labels:
        r = (s @ t) / d
        for f in (PRODUCT, SELECTOR, TABLES[7]):
            truth = s[x[:, 3]] * f[contexts(s[x[:, :3]])]
            for g in (PRODUCT, SELECTOR, TABLES[91]):
                fit = t[x[:, 3]] * g[contexts(t[x[:, :3]])]
                exact = truth @ fit / d**4
                assert abs(exact - correlation(r, f, g)) < 1e-14
            actual = (1 + BETA * truth).reshape(-1, d)
            assert np.all(actual.sum(axis=1) == d)
    for name, (i, j) in search.fit(c).items():
        allowed = search.allowed.get(name, np.arange(256))
        brute = (c @ TABLES[allowed].T).max()
        assert c[i] @ TABLES[j] == brute
    # Direct mixture over every one of the 256 tables per partition.
    short_c = search.counts(raw[:17])
    logweights = atanh(BETA) * (short_c @ TABLES.T)
    w = np.exp(logweights - logweights.max())
    w /= w.sum()
    direct = np.zeros(len(x))
    for i, t in enumerate(search.labels):
        table = w[i] @ TABLES
        direct += t[x[:, 3]] * table[contexts(t[x[:, :3]])]
    assert np.max(np.abs(direct - search.posterior(short_c))) < 2e-14
    return {
        "raw_tuples": d**4,
        "candidate_partitions": len(search.labels),
        "direct_score_records": len(raw),
    }


def experiment(state_counts):
    rng = np.random.default_rng(20261127)
    d = 12
    search = Search(d, state_counts)
    reports = []
    for source in ("product", "selector", "uniform_table"):
        for n in (d, 16 * d, 64 * d, 256 * d):
            values = {}
            posterior_gains = []
            for _ in range(128):
                s = rng.permutation(np.tile([1, -1], d // 2))
                f = {"product": PRODUCT, "selector": SELECTOR}.get(source)
                if f is None:
                    f = TABLES[rng.integers(256)]
                raw = samples(rng, n, s, f)
                c = search.counts(raw)
                fitted = {
                    name: (search.labels[i], j, int(c[i] @ TABLES[j]))
                    for name, (i, j) in search.fit(c).items()
                }
                fitted["supplemental_spectral"] = spectral_fit(raw, d)
                truth = s[search.raw[:, 3]] * f[contexts(s[search.raw[:, :3]])]
                posterior_gains.append(
                    float(
                        (1 + BETA * truth) @ np.log1p(BETA * search.posterior(c)) / d**4
                    )
                )
                for name, (t, j, score) in fitted.items():
                    r = float(s @ t / d)
                    g = TABLES[j]
                    exact = (r == 1 and np.array_equal(f, g)) or (
                        r == -1 and np.array_equal(-f[::-1], g)
                    )
                    values.setdefault(name, []).append(
                        [
                            gain(correlation(r, f, g)),
                            abs(r) == 1,
                            exact,
                            *(w[j] for w in state_counts.values()),
                            gain(correlation(r, f, g), np.clip(score / n, 0, BETA)),
                        ]
                    )
            scores = {}
            for name, values_for_method in values.items():
                a = np.array(values_for_method)
                scores[name] = {
                    "mean_gain": float(a[:, 0].mean()),
                    "gain_standard_error": float(a[:, 0].std(ddof=1) / np.sqrt(len(a))),
                    "exact_partition": int(a[:, 1].sum()),
                    "exact_law": int(a[:, 2].sum()),
                    "supplemental_gain_with_fitted_strength": float(a[:, -1].mean()),
                    "mean_minimum_states": {
                        key: float(a[:, h + 3].mean())
                        for h, key in enumerate(state_counts)
                    },
                }
            reports.append(
                {
                    "source": source,
                    "tasks": n,
                    "fits": 128,
                    "methods": scores,
                    "supplemental_full_posterior_gain": float(np.mean(posterior_gains)),
                    "posterior_gain_standard_error": float(
                        np.std(posterior_gains, ddof=1) / np.sqrt(128)
                    ),
                }
            )
    return reports


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    state_counts = widths()
    data = {
        "registration": REGISTRATION,
        "seed": 20261127,
        "vocabulary": 12,
        "contrast": BETA,
        "uniform_gain": 0.0,
        "oracle_gain": gain(1.0),
        "rules_by_minimum_states": {
            key: {str(w): int((value == w).sum()) for w in np.unique(value)}
            for key, value in state_counts.items()
        },
        "selector_states": {
            key: int(value[table_id(SELECTOR)]) for key, value in state_counts.items()
        },
        "product_states": {
            key: int(value[table_id(PRODUCT)]) for key, value in state_counts.items()
        },
        "checks": {d: check(d, state_counts) for d in (4, 6)},
        "selector_and_fourier_checks": selector_envelopes(state_counts),
        "reports": experiment(state_counts),
    }
    raw = json.dumps(data, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(raw.encode())
    else:
        print(raw, end="")
