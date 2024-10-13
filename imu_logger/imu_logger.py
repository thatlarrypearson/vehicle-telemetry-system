# telemetry-imu/telemetry_imu/imu_logger.py

from argparse import ArgumentParser
from math import atan2, asin
import logging
from sys import stdout, stderr
from os import fsync
from datetime import datetime, timezone
import json

from tcounter.common import (
    get_output_file_name,
    get_next_application_counter_value,
    BASE_PATH
)

from .usb_devices import get_serial_device_name
from .io import (
    DEFAULT_LOCAL_HOST_UDP_PORT_NUMBER,
    UDP_Reader,
    Serial_Reader,
)

from .__init__ import __version__

logger = logging.getLogger("imu_logger")

def quaternion_to_euler(v:list) -> tuple:
    """
    Convert Quaternion to yaw-pitch-roll
    v is vector of 4 float values and is Quaternion direct from hardware
    returns roll, pitch, yaw in radians
    """
    roll = atan2(
                    2 * ((v[2] * v[3]) + (v[0] * v[1])),
                    v[0]**2 - v[1]**2 - v[2]**2 + v[3]**2
                )
    pitch = asin(
                    2 * ((v[1] * v[3]) - (v[0] * v[2]))
                )
    yaw = atan2(
                    2 * ((v[1] * v[2]) + (v[0] * v[3])),
                    v[0]**2 + v[1]**2 - v[2]**2 - v[3]**2
                )
    return (roll, pitch, yaw)

def get_log_file_handle(base_path=BASE_PATH):
    """return a file handle opened for writing to a log file"""
    full_path = get_output_file_name('imu', base_path=base_path)

    logger.info(f"log file full path: {full_path}")

    # open for exclusive creation, failing if the file already exists
    try:
        log_file_handle = open(full_path, mode='x', encoding='utf-8')

    except FileExistsError:
        logger.error(f"get_log_file_handle(): FileExistsError: {full_path}")
        imu_counter = get_next_application_counter_value('imu')
        logger.error(f"get_log_file_handle(): Incremented 'imu' counter to {imu_counter}")
        return get_log_file_handle(base_path=BASE_PATH)

    return log_file_handle

def argument_parsing()-> dict:
    """Command line argument parsing"""
    parser = ArgumentParser(description="Telemetry IMU Logger")

    parser.add_argument(
        "base_path",
        nargs='?',
        metavar="base_path",
        default=BASE_PATH,
        help=f"Relative or absolute output data directory. Defaults to '{BASE_PATH}'.",
    )

    parser.add_argument(
        "--usb",
        default=False,
        action='store_true',
        help="CircuitPython microcontroller connects via USB is True. Default is False.",
    )

    serial_device_name = get_serial_device_name()

    parser.add_argument(
        "--serial_device_name",
        default=serial_device_name,
        help=f"Name for the hardware IMU serial device. Defaults to {serial_device_name}",
    )

    parser.add_argument(
        "--no_wifi",
        default=False,
        action='store_true',
        help="CircuitPython microcontroller does NOT use WIFI to connect.  Default is False",
    )

    parser.add_argument(
        "--upp_port_number",
        type=int,
        default=DEFAULT_LOCAL_HOST_UDP_PORT_NUMBER,
        help=f"TCP/IP UDP port number for receiving datagrams. Defaults to '{DEFAULT_LOCAL_HOST_UDP_PORT_NUMBER}'"
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
    args = argument_parsing()

    if args['version']:
        print(f"Version {__version__}", file=stdout)
        exit(0)

    verbose = args['verbose']

    logging_level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(stream=stderr, level=logging_level)
    logger.debug(f"argument --verbose: {verbose}")

    base_path = args['base_path']
    logger.info(f"argument --base_path: {base_path}")

    if args['usb']:
        logger.info(f"argument --usb: {args['usb']}, WIFI disabled.")

    if args['no_wifi']:
        logger.info(f"argument --no_wifi: {args['no_wifi']}, WIFI disabled.")

    if args['usb'] or args['no_wifi']:
        logger.info("USB enabled")
        serial_device_name = args['serial_device_name']
        logger.info(f"argument --serial_device_name: {serial_device_name}")
        io_iterator = Serial_Reader(logger, serial_device_name)
    else:
        logger.info("WIFI enabled")
        udp_port_number = args['udp_port_number']
        logger.info("argument --udp_port_number: {udp_port_number}")
        io_iterator = UDP_Reader(logger, local_host_udp_port_number=udp_port_number)

    log_file_handle = get_log_file_handle(base_path=base_path)
    logger.info(f"log file name: {log_file_handle.name}")

    iso_ts_pre = datetime.isoformat(datetime.now(tz=timezone.utc))

    for record_count, record in enumerate(io_iterator, start=1):
        logger.debug(f"json encoded record {record_count}: {record}")

        if record:
            # check record validity
            # reorganize data as required

            if record['command_name'] == 'rotation_vector':
                # "vector": [-0.646912, -0.262695, 0.230164, 0.677856],
                roll, pitch, yaw = quaternion_to_euler(record['obd_response_value']['vector'])
                record['obd_response_value']['roll'] = roll
                record['obd_response_value']['pitch'] = pitch
                record['obd_response_value']['yaw'] = yaw

            record['iso_ts_pre'] = iso_ts_pre
            record['iso_ts_post'] = datetime.isoformat(datetime.now(tz=timezone.utc))

            logger.debug(f"logging json record {record_count}: {record}")

            log_file_handle.write(json.dumps(record) + "\n")
            log_file_handle.flush()
            fsync(log_file_handle.fileno())

        iso_ts_pre = datetime.isoformat(datetime.now(tz=timezone.utc))

if __name__ == "__main__":
    main()
