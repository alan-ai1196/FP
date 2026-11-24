"""Likelihood training and packed execution of a latent word-class correction."""

import _ctypes
import ctypes
import os
import struct
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
from causal_state import binary_sizes, compile_libraries
from scipy.optimize import minimize
from scipy.special import expit, logit

MIN_RATE = 1 / 2048
TAGS = {
    "static": 1,
    "iid": 2,
    "persistent": 3,
    "persistent_u8": 4,
    "persistent_u16": 5,
    "residual": 6,
    "iid_ablation": 7,
}


def packet(name, x):
    if name == "base":
        return b""
    tag = TAGS[name]
    b0 = int(np.rint(1024 * x[0]))
    if name == "static":
        return struct.pack("<Bh", tag, b0)
    b1 = int(np.rint(1024 * x[1]))
    probability = int(np.rint(65535 * x[2]))
    if name in ("iid", "residual", "iid_ablation"):
        return struct.pack("<BhhH", tag, b0, b1, probability)
    return struct.pack("<BhhHH", tag, b0, b1, probability, int(np.rint(65535 * x[3])))


def unpack(word):
    if not word:
        return "base", np.empty(0)
    name = next(k for k, v in TAGS.items() if v == word[0])
    if name == "static":
        return name, np.array([struct.unpack("<Bh", word)[1] / 1024])
    if len(word) == 7:
        _, a, b, p = struct.unpack("<BhhH", word)
        values = [a / 1024, b / 1024, p / 65535]
        if name != "residual":
            values.append(1.0)
    else:
        _, a, b, p, h = struct.unpack("<BhhHH", word)
        values = [a / 1024, b / 1024, p / 65535, h / 65535]
    return name, np.array(values)


def levels(name):
    return {"persistent_u8": 256, "persistent_u16": 65536}.get(name, 0)


def initial(name, x):
    size = levels(name)
    if size:
        pi, h = x[2:]
        lo, hi = logit(h * pi), logit(1 - h * (1 - pi))
        code = (
            int(np.floor(0.5 + (size - 1) * (logit(pi) - lo) / (hi - lo)))
            if h < 1
            else 0
        )
        return np.array([code], np.uint8 if size == 256 else np.uint16)
    return np.array([x[2] if name == "persistent" else 0.0])


class Kernels:
    def __enter__(self):
        self.tmp = TemporaryDirectory()
        (path,) = compile_libraries(
            Path(self.tmp.name),
            ("address",),
            Path(__file__).with_name("word_persistence.c"),
        )
        self.binary = binary_sizes(path)
        self.lib = ctypes.CDLL(str(path))
        pd = np.ctypeslib.ndpointer(np.float64, flags="C_CONTIGUOUS")
        py = np.ctypeslib.ndpointer(np.uint8, flags="C_CONTIGUOUS")
        base = [ctypes.c_uint32, pd, py, pd]
        for fn in (self.lib.hidden_fit, self.lib.residual_fit):
            fn.argtypes, fn.restype = [*base, pd], ctypes.c_double
        self.lib.hidden_stream.argtypes = [*base, ctypes.c_uint32, ctypes.c_void_p, pd]
        self.lib.hidden_stream.restype = None
        self.lib.residual_stream.argtypes = [*base, pd, pd]
        self.lib.residual_stream.restype = None
        return self

    def __exit__(self, *exc):
        (_ctypes.FreeLibrary if os.name == "nt" else _ctypes.dlclose)(self.lib._handle)
        self.tmp.cleanup()

    def objective(self, kind, x, r, y):
        if kind == "static":
            z = x[0]
            odds = np.exp(z)
            den = 1 + (odds - 1) * r
            return np.mean(np.log(den) - y * z), np.array([np.mean(odds * r / den - y)])
        full = np.r_[x, 1.0] if kind == "iid" else np.ascontiguousarray(x)
        grad = np.empty_like(full)
        fn = self.lib.residual_fit if kind == "residual" else self.lib.hidden_fit
        value = fn(len(r), r, y, full, grad)
        return value / len(r), grad[: len(x)] / len(r)

    def release(self, word, r, y, carry):
        name, x = unpack(word)
        if name == "base":
            return r.copy()
        if name == "static":
            w = np.exp(x[0])
            return r * w / (1 + (w - 1) * r)
        if name in ("iid", "iid_ablation"):
            a, b = np.exp(x[:2])
            return (1 - x[2]) * a * r / (1 + (a - 1) * r) + x[2] * b * r / (
                1 + (b - 1) * r
            )
        out = np.empty(len(r))
        if name == "residual":
            self.lib.residual_stream(len(r), r, y, x, carry, out)
        else:
            self.lib.hidden_stream(
                len(r), r, y, x, levels(name), carry.ctypes.data, out
            )
        return out


def fit(kind, kernels, r, y):
    start = {
        "static": [[0.0]],
        "iid": [[-0.3, 0.3, 0.5], [-1.0, 0.5, 0.25], [-1.0, 1.0, 0.75]],
        "persistent": [
            [-0.5, 0.5, 0.5, 1 / 128],
            [-0.5, 0.5, 0.5, 1 / 16],
            [-0.8, 0.3, 0.25, 0.25],
            [-0.3, 0.8, 0.75, 0.5],
        ],
        "residual": [[0.0, 1.0, 1 / 64], [0.0, 1.0, 1 / 8], [0.0, 1.0, 0.5]],
    }[kind]
    bounds = {
        "static": [(-3, 3)],
        "iid": [(-3, 3), (-3, 3), (0.02, 0.98)],
        "persistent": [(-3, 3), (-3, 3), (0.02, 0.98), (MIN_RATE, 1)],
        "residual": [(-3, 3), (-16, 16), (MIN_RATE, 1)],
    }[kind]
    fits = []
    for v in start:
        opt = minimize(
            lambda x: kernels.objective(kind, x, r, y),
            v,
            jac=True,
            bounds=bounds,
            method="L-BFGS-B",
            options={"ftol": 2e-14, "gtol": 1e-8, "maxiter": 240, "maxls": 45},
        )
        if not opt.success:
            raise ArithmeticError((kind, opt.message))
        fits.append((float(opt.fun), opt.x, int(opt.nfev)))
    order = sorted(range(len(fits)), key=lambda i: fits[i][0])
    return fits[order[0]][1], [
        {"mean_relative_nll": v, "evaluations": n} for v, _, n in fits
    ]


def reference_hidden(x, r, y, codes=0):
    """Independent Bayes update from class probabilities and logit likelihood ratios."""
    a, b, pi, h = x
    lo, hi = logit(h * pi), logit(1 - h * (1 - pi))

    def rounded(v):
        if codes and h < 1:
            code = np.floor(0.5 + (logit(v) - lo) * (codes - 1) / (hi - lo))
            return expit(lo + np.clip(code, 0, codes - 1) * (hi - lo) / (codes - 1))
        return v

    w = rounded(pi)
    forecasts, priors = [], []
    for mass, hit in zip(r, y):
        p0, p1 = expit(logit(mass) + a), expit(logit(mass) + b)
        priors.append(w)
        forecasts.append(p0 + w * (p1 - p0))
        evidence = np.log(p1 / p0) if hit else np.log((1 - p1) / (1 - p0))
        u = expit(logit(w) + evidence)
        w = rounded(h * pi + (1 - h) * u)
    return np.array(forecasts), np.array(priors)
