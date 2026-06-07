---
name: scholar-papercraft
description: Material-driven academic paper writing and editing for control science, robotics, AI, and computer science. Use when drafting or revising papers, abstracts, introductions, methods, experiments, related work, rebuttals, reviewer responses, LaTeX/Word prose, scientific language constraint auditing, de-AI/humanized academic text, figure/table captions, graphical abstracts, or plotting code from user-provided materials such as methods, notes, code, logs, tables, figures, experiments, and existing drafts, especially for Science Robotics, IEEE T-RO, IEEE RA-L, ICRA, IROS, CDC, NeurIPS, ICML, and ICLR-style technical writing. Emphasizes evidence-grounded writing and must not invent methods, results, citations, or claims.
---

# Write Polish Research Papers

## Core posture

Act as a senior research writing collaborator, not as an idea generator. Transform the author's provided materials into clear, publishable prose, figures, rebuttals, and plotting code. Do not create a paper from nothing.

Use this invariant throughout:

```text
claim -> evidence -> wording -> venue fit -> verification
```

If any link is missing, mark it explicitly instead of filling the gap.

## Non-negotiable rules

- Ground every technical claim in provided materials: draft text, notes, equations, code, logs, tables, plots, videos, or author feedback.
- Never invent methods, datasets, baselines, numerical results, ablations, citations, theorem assumptions, robot hardware specs, or implementation details.
- Mark missing facts as `[NEEDS AUTHOR INPUT: ...]`, `[VERIFY RESULT: ...]`, or `[CITATION NEEDED: ...]`.
- Preserve LaTeX commands, labels, equations, macros, citations, figure references, and table references unless the user asks for structural editing.
- Verify new citations through available bibliographic sources or the user's `.bib`; do not write BibTeX from memory.
- Keep technical meaning stable when polishing or de-AI editing. Do not make academic writing casual.
- Prefer precise verbs and concrete nouns over generic significance language.
- Apply scientific language constraints before final wording: claim strength, causal verbs, guarantees, novelty, robustness, safety, stability, and significance must match the evidence.
- Use the target venue's current author instructions when formatting, page limits, AI disclosure, anonymity, or submission rules matter. These rules change.

## Quick workflow

1. Identify the target task:
   - Full paper or section drafting
   - Polishing, translation polishing, or de-AI editing
   - Related work or citation repair
   - Rebuttal or response letter
   - Figure/table captions, graphical abstract, or plotting code improvement

2. Inventory the materials:
   - Read the user's supplied files and nearby project context.
   - If the user gives a project folder, run `scripts/inventory_materials.py <project>`.
   - Build a short material map: method facts, claimed contributions, experimental evidence, figures, code paths, missing facts.

3. Build a claim-evidence ledger:
   - Use `references/material-audit.md` for the ledger template.
   - Separate confirmed claims, plausible but unverified claims, and missing author decisions.
   - Ask at most 1-3 targeted questions only when the paper's core contribution, target venue, or evidence is ambiguous enough to change the writing.

4. Choose the workflow reference:
   - For paper sections and polishing, read `references/writing-workflows.md`.
   - For scientific language constraints, claim calibration, and forbidden overclaiming words, read `references/scientific-language-constraints.md`.
   - For Science Robotics, T-RO, RA-L, ICRA, control, or AI venue tone, read `references/venue-packs.md`; use `references/venue-style.md` only for broader prose style.
   - For experiment reporting and reproducibility, read `references/reproducibility-reporting.md`.
   - For AI-writing disclosure, review privacy, and ethics/limitations, read `references/ai-disclosure-ethics.md`.
   - For figures, captions, tables, and plotting code, read `references/plotting-and-figures.md`.
   - For rebuttals and reviewer responses, read `references/review-rebuttal.md`.
   - For provenance and external inspirations behind this skill, read `references/source-notes.md`.

5. Draft or revise:
   - Start from the strongest evidence, not from generic field background.
   - Make the main contribution visible early.
   - Tie each experiment to a claim.
   - Prefer a concrete draft with flagged uncertainties over a long list of questions.

6. Verify before delivery:
   - Check numerical consistency against the source materials.
   - Check all figure/table/equation references.
   - Check citations are either verified or clearly marked.
   - For LaTeX projects, run `scripts/check_latex_citations.py <project>` when feasible.
   - For claim-heavy drafts, run `scripts/audit_scientific_claims.py <draft-or-project>` when feasible.
   - For LaTeX, compile or at least inspect syntax when feasible.
   - For plotting code, run the script when data and environment are available.

## Material package checklist

When the user asks for a paper-level task, look for:

- Problem statement and target venue
- One-sentence contribution
- Method description, algorithm, controller, model, or architecture
- Assumptions, theorem statements, stability/convergence arguments, or constraints
- Experimental setup: hardware, simulator, datasets, baselines, metrics, seeds, compute, hyperparameters
- Results: raw logs, summary tables, plots, videos, statistical variation, failed or negative results
- Existing figures, captions, and table drafts
- Existing `.tex`, `.bib`, Word, Markdown, or notes
- Related work seed papers and papers the authors must cite
- Reviewer comments, if revising or rebutting

If the package is thin, produce an evidence-first outline and a missing-material checklist before drafting high-confidence prose.

## Output contracts

For drafting:

- Return publishable prose in the requested format: LaTeX, Markdown, Word-ready text, or plain text.
- Include a short "open facts" list only for facts that block correctness.
- Keep author-facing notes outside the paper text.

For polishing:

- Return the revised text first.
- Then list only high-impact edits: claim sharpening, structure changes, terminology fixes, tone changes, citation/result warnings.
- Preserve the user's technical intent even if the original wording is rough.

For scientific language auditing:

- Return risky phrases with the evidence problem and a replacement.
- Downgrade unsupported causal, novelty, optimality, stability, robustness, safety, significance, and generalization claims.
- Prefer precise scoped claims over vague hedging.

For de-AI editing:

- Remove formulaic AI patterns, inflated significance claims, vague overimportance language, repetitive transitions, and generic conclusions.
- Keep the register appropriate for T-RO, RA-L, ICRA, Science Robotics, or the user's chosen venue.
- Preserve author voice if the user provides a writing sample.

For rebuttal:

- Parse reviewer comments into atomic issues.
- For each issue, answer with evidence, planned revision, and a concise respectful response.
- Do not concede a flaw that is not supported by the paper or author materials.

For plotting code:

- Preserve data provenance and metric definitions.
- Improve readability, accessibility, vector export, LaTeX integration, and reproducibility.
- Save or patch scripts rather than only describing changes when code is available.

## Style defaults

- For robotics and control papers, foreground the system, assumptions, stability/safety constraints, real-world setup, and reproducibility.
- For AI/CS papers, foreground the task, model/algorithm, baselines, ablations, metrics, and failure modes.
- For Science Robotics-style writing, make the biological/physical/robotic significance legible to a broader technical audience without diluting mechanism and evidence.
- For IEEE T-RO and RA-L, favor dense, precise, technically complete prose with clean notation and traceable experiments.
- For ICRA/IROS, favor clear problem framing, method overview figures, strong empirical claims, and concise contribution bullets.

## Example invocations

- "Use this skill to rewrite my abstract for RA-L. Here are the method notes and result table."
- "Polish this T-RO introduction in LaTeX, but do not change the technical claims."
- "Turn these experiment logs and plot scripts into a publication-quality ablation figure and caption."
- "Write a rebuttal from these reviewer comments and our extra experiment results."
- "De-AI this Science Robotics significance paragraph while preserving the mechanism and evidence."
