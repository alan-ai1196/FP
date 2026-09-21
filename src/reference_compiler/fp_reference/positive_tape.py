"""Positive indexed inference tape; a passive schedule, without Runtime authority."""
from . import positive_partition as exact


class Tape:
    def __init__(self):
        self.nodes = [('zero',), ('one',), ('nine',)]
        self.budgets = [0, 0, 0]

    def factor(self, edge, parity):
        self.nodes.append(('factor', edge, parity))
        self.budgets.append(0)
        return len(self.nodes)-1

    def op(self, tag, left, right):
        self.nodes.append((tag, left, right))
        a, b = self.budgets[left], self.budgets[right]
        self.budgets.append((a+b if tag == 'mul' else max(a, b))+1)
        return len(self.nodes)-1


def compile_tape(n, support, query, *, order=None, readout=True):
    tape = Tape()
    signed = tuple(int(e in support) for e in exact.edges(n))
    order = exact.greedy_order(exact.adjacency(n, signed)) if order is None else tuple(order)
    assert sorted(order) == list(range(n-1))
    kept = tuple(sorted({v for v in query if v}))
    factors = []
    for edge, (i, j) in enumerate(support):
        scope = tuple(v for v in (i, j) if v)
        values = []
        for word in range(1 << len(scope)):
            z = {v: (word >> k) & 1 for k, v in enumerate(scope)}
            values.append(tape.factor(edge, z.get(i, 0) ^ z.get(j, 0)))
        factors.append((scope, tuple(values)))

    def join(items, scope):
        positions = {v: k for k, v in enumerate(scope)}
        outputs = []
        for word in range(1 << len(scope)):
            value = 1
            for fs, table in items:
                index = sum(((word >> positions[v]) & 1) << k for k, v in enumerate(fs))
                value = tape.op('mul', value, table[index])
            outputs.append(value)
        return tuple(outputs)

    for v in (j+1 for j in order):
        if v in kept:
            continue
        bucket = [f for f in factors if v in f[0]]
        scope = tuple(sorted({v}.union(*(set(s) for s, _ in bucket))))
        joined = join(bucket, scope)
        position = scope.index(v)
        out_scope = tuple(u for u in scope if u != v)
        outputs = []
        for word in range(1 << len(out_scope)):
            index = (word & ((1 << position)-1)) | ((word >> position) << (position+1))
            outputs.append(tape.op('add', joined[index], joined[index | (1 << position)]))
        factors = [f for f in factors if v not in f[0]]+[(out_scope, tuple(outputs))]
    final = join(factors, kept)
    parts = [0, 0]
    for word, value in enumerate(final):
        z = {v: (word >> k) & 1 for k, v in enumerate(kept)}
        parity = z.get(query[0], 0) ^ z.get(query[1], 0)
        parts[parity] = tape.op('add', parts[parity], value)
    # Expose the same positive partitions for a complete native readout;
    # retaining this metadata changes no existing node or scalar operation.
    tape.partition_heads = tuple(parts)
    tape.elimination_order = order
    if not readout:
        return tape, tape.partition_heads
    heads = (tape.op('add', tape.op('mul', 2, parts[0]), parts[1]),
             tape.op('add', parts[0], tape.op('mul', 2, parts[1])))
    assert max(tape.budgets[h] for h in heads) <= len(support)+2*(n-1)+4
    return tape, heads
