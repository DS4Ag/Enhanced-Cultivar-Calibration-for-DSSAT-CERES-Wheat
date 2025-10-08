import os
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
import re
from matplotlib.lines import Line2D
import numpy as np

from src.plot_style.ts_panel import *  # Assuming this contains all style constants used
from utils import update_variable_names


def _plot_single_1x3(
    axarr,
    combined_plantgro_df,
    wht_dfs,
    treatments,
    cultivars,
    variable_name,
    y_axis_label
):
    """
    Draw a single 1x3 grid of growth curves with mean ± SD and measurement bands.

    Parameters:
    - axarr: 1x3 array of matplotlib Axes for subplots.
    - combined_plantgro_df: DataFrame with simulation data (includes 'short_label', 'treatment', 'genotype', variable_name, 'DAP').
    - wht_dfs: dict treatment -> measurement DataFrame.
    - treatments: list of 3 treatment names to assign to subplots.
    - cultivars: list of cultivar genotype names to average over.
    - variable_name: string name of trait column.
    - y_axis_label: prettified string for y-axis label.
    """
    # Unique calibration codes with assigned color and line style
    calib_codes = list(combined_plantgro_df['short_label'].unique())
    calib_legend_info = {}
    for j, calib_code in enumerate(calib_codes):
        line_color = COLOR_PALETTE[j % len(COLOR_PALETTE)]
        linestyle = LINESTYLES[j % len(LINESTYLES)]
        calib_legend_info[calib_code] = (line_color, linestyle)

    # Plot each treatment into corresponding subplot
    for idx, treatment in enumerate(treatments):
        ax = axarr.flat[idx]

        # Plot calibration means ± SD
        for calib_code in calib_codes:
            calib_df = combined_plantgro_df[
                (combined_plantgro_df['treatment'] == treatment) &
                (combined_plantgro_df['genotype'].isin(cultivars)) &
                (combined_plantgro_df['short_label'] == calib_code)
            ]
            if calib_df.empty:
                continue

            stats_df = (
                calib_df.groupby("DAP")
                .agg(mean_val=(variable_name, "mean"), sd_val=(variable_name, "std"))
                .reset_index()
            )
            stats_df["sd_val"] = stats_df["sd_val"].fillna(0.0)

            line_color, linestyle = calib_legend_info[calib_code]

            ax.plot(
                stats_df["DAP"], stats_df["mean_val"],
                color=line_color,
                linestyle=linestyle,
                linewidth=LINE_WIDTH,
            )
            ax.fill_between(
                stats_df["DAP"],
                stats_df["mean_val"] - stats_df["sd_val"],
                stats_df["mean_val"] + stats_df["sd_val"],
                color=line_color,
                alpha=MEAN_FILL_ALPHA,
            )

        # Overlay measurement ± SD bands if available
        wht_df = wht_dfs.get(treatment)
        if wht_df is not None and variable_name in wht_df.columns and wht_df[variable_name].dropna().size > 0:
            meas_stats = (
                wht_df[wht_df['genotype'].isin(cultivars)]
                .groupby("DAP")
                .agg(mean_val=(variable_name, "mean"), sd_val=(variable_name, "std"))
                .reset_index()
            )
            meas_stats["sd_val"] = meas_stats["sd_val"].fillna(0.0)

            ax.fill_between(
                meas_stats["DAP"],
                meas_stats["mean_val"] - meas_stats["sd_val"],
                meas_stats["mean_val"] + meas_stats["sd_val"],
                color=MEAS_POINT_COLOR,
                alpha=0.25,
            )

        # Annotate treatment label on subplot
        ax.text(
            x=0.03,
            y=0.97,
            s=re.sub(r"([A-Z]+)(\d+)", r"\1-\2", treatment),
            transform=ax.transAxes,
            fontsize=TITLE_FONTSIZE,
            va="top",
            ha="left"
        )

        # Tick formatting for readability
        ax.tick_params(axis='x', rotation=XTICK_ROTATION, labelsize=TICK_LABEL_FONTSIZE, width=2, length=6)
        ax.tick_params(axis='y', labelsize=TICK_LABEL_FONTSIZE, width=2, length=6)

        # Make all plot borders visible
        for spine in ax.spines.values():
            spine.set_visible(True)


