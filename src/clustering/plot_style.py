import matplotlib as mpl
from matplotlib.font_manager import FontProperties

# === Font & Layout Settings ===
font_name = 'Times New Roman'
fontsize_title = 30
fontsize_medium = 26
fontsize_tick = 26
fontsize_small = 18
fontsize_big = 26

# === Grid Style ===
grid_linestyle = '--'
grid_linewidth = 0.1
grid_alpha = 0.7

# === Marker & Line Appearance ===
line_color = '#0099b4'
line_width = 2
marker_style = 'o'
marker_size = 8

# === Threshold Line Styles ===
above_threshold_color = '#555555'
threshold_line_style_list = [
    '--', ':', '-.', (0, (5, 10)), (0, (3, 1, 1, 1))
]

# === PCA/Cluster Plot Settings ===
marker_size_pca = 120
edgecolor = 'k'
line_width_pca = 1
marker_styles = ['o', 's', '^', 'D', 'p', 'v', '<', '>', '*', '+', 'h']

# === Dendrogram Style ===
leaf_rotation = 0
color_threshold = 0

# === Legend Font ===
legend_font = FontProperties(family=font_name, size=fontsize_big)
legend_title_font = FontProperties(family=font_name, size=fontsize_big)

# === Method Colors ===
method_colors = {
    'wcss': '#E66100',
    'silhouette': '#0C7BDC',
    'gap': 'gray'  # ← 'gap' unused
}

# === Set Global Font ===
mpl.rcParams['font.family'] = font_name
mpl.rcParams['xtick.labelsize'] = fontsize_big
mpl.rcParams['ytick.labelsize'] = fontsize_big
mpl.rcParams['font.weight'] = 'normal'