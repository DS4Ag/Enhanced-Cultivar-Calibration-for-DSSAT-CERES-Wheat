"""
Utility to load clustering CSV datasets into a dictionary of DataFrames.
"""

import pandas as pd
from .config_paths import labels_dict

def load_clustering_data():
    """
    Load all CSVs defined in labels_dict into a dictionary of DataFrames.
    Returns:
        dict: {label: DataFrame}
    """
    return {label: pd.read_csv(path) for path, label in zip(labels_dict.keys(), labels_dict.values())}