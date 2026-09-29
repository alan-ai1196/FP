"""Public-value ownership attacks on actual historical and current Runtime.

No corpus, Torch, CUDA, parameter setter, private-state mutation or alternate
certificate issuer is used by the attacks. Frozen wrapper dictionaries are
ordinary returned/supplied metadata, as in the existing image-binding audit.
"""
from dataclasses import fields, replace, is_dataclass
from fractions import Fraction as F
from pathlib import Path
from types import ModuleType, MappingProxyType
from unittest.mock import patch
import argparse
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src/reference_compiler')]
from fp_reference import runtime, host_failure
from fp_reference.core import ContractError
from fp_reference.ingress import encode_context
from fp_reference.encoding import pack
from audit_token_reporting import report_registration
from audit_reference_search import runtime_fixture, finish

PREVIOUS = 'e13348e18181b8e64112b749ac766023c421542b'


def historical(name, label):
    path = 'src/reference_compiler/fp_reference/'+name+'.py'
    source = subprocess.check_output(['git', 'show', PREVIOUS+':'+path], cwd=ROOT, encoding='utf-8')
    module = ModuleType('fp_reference._public_value_historical_'+label)
    module.__package__ = 'fp_reference'
    sys.modules[module.__name__] = module
    exec(compile(source, 'git:'+PREVIOUS+':'+path, 'exec'), module.__dict__)
    return module


def old_runtime():
    old_guard = historical('host_failure', 'guard').guard_host_allocations
    with patch.object(host_failure, 'guard_host_allocations', old_guard):
        return historical('runtime', 'runtime')


def factory(module, cc, program, **kwargs):
    def convert(value, kind):
        return kind(**{f.name: getattr(value, f.name) for f in fields(value) if f.init})
    cc = convert(cc, module.ConstructionContract)
    if kwargs.get('online') is not None:
        kwargs['online'] = convert(kwargs['online'], module.OnlineContract)
    return module.ReferenceCompilerRuntime(cc, program, **kwargs)


def setup(module):
    cc, program, online, reporting = report_registration(count=4)
    return factory(module, cc, program, online=online, reporting=reporting)


def attacks(module, *, legacy):
    rt = setup(module)
    assert rt.predict_next('train/0', encode_context(())).status == 'PREDICTED_REFERENCE'
    assert rt.observe(0).status == 'OBSERVED_REFERENCE'
    snapshot = rt.snapshot()
    snapshot.observations[0].__dict__['target'] = 1
    forecast = rt.predict_next('train/1', encode_context(()))
    following = rt.snapshot()
    assert forecast.status == 'PREDICTED_REFERENCE' and following.halted is None
    assert following.pending.record.sources.past[0] == int(legacy)
    assert following.candidates[0].learner.targets == (0,)
    assert pack('1:0') in dict(following.buffers).values()
    causal = dict(prediction_status=forecast.status, actual_original_target=0,
        next_context_target=following.pending.record.sources.past[0],
        original_target_wire_and_learner_target_still_zero=True)

    rt = setup(module)
    probabilities = rt.predict_next('train/0', encode_context(())).predictions[0][1]
    original = probabilities.origin.output
    before = tuple(probabilities[i] for i in range(len(probabilities)))
    # A row permutation preserves every column total and maximum: ordinary
    # cache recomputation can accept the modified predecessor without a halt.
    probabilities.origin.__dict__['output'] = probabilities.origin.W[::-1].tobytes()
    after = tuple(probabilities[i] for i in range(len(probabilities)))
    assert before != after
    observed = rt.observe(0)
    following = rt.snapshot()
    changed = following.candidates[0].learner.origin.output != original
    assert observed.status == 'OBSERVED_REFERENCE' and following.halted is None
    assert changed == legacy
    forecast = dict(observation_status=observed.status, cursor=following.cursor,
        original_forecast=list(map(str, before)), altered_public_forecast=list(map(str, after)),
        live_readout_changed_without_update=changed)

    import audit_reference_search as search
    with patch.object(search, 'ReferenceCompilerRuntime', lambda cc, p, **kw: factory(module, cc, p, **kw)):
        rt, _ = runtime_fixture()
    selected = finish(rt, rt.start_reference_search('native'))
    proof = rt.reference_class_proof(selected.proof_id, decision_class_id=selected.decision_class_id)
    assert proof.best_likelihood == F(1, 4)
    proof.__dict__['best_likelihood'] = F(1)
    try:
        accepted = rt.verify_reference_class_proof(proof, decision_class_id=selected.decision_class_id)
    except ContractError:
        assert not legacy
        accepted = None
    else:
        assert legacy and accepted.best_likelihood == 1
    retained = rt.reference_class_proof(selected.proof_id, decision_class_id=selected.decision_class_id)
    assert retained.best_likelihood == (F(1) if legacy else F(1, 4))
    issuance = dict(decision_status=selected.status, actual_selected_likelihood='1/4',
        substituted_likelihood='1', altered_proof_accepted=accepted is not None,
        retained_issuance_likelihood=str(retained.best_likelihood))
    return dict(causal_history=causal, returned_forecast=forecast, reference_issuance=issuance)


