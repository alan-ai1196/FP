"""Exact fixture, independent finite-state oracles, structural and resource checks."""
from dataclasses import asdict
from fractions import Fraction as F
from itertools import product
from math import isqrt
import argparse
import json
from pathlib import Path
from random import Random

from learner import FitWork, Learner, words


def run_word(initial, step, word):
    state = initial
    for a in word:
        state = step(state, a)
    return state


def boundary(state, a):
    x, y, z = state
    if a == "q":
        return y, z, x
    if a == "m":
        return -x, -y, -z
    return x, y, -x - y - z


def parity(state, a):
    return -state if a == "m" else state


def observations(alphabet, capacity, initial, step, output):
    # Only (raw word, binary outcome) crosses into the learner.
    for w in words(alphabet, 2 * capacity - 1):
        clean = int(output(run_word(initial, step, w)) > 0)
        for y in (clean, 1 - clean, clean, clean):
            yield w, y


def table_fit(learner):
    """Independent categorical learner using all short suffix tests, no linear operators."""
    short = list(words(learner.alphabet, learner.capacity - 1))
    signatures = {}
    probes = 0
    for p in words(learner.alphabet, learner.capacity):
        values = []
        for s in short:
            zeros, ones = learner.counts[p + s]
            assert zeros != ones
            values.append(1 if ones > zeros else -1)
        signatures[p] = tuple(values)
        probes += len(values)
    representatives = {}
    for p in short:
        representatives.setdefault(signatures[p], p)
    keys = list(representatives)
    index = {key: i for i, key in enumerate(keys)}
    table = [[index[signatures[p + a]] for a in learner.alphabet]
             for p in representatives.values()]
    for p in short:
        assert table[index[signatures[p]]] == [index[signatures[p + a]] for a in learner.alphabet]
    return table, [key[0] for key in keys], probes


def reference_graph(alphabet, initial, step, output):
    states = [initial]
    index = {initial: 0}
    table = []
    for state in states:
        row = []
        for a in alphabet:
            after = step(state, a)
            if after not in index:
                index[after] = len(states)
                states.append(after)
            row.append(index[after])
        table.append(row)
    return table, tuple(output(s) for s in states)


def column_orbit(table, output):
    # Precompose output tests with letters; evaluate the whole column on every state.
    orient = lambda column: tuple(x * column[0] for x in column)
    lines = [orient(output)]
    seen = set(lines)
    for column in lines:
        for a in range(len(table[0])):
            successor = orient([column[row[a]] for row in table])
            if successor not in seen:
                seen.add(successor)
                lines.append(successor)
    return lines


def certify_equivalence(alphabet, machine, table, output):
    pairs = [(machine.initial, 0)]
    seen = set(pairs)
    for state, index in pairs:
        assert state[0] == output[index]
        for ai, a in enumerate(alphabet):
            nxt = machine.step(state, a), table[index][ai]
            if nxt not in seen:
                seen.add(nxt)
                pairs.append(nxt)
    return len(pairs)


def fixture(alphabet, capacity, initial, step, output):
    learner = Learner(alphabet, capacity)
    prequential = F(0)
    for w, y in observations(alphabet, capacity, initial, step, output):
        prequential += (learner.forecast(w) - y) ** 2
        learner.observe(w, y)
    work = FitWork()
    model = learner.fit(work, min_visits=4)
    assert model is not None and model.amplitude == F(1, 2)
    table, labels, probes = table_fit(learner)
    source, values = reference_graph(alphabet, initial, step, output)
    lines = column_orbit(source, values)
    assert certify_equivalence(alphabet, model, source, values) == len(source)
    assert certify_equivalence(alphabet, model, table, labels) == len(table)
    # Distinct complete rows from the independent oracle, even if its states are redundant.
    residuals = len(set(zip(*lines, strict=True)))
    learned = {a: [len(col) for col in model.transitions[a]] for a in alphabet}
    val = []
    for raw in product(alphabet, repeat=2 * capacity):
        w = "".join(raw)
        assert w not in learner.counts
        clean = int(output(run_word(initial, step, w)) > 0)
        val.extend((w, y) for y in (1 - clean, clean, clean, clean))
    assert not learner.select(model, val, tap_price=1)
    assert learner.select(model, val, tap_price=0)
    expected = sum((learner.forecast(w) - y) ** 2 for w, y in val) / len(val)
    assert expected == F(3, 16)
    # Fresh long words are checked against the source, including an unseen composition.
    unseen = [alphabet[-1] + alphabet[0] * (2 * capacity) + a for a in alphabet]
    for w in unseen:
        assert learner.forecast(w) == (1 + F(1, 2) * output(run_word(initial, step, w))) / 2
    state_bits = len(model.initial)
    b = 1 + isqrt(state_bits ** state_bits).bit_length()
    taps = sum(map(sum, learned.values()))
    visits = sum(sum(pair) for pair in learner.counts.values())
    return dict(rank=state_bits, deterministic_states=residuals, signed_copy_width=len(lines),
                taps_per_output=learned, acquisition_words=len(learner.counts), training_labels=visits,
                training_input_symbols=sum(len(w) * sum(c) for w, c in learner.counts.items()),
                prefit_brier=str(prequential / visits), fitted_brier=str(expected),
                validation_labels=len(val), validation_taps=sum(model.taps(w) for w, _ in val),
                integer_nonzero_parameters=taps,
                model_payload_bits=state_bits + len(alphabet) * state_bits ** 2 + b * taps,
                fit_work=asdict(work), categorical_signature_probes=probes,
                categorical_transition_entries=len(table) * len(alphabet)), (table, labels, model)


