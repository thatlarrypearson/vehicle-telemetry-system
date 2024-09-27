# Telemetry IMU (inertial motion unit) Logger

## **UNDER CONSTRUCTION**

Logs 9 DOF (degrees of freedom) captured from CircuitPython enabled feather micro-controller connected to I2C enabled 9 DOF feather wing.

## Usage

```bash
$ python -m imu_logger.imu_logger --help
usage: imu_logger.py [-h]
                     [--serial_device_name SERIAL_DEVICE_NAME] [--verbose] [--version]
                     [base_path]

Telemetry IMU Logger

positional arguments:
  base_path             Relative or absolute output data directory. Defaults to 'C:\Users\runar/telemetry-data/data'.

options:
  -h, --help            show this help message and exit
  --serial_device_name SERIAL_DEVICE_NAME
                        Name for the hardware IMU serial device. Defaults to None
  --verbose             Turn DEBUG logging on. Default is off.
  --version             Print version number and exit.
$
```

## Installation

### Problems Identifying Serial Device Name

Telemetry IMU includes ```imu_logger.usb_devices```, a Python program that will tell you if it can find the correct device name.

With the IMU (_Unexpected Maker FeatherS3_) unplugged from the host USB port, running ```imu_logger.usb_devices``` shows the GPS receiver which is plugged into a USB port.

```bash
lbp@telemetry2:~ $ python3.11 -m imu_logger.usb_devices
Candidate Serial Device List (non-USB devices excluded)

	+1 /dev/ttyACM0
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

Found 1 USB Serial Device(s)

Device <Unexpected Maker FeatherS3> not found.
lbp@telemetry2:~ $ 
```

Using a different MicroPython micro-controller (other than an _Unexpected Maker FeatherS3_) will require changing the following code snippet to match your MicroPython micro-controller.  Running the above will provide you with the correct values for ```DEFAULT_USB_VID``` and ```DEFAULT_USB_PID```.

```python
# The following are specific to the Unexpected Maker FeatherS3
DEFAULT_USB_VID = 12346
DEFAULT_USB_PID = 32983
CIRCUITPYTHON_DEVICE_NAME = "Unexpected Maker FeatherS3"
```

## LICENSE

[MIT License](./LICENSE.md)
