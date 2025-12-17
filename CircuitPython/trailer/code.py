# code.py
# code.py
__version__ = "0.5.0"
# telemetry-trailer-connector/CircuitPython/code.py
# Install this file onto a FeatherS3 (ESP32-S3) CircuitPython microcontroller as 'code.py'.

import board
from adafruit_ads1x15 import ADS1015
from adafruit_ads1x15 import AnalogIn
from adafruit_ads1x15 import ads1x15
import os
import wifi
import socketpool
import traceback
from time import sleep
from json import dumps
from adafruit_itertools import count

# The Raspberry Pi data collector acts as a WIFI hotspot with
# an IP address on the WIFI hotspot interface of '192.168.2.1'.
# The data collection device IP address reachable on the same
# LAN segment as the hotspot address is set below.
UDP_HOST = os.getenv('UDP_HOST')
UDP_PORT = os.getenv('UDP_PORT')

CONNECTION_FAILED_SLEEP_TIME = os.getenv('CONNECTION_FAILED_SLEEP_TIME')
WIFI_SSID = os.getenv('WIFI_SSID')
WIFI_PASSWORD = os.getenv('WIFI_PASSWORD')
ADS_GAIN = os.getenv('ADS_GAIN')
# Work around for gain "2/3" as opposed to [1,2,3,4]
if isinstance(ADS_GAIN, str) and ADS_GAIN == "2/3":
    ADS_GAIN = 2/3
ADS0_ADDRESS = os.getenv('ADS0_ADDRESS')
ADS1_ADDRESS = os.getenv('ADS1_ADDRESS')
# CYCLE_SLEEP is in milliseconds
CYCLE_SLEEP = float(os.getenv('CYCLE_SLEEP'))/1000.0

print("telemetry-trailer-connector/CircuitPython/code.py version:", __version__)
print("UDP_HOST:", UDP_HOST)
print("UDP_PORT:", UDP_PORT)
print("CONNECTION_FAILED_SLEEP_TIME:", CONNECTION_FAILED_SLEEP_TIME)
print("WIFI_SSID:", WIFI_SSID),
print("WIFI_PASSWORD:", WIFI_PASSWORD)
print("ADS_GAIN:", ADS_GAIN)
print("ADS0_ADDRESS:", ADS0_ADDRESS)
print("ADS1_ADDRESS:", ADS1_ADDRESS)
print("CYCLE_SLEEP:", CYCLE_SLEEP)

i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

while not i2c.try_lock():
    pass

print("I2C addr", [hex(device_address) for device_address in i2c.scan()])

i2c.unlock()

print(f"code.py version {__version__}")

# ads0 - No Jumpers, then address = 72
ads0 = ADS1015(i2c, gain=1, address=ADS0_ADDRESS)
# ads1 - Jumper between ADDR and SCL then address = 75
#                       ADDR and SDA then address = 74
#                       ADDR and VIN then address = 73
ads1 = ADS1015(i2c, gain=1, address=ADS1_ADDRESS)

sequence_number = 1

while True:
    # connect to WIFI
    # print("trying to connect")
    # print("trying to connect")
    try:
        wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
    except ConnectionError as e:
        #for item in traceback.format_exception(e):
        #    print(item)
        sleep(CONNECTION_FAILED_SLEEP_TIME)
        continue

    print("connected to WiFi:", WIFI_SSID)

    pool = socketpool.SocketPool(wifi.radio)
    broadcast = pool.socket(family=pool.AF_INET, type=pool.SOCK_DGRAM)
    print("MAC address:", [hex(i) for i in wifi.radio.mac_address])
    print("IP address:", wifi.radio.ipv4_address)

    while True:
        # Get and package ADC data
        analog_input_channels = {
            'ads0/0': AnalogIn(ads0, ads1x15.Pin.A0),   # 7 pin - blue,   brakes
            'ads0/1': AnalogIn(ads0, ads1x15.Pin.A1),   # 7 pin - brown,  taillights
            'ads0/2': AnalogIn(ads0, ads1x15.Pin.A2),   # 7 pin - yellow, left/stop
            'ads0/3': AnalogIn(ads0, ads1x15.Pin.A3),   # 7 pin - green,  right/stop

            'ads1/0': AnalogIn(ads1, ads1x15.Pin.A0),   # 7 pin - purple, backup
            'ads1/1': AnalogIn(ads1, ads1x15.Pin.A1),   # 4 pin - brown,  taillights
            'ads1/2': AnalogIn(ads1, ads1x15.Pin.A2),   # 4 pin - yellow, left/stop
            'ads1/3': AnalogIn(ads1, ads1x15.Pin.A3),   # 4 pin - green,  right/stop
        }

        record = {
            name: {
                'raw_value': channel.value,
                'voltage': channel.voltage,
            } for name, channel in analog_input_channels.items()
        }

        record['gain0'] = ads0.gain
        record['gain1'] = ads1.gain
        record['sequence_number'] = sequence_number
        json_record = dumps(record)

        # broadcast ADC data package
        try:
            broadcast.sendto(bytes(json_record, 'utf-8'), (UDP_HOST,UDP_PORT))
        except BrokenPipeError:
            # BrokenPipeError exception occurs when the hotspot is unreachable or down
            # Go back to trying to establish WIFI connection
            break

        sequence_number += 1

        sleep(CYCLE_SLEEP)
