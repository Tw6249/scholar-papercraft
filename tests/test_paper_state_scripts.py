from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run_script(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class PaperStateScriptTests(unittest.TestCase):
    def test_build_paper_state_creates_core_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "draft.tex").write_text("Abstract text.", encoding="utf-8")
            result = run_script("build_paper_state.py", str(project), "--venue", "T-RO", "--domain", "robotics")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            state = project / ".paper-state"
            self.assertTrue((state / "project.yaml").exists())
            self.assertTrue((state / "claim_ledger.json").exists())
            material_map = json.loads((state / "material_map.json").read_text(encoding="utf-8"))
            self.assertGreaterEqual(len(material_map["materials"]), 1)

    def test_claim_evidence_flags_confirmed_claim_without_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            state = project / ".paper-state"
            state.mkdir()
            (state / "claim_ledger.json").write_text(
                json.dumps(
                    {
                        "claims": [
                            {
                                "id": "C1",
                                "claim": "The controller guarantees safety.",
                                "strength": "theorem",
                                "status": "confirmed",
                                "scope": [],
                                "evidence": [],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            result = run_script("audit_claim_evidence.py", str(project))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("strong_claim_without_evidence", result.stdout)

    def test_traceability_builder_marks_missing_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            state = project / ".paper-state"
            state.mkdir()
            (state / "claim_ledger.json").write_text(
                json.dumps({"claims": [{"id": "C1", "claim": "A claim.", "strength": "missing", "status": "missing"}]}),
                encoding="utf-8",
            )
            result = run_script("build_traceability_matrix.py", str(project))
            self.assertNotEqual(result.returncode, 0)
            matrix = json.loads((state / "traceability_matrix.json").read_text(encoding="utf-8"))
            self.assertEqual(matrix["mappings"][0]["status"], "missing")


if __name__ == "__main__":
    unittest.main()
