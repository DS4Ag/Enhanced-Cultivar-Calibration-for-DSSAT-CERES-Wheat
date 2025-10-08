import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib.ticker import FuncFormatter
from src.plot_style.heatmap import *         # Import style constants (font sizes, etc.)
from utils import update_variable_names

def create_heatmap_plot(
    nrmse_filtered_ordered, mpe_filtered_ordered, r2_filtered_ordered, gain_filtered_ordered,
    output_dir, figure_name, treatment, XTICK_ROTATION, y_x_axis_title, X_TITLE, Y_TITLE
):
    """
    Create and save a 4-panel heatmap figure summarizing all main ecotype calibration metrics.

    Parameters:
    -----------
    nrmse_filtered_ordered : pd.DataFrame
        Data for the NRMSE heatmap.
    mpe_filtered_ordered : pd.DataFrame
        Data for the MPE (bias) heatmap.
    r2_filtered_ordered : pd.DataFrame
        Data for the R² (1:1) heatmap.
    gain_filtered_ordered : pd.DataFrame
        Data for the Gain (slope) heatmap.
    output_dir : str
        Directory where the plot will be saved.
    figure_name : str
        Name to include in the output file (e.g., 'cluster-evaluation').
    treatment : str
        Treatment label for output file.
    """

    # === 1. Set up the figure and axes ===
    # 4 horizontal subplots, one per metric, with shared y-axis for variable names
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(FIG_WIDTH, FIG_HEIGHT), sharey=True)

    # === 2. Define helper to control colorbar decimal formatting ===
    def format_colorbar(x, pos):
        return f'{x:.{NRMSE_DECIMALS}f}'

    # === 3. Plot NRMSE heatmap ===
    # This shows normalized RMSE for every variable x calibration set
    hm1 = sns.heatmap(
        nrmse_filtered_ordered,
        annot=True,
        fmt=f".{NRMSE_DECIMALS}f",
        cmap="YlGnBu",
        cbar_kws={"location": "top", "orientation": "horizontal", 'shrink': COLORBAR_SHRINK, 'format': FuncFormatter(format_colorbar)},
        annot_kws={"size": ANNOT_FONTSIZE},
        linewidths=HEATMAP_LINEWIDTH,
        square=HEATMAP_SQUARE,
        ax=ax1
    )
    # Title and style for the colorbar
    cbar1 = hm1.collections[0].colorbar
    cbar1.ax.set_title('NRMSE', fontsize=COLORBAR_LABEL_FONTSIZE, pad=COLORBAR_LABEL_PAD)
    cbar1.ax.tick_params(labelsize=COLORBAR_TICK_FONTSIZE)

    # X/Y axis label formatting for NRMSE
    ax1.set_yticklabels(ax1.get_yticklabels(), rotation=YTICK_ROTATION, fontsize=TICK_LABEL_FONTSIZE)
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=XTICK_ROTATION, ha=XTICK_HA, fontsize=TICK_LABEL_FONTSIZE)
    ax1.set_xlabel("")
    ax1.set_ylabel(Y_TITLE, fontsize=AXIS_LABEL_FONTSIZE, labelpad=AXIS_LABEL_PAD)
    ax1.set_title('', fontsize=TITLE_FONTSIZE, pad=TITLE_PAD)  # Blank subplot title

    # === 4. Plot MPE (bias) heatmap ===
    # Shows average bias for each variable/calibration set
    hm2 = sns.heatmap(
        mpe_filtered_ordered,
        annot=True,
        fmt=f".{NRMSE_DECIMALS}f",
        cmap="RdBu_r",
        center=0,
        ax=ax2,
        cbar_kws={"location": "top", "orientation": "horizontal", 'shrink': COLORBAR_SHRINK, 'format': FuncFormatter(format_colorbar)},
        annot_kws={"size": ANNOT_FONTSIZE},
        linewidths=HEATMAP_LINEWIDTH,
        square=HEATMAP_SQUARE
    )
    cbar2 = ax2.collections[0].colorbar
    cbar2.ax.set_title('MPE', fontsize=COLORBAR_LABEL_FONTSIZE, pad=COLORBAR_LABEL_PAD)
    cbar2.ax.tick_params(labelsize=COLORBAR_TICK_FONTSIZE)
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=XTICK_ROTATION, ha=XTICK_HA, fontsize=TICK_LABEL_FONTSIZE)
    ax2.set_xlabel("")
    ax2.set_title('', fontsize=TITLE_FONTSIZE, pad=TITLE_PAD)
    ax2.set_ylabel('')

    # === 5. Plot R² (1:1) heatmap ===
    # Shows R² value to 1:1 line for each scenario
    hm3 = sns.heatmap(
        r2_filtered_ordered,
        annot=True,
        fmt=f".{NRMSE_DECIMALS}f",
        cmap="YlGnBu_r",
        center=0,
        ax=ax3,
        cbar_kws={"location": "top", "orientation": "horizontal", 'shrink': COLORBAR_SHRINK, 'format': FuncFormatter(lambda x, pos: f'{x:.2f}')},
        annot_kws={"size": ANNOT_FONTSIZE},
        linewidths=HEATMAP_LINEWIDTH,
        square=HEATMAP_SQUARE
    )
    cbar3 = ax3.collections[0].colorbar
    cbar3.ax.set_title('R²', fontsize=COLORBAR_LABEL_FONTSIZE, pad=COLORBAR_LABEL_PAD)
    cbar3.ax.tick_params(labelsize=COLORBAR_TICK_FONTSIZE)
    ax3.set_xticklabels(ax3.get_xticklabels(), rotation=XTICK_ROTATION, ha=XTICK_HA, fontsize=TICK_LABEL_FONTSIZE)
    ax3.set_xlabel("")
    ax3.set_title('', fontsize=TITLE_FONTSIZE, pad=TITLE_PAD)
    ax3.set_ylabel('')

    # === 6. Plot Gain (slope) heatmap ===
    # Shows slope of actual vs predicted (ideal = 1.0)
    hm4 = sns.heatmap(
        gain_filtered_ordered,
        annot=True,
        fmt=f".{NRMSE_DECIMALS}f",
        cmap="RdBu_r",
        center=1.0,
        vmin=0.5,
        vmax=1.5,
        ax=ax4,
        cbar_kws={"location": "top", "orientation": "horizontal", 'shrink': COLORBAR_SHRINK, 'format': FuncFormatter(format_colorbar)},
        annot_kws={"size": ANNOT_FONTSIZE},
        linewidths=HEATMAP_LINEWIDTH,
        square=HEATMAP_SQUARE
    )
    cbar4 = ax4.collections[0].colorbar
    cbar4.ax.set_title('Gain', fontsize=COLORBAR_LABEL_FONTSIZE, pad=COLORBAR_LABEL_PAD)
    cbar4.ax.tick_params(labelsize=COLORBAR_TICK_FONTSIZE)
    ax4.set_xticklabels(ax4.get_xticklabels(), rotation=XTICK_ROTATION, ha=XTICK_HA, fontsize=TICK_LABEL_FONTSIZE)
    #ax4.set_xlabel(X_TITLE, fontsize=AXIS_LABEL_FONTSIZE, labelpad=AXIS_LABEL_PAD)
    ax4.set_xlabel("")
    ax4.set_title('', fontsize=TITLE_FONTSIZE, pad=TITLE_PAD)
    ax4.set_ylabel('')

    # === 7. Uniformly update y-tick labels using the update_variable_names function
    current_vars = [tick.get_text() for tick in ax1.get_yticklabels()]
    pretty_vars = update_variable_names(current_vars)
    for ax in [ax1, ax2, ax3, ax4]:
        ax.set_yticklabels(pretty_vars, rotation=YTICK_ROTATION, fontsize=TICK_LABEL_FONTSIZE)

    # === 8. Adjust horizontal spacing between panels
    plt.subplots_adjust(wspace=0.1)

    # =====================
    # Add one global x-axis title
    # =====================
    fig.supxlabel(X_TITLE, fontsize=AXIS_LABEL_FONTSIZE, y=y_x_axis_title)

    # === 9. Save the resulting figure to the specified output directory
    output_filename = f'{figure_name}_heatmap_{treatment}.{FILE_FORMAT}'
    plt.savefig(
        os.path.join(output_dir, output_filename),
        dpi=DPI,
        bbox_inches='tight',
        facecolor=BACKGROUND_COLOR
    )
    plt.close()

    print(f"Heatmap saved to: {os.path.join(output_dir, output_filename)}")