# Paper State

Use this reference when a task spans a full paper, a long section, multiple revision passes, or any workflow where claims can drift.

Paper State is the shared intermediate representation for the paper. It prevents roles from passing unsupported claims through natural-language memory.

## Directory

```text
.paper-state/
  project.yaml
  material_map.json
  claim_ledger.json
  argument_graph.json
  terminology.json
  insight_cards.json
  style_profile.json
  paragraph_contracts.jsonl
  review_issues.jsonl
  traceability_matrix.json
  revision_log.jsonl
```

Create the scaffold with:

```bash
python scripts/build_paper_state.py <project>
```

## File Roles

### `project.yaml`

Stores paper identity, venue, domain, audience, editing mode, central proposition, scope, and excluded claims.

Use this file to decide whether a requested edit is in scope.

### `material_map.json`

Indexes source artifacts and classifies them as factual material, style example, citation source, experiment output, figure source, code, or author note.

Style examples must never enter the claim ledger as factual evidence.

### `claim_ledger.json`

Stores every important claim with:

- stable id
- text
- strength
- scope
- evidence ids
- allowed verbs
- forbidden expansions
- status

Recommended strengths:

```text
definition
assumption
theorem
certified
controlled_experiment
ablation
case_study
qualitative_observation
hypothesis
missing
```

Recommended statuses:

```text
confirmed
weak
missing
author_confirmed
deprecated
```

### `argument_graph.json`

Represents the paper's reader path as typed nodes and logical edges.

Recommended node types:

```text
problem
gap
insight
method
definition
theory
experiment
limitation
contribution
conclusion
```

Recommended edge relations:

```text
motivates
resolved_by
implemented_by
certified_by
tested_by
illustrated_by
qualifies
contrasts_with
depends_on
```

### `terminology.json`

Stores canonical terms, aliases, forbidden synonyms, definitions, and section-specific usage notes.

Use it to prevent synonym cycling and field-inaccurate substitutions.

### `insight_cards.json`

Stores author-supplied or evidence-supported insights. These cards are the only safe source for mechanism explanations that are not already explicit in theorem/proof/experiment artifacts.

Mechanism status:

```text
CONFIRMED_MECHANISM
PLAUSIBLE_HYPOTHESIS
AUTHOR_INSIGHT_NEEDED
```

If the manuscript needs a mechanism but the evidence does not support it, ask the author a high-leverage question instead of inventing the bridge.

### `style_profile.json`

Stores community and venue taste distilled from multiple examples or selected packs.

A profile may guide section moves, sentence rhythm, citation placement, proof interpretation, experiment framing, and avoid-lists. It must not change claims.

### `paragraph_contracts.jsonl`

One JSON object per paragraph. Each contract licenses what the writer may include.

The Scientific Writer may write only inside the current contract.

### `review_issues.jsonl`

One structured issue per line from theory, experiment, community, venue, or integrity review.

Reviewers should produce issues, not free-form rewrites.

### `traceability_matrix.json`

Maps abstract sentences, contribution bullets, method/theory claims, experiments, figures/tables, and conclusion claims.

Use this to catch unsupported abstract claims, orphan experiments, contribution gaps, and conclusion escalation.

### `revision_log.jsonl`

Append-only log of targeted changes:

```json
{"timestamp":"2026-06-26T12:00:00Z","actor":"scientific_writer","location":"intro:P4","issue_id":"R2-017","claim_ids":["C4"],"change":"downgraded unsupported related-work contrast"}
```

## Minimal Paper State

For short tasks, do not create files unless useful. Keep a compact internal state:

```text
Material: ...
Licensed claims: ...
Missing evidence: ...
Style constraints: ...
Edit mode: ...
Verification needed: ...
```

## Invariants

- Every strong verb must be licensed by evidence strength.
- Every paragraph must have a primary role.
- Every abstract and contribution claim must map to later support.
- Every experiment must support a stated claim or be moved/removed.
- Every style transformation must preserve facts, numbers, citations, notation, and scope.
