"""Learn a delay and price two reusable online representations of its history."""

import argparse
import ctypes
import json
import os
import shutil
import struct
import subprocess
import tempfile
from fractions import Fraction as F
from math import ceil, floor
from pathlib import Path
from time import perf_counter

import numpy as np
from text import SCALE, outward, ratio_log

DELAY = 258048
LIMIT = 262144
SAMPLES = 256
PRICES = (F(0), F(3, 10), F(2, 5))
NAMES = ("fair", "raw", "coded")


def identify():
    rng = np.random.Generator(np.random.PCG64(2026112311))
    last = LIMIT // 2
    counts = np.zeros(last, dtype=np.int32)
    for _ in range(SAMPLES // 8):
        data = rng.integers(2, size=(8, LIMIT + 1), dtype=np.uint8)
        tail = LIMIT + 1 - DELAY
        data[:, DELAY:] = data[:, :tail] ^ (
            rng.integers(8, size=(8, tail), dtype=np.uint8) == 0
        )
        # Column zero is the past bit for the largest lag.
        counts += (data[:, :last] == data[:, -1:]).sum(axis=0, dtype=np.int32)[::-1]
    ordered = np.sort(counts)
    return last + 1 + int(np.argmax(counts)), int(ordered[-1]), int(ordered[-2])


def stream(periods, seed, lag):
    rng = np.random.Generator(np.random.PCG64(seed))
    data = np.empty((periods + 1, DELAY), dtype=np.uint8)
    data[0] = rng.integers(2, size=DELAY, dtype=np.uint8)
    for j in range(1, len(data)):
        data[j] = data[j - 1] ^ (rng.integers(8, size=DELAY, dtype=np.uint8) == 0)
    history = data[0, -lag:]
    if lag > len(history):
        history = np.pad(history, (lag - len(history), 0))
    return np.concatenate([history, data[1:].ravel()])


def estimate(raw):
    """Independent re-encoding reference. The C model stores only the declared packed ring."""
    result = raw.copy()
    end = len(raw) // 63 * 63
    bits = result[:end].reshape(-1, 63)
    position = np.arange(1, 64, dtype=np.uint8)
    syndrome = np.bitwise_xor.reduce(np.where(bits, position, 0), axis=1)
    bad = np.flatnonzero(syndrome)
    bits[bad, syndrome[bad] - 1] ^= 1
    return result


def errors(data, lag):
    raw = int(np.count_nonzero(data[lag:] != data[:-lag]))
    coded = 0
    for i in range(lag, len(data), lag):
        current = data[i : i + lag]
        pred = estimate(data[i - lag : i])
        coded += int(np.count_nonzero(pred[: len(current)] != current))
    return {"raw": raw, "coded": coded}


def binary_cost(error, rate):
    low = high = F(0)
    for amount, prob in ((error, rate), (1 - error, 1 - rate)):
        l, h = ratio_log(prob.denominator, prob.numerator)
        low += amount * l
        high += amount * h
    return low, high


def printed(interval):
    return outward((floor(interval[0]), ceil(interval[1])), 1)


def population(lag):
    eta = F(1, 8)
    protected = lag // 63 * 63
    coded = eta + (1 - 2 * eta) * F(protected, lag * 64)
    return {"fair": F(1, 2), "raw": eta, "coded": coded}


def charges(lag):
    return {
        "fair": 0,
        "raw": 8 * ((lag + 7) // 8 + 18),
        "coded": 8 * ((57 * (lag // 63) + lag % 63 + 7) // 8 + 128),
    }


def compare(counts, n, params, bits, lag, price):
    intervals = {}
    for name in NAMES:
        err = F(counts[name], n) if name != "fair" else F(1, 2)
        base = binary_cost(err, params[name])
        rent = price * bits[name] * SCALE / lag
        intervals[name] = tuple(x + rent for x in base)
    chosen = min(NAMES, key=lambda name: intervals[name][1])
    assert all(
        intervals[chosen][1] < intervals[name][0] for name in NAMES if name != chosen
    )
    return chosen, {k: printed(v) for k, v in intervals.items()}


def compile_libraries(directory, modes=("raw", "both")):
    source = Path(__file__).with_name("delayed_state.c").resolve()
    if os.name == "nt":
        from locale import getpreferredencoding

        finder = (
            Path(os.environ["ProgramFiles(x86)"])
            / "Microsoft Visual Studio/Installer/vswhere.exe"
        )
        installation = subprocess.check_output(
            [
                str(finder),
                "-latest",
                "-products",
                "*",
                "-requires",
                "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
                "-property",
                "installationPath",
            ],
            text=True,
        ).strip()
        setup = Path(installation) / "VC/Auxiliary/Build/vcvars64.bat"
        listing = subprocess.check_output(
            f'call "{setup}" >nul && set',
            shell=True,
            encoding=getpreferredencoding(False),
            errors="replace",
        )
        env = dict(
            line.split("=", 1)
            for line in listing.splitlines()
            if "=" in line and not line.startswith("=")
        )
        search = next(v for k, v in env.items() if k.upper() == "PATH")
        compiler = shutil.which("cl", path=search)
        suffix = ".dll"
    else:
        env = None
        compiler = shutil.which("cc")
        suffix = ".so"
    if not compiler:
        raise RuntimeError(
            "a native C compiler is needed for the optional packed-kernel check"
        )
    libraries = []
    defines = {"raw": ["-DFP_RAW_ONLY"], "both": [], "matrix": ["-DFP_MATRIX"]}
    for name in modes:
        lib = directory / (name + suffix)
        flags = defines[name]
        flags = [s.replace("-D", "/D") for s in flags] if os.name == "nt" else flags
        args = (
            [
                compiler,
                "/nologo",
                "/O2",
                "/W4",
                "/WX",
                "/LD",
                *flags,
                str(source),
                "/link",
                "/OUT:" + str(lib),
            ]
            if os.name == "nt"
            else [
                compiler,
                "-std=c11",
                "-O3",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-fPIC",
                "-shared",
                *flags,
                str(source),
                "-o",
                str(lib),
            ]
        )
        completed = subprocess.run(
            args,
            check=False,
            errors="replace",
            env=env,
            cwd=directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if completed.returncode:
            raise RuntimeError(completed.stdout)
        libraries.append(lib)
    return libraries


def binary_sizes(path):
    data = path.read_bytes()
    sizes = {"file_bytes": len(data)}
    if os.name == "nt":
        pe = struct.unpack_from("<I", data, 60)[0]
        number = struct.unpack_from("<H", data, pe + 6)[0]
        opt = struct.unpack_from("<H", data, pe + 20)[0]
        for j in range(number):
            start = pe + 24 + opt + 40 * j
            name = data[start : start + 8].rstrip(b"\0").decode()
            if name in (".text", ".rdata"):
                sizes[name] = struct.unpack_from("<I", data, start + 8)[0]
    return sizes


def check_native(tapes, lag):
    import _ctypes

    with tempfile.TemporaryDirectory() as temp:
        raw, both = compile_libraries(Path(temp))
        sizes = {"raw_only": binary_sizes(raw), "both": binary_sizes(both)}
        lib = ctypes.CDLL(str(both))
        try:
            pointer = np.ctypeslib.ndpointer(
                dtype=np.uint8, ndim=1, flags="C_CONTIGUOUS"
            )
            times = {}
            rng = np.random.default_rng(824)
            checks = [
                (rng.integers(2, size=3 * d + 11, dtype=np.uint8), d)
                for d in (1, 8, 33, 62, 63, 64, 91, 126, 127)
            ]
            for index, (data, d) in enumerate(
                [*checks, *[(data, lag) for data in tapes]]
            ):
                expected = errors(data, d)
                packed = np.packbits(data, bitorder="little")
                for name in ("raw", "coded"):
                    fn = getattr(lib, name + "_errors")
                    fn.argtypes = [pointer, ctypes.c_size_t, ctypes.c_uint32, pointer]
                    fn.restype = ctypes.c_uint64
                    width = d if name == "raw" else 57 * (d // 63) + d % 63
                    samples = []
                    for _ in range(3 if index == len(checks) + 2 else 1):
                        memory = np.zeros((width + 7) // 8, dtype=np.uint8)
                        start = perf_counter()
                        found = fn(packed, len(data), d, memory)
                        samples.append(round(1000 * (perf_counter() - start), 3))
                        assert found == expected[name], (d, name, found, expected[name])
                    if index == len(checks) + 2:
                        times[name] = samples
            return {
                "build": sizes,
                "report_kernel_ms_including_warmup": times,
                "matched_tapes": len(checks) + len(tapes),
            }
        finally:
            (_ctypes.FreeLibrary if os.name == "nt" else _ctypes.dlclose)(lib._handle)


def experiment(native):
    lag, best, second = identify()
    tapes = [
        stream(blocks, seed, lag)
        for blocks, seed in ((8, 2026112312), (4, 2026112313), (16, 2026112314))
    ]
    counts = [errors(tape, lag) for tape in tapes]
    lengths = [len(tape) - lag for tape in tapes]
    params = {
        "fair": F(1, 2),
        **{name: F(2 * v + 1, 2 * lengths[0] + 2) for name, v in counts[0].items()},
    }
    bits = charges(lag)
    risk = population(lag)
    observed = {}
    for price in PRICES:
        chosen, selection = compare(counts[1], lengths[1], params, bits, lag, price)
        _, report = compare(counts[2], lengths[2], params, bits, lag, price)
        public = {}
        for name, p in risk.items():
            bounds = binary_cost(p, params[name])
            public[name] = printed(
                tuple(x + price * bits[name] * SCALE / lag for x in bounds)
            )
        observed[str(price)] = {
            "selected": chosen,
            "selection": selection,
            "reporting": report,
            "population_if_lag_correct": public,
        }
    if native:
        print(json.dumps(check_native(tapes, lag), indent=2))
    return {
        "registration": "be51cdd",
        "true_lag": DELAY,
        "fitted_lag": lag,
        "training_windows": SAMPLES,
        "fitting_tokens": SAMPLES * (LIMIT + 1),
        "lag_comparisons": SAMPLES * (LIMIT // 2),
        "best_matches": best,
        "runner_up_matches": second,
        "scored_target_counts": lengths,
        "errors": counts,
        "fitted_error_probability": {k: str(v) for k, v in params.items()},
        "charged_bits": bits,
        "theoretical_error_if_lag_correct": {k: str(v) for k, v in risk.items()},
        "comparisons": observed,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native", action="store_true")
    parser.add_argument("--check", type=Path)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    result = experiment(args.native)
    if args.check:
        assert result == json.loads(args.check.read_text(encoding="utf-8"))
    output = json.dumps(result, indent=2) + "\n"
    if args.write:
        args.write.write_text(output, encoding="utf-8")
    elif not args.native:
        print(output, end="")
