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

logging.basicConfig(stream=stderr, level=logging.DEBUG)

def get_serial_device_name(verbose=False, default_serial_device=DEFAULT_SERIAL_DEVICE)->str:
    """Get serial device name for GPS"""

    logging.info("Candidate Serial Device List (non-USB devices excluded)")
    i = 0
    return_device = None

    for p in comports():
        vid = p.vid
        if not vid:
            # not a USB device
            continue

        device = p.device
        pid = p.pid

        i += 1
        logging.info(f"{i:3} {device}")
        logging.info(f"\tName: {p.name}")
        logging.info(f"\tUSB VID: {vid} type {type(vid)}")
        logging.info(f"\tUSB PID: {pid} type {type(pid)}")
        logging.info(f"\tDescription: {p.description}")
        logging.info(f"\tHardware ID: {p.hwid}")
        logging.info(f"\tManufacturer: {p.manufacturer}")
        logging.info(f"\tProduct: {p.product}")
        logging.info(f"\tSerial Number: {p.serial_number}")
        logging.info(f"\tLocation: {p.location}")
        logging.info(f"\tinterface: {p.interface}")
        logging.info(f"\tdevice: {device}")
        logging.info(f"\tdevice_path: {p.device_path}")
        logging.info(f"\tusb_device_path: {p.usb_device_path}")

        if p.vid == DEFAULT_USB_VID and p.pid == DEFAULT_USB_PID:
            return_device = device
            logging.info(f"** DEVICE FOUND: {return_device} **")

    logging.info(f"{i} USB Serial Device(s) Found")

    if return_device:
        return return_device

    logging.info(f"USB Attached GPS Device <{GPS_DEVICE_NAME}> not found.")
    logging.info(f"Using Default Serial Device <{default_serial_device}>.")

    return default_serial_device

def main():
    if sdn := get_serial_device_name(default_serial_device=None):
        logging.info(f"\nUSB Serial Device <{GPS_DEVICE_NAME}> Name {sdn} found")
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main()

