# telemetry-trailer-connector/trlr_logger/trlr_logger.py
"""
Telemetry Trailer Connector UDP (WIFI) Logger
"""
from argparse import ArgumentParser
import logging
from sys import stdout, stderr
from datetime import datetime, timezone
from os import fsync
from pathlib import Path
from datetime import datetime, timezone
from os import fsync
import json

from tcounter.common import (
    get_output_file_name,
    get_next_application_counter_value,
    BASE_PATH,
)

from .__version__ import __version__
from .udp import (
    TrailerConnector,
    DEFAULT_LOCAL_HOST_UDP_PORT_NUMBER,
    DEFAULT_RECORD_TYPE,
)

logger = logging.getLogger("tc_logger")

def argument_parsing()-> dict:
    """Argument parsing"""
    parser = ArgumentParser(description="Telemetry Trailer Connector UDP Logger")
    parser.add_argument(
        "base_path",
        nargs='?',
        metavar="base_path",
        default=[BASE_PATH, ],
        help=f"Relative or absolute output data directory. Defaults to '{BASE_PATH}'."
    )
    parser.add_argument(
        "--udp_port_number",
        type=int,
        default=DEFAULT_LOCAL_HOST_UDP_PORT_NUMBER,
        help=f"TCP/IP UDP port number for receiving datagrams. Defaults to '{DEFAULT_LOCAL_HOST_UDP_PORT_NUMBER}'"
    )
    parser.add_argument(
        "--log_file_directory",
        default=BASE_PATH,
        help=f"Place log files into this directory - defaults to {BASE_PATH}"
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

def dict_to_log_format(tc_record:dict) -> dict:
    """
    Converts weather report output to obd-logger output format:
    {
        'command_name': DEFAULT_RECORD_TYPE,
        'obd_response_value': "result of said command",
        'iso_ts_pre': "ISO format Linux time before running said command",
        'iso_ts_post': "ISO format Linux time after running said command",
    }
    """
    return {
        "command_name": DEFAULT_RECORD_TYPE,
        "obd_response_value": tc_record,
    }

def get_directory(base_path) -> Path:
    """Generate directory where data files go."""
    path = Path(base_path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_log_file_handle(base_path:str, base_name="trlr"):
    """return a file handle opened for writing to a log file"""
    full_path = get_directory(base_path) / get_output_file_name(base_name, base_path=base_path)

    logger.info(f"log file full path: {full_path}")

    log_file_handle = None

    try:
        log_file_handle = open(full_path, mode='x', encoding='utf-8')
    except FileExistsError:
        logger.error(f"get_log_file_handle(): FileExistsError: {full_path}")
        tc_counter = get_next_application_counter_value(base_name)
        logger.error(f"get_log_file_handle(): Incremented '{base_name}' counter to {tc_counter}")

        # recursion to get to the next free application counter value
        return get_log_file_handle(base_path, base_name=base_name)

    return log_file_handle

def main():
    """Run main function."""

    args = argument_parsing()

    if args['version']:
        print(f"Version {__version__}", file=stdout)
        exit(0)

    verbose = args['verbose']
    log_file_directory = args['log_file_directory']

    logging_level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(stream=stderr, level=logging_level)

    logger.debug(f"argument --verbose: {verbose}")

    logger.info(f"log_file_directory: {log_file_directory}")
    log_file_handle = get_log_file_handle(log_file_directory)

    # reads Trailer Connector input
    tc_reports = TrailerConnector(logger)

    iso_ts_pre = datetime.isoformat(datetime.now(tz=timezone.utc))

    for raw_record, record in tc_reports:
        logger.debug(f"raw record: {raw_record}")
        if not record:
            # skipping invalid (None value) data
            continue

        log_value = dict_to_log_format(record)

        log_value['iso_ts_pre'] = iso_ts_pre
        log_value['iso_ts_post'] = datetime.isoformat(datetime.now(tz=timezone.utc))

        logger.debug(f"logging: {log_value}")

        log_file_handle.write(json.dumps(log_value) + "\n")
        log_file_handle.flush()
        fsync(log_file_handle.fileno())

        iso_ts_pre = datetime.isoformat(datetime.now(tz=timezone.utc))

if __name__ == "__main__":
    main()
