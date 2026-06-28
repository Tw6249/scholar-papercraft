# Paragraph Contracts

Use paragraph contracts before structural revision, editorial rebuilds, introduction repair, abstract repair, and long-section rewriting.

A paragraph contract defines what a paragraph is allowed to do. It converts "make this smoother" into an auditable reader-path plan.

## Contract Shape

```json
{
  "section": "Introduction",
  "paragraph": "I-P4",
  "role": "specific_gap",
  "reader_question": "Why is sum-preserving decomposition insufficient?",
  "licensed_claims": ["C2", "C3"],
  "required_evidence": ["PROP-4", "PROP-5"],
  "new_information": ["aggregate feasibility", "local capacity mismatch"],
  "must_not_include": ["algorithm details", "experimental numbers", "distributed eigenpair estimation"],
  "transition_from": "Existing distributed CBF decompositions preserve the global row.",
  "transition_to": "This motivates reserve rather than burden allocation.",
  "target_length_words": [90, 140],
  "status": "draft"
}
```

Store one JSON object per line in `.paper-state/paragraph_contracts.jsonl` for long tasks.

## Paragraph Roles

Use a small controlled vocabulary:

```text
background
problem_tension
specific_gap
key_insight
method_overview
definition_setup
theorem_consequence
experiment_question
result_interpretation
related_work_positioning
limitation_scope
transition
contribution_summary
```

Each paragraph should have one primary role. A paragraph may mention prior material, but it should not make multiple new claims unless the role requires it.

## Contract Rules

- `licensed_claims` must exist in the claim ledger.
- `required_evidence` must name source artifacts, theorem ids, figure/table ids, log paths, citation keys, or author notes.
- `must_not_include` should name common drift risks.
- `transition_from` and `transition_to` should be logical relations, not decorative transitions.
- `target_length_words` is a guide, not a mechanical constraint.
- Scientific Writer may not add a claim outside `licensed_claims`.
- If a contract needs a missing mechanism, set the relevant insight card to `AUTHOR_INSIGHT_NEEDED`.

## Repair Patterns

### Abstract

Use compressed argument moves:

```text
problem -> specific gap -> key idea -> evidence -> scoped conclusion
```

Avoid inventory moves:

```text
we propose A, B, C, and D
```

unless the inventory is the contribution.

### Introduction

Make each paragraph answer the next reader question:

```text
Why this setting?
What breaks?
Why is the break not handled by existing work?
What is the key distinction?
How does the method enforce it?
What evidence supports it?
What exactly are the contributions?
```

### Experiments

Every experiment paragraph should follow:

```text
question -> setup -> metric/baseline -> result -> claim supported -> scope
```

Do not write pure curve-description paragraphs.

### Related Work

Use field-map paragraphs first, then closest-work contrast. End with a diplomatic positioning sentence:

```text
In contrast, our method [specific difference] under [specific assumptions/settings].
```

## Contract Review

Before rewriting, check:

- Does the sequence form a reader path?
- Does each paragraph introduce only one new burden?
- Does every strong claim have evidence?
- Does any paragraph require author insight?
- Are notation and implementation details delayed until readers need them?
- Is the section's central proposition visible early enough?
