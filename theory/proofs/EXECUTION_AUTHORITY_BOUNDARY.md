# Proof propositions and execution prefixes at the authority boundary

Status: implementation counterexamples and scoped proof obligation, 2026-09-06.
`FP_THEORY.md` remains normative and unchanged. No new semantic action is needed.

## Actual recovered-source counterexamples

`python -B scripts/audit_recovered_authorities.py` executes the preserved
`proof.py` and `bridge.py` from commit `39235ef` with reconstructed strict core
value objects. It does not claim the missing historical runtime was executable.
Git preserves the source; `evidence/minimal/FP_RECOVERED_AUTHORITY_AUDIT.json`
preserves the minimal result.

1. The proof verifier takes `(contract, provenance, payload, evidence)` but never
   the requested **kind**. Valid evidence for an upper bound is accepted and
   signed as `EQUIVALENCE`. Checking the signed kind later cannot repair this:
   the signer itself issued the wrong proposition.
2. The bridge accepts a jump from cursor 0 to cursor 2 and records one verified
   event. Equality at both endpoints permits an arbitrary disagreement at the
   omitted cursor 1. No coarse-to-internal-event implication was proved.
3. At cursor 2, both parameter dictionaries can be changed from 0 to 7 and
   authorized afresh. The endpoint relation holds, but neither state was reached
   by the checked execution prefix.
4. An issued authorization still verifies after the session is marked dead.

These falsify the sufficiency of the helpers as authority boundaries, not R4.

## Minimal invariant

An authorization proves a **typed proposition about a specific executed prefix**.
Authentication of an endpoint proves neither the proposition's type nor the
endpoint's reachability.

For each owned pair, retain exact checked complete endpoints and the next
registered microtransition phase. A transition consumes those endpoints,
executes the registered operation, and checks the relation at its required phase.
Authorize only the recorded endpoints of a live session. A failed relation
invalidates the prefix; later endpoint agreement cannot revive it.

Induction on the execution prefix proves the scoped result: initialization gives
the base relation. Each accepted next transition has exactly the recorded input,
the registered phase, and a checked successor. Thus every required phase
of the executed prefix has the relation. Authorizing the recorded endpoint
preserves this conclusion. A skipped phase, caller replacement endpoint, or
revival removes an induction premise.

This is a finite executed-prefix statement. A global transition theorem, an
abstract-real-to-float64 enclosure, stochastic coupling, and the actual GPU AMP
bridge remain separate obligations. Equality of two CPU paths cannot discharge
them. Registered Python functions remain trusted implementations whose semantics
need audit; HMAC neither proves mathematical soundness nor isolates hostile code.

Proof verification likewise must bind the full proposition (kind, exact decision
class, subject, provenance, immutable payload), with an immutable preregistered
verifier-to-kind assignment.
