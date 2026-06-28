#!/usr/bin/env python3
"""Audit simulation, benchmark, hardware, and experiment wording boundaries."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from paper_state_common import Issue, iter_text_files, print_issue_report, read_text, should_fail


SECTION_RE = re.compile(r"(?:\\(?:sub)*section\*?\{([^}]*)\}|^#{1,4}\s+(.+)$)", re.IGNORECASE | re.MULTILINE)
STRONG_EXPERIMENT_RE = re.compile(
    r"\b(experimental validation|validated experimentally|real[- ]world|deployment|field trial|hardware experiment|physical (?:system|robot) trial)s?\b",
    re.IGNORECASE,
)
EXPERIMENT_TITLE_RE = re.compile(r"^\s*(?:\\(?:sub)*section\*?\{\s*experiments?\s*\}|#{1,4}\s+experiments?\s*)\s*$", re.IGNORECASE | re.MULTILINE)


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def snippet(text: str, start: int, end: int, width: int = 120) -> str:
    left = max(0, start - width)
    right = min(len(text), end + width)
    return " ".join(text[left:right].split())


def audit_file(path: Path, evidence_boundary: str, field: str) -> list[Issue]:
    text = read_text(path)
    issues: list[Issue] = []
    if evidence_boundary != "simulation_only":
        return issues

    for match in STRONG_EXPERIMENT_RE.finditer(text):
        issues.append(
            Issue(
                "critical",
                "simulation_only_overclaim",
                f"{path}:{line_number(text, match.start())}",
                f"Simulation-only evidence conflicts with experiment/hardware/deployment wording: `{snippet(text, match.start(), match.end())}`",
                "Replace with simulation-scoped wording or add hardware, physical-system, or real-world dataset evidence.",
            )
        )

    if field in {"control", "robotics"}:
        for match in EXPERIMENT_TITLE_RE.finditer(text):
            issues.append(
                Issue(
                    "major",
                    "experiments_section_for_simulation_only",
                    f"{path}:{line_number(text, match.start())}",
                    "A section titled `Experiments` is risky when all empirical evidence is simulated in control/robotics work.",
                    "Use `Simulation Study`, `Numerical Evaluation`, or `Numerical Simulations` unless the target venue convention explicitly permits `Experiments`.",
                )
            )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".", help="Draft file or project directory")
    parser.add_argument("--evidence-boundary", choices=["unknown", "simulation_only", "benchmark_only", "hardware", "mixed"], default="unknown")
    parser.add_argument("--field", choices=["control", "robotics", "cs", "ai", "mixed"], default="control")
    parser.add_argument("--fail-on", choices=["critical", "major", "minor", "note", "none"], default="critical")
    args = parser.parse_args()

    files = iter_text_files([Path(args.path)])
    issues: list[Issue] = []
    for file in files:
        issues.extend(audit_file(file, args.evidence_boundary, args.field))

    print_issue_report("Evidence Boundary Audit", issues)
    return 1 if should_fail(issues, args.fail_on) else 0


if __name__ == "__main__":
    raise SystemExit(main())
