#!/usr/bin/env python
# coding: utf-8

# # Gear Study - Gear Determination And Error Estimation
# 
# This notebook uses statistical methods to determine the most likely gear ratios for each vehicle and stores the results in a file for later use.  Additionaly, error calculations are used to estimate the total error between calculated gear ratios and:
# 
# - gear ratios in vehicle documentation
# - angles calculated from SPEED and RPM pairs in records
# 
# ## Gear Determiniation
# 
# Vehicle gears are calculated from the following:
# 
# 1. Create new data fields from existing records
# 
#    a. Calculate acceleration as (SPEED<sub>i+1</sub> - SPEED<sub>i</sub>) / (iso_ts_pre<sub>i+1</sub> - iso_ts_pre<sub>i</sub>)
# 
#    b. Calculate revolutions per second (rps) as RPM / 60
# 
#    c. Calculate meters per second (mps) as SPEED * 0.44704
# 
# 2. Filter out all records when acceleration <= 0.0
# 
#    a. With some vehicles, this will need to be changed.  See file ```vehicle-telemetry-system/src/private/example-vehicles.py``` and look for ```vehicles[vin]['gear_study_dataframe_filter']```.
# 
#    b. The code that activates the filter can be found at ```vehicle-telemetry-system/src/telemetry_analysis/fuel.py``` in function ```gear_study_df_filter```.
# 
# 4. Filter out all records where SPEED <= 0 or SPEED > 130.0
# 5. Filter out all records where RPM < 400.0 or > 5000.0
# 6. Calculate theta<sub>i</sub>, the angle between vectors x<sub>rps</sub> and y<sub>mps</sub>, for each record using atan2(mps<sub>i</sub>, rps<sub>i</sub>)
# 7. Generate Kernel Density Estimate (KDE) plot using Gaussian kernels
# 8. Calculate the relative extrema of the KDE plot points
# 9. Save the relative extrema for later use
# 
# Limitations to this method affecting results include:
# 
# - Too few valid samples of RPM/SPEED for each gear
# - Excessive transmission, clutch and/or torque converter slip in some or all gears
# 
# For example, early results from 2023 Ford Maverick Lariat resulted in only 5 out of 8 gears identified.  It looked like the lower 3 gears were most affected by this limitation.
# 
# ## Theta File - Machine Generated File Containing Gear Information For Each Vehicle
# 
# 
# ## Error Rate Estimation
# 
# distance_error:
# - An error that measures the distance between the (rps, mps) point and the theta gear line.
# 
# theta_error:
# - An error that is the difference between the theta gear line and the theta value calculated from the (rps, mps) poin:
# 
# 
# ## Conversion
# 
# To convert this Jupyter Notebook to Markdown, run:
# 
# - ```python -m nbconvert --to=markdown --output-dir=../markdown Gear-Study-1.ipynb```
# 
# To convert this Jupyter Notebook to Python code, run:
# 
# - ```python -m nbconvert --to=python --output-dir=src/ Gear-Study-1.ipynb```
# 

# In[1]:


# Increase Jupyter Notebook display width to be the screen width
from IPython.display import display, HTML
display(HTML("<style>.container { width:100% !important; }</style>"))
display(HTML("<style>.output_result { max-width:100% !important; }</style>"))

# Enable imports relative to notebook
# https://mattoppenheim.com/2018/03/16/relative-imports-in-jupyter-notebooks/
# python -m pip install nbimporter
# conda install -c akode nbimporter
import nbimporter


# In[2]:


import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import ipywidgets as widgets
from datetime import datetime, timedelta, timezone
import pytz
import sys
import csv
from pathlib import Path
import numpy as np
import pandas as pd
from os import linesep as LF

# pip install rich
from rich.console import Console


# In[3]:


# Set Raspberry Pi zimezone
# See https://en.wikipedia.org/wiki/List_of_tz_database_time_zones  for list of timezone strings
rpi_timezone = pytz.timezone('US/Central')
telemetry_obd_sys_timezone = pytz.timezone('US/Central')

np.set_printoptions(linewidth=180)
pd.set_option("display.max.columns", None)

console = Console(width=140)


# In[4]:


# Enable imports from telemetry-analysis
for path in [str(Path.cwd().parent / Path("src")), ]:
    print(f"Adding to Python Path: {path}")
    sys.path.append(path)

from private.vehicles import vehicles
from telemetry_analysis.vins import fake_vin
from telemetry_analysis.theta import read_theta_data_file, theta_file_name
from telemetry_analysis.common import temporary_file_base_directory

