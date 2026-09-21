"""Exact lossless phase-codec audit; no owned CUDA execution is inferred."""
from dataclasses import dataclass, replace
from fractions import Fraction as F
from itertools import combinations, product
from pathlib import Path
from unittest.mock import patch
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'),str(ROOT/'experiments/joint_uncertainty')]
from fp_reference import phase_encoding as codec, indexed_amp as amp
from fp_reference.encoding import pack, packed_size
from fp_reference.core import ContractError
from fp_reference.resources import ResourceExceeded
from fp_reference.semantics import ArithmeticUnresolved
from fp_reference.indexed_count import CountState
from fp_reference.indexed_execution import IndexedState, IndexedEvaluation
from fp_reference.indexed_relation import IndexedRelation, DecodeAllowance, partition_shape_plan
from fp_reference.positive_tape import compile_tape
from fp_reference import positive_partition as partition
from fp_reference.cuda_prefix import IndexedCudaPhase
from fp_reference.float64_bridge import Float64Contract
from joint_model import data


def encode(value,*,cap=4<<20):
    size = codec.extent(value,encoded_cap=cap)
    result = bytearray(size.encoded_bytes)
    assert codec.write(value,result)==size
    assert codec.check(result,value)==size.expanded_bytes
    return bytes(result),size


def refuses(call,kind=(ContractError,ResourceExceeded)):
    try:
        call()
    except kind:
        return
    raise AssertionError('malformed or unfunded codec operation was accepted')


@dataclass(frozen=True)
class TypedFixture:
    name: str
    value: object


def primitive_audit():
    strings = ('','x','x'*300,'\x00\x7f\\\"','\U0001f600','\ud83d\ude00',
        '\ud800','\udfff','\u07ff\u0800\uffff\U00010000')
    values = [None,False,True,*strings,(),[],tuple(range(15)),list(range(16)),
        {F(1,2):'x','x':(True,1)},TypedFixture('x',('x','x',F(0)))]
    values.extend(range(-1024,1025))
    values.extend(F(a,b) for a,b in product(range(-32,33),range(1,18)))
    values.extend(sign*((1<<k)-1) for k in (7,8,31,32,63,64,32768) for sign in (-1,1))
    values.extend((s,[s,True,1,None],{s:TypedFixture(s,('x',F(-1,9)))}) for s in strings)
    encoded_bytes = expanded_bytes = 0
    for value in values:
        raw,size = encode(value)
        assert b''.join(codec.decoded_fragments(raw))==pack(value)
        encoded_bytes += len(raw)
        expanded_bytes += size.expanded_bytes
    assert encode('\U0001f600')[0] != encode('\ud83d\ude00')[0]
    assert len({encode(v)[0] for v in (None,False,True,0,1,F(0),F(1),'0',(),[])})==10
    poisoned = bytearray(b'!'*31)
    before = bytes(poisoned)
    refuses(lambda:codec.write(tuple(range(100)),poisoned),ResourceExceeded)
    assert bytes(poisoned)==before
    nested = None
    for _ in range(codec.MAX_DEPTH+1):
        nested = (nested,)
    with patch.object(codec,'packed_size',side_effect=AssertionError('unadmitted old encoding traversal')):
        refuses(lambda:codec.extent(nested,encoded_cap=4096),ResourceExceeded)
        refuses(lambda:codec.extent(1<<codec.INTEGER_BITS,encoded_cap=4096),ResourceExceeded)
    refuses(lambda:encode(tuple(str(k) for k in range(codec.MAX_STRINGS+1))),ResourceExceeded)
    bomb,_ = encode(('a'*1024,)*1024)
    refuses(lambda:b''.join(codec.decoded_fragments(bomb,expanded_cap=4096)),ResourceExceeded)
    malformed = (b'',b'\xff',b'\x03\x80\x00',b'\x06\x00',b'\x05\x01\x80',
        b'\x04\x02\x00',b'\x04\x04\x04',b'\x09\x00',b'\x00\x00',
        b'\x22\x05\x01a\x05\x01a',b'\x03'+b''.join(codec._uint((1<<(codec.INTEGER_BITS+1))-1)))
    for raw in malformed:
        refuses(lambda raw=raw:b''.join(codec.decoded_fragments(raw)))
    return {'typed_round_trips':len(values),'encoded_bytes':encoded_bytes,
        'exact_legacy_bytes_reconstructed':expanded_bytes,'malformed_streams_refused':len(malformed),
        'resource_and_prewrite_refusals':5,'source_code_points_and_primitive_types_distinct':True}


