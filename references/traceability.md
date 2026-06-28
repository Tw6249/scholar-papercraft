# Traceability and Quality Gates

Use this reference before finalizing abstracts, introductions, contribution bullets, related work, experiments, conclusions, and submission packages.

## Claim Traceability Matrix

The matrix maps claims across the paper:

```text
abstract sentence -> claim id -> intro contribution -> method/theory -> evidence -> conclusion
```

Store durable mappings in `.paper-state/traceability_matrix.json`.

Minimal entry:

```json
{
  "id": "T1",
  "claim_id": "C3",
  "abstract": "A2",
  "intro_contribution": "B2",
  "method_or_theory": ["Sec. IV", "Thm. 3"],
  "evidence": ["Fig. 3", "Table II"],
  "conclusion": "K2",
  "evidence_strength": "theorem",
  "status": "supported"
}
```

## Common Findings

```text
ABSTRACT CLAIM WITHOUT SUPPORT
An abstract sentence maps to a claim without theorem, experiment, cited source, or author-approved evidence.

ORPHAN EXPERIMENT
An experiment is reported but supports no stated contribution or claim.

CONTRIBUTION WITHOUT VALIDATION
A contribution bullet has no mapped theorem, figure, table, experiment, or citation.

CONCLUSION ESCALATION
A conclusion uses stronger language than the evidence permits.

STYLE FACT LEAKAGE
A fact appears only in a style example, not in project material.
```

## Related-Work Diplomacy

Use a positioning matrix when related work matters:

```text
Work | Problem | Assumptions | Guarantee | Input bounds | Local capacity | Relation
```

Allowed relation terms:

```text
extends
relaxes
specializes
combines
complements
differs in objective
differs in assumption
not directly comparable
addresses an orthogonal setting
```

Avoid unsupported attack verbs:

```text
fails to
cannot handle
ignores
is unsuitable
is flawed
```

Use attack verbs only when the cited source or an explicit proof supports them.

## Quality Gates

### Gate 0: Source Integrity

- No new numbers.
- No changed units.
- No new dataset, hardware, robot, simulator, baseline, or benchmark names.
- No unverified citation keys.
- No theorem assumption removed.
- No equation/label mutation unless authorized.

### Gate 1: Claim Integrity

- Every theorem-level verb maps to theorem/proof evidence.
- Every certified/safety/stability verb maps to formal evidence or is scoped as empirical.
- Every empirical comparative claim maps to a result.
- Every causal claim maps to proof, ablation, intervention, or author-approved insight.

### Gate 2: Cross-Section Consistency

- Abstract claims appear later.
- Contribution bullets are supported.
- Method names and notation are stable.
- Conclusion does not escalate evidence strength.
- Limitations do not contradict the headline claim without explanation.

### Gate 3: Argument Integrity

- Every paragraph has one primary role.
- Every major transition has a logical relation.
- Experiments are organized by evaluation question.
- Figures and tables have jobs in the argument.

### Gate 4: Style and Community Fit

- No excessive formulaic transitions.
- No unsupported importance language.
- Terminology matches the selected domain/venue packs.
- No single-paper phrase cloning.
- No style-example fact leakage.

### Gate 5: Technical Compilation

- LaTeX compiles when feasible.
- Citation keys resolve.
- Figure/table/equation references resolve.
- Algorithms and equations are unchanged unless authorized.
- Anonymity and AI disclosure constraints are checked when relevant.

## Gate Report Format

```text
PASS
0 critical
2 major resolved
7 minor remaining

BLOCKED
1 critical: abstract claim C8 lacks evidence
```

Use deterministic issue counts. Do not report arbitrary paper scores such as `92/100`.
