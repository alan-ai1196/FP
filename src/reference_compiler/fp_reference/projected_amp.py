"""Declared query-block AMP plan; complete global counts remain untouched.

Only geometry is shared with the exact reference. No exact partition,
forecast or gradient enters this physical schedule's construction.
"""
from itertools import combinations

from . import indexed_amp as amp, query_projection as projection
from .core import ContractError
from .indexed_relation import IndexedRelation, DecodeAllowance, allowance
from .positive_tape import compile_tape
from .semantics import ArithmeticUnresolved

BACKEND_ID = 'owned-indexed-query-block-radix9-half-products-single-readout-v1'
FORWARD_ID = 'indexed-positive-query-block-convolution-power-aliases-rne16-rne32-v1'
ORDERED_FORWARD_ID = 'indexed-positive-paid-query-block-order-convolution-rne16-rne32-v1'


def _prepare_prediction(program,state,rules,sources,*,output_cap,order_search=None,orders=None):
    if type(program) is not IndexedRelation or type(state) is not amp.IndexedAmpState or state.unit_count:
        raise ContractError('owned indexed syntax and committed AMP state required')
    state.__post_init__()
    if state.encoded.n != program.n:
        raise ContractError('projected AMP state differs from its program')
    query,_ = program.source_query(rules,sources)
    geometry = projection.prepare_shape(state.encoded,query,DecodeAllowance(),order_search=order_search,orders=orders)
    blocks,edges,height,tape_cells = [],set(),0,3
    for block in geometry.blocks:
        local = projection._local(state.encoded,block.vertices)
        support = tuple(edge for edge,d in zip(combinations(range(local.n),2),local.counts) if d)
        shape = dict(block.shape)
        # Partition-only tape: three shared constants, no final mass heads
        # and no unused exact integer sum of the two partition outputs.
        tape_cells += sum(2 if i == 0 else 4 for i,j in support)
        tape_cells += shape['positive_multiplications']+shape['positive_additions']-1
        height += sum(map(abs,local.counts))
        edges.update((block.vertices[i],block.vertices[j]) for i,j in support)
        blocks.append((block,support))
    tape_cells += 6*max(0,len(blocks)-1)
    allowance(tape_cells,amp.MAX_TAPE_CELLS,'projected AMP tape-cell allowance')
    if height+tape_cells+4 > amp.COUNTER_CAP:
        raise ArithmeticUnresolved('projected AMP exponent envelope exhausted before execution')
    support = tuple(sorted(edges))
    positions = tuple(i*(2*program.n-i-1)//2+j-i-1 for i,j in support)
    edge_indices = {edge:k for k,edge in enumerate(support)}
    nodes = [('zero',),('one',),('nine',)]
    parts = (1,0) if query[0] == query[1] else (1,1)

    def op(tag,a,b):
        nodes.append((tag,a,b))
        return len(nodes)-1

    for k,(block,local_support) in enumerate(blocks):
        tape,heads = compile_tape(len(block.vertices),local_support,block.query,
            order=block.order,readout=False)
        mapping = [0,1,2]
        for tag,*args in tape.nodes[3:]:
            if tag == 'factor':
                edge,parity = args
                i,j = local_support[edge]
                nodes.append((tag,edge_indices[(block.vertices[i],block.vertices[j])],parity))
            else:
                a,b = args
                nodes.append((tag,mapping[a],mapping[b]))
            mapping.append(len(nodes)-1)
        a,b = (mapping[h] for h in heads)
        if k:
            left,right = parts
            parts = (op('add',op('mul',left,a),op('mul',right,b)),
                     op('add',op('mul',left,b),op('mul',right,a)))
        else:
            parts = a,b
    if len(nodes) != tape_cells:
        raise ContractError('projected AMP tape differs from its metadata preflight')
    shape = geometry.shape+(('partition_tape_cells',tape_cells),)
    return amp._finish_plan(program.n,query,support,positions,tuple(nodes),parts,shape,output_cap,
                            orders=tuple(block.order for block in geometry.blocks))


def prepare_prediction(program,state,rules,sources,*,output_cap):
    return _prepare_prediction(program,state,rules,sources,output_cap=output_cap)


def check_prediction_plan(plan,program,state,rules,sources,*,output_cap,allow_orders=False):
    if type(allow_orders) is not bool or type(plan) is not amp.IndexedAmpPlan:
        raise ContractError('registered plan and immutable order-class flag required')
    expected = _prepare_prediction(program,state,rules,sources,output_cap=output_cap,
                                   orders=plan.orders if allow_orders else None)
    amp._check_plan(plan,expected)