def state_at(case,cursor):
    _,_,train,evaluation = data(case)
    edges = tuple(combinations(range(case[0]),2))
    addresses = {edge:k for k,edge in enumerate(edges)}
    values = [0]*len(edges)
    for i,j,y in (train+evaluation)[:cursor]:
        if i!=j:
            values[addresses[tuple(sorted((i,j)))]] += 1-2*y
    return CountState(case[0],tuple(values),None,cursor,cursor)


def phase_fixture(n,state,query,order):
    schema = IndexedRelation(n)
    edges = tuple(combinations(range(n),2))
    support = tuple(edge for edge,d in zip(edges,state.counts) if d)
    shape = partition_shape_plan(n,support,query,order,DecodeAllowance())
    graph,heads = compile_tape(n,support,query,order=order,readout=False)
    plan = amp._finish_plan(n,query,support,tuple(edges.index(e) for e in support),
        tuple(graph.nodes),heads,tuple(shape.items()),1<<20)
    parts,stats = partition.decode(n,state.counts,query,order=order)
    excesses = tuple(8*F(value,sum(parts)) for value in parts)
    masses = tuple(1+e for e in excesses)
    reference = IndexedEvaluation(state,query,excesses,masses,F(10),tuple(m/10 for m in masses),tuple(stats.items()))
    before,arithmetic = amp.IndexedAmpState(state),amp._Arithmetic(32768)
    raw,_ = amp.execute_prediction(plan,before,arithmetic)
    operations = tuple(('host-RNE32-ingress' if tag=='constant' else
        'cast-float'+str(width) if tag=='cast' else tag,width,(word,)) for tag,width,word in arithmetic.trace)
    assert amp.check_prediction_execution(plan,before,raw,operations,bit_limit=32768)==len(operations)
    try:
        relation = amp.check_prediction(reference,raw,Float64Contract(F(1,100),F(1,1000)),
            normalizer_cap=F(18),activation_cap=F(8),bit_limit=32768)
        numerical = 'PASS_POINT_RELATION'
    except ArithmeticUnresolved as exc:
        relation,numerical = None,str(exc)
    phase = IndexedCudaPhase('codec-fixture:phase','codec-fixture:candidate',schema.program_id,
        'ordinary:predict',state.cursor,'codec-fixture:actual-query','codec-fixture:predecessor',None,
        IndexedState(state),reference,before,raw,operations,relation,plan.output_cells,None,
        'PASSIVE_CPU_RNE_RECORD','no actual CUDA or Runtime authority',len(operations),execution_plan=plan)
    return phase,numerical


def phase_audit():
    tiny,_ = phase_fixture(3,CountState(3,(1,-1,2),None,4,4),(1,2),(0,1))
    raw,size = encode(tiny)
    substitutions = 0
    for k in range(len(raw)):
        for bit in range(8):
            changed = bytearray(raw)
            changed[k] ^= 1<<bit
            refuses(lambda:codec.check(changed,tiny,expanded_cap=size.expanded_bytes))
            substitutions += 1
    for end in range(len(raw)):
        refuses(lambda end=end:codec.check(raw[:end],tiny,expanded_cap=size.expanded_bytes))
    frontier = json.loads((ROOT/'evidence/minimal/FP_QUERY_ORDER_RESOURCE_FRONTIER.json').read_text())
    rows = []
    for row in frontier['tapes']:
        case,witness = tuple(row['case']),row['maximum_output_witness']
        assert len(witness['blocks'])==1 and witness['blocks'][0]['vertices']==list(range(16))
        state = state_at(case,witness['cursor'])
        phase,numerical = phase_fixture(16,state,tuple(witness['query']),tuple(witness['blocks'][0]['order']))
        payload,extent = encode(phase)
        # The independent old encoder and decoder materialize only in this
        # passive audit. Production will need paid streaming retention.
        assert b''.join(codec.decoded_fragments(payload))==pack(phase)
        assert extent.expanded_bytes > 4<<20 and extent.encoded_bytes < 4<<20
        rows.append({'case':case,'cursor':state.cursor,'query':witness['query'],
            'tape_nodes':len(phase.execution_plan.nodes),'floating_outputs':phase.output_cells,
            'encoded_bytes':extent.encoded_bytes,'legacy_bytes':extent.expanded_bytes,
            'string_definitions':extent.string_definitions,'point_numerical_relation':numerical,
            'fixed_old_output_cap_fits':phase.output_cells<=65536})
        print('PHASE '+str(case)+': '+str(extent.expanded_bytes)+' -> '+str(extent.encoded_bytes)+' bytes',flush=True)
    return {'complete_record_bit_substitutions_refused':substitutions,
        'complete_record_truncations_refused':len(raw),'full_phase_scope':'passive exact RNE candidate orders, not registered or executed CUDA phases',
        'model_prefix_records':rows}


