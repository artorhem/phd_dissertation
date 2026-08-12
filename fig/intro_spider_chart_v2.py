#!/usr/bin/env python3
"""
Spider / radar chart v2: honest scoring, merged axes.

Changes from v1:
  - "Insert Tput" and "Update Tput" merged into "Ingest/Update" (geometric mean)
  - "In-Mem Analytics" and "Dynamic OLAP" merged into single "In-Mem Analytics"
    axis with all systems (GapBS, FlexoGraph, Teseo, LiveGraph, Neo4j)
  - Scoring switched from log to sqrt for honest visual gaps:
      sqrt:   score = 1 + 4/sqrt(ratio)  — [1,5] range; honest gaps
      log:    score = 1 + 4*(1 - log10(ratio)/5)  — compresses gaps
      linear: score = 1 + 4/ratio  — harsh

Raw data sources (all from this evaluation):
  OOC analytics       — ooc-compare.csv, PR total time on graph500-26
  In-memory analytics — BFS+PR+WCC kernel time on g500-26, all systems
  Ingest/Update       — geomean of insertion tput (fig6b, g500-24) and
                         update tput (update_normal, g500-24), M ops/sec
  Property OLTP       — Aster ldbc_raw.dat, update-node-property latency
"""

import math
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

mpl.rcParams.update({
    "font.size": 8,
    "axes.labelsize": 8,
    "xtick.labelsize": 8,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
})

# ---- Scoring mode ----
# "sqrt" (default): honest middle ground — a 4x gap shows as a 2.5-point gap
# "linear":         harshest — a 4x gap shows as a 3.75-point gap
# "log":            original — a 4x gap shows as a 0.6-point gap (misleading)
SCORING = "sqrt"

# ---- Dimensions (axis labels) ----
DIMENSIONS = [
    "OOC\nAnalytics",
    "In-Mem\n  Analytics",
    "In-mem Dynamic Graph\nIngest/Update",
    "Property\nOLTP",
]

# ---- Raw measurements ----
# None = system does not support / was not measured for this dimension
#
# OOC analytics:    PR total time (algo+preproc) on graph500-26, seconds (lower=better)
# In-mem analytics: BFS+PR+WCC kernel time on graph500-26, seconds (lower=better)
#                   GapBS:  7.04  (static in-memory engine)
#                   FG:     10.92 (1.40+5.70+3.82, AdjList)
#                   LG:     38.84 (7.54+20.8+10.5)
#                   Teseo:  39.61 (0.61+27.0+12.0)
#                   Neo4j:  PR+WCC on cit-Patents = 1427.14
#                           (different dataset; included to represent capability)
# Ingest/Update:    geomean of insertion (M edges/s) and update (M ops/s)
#                   on graph500-24 (higher=better)
#                   FG:  sqrt(0.77 * 0.18) = 0.372  (AdjList consistently)
#                   Teseo: sqrt(5.135 * 7.034) = 6.012
#                   LG:  sqrt(0.483 * 0.421) = 0.451
#                   Neo4j: sqrt(0.081 * 0.053) = 0.066
# Property OLTP:   update-node-property latency, microseconds (lower=better)

RAW = {
    #                  OOC(s)   InMem(s)  Ingest(M)  PropOLTP(us)
    "FlexoGraph": [503.4,      10.92,     0.372,     11.05       ],
    "Blaze":      [851.5,      None,      None,      None        ],
    "GapBS":      [None,       7.04,      None,      None        ],
    "LiveGraph":  [None,       38.84,     0.451,     None        ],
    "Teseo":      [None,       39.61,     6.012,     None        ],
    "Neo4j":      [None,       1427.14,   0.066,     46684.0     ],
}

# Direction per dimension: "lower" = lower is better, "higher" = higher is better
DIRECTION = ["lower", "lower", "higher", "lower"]


def compute_scores(raw, direction, mode="sqrt"):
    """Compute scores for each system on each dimension.

    Non-participating systems (None) get 0 — plotted at the center.
    Participating systems score in [1, 5]:
      5 = best in this dimension
      1 = asymptotic floor (very far from best, but still participates)

    Modes (ratio = how many times worse than the best):
      "log":    score = 1 + 4 * max(0, 1 - log10(ratio)/5)
      "sqrt":   score = 1 + 4 / sqrt(ratio)         [default]
      "linear": score = 1 + 4 / ratio
    """
    n_dims = len(direction)
    systems = list(raw.keys())

    # Find best value per dimension
    best = [None] * n_dims
    for d in range(n_dims):
        vals = [raw[s][d] for s in systems if raw[s][d] is not None]
        if not vals:
            continue
        best[d] = min(vals) if direction[d] == "lower" else max(vals)

    scores = {}
    for s in systems:
        row = []
        for d in range(n_dims):
            v = raw[s][d]
            if v is None or best[d] is None:
                row.append(0.0)  # does not participate
                continue
            if direction[d] == "lower":
                ratio = v / best[d]
            else:
                ratio = best[d] / v
            ratio = max(ratio, 1.0)

            if mode == "log":
                score = 1.0 + 4.0 * max(0.0, 1.0 - math.log10(ratio) / 5.0)
            elif mode == "sqrt":
                score = 1.0 + 4.0 / math.sqrt(ratio)
            elif mode == "linear":
                score = 1.0 + 4.0 / ratio
            else:
                raise ValueError(f"Unknown mode: {mode}")

            row.append(score)
        scores[s] = row
    return scores


