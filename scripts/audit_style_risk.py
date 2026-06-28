#!/usr/bin/env python3
"""Context-aware academic style risk scanner.

This is not an AI detector and not a token ban list. It flags patterns that
often make academic prose generic, over-smoothed, or under-evidenced.
"""

from __future__ import annotations

import argparse
import math
import re
import statistics
from pathlib import Path

from paper_state_common import Issue, context, count_words, iter_text_files, line_number, print_issue_report, read_text, split_sentences


TRANSITIONS = {"moreover", "furthermore", "additionally", "in addition", "overall"}
VAGUE_EVALUATORS = {
    "important",
    "effective",
    "powerful",
    "comprehensive",
    "promising",
    "superior",
    "substantial",
    "crucial",
    "pivotal",
    "transformative",
    "groundbreaking",
}
EMPTY_CONCLUSION_RE = re.compile(
    r"\b(?:these|the)\s+results\s+(?:demonstrate|show|highlight|underscore)\s+"
    r"(?:the\s+)?(?:effectiveness|superiority|benefits?|advantages?)\b",
    re.IGNORECASE,
)
ROBUST_GENERIC_RE = re.compile(r"\brobust\s+(framework|method|approach|model|pipeline|system)\b", re.IGNORECASE)
ROBUST_ALLOWED_RE = re.compile(r"\brobust\s+(positive\s+invariance|control|optimization|stability|invariant\s+set)\b", re.IGNORECASE)
NOMINALIZATION_RE = re.compile(r"\b(realization|utilization|implementation|improvement|optimization|enhancement)\s+of\s+(?:the\s+)?\w+", re.IGNORECASE)
VAGUE_PRONOUN_START_RE = re.compile(r"^(this|these|it|such)\s+(?:is|are|was|were|can|could|may|might|also|therefore)\b", re.IGNORECASE)
TRIPLE_LIST_RE = re.compile(r"\b\w+(?:,\s+\w+){2,}\b")


def paragraph_starts(text: str) -> list[tuple[int, str]]:
    starts = []
    for para in re.split(r"\n\s*\n", text):
        stripped = para.strip()
        if not stripped:
            continue
        start = text.find(para)
        first = " ".join(stripped.split()[:4]).lower()
        starts.append((start, first))
    return starts