def create_growth_panel_comparison(
    growth_data_list,
    measurement_data_list,
    treatments,
    cultivars,
    var_names,
    panel_labels,
    output_dir,
    file_label=None
):
    """
    Create a figure with two vertically stacked 1x3 panels with shared y-axis in each panel.

    Nested GridSpec approach allows controlling spacing between panels without
    affecting shared axes, panel labels, or legends.
    """
    y_axis_label_dict = {
        'LAID': 'Leaf area index',
        'CWAD': 'Aboveground biomass at maturity (kg/ha)',
        'RDPD': 'Root depth (m)',
        'AWAD': 'Assimilate production rate (kg/ha/day)',
        'RWAD': 'Root weight (kg/ha)',
        'SWXD': 'Extractable water (mm)',
        'LWAD': 'Leaf weight (kg/ha)',
        'PARUD': 'PAR utilization efficiency (g/MJ)'
    }
    formatted_y_labels = [
        update_variable_names(y_axis_label_dict.get(vn, vn))[0]
        for vn in var_names
    ]

    # Create figure
    fig = plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT))

    # Outer GridSpec: 2 rows (panel a and panel b)
    outer_gs = GridSpec(
        nrows=2,
        ncols=1,
        figure=fig,
        height_ratios=[1, 1],
        hspace=0.25  # vertical space between top and bottom panel
    )

    # Store axes for each panel
    panel_axes = []

    for i in range(2):
        # Inner 1x3 GridSpec for each panel
        inner_gs = GridSpecFromSubplotSpec(
            1, 3,
            subplot_spec=outer_gs[i],
            wspace=0.15
        )

        # Create axes array as NumPy array for compatibility
        axes_array = np.empty((1, 3), dtype=object)
        for c in range(3):
            if c == 0:
                axes_array[0, c] = fig.add_subplot(inner_gs[0, c])
            else:
                axes_array[0, c] = fig.add_subplot(inner_gs[0, c], sharey=axes_array[0, 0])
                plt.setp(axes_array[0, c].get_yticklabels(), visible=False)

        # Only bottom row exists, so keep x-axis labels
        # for c in range(3):
        #     axes_array[0, c].tick_params(labelbottom=True)
        # Hide x-axis labels for all by default
        for c in range(3):
            axes_array[0, c].tick_params(labelbottom=False)

        # Only show x-axis labels for the bottom panel (i == 1)
        if i == 1:
            for c in range(3):
                axes_array[0, c].tick_params(labelbottom=True)


        # Plot the panel
        _plot_single_1x3(
            axarr=axes_array,
            combined_plantgro_df=growth_data_list[i],
            wht_dfs=measurement_data_list[i],
            treatments=treatments,
            cultivars=cultivars,
            variable_name=var_names[i],
            y_axis_label=formatted_y_labels[i]
        )

        # Add panel label (a/b)
        axes_array[0][0].text(
            -0.11, 1.1,
            panel_labels[i],
            transform=axes_array[0][0].transAxes,
            fontsize=TITLE_FONTSIZE + 7,
            fontweight='bold',
            va='top',
            ha='left'
        )

        panel_axes.append(axes_array)

    # Flatten axes for convenience if needed
    axes = [ax for panel in panel_axes for row in panel for ax in row]

    # Prepare legend handles (same as original code)
    calib_codes = list(growth_data_list[0]['short_label'].unique())
    calib_legend_info = {}
    for j, calib_code in enumerate(calib_codes):
        line_color = COLOR_PALETTE[j % len(COLOR_PALETTE)]
        linestyle = LINESTYLES[j % len(LINESTYLES)]
        calib_legend_info[calib_code] = (line_color, linestyle)

    legend_handles = [
        Line2D([0], [0], color=line_color, linestyle=linestyle,
               linewidth=LINE_WIDTH, label=f"{calib_code} (±SD)")
        for calib_code, (line_color, linestyle) in calib_legend_info.items()
    ]

    # Add measurement legend handle if present
    meas_present = any(
        md.get(treatment) is not None and
        var in md[treatment].columns and
        md[treatment][var].dropna().size > 0
        for md, var in zip(measurement_data_list, var_names)
        for treatment in treatments
    )
    if meas_present:
        legend_handles.append(Line2D(
            [0], [0],
            color=MEAS_POINT_COLOR,
            linestyle='-',
            linewidth=LINE_WIDTH,
            alpha=0.6,
            label="Measurements (±SD)"
        ))

    # Place shared legend
    fig.legend(
        handles=legend_handles,
        loc='lower center',
        bbox_to_anchor=(0.5, -0.07),
        ncol=max(3, len(legend_handles)),
        fontsize=LEGEND_FONT_SIZE,
        framealpha=0.9,
        title='Ecotype',
        title_fontsize=LEGEND_FONT_SIZE,
    )

    # Adjust margins
    fig.subplots_adjust(top=0.92, bottom=0.12, left=0.07, right=0.97)

    # Shared y-axis labels
    fig.text(-0.01, 0.72, formatted_y_labels[0], va='center', ha='center',
             rotation='vertical', fontsize=AXIS_LABEL_FONTSIZE)
    fig.text(-0.01, 0.32, formatted_y_labels[1], va='center', ha='center',
             rotation='vertical', fontsize=AXIS_LABEL_FONTSIZE)

    # Global x-axis label
    fig.text(0.5, 0.05, 'Days after planting', va='center', ha='center',
             fontsize=AXIS_LABEL_FONTSIZE)

    # Save figure
    os.makedirs(output_dir, exist_ok=True)
    filename = f"Figure-6_time-series_{'_'.join(var_names)}_{len(cultivars)}_Ecotypes"
    if file_label:
        filename += f"_{file_label}"
    filename += f".{FILE_FORMAT}"

    fig.savefig(os.path.join(output_dir, filename),
                dpi=DPI, bbox_inches='tight', facecolor=BACKGROUND_COLOR)
    print(f"Saved growth stacked panel plot to {os.path.join(output_dir, filename)}")
