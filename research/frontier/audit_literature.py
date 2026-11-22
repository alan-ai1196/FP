"""Exact finite instances of the two November 23 literature transfers."""

from fractions import Fraction as F
from itertools import combinations, permutations, product
from math import comb, factorial, log
from pathlib import Path
import argparse


def compositions(m, parts):
    if parts == 1:
        yield (m,)
        return
    for first in range(m + 1):
        for rest in compositions(m - first, parts - 1):
            yield first, *rest


def row_checks():
    exact_cases = 0
    for d, m in product((1, 2, 3), range(1, 6)):
        states = list(compositions(m, d + 1))
        for stored_shift in product(range(-2, 3), repeat=d):
            delta = (*stored_shift, -sum(stored_shift))
            donor = sum(max(-change, 0) for change in delta)
            good = sum(all(n + k >= 0 for n, k in zip(x, delta)) for x in states)
            assert good == (comb(m - donor + d, d) if donor <= m else 0)
            exact_cases += 1
    states = list(compositions(4, 3))
    profiles = lambda queries: {tuple(state[i] >= h for i, h in queries) for state in states}
    counts = [len(profiles(q)) for q in ([(0, 2)], [(i, 1) for i in range(3)],
                                          list(product(range(3), range(1, 5))))]
    assert counts == [2, 7, 15]
    assert F(sum(x[0] >= 2 for x in states), len(states)) == F(2, 5)
    simplex = lambda d: F((d + 1) * d**d, factorial(d))
    ratio = simplex(10)**2 / simplex(20)
    assert ratio == F(121 * comb(20, 10), 21 * 2**20) > 1
    assert 1 < comb(20, 10) < 2**20  # equal-volume dilation is between 1/2 and 1
    return exact_cases, counts, ratio


def walsh(values):
    data = list(values)
    half = 1
    while half < len(data):
        for start in range(0, len(data), 2 * half):
            for j in range(start, start + half):
                a, b = data[j], data[j + half]
                data[j], data[j + half] = a + b, a - b
        half *= 2
    return data


