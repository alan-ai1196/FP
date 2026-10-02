"""Historical guarded ports for exact owned-prefix/admission controls only."""
from contextlib import ExitStack, contextmanager
from pathlib import Path
from types import FunctionType
from unittest.mock import patch
import ast
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASELINE = '571af68'


def historical_method(module, cls, name, *, source=BASELINE, public_guard=False):
    from fp_reference.host_failure import _guard
    relative = Path(module.__file__).relative_to(ROOT).as_posix()
    text = subprocess.check_output(['git', 'show', source+':'+relative], cwd=ROOT, text=True)
    declaration = next(n for n in ast.parse(text).body if isinstance(n, ast.ClassDef) and n.name == cls.__name__)
    node = next(n for n in declaration.body if isinstance(n, ast.FunctionDef) and n.name == name)
    namespace = dict(vars(module))
    exec(compile(ast.Module(body=[node], type_ignores=[]), '<'+source+' '+cls.__name__+'.'+name+'>', 'exec'), namespace)
    parsed = namespace[name]
    # Share the real module globals, as the original method did. Passive
    # observers/fault controls must see exactly the same dynamic bindings.
    function = FunctionType(parsed.__code__, vars(module), name, parsed.__defaults__, parsed.__closure__)
    function.__kwdefaults__, function.__annotations__ = parsed.__kwdefaults__, parsed.__annotations__
    return _guard(function, diagnostic=False) if public_guard else function


@contextmanager
def historical_prediction_ports(source=BASELINE):
    from fp_reference import runtime
    cls = runtime.ReferenceCompilerRuntime
    with ExitStack() as stack:
        for name in ('begin_context', '_predict_received'):
            function = historical_method(runtime, cls, name, source=source, public_guard=not name.startswith('_'))
            stack.enter_context(patch.object(cls, name, function))
        yield
