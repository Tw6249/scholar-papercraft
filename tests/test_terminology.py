from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


class TerminologyTests(unittest.TestCase):
    def test_terminology_flags_forbidden_synonym(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            state = project / ".paper-state"
            state.mkdir()
            (state / "terminology.json").write_text(
                json.dumps(
                    {
                        "terms": [
                            {
                                "canonical": "bounded-input feasibility",
                                "aliases": [],
                                "forbidden_synonyms": ["authority robustness"],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            (project / "draft.md").write_text("We call this authority robustness.", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "audit_terminology.py"), str(project)],
                cwd=str(ROOT),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("forbidden_synonym", result.stdout)


if __name__ == "__main__":
    unittest.main()