def grid():
    cases = 0
    equality = 0
    for d in range(2, 5):
        cube = list(product((-1, 1), repeat=d))
        for coefficients in product(range(-2, 3), repeat=d):
            if sum(c != 0 for c in coefficients) < 2:
                continue
            count = sum(abs(sum(c * x for c, x in zip(coefficients, v))) == 1 for v in cube)
            assert 4 * count <= 3 * len(cube)
            equality += 4 * count == 3 * len(cube)
            cases += 1
    return dict(forms=cases, exact_boundary_cases=equality)


def small_automata():
    checks = 0
    for transitions in product(range(2), repeat=4):
        for signs in product((-1, 1), repeat=2):
            for start in range(2):
                table = [transitions[:2], transitions[2:]]
                def step(state, a):
                    return table[state][int(a)]
                t = Learner("01", 2)
                for w in words("01", 3):
                    t.observe(w, int(signs[run_word(start, step, w)] > 0))
                model = t.fit(FitWork())
                assert model is not None
                graph, labels = reference_graph("01", start, step, signs.__getitem__)
                certify_equivalence("01", model, graph, labels)
                lines = column_orbit(graph, labels)
                # For at most two rows, different projective sign columns are independent.
                assert len(model.initial) == len(lines)
                checks += 1
    return checks


def passive():
    rng = Random(91037)
    learner = Learner("qmv", 3)
    pool = list(words("qmv", 5))
    initial = (1, 1, -1)
    seen_letters = 0
    for _ in range(32768):
        w = rng.choice(pool)
        assert learner.forecast(w) == F(1, 2)
        y = int(boundary_sign(initial, w) > 0) ^ int(rng.randrange(4) == 0)
        learner.observe(w, y)
        seen_letters += len(w)
    model = learner.fit(FitWork())
    assert model is not None
    table, output = reference_graph("qmv", initial, boundary, lambda s: s[0])
    visited = certify_equivalence("qmv", model, table, output)
    excess = (model.amplitude - F(1, 2)) ** 2 / 4
    return dict(seed=91037, iid_pseudorandom_episodes=32768, input_symbols=seen_letters,
                min_visits=min(sum(c) for c in learner.counts.values()), inferred_rank=len(model.initial),
                paired_reachable_states=visited, calibration=str(model.amplitude), fresh_excess_brier=str(excess))


def boundary_sign(initial, word):
    return run_word(initial, boundary, word)[0]


def failures():
    # Every one-feature split has zero squared-loss gain on balanced XOR.
    rows = list(product(range(2), repeat=2))
    means = [[F(sum((x ^ y) for x, y in rows if (x, y)[j] == b), 2)
              for b in range(2)] for j in range(2)]
    assert means == [[F(1, 2)] * 2] * 2
    # Two equally calibrated fits with different evidence multiplicities.
    fits = []
    for copies in (1, 3):
        t = Learner("a", 1)
        for w in ("", "a"):
            for y in [1, 1, 1, 0] * copies:
                t.observe(w, y)
        before = t.fit(FitWork())
        for _ in range(3):
            t.observe("", 0)
        after = t.fit(FitWork())
        fits.append((before.forecast(""), after.forecast("")))
    assert fits[0][0] == fits[1][0] and fits[0][1] != fits[1][1]
    bad = Learner("a", 1)
    assert bad.fit(FitWork()) is None
    for w, y in [("", 0), ("", 1), ("a", 1)]:
        bad.observe(w, y)
    assert bad.fit(FitWork()) is None
    # A capacity-one fit is tested at its own horizon; an unseen longer exception survives it.
    for w in ("", "a"):
        bad.observe(w, 1)
    assert bad.fit(FitWork()) is not None
    return dict(unary_XOR_means=[[str(v) for v in row] for row in means],
                forecasts_before_and_after=[[str(v) for v in row] for row in fits])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r4-root", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not __debug__:
        parser.error("the audit requires assertions")
    p, p_models = fixture("qm", 2, -1, parity, lambda state: state)
    six, six_models = fixture("qmv", 4, (1, 1, -1), boundary, lambda state: state[0])
    assert (p["rank"], p["deterministic_states"], p["signed_copy_width"]) == (1, 2, 1)
    assert (six["rank"], six["deterministic_states"], six["signed_copy_width"]) == (3, 6, 4)
    result = dict(parity=p, six_state=six, cube=grid(), all_two_state_sources=small_automata(),
                  passive=passive(), failures=failures())
    if args.check:
        expected = json.loads(Path(__file__).with_name("result.json").read_text(encoding="utf-8"))
        assert result == expected
    print(json.dumps(result, indent=2))
    if args.r4_root:
        from positive_comparison import compare
        print(json.dumps({"R4": [compare(args.r4_root, a, *models) for a, models in
                                  [("qm", p_models), ("qmv", six_models)]]}, indent=2))


if __name__ == "__main__":
    main()
