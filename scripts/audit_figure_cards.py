#!/usr/bin/env python3
"""Audit Figure Cards for missing evidence contracts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


SEVERITY_RANK = {"critical": 0, "major": 1, "minor": 2, "note": 3}
COMPARATIVE_RE = re.compile(
    r"\b(reduce[sd]?|improve[sd]?|outperform[sd]?|better|worse|higher|lower|lowest|highest|best|degrade[sd]?|increase[sd]?|decrease[sd]?)\b",
    re.IGNORECASE,
)


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def nonempty(value: Any) -> bool:
    return value not in (None, "", [], {})


def inherited(scope: dict[str, Any], parent: dict[str, Any], key: str) -> Any:
    return scope.get(key) if nonempty(scope.get(key)) else parent.get(key, {})


def caption_contract(scope: dict[str, Any]) -> dict[str, Any]:
    value = scope.get("caption_contract")
    return value if isinstance(value, dict) else {}


def caption_text(scope: dict[str, Any]) -> str:
    return text(caption_contract(scope).get("text")) or text(scope.get("caption"))


def caption_claims(scope: dict[str, Any]) -> list[dict[str, Any]]:
    claims = caption_contract(scope).get("caption_claims", [])
    return claims if isinstance(claims, list) else []


def data_sources(scope: dict[str, Any], parent: dict[str, Any]) -> list[Any]:
    contract = inherited(scope, parent, "data_contract")
    sources = contract.get("sources", []) if isinstance(contract, dict) else []
    return sources if isinstance(sources, list) else []


def metric_contract(scope: dict[str, Any], parent: dict[str, Any]) -> dict[str, Any]:
    value = inherited(scope, parent, "metric_contract")
    return value if isinstance(value, dict) else {}


def statistical_contract(scope: dict[str, Any], parent: dict[str, Any]) -> dict[str, Any]:
    value = inherited(scope, parent, "statistical_contract")
    return value if isinstance(value, dict) else {}


def comparison_contract(scope: dict[str, Any], parent: dict[str, Any]) -> dict[str, Any]:
    value = inherited(scope, parent, "comparison_contract")
    return value if isinstance(value, dict) else {}


def visual_contract(scope: dict[str, Any], parent: dict[str, Any]) -> dict[str, Any]:
    value = inherited(scope, parent, "visual_contract")
    return value if isinstance(value, dict) else {}


def claim_ids(scope: dict[str, Any], parent: dict[str, Any]) -> list[str]:
    ids = scope.get("claim_ids")
    if isinstance(ids, list) and ids:
        return [str(item) for item in ids]
    parent_ids = parent.get("claim_ids", [])
    return [str(item) for item in parent_ids] if isinstance(parent_ids, list) else []


def is_comparative(scope: dict[str, Any]) -> bool:
    if text(scope.get("visual_claim_type")).lower() == "comparative":
        return True
    for claim in caption_claims(scope):
        if text(claim.get("claim_type")).lower() == "comparative":
            return True
        if COMPARATIVE_RE.search(text(claim.get("claim"))):
            return True
    return bool(COMPARATIVE_RE.search(caption_text(scope)))


def issue(severity: str, target: str, message: str, suggestion: str = "") -> dict[str, str]:
    out = {"severity": severity, "target": target, "message": message}
    if suggestion:
        out["suggestion"] = suggestion
    return out


def collect_claim_ledger_ids(path: Path) -> set[str]:
    data = load_json(path, None)
    ids: set[str] = set()

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if re.fullmatch(r"[A-Z]*C\d+[A-Z0-9_-]*", str(key)):
                    ids.add(str(key))
                if key in {"claim_id", "id"} and isinstance(item, str):
                    ids.add(item)
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    if data is not None:
        walk(data)
    return ids


def audit_scope(scope: dict[str, Any], parent: dict[str, Any], target: str, ledger_ids: set[str]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    claims = caption_claims(scope)
    ids = claim_ids(scope, parent)
    metric = metric_contract(scope, parent)
    stats = statistical_contract(scope, parent)
    comparison = comparison_contract(scope, parent)
    visual = visual_contract(scope, parent)
    caption = caption_text(scope)

    if claims and not ids:
        issues.append(issue("critical", target, "caption_claims exist but no claim_ids are linked."))
    if claims and not data_sources(scope, parent):
        issues.append(issue("critical", target, "caption_claims exist but no data source is recorded."))
    if claims and not (text(metric.get("name")) and text(metric.get("definition"))):
        issues.append(issue("critical", target, "caption_claims exist but metric name or definition is missing."))
    if is_comparative(scope) and not comparison.get("baselines"):
        issues.append(issue("critical", target, "comparative claim has no baseline in comparison_contract."))
    if is_comparative(scope) and not text(metric.get("direction")):
        issues.append(issue("critical", target, "comparative claim has no metric direction."))

    if caption and not ids:
        issues.append(issue("major", target, "caption exists but no claim_ids are linked."))

    encoding = visual.get("encoding", {}) if isinstance(visual, dict) else {}
    error_bar = isinstance(encoding, dict) and nonempty(encoding.get("error_bar"))
    caption_mentions_error = bool(re.search(r"\berror bars?\b|\bconfidence interval\b|\buncertainty\b", caption, re.I))
    if (error_bar or caption_mentions_error) and not text(stats.get("uncertainty")):
        issues.append(issue("major", target, "error bars or uncertainty are mentioned but statistical_contract.uncertainty is missing."))

    aggregate = any(nonempty(stats.get(key)) for key in ("aggregation", "uncertainty", "confidence_level"))
    if aggregate and not any(nonempty(stats.get(key)) for key in ("n", "trials", "seeds")):
        issues.append(issue("major", target, "aggregate result records aggregation or uncertainty but omits n, trials, or seeds."))

    for claim_id in ids:
        if ledger_ids and claim_id not in ledger_ids:
            issues.append(issue("major", target, f"claim_id {claim_id} was not found in .paper-state/claim_ledger.json."))

    accessibility = visual.get("accessibility", {}) if isinstance(visual, dict) else {}
    if isinstance(accessibility, dict):
        if accessibility.get("colorblind_safe") in (None, "", "unchecked", False):
            issues.append(issue("minor", target, "colorblind accessibility is unchecked."))
        if accessibility.get("grayscale_readable") in (None, "", "unchecked", False):
            issues.append(issue("minor", target, "grayscale readability is unchecked."))
    else:
        issues.append(issue("minor", target, "visual accessibility contract is missing."))

    exports = scope.get("exports", parent.get("exports", []))
    if isinstance(exports, list):
        for export in exports:
            if isinstance(export, dict) and not export.get("sha256"):
                issues.append(issue("minor", target, f"export has no hash: {export.get('path', '<unknown>')}"))
    if not text(scope.get("role")) or text(scope.get("role")) == "needs_author":
        issues.append(issue("minor", target, "argument role is not recorded."))
    return issues


def audit_cards(data: dict[str, Any], ledger_ids: set[str]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    figures = data.get("figures", [])
    if not isinstance(figures, list):
        return [issue("critical", "figure_cards.json", "top-level figures field is not a list.")]

    seen: dict[str, int] = {}
    for index, figure in enumerate(figures, start=1):
        if not isinstance(figure, dict):
            issues.append(issue("critical", f"figure[{index}]", "figure entry is not an object."))
            continue
        target = text(figure.get("figure_id")) or f"figure[{index}]"
        if not text(figure.get("figure_id")):
            issues.append(issue("critical", target, "figure_id is missing."))
        seen[target] = seen.get(target, 0) + 1
        issues.extend(audit_scope(figure, figure, target, ledger_ids))

        panels = figure.get("panels", [])
        if not isinstance(panels, list):
            issues.append(issue("major", target, "panels field is not a list."))
            continue
        for panel_index, panel in enumerate(panels, start=1):
            if not isinstance(panel, dict):
                issues.append(issue("major", f"{target}/panel[{panel_index}]", "panel entry is not an object."))
                continue
            panel_target = text(panel.get("panel_id")) or f"{target}/panel[{panel_index}]"
            if not text(panel.get("role")):
                issues.append(issue("major", panel_target, "panel exists but has no panel-level role."))
            issues.extend(audit_scope(panel, figure, panel_target, ledger_ids))

    for figure_id, count in seen.items():
        if count > 1:
            issues.append(issue("critical", figure_id, f"duplicate figure_id appears {count} times."))
    return sorted(issues, key=lambda item: (SEVERITY_RANK[item["severity"]], item["target"], item["message"]))


def print_report(issues: list[dict[str, str]]) -> None:
    counts = {severity: 0 for severity in SEVERITY_RANK}
    for item in issues:
        counts[item["severity"]] += 1
    print("# Figure Card Audit")
    blocked = [item for item in issues if item["severity"] == "critical"]
    warnings = [item for item in issues if item["severity"] != "critical"]
    if not blocked:
        print()
        print("PASS:")
        print("- 0 critical issues.")
    else:
        print()
        print("BLOCKED:")
        for item in blocked:
            print(f"- {item['severity'].upper()}: {item['target']}: {item['message']}")
            if item.get("suggestion"):
                print(f"  Suggestion: {item['suggestion']}")
    if warnings:
        print()
        print("WARN:")
        for item in warnings:
            print(f"- {item['severity'].upper()}: {item['target']}: {item['message']}")
            if item.get("suggestion"):
                print(f"  Suggestion: {item['suggestion']}")


def should_fail(issues: list[dict[str, str]], fail_on: str) -> bool:
    if fail_on == "none":
        return False
    threshold = SEVERITY_RANK[fail_on]
    return any(SEVERITY_RANK[item["severity"]] <= threshold for item in issues)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", nargs="?", default=".", help="Paper project folder")
    parser.add_argument("--cards", help="Path to figure_cards.json")
    parser.add_argument("--json-output", help="Write a structured audit report")
    parser.add_argument("--fail-on", choices=["critical", "major", "minor", "note", "none"], default="critical")
    args = parser.parse_args()

    root = Path(args.project).expanduser().resolve()
    cards_path = Path(args.cards).expanduser().resolve() if args.cards else root / ".paper-state" / "figure_cards.json"
    data = load_json(cards_path, {"figures": []})
    ledger_ids = collect_claim_ledger_ids(root / ".paper-state" / "claim_ledger.json")
    issues = audit_cards(data, ledger_ids)
    print_report(issues)

    report = {
        "gate": "figure_card_audit",
        "cards": str(cards_path),
        "issue_counts": {severity: sum(1 for item in issues if item["severity"] == severity) for severity in SEVERITY_RANK},
        "issues": issues,
    }
    json_output = Path(args.json_output).expanduser().resolve() if args.json_output else root / ".paper-state" / "figure_audit_report.json"
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 1 if should_fail(issues, args.fail_on) else 0


if __name__ == "__main__":
    raise SystemExit(main())
