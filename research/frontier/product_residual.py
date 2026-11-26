"""Construct every factor of a raw-name product from one normalized residual tensor."""

import argparse
import json
from itertools import product
from math import log, prod
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from threadpoolctl import threadpool_limits

REGISTRATION = "04a8519"
NAMES = 8
LENGTHS = (2, 3, 4)
SIZES = (256, 2048, 16384)
STRENGTHS = (0.0, 0.5, 0.75)
REPEATS = 16
CAL = 512


def sign(x):
    return np.where(x >= 0, 1, -1).astype(np.int8)


def values(tables):
    shape = tuple(len(t) for t in tables)
    result = np.ones(shape, dtype=np.int8)
    for axis, table in enumerate(tables):
        broadcast = [1] * len(shape)
        broadcast[axis] = len(table)
        result *= table.reshape(broadcast)
    return result


def oriented(tensor, tables):
    out = [t.copy() for t in tables]
    if np.sum(tensor * values(out)) < 0:
        out[-1] *= -1
    return out


def fiber_signs(tensor, order):
    current = tensor
    axes = list(range(tensor.ndim))
    tables = [None] * len(axes)
    for axis in order:
        pos = axes.index(axis)
        layer = np.moveaxis(current, pos, 0)
        fibers = layer.reshape(layer.shape[0], -1)
        row_order = np.argsort(-np.einsum("ij,ij->i", fibers, fibers), kind="stable")
        accumulated = np.zeros(fibers.shape[1], dtype=tensor.dtype)
        labels = np.ones(len(fibers), dtype=np.int8)
        for j in row_order:
            if accumulated @ fibers[j] < 0:
                labels[j] = -1
            accumulated += labels[j] * fibers[j]
        tables[axis] = labels
        current = accumulated.reshape(layer.shape[1:])
        axes.pop(pos)
    if current.item() < 0:
        tables[-1] *= -1
    return tables


def spectral(tensor):
    tables = []
    for axis, n in enumerate(tensor.shape):
        layer = np.moveaxis(tensor, axis, 0).reshape(n, -1).astype(float)
        _, basis = np.linalg.eigh(layer @ layer.T)
        tables.append(sign(basis[:, -1]))
    return oriented(tensor, tables)


def sparse_fiber_signs(entries, shape):
    """Keys encode the remaining tuple in mixed radix; zero entries need no storage."""
    current = dict(entries)
    divisor = prod(shape)
    tables = []
    visits = 0
    for k in shape:
        divisor //= k
        fibers = [{} for _ in range(k)]
        for key, val in current.items():
            name, suffix = divmod(key, divisor)
            fibers[name][suffix] = val
        visits += len(current)
        order = sorted(
            range(k), key=lambda name: -sum(x * x for x in fibers[name].values())
        )
        accumulated = {}
        labels = np.ones(k, dtype=np.int8)
        for name in order:
            fiber = fibers[name]
            orientation = (
                1
                if sum(accumulated.get(j, 0) * x for j, x in fiber.items()) >= 0
                else -1
            )
            labels[name] = orientation
            for j, x in fiber.items():
                accumulated[j] = accumulated.get(j, 0) + orientation * x
        tables.append(labels)
        current = {j: x for j, x in accumulated.items() if x}
    score = current.get(0, 0)
    if score < 0:
        tables[-1] *= -1
    return tables, abs(score), visits


