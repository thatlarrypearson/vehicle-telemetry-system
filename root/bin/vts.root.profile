#!/bin/bash
# vehicle-telemetry-system/root/bin/vts.root.profile

export VTS_USER="human"

export VTS_MODULE="${VTS_MODULE:-unknown}"
export VTS_TMP_DIR="/root/tmp"
export VTS_LOG_FILE="${TMP_DIR}/vts-${VTS_MODULE}-$(date '+%Y-%m-%d_%H-%M-%S').log"
export VTS_DEBUG="True"
export VTS_GROUP="dialout"
export VTS_HOME="/home/${VTS_USER}"
export VTS_BT_MAC_ADDRESS="00:04:3E:5A:A7:67"

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

