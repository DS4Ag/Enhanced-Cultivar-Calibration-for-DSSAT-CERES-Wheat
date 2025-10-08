import pandas as pd
import os
import re
import yaml

def validate_file_path(file_path):
    """
    Validates that the input file path exists.
    """
    if not file_path or not isinstance(file_path, str):
        raise ValueError(f"The file path must be a non-empty string.")
    if not os.path.isfile(file_path):
        file_name = os.path.basename(file_path)
        file_dir = os.path.dirname(file_path)
        raise FileNotFoundError(f"The file '{file_name}' does not exist at: {file_dir}")
    return file_path


def simulations_lines(file_path):
    """
    Identifies and extracts the line ranges associated with specific treatments in the OVERVIEW output file.

    Parameters:
    file_path (str): The path to the text file containing tOVERVIEW output file.

    Returns:
    dict: A dictionary where the keys are TREATMENT names and the values are
          tuples containing the start and end line numbers.
    """

    # Initialize dictionaries and lists to store relevant data
    result_dict = {}
    dssat_lines = []
    run_lines = []

    # Open the file and read all lines into a list
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Iterate through each line to identify lines starting with '*DSSAT' and '*RUN'
    for i, line in enumerate(lines):
        if '*DSSAT' in line:
            # Store the line number of each '*DSSAT' occurrence
            dssat_lines.append(i)
        if line.strip().startswith('TREATMENT'):
            # Store the line number and the content of each 'TREATMENT' line
            run_lines.append((i, line.strip()))

    # Process the stored lines to populate the result dictionary
    for i, start_line in enumerate(dssat_lines):
        if i < len(dssat_lines) - 1:
            # Determine the end line for the current '*DSSAT' section
            end_line = dssat_lines[i + 1] - 1
        else:
            # If it's the last '*DSSAT' section, set the end line as the last line of the file
            end_line = len(lines) - 1
            end_line = len(lines)

        # Find the appropriate '*RUN' line within the current '*DSSAT' section
        run_info = None
        for run_start, run_line in run_lines:
            if run_start >= start_line and run_start <= end_line:
                # Extract only the 'treatment' name from the 'TREATMENT -n' line
                run_info = run_line.split(':')[1].strip().rsplit(maxsplit=1)[0]

                break

        # If the treatment information was found, store it in the result dictionary
        if run_info:
            result_dict[run_info] = (start_line, end_line)

    # Return the entire dictionary with all treatment information
    return result_dict


