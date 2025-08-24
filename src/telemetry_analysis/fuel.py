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
    fuel_grams_to_milliliters,
    get_column_names_in_csv_file,
)
from private.vehicles import vehicles

fuel_study_input_columns = [
    "AMBIANT_AIR_TEMP",                                           # Celsius 
    "BAROMETRIC_PRESSURE",                                        # kilopascal (kPa)
    # "COMMANDED_EQUIV_RATIO",                                      # air/fuel equivalence ratio
    # "ENGINE_LOAD",                                                # % of maximum torque
    "FUEL_LEVEL",                                                 # % of useable fuel capacity
    # "FUEL_RATE",                                                  # liters per hour
    "FUEL_RATE_2-engine_fuel_rate",                               # grams per second
    # "FUEL_RATE_2-vehicle_fuel_rate",                              # grams per second
    "ODOMETER",                                                   # Kilometers
    # "MAF",                                                        # grams per second
    "THROTTLE_ACTUATOR",                                          # Gas Pedal Position - %, min @ idle = 0, max @ floor <= 100
    "THROTTLE_POS",                                               # Absolute Throttle Position - %, min @ idle > 0, max @ WOT <= 100
    "RPM",                                                        # revolutions per minute
    "SPEED",                                                      # kilometers per hour
    "GNGNS-alt",                                                  # altitude in meters
    "GNGNS-lat",                                                  # latitude in decimal degrees
    "GNGNS-lon",                                                  # longitude in decimal degrees
    "NMEA_GNGNS-alt",                                             # altitude in meters
    "NMEA_GNGNS-lat",                                             # latitude in decimal degrees
    "NMEA_GNGNS-lon",                                             # longitude in decimal degrees
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
    "magnetometer-x",                                             # micro Tesla (uT)
    "magnetometer-y",                                             # micro Tesla (uT)
    "magnetometer-z",                                             # micro Tesla (uT)
    "rotation_vector-record_number",                              # count in this "route"
    "rotation_vector-pitch",                                      # radians
    "rotation_vector-roll",                                       # radians
    "rotation_vector-yaw",                                        # radians
#    "rotation_vector-vector"
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
    "WTHR_rapid_wind-time_epoch",                                 # seconds (monotonically increasing)
    "WTHR_obs_st-time_epoch",                                     # seconds (monotonically increasing)
]

