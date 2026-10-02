"""Original complete observe body as a guarded, source-bound audit control.

Only the historical method is rebound. Both arms keep the actual current
Runtime, all ownership checks and the ordinary host/public-value guard.
"""
from pathlib import Path
import ast
import subprocess
import textwrap

ROOT = Path(__file__).resolve().parents[1]
BASELINE = '364934d'


def original_observe_source():
    source = subprocess.check_output(['git', 'show',
        BASELINE+':src/reference_compiler/fp_reference/runtime.py'], cwd=ROOT, text=True)
    cls = next(n for n in ast.parse(source).body
        if isinstance(n, ast.ClassDef) and n.name == 'ReferenceCompilerRuntime')
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'observe')
    extracted = textwrap.dedent(ast.get_source_segment(source, method))
    if ast.dump(ast.parse(extracted).body[0]) != ast.dump(method):
        raise RuntimeError('historical method extraction changed its AST')
    return extracted


def original_observe(source=None):
    from fp_reference import runtime
    from fp_reference.host_failure import _guard
    # Bounded workers receive the exact parent-extracted source so they never
    # need to spawn Git inside their one-process Windows job.
    tree = ast.parse(original_observe_source() if source is None else source)
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef) or tree.body[0].name != 'observe':
        raise RuntimeError('single original observe method source required')
    method = tree.body[0]
    namespace = dict(vars(runtime))
    exec(compile(ast.Module(body=[method], type_ignores=[]),
        '<canonical observe at '+BASELINE+'>', 'exec'), namespace)
    return _guard(namespace['observe'], diagnostic=False)
