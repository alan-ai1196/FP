"""Compatibility import for the canonical numerical predicate."""
import sys
from fp_reference import token_readout_relation as _implementation
sys.modules[__name__] = _implementation
