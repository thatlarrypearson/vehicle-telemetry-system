#!/usr/bin/env python
# coding: utf-8

# # Gear Study - Vehicle Route Videos Showing SPEED, RPM and Gear Changes
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

from telemetry_analysis.theta import (
    theta_file_name,
    read_theta_data_file,
)
from telemetry_analysis.gears import (
    route_report,
    route_by_name_table,
    generate_images_for_video,
)
from telemetry_analysis.widgets import select_vin_dialog
from telemetry_analysis.vins import (
    fake_vin,
    get_vin_from_vehicle_name,
)
from telemetry_analysis.common import temporary_file_base_directory
from private.vehicles import vehicles


# In[5]:


vins = select_vin_dialog(verbose=True)

vehicle_names = [vehicles[vin]['name'] for vin in vins]

print(f"Data available as of {datetime.now()} from data sets: \n  - {(LF + '  - ').join(vehicle_names)}")


# In[6]:


for vin in vins:
    # laod csv file into dataframe
    console.print(f"Loading CSV file for {vehicles[vin]['name']} (Gear-Study-{fake_vin}.csv) into Data Frame")
    df = pd.read_csv(
        f"{temporary_file_base_directory}/Gear-Study/Gear-Study-Error-Rates-{vin}.csv",
        parse_dates=['iso_ts_pre', 'iso_ts_post', ]
    )
    console.print(f"\t- rows loaded {df.shape[0]}")
    
    route_report(vin, df)
    route_by_name_table(vin, df)


# In[7]:


route_by_name = [
    # ('2023 Ford Maverick Lariat', 7),
    #
    # put the vehicle and route pairs desired into this array
    # ('2013 Jeep Wrangler Rubicon 2 Door', 142),   # count: 6841
    # ('2019 Ford EcoSport Platinum', 277), # count: 12823
    # ('2017 Ford F-450 Platinum', 54),     # count: 10248
    # ('2023 Ford Maverick Lariat', 13),
    # ('2023 Ford Maverick Lariat', 21),    # count: 92
    # ('2023 Ford Maverick Lariat', 24),    # count: 1850
    # ('2023 Ford Maverick Lariat', 242),   # count: 671
    # ('2023 Ford Maverick Lariat', 243),   # count: 818
    ('2023 Ford Maverick Lariat', 851),   # count: 32499
]


# In[ ]:


for name, route in route_by_name:
    vin = get_vin_from_vehicle_name(name)

    console.print(f"Loading CSV file for {vehicles[vin]['name']} (Gear-Study-Error-Rates-{fake_vin}.csv) into Data Frame")
    df = pd.read_csv(f"{temporary_file_base_directory}/Gear-Study/Gear-Study-Error-Rates-{vin}.csv", parse_dates=['iso_ts_pre', 'iso_ts_post', ])
    console.print(f"\t- rows loaded {df.shape[0]}")

    # reindex df
    df.reset_index(drop=True, inplace=True, names='i')

    # set create_video=True when your system (not Windows) is able to run ffmpeg
    console.print(f"Generating Images/Video For Vehicle {name} And Route {route}")
    try:
        generate_images_for_video(name, route, df, create_video=False, video_frame_rate=30)
    except Exception as e:
        console.print(f"If this is a memory error in matplotlib/seaborn, just restart.\n\n{e}")


# In[ ]:





# In[ ]:




