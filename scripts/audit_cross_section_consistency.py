#!/usr/bin/env python3
"""Audit claim traceability across abstract, contributions, evidence, and conclusions."""

from __future__ import annotations

import argparse

from paper_state_common import Issue, load_json, print_issue_report, state_file


WEAK_EVIDENCE = {"case_study", "qualitative_observation", "hypothesis", "missing"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", nargs="?", default=".", help="Project folder containing .paper-state")
    args = parser.parse_args()

    ledger = load_json(state_file(args.project, "claim_ledger.json"), {"claims": []})
    trace = load_json(state_file(args.project, "traceability_matrix.json"), {"mappings": [], "issues": []})
    graph = load_json(state_file(args.project, "argument_graph.json"), {"nodes": [], "edges": []})

    claim_ids = {str(c.get("id")) for c in ledger.get("claims", []) if isinstance(c, dict)}
    issues: list[Issue] = []

    for raw in trace.get("issues", []) or []:
        if isinstance(raw, dict):
            issues.append(
                Issue(
                    str(raw.get("severity", "major")),
                    str(raw.get("type", "traceability_issue")),
                    str(raw.get("location", "")),
                    str(raw.get("problem", "")),
                    str(raw.get("suggested_scope", "")),
                )
            )

    mapped_claims: set[str] = set()
    for mapping in trace.get("mappings", []) or []:
        if not isinstance(mapping, dict):
            issues.append(Issue("critical", "invalid_traceability_mapping", "traceability_matrix", "Mapping entry must be an object."))
            continue
        mid = str(mapping.get("id", "<missing-mapping-id>"))
        cid = str(mapping.get("claim_id", "")).strip()
        status = str(mapping.get("status", ""))
        evidence = mapping.get("evidence", []) or []
        evidence_strength = str(mapping.get("evidence_strength", ""))
        mapped_claims.add(cid)

        if cid not in claim_ids:
            issues.append(Issue("critical", "unknown_claim_id", mid, f"Mapping references unknown claim id `{cid}`."))
        if status in {"missing", "escalated"}:
            issues.append(Issue("critical", f"traceability_{status}", mid, f"Mapping for claim `{cid}` has status `{status}`."))
        if mapping.get("abstract") and not evidence and status != "supported":
            issues.append(
                Issue(
                    "critical",
                    "abstract_claim_without_support",
                    mid,
                    f"Abstract mapping for claim `{cid}` lacks evidence.",
                    "Add theorem/result/source support or remove/downgrade the abstract sentence.",
                )
            )
        if mapping.get("intro_contribution") and not evidence:
            issues.append(Issue("major", "contribution_without_validation", mid, f"Contribution for claim `{cid}` lacks mapped evidence."))
        if mapping.get("conclusion") and evidence_strength in WEAK_EVIDENCE:
            issues.append(
                Issue(
                    "major",
                    "conclusion_may_escalate_evidence",
                    mid,
                    f"Conclusion maps to weak evidence strength `{evidence_strength}`.",
                    "Use scoped wording such as illustrates, suggests, or is consistent with.",
                )
            )

    for claim in ledger.get("claims", []) or []:
        if not isinstance(claim, dict) or claim.get("status") == "deprecated":
            continue
        cid = str(claim.get("id", "")).strip()
        if cid and cid not in mapped_claims:
            issues.append(Issue("major", "claim_missing_from_traceability", f"claim_ledger:{cid}", "Active claim has no traceability mapping."))

    experiment_nodes = [n for n in graph.get("nodes", []) or [] if isinstance(n, dict) and n.get("type") == "experiment"]
    for node in experiment_nodes:
        node_id = str(node.get("id", "<experiment>"))
        node_claims = node.get("claim_ids", []) or []
        if not node_claims:
            issues.append(Issue("major", "orphan_experiment_node", f"argument_graph:{node_id}", "Experiment node supports no claim id."))

    return print_issue_report("Cross-Section Consistency Audit", issues)


if __name__ == "__main__":
    raise SystemExit(main())
