"""Fit both sides of a normalized word correction from ordinary prediction errors."""

import argparse
import base64
import hashlib
import json
import zlib
from fractions import Fraction as F
from itertools import product
from math import prod
from pathlib import Path

import numpy as np
from lexical_switch import tokens, windows
from scipy.optimize import minimize
from text import VOCAB
from threadpoolctl import threadpool_limits
from word_value import Base, quantized, sign_string

REGISTRATION = "5be147a"
TRAIN, LENGTH, START = 131072, 32768, 27000000
DIGEST = "634b826b79cb9871a12788986b0520d1ab3247c016b5e8829aad439085eeb669"
REPORTS = (
    (
        "train_source",
        29000000,
        "91a4746a21de328d782a355e94b6541a3ec4d25b1ecff3dfb02a58b792861b12",
    ),
    (
        "train_source",
        33000000,
        "d42c3ec72a745a3e72374368c58b5da1de585269507efaf61616172228a9f64e",
    ),
    (
        "reporting_source",
        1967232,
        "fe2ce7174972d67b4be62a189f600491dae40cc90e7a0226f1178c8e122b2cb3",
    ),
)
LAGS = (1, 2, 4, 8)
SIZES = (64, 256)
OUTPUTS = (8, 12)
LOW, HIGH = -2.0, 8191 / 4096
PRICES = ("unpriced", "shared_ranks", "standalone")


