"""Build the manuscript index and local release directories. Run from any directory."""

import argparse
import csv
import hashlib
import html
import io
import json
import os
import re
import subprocess
import tempfile
from collections import Counter
from datetime import datetime
from pathlib import Path, PurePosixPath
from urllib.parse import quote, unquote
from filelock import FileLock

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
CORPUS = ROOT / 'corpus'
OPENAI = CORPUS / 'openai_math_2026'
INITIAL = OPENAI / 'initial'
UPSTREAM = 'https://github.com/openai/math'
EDITIONS = (
    ('2026-10-06', 'adc7f1241b42e322a6451854ab7e4b4c146bf78a', 722, 372),
    ('2026-10-07', 'fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb', 719, 372),
    ('2026-10-26', '7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a', 721, 373),
    ('2026-10-29', '4eaee87548250b2682affda7d05d947c05554bae', 721, 373),
    ('2026-11-23', 'f5702854040e97fa7675c21ba37a9608f5f92dd3', 722, 374),
    ('2026-11-24', '3344da59991ed94f9ba711217b29c1d760badfa6', 730, 375),
)
FIELDS = ('id title authors publication_date source doi_or_arxiv original_url local_file_path '
          'version publication_review_status ai_involvement formal_verification_status reading_status '
          'reading_progress mathematical_topics extracted_instruments fp_relevance follow_up_status '
          'fulltext_url companion_urls').split()
READ_STAGE = {'unread': 0, 'screened': 1, 'scoped reading': 2, 'partially read': 2, 'fully read': 3}
WITHDRAWN = {
    'algebraicity of weil classes on split abelian eightfolds',
    'algebraicity of kuga–satake correspondences for k3 surfaces',
    'the rational hodge conjecture for products of k3 surfaces',
}
TOP = ['CONTENTS.md', 'README.md', 'overview.pdf', 'overview.tex', 'history.md', 'lean/formalization.yaml']
FAMILY = re.compile(r'^(?:<a\b[^>]*>\s*</a>\s*)?\*\*(\d{3})\. (.*?)\*\*')
PAPER = re.compile(r'&emsp;\[(.+)\]\((preprints/.+?\.pdf)\)')


def git(*args):
    return subprocess.check_output(['git', '-C', str(INITIAL), *args])


def table(path):
    if not path.exists():
        return {}
    with path.open(encoding='utf-8-sig', newline='') as handle:
        records = list(csv.DictReader(handle))
    result = {r['id']: r for r in records}
    if len(result) != len(records):
        raise ValueError(f'Duplicate IDs in {path}')
    return result


def save_table(path, fields, records):
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore', lineterminator='\n')
    writer.writeheader()
    writer.writerows(records)
    data = output.getvalue().encode('utf-8')
    if path.exists() and path.read_bytes() == data:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def plain(s):
    return html.unescape(re.sub(r'</?(?:i|b|sub|sup|em|strong)>', '', s)).strip()


def catalog(rev):
    families = {}
    items = {}
    family = None
    for line in git('show', f'{rev}:CONTENTS.md').decode().splitlines():
        if match := FAMILY.match(line):
            family = match[1]
            families[family] = plain(match[2]).rstrip('.')
        elif match := PAPER.match(line):
            name = unquote(match[2])
            if family is None or name in items:
                raise ValueError(f'Invalid catalog entry {line}')
            items[name] = (plain(match[1]), family, families[family])
    return families, items


def files(rev):
    entries = git('ls-tree', '-rz', rev, '--', 'preprints', *TOP)
    result = {}
    for entry in entries.split(b'\0'):
        if not entry:
            continue
        head, raw = entry.split(b'\t', 1)
        mode, kind, oid = head.decode().split()
        name = raw.decode()
        if kind != 'blob' or mode not in ('100644', '100755'):
            raise ValueError(f'Unexpected manuscript file {mode} {name}')
        result[name] = oid
    return result


