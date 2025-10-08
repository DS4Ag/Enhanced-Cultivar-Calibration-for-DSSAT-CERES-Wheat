"""
Save PCA future contributions for each data subset
"""

from src.clustering.pca_feature_contributions import analyze_feature_contributions
import os

if __name__ == "__main__":
    # Set directory to where the input datasets are located
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data', 'clustering')

    # Run the analysis
    analyze_feature_contributions(data_dir=data_dir)