def regularized_check():
    """Compare deterministic growth with an independent saturated convex fit."""
    rng = np.random.default_rng(20261127)
    shape = (3, 4, 3, 4)
    target = rng.integers(1, 14, size=shape)
    weights = target.sum(axis=-1) / target.sum()
    base = rng.uniform(0.05, 1, size=shape)
    base /= base.sum(axis=-1, keepdims=True)
    observed = target / target.sum()
    ridge = 0.03

    def objective(flat):
        w = flat.reshape(shape)
        mass = base * np.exp(w)
        norm = mass.sum(axis=-1)
        f = (
            np.sum(weights * np.log(norm))
            - np.sum(observed * w)
            + 0.5 * ridge * np.sum(w * w)
        )
        grad = weights[..., None] * mass / norm[..., None] - observed + ridge * w
        return f, grad.ravel()

    solve = minimize(
        objective,
        np.zeros(prod(shape)),
        jac=True,
        method="L-BFGS-B",
        options={"gtol": 1e-12, "ftol": 1e-15},
    )
    assert solve.success
    w = np.zeros(shape)
    start = -solve.fun
    smooth = 1 + ridge * w.size
    rate = 1 - 2 * ridge / smooth
    path = []
    for step in range(257):
        loss, flat = objective(w.ravel())
        grad = flat.reshape(shape)
        assert np.max(abs(grad.sum(axis=-1))) < 2e-14
        gap = loss - solve.fun
        assert gap <= start * rate**step + 1e-12
        if step in (0, 1, 4, 16, 64, 256):
            path.append(
                {
                    "steps": step,
                    "excess": float(gap),
                    "theorem_bound": start * rate**step,
                }
            )
        factors = fiber_signs(-grad, range(len(shape)))
        atom = values(factors).astype(float)
        atom -= atom.mean(axis=-1, keepdims=True)
        direction = -np.sum(grad * atom)
        assert direction**2 + 1e-20 >= 2 * np.sum(grad * grad)
        w += direction / smooth * atom
    return {
        "complete_logit_dimension": w.size,
        "ridge": ridge,
        "contraction_factor": rate,
        "path": path,
    }


def improve(tensor, tables):
    result = oriented(tensor, tables)
    all_values = values(result)
    for sweep in range(1, 65):
        changed = False
        for axis, n in enumerate(tensor.shape):
            signed = (
                np.moveaxis(tensor * all_values, axis, 0).reshape(n, -1).sum(axis=1)
            )
            if (signed < 0).any():
                result[axis][signed < 0] *= -1
                all_values = values(result)
                changed = True
        if not changed:
            return result, sweep
    return result, 64


def exact_product(tensor):
    choices = []
    for n in tensor.shape[:-1]:
        choices.append(
            [np.array((1, *v), dtype=np.int8) for v in product((-1, 1), repeat=n - 1)]
        )
    best = -1
    result = None
    for fixed in product(*choices):
        contracted = tensor
        for table in fixed:
            contracted = np.tensordot(table, contracted, axes=(0, 0))
        score = int(np.abs(contracted).sum())
        if score > best:
            best = score
            result = [*fixed, sign(contracted)]
    return result, best


def gain(mean, forecast):
    return 0.5 * ((1 + mean) * np.log1p(forecast) + (1 - mean) * np.log1p(-forecast))


def additive_fit(counts, totals, coords):
    l = coords.shape[0]
    k = counts.shape[0]
    count = counts.ravel()
    total = totals.ravel()

    def objective(v):
        grid = v.reshape(l, k)
        logits = sum(grid[a, coord] for a, coord in enumerate(coords))
        loss = np.sum(count * np.logaddexp(logits, -logits) - total * logits) + 4.0 * (
            v @ v
        )
        err = count * np.tanh(logits) - total
        grad = (
            np.concatenate([np.bincount(c, weights=err, minlength=k) for c in coords])
            + 8 * v
        )
        return loss, grad

    fit = minimize(
        objective,
        np.zeros(l * k),
        method="L-BFGS-B",
        jac=True,
        options={"ftol": 1e-13, "gtol": 1e-7},
    )
    assert fit.success, fit.message
    grid = fit.x.reshape(l, k)
    return np.tanh(sum(grid[a, c] for a, c in enumerate(coords))).reshape(counts.shape)


