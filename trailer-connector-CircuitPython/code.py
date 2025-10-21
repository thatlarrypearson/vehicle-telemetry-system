# telemetyry-trailer-connector/CircuitPython/code.py
# Install this file onto a FeatherS3 (ESP32-S3) CircuitPython microcontroller as 'code.py'.

import os
import wifi
import socketpool
import traceback
from time import sleep
import board
from adafruit_ads1x15 import ADS1015
from adafruit_ads1x15 import AnalogIn
from adafruit_ads1x15 import ads1x15
import json

# The Raspberry Pi data collector acts as a WIFI hotspot with
# an IP address on the WIFI hotspot interface of '192.168.2.1'.
# The data collection device IP address reachable on the same
# LAN segment as the hotspot address is set below.
UDP_HOST = os.getenv('UDP_HOST')
UDP_PORT = os.getenv('UDP_PORT')

CONNECTION_FAILED_SLEEP_TIME = os.getenv('CONNECTION_FAILED_SLEEP_TIME')
CIRCUITPY_WIFI_SSID = os.getenv('CIRCUITPY_WIFI_SSID')
CIRCUITPY_WIFI_PASSWORD = os.getenv('CIRCUITPY_WIFI_PASSWORD')
ADS_GAIN = os.getenv('ADS_GAIN')
# CYCLE_SLEEP is in milliseconds
CYCLE_SLEEP = float(os.getenv('CYCLE_SLEEP'))/1000.0

sequence_number = 1

print("UDP_HOST:", UDP_HOST)
print("UDP_PORT:", UDP_PORT)
print("CONNECTION_FAILED_SLEEP_TIME:", CONNECTION_FAILED_SLEEP_TIME)
print("CIRCUITPY_WIFI_SSID:", CIRCUITPY_WIFI_SSID),
print("CIRCUITPY_WIFI_PASSWORD:", CIRCUITPY_WIFI_PASSWORD)
print("ADS_GAIN:", ADS_GAIN)
print("CYCLE_SLEEP:", CYCLE_SLEEP)

# when the following fails, power cycle the FeatherS3
# after fixing the problem (e.g. I2C not connected to ADC).
i2c = board.I2C()

ads0 = ADS1015(i2c, gain=1, address=72)
# ads1 = ADS1015(i2c, gain=1, address=73)

while True:
    # connect to WIFI
    # print("trying to connect")
    try:
        wifi.radio.connect(CIRCUITPY_WIFI_SSID, CIRCUITPY_WIFI_PASSWORD)
    except ConnectionError as e:
        for item in traceback.format_exception(e):
            print(item)
        sleep(CONNECTION_FAILED_SLEEP_TIME)
        continue

    print("connected to WiFi:", CIRCUITPY_WIFI_SSID)

    pool = socketpool.SocketPool(wifi.radio)
    broadcast = pool.socket(family=pool.AF_INET, type=pool.SOCK_DGRAM)
    print("MAC address:", [hex(i) for i in wifi.radio.mac_address])
    print("IP address:", wifi.radio.ipv4_address)

    while True:
        # Get and package ADC data
        analog_input_channels = {}
        analog_input_channels['ads0/0'] = AnalogIn(ads0, ads1x15.Pin.A0)
        analog_input_channels['ads0/1'] = AnalogIn(ads0, ads1x15.Pin.A1)
        analog_input_channels['ads0/2'] = AnalogIn(ads0, ads1x15.Pin.A2)
        analog_input_channels['ads0/3'] = AnalogIn(ads0, ads1x15.Pin.A3)

#        analog_input_channels['ads1/0'] = AnalogIn(ads1, ads1x15.Pin.A0)
#        analog_input_channels['ads1/1'] = AnalogIn(ads1, ads1x15.Pin.A1)
#        analog_input_channels['ads1/2'] = AnalogIn(ads1, ads1x15.Pin.A2)
#        analog_input_channels['ads1/3'] = AnalogIn(ads1, ads1x15.Pin.A3)
#        analog_input_channels['ads1/3'] = AnalogIn(ads1, ads1x15.Pin.A3)

        record = {
            name: {
                'raw_value': channel.value,
                'voltage': channel.voltage
            } for name, channel in analog_input_channels.items()
        }

        record['gain0'] = ads0.gain
#        record['gain1'] = ads1.gain
        record['sequence_number'] = sequence_number
        json_record = json.dumps(record)

        # broadcast ADC data package
        broadcast.sendto(bytes(json_record, 'utf-8'), (UDP_HOST,UDP_PORT))
        sequence_number += 1
        print(json_record)

        sleep(CYCLE_SLEEP)
