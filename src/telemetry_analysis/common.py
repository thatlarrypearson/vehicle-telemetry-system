# telemetry-analysis/telemetry_analysis/common.py

from pathlib import Path
from datetime import datetime, timedelta, timezone
from itertools import islice
from numpy import arctan2, sin, cos
from private.vehicles import vehicles
from csv import DictReader

from u_tools.file_system_info import get_file_system_mount_points

def get_mount_point_from_volume_label(volume_label:str) -> str:
    """
    given a drive volume label, return the path to the the drive's mount point.
    # {
    #     'device': 'C:\\',
    #     'volume_label': 'Windows ',
    #     'mount_point': 'C:\\', 
    #     'file_system_type': 'NTFS', 
    #     'file_system_options': 'rw,fixed'
    # },
    """
    mount_points = get_file_system_mount_points()
    return next(
        (
            mount_point['mount_point']
            for mount_point in mount_points
            if mount_point['volume_label'] == volume_label
        ),
        None,
    )

# To use an alternative (external) drive, set the VOLUME_LABEL to the drive's volume label.
# Otherwise, set VOLUME_LABEL to None to use the user's home directory
if VOLUME_LABEL := "Telemetry":
    HOME = get_mount_point_from_volume_label(VOLUME_LABEL)
    if not HOME:
        mount_points = get_file_system_mount_points()
        for mount_point in mount_points:
            print(f"{mount_point}")
        raise ValueError(f"No mount point for volume label {VOLUME_LABEL}")
else:
    HOME = str(Path.home())

data_file_base_directory = f"{HOME}/telemetry-data"
work_product_file_path = f"{HOME}/testing/work-product-files"
temporary_file_base_directory = f"{HOME}/testing/work-product-files/Studies"
base_image_file_path = f"{HOME}/testing/work-product-files/images"
base_ffmpeg_file_path = f"{HOME}/testing/work-product-files/ffmpeg"
ffmpeg_program_path = "/usr/bin/ffmpeg"

Path(work_product_file_path).mkdir(parents=True, exist_ok=True)
Path(temporary_file_base_directory).mkdir(parents=True, exist_ok=True)
Path(base_image_file_path).mkdir(parents=True, exist_ok=True)
Path(base_ffmpeg_file_path).mkdir(parents=True, exist_ok=True)

image_file_extn='jpg'

def dict_head(d:dict, lines=10)->dict:
    return dict(islice(d.items(), 0, lines))

def dict_tail(d:dict, lines=10)->dict:
    return dict(islice(d.items(), len(d) - lines, len(d)))

def list_head(l:list, lines=10) -> list:
    return l[:lines]

def list_tail(l:list, lines=10) -> list:
    return l[len(l)-lines:]

def string_duration_to_timedelta(duration:str)->timedelta:
    # class datetime.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
    # 'duration': '0:09:42.936706' or 'hours:minutes:seconds'
    parts = duration.split(':')
    if len(parts) != 3:
        raise ValueError(f"duration format error: {duration}")
    return (timedelta(hours=int(parts[0]), minutes=int(parts[1]), seconds=float(parts[2]))).total_seconds()

def timedelta_to_hhmmss_str(td:timedelta) -> str:
    # actual format is "HH:MM:SS"
    # hours over 99 unknown response
    seconds = int(td.seconds)
    hh = seconds // 3600
    hh_remainder = int(seconds % 3600)
    mm = hh_remainder // 60
    ss = int(hh_remainder % 60)
    return f"{hh:02}:{mm:02}:{ss:02}"

def heading(a:list, b:list)->float:
    """
    Given two coordinates a and b (lat/lon pairs), return the
    true north compass heading in radians.
    Based on Towards Data Science article by Daniel Ellis Research
    titled "Calculating the bearing between two geospatial coordinates.
    """
    lat = 0
    lon = 1
    dL = b[lon] - a[lon]
    X = cos(b[lat]) * sin(dL)
    Y = cos(a[lat]) * sin(b[lat]) - sin(a[lat]) * cos(b[lat]) * cos(dL)

    # bearing = arctan2(X, Y)
    return arctan2(X, Y)

def fuel_grams_to_milliliters(vin:str, grams:float)->float:
    """
    Convert grams of fuel to milliliters of fuel.
    Conversion depends on Fuel Type.  Fuel Type ('fuel_type') in ../private/vehicles.py.
    Supported Fuel Types:
        - Gasoline
        - Diesel
    Conversion sourced from https://www.aqua-calc.com/calculate/weight-to-volume

    Future calculations might include Volume Correction Factors.

    The following can provide temperature and methanol blend % corrections to the basic weight to volume calculation:
        - https://ised-isde.canada.ca/site/measurement-canada/en/laws-and-requirements/volume-correction-factors-gasoline-and-gasoline-ethanol-blends
    Volume Correction Factors for liquids:
        - https://en.wikipedia.org/wiki/Volume_correction_factor
    Canadian Volume Correction Factors for Gasoline and Diesel including different blends:
        - https://www.ic.gc.ca/eic/site/mc-mc.nsf/vwapj/VCF_Gasoline_Ethanol-Blends.pdf/$file/VCF_Gasoline_Ethanol-Blends.pdf
        - https://www.ic.gc.ca/eic/site/mc-mc.nsf/vwapj/VCF_Diesel.pdf/$file/VCF_Diesel.pdf

    Alternative Fuels Data Center Fuel Properties Comparison
        - https://afdc.energy.gov/files/u/publication/fuel_comparison_chart.pdf
    SAE - 2014-03-05 Automotive Fuels Reference Book, Third Edition R-297
        - https://www.sae.org/publications/books/content/r-297/

    """
    if 'fuel_type' not in vehicles[vin]:
        raise ValueError(f"'fuel_type' missing in dictionary private/vehicles.py: vehicles[<vin>] ({vehicles[vin]['name']}).")
    
    fuel_type = vehicles[vin]['fuel_type']

    if fuel_type not in ['Gasoline', 'Diesel', ]:
        raise ValueError(f"{vehicles[vin]['name']} - Unsupported fuel_type <{fuel_type}>" +
                         "in private/vehicles.py: vehicles[<vin>]['fuel_type'].")

    if fuel_type == 'Gasoline':
        return grams * 1.335291761      # milliliters per gram of Gasoline
    elif fuel_type == "Diesel":
        return grams * 1.175364363      # milliliters per gram of Diesel

    return None

def get_column_names_in_csv_file(file_name:str):
    """
    Simple function to get the column names from the first line of a CSV file.
    Assumes
        - column names are on the first line of the CSV file
        - column names are comma separated.
    
    Returns sequence of
        - list of column names
        - number of data rows in the file
    """
    record_count = 0
    column_names = None
    with open(file_name) as fd:
        rows = DictReader(fd)
        for row in rows:
            if not column_names:
                column_names = list(row)
            else:
                record_count += 1

    return column_names, record_count

def within_timeframe(td:timedelta, datetime1:datetime, datetime2:datetime) -> bool:
    """
    Return true if datetime1 is within td of datetime2 otherwise false
    where td is the timedelta representing the maximum allowed time difference
    """
    return (abs(datetime1 - datetime2)) <= td

def day_matches(dt1:datetime, dt2:datetime) -> bool:
    """
    Returns True when dt1 and dt2 have the same year, month and day.
    """
    return dt1.year == dt2.year and dt1.month == dt2.month and dt1.day == dt2.day