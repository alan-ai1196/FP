"""Actual reference/AMP bridge integration is not implemented yet.

There is deliberately no callable bridge authority in this module. The unsafe
recovered endpoint-signing helper is preserved in Git commit 39235ef and is
executed verbatim by scripts/audit_recovered_authorities.py. Its certificates
cannot substitute for an owned, event-level target-device execution prefix.

See FP_THEORY.md XV/XVIII and theory/proofs/EXECUTION_AUTHORITY_BOUNDARY.md.
Importability of this reserved module is not an implemented bridge gate.
"""
