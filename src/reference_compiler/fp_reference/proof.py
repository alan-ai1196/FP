"""Typed, state-bound Runtime proof authority is not implemented yet.

There is deliberately no callable signing authority in this module. The unsafe
recovered verifier, which did not bind its requested proposition kind, remains
in Git commit 39235ef and scripts/audit_recovered_authorities.py replays it.

Arithmetic helpers return calculations only. No such result is currently a
complete Compiler, equivalence, persistence, bridge or install authorization.
"""
