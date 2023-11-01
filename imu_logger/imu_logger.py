# telemetry-imu/telemetry_imu/imu_logger.py

from serial import Serial
from time import sleep
from argparse import ArgumentParser
from math import atan2, asin
import logging
from sys import stdout, stderr
from os import fsync
from datetime import datetime, timezone
import json

from tcounter.common import (
    default_shared_imu_command_list as SHARED_DICTIONARY_COMMAND_LIST,
    SharedDictionaryManager,
    get_output_file_name,
    get_next_application_counter_value,
    BASE_PATH
)

from .usb_devices import get_serial_device_name
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
        help=f"Relative or absolute output data directory. Defaults to '{BASE_PATH}'."
    )

    parser.add_argument(
        "--shared_dictionary_name",
        default=None,
        help="Enable shared memory/dictionary using this name"
    )

    parser.add_argument(
        "--shared_dictionary_command_list",
        default=None,
        help=(
            "Comma separated list of IMU commands/reports to be shared (no spaces), defaults to all: " +
            f"{SHARED_DICTIONARY_COMMAND_LIST}"
        )
    )

    parser.add_argument(
        "--serial_device_name",
        default=get_serial_device_name(),
        help=f"Name for the hardware IMU serial device. Defaults to {get_serial_device_name()} "
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

def initialize_imu(serial_device_name):
    """initialize IMU connection and return serial device"""
    s = Serial(
        port=serial_device_name,
        baudrate=115200,
        write_timeout=4.0,
        timeout=4.0
    )
    logger.debug("initialize_imu(): Serial device open.")

    sleep(1.0)

    # flush serial buffer to remove any junk
    s.flushInput()
    s.flushOutput()

    s.write(b'\x0d')        # CR

    sleep(1.0)

    response_count = 0
    while (record := s.readline().decode('utf-8')) and response_count < 20:
        logger.debug(f"initialize_imu(): record {record}")

        sleep(1.0)

        if "code.py" in record:
            logger.debug("initialize_imu(): code.py open")
            s.write(b'\x0d')        # CR

        # Look for last command in set
        if 'rotation_vector' in record:
            logger.debug("initialize_imu(): found 'rotation_vector' in record")
            return s

        response_count += 1

    raise IOERROR(f"Unable to sync with IMU at {serial_device_name} after {response_count} responses")

def main():
    args = argument_parsing()

    if args['version']:
        print(f"Version {__version__}", file=stdout)
        exit(0)

    verbose = args['verbose']
    serial_device_name = args['serial_device_name']
    shared_dictionary_name = args['shared_dictionary_name']
    shared_dictionary_command_list = args['shared_dictionary_command_list']

    base_path = args['base_path']

    logging_level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(stream=stderr, level=logging_level)

    logger.debug(f"argument --verbose: {verbose}")

    log_file_handle = get_log_file_handle(base_path=base_path)
    logger.info(f"log file name: {log_file_handle.name}")

    if shared_dictionary_command_list:
        shared_dictionary_command_list = shared_dictionary_command_list.split(sep=',')
    else:
        shared_dictionary_command_list = SHARED_DICTIONARY_COMMAND_LIST

    logger.info(f"shared_dictionary_command_list {shared_dictionary_command_list})")

    if shared_dictionary_name:
        shared_dictionary = SharedDictionaryManager(shared_dictionary_name)
        logger.info(f"shared_dictionary_command_list {shared_dictionary_command_list}")
    else:
        shared_dictionary = None

    logger.info(f"shared_dictionary_name {shared_dictionary_name})")

    io_handle = initialize_imu(serial_device_name)

    iso_ts_pre = datetime.isoformat(datetime.now(tz=timezone.utc))

    record_count = 0
    while record := (io_handle.readline()).decode('utf-8'):
        record_count += 1
        logger.debug(f"json encoded record {record_count}: {record}")

        try:
            imu_data = json.loads(record)

            # check record validity
            # reorganize data as required

            if imu_data['command_name'] == 'rotation_vector':
                # "vector": [-0.646912, -0.262695, 0.230164, 0.677856],
                roll, pitch, yaw = quaternion_to_euler(imu_data['obd_response_value']['vector'])
                imu_data['obd_response_value']['roll'] = roll
                imu_data['obd_response_value']['pitch'] = pitch
                imu_data['obd_response_value']['yaw'] = yaw

            imu_data['iso_ts_pre'] = iso_ts_pre
            imu_data['iso_ts_post'] = datetime.isoformat(datetime.now(tz=timezone.utc))

            logger.debug(f"logging json record {record_count}: {imu_data}")

            log_file_handle.write(json.dumps(imu_data) + "\n")
            log_file_handle.flush()
            fsync(log_file_handle.fileno())

            shared_dict_index = 'IMU_' + imu_data["command_name"]
            if shared_dictionary is not None and shared_dict_index in shared_dictionary_command_list:
                    logger.debug( f"Sharing record {record_count}: {imu_data['command_name']}")
                    shared_dictionary[shared_dict_index] = imu_data

        except json.decoder.JSONDecodeError as e:
            # improperly closed JSON file
            logger.error(f"JSONDecodeError {e} in record {record_count}: {record}")

        iso_ts_pre = datetime.isoformat(datetime.now(tz=timezone.utc))

if __name__ == "__main__":
    main()
