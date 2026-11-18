"""Finite exact controls for ROUTING.md. Run with Python 3.12, no dependencies."""
from collections import Counter, defaultdict
from fractions import Fraction as F
from functools import cache
from itertools import combinations, product
from math import comb, prod
import json
import struct


def binary_probability(live, row, cap):
    """One fresh, noiseless forecast. Only called addresses access the row."""
    paid = [(address, row(address)) for address in live[:cap]]
    unobserved = len(live) - len(paid)
    return F(2 * sum(bit for _, bit in paid) + unobserved, 2 * len(live)), paid


def frequencies(outcomes):
    """Conditional probability distribution for each observed transcript."""
    bins = defaultdict(Counter)
    for transcript, label, weight in outcomes:
        bins[transcript][label] += weight
    return {key: (pair[0], pair[1]) for key, pair in bins.items()}


def supported_word_likelihood(zeros, ones):
    """exp(-unnormalized optimal log loss), exact including empty branches."""
    total = zeros + ones
    if total == 0:
        return F(1)
    return F(zeros, total)**zeros * F(ones, total)**ones


def worlds(weights, noise, *, duplicate=False):
    """Joint population from latent identity, independent bits and noise."""
    for inputs in product((0, 1), repeat=len(weights)):
        row = inputs[:-1] + (inputs[-2],) if duplicate else inputs
        for address, weight in enumerate(weights):
            for flip, count in enumerate((noise.denominator-noise.numerator, noise.numerator)):
                if weight and count:
                    yield row, row[address] ^ flip, weight * count


def projected(bins, chosen):
    return frequencies((tuple(row[j] for j in chosen), label, count)
                       for row, label, count in bins)


def policy_optimum(population, size, cap):
    # This oracle sees only a posterior over observable rows and labels.
    # It can stop or read any remaining column at every different transcript.
    @cache
    def solve(partial):
        counts = [0, 0]
        for row, label, count in population:
            if all(bit < 0 or bit == row[j] for j, bit in enumerate(partial)):
                counts[label] += count
        best = supported_word_likelihood(*counts)
        if size - partial.count(-1) < cap:
            for j, bit in enumerate(partial):
                if bit < 0:
                    left = partial[:j] + (0,) + partial[j+1:]
                    right = partial[:j] + (1,) + partial[j+1:]
                    best = max(best, solve(left) * solve(right))
        return best
    return solve((-1,) * size)


def hard_reads():
    policies = 0
    posteriors = [(0, 4, 1), (4, 0, 1, 2)]
    for size in (2, 3, 4):
        posteriors.extend(product((1, 2, 3), repeat=size))
    for weights, noise in product(posteriors, (F(0), F(1, 4))):
        population = tuple(worlds(weights, noise))
        size, total = len(weights), sum(weights)
        order = sorted(range(size), key=weights.__getitem__, reverse=True)
        for cap in range(size+1):
            chosen = order[:cap]
            bins = projected(population, chosen)
            likelihood = F(1)
            for signs, (zeros, ones) in bins.items():
                deviation = sum(weights[j]*(2*bit-1) for j, bit in zip(chosen, signs))
                p = F(1, 2) + (1-2*noise)*F(deviation, 2*total)
                assert F(ones, zeros+ones) == p
                likelihood *= (1-p)**zeros * p**ones
            assert likelihood == policy_optimum(population, size, cap)
            policies += 1
    correlated = tuple(worlds((4, 3, 3), F(0), duplicate=True))
    single = [prod(supported_word_likelihood(*pair) for pair in projected(correlated, [j]).values())
              for j in range(3)]
    assert single[0] < single[1] == single[2] == policy_optimum(correlated, 3, 1)
    return dict(adaptive_policy_decisions=policies, dependent_columns_reverse_ranking=True)


def recodings():
    transcripts = 0
    for size, noise in product(range(2, 6), (F(0), F(1, 4))):
        for parity in (False, True):
            required = set(range(size)) if parity else {0}
            population = []
            for row in product((0, 1), repeat=size):
                coded = (sum(row) % 2,) + row[1:]
                assert (sum(coded) % 2,) + coded[1:] == row
                clean = row[0]
                for flip, count in enumerate((noise.denominator-noise.numerator, noise.numerator)):
                    population.append((coded if parity else row, clean ^ flip, count))
            for length in range(size+1):
                for chosen in combinations(range(size), length):
                    for zeros, ones in projected(population, chosen).values():
                        smaller = F(min(zeros, ones), zeros+ones)
                        assert smaller == (noise if required.issubset(chosen) else F(1, 2))
                        transcripts += 1
            for quarters in range(4*size+1):
                budget = F(quarters, 4)
                full_probability = min(F(1), budget/len(required))
                assert full_probability * len(required) <= budget
                assert full_probability == 1 or full_probability * len(required) == budget
    return dict(partial_transcripts=transcripts, direct_and_parity_curves_attained=True)


