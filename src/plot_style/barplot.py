"""
Centralized plot style settings for parameter change boxplots.
Adjust values here to maintain consistent appearance across figures.
"""

import seaborn as sns

# Box width and spacing
BOX_GAP = 0.2
BAR_GAP = 0.02
BOX_WIDTH = 0.5
outlier_size = 5

# --- Figure size ---
FIGURE_SIZE = (11, 7)

# Marker style for outliers
FLIERPROPS = dict(marker='o', markersize=4, linestyle='none')

# Master ecotype order (keeps subset_C 3rd in plots)
MASTER_ECOTYPE_ORDER = [
    'subset_A', 'subset_B', 'subset_C', 'subset_D',
    'CI0001', 'AZWH18', 'DEFAULT', 'OTM', 'LAI', 'BM-LAI'
]

# Professional color palette with 10 distinct colors
# Subset C will always use the 3rd color in this list (locked across plots)
PALETTE = sns.color_palette("tab10", n_colors=10)

# Font settings
TITLE_FONTSIZE = 18
AXIS_LABEL_FONTSIZE = 18
TICK_LABEL_FONTSIZE = 18
LEGEND_FONTSIZE = 18
XTICK_ROTATION = 0  # Rotation of x-tick labels (set to 0 if no rotation desired)

# Mapping ecotype names to display labels
ECOTYPE_LABELS = {
    'subset_A': 'subset A',
    'subset_B': 'subset B',
    'subset_C': 'subset C',
    'subset_D': 'subset D'
}

# Output and export settings
DPI = 300
FILE_FORMAT = "png"
BACKGROUND_COLOR = "white"