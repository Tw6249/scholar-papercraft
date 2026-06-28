from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


class StyleRiskTests(unittest.TestCase):
    def test_style_risk_flags_empty_conclusion_and_generic_robust(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            draft = Path(tmp) / "draft.md"
            draft.write_text(
                "These results demonstrate the effectiveness of the proposed method.\n\n"
                "Moreover, we provide a robust framework for challenging settings.",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "audit_style_risk.py"), str(draft), "--fail-on-major"],
                cwd=str(ROOT),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("empty_conclusion", result.stdout)
            self.assertIn("generic_robust", result.stdout)


if __name__ == "__main__":
    unittest.main()
