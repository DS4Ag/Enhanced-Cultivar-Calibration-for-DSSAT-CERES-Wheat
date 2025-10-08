
NRMSE_DECIMALS = 2

def prepare_metrics_data(nrmse_data, mpe_data, r2_data, gain_data,
                         treatment, SELECTED_VARIABLES, selected_short_labels):
    """
    Prepare and order data for all four heatmap panels.

    Parameters
    ----------
    nrmse_data, mpe_data, r2_data, gain_data : pd.DataFrame
        Metric DataFrames from step 2
    treatment : str
        Treatment to filter for (e.g., 'WW-23')
    SELECTED_VARIABLES : list
        Variables to include in heatmap
    selected_short_labels : list
        Calibration labels to include

    Returns
    -------
    tuple
        (pivot_table_ordered_trt, mpe_filtered_ordered, r2_filtered_ordered, gain_filtered_ordered)
    """
    # =====================
    # DATA PREPARATION
    # =====================
    # Prepare NRMSE data
    filtered_trt = nrmse_data[
        (nrmse_data['short_label'].isin(selected_short_labels)) &
        (nrmse_data['treatment'] == treatment) &
        (nrmse_data['variable'].isin(SELECTED_VARIABLES))
        ]

    pivot_table_trt = filtered_trt.pivot(
        index='variable',
        columns='short_label',
        values='nrmse'
    ).round(NRMSE_DECIMALS)  # Use config variable

    # Order by performance
    treatment_order_trt = pivot_table_trt.mean(axis=1).sort_values().index
    calib_order_trt = pivot_table_trt.mean(axis=0).sort_values().index
    pivot_table_ordered_trt = pivot_table_trt.loc[treatment_order_trt, calib_order_trt]

    # Prepare MPE data
    mpe_filtered = mpe_data[
        (mpe_data['treatment'] == treatment) &
        (mpe_data['variable'].isin(SELECTED_VARIABLES)) &
        (mpe_data['short_label'].isin(selected_short_labels))
        ]

    pivot_mpe_trt = mpe_filtered.pivot(
        index='variable',
        columns='short_label',
        values='mpe'
    )

    # Apply same ordering as NRMSE plot
    mpe_filtered_ordered = pivot_mpe_trt.loc[treatment_order_trt, calib_order_trt]

    # Prepare R² data
    r2_filtered = r2_data[
        (r2_data['treatment'] == treatment) &
        (r2_data['variable'].isin(SELECTED_VARIABLES)) &
        (r2_data['short_label'].isin(selected_short_labels))
        ]

    pivot_r2_trt = r2_filtered.pivot(
        index='variable',
        columns='short_label',
        values='r2_1to1'
    )

    # Apply same ordering as NRMSE plot
    r2_filtered_ordered = pivot_r2_trt.loc[treatment_order_trt, calib_order_trt]

    # Prepare Gain data
    gain_filtered = gain_data[
        (gain_data['treatment'] == treatment) &
        (gain_data['variable'].isin(SELECTED_VARIABLES)) &
        (gain_data['short_label'].isin(selected_short_labels))
        ]

    pivot_gain_trt = gain_filtered.pivot(
        index='variable',
        columns='short_label',
        values='gain'
    )

    # Apply same ordering as NRMSE plot
    gain_filtered_ordered = pivot_gain_trt.loc[treatment_order_trt, calib_order_trt]

    return pivot_table_ordered_trt, mpe_filtered_ordered, r2_filtered_ordered, gain_filtered_ordered