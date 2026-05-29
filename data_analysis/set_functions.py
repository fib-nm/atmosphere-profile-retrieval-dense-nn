import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

def set_stats(x, singular_name, plural_name, humanizer=None):
    x_max = np.max(x)
    x_min = np.min(x)
    x_mean = np.mean(x)
    x_median = np.median(x)
    x_sum = np.sum(x)

    if humanizer is None:
        humanizer = lambda x: x

    if singular_name is not None:
        print(f"Max {singular_name}: {humanizer(x_max)}")
        print(f"Min {singular_name}: {humanizer(x_min)}")
        print(f"Mean {singular_name}: {humanizer(x_mean)}")
        print(f"Median {singular_name}: {humanizer(x_median)}")
    
    if plural_name is not None:
        print(f"Total {plural_name}: {humanizer(x_sum)}")


def hist(x, bins, first_n_bins, title, xlabel, xformatter=None):
    counts, edges = np.histogram(x, bins=bins)
    counts = counts[:first_n_bins]
    edges = edges[:first_n_bins+1]

    fig, ax = plt.subplots(layout="constrained", figsize=(6, 4))
    ax.bar(edges[:-1], counts, width=np.diff(edges), align="edge")

    if xformatter is not None:
        ax.xaxis.set_major_formatter(FuncFormatter(xformatter))
    
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Count")
    plt.show()


def rank_size_plot(x, title, ylabel, yformatter=None):
    x_sorted = np.sort(x)[::-1]

    n = np.arange(1, len(x_sorted) + 1)

    fig, ax = plt.subplots(layout="constrained", figsize=(6, 4))
    ax.plot(n, x_sorted)
    ax.set_xlabel("N")
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    if yformatter is not None:
        ax.yaxis.set_major_formatter(FuncFormatter(yformatter))

    ax.set_ylim(bottom=0)
    ax.set_xlim(left=-0.01*len(x))
    plt.show()


def cumulative_plot(x, title, levels=(0.5, 0.9)):
    x_sorted = np.sort(x)[::-1]

    cumsum = np.cumsum(x_sorted)

    total = cumsum[-1]

    fraction = cumsum / total

    n = np.arange(1, len(fraction) + 1)

    fig, ax = plt.subplots(layout="constrained", figsize=(6, 4))
    ax.plot(n, fraction)

    for level in levels:
        idx = np.searchsorted(fraction, level, side="left")
        n_level = n[idx]
        y_level = fraction[idx]
        
        ax.axhline(y_level, xmin=0, xmax=(n_level+10)/(ax.get_xlim()[1]-10), linestyle="--", linewidth=1)
        ax.axvline(n_level, ymin=0, ymax=y_level/1.01, linestyle="--", linewidth=1)

        ax.annotate(
            str(n_level),
            xy=(n_level, 0),
            xytext=(0, -15),
            textcoords="offset points",
            ha="center",
            va="top",
            clip_on=False,
        )

        ax.annotate(
            str(level),
            xy=(0, y_level),
            xytext=(-15, 0),
            textcoords="offset points",
            ha="center",
            va="top",
            clip_on=False,
        )

        ax.scatter(n_level, y_level, s=20, color="blue")

    ax.set_xlabel("N")
    ax.set_ylabel("Fraction")
    ax.set_title(title)
    ax.set_xlim(left=-10)
    ax.set_ylim([0, 1.01])
    plt.show()
