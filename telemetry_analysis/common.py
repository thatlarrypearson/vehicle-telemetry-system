# telemetry-analysis/telemetry_analysis/common.py

from pathlib import Path
from datetime import datetime, timedelta, timezone
from itertools import islice

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

def list_head(l:list, lines=10)->list:
    return l[0:lines]

def list_tail(l:list, lines=10)->list:
    return l[(len(l)-lines):len(l)]

def string_duration_to_timedelta(duration:str)->timedelta:
    # class datetime.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
    # 'duration': '0:09:42.936706' or 'hours:minutes:seconds'
    parts = duration.split(':')
    if len(parts) != 3:
        raise ValueError(f"duration format error: {duration}")
    return (timedelta(hours=int(parts[0]), minutes=int(parts[1]), seconds=float(parts[2]))).total_seconds()

def timedelta_to_hhmmss_str(td:timedelta)->str:
    # actual format is "HH:MM:SS"
    # hours over 99 unknown response
    seconds = int(td.seconds)
    hh = int(seconds / 3600)
    hh_remainder = int(seconds % 3600)
    mm = int(hh_remainder / 60)
    ss = int(hh_remainder % 60)
    return f"{hh:02}:{mm:02}:{ss:02}"
