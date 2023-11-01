# telemetry-imu/imu_logger/usb_devices.py

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

    print(f"Device <{CIRCUITPYTHON_DEVICE_NAME}> not found.")

    return None

def main():
    print("Candidate Serial Device List (non-USB devices excluded)")
    i = 0
    for p in comports():
        if not p.vid:
            # not a USB device
            continue
        i += 1
        print(f"\n\t+{i} {p.device}")
        print(f"\t\tName: {p.name}")
        print(f"\t\tUSB VID: {p.vid}")
        print(f"\t\tUSB PID: {p.pid}")
        print(f"\t\tDescription: {p.description}")
        print(f"\t\tHardware ID: {p.hwid}")
        print(f"\t\tManufacturer: {p.manufacturer}")
        print(f"\t\tProduct: {p.product}")
        print(f"\t\tSerial Number: {p.serial_number}")
        print(f"\t\tLocation: {p.location}")
        print(f"\t\tinterface: {p.interface}")

    print(f"\nFound {i} USB Serial Device(s)")

    if sdn := get_serial_device_name():
        print(f"\nUSB Serial Device <{CIRCUITPYTHON_DEVICE_NAME}> Name {sdn} found")
    else:
        print(f"\nUSB Serial Device <{CIRCUITPYTHON_DEVICE_NAME}> NOT found")

if __name__ == "__main__":
    main()

