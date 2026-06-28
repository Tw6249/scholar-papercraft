# Agent Orchestration

Use this reference for multi-pass paper editing. The roles can be run by one model in separated passes; the point is permission control, not number of agents.

## Role Permissions

| Role | May Do | Must Not Do |
| --- | --- | --- |
| Evidence Curator | Inventory materials, build material map, claim ledger, numeric sources, citation sources, terminology seeds. | Rewrite manuscript prose, infer mechanisms, create missing evidence. |
| Community Taste Analyst | Build style profile from venue packs, field conventions, and exemplars. | Copy exemplar facts or distinctive phrases, introduce claims, modify technical scope. |
| Story Architect | Build central proposition, argument graph, section plan, paragraph contracts, missing-insight questions. | Write polished body text, invent mechanisms, strengthen claims. |
| Scientific Writer | Rewrite only inside paragraph contracts and licensed claims. | Add claims, alter numbers, change theorem scope, add unverified citations. |
| Review Board | Produce structured issues with severity, location, type, evidence, required action, and rewrite permission. | Whole-paper rewriting, subjective scoring, unsupported accusations. |
| Integrity Verifier | Check numbers, citations, terminology, LaTeX references, claim traceability, style-example leakage, quality gates. | Improve prose by adding new content or style-driven claims. |

## Mechanism Discipline

When a logic bridge is missing, classify it:

```text
CONFIRMED_MECHANISM
Evidence: proof, derivation, author note, ablation, controlled experiment, or directly cited source.

PLAUSIBLE_HYPOTHESIS
Evidence: consistent with observed result but not isolated or proven.

AUTHOR_INSIGHT_NEEDED
Evidence: absent. Ask the author instead of filling it in.
```

Safe wording examples:

```text
This behavior is consistent with multiplier equalization.
[AUTHOR INSIGHT NEEDED: Can the lower centralized gap be attributed to multiplier equalization, or is this only an empirical observation?]
```

Do not write:

```text
The improvement occurs because reserve transfer equalizes marginal burden costs.
```

unless the evidence directly supports that causal mechanism.

## Issue-Driven Loop

Use targeted loops instead of subjective scores or repeated whole-paper regeneration.

1. Evidence Curator freezes factual material.
2. Story Architect creates paragraph contracts.
3. Scientific Writer revises only contracted locations.
4. Review Board emits structured issues.
5. Integrity Verifier runs deterministic gates.
6. Writer fixes only issues with rewrite permission.
7. Stop when no critical issues remain or when a blocker needs author input.

Typical loop count is 1-3. Do not run 5-10 whole-paper rewrites unless the user explicitly requests broad iterative generation.

## Structured Issue Shape

```json
{
  "issue_id": "R2-017",
  "severity": "critical",
  "location": "Introduction paragraph 5",
  "type": "unsupported_gap_claim",
  "claim_id": "C4",
  "problem": "The text states that prior distributed CBF methods cannot handle bounded local authority, but the cited paper is only shown not to address this case.",
  "evidence_available": ["related_work_matrix:row2"],
  "required_action": "downgrade",
  "suggested_scope": "Existing methods do not explicitly enforce per-agent capacity consistency.",
  "rewrite_permission": "sentence_only"
}
```

Severity:

```text
critical: factual, citation, numerical, theorem, or claim-strength issue blocks delivery
major: argument or support issue that should be fixed before submission
minor: style or clarity issue that does not change correctness
note: optional observation
```

Rewrite permission:

```text
none
sentence_only
paragraph_only
section_plan
author_input_required
```

## Reviewer Lenses

Theory reviewer checks assumptions, definitions, proof dependencies, theorem verbs, and simulation-as-proof errors.

Experiment reviewer checks baselines, setup fairness, metrics, seeds/variance, failure cases, and claim mapping.

Community reviewer checks closest-work positioning, gap diplomacy, terminology, missing citations, and over-attack.

Venue editor checks abstract level, page budget, Figure 1 role, contribution bullets, and venue-specific reviewer scanning.

Integrity verifier checks source preservation, traceability, citations, references, LaTeX, terminology, and AI disclosure.

## Stop Conditions

Return `PASS` when:

- zero critical issues remain
- no numerical/citation/equation/theorem mutations are detected
- abstract and contribution claims are mapped
- unresolved minor issues are listed

Return `BLOCKED` when correctness depends on missing author evidence or a venue/source that cannot be verified.
