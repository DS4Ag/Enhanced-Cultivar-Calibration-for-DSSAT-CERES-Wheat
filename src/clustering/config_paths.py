"""
Input and output paths used across clustering analysis.
"""

# Input files
labels_dict = {
    '../data/clustering/subset_a.csv': 'A',
    '../data/clustering/subset_b.csv': 'B',
    '../data/clustering/subset_c.csv': 'C',
    '../data/clustering/subset_d.csv': 'D'
}
paths = list(labels_dict.keys())
labels = list(labels_dict.values())

# Output files
final_figure_output = '../output/Figure-2_integrated_cluster.png'
feature_contributions_output = '../output/Table_B.1_PCA_feature_contributions.csv'