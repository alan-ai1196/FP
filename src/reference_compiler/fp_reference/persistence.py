"""Registered lower-wealth arithmetic, without persistence authority.

Runtime owns admission, fresh observations, predictable choices, lineage,
stopping and the global error ledger. These functions cannot attest to any
of them. In particular a deterministic unread corpus supplies no stochastic
law merely because this arithmetic runs on it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction as F

from .core import ContractError, natural
from .numerics import floor_nonnegative_dyadic
from .program import name, rational
from .semantics import _guard, _operation


@dataclass(frozen=True)
class PersistenceRule:
    rule_id: str
    epoch_events: int
    max_epochs: int
    alpha: F
    bet: F
    bound: F
    log_terms: int
    wealth_grid_bits: int
    # This fixed proposition includes the current mathematically defined
    # range-safe score on a failing attempt, then zeros after termination.
    # It cannot be replaced after seeing which computation succeeded.
    null_id: str = field(default='bounded-pre-context-stopped-reference-epoch-mean-v1', init=False)

    def __post_init__(self):
        name(self.rule_id, 'persistence rule ID')
        natural(self.epoch_events, 'registered events per persistence epoch', positive=True)
        natural(self.max_epochs, 'registered persistence horizon', positive=True)
        natural(self.log_terms, 'registered logarithm terms', positive=True)
        natural(self.wealth_grid_bits, 'registered wealth fractional bits')
        object.__setattr__(self, 'alpha', rational(self.alpha, 'identity alpha', positive=True))
        object.__setattr__(self, 'bet', rational(self.bet, 'predictable betting fraction'))
        object.__setattr__(self, 'bound', rational(self.bound, 'predictable gain bound', positive=True))
        if self.alpha >= 1 or self.bet >= 1:
            raise ContractError('persistence requires alpha < 1 and betting fraction < 1')


@dataclass(frozen=True)
class PersistenceContract:
    alpha_total: F
    rules: tuple[PersistenceRule, ...]

    def __post_init__(self):
        object.__setattr__(self, 'alpha_total', rational(self.alpha_total, 'global persistence alpha', positive=True))
        if self.alpha_total >= 1:
            raise ContractError('global persistence alpha must be less than one')
        rules = tuple(self.rules)
        if any(type(rule) is not PersistenceRule for rule in rules):
            raise ContractError('exact immutable persistence rule declarations required')
        if len({rule.rule_id for rule in rules}) != len(rules):
            raise ContractError('duplicate persistence rule ID')
        if any(rule.alpha > self.alpha_total for rule in rules):
            raise ContractError('one identity cannot exceed the entire global alpha budget')
        # Rule declaration is not an allocation. A rule can be admitted more
        # than once only if Runtime charges each new identity to its ledger.
        object.__setattr__(self, 'rules', rules)


def _exact(value, label, *, nonnegative=False):
    if type(value) is not F or nonnegative and value < 0:
        raise ContractError(f'{label} must be an exact {"nonnegative " if nonnegative else ""}Fraction')
    return value


def threshold_crossed(wealth: F, alpha: F, *, bit_limit: int) -> bool:
    """Exact guarded comparison with 1/alpha; no evidence identity is checked."""
    _exact(wealth, 'lower wealth', nonnegative=True)
    _exact(alpha, 'identity alpha')
    if not 0 < alpha < 1:
        raise ContractError('identity alpha must lie strictly between zero and one')
    natural(bit_limit, 'reference integer work limit', positive=True)
    return _operation(wealth, alpha, multiply=True, bit_limit=bit_limit) >= 1


def next_wealth(wealth: F, gain_lower: F, rule: PersistenceRule, *, bit_limit: int) -> F:
    """Floor one nonnegative linear factor to the registered dyadic grid.

For a proved true gain Y with -B <= gain_lower <= Y <= B, this update
is pointwise no larger than wealth*(1+bet*Y/B). Predictable bet and B
therefore preserve the mean-null supermartingale property. Floor losses
can destroy power or produce absorbing zero; no power bound is claimed.

Runtime must stop the identity at first crossing. Then the previous wealth
is < 1/alpha and this step's wealth is < 2/alpha. This is a bounded ordinary
wealth representation, not an ever-growing exact product. The helper does
not decide whether a new identity or another epoch may legally be admitted.
"""
    _exact(wealth, 'lower wealth', nonnegative=True)
    _exact(gain_lower, 'gain lower enclosure')
    if type(rule) is not PersistenceRule:
        raise ContractError('exact immutable persistence rule required')
    natural(bit_limit, 'reference integer work limit', positive=True)
    _guard(wealth, gain_lower, rule.alpha, rule.bet, rule.bound, bit_limit=bit_limit)
    inverse = F(rule.bound.denominator, rule.bound.numerator)
    scaled = _operation(gain_lower, inverse, multiply=True, bit_limit=bit_limit)
    # Comparing to +/-1 uses only the already guarded numerator/denominator.
    # Comparing the original two arbitrary Fractions could otherwise perform
    # unchecked cross-products larger than the reference integer work limit.
    if not -1 <= scaled <= 1:
        raise ContractError('gain enclosure lies outside its already proved predictable bound')
    if threshold_crossed(wealth, rule.alpha, bit_limit=bit_limit):
        raise ContractError('a crossed persistence identity must stop before another wealth update')
    if wealth == 0:
        return F(0)
    scaled = _operation(rule.bet, scaled, multiply=True, bit_limit=bit_limit)
    factor = _operation(F(1), scaled, multiply=False, bit_limit=bit_limit)
    if factor <= 0:
        raise ContractError('registered strict betting range failed positivity')
    raw = _operation(wealth, factor, multiply=True, bit_limit=bit_limit)
    return floor_nonnegative_dyadic(raw, bits=rule.wealth_grid_bits, bit_limit=bit_limit)
