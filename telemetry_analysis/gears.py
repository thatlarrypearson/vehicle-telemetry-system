# telemetry-analysis/telemetry_analysis/gears.py
#
# Gear Study Related functions
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
from scipy.signal import argrelextrema

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
)
from private.vehicles import vehicles

gear_study_input_columns = [
   "RPM",                                                        # revolutions per minute
   "SPEED",                                                      # kilometers per hour
   'duration',                                                   # seconds
   'iso_ts_pre',                                                 # UTC timestamp (before)
   'iso_ts_post',                                                # UTC timestamp (after)
]

gear_study_output_columns = [
   'i',                                                          # row number
   "RPM",                                                        # revolutions per minute
   "SPEED",                                                      # kilometers per hour
   'rps',                                                        # revolutions per second
   'mps',                                                        # meters per second
   'theta',                                                      # radians
   'radius',                                                     # not sure: meters per revolution?
   'm_per_r',                                                    # meters per rotation
   'r_per_m',                                                    # rotations per meter
   'closest_gear',                                               # ordinal gear number, integer 1 through 6
   'acceleration',                                               # meters per second squared
   'route',                                                      # source file number
   'duration',                                                   # seconds
   'iso_ts_pre',                                                 # UTC timestamp (before)
   'iso_ts_post',                                                # UTC timestamp (after)
]

gear_colors = {
1: 'blue',
2: 'orange',
3: 'green',
4: 'red',
5: 'purple',
6: 'brown',
7: 'pink',
8: 'gray',
9: 'olive',
10: 'cyan',
}

# Usable values for max_indices and vin_[xy]_values are generated in gear_study_kde_extrema_chart(vin:str, df:pd.DataFrame)
max_indices = None
vin_x_values = None
vin_y_values = None

console = Console()

def save_gear_study_data_to_csv(vin:str, output_file_name:str, obd_gear_study:list, force_save=True):
    console.print(f"Creating gear study CSV file for {vehicles[vin]['name']} as {output_file_name.replace(vin, fake_vin)}")
    if not obd_gear_study:
        ValueError("Empty OBD Gear Study passed to save_gear_study_data_to_csv()")

    if Path(output_file_name).is_file() and not force_save:
        console.print(f"\tCSV file for {vehicles[vin]['name']} already exists - skipping...")
    else:
        with open(output_file_name, "w") as csv_output:
            writer = csv.DictWriter(csv_output, fieldnames=gear_study_output_columns, escapechar="\\")
            writer.writeheader()
            for row in obd_gear_study:
                writer.writerow(row)

    return

def generate_gear_study_data(csv_file_dir:str, vin:str)->list:
    # sourcery skip: merge-dict-assign, move-assign-in-block, swap-nested-ifs
    Path(csv_file_dir).mkdir(parents=True, exist_ok=True)

    obd_gear_study = []
    theta_data = read_theta_data_file(theta_file_name)
    # console.print("theta_data = read_theta_data_file(theta_file_name)")
    # pprint(theta_data)
    bad_row_counter = 0

    # each raw JSON data file, after transformation into a CSV file, will have a
    # unique 'route_counter' value assigned to it.
    route_counter = 0

    # each row in the union of all CSV files has a unique row number 'i'
    i = 0

    for csv_data_file in (Path(csv_file_dir).glob(f"*{vin}*.csv")):
        with open(csv_data_file, "r") as csv_file:
            route_counter += 1
            previous_iso_ts_post = None
            previous_SPEED = 0
            line_number = 0

            # reader = csv.DictReader(csv_file, restkey="extra-junk", fieldnames=gear_study_input_columns)
            reader = csv.DictReader(csv_file)
            try:
                for row in reader:
                    i += 1
                    line_number += 1
                    record = {}
                    if (
                        row['SPEED'] is None or
                        len(row['SPEED']) == 0 or
                        row['RPM'] is None or
                        len(row['RPM']) == 0
                   ):
                        previous_iso_ts_post = None
                        previous_SPEED = 0
                        bad_row_counter += 1
                        continue

                    record['SPEED'] = float(row['SPEED'])
                    record['RPM'] = float(row['RPM'])

                    if (
                        record['SPEED'] <= 0.0 or
                        record['SPEED'] > 130.0 or
                        record['RPM'] < 400.0 or
                        record['RPM'] > 5000.0
                    ):
                        previous_iso_ts_post = None
                        previous_SPEED = 0
                        bad_row_counter += 1
                        continue

                    record['i'] = i
                    record['rps'] = record['RPM'] / 60.0
                    record['mps'] = record['SPEED'] * 0.44704
                    record['theta'] = atan2(record['mps'], record['rps'])
                    record['radius'] = sqrt((record['rps'] * record['rps']) + (record['mps'] * record['mps']))
                    if isinstance(row['iso_ts_pre'], str):
                        record['iso_ts_pre'] = parser.isoparse(row['iso_ts_pre'])
                    if isinstance(row['iso_ts_post'], str):
                        record['iso_ts_post'] = parser.isoparse(row['iso_ts_post'])
                    record['duration'] = record['iso_ts_post'] - record['iso_ts_pre']
                    record['duration'] = record['duration'].total_seconds()
                    record['acceleration'] = 0

                    if previous_iso_ts_post is not None:
                        time_delta = abs(record['iso_ts_pre'] - previous_iso_ts_post)
                        # route is current
                        record['acceleration'] = ((record['SPEED'] * 0.44704 - previous_SPEED * 0.44704)
                                                   / record['duration'])
                    record['route'] = route_counter
                    previous_iso_ts_post = record['iso_ts_post']
                    previous_SPEED = record['SPEED']

                    # ratio: meters per revolution
                    record['m_per_r'] = record['mps'] / record['rps']
                    # ratio: revolution per meter
                    record['r_per_m'] = record['rps'] / record['mps']

                    if theta_data and vin in theta_data:
                        # find closest gear using theta_data[vin][gear]['theta'] being compared to row['theta']
                        gear_distance = None
                        closest_gear = 1
                        for gear in theta_data[vin]:
                            if not gear:
                                continue
                            gear_distance = abs(theta_data[vin][gear]['theta'] - record['theta'])
                            if gear != closest_gear and gear_distance < last_gear_distance:
                                closest_gear = gear
                            last_gear_distance = gear_distance

                        record['closest_gear'] = closest_gear

                    else:

                        record['closest_gear'] = 0

                    obd_gear_study.append(record)

            except Exception as e:
                console.print(
                    f"oops {vehicles[vin]['name']}:\n{csv_data_file}\nline {line_number}\n{str(e)}"
                )
                pprint(row)
                pprint(record)

    console.print(f"{vehicles[vin]['name']} good rows: {len(obd_gear_study)} bad rows: {bad_row_counter} file count: {route_counter}")

    return obd_gear_study

