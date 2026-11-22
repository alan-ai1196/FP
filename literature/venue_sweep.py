"""Bounded venue sweep. Uses public publisher metadata and Python's standard library."""

import argparse
import calendar
import html
import json
import re
import time
from datetime import date, datetime, timedelta, timezone
from http.cookiejar import CookieJar
from html.parser import HTMLParser
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlencode, urljoin, urlparse
from urllib.request import HTTPCookieProcessor, Request, build_opener


JOURNALS = {
    "Annals of Mathematics": "0003-486X",
    "Inventiones Mathematicae": "0020-9910",
    "Journal of the American Mathematical Society": "0894-0347",
    "Acta Mathematica": "0001-5962",
    "Nature": "0028-0836",
    "Science": "0036-8075",
    "SIAM Journal on Computing": "0097-5397",
    "SIAM Journal on Optimization": "1052-6234",
    "SIAM Journal on Applied Dynamical Systems": "1536-0040",
    "SIAM Journal on Mathematics of Data Science": "2577-0187",
    "SIAM Journal on Applied Algebra and Geometry": "2470-6566",
    "SIAM Journal on Matrix Analysis and Applications": "0895-4798",
}
TITLE_PATTERNS = {
    "algebra and geometry": r"algebra(?:ic|s)?|geometr(?:y|ic)|topolog(?:y|ical)|symplectic|manifolds?|variet(?:y|ies)|cohomolog(?:y|ical)|moduli|sheaves|galois|hodge|automorphic|riemannian|curvature|lie groups?|modular forms?|categor(?:y|ies|ical)",
    "computation and learning": r"learning|regret|complexity|algorithm(?:ic|s)?|lower bounds?|theorem prov(?:ers?|ing)|formal verification|computability|communication costs?",
    "optimization and structure": r"tensors?|matri(?:x|ces)|polynomials?|optimi[sz]ation|approximation|dynamical systems?|entropy|information theor(?:y|etic)|representations?|factorizations?|spectral|stochastic control",
    "physical computation": r"(?:photonic|polaritonic|optical|quantum|boolean|arithmetic|neuromorphic) circuits?|memory bandwidth|reversible comput(?:ing|ation)",
    "predictive state and identification": r"predictive states?|causal states?|state identification|system identification|hidden markov|observable operators?|weighted automata|finite automata|sufficient statistics?|filtering",
    "sequence and world models": r"sequence model(?:s|ing)?|world models?|state[ -]space|recurrent|language models?|transformers?|attention|autoregressive|dynamics models?",
    "representation and learning dynamics": r"feature learning|representation learning|learning dynamics|implicit bias|symmetry breaking|compositional|in[ -]context learning|test[ -]time|continual learning|meta[ -]learning|superposition",
    "information and memory": r"information bottleneck|minimum description length|predictive information|rate[ -]distortion|compress(?:ion|ive)|working memory|associative memory|memory[ -]augmented|neural algorithms?|algorithm discovery",
    "observation and latent interfaces": r"tokeni[sz](?:ation|er|ers)|byte[ -]level|token[ -]free|latent prediction|continuous representations?|multimodal|patch(?:es|ing)?|sensorimotor",
    "interaction and decision": r"reinforcement learning|partial(?:ly)? observab(?:ility|le)|adaptive control|planning|exploration|decision processes?|causal inference|interventions?",
}
HEADERS = {"User-Agent": "FP-mathematics-literature/1.0 (+https://github.com/alan-ai1196/FP)"}
CROSSREF = "https://api.crossref.org"
PMLR = "https://proceedings.mlr.press/"
OPENREVIEW = "https://api2.openreview.net/notes"
PDF_LIMIT = 64 * 1024 * 1024
OPENER = build_opener(HTTPCookieProcessor(CookieJar()))


