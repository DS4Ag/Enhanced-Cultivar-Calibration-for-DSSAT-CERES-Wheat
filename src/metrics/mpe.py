import numpy as np
import pandas as pd

def calculate_mpe(df, group_cols):
    """
    Calculate Mean Percentage Error (MPE) for groups defined by group_cols.

    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe containing:
        - 'value_measured': Observed values
        - 'value_simulated': Model-predicted values
    group_cols : list
        Columns to group by (same as other metric functions)

    Returns:
    --------
    pd.DataFrame with columns:
        - All group_cols columns
        - 'mpe': Mean Percentage Error (%)

    Notes:
    ------
    MPE = mean((predicted - observed) / observed) * 100
    - Positive MPE: Model tends to overpredict
    - Negative MPE: Model tends to underpredict
    """
    results = []

    for group_key, group in df.groupby(group_cols):
        # Extract observed and predicted values
        y_true = group['value_measured']
        y_pred = group['value_simulated']

        # Calculate MPE: mean((predicted - observed) / observed) * 100
        # Handle division by zero by filtering out zero observed values
        non_zero_mask = y_true != 0

        if non_zero_mask.sum() > 0:  # Check if we have non-zero observations
            percentage_errors = ((y_pred[non_zero_mask] - y_true[non_zero_mask]) / y_true[non_zero_mask]) * 100
            mpe = np.mean(percentage_errors)
        else:
            mpe = np.nan  # All observed values are zero

        # Handle group key (single vs multi-column grouping)
        if isinstance(group_key, tuple):
            group_dict = dict(zip(group_cols, group_key))
        else:
            group_dict = {group_cols[0]: group_key}

        # Append results
        results.append({
            **group_dict,
            'mpe': mpe
        })

    return pd.DataFrame(results)