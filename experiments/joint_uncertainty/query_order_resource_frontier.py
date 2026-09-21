"""Exact order-class resource audit on the exposed indexed model tapes.

Passive mathematical decisions only: no Runtime, floating execution, model
scores, search funding, fresh evidence or installation authority.
"""
from functools import lru_cache
from itertools import combinations, combinations_with_replacement, permutations
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'),str(Path(__file__).parent)]
from joint_model import new_cases, data
from fp_reference.indexed_count import CountState
from fp_reference import query_projection as projection
from fp_reference.indexed_relation import DecodeAllowance, partition_shape_plan
from fp_reference.positive_tape import compile_tape
from fp_reference.indexed_amp import _finish_plan
from fp_reference.encoding import packed_size
from fp_reference.resources import ResourceExceeded
from fp_reference.semantics import ArithmeticUnresolved

def subset_costs(n, support, query, join_cap=4096, live_cap=32768, objective='outputs'):
    """Exact lexicographic outputs/nodes or nodes/outputs minimum under table caps.
    No order-search, packed-frame, exponent, time or whole-process claim.
    This routine is passive and has no Runtime authority.
    """
    if type(n) is not int or not 2 <= n <= 16:
        raise ValueError('passive subset search requires 1..15 free variables')
    if (type(support) is not tuple or any(type(e) is not tuple or len(e)!=2 or
            any(type(v) is not int for v in e) or not 0<=e[0]<e[1]<n for e in support)
            or tuple(sorted(set(support))) != support):
        raise ValueError('complete canonical active support required')
    if (type(query) is not tuple or len(query)!=2 or
            any(type(v) is not int or not 0<=v<n for v in query)):
        raise ValueError('complete ordered query required')
    if any(type(cap) is not int or cap<=0 for cap in (join_cap,live_cap)):
        raise ValueError('positive integer table caps required')
    if objective not in ('outputs','nodes'):
        raise ValueError('a declared lexicographic objective is required')
    key = (lambda pair: pair) if objective == 'outputs' else (lambda pair: (pair[1],pair[0]))
    m = n-1
    scopes = tuple(sum(1 << (v-1) for v in edge if v) for edge in support)
    adjacency = [0]*m
    for scope in scopes:
        for v in range(m):
            if scope >> v & 1:
                adjacency[v] |= scope ^ (1 << v)
    full = (1 << m)-1
    kept = sum(1 << (v-1) for v in set(query) if v)
    allowed = full ^ kept
    initial_cells = sum(1 << scope.bit_count() for scope in scopes)
    if initial_cells > live_cap:
        return None
    best = {0:(0,0)}
    previous = {}
    examined = transitions = 0
    terminal = None
    for removed in range(allowed+1):
        if removed & ~allowed or removed not in best:
            continue
        examined += 1
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
        current_cells = sum(1 << scope.bit_count() for scope in original+tuple(components))
        if removed == allowed:
            cells = 1 << kept.bit_count()
            if cells <= join_cap and current_cells+cells <= live_cap:
                a,b = len(original),len(components)
                terminal = (38+4*cells+6*max(0,b-1)*cells,
                            3+initial_cells+(a+b)*cells+cells)
            continue
        choices = allowed ^ removed
        while choices:
            bit = choices & -choices
            choices ^= bit
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
            cost = (4*(cells//2)+6*max(0,b-1)*cells, (a+b)*cells+cells//2)
            candidate = tuple(x+y for x,y in zip(best[removed],cost))
            following = removed | bit
            if following not in best or key(candidate) < key(best[following]):
                best[following] = candidate
                previous[following] = bit
    if terminal is None:
        return None
    mask = allowed
    order = []
    while mask:
        bit = previous[mask]
        order.append(bit.bit_length()-1)
        mask ^= bit
    order.reverse()
    order.extend(v for v in range(m) if kept >> v & 1)
    cells,nodes = (x+y for x,y in zip(best[allowed],terminal))
    return {'order':tuple(order), 'partition_only_output_cells':cells,
            'partition_only_tape_nodes':nodes,'subset_states':examined,
            'transitions':transitions}


def small_audit():
    wide = DecodeAllowance(join_cells=1<<8,live_cells=1<<14,arithmetic=10**8)
    graphs = queries = orders = decisions = refused = objective_checks = 0
    for n in range(2,6):
        edges = tuple(combinations(range(n),2))
        for mask in range(1<<len(edges)):
            support = tuple(edge for k,edge in enumerate(edges) if mask>>k&1)
            graphs += 1
            for query in combinations_with_replacement(range(n),2):
                queries += 1
                kept = {v-1 for v in query if v}
                free = tuple(v for v in range(n-1) if v not in kept)
                compiled = {}
                for prefix in permutations(free):
                    order = prefix+tuple(sorted(kept))
                    shape = partition_shape_plan(n,support,query,order,wide)
                    tape,_ = compile_tape(n,support,query,order=order,readout=False)
                    powers = []
                    adds = general = 0
                    for tag,*args in tape.nodes:
                        if tag in ('zero','one','nine','factor'):
                            powers.append(tag!='zero')
                        elif tag == 'add':
                            adds += 1
                            powers.append(False)
                        else:
                            a,b = args
                            general += int(not(powers[a] or powers[b]))
                            powers.append(powers[a] and powers[b])
                    compiled[order] = (38+4*adds+6*general,len(tape.nodes),
                        shape['largest_join_cells'],shape['peak_live_integer_cells'])
                    orders += 1
                for join_cap,live_cap in ((1<<(n-1),1<<(n+4)),(2,8),(4,16),(8,32)):
                    legal = [row[:2] for row in compiled.values() if row[2]<=join_cap and row[3]<=live_cap]
                    for objective in ('outputs','nodes'):
                        result = subset_costs(n,support,query,join_cap,live_cap,objective)
                        key = (lambda pair:pair) if objective=='outputs' else (lambda pair:(pair[1],pair[0]))
                        expected = min(legal,key=key) if legal else None
                        actual = None if result is None else (
                            result['partition_only_output_cells'],result['partition_only_tape_nodes'])
                        assert expected == actual,(n,support,query,join_cap,live_cap,objective,expected,actual)
                        if result is not None:
                            row = compiled[result['order']]
                            assert row[:2] == actual and row[2]<=join_cap and row[3]<=live_cap
                        objective_checks += 1
                    decisions += 1
                    refused += not legal
        print('SMALL through n'+str(n)+': '+str(objective_checks)+' objective checks',flush=True)
    for n in (1,17):
        try:
            subset_costs(n,(),(0,0))
        except ValueError:
            pass
        else:
            raise AssertionError('subset allocation exceeded the declared vertex class')
    return {'supports':graphs,'query_states':queries,'direct_compiled_orders':orders,
        'join_live_limit_decisions':decisions,'lexicographic_objective_checks':objective_checks,
        'empty_join_live_classes':refused,'vertex_guard_refusals':2}


cached=lru_cache(maxsize=2048)(subset_costs)

def solve_projected(state,query,verify=False):
    support=tuple(e for e,d in zip(combinations(range(state.n),2),state.counts) if d)
    path=projection._path(state.n,support,query)
    blocks=[]
    for vertices,u,v in path:
        local=projection._local(state,vertices)
        edges=tuple(combinations(range(local.n),2))
        active=tuple(e for e,d in zip(edges,local.counts) if d)
        local_query=(vertices.index(u),vertices.index(v))
        r=cached(local.n,active,local_query,4096,32768-(8 if len(path)>1 else 0))
        if r is None:return None
        if verify:
            shape=partition_shape_plan(local.n,active,local_query,r['order'],DecodeAllowance())
            tape,heads=compile_tape(local.n,active,local_query,order=r['order'],readout=False)
            p=_finish_plan(local.n,local_query,active,tuple(edges.index(e) for e in active),tuple(tape.nodes),heads,tuple(shape.items()),1<<30)
            assert (len(p.nodes),p.output_cells)==(r['partition_only_tape_nodes'],r['partition_only_output_cells'])
        blocks.append({'vertices':vertices,'local_query':local_query,**r})
    c=max(0,len(blocks)-1)
    return {'minimum_output_cells':38+sum(b['partition_only_output_cells']-38 for b in blocks)+32*c,
            'tape_nodes_at_minimum_output':3+sum(b['partition_only_tape_nodes']-3 for b in blocks)+6*c,
            'blocks':blocks}

def scan_tapes():
    rows = []
    for case in new_cases():
        if case[0]!=16:continue
        n=case[0];_,_,train,evaluation=data(case);tape=train+evaluation
        edges=tuple(combinations(range(n),2));addresses={e:k for k,e in enumerate(edges)};values=[0]*len(edges)
        report={'case':case,'queries':len(tape),'no_join_live_order':0,'minimum_output_exceeds_65536':0,
                'lex_minimum_within_all_four_limits':0,'minimum_output_fits_but_its_tape_exceeds_262144':0,
                'maximum_minimum_output':0,'maximum_tape_at_minimum_output':0,'first_output_refusal':None,'first_natural_geometry_refusal':None,
                'maximum_output_witness':None,'DP_cache_misses_start':cached.cache_info().misses}
        for t,(i,j,y) in enumerate(tape):
            state=CountState(n,tuple(values),None,t,t)
            if report['first_natural_geometry_refusal'] is None:
                try:
                    projection.prepare_shape(state,(i,j),DecodeAllowance())
                except (ResourceExceeded,ArithmeticUnresolved) as exc:
                    report['first_natural_geometry_refusal']={'cursor':t,'query':[i,j],'reason':str(exc)}
            result=solve_projected(state,(i,j))
            if result is None:
                report['no_join_live_order']+=1
            else:
                C,N=result['minimum_output_cells'],result['tape_nodes_at_minimum_output']
                witness={'cursor':t,'query':[i,j],'minimum_output_cells':C,'tape_nodes_at_minimum_output':N}
                if C>report['maximum_minimum_output']:
                    report['maximum_minimum_output']=C
                    report['maximum_output_witness']={**witness,'blocks':result['blocks']}
                report['maximum_tape_at_minimum_output']=max(report['maximum_tape_at_minimum_output'],N)
                if C>65536:
                    report['minimum_output_exceeds_65536']+=1
                    if report['first_output_refusal'] is None:
                        report['first_output_refusal']=witness
                        assert solve_projected(state,(i,j),True)==result
                elif N>262144:report['minimum_output_fits_but_its_tape_exceeds_262144']+=1
                else:report['lex_minimum_within_all_four_limits']+=1
            if i!=j:values[addresses[tuple(sorted((i,j)))]]+=1-2*y
        report['DP_cache_misses']=cached.cache_info().misses-report.pop('DP_cache_misses_start')
        rows.append(report)
        print('TAPE '+str(case)+': '+str(report['lex_minimum_within_all_four_limits'])+'/'+str(report['queries'])+' structural witnesses',flush=True)

    return rows


def obstructions(rows):
    reports = []
    wide=DecodeAllowance(join_cells=1<<16,live_cells=1<<20,arithmetic=10**8)
    for row in rows:
        case=tuple(row['case']);n=case[0];_,_,train,evaluation=data(case);tape=train+evaluation
        edges=tuple(combinations(range(n),2));addresses={e:k for k,e in enumerate(edges)}
        states=[];values=[0]*len(edges)
        for t,(i,j,y) in enumerate(tape):
            states.append(tuple(values))
            if i!=j:values[addresses[tuple(sorted((i,j)))]]+=1-2*y
        t=row['maximum_output_witness']['cursor'];q=tuple(row['maximum_output_witness']['query'])
        active=tuple(e for e,d in zip(edges,states[t]) if d)
        assert projection._path(n,active,q)[0][0]==tuple(range(n)) and len(projection._path(n,active,q))==1
        output_witness=solve_projected(CountState(n,states[t],None,t,t),q,True)
        assert output_witness['minimum_output_cells']==row['maximum_output_witness']['minimum_output_cells']
        assert output_witness['tape_nodes_at_minimum_output']==row['maximum_output_witness']['tape_nodes_at_minimum_output']
        result=subset_costs(n,active,q,objective='nodes')
        shape=partition_shape_plan(n,active,q,result['order'],wide)
        graph,heads=compile_tape(n,active,q,order=result['order'],readout=False)
        assert len(graph.nodes)==result['partition_only_tape_nodes']
        factor_cells=sum(2 if i==0 else 4 for i,j in active)
        binary_nodes=len(graph.nodes)-3-factor_cells
        minimum_frame_lower=8+65*binary_nodes
        phases=1+3*len(tape)
        assert packed_size(('add',0,0))==packed_size(('mul',0,0))==65
        assert minimum_frame_lower>((8<<30)//phases)
        report={'case':case,'uniform_frame_obstruction':{'cursor':t,'query':q,'minimum_tape_nodes':len(graph.nodes),
            'initial_factor_cells':factor_cells,'minimum_binary_nodes':binary_nodes,'frame_bytes_lower_bound':minimum_frame_lower,
            'required_phases':phases,'frame_bytes_upper_from_8GiB_alone':(8<<30)//phases,
            'retained_frames_bytes_lower_bound':phases*minimum_frame_lower,'node_minimizing_order':result['order'],
            'node_minimizing_shape':shape},'selected_order_infeasibility_witness':None}
        if row['no_join_live_order']:
            for t in range(len(tape)-1,-1,-1):
                i,j,_=tape[t]
                if i==j:continue
                active=tuple(e for e,d in zip(edges,states[t]) if d)
                path=projection._path(n,active,(i,j))
                if len(path)!=1 or path[0][0]!=tuple(range(n)):continue
                if subset_costs(n,active,(i,j)) is not None:continue
                assert subset_costs(n,active,(i,j),4096,1<<20) is None
                alternate=subset_costs(n,active,(i,j),8192,32768)
                assert alternate is not None
                shape=partition_shape_plan(n,active,(i,j),alternate['order'],wide)
                assert shape['largest_join_cells']==8192 and shape['peak_live_integer_cells']<=32768
                report['selected_order_infeasibility_witness']={'cursor':t,'query':[i,j],
                    'minimum_join_cells':8192,'width_search_live_cap':1<<20,
                    'witness_order':alternate['order'],'witness_shape':shape}
                break
            assert report['selected_order_infeasibility_witness'] is not None
        reports.append(report)
        print('OBSTRUCTION '+str(case)+': uniform frames need at least '+str(report['uniform_frame_obstruction']['retained_frames_bytes_lower_bound'])+' bytes',flush=True)

    return reports


def audit():
    model_path = ROOT/'evidence/minimal/FP_INDEXED_MODEL_A1.json'
    model = json.loads(model_path.read_text(encoding='utf-8'))
    assert model['status']=='COMPLETE_WITH_UNRESOLVED' and len(model['workers'])==16
    small = small_audit()
    rows = scan_tapes()
    witnesses = obstructions(rows)
    assert 'torch' not in sys.modules
    return {'status':'PASS_EXACT_ORDER_RESOURCE_FRONTIER',
        'scope':'passive finite order class; no Runtime certificate, numerical continuation or model score',
        'model_attempt':str(model_path.relative_to(ROOT)).replace('\\','/'),
        'native_execution_source':model['execution_source'],
        'decision_class':'all query-retaining binary bucket orders within each existing anchored query block; fixed power-alias interpreter and partition-only tape',
        'structural_caps':{'join_cells':4096,'logical_live_cells':32768,
            'tape_nodes':262144,'floating_outputs':65536},
        'precision_scope':'cost tags only; no finite-mantissa accuracy or exponent claim',
        'search_scope':'at most 15 free vertices; subset search and whole-resource execution remain unfunded here',
        'small_audit':small,'tapes':rows,'obstructions':witnesses}

if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,
        default=ROOT/'evidence/minimal/FP_QUERY_ORDER_RESOURCE_FRONTIER.json')
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    report = audit()
    if args.check or args.output.exists():
        assert json.loads(args.output.read_text(encoding='utf-8'))==json.loads(json.dumps(report))
    else:
        args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'small':report['small_audit'],
        'model_prefixes':sum(row['queries'] for row in report['tapes'])}),flush=True)
