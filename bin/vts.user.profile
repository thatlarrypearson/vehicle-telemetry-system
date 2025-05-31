#!/usr/bin/bash
#
# vts.user.profile

# change this value to your username
export VTS_USER="human"

# change this value to match the Bluetooth MAC Address
# for your Bluetooth OBD Adapter
export VTS_BT_MAC_ADDRESS="00:04:3E:5A:A7:67"

# only change this value after determining that the default
# serial device is different from the one listed below
export DEFAULT_GPS_SERIAL_DEVICE="/dev/ttyACM0"

# only change the following if you are comfortable making
# changes to UNIX/Linux systems
export VTS_HOME="/home/${VTS_USER}"
export VTS="vehicle-telemetry-system"
export VTS_GROUP="dialout"