input_float_columns = [
    "AMBIANT_AIR_TEMP",                                           # Celsius 
    "BAROMETRIC_PRESSURE",                                        # kilopascal (kPa)
    "COMMANDED_EQUIV_RATIO",                                      # air/fuel equivalence ratio
    "ENGINE_LOAD",                                                # % of maximum torque
    "FUEL_LEVEL",                                                 # % of useable fuel capacity
    "FUEL_RATE",                                                  # liters per hour
    "FUEL_RATE_2-engine_fuel_rate",                               # grams per second
    "FUEL_RATE_2-vehicle_fuel_rate",                              # grams per second
    "ODOMETER",                                                   # Kilometers
    "MAF",                                                        # grams per second
    "THROTTLE_ACTUATOR",                                          # Gas Pedal Position - %, min @ idle = 0, max @ floor <= 100
    "THROTTLE_POS",                                               # Absolute Throttle Position - %, min @ idle > 0, max @ WOT <= 100
    "RPM",                                                        # revolutions per minute
    "SPEED",                                                      # kilometers per hour
    "GNGNS-alt",                                                  # altitude in meters
    "GNGNS-lat",                                                  # latitude in decimal degrees
    "GNGNS-lon",                                                  # longitude in decimal degrees
    "NMEA_GNGNS-alt",                                             # altitude in meters
    "NMEA_GNGNS-lat",                                             # latitude in decimal degrees
    "NMEA_GNGNS-lon",                                             # longitude in decimal degrees
    "gravity-x",                                                  # meters per second squared
    "gravity-y",                                                  # meters per second squared
    "gravity-z",                                                  # meters per second squared
    "gyroscope-x",                                                # radians per second
    "gyroscope-y",                                                # radians per second
    "gyroscope-z",                                                # radians per second
    "linear_acceleration-x",                                      # meters per second squared
    "linear_acceleration-y",                                      # meters per second squared
    "linear_acceleration-z",                                      # meters per second squared
    "magnetometer-x",                                             # micro Tesla (uT)
    "magnetometer-y",                                             # micro Tesla (uT)
    "magnetometer-z",                                             # micro Tesla (uT)
    "rotation_vector-pitch",                                      # radians
    "rotation_vector-roll",                                       # radians
    "rotation_vector-yaw",                                        # radians
#    "rotation_vector-vector-w",                                   # dimensionless scaler
#    "rotation_vector-vector-x",                                   # dimensionless vector component
#    "rotation_vector-vector-y",                                   # dimensionless vector component
#    "rotation_vector-vector-z",                                   # dimensionless vector component
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
    "COMMANDED_EQUIV_RATIO",                                      # air/fuel equivalence ratio
    "ENGINE_LOAD",                                                # % of maximum torque
    "FUEL_LEVEL",                                                 # % of useable fuel capacity
    "FUEL_RATE",                                                  # liters per hour
    "FUEL_RATE_2-engine_fuel_rate",                               # grams per second
    "FUEL_RATE_2-vehicle_fuel_rate",                              # grams per second
    "ODOMETER",                                                   # Kilometers
    "MAF",                                                        # grams per second
    "THROTTLE_ACTUATOR",                                          # Gas Pedal Position - %, min @ idle = 0, max @ floor <= 100
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
    "magnetometer-x",                                             # micro Tesla (uT)
    "magnetometer-y",                                             # micro Tesla (uT)
    "magnetometer-z",                                             # micro Tesla (uT)
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
    'gps_distance',                                               # Kilometers
    'gps_heading',                                                # radians
    'gps_road_grade',                                             # percentage (100 * (rise/run))
    'gps_rise',                                                   # meters
    'gps_pitch',                                                  # radians
    'gps_yaw',                                                    # radians
    'vehicle_fuel_grams',                                         # total grams for record duration
    'vehicle_fuel_milliliters',                                   # total milliliters for record duration
    'fuel_milliliters',                                           # total milliliters for record duration
    'fuel_rate',                                                  # milliliters per second
    'fuel_maf_grams',                                             # total grams for record duration
    'fuel_maf_milliliters',                                       # total milliliters for record duration
    'fuel_maf_rate_milliliters',                                  # milliliters per second
    'fuel_maf_lambda_maf_grams',                                  # total grams for record duration
    'fuel_lambda_maf_milliliters',                                # total milliliters for record duration
    'fuel_lambda_maf_rate_milliliters',                           # milliliters per second
    'rotation_vector-record_number', 
    'engine_fuel_grams', 
    'engine_fuel_milliliters', 
    'magnetometer-record_number', 
    'gyroscope-record_number', 
    'linear_acceleration-record_number', 
    'gravity-record_number', 
    'fuel_lambda_maf_grams',
]

previous_input_columns = [
    "ENGINE_LOAD",                                                # % of maximum torque
    "FUEL_LEVEL",                                                 # % of useable fuel capacity
    "FUEL_RATE",                                                  # liters per hour
    "FUEL_RATE_2-engine_fuel_rate",                               # grams per second
    "FUEL_RATE_2-vehicle_fuel_rate",                              # grams per second
    "ODOMETER",                                                   # Kilometers
    "MAF",                                                        # grams per second
    "THROTTLE_ACTUATOR",                                          # Gas Pedal Position - %, min @ idle = 0, max @ floor <= 100
    "THROTTLE_POS",                                               # Absolute Throttle Position - %, min @ idle > 0, max @ WOT <= 100
    "RPM",                                                        # revolutions per minute
    "SPEED",                                                      # kilometers per hour
    "GNGNS-alt",                                                  # altitude in meters
    "GNGNS-lat",                                                  # latitude in decimal degrees
    "GNGNS-lon",                                                  # longitude in decimal degrees
    "iso_ts_post",                                                # timestamp
    "iso_ts_pre",                                                 # timestamp
    'gps_heading',
]

