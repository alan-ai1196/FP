"""Continuous token-ID text ingress for the external KenLM comparison.

The trial supplies an already declared train-only tape view. There are no
implicit document resets, special-token aliases, corpus reads or default
experimental budgets in this module.
"""
from operator import index
import numpy as np


def write_training_text(tape, output, *, vocabulary, chunk_tokens=65536):
    if type(vocabulary) is not int or not 1 <= vocabulary <= 65536:
        raise ValueError('uint16-compatible complete vocabulary required')
    if type(chunk_tokens) is not int or chunk_tokens < 1 or len(tape) == 0:
        raise ValueError('positive chunk and nonempty declared training view required')
    written = 0
    for start in range(0, len(tape), chunk_tokens):
        values = np.asarray(tape[start:start+chunk_tokens])
        if (values.ndim != 1 or values.dtype.kind not in 'iu'
                or np.any(values < 0) or np.any(values >= vocabulary)):
            raise ValueError('real corpus IDs must lie in the complete target alphabet')
        # Spaces between chunks are not sentence boundaries. Exactly one final
        # newline lets the upstream estimator add one BOS/EOS pair per view.
        if written:
            output.write(b' ')
        output.write(' '.join('t'+str(index(value)) for value in values).encode('ascii'))
        written += len(values)
    output.write(b'\n')
    return written
