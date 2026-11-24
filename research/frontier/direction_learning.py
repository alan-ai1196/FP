"""Learn a scalar recurrent projection and a raw-word readout from normalized errors."""

import struct

import numpy as np
from scipy.optimize import minimize
from scipy.signal import lfilter

RATES = (1 / 512, 1 / 128, 1 / 32, 1 / 8, 1.0)
RIDGE = 1e-6
TAGS = {"static": 1, "scalar": 2, "scalar_i16": 3, "common": 4, "diagonal": 5}
UNIT = 32767


def history(errors, rate):
    return lfilter([0.0, rate], [1.0, rate - 1.0], errors, axis=0)


def loss_shift(q, y, z):
    """Log of the normalizer minus the shift of the realized raw word."""
    return np.log(np.sum(q * np.exp(z), axis=1)) - z[np.arange(len(y)), y]


def scalar_loss(q, y, s, b, gain):
    z = s[:, None] * b
    return loss_shift(q, y, gain * z)


def fit_gain(q, y, design, bounds):
    # A bounded derivative root is unique unless the design has no variation.
    ydesign = design[np.arange(len(y)), y]

    def derivative(gain):
        tilted = q * np.exp(gain * design)
        return float(
            np.mean(np.sum(tilted * design, axis=1) / tilted.sum(axis=1) - ydesign)
        )

    lo, hi = bounds
    if derivative(lo) >= 0:
        return lo
    if derivative(hi) <= 0:
        return hi
    from scipy.optimize import brentq

    return float(brentq(derivative, lo, hi, xtol=1e-8))


def fit_directions(q, y, errors, states):
    n, d = states.shape
    moment = states.T @ states / n + RIDGE * np.eye(d)
    eig, vec = np.linalg.eigh(moment)
    inv = (vec / np.sqrt(eig)) @ vec.T
    cross = errors.T @ states / n
    left, sigma, right = np.linalg.svd(cross @ inv, full_matrices=False)
    a = inv @ right[0]
    b = left[:, 0].copy()
    if a[np.argmax(np.abs(a))] < 0:
        a = -a
        b = -b
    scale = 2 * sigma[0] * np.max(np.abs(a)) * np.max(np.abs(b))
    a /= np.max(np.abs(a))
    b /= np.max(np.abs(b))
    cert = sigma[0] ** 2
    realized = float(-scalar_loss(q, y, states @ a, b, scale).mean())
    assert realized >= cert - 3e-12
    ai = np.rint(UNIT * a).astype("<i2")
    bi = np.rint(UNIT * b).astype("<i2")
    design = (states @ (ai.astype(float) / UNIT))[:, None] * (bi.astype(float) / UNIT)
    gain = fit_gain(q, y, design, (0.0, 64.0))
    return (
        ai,
        bi,
        int(np.rint(gain * 256)),
        {
            "quadratic_certificate": float(cert),
            "exact_gain_at_certificate": realized,
            "unrounded_bound_scale": float(scale),
            "fitted_gain": gain,
        },
    )


def fit_diagonal(q, y, states=None):
    d = q.shape[1]
    slope = states is not None
    # The static tail shift is fixed to zero to identify the softmax intercept.
    cols = d if slope else d - 1
    scales = np.sqrt(np.mean(states**2, axis=0)).clip(1e-8) if slope else np.ones(cols)
    rows = np.arange(len(y))

    def objective(v):
        params = v / scales
        z = states * params if slope else np.broadcast_to(np.r_[params, 0.0], q.shape)
        tilted = q * np.exp(z)
        total = tilted.sum(axis=1)
        cost = (np.log(total) - z[rows, y]).mean()
        tilted /= total[:, None]
        tilted[rows, y] -= 1.0
        grad = (tilted * states).mean(axis=0) if slope else tilted[:, :-1].mean(axis=0)
        return float(cost), grad / scales

    limit = 64 if slope else 3
    bounds = [(-limit * s, limit * s) for s in scales]
    result = minimize(
        objective,
        np.zeros(cols),
        jac=True,
        bounds=bounds,
        method="L-BFGS-B",
        options={"maxiter": 350, "ftol": 1e-13, "gtol": 1e-8, "maxls": 40},
    )
    if not result.success:
        raise ArithmeticError(result.message)
    param = result.x / scales
    if not slope:
        param = np.r_[param, 0]
    unit = 256 if slope else 1024
    return np.rint(unit * param).astype("<i2")


def encode(kind, rate, ids, *data):
    return (
        struct.pack("<BB", TAGS[kind], rate)
        + np.asarray(ids, dtype="<u2").tobytes()
        + b"".join(np.asarray(x, dtype="<i2").tobytes() for x in data)
    )


def decode(word):
    tag, rate = struct.unpack_from("<BB", word)
    kind = next(name for name, v in TAGS.items() if v == tag)
    ids = np.frombuffer(word, dtype="<u2", count=32, offset=2)
    data = np.frombuffer(word, dtype="<i2", offset=2 + 2 * len(ids)).astype(float)
    d = len(ids) + 1
    if kind.startswith("scalar"):
        assert len(data) == 2 * d + 1
        params = (data[:d] / UNIT, data[d : 2 * d] / UNIT, data[-1] / 256)
    elif kind == "common":
        assert len(data) == 1
        params = (np.full(d, data[0] / 256),)
    else:
        assert len(data) == d
        params = (data / (1024 if kind == "static" else 256),)
    return kind, RATES[rate], ids, params


def fit_words(q, y, ids):
    errors = -q.copy()
    errors[np.arange(len(y)), y] += 1
    words = [encode("static", 0, ids, fit_diagonal(q, y))]
    certificates = []
    for i, rate in enumerate(RATES):
        states = history(errors, rate)
        a, b, gain, cert = fit_directions(q, y, errors, states)
        certificates.append(cert)
        for kind in ("scalar", "scalar_i16"):
            words.append(encode(kind, i, ids, a, b, gain))
        common = fit_gain(q, y, states, (-64.0, 64.0))
        words.append(encode("common", i, ids, int(np.rint(common * 256))))
        words.append(encode("diagonal", i, ids, fit_diagonal(q, y, states)))
    return words, certificates