def stopped_risk(members, cap, size):
    weights = [int(j in members) for j in range(size)]
    chosen = members[:cap]
    bins = projected(worlds(weights, F(0)), chosen)
    distribution = Counter()
    for signs, (zero, one) in bins.items():
        p, paid = binary_probability(members, dict(zip(chosen, signs)).__getitem__, cap)
        assert p == F(one, zero+one) and len(paid) == len(chosen)
        distribution[p] += F(zero+one, len(members) * 2**size)
    return distribution


def noiseless_learning():
    training_worlds = forecasts = 0
    for size in (2, 3, 4):
        addresses = tuple(range(size))
        rows = range(2**size)
        fresh = {(s, k): stopped_risk(s, k, size)
                 for m in range(1, size+1) for s in combinations(addresses, m)
                 for k in range(size+1)}
        for n in range(4):
            horizon_mass = size * (2**size)**n
            correct_probability = (1 - (1-F(1, 2**n))**size) / (size*F(1, 2**n))
            wrong_probability = (1-correct_probability)/(size-1)
            reached, joint = Counter(), Counter()
            reads = 0
            for tape in product(rows, repeat=n):
                # Literal oracle groups complete worlds by the revealed labels.
                groups = defaultdict(list)
                for true in addresses:
                    observed = tuple((row >> true) & 1 for row in tape)
                    groups[observed].append(true)
                for observed, possible in groups.items():
                    live = addresses
                    for t, (row, label) in enumerate(zip(tape, observed)):
                        p, paid = binary_probability(live, lambda j: (row >> j) & 1, size)
                        prefix = [j for ys, js in groups.items() if ys[:t] == observed[:t] for j in js]
                        assert p == F(sum((row >> j) & 1 for j in prefix), len(prefix))
                        reads += len(paid)*len(possible)
                        forecasts += 1
                        live = tuple(j for j, bit in paid if bit == label)
                    assert live == tuple(possible)
                    reached[live] += len(possible)
                    for true, picked in product(possible, live):
                        joint[true, picked] += F(1, len(live))
            training_worlds += horizon_mass
            assert sum(reached.values()) == horizon_mass
            assert F(reads, horizon_mass) == n+2*(size-1)*(1-F(1, 2**n))
            if n == 1:
                assert len(reached) == 2**size-1
            sizes = Counter()
            for survivors, mass in reached.items():
                sizes[len(survivors)] += F(mass, horizon_mass)
            for m in range(1, size+1):
                prob = F(1, 2**n)
                assert sizes[m] == comb(size-1, m-1)*prob**(m-1)*(1-prob)**(size-m)
            for k in range(size+1):
                actual, predicted = Counter(), Counter()
                for members, mass in reached.items():
                    for p, share in fresh[members, k].items():
                        actual[p] += F(mass, horizon_mass)*share
                for m, share in sizes.items():
                    r = min(m, k)
                    for i in range(r+1):
                        predicted[F(1, 2)+F(2*i-r, 2*m)] += share*F(comb(r, i), 2**r)
                assert actual == predicted
            for k in range(1, size+1):
                groups = [(j,) for j in range(k-1)] + [addresses[k-1:]]
                for group in groups:
                    mass = sum(joint[true, picked] for true in addresses for picked in group)
                    assert mass == F(horizon_mass*len(group), size)
                    for j in group:
                        posterior = sum(joint[j, picked] for picked in group)/mass
                        assert posterior == wrong_probability+(correct_probability-wrong_probability)/len(group)
    return dict(training_worlds=training_worlds, causal_forecasts_checked=forecasts,
                complete_fresh_probability_laws=True, finite_data_message_posteriors=True)


def partitions(items):
    if not items:
        yield ()
        return
    first, *rest = items
    for groups in partitions(rest):
        yield ((first,),) + groups
        for j, group in enumerate(groups):
            yield groups[:j] + ((first,)+group,) + groups[j+1:]


