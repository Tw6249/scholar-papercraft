#!/usr/bin/env python3
"""Scan drafts for scientific claims that often need evidence or scoping."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


TEXT_EXTS = {".tex", ".md", ".txt"}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TERMS = [
    ("stable", r"\bstabili[sz](?:e|es|ed|ing|ation)?\b|\bstable\b", "Needs proof or explicit empirical scope."),
    ("safe", r"\bsafe(?:ty)?\b|\bsafety-guaranteed\b", "Needs formal safety evidence or measured violations."),
    ("robust", r"\brobust(?:ness)?\b", "Needs perturbation range, uncertainty set, or robustness analysis."),
    ("real-time", r"\breal[- ]time\b", "Needs latency/frequency, hardware, and workload."),
    ("optimal", r"\b(?:globally\s+)?optimal(?:ity)?\b", "Needs proof or exact optimizer for stated objective."),
    ("guarantee", r"\bguarantee[sd]?\b|\bensures?\b", "Needs theorem, certification, or enforced constraint."),
    ("state-of-the-art", r"\bstate[- ]of[- ]the[- ]art\b|\bSOTA\b", "Needs current fair comparison to relevant methods."),
    ("generalize", r"\bgeneraliz(?:e|es|ed|ation)\b", "Needs held-out tasks, domains, datasets, embodiments, or theory."),
    ("significant", r"\bsignificant(?:ly)?\b", "Needs statistical test or exact measured improvement."),
    ("novel-first", r"\bnovel\b|\bfirst\b", "Needs related-work verification."),
    ("causal", r"\bcauses?\b|\bdue to\b|\bbecause of\b|\benables?\b", "Needs causal evidence, ablation, intervention, proof, or mechanism."),
]


def iter_files(paths: list[Path]) -> list[Path]:
    out: list[Path] = []
    for path in paths:
        if path.is_dir():
            for ext in TEXT_EXTS:
                out.extend(path.rglob(f"*{ext}"))
        elif path.is_file() and path.suffix.lower() in TEXT_EXTS:
            out.append(path)
    return sorted(set(out))


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def context(text: str, start: int, end: int, width: int) -> str:
    left = max(0, start - width)
    right = min(len(text), end + width)
    return " ".join(text[left:right].replace("\ufeff", "").split())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Draft files or directories")
    parser.add_argument("--context", type=int, default=100, help="Characters of context")
    args = parser.parse_args()

    files = iter_files([Path(p).expanduser().resolve() for p in args.paths])
    regexes = [(name, re.compile(pattern, re.IGNORECASE), note) for name, pattern, note in TERMS]
    total = 0

    for file in files:
        try:
            text = file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        hits = []
        for name, regex, note in regexes:
            for match in regex.finditer(text):
                hits.append((match.start(), line_number(text, match.start()), name, note, context(text, match.start(), match.end(), args.context)))
        if hits:
            print(f"\n## {file}")
            for _, line, name, note, snippet in sorted(hits):
                total += 1
                print(f"- line {line}: {name} -> {note}")
                print(f"  `{snippet}`")

    if total == 0:
        print("No configured high-risk scientific claim terms found.")
    else:
        print(f"\nTotal hits: {total}")
        print("Use hits as an evidence-scope checklist, not as automatic errors.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
