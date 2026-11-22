"""Exhaust the residual task sets of F_2^4 and check the sharp unseen-task bounds."""

from collections import Counter
from itertools import combinations
from math import comb, fsum, isclose, log, log1p

DIMENSION = 4
SIZE = 1 << DIMENSION
NOISE = 1 / 8


def entropy(probability):
    if probability == 0 or probability == 1:
        return 0.0
    return -probability * log(probability) - (1 - probability) * log1p(-probability)


def sign_histogram(residual, negative_characters):
    size = residual.bit_count()
    return tuple(
        sorted(
            abs(size - 2 * (residual & row).bit_count()) for row in negative_characters
        )
    )


def affine_orbit(initial):
    # Translation, adjacent coordinate permutations and one elementary shear
    # generate the affine group. Act on the subsets, independently of their spectra.
    maps = [[word ^ 1 for word in range(SIZE)]]
    for i in range(DIMENSION - 1):
        swap = []
        for word in range(SIZE):
            differing = ((word >> i) ^ (word >> (i + 1))) & 1
            swap.append(word ^ (differing * (3 << i)))
        maps.append(swap)
    maps.append([word ^ ((word >> 1) & 1) for word in range(SIZE)])
    # Half-word tables keep the finite enumeration fast.
    maps_by_byte = []
    for perm in maps:
        low = [
            sum(1 << perm[i] for i in range(8) if byte & (1 << i))
            for byte in range(256)
        ]
        high = [
            sum(1 << perm[i + 8] for i in range(8) if byte & (1 << i))
            for byte in range(256)
        ]
        maps_by_byte.append((low, high))
    seen = {initial}
    frontier = [initial]
    while frontier:
        subset = frontier.pop()
        for low, high in maps_by_byte:
            image = low[subset & 255] | high[subset >> 8]
            if image not in seen:
                seen.add(image)
                frontier.append(image)
    return seen


def mean_over_bijections(r):
    # Input zero has a deterministic clean bit. Every other input balances all keys.
    numerator = fsum(
        comb(SIZE // 2, j)
        * comb(SIZE // 2, r - j)
        * entropy(NOISE + (1 - 2 * NOISE) * j / r)
        for j in range(max(0, r - SIZE // 2), min(r, SIZE // 2) + 1)
    )
    return (1 - 1 / SIZE) * (numerator / comb(SIZE, r) - entropy(NOISE))


def audit():
    negative = [
        sum(1 << mask for mask in range(SIZE) if (mask & word).bit_count() % 2)
        for word in range(SIZE)
    ]
    total = 0
    print(
        "r  subsets  affine images minimizing loss   min excess   mean excess    max excess"
    )
    for r in range(1, SIZE + 1):
        initial = (1 << r) - 1
        initial_spectrum = sign_histogram(initial, negative)
        orbit = affine_orbit(initial)
        frequencies = Counter()
        for points in combinations(range(SIZE), r):
            residual = sum(1 << point for point in points)
            spectrum = sign_histogram(residual, negative)
            assert sum(a * a for a in spectrum) == SIZE * r
            assert (spectrum == initial_spectrum) == (residual in orbit)
            frequencies[spectrum] += 1
        deficits = {}
        for spectrum in frequencies:
            for order in range(2, 18, 2):
                assert sum(s**order for s in spectrum) <= sum(
                    s**order for s in initial_spectrum
                )
            deficits[spectrum] = fsum(
                entropy((1 + (1 - 2 * NOISE) * s / r) / 2) for s in spectrum
            ) / SIZE - entropy(NOISE)
        minimum = min(deficits.values())
        assert deficits[initial_spectrum] == minimum
        assert all(
            value > minimum + 1e-12
            for spectrum, value in deficits.items()
            if spectrum != initial_spectrum
        )
        coarse_bound = (1 - 1 / r) * (log(2) - entropy(NOISE))
        assert minimum >= coarse_bound - 1e-14
        assert isclose(minimum, coarse_bound, abs_tol=1e-14) == (r & (r - 1) == 0)
        cases = sum(frequencies.values())
        assert cases == comb(SIZE, r)
        mean = fsum(frequencies[key] * value for key, value in deficits.items()) / cases
        assert isclose(mean, mean_over_bijections(r), abs_tol=5e-15)
        if r <= DIMENSION + 1:
            independent = 1 | sum(1 << (1 << i) for i in range(r - 1))
            assert deficits[sign_histogram(independent, negative)] == max(
                deficits.values()
            )
        print(
            f"{r:2} {cases:8} {len(orbit):28}  {minimum:.9f}  {mean:.9f}  {max(deficits.values()):.9f}"
        )
        total += cases
    assert total == 65535


if __name__ == "__main__":
    audit()
