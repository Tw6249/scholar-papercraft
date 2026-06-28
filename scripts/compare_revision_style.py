#!/usr/bin/env python3
"""Compare an original draft and revision for language-layer regressions."""

from __future__ import annotations

import argparse
from pathlib import Path

from language_metrics import (
    extract_citation_keys,
    extract_numbers,
    extract_ref_keys,
    language_metrics,
    metric_table,
)
from paper_state_common import Issue, print_issue_report, read_text


def delta(after: float, before: float) -> float:
    return after - before


def percent_increase(after: int, before: int) -> float:
    return (after - before) / max(before, 1) * 100


def compare(before_text: str, after_text: str, location: str) -> tuple[list[Issue], list[tuple[str, str, str]]]:
    before = language_metrics(before_text)
    after = language_metrics(after_text)
    issues: list[Issue] = []

    before_numbers = extract_numbers(before_text)
    after_numbers = extract_numbers(after_text)
    before_cites = extract_citation_keys(before_text)
    after_cites = extract_citation_keys(after_text)
    before_refs = extract_ref_keys(before_text)
    after_refs = extract_ref_keys(after_text)

    word_growth = percent_increase(after.word_count, before.word_count)
    if word_growth > 15:
        issues.append(
            Issue(
                "major",
                "revision_expanded_text",
                location,
                f"Revision is {word_growth:.1f}% longer ({before.word_count} -> {after.word_count} words).",
                "Trim before beautifying; justify any expansion with new licensed information.",
            )
        )
    if after.filler_count > before.filler_count:
        issues.append(Issue("minor", "filler_increased", location, f"Filler count increased ({before.filler_count} -> {after.filler_count})."))
    if after.vague_evaluator_count > before.vague_evaluator_count:
        issues.append(Issue("major", "vague_evaluators_increased", location, f"Vague evaluators increased ({before.vague_evaluator_count} -> {after.vague_evaluator_count})."))
    if after.weak_verb_count > before.weak_verb_count:
        issues.append(Issue("minor", "weak_verbs_increased", location, f"Weak verbs increased ({before.weak_verb_count} -> {after.weak_verb_count})."))
    if after.claim_strength_term_count > before.claim_strength_term_count:
        issues.append(
            Issue(
                "major",
                "claim_strength_escalation",
                location,
                f"Claim-strength terms increased ({before.claim_strength_term_count} -> {after.claim_strength_term_count}).",
                "Check that stronger terms are licensed by the claim ledger.",
            )
        )
    if after.technical_action_balance + 1.0 < before.technical_action_balance:
        issues.append(
            Issue(
                "minor",
                "technical_density_decreased",
                location,
                f"Technical/action density decreased ({before.technical_action_balance:.1f} -> {after.technical_action_balance:.1f}).",
                "Ensure fluency edits did not dilute the technical core.",
            )
        )
    if before_numbers != after_numbers:
        issues.append(
            Issue(
                "critical",
                "numbers_changed",
                location,
                f"Numbers changed: before={before_numbers}, after={after_numbers}.",
                "Do not change numbers during language editing unless explicitly authorized.",
            )
        )
    if before_cites != after_cites:
        issues.append(
            Issue(
                "critical",
                "citation_keys_changed",
                location,
                f"Citation keys changed: before={sorted(before_cites)}, after={sorted(after_cites)}.",
                "Do not add, remove, or mutate citations during language editing.",
            )
        )
    if before_refs != after_refs:
        issues.append(
            Issue(
                "critical",
                "latex_refs_or_labels_changed",
                location,
                f"LaTeX refs/labels changed: before={sorted(before_refs)}, after={sorted(after_refs)}.",
                "Do not mutate labels or references during language editing.",
            )
        )

    rows = []
    before_table = dict(metric_table(before))
    after_table = dict(metric_table(after))
    for key in before_table:
        rows.append((key, before_table[key], after_table.get(key, "")))
    return issues, rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", help="Original draft file")
    parser.add_argument("after", help="Revised draft file")
    parser.add_argument("--fail-on-major", action="store_true", help="Exit nonzero when major or critical issues are found")
    parser.add_argument("--metrics", action="store_true", help="Print before/after metrics")
    args = parser.parse_args()

    before_path = Path(args.before).expanduser().resolve()
    after_path = Path(args.after).expanduser().resolve()
    issues, rows = compare(read_text(before_path), read_text(after_path), f"{before_path} -> {after_path}")

    if args.metrics:
        print("# Revision Metrics\n")
        print("| Metric | Before | After |")
        print("| --- | ---: | ---: |")
        for key, before_value, after_value in rows:
            print(f"| {key} | {before_value} | {after_value} |")
        print()

    code = print_issue_report("Revision Style Comparison", issues)
    if args.fail_on_major and any(issue.severity in {"critical", "major"} for issue in issues):
        return 1
    return 0 if not args.fail_on_major else code


if __name__ == "__main__":
    raise SystemExit(main())
