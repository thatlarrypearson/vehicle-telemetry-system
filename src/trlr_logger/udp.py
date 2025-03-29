# telemetry-trailer-connector/trlr_logger/udp.py
"""
Telemetry Trailer Connector Logger - UDP Communications Module

Implements server for client CircuitPython Analog to Digital Converter
found at telemetry-trailer-connector/CircuitPython/code.py
"""
import socket
import logging
import json
from datetime import datetime, timezone

DEFAULT_LOCAL_HOST_INTERFACE_ADDRESS = "0.0.0.0"
DEFAULT_LOCAL_HOST_UDP_PORT_NUMBER   = 50223
DEFAULT_RECORD_TYPE= "tc47pin"
BUFFER_SIZE  = 8193

raw_to_processed = {
    'ads0/0': "blue_brakes_7",
    'ads0/1': "brown_taillights_7",
    'ads0/2': "yellow_left_stop_7",
    'ads0/3': "green_right_stop_7",
    'ads1/0': "purple_backup_7",
    'ads1/1': "brown_taillights_4",
    'ads1/2': "yellow_left_stop_4",
    'ads1/3': "green_right_stop_4",
}

logger = logging.getLogger("tc_logger")

class TrailerConnector(object):
    """
    Listen on UDP port for trailer connector pin signal/voltage records.

    Parse each JSON encoded records and return dictionary
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
        Get the next iterable.   Returns tuple which contains both raw and processed data dictionaries. 
        """
        # message is type bytes, JSON encoded
        # ip_address_info is list [Sender IP Address:str, Sender Port Number int]
        message, ip_address_info = self.trailer_connector.recvfrom(BUFFER_SIZE)
        self.message_count += 1

        self.logger.debug(f"{self.message_count} address: {ip_address_info}")
        self.logger.debug(f"{self.message_count} message: {message}")

        try:
            # if weird decode errors, then use 'ignore' in: message.decode('utf-8', 'ignore')
            # weather_record = json.loads(message.decode('utf-8'))
            raw_record = json.loads(message)

        except json.decoder.JSONDecodeError as e:
            # improperly closed JSON file
            self.logger.error(f"{self.message_count}: Corrupted JSON info in message {message}\n{e}")
            return None, None

        if not isinstance(raw_record, dict):
            self.logger.error(f"{self.message_count}: JSON decode didn't return a dict: {message}")
            return None, None

        return raw_record, self.parse(raw_record)

    def parse(self, raw_record:dict) -> dict:
        """
        Reformat trailer connector record so that all (embedded) fields are represented as
        4 and 7 pin connector states.

        7-Pin Brake Light Plug			
        Pin #	Description                 Guage	Color
        1	    Ground	                    12  	White
        2	    Trailer Brakes	            12  	Blue
        3	    Tail/Running Lights	        16  	Brown
        4	    Auxiliary 12V+ Charging	    12	    Red/Black
        5	    Left Turn / Stop Lights	    16	    Yellow
        6	    Right Turn / Stop Lights	16  	Green
        7	    Backup Lights / Reverse	    16  	Purple

        """
        processed = {}

        for k, v in raw_to_processed.items():
            if k in raw_record:
                processed[v] = raw_record[k]['voltage']

        return processed
