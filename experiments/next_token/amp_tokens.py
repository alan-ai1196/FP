"""Compatibility import for the canonical passive token implementation."""
import sys
from fp_reference import token_amp as _implementation
sys.modules[__name__]=_implementation
