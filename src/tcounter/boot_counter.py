# telemetry-counter/counter/boot_counter.py
"""Returns the boot count to the calling shell."""

from argparse import ArgumentParser
from .common import (
    get_boot_count,
    get_next_boot_counter_value,
    get_boot_count_file_path,
)
from .__init__ import __version__


def argument_parsing()-> dict:
    """Argument parsing"""
    parser = ArgumentParser(description="Telemetry Boot Counter")

    parser.add_argument(
        "--boot_count_file_location",
        help="Print boot count file location and exit.",
        default=False,
        action='store_true'
    )

    parser.add_argument(
        "--current_boot_count",
        help="Print current boot count and exit.",
        default=False,
        action='store_true'
    )

    parser.add_argument(
        "--version",
        help=f"Print version ({__version__}) number and exit.",
        default=False,
        action='store_true'
    )
    return vars(parser.parse_args())

def main():
    """Run main function."""

    args = argument_parsing()

    if args['version']:
        print(f"boot_counter version: {__version__}")
        exit(0)

    if args['current_boot_count']:
        boot_count_string =  (f"{get_boot_count():10d}").replace(' ', '0')
        print(boot_count_string)
        exit(0)

    if args['boot_count_file_location']:
        print(f"{get_boot_count_file_path()}")
        exit(0)

    boot_count_string =  (f"{get_next_boot_counter_value():10d}").replace(' ', '0')
    print(boot_count_string)

if __name__ == "__main__":
    main()
