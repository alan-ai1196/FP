"""Actual Runtime lossless indexed causal source integration."""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import struct
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'experiments/next_token'), str(ROOT/'scripts')]
from fp_reference import ConstructionContract, OnlineContract, ReferenceCompilerRuntime
from fp_reference.core import ContractError
from fp_reference.data_usage import DataContract, StreamSpec, source_mapping
from fp_reference.encoding import packed_size
from fp_reference.info import Moment, QuerySpec, evaluate_query
from fp_reference.ingress import encode_context
from fp_reference.learner import LearnerSpec
from fp_reference.profile import ProfileSpec
from fp_reference.program import Program, SemanticRules, Source
from fp_reference.token_sources import TokenAtomFamily, TokenSourceReads, TokenContext
from audit_reference_construction import limits, rejects, validate_residency
from audit_native_tokens import fixture, same
import audit_token_runtime_sources as literal

ORIGINAL_REGISTRATION = literal.registration


def registration(d, initial, count=4, *, profile=None):
    cfg, graph, online = ORIGINAL_REGISTRATION(d, initial, count, profile=profile)
    family = TokenAtomFamily(d.sources.vocabulary, d.sources.context)
    cfg = replace(cfg, semantics=replace(cfg.semantics, sources=family))
    return cfg, graph, replace(online, data=replace(online.data, source_reads=TokenSourceReads(family)))


def histories():
    words = events = atoms = commits = 0
    for unit, kind, word in product((1, 2), ('mixed', 'zero-embedding', 'zero-core'), product((0, 1), repeat=4)):
        d, native = fixture(unit, kind)
        cfg, graph, online = registration(d, native)
        rt = ReferenceCompilerRuntime(cfg, graph, online=online)
        for t, target in enumerate(word):
            expected = native.predict()
            prediction = rt.predict_next(f'train/{t}', encode_context(()))
            assert prediction.status == 'PREDICTED_REFERENCE'
            state = validate_residency(rt)
            context = state.pending.record.sources
            assert type(context) is TokenContext and context.position == t
            values = source_mapping(context)
            for spec in cfg.semantics.sources:
                lag, token = context.family.coordinates(spec.source_id)
                assert spec.availability_delay == lag and spec.type_id == 'f' and spec.upper == 1
                assert values[spec.source_id] == expected.window.atom(lag, token)
                atoms += 1
            assert prediction.predictions[0][1] == tuple(expected.output.mass(y)/expected.output.normalizer for y in range(d.output.labels))
            assert rt.observe(target).status == 'OBSERVED_REFERENCE'
            native = native.observe(expected, target)
            if native.output.unit_count == unit:
                native = native.commit()
                commits += 1
            state = validate_residency(rt)
            same(native, next(s.learner for s in state.candidates if s.candidate_id == state.deployed_id))
            assert state.observations[-1].sources == context
            events += 1
        words += 1
    return dict(histories=words, owned_observations=events, optimizer_commits=commits,
        all_atom_type_delay_value_checks=atoms, complete_native_state_and_buffer_ownership_match=True)


def queries_and_attacks():
    d, root = fixture(2, 'mixed')
    cfg, graph, online = registration(d, root)
    query = QuerySpec('past-products', (Moment(('lag1/token2',)), Moment(('lag1/token0', 'lag2/token2'), 1)),
        (F(0), F(0)), (F(1), F(1)), 8, 4)
    online = replace(online, queries=(query,))
    rt = ReferenceCompilerRuntime(cfg, graph, online=online)
    for t, target in enumerate((0, 1, 1, 0)):
        assert rt.predict_next(f'train/{t}', encode_context(())).status == 'PREDICTED_REFERENCE'
        assert rt.observe(target).status == 'OBSERVED_REFERENCE'
    records = rt.snapshot().observations
    dense = tuple(replace(r, sources=tuple(source_mapping(r.sources).items())) for r in records)
    result = rt.query(query.query_id, tuple(r.observation_id for r in records))
    assert result == evaluate_query(query, dense, bit_limit=32768)
    assert rt.snapshot().data_uses[-1].purpose == 'proposal'
    family = cfg.semantics.sources
    for invalid in ('lag0/token0', 'lag4/token0', 'lag1/token3', 'lag01/token0', 'lag1/token+0', 'lag1/token-1'):
        rejects(lambda: family.coordinates(invalid))
    rejects(lambda: TokenContext(family, 0, (0, 2, 2)))
    rejects(lambda: TokenContext(family, 1, (2, 2, 2)))
    rejects(lambda: replace(online.data, input_upper=(F(1),)))
    rejects(lambda: replace(online.data, source_reads=TokenSourceReads(TokenAtomFamily(3, 3))).validate(cfg.semantics))
    rejects(lambda: replace(online.data, active_stream='heldout'))
    forged = replace(family)
    object.__setattr__(forged, 'context', 0)
    rejects(lambda: TokenSourceReads(forged))
    for metadata in (replace(family), TokenSourceReads(family), TokenContext(family, 0, (2, 2, 2))):
        object.__setattr__(metadata, 'hidden_source', (1, 0, 1))
        rejects(metadata.__post_init__)
    rejects(lambda: TokenAtomFamily(1 << 63, 1))
    rt = ReferenceCompilerRuntime(cfg, graph, online=online)
    rejects(lambda: rt.predict_next('train/0', encode_context((1,))))
    assert validate_residency(rt).halted is not None
    return dict(owned_query_coordinates=2, exact_dense_query_equality=True,
        malformed_context_role_reader_and_ingress_refusals=17, information_use_retained=True)


