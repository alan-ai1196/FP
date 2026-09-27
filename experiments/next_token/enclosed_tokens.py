"""Compatibility import for the canonical passive reference implementation."""
import sys
from fp_reference import token_enclosures as _implementation
sys.modules[__name__] = _implementation