def extract_simulation_data(file_path):
    """
    Extracts simulation data for each cultivar, including the experiment information,
    and returns a DataFrame with all the data.

    Parameters:
    file_path (str): The path to the text file containing the growth aspects data.

    Returns:
    pd.DataFrame: A DataFrame containing the parsed data for all cultivars, including the experiment info.
    """
    # Get the dictionary with the line ranges for each cultivar
    treatment_dict = simulations_lines(file_path)

    # Initialize an empty DataFrame to store all the data
    all_data = pd.DataFrame(
        columns=['TREATMENT', 'cultivar', 'VARIABLE', 'VALUE_SIMULATED', 'VALUE_MEASURED', 'EXPERIMENT', 'POSITION'])

    with open(file_path, 'r') as file:
        lines = file.readlines()

        # Iterate through each cultivar and extract data
        for treatment, (start_line, end_line) in treatment_dict.items():
            cultivar_data = []
            experiment_info = None

            # Iterate through the lines in the specified range to find the EXPERIMENT line
            for i in range(start_line, end_line):
                line = lines[i].strip()

                # Look for the line containing 'EXPERIMENT'
                if line.startswith('EXPERIMENT'):
                    # Extract the experiment description after the colon
                    experiment_info = line.split(':')[1].strip()

                if line.startswith('CROP') and 'CULTIVAR :' in line:
                    # Extract CULTIVAR information using split
                    parts = line.split('CULTIVAR :')
                    if len(parts) > 1:
                        cultivar = parts[1].split('ECOTYPE')[
                            0].strip()  # Extract everything between 'CULTIVAR :' and 'ECOTYPE'

                # Look for the line with simulation results (lines after @)
                if line.startswith('@'):

                    # Store the header line to return it
                    header_line = line

                    line_number = 0
                    for data_line in lines[i + 1:]:

                        line_number += 1

                        if not data_line.strip() or data_line.startswith('*'):
                            break

                        data_line = data_line.strip().split()
                        variable_name = ' '.join(data_line[:-2])  # Get the variable name
                        simulated_value = data_line[-2]
                        measured_value = data_line[-1]

                        # Replace any value starting with '-99' with an empty string
                        simulated_value = '' if simulated_value.startswith('-99') else simulated_value
                        measured_value = '' if measured_value.startswith('-99') else measured_value

                        # Append the row data
                        cultivar_data.append({
                            'TREATMENT': treatment,
                            'cultivar': cultivar,
                            'VARIABLE': variable_name,
                            'VALUE_SIMULATED': simulated_value,
                            'VALUE_MEASURED': measured_value,
                            'EXPERIMENT': experiment_info,
                            'POSITION': line_number,
                        })

                    # Convert to DataFrame and append to all_data
                    cultivar_df = pd.DataFrame(cultivar_data)
                    all_data = pd.concat([all_data, cultivar_df], ignore_index=True)

    # Remove rows where any of the columns 'VARIABLE', 'VALUE_SIMULATED', or 'VALUE_MEASURED' contain '--------'
    all_data = all_data[
        ~all_data[['VARIABLE', 'VALUE_SIMULATED', 'VALUE_MEASURED']].apply(lambda x: x.str.contains('--------')).any(
            axis=1)]

    # Convert the 'VALUE_SIMULATED' and 'VALUE_MEASURED' columns to numeric values
    all_data['VALUE_SIMULATED'] = pd.to_numeric(all_data['VALUE_SIMULATED'], errors='coerce')
    all_data['VALUE_MEASURED'] = pd.to_numeric(all_data['VALUE_MEASURED'], errors='coerce')

    # Split the 'Cultivar' column into 'treatment' and 'cultivar' columns
    # all_data[['treatment', 'cultivar']] = all_data['Cultivar'].str.split('_', expand=True)

    # Drop the original 'Cultivar' column as it's now split into two
    # all_data.drop(columns=['Cultivar'], inplace=True)

    # Convert all column names to lowercase
    all_data.columns = all_data.columns.str.lower()

    return all_data, header_line


def load_and_process_overview(calibration_code_list, base_data_dir,
                             treatments_dic, variable_name_mapping):
    """
        Loads, merges, and processes OVERVIEW.OUT and config.yaml files for each calibration code.

        Parameters
        ----------
        calibration_code_list : list of str
            List of subfolder names, e.g. ['cultivar_subset_a', ...]
        base_data_dir : str
            Path to the folder containing all calibration subfolders (e.g. '../data/ecotype_calibration')
        treatments_dic : dict
            Map short treatment codes to human-readable strings
        variable_name_mapping : dict
            Map raw DSSAT-like variable column names to human-readable ones
        extract_simulation_data : function
            Function to extract DataFrame from OVERVIEW.OUT (custom per-project)
        validate_file_path : function
            Function to check that a path is valid (custom per-project)

        Returns
        -------
        pd.DataFrame
            All processed, merged, and relabeled overview data
        """
    list_overview_df = []

    for calibration_code in calibration_code_list:
        print(calibration_code)

        # Full file path for this subset
        out_file_path = os.path.join(base_data_dir, calibration_code, 'OVERVIEW.OUT')
        # Validate that the file exists
        validated_path = validate_file_path(out_file_path)
        overview_df_raw, _ = extract_simulation_data(validated_path)
        # Remove rows where 'value_measured' column contains NaN values
        overview_df = overview_df_raw.dropna(subset=['value_measured']).copy()
        # Add calibration code as a new column
        overview_df['calibration_code'] = calibration_code

        # YAML meta extraction
        yaml_file_path = os.path.join(base_data_dir, calibration_code, 'config.yaml')
        with open(yaml_file_path) as config:
            try:
                config_file = yaml.safe_load(config)
            except yaml.YAMLError as exc:
                print(exc)

        for field in ['plantgro_variables', 'overview_variables', 'calibration_method', 'short_label', 'long_label']:
            value = config_file.get(field, [])
            overview_df[field] = ', '.join(value) if value else ''

        list_overview_df.append(overview_df)

    # Combine all into one big DataFrame
    overview_data = pd.concat(list_overview_df, ignore_index=True)

    # Unify and relabel columns
    overview_data.rename(columns={'treatment': 'treatment_cultivar'}, inplace=True)
    overview_data['treatment'] = overview_data['treatment_cultivar'].astype(str).str[:4]
    overview_data['treatment'] = overview_data['treatment'].map(treatments_dic)
    overview_data['variable'] = overview_data['variable'].map(variable_name_mapping)

    return overview_data


