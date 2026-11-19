"""Learn signed transformations from a reset word and a post-forecast binary label."""
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import gcd, lcm


def words(alphabet, depth):
    for length in range(depth + 1):
        for letters in product(alphabet, repeat=length):
            yield "".join(letters)


@dataclass
class FitWork:
    cell_lookups: int = 0
    divisions: int = 0
    multiply_subtracts: int = 0
    replay_letters: int = 0
    replay_taps: int = 0


def normalize(row, pivot, work):
    work.divisions += len(row)
    return [x / pivot for x in row]


def subtract(row, multiple, other, work):
    work.multiply_subtracts += len(row)
    return [x - multiple * y for x, y in zip(row, other, strict=True)]


def basis(short, table, limit, work):
    echelon = {}
    selected = []
    for prefix in short:
        row = [Fraction(table[prefix + suffix]) for suffix in short]
        work.cell_lookups += len(row)
        for j in sorted(echelon):
            if row[j]:
                row = subtract(row, row[j], echelon[j], work)
        pivot = next((j for j, value in enumerate(row) if value), None)
        if pivot is not None:
            if len(selected) == limit:
                return None
            echelon[pivot] = normalize(row, row[pivot], work)
            selected.append(prefix)
    return selected, [short[j] for j in sorted(echelon)]


def solve(left, right, work):
    """Solve all right-hand sides in one exact elimination."""
    n = len(left)
    rows = [list(map(Fraction, a + b)) for a, b in zip(left, right, strict=True)]
    for j in range(n):
        i = next(i for i in range(j, n) if rows[i][j])
        rows[j], rows[i] = rows[i], rows[j]
        rows[j] = normalize(rows[j], rows[j][j], work)
        for i, row in enumerate(rows):
            if i != j and row[j]:
                rows[i] = subtract(row, row[j], rows[j], work)
    return [row[n:] for row in rows]


def integer_column(values):
    scale = lcm(*(v.denominator for v in values))
    weights = [int(v * scale) for v in values]
    divisor = gcd(*weights)
    if not divisor:
        raise ValueError("zero column cannot encode a sign")
    return tuple((j, w // divisor) for j, w in enumerate(weights) if w)


@dataclass(frozen=True)
class Machine:
    initial: tuple
    transitions: dict
    amplitude: Fraction

    def step(self, state, letter):
        updated = []
        for column in self.transitions[letter]:
            if len(column) == 1:
                j, weight = column[0]
                updated.append(state[j] if weight > 0 else -state[j])
            else:
                total = sum(w if state[j] > 0 else -w for j, w in column)
                updated.append(1 if total >= 0 else -1)
        return tuple(updated)

    def state(self, word):
        state = self.initial
        for letter in word:
            state = self.step(state, letter)
        return state

    def forecast(self, word):
        return (1 + self.amplitude * self.state(word)[0]) / 2

    def taps(self, word):
        return sum(len(column) for letter in word for column in self.transitions[letter])


class Learner:
    def __init__(self, alphabet, capacity):
        self.alphabet = tuple(alphabet)
        if not self.alphabet or len(set(self.alphabet)) != len(self.alphabet):
            raise ValueError("alphabet must be nonempty and distinct")
        if any(not isinstance(a, str) or len(a) != 1 for a in self.alphabet):
            raise ValueError("use one character per symbol")
        if not isinstance(capacity, int) or capacity < 1:
            raise ValueError("capacity must be a positive integer")
        self.capacity = capacity
        self.counts = {}
        self.published = None

    def forecast(self, word):
        if self.published is None:
            return Fraction(1, 2)
        return self.published.forecast(word)

    def observe(self, word, label):
        if label not in (0, 1) or any(a not in self.alphabet for a in word):
            raise ValueError("example outside the declared interface")
        if len(word) <= 2 * self.capacity - 1:
            cell = self.counts.setdefault(word, [0, 0])
            cell[label] += 1

    def fit(self, work, min_visits=1):
        if min_visits < 1:
            raise ValueError("min_visits must be positive")
        table = {}
        agreement = 0
        total = 0
        for w in words(self.alphabet, 2 * self.capacity - 1):
            zeros, ones = self.counts.get(w, (0, 0))
            if zeros + ones < min_visits or zeros == ones:
                return None
            table[w] = 1 if ones > zeros else -1
            total += zeros + ones
            agreement += abs(ones - zeros)
        short = list(words(self.alphabet, self.capacity - 1))
        indices = basis(short, table, self.capacity, work)
        if indices is None:
            return None
        prefixes, suffixes = indices
        left = [[table[p + s] for s in suffixes] for p in prefixes]
        right = [[table[p + a + s] for a in self.alphabet for s in suffixes]
                 for p in prefixes]
        r = len(prefixes)
        work.cell_lookups += (1 + len(self.alphabet)) * r * r + r
        solution = solve(left, right, work)
        transitions = {}
        for i, a in enumerate(self.alphabet):
            transitions[a] = tuple(integer_column([row[i * r + j] for row in solution])
                                   for j in range(r))
        model = Machine(tuple(table[s] for s in suffixes), transitions,
                        Fraction(agreement, total))
        for w, target in table.items():
            work.replay_letters += len(w)
            work.replay_taps += model.taps(w)
            if model.state(w)[0] != target:
                return None
        return model

    def select(self, candidate, validation, tap_price=0, horizon=1, fixed_charge=0):
        """Price a frozen challenger against a fair forecast on arriving validation events."""
        if candidate is None:
            return False
        if min(tap_price, fixed_charge) < 0 or horizon <= 0:
            raise ValueError("invalid resource prices or horizon")
        gain = Fraction(0)
        taps = 0
        n = 0
        for word, label in validation:
            p = candidate.forecast(word)
            event_taps = candidate.taps(word)
            gain += Fraction(1, 4) - (label - p) ** 2
            taps += event_taps
            n += 1
        if not n:
            raise ValueError("empty validation block")
        use = horizon * (gain - tap_price * taps) > n * fixed_charge
        self.published = candidate if use else None
        return use