def full_vocabulary():
    V, L = 50257, 512
    family = TokenAtomFamily(V, L)
    query = QuerySpec('any-old-atom', (Moment((f'lag512/token{V}',)), Moment(('lag1/token0',))),
        (F(0), F(0)), (F(1), F(1)), 8, 4)
    data = DataContract((StreamSpec('train', 'train', tuple(f'train/{i}' for i in range(4))),),
        'train', (), TokenSourceReads(family))
    graph = Program((Source(f'lag512/token{V}'),), 0, (0,)*V)
    # An elementary supplied graph isolates the source integration. It is
    # neither the full token learner nor a language-quality experiment.
    with patch.object(TokenAtomFamily, '__getitem__', side_effect=AssertionError('full atom enumeration is forbidden')):
        rules = SemanticRules(family, ('f',), (('f', 'f', 'f'),), 'f', (F(1, V),)*V)
        cfg = ConstructionContract(rules, limits(byte_cap=256 << 20, work_cap=10**9),
            {'construct': 'compiler', 'range_audit': 'compiler'},
            {'nodes': 1, 'SUMs': 0, 'PRODUCTs': 0, 'edges': 0, 'slots': 0}, (F(0),), F(V+2), F(1), 32768)
        online = OnlineContract(data, LearnerSpec(1, F(1, 16), 16), queries=(query,))
        rt = ReferenceCompilerRuntime(cfg, graph, online=online)
        path = Path(r'F:\experiment\FP_Scaling_Trial_1R_RTX3090_WindowsGlobal_OneClick\data\train.bin')
        before = path.stat()
        assert before.st_size == 360000000
        with path.open('rb') as stream:
            payload = stream.read(8)
        after = path.stat()
        assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
        word = struct.unpack('<4H', payload)
        maximum_context_bytes = 0
        for t, target in enumerate(word):
            result = rt.predict_next(f'train/{t}', encode_context(()))
            assert result.status == 'PREDICTED_REFERENCE'
            assert all(p == F(1, V) for p in result.predictions[0][1])
            context = rt.snapshot().pending.record.sources
            assert context.past == tuple(V if lag > t else word[t-lag] for lag in range(1, L+1))
            maximum_context_bytes = max(maximum_context_bytes, packed_size(context))
            assert rt.observe(target).status == 'OBSERVED_REFERENCE'
        assert rt.query(query.query_id, tuple(f'train/{i}' for i in range(4))).status == 'ANSWERED'
        state = validate_residency(rt)
        assert state.cursor == 4 and state.halted is None
    return dict(vocabulary=V, context=L, complete_primitive_source_count=len(family), runtime_observations=4,
        atom_enumeration_attempts=0, maximum_packed_source_context_bytes=maximum_context_bytes,
        all_full_vocabulary_probabilities_checked=True, owned_query_pass=True, source_bytes_read=8,
        source_path=str(path), corpus_identity_source='evidence/minimal/FP_NEXT_TOKEN_DATA_ENTRY.json',
        validation_or_test_read=False, loss_scored=False,
        scope='source integration with supplied elementary graph; no packed token learner, whole-host, AMP or model claim')


def admission_before_decoding():
    import fp_reference.runtime as implementation
    family = TokenAtomFamily(2, 50000)
    rules = SemanticRules(family, ('f',), (), 'f', (F(1), F(1)))
    graph = Program((Source('lag1/token2'),), 0, (0, 0))
    cfg = ConstructionContract(rules, limits(byte_cap=1 << 20, work_cap=200000),
        {'construct': 'compiler', 'range_audit': 'compiler'},
        {'nodes': 1, 'SUMs': 0, 'PRODUCTs': 0, 'edges': 0, 'slots': 0}, (F(0),), F(4), F(1), 32768)
    data = DataContract((StreamSpec('train', 'train', ('train/0',)),), 'train', (), TokenSourceReads(family))
    online = OnlineContract(data, LearnerSpec(1, F(1, 16), 16))
    rt = ReferenceCompilerRuntime(cfg, graph, online=online)
    with patch.object(implementation, 'read_sources', side_effect=AssertionError('unfunded source decoder ran')) as decoder:
        result = rt.predict_next('train/0', encode_context(()))
        assert result.status == 'UNRESOLVED'
        assert not decoder.called
    state = validate_residency(rt)
    assert state.cursor == 0 and state.halted is not None and not state.observations
    return dict(source_decode_denied_before_history_copy_or_context_allocation=True,
        original_ingress_failure_retained=True, predictions_published=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = dict(status='PASS_OWNED_INDEXED_TOKEN_SOURCES')
    result['histories'] = histories()
    print('PASS histories', flush=True)
    with patch.object(literal, 'registration', side_effect=registration):
        result['profiles'] = literal.profiles()
    print('PASS original-context profiles', flush=True)
    result['queries_and_attacks'] = queries_and_attacks()
    print('PASS queries and attacks', flush=True)
    result['source_work_admission'] = admission_before_decoding()
    print('PASS source work admission', flush=True)
    result['full_vocabulary'] = full_vocabulary()
    print('PASS actual full-vocabulary source integration', flush=True)
    assert 'torch' not in sys.modules
    if args.write:
        (ROOT/'evidence/minimal/FP_INDEXED_TOKEN_SOURCES.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
