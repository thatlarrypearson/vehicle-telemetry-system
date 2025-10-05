# telemetry-gps/gps_logger/adafruit_ultimate_gps_logger.py
"""
Adafruit Ultimate GPS GNSS with USB
GPS Logger
"""
from argparse import ArgumentParser
import logging
from sys import stdout, stderr
from os import fsync
from datetime import datetime, timezone
import json
from serial import Serial
from serial.tools.list_ports import comports
from pathlib import Path
from pynmeagps import NMEAReader
from pyubx2.ubxhelpers import gnss2str

from tcounter.common import (
    get_output_file_name,
    get_next_application_counter_value,
    BASE_PATH
)

from .__init__ import __version__

from tcounter.common import (
    BASE_PATH
)

logger = logging.getLogger("gps_logger")

# The following are specific to the Adafruit Ultimate GPS GNSS receiver
DEFAULT_USB_VID = 4292
DEFAULT_USB_PID = 60000
GPS_DEVICE_NAME = "Adafruit Ultimate GPS GNSS Receiver"
DEFAULT_SERIAL_DEVICE="/dev/ttyUSB0"

def get_serial_device_name(verbose=False, default_serial_device=DEFAULT_SERIAL_DEVICE)->str:
    """Get serial device name for GPS"""

    logging.info("Candidate Serial Device List (non-USB devices excluded)")
    i = 0
    return_device = None

    for p in comports():
        vid = p.vid
        if not vid:
            # not a USB device
            continue

        device = p.device
        pid = p.pid

        i += 1
        logging.info(f"{i:3} {device}")
        logging.info(f"\tName: {p.name}")
        logging.info(f"\tUSB VID: {vid} type {type(vid)}")
        logging.info(f"\tUSB PID: {pid} type {type(pid)}")
        logging.info(f"\tDescription: {p.description}")
        logging.info(f"\tHardware ID: {p.hwid}")
        logging.info(f"\tManufacturer: {p.manufacturer}")
        logging.info(f"\tProduct: {p.product}")
        logging.info(f"\tSerial Number: {p.serial_number}")
        logging.info(f"\tLocation: {p.location}")
        logging.info(f"\tinterface: {p.interface}")
        logging.info(f"\tdevice: {device}")
        logging.info(f"\tdevice_path: {p.device_path}")
        logging.info(f"\tusb_device_path: {p.usb_device_path}")

        if p.vid == DEFAULT_USB_VID and p.pid == DEFAULT_USB_PID:
            return_device = device
            logging.info(f"** DEVICE FOUND: {return_device} **")

    logging.info(f"{i} USB Serial Device(s) Found")

    if return_device:
        return return_device

    logging.info(f"USB Attached GPS Device <{GPS_DEVICE_NAME}> not found.")
    logging.info(f"Using Default Serial Device <{default_serial_device}>.")

    return default_serial_device

def parsed_data_to_dict(parsed_data) -> dict:
    """
    convert parsed_data (NMEAMessage) to dictionary
    """
    if 'NMEAMessage' not in str(type(parsed_data)):
        raise ValueError(f"Unknown parsed_data type {type(parsed_data)}")

    return_value = {
        "Message_Type": "NMEA",
        "talker_identifier": parsed_data._talker,
        "sentence_formatter": parsed_data._msgID,
    }

    for parsed_data_attribute in parsed_data.__dict__:
        if not parsed_data_attribute.startswith('_'):
            if parsed_data_attribute.startswith("gnssId"):
                return_value[parsed_data_attribute] = gnss2str(parsed_data.__dict__[parsed_data_attribute])
            if type(parsed_data.__dict__[parsed_data_attribute]) == bytes:
                try:
                    return_value[parsed_data_attribute] = str(parsed_data.__dict__[parsed_data_attribute].rstrip(b"\x00"), "UTF-8")
                except Exception:
                    return_value[parsed_data_attribute] = str(parsed_data.__dict__[parsed_data_attribute].rstrip(b"\x00"))
            else:
                return_value[parsed_data_attribute] = str(parsed_data.__dict__[parsed_data_attribute])

    return return_value

def get_log_file_handle(base_path=BASE_PATH):
    """return a file handle opened for writing to a log file"""
    full_path = get_output_file_name('gps', base_path=base_path)

    logger.info(f"log file full path: {full_path}")

    try:
        # open for exclusive creation, failing if the file already exists
        log_file_handle = open(full_path, mode='x', encoding='utf-8')

    except FileExistsError:
        logger.error(f"get_log_file_handle(): FileExistsError: {full_path}")
        gps_counter = get_next_application_counter_value('gps')
        logger.error(f"get_log_file_handle(): Incremented 'gps' counter to {gps_counter}")
        return get_log_file_handle(base_path=BASE_PATH)

    return log_file_handle

def dict_to_log_format(data_dict:dict)->dict:
    """
    Converts .gps_config.parsed_data_to_dict() output to obd-logger output format:
    {
        'command_name': "name identifier",
        'obd_response_value': "result of said command",
        'iso_ts_pre': "ISO format Linux time before running said command",
        'iso_ts_post': "ISO format Linux time after running said command",
    }
    """
    log_value = {
        "command_name": f"{data_dict['talker_identifier']}{data_dict['sentence_formatter']}",
        "obd_response_value": {},
    }

    for key, value in data_dict.items():
        # filter out "command_name" values
        if key in ("Message_Type", "talker_identifier", "sentence_formatter"):
            continue
        if type(value) == str and not len(value):
            # make empty strings into None
            value = None
        log_value["obd_response_value"][key] = value

    return log_value

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
    if args['serial'] == DEFAULT_SERIAL_DEVICE:
        serial_device = get_serial_device_name()
    else:
        serial_device = args['serial']
    base_path = args['base_path']

    logging_level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(stream=stderr, level=logging_level)

    logging.debug(f"main(): argument --verbose: {verbose}")

    logging.info(f"main(): base path: {base_path}")

    log_file_handle = get_log_file_handle(base_path=base_path)
    logging.info(f"main(): log file name: {log_file_handle.name}")

    io_handle = Serial(serial_device)

    # reads NMEA input
    gps_reader = NMEAReader(io_handle)

    logging.debug("main(): NMEAReader active.")

    iso_ts_pre = datetime.isoformat(datetime.now(tz=timezone.utc))

    for (raw_data, parsed_data) in gps_reader:
        data_dict = parsed_data_to_dict(parsed_data)

        logging.debug(f"main(): GPS data {data_dict}")

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
