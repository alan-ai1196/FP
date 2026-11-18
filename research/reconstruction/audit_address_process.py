"""Enumerate every address, row, noise word and label in the temporal test."""
from collections import Counter
from fractions import Fraction as F
from itertools import combinations, product
from math import ceil, comb, gcd, prod
from pathlib import Path
import json
import sys


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


def general_binary_law():
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'src/reference_compiler'))
    from fp_reference.numerics import log_enclosure
    from audit_routing import frequencies, supported_word_likelihood
    log2 = log_enclosure(F(2), terms=14, bit_limit=32768)
    thresholds = []
    for a, b in combinations(range(9), 2):
        lower = upper = F(0)
        for x, y in ((a, b), (8-a, 8-b)):
            for c in (x, y):
                if c:
                    ratio = log_enclosure(F(2*c, x+y), terms=14, bit_limit=32768)
                    lower += F(c, 16)*ratio.lower
                    upper += F(c, 16)*ratio.upper
        assert lower > 0
        # Direct optimum over all binomial observations at each sample size.
        for n in range(1, ceil(2*log2.upper**2/lower)+1):
            overlap = sum(comb(n, k)*min(a**k*(8-a)**(n-k), b**k*(8-b)**(n-k))
                          for k in range(n+1))
            if 2*overlap <= 8**n:
                break
        else:
            raise AssertionError("upper sample bound violated")
        assert 16*n*lower >= 1 and n <= ceil(2*log2.lower**2/upper)
        thresholds.append(n)
    both = []
    for sensor in ("A", "B"):
        first, second = [], []
        for target, world, error in product(range(2), repeat=3):
            count = 1 if error else 3
            observation = target ^ (error if sensor == "A" else world)
            first.append((observation, target, count))
            second.append(((observation, target), world, count))
        both.append([prod(supported_word_likelihood(*v) for v in frequencies(events).values())
                     for events in (first, second)])
    assert both[0][0] > both[1][0] and prod(both[0]) < prod(both[1])
    return dict(binary_pairs=len(thresholds), optimum_sample_range=[min(thresholds), max(thresholds)],
                early_read_decision_reversed_by_future_score=True)


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("this audit requires assertions")
    lifetime()
    cases = [check(d, noise) for d, noise in product(range(1, 5), (F(0), F(1, 4)))]
    print(json.dumps(dict(temporal_controls=cases, lifetime_witness=["1", "1/2"],
                          general_binary=general_binary_law()), indent=2))
