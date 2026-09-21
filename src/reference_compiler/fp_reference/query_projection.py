"""Exact current-query block projection; full learner counts remain owned.

Planning reads the complete support before any numerical tables or powers.
The immutable plan is not a resource lease, learner state or certificate.
"""
from collections import deque
from dataclasses import dataclass
from itertools import combinations

from .core import ContractError
from .indexed_count import CountState, query as require_query
from .indexed_relation import DecodeAllowance, allowance, partition_plan, partition_shape_plan
from . import positive_partition as partition
from .semantics import ArithmeticUnresolved


@dataclass(frozen=True)
class BlockPlan:
    vertices: tuple[int, ...]
    query: tuple[int, int]
    shape: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class ProjectionPlan:
    blocks: tuple[BlockPlan, ...]
    shape: tuple[tuple[str, int], ...]


def _blocks(n, support):
    adjacency = [[] for _ in range(n)]
    for edge,(u,v) in enumerate(support):
        adjacency[u].append((v,edge))
        adjacency[v].append((u,edge))
    seen,low,parent,parent_edge = ([-1]*n for _ in range(4))
    clock, result, edge_stack = 0, [], []
    for root in range(n):
        if seen[root] >= 0:
            continue
        seen[root] = low[root] = clock
        clock += 1
        stack = [(root,iter(adjacency[root]))]
        while stack:
            v,children = stack[-1]
            child = next(children,None)
            if child is None:
                stack.pop()
                p = parent[v]
                if p >= 0:
                    low[p] = min(low[p],low[v])
                    if low[v] >= seen[p]:
                        edges = []
                        while True:
                            edge = edge_stack.pop()
                            edges.append(edge)
                            if edge == parent_edge[v]:
                                break
                        result.append(tuple(sorted({u for e in edges for u in support[e]})))
                continue
            u,edge = child
            if edge == parent_edge[v]:
                continue
            if seen[u] < 0:
                parent[u],parent_edge[u] = v,edge
                seen[u] = low[u] = clock
                clock += 1
                edge_stack.append(edge)
                stack.append((u,iter(adjacency[u])))
            elif seen[u] < seen[v]:
                low[v] = min(low[v],seen[u])
                edge_stack.append(edge)
        if edge_stack:
            raise ContractError('block decomposition left unassigned active edges')
    return tuple(result)


def _path(n, support, query):
    if query[0] == query[1]:
        return ()
    blocks = _blocks(n,support)
    tree = [[] for _ in range(n+len(blocks))]
    for k,vertices in enumerate(blocks):
        for v in vertices:
            tree[v].append(n+k)
            tree[n+k].append(v)
    parents = {query[0]: None}
    queue = deque((query[0],))
    while queue and query[1] not in parents:
        v = queue.popleft()
        for u in tree[v]:
            if u not in parents:
                parents[u] = v
                queue.append(u)
    if query[1] not in parents:
        return ()
    path, v = [], query[1]
    while v is not None:
        path.append(v)
        v = parents[v]
    path.reverse()
    return tuple((blocks[path[k]-n],path[k-1],path[k+1]) for k in range(1,len(path),2))


def _local(before, vertices):
    values = []
    for u,v in combinations(vertices,2):
        # Vertices stay globally sorted: a whole-program block preserves
        # the existing anchor and natural order exactly.
        edge = u*(2*before.n-u-1)//2+v-u-1
        values.append(before.counts[edge])
    return CountState(len(vertices),tuple(values),None,before.cursor,before.steps)


