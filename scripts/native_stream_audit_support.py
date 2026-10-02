"""Load source-bound compiled stream components for audits only.

Artifact digests bind native executable code and its canonical inputs. No
per-event hashing, corpus, Runtime root mutation or authority is supplied.
"""
from contextlib import contextmanager
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
import sysconfig

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src/reference_compiler'), str(ROOT/'scripts')]


def load():
    manifest = json.loads((ROOT/'build/native_streams/manifest.json').read_text(encoding='utf-8'))
    if manifest['abi'] != sysconfig.get_config_var('EXT_SUFFIX') or manifest['python'] != sys.version:
        raise RuntimeError('native stream artifact targets a different Python build')
    def check(path, expected):
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise RuntimeError('native stream input/artifact identity changed: '+str(path))
    for name, expected in manifest['sources'].items():
        check(ROOT/name, expected)
    modules = []
    for name in ('fp_reference._compiled_stream_encoding', 'fp_reference._compiled_stream_consumers'):
        entry = manifest['modules'][name]
        path = ROOT/entry['path']
        check(path, entry['sha256'])
        if name in sys.modules:
            module = sys.modules[name]
            if Path(module.__file__).resolve() != path.resolve():
                raise RuntimeError('different native stream module already loaded')
        else:
            import fp_reference
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
        modules.append(module)
    return *modules, manifest


@contextmanager
def compiled_controls(encoder, consumers):
    """Source-bound CPU component control, before constructing each audit root.

    Full Runtime/control evidence must be checked separately. This also serves
    the preregistered native cost control; it grants no production backend or
    CUDA authority. The context cannot be switched within an active trajectory.
    """
    from fp_reference import encoding, shared_reference
    replacements = {encoding.fragments: encoder.fragments,
        shared_reference._packed_parts: consumers._packed_parts,
        shared_reference._compare_stream: consumers._compare_stream}
    changed = []
    for name, module in tuple(sys.modules.items()):
        if name.startswith('fp_reference.') and '_compiled_stream_' not in name and module is not None:
            for attribute, value in tuple(vars(module).items()):
                try:
                    new = replacements.get(value)
                except TypeError:
                    continue
                if new is not None:
                    changed.append((module, attribute, value))
                    setattr(module, attribute, new)
    try:
        yield
    finally:
        for module, attribute, value in reversed(changed):
            setattr(module, attribute, value)
        # Imports during the control may have copied a compiled alias. Restore
        # those too so the following Python control cannot inherit this path.
        reverse = {value: key for key, value in replacements.items()}
        for name, module in tuple(sys.modules.items()):
            if name.startswith('fp_reference.') and '_compiled_stream_' not in name and module is not None:
                for attribute, value in tuple(vars(module).items()):
                    try:
                        old = reverse.get(value)
                    except TypeError:
                        continue
                    if old is not None:
                        setattr(module, attribute, old)
