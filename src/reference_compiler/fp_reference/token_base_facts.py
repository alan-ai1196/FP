"""Paid immutable facts about the registered token base tuple.

This private owner artifact contains no observation or learner endpoint. Its
dynamic scope only selects a read-only owner; it is not a process-global cache.
Passive calls outside a Runtime scope always execute the original operations.
"""
from contextvars import ContextVar, copy_context
from fractions import Fraction as F

from .core import ContractError
from .encoding import bounded_packed_size, fragments, write_packed
from .resources import ObjectSpec, ResourceExceeded
from .semantics import _operation

FACT_ID = 'owned-positive-token-base-and-guarded-fold-v1'
_ACTIVE = ContextVar('fp_owned_token_base_facts', default=None)


def guarded_fold(values, *, bit_limit):
    """Original ordered Fraction additions and their exact guard threshold.

    `required` characterizes THIS conservative preflight, not the smallest
    memory needed by any exact summation algorithm. No guarded operation is
    executed with a larger allowance than the caller supplied.
    """
    value, required = F(0), 0
    for item in values:
        if type(item) is not F:
            raise ContractError('exact Fraction operands required by the fold profile')
        nx, dx = value.numerator.bit_length(), value.denominator.bit_length()
        ny, dy = item.numerator.bit_length(), item.denominator.bit_length()
        required = max(required, nx, dx, ny, dy, max(nx+dy, ny+dx, dx+dy)+1)
        value = _operation(value, item, multiply=False, bit_limit=bit_limit)
        required = max(required, value.numerator.bit_length(), value.denominator.bit_length())
    return value, required


def positive_base_known(value):
    fact = _ACTIVE.get()
    return fact is not None and fact.source is value


def known_total(value, bit_limit):
    fact = _ACTIVE.get()
    if (fact is not None and fact.source is value
            and (bit_limit is None or type(bit_limit) is int and bit_limit >= fact.required_bits)):
        return fact.total
    # Preserve the original first guard/error when a smaller or malformed
    # allowance is supplied. Equality of final sums is not enough to accept.
    return None


def run_for(runtime, operation, *args, **kwargs):
    archive = runtime._reference_archive
    fact = None if archive is None else archive.base_facts
    # A disabled nested owner must mask an outer owner's fact, not inherit it.
    return _run(fact, operation, *args, **kwargs)


def _enter(fact, operation, args, kwargs):
    _ACTIVE.set(fact)
    return operation(*args, **kwargs)


def _run(fact, operation, *args, **kwargs):
    if _ACTIVE.get() is fact:
        return operation(*args, **kwargs)
    # ContextVar.reset can allocate a new HAMT path. Restoring the parent via
    # Context.run instead keeps that allocation out of the failure cleanup.
    # The new context and binding are disposable workspace under the host cap.
    return copy_context().run(_enter, fact, operation, args, kwargs)


class _TokenBaseFacts:
    def __init__(self, runtime, deployment_owner, cap):
        rt = runtime
        source = rt._contract.initializer_pattern.output.base
        ledger = rt._ledger
        entries = (len(ledger._objects)*(len(ledger._owners)+2)+len(ledger._events)
                   +len(ledger._owners)+len(ledger._retired)+len(rt._buffers)+16)
        # Bounds the source/encoding walks and this fixed scalar fold's work;
        # integer-bit and actual whole-host limits remain independently binding.
        ledger.charge_work('compiler', {'work': 128*cap+256*(len(source)+entries)},
                           note='owned-token-base-facts')
        bounded_packed_size(source, byte_limit=cap, integer_bits=rt._contract.reference_integer_bits)
        from .token_readout import exact
        if type(source) is not tuple or len(source) < 2:
            raise ContractError('complete immutable token base tuple required')
        for item in source:
            exact(item, positive=True)
        total, required = guarded_fold(source, bit_limit=rt._contract.reference_integer_bits)
        body = (FACT_ID, source, total, required)
        size = bounded_packed_size(body, byte_limit=cap, integer_bits=rt._contract.reference_integer_bits)
        if size > cap:
            raise ResourceExceeded('owned token base fact exceeds its registered capacity')
        identity = rt._runtime_id+':token-base-facts'
        scratch = identity+':copy'
        extent = {'reference_payload_bytes': size, 'physical_objects': 1}
        ledger.allocate(rt._data_owner, (ObjectSpec(scratch, 'token_base_fact_copy', extent, rt._chi),))
        rt._buffers[scratch] = bytearray(size)
        ledger.acquire(deployment_owner, scratch)
        write_packed(body, rt._buffers[scratch])
        ledger.allocate(rt._data_owner, (ObjectSpec(identity, 'immutable_token_base_fact', extent, rt._chi),))
        rt._buffers[identity] = bytes(rt._buffers[scratch])
        ledger.acquire(deployment_owner, identity)
        # Bind every retained byte with a fresh traversal, not a producer hint
        # or a preexisting canonical image. Partial attempts stay paid on error.
        offset = 0
        for fragment in fragments(body, packed=True):
            part = fragment.encode('utf-8', 'surrogatepass')
            if rt._buffers[identity][offset:offset+len(part)] != part:
                raise ContractError('token base fact differs from its complete retained body')
            offset += len(part)
        if offset != size:
            raise ContractError('token base fact lost a complete byte extent')
        # Only trusted successful construction publishes this immutable fact.
        # Snapshots expose builtin values, never this mutable private wrapper.
        self.source, self.total, self.required_bits = source, total, required
        self.buffer, self.size = identity, size
        ledger.release_many(((rt._data_owner, scratch, 1), (deployment_owner, scratch, 1)))
        rt._buffers.pop(scratch)

    def run(self, operation, *args, **kwargs):
        return _run(self, operation, *args, **kwargs)

    def snapshot(self):
        return (FACT_ID, self.source, self.total, self.required_bits, self.buffer, self.size)