# function to compute crossing points for a gear within the rectangle bounded by (xmin, ymin) and (xmax, ymax)
# relevant formula is:
#      tan(theta) = y/x
#
# function arguments:
#     xmin - left side of the bounding rectangle
#     xmax - right side of the bounding rectangle
#     ymin - bottom side of the bounding rectangle
#     ymax - top side of the bounding rectangle
#     theta - gear angle
#
# return value is a tuple representing two points (x1, y1) and (x2, y2) providing for a line that fits in/on the rectangle:
#          (x1, y1), (x2, y2)
#          or None when no solution for the line is found
def gear_lines(xmin:float, xmax:float, ymin:float, ymax:float, theta:float)->tuple:

    # solve for x when y is ymax
    x = ymax / tan(theta)
    if x <= xmax:
        # we have a solution
        return [(xmin, ymin), (x, ymax), ]

    # solve for y when x is xmax
    y = xmax * tan(theta)
    if y <= ymax:
        # we have a solution
        return [(xmin, ymin), (xmax, y), ]

    console.print(f"No valid points: xmin:{xmin}, xmax:{xmax}, ymin:{ymin}, ymax:{ymax}, theta:{theta}")
    return None


def gear_study_hexagonal_binning_chart(vin:str, df:pd.DataFrame):
    theta_data = read_theta_data_file(theta_file_name)

    # apply filters to better improve results by reducing error
    df2D = df
    df2D = df2D[(df2D['acceleration'] > 0)]

    xmin = df2D['rps'].min()
    xmax = df2D['rps'].max()
    ymin = df2D['mps'].min()
    ymax = df2D['mps'].max()

    if xmin == xmax or ymin == ymax:
        console.print(f"Hexagonal Binning Chart: Skipping {vehicles[vin]['name']} Gear-Study - no useful data")
        return

    fig, ax = plt.subplots(figsize=(8,8))
    sns.set_theme(style="ticks")

    plt.hexbin(
        'rps', 'mps', data=df2D,
        gridsize=25,
        xscale='linear', yscale='linear', bins='log',
        # https://matplotlib.org/stable/gallery/color/colormap_reference.html
        cmap='Purples', edgecolors='face'
    )

    ax.set_xlim(0.0, 80.0)
    ax.set_ylim(0.0, 60.0)

    if theta_data and vin in theta_data:
        for gear in vehicles[vin]['forward_gear_ratios']:
            if gear in theta_data[vin] and theta_data[vin][gear] and 'theta' in theta_data[vin][gear]:
                points = gear_lines(0.0, 80.0, 0.0, 60.0, theta_data[vin][gear]['theta'])
            df_points = pd.DataFrame(points, columns=['rps', 'mps'])
            axn = plt.plot( 'rps', 'mps', data=df_points, color=gear_colors[gear])
    else:
        console.print(f"{vehicles[vin]['name']} - theta_data not available")

    ax.set(title=f"{vehicles[vin]['name']} 2D hexagonal binning plot of points 'rps', 'mps' with 'theta_data' gear lines")
    plt.show()
    plt.close()

    return

def gear_study_rps_mps_kde_chart(vin:str, df:pd.DataFrame):
    theta_data = read_theta_data_file(theta_file_name)

    # apply filters to better improve results by reducing error
    df2D = df
    df2D = df2D[(df2D['acceleration'] > 0)]

    xmin = df2D['rps'].min()
    xmax = df2D['rps'].max()
    ymin = df2D['mps'].min()
    ymax = df2D['mps'].max()

    if xmin == xmax or ymin == ymax:
        console.print(f"KDE Chart: Skipping {vehicles[vin]['name']} Gear-Study - no useful data")
        return

    fig, ax = plt.subplots(figsize=(12,6))
    sns.set_theme(style="ticks")
    kde_plot = sns.kdeplot(   data=df2D,
                    x='rps',
                    y='mps',
                    fill=True,
                    cmap='Blues'
                )

    ax.set_xlim(0.0, 80.0)
    ax.set_ylim(0.0, 60.0)

    if theta_data and vin in theta_data:
        for gear in vehicles[vin]['forward_gear_ratios']:
            if gear in theta_data[vin] and theta_data[vin][gear] and 'theta' in theta_data[vin][gear]:
                points = gear_lines(0.0, 80.0, 0.0, 60.0, theta_data[vin][gear]['theta'])
            df_points = pd.DataFrame(points, columns=['rps', 'mps'])
            axn = plt.plot( 'rps', 'mps', data=df_points, color=gear_colors[gear])

    ax.set(title=f"{vehicles[vin]['name']} 'rps', 'mps' kernel density estimation (KDE) with 'theta_data' gear lines")
    plt.show()
    plt.close()

    return

