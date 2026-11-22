"""Check primary sources, retain newly found documents, and update the reading queue."""

import argparse
import hashlib
import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup
from filelock import FileLock

import library
import venue_sweep

AGENT = {'User-Agent': 'FP-mathematics-library/1.0 (https://github.com/alan-ai1196/FP)'}
CATEGORIES = ('cs.LG', 'cs.AI', 'cs.CL', 'cs.CV', 'cs.NE', 'cs.IT', 'cs.DS', 'cs.CC', 'cs.LO',
              'stat.ML', 'stat.TH', 'math.PR', 'math.ST', 'math.OC', 'math.DS', 'math.CO',
              'math.MG', 'math.FA', 'math.NA')
PHRASES = ('predictive state', 'causal state', 'state identification', 'system identification',
           'observable operator', 'hidden Markov', 'weighted automata', 'finite automata',
           'sequence model', 'world model', 'state space model', 'recurrent',
           'representation learning', 'feature learning', 'representation theorem',
           'learning dynamics', 'implicit bias', 'symmetry breaking', 'compositional',
           'in-context learning', 'test-time learning', 'continual learning',
           'information bottleneck', 'minimum description length', 'predictive information',
           'rate distortion', 'sufficient statistic', 'neural compression',
           'working memory', 'associative memory', 'memory augmented', 'algorithm discovery',
           'algorithmic reasoning', 'neural algorithm', 'language model', 'tokenization',
           'byte level', 'byte-level', 'token free', 'token-free', 'latent prediction',
           'continuous representation', 'multimodal representation', 'patch representation',
           'reinforcement learning', 'partial observability', 'adaptive control', 'regret bound',
           'communication complexity', 'tensor rank', 'convex geometry', 'formal proof')
ARXIV_PAGE_SIZE = 200
ARXIV_REQUEST_INTERVAL = 3.1
ARXIV_ID = re.compile(r'^\d{4}\.\d{4,5}v\d+$')
GIT_REPOS = ('openai/math', 'leanprover-community/mathlib4', 'leanprover/lean4')
FEEDS = {
    'OpenAI research/news feed': 'https://openai.com/news/rss.xml',
    'Anthropic research index': 'https://www.anthropic.com/research',
    'Google DeepMind feed': 'https://deepmind.google/blog/rss.xml',
}


def get(url, **opts):
    result = requests.get(url, headers=AGENT, timeout=opts.pop('timeout', (6, 25)), **opts)
    result.raise_for_status()
    return result


def archive(url, path, kind):
    if path.exists():
        return
    data = get(url).content
    if kind == 'pdf':
        if b'%PDF-' not in data[:1024] or b'%%EOF' not in data[-4096:]:
            raise ValueError('Response is not a complete PDF')
    elif not (data.startswith(b'\x1f\x8b') or data[257:262] == b'ustar'):
        raise ValueError('Source response is not a tar or gzip archive')
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.part')
    temp.write_bytes(data)
    temp.replace(path)


