#!/bin/bash
# vehicle-telemetry-system/root/bin/vts.root.profile

# change this to match the username of the user account that runs all of the modules
export VTS_USER="human"

export VTS_MODULE="${VTS_MODULE:-unknown}"
export VTS_TMP_DIR="/root/tmp"
export VTS_LOG_FILE="${TMP_DIR}/vts-${VTS_MODULE}-$(date '+%Y-%m-%d_%H-%M-%S').log"
export VTS_DEBUG="True"
export VTS_GROUP="dialout"
export VTS_HOME="/home/${VTS_USER}"
export VTS_SOURCE_DIR="${VTS_HOME}/vehicle-telemetry-system"

# change this value to match the Bluetooth MAC Address
# for your Bluetooth OBD Adapter
export VTS_BT_MAC_ADDRESS="00:04:3E:5A:A7:67"

# Only change this value after determining that the default
# serial device is different from the one listed below.
# This is the Adafruit Ultimate GPS.
export VTS_DEFAULT_GPS_SERIAL_DEVICE="/dev/ttyACM0"
# This is the Waveshare u-blox GPS Serial Device
# export VTS_DEFAULT_GPS_SERIAL_DEVICE="/dev/ttyACM0"

if [ ! -d "${VTS_TMP_DIR}" ]
then
        mkdir --parents "${VTS_TMP_DIR}"
fi

# redirect all stdout and stderr to file
exec &> "${LOG_FILE}"

# Debugging support
if [ "${VTS_DEBUG}" = "True" ]
then
        # enable shell debug mode
        set -x
fi

# turn off stdin
0<&-

