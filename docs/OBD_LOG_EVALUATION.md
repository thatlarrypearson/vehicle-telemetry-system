# OBD Log Evaluation

A vehicle's ```obd_logger``` configuration file should not contain unrecognizable OBD commands.  The ```obd_log_evaluation``` tool identifies non-responsive OBD commands.  It also identifies intermittant OBD commands possibly indicating the need to increase ```--timeout``` with ```telemetry_obd.obd_command_tester``` and ```telemetry_obd.obd_logger``` programs.

- An intermittant OBD command sometimes returns a valid value and sometimes returns ```no response```.

## Features

- Identifies unsupported OBD commands
- Identifies intermittant OBD commands
- Provides basic data types for each column (string, integer, float, list)
- When available, provides units of measure for numeric columns
- OBD commands returning lists of values are handled as a collection of individual commands
  - When subfield names are available, command names are modified for each element in the list
    - The command name shown in the report output is hyphenated with the subfield name
  - When subfield names are not available, subfields are identified by their number in the list
    - The command name shown in the report output is hyphenated with the subfield position in the list
- See [Examples](#examples) for more

## Command Line Usage

```bash
python3.10 -m obd_log_to_csv.obd_log_evaluation --help
usage: obd_log_evaluation [-h] [--verbose] [--csv] files [files ...]

OBD Log Evaluation performs simple analysis on telemetry_obd.obd_logger and telemetry_obd.obd_command_tester output
files. The analysis is oriented toward validating obd_logger config files and providing units for each OBD command.

positional arguments:
  files       telemetry_obd generated data files separated by spaces. Data file names can include full or relative
              paths.

optional arguments:
  -h, --help  show this help message and exit
  --verbose   Turn verbose output on. Default is off.
  --csv       Output CSV on stdout. Default is to rich table print on stdout.
```

## Jupyter Notebook Usage

The following can be included in Jupyter notebooks and python programs.  The only **required** parameter to ```main``` in ```obd_log_to_csv.obd_log_evaluation``` is the ```json_input_files``` parameter.  The other paramters default the same as the command line options.

```python
from obd_log_to_csv.obd_log_evaluation import main as obd_log_evaluation_main
from os import listdir

# file names are based on vehicle identification number or vin
vin = "the VIN number associated with this particular vehicle goes in here"

# directory where "*.json" data files are held
dname = f"../data/{vin}"

files = [f"{dname}/{fname}" for fname in listdir(dname) if fname.endswith(".json")]

obd_log_evaluation_main(json_input_files=files, verbose=False, csv_output=False) 
```

By default, [```rich```](https://rich.readthedocs.io/en/stable/introduction.html) will be used to display the results in table form.

![Jupyter Notebook Example](JupyterNotebook-obd_log_evaluation.jpg)

## Examples

### ```obd_log_evaluation``` Processing Sample Output From Frematics OBD-II Emulator

#### Input

- Sample input collected during testing.
- Collection program interrupted (```<CTRL-C>```) after 26 full test cycles.
- See [```telemetry_obd.obd_command_tester```](https://github.com/thatlarrypearson/telemetry-obd).

```python
# Command Tester Collection Program
python3.10 -m telemetry_obd.obd_command_tester --cycles 100
```

#### Output

- OBD log evaluation program runs on collected input data.
- Output in CSV format for importation into applications
  - [Microsoft Visual Studio Code](https://code.visualstudio.com/)
  - [CSV to Markdown Table](https://marketplace.visualstudio.com/items?itemName=Marchiore.csvtomarkdown)
  - [Microsoft Excel](https://www.microsoft.com/en-us/microsoft-365/excel)
- Output examples in table format
  - [Frematics OBD Emulator](OBD_LOG_EVALUATION-FrematicsEmulatorOutout.md)
  - [2013 Jeep Wrangler Rubicon](OBD_LOG_EVALUATION-2013JeepWranglerRubicon.md)
  - [2017 Ford F-450 Diesel Dually 4 Door Long Bed](OBD_LOG_EVALUATION-2017FordF450.md)
  - [2019 Ford EcoSport](OBD_LOG_EVALUATION-2019FordEcoSport.md)
  - [2021 Toyota Sienna LE](OBD_LOG_EVALUATION-2021ToyotaSiennaLE.md)

```python
python3.10 -m obd_log_to_csv.obd_log_evaluation --csv ./TESTVIN012345678-TEST-20211127145538.json
```

### Generating OBD Command Lists

#### Complete Command List

```bash
python3.10 -m obd_log_to_csv.obd_log_evaluation --csv "${VIN}-TEST-${YYYYMMDDhhmmss}-utc.json | \
awk -F "\"*,\"*" '{print $1}' | \
grep -v command | grep -v '-'
```

#### Valid Command List

```bash
python3.10 -m obd_log_to_csv.obd_log_evaluation --csv "${VIN}-TEST-${YYYYMMDDhhmmss}-utc.json | \
awk -F ',' '// { if ($4 != $5) {print $1}}' \
grep -v command | grep -v '-'
```

#### Invalid Command List

```bash
python3.10 -m obd_log_to_csv.obd_log_evaluation --csv "${VIN}-TEST-${YYYYMMDDhhmmss}-utc.json | \
awk -F ',' '// { if ($4 == $5) {print $1}}' \
grep -v command | grep -v '-'
```

## Related

Here are some related projects

- [telemetry-obd](https://github.com/thatlarrypearson/telemetry-obd): Telemetry OBDII (Onboard Diagnostic Data 2) Logger
  - ```telemetry_obd.obd_logger```
  - ```telemetry_obd.obd_command_tester```
- [telemetry-django-obd](https://github.com/thatlarrypearson/telemetry-django-obd): Django database OBD/ECU data loader

## License

[MIT](../LICENSE.md)
