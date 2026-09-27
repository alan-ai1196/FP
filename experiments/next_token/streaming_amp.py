"""Compatibility import for the canonical passive token implementation."""
import sys
from fp_reference import token_streaming as _implementation
sys.modules[__name__]=_implementation
