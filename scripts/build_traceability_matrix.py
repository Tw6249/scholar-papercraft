#!/usr/bin/env python3
"""Build or refresh a lightweight claim traceability matrix from Paper State."""

from __future__ import annotations

import argparse

from paper_state_common import load_json, state_file, write_json


def mapping_status(claim: dict[str, object]) -> str:
    evidence = claim.get("evidence", []) or []
    status = str(claim.get("status", ""))
    strength = str(claim.get("strength", ""))
    if status == "missing" or strength == "missing":
        return "missing"
    if evidence and status in {"confirmed", "author_confirmed"}:
        return "supported"
    if evidence:
        return "weak"
    return "missing"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", nargs="?", default=".", help="Project folder containing .paper-state")
    parser.add_argument("--stdout", action="store_true", help="Print JSON instead of writing .paper-state/traceability_matrix.json")
    args = parser.parse_args()

    ledger_path = state_file(args.project, "claim_ledger.json")
    ledger = load_json(ledger_path, {"claims": []})
    claims = ledger.get("claims", [])

    mappings = []
    issues = []
    for idx, claim in enumerate(claims, start=1):
        if not isinstance(claim, dict) or claim.get("status") == "deprecated":
            continue
        cid = str(claim.get("id", f"C{idx}"))
        evidence = claim.get("evidence", []) or []
        status = mapping_status(claim)
        mappings.append(
            {
                "id": f"T{idx:03d}",
                "claim_id": cid,
                "abstract": "",
                "intro_contribution": "",
                "method_or_theory": [],
                "evidence": evidence,
                "experiment": [],
                "conclusion": "",
                "evidence_strength": claim.get("strength", ""),
                "status": status,
            }
        )
        if status == "missing":
            issues.append(
                {
                    "issue_id": f"TRACE-{idx:03d}",
                    "severity": "critical",
                    "location": f"claim_ledger:{cid}",
                    "type": "claim_without_traceable_evidence",
                    "claim_id": cid,
                    "problem": "Claim has no traceable evidence mapping.",
                    "evidence_available": [],
                    "required_action": "support",
                    "suggested_scope": "",
                    "rewrite_permission": "author_input_required",
                    "status": "open",
                }
            )

    matrix = {"mappings": mappings, "issues": issues}
    if args.stdout:
        import json

        print(json.dumps(matrix, indent=2, ensure_ascii=False))
    else:
        out = state_file(args.project, "traceability_matrix.json")
        write_json(out, matrix)
        print(f"Wrote {out}")
        print(f"Mappings: {len(mappings)}")
        print(f"Issues: {len(issues)}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
