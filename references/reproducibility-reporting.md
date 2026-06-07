# Reproducibility and reporting

Use this reference before finalizing methods, experiments, appendices, rebuttals, or camera-ready revisions.

## Experiment card

For each main result, collect:

- Claim tested
- Task, dataset, robot, simulator, or environment
- Train/validation/test split or trial protocol
- Baselines and fairness controls
- Metrics, units, and metric direction
- Seeds, trials, episodes, or repetitions
- Hyperparameters and search ranges
- Compute: CPU/GPU, robot controller, simulator, runtime
- Statistical summary: mean, std/stderr/CI, test if used
- Failure cases and excluded runs

## Robotics experiment card

- Robot platform, end effector, sensors, calibration, payload
- Control frequency, perception frequency, planning frequency
- Environment and object/task variations
- Human intervention: teleoperation, reset, scripted initialization, shared autonomy, or none
- Simulation-to-hardware gap and domain randomization if used
- Number of hardware trials and safety stops

## Control experiment card

- Plant model and discretization
- Sampling time and solver/update rate
- Constraints, disturbance bounds, uncertainty sets
- Initial conditions and reference signals
- Feasibility/infeasibility handling
- Solver, tolerances, runtime, hardware
- Whether plots illustrate theory or provide only empirical evidence

## AI/CS experiment card

- Dataset versions, preprocessing, filtering, and leakage checks
- Model architecture, parameter count, optimizer, schedule, batch size
- Hyperparameter search budget and selected values
- Evaluation scripts and exact prompts if prompting is used
- Compute budget and training/inference cost
- Random seeds and variance across runs

## Reporting red flags

- Main result has no denominator or trial count.
- Baselines use unclear or unequal settings.
- "Real-time" appears without latency/frequency and hardware.
- "Robust" appears without perturbation range or analysis.
- Figure caption claims more than the plot shows.
- Appendix contains information needed to believe the main claim.

## Minimal deliverable

When materials are incomplete, produce a short missing-reporting list instead of inventing details:

```text
Missing for reproducibility: [seeds], [controller frequency], [baseline hyperparameters], [trial count].
```
