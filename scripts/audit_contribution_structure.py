#!/usr/bin/env python3
"""Audit contribution bullets for feature-inventory and evaluation-only structure."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from paper_state_common import Issue, iter_text_files, print_issue_report, read_text, should_fail


HEADING_RE = re.compile(r"^\s*(?:\\(?:sub)*section\*?\{([^}]*)\}|#{1,4}\s+(.+))", re.IGNORECASE)
BULLET_RE = re.compile(r"^\s*(?:[-*]|\d+[.)]|\\item)\s+(.*)")
EVALUATION_ONLY_RE = re.compile(r"\b(we\s+)?(report|evaluate|implement|provide|release)\b.*\b(simulations?|experiments?|code|repository|implementation)\b", re.IGNORECASE)
MODULE_ONLY_RE = re.compile(r"\b(module|lifecycle|pipeline|transaction|implementation detail|software)\b", re.IGNORECASE)


def contribution_blocks(text: str) -> list[tuple[int, list[tuple[int, str]]]]:
    blocks: list[tuple[int, list[tuple[int, str]]]] = []
    active = False
    start_line = 0
    bullets: list[tuple[int, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        heading = HEADING_RE.match(line)
        if heading:
            if active and bullets:
                blocks.append((start_line, bullets))
            title = " ".join(part for part in heading.groups() if part)
            active = "contribution" in title.lower()
            start_line = number
            bullets = []
            continue
        if active:
            bullet = BULLET_RE.match(line)
            if bullet:
                bullets.append((number, bullet.group(1).strip()))
    if active and bullets:
        blocks.append((start_line, bullets))
    return blocks


def audit_file(path: Path) -> list[Issue]:
    text = read_text(path)
    issues: list[Issue] = []
    for start, bullets in contribution_blocks(text):
        if len(bullets) > 4:
            issues.append(
                Issue(
                    "major",
                    "too_many_contribution_bullets",
                    f"{path}:{start}",
                    f"Contribution list has {len(bullets)} bullets; this often reads as a feature inventory.",
                    "Merge into 2-4 claim-bearing contributions unless the author explicitly justifies five or more independent contributions.",
                )
            )
        for line, bullet in bullets:
            if EVALUATION_ONLY_RE.search(bullet):
                issues.append(
                    Issue(
                        "major",
                        "evaluation_only_contribution",
                        f"{path}:{line}",
                        f"Contribution bullet appears to report evaluation or code rather than a core technical contribution: `{bullet}`",
                        "Move evaluation reporting into the evidence summary unless the benchmark, dataset, protocol, or artifact is itself new and reusable.",
                    )
                )
            if MODULE_ONLY_RE.search(bullet) and not re.search(r"\b(under|evidence|proof|theorem|simulation|ablation|guarantee|bound|metric)\b", bullet, re.IGNORECASE):
                issues.append(
                    Issue(
                        "minor",
                        "module_inventory_contribution",
                        f"{path}:{line}",
                        f"Contribution bullet may describe an internal module rather than a claim: `{bullet}`",
                        "Rewrite with novelty object, technical action, evidence type, and scope/assumptions.",
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
    print_issue_report("Contribution Structure Audit", issues)
    return 1 if should_fail(issues, args.fail_on) else 0


if __name__ == "__main__":
    raise SystemExit(main())
