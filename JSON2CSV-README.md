# Telemetry OBD Data To CSV File

Convert [Telemetry OBD Logger](https://github.com/thatlarrypearson/telemetry-obd) output to CSV format files suitable for importation into Python [Pandas](https://pandas.pydata.org/)  ```dataframe``` using the ```from_csv()``` method.

## Features

- Intelligently aggregates multiple vehicle OBD command responses into a record format for importing into common data analysis libraries such as Python Pandas
- Comes with Python Pandas data analysis examples
- Runs in Jupyter Notebooks and can run as a function in Python programs
- Comes with post processing programs that add in
  - rates of change in numeric columns - e.g. ```SPEED``` can become ```ACCELERATION```
  - ratios in pairs of columns - e.g. ```RPM/SPEED``` provides a current gear ratio
- Uses Python 3.8 or newer (Testing done with Python 3.11)
- Runs on Windows, Mac and Linux

When aggregating multiple OBD commands into records, ```obd_log_to_csv``` considers a record complete when it finds another entry for an OBD command already placed into the record.  OBD commands not found in the input by the time the record is complete are set to ```None``` in Python and that is translated to missing values in the CSV file.  In Pandas, such missing values get changed to ```NaN``` or Not a Number.

Time stamps are handled in the following way:

- ```iso_ts_pre```, the ISO format time stamp from right before an OBD command request is made to the vehicle, is set by the first OBD command included in the output record.

- ```iso_ts_post```, the ISO format time stamp from right after an OBD command response is received from the vehicle, is set by the last OBD command included in the output record.

- ```duration```, the number of seconds between ```iso_ts_pre``` and ```iso_ts_post```.

## ```obd_log_to_csv.obd_log_to_csv``` Usage

Given vehicle telemetry data files created by ```telemetry_obd.obd_logger```, create ```CSV``` files suitable for importation into spreadsheets (i.e. Microsoft Excel) or Python Pandas ecosystem components.

```bash
$ python3.11 -m obd_log_to_csv.obd_log_to_csv --help
usage: obd_log_to_csv [-h] [--commands COMMANDS] [--csv CSV] [--no_header]
                      [--verbose]
                      files [files ...]

Telemetry OBD Log To CSV

positional arguments:
  files                telemetry_obd generated data files separated by spaces.
                       Data file names can include full or relative paths.

optional arguments:
  -h, --help           show this help message and exit
  --commands COMMANDS  Command name list to include in CSV output record
                       generation. Comma separated list. e.g.
                       "SPEED,RPM,FUEL_RATE". In the JSON input,
                       "command_name" labelled items will be used. No default
                       value provided.
  --csv CSV            CSV output file. File can be either a full or relative
                       path name. If the file already exists, it will be
                       overwritten. Defaults to standard output (stdout)
                       instead of file.
  --no_header          CSV output file will NOT have a column name header
                       record. Default is False. (That is, a header will be
                       produced by default.)
  --verbose            Turn verbose output on. Default is off.

$
```

## ```obd_log_to_csv.obd_log_to_csv``` Command Line Usage Examples

The following example assumes data was collected using ```telemetry_obd.obd_logger``` and that the collected vehicle data is in the local directory ```data/{VehicleIdentificationNumber-VIN}```.  File names in the vehicle data directory will be in the form ```{VehicleIdentificationNumber-VIN}-{YYYYMMDDhhmmss}-utc.json``` where

- ```{VehicleIdentificationNumber-VIN}``` is the vehicle's VIN as collected by ```telemetry_obd.obd_logger```
- ```{YYYMMDDhhmmss}``` represents the date/time the data file was initially created.

On Linux/Mac, convert ```obd_logger``` generated data to Pandas compatible CSV format, the following command converts all of the data files in a vehicle's data directory into a single CSV format file.

```bash
export VIN="FT8W4DT5HED00000"
python3.11 -m obd_log_to_csv.obd_log_to_csv \
        --csv="${VIN}.csv" \
        --commands=ACCELERATOR_POS_D,ACCELERATOR_POS_E,AMBIANT_AIR_TEMP,BAROMETRIC_PRESSURE,COMMANDED_EGR,CONTROL_MODULE_VOLTAGE,COOLANT_TEMP,DISTANCE_SINCE_DTC_CLEAR,DISTANCE_W_MIL,ENGINE_LOAD,FUEL_LEVEL,FUEL_INJECT_TIMING,FUEL_RAIL_PRESSURE_ABS,FUEL_RAIL_PRESSURE_DIRECT,INTAKE_PRESSURE,INTAKE_TEMP,MAF,OIL_TEMP,RELATIVE_ACCEL_POS,RUN_TIME \
        data/"${VIN}"/*.json
```

In the above example, ```--commands={List-Of-OBD-Commands``` is all on a single line.  The ```\``` (back-slashes) at the ends of lines tell the ```bash``` (and other shells) interpreter to treat the following line as part of the current line.  The back-slashes were added to separate individual options/elements with the goal of improving readability.

Similarly, on Windows using PowerShell, the following will also process a group of files for the same vehicle assuming the same directory layout.

```powershell
$VIN ="FT8W4DT5HED00000"
python3.11 -m obd_log_to_csv.obd_log_to_csv --csv=${VIN}.csv --commands=RPM,SPEED,FUEL_RATE data/${VIN}/*.json
```

### ```ValueError: dict contains fields not in fieldnames```

If you get a value error in the Python ```csv``` module as shown below, then you must be working with commands that return either a list of results or a dictionary of results.  Two solutions:

- Run [```obd_log_to_csv.obd_log_evaluation```](docs/OBD_LOG_EVALUATION.md) to get a breakdown of all commands contained in your data.  Next, include only commands that show a data type in the "Data Type" column.  E.g. ```WTHR_rapid_wind``` doesn't show a data type (base command name) but ```WTHR_rapid_wind-wind_speed``` (base command dash sub command) does.
- Look at the ```fieldnames``` listed in the ```ValueError``` message.  Add these field names to your ```--commands``` list of commands.

```bash
lbp@telemetry4:telemetry-data/data/telemetry2$ python3.11 -m obd_log_to_csv.obd_log_to_csv --commands "WTHR_obs_st,WTHR_rapid_wind" telemetry2-000
0000076-wthr-0000000070.json
WTHR_obs_st,WTHR_rapid_wind,iso_ts_pre,iso_ts_post,duration
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/home/lbp/.local/lib/python3.11/site-packages/obd_log_to_csv/obd_log_to_csv.py", line 236, in <module>
    main()
  File "/home/lbp/.local/lib/python3.11/site-packages/obd_log_to_csv/obd_log_to_csv.py", line 233, in main
    cycle_through_input_files(json_input_files, commands, header, stdout, verbose=verbose)
  File "/home/lbp/.local/lib/python3.11/site-packages/obd_log_to_csv/obd_log_to_csv.py", line 153, in cycle_through_input_files
    input_file(json_input, commands, csv_output_file,
  File "/home/lbp/.local/lib/python3.11/site-packages/obd_log_to_csv/obd_log_to_csv.py", line 110, in input_file
    writer.writerow(output_record)
  File "/home/lbp/.local/lib/python3.11/csv.py", line 154, in writerow
    return self.writer.writerow(self._dict_to_list(rowdict))
                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/lbp/.local/lib/python3.11/csv.py", line 149, in _dict_to_list
    raise ValueError("dict contains fields not in fieldnames: "
ValueError: dict contains fields not in fieldnames: 'WTHR_rapid_wind-wind_speed', 'WTHR_rapid_wind-time_epoch', 'WTHR_rapid_wind-wind_direction'
lbp@telemetry4:telemetry-data/data/telemetry2$
```

## ```obd_log_to_csv.obd_log_to_csv``` Jupyter Notebook Usage Example

```python
from obd_log_to_csv.obd_log_to_csv import main as obd_log_to_csv_main

obd_log_to_csv_main(
  json_input_files=["telemetry-data/data/telemetry2/telemetry2-0000000076-obd-<vin>-0000000041.json", ],
  csv_output_file_name="telemetry2-0000000076-obd-<vin>-0000000041.csv",
  commands=['SPEED', 'RPM', 'FUEL_RATE_2', 'WTHR_rapid_wind-wind_speed',
  'WTHR_rapid_wind-time_epoch', 'WTHR_rapid_wind-wind_direction']
)
```

## Installation

Clone this repository from `git` and install using Python pip where the Python version is 3.11 or higher.

In some newer version of Python, ```pip``` is handled differently and not necessarily better which is why the two following ```pip``` installations have the command line options they do.

```bash
git clone https://github.com/thatlarrypearson/telemetry-obd-log-to-csv.git
python3.11 --version

# Python pip Install Support
python3.11 -m pip install --upgrade --force-reinstall --user pip
python3.11 -m pip install --upgrade --force-reinstall --user wheel setuptools markdown build
cd telemetry-obd-log-to-csv
python3.11 -m build
python3.11 -m pip install --user dist/telemetry_obd_log_to_csv-0.3.3-py3-none-any.whl
```

## Documentation

This [README](./README.md) has other companion documents as shown below in [OBD Log Evaluation](#OBD-LOG-EVALUATION), [Post Processing](#Post-Processing) and [Data Analysis](#Data-Analysis).

### OBD Log Evaluation

As an aid to determining which OBD commands should be in ```obd_logger``` configuration files, [```obd_log_evaluation```](./docs/OBD_LOG_EVALUATION.md) analyses output from  ```telemetry_obd.obd_command_tester``` and ```telemetry_obd.obd_logger```.

### JSON Data Integrator

The [JSON Data Integrator](./docs/JSON_DATA_INTEGRATOR.md) integrates telemetry JSON data from multiple sources into a single data file from multiple data sources:

- telemetry_obd.obd_logger
- gps_logger.gps_logger
- wthr_logger.wthr_logger
- imu_logger.imu_logger
- other sources conforming to [Telemetry OBD Logger Output Data Files](https://github.com/thatlarrypearson/telemetry-obd#telemetry-obd-logger-output-data-files)

### Post Processing

Additional data manipulation tools are available as part of this library and are described in [CSV File Post Processing](./docs/POST_PROCESSING.md).

### Data Analysis

Simple analysis tools based on [Python Pandas](https://pandas.pydata.org/) are shown in [CSV File Data Analysis](./docs/DATA_ANALYSIS.md).

## Example Programs

The repository's ```examples``` directory contains example programs showing how to extend and customize capabilities for different types of analysis.  The examples break down into two families of example programs:

- [Distance](docs/EXAMPLES-distance.md):
  Two methods for calculating distance travelled when target vehicle doesn't support ```ODOMETER``` OBD command.

- [Initial Data Analysis](docs/EXAMPLES-data_analysis.md):
  Simple data analysis creating artifacts assisting data analysts in identifying important or unexpected data relationships.

## Known Problems

Vehicle Identification Number (VIN) is not always correct.

- 2013 Jeep Wrangler Rubicon is missing leading ```1``` digit/letter
- 2017 Ford F-450 VIN is missing leading ```1``` digit/letter
- 2021 Toyota Sienna Hybrid LE is missing the trailing ```0``` digit/letter while another 2021 Sienna Hybrid LE (VIN: 5TDKRKEC6MS043967) was not missing any digits or letters.

## Related

Here are some related projects

- [telemetry-obd](https://github.com/thatlarrypearson/telemetry-obd): Telemetry OBDII (Onboard Diagnostic Data 2) Logger
- [telemetry-django-obd](https://github.com/thatlarrypearson/telemetry-django-obd): Django database OBD/ECU data loader

## License

[MIT](./LICENSE.md)
