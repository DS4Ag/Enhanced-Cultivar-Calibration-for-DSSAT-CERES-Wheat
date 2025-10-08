"""
Data preparation utilities for creating heatmap grid visualizations
of model calibration metrics across multiple treatments.

Functions:
- compute_global_metric_limits: Get global color limits for each metric.
- prepare_metrics_by_treatment: Generate pivoted, ordered metrics per treatment.
"""
import pandas as pd

NRMSE_DECIMALS = 2

def compute_global_metric_limits(nrmse_data, mpe_data, r2_data, gain_data, selected_variables, selected_short_labels):
    """Compute global min/max values for each metric, ensuring consistent color scales across treatments."""
    limits = {
        'nrmse_min': nrmse_data.loc[
            nrmse_data['variable'].isin(selected_variables) &
            nrmse_data['short_label'].isin(selected_short_labels),
            'nrmse'].min(),
        'nrmse_max': nrmse_data.loc[
            nrmse_data['variable'].isin(selected_variables) &
            nrmse_data['short_label'].isin(selected_short_labels),
            'nrmse'].max(),
        'mpe_min': mpe_data.loc[
            mpe_data['variable'].isin(selected_variables) &
            mpe_data['short_label'].isin(selected_short_labels),
            'mpe'].min(),
        'mpe_max': mpe_data.loc[
            mpe_data['variable'].isin(selected_variables) &
            mpe_data['short_label'].isin(selected_short_labels),
            'mpe'].max(),
        'r2_min': r2_data.loc[
            r2_data['variable'].isin(selected_variables) &
            r2_data['short_label'].isin(selected_short_labels),
            'r2_1to1'].min(),
        'r2_max': r2_data.loc[
            r2_data['variable'].isin(selected_variables) &
            r2_data['short_label'].isin(selected_short_labels),
            'r2_1to1'].max(),
        'gain_min': gain_data.loc[
            gain_data['variable'].isin(selected_variables) &
            gain_data['short_label'].isin(selected_short_labels),
            'gain'].min(),
        'gain_max': gain_data.loc[
            gain_data['variable'].isin(selected_variables) &
            gain_data['short_label'].isin(selected_short_labels),
            'gain'].max(),
    }
    return limits

def prepare_metrics_by_treatment(
    nrmse_data, mpe_data, r2_data, gain_data,
    treatment, selected_variables, selected_short_labels
):
    """
    Prepare ordered/pivoted metric data (NRMSE, MPE, R², Gain) for a given treatment, maintaining consistent sorting.
    Returns: tuple (nrmse, mpe, r2, gain) as ordered DataFrames.
    """
    # --- Prepare NRMSE ---
    filtered_trt = nrmse_data[
        (nrmse_data['short_label'].isin(selected_short_labels)) &
        (nrmse_data['treatment'] == treatment) &
        (nrmse_data['variable'].isin(selected_variables))
    ]
    pivot_table_trt = filtered_trt.pivot(
        index='variable', columns='short_label', values='nrmse'
    ).round(NRMSE_DECIMALS)
    treatment_order_trt = pivot_table_trt.mean(axis=1).sort_values().index
    calib_order_trt = pivot_table_trt.mean(axis=0).sort_values().index
    pivot_table_ordered_trt = pivot_table_trt.loc[treatment_order_trt, calib_order_trt]

    # --- MPE ---
    mpe_filtered = mpe_data[
        (mpe_data['treatment'] == treatment) &
        (mpe_data['variable'].isin(selected_variables)) &
        (mpe_data['short_label'].isin(selected_short_labels))
    ]
    pivot_mpe_trt = mpe_filtered.pivot(
        index='variable', columns='short_label', values='mpe'
    ).loc[treatment_order_trt, calib_order_trt]

    # --- R² ---
    r2_filtered = r2_data[
        (r2_data['treatment'] == treatment) &
        (r2_data['variable'].isin(selected_variables)) &
        (r2_data['short_label'].isin(selected_short_labels))
    ]
    pivot_r2_trt = r2_filtered.pivot(
        index='variable', columns='short_label', values='r2_1to1'
    ).loc[treatment_order_trt, calib_order_trt]

    # --- Gain ---
    gain_filtered = gain_data[
        (gain_data['treatment'] == treatment) &
        (gain_data['variable'].isin(selected_variables)) &
        (gain_data['short_label'].isin(selected_short_labels))
    ]
    pivot_gain_trt = gain_filtered.pivot(
        index='variable', columns='short_label', values='gain'
    ).loc[treatment_order_trt, calib_order_trt]

    return pivot_table_ordered_trt, pivot_mpe_trt, pivot_r2_trt, pivot_gain_trt