def arxiv(start, end, download=True):
    """Page the declared title/abstract search until its revision window is covered."""
    query = '(' + ' OR '.join('cat:' + cat for cat in CATEGORIES) + ') AND ('
    query += ' OR '.join(f'(ti:"{phrase}" OR abs:"{phrase}")' for phrase in PHRASES) + ')'
    url = 'https://export.arxiv.org/api/query'
    rows, problems = [], []
    selected, seen = [], set()
    offset, pages, examined = 0, 0, 0
    previous = None
    covered = False
    while True:
        if pages:
            time.sleep(ARXIV_REQUEST_INTERVAL)
        try:
            for attempt in range(3):
                try:
                    response = get(url, timeout=(10, 35), params=dict(search_query=query,
                        start=offset, max_results=ARXIV_PAGE_SIZE,
                        sortBy='lastUpdatedDate', sortOrder='descending'))
                    break
                except requests.RequestException:
                    if attempt == 2:
                        raise
                    time.sleep(ARXIV_REQUEST_INTERVAL)
            data = ET.fromstring(response.content)
            entries = data.findall('{*}entry')
            reported_total = data.findtext('{http://a9.com/-/spec/opensearch/1.1/}totalResults')
            pages += 1
            if not entries:
                covered = reported_total is not None and offset >= int(reported_total)
                if not covered:
                    problems.append(f'Empty page at offset {offset} before confirmed exhaustion')
                break
            page_new = 0
            for entry in entries:
                paper = entry.findtext('{*}id', '').rsplit('/', 1)[-1]
                if not ARXIV_ID.fullmatch(paper):
                    raise ValueError(f'Unexpected versioned arXiv ID {paper}')
                updated = date.fromisoformat(entry.findtext('{*}updated')[:10])
                if previous is not None and updated > previous:
                    raise ValueError('arXiv returned unsorted revision dates')
                previous = updated
                examined += 1
                if paper in seen:
                    continue
                seen.add(paper)
                page_new += 1
                if updated < start:
                    covered = True
                    break
                if updated <= end:
                    selected.append((paper, updated, entry))
            if covered:
                break
            offset += len(entries)
            if reported_total is not None and offset >= int(reported_total):
                covered = True
                break
            if not page_new:
                raise ValueError('arXiv pagination repeated records before covering the window')
        except (requests.RequestException, ValueError, TypeError, ET.ParseError) as exc:
            problems.append(f'Discovery page at offset {offset}: {exc}')
            break
    # Keep discoveries even if a later page or document cannot be retrieved.
    for paper, updated, entry in selected:
        title = ' '.join(entry.findtext('{*}title').split())
        base = library.CORPUS / 'arxiv_frontier' / paper
        pdf = base / 'paper.pdf'
        base.mkdir(parents=True, exist_ok=True)
        save_json(base / 'metadata.json', dict(id=paper, title=title,
            abstract=' '.join(entry.findtext('{*}summary', '').split()), updated=str(updated),
            original_url='https://arxiv.org/abs/' + paper))
        for dest, link, kind in ((pdf, f'https://arxiv.org/pdf/{paper}', 'pdf'),
                                  (base/'source.tar.gz', f'https://arxiv.org/src/{paper}', 'source')):
            if not download:
                continue
            try:
                if not dest.exists():
                    time.sleep(ARXIV_REQUEST_INTERVAL)
                archive(link, dest, kind)
            except (requests.RequestException, ValueError, OSError) as exc:
                problems.append(f'{paper} {kind}: {exc}')
        original = 'https://arxiv.org/abs/' + paper
        topics = venue_sweep.matches(title + ' ' + entry.findtext('{*}summary', ''))
        rows.append(dict(id='arXiv-' + paper, title=title,
            authors=', '.join(a.findtext('{*}name') for a in entry.findall('{*}author')),
            publication_date=entry.findtext('{*}published')[:10], source='P3 arXiv',
            doi_or_arxiv=paper, original_url=original, version=f'{paper} updated {updated}',
            local_file_path=pdf.relative_to(library.PROJECT).as_posix() if pdf.exists() else '',
            publication_review_status='arXiv author version. Journal status requires source check.',
            ai_involvement='Undetermined', formal_verification_status='Unassessed',
            reading_status='unread', mathematical_topics=', '.join(topics)
                or ', '.join(c.get('term') for c in entry.findall('{*}category')),
            follow_up_status='Read methods, proofs and appendices.' if pdf.exists()
                else 'Full text queued for download. Metadata is not a completed reading.'))
    return rows, dict(endpoint=url, query=query, records_examined=examined, matched=len(rows),
        pages=pages, page_size=ARXIV_PAGE_SIZE, date_window_covered=covered,
        scope='Declared categories intersected with title OR abstract phrases, by revision date. '
              'Metadata discovery is not full reading and is not a census of all relevant literature.',
        retrieval_issues=problems)


