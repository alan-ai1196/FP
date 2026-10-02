"""Historical whole-ledger and changed-port controls for owned transitions."""
from contextlib import contextmanager, ExitStack
from pathlib import Path
from unittest.mock import patch
import ast
import __future__
import subprocess
import sys

from owned_admission_audit_support import historical_method

ROOT = Path(__file__).resolve().parents[1]
BASELINE = 'a694441'


def ledger_class(source=BASELINE):
    from fp_reference import resources
    relative = Path(resources.__file__).relative_to(ROOT).as_posix()
    text = subprocess.check_output(['git', 'show', source+':'+relative], cwd=ROOT, text=True)
    node = next(n for n in ast.parse(text).body if isinstance(n, ast.ClassDef) and n.name == 'ResourceLedger')
    namespace = dict(vars(resources))
    exec(compile(ast.Module(body=[node], type_ignores=[]), '<'+source+' ResourceLedger>', 'exec',
                 flags=__future__.annotations.compiler_flag), namespace)
    return namespace['ResourceLedger']


@contextmanager
def historical_ledger(source=BASELINE):
    """Bind the complete original class, including independent mutable state.

    Passive audits import the ledger under several module aliases. Rebind all
    already loaded aliases, and restore aliases imported during the context as
    well. This is a serialized audit-only context, never a Runtime backend.
    """
    from fp_reference import resources, shared_reference
    original, historical = resources.ResourceLedger, ledger_class(source)
    def aliases(value):
        return [vars(module) for module in tuple(sys.modules.values())
                if module is not None and vars(module).get('ResourceLedger') is value]
    for namespace in aliases(original):
        namespace['ResourceLedger'] = historical
    try:
        # This was the sole trusted writer of object extent outside the old
        # ledger class. It belongs to the same historical state invariant.
        archive = shared_reference._SharedReference
        with patch.object(archive, '_relocate_frame',
                historical_method(shared_reference, archive, '_relocate_frame', source=source)):
            yield historical
    finally:
        for namespace in aliases(historical):
            namespace['ResourceLedger'] = original


@contextmanager
def original_transitions():
    from fp_reference import runtime
    cls = runtime.ReferenceCompilerRuntime
    with historical_ledger(), ExitStack() as stack:
        for name in ('__init__', '_release_owner', '_seal_cuda_frame', 'begin_context', 'observe', '_install_owned'):
            function = historical_method(runtime, cls, name, source=BASELINE,
                public_guard=not name.startswith('_'))
            stack.enter_context(patch.object(cls, name, function))
        yield
