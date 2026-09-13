"""RN-3 fixed data support; hidden bits are available only to data and scoring."""
from itertools import product
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'experiments/relation_noise'))
from model import context, counts_from_training, posterior, score, unseen_pairs
from model import data as diagnostic_data


def diagnostic_cases():
    return ((8, 'disconnected-a', 0), (8, 'disconnected-b', 0))


def new_cases():
    return tuple((n, 'iid-c'+str(c), seed) for c, seeds in ((2, (8, 9)), (4, (10, 11)))
                 for n in (8, 16) for seed in seeds)


def tasks():
    return (tuple(('FP', case) for case in diagnostic_cases())
            + tuple((kind, case) for case in new_cases() for kind in ('FP', 'posterior')))


def support(case):
    n, law, seed = case
    assert case in diagnostic_cases()+new_cases()
    c = 2 if law.startswith('disconnected') else int(law.removeprefix('iid-c'))
    assert n % c == 0
    width = n//c
    return tuple((i, i+1) for i in range(n-1) if (i+1) % width)


def data(case):
    if case in diagnostic_cases():
        result = diagnostic_data(case)
        assert result[1] == support(case)
        return result
    n, law, seed = case
    edges = support(case)
    hidden_rng = random.Random(2026091300+100*n+seed)
    hidden = tuple(hidden_rng.randrange(2) for _ in range(n))
    noise = random.Random(2026091400+100*n+seed)
    train = tuple((i, j, (hidden[i]^hidden[j]) ^ int(noise.randrange(10) == 0))
                  for i, j in edges for _ in range(10))
    pairs = list(product(range(n), repeat=2))
    random.Random(2026091600+100*n+seed).shuffle(pairs)
    noise = random.Random(2026091500+100*n+seed)
    evaluation = tuple((i, j, (hidden[i]^hidden[j]) ^ int(noise.randrange(10) == 0)) for i, j in pairs)
    return hidden, edges, train, evaluation
