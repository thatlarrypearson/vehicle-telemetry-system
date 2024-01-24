# telemetry-analysis/telemetry_analysis/fuel.py
#
# Fuel Study Related functions
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import csv
import subprocess
from pathlib import Path
from datetime import datetime, timedelta, timezone
from rich.console import Console
from rich.jupyter import print
from rich.pretty import pprint
from rich.table import Table
from dateutil import parser
from math import sqrt, atan2, tan, pi, radians, ceil
from haversine import haversine

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from telemetry_analysis.theta import (
    read_theta_data_file,
    theta_file_name,
    generate_theta_data_from_vehicle,
    write_theta_data_file,
    signed_point_to_theta_line_distance,
)
from telemetry_analysis.reports import (
    basic_stats_table_generator,
    basic_statistics,
    calculated_best_fit_gear_ratios,
    shades,
)
from telemetry_analysis.vins import (
    fake_vin,
    get_vin_from_vehicle_name,
)
from telemetry_analysis.common import (
    base_image_file_path,
    base_ffmpeg_file_path,
    ffmpeg_program_path,
    image_file_extn,
    timedelta_to_hhmmss_str,
    heading,
)
from private.vehicles import vehicles

fuel_study_input_columns = [
    "AMBIANT_AIR_TEMP",                                           # Celsius 
    "BAROMETRIC_PRESSURE",                                        # kilopascal (kPa)
    "ENGINE_LOAD",                                                # % of maximum torque
    "FUEL_LEVEL",                                                 # % of useable fuel capacity
    "FUEL_RATE",                                                  # liters per hour
    "FUEL_RATE_2-engine_fuel_rate",                               # grams per second
    "FUEL_RATE_2-vehicle_fuel_rate",                              # grams per second
    "ODOMETER",                                                   # Kilometers
    "MAF",                                                        # grams per second
    "THROTTLE_ACTUATOR,"                                          # Gas Pedal Position - %, min @ idle = 0, max @ floor <= 100
    "THROTTLE_POS",                                               # Absolute Throttle Position - %, min @ idle > 0, max @ WOT <= 100
    "RPM",                                                        # revolutions per minute
    "SPEED",                                                      # kilometers per hour
    "GNGNS-alt",                                                  # altitude in meters
    "GNGNS-lat",                                                  # latitude in decimal degrees
    "GNGNS-lon",                                                  # longitude in decimal degrees
    "gravity-record_number",                                      # count in this "route"
    "gravity-x",                                                  # meters per second squared
    "gravity-y",                                                  # meters per second squared
    "gravity-z",                                                  # meters per second squared
    "gyroscope-record_number",                                    # count in this "route"
    "gyroscope-x",                                                # radians per second
    "gyroscope-y",                                                # radians per second
    "gyroscope-z",                                                # radians per second
    "linear_acceleration-record_number",                          # count in this "route"
    "linear_acceleration-x",                                      # meters per second squared
    "linear_acceleration-y",                                      # meters per second squared
    "linear_acceleration-z",                                      # meters per second squared
    "magnetometer-record_number",                                 # count in this "route"
    "magnetometer-x",                                             # radians?
    "magnetometer-y",                                             # radians?
    "magnetometer-z",                                             # radians?
    "rotation_vector-record_number",                              # count in this "route"
    "rotation_vector-pitch",                                      # radians
    "rotation_vector-roll",                                       # radians
    "rotation_vector-yaw",                                        # radians
    "rotation_vector-vector"
#    "rotation_vector-vector-w",                                   # dimensionless scaler
#    "rotation_vector-vector-x",                                   # dimensionless vector component
#    "rotation_vector-vector-y",                                   # dimensionless vector component
#    "rotation_vector-vector-z",                                   # dimensionless vector component
    "WTHR_obs_st-time_epoch",                                     # seconds (monotonically increasing)
    "WTHR_obs_st-wind_lull",                                      # meters per second
    "WTHR_obs_st-wind_average",                                   # meters per second
    "WTHR_obs_st-wind_gust",                                      # meters per second
    "WTHR_obs_st-wind_direction",                                 # degrees (north @ 0 degrees in car's forward direction)
    "WTHR_rapid_wind-time_epoch",                                 # seconds (monotonically increasing)
    "WTHR_rapid_wind-wind_speed",                                 # meters per second
    "WTHR_rapid_wind-wind_direction",                             # degrees (north @ 0 degrees in car's forward direction)
    'duration',                                                   # seconds
    'iso_ts_pre',                                                 # UTC timestamp (before)
    'iso_ts_post',                                                # UTC timestamp (after)
]

