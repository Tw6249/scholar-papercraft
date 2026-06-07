# Venue style guide

Use this reference for tone and framing. Always verify current page limits, templates, AI disclosure rules, anonymity rules, and submission deadlines from official venue pages before formatting a submission.

## Science Robotics

Writing posture:

- Make the robotics significance clear to a broad technical readership.
- Lead with the scientific or robotic capability enabled by the work, not only the algorithmic component.
- Explain the physical system, environment, task, and mechanism in accessible language.
- Use strong visual storytelling: overview figure, real robot or system image, and evidence-rich results.
- Avoid narrow benchmark-only framing unless the benchmark exposes a broader robotic principle.

Typical emphasis:

- New robotic capability, physical intelligence, embodied interaction, bio-inspired design, autonomy, or field deployment.
- Mechanistic explanation and real-world evidence.
- Limitations stated plainly, especially around deployment conditions and generality.

Editing moves:

- Replace jargon stacks with one precise technical term plus an explanation.
- Move specialist derivations to later sections or supplementary materials when the main story needs breadth.
- Keep quantitative evidence visible in the abstract and main text.

## IEEE Transactions on Robotics (T-RO)

Writing posture:

- Dense, precise, archival, and technically complete.
- Prioritize correctness, notation consistency, reproducibility, and relationship to prior robotics literature.
- Make assumptions explicit before algorithms, theorems, or stability claims.

Typical emphasis:

- Formal problem statement, algorithm/controller design, theoretical properties, extensive experiments, ablations, and hardware validation when relevant.
- Strong baselines and careful comparison settings.
- Clear notation tables for complex methods.

Editing moves:

- Tighten definitions and symbols before polishing sentences.
- Ensure every theorem/claim has assumptions and a proof sketch or citation.
- Use "we show" only when the paper provides proof or experiment; use narrower verbs otherwise.

## IEEE Robotics and Automation Letters (RA-L)

Writing posture:

- Concise IEEE style with fast access to the method and evidence.
- Make the contribution and experiments visible early.
- Keep related work compact and sharply positioned.

Typical emphasis:

- Clear novelty in robotics/automation.
- Reproducible method and credible experiments within tight length constraints.
- Optional conference presentation framing when paired with ICRA/IROS, but the paper must stand as a journal letter.

Editing moves:

- Compress background.
- Merge related work with problem framing when space is tight.
- Use compact tables and captions that carry experimental interpretation.

## ICRA / IROS

Writing posture:

- Conference-readable, direct, and visually guided.
- A reviewer should understand the problem, gap, approach, and headline result from title, abstract, intro, and Figure 1.

Typical emphasis:

- Problem gap in robotics practice or theory.
- Method overview diagram.
- Experimental setup and baselines that establish the claim quickly.
- Failure cases and limitations where they improve trust.

Editing moves:

- Put contributions in 2-4 concise bullets.
- Tie each experiment to one contribution.
- Use clear subsection titles that signal the claim tested.

## AI / CS venues

Writing posture:

- Center the task, model/algorithm, assumptions, evaluation protocol, baselines, and ablations.
- Avoid robotics-specific claims unless supported by embodied experiments.

Typical emphasis:

- Benchmark fairness, data splits, compute, hyperparameters, reproducibility, ablations, and limitations.
- Related work organized by technical families, not paper-by-paper chronology.

## Cross-venue style calibration

| Need | Prefer |
| --- | --- |
| Broad impact | Science Robotics-style motivation with concrete capability |
| Archival completeness | T-RO-style definitions, assumptions, and experiments |
| Short journal letter | RA-L-style compression and dense captions |
| Conference review clarity | ICRA/IROS-style visual overview and explicit contribution bullets |
| AI benchmark paper | ML-style ablation, baseline, and metric transparency |

## Venue-sensitive warnings

- Do not rely on stale page limits or templates. Look up current official instructions.
- Check whether AI-assisted writing must be disclosed.
- Check whether videos, supplementary material, or code links are allowed during review.
- Check double-blind requirements before including lab names, project URLs, acknowledgments, or self-revealing videos.
