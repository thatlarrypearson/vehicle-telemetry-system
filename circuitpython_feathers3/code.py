# code.py
__version__ = "0.0.1"
# basic IMU software test

import time
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
from sys import stdin, stdout
from json import dumps
from adafruit_itertools import count

i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

while not i2c.try_lock():
    pass

print("I2C addr", [hex(device_address) for device_address in i2c.scan()])

i2c.unlock()

# wait for host to send <START><LF> message
print(f"code.py version {__version__}")
start_message = stdin.readline()

bno = BNO08X_I2C(i2c, debug=False)

bno.enable_feature(BNO_REPORT_ACCELEROMETER)
bno.enable_feature(BNO_REPORT_GYROSCOPE)
bno.enable_feature(BNO_REPORT_GRAVITY)
bno.enable_feature(BNO_REPORT_LINEAR_ACCELERATION)
bno.enable_feature(BNO_REPORT_MAGNETOMETER)
bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

for i in count(0):
    # print("before")
    x, y, z = bno.acceleration
    print(
        dumps({
                'command_name': 'acceleration',
                'obd_response_value': {
                    'record_number': i,
                    'x': x,
                    'y': y,
                    'z': z,
                },
            }
        ),
        file=stdout
    )
    x, y, z = bno.gravity
    print(
        dumps({
                'command_name': 'gravity',
                'obd_response_value': {
                    'record_number': i,
                    'x': x,
                    'y': y,
                    'z': z,
                },
            }
        ),
        file=stdout
    )
    x, y, z = bno.gyro
    print(
        dumps({
                'command_name': 'gyroscope',
                'obd_response_value': {
                    'record_number': i,
                    'x': x,
                    'y': y,
                    'z': z,
                },
            }
        ),
        file=stdout
    )
    x, y, z = bno.linear_acceleration
    print(
        dumps({
                'command_name': 'linear_acceleration',
                'obd_response_value': {
                    'record_number': i,
                    'x': x,
                    'y': y,
                    'z': z,
                },
            }
        ),
        file=stdout
    )
    x, y, z = bno.magnetic
    print(
        dumps({
                'command_name': 'magnetometer',
                'obd_response_value': {
                    'record_number': i,
                    'x': x,
                    'y': y,
                    'z': z,
                },
            }
        ),
        file=stdout
    )
    vector = bno.quaternion
    print(
        dumps({
                'command_name': 'rotation_vector',
                'obd_response_value': {
                    'record_number': i,
                    'vector': vector,
                },
            }
        ),
        file=stdout
    )

    time.sleep(1)

time.sleep(2)

