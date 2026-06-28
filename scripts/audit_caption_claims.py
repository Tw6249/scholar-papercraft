#!/usr/bin/env python3
"""Audit figure captions for overclaims against Figure Card evidence."""

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
FORMAL_TERMS_RE = re.compile(
    r"\b(guarantee[sd]?|ensures?|safe(?:ty)?|stabili[sz](?:e|es|ed|ing|ation)?|stable|optimal(?:ity)?)\b",
    re.IGNORECASE,
)
SIGNIFICANCE_RE = re.compile(r"\bsignificant(?:ly)?\b", re.IGNORECASE)
CAUSAL_RE = re.compile(r"\b(causes?|due to|because of|enables?)\b", re.IGNORECASE)
COMPARATIVE_RE = re.compile(
    r"\b(reduce[sd]?|improve[sd]?|outperform[sd]?|better|worse|higher|lower|lowest|highest|best|degrade[sd]?|increase[sd]?|decrease[sd]?)\b",
    re.IGNORECASE,
)
REAL_TIME_RE = re.compile(r"\breal[- ]time\b", re.IGNORECASE)
ROBUST_RE = re.compile(r"\brobust(?:ness)?\b", re.IGNORECASE)
GENERALIZE_RE = re.compile(r"\bgeneraliz(?:e|es|ed|ation)\b", re.IGNORECASE)


FORMAL_STRENGTHS = {
    "theorem",
    "proof",
    "formal",
    "certified",
    "certification",
    "safety_certificate",
    "stability_proof",
    "control_theory",
    "verified_constraint",
}
MECHANISM_STRENGTHS = FORMAL_STRENGTHS | {"ablation", "intervention", "mechanism", "controlled_experiment"}


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


def caption_claims(scope: dict[str, Any]) -> list[dict[str, Any]]:
    claims = caption_contract(scope).get("caption_claims", [])
    return claims if isinstance(claims, list) else []


def caption_text(scope: dict[str, Any]) -> str:
    contract = caption_contract(scope)
    parts = [text(contract.get("text")), text(scope.get("caption"))]
    for claim in caption_claims(scope):
        if isinstance(claim, dict):
            parts.append(text(claim.get("claim")))
    return " ".join(part for part in parts if part)


