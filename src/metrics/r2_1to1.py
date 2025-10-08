import numpy as np
import pandas as pd

def calculate_r2_1to1(df, group_cols):
    """
    Calculate R² against 1:1 line (variance explained by perfect prediction)
    """
    results = []

    for group_key, group in df.groupby(group_cols):
        y_true = group['value_measured']
        y_pred = group['value_simulated']

        # R² = 1 - (RSS/TSS)
        # RSS = sum of squared residuals
        # TSS = total sum of squares (variance in observed)
        rss = np.sum((y_true - y_pred) ** 2)
        tss = np.sum((y_true - np.mean(y_true)) ** 2)

        r2_1to1 = 1 - (rss / tss) if tss != 0 else np.nan

        # Handle group key
        if isinstance(group_key, tuple):
            group_dict = dict(zip(group_cols, group_key))
        else:
            group_dict = {group_cols[0]: group_key}

        results.append({
            **group_dict,
            'r2_1to1': r2_1to1
        })

    return pd.DataFrame(results)