#!/usr/bin/env python3
"""Generate thesis-quality 2x2 property CRUD bar chart."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RESULTS_DIR = '/home/puneet/scratch/Aster_artifact/results/figure_7'
OUT_DIR = '/home/puneet/Documents/thesis/fig/property'

COLORS = {
    'Neo4j':           '#AD88C6',
    'ArangoDB':        '#FF8000',
    'PostgreSQL':      '#EEAEAF',
    'OrientDB':        '#FFAE50',
    'JanusGraph':      '#FED98E',
    'AsterDB':         '#67A9CF',
    'FlexoGraph-Adj':  '#2CA02C',
    'FlexoGraph-Ekey': '#98DF8A',
}

HATCHES = {
    'Neo4j':           '',
    'ArangoDB':        '//',
    'PostgreSQL':      '\\\\',
    'OrientDB':        'xx',
    'JanusGraph':      '..',
    'AsterDB':         'oo',
    'FlexoGraph-Adj':  '',
    'FlexoGraph-Ekey': '--',
}

SKIP = {'NebulaGraph'}

file_label_pairs = [
    ('freebase_add_delete.dat', '(a) Freebase Add/Delete'),
    ('ldbc_add_delete.dat',     '(b) LDBC Add/Delete'),
    ('freebase_update_get.dat', '(c) Freebase Update/Get'),
    ('ldbc_update_get.dat',     '(d) LDBC Update/Get'),
]

with matplotlib.rc_context({
    'font.family': 'sans-serif',
    'font.size': 6,
    'axes.labelsize': 7,
    'axes.titlesize': 8,
    'xtick.labelsize': 5,
    'ytick.labelsize': 6,
    'legend.fontsize': 5.5,
    'hatch.linewidth': 0.6,
    'axes.linewidth': 1.0,
}):
    fig, axes = plt.subplots(2, 2, figsize=(3.33, 3.4))
    axes = axes.flatten()

    first_ax = None
    for ax, (fname, label) in zip(axes, file_label_pairs):
        fpath = os.path.join(RESULTS_DIR, fname)
        df = pd.read_csv(fpath, sep='\t')
        ops = df.iloc[:, 0].values
        systems = [s for s in df.columns[1:] if s not in SKIP]
        if first_ax is None:
            first_ax = ax

        n_ops = len(ops)
        n_sys = len(systems)
        bar_w = 0.88 / n_sys
        x = np.arange(n_ops)

        for i, sys_name in enumerate(systems):
            vals = pd.to_numeric(df[sys_name], errors='coerce').fillna(0).values
            offset = (i - (n_sys - 1) / 2) * bar_w
            ax.bar(x + offset, vals, bar_w,
                   color=COLORS.get(sys_name, '#999'),
                   hatch=HATCHES.get(sys_name, ''),
                   edgecolor='black', linewidth=0.25,
                   label=sys_name if ax is first_ax else '')

        ax.set_xticks(x)
        wrapped = [o.strip('"').replace(' ', '\n') for o in ops]
        ax.set_xticklabels(wrapped, ha='center')
        ax.set_yscale('log')
        ax.set_title(label, fontsize=7, fontweight='bold')
        ax.grid(True, axis='y', alpha=0.25, linestyle='--')
        ax.set_axisbelow(True)

    for row_start in [0, 2]:
        ymin = min(axes[row_start].get_ylim()[0], axes[row_start+1].get_ylim()[0])
        ymax = max(axes[row_start].get_ylim()[1], axes[row_start+1].get_ylim()[1])
        axes[row_start].set_ylim(ymin, ymax)
        axes[row_start+1].set_ylim(ymin, ymax)

    axes[0].set_ylabel('Latency (ms)')
    axes[2].set_ylabel('Latency (ms)')

    handles, lbls = first_ax.get_legend_handles_labels()
    fig.legend(handles, lbls, loc='upper center', ncol=4,
               frameon=False, borderpad=0.15, fontsize=5,
               handlelength=1.3, handletextpad=0.3, columnspacing=0.6,
               bbox_to_anchor=(0.5, 1.02))
    fig.tight_layout(rect=[0, 0, 1, 0.89])

    out = os.path.join(OUT_DIR, 'property_crud')
    fig.savefig(out + '.pdf', bbox_inches='tight')
    fig.savefig(out + '.png', bbox_inches='tight', dpi=200)
    plt.close(fig)
    print(f"Saved {out}.pdf / .png")
