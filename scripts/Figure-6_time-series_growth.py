import sys
import os
import pandas as pd

# Add the 'src' directory to sys.path so we can import local modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Import data loading and plotting functions from src
from ts_get_data import load_prepare_time_series_data
from ts_GROWTH_comparison_panel import create_growth_panel_comparison


# Define base directories for input data and output figure saving
BASE_DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/4_impact_assessmen_time-series data'))
BASE_OUTPUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../output/'))
dssat_wheat_dir = '../data/DSSAT48/Wheat'  # Relative to current script

# List of calibration codes to load data for
calibration_code_list = ['cultivar_subset_c', 'cultivar_CI0001', 'cultivar_AZWH18']

# List of treatments; these map to subplots (4 treatments = 2x2 grid)
treatments = ['WW23', 'DR22', 'DR23']

# List of cultivar genotypes to average across
cultivars = ['G-1', 'G-2', 'G-3', 'G-4', 'G-5', 'G-6', 'G-7', 'G-8',
             'G-9', 'G-10', 'G-11', 'G-12', 'G-13', 'G-14']

# Variables/traits to plot; each corresponds to one stacked panel (one top, one bottom)
var_names = ['LWAD', 'RWAD']

# Panel labels for figure annotation (top-left of each panel)
panel_labels = ['(a)', '(b)']

# Prepare containers to accumulate data for each trait/panel
growth_data_list = []       # List of pooled PlantGro DataFrames for each trait
measurement_data_list = []  # List of dicts mapping treatment -> measurement df (for each trait)

# Loop over variable names to load and combine data for each trait separately
for variable_name in var_names:
    all_plantgro_dfs = []      # Per trait: list of PlantGro dfs (one per treatment)
    treatment_wht_dfs = {}     # Dict treatment -> measurements DataFrame

    # Load data for all treatments and calibrations, concatenate accordingly
    for treatment in treatments:
        treatment_plantgro_dfs = []
        treatment_wht_dfs_list = []

        # Load PlantGro and measurement data for each calibration and treatment
        for calib_code in calibration_code_list:
            plantgro_df, wht_full_df = load_prepare_time_series_data(
                base_data_dir=BASE_DATA,
                dssat_wheat_dir=dssat_wheat_dir,
                calibration_code=calib_code,
                variable_name=variable_name,
                treatment=treatment
            )
            treatment_plantgro_dfs.append(plantgro_df)
            treatment_wht_dfs_list.append(wht_full_df)

        # Concatenate all calibration PlantGro data for this treatment
        combined_plantgro_df = pd.concat(treatment_plantgro_dfs, ignore_index=True)
        all_plantgro_dfs.append(combined_plantgro_df)

        # Concatenate all calibration measurement data for this treatment into one DataFrame
        treatment_wht_dfs[treatment] = pd.concat(treatment_wht_dfs_list, ignore_index=True)

    # Concatenate data for all treatments (for the trait) into a single DataFrame
    combined_plantgro_df_all = pd.concat(all_plantgro_dfs, ignore_index=True)

    # Add combined data and measurement dict to lists for plotting function
    growth_data_list.append(combined_plantgro_df_all)
    measurement_data_list.append(treatment_wht_dfs)

# Call the plotting function with all prepared data and config
create_growth_panel_comparison(
    growth_data_list=growth_data_list,             # List of DataFrames per trait
    measurement_data_list=measurement_data_list,   # List of dicts per trait
    treatments=treatments,
    cultivars=cultivars,
    var_names=var_names,
    panel_labels=panel_labels,
    output_dir=BASE_OUTPUT,
    file_label=None
)