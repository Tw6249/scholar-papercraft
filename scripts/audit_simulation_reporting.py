#!/usr/bin/env python3
"""Audit simulation reporting, paired comparisons, and suspicious table diagnostics."""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path

from paper_state_common import Issue, iter_text_files, print_issue_report, read_text, should_fail


COMPARATIVE_RE = re.compile(r"\b(reduce[sd]?|improve[sd]?|outperform[sd]?|better|lower|higher|decrease[sd]?|increase[sd]?)\b", re.IGNORECASE)
COUNT_RE = re.compile(r"\b(N\s*=|n\s*=|seeds?|trials?|runs?|episodes?|confidence interval|CI|standard deviation|std|stderr)\b", re.IGNORECASE)
MATCHED_SEED_RE = re.compile(r"\bmatched[- ]seed\b|\bpaired\b", re.IGNORECASE)
MEAN_STD_RE = re.compile(r"\\pm|±|\bmean\s*(?:\+/-|and)\s*(?:std|standard deviation)\b", re.IGNORECASE)
PAIRED_STATS_RE = re.compile(r"\bpaired\b|\bconfidence interval\b|\bCI\b|\bWilcoxon\b|\bt[- ]test\b|\bbootstrap\b", re.IGNORECASE)
TABLE_NUMBER_RE = re.compile(r"(?:\d+\.\d+(?:\s*(?:\\times|x|×)\s*10\^\{?-?\d+\}?)?|\d+(?:\.\d+)?e[-+]?\d+)", re.IGNORECASE)


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def audit_file(path: Path) -> list[Issue]:
    text = read_text(path)
    issues: list[Issue] = []
    lines = text.splitlines()

    for number, line in enumerate(lines, start=1):
        if COMPARATIVE_RE.search(line) and not COUNT_RE.search(line) and re.search(r"\b(simulation|seed|trial|run|scenario|baseline|method)\b", line, re.IGNORECASE):
            issues.append(
                Issue(
                    "major",
                    "comparative_claim_missing_reporting_contract",
                    f"{path}:{number}",
                    f"Comparative empirical wording lacks visible metric denominator, trial count, or uncertainty on the same line: `{line.strip()}`",
                    "Report metric definition, direction, denominator, seeds/trials/runs, and uncertainty, or downgrade the claim.",
                )
            )

    if MATCHED_SEED_RE.search(text) and MEAN_STD_RE.search(text) and not PAIRED_STATS_RE.search(text):
        issues.append(
            Issue(
                "major",
                "matched_seed_without_paired_statistics",
                str(path),
                "The draft mentions matched seeds and mean/std reporting but no paired difference, confidence interval, or paired test.",
                "For reduction/improvement claims, report paired differences with CI/test or downgrade wording.",
            )
        )

    repeated: dict[str, list[int]] = defaultdict(list)
    for number, line in enumerate(lines, start=1):
        if "&" not in line and "|" not in line:
            continue
        for match in TABLE_NUMBER_RE.finditer(line):
            token = re.sub(r"\s+", "", match.group(0)).replace("×", "x")
            repeated[token].append(number)
    for token, locations in repeated.items():
        if len(locations) >= 4:
            issues.append(
                Issue(
                    "major",
                    "repeated_table_diagnostic_value",
                    f"{path}:{locations[0]}",
                    f"The same table-like numeric value `{token}` appears {len(locations)} times across rows.",
                    "Verify metric computation/logging or explain that the value is a deterministic threshold, monitor floor, or shared constant.",
                )
            )

    if re.search(r"\b(success rate|success)\b", text, re.IGNORECASE) and re.search(r"\b(1\.00|100\s*%)\b", text) and not re.search(r"\b(failure|stress|boundary|hard case|excluded)\b", text, re.IGNORECASE):
        issues.append(
            Issue(
                "major",
                "perfect_success_without_stress_or_failure_context",
                str(path),
                "Perfect success rates appear without visible failure, stress-test, boundary-case, or exclusion context.",
                "Add stress/failure cases or limit robustness/generality wording.",
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
    print_issue_report("Simulation Reporting Audit", issues)
    return 1 if should_fail(issues, args.fail_on) else 0


if __name__ == "__main__":
    raise SystemExit(main())
