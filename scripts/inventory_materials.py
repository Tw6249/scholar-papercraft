#!/usr/bin/env python3
"""Inventory research-writing materials in a project folder.

The script prints a Markdown summary of likely drafts, notes, code, results,
figures, and citation files. It does not modify the project.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Iterable


IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
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
    ".idea",
    ".vscode",
}

TEXT_EXTS = {
    ".tex",
    ".bib",
    ".md",
    ".txt",
    ".rst",
    ".py",
    ".m",
    ".jl",
    ".r",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".csv",
    ".tsv",
}


def classify(path: Path) -> str:
    name = path.name.lower()
    ext = path.suffix.lower()
    stem = path.stem.lower()
    parts = {p.lower() for p in path.parts}

    if ext in {".tex", ".docx"} or ext in {".cls", ".sty"}:
        return "paper_draft_or_template"
    if ext == ".bib":
        return "citations"
    if ext in {".md", ".txt", ".rst"}:
        return "notes"
    if ext in {".csv", ".tsv", ".xlsx", ".xls", ".jsonl", ".mat", ".npy", ".npz", ".pkl"}:
        return "experiment_results"
    if ext in {".pdf", ".png", ".jpg", ".jpeg", ".svg", ".eps"}:
        if any(k in stem for k in ("fig", "plot", "result", "diagram", "overview")):
            return "figures"
        return "documents_or_images"
    if ext in {".py", ".m", ".ipynb", ".r", ".jl"}:
        if any(k in stem for k in ("plot", "fig", "visual", "draw", "chart")):
            return "plotting_code"
        return "source_code"
    if ext in {".yaml", ".yml", ".toml", ".ini", ".cfg"}:
        return "configs"
    if any(k in parts for k in ("results", "outputs", "logs", "runs", "experiments")):
        return "experiment_artifacts"
    return "other"


def iter_files(root: Path, max_files: int) -> Iterable[Path]:
    count = 0
    for current, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for filename in filenames:
            path = Path(current) / filename
            try:
                if path.is_file():
                    yield path
                    count += 1
                    if count >= max_files:
                        return
            except OSError:
                continue


def keyword_hits(path: Path) -> str:
    if path.suffix.lower() not in TEXT_EXTS:
        return ""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")[:20000].lower()
    except OSError:
        return ""
    keywords = []
    for key in (
        "abstract",
        "introduction",
        "contribution",
        "method",
        "experiment",
        "result",
        "baseline",
        "ablation",
        "theorem",
        "stability",
        "robot",
        "controller",
        "simulation",
        "hardware",
        "reviewer",
        "rebuttal",
    ):
        if key in text:
            keywords.append(key)
    return ", ".join(keywords[:8])


def format_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{num_bytes} B"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", nargs="?", default=".", help="Project folder to scan")
    parser.add_argument("--max-files", type=int, default=600, help="Maximum files to inspect")
    parser.add_argument("--top", type=int, default=120, help="Maximum rows to print")
    args = parser.parse_args()

    root = Path(args.project).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        parser.error(f"project folder does not exist: {root}")

    rows = []
    for path in iter_files(root, args.max_files):
        try:
            stat = path.stat()
        except OSError:
            continue
        category = classify(path)
        rel = path.relative_to(root)
        rows.append(
            {
                "category": category,
                "path": rel.as_posix(),
                "size": format_size(stat.st_size),
                "keywords": keyword_hits(path),
            }
        )

    priority = {
        "paper_draft_or_template": 0,
        "citations": 1,
        "notes": 2,
        "experiment_results": 3,
        "experiment_artifacts": 4,
        "plotting_code": 5,
        "figures": 6,
        "source_code": 7,
        "configs": 8,
        "documents_or_images": 9,
        "other": 10,
    }
    rows.sort(key=lambda r: (priority.get(r["category"], 99), r["path"]))

    print(f"# Material Inventory\n")
    print(f"Project: `{root}`")
    print(f"Files scanned: {len(rows)}")
    if len(rows) >= args.max_files:
        print(f"Scan stopped at --max-files={args.max_files}.")
    print()

    counts = {}
    for row in rows:
        counts[row["category"]] = counts.get(row["category"], 0) + 1
    print("## Counts\n")
    for category, count in sorted(counts.items(), key=lambda item: priority.get(item[0], 99)):
        print(f"- {category}: {count}")
    print()

    print("## High-signal files\n")
    print("| Category | Path | Size | Keyword hits |")
    print("| --- | --- | ---: | --- |")
    for row in rows[: args.top]:
        print(
            f"| {row['category']} | `{row['path']}` | {row['size']} | {row['keywords']} |"
        )

    print()
    print("## Next steps\n")
    print("- Read likely drafts, notes, result tables, and plotting code first.")
    print("- Build a claim-evidence ledger before drafting or polishing.")
    print("- Mark unsupported claims instead of filling missing facts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