def mask_checks():
    edges = list(combinations(range(4), 2))
    m = len(edges)
    perms = [[edges.index(tuple(sorted((vertex[i], vertex[j])))) for i,j in edges]
             for vertex in permutations(range(4))]
    def orbit(graph):
        return min(sum(1 << target for i, target in enumerate(perm) if graph & (1 << i)) for perm in perms)
    orbits = [orbit(x) for x in range(1 << m)]
    orbit_id = {g:i for i, g in enumerate(sorted(set(orbits)))}
    trials = 0
    for levels in product((0,1), repeat=len(orbit_id)):
        spectrum = walsh([levels[orbit_id[g]] for g in orbits])
        energy = [w*w for w in spectrum]
        energy[0] = 0
        total = sum(energy)
        for mask in range(1 << m):
            captured = sum(v for s, v in enumerate(energy) if s & mask == s)
            assert m * captured <= mask.bit_count() * total
            trials += 1
    # On six vertices the 20 triple coordinates form ten complementary pairs.
    # Compute the query-depth distribution independently by following the decision tree.
    r = 3
    m = comb(2*r, r)
    def residual(pairs, mate, budget):
        if not pairs:
            return F(0)
        if not budget:
            no_pair = F(3,4)**(pairs - int(mate)) * (F(1,2) if mate else 1)
            return no_pair * (1 - no_pair)
        if mate:
            return residual(pairs-1, False, budget-1) / 2
        return (residual(pairs-1, False, budget-1) + residual(pairs, True, budget-1)) / 2
    variance = F(3,4)**(m//2) * (1 - F(3,4)**(m//2))
    adaptive = residual(m//2, False, m-1)
    assert adaptive == F(1,2**(m+1)) < variance / m
    return trials, m, adaptive


def entropy(p):
    return -sum(x * log(x) for x in (p,1-p) if x)


def erased_token_check():
    # Explicit Bayes posterior of a noisy OR, conditioning on every single-coordinate erasure.
    n, p, eta = 3, F(1,3), F(1,8)
    worlds = [(v, p**sum(v)*(1-p)**(n-sum(v))) for v in product((0,1), repeat=n)]
    actual, pivotal = 0., F(0)
    for erased in range(n):
        groups = {}
        for state, mass in worlds:
            seen = state[:erased] + state[erased+1:]
            total, positives = groups.get(seen, (0,0))
            groups[seen] = (total+mass, positives+mass*int(any(state)))
        actual += sum(mass*(entropy(eta+(1-2*eta)*positives/mass)-entropy(eta))
                      for mass, positives in groups.values())
        pivotal += sum(mass for mass, positives in groups.values() if 0 < positives < mass)
    assert pivotal == n*(1-p)**(n-1)
    formula = float(pivotal)*(entropy(eta+(1-2*eta)*p)-entropy(eta))
    assert abs(actual-formula) < 1e-14
    return pivotal, actual


def hamming_checks():
    n = 7
    # Positions are numbered 1..7. The three syndrome columns at the check
    # positions are the coordinate vectors. Append them to each data position.
    basis = []
    for j in (3, 5, 6, 7):
        word = 1 << (j-1)
        for check in (1, 2, 4):
            if j & check:
                word |= 1 << (check-1)
        basis.append(word)
    assert [word.bit_count() for word in basis] == [3, 3, 3, 4]
    covered_counts = []
    for b in range(5):
        covered = {}
        for mask in range(1 << b):
            codeword = 0
            for i in range(b):
                if mask & (1 << i):
                    codeword ^= basis[i]
            for error in [0] + [1 << j for j in range(n)]:
                s = codeword ^ error
                assert s not in covered
                covered[s] = (mask, error)
        assert len(covered) == 8 * 2**b
        covered_counts.append(len(covered))
        stored = [sum(((x & w).bit_count() % 2) << i for i,w in enumerate(basis[:b]))
                  for x in range(1 << n)]
        for s in range(1 << n):
            if s in covered:
                mask, error = covered[s]
                for x, z in enumerate(stored):
                    assert ((mask & z).bit_count() + (x & error).bit_count()) % 2 == (s & x).bit_count() % 2
            else:
                # Every possible one-probe address, separately within each synopsis
                # cell, yields an exactly balanced target on every nonempty leaf.
                for j in range(n):
                    imbalance = [0] * (2 << b)
                    for x,z in enumerate(stored):
                        leaf = 2*z + ((x >> j) & 1)
                        imbalance[leaf] += (-1)**((s & x).bit_count() % 2)
                    assert not any(imbalance)
    return covered_counts


def alphatensor(path):
    import numpy as np
    with np.load(path, allow_pickle=False) as source:
        terms = source['4,4,4']
    assert terms.shape == (3,16,47) and np.isin(terms, (0,1)).all()
    u, v, w = terms.astype(np.int64)
    recovered = np.einsum('it,jt,kt->ijk', u, v, w)
    target = np.zeros_like(recovered)
    for i,j,k in product(range(4), repeat=3):
        target[4*i+j,4*j+k,4*k+i] = 1  # stored output factor is transposed
    residual = recovered - target
    assert not np.any(residual % 2)
    assert np.count_nonzero(residual) == 465 and np.abs(residual).max() == 8
    xors = sum(np.maximum(x.sum(axis=0)-1,0).sum() for x in (u,v))
    xors += np.maximum(w.sum(axis=1)-1,0).sum()
    assert int(xors) == 340
    print('AlphaTensor: 4096 field coefficients correct, 465 integer mismatches, 47 AND and 340 unshared XOR.')


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--alphatensor', type=Path, help='Also check the published rank-47 F2 factor archive')
    options = cli.parse_args()
    cases, responses, ratio = row_checks()
    trials, edges, adaptive = mask_checks()
    pivotal, slope = erased_token_check()
    covered = hamming_checks()
    print(f'{cases} lattice shifts. Answer profiles {responses}. Convex volume ratio {ratio}.')
    print(f'{trials} invariant function/mask checks. Adaptive residual on {edges} edges {adaptive}.')
    print(f'Noisy OR erasure tangent, pivotal sum {pivotal}, {slope:.12f} nats.')
    print(f'Seven-bit parity queries determined for 0 through 4 stored bits: {covered} of 128.')
    if options.alphatensor:
        alphatensor(options.alphatensor)
