#!/usr/bin/env python3
"""Run lightweight Scholar Papercraft regression fixtures."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def run(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return proc.returncode, proc.stdout


def main() -> int:
    failures = 0
    for fixture in sorted(p for p in FIXTURES.iterdir() if p.is_dir()):
        print(f"# Fixture: {fixture.name}")
        style_code, style_out = run([sys.executable, str(SCRIPTS / "audit_style_risk.py"), str(fixture), "--fail-on-major"])
        language_code, language_out = run([sys.executable, str(SCRIPTS / "audit_language_density.py"), str(fixture), "--fail-on-major"])
        expected_style_fail = (fixture / "EXPECT_STYLE_FAIL").exists()
        expected_language_fail = (fixture / "EXPECT_LANGUAGE_FAIL").exists()
        if bool(style_code) != expected_style_fail:
            failures += 1
            print("STYLE CHECK MISMATCH")
            print(style_out)
        if bool(language_code) != expected_language_fail:
            failures += 1
            print("LANGUAGE CHECK MISMATCH")
            print(language_out)

        claim_ledger = fixture / ".paper-state" / "claim_ledger.json"
        if claim_ledger.exists():
            claim_code, claim_out = run([sys.executable, str(SCRIPTS / "audit_claim_evidence.py"), str(fixture)])
            expected_claim_fail = (fixture / "EXPECT_CLAIM_FAIL").exists()
            if bool(claim_code) != expected_claim_fail:
                failures += 1
                print("CLAIM CHECK MISMATCH")
                print(claim_out)

        before = fixture / "before.md"
        after = fixture / "after.md"
        if before.exists() and after.exists():
            compare_code, compare_out = run([sys.executable, str(SCRIPTS / "compare_revision_style.py"), str(before), str(after), "--fail-on-major"])
            expected_compare_fail = (fixture / "EXPECT_COMPARE_FAIL").exists()
            if bool(compare_code) != expected_compare_fail:
                failures += 1
                print("COMPARE CHECK MISMATCH")
                print(compare_out)

        if not any((fixture / marker).exists() for marker in ("EXPECT_STYLE_FAIL", "EXPECT_LANGUAGE_FAIL", "EXPECT_CLAIM_FAIL", "EXPECT_COMPARE_FAIL")):
            print("PASS")
    if failures:
        print(f"\nFailures: {failures}")
        return 1
    print("\nAll eval fixtures matched expected outcomes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
