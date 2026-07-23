#!/usr/bin/env python3
"""
Spider / radar chart showing FlexoGraph's breadth across 4 evaluation
dimensions vs. best-in-class competitors from each system category.

Scoring: score = max(0, 5 - log10(ratio_to_best))
  - Best system in a dimension gets 5
  - Each order of magnitude worse costs 1 point
  - Systems that do not support a dimension get 0

Raw data sources (all from this evaluation):
  Dim 1  OOC analytics        – ooc-compare.csv, PR total time on graph500-26
  Dim 2  In-memory analytics  – flexograph_compare_inmem.csv, 4-algo total on g500-26
  Dim 3  Mutation throughput   – fig6b + update_normal SQLite, geomean of insertion
                                 and update throughput on graph500-24
  Dim 4  Property graph OLTP   – Aster ldbc_raw.dat, update-node-property latency
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

# ---- Dimensions (axis labels) ----
DIMENSIONS = [
    "OOC Analytics",
    "In-Mem Analytics",
    "Insert Tput",
    "Update Tput",
    "Property OLTP",
]

# ---- Raw measurements ----
# None = system does not support / was not measured for this dimension
#
# OOC analytics:  PR total time (algo+preproc) on graph500-26, seconds
# In-mem analytics: BFS+PR+WCC kernel time on graph500-26, seconds (algo only)
# Insertion tput: graph500-24 peak writers, M edges/sec
# Update tput:    graph500-24 mixed insert+delete, M ops/sec
# Property OLTP:  update-node-property latency, microseconds
RAW = {
    #                    OOC(s,lo)  InMem(s,lo)  Insert(M,hi) Update(M,hi)  PropOLTP(μs,lo)
    "FlexoGraph": [503.4,          10.92,        1.702,       1.057,        11.05          ],
    "Blaze":      [851.5,          None,         None,        None,         None           ],
    "GapBS":      [None,           7.04,         None,        None,         None           ],
    "LiveGraph":  [None,           None,         0.483,       0.421,        None           ],
    "Teseo":      [None,           39.57,        5.135,       7.034,        None           ],
    "Neo4j":      [None,           None,         0.081,       0.053,        46684.0        ],
}

# Direction per dimension: "lower" = lower value is better, "higher" = higher is better
DIRECTION = ["lower", "lower", "higher", "higher", "lower"]


def compute_scores(raw, direction):
    n_dims = len(direction)
    systems = list(raw.keys())

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
                row.append(0.0)
                continue
            if direction[d] == "lower":
                ratio = v / best[d]
            else:
                ratio = best[d] / v
            score = max(0.0, 5.0 - math.log10(max(ratio, 1.0)))
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

    # Per-label radial offsets from the outermost ring (5.0)
    # Smaller offset = closer to the plot
    LABEL_OFFSET = [5.4, 6.2, 5.8, 5.8, 6.2]  # top close; upper-right/left further
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

    ax.legend(
        loc="lower center",
        bbox_to_anchor=(0.5, -0.22),
        ncol=6,
        frameon=False,
        fontsize=6.5,
        handlelength=1.2,
        handletextpad=0.3,
        columnspacing=0.5,
    )

    fig.savefig(out_path, bbox_inches="tight", pad_inches=0.02)
    print(f"Saved {out_path}")
    plt.close(fig)


if __name__ == "__main__":
    scores = compute_scores(RAW, DIRECTION)

    print("Scores (0-5 scale):")
    print(f"{'System':>12s}", end="")
    for d in DIMENSIONS:
        print(f"  {d.replace(chr(10), ' '):>16s}", end="")
    print()
    for s in PLOT_ORDER:
        print(f"{s:>12s}", end="")
        for v in scores[s]:
            print(f"  {v:16.2f}", end="")
        print()

    plot_spider(scores, "intro_spider_chart.pdf")
