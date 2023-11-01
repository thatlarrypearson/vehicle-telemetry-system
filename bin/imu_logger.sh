#!/usr/bin/bash
# imu_logger.sh
#
# Runs IMU Logger

export APP_ID="imu"
export APP_HOME="/home/$(whoami)/telemetry-data"
export APP_TMP_DIR="${APP_HOME}/tmp"
export APP_BASE_PATH="${APP_HOME}/data"
export APP_PYTHON="/home/$(whoami)/.local/bin/python3.11"
export DEBUG="True"
export SHARED_DICTIONARY_NAME="TELEMETRY"
export RESTART_DELAY=30

# get next application startup counter
export APP_COUNT=$(${APP_PYTHON} -m tcounter.app_counter ${APP_ID})

# get current system startup counter
export BOOT_COUNT=$(${APP_PYTHON} -m tcounter.boot_counter --current_boot_count)

export APP_LOG_FILE="telemetry-${BOOT_COUNT}-${APP_ID}-${APP_COUNT}.log"

# Debugging support
if [ "${DEBUG}" = "True" ]
then
	# enable shell debug mode
	set -x
fi

if [ ! -d "${APP_TMP_DIR}" ]
then
	mkdir --parents "${APP_TMP_DIR}"
fi

# turn off stdin
0<&-

# redirect all stdout and stderr to file
exec &> "${APP_TMP_DIR}/${APP_LOG_FILE}"

date '+%Y/%m/%d %H:%M:%S'

if [ ! -d "${APP_BASE_PATH}" ]
then
	mkdir --parents "${APP_BASE_PATH}"
fi

cd "${APP_HOME}"

while date '+%Y/%m/%d %H:%M:%S'
do
	# Enable shared dictionary option
	${APP_PYTHON} -m imu_logger.imu_logger \
		--shared_dictionary_name "${SHARED_DICTIONARY_NAME}" \
		"${APP_BASE_PATH}"

	export RtnVal="$?"
	echo imu_logger returns "${RtnVal}"

    sleep 30

done

