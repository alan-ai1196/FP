from __future__ import annotations
from pathlib import Path
import os

VOCAB=50257
HORIZON=511
SEEDS=(1337,2027,3141)
SNAPSHOT_MINUTES=(7.5,15,30,60,120)
DEFAULT_RUN_SECONDS=7200.0

# One compiler evidence bank consists of two contiguous train-only halves. The
# first half solves/certifies as much of the finite first-order response cone as
# the numerical compile budget permits. The second half always continues active
# positive masses and, when present, compares candidate+value against value-only.
DISCOVERY_EVIDENCE_TOKENS=131072
CONFIRM_EVIDENCE_TOKENS=131072
EVIDENCE_TOKENS=DISCOVERY_EVIDENCE_TOKENS+CONFIRM_EVIDENCE_TOKENS
# Numerical effort budget for adaptive global pricing. Each pricing call returns
# a batch of exact KKT violations; the restricted cone is re-profiled before the
# second call. Hitting this cap returns an unresolved cone gap and never becomes
# model width/rank/support. The first real R4 run showed that one-column-at-a-time
# rescanning wasted the remaining top-k oracle output; R4.2 batches it instead.
CONE_SCAN_BUDGET=2
# Number of globally highest violated columns returned per pricing call. This is
# numerical batching only; it neither caps persistent support nor closes an
# unresolved cone. Two residual-adaptive batches keep confirmation dimension near
# the predecessor while removing repeated full-grammar scans.
CONE_PRICING_BATCH=16

NATIVE_CHUNK=65536
VALIDATION_WINDOWS=4096
HARD_VRAM_GIB=22.0

# Physical D2H cap for exact incumbent response telemetry. If the active program
# exceeds it, the compiler marks quotient geometry unresolved. It never rotates
# a subset and calls that quotient complete.
MAX_COMPILER_NODES=64

# Physical transaction constants. These are fixed data/certification budgets,
# not architecture hyperparameter sweeps.
TRANSACTION_EVAL_TOKENS=131072
TRANSACTION_EVAL_BLOCKS=4
TRANSACTION_SYSTEM_SECONDS=1.0
MAX_EXCLUSIVE_TRANSACTION_FRACTION=0.05

# CPU placement is compiler-throughput first because the predecessor run measured the CPU solver
# as the active acquisition bottleneck.  Layouts statistically/physically near
# the fastest compiler rate are tie-broken by ordinary GPU throughput.  This
# margin is a timing-equivalence tolerance, never a task-value criterion.
CPU_LAYOUT_NEAR_BEST_FRACTION=0.98


def find_data_root(pkg_root:Path):
    cand=[]
    e=os.environ.get('FP_DATA_ROOT')
    if e:cand.append(Path(e))
    cand += [pkg_root/'data',pkg_root.parent/'data',Path(r'F:\experiment\FP_Scaling_Trial_1R_RTX3090_WindowsGlobal_OneClick\data'),Path(r'F:\experiment\FP\data')]
    for p in cand:
        if (p/'train.bin').is_file() and (p/'val.bin').is_file():return p
    raise FileNotFoundError('train.bin/val.bin not found. Set FP_DATA_ROOT to the directory containing both files.')
