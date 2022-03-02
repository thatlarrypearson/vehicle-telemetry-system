# CSV To Delta CSV
# telemetry-obd-log-to-csv/obd_log_to_csv/csv_to_delta_csv.py
from sys import stdout, stderr
import csv
from argparse import ArgumentParser
from io import TextIOWrapper
from copy import deepcopy
from datetime import timedelta
from dateutil import parser


def command_line_options()->dict:
    parser = ArgumentParser(prog="obd_log_to_csv",
                        description="""Telemetry CSV To Delta CSV
                                generates values indicating the rate of change for
                                identified columns.  All original columns pass through
                                unmolested.  The delta columns are added columns.
                                """)

    parser.add_argument(
        "--input_csv_file",
        help="""
        CSV file generated by obd_log_to_csv.obd_log_to_csv that includes the header.
        That is, each column in the file has a valid text column name in the first row.
        """,
    )

    parser.add_argument(
        "--delta",
        help="""
        Comma separated list of commands where successive pairs of non-null return values would
        be used to calculate the rate of change between the two return values.  e.g.
        "SPEED,FUEL_LEVEL,THROTTLE_POSITION".  Calculated from
        "(second-return-value - first-return-value) / (second-iso_ts_post - first-iso_ts_post)".
        Applied in this way, delta SPEED would represent acceleration.
        The results will be in a column headed by delta-COMMAND_NAME.  e.g. delta SPEED column name
        would be "delta-SPEED".
        """,
    )

    parser.add_argument(
        "--output_csv_file",
        help="""CSV output file.
                File can be either a full or relative path name.
                If the file already exists, it will be overwritten.
                Do not make the input and output file the same.
                Bad things will happen.  Defaults to stdout (terminal output).
                """,
        default="stdout"
    )

    parser.add_argument(
        "--verbose",
        help="Turn verbose output on. Default is off.",
        default=False,
        action='store_true'
    )

    return vars(parser.parse_args())

def delta_column_names(delta_columns:list) -> list:
    return [f"delta-{name}" for name in delta_columns]

def delta(input_csv_file, output_csv_file, delta_columns, verbose=False):
    delta_column_name_list = delta_column_names(delta_columns)

    reader = csv.DictReader(input_csv_file)
    field_names = reader.fieldnames

    # check to make sure delta columns map into the input CSV file columns
    for name in (delta_columns + ['iso_ts_pre', 'iso_ts_post', ]):
        if name not in field_names:
            raise ValueError(f"delta column '{name}' missing from CSV input file")

    all_field_names = field_names + delta_column_name_list

    writer = csv.DictWriter(output_csv_file, fieldnames=all_field_names)
    writer.writeheader()

    delta_first = {}
    
    for in_row in reader:
        if verbose:
            print(f"in_row: {in_row}", file=stderr)

        # the original row passes through unmolested
        out_row = deepcopy(in_row)

        # delta columns are added and set to None
        for name in delta_columns:
            if (
                name in delta_first and 
                delta_first[name]['value'] and 
                in_row[name]
            ):
                v1 = float(delta_first[name]['value'])
                v2 = float(in_row[name])
                t1 = parser.isoparse(delta_first[name]['iso_ts_pre'])
                t2 = parser.isoparse(in_row['iso_ts_post'])
                out_row[f"delta-{name}"] = (v2 - v1) / (float((t2 - t1) / timedelta(microseconds=1)) * 1000000.0)

            else:
                out_row[f"delta-{name}"] = None

            if in_row[name]:       
                delta_first[name] = {
                    'value': in_row[name],
                    'iso_ts_pre': in_row['iso_ts_pre'],
                    'iso_ts_post': in_row['iso_ts_post'],
                }

        if verbose:
            print(f"out_row: {out_row}", file=stderr)

        writer.writerow(out_row)

def main():
    args = command_line_options()

    input_csv_file_name = args['input_csv_file']
    output_csv_file_name = args['output_csv_file']
    verbose = args['verbose']

    delta_columns = (args['delta']).split(sep=',') if args['delta'] else []

    if verbose:
        print(f"verbose: {args['verbose']}", file=stderr)
        print(f"input csv file: {input_csv_file_name}", file=stderr)
        print(f"output csv file: {output_csv_file_name}", file=stderr)
        print(f"delta: {delta_columns}", file=stderr)

    if output_csv_file_name != "stdout":
        with open(output_csv_file_name, "w") as output_csv_file:
            with open(input_csv_file_name, "r") as input_csv_file:
                delta(input_csv_file, output_csv_file, delta_columns, verbose=verbose)
    else:
        with open(input_csv_file_name, "r") as input_csv_file:
            delta(input_csv_file, stdout, delta_columns, verbose=verbose)

if __name__ == "__main__":
    main()
