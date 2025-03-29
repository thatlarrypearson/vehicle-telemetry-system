# OBD Log To CSV
# obd_log_to_csv/obd_log_to_csv.py
import json
import csv
from sys import stdout, stderr
from argparse import ArgumentParser
from io import TextIOWrapper
from pint import UnitRegistry, UndefinedUnitError, OffsetUnitCalculusError
from dateutil import parser
from .obd_log_common import (
    get_list_command_name, base_command_name_filter, pint_to_value_type, get_field_names,
    date_time_fields
)

def null_out_output_record(output_record:dict, commands:list) -> None:
    """Nulls out the values within the output record dictionary.
    """
    for column_name in csv_header(commands):
        output_record[column_name] = None

def csv_header(commands:list) -> list:
    return commands + date_time_fields

def input_file(json_input:TextIOWrapper, commands:list, csv_output:TextIOWrapper,
                header:bool=True, verbose:bool=False) -> None:
    """process input file given an open file handle for input,
        a list of OBD commands to include in the output and
        an output file handle for the CSV output file.
    """
    commands = get_field_names(commands)
    output_record = {}
    null_out_output_record(output_record, commands)
    output_record_is_nulled_out = True

    writer = csv.DictWriter(csv_output, fieldnames=csv_header(commands), escapechar="\\")

    if verbose:
        print(f"CSV field names: {csv_header(commands)}", file=stderr)

    if header:
        writer.writeheader()

    for line_number, json_record in enumerate(json_input, start=1):
        try:
            input_record = json.loads(json_record)
        except json.decoder.JSONDecodeError as e:
            # improperly closed JSON file
            if verbose:
                print(f"Corrupted JSON info:\n{e}", file=stderr)
            return

        if not base_command_name_filter(input_record['command_name'], commands):
            if verbose:
                print(f"base_command_name_filter({input_record['command_name']}) returned False")
            continue

        if verbose:
            print(f"input_record: {input_record['command_name']} value: {input_record['obd_response_value']}", file=stderr)

        write_row = False
        if isinstance(input_record['obd_response_value'], dict):
            for field_name, obd_response_value in input_record['obd_response_value'].items():
                command_name = f"{input_record['command_name']}-{field_name}"
                if command_name not in commands and input_record['command_name'] not in commands:
                    if verbose:
                        print(f"dict command_name {command_name} not in commands")
                    continue
                if command_name not in commands:
                    # then the root command name is in commands and the command with field name needs to be added to commands
                    if verbose:
                        print(f"dict command_name {command_name} added to commands")
                    commands.append(command_name)
                if verbose:
                    print(f"dict: {input_record['command_name']} to {command_name}: value: {obd_response_value}", file=stderr)
                if command_name in output_record and output_record[command_name]:
                    output_record['iso_ts_post'] = parser.isoparse(input_record['iso_ts_pre'])
                    write_row = True
                    break
        elif isinstance(input_record['obd_response_value'], list):
            for obd_response_index, obd_response_value in enumerate(input_record['obd_response_value'], start=0):
                command_name = get_list_command_name(input_record['command_name'], obd_response_index)
                if command_name not in commands and input_record['obd_response_value'] not in commands:
                    if verbose:
                        print(f"list command_name {command_name} not in commands")
                    continue
                if command_name not in commands:
                    # then the root command name is in commands and the command with field name needs to be added to commands
                    if verbose:
                        print(f"list command_name {command_name} added to commands")
                    commands.append(command_name)
                if verbose:
                    print(f"list: {input_record['command_name']} to {command_name}: value: {obd_response_value}", file=stderr)
                if command_name in output_record and output_record[command_name]:
                    output_record['iso_ts_post'] = parser.isoparse(input_record['iso_ts_pre'])
                    write_row = True
                    break
        else:
            command_name = input_record['command_name']
            if verbose:
                print(f"{command_name}: value: {input_record['obd_response_value']}", file=stderr)

            if command_name in commands and output_record[command_name]:
                output_record['iso_ts_post'] = parser.isoparse(input_record['iso_ts_pre'])
                write_row = True

        if write_row:
            if verbose:
                print(f"====================================\noutput_record: {output_record}\n====================================", file=stderr)
            output_record['duration'] = output_record['iso_ts_post'] - output_record['iso_ts_pre']
            # remove keys/value pairs from output_record where the key doesn't match a command in commands
            filtered_output_record = {k: v for k, v in output_record.items() if k in commands}
            writer.writerow(filtered_output_record)

            null_out_output_record(output_record, commands)
            output_record_is_nulled_out = True

        if output_record_is_nulled_out:
            try:
                output_record['iso_ts_pre'] = parser.isoparse(input_record['iso_ts_pre'])
            except KeyError:
                print(f"KeyError: 'iso_ts_pre' {line_number}: {input_record}")
                exit(1)
            output_record_is_nulled_out = False

        if isinstance(input_record['obd_response_value'], dict):
            for field_name, obd_response_value in input_record['obd_response_value'].items():
                command_name = f"{input_record['command_name']}-{field_name}"
                if command_name not in commands and input_record['command_name'] not in commands:
                    continue
                output_record[command_name], pint_value = pint_to_value_type(obd_response_value, verbose)
        elif isinstance(input_record['obd_response_value'], list):
            for obd_response_index, obd_response_value in enumerate(input_record['obd_response_value'], start=0):
                command_name = get_list_command_name(input_record['command_name'], obd_response_index)
                if command_name not in commands and input_record['obd_response_value'] not in commands:
                    continue
                output_record[command_name], pint_value = pint_to_value_type(obd_response_value, verbose)
        else:
            command_name = input_record['command_name']
            output_record[command_name], pint_value = pint_to_value_type(input_record['obd_response_value'], verbose)

    if not output_record_is_nulled_out: 
        if verbose:
            print(f"====================================\noutput_record: {output_record}\n====================================", file=stderr)
        output_record['iso_ts_post'] = parser.isoparse(input_record['iso_ts_pre'])
        output_record['duration'] = output_record['iso_ts_post'] - output_record['iso_ts_pre']
        final_output_record = {k: v for k, v in output_record.items() if k in commands}
        writer.writerow(final_output_record)

    return