input_int_columns = [
    "gravity-record_number",                                      # count in this "route"
    "gyroscope-record_number",                                    # count in this "route"
    "linear_acceleration-record_number",                          # count in this "route"
    "magnetometer-record_number",                                 # count in this "route"
    "rotation_vector-record_number",                              # count in this "route"
    "WTHR_obs_st-time_epoch",                                     # seconds (monotonically increasing)
]

input_float_columns = [
    "AMBIANT_AIR_TEMP",                                           # Celsius 
    "BAROMETRIC_PRESSURE",                                        # kilopascal (kPa)
    "ENGINE_LOAD",                                                # % of maximum torque
    "FUEL_LEVEL",                                                 # % of useable fuel capacity
    "FUEL_RATE",                                                  # liters per hour
    "FUEL_RATE_2-engine_fuel_rate",                               # grams per second
    "FUEL_RATE_2-vehicle_fuel_rate",                              # grams per second
    "ODOMETER",                                                   # Kilometers
    "MAF",                                                        # grams per second
    "THROTTLE_ACTUATOR,"                                          # Gas Pedal Position - %, min @ idle = 0, max @ floor <= 100
    "THROTTLE_POS",                                               # Absolute Throttle Position - %, min @ idle > 0, max @ WOT <= 100
    "RPM",                                                        # revolutions per minute
    "SPEED",                                                      # kilometers per hour
    "GNGNS-alt",                                                  # altitude in meters
    "GNGNS-lat",                                                  # latitude in decimal degrees
    "GNGNS-lon",                                                  # longitude in decimal degrees
    "gravity-x",                                                  # meters per second squared
    "gravity-y",                                                  # meters per second squared
    "gravity-z",                                                  # meters per second squared
    "gyroscope-x",                                                # radians per second
    "gyroscope-y",                                                # radians per second
    "gyroscope-z",                                                # radians per second
    "linear_acceleration-x",                                      # meters per second squared
    "linear_acceleration-y",                                      # meters per second squared
    "linear_acceleration-z",                                      # meters per second squared
    "magnetometer-x",                                             # radians?
    "magnetometer-y",                                             # radians?
    "magnetometer-z",                                             # radians?
    "rotation_vector-pitch",                                      # radians
    "rotation_vector-roll",                                       # radians
    "rotation_vector-yaw",                                        # radians
    "rotation_vector-vector-w",                                   # dimensionless scaler
    "rotation_vector-vector-x",                                   # dimensionless vector component
    "rotation_vector-vector-y",                                   # dimensionless vector component
    "rotation_vector-vector-z",                                   # dimensionless vector component
    "WTHR_obs_st-wind_lull",                                      # meters per second
    "WTHR_obs_st-wind_average",                                   # meters per second
    "WTHR_obs_st-wind_gust",                                      # meters per second
    "WTHR_obs_st-wind_direction",                                 # degrees (north @ 0 degrees in car's forward direction)
    "WTHR_rapid_wind-wind_speed",                                 # meters per second
    "WTHR_rapid_wind-wind_direction",                             # degrees (north @ 0 degrees in car's forward direction)
]

