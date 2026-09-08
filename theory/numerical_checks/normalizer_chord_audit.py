"""Global normalizer-chord CE certificates, with rational dual-residual correction."""
from fractions import Fraction as F
from functools import lru_cache
from heapq import heappop, heappush
from itertools import product
from pathlib import Path
from copy import deepcopy
import argparse
import json

from positive_cone_loss_audit import (Model, Unresolved, check_dual, check_primal, dot,
                                     from_features, likelihood, local_witness_proposal,
                                     lp_alternative, rational)


def floor_grid(v, bits):
    scale = 1 << bits
    return F(v.numerator*scale//v.denominator, scale)


@lru_cache(maxsize=4096)
def log_bounds(value, bits=48, terms=16):
    assert rational(value) and value > 0 and type(bits) is int and bits > 0 and type(terms) is int and terms > 0
    value = F(value)
    if value == 1:
        return F(0), F(0)
    exponent = value.numerator.bit_length()-value.denominator.bit_length()
    scale = F(2)**exponent
    reduced = value/scale
    if reduced < 1:
        reduced *= 2
        exponent -= 1
    assert 1 <= reduced < 2
    def series(r):
        z = (r-1)/(r+1)
        center = 2*sum((z**(2*j+1)/F(2*j+1) for j in range(terms)), F(0))
        power = 2*terms+1
        tail = 2*abs(z)**power/(power*(1-z*z))
        return center-tail, center+tail
    lo, hi = series(reduced)
    two_lo, two_hi = series(F(2))
    lo += exponent*(two_lo if exponent >= 0 else two_hi)
    hi += exponent*(two_hi if exponent >= 0 else two_lo)
    return floor_grid(lo, bits), -floor_grid(-hi, bits)


def masses(model, w):
    return tuple(b+sum((a[i]*v for a, v in zip(model.atoms, w)), F(0)) for i, b in enumerate(model.base))


def ce_upper(model, w):
    return -sum(c*log_bounds(q)[0] for c, q in zip(model.counts, model.prediction(w)))/sum(model.counts)


def root_box(model):
    boxes = []
    for i in range(0, len(model.base), model.labels):
        base = sum(model.base[i:i+model.labels])
        row = tuple(sum(a[i:i+model.labels]) for a in model.atoms)
        candidates = [rhs+base for original, rhs in model.restrictions if original == row]
        if not any(row):
            candidates.append(base)
        if not candidates:
            raise Unresolved('no finite normalizer cap proved from original rows')
        boxes.append((base, min(candidates)))
    return tuple(boxes)


def rows_for(model, box):
    rows = list(model.restrictions)
    for x, (lo, hi) in enumerate(box):
        i = x*model.labels
        base = sum(model.base[i:i+model.labels])
        total = tuple(sum(a[i:i+model.labels]) for a in model.atoms)
        rows.extend(((total, hi-base), (tuple(-v for v in total), base-lo)))
    return tuple(rows)


def chords(box):
    result = []
    for lo, hi in box:
        assert 0 < lo <= hi
        lower_log, upper_log = log_bounds(lo)[0], log_bounds(hi)[0]
        slope = F(0) if lo == hi else (upper_log-lower_log)/(hi-lo)
        result.append((slope, lower_log-slope*lo))
    return tuple(result)


def linearization(model, box, support):
    assert len(support) == len(model.base) and all(rational(s) and s > 0 for s in support)
    constant, gradient = F(0), [F(0)]*len(model.atoms)
    for x, (slope, intercept) in enumerate(chords(box)):
        i = x*model.labels
        count = sum(model.counts[i:i+model.labels])
        constant += count*(slope*sum(model.base[i:i+model.labels])+intercept)
        for j, atom in enumerate(model.atoms):
            gradient[j] += count*slope*sum(atom[i:i+model.labels])
    for i, (c, s, b) in enumerate(zip(model.counts, support, model.base)):
        constant += c*(1-log_bounds(s)[1]-b/s)
        for j, atom in enumerate(model.atoms):
            gradient[j] -= c*atom[i]/s
    return constant, tuple(gradient)


def lower_bound(model, box, support, dual):
    rows = rows_for(model, box)
    assert len(dual) == len(rows) and all(rational(y) and y <= 0 for y in dual)
    constant, gradient = linearization(model, box, support)
    penalty = F(0)
    for j, atom in enumerate(model.atoms):
        residual = max(F(0), sum(row[j]*y for (row, _), y in zip(rows, dual))-gradient[j])
        caps = []
        for x, (_, hi) in enumerate(box):
            i = x*model.labels
            total_atom = sum(atom[i:i+model.labels])
            if total_atom:
                caps.append((hi-sum(model.base[i:i+model.labels]))/total_atom)
        if caps:
            cap = min(caps)
            assert cap >= 0
            penalty += residual*cap
        else:
            assert residual == 0  # No finite bound may be invented for a null atom.
    uncorrected = constant+sum(rhs*y for (_, rhs), y in zip(rows, dual))
    return max(F(0), (uncorrected-penalty)/sum(model.counts)), penalty, uncorrected


def propose(model, box, feasible):
    import numpy as np
    from scipy.optimize import linprog, minimize
    rows = rows_for(model, box)
    width = len(model.atoms)
    if width == 0:
        return masses(model, feasible), (F(0),)*len(rows), feasible, 0
    matrix, rhs = np.array([a for a, _ in rows], float), np.array([b for _, b in rows], float)
    atom_matrix, base = np.array(model.atoms, float), np.array(model.base, float)
    counts = np.array(model.counts, float)
    slopes = np.array([float(a)*sum(model.counts[x*model.labels:(x+1)*model.labels])
                       for x, (a, _) in enumerate(chords(box))])
    def objective(w):
        mass = base+atom_matrix.T@w
        totals = mass.reshape(-1, model.labels).sum(1)
        return float(slopes@totals-counts@np.log(mass)), atom_matrix@(np.repeat(slopes, model.labels)-counts/mass)
    result = minimize(objective, np.array(feasible, float), jac=True, method='SLSQP',
                      bounds=[(0, None)]*width,
                      constraints={'type': 'ineq', 'fun': lambda w: rhs-matrix@w, 'jac': lambda w: -matrix},
                      options={'maxiter': 300, 'ftol': 1e-12})
    raw = np.maximum(result.x, 0) if np.all(np.isfinite(result.x)) else np.array(feasible, float)
    support = tuple(max(b/2, floor_grid(F(float(v)), 24)) for b, v in zip(model.base, base+atom_matrix.T@raw))
    witness = feasible
    score = likelihood(model.prediction(witness), model.counts)
    original = rows_for(model, root_box(model))
    for denominator in (1000, 10**6):
        for rounding in ('nearest', 'down'):
            candidate = tuple(F(float(v)).limit_denominator(denominator) if rounding == 'nearest'
                              else F(int(np.floor(v*denominator)), denominator) for v in raw)
            if check_primal(original, candidate):
                value = likelihood(model.prediction(candidate), model.counts)
                if value > score:
                    witness, score = candidate, value
    _, gradient = linearization(model, box, support)
    linear = linprog(np.array(gradient, float), A_ub=matrix, b_ub=rhs, bounds=(0, None), method='highs')
    dual = ((tuple(min(F(0), F(float(v)).limit_denominator(10**6)) for v in linear.ineqlin.marginals))
            if linear.success else (F(0),)*len(rows))
    try:
        lower_bound(model, box, support, dual)
    except AssertionError:
        dual = (F(0),)*len(rows)
    return support, dual, witness, result.nfev


def _solve(model, epsilon, node_budget):
    assert rational(epsilon) and epsilon > 0 and type(node_budget) is int and node_budget > 0
    box = root_box(model)
    status, point = lp_alternative(rows_for(model, box), len(model.atoms))
    if status == 'dual':
        return {'status': 'EMPTY_STATIC_CLASS', 'tree': {'kind': 'empty', 'dual': point}, 'nodes': 1}
    best, proposal_evaluations = local_witness_proposal(model, point)
    best_likelihood = likelihood(model.prediction(best), model.counts)
    upper = ce_upper(model, best)
    tree, queue = {}, []
    nodes, convex_evaluations = 0, 0

    def analyze(current_box, node):
        nonlocal nodes, convex_evaluations, best, best_likelihood, upper
        nodes += 1
        if nodes > node_budget:
            raise Unresolved('normalizer node budget exhausted')
        kind, value = lp_alternative(rows_for(model, current_box), len(model.atoms))
        if kind == 'dual':
            node.update(kind='empty', dual=value)
            return
        support, dual, candidate, evaluations = propose(model, current_box, value)
        convex_evaluations += evaluations
        candidate_score = likelihood(model.prediction(candidate), model.counts)
        if candidate_score > best_likelihood:
            best, best_likelihood, upper = candidate, candidate_score, ce_upper(model, candidate)
        lower, _, _ = lower_bound(model, current_box, support, dual)
        node.update(kind='bound', support=support, dual=dual, claimed_lower=lower)
        heappush(queue, (lower, nodes, current_box, node))

    analyze(box, tree)
    while queue:
        lower, _, current_box, node = heappop(queue)
        if lower >= upper-epsilon:
            continue
        axis = max(range(len(box)), key=lambda x: (current_box[x][1]-current_box[x][0])/current_box[x][0])
        lo, hi = current_box[axis]
        if lo == hi:
            raise Unresolved('support/dual precision cannot close a fixed-normalizer box')
        left, right = list(current_box), list(current_box)
        mid = (lo+hi)/2
        left[axis], right[axis] = (lo, mid), (mid, hi)
        node.clear()
        node.update(kind='split', axis=axis, left={}, right={})
        analyze(tuple(left), node['left'])
        analyze(tuple(right), node['right'])
    return {'status': 'CERTIFIED_STATIC_CE_BRACKET', 'epsilon': epsilon, 'witness': best,
            'ce_upper': upper, 'tree': tree, 'nodes': nodes,
            'initial_local_objective_evaluations': proposal_evaluations,
            'convex_proposal_objective_evaluations': convex_evaluations}


def solve(model, epsilon=F(1, 200), node_budget=5000):
    try:
        return _solve(model, epsilon, node_budget)
    except (Unresolved, RecursionError, OverflowError, FloatingPointError) as exc:
        return {'status': 'UNRESOLVED', 'reason': str(exc)}


def verify(model, result, expected_epsilon):
    assert result['status'] in ('EMPTY_STATIC_CLASS', 'CERTIFIED_STATIC_CE_BRACKET')
    box = root_box(model)
    if result['status'] == 'EMPTY_STATIC_CLASS':
        assert result['tree']['kind'] == 'empty'
        assert check_dual(rows_for(model, box), result['tree']['dual'], len(model.atoms))
        return None, 1
    epsilon, witness = result['epsilon'], result['witness']
    assert rational(epsilon) and rational(expected_epsilon) and epsilon == expected_epsilon and epsilon > 0
    assert len(witness) == len(model.atoms) and check_primal(rows_for(model, box), witness)
    upper = ce_upper(model, witness)
    assert rational(result['ce_upper']) and result['ce_upper'] == upper

    def walk(node, current_box):
        if node['kind'] == 'empty':
            assert check_dual(rows_for(model, current_box), node['dual'], len(model.atoms))
            return None, 1
        if node['kind'] == 'bound':
            lower, _, _ = lower_bound(model, current_box, node['support'], node['dual'])
            assert rational(node['claimed_lower']) and node['claimed_lower'] == lower and lower >= upper-epsilon
            return lower, 1
        assert node['kind'] == 'split' and type(node['axis']) is int and 0 <= node['axis'] < len(box)
        axis = node['axis']
        lo, hi = current_box[axis]
        assert lo < hi
        left, right = list(current_box), list(current_box)
        mid = (lo+hi)/2
        left[axis], right[axis] = (lo, mid), (mid, hi)
        a, an = walk(node['left'], tuple(left))
        b, bn = walk(node['right'], tuple(right))
        finite = [v for v in (a, b) if v is not None]
        return (min(finite) if finite else None), 1+an+bn
    lower, nodes = walk(result['tree'], box)
    assert lower is not None and lower <= upper and upper-lower <= epsilon and nodes == result['nodes']
    return lower, nodes


def audit():
    from decimal import Decimal, localcontext
    # Exact log identities exercise positive and negative power-of-two scaling.
    log_cases = 0
    for value in (F(1, 1024), F(1, 3), F(1), F(3, 2), F(2), F(17), F(1024)):
        lo, hi = log_bounds(value)
        inverse = log_bounds(1/value)
        doubled = log_bounds(value*2)
        two = log_bounds(F(2))
        assert lo <= hi and max(lo, -inverse[1]) <= min(hi, -inverse[0])
        assert max(doubled[0], lo+two[0]) <= min(doubled[1], hi+two[1])
        assert hi-lo < F(1, 10**12)
        with localcontext() as context:
            context.prec = 80
            reference = (Decimal(value.numerator)/Decimal(value.denominator)).ln()
            assert Decimal(lo.numerator)/Decimal(lo.denominator) <= reference <= Decimal(hi.numerator)/Decimal(hi.denominator)
        log_cases += 1
    curvature_cases = 0
    for lo, hi in ((F(1), F(2)), (F(2), F(4)), (F(3), F(7, 2)), (F(16), F(16))):
        slope, intercept = chords(((lo, hi),))[0]
        endpoint_error = max(log_bounds(v)[1]-log_bounds(v)[0] for v in (lo, hi))
        for fraction in (F(0), F(1, 4), F(1, 2), F(3, 4), F(1)):
            value = lo+(hi-lo)*fraction
            a, b = log_bounds(value)
            chord = slope*value+intercept
            assert chord <= a
            assert b-chord <= (hi-lo)**2/(8*lo**2)+endpoint_error+(b-a)
            curvature_cases += 1
    features = tuple((F(i == 0), F(i == 1), F(j == 0), F(j == 1)) for i, j in product((0, 1), repeat=2))
    model = from_features(features, ((3, 1), (1, 3), (1, 3), (3, 1)), cap=4)
    result = solve(model)
    if result['status'] == 'UNRESOLVED':
        raise Unresolved(result['reason'])
    lower, nodes = verify(model, result, F(1, 200))
    rejected = []
    for attack in ('missing_child', 'invalid_axis', 'false_lower', 'positive_dual', 'weaken_accuracy', 'invalid_witness'):
        fake = deepcopy(result)
        if attack == 'missing_child':
            del fake['tree']['right']
        elif attack == 'invalid_axis':
            fake['tree']['axis'] = len(root_box(model))
        elif attack in ('false_lower', 'positive_dual'):
            todo = [fake['tree']]
            while todo:
                node = todo.pop()
                if node['kind'] == 'bound':
                    if attack == 'false_lower':
                        node['claimed_lower'] += 1
                    else:
                        node['dual'] = (F(1),)+node['dual'][1:]
                    break
                if node['kind'] == 'split':
                    todo.extend((node['left'], node['right']))
        elif attack == 'weaken_accuracy':
            fake['epsilon'] = F(1)
        else:
            fake['witness'] = (F(-1),)+fake['witness'][1:]
        try:
            verify(model, fake, F(1, 200))
        except (AssertionError, KeyError):
            rejected.append(attack)
        else:
            raise AssertionError(f'forgery accepted: {attack}')

    # A null mass atom is not licensed a fabricated finite coefficient cap.
    null_model = Model(2, (1, 1), ((1, 0), (0, 0)), (3, 1), (((1, 0), 1), ((0, -1), -1)))
    null_box = root_box(null_model)
    dual = (F(0), F(-1), F(0), F(0))
    try:
        lower_bound(null_model, null_box, (F(1), F(1)), dual)
    except AssertionError:
        null_rejected = True
    else:
        raise AssertionError('unbounded null-atom residual was silently erased')
    assert solve(model, node_budget=1)['status'] == 'UNRESOLVED'
    unsupported = from_features(features, ((3, 1), (1, 3), (1, 3), (3, 1)))
    assert solve(unsupported)['status'] == 'UNRESOLVED'

    # Omitting a negative gradient residual produces a concretely false lower.
    residual_model = Model(2, (1, 1), ((1, 0),), (3, 1), (((1,), 2),))
    residual_box = root_box(residual_model)
    corrected, penalty, uncorrected = lower_bound(residual_model, residual_box, (F(1), F(1)),
                                                 (F(0),)*len(rows_for(residual_model, residual_box)))
    attained = ce_upper(residual_model, (F(2),))
    assert penalty > 0 and corrected <= attained < uncorrected/4

    # A genuinely coupled multiclass control, with a known independent optimum.
    multiclass = from_features(((F(1),), (F(1),)), ((3, 1, 0), (0, 1, 3)), cap=4)
    multi_result = solve(multiclass)
    multi_lower, multi_nodes = verify(multiclass, multi_result, F(1, 200))
    exact_likelihood = F(3, 8)**6*F(1, 4)**2
    assert likelihood(multiclass.prediction(multi_result['witness']), multiclass.counts) == exact_likelihood
    assert multi_lower <= -log_bounds(exact_likelihood)[1]/8

    def dyadic_lower(v):
        return str(floor_grid(v, 64))
    output_lower = F(dyadic_lower(lower))
    assert result['ce_upper']-output_lower <= F(1, 200)
    assert result['ce_upper']-lower < F(448, 100000)
    fine_result = solve(model, epsilon=F(1, 10**6))
    fine_lower, fine_nodes = verify(model, fine_result, F(1, 10**6))
    fine_output_lower = F(dyadic_lower(fine_lower))
    assert fine_result['ce_upper']-fine_output_lower <= F(1, 10**6)
    assert fine_result['ce_upper']-fine_lower < F(752, 10**9)
    assert F('0.68483177') <= fine_lower and fine_result['ce_upper'] <= F('0.68483253')
    return {'status': 'PASS', 'scope': 'same full cap-four normalized unary-SUM XOR class as XVII.9',
            'exact_log_enclosure_identity_cases': log_cases,
            'independent_decimal_log_reference_digits': 80,
            'rational_chord_curvature_cases': curvature_cases,
            'verified_normalizer_tree_nodes': nodes,
            'declared_mean_ce_epsilon': '1/200',
            'verified_mean_ce_lower_enclosure': str(output_lower), 'verified_mean_ce_upper': str(result['ce_upper']),
            'mean_ce_lower_float64_display': float(lower), 'mean_ce_upper_float64_display': float(result['ce_upper']),
            'mean_ce_width_float64_display': float(result['ce_upper']-lower),
            'initial_local_objective_evaluations': result['initial_local_objective_evaluations'],
            'convex_proposal_objective_evaluations': result['convex_proposal_objective_evaluations'],
            'previous_independently_verified_probability_tree_nodes': 43023,
            'previous_mean_ce_width_upper': '0.006',
            'high_accuracy_same_class': {'declared_epsilon': '1/1000000', 'verified_nodes': fine_nodes,
                                         'ce_lower_enclosure': str(fine_output_lower),
                                         'ce_upper': str(fine_result['ce_upper']),
                                         'conservative_decimal_interval': ['0.68483177', '0.68483253'],
                                         'width_float64_display': float(fine_result['ce_upper']-fine_lower)},
            'forged_certificate_rejections': rejected,
            'unbounded_null_atom_residual_rejected': null_rejected,
            'uncorrected_dual_has_explicit_false_lower_counterexample': True,
            'coupled_three_label_control': {'verified_nodes': multi_nodes,
                                           'lower_ce_enclosure': dyadic_lower(multi_lower),
                                           'upper_ce': str(multi_result['ce_upper']),
                                           'exact_optimum_likelihood_attained': str(exact_likelihood)},
            'node_budget_and_missing_caps_return_unresolved': True,
            'not_claimed': ['numerical convex optimizer is a completeness oracle', 'polynomial work bound',
                            'arbitrary unbounded normalizers handled by this fast path',
                            'physical Compiler budget or complete runtime/AMP certification']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_NORMALIZER_CHORD_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
