# telemetry-analysis/telemetry_analysis/pictures.py
#
# https://iptc.org/news/exif-3-0-released-featuring-utf-8-support/
# Article provides link to EXIF 3.0 Specification.
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

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

def exif_to_location(ie:dict)->dict:
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
    gps_time = f"{int(ie['GPSInfo']['GPSTimeStamp'][0]):2}:{int(ie['GPSInfo']['GPSTimeStamp'][1]):2}:{int(ie['GPSInfo']['GPSTimeStamp'][2]):2}"
    gps_time = gps_time.replace(' ', '0')

    # decimal degrees = degrees + (minutes / 60) + (seconds/3600)
    lat = ie['GPSInfo']['GPSLatitude'][0] + (ie['GPSInfo']['GPSLatitude'][1] / 60.0) + (ie['GPSInfo']['GPSLatitude'][2] / 3600.0)
    lon = ie['GPSInfo']['GPSLongitude'][0] + (ie['GPSInfo']['GPSLongitude'][1] / 60.0) + (ie['GPSInfo']['GPSLongitude'][2] / 3600.0)
    if ie['GPSInfo']['GPSAltitudeRef'] == b'\x00':
        # meters above sea level
        altitude = ie['GPSInfo']['GPSAltitude']
    else:
        # meters below sea level
        altitude = -ie['GPSInfo']['GPSAltitude']

    return {
        'time': gps_time,
        'lat': f"{lat}",
        'NS': ie['GPSInfo']['GPSLatitudeRef'],
        'lon': f"{lon}",
        'EW': ie['GPSInfo']['GPSLongitudeRef'],
        "alt": altitude,
    }

# testing above functions
#
# from pathlib import Path
# from telemetry_analysis.pictures import image_to_exif, exif_to_location
# image_path = Path.home() / Path('Dropbox/blog/Maverick') / Path('20240318-2024-03-18 13.23.20.jpg')
# image_exif = image_to_exif(image_path)
# print(image_exif)
# print(exif_to_location(image_exif))
#
# prints out the following dictionaries:
#
# (python311) > python test.py
# {
# 	'GPSInfo': {
# 		'GPSLatitudeRef': 'N', 
# 		'GPSLatitude': (29.0, 29.6583333, 0.0), 
# 		'GPSLongitudeRef': 'W', 
# 		'GPSLongitude': (98.0, 25.9116667, 0.0), 
# 		'GPSAltitudeRef': b'\x00', 
# 		'GPSAltitude': 214.81631097560975, 
# 		'GPSTimeStamp': (18.0, 23.0, 19.0), 
# 		'GPSSpeedRef': 'K', 
# 		'GPSSpeed': 0.0, 
# 		'GPSImgDirectionRef': 'T', 
# 		'GPSImgDirection': 119.49580374435119, 
# 		'GPSDestBearingRef': 'T', 
# 		'GPSDestBearing': 119.49580374435119, 
# 		'GPSDateStamp': '2024:03:18', 
# 		'GPSHPositioningError': 4.633924383150389
# 	}, 
# 	'ResolutionUnit': 2, 
# 	'ExifOffset': 224, 
# 	'Make': 'Apple', 
# 	'Model': 'iPhone 12', 
# 	'Software': 'Adobe Photoshop Lightroom Classic 13.2 (Windows)', 
# 	'DateTime': '2024:03:21 08:02:52', 
# 	'XResolution': 240.0, 
# 	'YResolution': 240.0, 
# 	'ExifVersion': b'0232', 
# 	'ShutterSpeedValue': 6.906891, 
# 	'ApertureValue': 1.356144, 
# 	'DateTimeOriginal': '2024:03:18 13:23:19', 
# 	'DateTimeDigitized': '2024:03:18 13:23:19', 
# 	'BrightnessValue': 5.688785601265823, 
# 	'ExposureBiasValue': 0.0, 
# 	'MeteringMode': 5, 
# 	'ColorSpace': 1, 
# 	'Flash': 16, 
# 	'FocalLength': 4.2, 
# 	'ExposureMode': 0, 
# 	'WhiteBalance': 0, 
# 	'FocalLengthIn35mmFilm': 26, 
# 	'SceneCaptureType': 0, 
# 	'OffsetTime': '-05:00', 
# 	'OffsetTimeOriginal': '-05:00', 
# 	'OffsetTimeDigitized': '-05:00', 
# 	'SubsecTimeOriginal': '881', 
# 	'SubjectLocation': (2009, 1502, 2208, 1387), 
# 	'SubsecTimeDigitized': '881', 
# 	'SensingMethod': 2, 
# 	'ExposureTime': 0.008333333333333333, 
# 	'FNumber': 1.6, 
# 	'SceneType': b'\x01', 
# 	'ExposureProgram': 2, 
# 	'ISOSpeedRatings': 32, 
# 	'LensSpecification': (1.5499999523160568, 4.2, 1.6, 2.4), 
# 	'LensMake': 'Apple', 
# 	'LensModel': 'iPhone 12 back dual wide camera 4.2mm f/1.6'
# }
# {
#     'time': '18:23:19', 
#     'lat': '29.494305555', 
#     'NS': 'N', 
#     'lon': '98.43186111166666', 
#     'EW': 'W', 
#     'alt': 214.81631097560975
# }
# (python311) >