fuel_study_output_columns = [
    'i',                                                          # row number
    "AMBIANT_AIR_TEMP",                                           # Celsius 
    "BAROMETRIC_PRESSURE",                                        # kilopascal (kPa)
    "ENGINE_LOAD",                                                # % of maximum torque
    "FUEL_LEVEL",                                                 # % of useable fuel capacity
    "FUEL_RATE",                                                  # liters per hour
    "FUEL_RATE_2-engine_fuel_rate",                               # grams per second
    "FUEL_RATE_2-vehicle_fuel_rate",                              # grams per second
    "ODOMETER",                                                   # Kilometers
    "MAF",                                                        # grams per second
    "THROTTLE_ACTUATOR,"                                          # Gas Pedal Position - %, min @ idle = 0, max @ floor <= 100
    "THROTTLE_POS",                                               # Absolute Throttle Position - %, min @ idle > 0, max @ WOT <= 100
    "RPM",                                                        # revolutions per minute
    "SPEED",                                                      # kilometers per hour
    "GNGNS-alt",                                                  # altitude in meters
    "GNGNS-lat",                                                  # latitude in decimal degrees
    "GNGNS-lon",                                                  # longitude in decimal degrees
    "gravity-x",                                                  # meters per second squared
    "gravity-y",                                                  # meters per second squared
    "gravity-z",                                                  # meters per second squared
    "gyroscope-x",                                                # radians per second
    "gyroscope-y",                                                # radians per second
    "gyroscope-z",                                                # radians per second
    "linear_acceleration-x",                                      # meters per second squared
    "linear_acceleration-y",                                      # meters per second squared
    "linear_acceleration-z",                                      # meters per second squared
    "magnetometer-x",                                             # radians?
    "magnetometer-y",                                             # radians?
    "magnetometer-z",                                             # radians?
    "rotation_vector-pitch",                                      # radians
    "rotation_vector-roll",                                       # radians
    "rotation_vector-yaw",                                        # radians
    "WTHR_obs_st-time_epoch",                                     # seconds (monotonically increasing)
    "WTHR_obs_st-wind_lull",                                      # meters per second
    "WTHR_obs_st-wind_average",                                   # meters per second
    "WTHR_obs_st-wind_gust",                                      # meters per second
    "WTHR_obs_st-wind_direction",                                 # RADIANS (north @ 0 RADIANS in car's forward direction)
    "WTHR_rapid_wind-time_epoch",                                 # seconds (monotonically increasing)
    "WTHR_rapid_wind-wind_speed",                                 # meters per second
    "WTHR_rapid_wind-wind_direction",                             # RADIANS (north @ 0 RADIANS in car's forward direction)
    'rps',                                                        # revolutions per second
    'mps',                                                        # meters per second
    'theta',                                                      # radians
    'closest_gear',                                               # ordinal gear number, integer 1 through 6
    'acceleration',                                               # meters per second squared
    'route',                                                      # source file number
    'duration',                                                   # seconds
    'iso_ts_pre',                                                 # UTC timestamp (before)
    'iso_ts_post',                                                # UTC timestamp (after)
]

previous_input_columns = [
    "ENGINE_LOAD",                                                # % of maximum torque
    "FUEL_LEVEL",                                                 # % of useable fuel capacity
    "FUEL_RATE",                                                  # liters per hour
    "FUEL_RATE_2-engine_fuel_rate",                               # grams per second
    "FUEL_RATE_2-vehicle_fuel_rate",                              # grams per second
    "ODOMETER",                                                   # Kilometers
    "MAF",                                                        # grams per second
    "THROTTLE_ACTUATOR,"                                          # Gas Pedal Position - %, min @ idle = 0, max @ floor <= 100
    "THROTTLE_POS",                                               # Absolute Throttle Position - %, min @ idle > 0, max @ WOT <= 100
    "RPM",                                                        # revolutions per minute
    "SPEED",                                                      # kilometers per hour
    "GNGNS-alt",                                                  # altitude in meters
    "GNGNS-lat",                                                  # latitude in decimal degrees
    "GNGNS-lon",                                                  # longitude in decimal degrees
]

console = Console()

def save_fuel_study_data_to_csv(vin:str, output_file_name:str, obd_fuel_study:list, force_save=False):
    console.print(f"Creating fuel study CSV file for {vehicles[vin]['name']} as {output_file_name.replace(vin, fake_vin)}")

    if Path(output_file_name).is_file() and not force_save:
        console.print(f"\tCSV file for {vehicles[vin]['name']} already exists - skipping...")
    else:
        with open(output_file_name, "w") as csv_output:
            writer = csv.DictWriter(csv_output, fieldnames=fuel_study_output_columns, escapechar="\\")
            writer.writeheader()
            for row in obd_fuel_study:
                writer.writerow(row)

    return

