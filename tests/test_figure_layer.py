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
        text=True,
        capture_output=True,
        encoding="utf-8",
    )


class FigureLayerTests(unittest.TestCase):
    def test_build_figure_cards_from_latex(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "figures").mkdir()
            (project / "results").mkdir()
            (project / "scripts").mkdir()
            (project / "figures" / "ablation.pdf").write_bytes(b"%PDF-1.4\n")
            (project / "results" / "ablation.csv").write_text("method,count\nours,2\nbase,5\n", encoding="utf-8")
            (project / "scripts" / "plot_ablation.py").write_text("print('plot')\n", encoding="utf-8")
            (project / "main.tex").write_text(
                r"""
\begin{figure}
\includegraphics[width=\linewidth]{figures/ablation.pdf}
\caption{Ablation on infeasible QP count. Error bars show standard deviation over 5 trials.}
\label{fig:ablation}
\end{figure}
""",
                encoding="utf-8",
            )

            result = run_script("build_figure_cards.py", str(project))
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            cards = json.loads((project / ".paper-state" / "figure_cards.json").read_text(encoding="utf-8"))
            self.assertEqual(len(cards["figures"]), 1)
            figure = cards["figures"][0]
            self.assertEqual(figure["label"], "fig:ablation")
            self.assertEqual(figure["exports"][0]["path"], "figures/ablation.pdf")
            self.assertEqual(figure["plotting"]["script"], "scripts/plot_ablation.py")
            self.assertEqual(figure["data_contract"]["sources"][0]["path"], "results/ablation.csv")
            self.assertIn("standard deviation", figure["caption_contract"]["text"])

    def test_audit_figure_cards_detects_missing_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            state = project / ".paper-state"
            state.mkdir()
            cards = {
                "version": 1,
                "figures": [
                    {
                        "figure_id": "Fig. 1",
                        "label": "fig:bad",
                        "status": "draft",
                        "claim_ids": [],
                        "panels": [],
                        "caption_contract": {
                            "text": "The method reduces failures.",
                            "caption_claims": [{"claim": "The method reduces failures.", "claim_type": "comparative"}],
                        },
                        "data_contract": {"sources": []},
                        "metric_contract": {"name": "", "definition": "", "direction": ""},
                        "comparison_contract": {"baselines": []},
                        "exports": [{"path": "figures/bad.pdf", "format": "pdf", "vector": True, "sha256": ""}],
                        "checks": {},
                    }
                ],
            }
            (state / "figure_cards.json").write_text(json.dumps(cards), encoding="utf-8")

            result = run_script("audit_figure_cards.py", str(project))
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("caption_claims exist but no claim_ids", result.stdout)
            self.assertIn("comparative claim has no baseline", result.stdout)

    def test_caption_audit_blocks_formal_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            state = project / ".paper-state"
            state.mkdir()
            cards = {
                "version": 1,
                "figures": [
                    {
                        "figure_id": "Fig. 2",
                        "label": "fig:safety",
                        "status": "draft",
                        "claim_ids": ["C1"],
                        "panels": [],
                        "caption_contract": {
                            "text": "The controller guarantees safety in cluttered scenes.",
                            "caption_claims": [
                                {
                                    "claim": "The controller guarantees safety.",
                                    "claim_id": "C1",
                                    "allowed_strength": "controlled_experiment",
                                }
                            ],
                        },
                        "data_contract": {"sources": [{"path": "results/safety.csv"}]},
                        "metric_contract": {"name": "violations", "definition": "constraint violations", "direction": "lower_is_better"},
                        "comparison_contract": {"baselines": ["baseline"]},
                        "exports": [],
                        "checks": {},
                    }
                ],
            }
            (state / "figure_cards.json").write_text(json.dumps(cards), encoding="utf-8")

            result = run_script("audit_caption_claims.py", str(project))
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("theorem-level", result.stdout)
            self.assertIn("guarantees", result.stdout)

    def test_caption_audit_can_fail_on_major(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            state = project / ".paper-state"
            state.mkdir()
            cards = {
                "version": 1,
                "figures": [
                    {
                        "figure_id": "Fig. 3",
                        "label": "fig:sig",
                        "status": "draft",
                        "claim_ids": ["C2"],
                        "panels": [],
                        "caption_contract": {
                            "text": "The proposed method significantly improves tracking error.",
                            "caption_claims": [
                                {
                                    "claim": "The proposed method significantly improves tracking error.",
                                    "claim_id": "C2",
                                    "claim_type": "comparative",
                                    "allowed_strength": "ablation",
                                }
                            ],
                        },
                        "data_contract": {"sources": [{"path": "results/tracking.csv"}]},
                        "metric_contract": {"name": "tracking error", "definition": "RMSE against reference trajectory", "direction": "lower_is_better"},
                        "comparison_contract": {"baselines": ["baseline"]},
                        "statistical_contract": {"aggregation": "mean"},
                        "exports": [],
                        "checks": {},
                    }
                ],
            }
            (state / "figure_cards.json").write_text(json.dumps(cards), encoding="utf-8")

            result = run_script("audit_caption_claims.py", str(project), "--fail-on", "major")
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("statistical_test", result.stdout)


if __name__ == "__main__":
    unittest.main()

