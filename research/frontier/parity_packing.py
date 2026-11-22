"""Enumerate population-optimal one-generator updates for the seven-bit access problem."""

from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache

M = 7
SIZE = 1 << M
ERRORS = (0, *(1 << i for i in range(M)))
BALL = [sum(1 << (v ^ e) for e in ERRORS) for v in range(SIZE)]


@cache
def coverage(space):
    bits = 0
    for word in space:
        bits |= BALL[word]
    return bits.bit_count()


def extend(space, word):
    return tuple(sorted((*space, *(v ^ word for v in space))))


@cache
def best(space):
    seen = set(space)
    candidates = []
    for word in range(1, SIZE):
        if word in seen:
            continue
        enlarged = extend(space, word)
        seen.update(enlarged)
        candidates.append(enlarged)
    optimum = max(map(coverage, candidates))
    return tuple(c for c in candidates if coverage(c) == optimum)


def path(words):
    space = (0,)
    for word in words:
        enlarged = extend(space, word)
        assert enlarged in best(space)
        space = enlarged
    return space


def audit():
    layer = {(0,): Fraction(1)}
    counts = [1]
    third = None
    for rank in range(1, 5):
        following = defaultdict(Fraction)
        for space, probability in layer.items():
            children = best(space)
            for child in children:
                following[child] += probability / len(children)
        layer = following
        assert sum(layer.values()) == 1
        counts.append(len(layer))
        if rank == 3:
            third = tuple(layer)
    assert counts == [1, 99, 1225, 1605, 870]
    extension_types = Counter((coverage(best(c)[0]), len(best(c))) for c in third)
    assert extension_types == {(112, 4):1260, (128, 1):240, (128, 2):105}
    endpoints = Counter(coverage(c) for c in layer)
    success = sum(p for c, p in layer.items() if coverage(c) == SIZE)
    assert endpoints == {112:840, 128:30} and success == Fraction(416, 2299)
    trap = path((7, 25, 98))
    optimum = path((7, 25, 42, 75))
    assert (coverage(trap), coverage(best(trap)[0]), coverage(optimum)) == (64,112,128)
    print('Reachable subspaces by dimension:', counts)
    print('Dimension-three types (best coverage, maximizing extensions):', dict(sorted(extension_types.items())))
    print('Endpoint coverage:', dict(sorted(endpoints.items())))
    print('Perfect-coverage probability with uniform choices among immediate maximizers:', success)


if __name__ == '__main__':
    audit()
