"""Global static likelihood bounds with independently checked rational proof trees."""
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from copy import deepcopy
from math import log
from heapq import heappop, heappush
import argparse
import json


class Unresolved(RuntimeError):
    pass


def rational(value):
    return type(value) in (int, F)


def dot(a, b):
    return sum((x*y for x, y in zip(a, b)), F(0))


@dataclass(frozen=True)
class Model:
    labels: int
    base: tuple
    atoms: tuple  # atom-major flat context/label columns
    counts: tuple
    restrictions: tuple = ()  # (row, rhs), row*w <= rhs

    def __post_init__(self):
        assert type(self.labels) is int and self.labels >= 2 and len(self.base) % self.labels == 0
        assert all(rational(v) for v in self.base)
        assert len(self.counts) == len(self.base) and min(self.base) > 0
        assert all(type(c) is int and c >= 0 for c in self.counts) and sum(self.counts) > 0
        assert all(len(a) == len(self.base) and all(rational(v) for v in a) and min(a) >= 0 for a in self.atoms)
        assert all(len(a) == len(self.atoms) and all(rational(v) for v in a) and rational(b)
                   for a, b in self.restrictions)
        object.__setattr__(self, 'base', tuple(map(F, self.base)))
        object.__setattr__(self, 'counts', tuple(self.counts))
        object.__setattr__(self, 'atoms', tuple(tuple(map(F, a)) for a in self.atoms))
        object.__setattr__(self, 'restrictions', tuple((tuple(map(F, a)), F(b)) for a, b in self.restrictions))

    def prediction(self, w):
        assert len(w) == len(self.atoms) and min(w, default=0) >= 0
        masses = tuple(b+sum((a[i]*v for a, v in zip(self.atoms, w)), F(0)) for i, b in enumerate(self.base))
        return tuple(m/sum(masses[i:i+self.labels])
                     for i in range(0, len(masses), self.labels) for m in masses[i:i+self.labels])

    def inequalities(self, box):
        rows = list(self.restrictions)
        for i in range(0, len(self.base), self.labels):
            total_base = sum(self.base[i:i+self.labels])
            total_atoms = tuple(sum(a[i:i+self.labels]) for a in self.atoms)
            for j in range(i, i+self.labels):
                lo, hi = box[j]
                column = tuple(a[j] for a in self.atoms)
                rows.append((tuple(v-hi*t for v, t in zip(column, total_atoms)), hi*total_base-self.base[j]))
                rows.append((tuple(lo*t-v for v, t in zip(column, total_atoms)), self.base[j]-lo*total_base))
        return tuple(rows)


def likelihood(q, counts):
    result = F(1)
    for p, c in zip(q, counts):
        result *= p**c
    return result


def initial_box(model):
    """Infer only caps whose exact coefficient row is an original constraint."""
    box = [(F(0), F(1)) for _ in model.base]
    for i in range(0, len(model.base), model.labels):
        base_total = sum(model.base[i:i+model.labels])
        total_row = tuple(sum(a[i:i+model.labels]) for a in model.atoms)
        caps = [rhs+base_total for row, rhs in model.restrictions if row == total_row and rhs >= 0]
        if caps:
            cap = min(caps)
            for j in range(i, i+model.labels):
                box[j] = (model.base[j]/cap, 1-(base_total-model.base[j])/cap)
    return tuple(box)


def tighten(box, labels):
    result = []
    for i in range(0, len(box), labels):
        group = box[i:i+labels]
        lower, upper = sum(a for a, _ in group), sum(b for _, b in group)
        if lower > 1 or upper < 1 or any(a > b for a, b in group):
            return None
        result.extend((max(a, 1-upper+b), min(b, 1-lower+a)) for a, b in group)
    return tuple(result)


