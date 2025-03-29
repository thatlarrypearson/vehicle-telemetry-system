#!/usr/bin/bash
# file_system_info.sh
#
# Runs file_system_info and if the correct drive (volume name or volume label) is found it will sync
# the data directory on the host to the USB drive identified by volume name.

# Need time for the system to startup the Bluetooth connection
export STARTUP_DELAY=60

# Identifier for the correct volume/drive name/label
export VOLUME_LABEL="M2-256"

export DEBUG=False
export HOSTNAME="$(hostname)"
export APP_ID="utility"
export APP_PYTHON="/home/$(whoami)/.local/bin/python3.11"
export APP_HOME="/home/$(whoami)/telemetry-data"
export APP_TMP_DIR="${APP_HOME}/tmp"
export APP_LOG_FILE="${APP_TMP_DIR}/${APP_ID}-$(date '+%Y%m%d_%H%M%S').log"

sleep ${STARTUP_DELAY}

# Debugging support
if [ "${DEBUG}" = "True" ]
then
	# enable shell debug mode
	set -x
fi

# turn off stdin
0<&-

# redirect all stdout and stderr to file
exec &> "${APP_LOG_FILE}"

date '+%Y/%m/%d %H:%M:%S'

cd "${APP_HOME}"

${APP_PYTHON} -m u_tools.file_system_info --verbose

date '+%Y/%m/%d %H:%M:%S'

export MOUNT_POINT="$(${APP_PYTHON} -m u_tools.file_system_info --match_field volume_label --match_value ${VOLUME_LABEL} --print_field mount_point)"

date '+%Y/%m/%d %H:%M:%S'

if [ -z  "${MOUNT_POINT}" ]
then
	echo Did not find a match for volume_label ${VOLUME_LABEL}
	exit 0
fi

echo Match Found mount_point ${MOUNT_POINT} for volume_label ${VOLUME_LABEL}

echo syncing "${APP_HOME}" to "${MOUNT_POINT}/${HOSTNAME}/"
rsync -rv "${APP_HOME}" "${MOUNT_POINT}/${HOSTNAME}/"

echo rsync returned status code $?

exit 0