def update_variable_names(variable_names):
    """
    Format variable names with scientific notation for units
    """
    if isinstance(variable_names, str):
        variable_names = [variable_names]

    updated_names = []
    for var in variable_names:
        var = var.replace(r'kg/ha/day', 'kg ha$^{-1}$ day$^{-1}$')
        var = var.replace('g/m2', 'g m$^{-2}$')
        var = var.replace('kg/ha', 'kg ha$^{-1}$')
        var = var.replace('m2', 'm$^{-2}$')
        var = var.replace('g/MJ', 'g MJ$^{-2}$')
        var = re.sub(r'\bm2\b', 'm$^{-2}$', var)
        updated_names.append(var)
    return updated_names

###################################
## Revise these ones
###################################
def simulations_lines(file_path):
    """
    Identifies and extracts the line ranges associated with specific treatments in the OVERVIEW output file.

    Parameters:
    file_path (str): The path to the text file containing tOVERVIEW output file.

    Returns:
    dict: A dictionary where the keys are TREATMENT names and the values are
          tuples containing the start and end line numbers.
    """

    # Initialize dictionaries and lists to store relevant data
    result_dict = {}
    dssat_lines = []
    run_lines = []

    # Open the file and read all lines into a list
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Iterate through each line to identify lines starting with '*DSSAT' and '*RUN'
    for i, line in enumerate(lines):
        if '*DSSAT' in line:
            # Store the line number of each '*DSSAT' occurrence
            dssat_lines.append(i)
        if line.strip().startswith('TREATMENT'):
            # Store the line number and the content of each 'TREATMENT' line
            run_lines.append((i, line.strip()))

    # Process the stored lines to populate the result dictionary
    for i, start_line in enumerate(dssat_lines):
        if i < len(dssat_lines) - 1:
            # Determine the end line for the current '*DSSAT' section
            end_line = dssat_lines[i + 1] - 1
        else:
            # If it's the last '*DSSAT' section, set the end line as the last line of the file
            end_line = len(lines) - 1
            end_line = len(lines)

        # Find the appropriate '*RUN' line within the current '*DSSAT' section
        run_info = None
        for run_start, run_line in run_lines:
            if run_start >= start_line and run_start <= end_line:
                # Extract only the 'treatment' name from the 'TREATMENT -n' line
                run_info = run_line.split(':')[1].strip().rsplit(maxsplit=1)[0]

                break

        # If the treatment information was found, store it in the result dictionary
        if run_info:
            result_dict[run_info] = (start_line, end_line)

    # Return the entire dictionary with all treatment information
    return result_dict


