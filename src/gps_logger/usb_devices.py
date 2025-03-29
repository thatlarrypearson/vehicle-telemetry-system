# telemetry-gps/gps_logger/usb_devices.py

import logging
from sys import stderr
from serial.tools.list_ports import comports

# The following are specific to the u-blox GNSS receiver
DEFAULT_USB_VID = 5446
DEFAULT_USB_PID = 424
GPS_DEVICE_NAME = "u-blox GNSS receiver"

# This default is the default device name on a Raspberry Pi when the GPS is the only attached serial USB device.
DEFAULT_SERIAL_DEVICE="/dev/ttyACM0"

def get_serial_device_name(verbose=False, default_serial_device=DEFAULT_SERIAL_DEVICE)->str:
    """Get serial device name for GPS"""

    for p in comports():
        if p.vid and p.vid == DEFAULT_USB_VID and p.pid == DEFAULT_USB_PID:
            return p.device

    logging.error(f"USB attached GPS device <{GPS_DEVICE_NAME}> not found.")
    logging.info(f"Trying serial port device <{default_serial_device}>.")

    return default_serial_device

def main():
    logging.basicConfig(stream=stderr, level=logging.DEBUG)

    logging.info("Candidate Serial Device List (non-USB devices excluded)")
    i = 0
    for p in comports():
        if not p.vid:
            # not a USB device
            continue
        i += 1
        logging.info(f"\n\t+{i} {p.device}")
        logging.info(f"\t\tName: {p.name}")
        logging.info(f"\t\tUSB VID: {p.vid}")
        logging.info(f"\t\tUSB PID: {p.pid}")
        logging.info(f"\t\tDescription: {p.description}")
        logging.info(f"\t\tHardware ID: {p.hwid}")
        logging.info(f"\t\tManufacturer: {p.manufacturer}")
        logging.info(f"\t\tProduct: {p.product}")
        logging.info(f"\t\tSerial Number: {p.serial_number}")
        logging.info(f"\t\tLocation: {p.location}")
        logging.info(f"\t\tinterface: {p.interface}")

    logging.info(f"\nFound {i} USB Serial Device(s)")

    if sdn := get_serial_device_name(default_serial_device=None):
        logging.info(f"\nUSB Serial Device <{GPS_DEVICE_NAME}> Name {sdn} found")
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main()

