# Venue packs

Use this compact router when adapting a draft to a field. Do not rely on this file for current page limits, deadlines, templates, or AI-disclosure wording; check the official venue page when those details matter.

## Robotics journals and conferences

Science Robotics:

- Lead with the robotic or scientific capability, not only the algorithm.
- Explain physical system, environment, embodiment, sensing, actuation, and mechanism.
- Prefer evidence-rich visual storytelling: overview, real system, result, limitation.
- Avoid benchmark-only framing unless it exposes a broader robotics principle.

T-RO / IJRR:

- Write as archival robotics: problem definition, assumptions, notation, method, theory if present, extensive evaluation.
- Make limitations and operating conditions explicit.
- Require traceable robot platform, sensors, controller frequency, compute, simulator/hardware split, trial count, and baselines.

RA-L:

- Compress aggressively. Contribution, method, and evidence must appear early.
- Captions and tables should carry interpretation because space is tight.
- Related work should position against closest robotics methods, not survey broadly.

ICRA / IROS:

- Optimize for reviewer scanning: title, abstract, introduction, Figure 1, contribution bullets, main result.
- Tie each experiment to a contribution.
- Prepare video, graphical abstract, and supplementary material when the venue allows or requires them.

## Control venues

TAC / Automatica:

- Prioritize theorem-quality precision: assumptions, problem statement, definitions, lemmas, proof dependencies.
- Distinguish stability, convergence, feasibility, optimality, and robustness claims.
- Do not present simulation as proof; use it as illustration or validation under stated settings.

TCST:

- Emphasize control design plus implementation realism.
- Report sampling time, plant/model mismatch, disturbance assumptions, actuator/sensor constraints, and computational burden.

L-CSS / CDC / ACC:

- Use letter-style compression: one sharp problem, one main contribution, compact proof sketch, concise examples.
- Move nonessential derivations, extra simulations, and extended discussion out when page limits are tight.

## AI and CS venues

NeurIPS / ICML / ICLR:

- Emphasize task, method, baselines, ablations, data, compute, statistical variation, limitations, and reproducibility.
- Avoid state-of-the-art claims without current, broad, fair comparisons.
- Include ethics/impact/LLM-use disclosure when required.

CVPR / ICCV / ECCV:

- Make visual evidence strong: qualitative examples, failure cases, ablations, and benchmark comparisons.
- Check dataset licensing, annotation protocol, and train/test leakage risks.

ACL / EMNLP:

- Emphasize dataset construction, evaluation protocol, limitations, ethics, and language coverage.
- Be precise about model use, prompting, annotators, and automatic vs human evaluation.

## Conversion rules

- Journal-to-conference: compress background and proof detail; promote Figure 1 and main result.
- Conference-to-journal: add theory, details, ablations, extended experiments, limitations, and clearer relation to prior work.
- AI-to-robotics: add embodiment, control loop, sensing, hardware/simulation boundary, and deployment conditions.
- Robotics-to-control: strengthen assumptions, mathematical problem statement, and proof language.
