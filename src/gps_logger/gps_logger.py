# telemetry-gps/gps_logger/gps_logger.py
"""
GPS Logger
"""
from argparse import ArgumentParser
import logging
from sys import stdout, stderr
from os import fsync
from datetime import datetime, timezone
import json

from pyubx2 import UBXReader

from .__init__ import __version__
from .gps_config import (
    parsed_data_to_dict,
    get_log_file_handle,
)
from .connection import (
    initialize_gps,
    dict_to_log_format,
)
from .usb_devices import get_serial_device_name
from tcounter.common import (
    BASE_PATH
)

DEFAULT_SERIAL_DEVICE=get_serial_device_name()
TIMEOUT=1.0
MESSAGE_RATE=1

logger = logging.getLogger("gps_logger")

def argument_parsing()-> dict:
    """Argument parsing"""
    parser = ArgumentParser(description="Telemetry GPS Logger")

    parser.add_argument(
        "base_path",
        nargs='?',
        metavar="base_path",
        default=BASE_PATH,
        help=f"Relative or absolute output data directory. Defaults to '{BASE_PATH}'."
    )

    parser.add_argument(
        "--message_rate",
        default=MESSAGE_RATE,
        type=int,
        help=f"Number of whole seconds between each GPS fix.  Defaults to {MESSAGE_RATE}."
    )

    parser.add_argument(
        "--serial",
        default=DEFAULT_SERIAL_DEVICE,
        help=f"Full path to the serial device where the GPS can be found, defaults to {DEFAULT_SERIAL_DEVICE}"
    )

    parser.add_argument(
        "--verbose",
        default=False,
        action='store_true',
        help="Turn DEBUG logging on. Default is off."
    )

    parser.add_argument(
        "--version",
        default=False,
        action='store_true',
        help="Print version number and exit."
    )

    return vars(parser.parse_args())

def main():
    """Run main function."""

    args = argument_parsing()

    if args['version']:
        print(f"Version {__version__}", file=stdout)
        exit(0)

    verbose = args['verbose']
    serial_device = args['serial']
    message_rate = args['message_rate']
    base_path = args['base_path']

    logging_level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(stream=stderr, level=logging_level)

    logging.debug(f"main(): argument --verbose: {verbose}")

    logging.info(f"main(): base path: {base_path}")

    log_file_handle = get_log_file_handle(base_path=base_path)
    logging.info(f"main(): log file name: {log_file_handle.name}")

    io_handle = initialize_gps(serial_device, message_rate)

    # reads NMEA, UBX and RTM input
    gps_reader = UBXReader(io_handle)

    logging.debug("main(): gps_reader active.")

    iso_ts_pre = datetime.isoformat(datetime.now(tz=timezone.utc))

    for (raw_data, parsed_data) in gps_reader:
        data_dict = parsed_data_to_dict(parsed_data)

        logging.debug(f"main(): GPS data {data_dict}")

        if 'umsg_name' in data_dict and data_dict['umsg_name'] == 'MON-VER':
            gps_software = data_dict
            logging.info(f"main(): GPS SOFTWARE: {data_dict}")

        if 'umsg_name' in data_dict and data_dict['umsg_name'] == 'MON-HW':
            gps_hardware = data_dict
            logging.info(f"main(): GPS HARDWARE: {data_dict}")

        if data_dict['Message_Type'] != "NMEA":
            # "Skipping UBX and RTM messages"
            logging.debug(f"main(): skipping Message_Type {data_dict['Message_Type']}")
            iso_ts_pre = datetime.isoformat(datetime.now(tz=timezone.utc))
            continue

        log_value = dict_to_log_format(data_dict)

        log_value['iso_ts_pre'] = iso_ts_pre
        log_value['iso_ts_post'] = datetime.isoformat(datetime.now(tz=timezone.utc))

        logging.debug(f"main(): logging: {log_value}")

        if log_file_handle:
            log_file_handle.write(json.dumps(log_value) + "\n")
            log_file_handle.flush()
            fsync(log_file_handle.fileno())

        iso_ts_pre = datetime.isoformat(datetime.now(tz=timezone.utc))

if __name__ == "__main__":
    main()
