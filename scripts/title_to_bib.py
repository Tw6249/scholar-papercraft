#!/usr/bin/env python3
"""Experimentally recover BibTeX candidates from paper titles.

This script treats a title as a search query, not as bibliographic truth. It
collects candidates from public metadata services, verifies title similarity,
prefers DOI-backed records, and refuses low-confidence matches by default. Its
output is a draft for manual verification, not a guarantee of citation accuracy.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any


DEFAULT_TIMEOUT = 20
DEFAULT_USER_AGENT = "scholar-papercraft-title-to-bib/0.1"
TITLE_PUNCT_RE = re.compile(r"[^a-z0-9]+")
SPACE_RE = re.compile(r"\s+")
BRACE_RE = re.compile(r"[{}]")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


@dataclass
class Candidate:
    source: str
    title: str
    doi: str | None = None
    year: int | None = None
    authors: list[str] = field(default_factory=list)
    venue: str | None = None
    url: str | None = None
    arxiv_id: str | None = None
    work_type: str | None = None
    publisher: str | None = None
    score: float | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class Resolution:
    query: str
    accepted: Candidate | None
    confidence: float
    reason: str
    bibtex: str | None
    candidates: list[Candidate]


def normalize_title(title: str) -> str:
    title = html.unescape(title).lower()
    title = title.replace("&", " and ")
    title = TITLE_PUNCT_RE.sub(" ", title)
    return SPACE_RE.sub(" ", title).strip()


def title_similarity(a: str, b: str) -> float:
    na = normalize_title(a)
    nb = normalize_title(b)
    if not na or not nb:
        return 0.0
    ratio = SequenceMatcher(None, na, nb).ratio()
    a_tokens = set(na.split())
    b_tokens = set(nb.split())
    jaccard = len(a_tokens & b_tokens) / max(len(a_tokens | b_tokens), 1)
    containment = len(a_tokens & b_tokens) / max(min(len(a_tokens), len(b_tokens)), 1)
    return max(ratio, 0.55 * jaccard + 0.45 * containment)


def request_json(url: str, *, timeout: int, user_agent: str) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": user_agent, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def request_text(url: str, *, timeout: int, user_agent: str, accept: str = "text/plain") -> str:
    req = urllib.request.Request(url, headers={"User-Agent": user_agent, "Accept": accept})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def clean_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    doi = doi.strip()
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi, flags=re.I)
    doi = re.sub(r"^doi:\s*", "", doi, flags=re.I)
    doi = doi.strip().rstrip(".,;)")
    return doi.lower() or None


def first_text(value: Any) -> str | None:
    if isinstance(value, list) and value:
        value = value[0]
    if isinstance(value, str):
        return value.strip() or None
    return None


def issued_year(item: dict[str, Any]) -> int | None:
    for key in ("published-print", "published-online", "published", "issued", "created"):
        parts = item.get(key, {}).get("date-parts")
        if parts and isinstance(parts, list) and parts[0]:
            try:
                return int(parts[0][0])
            except (TypeError, ValueError):
                continue
    return None


def authors_from_crossref(item: dict[str, Any]) -> list[str]:
    authors: list[str] = []
    for author in item.get("author", [])[:8]:
        family = author.get("family", "")
        given = author.get("given", "")
        name = " ".join(part for part in (given, family) if part).strip()
        if name:
            authors.append(name)
    return authors


def query_crossref(title: str, rows: int, timeout: int, user_agent: str, email: str | None) -> list[Candidate]:
    params = {
        "query.title": title,
        "rows": str(rows),
        "select": "DOI,title,author,published,published-print,published-online,issued,created,container-title,type,publisher,score,URL",
    }
    if email:
        params["mailto"] = email
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
    data = request_json(url, timeout=timeout, user_agent=user_agent)
    candidates: list[Candidate] = []
    for item in data.get("message", {}).get("items", []):
        item_title = first_text(item.get("title"))
        if not item_title:
            continue
        candidates.append(
            Candidate(
                source="crossref",
                title=item_title,
                doi=clean_doi(item.get("DOI")),
                year=issued_year(item),
                authors=authors_from_crossref(item),
                venue=first_text(item.get("container-title")),
                url=item.get("URL"),
                work_type=item.get("type") or item.get("subtype"),
                publisher=item.get("publisher"),
                score=float(item["score"]) if "score" in item else None,
                raw=item,
            )
        )
    return candidates


def query_openalex(title: str, rows: int, timeout: int, user_agent: str, email: str | None) -> list[Candidate]:
    params = {
        "search": title,
        "per-page": str(rows),
    }
    if email:
        params["mailto"] = email
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    data = request_json(url, timeout=timeout, user_agent=user_agent)
    candidates: list[Candidate] = []
    for item in data.get("results", []):
        item_title = item.get("title") or item.get("display_name")
        if not item_title:
            continue
        authors = []
        for authorship in item.get("authorships", [])[:8]:
            name = authorship.get("author", {}).get("display_name")
            if name:
                authors.append(name)
        venue = None
        primary_location = item.get("primary_location") or {}
        source = primary_location.get("source") or {}
        if source:
            venue = source.get("display_name")
        venue = venue or (item.get("host_venue") or {}).get("display_name")
        candidates.append(
            Candidate(
                source="openalex",
                title=item_title,
                doi=clean_doi(item.get("doi")),
                year=item.get("publication_year"),
                authors=authors,
                venue=venue,
                url=item.get("id"),
                work_type=item.get("type"),
                raw=item,
            )
        )
    return candidates


def query_semantic_scholar(title: str, rows: int, timeout: int, user_agent: str) -> list[Candidate]:
    params = {
        "query": title,
        "limit": str(rows),
        "fields": "title,year,authors,venue,externalIds,url",
    }
    url = "https://api.semanticscholar.org/graph/v1/paper/search?" + urllib.parse.urlencode(params)
    data = request_json(url, timeout=timeout, user_agent=user_agent)
    candidates: list[Candidate] = []
    for item in data.get("data", []):
        item_title = item.get("title")
        if not item_title:
            continue
        external = item.get("externalIds") or {}
        authors = [a.get("name", "") for a in item.get("authors", [])[:8] if a.get("name")]
        candidates.append(
            Candidate(
                source="semantic_scholar",
                title=item_title,
                doi=clean_doi(external.get("DOI")),
                year=item.get("year"),
                authors=authors,
                venue=item.get("venue"),
                url=item.get("url"),
                arxiv_id=external.get("ArXiv"),
                work_type=item.get("publicationTypes", [None])[0] if item.get("publicationTypes") else None,
                raw=item,
            )
        )
    return candidates


def query_arxiv(title: str, rows: int, timeout: int, user_agent: str) -> list[Candidate]:
    # arXiv search syntax is brittle for long titles, so use all-title search.
    search = f'ti:"{title}"'
    params = {
        "search_query": search,
        "start": "0",
        "max_results": str(rows),
    }
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
    text = request_text(url, timeout=timeout, user_agent=user_agent, accept="application/atom+xml")
    root = ET.fromstring(text)
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    candidates: list[Candidate] = []
    for entry in root.findall("atom:entry", ns):
        item_title = "".join(entry.findtext("atom:title", default="", namespaces=ns).split())
        if not item_title:
            continue
        item_title = SPACE_RE.sub(" ", entry.findtext("atom:title", default="", namespaces=ns)).strip()
        published = entry.findtext("atom:published", default="", namespaces=ns)
        year = int(published[:4]) if published[:4].isdigit() else None
        authors = [
            name.text.strip()
            for name in entry.findall("atom:author/atom:name", ns)
            if name.text and name.text.strip()
        ][:8]
        doi = entry.findtext("arxiv:doi", default="", namespaces=ns)
        entry_id = entry.findtext("atom:id", default="", namespaces=ns)
        arxiv_id = entry_id.rstrip("/").split("/")[-1] if entry_id else None
        candidates.append(
            Candidate(
                source="arxiv",
                title=item_title,
                doi=clean_doi(doi),
                year=year,
                authors=authors,
                venue="arXiv",
                url=entry_id,
                arxiv_id=arxiv_id,
                work_type="preprint",
            )
        )
    return candidates


def collect_candidates(args: argparse.Namespace, title: str) -> list[Candidate]:
    candidates: list[Candidate] = []
    errors: list[str] = []
    sources = {
        "crossref": lambda: query_crossref(title, args.rows, args.timeout, args.user_agent, args.email),
        "openalex": lambda: query_openalex(title, args.rows, args.timeout, args.user_agent, args.email),
        "semantic_scholar": lambda: query_semantic_scholar(title, args.rows, args.timeout, args.user_agent),
        "arxiv": lambda: query_arxiv(title, args.rows, args.timeout, args.user_agent),
    }
    for source, func in sources.items():
        if source in args.skip_source:
            continue
        try:
            candidates.extend(func())
            time.sleep(args.sleep)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ET.ParseError, json.JSONDecodeError) as exc:
            errors.append(f"{source}: {exc}")
    if errors and args.verbose:
        print(f"[warn] {title}: " + "; ".join(errors), file=sys.stderr)
    return dedupe_candidates(candidates)


def dedupe_candidates(candidates: list[Candidate]) -> list[Candidate]:
    seen: set[tuple[str, str | None, str]] = set()
    unique: list[Candidate] = []
    for candidate in candidates:
        key = (candidate.source, candidate.doi, normalize_title(candidate.title))
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
    return unique


def confidence_for(query: str, candidate: Candidate, all_candidates: list[Candidate]) -> tuple[float, str]:
    sim = title_similarity(query, candidate.title)
    same_doi_sources = 0
    same_title_sources = 0
    for other in all_candidates:
        if other is candidate:
            continue
        if candidate.doi and other.doi == candidate.doi:
            same_doi_sources += 1
        elif title_similarity(candidate.title, other.title) >= 0.94:
            same_title_sources += 1

    confidence = sim
    reasons = [f"title_similarity={sim:.3f}"]
    if candidate.doi:
        confidence += 0.06
        reasons.append("has_doi")
    if same_doi_sources:
        confidence += min(0.08, 0.04 * same_doi_sources)
        reasons.append(f"doi_seen_in_{same_doi_sources + 1}_sources")
    if same_title_sources:
        confidence += min(0.04, 0.02 * same_title_sources)
        reasons.append(f"title_seen_in_{same_title_sources + 1}_sources")
    if candidate.source == "crossref" and candidate.doi:
        confidence += 0.02
        reasons.append("crossref_doi")
    if candidate.arxiv_id:
        confidence += 0.03
        reasons.append("has_arxiv_id")

    same_title_dois = {
        other.doi
        for other in all_candidates
        if other.doi and title_similarity(candidate.title, other.title) >= 0.98
    }
    if candidate.doi and len(same_title_dois) > 1:
        penalty = min(0.18, 0.05 * (len(same_title_dois) - 1))
        confidence -= penalty
        reasons.append(f"same_title_has_{len(same_title_dois)}_different_dois")

    work_type = (candidate.work_type or "").lower()
    if candidate.doi and not candidate.venue and work_type in {"posted-content", "preprint"}:
        confidence -= 0.08
        reasons.append("doi_is_unvenueed_preprint")

    return max(0.0, min(confidence, 1.0)), ", ".join(reasons)


def candidate_quality(candidate: Candidate) -> int:
    quality = 0
    if candidate.doi:
        quality += 3
    if candidate.venue and candidate.venue.lower() != "arxiv":
        quality += 2
    if candidate.arxiv_id:
        quality += 1
    work_type = (candidate.work_type or "").lower()
    if work_type in {"posted-content", "preprint"} and candidate.doi and not candidate.venue:
        quality -= 3
    return quality


def choose_candidate(query: str, candidates: list[Candidate], threshold: float) -> tuple[Candidate | None, float, str]:
    if not candidates:
        return None, 0.0, "no candidates found"
    scored = []
    for candidate in candidates:
        confidence, reason = confidence_for(query, candidate, candidates)
        scored.append((confidence, candidate, reason))
    scored.sort(key=lambda item: (item[0], candidate_quality(item[1])), reverse=True)
    best_confidence, best_candidate, best_reason = scored[0]
    if best_confidence < threshold:
        return None, best_confidence, f"below threshold {threshold:.2f}; {best_reason}"
    if len(scored) > 1:
        second_confidence, second_candidate, _ = scored[1]
        different_doi = best_candidate.doi and second_candidate.doi and best_candidate.doi != second_candidate.doi
        if different_doi and best_confidence - second_confidence < 0.04:
            return None, best_confidence, "ambiguous top candidates with different DOI values"
    return best_candidate, best_confidence, best_reason


def bibtex_for_doi(doi: str, timeout: int, user_agent: str) -> str | None:
    url = "https://doi.org/" + urllib.parse.quote(doi, safe="/")
    try:
        text = request_text(url, timeout=timeout, user_agent=user_agent, accept="application/x-bibtex")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        return None
    text = text.strip()
    if not text.startswith("@"):
        return None
    return text


def latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in value)


def make_key(candidate: Candidate) -> str:
    first_author = "unknown"
    if candidate.authors:
        first_author = candidate.authors[0].split()[-1]
    first_author = re.sub(r"[^A-Za-z0-9]+", "", first_author).lower() or "unknown"
    year = str(candidate.year or "nd")
    title_words = [
        token
        for token in normalize_title(candidate.title).split()
        if token not in {"a", "an", "and", "for", "from", "in", "of", "on", "the", "to", "with"}
    ][:3]
    return first_author + year + "".join(word[:8] for word in title_words)


def generated_bibtex(candidate: Candidate) -> str:
    entry_type = "article" if candidate.venue and candidate.venue.lower() != "arxiv" else "misc"
    lines = [f"@{entry_type}{{{make_key(candidate)},"]
    lines.append(f"  title = {{{latex_escape(candidate.title)}}},")
    if candidate.authors:
        authors = " and ".join(latex_escape(a) for a in candidate.authors)
        lines.append(f"  author = {{{authors}}},")
    if candidate.year:
        lines.append(f"  year = {{{candidate.year}}},")
    if candidate.venue and candidate.venue.lower() != "arxiv":
        lines.append(f"  journal = {{{latex_escape(candidate.venue)}}},")
    if candidate.doi:
        lines.append(f"  doi = {{{candidate.doi}}},")
    if candidate.arxiv_id:
        lines.append(f"  eprint = {{{candidate.arxiv_id}}},")
        lines.append("  archivePrefix = {arXiv},")
    if candidate.url:
        lines.append(f"  url = {{{candidate.url}}},")
    lines[-1] = lines[-1].rstrip(",")
    lines.append("}")
    return "\n".join(lines)


def bibtex_for_candidate(candidate: Candidate, timeout: int, user_agent: str) -> tuple[str | None, str]:
    if candidate.doi:
        bibtex = bibtex_for_doi(candidate.doi, timeout, user_agent)
        if bibtex:
            return bibtex, "doi_content_negotiation"
    if candidate.arxiv_id:
        return generated_bibtex(candidate), "generated_from_arxiv_metadata"
    if candidate.doi:
        return generated_bibtex(candidate), "generated_from_verified_metadata"
    return None, "accepted candidate has no DOI or arXiv ID"


def resolve_title(args: argparse.Namespace, title: str) -> Resolution:
    candidates = collect_candidates(args, title)
    accepted, confidence, reason = choose_candidate(title, candidates, args.min_confidence)
    if not accepted:
        return Resolution(title, None, confidence, reason, None, candidates)
    bibtex, bib_reason = bibtex_for_candidate(accepted, args.timeout, args.user_agent)
    if not bibtex:
        return Resolution(title, None, confidence, f"{reason}; {bib_reason}", None, candidates)
    return Resolution(title, accepted, confidence, f"{reason}; bibtex={bib_reason}", bibtex, candidates)


def read_titles(args: argparse.Namespace) -> list[str]:
    titles: list[str] = []
    titles.extend(args.title or [])
    if args.file:
        path = Path(args.file).expanduser()
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                titles.append(line)
    return titles


def candidate_to_json(candidate: Candidate) -> dict[str, Any]:
    return {
        "source": candidate.source,
        "title": candidate.title,
        "doi": candidate.doi,
        "year": candidate.year,
        "authors": candidate.authors,
        "venue": candidate.venue,
        "url": candidate.url,
        "arxiv_id": candidate.arxiv_id,
    }


def write_report(resolutions: list[Resolution], path: Path) -> None:
    data = []
    for result in resolutions:
        data.append(
            {
                "query": result.query,
                "accepted": candidate_to_json(result.accepted) if result.accepted else None,
                "confidence": result.confidence,
                "reason": result.reason,
                "candidates": [candidate_to_json(c) for c in result.candidates],
            }
        )
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", action="append", help="Paper title to resolve. Can be repeated.")
    parser.add_argument("--file", help="Text file with one title per line.")
    parser.add_argument("--out", default="resolved_references.bib", help="Output .bib path.")
    parser.add_argument("--report", default="title_to_bib_report.json", help="JSON report path.")
    parser.add_argument("--rows", type=int, default=5, help="Candidates per source.")
    parser.add_argument("--min-confidence", type=float, default=0.90, help="Minimum confidence for accepting a match.")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Network timeout in seconds.")
    parser.add_argument("--sleep", type=float, default=0.2, help="Pause between metadata services.")
    parser.add_argument("--email", help="Email for Crossref/OpenAlex polite requests.")
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT, help="HTTP user agent.")
    parser.add_argument(
        "--skip-source",
        action="append",
        default=[],
        choices=["crossref", "openalex", "semantic_scholar", "arxiv"],
        help="Skip a metadata source. Can be repeated.",
    )
    parser.add_argument("--verbose", action="store_true", help="Print source errors.")
    args = parser.parse_args()

    titles = read_titles(args)
    if not titles:
        parser.error("provide --title or --file")

    resolutions: list[Resolution] = []
    accepted_bibtex: list[str] = []
    for title in titles:
        result = resolve_title(args, title)
        resolutions.append(result)
        status = "accepted" if result.bibtex else "rejected"
        print(f"[{status}] {title}")
        print(f"  confidence: {result.confidence:.3f}")
        print(f"  reason: {result.reason}")
        if result.accepted:
            print(f"  match: {result.accepted.title}")
            print(f"  source: {result.accepted.source}")
            if result.accepted.doi:
                print(f"  doi: {result.accepted.doi}")
        if result.bibtex:
            accepted_bibtex.append(result.bibtex)

    out_path = Path(args.out).expanduser()
    report_path = Path(args.report).expanduser()
    if accepted_bibtex:
        out_path.write_text("\n\n".join(accepted_bibtex) + "\n", encoding="utf-8")
        print(f"\nWrote {len(accepted_bibtex)} BibTeX entries to {out_path}")
    else:
        print("\nNo BibTeX entries accepted.")
    write_report(resolutions, report_path)
    print(f"Wrote verification report to {report_path}")
    rejected = sum(1 for result in resolutions if not result.bibtex)
    return 1 if rejected else 0


if __name__ == "__main__":
    raise SystemExit(main())