def extract(directory, names, tree):
    directory.mkdir(parents=True, exist_ok=True)
    with subprocess.Popen(['git', '-C', str(INITIAL), 'cat-file', '--batch'],
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE) as blobs:
        for name in sorted(names):
            target = directory.joinpath(*PurePosixPath(name).parts)
            target.resolve().relative_to(directory.resolve())
            oid = tree[name]
            if target.exists():
                existing = target.read_bytes()
                blob = b'blob ' + str(len(existing)).encode() + b'\0' + existing
                if hashlib.sha1(blob).hexdigest() != oid:
                    raise ValueError(f'Existing edition differs from pinned Git object: {target}')
                continue
            blobs.stdin.write((oid + '\n').encode())
            blobs.stdin.flush()
            actual, kind, length = blobs.stdout.readline().split()
            if actual.decode() != oid or kind != b'blob':
                raise ValueError(f'Missing Git blob {oid}')
            data = blobs.stdout.read(int(length))
            if len(data) != int(length) or blobs.stdout.read(1) != b'\n':
                raise ValueError(f'Incomplete Git blob {oid}')
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as f:
                f.write(data)
        blobs.stdin.close()
        if blobs.wait() != 0:
            raise RuntimeError('Could not read pinned release objects')


def paper_directory(name):
    return '/'.join(name.split('/')[:2])


def metadata(folder):
    readme = (folder / 'README.md').read_text(encoding='utf-8')
    def value(label):
        match = re.search(rf'^(?:\*\*)?{label}:(?:\*\*)?\s*(.+)', readme, re.MULTILINE)
        return match[1].strip() if match else ''
    date = value('Date')
    if not date:
        match = re.search(r'\b(?:September|October|November) \d{1,2}, 2026\b', readme.split('## Citation')[0])
        date = match[0] if match else ''
    if date:
        try:
            date = datetime.strptime(date, '%B %d, %Y').date().isoformat()
        except ValueError:
            pass
    return value('Author') or value('Authors') or 'OpenAI', date


def build_openai():
    if not (INITIAL / '.git').is_dir():
        INITIAL.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['git', 'clone', '--no-checkout', UPSTREAM + '.git', str(INITIAL)], check=True)
        git('config', 'core.longpaths', 'true')
        git('config', 'core.autocrlf', 'false')
        git('checkout', '--detach', EDITIONS[0][1])
    if git('rev-parse', 'HEAD').decode().strip() != EDITIONS[0][1]:
        raise ValueError('Original checkout must be at the October 6 revision')
    if git('status', '--porcelain', '--untracked-files=no'):
        raise ValueError('The frozen original checkout has modified tracked files')
    rows, releases, active = {}, [], {}
    previous_tree, previous_items = {}, {}
    for date, rev, count, family_count in EDITIONS:
        families, items = catalog(rev)
        tree = files(rev)
        if (len(items), len(families)) != (count, family_count):
            raise ValueError(f'Unexpected catalog counts at {rev}')
        initial = not releases
        local = INITIAL if initial else OPENAI / 'releases' / date
        changed = {p for p in items if p not in previous_items or tree[p] != previous_tree[p]}
        gone = set(previous_items) - set(items)
        for name in gone | (changed & set(previous_items)):
            old = rows[active.pop(name)]
            withdrawn = old['title'].casefold().replace('-', '–') in WITHDRAWN
            old['publication_review_status'] = 'publisher withdrawal' if withdrawn else 'superseded preprint'
            old['follow_up_status'] = f'Consult {date} release history and replacement or withdrawal notice.'
        changed_dirs = set()
        if not initial:
            for name in tree.keys() | previous_tree.keys():
                if name.startswith('preprints/') and tree.get(name) != previous_tree.get(name):
                    changed_dirs.add(paper_directory(name))
            selected = {p for p in tree if p in TOP or paper_directory(p) in changed_dirs}
            extract(local, selected, tree)
        formal_yaml = (local / 'lean/formalization.yaml').read_text(encoding='utf-8')
        listed = set(re.findall(r'^\s+id:\s*\.\./(preprints/\S+\.pdf)\s*$', formal_yaml, re.MULTILINE))
        for ordinal, (name, (title, family, subject)) in enumerate(items.items(), 1):
            if name not in changed:
                continue
            pdf = local / name
            with pdf.open('rb') as f:
                if f.read(5) != b'%PDF-':
                    raise ValueError(f'Invalid PDF: {pdf}')
            if not any(pdf.parent.rglob('*.tex')):
                raise ValueError(f'No accompanying LaTeX found for {pdf}')
            authors, manuscript_date = metadata(pdf.parent)
            row_id = f'OAI-{date[5:].replace("-", "")}-{ordinal:03d}'
            rows[row_id] = dict(id=row_id, title=title, authors=authors, publication_date=manuscript_date,
                source=f'P0 OpenAI Math, family {family}', original_url=f'{UPSTREAM}/blob/{rev}/{quote(name)}',
                local_file_path=pdf.relative_to(PROJECT).as_posix(), version=date,
                publication_review_status='publisher preprint', ai_involvement='OpenAI model-generated research',
                formal_verification_status=('Primary PDF listed in release Lean manifest' if name in listed
                    else 'Primary PDF not directly matched in release Lean manifest') + '. Local replay pending.',
                reading_status='unread', mathematical_topics=subject, extracted_instruments='', fp_relevance='',
                follow_up_status='Read full original and inspect dependencies.' if initial else 'Read this edition and compare the release history.')
            active[name] = row_id
        releases.append(dict(date=date, commit=rev, manuscripts=count, families=family_count,
            new_pdf_editions=len(changed), removed_catalog_paths=len(gone),
            changed_manuscript_directories=len(changed_dirs) if not initial else count,
            local_catalog=(local/'CONTENTS.md').relative_to(PROJECT).as_posix()))
        previous_tree, previous_items = tree, items
    return rows, releases


