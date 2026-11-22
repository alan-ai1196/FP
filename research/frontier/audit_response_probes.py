"""Exact observation-design checks for learning the response operation."""

from fractions import Fraction
from itertools import combinations
from math import comb, prod


def signatures(columns, size, gate):
    def bit(task, probe):
        overlap = task & probe
        return overlap.bit_count() % 2 if gate == "xor" else int(bool(overlap))

    return {tuple(bit(task, column) for column in columns) for task in range(size)}


def generated_space(points):
    space = {0}
    for point in points:
        space.update({s ^ point for s in space})
    return space


def essential(gate):
    bit = lambda i: (gate >> i) & 1
    return (bit(0) != bit(2) or bit(1) != bit(3)) and (
        bit(0) != bit(1) or bit(2) != bit(3)
    )


def closed_essential(rows):
    gates = []
    for gate in range(16):
        if essential(gate) and all(
            tuple((gate >> (2 * a + b)) & 1 for a, b in zip(x, y)) in rows
            for x in rows
            for y in rows
        ):
            gates.append(gate)
    return gates


def exhaustive_designs():
    size = 8
    singles = {1, 2, 4}
    counts = {
        "subsets": 0,
        "xor_separating": 0,
        "or_separating": 0,
        "xor_with_even_witness": 0,
        "or_with_joint_witness": 0,
    }
    for m in range(9):
        for columns in combinations(range(size), m):
            counts["subsets"] += 1
            xor = signatures(columns, size, "xor")
            disjunction = signatures(columns, size, "or")
            rank_full = len(generated_space(columns)) == size
            assert (len(xor) == size) == rank_full
            assert (len(disjunction) == size) == singles.issubset(columns)
            counts["xor_separating"] += int(rank_full)
            counts["or_separating"] += int(singles.issubset(columns))
            # Check all independent choices of pivot columns for the XOR certificate.
            pivot_witnesses = []
            for basis in combinations(columns, 3):
                if len(generated_space(basis)) == size:
                    even = {a ^ b for a, b in combinations(basis, 2)}
                    pivot_witnesses.append(bool(even.intersection(columns)))
            if any(pivot_witnesses):
                assert closed_essential(xor) == [6]
                counts["xor_with_even_witness"] += 1
            if singles.issubset(columns) and any(x.bit_count() >= 2 for x in columns):
                assert closed_essential(disjunction) == [14]
                counts["or_with_joint_witness"] += 1
    assert counts["subsets"] == 256
    return counts


def law_probabilities(d, m):
    size = 1 << d
    # Exact probability of a spanning binary d-by-m matrix.
    xor = (
        prod(Fraction((1 << m) - (1 << i), 1 << m) for i in range(d))
        if m >= d
        else Fraction(0)
    )
    # Inclusion-exclusion over missing singleton inputs.
    disjunction = sum(
        (-1) ** j * comb(d, j) * Fraction(size - j, size) ** m for j in range(d + 1)
    )
    return xor, disjunction


def expected_columns(d):
    n = 1 << d
    xor = sum(Fraction(n, n - (1 << j)) for j in range(d))
    disjunction = n * sum(Fraction(1, j) for j in range(1, d + 1))
    return xor, disjunction


if __name__ == "__main__":
    print(exhaustive_designs())
    # Enumerate all ordered short streams separately from the inclusion-exclusion
    # and rank formulas, counting exact repeated columns and the zero column.
    from itertools import product

    for m in range(6):
        sequences = list(product(range(4), repeat=m))
        x = sum(len(generated_space(seq)) == 4 for seq in sequences)
        o = sum({1, 2}.issubset(seq) for seq in sequences)
        assert (
            Fraction(x, len(sequences)),
            Fraction(o, len(sequences)),
        ) == law_probabilities(2, m)
    print(
        "Seven-bit expected columns for separation",
        *(float(v) for v in expected_columns(7)),
    )
    for m in (8, 16, 32, 128, 256, 512):
        print(
            "columns and separation probabilities",
            m,
            *(float(v) for v in law_probabilities(7, m)),
        )