def publication_files(url, label, download=True):
    response = get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    article = soup.find('article') or soup.find('main') or soup
    article_text = article.get_text(' ', strip=True)
    topics = venue_sweep.matches(article_text)
    # Institution research pages remain leads even when terminology is unfamiliar.
    folder_name = label.split()[0].lower()
    slug = re.sub(r'[^A-Za-z0-9_.-]', '_', urlsplit(url).path.strip('/')) or 'index'
    article_path = library.CORPUS / 'institutional' / folder_name / (slug + '.html')
    article_path.parent.mkdir(parents=True, exist_ok=True)
    article_path.write_bytes(response.content)
    date_meta = soup.select_one('meta[property="article:published_time"], meta[name="citation_date"]')
    date_text = date_meta.get('content', '')[:10] if date_meta else ''
    files = {}
    for link in soup.select('a[href]'):
        dest = urljoin(url, link['href']).split('#')[0]
        path = urlsplit(dest).path.lower()
        caption = link.get_text(' ', strip=True).casefold()
        main = bool(re.fullmatch(r'(?:download|read|view)?\s*(?:the |our |full )?(?:research |technical )?(?:paper|pdf|report)(?:\s*\(pdf\))?', caption))
        appendix = caption in ('appendix', 'supplement', 'supplementary material')
        if not main and not appendix:
            continue
        if urlsplit(dest).hostname in ('arxiv.org', 'www.arxiv.org') and path.startswith('/abs/'):
            dest = dest.replace('/abs/', '/pdf/')
        elif not path.endswith('.pdf'):
            continue
        files.setdefault(dest, 'paper' if main else 'appendix')
    folder = 'anthropic_math' if label.startswith('Anthropic') else 'ai_formal_proofs'
    results = []
    for dest, kind in sorted(files.items()):
        ident = hashlib.sha256(dest.encode()).hexdigest()[:20]
        local = library.CORPUS/folder/(ident + '.pdf')
        info = dict(kind=kind, url=dest, id='PDF-'+ident)
        if download:
            try:
                archive(dest, local, 'pdf')
            except (requests.RequestException, ValueError) as exc:
                info['retrieval_issue'] = str(exc)
        if local.exists():
            info['local_file_path'] = local.relative_to(library.PROJECT).as_posix()
        results.append(info)
    authors = [tag.get('content', '').strip() for tag in soup.select('meta[name="citation_author"]')]
    return date_text, ', '.join(author for author in authors if author), results, article_path.relative_to(library.PROJECT).as_posix(), topics


def institution(label, url, start, end, download=True):
    response = get(url)
    announcements = {}
    if label.startswith('Anthropic'):
        soup = BeautifulSoup(response.content, 'html.parser')
        for a in soup.select('a[href]'):
            src = urljoin(url, a['href'])
            title = a.get_text(' ', strip=True)
            if '/research/' in src and urlsplit(src).hostname == urlsplit(url).hostname:
                announcements.setdefault(src, (title, ''))
    else:
        root = ET.fromstring(response.content)
        for item in root.findall('.//item'):
            title, src = item.findtext('title'), item.findtext('link')
            stamp = parsedate_to_datetime(item.findtext('pubDate')).date()
            if start <= stamp <= end:
                announcements[src] = (title, str(stamp))
    matches = []
    for src, (title, stamp) in announcements.items():
        item = dict(title=title, url=src, date=stamp)
        try:
            pub_date, item['authors'], item['publisher_files'], item['local_article'], item['topics'] = publication_files(src, label, download)
            item['date'] = pub_date or stamp
            item['relevance'] = 'topic match' if item['topics'] else 'pending primary-page inspection'
        except requests.RequestException as exc:
            item['retrieval_issue'] = str(exc)
        matches.append(item)
    return dict(endpoint=url, matched=len(matches), items=matches,
        scope='All recent feed items and all visible Anthropic research links. No mathematics-title filter. '
              'Research pages and uncertain leads are retained. Landing-page coverage is not the complete institutional archive.')


def github(repo):
    path = 'releases/latest' if repo.endswith('/lean4') else 'commits'
    url = f'https://api.github.com/repos/{repo}/{path}'
    item = get(url, params={'per_page':1} if path == 'commits' else {}).json()
    if path == 'commits':
        item = item[0]
        return dict(endpoint=url, revision=item['sha'], date=item['commit']['committer']['date'], url=item['html_url'])
    return dict(endpoint=url, revision=item['tag_name'], date=item['published_at'], url=item['html_url'])


