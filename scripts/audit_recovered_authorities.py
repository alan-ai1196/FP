"""Replay the actual preserved bridge/proof bytes against strict value objects.

The source is read from its canonical Git recovery commit, never reconstructed
as a deliberately weakened imitation. Run with `python -B` from any directory.
"""
from dataclasses import replace
from pathlib import Path
import json
import subprocess
import sys
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/reference_compiler'))
from fp_reference import core
from fp_reference.core import CertificateKind, CertificateProvenance, ClaimContract

RECOVERY = '39235ef8678cabc6fa675eb9e0568895d72d9b61'
PACKAGE = 'fp_reference._historical_authority_audit'
package = types.ModuleType(PACKAGE)
package.__path__ = []
sys.modules[PACKAGE] = package
sys.modules[f'{PACKAGE}.core'] = core


def historical(name):
    path = f'src/reference_compiler/fp_reference/{name}.py'
    source = subprocess.check_output(['git', 'show', f'{RECOVERY}:{path}'], cwd=ROOT, text=True)
    module = types.ModuleType(f'{PACKAGE}.{name}')
    module.__package__ = PACKAGE
    sys.modules[module.__name__] = module
    exec(compile(source, f'{RECOVERY}:{path}', 'exec'), module.__dict__)
    return module


def run():
    CompleteLearnerState = historical('learner').CompleteLearnerState
    proof, bridge = historical('proof'), historical('bridge')
    contract = ClaimContract({'audit': 'recovered authority counterexamples'}, ('upper-only',), ('equal',))
    provenance = CertificateProvenance(contract.chi, 'deployed', 'snapshot', 'finite-class')
    # A legitimate verifier for the proposition "objective <= 1" cannot inspect
    # the requested certificate kind in the recovered signature.
    authority = proof.ProofAuthority(contract, {'upper-only': lambda c, p, payload, e: payload == {'upper': 1} and e == (0, 1)})
    token = authority.issue(verifier_id='upper-only', kind=CertificateKind.EQUIVALENCE,
                            provenance=provenance, payload={'upper': 1}, evidence=(0, 1))
    accepted = authority.verify(token, chi=contract.chi, base_lineage_id='deployed',
                                snapshot_id='snapshot', expected_kind=CertificateKind.EQUIVALENCE)
    equal = lambda r, a: r.theta == a.theta
    authority = bridge.BridgeAuthority(contract, {'equal': equal})
    ref = CompleteLearnerState('ref', 0, 'physical', theta={'w': 0.0})
    amp = CompleteLearnerState('amp', 0, 'physical', theta={'w': 0.0})
    key = authority.initialize(physical_lineage_id='physical', reference_state=ref, amp_state=amp, relation_id='equal')
    # The unobserved cursor-1 pair may disagree arbitrarily. Cursor 2 agrees.
    ref.cursor = amp.cursor = 2
    authority.verify_event(key, ref, amp)
    skipped = authority.authorize(key, ref, amp)
    # No transition ran: replace both complete endpoints at the same cursor.
    ref.theta['w'] = amp.theta['w'] = 7.0
    replaced = authority.authorize(key, ref, amp)
    authority.verify_authorization(replaced, physical_lineage_id='physical', reference_state=ref, amp_state=amp)
    authority.sessions[key.key].alive = False
    authority.verify_authorization(replaced, physical_lineage_id='physical', reference_state=ref, amp_state=amp)
    return {
        'source_commit': RECOVERY,
        'scope': 'actual recovered proof/bridge code, reconstructed strict core data objects',
        'upper_evidence_accepted_as_equivalence': accepted.kind is CertificateKind.EQUIVALENCE,
        'skipped_event_accepted': skipped.cursor == 2 and skipped.verified_event_count == 1,
        'same_cursor_unexecuted_state_replacement_accepted': skipped.reference_state_id != replaced.reference_state_id,
        'dead_session_authorization_accepted': True,
        'interpretation': 'implementation mismatches, not Foundation R4 counterexamples',
    }


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
