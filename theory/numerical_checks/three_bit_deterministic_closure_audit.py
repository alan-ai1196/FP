"""Exact three-bit deterministic conditional closure audit (standard library only).

Run with --write to persist the deterministic minimal evidence. The witnesses
are proposals, not authority: every row is checked by independent Laurent and
actual rational SUM/PRODUCT execution. No SMT/LP/optimizer is used by this audit.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from itertools import permutations, product
from math import comb
import json
from pathlib import Path
from random import Random

BASE_COMMIT = "388251d8b05de10536bdf650e4c1a56a2bd46a4b"
X = tuple(product((0, 1), repeat=3))
# A None slot is an absent edge; integer w means coefficient epsilon**w.
# Feature order: x0,x1,y0,y1,z0,z1, then earlier scalar PRODUCTs.
# Record: (PRODUCT parent pairs, two excess readouts, expected symmetry orbit).
WITNESSES = {0: ([], [[None, None, None, None, -1, -1], [None, None, None, None, None, None]], 2),
 1: ([], [[None, -2, None, -2, None, -2], [-1, None, None, None, None, None]], 16),
 3: ([], [[None, -2, None, -2, None, None], [None, None, -1, None, None, None]], 24),
 6: ([[[None, None, -1, None, None, -1], [None, None, None, -1, -1, None]]],
     [[None, -1, None, None, None, None, 0], [-1, None, None, None, None, None, None]],
     24),
 7: ([], [[-1, -3, None, None, None, None], [None, None, -2, None, -2, None]], 48),
 15: ([], [[None, -1, None, None, None, None], [-1, None, None, None, None, None]], 6),
 22: ([[[None, 0, None, None, None, -2], [None, 0, None, -2, None, None]]],
      [[None, None, -1, None, None, None, -1], [None, -2, None, -2, None, -2, None]],
      16),
 23: ([[[-1, None, None, None, 0, None], [None, None, -1, None, 1, None]]],
      [[None, -1, None, None, None, -1, None], [None, None, None, None, None, None, -1]],
      8),
 24: ([[[-1, None, None, -1, None, 0], [None, 0, -1, None, -1, None]]],
      [[None, None, None, None, None, None, 0], [-1, None, None, None, -1, None, None]],
      8),
 25: ([[[None, None, None, -1, None, -1], [None, 0, -1, None, -1, None]]],
      [[None, None, None, None, None, None, 0], [-1, None, None, None, -1, None, None]],
      48),
 27: ([[[None, None, -1, None, None, -1], [-1, None, None, None, -1, None]]],
      [[None, -1, None, None, -1, None, None], [None, None, None, None, None, None, 0]],
      24),
 30: ([[[None, None, None, -1, None, -1], [-2, None, None, None, None, None]]],
      [[-2, None, None, -1, None, -2, None], [None, None, -1, None, None, None, 0]],
      24),
 60: ([[[None, 0, None, -1, None, None], [-1, None, -1, None, None, None]]],
      [[-1, None, None, -1, None, None, None], [None, None, None, None, None, None, 0]],
      6),
 105: ([[[None, 0, None, 0, None, None], [0, None, 0, None, None, None]],
        [[None, None, None, None, None, None, 0], [None, None, None, None, None, 0, None]]],
       [[None, None, None, None, None, -1, -2, None], [None, None, None, None, -1, None, None, -3]],
       2)}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checked_shape(certificate):
    nodes, heads, _ = certificate
    require(len(nodes) <= 2 and len(heads) == 2, "wrong node/head count")
    for j, parents in enumerate(nodes):
        require(len(parents) == 2, "PRODUCT is binary")
        for weights in parents:
            require(len(weights) == 6+j, "parent uses unavailable feature")
            require(any(w is not None for w in weights), "empty PRODUCT parent")
    for weights in heads:
        require(len(weights) == 6+len(nodes), "wrong readout length")
    for weights in [w for node in nodes for w in node]+list(heads):
        require(all(w is None or type(w) is int for w in weights),
                "only integer orders or absent edges are accepted")


def plus(polys):
    out = {}
    for poly in polys:
        for degree, coefficient in poly.items():
            out[degree] = out.get(degree, 0)+coefficient
    return out


def times(left, right):
    return plus({a+b: c*d} for a, c in left.items() for b, d in right.items())


def laurent_masses(certificate, x):
    nodes, heads, _ = certificate
    values = [{0: 1} if x[i] == b else {} for i in range(3) for b in (0, 1)]
    def weighted(weights):
        return plus({a+w: c for a, c in v.items()}
                    for w, v in zip(weights, values) if w is not None)
    for left, right in nodes:
        values.append(times(weighted(left), weighted(right)))
    return [plus(({0: 1}, weighted(head))) for head in heads]


def minimum_orders(certificate, x):
    # Separate evaluator: it never expands or reads a Laurent polynomial.
    values = [0 if x[i] == b else None for i in range(3) for b in (0, 1)]
    def weighted(weights):
        active = [a+w for a, w in zip(values, weights) if a is not None and w is not None]
        return min(active) if active else None
    for left, right in certificate[0]:
        a, b = weighted(left), weighted(right)
        values.append(None if a is None or b is None else a+b)
    return [min(0, v) if v is not None else 0
            for v in (weighted(head) for head in certificate[1])]


def verify(mask, certificate):
    try:
        require(type(mask) is int and 0 <= mask < 256, "bad external target")
        checked_shape(certificate)
        for i, x in enumerate(X):
            masses = laurent_masses(certificate, x)
            orders = [min(m) for m in masses]
            require(orders == minimum_orders(certificate, x), "inconsistent order evaluators")
            correct = (mask >> i) & 1
            require(orders[1-correct] >= orders[correct]+1, "wrong support/leading order")
        return True
    except (ValueError, TypeError, IndexError, KeyError):
        return False


def native_masses(certificate, x, epsilon):
    values = [F(x[i] == b) for i in range(3) for b in (0, 1)]
    def weighted(weights):
        return sum((epsilon**w*v for w, v in zip(weights, values) if w is not None), F(0))
    for left, right in certificate[0]:
        values.append(weighted(left)*weighted(right))
    return [1+weighted(head) for head in certificate[1]]


def alphabet_masses(certificate, x, k):
    # Execute the expanded graph, not a coefficient-count estimate.
    values = [F(x[i] == b) for i in range(3) for b in (0, 1)]
    sums, products = 1, 0
    one = values[0]+values[1]
    def weighted(weights, base=None):
        nonlocal sums
        terms = [] if base is None else [base]
        for w, v in zip(weights, values):
            if w is None:
                continue
            for _ in range(abs(w)*k):
                v *= F(1, 2) if w > 0 else 2
                sums += 1
            terms.append(v)
        require(bool(terms), "expanded empty sum")
        sums += len(terms)-1
        return sum(terms, F(0))
    for left, right in certificate[0]:
        a, b = weighted(left), weighted(right)
        values.append(a*b)
        products += 1
    masses = [weighted(head, one) for head in certificate[1]]
    return masses, sums, products


def resource_constants(certificate):
    parents = [w for node in certificate[0] for w in node]
    heads = certificate[1]
    weight_work = sum(abs(w) for row in parents+list(heads) for w in row if w is not None)
    overhead = 1+sum(sum(w is not None for w in row)-1 for row in parents)
    overhead += sum(sum(w is not None for w in row) for row in heads)
    return weight_work, overhead


def mapped_context(x, permutation, flips):
    return tuple(x[permutation[j]] ^ flips[j] for j in range(3))


def transformed_mask(mask, permutation, flips, complement):
    out = 0
    for i, x in enumerate(X):
        y = mapped_context(x, permutation, flips)
        j = 4*y[0]+2*y[1]+y[2]
        out |= (((mask >> j) & 1) ^ complement) << i
    return out


def decision_list_masks():
    # All complete literal lists. Shorter lists extend by a constant suffix.
    masks = set()
    for order in permutations(range(3)):
        for branches in X:
            for labels in X:
                for default in (0, 1):
                    mask = 0
                    for i, x in enumerate(X):
                        label = default
                        for coordinate, branch, output in zip(order, branches, labels):
                            if x[coordinate] == branch:
                                label = output
                                break
                        mask |= label << i
                    masks.add(mask)
    return masks


def obstruction_core(mask):
    # Exhaustive independent lower certificate, at most 255 subsets.
    for core in range(1, 256):
        indices = [i for i in range(8) if (core >> i) & 1]
        if len({(mask >> i) & 1 for i in indices}) != 2:
            continue
        valid = True
        for coordinate in range(3):
            for bit in (0, 1):
                labels = {(mask >> i) & 1 for i in indices if X[i][coordinate] == bit}
                if len(labels) == 1:
                    valid = False
        if valid:
            return core
    return None


def audit():
    require(len(WITNESSES) == 14, "incomplete representative list")
    coverage, prototype_data = {}, {}
    for mask, certificate in sorted(WITNESSES.items()):
        require(verify(mask, certificate), f"invalid witness {mask}")
        orbit = set()
        for permutation in permutations(range(3)):
            for flips in X:
                for complement in (0, 1):
                    target = transformed_mask(mask, permutation, flips, complement)
                    orbit.add(target)
                    record = (mask, permutation, flips, complement)
                    if target in coverage:
                        require(coverage[target][0] == mask, "overlapping distinct orbits")
                    else:
                        coverage[target] = record
        require(len(orbit) == certificate[2], "false orbit size")
        bound, exponent, total_coefficients = F(0), 0, 0
        for i, x in enumerate(X):
            masses = laurent_masses(certificate, x)
            correct = (mask >> i) & 1
            leading = masses[correct][min(masses[correct])]
            bound = max(bound, F(sum(masses[1-correct].values()), leading))
            exponent = max(exponent, -min(min(m) for m in masses))
            total_coefficients = max(total_coefficients, sum(sum(m.values()) for m in masses))
        work, overhead = resource_constants(certificate)
        require(bound <= 4 and exponent <= 5 and total_coefficients <= 9, "false uniform bound")
        require(work <= 12 and overhead <= 8, "false uniform SUM work bound")
        prototype_data[str(mask)] = {
            "orbit": len(orbit), "PRODUCTs": len(certificate[0]),
            "sup_error_over_epsilon_upper": str(bound),
            "maximum_mass_pole_order": exponent,
            "maximum_row_total_coefficient_sum": total_coefficients,
            "SUM_count_at_epsilon_2_to_minus_k": f"{work}*k+{overhead}"}
    require(set(coverage) == set(range(256)), "not all targets covered")
    lists = decision_list_masks()
    require(len(lists) == 96, "wrong literal-list classification")
    counts, lower_cores, rational_contexts, expanded_graphs = [0, 0, 0], 0, 0, 0
    for target, (mask, permutation, flips, complement) in sorted(coverage.items()):
        certificate = WITNESSES[mask]
        p = len(certificate[0])
        counts[p] += 1
        require((target in lists) == (p == 0), "SUM upper/lower classifications disagree")
        core = obstruction_core(target)
        require((core is None) == (p == 0), "missing independent core certificate")
        lower_cores += core is not None
        if p == 2:
            require(target in (105, 150), "unproved one-PRODUCT exclusion")
        work, overhead = resource_constants(certificate)
        bound = F(prototype_data[str(mask)]["sup_error_over_epsilon_upper"])
        for k in (1, 4, 8):
            epsilon = F(1, 2**k)
            for i, x in enumerate(X):
                y = mapped_context(x, permutation, flips)
                native = native_masses(certificate, y, epsilon)
                expanded, sum_count, product_count = alphabet_masses(certificate, y, k)
                polys = laurent_masses(certificate, y)
                algebraic = [sum((c*epsilon**a for a, c in poly.items()), F(0)) for poly in polys]
                require(native == expanded == algebraic, "rational execution mismatch")
                require(sum_count == work*k+overhead and product_count == p,
                        "false complete expanded graph count")
                q_one = native[1-complement]/sum(native)
                label = (target >> i) & 1
                error = abs(q_one-label)
                require(error <= bound*epsilon, "false finite error bound")
                rational_contexts += 1
            expanded_graphs += 1
    require(counts == [96, 158, 2], "wrong exact minima counts")
    # Adversarial evidence: labels/budgets/orders are external, not trusted metadata.
    rejected = 0
    for mask, certificate in WITNESSES.items():
        require(not verify(mask ^ 255, certificate), "accepted wrong target")
        rejected += 1
    for bad_value in (0.0, True, "0"):
        bad = deepcopy(WITNESSES[6]); bad[0][0][0][0] = bad_value
        require(not verify(6, bad), "accepted inexact or malformed coefficient")
        rejected += 1
    bad = deepcopy(WITNESSES[6]); bad[0][0][0].append(0)
    require(not verify(6, bad), "accepted illegal parent dimension"); rejected += 1
    for mask, certificate in WITNESSES.items():
        if len(certificate[0]) <= 1:
            require(not verify(105, certificate), "accepted one-PRODUCT parity certificate")
            rejected += 1
    # Independent exact evaluations of the complete one-PRODUCT moment identity.
    rng = Random(20260912)
    moment_cases = 240
    for case in range(moment_cases):
        coeff = lambda n: [F(rng.randrange(9), rng.randrange(1, 8)) for _ in range(n)]
        left, right = coeff(6), coeff(6)
        if case % 3 == 0:
            right = list(left)  # repeated parent / square is included
        heads = [coeff(7), coeff(7)]
        masses = []
        for x in X:
            source = [F(x[i] == b) for i in range(3) for b in (0, 1)]
            g = sum(a*b for a, b in zip(left, source))*sum(a*b for a, b in zip(right, source))
            vals = source+[g]
            masses.append([1+sum(a*b for a, b in zip(head, vals)) for head in heads])
        for label in (0, 1):
            require(sum(((-1)**sum(x))*m[label] for x, m in zip(X, masses)) == 0,
                    "invalid complete-class degree moment")
        require(max(abs(m[1]/sum(m)-(sum(x)%2)) for x, m in zip(X, masses)) >= F(1, 2),
                "false parity lower bound")
    # A convex mixture of five SUM-closure points needs TWO PRODUCTs.
    components = [(255, F(3, 7))]+[(1 << i, F(1, 7)) for i, x in enumerate(X) if sum(x)%2]
    require(all(mask in lists for mask, _ in components), "component not SUM closure")
    target = [sum(w*((mask >> i)&1) for mask, w in components) for i in range(8)]
    require(target == [F(4 if sum(x)%2 else 3, 7) for x in X], "wrong mixture")
    r, caps = F(4, 3), []
    for x, expected in zip(X, target):
        a = (x[0]+x[1])*(2-x[0]-x[1])
        b = a*x[2]
        m0 = 1+(r-1)*(1-x[2])+(r-1)*(r+1)**2*b
        m1 = 1+(r-1)*x[2]+(r*r-1)*a
        require(m1/(m0+m1) == expected, "wrong exact two-PRODUCT mixture witness")
        caps.append(m0+m1)
    require(max(caps) == F(133, 27), "wrong fixed-bank cap")
    # Finite SUM components, not boundary points: all-dimension parity mixtures.
    mixture_rows, mixture_component_contexts, mixture_cases = 0, 0, []
    for d in range(1, 9):
        contexts = tuple(product((0, 1), repeat=d))
        odd = [v for v in contexts if sum(v) % 2]
        K = len(odd)
        midpoint = F(4, 1)-F(2, 2**d)
        midpoint /= 3*(d+1)
        h = 1-midpoint
        amplitude = F(1, 3*(2**d)*(d+1))
        require(F(0) < midpoint <= F(1, 2), "illegal constant SUM component")
        require(1/midpoint <= 3*(d+1), "constant component exceeds declared cap")
        finite_target = []
        for x in contexts:
            component_sum = F(0)
            for v in odd:
                distance = sum(a != b for a, b in zip(x, v))
                m0, m1 = 1+3*distance, 2
                require(m0+m1 <= 3*(d+1), "native SUM component exceeds cap")
                component_sum += F(m1, m0+m1)
                mixture_component_contexts += 1
            q = h/2+component_sum/(2*K)
            expected = F(1, 2)+(amplitude if sum(x) % 2 else -amplitude)
            require(q == expected, "false finite-mixture parity amplitude")
            finite_target.append(q)
            mixture_rows += 1
        mixture_cases.append({"d": d, "finite_SUM_components": K+1,
                              "component_normalizer_cap": 3*(d+1),
                              "parity_amplitude": str(amplitude),
                              "necessary_PRODUCT_count": (d-1).bit_length()})
        if d == 3:
            eta = F(47, 96)
            ratio = (1-eta)/eta
            finite_cap = F(0)
            for x, q in zip(contexts, finite_target):
                a = (x[0]+x[1])*(2-x[0]-x[1]); b = a*x[2]
                m0 = 1+(ratio-1)*(1-x[2])+(ratio-1)*(ratio+1)**2*b
                m1 = 1+(ratio-1)*x[2]+(ratio*ratio-1)*a
                require(m1/(m0+m1) == q, "finite mixture lacks claimed exact two-PRODUCT witness")
                finite_cap = max(finite_cap, m0+m1)
            require(finite_cap == F(239520, 103823), "wrong finite-mixture witness cap")
    for d in range(1, 13):
        require(sum(F((-1)**r*comb(d, r), r+1) for r in range(d+1)) == F(1, d+1),
                "false alternating reciprocal identity")
    return {
        "status": "PASS", "base_commit": BASE_COMMIT,
        "scope": "static three-bit deterministic prediction closure; unrestricted normalizers and finite SUM work",
        "arithmetic": "exact integer Laurent coefficients and fractions.Fraction; no solver in verifier",
        "truth_tables": 256, "symmetry_orbits": 14,
        "minimum_PRODUCT_counts": {"0": counts[0], "1": counts[1], "2": counts[2]},
        "independent_literal_list_functions": len(lists), "independent_SUM_obstruction_cores": lower_cores,
        "SUM_sup_error_lower_outside_lists": "1/5", "one_PRODUCT_parity_sup_error_lower": "1/2",
        "rational_native_context_checks": rational_contexts,
        "expanded_finite_alphabet_graphs": expanded_graphs,
        "finite_epsilon_values": ["1/2", "1/16", "1/256"],
        "uniform_constructive_bounds": {"sup_error": "4*2^(-k)",
            "normalizer": "9*2^(5*k)", "SUM_nodes": "12*k+8",
            "local_coefficient_alphabet": ["1/2", "1", "2"]},
        "forged_certificates_rejected": rejected, "exact_one_PRODUCT_moment_cases": moment_cases,
        "convex_mixture_counterexample": {"SUM_closure_components": 5,
            "target_even": "3/7", "target_odd": "4/7", "minimum_PRODUCTs": 2,
            "one_PRODUCT_sup_error_lower": "1/14", "exact_two_PRODUCT_witness_cap": "133/27"},
        "finite_SUM_mixture_theorem": {"dimensions_checked": mixture_cases,
            "complete_target_rows": mixture_rows, "native_component_context_checks": mixture_component_contexts,
            "alternating_identity_dimensions": 12,
            "three_bit_target_even": "47/96", "three_bit_target_odd": "49/96",
            "three_bit_exact_minimum_PRODUCTs": 2, "three_bit_one_PRODUCT_sup_gap": "1/96",
            "three_bit_exact_two_PRODUCT_witness_cap": "239520/103823",
            "uniform_in_dimension_margin_claimed": False},
        "prototype_resource_bounds": prototype_data,
        "not_claimed": ["two-PRODUCT universality for arbitrary strictly positive binary three-bit tables",
                        "fixed normalizer cap closure or exact deterministic probabilities with base one",
                        "unknown-target acquisition, optimizer reachability, Runtime freeze, persistence or AMP bridge"],
        "source_sha256": sha256(Path(__file__).read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the deterministic minimal evidence")
    args = parser.parse_args()
    result = audit()
    text = json.dumps(result, indent=2, sort_keys=True)+"\n"
    if args.write:
        path = Path(__file__).resolve().parents[2]/"evidence/minimal/FP_THREE_BIT_DETERMINISTIC_CLOSURE_AUDIT.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
