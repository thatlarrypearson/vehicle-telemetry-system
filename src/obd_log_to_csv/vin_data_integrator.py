# telemetry-obd_log_to_csv/obd_log_to_csv/vin_data_integrator.py
"""
VIN Data Integrator

Integrates/combines telemetry data in JSON format into data files in JSON format.

Data comes from these data sources:
- telemetry_obd.obd_logger
- gps_logger.gps_logger
- wthr_logger.wthr_logger
- imu_logger.imu_logger
- other sources conforming to https://github.com/thatlarrypearson/telemetry-obd#telemetry-obd-logger-output-data-files

Starting with a VIN, obd_logger generated files are identified and used to find other
related sources of JSON data created at the same time.  See JSON_DATA_INTEGRATOR.md.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from argparse import ArgumentParser
from rich.console import Console

from .__init__ import __version__
from tcounter.common import  BASE_PATH

console = Console(width=140)

def get_output_file_path(base_path:Path, obd_file_name:str)->Path:
    flavor, hostname, application, boot_count_string, application_count_string, vin = get_info_from_json_file_name(obd_file_name)

    if vin is None:
        vin = "UNKNOWN_VIN"

    if flavor == 'counter':
        output_file_path = Path(f"{base_path}/{hostname}/{hostname}-{boot_count_string}-integrated-{vin}.json")
    elif flavor == 'interim':
        #   <application_name>-<boot_count>.json
        output_file_path = Path(f"{base_path}/interim/interim-{boot_count_string}-integrated-{vin}.json")
    elif flavor == 'original':
        output_file_path = Path(f"{base_path}/original/original-{boot_count_string}-integrated-{vin}.json")
    else:
        raise ValueError(f"unknown flavor {flavor}, unable to create output file path")

    output_file_path.parent.mkdir(parents=True, exist_ok=True)

    return output_file_path

def string_timestamp_to_datetime(s:str)->datetime:
    # sourcery skip: remove-redundant-slice-index
    if len(s) != 14:
        raise ValueError(f"string <{s}> not in timestamp format (YYYYMMDDhhmmss)")

    year    = int(s[0:4])
    month   = int(s[4:6])
    day     = int(s[6:8])
    hour    = int(s[8:10])
    minute  = int(s[10:12])
    second  = int(s[12:14])

    return datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second, tzinfo=timezone.utc)

def get_original_strategy_files(base_path:str, obd_timestamp:str)->list:
    """Get list of 'original' naming strategy files close to obd_file_name_timestamp"""
    # obd_timestamp = string_timestamp_to_datetime(obd_file_name_timestamp)
    path_list = []

    #   <application_name>-<YYYYmmddHHMMSS>-utc.json
    for p in Path(base_path).glob("**/*-utc.json"):
        if 'interim' in str(p):
            continue

        parts = p.name.split('-')
        if len(parts) != 3 or len(parts[0]) > 4 or len(parts[1]) != 14 or 'interim' in str(p):
            # application names are 3 or 4 characters (vins are greater than 4 characters)
            # the timestamp string must be 14 characters
            continue

        application_timestamp = string_timestamp_to_datetime(parts[1])
        delta_timestamp_seconds = abs(obd_timestamp - application_timestamp).total_seconds()

        # 4 hour grace period for 'similar' enough file matching
        if delta_timestamp_seconds > float(4*60*60):
            continue

        path_list.append(p)

    return path_list

def get_interim_strategy_files(base_path:str, application_name:str, boot_count_string:str) -> list:
    """Get list of 'interim' naming strategy files with the same boot count string"""
    #   <application_name>-<boot_count>.json
    return [p for p in Path(base_path).glob(f"**/{application_name}-{boot_count_string}.json") if 'integrated' not in str(p)]

def get_counter_strategy_files(base_path:str, hostname:str, vin:str, boot_count_string:str)->list:
    """Get list of 'counter' strategy files with same hostname and boot count string"""
    #   <hostname>-<boot_count>-<application_name>-<application_count>.json
    return [p for p in Path(base_path).glob(f"**/{hostname}-{boot_count_string}-*-*.json") if 'integrated' not in str(p)]

def get_info_from_json_file_name(json_file_name, verbose=False):
    # sourcery skip: hoist-statement-from-if
    """parse json file name to determine flavor, hostname, application, boot_count_string, application_count_string, and vin"""

    vin = None
    application_count_string = None
    boot_count_string = None
    application = None
    hostname = None
    flavor = None

    # remove .json from json_file_name, break json_file_name into sections
    base_name = json_file_name.replace('.json', '')
    sections = base_name.split('-')

    # ORIGINAL
    #   <vin>-<YYYYmmddHHMMSS>-utc.json
    #   C4HJWCG5DL9999-20230112133422-utc.json
    #   C4HJWCG5DL9999-TEST-20230112133422-utc.json
    #
    #   <application_name>-<YYYYmmddHHMMSS>-utc.json
    #   NMEA-20220610172050-utc.json
    if 'utc' in base_name:
        flavor = 'original'
        if 'NMEA' in base_name:
            application = 'gps'
        else:
            application = 'obd'
            vin = sections[0]

        boot_count_string = sections[2] if 'TEST' in base_name else sections[1]

    # INTERIM
    #   <vin>-<boot_count>.json
    #   3FTTW8F97PRA99999-0000000007.json
    #   3FTTW8F97PRA99999-TEST-0000000007.json
    #
    #   <application_name>-<boot_count>.json
    #   NMEA-0000000032.json
    elif len(sections) == 2 or (len(sections) == 3 and sections[1] == 'TEST'):
        flavor = 'interim'

        if 'NMEA' in base_name:
            application = 'gps'
        else:
            # 3FTTW8F97PRA99999-TEST-0000000001.json
            application = 'obd'
            vin = sections[0]

        boot_count_string = sections[1] if len(sections) == 2 else sections[2]

    # COUNTER (CURRENT)
    #   <hostname>-<boot_count>-<application_name>-<vin>-<application_count>.json
    #   telemetry2-0000000072-obd-C4HJWCG9DL9999-0000000039.json
    #
    #   <hostname>-<boot_count>-<application_name>-<application_count>.json
    #   telemetry2-0000000072-gps-0000000114.json
    #   telemetry2-0000000072-imu-0000000078.json
    #   telemetry2-0000000072-wthr-0000000066.json
    else:
        flavor = 'counter'
        hostname = sections[0]            
        boot_count_string = sections[1]
        application = sections[2]
        if len(sections) == 5:
            vin = sections[3]
            application_count_string = sections[4]
        elif len(sections) == 4:
            application_count_string = sections[3]
        else:
            raise ValueError(f"len(sections) <{len(sections)}> doesn't match flavor {flavor} sections {sections}")

    return flavor, hostname, application, boot_count_string, application_count_string, vin

def get_companion_json_file_list(base_path:str, obd_file_name:str, verbose=False)->list:
    """
    Returns a list containing file paths to files that are companions to the OBD file.
    """
    # determine the type of OBD file name convention - current, interim, original
    flavor, hostname, application, boot_count_string, application_count_string, vin = get_info_from_json_file_name(obd_file_name)

    if verbose:
        console.print(f"get_companion_json_file_list({obd_file_name}) flavor {flavor}")

    # determine file search strategy
    # search files and return list
    if flavor == 'original':
        obd_file_name_timestamp = string_timestamp_to_datetime(boot_count_string)
        return get_original_strategy_files(base_path, obd_file_name_timestamp)
    elif flavor == 'interim':
        return get_interim_strategy_files(base_path, 'NMEA', boot_count_string)
    elif flavor == 'counter':
        return get_counter_strategy_files(base_path, hostname, vin, boot_count_string)

    return []

def write_json_data_to_integrated_file(records, output_file_path, verbose=True)->Path:
    """write output file to integrated file"""
    if verbose:
        console.print(f"writing {len(records)} records of integrated JSON data to {output_file_path}")

    # truncate file on open for write
    with open(output_file_path, "w", encoding='utf-8') as output_file:
        for record in records:
            output_file.write(json.dumps(record) + "\n")

    return

def sort_key(json_data_record:dict):
    """
    - json_data_record["iso_ts_pre"]
    - json_data_record["iso_ts_post"]
    - json_data_record["command_name"]
    """
    return json_data_record["iso_ts_pre"] + json_data_record["iso_ts_post"] + json_data_record["command_name"]

def get_json_vin_file_list(base_path:str, vin:str, verbose=False) -> list:
    """Return a list of file paths to OBD files for a VIN."""
    if verbose:
        console.print(f"base path {base_path}, vin {vin}")

    file_list = [file_path for file_path in list((Path(base_path).glob(f"**/*{vin}*.json"))) if 'integrated' not in file_path.name]

    if verbose:
        console.print(f"input {vin} file_list {file_list}")

    return file_list

def command_line_options()->dict:
    parser = ArgumentParser(prog="json_data_integrator", description="Telemetry JSON Data Integrator")

    parser.add_argument(
        "--base_path",
        help=f"BASE_PATH directory variable.  Defaults to {BASE_PATH}",
        default=BASE_PATH,
    )

    parser.add_argument(
        "--vin",
        help="The VIN for the vehicle in a study.",
        required=True,
    )

    parser.add_argument(
        "--skip",
        help="Skip processing if output file already exists.",
        default=False,
        action='store_true',
    )

    parser.add_argument(
        "--version",
        help="Returns version and exit.",
        default=False,
        action='store_true',
    )

    parser.add_argument(
        "--verbose",
        help="Turn verbose output on. Default is off.",
        default=False,
        action='store_true',
    )

    return vars(parser.parse_args())

def main(args=None, base_path=BASE_PATH, vin=None, skip=False, verbose=False):
    if args is not None:
        # Called from command line
        if args['version']:
            # return version and exit
            console.print(f"Version {__version__}")
            exit(0)

        base_path = args['base_path']
        vin = args['vin']
        verbose = args['verbose']
        skip = args['skip']

    elif vin is None:
        # External call to main, required args not provided.
        raise ValueError("boot_count and hostname must have valid values (can't be None)")

    if verbose:
        console.print(f"base_path {base_path}")
        console.print(f"vin {vin}")

    skipped_files = 0
    written_files = 0

    sortable_list = []
    for obd_file in get_json_vin_file_list(base_path, vin, verbose=verbose):

        output_file_path = get_output_file_path(base_path, obd_file.name)

        if verbose:
            console.print(f"Input OBD file {obd_file.name}, Output integrated file {output_file_path.name}")

        if output_file_path.exists() and skip:
            skipped_files += 1
            if verbose:
                console.print(f"skipping input {obd_file.name} output {output_file_path.name}")
            continue

        written_files += 1
        with open(obd_file,  "r") as json_input:
            for line_number, json_record in enumerate(json_input, start=1):
                try:
                    input_record = json.loads(json_record)

                except json.decoder.JSONDecodeError as e:
                    # improperly closed JSON file
                    if verbose:
                        print(f"Corrupted JSON info {obd_file.name} line {line_number}:\n{e}")
                    break

                sortable_list.append(input_record)

        for companion_file in get_companion_json_file_list(base_path, obd_file.name, verbose=verbose):
            if verbose:
                console.print(f"OBD file {obd_file.name} companion file {companion_file.name}")

            with open (companion_file, "r") as json_input:
                for line_number, json_record in enumerate(json_input, start=1):
                    try:
                        input_record = json.loads(json_record)
                        sortable_list.append(input_record)

                    except json.decoder.JSONDecodeError as e:
                        # improperly closed JSON file
                        if verbose:
                            print(f"Corrupted JSON info {companion_file.name} line {line_number}:\n{e}")
                        break

        # Sort using key "<iso_ts_pre><iso_ts_post><command_name>"
        if verbose:
            console.print(f"sorting {len(sortable_list)}")
        sortable_list.sort(key=sort_key)

        # Remove duplicate records
        if verbose:
            console.print(f"sorted list {len(sortable_list)} before un-duplicating")

        un_duplicate_list = {sort_key(record): record for record in sortable_list}
        un_duplicate_list = [record for k, record in un_duplicate_list.items()]

        if verbose:
            print(f"sorted list {len(un_duplicate_list)} after un-duplicating")

        # write sorted_list to file
        if verbose:
            console.print("writing sorted list")

        write_json_data_to_integrated_file(un_duplicate_list, output_file_path, verbose=verbose)

    if verbose:
        console.print(f"Integrated Files Written {written_files}, Files Skipped {skipped_files}")

    return

if __name__ == "__main__":
    args = command_line_options()
    main(args=args,)

