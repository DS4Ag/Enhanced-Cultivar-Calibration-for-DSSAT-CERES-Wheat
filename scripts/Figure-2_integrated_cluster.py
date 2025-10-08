"""
Run the integrated cluster figure generator from script.
"""

import sys
import os

# Ensure src/ is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from clustering.integrated_cluster_figure import generate_integrated_cluster_figure

if __name__ == '__main__':
    generate_integrated_cluster_figure()