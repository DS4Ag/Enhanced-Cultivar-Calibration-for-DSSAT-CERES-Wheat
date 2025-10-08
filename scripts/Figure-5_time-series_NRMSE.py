"""
Script entry point to create a grid of multi-metric, multi-treatment heatmaps for wheat model calibration.
Uses:
- data_preparation_grid.py (data utilities)
- heatmap_plot_grid.py (plotting function)
- metric calculation utilities and variable name mapping from src/
"""
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from utils import load_and_process_overview
from variable_mapping import treatments_dic, variable_name_mapping
from metrics import compute_grouped_nrmse, calculate_mpe, calculate_r2_1to1, calculate_gain
from data_preparation_grid import compute_global_metric_limits, prepare_metrics_by_treatment
from heatmap_plot_grid_NRMSE import create_metric_grid_heatmaps

# =====================
# USER-DEFINED VARIABLES
# =====================

BASE_DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/4_impact_assessmen_time-series data'))
BASE_OUTPUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../output/'))

treatments = ['WW-23', 'DR-22', 'DR-23', 'HT-22']

SELECTED_VARIABLES = [
    'Anthesis (DAP)', 'Maturity (DAP)', 'Grain yield (kg/ha)',
    'Grain unit weight (g)', 'Grains m2', 'Harvest index',
    'Maximum leaf area index', 'Aboveground biomass at maturity (kg/ha)',
    'Vegetative biomass at maturity (kg/ha)',
    'Grain nitrogen content (kg/ha)', 'Grain nitrogen content (%)'
]

calibration_code_list = [
    'BM-ts', 'BM-ts_LAI-ts',
    'LAI-ts', 'No-ts'
]

input_files = {code: os.path.join(BASE_DATA, code, 'OVERVIEW.OUT') for code in calibration_code_list}
yaml_files = {code: os.path.join(BASE_DATA, code, 'config.yaml') for code in calibration_code_list}

if __name__ == '__main__':
    overview_data = load_and_process_overview(
        calibration_code_list,
        BASE_DATA,
        treatments_dic,
        variable_name_mapping
    )

    group_cols = ['variable', 'calibration_method', 'short_label', 'long_label', 'treatment']
    nrmse_data = compute_grouped_nrmse(overview_data, group_cols, norm_method='mean')

    # # Set Pandas display options to show all rows and columns
    # output_path = os.path.join(BASE_OUTPUT, 'nrmse_data.csv')
    # nrmse_data.to_csv(output_path)

    selected_short_labels_list = nrmse_data['short_label'].unique().tolist()
    selected_short_labels = selected_short_labels_list

    mpe_data = calculate_mpe(overview_data, group_cols)
    r2_data = calculate_r2_1to1(overview_data, group_cols)
    gain_data = calculate_gain(overview_data, group_cols)

    # --- Compute global colorbar limits for all treatments ---
    global_limits = compute_global_metric_limits(
        nrmse_data, mpe_data, r2_data, gain_data, SELECTED_VARIABLES, selected_short_labels
    )

    # --- Collect per-treatment prepared data ---
    metrics_by_treatment = {}
    for treatment in treatments:
        piv_nrmse, piv_mpe, piv_r2, piv_gain = prepare_metrics_by_treatment(
            nrmse_data, mpe_data, r2_data, gain_data,
            treatment, SELECTED_VARIABLES, selected_short_labels
        )
        metrics_by_treatment[treatment] = (piv_nrmse, piv_mpe, piv_r2, piv_gain)

    # --- Plot the grid heatmaps ---
    create_metric_grid_heatmaps(
        metrics_by_treatment=metrics_by_treatment,
        treatments=treatments,
        global_limits=global_limits,
        output_dir=BASE_OUTPUT,
        filename_stem='Figure-5_time-series_NRMSE',
        XTICK_ROTATION=45,
        ytick_rotation=0,
        y_x_axis_title=0.01,
        x_axis_title='Data subset',
        y_axis_title='Evaluated variable'
    )
