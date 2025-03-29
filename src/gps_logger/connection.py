# telemetry-gps/gps_logger/connection.py
"""
Manage gps connections through serial interfaces.
"""
from serial import Serial
import logging
from .gps_config import (
    turn_off_all_messages_on_all_interfaces, turn_on_nmea_messages,
    set_base_message_rate, set_port_configuration,
    gps_software_version, gps_hardware_version,
    INTERFACES,
)

def connect_to_gps(device_path:str, **kwargs)->Serial:
    """
    Open USB/UART/Serial GPS and return serial IO handle
    """
    logging.debug(f"open GPS serial port {device_path}")
    return Serial(port=device_path, **kwargs)

def initialize_gps(device_path:str, message_rate:int, **kwargs)->Serial:
    """
    Initializes GPS for delivering stream of NMEA messages over interface
    """
    logging.debug(f"initializing GPS at {device_path}")
    io_handle = connect_to_gps(device_path, **kwargs)

    set_port_configuration(io_handle, INTERFACES["USB"])

    set_base_message_rate(io_handle)

    turn_off_all_messages_on_all_interfaces(io_handle)

    gps_software_version(io_handle)
    gps_hardware_version(io_handle)

    turn_on_nmea_messages(io_handle, message_rate)

    return io_handle

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

