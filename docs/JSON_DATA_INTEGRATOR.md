# JSON Data Integrator

## **UNDER CONSTRUCTION**

The JSON Data Integrator integrates telemetry JSON data from multiple sources into a single data file:

- telemetry_obd.obd_logger
- gps_logger.gps_logger
- wthr_logger.wthr_logger
- imu_logger.imu_logger
- other sources conforming to [Telemetry OBD Logger Output Data Files](https://github.com/thatlarrypearson/telemetry-obd#telemetry-obd-logger-output-data-files)

## Usage

```bash
$ python -m obd_log_to_csv.json_data_integrator --help
usage: json_data_integrator [-h] [--base_path BASE_PATH] --hostname HOSTNAME --boot_count BOOT_COUNT [--version VERSION] [--verbose]

Telemetry JSON Data Integrator

options:
  -h, --help            show this help message and exit
  --base_path BASE_PATH
                        BASE_PATH directory variable. Defaults to C:\Users\runar/telemetry-data/data
  --hostname HOSTNAME   The hostname of the computer where the data was collected.
  --boot_count BOOT_COUNT
                        A counter used to identify the number of times the data collection computer booted since telemetry-counter was installed and configured.
  --version VERSION     Returns version and exit.
  --verbose             Turn verbose output on. Default is off.
$
```

## Directory Structure

Directory Structure

### DATA_PATH

- ```telemetry-data```

### BASE_PATH

- ```~/<DATA_PATH>/data```
- ```~/telemetry-data/data```

Where ```~/``` is the same as ```${HOME}``` or ```<HOME>``` or just the home directory.

### JSON Data Directory

- ```<HOME>/<DATA_PATH>/data/<HOSTNAME>```
- ```~/<DATA_PATH>/data/<HOSTNAME>```
- ```~/telemetry-data/data/<HOSTNAME>```
- ```C:\Users\lbp/telemetry-data/data/telemetry2```

Where ```<HOSTNAME>``` is the hostname of the computer where the data was collected.

### JSON Data File Names

Many different naming formats.

#### COUNTER (CURRENT) INPUT FILE NAMING FORMAT

There are two variations of the current format.  The one for ```OBD``` and the one for everything else.  The ```OBD``` naming format follows.

- ```<HOSTNAME>-<boot_count>-<application_name>-<VIN>-<application_count>.json```
- ```telemetry2-0000000072-obd-C4HJWCG9DL9999-0000000039.json```

Where ```<VIN>``` is the vehicle VIN as provided through the ```OBD``` interface and the ```<application_name>``` is "obd".

Everything other than ```OBD``` is as follows.

- ```<HOSTNAME>-<boot_count>-<application_name>-<application_count>.json```
- ```telemetry2-0000000072-gps-0000000114.json```
- ```telemetry2-0000000072-imu-0000000078.json```
- ```telemetry2-0000000072-wthr-0000000066.json```

Where ```<application_name>``` is one of ```gps```, ```imu```, ```wthr```, etc.

#### INTERIM INPUT FILE NAMING FORMAT

The interim file naming format is similar to the current format in that it uses a ```boot_count```.  For ```OBD``` data files, this is as follows.

- ```<VIN>-<boot_count>.json```
- ```3FTTW8F97PRA99999-0000000007.json```

For all other sensor file types, it is as follows:

- ```<application_name>-<boot_count>.json```
- ```NMEA-0000000032.json```

```NMEA``` is the application name for ```gps``` before the current naming scheme.

#### ORIGINAL INPUT FILE NAMING FORMAT

The original file naming format used [Coordinated Universal Time or UTC](https://en.wikipedia.org/wiki/Coordinated_Universal_Time) timestamps in the file name.  These files all ended with the timestamp followed by ```-utc``` and used the file suffix ```.json```.  The ```OBD``` data file name format was

- ```<VIN>-<utc_timestamp>-utc.json```
- ```<VIN>-<YYYYmmddHHMMSS>-utc.json```
- ```C4HJWCG5DL9999-20230112133422-utc.json```

During the time this format was used, the only application name in use was ```NMEA```, now called ```gps```.

- ```<application_name>-<utc_timestamp>-utc.json```
- ```<application_name>-<YYYYmmddHHMMSS>-utc.json```
- ```NMEA-20220610172050-utc.json```

## JSON Record Format

The JSON record format hasn't changed.  It is still the same.

```python
json_record = {
    "command_name": "WTHR_rapid_wind",
    "obd_response_value": {
        "time_epoch": 1705005028,
        "wind_speed": 5.49,
        "wind_direction": 3
    },
    "iso_ts_pre": "2024-01-12T15:29:28.675679+00:00",
    "iso_ts_post": "2024-01-12T15:29:30.944695+00:00"
}
```

## Output Sort Order

When all three of the JSON record fields in two different records have the same values, then one of the records is a duplicate record.  All of the records are sorted using the ordering shown below.  Duplicate records are deleted.

- ```json_record["iso_ts_pre"]```
- ```json_record["iso_ts_post"]```
- ```json_record["command_name"]```

## Output File Name

There will be some file name format differences between the current, interim and original input file naming conventions.

### CURRENT

- ```<HOSTNAME>-<boot_count>-integrated-<VIN>.json```
- ```telemetry2-0000000072-integrated-C4HJWCG9DL9999.json```

### INTERIM

- ```INTERIM-<boot_count>-integrated-<VIN>.json```
- ```INTERIM-0000000072-integrated-C4HJWCG9DL9999.json```

### ORIGINAL

- ```ORIGINAL-<utc_timestamp>-integrated-<VIN>.json```
- ```ORIGINAL-<YYYYmmddHHMMSS>-integrated-<VIN>.json```
- ```ORIGINAL-20230112133422-integrated-C4HJWCG5DL9999.json```

## License

[MIT License](../LICENSE.md)
