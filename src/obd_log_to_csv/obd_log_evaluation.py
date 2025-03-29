# OBD Log Evaluation
# telemetry-obd-log-to-csv/obd_log_to_csv/obd_log_evaluation.py
import json
import csv
from sys import stdout, stderr
from argparse import ArgumentParser
from rich.console import Console
from rich.table import Table
from .obd_log_common import get_list_command_name, pint_to_value_type, get_mode_pid_from_command_name

def csv_print(raw_data:dict, verbose=False):
    field_names = [
        'command',
        'mode',
        'pid',
        'count',
        'no response',
        'data type',
        'units',
    ]
    writer = csv.DictWriter(stdout, fieldnames=field_names)
    writer.writeheader()
    
    for key, value in sorted(raw_data.items()):
        if verbose:
            print(f"csv_print(): key {key}", file=stderr)
        value['command'] = key
        if not key.startswith("NMEA"):
            try:
                mode, pid = get_mode_pid_from_command_name(key)
            except ValueError:
                mode, pid = '??', '??'

            value['mode'] = f"0x{mode}"
            value['pid'] = f"0x{pid}"
        else:
            value['mode'] = ""
            value['pid'] = ""
        writer.writerow(value)

def rich_output(raw_data:dict, title=None, width=None, verbose=False):
    console = Console()

    if not title:
        table = Table(
            show_header=True,
            header_style="bold magenta",
            title="OBD Log Evaluation",
            width=width,
        )
    else:
        table = Table(
            show_header=True,
            header_style="bold magenta",
            title=title,
            width=width,
        )
    table.add_column("OBD Command", justify='left')
    table.add_column("Mode")
    table.add_column("PID")
    table.add_column("Count", justify='right')
    table.add_column("No Response", justify='right')
    table.add_column('Data Type', justify='left')
    table.add_column("Units", justify="left")

    count_total = 0
    no_response_total = 0

    for key, value in sorted(raw_data.items()):
        count_total += value['count']
        no_response_total += value['no response']

        value_key = key
        if not key.startswith("NMEA"):
            try:
                mode, pid = get_mode_pid_from_command_name(key)
            except ValueError:
                mode, pid = '??', '??'
            value_mode = f"0x{mode}"
            value_pid = f"0x{pid}"
        else:
            value_mode = "----"
            value_pid = "----"
        value_count = str(value['count'])
        value_no_response = str(value['no response'])

        if value['count'] == value['no response']:
            value_key = f"[bold red]{key}[/bold red]"
            value_count = f"[bold red]{value['count']}[/bold red]"
            value_mode = f"[bold red]{value_mode}[/bold red]"
            value_pid = f"[bold red]{value_pid}[/bold red]"
        if value['no response'] > 0:
            value_no_response = f"[bold red]{value['no response']}[/bold red]"

        table.add_row(
            value_key,
            value_mode,
            value_pid,
            value_count,
            value_no_response,
            value['data type'],
            value['units'],
        )

    table.add_row(
        '[bold]TOTALS[/bold]',
        '',
        '',
        f"[bold]{count_total}[/bold]",
        f"[bold red]{no_response_total}[/bold red]",
        '',
        ''
    )

    console.print(table)


def get_data_type(data)->str:
    if isinstance(data, str):
        return 'string'
    if isinstance(data, int):
        return 'integer'
    if isinstance(data, float):
        return 'float'
    if isinstance(data, bool):
        return 'bool'
    return None

def command_name_in_raw_data(command_name:str, raw_data:dict):
    """
    when command_name is/isn't in raw data
    """
    if command_name in raw_data:
        raw_data[command_name]['count'] += 1
    else:
        raw_data[command_name] = {
            'count': 1,
            'no response': 0,
            'data type': None,
            'units': None,
        }

def pint_to_raw_data(command_name:str, obd_response_value, raw_data:dict, verbose=False):
    """
    decompose pint values and store data type and units in raw_data
    """
    value, pint_units = pint_to_value_type(obd_response_value, verbose)
    data_type = get_data_type(value)
    if verbose:
        print(f"pint_to_raw_data: command_name: {command_name} value: {value}, pint_units: {pint_units} data_type: {data_type}", file=stderr)
    if data_type:
        raw_data[command_name]['data type'] = data_type
    if pint_units:
        raw_data[command_name]['units'] = pint_units