def simplex_maximum(box, counts):
    lower, upper = tuple(a for a, _ in box), tuple(b for _, b in box)
    assert sum(lower) <= 1 <= sum(upper)
    positive = [i for i, c in enumerate(counts) if c]
    zero = [i for i, c in enumerate(counts) if not c]

    def fill(q, indices):
        remaining = 1-sum(q)
        for i in indices:
            amount = min(remaining, upper[i]-q[i])
            q[i] += amount
            remaining -= amount
        assert remaining == 0
        return tuple(q)

    if any(upper[i] == 0 for i in positive):
        return fill(list(lower), range(len(box)))  # Every likelihood is zero.
    if sum(upper[i] for i in positive)+sum(lower[i] for i in zero) <= 1:
        return fill([upper[i] if counts[i] else lower[i] for i in range(len(box))], zero)
    breaks = sorted({F(counts[i])/v for i in positive for v in (lower[i], upper[i]) if v > 0})
    probes = [breaks[0]/2]+[(a+b)/2 for a, b in zip(breaks, breaks[1:])]+[2*breaks[-1]+1]

    def clipped(lam):
        return tuple(min(upper[i], max(lower[i], F(c)/lam)) if c else lower[i]
                     for i, c in enumerate(counts))

    for probe in probes:
        q = clipped(probe)
        if sum(q) == 1:
            return q
        free = [i for i in positive if lower[i] < F(counts[i])/probe < upper[i]]
        remaining = 1-sum(q[i] for i in range(len(box)) if i not in free)
        if free and remaining > 0:
            lam = F(sum(counts[i] for i in free))/remaining
            candidate = clipped(lam)
            if sum(candidate) == 1:
                return candidate
    raise AssertionError('exact water-filling normalization was not found')


def box_upper(model, box):
    q = []
    for i in range(0, len(box), model.labels):
        group, counts = box[i:i+model.labels], model.counts[i:i+model.labels]
        point = simplex_maximum(group, counts)
        check_simplex_maximum(group, counts, point)
        q.extend(point)
    q = tuple(q)
    return likelihood(q, model.counts), q


def check_simplex_maximum(box, counts, q):
    """Separate exact KKT check; never trust the active-set proposal itself."""
    assert sum(q) == 1 and all(lo <= p <= hi for p, (lo, hi) in zip(q, box))
    if any(c and hi == 0 for c, (_, hi) in zip(counts, box)):
        return  # All feasible likelihoods vanish.
    lower, upper, free = F(0), None, []
    for p, c, (lo, hi) in zip(q, counts, box):
        if lo == hi:
            continue
        assert p > 0 or c == 0
        derivative = F(c)/p if c else F(0)
        if p == lo:
            lower = max(lower, derivative)
        elif p == hi:
            upper = derivative if upper is None else min(upper, derivative)
        else:
            free.append(derivative)
    if free:
        assert all(v == free[0] for v in free) and free[0] >= lower
        assert upper is None or free[0] <= upper
    else:
        assert upper is None or lower <= upper


def check_primal(rows, w):
    return all(rational(v) for v in w) and min(w, default=0) >= 0 and all(dot(row, w) <= rhs for row, rhs in rows)


def check_dual(rows, dual, width):
    return (len(dual) == len(rows) and all(rational(v) for v in dual) and min(dual, default=0) >= 0
            and dot(tuple(rhs for _, rhs in rows), dual) < 0
            and all(sum(row[j]*y for (row, _), y in zip(rows, dual)) >= 0 for j in range(width)))


def lp_alternative(rows, width):
    import numpy as np
    from scipy.optimize import linprog
    a, b = tuple(row for row, _ in rows), tuple(rhs for _, rhs in rows)
    if width == 0:
        if all(v >= 0 for v in b):
            return 'primal', ()
        bad = next(i for i, v in enumerate(b) if v < 0)
        return 'dual', tuple(F(i == bad) for i in range(len(rows)))
    matrix, rhs = np.array(a, float), np.array(b, float)
    result = linprog(np.zeros(width), A_ub=matrix, b_ub=rhs, bounds=(0, None), method='highs')
    if result.success:
        for denominator in (10**3, 10**6, 10**10):
            w = tuple(F(float(v)).limit_denominator(denominator) for v in result.x)
            if check_primal(rows, w):
                return 'primal', w
    result = linprog(np.zeros(len(rows)), A_ub=np.vstack((-matrix.T, rhs)),
                     b_ub=np.r_[np.zeros(width), -1.0], bounds=(0, None), method='highs')
    if result.success:
        for denominator in (10**3, 10**6, 10**10):
            dual = tuple(F(float(v)).limit_denominator(denominator) for v in result.x)
            if check_dual(rows, dual, width):
                return 'dual', dual
    raise Unresolved('LP supplied no exactly checked primal or Farkas alternative')


