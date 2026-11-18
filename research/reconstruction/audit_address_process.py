"""Enumerate every address, row, noise word and label in the temporal test."""
from collections import Counter
from fractions import Fraction as F
from itertools import product
from math import gcd, prod
import json


def clean_word(rows, path):
    # A row's low and high bits are its two physical source cells.
    return sum(((row >> ((path >> t) & 1)) & 1) << t for t, row in enumerate(rows))


def conditional_laws(clean, noise, path_weights):
    size = len(clean)
    d = size.bit_length()-1
    counts = [[0]*size for _ in path_weights]
    for errors in range(size):
        flips = errors.bit_count()
        multiplicity = noise.numerator**flips * (noise.denominator-noise.numerator)**(d-flips)
        for path, emitted in enumerate(clean):
            for table, masses in zip(counts, path_weights):
                table[emitted ^ errors] += masses[path]*multiplicity
    return counts


def product_testing_error(likelihood_bins, total, blocks):
    # Equal-prior optimum by summing the smaller joint probability at every
    # observed word. Grouping equal likelihood ratios is exact for products.
    overlap = 0
    for history in product(likelihood_bins, repeat=blocks):
        overlap += min(prod(pair[0] for pair in history), prod(pair[1] for pair in history))
    return F(overlap, 2*total**blocks)


def check(d, noise):
    size = 2**d
    theta = 1-2*noise
    even = [int(u.bit_count() % 2 == 0) for u in range(size)]
    odd = [1-v for v in even]
    asymmetric = [(2+u)**2 for u in range(size)]
    moments = [0]*size
    ratios = {}
    parity_mass = (size//2)*noise.denominator**d
    asymmetric_mass = sum(asymmetric)*noise.denominator**d
    distance_sum = useful = labels = 0
    for rows in product(range(4), repeat=d):
        clean = [clean_word(rows, path) for path in range(size)]
        positive, negative, empirical = conditional_laws(clean, noise, (even, odd, asymmetric))
        assert sum(positive) == sum(negative) == parity_mass and sum(empirical) == asymmetric_mass
        informative = all(row in (1, 2) for row in rows)
        useful += informative
        orientation = clean[0]
        for y, (a, b, mass) in enumerate(zip(positive, negative, empirical)):
            labels += 1
            if informative:
                sign = (-1)**((y ^ orientation).bit_count())
                assert F(a, parity_mass) == (1+sign*theta**d)/size
                assert F(b, parity_mass) == (1-sign*theta**d)/size
            else:
                assert a == b
            distance_sum += abs(a-b)
            if a+b:
                divisor = gcd(a, b)
                pair = ratios.setdefault((a//divisor, b//divisor), [0, 0])
                pair[0] += a
                pair[1] += b
            for u, candidate in enumerate(clean):
                moments[u] += mass*(-1)**((y ^ candidate).bit_count())
    total_rows = 4**d
    assert F(useful, total_rows) == F(1, size)
    tv = F(distance_sum, 2*total_rows*parity_mass)
    assert tv == theta**d/size
    reconstructed = [F(v, total_rows*asymmetric_mass)/theta**d for v in moments]
    assert reconstructed == [F(w, sum(asymmetric)) for w in asymmetric]
    for blocks in (range(5) if noise == 0 else (1,)):
        error = product_testing_error(ratios.values(), total_rows*parity_mass, blocks)
        if noise == 0:
            assert error == (1-F(1, size))**blocks/2
        else:
            assert error == (1-tv)/2
    return dict(depth=d, noise=str(noise), observational_tv=str(tv),
                complete_row_label_pairs=labels, acquired_path_probabilities=len(reconstructed))


def lifetime():
    # The first row (1,0) and first label 1 reveal address 0. Give the same
    # second row, compare every latent path under persistence versus redraw.
    def prediction(paths):
        posterior = Counter()
        for first, second in paths:
            if first == 0:
                posterior[int(second == 0)] += 1
        return F(posterior[1], posterior.total())
    assert prediction(((0, 0), (1, 1))) == 1
    assert prediction(product((0, 1), repeat=2)) == F(1, 2)


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("this audit requires assertions")
    lifetime()
    cases = [check(d, noise) for d, noise in product(range(1, 5), (F(0), F(1, 4)))]
    print(json.dumps(dict(temporal_controls=cases, lifetime_witness=["1", "1/2"]), indent=2))