from telemetry_analysis.widgets import select_vin_dialog
from telemetry_analysis.reports import (
    obd_log_evaluation_report,
    basic_statistics,
    generate_basic_stats_report,
    plot_color_table,
)
from telemetry_analysis.gears import (
    save_gear_study_data_to_csv,
    generate_gear_study_data,
    gear_study_input_columns,
    gear_study_output_columns,
    gear_study_simple_histogram,
    gear_study_hexagonal_binning_chart,
    gear_study_rps_mps_kde_chart,
    gear_study_kde_extrema_chart,
    kde_plot_overlay_for_each_gear,
    gear_study_samples_by_closest_gear,
    gear_study_theta_histogram,
    error_rate_estimation,
    error_relationships,
    theta_error_local_maximums,
)
from telemetry_analysis.data_files import obd_to_csv


# In[5]:


# colors used in gear color lines
plot_color_table()


# In[6]:


vins = select_vin_dialog(verbose=True)

vehicle_names = [vehicles[vin]['name'] for vin in vins]

print(f"Data available as of {datetime.now()} from data sets: \n  - {(LF + '  - ').join(vehicle_names)}")


# In[7]:


# read theta data if available
theta_data = read_theta_data_file(theta_file_name)


# In[8]:


# Write obd_gear_study_data[vin] to csv files
########################################################

for vin in vins:
    #   - Each vehicle file is written to a smaller temporary csv file using the same basename by obd_log_to_csv_main()
    #   - Each temporary vehicle file gets processed and added to obd_files with a unique route number by generate_gear_study_data()
    obd_to_csv(vin, gear_study_input_columns)

    # Gear Study Data is created in this step
    force_new_gear_study = False
    if not (theta_data := read_theta_data_file(theta_file_name)) or vin not in theta_data:
        # rerun gear study again later
        force_new_gear_study = True

    obd_gear_study = generate_gear_study_data(f"{temporary_file_base_directory}/{vin}/gear", vin)

    console.print(f"obd_gear_study data: {len(obd_gear_study)}")
    
    output_file_name = f"{temporary_file_base_directory}/Gear-Study/Gear-Study-{vin}.csv"
    Path(output_file_name).parent.mkdir(parents=True, exist_ok=True)
    save_gear_study_data_to_csv(vin, output_file_name, obd_gear_study, force_save=True)

    # laod csv file into dataframe
    console.print(f"Loading CSV file for {vehicles[vin]['name']} (Gear-Study-{fake_vin}.csv) into Data Frame")
    df = pd.read_csv(output_file_name, parse_dates=['iso_ts_pre', 'iso_ts_post', ])
    console.print(f"\t- rows loaded {df.shape[0]}")

    console.print(f"Gear Study Basic Statistics Report - {vehicles[vin]['name']}")
    generate_basic_stats_report(vin, df, gear_study_output_columns)

    gear_study_simple_histogram(vin, df, title=f"Gear-Study-1 {vehicles[vin]['name']} 'theta' Histogram", column="theta")
    gear_study_simple_histogram(vin, df, title=f"Gear-Study-1 {vehicles[vin]['name']} 'SPEED' Histogram", column="SPEED")
    gear_study_simple_histogram(vin, df, title=f"Gear-Study-1 {vehicles[vin]['name']} 'RPM' Histogram", column="RPM")
                                
    gear_study_hexagonal_binning_chart(vin, df)
    gear_study_rps_mps_kde_chart(vin, df)
    gear_study_kde_extrema_chart(vin, df)

    if force_new_gear_study:
        # rerunning gear study
        console.print("Forcing New Gear Study")
        obd_gear_study = generate_gear_study_data(f"{temporary_file_base_directory}/{vin}/gear", vin)
        save_gear_study_data_to_csv(vin, output_file_name, obd_gear_study, force_save=True)

        # relaod csv file into dataframe
        console.print(f"Reloading CSV file for {vehicles[vin]['name']} (Gear-Study-{fake_vin}.csv) into Data Frame")
        df = pd.read_csv(output_file_name, parse_dates=['iso_ts_pre', 'iso_ts_post', ])
        console.print(f"\t- rows loaded {df.shape[0]}")

        # rerun reports
        console.print(f"Gear Study Basic Statistics Report - {vehicles[vin]['name']}")
        generate_basic_stats_report(vin, df, gear_study_output_columns)

        gear_study_hexagonal_binning_chart(vin, df)
        gear_study_rps_mps_kde_chart(vin, df)
        gear_study_kde_extrema_chart(vin, df)

    gear_study_samples_by_closest_gear(vin, df)

    if isinstance(df_error_rates := error_rate_estimation(vin, df), pd.DataFrame):
        df = df_error_rates

        console.print(f"Gear Study Error Rates Report - {vehicles[vin]['name']}")
        generate_basic_stats_report(vin, df, ['distance_error', 'theta_error', ])

        output_file_name = f"{temporary_file_base_directory}/Gear-Study/Gear-Study-Error-Rates-{vin}.csv"
        console.print(f"Writing CSV file with Gear Study Error Rates for {vehicles[vin]['name']}")
        console.print(f"\t{output_file_name.replace(vin, fake_vin)}")
        df.to_csv(output_file_name, index=False)

        # the following function is not very useful
        # error_relationships(vin, df)

        theta_error_local_maximums(vin, df)