def input_record_single_value(input_record:dict, raw_data:dict, verbose=False):
    """
    process an obd_response_value of single value type
    """
    command_name = input_record['command_name']
    obd_response_value = input_record['obd_response_value']
    command_name_in_raw_data(command_name, raw_data)

    if obd_response_value in ['no response', 'not supported']:
        raw_data[command_name]['no response'] += 1
        return

    pint_to_raw_data(command_name, obd_response_value, raw_data, verbose=verbose)

def input_record_list(input_record:dict, raw_data:dict, verbose=False):
    """
    process an obd_response_value of type list
    """
    command_name = input_record['command_name']
    obd_response_values = input_record['obd_response_value']
    command_name_in_raw_data(command_name, raw_data)

    for obd_response_index, obd_response_value in enumerate(obd_response_values, start=0):
        command_name = get_list_command_name(input_record['command_name'], obd_response_index)

        command_name_in_raw_data(command_name, raw_data)

        if obd_response_value in ['no response', 'not supported']:
            raw_data[command_name]['no response'] += 1
            break

        pint_to_raw_data(command_name, obd_response_value, raw_data, verbose=verbose)

def input_record_dict(input_record:dict, raw_data:dict, verbose=False):
    """
    process an obd_response_value of type dict
    """
    command_name = input_record['command_name']
    obd_response_values = input_record['obd_response_value']
    command_name_in_raw_data(command_name, raw_data)

    for field_name, obd_response_value in obd_response_values.items():
        command_field_name = f"{command_name}-{field_name}"

        command_name_in_raw_data(command_field_name, raw_data)

        if obd_response_value in ['no response', 'not supported'] or (
            obd_response_value is None) or (
            isinstance(obd_response_value, str) and len(obd_response_value) == 0):

            raw_data[command_field_name]['no response'] += 1
            break

        pint_to_raw_data(command_field_name, obd_response_value, raw_data, verbose=verbose)

def input_file(json_input_files:list, verbose=False)->dict:
    """
    process an input file and return dict structure containing results
    """
    raw_data = {}

    for json_input_file_name in json_input_files:
        if verbose:
            print(f"processing input file {json_input_file_name}", file=stderr)
        with open(json_input_file_name, "r") as json_input:
            for json_record in json_input:
                try:
                    input_record = json.loads(json_record)
                except json.decoder.JSONDecodeError as e:
                    # improperly closed JSON file
                    if verbose:
                        print(f"Corrupted JSON info:\n{e}", file=stderr)
                    break

                obd_response_value = input_record['obd_response_value']

                if isinstance(obd_response_value, dict):
                    input_record_dict(input_record, raw_data, verbose=verbose)
                elif isinstance(obd_response_value, list):
                    input_record_list(input_record, raw_data, verbose=verbose)
                else:
                    input_record_single_value(input_record, raw_data, verbose=verbose)

    return raw_data

def command_line_options()->dict:
    parser = ArgumentParser(prog="obd_log_evaluation",
                        description="""OBD Log Evaluation
                        performs simple analysis on telemetry_obd.obd_logger
                        and telemetry_obd.obd_command_tester output files.
                        The analysis is oriented toward validating obd_logger
                        config files and providing units for each OBD command.
                        """)

    parser.add_argument(
        "--verbose",
        help="Turn verbose output on. Default is off.",
        default=False,
        action='store_true'
    )

    parser.add_argument(
        "--csv",
        help="Output CSV on stdout.  Default is to rich table print on stdout.",
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


def main(json_input_files=None, verbose=False, csv_output=False):
    if json_input_files:
        main_as_function = True
        args = {
            'files': json_input_files,
            'verbose': verbose,
            'csv': csv_output,
        }
    else:
        main_as_function = False
        args = command_line_options()
        json_input_files = args['files']
        verbose = args['verbose']
        csv_output = args['csv']

    if verbose:
        print(f"verbose: {verbose}", file=stderr)
        print(f"csv: {csv_output}", file=stderr)
        print(f"files: {json_input_files}", file=stderr)

    raw_data = input_file(json_input_files, verbose=verbose)

    if not csv_output:
        rich_output(raw_data, verbose=verbose)
    else:
        csv_print(raw_data, verbose=verbose)
    
    if main_as_function:
        return raw_data
    
    exit(0)
        

if __name__ == "__main__":
    main()
