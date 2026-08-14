#!/usr/bin/env python3
"""Generate adjacency matrix sparsity pattern and degree distribution
plots for soc-Epinions1 as PDFs."""

import os
import gzip
import urllib.request
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.sparse import coo_matrix

DATA_URL = "https://snap.stanford.edu/data/soc-Epinions1.txt.gz"
DATA_FILE = "/tmp/soc-Epinions1.txt.gz"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

def download_data():
    if not os.path.exists(DATA_FILE):
        print("Downloading soc-Epinions1...")
        urllib.request.urlretrieve(DATA_URL, DATA_FILE)
    return DATA_FILE

def load_edges(path):
    src, dst = [], []
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt") as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split()
            if len(parts) >= 2:
                src.append(int(parts[0]))
                dst.append(int(parts[1]))
    return np.array(src), np.array(dst)

def main():
    path = download_data()
    src, dst = load_edges(path)
    n = max(src.max(), dst.max()) + 1
    print(f"Loaded {len(src)} edges, {n} nodes")

    mat = coo_matrix((np.ones(len(src)), (src, dst)), shape=(n, n))

    # --- Plot 1: Adjacency matrix sparsity pattern ---
    fig1, ax1 = plt.subplots(figsize=(4.5, 3.8))
    ax1.spy(mat, markersize=0.01, rasterized=True, color="#0077BB")
    ax1.set_xlabel("Destination vertex", fontsize=16)
    ax1.set_ylabel("Source vertex", fontsize=16)
    ax1.set_title("")
    # Format tick labels as 0, 10k, 20k, ...
    from matplotlib.ticker import FuncFormatter, MultipleLocator
    def thousands_fmt(x, pos):
        if x == 0:
            return "0"
        return f"{int(x/1000)}k"
    # Tick spacing adapts to graph size
    tick_step = max(n // 4, 1000)
    tick_step = round(tick_step, -len(str(tick_step)) + 1)  # round to leading digit
    ax1.xaxis.set_major_locator(MultipleLocator(tick_step))
    ax1.yaxis.set_major_locator(MultipleLocator(tick_step))
    ax1.xaxis.set_major_formatter(FuncFormatter(thousands_fmt))
    ax1.yaxis.set_major_formatter(FuncFormatter(thousands_fmt))
    ax1.tick_params(axis="both", labelsize=14)
    fig1.tight_layout()
    out1 = os.path.join(OUT_DIR, "epinions_adjmatrix.pdf")
    fig1.savefig(out1, dpi=300, bbox_inches="tight")
    print(f"Saved {out1}")

    # --- Plot 2: Degree distribution ---
    csr = mat.tocsr()
    out_degrees = np.diff(csr.indptr)
    # Count how many nodes have each degree
    max_deg = out_degrees.max()
    deg_counts = np.bincount(out_degrees, minlength=max_deg + 1)
    degrees = np.arange(len(deg_counts))
    # Filter out zero counts for log-log
    mask = deg_counts > 0
    degrees = degrees[mask]
    counts = deg_counts[mask]

    fig2, ax2 = plt.subplots(figsize=(4.5, 3.8))
    ax2.scatter(degrees, counts, s=8, alpha=0.6, color="#0077BB", edgecolors="none")
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_xlabel("Degree (out)", fontsize=16)
    ax2.set_ylabel("Frequency", fontsize=16)
    ax2.tick_params(axis="both", labelsize=14)
    ax2.set_ylim(top=1e5)
    ax2.set_title("")
    fig2.tight_layout()
    out2 = os.path.join(OUT_DIR, "degree_distribution_epinions.pdf")
    fig2.savefig(out2, dpi=300, bbox_inches="tight")
    print(f"Saved {out2}")

if __name__ == "__main__":
    main()
