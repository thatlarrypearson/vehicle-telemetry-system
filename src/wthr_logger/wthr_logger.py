# telemetry-wthr/wthr_logger/wthr_logger.py
"""
Weather Logger
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

from .__init__ import __version__
from .udp import WeatherReports, WEATHER_REPORT_EXCLUDE_LIST

logger = logging.getLogger("wthr_logger")


def argument_parsing()-> dict:
    """Argument parsing"""
    parser = ArgumentParser(description="Telemetry Weather Logger")
    parser.add_argument(
        "base_path",
        nargs='?',
        metavar="base_path",
        default=[BASE_PATH, ],
        help=f"Relative or absolute output data directory. Defaults to '{BASE_PATH}'."
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

def dict_to_log_format(weather_report:dict) -> dict:
    """
    Converts weather report output to obd-logger output format:
    {
        'command_name': "name identifier",
        'obd_response_value': "result of said command",
        'iso_ts_pre': "ISO format Linux time before running said command",
        'iso_ts_post': "ISO format Linux time after running said command",
    }
    """
    command_name = weather_report['type']

    obd_response_value = {
        "command_name": f"WTHR_{command_name}",
        "obd_response_value": {},
    }

    for key, value in weather_report.items():
        # filter out "command_name", and serial number values
        if key in ("type", "message_type", "serial_number", "hub_sn"):
            continue
        if type(value) == str and not len(value):
            # make empty strings into None
            value = None
        obd_response_value["obd_response_value"][key] = value

    return obd_response_value

def get_directory(base_path) -> Path:
    """Generate directory where data files go."""
    path = Path(base_path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_log_file_handle(base_path:str, base_name="wthr"):
    """return a file handle opened for writing to a log file"""
    full_path = get_directory(base_path) / get_output_file_name(base_name, base_path=base_path)

    logger.info(f"log file full path: {full_path}")

    try:
        log_file_handle = open(full_path, mode='x', encoding='utf-8')

    except FileExistsError:
        logger.error(f"get_log_file_handle(): FileExistsError: {full_path}")
        wthr_counter = get_next_application_counter_value(base_name)
        logger.error(f"get_log_file_handle(): Incremented '{base_name}' counter to {wthr_counter}")
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

    if log_file_directory:
        logger.info(f"log_file_directory: {log_file_directory}")
        log_file_handle = get_log_file_handle(log_file_directory)
    else:
        log_file_handle = None

    # reads Weather input
    weather_reports = WeatherReports(logger)

    iso_ts_pre = datetime.isoformat(datetime.now(tz=timezone.utc))

    for raw_weather_report, weather_report in weather_reports:
        if not weather_report:
            # skipping invalid (None value) data
            continue

        if weather_report['type'] in WEATHER_REPORT_EXCLUDE_LIST:
            # skipping unwanted weather report types
            logger.debug(f"skipping Message_Type {weather_report['type']}")
            iso_ts_pre = datetime.isoformat(datetime.now(tz=timezone.utc))
            continue

        log_value = dict_to_log_format(weather_report)

        log_value['iso_ts_pre'] = iso_ts_pre
        log_value['iso_ts_post'] = datetime.isoformat(datetime.now(tz=timezone.utc))

        logger.debug(f"logging: {log_value}")

        if log_file_handle:
            log_file_handle.write(json.dumps(log_value) + "\n")
            # want a command line option to disable forced buffer write to disk with default on
            log_file_handle.flush()
            fsync(log_file_handle.fileno())

        iso_ts_pre = datetime.isoformat(datetime.now(tz=timezone.utc))

if __name__ == "__main__":
    main()
