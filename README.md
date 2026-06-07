# Scholar Papercraft

`scholar-papercraft` is a Codex skill for evidence-grounded academic paper writing and revision.

It helps turn existing research materials, such as method notes, LaTeX drafts, experiment logs, figures, tables, code, reviewer comments, and `.bib` files, into polished paper text without inventing methods, results, claims, or citations.

## What it supports

- Paper drafting and polishing for robotics, control, AI, and computer science.
- Venue-aware writing for styles such as Science Robotics, T-RO, RA-L, ICRA/IROS, CDC/ACC, NeurIPS, ICML, and ICLR.
- Scientific claim auditing for words such as `stable`, `safe`, `robust`, `real-time`, `optimal`, `guarantee`, `state-of-the-art`, and `generalize`.
- Rebuttal and reviewer-response drafting from concrete evidence.
- Figure, table, caption, and plotting-code improvement.
- Reproducibility, AI-disclosure, citation-key, and reporting checks.

## Use

```text
Use $scholar-papercraft to polish this RA-L abstract without changing technical claims.
```

```text
Use $scholar-papercraft to audit this T-RO draft for unsupported stability, safety, robustness, and real-time claims.
```

```text
Use $scholar-papercraft to turn these experiment results and plotting code into a publication-quality figure and caption.
```

## Included checks

- `scripts/inventory_materials.py`: summarize likely paper materials in a project folder.
- `scripts/audit_scientific_claims.py`: flag high-risk scientific claim terms.
- `scripts/check_latex_citations.py`: check LaTeX citation keys against local `.bib` files.
- `scripts/audit_ai_phrases.py`: flag common AI-like academic phrasing.
- `scripts/title_to_bib.py`: experimental helper for recovering BibTeX candidates from paper titles. Treat its output as a draft and inspect the JSON report before adding entries to a paper.

Example:

```bash
python scripts/title_to_bib.py --file missing_titles.txt --out recovered.bib --report recovered_report.json
```

The core skill instructions are in [SKILL.md](SKILL.md).
