# code.py
__version__ = "0.0.1"
# basic IMU software test

import board
import board
import adafruit_bno08x
from adafruit_bno08x.i2c import BNO08X_I2C
from adafruit_bno08x import (
    BNO_REPORT_ACCELEROMETER,
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_GRAVITY,
    BNO_REPORT_LINEAR_ACCELERATION,
    BNO_REPORT_MAGNETOMETER,
    BNO_REPORT_ROTATION_VECTOR,
)
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
# CYCLE_SLEEP is in milliseconds
CYCLE_SLEEP = float(os.getenv('CYCLE_SLEEP'))/1000.0

sequence_number = 1

print("UDP_HOST:", UDP_HOST)
print("UDP_PORT:", UDP_PORT)
print("CONNECTION_FAILED_SLEEP_TIME:", CONNECTION_FAILED_SLEEP_TIME)
print("WIFI_SSID:", WIFI_SSID),
print("WIFI_PASSWORD:", WIFI_PASSWORD)
print("CYCLE_SLEEP:", CYCLE_SLEEP)

i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

while not i2c.try_lock():
    pass

print("I2C addr", [hex(device_address) for device_address in i2c.scan()])

i2c.unlock()

print(f"code.py version {__version__}")

bno = BNO08X_I2C(i2c, debug=False)

bno.enable_feature(BNO_REPORT_ACCELEROMETER)
bno.enable_feature(BNO_REPORT_GYROSCOPE)
bno.enable_feature(BNO_REPORT_GRAVITY)
bno.enable_feature(BNO_REPORT_LINEAR_ACCELERATION)
bno.enable_feature(BNO_REPORT_MAGNETOMETER)
bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

i = 0
while True:
    # connect to WIFI
    # print("trying to connect")
    try:
        wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
    except ConnectionError as e:
        for item in traceback.format_exception(e):
            print(item)
        sleep(CONNECTION_FAILED_SLEEP_TIME)
        continue

    print("connected to WiFi:", WIFI_SSID)

    pool = socketpool.SocketPool(wifi.radio)
    broadcast = pool.socket(family=pool.AF_INET, type=pool.SOCK_DGRAM)
    print("MAC address:", [hex(i) for i in wifi.radio.mac_address])
    print("IP address:", wifi.radio.ipv4_address)

    try:
        while True:
            i += 1

            x, y, z = bno.acceleration
            broadcast.sendto(
                bytes(dumps({
                    'command_name': 'acceleration',
                    'obd_response_value': {
                        'record_number': i,
                        'x': x,
                        'y': y,
                        'z': z,
                    }, }),
                    'UTF-8'
                ),
                (UDP_HOST,UDP_PORT)
            )
            x, y, z = bno.gravity
            broadcast.sendto(
                bytes(dumps({
                    'command_name': 'gravity',
                    'obd_response_value': {
                        'record_number': i,
                        'x': x,
                        'y': y,
                        'z': z,
                    }, }),
                    'UTF-8'
                ),
                (UDP_HOST,UDP_PORT)
            )
            x, y, z = bno.gyro
            broadcast.sendto(
                bytes(dumps({
                    'command_name': 'gyroscope',
                    'obd_response_value': {
                        'record_number': i,
                        'x': x,
                        'y': y,
                        'z': z,
                    }, }),
                    'UTF-8'
                ),
                (UDP_HOST,UDP_PORT)
            )
            x, y, z = bno.linear_acceleration
            broadcast.sendto(
                bytes(dumps({
                    'command_name': 'linear_acceleration',
                    'obd_response_value': {
                        'record_number': i,
                        'x': x,
                        'y': y,
                        'z': z,
                    }, }),
                    'UTF-8'
                ),
                (UDP_HOST,UDP_PORT)
            )
            x, y, z = bno.magnetic
            broadcast.sendto(
                bytes(dumps({
                    'command_name': 'magnetometer',
                    'obd_response_value': {
                        'record_number': i,
                        'x': x,
                        'y': y,
                        'z': z,
                    }, }),
                    'UTF-8'
                ),
                (UDP_HOST,UDP_PORT)
            )
            vector = bno.quaternion
            broadcast.sendto(
                bytes(dumps({
                    'command_name': 'rotation_vector',
                    'obd_response_value': {
                        'record_number': i,
                        'vector': vector,
                    }, }),
                    'UTF-8'
                ),
                (UDP_HOST,UDP_PORT)
            )

            sleep(CYCLE_SLEEP)

    except Exception as e:
        for item in traceback.format_exception(e):
            print(item)
        sleep(CONNECTION_FAILED_SLEEP_TIME)
        continue

