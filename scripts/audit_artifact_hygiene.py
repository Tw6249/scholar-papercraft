#!/usr/bin/env python3
"""Audit main-paper leakage of script names, result files, and internal paths."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from paper_state_common import Issue, iter_text_files, print_issue_report, read_text, should_fail


ARTIFACT_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])(?:[A-Za-z0-9_.\\/-]+[\\/])?[A-Za-z0-9_.-]+\.(?:py|csv|json|jsonl|pkl|npy|npz|mat|ipynb|log)(?![A-Za-z0-9_.-])",
    re.IGNORECASE,
)
PROVENANCE_RE = re.compile(r"\b(raw_runs|aggregate|debug|logs?|notebook|script|ranking code)\b", re.IGNORECASE)
ALLOWED_HEADING_RE = re.compile(
    r"(code and data availability|data availability|reproducibility statement|supplementary material|appendix|reproduction instructions)",
    re.IGNORECASE,
)
HEADING_RE = re.compile(r"^\s*(?:\\(?:sub)*section\*?\{([^}]*)\}|#{1,4}\s+(.+))", re.IGNORECASE)


def allowed_line_numbers(text: str) -> set[int]:
    allowed: set[int] = set()
    active = False
    for number, line in enumerate(text.splitlines(), start=1):
        heading = HEADING_RE.match(line)
        if heading:
            title = " ".join(part for part in heading.groups() if part)
            active = bool(ALLOWED_HEADING_RE.search(title))
        if active:
            allowed.add(number)
    return allowed


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def audit_file(path: Path) -> list[Issue]:
    text = read_text(path)
    allowed = allowed_line_numbers(text)
    issues: list[Issue] = []
    for match in ARTIFACT_RE.finditer(text):
        line = line_number(text, match.start())
        if line in allowed:
            continue
        issues.append(
            Issue(
                "critical",
                "main_text_artifact_path",
                f"{path}:{line}",
                f"Main narrative exposes a script/data artifact path or filename: `{match.group(0)}`.",
                "Move concrete filenames, commands, and local paths to Code/Data Availability, supplement, appendix, or repository documentation.",
            )
        )
    for match in PROVENANCE_RE.finditer(text):
        line = line_number(text, match.start())
        if line in allowed:
            continue
        issues.append(
            Issue(
                "major",
                "main_text_provenance_term",
                f"{path}:{line}",
                f"Main narrative contains implementation/provenance wording: `{match.group(0)}`.",
                "Keep the paper focused on protocol, metrics, seeds, parameters, and evidence; move engineering provenance to reproducibility materials.",
            )
        )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".", help="Draft file or project directory")
    parser.add_argument("--fail-on", choices=["critical", "major", "minor", "note", "none"], default="critical")
    args = parser.parse_args()

    issues: list[Issue] = []
    for file in iter_text_files([Path(args.path)]):
        issues.extend(audit_file(file))
    print_issue_report("Artifact Hygiene Audit", issues)
    return 1 if should_fail(issues, args.fail_on) else 0


if __name__ == "__main__":
    raise SystemExit(main())
