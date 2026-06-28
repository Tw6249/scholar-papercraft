#!/usr/bin/env python3
"""Build or update Figure Cards for a paper project."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


IGNORE_DIRS = {
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
FIGURE_EXTS = {".pdf", ".png", ".jpg", ".jpeg", ".svg", ".eps"}
VECTOR_EXTS = {".pdf", ".svg", ".eps"}
PLOT_SCRIPT_EXTS = {".py", ".m", ".ipynb", ".r", ".jl"}
RESULT_EXTS = {".csv", ".tsv", ".json", ".jsonl", ".xlsx", ".xls", ".mat", ".npy", ".npz"}


def iter_files(root: Path) -> Iterable[Path]:
    for current, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for filename in filenames:
            path = Path(current) / filename
            try:
                if path.is_file():
                    yield path
            except OSError:
                continue


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError:
        return ""
    return digest.hexdigest()


def compact_text(text: str) -> str:
    text = re.sub(r"%.*", "", text)
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?", "", text)
    text = text.replace("{", "").replace("}", "")
    return " ".join(text.split())


def command_args(source: str, command: str) -> list[str]:
    pattern = re.compile(rf"\\{re.escape(command)}\*?(?:\s*\[[^\]]*\])?\s*\{{")
    out: list[str] = []
    for match in pattern.finditer(source):
        start = match.end() - 1
        depth = 0
        for index in range(start, len(source)):
            char = source[index]
            if char == "{":
                depth += 1
                if depth == 1:
                    content_start = index + 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    out.append(source[content_start:index])
                    break
    return out


def figure_environments(source: str) -> list[str]:
    pattern = re.compile(r"\\begin\{figure\*?\}(.*?)\\end\{figure\*?\}", re.DOTALL)
    return [m.group(1) for m in pattern.finditer(source)]


def resolve_include(root: Path, tex_file: Path, include_path: str) -> Path | None:
    raw = include_path.strip()
    candidates = []
    base_paths = [tex_file.parent / raw, root / raw]
    for base in base_paths:
        candidates.append(base)
        if not base.suffix:
            for ext in FIGURE_EXTS:
                candidates.append(base.with_suffix(ext))
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return None


def scan_latex(root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for tex_file in sorted(root.rglob("*.tex")):
        if any(part in IGNORE_DIRS for part in tex_file.parts):
            continue
        source = read_text(tex_file)
        for env in figure_environments(source):
            labels = command_args(env, "label")
            captions = command_args(env, "caption")
            includes = command_args(env, "includegraphics")
            resolved = []
            for include in includes:
                path = resolve_include(root, tex_file, include)
                resolved.append(rel(path, root) if path else include.strip())
            records.append(
                {
                    "figure_id": f"Fig. {len(records) + 1}",
                    "tex_file": rel(tex_file, root),
                    "label": labels[0].strip() if labels else "",
                    "caption": compact_text(captions[0]) if captions else "",
                    "includegraphics": resolved,
                }
            )
    return records


def name_tokens(path_or_name: str) -> set[str]:
    stem = Path(path_or_name).stem.lower()
    return {token for token in re.split(r"[^a-z0-9]+", stem) if token and token not in {"fig", "figure", "plot"}}


def best_related(target: str, candidates: list[Path], root: Path) -> Path | None:
    target_tokens = name_tokens(target)
    best: tuple[int, str, Path] | None = None
    for candidate in candidates:
        candidate_rel = rel(candidate, root)
        candidate_tokens = name_tokens(candidate_rel)
        score = len(target_tokens & candidate_tokens)
        if score == 0:
            continue
        ranking = (score, candidate_rel, candidate)
        if best is None or ranking > best:
            best = ranking
    return best[2] if best else None


def export_entry(path: Path, root: Path) -> dict[str, Any]:
    ext = path.suffix.lower().lstrip(".")
    return {
        "path": rel(path, root),
        "format": ext,
        "vector": path.suffix.lower() in VECTOR_EXTS,
        "sha256": sha256_file(path),
    }


def data_source_entry(path: Path, root: Path) -> dict[str, Any]:
    return {
        "path": rel(path, root),
        "role": "metric_source",
        "raw_or_processed": "needs_author",
        "sha256": sha256_file(path),
    }


def default_checks() -> dict[str, str]:
    return {
        "figure_card_audit": "pending",
        "caption_claim_audit": "pending",
        "plot_code_audit": "pending",
        "export_audit": "pending",
        "data_comparison_audit": "pending",
        "latex_reference_audit": "pending",
    }


def make_card(
    *,
    figure_id: str,
    label: str,
    caption: str,
    exports: list[Path],
    root: Path,
    tex_record: dict[str, Any] | None,
    plot_scripts: list[Path],
    result_files: list[Path],
) -> dict[str, Any]:
    export_entries = [export_entry(path, root) for path in exports]
    primary_name = export_entries[0]["path"] if export_entries else label or figure_id
    plot_script = best_related(primary_name, plot_scripts, root)
    data_source = best_related(primary_name, result_files, root)
    data_sources = [data_source_entry(data_source, root)] if data_source else []
    plotting = {}
    if plot_script:
        plotting = {
            "script": rel(plot_script, root),
            "language": plot_script.suffix.lower().lstrip("."),
            "entrypoint": "",
            "sha256": sha256_file(plot_script),
        }
    return {
        "figure_id": figure_id,
        "label": label,
        "role": "needs_author",
        "status": "draft",
        "claim_ids": [],
        "argument_node_ids": [],
        "panels": [],
        "caption": caption,
        "data_contract": {
            "sources": data_sources,
            "needs_author": not bool(data_sources),
        },
        "metric_contract": {
            "name": "",
            "definition": "",
            "unit": "",
            "direction": "",
            "denominator": "",
        },
        "statistical_contract": {},
        "comparison_contract": {
            "ours": "",
            "baselines": [],
        },
        "visual_contract": {
            "plot_type": "needs_author",
            "encoding": {},
            "accessibility": {
                "colorblind_safe": "unchecked",
                "uses_markers_or_patterns": "unchecked",
                "grayscale_readable": "unchecked",
            },
        },
        "caption_contract": {
            "text": caption,
            "caption_claims": [],
            "must_include": [],
            "must_not_claim": [],
        },
        "plotting": plotting,
        "exports": export_entries,
        "latex_reference": {
            "label": label,
            "includegraphics": tex_record.get("includegraphics", []) if tex_record else [entry["path"] for entry in export_entries],
            "tex_file": tex_record.get("tex_file", "") if tex_record else "",
            "referenced_in_text": False,
            "argument_contexts": [],
        },
        "checks": default_checks(),
    }


def load_existing(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "figures": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"version": 1, "figures": []}
    if not isinstance(data, dict):
        return {"version": 1, "figures": []}
    data.setdefault("version", 1)
    data.setdefault("figures", [])
    return data


def empty(value: Any) -> bool:
    return value in (None, "", [], {}) or value == "needs_author"


def merge_missing(existing: Any, generated: Any) -> Any:
    if isinstance(existing, dict) and isinstance(generated, dict):
        merged = dict(existing)
        for key, value in generated.items():
            if key not in merged or empty(merged[key]):
                merged[key] = value
            else:
                merged[key] = merge_missing(merged[key], value)
        return merged
    if isinstance(existing, list):
        return generated if not existing else existing
    return generated if empty(existing) else existing


def card_key(card: dict[str, Any]) -> str:
    if card.get("label"):
        return f"label:{card['label']}"
    exports = card.get("exports") or []
    if exports and isinstance(exports[0], dict) and exports[0].get("path"):
        return f"export:{exports[0]['path']}"
    return f"figure:{card.get('figure_id', '')}"


def build_cards(root: Path, output: Path) -> tuple[dict[str, Any], list[str]]:
    figure_files = sorted(path for path in iter_files(root) if path.suffix.lower() in FIGURE_EXTS)
    plot_scripts = sorted(
        path
        for path in iter_files(root)
        if path.suffix.lower() in PLOT_SCRIPT_EXTS and re.search(r"(plot|fig|visual|draw|chart)", path.stem, re.I)
    )
    result_files = sorted(path for path in iter_files(root) if path.suffix.lower() in RESULT_EXTS)
    latex_records = scan_latex(root)
    used_exports: set[str] = set()
    generated: list[dict[str, Any]] = []

    for record in latex_records:
        exports = []
        for include in record["includegraphics"]:
            path = (root / include).resolve()
            if path.exists():
                exports.append(path)
                used_exports.add(rel(path, root))
        generated.append(
            make_card(
                figure_id=record["figure_id"],
                label=record["label"],
                caption=record["caption"],
                exports=exports,
                root=root,
                tex_record=record,
                plot_scripts=plot_scripts,
                result_files=result_files,
            )
        )

    for figure_file in figure_files:
        figure_rel = rel(figure_file, root)
        if figure_rel in used_exports:
            continue
        generated.append(
            make_card(
                figure_id=f"Fig. {len(generated) + 1}",
                label="",
                caption="",
                exports=[figure_file],
                root=root,
                tex_record=None,
                plot_scripts=plot_scripts,
                result_files=result_files,
            )
        )

    existing = load_existing(output)
    existing_by_key = {card_key(card): card for card in existing.get("figures", []) if isinstance(card, dict)}
    merged = []
    for card in generated:
        key = card_key(card)
        if key in existing_by_key:
            merged.append(merge_missing(existing_by_key.pop(key), card))
        else:
            merged.append(card)
    merged.extend(existing_by_key.values())
    data = {"version": 1, "figures": merged}

    warnings = []
    for card in merged:
        figure_id = card.get("figure_id", "<missing figure_id>")
        if card.get("caption") and not card.get("claim_ids"):
            warnings.append(f"{figure_id} has a caption but no claim_ids.")
        if not (card.get("data_contract") or {}).get("sources"):
            warnings.append(f"{figure_id} has no linked data source.")
        if card.get("exports") and not (card.get("plotting") or {}).get("script"):
            warnings.append(f"{figure_id} has exports but no linked plotting script.")
    return data, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", nargs="?", default=".", help="Paper project folder")
    parser.add_argument("--output", help="Output figure_cards.json path")
    parser.add_argument("--dry-run", action="store_true", help="Print summary without writing")
    args = parser.parse_args()

    root = Path(args.project).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        parser.error(f"project folder does not exist: {root}")

    output = Path(args.output).expanduser().resolve() if args.output else root / ".paper-state" / "figure_cards.json"
    data, warnings = build_cards(root, output)

    if not args.dry_run:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Created/updated: {output}")
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))

    print(f"Figures: {len(data.get('figures', []))}")
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"- {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
