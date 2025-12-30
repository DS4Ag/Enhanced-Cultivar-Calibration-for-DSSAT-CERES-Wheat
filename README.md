
# **Enhanced Cultivar Calibration for DSSAT-CERES Wheat**

<img src="https://github.com/DS4Ag/dpest/blob/main/graphics/icon.svg" width="240" alt="dpest"/>

[![Python version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-GPL--3.0-green.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Documentation Status](https://readthedocs.org/projects/dpest/badge/?version=latest)](https://dpest.readthedocs.io/en/latest/?badge=latest)
[![DOI](https://zenodo.org/badge/1072290767.svg)](https://doi.org/10.5281/zenodo.18099536)

### *Integrating Ecotype Parameterization and Time-Series Data*

This repository contains the reproducible framework and data used in the study:
**“Enhancing DSSAT-CERES Wheat Calibration with Ecotype Parameterization and Time-Series Data”**
*(Vargas-Rojas et al., 2025)*

The project develops a systematic workflow for calibrating DSSAT-CERES Wheat model parameters using ecotype-specific coefficients and time-series observations. It integrates multiple calibration steps, clustering-based ecotype definition, and automated parameter optimization through the PEST software.

---

## **Repository Structure**

```
Enhanced_Cultivar_Calibration_DSSAT_Ecotype_Timeseries/
│
├── data/                         # Input data and calibration sets
│   ├── 1_ecotype_calibration/    # Ecotype-level calibration (subset A–D)
│   ├── 2_cultivar_calibration/   # Cultivar-level calibration (subset A–D)
│   ├── 3_ecotype_impact_assessment/ # Comparison across representative ecotypes
│   ├── 4_impact_assessment_time-series data/ # Time-series based calibration
│   ├── clustering/               # Phenotypic clustering datasets
│   ├── cultivar_parameters/      # Aggregated parameters for barplot analysis
│   └── DSSAT48/                  # DSSAT input data (weather, soil, genotype)
│
├── output/                       # Generated plots and summary tables
│   ├── Figure-2_integrated_cluster.png
│   ├── Figure-3_parameters_barplot.png
│   ├── Figure-4_ecotype-comparison_heatmap_WW-23.png
│   ├── Figure-5_time-series_NRMSE_heatmap.png
│   ├── Figure-6_time-series_LWAD_RWAD_14_Ecotypes.png
│   ├── Figure-B.2_ecotype-calibration_heatmap_WW-23.png
│   └── Table_B.1_PCA_feature_contributions.csv
│
├── scripts/                      # Script entry points to reproduce each figure/table
│   ├── Figure-2_integrated_cluster.py
│   ├── Figure-3_parameters_barplot.py
│   ├── Figure-4_ecotype-comparison_heatmap.py
│   ├── Figure-5_time-series_NRMSE.py
│   ├── Figure-6_time-series_growth.py
│   ├── Figure-B.2_ecotype-calibration_heatmap.py
│   └── Table_B.1_PCA_feature_contributions.py
│
├── src/                          # Core reusable code
│   ├── clustering/               # PCA, clustering, and feature contribution modules
│   ├── metrics/                  # NRMSE, RMSE, MPE, R²(1:1), and Gain calculations
│   ├── plot_style/               # Unified styling for barplots, heatmaps, time-series
│   ├── barplot_parameters.py     # Generates parameter adjustment plots
│   ├── data_preparation*.py      # Prepares calibration data grids and summaries
│   ├── heatmap_plot*.py          # Multi-panel heatmaps for calibration results
│   ├── ts_*                      # Time-series data extraction and plotting modules
│   ├── utils.py                  # Common helper functions
│   └── variable_mapping.py       # Standardized variable names across modules
│
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── .gitignore                    # Excluded files and folders
```

---

## **Environment Setup**

```bash
# Clone repository
git clone https://github.com/DS4Ag/Enhanced-Cultivar-Calibration-for-DSSAT-CERES-Wheat.git
cd Enhanced-Cultivar-Calibration-for-DSSAT-CERES-Wheat

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)

# Install dependencies
pip install -r requirements.txt
```

---

## **Reproducibility**

Each figure or table in the study corresponds to a single executable Python script in the `scripts/` directory.
Running these scripts reproduces all outputs in the `/output/` folder.

---

### **Example 1: Parameter Change Barplots (Figure 3)**

```bash
# Generate Figure 3
python scripts/Figure-3_parameters_barplot.py
```

**Input source:** `data/cultivar_parameters/CULTIVAR_parameters.csv`
**Output file:** `output/Figure-3_parameters_barplot.png`

This script summarizes cultivar parameter changes (mean ± SE) across calibration steps.
The user can modify paths, variables, or analysis steps directly at the top of each script.
No edits to the `src/` modules are needed for standard use.

---

### **Example 2: Ecotype Comparison Heatmap (Figure 4)**

```bash
python scripts/Figure-4_ecotype-comparison_heatmap.py
```

This script:

* Loads multiple calibrated ecotype sets (`cultivar_AZWH18`, `CI0001`, `DEFAULT`, and `subset_C`)
* Computes **NRMSE**, **MPE**, **R² (1:1)**, and **Gain** metrics from `OVERVIEW.OUT`
* Generates a **four-panel heatmap** comparing performance across ecotypes

**Output:**
`output/Figure-4_ecotype-comparison_heatmap_WW-23.png`

---

### **Example 3: Time-Series Growth Comparison (Figure 6)**

```bash
python scripts/Figure-6_time-series_growth.py
```

This script:

* Reads `PlantGro.OUT` and measured data (`.WHT`) for each calibration
* Aggregates growth data across 14 cultivars and 3 treatments
* Plots **simulated vs. observed** biomass and LAI trajectories

**Output:**
`output/Figure-6_time-series_LWAD_RWAD_14_Ecotypes.png`

---

## **Calibration and Model Reproduction**

### **DSSAT Input Files**

The repository provides a complete set of DSSAT input files (version 4.8) under `data/DSSAT48/`, including:

| Type           | Files                                                     |
| -------------- | --------------------------------------------------------- |
| **Genotype**   | `WHCER048.CUL`, `WHCER048.ECO`                            |
| **Soil**       | `SOIL.SOL`                                                |
| **Weather**    | Multiple `.WTH` files (2017–2023) and climate definitions |
| **Management** | `.WHA`, `.WHT`, `.WHX` defining wheat experiments         |

These files allow users to reproduce all model simulations and calibrations without additional DSSAT setup.

---

### **PEST Calibration Workflow**

Each numbered folder under `/data/` corresponds to a calibration stage:

| Stage                                | Description                                                                                                 | Folder                                  |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| 1. **Ecotype Calibration**           | Calibrates 32 ecotype parameters using grouped cultivars (A–D) and one-time observations.                   | `1_ecotype_calibration/`                |
| 2. **Cultivar Calibration**          | Optimizes 7 cultivar parameters (`P1V`, `P1D`, `P5`, `G1`, `G2`, `G3`, `PHINT`) using ecotype coefficients. | `2_cultivar_calibration/`               |
| 3. **Ecotype Impact Assessment**     | Evaluates model behavior using multiple ecotype baselines (cluster-derived, `CI0001`, `AZWH18`, `DEFAULT`). | `3_ecotype_impact_assessment/`          |
| 4. **Time-Series Impact Assessment** | Assesses benefits of adding biomass (`BMTS`) and LAI (`LAITS`) time-series to cultivar calibration.         | `4_impact_assessment_time-series data/` |

---

### **Configuration and Automation**

Each calibration subfolder contains:

| File                           | Purpose                                                                          |
| ------------------------------ | -------------------------------------------------------------------------------- |
| `config.yaml`                  | Defines treatments, variables, file paths, and calibration parameters.           |
| `pest_dssat_calibration.py`    | Automates creation and validation of PEST files and runs DSSAT/PEST calibration. |
| `.pst`, `.tpl`, `.ins` files   | Generated PEST control, template, and instruction files.                         |
| `OVERVIEW.OUT`, `PlantGro.OUT` | DSSAT model output files used for calibration.                                   |

---

**Example Workflow**

```bash
cd data/2_cultivar_calibration/cultivar_subset_a/
python pest_dssat_calibration.py
```

This script:

1. Loads the local YAML configuration
2. Generates all PEST input files (`TPL`, `INS`, `PST`)
3. Validates files using `tempchek`, `inschek`, and `pestchek`
4. Runs calibration with `PEST.exe`
5. Outputs results and updated control files to the same folder

---

## **Key Components**

| Module                        | Purpose                                                                   |
| ----------------------------- | ------------------------------------------------------------------------- |
| **Ecotype Calibration**       | Uses PEST to estimate shared ecotype coefficients (32 parameters).        |
| **Cultivar Calibration**      | Refines cultivar-specific coefficients (7 parameters).                    |
| **Ecotype Impact Assessment** | Tests different ecotype baselines and compares model accuracy.            |
| **Time-Series Calibration**   | Integrates LAI and biomass data for dynamic performance evaluation.       |
| **Clustering**                | Defines ecotype groups through PCA and hierarchical clustering of traits. |
| **Metrics**                   | Calculates RMSE, NRMSE, MPE, R²(1:1), and Gain for model validation.      |

---

## **Figure Generation Summary**

| Figure/Table | Script                                              | Description                                  |
| ------------ | --------------------------------------------------- | -------------------------------------------- |
| Figure 2     | `scripts/Figure-2_integrated_cluster.py`            | PCA and cluster visualization                |
| Figure 3     | `scripts/Figure-3_parameters_barplot.py`            | Parameter change across calibration steps    |
| Figure 4     | `scripts/Figure-4_ecotype-comparison_heatmap.py`    | Performance comparison across ecotypes       |
| Figure 5     | `scripts/Figure-5_time-series_NRMSE.py`             | Time-series model accuracy heatmap           |
| Figure 6     | `scripts/Figure-6_time-series_growth.py`            | Growth trajectories under different ecotypes |
| Figure B.2   | `scripts/Figure-B.2_ecotype-calibration_heatmap.py` | Supplementary ecotype performance map        |
| Table B.1    | `scripts/Table_B.1_PCA_feature_contributions.py`    | PCA feature contribution summary             |

---

## **Dependencies**

This project was tested with:

* Python ≥ 3.10
* Pandas, NumPy, Matplotlib, Seaborn
* YAML, SciPy
* DSSAT v4.8 outputs and PEST v21 executables (external tools)

---

## **Reproducibility and FAIR Data**

* All datasets follow the **Tidy Data** principle.
* Each calibration subset contains its own `config.yaml` and `pest_dssat_calibration.py` for local execution.
* Outputs are automatically saved with standardized file names and figure formats.

---

## **Citation**

If you use this repository or its components, please cite:

> Vargas-Rojas, L., Wang, D. R., et al. (2025). *Enhancing DSSAT-CERES Wheat Calibration with Ecotype Parameterization and Time-Series Data.*
> [Manuscript submitted to *in silico Plants* (ISPLANTS-2025-064)].

## **License**

This repository is released under the [GNU General Public License v3.0 only](https://www.gnu.org/licenses/gpl-3.0.html).
