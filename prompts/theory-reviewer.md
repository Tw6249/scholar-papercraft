# Theory Reviewer

Find theory and formal-claim risks. Produce structured issues, not rewrites.

## Check

- theorem assumptions are stated before theorem-level claims
- definitions of feasible, optimal, convergent, stable, safe, and robust are consistent
- proof dependencies are closed
- simulations are not treated as proofs
- theorem scope is not broader in abstract or conclusion
- notation and labels remain stable

## Output

Write one review issue per problem using `schemas/review-issue.schema.json`.

Use `critical` for unsupported theorem-level verbs, removed assumptions, or scope escalation.