def gear_study_kde_extrema_chart(vin:str, df:pd.DataFrame):
    # sourcery skip: flip-comparison, identity-comprehension, merge-dict-assign, move-assign-in-block
    # This computes the local maximums for 'theta' column kernel density estimation (KDE)
    # apply filters to better improve results by reducing error
    df2D = df
    df2D = df2D[(0.0 <= df2D['theta']) & (df2D['theta'] <= pi)]
    df2D = df2D[df2D['acceleration'] > 0]

    xmin = df2D['theta'].min()
    xmax = df2D['theta'].max()
    ymin = df2D['radius'].min()
    ymax = df2D['radius'].max()

    if xmin == xmax or ymin == ymax:
        console.print(f"Gear Study KDE Extrema Chart: Skipping {vehicles[vin]['name']} 'theta' KDE")
        return

    # df_theta_count = (df[vin]).groupby(['theta',]).size().reset_index().rename(columns={0:'count'})

    fig, ax = plt.subplots(figsize=(12,12))
    sns.set_theme(style="ticks")
    ax.set_xlim(0.0, 1.2)
    ax.set_ylim(0.0, 16.0)

    ax.set(title=f"{vehicles[vin]['name']} 'theta' kernel density estimation (KDE)")

    # axn = sns.kdeplot(data=df2D, ax=ax, x="theta", weights='count', color='green', fill=False)
    axn = sns.kdeplot(data=df2D, ax=ax, x="theta", color='green', fill=False)

    # for the following to work, above kdeplot fill parameter must be false.
    x, y = (ax.lines[0]).get_data()

    max_indices = argrelextrema(y, np.greater)

    x_values = x[max_indices]
    y_values = y[max_indices]
    
    vin_x_values = x_values
    vin_y_values = y_values

    plt.show()
    plt.close()

    # apply filters to better improve results by reducing error
    df2D = df
    df2D = df2D[(0.0 <= df2D['theta']) & (df2D['theta'] <= pi)]
    df2D = df2D[df2D['acceleration'] > 0]

    xmin = df2D['theta'].min()
    xmax = df2D['theta'].max()
    ymin = df2D['radius'].min()
    ymax = df2D['radius'].max()

    if xmin == xmax or ymin == ymax:
        console.print(f"Gear Study KDE Extrema Chart: Skipping {vehicles[vin]['name']} 'theta' KDE visualization")
        return

    fig, ax = plt.subplots(figsize=(12.0,12.0))
    sns.set_theme(style="ticks")
    ax.set_xlim(0.0, 1.2)
    ax.set_ylim(0.0, 16.0)

    for x, y in zip(vin_x_values, vin_y_values):
        # the position of the data label relative to the data point can be adjusted by adding/subtracting a value from the x &/ y coordinates
        fig.text(
            x=x,                              # x-coordinate position of data label
            y=(y+0.20),                       # y-coordinate position of data label, adjusted '-' below, '+' abovee the data point
            transform=ax.transData,           # gets the positioning relative to the plot axis
            s="{:.3f}".format(x),             # data label, formatted to ignore decimals
            color="red"                       # set text color
         )

    ax.set_xlim(0.0, 1.2)
    ax.set_ylim(0.0, 16.0)

    ax1 = sns.scatterplot(ax=ax, x=vin_x_values, y=vin_y_values, size_norm=None, marker='+', color='red', s=200)
    ax2 = ax.twinx()
    ax2.set_xlim(0.0, 1.2)
    ax2.set_ylim(0.0, 16.0)
    ax2.set(title=f"{vehicles[vin]['name']} 'theta' kernel density estimation (KDE) with local maximums")

    ax3 = sns.kdeplot(data=df2D, ax=ax2, x="theta", color='green', fill=True)
    
    plt.show()
    plt.close()

    # assume that there is some 'a' where gear_ratio = a * one_over_tan_theta
    # solving for a:  a = gear_ratio * tan(theta)

    df_dict = {}

    vehicle = vehicles[vin]
    vehicles['theta'] = {gear: theta for gear, theta in enumerate(vin_x_values, start=1)}
    df_dict['theta'] = [theta for gear, theta in enumerate(vin_x_values, start=1)]
    df_dict['one_over_tan_theta'] = [1.0/tan(theta) for gear, theta in enumerate(vin_x_values, start=1)]
    df_dict['gear']  = [gear for gear in vehicle['forward_gear_ratios']]
    df_dict['gear_ratio'] = [gear_ratio for gear, gear_ratio in vehicle['forward_gear_ratios'].items()]
    df_dict['a'] = [df_dict['gear_ratio'][i] * tan(df_dict['theta'][i]) for i, theta in enumerate(df_dict['theta'])]
    
    vehicles[vin]['theta'] = {gear: theta for gear, theta in enumerate(vin_x_values, start=1)}
    vehicles[vin]['one_over_tan_theta'] = {gear: 1.0/tan(theta) for gear, theta in enumerate(vin_x_values, start=1)}
    vehicles[vin]['a'] = {gear: vehicle['forward_gear_ratios'][gear] * tan(theta) for gear, theta in enumerate(vin_x_values, start=1)}

    if len(vehicle['forward_gear_ratios']) != len(vin_x_values):
        console.print(f"\n{80 * '*'}\n{vehicles[vin]['name']} Expecting {len(vehicle['forward_gear_ratios'])} gears, got {len(vin_x_values)} instead\n{80 * '*'}")
        for gear in range( (len(vin_x_values) + 1), (len(vehicle['forward_gear_ratios']) + 1)):
            vehicle['theta'][gear] = None
            df_dict['theta'].append(None)
            df_dict['one_over_tan_theta'].append(None)
            df_dict['a'].append(None)

    df_gear_study = pd.DataFrame.from_dict(df_dict)

    console.print(f"{vehicles[vin]['name']} computed 'a' values")

    basic_stats_table_generator(vin, basic_statistics(vin, ['a', ], df_gear_study))

    calculated_best_fit_gear_ratios(vin, vehicle)

    # the following updates the theta_data file automatically
    theta_data = generate_theta_data_from_vehicle(vin, vehicle)

    return theta_data

