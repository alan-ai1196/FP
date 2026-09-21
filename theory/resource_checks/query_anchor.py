"""Passive exact gauge/query-width audit. No Runtime or CUDA authority.

The full learner stays in its original coordinates. Relabeling is only a
partition computation, with exact independent world sums as its oracle.
"""
from functools import lru_cache
from itertools import combinations, combinations_with_replacement, permutations, product
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'src/reference_compiler'),str(ROOT/'experiments/joint_uncertainty')]
from fp_reference import positive_partition as partition
from fp_reference import query_projection as projection
from fp_reference.indexed_relation import DecodeAllowance,partition_shape_plan
from fp_reference.positive_tape import compile_tape
from fp_reference.indexed_amp import _finish_plan
from query_order_resource_frontier import subset_costs
from joint_model import data


def relabel(n,support,query,anchor):
    vertices = (anchor,)+tuple(v for v in range(n) if v!=anchor)
    local = {v:k for k,v in enumerate(vertices)}
    edges = tuple(sorted(tuple(sorted((local[u],local[v]))) for u,v in support))
    return vertices,edges,tuple(local[v] for v in query)


@lru_cache(maxsize=None)
def treewidth(n,edges):
    """Independent direct clique-fill enumeration, only through five vertices."""
    assert 1<=n<=5
    original = [set() for _ in range(n)]
    for u,v in edges:
        original[u].add(v)
        original[v].add(u)
    best = n
    for order in permutations(range(n)):
        graph = [set(neighbors) for neighbors in original]
        width = 0
        for v in order:
            neighbors = graph[v]
            width = max(width,len(neighbors))
            for u in neighbors:
                graph[u].update(neighbors-{u})
                graph[u].discard(v)
            graph[v] = set()
        best = min(best,width)
    return best


def small_width_audit():
    wide = DecodeAllowance(join_cells=32,live_cells=4096,arithmetic=10**8)
    graphs = queries = anchors = orders = strict = 0
    for n in range(2,6):
        edges = tuple(combinations(range(n),2))
        for mask in range(1<<len(edges)):
            support = tuple(e for k,e in enumerate(edges) if mask>>k&1)
            graphs += 1
            for query in combinations(range(n),2):
                augmented = tuple(sorted(set(support)|{query}))
                width = treewidth(n,augmented)
                costs = []
                for anchor in range(n):
                    _,local,q = relabel(n,support,query,anchor)
                    _,augmented_local,_ = relabel(n,augmented,query,anchor)
                    deleted = tuple((u-1,v-1) for u,v in augmented_local if u)
                    predicted = 1<<(treewidth(n-1,deleted)+1)
                    kept = tuple(sorted({v-1 for v in q if v}))
                    free = tuple(v for v in range(n-1) if v not in kept)
                    actual = 1<<n
                    for prefix in permutations(free):
                        shape = partition_shape_plan(n,local,q,prefix+kept,wide)
                        actual = min(actual,shape['largest_join_cells'])
                        orders += 1
                    assert actual==predicted,(n,support,query,anchor,actual,predicted)
                    assert 1<<width<=actual<=1<<(width+1)
                    costs.append(actual)
                    anchors += 1
                assert max(costs)<=2*min(costs)
                strict += max(costs)==2*min(costs)
                queries += 1
        print('WIDTH through n'+str(n)+': '+str(anchors)+' anchor decisions',flush=True)
    return {'supports':graphs,'nonloop_query_states':queries,'anchor_decisions':anchors,
        'direct_bucket_orders':orders,'queries_attaining_factor_two_variation':strict}


def gauge_audit():
    states = mapped_worlds = partitions = 0
    for n in range(2,5):
        edges = tuple(combinations(range(n),2))
        queries = tuple(combinations_with_replacement(range(n),2))
        for counts in product((-1,0,1),repeat=len(edges)):
            oracle = {q:[0,0] for q in queries}
            worlds = []
            for word in range(1<<(n-1)):
                z = (0,)+tuple((word>>k)&1 for k in range(n-1))
                weight = 9**sum(max(d,0) if z[u]==z[v] else max(-d,0) for (u,v),d in zip(edges,counts))
                worlds.append((z,weight))
                for u,v in queries:
                    oracle[u,v][z[u]^z[v]] += weight
            address = dict(zip(edges,counts))
            for anchor in range(n):
                vertices = (anchor,)+tuple(v for v in range(n) if v!=anchor)
                local = tuple(address[tuple(sorted((u,v)))] for u,v in combinations(vertices,2))
                seen = set()
                for z,weight in worlds:
                    w = tuple(z[v]^z[anchor] for v in vertices)
                    assert w[0]==0 and tuple(w[vertices.index(v)]^w[vertices.index(0)] for v in range(n))==z
                    assert 9**sum(max(d,0) if w[u]==w[v] else max(-d,0) for (u,v),d in zip(edges,local))==weight
                    seen.add(w)
                    mapped_worlds += 1
                assert len(seen)==1<<(n-1)
                for q in queries:
                    actual,_ = partition.decode(n,local,tuple(vertices.index(v) for v in q),order=tuple(range(n-1)))
                    assert actual==tuple(oracle[q])
                    partitions += 1
            states += 1
    return {'ternary_count_states':states,'bijective_world_images':mapped_worlds,
        'exact_partition_pairs':partitions,'full_counts_remain_in_original_coordinates':True}


