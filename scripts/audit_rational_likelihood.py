"""Actual rational descriptor/decoder and Runtime payment boundary, CPU only.

The funding probe substitutes a refusing backend, never a successful device
phase. Native and rounding oracles are independent of the production decoder.
"""
from dataclasses import replace
from fractions import Fraction as F
from itertools import product
from math import gcd, lcm
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch
import argparse
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts'),
               str(ROOT/'experiments/joint_uncertainty')]
from fp_reference import ReferenceCompilerRuntime
from fp_reference.core import ContractError, stable_hash
from fp_reference.encoding import pack
from fp_reference import learner as native
from fp_reference import likelihood_encoding as encoding
from fp_reference import cuda_learner
from fp_reference.cuda_prefix import output_cells, IndexedCudaPrefixContract
from fp_reference.data_usage import DataContract, SourceRead, StreamSpec
from fp_reference.resources import ObjectSpec, ResourceExceeded
from fp_reference.runtime import OnlineContract
from fp_reference.program import Program, Sum, Term
from fp_reference.semantics import ArithmeticUnresolved, evaluate
from audit_cuda_runtime import cuda_contract
from audit_likelihood_encoding import verify_model, expected_metadata, rounded_rational_commit
from audit_cuda_learner import model_initial, SINGLE
from audit_reference_construction import contract, limits, rejects, validate_residency
import likelihood_information as finite
import noise_acquisition as noise

BITS = 32768
BUDGET = encoding.RationalLikelihoodContract(basis_cells=8)
OUTPUT = ROOT/'evidence/minimal/FP_RATIONAL_LIKELIHOOD_CPU.json'


