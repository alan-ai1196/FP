"""Compare the conflict-graph test with every binary completion of three rows and columns."""

from itertools import permutations, product


def graph(mask, values):
    rows = [(mask >> (3 * i)) & 7 for i in range(3)]
    bits = [(values >> (3 * i)) & 7 for i in range(3)]
    return sum(
        1 << k
        for k, (i, j) in enumerate(((0, 1), (0, 2), (1, 2)))
        if (bits[i] ^ bits[j]) & rows[i] & rows[j]
    )


def colors(edges):
    if edges == 0:
        return 1
    return 3 if edges == 7 else 2


def completions():
    full = range(512)
    counts = [len({(law >> (3 * i)) & 7 for i in range(3)}) for law in full]
    optimum = []
    for mask in full:
        direct = {}
        for law, n in zip(full, counts, strict=True):
            observed = law & mask
            direct[observed] = min(n, direct.get(observed, 4))
        optimum.append(direct)
    checked = candidates = 0
    pairs = ((0, 1), (0, 2), (1, 2))
    for mask, direct in enumerate(optimum):
        for law, n in direct.items():
            edges = graph(mask, law)
            assert colors(edges) == n
            checked += 1
            for u, v in product(range(3), repeat=2):
                bit = 1 << (3 * u + v)
                if mask & bit:
                    continue
                for outcome in range(2):
                    augmented = edges
                    for w in range(3):
                        other = 1 << (3 * w + v)
                        if mask & other and bool(law & other) != bool(outcome):
                            augmented |= 1 << pairs.index(tuple(sorted((u, w))))
                    assert colors(augmented) == optimum[mask | bit][law | outcome * bit]
                    candidates += 1
    assert checked == 3**9 and candidates == 18 * 3**8
    return checked, candidates


def nae_gadgets():
    for literal in product(range(2), repeat=3):
        can_extend = any(
            all(a != b for a, b in zip(literal, triangle, strict=True))
            for triangle in permutations(range(3))
        )
        assert can_extend == (len(set(literal)) == 2)
    for length in (2, 3):
        for palette in (2, 3):
            for a, b in product(range(palette), repeat=2):
                ok = False
                for middle in product(range(palette), repeat=length - 1):
                    path = (a, *middle, b)
                    if all(path[i] != path[i + 1] for i in range(length)):
                        ok = True
                        break
                assert ok == (palette == 3 or ((a != b) == bool(length % 2)))


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("verification requires assertions")
    print("partial matrices and candidate missing laws", completions())
    nae_gadgets()
    print("clause and parity path checks passed")