def wrappers(value):
    """All mutable containers/metadata reachable under the closed value model."""
    found, visited = set(), set()
    def visit(item):
        if id(item) in visited:
            return
        visited.add(id(item))
        if is_dataclass(item) and not isinstance(item, type):
            found.add(id(item))
            for child in vars(item).values() if hasattr(item, '__dict__') else (getattr(item, f.name) for f in fields(item)):
                visit(child)
        elif type(item) in (dict, MappingProxyType):
            found.add(id(item))
            for key, child in item.items():
                visit(key); visit(child)
        elif type(item) in (tuple, list):
            if type(item) is list:
                found.add(id(item))
            for child in item:
                visit(child)
    visit(value)
    return found


def isolation():
    from fp_reference.public_values import detached
    cc, program, online, reporting = report_registration(count=4)
    rt = runtime.ReferenceCompilerRuntime(cc, program, online=online, reporting=reporting)
    supplied = (cc, program, online, reporting)
    owned = (rt._contract, tuple(rt._programs.values()), rt._online, rt._token_report_contract)
    assert not wrappers(supplied) & wrappers(owned)
    encoded = pack(rt.snapshot())
    cc.__dict__['normalizer_cap'] = F(1)
    program.__dict__['definition'] = None
    online.data.streams[0].__dict__['observation_ids'] = ('foreign',)
    reporting.__dict__['stream_id'] = 'foreign'
    assert pack(rt.snapshot()) == encoded
    for getter in ('contract', 'online_contract'):
        value = getattr(rt, getter)
        value.__dict__.clear()
        assert pack(rt.snapshot()) == encoded
    assert rt.predict_next('train/0', encode_context(())).status == 'PREDICTED_REFERENCE'
    assert rt.observe(0).status == 'OBSERVED_REFERENCE'
    public = rt.snapshot()
    # A second export has no shared wrappers, while exact immutable byte /
    # source tuples may remain shared. Internal alias topology is preserved.
    assert not wrappers(public) & wrappers(rt.snapshot())
    assert public.event_traces[0].after_observe is public.candidates[0].learner
    public.candidates[0].learner.origin.__dict__.clear()
    assert rt.predict_next('train/1', encode_context(())).status == 'PREDICTED_REFERENCE'
    assert rt.observe(1).status == 'OBSERVED_REFERENCE'
    immutable = (b'complete bytes', (F(1, 3), 2, 'source'))
    assert detached(immutable) is immutable
    return dict(all_constructor_wrappers_detached=True, contract_getters_detached=True,
        old_snapshot_mutation_cannot_change_continuation=True, internal_aliases_preserved=True,
        immutable_source_and_byte_identity_preserved=True)


def failures():
    checked = 0
    for port in ('snapshot', 'contract', 'predict_next', 'observe'):
        rt = setup(runtime)
        if port == 'observe':
            rt.predict_next('train/0', encode_context(()))
        with patch.object(host_failure, 'detached', side_effect=MemoryError('public value copy')):
            try:
                if port == 'contract':
                    _ = rt.contract
                elif port == 'predict_next':
                    rt.predict_next('train/0', encode_context(()))
                elif port == 'observe':
                    rt.observe(0)
                else:
                    rt.snapshot()
            except MemoryError:
                pass
            else:
                raise AssertionError('public copy failure was hidden')
        snapshot = rt.snapshot()
        assert snapshot.halted is host_failure.HOST_ALLOCATION_FAILURE
        if port == 'observe':
            assert snapshot.cursor == 1 and snapshot.observations[0].target == 0
        try:
            rt.predict_next('train/1', encode_context(()))
        except ContractError:
            pass
        else:
            raise AssertionError('failed export regained authority')
        checked += 1
    return dict(terminal_copy_failure_ports=checked, already_revealed_target_and_published_prefix_retained=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--historical-only', action='store_true')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = dict(status='REPRODUCED_PUBLIC_VALUE_AUTHORITY_ALIASES', previous_source=PREVIOUS,
        historical=attacks(old_runtime(), legacy=True), actual_corpus_opened=False, cuda_execution=False)
    artifact = 'FP_PUBLIC_VALUE_BOUNDARY_COUNTEREXAMPLES.json'
    if not args.historical_only:
        result.update(status='PASS_PUBLIC_VALUE_BOUNDARY_CPU', current=attacks(runtime, legacy=False),
            isolation=isolation(), failures=failures())
        artifact = 'FP_PUBLIC_VALUE_BOUNDARY_CPU.json'
    if args.write:
        (ROOT/'evidence/minimal'/artifact).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
