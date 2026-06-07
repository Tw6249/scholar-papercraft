# Plotting, figures, and table improvement

Use this reference when creating or improving figures, captions, tables, or plotting code.

## Figure decision guide

| Input | Best output |
| --- | --- |
| Method architecture, controller pipeline, robot system flow | overview diagram |
| Training/evaluation over time | line plot with confidence band |
| Methods across metrics/tasks | grouped bar chart or compact table |
| Ablation over components | grouped bar chart, line plot, or table |
| Tracking or control error | time-series plot with units and event markers |
| Real robot trajectory | trajectory plot with environment context |
| Distribution across trials | box, violin, or ECDF |
| Confusion/error matrix | heatmap |

Avoid pie charts for technical results unless composition is truly the claim.

## Plot code improvement checklist

- Preserve raw data loading and metric definitions.
- Add clear units to axis labels.
- Use vector export for paper figures: PDF/SVG/EPS when possible.
- Export PNG at 300-600 DPI for preview or raster-only content.
- Use colorblind-safe palettes plus line styles or markers.
- Avoid chart titles inside paper figures; use captions instead.
- Remove chart junk: heavy grids, unnecessary frames, duplicate legends.
- Use consistent fonts and sizes across figures.
- Use deterministic ordering for methods and benchmarks.
- Highlight the proposed method consistently.
- Put uncertainty bands or error bars where multiple runs exist.
- State whether error bars are std, stderr, confidence intervals, or min/max.
- Keep scripts reproducible: no absolute paths unless necessary; expose input/output paths as arguments.

## Matplotlib defaults

Use a compact style suitable for IEEE two-column papers:

```python
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 8.5,
    "axes.labelsize": 8.5,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "legend.fontsize": 7.5,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.18,
    "grid.linewidth": 0.5,
})

OKABE_ITO = [
    "#E69F00", "#56B4E9", "#009E73", "#F0E442",
    "#0072B2", "#D55E00", "#CC79A7", "#000000",
]
OUR_COLOR = "#D55E00"
BASELINE_COLOR = "#9AA0A6"
FIG_SINGLE = (3.35, 2.25)
FIG_DOUBLE = (6.85, 2.6)
```

## MATLAB plotting defaults

For MATLAB figures:

```matlab
set(groot, 'defaultAxesFontName', 'Times New Roman');
set(groot, 'defaultTextFontName', 'Times New Roman');
set(groot, 'defaultAxesFontSize', 8.5);
set(groot, 'defaultLineLineWidth', 1.4);
set(groot, 'defaultAxesBox', 'off');
set(groot, 'defaultAxesTickDir', 'out');
set(groot, 'defaultAxesGridAlpha', 0.18);
```

Export:

```matlab
exportgraphics(gcf, 'fig_result.pdf', 'ContentType', 'vector');
exportgraphics(gcf, 'fig_result.png', 'Resolution', 300);
```

## Robotics/control figure specifics

- For trajectory plots, show start, goal, obstacles, and scale.
- For time-series control plots, label phases/events and saturation limits.
- For tracking error, include units and reference trajectory context.
- For real robot results, distinguish simulation and hardware clearly.
- For success/failure rates, report number of trials.
- For latency/control frequency, specify hardware and load.

## Caption templates

Trajectory:

```text
Trajectory tracking on [task/environment]. The proposed method [what line/color] follows [reference] while maintaining [constraint]. Shaded regions indicate [uncertainty/obstacle/safety boundary]. Across [N] trials, [verified result].
```

Ablation:

```text
Ablation of [components] on [metric/task]. Removing [component] degrades [metric] by [number], indicating that [claim]. Error bars show [definition] over [N] seeds/trials.
```

Overview:

```text
Overview of [method/system]. [Input] is processed by [modules] to produce [output]. The key distinction from prior work is [specific mechanism], which enables [capability] under [conditions].
```

## Table improvement

- Use `booktabs` in LaTeX.
- Align decimal points.
- State metric direction in the header or caption.
- Bold only the best values that are meaningfully comparable.
- Do not overbold every number from the proposed method.
- Keep precision consistent with measurement noise.

## Verification

Before finalizing:

- Run the plotting script when data and environment are available.
- Open or inspect the generated figure.
- Check that text remains readable at final column width.
- Check grayscale readability.
- Check that the caption's claim is visible in the plot.
