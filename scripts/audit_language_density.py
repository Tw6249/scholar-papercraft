#!/usr/bin/env python3
"""Audit academic prose for information density and language-layer risks.

This is a warning-oriented linter. It is not an AI detector. Use
--fail-on-major when a strict workflow or CI should reject major issues.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from language_metrics import language_metrics, metric_table
from paper_state_common import Issue, iter_text_files, print_issue_report, read_text


MODE_THRESHOLDS = {
    "cold-dense": {
        "transition_per_1000": 5.0,
        "filler_per_1000": 2.0,
        "vague_evaluator_per_1000": 4.0,
        "weak_verb_per_1000": 3.0,
        "nominalization_per_1000": 4.0,
        "sentence_mean": 30.0,
        "sentence_stdev_min": 5.0,
    },
    "narrative-persuasive": {
        "transition_per_1000": 8.0,
        "filler_per_1000": 2.5,
        "vague_evaluator_per_1000": 4.5,
        "weak_verb_per_1000": 4.0,
        "nominalization_per_1000": 4.5,
        "sentence_mean": 36.0,
        "sentence_stdev_min": 4.0,
    },
}


def audit_text(text: str, location: str, mode: str) -> tuple[list[Issue], list[tuple[str, str]]]:
    metrics = language_metrics(text)
    thresholds = MODE_THRESHOLDS[mode]
    issues: list[Issue] = []

    if metrics.empty_conclusion_count:
        issues.append(
            Issue(
                "major",
                "empty_conclusion",
                location,
                f"Found {metrics.empty_conclusion_count} generic result conclusion(s).",
                "Replace with a claim-supported takeaway naming the result, comparator, or scope.",
            )
        )
    if metrics.filler_per_1000 > thresholds["filler_per_1000"]:
        issues.append(
            Issue(
                "minor",
                "filler_density",
                location,
                f"Filler density is {metrics.filler_per_1000:.1f} per 1000 words.",
                "Delete fake openings and meta-discourse before polishing.",
            )
        )
    if metrics.transition_per_1000 > thresholds["transition_per_1000"]:
        severity = "major" if mode == "cold-dense" else "minor"
        issues.append(
            Issue(
                severity,
                "decorative_transition_density",
                location,
                f"Transition density is {metrics.transition_per_1000:.1f} per 1000 words in `{mode}` mode.",
                "Replace decorative transitions with explicit logical relations.",
            )
        )
    if metrics.vague_evaluator_per_1000 > thresholds["vague_evaluator_per_1000"]:
        issues.append(
            Issue(
                "major",
                "vague_evaluator_density",
                location,
                f"Vague evaluative language density is {metrics.vague_evaluator_per_1000:.1f} per 1000 words.",
                "Replace evaluators with metrics, settings, comparisons, or scoped claims.",
            )
        )
    if metrics.weak_verb_per_1000 > thresholds["weak_verb_per_1000"]:
        issues.append(
            Issue(
                "minor",
                "weak_verb_density",
                location,
                f"Weak verb density is {metrics.weak_verb_per_1000:.1f} per 1000 words.",
                "Prefer precise research actions such as bounds, estimates, enforces, reduces, or establishes.",
            )
        )
    if metrics.nominalization_per_1000 > thresholds["nominalization_per_1000"]:
        issues.append(
            Issue(
                "minor",
                "nominalization_density",
                location,
                f"Nominalization density is {metrics.nominalization_per_1000:.1f} per 1000 words.",
                "Convert noun stacks to verbs when this preserves technical meaning.",
            )
        )
    if metrics.sentence_count >= 8 and metrics.sentence_stdev < thresholds["sentence_stdev_min"]:
        issues.append(
            Issue(
                "minor",
                "uniform_sentence_rhythm",
                location,
                f"Sentence length standard deviation is {metrics.sentence_stdev:.1f}.",
                "Vary sentence jobs naturally; avoid uniform AI-like smoothing.",
            )
        )
    if metrics.sentence_mean > thresholds["sentence_mean"]:
        issues.append(
            Issue(
                "minor",
                "long_average_sentence",
                location,
                f"Average sentence length is {metrics.sentence_mean:.1f} words in `{mode}` mode.",
                "Split only where one sentence carries multiple scientific jobs.",
            )
        )
    if metrics.repeated_opening_count:
        issues.append(
            Issue(
                "minor",
                "repeated_sentence_openings",
                location,
                f"Found {metrics.repeated_opening_count} repeated sentence opening(s).",
                "Avoid template-like sentence starts unless parallel structure is intentional.",
            )
        )
    if metrics.word_count >= 80 and metrics.claim_bearing_ratio < 0.12:
        issues.append(
            Issue(
                "minor",
                "low_claim_bearing_ratio",
                location,
                f"Only {metrics.claim_bearing_ratio:.2f} of sentences look claim-bearing.",
                "Check whether the paragraph describes rather than argues.",
            )
        )

    return issues, metric_table(metrics)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Draft files or directories")
    parser.add_argument("--mode", choices=sorted(MODE_THRESHOLDS), default="cold-dense", help="Language target mode")
    parser.add_argument("--fail-on-major", action="store_true", help="Exit nonzero when major issues are found")
    parser.add_argument("--metrics", action="store_true", help="Print metrics table for each file")
    args = parser.parse_args()

    files = iter_text_files([Path(p) for p in args.paths])
    all_issues: list[Issue] = []
    metric_blocks: list[tuple[str, list[tuple[str, str]]]] = []
    for file in files:
        issues, table = audit_text(read_text(file), str(file), args.mode)
        all_issues.extend(issues)
        metric_blocks.append((str(file), table))

    if args.metrics:
        print(f"# Language Metrics ({args.mode})\n")
        for file, rows in metric_blocks:
            print(f"## {file}")
            for key, value in rows:
                print(f"- {key}: {value}")
            print()

    code = print_issue_report(f"Language Density Audit ({args.mode})", all_issues)
    if args.fail_on_major and any(issue.severity in {"critical", "major"} for issue in all_issues):
        return 1
    return 0 if not args.fail_on_major else code


if __name__ == "__main__":
    raise SystemExit(main())
