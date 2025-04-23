# Vehicle Telemetry System

System for collecting and processing motor vehicle data using included sensor modules.

## **Under Construction**

The following repositories have been combined to create this repository:

- **Vehicle Sensor Module Repositories**
  - [engine](https://github.com/thatlarrypearson/telemetry-obd) (OBD)
  - [location](https://github.com/thatlarrypearson/telemetry-gps) (GPS)
  - [motion](https://github.com/thatlarrypearson/telemetry-imu) (IMU)
  - [weather](https://github.com/thatlarrypearson/telemetry-wthr) (WTHR)
  - [trailer](https://github.com/thatlarrypearson/telemetry-trailer-connector) (TRLR)
- **Common Function Repositories**
  - [Common utilities](https://github.com/thatlarrypearson/telemetry-utility) (UTILITY)
  - [Audit Capabilities](https://github.com/thatlarrypearson/telemetry-counter) (COUNTER)
- **Data Analysis Repositories**
  - [Combine JSON records into CSV records](https://github.com/thatlarrypearson/telemetry-obd-log-to-csv) (JSON2CSV)
  - [Notebook Data Analysis](https://github.com/thatlarrypearson/telemetry-analysis) (ANALYSIS)

## Python Project Software Installation

For this project, [```uv```](https://github.com/astral-sh/uv) is used to

- Install Python
- Create and manage the virtual Python runtime environment
- Create a Python package and install it into the virtual environment
- Run specific Python modules installed in the virtual environment

To install [```uv```](https://github.com/astral-sh/uv), follow these [```uv``` install instructions](https://docs.astral.sh/uv/getting-started/installation/)

After installing and testing [```uv```](https://github.com/astral-sh/uv), use [```git```](https://git-scm.com/downloads) to [clone this repository](https://github.com/thatlarrypearson/vehicle-telemetry-system) onto your local target computer.

```bash
# clone the git repository
git clone https://github.com/thatlarrypearson/vehicle-telemetry-system.git
```

Next, use [```uv```](https://github.com/astral-sh/uv) to prepare the virtual Python environment, install the needed Python version (if needed), install the required external Python libraries, build [Vehicle Telemetry System software](https://github.com/thatlarrypearson/vehicle-telemetry-system), install [Vehicle Telemetry System software](https://github.com/thatlarrypearson/vehicle-telemetry-system) and run a simple test of the newly installed software.

```bash
# get into the cloned repository directory
cd vehicle-telemetry-system

# create the virtual Python environment with the needed libraries
# by using the ```dependencies``` in the file
uv sync
```

## License

[MIT](./LICENSE.md)

