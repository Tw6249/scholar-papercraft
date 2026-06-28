# Integrity Verifier

Run deterministic checks and report gate status.

## Check

- number and unit preservation
- citation-key resolution
- equation, figure, table, and label references
- claim ledger evidence coverage
- cross-section traceability
- terminology consistency
- style-example fact leakage
- contextual style risk
- language density and before/after language regressions
- LaTeX compile status when feasible

## Tools

Use relevant scripts:

```bash
python scripts/audit_claim_evidence.py <project>
python scripts/audit_cross_section_consistency.py <project>
python scripts/audit_style_risk.py <draft-or-project>
python scripts/audit_language_density.py <draft-or-project>
python scripts/compare_revision_style.py <before> <after>
python scripts/audit_scientific_claims.py <draft-or-project>
python scripts/audit_terminology.py <project>
python scripts/check_latex_citations.py <project>
```

## Output

Report:

```text
PASS / BLOCKED / WARN
critical issues:
major issues:
minor issues:
author input needed:
```

Do not add new manuscript content while verifying.
