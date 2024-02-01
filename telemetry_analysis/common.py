# telemetry-analysis/telemetry_analysis/common.py

from pathlib import Path
from datetime import datetime, timedelta, timezone
from itertools import islice
from numpy import arctan2, sin, cos
from private.vehicles import vehicles

data_file_base_directory = f"{str(Path.home())}/telemetry-data"
work_product_file_path = f"{str(Path.home())}/testing/work-product-files"
temporary_file_base_directory = f"{str(Path.home())}/testing/work-product-files/Studies"
base_image_file_path = f"{str(Path.home())}/testing/work-product-files/images"
base_ffmpeg_file_path = f"{str(Path.home())}/testing/work-product-files/ffmpeg"
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