def memory_frontier():
    tested = 0
    for size, eta in product(range(2, 8), (F(0), F(1, 4))):
        @cache
        def best_cell(cell):
            best = F(0)
            for action in range(size):
                bins = frequencies((seen, (seen if j == action else other) ^ flip, weight)
                    for j, seen, other, (flip, weight) in product(cell, (0, 1), (0, 1),
                        ((0, eta.denominator-eta.numerator), (1, eta.numerator))))
                best = max(best, prod(supported_word_likelihood(*z) for z in bins.values()))
            return best
        achieved, winning_sizes = {}, {}
        for partition in partitions(list(range(size))):
            likelihood = prod(best_cell(cell) for cell in partition)
            k = len(partition)
            shape = tuple(sorted(map(len, partition)))
            if likelihood > achieved.get(k, 0):
                achieved[k], winning_sizes[k] = likelihood, {shape}
            elif likelihood == achieved[k]:
                winning_sizes[k].add(shape)
            tested += 1
        for k, optimum in achieved.items():
            shape = (1,)*(k-1) + (size-k+1,)
            assert winning_sizes[k] == {shape}
            expected = F(1)
            for m in shape:
                p = F(1, 2) + (1-2*eta)/(2*m)
                total = 4*eta.denominator*m
                assert (total*p).denominator == 1
                expected *= p**int(total*p) * (1-p)**int(total*(1-p))
            assert optimum == expected
    return dict(partitions_with_noise_cases=tested, all_optimal_size_multisets_checked=True)


def likelihood_and_attacks():
    episodes = 0
    for rows in product(range(4), repeat=3):
        for labels in product((0, 1), repeat=3):
            weights = [1, 1]
            for row, label in zip(rows, labels):
                weights = [w*(3 if (row >> j) & 1 == label else 1) for j, w in enumerate(weights)]
            scores = [sum((2*((row >> j) & 1)-1)*(2*label-1) for row, label in zip(rows, labels))
                      for j in (0, 1)]
            assert F(weights[0], weights[1]) == F(3)**((scores[0]-scores[1])//2)
            counts = Counter()
            for j, errors in product((0, 1), product((0, 1), repeat=3)):
                emitted = tuple(((row >> j) & 1) ^ err for row, err in zip(rows, errors))
                if emitted == labels:
                    counts[j] += 3**(3-sum(errors))
            assert counts[0]*weights[1] == counts[1]*weights[0]
            episodes += 1
    tiny = F(1, 1+3**16)
    assert tiny < F(1, 2**25) and struct.unpack('e', struct.pack('e', float(tiny)))[0] == 0
    assert tiny*3**16 == 1-tiny

    # Arbitrary binary channels including nondeterministic postprocessing.
    pool_checks = 0
    grid = [F(k, 3) for k in range(4)]
    for w, x, z, left, right in product(grid, repeat=5):
        def transform(p):
            return (1-p)*left + p*right
        assert transform(w*x+(1-w)*z) == w*transform(x)+(1-w)*transform(z)
        pool_checks += 1
    assert (1 ^ 1) != 1  # constant-to-one channel versus XOR at (1,1)
    # At H=Y a positive independent encoding yields identical decoder rows.
    independent = ((F(1, 3), F(2, 3)),)*2
    for z in range(2):
        assert independent[1][z]/sum(row[z] for row in independent) == F(1, 2)
    # The divergent stopping gains compare exactly via the leaf likelihoods.
    agree = supported_word_likelihood(5, 1)
    disagree = supported_word_likelihood(3, 3)
    end_agree = supported_word_likelihood(3, 0) * supported_word_likelihood(2, 1)
    end_disagree = supported_word_likelihood(1, 2) * supported_word_likelihood(2, 1)
    assert end_agree / agree > end_disagree / disagree > 1
    return dict(noisy_histories=episodes, stochastic_pool_checks=pool_checks,
                exact_loser=str(tiny), binary16_loser=0, reversed_exact_posterior="1/2",
                independent_bottleneck_fixed_point=True, stopping_gains_differ=True)


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("this audit requires assertions")
    print(json.dumps(dict(recodings=recodings(), reading=hard_reads(),
                          learning=noiseless_learning(), memory=memory_frontier(),
                          attacks=likelihood_and_attacks()), indent=2))
