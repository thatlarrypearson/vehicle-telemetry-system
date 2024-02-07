# telemetry-analysis/telemetry_analysis/data_files.py
#
# Data file handling and management
from pathlib import Path
from rich.console import Console
from rich.jupyter import print

from private.vehicles import vehicles
from .common import data_file_base_directory, work_product_file_path, temporary_file_base_directory
from .vins import fake_vin

from obd_log_to_csv.obd_log_evaluation import input_file as obd_log_evaluation_input_file
from obd_log_to_csv.obd_log_evaluation import rich_output as obd_log_evaluation_rich_output
from obd_log_to_csv.obd_log_to_csv import main as obd_log_to_csv_main

console = Console()

Path(work_product_file_path).mkdir(parents=True, exist_ok=True)

# Sort list of files in timestamp order - This is the sorted() function parameter required to change how the sort is done.
def sort_key_on_timestamp(file_path:str)->str:
    # TEST form "../../telemetry-obd/data/{vin}/{vin}-TEST-20221102183723-utc.json"
    # Normal form "../../telemetry-obd/data/{vin}/{vin}-20221030145832-utc.json"
    file_name = (file_path.split('/'))[-1]
    date_part = ((file_name.split('-'))[-2:-1])[0]
    return date_part

def obd_to_csv_file_name(obd_file_name:str)->str:
    # convert OBD data file name into csv file name
    # from TEST form "../../telemetry-obd/data/{vin}/{vin}-TEST-20221102183723-utc.json"
    #   to TEST form "{vin}-TEST-20221102183723-utc.json"
    # from Normal form "../../telemetry-obd/data/{vin}/{vin}-20221030145832-utc.json"
    #   to Normal form "{vin}-20221030145832-utc.json"
    obd_file = (obd_file_name.split('/'))[-1]
    return obd_file.replace('.json', '.csv')

def quotes_around_string(command:str, single_quote="'")->str:
    return (single_quote + command + single_quote)

def obd_to_csv(vin:str, columns:list, study="gear", verbose=False):
    # make temporary directory
    temporary_file_directory = f"{temporary_file_base_directory}/{vin}/{study}"
    Path(temporary_file_directory).mkdir(parents=True, exist_ok=True)
    create_count = 0
    skip_count = 0

    console.print(f"{vehicles[vin]['name']} Generating CSV Files in {temporary_file_directory}")

    # Make a list of OBD data files.
    # directory where "*.json" OBD data files are held
    root = Path(data_file_base_directory)
    obd_files = [ str(rp) for rp in root.rglob(f"*{vin}*.json") if rp.is_file() and 'integrated' not in rp.name]    

    # Make a sorted list of OBD data files.
    # obd_files = sorted(obd_files, key=sort_key_on_timestamp)

    for obd_file in obd_files:
        # generate CSV version of OBD data file
        output_file_name = f"{temporary_file_directory}/{str(Path(obd_to_csv_file_name(obd_file)).name)}"

        # Only (re)generate when the file doesn't already exist
        if (Path(output_file_name)).is_file():
            if verbose:
                fake_name = (str(output_file_name)).replace(vin, fake_vin)
                console.print(f"CSV file for {vehicles[vin]['name']} {fake_name} already exists - skipping...")
            skip_count += 1
            continue

        obd_log_to_csv_main(json_input_files=[obd_file, ], csv_output_file_name=output_file_name, commands=columns)
        if verbose:
            fake_name = (str(output_file_name)).replace(vin, fake_vin)
            console.print(f"CSV file for {vehicles[vin]['name']} {fake_name} created")
        create_count +=1

    console.print(f"\tCreated {create_count}\n\tSkipped {skip_count}\n")
