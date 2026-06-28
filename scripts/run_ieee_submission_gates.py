#!/usr/bin/env python3
"""Run strict IEEE/control/CS submission gates as a single audit pipeline."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def project_root(path_arg: str) -> Path:
    path = Path(path_arg).expanduser().resolve()
    return path.parent if path.is_file() else path


def run_gate(name: str, script: str, args: list[str]) -> tuple[str, int]:
    command = [sys.executable, str(SCRIPT_DIR / script), *args]
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
    print(f"\n===== {name} =====")
    print("$ " + " ".join(command))
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print("\nSTDERR:")
        print(result.stderr.rstrip())
    status = "PASS" if result.returncode == 0 else "BLOCKED"
    print(f"\n{name}: {status} (exit {result.returncode})")
    return name, result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", nargs="?", default=".", help="Paper project folder or draft file")
    parser.add_argument("--venue", default="ieee-control-journal", help="Target venue label for Paper State")
    parser.add_argument("--field", choices=["control", "robotics", "cs", "ai", "mixed"], default="control")
    parser.add_argument("--evidence-boundary", choices=["unknown", "simulation_only", "benchmark_only", "hardware", "mixed"], default="unknown")
    parser.add_argument("--fail-on", choices=["critical", "major", "minor", "note", "none"], default="major")
    args = parser.parse_args()

    target = Path(args.project).expanduser().resolve()
    root = project_root(args.project)
    if not root.exists():
        parser.error(f"project path does not exist: {target}")

    project_arg = str(root)
    target_arg = str(target)
    strict_profile = "ieee-control" if args.field in {"control", "robotics", "mixed"} else "ieee-cs"

    gates = [
        ("Paper State", "build_paper_state.py", [project_arg, "--venue", args.venue, "--domain", args.field, "--mode", "submission-audit"]),
        ("Claim Evidence", "audit_claim_evidence.py", [project_arg, "--strict", "--fail-on", args.fail_on]),
        ("Cross-Section Consistency", "audit_cross_section_consistency.py", [project_arg]),
        ("Scientific Claims", "audit_scientific_claims.py", [target_arg, "--strict", strict_profile, "--field", args.field, "--evidence-boundary", args.evidence_boundary, "--fail-on", args.fail_on]),
        ("Evidence Boundary", "audit_experiment_boundary.py", [target_arg, "--field", args.field, "--evidence-boundary", args.evidence_boundary, "--fail-on", args.fail_on]),
        ("Artifact Hygiene", "audit_artifact_hygiene.py", [target_arg, "--fail-on", args.fail_on]),
        ("Contribution Structure", "audit_contribution_structure.py", [target_arg, "--fail-on", args.fail_on]),
        ("Theory Assumption Scope", "audit_theory_assumption_scope.py", [target_arg, "--evidence-boundary", args.evidence_boundary, "--fail-on", args.fail_on]),
        ("Simulation Reporting", "audit_simulation_reporting.py", [target_arg, "--fail-on", args.fail_on]),
        ("Build Figure Cards", "build_figure_cards.py", [project_arg]),
        ("Figure Cards", "audit_figure_cards.py", [project_arg, "--fail-on", args.fail_on]),
        ("Caption Claims", "audit_caption_claims.py", [project_arg, "--fail-on", args.fail_on]),
        ("LaTeX Citations", "check_latex_citations.py", [project_arg]),
        ("Reference Maturity", "audit_reference_maturity.py", [project_arg, "--fail-on", args.fail_on]),
        ("IEEE Venue Shape", "audit_ieee_venue_shape.py", [project_arg, "--fail-on", args.fail_on]),
    ]

    results = [run_gate(name, script, gate_args) for name, script, gate_args in gates]
    blocked = [(name, code) for name, code in results if code != 0]

    print("\n===== Strict Submission Gate Summary =====")
    if blocked:
        print(f"BLOCKED: {len(blocked)} gate(s) failed.")
        for name, code in blocked:
            print(f"- {name}: exit {code}")
        print("\nDo not final-polish this manuscript as publication-ready until BLOCKED gates are repaired or explicitly marked unavailable with reason.")
        return 1

    print("PASS: all configured strict submission gates passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
