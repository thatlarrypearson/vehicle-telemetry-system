# telemetry-analysis/telemetry_analysis/reports.py
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from pathlib import Path
from datetime import datetime, timedelta, timezone
from os import linesep as LF
from math import sqrt, atan2, tan, pi, radians, ceil
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.colors as mcolors

# pip install rich
from rich.console import Console
from rich.table import Table
from rich.jupyter import print

# import telemetry-analysis modules
from private.vehicles import vehicles
from telemetry_analysis.common import data_file_base_directory

# import external telemetry modules
from obd_log_to_csv.obd_log_evaluation import input_file as obd_log_evaluation_input_file
from obd_log_to_csv.obd_log_evaluation import rich_output as obd_log_evaluation_rich_output

console = Console()

def quotes_around_string(command:str)->str:
    single_quote = "'"
    return (single_quote + command + single_quote)

def obd_log_evaluation_report(vin, console, width=None, verbose=False):
    # Make a list of OBD data files.
    # directory where "*.json" OBD data files are held
    root = Path(data_file_base_directory)
    obd_files = [ str(rp) for rp in root.rglob(f"*{vin}*.json") if rp.is_file() ]

    console.print(f"OBD Log Evaluation Report: {vehicles[vin]['name']} OBD data file count {len(obd_files)}\n")

    # get dictionary of command statistics by command
    raw_data = obd_log_evaluation_input_file(obd_files)

    # filter out commands that have no valid results
    # filter out commands for command names that start with "PIDS_"
    for key, value in sorted(raw_data.items()):
        if value['count'] == value['no response'] or key.startswith('PIDS_'):
            raw_data.pop(key, None)

    # Pretty print output
    obd_log_evaluation_rich_output(
        raw_data,
        title=f"OBD Log Evaluation Report: {vehicles[vin]['name']}",
        width=width,
    )

    # for each vin, create a list of commands
    vin_commands = [ quotes_around_string(command) for command in sorted(raw_data) if '-' not in command]
    console.print(f"\n\nOBD Log Evaluation Report: {vehicles[vin]['name']} Command List")
    console.print(f"command_list = [{', '.join(vin_commands)}]")
    console.print("\n\n")

    return

def basic_stats_table_generator(vin:str, basic_statistics:dict):
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Column", justify='left')
    
    columns = [column for column in basic_statistics if column not in ['iso_ts_pre', 'iso_ts_post', ]]

    [table.add_column(vstat, justify='right') for vstat in basic_statistics[columns[0]]]

    for column in columns:
        argv = [column, ]

        for vstat in basic_statistics[columns[0]]:
            try:
                argv.append(f"{(basic_statistics[column][vstat]):.2f}")
            except Exception as e:
                console.print(f"{column}: {vstat}: {(basic_statistics[column][vstat])}")
                argv.append(f"{(basic_statistics[column][vstat])}")

        table.add_row(*argv)

    console.print(f"{'=' * 80}\n{vehicles[vin]['name']}")
    console.print(table)

def basic_statistics(vin:str, columns:list, df:pd.DataFrame)->dict:
    df_basic_statistics = {}

    for column in columns:
        df_basic_statistics[column] = {
            'max': (df[df[column].notnull()])[column].max(),
            'min': (df[df[column].notnull()])[column].min(),
            'mean': (df[df[column].notnull()])[column].mean(),
            'std': (df[df[column].notnull()])[column].std(),
            'not_null_rows': (df[df[column].notnull()])[column].shape[0],
            'null_rows': df.shape[0] - (df[df[column].notnull()])[column].shape[0],
        }

    return df_basic_statistics

def generate_basic_stats_report(vin:str, df:pd.DataFrame, columns:list):
    stat_columns = [column for column in columns if column not in ['iso_ts_pre', 'iso_ts_post', ]]

    basic_stats_table_generator(vin, basic_statistics(vin, stat_columns, df))

    return

