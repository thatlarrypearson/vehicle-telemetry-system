# OBD Log To CSV
# obd_log_to_csv/obd_log_to_csv.py
import json
import csv
import itertools
from sys import stdout, stderr
from argparse import ArgumentParser
from datetime import datetime
from time import sleep
from io import TextIOWrapper
from pint import UnitRegistry, UndefinedUnitError, OffsetUnitCalculusError
from .obd_log_common import (
    get_list_command_name,
    pint_to_value_type,
    get_base_command_name,
    csv_header,
)

def input_file(json_input:TextIOWrapper, commands:list, csv_output:TextIOWrapper,
                header:bool=True, verbose:bool=False) -> None:
    """process input file given an open file handle for input,
        a list of OBD commands to include in the output and
        an output file handle for the CSV output file.
    """

    base_commands = [get_base_command_name(command) for command in commands]
    iso_ts_pre = None

    # Start with a no key/value pairs in dict
    output_record = {}

    writer = csv.DictWriter(
        csv_output,
        fieldnames=csv_header(
            list(
                itertools.chain(
                    commands,
                    # ['iso_ts_pre', 'iso_ts_post', 'duration', ]
                )
            )
        ),
        escapechar="\\",
        extrasaction='ignore'
    )

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

        base_command_name = get_base_command_name(input_record['command_name'])
        if base_command_name not in base_commands:
            # This is NOT a command name we are looking for so get the NEXT input_record
            continue

        # The current output_record gets written when the current input is for a command
        # that has already been added to the output_record.
        if base_command_name in output_record:
            # For the record being output, the ending time boundary ends where the next
            # input field is added.
            output_record['iso_ts_post'] = datetime.fromisoformat(input_record['iso_ts_pre'])
            output_record['iso_ts_pre'] = iso_ts_pre

            # if not isinstance(output_record['iso_ts_post'], datetime):
            #     print(f"output_record['iso_ts_post'] = {output_record['iso_ts_post']} is type {type(output_record['iso_ts_post'])}")
            # if not isinstance(output_record['iso_ts_pre'], datetime):
            #     print(f"output_record['iso_ts_pre'] = {output_record['iso_ts_pre']} is type {type(output_record['iso_ts_pre'])}")
            output_record['duration'] = (output_record['iso_ts_post'] - output_record['iso_ts_pre']).total_seconds()

            # Reset iso_ts_pre so that the next valid command will start its start time
            iso_ts_pre = None

            writer.writerow(output_record)

            # Start again with a no key/value pairs in dict
            output_record = {}

        # For the record being output, the beginning time boundary starts with
        # the first input field that was added.
        if not iso_ts_pre:
            # This is the first command in a CSV output record:
            #   - record the starting timestamp for this record
            iso_ts_pre = datetime.fromisoformat(input_record['iso_ts_pre'])

        # The current command name is in the list and should move to output
        # Trick to get the write(output record) to trigger for dicts and lists:
        # - For single value responses, output_record[command_name] gets filled in
        #   with the correct value.
        output_record[base_command_name] = True
        if isinstance(input_record['obd_response_value'], dict):
            for field_name, obd_response_value in input_record['obd_response_value'].items():
                command_name = f"{input_record['command_name']}-{field_name}"
                output_record[command_name], pint_value = pint_to_value_type(obd_response_value, verbose)
        elif isinstance(input_record['obd_response_value'], list):
            for obd_response_index, obd_response_value in enumerate(input_record['obd_response_value'], start=0):
                command_name = get_list_command_name(input_record['command_name'], obd_response_index)
                output_record[command_name], pint_value = pint_to_value_type(obd_response_value, verbose)
        else:
            command_name = input_record['command_name']
            output_record[command_name], pint_value = pint_to_value_type(input_record['obd_response_value'], verbose)

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
    else:
        args = {
            'json_input_files': json_input_files,
            'csv_output_file_name': csv_output_file_name,
            'header': header,
            'verbose': verbose,
            'commands': commands,
        }

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