def save_json(path, value):
    payload = json.dumps(value, indent=2, ensure_ascii=False) + '\n'
    if path.exists() and path.read_text(encoding='utf-8') == payload:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(payload, encoding='utf-8')
    temporary.replace(path)


def venues(end, days, imported, download=True):
    directory = library.CORPUS/'peer_reviewed'
    saved = directory/f'venues-{end}.json'
    if imported is None:
        curation = {}
        for snapshot in sorted(directory.glob('venues-????-??-??.json')):
            prior = json.loads(snapshot.read_text(encoding='utf-8'))
            curation.update({i['id']:i['curation'] for i in prior['items'] if i.get('curation')})
        report = venue_sweep.sweep_venues(end, days, directory/'venue_docs' if download else None, curation)
    else:
        report = json.loads(imported.read_text(encoding='utf-8-sig'))
        if report['as_of'] != str(end) or report['days'] != days:
            raise ValueError('Venue intake does not match the requested observation window')
    save_json(saved, report)
    rows = []
    for item in report['items']:
        curated = item.get('curation', {})
        manuscript = curated.get('author_manuscript', {})
        companions = [manuscript.get('primary_url'), manuscript.get('source_url'),
                      curated.get('supplement_url'), curated.get('author_code')]
        collected = item['local_file_path']
        if collected and download:
            target = library.PROJECT/collected
            if not target.is_file():
                raise FileNotFoundError(target)
            collected = target.relative_to(library.PROJECT).as_posix()
        rows.append(dict(item, authors=', '.join(item['authors']) if isinstance(item['authors'],list) else item['authors'],
            source='P1 '+item['source'], local_file_path=collected,
            publication_review_status=curated.get('publication_review_status',item.get('publication_review_status','Unassessed')),
            reading_progress=curated.get('reading_progress',''), reading_status=curated.get('reading_status',item['reading_status']),
            mathematical_topics=', '.join(item['title_matches']), fulltext_url=item.get('open_pdf_url',''),
            companion_urls=' '.join(url for url in companions if url),
            extracted_instruments=' / '.join(curated.get('instruments', [])),
            version=item.get('local_version',item.get('version','Publisher record')),
            fp_relevance=curated.get('discovery_relevance',''), follow_up_status='Inspect primary argument and supplementary materials.'))
    summary = [{k:s.get(k) for k in ('source','channel','scanned','matches','failures')} for s in report['sources']]
    return rows, dict(scope=report['scope'], matched=len(rows), sources=summary,
                      local_report=saved.relative_to(library.PROJECT).as_posix())


def daily_entry(end, new_ids):
    path = library.ROOT/'DAILY_DISCOVERIES.md'
    log = path.read_text(encoding='utf-8') if path.exists() else '# Daily discoveries\n'
    marker = f'<!-- sweep {end} -->'
    line = (f'{marker} The dated sweep recorded {len(new_ids)} newly indexed editions. '
            f'[Source counts and retrieval exceptions](snapshots/discovery-{end}.json)')
    if marker in log:
        log = '\n'.join(line if marker in old else old for old in log.splitlines()) + '\n'
    elif f'## {end}' in log:
        log = log.replace(f'## {end}', f'## {end}\n\n{line}', 1)
    else:
        log += f'\n## {end}\n\n{line}\n'
    if not path.exists() or log != path.read_text(encoding='utf-8'):
        path.write_text(log, encoding='utf-8')