def verify_cost(n,edges,q,result,join_cap,live_cap):
    shape = partition_shape_plan(n,edges,q,result['order'],
        DecodeAllowance(join_cells=join_cap,live_cells=live_cap,arithmetic=10**8))
    tape,heads = compile_tape(n,edges,q,order=result['order'],readout=False)
    positions = tuple(u*(2*n-u-1)//2+v-u-1 for u,v in edges)
    plan = _finish_plan(n,q,edges,positions,tuple(tape.nodes),heads,tuple(shape.items()),1<<30)
    assert (len(plan.nodes),plan.output_cells)==(result['partition_only_tape_nodes'],result['partition_only_output_cells'])
    return shape


def model_audit():
    rows = []
    for case,cursor in (((16,'iid-c4',18),276),((16,'iid-c2',17),332),
                        ((16,'iid-c4',18),372),((16,'iid-c4',19),368)):
        _,_,train,evaluation = data(case)
        tape = train+evaluation
        edges = tuple(combinations(range(16),2))
        addresses = {e:k for k,e in enumerate(edges)}
        counts = [0]*len(edges)
        for u,v,y in tape[:cursor]:
            if u!=v:
                counts[addresses[tuple(sorted((u,v)))]] += 1-2*y
        query = tuple(tape[cursor][:2])
        support = tuple(e for e,d in zip(edges,counts) if d)
        path = projection._path(16,support,query)
        assert len(path)==1 and path[0][0]==tuple(range(16))
        decisions = []
        for anchor in range(16):
            vertices,local,q = relabel(16,support,query,anchor)
            result = subset_costs(16,local,q)
            row = {'anchor':anchor,'minimum_output_cells':None,'nodes_at_minimum_output':None}
            if result is None:
                # Make the join-only lower bound independent of the live cap.
                assert subset_costs(16,local,q,4096,1<<20) is None
            else:
                shape = verify_cost(16,local,q,result,4096,32768)
                row.update(minimum_output_cells=result['partition_only_output_cells'],
                    nodes_at_minimum_output=result['partition_only_tape_nodes'],
                    local_order=result['order'],largest_join=shape['largest_join_cells'],
                    peak_live=shape['peak_live_integer_cells'])
            decisions.append(row)
        report = {'case':case,'cursor':cursor,'query':query,'all_anchor_decisions':decisions,
            'empty_join_classes':sum(d['minimum_output_cells'] is None for d in decisions)}
        feasible = [d for d in decisions if d['minimum_output_cells'] is not None]
        if feasible:
            report['best_output_then_nodes_then_anchor'] = min(feasible,
                key=lambda d:(d['minimum_output_cells'],d['nodes_at_minimum_output'],d['anchor']))
        else:
            _,local,q = relabel(16,support,query,0)
            result = subset_costs(16,local,q,8192,32768)
            assert result is not None
            shape = verify_cost(16,local,q,result,8192,32768)
            assert shape['largest_join_cells']==8192
            report['minimum_join_over_all_anchors'] = 8192
            report['matching_anchor0_order'] = result['order']
            report['matching_shape'] = shape
        rows.append(report)
        print('MODEL '+str(case)+'/'+str(cursor)+': '+str(report['empty_join_classes'])+' empty anchor classes',flush=True)
    return rows


def audit():
    result = {'status':'PASS_EXACT_GAUGE_AND_QUERY_WIDTH','scope':'passive structural/partition audit; no funded search, AMP conformance or Runtime authority',
        'law':'minimum_join(anchor a) = 2^(tw((G + query edge) - a)+1); anchor variation at most a factor of two',
        'small_width':small_width_audit(),'gauge':gauge_audit(),'selected_model_cuts':model_audit()}
    assert 'torch' not in sys.modules
    return result


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'evidence/minimal/FP_QUERY_ANCHOR_RESOURCE.json')
    args = parser.parse_args()
    result = audit()
    serialized = json.loads(json.dumps(result))
    if args.output.exists():
        assert json.loads(args.output.read_text(encoding='utf-8'))==serialized
    else:
        args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='selected_model_cuts'}),flush=True)
