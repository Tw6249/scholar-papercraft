# Review response and rebuttal workflow

Use this reference for rebuttals, response letters, and revision plans.

## Inputs

Collect:

- Reviewer comments and scores
- Current manuscript
- Author notes on which criticisms are valid
- Additional experiments, tables, or figures
- Page/word limits and rebuttal format
- Constraints on new results or supplementary material

## Stage 1: Break down reviews

Parse each review into atomic issues:

| Issue ID | Reviewer | Type | Comment | Severity | Evidence needed |
| --- | --- | --- | --- | --- | --- |
| R2.3 | R2 | missing baseline | asks for comparison to X | high | experiment/table/citation |

Issue types:

- misunderstanding
- missing experiment
- missing baseline
- unclear method
- weak related work
- unsupported claim
- reproducibility concern
- writing/organization
- ethics/safety/limitation

## Stage 2: Decide response strategy

For each issue, choose one:

- `accept and fix`: reviewer is right; state the revision.
- `clarify`: manuscript was unclear; explain and revise text.
- `evidence`: answer with existing or new result.
- `scope`: explain why the request is outside scope, respectfully.
- `correct misconception`: cite manuscript evidence and improve wording.

Never dismiss a reviewer. Never write "the reviewer misunderstood" without taking responsibility for clarity.

## Stage 3: Draft responses

Use this structure:

```text
Thank you for pointing this out. [Direct answer.]
[Evidence: result, table, figure, theorem, citation, or new experiment.]
[Revision: exact place in paper and what will change.]
```

For a missing baseline:

```text
We added the requested comparison to [baseline] under the same [setting]. The new result shows [number], while our method achieves [number]. We will include this comparison in Table X and describe the setup in Sec. Y.
```

For a misunderstanding:

```text
The current manuscript did not make this distinction clear. Our method assumes [specific assumption], not [misread assumption]. We will revise Sec. X to define [term] before introducing Eq. Y.
```

For an out-of-scope request:

```text
We agree that [request] is important. The present work focuses on [scope] because [reason tied to contribution]. We will add this as a limitation and clarify that extending to [request] requires [missing ingredient].
```

## Stage 4: Build the response letter

Order:

1. Brief thanks and high-level revision summary.
2. Cross-reviewer major issues.
3. Reviewer-by-reviewer responses.
4. New experiments or manuscript changes.
5. Closing sentence.

Keep tone concise and evidence-heavy.

## Stage 5: Verify

- Every promise in the rebuttal has a manuscript change or clear plan.
- Every new number is traceable to data.
- The response does not exceed the word/page limit.
- The response does not reveal identity in double-blind review.
- The response does not make stronger claims than the manuscript.

## Rebuttal-specific de-AI editing

Remove:

- Over-apologizing.
- Generic gratitude repeated on every line.
- "We believe" when evidence can speak.
- Long background explanations that do not answer the issue.

Prefer:

- "We added..."
- "We clarified..."
- "The new experiment shows..."
- "We will revise Sec. X..."
