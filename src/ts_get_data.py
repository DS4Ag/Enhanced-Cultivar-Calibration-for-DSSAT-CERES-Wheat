import os
import pandas as pd
import yaml
from utils import *

def load_prepare_time_series_data(
    base_data_dir,
    dssat_wheat_dir,
    calibration_code,
    variable_name,
    treatment
):
    """
    Load and prepare PlantGro simulation and WHT measurement data from a single calibration folder.
    The calibration code (label) is extracted from the config.yaml 'short_label' field reliably.

    Parameters
    ----------
    base_data_dir : str
        Directory containing calibration subfolders.
    dssat_wheat_dir : str
        Directory containing DSSAT Wheat .WHT files.
    calibration_code: str
        Name of the calibration folder to load.
    variable_name : str or None
        Data variable (column) from PlantGro to keep alongside metadata.
    treatment : str
        Treatment to filter on in PlantGro data.

    Returns
    -------
    plantgro_df : pd.DataFrame
        Filtered PlantGro DataFrame with assigned calibration_code from YAML.
    wht_full_df : pd.DataFrame
        Filtered WHT DataFrame enriched with timing info.
        If no measurement data for the variable is available, returns an empty DataFrame.
    """
    # YAML meta extraction
    yaml_file_path = os.path.join(base_data_dir, calibration_code, 'config.yaml')
    with open(yaml_file_path) as config:
        try:
            config_file = yaml.safe_load(config)
        except yaml.YAMLError as exc:
            print(exc)
            config_file = {}
    short_label = config_file.get('short_label', '')
    if isinstance(short_label, list):
        short_label_str = short_label[0] if short_label else ''
    else:
        short_label_str = short_label

    # Load PlantGro.OUT with metadata annotations
    out_file_path = os.path.join(base_data_dir, calibration_code, 'PlantGro.OUT')
    validate_file_path(out_file_path)
    treatment_dict = simulations_lines(out_file_path)
    treatment_number_name, treatment_experiment_name = extract_treatment_info_plantgrowth(out_file_path, treatment_dict)

    all_plantgro_dfs = []
    for genotype in treatment_dict:
        treatment_range = treatment_dict[genotype]
        df = read_growth_file(out_file_path, treatment_range)
        treat, geno = genotype.split('_')
        df['treatment'] = treat
        df['genotype'] = geno
        df['sim_id'] = genotype
        df['treatment_number'] = treatment_number_name[genotype]
        df['experiment_id'] = treatment_experiment_name[genotype]
        df.loc[:, 'short_label'] = short_label_str
        all_plantgro_dfs.append(df)
    plantgro_df = pd.concat(all_plantgro_dfs, ignore_index=True)
    # Filter by requested treatment
    plantgro_df = plantgro_df[plantgro_df['treatment'] == treatment]
    # Compose YYYYDDD DATE column and move to front
    plantgro_df['DATE'] = plantgro_df['@YEAR'].astype(str) + plantgro_df['DOY'].astype(str).str.zfill(3)
    plantgro_df.drop(columns=['@YEAR', 'DOY'], inplace=True)
    plantgro_df.insert(0, 'DATE', plantgro_df.pop('DATE'))

    # Select essential columns + variable_name if present
    essential_cols_plantgro = [
        'DATE', 'DAS', 'DAP', 'treatment', 'genotype', 'sim_id',
        'treatment_number', 'experiment_id', 'short_label'
    ]
    if variable_name:
        if variable_name in plantgro_df.columns:
            essential_cols_plantgro.append(variable_name)
        else:
            print(f"Warning: variable '{variable_name}' not found in PlantGro data.")

    plantgro_df = plantgro_df.loc[:, essential_cols_plantgro]

    # Extract date when DAP is 0
    dap0_dates = plantgro_df.loc[plantgro_df['DAP'] == 0, 'DATE'].unique()
    dap0_dates_dt = pd.to_datetime(dap0_dates, format='%Y%j')
    print('dap0_dates: ',  dap0_dates_dt )

    # Load WHT measurement data for unique experiments
    unique_wht = set(treatment_experiment_name.values())
    wht_dfs = []
    for wht in unique_wht:
        wht_file_path = os.path.join(dssat_wheat_dir, wht + '.WHT')
        wht_df = wht_filedata_to_dataframe(wht_file_path)
        wht_df['experiment_id'] = wht
        wht_dfs.append(wht_df)
    wht_full_df = pd.concat(wht_dfs, ignore_index=True)

    # Build mapping df
    mapping_rows = []
    for sim_id, experiment_id in treatment_experiment_name.items():
        treatment_number = treatment_number_name[sim_id]
        treat, geno = sim_id.split('_')
        mapping_rows.append({
            'experiment_id': experiment_id,
            'treatment_number': int(treatment_number),
            'sim_id': sim_id,
            'treatment': treat,
            'genotype': geno
        })
    mapping_df = pd.DataFrame(mapping_rows)

    # Convert TRNO to int for matching
    wht_full_df['TRNO'] = wht_full_df['TRNO'].astype(int)

    # Merge measurement data with mapping
    wht_full_df = wht_full_df.merge(
        mapping_df,
        left_on=['experiment_id', 'TRNO'],
        right_on=['experiment_id', 'treatment_number'],
        how='left'
    )

    # Filter by requested treatment
    wht_full_df = wht_full_df[wht_full_df['treatment'] == treatment]

    # Enrich with timing info from PlantGro
    timing_cols = ['DATE', 'treatment', 'genotype', 'DAS', 'DAP']
    timing_df = plantgro_df[timing_cols].drop_duplicates(subset=['DATE', 'treatment', 'genotype'])
    wht_full_df = wht_full_df.merge(timing_df, how='left', on=['DATE', 'treatment', 'genotype'])

    # Select relevant cols and add short_label
    essential_cols_wht = [
        'TRNO', 'DATE', 'experiment_id', 'sim_id',
        'treatment', 'genotype', 'DAS', 'DAP', 'short_label'
    ]
    if variable_name and variable_name in plantgro_df.columns:
        essential_cols_wht.append(variable_name)

    # Convert to datetime
    wht_full_df['DATE_dt'] = pd.to_datetime(wht_full_df['DATE'], format='%Y%j')
    reference_zero_dap_date = dap0_dates_dt.min()

    # For rows missing DAP, calculate as difference in days from reference
    missing_dap_mask = wht_full_df['DAP'].isnull()
    wht_full_df.loc[missing_dap_mask, 'DAP'] = (
        (wht_full_df.loc[missing_dap_mask, 'DATE_dt'] - reference_zero_dap_date).dt.days
    )
    wht_full_df.loc[:, 'short_label'] = short_label_str

    # Filter wht_full_df to columns of interest if they exist
    missing_cols = [col for col in essential_cols_wht if col not in wht_full_df.columns]
    if missing_cols:
        print(f"Warning: Columns {missing_cols} missing from WHT data, dropping them.")
    essential_cols_wht = [col for col in essential_cols_wht if col in wht_full_df.columns]

    wht_full_df = wht_full_df.loc[:, essential_cols_wht]

    # Handle case when variable_name is not in WHT file:
    if variable_name not in wht_full_df.columns or wht_full_df[variable_name].dropna().empty:
        print(f"Info: Variable '{variable_name}' not found or empty in WHT data. Returning empty WHT DataFrame.")
        wht_full_df = pd.DataFrame(columns=wht_full_df.columns)  # Empty DF with correct columns

    # Drop zero or negative or NaN for variable_name in measurement data for plotting
    if variable_name in wht_full_df.columns and not wht_full_df.empty:
        wht_full_df[variable_name] = pd.to_numeric(wht_full_df[variable_name], errors='coerce')
        wht_full_df = wht_full_df[wht_full_df[variable_name] > 0]

    # Sampling id by genotype and DAP order for plotting measurement error bars if used
    if not wht_full_df.empty:
        wht_full_df['sampling_id'] = wht_full_df.groupby('genotype')['DAP'].rank(method='dense', ascending=True).astype(int)
    else:
        # Provide empty sampling_id column for consistency
        wht_full_df['sampling_id'] = pd.Series(dtype=int)

    return plantgro_df, wht_full_df