def read_growth_file(file_path, treatment_range):
    """
    Reads a growth aspects output file and converts it into a pandas DataFrame.

    Arguments:
    file_path (str): The path to the text file containing the growth aspects data.
    treatment_range (tuple): A tuple containing the start and end line numbers for the treatment data.

    Returns:
    pd.DataFrame: A DataFrame containing the parsed data.
    """
    # Initialize an empty list to store the data
    data = []

    start_line, end_line = treatment_range

    # Open and read the file
    with open(file_path, "r") as text_file:
        lines = text_file.readlines()

        # Filter lines for the specified treatment
        treatment_lines = lines[start_line - 1:end_line]  # -1 to account for 0-based indexing

        # Find the line starting with '@' which contains the column headers
        for i, line in enumerate(treatment_lines):
            if line.startswith('@'):
                header_line = line
                break

        # Extract the column headers by splitting the line at whitespace
        headers = header_line.strip().split()

        # Extract the data starting from the next line after the headers
        for line in treatment_lines[i + 1:]:
            # Split the line into individual values based on whitespace
            row = line.strip().split()
            # Append the row to the data list
            data.append(row)

    # Create a DataFrame from the data with the extracted headers
    df = pd.DataFrame(data, columns=headers)

    # Convert appropriate columns to numeric data types
    df = df.apply(pd.to_numeric)

    return df


def extract_treatment_info_plantgrowth(file_path, treatment_dict):
    """
    Extracts treatment information and their corresponding codes from a file.

    Args:
        file_path (str): Path to the input file.
        treatment_dict (dict): A dictionary with treatment names as keys and their line ranges as values.

    Returns:
        dict: A dictionary where keys are treatment names and values are treatment codes.
    """
    treatment_number_name = {}
    treatment_experiment_name = {}

    # Read the file lines
    with open(file_path, 'r') as file:
        lines = file.readlines()

        # Iterate through each treatment range and extract data
        for treatment, (start_line, end_line) in treatment_dict.items():
            # Iterate through the lines in the specified range
            for i in range(start_line, end_line):
                line = lines[i].strip()

                # Look for the line containing 'EXPERIMENT'
                if line.startswith('EXPERIMENT'):
                    # Extract the code between 'EXPERIMENT' and ':'
                    experiment_info = line.split(':')[1].split()[0]

                # Look for the line containing 'TREATMENT'
                if line.startswith('TREATMENT'):
                    # Extract the code between 'TREATMENT' and ':'
                    treatment_code = line.split()[1].strip()

                    # Extract the treatment_info after the ':' and before trailing spaces
                    treatment_info = line.split(':')[1].strip().rsplit(maxsplit=1)[0]

                    # Store the values in the dictionary
                    treatment_number_name[treatment_info] = treatment_code

                    treatment_experiment_name[treatment_info] = experiment_info

    return treatment_number_name, treatment_experiment_name