class ClassMass:
    """Aggregate each positive trigram/backoff row exactly into named output bins."""

    def __init__(self, base, size):
        d = size + 1
        self.bins = np.full(VOCAB, size, dtype=int)
        names = base.bg.names[:size]
        self.bins[names] = np.arange(size)
        lexical = np.r_[base.lexical[names], base.lexical[self.bins == size].sum()]
        kn = base.kn
        unigram = np.r_[kn.unigram[names], kn.unigram[self.bins == size].sum()]
        keys, values = kn.bigram
        big = np.bincount(
            (keys // VOCAB) * d + self.bins[keys % VOCAB],
            weights=10 * values - 9,
            minlength=VOCAB * d,
        ).reshape(-1, d)
        lower = np.divide(
            big / 10 + 0.9 * kn.lower_types[:, None] * unigram,
            kn.lower_total[:, None],
            out=np.broadcast_to(unigram, big.shape).copy(),
            where=kn.lower_total[:, None] > 0,
        )
        self.keys, totals = base.bg.ab
        keys, values = base.bg.aby
        pos = np.searchsorted(self.keys, keys // VOCAB)
        assert np.array_equal(self.keys[pos], keys // VOCAB)
        trigram = np.bincount(
            pos * d + self.bins[keys % VOCAB],
            weights=10 * values - 9,
            minlength=len(self.keys) * d,
        ).reshape(-1, d)
        high = (
            trigram / 10 + 0.9 * np.bincount(pos)[:, None] * lower[self.keys % VOCAB]
        ) / totals[:, None]
        self.rows = (1 - base.mix) * np.vstack((high, lower)) + base.mix * lexical
        assert self.rows.min() > 0 and np.max(abs(self.rows.sum(axis=1) - 1)) < 2e-13

    def lookup(self, a, b):
        key = a * VOCAB + b
        pos = np.minimum(np.searchsorted(self.keys, key), len(self.keys) - 1)
        return np.where(self.keys[pos] == key, pos, len(self.keys) + b)


class Sample:
    def __init__(self, raw, start, n, base, groups):
        a, b, y = windows(raw, start, n)
        keys, self.context = np.unique(groups.lookup(a, b), return_inverse=True)
        self.q = groups.rows[keys]
        self.y = groups.bins[y]
        self.input_rank = {
            lag: base.bg.bins[raw[start - lag : start + n - lag]] for lag in LAGS
        }
        self.base_nll = -np.log(base.point(a, b, y))
        self.set_bias(np.zeros(self.q.shape[1] - 1, dtype=np.int16))

    def set_bias(self, bias):
        self.bias = bias
        delta = np.r_[bias / 4096, 0.0]
        mass = self.q * np.exp(delta)
        denom = mass.sum(axis=1)
        self.cal = mass / denom[:, None]
        self.static = delta[self.y] - np.log(denom[self.context])

    def inputs(self, size, lag):
        return np.minimum(self.input_rank[lag], size)


def minimize_scaled(function, start, scale, lo, hi):
    """Scale each free logit by its approximate information before L-BFGS."""
    shape = start.shape
    sc = scale.ravel()
    lower, upper = np.broadcast_arrays(lo * scale, hi * scale)

    def fun(x):
        val, grad = function((x / sc).reshape(shape))
        return val, grad.ravel() / sc

    fit = minimize(
        fun,
        np.clip(start.ravel() * sc, lower.ravel(), upper.ravel()),
        jac=True,
        method="L-BFGS-B",
        bounds=list(zip(lower.ravel(), upper.ravel())),
        options={"maxiter": 120, "ftol": 3e-13, "gtol": 2e-5, "maxcor": 12},
    )
    if not fit.success:
        raise ArithmeticError(fit.message)
    return (fit.x / sc).reshape(shape), fit.nfev


def fit_direction(data, labels, ridge, start):
    q = data.cal
    d = len(start) + 1
    cases = []
    for sign in (-1, 1):
        freq = np.bincount(data.context[labels == sign], minlength=len(q))
        if freq.sum():
            cases.append((sign, freq))
    target = np.bincount(data.y, weights=labels, minlength=d)[:-1]

    def loss(x):
        val = 0.5 * ridge * (x @ x) - target @ x
        grad = ridge * x - target
        for sign, freq in cases:
            fac = np.exp(np.r_[sign * x, 0.0])
            normalizer = q @ fac
            val += freq @ np.log(normalizer)
            grad += sign * fac[:-1] * (q.T @ (freq / normalizer))[:-1]
        return val, grad

    weight = np.bincount(data.context, minlength=len(q))
    scale = np.sqrt(np.maximum(1.0, ridge + weight @ (q[:, :-1] * (1 - q[:, :-1]))))
    direction, steps = minimize_scaled(loss, start, scale, LOW, HIGH)
    return quantized(direction), steps


def residual(data, inputs, size):
    d = data.cal.shape[1]
    observed = np.bincount(inputs * d + data.y, minlength=size * d).reshape(size, d)
    expected = np.stack(
        [
            np.bincount(inputs, weights=data.cal[data.context, j], minlength=size)
            for j in range(d)
        ],
        axis=1,
    )
    return observed - expected


def both_signs(r):
    """Visit each output mask modulo the simultaneous reversal of both tables."""
    g = r.shape[1] - 1
    integers = np.arange(1 << g, dtype=np.uint32)
    masks = np.ones((g + 1, len(integers)))
    masks[:g] -= 2 * ((integers[None, :] >> np.arange(g)[:, None]) & 1)
    projections = r @ masks
    scores = np.abs(projections).sum(axis=0)
    best = int(np.argmax(scores))
    return (
        masks[:, best].astype(np.int8),
        np.where(projections[:, best] >= 0, 1, -1).astype(np.int8),
        scores[best],
    )


def scalar_fit(data, inputs, z, s):
    m = np.clip(data.cal @ s, -1.0, 1.0)
    actual = s[data.y].astype(float)
    count = len(z)
    n_eval = 0
    for _ in range(8):
        h = z[inputs]
        obs = h @ actual
        plus = np.bincount(data.context[h > 0], minlength=len(m))
        minus = np.bincount(data.context[h < 0], minlength=len(m))

        def details(value, obs=obs, plus=plus, minus=minus):
            t = np.tanh(value)
            grad = (
                obs - plus @ ((m + t) / (1 + m * t)) + minus @ ((m - t) / (1 - m * t))
            )
            gain = (
                value * obs
                - len(inputs) * np.log(np.cosh(value))
                - plus @ np.log1p(m * t)
                - minus @ np.log1p(-m * t)
            )
            return grad, gain

        lo, hi = 0, 8191
        while lo < hi:
            mid = (lo + hi) // 2
            n_eval += 1
            if details(mid / 4096)[0] > 0:
                lo = mid + 1
            else:
                hi = mid
        choices = {lo, max(0, lo - 1)}
        beta = max(sorted(choices), key=lambda v: details(v / 4096)[1])
        n_eval += len(choices)
        value = beta / 4096
        votes = np.bincount(
            inputs,
            weights=value * actual - np.arctanh(m * np.tanh(value))[data.context],
            minlength=count,
        )
        proposed = np.where(votes == 0, z, np.where(votes > 0, 1, -1)).astype(np.int8)
        if np.array_equal(proposed, z):
            break
        z = proposed
    return z, beta, n_eval


def refine(data, inputs, labels, initial, ridge):
    z = labels.copy()
    start = initial
    steps = 0
    for _ in range(5):
        head, neval = fit_direction(data, z[inputs], ridge, start)
        steps += neval
        direction = np.r_[head / 4096, 0.0]
        half = 0.5 * (
            np.log(data.cal @ np.exp(direction)) - np.log(data.cal @ np.exp(-direction))
        )
        votes = np.bincount(
            inputs, weights=direction[data.y] - half[data.context], minlength=len(z)
        )
        proposed = np.where(votes == 0, z, np.where(votes > 0, 1, -1)).astype(np.int8)
        if np.array_equal(z, proposed):
            break
        z = proposed
        start = direction[:-1]
    return z, head, steps


class DirectRows:
    def __init__(self, data, inputs, size):
        self.d = data.cal.shape[1]
        nctx = len(data.cal)
        pair, self.freq = np.unique(inputs * nctx + data.context, return_counts=True)
        self.i = pair // nctx
        self.q = data.cal[pair % nctx]
        self.obs = np.bincount(
            inputs * self.d + data.y, minlength=size * self.d
        ).reshape(size, self.d)[:, :-1]
        self.info = self.groupby(
            self.freq[:, None] * self.q[:, :-1] * (1 - self.q[:, :-1]), size
        )
        self.bias = data.bias / 4096

    def groupby(self, values, size):
        return np.stack(
            [np.bincount(self.i, weights=col, minlength=size) for col in values.T],
            axis=1,
        )

    def fit(self, ridge, start):
        def loss(x):
            mass = self.q.copy()
            mass[:, :-1] *= np.exp(x)[self.i]
            denom = mass.sum(axis=1)
            val = (
                self.freq @ np.log(denom)
                - np.sum(self.obs * x)
                + 0.5 * ridge * np.sum(x * x)
            )
            gradient = (
                self.groupby(mass[:, :-1] * (self.freq / denom)[:, None], len(x))
                - self.obs
                + ridge * x
            )
            return val, gradient

        result, work = minimize_scaled(
            loss, start, np.sqrt(self.info + ridge), LOW - self.bias, HIGH - self.bias
        )
        return result, quantized(result + self.bias), work


def scores(data, spec, output_logits, position=None):
    family, ni = spec["family"], spec.get("inputs", 0)
    indexing = data.inputs(ni, spec["lag"]) if ni else np.zeros(len(data.y), dtype=int)
    if position is not None:
        return output_logits[indexing[position]]
    if family == "base":
        return np.zeros(len(data.y))
    shifts = output_logits[indexing]
    return shifts[np.arange(len(shifts)), data.y] - np.log(
        np.einsum("ij,ij->i", data.q[data.context], np.exp(shifts))
    )


class Selection:
    def __init__(self):
        self.chosen = {}
        self.counts = {}
        self.work = {
            "output_masks": 0,
            "input_projections": 0,
            "direct_objectives": 0,
            "direction_objectives": 0,
            "scalar_objectives": 0,
            "max_distinct_input_context_pairs": 0,
        }

    def consider(self, data, spec, extra_bits, logits):
        family = spec["family"]
        self.counts[family] = self.counts.get(family, 0) + 1
        gain = float(scores(data, spec, logits).sum())
        standalone = extra_bits + 16 * max(
            spec.get("inputs", 0), spec.get("outputs", 0)
        )
        info = {
            **spec,
            "incremental_bits": extra_bits,
            "standalone_bits": standalone,
            "validation_gain": gain,
        }
        for mode, cost in zip(PRICES, (0, extra_bits, standalone)):
            key = family + "_" + mode
            order = (gain - np.log(2) * cost, -standalone)
            if key not in self.chosen or order > self.chosen[key][0]:
                self.chosen[key] = (order, info, logits)


def fit(data, valid, book, g):
    bias, steps = fit_direction(
        data, np.ones(len(data.y), dtype=np.int8), 0.0, np.zeros(g)
    )
    book.work["direction_objectives"] += steps
    data.set_bias(bias)
    valid.set_bias(bias)
    b = np.r_[bias / 4096, 0.0]
    static = {"outputs": g, "bias_q12": bias.tolist()}
    static_bits = 4 + 14 * g
    book.consider(valid, {**static, "family": "pooled"}, static_bits, b[None, :])
    for ni, lag in product(SIZES, LAGS):
        i = data.inputs(ni, lag)
        r = residual(data, i, ni + 1)
        s, z, contrast = both_signs(r)
        assert np.max(abs(r.sum(axis=1))) < 2e-6
        book.work["output_masks"] += 1 << g
        book.work["input_projections"] += (1 << g) * (ni + 1)
        fixed = np.r_[-np.ones(g, dtype=np.int8), 1].astype(np.int8)
        specs = {**static, "inputs": ni, "lag": lag}
        common_bits = static_bits + 3 + ni + 1
        for family, labels, output in (
            ("fixed_output", np.where(r @ fixed >= 0, 1, -1), fixed),
            ("joint_sign", z, s),
        ):
            score = float(labels @ r @ output)
            n = len(data.y)
            cert_beta = score / n
            normal = np.cosh(cert_beta) + labels[i] * (data.cal @ output)[
                data.context
            ] * np.sinh(cert_beta)
            realized = float(
                (cert_beta * labels[i] * output[data.y] - np.log(normal)).sum()
            )
            assert realized + 1e-7 >= score * score / (2 * n)
            labels, beta, work = scalar_fit(data, i, labels, output)
            book.work["scalar_objectives"] += work
            info = {
                **specs,
                "family": family,
                "z": sign_string(labels),
                "s": sign_string(output),
                "beta_q12": beta,
                "residual_contrast": score,
                "certified_train_gain": score * score / (2 * n),
                "realized_train_gain_at_certificate_step": realized,
            }
            logits = b + labels[:, None] * (beta / 4096) * output
            book.consider(
                valid,
                info,
                common_bits + 14 + (g if family == "joint_sign" else 0),
                logits,
            )
            if family == "joint_sign":
                assert abs(contrast - score) < 1e-6
                for ridge in (16, 256):
                    init = np.clip(
                        (output[:-1] - output[-1]) * (beta / 4096), LOW, HIGH
                    )
                    zr, head, work = refine(data, i, labels, init, ridge)
                    book.work["direction_objectives"] += work
                    info = {
                        **specs,
                        "family": "joint_real",
                        "z": sign_string(zr),
                        "head_q12": head.tolist(),
                        "ridge": ridge,
                    }
                    logits = b + zr[:, None] * np.r_[head / 4096, 0.0]
                    book.consider(valid, info, common_bits + 14 * g, logits)
        model = DirectRows(data, i, ni + 1)
        book.work["max_distinct_input_context_pairs"] = max(
            book.work["max_distinct_input_context_pairs"], len(model.i)
        )
        start = np.zeros((ni + 1, g))
        for ridge in (2048, 256, 32):
            start, total, work = model.fit(ridge, start)
            book.work["direct_objectives"] += work
            packed = zlib.compress(np.asarray(total, dtype="<i2").tobytes())
            name = base64.b64encode(packed).decode("ascii")
            info = {
                "family": "direct",
                "outputs": g,
                "inputs": ni,
                "lag": lag,
                "ridge": ridge,
                "total_q12_row_major_zlib_base64": name,
            }
            book.consider(
                valid,
                info,
                7 + 14 * (ni + 1) * g,
                np.pad(total / 4096, ((0, 0), (0, 1))),
            )


def exact_checks():
    q = [[F(1, 4), F(1, 2), F(1, 4)], [F(2, 5), F(1, 5), F(2, 5)]]
    stream = [
        (0, 1, 1),
        (0, 0, 1),
        (1, 0, 2),
        (1, 1, 2),
        (1, 0, 0),
        (2, 0, 0),
        (2, 1, 1),
        (3, 1, 0),
        (3, 0, 1),
    ]
    r = [[F(0) for _ in range(3)] for _ in range(4)]
    for i, ctx, y in stream:
        for j in range(3):
            r[i][j] += int(y == j) - q[ctx][j]
    count = 0
    exact_max = F(0)
    for s in product((-1, 1), repeat=3):
        all_products = []
        votes = [[F(1), F(1)] for _ in r]
        for i, ctx, y in stream:
            for n, sign in enumerate((-1, 1)):
                tilt = [F(2) ** (sign * v) for v in s]
                denom = sum(a * b for a, b in zip(q[ctx], tilt))
                assert sum(a * b / denom for a, b in zip(q[ctx], tilt)) == 1
                votes[i][n] *= tilt[y] / denom
        for z in product((-1, 1), repeat=4):
            exact_max = max(
                exact_max,
                sum(z[i] * r[i][j] * s[j] for i in range(4) for j in range(3)),
            )
            ratio = F(1)
            for i, ctx, y in stream:
                fac = [F(2) ** (z[i] * v) for v in s]
                ratio *= fac[y] / sum(a * b for a, b in zip(q[ctx], fac))
            all_products.append(ratio)
            count += 1
        assert max(all_products) == prod(max(row) for row in votes)
    _, _, found = both_signs(np.array(r, dtype=float))
    assert abs(float(exact_max) - found) < 1e-12
    return {
        "joint_sign_assignments": count,
        "signed_finite_objective_optima": 8,
        "maximum_residual_contrast": str(exact_max),
    }


def experiment(directory):
    audit = exact_checks()
    base = Base(directory)
    counts = np.bincount(
        base.bg.aby[0] % VOCAB, weights=base.bg.aby[1], minlength=VOCAB
    )
    assert np.array_equal(
        np.argsort(-counts, kind="stable")[: max(SIZES)], base.bg.names
    )
    groups = {g: ClassMass(base, g) for g in OUTPUTS}
    raw = tokens("train_source", START + TRAIN + LENGTH, DIGEST, directory)
    book = Selection()
    biases = {}
    for g, group in groups.items():
        train = Sample(raw, START, TRAIN, base, group)
        valid = Sample(raw, START + TRAIN, LENGTH, base, group)
        if g == OUTPUTS[0]:
            book.consider(valid, {"family": "base"}, 0, np.zeros((1, g + 1)))
        fit(train, valid, book, g)
        biases[g] = train.bias.copy()

    reports = []
    for role, start, digest in REPORTS:
        raw = tokens(role, start + LENGTH, digest, directory)
        samples = {
            g: Sample(raw, start, LENGTH, base, group) for g, group in groups.items()
        }
        for g, sample in samples.items():
            sample.set_bias(biases[g])
        pos = 1234
        prob = base.point(
            np.full(VOCAB, int(raw[start + pos - 2])),
            np.full(VOCAB, int(raw[start + pos - 1])),
            np.arange(VOCAB),
        )
        y = raw[start + pos]
        # Use 64-bit context IDs when combining them into trigram keys.
        assert abs(prob.sum() - 1) < 2e-12
        normalization_error = 0.0
        methods = {}
        for key, (_, spec, logits) in book.chosen.items():
            g = spec.get("outputs", OUTPUTS[0])
            data, group = samples[g], groups[g]
            gain = scores(data, spec, logits)
            delta = scores(data, spec, logits, pos)
            bins = np.bincount(group.bins, weights=prob, minlength=g + 1)
            norm = bins @ np.exp(delta)
            actual = prob * np.exp(delta[group.bins]) / norm
            error = max(
                abs(bins - data.q[data.context[pos]]).max(),
                abs(actual.sum() - 1),
                abs(np.log(actual[y] / prob[y]) - gain[pos]),
            )
            normalization_error = max(normalization_error, float(error))
            row = {
                "nll_per_word": float(np.mean(data.base_nll - gain)),
                "gain_nats": float(gain.sum()),
                "gain_by_4096_words": gain.reshape(8, -1).sum(axis=1).tolist(),
            }
            if spec["family"] != "base":
                row["gain_over_same_pooled_offsets"] = float((gain - data.static).sum())
            if "z" in spec:
                z = np.array([1 if label == "+" else -1 for label in spec["z"]])
                positive = z[data.inputs(spec["inputs"], spec["lag"])] > 0
                row["positive_input_occurrences"] = int(positive.sum())
                row["gain_over_pooled_positive_negative"] = [
                    float((gain - data.static)[which].sum())
                    for which in (positive, ~positive)
                ]
            methods[key] = row
        assert normalization_error < 2e-12, normalization_error
        reports.append(
            {
                "role": role,
                "offset": start,
                "prefix_sha256": digest,
                "methods": methods,
                "full_row_max_error": normalization_error,
            }
        )
    installed, selected = {}, {}
    for key, (order, info, _) in book.chosen.items():
        name = (
            info["family"]
            + "-"
            + hashlib.sha256(json.dumps(info, sort_keys=True).encode()).hexdigest()[:12]
        )
        installed[name] = info
        selected[key] = {"model": name, "validation_score_after_price": order[0]}
    return {
        "registered_at": REGISTRATION,
        "train_offset": START,
        "train_words": TRAIN,
        "select_words": LENGTH,
        "train_validation_prefix_sha256": DIGEST,
        "ranked_raw_names": base.bg.names.tolist(),
        "exact_checks": audit,
        "work": book.work,
        "candidates": book.counts,
        "installed": installed,
        "selected": selected,
        "reports": reports,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--data-dir", type=Path)
    args = parser.parse_args()
    with threadpool_limits(limits=1):
        result = experiment(args.data_dir)
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(serialized.encode())
    else:
        print(serialized, end="")