def indexed_byte_bound(phase,extent):
    """A structural upper bound, with independently encoded non-tape data."""
    plan = phase.execution_plan
    nodes,operations = plan.nodes,phase.raw_operations
    assert len(nodes)<=262144 and len(operations)<1<<21 and extent.string_definitions<=128
    assert len(plan.power_tags)==len(nodes) and all(type(v) is bool for v in plan.power_tags)
    for node in nodes:
        assert node[0] in ('zero','one','nine','factor','add','mul')
        assert len(node)==(1 if node[0] in ('zero','one','nine') else 3)
        assert all(type(v) is int and 0<=v<262144 for v in node[1:])
    for tag,width,words in operations:
        assert type(tag) is str and width in (16,32) and len(words)==1
        assert type(words[0]) is int and 0<=words[0]<1<<width
    assert len(operations)<=phase.output_cells
    removed = {node[0] for node in nodes}|{tag for tag,_,_ in operations}
    definitions = sum(1+len(b''.join(codec._uint(len(s.encode('utf-8','surrogatepass')))))
        +len(s.encode('utf-8','surrogatepass')) for s in removed)
    skeleton = replace(phase,execution_plan=replace(plan,nodes=(),power_tags=()),raw_operations=())
    metadata = codec.extent(skeleton,encoded_cap=codec.EXPANDED_CAP).encoded_bytes
    # Three sequence length headers grow by at most three bytes each.
    residual = metadata+definitions+9
    upper = 12*(len(nodes)+phase.output_cells)+residual
    assert extent.encoded_bytes<=upper
    return {'non_tape_record_bytes':metadata,'removed_string_definition_allowance':definitions,
        'metadata_allowance_B':residual,'encoded_upper_bound':upper,
        'four_MiB_sufficient_at_registered_N_C_caps':residual<=262136}


def bound_audit():
    prior = json.loads((ROOT/'evidence/minimal/FP_PHASE_ENCODING_CPU.json').read_text())
    frontier = json.loads((ROOT/'evidence/minimal/FP_QUERY_ORDER_RESOURCE_FRONTIER.json').read_text())
    rows = []
    for previous,row in zip(prior['phase']['model_prefix_records'],frontier['tapes']):
        case,witness = tuple(row['case']),row['maximum_output_witness']
        phase,numerical = phase_fixture(16,state_at(case,witness['cursor']),
            tuple(witness['query']),tuple(witness['blocks'][0]['order']))
        extent = codec.extent(phase,encoded_cap=4<<20)
        assert extent.encoded_bytes==previous['encoded_bytes'] and extent.expanded_bytes==previous['legacy_bytes']
        result = {'case':case,'cursor':witness['cursor'],'query':witness['query'],
            'tape_nodes':len(phase.execution_plan.nodes),'floating_outputs':phase.output_cells,
            'encoded_bytes':extent.encoded_bytes,**indexed_byte_bound(phase,extent)}
        rows.append(result)
        print('BOUND '+str(case)+' B='+str(result['metadata_allowance_B']),flush=True)
    return {'status':'PASS_INDEXED_PHASE_BYTE_BOUND','law':'E <= 12*(N+C)+B',
        'scope':'fixed scalar indexed records with N<=262144, at most128 strings, and stated metadata allowance; not arbitrary FP records',
        'rows':rows}


def regression_audit():
    import ast
    import audit_cuda_frame_storage as storage
    from audit_indexed_amp import cpu_audit
    from audit_phase_retention import audit as retention_audit
    repeated = ('x'*1024,)*1024
    with patch.object(codec,'packed_size',side_effect=AssertionError('unfunded aggregate legacy traversal')):
        refuses(lambda:codec.extent(repeated,encoded_cap=4096,expanded_cap=65536),ResourceExceeded)
        refuses(lambda:codec.check(b'\x00',repeated,expanded_cap=65536),ResourceExceeded)
    raw = b'\x05'+b''.join(codec._uint(1024))+b'x'*1024
    try:
        b''.join(codec.decoded_fragments(raw,expanded_cap=16))
    except ResourceExceeded as exc:
        assert 'string exceeds its remaining' in str(exc)
    else:
        raise AssertionError('oversized string reached decoded output')
    primitive = primitive_audit()
    retained = json.loads((ROOT/'evidence/minimal/FP_PHASE_ENCODING_CPU.json').read_text())
    assert primitive==retained['primitive']
    # The old storage experiment explicitly binds the pre-indexed constructor.
    # Preserve that old scope; this regression instead compares all three
    # unchanged storage methods with the immediate pre-codec research source.
    def methods(text):
        root = next(n for n in ast.parse(text).body if isinstance(n,ast.ClassDef) and n.name=='ReferenceCompilerRuntime')
        return {n.name:ast.dump(n) for n in root.body if isinstance(n,ast.FunctionDef)
            and n.name in ('__init__','snapshot','_seal_cuda_frame')}
    path = 'src/reference_compiler/fp_reference/runtime.py'
    previous = methods(storage.git('show','e8fa568:'+path))
    current = methods((ROOT/path).read_text(encoding='utf-8'))
    assert previous==current and len(current)==3
    old = methods(storage.git('show',storage.BASELINE+':'+path))
    assert old['__init__']!=current['__init__'] and old['snapshot']==current['snapshot']
    comparison = {'baseline':storage.git('rev-parse','e8fa568'),
        'constructor_snapshot_and_sealer_AST_unchanged_since_precodec':True,
        'old_storage_experiment_anchor':storage.git('rev-parse',storage.BASELINE),
        'old_constructor_predicate':'FAILS_ALREADY_BEFORE_CODEC_DUE_TO_INDEXED_EXTENSION; no old-scope rerun claim'}
    with patch.object(storage,'source_check',lambda:comparison):
        frame_result = storage.exact_audit()
    result = {'status':'PASS_PHASE_ENCODING_CPU_REGRESSIONS',
        'aggregate_length_preflight_refusals':2,'oversized_raw_string_refused_before_copy':True,
        'current_primitive_audit':primitive,'immutable_frame_audit':frame_result,
        'owned_retention_hook':retention_audit(),'unchanged_exact_RNE_bridge':cpu_audit()}
    assert 'torch' not in sys.modules
    return result