def merge(rows, incoming):
    for ident, fresh in incoming.items():
        previous = rows.get(ident, {})
        delta = READ_STAGE[fresh['reading_status']] - READ_STAGE[previous.get('reading_status', 'unread')]
        if delta < 0:
            fresh['reading_status'] = previous['reading_status']
        if previous.get('authors') and not fresh.get('authors'):
            fresh['authors'] = previous['authors']
        if previous.get('local_file_path') and not fresh.get('local_file_path'):
            fresh['local_file_path'] = previous['local_file_path']
            if previous.get('version'):
                fresh['version'] = previous['version']
        for field in ('reading_progress', 'extracted_instruments', 'fp_relevance', 'fulltext_url', 'companion_urls',
                      'version', 'publication_review_status', 'ai_involvement', 'formal_verification_status'):
            if previous.get(field) and (delta < 0 or not fresh.get(field)):
                fresh[field] = previous[field]
        if previous.get('follow_up_status') and previous.get('publication_review_status') == fresh.get('publication_review_status'):
            fresh['follow_up_status'] = previous['follow_up_status']
        rows[ident] = {k: fresh.get(k, '') for k in FIELDS}


def import_intake(rows, path):
    entries = json.loads(path.read_text(encoding='utf-8-sig'))
    if isinstance(entries, dict):
        entries = entries['items']
    records = {}
    for entry in entries:
        record = {key:entry.get(key, '') for key in FIELDS}
        record['fulltext_url'] = record['fulltext_url'] or entry.get('pdf_url', '')
        companions = entry.get('companion_urls') or entry.get('additional_urls', [])
        if isinstance(companions, list):
            record['companion_urls'] = ' '.join(companions)
        if not record['id'] or not record['title'] or not record['original_url']:
            raise ValueError(f'Incomplete source record in {path}: {record}')
        if record['local_file_path']:
            local = PROJECT / record['local_file_path']
            if not local.exists():
                raise FileNotFoundError(local)
        record['reading_status'] = record['reading_status'] or 'unread'
        if record['id'] in records:
            raise ValueError(f'Duplicate source record in {path}: {record["id"]}')
        records[record['id']] = record
    merge(rows, records)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--intake', nargs='*', type=Path, default=[], help='Primary metadata JSON files')
    ap.add_argument('--intake-only', action='store_true', help='Keep the frozen OpenAI index as it is')
    args = ap.parse_args()
    index = ROOT / 'index.csv'
    openai = {}
    if not args.intake_only:
        openai, releases = build_openai()
        save_table(ROOT/'snapshots/openai_math.csv', list(releases[0]), releases)
    CORPUS.mkdir(parents=True, exist_ok=True)
    with FileLock(str(CORPUS/'.index.lock'), timeout=30):
        rows = table(index)
        merge(rows, openai)
        for path in args.intake:
            import_intake(rows, path)
        save_table(index, FIELDS, rows.values())
    print(f'{len(rows)} editions. Reading status {dict(Counter(r["reading_status"] for r in rows.values()))}')


if __name__ == '__main__':
    main()
