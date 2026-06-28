# Figure Layer

Use this reference when paper figures support claims, when captions make result claims, or when plotting data/scripts/exports are available. The goal is to treat each figure as a typed evidence interface, not as a visual asset.

Use `references/plotting-and-figures.md` for visual design, plotting defaults, and table/caption craft. Use this file for structured state, deterministic gates, stale detection, and caption claim control.

## Core model

Maintain figure evidence in:

```text
.paper-state/
  figure_cards.json
  figure_audit_report.json
  figure_dependency_lock.json
```

The first required state file is `.paper-state/figure_cards.json`. Each figure card should answer:

- What figure or panel is being discussed?
- Which claim IDs does it support?
- Which data sources, processing scripts, metrics, and statistical contracts produce the plotted values?
- Which visual encoding and exported artifacts represent the evidence?
- What does the caption claim, and what must it not claim?
- Is the figure used by the LaTeX argument, not merely included?

Prefer panel-level evidence mapping for multi-panel figures. A figure-level claim is acceptable only when the whole figure supports the same claim.

## Figure card fields

Use these fields as the default contract:

```json
{
  "figure_id": "Fig. 3",
  "label": "fig:main-results",
  "role": "main_result_bundle",
  "status": "draft",
  "claim_ids": ["C4"],
  "argument_node_ids": ["E2"],
  "panels": [],
  "data_contract": {
    "sources": [
      {
        "path": "results/ablation.csv",
        "role": "metric_source",
        "raw_or_processed": "processed",
        "sha256": ""
      }
    ]
  },
  "metric_contract": {
    "name": "infeasible QP count",
    "definition": "Number of infeasible solver calls per trial.",
    "unit": "count",
    "direction": "lower_is_better"
  },
  "statistical_contract": {
    "sample_unit": "trial",
    "n": 50,
    "aggregation": "mean",
    "uncertainty": "standard deviation",
    "statistical_test": null,
    "claim_allows_significance_language": false
  },
  "comparison_contract": {
    "ours": "proposed method",
    "baselines": ["baseline method"]
  },
  "visual_contract": {
    "plot_type": "grouped_bar",
    "encoding": {
      "x": "method",
      "y": "infeasible QP count",
      "error_bar": "standard deviation"
    },
    "accessibility": {
      "colorblind_safe": true,
      "uses_markers_or_patterns": true,
      "grayscale_readable": "unchecked"
    }
  },
  "caption_contract": {
    "text": "Ablation on infeasible QP count. Error bars show standard deviation over 50 trials.",
    "caption_claims": [
      {
        "claim": "The proposed method reduces infeasible QP instances in the tested setting.",
        "claim_id": "C4",
        "claim_type": "comparative",
        "allowed_strength": "ablation"
      }
    ],
    "must_include": ["metric", "scope", "number of trials", "error bar definition"],
    "must_not_claim": ["safety guarantee", "stability guarantee", "real-world deployment readiness"]
  },
  "exports": [
    {
      "path": "figures/fig3_ablation.pdf",
      "format": "pdf",
      "vector": true,
      "sha256": ""
    }
  ],
  "checks": {
    "figure_card_audit": "pending",
    "caption_claim_audit": "pending"
  }
}
```

## Status values

Use explicit lifecycle states:

```text
draft
needs_data
needs_metric_definition
needs_plot_script
needs_export
audited
approved
stale_data
stale_script
stale_caption
blocked
```

When data, plotting scripts, exported figures, captions, or linked claims change, move approved figures back to a stale or draft state before relying on them.

## Deterministic gates

Run the available gates from the skill folder:

```bash
python scripts/build_figure_cards.py <project>
python scripts/audit_figure_cards.py <project>
python scripts/audit_caption_claims.py <project>
```

For paper-level figure work, run at least:

```bash
python scripts/audit_figure_cards.py <project>
python scripts/audit_caption_claims.py <project>
```

Treat gate output as a claim-evidence checklist. Fix critical issues before final prose or captions. Major issues usually block strong wording, even when they do not block figure inclusion.

## Severity levels

Use deterministic issue counts rather than scores:

```text
critical
major
minor
note
```

Critical examples:

- Caption claims exist but no claim IDs are linked.
- Caption claims exist but no data source is recorded.
- A comparative claim has no baseline.
- A metric or metric direction is missing for a comparative claim.
- A caption claims safety, stability, optimality, or guarantees from non-formal evidence.

Major examples:

- Error bars are shown but uncertainty is undefined.
- Aggregate results omit n, trial count, or seed information.
- A caption says "significantly" without a statistical test or explicit non-statistical meaning.
- Causal verbs appear without ablation, intervention, proof, or author-approved mechanism.

Minor examples:

- Accessibility or grayscale readability is unchecked.
- Export hashes are missing.
- The figure role in the paper argument is not recorded.

## Caption claim control

Captions must stay inside the evidence strength recorded in the Figure Card.

- Do not claim `guarantees`, `safety`, `stability`, or `optimality` unless linked evidence is theorem-level, certified, or formal.
- Do not use `significant` or `significantly` unless `statistical_test` is recorded or the caption explicitly uses a non-statistical sense.
- Do not use causal language such as `causes`, `due to`, `because of`, or `enables` unless the card records ablation, intervention, proof, or a verified mechanism.
- Comparative claims require baseline, metric definition, metric direction, and scope.
- Real-time claims require latency or frequency, hardware, and workload.
- Robustness and generalization claims require perturbation/domain-shift or held-out task evidence.

Prefer scoped empirical language:

```text
reduced constraint violations in the tested simulation setting
```

over theorem-level language:

```text
guarantees safety
```

