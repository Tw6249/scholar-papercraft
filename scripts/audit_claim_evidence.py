#!/usr/bin/env python3
"""Audit claim ledger entries for evidence, scope, and strength mismatches."""

from __future__ import annotations

import argparse

from paper_state_common import Issue, load_json, print_issue_report, should_fail, state_file


STRONG_STRENGTHS = {"theorem", "certified", "controlled_experiment", "ablation", "case_study"}
FORMAL_STRENGTHS = {"theorem", "certified"}
STRONG_VERBS = {"prove", "proves", "guarantee", "guarantees", "ensure", "ensures", "establish", "establishes", "optimal", "stable", "safe"}
CAUSAL_VERBS = {"cause", "causes", "because", "due", "enables", "enabled"}


def claim_location(claim: dict[str, object]) -> str:
    return str(claim.get("id", "<missing-id>"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", nargs="?", default=".", help="Project folder containing .paper-state")
    parser.add_argument("--strict", action="store_true", help="Treat an empty ledger as blocking for paper-level submission audit")
    parser.add_argument("--fail-on", choices=["critical", "major", "minor", "note", "none"], default="critical")
    args = parser.parse_args()

    ledger_path = state_file(args.project, "claim_ledger.json")
    issues: list[Issue] = []
    try:
        ledger = load_json(ledger_path)
    except FileNotFoundError:
        issues.append(
            Issue(
                "critical",
                "missing_claim_ledger",
                str(ledger_path),
                "Paper-level audit requires .paper-state/claim_ledger.json.",
                "Run build_paper_state.py and populate claim ids, evidence strength, scope, and sources before final polishing.",
            )
        )
        print_issue_report("Claim Evidence Audit", issues)
        return 1 if should_fail(issues, args.fail_on) else 0

    claims = ledger.get("claims", [])
    if not isinstance(claims, list):
        issues.append(Issue("critical", "invalid_claim_ledger", str(ledger_path), "`claims` must be a list."))
        print_issue_report("Claim Evidence Audit", issues)
        return 1 if should_fail(issues, args.fail_on) else 0

    if args.strict and not claims:
        issues.append(
            Issue(
                "critical",
                "empty_claim_ledger",
                str(ledger_path),
                "Strict submission audit cannot verify claim-evidence traceability from an empty ledger.",
                "Add abstract, contribution, theorem, experiment, figure, and conclusion claims before final polishing.",
            )
        )

    seen_ids: set[str] = set()
    for claim in claims:
        if not isinstance(claim, dict):
            issues.append(Issue("critical", "invalid_claim_entry", str(ledger_path), "Every claim entry must be an object."))
            continue
        cid = str(claim.get("id", "")).strip()
        location = claim_location(claim)
        if not cid:
            issues.append(Issue("critical", "missing_claim_id", location, "Claim entry has no stable id."))
        elif cid in seen_ids:
            issues.append(Issue("critical", "duplicate_claim_id", location, f"Claim id `{cid}` appears more than once."))
        seen_ids.add(cid)

        if claim.get("status") == "deprecated":
            continue

        text = str(claim.get("claim", "")).strip()
        strength = str(claim.get("strength", "")).strip()
        status = str(claim.get("status", "")).strip()
        evidence = claim.get("evidence", []) or []
        scope = claim.get("scope", []) or []
        allowed_verbs = {str(v).lower() for v in claim.get("allowed_verbs", []) or []}

        if not text:
            issues.append(Issue("critical", "missing_claim_text", location, "Claim has no text."))
        if not strength:
            issues.append(Issue("critical", "missing_claim_strength", location, "Claim has no evidence strength."))
        if not status:
            issues.append(Issue("critical", "missing_claim_status", location, "Claim has no status."))

        if strength in STRONG_STRENGTHS and not evidence:
            issues.append(
                Issue(
                    "critical",
                    "strong_claim_without_evidence",
                    location,
                    f"`{strength}` claim has no evidence links.",
                    "Add theorem/result/source ids or downgrade the claim.",
                )
            )
        if strength in FORMAL_STRENGTHS and not scope:
            issues.append(
                Issue(
                    "major",
                    "formal_claim_without_scope",
                    location,
                    f"`{strength}` claim lacks scope or assumptions.",
                    "List assumptions, sampling conditions, domains, or proof scope.",
                )
            )
        if status == "confirmed" and strength not in {"definition", "assumption"} and not evidence:
            issues.append(
                Issue(
                    "critical",
                    "confirmed_claim_without_evidence",
                    location,
                    "Confirmed claim has no evidence source.",
                    "Link it to a source artifact or change status to weak/missing.",
                )
            )
        if status == "missing" and strength != "missing":
            issues.append(Issue("major", "missing_claim_has_strength", location, "Missing claim should usually use strength `missing`."))
        if strength == "hypothesis" and allowed_verbs.intersection(STRONG_VERBS):
            issues.append(
                Issue(
                    "critical",
                    "hypothesis_with_strong_verbs",
                    location,
                    "Hypothesis lists theorem-level or guarantee verbs.",
                    "Use suggests, is consistent with, or mark AUTHOR_INSIGHT_NEEDED.",
                )
            )
        if strength in {"qualitative_observation", "case_study"} and allowed_verbs.intersection(CAUSAL_VERBS):
            issues.append(
                Issue(
                    "major",
                    "weak_evidence_with_causal_verbs",
                    location,
                    "Observation or case-study evidence should not license causal verbs.",
                    "Require ablation/proof/intervention or downgrade wording.",
                )
            )

    print_issue_report("Claim Evidence Audit", issues)
    return 1 if should_fail(issues, args.fail_on) else 0


if __name__ == "__main__":
    raise SystemExit(main())
