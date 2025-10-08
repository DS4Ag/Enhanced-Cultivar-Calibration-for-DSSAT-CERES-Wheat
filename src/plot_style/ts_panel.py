"""
Centralized plot style constants for time series visualization.

This file defines colors, line styles, font sizes,
marker sizes, and other appearance-related constants
for consistent plotting aesthetics across the project.
"""

# --- Colors cycle for up to 4 calibration groups ---
CALIBRATION_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

# CALIBRATION_COLORS = [
#     "#E69F00",  # orange
#     "#CC79A7",  # magenta
#     "#009E73",  # green
#     "#0072B2"  # dark blue
#     # "#56B4E9",  # blue
#     # "#D55E00",  # red-orange
#     # "#CC79A7",  # magenta
#     # "#F0E442"   # yellow
# ]

# --- Line styles cycle for up to 4 calibration groups ---
CALIBRATION_LINESTYLES = [(None, None), (4, 2), (2, 2, 8, 2), (1, 1)]

# --- Font sizes for titles, axis labels, ticks, and legends ---
TITLE_FONTSIZE = 24
AXIS_LABEL_FONTSIZE = 24
TICK_LABEL_FONTSIZE = 24
LEGEND_FONT_SIZE = 24

# --- Marker style parameters ---
MARKER_SIZE = 24
MARKER_EDGE_WIDTH = 2
MARKER_ALPHA = 0.9

# --- Axis and tick parameters ---
YTICK_ROTATION = 0
XTICK_ROTATION = 0
XTICK_HA = "right"
TITLE_PAD = 20
AXIS_LABEL_PAD = 15

# --- Line width for plots ---
LINE_WIDTH = 2.0

# ---  Figure layout configuration ---
FIG_WIDTH = 18
FIG_HEIGHT = 13.4

# --- Save figure options ---
DPI = 300
FILE_FORMAT = 'png'
BACKGROUND_COLOR = 'white'

# --- Axis label padding ---
X_LABELPAD = 14
Y_LABELPAD = 14

# -------------------------
# Added style constants used by growth-comparison plotting
# -------------------------

# color palette for cultivars / series (up to 14 unique entries)
COLOR_PALETTE = [
    "#1f77b4", "#d62728", "#2ca02c", "#ff7f0e",
    "#9467bd", "#17becf", "#8c564b", "#e377c2",
    "#7f7f7f", "#bcbd22", "#393b79", "#ad494a",
    "#637939", "#8c6d31",
]

# marker list for cultivars (keeps one-to-one mapping to palette indices)
MARKER_LIST = ['o', 's', '^', 'D', 'v', '*', 'P', 'X', 'h', '8', 'H', '<', '>', 'p']

# richer linestyle set (strings + dash tuples)
LINESTYLES = [
    '-', '--', '-.', ':',
    (0, (1, 1)),          # densely dotted
    (0, (5, 1)),          # long solid with tiny gaps
    (0, (3, 5, 1, 5)),    # dash-dot-dot
    (0, (5, 10)),         # widely dashed
    (0, (3, 1, 1, 1)),    # tight dash-dot
    (0, (3, 10, 1, 10)),  # spaced dash-dot
    (0, (1, 10)),         # sparse dotted
    (0, (7, 3)),          # long dash, short gap
    (0, (2, 4, 2, 4)),    # even dash spacing
    (0, (4, 4, 1, 4)),    # dash-dot variant
]

# default colors used for the aggregated mean and measurement points
MEAN_LINE_COLOR = COLOR_PALETTE[0]
MEAN_FILL_ALPHA = 0.2
MEAS_POINT_COLOR = "#d62728"