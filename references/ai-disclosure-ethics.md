# AI disclosure, privacy, ethics, and limitations

Use this reference when the task involves submission, rebuttal, camera-ready text, private reviews, human/robot data, or AI-assisted writing disclosure.

## AI assistance

- Check the target venue's current AI policy before submission.
- Disclose AI assistance when the venue requires it or when substantial drafting, editing, figure generation, code generation, or translation polishing was used.
- Do not claim AI tools as authors.
- Do not use AI to fabricate data, citations, images, code results, reviewer quotes, or experiments.
- Keep author responsibility explicit: authors verify claims, citations, results, and final wording.

Disclosure template:

```text
The authors used AI-based writing assistance for language editing and draft organization. All technical claims, experiments, citations, and final text were reviewed and verified by the authors.
```

Use a narrower template if AI was only used for grammar or translation.

## Review privacy

- Do not upload confidential manuscripts, reviews, rebuttal text, or reviewer identities to external services unless the venue and authors allow it.
- Remove private metadata from PDFs, videos, and supplementary files when anonymity matters.
- Do not reveal lab identity through acknowledgments, URLs, file names, repository names, videos, or self-citations in double-blind review.

## Ethics and safety

For robotics/control:

- State safety boundaries, test environment restrictions, human supervision, emergency stops, and failure modes when relevant.
- Do not imply deployability in human environments from lab-only demonstrations.
- Report collisions, unsafe stops, or excluded failures when they affect interpretation.

For AI/CS:

- State dataset licenses, human-subject considerations, privacy risks, misuse risks, and annotation protocol when relevant.
- Include model/data limitations and benchmark scope.

## Limitations

Good limitations are scoped and nonfatal:

```text
The current hardware experiments are limited to tabletop manipulation with rigid objects; deformable objects require additional perception and contact modeling.
```

Avoid generic endings:

```text
Future work will explore broader applications.
```
