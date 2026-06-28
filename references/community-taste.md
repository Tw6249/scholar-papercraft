# Community Taste Model

Use this reference when the user provides exemplar papers or asks for venue/field style, author voice, de-AI editing, or sample-guided rewriting.

The goal is not style cloning. The goal is field-appropriate argumentation while preserving facts and claim strength.

## What to Extract

From multiple exemplars or taste packs, extract:

- section moves
- sentence-length distribution
- active/passive tendency
- citation placement
- paragraph workload
- gap wording
- theorem-claim qualification
- proof interpretation style
- experiment-to-conclusion pattern
- transition density
- field-specific avoid-list
- reviewer-facing emphasis
- reusable rhetorical moves such as gap, claim qualification, figure interpretation, limitation, and related-work contrast patterns

Do not extract:

- facts
- citations
- definitions
- limitations
- assumptions
- result numbers
- distinctive consecutive phrases
- claims about the target paper

## Structured Profile

Store durable profiles in `.paper-state/style_profile.json`.

```json
{
  "corpus": {
    "venue": "Automatica",
    "num_papers": 5,
    "sections_analyzed": ["abstract", "introduction", "theory", "experiments"]
  },
  "abstract": {
    "median_sentence_words": 24,
    "typical_moves": ["problem", "specific limitation", "method", "theoretical property", "experimental scope"],
    "first_person_preference": "moderate",
    "citation_density": "none_or_low",
    "avoid": ["generic impact opening", "implementation inventory"]
  },
  "theorem_prose": {
    "assumptions_before_claim": true,
    "preferred_verbs": ["establish", "imply", "converge"],
    "scope_repetition": "explicit",
    "interpretation_after_proof": true
  },
  "experiments": {
    "paragraph_pattern": ["question", "comparison", "quantitative result", "mechanistic interpretation", "scope"]
  }
}
```

The current extractor may also add:

```json
{
  "language_modes": {
    "cold-dense": {"goal": "short, precise, evidence-forward"},
    "narrative-persuasive": {"goal": "reader path and paragraph momentum without hype"}
  },
  "rhetorical_moves": {
    "gap_sentence_patterns": [],
    "claim_qualification_patterns": [],
    "theorem_interpretation_patterns": [],
    "figure_interpretation_patterns": [],
    "experiment_takeaway_patterns": [],
    "limitation_phrasing_patterns": [],
    "related_work_contrast_patterns": [],
    "abstract_ending_patterns": []
  },
  "preferred_verbs": [],
  "avoid_phrases": [],
  "phrase_copying_risk_notes": []
}
```

These fields are a language-action library, not a phrase bank. Use them to infer what kind of sentence the community writes; do not copy exemplar wording.

## Taste Packs

Use `references/taste-packs/` as composable constraints:

```text
domain pack + venue pack + section goal
```

Example:

```text
control/cbf-safety.yaml
+ control/distributed-optimization.yaml
+ venues/automatica.yaml
+ theory section
```

Each pack should help answer:

- What does the reader already know?
- What must be defined?
- Which claims require theorem-level support?
- Which baselines or comparisons are expected?
- Which reviewer objections are common?
- Which terms are standard?
- Which marketing expressions are out of place?
- How are proofs and experiments typically organized?

## Style Risk Rules

Use `scripts/audit_style_risk.py` for contextual checks. It treats phrases as risk signals, not bans.

Examples:

```text
robust framework
high risk unless the disturbance set or tested perturbation is named

robust positive invariance
allowed as a control-theory term

Furthermore once in a section
not an issue

Furthermore / Moreover / Additionally every 200 words
formulaic transition risk
```

For language density and before/after regression checks, use:

```bash
python scripts/audit_language_density.py <draft-or-project>
python scripts/compare_revision_style.py <before> <after>
```

## Visible Output

When the user wants the profile, keep it operational:

```text
Compact Taste Profile
- Community assumptions:
- Section moves:
- Claim style:
- Citation style:
- Sentence rhythm:
- Avoid:
```

When the user only wants edited paper text, apply the profile silently and report only high-impact changes or risks.
