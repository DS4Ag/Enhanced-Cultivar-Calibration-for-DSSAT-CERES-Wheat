"""
General-purpose module to create mean barplots (± standard error) of parameter changes
by ecotype and analysis step, with customizable intra-group bar gap (BAR_GAP).
All plotting styles are controlled via src/plot_style/boxplot.py for consistency.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.plot_style.barplot import *  # Centralized style constants for all parameter plots
import numpy as np

def create_parameter_barplot(BASE_DATA, BASE_OUTPUT, DATAFILE_NAME, PARAMS, STEP_ORDER, Y_LIMITS, LEGEND_TITLES):
    """
    Workflow to process multi-step, multi-ecotype parameter calibration data
    and produce mean ± standard error barplots for each parameter.

    Steps:
    1. Load crop parameter data from CSV, filter and compute % change from baseline for each row.
    2. For each analysis/calibration step, compute group means and standard error per ecotype/parameter.
    3. Plot means and error bars as grouped barplots for each step, with configurable gap (BAR_GAP) between bars.
    4. Style axes, legends, and subplot/figure layout for publication quality.
    5. Save the barplot to the output directory.

    Parameters
    ----------
    BASE_DATA : str
        Path to directory with CSV input file.
    BASE_OUTPUT : str
        Directory where the plot will be saved.
    DATAFILE_NAME : str
        Input filename (full or relative to BASE_DATA).
    PARAMS : list of str
        List of crop model parameter columns to analyze.
    STEP_ORDER : list of str
        List of step names for each subplot row (e.g., ['Cultivar calibration', ...]).
    Y_LIMITS: list of tuple
        List of (Y_BOTTOM, Y_TOP) tuples for each subplot row in STEP_ORDER.

    Returns
    -------
    None (saves figure to BASE_OUTPUT)
    """

    # === Load and prepare data ===
    df = pd.read_csv(os.path.join(BASE_DATA, DATAFILE_NAME))

    # Extract "initial" values for use as baseline (Yecora_Rojo, CI0001, step: Initial_value)
    initial_row = df[
        (df['step'] == 'Initial_value') &
        (df['cultivar'] == 'Yecora_Rojo') &
        (df['ecotype'] == 'CI0001')
    ]
    initial_vals = initial_row[PARAMS].iloc[0].astype(float)

    # Exclude the baseline row from further calculations
    df_calc = df[~(
        (df['step'] == 'Initial_value') &
        (df['cultivar'] == 'Yecora_Rojo') &
        (df['ecotype'] == 'CI0001')
    )].copy()

    # Compute percent change for each parameter relative to initial value
    for p in PARAMS:
        df_calc[f'{p}_pctchange'] = (df_calc[p].astype(float) - initial_vals[p]) / initial_vals[p] * 100

    # Duplicate subset_C rows across steps for direct comparison as in original workflow
    subsetC_rows = df_calc[
        (df_calc['step'] == 'Cultivar calibration') &
        (df_calc['ecotype'] == 'subset_C')
    ].copy()
    for target_step in ["Ecotype assessment", "Calibrarion time-series "]:
        sc_copied = subsetC_rows.copy()
        sc_copied['step'] = target_step
        df_calc = pd.concat([df_calc, sc_copied], ignore_index=True)

    # === Convert to long format for plotting ===
    df_long = df_calc.melt(
        id_vars=['step', 'ecotype'],
        value_vars=[f'{p}_pctchange' for p in PARAMS],
        var_name='Parameter',
        value_name='Percent Change'
    )
    df_long['Parameter'] = df_long['Parameter'].str.replace('_pctchange', '')

    # Scale P1V only for 'Ecotype assessment' step (per original code/notes)
    scaling_rows = (df_long['step'] == 'Ecotype assessment') & (df_long['Parameter'] == 'P1V')
    df_long.loc[scaling_rows, 'Percent Change'] = df_long.loc[scaling_rows, 'Percent Change'] / 20

    # === Set up the figure with one barplot per analysis/calibration step ===
    n_steps = len(STEP_ORDER)
    fig, axes = plt.subplots(nrows=n_steps, ncols=1, figsize=(FIGURE_SIZE[0], FIGURE_SIZE[1] * 1.5), sharey=False)
    subplot_labels = ['(a)', '(b)', '(c)', '(d)', '(e)'][:n_steps]  # Adjust as needed

    # === Prepare to collect summary stats for all steps and save to CSV ===
    all_summaries = []  # will hold DataFrames for all steps

    # Main loop through each subplot ("step")
    for idx, (ax, step) in enumerate(zip(axes, STEP_ORDER)):
        data = df_long[df_long['step'] == step].copy()

        # Enforce ecotype plotting order, always keeping 'subset_C' in a fixed spot
        plot_order = [e for e in MASTER_ECOTYPE_ORDER if e in data['ecotype'].unique()]
        if 'subset_C' in plot_order:
            plot_order.remove('subset_C')
            plot_order.insert(2, 'subset_C')  # always 3rd

        data['ecotype'] = pd.Categorical(data['ecotype'], categories=plot_order, ordered=True)

        # === Group by ecotype & parameter for mean/se calculation ===
        summary = (
            data.groupby(['Parameter', 'ecotype'], observed=True)['Percent Change']
                .agg(['mean', 'sem'])
                .reset_index()
        )

        summary['step'] = step  # add explicit step column for later concatenation
        all_summaries.append(summary)

        # === Color map per ecotype (like in the boxplot ver.) ===
        cb_palette = sns.color_palette("deep")
        COLOR_POOL = [
            [cb_palette[0], cb_palette[1], cb_palette[2], cb_palette[3]], # Row 1
            [cb_palette[4], cb_palette[5], cb_palette[6]],                # Row 2
            [cb_palette[7], cb_palette[8], cb_palette[9]],                # Row 3
        ]
        FIXED_COLOR = cb_palette[3]
        unique_ecotypes = list(data['ecotype'].cat.categories)
        color_map = {}
        pool_idx = 0
        for eco in unique_ecotypes:
            if eco == "subset_C" and idx < 2:
                color_map[eco] = FIXED_COLOR
            elif eco == "subset_C" and idx == 2:  # On last row, rename later to BM
                color_map[eco] = FIXED_COLOR
            else:
                color_map[eco] = COLOR_POOL[idx][pool_idx % len(COLOR_POOL[idx])]
                pool_idx += 1

        # ==== Generate grouped bar positions with intra-group gap ====
        n_params = len(PARAMS)
        n_ecos = len(plot_order)
        total_bar_width = 0.7
        group_gap = 0
        bar_gap = BAR_GAP
        bar_width = (total_bar_width - (n_ecos - 1) * bar_gap) / n_ecos
        x_base = np.arange(n_params)

        for j, eco in enumerate(plot_order):
            vals = summary[summary['ecotype'] == eco]
            means = [vals[vals['Parameter']==p]['mean'].values[0] if not vals[vals['Parameter']==p].empty else float('nan') for p in PARAMS]
            errors = [vals[vals['Parameter']==p]['sem'].values[0] if not vals[vals['Parameter']==p].empty else float('nan') for p in PARAMS]
            base_offset = -0.5 * ((n_ecos - 1) * (bar_width + bar_gap))
            bar_pos = x_base + base_offset + j * (bar_width + bar_gap)
            ax.bar(
                bar_pos, means, width=bar_width, color=color_map[eco], label=ECOTYPE_LABELS.get(eco, eco),
                yerr=errors, capsize=4, alpha=0.87, edgecolor="none", linewidth=0.7, error_kw=dict(lw=1.1)
            )

        # Reference line
        ax.axhline(0, color='gray', linestyle='--', linewidth=0.9)

        # ✅ Apply custom y-limits for this subplot
        if idx < len(Y_LIMITS):
            y_bottom, y_top = Y_LIMITS[idx]
            ax.set_ylim(y_bottom, y_top)

        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_xticks(x_base)
        param_labels = ['P1V**' if p == 'P1V' and idx == n_steps-1 else p for p in PARAMS]
        if idx == n_steps-1:
            ax.set_xticklabels(param_labels, rotation=XTICK_ROTATION, ha='center', fontsize=TICK_LABEL_FONTSIZE)
        else:
            ax.set_xticklabels([''] * len(PARAMS))
        ax.set_title(subplot_labels[idx], loc='left', fontsize=TITLE_FONTSIZE, pad=5, fontweight='bold')
        ax.tick_params(axis='y', labelsize=TICK_LABEL_FONTSIZE)
        handles, labels = ax.get_legend_handles_labels()
        new_labels = [ECOTYPE_LABELS.get(l, l) for l in labels]
        if idx == 2:
            new_labels = ['BM*' if l in ('subset C', 'subset_C') else l for l in new_labels]
        leg = ax.legend(
            handles=handles, labels=new_labels, title='Ecotype',
            loc='center left', bbox_to_anchor=(1.01, 0.5),
            borderaxespad=0., alignment='left' , fontsize=LEGEND_FONTSIZE
        )
        leg.set_title(LEGEND_TITLES[idx], prop={"size": LEGEND_FONTSIZE})

    # === Shared formatting, labels, and layout adjustments ===
    fig.text(0.40, 0.02, "Parameter", ha='center', va='center', fontsize=AXIS_LABEL_FONTSIZE)
    fig.text(0.02, 0.5, "Parameter adjustment (%)", ha='center', va='center', rotation='vertical', fontsize=AXIS_LABEL_FONTSIZE)
    fig.subplots_adjust(hspace=0.8)
    plt.tight_layout(rect=[0.04, 0.03, 1, 1], h_pad=3.0)

    # Ativate to make plot borders (top, bottom, left, right) of each subplot (the axes spines) visible
    # sns.despine()

    output_path = os.path.join(BASE_OUTPUT, f"Figure-3_parameters_barplot.{FILE_FORMAT}")
    fig.patch.set_facecolor(BACKGROUND_COLOR)
    plt.savefig(output_path, dpi=DPI, format=FILE_FORMAT, facecolor=BACKGROUND_COLOR)
    plt.close()
    print(f"Parameter barplot saved to: {output_path}")