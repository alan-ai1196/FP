"""Closed value exchange for indexed prediction proposals and results.

Only exact immutable primitives cross the delegated reference boundary.
The owner, this bounded reifier and the fixed numerical kernels are trusted;
helpers receive no owner, live source dictionary, live native record or old accepted result.
This is an alias/frame guarantee, not attestation of arbitrary Python code.
"""
from dataclasses import fields

from .core import ContractError
from .resources import ResourceExceeded


def _classes():
    # Lazy imports keep the passive arithmetic modules independent of the
    # owned exchange. The registry is closed: no import name comes from data.
    from .indexed_count import CountState
    from .indexed_execution import IndexedPredictionPlan
    from .query_projection import ProjectionPlan, BlockPlan
    return CountState, IndexedPredictionPlan, ProjectionPlan, BlockPlan


def reference_cells(n):
    # Counts plus all block vertices and table shapes.
    # A block path has sum(|V_b|-1)<=n-1, even when its original graph is dense.
    return 128*(n*(n-1)//2+n+16)


def _convert(value, *, cells, bits, decode):
    if type(cells) is not int or cells <= 0 or type(bits) is not int or bits <= 0:
        raise ContractError('registered indexed value traversal allowance required')
    bits = min(bits, 32768)
    registry = {cls.__name__: cls for cls in _classes()}
    remaining = cells

    def visit(item, depth):
        nonlocal remaining
        remaining -= 1
        if remaining < 0 or depth > 16:
            raise ResourceExceeded('indexed value traversal allowance exhausted')
        kind = type(item)
        if item is None or kind is bool:
            return item
        if kind is int:
            if item.bit_length() > max(63, bits):
                raise ResourceExceeded('indexed value integer allowance exhausted')
            return item
        if kind is str:
            if len(item) > 128:
                raise ResourceExceeded('indexed value string allowance exhausted')
            return item
        if decode:
            if kind is not tuple or not item or type(item[0]) is not str:
                raise ContractError('closed immutable indexed value required')
            if item[0] == 'tuple' and len(item) == 2 and type(item[1]) is tuple:
                if len(item[1]) > remaining:
                    raise ResourceExceeded('indexed value tuple allowance exhausted')
                return tuple(visit(child, depth+1) for child in item[1])
            if (item[0] == 'record' and len(item) == 3 and type(item[1]) is str
                    and item[1] in registry and type(item[2]) is tuple):
                cls = registry[item[1]]
                if len(item[2]) != len(fields(cls)):
                    raise ContractError('complete indexed record coordinates required')
                return cls(*(visit(child, depth+1) for child in item[2]))
            raise ContractError('unregistered indexed value constructor')
        if kind is tuple:
            if len(item) > remaining:
                raise ResourceExceeded('indexed value tuple allowance exhausted')
            return 'tuple', tuple(visit(child, depth+1) for child in item)
        if kind in registry.values():
            names = tuple(f.name for f in fields(kind))
            if vars(item).keys() != set(names):
                raise ContractError('complete closed indexed record required')
            return 'record', kind.__name__, tuple(visit(getattr(item, name), depth+1) for name in names)
        raise ContractError('mutable or unregistered indexed exchange value')

    result = visit(value, 0)
    if remaining < 0:
        raise ResourceExceeded('indexed value traversal allowance exhausted')
    return result


def freeze(value, *, cells, bits):
    return _convert(value, cells=cells, bits=bits, decode=False)


def thaw(value, *, cells, bits):
    return _convert(value, cells=cells, bits=bits, decode=True)


def same(a, b):
    """Exact primitive equality after bounded conversion, including types."""
    if type(a) is not type(b):
        return False
    if type(a) is tuple:
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def reference(n, budget_values, argument, *, bits):
    """Delegated port. Every argument and the successful result is a value.

    The metadata helper runs inside this fresh local object graph.
    Even a helper that retains or mutates its arguments/results receives no
    alias into the caller's complete state or an earlier accepted result.
    """
    from .indexed_execution import IndexedReferenceMachine, IndexedState
    from .indexed_relation import IndexedRelation, DecodeAllowance
    schema = IndexedRelation(n)
    machine = IndexedReferenceMachine(n, DecodeAllowance(*budget_values))
    limit = reference_cells(n)
    before, query = thaw(argument, cells=limit, bits=bits)
    result = machine.prepare_prediction(schema, schema.rules(), IndexedState(before),
        schema.source_row(query[0]*n+query[1]), bit_limit=bits)
    return freeze(result, cells=limit, bits=bits)


def predict(machine, program, rules, state, sources, *, bit_limit, execution_debit):
    """Private owner path: fix the actual input before invoking any helper."""
    from .indexed_execution import IndexedState, IndexedPredictionPlan, _execute_owned_prediction
    machine.require_program(program)
    if type(state) is not IndexedState or state.encoded.n != program.n or state.unit_count:
        raise ContractError('owned committed indexed predecessor required')
    query, _ = program.source_query(rules, sources)
    budget = machine.budget
    budget_values = budget.join_cells, budget.live_cells, budget.arithmetic, budget.integer_bits
    limit = reference_cells(program.n)
    argument = freeze((state.encoded, query), cells=limit, bits=bit_limit)
    proposal = reference(program.n, budget_values, argument, bits=bit_limit)
    plan = thaw(proposal, cells=limit, bits=bit_limit)
    if (type(plan) is not IndexedPredictionPlan or plan.before != state.encoded
            or type(plan.query) is not tuple or len(plan.query) != 2
            or any(type(v) is not int for v in plan.query) or plan.query != query
            or type(plan.bit_limit) is not int or plan.bit_limit != bit_limit):
        raise ContractError('indexed plan differs from the private predecessor or actual input')
    # The complete reconstruction remains private, including its funding.
    execution_debit(machine.prediction_execution_work(plan))
    return _execute_owned_prediction(plan, program.n)
