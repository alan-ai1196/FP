"""Ordinary positive shared-marginal syntax; no construction authority.

The enclosing simplex proposer checks the entire source/learner/initializer
interface and prepays the finite emission before calling this private emitter.
Integer-indexed prefix layers avoid materializing a table of latent bit strings.
"""
from .program import Product, Program, Source, Sum, Term


SOLVER = 'native-binary-relation-positive-pair-marginals-v8'


def marginal_counts(n, worlds):
    singleton = 2 if n == 2 else 0
    sums = 7*worlds+3-(n*n+7*n)//2+singleton
    products = 2*n*n+2
    sum_edges = 14*worlds-6*n+singleton
    return {'nodes': 2*n+sums+products, 'SUMs': sums, 'PRODUCTs': products,
            'edges': sum_edges+2*products, 'slots': worlds+1}


def _emit_pair_marginals(rules, atoms, worlds):
    n, m, dtype = len(atoms), len(atoms)-1, rules.readout_type
    nodes = [Source(source.source_id) for source in rules.sources]
    indices = {source.source_id: i for i, source in enumerate(rules.sources)}

    def emit(node):
        nodes.append(node)
        return len(nodes)-1

    def balanced(terms):
        layer = list(terms)
        while len(layer) > 1:
            layer = [Term(emit(Sum(dtype, (layer[k], layer[k+1]))), 0)
                     for k in range(0, len(layer), 2)]
        return layer[0]

    def value(term):
        return term.parent if term.slot == 0 else emit(Sum(dtype, (term,)))

    unit = emit(Sum(dtype, tuple(Term(indices[pair[0]], 0) for pair in atoms)))
    prefix = [None]*(m+1)
    prefix[m] = [Term(unit, slot) for slot in range(1, worlds+1)]
    for depth in range(m-1, -1, -1):
        child = prefix[depth+1]
        prefix[depth] = [balanced((child[k], child[k+1])) for k in range(0, len(child), 2)]
    filtered = {}
    for j in range(1, m+1):
        for b in (0, 1):
            levels = [None]*j
            levels[j-1] = prefix[j][b::2]
            for depth in range(j-2, -1, -1):
                child = levels[depth+1]
                levels[depth] = [balanced((child[k], child[k+1])) for k in range(0, len(child), 2)]
            filtered[j, b] = levels
    marginals = {(0, j, y): filtered[j, y][0][0]
                 for j in range(1, m+1) for y in (0, 1)}
    for i in range(1, m+1):
        for j in range(i+1, m+1):
            for y in (0, 1):
                marginals[i, j, y] = balanced(filtered[j, (p & 1) ^ y][i][p]
                                               for p in range(1 << i))
    marginal_nodes = {key: value(term) for key, term in marginals.items()}
    total = value(prefix[0][0])
    queries = {(i, j): emit(Product(dtype, indices[atoms[i][0]], indices[atoms[j][1]]))
               for i in range(n) for j in range(n)}
    output = [[], []]
    for i in range(n):
        output[0].append(Term(emit(Product(dtype, queries[i, i], total)), 0))
    for i in range(n):
        for j in range(i+1, n):
            query = emit(Sum(dtype, (Term(queries[i, j], 0), Term(queries[j, i], 0))))
            for y in (0, 1):
                output[y].append(Term(emit(Product(dtype, query, marginal_nodes[i, j, y])), 0))
    heads = tuple(emit(Sum(dtype, tuple(terms))) for terms in output)
    eight = unit
    for _ in range(3):
        eight = emit(Sum(dtype, (Term(eight, 0), Term(eight, 0))))
    heads = tuple(emit(Product(dtype, head, eight)) for head in heads)
    return Program(tuple(nodes), worlds+1, heads)