def low_memory_basic_statistics(vin:str, columns:list, csv_file)->dict:
    df_basic_statistics = {}

    for column in columns:
        df = pd.read_csv(csv_file, usecols=[column, ])
        df_basic_statistics[column] = {
            'max': (df[df[column].notnull()])[column].max(),
            'min': (df[df[column].notnull()])[column].min(),
            'mean': (df[df[column].notnull()])[column].mean(),
            'std': (df[df[column].notnull()])[column].std(),
            'not_null_rows': (df[df[column].notnull()])[column].shape[0],
            'null_rows': df.shape[0] - (df[df[column].notnull()])[column].shape[0],
        }
        del df

    return df_basic_statistics

def generate_low_memory_basic_stats_report(vin:str, csv_file, columns:list):
    """
    Generate a basic statistics report with the same output as generate_basic_stats_report()
    but without loading the entire CSV file into a pandas dataframe first.
    """
    # remove datetime objects from column list
    stat_columns = [column for column in columns if column not in ['iso_ts_pre', 'iso_ts_post', ]]

    basic_stats_table_generator(vin, low_memory_basic_statistics(vin, stat_columns, csv_file))

    return


# https://matplotlib.org/stable/gallery/color/named_colors.html
def plot_color_table(colors=mcolors.TABLEAU_COLORS, ncols=4, sort_colors=True):

    cell_width = 212
    cell_height = 22
    swatch_width = 48
    margin = 12

    # Sort colors by hue, saturation, value and name.
    if sort_colors is True:
        names = sorted(
            colors, key=lambda c: tuple(mcolors.rgb_to_hsv(mcolors.to_rgb(c))))
    else:
        names = list(colors)

    n = len(names)
    nrows = ceil(n / ncols)

    width = cell_width * 4 + 2 * margin
    height = cell_height * nrows + 2 * margin
    dpi = 72

    fig, ax = plt.subplots(figsize=(width / dpi, height / dpi), dpi=dpi)
    fig.subplots_adjust(margin/width, margin/height,
                        (width-margin)/width, (height-margin)/height)
    ax.set_xlim(0, cell_width * 4)
    ax.set_ylim(cell_height * (nrows-0.5), -cell_height/2.)
    ax.yaxis.set_visible(False)
    ax.xaxis.set_visible(False)
    ax.set_axis_off()

    for i, name in enumerate(names):
        row = i % nrows
        col = i // nrows
        y = row * cell_height

        swatch_start_x = cell_width * col
        text_pos_x = cell_width * col + swatch_width + 7

        gear = i + 1
        short_name = (name.split(':'))[-1]
        ax.text(text_pos_x, y, f"gear {gear} color {short_name}", fontsize=14,
                horizontalalignment='left',
                verticalalignment='center')

        ax.add_patch(
            Rectangle(xy=(swatch_start_x, y-9), width=swatch_width,
                      height=18, facecolor=colors[name], edgecolor='0.7')
        )

    console.print("Gear Color Table")
    plt.show()
    plt.close()

shades = [  'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn'
         ]

def calculated_best_fit_gear_ratios(vin:str, vehicle:dict):
    # vehicle maybe updated but comes from  vehicle = vehicles[vin]
    console = Console()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column('VIN', justify='left')
    table.add_column('gear', justify='right')
    table.add_column('gear ratio', justify='right')
    table.add_column('theta', justify='right')
    table.add_column('1/tan(theta)', justify='right')
    table.add_column('a', justify='right')

    table.add_row(
            vehicles[vin]['name'],
            " ",
            " ",
            " ",
            " ",
            " "
    )
    for gear, gear_ratio in vehicle['forward_gear_ratios'].items():
        if 'theta' in vehicle and gear in vehicle['theta'] and vehicle['theta'][gear]:
            table.add_row(
                " ",
                f"{gear}",
                f"{gear_ratio:.4f}",
                f"{vehicle['theta'][gear]:6f}",
                f"{vehicle['one_over_tan_theta'][gear]:.6f}",
                f"{vehicle['a'][gear]:.6f}"
            )
        else:
            table.add_row(" ", f"{gear}", f"{gear_ratio:.4f}", "????", "????", "????")
    table.add_row(
            " ",
            " ",
            " ",
            " ",
            " ",
            " "
    )

    console.print(table)
    console.print("NOTE: column '1/tan(theta)' is the calculated best fit final gear ratio.")
    console.print("NOTE: column 'a' is the calculated best fit theta to gear ratio multiplier.")

    return
