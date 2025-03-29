# telemetry-counter/counter/app_counter.py
"""Returns the app start count to the calling shell."""

from argparse import ArgumentParser
from .common import (
    get_application_counter_value,
    get_next_application_counter_value,
    get_count_file_path,
    APPLICATION_LIST,
)
from .__init__ import __version__

def argument_parsing()-> dict:
    """Argument parsing"""
    parser = ArgumentParser(description="Telemetry Application Start Counter")

    parser.add_argument(
        "application_id",
        nargs=1,
        metavar="application_id",
        # default=[None, ],
        help=f"Application Identifier must be one of {APPLICATION_LIST}."
    )

    parser.add_argument(
        "--app_count_file_location",
        help="Print application start count file location and exit.",
        default=False,
        action='store_true'
    )

    parser.add_argument(
        "--current_app_count",
        help="Print current application start count and exit.",
        default=False,
        action='store_true'
    )

    parser.add_argument(
        "--version",
        help=f"Print version number ({__version__}) and exit.",
        default=False,
        action='store_true'
    )
    return vars(parser.parse_args())

def main():
    """Run main function."""

    args = argument_parsing()

    application_id = args['application_id'][0]
    if application_id not in APPLICATION_LIST:
        print(f"ValueError: required argument application_id {application_id} not in {APPLICATION_LIST}")
        exit(1)

    if args['version']:
        print(f"app_counter version: {__version__}")
        exit(0)

    if args['current_app_count']:
        app_count_string =  (f"{get_application_counter_value(application_id):10d}").replace(' ', '0')
        print(app_count_string)
        exit(0)

    if args['app_count_file_location']:
        print(f"{get_count_file_path(application_id)}")
        exit(0)

    app_count_string =  (f"{get_next_application_counter_value(application_id):10d}").replace(' ', '0')
    print(app_count_string)

if __name__ == "__main__":
    main()
