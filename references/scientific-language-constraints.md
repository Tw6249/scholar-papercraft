# Scientific language constraints

Use this reference before finalizing abstracts, introductions, method claims, experiments, captions, rebuttals, and limitations. The goal is not only "good English"; the goal is language whose logical strength matches the evidence.

## Evidence strength ladder

Choose verbs and claims from the strongest evidence actually available:

| Evidence | Allowed language | Avoid |
| --- | --- | --- |
| Formal theorem/proof under stated assumptions | proves, guarantees, ensures, is stable under [assumptions] | empirical-only phrasing that hides the theorem assumptions |
| Formal verification or certified constraint satisfaction | certifies, verifies, guarantees within [set] | safe in general, always safe |
| Controlled experiment with fair baselines and repeated trials | shows, demonstrates, improves by [number] on [setting] | proves, guarantees, universally outperforms |
| Ablation or sensitivity study | indicates, supports, contributes to, is associated with | causes, is necessary, is sufficient |
| Single hardware demo or case study | illustrates, demonstrates feasibility in [setting] | validates general robustness, deployable in the real world |
| Qualitative observation | suggests, is consistent with | establishes, confirms |
| No direct evidence | hypothesize, expect, leave as future work, mark as missing | any unqualified scientific claim |

Prefer scoped claims:

```text
Our controller reduces RMS tracking error by 18.6% on the tested pick-and-place tasks.
```

Do not write:

```text
Our controller is robust and superior.
```

## Red-line terms

Use the stronger term only when the listed condition is met. Otherwise use the safer replacement.

| Term | Required evidence | Safer replacement |
| --- | --- | --- |
| stable / stabilizes | stability proof, Lyapunov argument, boundedness theorem, or explicitly scoped empirical boundedness | maintained bounded tracking error in [tested condition] |
| safe / safety-guaranteed | formal safety constraint, verification, certified set, or measured violation rate | reduced collisions, satisfied constraints in [N] trials |
| robust | tested perturbations, uncertainty ranges, domain shifts, or robust control analysis | maintained performance under [specific perturbation] |
| real-time | latency/frequency, hardware, workload, and deadline | runs at [Hz/ms] on [hardware] |
| optimal / globally optimal | proof or exact optimizer for a stated objective | lower cost, best among evaluated methods |
| guarantee / ensure | formal proof or certified mechanism | encourage, enforce in the implemented constraint, observed to |
| significant | statistical test or explicit use as plain-language importance with evidence | improved by [number], statistically significant with [test] |
| state-of-the-art | current, fair, broad comparison to relevant published methods | outperforms evaluated baselines |
| novel / first | careful related-work verification | introduce, develop, propose |
| generalizes | held-out tasks, domains, embodiments, datasets, or theory | transfers to tested [tasks/domains] |
| autonomous | no hidden human intervention in perception, decision, and execution | closed-loop, automated, operator-initialized |
| learns / adapts online | parameter/model/policy updates during operation | uses a learned model, is trained offline |

## Causality constraints

Use causal verbs only with causal evidence:

- `causes`, `because of`, `due to`: require controlled comparison, ablation, intervention, proof, or mechanism.
- `enables`: require the method component to be necessary or clearly responsible for the capability.
- `correlates with`, `is associated with`, `suggests`: use for observational or incomplete evidence.

Bad:

```text
The attention module causes better sim-to-real transfer.
```

Better:

```text
The ablation suggests that the attention module contributes to sim-to-real transfer: removing it lowers hardware success rate from 82% to 69%.
```

## Quantitative language

- Always attach units: Hz, ms, m/s, rad, N, Nm, %, percentage points, trials, seeds.
- Distinguish relative percent from absolute percentage points.
- State denominator for rates: `17/20 trials`, not only `85%`.
- Do not round numbers into stronger claims. Keep precision consistent with noise.
- Do not call a difference meaningful if variance overlaps heavily unless a test or domain reason supports it.
- In captions, make sure the plotted data visibly supports the written takeaway.

## Scope language

Every empirical claim should answer:

- On what robot, simulator, dataset, or task?
- Under what assumptions or environmental conditions?
- Compared with which baselines?
- Measured by which metric?
- Over how many seeds, trials, or episodes?

If the answer is unknown, scope the sentence or mark it.

## Tense and voice

- Use present tense for paper structure: "Figure 3 shows..."
- Use past tense for completed experiments: "We evaluated..."
- Use present tense for established facts and method definitions: "The controller computes..."
- Use active voice when it clarifies the actor: "We train the policy..." rather than "The policy is trained..."
- Passive voice is acceptable when the actor is irrelevant or the object is the topic.

## Sentence and paragraph constraints

- Put one scientific claim in one sentence when precision matters.
- Put the main claim of a paragraph in the first or last sentence, not hidden mid-paragraph.
- Keep subject and verb close.
- Replace vague `this` with a noun: `this result`, `this constraint`, `this ablation`.
- Use the same term for the same concept; do not cycle synonyms for style.
- Do not mix problem, method, result, and implication in one long sentence.

## Robotics-specific constraints

- Do not say `real-world` when the evidence is only simulation. Say `simulation`.
- For lab hardware, prefer `hardware experiments` unless the system was tested in a field environment.
- Report robot platform, sensors, control frequency, compute, environment, task, and number of trials when claims depend on them.
- Do not claim deployment readiness from a controlled demo.
- Distinguish teleoperation, scripted initialization, shared autonomy, and full autonomy.

## Control-specific constraints

- Do not say stable, convergent, optimal, feasible, or recursive feasible unless the proof or solver property is present.
- State assumptions before theorem-level claims.
- Distinguish asymptotic stability, exponential stability, bounded-input bounded-output stability, input-to-state stability, practical stability, and empirical boundedness.
- State sampling time, discretization, model mismatch, disturbance bounds, and constraint sets when they affect the claim.
- Do not turn an empirical tracking plot into a theoretical stability claim.

## AI/CS-specific constraints

- Do not say state-of-the-art without current and fair comparisons.
- Do not say generalization unless held-out tasks/domains/datasets support it.
- Report data splits, seeds, hyperparameter search, compute, and evaluation protocol when relevant.
- Distinguish training accuracy, validation performance, test performance, and deployment performance.
- Avoid benchmark overreach: performance on one benchmark does not imply general intelligence, robust reasoning, or broad autonomy.

## Revision pattern

When auditing text, produce:

```text
Risky phrase: "..."
Problem: [unsupported causal/stability/safety/novelty/etc.]
Evidence available: [source or missing]
Replacement: "..."
```

If editing the manuscript directly, silently apply safe replacements and report only the high-impact downgrades.
