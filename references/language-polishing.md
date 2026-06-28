# Language Polishing

Use this reference for de-AI editing, trim-and-sharpen revision, author-voice preservation, Chinese-to-English polishing, and any request to make academic prose shorter, sharper, less generic, or more field-authored.

The goal is not to hide AI use. The goal is information density, visible judgment, evidence-matched wording, and field-appropriate prose.

## Language Modes

### `cold-dense`

Use by default for control, robotics, Automatica, T-RO, RA-L, CDC/ACC, and theorem-heavy ICRA/IROS papers.

Priorities:

- shorten before beautifying
- use precise verbs and concrete nouns
- reduce decorative transitions
- keep claims scoped
- prefer restraint over persuasion
- let equations, definitions, and measured results carry weight

### `narrative-persuasive`

Use for Science Robotics, Nature-family venues, broader-audience robotics papers, and some NeurIPS/ICLR introductions.

Priorities:

- keep a clear reader path
- make the problem tension legible
- allow more paragraph momentum
- preserve mechanism and evidence
- avoid hype, generic impact language, and unsupported breadth

Both modes must preserve facts, numbers, citations, theorem scope, notation, and claim strength.

## Trim-And-Sharpen Order

1. Compress first. Remove 15-30% when the prose is padded.
2. Check claim strength. Strong verbs require evidence.
3. Replace weak verbs with research actions.
4. Put sentence stress at the end.
5. Vary rhythm only where the argument needs emphasis.
6. Preserve author judgment: what the result shows, what it does not show, and where its boundary lies.

## Edit Rules

### Delete fake openings

Weak:

```text
It is important to note that the proposed method improves feasibility.
```

Better:

```text
The proposed method improves feasibility.
```

Sharper:

```text
The reserve allocation makes local feasibility invariant.
```

### Replace evaluators with evidence

Weak:

```text
The method is highly effective.
```

Better:

```text
The method reduces infeasible QP instances from 18/50 to 2/50.
```

If the evidence is absent, mark it instead of decorating the claim.

### Replace decorative transitions with logical relations

Weak:

```text
Furthermore, the method handles input bounds.
```

Better:

```text
Input bounds are the failure mode that motivates the reserve variable.
```

Good transitions name relations:

```text
This mismatch motivates...
This assumption limits...
This result narrows...
This ablation separates...
```

### Replace generic conclusions with claim-supported takeaways

Weak:

```text
These results demonstrate the effectiveness of the proposed method.
```

Better:

```text
The ablation suggests that reserve transfer, rather than uniform burden splitting, accounts for the lower infeasibility rate.
```

### Convert nominalizations to verbs

Weak:

```text
The realization of the improvement of performance is achieved through optimization.
```

Better:

```text
The optimizer reduces tracking error.
```

Do not force verb edits when the nominal form is a standard term, such as `positive invariance` or `constraint satisfaction`.

### Preserve sharp author judgment

Weak:

```text
This may provide a useful solution for multi-agent systems.
```

Sharper:

```text
The result narrows the claim: feasibility is preserved at each reserve iterate, but optimality still depends on convergence of the master allocation.
```

## Weak Verb Replacements

Prefer specific research actions:

| Weak | Replace with when true |
| --- | --- |
| highlights | shows, separates, identifies |
| underscores | supports, motivates, constrains |
| leverages | uses, exploits, parameterizes |
| showcases | illustrates, evaluates |
| facilitates | enables, reduces, removes |
| utilizes | uses |

Do not use a stronger verb unless the claim ledger licenses it.

## Chinese-To-English Sharpening

- Replace literal `based on` with the actual relation: `uses`, `conditions on`, `derives from`, `builds on`, or `under`.
- Replace `aiming at` with an action: `to reduce`, `to enforce`, `to estimate`.
- Use `we` only when author preference and venue allow it; otherwise prefer the method or result as subject.
- Watch empty topic openers such as `In this paper, ...`.
- Keep established field terms even when they sound repetitive.

## Before/After Checks

After substantial language editing, run:

```bash
python scripts/audit_language_density.py <draft-or-project>
python scripts/compare_revision_style.py <before> <after>
```

Use `--fail-on-major` only for strict audit or CI.