def generate_fuel_study_data(csv_file_dir:str, vin:str)->list:
    Path(csv_file_dir).mkdir(parents=True, exist_ok=True)

    obd_fuel_study = []
    theta_data = read_theta_data_file(theta_file_name)
    bad_row_counter = 0

    # each raw JSON data file, after transformation into a CSV file, will have a
    # unique 'route_counter' value assigned to it.
    route_counter = 0

    # each row in the union of all CSV files has a unique row number 'i'
    i = 0

    for csv_data_file in (Path(csv_file_dir).glob(f"*{vin}*.csv")):
        with open(csv_data_file, "r") as csv_file:
            route_counter += 1
            line_number = 0

            # previous value setup
            previous = {column: None for column in previous_input_columns}

            reader = csv.DictReader(csv_file)
            try:
                for row in reader:
                    i += 1
                    line_number += 1
                    record = {}

                    # convert floats
                    for column in input_float_columns:
                        if row[column] and isinstance(row[column], str) and len(row[column]) > 0:
                            record[column] = float(row[column])
                        elif row[column] and isinstance(row[column], float):
                            record[column] = row[column]
                        elif row[column] and isinstance(row[column], int):
                            record[column] = float(row[column])
                        else:
                            record[column] = None

                    # "rotation_vector-vector" is list
                    if isinstance(row["rotation_vector-rotation_vector"], list):
                        row["rotation_vector-vector-w"] = record['rotation_vector'][0]
                        row["rotation_vector-vector-x"] = record['rotation_vector'][1]
                        row["rotation_vector-vector-y"] = record['rotation_vector'][2]
                        row["rotation_vector-vector-z"] = record['rotation_vector'][3]

                    # convert ints
                    for column in input_int_columns:
                        if row[column] and isinstance(row[column], str) and len(row[column]) > 0:
                            record[column] = int(row[column])
                        elif row[column] and isinstance(row[column], int):
                            record[column] = row[column]
                        else:
                            record[column] = None

                    # convert date/time
                    if isinstance(row['iso_ts_pre'], str):
                        record['iso_ts_pre'] = parser.isoparse(row['iso_ts_pre'])

                    if isinstance(row['iso_ts_post'], str):
                        record['iso_ts_post'] = parser.isoparse(row['iso_ts_post'])

                    record['duration'] = record['iso_ts_post'] - record['iso_ts_pre']
                    record['duration'] = record['duration'].total_seconds()

                    record['i'] = i
                    record['route'] = route_counter

                    # create modify fields
                    record['rps'] = record['RPM'] / 60.0
                    record['mps'] = record['SPEED'] * 0.44704
                    record['theta'] = atan2(record['mps'], record['rps'])
                    record['acceleration'] = 0

                    # need previous[column] to track all of the previous things

                    record['acceleration'] = None
                    if previous['iso_ts_post'] is not None and previous['SPEED'] is not None and record['SPEED'] is not None:
                        # route is current
                        record['acceleration'] = (((record['SPEED'] - previous['SPEED']) * 0.44704)
                                                   / record['duration'])

                    record['gps_distance'] = None
                    if (previous['GNGNS_lat'] is not None and
                         record['GNGNS_lat'] is not None and
                       previous['GNGNS_lon'] is not None and
                         record['GNGNS_lon'] is not None):
                        
                        record['gps_distance'] = haversine(
                            (previous['GNGNS_lat'], previous['GNGNS_lon']),
                            (record['GNGNS_lat'], record['GNGNS_lon'])
                        )
                        record['gps_heading'] = heading(
                            (previous['GNGNS-lat'], previous['lon']),
                            (record['GNGNS_lat'], record['GNGNS_lon'])
                        )

                    record['WTHR_rapid_wind-wind_direction'] = None
                    if row['WTHR_rapid_wind-wind_direction'] is not None:
                        record['WTHR_rapid_wind-wind_direction'] = radians(row['WTHR_rapid_wind-wind_direction'])

                    record['WTHR_obs_st-wind_direction'] = None
                    if row['WTHR_obs_st-wind_direction'] is not None:
                        record['WTHR_obs_st-wind_direction'] = radians(row['WTHR_obs_st-wind_direction'])

                    record['gps-rise'] = None
                    if previous['GNGNS_alt'] is not None and record['GNGNS_alt'] is not None:
                        record['gps-rise'] = record['GNGNS_alt'] - previous['GNGNS_alt']

                    # Alternative Fuels Data Center Fuel Properties Comparison
                    # https://afdc.energy.gov/files/u/publication/fuel_comparison_chart.pdf
                    # SAE - 2014-03-05 Automotive Fuels Reference Book, Third Edition R-297
                    # https://www.sae.org/publications/books/content/r-297/
                    if row['FUEL_RATE_2-engine_fuel_rate'] is not None:
                        
                    if row['FUEL_RATE_2-vehicle_fuel_rate'] is not None:

                    if theta_data and vin in theta_data:
                        # find closest gear using theta_data[vin][gear]['theta'] being compared to row['theta']
                        gear_distance = None
                        closest_gear = 1
                        for gear in theta_data[vin]:
                            if not gear:
                                continue
                            gear_distance = abs(theta_data[vin][gear]['theta'] - record['theta'])
                            if gear != closest_gear:
                                if gear_distance < last_gear_distance:
                                    closest_gear = gear
                            last_gear_distance = gear_distance

                        record['closest_gear'] = closest_gear

                    else:

                        record['closest_gear'] = 0

                    previous = {column: record[column] for column in previous_input_columns}
                    obd_fuel_study.append(record)

            except Exception as e:
                console.print(
                    f"oops {vehicles[vin]['name']}:\n{csv_data_file}\nline {line_number}\n{str(e)}"
                )
                pprint(row)
                pprint(record)

    console.print(f"{vehicles[vin]['name']} good rows: {len(obd_fuel_study)} bad rows: {bad_row_counter} file count: {route_counter}")

    return obd_fuel_study