def kde_plot_overlay_for_each_gear(vin:str, df:pd.DataFrame):

    theta_data = read_theta_data_file(theta_file_name)

    gear_count = len(theta_data[vin])

    fig, ax = plt.subplots(figsize=(12,6))
    sns.set_theme(style="ticks")

    ax.set_xlim(0.0, 80.0)
    ax.set_ylim(0.0, 60.0)

    for gear in range(1, gear_count + 1):
        # apply filters to better improve results by reducing error
        df2D = (df)[((df)['closest_gear'] == gear) & ((df)['acceleration'] > 0.0)]

        if gear == 2:
            ax2 = ax.twinx()

        if gear == 1:
            axn = sns.kdeplot(data=df2D, ax=ax, x='rps', y='mps', fill=True, cmap=shades[gear])
            ax.set_xlim(0.0, 80.0)
            ax.set_ylim(0.0, 60.0)
        else:
            axn = sns.kdeplot(data=df2D, ax=ax2, x='rps', y='mps', fill=True, cmap=shades[gear])
            axn.set(yticklabels=[])  
            axn.set(title=None)
            axn.set(ylabel=None)
            axn.tick_params(right=False)
            axn.set_xlim(0.0, 80.0)
            axn.set_ylim(0.0, 60.0)

    if theta_data and vin in theta_data and gear in theta_data[vin] and 'theta' in theta_data[vin][gear]:
        for gear in theta_data[vin]:
            points = gear_lines(0.0, 80.0, 0.0, 60.0, theta_data[vin][gear]['theta'])
            df_points = pd.DataFrame(points, columns=['rps', 'mps'])
            axn = plt.plot( 'rps', 'mps', data=df_points, color='black')

    ax.set(title=f"{vehicles[vin]['name']} KDE plot overlay for each of {gear_count} gears where acceleration > 0 with 'theta_data' gear lines")

    plt.show()
    plt.close()

    return

def gear_study_samples_by_closest_gear(vin:str, df:pd.DataFrame):
    theta_data = read_theta_data_file(theta_file_name)

    gear_count = len(theta_data[vin])

    # apply filters to better improve results by reducing error
    df2D = (df)[(df)['closest_gear'] > 0]

    fig, ax = plt.subplots(figsize=(12,6))
    sns.set_theme(style="ticks")

    sns.histplot(data=df2D, x="closest_gear", discrete=True)

    ax.set(title=f"{vehicles[vin]['name']} Gear-Study Data Samples by Closest Gear in {gear_count} Gears")

    plt.show()
    plt.close()

    return

def gear_study_theta_histogram(vin:str, df:pd.DataFrame):
    # apply filters to better improve results by reducing error
    df2D = (df)[(df)['closest_gear'] > 0]

    fig, ax = plt.subplots(figsize=(12,6))
    sns.set_theme(style="ticks")

    sns.histplot(data=df2D, x="theta", discrete=False)
    ax.set(title=f"{vehicles[vin]['name']} histogram 'theta' sample count by 'theta' value")

    plt.show()
    plt.close()

    return

def gear_study_kde_plot_overlays_for_each_gear(vin:str, df:pd.DataFrame):
    theta_data = read_theta_data_file(theta_file_name)

    if not vin_x_values:
        ValueError("vin_x_values not set. run telemetry_analysis.gears.gear_study_kde_plot_overlays_for_each_gear() first")

    gear_count = len(theta_data[vin])

    fig, ax = plt.subplots(figsize=(12,6))
    sns.set_theme(style="ticks")

    ax.set_xlim(0.0, 1.2)
    ax.set_ylim(0.0, 16.0)

    for gear in range(1, gear_count + 1):
        # apply filters to better improve results by reducing error
        df2D = (df)[((df)['closest_gear'] == gear) & ((df)['acceleration'] > 0.0)]

        if gear == 2:
            ax2 = ax.twinx()

        # Note the difference between left and right axis ticks and label values.
        # Without the theta gear lines, left axis is first gear and right axis is the last gear.
        # With the theta gear lines, left axis is the first gear and right axis is the last gear's theta line.
        # Very confusing.
        if gear == 1:
            axn = sns.kdeplot(data=df2D, ax=ax, x='theta', fill=False, color=gear_colors[gear])
        else:
            axn = sns.kdeplot(data=df2D, ax=ax2, x='theta', fill=False, color=gear_colors[gear])

        ax.set_xlim(0.0, 1.2)
        ax.set_ylim(0.0, 16.0)

    for gear, x in enumerate(vin_x_values, start=1):
        points = [(x, 0.0), (x, 300.0),]
        df_theta = pd.DataFrame(points, columns=['theta', 'Density'])
        # sns.lineplot(data=df_theta, ax=ax2, x='theta', y='Density', color=gear_colors[gear], legend=False)
        axn = sns.lineplot(data=df_theta, ax=ax2, x='theta', y='Density', color='black', legend=False)
        axn.set(yticklabels=[])  
        axn.set(title=None)
        axn.set(ylabel=None)
        axn.tick_params(right=False)
        ax.set_xlim(0.0, 1.2)
        ax.set_ylim(0.0, 16.0)

    ax.set(title=f"{vehicles[vin]['name']} KDE plot overlays for each of {gear_count} gears when acceleration > 0")

    plt.show()
    plt.close()


