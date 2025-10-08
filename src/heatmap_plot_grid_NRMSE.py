"""
Heatmap plotting utilities for summarizing calibration metrics in a grid (treatments × metrics).

Function:
- create_metric_grid_heatmaps: Create and save a grid figure of all selected treatments and metrics.
"""
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
import os
from src.plot_style.heatmap import *         # Style constants (font sizes, etc.)
from utils import update_variable_names

def create_metric_grid_heatmaps(
    metrics_by_treatment,             # dict: treatment → (nrmse, mpe, r2, gain) DataFrames
    treatments,                       # list of treatments
    global_limits,                    # dict from compute_global_metric_limits
    output_dir,                       # path to save
    filename_stem,                    # output file root
    y_x_axis_title,
    XTICK_ROTATION, ytick_rotation,
    x_axis_title, y_axis_title,
):
    """
    Plots a grid of heatmaps: one column per treatment, one row per metric.
    Common colorbars are added for each metric (row).
    """
    metric_labels = ["NRMSE"]  # Only plot NRMSE
    num_metrics = 1            # Only the first row
    num_treatments = len(treatments)
    figsize = (FIG_WIDTH, FIG_HEIGHT*0.9)  # Only one row, so height reduced

    fig, axes = plt.subplots(num_metrics, num_treatments,
                             figsize=figsize,
                             sharey=False)

    # Always treat axes as 2D array for consistent indexing
    if num_treatments == 1:
        axes = axes.reshape((num_metrics, 1))
    if num_metrics == 1:
        axes = axes.reshape((1, num_treatments))

    heatmaps_by_metric = {i: [] for i in range(num_metrics)}

    for col, treatment in enumerate(treatments):
        nrmse, mpe, r2, gain = metrics_by_treatment[treatment]
        metric_data = [nrmse]  # Only NRMSE
        vminmax = [
            (global_limits['nrmse_min'], global_limits['nrmse_max'])
        ]
        cmaps = ["YlGnBu"]
        centers = [None]

        for row in range(num_metrics):
            ax = axes[row, col]
            kw = dict(
                annot=True, fmt=f".{NRMSE_DECIMALS}f",
                cmap=cmaps[row], vmin=vminmax[row][0], vmax=vminmax[row][1],
                cbar=False,
                annot_kws={"size": ANNOT_FONTSIZE},
                linewidths=HEATMAP_LINEWIDTH, square=HEATMAP_SQUARE,
                ax=ax
            )
            if centers[row] is not None:
                kw['center'] = centers[row]

            hm = sns.heatmap(metric_data[row], **kw)
            heatmaps_by_metric[row].append(hm)

            # Axis/tick formatting
            ax.set_xticklabels(ax.get_xticklabels(), rotation=XTICK_ROTATION,
                               ha=XTICK_HA, fontsize=TICK_LABEL_FONTSIZE)
            ax.set_yticklabels(ax.get_yticklabels(), rotation=ytick_rotation,
                               fontsize=TICK_LABEL_FONTSIZE)
            ax.set_xlabel('')

            if col == 0:
                ax.set_ylabel(y_axis_title, fontsize=AXIS_LABEL_FONTSIZE, labelpad=AXIS_LABEL_PAD)
            else:
                ax.set_ylabel('')
                ax.set_yticklabels(['']*len(ax.get_yticklabels()))
            if row == 0:
                ax.set_title(treatment, fontsize=TITLE_FONTSIZE, pad=TITLE_PAD)
            else:
                ax.set_title('')

            # Prettier variable names
            current_vars = [tick.get_text() for tick in ax.get_yticklabels()]
            pretty_vars = update_variable_names(current_vars)
            ax.set_yticklabels(pretty_vars, rotation=ytick_rotation, fontsize=TICK_LABEL_FONTSIZE)

    # Add global x-axis title
    fig.supxlabel(x_axis_title, fontsize=AXIS_LABEL_FONTSIZE, y=y_x_axis_title)

    # One shared colorbar per metric row (on right)
    for row_idx, label in enumerate(metric_labels):
        hm = heatmaps_by_metric[row_idx][0]
        pos = axes[row_idx, 0].get_position()
        cax = fig.add_axes([
            0.92,
            pos.y0,
            0.015,
            pos.height
        ])
        cbar = fig.colorbar(hm.collections[0], cax=cax)
        cbar.ax.set_title(label, fontsize=COLORBAR_LABEL_FONTSIZE, pad=10)
        cbar.ax.tick_params(labelsize=COLORBAR_TICK_FONTSIZE)

    #plt.subplots_adjust(wspace=0.2, hspace=0.3, right=0.9)
    # === 8. Adjust horizontal spacing between panels
    plt.subplots_adjust(wspace=0.1)

    output_path = os.path.join(output_dir, f"{filename_stem}_heatmap.{FILE_FORMAT}")
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', facecolor=BACKGROUND_COLOR)
    plt.close()
    print(f"Grid heatmap saved to: {output_path}")
