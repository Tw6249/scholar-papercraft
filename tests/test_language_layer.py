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


class LanguageLayerTests(unittest.TestCase):
    def test_language_density_flags_filler_empty_conclusion_weak_verb_and_nominalization(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            draft = Path(tmp) / "draft.md"
            draft.write_text(
                "It is important to note that these results demonstrate the effectiveness of the proposed method. "
                "Moreover, the realization of the improvement of performance leverages a comprehensive framework.",
                encoding="utf-8",
            )
            result = run_script("audit_language_density.py", str(draft), "--fail-on-major")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("empty_conclusion", result.stdout)
            self.assertIn("vague_evaluator_density", result.stdout)
            self.assertIn("weak_verb_density", result.stdout)
            self.assertIn("nominalization_density", result.stdout)

    def test_cold_dense_is_stricter_about_transition_density(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            draft = Path(tmp) / "draft.md"
            draft.write_text(
                "Moreover, the controller enforces the input constraint. "
                "Furthermore, the optimizer bounds the tracking error. "
                "Additionally, the ablation separates the reserve term from the baseline. "
                "Therefore, the result narrows the feasible operating region.",
                encoding="utf-8",
            )
            cold = run_script("audit_language_density.py", str(draft), "--mode", "cold-dense", "--fail-on-major")
            narrative = run_script("audit_language_density.py", str(draft), "--mode", "narrative-persuasive", "--fail-on-major")
            self.assertNotEqual(cold.returncode, 0)
            self.assertIn("decorative_transition_density", cold.stdout)
            self.assertEqual(narrative.returncode, 0, narrative.stdout + narrative.stderr)

    def test_compare_revision_style_flags_regressions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            before = Path(tmp) / "before.md"
            after = Path(tmp) / "after.md"
            before.write_text(
                "Our controller reduces tracking error by 12% on the tested task \\cite{a}; Fig.~\\ref{fig:a} reports the metric.",
                encoding="utf-8",
            )
            after.write_text(
                "It is important to note that our novel and robust controller guarantees safe performance and reduces tracking error by 13% on the tested task \\cite{b}; Fig.~\\ref{fig:b} reports the metric.",
                encoding="utf-8",
            )
            result = run_script("compare_revision_style.py", str(before), str(after), "--fail-on-major")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("numbers_changed", result.stdout)
            self.assertIn("citation_keys_changed", result.stdout)
            self.assertIn("claim_strength_escalation", result.stdout)

    def test_extract_style_profile_outputs_rhetorical_moves_without_fact_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            exemplar = Path(tmp) / "exemplar.md"
            exemplar.write_text(
                "Existing methods guarantee feasibility under centralized information, but they do not address bounded local authority. "
                "Under Assumption 1, Theorem 2 establishes recursive feasibility. "
                "Figure 3 shows that the ablation reduces infeasible instances. "
                "In contrast, our method differs in assumption rather than objective.",
                encoding="utf-8",
            )
            result = run_script("extract_style_profile.py", str(exemplar), "--venue", "Automatica", "--domain", "control")
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertIn("rhetorical_moves", data)
            self.assertIn("gap_sentence_patterns", data["rhetorical_moves"])
            self.assertNotIn("claims", data)
            self.assertNotIn("evidence", data)


if __name__ == "__main__":
    unittest.main()
