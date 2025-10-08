import numpy as np
import pandas as pd

def compute_grouped_rmse(df, group_cols):
    """
    Compute RMSE between value_measured and value_simulated,
    grouped by specified columns.

    Parameters:
        df (pd.DataFrame): Input dataframe with 'value_measured' and 'value_simulated' columns.
        group_cols (list): List of columns to group by (e.g., ['calibration_method', 'experiment']).

    Returns:
        pd.DataFrame: DataFrame with group columns and RMSE values.
    """

    def rmse(y_true, y_pred):
        return np.sqrt(mean_squared_error(y_true, y_pred))

    grouped_rmse = (
        df.groupby(group_cols)[['value_measured', 'value_simulated']]
        .apply(lambda g: rmse(g['value_measured'], g['value_simulated']))
        .reset_index(name='rmse')
    )

    return grouped_rmse
