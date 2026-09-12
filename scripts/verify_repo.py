from __future__ import annotations
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
required = [
    'README.md','FP_THEORY.md','HANDOFF.md','RESEARCH_HISTORY.md',
    'CLAIMS_AND_STATUS.md','OPEN_PROBLEMS.md','IMPLEMENTATION_STATUS.md',
    'EXPERIMENT_RESOURCE_CONTRACT.md','.gitignore'
]
for p in required:
    if not (ROOT / p).is_file():
        raise SystemExit(f'missing required file: {p}')

forbidden_dirs = {
    '.venv','venv','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache',
    'checkpoints','models','datasets','cache'
}
for p in ROOT.rglob('*'):
    if '.git' in p.relative_to(ROOT).parts:
        continue
    if any(part in forbidden_dirs for part in p.parts):
        raise SystemExit(f'forbidden cache/artifact path: {p.relative_to(ROOT)}')
    if p.is_file() and p.suffix.lower() in {'.pt','.pth','.ckpt','.safetensors','.gguf','.zip','.7z'}:
        raise SystemExit(f'forbidden bulk artifact: {p.relative_to(ROOT)}')
    if p.is_file() and p.stat().st_size > 5_000_000:
        raise SystemExit(f'unexpected large file: {p.relative_to(ROOT)} {p.stat().st_size}')

patterns = {
    'openai_key': re.compile(r'\bsk-[A-Za-z0-9_-]{20,}\b'),
    'github_token': re.compile(r'\b(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}\b'),
    'hf_token': re.compile(r'\bhf_[A-Za-z0-9]{20,}\b'),
    'aws_key': re.compile(r'\bAKIA[0-9A-Z]{16}\b'),
    'private_key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
}
for p in ROOT.rglob('*'):
    if '.git' in p.relative_to(ROOT).parts:
        continue
    if not p.is_file():
        continue
    try:
        text = p.read_text(encoding='utf-8', errors='strict')
    except (UnicodeDecodeError, OSError):
        continue
    for name, pat in patterns.items():
        if pat.search(text):
            raise SystemExit(f'possible secret {name}: {p.relative_to(ROOT)}')

text = (ROOT / 'FP_THEORY.md').read_text(encoding='utf-8')
for needle in ['Canonical status','complete claim state','UNRESOLVED','Reference and AMP','Atomic self-Compiler boundary']:
    if needle not in text:
        raise SystemExit(f'FP_THEORY missing expected canonical content: {needle}')
print('repository structural/secret audit: PASS')
