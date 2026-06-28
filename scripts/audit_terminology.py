#!/usr/bin/env python3
"""Audit manuscript terminology against .paper-state/terminology.json."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from paper_state_common import Issue, iter_text_files, line_number, load_json, print_issue_report, read_text, state_file


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", nargs="?", default=".", help="Project folder containing .paper-state")
    parser.add_argument("--paths", nargs="*", help="Optional draft files/folders; defaults to project")
    args = parser.parse_args()

    terms_path = state_file(args.project, "terminology.json")
    terms_doc = load_json(terms_path, {"terms": []})
    terms = terms_doc.get("terms", []) or []
    if not terms:
        print("# Terminology Audit\n\nNo terminology entries configured.")
        return 0

    paths = [Path(p) for p in args.paths] if args.paths else [Path(args.project)]
    files = iter_text_files(paths)
    issues: list[Issue] = []

    for file in files:
        text = read_text(file)
        for term in terms:
            if not isinstance(term, dict):
                continue
            canonical = str(term.get("canonical", "")).strip()
            aliases = [str(a) for a in term.get("aliases", []) or []]
            forbidden = [str(a) for a in term.get("forbidden_synonyms", []) or []]
            if not canonical:
                continue
            canonical_re = re.compile(rf"\b{re.escape(canonical)}\b", re.IGNORECASE)
            canonical_present = bool(canonical_re.search(text))
            for alias in aliases:
                alias_re = re.compile(rf"\b{re.escape(alias)}\b", re.IGNORECASE)
                for match in alias_re.finditer(text):
                    if not canonical_present:
                        issues.append(
                            Issue(
                                "minor",
                                "alias_without_canonical_term",
                                f"{file}:{line_number(text, match.start())}",
                                f"Alias `{match.group(0)}` appears, but canonical term `{canonical}` is absent from this file.",
                                "Use the canonical term at first mention and aliases only when explicitly licensed.",
                            )
                        )
            for bad in forbidden:
                bad_re = re.compile(rf"\b{re.escape(bad)}\b", re.IGNORECASE)
                for match in bad_re.finditer(text):
                    issues.append(
                        Issue(
                            "major",
                            "forbidden_synonym",
                            f"{file}:{line_number(text, match.start())}",
                            f"Forbidden synonym `{match.group(0)}` used for canonical term `{canonical}`.",
                            "Replace with the canonical term unless the local context intentionally differs.",
                        )
                    )

    code = print_issue_report("Terminology Audit", issues)
    if any(issue.severity in {"critical", "major"} for issue in issues):
        return 1
    return code


if __name__ == "__main__":
    raise SystemExit(main())