def _prepare(before, query, budget, *, integer):
    if type(before) is not CountState or before.pending is not None or type(budget) is not DecodeAllowance:
        raise ContractError('complete committed count state and decoder allowance required')
    if type(query) is not tuple or len(query) != 2:
        raise ContractError('complete ordered query required')
    before.__post_init__()
    require_query(before.n,*query)
    support = tuple(edge for edge,d in zip(combinations(range(before.n),2),before.counts) if d)
    path = _path(before.n,support,query)
    blocks, height, edge_count = [], 0, 0
    for vertices,u,v in path:
        local = _local(before,vertices)
        height += sum(map(abs,local.counts))
        edge_count += sum(d != 0 for d in local.counts)
        local_query = vertices.index(u),vertices.index(v)
        order = tuple(range(local.n-1))
        if integer:
            shape = partition_plan(local,local_query,order,budget)
        else:
            active = tuple(edge for edge,d in zip(combinations(range(local.n),2),local.counts) if d)
            shape = partition_shape_plan(local.n,active,local_query,order,budget)
        blocks.append(BlockPlan(vertices,local_query,tuple(shape.items())))
    vertices = 1+sum(len(block.vertices)-1 for block in blocks) if blocks else 0
    # Positive block convolution also needs this combined height envelope.
    # Off-path counts are retained, but no power of them is evaluated here.
    if integer and vertices+4*height+8 > budget.integer_bits:
        raise ArithmeticUnresolved('projected response integer envelope exceeds its declared allowance')
    shapes = tuple(dict(block.shape) for block in blocks)
    convolutions = max(0,len(blocks)-1)
    shape = {
        'positive_multiplications': sum(row['positive_multiplications'] for row in shapes)+4*convolutions,
        'positive_additions': sum(row['positive_additions'] for row in shapes)+2*convolutions+int(convolutions > 0),
        'largest_join_cells': max((row['largest_join_cells'] for row in shapes),default=1),
        # Eight extra scalar cells conservatively cover the retained response
        # and convolution temporaries. A sole block returns its own result.
        'peak_live_integer_cells': max((row['peak_live_integer_cells'] for row in shapes),default=2)+(8 if convolutions else 0),
        'projected_blocks': len(blocks), 'projected_vertices': vertices,
        'projected_active_edges': edge_count, 'complete_counts_scanned': len(before.counts)}
    allowance(shape['positive_multiplications']+shape['positive_additions'],budget.arithmetic,'projected arithmetic allowance')
    allowance(shape['largest_join_cells'],budget.join_cells,'projected join-cell allowance')
    allowance(shape['peak_live_integer_cells'],budget.live_cells,'projected live-cell allowance')
    return ProjectionPlan(tuple(blocks),tuple(shape.items()))


def prepare(before, query, budget):
    """Exact integer decoder: combined and individual height guards apply."""
    return _prepare(before,query,budget,integer=True)


def prepare_shape(before, query, budget):
    """Only table geometry; mantissa/exponent execution needs its own guard."""
    return _prepare(before,query,budget,integer=False)


def execute(before, query, plan):
    if type(plan) is not ProjectionPlan:
        raise ContractError('complete projected numerical schedule required')
    # Runtime independently reconstructs and checks the metadata plan before
    # paying its numerical debit. This helper supplies no ownership authority.
    result = (1,0) if query[0] == query[1] else (1,1)
    maximum_bits, width = 1 if query[0] == query[1] else 2, 0
    multiply = add = 0
    for k,block in enumerate(plan.blocks):
        local = _local(before,block.vertices)
        parts,stats = partition.decode(local.n,local.counts,block.query,order=tuple(range(local.n-1)))
        if any(stats[key] != value for key,value in block.shape):
            raise ContractError('executed block differs from its prepaid table schedule')
        multiply += stats['positive_multiplications']
        add += stats['positive_additions']
        maximum_bits = max(maximum_bits,stats['maximum_integer_bits'])
        width = max(width,stats['base_order_width'])
        if k:
            a,b = result
            c,d = parts
            result = a*c+b*d,a*d+b*c
            multiply += 4
            add += 2
            maximum_bits = max(maximum_bits,*(v.bit_length() for v in result))
        else:
            result = parts
    if len(plan.blocks) > 1:
        maximum_bits = max(maximum_bits,sum(result).bit_length())
        add += 1
    shape = dict(plan.shape)
    if (multiply,add) != (shape['positive_multiplications'],shape['positive_additions']):
        raise ContractError('executed convolution differs from its prepaid schedule')
    return result, {**shape,'maximum_integer_bits': maximum_bits,'maximum_block_order_width': width}