def audit_file(path: Path) -> list[Issue]:
    text = read_text(path)
    issues: list[Issue] = []
    words = max(count_words(text), 1)
    sentences = split_sentences(text)
    sentence_lengths = [count_words(s) for s in sentences if count_words(s) > 0]
    loc = str(path)

    transition_hits = []
    for term in TRANSITIONS:
        pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
        transition_hits.extend(pattern.finditer(text))
    density = len(transition_hits) / words * 1000
    if len(transition_hits) >= 3 and density > 6:
        issues.append(
            Issue(
                "minor",
                "formulaic_transition_density",
                loc,
                f"Transition density is {density:.1f} per 1000 words across {len(transition_hits)} hits.",
                "Use logical transitions only where they name a relation.",
            )
        )

    starts = paragraph_starts(text)
    last_transition = ""
    last_line = 0
    for start, first in starts:
        transition = next((t for t in TRANSITIONS if first.startswith(t)), "")
        if transition and transition == last_transition:
            issues.append(
                Issue(
                    "minor",
                    "repeated_paragraph_transition",
                    f"{loc}:{line_number(text, start)}",
                    f"Adjacent paragraphs start with `{transition}`.",
                    "Replace decorative transitions with the actual logical relation.",
                )
            )
        if transition:
            last_transition = transition
            last_line = line_number(text, start)
        elif last_line:
            last_transition = ""

    if len(sentence_lengths) >= 8:
        mean_len = statistics.mean(sentence_lengths)
        stdev_len = statistics.pstdev(sentence_lengths)
        if stdev_len < 5 and 14 <= mean_len <= 32:
            issues.append(
                Issue(
                    "minor",
                    "uniform_sentence_length",
                    loc,
                    f"Sentence lengths are unusually uniform: mean {mean_len:.1f}, standard deviation {stdev_len:.1f}.",
                    "Vary sentence roles naturally; do not force artificial short sentences.",
                )
            )

    long_run = 0
    for sent in sentences:
        long_run = long_run + 1 if count_words(sent) >= 38 else 0
        if long_run >= 3:
            idx = text.find(sent)
            issues.append(
                Issue(
                    "minor",
                    "consecutive_long_sentences",
                    f"{loc}:{line_number(text, idx)}",
                    "Three or more consecutive sentences exceed 38 words.",
                    "Split only where a sentence carries more than one scientific claim.",
                )
            )
            break

    for word in VAGUE_EVALUATORS:
        pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
        for match in pattern.finditer(text):
            issues.append(
                Issue(
                    "minor",
                    "vague_evaluative_language",
                    f"{loc}:{line_number(text, match.start())}",
                    f"`{match.group(0)}` needs a comparator, metric, setting, or source. Context: {context(text, match.start(), match.end(), 80)}",
                    "Ask: compared with what, measured how, under which setting, and supported by which result?",
                )
            )

    for match in EMPTY_CONCLUSION_RE.finditer(text):
        sent = next((s for s in sentences if match.group(0) in s), context(text, match.start(), match.end(), 80))
        if not re.search(r"\d", sent):
            issues.append(
                Issue(
                    "major",
                    "empty_conclusion",
                    f"{loc}:{line_number(text, match.start())}",
                    f"Generic result conclusion without number, comparator, or concrete capability: {sent}",
                    "State the measured result and claim supported, or downgrade the sentence.",
                )
            )

    for match in ROBUST_GENERIC_RE.finditer(text):
        local = context(text, max(0, match.start() - 40), min(len(text), match.end() + 80), 0)
        if not ROBUST_ALLOWED_RE.search(local) and not re.search(r"\b(perturb|disturb|uncertain|noise|domain shift|range|bounded)\b", local, re.IGNORECASE):
            issues.append(
                Issue(
                    "major",
                    "generic_robust",
                    f"{loc}:{line_number(text, match.start())}",
                    f"`{match.group(0)}` does not name the disturbance, uncertainty, or tested setting.",
                    "Use robust only with a formal uncertainty set or tested perturbation.",
                )
            )

    for match in NOMINALIZATION_RE.finditer(text):
        issues.append(
            Issue(
                "minor",
                "dense_nominalization",
                f"{loc}:{line_number(text, match.start())}",
                f"Nominalized phrasing may obscure the actor/action: `{match.group(0)}`.",
                "Prefer a verb construction when it preserves technical meaning.",
            )
        )

    for sent in sentences:
        if VAGUE_PRONOUN_START_RE.search(sent):
            idx = text.find(sent)
            issues.append(
                Issue(
                    "minor",
                    "vague_pronoun_reference",
                    f"{loc}:{line_number(text, idx)}",
                    f"Sentence starts with a vague reference: {sent[:160]}",
                    "Replace vague `this/these/it` with a stable noun when ambiguity is possible.",
                )
            )

    repeated_starts: dict[str, int] = {}
    for sent in sentences:
        start = " ".join(re.findall(r"[A-Za-z]+", sent.lower())[:3])
        if len(start.split()) == 3:
            repeated_starts[start] = repeated_starts.get(start, 0) + 1
    for start, count in repeated_starts.items():
        if count >= max(3, math.ceil(len(sentences) * 0.18)):
            issues.append(Issue("minor", "repeated_sentence_template", loc, f"Sentence opening `{start}` repeats {count} times."))

    triple_lists = TRIPLE_LIST_RE.findall(text)
    if len(triple_lists) >= 6 and len(triple_lists) / words * 1000 > 4:
        issues.append(Issue("minor", "list_rhythm_overuse", loc, "Dense repeated comma-list rhythm may read templated."))

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Draft files or directories")
    parser.add_argument("--fail-on-major", action="store_true", help="Exit nonzero when major issues are found")
    args = parser.parse_args()

    files = iter_text_files([Path(p) for p in args.paths])
    issues: list[Issue] = []
    for file in files:
        issues.extend(audit_file(file))

    code = print_issue_report("Contextual Style Risk Audit", issues)
    if args.fail_on_major and any(i.severity in {"critical", "major"} for i in issues):
        return 1
    return code


if __name__ == "__main__":
    raise SystemExit(main())