def local_witness_proposal(model, incumbent):
    """Generic float64 multistart proposals; only exact feasibility/score can improve a lower."""
    import numpy as np
    from scipy.optimize import linprog, minimize
    width = len(model.atoms)
    if width == 0:
        return incumbent, 0
    atoms, base = np.array(model.atoms, float), np.array(model.base, float)
    counts = np.array(model.counts, float)
    context_counts = counts.reshape(-1, model.labels).sum(1)
    total = counts.sum()
    def objective(w):
        masses = base+atoms.T@w
        totals = masses.reshape(-1, model.labels).sum(1)
        value = (context_counts@np.log(totals)-counts@np.log(masses))/total
        gradient = atoms@(np.repeat(context_counts/totals, model.labels)-counts/masses)/total
        return value, gradient
    rows = model.inequalities(initial_box(model))
    a, b = np.array([row for row, _ in rows], float), np.array([rhs for _, rhs in rows], float)
    upper = max(1000.0, 2*max(map(float, incumbent), default=0))
    bounds = [(0, upper)]*width  # Proposal box only; global proof retains the whole class.
    constraints = {'type': 'ineq', 'fun': lambda w: b-a@w, 'jac': lambda w: -a}
    rng = np.random.default_rng(20260909)
    best_w, best = incumbent, likelihood(model.prediction(incumbent), model.counts)
    evaluations = 0
    for attempt in range(8):
        if attempt == 0:
            start = np.array(incumbent, float)
        else:
            vertex = linprog(rng.normal(size=width), A_ub=a, b_ub=b, bounds=bounds, method='highs')
            if not vertex.success:
                continue
            start = vertex.x
        result = minimize(objective, start, jac=True, method='SLSQP', bounds=bounds,
                          constraints=constraints, options={'maxiter': 300, 'ftol': 1e-12})
        evaluations += result.nfev
        if not np.all(np.isfinite(result.x)):
            continue
        for denominator in (1000, 10**6):
            for rounding in ('nearest', 'down'):
                proposal = tuple(F(float(v)).limit_denominator(denominator) if rounding == 'nearest'
                                 else F(int(np.floor(v*denominator)), denominator) for v in result.x)
                if check_primal(rows, proposal):
                    score = likelihood(model.prediction(proposal), model.counts)
                    if score > best:
                        best_w, best = proposal, score
    return best_w, evaluations


