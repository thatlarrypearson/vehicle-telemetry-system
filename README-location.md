# Vehicle Telemetry System Location Logger

The location module captures location and time data using a GPS receiver. While the logger is running, location and time output is written to files.

## Motivation

Integrate GPS location and time data collection with vehicle engine data for better, more accurate analytics.

## Features

There are two versions of this.  The **current** supported version uses [**Adafruit Ultimate GPS with USB - 99 channel w/10 Hz updates**](https://www.adafruit.com/product/4279).  The **original** version uses a [Waveshare NEO-M8T GNSS TIMING HAT for Raspberry Pi, Single-Satellite Timing, Concurrent Reception of GPS, Beidou, Galileo, GLONASS](https://www.waveshare.com/neo-m8t-gnss-timing-hat.htm).

The Adafruit GPS was chosen when the original hardware stopped providing location information under open skies.  It was simpler to replace than debug what I suspect was a [hardware issue](#suspected-problems) affecting both the GPS receiver and the antenna.

- Logs location data to file

- Works with large family of GNSS enabling multiple constellations of satellites transmitting positioning and timing data
- Works with Python 3.10 and newer
- Raspberry Pi 4/5 hardware and Raspberry Pi OS target environment

### Current Supported Version

- Uses [GlobalTop MT3339](https://learn.adafruit.com/adafruit-ultimate-gps/downloads) chip set packaged by [CD Technology](https://www.cdtop-tech.com/products/pa1616d)

### Original Version

- Uses ([u-blox]((https://www.u-blox.com)) supporting GPS, GLONASS, Galileo and BeiDou Global Navigation Satellite Systems (GNSS) chip set families

## Target System

Raspberry Pi 4 or 5 with 4 GB RAM (or more) and with a 32 GB (or more) SD card.

## Target GPS Hardware

### Original Version Target GPS Hardware

Devices supporting USB or **RS-232**/**UART** interfaces made from **u-blox 8** or **u-blox M8** or newer GPS receiver chip sets are required for this application.  **u-blox** devices support the **UBX** protocol in addition to the **NMEA** protocol.  UBX is used for device configuration.  **NMEA** is used to decode **NMEA** location data.  The libraries used to support this application are bilingual.  That is, the libraries speak both **UBX** and **NMEA**.

Interfaces not supported include **SPI**, **I2C** and **DDC**.

The reference hardware is [Waveshare NEO-M8T GNSS TIMING HAT for Raspberry Pi, Single-Satellite Timing, Concurrent Reception of GPS, Beidou, Galileo, GLONASS](https://www.waveshare.com/neo-m8t-gnss-timing-hat.htm).  The board has a USB interface as well as a serial RS-232/UART interface.  The correct USB cable comes in the package.  The board is also a Raspberry Pi HAT.  Using the Raspberry Pi header, the board plugs into a UART interface.  GPS board comes with an external GPS antenna, a useful feature to keep electronics off the dashboard and out of the sun.

The **u-blox** device on the reference hardware is a [NEO-M8T](https://www.u-blox.com/en/product/neolea-m8t-series) chip.

In theory, any **u-blox** GPS devices supporting a USB interface should work fine with this software.  RS232 serial may work but might need some modifications to code to get the BAUD rate, data bits and parity right.

## Usage

### Current Support Version Usage

```bash
$ uv run -m gps_logger.adafruit_ultimate_gps_logger --help
usage: adafruit_ultimate_gps_logger.py [-h] [--serial SERIAL] [--verbose] [--version] [base_path]

Telemetry GPS Logger

positional arguments:
  base_path        Relative or absolute output data directory. Defaults to 'telemetry-data\data'.

options:
  -h, --help       show this help message and exit
  --serial SERIAL  Full path to the serial device where the GPS can be found, defaults to /dev/ttyUSB0
  --verbose        Turn DEBUG logging on. Default is off.
  --version        Print version number and exit.
$
```

### Original Version Usage

```bash
$ uv run -m gps_logger.gps_logger --help
usage: gps_logger.py [-h] [--message_rate MESSAGE_RATE] [--serial SERIAL] [--verbose] [--version] [base_path]

Telemetry GPS Logger

positional arguments:
  base_path             Relative or absolute output data directory. Defaults to 'telemetry-data\data'.

options:
  -h, --help            show this help message and exit
  --message_rate MESSAGE_RATE
                        Number of whole seconds between each GPS fix. Defaults to 1.
  --serial SERIAL       Full path to the serial device where the GPS can be found, defaults to /dev/ttyACM0
  --verbose             Turn DEBUG logging on. Default is off.
  --version             Print version number and exit.
$
```

## Output Data File Naming

Output data files are named as follows:

- ```"{BASE_PATH}/{HOST_ID}/{HOST_ID}-{boot_count_string}-{application_id}-{application_counter_string}.json"```

or expressed slightly differently:

- ```"{HOME}/telemetry-data/{HOST_ID}/{HOST_ID}-{boot_count_string}-{application_id}-{application_counter_string}.json"```

Where:

- ```BASE_PATH``` is the ```telemetry-data``` directory in the home directory of the user invoking this application.  Same as the output from the ```echo $HOME/telemetry-data``` command.
- ```HOST_ID``` is the host name of the computer the application is running on.  Same as the output from ```hostname``` command.
- ```boot_count_string``` is a zero padded number found in the system's boot count file.  See installation instructions for more info.
- ```application_id``` for this application is ```gps```.
- ```application_counter_string``` is a zero padded number hidden in the data file directory.  This number gets incremented every time this application is started.

For example, the following is the full path to the file as generated by this application:

- ```/home/human/telemetry-data/telemetry3/telemetry3-0000000010-gps-0000000159.json```

Why?  When aggregating data from multiple vehicles, each with its own little computer, the file names need to be unique and invariant across all of the vehicles.  All that the system creators need to do is to ensure that the host name on each computer is unique.  For more information on data file naming, consult [Telemetry System Boot and Application Startup Counter](./README-audit.md).

## Output Data File Format

The output data file format is the same format for all data collection modules in the [Vehicle Telemetry System](./README.md). General information about data logging, data formats and data processing can be found in [Data](./README.md/#data).  Using a standard data representation allows downstream processing of captured data using the same analysis tools.

Records in the log files are separated by line feeds ```<LF>```.  Each record is in JSON format representing the key/value pairs described below under [JSON Fields](#json-fields).

The following discussion describes specific aspects of the data generated in this module.

### JSON Fields

#### ```command_name```

The ```command_name``` identifies the ```<talker identifier><sentence formatter>``` of the specific GPS data source.  See **Section 31 NMEA Protocol** in the [u-blox 8 / u-blox M8 Receiver description Manual](https://content.u-blox.com/sites/default/files/products/documents/u-blox8-M8_ReceiverDescrProtSpec_UBX-13003221.pdf).

| **NMEA Talker IDs**| |
| ----- | ---- |
| **GNSS** | **Talker ID** |
| GPS | GP |
| GLONASS | GL |
| Galileo | GA |
| BeiDou | GB |
| Any combination of GNSS | GN |

#### ```obd_response_value```

Reflects the key/value pairs returned by the GPS.  The actual parsed NMEA output is contained in the ```obd_response_value``` field as a dictionary (key/value pairs).  That is, ```obd_response_value``` is a field that contains an NMEA record which also contains fields.  The field name is the key portion of the field.  The field value is the value part of the field.  Each NMEA sentence has its own unique set of field names.

##### Current Solution ```obd_response_value```

For the current GPS hardware, a decent description of the key/value pairs returned by the GPS are provided in the [GPS - NMEA sentence information](https://aprs.gids.nl/nmea/) web page.  Just remember to pay attention to the ```sentence formatter``` portion of the sentence identifier (see [Command Name](#command_name)) above.

The logged command names will be a combination of **talker identifiers** ```GP``` (GPS only), ```GL``` (GLONASS only) and ```GN``` (GPS and GLONASS).  For most uses, ```GN``` prefixed command names will provide greater accuracy than ```GP``` or ```GL``` variants.  That is, generally, two GNSS's are better than one.

The following represent the current solution's supported **sentence formatter**.

- ```<talker identifier>```**```<sentence formatter>```**
  - ```GGA``` Time, position and fix data
  - ```GSA``` GNSS receiver operating mode, active satellites used in the position solution and DOP values
  - ```GSV``` The number of GNSS satellites in view, satellite ID numbers, elevation, azimuth and SNR values
  - ```RMC``` Time, date, position, course and speed data
  - ```VTG``` Course and speed information relative to the ground

##### Original Version ```obd_response_value```

For the original solutions hardware, field names and value types can be found in the [u-blox 8 / u-blox M8 Receiver description - Manual](https://content.u-blox.com/sites/default/files/products/documents/u-blox8-M8_ReceiverDescrProtSpec_UBX-13003221.pdf) in the "31.2 Standard Messages" (messages as defined in the NMEA standard) section.  The current GPS data sources have a **talker identifier** of ```GN``` indicating any combination of GNSS (GPS, SBAS, QZSS, GLONASS, Galileo and/or BeiDou) as supported by the GPS unit will be used for positioning output data.

The following represent the original version's supported **sentence formatter**.

- ```<talker identifier>```**```<sentence formatter>```**
  - ```GNS``` Fix data
  - ```GST``` Pseudo range error statistics
  - ```THS``` True heading and status
  - ```TXT``` Text data (Not NMEA, proprietary u-blox protocol responses)
  - ```VTD``` Time and data

```iso_ts_pre``` ISO formatted timestamp taken before the GPS command was processed (```datetime.isoformat(datetime.now(tz=timezone.utc))```).

```iso_ts_post``` ISO formatted timestamp taken after the GPS command was processed (```datetime.isoformat(datetime.now(tz=timezone.utc))```).

### NMEA Sample Log Output - Current Adafruit GlobalTop Solution

In the sample output below, the format has been slightly modified for readability.  Below, the ```<LF>``` refers to Linux line feed and is used as a record terminator.

```bash
$ cd teleletry-gps/data/$(hostname)
$ cat telemetry2-0000001286-gps-0000001713.json
{
  "command_name": "GNGGA",
  "obd_response_value": {
    "time": "16:30:21",
    "lat": "38.5554133333",
    "NS": "N",
    "lon": "-90.4071366667",
    "EW": "W",
    "quality": "1",
    "numSV": "17",
    "HDOP": "0.62",
    "alt": "206.0",
    "altUnit": "M",
    "sep": "-33.5",
    "sepUnit": "M",
    "diffAge": null,
    "diffStation": null
  },
  "iso_ts_pre": "2025-10-29T16:30:17.640432+00:00",
  "iso_ts_post": "2025-10-29T16:30:18.027619+00:00"
}<LF>
{
  "command_name": "GPGSA",
  "obd_response_value": {
    "opMode": "A",
    "navMode": "3",
    "svid_01": "28",
    "svid_02": "31",
    "svid_03": "32",
    "svid_04": "10",
    "svid_05": "25",
    "svid_06": "1",
    "svid_07": "2",
    "svid_08": "3",
    "svid_09": "26",
    "svid_10": "12",
    "svid_11": null,
    "svid_12": null,
    "PDOP": "0.95",
    "HDOP": "0.62",
    "VDOP": "0.72"
  },
  "iso_ts_pre": "2025-10-29T16:30:18.031191+00:00",
  "iso_ts_post": "2025-10-29T16:30:18.093274+00:00"
}<LF>
{
  "command_name": "GLGSA",
  "obd_response_value": {
    "opMode": "A",
    "navMode": "3",
    "svid_01": "77",
    "svid_02": "67",
    "svid_03": "66",
    "svid_04": "76",
    "svid_05": "83",
    "svid_06": "82",
    "svid_07": "78",
    "svid_08": null,
    "svid_09": null,
    "svid_10": null,
    "svid_11": null,
    "svid_12": null,
    "PDOP": "0.95",
    "HDOP": "0.62",
    "VDOP": "0.72"
  },
  "iso_ts_pre": "2025-10-29T16:30:18.109362+00:00",
  "iso_ts_post": "2025-10-29T16:30:18.152529+00:00"
}<LF>
{
  "command_name": "GNRMC",
  "obd_response_value": {
    "time": "16:30:21",
    "status": "A",
    "lat": "38.5554133333",
    "NS":
    "N",
    "lon": "-90.4071366667",
    "EW": "W",
    "spd": "31.78",
    "cog": "182.09",
    "date": "2025-10-29",
    "mv": null,
    "mvEW": null,
    "posMode": "A"
  },
  "iso_ts_pre": "2025-10-29T16:30:18.169737+00:00",
  "iso_ts_post": "2025-10-29T16:30:18.228647+00:00"
}<LF>
{
  "command_name": "GNVTG", 
  "obd_response_value": {
    "cogt": "182.09",
    "cogtUnit": "T",
    "cogm": null,
    "cogmUnit": "M",
    "sogn": "31.78",
    "sognUnit": "N",
    "sogk": "58.88",
    "sogkUnit": "K",
    "posMode": "A"
  },
  "iso_ts_pre": "2025-10-29T16:30:18.248534+00:00",
  "iso_ts_post": "2025-10-29T16:30:18.270755+00:00"
}<LF>
```

### NMEA Sample Log Output - Original Waveshare uBlox Solution

In the sample output below, the format has been modified for readability.  Below, the ```<LF>``` refers to Linux line feed and is used as a record terminator.

```bash
$ cd teleletry-gps/data/$(hostname)
$ cat NMEA-20220525142137-utc.json
{
    "command_name": "NMEA_GNVTG",
    "obd_response_value":
    {
        "cogt": null,
        "cogtUnit": "T",
        "cogm": null,
        "cogmUnit": "M",
        "sogn": "0.024",
        "sognUnit": "N",
        "sogk": "0.045",
        "sogkUnit": "K",
        "posMode": "A"
    },
    "iso_ts_pre": "2022-05-25T14:45:18.162234+00:00",
    "iso_ts_post": "2022-05-25T14:45:22.121613+00:00"
}<LF>
{
    "command_name": "NMEA_GNGNS",
    "obd_response_value":
    {
        "time": "14:45:22",
        "lat": "29.5000000",
        "NS": "N",
        "lon": "-98.43000000",
        "EW": "W",
        "posMode": "AA",
        "numSV": "11",
        "HDOP": "1.08",
        "alt": "300.6",
        "sep": "-22.8",
        "diffAge": null,
        "diffStation": null
    },
    "iso_ts_pre": "2022-05-25T14:45:22.125739+00:00",
    "iso_ts_post": "2022-05-25T14:45:22.128793+00:00"
}<LF>
{
    "command_name": "NMEA_GNGST",
    "obd_response_value":
    {
        "time": "14:45:22",
        "rangeRms": "32.0",
        "stdMajor": null,
        "stdMinor": null,
        "orient": null,
        "stdLat": "2.1",
        "stdLong": "1.1",
        "stdAlt": "2.4"
    },
    "iso_ts_pre": "2022-05-25T14:45:22.133219+00:00",
    "iso_ts_post": "2022-05-25T14:45:22.135003+00:00"
}<LF>
{
    "command_name": "NMEA_GNZDA",
    "obd_response_value":
    {
        "time": "14:45:22",
        "day": "25",
        "month": "5",
        "year": "2022",
        "ltzh": "00",
        "ltzn": "00"
    },
    "iso_ts_pre": "2022-05-25T14:45:22.141224+00:00",
    "iso_ts_post": "2022-05-25T14:45:22.142981+00:00"
}<LF>
$
```

## What To Do When Your GPS Device Is Not Found

You can tell when your GPS device is not being found when you receive the following two error logging messages from ```gps_logger.gps_logger```:

- ```USB attached GPS device <u-blox GNSS receiver> not found.```
- ```Trying serial port device </dev/ttyACM0>.```

Telemetry GPS includes ```gps_logger.usb_devices```, a Python program that will tell you if it can find the correct device name and **it may help you find the correct device name**.

With both the GPS (_u-blox GNSS receiver_) and IMU (_Unexpected Maker FeatherS3_) plugged into host USB ports, running ```gps_logger.usb_devices``` will show both devices and it will show that it did or did not find the GPS device.

In the event that your ```u-blox``` GPS device is plugged in but it isn't showing as found, use ```gps_logger.usb_devices``` to get the correct values for ```DEFAULT_USB_VID``` and ```DEFAULT_USB_PID```.  Change these values in ```telemetry-gps/gps_logger/usb_devices.py``` and rebuild/reinstall the _Telemetry GPS_ package per the above instructions.

```bash
$ uv run -m gps_logger.usb_devices
Candidate Serial Device List (non-USB devices excluded)

	+1 /dev/ttyACM1
		Name: ttyACM1
		USB VID: 12346
		USB PID: 32983
		Description: FeatherS3 - CircuitPython CDC control
		Hardware ID: USB VID:PID=303A:80D7 SER=CEADB3143BC5 LOCATION=1-1.1:1.0
		Manufacturer: UnexpectedMaker
		Product: FeatherS3
		Serial Number: CEADB3143BC5
		Location: 1-1.1:1.0
		interface: CircuitPython CDC control

	+2 /dev/ttyACM0
		Name: ttyACM0
		USB VID: 5446
		USB PID: 424
		Description: u-blox GNSS receiver
		Hardware ID: USB VID:PID=1546:01A8 LOCATION=1-1.2:1.0
		Manufacturer: u-blox AG - www.u-blox.com
		Product: u-blox GNSS receiver
		Serial Number: None
		Location: 1-1.2:1.0
		interface: None

Found 2 USB Serial Device(s)

USB Serial Device <u-blox GNSS receiver> Name /dev/ttyACM0 found
$ 
```

## Known Problems

The ```gps_logger.gps_logger``` application fails periodically when noise on the serial interfaces causes bit changes.  This extremely rare occurrence causes an ```NMEAParseError``` exception to be raised.  When ```NMEAParseError```s occur, the boot startup shell program ```bin/gps_logger.sh``` waits 20 seconds before restarting ```gps_logger.gps_logger```.

Zero length data files can occur when the Raspberry Pi host isn't seeing the GPS device.  For example, when a USB GPS device either has a bad cable or wasn't plugged in properly, the log files found in the ```tmp``` directory off the telemetry-gps project directory will have entries similar to the following:

```bash
Traceback (most recent call last):
  File "/home/human/.local/lib/python3.11/site-packages/serial/serialposix.py", line 322, in open
    self.fd = os.open(self.portstr, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
FileNotFoundError: [Errno 2] No such file or directory: '/dev/ttyACM0'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/local/lib/python3.11/runpy.py", line 196, in _run_module_as_main
    return _run_code(code, main_globals, None,
  File "/usr/local/lib/python3.11/runpy.py", line 86, in _run_code
    exec(code, run_globals)
  File "/home/human/telemetry-gps/gps_logger/gps_logger.py", line 148, in <module>
    main()
  File "/home/human/telemetry-gps/gps_logger/gps_logger.py", line 103, in main
    io_handle = initialize_gps(serial_device, 4)
  File "/home/human/telemetry-gps/gps_logger/connection.py", line 34, in initialize_gps
    io_handle = connect_to_gps(device_path, **kwargs)
  File "/home/human/telemetry-gps/gps_logger/connection.py", line 27, in connect_to_gps
    return Serial(port=device_path, **kwargs)
  File "/home/human/.local/lib/python3.11/site-packages/serial/serialutil.py", line 244, in __init__
    self.open()
  File "/home/human/.local/lib/python3.11/site-packages/serial/serialposix.py", line 325, in open
    raise SerialException(msg.errno, "could not open port {}: {}".format(self._port, msg))
serial.serialutil.SerialException: [Errno 2] could not open port /dev/ttyACM0: [Errno 2] No such file or directory: '/dev/ttyACM0'
```

Note the above places where it says ```No such file or directory: '/dev/ttyACM0'```.  ```/dev/ttypACM0``` is one of the default device file names for a Raspberry Pi USB GPS device.

The following shows how to identify and then remove zero length JSON data files.

```bash
$ # From the telemetry-gps project directory
$ cd data
$ ls -l
-rw-r--r-- 1 human 197609    3570 Aug 14 06:31 NMEA-20220814113106-utc.json
-rw-r--r-- 1 human 197609  143497 Aug 26 08:39 NMEA-20220826133137-utc.json
-rw-r--r-- 1 human 197609 1883662 Aug 26 10:34 NMEA-20220826134824-utc.json
-rw-r--r-- 1 human 197609   81748 Aug 26 10:39 NMEA-20220826153428-utc.json
-rw-r--r-- 1 human 197609  102988 Aug 26 10:56 NMEA-20220826155057-utc.json
-rw-r--r-- 1 human 197609   18169 Aug 26 11:08 NMEA-20220826160759-utc.json
-rw-r--r-- 1 human 197609 1617134 Aug 26 12:58 NMEA-20220826162732-utc.json
-rw-r--r-- 1 human 197609  411207 Aug 26 13:21 NMEA-20220826175820-utc.json
-rw-r--r-- 1 human 197609   19072 Sep  5 14:51 NMEA-20220905195019-utc.json
-rw-r--r-- 1 human 197609       0 Sep 10 12:08 NMEA-20220910170858-utc.json
-rw-r--r-- 1 human 197609       0 Sep 10 12:09 NMEA-20220910170909-utc.json
-rw-r--r-- 1 human 197609       0 Sep 10 12:09 NMEA-20220910170921-utc.json
-rw-r--r-- 1 human 197609       0 Sep 10 12:09 NMEA-20220910170931-utc.json
-rw-r--r-- 1 human 197609       0 Sep 10 12:09 NMEA-20220910170942-utc.json
-rw-r--r-- 1 human 197609       0 Sep 10 12:09 NMEA-20220910170952-utc.json
-rw-r--r-- 1 human 197609       0 Sep 10 12:10 NMEA-20220910171003-utc.json
$
$ # Above, files starting with "NMEA-20220910" are all zero length
$
$ # To find zero length JSON files programmatically:
$ find . -type f -name '*.json' -size 0 -print
NMEA-20220910170858-utc.json
NMEA-20220910170909-utc.json
NMEA-20220910170921-utc.json
NMEA-20220910170931-utc.json
NMEA-20220910170942-utc.json
NMEA-20220910170952-utc.json
NMEA-20220910171003-utc.json
$
$ # To find and delete zero length JSON files programmatically:
$ find . -type f -name '*.json' -size 0 -print | while read filename
> do
> echo "${fname}"
> rm -f "${fname}"
> done
./NMEA-20220910170858-utc.json
./NMEA-20220910170909-utc.json
./NMEA-20220910170921-utc.json
./NMEA-20220910170931-utc.json
./NMEA-20220910170942-utc.json
./NMEA-20220910170952-utc.json
./NMEA-20220910171003-utc.json
$
$ # If you have a LARGE NUMBER of zero length JSON files, this may run out of memory.
$ # To do the find and delete operation on a single line:
$ rm -f $(find . -type f -name '*.json' -size 0 -print)
```

## Suspected Problems

GPS receivers may be susceptible to failure when antenna wires or antennas are sitting on top of a vehicle speaker.  This is the case on the current primary test vehicle.  The GPS receiver failed within a month of placement on top of a speaker.

## License

[MIT](LICENSE.md)
