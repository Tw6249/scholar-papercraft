#!/usr/bin/env python3
"""Find common AI-like phrasing patterns in academic drafts.

This is a lightweight heuristic scanner. A hit is not proof of AI writing; use
the output as an editing checklist.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


PATTERNS = [
    r"\bcrucial\b",
    r"\bpivotal\b",
    r"\btransformative\b",
    r"\bgroundbreaking\b",
    r"\bunderscores?\b",
    r"\bhighlights?\b",
    r"\bshowcases?\b",
    r"\bleverages?\b",
    r"\brobust and efficient\b",
    r"\bseamless\b",
    r"\bplays? a key role\b",
    r"\bit is worth noting that\b",
    r"\bin order to\b",
    r"\bmoreover\b",
    r"\bfurthermore\b",
    r"\badditionally\b",
    r"\bopens? new avenues\b",
    r"\bpaves? the way\b",
    r"\bstate-of-the-art\b",
    r"\bnot only\b.*\bbut also\b",
]


def iter_targets(paths: list[Path]) -> list[Path]:
    targets: list[Path] = []
    for path in paths:
        if path.is_dir():
            for ext in ("*.tex", "*.md", "*.txt"):
                targets.extend(path.rglob(ext))
        elif path.is_file():
            targets.append(path)
    return sorted(set(targets))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Draft files or folders")
    parser.add_argument("--context", type=int, default=90, help="Characters of context")
    args = parser.parse_args()

    targets = iter_targets([Path(p).expanduser().resolve() for p in args.paths])
    compiled = [(p, re.compile(p, re.IGNORECASE | re.DOTALL)) for p in PATTERNS]

    total = 0
    for target in targets:
        try:
            text = target.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        file_hits = []
        for pattern, regex in compiled:
            for match in regex.finditer(text):
                total += 1
                start = max(0, match.start() - args.context)
                end = min(len(text), match.end() + args.context)
                line = text.count("\n", 0, match.start()) + 1
                snippet = " ".join(text[start:end].split())
                file_hits.append((line, pattern, snippet))
        if file_hits:
            print(f"\n## {target}")
            for line, pattern, snippet in file_hits:
                print(f"- line {line}: `{pattern}` -> {snippet}")

    if total == 0:
        print("No configured AI-phrase patterns found.")
    else:
        print(f"\nTotal hits: {total}")
        print("Treat hits as prompts for revision, not as proof of authorship.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
