import numpy as np
import pandas as pd
import scipy

def calculate_gain(df, group_cols):
    """
    Calculate gain (slope of actual vs predicted regression)
    with handling for constant predictions
    """
    results = []

    for group_key, group in df.groupby(group_cols):
        y_true = group['value_measured']
        y_pred = group['value_simulated']

        # Skip groups with < 2 observations
        if len(y_true) < 2:
            gain = np.nan
        # Check if predictions are constant
        elif np.all(y_pred == y_pred.iloc[0]):
            gain = np.nan
        else:
            try:
                slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(y_pred, y_true)
                gain = slope
            except ValueError:
                gain = np.nan

        # Handle group key
        if isinstance(group_key, tuple):
            group_dict = dict(zip(group_cols, group_key))
        else:
            group_dict = {group_cols[0]: group_key}

        results.append({
            **group_dict,
            'gain': gain
        })

    return pd.DataFrame(results)