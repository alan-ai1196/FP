"""Causal native replay with one persistent scalar or a vector of class errors."""

import _ctypes
import ctypes
import os
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
from causal_state import binary_sizes, compile_libraries
from direction_learning import UNIT, decode, loss_shift


class Native:
    def __enter__(self):
        self.tmp = TemporaryDirectory()
        (path,) = compile_libraries(
            Path(self.tmp.name),
            ("address",),
            Path(__file__).with_name("direction_filter.c"),
        )
        self.binary = binary_sizes(path)
        self.lib = ctypes.CDLL(str(path))
        u32 = ctypes.c_uint32
        pd = np.ctypeslib.ndpointer(np.float64, flags="C_CONTIGUOUS")
        py = np.ctypeslib.ndpointer(np.uint8, flags="C_CONTIGUOUS")
        start = [u32, u32, pd, py]
        self.lib.direction_stream.argtypes = [
            *start,
            pd,
            pd,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            u32,
            ctypes.c_void_p,
            pd,
        ]
        self.lib.diagonal_stream.argtypes = [*start, pd, ctypes.c_double, pd, pd]
        self.lib.direction_stream.restype = self.lib.diagonal_stream.restype = None
        return self

    def __exit__(self, *_):
        (_ctypes.FreeLibrary if os.name == "nt" else _ctypes.dlclose)(self.lib._handle)
        self.tmp.cleanup()

    def release(self, decoded, q, y, carry):
        kind, rate, _, params = decoded
        if kind == "static":
            return loss_shift(q, y, np.broadcast_to(params[0], q.shape))
        out = np.empty(len(q))
        if kind.startswith("scalar"):
            a, b, gain = params
            self.lib.direction_stream(
                len(q),
                q.shape[1],
                q,
                y,
                a,
                b,
                gain,
                rate,
                float(np.ptp(a)),
                int(kind == "scalar_i16"),
                carry.ctypes.data,
                out,
            )
        else:
            self.lib.diagonal_stream(
                len(q), q.shape[1], q, y, params[0], rate, carry, out
            )
        return out


def initial(decoded):
    kind, _, ids, _ = decoded
    if kind == "static":
        return np.zeros(0)
    if kind.startswith("scalar"):
        return np.zeros(1, np.int16 if kind == "scalar_i16" else np.float64)
    return np.zeros(len(ids) + 1)


def reference_logits(word, states, errors):
    kind, rate, _, params = decode(word)
    if kind == "static":
        return np.broadcast_to(params[0], states.shape)
    if not kind.startswith("scalar"):
        return states * params[0]
    a, b, g = params
    if kind == "scalar_i16":
        projection = errors @ a
        stored = np.empty(len(states))
        s = 0.0
        spread = float(np.ptp(a))
        if spread:
            for t, value in enumerate(projection):
                stored[t] = s
                grid = (s + rate * (value - s)) * UNIT / spread
                s = np.copysign(np.floor(abs(grid) + 0.5), grid) * spread / UNIT
        else:
            stored.fill(0)
    else:
        stored = states @ a
    return (g * stored[:, None]) * b
