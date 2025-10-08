"""
Script entry point to create parameter change barplots (mean ± SE) for wheat calibration.
Edit settings below for your specific data location, and parameter/step selection.
"""

import sys
import os

# Allow imports from src/ wherever this script is run
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from barplot_parameters import create_parameter_barplot

# --- User Settings: configure for different runs/locations ---
BASE_DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/cultivar_parameters'))
BASE_OUTPUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../output/'))
DATAFILE_NAME = 'CULTIVAR_parameters.csv'
PARAMS = ['P1V', 'P1D', 'P5', 'G1', 'G2', 'G3', 'PHINT']  # List ALL parameters/columns to show as bars
STEP_ORDER = ['Cultivar calibration', 'Ecotype assessment', 'Calibrarion time-series ']
# Custom legend titles for each subplot
LEGEND_TITLES = [
    "Cluster-derived ecotype",  # row 1, idx=0
    "Ecotype baseline",          # row 2, idx=1
    "Data combination"          # row 3, idx=2
]

# Y-axis limits
# Y_TOP = 130
# Y_BOTTOM = -90
Y_LIMITS = [(-60, 70), (-90, 140), (-60, 70)]
# ------------------------------------------------------------

if __name__ == '__main__':
    create_parameter_barplot(
        BASE_DATA,
        BASE_OUTPUT,
        DATAFILE_NAME,
        PARAMS,
        STEP_ORDER,
        Y_LIMITS,
        LEGEND_TITLES
    )