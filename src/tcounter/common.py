"""telemetry-counter/tcounter/common.py: functions used by other telemetry modules"""

import logging
from pathlib import Path
from socket import gethostname

# defaults
DATA_PATH = "telemetry-data"
HOST_ID = gethostname()
HOME = Path.home()
BASE_PATH = HOME / Path(f"{DATA_PATH}/data")
CONFIG_PATH = f"{HOME}/telemetry-obd/config"
SYSTEM_BOOT_COUNT_APPLICATION_NAME = "system-boot-count"

default_shared_gps_command_list = [
    "GPS_GNGNS",       # Fix data
    "GPS_GNGST",       # Pseudorange error statistics
    "GPS_GNVTG",       # Course over ground and ground speed
    "GPS_GNZDA",       # Time and data
]

default_shared_wthr_command_list = [
    "WTHR_rapid_wind",
    "WTHR_hub_status",
    "WTHR_device_status",
    "WTHR_obs_st",
    "WTHR_evt_precip",
]

default_shared_imu_command_list = [
    "IMU_accelerometer",
    "IMU_gyroscope",
    "IMU_gravity",
    "IMU_linear_acceleration",
    "IMU_magnetometer",
    "IMU_rotation_vector",
]

# Known application shortcuts
APPLICATION_LIST = ['obd', 'obd-cmd-test', 'gps', 'wthr', 'imu', 'trlr', ]

# Default data file paths and names

# - for telemetry-obd data
#   f"{BASE_PATH}/{HOST_ID}/{HOST_ID}-{system_boot_count}-{application_id}-{vin}-{application_counter}.json"

# - for telemetry-wthr, telemetry-gps, telemetry-imu, telemetry-trlr data
#   f"{BASE_PATH}/{HOST_ID}/{HOST_ID}-{system_boot_count}-{application_id}-{application_counter}.json"

# Application_counter values stored in 
# - for telemetry-obd data, telemetry-wthr, telemetry-gps, telemetry-imu, telemetry-trlr
#   f"{BASE_PATH}/{HOST_ID}/.{application_id}-counter_value.txt"

def get_data_file_path(base_path=BASE_PATH) -> Path:
    """If needed, Create data file directories and return the path."""
    return Path(base_path)

logger = logging.getLogger("common")

def get_config_file_path(vin:str, config="config", base_path=BASE_PATH) -> Path:
    """Return path to settings file."""
    for possible_path in [f"{vin}.ini", "default.ini"]:
        path = Path(f"config/{possible_path}")
        if path.is_file():
            return path

        path = Path(base_path) / path
        if path.is_file():
            return path

    raise ValueError(f"no 'default.ini' or '{vin}.ini' available in '{base_path}/{config}/' or just '{config}/'.")

def get_application_counter_value(application_id:str, base_path=BASE_PATH)->int:
    # get the counter value (integer) held in the hidden file
    path = Path(f"{base_path}/{HOST_ID}/.{application_id}-counter_value.txt")
    if path.is_file():
        with open(path,"r") as counter_file:
            counter_value = int(counter_file.read())
    else:
        counter_value = 0
        Path(f"{base_path}/{HOST_ID}/").mkdir(parents=True, exist_ok=True)

    return counter_value

def get_count_file_path(application_id:str, base_path=BASE_PATH)->str:
    # returns the full path to the count file for the application
    return f"{base_path}/{HOST_ID}/.{application_id}-counter_value.txt"

def get_boot_count_file_path()->str:
    # returns the full path to the boot count file
    return get_count_file_path(SYSTEM_BOOT_COUNT_APPLICATION_NAME)

def get_boot_count()->int:
    # returns the boot counter which is just like an application counter only the
    # application_id is set to SYSTEM_BOOT_COUNT_APPLICATION_NAME
    return get_application_counter_value(SYSTEM_BOOT_COUNT_APPLICATION_NAME)

def save_application_counter_value(application_id:str, counter_value:int):
    # save the counter value (integer) as a string held in the hidden file
    path = Path(get_count_file_path(application_id))
    with open(path, 'w') as counter_file:
        counter_file.write(str(counter_value))
    return

def get_next_application_counter_value(application_id:str)->int:
    # get, increment and save application counter
    application_counter_value = get_application_counter_value(application_id)
    application_counter_value += 1
    save_application_counter_value(application_id, application_counter_value)
    return application_counter_value

def get_next_boot_counter_value()->int:
    return get_next_application_counter_value(SYSTEM_BOOT_COUNT_APPLICATION_NAME)

def get_output_file_name(application_id:str, vin:str=None, base_path=BASE_PATH) -> Path:
    # sourcery skip: collection-into-set
    """Create output file name."""
    application_counter_value = get_application_counter_value(application_id)
    boot_count_string =  (f"{get_boot_count():10d}").replace(' ', '0')
    counter_string = (f"{application_counter_value:10d}").replace(' ', '0')

    # - for telemetry-obd data
    if vin and application_id in ['obd', 'obd-cmd-test']:
        return Path(f"{base_path}/{HOST_ID}/{HOST_ID}-{boot_count_string}-{application_id}-{vin}-{counter_string}.json")

    # - for telemetry-wthr, telemetry-gps, telemetry-imu, telemetry-trlr data
    return Path(f"{base_path}/{HOST_ID}/{HOST_ID}-{boot_count_string}-{application_id}-{counter_string}.json")

try:
    # Not making UltraDict a requirement.
    from UltraDict import UltraDict

    def shared_dictionary_to_dictionary(shared_dictionary:UltraDict)->dict:
        # sourcery skip: assign-if-exp, dict-comprehension
        """
        Convert UltraDict item to a real dictionary
        so that the return value will work in json.dumps functions
        """
        logging.info(f"shared_dictionary type {type(shared_dictionary)}")

        if 'UltraDict' not in str(type(shared_dictionary)):
            return shared_dictionary

        return_value = {}
        
        for key, value in shared_dictionary.items():
            logging.info(f"key {key} value type {type(value)}")
            if 'UltraDict' in str(type(shared_dictionary)):
                return_value[key] = shared_dictionary_to_dictionary(value)
            else:
                return_value[key] = value
        
        return return_value


    class SharedDictionaryManager(UltraDict):
        """
        Shared Dictionary Manager - Uses a dictionary as the shared memory metaphor.
        Supports multiple instances within single process so long as 'name'
        is distinct for each instance.  This is not enforced as this class doesn't
        use the singleton pattern.
        Different processes can share the same shared memory/dictionary so long as they use the
        same value for the 'name' constructor variable.
        """
        def __init__(self, name:str):
            """
            SharedDictionaryManager constructor
            arguments
                name
                    name of the shared memory/dictionary region
            """
            # UltraDict(*arg, name=None, buffer_size=10000, serializer=pickle, shared_lock=False, full_dump_size=None, auto_unlink=True, recurse=False, **kwargs)
            super().__init__(
                name=name,
                buffer_size=1048576,    # 1 MB
                shared_lock=True,       # enabling multiple writers on shared memory/dictionary
                full_dump_size=None,    # change this value to buffer_size or larger for Windows machines
                auto_unlink=False,      # once created, shared memory/dictionary persists on process exit
                recurse=True            # dictionary can contain dictionary and updates are nested
            )

except ImportError:
    # logging.error(f"common.SharedDictionaryManager: ImportError")
    SharedDictionaryManager = None
    default_shared_gps_command_list = None
    default_shared_weather_command_list = None

    def shared_dictionary_to_dictionary(shared_dictionary:dict)->dict:
        return shared_dictionary


