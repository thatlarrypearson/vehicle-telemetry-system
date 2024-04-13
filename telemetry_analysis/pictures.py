# telemetry-analysis/telemetry_analysis/pictures.py
#
# https://iptc.org/news/exif-3-0-released-featuring-utf-8-support/
# Article provides link to EXIF 3.0 Specification.
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from pathlib import Path
from argparse import ArgumentParser
from datetime import datetime, timedelta
import pytz

from rich.pretty import pprint

DEFAULT_HOME_TIMEZONE = pytz.timezone('US/Central')
DEFAULT_IMAGE_DIRECTORY = Path.home() / Path("telemetry-data/fuel-images")
DEFAULT_IMAGE_SUFFIX = '.jpg'

# In this case, available_timezones are limited to the ones in the USA.
# Also, timezone ordering is important.  Use the following commented line
# to retrieve timezones and then order them as needed.
# available_timezones = [tz for tz in pytz.all_timezones if 'US/' in tz]
available_timezones = [
    'US/Eastern',
    'US/Central',
    'US/Mountain',
    'US/Pacific',
    'US/Michigan',
    'US/East-Indiana',
    'US/Indiana-Starke',
    'US/Arizona',
    'US/Alaska',
    'US/Aleutian',
    'US/Hawaii',
    'US/Samoa',
]

DateTime_mapping_to_OffsetTime = {
    'DateTimeOriginal': 'OffsetTimeOriginal',
    'DateTimeDigitized': 'OffsetTimeDigitized',
    'DateTime': 'OffsetTime',
}

def datetime_with_tzinfo(
    year=0,
    month=0,
    day=0,
    hour=0,
    minute=0,
    second=0,
    offset_hour=0,
    offset_minute=0,
    verbose=False
)->datetime:
    """
    Create a timezone aware datetime object
    """
    offset_seconds = (hour * 3600) + (minute * 60)
    naive = datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second) - timedelta(seconds=offset_seconds)
    utc_aware = pytz.timezone('UTC').localize(naive)

    return utc_aware

def exif_GPSDateTimeStamp_to_datetime(gps_date, gps_time)->datetime:
    gd = gps_date.split('/')
    gt = gps_time.split(':')
    naive = datetime(year=int(gd[0]), month=int(gd[1]), day=int(gd[2]), hour=int(gt[0]), minute=int(gt[1]), second=int(gt[2]))
    utc_aware = pytz.timezone('UTC').localize(naive)
    return utc_aware

def exif_DateTime_to_datetime(exif_DateTime, exif_OffsetTime)->datetime:
    """
    EXIF data field pairs that can be converted to python datetime:
        DateTime, OffsetTime,
        DateTimeOriginal, OffsetTimeOriginal,
        DateTimeDigitized, OffsetTimeDigitized,
    Returns:
        datetime object with offset time set.
    """
    # 'DateTimeOriginal': '2024:03:03 08:44:38',
    # 'OffsetTimeOriginal': '-06:00',
    sign = exif_OffsetTime[0]
    sign = -1 if sign == '-' else 1

    return datetime_with_tzinfo(
        year=int(exif_DateTime[:4]),
        month=int(exif_DateTime[5:7]),
        day=int(exif_DateTime[8:10]),
        hour=int(exif_DateTime[11:13]),
        minute=int(exif_DateTime[14:16]),
        second=int(exif_DateTime[17:19]),
        offset_hour =(sign * int(exif_OffsetTime[1:3])),
        offset_minute=int(exif_OffsetTime[4:6])
    )