# ---- Styling (Wong / Okabe-Ito palette) ----
STYLE = {
    "FlexoGraph": {"color": "#009E73", "lw": 2.0, "ls": "-",  "marker": "o", "ms": 4, "alpha": 0.15, "zorder": 10},
    "Blaze":      {"color": "#D55E00", "lw": 1.4, "ls": "-",  "marker": "s", "ms": 3, "alpha": 0.30, "zorder": 6},
    "GapBS":      {"color": "#56B4E9", "lw": 1.4, "ls": "-",  "marker": "^", "ms": 3, "alpha": 0.30, "zorder": 7},
    "LiveGraph":  {"color": "#E69F00", "lw": 1.4, "ls": "-",  "marker": "D", "ms": 3, "alpha": 0.30, "zorder": 8},
    "Teseo":      {"color": "#0072B2", "lw": 1.4, "ls": "-",  "marker": "v", "ms": 3, "alpha": 0.30, "zorder": 9},
    "Neo4j":      {"color": "#CC79A7", "lw": 1.4, "ls": "-",  "marker": "P", "ms": 3, "alpha": 0.30, "zorder": 5},
}

PLOT_ORDER = ["Neo4j", "Blaze", "GapBS", "LiveGraph", "Teseo", "FlexoGraph"]


def plot_spider(scores, out_path):
    n = len(DIMENSIONS)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(3.33, 2.4), subplot_kw=dict(polar=True))
    fig.subplots_adjust(top=0.92, bottom=0.18)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([])  # Remove default labels; place manually below

    # Per-label radial offsets — tuned so multi-line labels don't overlap
    LABEL_OFFSET = [5.6, 6.2, 5.8, 6.2]
    for i, (angle, dim) in enumerate(zip(angles[:-1], DIMENSIONS)):
        ax.text(angle, LABEL_OFFSET[i], dim,
                fontsize=7, fontweight="bold",
                ha="center", va="center")

    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"], fontsize=6.5, color="grey")
    ax.set_rlabel_position(30)

    ax.spines["polar"].set_visible(False)
    ax.grid(True, alpha=0.3, linestyle="--")

    for sys_name in PLOT_ORDER:
        vals = scores[sys_name] + scores[sys_name][:1]
        st = STYLE[sys_name]
        ax.plot(angles, vals, color=st["color"], linewidth=st["lw"],
                linestyle=st["ls"], marker=st["marker"], markersize=st["ms"] + 1,
                label=sys_name, zorder=st["zorder"])
        ax.fill(angles, vals, color=st["color"], alpha=st["alpha"],
                zorder=st["zorder"] - 1)

    # Split legend across bottom-left and bottom-right to avoid the bottom label
    handles, labels = ax.get_legend_handles_labels()
    mid = len(handles) // 2
    leg1 = ax.legend(handles[:mid], labels[:mid],
                     loc="lower left", bbox_to_anchor=(-0.28, -0.12),
                     ncol=1, frameon=False, fontsize=6.5,
                     handlelength=1.2, handletextpad=0.3)
    ax.add_artist(leg1)
    ax.legend(handles[mid:], labels[mid:],
              loc="lower right", bbox_to_anchor=(1.35, -0.12),
              ncol=1, frameon=False, fontsize=6.5,
              handlelength=1.2, handletextpad=0.3)

    fig.savefig(out_path, bbox_inches="tight", pad_inches=0.02)
    print(f"Saved {out_path}")
    plt.close(fig)


def print_scores(scores, mode, systems):
    dim_labels = [d.replace("\n", " ") for d in DIMENSIONS]
    print(f"\n{'--- ' + mode.upper() + ' scoring ---':^80}")
    print(f"{'System':>12s}", end="")
    for d in dim_labels:
        print(f"  {d:>16s}", end="")
    print()
    for s in systems:
        print(f"{s:>12s}", end="")
        for v in scores[s]:
            print(f"  {v:16.2f}", end="")
        print()


if __name__ == "__main__":
    # Print all three scoring modes for comparison
    for mode in ["log", "sqrt", "linear"]:
        sc = compute_scores(RAW, DIRECTION, mode=mode)
        print_scores(sc, mode, PLOT_ORDER)

    # Generate the chart with the selected scoring mode
    scores = compute_scores(RAW, DIRECTION, mode=SCORING)
    plot_spider(scores, "spider_chart_v2.pdf")
    plot_spider(scores, "spider_chart_v2.png")
