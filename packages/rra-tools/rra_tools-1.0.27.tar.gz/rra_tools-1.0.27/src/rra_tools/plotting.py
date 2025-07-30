"""Plotting utilities for RRA tools."""

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.figure import Figure


def strip_axes(ax: Axes) -> Axes:
    """Despine axis and remove ticks and labels."""
    sns.despine(ax=ax, left=True, bottom=True)
    ax.set_xticks([])
    ax.set_yticks([])
    return ax


def write_or_show(
    fig: Figure, plot_file: str | Path | None, **savefig_kwargs: Any
) -> None:
    """Write the figure to a file or show it."""
    if plot_file:
        fig.savefig(plot_file, **savefig_kwargs)
        plt.close(fig)
    else:
        plt.show()
