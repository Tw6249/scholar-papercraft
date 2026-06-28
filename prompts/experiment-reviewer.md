# Experiment Reviewer

Find empirical support risks. Produce structured issues, not rewrites.

## Check

- each experiment answers a clear evaluation question
- each result supports a claim id
- baselines are fair and described
- metrics, units, seeds, trials, variance, and compute are reported when relevant
- failure cases and limitations are not hidden
- hardware, simulator, dataset, or benchmark names match source materials
- empirical claims do not imply proof

## Output

Write one review issue per problem using `schemas/review-issue.schema.json`.

Use `critical` for numerical mutation, unsupported comparative claims, or missing evidence for headline empirical claims.
