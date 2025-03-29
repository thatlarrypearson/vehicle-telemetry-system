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
# # Gear Study - Per Vehicle OBD Log Evaluation Reports
#
# OBD Log Evaluation Reports are generated using all available ```telemetry-obd``` generated data files.  Example report output can be found in ```telemetry-analysis/markdown/Gear-Study-0.md```.
#
# To minimize the amount of noise in the reports, the following data items are automatically filtered from the report output:
#
# - Commands starting with ```PIDS_```
# - Commands without any valid responses
#
# The filtering ensures that only useful data is included in each report.
#
# To convert this Jupyter Notebook to Markdown, run:
#
# - ```python -m nbconvert --to=markdown --output-dir=../markdown Gear-Study-0.ipynb```
#
# To convert this Jupyter Notebook to Python code, run:
#
# - ```python -m nbconvert --to=python --output-dir=src/ Gear-Study-0.ipynb```
#
# At the end of this Notebook, there is a manual step to perform.

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
import ipywidgets as widgets
from datetime import datetime, timedelta, timezone
import pytz
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from os import linesep as LF

# pip install rich
from rich.console import Console

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

from private.vehicles import vehicles
from telemetry_analysis.widgets import select_vin_dialog
from telemetry_analysis.reports import obd_log_evaluation_report

# %%
vins = select_vin_dialog(title="Generate Reports for Checked Vehicles", verbose=True)

vehicle_names = [vehicles[vin]['name'] for vin in vins]

print(f"Data available as of {datetime.now()} from data sets: \n  - {(LF + '  - ').join(vehicle_names)}")

# %%
for vin in vins:
    obd_log_evaluation_report(vin, console, width=140)

# %% [markdown]
# # Manual Task Using Data Provided Above
#
# Examine each command in each vehicle's "OBD Log Evaluation Report: <vehicle[vin]>" to determine which of these commands should be included in the ```vehicles[vin]['command_list']``` list found in ```telemetry-analysis/private/vehicles.py```.
#
# Consider this the first cut toward coming up with a working list of OBD commands to include in data analysis.

# %%