def exif_to_location(ie:dict, gps_info='GPSInfo')->dict:
    """
    given the image_exif (ie) output from image_to_exif_dict(image_file_path), 
    return location data dictionary in the form:
    {
        "time": "19:55:21",
        "lat": "29.6005715",
        "NS": "N",
        "lon": "-97.952421",
        "EW": "W",
        "alt": "179.0",
    }
    """
    if 'GPSDateStamp' in ie[gps_info]:
        gps_date = ie[gps_info]['GPSDateStamp'].replace(':', '/')
    else:
        gps_date = None

    if 'GPSTimeStamp' in ie[gps_info]:
        gps_time = f"{int(ie[gps_info]['GPSTimeStamp'][0]):2}:{int(ie[gps_info]['GPSTimeStamp'][1]):2}:{int(ie[gps_info]['GPSTimeStamp'][2]):2}"
        gps_time = gps_time.replace(' ', '0')
    else:
        gps_time = None

    if gps_date and gps_time:
        aware_gps_datetime = exif_GPSDateTimeStamp_to_datetime(gps_date, gps_time)
    else:
        aware_gps_datetime = None

    # decimal degrees = degrees + (minutes / 60) + (seconds/3600)
    if 'GPSLatitude' in ie[gps_info] and 'GPSLongitude' in ie[gps_info]:
        lat = ie[gps_info]['GPSLatitude'][0] + (ie[gps_info]['GPSLatitude'][1] / 60.0) + (ie[gps_info]['GPSLatitude'][2] / 3600.0)
        lon = ie[gps_info]['GPSLongitude'][0] + (ie[gps_info]['GPSLongitude'][1] / 60.0) + (ie[gps_info]['GPSLongitude'][2] / 3600.0)
        ns = ie[gps_info]['GPSLatitudeRef']
        ew = ie[gps_info]['GPSLongitudeRef']
    else:
        lat = None
        lon = None
        ns = None
        ew = None
    if 'GPSAltitudeRef' in ie[gps_info] and ie[gps_info]['GPSAltitudeRef'] == b'\x00':
        # meters above sea level
        altitude = ie[gps_info]['GPSAltitude']
    elif 'GPSAltitude' in ie[gps_info]:
        # meters below sea level
        altitude = -ie[gps_info]['GPSAltitude']
    else:
        altitude = None

    return {
        'time': gps_time,                           # string - "HH:MM:SS" (hours:minutes:seconds)
        'date': gps_date,                           # string - "YYYY/MM/DD" (year/month/day)
        'aware_gps_datetime': aware_gps_datetime,   # UTC timezone aware datetime from gps_date and gps_time
        'lat': lat,                                 # decimal degrees
        'ns': ns,                                   # North/South
        'lon': lon,                                 # decimal degrees
        'ew': ew,                                   # East/West
        "alt": altitude,                            # meters above (positive values) sea level
    }

def image_to_exif(image_path:str, verbose=False)->dict:
    # sourcery skip: assign-if-exp, dict-comprehension
    """
    Extract image data and return a dictionary (which may include dictionaries)
    containing the image's EXIF data. 
    """
    image = Image.open(image_path)
    raw_exif_data = image._getexif()
    return_value = {}

    for k, v in raw_exif_data.items():
        tag = TAGS[k]
        if tag == 'GPSInfo':
            return_value[tag] = {GPSTAGS[k2]: v2 for k2, v2 in v.items()}
        else:
            return_value[tag] = v

    for DateTime in ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']:
        OffsetTime = DateTime_mapping_to_OffsetTime[DateTime]
        if DateTime not in return_value or OffsetTime not in return_value:
            continue

        return_value[f"_{DateTime}"] = return_value[DateTime]
        return_value[f"_{OffsetTime}"] = return_value[OffsetTime]
        # 'DateTime': '2024:03:21 07:59:30',
        # 'OffsetTime': '-05:00',
        return_value[DateTime] = exif_DateTime_to_datetime(return_value[DateTime], return_value[OffsetTime])

    if 'GPSInfo' in return_value:
        return_value['_GPSInfo'] = return_value['GPSInfo']
        return_value['GPSInfo'] = exif_to_location(return_value, gps_info='_GPSInfo')
        if return_value['GPSInfo']['aware_gps_datetime']:
            return_value['aware_gps_datetime'] = return_value['GPSInfo']['aware_gps_datetime']

    return return_value

def image_directory_to_exif(image_directory=DEFAULT_IMAGE_DIRECTORY, image_suffix=DEFAULT_IMAGE_SUFFIX, verbose=False)->dict:
    """
    Given an image_directory, find all images in the directory (and sub-directories)
    matching the image_suffix.

    Return a dictionary with
        key - image_file_name
        value - exif data
    """
    root = Path(image_directory)
    images = [ str(image) for image in root.rglob(f"*{image_suffix}") if image.is_file()]
    image_exif_data = {}
    for image in images:
        file_string = image
        image_exif_data[file_string] = image_to_exif(image, verbose=verbose)

    if verbose:
        pprint(image_exif_data)

    return image_exif_data

def command_line_options()->dict:
    parser = ArgumentParser(prog="telemetry_analysis.pictures", description="Telemetry Analysis Picture EXIF Data Extractor")

    parser.add_argument(
        "--verbose",
        help="Turn verbose output on. Default is off.",
        default=False,
        action='store_true'
    )

    parser.add_argument(
        "images",
        help="""One or more image files separated by spaces.
                Can include full or relative paths.
            """,
        default=None,
        nargs="+",
    )

    return vars(parser.parse_args())

