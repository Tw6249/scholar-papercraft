# Scholar Papercraft

`scholar-papercraft` is an evidence-grounded academic writing and editing skill for robotics, control, AI, and computer science papers.

It now treats a paper as a structured, auditable object rather than only prose. For substantial work it builds a `.paper-state/` with claim ledgers, paragraph contracts, argument graphs, author insight cards, taste profiles, review issues, and traceability matrices.

## Core Capabilities

- Material-driven drafting and revision from notes, LaTeX/Word drafts, equations, proofs, code, logs, tables, figures, reviewer comments, and `.bib` files.
- Structured Paper State for long or multi-pass paper work.
- Claim-evidence ledgers with evidence strength, scope, allowed verbs, and forbidden expansions.
- Paragraph contracts before structural rewriting.
- Community taste profiles and domain x venue packs without style-example fact leakage.
- Dual language modes: `cold-dense` and `narrative-persuasive`.
- Trim-and-sharpen language editing for shorter, sharper, less generic prose.
- Reviewer issue schemas and role-bounded review passes.
- Deterministic gates for claim support, cross-section consistency, contextual style risk, terminology, citations, and LaTeX references.
- Rebuttal, figure/table/caption, reproducibility, and AI-disclosure support.

## Typical Use

```text
Use $scholar-papercraft to diagnose this T-RO introduction and build paragraph contracts before rewriting.
```

```text
Use $scholar-papercraft to audit this abstract for unsupported safety, robustness, and conclusion-escalation claims.
```

```text
Use $scholar-papercraft to create a Paper State for this LaTeX project and generate a claim traceability matrix.
```

## Key Scripts

```bash
python scripts/build_paper_state.py <project>
python scripts/inventory_materials.py <project>
python scripts/audit_claim_evidence.py <project>
python scripts/build_traceability_matrix.py <project>
python scripts/audit_cross_section_consistency.py <project>
python scripts/audit_style_risk.py <draft-or-project>
python scripts/audit_language_density.py <draft-or-project>
python scripts/compare_revision_style.py <before> <after>
python scripts/audit_scientific_claims.py <draft-or-project>
python scripts/audit_terminology.py <project>
python scripts/check_latex_citations.py <project>
python scripts/render_revision_report.py <project>
```

`scripts/audit_ai_phrases.py` remains as a fast coarse scanner, but `scripts/audit_style_risk.py` is the preferred contextual linter.

## Validation

```bash
python -m unittest discover -s tests
python evals/run_eval.py
```

The core skill instructions are in [SKILL.md](SKILL.md).