class MetaTags(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.fields = {}
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        if tag == "meta":
            attrs = dict(attrs)
            self.fields[attrs.get("name", "").lower()] = attrs.get("content", "")


def fetch(url, params=None, limit=20 * 1024 * 1024):
    if params:
        url += "?" + urlencode(params)
    for attempt in range(3):
        try:
            with OPENER.open(Request(url, headers=HEADERS), timeout=18) as response:
                body = response.read(limit + 1)
                if len(body) > limit:
                    raise ValueError(f"Response exceeded {limit} bytes")
                return body, response.url
        except HTTPError as error:
            if error.code not in (429, 502, 503, 504) or attempt == 2:
                raise
            retry = error.headers.get("Retry-After", "")
            seconds = int(retry) if retry.isdecimal() else 2 ** (attempt + 1)
            if seconds > 30:
                raise
            time.sleep(seconds)


def cleaned(value):
    return " ".join(html.unescape(re.sub(r"<[^>]*>", " ", value)).split())


def matches(title):
    return {topic: m.group(0).lower() for topic, pattern in TITLE_PATTERNS.items()
            if (m := re.search(r"\b(?:" + pattern + r")\b", title, re.I))}


def publication_in_window(work, start, end):
    for field in ("published-online", "published-print", "published", "issued"):
        parts = work.get(field, {}).get("date-parts", [[]])[0]
        if not parts or not all(parts):
            continue
        year, month, day = (parts + [1, 1])[:3]
        lower = date(year, month, day)
        if len(parts) == 3:
            upper = lower
        elif len(parts) == 2:
            upper = date(year, month, calendar.monthrange(year, month)[1])
        else:
            upper = date(year, 12, 31)
        if lower <= end and upper >= start:
            return "-".join([f"{parts[0]:04d}", *[f"{n:02d}" for n in parts[1:]]]), field
    return None


def record(source, identifier, title, authors, released, url, pdfs, coverage_date, basis, abstract=""):
    return {"id": identifier, "title": title, "authors": authors, "publication_date": released,
            "source": source, "doi_or_arxiv": identifier.removeprefix("doi:") if identifier.startswith("doi:") else "",
            "original_url": url, "date_in_scope": coverage_date, "date_basis": basis,
            "title_matches": matches(title + " " + abstract), "abstract": abstract,
            "pdf_candidates": list(dict.fromkeys(pdfs)),
            "open_pdf_url": "", "local_file_path": "", "reading_status": "unread",
            "publication_review_status": "Publisher or venue record. Review status unassessed",
            "formal_verification_status": "unassessed", "ai_involvement": "unassessed"}


def crossref_source(name, base, filters, start, end, stats):
    fields = "DOI,title,abstract,author,published,published-online,published-print,issued,link,URL"
    common = {"filter": ",".join([*filters, f"from-pub-date:{start}", f"until-pub-date:{end}"]),
              "select": fields, "rows": 250}
    stats["queries"].append(base + "?" + urlencode(common))
    cursor = "*"
    seen = set()
    while True:
        time.sleep(1.05)
        response = json.loads(fetch(base, dict(common, cursor=cursor))[0])["message"]
        batch = response["items"]
        stats["reported_total"] = response["total-results"]
        before = len(seen)
        for work in batch:
            if work["DOI"] in seen:
                continue
            seen.add(work["DOI"])
            stats["scanned"] += 1
            title = cleaned(" ".join(work.get("title", [])))
            abstract = cleaned(work.get("abstract", ""))
            when = publication_in_window(work, start, end)
            if not when:
                continue
            # Specialist venues are retained in full. Missing abstracts in broad
            # journals are unresolved leads, not evidence of irrelevance.
            if name in ("Nature", "Science") and abstract and not matches(title + " " + abstract):
                continue
            doi = work["DOI"].lower()
            pdfs = [x["URL"] for x in work.get("link", []) if "pdf" in x.get("content-type", "").lower()
                    or "/pdf" in x.get("URL", "").lower()]
            authors = [a.get("name") or " ".join(filter(None, (a.get("given"), a.get("family"))))
                       for a in work.get("author", [])]
            item = record(name, "doi:" + doi, title, authors, when[0], "https://doi.org/" + doi,
                          pdfs, when[0], "Crossref publisher deposit: " + when[1], abstract)
            if not matches(title + " " + abstract):
                item["relevance_pending"] = "Retained by specialist venue" if name not in ("Nature", "Science") else "Abstract unavailable. Inspect primary page"
            item["version"] = "Publisher-registered journal or proceedings record"
            yield item
        if stats["scanned"] >= stats["reported_total"]:
            return
        if len(seen) == before or not response.get("next-cursor"):
            raise ValueError("Pagination stopped before the reported total")
        cursor = response["next-cursor"]


def pmlr_source(name, start, end, stats):
    stats["queries"].append(PMLR)
    catalog = fetch(PMLR)[0].decode()
    volumes = re.findall(r'<li>\s*<a href="(v\d+)/?"[^>]*>.*?</a>\s*([^<]+)</li>', catalog, re.S)
    if not volumes:
        raise ValueError("Unrecognized PMLR volume listing")
    wanted = {f"Proceedings of {name} {y}" for y in range(start.year - 1, end.year + 1)}
    for volume, label in volumes:
        if cleaned(label) not in wanted:
            continue
        url = urljoin(PMLR, volume + "/")
        stats["queries"].append(url)
        page = fetch(url)[0].decode()
        desc = MetaTags(page[:15000]).fields.get("description", "")
        stamp = re.search(r"Published as Volume \d+ .*? on (\d{1,2} \w+ \d{4})", desc, re.I)
        if not stamp:
            raise ValueError("PMLR volume has no interpretable publisher release date: " + url)
        released = datetime.strptime(stamp[1], "%d %B %Y").date()
        stats.setdefault("volume_dates", {})[volume] = str(released)
        if not start <= released <= end:
            continue
        entries = re.findall(r'<div class="paper">(.*?)</div>', page, re.S)
        if not entries:
            raise ValueError("Unrecognized PMLR paper entries: " + url)
        for entry in entries:
            stats["scanned"] += 1
            title = cleaned(re.search(r'<p class="title">(.*?)</p>', entry, re.S)[1])
            authors = cleaned(re.search(r'<span class="authors">(.*?)</span>', entry, re.S)[1]).split(",")
            links = {cleaned(text): urljoin(url, html.unescape(link))
                     for link, text in re.findall(r'<a href="([^"]+)"[^>]*>(.*?)</a>', entry, re.S)}
            primary = links["abs"]
            pdfs = [link for text, link in links.items() if "pdf" in text.lower()]
            item = record(name, "pmlr:" + urlparse(primary).path.strip("/").removesuffix(".html"),
                          title, [a.strip() for a in authors], str(released), primary,
                          pdfs, str(released), "PMLR official volume publication date")
            item["open_pdf_url"] = next(iter(pdfs), "")
            yield item
    if not stats.get("volume_dates"):
        raise ValueError("No recent corresponding PMLR volume found")


def openreview_source(name, start, end, stats):
    for year in range(start.year, end.year + 1):
        venue = f"{name}.cc/{year}/Conference"
        offset = 0
        previous = None
        base = {"content.venueid": venue, "sort": "tmdate:desc", "limit": 200}
        stats["queries"].append(OPENREVIEW + "?" + urlencode(base))
        while True:
            notes = json.loads(fetch(OPENREVIEW, dict(base, offset=offset))[0])["notes"]
            for note in notes:
                changed = datetime.fromtimestamp(note["tmdate"] / 1000, timezone.utc).date()
                if previous and changed > previous:
                    raise ValueError("OpenReview returned unsorted modification dates")
                previous = changed
                stats["scanned"] += 1
                if changed < start:
                    break
                fields = {key: obj.get("value") for key, obj in note["content"].items()}
                title = cleaned(fields.get("title") or "")
                if changed > end or fields.get("venueid") != venue:
                    continue
                forum = note["forum"]
                published = datetime.fromtimestamp(note["pdate"] / 1000, timezone.utc).date() if note.get("pdate") else ""
                pdfs = ["https://openreview.net/pdf?id=" + note["id"]] if fields.get("pdf") else []
                yield record(name, "openreview:" + forum, title, fields.get("authors") or [], str(published),
                             "https://openreview.net/forum?id=" + forum, pdfs, str(changed),
                             "Accepted OpenReview note modification in UTC. Content change unverified",
                             cleaned(fields.get("abstract") or ""))
            if len(notes) < base["limit"] or previous is not None and previous < start:
                break
            offset += len(notes)


def program_source(name, start, end, stats):
    """A public presentation date is a discovery event separate from paper publication."""
    domain = "https://" + name.lower() + ".cc"
    for year in range(start.year, end.year + 1):
        url = f"{domain}/static/virtual/data/{name.lower()}-{year}-orals-posters.json"
        stats["queries"].append(url)
        while url:
            program = json.loads(fetch(url, limit=48 * 1024 * 1024)[0])
            for event in program["results"]:
                stats["scanned"] += 1
                if not event.get("starttime") or not event.get("visible", True):
                    continue
                stamp = datetime.fromisoformat(event["starttime"]).astimezone(timezone.utc).date()
                title = cleaned(event["name"])
                if not start <= stamp <= end:
                    continue
                primary = event.get("paper_url") or urljoin(domain, event["virtualsite_url"])
                parsed = urlparse(primary)
                forum = parse_qs(parsed.query).get("id", [""])[0] if parsed.hostname == "openreview.net" else ""
                key = "openreview:" + forum if forum else f"{name.lower()}:{year}:{event['id']}"
                pdf = event.get("paper_pdf_url") or ("https://openreview.net/pdf?id=" + forum if forum else "")
                yield record(name, key, title, [a["fullname"] for a in event["authors"]], "", primary,
                             [urljoin(domain, pdf)] if pdf else [], str(stamp), "Official conference presentation (UTC)",
                             cleaned(event.get("abstract") or ""))
            url = program.get("next")


def ordinal(number):
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    return str(number) + ("th" if 11 <= number % 100 <= 13 else suffix)


def source_runs(start, end):
    for venue, issn in JOURNALS.items():
        yield venue, crossref_source, (f"{CROSSREF}/journals/{issn}/works", ["type:journal-article"])
    for year in range(start.year, end.year + 1):
        titles = {"STOC": ("10.1145", f"Proceedings of the {ordinal(year - 1968)} Annual ACM Symposium on Theory of Computing"),
                  "FOCS": ("10.1109", f"{year} IEEE {ordinal(year - 1959)} Annual Symposium on Foundations of Computer Science (FOCS)")}
        for venue, (prefix, title) in titles.items():
            yield venue, crossref_source, (f"{CROSSREF}/prefixes/{prefix}/works", ["type:proceedings-article", "container-title:" + title])
    for name in ("ICML", "COLT"):
        yield name, pmlr_source, ()
    for name in ("ICLR", "NeurIPS"):
        yield name, program_source, ()
        yield name, openreview_source, ()


def save_pdf(item, directory):
    details = item.get("curation", {})
    candidates = [*item["pdf_candidates"], *details.get("publisher_pdf_urls", [])]
    author = details.get("author_manuscript", {})
    errors = []
    try:
        landing, resolved = fetch(item["original_url"], limit=6 * 1024 * 1024)
        if landing.lstrip().startswith(b"%PDF-"):
            candidates.insert(0, resolved)
        else:
            meta = MetaTags(landing.decode("utf-8", errors="replace")).fields
            if meta.get("citation_pdf_url"):
                candidates.insert(0, urljoin(resolved, meta["citation_pdf_url"]))
    except (OSError, ValueError) as error:
        errors.append(str(error))
    if author:
        candidates.append(author["pdf_url"])
    for candidate in dict.fromkeys(candidates):
        try:
            is_author = candidate == author.get("pdf_url")
            label = author["version"] if is_author else item["id"] + "-" + item["date_in_scope"]
            path = directory / (re.sub(r"[^A-Za-z0-9_.-]", "_", label) + ".pdf")
            if path.is_file():
                with path.open("rb") as previous:
                    if previous.read(5) != b"%PDF-":
                        raise ValueError("Existing local document failed PDF signature check")
                item.update(open_pdf_url=candidate, local_file_path=path.as_posix(),
                            pdf_status="Previously saved", local_version=author["version"] if is_author else "Publisher/venue PDF")
                if is_author and errors:
                    item["publisher_pdf_failures"] = errors
                return
            payload, resolved = fetch(candidate, limit=PDF_LIMIT)
            if not payload.lstrip().startswith(b"%PDF-") or b"%%EOF" not in payload[-4096:]:
                raise ValueError("Candidate returned incomplete or non-PDF content")
            directory.mkdir(parents=True, exist_ok=True)
            with NamedTemporaryFile(dir=directory, delete=False) as output:
                output.write(payload)
            Path(output.name).replace(path)
            item.update(open_pdf_url=candidate, local_file_path=path.as_posix(), pdf_status="Downloaded",
                        local_version=author["version"] if is_author else "Publisher/venue PDF")
            if is_author and errors:
                item["publisher_pdf_failures"] = errors
            return
        except (OSError, ValueError) as error:
            errors.append(str(error))
    item["pdf_status"] = "Awaiting primary PDF"
    item["pdf_failures"] = errors or ["No publisher PDF link in the record or landing page"]


def sweep_venues(as_of, days=7, pdf_dir=None, curation=None):
    """Return every matched item and per-source counts/failures for an inclusive date window."""
    end = date.fromisoformat(str(as_of))
    if days < 1:
        raise ValueError("days must be positive")
    start = end - timedelta(days=days - 1)
    items = {}
    sources = []
    for name, reader, args in source_runs(start, end):
        stats = {"source": name, "channel": reader.__name__.removesuffix("_source"),
                 "queries": [], "scanned": 0, "matches": 0, "failures": []}
        try:
            for item in reader(name, *args, start, end, stats):
                prior = items.setdefault(item["id"], item)
                event = {"channel": stats["channel"], "date": item["date_in_scope"], "basis": item["date_basis"]}
                events = prior.setdefault("discovery_events", [])
                if event not in events:
                    events.append(event)
                if not prior["publication_date"]:
                    prior["publication_date"] = item["publication_date"]
                prior["pdf_candidates"] = list(dict.fromkeys(prior["pdf_candidates"] + item["pdf_candidates"]))
                stats["matches"] += 1
        except (OSError, ValueError, KeyError, IndexError, TypeError) as error:
            stats["failures"].append(f"{type(error).__name__}: {error}")
        stats["status"] = "partial" if stats["failures"] else "complete within scope"
        sources.append(stats)
    result = sorted(items.values(), key=lambda item: (item["source"], item["title"], item["id"]))
    for item in result:
        if curation and item["id"] in curation:
            item["curation"] = curation[item["id"]]
            for key in ("publication_review_status", "ai_involvement", "formal_verification_status", "reading_status"):
                if key in item["curation"]:
                    item[key] = item["curation"][key]
            if pdf_dir is None and item["curation"].get("author_manuscript"):
                item["open_pdf_url"] = item["curation"]["author_manuscript"]["pdf_url"]
        if pdf_dir is not None:
            save_pdf(item, Path(pdf_dir))
    return {"as_of": str(end), "from": str(start), "days": days, "title_patterns": TITLE_PATTERNS,
            "scope": "Publisher-registered publication dates for the declared journal ISSNs and exact annual ACM/IEEE proceedings titles. All in-window specialist math and ML venue records are retained. Nature and Science use title plus deposited abstract, retaining records with missing abstracts for inspection. PMLR release dates, ICLR/NeurIPS official presentation dates and accepted OpenReview note modifications are distinct discovery channels. Inclusive UTC dates. Partial publication dates qualify when their ranges overlap the window. Metadata intake is not full reading.",
            "sources": sources, "items": result}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--pdf-dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    curation = {}
    if args.output.exists():
        prior = json.loads(args.output.read_text(encoding="utf-8"))
        if prior.get("as_of") != args.as_of:
            parser.error("Use a separate output filename to retain a different date's snapshot.")
        curation = {row["id"]: row["curation"] for row in prior["items"] if row.get("curation")}
    report = sweep_venues(args.as_of, args.days, args.pdf_dir, curation)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(report['items'])} matches, {sum(bool(s['failures']) for s in report['sources'])} source failures")
