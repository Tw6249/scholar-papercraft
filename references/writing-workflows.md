# Writing and polishing workflows

Use this reference for drafting sections, polishing academic prose, translation polishing, and de-AI editing.

## Full paper workflow

1. Build the material inventory and claim ledger.
2. Confirm target venue and one-sentence contribution if absent.
3. Draft the paper skeleton:
   - Title candidates
   - Abstract
   - Introduction with contribution bullets
   - Related work structure
   - Method structure
   - Experiments mapped to claims
   - Limitations
4. Draft section by section, keeping author-facing uncertainty notes outside paper text.
5. Verify citations, numbers, figure references, and LaTeX syntax.

## Abstract

Use a five-move structure, adapted to the venue:

1. Problem and why it matters in the target domain.
2. Specific gap in prior work.
3. Proposed method/system/controller/model.
4. Evidence: tasks, robots, datasets, baselines, theory, or deployment.
5. Headline result or capability.

Rules:

- Do not open with generic field hype.
- Include numbers only when verified.
- Avoid "novel", "effective", "robust", and "significant" unless the sentence states evidence.
- For Science Robotics, make the capability and physical system legible.
- For T-RO/RA-L/ICRA, make the technical contribution and evidence explicit.

## Introduction

Recommended structure:

1. Concrete problem in robotics/control/AI.
2. Why existing approaches fail under the stated assumptions or setting.
3. Key insight.
4. Method overview.
5. Evidence summary.
6. Contribution bullets.

Contribution bullets should be specific and testable:

- Bad: "We propose a novel and robust framework."
- Good: "We introduce a contact-aware MPC policy that enforces friction-cone constraints during whole-body manipulation."

## Related work

Organize by technical relationship, not by a list of papers:

- Problem family
- Method family
- Closest competing approach
- Why the proposed work differs

Each paragraph should end with a positioning sentence:

```text
In contrast, our method [specific difference] under [specific assumptions/settings].
```

Citation rules:

- Use the user's `.bib` and seed papers first.
- Verify any new citation.
- If a citation cannot be verified, mark it with `[CITATION NEEDED: topic]`.

## Method

Write for reimplementation:

- Define inputs, outputs, state, action, constraints, and assumptions.
- Present the method in the order the system executes.
- Put notation before equations.
- Explain the role of each loss term, controller term, module, or planning stage.
- Tie design choices to failure modes or requirements.
- Use pseudocode when it clarifies sequence or dependency.

For control papers:

- State plant model, uncertainty, constraints, and sampling/update rates.
- Distinguish proved properties from empirical behavior.
- Do not imply stability, safety, or optimality unless supported.

For AI papers:

- State architecture, training objective, data, hyperparameters, inference procedure, and compute.
- Separate final method from ablations.

## Experiments

Each experiment should have:

```text
Question -> setup -> metrics -> baselines -> result -> claim supported
```

Write the first sentence of each experiment subsection as the claim being tested.

Include:

- Hardware/simulator/dataset
- Baselines and why they are fair
- Metrics and units
- Number of runs/seeds
- Variance or confidence where available
- Failure cases or boundary conditions

Avoid:

- "The results demonstrate superiority" without numbers.
- Combining multiple claims in one paragraph.
- Hiding setup details that determine fairness.

## Captions

Figure captions should stand alone:

1. What the figure shows.
2. How to read it.
3. Main takeaway, with numbers when verified.

Table captions should state metrics, directions, and scope:

```text
Higher is better for success rate; lower is better for tracking error.
```

## Polishing

Polish in this order:

1. Correct technical meaning.
2. Paragraph structure.
3. Sentence clarity.
4. Terminology consistency.
5. Tone and rhythm.
6. Grammar and formatting.

High-value edits:

- Put old/context information before new information.
- Keep subject and verb close.
- Put the main stress at the end of the sentence.
- Replace nominalizations with verbs when possible.
- Split paragraphs that make more than one point.
- Use the same term for the same concept.

## De-AI academic editing

Remove:

- Inflated significance language: "crucial", "pivotal", "transformative", "groundbreaking" unless evidence justifies it.
- Generic transitions: "Moreover", "Furthermore", "In addition" stacked mechanically.
- Vague verbs: "highlight", "underscore", "showcase", "leverage" when a precise verb exists.
- Formulaic endings: "This opens new avenues..."
- Repetitive three-part lists that do not reflect real structure.

Keep:

- Formal academic register.
- Domain terminology.
- Necessary hedging where evidence is limited.
- The author's argument and technical claims.

Do not over-humanize into casual prose. The goal is authored, precise, and field-appropriate writing.

## Chinese-to-English paper polishing

When polishing Chinese-authored English:

- Preserve technical terms already established in the field.
- Avoid literal translation of "based on", "aiming at", "according to" when English needs a stronger verb.
- Replace "this paper" with "we" only if the venue and author preference allow it.
- Watch article usage, countability, and prepositions.
- Keep equations and notation stable.

## Delivery formats

For small text:

- Return revised text first.
- Then provide a brief edit note.

For long sections:

- Patch the source file when available.
- Summarize structural changes and unresolved facts.

For paper-level work:

- Provide an outline or edited files.
- Include a "verification needed" list for citations, numbers, or missing materials.