def main(images=None, verbose=False):
    if images is None:
        args = command_line_options()
        images = args['images']
        verbose = args['verbose']

    if not images:
        raise ValueError("required images argument is None, should be a list of image files")

    if verbose:
        print(f"verbose: {verbose}")
        print(f"files: {images}")

    image_exif_data = {}
    for image in images:
        image_path = Path(image)
        image_exif_data[image] = image_to_exif(image_path)
        if 'GPSInfo' in image_exif_data[image]:
            image_exif_data[image]['_GPSInfo'] = image_exif_data[image]['GPSInfo']
            image_exif_data[image]['GPSInfo'] = exif_to_location(image_exif_data[image], gps_info='_GPSInfo')

    pprint(image_exif_data)

if __name__ == "__main__":
    main()

# testing example with output using Windows PowerShell:

# (python311) PS src\telemetry-analysis> python .\telemetry_analysis\pictures.py -h
# Telemetry Analysis Picture EXIF Data Extractor

# positional arguments:
#   images      One or more image files separated by spaces. Can include full or relative paths.

# options:
#   -h, --help  show this help message and exit
#   --verbose   Turn verbose output on. Default is off.
# (python311) PS src\telemetry-analysis>

# (python311) PS src\telemetry-analysis> python .\telemetry_analysis\pictures.py 'telemetry-data\images\20240303-2024-03-03 08.44.38.jpg'
# {
# │   'telemetry-data\\images\\20240303-2024-03-03 08.44.38.jpg': {
# │   │   '_GPSInfo': {
# │   │   │   'GPSLatitudeRef': 'N',
# │   │   │   'GPSLatitude': (29.0, 31.1421667, 0.0),
# │   │   │   'GPSLongitudeRef': 'W',
# │   │   │   'GPSLongitude': (98.0, 26.9736667, 0.0),
# │   │   │   'GPSAltitudeRef': b'\x00',
# │   │   │   'GPSAltitude': 227.7838400666389,
# │   │   │   'GPSTimeStamp': (14.0, 44.0, 36.0),
# │   │   │   'GPSSpeedRef': 'K',
# │   │   │   'GPSSpeed': 0.0,
# │   │   │   'GPSImgDirectionRef': 'T',
# │   │   │   'GPSImgDirection': 144.9593544530783,
# │   │   │   'GPSDestBearingRef': 'T',
# │   │   │   'GPSDestBearing': 144.9593544530783,
# │   │   │   'GPSHPositioningError': 3.6689586817815774
# │   │   },
# │   │   'ResolutionUnit': 2,
# │   │   'ExifOffset': 224,
# │   │   'Make': 'Apple',
# │   │   'Model': 'iPhone 12',
# │   │   'Software': 'Adobe Photoshop Lightroom Classic 13.2 (Windows)',
# │   │   'DateTime': '2024:03:21 07:59:30',
# │   │   'XResolution': 240.0,
# │   │   'YResolution': 240.0,
# │   │   'ExifVersion': b'0232',
# │   │   'ShutterSpeedValue': 5.906891,
# │   │   'ApertureValue': 1.356144,
# │   │   'DateTimeOriginal': '2024:03:03 08:44:38',
# │   │   'DateTimeDigitized': '2024:03:03 08:44:38',
# │   │   'BrightnessValue': 0.6367765967111838,
# │   │   'ExposureBiasValue': 0.0,
# │   │   'MeteringMode': 5,
# │   │   'ColorSpace': 1,
# │   │   'Flash': 16,
# │   │   'FocalLength': 4.2,
# │   │   'ExposureMode': 0,
# │   │   'WhiteBalance': 0,
# │   │   'FocalLengthIn35mmFilm': 26,
# │   │   'SceneCaptureType': 0,
# │   │   'OffsetTime': '-05:00',
# │   │   'OffsetTimeOriginal': '-06:00',
# │   │   'OffsetTimeDigitized': '-06:00',
# │   │   'SubsecTimeOriginal': '195',
# │   │   'SubjectLocation': (2009, 1502, 2208, 1387),
# │   │   'SubsecTimeDigitized': '195',
# │   │   'SensingMethod': 2,
# │   │   'ExposureTime': 0.016666666666666666,
# │   │   'FNumber': 1.6,
# │   │   'SceneType': b'\x01',
# │   │   'ExposureProgram': 2,
# │   │   'ISOSpeedRatings': 500,
# │   │   'LensSpecification': (1.5499999523160568, 4.2, 1.6, 2.4),
# │   │   'LensMake': 'Apple',
# │   │   'LensModel': 'iPhone 12 back dual wide camera 4.2mm f/1.6',
# │   │   'GPSInfo': {
# │   │   │   'time': '14:44:36',
# │   │   │   'lat': '29.519036111666665',
# │   │   │   'NS': 'N',
# │   │   │   'lon': '98.44956111166667',
# │   │   │   'EW': 'W',
# │   │   │   'alt': 227.7838400666389
# │   │   }
# │   }
# }
# (python311) PS src\telemetry-analysis>
