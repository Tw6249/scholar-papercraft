#!/usr/bin/env python3
"""Check LaTeX citation keys against local BibTeX files."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


CITE_RE = re.compile(
    r"\\(?:cite|citet|citep|citealp|citeauthor|citeyear|parencite|textcite|autocite|supercite)"
    r"(?:\s*\[[^\]]*\]){0,2}\s*\{([^}]*)\}",
    re.MULTILINE,
)
BIB_ENTRY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)", re.MULTILINE)
ADDBIB_RE = re.compile(r"\\addbibresource(?:\s*\[[^\]]*\])?\s*\{([^}]*)\}")
BIBLIOGRAPHY_RE = re.compile(r"\\bibliography\s*\{([^}]*)\}")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def find_tex_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root] if root.suffix.lower() == ".tex" else []
    return sorted(root.rglob("*.tex"))


def extract_cites(tex_files: list[Path]) -> dict[str, list[tuple[Path, int]]]:
    cites: dict[str, list[tuple[Path, int]]] = {}
    for tex in tex_files:
        text = tex.read_text(encoding="utf-8", errors="ignore")
        for match in CITE_RE.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            for key in match.group(1).split(","):
                key = key.strip()
                if key:
                    cites.setdefault(key, []).append((tex, line))
    return cites


def bib_paths_from_tex(tex_files: list[Path], root: Path) -> set[Path]:
    paths: set[Path] = set()
    for tex in tex_files:
        text = tex.read_text(encoding="utf-8", errors="ignore")
        for match in ADDBIB_RE.finditer(text):
            raw = match.group(1).strip()
            paths.add((tex.parent / raw).resolve())
        for match in BIBLIOGRAPHY_RE.finditer(text):
            for raw in match.group(1).split(","):
                raw = raw.strip()
                if not raw:
                    continue
                if not raw.lower().endswith(".bib"):
                    raw += ".bib"
                paths.add((tex.parent / raw).resolve())
    if root.is_dir():
        paths.update(p.resolve() for p in root.rglob("*.bib"))
    return paths


def extract_bib_keys(bib_files: set[Path]) -> dict[str, Path]:
    keys: dict[str, Path] = {}
    for bib in sorted(bib_files):
        if not bib.exists():
            continue
        text = bib.read_text(encoding="utf-8", errors="ignore")
        for match in BIB_ENTRY_RE.finditer(text):
            keys.setdefault(match.group(1).strip(), bib)
    return keys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", nargs="?", default=".", help="LaTeX project folder or .tex file")
    parser.add_argument("--unused", action="store_true", help="Also report bib entries not cited")
    args = parser.parse_args()

    root = Path(args.project).expanduser().resolve()
    tex_files = find_tex_files(root)
    if not tex_files:
        print("No .tex files found.")
        return 1

    cites = extract_cites(tex_files)
    bib_files = bib_paths_from_tex(tex_files, root if root.is_dir() else root.parent)
    bib_keys = extract_bib_keys(bib_files)
    missing = sorted(k for k in cites if k not in bib_keys)

    print(f"TeX files: {len(tex_files)}")
    print(f"Bib files found: {sum(1 for p in bib_files if p.exists())}")
    print(f"Citation keys used: {len(cites)}")
    print(f"Bib keys found: {len(bib_keys)}")

    if missing:
        print("\n## Missing citation keys")
        for key in missing:
            locs = ", ".join(f"{p.name}:{line}" for p, line in cites[key][:5])
            print(f"- `{key}` used at {locs}")
    else:
        print("\nNo missing citation keys found.")

    if args.unused:
        unused = sorted(k for k in bib_keys if k not in cites)
        print(f"\nUnused bib keys: {len(unused)}")
        for key in unused[:100]:
            print(f"- `{key}` in {bib_keys[key].name}")

    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