def compression_audit():
    """Strong conventional byte baseline; passive, outside Runtime authority."""
    import subprocess
    import zlib
    source = subprocess.check_output(('git','rev-parse','HEAD'),cwd=ROOT,encoding='utf-8').strip()
    report = {'status':'PASS_PASSIVE_FULL_RECORD_COMPRESSION','execution_source':source,
        'scope':'ordinary zlib level6 against both complete legacy and typed-binary phase payloads; exact decompression only, no Runtime or resource authority',
        'zlib_runtime':zlib.ZLIB_RUNTIME_VERSION,'level':6,'rows':[]}
    frontier = json.loads((ROOT/'evidence/minimal/FP_QUERY_ORDER_RESOURCE_FRONTIER.json').read_text())
    for row in frontier['tapes']:
        case,w = tuple(row['case']),row['maximum_output_witness']
        phase,_ = phase_fixture(16,state_at(case,w['cursor']),tuple(w['query']),tuple(w['blocks'][0]['order']))
        raw = pack(phase)
        extent = codec.extent(phase,encoded_cap=4<<20)
        binary = bytearray(extent.encoded_bytes)
        assert codec.write(phase,binary)==extent
        first,second = zlib.compress(raw,6),zlib.compress(binary,6)
        assert zlib.decompress(first)==raw and zlib.decompress(second)==binary
        assert codec.check(binary,phase)==len(raw)
        result = {'case':case,'cursor':w['cursor'],'query':w['query'],'legacy_bytes':len(raw),
            'typed_binary_bytes':len(binary),'zlib_legacy_bytes':len(first),'zlib_binary_bytes':len(second),
            'exact_complete_decompression':True}
        report['rows'].append(result)
        print(json.dumps(result),flush=True)
    return report


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bounds',action='store_true')
    parser.add_argument('--regressions',action='store_true')
    parser.add_argument('--compression',action='store_true')
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    if args.compression:
        report = compression_audit()
        args.output = args.output or ROOT/'evidence/minimal/FP_PHASE_COMPRESSION_CPU_A1.json'
    elif args.regressions:
        report = regression_audit()
        args.output = args.output or ROOT/'evidence/minimal/FP_PHASE_ENCODING_REGRESSION_CPU.json'
    elif args.bounds:
        report = bound_audit()
        args.output = args.output or ROOT/'evidence/minimal/FP_PHASE_ENCODING_BOUND_CPU.json'
    else:
        primitive = primitive_audit()
        print('PRIMITIVES '+str(primitive['typed_round_trips']),flush=True)
        phases = phase_audit()
        report = {'status':'PASS_LOSSLESS_TYPED_PHASE_CPU','codec':codec.ENCODING_ID,
            'scope':'exact byte reconstruction and passive CPU RNE records; no Runtime, GPU, whole-memory or installation claim',
            'primitive':primitive,'phase':phases}
        args.output = args.output or ROOT/'evidence/minimal/FP_PHASE_ENCODING_CPU.json'
    assert 'torch' not in sys.modules
    normalized = json.loads(json.dumps(report))
    if args.output.exists():
        prior = json.loads(args.output.read_text())
        # Reproduction compares all observations while preserving the first
        # observation's provenance. The initial compression audit was inline;
        # this function makes those exact steps a reusable repository command.
        if args.compression:
            normalized['execution_source']=prior['execution_source']
        assert prior==normalized
    else:
        args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status']}),flush=True)
