"""telemetry_obd/common.py: Common functions."""

from time import sleep
from pathlib import Path
from typing import List
from datetime import datetime, timezone
import configparser
import obd
from pint import UnitRegistry
from obd.utils import BitArray
from obd.codes import BASE_TESTS
from obd.OBDResponse import Status
from .add_commands import NEW_COMMANDS

ureg = UnitRegistry()
CONNECTION_WAIT_DELAY = 15.0
CONNECTION_RETRY_COUNT = 5

local_commands = {
    new_command.name: new_command for new_command in NEW_COMMANDS
}



class CommandNameGenerator():
    """Iterator for providing a never ending list of OBD commands."""

    # Three different cycles for running commands
    startup_names: List[str] = []
    startup = None
    housekeeping_names: List[str] = []
    housekeeping = None
    cycle_names: List[str] = []
    cycle = None
    full_cycles_count = 0

    def __init__(self, settings_file: str):
        """Init function."""
        self.settings_file = settings_file
        self.load_names()

    def load_names(self):
        """Load three sets of OBD command names."""
        config = configparser.ConfigParser()
        config.read(self.settings_file)
        self.startup_names = (config['STARTUP NAMES']['startup']).split()
        self.startup = self.startup_names.__iter__()

        self.housekeeping_names = (
                (config['HOUSEKEEPING NAMES']['housekeeping']).split()
        )
        self.housekeeping = self.housekeeping_names.__iter__()

        self.cycle_names = (config['CYCLE NAMES']['cycle']).split()
        self.cycle = self.cycle_names.__iter__()

    def __iter__(self):
        """Start iterator."""
        return self

    def __next__(self):
        """Get the next iterable."""
        if self.startup:
            try:
                return self.startup.__next__()
            except StopIteration:
                self.startup = None

        if self.cycle:
            try:
                return self.cycle.__next__()
            except StopIteration:
                self.cycle = None

        if not self.housekeeping:
            self.housekeeping = self.housekeeping_names.__iter__()

        self.cycle = self.cycle_names.__iter__()

        try:
            return self.housekeeping.__next__()
        except StopIteration:
            self.housekeeping = None
            self.full_cycles_count += 1

        return self.__next__()


def get_vin_from_vehicle(connection):
    """Get Vehicle Information Number (VIN) from vehicle."""
    obd_response = connection.query(obd.commands["VIN"])

    if obd_response and obd_response.value:
        return str(bytes(obd_response.value), 'utf-8')

    return 'UNKNOWN_VIN'

def get_elm_info(connection):
    """Return ELM version and voltage"""
    version_response = connection.query(obd.commands["ELM_VERSION"])
    voltage_response = connection.query(obd.commands["ELM_VOLTAGE"])

    return str(version_response.value), str(voltage_response.value)

def get_directory(base_path, vin):
    """Generate directory where data files go."""
    # print("base_path", base_path, "vin", vin)
    path = Path(base_path) / Path(str(vin))
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_config_path(base_path, vin):
    """Return path to settings file."""
    path = Path(str(vin) + '.ini')
    if path.is_file():
        return path

    path = Path(base_path) / path
    if path.is_file():
        return path

    path = Path('default.ini')
    if path.is_file():
        return path

    path = Path(base_path) / path
    if path.is_file():
        return path

    raise ValueError(f"no default.ini or {vin}.ini available")

def get_output_file_name(vin):
    """Create an output file name."""
    dt_now = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")
    return Path(f"{vin}-{dt_now}-utc.json")

def load_custom_commands(connection, verbose=False):
    """Load custom commands into a dictionary."""
    custom_commands = {}
    for new_command in NEW_COMMANDS:
        if verbose:
            print(f"load_custom_commands(): {new_command.name}")
        if connection:
            connection.supported_commands.add(new_command)
        custom_commands[new_command.name] = new_command
    return custom_commands

def tuple_to_list_converter(t:tuple)->list:
    """
    Converts python-OBD/OBD/OBDCommand.py OBDCommand tuple output to list output.
    For example, O2_SENSORS value: "((), (False, False, False, False), (False, False, False, True))"
    gets converted to [False, False, False, False, False, False, False, True]
    """
    return_value = []
    for item in t:
        if isinstance(item, tuple) and len(item) == 0:
            continue
        elif isinstance(item, tuple):
            return_value += tuple_to_list_converter(item)
        elif isinstance(item, BitArray):
            for b in item:
                return_value.append(b)
        else:
            return_value.append(item)

    return return_value

