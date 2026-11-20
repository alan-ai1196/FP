"""Fit scalar forecast updates and propagate a finite-sample interval for their laws."""
from fractions import Fraction as F


SQUARE = [(F(0), F(0)), (F(1), F(0)), (F(1), F(1)), (F(0), F(1))]


def step(endpoints, value):
    lo, hi = endpoints
    return lo + (hi - lo) * value


def bounded(value):
    return max(F(0), min(F(1), value))


def fit_symbol(pairs):
    """Each pair holds the empirical prefix mean, child mean and child label count."""
    if not pairs:
        return (F(1, 2), F(1, 2))
    weight = sum(n for _, _, n in pairs)
    mean_x = sum(n*x for x, _, n in pairs) / weight
    mean_y = sum(n*y for _, y, n in pairs) / weight
    variance = sum(n*(x-mean_x)**2 for x, _, n in pairs)
    if not variance:
        return (mean_y, mean_y)
    slope = sum(n*(x-mean_x)*(y-mean_y) for x, y, n in pairs) / variance
    intercept = mean_y - slope*mean_x
    unconstrained = (intercept, intercept+slope)
    if all(0 <= v <= 1 for v in unconstrained):
        return unconstrained

    candidates = []
    for begin, end in zip(SQUARE, SQUARE[1:] + SQUARE[:1], strict=True):
        directions = [(step(end, x) - step(begin, x), y-step(begin, x), n) for x, y, n in pairs]
        denom = sum(n*d*d for d, _, n in directions)
        t = bounded(sum(n*d*res for d, res, n in directions) / denom) if denom else F(0)
        point = tuple(a + t*(b-a) for a, b in zip(begin, end, strict=True))
        loss = sum(n*(step(point, x) - y)**2 for x, y, n in pairs)
        candidates.append((loss, point))
    return min(candidates)[1]


def clip_polygon(poly, a, b, limit):
    """Intersect a convex polygon, segment or singleton with a*x+b*y <= limit."""
    kept = []
    for start, end in zip(poly, poly[1:] + poly[:1], strict=True):
        s = a*start[0] + b*start[1] - limit
        t = a*end[0] + b*end[1] - limit
        if s <= 0:
            kept.append(start)
        if s*t < 0:
            alpha = s / (s-t)
            kept.append(tuple(x+alpha*(y-x) for x, y in zip(start, end, strict=True)))
    return list(dict.fromkeys(kept))


def feasible_endpoints(interval_pairs):
    vertices = []
    for sign in (1, -1):
        poly = clip_polygon(SQUARE, sign, -sign, 0)
        for (xl, xu), (yl, yu) in interval_pairs:
            lower_at, upper_at = (xl, xu) if sign == 1 else (xu, xl)
            poly = clip_polygon(poly, 1-lower_at, lower_at, yu)
            poly = clip_polygon(poly, -(1-upper_at), -upper_at, -yl)
        vertices.extend(poly)
    return tuple(dict.fromkeys(vertices))


def learn(counts, radii, alphabet):
    """Counts map words to (number of labels, number positive) at the current checkpoint."""
    means = {w: F(h, n) for w, (n, h) in counts.items()}
    intervals = {w: (bounded(y-radii[w]), bounded(y+radii[w])) for w, y in means.items()}
    pairs = {a: [] for a in alphabet}
    boxes = {a: [] for a in alphabet}
    for word in counts:
        if word and word[:-1] in counts:
            parent, symbol = word[:-1], word[-1]
            pairs[symbol].append((means[parent], means[word], counts[word][0]))
            boxes[symbol].append((intervals[parent], intervals[word]))
    points = {a: fit_symbol(pairs[a]) for a in pairs}
    vertices = {a: feasible_endpoints(boxes[a]) for a in boxes}
    certificate = vertices if all(vertices.values()) else None
    return means.get("", F(1,2)), points, intervals.get("", (F(0), F(1))), certificate


def propagate(vertices, interval):
    if not vertices:
        return F(0), F(1)
    extrema = [step(point, x) for point in vertices for x in interval]
    return min(extrema), max(extrema)
