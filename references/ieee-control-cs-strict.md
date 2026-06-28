# IEEE / Control / CS Strict Rules

Use this reference for paper-level submission audits in IEEE, control, robotics, and computer-science venues. It turns general editorial advice into fail-fast gates.

## Core Rule

If a draft has paper-level submission risks, do not make it look publication-ready before resolving the risks.

A polished but structurally non-compliant manuscript is a failed output.

## Evidence Boundary

- For control and robotics papers, use `Simulation Study`, `Numerical Evaluation`, or `Numerical Simulations` when all empirical evidence is simulated.
- Use `Experiments` only when the section includes hardware trials, physical-system trials, real-world datasets, or the target CS venue convention treats benchmark evaluation as experiments.
- Never use `real-world`, `hardware`, `deployment`, `field trial`, or `experimental validation` for simulation-only evidence.
- If the abstract or conclusion says the method was experimentally validated while evidence is simulation-only, block final prose and rewrite to `evaluated in simulation` or `numerical simulations show`.

## Theory

- State plant, graph, communication, solver, timing, and initialization assumptions before theorem-level claims.
- Theorem-level verbs require theorem-level evidence and visible assumptions.
- Simulations may illustrate or empirically evaluate a theorem; they do not prove it.
- Continuous-time guarantees and sampled-data simulations must be reconciled when the evidence uses zero-order hold, Euler integration, finite sampling, or simulator-specific monitors.
- If a guarantee depends on certified local solves, centralized initialization, atomic commits, non-overlap, protected aborts, no message loss, or non-Zeno switching, surface that scope in the title, abstract, contribution bullets, theorem statement, and conclusion.

## Contributions

- Default to 2-4 contribution bullets.
- Each bullet must be a claim, not a module name.
- Each bullet should expose the novelty object, technical action, evidence type, and scope/assumption.
- Evaluation is not a contribution unless the benchmark, dataset, protocol, or artifact is itself new and reusable.
- Do not list internal lifecycle steps, transactions, scripts, or implementation modules as parallel core contributions unless they are the paper's actual contribution.

## Experiments And Simulations

- Each empirical subsection should follow: question -> setup -> metric -> baseline -> result -> claim supported.
- Report N, seeds/trials/runs, metric definition, metric direction, uncertainty type, and failure/exclusion criteria.
- Matched-seed comparisons should report paired differences, confidence intervals, or paired tests when claiming reduction or improvement.
- Stress tests are required when claiming robustness, scalability, asynchronous reliability, distributed reliability, or operating margin.
- If a diagnostic value repeats identically across methods or scenarios, block strong result wording until the metric computation is verified or the value is explained as a deterministic threshold, monitor floor, or shared constant.

## Artifact Hygiene

- Do not include script names, local paths, CSV names, debug files, notebook provenance, or raw log filenames in the main narrative.
- Use `Code and Data Availability`, supplement, appendix, or repository README for reproduction commands and filenames.
- In the main paper, describe protocol, metrics, trial count, seeds, parameter values, solver settings, and data-processing contract.

Acceptable main-paper wording:

```text
We evaluated the method in a 960-run simulation study over four scenarios and 30 matched seeds. The public repository contains the scripts and data needed to reproduce the reported tables and figures.
```

## Figures

- Export line art as vector PDF, SVG, or EPS unless there is a content-specific reason for raster output.
- Check one-column and two-column readability.
- Use markers, line styles, hatches, or labels in addition to color.
- Define error bars, uncertainty bands, sample counts, and metric direction.
- Multi-panel script composites are allowed when panels share a data source, metric contract, axes, statistical encoding, or synchronized legend.
- LaTeX subfigures are preferred when panels are semantically independent, reused separately, or cited as separate subfigures.
- Claim-bearing captions require Figure Cards. Without a Figure Card, do not write result-strength caption claims.

## References

- Prefer peer-reviewed or final published versions over arXiv when available.
- Do not make novelty, first, or state-of-the-art claims without a verified closest-work search.
- In IEEE journal submissions, a bibliography dominated by arXiv entries is a maturity warning and should trigger publication-version checks.
- Citation recovery tools produce candidates only; they do not replace reference audit.

## Venue Shape

- For IEEE journal drafts, check title, abstract, index terms/keywords, first footnote/funding placeholders where applicable, method/results/discussion/conclusion structure, references, and acknowledgments.
- IEEE-style abstracts should generally be one paragraph, self-contained, 250 words or fewer, and free of citations, footnotes, unexplained abbreviations, and display math unless a target journal explicitly differs.
- Titles should be specific, concise, and descriptive; avoid `new` and `novel` unless there is a venue-specific reason.
- Simulation-only robotics/control papers should include explicit limitations or discussion of simulation scope.

## Mandatory Gate Set

For paper-level IEEE/control/CS submission audit, run or explicitly mark unavailable:

1. claim-evidence gate
2. evidence-boundary gate
3. contribution-structure gate
4. theory-assumption gate
5. experiment/simulation reporting gate
6. artifact-hygiene gate
7. figure/table publication gate
8. reference-maturity gate
9. venue-shape gate
10. conclusion-escalation gate

Report each item as `PASS`, `BLOCKED`, or `WARN`. A `BLOCKED` item must include the manuscript location, reason, and required repair.