def list_cleaner(command_name:str, items:list, verbose=False)->list:
    return_value = []
    for item in items:
        if (
            isinstance(item, ureg.Quantity) or
            isinstance(item, bytearray)
        ):
            return_value.append(str(item))
        elif 'Quantity' in item.__class__.__name__:
            return_value.append(str(item))
        else:
            return_value.append(item)
    return return_value

def clean_obd_query_response(command_name:str, obd_response, verbose=False):
    """
    fixes problems in OBD connection.query responses.
    - is_null() True to "no response"
    - tuples to lists
    - bytearrays to strings
    - "NO DATA" to "no response"
    - None to "no response"
    - BitArray to list of True/False values
    - Status to serialized version of Status
    - pint Quantity object serialized by pint.
    """
    if (obd_response.is_null() or
        obd_response.value is None or (
        isinstance(obd_response.value, str) and "NO DATA" in obd_response.value )):
        obd_response_value = "no response"
    elif isinstance(obd_response.value, bytearray):
        obd_response_value = obd_response.value.decode("utf-8")
    elif isinstance(obd_response.value, BitArray):
        obd_response_value = []
        for b in obd_response.value:
            obd_response_value.append(b)
    elif isinstance(obd_response.value, Status):
        obd_response_value = []
        for base_test in BASE_TESTS:
            obd_response_value.append(str(obd_response.value.__dict__[base_test]))
    elif isinstance(obd_response.value, ureg.Quantity):
        obd_response_value = str(obd_response.value)
    elif 'Quantity' in obd_response.value.__class__.__name__:
        obd_response_value = str(obd_response.value)
    elif isinstance(obd_response.value, list):
        obd_response_value = list_cleaner(command_name, obd_response.value, verbose=verbose)
    elif isinstance(obd_response.value, tuple):
        obd_response_value = tuple_to_list_converter(obd_response.value)
    else:
        obd_response_value = obd_response.value

    return obd_response_value

def get_obd_connection(fast:bool, timeout:float, verbose=True)->obd.OBD:
    """
    return an OBD connection instance that connects to the first ELM 327 compatible device
    connected to any of the local serial ports.  If no device found, exit program with error code 1.
    """
    ports = obd.scan_serial()

    if verbose:
        print(f"identified ports {ports}")

    for port in ports:
        print(f"connecting to port {port}")

        try:

            # OBD(portstr=None, baudrate=None, protocol=None, fast=True, timeout=0.1, check_voltage=True)
            connection = obd.OBD(portstr=port, fast=fast, timeout=timeout)
            for t in range(1, CONNECTION_RETRY_COUNT):

                if connection.is_connected():
                    print(f"connected to {port} on try {t} of {CONNECTION_RETRY_COUNT}")
                    custom_commands = load_custom_commands(connection, verbose=verbose)
                    return connection

                if connection.status() == obd.OBDStatus.NOT_CONNECTED:
                    if verbose:
                        print(f"ELM 327 Adapter Not Found on {port}on try {t} of {CONNECTION_RETRY_COUNT}")
                    break

                if verbose:
                    print(f"Waiting for OBD Connection on {port} on try {t} of {CONNECTION_RETRY_COUNT}: {connection.status()}")

                # connection.close()
                sleep(CONNECTION_WAIT_DELAY)
                # connection = obd.OBD(portstr=port, fast=fast, timeout=timeout)

        except Exception as e:
            print(f"OBD Connection on port {port} unavailable.")

    print(f"ELM 327 type device not found in devices: {ports}")
    print("exiting...")

    exit(1)

def recover_lost_connection(connection:obd.OBD, fast:bool, timeout:float, verbose=True)->obd.OBD:
    """
    Recover lost connection and return a new working connection handle.
    """
    print("recovering lost connection")
    connection.close()
    sleep(CONNECTION_WAIT_DELAY)
    connection = get_obd_connection(fast=fast, timeout=timeout, verbose=verbose)

    return connection

def execute_obd_command(connection:obd.OBD, command_name:str, verbose=True):
    """
    executes OBD interface query given command_name on OBD connection.
    returns list or value
    """
    if obd.commands.has_name(command_name):
        obd_response = connection.query(obd.commands[command_name], force=True)

    elif command_name in local_commands:
        obd_response = connection.query(local_commands[command_name], force=True)
    else:
        # raise LookupError(f"command <{command_name}> missing from python-obd and custom commands")
        return f"LookupError: command <{command_name}> missing from python-obd and custom commands"

    return obd_response
