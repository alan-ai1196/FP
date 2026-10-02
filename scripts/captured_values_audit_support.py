"""Audit-only original literal prediction methods from canonical Git."""
from contextlib import contextmanager, ExitStack
from pathlib import Path
from unittest.mock import patch
import ast
import copy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'c67a0aad7468d5e59635e02fb1501fee93c2f68e'


@contextmanager
def literal_predictions(source_text=None):
    from fp_reference import token_execution as module
    path = 'src/reference_compiler/fp_reference/token_execution.py'
    # A one-process job cannot launch Git. Its launcher can supply the exact
    # historical file after binding that artifact's bytes to SOURCE. This is
    # an audit-only comparator, never a Runtime authority or production mode.
    text = (subprocess.check_output(['git', 'show', SOURCE+':'+path], cwd=ROOT, text=True)
            if source_text is None else source_text)
    assert type(text) is str
    original = ast.parse(text)
    current = ast.parse((ROOT/path).read_text(encoding='utf-8'))
    def unchanged(tree):
        tree = copy.deepcopy(tree)
        tree.body = [node for node in tree.body if not
            (isinstance(node, ast.ImportFrom) and node.module == 'token_values')]
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == 'TokenReferenceMachine':
                node.body = [child for child in node.body if not
                    (isinstance(child, ast.FunctionDef) and child.name in ('predict', 'activation_values'))]
            if isinstance(node, ast.ClassDef) and node.name == 'TokenEvaluation':
                for child in node.body:
                    if isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name) and child.target.id == 'values':
                        child.annotation = ast.Name(id='LogicalValueTuple', ctx=ast.Load())
        return ast.dump(tree, include_attributes=False)
    # The historical methods run against unchanged numerical/validation code,
    # not an unbound future version of _forward or another new implementation.
    assert unchanged(original) == unchanged(current), 'literal prediction dependency changed'
    cls = next(n for n in original.body if isinstance(n, ast.ClassDef)
               and n.name == 'TokenReferenceMachine')
    names = ('predict', 'activation_values')
    methods = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert len(methods) == len(names)
    code = ast.Module(body=[ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0),
                           *methods], type_ignores=[])
    namespace = {}
    exec(compile(ast.fix_missing_locations(code), SOURCE+':'+path, 'exec'), module.__dict__, namespace)
    with ExitStack() as stack:
        for name in names:
            stack.enter_context(patch.object(module.TokenReferenceMachine, name, namespace[name]))
        yield
