# Vehicle Telemetry System

System for collecting and processing motor vehicle data using included sensor modules.

## **Under Construction**

The following repositories have been combined to create this repository:

- **Vehicle Sensor Modules**
  - [engine](https://github.com/thatlarrypearson/telemetry-obd) (OBD)
  - [location](https://github.com/thatlarrypearson/telemetry-gps) (GPS)
  - [motion](https://github.com/thatlarrypearson/telemetry-imu) (IMU)
  - [weather](https://github.com/thatlarrypearson/telemetry-wthr) (WTHR)
  - [trailer](https://github.com/thatlarrypearson/telemetry-trailer-connector) (TRLR)
- **Common Functions**
  - [Common utilities](https://github.com/thatlarrypearson/telemetry-utility) (UTILITY)
  - [Audit Capabilities](https://github.com/thatlarrypearson/telemetry-counter) (COUNTER)
- **Data Management Analysis**
  - [Combine JSON records into CSV records](https://github.com/thatlarrypearson/telemetry-obd-log-to-csv) (JSON2CSV)
  - [Notebook Data Analysis](https://github.com/thatlarrypearson/telemetry-analysis) (ANALYSIS)

Moving forward, module development will be in this repository.  Development in the original repositories has stopped.

## Project Summary and Purpose

I started this project thinking that I was better at selecting transmission gears for improved fuel economy than the engine/transmission controller is.  Now I'm not so sure.  But the gear selection hypothesis lead to other questions that look suspiciously like functional requirements.

As a driver, I want to know how my driving choices affect fuel use so that I can make rational tradeoffs between fuel use and:

- transmission gear selection
- drive time
- wind and temperature
- elevation
- route
- speed
- cargo/loading
- vehicle (and trailer) modifications
- traffic congestion (lights and idling)
- acceleration rates

The first step involved creating a data collection environment and then adding sensors to collect the data.  After collecting hours of driving data, data analysis work began to:

- identify software issues
- (in)validate assumptions
  - fuel use spikes in Diesel engines using DEF for emissions control
  - gear identification using Kernel Density Estimation (KDE) extrema
  - error calculations on identified gears
- validate data by comparing similar data from different sources
  - GPS distance traveled versus odometer or speed times time
- identify current gear

Additionally, work has begun to estimate gallons of fuel remaining in fuel tank based on the percentage of fuel the engine controller thinks is still in the tank.  It is unlikely that the percentage provided through the OBD interface is linear with respect to the actual fuel use compared to the actual volume of fuel held in the tank.  Temperature also affects fuel volume and this needs to be taken into account.

![Context Diagram](./docs/VTS-Summary-ContextDiagram.jpg)

## Python Project Software Build and Installation

For this project, [```uv```](https://github.com/astral-sh/uv) is used to

- Install Python
- Create and manage the virtual Python runtime environment
- Create a Python package and install it into the virtual environment
- Run specific Python modules installed in the virtual environment

Install ```git``` before cloning the software from this [github repository](https://github.com/thatlarrypearson/vehicle-telemetry-system).  For a Windows or Mac ```git``` installation, go to [Microsoft Learn - Install and set up Git](https://learn.microsoft.com/en-us/devops/develop/git/install-and-set-up-git) and follow their instructions.

Use the ```apt``` package management system to install ```git``` on Debian Linux variants including Raspberry Pi, Ubuntu and Linux Mint.

```bash
apt install git
```

For Windows (and Mac) users, [GitHub Desktop](https://desktop.github.com/download/) is a GUI interface I use myself to simplify my development workflow.

To install [```uv```](https://github.com/astral-sh/uv), follow these [```uv``` install instructions](https://docs.astral.sh/uv/getting-started/installation/)

After installing and testing [```uv```](https://github.com/astral-sh/uv), use [```git```](https://git-scm.com/downloads) to [clone this repository](https://github.com/thatlarrypearson/vehicle-telemetry-system) onto your local target computer.

```bash
# Clone the git repository
git clone https://github.com/thatlarrypearson/vehicle-telemetry-system.git
```

Next, use [```uv```](https://github.com/astral-sh/uv) to prepare the virtual Python environment, install the needed Python version (if needed), install the required external Python libraries, build [Vehicle Telemetry System software](https://github.com/thatlarrypearson/vehicle-telemetry-system), install [Vehicle Telemetry System software](https://github.com/thatlarrypearson/vehicle-telemetry-system) and run a simple test of the newly installed software.

```bash
# get into the cloned repository directory
cd vehicle-telemetry-system

# create the virtual Python environment with the needed libraries
# by using the ```dependencies``` in the ```pyproject.toml``` file
uv sync

# Activate the Python Virtual Environment

# Windows PowerShell
.\.venv\Scripts\activate

# Linux/Mac bash Shell
source .venv/Scripts/activate

# When the Python Virtual Environment is activated, the prompt will change.

# Windows PowerShell
#     - (vehicle-telemetry-system) PS C:\Users\username\vehicle-telemetry-system >

# Linux/Mac bash Shell
#     - (vehicle-telemetry-system) user@hostname:~/vehicle-telemetry-system $

uv build .

# Developers may want to install the software such that changes are reflected in the virtual runtime environment automatically.
uv pip install -e .

# For production use, install the software as a Python package.
uv pip install dist/vehicle_telemetry_system-0.5.0-py3-none-any.whl
```

## Simple Tests Validating Build and Installation

Before running any module, be sure to activate the Python virtual environment.

```bash
# get into the cloned repository directory
cd vehicle-telemetry-system

# Activate the Python Virtual Environment

# Windows PowerShell
.\.venv\Scripts\activate

# Linux/Mac bash Shell
source .venv/Scripts/activate
```

Once the Python virtual environment is activated, get the usage from each of the modules as shown below.  If errors occur, resolve them before continuing.

### Engine (```telemetry_obd.obd_logger```)

```bash
uv run -m telemetry_obd.obd_logger --help
```

Results should look something like the following:

```bash
usage: obd_logger.py [-h] [--config_file CONFIG_FILE] [--config_dir CONFIG_DIR] [--full_cycles FULL_CYCLES]
                     [--timeout TIMEOUT] [--logging] [--no_fast] [--start_cycle_delay START_CYCLE_DELAY] [--verbose]
                     [--version]
                     [base_path]

Telemetry OBD Logger

positional arguments:
  base_path             Relative or absolute output data directory. Defaults to 'C:\Users\username\telemetry-data\data'.

options:
  -h, --help            show this help message and exit
  --config_file CONFIG_FILE
                        Settings file name. Defaults to '<vehicle-VIN>.ini' or 'default.ini'.
  --config_dir CONFIG_DIR
                        Settings directory path. Defaults to './config'.
  --full_cycles FULL_CYCLES
                        The number of full cycles before a new output file is started. Default is 5000.
  --timeout TIMEOUT     The number seconds before the current command times out. Default is 1.0 seconds.
  --logging             Turn on logging in python-obd library. Default is off.
  --no_fast             When on, commands for every request will be unaltered with potentially long timeouts when the
                        car doesn't respond promptly or at all. When off (fast is on), commands are optimized before
                        being sent to the car. A timeout is added at the end of the command. Default is off.
  --start_cycle_delay START_CYCLE_DELAY
                        Delay in seconds before first OBD command in cycle. Default is 0.
  --verbose             Turn verbose output on. Default is off.
  --version             Print version number and exit.
```

### Location (```gps_logger.gps_logger```)

```bash
uv run -m gps_logger.gps_logger --help
```

Results should look something like the following:

```bash
usage: gps_logger.py [-h] [--log_file_directory LOG_FILE_DIRECTORY]
                     [--serial SERIAL] [--verbose] [--version]

Telemetry GPS Logger

options:
  -h, --help            show this help message and exit
  --message_rate MESSAGE_RATE
                        Number of whole seconds between each GPS fix.  Defaults to 1.
  --serial SERIAL       Full path to the serial device where the GPS can be found, defaults to /dev/ttyACM0
  --verbose             Turn DEBUG logging on. Default is off.
  --version             Print version number and exit.
```

### Motion (```imu_logger.imu_logger```)

```bash
uv run -m imu_logger.imu_logger --help
```

Results should look something like the following:

```bash
WARNING:root:USB Serial Device <Unexpected Maker FeatherS3> NOT found
usage: imu_logger.py [-h] [--usb] [--serial_device_name SERIAL_DEVICE_NAME] [--no_wifi]
                     [--udp_port_number UDP_PORT_NUMBER] [--verbose] [--version]
                     [base_path]

Telemetry IMU Logger

positional arguments:
  base_path             Relative or absolute output data directory. Defaults to 'C:\Users\username\telemetry-data\data'.

options:
  -h, --help            show this help message and exit
  --usb                 CircuitPython microcontroller connects via USB is True. Default is False.
  --serial_device_name SERIAL_DEVICE_NAME
                        Name for the hardware IMU serial device. Defaults to None
  --no_wifi             CircuitPython microcontroller does NOT use WIFI to connect. Default is False
  --udp_port_number UDP_PORT_NUMBER
                        TCP/IP UDP port number for receiving datagrams. Defaults to '50219'
  --verbose             Turn DEBUG logging on. Default is off.
  --version             Print version number and exit.
```

### Weather (```wthr_logger.wthr_logger```)

```bash
uv run -m wthr_logger.wthr_logger --help
```

Results should look something like the following:

```bash
usage: wthr_logger.py [-h] [--log_file_directory LOG_FILE_DIRECTORY] [--verbose]
                      [--version]

Telemetry Weather Logger

options:
  -h, --help            show this help message and exit
  --log_file_directory LOG_FILE_DIRECTORY
                        Enable logging and place log files into this directory
  --verbose             Turn DEBUG logging on. Default is off.
  --version             Print version number and exit.
```

### Trailer (```trlr_logger.trlr_logger```)

```bash
uv run -m trlr_logger.trlr_logger --help
```

Results should look something like the following:

```bash
usage: trlr_logger.py [-h] [--udp_port_number UDP_PORT_NUMBER] [--log_file_directory LOG_FILE_DIRECTORY]
                      [--verbose] [--version]
                      [base_path]

Telemetry Trailer Connector UDP Logger

positional arguments:
  base_path             Relative or absolute output data directory. Defaults to '/home/username/telemetry-data/data'.

options:
  -h, --help            show this help message and exit
  --udp_port_number UDP_PORT_NUMBER
                        TCP/IP UDP port number for receiving datagrams. Defaults to '50223'
  --log_file_directory LOG_FILE_DIRECTORY
                        Place log files into this directory - defaults to /home/username/telemetry-data/data
  --verbose             Turn DEBUG logging on. Default is off.
  --version             Print version number and exit.
```

## Installing On Raspberry Pi

First, complete the [Python Project Software Installation](#python-project-software-build-and-installation) instructions.

Certain modules require configuration changes to [Raspberry Pi OS](https://www.raspberrypi.com/software/) to operate correctly.  No need to configure for modules not being used.

## Data Analysis

## License

[MIT](./LICENSE.md)

