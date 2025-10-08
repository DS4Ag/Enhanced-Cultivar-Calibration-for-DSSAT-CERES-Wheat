import os
import subprocess
from dpest.wheat.ceres import cul, eco
from dpest.wheat import overview, plantgro
from dpest import pst
from dpest.wheat.utils import uplantgro
from dpest.utils import *
import yaml


def noptswitch(pst_path, new_value=1):
    """
    Updates the NOPTSWITCH parameter in a PEST control (.pst) file.

    The NOPTSWITCH parameter determines the iteration before which PEST will not switch to
    central derivatives computation. This function allows you to set NOPTSWITCH to any integer
    value greater than or equal to 1.

    **Required Arguments:**
    =======

        * **pst_path** (*str*):
            Path to the ``.pst`` PEST control file whose NOPTSWITCH value you wish to update.

    **Optional Arguments:**
    =======

        * **new_value** (*int*, *default: 1*):
            The new value for the NOPTSWITCH parameter. Must be an integer greater than or equal to 1.

    **Returns:**
    =======

        * ``None``

    **Examples:**
    =======

    1. **Set NOPTSWITCH to 3 (delay central derivatives until 3rd iteration):**

       .. code-block:: python

          from dpest.utils import noptswitch

          pst_file_path = 'PEST_CONTROL.pst'
          noptswitch(pst_file_path, 3)
    """
    try:
        # Validation for NOPTSWITCH value
        if not isinstance(new_value, int) or new_value < 1:
            raise ValueError("NOPTSWITCH must be an integer greater than or equal to 1.")

        with open(pst_path, 'r') as f:
            lines = f.readlines()

        # PHIREDSWH and NOPTSWITCH are on line 8 (index 7) in standard PEST control files
        target_line_idx = 7  # Corrected from 6 to 7
        if target_line_idx >= len(lines):
            raise IndexError(f"Expected at least {target_line_idx + 1} lines in the file, but got {len(lines)}.")

        current_line = lines[target_line_idx]
        values = current_line.split()

        if not values:
            raise ValueError("PHIREDSWH/NOPTSWITCH line not found or is empty in the control file.")

        # If only PHIREDSWH is present, append NOPTSWITCH
        if len(values) == 1:
            values.append(str(new_value))
        else:
            values[1] = str(new_value)

        # Preserve original spacing
        current_padding = len(current_line) - len(current_line.lstrip())
        new_line = " " * current_padding + "   ".join(values) + "\n"
        lines[target_line_idx] = new_line

        with open(pst_path, 'w') as f:
            f.writelines(lines)

    except FileNotFoundError:
        print(f"Error: The file '{pst_path}' was not found.")
    except IndexError as ie:
        print(f"IndexError: {ie}")
    except ValueError as ve:
        print(f"ValueError: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



def load_yaml_config(cal_path):
    """Load the YAML configuration file from cal_path."""
    config_path = os.path.join(cal_path, "config.yaml")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file {config_path} not found!")

    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    return config


def run_command(cmd):
    print(f"\nExecuting: {' '.join(cmd)}")
    subprocess.run(cmd, shell=True, check=True)


def main():
    # Define calibration folder
    cal_path = "./"   #"./pest_cal1_1/"

    # Load configuration from YAML
    config = load_yaml_config(cal_path)

    # Extract variables
    ww2023_data = config["ww2023_data"]
    plantgro_variables = config["plantgro_variables"]
    overview_variables = config["overview_variables"]

    # Extract file paths
    file_paths = config["file_paths"]
    cul_file_path = file_paths["cul_file"]
    overview_file_path = file_paths["overview_file"]
    plantgro_file_path = file_paths["plantgro_file"]

    # Extract command-line settings
    commands = config["commands"]
    model_comand_line = commands["model_command"]
    py_comand_file = commands["py_command_file"]

    print(f"Loaded configuration:\n{config}")

    for treatment, cultivar in ww2023_data.items():
        print(f"\n~~~~~~~~~~~~~~~~~~~\nTreatment: {treatment}, Cultivar: {cultivar}\n~~~~~~~~~~~~~~~~~~~\n")

        # Create the folder to save the PEST files
        folder_name = cultivar.replace(" ", "")  # Remove spaces
        output_path = os.path.join(cal_path, folder_name)
        os.makedirs(output_path, exist_ok=True)  # Create the folder

        #############################
        # 1. Create PEST input files
        #############################

        # Create CULTIVAR parameters TPL file
        cultivar_parameters, cultivar_tpl_path = cul( cultivar = cultivar,
                                                      cul_file_path = cul_file_path,
                                                      output_path = output_path,
                                                      P = 'P1V, P1D',
                                                      P5 = 'P5',
                                                      G = 'G1, G2',
                                                      G3 = 'G3',
                                                      PHINT = 'PHINT'
        )


        # Create OVERVIEW observations INS file
        overview_observations, overview_ins_path = overview(
            treatment = treatment,
            overview_file_path = overview_file_path,
            output_path = output_path,
            variables = overview_variables
        )


        if plantgro_variables is not None:
            # Create PlantGro observations INS file
            plantgro_observations, plantgro_ins_path = plantgro(
                plantgro_file_path = plantgro_file_path,
                treatment = treatment,
                variables = plantgro_variables,
                output_path = output_path
            )

            for variable in plantgro_variables:
                # Add empty lines to the initial PlantGro file if needed
                uplantgro(plantgro_file_path, treatment, variable)

        # Create the PST file
        if plantgro_variables is not None:
            pst(
                cultivar_parameters,
                dataframe_observations=[overview_observations, plantgro_observations],
                output_path=output_path,
                model_comand_line=model_comand_line,
                input_output_file_pairs=[
                    (cultivar_tpl_path, cul_file_path),
                    (overview_ins_path, overview_file_path),
                    (plantgro_ins_path, plantgro_file_path),
                ],
            )
        else:
            pst(
                cultivar_parameters,
                dataframe_observations=[overview_observations],
                output_path=output_path,
                model_comand_line=model_comand_line,
                input_output_file_pairs=[
                    (cultivar_tpl_path, cul_file_path),
                    (overview_ins_path, overview_file_path),
                ],
            )

        #############################
        # 2. PEST input files validation
        #############################

        # Validate the WHCER048_CUL.TPL File
        run_command(['tempchek.exe', cultivar_tpl_path])

        # Validate the Overview Instruction File (.INS)
        run_command(['inschek.exe', overview_ins_path, overview_file_path])

        if plantgro_variables is not None:
            # Use the uplantgro function to fill the incomplete simulation lines
            uplantgro(plantgro_file_path, treatment, plantgro_variables)

            # Validate the PlantGro Instruction File (.INS)
            run_command(['inschek.exe', plantgro_ins_path, plantgro_file_path])

        # Validate the PEST Control File (.PST)
        pst_file_path = os.path.normpath(os.path.join(output_path, 'PEST_CONTROL.pst'))
        run_command(['pestchek.exe', pst_file_path])

        # Insert the uplantgro line to the end of the Python command file
        with open(py_comand_file, 'r+') as file:
            lines = file.readlines()

            # Remove all lines that start with 'uplantgro('
            lines = [line for line in lines if not line.strip().startswith("uplantgro(")]

            # Remove trailing blank lines
            while lines and lines[-1].strip() == "":
                lines.pop()

            # Only add a new line if plantgro_variables is not None
            if plantgro_variables is not None:
                # Make sure the last remaining line ends with '\n'
                if lines and not lines[-1].endswith('\n'):
                    lines[-1] += '\n'

                # Add the new uplantgro line
                new_line = f"uplantgro('{plantgro_file_path}', '{treatment}', {plantgro_variables})\n"
                lines.append(new_line)

            # Overwrite the file with cleaned and updated lines
            file.seek(0)
            file.truncate()
            file.writelines(lines)

        #############################
        # 3. PST file first adjustments before getting the observation weights
        #############################

        print('\n ~~~~~~~~ PST file adjustment')
        #######################
        # update the noptmax value to 0 to run the model only once using the unoptmax function
        # Run the function
        noptmax(pst_file_path, new_value = 0)

        # Removes SPLITTHRESH/SPLITRELDIFF/SPLITACTION columns
        rmv_splitcols(pst_file_path)

        # Updates the RLAMBDA1 parameter
        rlambda1(pst_file_path, 5.0)

        # Updates the RLAMFAC parameter
        rlamfac(pst_file_path, 2.0)

        # Updates the PHIRATSUF parameter
        phiratsuf(pst_file_path, 0.3)

        # Updates the PHIREDLAM parameter
        phiredlam(pst_file_path, 0.03)

        # Updates the PHIREDSTP parameter
        phiredstp(pst_file_path, 0.001)

        # Updates the NPHISTP parameter
        nphistp(pst_file_path, 4)

        # Updates the NPHINORED parameter
        nphinored(pst_file_path, 4)

        # Updates the RELPARSTP parameter
        relparstp(pst_file_path, 0.001)

        # Updates the NRELPAR parameter
        nrelpar(pst_file_path, 4)

        # Updates the NOPTSWITCH parameter
        noptswitch(pst_file_path, 3)

        ######################

        # Run the calibration one time
        run_command(['PEST.exe', pst_file_path])
        #
        # Get the observation weights
        pst_file_path_bal = os.path.join(output_path, 'PEST_CONTROL_bal.pst')
        run_command(['pwtadj1.exe', pst_file_path, pst_file_path_bal, '1.0'])

        #############################
        # 4. PST file second set of adjustments after getting the observation weights
        #############################

        # # Modify the new balanced PEST control file for full calibration updating the noptmax argument to 10000
        noptmax(pst_file_path_bal, new_value = 10000)

        # Removes SPLITTHRESH/SPLITRELDIFF/SPLITACTION columns
        rmv_splitcols(pst_file_path)

        ###########################
        # 5. Run the Calibration
        ###########################
        #pst_file_path_bal = './pest_cal1/ENTRY1/pest_control_bal.pst'
        run_command(['PEST.exe', pst_file_path_bal])

if __name__ == "__main__":
    main()