#!/usr/bin/env python3
"""Render a Markdown report from Scholar Papercraft Paper State files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from paper_state_common import load_json, state_dir


def read_jsonl(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            rows.append({"parse_error": line})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", nargs="?", default=".", help="Project folder containing .paper-state")
    parser.add_argument("--out", help="Write report to Markdown file")
    args = parser.parse_args()

    state = state_dir(args.project)
    claims = load_json(state / "claim_ledger.json", {"claims": []}).get("claims", [])
    trace = load_json(state / "traceability_matrix.json", {"mappings": [], "issues": []})
    review_issues = read_jsonl(state / "review_issues.jsonl")
    revision_log = read_jsonl(state / "revision_log.jsonl")

    lines = ["# Scholar Papercraft Revision Report", ""]
    lines.append(f"Paper State: `{state}`")
    lines.append("")
    lines.append("## Claim Ledger")
    lines.append("")
    lines.append(f"- claims: {len(claims)}")
    status_counts: dict[str, int] = {}
    for claim in claims:
        if isinstance(claim, dict):
            status = str(claim.get("status", "unknown"))
            status_counts[status] = status_counts.get(status, 0) + 1
    for status, count in sorted(status_counts.items()):
        lines.append(f"- {status}: {count}")
    lines.append("")
    lines.append("## Traceability")
    lines.append("")
    mappings = trace.get("mappings", []) or []
    trace_issues = trace.get("issues", []) or []
    lines.append(f"- mappings: {len(mappings)}")
    lines.append(f"- traceability issues: {len(trace_issues)}")
    lines.append("")
    if trace_issues:
        lines.append("### Open Traceability Issues")
        lines.append("")
        for issue in trace_issues[:50]:
            lines.append(f"- [{issue.get('severity', 'issue')}] {issue.get('type', '')}: {issue.get('problem', '')}")
        lines.append("")
    lines.append("## Review Issues")
    lines.append("")
    lines.append(f"- issues: {len(review_issues)}")
    for issue in review_issues[:50]:
        if isinstance(issue, dict):
            lines.append(f"- [{issue.get('severity', 'issue')}] {issue.get('issue_id', '')}: {issue.get('problem', '')}")
    lines.append("")
    lines.append("## Revision Log")
    lines.append("")
    lines.append(f"- entries: {len(revision_log)}")
    for entry in revision_log[-25:]:
        if isinstance(entry, dict):
            lines.append(f"- {entry.get('timestamp', '')} `{entry.get('actor', '')}` {entry.get('location', '')}: {entry.get('change', '')}")
    lines.append("")

    report = "\n".join(lines)
    if args.out:
        out = Path(args.out).expanduser().resolve()
        out.write_text(report, encoding="utf-8")
        print(f"Wrote {out}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