def integer_checks():
    rng = np.random.default_rng(20261127)
    checked = exact_matches = cases = 0
    worst_ratio = 1.0
    for shape in ((2, 2), (2, 2, 2), (2, 2, 2, 2), (3, 3, 3), (3, 2, 2, 3)):
        for _ in range(64):
            a = rng.integers(-5, 6, size=shape)
            raw = fiber_signs(a, list(range(len(shape))))
            objective = int(np.sum(a * values(raw)))
            norm = int(np.sum(a * a))
            assert objective**2 >= norm
            sparse = {i: int(x) for i, x in enumerate(a.ravel()) if x}
            encoded, score, _ = sparse_fiber_signs(sparse, shape)
            assert score == objective and np.array_equal(values(encoded), values(raw))
            _, best = exact_product(a)
            assert objective <= best
            exact_matches += int(objective == best)
            worst_ratio = min(worst_ratio, objective / best if best else 1.0)
            checked += 1
    for l in (2, 3, 4):
        for _ in range(32):
            tables = [sign(rng.normal(size=4)) for _ in range(l)]
            truth = values(tables)
            a = truth * rng.integers(1, 10, size=truth.shape)
            learned = values(fiber_signs(a, list(range(l))))
            assert np.array_equal(learned, truth)
            cases += 1
    large_shape = (64,) * 12
    sample = rng.integers(64, size=(4096, 12))
    entries = {}
    for i, row in enumerate(sample):
        key = 0
        for name in row:
            key = key * 64 + int(name)
        entries[key] = entries.get(key, 0) + (1 if i % 2 == 0 else -1)
    tables, score, visits = sparse_fiber_signs(entries, large_shape)
    realized = sum(
        (1 if i % 2 == 0 else -1) * prod(int(t[name]) for t, name in zip(tables, row))
        for i, row in enumerate(sample)
    )
    assert score == realized and score**2 >= sum(x * x for x in entries.values())
    return {
        "integer_tensors_checked": checked,
        "fiber_also_globally_optimal": exact_matches,
        "smallest_score_fraction_of_global_optimum": worst_ratio,
        "positive_weight_signed_products_recovered": cases,
        "sparse_twelve_slot_check": {
            "possible_tuples": str(prod(large_shape)),
            "occupied_tuples": len(entries),
            "nonzero_entries_visited_across_contractions": visits,
            "realized_contrast": score,
        },
        "regularized_multiclass_growth": regularized_check(),
    }


def record(agg, method, truth, pred, hold, extra=None):
    stats = agg.setdefault(method, {"runs": 0})
    stats["runs"] += 1
    gains = gain(truth, pred)
    for key, x in (
        ("held_gain", gains[hold].mean()),
        ("seen_gain", gains[~hold].mean()),
        ("all_gain", gains.mean()),
    ):
        stats[key] = stats.get(key, 0.0) + float(x)
    for key, x in (extra or {}).items():
        stats[key] = stats.get(key, 0) + x


