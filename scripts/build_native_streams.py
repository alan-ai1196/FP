"""Compile the canonical stream algorithms without a second authored codec.

Build-only dependency: Cython 3.1.8. Outputs live in ignored build/native_streams.
The generated consumer source contains exact AST-selected functions from the
canonical owner. No production module or Runtime registration is changed here.
"""
from pathlib import Path
import ast
import hashlib
import json
import sys
import sysconfig

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT/'src/reference_compiler/fp_reference'
BUILD = ROOT/'build/native_streams'
DIRECTIVES = dict(language_level=3, infer_types=False, annotation_typing=False,
    overflowcheck=True, boundscheck=True, wraparound=True, initializedcheck=True,
    nonecheck=True, binding=True)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    sys.path.insert(0, str(ROOT/'build/native_tools'))
    import Cython
    from Cython.Build import cythonize
    from setuptools import Extension, Distribution
    if Cython.__version__ != '3.1.8':
        raise RuntimeError('use the declared Cython 3.1.8 build dependency')
    BUILD.mkdir(parents=True, exist_ok=True)
    source = (PACKAGE/'shared_reference.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    names = ('_packed_parts', '_compare_stream')
    functions = {node.name: ast.get_source_segment(source, node) for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name in names}
    assert set(functions) == set(names)
    consumer = BUILD/'_compiled_stream_consumers.py'
    consumer.write_text('from .core import ContractError\nfrom . import byte_archive as archive\n'
        'from ._compiled_stream_encoding import fragments\n\n'+
        '\n\n'.join(functions[name] for name in names)+'\n', encoding='utf-8')
    extensions = [Extension('fp_reference._compiled_stream_encoding', [str(PACKAGE/'encoding.py')]),
                  Extension('fp_reference._compiled_stream_consumers', [str(consumer)])]
    modules = cythonize(extensions, build_dir=str(BUILD/'generated'), compiler_directives=DIRECTIVES,
        force=True, quiet=True)
    distribution = Distribution(dict(name='fp-native-stream-controls', ext_modules=modules))
    command = distribution.get_command_obj('build_ext')
    command.build_lib, command.build_temp = str(BUILD), str(BUILD/'temp')
    command.ensure_finalized()
    command.run()
    paths = {ext.name: Path(command.get_ext_fullpath(ext.name)) for ext in modules}
    if any(not p.is_file() or BUILD.resolve() not in p.resolve().parents for p in paths.values()):
        raise RuntimeError('compiled artifact escaped its declared build directory')
    inputs = (PACKAGE/'encoding.py', PACKAGE/'shared_reference.py', Path(__file__))
    receipt = dict(status='BUILT_NATIVE_STREAM_COMPONENTS', cython=Cython.__version__,
        python=sys.version, abi=sysconfig.get_config_var('EXT_SUFFIX'),
        directives=DIRECTIVES, compiler_executable=getattr(command.compiler, 'cc', None),
        sources={p.relative_to(ROOT).as_posix(): digest(p) for p in inputs},
        modules={name: dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size,
                           sha256=digest(p)) for name, p in paths.items()},
        generated_consumers_are_exact_canonical_function_sources=True)
    (BUILD/'manifest.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
