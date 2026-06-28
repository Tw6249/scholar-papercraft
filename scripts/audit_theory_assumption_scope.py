#!/usr/bin/env python3
"""Audit theorem-level wording for visible assumptions and evidence scope."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from paper_state_common import Issue, iter_text_files, print_issue_report, read_text, should_fail


FORMAL_CLAIM_RE = re.compile(r"\b(guarantee[sd]?|ensures?|preserv(?:e|es|ation)|stable|stability|safe|safety|convergen(?:t|ce)|optimal)\b", re.IGNORECASE)
ASSUMPTION_RE = re.compile(r"\b(under|assuming|assumption|provided that|subject to|if|when|certified|atomic|non[- ]Zeno|bounded|with probability)\b", re.IGNORECASE)
RESTRICTIVE_ASSUMPTION_RE = re.compile(r"\b(centralized initialization|global mirror|atomic commit|certified local solves?|non[- ]overlapping commits?|protected aborts?|zero[- ]order hold|Euler integration|sampled[- ]data)\b", re.IGNORECASE)
SECTION_RE = re.compile(r"^\s*(?:\\(?:sub)*section\*?\{([^}]*)\}|#{1,4}\s+(.+))", re.IGNORECASE)


def current_section_lines(text: str) -> dict[int, str]:
    section = ""
    out: dict[int, str] = {}
    for number, line in enumerate(text.splitlines(), start=1):
        heading = SECTION_RE.match(line)
        if heading:
            section = " ".join(part for part in heading.groups() if part).lower()
        out[number] = section
    return out


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def line_text(text: str, line: int) -> str:
    lines = text.splitlines()
    if 1 <= line <= len(lines):
        return lines[line - 1].strip()
    return ""


def audit_file(path: Path, evidence_boundary: str) -> list[Issue]:
    text = read_text(path)
    sections = current_section_lines(text)
    issues: list[Issue] = []
    restrictive_seen = bool(RESTRICTIVE_ASSUMPTION_RE.search(text))

    for match in FORMAL_CLAIM_RE.finditer(text):
        line = line_number(text, match.start())
        sentence = line_text(text, line)
        section = sections.get(line, "")
        if section in {"abstract", "conclusion", "conclusions"} and not ASSUMPTION_RE.search(sentence):
            severity = "critical" if restrictive_seen else "major"
            issues.append(
                Issue(
                    severity,
                    "unscoped_formal_claim",
                    f"{path}:{line}",
                    f"Theorem-level wording appears in {section or 'main text'} without visible assumptions: `{sentence}`",
                    "State the material assumptions in the title/abstract/conclusion wording, or downgrade to empirical/scoped language.",
                )
            )
        if evidence_boundary == "simulation_only" and re.search(r"\b(proves?|guarantee[sd]?|establish(?:es|ed)?)\b", sentence, re.IGNORECASE):
            issues.append(
                Issue(
                    "major",
                    "simulation_adjacent_formal_wording",
                    f"{path}:{line}",
                    f"Formal wording appears in a simulation-only audit context: `{sentence}`",
                    "Ensure the wording maps to theorem/proof evidence, not only simulation plots or tables.",
                )
            )

    if restrictive_seen and not re.search(r"\bunder\b.*\b(assumption|condition|certified|atomic|bounded)\b", text, re.IGNORECASE | re.DOTALL):
        issues.append(
            Issue(
                "major",
                "restrictive_assumptions_not_surface_scoped",
                str(path),
                "Restrictive assumptions appear in the draft, but the paper may not surface them near headline claims.",
                "Check title, abstract, contribution bullets, theorem statements, and conclusions for explicit conditional scope.",
            )
        )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".", help="Draft file or project directory")
    parser.add_argument("--evidence-boundary", choices=["unknown", "simulation_only", "benchmark_only", "hardware", "mixed"], default="unknown")
    parser.add_argument("--fail-on", choices=["critical", "major", "minor", "note", "none"], default="critical")
    args = parser.parse_args()

    issues: list[Issue] = []
    for file in iter_text_files([Path(args.path)]):
        issues.extend(audit_file(file, args.evidence_boundary))
    print_issue_report("Theory Assumption Scope Audit", issues)
    return 1 if should_fail(issues, args.fail_on) else 0


if __name__ == "__main__":
    raise SystemExit(main())
