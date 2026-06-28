#!/usr/bin/env python3
"""Shared helpers for Scholar Papercraft scripts."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


TEXT_EXTS = {".tex", ".md", ".txt", ".rst"}
SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".paper-state",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    "target",
}

SEVERITY_RANK = {"critical": 0, "major": 1, "minor": 2, "note": 3}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


@dataclass
class Issue:
    severity: str
    issue_type: str
    location: str
    message: str
    suggestion: str = ""


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_project(path_arg: str | Path) -> Path:
    path = Path(path_arg).expanduser().resolve()
    if path.is_file():
        return path.parent
    return path


def state_dir(project: str | Path) -> Path:
    root = resolve_project(project)
    if root.name == ".paper-state":
        return root
    return root / ".paper-state"


def state_file(project: str | Path, name: str) -> Path:
    return state_dir(project) / name


def iter_text_files(paths: Iterable[Path]) -> list[Path]:
    out: list[Path] = []
    for path in paths:
        path = path.expanduser().resolve()
        if path.is_file() and path.suffix.lower() in TEXT_EXTS:
            out.append(path)
        elif path.is_dir():
            for child in path.rglob("*"):
                if any(part in SKIP_DIRS for part in child.parts):
                    continue
                if child.is_file() and child.suffix.lower() in TEXT_EXTS:
                    out.append(child)
    return sorted(set(out))


def count_words(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", text))


def split_sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text.replace("\n", " ")).strip()
    if not cleaned:
        return []
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\\])", cleaned)
    return [p.strip() for p in parts if p.strip()]


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def context(text: str, start: int, end: int, width: int = 120) -> str:
    left = max(0, start - width)
    right = min(len(text), end + width)
    return " ".join(text[left:right].replace("\ufeff", "").split())


def print_issue_report(title: str, issues: list[Issue]) -> int:
    print(f"# {title}")
    if not issues:
        print("\nPASS: no configured issues found.")
        return 0

    issues = sorted(issues, key=lambda item: (SEVERITY_RANK.get(item.severity, 99), item.location, item.issue_type))
    counts: dict[str, int] = {}
    for issue in issues:
        counts[issue.severity] = counts.get(issue.severity, 0) + 1
    print()
    for severity in ("critical", "major", "minor", "note"):
        if severity in counts:
            print(f"- {severity}: {counts[severity]}")
    print()
    for issue in issues:
        print(f"## {issue.severity.upper()}: {issue.issue_type}")
        print(f"Location: {issue.location}")
        print(issue.message)
        if issue.suggestion:
            print(f"Suggestion: {issue.suggestion}")
        print()
    return 1 if counts.get("critical", 0) else 0


def should_fail(issues: list[Issue], fail_on: str) -> bool:
    if fail_on == "none":
        return False
    threshold = SEVERITY_RANK[fail_on]
    return any(SEVERITY_RANK.get(issue.severity, 99) <= threshold for issue in issues)
