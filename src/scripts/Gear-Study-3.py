# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Gear Study - Exploring Closest Gear Theta Errors as a Function of RPM and Speed
#

# %%
# Increase Jupyter Notebook display width to be the screen width
from IPython.display import display, HTML
display(HTML("<style>.container { width:100% !important; }</style>"))
display(HTML("<style>.output_result { max-width:100% !important; }</style>"))

# Enable imports relative to notebook
# https://mattoppenheim.com/2018/03/16/relative-imports-in-jupyter-notebooks/
# python -m pip install nbimporter
# conda install -c akode nbimporter
import nbimporter

# %%
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
from rich.pretty import pprint

# %%
# Set Raspberry Pi zimezone
# See https://en.wikipedia.org/wiki/List_of_tz_database_time_zones  for list of timezone strings
rpi_timezone = pytz.timezone('US/Central')
telemetry_obd_sys_timezone = pytz.timezone('US/Central')

np.set_printoptions(linewidth=180)
pd.set_option("display.max.columns", None)

console = Console(width=140)

# %%
# Enable imports from telemetry-analysis
sys.path.append(str((Path.cwd()).parent))

from telemetry_analysis.theta import (
    theta_file_name,
    read_theta_data_file,
)
from telemetry_analysis.gears import (
    column_range_study,
)
from telemetry_analysis.widgets import select_vin_dialog
from telemetry_analysis.vins import (
    fake_vin,
    get_vin_from_vehicle_name,
)
from telemetry_analysis.common import temporary_file_base_directory
from private.vehicles import vehicles

# %%
vins = select_vin_dialog(verbose=True)

vehicle_names = [vehicles[vin]['name'] for vin in vins]

print(f"Data available as of {datetime.now()} from data sets: \n  - {(LF + '  - ').join(vehicle_names)}")

# %%
for vin in vins:
    # laod csv file into dataframe
    console.print(f"Loading CSV file for {vehicles[vin]['name']} (Gear-Study-{fake_vin}.csv) into Data Frame")
    df = pd.read_csv(
        f"{temporary_file_base_directory}/Gear-Study/Gear-Study-Error-Rates-{vin}.csv",
        parse_dates=['iso_ts_pre', 'iso_ts_post', ]
    )
    console.print(f"\t- rows loaded {df.shape[0]}")
    
    crs_results = column_range_study(df, 'SPEED')
    pprint(crs_results)