def wht_filedata_to_dataframe(file_path):
    """
    Parses a DSSAT-style TXT file and returns a DataFrame.

    Parameters:
        file_path (str): The path to the TXT file.

    Returns:
        pd.DataFrame: A DataFrame containing the data from the TXT file.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Find the line with column headers (starts with '@')
    header_line = None
    for line in lines:
        if line.startswith('@'):
            header_line = line.strip()
            break

    if header_line is None:
        raise ValueError("No header line starting with '@' found in the file.")

    # Extract column names from the header line
    columns = header_line[1:].split()

    # Find the data lines (non-comment and numeric)
    data_lines = [
        line.strip() for line in lines
        if line.strip() and not line.startswith(('*', '!', '@'))
    ]

    # Parse data lines into a list of lists for the DataFrame
    data = []
    for line in data_lines:
        # Split on whitespace and ensure consistency with the number of columns
        values = line.split()
        if len(values) == len(columns):
            data.append(values)
        else:
            raise ValueError(f"Data row has inconsistent column count: {line}")

    # Create and return the DataFrame
    df = pd.DataFrame(data, columns=columns)
    return df


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

    # Extract string scalar from list or use empty string fallback
    if isinstance(short_label, list):
        short_label_str = short_label[0] if short_label else ''
    else:
        short_label_str = short_label

    # Load and parse PlantGro.OUT with metadata annotations
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

        # Assign short_label string scalar to entire DataFrame column safely
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

    # Filter wht_full_df where DAP is 0
    plantgro_df = plantgro_df.loc[:, essential_cols_plantgro]

    # Extract date when DAP is 0
    dap0_dates = plantgro_df.loc[plantgro_df['DAP'] == 0, 'DATE'].unique()
    # Convert dap0_dates strings (YYYYDDD) to datetime objects for reference
    dap0_dates_dt = pd.to_datetime(dap0_dates, format='%Y%j')

    print('dap0_dates: ',  dap0_dates_dt )

    # Load WHT measurement data for all unique experiments in this calibration
    unique_wht = set(treatment_experiment_name.values())

    wht_dfs = []
    for wht in unique_wht:
        wht_file_path = os.path.join(dssat_wheat_dir, wht + '.WHT')
        wht_df = wht_filedata_to_dataframe(wht_file_path)
        wht_df['experiment_id'] = wht
        wht_dfs.append(wht_df)

    wht_full_df = pd.concat(wht_dfs, ignore_index=True)

    # Build reference DataFrame for mapping
    mapping_rows = []
    for sim_id, experiment_id in treatment_experiment_name.items():
        treatment_number = treatment_number_name[sim_id]
        treat, geno = sim_id.split('_')
        mapping_rows.append({
            'experiment_id': experiment_id,
            'treatment_number': int(treatment_number),  # Convert to int for matching with TRNO
            'sim_id': sim_id,
            'treatment': treat,
            'genotype': geno
        })

    mapping_df = pd.DataFrame(mapping_rows)

    # Ensure TRNO is int in wht_full_df for matching
    wht_full_df['TRNO'] = wht_full_df['TRNO'].astype(int)

    # Merge measurement data with mapping on experiment_id and treatment number = TRNO
    wht_full_df = wht_full_df.merge(
        mapping_df,
        left_on=['experiment_id', 'TRNO'],
        right_on=['experiment_id', 'treatment_number'],
        how='left'
    )

    # Filter by requested treatment
    wht_full_df = wht_full_df[wht_full_df['treatment'] == treatment]

    # Enrich WHT with timing info (DAS, DAP) from PlantGro by keys
    timing_cols = ['DATE', 'treatment', 'genotype', 'DAS', 'DAP']
    timing_df = plantgro_df[timing_cols].drop_duplicates(subset=['DATE', 'treatment', 'genotype'])
    wht_full_df = wht_full_df.merge(timing_df, how='left', on=['DATE', 'treatment', 'genotype'])

    # Select relevant columns and add short_label column
    essential_cols_wht = [
        'TRNO', 'DATE', 'experiment_id', 'sim_id',
        'treatment', 'genotype', 'DAS', 'DAP', 'short_label'
    ]

    if variable_name:
        if variable_name in plantgro_df.columns:
            essential_cols_wht.append(variable_name)

    # Convert wht_full_df['DATE'] to datetime
    wht_full_df['DATE_dt'] = pd.to_datetime(wht_full_df['DATE'], format='%Y%j')

    # Use the earliest zero-DAP simulation date as the reference
    reference_zero_dap_date = dap0_dates_dt.min()

    # Create mask for rows where DAP is missing or NaN
    missing_dap_mask = wht_full_df['DAP'].isnull()

    # Calculate DAP as difference in days from reference date for missing DAP rows
    wht_full_df.loc[missing_dap_mask, 'DAP'] = (
        (wht_full_df.loc[missing_dap_mask, 'DATE_dt'] - reference_zero_dap_date).dt.days
    )

    wht_full_df.loc[:, 'short_label'] = short_label_str
    wht_full_df = wht_full_df.loc[:, essential_cols_wht]

    # Drop rows where the variable_name column is zero, NaN, or empty string
    wht_full_df[variable_name] = pd.to_numeric(wht_full_df[variable_name], errors='coerce')
    wht_full_df = wht_full_df[wht_full_df[variable_name] > 0]

    # Add sampling order
    wht_full_df['sampling_id'] = wht_full_df.groupby('genotype')['DAP'].rank(method='dense', ascending=True).astype(int)

    return plantgro_df, wht_full_df