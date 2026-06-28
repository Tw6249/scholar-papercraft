#!/usr/bin/env python3
"""Audit bibliography maturity for submission-oriented IEEE/control/CS drafts."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from paper_state_common import Issue, print_issue_report, should_fail


ENTRY_RE = re.compile(r"@\w+\s*\{\s*([^,]+),(.*?)(?=\n@\w+\s*\{|$)", re.DOTALL | re.IGNORECASE)
FIELD_RE = re.compile(r"\b([A-Za-z]+)\s*=\s*(?:\{([^{}]*)\}|\"([^\"]*)\")", re.DOTALL)


def parse_entries(path: Path) -> list[tuple[str, dict[str, str]]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    entries: list[tuple[str, dict[str, str]]] = []
    for match in ENTRY_RE.finditer(text):
        key = match.group(1).strip()
        fields: dict[str, str] = {}
        body = match.group(2)
        for field in FIELD_RE.finditer(body):
            fields[field.group(1).lower()] = " ".join((field.group(2) or field.group(3) or "").split())
        entries.append((key, fields))
    return entries


def has_published_venue(fields: dict[str, str]) -> bool:
    return bool(fields.get("journal") or fields.get("booktitle") or fields.get("doi"))


def is_arxiv(fields: dict[str, str]) -> bool:
    values = " ".join(fields.values()).lower()
    return "arxiv" in values or fields.get("archiveprefix", "").lower() == "arxiv" or bool(fields.get("eprint") and not has_published_venue(fields))


def audit_bib(path: Path) -> list[Issue]:
    issues: list[Issue] = []
    entries = parse_entries(path)
    if not entries:
        issues.append(Issue("major", "empty_or_unparsed_bibliography", str(path), "No BibTeX entries were parsed from this bibliography."))
        return issues

    arxiv_entries = []
    for key, fields in entries:
        if is_arxiv(fields):
            arxiv_entries.append(key)
            if not has_published_venue(fields):
                issues.append(
                    Issue(
                        "major",
                        "arxiv_only_reference",
                        f"{path}:{key}",
                        "Reference appears arXiv-only or lacks venue/DOI metadata.",
                        "Check whether a peer-reviewed or final DOI version exists and cite that version when available.",
                    )
                )
        if not fields.get("year"):
            issues.append(Issue("minor", "missing_reference_year", f"{path}:{key}", "Reference metadata lacks a year."))
        if not has_published_venue(fields) and not is_arxiv(fields):
            issues.append(
                Issue(
                    "minor",
                    "reference_lacks_venue_or_doi",
                    f"{path}:{key}",
                    "Reference metadata lacks journal, booktitle, or DOI.",
                    "Normalize BibTeX metadata before submission.",
                )
            )

    ratio = len(arxiv_entries) / len(entries)
    if ratio > 0.40:
        issues.append(
            Issue(
                "major",
                "high_arxiv_reference_ratio",
                str(path),
                f"{len(arxiv_entries)}/{len(entries)} references appear arXiv-only or arXiv-first.",
                "For IEEE journal submissions, check publication versions and replace foundational citations with final versions where available.",
            )
        )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", nargs="?", default=".", help="Project folder or .bib file")
    parser.add_argument("--fail-on", choices=["critical", "major", "minor", "note", "none"], default="critical")
    args = parser.parse_args()

    root = Path(args.project).expanduser().resolve()
    bib_files = [root] if root.is_file() and root.suffix.lower() == ".bib" else sorted(root.rglob("*.bib"))
    issues: list[Issue] = []
    if not bib_files:
        issues.append(
            Issue(
                "major",
                "missing_bibliography",
                str(root),
                "No .bib files found for reference maturity audit.",
                "Provide a bibliography or mark reference audit unavailable before submission.",
            )
        )
    for bib in bib_files:
        issues.extend(audit_bib(bib))
    print_issue_report("Reference Maturity Audit", issues)
    return 1 if should_fail(issues, args.fail_on) else 0


if __name__ == "__main__":
    raise SystemExit(main())