def trial(l, rep, strength, results, work):
    shape = (NAMES,) * l
    rng = np.random.default_rng(np.random.SeedSequence([20261127, l, rep]))
    tables = [
        rng.permutation(np.tile([-1, 1], NAMES // 2)).astype(np.int8) for _ in range(l)
    ]
    hidden = values(tables)
    total_cells = hidden.size
    hold = np.zeros(total_cells, dtype=bool)
    hold[rng.choice(total_cells, total_cells // 4, replace=False)] = True
    visible = np.flatnonzero(~hold)
    hold = hold.reshape(shape)
    x = rng.choice(visible, max(SIZES))
    y = hidden.ravel()[x] * np.where(rng.random(len(x)) < (1 + strength) / 2, 1, -1)
    cx = rng.choice(visible, CAL)
    cy = hidden.ravel()[cx] * np.where(rng.random(CAL) < (1 + strength) / 2, 1, -1)
    coords = np.indices(shape).reshape(l, -1)
    pop = strength * hidden
    raw_amp = strength or 0.5
    for n in SIZES:
        stats = results.setdefault((l, strength, n), {})
        counts = np.bincount(x[:n], minlength=total_cells).reshape(shape)
        totals = (
            np.bincount(x[:n], weights=y[:n], minlength=total_cells)
            .reshape(shape)
            .astype(np.int64)
        )
        base = totals / (counts + 1)
        record(stats, "direct_tuple", pop, base, hold)
        record(stats, "additive", pop, additive_fit(counts, totals, coords), hold)
        choices = []
        for axis in range(l):
            for prior in (1, 16, 128):
                mean = totals.sum(axis=axis, keepdims=True) / (
                    counts.sum(axis=axis, keepdims=True) + prior
                )
                mean = np.broadcast_to(mean, shape)
                score = np.log1p(cy * mean.ravel()[cx]).sum()
                choices.append((score, mean))
        best = max(choices, key=lambda item: item[0])[1]
        record(stats, "leave_one_out", pop, best, hold)
        forward = fiber_signs(totals, list(range(l)))
        reverse = fiber_signs(totals, list(reversed(range(l))))
        leading = spectral(totals)
        paths = {"fiber": forward, "spectral": leading}
        draws = np.random.default_rng(np.random.SeedSequence([rep, l, n, 9907]))
        starts = [
            forward,
            reverse,
            leading,
            *[[sign(draws.normal(size=NAMES)) for _ in range(l)] for _ in range(4)],
        ]
        options = []
        for start in starts:
            fit, sweeps = improve(totals, start)
            work["alternating_sweeps"] += sweeps
            options.append((np.sum(totals * values(fit)), fit))
        paths["alternating"] = max(options, key=lambda x: x[0])[1]
        if l == 2:
            paths["exhaustive"], _ = exact_product(totals)
        work["fiber_starts"] += 2
        work["mode_eigensystems"] += l
        for method, fit in paths.items():
            h = values(fit)
            full = np.array_equal(h, hidden)
            corr = int(np.sum(totals * h))
            if method == "fiber":
                assert corr**2 >= int(np.sum(totals * totals))
            fixed = h * raw_amp
            record(
                stats,
                method,
                pop,
                fixed,
                hold,
                {
                    "exact_product": int(full),
                    "held_sign_accuracy": float((h[hold] == hidden[hold]).mean()),
                    "training_correlation": corr / n,
                },
            )
            votes = cy * h.ravel()[cx]
            amp = float(np.clip(np.rint(4096 * votes.mean()) / 4096, -0.95, 0.95))
            install = bool(np.log1p(amp * votes).sum() > (14 + 7 * l + 3) * log(2))
            record(
                stats,
                method + "_calibrated",
                pop,
                amp * h if install else np.zeros(shape),
                hold,
                {"installations": int(install)},
            )


def experiment():
    checks = integer_checks()
    stats = {}
    work = {"fiber_starts": 0, "mode_eigensystems": 0, "alternating_sweeps": 0}
    for l, rep, strength in product(LENGTHS, range(REPEATS), STRENGTHS):
        trial(l, rep, strength, stats, work)
    rows = []
    for (l, strength, n), methods in sorted(stats.items()):
        for d in methods.values():
            for key in (
                "held_gain",
                "seen_gain",
                "all_gain",
                "held_sign_accuracy",
                "training_correlation",
            ):
                if key in d:
                    d[key] /= d["runs"]
        rows.append(
            {
                "slots": l,
                "strength": strength,
                "training_panels": n,
                "oracle_gain": float(gain(strength, strength)),
                "methods": methods,
            }
        )
    return {
        "registration": REGISTRATION,
        "names_per_slot": NAMES,
        "calibration_panels": CAL,
        "hidden_fraction": 0.25,
        "assignments_per_case": REPEATS,
        "integer_checks": checks,
        "training_work": work,
        "cases": rows,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with threadpool_limits(limits=1):
        result = experiment()
    body = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_bytes(body.encode())
    else:
        print(body, end="")
