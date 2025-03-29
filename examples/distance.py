# telemetry-obd-log-to-csv/obd_log_to_csv/distance.py
"""
Example program showing how to read through CSV file to extract and transform data.

NOTE: Input CSV files must have column headers in the first line of the file.  IE - don't use --no_headers on obd_log_to_csv.

NOTE: The column names in the input CSV files must have the same column names and be in the same order.

NOTE: Requires additional Python package
      https://pypi.org/project/pytimeparse/1.1.5/
      python3.8 -m pip install pytimeparse

SPEED is in kilometers per hour
duration is in seconds
"""
from sys import stdout, stderr
from argparse import ArgumentParser
from io import TextIOWrapper
from csv import DictReader, DictWriter
from copy import deepcopy
from pytimeparse import parse

def process_file(csv_input:TextIOWrapper, csv_output_file:TextIOWrapper, header:bool=False, verbose:bool=False):
    """convert speed and time to distance"""
    reader = DictReader(csv_input)
    field_names = reader.fieldnames
    all_field_names = field_names + [
        'distance', 'distance_sum',
        'miles', 'miles_sum',
    ]
    if "DISTANCE_SINCE_DTC_CLEAR" in field_names:
        all_field_names += ['miles_since_dtc_clear', ]

    if verbose:
        print(f"field_names: {field_names}, all_field_names: {all_field_names}", file=stderr)

    if "SPEED" not in field_names or "duration" not in field_names:
        raise ValueError(f"SPEED and/or duration not in {field_names}")

    writer = DictWriter(csv_output_file, fieldnames=all_field_names)

    if header:
        writer.writeheader()

    distance_sum = 0.0
    miles_since_dtc_clear = None

    for line_count, in_row in enumerate(reader, 2):
        if verbose:
            print(f"input line {line_count}: {in_row}", file=stderr)

        # the original row passes through unmolested
        out_row = deepcopy(in_row)

        duration = parse(in_row['duration'])

        if not in_row['SPEED']:
            print(f"input line {line_count}: SPEED has None value, skipping row", file=stderr)
            continue
        if not in_row['duration']:
            raise ValueError(f"input line {line_count}: duration has None or zero value")

        distance = float(in_row['SPEED']) * duration / 3600.0
        distance_sum += distance

        miles_since_dtc_clear = None
        if 'DISTANCE_SINCE_DTC_CLEAR' in out_row and out_row['DISTANCE_SINCE_DTC_CLEAR']:
            miles_since_dtc_clear = float(out_row['DISTANCE_SINCE_DTC_CLEAR']) * 0.62137119

        if 'DISTANCE_SINCE_DTC_CLEAR' in out_row:
            out_row['miles_since_dtc_clear'] = miles_since_dtc_clear

        out_row['distance'] = distance
        out_row['miles'] = distance * 0.62137119
        out_row['distance_sum'] = distance_sum
        out_row['miles_sum'] = distance_sum * 0.62137119

        if verbose:
            print(f"output line {line_count}: {out_row}", file=stderr)

        writer.writerow(out_row)

def cycle_through_input_files(csv_input_files:list, csv_output_file:TextIOWrapper, verbose=False):
    header = True
    for csv_input_file_name in csv_input_files:
        if verbose:
            print(f"processing input file {csv_input_file_name}", file=stderr)
        with open(csv_input_file_name, "r") as csv_input:
            process_file(csv_input, csv_output_file, header=header, verbose=verbose)

        header = False



def command_line_options():
    """parse command line options"""
    parser = ArgumentParser(prog="obd_log_to_csv", description="distance = rate * time.  Calculate distance from speed and time.  Compare to distance since DTC clear.")

    parser.add_argument(
        "--csv",
        help="""CSV output file.
                File can be either a full or relative path name.
                If the file already exists, it will be overwritten.
                Defaults to terminal output (stdout).
                """,
        default="stdout"
    )

    parser.add_argument(
        "--verbose",
        help="Turn verbose output on. Default is off.",
        default=False,
        action='store_true'
    )

    parser.add_argument(
        "files",
        help="""obd_log_to_csv generated data files separated by spaces.
                Data file names can include full or relative paths.
            """,
        default=None,
        nargs="+",
    )

    return vars(parser.parse_args())

def main():
    """use python -m obd_log_to_csv.distance [args] to run this program."""

    args = command_line_options()

    csv_input_files = args['files']
    csv_output_file_name = args['csv']
    verbose = args['verbose']

    if verbose:
        print(f"verbose: {verbose}", file=stderr)
        print(f"files: {csv_input_files}", file=stderr)
        print(f"csv: {csv_output_file_name}", file=stderr)

    header = True

    if csv_output_file_name != "stdout":
        with open(csv_output_file_name, "w") as csv_output_file:
            cycle_through_input_files(csv_input_files, csv_output_file, verbose=verbose)
    else:
        cycle_through_input_files(csv_input_files, stdout, verbose=verbose)

if __name__ == "__main__":
    main()
    exit(0)
