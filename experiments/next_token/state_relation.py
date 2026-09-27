"""Compatibility import for the canonical numerical predicate."""
import sys
from fp_reference import token_state_relation as _implementation
sys.modules[__name__] = _implementation
