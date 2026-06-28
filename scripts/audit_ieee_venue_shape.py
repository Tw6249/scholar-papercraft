#!/usr/bin/env python3
"""Audit IEEE-style submission shape and high-level venue constraints."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from paper_state_common import Issue, count_words, print_issue_report, read_text, should_fail


ABSTRACT_RE = re.compile(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", re.DOTALL | re.IGNORECASE)
TITLE_RE = re.compile(r"\\title(?:\[[^\]]*\])?\{([^}]*)\}", re.DOTALL | re.IGNORECASE)
INDEX_TERMS_RE = re.compile(r"\\begin\{IEEEkeywords\}|\\begin\{keywords\}|\\keywords\b|\\IEEEkeywords\b|Index Terms", re.IGNORECASE)
DISPLAY_MATH_RE = re.compile(r"\\\[|\\begin\{equation\}|\\begin\{align\}|\$\$")
CITE_RE = re.compile(r"\\(?:cite|citet|citep|parencite|textcite)\b")


def tex_files(root: Path) -> list[Path]:
    if root.is_file() and root.suffix.lower() == ".tex":
        return [root]
    if root.is_dir():
        return sorted(path for path in root.rglob("*.tex") if ".paper-state" not in path.parts)
    return []


def compact(text: str) -> str:
    return " ".join(text.split())


def audit_tex(path: Path) -> list[Issue]:
    text = read_text(path)
    issues: list[Issue] = []

    title = TITLE_RE.search(text)
    if title:
        title_text = compact(title.group(1))
        if re.search(r"\b(new|novel)\b", title_text, re.IGNORECASE):
            issues.append(
                Issue(
                    "major",
                    "title_contains_new_or_novel",
                    str(path),
                    f"IEEE titles should usually avoid `new` or `novel`: `{title_text}`",
                    "Use a specific, concise, descriptive title unless the target journal explicitly favors novelty wording.",
                )
            )

    abstracts = ABSTRACT_RE.findall(text)
    if not abstracts:
        issues.append(Issue("major", "missing_latex_abstract", str(path), "No LaTeX abstract environment found."))
    for abstract in abstracts:
        words = count_words(abstract)
        if words > 250:
            issues.append(
                Issue(
                    "critical",
                    "ieee_abstract_over_250_words",
                    str(path),
                    f"Abstract has approximately {words} words.",
                    "Compress to 250 words or less unless the target IEEE journal says otherwise.",
                )
            )
        if CITE_RE.search(abstract):
            issues.append(Issue("critical", "citation_in_ieee_abstract", str(path), "Abstract contains citation commands.", "Remove citations from the abstract."))
        if DISPLAY_MATH_RE.search(abstract):
            issues.append(Issue("critical", "display_math_in_ieee_abstract", str(path), "Abstract contains display math.", "Move equations to the main text and describe the idea in words."))
        if re.search(r"\b[A-Z]{2,}\b", abstract) and not re.search(r"\([A-Z]{2,}\)", abstract):
            issues.append(
                Issue(
                    "minor",
                    "possible_unexplained_abbreviation_in_abstract",
                    str(path),
                    "Abstract contains uppercase abbreviations; verify each is explained or standard for the venue.",
                )
            )

    if not INDEX_TERMS_RE.search(text):
        issues.append(
            Issue(
                "critical",
                "missing_index_terms",
                str(path),
                "IEEE-style draft has no visible Index Terms / Keywords block.",
                "Add 3-5 Index Terms or keywords unless the target venue uses a different format.",
            )
        )

    conclusion_match = re.search(r"\\(?:sub)*section\*?\{Conclusions?\}(.*?)(?:\\(?:sub)*section\*?\{|\\bibliography|\\begin\{thebibliography\}|$)", text, re.DOTALL | re.IGNORECASE)
    if conclusion_match and re.search(r"\b(guarantee[sd]?|robust|real[- ]world|deployment|significant(?:ly)?|state[- ]of[- ]the[- ]art)\b", conclusion_match.group(1), re.IGNORECASE):
        issues.append(
            Issue(
                "major",
                "conclusion_escalation_risk",
                str(path),
                "Conclusion contains high-strength or deployment wording.",
                "Verify every conclusion claim is no stronger than the theorem, experiment, figure, and limitation evidence.",
            )
        )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", nargs="?", default=".", help="LaTeX project folder or .tex file")
    parser.add_argument("--fail-on", choices=["critical", "major", "minor", "note", "none"], default="critical")
    args = parser.parse_args()

    root = Path(args.project).expanduser().resolve()
    files = tex_files(root)
    issues: list[Issue] = []
    if not files:
        issues.append(Issue("major", "missing_tex_source", str(root), "No .tex files found for IEEE venue-shape audit."))
    for file in files:
        issues.extend(audit_tex(file))
    print_issue_report("IEEE Venue Shape Audit", issues)
    return 1 if should_fail(issues, args.fail_on) else 0


if __name__ == "__main__":
    raise SystemExit(main())