def _solve(model, gamma, node_budget):
    assert rational(gamma) and gamma > 1 and type(node_budget) is int and node_budget >= 1
    root_box = initial_box(model)
    root_rows = model.inequalities(root_box)
    kind, value = lp_alternative(root_rows, len(model.atoms))
    if kind == 'dual':
        return {'status': 'EMPTY_STATIC_CLASS', 'tree': {'kind': 'empty', 'dual': value}, 'nodes': 1}
    best_w, best = value, likelihood(model.prediction(value), model.counts)
    nodes, lp_calls = 0, 1
    # Strong proposal: the full independent-context likelihood optimizer.
    _, unconstrained = box_upper(model, root_box)
    kind, value = lp_alternative(model.inequalities(tuple((q, q) for q in unconstrained)), len(model.atoms))
    lp_calls += 1
    if kind == 'primal':
        best_w, best = value, likelihood(model.prediction(value), model.counts)
        proposal_evaluations = 0
    else:
        best_w, proposal_evaluations = local_witness_proposal(model, best_w)
        best = likelihood(model.prediction(best_w), model.counts)

    tree, pending, serial = {}, [], 0
    def enqueue(raw_box, node):
        nonlocal serial
        box = tighten(raw_box, model.labels)
        upper = F(0) if box is None else box_upper(model, box)[0]
        heappush(pending, (-upper, serial, box, node))
        serial += 1
    enqueue(root_box, tree)
    try:
        while pending:
            neg_upper, _, box, node = heappop(pending)
            nodes += 1
            if nodes > node_budget:
                raise Unresolved('declared branch node budget exhausted')
            if box is None:
                node.update(kind='simplex_empty')
                continue
            upper = -neg_upper
            if upper <= gamma*best:
                node.update(kind='bound', upper=upper)
                continue
            kind, value = lp_alternative(model.inequalities(box), len(model.atoms))
            lp_calls += 1
            if kind == 'dual':
                node.update(kind='empty', dual=value)
                continue
            score = likelihood(model.prediction(value), model.counts)
            if score > best:
                best_w, best = value, score
            if upper <= gamma*best:
                node.update(kind='bound', upper=upper)
                continue
            axis = max(range(len(box)), key=lambda i: box[i][1]-box[i][0])
            lo, hi = box[axis]
            assert lo < hi
            mid = (lo+hi)/2
            left, right = list(box), list(box)
            left[axis], right[axis] = (lo, mid), (mid, hi)
            node.update(kind='split', axis=axis, left={}, right={})
            enqueue(tuple(left), node['left'])
            enqueue(tuple(right), node['right'])
    except Unresolved as exc:
        return {'status': 'UNRESOLVED', 'reason': str(exc), 'witness': best_w,
                'likelihood_lower': best, 'nodes': nodes, 'lp_calls': lp_calls}
    return {'status': 'CERTIFIED_STATIC_LIKELIHOOD_BRACKET', 'gamma': gamma, 'witness': best_w,
            'likelihood_lower': best, 'tree': tree, 'nodes': nodes, 'lp_calls': lp_calls,
            'local_proposal_objective_evaluations': proposal_evaluations}


def solve(model, gamma=F(2), node_budget=10000):
    try:
        return _solve(model, gamma, node_budget)
    except (Unresolved, RecursionError) as exc:
        return {'status': 'UNRESOLVED', 'reason': str(exc)}


def verify(model, result, expected_gamma):
    """No optimizer calls. Reconstruct coverage and all authority from original inputs."""
    assert result['status'] in ('CERTIFIED_STATIC_LIKELIHOOD_BRACKET', 'EMPTY_STATIC_CLASS')
    root_box = initial_box(model)
    if result['status'] == 'EMPTY_STATIC_CLASS':
        assert result['tree']['kind'] == 'empty'
        assert check_dual(model.inequalities(root_box), result['tree']['dual'], len(model.atoms))
        return F(0), 1
    gamma = result['gamma']
    assert rational(gamma) and rational(expected_gamma) and gamma == expected_gamma and gamma > 1
    w = result['witness']
    assert len(w) == len(model.atoms) and check_primal(model.inequalities(root_box), w)
    lower = likelihood(model.prediction(w), model.counts)
    assert rational(result['likelihood_lower']) and lower == result['likelihood_lower'] and lower > 0

    def walk(node, raw_box):
        box = tighten(raw_box, model.labels)
        if box is None:
            assert node['kind'] == 'simplex_empty'
            return F(0), 1
        if node['kind'] == 'empty':
            assert check_dual(model.inequalities(box), node['dual'], len(model.atoms))
            return F(0), 1
        if node['kind'] == 'bound':
            upper, _ = box_upper(model, box)
            assert rational(node['upper']) and node['upper'] == upper and upper <= gamma*lower
            return upper, 1
        assert node['kind'] == 'split' and type(node['axis']) is int
        axis = node['axis']
        assert 0 <= axis < len(box)
        lo, hi = box[axis]
        assert lo < hi
        mid = (lo+hi)/2
        left, right = list(box), list(box)
        left[axis], right[axis] = (lo, mid), (mid, hi)
        a, an = walk(node['left'], tuple(left))
        b, bn = walk(node['right'], tuple(right))
        return max(a, b), 1+an+bn

    upper, nodes = walk(result['tree'], root_box)
    assert lower <= upper <= gamma*lower
    assert nodes == result['nodes']
    return upper, nodes


