# telemetry-obd_log_to_csv/obd_log_to_csv/json_data_integrator.py
"""
JSON Data Integrator

Integrates telemetry JSON data from multiple sources into a single data file from
multiple data sources:
- telemetry_obd.obd_logger
- gps_logger.gps_logger
- wthr_logger.wthr_logger
- imu_logger.imu_logger
- other sources conforming to https://github.com/thatlarrypearson/telemetry-obd#telemetry-obd-logger-output-data-files
"""

import json
from pathlib import Path
from argparse import ArgumentParser

from .__init__ import __version__
from tcounter.common import (
    BASE_PATH,
)

def write_json_data_to_integrated_file(records:list, base_path:str, hostname:str, boot_count:int, vin:str, verbose=False):
    if vin is None:
        vin = "UNKNOWN_VIN"

    boot_count_string =  (f"{boot_count:10d}").replace(' ', '0')
    output_file_path = Path(f"{base_path}/{hostname}/{hostname}-{boot_count_string}-integrated-{vin}.json")

    if verbose:
        print(f"writing integrated JSON data to {output_file_path}")

    with open(output_file_path, "w+", encoding='utf-8') as output_file:
        for record in records:
            output_file.write(json.dumps(record) + "\n")

    return output_file_path

def sort_key(json_data_record:dict):
    """
    - json_data_record["iso_ts_pre"]
    - json_data_record["iso_ts_post"]
    - json_data_record["command_name"]
    """
    return json_data_record["iso_ts_pre"] + json_data_record["iso_ts_post"] + json_data_record["command_name"]

def get_json_file_list(base_path:str, hostname:str, boot_count:int, verbose=False):
    """
    Return list of JSON data files matching the input parameters
    """
    file_list = []
    data_directory = f"{base_path}/{hostname}"
    for json_data_file_path in (Path(data_directory).glob(f"{hostname}*.json")):
        file_name_parts = json_data_file_path.name.split('-')
        if boot_count == int(file_name_parts[1]) and "integrated" not in json_data_file_path.name:
            if verbose:
                print(f"boot_count {boot_count} file {json_data_file_path.name}")
            file_list.append(json_data_file_path)

    if verbose:
        print(f"json file list {file_list}")
    return file_list

def get_vin_from_json_file_list(json_file_list)->str:
    """
    Return VIN from get_json_file_list() output or return None if not found.
    """
    # json_file_list is really pathlib.Path values.
    for json_data_file_path in json_file_list:
        if '-obd-' in json_data_file_path.name:
            file_name_parts = json_data_file_path.name.split('-')
            if file_name_parts[2] == 'obd':
                return file_name_parts[3]

    return None

def command_line_options()->dict:
    parser = ArgumentParser(prog="json_data_integrator", description="Telemetry JSON Data Integrator")

    parser.add_argument(
        "--base_path",
        help=f"BASE_PATH directory variable.  Defaults to {BASE_PATH}",
        default=BASE_PATH,
    )

    parser.add_argument(
        "--hostname",
        help="The hostname of the computer where the data was collected.",
        required=True,
    )

    parser.add_argument(
        "--boot_count",
        help="""A counter used to identify the number of times the data collection computer booted since
        telemetry-counter was installed and configured.
        """,
        required=True,
        type=int,
    )

    parser.add_argument(
        "--version",
        help="Returns version and exit.",
        required=False,
    )

    parser.add_argument(
        "--verbose",
        help="Turn verbose output on. Default is off.",
        default=False,
        action='store_true'
    )

    return vars(parser.parse_args())

def main(args=None, base_path=BASE_PATH, hostname=None, boot_count=None, verbose=False):
    if args is not None:
        # Called from command line
        if args['version']:
            # return version and exit
            print(f"Version {__version__}")
            exit(0)

        base_path = args['base_path']
        hostname = args['hostname']
        boot_count = args['boot_count']
        verbose = args['verbose']

    elif hostname is None or boot_count is None:
        # External call to main, required args not provided.
        raise ValueError("boot_count and hostname must have valid values (can't be None)")

    if verbose:
        print(f"base_path {base_path}")
        print(f"hostname {hostname}")
        print(f"boot_count {boot_count}")

    sortable_list = []
    for file in get_json_file_list(base_path, hostname, boot_count, verbose=verbose):
        if verbose:
            print(f"file {file.name}")
        with open(file,  "r") as json_input:
            for line_number, json_record in enumerate(json_input, start=1):
                try:
                    input_record = json.loads(json_record)

                except json.decoder.JSONDecodeError as e:
                    # improperly closed JSON file
                    if verbose:
                        print(f"Corrupted JSON info {file.name} line {line_number}:\n{e}")
                    break

                sortable_list.append(input_record)

    # Sort using key "<iso_ts_pre><iso_ts_post><command_name>"
    if verbose:
        print(f"sorting {len(sortable_list)}")
    sortable_list.sort(key=sort_key)

    # Remove duplicate records
    if verbose:
        print(f"sorted list {len(sortable_list)} before un-duplicating")

    un_duplicate_list = {sort_key(record): record for record in sortable_list}
    un_duplicate_list = [record for k, record in un_duplicate_list.items()]

    if verbose:
        print(f"sorted list {len(un_duplicate_list)} after un-duplicating")

    # write sorted_list to file
    if verbose:
        print("writing sorted list")

    vin = get_vin_from_json_file_list(get_json_file_list(base_path, hostname, boot_count, verbose=verbose))
    output_file_path = write_json_data_to_integrated_file(un_duplicate_list, base_path, hostname, boot_count, vin, verbose=verbose)

    if verbose:
        print(f"un-duplicate sorted list written out to {output_file_path}")

    return

if __name__ == "__main__":
    args = command_line_options()
    main(args=args,)

