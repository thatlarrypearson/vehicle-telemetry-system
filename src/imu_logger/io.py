# telemetry-trailer-connector/imu_logger/io.py
"""
Telemetry Trailer Connector Logger - UDP Communications Module

Implements server for client CircuitPython Analog to Digital Converter
found at telemetry-imu/CircuitPython/code.py
"""
from serial import Serial
from time import sleep
import socket
import logging
import json

DEFAULT_LOCAL_HOST_INTERFACE_ADDRESS = "0.0.0.0"
DEFAULT_LOCAL_HOST_UDP_PORT_NUMBER   = 50219
BUFFER_SIZE  = 8193

logger = logging.getLogger("imu_logger")

class UDP_Reader(object):
    """
    Listen on UDP port for IMU records.

    Parse JSON encoded records and return dictionary
    """
    message_count = 0
    logger = None
    trailer_connector = None

    def __init__(
        self,
        logger,
        local_host_interface_address=DEFAULT_LOCAL_HOST_INTERFACE_ADDRESS,
        local_host_udp_port_number=DEFAULT_LOCAL_HOST_UDP_PORT_NUMBER,
    ):
        self.local_host_interface_address = local_host_interface_address
        self.local_host_udp_port_number = local_host_udp_port_number
        self.trailer_connector = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.trailer_connector.bind((local_host_interface_address, local_host_udp_port_number))
        self.logger = logger
        self.logger.info(f"UDP client ready on {local_host_interface_address} port {local_host_udp_port_number}")

    def __iter__(self):
        """Start iterator."""
        return self

    def __next__(self):
        """
        Get the next iterable.   Returns raw data dictionary. 
        """
        # message is type bytes, JSON encoded
        # ip_address_info is list [Sender IP Address:str, Sender Port Number int]
        message, ip_address_info = self.trailer_connector.recvfrom(BUFFER_SIZE)
        self.message_count += 1

        self.logger.debug(f"{self.message_count} address: {ip_address_info}")
        self.logger.debug(f"{self.message_count} message: {message}")

        try:
            # if weird decode errors, then use 'ignore' in: message.decode('utf-8', 'ignore')
            # raw_record = json.loads(message.decode('utf-8'))
            raw_record = json.loads(message)

        except json.decoder.JSONDecodeError as e:
            # improperly closed JSON record
            self.logger.error(f"{self.message_count}: Corrupted JSON info in message {message}\n{e}")
            return None

        if not isinstance(raw_record, dict):
            self.logger.error(f"{self.message_count}: JSON decode didn't return a dict: {message}")
            return None

        return raw_record

class Serial_Reader(object):
    serial_device_name = None
    io_handle = None
    record_count = 0
    logger = None

    def __init__(self, logger, serial_device_name:str):
        """initialize serial IMU connection"""
        self.serial_device_name = serial_device_name

        self.io_handle = Serial(port=serial_device_name, baudrate=115200, write_timeout=4.0, timeout=4.0)
        self.logger.debug("initialize_imu(): Serial device open.")

        sleep(1.0)

        # flush serial buffer to remove any junk
        self.io_handle.flushInput()
        self.io_handle.flushOutput()

        self.io_handle.write(b'\x0d')        # CR

        sleep(1.0)

        response_count = 0
        while (record := self.io_handle.readline().decode('utf-8')) and response_count < 20:
            logger.debug(f"initialize_imu(): record {record}")

            sleep(1.0)

            if "code.py" in record:
                self.logger.debug("initialize_imu(): code.py open")
                self.io_handle.write(b'\x0d')        # CR

            # Look for last command in set
            if 'rotation_vector' in record:
                self.logger.debug("initialize_imu(): found 'rotation_vector' in record")
                self.logger.debug("initialize_imu(): IMU serial interface initialized")
                return

            response_count += 1

        raise IOError(f"Unable to sync with IMU at {self.serial_device_name} after {response_count} responses")

    def __iter__(self):
        """Start iterator."""
        return self

    def __next__(self):
        record = (self.io_handle.readline()).decode('utf-8')
        self.record_count += 1
        self.logger.debug(f"json encoded record {self.record_count}: {record}")

        try:
            imu_data = json.loads(record)

        except json.decoder.JSONDecodeError as e:
            # improperly closed JSON record
            logger.error(f"JSONDecodeError {e} in record {self.record_count}: {record}")
            imu_data = None

        return imu_data