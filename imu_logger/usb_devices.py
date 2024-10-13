# telemetry-imu/imu_logger/usb_devices.py

import logging
from sys import stderr
from serial.tools.list_ports import comports

# The following are specific to the Unexpected Maker FeatherS3
DEFAULT_USB_VID = 12346
DEFAULT_USB_PID = 32983
CIRCUITPYTHON_DEVICE_NAME = "Unexpected Maker FeatherS3"

def get_serial_device_name(verbose=False)->str:
    """Get serial device name for CIRCUITPYTHON_DEVICE_NAME from OS"""

    for p in comports():
        if p.vid and p.vid == DEFAULT_USB_VID and p.pid == DEFAULT_USB_PID:
            return p.device

    logging.warning(f"\nUSB Serial Device <{CIRCUITPYTHON_DEVICE_NAME}> NOT found")

    return None

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

    print(f"\nFound {i} USB Serial Device(s)")

    if sdn := get_serial_device_name():
        logging.info(f"\nUSB Serial Device <{CIRCUITPYTHON_DEVICE_NAME}> Name {sdn} found")
        exit(0)
    else:
        logging.info(f"\nUSB Serial Device <{CIRCUITPYTHON_DEVICE_NAME}> NOT found")
        exit(1)

if __name__ == "__main__":
    main()

