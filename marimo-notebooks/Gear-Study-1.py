

import marimo

__generated_with = "0.13.0"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Gear Study - Gear Determination And Error Estimation

        This notebook uses statistical methods to determine the most likely gear ratios for each vehicle and stores the results in a file for later use.  Additionally, error calculations are used to estimate the total error between calculated gear ratios and:

        - gear ratios in vehicle documentation
        - angles calculated from SPEED and RPM pairs in records

        ## Gear Determination

        Vehicle gears are calculated from the following:

        1. Create new data fields from existing records

           a. Calculate acceleration as (SPEED<sub>i+1</sub> - SPEED<sub>i</sub>) / (iso_ts_pre<sub>i+1</sub> - iso_ts_pre<sub>i</sub>)

           b. Calculate revolutions per second (rps) as RPM / 60

           c. Calculate meters per second (mps) as SPEED * 0.44704

        2. Filter out all records with acceleration <= 0.0
        3. Filter out all records where SPEED <= 0 or SPEED > 130.0
        4. Filter out all records where RPM < 400.0 or > 5000.0
        5. Calculate theta<sub>i</sub>, the angle between vectors x<sub>rps</sub> and y<sub>mps</sub>, for each record using atan2(mps<sub>i</sub>, rps<sub>i</sub>)
        6. Generate Kernel Density Estimate (KDE) plot using Gaussian kernels
        7. Calculate the relative extrema of the KDE plot points
        8. Save the relative extrema for later use

        Limitations to this method affecting results include:

        - Too few valid samples of RPM/SPEED for each gear
        - Excessive transmission, clutch and/or torque converter slip in some or all gears

        For example, early results from 2023 Ford Maverick Lariat resulted in only 5 out of 8 gears identified.  It looked like the lower 3 gears were most affected by this limitation.

        ## Theta File - Machine Generated File Containing Gear Information For Each Vehicle


        ## Error Rate Estimation

        distance_error:
        - An error that measures the distance between the (rps, mps) point and the theta gear line.

        theta_error:
        - An error that is the difference between the theta gear line and the theta value calculated from the (rps, mps) poin:


        ## Conversion

        To convert this Jupyter Notebook to Markdown, run:

        - ```python -m nbconvert --to=markdown --output-dir=../markdown Gear-Study-1.ipynb```

        To convert this Jupyter Notebook to Python code, run:

        - ```python -m nbconvert --to=python --output-dir=src/ Gear-Study-1.ipynb```
        """
    )
    return


@app.cell
def _():
    import warnings
    warnings.simplefilter(action='ignore', category=FutureWarning)

    # import ipywidgets as widgets
    import marimo as mo
    from datetime import datetime
    import pytz
    import sys
    from pathlib import Path
    import numpy as np
    import pandas as pd
    from os import linesep as LF

    # pip install rich
    from rich.console import Console

    return Console, Path, mo, np, pd, pytz, sys


@app.cell
def _(Console, np, pd, pytz):
    # Set Raspberry Pi zimezone
    # See https://en.wikipedia.org/wiki/List_of_tz_database_time_zones  for list of timezone strings
    rpi_timezone = pytz.timezone('US/Central')
    telemetry_obd_sys_timezone = pytz.timezone('US/Central')

    np.set_printoptions(linewidth=180)
    pd.set_option("display.max.columns", None)

    console = Console(width=140)

    return (console,)


@app.cell
def _(Path, sys):
    # Enable imports from telemetry-analysis
    sys.path.append(str((Path.cwd()).parent))

    from private.vehicles import vehicles
    from telemetry_analysis.vins import fake_vin
    from telemetry_analysis.theta import read_theta_data_file, theta_file_name
    from telemetry_analysis.common import temporary_file_base_directory

    from telemetry_analysis.marimo_ui import select_vin_dialog
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
        gear_study_hexagonal_binning_chart,
        gear_study_rps_mps_kde_chart,
        gear_study_kde_extrema_chart,
        gear_study_samples_by_closest_gear,
        error_rate_estimation,
        theta_error_local_maximums,
    )
    from telemetry_analysis.data_files import obd_to_csv
    return (
        error_rate_estimation,
        fake_vin,
        gear_study_hexagonal_binning_chart,
        gear_study_input_columns,
        gear_study_kde_extrema_chart,
        gear_study_output_columns,
        gear_study_rps_mps_kde_chart,
        gear_study_samples_by_closest_gear,
        generate_basic_stats_report,
        generate_gear_study_data,
        obd_to_csv,
        read_theta_data_file,
        save_gear_study_data_to_csv,
        temporary_file_base_directory,
        theta_error_local_maximums,
        theta_file_name,
        vehicles,
    )


@app.cell
def _(mo, vehicles):

    vehicle_names = [vehicles[vin]['name'] for vin in vehicles]
    name_to_vin = {vehicle['name']: vin for vin, vehicle in vehicles.items()}

    selected_names = mo.ui.multiselect(
        options=vehicle_names,
        label="Select vehicles then click RUN to run.",
    )

    button = mo.ui.run_button(label="RUN")

    mo.hstack([selected_names, button])


    return button, name_to_vin, selected_names


@app.cell
def _(button, name_to_vin, selected_names):
    selected_names
    button
    # mo.hstack([selected_names, mo.md(f"Has value: {selected_names.value}")])
    print(f"{selected_names.value}")

    vins = [name_to_vin[selected_name] for selected_name in selected_names.value]

    return (vins,)


@app.cell
def _(read_theta_data_file, theta_file_name):
    _theta_data = read_theta_data_file(theta_file_name)
    return


@app.cell
def _(
    Path,
    console,
    error_rate_estimation,
    fake_vin,
    gear_study_hexagonal_binning_chart,
    gear_study_input_columns,
    gear_study_kde_extrema_chart,
    gear_study_output_columns,
    gear_study_rps_mps_kde_chart,
    gear_study_samples_by_closest_gear,
    generate_basic_stats_report,
    generate_gear_study_data,
    obd_to_csv,
    pd,
    read_theta_data_file,
    save_gear_study_data_to_csv,
    temporary_file_base_directory,
    theta_error_local_maximums,
    theta_file_name,
    vehicles,
    vins,
):
    for vin in vins:
        obd_to_csv(vin, gear_study_input_columns)
        force_new_gear_study = False
        if not (_theta_data := read_theta_data_file(theta_file_name)) or vin not in _theta_data:
            force_new_gear_study = True
        obd_gear_study = generate_gear_study_data(f'{temporary_file_base_directory}/{vin}/gear', vin)
        console.print(f'obd_gear_study data: {len(obd_gear_study)}')
        output_file_name = f'{temporary_file_base_directory}/Gear-Study/Gear-Study-{vin}.csv'
        Path(output_file_name).parent.mkdir(parents=True, exist_ok=True)
        save_gear_study_data_to_csv(vin, output_file_name, obd_gear_study, force_save=True)
        console.print(f'Loading CSV file for {vehicles[vin]['name']} (Gear-Study-{fake_vin}.csv) into Data Frame')
        df = pd.read_csv(output_file_name, parse_dates=['iso_ts_pre', 'iso_ts_post'])
        console.print(f'\t- rows loaded {df.shape[0]}')
        console.print(f'Gear Study Basic Statistics Report - {vehicles[vin]['name']}')
        generate_basic_stats_report(vin, df, gear_study_output_columns)
        gear_study_hexagonal_binning_chart(vin, df)
        gear_study_rps_mps_kde_chart(vin, df)
        gear_study_kde_extrema_chart(vin, df)
        if force_new_gear_study:
            console.print('Forcing New Gear Study')
            obd_gear_study = generate_gear_study_data(f'{temporary_file_base_directory}/{vin}/gear', vin)
            save_gear_study_data_to_csv(vin, output_file_name, obd_gear_study, force_save=True)
            console.print(f'Reloading CSV file for {vehicles[vin]['name']} (Gear-Study-{fake_vin}.csv) into Data Frame')
            df = pd.read_csv(output_file_name, parse_dates=['iso_ts_pre', 'iso_ts_post'])
            console.print(f'\t- rows loaded {df.shape[0]}')
            console.print(f'Gear Study Basic Statistics Report - {vehicles[vin]['name']}')
            generate_basic_stats_report(vin, df, gear_study_output_columns)
            gear_study_hexagonal_binning_chart(vin, df)
            gear_study_rps_mps_kde_chart(vin, df)
            gear_study_kde_extrema_chart(vin, df)
        gear_study_samples_by_closest_gear(vin, df)

        if isinstance((df_error_rates := error_rate_estimation(vin, df)), pd.DataFrame):
            df = df_error_rates
            console.print(f'Gear Study Error Rates Report - {vehicles[vin]['name']}')
            generate_basic_stats_report(vin, df, ['distance_error', 'theta_error'])
            output_file_name = f'{temporary_file_base_directory}/Gear-Study/Gear-Study-Error-Rates-{vin}.csv'
            console.print(f'Writing CSV file with Gear Study Error Rates for {vehicles[vin]['name']}')
            console.print(f'\t{output_file_name}')
            df.to_csv(output_file_name, index=False)
            theta_error_local_maximums(vin, df)

    return


if __name__ == "__main__":
    app.run()