# distance_error:
#   - an error that measures the distance between the (rps, mps) point and the theta gear line
# theta_error
#   - an error that is the difference between the theta gear line and the theta value calculated from the (rps, mps) point.for vin in vins:
def error_rate_estimation(vin:str, df:pd.DataFrame)->pd.DataFrame:
    theta_data = read_theta_data_file(theta_file_name)
    if not theta_data and vin not in theta_data:
        console.print(f"theta data not available for {vin}")
        return None

    df = df.reset_index()

    distance_errors = [
                            signed_point_to_theta_line_distance(
                                row['rps'], row['mps'], theta_data[vin][row['closest_gear']]['theta']
                            ) if row['closest_gear'] else None
                            for index, row in df.iterrows()
                        ]

    df['distance_error'] = distance_errors

    theta_errors = [
                        (theta_data[vin][row['closest_gear']]['theta'] - row['theta']) if row['closest_gear'] else None
                        for index, row in df.iterrows()
                    ]

    df['theta_error'] = theta_errors

    return df

# what is the relationship between:
#    - 'acceleration' and 'theta_error'
#    - 'acceleration' and 'distance_error'
#    - 'acceleration' and 'rps'
#    - 'acceleration' and 'mps'
# when 'acceleration' > 0
def error_relationships(vin:str, df:pd.DataFrame):
    theta_data = read_theta_data_file(theta_file_name)
    
    if theta_data and vin not in theta_data:
        console.print(f"{vehicles[vin]['name']} - skipping error relationships kernel density estimation (KDE)")
        return
    
    for y_column_name in ['acceleration', 'rps', 'mps', ]:
        for x_column_name in ['theta_error', 'distance_error', ]:

            for sgear in theta_data[vin]:
                gear = int(sgear)
                if gear == 0:
                    continue

                df2D = df
                # df2D = df2D[df2D['acceleration'] > 0.0]
                df2D = df2D[df2D['closest_gear'] == gear]

                xmin = df2D[x_column_name].min()
                xmax = df2D[x_column_name].max()
                ymin = df2D[y_column_name].min()
                ymax = df2D[y_column_name].max()

                if xmin == xmax or ymin == ymax:
                    console.print(
                        f"Skipping {vehicles[vin]['name']} Gear-Study: ({x_column_name}, {y_column_name}), gear {gear}"
                    )
                    continue

                fig, ax = plt.subplots(figsize=(12,6))
                sns.set_theme(style="ticks")

                try:
                    kde_plot = sns.kdeplot(   data=df2D,
                                    x=x_column_name,
                                    y=y_column_name,
                                    fill=True,
                                    cmap='Blues'
                                )

                except Exception as e:
                    # ValueError: Contour levels must be increasing
                    # Want to know when this is happening.  Don't want to stop execution.
                    console.print(
                        f"{repr(type(e))} Exception Occurred:\n" +
                        f"\t{vehicles[vin]['name']} ('{x_column_name}', '{y_column_name}') " +
                        f"kernel density estimation (KDE) where gear = {gear}\n" +
                        repr(e)
                    )

                ax.set_xlim(xmin, xmax)
                ax.set_ylim(ymin, ymax)

                ax.set(
                    title=(
                            f"{vehicles[vin]['name']} ('{x_column_name}', '{y_column_name}') " +
                            f"kernel density estimation (KDE) where gear = {gear}"
                        )
                    )
                plt.show()
                plt.close()

    return

