#!/usr/bin/env python3
"""Create a Scholar Papercraft .paper-state scaffold for a research project."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from paper_state_common import write_json


IGNORE_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "node_modules", ".paper-state"}


def classify(path: Path) -> tuple[str, str]:
    name = path.name.lower()
    ext = path.suffix.lower()
    if ext in {".tex", ".docx"}:
        return "draft", "factual_source"
    if ext == ".bib":
        return "citation", "citation_source"
    if ext in {".md", ".txt", ".rst"}:
        if any(k in name for k in ("style", "example", "sample", "exemplar")):
            return "style_example", "style_only"
        return "author_note", "factual_source"
    if ext in {".csv", ".tsv", ".json", ".jsonl", ".xlsx", ".xls", ".mat", ".npy", ".npz"}:
        return "table", "factual_source"
    if ext in {".png", ".jpg", ".jpeg", ".svg", ".eps", ".pdf"}:
        return "figure", "unverified"
    if ext in {".py", ".m", ".ipynb", ".r", ".jl"}:
        return "code", "factual_source"
    return "other", "unverified"


def inventory(root: Path, max_files: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    count = 0
    for current, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for filename in filenames:
            path = Path(current) / filename
            if not path.is_file():
                continue
            kind, factual_status = classify(path)
            rel = path.relative_to(root).as_posix()
            rows.append(
                {
                    "id": f"M{len(rows) + 1:03d}",
                    "path": rel,
                    "kind": kind,
                    "factual_status": factual_status,
                    "description": "",
                    "claim_ids": [],
                    "notes": "",
                }
            )
            count += 1
            if count >= max_files:
                return rows
    return rows


def write_if_missing(path: Path, text: str, force: bool) -> bool:
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def write_json_if_missing(path: Path, data: object, force: bool) -> bool:
    if path.exists() and not force:
        return False
    write_json(path, data)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", nargs="?", default=".", help="Research project folder")
    parser.add_argument("--title", default="", help="Working paper title")
    parser.add_argument("--venue", default="", help="Target venue")
    parser.add_argument("--domain", default="", help="Domain or community")
    parser.add_argument("--mode", default="diagnose-only", choices=["diagnose-only", "conservative-edit", "trim-and-sharpen", "structural-revision", "editorial-rebuild", "submission-audit"])
    parser.add_argument("--max-files", type=int, default=300, help="Maximum project files to index")
    parser.add_argument("--force", action="store_true", help="Overwrite existing state files")
    args = parser.parse_args()

    root = Path(args.project).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        parser.error(f"project folder does not exist: {root}")

    state = root / ".paper-state"
    state.mkdir(parents=True, exist_ok=True)

    project_yaml = f"""paper:
  title_working: "{args.title}"
  venue: "{args.venue}"
  domain: "{args.domain}"
  audience:
    primary: ""
    secondary: ""

central_proposition:
  text: ""
  status: "missing"

scope:
  included: []
  excluded: []

editing_mode: "{args.mode}"
"""

    created = []
    if write_if_missing(state / "project.yaml", project_yaml, args.force):
        created.append("project.yaml")
    if write_json_if_missing(state / "material_map.json", {"materials": inventory(root, args.max_files)}, args.force):
        created.append("material_map.json")
    templates = {
        "claim_ledger.json": {"claims": []},
        "argument_graph.json": {"nodes": [], "edges": []},
        "terminology.json": {"terms": []},
        "insight_cards.json": {"insights": []},
        "style_profile.json": {"corpus": {}, "sections": {}, "language_modes": {}, "rhetorical_moves": {}, "section_patterns": {}, "preferred_verbs": [], "avoid_phrases": [], "phrase_copying_risk_notes": [], "global_avoid": [], "fact_isolation_notes": []},
        "traceability_matrix.json": {"mappings": [], "issues": []},
    }
    for name, data in templates.items():
        if write_json_if_missing(state / name, data, args.force):
            created.append(name)
    for name in ("paragraph_contracts.jsonl", "review_issues.jsonl", "revision_log.jsonl"):
        if write_if_missing(state / name, "", args.force):
            created.append(name)

    print(f"Paper State: {state}")
    if created:
        print("Created or updated:")
        for name in created:
            print(f"- {name}")
    else:
        print("No files changed. Use --force to overwrite existing state files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