def sweep(end, days, venue_snapshot=None, download=True):
    start = end - timedelta(days=days-1)
    index = library.ROOT/'index.csv'
    if not index.exists():
        raise ValueError('Build the initial local catalog with library.py first')
    observations = {}
    rows = []
    def check(name, fn):
        try:
            return fn()
        except (requests.RequestException, ValueError, OSError, KeyError, ET.ParseError) as exc:
            observations[name] = {'error':str(exc)}
            return None
    for repo in GIT_REPOS:
        value = check(repo, lambda: github(repo))
        if value:
            observations[repo] = value
    if tip := observations['openai/math'].get('revision'):
        observations['openai/math']['index_current'] = tip == library.EDITIONS[-1][1]
        if not observations['openai/math']['index_current']:
            library.git('fetch', 'origin', tip)
            observations['openai/math']['follow_up'] = 'New upstream revision fetched locally. Compare primary catalogs before assigning editions.'
    for name, url in FEEDS.items():
        value = check(name, lambda: institution(name, url, start, end, download))
        if value:
            observations[name] = value
            for item in value['items']:
                if item.get('local_article'):
                    rows.append(dict(id='web:' + item['url'], title=item['title'], authors=item.get('authors', ''),
                        publication_date=item['date'], source=name, original_url=item['url'],
                        local_file_path=item['local_article'], version='Publisher web article captured ' + str(end),
                        publication_review_status='Institutional web article. Research relevance requires reading.',
                        reading_status='unread', formal_verification_status='Unassessed', ai_involvement='Unassessed',
                        mathematical_topics=', '.join(item.get('topics', {})),
                        follow_up_status='Inspect the complete article, linked paper and supplements.'))
                for doc in item.get('publisher_files', []):
                    if doc['kind'] == 'paper':
                        companions = [p['url'] for p in item['publisher_files'] if p['kind'] == 'appendix']
                        rows.append(dict(id=doc['id'], title=item['title'], authors=item.get('authors', ''),
                            publication_date=item['date'], source=name, original_url=doc['url'],
                            local_file_path=doc.get('local_file_path',''), version='Publisher PDF at linked URL',
                            publication_review_status='Institutional technical report', reading_status='unread',
                            fulltext_url=doc['url'], companion_urls=' '.join(companions + [item['url']]),
                            formal_verification_status='Unassessed', ai_involvement='Unassessed',
                            follow_up_status='Confirm author list and inspect linked supplementary files.'))
    result = check('arXiv', lambda: arxiv(start, end, download))
    if result:
        arxiv_rows, observations['arXiv'] = result
        rows.extend(arxiv_rows)
    result = check('Journals and conferences', lambda: venues(end, days, venue_snapshot, download))
    if result:
        venue_rows, observations['Journals and conferences'] = result
        rows.extend(venue_rows)
    by_id = {row['id']:row for row in rows}
    with FileLock(str(library.CORPUS/'.index.lock'), timeout=30):
        existing = library.table(index)
        new_ids = [ident for ident in by_id if ident not in existing]
        library.merge(existing, by_id)
        library.save_table(index, library.FIELDS, existing.values())
    snapshot = library.ROOT/'snapshots'/f'discovery-{end}.json'
    prior = json.loads(snapshot.read_text(encoding='utf-8')) if snapshot.exists() else {}
    seen_today = sorted(set(prior.get('newly_indexed',prior.get('new_arxiv_ids',[]))) | set(new_ids))
    save_json(snapshot, dict(date=str(end), window_start=str(start), window_end=str(end), newly_indexed=seen_today,
        document_downloads_requested=download,
        sources=observations))
    daily_entry(end, seen_today)
    print(f'{end} within {start} to {end}: {len(rows)} identified editions, {len(new_ids)} first indexed.')
    for name, item in observations.items():
        print(name, item.get('error', item.get('revision', item.get('matched'))))
    return observations


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--date', type=date.fromisoformat, default=datetime.now(ZoneInfo('Asia/Shanghai')).date())
    cli.add_argument('--days', type=int, default=7)
    cli.add_argument('--venue-snapshot', type=Path, help="Use a completed venue pass for exactly this window")
    cli.add_argument('--metadata-only', action='store_true', help='Save the complete discovery queue first. Full texts stay pending until downloaded.')
    options = cli.parse_args()
    if options.days < 1:
        cli.error('--days must be positive')
    library.CORPUS.mkdir(parents=True, exist_ok=True)
    with FileLock(str(library.CORPUS/'.sweep.lock'), timeout=0):
        sweep(options.date, options.days, options.venue_snapshot, download=not options.metadata_only)