# Compute the local maximums for 'theta_error' column kernel density estimation (KDE)
def theta_error_local_maximums(vin:str, df:pd.DataFrame, verbose=False):
    # sourcery skip: flip-comparison
    theta_data = read_theta_data_file(theta_file_name)
    
    if theta_data and vin not in theta_data:
        console.print(f"{vehicles[vin]['name']} - skipping error relationships kernel density estimation (KDE)")
        return
    
    if verbose:
        console.print(f"{vehicles[vin]['name']} - working on error relationships kernel density estimation (KDE)")

    vin_gear_x_values = {}
    vin_gear_y_values = {}
    for sgear in theta_data[vin]:

        gear = int(sgear)
        if gear == 0:
            continue

        df2D = df

        df2D = df2D[(0.0 <= df2D['theta']) & (df2D['theta'] <= pi)]
        # df2D = df2D[df2D['acceleration'] > 0]
        df2D = df2D[df2D['closest_gear'] == gear]

        xmin = df2D['theta_error'].min()
        xmax = df2D['theta_error'].max()

        if xmin == xmax:
            console.print(
                f"Skipping {vehicles[vin]['name']} Gear-Study gear {gear} Theta Error Local Maximums"
            )
            continue

        if verbose:
            console.print(
                f"Working {vehicles[vin]['name']} Gear-Study gear {gear} Theta Error Local Maximums"
            )

        fig, ax = plt.subplots(figsize=(12,12))
        sns.set_theme(style="ticks")
        ax.set_xlim(xmin, xmax)

        ax.set(title=f"{vehicles[vin]['name']} gear {gear} 'theta_error' kernel density estimation (KDE)")

        axn = sns.kdeplot(ax=ax, data=df2D, x="theta_error", color='green', fill=False)

        # for the following to work, above kdeplot fill parameter must be false.
        x, y = (ax.lines[0]).get_data()

        max_indices = argrelextrema(y, np.greater)

        x_values = x[max_indices]
        y_values = y[max_indices]

        vin_gear_x_values[gear] = x_values
        vin_gear_y_values[gear] = y_values

        plt.show()
        plt.close()

        xmin = df2D['theta_error'].min()
        xmax = df2D['theta_error'].max()
        ymin = (vin_gear_y_values[gear]).min()
        ymax = (vin_gear_y_values[gear]).max()
        mean = (df2D['theta_error']).mean()
        std = (df2D['theta_error']).std()

        ymax = ymax + (ymax * 0.10)

        if xmin == xmax:
            console.print(f"Skipping {vehicles[vin]['name']} gear {gear} 'theta_error' kernel density estimation (KDE)")
            continue

        fig, ax = plt.subplots(figsize=(12.0,12.0))
        sns.set_theme(style="ticks")
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)

        for x, y in zip(vin_gear_x_values[gear], vin_gear_y_values[gear]):
            # the position of the data label relative to the data point can be adjusted by adding/subtracting a value from the x &/ y coordinates
            fig.text(
                x=x,                              # x-coordinate position of data label
                y=(y+0.20),                       # y-coordinate position of data label, adjusted '-' below, '+' abovee the data point
                transform=ax.transData,           # gets the positioning relative to the plot axis
                s="{:.3f}".format(x),             # data label, formatted to ignore decimals
                color="red"                       # set text color
             )

        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)

        ax1 = sns.scatterplot(ax=ax, x=vin_gear_x_values[gear], y=vin_gear_y_values[gear], size_norm=None, marker='+', color='red', s=200)
        ax2 = ax.twinx()
        ax2.set_xlim(xmin, xmax)
        ax2.set_ylim(ymin, ymax)
        ax2.set(title=f"{vehicles[vin]['name']} gear {gear}\n'theta_error' kernel density estimation (KDE) with local maximums\nNormal Distribution with mean {mean:.4f} and standard deviation {std:.4f}")

        # Kernel Density Estimation plot
        ax3 = sns.kdeplot(ax=ax2, data=df2D, x="theta_error", color='green', fill=True)

        # Create a list of values for the x-axis
        x_axis = np.linspace(xmin, xmax, 400)

        # Calculate the probability density function for each value of x
        probability_density_function = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-(x_axis - mean)**2 / (2 * std**2))

        # Plot the probability density function
        ax4 = sns.lineplot(ax=ax2, x=x_axis, y=probability_density_function, color='blue')

        # plot mean and standard deviations
        ax5 = sns.lineplot(ax=ax2, x=(mean, mean), y=(ymin, ymax), color='blue', linewidth=2.0)
        ax6 = sns.lineplot(ax=ax2, x=(mean - std, mean - std), y=(ymin, ymax), color='black', linewidth=1.5)
        ax7 = sns.lineplot(ax=ax2, x=(mean + std, mean + std), y=(ymin, ymax), color='black', linewidth=1.5)
        ax8 = sns.lineplot(ax=ax2, x=(mean - (2 * std), mean - (2 * std)), y=(ymin, ymax), color='red', linewidth=1.5)
        ax9 = sns.lineplot(ax=ax2, x=(mean + (2 * std), mean + (2 * std)), y=(ymin, ymax), color='red', linewidth=1.5)

        plt.show()
        plt.close()

def route_report(vin:str, df:pd.DataFrame):
    # DataFrame Columns
    #   i, route,
    #   rps, mps, theta, radius, closest_gear,
    #   RPM, SPEED,
    #   m_per_r, r_per_m, acceleration, iso_ts_pre, iso_ts_post, duration
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column('Vehicle', justify='left')
    table.add_column('route', justify='right')
    table.add_column('rows', justify='right')
    table.add_column('i\nmin', justify='right')
    table.add_column('i\nmax', justify='right')
    table.add_column('duration\nmin', justify='right')
    table.add_column('duration\nmax', justify='right')
    table.add_column('duration\navg', justify='right')

    table.add_row(
            vehicles[vin]['name'],
            " ",
            " ",
            " ",
            " "
    )

    df2D = df

    # unique list of routes
    routes = (df2D['route']).unique()

    for route in routes:
        imin = (df2D[df2D['route'] == route])['i'].min()
        imax = (df2D[df2D['route'] == route])['i'].max()
        dmin = (df2D[df2D['route'] == route])['duration'].min()
        dmax = (df2D[df2D['route'] == route])['duration'].max()
        dmean = (df2D[df2D['route'] == route])['duration'].mean()
        table.add_row(
            " ",
            f"{route}",
            f"{imax - imin}",
            f"{imin}",
            f"{imax}",
            f"{dmin}",
            f"{dmax}",
            f"{dmean:.2f}"
        )

    console.print(table)

    return

