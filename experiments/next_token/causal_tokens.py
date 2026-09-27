"""Compatibility import for the canonical passive reference implementation."""
import sys
from fp_reference import token_causal as _implementation
sys.modules[__name__] = _implementation
