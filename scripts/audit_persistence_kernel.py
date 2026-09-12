"""Exact bounded-wealth and short filtration adversaries, without Runtime claims.

The independent tree enumerations check finite null laws and adaptive past-only
policies. They are not evidence that an external stream follows such a law.
No static FP architecture or power constant is added by this audit.
"""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction as F
from itertools import product
from math import comb
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src/reference_compiler'))

from fp_reference.core import ContractError
from fp_reference.persistence import PersistenceContract, PersistenceRule, next_wealth, threshold_crossed
from fp_reference.semantics import ArithmeticUnresolved


BITS = 512


def rule(**changes):
    initial = PersistenceRule('linear', 1, 8, F(1, 20), F(1, 2), F(2), 16, 12)
    return replace(initial, **changes)


def rejects(fn, error=ContractError):
    try:
        fn()
    except error:
        return
    raise AssertionError(f'expected {error.__name__}')


def independent_floor(value, bits):
    scale = 2**bits
    return F(value.numerator*scale//value.denominator, scale)


def audit_contracts():
    cases = 0
    invalid = {'epoch_events': (0, -1, True, F(1)),
               'max_epochs': (0, -1, True, 1.0),
               'log_terms': (0, -1, True, 1.0),
               'wealth_grid_bits': (-1, True, F(1)),
               'alpha': (F(0), F(1), F(-1), 0.1, True),
               'bet': (F(-1), F(1), 0.5, False),
               'bound': (F(0), F(-1), 1.0, True),
               'rule_id': ('', 1, True)}
    for field, values in invalid.items():
        for value in values:
            rejects(lambda field=field, value=value: rule(**{field: value}))
            cases += 1
    valid = rule(bet=0, bound=2)
    assert type(valid.bet) is F and type(valid.bound) is F
    rejects(lambda: setattr(valid, 'bet', F(1)), FrozenInstanceError)
    declarations = [valid]
    registered = PersistenceContract(F(1, 10), declarations)
    declarations.clear()
    assert registered.rules == (valid,)
    rejects(lambda: PersistenceContract(F(1, 10), (valid, valid)))
    rejects(lambda: PersistenceContract(F(1, 100), (valid,)))
    for invalid_alpha in (0, 1, -1, 0.1, True):
        rejects(lambda invalid_alpha=invalid_alpha: PersistenceContract(invalid_alpha, ()))
        cases += 1
    rejects(lambda: PersistenceContract(F(1, 10), (object(),)))

    class FractionSubclass(F):
        pass

    for value in (1, True, 1.0, FractionSubclass(1), F(-1)):
        rejects(lambda value=value: next_wealth(value, F(0), valid, bit_limit=BITS))
        cases += 1
    for value in (0, True, 0.0, FractionSubclass(0)):
        rejects(lambda value=value: next_wealth(F(1), value, valid, bit_limit=BITS))
        cases += 1
    for value in (F(-3), F(3)):
        rejects(lambda value=value: next_wealth(F(1), value, valid, bit_limit=BITS))
        cases += 1
    rejects(lambda: next_wealth(F(20), F(0), valid, bit_limit=BITS))
    rejects(lambda: next_wealth(F(1), F(0), rule(wealth_grid_bits=64), bit_limit=32), ArithmeticUnresolved)
    rejects(lambda: next_wealth(F(1), F(0), valid, bit_limit=True))
    rejects(lambda: threshold_crossed(F(1 << 31), F(1, 2), bit_limit=32), ArithmeticUnresolved)
    for alpha in (F(0), F(1), F(-1), 0.05, True):
        rejects(lambda alpha=alpha: threshold_crossed(F(1), alpha, bit_limit=BITS))
        cases += 1
    return cases


def audit_floor():
    cases = 0
    for bet, bound, bits in product((F(0), F(1, 4), F(1, 2), F(7, 8)),
                                    (F(1), F(2)), (0, 1, 4, 16)):
        registered = rule(bet=bet, bound=bound, wealth_grid_bits=bits)
        for wealth, fraction in product((F(0), F(1, 17), F(1, 3), F(1), F(7, 2), F(19)),
                                        (F(-1), F(-3, 4), F(-1, 4), F(0), F(1, 4), F(3, 4), F(1))):
            gain = bound*fraction
            raw = wealth*(1+bet*gain/bound)
            result = next_wealth(wealth, gain, registered, bit_limit=BITS)
            assert result == independent_floor(raw, bits)
            assert F(0) <= result <= raw < result+F(1, 2**bits)
            assert result < 2/registered.alpha
            if wealth == 0:
                assert result == 0
            cases += 1
    # The true score can be larger than the input lower score. Direction of
    # enclosure is essential; floor is below the original, unfloored process.
    for lower, true_gain in product((F(i, 4) for i in range(-8, 9)), repeat=2):
        if lower > true_gain:
            continue
        result = next_wealth(F(3), lower, rule(), bit_limit=BITS)
        assert result <= F(3)*(1+rule().bet*true_gain/rule().bound)
        cases += 1
    for exponent, bits in product((1, 4, 20), (0, 8, 24)):
        registered = rule(alpha=F(1, 2**exponent), wealth_grid_bits=bits)
        previous = F(2**exponent)-F(1, 2**bits)
        result = next_wealth(previous, registered.bound, registered, bit_limit=BITS)
        assert result.numerator.bit_length() <= exponent+bits+2
        assert result < F(2)/registered.alpha
        cases += 1
    assert next_wealth(F(1, 8), F(-2), rule(wealth_grid_bits=0), bit_limit=BITS) == 0
    assert next_wealth(F(0), F(2), rule(wealth_grid_bits=0), bit_limit=BITS) == 0
    for numerator in range(80):
        wealth = F(numerator, 4)
        assert threshold_crossed(wealth, F(1, 7), bit_limit=BITS) == (wealth >= 7)
        cases += 1
    return cases


def audit_null_tree(*, adaptive_bets, bits, depth=8):
    """An exact law at every node, with choices depending on past signs only."""
    alpha = F(1, 4)
    leaves, local_checks = [], 0

    def walk(history, wealth, probability, stopped):
        nonlocal local_checks
        if len(history) == depth:
            leaves.append((probability, wealth, stopped))
            return
        if stopped:
            # Remaining external coin flips still exist; storing one combined
            # leaf here is exact marginalization after a valid stopping time.
            leaves.append((probability, wealth, True))
            return
        successes = sum(history)
        positive = F(1+(successes % 2))
        negative = F(1+((len(history)+successes) % 2))
        p_positive = negative/(positive+negative)
        bet = (F(0), F(1, 4), F(1, 2), F(3, 4))[(len(history)+successes) % 4] if adaptive_bets else F(3, 4)
        registered = rule(alpha=alpha, bet=bet, wealth_grid_bits=bits)
        descendants = []
        for sign, gain, chance in ((1, positive, p_positive), (0, -negative, 1-p_positive)):
            lower = max(-registered.bound, gain-F(1, 32))
            next_value = next_wealth(wealth, lower, registered, bit_limit=BITS)
            assert next_value == independent_floor(wealth*(1+bet*lower/registered.bound), bits)
            crossed = next_value >= 1/alpha
            descendants.append((sign, next_value, chance, crossed))
        assert p_positive*positive+(1-p_positive)*(-negative) == 0
        assert sum((chance*value for _, value, chance, _ in descendants), F(0)) <= wealth
        local_checks += 1
        for sign, value, chance, crossed in descendants:
            walk(history+(sign,), value, probability*chance, crossed)

    walk((), F(1), F(1), False)
    assert sum((chance for chance, _, _ in leaves), F(0)) == 1
    expectation = sum((chance*value for chance, value, _ in leaves), F(0))
    crossing = sum((chance for chance, _, stopped in leaves if stopped), F(0))
    assert expectation <= 1 and crossing <= alpha
    return {'adaptive_past_only_bets': adaptive_bets, 'grid_bits': bits,
            'conditional_null_checks': local_checks, 'terminal_nodes': len(leaves),
            'crossing_probability': str(crossing), 'stopped_expectation': str(expectation)}


def audit_global_alpha():
    # The second identity is admitted using only the first two outcomes. All
    # live identities share each later observation: independence is not used.
    total, false_crossing, paths, allocations = F(3, 8), F(0), 0, set()
    for outcomes in product((F(-1), F(1)), repeat=8):
        entries = [(rule(rule_id='first', alpha=F(1, 4), bound=F(1), bet=F(3, 4)), F(1), False)]
        spent = F(1, 4)
        for t, gain in enumerate(outcomes):
            if t == 2 and outcomes[0] == outcomes[1]:
                alpha = F(1, 8) if outcomes[0] > 0 else F(1, 16)
                entries.append((rule(rule_id='later', alpha=alpha, bound=F(1), bet=F(7, 8)), F(1), False))
                spent += alpha
            updated = []
            for registered, wealth, stopped in entries:
                value = wealth if stopped else next_wealth(wealth, gain, registered, bit_limit=BITS)
                updated.append((registered, value, stopped or value >= 1/registered.alpha))
            entries = updated
            assert spent <= total
        allocations.add(str(spent))
        false_crossing += F(any(stopped for _, _, stopped in entries), 2**8)
        paths += 1
    assert 0 < false_crossing <= total
    return {'complete_shared_observation_paths': paths, 'global_alpha': str(total),
            'actual_spending_values': sorted(allocations), 'any_false_crossing_probability': str(false_crossing)}


def audit_unsound_shortcuts():
    # Under fair +/-1, outcome-adaptive bet and skipping negatives both replace
    # the legal negative factor 1/2 by 1. Four positive outcomes cross level 4.
    bad_crossing = sum((F(comb(8, k), 2**8) for k in range(4, 9)), F(0))
    assert bad_crossing == F(163, 256) > F(1, 4)
    assert F(1, 2)*F(3, 2)+F(1, 2)*F(1) == F(5, 4) > 1

    # Round each ordinary product upward to an integer under a bounded zero-
    # mean gain law. This is the opposite numerical direction from the kernel.
    upward_crossing = F(0)
    for gains in product((F(-1, 3), F(1, 3)), repeat=8):
        wealth, crossed = F(1), False
        for gain in gains:
            if crossed:
                break
            raw = wealth*(1+F(1, 2)*gain)
            wealth = F(-((-raw.numerator)//raw.denominator))
            crossed = wealth >= 4
        upward_crossing += F(crossed, 2**8)
    assert upward_crossing > F(1, 4)

    # Every independent block has at least the all-positive crossing event.
    # Refunding the same alpha and restarting sixteen times violates lifetime
    # control, irrespective of additional crossing paths in each block.
    restart_lower = 1-F(255, 256)**16
    assert F(3, 2)**8 > 20 and restart_lower > F(1, 20)
    return {'outcome_adaptive_bet_one_step_mean': '5/4',
            'outcome_adaptive_bet_or_loss_skipping_crossing': str(bad_crossing),
            'upward_integer_rounding_crossing': str(upward_crossing),
            'wrong_alpha_for_previous_three': '1/4',
            'refunded_alpha': '1/20', 'refund_restart_blocks': 16,
            'refund_crossing_probability_lower': str(restart_lower)}


def audit():
    invalid = audit_contracts()
    pointwise = audit_floor()
    trees = [audit_null_tree(adaptive_bets=adaptive, bits=bits)
             for adaptive, bits in product((False, True), (0, 4, 16))]
    return {'status': 'PASS',
            'scope': 'exact lower-wealth kernel and finite declared null-law audits; no Runtime authority',
            'invalid_registration_or_argument_cases': invalid,
            'pointwise_floor_bound_and_threshold_cases': pointwise,
            'exact_conditional_null_trees': trees,
            'global_error_composition': audit_global_alpha(),
            'reproduced_unsound_shortcuts': audit_unsound_shortcuts(),
            'not_claimed': ['freshness or lineage enforced by this helper',
                            'external corpus obeys an audited probability law',
                            'positive power under wealth quantization',
                            'reference/AMP bridge or installation authorization']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = audit()
    if args.write:
        (ROOT/'evidence/minimal/FP_PERSISTENCE_KERNEL_AUDIT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