def route_by_name_table(vin:str, df:pd.DataFrame):
    console.print("route_by_name = [")

    # unique list of routes
    routes = df['route'].unique()

    for route in routes:
        # ('2023 Ford Maverick Lariat', 7),
        console.print(f"\t# ('{vehicles[vin]['name']}', {route}),\t# count: {(df[df['route'] == route]).shape[0]}")

    console.print("]")
    return

def generate_images_for_video(name:str, route:int, df:pd.DataFrame, create_video=False, verbose=False):
    # set create_video=True when your system (not Windows) is able to run ffmpeg 
    theta_data = read_theta_data_file(theta_file_name)

    # video creation parameters
    xspeed = 2.0
    yspeed = 55.0
    xrpm = 70.0
    yrpm = 2.0
    xgear = xspeed
    ygear = yspeed - 5.0
    xfps = xgear              # frames per second x coordinate
    yfps = ygear - 5.0        # frames per second y coordinate
    xsecs = xfps              # seconds into video (reflects drive time) x coordinate
    ysecs = yfps - 5.0        # seconds into video (reflects drive time) y coordinate
    trailing_points = 4
    video_frame_rate = 16

    vin = get_vin_from_vehicle_name(name)

    if not vin:
        console.print(f"Vehicle name <{name}> not found in private.vehicles.py")
        return

    console.print(f"\t# ('{name}', {route}),\t# count: {(df[df['route'] == route]).shape[0]}")


    elapsed_time = None
    vehicle_name = (vehicles[vin]['name']).replace(' ', '-')

    image_file_full_path = f"{base_image_file_path}/{vehicle_name}/{route}"
    Path(image_file_full_path).mkdir(parents=True, exist_ok=True)

    mp4_file_full_path = f"{base_ffmpeg_file_path}/{vehicle_name}"
    Path(mp4_file_full_path).mkdir(parents=True, exist_ok=True)

    if verbose:
        console.print(f"image file full path {image_file_full_path}")

    imin = (df[df['route'] == route])['i'].min()
    imax = (df[df['route'] == route])['i'].max()

    for i in range(imin, imax + 1):
        image_file_name = f"{i:010}.{image_file_extn}"
    
        if Path(f"{image_file_full_path}/{image_file_name}").is_file():
            # No need to recreate image file if it already exists.
            # Memory error/leak in matplotlib/seaborn causes out of memory errors
            # so restarts might be required.
            if verbose:
                console.print(f"Image file already exists, skipping: {image_file_name}")
            continue

        df_route_i = df[(df['i'] <= i) & (df['i'] >= (i - trailing_points))]

        current_row = (df[(df['i'] == i)]).to_dict(orient='records')

        if len(current_row) == 0:
            if verbose:
                console.print(f"Current row length 0, skipping: {image_file_name}")
            continue

        if elapsed_time is None:
            elapsed_time = timedelta(seconds=current_row[0]['duration'])
        else:
            elapsed_time += timedelta(seconds=current_row[0]['duration'])

        kph = current_row[0]['SPEED']
        rpm = current_row[0]['RPM']
        mph = kph * 0.621371

        closest_gear = current_row[0]['closest_gear']

        fig, ax = plt.subplots(figsize=(12,6))
        sns.set_theme(style="ticks")
        kde_plot = sns.scatterplot(
            data=df_route_i,
            x='rps', y='mps',
            hue='i', palette='Blues', legend=False, hue_norm=(i-trailing_points, i), s=200
        )

        ax.set_xlim(0.0, 80.0)
        ax.set_ylim(0.0, 60.0)

        fig.text(
                x=xspeed,                       # x-coordinate position of data label
                y=yspeed,                       # y-coordinate position of data label, adjusted '-' below, '+' abovee the data point
                transform=ax.transData,         # gets the positioning relative to the plot axis
                # s=f"KPH:{kph:4.0f}",          # kilometers per hour data label, formatted to ignore decimals
                s=f"MPH:{mph:5.1f}",            # miles per hour data label, formatted to ignore decimals
                color="blue"                    # set text color
        )
        fig.text(
            x=xrpm,                             # x-coordinate position of data label
            y=yrpm,                             # y-coordinate position of data label, adjusted '-' below, '+' above the data point
            transform=ax.transData,             # gets the positioning relative to the plot axis
            s=f"RPM:{rpm:5.0f}",                # revolutions per minute data label, formatted to ignore decimals
            color="blue"                        # set text color
        )
        fig.text(
            x=xfps,                             # x-coordinate position of data label
            y=yfps,                             # y-coordinate position of data label, adjusted '-' below, '+' above the data point
            transform=ax.transData,             # gets the positioning relative to the plot axis
            s=f"FPS:{video_frame_rate:8}",   # frames per second data label, formatted to ignore decimals
            color="blue"                        # set text color
        )
        fig.text(
            x=xsecs,                            # x-coordinate position of data label
            y=ysecs,                            # y-coordinate position of data label, adjusted '-' below, '+' above the data point
            transform=ax.transData,             # gets the positioning relative to the plot axis
            s=f"{timedelta_to_hhmmss_str(elapsed_time)}",  # hh:mm:ss data label, formatted to ignore decimals
            color="blue"                        # set text color
        )
        fig.text(
            x=xgear,                            # x-coordinate position of data label
            y=ygear,                            # y-coordinate position of data label, adjusted '-' below, '+' above the data point
            transform=ax.transData,             # gets the positioning relative to the plot axis
            s=f"gear:{closest_gear:8}",        # hh:mm:ss data label, formatted to ignore decimals
            color="blue"                        # set text color
        )

        for gear in vehicles[vin]['forward_gear_ratios']:
            if gear in theta_data[vin] and 'theta' in theta_data[vin][gear] and theta_data[vin][gear]['theta']:
                points = gear_lines(0.0, 80.0, 0.0, 60.0, theta_data[vin][gear]['theta'])
                df_points = pd.DataFrame(points, columns=['rps', 'mps'])
                if gear == closest_gear:
                    axn = plt.plot( 'rps', 'mps', data=df_points, color='black', linewidth=2.0)
                else:
                    axn = plt.plot( 'rps', 'mps', data=df_points, color=gear_colors[gear])

        ax.set(title=f"{vehicles[vin]['name']} 'rps', 'mps' video with 'theta_data' gear lines")

        if verbose:
            console.print(f"- {image_file_full_path}/{image_file_name}")

        plt.savefig(f"{image_file_full_path}/{image_file_name}", dpi=300)
        plt.close()

    # !ffmpeg -framerate 30 -pattern_type glob -i '*.jpg' -c:v libx264 -pix_fmt yuv420p Jeep-12-fr30.mp4
    # !ffmpeg -framerate 2 -pattern_type glob -i '*.jpg' -c:v libx264 -pix_fmt yuv420p Jeep-12-fr02.mp4
    # !ffmpeg -framerate 1 -pattern_type glob -i '*.jpg' -c:v libx264 -pix_fmt yuv420p Jeep-12-fr01.mp4

    # Windows command line ffmpeg doesn't support globbing
    # I'm running ffmpeg in Ubuntu on WSL (Windows Subsystem for Linux)
    command_line = [
        ffmpeg_program_path,
        '-framerate', f"{video_frame_rate}",
        # following works well for small to large numbers of image files but doesn't work on Windows
        '-pattern_type', 'glob', '-i', f"{base_image_file_path}/{vehicle_name}/{route}/'*.jpg'",
        # on windows, doing following might result in overflowing shell buffers
        # '-i', f"{base_image_file_path}/*.jpg",
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        f"{mp4_file_full_path}/{vehicle_name}-{route}-fps{video_frame_rate:02}.mp4"
    ]

    console.print(f"{' '.join(command_line).replace(vin, fake_vin)}")

    if create_video:
        child = subprocess.Popen(command_line, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        console.print(child.stdout.read())

    return

def column_range_study_column(df:pd.DataFrame, column_name:str)->dict:
    return_value = {}
    return_value['count'] = df.shape[0]
    return_value['mean']  = df[column_name].mean()
    return_value['std']   = df[column_name].std()
    return_value['min']   = df[column_name].min()
    return_value['max']   = df[column_name].max()

    return return_value

def column_range_study(df:pd.DataFrame, column_name:str)->dict:
    # column value ranges are based on mean and standard deviation creating 4 ranges where
    # first quartile:  -2*stddev <= column values <= -1*stddev
    # second quartile: -1*stddev <= column values <= mean
    # third quartile:     mean <= column values <= +1*stddev
    # fourth quartile: +1*stddev <= column values <= +2*stddev

    df = df[~df[column_name].isnull()]
    # get sorted list of closest_gears
    gear_list = sorted((df[~df['closest_gear'].isnull()])['closest_gear'].unique())

    # return value == rv
    rv = {
        'column_name': column_name,
        'column_stats': column_range_study_column(df, column_name),
        'theta_error_stats': column_range_study_column(df, 'theta_error'),
        'gears': {},
    }

    for gear in gear_list:
        if gear == 0:
            continue

        # gear df == gdf
        gdf = df[df['closest_gear'] == gear]
        crsc = column_range_study_column(gdf, column_name)

        tdf0 = df[
            ((-2.0*crsc['std']) <= df[column_name]) & (df[column_name] < (-1.0*crsc['std']))
        ]
        tdf1 = df[
            ((-1.0*crsc['std']) <= df[column_name]) & (df[column_name] < (crsc['mean']))
        ]
        tdf2 = df[
            ((crsc['mean']) <= df[column_name]) & (df[column_name] < (crsc['std']))
        ]
        tdf3 = df[
            ((crsc['std']) <= df[column_name]) & (df[column_name] <= (2.0*crsc['std']))
        ]
        rv['gears'][gear] = {
            'column_stats': crsc,
            'theta_error_stats': column_range_study_column(gdf, 'theta_error'),
            'quantile_stats': {
                '-2*std <= value < -1*std': {
                    'column_stats': column_range_study_column(tdf0, column_name),
                    'theta_error_stats': column_range_study_column(tdf0, 'theta_error')
                },
                '-1*std <= value < mean': {
                    'column_stats': column_range_study_column(tdf1, column_name),
                    'theta_error_stats': column_range_study_column(tdf1, 'theta_error')
                },
                'mean <= value < std': {
                    'column_stats': column_range_study_column(tdf2, column_name),
                    'theta_error_stats': column_range_study_column(tdf2, 'theta_error')
                },
                'std <= value < 2*std': {
                    'column_stats': column_range_study_column(tdf3, column_name),
                    'theta_error_stats': column_range_study_column(tdf3, 'theta_error')
                },
            },
        }

    return rv
