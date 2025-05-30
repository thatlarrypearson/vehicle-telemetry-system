#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# # Fuel Study - Identifying Factors Related To Fuel Usage
# 
# This notebook uses statistical methods to determine fuel usage and the factors contributing to fuel usage.
# 
# 
# ## Fuel Usage Determiniation
# 
# 
# 
# Limitations to these methods affecting results include:
# 
# 
# 
# ## Error Rate Estimation
# 
# 
# 
# ## Conversion
# 
# To convert this Jupyter Notebook to Markdown, run:
# 
# - ```python -m nbconvert --to=markdown --output-dir=../markdown Fuel-Study-1.ipynb```
# 
# To convert this Jupyter Notebook to Python code, run:
# 
# - ```python -m nbconvert --to=python --output-dir=src/ Fuel-Study-1.ipynb```
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
sys.path.append(str((Path.cwd()).parent))

from private.vehicles import vehicles
from telemetry_analysis.vins import fake_vin
from telemetry_analysis.theta import read_theta_data_file, theta_file_name
from telemetry_analysis.common import (
    temporary_file_base_directory,
    get_column_names_in_csv_file,
)

from obd_log_to_csv.vin_data_integrator import main as integrator

from telemetry_analysis.widgets import select_vin_dialog
from telemetry_analysis.reports import (
    obd_log_evaluation_report,
    basic_statistics,
    generate_basic_stats_report,
    generate_low_memory_basic_stats_report,
    plot_color_table,
)
from telemetry_analysis.data_files import (
    obd_to_csv,
    integrated_to_csv,
)
from telemetry_analysis.fuel import (
    save_fuel_study_data_to_csv,
    generate_fuel_study_data,
    fuel_study_input_columns,
    fuel_study_output_columns,
)


# In[5]:


# colors used in fuel color lines
plot_color_table()


# In[6]:


vins = select_vin_dialog(verbose=True)

vehicle_names = [vehicles[vin]['name'] for vin in vins]

print(f"Data available as of {datetime.now()} from data sets: \n  - {(LF + '  - ').join(vehicle_names)}")


# In[7]:


# Integrate OBD, IMU, GPS and Weather JSON data into 'integrated' JSON data
# Write obd_fuel_study_data[vin] to csv files
########################################################

for vin in vins:
    #   - Each vehicle file is written to a temporary csv file using the same basename by obd_log_to_csv_main()
    integrator(vin=vin, skip=True, verbose=False)
    #   - Each temporary vehicle file gets processed and added to obd_files with a unique route number by generate_fuel_study_data()
    integrated_to_csv(vin, fuel_study_input_columns, study="fuel", verbose=False)

    # Fuel Study Data is created in this step
    output_file = Path(f"{temporary_file_base_directory}/Fuel-Study/Fuel-Study-{vin}.csv")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    csv_file_dir = f"{temporary_file_base_directory}/{vin}/fuel"
    row_count = generate_fuel_study_data(vin, output_file, csv_file_dir, force_save=True, verbose=False)
    
    # laod csv file into dataframe
    console.print(f"Loading CSV file for {vehicles[vin]['name']} ({output_file.name.replace(vin,fake_vin)}) into Data Frame\n")

    # EcoSport Data - 69 columns X 68,230,747 rows = 35 GigaBytes in RAM memory allocation fails on 64.0 GB (63.6 GB usable) RAM Intel 686 CPU
    # Jeep Data     - 69 columns x 78,311,620 rows works on same computer
    # F-450         - 69 columns x  4,139,019 rows works on same computer
    # Maverick      - 69 columns x 20,943,444 rows works on same computer
    column_names, record_count = get_column_names_in_csv_file(output_file)

    console.print(f"CSV file ({output_file.name.replace(vin,fake_vin)}) for {vehicles[vin]['name']}  has:")
    console.print(f"\t- {len(column_names)} columns")
    console.print(f"\t- {column_names}")
    console.print(f"\t- {record_count} records\n")



# In[8]:


for vin in vins:
    # Generate Fuel Study Basic Statistics Report Using Full Dataset
    output_file = Path(f"{temporary_file_base_directory}/Fuel-Study/Fuel-Study-{vin}.csv")

    console.print(f"Low Memory Version: Fuel Study Basic Statistics Report - {vehicles[vin]['name']}")
    generate_low_memory_basic_stats_report(vin, output_file, fuel_study_output_columns)


# In[ ]:




