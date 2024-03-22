# telemetry-analysis/telemetry_analysis/pictures.py
#
# https://iptc.org/news/exif-3-0-released-featuring-utf-8-support/
# Article provides link to EXIF 3.0 Specification.
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from pathlib import Path
from argparse import ArgumentParser
from rich.pretty import pprint

def image_to_exif(image_path:str)->dict:
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

    return return_value

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
    gps_time = f"{int(ie[gps_info]['GPSTimeStamp'][0]):2}:{int(ie[gps_info]['GPSTimeStamp'][1]):2}:{int(ie[gps_info]['GPSTimeStamp'][2]):2}"
    gps_time = gps_time.replace(' ', '0')

    # decimal degrees = degrees + (minutes / 60) + (seconds/3600)
    lat = ie[gps_info]['GPSLatitude'][0] + (ie[gps_info]['GPSLatitude'][1] / 60.0) + (ie[gps_info]['GPSLatitude'][2] / 3600.0)
    lon = ie[gps_info]['GPSLongitude'][0] + (ie[gps_info]['GPSLongitude'][1] / 60.0) + (ie[gps_info]['GPSLongitude'][2] / 3600.0)
    if ie[gps_info]['GPSAltitudeRef'] == b'\x00':
        # meters above sea level
        altitude = ie[gps_info]['GPSAltitude']
    else:
        # meters below sea level
        altitude = -ie[gps_info]['GPSAltitude']

    return {
        'time': gps_time,                           # string - "HH:MM:SS" (hours:minutes:seconds)
        'lat': f"{lat}",                            # decimal degrees
        'NS': ie[gps_info]['GPSLatitudeRef'],      # North/South
        'lon': f"{lon}",                            # decimal degrees
        'EW': ie[gps_info]['GPSLongitudeRef'],     # East/West
        "alt": altitude,                            # meters above (positive values) sea level
    }

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

# (python311) PS src\telemetry-analysis> python .\telemetry_analysis\pictures.py '..\..\Blog\Maverick\20240303-2024-03-03 08.44.38.jpg'
# {
# │   '..\\..\\Blog\\Maverick\\20240303-2024-03-03 08.44.38.jpg': {
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
# │   │   │   'GPSDateStamp': '2024:03:03',
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
