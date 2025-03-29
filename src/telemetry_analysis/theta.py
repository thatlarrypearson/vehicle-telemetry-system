# telemetry-analysis/telemetry_analysis/theta.py
#
# Contains routines related to identifying gears and the most likely gear the vehicle is in.
import json
from pathlib import Path
from rich.console import Console
from rich.jupyter import print
from math import sqrt, atan2, tan, pi, radians, ceil

from .common import work_product_file_path, temporary_file_base_directory, data_file_base_directory
from private.vehicles import vehicles

console = Console()

# theta data file/dictionary format
# {
#   "{vin}": {
#           1: {
#                    "theta": 0.2307119668775678,
#                    "a": 0.8432712076533723},
#           2: {
#                    "theta": 0.40496311747540936,
#                    "a": 0.9387563421388321
#           },
#           3: {
#                    "theta": 0.5891714766788418,
#                    "a": 0.942382462560035
#           },
#           4: {
#                    "theta": 0.758444022973888,
#                    "a": 0.9474942502955929
#           },
#           5: {
#                    "theta": 0.8629947133325929,
#                    "a": 0.9699509919645454
#           }
#     }, 
# }
theta_file_name = f"{work_product_file_path}/Studies/Gear-Study/theta-file.json"

# read JSON encoded theta data file
def read_theta_data_file(filename:str)->dict:
    if not (Path(filename)).is_file():
        console.print(f"JSON theta data file ({filename}) not found.")
        return None

    with open(filename, "r") as json_input:
        data_dict = json.load(json_input)

    theta_data_dict = {}
    # when writing the json output, the gear integer values are converted to string values.
    # when reading the json input, the gears are represented as string values.
    # these need to be converted to integer values before being returned to the calling program.
    for vin, gear_data in data_dict.items():
        theta_data_dict[vin] = {}
        for gear, data in gear_data.items():
            gear_number = int(gear)
            theta_data_dict[vin][gear_number] = data
        theta_data_dict[vin][0] = {'theta': None , 'a': None, }

    return theta_data_dict

# write JSON encoded theta data file 
def write_theta_data_file(theta_dict:dict, filename:str):
    if (Path(filename)).is_file():
        console.print(f"rewriting JSON file ({filename})")
    else:
        console.print(f"creating JSON theta file ({filename})")
        Path(filename).parent.mkdir(parents=True, exist_ok=True)

    with open(filename, "w") as json_output:
        json.dump(theta_dict, json_output)

    return

# generate theta data dictionary from modified vehicles dictionary
def generate_theta_data_from_vehicle(vin:str, vehicle:dict)->dict:
    if not (theta_data := read_theta_data_file(theta_file_name)):
        theta_data = {}

    theta_data[vin] = {}

    for gear in vehicle['a']:
        theta_data[vin][gear] = {
            'theta': vehicle['theta'][gear],
            'a':     vehicle['a'][gear],
        }

    write_theta_data_file(theta_data, theta_file_name)

    return theta_data

# distance = point_to_line_distance(x0, y0, a, b, c)
# where
#      distance d
#      point coordinates (x0, y0)
#      line expressed as ax + by + c = 0
#      d = abs(ax0 + by0 + c) / sqrt(a**2 + b**2)
#
def point_to_line_distance(x0:float, y0:float, a:float, b:float, c:float)->float:
    return abs( (a*x0) + (b*y0) + c) / sqrt((a*a) + (b*b))

# distance = point_to_theta_line_distance(x, y, theta)
# where
#       point coordinates (x,y)
#       line expressed as an angle through the origin
def point_to_theta_line_distance(x:float, y:float, theta:float)->float:
    return point_to_line_distance(x, y, tan(theta), -1.0, 0.0)

# when point (x, y) above theta line return point to theta line distance as positive,
# otherwise return point ot theta line distance as negative
def signed_point_to_line_distance(x0:float, y0:float, a:float, b:float, c:float)->float:
    return ((a*x0) + (b*y0) + c) / sqrt((a*a) + (b*b))

def signed_point_to_theta_line_distance(x: float, y:float, theta:float)->float:
    return signed_point_to_line_distance(x, y, tan(theta), -1.0, 0.0)

