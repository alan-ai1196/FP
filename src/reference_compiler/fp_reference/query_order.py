"""Packed exact structural order search; no Runtime or numerical authority.

The caller must own the supplied byte extent and prepay search_work before
calling search. Only the exponential DP table occupies that extent; bounded
graph metadata and host interpreter memory are not a whole-process claim.
The result minimizes a structural pair, never numerical error or precision.
"""
from dataclasses import dataclass
import struct

from .core import ContractError
from .resources import ResourceExceeded
from .semantics import ArithmeticUnresolved

MAX_FREE = 15
WORK_MODEL = 'prepaid-packed-query-order-subsets-v1'
_ROW = struct.Struct('<III')  # floating outputs, tape nodes, predecessor bit+1


def _dimensions(n, query):
    if type(n) is not int or not 2 <= n <= MAX_FREE+1:
        raise ArithmeticUnresolved('query-order search exceeds its declared 1..15 free-vertex class')
    if (type(query) is not tuple or len(query) != 2
            or any(type(v) is not int or not 0 <= v < n for v in query)):
        raise ContractError('complete ordered query required for structural order search')
    kept = tuple(v for v in range(n-1) if v+1 in query)
    choices = tuple(v for v in range(n-1) if v not in kept)
    return kept, choices


def workspace_bytes(n, query):
    _, choices = _dimensions(n, query)
    return _ROW.size*(1 << len(choices))


def search_work(n, edge_count, query):
    _, choices = _dimensions(n, query)
    if type(edge_count) is not int or not 0 <= edge_count <= n*(n-1)//2:
        raise ContractError('bounded complete active-edge count required')
    # Conservative fixed-width primitive/visit tariff, not measured CPU time.
    # Includes validation, initialization, all row/choice/scoped-factor visits,
    # terminal join and order reconstruction. Bits and table words are <=32.
    return 128*((1 << len(choices))+1)*n*(edge_count+n)


@dataclass(frozen=True)
class OrderMinimum:
    order: tuple[int, ...]
    output_cells: int
    tape_nodes: int
    subset_states: int
    transitions: int


def search(n, support, query, join_cap, live_cap, workspace, *, objective='outputs'):
    """Exact lex(C,N), or lex(N,C), over all query-retaining orders.

    None means the declared join/live class is empty, not that every FP
    decoder or precision-aware class is infeasible. Resource exhaustion and
    out-of-class input raise before search; they never become an empty class.
    The supplied buffer is the actual DP table, not a dummy paid reservation.
    """
    kept, choices = _dimensions(n, query)
    if (type(support) is not tuple or len(support) > n*(n-1)//2
            or any(type(e) is not tuple or len(e) != 2 or any(type(v) is not int for v in e)
                   or not 0 <= e[0] < e[1] < n for e in support)
            or any(a >= b for a, b in zip(support, support[1:]))):
        raise ContractError('complete canonical active support required for order search')
    if any(type(cap) is not int or cap <= 0 for cap in (join_cap, live_cap)):
        raise ContractError('positive integer table caps required for order search')
    if type(objective) is not str or objective not in ('outputs', 'nodes'):
        raise ContractError('registered structural lexicographic objective required')
    rows = 1 << len(choices)
    if type(workspace) is not bytearray or len(workspace) < rows*_ROW.size:
        raise ResourceExceeded('query-order DP needs its complete owned byte extent')
    scopes = tuple(sum(1 << (v-1) for v in edge if v) for edge in support)
    m, full = n-1, (1 << (n-1))-1
    adjacency = [0]*m
    for scope in scopes:
        for v in range(m):
            if scope >> v & 1:
                adjacency[v] |= scope ^ (1 << v)
    initial_cells = sum(1 << scope.bit_count() for scope in scopes)
    if initial_cells > live_cap:
        return None
    # Reset only the leased prefix without another exponential zero buffer.
    # prev==0 marks an unreachable nonzero row; row0 is the empty prefix.
    for row in range(rows):
        _ROW.pack_into(workspace, row*_ROW.size, 0, 0, 0)
    examined = transitions = 0
    terminal = None
    for mask in range(rows):
        old_c, old_n, prev = _ROW.unpack_from(workspace, mask*_ROW.size)
        if mask and not prev:
            continue
        examined += 1
        removed = sum(1 << v for k, v in enumerate(choices) if mask >> k & 1)
        left = full ^ removed
        components = []
        unseen = removed
        while unseen:
            fringe = unseen & -unseen
            component = boundary = 0
            while fringe:
                bit = fringe & -fringe
                fringe ^= bit
                v = bit.bit_length()-1
                component |= bit
                boundary |= adjacency[v]
                fringe |= adjacency[v] & removed & ~component
            unseen &= ~component
            components.append(boundary & left)
        original = tuple(scope for scope in scopes if not scope & removed)
        current_cells = sum(1 << scope.bit_count() for scope in original)+sum(
            1 << scope.bit_count() for scope in components)
        if mask == rows-1:
            cells = 1 << len(kept)
            if cells <= join_cap and current_cells+cells <= live_cap:
                a, b = len(original), len(components)
                terminal = (old_c+38+4*cells+6*max(0, b-1)*cells,
                            old_n+3+initial_cells+(a+b)*cells+cells)
            continue
        for k, v in enumerate(choices):
            if mask >> k & 1:
                continue
            bit = 1 << v
            a = b = 0
            scope = bit
            for item in original:
                if item & bit:
                    a += 1
                    scope |= item
            for item in components:
                if item & bit:
                    b += 1
                    scope |= item
            cells = 1 << scope.bit_count()
            if cells > join_cap or current_cells+cells+cells//2 > live_cap:
                continue
            transitions += 1
            c = old_c+4*(cells//2)+6*max(0, b-1)*cells
            t = old_n+(a+b)*cells+cells//2
            following = mask | (1 << k)
            stored_c, stored_n, stored_prev = _ROW.unpack_from(workspace, following*_ROW.size)
            better = ((c, t) < (stored_c, stored_n) if objective == 'outputs'
                      else (t, c) < (stored_n, stored_c))
            if not stored_prev or better:
                # All partial/terminal counts are <2^27 at m<=15. Keep this
                # guard so a future class expansion cannot silently wrap.
                if not 0 <= c < 1 << 32 or not 0 <= t < 1 << 32:
                    raise ArithmeticUnresolved('query-order cost exceeds its packed-word class')
                _ROW.pack_into(workspace, following*_ROW.size, c, t, k+1)
    if terminal is None:
        return None
    order, mask = [], rows-1
    while mask:
        _, _, prev = _ROW.unpack_from(workspace, mask*_ROW.size)
        if not 1 <= prev <= len(choices) or not mask >> (prev-1) & 1:
            raise ContractError('query-order reconstruction lost its reachable predecessor')
        order.append(choices[prev-1])
        mask ^= 1 << (prev-1)
    order.reverse()
    order.extend(kept)
    return OrderMinimum(tuple(order), *terminal, examined, transitions)
