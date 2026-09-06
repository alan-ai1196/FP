from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping
import hashlib, hmac, secrets

from .core import Certificate, CertificateKind, CertificateProvenance, ClaimContract, ContractError, stable_hash


Verifier = Callable[[ClaimContract, CertificateProvenance, Mapping[str,Any], Any], bool]


@dataclass(frozen=True)
class VerifiedCertificate:
    """Authority-issued proof token for decision-critical certificate use.

    The underlying Certificate remains a public mathematical data object.  It is
    not privileged until a verifier registered *before* the decision has checked
    the evidence and this authority has signed the exact certificate/evidence.
    """
    certificate: Certificate
    verifier_id: str
    evidence_hash: str
    authority_id: str
    signature: str

    @property
    def certificate_id(self)->str:
        return self.certificate.certificate_id


class ProofAuthority:
    def __init__(self, contract:ClaimContract, verifiers:Mapping[str,Verifier]):
        if not verifiers: raise ContractError('proof authority needs at least one registered verifier')
        unknown=set(verifiers)-set(contract.proof_verifier_ids)
        if unknown: raise ContractError(f'proof verifier ids not declared by claim contract: {sorted(unknown)}')
        missing=set(contract.proof_verifier_ids)-set(verifiers)
        if missing: raise ContractError(f'claim-declared proof verifiers missing implementations: {sorted(missing)}')
        self.contract=contract; self.verifiers=dict(verifiers)
        self._secret=secrets.token_bytes(32)
        self.authority_id=hashlib.sha256(self._secret).hexdigest()[:24]

    def _sign(self, fields:tuple)->str:
        return hmac.new(self._secret,stable_hash(fields).encode('ascii'),hashlib.sha256).hexdigest()

    def issue(self, *, verifier_id:str, kind:CertificateKind, provenance:CertificateProvenance,
              payload:Mapping[str,Any], evidence:Any)->VerifiedCertificate:
        if verifier_id not in self.verifiers: raise ContractError(f'unregistered proof verifier {verifier_id!r}')
        if provenance.chi!=self.contract.chi: raise ContractError('proof evidence belongs to different claim contract')
        evidence_hash=stable_hash(evidence)
        try: ok=bool(self.verifiers[verifier_id](self.contract,provenance,payload,evidence))
        except Exception as exc: raise ContractError(f'proof verifier {verifier_id!r} failed: {exc}') from exc
        if not ok: raise ContractError(f'proof verifier {verifier_id!r} rejected evidence')
        cert=Certificate(kind,provenance,dict(payload))
        fields=(cert.certificate_id,cert.kind.value,cert.provenance.key,stable_hash(cert.payload),verifier_id,evidence_hash,self.authority_id)
        return VerifiedCertificate(cert,verifier_id,evidence_hash,self.authority_id,self._sign(fields))

    def verify(self, token:VerifiedCertificate, *, chi:str, base_lineage_id:str, snapshot_id:str,
               expected_kind:CertificateKind|None=None)->Certificate:
        if token.authority_id!=self.authority_id: raise ContractError('proof token issued by different authority')
        c=token.certificate
        if expected_kind is not None and c.kind is not expected_kind: raise ContractError(f'expected {expected_kind.value} proof, got {c.kind.value}')
        c.assert_current(chi=chi,base_lineage_id=base_lineage_id,snapshot_id=snapshot_id)
        fields=(c.certificate_id,c.kind.value,c.provenance.key,stable_hash(c.payload),token.verifier_id,token.evidence_hash,token.authority_id)
        if not hmac.compare_digest(token.signature,self._sign(fields)): raise ContractError('invalid proof-token signature')
        if token.verifier_id not in self.verifiers: raise ContractError('proof verifier no longer registered')
        return c
