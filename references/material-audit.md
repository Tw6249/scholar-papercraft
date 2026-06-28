# Material audit and claim ledger

Use this reference when starting from notes, a repo, experiment folders, or a partial draft.

## Material inventory

Create a compact inventory before drafting:

| Category | Evidence to collect | Why it matters |
| --- | --- | --- |
| Core contribution | one-sentence claim, method name, novelty notes | anchors title, abstract, intro |
| Method | equations, pseudocode, architecture, controller, assumptions, code path | prevents invented mechanism details |
| Theory | theorem statements, assumptions, proof sketches, stability/convergence margins | prevents overclaiming |
| Experiments | raw logs, tables, plots, seeds, hardware/simulator, datasets, baselines | supports claims |
| Figures | source scripts, image files, captions, diagram notes | keeps visual story consistent |
| Citations | `.bib`, seed papers, related work notes | prevents citation hallucination |
| Venue | template, page limit, review criteria, anonymity rules | controls framing and format |

Run `scripts/inventory_materials.py <project>` when a folder is available.

For paper-level work, create a durable Paper State before drafting:

```bash
python scripts/build_paper_state.py <project>
```

Then store the inventory in `.paper-state/material_map.json`, not only in chat context.

## Claim-evidence ledger

Use this table internally, then expose only the useful parts to the user:

| ID | Claim | Evidence source | Status | Strength | Scope | Allowed verbs | Forbidden expansions | Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | What the paper proves/shows | file/table/figure/log | confirmed / weak / missing | theorem / experiment / hypothesis | assumptions/settings | proves, shows, suggests | general safety | overclaim / missing baseline / unsupported |

Status definitions:

- `confirmed`: directly supported by a source artifact or explicit author statement.
- `weak`: plausible, but the source does not fully support the strength of the wording.
- `missing`: needed for the paper, but not present in the materials.
- `author_confirmed`: directly supplied by the author but still may need citation, proof, or result support before publication.
- `deprecated`: no longer part of the active paper argument.

Strength definitions:

- `theorem`: formal proof or theorem statement under stated assumptions.
- `certified`: verified constraint satisfaction or certified property.
- `controlled_experiment`: fair empirical comparison with repeated trials or clear protocol.
- `ablation`: component or mechanism study.
- `case_study`: single scenario, demo, or illustrative run.
- `qualitative_observation`: observation without controlled isolation.
- `hypothesis`: plausible explanation that must be scoped.
- `missing`: claim needed but unsupported.

Risk labels:

- `overclaim`: wording is stronger than evidence.
- `scope`: claim does not specify assumptions, domains, or robot/task conditions.
- `baseline`: comparison lacks a necessary baseline or fair setting.
- `stat`: no variance, seed count, confidence interval, or significance details.
- `citation`: needs a verified citation.
- `repro`: implementation detail missing for reproduction.

## Evidence-grounded drafting rules

- Write from confirmed claims first.
- Downgrade weak claims using precise scope, not vague hedging.
- Replace "significantly improves" with measured evidence, such as "improves success rate by 12.4 points on X".
- Replace "robust" with the tested perturbation, uncertainty, or domain shift.
- Replace "real-time" with frequency, latency, hardware, and load.
- Replace "safe" with the formal safety property, constraint satisfaction rate, or failure boundary.
- Replace "generalizable" with the tested environments, embodiments, datasets, or held-out tasks.

## Missing-material questions

Ask only high-leverage questions. Good questions are specific and answerable:

- "Which result is the headline claim: success rate, tracking error, sample efficiency, or latency?"
- "Are these baselines run under the same simulator seed and compute budget?"
- "Should the introduction frame the contribution as a controller, a representation, a planning pipeline, or an experimental finding?"
- "Can we state stability/convergence, or should this remain an empirical claim?"

Avoid broad questions like "What should I write?" when the materials already support a draft.

## Consistency checks

Before returning prose:

- Match all numbers to source tables/logs.
- Use the same method name everywhere.
- Check figure captions do not claim results absent from the figure.
- Check abstract claims reappear in experiments or theory.
- Check limitations do not undermine the main contribution without explanation.
- Check self-citations and acknowledgments for anonymity if under double-blind review.

For long drafts, run:

```bash
python scripts/audit_claim_evidence.py <project>
python scripts/build_traceability_matrix.py <project>
python scripts/audit_cross_section_consistency.py <project>
```