def contract(scope: dict[str, Any], parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = inherited(scope, parent, key)
    return value if isinstance(value, dict) else {}


def evidence_strengths(scope: dict[str, Any], parent: dict[str, Any]) -> set[str]:
    strengths = set()
    for source in (parent, scope):
        for key in ("evidence_strength", "allowed_strength"):
            if text(source.get(key)):
                strengths.add(text(source.get(key)).lower())
        for claim in caption_claims(source):
            if isinstance(claim, dict):
                for key in ("allowed_strength", "evidence_strength"):
                    if text(claim.get(key)):
                        strengths.add(text(claim.get(key)).lower())
    return strengths


def has_any_strength(strengths: set[str], allowed: set[str]) -> bool:
    return any(any(token in strength for token in allowed) for strength in strengths)


def issue(severity: str, target: str, message: str, suggestion: str = "") -> dict[str, str]:
    out = {"severity": severity, "target": target, "message": message}
    if suggestion:
        out["suggestion"] = suggestion
    return out


def audit_scope(scope: dict[str, Any], parent: dict[str, Any], target: str) -> list[dict[str, str]]:
    caption = caption_text(scope)
    if not caption:
        return []

    issues: list[dict[str, str]] = []
    strengths = evidence_strengths(scope, parent)
    metric = contract(scope, parent, "metric_contract")
    stats = contract(scope, parent, "statistical_contract")
    comparison = contract(scope, parent, "comparison_contract")

    formal_hits = sorted(set(match.group(0) for match in FORMAL_TERMS_RE.finditer(caption)), key=str.lower)
    if formal_hits and not has_any_strength(strengths, FORMAL_STRENGTHS):
        issues.append(
            issue(
                "critical",
                target,
                f"caption uses theorem-level term(s) {', '.join(formal_hits)} without formal/certified evidence.",
                "Replace with scoped empirical wording, e.g. 'reduced violations in the tested setting', or link theorem-level evidence.",
            )
        )

    if SIGNIFICANCE_RE.search(caption):
        allows = stats.get("claim_allows_significance_language") is True
        if not stats.get("statistical_test") and not allows:
            issues.append(
                issue(
                    "major",
                    target,
                    "caption uses significant/significantly without a recorded statistical_test.",
                    "Use exact measured change or add the statistical test and correction details.",
                )
            )

    causal_hits = sorted(set(match.group(0) for match in CAUSAL_RE.finditer(caption)), key=str.lower)
    if causal_hits and not has_any_strength(strengths, MECHANISM_STRENGTHS):
        issues.append(
            issue(
                "major",
                target,
                f"caption uses causal term(s) {', '.join(causal_hits)} without ablation, intervention, proof, or mechanism evidence.",
                "Use association language or record the mechanism/ablation evidence in caption_contract.",
            )
        )

    if COMPARATIVE_RE.search(caption):
        if not comparison.get("baselines"):
            issues.append(issue("major", target, "comparative caption language lacks comparison_contract.baselines."))
        if not (text(metric.get("name")) and text(metric.get("definition"))):
            issues.append(issue("major", target, "comparative caption language lacks metric name or definition."))
        if not text(metric.get("direction")):
            issues.append(issue("major", target, "comparative caption language lacks metric direction."))

    if REAL_TIME_RE.search(caption):
        metric_blob = " ".join(text(metric.get(key)) for key in ("name", "definition", "unit")).lower()
        if not any(token in metric_blob for token in ("latency", "frequency", "hz", "runtime", "time")):
            issues.append(issue("major", target, "real-time claim lacks latency/frequency metric details."))
        if not re.search(r"\b(cpu|gpu|hardware|processor|rtx|hz|ms)\b", caption, re.I):
            issues.append(issue("major", target, "real-time claim lacks hardware or workload scope in the caption."))

    if ROBUST_RE.search(caption) and not re.search(r"\b(perturb|domain shift|uncertainty|noise|disturbance|range)\b", caption, re.I):
        issues.append(issue("major", target, "robustness claim lacks perturbation, uncertainty, or domain-shift scope."))

    if GENERALIZE_RE.search(caption) and not re.search(r"\b(held[- ]out|unseen|test tasks?|domains?|datasets?)\b", caption, re.I):
        issues.append(issue("major", target, "generalization claim lacks held-out task/domain/dataset scope."))

    return issues


def audit_cards(data: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    figures = data.get("figures", [])
    if not isinstance(figures, list):
        return [issue("critical", "figure_cards.json", "top-level figures field is not a list.")]
    for index, figure in enumerate(figures, start=1):
        if not isinstance(figure, dict):
            issues.append(issue("critical", f"figure[{index}]", "figure entry is not an object."))
            continue
        target = text(figure.get("figure_id")) or f"figure[{index}]"
        issues.extend(audit_scope(figure, figure, target))
        panels = figure.get("panels", [])
        if isinstance(panels, list):
            for panel_index, panel in enumerate(panels, start=1):
                if isinstance(panel, dict):
                    panel_target = text(panel.get("panel_id")) or f"{target}/panel[{panel_index}]"
                    issues.extend(audit_scope(panel, figure, panel_target))
    return sorted(issues, key=lambda item: (SEVERITY_RANK[item["severity"]], item["target"], item["message"]))


def print_report(issues: list[dict[str, str]]) -> None:
    counts = {severity: 0 for severity in SEVERITY_RANK}
    for item in issues:
        counts[item["severity"]] += 1
    print("# Caption Claim Audit")
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
    parser.add_argument("--json-output", help="Write a structured caption audit report")
    parser.add_argument("--fail-on", choices=["critical", "major", "minor", "note", "none"], default="critical")
    args = parser.parse_args()

    root = Path(args.project).expanduser().resolve()
    cards_path = Path(args.cards).expanduser().resolve() if args.cards else root / ".paper-state" / "figure_cards.json"
    data = load_json(cards_path, {"figures": []})
    issues = audit_cards(data)
    print_report(issues)

    report = {
        "gate": "caption_claim_audit",
        "cards": str(cards_path),
        "issue_counts": {severity: sum(1 for item in issues if item["severity"] == severity) for severity in SEVERITY_RANK},
        "issues": issues,
    }
    json_output = Path(args.json_output).expanduser().resolve() if args.json_output else root / ".paper-state" / "caption_claim_audit_report.json"
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 1 if should_fail(issues, args.fail_on) else 0


if __name__ == "__main__":
    raise SystemExit(main())
