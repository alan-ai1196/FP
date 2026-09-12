"""Complete ordered finite native syntax, with a checked explicit DFS cursor.

The planner has no proof authority. Checked transitions count all alternatives
independently of the planner's proposed action and bind each selected ordinal.
No current-value, gradient, support or graph-isomorphism quotient is taken.
Runtime must own the initial cursor and every subsequent transition to claim
coverage; a caller-created cursor, action or helper result proves nothing.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from .core import ContractError, natural
from .program import Binding, Node, Product, Program, SemanticRules, Source, State, Sum, Term


@dataclass(frozen=True)
class GrammarLimits:
    nodes: int
    SUMs: int
    PRODUCTs: int
    edges: int
    slots: int

    def __post_init__(self):
        for key in ('nodes', 'SUMs', 'PRODUCTs', 'edges', 'slots'):
            natural(getattr(self, key), f'finite grammar {key}')

    def admits(self, program: Program) -> bool:
        counts = program.counts()
        return all(counts[key] <= getattr(self, key) for key in ('nodes', 'SUMs', 'PRODUCTs', 'edges', 'slots'))


@dataclass(frozen=True)
class Frame:
    next_output: int = 0
    next_child: int = 0


@dataclass(frozen=True)
class GrammarCursor:
    slot_count: int = 0
    nodes: tuple[Node, ...] = ()
    frames: tuple[Frame, ...] = (Frame(),)
    emitted: int = 0
    transitions: int = 0
    done: bool = False


@dataclass(frozen=True)
class GrammarAction:
    kind: str
    node: Node | None = None
    program: Program | None = None


def _mul(a, b, cap):
    if not a or not b:
        return 0
    return cap if a > cap//b else min(cap, a*b)


def _add(a, b, cap):
    return min(cap, a+b)


def _power(base, exponent, cap):
    value = min(1, cap)
    while exponent:
        if exponent & 1:
            value = _mul(value, base, cap)
        base = _mul(base, base, cap)
        exponent >>= 1
    return value


def _geometric(base, terms, cap):
    """min(cap, 1+base+...+base**(terms-1)), without huge hidden integers."""
    power, total, step_power, step_total = min(1, cap), 0, min(base, cap), min(1, cap)
    while terms:
        if terms & 1:
            total = _add(total, _mul(power, step_total, cap), cap)
            power = _mul(power, step_power, cap)
        step_total = _add(step_total, _mul(step_power, step_total, cap), cap)
        step_power = _mul(step_power, step_power, cap)
        terms >>= 1
    return total


def _factorial(n, cap):
    value = min(1, cap)
    for factor in range(2, n+1):
        value = _mul(value, factor, cap)
        if value == cap:
            break
    return value


def _prefix(cursor, rules):
    program = Program(cursor.nodes, cursor.slot_count, ())
    return program.node_types(rules), program.counts()


def output_count(cursor: GrammarCursor, rules: SemanticRules, cap: int) -> int:
    types, _ = _prefix(cursor, rules)
    value = _power(types.count(rules.readout_type), len(rules.base), cap)
    value = _mul(value, _factorial(len(rules.states), cap), cap)
    # Do not stop at saturation: a later absent body type makes the total zero.
    for state in rules.states:
        value = _mul(value, types.count(state.type_id), cap)
    return value


def child_count(cursor: GrammarCursor, rules: SemanticRules, limits: GrammarLimits, cap: int) -> int:
    if len(cursor.nodes) >= limits.nodes:
        return 0
    types, counts = _prefix(cursor, rules)
    remaining = limits.edges-counts['edges']
    value = min(cap, len(rules.sources)+len(rules.states))
    if counts['SUMs'] < limits.SUMs:
        for type_id in rules.sum_types:
            value = _add(value, _geometric(types.count(type_id)*cursor.slot_count, remaining+1, cap), cap)
    if counts['PRODUCTs'] < limits.PRODUCTs and remaining >= 2:
        for left, right, _ in rules.product_rules:
            value = _add(value, _mul(types.count(left), types.count(right), cap), cap)
    return value


def _indices(types, type_id):
    return tuple(i for i, value in enumerate(types) if value == type_id)


def _digits(rank, bases):
    values = []
    for base in reversed(bases):
        rank, value = divmod(rank, base)
        values.append(value)
    if rank:
        raise ContractError('ordinal is outside its complete native coordinate class')
    return tuple(reversed(values))


def _permutation(rank, n):
    remaining, result = list(range(n)), []
    while remaining:
        size = _factorial(len(remaining)-1, rank+1)
        digit, rank = divmod(rank, size)
        if digit >= len(remaining):
            raise ContractError('delayed-binding permutation ordinal is outside its class')
        result.append(remaining.pop(digit))
    return tuple(result)


def output_at(cursor: GrammarCursor, rules: SemanticRules, rank: int) -> Program:
    types, _ = _prefix(cursor, rules)
    heads = _indices(types, rules.readout_type)
    bodies = tuple(_indices(types, s.type_id) for s in rules.states)
    # Fastest coordinates are body choices in registered state order, then
    # binding permutation, then readout roots. All orderings remain distinct.
    body_digits = []
    for choices in reversed(bodies):
        rank, digit = divmod(rank, len(choices))
        body_digits.append(digit)
    body_digits.reverse()
    permutation_count = _factorial(len(rules.states), rank+1)
    rank, permutation_rank = divmod(rank, permutation_count)
    head_digits = _digits(rank, (len(heads),)*len(rules.base))
    order = _permutation(permutation_rank, len(rules.states))
    bindings = tuple(Binding(rules.states[i].state_id, bodies[i][body_digits[i]]) for i in order)
    return Program(cursor.nodes, cursor.slot_count, tuple(heads[i] for i in head_digits), bindings)


def node_at(cursor: GrammarCursor, rules: SemanticRules, limits: GrammarLimits, rank: int) -> Node:
    types, counts = _prefix(cursor, rules)
    if rank < len(rules.sources):
        return Source(rules.sources[rank].source_id)
    rank -= len(rules.sources)
    if rank < len(rules.states):
        return State(rules.states[rank].state_id)
    rank -= len(rules.states)
    if counts['SUMs'] < limits.SUMs:
        remaining = limits.edges-counts['edges']
        for type_id in rules.sum_types:
            parents = _indices(types, type_id)
            alphabet = len(parents)*cursor.slot_count
            count = _geometric(alphabet, remaining+1, rank+1)
            if rank >= count:
                rank -= count
                continue
            arity = 0
            if alphabet == 1:
                arity, rank = rank, 0
            elif alphabet:
                power = 1
                while rank >= power:
                    rank -= power
                    power *= alphabet
                    arity += 1
            digits = _digits(rank, (alphabet,)*arity)
            return Sum(type_id, tuple(Term(parents[digit//cursor.slot_count], digit % cursor.slot_count) for digit in digits))
    if counts['PRODUCTs'] < limits.PRODUCTs and limits.edges-counts['edges'] >= 2:
        for left_type, right_type, result in rules.product_rules:
            left, right = _indices(types, left_type), _indices(types, right_type)
            count = len(left)*len(right)
            if rank >= count:
                rank -= count
                continue
            i, j = divmod(rank, len(right))
            return Product(result, left[i], right[j])
    raise ContractError('planner requested a nonexistent native child')


def _rank_digits(digits, bases, cap):
    rank = 0
    for digit, base in zip(digits, bases):
        if not 0 <= digit < base:
            raise ContractError('native coordinate is outside its complete choice range')
        rank = _add(_mul(rank, base, cap), digit, cap)
    return rank


def _output_rank(program: Program, cursor: GrammarCursor, rules: SemanticRules, cap: int) -> int:
    types = program.validate(rules)
    if program.nodes != cursor.nodes or program.slot_count != cursor.slot_count:
        raise ContractError('planner substituted another native prefix or parameter class')
    heads = _indices(types, rules.readout_type)
    rank = _rank_digits(tuple(heads.index(h) for h in program.heads), (len(heads),)*len(rules.base), cap)
    available = [s.state_id for s in rules.states]
    permutation = 0
    for binding in program.bindings:
        digit = available.index(binding.state_id)
        permutation = _add(_mul(permutation, len(available), cap), digit, cap)
        available.pop(digit)
    rank = _add(_mul(rank, _factorial(len(rules.states), cap), cap), permutation, cap)
    by_id = {b.state_id: b.body for b in program.bindings}
    for state in rules.states:
        choices = _indices(types, state.type_id)
        rank = _add(_mul(rank, len(choices), cap), choices.index(by_id[state.state_id]), cap)
    return rank


def _node_rank(node: Node, cursor: GrammarCursor, rules: SemanticRules, limits: GrammarLimits, cap: int) -> int:
    # Native validation and complete budgets are independent of the planner.
    trial = Program(cursor.nodes+(node,), cursor.slot_count, ())
    trial.node_types(rules)
    if not limits.admits(trial):
        raise ContractError('planner child exceeds the declared native resources')
    if type(node) is Source:
        return next(i for i, s in enumerate(rules.sources) if s.source_id == node.source_id)
    if type(node) is State:
        return len(rules.sources)+next(i for i, s in enumerate(rules.states) if s.state_id == node.state_id)
    types, counts = _prefix(cursor, rules)
    rank = min(cap, len(rules.sources)+len(rules.states))
    remaining = limits.edges-counts['edges']
    if counts['SUMs'] < limits.SUMs:
        for type_id in rules.sum_types:
            parents = _indices(types, type_id)
            alphabet = len(parents)*cursor.slot_count
            if type(node) is Sum and node.type_id == type_id:
                rank = _add(rank, _geometric(alphabet, len(node.terms), cap), cap)
                digits = tuple(parents.index(t.parent)*cursor.slot_count+t.slot for t in node.terms)
                return _add(rank, _rank_digits(digits, (alphabet,)*len(digits), cap), cap)
            rank = _add(rank, _geometric(alphabet, remaining+1, cap), cap)
    if type(node) is Product and counts['PRODUCTs'] < limits.PRODUCTs and remaining >= 2:
        for left_type, right_type, result in rules.product_rules:
            left, right = _indices(types, left_type), _indices(types, right_type)
            if node.type_id == result and node.left in left and node.right in right:
                local = left.index(node.left)*len(right)+right.index(node.right)
                return _add(rank, local, cap)
            rank = _add(rank, _mul(len(left), len(right), cap), cap)
    raise ContractError('planner child does not belong to the registered native alphabet')


def plan(cursor: GrammarCursor, rules: SemanticRules, limits: GrammarLimits) -> GrammarAction:
    if cursor.done:
        return GrammarAction('done')
    frame = cursor.frames[-1]
    if output_count(cursor, rules, frame.next_output+1) > frame.next_output:
        return GrammarAction('emit', program=output_at(cursor, rules, frame.next_output))
    if child_count(cursor, rules, limits, frame.next_child+1) > frame.next_child:
        return GrammarAction('descend', node=node_at(cursor, rules, limits, frame.next_child))
    return GrammarAction('close')


def apply_checked(cursor: GrammarCursor, action: GrammarAction, rules: SemanticRules, limits: GrammarLimits) -> tuple[GrammarCursor, Program | None]:
    """An action cannot skip an ordinal, change an endpoint or close early."""
    if type(action) is not GrammarAction:
        raise ContractError('native planner must return a typed action')
    if cursor.done:
        if action != GrammarAction('done'):
            raise ContractError('native class is already exhausted')
        return cursor, None
    frame = cursor.frames[-1]
    outputs = output_count(cursor, rules, frame.next_output+1)
    children = child_count(cursor, rules, limits, frame.next_child+1)
    base = replace(cursor, transitions=cursor.transitions+1)
    if action.kind == 'emit':
        if type(action.program) is not Program or action.node is not None or outputs <= frame.next_output:
            raise ContractError('planner emitted outside the complete root class')
        if _output_rank(action.program, cursor, rules, frame.next_output+1) != frame.next_output:
            raise ContractError('planner skipped or repeated a completed native program')
        new_frame = replace(frame, next_output=frame.next_output+1)
        return replace(base, frames=cursor.frames[:-1]+(new_frame,), emitted=cursor.emitted+1), action.program
    if action.program is not None:
        raise ContractError('planner attached an unrelated program to a non-emission')
    if action.kind == 'descend':
        if outputs != frame.next_output or children <= frame.next_child or action.node is None:
            raise ContractError('planner skipped roots or descended beyond a complete prefix')
        if _node_rank(action.node, cursor, rules, limits, frame.next_child+1) != frame.next_child:
            raise ContractError('planner skipped or repeated a native child')
        new_frame = replace(frame, next_child=frame.next_child+1)
        return replace(base, nodes=cursor.nodes+(action.node,), frames=cursor.frames[:-1]+(new_frame, Frame())), None
    if action != GrammarAction('close') or outputs != frame.next_output or children != frame.next_child:
        raise ContractError('planner cannot declare an incompletely visited native prefix exhausted')
    if cursor.nodes:
        return replace(base, nodes=cursor.nodes[:-1], frames=cursor.frames[:-1]), None
    if cursor.slot_count < limits.slots:
        return replace(base, slot_count=cursor.slot_count+1, frames=(Frame(),)), None
    return replace(base, frames=(), done=True), None