def fixtures():
    banks = finite.models() | {'prior_only_factor':
        (finite.bernoulli(((F(1, 2),)*2,), (F(1, 8), F(7, 8))), 3, 0)}
    for name, (model, depth, _) in banks.items():
        rules, graph, spec, scale = finite.native_graph(model)
        domain = tuple(tuple(F(i == x) for i in range(len(model.table))) for x in range(len(model.table)))
        step = lambda s, e, m=model, b=(rules, graph, spec, scale): finite.native_step(m, b, s, e)
        yield name, model, rules, graph, spec, domain, step, depth
    for n, depth in ((2, 3), (3, 2)):
        bundle = noise.native_contract(n)
        model, rules, graph, spec, _ = bundle
        domain = tuple(noise.source_point(n, p) for p in product(range(n), repeat=2))
        step = lambda s, e, n=n, b=bundle: noise.native_step(n, b, s, (e[0]//n, e[0]%n, e[1]))
        yield f'joint_noise_n{n}', model, rules, graph, spec, domain, step, depth


def derive(fixture, budget=BUDGET, bits=BITS, **kwargs):
    _, model, rules, graph, spec, domain, _, _ = fixture
    work = encoding.preparation_work(graph, rules, spec, domain, bits, budget)
    return encoding.prepare_model(graph, rules, (F(1),)+model.prior, spec, domain, budget,
        bit_limit=bits, **({'work_limit': work} | kwargs))


def primitive(joint):
    denominator = lcm(*(v.denominator for v in joint))
    weights = tuple(v.numerator*(denominator//v.denominator) for v in joint)
    divisor = gcd(*weights)
    return tuple(v//divisor for v in weights)


def exact_audit():
    result = []
    for fixture in fixtures():
        name, bank, rules, graph, spec, domain, step, depth = fixture
        model = derive(fixture)
        audited_bank, representatives = verify_model(model, graph, rules, (F(1),)+bank.prior, spec, domain)
        assert audited_bank == bank.factors and model.rank == finite.Coordinates(bank).rho
        encoded = encoding.EncodedLikelihoodState(model, (0,)*model.rank, None)
        native_state = native.initial_state(graph, rules, (F(1),)+bank.prior, 0, spec=spec, bit_limit=BITS)
        physical = model_initial(graph, rules, (F(1),)+bank.prior, 0)
        levels = [(native_state, encoded, bank.prior)]
        cases = 0
        with memoryview(bytearray(encoding.decode_workspace(model, BITS))) as scratch:
            for time in range(1, depth+1):
                following = []
                for before, state, joint in levels:
                    for a, event in enumerate(bank.events):
                        actual = step(before, event)
                        query, target = event
                        pending = state.observe(query, target)
                        assert pending.raw() == expected_metadata(model, audited_bank, representatives, joint, time-1, a)
                        count = output_cells('commit', graph, rules, spec, encoded_state=pending,
                                             steps=time-1, bit_limit=BITS)
                        successor = pending.commit()
                        next_joint = tuple(v*p for v, p in zip(joint, bank.factors[a]))
                        values = encoding.joint_inputs(successor, time, bit_limit=BITS, workspace=scratch)
                        weights = primitive(next_joint)
                        scale = 1 << max(v.bit_length() for v in weights)
                        assert values == tuple(F(v, scale) for v in weights)
                        assert finite.normalize(values) == actual.theta[1:]
                        stride = (BITS+7)//8
                        assert tuple(int.from_bytes(scratch[i*stride:(i+1)*stride], 'little') for i in range(bank.worlds)) == weights
                        assert successor.raw() == expected_metadata(model, audited_bank, representatives, next_joint, time, None)
                        _, trace, cells = rounded_rational_commit(physical, spec, next_joint)
                        assert cells == count == 1+3*bank.worlds+2*graph.slot_count
                        assert trace[0] == ('host-RNE32-ingress', 32, tuple(SINGLE.rounded(v) for v in values))
                        following.append((actual, successor, next_joint))
                        cases += 1
                levels = following
        result.append({'bank': name, 'rank': model.rank, 'bases': model.factor_bases,
                       'complete_native_triples': cases, 'derivation_operations': model.preparation_operations,
                       'prepaid_derivation': encoding.preparation_work(graph, rules, spec, domain, BITS, BUDGET),
                       'prepaid_scratch': encoding.preparation_workspace(graph, rules, spec, domain, BITS, BUDGET),
                       'integer_decode_scratch': encoding.decode_workspace(model, BITS)})
    return result


def adversarial():
    fixture = tuple(fixtures())[-2]
    model = derive(fixture)
    state = encoding.EncodedLikelihoodState(model, (0,)*model.rank, None).observe(0, 0).commit()
    size = encoding.decode_workspace(model, BITS)
    scratch = bytearray(size)
    wrong = (None, memoryview(bytearray(size-1)), memoryview(bytes(size)), memoryview(bytearray(2*size))[::2])
    for view in wrong:
        rejects(lambda v=view: encoding.joint_inputs(state, 1, bit_limit=BITS, workspace=v))
    for view in wrong[1:]:
        view.release()
    for field in ('factor_work', 'decode_work', 'basis_cells'):
        rejects(lambda f=field: replace(BUDGET, **{f: 0}))
    rejects(lambda: derive(fixture, replace(BUDGET, factor_work=1)), ArithmeticUnresolved)
    rejects(lambda: derive(fixture, replace(BUDGET, basis_cells=1)), ArithmeticUnresolved)
    rejects(lambda: derive(fixture, work_limit=1), ArithmeticUnresolved)
    low_work = replace(state, model=replace(model, contract=replace(BUDGET, decode_work=1)))
    before = bytes(scratch)
    rejects(lambda: encoding.joint_inputs(low_work, 1, bit_limit=BITS, workspace=memoryview(scratch)), ArithmeticUnresolved)
    assert bytes(scratch) == before
    low_precision = encoding.EncodedLikelihoodState(model, (0,)*model.rank, None)
    for _ in range(80):
        low_precision = low_precision.observe(1, 0).commit()
    tiny = bytearray(encoding.decode_workspace(model, 64))
    rejects(lambda: encoding.joint_inputs(low_precision, 80, bit_limit=64, workspace=memoryview(tiny)), ArithmeticUnresolved)
    assert not any(tiny)
    narrow = replace(state, model=replace(model, contract=replace(BUDGET, counter_bits=2)))
    rejects(lambda: encoding.exponents(narrow, 2, bit_limit=BITS), ArithmeticUnresolved)
    rejects(lambda: encoding.power_schedule(state, 1, bit_limit=BITS))
    rejects(lambda: replace(model, factor_bases=(2, 4, 5)))
    rejects(lambda: derive(fixture, encoding.LikelihoodEncodingContract()), ArithmeticUnresolved)
    descriptor = replace(model, prior_exponents=tuple(1 if i == 3 else v for i, v in enumerate(model.prior_exponents)))
    altered = replace(state, model=descriptor)
    assert state.raw()[1] != altered.raw()[1]
    _, bank, rules, graph, spec, domain, _, _ = fixture
    rejects(lambda: verify_model(descriptor, graph, rules, (F(1),)+bank.prior, spec, domain), AssertionError)
    cuda = cuda_contract(likelihood_encoding=BUDGET)
    legacy = cuda_contract(likelihood_encoding=encoding.LikelihoodEncodingContract())
    assert cuda.backend_id != legacy.backend_id and cuda.work_model != legacy.work_model
    rejects(lambda: IndexedCudaPrefixContract(cuda.storage, cuda.state_atol, cuda.probability_atol,
                                               n=2, likelihood_encoding=BUDGET))
    object.__setattr__(cuda, 'backend_id', legacy.backend_id)
    rejects(cuda.__post_init__)
    return {'wrong_scratch': 4, 'invalid_allowances': 3, 'derivation_refusals': 3,
            'unchanged_buffer_decode_refusals': 2, 'counter_refusal': 1,
            'single_radix_schedule_refusal': 1, 'noncoprime_descriptor_refusal': 1,
            'legacy_incompatible_bank_refusal': 1, 'descriptor_mutation': 1, 'identity_refusals': 2}


def legacy_identity():
    """Compare serialized descriptors with the actual pre-change source."""
    from audit_simplex_learner import fixture
    source = '1dfe683'
    code = subprocess.run(('git', 'show', source+':src/reference_compiler/fp_reference/likelihood_encoding.py'),
                          cwd=ROOT, capture_output=True, text=True, encoding='utf-8', check=True).stdout
    name = 'fp_reference._legacy_likelihood_identity_audit'
    old = ModuleType(name)
    sys.modules[name] = old
    try:
        exec(compile(code, '<committed legacy likelihood module>', 'exec'), old.__dict__)
        # Preserve the committed types' original serialization names. These
        # are separate audit-only classes, not changes to the current module.
        for key in ('LikelihoodEncodingContract', 'LikelihoodModel', 'EncodedLikelihoodState'):
            getattr(old, key).__module__ = encoding.__name__
        checks = 0
        for n in (2, 3):
            cfg, graph, online, _ = fixture(n)
            models = []
            for implementation in (old, encoding):
                model = implementation.prepare_model(graph, cfg.semantics, cfg.initializer_pattern,
                    online.learner, cfg.source_domain, implementation.LikelihoodEncodingContract(),
                    bit_limit=BITS, work_limit=implementation.preparation_work(graph, cfg.semantics,
                        online.learner, cfg.source_domain, BITS))
                models.append(model)
            assert pack(models[0]) == pack(models[1])
            states = [implementation.EncodedLikelihoodState(model, (0,)*model.rank, None)
                      for implementation, model in zip((old, encoding), models)]
            for query, target in ((0, 0), (1, 0), (1, 1)):
                assert states[0].raw() == states[1].raw()
                states = [state.observe(query, target) for state in states]
                assert states[0].raw() == states[1].raw()
                states = [state.commit() for state in states]
                assert states[0].raw() == states[1].raw()
                checks += 1
        return {'source': source, 'identical_serialized_models': 2, 'identical_metadata_transition_triples': checks}
    finally:
        del sys.modules[name]


def noncontiguous():
    bank = finite.bernoulli(((F(1, 3), F(2, 3)), (F(3, 4), F(1, 4))))
    rules, original, old_spec, scale = finite.native_graph(bank)
    mapping = {0: 2, 1: 0, 2: 4}
    graph = Program(tuple(Sum(node.type_id, tuple(Term(t.parent, mapping[t.slot]) for t in node.terms))
                          if type(node) is Sum else node for node in original.nodes), 6, original.heads)
    spec = replace(old_spec, simplex_slots=(0, 4))
    theta = (bank.prior[0], F(17, 7), F(1), F(0), bank.prior[1], F(5, 11))
    domain = ((F(1), F(0)), (F(0), F(1)))
    model = encoding.prepare_model(graph, rules, theta, spec, domain, BUDGET, bit_limit=BITS,
        work_limit=encoding.preparation_work(graph, rules, spec, domain, BITS, BUDGET))
    verify_model(model, graph, rules, theta, spec, domain)
    encoded = encoding.EncodedLikelihoodState(model, (0,)*model.rank, None)
    actual = native.initial_state(graph, rules, theta, 11, spec=spec, bit_limit=BITS)
    joint = bank.prior
    word = ((0, 0), (1, 0), (1, 1), (0, 1), (1, 0), (0, 0))
    with memoryview(bytearray(encoding.decode_workspace(model, BITS))) as scratch:
        for t, event in enumerate(word, 1):
            x, y = event
            cache = evaluate(graph, rules, actual.theta, dict(zip(model.source_ids, domain[x])), (), bit_limit=BITS)
            assert cache == finite.cache_oracle(bank, tuple(actual.theta[s] for s in spec.simplex_slots), x, scale)
            observed = native.observe_event(graph, actual, spec, cache, y, bit_limit=BITS)
            expected = [F(0)]*6
            expected[2] = 1/cache.masses[y]-F(2, scale)
            for slot, probability in zip(spec.simplex_slots, bank.table[x][y]):
                expected[slot] = F(scale-2, scale)-(scale*probability-1)/cache.masses[y]
            assert observed.gradient_sum == tuple(expected)
            actual = native.commit_event(observed, spec, bit_limit=BITS)
            encoded = encoded.observe(x, y).commit()
            joint = tuple(v*p for v, p in zip(joint, bank.table[x][y]))
            values = encoding.joint_inputs(encoded, actual.optimizer_steps, bit_limit=BITS, workspace=scratch)
            assert finite.normalize(values) == finite.normalize(joint) == tuple(actual.theta[s] for s in spec.simplex_slots)
            assert all(actual.theta[s] == theta[s] for s in (1, 2, 3, 5))
            assert actual.gradient_sum == (F(0),)*6 and actual.cursor == 11+t and actual.optimizer_steps == t
    return {'native_triples': len(word), 'selected_slots': [0, 4], 'complete_slots': 6,
            'initial_cursor': 11, 'final_cursor': actual.cursor, 'final_steps': actual.optimizer_steps}


def funding_probe():
    """Real ledger/control code, with a backend that always refuses admission."""
    fixture = tuple(fixtures())[-2]
    _, bank, rules, graph, spec, domain, _, _ = fixture
    bits = 1075
    model = derive(fixture, bits=bits)
    state = encoding.EncodedLikelihoodState(model, (0,)*model.rank, None).observe(0, 0)
    cfg = replace(contract(source_domain=False, pattern=(F(1),)+bank.prior), semantics=rules,
        source_domain=domain, normalizer_cap=F(22), activation_cap=F(18), reference_integer_bits=bits,
        limits=limits(byte_cap=128 << 20, work_cap=10**10))
    data = DataContract((StreamSpec('online', 'online', ('probe-event',)),), 'online',
        (F(1),)*len(rules.sources), tuple(SourceRead(s.source_id, 'input', i, 0) for i, s in enumerate(rules.sources)))
    online = OnlineContract(data, spec)
    cuda = cuda_contract(phase_evidence_bytes=65536, likelihood_encoding=BUDGET)
    workspace_bytes = encoding.decode_workspace(model, bits)
    rows = []
    for case in ('retained-refusal', 'work-short', 'scratch-short'):
        resource_limits = cfg.limits
        if case == 'work-short':
            resource_limits = limits(byte_cap=128 << 20, work_cap=encoding.decode_work(model, bits)-1)
        elif case == 'scratch-short':
            resource_limits = limits(byte_cap=cuda.phase_evidence_bytes+workspace_bytes-1, work_cap=10**10)
        rt = ReferenceCompilerRuntime(replace(cfg, limits=resource_limits), graph, online=online)
        candidate = rt._deployed_id
        record = rt._candidates[candidate].learner
        readout_id = rt._runtime_id+':cuda-raw-readout'
        # This CPU probe never reads a GPU word; the existing owner argument is
        # supplied as a paid empty extent so execution stops inside the probe.
        rt._ledger.allocate(rt._data_owner, (ObjectSpec(readout_id, 'CPU_probe_readout',
            {'reference_payload_bytes': 0, 'physical_objects': 1}, rt._chi),))
        rt._buffers[readout_id] = bytearray()
        entered, held = [], []
        def refuse(*args, **kwargs):
            view = kwargs['likelihood_workspace']
            encoding.require_workspace(view, workspace_bytes)
            paid = [e for e in rt._ledger._events if e.action == 'work' and ':cuda:' in e.note]
            assert paid and dict(paid[-1].debit)['work'] >= encoding.decode_work(model, bits)
            assert args[0]+':likelihood-scratch' in rt._ledger._objects
            entered.append(True)
            held.append(view)
            raise ArithmeticUnresolved('CPU probe refuses before any device arithmetic')
        probe = SimpleNamespace(contract=cuda, phases={}, staged={candidate: 'physical'}, current={candidate: 'physical'},
            _values={'physical': SimpleNamespace(encoding=state)}, relation_work=lambda *args: 0, execute=refuse)
        rt._cuda = probe
        error = None
        try:
            rt._cuda_execute('commit', graph, candidate, record, origin='ordinary', observation_id='probe-event',
                             sources=None, reference_prediction=None, target=None)
        except (ArithmeticUnresolved, ResourceExceeded) as exc:
            error = str(exc)
        assert error is not None
        rt._cuda = None  # Restore the probe fixture's original CPU endpoint.
        snapshot = validate_residency(rt)
        scratch_ids = [key for key, _ in snapshot.buffers if key.endswith(':likelihood-scratch')]
        assert bool(entered) == (case == 'retained-refusal')
        assert bool(scratch_ids) == bool(entered)
        if held:
            assert held[0].obj is rt._buffers[scratch_ids[0]]
            held[0][0] = 123
            assert rt._buffers[scratch_ids[0]][0] == 123
        assert not snapshot.install_receipts and not snapshot.observations and not snapshot.reference_proofs
        rows.append({'case': case, 'backend_entries': len(entered), 'retained_scratch_bytes': workspace_bytes if held else 0,
                     'reason': error})
    return rows


def run():
    report = {'status': 'PASS_RATIONAL_DESCRIPTOR_DECODE_AND_FUNDING_CPU', 'native_banks': exact_audit(),
              'adversarial': adversarial(), 'funding': funding_probe(), 'legacy_identity': legacy_identity(),
              'noncontiguous_late_birth': noncontiguous(),
              'scope': 'CPU only; funding backend always refuses; no successful GPU phase, persistence or installation claim'}
    assert 'torch' not in sys.modules
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = run()
    if args.write:
        OUTPUT.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