def cycle_through_input_files(json_input_files:list, commands:list, header:bool, csv_output_file:TextIOWrapper, verbose=False):
    for json_input_file_name in json_input_files:
        if verbose:
            print(f"processing input file {json_input_file_name}", file=stderr)
        with open(json_input_file_name, "r") as json_input:
            input_file(json_input, commands, csv_output_file,
                        header=header, verbose=verbose)
        header = False

    return

def command_line_options()->dict:
    parser = ArgumentParser(prog="obd_log_to_csv", description="Telemetry OBD Log To CSV")

    parser.add_argument(
        "--commands",
        help="""Command name list to include in CSV output record generation.
                Comma separated list.  e.g. "SPEED,RPM,FUEL_RATE".
                In the JSON input, "command_name" labelled items will be used.
                No default value provided.
                """,
    )

    parser.add_argument(
        "--csv",
        help="""CSV output file.
                File can be either a full or relative path name.
                If the file already exists, it will be overwritten.
                Defaults to standard output (stdout) instead of file.
                """,
        default="stdout",
    )

    parser.add_argument(
        "--no_header",
        help="""CSV output file will NOT have a column name header record.
                Default is False.  (That is, a header will be produced by default.)
        """,
        default=False,
        action='store_true'
    )

    parser.add_argument(
        "--verbose",
        help="Turn verbose output on. Default is off.",
        default=False,
        action='store_true'
    )

    parser.add_argument(
        "files",
        help="""telemetry_obd generated data files separated by spaces.
                Data file names can include full or relative paths.
            """,
        default=None,
        nargs="+",
    )

    return vars(parser.parse_args())


def main(json_input_files=None, csv_output_file_name='stdout', header=True, verbose=False, commands=None):
    if json_input_files is None:
        args = command_line_options()

        json_input_files = args['files']
        csv_output_file_name = args['csv']
        header = not args['no_header']
        verbose = args['verbose']
        commands = (args['commands']).split(sep=',')

    if not commands:
        raise ValueError("required argument is None, should be a comma separated list of OBD commands")

    if verbose:
        print(f"verbose: {args['verbose']}", file=stderr)
        print(f"commands: {args['commands']}", file=stderr)
        print(f"header: {header}", file=stderr)
        print(f"files: {json_input_files}", file=stderr)
        print(f"csv: {csv_output_file_name}", file=stderr)

    if csv_output_file_name != "stdout":
        with open(csv_output_file_name, "w") as csv_output_file:
            cycle_through_input_files(json_input_files, commands, header, csv_output_file, verbose=verbose)
    else:
        cycle_through_input_files(json_input_files, commands, header, stdout, verbose=verbose)

if __name__ == "__main__":
    main()