console = Console()

def save_fuel_study_data_to_csv(vin:str, output_file_name:str, obd_fuel_study:list, force_save=False):
    # sourcery skip: remove-unnecessary-cast
    console.print(f"Creating fuel study CSV file for {vehicles[vin]['name']} as {str(output_file_name).replace(vin, fake_vin)}")

    if Path(output_file_name).is_file() and not force_save:
        console.print(f"\tCSV file for {vehicles[vin]['name']} already exists - skipping...")
    else:
        with open(output_file_name, "w") as csv_output:
            writer = csv.DictWriter(csv_output, fieldnames=fuel_study_output_columns, escapechar="\\")
            writer.writeheader()
            for row in obd_fuel_study:
                writer.writerow(row)

        console.print(f"\tCSV file for {vehicles[vin]['name']} created")

    return

def generate_fuel_study_data(vin:str, output_file_name:str, csv_file_dir:str, force_save=False, verbose=False)->int:
    """
    open output CSV for writing
    for each input CSV file associated with a single VIN
        increment route_counter
        for each line in input CSV file
            calculate additional fields
            write new fields to output CSV
    returns total number of rows processed
    """
    Path(csv_file_dir).mkdir(parents=True, exist_ok=True)

    console.print(
        f"Generating fuel study CSV file for {vehicles[vin]['name']} as " +
        f"{str(output_file_name).replace(vin, fake_vin)}"
    )

    theta_data = read_theta_data_file(theta_file_name)

    # each raw JSON data file, after transformation into a CSV file, will have a
    # unique 'route_counter' value assigned to it.
    route_counter = 0
    row_counter = 0

    if Path(output_file_name).is_file() and not force_save:
        console.print(f"\tCSV file for {vehicles[vin]['name']} already exists - skipping...")
    else:
        with open(output_file_name, "w") as csv_output:
            writer = csv.DictWriter(csv_output, fieldnames=fuel_study_output_columns, escapechar="\\")
            writer.writeheader()

            # each row in the union of all CSV files has a unique row number 'i'
            i = 0

            for csv_data_file in (Path(csv_file_dir).glob(f"**/*integrated-{vin}.csv")):
                with open(csv_data_file, "r") as csv_file:
                    route_counter += 1
                    line_number = 0

                    # previous value setup
                    previous = {column: None for column in previous_input_columns}

                    reader = csv.DictReader(csv_file)
                    for row in reader:
                        i += 1
                        line_number += 1
                        row_counter += 1
                        record = {}

                        # convert floats
                        for column in input_float_columns:
                            try:
                                record[column] = float(row[column])
                            except ValueError:
                                record[column] = None

                        # Column names changed midway through data collection
                        #   "NMEA_GNGNS-alt" to "GNGNS-alt"
                        #   "NMEA_GNGNS-lat" to "GNGNS-lat"
                        #   "NMEA_GNGNS-lon" to "GNGNS-lon"
                        for column in ['NMEA_GNGNS-alt', 'NMEA_GNGNS-lat', 'NMEA_GNGNS-lon', ]:
                            if record[column]:
                                record[column.replace('NMEA_', '')] = record[column]

                        # convert ints
                        for column in input_int_columns:
                            try:
                                record[column] = int(row[column])
                            except ValueError:
                                record[column] = None

                        # "rotation_vector-vector" is list
                        # if isinstance(record["rotation_vector-rotation_vector"], list):
                        #     record["rotation_vector-vector-w"] = record['rotation_vector'][0]
                        #     record["rotation_vector-vector-x"] = record['rotation_vector'][1]
                        #     record["rotation_vector-vector-y"] = record['rotation_vector'][2]
                        #     record["rotation_vector-vector-z"] = record['rotation_vector'][3]

                        # convert date/time
                        if isinstance(row['iso_ts_pre'], str):
                            record['iso_ts_pre'] = datetime.fromisoformat(row['iso_ts_pre'])

                        if isinstance(row['iso_ts_post'], str):
                            record['iso_ts_post'] = datetime.fromisoformat(row['iso_ts_post'])

                        record['duration'] = record['iso_ts_post'] - record['iso_ts_pre']
                        record['duration'] = record['duration'].total_seconds()

                        record['i'] = i
                        record['route'] = route_counter

                        # create modify fields
                        record['mps'] = None
                        record['rps'] = None
                        record['theta'] = None
                        if record['RPM'] is not None:
                            record['rps'] = record['RPM'] / 60.0
                        if record['SPEED'] is not None:
                            record['mps'] = record['SPEED'] * 0.44704
                        if record['mps'] is not None and record['rps'] is not None:
                            record['theta'] = atan2(record['mps'], record['rps'])

                        try:
                            record['acceleration'] = (((record['SPEED'] - previous['SPEED']) * 0.44704)
                                                        / record['duration'])
                        except Exception:
                            record['acceleration'] = None

                        # GPS
                        record['gps_distance'] = None
                        record['gps_heading'] = None
                        if (previous['GNGNS-lat'] is not None and
                                record['GNGNS-lat'] is not None and
                            previous['GNGNS-lon'] is not None and
                                record['GNGNS-lon'] is not None):

                            record['gps_distance'] = haversine(
                                (previous['GNGNS-lat'], previous['GNGNS-lon']),
                                (record['GNGNS-lat'], record['GNGNS-lon'])
                            )
                            record['gps_heading'] = heading(
                                (previous['GNGNS-lat'], previous['GNGNS-lon']),
                                (record['GNGNS-lat'], record['GNGNS-lon'])
                            )

                        record['gps_rise'] = None
                        if previous['GNGNS-alt'] is not None and record['GNGNS-alt'] is not None:
                            record['gps_rise'] = record['GNGNS-alt'] - previous['GNGNS-alt']

                        # USA Grade Definition
                        # https://en.wikipedia.org/wiki/Grade_(slope)
                        record['gps_pitch'] = None
                        record['gps_road_grade'] = None
                        if record['gps_rise'] is not None and record['gps_distance'] is not None:
                            record['gps_pitch'] = atan2(record['gps_rise'], record['gps_distance'])
                            if record['gps_distance'] != 0.0:
                                record['gps_road_grade'] = abs(100.0 * record['gps_rise'] / record['gps_distance'])

                        record['gps_yaw'] = None
                        if record['gps_heading'] is not None and previous['gps_heading'] is not None:
                            record['gps_yaw'] = record['gps_heading'] - previous['gps_heading']

                        # Weather - Wind Direction to Radians
                        if record['WTHR_rapid_wind-wind_direction'] is not None:
                            record['WTHR_rapid_wind-wind_direction'] = radians(record['WTHR_rapid_wind-wind_direction'])

                        if record['WTHR_obs_st-wind_direction'] is not None:
                            record['WTHR_obs_st-wind_direction'] = radians(record['WTHR_obs_st-wind_direction'])

                        # FUEL_RATE_2
                        # grams per second
                        # see fuel_grams_to_milliliters() in common.py for info.
                        record['engine_fuel_grams'] = None
                        record['engine_fuel_milliliters'] = None
                        if record['FUEL_RATE_2-engine_fuel_rate'] is not None:
                            record['engine_fuel_grams'] = record['FUEL_RATE_2-engine_fuel_rate'] * record['duration']
                            record['engine_fuel_milliliters'] = fuel_grams_to_milliliters(vin, record['engine_fuel_grams'])

                        record['vehicle_fuel_grams'] = None
                        record['vehicle_fuel_milliliters'] = None
                        if record['FUEL_RATE_2-vehicle_fuel_rate'] is not None:
                            record['vehicle_fuel_grams'] = record['FUEL_RATE_2-vehicle_fuel_rate'] * record['duration']
                            record['vehicle_fuel_milliliters'] = fuel_grams_to_milliliters(vin, record['vehicle_fuel_grams'])

                        # FUEL_RATE
                        # liters per hour to milliliters per second
                        # divide the volume / time value by 3.6
                        # This is not volume/temperature corrected.
                        record['fuel_milliliters'] = None
                        record['fuel_rate'] = None
                        if record['FUEL_RATE'] is not None:
                            record['fuel_rate'] = record['FUEL_RATE'] / 3.6
                            record['fuel_milliliters'] = record['fuel_rate'] * record['duration']

                        # fuel usage based on MAF alone
                        #   - https://www.windmill.co.uk/fuel.html
                        #       - "chemically ideal value of 14.7 grams of air to every gram of gasoline"
                        #   - SAE J1979DA Standard shows ideal value of 14.64
                        record['fuel_maf_grams'] = None
                        record['fuel_maf_milliliters'] = None
                        record['fuel_maf_rate_milliliters'] = None
                        if record['MAF'] is not None:
                            record['fuel_maf_rate_milliliters'] = (record['MAF'] / 14.64)
                            record['fuel_maf_grams'] = (record['MAF'] / 14.64) * record['duration']
                            record['fuel_maf_milliliters'] = fuel_grams_to_milliliters(vin, record['fuel_maf_grams'])

                        # fuel usage based on MAF and Lambda, Air/Fuel mixture ratio
                        #   - SAE J1979DA Standard for 0x44 COMMANDED_EQUIV_RATIO
                        record['fuel_lambda_maf_grams'] = None
                        record['fuel_lambda_maf_milliliters'] = None
                        record['fuel_lambda_maf_rate_milliliters'] = None
                        if record['MAF'] is not None and record['COMMANDED_EQUIV_RATIO'] is not None:
                            record['fuel_lambda_maf_rate_milliliters'] = (record['MAF'] / (14.64 * record['COMMANDED_EQUIV_RATIO']))
                            record['fuel_lambda_maf_grams'] = (record['MAF'] / (14.64 * record['COMMANDED_EQUIV_RATIO'])) * record['duration']
                            record['fuel_lambda_maf_milliliters'] = fuel_grams_to_milliliters(vin, record['fuel_lambda_maf_grams'])

                        # closest_gear assignment
                        if theta_data and vin in theta_data and record['theta']:
                            # find closest gear using theta_data[vin][gear]['theta'] being compared to record['theta']
                            gear_distance = None
                            closest_gear = 1
                            for gear in theta_data[vin]:
                                # sourcery skip: merge-nested-ifs
                                if gear:
                                    gear_distance = abs(theta_data[vin][gear]['theta'] - record['theta'])
                                    # sourcery skip: merge-nested-ifs
                                    if gear != closest_gear:
                                        if gear_distance < last_gear_distance:
                                            closest_gear = gear
                                    last_gear_distance = gear_distance

                            record['closest_gear'] = closest_gear
                        else:
                            record['closest_gear'] = 0

                        # need previous[column] to track all of the previous things
                        previous = {column: record[column] for column in previous_input_columns}

                        # The column names that changed midway through data collection
                        # need to be removed from the dictionary.
                        #   "NMEA_GNGNS-alt" to "GNGNS-alt"
                        #   "NMEA_GNGNS-lat" to "GNGNS-lat"
                        #   "NMEA_GNGNS-lon" to "GNGNS-lon"
                        for column in ['NMEA_GNGNS-alt', 'NMEA_GNGNS-lat', 'NMEA_GNGNS-lon', ]:
                            del record[column]

                        writer.writerow(record)

                if verbose:
                    print(f"{route_counter}: {str(csv_data_file).replace(vin, '<VIN>')}: {line_number} ")

    console.print(f"{vehicles[vin]['name']} rows: {row_counter} file count: {route_counter}")

    return row_counter