def from_features(features, counts, cap=None):
    labels, n = len(counts[0]), len(counts)
    atoms = tuple(tuple(F(row[j] if y == label else 0) for row in features for y in range(labels))
                  for j in range(len(features[0])) for label in range(labels))
    restrictions = () if cap is None else tuple((tuple(sum(a[i*labels:(i+1)*labels]) for a in atoms), F(cap-labels))
                                               for i in range(n))
    return Model(labels, (F(1),)*(n*labels), atoms, tuple(c for row in counts for c in row), restrictions)


def audit():
    # Independent finite-grid control of the exact per-context optimization.
    water_cases = 0
    for counts in ((0, 0, 0), (3, 1, 2), (0, 4, 1), (2, 0, 0)):
        for raw in product(((F(0), F(1)), (F(1, 4), F(3, 4)), (F(0), F(1, 2))), repeat=3):
            box = tighten(raw, 3)
            if box is None:
                continue
            q = simplex_maximum(box, counts)
            assert sum(q) == 1 and all(a <= v <= b for v, (a, b) in zip(q, box))
            score = likelihood(q, counts)
            for i in range(9):
                for j in range(9-i):
                    point = (F(i, 8), F(j, 8), F(8-i-j, 8))
                    if all(a <= v <= b for v, (a, b) in zip(point, box)):
                        assert likelihood(point, counts) <= score
            water_cases += 1

    features = tuple((F(i == 0), F(i == 1), F(j == 0), F(j == 1)) for i, j in product((0, 1), repeat=2))
    rows, certificates = [], []
    fixtures = [('xor_closure_unattained', ((3, 1), (1, 3), (1, 3), (3, 1)), None, F(11, 10)),
                ('xor_cap_four', ((3, 1), (1, 3), (1, 3), (3, 1)), 4, F(11, 10)),
                ('multiclass_bayes', ((1, 2, 3),)*4, None, F(11, 10)),
                ('zero_count_labels', ((4, 0), (0, 4), (0, 4), (4, 0)), None, F(2))]
    for name, counts, cap, gamma in fixtures:
        model = from_features(features, counts, cap)
        result = solve(model, gamma, node_budget=50000)
        if result['status'] == 'UNRESOLVED':
            raise Unresolved(f'{name}: {result["reason"]}; nodes={result["nodes"]}')
        upper, checked_nodes = verify(model, result, gamma)
        lower = result['likelihood_lower']
        if name == 'xor_closure_unattained':
            exact_supremum = F(729, 16777216)
            assert lower < exact_supremum <= upper
        certificates.append((model, result))
        scale = 1 << 80
        rounded_lower = F(lower.numerator*scale//lower.denominator, scale)
        rounded_upper = F(-((-upper.numerator*scale)//upper.denominator), scale)
        assert 0 < rounded_lower <= lower <= upper <= rounded_upper
        assert rounded_upper <= gamma*rounded_lower
        rows.append({'case': name, 'status': result['status'], 'verified_nodes': checked_nodes,
                     'certification_lp_proposals': result['lp_calls'], 'likelihood_lower_enclosure': str(rounded_lower),
                     'local_proposal_objective_evaluations': result['local_proposal_objective_evaluations'],
                     'likelihood_upper_enclosure': str(rounded_upper), 'verified_relative_factor': str(gamma),
                     'exact_bayes_attainment': lower == upper,
                     'mean_ce_lower_float64_display': -log(float(upper))/sum(model.counts),
                     'mean_ce_upper_float64_display': -log(float(lower))/sum(model.counts),
                     'mean_ce_width_float64_display': log(float(upper/lower))/sum(model.counts)})

    # Deliberately forge proof content, rather than only testing helpers.
    model, result = certificates[0]
    rejected = []
    for attack in ('missing_child', 'invalid_axis', 'false_upper', 'false_witness', 'false_dual', 'weaken_accuracy', 'float_witness'):
        fake = deepcopy(result)
        if attack == 'missing_child':
            assert fake['tree']['kind'] == 'split'
            del fake['tree']['right']
        elif attack == 'invalid_axis':
            fake['tree']['axis'] = len(model.base)
        elif attack == 'false_upper':
            pending = [fake['tree']]
            while pending:
                node = pending.pop()
                if node['kind'] == 'bound':
                    node['upper'] = F(0)
                    break
                if node['kind'] == 'split':
                    pending.extend((node['left'], node['right']))
        elif attack == 'false_witness':
            fake['witness'] = (F(-1),)+fake['witness'][1:]
        elif attack == 'false_dual':
            fake['tree'] = {'kind': 'empty', 'dual': (F(0),)*len(model.inequalities(tuple((F(0), F(1)) for _ in model.base)))}
        elif attack == 'weaken_accuracy':
            fake['gamma'] = F(100)
        else:
            fake['witness'] = tuple(map(float, fake['witness']))
        try:
            verify(model, fake, result['gamma'])
        except (AssertionError, KeyError):
            rejected.append(attack)
        else:
            raise AssertionError(f'forged certificate accepted: {attack}')
    unresolved = solve(certificates[0][0], F(11, 10), node_budget=1)
    assert unresolved['status'] == 'UNRESOLVED'
    empty_model = from_features(features, fixtures[0][1], cap=1)
    empty = solve(empty_model)
    assert empty['status'] == 'EMPTY_STATIC_CLASS' and verify(empty_model, empty, F(2)) == (F(0), 1)
    atomless = Model(2, (F(1), F(1)), (), (3, 1))
    atomless_result = solve(atomless, F(11, 10))
    assert verify(atomless, atomless_result, F(11, 10))[0] >= F(1, 16)
    # Zero-count contexts can still own a restriction on shared coefficients.
    unscored = Model(2, (1, 1, 1, 1), ((1, 0, 1, 0),), (3, 1, 0, 0), (((1,), 1),))
    unscored_result = solve(unscored, F(11, 10))
    unscored_upper, _ = verify(unscored, unscored_result, F(11, 10))
    assert unscored_result['likelihood_lower'] == unscored_upper == F(8, 81) < F(27, 256)
    negative_row = Model(2, (1, 1), ((1, 0), (0, 1)), (3, 1), (((-1, 0), -2),))
    negative_result = solve(negative_row, F(11, 10))
    assert verify(negative_row, negative_result, F(11, 10))[0] == F(27, 256)
    try:
        check_simplex_maximum(((F(0), F(1)),)*2, (3, 1), (F(1, 2),)*2)
    except AssertionError:
        kkt_rejected = True
    else:
        raise AssertionError('suboptimal box optimizer passed KKT authority')
    return {'status': 'PASS', 'scope': 'explicit rational mass atoms/base/counts/polyhedral coefficient domain',
            'exact_simplex_box_optimizer_grid_cases': water_cases, 'global_likelihood_brackets': rows,
            'forged_complete_tree_rejections': rejected, 'node_budget_exhaustion_returns_unresolved': True,
            'empty_coefficient_class_exact_dual_checked': True,
            'zero_count_context_retains_shared_resource_constraint': True,
            'negative_polyhedral_constraint_row_checked': True,
            'suboptimal_box_optimizer_rejected_by_exact_kkt': kkt_rejected,
            'not_claimed': ['exact attainment of the unbounded SUM optimum', 'polynomial work bound',
                            'unary-SUM parity conjecture proved', 'unknown dictionary or table acquisition',
                            'optimizer-reachable coefficient optimum', 'complete Reference Compiler or AMP certificate']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(), indent=2)+'\n'
    if args.write:
        root = Path(__file__).resolve().parents[2]
        (root/'evidence/minimal/FP_POSITIVE_CONE_LOSS_AUDIT.json').write_text(result, encoding='utf-8')
    print(result, end='')
